"""MICA runtime discovery and context loading for SPAR workflows."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import yaml


def discover_mica_runtime(project_root: str | Path) -> dict[str, Any]:
    """Discover MICA runtime state using the v0.2.2 detection order."""
    root = Path(project_root).resolve()
    mica_yaml = root / "mica.yaml"
    memory_mica_yaml = root / "memory" / "mica.yaml"
    archive_candidates = sorted(
        (root / "memory").glob("*.mica.*.json"),
        reverse=True,
    )

    if mica_yaml.exists():
        return {
            "state": "INVOCATION_MODE",
            "project_root": str(root),
            "mica_path": str(mica_yaml),
            "archive_path": None,
        }
    if memory_mica_yaml.exists():
        return {
            "state": "INVOCATION_MODE",
            "project_root": str(root),
            "mica_path": str(memory_mica_yaml),
            "archive_path": None,
        }
    if archive_candidates:
        return {
            "state": "LEGACY_MODE",
            "project_root": str(root),
            "mica_path": None,
            "archive_path": str(archive_candidates[0]),
        }
    return {
        "state": "INACTIVE",
        "project_root": str(root),
        "mica_path": None,
        "archive_path": None,
    }


def load_mica_runtime_context(
    *,
    project_root: str | Path | None = None,
    mica_context_path: str | Path | None = None,
) -> dict[str, Any] | None:
    """Load MICA runtime context from explicit path or project discovery."""
    if mica_context_path:
        path = Path(mica_context_path).resolve()
        if path.name == "mica.yaml":
            return _context_from_mica_yaml(path)
        loaded = _load_yaml(path)
        loaded.setdefault("_mica_runtime", {})
        loaded["_mica_runtime"].setdefault("state", "INVOCATION_MODE")
        loaded["_mica_runtime"].setdefault("source_path", str(path))
        return loaded

    if not project_root:
        return None

    discovery = discover_mica_runtime(project_root)
    if discovery["state"] == "INVOCATION_MODE":
        return _context_from_mica_yaml(Path(discovery["mica_path"]))
    if discovery["state"] == "LEGACY_MODE":
        return _context_from_legacy_archive(Path(discovery["archive_path"]))
    return None


def _context_from_mica_yaml(path: Path) -> dict[str, Any]:
    mica = _load_yaml(path)
    root = path.parent
    archive_layer = _resolve_layer_path(root, mica, "archive")
    playbook_layer = _resolve_layer_path(root, mica, "playbook")
    archive = _load_json(archive_layer) if archive_layer and archive_layer.exists() else {}
    invariants = _invariant_counts(archive)

    return {
        "project": {
            "name": mica.get("name") or archive.get("project", {}).get("name"),
            "full_name": archive.get("project", {}).get("full_name"),
        },
        "mode": mica.get("mode"),
        "pattern": mica.get("invocation_protocol", {}).get("primary_pattern"),
        "mica_spec": mica.get("mica_spec"),
        "archive_id": archive.get("operation_meta", {}).get("archive_id"),
        "last_updated": archive.get("operation_meta", {}).get("last_updated"),
        "pct_status": archive.get("operation_meta", {}).get("current_state"),
        "invariants": invariants,
        "loaded_layers": {
            "archive": _safe_layer_ref(root, archive_layer),
            "playbook": _safe_layer_ref(root, playbook_layer),
        },
        "_mica_runtime": {
            "state": "INVOCATION_MODE",
            "source_path": str(path),
            "project_root": str(root),
        },
    }


def _context_from_legacy_archive(path: Path) -> dict[str, Any]:
    archive = _load_json(path)
    invariants = _invariant_counts(archive)
    return {
        "project": {
            "name": archive.get("project", {}).get("name"),
            "full_name": archive.get("project", {}).get("full_name"),
        },
        "mode": archive.get("operation_meta", {}).get("operating_mode"),
        "pattern": None,
        "mica_spec": archive.get("mica_spec") or archive.get("mica_schema_version"),
        "archive_id": archive.get("operation_meta", {}).get("archive_id"),
        "last_updated": archive.get("operation_meta", {}).get("last_updated"),
        "pct_status": archive.get("operation_meta", {}).get("current_state"),
        "invariants": invariants,
        "loaded_layers": {
            "archive": path.name,
            "playbook": None,
        },
        "_mica_runtime": {
            "state": "LEGACY_MODE",
            "source_path": str(path),
            "project_root": str(path.parent.parent if path.parent.name == "memory" else path.parent),
        },
    }


def _resolve_layer_path(root: Path, mica: dict[str, Any], layer_name: str) -> Path | None:
    for layer in mica.get("layers", []):
        if layer.get("name") == layer_name and layer.get("path"):
            return (root / layer["path"]).resolve()
    return None


def _invariant_counts(archive: dict[str, Any]) -> dict[str, int]:
    counts = {"critical": 0, "high": 0, "total": 0}
    for item in archive.get("design_invariants", []) or []:
        counts["total"] += 1
        severity = item.get("severity")
        if severity == "critical":
            counts["critical"] += 1
        if severity == "high":
            counts["high"] += 1
    return counts


def _safe_layer_ref(root: Path, path: Path | None) -> str | None:
    if not path:
        return None
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return path.name


def _load_yaml(path: Path) -> dict[str, Any]:
    loaded = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(loaded, dict):
        raise ValueError(f"Expected mapping payload at {path}")
    return loaded


def _load_json(path: Path) -> dict[str, Any]:
    loaded = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(loaded, dict):
        raise ValueError(f"Expected object payload at {path}")
    return loaded
