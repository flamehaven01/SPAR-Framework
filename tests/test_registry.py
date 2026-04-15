import json
from pathlib import Path

from spar_framework import __version__
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


def test_run_review_emits_safe_context_summary():
    from spar_framework.engine import ReviewRuntime, run_review
    from spar_framework.result_types import CheckResult

    runtime = ReviewRuntime(
        build_layer_a=lambda **_: [CheckResult("A1", "anchor", "PASS", "ok")],
        build_layer_b=lambda **_: [CheckResult("B1", "scope", "PASS", "ok")],
        build_layer_c=lambda **_: [CheckResult("C1", "maturity", "PASS", "ok")],
    )

    result = run_review(
        runtime=runtime,
        subject="demo",
        memory_context={"project_name": "mica-demo", "mode": "memory_injection"},
        leda_injection={
            "source": {"analyzer": "LEDA", "generated_at": "2026-04-12T00:00:00Z"},
            "security": {"classification": "restricted"},
            "claim_risk": [{"id": "registry_drift", "severity": "high"}],
            "maturity": {"suggested_current": "partial"},
            "spar_review_hints": {"preferred_layers": ["Layer C"]},
        },
    )

    payload = result.to_dict()
    assert payload["context_summary"]["sources"] == ["mica", "leda"]
    assert payload["context_summary"]["leda"]["claim_risk_count"] == 1
    assert payload["context_summary"]["leda"]["suggested_maturity"] == "partial"


def test_run_contextual_review_loads_redacted_leda(tmp_path):
    import yaml

    from spar_domain_physics.runtime import get_review_runtime
    from spar_framework.workflow import run_contextual_review

    mica_path = tmp_path / "mica.yaml"
    mica_path.write_text("project_name: demo\nmode: memory_injection\n", encoding="utf-8")
    leda_path = tmp_path / "leda.yaml"
    leda_path.write_text(
        yaml.safe_dump(
            {
                "project": {"name": "demo", "root": "/secret/root"},
                "source": {
                    "analyzer": "LEDA",
                    "generated_at": "2026-04-12T00:00:00Z",
                    "config_path": "/secret/config",
                    "history_db": "/secret/history.db",
                },
                "security": {"classification": "internal"},
                "claim_risk": [
                    {
                        "id": "registry_drift",
                        "severity": "high",
                        "layer_hint": "Layer C",
                        "evidence": ["secret"],
                    }
                ],
                "maturity": {"suggested_current": "partial"},
                "spar_review_hints": {"preferred_layers": ["Layer C"]},
                "overrides": {"configured_override_count": 1},
            },
            sort_keys=False,
        ),
        encoding="utf-8",
    )

    result = run_contextual_review(
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
        mica_context_path=str(mica_path),
        leda_injection_path=str(leda_path),
    )

    payload = result.to_dict()
    assert payload["context_summary"]["mica"]["state"] == "INVOCATION_MODE"
    assert payload["context_summary"]["mica"]["mode"] == "memory_injection"
    assert payload["context_summary"]["leda"]["classification"] == "restricted"
    assert payload["context_summary"]["leda"]["claim_risk_count"] == 1
    assert "claim_risk_ids" not in payload["context_summary"]["leda"]


def test_discover_mica_runtime_invocation_mode(tmp_path):
    from spar_framework.mica import discover_mica_runtime, load_mica_runtime_context

    (tmp_path / "memory").mkdir()
    (tmp_path / "mica.yaml").write_text(
        "\n".join(
            [
                "mica_spec: \"0.2.2\"",
                "name: demo-project",
                "mode: memory_injection",
                "layers:",
                "  - name: archive",
                "    path: memory/demo.mica.v1.0.0.json",
                "invocation_protocol:",
                "  primary_pattern: hook_trigger",
            ]
        ),
        encoding="utf-8",
    )
    (tmp_path / "memory" / "demo.mica.v1.0.0.json").write_text(
        json.dumps(
            {
                "project": {"name": "demo-project"},
                "design_invariants": [
                    {"id": "DI-001", "severity": "critical"},
                    {"id": "DI-002", "severity": "high"},
                ],
                "operation_meta": {
                    "archive_id": "MICA-DEMO-001",
                    "last_updated": "2026-04-12",
                    "current_state": "active",
                },
            }
        ),
        encoding="utf-8",
    )

    discovery = discover_mica_runtime(tmp_path)
    context = load_mica_runtime_context(project_root=tmp_path)

    assert discovery["state"] == "INVOCATION_MODE"
    assert context is not None
    assert context["_mica_runtime"]["state"] == "INVOCATION_MODE"
    assert context["invariants"]["critical"] == 1
    assert context["pattern"] == "hook_trigger"


