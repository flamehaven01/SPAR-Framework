"""Generic Layer A -- claim anchor and scope bounding checks."""

from __future__ import annotations

from typing import Any

from spar_framework.result_types import CheckResult


def _profile(subject: dict[str, Any]) -> dict[str, Any]:
    profile = subject.get("claim_profile")
    return profile if isinstance(profile, dict) else {}


def check_a1_claim_anchor(subject: dict[str, Any]) -> CheckResult:
    """A claim must have at least one evidence reference."""
    profile = _profile(subject)
    if not profile.get("claim_made", False):
        return CheckResult(
            "A1", "Claim anchor", "PASS",
            "claim_made=false; no anchor required.",
        )
    if not profile.get("evidence_cited", False):
        return CheckResult(
            "A1", "Claim anchor", "FAIL",
            "claim_made=true but evidence_cited=false. Claim lacks an anchor.",
        )
    return CheckResult(
        "A1", "Claim anchor", "CONSISTENT",
        "Claim is anchored by cited evidence.",
    )


def check_a2_scope_bounded(subject: dict[str, Any]) -> CheckResult:
    """A claim should declare its scope of applicability."""
    profile = _profile(subject)
    if not profile.get("claim_made", False):
        return CheckResult(
            "A2", "Claim scope bounded", "PASS",
            "claim_made=false; scope check not required.",
        )
    if not profile.get("scope_bounded", False):
        return CheckResult(
            "A2", "Claim scope bounded", "GAP",
            "claim_made=true but scope_bounded=false. Claim scope is unstated.",
        )
    return CheckResult(
        "A2", "Claim scope bounded", "CONSISTENT",
        "Claim scope is bounded.",
    )


def build_layer_a_checks(
    *,
    subject: dict[str, Any],
    source: str = "",
    gate: str = "",
    params: dict[str, Any] | None = None,
    context: dict[str, Any] | None = None,
) -> list[CheckResult]:
    del source, gate, params, context
    return [
        check_a1_claim_anchor(subject),
        check_a2_scope_bounded(subject),
    ]
