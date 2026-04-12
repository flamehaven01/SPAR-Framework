"""Initial physics analytical anchor table."""

from __future__ import annotations

from typing import Any

GROUND_TRUTH: dict[str, dict[str, Any]] = {
    "flat": {
        "gate": {
            "expected": "PASS",
            "ref": "Polchinski Vol.1 §3.7",
            "detail": "Flat Minkowski is the zero-residual baseline.",
        },
        "beta_G_norm": {
            "expected": 0.0,
            "tolerance": 1e-4,
            "ref": "Polchinski Vol.1 §3.7",
        },
        "beta_B_norm": {
            "expected": 0.0,
            "tolerance": 1e-4,
            "ref": "Polchinski Vol.1 §3.7",
        },
        "beta_Phi_norm": {
            "expected": 0.0,
            "tolerance": 1e-4,
            "ref": "Polchinski Vol.1 §3.7",
        },
    },
    "schwarzschild": {
        "gate": {
            "expected": "PASS",
            "ref": "Wald GR §4.3",
            "detail": "Ricci-flat metric baseline for the geometry sector.",
        },
        "beta_G_norm": {
            "expected": 0.0,
            "tolerance": 1e-4,
            "ref": "Wald GR §4.3",
        },
    },
    "schwarzschild_dilaton": {
        "beta_G_norm": {
            "expected": 0.0,
            "tolerance": 1e-4,
            "ref": "Wald GR §4.3",
        },
        "beta_Phi_norm": {
            "expected": None,
            "formula": None,
            "ref": "Polchinski Vol.1 §3.4",
        },
        "gate": {
            "expected": "FAIL",
            "ref": "Polchinski Vol.1 §3.4",
            "detail": "Schwarzschild plus non-trivial dilaton is not a valid string vacuum on this path.",
        },
    },
    "de_sitter": {
        "gate": {
            "expected": "FAIL",
            "ref": "Maldacena-Nunez 2001",
            "detail": "Admissibility gate should fail on this reference path.",
        }
    },
    "linear_dilaton": {
        "gate": {
            "expected": "PASS",
            "ref": "Polchinski Vol.1 §3.4",
        },
        "beta_G_norm": {
            "expected": 0.0,
            "tolerance": 1e-4,
            "ref": "Polchinski Vol.1 §3.4",
        },
        "beta_Phi_norm": {
            "expected": None,
            "formula": "4*V^2",
            "ref": "Polchinski Vol.1 §3.4",
        },
    },
    "wzw": {
        "gate": {
            "expected": "PASS",
            "ref": "Polchinski Vol.1 §15.1",
        },
        "beta_G_norm": {
            "expected": 0.0,
            "tolerance": 0.05,
            "ref": "Polchinski Vol.1 §15.1",
        },
    },
    "ads": {
        "gate": {
            "expected": "PASS",
            "ref": "Maldacena hep-th/9711200",
        },
        "beta_G_norm": {
            "expected": 0.0,
            "tolerance": 0.1,
            "ref": "Maldacena hep-th/9711200",
        },
    },
}
