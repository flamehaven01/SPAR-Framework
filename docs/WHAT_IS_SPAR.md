# What Is SPAR

**SPAR** stands for **Sovereign Physics Autonomous Review**.

It began as a deterministic adversarial review layer inside Flamehaven-TOE, an
open physics simulation and AI governance engine. The extracted framework keeps
the same core purpose:

**review whether an output deserves the claim attached to it.**

That is the central distinction.

- ordinary validation asks whether the system still produces the expected output
- SPAR asks whether the interpretation built on top of that output is still justified

SPAR therefore sits above unit tests and regression checks. It does not replace
them. It reviews a different object.

## What problem it solves

SPAR exists for systems where stable output is not enough.

Examples:

- a mathematical model can remain numerically stable while the analytical
  justification weakens
- a computation path can improve while the outward-facing maturity label remains
  stale
- an approximation can be reported as if it were closed
- a score can remain reproducible while its claim becomes too strong

The framework is most naturally suited to:

- physics and mathematical model validation
- scientific computing pipelines
- research systems that need explicit admissibility or maturity surfaces

The same review pattern can then extend into:

- model governance
- scientific ML
- AI code review
- regulated analytics and reporting

## What makes SPAR different

SPAR is not:

- a generic linter
- a theorem prover
- a free-form LLM judge

SPAR is:

- a deterministic review kernel
- a registry-backed maturity and gap model
- a layered framework for reviewing claim-worthiness

In the current physics adapter, contextual review now includes:

- `B5` — MICA runtime state
- `C10` — MICA invariant continuity

Those checks do not replace physics contracts. They tighten interpretation and
maturity review around them.

The first adapter in this repository is physics. That is the proof case, not
the final limit of the framework.

The next expansion path is a **scientific-model adapter** for PDE systems,
dynamical systems, inverse problems, constrained optimization models, and
scientific ML surrogates.
