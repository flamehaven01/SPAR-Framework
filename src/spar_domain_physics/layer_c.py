"""Physics Layer C builder."""

from __future__ import annotations

from typing import Any

from .context_signals import (
    check_c10_mica_invariant_continuity,
    check_c9_leda_maturity_alignment,
    extract_leda_summary,
    extract_mica_summary,
)
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
    # Layer C is scoped to implementation-path and maturity probes in the
    # current adapter. Gate and free-form params are reserved for future
    # extensions but do not influence the existing checks.
    del gate, params
    leda = extract_leda_summary(context)
    mica = extract_mica_summary(context)
    return [
        *build_layer_c_foundations(subject=subject, source=source),
        *build_layer_c_advanced(subject=subject),
        check_c9_leda_maturity_alignment(leda),
        check_c10_mica_invariant_continuity(mica),
    ]
