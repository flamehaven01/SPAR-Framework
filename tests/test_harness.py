"""Regression tests for the batch harness and compare surface."""

from __future__ import annotations

import json


def _ml_subject(**overrides):
    subject = {
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
            "generalization_claimed": False,
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
            "claim_scope_restricted": False,
        },
    }
    subject.update(overrides)
    return subject


def _math_subject(**overrides):
    subject = {
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
    }
    subject.update(overrides)
    return subject


# ---------------------------------------------------------------------------
# harness.run_batch
# ---------------------------------------------------------------------------


def test_run_batch_counts_subjects(tmp_path):
    from spar_domain_ml.runtime import get_review_runtime
    from spar_framework.harness import run_batch

    subjects_dir = tmp_path / "subjects"
    subjects_dir.mkdir()
    for i in range(3):
        (subjects_dir / f"s{i}.json").write_text(json.dumps(_ml_subject()), encoding="utf-8")

    summary = run_batch(
        runtime=get_review_runtime(),
        adapter="ml",
        subject_paths=sorted(subjects_dir.glob("*.json")),
    )
    assert summary.count == 3
    assert summary.adapter == "ml"


def test_run_batch_verdict_distribution_sums_to_count(tmp_path):
    from spar_domain_ml.runtime import get_review_runtime
    from spar_framework.harness import run_batch

    subjects_dir = tmp_path / "subjects"
    subjects_dir.mkdir()
    for i in range(4):
        (subjects_dir / f"s{i}.json").write_text(json.dumps(_ml_subject()), encoding="utf-8")

    summary = run_batch(
        runtime=get_review_runtime(),
        adapter="ml",
        subject_paths=sorted(subjects_dir.glob("*.json")),
    )
    assert sum(summary.verdicts.values()) == summary.count


def test_run_batch_metric_ranges(tmp_path):
    from spar_domain_ml.runtime import get_review_runtime
    from spar_framework.harness import run_batch

    subjects_dir = tmp_path / "subjects"
    subjects_dir.mkdir()
    (subjects_dir / "s1.json").write_text(json.dumps(_ml_subject()), encoding="utf-8")

    summary = run_batch(
        runtime=get_review_runtime(),
        adapter="ml",
        subject_paths=list(subjects_dir.glob("*.json")),
    )
    assert summary.mean_claim_drift >= 0
    assert 0.0 <= summary.mean_coverage_rate <= 1.0
    assert 0.0 <= summary.cannot_check_rate <= 1.0
    assert 0.0 <= summary.framework_declared_rate <= 1.0


def test_run_batch_writes_individual_reviews(tmp_path):
    from spar_domain_ml.runtime import get_review_runtime
    from spar_framework.harness import run_batch

    subjects_dir = tmp_path / "subjects"
    subjects_dir.mkdir()
    (subjects_dir / "subject_a.json").write_text(json.dumps(_ml_subject()), encoding="utf-8")
    reports_dir = tmp_path / "reports"

    run_batch(
        runtime=get_review_runtime(),
        adapter="ml",
        subject_paths=list(subjects_dir.glob("*.json")),
        reports_dir=reports_dir,
    )
    review_files = list(reports_dir.glob("*_review.json"))
    assert len(review_files) == 1
    payload = json.loads(review_files[0].read_text(encoding="utf-8"))
    assert payload["verdict"] in {"ACCEPT", "MINOR_REVISION", "MAJOR_REVISION", "REJECT"}


def test_run_batch_empty_returns_zero_count():
    from spar_framework.harness import _compute_summary

    summary = _compute_summary("ml", [])
    assert summary.count == 0
    assert summary.verdicts == {}
    assert summary.top_flags == []


def test_run_batch_math_adapter(tmp_path):
    from spar_domain_math.runtime import get_review_runtime
    from spar_framework.harness import run_batch

    subjects_dir = tmp_path / "subjects"
    subjects_dir.mkdir()
    for i in range(2):
        (subjects_dir / f"m{i}.json").write_text(json.dumps(_math_subject()), encoding="utf-8")

    summary = run_batch(
        runtime=get_review_runtime(),
        adapter="math",
        subject_paths=sorted(subjects_dir.glob("*.json")),
    )
    assert summary.adapter == "math"
    assert summary.count == 2


