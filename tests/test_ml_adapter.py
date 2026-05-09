"""Regression tests for the spar_domain_ml benchmark claim-drift adapter."""

from __future__ import annotations


def _base_subject(**overrides):
    subject = {
        "task_family": "image_classification",
        "dataset": "ImageNet-1k",
        "split": "val",
        "metric_name": "top1_accuracy",
        "metric_value": 0.912,
        "metric_direction": "higher_is_better",
        "baseline_name": "prior_sota",
        "baseline_value": 0.905,
        "claim_profile": {
            "sota_claimed": True,
            "generalization_claimed": False,
            "robustness_claimed": False,
        },
        "reproducibility": {
            "seed_present": True,
            "dataset_version_present": True,
            "config_hash_present": True,
        },
        "evaluation_scope": {
            "ood_evaluated": False,
            "robustness_evaluated": False,
            "claim_scope_restricted": False,
        },
    }
    subject.update(overrides)
    return subject


# ---------------------------------------------------------------------------
# Runtime wiring
# ---------------------------------------------------------------------------


def test_ml_runtime_produces_review_result():
    from spar_domain_ml.runtime import get_review_runtime
    from spar_framework.engine import run_review

    result = run_review(
        runtime=get_review_runtime(),
        subject=_base_subject(),
        source="imagenet_val",
        gate="PASS",
        report_text="We report top-1 accuracy on ImageNet-1k validation split.",
    )
    assert result.verdict in {"ACCEPT", "MINOR_REVISION", "MAJOR_REVISION", "REJECT"}
    assert result.score >= 0
    assert result.model_registry_snapshot is not None
    assert result.gap_registry_snapshot is not None


def test_ml_framework_declared_have_adapter_limitation_scope():
    from spar_domain_ml.layer_c_advanced import build_framework_declared_checks

    checks = build_framework_declared_checks(subject={})
    for check in checks:
        assert check.scope == "adapter_limitation", f"{check.check_id} scope={check.scope!r}"
        assert check.basis == "framework_declared"


# ---------------------------------------------------------------------------
# Claim drift case 1: SOTA claim without baseline -> FAIL
# ---------------------------------------------------------------------------


def test_sota_claim_without_baseline_fails():
    from spar_domain_ml.layer_a import check_a1_sota

    subject = _base_subject()
    del subject["baseline_value"]
    result = check_a1_sota(subject)
    assert result.status == "FAIL", f"Expected FAIL, got {result.status}"


# ---------------------------------------------------------------------------
# Claim drift case 2: generalization claim without OOD or scope restriction -> GAP
# ---------------------------------------------------------------------------


def test_generalization_claim_without_ood_or_restriction_is_gap():
    from spar_domain_ml.layer_a import check_a2_generalization

    subject = _base_subject(
        claim_profile={"sota_claimed": False, "generalization_claimed": True, "robustness_claimed": False},
        evaluation_scope={"ood_evaluated": False, "robustness_evaluated": False, "claim_scope_restricted": False},
    )
    result = check_a2_generalization(subject)
    assert result.status == "GAP"


def test_generalization_claim_with_scope_restriction_passes():
    from spar_domain_ml.layer_a import check_a2_generalization

    subject = _base_subject(
        claim_profile={"sota_claimed": False, "generalization_claimed": True, "robustness_claimed": False},
        evaluation_scope={"ood_evaluated": False, "robustness_evaluated": False, "claim_scope_restricted": True},
    )
    result = check_a2_generalization(subject)
    assert result.status == "CONSISTENT"


# ---------------------------------------------------------------------------
# Claim drift case 3: robustness claim without eval -> GAP
# ---------------------------------------------------------------------------


def test_robustness_claim_without_eval_is_gap():
    from spar_domain_ml.layer_a import check_a3_robustness

    subject = _base_subject(
        claim_profile={"sota_claimed": False, "generalization_claimed": False, "robustness_claimed": True},
        evaluation_scope={"ood_evaluated": False, "robustness_evaluated": False, "claim_scope_restricted": False},
    )
    result = check_a3_robustness(subject)
    assert result.status == "GAP"