def test_discover_mica_runtime_legacy_mode(tmp_path):
    from spar_framework.mica import discover_mica_runtime, load_mica_runtime_context

    (tmp_path / "memory").mkdir()
    (tmp_path / "memory" / "legacy.mica.v1.0.0.json").write_text(
        json.dumps(
            {
                "mica_spec": "0.2.2",
                "project": {"name": "legacy-demo"},
                "design_invariants": [{"id": "DI-001", "severity": "critical"}],
                "operation_meta": {
                    "archive_id": "MICA-LEGACY-001",
                    "last_updated": "2026-04-11",
                    "current_state": "active",
                    "operating_mode": "protocol_evolution",
                },
            }
        ),
        encoding="utf-8",
    )

    discovery = discover_mica_runtime(tmp_path)
    context = load_mica_runtime_context(project_root=tmp_path)

    assert discovery["state"] == "LEGACY_MODE"
    assert context is not None
    assert context["_mica_runtime"]["state"] == "LEGACY_MODE"
    assert context["archive_id"] == "MICA-LEGACY-001"


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


def test_planck_mass_constant_is_single_source():
    from spar_domain_physics.ground_truth import PLANCK_MASS_GEV as truth_planck
    from spar_domain_physics.layer_a_runtime_checks import PLANCK_MASS_GEV as layer_a_planck

    assert layer_a_planck == truth_planck


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


def test_matcher_does_not_misclassify_ads_dilaton_as_linear_dilaton():
    from spar_domain_physics.matcher import match_ground_truth_source

    assert match_ground_truth_source("ads dilaton") == "ads"


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
    assert checks[3].status == "CANNOT_CHECK"
    assert checks[4].status == "CANNOT_CHECK"


def test_physics_layer_b_reads_leda_claim_surface():
    from spar_domain_physics.layer_b import build_layer_b

    checks = build_layer_b(
        subject={
            "eft_m_kk_gev": 1.0e16,
            "ricci_norm": 0.02,
        },
        source="ads",
        gate="PASS",
        report_text="Tight bounded statement.",
        context={
            "leda_injection": {
                "claim_risk": [{"id": "registry_drift"}],
                "maturity": {"suggested_current": "partial"},
                "spar_review_hints": {"preferred_layers": ["Layer C"]},
            }
        },
    )

    assert checks[3].status == "WARN"
    assert checks[4].status == "CANNOT_CHECK"


def test_physics_layer_b_reads_mica_runtime_state():
    from spar_domain_physics.layer_b import build_layer_b

    checks = build_layer_b(
        subject={
            "eft_m_kk_gev": 1.0e16,
            "ricci_norm": 0.02,
        },
        source="ads",
        gate="PASS",
        report_text="Tight bounded statement.",
        context={
            "memory_context": {
                "archive_id": "MICA-DEMO-001",
                "invariants": {"critical": 2, "high": 1},
                "_mica_runtime": {"state": "INVOCATION_MODE"},
            }
        },
    )

    assert checks[4].status == "PASS"


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
    c9 = next(check for check in checks if check.check_id == "C9")
    assert c9.status == "CANNOT_CHECK"
    c10 = next(check for check in checks if check.check_id == "C10")
    assert c10.status == "CANNOT_CHECK"


