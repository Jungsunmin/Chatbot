"""API 고정 문구 (답변 본문은 generator LLM)."""
from __future__ import annotations

_TEMPLATES = {
    "ko": {
        "unknown": (
            "해당 내용은 가이드북에서 확인되지 않아 답변드리기 어렵습니다.\n"
            "국제처·외국인학생센터에 문의해 주세요."
        ),
    },
    "en": {
        "unknown": (
            "I could not verify this in the guidebook, so I cannot answer from official sources.\n"
            "Please contact the International Office."
        ),
    },
    "zh": {
        "unknown": "指南中未能确认该内容，无法根据官方来源回答。请联系国际处。",
    },
    "ja": {
        "unknown": "ガイドブックで確認できないため、公式情報に基づく回答はできません。国際処にお問い合わせください。",
    },
}


def _tpl(lang: str) -> dict[str, str]:
    return _TEMPLATES.get(lang, _TEMPLATES["en"])


def unknown_message(lang: str = "ko") -> str:
    return _tpl(lang)["unknown"]
