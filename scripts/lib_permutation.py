#!/usr/bin/env python3
"""
Paired permutation tests on per-tile detection counts (PI ruling D42).

Why this module exists
----------------------
PI ruling D42 (2026-10-05, ``planning/pi-decisions-2026-09-20.md``): every
contrast is tested by the paired tile-swap permutation test with
Benjamini-Hochberg (BH) correction, and no p-value is read from a bootstrap.
The retest-era bootstrap p-value (2 x the minority tail, floored at 1/B,
read off an uncentred bootstrap) sits at its floor whenever two arms differ
on a few tiles in one direction, identical outputs included; on 10,035
replicate pairs it rejected 12.5 % of sparse-discordance pairs against the
permutation test's 6.2 % (``reports/retest-bootstrap-check-2026-10-05.md``).
Bootstrap confidence intervals stay in use; only the test changes.

The project already had the tile-swap test in two board scripts
(``pairwise_permutation_test.run_permutation_test`` on GeoDataFrames,
``n1_baseline_leaderboard_tiering.permutation_test_float`` on arrays). This
module is the one array-level kernel every other contrast now calls:

* :func:`paired_permutation_test`: two arms, F1, precision and recall from
  ONE shared swap mask. On single-run (1-D) arrays it reproduces
  ``permutation_test_float`` exactly (same random stream, same arithmetic;
  pinned by ``tests/test_lib_permutation.py``). Multi-run arms (2-D,
  runs x tiles) swap each tile's whole run block, and the statistic is the
  mean over runs of each run's micro metric (the E22 per-run convention).
* :func:`paired_interaction_permutation`: a 2 x 2 difference of differences,
  ``(m(a) - m(b)) - (m(c) - m(d))``; each tile exchanges the pair ``(a, b)``
  with the pair ``(c, d)`` with probability 0.5.
* :func:`label_permutation_sums`: K conditions, each tile's K condition
  labels permuted uniformly and independently (the K-arm generalisation of
  the tile swap, used for H1's pooled contrast); yields summed counts and
  leaves the statistic to the caller.
* :func:`bh_adjust`: BH step-up adjusted p-values.

The test and its limits
-----------------------
The null is that, within each tile, the arms' labels are exchangeable, which
is exactly what identical requests satisfy, so the test is exact for it. It
compares the OUTPUTS it is given: it treats each output as fixed and carries
no run-to-run (pass-level) variance, so a small p between two single runs
says the outputs differ, not that the configurations do (tracker W2.7, S-10).

The p-value is ``mean(|null| >= |observed|)``, two-sided, as on the signed
boards; it can be exactly 0, which prose reports as "p < 1/n_permutations"
(D42 implementation default (d), Session 161).

Usage::

    from lib_permutation import paired_permutation_test
    res = paired_permutation_test({"tp": tp_a, "fp": fp_a, "fn": fn_a},
                                  {"tp": tp_b, "fp": fp_b, "fn": fn_b})
    res["metrics"]["f1"]["p_value"]

Created: 2026-10-05 (Session 161, D42)
Author: Shawn Ross, Claude Code
Licence: Apache 2.0
"""

from __future__ import annotations

from collections.abc import Iterator, Mapping, Sequence

import numpy as np

#: Project-standard permutation count and seed (the boards' values).
N_PERMUTATIONS = 10_000
SEED = 42

#: Permutations drawn per chunk. Chunking bounds memory on the 8,541-tile
#: corpus; it does not change the random stream (rows are drawn in order).
DEFAULT_CHUNK = 500

COUNT_KEYS = ("tp", "fp", "fn")
METRICS = ("f1", "precision", "recall")

#: Recorded in every result so an artefact says which test produced its p.
METHOD = ("paired tile-swap permutation test (PI ruling D42): per-tile label "
          "swap with probability 0.5, two-sided p = mean(|null| >= |observed|)")


