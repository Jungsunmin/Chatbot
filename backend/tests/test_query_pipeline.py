"""Query 파이프라인 단위 테스트."""
from rag.query_pipeline import build_query, build_search_text


def test_build_query_en():
    q = build_query("What documents for alien registration?", "en")
    assert q.response_lang == "en"
    assert q.normalized_query_en
    assert q.intent == "document_list"


def test_build_search_text_includes_terms():
    q = build_query("외국인등록 서류", "ko")
    text = build_search_text(q)
    assert "제출서류" in text or "외국인" in text
