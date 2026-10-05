"""Tier-1 tests for scripts/lib_permutation.py (PI ruling D42).

The kernel replaces every bootstrap p-value in the project, so these tests
pin three things: (1) on single-run arrays it reproduces the signed boards'
kernel (``n1_baseline_leaderboard_tiering.permutation_test_float``) exactly;
(2) it behaves correctly where the retired bootstrap p failed (identical
arms, a handful of discordant tiles); and (3) the interaction, K-label and
BH helpers keep their stated invariants.
"""

import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from lib_permutation import (  # noqa: E402
    bh_adjust,
    label_permutation_sums,
    n_discordant_tiles,
    paired_interaction_permutation,
    paired_permutation_test,
    scalar_metrics,
    swap_masks,
)
from n1_baseline_leaderboard_tiering import permutation_test_float  # noqa: E402

pytestmark = pytest.mark.tier1


def _arm(rng: np.random.Generator, n: int, scale: float = 1.0,
         as_float: bool = False) -> dict[str, np.ndarray]:
    """Random per-tile counts; mostly-empty tiles, like the real corpora."""
    tp = rng.poisson(0.6 * scale, n)
    fp = rng.poisson(0.4, n)
    fn = rng.poisson(0.3, n)
    arm = {"tp": tp, "fp": fp, "fn": fn}
    if as_float:
        arm = {k: v / 3.0 for k, v in arm.items()}  # pass-mean style floats
    return {k: np.asarray(v, dtype=float) for k, v in arm.items()}


def _perturb(rng: np.random.Generator, arm: dict, n_tiles: int) -> dict:
    """Copy ``arm`` and change the counts on ``n_tiles`` random tiles."""
    out = {k: v.copy() for k, v in arm.items()}
    idx = rng.choice(len(arm["tp"]), n_tiles, replace=False)
    out["fp"][idx] += 1
    return out


@pytest.mark.parametrize("as_float", [False, True])
@pytest.mark.parametrize("n_changed", [3, 40, 300])
def test_reproduces_the_board_kernel_exactly(as_float, n_changed):
    """F1 p and observed difference equal permutation_test_float's."""
    rng = np.random.default_rng(7)
    a = _arm(rng, 400, as_float=as_float)
    b = _perturb(rng, a, n_changed) if n_changed < 300 else _arm(rng, 400, 1.3, as_float)
    mine = paired_permutation_test(a, b, n_permutations=3000, seed=42, chunk=128)
    board = permutation_test_float(a["tp"], a["fp"], a["fn"],
                                   b["tp"], b["fp"], b["fn"],
                                   n_permutations=3000, seed=42)
    assert round(mine["metrics"]["f1"]["p_value"], 4) == board["p_value"]
    assert round(mine["metrics"]["f1"]["observed_diff"], 6) == board["observed_diff"]
    assert round(mine["metrics"]["f1"]["null_mean"], 6) == board["null_mean"]


def test_chunking_does_not_change_the_result():
    """The random stream is drawn in row order whatever the chunk size."""
    rng = np.random.default_rng(3)
    a, b = _arm(rng, 250), _arm(rng, 250, 1.2)
    one = paired_permutation_test(a, b, n_permutations=1000, chunk=1000)
    many = paired_permutation_test(a, b, n_permutations=1000, chunk=7)
    assert one == many
    stacked = np.vstack(list(swap_masks(1000, 50, 42, chunk=33)))
    assert np.array_equal(stacked, np.random.default_rng(42).random((1000, 50)) < 0.5)


def test_identical_arms_give_p_one_on_every_metric():
    """Where the retired bootstrap p sat at its floor, the permutation p is 1."""
    rng = np.random.default_rng(11)
    a = _arm(rng, 300)
    res = paired_permutation_test(a, a, n_permutations=500)
    assert res["n_discordant_tiles"] == 0
    for m in ("f1", "precision", "recall"):
        assert res["metrics"][m]["observed_diff"] == 0.0
        assert res["metrics"][m]["p_value"] == 1.0


def test_one_discordant_tile_can_never_be_significant():
    """With k = 1 every swap gives |null| = |observed|, so p = 1."""
    rng = np.random.default_rng(5)
    a = _arm(rng, 300)
    b = _perturb(rng, a, 1)
    res = paired_permutation_test(a, b, n_permutations=500)
    assert res["n_discordant_tiles"] == 1
    assert res["metrics"]["f1"]["p_value"] == 1.0


def test_a_strong_effect_is_detected():
    """A large, consistent difference gives a small p on F1 and precision."""
    rng = np.random.default_rng(9)
    a = _arm(rng, 300)
    b = {k: v.copy() for k, v in a.items()}
    b["fp"] = b["fp"] + 2  # B adds two false positives on every tile
    res = paired_permutation_test(a, b, n_permutations=1000)
    assert res["metrics"]["f1"]["observed_diff"] > 0
    assert res["metrics"]["f1"]["p_value"] < 0.01
    assert res["metrics"]["precision"]["p_value"] < 0.01
    assert res["metrics"]["recall"]["p_value"] == 1.0  # recall is untouched


