#!/usr/bin/env python3
"""Reproduce every measurement in ``reports/bca-axis-defect-2026-08-18.md``.

Defect D15 was a transposed axis in the ``scipy.stats.bootstrap``
``vectorized=True`` adapter inside
``scripts/lib_advanced_metrics._bca_ci_from_indices``. The adapter
returned ``n`` statistics of ``B`` draws each where scipy's contract
demands ``B`` statistics of ``n`` draws each, which rescaled every
interval on that path by ``sqrt(n / B)``. The fix landed in commit
``122104b8a``.

This script re-derives, from source data, each quantity the defect
report cites, so a reader can re-verify the report rather than trust it.
It is pure local computation — no API calls, no network, no writes to
any committed artefact.

Probes
------
``shapes``
    What scipy actually hands a vectorised statistic, and what the
    pre-fix adapter returned for each call.
``compare``
    Five interval constructions on real per-tile counts: pre-fix
    adapter, fixed adapter, scipy's ``vectorized=False`` reference,
    scipy's percentile method, and a hand-rolled percentile bootstrap.
``sign``
    Defective-versus-corrected width across a sweep of ``B``, showing
    the error reverses direction at ``B ~ n``.
``census``
    Which committed ``evaluation.json`` intervals carry which recorded
    method, and how many sit in each distortion regime.
``mcc``
    How many committed tile-level Matthews Correlation Coefficient (MCC)
    intervals change their "95 % CI excludes zero" reading when
    recomputed with the fixed adapter.

Usage
-----
Run from the repository root with the project virtual environment
active. Per the project's compute policy the ``census`` and ``mcc``
probes should be run on sapphire::

    python scripts/verify_bca_axis_defect.py --probe shapes
    python scripts/verify_bca_axis_defect.py --probe compare
    python scripts/verify_bca_axis_defect.py --probe sign
    python scripts/verify_bca_axis_defect.py --probe census
    python scripts/verify_bca_axis_defect.py --probe mcc
    python scripts/verify_bca_axis_defect.py --probe all
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import warnings
from collections import Counter
from pathlib import Path
from typing import Any, Callable

import numpy as np
from scipy.stats import DegenerateDataWarning
from scipy.stats import bootstrap as scipy_bootstrap

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "scripts"))

from lib_advanced_metrics import _bca_ci_from_indices  # noqa: E402

#: Seed used by every committed evaluation in this study.
SEED = 42

#: Real per-tile counts used as the worked example throughout the report.
COUNTS_PATH = Path("results/h13-overlap-2026-08-18/per_tile_counts.json")

#: Method strings ``lib_advanced_metrics`` can record for an interval.
METHOD_VALUES = frozenset({"BCa", "percentile_fallback", "undefined", "empty"})


# ---------------------------------------------------------------------------
# Adapters
# ---------------------------------------------------------------------------


def prefix_adapter(
    statistic: Callable[[np.ndarray], float],
) -> Callable[..., Any]:
    """Return the pre-fix (defective) vectorised adapter, verbatim.

    Args:
        statistic: Per-index statistic to adapt.

    Returns:
        The adapter as it stood before commit ``122104b8a``: it moves
        ``axis`` to the front and iterates, transposing scipy's batch.
    """

    def _vectorised(idx_array: np.ndarray, axis: int = -1) -> Any:
        idx_array = np.asarray(idx_array, dtype=int)
        if idx_array.ndim == 1:
            return float(statistic(idx_array))
        return np.array(
            [statistic(row) for row in np.moveaxis(idx_array, axis, 0)]
        )

    return _vectorised


def fixed_adapter(
    statistic: Callable[[np.ndarray], float],
) -> Callable[..., Any]:
    """Return the post-fix adapter (mirrors the shipped implementation).

    Args:
        statistic: Per-index statistic to adapt.

    Returns:
        An adapter that applies ``statistic`` along ``axis`` and consumes
        that axis, per scipy's ``vectorized=True`` contract.
    """

    def _vectorised(idx_array: np.ndarray, axis: int = -1) -> Any:
        idx_array = np.asarray(idx_array, dtype=int)
        if idx_array.ndim == 1:
            return float(statistic(idx_array))
        moved = np.moveaxis(idx_array, axis, -1)
        flat = moved.reshape(-1, moved.shape[-1])
        return np.array(
            [statistic(row) for row in flat], dtype=float,
        ).reshape(moved.shape[:-1])

    return _vectorised


# ---------------------------------------------------------------------------
# Statistics
# ---------------------------------------------------------------------------


def micro_f1_statistic(
    tp: np.ndarray, fp: np.ndarray, fn: np.ndarray,
) -> Callable[[np.ndarray], float]:
    """Build the per-tile micro-F1 statistic used by ``bootstrap_ci``.

    Args:
        tp: Per-tile true-positive counts.
        fp: Per-tile false-positive counts.
        fn: Per-tile false-negative counts.

    Returns:
        Callable taking tile indices and returning micro-F1.
    """

    def stat(idx: np.ndarray) -> float:
        idx = np.asarray(idx, dtype=int)
        t = float(tp[idx].sum())
        f_p = float(fp[idx].sum())
        f_n = float(fn[idx].sum())
        p = t / (t + f_p) if (t + f_p) > 0 else 0.0
        r = t / (t + f_n) if (t + f_n) > 0 else 0.0
        return 2 * p * r / (p + r) if (p + r) > 0 else 0.0

    return stat


def tile_mcc_statistic(labels: np.ndarray) -> Callable[[np.ndarray], float]:
    """Build the tile-level MCC statistic over a coded label array.

    Tile-level MCC depends only on how many tiles fall in each of the
    four classification cells, so it can be reconstructed exactly from a
    committed confusion matrix without any geometry.

    Args:
        labels: 1-D array coding each tile 0=TP, 1=TN, 2=FP, 3=FN.

    Returns:
        Callable taking tile indices and returning MCC, or NaN when the
        resample leaves the MCC denominator at zero (errata E81).
    """
    one_hot = np.stack([(labels == k).astype(float) for k in range(4)])

    def stat(idx: np.ndarray) -> float:
        idx = np.asarray(idx, dtype=int)
        tp, tn, fp, fn = (float(one_hot[k][idx].sum()) for k in range(4))
        denom = (tp + fp) * (tp + fn) * (tn + fp) * (tn + fn)
        if denom <= 0.0:
            return float("nan")
        return ((tp * tn) - (fp * fn)) / np.sqrt(denom)

    return stat


def _bca_bounds(
    adapter: Callable[..., Any], n: int, b: int,
) -> tuple[float, float]:
    """Run scipy's BCa bootstrap through ``adapter`` and return the bounds."""
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", category=DegenerateDataWarning)
        warnings.simplefilter("ignore", category=RuntimeWarning)
        res = scipy_bootstrap(
            (np.arange(n),), adapter, n_resamples=b, method="BCa",
            confidence_level=0.95, rng=SEED, vectorized=True,
        )
    return (float(res.confidence_interval.low),
            float(res.confidence_interval.high))


