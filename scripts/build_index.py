#!/usr/bin/env python3
"""chunks.jsonl → Chroma 벡터 인덱스."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.utils.paths import PROJECT_ROOT

CHUNKS_PATH = PROJECT_ROOT / "data" / "processed" / "chunks.jsonl"
INDEX_DIR = PROJECT_ROOT / "data" / "index"
COLLECTION_NAME = "exchange_faq"
EMBED_MODEL = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"


def run() -> int:
    if not CHUNKS_PATH.exists():
        print(f"Missing {CHUNKS_PATH}. Run build_chunks.py first.")
        return 1

    chunks: list[dict] = []
    with CHUNKS_PATH.open(encoding="utf-8") as f:
        for line in f:
            if line.strip():
                chunks.append(json.loads(line))

    if not chunks:
        print("No chunks to index.")
        return 1

    import chromadb
    from chromadb.utils import embedding_functions

    INDEX_DIR.mkdir(parents=True, exist_ok=True)
    client = chromadb.PersistentClient(path=str(INDEX_DIR))

    # 기존 컬렉션 삭제 후 재생성
    try:
        client.delete_collection(COLLECTION_NAME)
    except Exception:
        pass

    ef = embedding_functions.SentenceTransformerEmbeddingFunction(model_name=EMBED_MODEL)
    collection = client.create_collection(name=COLLECTION_NAME, embedding_function=ef)

    ids = [c["chunk_id"] for c in chunks]
    documents = [c["text"] for c in chunks]
    metadatas = []
    for c in chunks:
        metadatas.append(
            {
                "lang": c.get("lang", "en"),
                "category": c.get("category", "general"),
                "source_type": c.get("source_type", "local"),
                "source_uri": c.get("source_uri", ""),
                "source_domain": c.get("source_domain") or "",
            }
        )

    batch = 64
    for i in range(0, len(ids), batch):
        collection.add(
            ids=ids[i : i + batch],
            documents=documents[i : i + batch],
            metadatas=metadatas[i : i + batch],
        )

    print(f"Indexed {len(ids)} chunks -> {INDEX_DIR} ({COLLECTION_NAME})")
    return 0


if __name__ == "__main__":
    raise SystemExit(run())
