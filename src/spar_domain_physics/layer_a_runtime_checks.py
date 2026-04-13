"""Physics Layer A runtime admissibility checks."""

from __future__ import annotations

from typing import Any

from spar_framework.result_types import CheckResult
from .ground_truth import PLANCK_MASS_GEV


def check_a4(gate: str, gt: dict[str, Any] | None, source: str) -> CheckResult:
    if gt and "gate" in gt:
        expected_gate = gt["gate"]["expected"]
        if expected_gate is not None:
            if gate == expected_gate:
                status, detail = "CONSISTENT", f"gate={gate} matches expected {expected_gate}"
            else:
                status = "ANOMALY"
                detail = (
                    f"gate={gate} DOES NOT match expected={expected_gate}. "
                    f"{gt['gate'].get('detail', '')} PROBABLE GATE LOGIC BUG."
                )
            return CheckResult("A4", "Gate vs expected (ground truth)", status, detail, gt["gate"].get("ref", ""))
        return CheckResult("A4", "Gate vs expected", "CANNOT_CHECK", "No gate expectation for this source")
    return CheckResult("A4", "Gate vs expected", "CANNOT_CHECK", f"Source '{source}' not in ground truth table")


def check_a5(omega: Any) -> CheckResult:
    if omega is not None:
        omega_f = float(omega)
        if 0.0 <= omega_f <= 1.0:
            return CheckResult("A5", "Omega in [0,1]", "CONSISTENT", f"Omega={omega_f:.4f} in valid range", "SIDRCE normalization")
        return CheckResult("A5", "Omega in [0,1]", "ANOMALY", f"Omega={omega_f:.4f} OUTSIDE [0,1] -- normalization bug", "SIDRCE normalization")
    return CheckResult("A5", "Omega in [0,1]", "CANNOT_CHECK", "sidrce_omega not in output")


def check_a6(eft_kk: Any) -> CheckResult:
    if eft_kk is not None:
        kk = float(eft_kk)
        if kk < PLANCK_MASS_GEV:
            return CheckResult("A6", "EFT m_KK < Planck scale", "CONSISTENT", f"m_KK={kk:.3g} GeV < M_Pl={PLANCK_MASS_GEV:.3g} GeV", "EFT validity")
        return CheckResult("A6", "EFT m_KK < Planck scale", "ANOMALY", f"m_KK={kk:.3g} GeV >= M_Pl={PLANCK_MASS_GEV:.3g} GeV -- EFT breakdown", "EFT validity")
    return CheckResult("A6", "EFT m_KK < Planck scale", "CANNOT_CHECK", "eft_m_kk_gev not in output")
