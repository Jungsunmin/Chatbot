"""Chroma 기반 문서 검색 + 휴리스틱 rerank + 관련도 밴드."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer

from rag.config import (
    CHROMA_COLLECTION,
    DISTANCE_HIGH_MAX,
    DISTANCE_LOW_MAX,
    EMBEDDING_MODEL,
    INDEX_DIR,
    TOP_K,
)
from rag.doc_router import DocRoute, resolve_doc_route
from rag.intent import QueryIntent, classify_intent, expand_query
from rag.query_pipeline import Query, build_search_text
from rag.types import RetrievedDoc

RelevanceBand = Literal["high", "medium", "low", "none"]

# rerank 가중치 — 낮을수록 상위
_BOOST_SUBMISSION_SECTION = -2
_BOOST_EXPANDED_TERM = -1
_BOOST_DOC_ID_MATCH = -6
_PENALTY_DOC_ID_MISMATCH = 4


@dataclass
class RetrievalResult:
    docs: list[RetrievedDoc]
    band: RelevanceBand
    best_distance: float | None


def _band_from_distance(dist: float | None) -> RelevanceBand:
    if dist is None:
        return "none"
    if dist <= DISTANCE_HIGH_MAX:
        return "high"
    if dist <= DISTANCE_LOW_MAX:
        return "medium"
    return "low"


def _doc_from_meta(text: str, meta: dict, dist: float | None) -> RetrievedDoc:
    return RetrievedDoc(
        text=text,
        source_id=meta.get("source_id", ""),
        title=meta.get("title", ""),
        lang=meta.get("lang", "ko"),
        distance=dist,
        source_url=meta.get("source_url") or "",
        label=meta.get("label") or "",
        doc_type=meta.get("doc_type") or "",
        section_title=meta.get("section_title") or "",
        doc_id=meta.get("doc_id") or "",
        category=meta.get("category") or "",
        sensitive_topic=meta.get("sensitive_topic") or "",
    )


def _is_submission_section(doc: RetrievedDoc) -> bool:
    title = doc.section_title or ""
    return "제출서류" in title or "제출 서류" in title or "기본 제출서류" in title


def _merge_docs(primary: list[RetrievedDoc], extra: list[RetrievedDoc]) -> list[RetrievedDoc]:
    """source_id+section+text 앞부분 기준 중복 제거 병합."""
    seen: set[str] = set()
    out: list[RetrievedDoc] = []
    for d in primary + extra:
        key = f"{d.source_id}|{d.section_title}|{d.text[:80]}"
        if key in seen:
            continue
        seen.add(key)
        out.append(d)
    return out


def _rerank_heuristic(
    docs: list[RetrievedDoc],
    intent: QueryIntent,
    expanded_terms: list[str],
    route: DocRoute | None = None,
) -> list[RetrievedDoc]:
    """거리 + 제출서류·확장어·doc_id 라우팅 가중."""

    def score(d: RetrievedDoc) -> tuple[int, float]:
        boost = 0
        blob = f"{d.section_title or ''} {d.text[:500]}"

        if intent == "document_list" and (
            "제출서류" in blob or "제출 서류" in blob or "기본 제출서류" in blob
        ):
            boost += _BOOST_SUBMISSION_SECTION

        for term in expanded_terms:
            if term and term in blob:
                boost += _BOOST_EXPANDED_TERM

        if route:
            if d.doc_id == route.doc_id or d.doc_type == route.subcategory:
                boost += _BOOST_DOC_ID_MATCH
            elif intent == "document_list":
                boost += _PENALTY_DOC_ID_MISMATCH

        dist = d.distance if d.distance is not None else 1.0
        return (boost, dist)

    return sorted(docs, key=score)


def _dominant_doc_pool(docs: list[RetrievedDoc]) -> list[RetrievedDoc]:
    """route 없을 때 가장 많이 등장하는 doc_id 문서로 pool을 한정.
    여러 문서 청크가 섞여 있을 때 엉뚱한 문서의 제출서류를 선택하는 것을 방지.
    빈도 동점 시 docs 앞쪽(거리 낮음) doc_id 우선."""
    from collections import Counter

    if not docs:
        return docs
    counts = Counter(d.doc_id for d in docs if d.doc_id)
    if not counts:
        return docs
    max_count = counts.most_common(1)[0][1]
    # 동점이면 첫 번째로 등장하는 doc_id (retriever가 거리 순 정렬)
    dominant = next(d.doc_id for d in docs if counts.get(d.doc_id, 0) == max_count)
    filtered = [d for d in docs if d.doc_id == dominant]
    return filtered if filtered else docs


def _narrow_document_list(
    docs: list[RetrievedDoc],
    route: DocRoute | None,
) -> list[RetrievedDoc]:
    """document_list: 한 doc_id의 제출서류 섹션 청크 1개만."""
    if not docs:
        return docs

    if route:
        matched = [d for d in docs if d.doc_id == route.doc_id]
        pool = matched if matched else docs
    else:
        # route 없을 때: 여러 문서 혼합 방지 — 가장 관련 높은 문서로 좁힘
        pool = _dominant_doc_pool(docs)

    submission = [d for d in pool if _is_submission_section(d)]
    if submission:
        return submission[:1]

    return pool[:1]


class Retriever:
    def __init__(self) -> None:
        self._embedder: SentenceTransformer | None = None
        self._client = chromadb.PersistentClient(
            path=str(INDEX_DIR),
            settings=Settings(anonymized_telemetry=False),
        )
        self._collection = self._client.get_or_create_collection(CHROMA_COLLECTION)

    def embedder_is_ready(self) -> bool:
        """임베딩 모델이 메모리에 로드됐는지."""
        return self._embedder is not None

    def warmup(self) -> None:
        """서버 시작 시 임베딩 모델을 미리 로드."""
        self._embedder_model()

    def shutdown(self) -> None:
        """서버 종료 시 임베딩 참조 해제."""
        self._embedder = None

    def _embedder_model(self) -> SentenceTransformer:
        if self._embedder is None:
            self._embedder = SentenceTransformer(EMBEDDING_MODEL)
        return self._embedder

    def _query_collection(
        self,
        q_emb: list[list[float]],
        n: int,
        doc_id: str | None = None,
    ) -> list[RetrievedDoc]:
        kwargs: dict = {
            "query_embeddings": q_emb,
            "n_results": n,
        }
        if doc_id:
            kwargs["where"] = {"doc_id": doc_id}

        result = self._collection.query(**kwargs)
        docs_raw = result.get("documents") or [[]]
        metas = result.get("metadatas") or [[]]
        dists = result.get("distances") or [[]]

        out: list[RetrievedDoc] = []
        for text, meta, dist in zip(docs_raw[0], metas[0], dists[0]):
            out.append(_doc_from_meta(text, meta, dist))
        return out

    def search(self, query: str, top_k: int | None = None) -> list[RetrievedDoc]:
        return self.search_with_band(query, top_k).docs

    def search_with_band(
        self,
        query: str | Query,
        top_k: int | None = None,
        intent: QueryIntent | None = None,
    ) -> RetrievalResult:
        k = top_k or TOP_K
        if self._collection.count() == 0:
            return RetrievalResult(docs=[], band="none", best_distance=None)

        message = ""
        if isinstance(query, Query):
            q_obj = query
            search_q = build_search_text(q_obj)
            intent = q_obj.intent
            expanded = q_obj.expanded_terms
            message = q_obj.message
        else:
            intent = intent or classify_intent(query)
            search_q = expand_query(query, intent)
            expanded = []
            message = query

        route = resolve_doc_route(message)

        q_emb = self._embedder_model().encode([search_q], show_progress_bar=False).tolist()
        n = min(max(k * 2, k), self._collection.count())
        out = self._query_collection(q_emb, n)

        # 라우팅 doc: 해당 문서 청크를 넓게 보강 (제출서류 섹션 누락 방지)
        if route:
            routed_n = min(max(k * 3, 10), self._collection.count())
            routed = self._query_collection(q_emb, routed_n, doc_id=route.doc_id)
            out = _merge_docs(out, routed)

        out = _rerank_heuristic(out, intent, expanded, route)

        if intent == "document_list":
            out = _narrow_document_list(out, route)
        else:
            out = out[:k]

        if not out:
            return RetrievalResult(docs=[], band="none", best_distance=None)

        best_dist = out[0].distance
        band = _band_from_distance(best_dist)

        if band == "low":
            return RetrievalResult(docs=[], band="low", best_distance=best_dist)

        filtered = [d for d in out if d.distance is not None and d.distance <= DISTANCE_LOW_MAX]
        if not filtered:
            return RetrievalResult(docs=[], band="low", best_distance=best_dist)

        return RetrievalResult(docs=filtered, band=band, best_distance=best_dist)
