"""Hugging Face instruct 모델 — 검색 청크만 읽고 RAG 답변 생성."""
from __future__ import annotations

import logging

from rag.answer_composer import unknown_message
from rag.intent import QueryIntent, classify_intent
from rag.types import RetrievedDoc

logger = logging.getLogger(__name__)

_UNKNOWN_MARKER = "__UNKNOWN__"

_LANG_NAMES = {
    "ko": "Korean",
    "en": "English",
    "zh": "Chinese",
    "ja": "Japanese",
}

# 의도별 답변 지시 (검색 보강용 intent를 답변 힌트로만 사용)
_INTENT_INSTRUCTIONS: dict[str, dict[QueryIntent, str]] = {
    "ko": {
        "document_list": (
            "질문에 필요한 제출 서류·준비 서류만 bullet(•)으로 나열하세요. "
            "수수료, URL, 전화 안내, '추가 서류 요청' 같은 문장은 넣지 마세요."
        ),
        "procedure": "신청 방법·절차만 짧게 bullet으로 정리하세요.",
        "deadline": "기한·시기·며칠 이내 등 날짜 관련 내용만 bullet으로 정리하세요.",
        "general": (
            "질문에 직접 답하는 내용만 2~5개 bullet으로 정리하세요. "
            "같은 페이지의 무관한 절(다른 주제)은 제외하세요."
        ),
    },
    "en": {
        "document_list": (
            "List ONLY required submission documents as bullets (•). "
            "Do NOT include fees, URLs, phone notices, or generic disclaimers."
        ),
        "procedure": "List only steps or how-to apply, as short bullets.",
        "deadline": "List only deadlines, time limits, or when to apply.",
        "general": (
            "Give 2–5 bullets that directly answer the question. "
            "Exclude unrelated sections from the same page."
        ),
    },
    "zh": {
        "document_list": "仅列出需提交的材料（bullet），不要包含费用、链接或一般性说明。",
        "procedure": "仅说明办理步骤或方法，用 bullet 列出。",
        "deadline": "仅说明期限或时间要求。",
        "general": "用 2–5 条 bullet 直接回答问题，省略无关段落。",
    },
    "ja": {
        "document_list": "提出が必要な書類のみを bullet で列挙。手数料・URL・一般注意は含めない。",
        "procedure": "手続き・方法のみを bullet で簡潔に。",
        "deadline": "期限・時期のみを bullet で。",
        "general": "質問に直接答える 2〜5 bullet のみ。無関係な節は除く。",
    },
}

_FORMAT_INSTRUCTIONS: dict[str, str] = {
    "ko": (
        "형식:\n"
        "1) 첫 줄: 짧은 안내 헤더 한 줄\n"
        "2) 빈 줄 후 • 로 시작하는 bullet 목록\n"
        "3) 마지막 줄: 출처: (context의 페이지 title, 하나만)\n"
        "컨텍스트에 질문과 관련된 정보가 있으면 반드시 bullet으로 답하세요. "
        "전혀 관련 정보가 없을 때만 다른 말 없이 __UNKNOWN__ 만 출력."
    ),
    "en": (
        "Format:\n"
        "1) One short header line\n"
        "2) Blank line, then bullets starting with •\n"
        "3) Last line: Sources: (single page title from context)\n"
        "If context is insufficient, output exactly __UNKNOWN__ and nothing else."
    ),
    "zh": (
        "格式：简短标题一行；空行；• 开头的列表；最后一行：出处：（一个 title）。"
        "无法从上下文回答则只输出 __UNKNOWN__。"
    ),
    "ja": (
        "形式：短い見出し1行、空行、• のリスト、最後に 出典：（title 1つ）。"
        "コンテキストで答えられない場合は __UNKNOWN__ のみ。"
    ),
}


