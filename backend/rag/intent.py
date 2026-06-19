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
    # 한국어
    r"서류",
    r"제출서류",
    r"필요한\s*서류",
    r"무엇.*서류",
    r"뭐.*서류",
    r"뭐가\s*필요",
    r"준비.*서류",
    # 영어 — "what documents", "required documents", "what do I need"
    r"what\s+documents",
    r"required\s+documents",
    r"submission\s+documents",
    r"documents?\s+(do\s+i\s+need|needed|required|to\s+(prepare|bring|submit))",
    r"what\s+(do\s+i\s+need|should\s+i\s+bring|do\s+i\s+have\s+to\s+bring)",
    r"materials?\s+(needed|required|to\s+(bring|prepare))",
    r"paperwork",
    # 중국어
    r"需要.*材料|所需.*材料|准备.*材料|提交.*材料",
    # 일본어
    r"必要.*書類|準備.*書類|提出.*書類",
]

_PROCEDURE_PATTERNS = [
    # 한국어
    r"어떻게",
    r"방법",
    r"절차",
    r"신청\s*방법",
    r"어디서",
    # 영어 — "how to", "how do I", "how can I", "steps", "process", "guide"
    r"how\s+to",
    r"how\s+(do|can|should|would|must)\s+i",
    r"how\s+(do|can)\s+(we|they|students?)",
    r"procedure",
    r"step[-\s]*by[-\s]*step",
    r"steps?\s+(to|for)",
    r"process\s+(to|for|of)",
    r"guide\s+(to|for|on)",
    r"where\s+(do|can|should)\s+i",
    r"where\s+to\s+(go|apply|submit)",
    # 중국어
    r"如何|怎么|怎样|办理|流程|申请方法",
    # 일본어
    r"どうやって|手続き|申請方法|どこで",
]

_DEADLINE_PATTERNS = [
    # 한국어
    r"언제",
    r"기한",
    r"며칠",
    r"기간",
    r"몇\s*일",
    # 영어
    r"deadline",
    r"when\s+(do|should|must|can)\s+i",
    r"when\s+is",
    r"within\s+\d+",
    r"how\s+(long|many\s+days|soon)",
    r"time\s+limit",
    r"due\s+date",
    # 중국어
    r"什么时候|多少天|期限|截止",
    # 일본어
    r"いつ|期限|何日以内",
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


def expanded_terms_for_intent(intent: QueryIntent, query: str) -> list[str]:
    """한국어 행정어 확장 — embed 검색에 병합."""
    if intent == "document_list":
        return ["제출서류", "필요 서류", "외국인등록", "신청 서류"]
    if intent == "deadline":
        return ["기한", "마감", "일정"]
    if intent == "procedure":
        return ["방법", "절차", "신청"]
    return []
