"""Deterministic report-language rules for physics Layer B."""

from __future__ import annotations

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


def slop_check(text: str) -> tuple[int, list[str]]:
    """Return a deterministic penalty and matched phrases."""

    lowered = text.lower()
    hits = [phrase for phrase in SLOP_PHRASES if phrase in lowered]
    return len(hits) * 10, hits
