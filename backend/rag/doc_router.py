"""질문 → doc_id/subcategory 라우팅.

규칙은 소스 md의 frontmatter(`route_patterns`)에서 동적으로 읽어온다 — 하드코딩 리스트가
아니므로 새 문서를 추가/변경할 때 이 파일을 고칠 필요가 없다. `route_priority`(낮을수록
먼저 매칭)로 문서 간 순서를, `route_exclude_patterns`로 문서 내 예외를 표현한다.
"""
from __future__ import annotations

import logging
import re
from dataclasses import dataclass

from rag.indexer import list_sources

logger = logging.getLogger(__name__)

_SUPPORTED_LANGS = ("ko", "en", "zh", "ja")


@dataclass(frozen=True)
class DocRoute:
    doc_id: str
    subcategory: str


@dataclass(frozen=True)
class _RouteRule:
    pattern: re.Pattern
    exclude: re.Pattern | None
    doc_ids: dict[str, str]
    subcategory: str
    priority: int


def _compile_or(patterns: list[str]) -> re.Pattern | None:
    if not patterns:
        return None
    combined = "|".join(f"(?:{p})" for p in patterns)
    return re.compile(combined, re.I)


def _build_rules() -> list[_RouteRule]:
    rules: list[_RouteRule] = []
    for src in list_sources():
        if not src.route_patterns:
            continue
        try:
            pattern = _compile_or(src.route_patterns)
            exclude = _compile_or(src.route_exclude_patterns)
        except re.error as e:
            logger.warning("Invalid route_patterns for doc_id=%s: %s", src.doc_id, e)
            continue
        if pattern is None:
            continue
        rules.append(
            _RouteRule(
                pattern=pattern,
                exclude=exclude,
                doc_ids={lang: src.doc_id for lang in _SUPPORTED_LANGS},
                subcategory=src.doc_type or src.category or "",
                priority=src.route_priority,
            )
        )
    rules.sort(key=lambda r: r.priority)
    logger.info("Loaded %d route rules from source frontmatter", len(rules))
    return rules


_rules_cache: list[_RouteRule] | None = None


def _get_rules() -> list[_RouteRule]:
    global _rules_cache
    if _rules_cache is None:
        _rules_cache = _build_rules()
    return _rules_cache


def refresh_route_rules() -> None:
    """소스 변경/재인덱싱 후 라우팅 규칙 캐시를 강제로 다시 빌드."""
    global _rules_cache
    _rules_cache = _build_rules()


def _pick_doc_id(doc_ids: dict[str, str], lang: str) -> str | None:
    """요청 언어의 doc_id 우선, 없으면 큐레이션된 다른 언어로 폴백."""
    if lang in doc_ids:
        return doc_ids[lang]
    return next(iter(doc_ids.values()), None)


def resolve_doc_route(query: str, lang: str = "ko") -> DocRoute | None:
    """질문 + 응답 언어에서 가장 적합한 가이드북 doc_id 추정. 없으면 None."""
    q = query.strip()
    if not q:
        return None

    for rule in _get_rules():
        if rule.exclude and rule.exclude.search(q):
            continue
        if rule.pattern.search(q):
            doc_id = _pick_doc_id(rule.doc_ids, lang)
            if doc_id:
                return DocRoute(doc_id=doc_id, subcategory=rule.subcategory)

    return None
