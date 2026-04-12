"""Minimal registry model for standalone SPAR."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class ModelSpec:
    model_id: str
    name: str
    maturity: str
    scope_note: str
    module_path: str = ""
    group: str = ""


@dataclass(frozen=True)
class GapSpec:
    check_id: str
    title: str
    state: str
    summary: str
    related_models: tuple[str, ...]


def model_registry_snapshot(models: list[ModelSpec]) -> dict[str, object]:
    grouped: dict[str, list[dict[str, str]]] = {}
    entries: list[dict[str, str]] = []
    for model in models:
        item = {
            "model_id": model.model_id,
            "name": model.name,
            "maturity": model.maturity,
            "scope_note": model.scope_note,
        }
        if model.module_path:
            item["module_path"] = model.module_path
        if model.group:
            item["group"] = model.group
            grouped.setdefault(model.group, []).append(item)
        entries.append(item)
    return {
        "total_models": len(models),
        "models": entries,
        "groups": grouped,
    }


def gap_registry_snapshot(gaps: list[GapSpec]) -> dict[str, object]:
    state_counts: dict[str, int] = {}
    for gap in gaps:
        state_counts[gap.state] = state_counts.get(gap.state, 0) + 1
    return {
        "total_gaps": len(gaps),
        "state_counts": state_counts,
        "gaps": [
            {
                "check_id": gap.check_id,
                "title": gap.title,
                "state": gap.state,
                "summary": gap.summary,
                "related_models": list(gap.related_models),
            }
            for gap in gaps
        ],
    }


def build_registry_snapshots(
    *,
    models: list[ModelSpec],
    gaps: list[GapSpec],
) -> dict[str, Any]:
    return {
        "model_registry_snapshot": model_registry_snapshot(models),
        "gap_registry_snapshot": gap_registry_snapshot(gaps),
    }
