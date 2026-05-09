"""Deterministic report-language slop rules for the ML adapter."""

from __future__ import annotations

from spar_framework.scoring import ReviewPolicy, default_policy

SLOP_PHRASES = [
    "groundbreaking",
    "revolutionary",
    "paradigm shift",
    "unprecedented",
    "cutting-edge",
    "state-of-the-art",
    "novel approach",
    "significant contribution",
    "dramatically outperforms",
    "massively improves",
    "further research is needed",
    "opens up new possibilities",
]


def slop_check(text: str, policy: ReviewPolicy = default_policy) -> tuple[int, list[str]]:
    """Return a deterministic slop penalty and matched phrases."""
    lowered = text.lower()
    hits = [phrase for phrase in SLOP_PHRASES if phrase in lowered]
    return len(hits) * policy.slop_penalty_per_hit, hits
