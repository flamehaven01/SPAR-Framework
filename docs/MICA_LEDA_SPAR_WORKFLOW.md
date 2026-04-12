# MICA -> LEDA -> SPAR Workflow

This workflow separates three different responsibilities.

## Role Split

### 1. MICA

`MICA` injects memory context.

It provides:

- project archive
- design invariants
- prior decisions
- runtime memory loading contract

This is **memory truth**.

### 2. LEDA

`LEDA` analyzes the current codebase and emits a structured YAML payload.

It provides:

- current code-analysis surface
- calibration and override state
- claim-risk candidates
- suggested maturity hints

This is **code truth**.

### 3. SPAR

`SPAR` consumes:

- runtime result
- MICA memory context
- optional LEDA injection payload

It performs:

- Layer A: anchor consistency
- Layer B: interpretation validity
- Layer C: existence and maturity review

This is **admissibility review**.

## Execution Order

```text
MICA detect
  -> classify INVOCATION_MODE / LEGACY_MODE / INACTIVE

MICA load
  -> inject design invariants and archive context

LEDA analyze
  -> emit leda_injection.yaml

SPAR review
  -> read runtime result + MICA context + LEDA injection
  -> produce review surface and verdict
```

## Why This Split Matters

If these roles collapse together, the system becomes harder to reason about.

- MICA should not generate verdicts
- LEDA should not replace SPAR
- SPAR should not pretend to infer design memory from code alone

The architecture works because each engine is responsible for a different kind
of truth surface.

`MICA` is not just loaded and forgotten. In contextual review, its runtime
state and invariant surface can tighten Layer B/Layer C interpretation without
replacing domain-specific physics checks.

## MICA Runtime Contract in SPAR

When a project root is provided, SPAR follows the MICA v0.2.2 detection order:

1. project root `mica.yaml`
2. `memory/mica.yaml`
3. `memory/*.mica.*.json`

That gives SPAR an explicit runtime state:

- `INVOCATION_MODE`
- `LEGACY_MODE`
- `INACTIVE`

SPAR persists only a safe summary of that state in `context_summary`.
