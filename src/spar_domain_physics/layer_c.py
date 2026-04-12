"""Physics Layer C builder."""

from __future__ import annotations

from typing import Any

from .layer_c_advanced import build_layer_c_advanced
from .layer_c_foundations import build_layer_c_foundations


def build_layer_c(
    *,
    subject: dict[str, Any],
    source: str,
    gate: str,
    params: dict[str, Any],
) -> list:
    del gate, params
    return [
        *build_layer_c_foundations(subject=subject, source=source),
        *build_layer_c_advanced(subject=subject),
    ]
