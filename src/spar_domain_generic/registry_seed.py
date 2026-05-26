"""Generic adapter model and gap registry seed data."""

from __future__ import annotations

from spar_framework.registry import (
    GapSpec,
    ModelSpec,
    gap_registry_snapshot,
    model_registry_snapshot,
)

GENERIC_MODELS: list[ModelSpec] = [
    ModelSpec(
        model_id="claim_anchor_checker",
        name="Claim Anchor Checker",
        maturity="Production",
        scope_note="Deterministic claim-vs-evidence anchor matching for generic subjects.",
        module_path="spar_domain_generic/layer_a.py",
        group="core_generic_checks",
    ),
    ModelSpec(
        model_id="scope_bounding_probe",
        name="Scope Bounding Probe",
        maturity="Production",
        scope_note="Checks whether a claim declares its scope of applicability.",
        module_path="spar_domain_generic/layer_a.py",
        group="core_generic_checks",
    ),
    ModelSpec(
        model_id="evidence_surface_probe",
        name="Evidence Surface Probe",
        maturity="Production",
        scope_note="Reports whether claim-supporting evidence is present.",
        module_path="spar_domain_generic/layer_c.py",
        group="core_generic_checks",
    ),
]

GENERIC_GAPS: list[GapSpec] = [
    GapSpec(
        "GA1", "Domain-specific evidence verification", "open",
        "Generic adapter does not verify domain-specific evidence types.",
        ("claim_anchor_checker",),
    ),
    GapSpec(
        "GA2", "Cross-domain claim transfer", "open",
        "Generic adapter does not analyse cross-domain claims.",
        ("scope_bounding_probe",),
    ),
    GapSpec(
        "GA3", "Quantitative metric validation", "open",
        "Numeric thresholds and metric comparisons are out of scope.",
        ("evidence_surface_probe",),
    ),
]


def generic_model_registry_snapshot() -> dict[str, object]:
    return model_registry_snapshot(GENERIC_MODELS)


def generic_gap_registry_snapshot() -> dict[str, object]:
    return gap_registry_snapshot(GENERIC_GAPS)
