"""Workflow helpers for contextual SPAR review."""

from __future__ import annotations

from typing import Any

from .context import load_leda_injection, load_mica_context
from .mica import load_mica_runtime_context
from .engine import ReviewRuntime, run_review
from .result_types import ReviewResult


def run_contextual_review(
    *,
    runtime: ReviewRuntime,
    subject: Any,
    source: str = "",
    gate: str = "",
    params: dict[str, Any] | None = None,
    report_text: str = "",
    project_root: str | None = None,
    mica_context_path: str | None = None,
    leda_injection_path: str | None = None,
    leda_profile: str = "restricted",
) -> ReviewResult:
    """Run SPAR review with optional MICA and LEDA context loading."""
    memory_context = (
        load_mica_context(mica_context_path)
        if mica_context_path
        else load_mica_runtime_context(project_root=project_root)
        if project_root
        else None
    )
    leda_injection = (
        load_leda_injection(leda_injection_path, profile=leda_profile)
        if leda_injection_path
        else None
    )
    return run_review(
        runtime=runtime,
        subject=subject,
        source=source,
        gate=gate,
        params=params,
        report_text=report_text,
        memory_context=memory_context,
        leda_injection=leda_injection,
    )
