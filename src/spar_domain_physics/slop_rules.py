"""Deterministic report-language rules for physics Layer B."""

from __future__ import annotations

from spar_framework.scoring import ReviewPolicy, default_policy

# Flat-severity phrases. Evolution path: assign per-phrase severity tiers
# (critical/high/medium/low) and use policy.slop_severity_weights for weighted
# sum scoring -- matching the AI-SLOP-Detector v3.7.x tiered model.
SLOP_PHRASES = [
    "groundbreaking",
    "revolutionary",
    "paradigm shift",
    "game changer",
    "unprecedented",
    "cutting-edge",
    "state-of-the-art",
    "novel approach",
    "significant contribution",
    "important step",
    "further research is needed",
    "opens up new possibilities",
    "paves the way",
    "could be beneficial",
]


def slop_check(text: str, policy: ReviewPolicy = default_policy) -> tuple[int, list[str]]:
    """Return a deterministic penalty and matched phrases.

    Adapters that need a domain-specific slop policy should bind the policy
    argument via functools.partial before passing to ReviewRuntime.slop_check.
    """
    lowered = text.lower()
    hits = [phrase for phrase in SLOP_PHRASES if phrase in lowered]
    return len(hits) * policy.slop_penalty_per_hit, hits
