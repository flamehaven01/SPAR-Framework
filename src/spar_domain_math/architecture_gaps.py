"""Static architecture gap descriptions for the math adapter."""

MATH_ARCHITECTURE_GAPS: dict[str, str] = {
    "MA1": "Machine-checked formal verification (Coq, Lean, Isabelle) is not reviewed in v0.4.x.",
    "MA2": "Cross-domain claim transfer is outside the current review surface.",
    "MA3": "Conjecture status tracking beyond the stated domain is not measured.",
}
