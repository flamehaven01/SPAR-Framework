# Changelog

## [Unreleased]

## [0.6.0] - 2026-05-26

### Added

- **SPAR-001 (CLI ergonomics).** `spar review` accepts a new
  `--from-json PATH` flag and an optional positional `<project>` argument.
  `--from-json` runs a heuristic key router over freeform JSON: keys matching
  `report_text` / `report` / `summary` / `description` / `narrative` (string
  values) are routed to `report_text`; keys matching `source` / `background`
  / `ground_truth` / `ground_truth_source` (string values) populate the
  `--source` field; everything else is preserved on `subject` as-is.
  `--subject-json` (canonical, strict schema) is now optional but still
  validated; passing both `--subject-json` and `--from-json` is rejected as
  `input_error`. Positional `<project>` aliases `--project-root` when the
  flag is unset. Legacy invocations are byte-for-byte compatible.
- **SPAR-002 (`spar_domain_generic` adapter).** New domain-agnostic adapter
  package at `src/spar_domain_generic/`. Operates on a minimal
  `claim_profile` schema (`claim_made`, `evidence_cited`, `scope_bounded`)
  with no physics/ML/math-specific keys. Wired into the CLI as
  `--adapter generic`. Intended as (a) a template for new adapters and
  (b) a fallback for `--from-json` input that does not commit to a specific
  domain schema.
- **SPAR-003 (`ReviewResult.warnings`).** New `warnings: list[str]` field on
  `ReviewResult`. The engine emits `no_observation_source` when
  `len(layer_a) == 0 AND claim_drift == 0` — a guard against the
  silent-pass-on-empty-input case where a missing or garbage subject would
  otherwise look identical to a clean review. `to_dict()` omits `warnings`
  when the list is empty (no breaking change for downstream consumers).
- **SPAR-005 (`$SPAR_POLICY_PATH`).** Scoring policy resolution now consults
  the `SPAR_POLICY_PATH` environment variable before falling back to the
  packaged default at `spar_framework/policies/review_policy.v1.json`.
  A path that is set but missing raises `FileNotFoundError` instead of
  silently falling through. Cached for the process lifetime; tests rebuild
  via `scoring._load_review_policy.cache_clear()`.

### Documentation

- **SPAR-004.** New `docs/RUNTIME.md` documenting the `ReviewRuntime`
  contract: minimal vs full construction, layer-builder signatures, the
  generic adapter as a template, and the `$SPAR_POLICY_PATH` override.

### Tests

- 22 new tests across 4 files:
  - `tests/test_cli_review.py` (7) — SPAR-001 backward compatibility,
    mutual exclusion, missing-input errors, heuristic key routing,
    subject-wrapper unwrapping, non-object payload rejection.
  - `tests/test_warnings.py` (4) — SPAR-003 emission conditions and
    `to_dict()` omission.
  - `tests/test_policy_env.py` (4) — SPAR-005 default, override, missing
    file, whitespace-only env var.
  - `tests/test_generic_adapter.py` (7) — SPAR-002 runtime invocation,
    layer A/C status flags, slop detection, framework-declared gaps,
    registry snapshot shape, CLI smoke tests for `--adapter generic`.
- Total: **147 passing tests** (up from 125 in v0.5.0).

### Notes

- No regressions: all 125 v0.5.0 tests still pass.
- No silent fallbacks introduced: the new `--from-json` path never invents
  data; unrecognised keys are preserved on `subject` and surfaced through
  the adapter's existing layer-A checks.

## [0.5.0] - 2026-05-09

### Benchmark harness and comparison surface

**`src/spar_framework/harness.py`** (new):
- `BatchSummary` dataclass: `adapter`, `count`, `verdicts`, `mean_claim_drift`, `mean_coverage_rate`, `cannot_check_rate`, `framework_declared_rate`, `top_flags`. `.to_dict()` rounds floats to 4 decimal places.
- `run_batch(runtime, adapter, subject_paths, ...)` — runs review on each subject file, optionally writes individual review JSONs to `reports_dir`, returns `BatchSummary`. Creates `reports_dir` if needed.
- `_compute_summary(adapter, results)` — aggregates verdict distribution, per-subject CANNOT_CHECK rate, framework_declared rate, mean claim_drift/coverage_rate, top 5 non-passing flag IDs.
- `compare_reviews(review_paths)` — extracts verdict/score/claim_drift/coverage_rate/flags from each review JSON for side-by-side comparison.

