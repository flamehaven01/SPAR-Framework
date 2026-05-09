"""Math adapter framework-declared limitation surfaces."""

from __future__ import annotations

from typing import Any

from spar_framework.result_types import CheckResult

from .architecture_gaps import MATH_ARCHITECTURE_GAPS


def build_framework_declared_checks(
    *,
    subject: dict[str, Any],
    source: str = "",
    gate: str = "",
    params: dict[str, Any] | None = None,
    context: dict[str, Any] | None = None,
) -> list[CheckResult]:
    del subject, source, gate, params, context
    return [
        CheckResult(
            "FD-MA1",
            "Formal verification coverage policy",
            "DECLARED_NOT_COVERED",
            MATH_ARCHITECTURE_GAPS["MA1"],
            basis="framework_declared",
            scope="adapter_limitation",
        ),
        CheckResult(
            "FD-MA2",
            "Cross-domain transfer policy",
            "DECLARED_NOT_COVERED",
            MATH_ARCHITECTURE_GAPS["MA2"],
            basis="framework_declared",
            scope="adapter_limitation",
        ),
        CheckResult(
            "FD-MA3",
            "Conjecture tracking policy",
            "DECLARED_PARTIAL",
            MATH_ARCHITECTURE_GAPS["MA3"],
            basis="framework_declared",
            scope="adapter_limitation",
        ),
    ]
