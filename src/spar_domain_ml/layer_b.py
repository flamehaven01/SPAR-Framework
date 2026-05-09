"""ML Layer B -- claim language strength vs subject claim profile."""

from __future__ import annotations

from typing import Any

from spar_framework.result_types import CheckResult

from .policy_loader import get_layer_b_phrases

_PHRASES = get_layer_b_phrases()
_SOTA_PHRASES: list[str] = _PHRASES["sota_phrases"]
_GEN_PHRASES: list[str] = _PHRASES["generalization_phrases"]
_ROB_PHRASES: list[str] = _PHRASES["robustness_phrases"]


def _text_contains_any(text: str, phrases: list[str]) -> str | None:
    lowered = text.lower()
    for phrase in phrases:
        if phrase in lowered:
            return phrase
    return None


def check_b1_sota_language(subject: dict[str, Any], report_text: str) -> CheckResult:
    """SOTA language in report_text vs claim_profile.sota_claimed."""
    hit = _text_contains_any(report_text, _SOTA_PHRASES)
    sota_in_profile = subject.get("claim_profile", {}).get("sota_claimed", False)

    if hit and not sota_in_profile:
        return CheckResult(
            "B1", "SOTA language vs profile", "WARN",
            f"Report text contains SOTA claim phrase '{hit}' but claim_profile.sota_claimed=false. "
            "Text claim exceeds structured profile.",
        )
    if hit and sota_in_profile:
        return CheckResult("B1", "SOTA language vs profile", "PASS",
                           f"SOTA phrase '{hit}' matches claim_profile.sota_claimed=true.")
    return CheckResult("B1", "SOTA language vs profile", "PASS", "No SOTA claim language detected.")


def check_b2_generalization_language(subject: dict[str, Any], report_text: str) -> CheckResult:
    """Generalization language in report_text vs claim_profile.generalization_claimed."""
    hit = _text_contains_any(report_text, _GEN_PHRASES)
    gen_in_profile = subject.get("claim_profile", {}).get("generalization_claimed", False)

    if hit and not gen_in_profile:
        return CheckResult(
            "B2", "Generalization language vs profile", "WARN",
            f"Report text contains generalization phrase '{hit}' but claim_profile.generalization_claimed=false.",
        )
    return CheckResult("B2", "Generalization language vs profile", "PASS",
                       "Generalization language consistent with claim profile.")


def check_b3_extended_claims(report_text: str) -> CheckResult:
    """Extended claim classes (fairness, calibration, etc.) are not reviewed."""
    return CheckResult(
        "B3", "Extended claim class coverage", "CANNOT_CHECK",
        "Extended claim classes (fairness, calibration, efficiency, safety) are not reviewed in v0.3.0.",
        basis="subject_derived",
    )


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
        check_b1_sota_language(subject, report_text),
        check_b2_generalization_language(subject, report_text),
        check_b3_extended_claims(report_text),
    ]