# ---------------------------------------------------------------------------
# harness.compare_reviews
# ---------------------------------------------------------------------------


def test_compare_reviews_returns_one_entry_per_file(tmp_path):
    from spar_domain_ml.runtime import get_review_runtime
    from spar_framework.engine import run_review
    from spar_framework.harness import compare_reviews

    paths = []
    for i in range(3):
        result = run_review(
            runtime=get_review_runtime(),
            subject=_ml_subject(),
            source="",
            gate="PASS",
            report_text="",
        )
        p = tmp_path / f"review_{i}.json"
        p.write_text(json.dumps(result.to_dict()), encoding="utf-8")
        paths.append(p)

    comparisons = compare_reviews(paths)
    assert len(comparisons) == 3
    for c in comparisons:
        assert "verdict" in c
        assert "score" in c
        assert "claim_drift" in c
        assert "flags" in c


def test_compare_reviews_flags_non_passing_checks(tmp_path):
    from spar_domain_ml.runtime import get_review_runtime
    from spar_framework.engine import run_review
    from spar_framework.harness import compare_reviews

    # Subject with SOTA claim but lower metric — will produce ANOMALY on A1
    bad_subject = _ml_subject(metric_value=0.880, baseline_value=0.905)
    result = run_review(
        runtime=get_review_runtime(),
        subject=bad_subject,
        source="",
        gate="PASS",
        report_text="",
    )
    p = tmp_path / "bad_review.json"
    p.write_text(json.dumps(result.to_dict()), encoding="utf-8")

    comparisons = compare_reviews([p])
    assert "A1" in comparisons[0]["flags"]


# ---------------------------------------------------------------------------
# harness.BatchSummary.to_dict
# ---------------------------------------------------------------------------


def test_batch_summary_to_dict_has_all_fields(tmp_path):
    from spar_domain_ml.runtime import get_review_runtime
    from spar_framework.harness import run_batch

    subjects_dir = tmp_path / "subjects"
    subjects_dir.mkdir()
    (subjects_dir / "s1.json").write_text(json.dumps(_ml_subject()), encoding="utf-8")

    summary = run_batch(
        runtime=get_review_runtime(),
        adapter="ml",
        subject_paths=list(subjects_dir.glob("*.json")),
    )
    d = summary.to_dict()
    for key in ("adapter", "count", "verdicts", "mean_claim_drift",
                "mean_coverage_rate", "cannot_check_rate",
                "framework_declared_rate", "top_flags"):
        assert key in d, f"Missing key: {key}"


# ---------------------------------------------------------------------------
# report.py -- Markdown rendering
# ---------------------------------------------------------------------------


def test_batch_summary_to_markdown_contains_adapter(tmp_path):
    from spar_domain_ml.runtime import get_review_runtime
    from spar_framework.harness import run_batch
    from spar_framework.report import batch_summary_to_markdown

    subjects_dir = tmp_path / "subjects"
    subjects_dir.mkdir()
    (subjects_dir / "s1.json").write_text(json.dumps(_ml_subject()), encoding="utf-8")

    summary = run_batch(
        runtime=get_review_runtime(),
        adapter="ml",
        subject_paths=list(subjects_dir.glob("*.json")),
    )
    md = batch_summary_to_markdown(summary)
    assert "ml" in md
    assert "Verdict Distribution" in md
    assert "Metrics" in md


def test_compare_reviews_to_markdown_contains_table_header(tmp_path):
    from spar_domain_ml.runtime import get_review_runtime
    from spar_framework.engine import run_review
    from spar_framework.harness import compare_reviews
    from spar_framework.report import compare_reviews_to_markdown

    result = run_review(
        runtime=get_review_runtime(),
        subject=_ml_subject(),
        source="",
        gate="PASS",
        report_text="",
    )
    p = tmp_path / "review.json"
    p.write_text(json.dumps(result.to_dict()), encoding="utf-8")

    md = compare_reviews_to_markdown(compare_reviews([p]))
    assert "| File |" in md
    assert "Verdict" in md
    assert "Claim Drift" in md


# ---------------------------------------------------------------------------
# CLI e2e
# ---------------------------------------------------------------------------


