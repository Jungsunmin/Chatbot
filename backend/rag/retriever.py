"""Chroma 기반 문서 검색."""
from __future__ import annotations

from dataclasses import dataclass

import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer

from rag.config import CHROMA_COLLECTION, EMBEDDING_MODEL, INDEX_DIR, TOP_K


@dataclass
class RetrievedDoc:
    text: str
    source_id: str
    title: str
    lang: str
    distance: float | None


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
        k = top_k or TOP_K
        if self._collection.count() == 0:
            return []
        q_emb = self._embedder_model().encode([query], show_progress_bar=False).tolist()
        result = self._collection.query(query_embeddings=q_emb, n_results=min(k, self._collection.count()))
        docs = result.get("documents") or [[]]
        metas = result.get("metadatas") or [[]]
        dists = result.get("distances") or [[]]
        out: list[RetrievedDoc] = []
        for text, meta, dist in zip(docs[0], metas[0], dists[0]):
            out.append(
                RetrievedDoc(
                    text=text,
                    source_id=meta.get("source_id", ""),
                    title=meta.get("title", ""),
                    lang=meta.get("lang", "en"),
                    distance=dist,
                )
            )
        return out
