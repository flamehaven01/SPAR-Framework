"""Load packaged JSON schema artifacts for SPAR CLI contracts."""

from __future__ import annotations

import json
from importlib import resources
from typing import Any

SCHEMA_FILES = {
    "subject": "subject.physics.schema.json",
    "result": "result.schema.json",
    "context": "context.schema.json",
}


def schema_names() -> list[str]:
    return sorted(SCHEMA_FILES.keys())


def load_schema(name: str) -> dict[str, Any]:
    try:
        schema_file = SCHEMA_FILES[name]
    except KeyError as exc:
        raise ValueError(f"Unsupported schema target: {name}") from exc

    text = (
        resources.files("spar_framework")
        .joinpath("schemas")
        .joinpath(schema_file)
        .read_text(encoding="utf-8")
    )
    loaded = json.loads(text)
    if not isinstance(loaded, dict):
        raise ValueError(f"Schema payload must be a JSON object: {schema_file}")
    return loaded
