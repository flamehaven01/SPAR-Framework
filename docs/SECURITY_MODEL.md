# Security Model

SPAR review context can be more sensitive than source code.

Why:

- it may expose known weakness surfaces
- it can reveal maturity gaps directly
- it may encode override zones and review blind spots

That makes raw review context a higher-risk artifact than many normal logs.

## Rule 1: Do not persist raw LEDA context in review results

`ReviewResult` should carry only a **safe context summary**.

This repository now follows that rule:

- raw `LEDA` payload may be supplied to `run_review()`
- only `context_summary` is persisted in the result surface
- raw evidence and sensitive file paths are not copied into `ReviewResult`

## Rule 2: Use redaction profiles

LEDA payloads should be emitted with an explicit profile:

- `internal`
- `restricted`
- `public`

Recommended defaults:

- internal pipeline ingestion: `restricted`
- human-reviewed internal diagnostics: `internal`
- any outward-facing artifact: `public`

Public payloads are **not** trusted review inputs.

If a `LEDA` payload is marked `public`, SPAR should treat it as a publication-safe summary and ignore it for Layer B/Layer C contextual inference.

## Rule 3: Keep weakness surfaces out of public repos

Examples of sensitive fields:

- project root paths
- config paths
- history database paths
- raw evidence lists
- detailed override maps

These should not be published unless there is a deliberate internal reason.

## Rule 4: Separate truth surfaces

- `MICA` is memory truth
- `LEDA` is code truth
- `SPAR` is admissibility truth

Do not let one engine silently impersonate another.

## Operational Recommendation

If a team needs strong internal review but safe external reporting:

1. emit `LEDA` as `internal` or `restricted`
2. ingest it into SPAR
3. expose only SPAR review result + safe summary outside the boundary

That keeps the review useful without turning the system into a map of its own weaknesses.