**`src/spar_framework/report.py`** (new):
- `batch_summary_to_markdown(summary)` — renders BatchSummary as a Markdown document with verdict table and metrics section.
- `compare_reviews_to_markdown(comparisons)` — renders comparison list as a Markdown table.

### CLI additions

- `spar batch --adapter ADAPTER --subjects DIR [--reports DIR] [--output-json PATH] [--output-md PATH]` — batch review over a directory of subject JSON files; emits summary JSON to stdout.
- `spar compare review1.json review2.json ... [--output-json PATH] [--output-md PATH]` — side-by-side comparison of review files.
- `SUBCOMMANDS` extended with `batch` and `compare`.

### Validation

- Added `tests/test_harness.py` with 17 tests covering:
  - `run_batch` count, verdict distribution, metric ranges, individual report writing
  - Empty subject list returns zero-count summary
  - Math adapter batch run
  - `compare_reviews` entry count, flag extraction for ANOMALY subjects
  - `BatchSummary.to_dict` has all required fields
  - Markdown rendering for batch summary and comparison table
  - CLI e2e: `spar batch` writes JSON + Markdown + individual reports; empty dir returns error
  - CLI e2e: `spar compare` writes JSON + Markdown
- Total: **125 passing tests** (52 physics + 26 ML + 30 math + 17 harness)

## [0.4.1] - 2026-05-09

### Math adapter policy wiring hardening

**`layer_a.py` — `novelty_uncited_status` consumed:**
- `check_a3_novelty()` now reads `_RULES.get("novelty_uncited_status", "WARN")` instead of hardcoding the string `"WARN"`. Policy can now change the novelty uncited status without a code change.

**`layer_c.py` — `proof_status_values` guard:**
- Loads `_PROOF_STATUS_VALUES = frozenset(_LAYER_C_CONFIG["proof_status_values"])` at import time.
- `check_c1_proof_maturity()` now returns `CANNOT_CHECK` when `proof_status` is not in the recognized set, rather than silently falling through to the `absent` branch. Unknown values are now surfaced explicitly.

### Validation

- Added 8 regression tests:
  - B2 generality language: phrase detected without profile → WARN; with profile → PASS
  - B3 novelty language: phrase detected without profile → WARN; with profile → PASS
  - `novelty_uncited_status` policy field is consumed: A3 runtime status matches policy declaration
  - `proof_status_values` guard: unknown `proof_status` value → CANNOT_CHECK
- Total: **108 passing tests** (52 physics + 26 ML + 30 math)

## [0.4.0] - 2026-05-09

### New adapter: spar_domain_math

Third domain adapter. Covers proof claim drift for mathematical results. Scope is deliberately narrow: proof/generality/novelty 3-claim contract, proof evidence surface, statement boundary clarity. Extended surfaces (formal verification, cross-domain transfer) are declared via framework_declared.

**Subject schema** (`src/spar_domain_math/schemas/math_subject.schema.json`):
- `theorem_id`, `theorem_type` (`theorem|lemma|proposition|corollary|conjecture`), `domain`
- `claim_profile`: `proof_claimed`, `generality_claimed`, `novelty_claimed`
- `proof_surface`: `proof_status` (enum: `complete|sketch|absent`), `assumptions_explicit`, `prior_art_cited`

**Layer A — proof contract checks:**
- A1: Proof claim vs evidence surface (FAIL if absent; ANOMALY if conjecture + proof_claimed; CONSISTENT otherwise)
- A2: Generality claim vs assumptions (GAP if no explicit assumptions)
- A3: Novelty claim vs prior art (WARN if prior_art_cited=false — not GAP; novelty is inherently harder to verify)

**Layer B — claim language vs subject profile:**
- B1: Proof language in report_text vs `proof_claimed` (WARN if exceeds profile)
- B2: Generality language vs `generality_claimed` (WARN if exceeds)
- B3: Novelty language vs `novelty_claimed` (WARN if exceeds)
- B4: Formal verification language detection (CANNOT_CHECK conditional — only fires on detected phrase)

