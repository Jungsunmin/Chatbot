"""멀티턴: 슬롯 clarify → RAG + 생성."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

from src.dialog.intent_rules import detect_category
from src.inference.generator import AnswerGenerator
from src.rag.retriever import RagRetriever
from src.utils.paths import PROJECT_ROOT

SCHEMAS_DIR = PROJECT_ROOT / "data" / "schemas"


@dataclass
class ChatSession:
    category: str = "general"
    slots: dict[str, Any] = field(default_factory=dict)
    lang: str = "en"


@dataclass
class ChatResponse:
    type: str  # clarify | answer | fallback
    message: str | None = None
    text: str | None = None
    fields: list[dict] | None = None
    citations: list[dict] | None = None
    category: str | None = None


def _load_schema(category: str) -> dict | None:
    path = SCHEMAS_DIR / f"{category}.yaml"
    if not path.exists():
        return None
    with path.open(encoding="utf-8") as f:
        return yaml.safe_load(f)


def _schema_to_fields(schema: dict, lang: str) -> list[dict]:
    required_names = {s["name"] for s in schema.get("required_slots", [])}
    fields = []
    for slot in schema.get("required_slots", []) + schema.get("optional_slots", []):
        labels = slot.get("labels") or {}
        fields.append(
            {
                "name": slot["name"],
                "type": slot.get("type", "text"),
                "label": labels.get(lang) or labels.get("en") or slot["name"],
                "options": slot.get("options"),
                "required": slot["name"] in required_names,
            }
        )
    return fields


def _missing_required(schema: dict, slots: dict) -> list[str]:
    missing = []
    for slot in schema.get("required_slots", []):
        name = slot["name"]
        if not slots.get(name):
            missing.append(name)
    return missing


class DialogManager:
    def __init__(self) -> None:
        self.retriever = RagRetriever()
        self.generator = AnswerGenerator()

    def handle(
        self,
        session: ChatSession,
        message: str | None = None,
        slots_update: dict | None = None,
    ) -> ChatResponse:
        if message:
            session.category = detect_category(message)

        if slots_update:
            session.slots.update(slots_update)

        schema = _load_schema(session.category)
        if schema:
            missing = _missing_required(schema, session.slots)
            if missing:
                msg_map = schema.get("clarify_message") or {}
                return ChatResponse(
                    type="clarify",
                    message=msg_map.get(session.lang) or msg_map.get("en", ""),
                    fields=_schema_to_fields(schema, session.lang),
                    category=session.category,
                )

        query = message or " ".join(f"{k}:{v}" for k, v in session.slots.items())
        if not query.strip():
            return ChatResponse(
                type="fallback",
                text=(
                    "질문을 입력해 주세요."
                    if session.lang == "ko"
                    else "Please enter your question."
                ),
            )

        try:
            chunks = self.retriever.retrieve(
                query=query,
                lang=session.lang,
                category=session.category if session.category != "general" else None,
            )
        except FileNotFoundError as e:
            return ChatResponse(type="fallback", text=str(e))

        if not chunks:
            from src.inference.prompts import FALLBACK_EN, FALLBACK_KO

            return ChatResponse(
                type="fallback",
                text=FALLBACK_KO if session.lang == "ko" else FALLBACK_EN,
                category=session.category,
            )

        answer = self.generator.generate(
            question=query,
            lang=session.lang,
            chunks=chunks,
            slots=session.slots,
        )
        citations = [
            {
                "chunk_id": c.chunk_id,
                "source_uri": c.source_uri,
                "source_type": c.source_type,
            }
            for c in chunks
        ]
        return ChatResponse(
            type="answer",
            text=answer,
            citations=citations,
            category=session.category,
        )
