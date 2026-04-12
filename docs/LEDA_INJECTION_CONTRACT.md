# LEDA Injection Contract

`LEDA` is not the SPAR verdict engine.

Its role is narrower: analyze the current codebase and emit a structured
injection surface that SPAR can optionally consume during review.

## Purpose

This payload exists to carry **code-truth** into SPAR.

Used together:

- `MICA` provides memory truth
- `LEDA` provides code truth
- `SPAR` provides admissibility review

## Responsibilities

LEDA should:

- analyze the current codebase
- read configuration overrides and calibration state
- summarize claim-risk candidates
- suggest maturity hints
- emit a YAML artifact

LEDA should **not**:

- issue the final SPAR verdict
- replace Layer A / B / C review
- act as a free-form judge

## Canonical Payload Shape

```yaml
version: "0.1"
project:
  name: "ai-slop-detector"
  root: "/workspace/ai-slop-detector"
  type: "python"

source:
  analyzer: "LEDA"
  generated_at: "2026-04-12T00:00:00Z"
  config_path: "/workspace/.slopconfig.yaml"
  history_db: "/home/user/.slop-detector/history.db"

analysis:
  mode: "project"
  status: "suspicious"
  total_files: 42
  deficit_files: 5
  clean_files: 37
  avg_deficit_score: 24.7
  weighted_deficit_score: 22.9

calibration:
  status: "ok"
  history_records: 34
  unique_files: 12
  improvement_events: 8
  fp_candidates: 7
  confidence_gap: 0.18
  current_weights:
    ldr: 0.4
    inflation: 0.3
    ddc: 0.3
    purity: 0.1
  optimal_weights:
    ldr: 0.45
    inflation: 0.25
    ddc: 0.2
    purity: 0.1

claim_risk:
  - id: "adaptive_weight_surface_active"
    severity: "medium"
    layer_hint: "Layer C"
    finding: "History-backed calibration is active, so effective review weighting may evolve beyond static documentation."
    evidence:
      - "calibration_status=ok"
      - "history_records=15"
    suggested_action: "Treat maturity and registry state as a moving review surface, not a fixed declaration."

maturity:
  suggested_current: "partial"
  confidence: 0.78
  rationale: "Stable analysis surface supports bounded confidence, but code-quality evidence alone does not justify closure."

overrides:
  configured_domain_overrides: []
  suggested_domain_overrides: []

spar_review_hints:
  preferred_layers:
    - "Layer B"
    - "Layer C"
  registry_candidates:
    - "heuristic"
    - "partial"
    - "environment_conditional"
  notes:
    - "LEDA is a code-truth surface only. It does not issue final admissibility verdicts."
```

## Consumption Rules

SPAR should treat this payload as:

- optional context
- evidence for interpretation and maturity review
- a non-authoritative input to Layer B / Layer C

SPAR should **not** treat LEDA output as:

- analytical ground truth
- a final maturity decision
- a substitute for runtime result data

## Where It Fits

This contract is most useful when:

- the project already has code-analysis history
- calibration or override state matters
- implementation quality and outward-facing claims may drift apart

It is especially useful as a bridge between:

- `MICA` memory injection
- codebase analysis
- SPAR admissibility review
