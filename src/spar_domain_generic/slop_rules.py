"""Deterministic report-language slop rules for the generic adapter."""

from __future__ import annotations

from spar_framework.scoring import ReviewPolicy, default_policy

SLOP_PHRASES = [
    "clearly",
    "obviously",
    "trivially",
    "needless to say",
    "it goes without saying",
    "groundbreaking",
    "revolutionary",
    "paradigm shift",
    "world-class",
    "state-of-the-art",
]


def slop_check(text: str, policy: ReviewPolicy = default_policy) -> tuple[int, list[str]]:
    """Return a deterministic slop penalty and matched phrases."""
    if not text:
        return 0, []
    lowered = text.lower()
    hits = [phrase for phrase in SLOP_PHRASES if phrase in lowered]
    return len(hits) * policy.slop_penalty_per_hit, hits
