#!/usr/bin/env python3
"""RAG 인덱스 수동 구축. backend/ 에서: python scripts/build_index.py"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from rag.indexer import build_index

if __name__ == "__main__":
    n = build_index(force=True)
    print(f"Indexed chunks: {n}")
