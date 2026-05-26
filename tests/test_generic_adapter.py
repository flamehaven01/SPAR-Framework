"""Tests for the generic (domain-agnostic) adapter (SPAR-002)."""

from __future__ import annotations

import io
import json
from contextlib import redirect_stdout

import pytest

from spar_domain_generic.runtime import get_review_runtime
from spar_framework.cli import main
from spar_framework.engine import run_review


def _capture(argv: list[str]) -> tuple[int, dict]:
    buf = io.StringIO()
    with redirect_stdout(buf):
        code = main(argv)
    out = buf.getvalue().strip()
    return code, (json.loads(out) if out else {})


def test_runtime_runs_clean_claim() -> None:
    runtime = get_review_runtime()
    subject = {
        "claim_id": "c-1",
        "claim_profile": {
            "claim_made": True,
            "evidence_cited": True,
            "scope_bounded": True,
        },
    }
    result = run_review(runtime=runtime, subject=subject, report_text="")
    assert result.verdict in {"ACCEPT", "MINOR_REVISION"}
    assert any(check.check_id == "A1" for check in result.layer_a)
    assert "no_observation_source" not in result.warnings


def test_runtime_flags_missing_evidence() -> None:
    runtime = get_review_runtime()
    subject = {
        "claim_profile": {
            "claim_made": True,
            "evidence_cited": False,
            "scope_bounded": True,
        },
    }
    result = run_review(runtime=runtime, subject=subject, report_text="")
    a1 = next(c for c in result.layer_a if c.check_id == "A1")
    assert a1.status == "FAIL"
    c1 = next(c for c in result.layer_c if c.check_id == "C1")
    assert c1.status == "GAP"


def test_slop_rules_detect_buzz() -> None:
    runtime = get_review_runtime()
    subject = {"claim_profile": {"claim_made": False}}
    result = run_review(
        runtime=runtime,
        subject=subject,
        report_text="this is a groundbreaking, state-of-the-art result, clearly",
    )
    assert "groundbreaking" in result.slop_hits
    assert "state-of-the-art" in result.slop_hits
    assert "clearly" in result.slop_hits


def test_framework_declared_emits_three_gaps() -> None:
    runtime = get_review_runtime()
    result = run_review(runtime=runtime, subject={"claim_profile": {}})
    fd_ids = {check.check_id for check in result.framework_declared}
    assert fd_ids == {"FD-GA1", "FD-GA2", "FD-GA3"}


def test_registry_snapshot_has_three_models() -> None:
    runtime = get_review_runtime()
    result = run_review(runtime=runtime, subject={"claim_profile": {}})
    assert result.model_registry_snapshot is not None
    assert result.model_registry_snapshot["total_models"] == 3


def test_cli_review_generic_adapter_subject_json(tmp_path) -> None:
    subj = tmp_path / "subject.json"
    subj.write_text(
        json.dumps(
            {
                "claim_profile": {
                    "claim_made": True,
                    "evidence_cited": True,
                    "scope_bounded": True,
                }
            }
        ),
        encoding="utf-8",
    )
    code, payload = _capture(
        ["review", "--adapter", "generic", "--subject-json", str(subj)]
    )
    assert code == 0
    assert payload["verdict"] in {"ACCEPT", "MINOR_REVISION"}


def test_cli_review_generic_adapter_from_json(tmp_path) -> None:
    free = tmp_path / "free.json"
    free.write_text(
        json.dumps(
            {
                "claim_profile": {
                    "claim_made": True,
                    "evidence_cited": True,
                    "scope_bounded": True,
                },
                "report_text": "we show the result holds",
            }
        ),
        encoding="utf-8",
    )
    code, payload = _capture(
        ["review", "--adapter", "generic", "--from-json", str(free)]
    )
    assert code == 0
    assert payload["verdict"] in {"ACCEPT", "MINOR_REVISION"}