def _format_context(docs: list[RetrievedDoc]) -> str:
    parts = []
    for i, d in enumerate(docs, 1):
        url = d.source_url or "(no url)"
        section = d.section_title or "(no section)"
        parts.append(
            f"[{i}] title={d.title} | section={section} | url={url}\n{d.text}"
        )
    return "\n\n".join(parts)


def _intent_instruction(lang: str, intent: QueryIntent) -> str:
    table = _INTENT_INSTRUCTIONS.get(lang, _INTENT_INSTRUCTIONS["en"])
    return table.get(intent, table["general"])


def _is_unknown_output(text: str) -> bool:
    """__UNKNOWN__ 마커만 인정 (가이드북 본문의 '확인' 등과 혼동 방지)."""
    t = text.strip()
    if not t:
        return True
    if t == _UNKNOWN_MARKER or t.upper() == "UNKNOWN":
        return True
    # 마커만 섞인 짧은 출력
    cleaned = t.replace(_UNKNOWN_MARKER, "").strip()
    if not cleaned and _UNKNOWN_MARKER in t:
        return True
    return False


def _fallback_from_docs(docs: list[RetrievedDoc], lang: str, query: str = "") -> str:
    """모델 실패 시 unknown (옛 문장 인용 경로 제거)."""
    return unknown_message(lang)


def generate_answer(
    query: str,
    docs: list[RetrievedDoc],
    lang: str = "ko",
    intent: QueryIntent | None = None,
    user_confirmed: bool = False,
) -> tuple[str, bool]:
    """
    검색된 청크만으로 LLM 답변 생성.
    Returns: (answer_text, model_used)
    """
    if not docs:
        return unknown_message(lang), False

    intent = intent or classify_intent(query)
    context = _format_context(docs)
    lang_name = _LANG_NAMES.get(lang, "English")
    fmt = _FORMAT_INSTRUCTIONS.get(lang, _FORMAT_INSTRUCTIONS["en"])
    task = _intent_instruction(lang, intent)

    system = (
        "You are an assistant for Konkuk University international students. "
        "Answer ONLY using the provided context chunks. "
        "Do not use outside knowledge. "
        "Use exact names and facts from the context when possible. "
        f"Write the entire reply in {lang_name}."
    )
    confirm_note = ""
    if user_confirmed:
        confirm_note = (
            "\nNote: The user confirmed the retrieved context is relevant to their question. "
            "You must answer from the context; do not output __UNKNOWN__ if the context contains related information.\n"
        )
    # frontmatter preserve_terms — English (한국어) 병기 힌트
    terms_hint = ""
    for d in docs:
        meta_terms = getattr(d, "preserve_terms", None)
        if meta_terms:
            terms_hint = f"\nWhen mentioning these Korean admin terms, use English with Korean in parentheses: {meta_terms}\n"
            break

    user = (
        f"{fmt}{confirm_note}{terms_hint}\n\n"
        f"Task: {task}\n\n"
        f"Context:\n{context}\n\n"
        f"Question: {query}"
    )

    try:
        from rag.model_loader import get_model_and_tokenizer

        model, tokenizer = get_model_and_tokenizer()
        messages = [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ]
        text = tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True,
        )
        inputs = tokenizer(text, return_tensors="pt").to(model.device)
        outputs = model.generate(
            **inputs,
            max_new_tokens=384,
            do_sample=False,
        )
        new_tokens = outputs[0][inputs["input_ids"].shape[1] :]
        answer = tokenizer.decode(new_tokens, skip_special_tokens=True).strip()

        if not answer:
            logger.warning("LLM returned empty answer for query=%r", query[:80])
            return unknown_message(lang), True

        if _is_unknown_output(answer):
            logger.warning("LLM returned UNKNOWN marker for query=%r", query[:80])
            return unknown_message(lang), True

        answer = answer.replace(_UNKNOWN_MARKER, "").strip()
        if not answer:
            return unknown_message(lang), True

        return answer, True
    except Exception as e:
        logger.warning("LLM generation failed: %s", e)
        return _fallback_from_docs(docs, lang, query=query), False
