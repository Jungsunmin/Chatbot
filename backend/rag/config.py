"""RAG·모델 경로 및 환경 변수."""
from pathlib import Path

import os

# backend/ 기준 경로
BACKEND_ROOT = Path(__file__).resolve().parents[1]
SOURCES_DIR = BACKEND_ROOT / "data" / "sources"
INDEX_DIR = BACKEND_ROOT / "data" / "index"

MODEL_ID = os.getenv("CHATBOT_MODEL_ID", "Qwen/Qwen2.5-0.5B-Instruct")
EMBEDDING_MODEL = os.getenv(
    "CHATBOT_EMBEDDING_MODEL",
    "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
)
TOP_K = int(os.getenv("CHATBOT_TOP_K", "4"))
CHROMA_COLLECTION = "ku_intl_docs"
