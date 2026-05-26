"""CLI tests for the `spar review` subcommand (SPAR-001, SPAR-003)."""

from __future__ import annotations

import io
import json
from contextlib import redirect_stdout
from pathlib import Path

import pytest

from spar_framework.cli import main


def _write_json(path: Path, payload: dict) -> Path:
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


def _capture_review(argv: list[str]) -> tuple[int, dict]:
    buf = io.StringIO()
    with redirect_stdout(buf):
        code = main(argv)
    out = buf.getvalue().strip()
    parsed = json.loads(out) if out else {}
    return code, parsed


# ---------------------------------------------------------------------------
# SPAR-001 — backward compatibility of --subject-json
# ---------------------------------------------------------------------------


def test_subject_json_still_required_path_works(tmp_path: Path) -> None:
    """Legacy --subject-json invocation must keep working unchanged."""
    subject_path = _write_json(
        tmp_path / "subject.json",
        {
            "theorem_id": "thm-x",
            "theorem_type": "theorem",
            "domain": "topology",
            "claim_profile": {
                "proof_claimed": True,
                "generality_claimed": False,
                "novelty_claimed": False,
            },
            "proof_surface": {
                "proof_status": "complete",
                "assumptions_explicit": True,
                "prior_art_cited": True,
            },
        },
    )
    code, payload = _capture_review(
        ["review", "--adapter", "math", "--subject-json", str(subject_path)]
    )
    assert code == 0
    assert payload["verdict"] in {"ACCEPT", "MINOR_REVISION"}


# ---------------------------------------------------------------------------
# SPAR-001 — mutual exclusion and missing-input errors
# ---------------------------------------------------------------------------


def test_both_subject_and_from_json_is_input_error(tmp_path: Path) -> None:
    subj = _write_json(tmp_path / "s.json", {"claim_profile": {}})
    free = _write_json(tmp_path / "f.json", {"phase": "G1"})
    code, payload = _capture_review(
        [
            "review",
            "--adapter",
            "math",
            "--subject-json",
            str(subj),
            "--from-json",
            str(free),
        ]
    )
    assert code == 2
    assert payload["error"] == "input_error"
    assert "mutually exclusive" in payload["detail"]


def test_neither_subject_nor_from_json_is_input_error() -> None:
    code, payload = _capture_review(["review", "--adapter", "math"])
    assert code == 2
    assert payload["error"] == "input_error"
    assert "--subject-json" in payload["detail"]


# ---------------------------------------------------------------------------
# SPAR-001 — --from-json heuristic mapping
# ---------------------------------------------------------------------------


def test_from_json_heuristic_extracts_report_text(tmp_path: Path) -> None:
    free = _write_json(
        tmp_path / "free.json",
        {
            "theorem_id": "thm-1",
            "theorem_type": "theorem",
            "domain": "topology",
            "claim_profile": {
                "proof_claimed": True,
                "generality_claimed": False,
                "novelty_claimed": False,
            },
            "proof_surface": {
                "proof_status": "complete",
                "assumptions_explicit": True,
                "prior_art_cited": True,
            },
            # heuristic-mapped:
            "report_text": "clearly the result is groundbreaking",
        },
    )
    code, payload = _capture_review(
        ["review", "--adapter", "math", "--from-json", str(free)]
    )
    # report_text routed into layer_b; slop phrases detected so slop_hits non-empty
    assert code in {0, 1}  # depends on score after slop penalty
    assert "clearly" in payload["slop_hits"] or "groundbreaking" in payload["slop_hits"]


def test_from_json_preserves_unrecognised_keys_in_subject(tmp_path: Path) -> None:
    free = _write_json(
        tmp_path / "free.json",
        {
            "theorem_id": "thm-2",
            "theorem_type": "theorem",
            "domain": "topology",
            "phase": "G2",
            "delta_ricci": 0.02,
            "claim_profile": {
                "proof_claimed": False,
                "generality_claimed": False,
                "novelty_claimed": False,
            },
            "proof_surface": {
                "proof_status": "complete",
                "assumptions_explicit": True,
                "prior_art_cited": True,
            },
        },
    )
    code, payload = _capture_review(
        ["review", "--adapter", "math", "--from-json", str(free)]
    )
    # Unrecognised keys (phase, delta_ricci) must not crash the run.
    assert code == 0
    assert payload["verdict"] in {"ACCEPT", "MINOR_REVISION"}


def test_from_json_subject_wrapper_is_unwrapped(tmp_path: Path) -> None:
    free = _write_json(
        tmp_path / "free.json",
        {
            "subject": {
                "theorem_id": "thm-3",
                "theorem_type": "theorem",
                "domain": "topology",
                "claim_profile": {
                    "proof_claimed": True,
                    "generality_claimed": False,
                    "novelty_claimed": False,
                },
                "proof_surface": {
                    "proof_status": "complete",
                    "assumptions_explicit": True,
                    "prior_art_cited": True,
                },
            }
        },
    )
    code, payload = _capture_review(
        ["review", "--adapter", "math", "--from-json", str(free)]
    )
    assert code == 0
    assert payload["verdict"] in {"ACCEPT", "MINOR_REVISION"}


def test_from_json_payload_must_be_object(tmp_path: Path) -> None:
    bad = tmp_path / "bad.json"
    bad.write_text("[1, 2, 3]", encoding="utf-8")
    code, payload = _capture_review(
        ["review", "--adapter", "math", "--from-json", str(bad)]
    )
    assert code == 2
    assert payload["error"] == "input_error"
