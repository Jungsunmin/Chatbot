"""마크다운·텍스트를 RAG용 청크로 분할."""
from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass
class Chunk:
    text: str
    source_id: str
    title: str
    lang: str


def chunk_markdown(text: str, source_id: str, title: str, lang: str, max_chars: int = 600) -> list[Chunk]:
    """## 헤더 또는 빈 줄 기준으로 나누고, 너무 긴 블록은 잘라 청크 생성."""
    blocks = re.split(r"\n(?=## )", text.strip())
    chunks: list[Chunk] = []
    for i, block in enumerate(blocks):
        block = block.strip()
        if not block:
            continue
        while len(block) > max_chars:
            chunks.append(
                Chunk(
                    text=block[:max_chars],
                    source_id=source_id,
                    title=title,
                    lang=lang,
                )
            )
            block = block[max_chars:]
        if block:
            chunks.append(
                Chunk(
                    text=block,
                    source_id=source_id,
                    title=title,
                    lang=lang,
                )
            )
    return chunks
