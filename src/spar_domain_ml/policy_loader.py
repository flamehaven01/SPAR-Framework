"""Load packaged ML review policy surfaces."""

from __future__ import annotations

from functools import lru_cache
from typing import Any

from spar_framework.package_data import load_packaged_json


@lru_cache(maxsize=1)
def load_ml_review_policy() -> dict[str, Any]:
    return load_packaged_json("spar_domain_ml", "policies", "ml_review_policy.v1.json")


def get_layer_a_rules() -> dict[str, Any]:
    return load_ml_review_policy()["layer_a"]


def get_layer_b_phrases() -> dict[str, Any]:
    return load_ml_review_policy()["layer_b"]


def get_layer_c_thresholds() -> dict[str, Any]:
    return load_ml_review_policy()["layer_c"]
