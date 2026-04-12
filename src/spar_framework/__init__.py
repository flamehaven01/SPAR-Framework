"""Standalone SPAR framework scaffold."""

__version__ = "0.1.1"

from .engine import ReviewRuntime, run_review
from .interfaces import LayerABuilder, LayerBBuilder, LayerCBuilder
from .context import load_leda_injection, load_mica_context, summarize_review_context
from .mica import discover_mica_runtime, load_mica_runtime_context
from .result_types import CheckResult, ReviewResult
from .runtime_context import build_core_review, build_registry_snapshots
from .scoring import ReviewPolicy, compute_score, default_policy, grade_from_score, journal_verdict
from .registry import GapSpec, ModelSpec, gap_registry_snapshot, model_registry_snapshot
from .workflow import run_contextual_review

__all__ = [
    "__version__",
    "CheckResult",
    "ReviewResult",
    "ReviewRuntime",
    "run_review",
    "run_contextual_review",
    "LayerABuilder",
    "LayerBBuilder",
    "LayerCBuilder",
    "load_mica_context",
    "discover_mica_runtime",
    "load_mica_runtime_context",
    "load_leda_injection",
    "summarize_review_context",
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
