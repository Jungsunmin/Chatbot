"""RAG 공용 타입 (Chroma 등 무거운 의존성 없음)."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class RetrievedDoc:
    text: str
    source_id: str
    title: str
    lang: str
    distance: float | None
    source_url: str = ""
    label: str = ""
    doc_type: str = ""
    section_title: str = ""
    doc_id: str = ""
    category: str = ""
    sensitive_topic: str = ""
