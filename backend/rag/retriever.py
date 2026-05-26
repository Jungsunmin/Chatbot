"""Chroma 기반 문서 검색 + 관련도 밴드."""
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


class Retriever:
    def __init__(self) -> None:
        self._embedder: SentenceTransformer | None = None
        self._client = chromadb.PersistentClient(
            path=str(INDEX_DIR),
            settings=Settings(anonymized_telemetry=False),
        )
        self._collection = self._client.get_or_create_collection(CHROMA_COLLECTION)

    def _embedder_model(self) -> SentenceTransformer:
        if self._embedder is None:
            self._embedder = SentenceTransformer(EMBEDDING_MODEL)
        return self._embedder

    def search(self, query: str, top_k: int | None = None) -> list[RetrievedDoc]:
        """하위 호환 — 밴드 필터 없이 raw top-k."""
        return self.search_with_band(query, top_k).docs

    def search_with_band(
        self,
        query: str,
        top_k: int | None = None,
        intent: QueryIntent | None = None,
    ) -> RetrievalResult:
        k = top_k or TOP_K
        if self._collection.count() == 0:
            return RetrievalResult(docs=[], band="none", best_distance=None)

        intent = intent or classify_intent(query)
        search_q = expand_query(query, intent)
        q_emb = self._embedder_model().encode([search_q], show_progress_bar=False).tolist()
        result = self._collection.query(
            query_embeddings=q_emb,
            n_results=min(k, self._collection.count()),
        )
        docs_raw = result.get("documents") or [[]]
        metas = result.get("metadatas") or [[]]
        dists = result.get("distances") or [[]]

        out: list[RetrievedDoc] = []
        for text, meta, dist in zip(docs_raw[0], metas[0], dists[0]):
            out.append(
                RetrievedDoc(
                    text=text,
                    source_id=meta.get("source_id", ""),
                    title=meta.get("title", ""),
                    lang=meta.get("lang", "en"),
                    distance=dist,
                    source_url=meta.get("source_url") or "",
                    label=meta.get("label") or "",
                    doc_type=meta.get("doc_type") or "",
                    section_title=meta.get("section_title") or "",
                )
            )

        if intent == "document_list" and out:
            out.sort(
                key=lambda d: (
                    0
                    if "제출서류" in (d.section_title or "") or "제출서류" in d.text[:400]
                    else 1,
                    d.distance if d.distance is not None else 1.0,
                )
            )

        if not out:
            return RetrievalResult(docs=[], band="none", best_distance=None)

        best_dist = out[0].distance
        band = _band_from_distance(best_dist)

        # low: 검색됐어도 관련 없음으로 취급
        if band == "low":
            return RetrievalResult(docs=[], band="low", best_distance=best_dist)

        # usable docs: distance within LOW_MAX
        filtered = [d for d in out if d.distance is not None and d.distance <= DISTANCE_LOW_MAX]
        if not filtered:
            return RetrievalResult(docs=[], band="low", best_distance=best_dist)

        return RetrievalResult(docs=filtered, band=band, best_distance=best_dist)
