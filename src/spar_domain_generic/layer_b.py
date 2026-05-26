"""Generic Layer B -- report-text language vs claim profile."""

from __future__ import annotations

from typing import Any

from spar_framework.result_types import CheckResult

# Substring matchers, lowercase. Intentionally small and conservative.
_STRONG_CLAIM_PHRASES = (
    "we prove",
    "we show",
    "we establish",
    "this proves",
    "demonstrates that",
    "guarantees that",
)
_UNBOUNDED_PHRASES = (
    "in general",
    "for all",
    "always",
    "in every case",
    "universally",
)


def _hit(text: str, phrases: tuple[str, ...]) -> str | None:
    if not text:
        return None
    lowered = text.lower()
    for phrase in phrases:
        if phrase in lowered:
            return phrase
    return None


def check_b1_claim_language(subject: dict[str, Any], report_text: str) -> CheckResult:
    profile = subject.get("claim_profile") if isinstance(subject.get("claim_profile"), dict) else {}
    hit = _hit(report_text, _STRONG_CLAIM_PHRASES)
    claim_made = profile.get("claim_made", False)
    if hit and not claim_made:
        return CheckResult(
            "B1", "Strong-claim language vs profile", "WARN",
            f"Report text contains strong-claim phrase '{hit}' but claim_profile.claim_made=false.",
        )
    return CheckResult(
        "B1", "Strong-claim language vs profile", "PASS",
        "Claim language consistent with claim profile.",
    )


def check_b2_unbounded_language(subject: dict[str, Any], report_text: str) -> CheckResult:
    profile = subject.get("claim_profile") if isinstance(subject.get("claim_profile"), dict) else {}
    hit = _hit(report_text, _UNBOUNDED_PHRASES)
    scope_bounded = profile.get("scope_bounded", True)
    if hit and not scope_bounded:
        return CheckResult(
            "B2", "Unbounded language vs scope", "WARN",
            f"Report text contains unbounded phrase '{hit}' but claim scope is not bounded.",
        )
    return CheckResult(
        "B2", "Unbounded language vs scope", "PASS",
        "Report scope language consistent with claim profile.",
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
        check_b1_claim_language(subject, report_text),
        check_b2_unbounded_language(subject, report_text),
    ]