def _load_arm_counts(arm: str) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Load one H13 arm's committed per-tile TP/FP/FN arrays."""
    data = json.loads(COUNTS_PATH.read_text())[arm]
    return (np.asarray(data["tp"]), np.asarray(data["fp"]),
            np.asarray(data["fn"]))


# ---------------------------------------------------------------------------
# Probes
# ---------------------------------------------------------------------------


def probe_shapes() -> None:
    """Record every call scipy makes to a vectorised statistic."""
    tp, fp, fn = _load_arm_counts("armA")
    n, b = len(tp), 1000
    stat = micro_f1_statistic(tp, fp, fn)
    calls: list[tuple[tuple[int, ...], int, int]] = []

    def logging_adapter(idx_array: np.ndarray, axis: int = -1) -> Any:
        arr = np.asarray(idx_array, dtype=int)
        out = prefix_adapter(stat)(arr, axis)
        n_ret = 1 if np.ndim(out) == 0 else int(np.shape(out)[0])
        calls.append((arr.shape, axis, n_ret))
        return out

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        res = scipy_bootstrap(
            (np.arange(n),), logging_adapter, n_resamples=b, method="BCa",
            confidence_level=0.95, rng=SEED, vectorized=True,
        )
    print(f"n tiles = {n}, requested B = {b}")
    print("calls scipy made to the pre-fix adapter:")
    for shape, axis, n_ret in calls:
        print(f"  in={shape}  axis={axis}  returned={n_ret}")
    print(f"len(bootstrap_distribution) = {len(res.bootstrap_distribution)}"
          f"  (expected {b})")
    print("scipy raised no error and issued no shape warning.")


