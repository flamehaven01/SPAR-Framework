"""AI-friendly CLI for SPAR review workflows."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from .mica import discover_mica_runtime
from .schema_loader import load_schema
from .workflow import run_contextual_review

EXIT_OK = 0
EXIT_REVIEW_FAILURE = 1
EXIT_INPUT_ERROR = 2
EXIT_SYSTEM_ERROR = 3

SUBCOMMANDS = {"review", "explain", "discover", "schema", "example", "batch", "compare"}

# (package, subdir, filename) for adapter-specific schema targets.
# Entries here take precedence over the framework-level schema_loader.
_ADAPTER_SCHEMA_ROUTES: dict[str, dict[str, tuple[str, str, str]]] = {
    "ml": {
        "subject": ("spar_domain_ml", "schemas", "ml_subject.schema.json"),
    },
    "math": {
        "subject": ("spar_domain_math", "schemas", "math_subject.schema.json"),
    },
}

_ADAPTER_CHOICES = ["physics", "ml", "math", "generic"]


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
        choices=_ADAPTER_CHOICES,
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
        "--adapter",
        default="physics",
        choices=_ADAPTER_CHOICES,
        help="Adapter context for schema selection (default: physics)",
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
        choices=_ADAPTER_CHOICES,
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

    batch = subparsers.add_parser(
        "batch",
        help="Run SPAR review on a directory of subject files and emit a batch summary.",
    )
    batch.add_argument(
        "--adapter",
        default="physics",
        choices=_ADAPTER_CHOICES,
        help="Domain adapter to use for all subjects",
    )
    batch.add_argument("--subjects", required=True, help="Directory containing subject JSON files")
    batch.add_argument("--reports", help="Optional directory to write individual review JSONs")
    batch.add_argument("--report-text", default="", help="Shared report text for all subjects")
    batch.add_argument("--source", default="", help="Shared source value for all subjects")
    batch.add_argument("--gate", default="", help="Shared gate value for all subjects")
    batch.add_argument("--output-json", help="Optional path to write batch summary JSON")
    batch.add_argument("--output-md", help="Optional path to write batch summary Markdown")

    compare = subparsers.add_parser(
        "compare",
        help="Compare multiple SPAR review JSON files and emit a side-by-side summary.",
    )
    compare.add_argument("review_jsons", nargs="+", help="Paths to SPAR review JSON files")
    compare.add_argument("--output-json", help="Optional path to write comparison JSON")
    compare.add_argument("--output-md", help="Optional path to write comparison Markdown")

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
        if args.command == "batch":
            return _run_batch(args)
        if args.command == "compare":
            return _run_compare(args)
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
    # v0.6.0 (SPAR-001): positional <project> + --from-json heuristic added.
    # --subject-json kept as the canonical, strict-schema entry point (now optional;
    # validation lives in _run_review so legacy callers keep working unchanged).
    parser.add_argument(
        "project",
        nargs="?",
        default=None,
        help="Optional project root (alias for --project-root when --project-root is omitted).",
    )
    parser.add_argument("--subject-json", help="Path to subject JSON file (strict schema)")
    parser.add_argument(
        "--from-json",
        dest="from_json",
        help="Path to freeform JSON; keys are heuristically mapped to layer A/B/C surfaces. "
             "Mutually exclusive with --subject-json.",
    )
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
        choices=_ADAPTER_CHOICES,
        help="Domain adapter to use for review",
    )
    parser.add_argument("--output-json", help="Path to write JSON review result")


def _run_review(args: argparse.Namespace) -> int:
    # v0.6.0 (SPAR-001): resolve subject from one of three sources.
    subject_json = getattr(args, "subject_json", None)
    from_json = getattr(args, "from_json", None)
    if subject_json and from_json:
        return _emit_error(
            EXIT_INPUT_ERROR,
            "input_error",
            "--subject-json and --from-json are mutually exclusive; pick one.",
        )
    if not subject_json and not from_json:
        return _emit_error(
            EXIT_INPUT_ERROR,
            "input_error",
            "review requires --subject-json PATH or --from-json PATH.",
        )

    runtime = _get_runtime(args.adapter)
    report_text = args.report_text
    if args.report_file:
        report_text = Path(args.report_file).read_text(encoding="utf-8")

    derived_source = ""
    if subject_json:
        subject = _load_subject_payload(subject_json)
    else:
        subject, derived_report, derived_source = _heuristic_from_json(from_json)
        if derived_report and not report_text:
            report_text = derived_report

    source = args.source or derived_source

    # positional <project> is an alias for --project-root when the flag is unset
    positional_project = getattr(args, "project", None)
    project_root = args.project_root or positional_project

    result = run_contextual_review(
        runtime=runtime,
        subject=subject,
        source=source,
        gate=args.gate,
        report_text=report_text,
        project_root=project_root,
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
    adapter = getattr(args, "adapter", "physics")
    route = _ADAPTER_SCHEMA_ROUTES.get(adapter, {}).get(args.target)
    if route:
        from .package_data import load_packaged_json
        payload = load_packaged_json(*route)
    else:
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
    elif adapter == "math":
        payload = {"task": args.task, "subject": _math_example_subject(args.task)}
    else:
        from spar_domain_physics.ground_truth_table import GROUND_TRUTH
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


# v0.6.0 (SPAR-001): freeform-JSON heuristic key router.
# Keys that the framework needs to recognise are pulled out by substring match;
# everything else is preserved in subject as-is so adapter-specific keys keep working.
_REPORT_TEXT_KEYS = ("report_text", "report", "summary", "description", "narrative")
_SOURCE_KEYS = ("source", "background", "ground_truth", "ground_truth_source")


def _heuristic_from_json(path: str) -> tuple[dict[str, Any], str, str]:
    """Map freeform JSON to (subject, report_text, source).

    Rules:
      - Top-level key matching _REPORT_TEXT_KEYS (str value) -> report_text.
      - Top-level key matching _SOURCE_KEYS (str value) -> source.
      - Everything else (including unrecognised keys) is kept in subject.
      - {"subject": {...}} wrapper is unwrapped first so wrapped/raw both work.
    """
    raw = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise ValueError("--from-json payload must be a JSON object.")
    if isinstance(raw.get("subject"), dict):
        raw = dict(raw["subject"])

    report_text = ""
    source = ""
    subject: dict[str, Any] = {}
    for key, value in raw.items():
        lk = key.lower()
        if not report_text and isinstance(value, str) and lk in _REPORT_TEXT_KEYS:
            report_text = value
            continue
        if not source and isinstance(value, str) and lk in _SOURCE_KEYS:
            source = value
            continue
        subject[key] = value
    return subject, report_text, source


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


def _math_example_subject(task: str) -> dict[str, Any]:
    examples: dict[str, dict[str, Any]] = {
        "topology": {
            "theorem_id": "thm-1",
            "theorem_type": "theorem",
            "domain": "topology",
            "claim_profile": {
                "proof_claimed": True,
                "generality_claimed": True,
                "novelty_claimed": False,
            },
            "proof_surface": {
                "proof_status": "complete",
                "assumptions_explicit": True,
                "prior_art_cited": True,
            },
        },
        "combinatorics": {
            "theorem_id": "lemma-3",
            "theorem_type": "lemma",
            "domain": "combinatorics",
            "claim_profile": {
                "proof_claimed": True,
                "generality_claimed": False,
                "novelty_claimed": True,
            },
            "proof_surface": {
                "proof_status": "sketch",
                "assumptions_explicit": True,
                "prior_art_cited": False,
            },
        },
    }
    return examples.get(task, examples["topology"])


def _get_runtime(adapter: str):
    if adapter == "physics":
        from spar_domain_physics.runtime import get_review_runtime
        return get_review_runtime()
    if adapter == "ml":
        from spar_domain_ml.runtime import get_review_runtime as get_ml_runtime
        return get_ml_runtime()
    if adapter == "math":
        from spar_domain_math.runtime import get_review_runtime as get_math_runtime
        return get_math_runtime()
    if adapter == "generic":
        # v0.6.0 (SPAR-002): domain-agnostic adapter with minimal claim_profile.
        from spar_domain_generic.runtime import get_review_runtime as get_generic_runtime
        return get_generic_runtime()
    raise ValueError(f"Unsupported adapter: {adapter}")


def _run_batch(args: argparse.Namespace) -> int:
    from .harness import run_batch

    subjects_dir = Path(args.subjects)
    if not subjects_dir.is_dir():
        return _emit_error(EXIT_INPUT_ERROR, "input_error",
                           f"--subjects must be a directory: {subjects_dir}")

    subject_paths = sorted(subjects_dir.glob("*.json"))
    if not subject_paths:
        return _emit_error(EXIT_INPUT_ERROR, "input_error",
                           f"No JSON files found in {subjects_dir}")

    reports_dir = None
    if args.reports:
        reports_dir = Path(args.reports)
        reports_dir.mkdir(parents=True, exist_ok=True)

    summary = run_batch(
        runtime=_get_runtime(args.adapter),
        adapter=args.adapter,
        subject_paths=subject_paths,
        report_text=args.report_text,
        source=args.source,
        gate=args.gate,
        reports_dir=reports_dir,
    )

    encoded = json.dumps(summary.to_dict(), indent=2)
    if args.output_json:
        Path(args.output_json).write_text(encoded, encoding="utf-8")
    print(encoded)

    if args.output_md:
        from .report import batch_summary_to_markdown
        Path(args.output_md).write_text(batch_summary_to_markdown(summary), encoding="utf-8")

    return EXIT_OK


def _run_compare(args: argparse.Namespace) -> int:
    from .harness import compare_reviews

    review_paths = [Path(p) for p in args.review_jsons]
    comparisons = compare_reviews(review_paths)

    payload = {"compared": len(comparisons), "reviews": comparisons}
    encoded = json.dumps(payload, indent=2)
    if args.output_json:
        Path(args.output_json).write_text(encoded, encoding="utf-8")
    print(encoded)

    if args.output_md:
        from .report import compare_reviews_to_markdown
        Path(args.output_md).write_text(compare_reviews_to_markdown(comparisons), encoding="utf-8")

    return EXIT_OK


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
