"""HF 모델·토크나이저 공유 로더 (4bit NF4 또는 Mac fp16)."""
from __future__ import annotations

import logging
import threading

logger = logging.getLogger(__name__)

_model = None
_tokenizer = None
_lock = threading.Lock()


def _load_tokenizer(model_id: str):
    from transformers import AutoTokenizer

    tokenizer = AutoTokenizer.from_pretrained(model_id, trust_remote_code=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    return tokenizer


def _load_causal_lm(model_id: str, load_in_4bit: bool):
    import torch
    from transformers import AutoModelForCausalLM

    if not load_in_4bit:
        logger.info("Loading model (full precision, device_map=auto): %s", model_id)
        return AutoModelForCausalLM.from_pretrained(
            model_id,
            trust_remote_code=True,
            device_map="auto",
        )

    # NVIDIA CUDA — bitsandbytes 4bit NF4
    if torch.cuda.is_available():
        try:
            from transformers import BitsAndBytesConfig

            qconfig = BitsAndBytesConfig(
                load_in_4bit=True,
                bnb_4bit_compute_dtype=torch.float16,
                bnb_4bit_quant_type="nf4",
                bnb_4bit_use_double_quant=True,
            )
            logger.info("Loading model in 4-bit NF4 (CUDA): %s", model_id)
            return AutoModelForCausalLM.from_pretrained(
                model_id,
                quantization_config=qconfig,
                device_map="auto",
                trust_remote_code=True,
            )
        except Exception as e:
            logger.warning("4-bit CUDA load failed, falling back: %s", e)

    # Apple Silicon — bitsandbytes 4bit 미지원 시 fp16 MPS
    if torch.backends.mps.is_available():
        logger.warning(
            "CHATBOT_LOAD_IN_4BIT=true 이지만 이 Mac에는 CUDA가 없습니다. "
            "fp16 + MPS로 로드합니다 (진짜 4bit는 NVIDIA GPU 서버에서만)."
        )
        return AutoModelForCausalLM.from_pretrained(
            model_id,
            trust_remote_code=True,
            torch_dtype=torch.float16,
            low_cpu_mem_usage=True,
            device_map={"": "mps"},
        )

    logger.warning("4-bit unavailable; loading fp32 on CPU (very slow).")
    return AutoModelForCausalLM.from_pretrained(
        model_id,
        trust_remote_code=True,
        low_cpu_mem_usage=True,
    )


def get_model_and_tokenizer():
    global _model, _tokenizer
    with _lock:
        if _model is not None:
            return _model, _tokenizer

        from rag.config import LOAD_IN_4BIT, MODEL_ID

        _tokenizer = _load_tokenizer(MODEL_ID)
        _model = _load_causal_lm(MODEL_ID, load_in_4bit=LOAD_IN_4BIT)
        logger.info("Model ready: %s (4bit_requested=%s)", MODEL_ID, LOAD_IN_4BIT)
        return _model, _tokenizer
