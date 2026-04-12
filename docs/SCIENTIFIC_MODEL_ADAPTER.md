# Scientific Model Adapter Draft

This note defines the next adapter direction after `spar_domain_physics`.

The goal is not to turn SPAR into a generic governance tool. The goal is to
extend SPAR from a physics proof case into a broader mathematical and
scientific-model validation framework.

## Target Model Classes

- PDE and simulation models
- dynamical systems
- control models
- inverse problems
- calibration models
- constrained optimization models
- scientific ML surrogates
- PINNs and hybrid scientific models

## What the Adapter Should Provide

### Layer A

Analytical or contractual anchors for the model family:

- conservation or boundedness contracts
- convergence or residual contracts
- domain-specific validity regimes

### Layer B

Interpretation rules for model claims:

- exact vs approximate
- calibrated vs justified
- surrogate vs theory-grounded
- bounded regime vs general claim

### Layer C

Implementation and maturity review:

- heuristic
- partial
- closed
- environment-conditional
- research-only

## Why This Adapter Matters

The physics adapter proves SPAR in a hard domain. The scientific-model adapter
would prove that the same review structure works across mathematical model
families without collapsing into generic compliance prose.

That keeps SPAR where it is strongest:

- stable output is not enough
- passing regression is not enough
- numerical success does not automatically justify a stronger claim

## Non-Goals

- generic software linting
- business-rule validation
- replacing theorem provers
- replacing domain-specific scientific judgment

This adapter should extend SPAR's admissibility logic, not dilute it.
