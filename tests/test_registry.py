from spar_framework.registry import GapSpec, ModelSpec, gap_registry_snapshot, model_registry_snapshot


def test_model_registry_snapshot_counts_models():
    snapshot = model_registry_snapshot(
        [ModelSpec("m1", "Model 1", "Production", "Test scope")]
    )
    assert snapshot["total_models"] == 1


def test_gap_registry_snapshot_counts_states():
    snapshot = gap_registry_snapshot(
        [GapSpec("C1", "Gap 1", "partial", "Test", ("m1",))]
    )
    assert snapshot["state_counts"]["partial"] == 1


def test_run_review_emits_registry_snapshots():
    from spar_framework.engine import ReviewRuntime, run_review
    from spar_framework.result_types import CheckResult

    runtime = ReviewRuntime(
        build_layer_a=lambda **_: [CheckResult("A1", "anchor", "PASS", "ok")],
        build_layer_b=lambda **_: [CheckResult("B1", "scope", "PASS", "ok")],
        build_layer_c=lambda **_: [CheckResult("C1", "maturity", "GAP", "stale")],
        build_model_registry_snapshot=lambda: {"total_models": 1},
        build_gap_registry_snapshot=lambda: {"total_gaps": 1},
        slop_check=lambda report_text: (0, []),
    )

    result = run_review(runtime=runtime, subject="demo", source="unit", gate="PASS", report_text="ok")
    payload = result.to_dict()

    assert payload["score"] == 95
    assert payload["verdict"] == "ACCEPT"
    assert payload["model_registry_snapshot"]["total_models"] == 1
    assert payload["gap_registry_snapshot"]["total_gaps"] == 1


def test_physics_adapter_seed_emits_grouped_registry():
    from spar_domain_physics.registry_seed import physics_model_registry_snapshot

    snapshot = physics_model_registry_snapshot()

    assert snapshot["total_models"] >= 1
    assert "core_physics_models" in snapshot["groups"]


def test_physics_adapter_seed_exposes_gap_states():
    from spar_domain_physics.registry_seed import physics_gap_registry_snapshot

    snapshot = physics_gap_registry_snapshot()

    assert snapshot["total_gaps"] >= 1
    assert "partial" in snapshot["state_counts"]


def test_physics_layer_a_matches_flat_ground_truth():
    from spar_domain_physics.layer_a import build_layer_a

    checks = build_layer_a(
        subject={
            "beta_G_norm": 0.0,
            "beta_B_norm": 0.0,
            "beta_Phi_norm": 0.0,
            "sidrce_omega": 1.0,
            "eft_m_kk_gev": 1.0e16,
        },
        source="flat minkowski",
        gate="PASS",
        params={},
    )

    assert checks[0].status == "CONSISTENT"
    assert checks[3].status == "CONSISTENT"


def test_physics_layer_a_flags_gate_mismatch():
    from spar_domain_physics.layer_a import build_layer_a

    checks = build_layer_a(
        subject={
            "beta_G_norm": 0.0,
            "sidrce_omega": 0.2,
        },
        source="de_sitter",
        gate="PASS",
        params={},
    )

    assert checks[3].status == "ANOMALY"


def test_physics_layer_b_flags_eft_scope_failure():
    from spar_domain_physics.layer_b import build_layer_b

    checks = build_layer_b(
        subject={
            "eft_m_kk_gev": 2.0e19,
            "ricci_norm": 0.001,
        },
        source="flat minkowski",
        gate="PASS",
        report_text="Tight bounded statement.",
    )

    assert checks[0].status == "FAIL"
    assert checks[1].status == "PASS"


def test_physics_layer_b_warns_on_slop_phrase():
    from spar_domain_physics.layer_b import build_layer_b

    checks = build_layer_b(
        subject={
            "eft_m_kk_gev": 1.0e16,
            "ricci_norm": 0.02,
        },
        source="ads",
        gate="PASS",
        report_text="This is a groundbreaking result that opens up new possibilities.",
    )

    assert checks[1].status == "WARN"
    assert checks[2].status == "WARN"


def test_physics_runtime_emits_slop_hits_and_registry_snapshots():
    from spar_domain_physics.runtime import get_review_runtime
    from spar_framework.engine import run_review

    result = run_review(
        runtime=get_review_runtime(),
        subject={
            "beta_G_norm": 0.0,
            "beta_B_norm": 0.0,
            "beta_Phi_norm": 0.0,
            "sidrce_omega": 1.0,
            "eft_m_kk_gev": 1.0e16,
            "ricci_norm": 0.02,
        },
        source="flat minkowski",
        gate="PASS",
        report_text="A groundbreaking result.",
    )

    payload = result.to_dict()

    assert payload["model_registry_snapshot"]["total_models"] >= 1
    assert payload["gap_registry_snapshot"]["total_gaps"] >= 1
    assert "groundbreaking" in payload["slop_hits"]


def test_physics_layer_c_marks_closed_gap_as_genuine():
    from spar_domain_physics.layer_c import build_layer_c

    checks = build_layer_c(
        subject={
            "sidrce_omega": 0.7,
            "ricci_norm": 0.001,
            "partial_G": {"dummy": 1},
            "F2": {"dummy": 1},
        },
        source="flat minkowski",
        gate="PASS",
        params={},
    )

    c7 = next(check for check in checks if check.check_id == "C7")
    assert c7.status == "GENUINE"


def test_physics_layer_c_flags_missing_omega_as_cannot_determine():
    from spar_domain_physics.layer_c import build_layer_c

    checks = build_layer_c(
        subject={},
        source="wzw background",
        gate="PASS",
        params={},
    )

    c4 = next(check for check in checks if check.check_id == "C4")
    assert c4.status == "CANNOT_DETERMINE"


def test_physics_runtime_layer_c_affects_score():
    from spar_domain_physics.runtime import get_review_runtime
    from spar_framework.engine import run_review

    result = run_review(
        runtime=get_review_runtime(),
        subject={
            "beta_G_norm": 0.0,
            "beta_B_norm": 0.0,
            "beta_Phi_norm": 0.0,
            "sidrce_omega": 0.9,
            "eft_m_kk_gev": 1.0e16,
            "ricci_norm": 0.02,
        },
        source="flat minkowski",
        gate="PASS",
        report_text="Clean report.",
    )

    payload = result.to_dict()

    assert payload["score"] < 100
    assert any(check["check_id"] == "C4" for check in payload["layer_c"])