**Layer C — evidence maturity:**
- C1: Proof completeness maturity (`complete`=GENUINE, `sketch`=APPROXIMATION, `absent`=GAP)
- C2: Statement boundary clarity (`assumptions_explicit`=GENUINE, else GAP)

**Framework-declared limitation surfaces (not scored):**
- FD-MA1: Machine-checked formal verification not covered
- FD-MA2: Cross-domain claim transfer not reviewed
- FD-MA3: Conjecture status tracking partial

**Policy file:** `src/spar_domain_math/policies/math_review_policy.v1.json`

**Design decisions vs ML adapter:**
- `proof_status` uses a 3-value enum (`complete|sketch|absent`) instead of two booleans — eliminates contradictory states
- A3 novelty emits WARN (not GAP) because prior art absence is not conclusive evidence of novelty drift
- `conjecture` is first-class in `theorem_type` and creates a structural ANOMALY when combined with `proof_claimed=true`

### CLI generalization

- `--adapter` now accepts `physics`, `ml`, and `math` in `spar review`, `spar discover`, and `spar example`
- Adapter choices extracted to `_ADAPTER_CHOICES` list — adding future adapters is a single list entry
- `spar example --adapter math --task topology` generates math subject templates
- `spar example --adapter math --task combinatorics` available
- `spar schema subject --adapter math` returns `math_subject.schema.json`
- `_ADAPTER_SCHEMA_ROUTES` extended with `math/subject` entry

### Validation

- Added `tests/test_math_adapter.py` with 24 tests covering:
  - All 3 Layer A claim drift cases (proof absent→FAIL, conjecture+proof→ANOMALY, novelty uncited→WARN)
  - proof_status sketch→CONSISTENT (A1), APPROXIMATION (C1)
  - Generality with/without assumptions (A2 CONSISTENT/GAP)
  - Novelty with/without prior art (A3 CONSISTENT/WARN)
  - B1 proof language without profile → WARN
  - B4 formal verification phrase → CANNOT_CHECK; no phrase → PASS
  - C1 all three proof_status states (GENUINE/APPROXIMATION/GAP)
  - C2 assumptions present/absent (GENUINE/GAP)
  - Framework-declared scope validation
  - Registry snapshot counts (3 models, 3 gaps)
  - Policy loader correctness (layer_a rules)
  - CLI e2e: review, example, schema with --adapter math
- Total: **102 passing tests** (52 physics + 26 ML + 24 math)

## [0.3.2] - 2026-05-09

### CLI adapter decoupling

- Removed top-level `from spar_domain_physics.ground_truth_table import GROUND_TRUTH` and `from spar_domain_physics.runtime import get_review_runtime` imports from `cli.py`. Both are now lazy imports inside the functions that need them (`_run_example()` physics branch and `_get_runtime()` physics branch). Importing the `spar_framework.cli` module no longer forces the physics adapter to load.
- Replaced inline `if adapter == "ml" and args.target == "subject"` check in `_run_schema()` with a `_ADAPTER_SCHEMA_ROUTES` dict (`dict[str, dict[str, tuple[str, str, str]]]`). Adding a new adapter's schema surface is now a single dict entry rather than a new conditional branch.

### Validation

- No new tests (no behavioral change). All **78 tests** still pass.

## [0.3.1] - 2026-05-09

### ML adapter hardening

**Layer B completeness:**
- Added `check_b3_robustness_language()`: WARN when robustness phrases detected in report_text but `robustness_claimed=false`. Uses `robustness_phrases` from policy (was loaded but unused in v0.3.0).
- Renamed former B3 to `check_b4_extended_claims()`: now conditional — emits `CANNOT_CHECK` only when extended claim phrases (fairness, calibration, efficiency, safety) are actually detected in report_text; emits `PASS` otherwise. Previously always emitted `CANNOT_CHECK`, inflating false positives on coverage_rate.
- Added `extended_claim_phrases` list to `ml_review_policy.v1.json` `layer_b` section.
- `build_layer_b_checks()` now returns B1, B2, B3, B4 (four checks; was three).

