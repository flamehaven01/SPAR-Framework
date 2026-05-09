"""Math Layer B -- claim language strength vs subject claim profile."""

from __future__ import annotations

from typing import Any

from spar_framework.result_types import CheckResult

from .policy_loader import get_layer_b_phrases

_PHRASES = get_layer_b_phrases()
_PROOF_PHRASES: list[str] = _PHRASES["proof_phrases"]
_GEN_PHRASES: list[str] = _PHRASES["generality_phrases"]
_NOV_PHRASES: list[str] = _PHRASES["novelty_phrases"]
_FV_PHRASES: list[str] = _PHRASES.get("formal_verification_phrases", [])


def _text_contains_any(text: str, phrases: list[str]) -> str | None:
    lowered = text.lower()
    for phrase in phrases:
        if phrase in lowered:
            return phrase
    return None


def check_b1_proof_language(subject: dict[str, Any], report_text: str) -> CheckResult:
    """Proof language in report_text vs claim_profile.proof_claimed."""
    hit = _text_contains_any(report_text, _PROOF_PHRASES)
    proof_in_profile = subject.get("claim_profile", {}).get("proof_claimed", False)

    if hit and not proof_in_profile:
        return CheckResult(
            "B1", "Proof language vs profile", "WARN",
            f"Report text contains proof phrase '{hit}' but claim_profile.proof_claimed=false. "
            "Text claim exceeds structured profile.",
        )
    if hit and proof_in_profile:
        return CheckResult("B1", "Proof language vs profile", "PASS",
                           f"Proof phrase '{hit}' matches claim_profile.proof_claimed=true.")
    return CheckResult("B1", "Proof language vs profile", "PASS", "No proof claim language detected.")


def check_b2_generality_language(subject: dict[str, Any], report_text: str) -> CheckResult:
    """Generality language in report_text vs claim_profile.generality_claimed."""
    hit = _text_contains_any(report_text, _GEN_PHRASES)
    gen_in_profile = subject.get("claim_profile", {}).get("generality_claimed", False)

    if hit and not gen_in_profile:
        return CheckResult(
            "B2", "Generality language vs profile", "WARN",
            f"Report text contains generality phrase '{hit}' but claim_profile.generality_claimed=false.",
        )
    return CheckResult("B2", "Generality language vs profile", "PASS",
                       "Generality language consistent with claim profile.")


def check_b3_novelty_language(subject: dict[str, Any], report_text: str) -> CheckResult:
    """Novelty language in report_text vs claim_profile.novelty_claimed."""
    hit = _text_contains_any(report_text, _NOV_PHRASES)
    nov_in_profile = subject.get("claim_profile", {}).get("novelty_claimed", False)

    if hit and not nov_in_profile:
        return CheckResult(
            "B3", "Novelty language vs profile", "WARN",
            f"Report text contains novelty phrase '{hit}' but claim_profile.novelty_claimed=false.",
        )
    return CheckResult("B3", "Novelty language vs profile", "PASS",
                       "Novelty language consistent with claim profile.")


def check_b4_formal_verification_claims(report_text: str) -> CheckResult:
    """Formal verification language detection — CANNOT_CHECK only when detected."""
    hit = _text_contains_any(report_text, _FV_PHRASES)
    if hit:
        return CheckResult(
            "B4", "Formal verification claim coverage", "CANNOT_CHECK",
            f"Formal verification phrase '{hit}' detected. Machine-checked proofs (Coq, Lean, Isabelle) "
            "are not reviewed in v0.4.x.",
            basis="subject_derived",
        )
    return CheckResult("B4", "Formal verification claim coverage", "PASS",
                       "No formal verification language detected.")


def build_layer_b_checks(
    *,
    subject: dict[str, Any],
    source: str = "",
    gate: str = "",
    report_text: str = "",
    context: dict[str, Any] | None = None,
) -> list[CheckResult]:
    del source, gate, context
    return [
        check_b1_proof_language(subject, report_text),
        check_b2_generality_language(subject, report_text),
        check_b3_novelty_language(subject, report_text),
        check_b4_formal_verification_claims(report_text),
    ]
