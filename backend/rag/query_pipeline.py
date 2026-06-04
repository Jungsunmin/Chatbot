"""Query 파이프라인 — 언어 감지, response_lang, 검색용 정규화(T05 MVP stub)."""
from __future__ import annotations

from dataclasses import dataclass, field

from rag.config import LANG_DETECT_MIN_CONFIDENCE
from rag.intent import QueryIntent, classify_intent, expand_query, expanded_terms_for_intent

_SUPPORTED = frozenset({"ko", "en", "zh", "ja"})


@dataclass
class Query:
    message: str
    ui_lang: str
    detected_lang: str
    detect_confidence: float
    response_lang: str
    normalized_query_en: str
    expanded_terms: list[str] = field(default_factory=list)
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
    """UI lang 우선; 감지 신뢰도 ≥ 임계값이면 detected, 아니면 en."""
    if ui_lang in _SUPPORTED:
        primary = ui_lang
    else:
        primary = "en"
    if confidence >= LANG_DETECT_MIN_CONFIDENCE and detected_lang in _SUPPORTED:
        return detected_lang
    return primary if primary in _SUPPORTED else "en"


def normalize_query_en(message: str, ui_lang: str, detected_lang: str) -> str:
    """T05 MVP stub: en이면 copy, 그 외 message 그대로(추후 LLM 번역)."""
    if ui_lang == "en" or detected_lang == "en":
        return message.strip()
    return message.strip()


def build_search_text(query: Query) -> str:
    """임베딩 입력: normalized_query_en + expanded_terms."""
    parts = [query.normalized_query_en]
    if query.expanded_terms:
        parts.append(" ".join(query.expanded_terms))
    return " ".join(p for p in parts if p).strip()


def build_query(message: str, ui_lang: str) -> Query:
    """단일 진입 — /chat 1차 턴에서 사용."""
    msg = message.strip()
    detected, conf = _detect_language(msg)
    response_lang = resolve_response_lang(ui_lang, detected, conf)
    intent = classify_intent(msg)
    expanded = expanded_terms_for_intent(intent, msg)
    norm_en = normalize_query_en(msg, ui_lang, detected)
    return Query(
        message=msg,
        ui_lang=ui_lang if ui_lang in _SUPPORTED else "en",
        detected_lang=detected,
        detect_confidence=conf,
        response_lang=response_lang,
        normalized_query_en=norm_en,
        expanded_terms=expanded,
        intent=intent,
        ambiguity_level="low",
    )
