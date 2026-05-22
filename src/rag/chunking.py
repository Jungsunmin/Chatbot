"""텍스트 청킹."""
from __future__ import annotations


def chunk_text(
    text: str,
    chunk_size: int = 450,
    overlap: int = 50,
) -> list[str]:
    text = " ".join(text.split())
    if not text:
        return []
    if len(text) <= chunk_size:
        return [text]

    chunks: list[str] = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end].strip())
        if end >= len(text):
            break
        start = end - overlap
    return [c for c in chunks if c]
