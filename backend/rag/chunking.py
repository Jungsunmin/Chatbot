"""마크다운·텍스트를 섹션 단위 RAG 청크로 분할."""
from __future__ import annotations

import re
from dataclasses import dataclass

# 소제목 경계 (가이드북 HTML ingest 형식)
_SUBSECTION_SPLIT = re.compile(
    r"\n(?=(?:다\.|나\.|라\.|가\.|마\.|바\.)\s+[^\n])"
)


@dataclass
class Chunk:
    text: str        # 원본 텍스트 — LLM 프롬프트·citations 표시용
    embed_text: str  # 컨텍스트 prefix 붙인 텍스트 — 임베딩 전용
    source_id: str
    title: str
    lang: str
    source_url: str = ""
    label: str = ""
    doc_type: str = ""
    section_title: str = ""


def _embed_prefix(doc_title: str, section_title: str) -> str:
    """임베딩용 컨텍스트 prefix.

    동일 표현("14일 이내", "제출서류" 등)이 여러 문서에 있을 때
    임베딩 벡터가 문서마다 달라지도록 문서·섹션 정보를 앞에 붙인다.
    """
    if section_title and section_title != doc_title:
        return f"{doc_title} > {section_title}: "
    return f"{doc_title}: "


def _emit_pieces(
    text: str,
    source_id: str,
    page_title: str,
    lang: str,
    section_title: str,
    max_chars: int,
    min_chars: int,
    out: list[Chunk],
) -> None:
    block = text.strip()
    if not block or len(block) < min_chars:
        return
    prefix = _embed_prefix(page_title, section_title)
    while len(block) > max_chars:
        piece = block[:max_chars]
        out.append(
            Chunk(
                text=piece,
                embed_text=prefix + piece,
                source_id=source_id,
                title=page_title,
                lang=lang,
                section_title=section_title,
            )
        )
        block = block[max_chars:]
    if block:
        out.append(
            Chunk(
                text=block,
                embed_text=prefix + block,
                source_id=source_id,
                title=page_title,
                lang=lang,
                section_title=section_title,
            )
        )


def chunk_markdown(
    text: str,
    source_id: str,
    title: str,
    lang: str,
    max_chars: int = 600,
    min_chars: int = 20,
) -> list[Chunk]:
    """## 및 다./나./라. 소제목 기준 분할.

    각 청크는 text(원본)와 embed_text(contextual prefix 포함)를 별도 보유.
    min_chars 미만(제목만 있는 청크 등)은 제외.
    """
    chunks: list[Chunk] = []
    major_blocks = re.split(r"\n(?=## )", text.strip())

    for major in major_blocks:
        major = major.strip()
        if not major:
            continue

        section_path = title
        if major.startswith("## "):
            first_line = major.split("\n", 1)[0]
            section_path = first_line.replace("##", "").strip()
            body = major.split("\n", 1)[1] if "\n" in major else ""
        else:
            body = major

        if not body.strip():
            _emit_pieces(major, source_id, title, lang, section_path, max_chars, min_chars, chunks)
            continue

        sub_parts = _SUBSECTION_SPLIT.split(body)
        if len(sub_parts) <= 1:
            _emit_pieces(body, source_id, title, lang, section_path, max_chars, min_chars, chunks)
            continue

        for sub in sub_parts:
            sub = sub.strip()
            if not sub:
                continue
            sub_title = section_path
            head = sub.split("\n", 1)[0].strip()
            if re.match(r"^[가-힣a-zA-Z]?\.?\s*", head) and len(head) < 80:
                sub_title = f"{section_path} > {head}"
            _emit_pieces(sub, source_id, title, lang, sub_title, max_chars, min_chars, chunks)

    return chunks
