"""ML adapter model and gap registry seed data."""

from __future__ import annotations

from spar_framework.registry import GapSpec, ModelSpec, build_registry_snapshots, gap_registry_snapshot, model_registry_snapshot

ML_MODELS: list[ModelSpec] = [
    ModelSpec(
        model_id="benchmark_sota_checker",
        name="Benchmark SOTA Checker",
        maturity="Production",
        scope_note="Deterministic claim-anchor matching for SOTA claims on standard benchmarks.",
        module_path="spar_domain_ml/layer_a.py",
        group="core_ml_checks",
    ),
    ModelSpec(
        model_id="reproducibility_probe",
        name="Reproducibility Maturity Probe",
        maturity="Production",
        scope_note="Evidence surface completeness check against reproducibility field contract.",
        module_path="spar_domain_ml/layer_c.py",
        group="core_ml_checks",
    ),
    ModelSpec(
        model_id="claim_scope_validator",
        name="Claim Scope Validator",
        maturity="Production",
        scope_note="Generalization and robustness claim scope vs evaluation surface contract.",
        module_path="spar_domain_ml/layer_a.py",
        group="core_ml_checks",
    ),
]

ML_GAPS: list[GapSpec] = [
    GapSpec("M1", "Extended claim class coverage", "open",
            "Fairness, calibration, efficiency, safety claims not reviewed in v0.3.0.",
            ("claim_scope_validator",)),
    GapSpec("M2", "Temporal model drift", "open",
            "Model performance drift over time outside current review surface.",
            ("benchmark_sota_checker",)),
    GapSpec("M3", "Cross-task generalization", "partial",
            "Generalization check covers OOD flag only; cross-task scope not measured.",
            ("claim_scope_validator",)),
]

_ML_GAP_BY_ID = {gap.check_id: gap for gap in ML_GAPS}


def ml_model_registry_snapshot() -> dict[str, object]:
    return model_registry_snapshot(ML_MODELS)


def ml_gap_registry_snapshot() -> dict[str, object]:
    return gap_registry_snapshot(ML_GAPS)


def ml_registry_snapshots() -> dict[str, object]:
    return build_registry_snapshots(models=ML_MODELS, gaps=ML_GAPS)
