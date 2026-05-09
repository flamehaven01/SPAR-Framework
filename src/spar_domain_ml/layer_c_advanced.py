"""ML adapter framework-declared limitation surfaces."""

from __future__ import annotations

from typing import Any

from spar_framework.result_types import CheckResult

from .architecture_gaps import ML_ARCHITECTURE_GAPS


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
            "FD-M1",
            "Extended claim class coverage policy",
            "DECLARED_NOT_COVERED",
            ML_ARCHITECTURE_GAPS["M1"],
            basis="framework_declared",
            scope="adapter_limitation",
        ),
        CheckResult(
            "FD-M2",
            "Temporal drift analysis policy",
            "DECLARED_NOT_COVERED",
            ML_ARCHITECTURE_GAPS["M2"],
            basis="framework_declared",
            scope="adapter_limitation",
        ),
        CheckResult(
            "FD-M3",
            "Cross-task generalization policy",
            "DECLARED_PARTIAL",
            ML_ARCHITECTURE_GAPS["M3"],
            basis="framework_declared",
            scope="adapter_limitation",
        ),
    ]
