"""Generic domain-agnostic adapter for the SPAR framework.

This adapter is intentionally minimal. It applies claim-anchor and language
checks that do not assume a specific domain schema (no proof_status, no
metric_value, no beta_*). It is intended as:
  (a) a starting template for new domain adapters,
  (b) a fallback when a user wants to run SPAR against freeform input
      mapped through `spar review --from-json` (SPAR-001) without committing
      to physics / ml / math adapter schemas.

The generic surface is:
  subject = {
    "claim_id": str,          # optional identifier
    "claim_profile": {
        "claim_made": bool,           # any claim at all?
        "evidence_cited": bool,       # is supporting evidence referenced?
        "scope_bounded": bool,        # are claim limits stated?
    },
  }
"""
