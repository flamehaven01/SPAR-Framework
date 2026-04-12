# Admissibility

SPAR's core idea is simple:

**reliability and admissibility are not the same thing.**

Reliability asks whether a system produces stable, repeatable outputs.
Admissibility asks whether those outputs deserve the meanings attached to them.

In practical terms, SPAR treats admissibility as **claim-worthiness**:

- does this result justify the interpretation attached to it
- does the reported maturity state still match the implementation state
- does the system have enough basis to make the outward-facing claim it is making

## Why regression is not enough

A system can stay green while still becoming less honest about what it is doing.

Examples:

- a stub can return a stable value and still support a false claim
- a heuristic path can be reported as if it were exact
- a registry can lag behind an implementation change
- a score can remain smooth while its justification is weak

Regression catches continuity problems. SPAR is designed to catch
**claim drift**.

## The working definition

SPAR does not promise truth.

It prevents unjustified confidence.

That is a more defensible engineering target than universal truth adjudication.
It lets teams force a warning, downgrade, or reclassification when output,
implementation state, and interpretation stop matching.

## Why this matters first in physics

Physics and mathematical model validation are the first hard proof case because
they make the difference between:

- stable output
- justified claim
- declared maturity

sharp enough to review rigorously.

That same structure then generalizes into other systems where interpretation
cannot be allowed to ride for free on top of green output.
