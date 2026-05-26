"""질문 의도 분류 (규칙 기반)."""
from __future__ import annotations

import re
from typing import Literal

QueryIntent = Literal["document_list", "procedure", "deadline", "general"]

# 의도별 검색·문장 선택 시 반드시 포함할 토큰 (질문에 있을 때만 적용)
_REQUIRED_TERMS: dict[QueryIntent, list[str]] = {
    "document_list": ["서류", "제출", "documents", "document"],
    "procedure": [],
    "deadline": [],
    "general": [],
}

_DOCUMENT_PATTERNS = [
    r"서류",
    r"제출서류",
    r"필요한\s*서류",
    r"무엇.*서류",
    r"뭐.*서류",
    r"what\s+documents",
    r"required\s+documents",
    r"submission\s+documents",
]

_PROCEDURE_PATTERNS = [
    r"어떻게",
    r"방법",
    r"절차",
    r"how\s+to",
    r"procedure",
]

_DEADLINE_PATTERNS = [
    r"언제",
    r"기한",
    r"며칠",
    r"deadline",
    r"when\s+",
    r"within\s+\d+",
]


def classify_intent(query: str) -> QueryIntent:
    q = query.strip().lower()
    for pat in _DOCUMENT_PATTERNS:
        if re.search(pat, q, re.I):
            return "document_list"
    for pat in _DEADLINE_PATTERNS:
        if re.search(pat, q, re.I):
            return "deadline"
    for pat in _PROCEDURE_PATTERNS:
        if re.search(pat, q, re.I):
            return "procedure"
    return "general"


def required_terms_for_intent(intent: QueryIntent, query: str) -> list[str]:
    """질문에 실제 등장하는 필수 토큰만 반환."""
    q_lower = query.lower()
    candidates = _REQUIRED_TERMS.get(intent, [])
    matched = []
    for term in candidates:
        if term.lower() in q_lower:
            matched.append(term.lower())
    return matched


def expand_query(query: str, intent: QueryIntent | None = None) -> str:
    """검색 쿼리 확장."""
    intent = intent or classify_intent(query)
    if intent == "document_list":
        return f"{query} 제출서류 필요 서류 외국인 등록 신청 서류"
    if intent == "deadline":
        return f"{query} 기한 마감 일정"
    if intent == "procedure":
        return f"{query} 방법 절차 신청"
    return query
