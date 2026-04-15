# Changelog

## [Unreleased]

### External audit follow-up

- Hardened the `spar` CLI so unknown subcommands now return a structured `unknown_command` error instead of falling through to the legacy review path
- Synchronized the checked-in MICA archive and playbook with the current package release surface (`0.1.4`)
- Added regression coverage to keep the packaged version and MICA archive metadata aligned

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
