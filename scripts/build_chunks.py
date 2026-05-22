#!/usr/bin/env python3
"""manifest + 로컬 파일 → chunks.jsonl."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.rag.chunking import chunk_text
from src.rag.text_extract import extract_text
from src.utils.paths import PROJECT_ROOT

MANIFEST_PATH = PROJECT_ROOT / "data" / "processed" / "ingest_manifest.jsonl"
CHUNKS_PATH = PROJECT_ROOT / "data" / "processed" / "chunks.jsonl"
WEB_CACHE = PROJECT_ROOT / "data" / "processed" / "web_cache"


def _read_manifest() -> list[dict]:
    if not MANIFEST_PATH.exists():
        return []
    rows = []
    with MANIFEST_PATH.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def _text_for_entry(entry: dict) -> str:
    if entry.get("source_type") == "web":
        uri = entry.get("source_uri", "")
        for p in WEB_CACHE.glob("*.txt"):
            if uri in p.read_text(encoding="utf-8", errors="replace")[:200]:
                pass
        # seed crawl 시 캐시 파일명이 hash 기반이라 manifest 순회로 매칭 어려움 → ingest_web 개선 전 로컬만 권장
        return ""
    rel = entry.get("source_uri", "")
    path = PROJECT_ROOT / rel
    if path.is_file():
        return extract_text(path)
    return ""


def run() -> int:
    entries = _read_manifest()
    if not entries:
        print(f"No manifest at {MANIFEST_PATH}. Run ingest_local.py first.")
        return 1

    CHUNKS_PATH.parent.mkdir(parents=True, exist_ok=True)
    chunk_count = 0
    with CHUNKS_PATH.open("w", encoding="utf-8") as out:
        for entry in entries:
            if not entry.get("verified", True):
                continue
            text = _text_for_entry(entry)
            if not text.strip() and entry.get("source_type") == "web":
                print(f"[skip] web text missing (re-run ingest or use local): {entry.get('source_uri')}")
                continue
            if not text.strip():
                print(f"[skip] empty: {entry.get('source_uri')}")
                continue

            category = entry.get("category", "general")
            lang = entry.get("lang", "en")
            source_uri = entry.get("source_uri", "")
            source_type = entry.get("source_type", "local")
            source_domain = entry.get("source_domain")

            for i, piece in enumerate(chunk_text(text)):
                chunk_id = f"{category}-{lang}-{hash(source_uri) % 10**8}-{i}"
                row = {
                    "chunk_id": chunk_id,
                    "text": piece,
                    "lang": lang,
                    "category": category,
                    "slots": entry.get("slots") or {},
                    "source_type": source_type,
                    "source_uri": source_uri,
                    "source_domain": source_domain,
                    "verified": True,
                }
                out.write(json.dumps(row, ensure_ascii=False) + "\n")
                chunk_count += 1

    print(f"Wrote {chunk_count} chunks -> {CHUNKS_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(run())
