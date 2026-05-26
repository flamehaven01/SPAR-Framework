"""Generic Layer C -- evidence-surface maturity probes."""

from __future__ import annotations

from typing import Any

from spar_framework.result_types import CheckResult


def check_c1_evidence_surface(subject: dict[str, Any]) -> CheckResult:
    profile = subject.get("claim_profile") if isinstance(subject.get("claim_profile"), dict) else {}
    if not profile.get("claim_made", False):
        return CheckResult(
            "C1", "Evidence surface", "PASS",
            "claim_made=false; evidence surface not required.",
        )
    if profile.get("evidence_cited", False):
        return CheckResult(
            "C1", "Evidence surface", "GENUINE",
            "Evidence is cited for the claim.",
        )
    return CheckResult(
        "C1", "Evidence surface", "GAP",
        "Claim has no cited evidence surface.",
    )


def build_layer_c_checks(
    *,
    subject: dict[str, Any],
    source: str = "",
    gate: str = "",
    params: dict[str, Any] | None = None,
    context: dict[str, Any] | None = None,
) -> list[CheckResult]:
    del source, gate, params, context
    return [check_c1_evidence_surface(subject)]
