"""Helpers for physics Layer C foundation/existence probes."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .architecture_gaps import PHYSICS_ARCHITECTURE_GAPS


@dataclass(frozen=True)
class BetaBGenuinenessContext:
    beta_b_value: float | None
    h_flux_norm: float
    dilaton_potential: Any
    partial2_b: Any


def _coerce_optional_float(value: Any) -> float | None:
    return float(value) if value is not None else None


def _extract_beta_b_context(subject: dict[str, Any]) -> BetaBGenuinenessContext:
    return BetaBGenuinenessContext(
        beta_b_value=_coerce_optional_float(subject.get("beta_B_norm", subject.get("beta_B"))),
        h_flux_norm=float(subject.get("h_flux_norm", subject.get("h_flux", 0.0))),
        dilaton_potential=subject.get("dilaton_V", subject.get("dilaton_gradient", subject.get("V"))),
        partial2_b=subject.get("partial2_B"),
    )


def _classify_zero_beta_b_case(ctx: BetaBGenuinenessContext) -> tuple[str, str]:
    if ctx.h_flux_norm == 0.0 and ctx.dilaton_potential is None:
        return (
            "GENUINE",
            "beta_B=0: genuine physical zero (no H-flux, no dilaton gradient). Both Term 1 and Term 2 are physically absent.",
        )
    if ctx.partial2_b is None:
        return (
            "GAP",
            f"beta_B={ctx.beta_b_value:.4g}~0 but partial2_B not provided. "
            f"Term 1 (div_H contribution) is silently omitted. {PHYSICS_ARCHITECTURE_GAPS['C1']}",
        )
    return "GENUINE", f"beta_B={ctx.beta_b_value:.4g}: partial2_B provided, Term 1 active."


def evaluate_beta_b_genuineness(subject: dict[str, Any]) -> tuple[str, str]:
    ctx = _extract_beta_b_context(subject)
    if ctx.beta_b_value is not None and abs(ctx.beta_b_value) < 1e-9:
        return _classify_zero_beta_b_case(ctx)
    return "CANNOT_DETERMINE", "beta_B non-zero or unavailable; genuineness depends on H-flux configuration."


def _classify_brst_with_ricci(ricci_norm: float) -> tuple[str, str]:
    if ricci_norm >= 0.1:
        return (
            "GAP",
            f"ricci_norm={ricci_norm:.4g} >= 0.1: alpha' corrections significant. "
            f"Leading-order c_total insufficient for this curvature. {PHYSICS_ARCHITECTURE_GAPS['C2']}",
        )
    if ricci_norm >= 0.01:
        return (
            "APPROXIMATION",
            f"ricci_norm={ricci_norm:.4g}: moderate curvature. "
            f"Leading-order c_total adequate but alpha' gap remains. {PHYSICS_ARCHITECTURE_GAPS['C2']}",
        )
    return (
            "GENUINE",
            f"ricci_norm={ricci_norm:.4g} < 0.01: near-flat. "
            f"Leading-order c_total exact to O(alpha'^2). {PHYSICS_ARCHITECTURE_GAPS['C2']}",
        )


def _source_has_torsion_or_dilaton(source: str) -> bool:
    lowered = source.lower()
    return "wzw" in lowered or "wess-zumino" in lowered or "dilaton" in lowered


def evaluate_brst_genuineness(subject: dict[str, Any], source: str) -> tuple[str, str]:
    ricci_norm = _coerce_optional_float(subject.get("ricci_norm"))
    if ricci_norm is not None:
        return _classify_brst_with_ricci(ricci_norm)
    if _source_has_torsion_or_dilaton(source):
        return "GAP", f"Source '{source}' has torsion/dilaton content (ricci_norm unavailable). {PHYSICS_ARCHITECTURE_GAPS['C2']}"
    return "APPROXIMATION", f"BRST check: leading-order c_total (ricci_norm unavailable). {PHYSICS_ARCHITECTURE_GAPS['C2']}"