# ---------------------------------------------------------------------------
# Metric formulas. The scalar form mirrors n1_baseline_leaderboard_tiering's
# micro_f1 (and pairwise_permutation_test._compute_f1); the vector form
# mirrors its _micro_f1_vec. Both are kept exactly so the two-arm test
# reproduces the signed boards' p-values bit for bit.
# ---------------------------------------------------------------------------

def scalar_metrics(tp: float, fp: float, fn: float) -> dict[str, float]:
    """Micro precision, recall and F1 from aggregate counts.

    Returns 0.0 for a zero denominator, and F1 = 0.0 whenever ``tp == 0``,
    as the board scripts do.

    Args:
        tp: Aggregate true positives (int or float pass-mean sum).
        fp: Aggregate false positives.
        fn: Aggregate false negatives.

    Returns:
        Dict with ``f1``, ``precision`` and ``recall``.

    Example:
        >>> round(scalar_metrics(8, 2, 2)["f1"], 6)
        0.8
    """
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    if tp == 0 or precision + recall == 0:
        f1 = 0.0
    else:
        f1 = 2 * precision * recall / (precision + recall)
    return {"f1": f1, "precision": precision, "recall": recall}


def vector_metrics(tp: np.ndarray, fp: np.ndarray,
                   fn: np.ndarray) -> dict[str, np.ndarray]:
    """Vectorised :func:`scalar_metrics` over arrays of aggregate counts.

    Args:
        tp: Aggregate true positives, any shape (float).
        fp: Aggregate false positives, same shape.
        fn: Aggregate false negatives, same shape.

    Returns:
        Dict of arrays with ``f1``, ``precision`` and ``recall``.
    """
    tp = np.asarray(tp, dtype=float)
    fp = np.asarray(fp, dtype=float)
    fn = np.asarray(fn, dtype=float)
    denom_p = tp + fp
    denom_r = tp + fn
    precision = np.divide(tp, denom_p, out=np.zeros_like(tp), where=denom_p > 0)
    recall = np.divide(tp, denom_r, out=np.zeros_like(tp), where=denom_r > 0)
    denom_f = precision + recall
    f1 = np.divide(2 * precision * recall, denom_f, out=np.zeros_like(tp),
                   where=denom_f > 0)
    f1[tp == 0] = 0.0
    return {"f1": f1, "precision": precision, "recall": recall}


# ---------------------------------------------------------------------------
# Input handling
# ---------------------------------------------------------------------------

def _as_runs(counts: Mapping[str, np.ndarray]) -> dict[str, np.ndarray]:
    """Return each count array as float, shape ``[n_runs, n_tiles]``.

    A 1-D array is one run. Raises if the three arrays disagree in shape.
    """
    out = {}
    for key in COUNT_KEYS:
        arr = np.asarray(counts[key], dtype=float)
        if arr.ndim == 1:
            arr = arr[np.newaxis, :]
        if arr.ndim != 2:
            raise ValueError(f"'{key}' must be 1-D (tiles) or 2-D (runs x tiles), "
                             f"got shape {arr.shape}")
        out[key] = arr
    shapes = {out[k].shape for k in COUNT_KEYS}
    if len(shapes) != 1:
        raise ValueError(f"tp/fp/fn shapes differ: {shapes}")
    return out


def _check_aligned(*arms: dict[str, np.ndarray]) -> tuple[int, int]:
    """Assert every arm has the same (runs, tiles) shape; return it."""
    shapes = {arm["tp"].shape for arm in arms}
    if len(shapes) != 1:
        raise ValueError(f"arms are not aligned (runs x tiles differ): {shapes} — "
                         "a paired test needs the same tiles, in the same order, "
                         "and the same number of runs in every arm")
    n_runs, n_tiles = shapes.pop()
    return n_runs, n_tiles


