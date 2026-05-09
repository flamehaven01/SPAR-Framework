"""Static architecture gap descriptions for the ML adapter."""

ML_ARCHITECTURE_GAPS: dict[str, str] = {
    "M1": "Extended claim classes (fairness, calibration, efficiency, safety) are not reviewed in v0.3.0.",
    "M2": "Temporal model performance drift is outside the current review surface.",
    "M3": "Cross-task generalization is not measured; only OOD flag is checked.",
}
