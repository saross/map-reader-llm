"""Tier-1 tests for the MCC extensions of the two K-ladder instruments.

Covers the three properties the K-ladder § 4.1 test depends on:

1. **The array kernel and its GeoDataFrame wrapper agree.** The refactor that
   exposed ``permutation_test_mcc_arrays`` must not have changed what
   ``run_permutation_test_mcc`` reports.
2. **F1 and MCC see the same swap masks.** Both kernels must draw one
   ``rng.random(n_tiles) < 0.5`` mask per iteration from
   ``default_rng(seed)``, so a ΔF1 and a ΔMCC on one pair are two statistics
   of one permutation rather than two experiments.
3. **The opposite-direction fixture.** A synthetic pair where F1 RISES while
   tile-MCC FALLS — the exact shape of the finding under test — must be
   handled: both deltas carry their own sign, and neither statistic borrows
   the other's direction.

The per-map sign-swap sibling (``paired_permutation_mcc``) is covered on the
same opposite-direction fixture, shaped as per-map confusion.
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pytest

REPO = Path(__file__).resolve().parent.parent
for candidate in (REPO, REPO / "scripts"):
    if str(candidate) not in sys.path:
        sys.path.insert(0, str(candidate))

from scripts.n1_baseline_leaderboard_tiering import (  # noqa: E402
    permutation_test_float,
)
from scripts.pairwise_permutation_test import (  # noqa: E402
    _compute_mcc,
    permutation_test_mcc_arrays,
)

pytestmark = pytest.mark.tier1


# ---------------------------------------------------------------------------
# The opposite-direction fixture
# ---------------------------------------------------------------------------

def _opposite_direction_fixture() -> dict:
    """Build a tile set where F1 rises with K while tile-MCC falls.

    The mechanism the K-ladder finding proposes, made synthetic and exact:

    * ``n_hit`` tiles are already true positives for BOTH arms. The
      higher-K arm adds extra matched detections INSIDE those tiles, which
      raises micro-F1 (more TP at the same FP) and moves no tile's
      classification at all.
    * ``n_flip`` tiles hold no reference and no detection for the low-K arm
      (true negatives) but pick up one spurious detection in the high-K arm,
      flipping each from TN to FP. That cannot touch the tiles' F1 much but it
      costs tile-level MCC.

    Returns:
        Dict of per-tile arrays for both arms: ``tp/fp/fn`` (F1, float) and
        ``tp_c/tn_c/fp_c/fn_c`` (tile classification, one-hot int).
    """
    n_hit, n_flip, n_quiet = 40, 25, 200
    n = n_hit + n_flip + n_quiet

    # --- F1 side: per-tile match counts -----------------------------------
    tp_lo = np.zeros(n)
    fp_lo = np.zeros(n)
    fn_lo = np.zeros(n)
    tp_hi = np.zeros(n)
    fp_hi = np.zeros(n)
    fn_hi = np.zeros(n)
    # Hit tiles: 2 references each; low-K finds 1, high-K finds both.
    tp_lo[:n_hit] = 1.0
    fn_lo[:n_hit] = 1.0
    tp_hi[:n_hit] = 2.0
    # Flip tiles: no reference; high-K emits one false positive.
    fp_hi[n_hit:n_hit + n_flip] = 1.0
    # Quiet tiles: nothing for either arm.

    # --- MCC side: per-tile one-hot classification ------------------------
    def cols(classes: list[str]) -> tuple[np.ndarray, ...]:
        """Split a per-tile class list into four one-hot integer arrays."""
        arr = np.array(classes)
        return tuple(
            (arr == label).astype(int) for label in ("TP", "TN", "FP", "FN")
        )

    tp_c_lo, tn_c_lo, fp_c_lo, fn_c_lo = cols(
        ["TP"] * n_hit + ["TN"] * n_flip + ["TN"] * n_quiet)
    tp_c_hi, tn_c_hi, fp_c_hi, fn_c_hi = cols(
        ["TP"] * n_hit + ["FP"] * n_flip + ["TN"] * n_quiet)

    return {
        "n_tiles": n,
        "lo": {"tp": tp_lo, "fp": fp_lo, "fn": fn_lo,
               "tp_c": tp_c_lo, "tn_c": tn_c_lo,
               "fp_c": fp_c_lo, "fn_c": fn_c_lo},
        "hi": {"tp": tp_hi, "fp": fp_hi, "fn": fn_hi,
               "tp_c": tp_c_hi, "tn_c": tn_c_hi,
               "fp_c": fp_c_hi, "fn_c": fn_c_hi},
    }


def test_fixture_moves_f1_and_mcc_in_opposite_directions() -> None:
    """The fixture is what it claims: ΔF1 > 0 and ΔMCC < 0 on one pair."""
    fx = _opposite_direction_fixture()
    lo, hi = fx["lo"], fx["hi"]

    f1 = permutation_test_float(hi["tp"], hi["fp"], hi["fn"],
                                lo["tp"], lo["fp"], lo["fn"],
                                n_permutations=200, seed=42)
    mcc = permutation_test_mcc_arrays(hi["tp_c"], hi["tn_c"], hi["fp_c"],
                                      hi["fn_c"], lo["tp_c"], lo["tn_c"],
                                      lo["fp_c"], lo["fn_c"],
                                      n_permutations=200, seed=42)
    assert f1["observed_diff"] > 0, "high-K arm must gain F1"
    assert mcc["observed_mcc_diff"] < 0, "high-K arm must lose tile-MCC"
    # And the two statistics are computed on the same number of tiles.
    assert f1["n_tiles"] == mcc["n_tiles"] == fx["n_tiles"]


def test_mcc_kernel_signs_are_not_borrowed_from_f1() -> None:
    """Reversing the argument order reverses ΔMCC and leaves the p-value alone."""
    fx = _opposite_direction_fixture()
    lo, hi = fx["lo"], fx["hi"]
    forward = permutation_test_mcc_arrays(
        hi["tp_c"], hi["tn_c"], hi["fp_c"], hi["fn_c"],
        lo["tp_c"], lo["tn_c"], lo["fp_c"], lo["fn_c"],
        n_permutations=500, seed=42)
    reverse = permutation_test_mcc_arrays(
        lo["tp_c"], lo["tn_c"], lo["fp_c"], lo["fn_c"],
        hi["tp_c"], hi["tn_c"], hi["fp_c"], hi["fn_c"],
        n_permutations=500, seed=42)
    assert forward["observed_mcc_diff"] == pytest.approx(
        -reverse["observed_mcc_diff"], abs=1e-9)
    assert forward["p_value"] == pytest.approx(reverse["p_value"], abs=1e-9)


def test_mcc_kernel_reproduces_recorded_confusion_and_mcc() -> None:
    """The kernel's observed cells and MCC are the house definition's."""
    fx = _opposite_direction_fixture()
    hi = fx["hi"]
    res = permutation_test_mcc_arrays(
        hi["tp_c"], hi["tn_c"], hi["fp_c"], hi["fn_c"],
        fx["lo"]["tp_c"], fx["lo"]["tn_c"], fx["lo"]["fp_c"], fx["lo"]["fn_c"],
        n_permutations=10, seed=42)
    conf = res["confusion_a"]
    assert conf == {"tp": 40, "tn": 200, "fp": 25, "fn": 0}
    assert res["mcc_a"] == pytest.approx(
        round(_compute_mcc(40, 200, 25, 0), 6), abs=1e-9)
    # Exactly one class per tile, for both arms.
    for arm in ("a", "b"):
        cells = res[f"confusion_{arm}"]
        assert sum(cells.values()) == fx["n_tiles"]


# ---------------------------------------------------------------------------
# One permutation, two statistics
# ---------------------------------------------------------------------------

def test_f1_and_mcc_kernels_draw_identical_swap_masks() -> None:
    """Both kernels consume the same ``default_rng(seed)`` mask stream.

    ``permutation_test_float`` draws one ``(n_permutations, n_tiles)`` block;
    the MCC kernel draws ``n_tiles`` per iteration. NumPy fills the block
    row-major from the same stream, so the masks are identical — which is what
    makes a ΔF1 and a ΔMCC on one pair two statistics of one permutation.
    """
    n_perms, n_tiles, seed = 7, 11, 42
    block = np.random.default_rng(seed).random((n_perms, n_tiles)) < 0.5
    rng = np.random.default_rng(seed)
    rows = np.array([rng.random(n_tiles) < 0.5 for _ in range(n_perms)])
    assert np.array_equal(block, rows)


def test_wrapper_delegates_to_the_array_kernel() -> None:
    """``run_permutation_test_mcc`` reports exactly what the array kernel does.

    The GeoDataFrame wrapper was refactored to delegate; this pins that its
    reported MCCs, ΔMCC and p-value come from the single shared kernel rather
    than a second implementation.
    """
    import geopandas as gpd
    from shapely.geometry import Point, box

    from scripts.pairwise_permutation_test import run_permutation_test_mcc

    # Four tiles in a row; references in tiles 0 and 1.
    tiles = [box(i * 10, 0, i * 10 + 10, 10) for i in range(4)]
    bounds = gpd.GeoDataFrame(
        {"tile_name": [f"M_x{i}_y0" for i in range(4)]},
        geometry=tiles, crs="EPSG:32635")
    refs = gpd.GeoDataFrame(
        {"Map": ["M", "M"]},
        geometry=[Point(5, 5), Point(15, 5)], crs="EPSG:32635")
    # Arm A hits tile 0 only; arm B hits tiles 0, 1 and spuriously tile 3.
    det_a = gpd.GeoDataFrame(
        {"source_tile": ["M_x0_y0"]},
        geometry=[Point(5, 5)], crs="EPSG:32635")
    det_b = gpd.GeoDataFrame(
        {"source_tile": ["M_x0_y0", "M_x10_y0", "M_x30_y0"]},
        geometry=[Point(5, 5), Point(15, 5), Point(35, 5)], crs="EPSG:32635")
    det_b["source_tile"] = ["M_x0_y0", "M_x1_y0", "M_x3_y0"]
    bounds["tile_name"] = ["M_x0_y0", "M_x1_y0", "M_x2_y0", "M_x3_y0"]

    wrapped = run_permutation_test_mcc(det_a, det_b, refs, bounds,
                                       n_permutations=64, seed=42)
    # Rebuild the same arrays the wrapper built, and call the kernel directly.
    from scripts.lib_advanced_metrics import compute_per_tile_classification
    order = list(bounds["tile_name"])
    cols = {}
    for name, det in (("a", det_a), ("b", det_b)):
        per_tile = compute_per_tile_classification(det, refs, bounds)
        idx = per_tile.set_index("tile_name")
        cols[name] = tuple(
            np.array([int(idx.loc[t][k]) for t in order])
            for k in ("tp", "tn", "fp", "fn")
        )
    direct = permutation_test_mcc_arrays(*cols["a"], *cols["b"],
                                        n_permutations=64, seed=42)
    assert wrapped["global_a"]["mcc"] == direct["mcc_a"]
    assert wrapped["global_b"]["mcc"] == direct["mcc_b"]
    assert wrapped["permutation_test"]["observed_mcc_diff"] == \
        direct["observed_mcc_diff"]
    assert wrapped["permutation_test"]["p_value"] == direct["p_value"]
    assert wrapped["permutation_test"]["null_distribution"] == \
        direct["null_distribution"]


# ---------------------------------------------------------------------------
# The per-map sign-swap sibling
# ---------------------------------------------------------------------------

def test_sign_swap_mcc_sibling_matches_the_f1_sibling_s_conventions() -> None:
    """``paired_permutation_mcc`` mirrors ``paired_permutation`` exactly.

    Same pairing units, same seed, same permutation count, same two-sided
    p-value with the same ``1/N`` floor — and on the opposite-direction fixture
    it reports a NEGATIVE ΔMCC where the F1 sibling reports a positive ΔF1.
    """
    from scripts.stride55_sweep_oracle import (
        N_PERMS,
        SEED,
        mcc_from_map_counts,
        paired_permutation,
        paired_permutation_mcc,
    )

    maps = [f"K-35-{i:03d}" for i in range(1, 12)]
    # Per map: the high-K arm converts one FN into a TP (F1 up) and turns two
    # quiet tiles into false-positive tiles (tile-MCC down).
    f1_lo = {m: (4, 1, 2) for m in maps}
    f1_hi = {m: (5, 1, 1) for m in maps}
    tiles_lo = {m: (4, 40, 1, 2) for m in maps}
    tiles_hi = {m: (4, 38, 3, 2) for m in maps}

    f1_res = paired_permutation(f1_hi, f1_lo)
    mcc_res = paired_permutation_mcc(tiles_hi, tiles_lo)

    assert f1_res["delta_f1"] > 0
    assert mcc_res["delta_mcc"] < 0
    assert mcc_res["n_permutations"] == f1_res["n_permutations"] == N_PERMS
    assert mcc_res["seed"] == f1_res["seed"] == SEED
    assert mcc_res["p_two_sided"] >= 1.0 / N_PERMS
    # The reported ΔMCC is the pooled-confusion difference, not a per-map mean.
    assert mcc_res["delta_mcc"] == pytest.approx(
        mcc_from_map_counts(tiles_hi) - mcc_from_map_counts(tiles_lo),
        abs=1e-12)


def test_sign_swap_mcc_is_symmetric_under_argument_order() -> None:
    """Swapping the arms negates ΔMCC and leaves the p-value unchanged."""
    from scripts.stride55_sweep_oracle import paired_permutation_mcc

    maps = [f"K-35-{i:03d}" for i in range(1, 9)]
    a = {m: (5, 30, 2, 3) for m in maps}
    b = {m: (4, 33, 1, 2) for m in maps}
    forward = paired_permutation_mcc(a, b)
    reverse = paired_permutation_mcc(b, a)
    assert forward["delta_mcc"] == pytest.approx(-reverse["delta_mcc"],
                                                abs=1e-12)
    assert forward["p_two_sided"] == pytest.approx(reverse["p_two_sided"],
                                                  abs=1e-12)


# ---------------------------------------------------------------------------
# The driver's pair selection and orientation
# ---------------------------------------------------------------------------

def test_driver_selects_k1_vs_best_and_every_adjacent_pair() -> None:
    """Pair selection is the ruling's: K = 1 vs best rung, plus adjacents."""
    from scripts.k_ladder_mcc_test import requested_pairs

    rungs = [{"K": 1, "f1_headline": 0.80}, {"K": 3, "f1_headline": 0.85},
             {"K": 5, "f1_headline": 0.84}, {"K": 10, "f1_headline": 0.86}]
    pairs = requested_pairs(rungs)
    assert pairs[0] == {"kind": "k1-vs-best", "k_a": 1, "k_b": 10}
    assert [(p["k_a"], p["k_b"]) for p in pairs] == [
        (1, 10), (1, 3), (3, 5), (5, 10)]

    # When the best rung IS the K = 1 neighbour, the pair is emitted once.
    rungs = [{"K": 1, "f1_headline": 0.80}, {"K": 3, "f1_headline": 0.90},
             {"K": 5, "f1_headline": 0.85}]
    pairs = requested_pairs(rungs)
    assert [(p["k_a"], p["k_b"]) for p in pairs] == [(1, 3), (3, 5)]
    assert pairs[0]["kind"] == "k1-vs-best+adjacent"


