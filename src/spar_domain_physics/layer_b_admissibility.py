"""Physics Layer B admissibility and scope checks."""

from __future__ import annotations

from typing import Any

from spar_framework.result_types import CheckResult

from .ground_truth import PLANCK_MASS_GEV


def check_b1(eft_kk: Any) -> CheckResult:
    if eft_kk is None:
        return CheckResult(
            "B1",
            "Swampland: EFT KK mass",
            "CANNOT_CHECK",
            "eft_m_kk_gev not available; Swampland check skipped",
            "Swampland/WGC",
        )

    kk = float(eft_kk)
    if kk < PLANCK_MASS_GEV:
        return CheckResult(
            "B1",
            "Swampland: EFT KK mass below Planck",
            "PASS",
            f"m_KK={kk:.3g} GeV satisfies basic EFT < M_Pl. Full WGC check requires coupling g_4d not available.",
            "Swampland/WGC",
        )
    return CheckResult(
        "B1",
        "Swampland: EFT KK mass below Planck",
        "FAIL",
        f"m_KK={kk:.3g} GeV >= M_Pl -- violates Swampland EFT consistency.",
        "Swampland/WGC",
    )


def check_b2(ricci_norm: Any) -> CheckResult:
    if ricci_norm is None:
        return CheckResult(
            "B2",
            "alpha' corrections",
            "CANNOT_CHECK",
            "ricci_norm not in output",
            "String perturbation theory",
        )

    rn = float(ricci_norm)
    if rn < 0.01:
        status = "PASS"
        detail = f"ricci_norm={rn:.4g} << 0.1: alpha' corrections negligible"
    elif rn < 0.1:
        status = "WARN"
        detail = f"ricci_norm={rn:.4g} < 0.1: alpha' corrections small but non-negligible"
    else:
        status = "FAIL"
        detail = f"ricci_norm={rn:.4g} >= 0.1: alpha' corrections likely significant. One-loop validity questionable."

    return CheckResult(
        "B2",
        "alpha' corrections estimate (alpha'*R<<1)",
        status,
        detail,
        "String perturbation theory",
    )
