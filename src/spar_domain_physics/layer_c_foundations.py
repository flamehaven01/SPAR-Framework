"""Physics Layer C foundation/existence probes C1-C4."""

from __future__ import annotations

from typing import Any

from spar_framework.result_types import CheckResult

from .architecture_gaps import PHYSICS_ARCHITECTURE_GAPS
from .layer_c_foundation_helpers import evaluate_beta_b_genuineness, evaluate_brst_genuineness
from .registry_seed import format_gap_state


def build_layer_c_foundations(*, subject: dict[str, Any], source: str) -> list[CheckResult]:
    results: list[CheckResult] = []

    existence, detail = evaluate_beta_b_genuineness(subject)
    results.append(
            CheckResult(
                "C1",
                "beta^B genuineness",
                existence,
                detail + f" [{PHYSICS_ARCHITECTURE_GAPS['C1'][:60]}...] [{format_gap_state('C1')}]",
            )
        )

    existence, detail = evaluate_brst_genuineness(subject, source)
    results.append(
        CheckResult(
            "C2",
            "BRST genuineness",
            existence,
            f"{detail} [{format_gap_state('C2')}]",
        )
    )

    partial_g = subject.get("partial_G")
    f2 = subject.get("F2")
    c3_status = "GENUINE" if partial_g is not None and f2 is not None else "APPROXIMATION"
    results.append(
        CheckResult(
            "C3",
            "GS anomaly completeness",
            c3_status,
            "GS check uses Pontryagin 4-form (adapter extraction path). "
            f"{PHYSICS_ARCHITECTURE_GAPS['C3']} [{format_gap_state('C3')}]",
        )
    )

    omega = subject.get("sidrce_omega")
    if omega is not None:
        results.append(
            CheckResult(
                "C4",
                "SIDRCE Omega derivation",
                "GAP",
                f"Omega={float(omega):.4f}. {PHYSICS_ARCHITECTURE_GAPS['C4']} [{format_gap_state('C4')}]",
            )
        )
    else:
        results.append(
            CheckResult(
                "C4",
                "SIDRCE Omega derivation",
                "CANNOT_DETERMINE",
                "sidrce_omega not in output",
            )
        )

    return results
