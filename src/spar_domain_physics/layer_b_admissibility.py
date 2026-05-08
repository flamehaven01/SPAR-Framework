"""Physics Layer B admissibility and scope checks."""

from __future__ import annotations

from typing import Any

from spar_framework.result_types import CheckResult

from .ground_truth import PLANCK_MASS_GEV
from .policy_loader import get_layer_b_thresholds

_LAYER_B_THRESHOLDS = get_layer_b_thresholds()
RICCI_PASS_BELOW = float(_LAYER_B_THRESHOLDS["ricci_norm_pass_below"])
RICCI_WARN_BELOW = float(_LAYER_B_THRESHOLDS["ricci_norm_warn_below"])


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
            "Swampland heuristic: EFT KK mass below Planck",
            "PASS",
            f"Static heuristic threshold: m_KK={kk:.3g} GeV satisfies EFT < M_Pl. Full WGC check requires coupling g_4d not available.",
            "Swampland/WGC",
        )
    return CheckResult(
        "B1",
        "Swampland heuristic: EFT KK mass below Planck",
        "FAIL",
        f"Static heuristic threshold: m_KK={kk:.3g} GeV >= M_Pl -- violates this adapter's EFT admissibility rule.",
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
    if rn < RICCI_PASS_BELOW:
        status = "PASS"
        detail = f"Static heuristic threshold: ricci_norm={rn:.4g} < {RICCI_PASS_BELOW:.4g} so alpha' corrections are treated as negligible"
    elif rn < RICCI_WARN_BELOW:
        status = "WARN"
        detail = f"Static heuristic threshold: ricci_norm={rn:.4g} < {RICCI_WARN_BELOW:.4g} so alpha' corrections are treated as small but non-negligible"
    else:
        status = "FAIL"
        detail = f"Static heuristic threshold: ricci_norm={rn:.4g} >= {RICCI_WARN_BELOW:.4g} so alpha' corrections are treated as significant. One-loop validity is questionable."

    return CheckResult(
        "B2",
        "alpha' corrections estimate (alpha'*R<<1)",
        status,
        detail,
        "String perturbation theory",
    )
