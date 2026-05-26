"""Hugging Face instruct 모델로 RAG 답변 생성."""
from __future__ import annotations

import logging
import threading

from rag.retriever import RetrievedDoc

logger = logging.getLogger(__name__)

_model = None
_tokenizer = None
_lock = threading.Lock()


def _load_model():
    global _model, _tokenizer
    with _lock:
        if _model is not None:
            return _model, _tokenizer
        from transformers import AutoModelForCausalLM, AutoTokenizer

        from rag.config import MODEL_ID

        logger.info("Loading HF model: %s", MODEL_ID)
        _tokenizer = AutoTokenizer.from_pretrained(MODEL_ID, trust_remote_code=True)
        _model = AutoModelForCausalLM.from_pretrained(
            MODEL_ID,
            trust_remote_code=True,
            device_map="auto",
        )
        return _model, _tokenizer


def _format_context(docs: list[RetrievedDoc]) -> str:
    parts = []
    for i, d in enumerate(docs, 1):
        parts.append(f"[{i}] ({d.title} / {d.source_id})\n{d.text}")
    return "\n\n".join(parts)


def generate_answer(query: str, docs: list[RetrievedDoc], lang: str = "en") -> tuple[str, bool]:
    """
    RAG 프롬프트로 답변 생성.
    Returns: (answer_text, model_used)
    """
    if not docs:
        return (
            "I could not find relevant information in the guide. Please contact the International Office.",
            False,
        )

    context = _format_context(docs)
    lang_hint = {"en": "English", "zh": "Chinese", "ja": "Japanese"}.get(lang, "English")
    system = (
        "You are a helpful assistant for Konkuk University international students. "
        "Answer ONLY using the provided context. If the context is insufficient, say you are not sure "
        "and suggest contacting the International Office. Include source numbers like [1] when relevant. "
        f"Reply in {lang_hint}."
    )
    user = f"Context:\n{context}\n\nQuestion: {query}"

    try:
        model, tokenizer = _load_model()
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
            max_new_tokens=256,
            do_sample=False,
        )
        new_tokens = outputs[0][inputs["input_ids"].shape[1] :]
        answer = tokenizer.decode(new_tokens, skip_special_tokens=True).strip()
        return answer or _fallback_from_docs(docs), True
    except Exception as e:
        logger.warning("LLM generation failed, using retrieval fallback: %s", e)
        return _fallback_from_docs(docs), False


def _fallback_from_docs(docs: list[RetrievedDoc]) -> str:
    """모델 로드 실패 시 검색 상위 문단만 반환."""
    lines = ["(Retrieved excerpts — model unavailable)\n"]
    for i, d in enumerate(docs[:3], 1):
        lines.append(f"[{i}] {d.title}: {d.text[:400]}...")
    return "\n".join(lines)
