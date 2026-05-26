"""마크다운 YAML frontmatter 파싱."""
from __future__ import annotations

import re
from typing import Any

import yaml

_FRONTMATTER = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)


def split_frontmatter(text: str) -> tuple[dict[str, Any], str]:
    """(meta, body) — frontmatter 없으면 meta는 빈 dict."""
    m = _FRONTMATTER.match(text)
    if not m:
        return {}, text.strip()
    meta = yaml.safe_load(m.group(1)) or {}
    body = text[m.end() :].strip()
    return meta, body
