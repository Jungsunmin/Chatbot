"""소스 문서 → Chroma 인덱스 구축 (frontmatter v2)."""
from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
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
    doc_id: str = ""
    category: str = ""
    sensitive_topic: str = "general"
    preserve_terms: list[str] = field(default_factory=list)


def _lang_from_path(path: Path) -> str:
    stem = path.stem
    parts = stem.rsplit("_", 1)
    if len(parts) == 2 and parts[-1] in ("ko", "en", "zh", "ja"):
        return parts[-1]
    return "ko"


def _load_sources() -> list[LoadedSource]:
    items: list[LoadedSource] = []
    if not SOURCES_DIR.exists():
        return items
    for path in sorted(SOURCES_DIR.glob("**/*")):
        if path.suffix not in {".md", ".txt"} or path.name in {"urls.yaml", "README.md"}:
            continue
        raw = path.read_text(encoding="utf-8")
        meta, body = split_frontmatter(raw)
        source_id = str(path.relative_to(SOURCES_DIR))
        doc_id = str(meta.get("doc_id") or path.stem.replace("_ko", ""))
        title = (
            meta.get("source_title")
            or meta.get("title")
            or path.stem.replace("_", " ").title()
        )
        lang = (
            meta.get("curated_language")
            or meta.get("source_language")
            or meta.get("lang")
            or _lang_from_path(path)
        )
        preserve = meta.get("preserve_terms") or []
        if isinstance(preserve, str):
            preserve = [preserve]
        items.append(
            LoadedSource(
                source_id=source_id,
                title=title,
                lang=str(lang),
                body=body,
                source_url=str(meta.get("source_url", "") or ""),
                label=meta.get("label", "") or "",
                doc_type=meta.get("type", "") or meta.get("subcategory", "") or "",
                doc_id=doc_id,
                category=str(meta.get("category", "") or ""),
                sensitive_topic=str(meta.get("sensitive_topic", "general") or "general"),
                preserve_terms=list(preserve),
            )
        )
    return items


def list_sources() -> list[LoadedSource]:
    """SOURCES_DIR 아래 모든 가이드북 소스 목록."""
    return _load_sources()


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
            c.doc_type = src.doc_type or src.category
        all_chunks.extend((src, c) for c in chunks)

    if not all_chunks:
        return 0

    # embed_text: contextual prefix 포함 — 임베딩 품질 향상
    # text: 원본 — Chroma document 저장, LLM 프롬프트·citations에 사용
    embed_texts = [c.embed_text for _, c in all_chunks]
    display_texts = [c.text for _, c in all_chunks]
    embeddings = embedder.encode(embed_texts, show_progress_bar=False).tolist()
    ids = [
        hashlib.sha256(
            f"{src.doc_id or c.source_id}:{i}:{c.text[:80]}".encode()
        ).hexdigest()[:32]
        for i, (src, c) in enumerate(all_chunks)
    ]
    collection.add(
        ids=ids,
        embeddings=embeddings,
        documents=display_texts,
        metadatas=[
            {
                "source_id": c.source_id,
                "doc_id": src.doc_id or "",
                "title": c.title,
                "lang": c.lang,
                "source_url": c.source_url or "",
                "label": c.label or "",
                "doc_type": c.doc_type or "",
                "section_title": c.section_title or "",
                "category": src.category or "",
                "sensitive_topic": src.sensitive_topic or "general",
                "preserve_terms": ",".join(src.preserve_terms[:20]),
            }
            for src, c in all_chunks
        ],
    )
    return collection.count()
