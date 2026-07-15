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
MAX_QUERY_LENGTH = int(os.getenv("CHATBOT_MAX_QUERY_LENGTH", "300"))
CHROMA_COLLECTION = "ku_intl_docs"

# 설정돼 있으면 /admin/reindex에 X-Admin-Token 헤더 일치를 요구. 빈 값(기본)이면 로컬 개발처럼 무인증 허용.
ADMIN_TOKEN = os.getenv("CHATBOT_ADMIN_TOKEN", "")

# 콤마 구분 origin 목록. 기본값 "*"(전체 허용) — 배포 시 명시적 도메인 목록으로 교체 권장.
CORS_ORIGINS = os.getenv("CHATBOT_CORS_ORIGINS", "*")

# Chroma cosine distance — 낮을수록 유사. env로 조정 가능.
DISTANCE_HIGH_MAX = float(os.getenv("CHATBOT_DISTANCE_HIGH_MAX", "0.35"))
DISTANCE_LOW_MAX = float(os.getenv("CHATBOT_DISTANCE_LOW_MAX", "0.55"))
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