**Layer A policy wiring:**
- `check_a1_sota()`, `check_a2_generalization()`, `check_a3_robustness()` now read gates from `_RULES` (`sota_requires_baseline`, `generalization_requires_ood_or_scope_restriction`, `robustness_requires_eval`) instead of hardcoded `True`. When a policy flag is `false`, the check returns `PASS` or `CANNOT_CHECK` rather than `FAIL`/`GAP`. `_RULES` was loaded in v0.3.0 but not wired.

**CLI schema surface:**
- `spar schema subject --adapter ml` now returns `ml_subject.schema.json`. Without `--adapter ml`, falls through to the physics schema (unchanged default). `--adapter` flag added to the `schema` subcommand.

### Validation

- Added 10 regression tests:
  - B3: robustness phrase triggers WARN, matching profile passes
  - B4: extended phrase triggers CANNOT_CHECK, no phrase returns PASS
  - Layer A rules loaded from policy with correct values
  - CLI e2e: `spar review --adapter ml` produces valid result with B1/B3/B4 in layer_b
  - CLI e2e: `spar review --adapter ml` accepts wrapped example payload
  - CLI e2e: `spar example --adapter ml --task image_classification` emits correct structure
  - CLI e2e: `spar schema subject --adapter ml` returns ML subject schema title
  - CLI e2e: `spar explain` with ML review output emits verdict and score
- Total: **78 passing tests** (52 physics + 26 ML)

## [0.3.0] - 2026-05-09

### New adapter: spar_domain_ml

Second domain adapter. Covers benchmark claim drift for ML systems. Scope is deliberately narrow: benchmark/metric/split contract, reproducibility surface, and three first-class claim types (SOTA, generalization, robustness). Extended claims (fairness, calibration, efficiency) are declared as not covered via framework_declared surfaces.

**Subject schema** (`src/spar_domain_ml/schemas/ml_subject.schema.json`):
- `task_family`, `dataset`, `split`, `metric_name`, `metric_value`, `metric_direction`
- `baseline_name`, `baseline_value` (required when `sota_claimed=true`)
- `claim_profile`: `sota_claimed`, `generalization_claimed`, `robustness_claimed`
- `reproducibility`: `seed_present`, `dataset_version_present`, `config_hash_present`
- `evaluation_scope`: `ood_evaluated`, `robustness_evaluated`, `claim_scope_restricted`

**Layer A — benchmark contract checks:**
- A1: SOTA claim vs baseline anchor (FAIL if missing, ANOMALY if metric contradicts)
- A2: Generalization claim vs OOD / scope restriction (GAP if neither present)
- A3: Robustness claim vs evaluation evidence (GAP if not evaluated)

**Layer B — claim language vs subject profile:**
- B1: SOTA language in report_text vs `sota_claimed` (WARN if exceeds profile)
- B2: Generalization language vs `generalization_claimed` (WARN if exceeds)
- B3: Extended claim class coverage (CANNOT_CHECK — not reviewed in v0.3.0)

**Layer C — evidence maturity:**
- C1: Reproducibility maturity (3/3=GENUINE, 2/3=APPROXIMATION, <2=GAP)
- C2: Evaluation surface completeness vs claimed scope

**Framework-declared limitation surfaces (not scored):**
- FD-M1: Extended claim classes not covered
- FD-M2: Temporal drift analysis not reviewed
- FD-M3: Cross-task generalization declared partial

**Policy file:** `src/spar_domain_ml/policies/ml_review_policy.v1.json`

### CLI generalization

- `--adapter` now accepts `physics` and `ml` in `spar review`, `spar discover`, and `spar example`
- `spar example --adapter ml --task image_classification` generates ML subject templates
- `spar example --adapter ml --task text_classification` available
- Physics `--source` validation moved from argparse `choices=` into runtime check to support adapter-specific source sets

### Validation

- Added `tests/test_ml_adapter.py` with 16 tests covering:
  - All 5 claim drift cases (SOTA without baseline, generalization without OOD, robustness without eval, metric contradiction, text exceeds profile)
  - Reproducibility threshold boundaries (3/3, 2/3, 1/3)
  - Framework-declared scope validation
  - Registry snapshot counts
  - Policy loader correctness
- Total: **68 passing tests** (52 physics + 16 ML)

## [0.2.3] - 2026-05-09

