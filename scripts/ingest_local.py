#!/usr/bin/env python3
"""allowlist 로컬 폴더만 스캔하여 ingest manifest 생성."""
from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.rag.allowlist import get_allowed_roots, is_path_allowed
from src.rag.text_extract import extract_text
from src.utils.paths import PROJECT_ROOT

MANIFEST_PATH = PROJECT_ROOT / "data" / "processed" / "ingest_manifest.jsonl"
MANIFEST_CSV = PROJECT_ROOT / "data" / "sources" / "manifest.csv"


def _load_manifest_csv() -> dict[str, dict]:
    """파일명 → category, lang 메타 (선택)."""
    meta: dict[str, dict] = {}
    if not MANIFEST_CSV.exists():
        return meta
    with MANIFEST_CSV.open(encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            fname = (row.get("filename") or "").strip()
            if fname:
                meta[fname] = {
                    "category": row.get("category") or "general",
                    "lang": row.get("lang") or "en",
                    "verified": (row.get("verified") or "true").lower() == "true",
                }
    return meta


def _guess_meta(filename: str) -> dict:
    lower = filename.lower()
    lang = "ko" if "_ko" in lower or "-ko." in lower else "en"
    category = "general"
    for cat in (
        "housing",
        "visa",
        "course_registration",
        "orientation",
        "insurance",
    ):
        if cat.replace("_", "") in lower.replace("_", ""):
            category = cat
            break
    return {"category": category, "lang": lang, "verified": True}


def run() -> int:
    MANIFEST_PATH.parent.mkdir(parents=True, exist_ok=True)
    csv_meta = _load_manifest_csv()
    entries: list[dict] = []

    for root in get_allowed_roots():
        if not root.exists():
            print(f"[skip] root not found: {root}")
            continue
        for path in sorted(root.rglob("*")):
            if not path.is_file():
                continue
            if not is_path_allowed(path):
                print(f"[deny] outside allowlist: {path}")
                continue
            text = extract_text(path)
            if not text.strip():
                print(f"[warn] empty text: {path}")
                continue
            rel = str(path.relative_to(PROJECT_ROOT))
            meta = csv_meta.get(path.name) or _guess_meta(path.name)
            entries.append(
                {
                    "source_type": "local",
                    "source_uri": rel,
                    "source_domain": None,
                    "filename": path.name,
                    "text_preview_len": len(text),
                    **meta,
                }
            )
            print(f"[ok] {rel}")

    with MANIFEST_PATH.open("w", encoding="utf-8") as f:
        for e in entries:
            f.write(json.dumps(e, ensure_ascii=False) + "\n")

    print(f"Wrote {len(entries)} entries -> {MANIFEST_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(run())