def test_physics_layer_c_reads_leda_maturity_alignment():
    from spar_domain_physics.layer_c import build_layer_c

    checks = build_layer_c(
        subject={},
        source="wzw background",
        gate="PASS",
        params={},
        context={
            "leda_injection": {
                "security": {"classification": "restricted"},
                "maturity": {"suggested_current": "partial", "confidence": 0.77},
            }
        },
    )

    c9 = next(check for check in checks if check.check_id == "C9")
    assert c9.status == "APPROXIMATION"
    c10 = next(check for check in checks if check.check_id == "C10")
    assert c10.status == "CANNOT_CHECK"


def test_physics_layer_c_reads_mica_invariant_continuity():
    from spar_domain_physics.layer_c import build_layer_c

    checks = build_layer_c(
        subject={},
        source="wzw background",
        gate="PASS",
        params={},
        context={
            "memory_context": {
                "pct_status": "active",
                "invariants": {"critical": 2, "high": 1},
                "_mica_runtime": {"state": "INVOCATION_MODE"},
            }
        },
    )

    c10 = next(check for check in checks if check.check_id == "C10")
    assert c10.status == "GENUINE"


def test_physics_layer_c_marks_legacy_mica_as_approximation():
    from spar_domain_physics.layer_c import build_layer_c

    checks = build_layer_c(
        subject={},
        source="wzw background",
        gate="PASS",
        params={},
        context={
            "memory_context": {
                "pct_status": "active",
                "invariants": {"critical": 1, "high": 0},
                "_mica_runtime": {"state": "LEGACY_MODE"},
            }
        },
    )

    c10 = next(check for check in checks if check.check_id == "C10")
    assert c10.status == "APPROXIMATION"


def test_public_leda_payload_is_not_ingested_by_physics_layers():
    from spar_domain_physics.layer_b import build_layer_b
    from spar_domain_physics.layer_c import build_layer_c

    b_checks = build_layer_b(
        subject={
            "eft_m_kk_gev": 1.0e16,
            "ricci_norm": 0.02,
        },
        source="ads",
        gate="PASS",
        report_text="Tight bounded statement.",
        context={
            "leda_injection": {
                "security": {"classification": "public", "ingestible_by_spar": False},
                "claim_risk": [{"id": "registry_drift"}],
                "maturity": {"suggested_current": "partial", "confidence": 0.77},
            }
        },
    )
    c_checks = build_layer_c(
        subject={},
        source="wzw background",
        gate="PASS",
        params={},
        context={
            "leda_injection": {
                "security": {"classification": "public", "ingestible_by_spar": False},
                "claim_risk": [{"id": "registry_drift"}],
                "maturity": {"suggested_current": "partial", "confidence": 0.77},
            }
        },
    )

    assert b_checks[3].status == "CANNOT_CHECK"
    c9 = next(check for check in c_checks if check.check_id == "C9")
    assert c9.status == "CANNOT_CHECK"


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


def test_spar_context_review_cli_writes_json(tmp_path):
    import yaml

    from spar_framework.cli import main

    subject_path = tmp_path / "subject.json"
    subject_path.write_text(
        json.dumps(
            {
                "beta_G_norm": 0.0,
                "beta_B_norm": 0.0,
                "beta_Phi_norm": 0.0,
                "sidrce_omega": 1.0,
                "eft_m_kk_gev": 1.0e16,
                "ricci_norm": 0.02,
            }
        ),
        encoding="utf-8",
    )
    mica_path = tmp_path / "mica.yaml"
    mica_path.write_text("project_name: demo\nmode: memory_injection\n", encoding="utf-8")
    leda_path = tmp_path / "leda.yaml"
    leda_path.write_text(
        yaml.safe_dump(
            {
                "source": {"analyzer": "LEDA", "generated_at": "2026-04-12T00:00:00Z"},
                "security": {"classification": "restricted"},
                "claim_risk": [{"id": "registry_drift", "severity": "high"}],
                "maturity": {"suggested_current": "partial"},
                "spar_review_hints": {"preferred_layers": ["Layer C"]},
            },
            sort_keys=False,
        ),
        encoding="utf-8",
    )
    output_path = tmp_path / "review.json"

    import sys
    from unittest.mock import patch

    with patch.object(
        sys,
        "argv",
        [
            "spar-context-review",
            "--subject-json",
            str(subject_path),
            "--source",
            "flat minkowski",
            "--gate",
            "PASS",
            "--mica-context",
            str(mica_path),
            "--leda-injection",
            str(leda_path),
            "--output-json",
            str(output_path),
        ],
    ):
        rc = main()

    assert rc == 0
    payload = json.loads(output_path.read_text(encoding="utf-8"))
    assert payload["context_summary"]["sources"] == ["mica", "leda"]
    assert any(check["check_id"] == "C9" for check in payload["layer_c"])


