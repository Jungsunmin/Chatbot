"""chunk_markdown 단위 테스트 — 소제목 분할과 문장 경계 슬라이싱."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from rag.chunking import chunk_markdown


def test_splits_on_markdown_subsection_headers():
    text = (
        "## 1. Alien Registration\n\n"
        "### A. Eligibility\n\n"
        "Foreign nationals who intend to stay more than 90 days.\n\n"
        "### B. Application Period\n\n"
        "Must apply within 90 days of entry."
    )
    chunks = chunk_markdown(text, "doc.md", "Guide", "en")
    titles = [c.section_title for c in chunks]
    assert any("A. Eligibility" in t for t in titles)
    assert any("B. Application Period" in t for t in titles)


def test_splits_on_plain_lettered_lines():
    text = (
        "## 1. National Health Insurance\n\n"
        "A. Covers approximately 50% of medical expenses.\n\n"
        "B. Enrollment is mandatory."
    )
    chunks = chunk_markdown(text, "doc.md", "Guide", "en")
    titles = [c.section_title for c in chunks]
    assert any("A. Covers" in t for t in titles)
    assert any("B. Enrollment" in t for t in titles)


def test_long_section_breaks_at_sentence_boundary_not_mid_word():
    sentence = "This is a required document for the application. "
    body = sentence * 20  # far beyond max_chars=600
    text = f"## 1. Required Documents\n\n{body}"
    chunks = chunk_markdown(text, "doc.md", "Guide", "en", max_chars=600, min_chars=20)
    assert len(chunks) > 1
    for c in chunks[:-1]:
        # 문장 중간에서 잘리지 않고 항상 "다." 같은 문장부호 뒤에서 끝나야 함
        assert c.text.rstrip().endswith(".")
        stripped = c.text.strip()
        last_word = stripped.split()[-1]
        assert last_word.endswith(".")


def test_hard_cut_fallback_for_single_long_token():
    # 경계 후보가 전혀 없는 매우 긴 단일 토큰 — max_chars에서 하드 컷 폴백
    text = "## 1. Section\n\n" + ("a" * 1500)
    chunks = chunk_markdown(text, "doc.md", "Guide", "en", max_chars=600, min_chars=20)
    assert len(chunks) >= 2
    assert all(len(c.text) <= 600 for c in chunks)
