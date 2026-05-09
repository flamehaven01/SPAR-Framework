"""Explicit scoring and verdict policy loaded from packaged JSON."""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from typing import TYPE_CHECKING, Any

from .package_data import load_packaged_json

if TYPE_CHECKING:
    from .result_types import CheckResult


@lru_cache(maxsize=1)
def _load_review_policy() -> dict[str, Any]:
    return load_packaged_json("spar_framework", "policies", "review_policy.v1.json")


@dataclass(frozen=True)
class ReviewPolicy:
    score_table: dict[str, int]
    accept_threshold: int = 85
    minor_revision_threshold: int = 70
    major_revision_threshold: int = 50
    layer_a_anomaly_reject_count: int = 2
    pass_threshold: int = 70

    def verdict(self, score: int, layer_a_anomalies: int) -> str:
        if layer_a_anomalies >= self.layer_a_anomaly_reject_count:
            return "REJECT"
        if score >= self.accept_threshold:
            return "ACCEPT"
        if score >= self.minor_revision_threshold:
            return "MINOR_REVISION"
        if score >= self.major_revision_threshold:
            return "MAJOR_REVISION"
        return "REJECT"


def _build_default_policy() -> ReviewPolicy:
    data = _load_review_policy()
    return ReviewPolicy(
        score_table=data["scoring"]["penalties"],
        accept_threshold=data["verdict"]["accept_threshold"],
        minor_revision_threshold=data["verdict"]["minor_revision_threshold"],
        major_revision_threshold=data["verdict"]["major_revision_threshold"],
        layer_a_anomaly_reject_count=data["verdict"]["layer_a_anomaly_reject_count"],
        pass_threshold=data["grade"]["pass_threshold"],
    )


default_policy: ReviewPolicy = _build_default_policy()


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


def grade_from_score(score: int, policy: ReviewPolicy = default_policy) -> str:
    return "PASS" if score >= policy.pass_threshold else "FAIL"


def journal_verdict(
    score: int,
    layer_a: list["CheckResult"],
    policy: ReviewPolicy = default_policy,
) -> str:
    return policy.verdict(score, count_layer_a_anomalies(layer_a))


def compute_claim_drift(
    layer_a: list["CheckResult"],
    layer_b: list["CheckResult"],
    layer_c: list["CheckResult"],
    policy: ReviewPolicy = default_policy,
) -> int:
    """Sum of detected structural penalties from subject checks, excluding slop.

    Distinct from (100 - score) when slop_penalty > 0.
    framework_declared checks are excluded: they describe adapter limitations,
    not subject drift.
    """
    return sum(
        abs(score_delta(check, policy))
        for check in iter_checks(layer_a, layer_b, layer_c)
    )


def compute_coverage_rate(
    layer_a: list["CheckResult"],
    layer_b: list["CheckResult"],
    layer_c: list["CheckResult"],
) -> float:
    """Fraction of subject checks that returned a determinate result.

    CANNOT_CHECK counts as uncovered. framework_declared is excluded entirely
    because those checks characterise adapter limitations, not the subject.
    """
    all_checks = list(iter_checks(layer_a, layer_b, layer_c))
    if not all_checks:
        return 0.0
    covered = sum(1 for check in all_checks if check.status != "CANNOT_CHECK")
    return round(covered / len(all_checks), 4)
