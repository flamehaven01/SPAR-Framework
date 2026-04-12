"""Physics analytical anchor facade."""

from __future__ import annotations

from typing import Any

from .matcher import match_ground_truth_source
from .ground_truth_table import GROUND_TRUTH

PLANCK_MASS_GEV = 1.22e19  # GeV


def get_ground_truth(source: str) -> dict[str, Any] | None:
    key = match_ground_truth_source(source)
    return GROUND_TRUTH.get(key) if key else None
