"""config/sources.yaml 로드."""
from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from src.utils.paths import PROJECT_ROOT


def load_sources_config(path: Path | None = None) -> dict[str, Any]:
    cfg_path = path or (PROJECT_ROOT / "config" / "sources.yaml")
    with cfg_path.open(encoding="utf-8") as f:
        return yaml.safe_load(f) or {}
