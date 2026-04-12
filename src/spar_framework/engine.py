"""Domain-agnostic SPAR orchestration kernel."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

from .context import summarize_review_context
from .result_types import ReviewResult
from .runtime_context import build_core_review, build_registry_snapshots

LayerBuilder = Callable[..., list]
SlopChecker = Callable[[str], tuple[int, list[str]]]


@dataclass(frozen=True)
class ReviewRuntime:
    build_layer_a: LayerBuilder
    build_layer_b: LayerBuilder
    build_layer_c: LayerBuilder
    build_model_registry_snapshot: Callable[[], dict[str, Any] | None] | None = None
    build_gap_registry_snapshot: Callable[[], dict[str, Any] | None] | None = None
    slop_check: SlopChecker | None = None


def run_review(
    *,
    runtime: ReviewRuntime,
    subject: Any,
    source: str = "",
    gate: str = "",
    params: dict[str, Any] | None = None,
    report_text: str = "",
    memory_context: dict[str, Any] | None = None,
    leda_injection: dict[str, Any] | None = None,
) -> ReviewResult:
    params = params or {}
    context = {
        "memory_context": memory_context,
        "leda_injection": leda_injection,
    }

    layer_a = runtime.build_layer_a(
        subject=subject, source=source, gate=gate, params=params, context=context
    )
    layer_b = runtime.build_layer_b(
        subject=subject,
        source=source,
        gate=gate,
        report_text=report_text,
        context=context,
    )
    layer_c = runtime.build_layer_c(
        subject=subject, source=source, gate=gate, params=params, context=context
    )

    slop_penalty = 0
    slop_hits: list[str] = []
    if runtime.slop_check is not None and report_text:
        slop_penalty, slop_hits = runtime.slop_check(report_text)

    core_review = build_core_review(
        layer_a=layer_a,
        layer_b=layer_b,
        layer_c=layer_c,
        slop_penalty=slop_penalty,
    )
    registry_snapshots = build_registry_snapshots(
        model_registry_snapshot=runtime.build_model_registry_snapshot() if runtime.build_model_registry_snapshot else None,
        gap_registry_snapshot=runtime.build_gap_registry_snapshot() if runtime.build_gap_registry_snapshot else None,
    )

    return ReviewResult(
        subject=str(subject),
        gate=gate,
        layer_a=layer_a,
        layer_b=layer_b,
        layer_c=layer_c,
        score=core_review["score"],
        grade=core_review["grade"],
        verdict=core_review["verdict"],
        slop_hits=slop_hits,
        context_summary=summarize_review_context(
            memory_context=memory_context,
            leda_injection=leda_injection,
        ),
        model_registry_snapshot=registry_snapshots["model_registry_snapshot"],
        gap_registry_snapshot=registry_snapshots["gap_registry_snapshot"],
    )
