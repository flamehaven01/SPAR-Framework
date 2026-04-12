"""Physics Layer C builder."""

from __future__ import annotations

from typing import Any

from .context_signals import check_c9_leda_maturity_alignment, extract_leda_summary
from .layer_c_advanced import build_layer_c_advanced
from .layer_c_foundations import build_layer_c_foundations


def build_layer_c(
    *,
    subject: dict[str, Any],
    source: str,
    gate: str,
    params: dict[str, Any],
    context: dict[str, Any] | None = None,
) -> list:
    del gate, params
    leda = extract_leda_summary(context)
    return [
        *build_layer_c_foundations(subject=subject, source=source),
        *build_layer_c_advanced(subject=subject),
        check_c9_leda_maturity_alignment(leda),
    ]