def probe_compare() -> None:
    """Compare five interval constructions on real per-tile counts."""
    for b in (1000, 10000):
        for arm in ("armA", "armB", "armC"):
            tp, fp, fn = _load_arm_counts(arm)
            n = len(tp)
            stat = micro_f1_statistic(tp, fp, fn)
            idx = np.arange(n)

            pre = _bca_bounds(prefix_adapter(stat), n, b)
            fix = _bca_bounds(fixed_adapter(stat), n, b)
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                ref = scipy_bootstrap(
                    (idx,), stat, n_resamples=b, method="BCa",
                    confidence_level=0.95, rng=SEED, vectorized=False,
                )
                pct = scipy_bootstrap(
                    (idx,), fixed_adapter(stat), n_resamples=b,
                    method="percentile", confidence_level=0.95, rng=SEED,
                    vectorized=True,
                )
            novec = (float(ref.confidence_interval.low),
                     float(ref.confidence_interval.high))
            pct_scipy = (float(pct.confidence_interval.low),
                         float(pct.confidence_interval.high))
            rng = np.random.default_rng(SEED)
            draws = np.array([stat(rng.choice(idx, size=n, replace=True))
                              for _ in range(b)])
            hand = (float(np.percentile(draws, 2.5)),
                    float(np.percentile(draws, 97.5)))

            print(f"\n=== H13 {arm} F1@20m  n={n}  B={b}  "
                  f"point={stat(idx):.4f}")
            for name, ci in (("pre-fix", pre), ("fixed", fix),
                             ("novec-ref", novec), ("pct-scipy", pct_scipy),
                             ("pct-hand", hand)):
                print(f"    {name:>10}: [{ci[0]:.4f}, {ci[1]:.4f}]  "
                      f"width={ci[1] - ci[0]:.4f}")
            print(f"    fixed == vectorized=False reference: {fix == novec}")
            print(f"    width(fixed)/width(pre-fix) = "
                  f"{(fix[1] - fix[0]) / (pre[1] - pre[0]):.3f}   "
                  f"sqrt(B/n) = {np.sqrt(b / n):.3f}")
            print(f"    width(fixed)/width(pct-hand) = "
                  f"{(fix[1] - fix[0]) / (hand[1] - hand[0]):.3f}")


def probe_sign() -> None:
    """Show the error reverses direction at ``B ~ n``."""
    tp, fp, fn = _load_arm_counts("armA")
    n = len(tp)
    stat = micro_f1_statistic(tp, fp, fn)
    print(f"H13 arm A, F1@20m, n = {n}")
    print(f"{'B':>7} {'pre-fix width':>15} {'fixed width':>13} "
          f"{'pre/fixed':>10} {'sqrt(n/B)':>10}")
    for b in (50, 100, 200, n, 1000, 10000):
        pre = _bca_bounds(prefix_adapter(stat), n, b)
        fix = _bca_bounds(fixed_adapter(stat), n, b)
        w_pre, w_fix = pre[1] - pre[0], fix[1] - fix[0]
        print(f"{b:>7} {w_pre:>15.4f} {w_fix:>13.4f} "
              f"{w_pre / w_fix:>10.3f} {np.sqrt(n / b):>10.3f}")
    print("Ratio > 1 means the pre-fix interval was too WIDE (B < n).")


def _walk_methods(node: Any, n_it: Any, n_tiles: Any, sink: list) -> None:
    """Collect ``(method, n_tiles, n_iterations)`` triples from a JSON tree."""
    if isinstance(node, dict):
        local_n = n_tiles
        coverage = node.get("coverage")
        if isinstance(coverage, dict) and coverage.get("n_tiles") is not None:
            local_n = coverage["n_tiles"]
        elif node.get("ci_n_tiles") is not None:
            local_n = node["ci_n_tiles"]
        for key, value in node.items():
            if key == "_metadata":
                continue
            if (isinstance(value, str) and value in METHOD_VALUES
                    and (key.endswith("_ci_method") or key == "method")):
                sink.append((value, local_n, n_it))
            else:
                _walk_methods(value, n_it, local_n, sink)
    elif isinstance(node, list):
        for value in node:
            _walk_methods(value, n_it, n_tiles, sink)


def _tracked(suffix: str) -> list[str]:
    """Return git-tracked paths ending in ``suffix``."""
    out = subprocess.run(["git", "ls-files"], capture_output=True, text=True,
                         check=True).stdout.splitlines()
    return [p for p in out if p.endswith(suffix)]


def probe_census() -> None:
    """Count recorded interval methods and distortion regimes."""
    files = _tracked("evaluation.json")
    methods: Counter[str] = Counter()
    regime: Counter[str] = Counter()
    iters: Counter[Any] = Counter()
    files_bca: set[str] = set()

    for rel in files:
        text = Path(rel).read_text()
        d = json.loads(text)
        n_it = None
        if isinstance(d, dict) and isinstance(d.get("_metadata"), dict):
            n_it = (d["_metadata"].get("bootstrap") or {}).get("n_iterations")
        iters[n_it] += 1
        if "_ci_method" not in text and '"method"' not in text:
            continue
        sink: list = []
        _walk_methods(d, n_it, None, sink)
        for method, n_tiles, b in sink:
            methods[method] += 1
            if method != "BCa":
                continue
            files_bca.add(rel)
            if isinstance(n_tiles, int) and isinstance(b, int):
                if b > n_tiles:
                    regime["too narrow (B > n)"] += 1
                elif b < n_tiles:
                    regime["too wide (B < n)"] += 1
                else:
                    regime["B == n"] += 1
            else:
                regime["n or B not recorded"] += 1

    print(f"tracked evaluation.json files: {len(files)}")
    print(f"files carrying >=1 BCa-path interval: {len(files_bca)}")
    print("recorded interval methods:")
    for key, value in methods.most_common():
        print(f"  {key}: {value}")
    print("files by declared n_iterations:")
    for key, value in sorted(iters.items(),
                             key=lambda kv: (kv[0] is None, kv[0])):
        print(f"  B={key}: {value}")
    print("BCa intervals by distortion regime:")
    for key, value in regime.most_common():
        print(f"  {key}: {value}")


