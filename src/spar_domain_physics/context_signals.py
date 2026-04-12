"""Restricted contextual signals for physics adapter review."""

from __future__ import annotations

from typing import Any

from spar_framework.result_types import CheckResult


def extract_leda_summary(context: dict[str, Any] | None) -> dict[str, Any] | None:
    if not context:
        return None
    leda = context.get("leda_injection")
    if not isinstance(leda, dict):
        return None
    security = leda.get("security", {})
    if security.get("ingestible_by_spar") is False:
        return None
    if security.get("classification") == "public":
        return None
    return leda


def check_b4_leda_claim_surface(leda: dict[str, Any] | None) -> CheckResult:
    if not leda:
        return CheckResult(
            "B4",
            "LEDA claim-risk surface",
            "CANNOT_CHECK",
            "No LEDA injection context provided",
        )

    risk_count = len(leda.get("claim_risk", []))
    maturity = leda.get("maturity", {}).get("suggested_current")
    preferred_layers = leda.get("spar_review_hints", {}).get("preferred_layers", [])

    if risk_count == 0:
        return CheckResult(
            "B4",
            "LEDA claim-risk surface",
            "PASS",
            "Restricted LEDA context reports no explicit claim-risk candidates.",
        )

    return CheckResult(
        "B4",
        "LEDA claim-risk surface",
        "WARN",
        f"Restricted LEDA context reports {risk_count} claim-risk candidates; suggested_maturity={maturity}; preferred_layers={preferred_layers}.",
    )


def check_c9_leda_maturity_alignment(leda: dict[str, Any] | None) -> CheckResult:
    if not leda:
        return CheckResult(
            "C9",
            "LEDA maturity alignment",
            "CANNOT_CHECK",
            "No LEDA injection context provided",
        )

    maturity = leda.get("maturity", {}).get("suggested_current")
    confidence = leda.get("maturity", {}).get("confidence")
    classification = leda.get("security", {}).get("classification")

    if maturity in {None, ""}:
        return CheckResult(
            "C9",
            "LEDA maturity alignment",
            "CANNOT_CHECK",
            "LEDA injection does not contain a maturity suggestion.",
        )

    if maturity == "partial":
        return CheckResult(
            "C9",
            "LEDA maturity alignment",
            "APPROXIMATION",
            f"Restricted LEDA context suggests partial maturity (confidence={confidence}, profile={classification}).",
        )
    if maturity in {"heuristic", "environment_conditional"}:
        return CheckResult(
            "C9",
            "LEDA maturity alignment",
            "GAP",
            f"Restricted LEDA context suggests {maturity} maturity (confidence={confidence}, profile={classification}).",
        )
    return CheckResult(
        "C9",
        "LEDA maturity alignment",
        "GENUINE",
        f"Restricted LEDA context suggests {maturity} maturity (confidence={confidence}, profile={classification}).",
    )
