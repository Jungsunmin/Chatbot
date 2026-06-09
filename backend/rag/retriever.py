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
from rag.intent import QueryIntent, classify_intent, expand_query
from rag.query_pipeline import Query, build_search_text
from rag.types import RetrievedDoc

RelevanceBand = Literal["high", "medium", "low", "none"]


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


def _rerank_heuristic(
    docs: list[RetrievedDoc],
    intent: QueryIntent,
    expanded_terms: list[str],
) -> list[RetrievedDoc]:
    """거리 + 제출서류·expanded_terms 부분 문자열 가중."""

    def score(d: RetrievedDoc) -> tuple[int, float]:
        boost = 0
        blob = f"{d.section_title or ''} {d.text[:500]}"
        if intent == "document_list" and (
            "제출서류" in blob or "제출 서류" in blob
        ):
            boost -= 2
        for term in expanded_terms:
            if term and term in blob:
                boost -= 1
        dist = d.distance if d.distance is not None else 1.0
        return (boost, dist)

    return sorted(docs, key=score)


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

        if isinstance(query, Query):
            q_obj = query
            search_q = build_search_text(q_obj)
            intent = q_obj.intent
            expanded = q_obj.expanded_terms
        else:
            intent = intent or classify_intent(query)
            search_q = expand_query(query, intent)
            expanded = []

        q_emb = self._embedder_model().encode([search_q], show_progress_bar=False).tolist()
        n = min(max(k * 2, k), self._collection.count())
        result = self._collection.query(
            query_embeddings=q_emb,
            n_results=n,
        )
        docs_raw = result.get("documents") or [[]]
        metas = result.get("metadatas") or [[]]
        dists = result.get("distances") or [[]]

        out: list[RetrievedDoc] = []
        for text, meta, dist in zip(docs_raw[0], metas[0], dists[0]):
            out.append(_doc_from_meta(text, meta, dist))

        out = _rerank_heuristic(out, intent, expanded)[:k]

        if not out:
            return RetrievalResult(docs=[], band="none", best_distance=None)

        best_dist = out[0].distance
        band = _band_from_distance(best_dist)

        if band == "low":
            return RetrievalResult(docs=[], band="low", best_distance=best_dist)

        filtered = [d for d in out if d.distance is not None and d.distance <= DISTANCE_LOW_MAX]
        if not filtered:
            return RetrievalResult(docs=[], band="low", best_distance=best_dist)

        return RetrievalResult(docs=filtered[:k], band=band, best_distance=best_dist)
