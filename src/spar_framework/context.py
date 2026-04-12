"""Context ingestion and redaction helpers for SPAR workflows."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

import yaml


def load_mica_context(path: str | Path) -> dict[str, Any]:
    """Load MICA context from YAML."""
    return _load_yaml(path)


def load_leda_injection(
    path: str | Path,
    *,
    profile: str = "restricted",
) -> dict[str, Any]:
    """Load LEDA injection payload and optionally redact it further."""
    payload = _load_yaml(path)
    return redact_leda_payload(payload, profile=profile)


def redact_leda_payload(payload: dict[str, Any], *, profile: str = "restricted") -> dict[str, Any]:
    """Redact LEDA payload to a safe review-context surface."""
    if profile not in {"internal", "restricted", "public"}:
        raise ValueError("profile must be one of: internal, restricted, public")
    original_profile = (
        payload.get("security", {}).get("classification")
        if isinstance(payload.get("security"), dict)
        else None
    )
    effective_profile = _more_restrictive_profile(original_profile, profile)
    if effective_profile == "internal":
        payload.setdefault("security", {})
        payload["security"]["classification"] = "internal"
        payload["security"]["ingestible_by_spar"] = True
        return payload

    redacted = deepcopy(payload)
    redacted.setdefault("security", {})
    redacted["security"]["original_classification"] = original_profile
    redacted["security"]["classification"] = effective_profile
    redacted["security"]["shareable"] = effective_profile == "public"
    redacted["security"]["ingestible_by_spar"] = effective_profile != "public"
    project = redacted.get("project", {})
    project.pop("root", None)
    source = redacted.get("source", {})
    source["config_path"] = None
    source["history_db"] = None

    if effective_profile == "restricted":
        for risk in redacted.get("claim_risk", []):
            risk.pop("evidence", None)
        return redacted

    total_risks = len(redacted.get("claim_risk", []))
    high_risks = sum(
        1 for risk in redacted.get("claim_risk", []) if risk.get("severity") == "high"
    )
    redacted["claim_risk"] = []
    redacted["claim_risk_summary"] = {
        "total": total_risks,
        "high_severity": high_risks,
    }
    if "analysis" in redacted:
        redacted["analysis"] = {
            "mode": redacted["analysis"].get("mode"),
            "status": redacted["analysis"].get("status"),
        }
    if "calibration" in redacted:
        redacted["calibration"] = {
            "status": redacted["calibration"].get("status"),
            "history_records": redacted["calibration"].get("history_records", 0),
        }
    if "maturity" in redacted:
        redacted["maturity"] = {
            "suggested_current": redacted["maturity"].get("suggested_current")
        }
    if "overrides" in redacted:
        count = redacted["overrides"].get("configured_override_count", 0)
        redacted["overrides"] = {"configured_override_count": count}
    if "spar_review_hints" in redacted:
        redacted["spar_review_hints"] = {
            "preferred_layers": [],
            "registry_candidates": [],
            "notes": ["Public LEDA payloads are publication-safe summaries, not review inputs."],
        }
    return redacted


def summarize_review_context(
    *,
    memory_context: dict[str, Any] | None = None,
    leda_injection: dict[str, Any] | None = None,
) -> dict[str, Any] | None:
    """Return a safe summary for persistence inside ReviewResult."""
    if not memory_context and not leda_injection:
        return None

    summary: dict[str, Any] = {"sources": []}
    if memory_context:
        summary["sources"].append("mica")
        summary["mica"] = {
            "mode": memory_context.get("mode") or memory_context.get("invocation_mode"),
            "pattern": memory_context.get("pattern"),
            "project": memory_context.get("project", {}).get("name")
            if isinstance(memory_context.get("project"), dict)
            else memory_context.get("project_name"),
        }
    if leda_injection:
        summary["sources"].append("leda")
        classification = leda_injection.get("security", {}).get("classification")
        summary["leda"] = {
            "analyzer": leda_injection.get("source", {}).get("analyzer"),
            "generated_at": leda_injection.get("source", {}).get("generated_at"),
            "classification": classification,
            "claim_risk_count": len(leda_injection.get("claim_risk", [])),
            "suggested_maturity": leda_injection.get("maturity", {}).get("suggested_current"),
            "preferred_layers": leda_injection.get("spar_review_hints", {}).get("preferred_layers", []),
        }
        if classification == "internal":
            summary["leda"]["claim_risk_ids"] = [
                item.get("id") for item in leda_injection.get("claim_risk", [])
            ]
    return summary


def _load_yaml(path: str | Path) -> dict[str, Any]:
    loaded = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    if not isinstance(loaded, dict):
        raise ValueError(f"Expected mapping payload at {path}")
    return loaded


def _more_restrictive_profile(
    original_profile: str | None,
    requested_profile: str,
) -> str:
    order = {"internal": 0, "restricted": 1, "public": 2}
    normalized_original = original_profile if original_profile in order else "internal"
    return max(normalized_original, requested_profile, key=lambda value: order[value])
