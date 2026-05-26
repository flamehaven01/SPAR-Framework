"""Generic adapter framework-declared limitation surfaces."""

from __future__ import annotations

from typing import Any

from spar_framework.result_types import CheckResult

from .architecture_gaps import GENERIC_ARCHITECTURE_GAPS


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
            "FD-GA1",
            "Domain-specific evidence policy",
            "DECLARED_NOT_COVERED",
            GENERIC_ARCHITECTURE_GAPS["GA1"],
            basis="framework_declared",
            scope="adapter_limitation",
        ),
        CheckResult(
            "FD-GA2",
            "Cross-domain transfer policy",
            "DECLARED_NOT_COVERED",
            GENERIC_ARCHITECTURE_GAPS["GA2"],
            basis="framework_declared",
            scope="adapter_limitation",
        ),
        CheckResult(
            "FD-GA3",
            "Quantitative metric policy",
            "DECLARED_NOT_COVERED",
            GENERIC_ARCHITECTURE_GAPS["GA3"],
            basis="framework_declared",
            scope="adapter_limitation",
        ),
    ]
