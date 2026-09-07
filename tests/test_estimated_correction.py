"""Tier-1 tests for the estimated-correction column (r2 chain step 6, card § 2)."""

import json
import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scripts import estimated_correction as ec  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent


@pytest.mark.tier1
def test_counts_round_trip_precision_recall():
    c = ec.Counts.from_prn(0.9, 0.8, 1000)
    p, r, _f = ec.prf(np.array(c.tp), np.array(c.fp), np.array(c.fn))
    assert float(p) == pytest.approx(0.9) and float(r) == pytest.approx(0.8)


@pytest.mark.tier1
def test_zero_rates_leave_a_condition_unchanged():
    """With no unseen error the column must equal the r2 point estimate."""
    c = ec.Counts.from_prn(0.85, 0.80, 4000)
    p, r, f = ec.apply_correction(c, 0.0, 0.0, 0.0)
    p0, r0, f0 = ec.prf(np.array(c.tp), np.array(c.fp), np.array(c.fn))
    assert float(p) == pytest.approx(float(p0)) and float(r) == pytest.approx(float(r0))
    assert float(f) == pytest.approx(float(f0))


@pytest.mark.tier1
def test_unseen_misses_lower_recall_and_omissions_raise_precision():
    c = ec.Counts.from_prn(0.85, 0.80, 4000)
    p_m, r_m, _ = ec.apply_correction(c, 50.0, 0.0, 0.0)  # unseen missed mounds
    p_o, r_o, _ = ec.apply_correction(c, 0.0, 0.0, 36.0)  # model-found omissions
    base_p, base_r, _ = ec.prf(np.array(c.tp), np.array(c.fp), np.array(c.fn))
    assert float(r_m) < float(base_r) and float(p_m) == pytest.approx(float(base_p))
    assert float(p_o) > float(base_p) and float(r_o) > float(base_r)


@pytest.mark.tier1
def test_omission_conversion_is_capped_at_the_false_positives():
    c = ec.Counts(tp=100.0, fp=5.0, fn=20.0)
    p, _r, _f = ec.apply_correction(c, 0.0, 0.0, 36.0)
    assert float(p) == pytest.approx(1.0)  # all five FPs converted, no more


@pytest.mark.tier1
def test_board_estimate_is_deterministic_and_intervals_bracket_the_point():
    board_path = ROOT / "results/55map-final-board-r2-2026-09-06/final_board_50m.json"
    if not board_path.exists():
        pytest.skip("r2 final board not present")
    board = json.loads(board_path.read_text())
    a = ec.estimate_board(board, draws=2000, seed=42)
    b = ec.estimate_board(board, draws=2000, seed=42)
    assert [c["f1_hat"] for c in a["cells"]] == [c["f1_hat"] for c in b["cells"]]
    assert len(a["cells"]) == len(board["cells"]) == 35
    for c in a["cells"]:
        f = c["f1_hat"]
        assert f["ci_lower"] <= f["point"] <= f["ci_upper"]
        assert abs(c["delta_f1_hat_minus_r2"]) < 0.05  # a column, not a re-tiering
    # The recorded rates are the audits' counts (card section 2).
    assert (a["rates"]["p_dm_empty"]["k"], a["rates"]["p_dm_empty"]["n"]) == (5, 470)
    assert a["rates"]["p_dm_cluster"]["applied_to"] == 0  # census complete; in r2 already
