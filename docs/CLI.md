# CLI

SPAR ships with an AI-friendly CLI contract. The goal is not shell convenience first. The goal is **predictable, machine-readable review behavior** with safe defaults.

## Entry points

```bash
spar review
spar explain
spar discover
spar schema
spar example
```

Legacy compatibility is still available through:

```bash
spar-context-review
```

That entry point maps to the older flat argument surface and remains for compatibility with existing automation.

## Design rules

- Default output is JSON
- Review execution and review explanation are separate commands
- Context is optional, but missing context becomes `CANNOT_CHECK`, not silent inference
- `public` LEDA payloads are not ingestible by SPAR
- Review results persist only safe `context_summary`, never raw MICA or LEDA payloads

## Commands

### `spar review`

Run a review and emit machine-readable JSON.

```bash
spar review \
  --subject-json subject.json \
  --source "flat minkowski" \
  --gate PASS \
  --project-root /path/to/project \
  --leda-injection reports/leda_injection.yaml \
  --output-json review.json
```

Important flags:

- `--subject-json`: required subject payload
- `--source`: declared source or background
- `--gate`: declared gate status
- `--report-text`: inline report text
- `--report-file`: report text file
- `--project-root`: MICA auto-discovery root
- `--mica-context`: explicit MICA context path
- `--leda-injection`: optional LEDA injection YAML
- `--leda-profile`: `internal`, `restricted`, `public` (default: `restricted`)
- `--adapter`: current value `physics`
- `--output-json`: optional file sink

### `spar explain`

Summarize an existing review JSON.

```bash
spar explain --review-json review.json --format text
```

Formats:

- `json`
- `text`

### `spar discover`

Discover contextual runtime state for a project root.

```bash
spar discover --project-root /path/to/project --adapter physics
```

This reports:

- adapter
- MICA runtime state
- supported LEDA profiles
- recommended LEDA profile

### `spar schema`

Emit schema guidance for subjects, results, or contextual inputs.

```bash
spar schema subject
spar schema result
spar schema context
spar schema subject --output-json subject-schema.json
```

These payloads come from packaged JSON schema artifacts under `src/spar_framework/schemas/`, not from ad hoc in-code dicts.

### `spar example`

Emit example subject payloads.

```bash
spar example --source flat
spar example --source ads --output-json ads.json
```

## Exit codes

| Code | Meaning |
|---|---|
| `0` | Review succeeded and verdict is acceptable for CLI success (`ACCEPT`, `MINOR_REVISION`) |
| `1` | Review completed, but verdict is non-passing (`MAJOR_REVISION`, `REJECT`) |
| `2` | Input or schema error |
| `3` | System/runtime error |

## Security defaults

- Default LEDA profile is `restricted`
- `public` LEDA payloads are not ingested into review logic
- Raw evidence, file paths, DB paths, and detailed weakness surfaces are not persisted into result payloads

See [SECURITY_MODEL.md](SECURITY_MODEL.md) for the full model.