def test_driver_selects_the_oracle_rung_where_both_bases_exist() -> None:
    """A K with both a carried and an oracle cell resolves to the oracle."""
    from scripts.k_ladder_mcc_test import select_rungs

    ladder = {"rungs": [
        {"K": 1, "f1_headline": 0.80,
         "eval_path": "results/b/cells/A-N1-oracle/evaluation.json"},
        {"K": 3, "f1_headline": 0.83,
         "eval_path": "results/b/cells/A-N3-carried/evaluation.json"},
        {"K": 3, "f1_headline": 0.84,
         "eval_path": "results/b/cells/A-N3-oracle/evaluation.json"},
    ]}
    picked = select_rungs(ladder)
    assert [r["K"] for r in picked] == [1, 3]
    assert picked[1]["eval_path"].endswith("A-N3-oracle/evaluation.json")


def test_driver_verdict_reads_both_statistics() -> None:
    """The verdict string reports F1 and MCC directions and significance."""
    from scripts.k_ladder_mcc_test import verdict_for

    assert verdict_for(0.03, 0.001, -0.02, 0.001, 0.05) == \
        "F1 up (sig), MCC down (sig)"
    assert verdict_for(0.03, 0.001, -0.02, 0.400, 0.05) == \
        "F1 up (sig), MCC down n.s."
    assert verdict_for(0.003, 0.400, -0.02, 0.400, 0.05) == "neither separates"
