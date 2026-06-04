#!/usr/bin/env python3
"""
urls.yaml 에 등록된 URL만 가져와 backend/data/sources/web/*.md 로 저장.
하위 링크 자동 크롤링 없음 (rag_scope: single_page_only).

사용: cd backend && python scripts/ingest_urls.py
"""
from __future__ import annotations

import sys
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from rag.config import SOURCES_DIR
from rag.url_fetch import fetch_page_text

URLS_FILE = SOURCES_DIR / "urls.yaml"
WEB_DIR = SOURCES_DIR / "web"


def _build_md(entry: dict, body: str) -> str:
    meta = {
        "label": entry["label"],
        "title": entry["title"],
        "source_url": entry["url"],
        "category": entry.get("category", ""),
        "type": entry.get("type", ""),
        "lang": entry.get("lang", "ko"),
        "rag_scope": entry.get("rag_scope", "single_page_only"),
    }
    header = yaml.dump(meta, allow_unicode=True, sort_keys=False).strip()
    return f"---\n{header}\n---\n\n# {entry['title']}\n\n{body}\n"


def main() -> None:
    if not URLS_FILE.exists():
        print(f"Missing {URLS_FILE}")
        sys.exit(1)

    data = yaml.safe_load(URLS_FILE.read_text(encoding="utf-8")) or {}
    sources = data.get("sources") or []
    WEB_DIR.mkdir(parents=True, exist_ok=True)

    for entry in sources:
        label = entry["label"]
        url = entry["url"]
        out = WEB_DIR / f"{label}_{entry.get('lang', 'ko')}.md"
        print(f"Fetching {label}: {url}")
        try:
            body = fetch_page_text(url)
        except Exception as e:
            print(f"  FAILED: {e}")
            continue
        if len(body) < 50:
            print(f"  WARN: very short content ({len(body)} chars)")
        out.write_text(_build_md(entry, body), encoding="utf-8")
        print(f"  -> {out} ({len(body)} chars)")

    print("Done. Run: python scripts/build_index.py")


if __name__ == "__main__":
    main()
