"""Physics Layer B builder."""

from __future__ import annotations

from typing import Any

from .layer_b_admissibility import check_b1, check_b2
from .layer_b_report_checks import check_b3


def build_layer_b(
    *,
    subject: dict[str, Any],
    source: str,
    gate: str,
    report_text: str,
) -> list:
    del source, gate
    b3, _, _ = check_b3(report_text)
    return [
        check_b1(subject.get("eft_m_kk_gev")),
        check_b2(subject.get("ricci_norm")),
        b3,
    ]
