"""Tests for ReviewResult.warnings (SPAR-003)."""

from __future__ import annotations

from spar_framework.engine import ReviewRuntime, run_review
from spar_framework.result_types import CheckResult


def _empty_layer(**_kwargs) -> list[CheckResult]:
    return []


def _one_pass_layer_a(**_kwargs) -> list[CheckResult]:
    return [CheckResult("A1", "stub", "PASS", "ok")]


def test_warning_emitted_when_layer_a_empty_and_no_drift() -> None:
    runtime = ReviewRuntime(
        build_layer_a=_empty_layer,
        build_layer_b=_empty_layer,
        build_layer_c=_empty_layer,
    )
    result = run_review(runtime=runtime, subject={})
    assert "no_observation_source" in result.warnings
    payload = result.to_dict()
    assert payload["warnings"] == ["no_observation_source"]


def test_no_warning_when_layer_a_has_checks() -> None:
    runtime = ReviewRuntime(
        build_layer_a=_one_pass_layer_a,
        build_layer_b=_empty_layer,
        build_layer_c=_empty_layer,
    )
    result = run_review(runtime=runtime, subject={})
    assert "no_observation_source" not in result.warnings


def test_no_warning_when_claim_drift_nonzero() -> None:
    def _layer_with_drift(**_kwargs) -> list[CheckResult]:
        # FAIL incurs a non-zero penalty -> claim_drift > 0
        return [CheckResult("B1", "stub", "FAIL", "broken")]

    runtime = ReviewRuntime(
        build_layer_a=_empty_layer,
        build_layer_b=_layer_with_drift,
        build_layer_c=_empty_layer,
    )
    result = run_review(runtime=runtime, subject={})
    assert result.claim_drift > 0
    assert "no_observation_source" not in result.warnings


def test_warnings_omitted_from_to_dict_when_empty() -> None:
    runtime = ReviewRuntime(
        build_layer_a=_one_pass_layer_a,
        build_layer_b=_empty_layer,
        build_layer_c=_empty_layer,
    )
    result = run_review(runtime=runtime, subject={})
    payload = result.to_dict()
    assert "warnings" not in payload
