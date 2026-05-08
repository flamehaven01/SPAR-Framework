"""Helpers for reading packaged JSON artifacts."""

from __future__ import annotations

import json
from importlib import resources
from typing import Any


def load_packaged_json(package: str, *parts: str) -> dict[str, Any]:
    path = resources.files(package)
    for part in parts:
        path = path.joinpath(part)
    loaded = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(loaded, dict):
        joined = "/".join(parts)
        raise ValueError(f"Packaged JSON payload must be an object: {package}/{joined}")
    return loaded