def test_observed_metrics_match_the_scalar_formula():
    """``a`` and ``b`` are the arms' micro metrics on the full tile set."""
    rng = np.random.default_rng(2)
    a, b = _arm(rng, 120), _arm(rng, 120)
    res = paired_permutation_test(a, b, n_permutations=50)
    want = scalar_metrics(a["tp"].sum(), a["fp"].sum(), a["fn"].sum())
    for m, v in want.items():
        assert res["metrics"][m]["a"] == pytest.approx(v, abs=1e-12)


def test_one_run_as_a_2d_block_equals_the_1d_arm():
    """A [1, T] block is the same test as a [T] vector."""
    rng = np.random.default_rng(4)
    a, b = _arm(rng, 200), _arm(rng, 200, 1.1)
    flat = paired_permutation_test(a, b, n_permutations=400)
    block = paired_permutation_test({k: v[None, :] for k, v in a.items()},
                                    {k: v[None, :] for k, v in b.items()},
                                    n_permutations=400)
    assert flat["metrics"] == block["metrics"]


def test_multi_run_statistic_is_the_mean_of_per_run_metrics():
    """Runs x tiles arms: observed = mean over runs of each run's F1."""
    rng = np.random.default_rng(6)
    runs_a = [_arm(rng, 150) for _ in range(3)]
    runs_b = [_arm(rng, 150, 1.4) for _ in range(3)]
    a = {k: np.stack([r[k] for r in runs_a]) for k in ("tp", "fp", "fn")}
    b = {k: np.stack([r[k] for r in runs_b]) for k in ("tp", "fp", "fn")}
    res = paired_permutation_test(a, b, n_permutations=300)
    f1_a = np.mean([scalar_metrics(r["tp"].sum(), r["fp"].sum(), r["fn"].sum())["f1"]
                    for r in runs_a])
    assert res["n_runs"] == 3
    assert res["metrics"]["f1"]["a"] == pytest.approx(f1_a, abs=1e-12)


def test_misaligned_arms_are_refused():
    """Different tile counts or run counts raise rather than mis-pair."""
    rng = np.random.default_rng(1)
    with pytest.raises(ValueError, match="not aligned"):
        paired_permutation_test(_arm(rng, 10), _arm(rng, 11), n_permutations=10)
    two_runs = {k: np.stack([v, v]) for k, v in _arm(rng, 10).items()}
    with pytest.raises(ValueError, match="not aligned"):
        paired_permutation_test(_arm(rng, 10), two_runs, n_permutations=10)


def test_interaction_null_and_symmetry():
    """No interaction gives p = 1; a real one gives a small p."""
    rng = np.random.default_rng(12)
    a, b = _arm(rng, 300), _arm(rng, 300, 1.3)
    flat = paired_interaction_permutation(a, b, a, b, n_permutations=400)
    assert flat["observed"] == 0.0
    assert flat["p_value"] == 1.0
    # The factor-2 effect exists at level 1 only: c == d, a far below b.
    c = _arm(rng, 300)
    b_strong = {k: v.copy() for k, v in a.items()}
    b_strong["fp"] = b_strong["fp"] - np.minimum(b_strong["fp"], 1)
    a_noisy = {k: v.copy() for k, v in a.items()}
    a_noisy["fp"] = a_noisy["fp"] + 2
    res = paired_interaction_permutation(a_noisy, b_strong, c, c, n_permutations=1000)
    assert res["observed"] < 0
    assert res["p_value"] < 0.01


def test_label_permutation_conserves_totals_and_identity():
    """Relabelling moves counts between conditions but never creates them."""
    rng = np.random.default_rng(8)
    stack = rng.poisson(0.7, (5, 3, 60, 3)).astype(float)  # K, R, T, 3
    total = stack.sum(axis=(0, 2))  # [R, 3]
    for sums in label_permutation_sums(stack, n_permutations=120, chunk=50):
        assert sums.shape[1:] == (5, 3, 3)
        assert np.allclose(sums.sum(axis=1), total[None, :, :])
    same = np.broadcast_to(stack[:1], stack.shape).copy()  # five identical conditions
    for sums in label_permutation_sums(same, n_permutations=30):
        assert np.allclose(sums, same.sum(axis=2)[None])


def test_discordance_count():
    """k counts tiles where any count differs."""
    rng = np.random.default_rng(10)
    a = _arm(rng, 80)
    assert n_discordant_tiles(a, _perturb(rng, a, 6)) == 6


def test_bh_adjust_matches_hand_computation():
    """Step-up adjustment, monotone and capped, in the input order."""
    got = bh_adjust([0.01, 0.04, 0.03, 0.5])
    # Sorted 0.01, 0.03, 0.04, 0.5 -> 0.04, 0.06, 0.0533, 0.5 -> monotone.
    assert got == pytest.approx([0.04, 0.0533333, 0.0533333, 0.5], abs=1e-6)
    assert bh_adjust([]) == []
    assert bh_adjust([0.9, 0.95]) == pytest.approx([0.95, 0.95])


def test_bh_adjust_is_the_boards_bh():
    """bh_adjust and apply_bh_correction agree, ties included."""
    from apply_fdr_correction import apply_bh_correction

    rng = np.random.default_rng(13)
    p = list(np.round(rng.random(40), 2))  # rounding forces ties
    assert bh_adjust(p) == pytest.approx(apply_bh_correction(p), abs=0)
