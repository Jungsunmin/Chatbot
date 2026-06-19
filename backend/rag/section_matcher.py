"""의도(intent)에 맞는 검색 청크·섹션 선택."""
from __future__ import annotations

from rag.intent import QueryIntent
from rag.types import RetrievedDoc

# section_title·본문에서 우선 매칭할 키워드
_INTENT_SECTION_KEYWORDS: dict[QueryIntent, list[str]] = {
    "document_list": ["기본 제출서류", "제출서류", "제출 서류"],
    "procedure": ["신청 방법", "신청 장소", "신청 절차", "절차", "방법"],
    "deadline": ["신청 시기", "신청 기한", "기한", "기간", "시기"],
    "general": [],
}


def _section_score(doc: RetrievedDoc, keywords: list[str]) -> int:
    """낮을수록 우선. 매칭 없으면 큰 값."""
    blob = f"{doc.section_title or ''} {doc.text[:200]}"
    for i, kw in enumerate(keywords):
        if kw in blob:
            return i
    return len(keywords) + 10


def select_docs_for_intent(
    docs: list[RetrievedDoc],
    intent: QueryIntent,
) -> list[RetrievedDoc]:
    """의도에 맞는 섹션 청크만 반환 (검색 순서·거리는 retriever 결과 유지)."""
    if not docs:
        return []

    keywords = _INTENT_SECTION_KEYWORDS.get(intent, [])
    if intent == "general" or not keywords:
        # general: 상위 1~2청크 전문 사용
        return docs[:2]

    scored = sorted(
        docs,
        key=lambda d: (_section_score(d, keywords), d.distance or 1.0),
    )
    best_score = _section_score(scored[0], keywords)
    if best_score > len(keywords):
        return docs[:1]

    matched = [d for d in scored if _section_score(d, keywords) == best_score]
    chosen = matched or docs[:1]

    # document_list: 한 문서·한 섹션 청크만 (혼합 방지)
    if intent == "document_list":
        return chosen[:1]

    return chosen
