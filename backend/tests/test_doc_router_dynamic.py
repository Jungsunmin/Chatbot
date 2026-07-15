"""doc_router가 하드코딩 리스트가 아니라 실제로 frontmatter(route_patterns)를 읽어서
라우팅 규칙을 만든다는 것을 검증 — list_sources()를 몽키패치해 가짜 문서를 주입한다."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import rag.doc_router as doc_router
from rag.indexer import LoadedSource


def _fake_source(**overrides) -> LoadedSource:
    base = dict(
        source_id="fake.md",
        title="Fake Doc",
        lang="en",
        body="fake body",
        doc_id="fake-doc-id",
        doc_type="fake_category",
        route_patterns=[],
        route_exclude_patterns=[],
        route_priority=100,
    )
    base.update(overrides)
    return LoadedSource(**base)


def _reset_cache():
    doc_router._rules_cache = None


def test_resolve_doc_route_reads_frontmatter_patterns(monkeypatch):
    fake = _fake_source(doc_id="totally-made-up-doc", route_patterns=["아주특이한키워드테스트"])
    monkeypatch.setattr(doc_router, "list_sources", lambda: [fake])
    _reset_cache()
    try:
        route = doc_router.resolve_doc_route("아주특이한키워드테스트가 뭐예요", "ko")
        assert route is not None
        assert route.doc_id == "totally-made-up-doc"
    finally:
        _reset_cache()


def test_resolve_doc_route_no_match_returns_none(monkeypatch):
    fake = _fake_source(doc_id="totally-made-up-doc", route_patterns=["아주특이한키워드테스트"])
    monkeypatch.setattr(doc_router, "list_sources", lambda: [fake])
    _reset_cache()
    try:
        route = doc_router.resolve_doc_route("전혀 관련 없는 질문", "ko")
        assert route is None
    finally:
        _reset_cache()


def test_exclude_pattern_suppresses_match(monkeypatch):
    fake = _fake_source(
        doc_id="totally-made-up-doc",
        route_patterns=["키워드"],
        route_exclude_patterns=["제외단어"],
    )
    monkeypatch.setattr(doc_router, "list_sources", lambda: [fake])
    _reset_cache()
    try:
        assert doc_router.resolve_doc_route("키워드 질문", "ko") is not None
        assert doc_router.resolve_doc_route("키워드 제외단어 질문", "ko") is None
    finally:
        _reset_cache()


def test_priority_order_across_sources(monkeypatch):
    general = _fake_source(doc_id="general-doc", route_patterns=["공통"], route_priority=100)
    specific = _fake_source(doc_id="specific-doc", route_patterns=["공통 특수"], route_priority=10)
    monkeypatch.setattr(doc_router, "list_sources", lambda: [general, specific])
    _reset_cache()
    try:
        route = doc_router.resolve_doc_route("공통 특수 케이스 질문", "ko")
        assert route is not None
        assert route.doc_id == "specific-doc"
    finally:
        _reset_cache()


def test_refresh_route_rules_rebuilds_cache(monkeypatch):
    monkeypatch.setattr(doc_router, "list_sources", lambda: [])
    _reset_cache()
    try:
        assert doc_router.resolve_doc_route("아무 질문", "ko") is None

        fake = _fake_source(doc_id="new-doc", route_patterns=["새로생긴키워드"])
        monkeypatch.setattr(doc_router, "list_sources", lambda: [fake])
        doc_router.refresh_route_rules()

        route = doc_router.resolve_doc_route("새로생긴키워드 질문", "ko")
        assert route is not None
        assert route.doc_id == "new-doc"
    finally:
        _reset_cache()
