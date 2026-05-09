"""Regression tests for the spar_domain_math proof claim-drift adapter."""

from __future__ import annotations

import json


def _base_subject(**overrides):
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
# Runtime wiring
# ---------------------------------------------------------------------------


def test_math_runtime_produces_review_result():
    from spar_domain_math.runtime import get_review_runtime
    from spar_framework.engine import run_review

    result = run_review(
        runtime=get_review_runtime(),
        subject=_base_subject(),
        source="",
        gate="PASS",
        report_text="We prove that every compact Hausdorff space is normal.",
    )
    assert result.verdict in {"ACCEPT", "MINOR_REVISION", "MAJOR_REVISION", "REJECT"}
    assert result.score >= 0
    assert result.model_registry_snapshot is not None
    assert result.gap_registry_snapshot is not None


def test_math_framework_declared_have_adapter_limitation_scope():
    from spar_domain_math.layer_c_advanced import build_framework_declared_checks

    checks = build_framework_declared_checks(subject={})
    for check in checks:
        assert check.scope == "adapter_limitation", f"{check.check_id} scope={check.scope!r}"
        assert check.basis == "framework_declared"


# ---------------------------------------------------------------------------
# Layer A -- claim drift cases
# ---------------------------------------------------------------------------


def test_proof_claim_absent_status_fails():
    from spar_domain_math.layer_a import check_a1_proof

    subject = _base_subject(proof_surface={"proof_status": "absent",
                                           "assumptions_explicit": True, "prior_art_cited": True})
    result = check_a1_proof(subject)
    assert result.status == "FAIL"


def test_conjecture_with_proof_claimed_is_anomaly():
    from spar_domain_math.layer_a import check_a1_proof

    subject = _base_subject(theorem_type="conjecture")
    result = check_a1_proof(subject)
    assert result.status == "ANOMALY"


def test_proof_claimed_false_passes():
    from spar_domain_math.layer_a import check_a1_proof

    subject = _base_subject(claim_profile={"proof_claimed": False,
                                           "generality_claimed": False, "novelty_claimed": False})
    result = check_a1_proof(subject)
    assert result.status == "PASS"


def test_proof_claim_sketch_status_is_consistent():
    from spar_domain_math.layer_a import check_a1_proof

    subject = _base_subject(proof_surface={"proof_status": "sketch",
                                           "assumptions_explicit": True, "prior_art_cited": True})
    result = check_a1_proof(subject)
    assert result.status == "CONSISTENT"


def test_generality_without_assumptions_is_gap():
    from spar_domain_math.layer_a import check_a2_generality

    subject = _base_subject(
        claim_profile={"proof_claimed": False, "generality_claimed": True, "novelty_claimed": False},
        proof_surface={"proof_status": "complete", "assumptions_explicit": False, "prior_art_cited": True},
    )
    result = check_a2_generality(subject)
    assert result.status == "GAP"


def test_generality_with_assumptions_is_consistent():
    from spar_domain_math.layer_a import check_a2_generality

    subject = _base_subject(
        claim_profile={"proof_claimed": False, "generality_claimed": True, "novelty_claimed": False},
    )
    result = check_a2_generality(subject)
    assert result.status == "CONSISTENT"


def test_novelty_without_prior_art_is_warn():
    from spar_domain_math.layer_a import check_a3_novelty

    subject = _base_subject(
        claim_profile={"proof_claimed": False, "generality_claimed": False, "novelty_claimed": True},
        proof_surface={"proof_status": "complete", "assumptions_explicit": True, "prior_art_cited": False},
    )
    result = check_a3_novelty(subject)
    assert result.status == "WARN"


def test_novelty_with_prior_art_is_consistent():
    from spar_domain_math.layer_a import check_a3_novelty

    subject = _base_subject(
        claim_profile={"proof_claimed": False, "generality_claimed": False, "novelty_claimed": True},
    )
    result = check_a3_novelty(subject)
    assert result.status == "CONSISTENT"


# ---------------------------------------------------------------------------
# Layer B
# ---------------------------------------------------------------------------


def test_proof_language_without_profile_warns():
    from spar_domain_math.layer_b import check_b1_proof_language

    subject = _base_subject(
        claim_profile={"proof_claimed": False, "generality_claimed": False, "novelty_claimed": False}
    )
    result = check_b1_proof_language(subject, "We prove that the space is connected.")
    assert result.status == "WARN"


def test_formal_verification_phrase_is_cannot_check():
    from spar_domain_math.layer_b import check_b4_formal_verification_claims

    result = check_b4_formal_verification_claims("The result is formally verified using Lean proof.")
    assert result.status == "CANNOT_CHECK"
    assert result.check_id == "B4"


