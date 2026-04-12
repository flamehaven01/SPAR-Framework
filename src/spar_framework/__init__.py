"""Standalone SPAR framework scaffold."""

__version__ = "0.1.1"

from .engine import ReviewRuntime, run_review
from .interfaces import LayerABuilder, LayerBBuilder, LayerCBuilder
from .result_types import CheckResult, ReviewResult
from .runtime_context import build_core_review, build_registry_snapshots
from .scoring import ReviewPolicy, compute_score, default_policy, grade_from_score, journal_verdict
from .registry import GapSpec, ModelSpec, gap_registry_snapshot, model_registry_snapshot

__all__ = [
    "__version__",
    "CheckResult",
    "ReviewResult",
    "ReviewRuntime",
    "run_review",
    "LayerABuilder",
    "LayerBBuilder",
    "LayerCBuilder",
    "ReviewPolicy",
    "compute_score",
    "default_policy",
    "grade_from_score",
    "journal_verdict",
    "build_core_review",
    "build_registry_snapshots",
    "GapSpec",
    "ModelSpec",
    "gap_registry_snapshot",
    "model_registry_snapshot",
]
