"""Tests for $SPAR_POLICY_PATH env-var override (SPAR-005)."""

from __future__ import annotations

import json
import os
from pathlib import Path

import pytest

from spar_framework import scoring


@pytest.fixture(autouse=True)
def _reset_cache_and_env(monkeypatch: pytest.MonkeyPatch):
    """Ensure each test starts with a clean cache and no env override."""
    monkeypatch.delenv("SPAR_POLICY_PATH", raising=False)
    scoring._load_review_policy.cache_clear()
    yield
    scoring._load_review_policy.cache_clear()


def test_default_policy_loads_from_package_when_env_unset() -> None:
    policy = scoring._load_review_policy()
    assert "scoring" in policy
    assert "verdict" in policy


def test_env_var_override_loads_custom_policy(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    custom = {
        "scoring": {
            "base_score": 50,
            "penalties": {"FAIL": -99},
            "slop_penalty_per_hit": 1,
            "coverage_rate_precision": 2,
        },
        "verdict": {
            "accept_threshold": 40,
            "minor_revision_threshold": 30,
            "major_revision_threshold": 20,
            "layer_a_anomaly_reject_count": 1,
        },
        "grade": {"pass_threshold": 25},
    }
    policy_path = tmp_path / "custom_policy.json"
    policy_path.write_text(json.dumps(custom), encoding="utf-8")

    monkeypatch.setenv("SPAR_POLICY_PATH", str(policy_path))
    scoring._load_review_policy.cache_clear()

    loaded = scoring._load_review_policy()
    assert loaded["scoring"]["base_score"] == 50
    assert loaded["verdict"]["accept_threshold"] == 40


def test_env_var_pointing_to_missing_file_raises(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    missing = tmp_path / "does_not_exist.json"
    monkeypatch.setenv("SPAR_POLICY_PATH", str(missing))
    scoring._load_review_policy.cache_clear()

    with pytest.raises(FileNotFoundError):
        scoring._load_review_policy()


def test_whitespace_only_env_var_falls_back_to_default(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("SPAR_POLICY_PATH", "   ")
    scoring._load_review_policy.cache_clear()
    policy = scoring._load_review_policy()
    # Falls through to packaged default; structure intact
    assert "scoring" in policy
