"""Physics Layer A runtime admissibility checks."""

from __future__ import annotations

from typing import Any

from spar_framework.result_types import CheckResult
from .ground_truth import PLANCK_MASS_GEV
from .policy_loader import get_layer_a_defaults

_LAYER_A_DEFAULTS = get_layer_a_defaults()
_OMEGA_BOUNDS = _LAYER_A_DEFAULTS["omega_bounds"]
OMEGA_MIN = float(_OMEGA_BOUNDS["min"])
OMEGA_MAX = float(_OMEGA_BOUNDS["max"])


def check_a4(gate: str, gt: dict[str, Any] | None, source: str) -> CheckResult:
    if gt and "gate" in gt:
        expected_gate = gt["gate"]["expected"]
        if expected_gate is not None:
            if gate == expected_gate:
                status, detail = "CONSISTENT", f"Static analytical anchor: gate={gate} matches expected {expected_gate}"
            else:
                status = "ANOMALY"
                detail = (
                    f"Static analytical anchor: gate={gate} DOES NOT match expected={expected_gate}. "
                    f"{gt['gate'].get('detail', '')} PROBABLE GATE LOGIC BUG."
                )
            return CheckResult("A4", "Gate vs expected (ground truth)", status, detail, gt["gate"].get("ref", ""))
        return CheckResult("A4", "Gate vs expected", "CANNOT_CHECK", "No gate expectation for this source")
    return CheckResult("A4", "Gate vs expected", "CANNOT_CHECK", f"Source '{source}' not in ground truth table")


def check_a5(omega: Any) -> CheckResult:
    if omega is not None:
        omega_f = float(omega)
        if OMEGA_MIN <= omega_f <= OMEGA_MAX:
            return CheckResult("A5", "Omega heuristic in [0,1]", "CONSISTENT", f"Static normalization heuristic: Omega={omega_f:.4f} in valid range [{OMEGA_MIN:.1f}, {OMEGA_MAX:.1f}]", "SIDRCE normalization")
        return CheckResult("A5", "Omega heuristic in [0,1]", "ANOMALY", f"Static normalization heuristic: Omega={omega_f:.4f} OUTSIDE [{OMEGA_MIN:.1f}, {OMEGA_MAX:.1f}] -- normalization bug", "SIDRCE normalization")
    return CheckResult("A5", "Omega in [0,1]", "CANNOT_CHECK", "sidrce_omega not in output")


def check_a6(eft_kk: Any) -> CheckResult:
    if eft_kk is not None:
        kk = float(eft_kk)
        if kk < PLANCK_MASS_GEV:
            return CheckResult("A6", "EFT heuristic m_KK < Planck scale", "CONSISTENT", f"Static admissibility threshold: m_KK={kk:.3g} GeV < M_Pl={PLANCK_MASS_GEV:.3g} GeV", "EFT validity")
        return CheckResult("A6", "EFT heuristic m_KK < Planck scale", "ANOMALY", f"Static admissibility threshold: m_KK={kk:.3g} GeV >= M_Pl={PLANCK_MASS_GEV:.3g} GeV -- EFT breakdown", "EFT validity")
    return CheckResult("A6", "EFT m_KK < Planck scale", "CANNOT_CHECK", "eft_m_kk_gev not in output")