def n_discordant_tiles(*arms: Mapping[str, np.ndarray]) -> int:
    """Number of tiles on which any count differs between the arms (k).

    k is what decides how informative a paired test can be: two arms that
    differ on three tiles have at most 2**3 distinct swap outcomes.

    Args:
        *arms: Two or more count mappings, 1-D or 2-D, aligned.

    Returns:
        The count of discordant tiles.
    """
    runs = [_as_runs(a) for a in arms]
    _check_aligned(*runs)
    differs = np.zeros(runs[0]["tp"].shape[1], dtype=bool)
    for other in runs[1:]:
        for key in COUNT_KEYS:
            differs |= (other[key] != runs[0][key]).any(axis=0)
    return int(differs.sum())


def swap_masks(n_permutations: int, n_tiles: int, seed: int,
               chunk: int = DEFAULT_CHUNK) -> Iterator[np.ndarray]:
    """Yield boolean swap masks, ``chunk`` permutations at a time.

    The concatenated chunks equal ``rng.random((n_permutations, n_tiles))
    < 0.5`` drawn in one call, so chunking never changes a p-value.

    Args:
        n_permutations: Total permutations.
        n_tiles: Tiles per permutation.
        seed: Seed for ``numpy.random.default_rng``.
        chunk: Permutations per yielded block.

    Yields:
        Boolean arrays of shape ``[<= chunk, n_tiles]``.
    """
    rng = np.random.default_rng(seed)
    done = 0
    while done < n_permutations:
        size = min(chunk, n_permutations - done)
        yield rng.random((size, n_tiles)) < 0.5
        done += size


def _arm_statistic_scalar(arm: dict[str, np.ndarray]) -> dict[str, float]:
    """Observed statistic: mean over runs of each run's scalar micro metrics."""
    per_run = [scalar_metrics(arm["tp"][r].sum(), arm["fp"][r].sum(),
                              arm["fn"][r].sum())
               for r in range(arm["tp"].shape[0])]
    return {m: float(np.mean([pr[m] for pr in per_run])) for m in METRICS}


def _arm_statistic_vector(sums: dict[str, np.ndarray]) -> dict[str, np.ndarray]:
    """Null statistic from swapped sums of shape ``[n_runs, chunk]``."""
    vm = vector_metrics(sums["tp"], sums["fp"], sums["fn"])
    return {m: vm[m].mean(axis=0) for m in METRICS}


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def paired_permutation_test(
    a: Mapping[str, np.ndarray],
    b: Mapping[str, np.ndarray],
    *,
    n_permutations: int = N_PERMUTATIONS,
    seed: int = SEED,
    chunk: int = DEFAULT_CHUNK,
) -> dict:
    """Paired tile-swap permutation test of arm A minus arm B.

    One swap mask per permutation serves all three metrics, so F1,
    precision and recall are tested on the same null draws.

    Args:
        a: Arm A counts: ``tp``, ``fp``, ``fn`` arrays, 1-D (tiles) or 2-D
            (runs x tiles), aligned with ``b`` tile for tile.
        b: Arm B counts, same shape as ``a``.
        n_permutations: Permutations (default 10,000, the boards' value).
        seed: Random seed (default 42).
        chunk: Permutations per block (memory only; no effect on results).

    Returns:
        Dict with ``n_tiles``, ``n_runs``, ``n_discordant_tiles``,
        ``n_permutations``, ``seed``, ``method`` and ``metrics``: for each of
        f1, precision and recall, ``a``, ``b``, ``observed_diff`` (A - B),
        ``p_value``, ``null_mean`` and ``null_std``.

    Example:
        >>> tp = np.array([3, 0, 2]); z = np.zeros(3)
        >>> r = paired_permutation_test({"tp": tp, "fp": z, "fn": z},
        ...                             {"tp": tp, "fp": z, "fn": z})
        >>> r["metrics"]["f1"]["p_value"]
        1.0
    """
    arm_a, arm_b = _as_runs(a), _as_runs(b)
    n_runs, n_tiles = _check_aligned(arm_a, arm_b)

    obs_a = _arm_statistic_scalar(arm_a)
    obs_b = _arm_statistic_scalar(arm_b)
    observed = {m: obs_a[m] - obs_b[m] for m in METRICS}

    null = {m: np.empty(n_permutations) for m in METRICS}
    done = 0
    for mask in swap_masks(n_permutations, n_tiles, seed, chunk):
        size = mask.shape[0]
        sums_a, sums_b = {}, {}
        for key in COUNT_KEYS:
            # [n_runs, size]: each run's tile sums after the swap. The
            # np.where-then-sum form matches the board kernel's arithmetic.
            sums_a[key] = np.stack([np.where(mask, arm_b[key][r], arm_a[key][r]).sum(axis=1)
                                    for r in range(n_runs)])
            sums_b[key] = np.stack([np.where(mask, arm_a[key][r], arm_b[key][r]).sum(axis=1)
                                    for r in range(n_runs)])
        stat_a = _arm_statistic_vector(sums_a)
        stat_b = _arm_statistic_vector(sums_b)
        for m in METRICS:
            null[m][done:done + size] = stat_a[m] - stat_b[m]
        done += size

    metrics = {}
    for m in METRICS:
        metrics[m] = {
            "a": obs_a[m],
            "b": obs_b[m],
            "observed_diff": observed[m],
            "p_value": float(np.mean(np.abs(null[m]) >= abs(observed[m]))),
            "null_mean": float(np.mean(null[m])),
            "null_std": float(np.std(null[m])),
        }
    return {
        "method": METHOD,
        "n_tiles": n_tiles,
        "n_runs": n_runs,
        "n_discordant_tiles": n_discordant_tiles(arm_a, arm_b),
        "n_permutations": n_permutations,
        "seed": seed,
        "metrics": metrics,
    }


