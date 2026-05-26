# ReviewRuntime construction guide

`ReviewRuntime` is the dependency bundle SPAR's core engine consumes to run a
single review. Adapters (`spar_domain_physics`, `spar_domain_ml`,
`spar_domain_math`, `spar_domain_generic`) build one of these at import time
and expose it via `get_review_runtime()`. You can also build your own.

## Minimal runtime

The smallest valid `ReviewRuntime` provides only the three layer builders.
Registry snapshots, framework-declared limitations, and slop-checking are all
optional.

```python
from spar_framework.engine import ReviewRuntime, run_review
from spar_framework.result_types import CheckResult


def build_layer_a(*, subject, source="", gate="", params=None, context=None):
    return [CheckResult("A1", "stub anchor", "PASS", "ok")]


def build_layer_b(*, subject, source="", gate="", report_text="", context=None):
    return []  # empty layer is legal


def build_layer_c(*, subject, source="", gate="", params=None, context=None):
    return []


runtime = ReviewRuntime(
    build_layer_a=build_layer_a,
    build_layer_b=build_layer_b,
    build_layer_c=build_layer_c,
)
result = run_review(runtime=runtime, subject={})
```

## Full runtime

```python
from spar_framework.engine import ReviewRuntime

runtime = ReviewRuntime(
    build_layer_a=build_layer_a,
    build_layer_b=build_layer_b,
    build_layer_c=build_layer_c,
    build_framework_declared=build_framework_declared,   # optional
    build_model_registry_snapshot=lambda: {...},         # optional
    build_gap_registry_snapshot=lambda: {...},           # optional
    slop_check=slop_check,                               # optional
)
```

## Layer builder signatures

All three layer builders are called with keyword arguments. They must accept
unknown keyword arguments without failing — adding `**kwargs` or accepting the
documented kwargs explicitly are both fine.

```text
build_layer_a(*, subject, source, gate, params, context) -> list[CheckResult]
build_layer_b(*, subject, source, gate, report_text, context) -> list[CheckResult]
build_layer_c(*, subject, source, gate, params, context) -> list[CheckResult]
```

`context` is `{"memory_context": ..., "leda_injection": ...}` when MICA/LEDA
sources are loaded; otherwise both keys are `None`.

## Where to find a complete example

`src/spar_domain_generic/` is the smallest production adapter and the
recommended template for building a new domain adapter from scratch. It
defines all six layer/registry callables plus `slop_check`.

## Policy overrides

The default scoring policy is loaded from
`spar_framework/policies/review_policy.v1.json`. To override it:

```bash
export SPAR_POLICY_PATH=/path/to/custom_policy.json
spar review --adapter generic --subject-json subject.json
```

Precedence: `$SPAR_POLICY_PATH` (if set and readable) > packaged default.
The path is read once per process and cached.
