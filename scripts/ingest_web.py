#!/usr/bin/env python3
"""allowlist 도메인·URL만 웹 수집 (선택)."""
from __future__ import annotations

import json
import sys
from pathlib import Path
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.config_loader import load_sources_config
from src.rag.allowlist import is_url_allowed
from src.utils.paths import PROJECT_ROOT

MANIFEST_PATH = PROJECT_ROOT / "data" / "processed" / "ingest_manifest.jsonl"


def _fetch_text(url: str, timeout: int = 15) -> str:
    resp = requests.get(url, timeout=timeout, headers={"User-Agent": "ExchangeStudentBot/1.0"})
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")
    for tag in soup(["script", "style", "nav", "footer"]):
        tag.decompose()
    return soup.get_text(separator="\n", strip=True)


def run() -> int:
    cfg = load_sources_config()
    web = cfg.get("web") or {}
    if not web.get("enabled", False):
        print("web.enabled is false — nothing to do")
        return 0

    seeds = web.get("seed_urls") or []
    max_pages = int(web.get("max_pages_per_domain", 100))
    visited: set[str] = set()
    entries: list[dict] = []

    for seed in seeds:
        if not is_url_allowed(seed):
            print(f"[deny] URL not in allowlist: {seed}")
            continue
        queue = [seed]
        domain = urlparse(seed).hostname
        count = 0
        while queue and count < max_pages:
            url = queue.pop(0)
            if url in visited:
                continue
            visited.add(url)
            if not is_url_allowed(url):
                continue
            try:
                text = _fetch_text(url)
            except Exception as e:
                print(f"[err] {url}: {e}")
                continue
            if text.strip():
                entries.append(
                    {
                        "source_type": "web",
                        "source_uri": url,
                        "source_domain": domain,
                        "filename": url,
                        "category": "general",
                        "lang": "en",
                        "verified": True,
                        "text_preview_len": len(text),
                        "_full_text": text,
                    }
                )
                print(f"[ok] {url}")
            count += 1
            # 같은 도메인 링크만 1단계 확장 (단순 MVP)
            try:
                resp = requests.get(url, timeout=15, headers={"User-Agent": "ExchangeStudentBot/1.0"})
                soup = BeautifulSoup(resp.text, "html.parser")
                for a in soup.find_all("a", href=True):
                    next_url = urljoin(url, a["href"])
                    if is_url_allowed(next_url) and next_url not in visited:
                        queue.append(next_url)
            except Exception:
                pass

    MANIFEST_PATH.parent.mkdir(parents=True, exist_ok=True)
    mode = "a" if MANIFEST_PATH.exists() else "w"
    with MANIFEST_PATH.open(mode, encoding="utf-8") as f:
        for e in entries:
            out = {k: v for k, v in e.items() if k != "_full_text"}
            f.write(json.dumps(out, ensure_ascii=False) + "\n")

    # 웹 전문은 별도 캐시 (재청킹용)
    cache_dir = PROJECT_ROOT / "data" / "processed" / "web_cache"
    cache_dir.mkdir(parents=True, exist_ok=True)
    for e in entries:
        if "_full_text" in e:
            safe = urlparse(e["source_uri"]).netloc.replace(".", "_")
            (cache_dir / f"{safe}_{hash(e['source_uri']) % 10**8}.txt").write_text(
                e["_full_text"], encoding="utf-8"
            )

    print(f"Appended {len(entries)} web entries")
    return 0


if __name__ == "__main__":
    raise SystemExit(run())
