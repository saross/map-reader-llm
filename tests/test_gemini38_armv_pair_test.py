"""Tier-1 guard for the Arm V pair test's hand-typed incumbent values.

`scripts/gemini38_armv_pair_test.py` gates each incumbent side on a
committed F1@20 typed into its ``INCUMBENTS`` table. This test pins those
numbers to the results files they were read from, so a later re-score of
either 3.7 cell cannot leave the pair test gating against a stale value.
"""

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scripts.gemini38_armv_pair_test import GATE_TOL, INCUMBENTS  # noqa: E402

PROJECT_ROOT = Path(__file__).resolve().parent.parent

#: Where each incumbent's committed verified-best F1@20 lives on disk.
ANALYSES = {
    "all-3.7": PROJECT_ROOT / "results/gemini37-screen-2026-08-28/swap37/analysis.json",
    "carried-G3": PROJECT_ROOT / "results/gemini37-screen-2026-08-28/analysis.json",
}


@pytest.mark.tier1
def test_incumbent_values_match_their_committed_analyses():
    """Each hand-typed committed F1@20 must equal the analysis.json best to 1e-4."""
    assert len(INCUMBENTS) == 2
    for label, geojson, committed in INCUMBENTS:
        assert geojson.exists(), f"{label}: verified set missing at {geojson}"
        best = json.loads(ANALYSES[label].read_text())["image_best"]["f1"]
        assert committed == pytest.approx(best, abs=1e-4), (
            f"{label}: table says {committed}, analysis.json says {best:.4f}")
    assert GATE_TOL == 1e-3
