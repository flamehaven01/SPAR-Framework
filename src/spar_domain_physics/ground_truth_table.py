"""Physics analytical anchor table loaded from packaged policy data."""

from __future__ import annotations

from .policy_loader import get_physics_ground_truth

GROUND_TRUTH = get_physics_ground_truth()
