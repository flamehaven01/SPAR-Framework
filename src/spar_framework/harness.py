"""Batch review harness and multi-review comparison surface."""

from __future__ import annotations

import json
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from .engine import ReviewRuntime, run_review


@dataclass
class BatchSummary:
    adapter: str
    count: int
    verdicts: dict[str, int]
    mean_claim_drift: float
    mean_coverage_rate: float
    cannot_check_rate: float
    framework_declared_rate: float
    top_flags: list[str]

    def to_dict(self) -> dict[str, Any]:
        return {
            "adapter": self.adapter,
            "count": self.count,
            "verdicts": self.verdicts,
            "mean_claim_drift": round(self.mean_claim_drift, 4),
            "mean_coverage_rate": round(self.mean_coverage_rate, 4),
            "cannot_check_rate": round(self.cannot_check_rate, 4),
            "framework_declared_rate": round(self.framework_declared_rate, 4),
            "top_flags": self.top_flags,
        }


def run_batch(
    runtime: ReviewRuntime,
    adapter: str,
    subject_paths: list[Path],
    *,
    report_text: str = "",
    source: str = "",
    gate: str = "",
    reports_dir: Path | None = None,
) -> BatchSummary:
    """Run review on each subject file and return an aggregated BatchSummary."""
    results: list[dict[str, Any]] = []

    for path in subject_paths:
        payload = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(payload, dict) and isinstance(payload.get("subject"), dict):
            subject = payload["subject"]
        else:
            subject = payload

        result = run_review(
            runtime=runtime,
            subject=subject,
            source=source,
            gate=gate,
            report_text=report_text,
        )
        result_dict = result.to_dict()
        result_dict["_source_file"] = path.name
        results.append(result_dict)

        if reports_dir is not None:
            reports_dir.mkdir(parents=True, exist_ok=True)
            out_path = reports_dir / f"{path.stem}_review.json"
            out_path.write_text(json.dumps(result_dict, indent=2), encoding="utf-8")

    return _compute_summary(adapter, results)


def _compute_summary(adapter: str, results: list[dict[str, Any]]) -> BatchSummary:
    count = len(results)
    if count == 0:
        return BatchSummary(
            adapter=adapter, count=0, verdicts={}, mean_claim_drift=0.0,
            mean_coverage_rate=0.0, cannot_check_rate=0.0,
            framework_declared_rate=0.0, top_flags=[],
        )

    verdict_counter: Counter[str] = Counter()
    claim_drifts: list[float] = []
    coverage_rates: list[float] = []
    cannot_check_rates: list[float] = []
    fd_rates: list[float] = []
    flag_counter: Counter[str] = Counter()

    for r in results:
        verdict_counter[r.get("verdict", "UNKNOWN")] += 1
        claim_drifts.append(float(r.get("claim_drift") or 0))
        coverage_rates.append(float(r.get("coverage_rate") or 0.0))

        subject_checks = (
            r.get("layer_a", []) + r.get("layer_b", []) + r.get("layer_c", [])
        )
        fd_checks = r.get("framework_declared", [])
        total_subject = len(subject_checks)
        total_all = total_subject + len(fd_checks)

        cannot_check_rates.append(
            sum(1 for c in subject_checks if c.get("status") == "CANNOT_CHECK") / total_subject
            if total_subject else 0.0
        )
        fd_rates.append(len(fd_checks) / total_all if total_all else 0.0)

        for c in subject_checks:
            if c.get("status") not in {"PASS", "CONSISTENT", "GENUINE", "CANNOT_CHECK"}:
                flag_counter[c["check_id"]] += 1

    top_flags = [check_id for check_id, _ in flag_counter.most_common(5)]

    return BatchSummary(
        adapter=adapter,
        count=count,
        verdicts=dict(verdict_counter),
        mean_claim_drift=sum(claim_drifts) / count,
        mean_coverage_rate=sum(coverage_rates) / count,
        cannot_check_rate=sum(cannot_check_rates) / count,
        framework_declared_rate=sum(fd_rates) / count,
        top_flags=top_flags,
    )


def compare_reviews(review_paths: list[Path]) -> list[dict[str, Any]]:
    """Extract key metrics from multiple review JSON files for side-by-side comparison."""
    comparisons = []
    for path in review_paths:
        r = json.loads(path.read_text(encoding="utf-8"))
        subject_checks = r.get("layer_a", []) + r.get("layer_b", []) + r.get("layer_c", [])
        comparisons.append({
            "file": path.name,
            "verdict": r.get("verdict"),
            "score": r.get("score"),
            "grade": r.get("grade"),
            "claim_drift": r.get("claim_drift"),
            "coverage_rate": r.get("coverage_rate"),
            "flags": [
                c["check_id"] for c in subject_checks
                if c.get("status") not in {"PASS", "CONSISTENT", "GENUINE", "CANNOT_CHECK"}
            ],
        })
    return comparisons
