"""Deterministic report-language slop rules for the math adapter."""

from __future__ import annotations

from spar_framework.scoring import ReviewPolicy, default_policy

SLOP_PHRASES = [
    "trivially follows",
    "it is easy to see",
    "clearly",
    "obviously",
    "straightforward",
    "well-known",
    "the proof is left to the reader",
    "groundbreaking",
    "revolutionary",
    "paradigm shift",
    "novel approach",
]


def slop_check(text: str, policy: ReviewPolicy = default_policy) -> tuple[int, list[str]]:
    """Return a deterministic slop penalty and matched phrases."""
    lowered = text.lower()
    hits = [phrase for phrase in SLOP_PHRASES if phrase in lowered]
    return len(hits) * policy.slop_penalty_per_hit, hits
