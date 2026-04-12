"""Physics-domain runtime wiring for standalone SPAR."""

from __future__ import annotations

from typing import Any

from spar_framework.engine import ReviewRuntime

from .layer_a import build_layer_a
from .layer_b import build_layer_b
from .layer_c import build_layer_c
from .registry_seed import physics_registry_snapshots
from .slop_rules import slop_check


def get_review_runtime() -> ReviewRuntime:
    return ReviewRuntime(
        build_layer_a=build_layer_a,
        build_layer_b=build_layer_b,
        build_layer_c=build_layer_c,
        build_model_registry_snapshot=lambda: physics_registry_snapshots()["model_registry_snapshot"],
        build_gap_registry_snapshot=lambda: physics_registry_snapshots()["gap_registry_snapshot"],
        slop_check=slop_check,
    )


def get_runtime_seed() -> dict[str, object]:
    return {
        "registry_snapshots": physics_registry_snapshots(),
        "status": "layer_a_b_c_extracted",
    }
