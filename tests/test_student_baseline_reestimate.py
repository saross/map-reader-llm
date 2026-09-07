"""Tier-1 tests for the r2 student-baseline re-estimate (r2 chain step 9, card § 2b)."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scripts import student_baseline_reestimate as sb  # noqa: E402


@pytest.mark.tier1
def test_reestimate_is_deterministic_and_well_formed():
    a = sb.reestimate(draws=2000, seed=42)
    b = sb.reestimate(draws=2000, seed=42)
    assert a["rows"][0]["f1"] == b["rows"][0]["f1"]
    assert [r["row"] for r in a["rows"]][2].startswith("GS-4 direct")
    assert a["inputs"]["extension_mounds_r2"] == 278 and a["inputs"]["audit_additions"] == 14


@pytest.mark.tier1
def test_extrapolated_terms_lower_recall_but_not_precision():
    a = sb.reestimate(draws=2000, seed=42)
    full, reviewed_only = a["rows"][0], a["rows"][1]
    assert reviewed_only["recall"]["mean"] > full["recall"]["mean"]
    assert reviewed_only["precision"]["mean"] == pytest.approx(full["precision"]["mean"])
    assert 0.98 < full["precision"]["mean"] < 1.0  # a small, non-zero student FP rate
    assert full["recall"]["ci_lower"] <= full["recall"]["mean"] <= full["recall"]["ci_upper"]