def test_no_formal_verification_phrase_is_pass():
    from spar_domain_math.layer_b import check_b4_formal_verification_claims

    result = check_b4_formal_verification_claims("We prove the theorem by induction.")
    assert result.status == "PASS"
    assert result.check_id == "B4"


# ---------------------------------------------------------------------------
# Layer C
# ---------------------------------------------------------------------------


def test_proof_status_complete_is_genuine():
    from spar_domain_math.layer_c import check_c1_proof_maturity

    assert check_c1_proof_maturity(_base_subject()).status == "GENUINE"


def test_proof_status_sketch_is_approximation():
    from spar_domain_math.layer_c import check_c1_proof_maturity

    subject = _base_subject(proof_surface={"proof_status": "sketch",
                                           "assumptions_explicit": True, "prior_art_cited": True})
    assert check_c1_proof_maturity(subject).status == "APPROXIMATION"


def test_proof_status_absent_is_gap():
    from spar_domain_math.layer_c import check_c1_proof_maturity

    subject = _base_subject(proof_surface={"proof_status": "absent",
                                           "assumptions_explicit": True, "prior_art_cited": True})
    assert check_c1_proof_maturity(subject).status == "GAP"


def test_assumptions_explicit_is_genuine():
    from spar_domain_math.layer_c import check_c2_statement_boundary

    assert check_c2_statement_boundary(_base_subject()).status == "GENUINE"


def test_assumptions_missing_is_gap():
    from spar_domain_math.layer_c import check_c2_statement_boundary

    subject = _base_subject(proof_surface={"proof_status": "complete",
                                           "assumptions_explicit": False, "prior_art_cited": True})
    assert check_c2_statement_boundary(subject).status == "GAP"


# ---------------------------------------------------------------------------
# Registry
# ---------------------------------------------------------------------------


def test_math_registry_snapshot_counts_models():
    from spar_domain_math.registry_seed import math_model_registry_snapshot

    snapshot = math_model_registry_snapshot()
    assert snapshot["total_models"] == 3
    model_ids = {m["model_id"] for m in snapshot["models"]}
    assert "proof_anchor_checker" in model_ids
    assert "generality_scope_validator" in model_ids
    assert "statement_boundary_probe" in model_ids


def test_math_gap_registry_snapshot_counts_states():
    from spar_domain_math.registry_seed import math_gap_registry_snapshot

    snapshot = math_gap_registry_snapshot()
    assert snapshot["total_gaps"] == 3
    states = {g["state"] for g in snapshot["gaps"]}
    assert "open" in states
    assert "partial" in states


# ---------------------------------------------------------------------------
# Policy loader
# ---------------------------------------------------------------------------


def test_math_layer_a_rules_from_policy():
    from spar_domain_math.policy_loader import get_layer_a_rules

    rules = get_layer_a_rules()
    assert rules["proof_requires_evidence"] is True
    assert rules["generality_requires_assumptions"] is True
    assert rules["novelty_uncited_status"] == "WARN"


# ---------------------------------------------------------------------------
# CLI e2e
# ---------------------------------------------------------------------------


def test_spar_review_math_adapter_produces_valid_result(tmp_path):
    from spar_framework.cli import main

    subject_path = tmp_path / "math_subject.json"
    subject_path.write_text(json.dumps(_base_subject()), encoding="utf-8")
    output_path = tmp_path / "math_review.json"

    rc = main([
        "review", "--adapter", "math",
        "--subject-json", str(subject_path),
        "--report-text", "We prove that every compact Hausdorff space is normal.",
        "--output-json", str(output_path),
    ])

    assert rc == 0
    payload = json.loads(output_path.read_text(encoding="utf-8"))
    assert payload["verdict"] in {"ACCEPT", "MINOR_REVISION", "MAJOR_REVISION", "REJECT"}
    assert "claim_drift" in payload
    check_ids = {c["check_id"] for c in payload["layer_b"]}
    assert "B1" in check_ids and "B4" in check_ids


def test_spar_example_math_topology(tmp_path):
    from spar_framework.cli import main

    output_path = tmp_path / "example.json"

    rc = main(["example", "--adapter", "math", "--task", "topology",
               "--output-json", str(output_path)])

    assert rc == 0
    payload = json.loads(output_path.read_text(encoding="utf-8"))
    assert payload["task"] == "topology"
    subject = payload["subject"]
    assert subject["theorem_type"] == "theorem"
    assert "claim_profile" in subject
    assert "proof_surface" in subject


def test_spar_schema_math_subject(capsys):
    from spar_framework.cli import main

    rc = main(["schema", "subject", "--adapter", "math"])

    assert rc == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["title"] == "SPAR Math Adapter Subject"
    assert "theorem_type" in payload["properties"]
    assert "proof_surface" in payload["properties"]