def test_spar_batch_cli_produces_summary(tmp_path):
    from spar_framework.cli import main

    subjects_dir = tmp_path / "subjects"
    subjects_dir.mkdir()
    for i in range(3):
        (subjects_dir / f"s{i}.json").write_text(json.dumps(_ml_subject()), encoding="utf-8")
    output_path = tmp_path / "batch_summary.json"

    rc = main([
        "batch", "--adapter", "ml",
        "--subjects", str(subjects_dir),
        "--output-json", str(output_path),
    ])

    assert rc == 0
    payload = json.loads(output_path.read_text(encoding="utf-8"))
    assert payload["adapter"] == "ml"
    assert payload["count"] == 3
    assert sum(payload["verdicts"].values()) == 3
    assert "mean_claim_drift" in payload


def test_spar_batch_cli_writes_markdown(tmp_path):
    from spar_framework.cli import main

    subjects_dir = tmp_path / "subjects"
    subjects_dir.mkdir()
    (subjects_dir / "s1.json").write_text(json.dumps(_ml_subject()), encoding="utf-8")
    md_path = tmp_path / "summary.md"

    rc = main([
        "batch", "--adapter", "ml",
        "--subjects", str(subjects_dir),
        "--output-md", str(md_path),
    ])

    assert rc == 0
    md = md_path.read_text(encoding="utf-8")
    assert "SPAR Batch Review Summary" in md


def test_spar_batch_cli_writes_individual_reports(tmp_path):
    from spar_framework.cli import main

    subjects_dir = tmp_path / "subjects"
    subjects_dir.mkdir()
    (subjects_dir / "subject_a.json").write_text(json.dumps(_ml_subject()), encoding="utf-8")
    reports_dir = tmp_path / "reports"

    rc = main([
        "batch", "--adapter", "ml",
        "--subjects", str(subjects_dir),
        "--reports", str(reports_dir),
    ])

    assert rc == 0
    assert (reports_dir / "subject_a_review.json").exists()


def test_spar_batch_cli_empty_dir_returns_error(tmp_path, capsys):
    from spar_framework.cli import EXIT_INPUT_ERROR, main

    subjects_dir = tmp_path / "empty"
    subjects_dir.mkdir()

    rc = main(["batch", "--adapter", "ml", "--subjects", str(subjects_dir)])
    assert rc == EXIT_INPUT_ERROR


def test_spar_compare_cli_produces_comparison(tmp_path):
    from spar_framework.cli import main

    subjects_dir = tmp_path / "subjects"
    subjects_dir.mkdir()
    for i in range(2):
        (subjects_dir / f"s{i}.json").write_text(json.dumps(_ml_subject()), encoding="utf-8")
    reviews_dir = tmp_path / "reviews"

    main([
        "batch", "--adapter", "ml",
        "--subjects", str(subjects_dir),
        "--reports", str(reviews_dir),
    ])

    review_files = sorted(reviews_dir.glob("*.json"))
    output_path = tmp_path / "comparison.json"

    rc = main(["compare"] + [str(p) for p in review_files] + ["--output-json", str(output_path)])

    assert rc == 0
    payload = json.loads(output_path.read_text(encoding="utf-8"))
    assert payload["compared"] == 2
    assert len(payload["reviews"]) == 2
    for r in payload["reviews"]:
        assert "verdict" in r
        assert "claim_drift" in r


def test_spar_compare_cli_writes_markdown(tmp_path):
    from spar_framework.cli import main

    subjects_dir = tmp_path / "subjects"
    subjects_dir.mkdir()
    (subjects_dir / "s1.json").write_text(json.dumps(_ml_subject()), encoding="utf-8")
    reviews_dir = tmp_path / "reviews"

    main(["batch", "--adapter", "ml", "--subjects", str(subjects_dir),
          "--reports", str(reviews_dir)])

    review_files = sorted(reviews_dir.glob("*.json"))
    md_path = tmp_path / "compare.md"

    rc = main(["compare"] + [str(p) for p in review_files] + ["--output-md", str(md_path)])

    assert rc == 0
    assert "SPAR Review Comparison" in md_path.read_text(encoding="utf-8")