# ---------------------------------------------------------------------------
# Claim drift case 4: SOTA claim contradicts metric direction -> ANOMALY
# ---------------------------------------------------------------------------


def test_sota_claim_metric_lower_than_baseline_is_anomaly():
    from spar_domain_ml.layer_a import check_a1_sota

    subject = _base_subject(metric_value=0.890, baseline_value=0.905)
    result = check_a1_sota(subject)
    assert result.status == "ANOMALY"


def test_sota_claim_lower_is_better_direction():
    from spar_domain_ml.layer_a import check_a1_sota

    subject = _base_subject(
        metric_name="error_rate",
        metric_value=0.05,
        metric_direction="lower_is_better",
        baseline_value=0.08,
    )
    result = check_a1_sota(subject)
    assert result.status == "CONSISTENT"


# ---------------------------------------------------------------------------
# Claim drift case 5: report text exceeds claim profile -> Layer B WARN
# ---------------------------------------------------------------------------


def test_sota_language_without_profile_claim_warns():
    from spar_domain_ml.layer_b import check_b1_sota_language

    subject = _base_subject(
        claim_profile={"sota_claimed": False, "generalization_claimed": False, "robustness_claimed": False}
    )
    result = check_b1_sota_language(subject, "We achieve state-of-the-art performance on ImageNet.")
    assert result.status == "WARN"


def test_sota_language_matching_profile_passes():
    from spar_domain_ml.layer_b import check_b1_sota_language

    subject = _base_subject()
    result = check_b1_sota_language(subject, "We achieve state-of-the-art top-1 accuracy.")
    assert result.status == "PASS"


# ---------------------------------------------------------------------------
# Layer C: reproducibility maturity thresholds
# ---------------------------------------------------------------------------


def test_reproducibility_3_of_3_is_genuine():
    from spar_domain_ml.layer_c import check_c1_reproducibility

    subject = _base_subject(reproducibility={
        "seed_present": True, "dataset_version_present": True, "config_hash_present": True
    })
    assert check_c1_reproducibility(subject).status == "GENUINE"


def test_reproducibility_2_of_3_is_approximation():
    from spar_domain_ml.layer_c import check_c1_reproducibility

    subject = _base_subject(reproducibility={
        "seed_present": True, "dataset_version_present": True, "config_hash_present": False
    })
    assert check_c1_reproducibility(subject).status == "APPROXIMATION"


def test_reproducibility_1_of_3_is_gap():
    from spar_domain_ml.layer_c import check_c1_reproducibility

    subject = _base_subject(reproducibility={
        "seed_present": True, "dataset_version_present": False, "config_hash_present": False
    })
    assert check_c1_reproducibility(subject).status == "GAP"


# ---------------------------------------------------------------------------
# Registry
# ---------------------------------------------------------------------------


def test_ml_registry_snapshot_counts_models():
    from spar_domain_ml.registry_seed import ml_model_registry_snapshot

    snapshot = ml_model_registry_snapshot()
    assert snapshot["total_models"] == 3
    model_ids = {m["model_id"] for m in snapshot["models"]}
    assert "benchmark_sota_checker" in model_ids
    assert "reproducibility_probe" in model_ids
    assert "claim_scope_validator" in model_ids


def test_ml_gap_registry_snapshot_counts_states():
    from spar_domain_ml.registry_seed import ml_gap_registry_snapshot

    snapshot = ml_gap_registry_snapshot()
    assert snapshot["total_gaps"] == 3
    states = {g["state"] for g in snapshot["gaps"]}
    assert "open" in states
    assert "partial" in states


# ---------------------------------------------------------------------------
# Policy loader
# ---------------------------------------------------------------------------


def test_ml_layer_c_thresholds_from_policy():
    from spar_domain_ml.policy_loader import get_layer_c_thresholds

    t = get_layer_c_thresholds()
    assert t["genuine_threshold"] == 3
    assert t["approximation_threshold"] == 2
    assert "seed_present" in t["reproducibility_fields"]
