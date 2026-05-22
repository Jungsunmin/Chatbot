"""RAG 프롬프트 템플릿."""
from __future__ import annotations

from src.rag.retriever import RetrievedChunk

FALLBACK_EN = (
    "I could not find enough information in the official guides. "
    "Please contact the International Office for help."
)
FALLBACK_KO = (
    "공식 안내에서 충분한 정보를 찾지 못했습니다. "
    "국제처(International Office)에 문의해 주세요."
)


def build_context_block(chunks: list[RetrievedChunk]) -> str:
    lines = []
    for i, c in enumerate(chunks, 1):
        lines.append(f"[{i}] ({c.source_uri})\n{c.text}")
    return "\n\n".join(lines)


def build_prompt(
    question: str,
    lang: str,
    chunks: list[RetrievedChunk],
    slots: dict | None = None,
) -> str:
    ctx = build_context_block(chunks)
    slot_str = ""
    if slots:
        slot_str = " | ".join(f"{k}={v}" for k, v in slots.items())

    if lang == "ko":
        return f"""당신은 교환학생을 돕는 학교 안내 챗봇입니다.
아래 [Sources]에 있는 내용만 사용해 답하세요. 없는 내용은 추측하지 말고 모른다고 하세요.

[Sources]
{ctx}

[질문] {question}
[추가정보] {slot_str}

[답변]"""
    return f"""You are a school guide chatbot for exchange students.
Answer ONLY using [Sources]. Do not guess. If insufficient, say you do not know.

[Sources]
{ctx}

[Question] {question}
[Extra] {slot_str}

[Answer]"""
