"""Restricted contextual signals for physics adapter review."""

from __future__ import annotations

from typing import Any

from spar_framework.result_types import CheckResult


def extract_mica_summary(context: dict[str, Any] | None) -> dict[str, Any] | None:
    if not context:
        return None
    mica = context.get("memory_context")
    if not isinstance(mica, dict):
        return None
    return mica


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


def check_b5_mica_runtime_state(mica: dict[str, Any] | None) -> CheckResult:
    if not mica:
        return CheckResult(
            "B5",
            "MICA runtime state",
            "CANNOT_CHECK",
            "No MICA context provided",
        )

    runtime = mica.get("_mica_runtime", {})
    invariants = mica.get("invariants", {})
    state = runtime.get("state")
    critical = invariants.get("critical", 0)
    archive_id = mica.get("archive_id")

    if state == "INVOCATION_MODE":
        return CheckResult(
            "B5",
            "MICA runtime state",
            "PASS",
            f"MICA invocation mode is active with {critical} critical invariants (archive_id={archive_id}).",
        )
    if state == "LEGACY_MODE":
        return CheckResult(
            "B5",
            "MICA runtime state",
            "WARN",
            f"MICA is running in legacy archive mode; invariant context is present but runtime enforcement may be weaker (archive_id={archive_id}).",
        )
    return CheckResult(
        "B5",
        "MICA runtime state",
        "CANNOT_CHECK",
        "MICA runtime is inactive or unresolved for this review.",
    )


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


def check_c10_mica_invariant_continuity(mica: dict[str, Any] | None) -> CheckResult:
    if not mica:
        return CheckResult(
            "C10",
            "MICA invariant continuity",
            "CANNOT_CHECK",
            "No MICA context provided",
        )

    runtime = mica.get("_mica_runtime", {})
    invariants = mica.get("invariants", {})
    state = runtime.get("state")
    critical = invariants.get("critical", 0)
    high = invariants.get("high", 0)
    pct_status = mica.get("pct_status")

    if state == "INVOCATION_MODE" and critical > 0:
        return CheckResult(
            "C10",
            "MICA invariant continuity",
            "GENUINE",
            f"MICA invocation mode carries {critical} critical and {high} high invariants into review (pct_status={pct_status}).",
        )
    if state == "LEGACY_MODE":
        return CheckResult(
            "C10",
            "MICA invariant continuity",
            "APPROXIMATION",
            f"MICA context is available only through legacy archive mode (pct_status={pct_status}).",
        )
    if state == "INVOCATION_MODE":
        return CheckResult(
            "C10",
            "MICA invariant continuity",
            "CANNOT_DETERMINE",
            "MICA invocation mode is active, but no critical invariants were surfaced.",
        )
    return CheckResult(
        "C10",
        "MICA invariant continuity",
        "CANNOT_CHECK",
        "MICA runtime is inactive or unresolved for this review.",
    )
