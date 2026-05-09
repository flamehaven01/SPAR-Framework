"""Core result types for standalone SPAR."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

STATUS = str


@dataclass
class CheckResult:
    check_id: str
    label: str
    status: STATUS
    detail: str
    ref: str = ""
    basis: str = "subject_derived"
    scope: str = "subject"

    def to_dict(self) -> dict[str, Any]:
        return {
            "check_id": self.check_id,
            "label": self.label,
            "status": self.status,
            "detail": self.detail,
            "ref": self.ref,
            "basis": self.basis,
            "scope": self.scope,
        }


@dataclass
class ReviewResult:
    subject: str
    gate: str = ""
    layer_a: list[CheckResult] = field(default_factory=list)
    layer_b: list[CheckResult] = field(default_factory=list)
    layer_c: list[CheckResult] = field(default_factory=list)
    framework_declared: list[CheckResult] = field(default_factory=list)
    score: int = 100
    grade: str = "PASS"
    verdict: str = "ACCEPT"
    claim_drift: int = 0
    coverage_rate: float = 0.0
    slop_hits: list[str] = field(default_factory=list)
    context_summary: dict[str, Any] | None = None
    model_registry_snapshot: dict[str, Any] | None = None
    gap_registry_snapshot: dict[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "subject": self.subject,
            "gate": self.gate,
            "score": self.score,
            "grade": self.grade,
            "verdict": self.verdict,
            "claim_drift": self.claim_drift,
            "coverage_rate": self.coverage_rate,
            "slop_hits": self.slop_hits,
            "context_summary": self.context_summary,
            "model_registry_snapshot": self.model_registry_snapshot,
            "gap_registry_snapshot": self.gap_registry_snapshot,
            "layer_a": [item.to_dict() for item in self.layer_a],
            "layer_b": [item.to_dict() for item in self.layer_b],
            "layer_c": [item.to_dict() for item in self.layer_c],
            "framework_declared": [item.to_dict() for item in self.framework_declared],
        }
