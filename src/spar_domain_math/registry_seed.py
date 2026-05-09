"""Math adapter model and gap registry seed data."""

from __future__ import annotations

from spar_framework.registry import GapSpec, ModelSpec, build_registry_snapshots, gap_registry_snapshot, model_registry_snapshot

MATH_MODELS: list[ModelSpec] = [
    ModelSpec(
        model_id="proof_anchor_checker",
        name="Proof Anchor Checker",
        maturity="Production",
        scope_note="Deterministic claim-anchor matching for proof claims vs proof evidence surface.",
        module_path="spar_domain_math/layer_a.py",
        group="core_math_checks",
    ),
    ModelSpec(
        model_id="generality_scope_validator",
        name="Generality Scope Validator",
        maturity="Production",
        scope_note="Generality claim scope vs assumption explicitness contract.",
        module_path="spar_domain_math/layer_a.py",
        group="core_math_checks",
    ),
    ModelSpec(
        model_id="statement_boundary_probe",
        name="Statement Boundary Probe",
        maturity="Production",
        scope_note="Proof maturity and assumption boundary clarity surface checks.",
        module_path="spar_domain_math/layer_c.py",
        group="core_math_checks",
    ),
]

MATH_GAPS: list[GapSpec] = [
    GapSpec("MA1", "Formal verification coverage", "open",
            "Machine-checked proofs (Coq, Lean, Isabelle) are not reviewed in v0.4.x.",
            ("proof_anchor_checker",)),
    GapSpec("MA2", "Cross-domain claim transfer", "open",
            "Claims whose scope crosses mathematical domains are not tracked.",
            ("generality_scope_validator",)),
    GapSpec("MA3", "Conjecture status tracking", "partial",
            "Conjecture type triggers A1 ANOMALY; ongoing conjecture resolution tracking not covered.",
            ("proof_anchor_checker",)),
]

_MATH_GAP_BY_ID = {gap.check_id: gap for gap in MATH_GAPS}


def math_model_registry_snapshot() -> dict[str, object]:
    return model_registry_snapshot(MATH_MODELS)


def math_gap_registry_snapshot() -> dict[str, object]:
    return gap_registry_snapshot(MATH_GAPS)


def math_registry_snapshots() -> dict[str, object]:
    return build_registry_snapshots(models=MATH_MODELS, gaps=MATH_GAPS)
