"""Markdown rendering for SPAR batch summaries and comparison tables."""

from __future__ import annotations

from typing import Any

from .harness import BatchSummary

_VERDICT_ORDER = ["ACCEPT", "MINOR_REVISION", "MAJOR_REVISION", "REJECT"]


def batch_summary_to_markdown(summary: BatchSummary) -> str:
    lines = [
        "# SPAR Batch Review Summary",
        "",
        f"**Adapter:** `{summary.adapter}`  ",
        f"**Subjects reviewed:** {summary.count}",
        "",
        "## Verdict Distribution",
        "",
    ]

    for verdict in _VERDICT_ORDER:
        n = summary.verdicts.get(verdict, 0)
        pct = n / summary.count * 100 if summary.count else 0
        lines.append(f"- **{verdict}**: {n} ({pct:.0f}%)")

    lines += [
        "",
        "## Metrics",
        "",
        "| Metric | Value |",
        "|--------|-------|",
        f"| Mean claim drift | {summary.mean_claim_drift:.4f} |",
        f"| Mean coverage rate | {summary.mean_coverage_rate:.4f} |",
        f"| CANNOT_CHECK rate | {summary.cannot_check_rate:.4f} |",
        f"| Framework-declared rate | {summary.framework_declared_rate:.4f} |",
        "",
    ]

    if summary.top_flags:
        lines += ["## Top Flags", ""]
        for flag in summary.top_flags:
            lines.append(f"- `{flag}`")
        lines.append("")

    return "\n".join(lines)


def compare_reviews_to_markdown(comparisons: list[dict[str, Any]]) -> str:
    lines = [
        "# SPAR Review Comparison",
        "",
        "| File | Verdict | Score | Claim Drift | Coverage | Flags |",
        "|------|---------|-------|-------------|----------|-------|",
    ]
    for c in comparisons:
        flags = ", ".join(f"`{f}`" for f in c.get("flags", [])) or "-"
        cov = f"{c['coverage_rate']:.4f}" if c.get("coverage_rate") is not None else "-"
        lines.append(
            f"| {c['file']} | {c['verdict']} | {c['score']} | "
            f"{c['claim_drift']} | {cov} | {flags} |"
        )
    lines.append("")
    return "\n".join(lines)
