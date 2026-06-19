"""가이드북 청크 전문 추출 — LLM 요약 없이 의도별 답변 포맷."""
from __future__ import annotations

import re

from rag.intent import QueryIntent
from rag.section_matcher import select_docs_for_intent
from rag.types import RetrievedDoc

# 서류 목록에서 제외할 수수료 관련 줄
_FEE_RE = re.compile(r"(발급)?수수료", re.I)

_LABELS: dict[str, dict[str, str]] = {
    "ko": {"source": "출처"},
    "en": {"source": "Sources"},
    "zh": {"source": "出处"},
    "ja": {"source": "出典"},
}


def _is_fee_line(text: str) -> bool:
    """수수료 안내 줄 — document_list에서 제외."""
    return bool(_FEE_RE.search(text))


def extract_content_lines(text: str, intent: QueryIntent) -> list[str]:
    """
    청크 본문에서 줄 단위 추출.
    - bullet(-)이 있으면 bullet 전부 (하위 들여쓰기 포함)
    - 없으면 비어 있지 않은 줄 전부
    """
    lines = text.splitlines()
    bullet_lines: list[str] = []

    for line in lines:
        m = re.match(r"^(\s*)-\s+(.+)$", line)
        if not m:
            continue
        indent, body = m.group(1), m.group(2).strip()
        if intent == "document_list" and _is_fee_line(body):
            continue
        prefix = "  " if len(indent) >= 2 else ""
        bullet_lines.append(f"{prefix}{body}")

    if bullet_lines:
        return bullet_lines

    # bullet 없는 절차/안내 문단
    plain = [ln.strip() for ln in lines if ln.strip()]
    if intent == "document_list":
        return []
    return plain


def _dedupe_preserve_order(lines: list[str]) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for line in lines:
        key = line.strip()
        if not key or key in seen:
            continue
        seen.add(key)
        out.append(line)
    return out


def _default_header(intent: QueryIntent, section: str, lang: str) -> str:
    if section:
        return section
    defaults = {
        "ko": {
            "document_list": "제출 서류",
            "procedure": "신청 방법",
            "deadline": "신청 시기·기한",
            "general": "안내",
        },
        "en": {
            "document_list": "Required documents",
            "procedure": "How to apply",
            "deadline": "Deadlines",
            "general": "Information",
        },
    }
    table = defaults.get(lang, defaults["en"])
    return table.get(intent, table["general"])


def _format_answer(
    header: str,
    lines: list[str],
    source_title: str,
    lang: str,
) -> str:
    """템플릿 포맷 — 내용은 가이드북 문구 그대로."""
    label = _LABELS.get(lang, _LABELS["en"])["source"]
    bullets = "\n".join(
        f"• {ln}" if not ln.startswith("  ") else f"  • {ln.strip()}" for ln in lines
    )
    return f"{header}\n\n{bullets}\n\n{label}: {source_title}"


def compose_verbatim_answer(
    docs: list[RetrievedDoc],
    intent: QueryIntent,
    lang: str = "ko",
) -> str | None:
    """
    검색 청크에서 의도에 맞는 내용을 전량 추출해 포맷.
    추출 불가 시 None → LLM fallback.
    """
    selected = select_docs_for_intent(docs, intent)
    if not selected:
        return None

    all_lines: list[str] = []
    for doc in selected:
        all_lines.extend(extract_content_lines(doc.text, intent))

    all_lines = _dedupe_preserve_order(all_lines)
    if not all_lines:
        return None

    primary = selected[0]
    header = _default_header(intent, primary.section_title or "", lang)
    source = primary.title or primary.source_id

    return _format_answer(header, all_lines, source, lang)
