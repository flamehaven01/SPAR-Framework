"""AI-friendly CLI for SPAR review workflows."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from spar_domain_physics.ground_truth_table import GROUND_TRUTH
from spar_domain_physics.runtime import get_review_runtime

from .mica import discover_mica_runtime
from .schema_loader import load_schema
from .workflow import run_contextual_review

EXIT_OK = 0
EXIT_REVIEW_FAILURE = 1
EXIT_INPUT_ERROR = 2
EXIT_SYSTEM_ERROR = 3

SUBCOMMANDS = {"review", "explain", "discover", "schema", "example"}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="spar",
        description="SPAR CLI for claim-aware review of mathematical and physics-grade models.",
    )
    subparsers = parser.add_subparsers(dest="command")

    review = subparsers.add_parser(
        "review",
        help="Run contextual SPAR review and emit machine-readable JSON.",
    )
    _add_review_args(review)

    explain = subparsers.add_parser(
        "explain",
        help="Summarize an existing SPAR review result.",
    )
    explain.add_argument("--review-json", required=True, help="Path to SPAR review JSON")
    explain.add_argument(
        "--format",
        choices=["json", "text"],
        default="json",
        help="Output format for the explanation summary",
    )

    discover = subparsers.add_parser(
        "discover",
        help="Discover adapter and contextual inputs for a project root.",
    )
    discover.add_argument("--project-root", required=True, help="Project root to inspect")
    discover.add_argument(
        "--adapter",
        default="physics",
        choices=["physics", "ml"],
        help="Adapter to use for discovery",
    )

    schema = subparsers.add_parser(
        "schema",
        help="Emit machine-readable schema guidance for SPAR inputs and outputs.",
    )
    schema.add_argument(
        "target",
        choices=["subject", "result", "context"],
        help="Schema target to emit",
    )
    schema.add_argument(
        "--output-json",
        help="Optional path to write the schema JSON payload",
    )

    example = subparsers.add_parser(
        "example",
        help="Emit example subject payloads for the selected adapter.",
    )
    example.add_argument(
        "--adapter",
        default="physics",
        choices=["physics", "ml"],
        help="Adapter to generate example for",
    )
    example.add_argument(
        "--source",
        default="flat",
        help="Ground-truth source key for physics adapter (e.g. flat, ads, linear_dilaton)",
    )
    example.add_argument(
        "--task",
        default="image_classification",
        help="Task profile for ml adapter (e.g. image_classification, text_classification)",
    )
    example.add_argument(
        "--output-json",
        help="Optional path to write the example JSON payload",
    )

    return parser


def legacy_main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="spar-context-review",
        description="Run SPAR contextual review with optional MICA and LEDA inputs.",
    )
    _add_review_args(parser)
    args = parser.parse_args(argv)
    return _run_review(args)


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if not argv or argv[0].startswith("-"):
        return legacy_main(argv)
    if argv[0] not in SUBCOMMANDS:
        return _emit_error(
            EXIT_INPUT_ERROR,
            "unknown_command",
            f"Unsupported command: {argv[0]}",
        )

    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        if args.command == "review":
            return _run_review(args)
        if args.command == "explain":
            return _run_explain(args)
        if args.command == "discover":
            return _run_discover(args)
        if args.command == "schema":
            return _run_schema(args)
        if args.command == "example":
            return _run_example(args)
        return _emit_error(
            EXIT_INPUT_ERROR,
            "unknown_command",
            f"Unsupported command: {args.command}",
        )
    except (FileNotFoundError, json.JSONDecodeError, ValueError) as exc:
        return _emit_error(EXIT_INPUT_ERROR, "input_error", str(exc))
    except Exception as exc:  # pragma: no cover - last-resort system boundary
        return _emit_error(EXIT_SYSTEM_ERROR, "system_error", str(exc))


def _add_review_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--subject-json", required=True, help="Path to subject JSON file")
    parser.add_argument("--source", default="", help="Declared source/background name")
    parser.add_argument("--gate", default="", help="Declared gate status")
    parser.add_argument("--report-text", default="", help="Inline report text")
    parser.add_argument("--report-file", help="Path to report text file")
    parser.add_argument(
        "--project-root",
        help="Project root for MICA auto-discovery when --mica-context is not provided",
    )
    parser.add_argument("--mica-context", help="Path to mica.yaml or MICA context YAML")
    parser.add_argument("--leda-injection", help="Path to LEDA injection YAML")
    parser.add_argument(
        "--leda-profile",
        choices=["internal", "restricted", "public"],
        default="restricted",
        help="Redaction profile for LEDA ingestion (default: restricted)",
    )
    parser.add_argument(
        "--adapter",
        default="physics",
        choices=["physics", "ml"],
        help="Domain adapter to use for review",
    )
    parser.add_argument("--output-json", help="Path to write JSON review result")


def _run_review(args: argparse.Namespace) -> int:
    runtime = _get_runtime(args.adapter)
    subject = _load_subject_payload(args.subject_json)
    report_text = args.report_text
    if args.report_file:
        report_text = Path(args.report_file).read_text(encoding="utf-8")

    result = run_contextual_review(
        runtime=runtime,
        subject=subject,
        source=args.source,
        gate=args.gate,
        report_text=report_text,
        project_root=args.project_root,
        mica_context_path=args.mica_context,
        leda_injection_path=args.leda_injection,
        leda_profile=args.leda_profile,
    )

    payload = result.to_dict()
    encoded = json.dumps(payload, indent=2)
    if args.output_json:
        Path(args.output_json).write_text(encoded, encoding="utf-8")
    print(encoded)

    if result.verdict in {"ACCEPT", "MINOR_REVISION"}:
        return EXIT_OK
    return EXIT_REVIEW_FAILURE


def _run_explain(args: argparse.Namespace) -> int:
    payload = json.loads(Path(args.review_json).read_text(encoding="utf-8"))
    context_summary = payload.get("context_summary") or {}
    summary = {
        "verdict": payload.get("verdict"),
        "score": payload.get("score"),
        "grade": payload.get("grade"),
        "layer_a_anomalies": sum(
            1 for item in payload.get("layer_a", []) if item.get("status") == "ANOMALY"
        ),
        "layer_b_flags": [
            item["check_id"]
            for item in payload.get("layer_b", [])
            if item.get("status") not in {"PASS", "CONSISTENT", "GENUINE"}
        ],
        "layer_c_flags": [
            item["check_id"]
            for item in payload.get("layer_c", [])
            if item.get("status") not in {"PASS", "CONSISTENT", "GENUINE"}
        ],
        "framework_declared_flags": [
            item["check_id"]
            for item in payload.get("framework_declared", [])
            if item.get("status") not in {"DECLARED_CLOSED"}
        ],
        "context_sources": context_summary.get("sources", []),
    }

    if args.format == "text":
        lines = [
            f"verdict: {summary['verdict']}",
            f"score: {summary['score']}",
            f"grade: {summary['grade']}",
            f"layer_a_anomalies: {summary['layer_a_anomalies']}",
            f"layer_b_flags: {', '.join(summary['layer_b_flags']) or 'none'}",
            f"layer_c_flags: {', '.join(summary['layer_c_flags']) or 'none'}",
            f"framework_declared_flags: {', '.join(summary['framework_declared_flags']) or 'none'}",
            f"context_sources: {', '.join(summary['context_sources']) or 'none'}",
        ]
        print("\n".join(lines))
    else:
        print(json.dumps(summary, indent=2))
    return EXIT_OK


def _run_discover(args: argparse.Namespace) -> int:
    mica = discover_mica_runtime(args.project_root)
    payload = {
        "adapter": args.adapter,
        "project_root": str(Path(args.project_root).resolve()),
        "mica": mica,
        "leda": {
            "supported_profiles": ["internal", "restricted", "public"],
            "recommended_profile": "restricted",
            "public_ingestible_by_spar": False,
        },
    }
    print(json.dumps(payload, indent=2))
    return EXIT_OK


def _run_schema(args: argparse.Namespace) -> int:
    payload = load_schema(args.target)
    encoded = json.dumps(payload, indent=2)
    if args.output_json:
        Path(args.output_json).write_text(encoded, encoding="utf-8")
    print(encoded)
    return EXIT_OK


def _run_example(args: argparse.Namespace) -> int:
    adapter = getattr(args, "adapter", "physics")
    if adapter == "ml":
        payload = {"task": args.task, "subject": _ml_example_subject(args.task)}
    else:
        source = args.source
        if source not in GROUND_TRUTH:
            return _emit_error(EXIT_INPUT_ERROR, "input_error",
                               f"Unknown source '{source}'. Valid: {sorted(GROUND_TRUTH.keys())}")
        payload = {"source": source, "subject": _example_subject(source)}
    encoded = json.dumps(payload, indent=2)
    if args.output_json:
        Path(args.output_json).write_text(encoded, encoding="utf-8")
    print(encoded)
    return EXIT_OK


def _example_subject(source: str) -> dict[str, Any]:
    examples: dict[str, dict[str, Any]] = {
        "flat": {
            "beta_G_norm": 0.0,
            "beta_B_norm": 0.0,
            "beta_Phi_norm": 0.0,
            "sidrce_omega": 1.0,
            "eft_m_kk_gev": 1.0e16,
            "ricci_norm": 0.02,
        },
        "de_sitter": {
            "beta_G_norm": 0.0,
            "sidrce_omega": 0.2,
            "eft_m_kk_gev": 1.0e16,
            "ricci_norm": 0.02,
        },
        "ads": {
            "beta_G_norm": 0.0,
            "beta_B_norm": 0.0,
            "beta_Phi_norm": 0.0,
            "sidrce_omega": 0.8,
            "eft_m_kk_gev": 1.0e16,
            "ricci_norm": 0.02,
        },
    }
    return examples.get(source, {"beta_G_norm": 0.0})


def _load_subject_payload(path: str) -> dict[str, Any]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if isinstance(payload, dict) and isinstance(payload.get("subject"), dict):
        return payload["subject"]
    if isinstance(payload, dict):
        return payload
    raise ValueError("Subject JSON must be an object or an example wrapper with a 'subject' object.")


def _ml_example_subject(task: str) -> dict[str, Any]:
    examples: dict[str, dict[str, Any]] = {
        "image_classification": {
            "task_family": "image_classification",
            "dataset": "ImageNet-1k",
            "split": "val",
            "metric_name": "top1_accuracy",
            "metric_value": 0.912,
            "metric_direction": "higher_is_better",
            "baseline_name": "prior_sota",
            "baseline_value": 0.905,
            "claim_profile": {
                "sota_claimed": True,
                "generalization_claimed": True,
                "robustness_claimed": False,
            },
            "reproducibility": {
                "seed_present": True,
                "dataset_version_present": True,
                "config_hash_present": True,
            },
            "evaluation_scope": {
                "ood_evaluated": False,
                "robustness_evaluated": False,
                "claim_scope_restricted": True,
            },
        },
        "text_classification": {
            "task_family": "text_classification",
            "dataset": "GLUE",
            "split": "dev",
            "metric_name": "accuracy",
            "metric_value": 0.921,
            "metric_direction": "higher_is_better",
            "baseline_name": "bert_base",
            "baseline_value": 0.847,
            "claim_profile": {
                "sota_claimed": True,
                "generalization_claimed": False,
                "robustness_claimed": False,
            },
            "reproducibility": {
                "seed_present": True,
                "dataset_version_present": True,
                "config_hash_present": False,
            },
            "evaluation_scope": {
                "ood_evaluated": False,
                "robustness_evaluated": False,
                "claim_scope_restricted": False,
            },
        },
    }
    return examples.get(task, examples["image_classification"])


def _get_runtime(adapter: str):
    if adapter == "physics":
        return get_review_runtime()
    if adapter == "ml":
        from spar_domain_ml.runtime import get_review_runtime as get_ml_runtime
        return get_ml_runtime()
    raise ValueError(f"Unsupported adapter: {adapter}")


def _emit_error(code: int, error: str, detail: str) -> int:
    print(
        json.dumps(
            {
                "ok": False,
                "error": error,
                "detail": detail,
                "exit_code": code,
            },
            indent=2,
        )
    )
    return code


if __name__ == "__main__":
    raise SystemExit(main())
