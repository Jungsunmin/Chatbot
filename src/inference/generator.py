"""decoder-only 로컬 생성 (없으면 검색 결과만 반환)."""
from __future__ import annotations

import os

from src.inference.prompts import FALLBACK_EN, FALLBACK_KO, build_prompt
from src.rag.retriever import RetrievedChunk

MODEL_ID = os.environ.get("CHATBOT_MODEL_ID", "Qwen/Qwen2.5-0.5B-Instruct")


class AnswerGenerator:
    def __init__(self) -> None:
        self._model = None
        self._tokenizer = None
        self._load_error: str | None = None

    def _try_load(self) -> bool:
        if self._model is not None:
            return True
        if self._load_error:
            return False
        try:
            import torch
            from transformers import AutoModelForCausalLM, AutoTokenizer

            self._tokenizer = AutoTokenizer.from_pretrained(MODEL_ID, trust_remote_code=True)
            load_kwargs: dict = {"trust_remote_code": True}
            if torch.cuda.is_available():
                load_kwargs["device_map"] = "auto"
                load_kwargs["torch_dtype"] = torch.float16
            else:
                # CPU: 소형 모델만 로드 (느림)
                load_kwargs["torch_dtype"] = torch.float32
            self._model = AutoModelForCausalLM.from_pretrained(MODEL_ID, **load_kwargs)
            return True
        except Exception as e:
            self._load_error = str(e)
            return False

    def generate(
        self,
        question: str,
        lang: str,
        chunks: list[RetrievedChunk],
        slots: dict | None = None,
        max_new_tokens: int = 256,
    ) -> str:
        if not chunks:
            return FALLBACK_KO if lang == "ko" else FALLBACK_EN

        if not self._try_load():
            # RAG-only 폴백: 검색 문단을 그대로 요약 형태로 반환
            parts = [f"- {c.text}" for c in chunks[:3]]
            header = "다음은 공식 안내에서 찾은 내용입니다:\n" if lang == "ko" else "From official guides:\n"
            return header + "\n".join(parts)

        prompt = build_prompt(question, lang, chunks, slots)
        import torch

        inputs = self._tokenizer(prompt, return_tensors="pt")
        if hasattr(self._model, "device"):
            inputs = {k: v.to(self._model.device) for k, v in inputs.items()}

        with torch.no_grad():
            out = self._model.generate(
                **inputs,
                max_new_tokens=max_new_tokens,
                do_sample=False,
                temperature=0.2,
                pad_token_id=self._tokenizer.eos_token_id,
            )
        text = self._tokenizer.decode(out[0], skip_special_tokens=True)
        if "[Answer]" in text:
            text = text.split("[Answer]")[-1]
        elif "[답변]" in text:
            text = text.split("[답변]")[-1]
        return text.strip() or (FALLBACK_KO if lang == "ko" else FALLBACK_EN)