### Core hardening — adapter override readiness

- Parameterized `slop_check(text, policy=default_policy)` in `slop_rules.py`. Adapters that need a domain-specific slop penalty multiplier can now bind a custom `ReviewPolicy` via `functools.partial` before passing the checker to `ReviewRuntime.slop_check`. The `SlopChecker = Callable[[str], tuple[int, list[str]]]` contract in `engine.py` is unchanged — callers use the default or bind via partial.
- Imported `ReviewPolicy` into `slop_rules.py` alongside `default_policy` to support the explicit type annotation.

### Validation

- Added 2 regression tests covering:
  - `slop_check` with a custom policy (`slop_penalty_per_hit=5`) returns the correct scaled penalty
  - `functools.partial`-bound checker produces identical results to a direct call with the same policy
- Total: **52 passing tests**

## [0.2.2] - 2026-05-09

### Physics adapter threshold hardening

- Added `layer_c` section to `physics_review_policy.v1.json` with three explicitly named thresholds:
  - `beta_b_near_zero_threshold: 1e-9` — boundary below which `beta_B` is classified as near-zero in `evaluate_beta_b_genuineness()`
  - `brst_ricci_gap_above: 0.1` — `ricci_norm` at or above this threshold → `GAP` in BRST genuineness
  - `brst_ricci_approx_above: 0.01` — `ricci_norm` at or above this threshold → `APPROXIMATION` in BRST genuineness
- Added `get_layer_c_thresholds()` to `policy_loader.py` following the existing `get_layer_b_thresholds()` pattern.
- Updated `layer_c_foundation_helpers.py` to load all three thresholds from policy at import time; removed all literal `1e-9`, `0.1`, `0.01` comparisons from check logic.

### Validation

- Added 2 regression tests covering:
  - `get_layer_c_thresholds()` returns values matching policy JSON
  - BRST ricci boundary classification is correct at `0.1` (GAP), `0.05` (APPROXIMATION), `0.005` (GENUINE)
- Total: **50 passing tests**

## [0.2.1] - 2026-05-09

### Core policy hardening

- Externalized `slop_penalty_per_hit` (10) into `review_policy.v1.json` under `scoring`. `slop_rules.slop_check()` now reads the multiplier from `default_policy` instead of a hardcoded literal.
- Externalized `coverage_rate_precision` (4) into `review_policy.v1.json` under `scoring`. `compute_coverage_rate()` now rounds to the policy-defined decimal place count.
- Added `slop_severity_weights` table (`critical`/`high`/`medium`/`low`) to `review_policy.v1.json` as a reserved structure aligned with the AI-SLOP-Detector v3.7.x tiered model. Currently unused in scoring logic; marks the evolution path from flat-multiplier to per-severity weighted slop scoring.
- Added `slop_penalty_per_hit`, `coverage_rate_precision`, and `slop_severity_weights` fields to the `ReviewPolicy` dataclass.
- `compute_coverage_rate()` now accepts an optional `policy` parameter (default: `default_policy`).

### Validation

- Added 2 regression tests covering:
  - `slop_penalty_per_hit` loaded from JSON and propagated through `slop_check()`
  - `coverage_rate_precision` loaded from JSON and applied in `compute_coverage_rate()`
- Total: **48 passing tests**

## [0.2.0] - 2026-05-09

### Framework core hardening

- Added `scope` field to `CheckResult` (default `"subject"`). Framework-declared adapter policy checks now carry `scope = "adapter_limitation"` so they are structurally distinct from subject-derived findings.
- Added `claim_drift` and `coverage_rate` to `ReviewResult`:
  - `claim_drift` — sum of absolute penalty weights from subject checks (Layer A/B/C); excludes `slop_penalty` and `framework_declared`
  - `coverage_rate` — fraction of subject checks that returned a determinate result (not `CANNOT_CHECK`); `framework_declared` excluded from denominator
