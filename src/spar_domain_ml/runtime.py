"""ML adapter runtime entry point for the SPAR framework."""

from __future__ import annotations

from spar_framework.engine import ReviewRuntime

from .layer_a import build_layer_a_checks
from .layer_b import build_layer_b_checks
from .layer_c import build_layer_c_checks
from .layer_c_advanced import build_framework_declared_checks
from .registry_seed import ml_gap_registry_snapshot, ml_model_registry_snapshot
from .slop_rules import slop_check


def get_review_runtime() -> ReviewRuntime:
    return ReviewRuntime(
        build_layer_a=build_layer_a_checks,
        build_layer_b=build_layer_b_checks,
        build_layer_c=build_layer_c_checks,
        build_framework_declared=build_framework_declared_checks,
        build_model_registry_snapshot=ml_model_registry_snapshot,
        build_gap_registry_snapshot=ml_gap_registry_snapshot,
        slop_check=slop_check,
    )
