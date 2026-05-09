"""Math Layer A -- proof contract and claim-anchor consistency checks."""

from __future__ import annotations

from typing import Any

from spar_framework.result_types import CheckResult

from .policy_loader import get_layer_a_rules

_RULES = get_layer_a_rules()


def check_a1_proof(subject: dict[str, Any]) -> CheckResult:
    """Proof claim vs proof evidence surface."""
    claim_profile = subject.get("claim_profile", {})
    if not claim_profile.get("proof_claimed", False):
        return CheckResult("A1", "Proof claim anchor", "PASS", "proof_claimed=false; proof surface not required.")

    # conjecture + proof_claimed is a structural contradiction
    theorem_type = subject.get("theorem_type", "theorem")
    if theorem_type == "conjecture":
        return CheckResult(
            "A1", "Proof claim anchor", "ANOMALY",
            "proof_claimed=true but theorem_type=conjecture. A conjecture cannot have a confirmed proof by definition.",
        )

    proof_status = subject.get("proof_surface", {}).get("proof_status", "absent")
    if proof_status == "absent":
        if _RULES.get("proof_requires_evidence", True):
            return CheckResult(
                "A1", "Proof claim anchor", "FAIL",
                "proof_claimed=true but proof_status=absent. Claim has no evidence surface.",
            )
        return CheckResult("A1", "Proof claim anchor", "CANNOT_CHECK",
                           "proof_claimed=true but proof_status=absent; policy permits unchecked claim.")

    return CheckResult(
        "A1", "Proof claim anchor", "CONSISTENT",
        f"proof_claimed=true and proof_status={proof_status}.",
    )


def check_a2_generality(subject: dict[str, Any]) -> CheckResult:
    """Generality claim vs assumption surface."""
    claim_profile = subject.get("claim_profile", {})
    if not claim_profile.get("generality_claimed", False):
        return CheckResult("A2", "Generality claim scope", "PASS", "generality_claimed=false.")

    assumptions_explicit = subject.get("proof_surface", {}).get("assumptions_explicit", False)
    if not assumptions_explicit:
        if _RULES.get("generality_requires_assumptions", True):
            return CheckResult(
                "A2", "Generality claim scope", "GAP",
                "generality_claimed=true but assumptions_explicit=false. Claim scope unbounded.",
            )
        return CheckResult("A2", "Generality claim scope", "PASS",
                           "Policy permits generality claim without explicit assumptions.")

    return CheckResult("A2", "Generality claim scope", "CONSISTENT",
                       "Generality claim bounded by explicit assumptions.")


def check_a3_novelty(subject: dict[str, Any]) -> CheckResult:
    """Novelty claim vs prior art surface."""
    claim_profile = subject.get("claim_profile", {})
    if not claim_profile.get("novelty_claimed", False):
        return CheckResult("A3", "Novelty claim evidence", "PASS", "novelty_claimed=false.")

    prior_art_cited = subject.get("proof_surface", {}).get("prior_art_cited", False)
    if not prior_art_cited:
        status = _RULES.get("novelty_uncited_status", "WARN")
        return CheckResult(
            "A3", "Novelty claim evidence", status,
            "novelty_claimed=true but prior_art_cited=false. Novelty claim lacks prior art context.",
        )

    return CheckResult("A3", "Novelty claim evidence", "CONSISTENT",
                       "Novelty claim accompanied by prior art citations.")


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
        check_a1_proof(subject),
        check_a2_generality(subject),
        check_a3_novelty(subject),
    ]
