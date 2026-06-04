"""민감 주제 SafetyNotice (T11)."""
from __future__ import annotations

_SENSITIVE_TOPICS = frozenset(
    {"immigration", "medical", "legal", "employment", "financial"}
)

_NOTICES: dict[str, dict[str, str]] = {
    "ko": {
        "immigration": (
            "이 안내는 일반 정보이며, 개인 상황·법무부 판단에 따라 달라질 수 있습니다. "
            "최종 확인은 하이코리아(www.hikorea.go.kr) 또는 출입국·외국인청(1345)에 하세요."
        ),
        "default": (
            "AI가 정리한 안내입니다. 공식 기관·건국대 국제처에 최종 확인하세요."
        ),
    },
    "en": {
        "immigration": (
            "This is general information only. Requirements may vary by case. "
            "Verify on HiKorea or the Immigration Contact Center (1345)."
        ),
        "default": (
            "AI-curated guidance. Confirm with official sources or KU international offices."
        ),
    },
    "zh": {
        "immigration": "以下为一般性说明，请以韩国出入境官网或1345热线最终确认。",
        "default": "AI整理内容，请以学校国际处或官方渠道最终确认。",
    },
    "ja": {
        "immigration": "一般的な案内です。最終確認はハイコリアまたは出入国管理庁（1345）で行ってください。",
        "default": "AIによる案内です。公式機関・国際処で最終確認してください。",
    },
}


def safety_notice_for_docs(lang: str, docs: list) -> str | None:
    """청크 메타에 민감 주제가 있으면 안내 문구 반환."""
    lang = lang if lang in _NOTICES else "en"
    topics = {getattr(d, "sensitive_topic", "") or "" for d in docs}
    if topics & _SENSITIVE_TOPICS:
        if "immigration" in topics:
            return _NOTICES[lang].get("immigration") or _NOTICES["en"]["immigration"]
        return _NOTICES[lang].get("default") or _NOTICES["en"]["default"]
    return None
