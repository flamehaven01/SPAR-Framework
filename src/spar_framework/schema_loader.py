"""Load packaged JSON schema artifacts for SPAR CLI contracts."""

from __future__ import annotations

from typing import Any

from .package_data import load_packaged_json

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
    return load_packaged_json("spar_framework", "schemas", schema_file)
