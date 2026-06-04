"""의도 분류·인용 dedupe 단위 테스트 (Chroma 불필요)."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from rag.intent import classify_intent, expand_query, required_terms_for_intent


def test_classify_document_list():
    assert classify_intent("외국인 등록에 필요한 서류가 뭐야?") == "document_list"
    assert classify_intent("what documents do I need") == "document_list"


def test_classify_reentry_general():
    assert classify_intent("재입국 허가 필요해?") == "general"


def test_expand_query_document():
    q = expand_query("외국인 등록 서류", "document_list")
    assert "제출서류" in q


def test_required_terms_when_query_has_seru():
    terms = required_terms_for_intent("document_list", "필요한 서류")
    assert "서류" in terms


def test_citation_dedupe_logic():
    docs = [
        {"source_url": "https://x.com", "source_id": "id1"},
        {"source_url": "https://x.com", "source_id": "id1"},
    ]
    seen: set[str] = set()
    count = 0
    for d in docs:
        key = d["source_url"] or d["source_id"]
        if key in seen:
            continue
        seen.add(key)
        count += 1
    assert count == 1
