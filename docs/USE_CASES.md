# Use Cases

SPAR is built first for mathematical and physics-grade model review, but the
review pattern is broader.

## Primary fit

### Physics and mathematical model validation

Use SPAR when:

- output can remain numerically stable while justification weakens
- analytical anchors matter
- maturity state changes what a result is allowed to claim
- approximation, boundedness, or partial closure must remain visible
- runtime memory state and invariant continuity should tighten review, not stay outside it

In the current physics adapter, this contextual tightening already appears as:

- `B5` — MICA runtime state
- `C10` — MICA invariant continuity

### Scientific computing

Use SPAR when:

- reproducibility is necessary but not sufficient
- review must distinguish exact, approximate, heuristic, and bounded results
- implementation changes can outpace governance language

This is also the natural bridge to the next adapter direction:

- generic scientific-model review for PDEs
- dynamical and control models
- inverse and calibration models
- constrained optimization systems
- scientific ML surrogates

## Secondary fit

### Scientific ML

Use SPAR when a model can predict well but still overstate what part of the
underlying theory it actually instantiates.

### Model governance

Use SPAR when output status, maturity labels, and implementation reality can
drift apart across releases or operating environments.

### AI code review

Use SPAR when tests pass but the claim of completeness, closure, or capability
still needs a second review surface.

### Regulated analytics and reporting

Use SPAR when a green dashboard is not enough and downstream users need to know
whether a result is exact, partial, heuristic, or environment-conditional.
