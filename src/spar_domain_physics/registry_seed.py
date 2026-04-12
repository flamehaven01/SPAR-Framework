"""Physics-domain seed data for the standalone SPAR framework."""

from __future__ import annotations

from spar_framework.registry import GapSpec, ModelSpec, build_registry_snapshots, gap_registry_snapshot, model_registry_snapshot

PHYSICS_MODELS: list[ModelSpec] = [
    ModelSpec(
        model_id="beta_residual",
        name="Beta-function residual",
        maturity="Production",
        scope_note="Full beta^G, beta^B, beta^Phi path on the supported physics surface.",
        module_path="physics/beta_residual.py",
        group="core_physics_models",
    ),
    ModelSpec(
        model_id="chi_squared_omega",
        name="Chi-squared omega",
        maturity="Production",
        scope_note="Gaussian residual scoring with inverse interpretation.",
        module_path="governance/orchestrator.py",
        group="core_physics_models",
    ),
    ModelSpec(
        model_id="qgb",
        name="Quantum Geometry Bridge",
        maturity="Production (heuristic)",
        scope_note="Curvature-to-decoherence map with calibration-backed coupling.",
        module_path="physics/qgb.py",
        group="extended_physics_models",
    ),
    ModelSpec(
        model_id="rg_flow_linearized",
        name="RG flow (linearized)",
        maturity="Production (linearized)",
        scope_note="Dilaton-only path; full metric evolution is separate.",
        module_path="analysis/rg_flow.py",
        group="extended_physics_models",
    ),
]

PHYSICS_GAPS: list[GapSpec] = [
    GapSpec("C1", "beta^B genuineness", "partial", "beta^B coverage is still partial on the full formula surface.", ("beta_residual",)),
    GapSpec("C2", "BRST genuineness", "partial", "Central-charge corrections remain regime-dependent.", ("beta_residual",)),
    GapSpec("C3", "GS anomaly completeness", "partial", "GS completeness depends on available curvature and gauge inputs.", ("beta_residual",)),
    GapSpec("C4", "SIDRCE omega derivation", "open", "Tolerance magnitudes remain calibrated rather than derived.", ("chi_squared_omega",)),
    GapSpec("C5", "Independent verification coverage", "partial", "Symbolic and cross-validation coverage remains partial.", ("beta_residual",)),
    GapSpec("C6", "QGB alpha provenance", "partial", "QGB coupling magnitude remains calibration-backed.", ("qgb",)),
    GapSpec("C7", "T-duality phi-gradient preservation", "closed", "Supported T-duality path is closed in current physics adapter framing.", ("beta_residual",)),
    GapSpec("C8", "RG flow metric evolution", "partial", "Reduced Ricci-flow exists, but linearized RG remains approximate.", ("rg_flow_linearized",)),
]

_PHYSICS_GAP_BY_ID = {gap.check_id: gap for gap in PHYSICS_GAPS}


def physics_model_registry_snapshot() -> dict[str, object]:
    return model_registry_snapshot(PHYSICS_MODELS)


def physics_gap_registry_snapshot() -> dict[str, object]:
    return gap_registry_snapshot(PHYSICS_GAPS)


def physics_registry_snapshots() -> dict[str, object]:
    return build_registry_snapshots(models=PHYSICS_MODELS, gaps=PHYSICS_GAPS)


def get_physics_gap(check_id: str) -> GapSpec | None:
    return _PHYSICS_GAP_BY_ID.get(check_id)


def format_gap_state(check_id: str) -> str:
    gap = get_physics_gap(check_id)
    if gap is None:
        return "state=unknown"
    models = ", ".join(gap.related_models)
    return f"state={gap.state}; related_models={models}"