- Added `external_ref: bool = False` to `ModelSpec`. When `True`, the `model_registry_snapshot` emits the flag so consumers can distinguish in-package modules from external implementation references. All four current physics models are marked `external_ref=True`.
- Externalized the framework core scoring policy into `src/spar_framework/policies/review_policy.v1.json`. Previously, penalty weights and verdict thresholds were hardcoded in `scoring.py`; they are now loaded at runtime via `importlib.resources` and cached. The physics adapter retains its own `physics_review_policy.v1.json` for adapter-specific Layer A/B thresholds.
- Added `compute_claim_drift()` and `compute_coverage_rate()` to `scoring.py`.
- Added `build_registry_snapshots()` and updated `build_core_review()` in `runtime_context.py` to wire the new metrics through the engine.
- Added `"policies/*.json"` to `spar_framework` package-data in `pyproject.toml`.

### Physics adapter

- Applied `scope = "adapter_limitation"` to all five `framework_declared` checks (C4-C8) in `layer_c_advanced.py`.
- Applied `external_ref=True` to all four `PHYSICS_MODELS` entries in `registry_seed.py`.

### Validation

- Added 8 regression tests covering:
  - `CheckResult.scope` default and serialization
  - `framework_declared` checks carry `adapter_limitation` scope
  - `claim_drift` and `coverage_rate` values on a full review run
  - `claim_drift` excludes `slop_penalty` (score gap > drift gap > 0)
  - `coverage_rate` excludes `CANNOT_CHECK` and `framework_declared` from denominator
  - framework core scoring policy loaded from packaged JSON
  - `external_ref` flag present / absent in model registry snapshot
- Total: **46 passing tests**

## [0.1.5] - 2026-05-07

### External audit follow-up

- Hardened the `spar` CLI so unknown subcommands now return a structured `unknown_command` error instead of falling through to the legacy review path
- Synchronized the checked-in MICA archive and playbook with the current package release surface (`0.1.5`)
- Added regression coverage to keep the packaged version and MICA archive metadata aligned
- Separated `framework_declared` adapter policy surfaces from scored subject-derived review findings so static doctrine no longer masquerades as runtime validation
- Made `spar review` accept the wrapped payload emitted by `spar example`
- Made `spar explain` null-safe when `context_summary` is absent
- Externalized the physics adapter review policy into packaged JSON (`src/spar_domain_physics/policies/physics_review_policy.v1.json`) and wired Layer A/B thresholds to that policy data

## [0.1.4] - 2026-04-13

### Release correction

- Reissued the package from the correct `main` head after the `v0.1.3` tag was found to point at an older `0.1.2` commit
- Preserved the `0.1.3` code changes while publishing them under a clean `0.1.4` package and release tag

## [0.1.3] - 2026-04-13

### Physics adapter correctness

- Removed the duplicate `PLANCK_MASS_GEV` definition from Layer A runtime checks so A6 and B1 now share the same source constant
- Fixed `match_ground_truth_source()` so `ads dilaton` no longer falls through to the `linear_dilaton` table
- Restored `Any` import in the CLI example-subject type surface

### Review architecture documentation

- Added explicit comments clarifying why Layer A ignores context, Layer B ignores source/gate, and Layer C ignores gate/params in the current physics adapter
- Added a `docs_sanity` badge and a short correctness-fix note to the README hero surface

### Validation

- Added regression coverage for:
  - single-source Planck mass consistency
  - `ads dilaton` matcher correctness
- Verified current package state with `34` passing tests

## [0.1.2] - 2026-04-12

### CLI

- Added AI-friendly `spar` CLI with explicit subcommands:
  - `review`
  - `explain`
  - `discover`
  - `schema`
  - `example`
- Preserved `spar-context-review` as a legacy compatibility entrypoint
- Added `docs/CLI.md` to document command contracts, exit codes, and security defaults
- Promoted `subject`, `result`, and `context` schemas into packaged JSON artifacts under `src/spar_framework/schemas/`
- Added `--output-json` support to `spar schema`

### Integration docs

- Added `docs/LEDA_INJECTION_CONTRACT.md`
- Added `docs/MICA_LEDA_SPAR_WORKFLOW.md`
- Added `docs/SECURITY_MODEL.md`
- Linked the README to the new integration contract docs so MICA/LEDA/SPAR
  role separation is explicit

### Context ingestion

- Added context ingestion helpers:
  - `src/spar_framework/context.py`
  - `src/spar_framework/mica.py`
  - `src/spar_framework/workflow.py`
- Added CLI workflow entrypoint:
  - `spar-context-review`
