"""ML Layer A -- benchmark contract and claim-anchor consistency checks."""

from __future__ import annotations

from typing import Any

from spar_framework.result_types import CheckResult

from .policy_loader import get_layer_a_rules

_RULES = get_layer_a_rules()


def _beats_baseline(metric: float, baseline: float, direction: str) -> bool:
    if direction == "lower_is_better":
        return metric < baseline
    return metric > baseline


def check_a1_sota(subject: dict[str, Any]) -> CheckResult:
    """SOTA claim vs baseline anchor."""
    claim_profile = subject.get("claim_profile", {})
    if not claim_profile.get("sota_claimed", False):
        return CheckResult("A1", "SOTA claim anchor", "PASS", "sota_claimed=false; baseline check not required.")

    baseline_value = subject.get("baseline_value")
    if baseline_value is None:
        if _RULES.get("sota_requires_baseline", True):
            return CheckResult(
                "A1", "SOTA claim anchor", "FAIL",
                "sota_claimed=true but baseline_value absent. Claim has no measurable anchor.",
            )
        return CheckResult("A1", "SOTA claim anchor", "CANNOT_CHECK",
                           "sota_claimed=true but baseline_value absent; policy permits unchecked claim.")

    metric_value = subject.get("metric_value")
    if metric_value is None:
        return CheckResult("A1", "SOTA claim anchor", "CANNOT_CHECK", "metric_value absent; cannot evaluate SOTA claim.")

    direction = subject.get("metric_direction", "higher_is_better")
    if not _beats_baseline(float(metric_value), float(baseline_value), direction):
        return CheckResult(
            "A1", "SOTA claim anchor", "ANOMALY",
            f"sota_claimed=true but metric_value={metric_value} does not beat "
            f"baseline_value={baseline_value} ({direction}).",
        )

    return CheckResult(
        "A1", "SOTA claim anchor", "CONSISTENT",
        f"metric_value={metric_value} beats baseline_value={baseline_value} ({direction}).",
    )


def check_a2_generalization(subject: dict[str, Any]) -> CheckResult:
    """Generalization claim vs OOD / scope evidence."""
    claim_profile = subject.get("claim_profile", {})
    if not claim_profile.get("generalization_claimed", False):
        return CheckResult("A2", "Generalization claim scope", "PASS", "generalization_claimed=false.")

    eval_scope = subject.get("evaluation_scope", {})
    ood = eval_scope.get("ood_evaluated", False)
    restricted = eval_scope.get("claim_scope_restricted", False)

    if not ood and not restricted:
        if _RULES.get("generalization_requires_ood_or_scope_restriction", True):
            return CheckResult(
                "A2", "Generalization claim scope", "GAP",
                "generalization_claimed=true but ood_evaluated=false and claim_scope_restricted=false. "
                "Claim exceeds evaluation surface.",
            )
        return CheckResult("A2", "Generalization claim scope", "PASS",
                           "Policy permits generalization claim without OOD or scope restriction.")
    return CheckResult(
        "A2", "Generalization claim scope", "CONSISTENT",
        f"Generalization claim bounded: ood_evaluated={ood}, claim_scope_restricted={restricted}.",
    )


def check_a3_robustness(subject: dict[str, Any]) -> CheckResult:
    """Robustness claim vs evaluation evidence."""
    claim_profile = subject.get("claim_profile", {})
    if not claim_profile.get("robustness_claimed", False):
        return CheckResult("A3", "Robustness claim evidence", "PASS", "robustness_claimed=false.")

    eval_scope = subject.get("evaluation_scope", {})
    if not eval_scope.get("robustness_evaluated", False):
        if _RULES.get("robustness_requires_eval", True):
            return CheckResult(
                "A3", "Robustness claim evidence", "GAP",
                "robustness_claimed=true but robustness_evaluated=false. No supporting evidence surface.",
            )
        return CheckResult("A3", "Robustness claim evidence", "PASS",
                           "Policy permits robustness claim without evaluation evidence.")
    return CheckResult("A3", "Robustness claim evidence", "CONSISTENT", "Robustness claim backed by evaluation.")


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
        check_a1_sota(subject),
        check_a2_generalization(subject),
        check_a3_robustness(subject),
    ]
