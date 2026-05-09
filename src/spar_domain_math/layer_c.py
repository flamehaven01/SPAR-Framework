"""Math Layer C -- proof maturity and statement boundary probes."""

from __future__ import annotations

from typing import Any

from spar_framework.result_types import CheckResult


def check_c1_proof_maturity(subject: dict[str, Any]) -> CheckResult:
    """Proof completeness maturity: complete=GENUINE, sketch=APPROXIMATION, absent=GAP."""
    proof_status = subject.get("proof_surface", {}).get("proof_status", "absent")

    if proof_status == "complete":
        return CheckResult("C1", "Proof maturity", "GENUINE", "proof_status=complete.")
    if proof_status == "sketch":
        return CheckResult("C1", "Proof maturity", "APPROXIMATION",
                           "proof_status=sketch. Proof outline present but not complete.")
    return CheckResult("C1", "Proof maturity", "GAP", "proof_status=absent. No proof evidence present.")


def check_c2_statement_boundary(subject: dict[str, Any]) -> CheckResult:
    """Statement boundary clarity: assumptions_explicit governs theorem scope."""
    assumptions_explicit = subject.get("proof_surface", {}).get("assumptions_explicit", False)

    if assumptions_explicit:
        return CheckResult("C2", "Statement boundary clarity", "GENUINE",
                           "assumptions_explicit=true. Theorem boundary conditions are stated.")
    return CheckResult("C2", "Statement boundary clarity", "GAP",
                       "assumptions_explicit=false. Theorem boundary conditions are unstated.")


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
        check_c1_proof_maturity(subject),
        check_c2_statement_boundary(subject),
    ]
