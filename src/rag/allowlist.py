"""allowlist 검증 — 허용 폴더·도메인만 수집."""
from __future__ import annotations

from pathlib import Path
from urllib.parse import urlparse

from src.config_loader import load_sources_config
from src.utils.paths import PROJECT_ROOT


def _normalize_ext(ext: str) -> str:
    e = ext.lower()
    return e if e.startswith(".") else f".{e}"


def get_allowed_roots() -> list[Path]:
    cfg = load_sources_config()
    local = cfg.get("local") or {}
    if not local.get("enabled", True):
        return []
    roots: list[Path] = []
    for rel in local.get("allowed_roots") or []:
        p = (PROJECT_ROOT / rel).resolve()
        roots.append(p)
    return roots


def get_allowed_extensions() -> set[str]:
    cfg = load_sources_config()
    exts = cfg.get("local", {}).get("allowed_extensions") or []
    return {_normalize_ext(x) for x in exts}


def is_path_allowed(file_path: Path, follow_symlinks: bool | None = None) -> bool:
    """파일이 allowlist 루트 안에 있고 확장자가 허용되는지 확인."""
    cfg = load_sources_config()
    local = cfg.get("local") or {}
    if not local.get("enabled", True):
        return False

    follow = (
        follow_symlinks
        if follow_symlinks is not None
        else local.get("follow_symlinks", False)
    )
    try:
        resolved = file_path.resolve() if follow else file_path.absolute()
    except OSError:
        return False

    if not resolved.is_file():
        return False

    if resolved.suffix.lower() not in get_allowed_extensions():
        return False

    for root in get_allowed_roots():
        root_resolved = root.resolve()
        try:
            resolved.relative_to(root_resolved)
            return True
        except ValueError:
            continue
    return False


def is_url_allowed(url: str) -> bool:
    cfg = load_sources_config()
    web = cfg.get("web") or {}
    if not web.get("enabled", False):
        return False

    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https"):
        return False

    host = (parsed.hostname or "").lower()
    allowed_domains = [d.lower() for d in (web.get("allowed_domains") or [])]
    if not allowed_domains or host not in allowed_domains:
        return False

    prefixes = web.get("allowed_path_prefixes") or []
    if prefixes:
        path = parsed.path or "/"
        if not any(path.startswith(p) for p in prefixes):
            return False
    return True
