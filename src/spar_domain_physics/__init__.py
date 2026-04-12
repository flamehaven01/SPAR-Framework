"""Physics-domain adapter seed package for SPAR."""

from .architecture_gaps import PHYSICS_ARCHITECTURE_GAPS
from .layer_a import build_layer_a
from .layer_b import build_layer_b
from .layer_c import build_layer_c
from .ground_truth import get_ground_truth
from .registry_seed import (
    PHYSICS_GAPS,
    PHYSICS_MODELS,
    format_gap_state,
    get_physics_gap,
    physics_gap_registry_snapshot,
    physics_model_registry_snapshot,
    physics_registry_snapshots,
)
from .runtime import get_review_runtime
from .slop_rules import slop_check

__all__ = [
    "PHYSICS_ARCHITECTURE_GAPS",
    "PHYSICS_GAPS",
    "PHYSICS_MODELS",
    "build_layer_a",
    "build_layer_b",
    "build_layer_c",
    "format_gap_state",
    "get_ground_truth",
    "get_physics_gap",
    "get_review_runtime",
    "physics_gap_registry_snapshot",
    "physics_model_registry_snapshot",
    "physics_registry_snapshots",
    "slop_check",
]
