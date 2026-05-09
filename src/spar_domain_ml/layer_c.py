"""ML Layer C -- evidence maturity and reproducibility surface probes."""

from __future__ import annotations

from typing import Any

from spar_framework.result_types import CheckResult

from .policy_loader import get_layer_c_thresholds

_THRESHOLDS = get_layer_c_thresholds()
_REPRO_FIELDS: list[str] = _THRESHOLDS["reproducibility_fields"]
_GENUINE_THRESHOLD: int = int(_THRESHOLDS["genuine_threshold"])
_APPROX_THRESHOLD: int = int(_THRESHOLDS["approximation_threshold"])


def check_c1_reproducibility(subject: dict[str, Any]) -> CheckResult:
    """Reproducibility surface maturity: 3/3=GENUINE, 2/3=APPROXIMATION, <2=GAP."""
    repro = subject.get("reproducibility", {})
    present = [f for f in _REPRO_FIELDS if repro.get(f, False)]
    missing = [f for f in _REPRO_FIELDS if not repro.get(f, False)]
    count = len(present)

    if count >= _GENUINE_THRESHOLD:
        return CheckResult("C1", "Reproducibility maturity", "GENUINE",
                           f"{count}/{len(_REPRO_FIELDS)} reproducibility fields present.")
    if count >= _APPROX_THRESHOLD:
        return CheckResult("C1", "Reproducibility maturity", "APPROXIMATION",
                           f"{count}/{len(_REPRO_FIELDS)} reproducibility fields present. Missing: {missing}.")
    return CheckResult("C1", "Reproducibility maturity", "GAP",
                       f"{count}/{len(_REPRO_FIELDS)} reproducibility fields present. Missing: {missing}.")


def check_c2_evaluation_surface(subject: dict[str, Any]) -> CheckResult:
    """Evaluation surface completeness vs claimed scope."""
    claim_profile = subject.get("claim_profile", {})
    eval_scope = subject.get("evaluation_scope", {})

    gen_claimed = claim_profile.get("generalization_claimed", False)
    rob_claimed = claim_profile.get("robustness_claimed", False)

    if gen_claimed and not eval_scope.get("ood_evaluated", False):
        return CheckResult(
            "C2", "Evaluation surface completeness", "GAP",
            "generalization_claimed=true but no OOD evaluation in scope.",
        )
    if rob_claimed and not eval_scope.get("robustness_evaluated", False):
        return CheckResult(
            "C2", "Evaluation surface completeness", "GAP",
            "robustness_claimed=true but no robustness evaluation in scope.",
        )
    return CheckResult("C2", "Evaluation surface completeness", "GENUINE",
                       "Evaluation surface matches claimed scope.")


def build_layer_c_checks(
    *,
    subject: dict[str, Any],
    source: str = "",
    gate: str = "",
    params: dict[str, Any] | None = None,
    context: dict[str, Any] | None = None,
) -> list[CheckResult]:
    del source, gate, params, context
    return [
        check_c1_reproducibility(subject),
        check_c2_evaluation_surface(subject),
    ]
