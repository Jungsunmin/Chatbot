"""프로젝트 루트 경로 유틸."""
from pathlib import Path

# Chatbot/ 디렉터리 (src/utils/paths.py 기준 상위 2단계)
PROJECT_ROOT = Path(__file__).resolve().parents[2]


def resolve_from_root(rel: str) -> Path:
    return (PROJECT_ROOT / rel).resolve()
