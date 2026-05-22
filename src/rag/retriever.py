"""Chroma RAG 검색."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import chromadb
from chromadb.utils import embedding_functions

from src.utils.paths import PROJECT_ROOT

INDEX_DIR = PROJECT_ROOT / "data" / "index"
COLLECTION_NAME = "exchange_faq"
EMBED_MODEL = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
DEFAULT_TOP_K = 4
# MVP: top-k만 사용 (거리 임계값은 운영 데이터 확보 후 조정)


@dataclass
class RetrievedChunk:
    chunk_id: str
    text: str
    lang: str
    category: str
    source_type: str
    source_uri: str
    source_domain: str | None
    distance: float | None


class RagRetriever:
    def __init__(self) -> None:
        self._client: chromadb.ClientAPI | None = None
        self._collection = None

    def _ensure_collection(self):
        if self._collection is not None:
            return self._collection
        if not INDEX_DIR.exists():
            raise FileNotFoundError(
                f"Index not found at {INDEX_DIR}. Run scripts/build_index.py on the server."
            )
        ef = embedding_functions.SentenceTransformerEmbeddingFunction(model_name=EMBED_MODEL)
        self._client = chromadb.PersistentClient(path=str(INDEX_DIR))
        self._collection = self._client.get_collection(
            name=COLLECTION_NAME, embedding_function=ef
        )
        return self._collection

    def retrieve(
        self,
        query: str,
        lang: str = "en",
        category: str | None = None,
        top_k: int = DEFAULT_TOP_K,
    ) -> list[RetrievedChunk]:
        col = self._ensure_collection()
        where: dict[str, Any] | None = {"lang": lang}
        if category:
            where = {"$and": [{"lang": lang}, {"category": category}]}

        try:
            result = col.query(
                query_texts=[query],
                n_results=top_k,
                where=where,
            )
        except Exception:
            # 필터 실패 시 lang만
            result = col.query(query_texts=[query], n_results=top_k, where={"lang": lang})

        chunks: list[RetrievedChunk] = []
        if not result["ids"] or not result["ids"][0]:
            return chunks

        for i, cid in enumerate(result["ids"][0]):
            meta = (result["metadatas"] or [[]])[0][i] or {}
            doc = (result["documents"] or [[]])[0][i] or ""
            dist_list = result.get("distances")
            dist = dist_list[0][i] if dist_list and dist_list[0] else None
            chunks.append(
                RetrievedChunk(
                    chunk_id=cid,
                    text=doc,
                    lang=meta.get("lang", lang),
                    category=meta.get("category", "general"),
                    source_type=meta.get("source_type", "local"),
                    source_uri=meta.get("source_uri", ""),
                    source_domain=meta.get("source_domain") or None,
                    distance=dist,
                )
            )
        return chunks