def test_spar_context_review_cli_can_auto_discover_mica(tmp_path):
    import yaml

    from spar_framework.cli import main

    (tmp_path / "memory").mkdir()
    subject_path = tmp_path / "subject.json"
    subject_path.write_text(
        json.dumps(
            {
                "beta_G_norm": 0.0,
                "beta_B_norm": 0.0,
                "beta_Phi_norm": 0.0,
                "sidrce_omega": 1.0,
                "eft_m_kk_gev": 1.0e16,
                "ricci_norm": 0.02,
            }
        ),
        encoding="utf-8",
    )
    (tmp_path / "mica.yaml").write_text(
        "\n".join(
            [
                "mica_spec: \"0.2.2\"",
                "name: demo-project",
                "mode: memory_injection",
                "layers:",
                "  - name: archive",
                "    path: memory/demo.mica.v1.0.0.json",
                "invocation_protocol:",
                "  primary_pattern: readme_protocol",
            ]
        ),
        encoding="utf-8",
    )
    (tmp_path / "memory" / "demo.mica.v1.0.0.json").write_text(
        json.dumps(
            {
                "project": {"name": "demo-project"},
                "design_invariants": [{"id": "DI-001", "severity": "critical"}],
                "operation_meta": {
                    "archive_id": "MICA-DEMO-CLI-001",
                    "last_updated": "2026-04-12",
                    "current_state": "active",
                },
            }
        ),
        encoding="utf-8",
    )
    leda_path = tmp_path / "leda.yaml"
    leda_path.write_text(
        yaml.safe_dump(
            {
                "source": {"analyzer": "LEDA", "generated_at": "2026-04-12T00:00:00Z"},
                "security": {"classification": "restricted", "ingestible_by_spar": True},
                "claim_risk": [{"id": "registry_drift", "severity": "high"}],
                "maturity": {"suggested_current": "partial"},
                "spar_review_hints": {"preferred_layers": ["Layer C"]},
            },
            sort_keys=False,
        ),
        encoding="utf-8",
    )
    output_path = tmp_path / "review.json"

    import sys
    from unittest.mock import patch

    with patch.object(
        sys,
        "argv",
        [
            "spar-context-review",
            "--subject-json",
            str(subject_path),
            "--source",
            "flat minkowski",
            "--gate",
            "PASS",
            "--project-root",
            str(tmp_path),
            "--leda-injection",
            str(leda_path),
            "--output-json",
            str(output_path),
        ],
    ):
        rc = main()

    assert rc == 0
    payload = json.loads(output_path.read_text(encoding="utf-8"))
    assert payload["context_summary"]["mica"]["state"] == "INVOCATION_MODE"
    assert payload["context_summary"]["mica"]["archive_id"] == "MICA-DEMO-CLI-001"


