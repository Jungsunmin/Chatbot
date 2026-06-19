"""doc_id로 가이드북 md 본문·메타 로드."""
from __future__ import annotations

from rag.indexer import LoadedSource, list_sources


def load_source_by_doc_id(doc_id: str) -> LoadedSource | None:
    """frontmatter doc_id와 일치하는 소스 1건 반환."""
    for src in list_sources():
        if src.doc_id == doc_id:
            return src
    return None
