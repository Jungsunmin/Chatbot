"""RAG·모델 경로 및 환경 변수."""
from pathlib import Path

import os

# backend/ 기준 경로
BACKEND_ROOT = Path(__file__).resolve().parents[1]
SOURCES_DIR = BACKEND_ROOT / "data" / "sources"
INDEX_DIR = BACKEND_ROOT / "data" / "index"

MODEL_ID = os.getenv("CHATBOT_MODEL_ID", "Qwen/Qwen2.5-1.5B-Instruct")
EMBEDDING_MODEL = os.getenv(
    "CHATBOT_EMBEDDING_MODEL",
    "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
)
TOP_K = int(os.getenv("CHATBOT_TOP_K", "4"))
# llm_rag: 검색 청크 → LLM (유일한 답변 경로)
ANSWER_MODE = os.getenv("CHATBOT_ANSWER_MODE", "llm_rag")
CHROMA_COLLECTION = "ku_intl_docs"

# Chroma cosine distance — 낮을수록 유사. env로 조정 가능.
DISTANCE_HIGH_MAX = float(os.getenv("CHATBOT_DISTANCE_HIGH_MAX", "0.35"))
DISTANCE_LOW_MAX = float(os.getenv("CHATBOT_DISTANCE_LOW_MAX", "0.55"))
PENDING_SESSION_TTL_SEC = int(os.getenv("CHATBOT_PENDING_TTL_SEC", "600"))
LANG_DETECT_MIN_CONFIDENCE = float(os.getenv("CHATBOT_LANG_DETECT_MIN_CONFIDENCE", "0.70"))


def _env_bool(name: str, default: bool) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.strip().lower() in ("1", "true", "yes", "on")


# 4bit NF4 (bitsandbytes, CUDA 권장). Mac은 fp16 MPS 등으로 자동 대체 가능
LOAD_IN_4BIT = _env_bool("CHATBOT_LOAD_IN_4BIT", True)
# 서버 시작 시 임베딩·LLM 미리 로드 (첫 /chat 지연·kill 중 오류 완화)
PRELOAD_MODELS = _env_bool("CHATBOT_PRELOAD_MODELS", True)