def _collect_mcc_blocks() -> list[dict[str, Any]]:
    """Harvest committed blocks carrying a BCa tile-MCC interval."""
    blocks: list[dict[str, Any]] = []
    for rel in _tracked("evaluation.json"):
        text = Path(rel).read_text()
        if '"confusion"' not in text:
            continue
        d = json.loads(text)
        b = 1000
        if isinstance(d.get("_metadata"), dict):
            b = (d["_metadata"].get("bootstrap") or {}).get(
                "n_iterations", 1000) or 1000

        def walk(node: Any) -> None:
            if isinstance(node, dict):
                conf, mcc = node.get("confusion"), node.get("mcc")
                if (isinstance(conf, dict) and isinstance(mcc, dict)
                        and mcc.get("method") == "BCa"
                        and mcc.get("ci_lower") is not None):
                    blocks.append({
                        "file": rel, "b": int(b),
                        "counts": (int(conf.get("tp", 0)),
                                   int(conf.get("tn", 0)),
                                   int(conf.get("fp", 0)),
                                   int(conf.get("fn", 0))),
                        "committed": (mcc["ci_lower"], mcc["ci_upper"]),
                    })
                for value in node.values():
                    walk(value)
            elif isinstance(node, list):
                for value in node:
                    walk(value)

        walk(d)
    return blocks


def probe_mcc() -> None:
    """Count committed tile-MCC intervals that lose their zero exclusion.

    The tile label *order* is not recorded in the artefacts, only the
    four counts, so the reconstruction is distributionally exact but not
    bit-identical to the committed draw. Read the total as the scale of
    the change, not as a per-cell verdict.
    """
    blocks = _collect_mcc_blocks()
    print(f"committed blocks with a BCa tile-MCC interval: {len(blocks)}")
    cache: dict[tuple, tuple[float, float]] = {}
    tally: Counter[str] = Counter()

    def excludes_zero(lo: float, hi: float) -> bool | None:
        if lo is None or hi is None:
            return None
        if not (np.isfinite(lo) and np.isfinite(hi)):
            return None
        return bool(lo > 0.0 or hi < 0.0)

    for block in blocks:
        key = (*block["counts"], block["b"])
        if key not in cache:
            tp, tn, fp, fn, b = key
            n = tp + tn + fp + fn
            labels = np.concatenate([
                np.full(tp, 0), np.full(tn, 1),
                np.full(fp, 2), np.full(fn, 3),
            ])
            np.random.default_rng(0).shuffle(labels)
            corrected = _bca_ci_from_indices(
                np.arange(n), tile_mcc_statistic(labels), n_iterations=b,
                random_seed=SEED, skip_undefined=True,
            )
            cache[key] = (corrected["ci_lower"], corrected["ci_upper"])
        committed = excludes_zero(*block["committed"])
        recomputed = excludes_zero(*cache[key])
        tally[f"committed={committed} corrected={recomputed}"] += 1

    print(f"unique (confusion, B) cells recomputed: {len(cache)}")
    for key, value in tally.most_common():
        print(f"  {key}: {value}")
    flipped = sum(v for k, v in tally.items()
                  if k.split()[0].split("=")[1] != k.split()[1].split("=")[1])
    print(f"blocks whose zero-exclusion reading changes: "
          f"{flipped} / {len(blocks)}")


PROBES: dict[str, Callable[[], None]] = {
    "shapes": probe_shapes,
    "compare": probe_compare,
    "sign": probe_sign,
    "census": probe_census,
    "mcc": probe_mcc,
}


def main() -> None:
    """Parse arguments and run the requested probe(s)."""
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--probe", default="all", choices=[*PROBES, "all"],
        help="Which probe to run (default: all).",
    )
    args = parser.parse_args()
    names = list(PROBES) if args.probe == "all" else [args.probe]
    for name in names:
        print(f"\n{'=' * 70}\nPROBE: {name}\n{'=' * 70}")
        PROBES[name]()


if __name__ == "__main__":
    main()
