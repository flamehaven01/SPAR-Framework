"""Source-string matching helpers for physics analytical anchors."""

from __future__ import annotations

_SOURCE_MATCH_RULES: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("flat", ("flat", "minkowski")),
    ("schwarzschild_dilaton", ("schwarzschild", "dilaton")),
    ("schwarzschild", ("schwarzschild", "black hole")),
    ("de_sitter", ("de_sitter", "desitter", "de sitter")),
    ("wzw", ("wzw", "wess-zumino")),
    ("linear_dilaton", ("linear_dilaton", "dilaton")),
    ("ads", ("ads", "anti-de sitter", "anti_de_sitter")),
)


def _contains_all(source: str, needles: tuple[str, ...]) -> bool:
    return all(needle in source for needle in needles)


def _match_wzw_special_case(source: str) -> str | None:
    if "s3" in source and "ads" not in source:
        return "wzw"
    return None


def _match_linear_dilaton_special_case(source: str) -> str | None:
    if "dilaton" in source and "ads" not in source:
        return "linear_dilaton"
    return None


def match_ground_truth_source(source: str) -> str | None:
    normalized = source.lower()
    for key, aliases in _SOURCE_MATCH_RULES:
        if key == "schwarzschild_dilaton":
            if _contains_all(normalized, aliases):
                return key
            continue
        if any(alias in normalized for alias in aliases):
            if key == "wzw":
                return _match_wzw_special_case(normalized) or key
            if key == "linear_dilaton":
                result = _match_linear_dilaton_special_case(normalized)
                if result is not None:
                    return result
                continue
            return key
    return _match_wzw_special_case(normalized) or _match_linear_dilaton_special_case(normalized)
