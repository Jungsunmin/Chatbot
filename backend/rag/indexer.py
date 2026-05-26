"""소스 문서 → Chroma 인덱스 구축."""
from __future__ import annotations

import hashlib
from pathlib import Path

import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer

from rag.chunking import chunk_markdown
from rag.config import CHROMA_COLLECTION, EMBEDDING_MODEL, INDEX_DIR, SOURCES_DIR


def _load_sources() -> list[tuple[str, str, str, str]]:
    """(source_id, title, lang, full_text) 목록."""
    items: list[tuple[str, str, str, str]] = []
    if not SOURCES_DIR.exists():
        return items
    for path in sorted(SOURCES_DIR.glob("**/*")):
        if path.suffix not in {".md", ".txt"}:
            continue
        # 파일명 예: visa_en.md → lang en
        stem = path.stem
        parts = stem.rsplit("_", 1)
        lang = parts[-1] if len(parts) == 2 and len(parts[-1]) == 2 else "en"
        title = parts[0].replace("_", " ").title() if parts else stem
        source_id = str(path.relative_to(SOURCES_DIR))
        items.append((source_id, title, lang, path.read_text(encoding="utf-8")))
    return items


def build_index(force: bool = False) -> int:
    """Chroma 컬렉션을 (재)구축하고 청크 수를 반환."""
    INDEX_DIR.mkdir(parents=True, exist_ok=True)
    client = chromadb.PersistentClient(
        path=str(INDEX_DIR),
        settings=Settings(anonymized_telemetry=False),
    )
    if force:
        try:
            client.delete_collection(CHROMA_COLLECTION)
        except Exception:
            pass

    collection = client.get_or_create_collection(
        name=CHROMA_COLLECTION,
        metadata={"hnsw:space": "cosine"},
    )
    if collection.count() > 0 and not force:
        return collection.count()

    embedder = SentenceTransformer(EMBEDDING_MODEL)
    all_chunks = []
    for source_id, title, lang, body in _load_sources():
        all_chunks.extend(chunk_markdown(body, source_id, title, lang))

    if not all_chunks:
        return 0

    texts = [c.text for c in all_chunks]
    embeddings = embedder.encode(texts, show_progress_bar=False).tolist()
    ids = [
        hashlib.sha256(f"{c.source_id}:{i}:{c.text[:80]}".encode()).hexdigest()[:32]
        for i, c in enumerate(all_chunks)
    ]
    collection.add(
        ids=ids,
        embeddings=embeddings,
        documents=texts,
        metadatas=[
            {"source_id": c.source_id, "title": c.title, "lang": c.lang}
            for c in all_chunks
        ],
    )
    return collection.count()