def paired_interaction_permutation(
    a: Mapping[str, np.ndarray],
    b: Mapping[str, np.ndarray],
    c: Mapping[str, np.ndarray],
    d: Mapping[str, np.ndarray],
    *,
    metric: str = "f1",
    n_permutations: int = N_PERMUTATIONS,
    seed: int = SEED,
    chunk: int = DEFAULT_CHUNK,
) -> dict:
    """Permutation test of the 2 x 2 interaction ``(m(a) - m(b)) - (m(c) - m(d))``.

    Under the null that, within each tile, the factor-level pair ``(a, b)``
    is exchangeable with the pair ``(c, d)``, each tile swaps the two pairs
    with probability 0.5 (``a`` with ``c`` and ``b`` with ``d``, together).
    Swapping every tile negates the statistic, so the null is symmetric.

    Args:
        a: Counts, first level of factor 1, first level of factor 2.
        b: Counts, first level of factor 1, second level of factor 2.
        c: Counts, second level of factor 1, first level of factor 2.
        d: Counts, second level of factor 1, second level of factor 2.
        metric: ``f1``, ``precision`` or ``recall``.
        n_permutations: Permutations (default 10,000).
        seed: Random seed (default 42).
        chunk: Permutations per block (memory only).

    Returns:
        Dict with ``observed`` (the difference of differences),
        ``p_value``, ``null_mean``, ``null_std``, ``n_tiles``,
        ``n_permutations``, ``seed`` and ``method``.
    """
    if metric not in METRICS:
        raise ValueError(f"metric must be one of {METRICS}, got {metric!r}")
    arms = [_as_runs(x) for x in (a, b, c, d)]
    n_runs, n_tiles = _check_aligned(*arms)

    obs = [_arm_statistic_scalar(x)[metric] for x in arms]
    observed = (obs[0] - obs[1]) - (obs[2] - obs[3])

    null = np.empty(n_permutations)
    done = 0
    for mask in swap_masks(n_permutations, n_tiles, seed, chunk):
        size = mask.shape[0]
        stats = []
        # Swapped arm i takes arm (i + 2) % 4 where the mask is set:
        # a <-> c and b <-> d.
        for i in range(4):
            mine, partner = arms[i], arms[(i + 2) % 4]
            sums = {key: np.stack([np.where(mask, partner[key][r], mine[key][r]).sum(axis=1)
                                   for r in range(n_runs)])
                    for key in COUNT_KEYS}
            stats.append(_arm_statistic_vector(sums)[metric])
        null[done:done + size] = (stats[0] - stats[1]) - (stats[2] - stats[3])
        done += size

    return {
        "method": ("paired interaction permutation test (PI ruling D42): per tile "
                   "the pairs (a, b) and (c, d) swap with probability 0.5; "
                   "two-sided p = mean(|null| >= |observed|)"),
        "metric": metric,
        "observed": float(observed),
        "p_value": float(np.mean(np.abs(null) >= abs(observed))),
        "null_mean": float(np.mean(null)),
        "null_std": float(np.std(null)),
        "n_tiles": n_tiles,
        "n_permutations": n_permutations,
        "seed": seed,
    }


