"""소스 문서 → Chroma 인덱스 구축."""
from __future__ import annotations

import hashlib
from dataclasses import dataclass
from pathlib import Path

import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer

from rag.chunking import chunk_markdown
from rag.config import CHROMA_COLLECTION, EMBEDDING_MODEL, INDEX_DIR, SOURCES_DIR
from rag.frontmatter import split_frontmatter


@dataclass
class LoadedSource:
    source_id: str
    title: str
    lang: str
    body: str
    source_url: str = ""
    label: str = ""
    doc_type: str = ""


def _lang_from_path(path: Path) -> str:
    stem = path.stem
    parts = stem.rsplit("_", 1)
    if len(parts) == 2 and len(parts[-1]) == 2:
        return parts[-1]
    return "en"


def _load_sources() -> list[LoadedSource]:
    items: list[LoadedSource] = []
    if not SOURCES_DIR.exists():
        return items
    for path in sorted(SOURCES_DIR.glob("**/*")):
        if path.suffix not in {".md", ".txt"} or path.name == "urls.yaml":
            continue
        raw = path.read_text(encoding="utf-8")
        meta, body = split_frontmatter(raw)
        source_id = str(path.relative_to(SOURCES_DIR))
        title = meta.get("title") or path.stem.replace("_", " ").title()
        lang = meta.get("lang") or _lang_from_path(path)
        items.append(
            LoadedSource(
                source_id=source_id,
                title=title,
                lang=lang,
                body=body,
                source_url=meta.get("source_url", ""),
                label=meta.get("label", ""),
                doc_type=meta.get("type", ""),
            )
        )
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
    for src in _load_sources():
        chunks = chunk_markdown(src.body, src.source_id, src.title, src.lang)
        for c in chunks:
            c.source_url = src.source_url
            c.label = src.label
            c.doc_type = src.doc_type
        all_chunks.extend(chunks)

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
            {
                "source_id": c.source_id,
                "title": c.title,
                "lang": c.lang,
                "source_url": c.source_url or "",
                "label": c.label or "",
                "doc_type": c.doc_type or "",
                "section_title": c.section_title or "",
            }
            for c in all_chunks
        ],
    )
    return collection.count()