def test_spar_review_subcommand_writes_json(tmp_path):
    from spar_framework.cli import main

    subject_path = tmp_path / "subject.json"
    subject_path.write_text(
        json.dumps(
            {
                "beta_G_norm": 0.0,
                "beta_B_norm": 0.0,
                "beta_Phi_norm": 0.0,
                "sidrce_omega": 1.0,
                "eft_m_kk_gev": 1.0e16,
                "ricci_norm": 0.02,
            }
        ),
        encoding="utf-8",
    )
    output_path = tmp_path / "review.json"

    rc = main(
        [
            "review",
            "--subject-json",
            str(subject_path),
            "--source",
            "flat minkowski",
            "--gate",
            "PASS",
            "--output-json",
            str(output_path),
        ]
    )

    assert rc == 0
    payload = json.loads(output_path.read_text(encoding="utf-8"))
    assert payload["verdict"] == "MINOR_REVISION"
    assert payload["score"] >= 70
    assert payload["context_summary"] is None


def test_spar_explain_subcommand_emits_summary(tmp_path, capsys):
    from spar_framework.cli import main

    review_path = tmp_path / "review.json"
    review_path.write_text(
        json.dumps(
            {
                "verdict": "MINOR_REVISION",
                "score": 78,
                "grade": "WARN",
                "context_summary": {"sources": ["mica"]},
                "layer_a": [{"check_id": "A1", "status": "PASS"}],
                "layer_b": [{"check_id": "B5", "status": "WARN"}],
                "layer_c": [{"check_id": "C10", "status": "APPROXIMATION"}],
            }
        ),
        encoding="utf-8",
    )

    rc = main(["explain", "--review-json", str(review_path), "--format", "text"])

    assert rc == 0
    out = capsys.readouterr().out
    assert "verdict: MINOR_REVISION" in out
    assert "layer_b_flags: B5" in out
    assert "context_sources: mica" in out


def test_spar_discover_subcommand_reports_profiles(tmp_path, capsys):
    from spar_framework.cli import main

    rc = main(["discover", "--project-root", str(tmp_path), "--adapter", "physics"])

    assert rc == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["adapter"] == "physics"
    assert payload["mica"]["state"] == "INACTIVE"
    assert payload["leda"]["recommended_profile"] == "restricted"


def test_spar_schema_subcommand_emits_subject_contract(capsys):
    from spar_framework.cli import main

    rc = main(["schema", "subject"])

    assert rc == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["title"] == "SPAR Physics Subject"
    assert "beta_G_norm" in payload["properties"]


def test_spar_schema_subcommand_writes_schema_file(tmp_path):
    from spar_framework.cli import main

    output_path = tmp_path / "subject-schema.json"

    rc = main(["schema", "subject", "--output-json", str(output_path)])

    assert rc == 0
    payload = json.loads(output_path.read_text(encoding="utf-8"))
    assert payload["title"] == "SPAR Physics Subject"


def test_spar_example_subcommand_writes_example(tmp_path):
    from spar_framework.cli import main

    output_path = tmp_path / "example.json"

    rc = main(["example", "--source", "flat", "--output-json", str(output_path)])

    assert rc == 0
    payload = json.loads(output_path.read_text(encoding="utf-8"))
    assert payload["source"] == "flat"
    assert payload["subject"]["beta_G_norm"] == 0.0


def test_spar_unknown_subcommand_returns_structured_error(capsys):
    from spar_framework.cli import EXIT_INPUT_ERROR, main

    rc = main(["frobnicate"])

    assert rc == EXIT_INPUT_ERROR
    payload = json.loads(capsys.readouterr().out)
    assert payload["error"] == "unknown_command"
    assert "frobnicate" in payload["detail"]


def test_load_schema_reads_packaged_artifact():
    from spar_framework.schema_loader import load_schema

    subject_schema = load_schema("subject")
    result_schema = load_schema("result")
    context_schema = load_schema("context")

    assert subject_schema["title"] == "SPAR Physics Subject"
    assert result_schema["title"] == "SPAR Review Result"
    assert context_schema["title"] == "SPAR Context Contracts"


def test_mica_archive_version_tracks_package_version():
    archive = json.loads(
        Path("memory/spar-framework.mica.v1.0.0.json").read_text(encoding="utf-8")
    )

    assert archive["project"]["version"] == __version__
    assert archive["operation_meta"]["baseline_ref"].startswith(f"v{__version__}-")