- `run_review()` now accepts optional `memory_context` and `leda_injection`
- `ReviewResult` now persists only `context_summary`, not the raw payload
- Added tests covering safe context summarization and contextual review loading
- Added MICA runtime discovery using the v0.2.2 detection order:
  - root `mica.yaml`
  - `memory/mica.yaml`
  - legacy `memory/*.mica.*.json`
- Added explicit MICA runtime states to contextual review:
  - `INVOCATION_MODE`
  - `LEGACY_MODE`
  - `INACTIVE`

### Physics adapter context use

- Physics Layer B now emits an additional check when restricted LEDA context
  reports claim-risk candidates
- Physics Layer C now emits an additional maturity-alignment check from
  restricted LEDA context
- Physics Layer B now reads MICA runtime state as an interpretation-tightening
  signal
- Physics Layer C now reads MICA invariant continuity as a maturity-context
  signal

### Documentation

- Added contextual README examples for `INVOCATION_MODE` and `LEGACY_MODE`
- Added architecture notes for `B5` and `C10`
- Added `docs/SCIENTIFIC_MODEL_ADAPTER.md` as the next adapter draft
- Added repository logo to README
- Rebuilt the README around a clearer GitHub landing order:
  - hero
  - why it exists
  - quick start
  - three-layer structure
  - scoring
  - fit / adoption / docs

### Publishing

- Simplified `.github/workflows/publish.yml` to publish on version tags and manual dispatch only
- Removed release-event publishing to avoid duplicate PyPI publish attempts for the same version
- Added a PyPI version badge to the README
- Opted the publish workflow into Node 24 for GitHub JavaScript actions

## [0.1.1] - 2026-04-12

### PyPI publishing readiness

- Added GitHub Actions publish workflow:
  - `.github/workflows/publish.yml`
- Aligned package metadata URLs with the live repository:
  - `Homepage`
  - `Repository`
  - `Issues`
- Prepared the repository for PyPI Trusted Publisher flow using GitHub OIDC
- Preserved the standalone kernel, physics adapter, and current passing test/build state

### Documentation structure

- Added canonical concept docs under `docs/`:
  - `WHAT_IS_SPAR.md`
  - `ADMISSIBILITY.md`
  - `PHYSICS_PROOF_CASE.md`
  - `USE_CASES.md`
- Linked the README to the concept docs so the external article thesis has a
  durable in-repo documentation surface

## [0.1.0] - 2026-04-11

### Initial scaffold

- Created standalone `spar-framework` project root
- Added package skeleton for:
  - core result model
  - scoring policy
  - registry snapshots
  - domain adapter interfaces
- Added architecture and extraction docs
- Added MICA v0.2.2 package:
  - `mica.yaml`
  - archive JSON
  - playbook
  - runtime note

### Intended next step

- extract reusable logic from TOE `src/toe/spar`
- keep physics contracts as the first domain adapter
- preserve snapshot-emitting behavior during extraction

### Extraction progress

- Added generic review kernel:
  - `engine.py`
  - `runtime_context.py`
  - `result_types.py`
  - `scoring.py`
  - `registry.py`
- Added first domain adapter package `spar_domain_physics`
- Extracted physics adapter Layer A, Layer B, and Layer C review logic
- Added `get_review_runtime()` so external consumers can wire the physics adapter into the generic kernel
- Verified current standalone state with `13` passing tests

### README repositioning

- Reframed the README around **claim-aware review** instead of physics-first framing
- Moved physics from entrypoint to proof case
- Added adoption ladder for dev/B2B readers:
  - Level 1 `Claim Check`
  - Level 2 `Maturity Labels`
  - Level 3 `Full SPAR`
- Added clearer product framing:
  - outputs can pass while claims drift
  - SPAR prevents unjustified confidence rather than promising truth
- Added first-screen product surface improvements:
  - badge row
  - tighter hero framing
  - clearer workflow mermaid showing ordinary review vs SPAR divergence
- Reworked early README sections into more scannable product blocks:
  - `Why Teams Use It`
  - compressed `Where It Fits`
  - feature-style `What SPAR Provides`
- Added a compact first-screen value grid under the hero:
  - catch claim drift
  - emit maturity state
  - adopt in layers
