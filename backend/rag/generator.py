"""Hugging Face instruct 모델 — 가이드 전문 또는 청크로 구조화 답변 생성."""
from __future__ import annotations

import logging

from rag.answer_composer import unknown_message
from rag.indexer import LoadedSource
from rag.intent import QueryIntent
from rag.prompt_templates import build_system_prompt, build_user_prompt
from rag.types import RetrievedDoc

logger = logging.getLogger(__name__)

_UNKNOWN_MARKER = "__UNKNOWN__"
_MAX_NEW_TOKENS = 768


def _is_unknown_output(text: str) -> bool:
    """__UNKNOWN__ 마커만 인정 (가이드북 본문의 '확인' 등과 혼동 방지)."""
    t = text.strip()
    if not t:
        return True
    if t == _UNKNOWN_MARKER or t.upper() == "UNKNOWN":
        return True
    cleaned = t.replace(_UNKNOWN_MARKER, "").strip()
    if not cleaned and _UNKNOWN_MARKER in t:
        return True
    return False


def _preserve_terms_hint(terms: list[str], lang: str) -> str:
    """frontmatter preserve_terms — 응답 언어에 맞는 용어 지시."""
    if not terms:
        return ""
    joined = ", ".join(terms)
    if lang == "ko":
        return (
            f"\n다음 행정 용어는 문서에 나온 한국어 표기를 그대로 사용하세요: {joined}\n"
            "영어 번역이나 괄호 병기를 추가하지 마세요.\n"
        )
    if lang == "en":
        return (
            f"\nWhen mentioning these Korean admin terms, "
            f"write the English name followed by Korean in parentheses: {joined}\n"
        )
    if lang == "zh":
        return f"\n提及以下韩语行政术语时，请在中文译名后附上韩语原文（括号内）：{joined}\n"
    if lang == "ja":
        return f"\n以下の韓国語行政用語は、日本語訳の後に韓国語を括弧内に表記してください：{joined}\n"
    return ""


def _dedup_output_lines(text: str) -> str:
    """LLM 출력에서 중복 줄 제거 — 반복 루프 발생 시 후처리 안전망."""
    lines = text.splitlines()
    seen: set[str] = set()
    out: list[str] = []
    for line in lines:
        key = line.strip()
        if key and key in seen:
            continue
        if key:
            seen.add(key)
        out.append(line)
    return "\n".join(out)


def _run_llm(system: str, user: str) -> str | None:
    """LLM 호출 — 성공 시 답변 문자열, 실패 시 None."""
    try:
        import torch

        from rag.model_loader import get_model_and_tokenizer

        model, tokenizer = get_model_and_tokenizer()

        # MPS(Apple Silicon) 부동소수점 비결정성 완화 — 동일 질문 동일 답변
        torch.manual_seed(42)
        if torch.backends.mps.is_available():
            torch.mps.manual_seed(42)

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
            max_new_tokens=_MAX_NEW_TOKENS,
            do_sample=False,
            temperature=1.0,  # do_sample=False 시 무시되나 일부 구현에서 명시 필요
        )
        new_tokens = outputs[0][inputs["input_ids"].shape[1] :]
        raw = tokenizer.decode(new_tokens, skip_special_tokens=True).strip()
        return _dedup_output_lines(raw)
    except Exception as e:
        logger.warning("LLM generation failed: %s", e)
        return None


def _finalize_answer(raw: str | None, lang: str) -> tuple[str, bool]:
    """LLM 출력 → (답변, model_used)."""
    if not raw:
        return unknown_message(lang), False
    if _is_unknown_output(raw):
        logger.warning("LLM returned UNKNOWN marker")
        return unknown_message(lang), True
    answer = raw.replace(_UNKNOWN_MARKER, "").strip()
    if not answer:
        return unknown_message(lang), True
    return answer, True


def generate_answer_from_source(
    source: LoadedSource,
    query: str,
    lang: str = "ko",
) -> tuple[str, bool]:
    """doc_id로 로드한 md 전문으로 고정 5단계 프롬프트 답변."""
    system = build_system_prompt(lang)
    user = build_user_prompt(lang, query, source.body, source.title)
    user += _preserve_terms_hint(source.preserve_terms, lang)
    return _finalize_answer(_run_llm(system, user), lang)


def _chunks_to_document(docs: list[RetrievedDoc]) -> tuple[str, str]:
    """검색 청크 묶음 → 프롬프트용 단일 문서 텍스트."""
    parts: list[str] = []
    title = docs[0].title if docs else "Guide"
    for i, d in enumerate(docs, 1):
        section = d.section_title or d.title
        parts.append(f"### [{i}] {section}\n{d.text}")
    return "\n\n".join(parts), title


def generate_answer(
    query: str,
    docs: list[RetrievedDoc],
    lang: str = "ko",
    intent: QueryIntent | None = None,
    user_confirmed: bool = False,
) -> tuple[str, bool]:
    """
    검색 청크 fallback — 동일 고정 프롬프트로 LLM 답변.
    Returns: (answer_text, model_used)
    """
    del intent, user_confirmed  # 하위 호환용 인자, 미사용
    if not docs:
        return unknown_message(lang), False

    document, source_title = _chunks_to_document(docs)
    system = build_system_prompt(lang)
    user = build_user_prompt(lang, query, document, source_title)

    terms: list[str] = []
    for d in docs:
        meta_terms = getattr(d, "preserve_terms", None)
        if meta_terms:
            terms = list(meta_terms)
            break
    user += _preserve_terms_hint(terms, lang)

    return _finalize_answer(_run_llm(system, user), lang)
