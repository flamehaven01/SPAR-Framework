"""Physics Layer A builder."""

from __future__ import annotations

from typing import Any

from .ground_truth import get_ground_truth
from .layer_a_beta_checks import check_a1, check_a2, check_a3
from .layer_a_runtime_checks import check_a4, check_a5, check_a6


def build_layer_a(
    *,
    subject: dict[str, Any],
    source: str,
    gate: str,
    params: dict[str, Any],
) -> list:
    gt = get_ground_truth(source)
    beta_tol_g = float(params.get("beta_tol_G", 1e-4))
    beta_tol_b = float(params.get("beta_tol_B", 1e-4))
    beta_tol_phi = float(params.get("beta_tol_Phi", 1e-4))
    beta_g = subject.get("beta_G_norm", subject.get("beta_G"))
    beta_b = subject.get("beta_B_norm", subject.get("beta_B"))
    beta_phi = subject.get("beta_Phi_norm", subject.get("beta_Phi"))
    return [
        check_a1(beta_g, gt, beta_tol_g),
        check_a2(beta_b, subject, gt, source, beta_tol_b),
        check_a3(beta_phi, subject, gt, beta_tol_phi),
        check_a4(gate, gt, source),
        check_a5(subject.get("sidrce_omega")),
        check_a6(subject.get("eft_m_kk_gev")),
    ]

