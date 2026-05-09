"""Framework-declared physics maturity and limitation surfaces C4-C8."""

from __future__ import annotations

from typing import Any

from spar_framework.result_types import CheckResult

from .architecture_gaps import PHYSICS_ARCHITECTURE_GAPS
from .registry_seed import format_gap_state


def build_framework_declared_checks(
    *,
    subject: dict[str, Any],
    source: str = "",
    gate: str = "",
    params: dict[str, Any] | None = None,
    context: dict[str, Any] | None = None,
) -> list[CheckResult]:
    del source, gate, params, context
    blind_spots = [
        "beta_B Term1 (partial2_B path) -- no independent symbolic crosscheck",
        "GS Pontryagin density -- no full external curvature verification",
        "EFT KK mass formula -- no analytical crosscheck",
        "chi-squared tolerance magnitudes -- calibrated, not first-principles",
    ]

    omega = subject.get("sidrce_omega")
    omega_detail = (
        f"Omega={float(omega):.4f}. "
        if omega is not None
        else "sidrce_omega not surfaced in subject payload. "
    )

    return [
        CheckResult(
            "C4",
            "SIDRCE Omega derivation policy",
            "DECLARED_OPEN",
            f"{omega_detail}{PHYSICS_ARCHITECTURE_GAPS['C4']} [{format_gap_state('C4')}]",
            basis="framework_declared",
            scope="adapter_limitation",
        ),
        CheckResult(
            "C5",
            "Independent verification coverage policy",
            "DECLARED_PARTIAL",
            f"{PHYSICS_ARCHITECTURE_GAPS['C5']} Blind spots: {blind_spots} [{format_gap_state('C5')}]",
            basis="framework_declared",
            scope="adapter_limitation",
        ),
        CheckResult(
            "C6",
            "QGB alpha heuristic policy",
            "DECLARED_HEURISTIC",
            f"{PHYSICS_ARCHITECTURE_GAPS['C6']} [{format_gap_state('C6')}]",
            basis="framework_declared",
            scope="adapter_limitation",
        ),
        CheckResult(
            "C7",
            "T-duality phi_gradient policy",
            "DECLARED_CLOSED",
            f"{PHYSICS_ARCHITECTURE_GAPS['C7']} [{format_gap_state('C7')}]",
            basis="framework_declared",
            scope="adapter_limitation",
        ),
        CheckResult(
            "C8",
            "RG flow metric evolution policy",
            "DECLARED_APPROXIMATION",
            f"{PHYSICS_ARCHITECTURE_GAPS['C8']} [{format_gap_state('C8')}]",
            basis="framework_declared",
            scope="adapter_limitation",
        ),
    ]
