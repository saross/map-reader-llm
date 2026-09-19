"""The 2x2 interaction test (reports/image-2x2-tests-declaration-2026-09-19.md).

Synthetic tiles: under no interaction the arm effect is the same in both
rows and p is large; under a strong interaction p is small; the statistic is
antisymmetric in the rows and zero when both rows share the same cells.

The last three tests cover the family the Benjamini-Hochberg correction is
applied over, which is the rung's, not always five (audit finding M1,
2026-09-20): fake p-values make the family size readable off the adjusted
values, and a row outside the family keeps its raw statistic while losing
its verdict.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scripts.gemini37_image_55map_r2 import did_test_f1, did_test_mcc  # noqa: E402

pytestmark = pytest.mark.tier1
N = 600


def _counts(rng, tp_rate, fp_rate):
    tp = (rng.random(N) < tp_rate).astype(float)
    fp = (rng.random(N) < fp_rate).astype(float)
    fn = 1.0 - tp
    return tp, fp, fn


def test_no_interaction_gives_a_large_p_on_f1():
    rng = np.random.default_rng(1)
    tp, fp, fn = {}, {}, {}
    for c, (t, f) in {"A1": (0.6, 0.3), "A2": (0.7, 0.2), "B1": (0.5, 0.4), "B2": (0.6, 0.3)}.items():
        tp[c], fp[c], fn[c] = _counts(rng, t, f)
    r = did_test_f1(tp, fp, fn, n_permutations=2000, seed=3)
    assert r["n_tiles"] == N and r["n_permutations"] == 2000
    assert r["p_value"] > 0.05


def test_a_strong_interaction_gives_a_small_p_on_f1():
    rng = np.random.default_rng(2)
    tp, fp, fn = {}, {}, {}
    # arm 2 helps row A a lot and hurts row B
    for c, (t, f) in {"A1": (0.5, 0.4), "A2": (0.9, 0.05), "B1": (0.7, 0.2), "B2": (0.5, 0.4)}.items():
        tp[c], fp[c], fn[c] = _counts(rng, t, f)
    r = did_test_f1(tp, fp, fn, n_permutations=2000, seed=3)
    assert r["observed_diff"] > 0.2
    assert r["p_value"] < 0.01


def test_identical_rows_give_zero_statistic():
    rng = np.random.default_rng(4)
    a1 = _counts(rng, 0.6, 0.3)
    a2 = _counts(rng, 0.7, 0.2)
    tp = {"A1": a1[0], "A2": a2[0], "B1": a1[0], "B2": a2[0]}
    fp = {"A1": a1[1], "A2": a2[1], "B1": a1[1], "B2": a2[1]}
    fn = {"A1": a1[2], "A2": a2[2], "B1": a1[2], "B2": a2[2]}
    r = did_test_f1(tp, fp, fn, n_permutations=500, seed=3)
    assert abs(r["observed_diff"]) < 1e-12
    assert r["p_value"] == 1.0


def test_swapping_the_rows_flips_the_sign_and_keeps_p():
    rng = np.random.default_rng(5)
    cells = {c: _counts(rng, t, f) for c, (t, f) in
             {"A1": (0.5, 0.4), "A2": (0.8, 0.1), "B1": (0.6, 0.3), "B2": (0.6, 0.3)}.items()}
    tp = {c: v[0] for c, v in cells.items()}
    fp = {c: v[1] for c, v in cells.items()}
    fn = {c: v[2] for c, v in cells.items()}
    r1 = did_test_f1(tp, fp, fn, n_permutations=1000, seed=3)
    swap = {"A1": "B1", "A2": "B2", "B1": "A1", "B2": "A2"}
    r2 = did_test_f1({k: tp[swap[k]] for k in tp}, {k: fp[swap[k]] for k in fp},
                     {k: fn[swap[k]] for k in fn}, n_permutations=1000, seed=3)
    assert abs(r1["observed_diff"] + r2["observed_diff"]) < 1e-12
    assert r1["p_value"] == r2["p_value"]


def test_mcc_interaction_detects_a_row_dependent_arm_effect():
    rng = np.random.default_rng(6)
    truth = rng.random(N) < 0.4

    def pred(hit, false):
        return np.where(truth, rng.random(N) < hit, rng.random(N) < false)

    p = {"A1": pred(0.6, 0.3), "A2": pred(0.95, 0.05), "B1": pred(0.7, 0.2), "B2": pred(0.6, 0.3)}
    r = did_test_mcc(p, truth, n_permutations=2000, seed=3)
    assert r["observed_diff"] > 0.2 and r["p_value"] < 0.01
    q = {"A1": pred(0.6, 0.3), "A2": pred(0.7, 0.2), "B1": pred(0.6, 0.3), "B2": pred(0.7, 0.2)}
    r0 = did_test_mcc(q, truth, n_permutations=2000, seed=3)
    assert r0["p_value"] > 0.05


def test_the_null_micro_f1_is_bitwise_identical_to_the_boards_scalar():
    """The null and the observed statistic must use the same arithmetic.

    ``did_test_f1`` computes the observed D with the board's scalar
    ``micro_f1`` and every null D with ``_micro_f1_vec``, then compares
    them with ``>=``. The closed form ``2*tp / (2*tp + fp + fn)`` is
    algebraically equal to ``2PR / (P + R)`` but not equal in floating
    point: it differed from ``micro_f1`` in the last ULP on 7,526 of
    20,000 random count triples. This pins the two to the same spelling.
    """
    from scripts.gemini37_image_55map_r2 import _micro_f1_vec
    from scripts.n1_baseline_leaderboard_tiering import micro_f1

    rng = np.random.default_rng(0)
    tp = rng.integers(0, 50, 5000).astype(float)
    fp = rng.integers(0, 50, 5000).astype(float)
    fn = rng.integers(0, 50, 5000).astype(float)

    scalar = np.array([micro_f1(a, b, c) for a, b, c in zip(tp, fp, fn)])
    vector = _micro_f1_vec(tp, fp, fn)

    assert np.array_equal(vector, scalar), (
        f"{int((vector != scalar).sum())} of {len(scalar)} triples differ"
    )


def test_the_null_micro_f1_keeps_the_zero_rule():
    """tp == 0 is 0.0 even when fp and fn are zero too (no NaN)."""
    from scripts.gemini37_image_55map_r2 import _micro_f1_vec

    out = _micro_f1_vec(
        np.array([0.0, 0.0, 3.0]),
        np.array([0.0, 5.0, 0.0]),
        np.array([0.0, 5.0, 0.0]),
    )
    assert np.array_equal(out, np.array([0.0, 0.0, 1.0]))


def test_the_null_is_centred_on_zero():
    """A correct exchangeable null has mean zero.

    The existing fixtures assert only `p > 0.05` / `p < 0.01`, which is
    loose enough to survive a badly biased null: raising the per-tile swap
    probability from 0.5 to 0.9 moves `null_mean` from -0.0002 to -0.45 and
    every assertion still passes. Centredness is the property that breaks
    first when the permutation scheme is wrong.
    """
    rng = np.random.default_rng(2)
    tp, fp, fn = {}, {}, {}
    for c, (t, f) in {"A1": (0.5, 0.4), "A2": (0.9, 0.05),
                      "B1": (0.7, 0.2), "B2": (0.5, 0.4)}.items():
        tp[c], fp[c], fn[c] = _counts(rng, t, f)

    r = did_test_f1(tp, fp, fn, n_permutations=2000, seed=3)

    # Standard error of the null mean over n permutations.
    tolerance = 4.0 * r["null_std"] / np.sqrt(r["n_permutations"])
    assert abs(r["null_mean"]) < tolerance, (
        f"null_mean {r['null_mean']:+.5f} exceeds {tolerance:.5f} — "
        "the permutation scheme is biased"
    )


def test_identical_rows_make_every_permutation_a_no_op():
    """The swap is PAIRED: the (A1, A2) pair moves as one unit.

    When the two rows hold the same cells, swapping a tile's row-A pair
    with its row-B pair changes nothing, so every null D is exactly zero
    and the null has no spread at all. An independent mask per cell — the
    obvious way to break the pairing — would mix arm 1 of one row with arm
    2 of the other and give a non-degenerate null here.
    """
    rng = np.random.default_rng(4)
    a1 = _counts(rng, 0.6, 0.3)
    a2 = _counts(rng, 0.7, 0.2)
    tp = {"A1": a1[0], "A2": a2[0], "B1": a1[0], "B2": a2[0]}
    fp = {"A1": a1[1], "A2": a2[1], "B1": a1[1], "B2": a2[1]}
    fn = {"A1": a1[2], "A2": a2[2], "B1": a1[2], "B2": a2[2]}

    r = did_test_f1(tp, fp, fn, n_permutations=500, seed=3)

    assert r["null_std"] == 0.0
    assert r["null_mean"] == 0.0


def test_the_seed_is_live():
    """Two seeds must give two null draws.

    `default_rng(seed)` hard-coded to `default_rng(0)` would make the seed
    argument decorative and the run irreproducible from its recorded seed,
    with every existing assertion still satisfied.
    """
    rng = np.random.default_rng(1)
    tp, fp, fn = {}, {}, {}
    for c, (t, f) in {"A1": (0.6, 0.3), "A2": (0.7, 0.2),
                      "B1": (0.5, 0.4), "B2": (0.6, 0.3)}.items():
        tp[c], fp[c], fn[c] = _counts(rng, t, f)

    a = did_test_f1(tp, fp, fn, n_permutations=2000, seed=3)
    b = did_test_f1(tp, fp, fn, n_permutations=2000, seed=99)
    again = did_test_f1(tp, fp, fn, n_permutations=2000, seed=3)

    assert a["observed_diff"] == b["observed_diff"]  # the data did not change
    assert a["null_mean"] != b["null_mean"]          # the draw did
    assert a["null_mean"] == again["null_mean"]      # and is reproducible


# ─────────────────────────────────────────────────────────────────────
# The BH family at each rung (audit finding M1, 2026-09-20)
# ─────────────────────────────────────────────────────────────────────

# Raw p-values chosen so every rank is unambiguous, the monotonicity
# cummin never fires, and m = 4 and m = 5 give different answers on every
# member — so the family size is readable off the arithmetic alone.
_RAW_P = {"T1": 0.001, "T2": 0.010, "T3": 0.020, "T4": 0.900, "T5": 0.002}


def _family_rows(t5_meaningful: bool) -> list[dict]:
    """The declared five rows, with T5 flagged as the rung requires."""
    rows = [{"test": t, "name": t, "p_value": _RAW_P[t], "observed_diff": 0.01}
            for t in ("T1", "T2", "T3", "T4")]
    rows.append({"test": "T5", "name": "confound check vs IM-k3",
                 "p_value": _RAW_P["T5"], "observed_diff": 0.05,
                 "meaningful": t5_meaningful})
    return rows


def test_the_bh_family_is_four_at_k_ne_3_and_five_at_k_3():
    """The family size is the rung's, and it is visible in the arithmetic.

    `reports/image-2x2-tests-declaration-2026-09-19.md` section 3 makes T5
    meaningful only at K = 3. Until 2026-09-20 all five rows went into the
    correction at every rung, so the four real tests at K = 1 and K = 5
    were corrected against m = 5: the K = 5 file's MCC T3 row carries
    `0.0629 * 5/3 = 0.104833` where the declared family gives
    `0.0629 * 4/3 = 0.083867`. That direction is conservative — it can
    only suppress a finding — but it is not the declared family.
    """
    from scripts.gemini37_image_55map_r2 import apply_bh_to_family

    exploratory = _family_rows(t5_meaningful=False)
    members = apply_bh_to_family(exploratory, note="outside")
    by_test = {r["test"]: r for r in exploratory}

    assert [r["test"] for r in members] == ["T1", "T2", "T3", "T4"]
    # p * m / rank with m = 4 and ranks 1..4 over T1, T2, T3, T4.
    assert by_test["T1"]["bh_adjusted_p"] == round(0.001 * 4 / 1, 6)
    assert by_test["T2"]["bh_adjusted_p"] == round(0.010 * 4 / 2, 6)
    assert by_test["T3"]["bh_adjusted_p"] == round(0.020 * 4 / 3, 6)
    assert by_test["T4"]["bh_adjusted_p"] == round(0.900 * 4 / 4, 6)

    primary = _family_rows(t5_meaningful=True)
    members = apply_bh_to_family(primary, note="outside")
    by_test = {r["test"]: r for r in primary}

    assert [r["test"] for r in members] == ["T1", "T2", "T3", "T4", "T5"]
    # m = 5, and T5's p = 0.002 takes rank 2, pushing T2, T3, T4 down one.
    assert by_test["T1"]["bh_adjusted_p"] == round(0.001 * 5 / 1, 6)
    assert by_test["T5"]["bh_adjusted_p"] == round(0.002 * 5 / 2, 6)
    assert by_test["T2"]["bh_adjusted_p"] == round(0.010 * 5 / 3, 6)
    assert by_test["T3"]["bh_adjusted_p"] == round(0.020 * 5 / 4, 6)
    assert by_test["T4"]["bh_adjusted_p"] == round(0.900 * 5 / 5, 6)


def test_a_row_outside_the_family_keeps_its_statistic_and_loses_its_verdict():
    """The second half of M1: no adjusted p-value, no significance.

    At K = 5 the F1 T5 row read `"meaningful": false, "p_value": 0.0009,
    "bh_adjusted_p": 0.001125, "significant": true` — a verdict on a
    contrast the family declares meaningless at that rung, one citation
    away from being read as a confound check that passed. The raw
    statistic stays, because the row is still reported for completeness.
    """
    from scripts.gemini37_image_55map_r2 import (
        T5_OUT_OF_FAMILY,
        apply_bh_to_family,
    )

    rows = _family_rows(t5_meaningful=False)
    apply_bh_to_family(rows, note=T5_OUT_OF_FAMILY)
    t5 = rows[-1]

    assert "bh_adjusted_p" not in t5
    assert t5["significant"] is None
    assert t5["p_value"] == 0.002 and t5["observed_diff"] == 0.05
    assert "outside" in t5["note"]
    # The four members keep a boolean verdict, both ways round.
    assert [r["significant"] for r in rows[:4]] == [True, True, True, False]


def test_the_primary_rung_is_unchanged_by_the_family_rule():
    """K = 3 must produce exactly what it produced before.

    The committed `tests_2x2_K3.json` is citable and the PI's ruling
    changes nothing at the primary rung, so the meaningful-T5 path has to
    stay bit-for-bit identical to a plain correction over all five rows.
    """
    from scripts.apply_fdr_correction import apply_bh_correction
    from scripts.gemini37_image_55map_r2 import apply_bh_to_family

    rows = _family_rows(t5_meaningful=True)
    expected = apply_bh_correction([r["p_value"] for r in rows], q=0.05)

    apply_bh_to_family(rows, note="outside")

    assert [r["bh_adjusted_p"] for r in rows] == [
        round(float(p), 6) for p in expected
    ]
    assert all("note" not in r for r in rows)
    assert all(isinstance(r["significant"], bool) for r in rows)
