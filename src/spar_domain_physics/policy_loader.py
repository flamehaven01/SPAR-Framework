"""Load packaged physics review policy surfaces."""

from __future__ import annotations

from functools import lru_cache
from typing import Any

from spar_framework.package_data import load_packaged_json


@lru_cache(maxsize=1)
def load_physics_review_policy() -> dict[str, Any]:
    return load_packaged_json(
        "spar_domain_physics",
        "policies",
        "physics_review_policy.v1.json",
    )


def get_physics_ground_truth() -> dict[str, dict[str, Any]]:
    return load_physics_review_policy()["ground_truth"]


def get_planck_mass_gev() -> float:
    return float(load_physics_review_policy()["constants"]["planck_mass_gev"])


def get_layer_a_defaults() -> dict[str, Any]:
    return load_physics_review_policy()["layer_a"]


def get_layer_b_thresholds() -> dict[str, Any]:
    return load_physics_review_policy()["layer_b"]
