# Physics as the Proof Case

SPAR is not a physics-only framework.

Physics is where the framework first proved itself.

That matters because mathematical and physics-grade systems make claim drift
visible in a particularly hard form:

- analytical contracts matter
- approximation regimes matter
- maturity state changes what the result is allowed to claim
- reproducibility alone is not enough

## Why physics came first

In Flamehaven-TOE, the review problem was not simply whether the engine ran.
The harder problem was whether the output still deserved the claim attached to
it.

That produced concrete failure modes:

- a path can return acceptable-looking values while remaining epistemically empty
- a formerly heuristic path can become genuine while the registry remains stale
- a governance score can look smooth before its underlying formula deserves the
  confidence attached to it

## The Omega transition

The clearest example is SIDRCE Omega.

An earlier version used a large arbitrary multiplicative constant on a raw
residual. The score behaved smoothly, but the formula was stronger in
presentation than in justification.

It was later replaced with a chi-squared Gaussian construction. That changed
the epistemic status of the score because the reported value became reversibly
connected to the underlying residual:

```text
||beta|| = tol * sqrt(-2 * ln(score))
```

That is exactly the kind of shift SPAR is meant to notice and classify.

## Registry-backed review

The other proof point is the registry itself.

SPAR keeps maturity and gap states as machine-readable review objects rather
than prose-only caveats. That allows the runtime to emit:

- model registry snapshots
- gap registry snapshots
- maturity state surfaces that travel with the result

This is the bridge between concept and operational review.
