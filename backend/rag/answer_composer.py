"""API 고정 문구·확인 턴 미리보기 (답변 본문은 generator LLM)."""
from __future__ import annotations

from rag.types import RetrievedDoc

_TEMPLATES = {
    "ko": {
        "unknown": (
            "해당 내용은 가이드북에서 확인되지 않아 답변드리기 어렵습니다.\n"
            "국제처·외국인학생센터에 문의해 주세요."
        ),
        "confirm_prompt": "아래 안내가 질문과 관련이 있나요?",
        "confirm_preview": "미리보기: {body}",
    },
    "en": {
        "unknown": (
            "I could not verify this in the guidebook, so I cannot answer from official sources.\n"
            "Please contact the International Office."
        ),
        "confirm_prompt": "Is the preview below related to your question?",
        "confirm_preview": "Preview: {body}",
    },
    "zh": {
        "unknown": "指南中未能确认该内容，无法根据官方来源回答。请联系国际处。",
        "confirm_prompt": "以下预览是否与你的问题相关？",
        "confirm_preview": "预览：{body}",
    },
    "ja": {
        "unknown": "ガイドブックで確認できないため、公式情報に基づく回答はできません。国際処にお問い合わせください。",
        "confirm_prompt": "以下のプレビューはご質問に関連がありますか？",
        "confirm_preview": "プレビュー: {body}",
    },
}

_PREVIEW_MAX = 320


def _tpl(lang: str) -> dict[str, str]:
    return _TEMPLATES.get(lang, _TEMPLATES["en"])


def unknown_message(lang: str = "ko") -> str:
    return _tpl(lang)["unknown"]


def confirm_prompt_text(lang: str = "ko") -> str:
    return _tpl(lang)["confirm_prompt"]


def compose_confirm_preview(docs: list[RetrievedDoc], lang: str = "ko") -> str:
    """medium 밴드 확인 턴 — 첫 청크 앞부분만 잘라 표시."""
    t = _tpl(lang)
    if not docs:
        return unknown_message(lang)
    body = " ".join(docs[0].text.split())[:_PREVIEW_MAX]
    return t["confirm_preview"].format(body=body)
