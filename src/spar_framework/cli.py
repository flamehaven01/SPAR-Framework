"""CLI entrypoint for contextual SPAR review."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from spar_domain_physics.runtime import get_review_runtime

from .workflow import run_contextual_review


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run SPAR contextual review with optional MICA and LEDA inputs."
    )
    parser.add_argument("--subject-json", required=True, help="Path to subject JSON file")
    parser.add_argument("--source", default="", help="Declared source/background name")
    parser.add_argument("--gate", default="", help="Declared gate status")
    parser.add_argument("--report-text", default="", help="Inline report text")
    parser.add_argument("--report-file", help="Path to report text file")
    parser.add_argument("--mica-context", help="Path to mica.yaml or MICA context YAML")
    parser.add_argument("--leda-injection", help="Path to LEDA injection YAML")
    parser.add_argument(
        "--leda-profile",
        choices=["internal", "restricted", "public"],
        default="restricted",
        help="Redaction profile for LEDA ingestion (default: restricted)",
    )
    parser.add_argument("--output-json", help="Path to write JSON review result")
    return parser


def main() -> int:
    args = _build_parser().parse_args()
    subject = json.loads(Path(args.subject_json).read_text(encoding="utf-8"))
    report_text = args.report_text
    if args.report_file:
        report_text = Path(args.report_file).read_text(encoding="utf-8")

    result = run_contextual_review(
        runtime=get_review_runtime(),
        subject=subject,
        source=args.source,
        gate=args.gate,
        report_text=report_text,
        mica_context_path=args.mica_context,
        leda_injection_path=args.leda_injection,
        leda_profile=args.leda_profile,
    )

    payload = result.to_dict()
    encoded = json.dumps(payload, indent=2)
    if args.output_json:
        Path(args.output_json).write_text(encoded, encoding="utf-8")
        print(f"[+] SPAR review saved to {Path(args.output_json).resolve()}")
    else:
        print(encoded)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
