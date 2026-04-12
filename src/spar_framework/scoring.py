"""Explicit scoring and verdict policy."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .result_types import CheckResult


@dataclass(frozen=True)
class ReviewPolicy:
    score_table: dict[str, int]

    def verdict(self, score: int, layer_a_anomalies: int) -> str:
        if layer_a_anomalies >= 2:
            return "REJECT"
        if score >= 85:
            return "ACCEPT"
        if score >= 70:
            return "MINOR_REVISION"
        if score >= 50:
            return "MAJOR_REVISION"
        return "REJECT"


default_policy = ReviewPolicy(
    score_table={
        "ANOMALY": -15,
        "FAIL": -10,
        "GAP": -5,
        "WARN": -3,
        "APPROXIMATION": -2,
    }
)


def iter_checks(*layers: list["CheckResult"]) -> list["CheckResult"]:
    merged: list["CheckResult"] = []
    for layer in layers:
        merged.extend(layer)
    return merged


def score_delta(check: "CheckResult", policy: ReviewPolicy = default_policy) -> int:
    return policy.score_table.get(check.status, 0)


def count_layer_a_anomalies(layer_a: list["CheckResult"]) -> int:
    return sum(1 for check in layer_a if check.status == "ANOMALY")


def compute_score(
    layer_a: list["CheckResult"],
    layer_b: list["CheckResult"],
    layer_c: list["CheckResult"],
    slop_penalty: int = 0,
    policy: ReviewPolicy = default_policy,
) -> int:
    score = 100
    for check in iter_checks(layer_a, layer_b, layer_c):
        score += score_delta(check, policy)
    score -= slop_penalty
    return max(0, score)


def grade_from_score(score: int) -> str:
    return "PASS" if score >= 70 else "FAIL"


def journal_verdict(
    score: int,
    layer_a: list["CheckResult"],
    policy: ReviewPolicy = default_policy,
) -> str:
    return policy.verdict(score, count_layer_a_anomalies(layer_a))
