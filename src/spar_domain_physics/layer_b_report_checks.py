"""Physics Layer B report-text checks."""

from __future__ import annotations

from spar_framework.result_types import CheckResult

from .slop_rules import slop_check


def check_b3(report_text: str) -> tuple[CheckResult, int, list[str]]:
    if not report_text:
        return (
            CheckResult(
                "B3",
                "Slop detection",
                "CANNOT_CHECK",
                "No report text to scan",
            ),
            0,
            [],
        )

    penalty, hits = slop_check(report_text)
    if not hits:
        return (
            CheckResult("B3", "Slop detection", "PASS", "No generalisation phrases detected"),
            penalty,
            hits,
        )

    return (
        CheckResult(
            "B3",
            "Slop detection",
            "WARN",
            f"Generalisation phrases detected (-{penalty} pts): {hits}",
        ),
        penalty,
        hits,
    )
