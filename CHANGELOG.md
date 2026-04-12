# Changelog

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
