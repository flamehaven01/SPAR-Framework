"""Physics analytical anchor facade."""

from __future__ import annotations

from typing import Any

from .matcher import match_ground_truth_source
from .ground_truth_table import GROUND_TRUTH
from .policy_loader import get_planck_mass_gev

PLANCK_MASS_GEV = get_planck_mass_gev()


def get_ground_truth(source: str) -> dict[str, Any] | None:
    key = match_ground_truth_source(source)
    return GROUND_TRUTH.get(key) if key else None