def label_permutation_sums(
    stack: np.ndarray,
    *,
    n_permutations: int = N_PERMUTATIONS,
    seed: int = SEED,
    chunk: int = 200,
) -> Iterator[np.ndarray]:
    """Yield per-condition summed counts under within-tile label permutation.

    For K conditions, each permutation draws, independently for every tile,
    a uniform random permutation of the K condition labels and gives each
    condition the counts (all runs) of the condition it was relabelled from.
    For K = 2 this is the tile swap, drawn from a different random stream.

    Args:
        stack: Float array ``[K, n_runs, n_tiles, 3]`` (TP, FP, FN last).
        n_permutations: Permutations.
        seed: Random seed.
        chunk: Permutations per yielded block (memory: chunk x tiles x K x
            runs x 3 floats).

    Yields:
        Arrays ``[<= chunk, K, n_runs, 3]`` of summed counts.
    """
    stack = np.asarray(stack, dtype=float)
    if stack.ndim != 4 or stack.shape[3] != 3:
        raise ValueError(f"stack must be [K, runs, tiles, 3], got {stack.shape}")
    n_cond, _n_runs, n_tiles, _ = stack.shape
    by_tile = np.transpose(stack, (2, 0, 1, 3))  # [T, K, R, 3]
    tile_idx = np.arange(n_tiles)[np.newaxis, :, np.newaxis]
    rng = np.random.default_rng(seed)
    done = 0
    while done < n_permutations:
        size = min(chunk, n_permutations - done)
        # perm[p, t, new] = the old condition whose counts the new label takes.
        perm = np.argsort(rng.random((size, n_tiles, n_cond)), axis=2)
        gathered = by_tile[tile_idx, perm]  # [size, T, K, R, 3]
        yield gathered.sum(axis=1)
        done += size


def bh_adjust(p_values: Sequence[float]) -> list[float]:
    """Benjamini-Hochberg step-up adjusted p-values (monotone, capped at 1).

    Args:
        p_values: Raw p-values, in any order.

    Returns:
        Adjusted p-values in the input order; reject at FDR q where
        ``adjusted <= q``.

    Example:
        >>> [round(x, 6) for x in bh_adjust([0.01, 0.04, 0.03])]
        [0.03, 0.04, 0.04]
    """
    p = np.asarray(p_values, dtype=float)
    m = len(p)
    if m == 0:
        return []
    order = np.argsort(p, kind="stable")
    ranked = p[order] * m / np.arange(1, m + 1)
    # Enforce monotonicity from the largest rank down, then cap at 1.
    adjusted_sorted = np.minimum.accumulate(ranked[::-1])[::-1]
    adjusted = np.empty(m)
    adjusted[order] = np.minimum(adjusted_sorted, 1.0)
    return [float(x) for x in adjusted]
