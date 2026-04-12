# Extraction Map

Current source repository:

- `D:/Sanctum/Flamehaven-TOE/flamehaven-toe-v4.5.0`

## Expected Moves

### Into `spar-framework`

- `src/toe/spar/result_types.py`
- `src/toe/spar/scoring.py`
- reusable parts of `src/toe/spar/spar_engine.py`
- `src/toe/spar/model_registry.py` split into generic registry model plus
  domain-owned seed data
- `src/toe/spar/runtime_context.py` generic review-composition pieces

### Remain Domain-Specific

- `src/toe/spar/ground_truth.py`
- `src/toe/spar/ground_truth_table.py`
- `src/toe/spar/ground_truth_matcher.py`
- `src/toe/spar/architecture_gaps.py`
- TOE-specific `layer_a_*`, `layer_b_*`, `layer_c_*` checks until generalized

### First adapter package in this repo

- `src/spar_domain_physics/registry_seed.py`
- `src/spar_domain_physics/ground_truth_table.py`
- `src/spar_domain_physics/architecture_gaps.py`
- `src/spar_domain_physics/layer_a.py`
- `src/spar_domain_physics/layer_b.py`
- `src/spar_domain_physics/layer_b_admissibility.py`
- `src/spar_domain_physics/layer_b_report_checks.py`
- `src/spar_domain_physics/layer_c.py`
- `src/spar_domain_physics/layer_c_foundations.py`
- `src/spar_domain_physics/layer_c_advanced.py`
- `src/spar_domain_physics/layer_c_foundation_helpers.py`
- `src/spar_domain_physics/matcher.py`
- `src/spar_domain_physics/runtime.py`

### Remain in TOE

- `src/toe/api/routers/infra.py`
- report/export builders
- TOE pipeline integration

## Extraction Constraint

The extracted core must not require `toe.*` imports.
