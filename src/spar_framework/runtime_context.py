"""Runtime composition helpers for standalone SPAR."""

from __future__ import annotations

from typing import Any

from .result_types import CheckResult
from .scoring import compute_score, grade_from_score, journal_verdict


def build_core_review(
    *,
    layer_a: list[CheckResult],
    layer_b: list[CheckResult],
    layer_c: list[CheckResult],
    slop_penalty: int = 0,
) -> dict[str, Any]:
    score = compute_score(layer_a, layer_b, layer_c, slop_penalty)
    grade = grade_from_score(score)
    verdict = journal_verdict(score, layer_a)
    return {
        "score": score,
        "grade": grade,
        "verdict": verdict,
    }


def build_registry_snapshots(
    *,
    model_registry_snapshot: dict[str, Any] | None = None,
    gap_registry_snapshot: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return {
        "model_registry_snapshot": model_registry_snapshot,
        "gap_registry_snapshot": gap_registry_snapshot,
    }

