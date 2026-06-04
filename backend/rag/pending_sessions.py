"""확인(confirm) 턴용 in-memory 세션 — MVP."""
from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field

from rag.config import PENDING_SESSION_TTL_SEC
from rag.types import RetrievedDoc


@dataclass
class PendingSession:
    query: str
    lang: str
    docs: list[RetrievedDoc]
    created_at: float = field(default_factory=time.time)


_store: dict[str, PendingSession] = {}


def _purge_expired() -> None:
    now = time.time()
    expired = [k for k, v in _store.items() if now - v.created_at > PENDING_SESSION_TTL_SEC]
    for k in expired:
        del _store[k]


def doc_to_dict(d: RetrievedDoc) -> dict:
    return {
        "text": d.text,
        "source_id": d.source_id,
        "title": d.title,
        "lang": d.lang,
        "distance": d.distance,
        "source_url": d.source_url,
        "label": d.label,
        "doc_type": d.doc_type,
        "section_title": d.section_title,
    }


def doc_from_dict(data: dict) -> RetrievedDoc:
    return RetrievedDoc(
        text=data["text"],
        source_id=data["source_id"],
        title=data["title"],
        lang=data["lang"],
        distance=data.get("distance"),
        source_url=data.get("source_url", ""),
        label=data.get("label", ""),
        doc_type=data.get("doc_type", ""),
        section_title=data.get("section_title", ""),
    )


def create(query: str, lang: str, docs: list[RetrievedDoc]) -> str:
    _purge_expired()
    pending_id = str(uuid.uuid4())
    _store[pending_id] = PendingSession(query=query, lang=lang, docs=docs)
    return pending_id


def get(pending_id: str) -> PendingSession | None:
    _purge_expired()
    session = _store.get(pending_id)
    if session is None:
        return None
    if time.time() - session.created_at > PENDING_SESSION_TTL_SEC:
        del _store[pending_id]
        return None
    return session


def pop(pending_id: str) -> PendingSession | None:
    session = get(pending_id)
    if session is not None:
        _store.pop(pending_id, None)
    return session
