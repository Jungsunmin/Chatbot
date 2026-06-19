"""Query 파이프라인 — 언어 감지, response_lang, 크로스링궐 키워드 브리징."""
from __future__ import annotations

import re
from dataclasses import dataclass, field

from rag.config import LANG_DETECT_MIN_CONFIDENCE
from rag.intent import QueryIntent, classify_intent, expand_query, expanded_terms_for_intent

_SUPPORTED = frozenset({"ko", "en", "zh", "ja"})

# 비한국어 쿼리에서 한국어 문서를 찾기 위한 키워드 브리지.
# 각 항목: (매칭 정규식, 주입할 한국어 키워드 목록)
# 영어/중국어/일본어 표현 → 한국어 행정 용어로 매핑
_KO_BRIDGE: list[tuple[str, list[str]]] = [
    # 외국인 등록
    (
        r"alien\s*regist|foreigner\s*regist|\barc\b|外国人.*登记|外籍.*登记|外国人.*登録|在留.*登録",
        ["외국인등록", "외국인등록증"],
    ),
    # 체류 연장
    (
        r"stay\s*extens|extend.*stay|stay.*renew|visa.*extens|stay.*period"
        r"|延长.*签证|延长.*居留|居留.*延长|在留.*延長|延長.*在留",
        ["체류기간연장", "체류 연장", "체류기간"],
    ),
    # 시간제 취업
    (
        r"part[-\s]*time|work\s*permit|campus\s*job|student\s*work"
        r"|兼职|打工|工作许可|アルバイト|시간제",
        ["시간제취업", "아르바이트", "시간제"],
    ),
    # 주소/체류지 변경
    (
        r"address\s*change|change.*address|move.*address|notify.*address"
        r"|地址变更|搬家|住所変更",
        ["체류지변경", "주소변경", "체류지"],
    ),
    # 재입국 허가
    (
        r"re[-\s]*entry|reentry|再入国|重新入境",
        ["재입국허가", "재입국"],
    ),
    # 하이코리아 방문 예약
    (
        r"hikorea.*visit|visit.*hikorea|book.*hikorea|hikorea.*reserv"
        r"|visit\s*reserv|make.*appointment|ハイコリア.*予約",
        ["하이코리아 방문예약", "방문 예약"],
    ),
    # 하이코리아 온라인 전자민원
    (
        r"hikorea.*online|online.*hikorea|online.*civil|electronic.*application"
        r"|e[-\s]*application|전자민원",
        ["전자민원", "온라인 신청", "하이코리아"],
    ),
    # 재발급
    (
        r"reissue|re[-\s]*issue|lost\s*card|card\s*lost|damaged\s*card"
        r"|再发|遗失|再発行|紛失",
        ["재발급", "외국인등록증 재발급"],
    ),
    # 서류 일반
    (
        r"documents?\s+(do\s+i\s+need|needed|required)|paperwork|必要.*書類|所需.*材料",
        ["서류", "제출서류"],
    ),
    # 절차/방법 일반
    (
        r"how\s+(do|can|should)\s+i|how\s+to\s+|steps?\s+(to|for)|procedure"
        r"|如何|怎么|どうやって|手続き",
        ["절차", "방법", "신청방법"],
    ),
    # 등록증 카드
    (
        r"registration\s*card|id\s*card|residence\s*card|在留カード",
        ["외국인등록증"],
    ),
]


@dataclass
class Query:
    message: str
    ui_lang: str
    detected_lang: str
    detect_confidence: float
    response_lang: str
    normalized_query_en: str
    expanded_terms: list[str] = field(default_factory=list)
    bridge_terms: list[str] = field(default_factory=list)
    intent: QueryIntent = "general"
    ambiguity_level: str = "low"


def _detect_language(message: str) -> tuple[str, float]:
    try:
        import langdetect

        langs = langdetect.detect_langs(message)
        if not langs:
            return "en", 0.0
        best = langs[0]
        code = best.lang.split("-")[0]
        if code not in _SUPPORTED:
            code = "en"
        return code, float(best.prob)
    except Exception:
        return "en", 0.0


def resolve_response_lang(ui_lang: str, detected_lang: str, confidence: float) -> str:
    """질문 언어 감지 신뢰도 ≥ 임계값이면 detected 우선, 아니면 UI lang."""
    ui = ui_lang if ui_lang in _SUPPORTED else "en"
    if confidence >= LANG_DETECT_MIN_CONFIDENCE and detected_lang in _SUPPORTED:
        return detected_lang
    return ui


def normalize_query_en(message: str, ui_lang: str, detected_lang: str) -> str:
    """검색용 정규화 쿼리. 현재는 원본 그대로 반환하며 bridge_terms로 보완."""
    return message.strip()


def _bridge_ko_keywords(message: str, detected_lang: str) -> list[str]:
    """비한국어 쿼리에서 매칭되는 한국어 키워드를 반환.

    영어/중국어/일본어 → 한국어 행정 키워드를 search_text에 병합해
    멀티링궐 임베딩 모델의 크로스링궐 거리 문제를 완화한다.
    한국어 쿼리는 이미 한국어 문서와 직접 매칭되므로 건너뜀.
    """
    if detected_lang == "ko":
        return []
    q_lower = message.lower()
    terms: list[str] = []
    seen: set[str] = set()
    for pattern, ko_words in _KO_BRIDGE:
        if re.search(pattern, q_lower, re.I):
            for w in ko_words:
                if w not in seen:
                    seen.add(w)
                    terms.append(w)
    return terms


def build_search_text(query: Query) -> str:
    """임베딩 입력: 원본 쿼리 + intent 확장어 + 크로스링궐 한국어 브리지 키워드."""
    parts = [query.normalized_query_en]
    if query.expanded_terms:
        parts.append(" ".join(query.expanded_terms))
    if query.bridge_terms:
        parts.append(" ".join(query.bridge_terms))
    return " ".join(p for p in parts if p).strip()


def build_query(message: str, ui_lang: str) -> Query:
    """단일 진입 — /chat 1차 턴에서 사용."""
    msg = message.strip()
    detected, conf = _detect_language(msg)
    response_lang = resolve_response_lang(ui_lang, detected, conf)
    intent = classify_intent(msg)
    expanded = expanded_terms_for_intent(intent, msg)
    norm_en = normalize_query_en(msg, ui_lang, detected)
    bridge = _bridge_ko_keywords(msg, detected)
    return Query(
        message=msg,
        ui_lang=ui_lang if ui_lang in _SUPPORTED else "en",
        detected_lang=detected,
        detect_confidence=conf,
        response_lang=response_lang,
        normalized_query_en=norm_en,
        expanded_terms=expanded,
        bridge_terms=bridge,
        intent=intent,
        ambiguity_level="low",
    )
