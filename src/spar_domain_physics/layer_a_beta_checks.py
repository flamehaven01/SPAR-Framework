"""Physics Layer A beta-function analytical checks."""

from __future__ import annotations

from typing import Any

from spar_framework.result_types import CheckResult


def _compare_against_expected(
    check_id: str,
    title: str,
    actual: float,
    expected: float,
    tolerance: float,
    reference: str = "",
    consistent_detail: str | None = None,
    anomaly_detail: str | None = None,
) -> CheckResult:
    if abs(actual - expected) <= tolerance:
        detail = consistent_detail or f"{title}={actual:.6g} matches expected {expected} (tol={tolerance})"
        return CheckResult(check_id, title, "CONSISTENT", detail, reference)
    detail = anomaly_detail or f"{title}={actual:.6g} deviates from expected {expected} by {abs(actual - expected):.4g}"
    return CheckResult(check_id, title, "ANOMALY", detail, reference)


def _check_ground_truth_beta(
    check_id: str,
    title: str,
    beta_value: Any,
    spec: dict[str, Any] | None,
    default_tolerance: float,
) -> CheckResult | None:
    if spec is None or beta_value is None:
        return None
    actual = float(beta_value)
    expected = spec["expected"]
    tolerance = spec.get("tolerance", default_tolerance)
    reference = spec.get("ref", "")
    return _compare_against_expected(
        check_id=check_id,
        title=title,
        actual=actual,
        expected=expected,
        tolerance=tolerance,
        reference=reference,
    )


def _check_linear_dilaton_beta_phi(
    beta_phi: Any,
    phys: dict[str, Any],
    spec: dict[str, Any],
    beta_tol_phi: float,
) -> CheckResult:
    dil_v = phys.get("dilaton_V", phys.get("dilaton_gradient", phys.get("V")))
    reference = spec.get("ref", "")
    if dil_v is None:
        return CheckResult(
            "A3",
            "beta_Phi vs 4*V^2",
            "CANNOT_CHECK",
            "dilaton_V not in physics output; cannot verify 4*V^2 formula",
            reference,
        )
    expected_val = 4.0 * float(dil_v) ** 2
    actual = float(beta_phi)
    tolerance = max(spec.get("tolerance", beta_tol_phi), 1e-2 * abs(expected_val))
    return _compare_against_expected(
        check_id="A3",
        title="beta_Phi vs 4*V^2 (linear dilaton)",
        actual=actual,
        expected=expected_val,
        tolerance=tolerance,
        reference=reference,
        consistent_detail=f"beta_Phi={actual:.6g} matches 4*V^2={expected_val:.6g}",
        anomaly_detail=(
            f"beta_Phi={actual:.6g} != 4*V^2={expected_val:.6g} "
            f"(V={float(dil_v):.4g}). Possible formula error."
        ),
    )


def check_a1(beta_g: Any, gt: dict[str, Any] | None, beta_tol_g: float) -> CheckResult:
    spec = gt.get("beta_G_norm") if gt else None
    result = _check_ground_truth_beta("A1", "beta_G vs analytical", beta_g, spec, beta_tol_g)
    if result is not None:
        return result
    detail = "No ground truth for this source" if not gt else "beta_G_norm not in physics output"
    return CheckResult("A1", "beta_G vs analytical", "CANNOT_CHECK", detail)


def check_a2(
    beta_b: Any,
    phys: dict[str, Any],
    gt: dict[str, Any] | None,
    source: str,
    beta_tol_b: float,
) -> CheckResult:
    spec = gt.get("beta_B_norm") if gt else None
    if spec is not None and beta_b is not None:
        actual = float(beta_b)
        expected = spec["expected"]
        tolerance = spec.get("tolerance", beta_tol_b)
        return _compare_against_expected(
            check_id="A2",
            title="beta_B vs H-flux/dilaton coupling",
            actual=actual,
            expected=expected,
            tolerance=tolerance,
            reference=spec.get("ref", ""),
            consistent_detail=f"beta_B_norm={actual:.6g} matches expected {expected}",
            anomaly_detail=f"beta_B_norm={actual:.6g} deviates from expected {expected}",
        )
    if beta_b is not None:
        h_flux_present = bool(phys.get("h_flux_norm", phys.get("h_flux", 0.0)))
        if not h_flux_present and abs(float(beta_b)) < beta_tol_b:
            return CheckResult(
                "A2",
                "beta_B vs H-flux/dilaton coupling",
                "CONSISTENT",
                f"beta_B_norm={float(beta_b):.6g}~0 consistent with no H-flux",
            )
        return CheckResult(
            "A2",
            "beta_B vs H-flux/dilaton coupling",
            "CANNOT_CHECK",
            f"beta_B_norm={float(beta_b):.6g}; no specific expected value for source '{source}'",
        )
    return CheckResult("A2", "beta_B vs H-flux/dilaton coupling", "CANNOT_CHECK", "beta_B not in output")


def check_a3(
    beta_phi: Any,
    phys: dict[str, Any],
    gt: dict[str, Any] | None,
    beta_tol_phi: float,
) -> CheckResult:
    spec = gt.get("beta_Phi_norm") if gt else None
    if spec is not None and beta_phi is not None:
        if spec.get("formula") == "4*V^2":
            return _check_linear_dilaton_beta_phi(beta_phi, phys, spec, beta_tol_phi)
        if spec.get("expected") is not None:
            actual = float(beta_phi)
            expected = spec["expected"]
            tolerance = spec.get("tolerance", beta_tol_phi)
            return _compare_against_expected(
                check_id="A3",
                title="beta_Phi vs analytical",
                actual=actual,
                expected=expected,
                tolerance=tolerance,
                reference=spec.get("ref", ""),
            )
        return CheckResult("A3", "beta_Phi vs analytical", "CANNOT_CHECK", "No static expected value for beta_Phi at this source")
    return CheckResult("A3", "beta_Phi vs analytical", "CANNOT_CHECK", "No ground truth entry or beta_Phi missing")

