#!/usr/bin/env python3
"""
Run A scoring: the 55-map T03 and text-MIN 3-of-5 and 4-of-5 cells under one verifier date.

Run A (PI ruling D49) re-verified, on 2026-10-07, each family's 4-of-5 set (first
verified April 2026) and its vote-3 shell (first verified 2026-06-06) with the same
verifier configuration, on the same crops and manifests, so candidate ids align
exactly. This scores, on the board's own path (reference r2, 50 m,
compute_per_tile_tp_fp_fn, micro-F1), each family's cells under four probability
variants: the committed mixed-date probabilities (must reproduce the board), all
October, October on the 4-of-5 set only, and October on the shell only; runs the
paired tile-swap permutation test on the contrasts that matter; and counts decision
flips between dates on identical candidates.

Run on sapphire from the repository root:
    .venv/bin/python <this file> --out <dir>

Author: Shawn Ross & Claude (Anthropic) | Created: 2026-10-07 | Apache 2.0
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from multiprocessing import Pool
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd

sys.path.insert(0, ".")
from scripts.build_55map_leaderboard import BOUNDS, reference_gt  # noqa: E402
from scripts.final_board_sweeps import BUFFER_M, DEPLOY, load_manifest_probs  # noqa: E402
from scripts.lib_advanced_metrics import compute_per_tile_tp_fp_fn  # noqa: E402
from scripts.lib_permutation import paired_permutation_test  # noqa: E402
from scripts.n1_baseline_leaderboard_tiering import micro_f1  # noqa: E402
from scripts.pairwise_permutation_test import assign_source_tiles  # noqa: E402

OCT = Path("outputs/verifier-date-2026-10-07")
FAMILIES = {
    "T03": "55maps-text-high-t0.3-generalisation",
    "TM": "55maps-text-min-generalisation",
}
#: Committed board values the mixed variant must reproduce (final-board-50m.md).
BOARD = {
    ("T03", 0.15, 4): 0.8294,
    ("T03", 0.20, 3): 0.8399,
    ("TM", 0.15, 4): 0.7826,
    ("TM", 0.20, 3): 0.8103,
}
POINTS = [(0.15, 3), (0.15, 4), (0.20, 3), (0.20, 4)]
_G: dict = {}


def wilson(k: int, n: int, z: float = 1.959964) -> tuple[float, float]:
    """Wilson score interval for a proportion k / n."""
    if n == 0:
        return (math.nan, math.nan)
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (c - h, c + h)


def load_family(run: str) -> pd.DataFrame:
    """Committed and October probabilities for one family, aligned by candidate.

    Args:
        run: The run directory name under outputs/.

    Returns:
        One frame: subset ('k4' or 'shell'), vote_count, source_tile, geometry,
        p_committed (April for k4, June 6 for the shell) and p_oct.
    """
    k4c, k4v = Path("outputs") / run / "crops", Path("outputs") / run / "verified"
    shc, shv = DEPLOY / run / "crops", DEPLOY / run / "verified"
    parts = []
    for subset, cdir, vdir, odir in (
        ("k4", k4c, k4v, OCT / run / "verified-k4set"),
        ("shell", shc, shv, OCT / run / "verified-increment"),
    ):
        a = load_manifest_probs(cdir, vdir)
        b = load_manifest_probs(cdir, odir)
        assert len(a) == len(b)
        assert (a.geometry.x.values == b.geometry.x.values).all()
        assert (a.vote_count.values == b.vote_count.values).all()
        a = a.rename(columns={"mound_probability": "p_committed"})
        a["p_oct"] = b["mound_probability"].to_numpy()
        a["subset"] = subset
        parts.append(a)
    return gpd.GeoDataFrame(pd.concat(parts, ignore_index=True), crs="EPSG:32635")


def _init(ref, bounds):
    _G["ref"], _G["bounds"] = ref, bounds


def _score(task):
    """Per-tile counts for one (family, variant, point)."""
    fam, variant, pt, k, g = task
    sub = g[(g["p"] >= pt) & (g["vote_count"] >= k)]
    tm = compute_per_tile_tp_fp_fn(sub, _G["ref"], _G["bounds"], buffer_metres=BUFFER_M)
    tm = tm.sort_values("tile_name").reset_index(drop=True)
    return (fam, variant, pt, k), tm, len(sub)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--workers", type=int, default=16)
    args = ap.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    bounds = gpd.read_file(BOUNDS)
    bounds = (bounds.set_crs("EPSG:4326") if bounds.crs is None else bounds).to_crs("EPSG:32635")
    ref = reference_gt("r2")
    res: dict = {"families": {}}
    tasks = []
    frames = {}
    for fam, run in FAMILIES.items():
        f = load_family(run)
        f = gpd.GeoDataFrame(assign_source_tiles(f, bounds), crs="EPSG:32635")
        frames[fam] = f
        k4 = f.subset == "k4"
        variants = {
            "mixed": f.p_committed.to_numpy(),
            "all_oct": f.p_oct.to_numpy(),
            "k4_oct": np.where(k4, f.p_oct, f.p_committed),
            "shell_oct": np.where(~k4, f.p_oct, f.p_committed),
        }
        for v, p in variants.items():
            g = f[["vote_count", "source_tile", "geometry"]].copy()
            g["p"] = p
            for pt, k in POINTS:
                tasks.append((fam, v, pt, k, g))
        # decision agreement between dates on identical candidates
        agree = {}
        for subset, label in (
            ("k4", "April->October (4-of-5 set)"),
            ("shell", "June 6->October (vote-3 shell)"),
        ):
            s = f[f.subset == subset]
            d = s.p_oct - s.p_committed
            row = {
                "n": int(len(s)),
                "identical": float((d == 0).mean()),
                "mean_abs_dp": float(d.abs().mean()),
                "signed_mean_dp": float(d.mean()),
            }
            for t in (0.15, 0.20):
                a, b = s.p_committed >= t, s.p_oct >= t
                fl = int((a != b).sum())
                row[f"flips_{t}"] = fl
                row[f"flip_rate_{t}"] = fl / len(s)
                row[f"flip_wilson_{t}"] = wilson(fl, len(s))
                row[f"up_{t}"] = int((~a & b).sum())
                row[f"down_{t}"] = int((a & ~b).sum())
            agree[label] = row
        res["families"][fam] = {"agreement": agree}
    with Pool(args.workers, initializer=_init, initargs=(ref, bounds)) as pool:
        out = pool.map(_score, tasks, chunksize=1)
    tiles, scores = {}, {}
    for key, tm, n in out:
        tiles[key] = tm
        tp, fp, fn = int(tm.tp.sum()), int(tm.fp.sum()), int(tm.fn.sum())
        scores[key] = {"n": n, "tp": tp, "fp": fp, "fn": fn, "f1": micro_f1(tp, fp, fn)}
    # gate: the mixed variant reproduces the board
    gates = {
        f"{fam} ({pt}, k{k})": {
            "board": v,
            "got": round(scores[(fam, "mixed", pt, k)]["f1"], 4),
            "pass": abs(scores[(fam, "mixed", pt, k)]["f1"] - v) <= 0.0005,
        }
        for (fam, pt, k), v in BOARD.items()
    }
    res["gates"] = gates
    if not all(g["pass"] for g in gates.values()):
        (args.out / "runA_results.json").write_text(json.dumps(res, indent=1, default=str))
        print("GATE FAILURE", gates)
        return 1

    def arm(key):
        t = tiles[key]
        return {c: t[c].to_numpy(dtype=float) for c in ("tp", "fp", "fn")}

    pairs = []
    for fam in FAMILIES:
        for v in ("mixed", "all_oct"):
            pairs.append((fam, f"{v}: k3-k4 @0.15", (fam, v, 0.15, 3), (fam, v, 0.15, 4)))
            pairs.append((fam, f"{v}: (0.20,k3)-(0.15,k4)", (fam, v, 0.20, 3), (fam, v, 0.15, 4)))
        pairs.append(
            (
                fam,
                "k4 cell October-April @(0.15,k4)",
                (fam, "all_oct", 0.15, 4),
                (fam, "mixed", 0.15, 4),
            )
        )
        pairs.append(
            (
                fam,
                "k4 cell October-April @(0.20,k4)",
                (fam, "all_oct", 0.20, 4),
                (fam, "mixed", 0.20, 4),
            )
        )
        pairs.append(
            (
                fam,
                "k3 cell October-mixed @(0.20,k3)",
                (fam, "all_oct", 0.20, 3),
                (fam, "mixed", 0.20, 3),
            )
        )
        pairs.append(
            (
                fam,
                "k3 cell, shell only October-June @(0.15,k3)",
                (fam, "shell_oct", 0.15, 3),
                (fam, "mixed", 0.15, 3),
            )
        )
    for fam, lab, ka, kb in pairs:
        r = paired_permutation_test(arm(ka), arm(kb), n_permutations=10_000, seed=42)
        f1 = r["metrics"]["f1"]
        res["families"][fam].setdefault("tests", {})[lab] = {
            "a": f1["a"],
            "b": f1["b"],
            "diff": f1["observed_diff"],
            "p": f1["p_value"],
            "null_std": f1["null_std"],
            "discordant": r["n_discordant_tiles"],
        }
    for (fam, v, pt, k), s in scores.items():
        res["families"][fam].setdefault("scores", {})[f"{v}|{pt}|k{k}"] = s
    (args.out / "runA_results.json").write_text(json.dumps(res, indent=1, default=str))
    print(json.dumps(gates, indent=1))
    for fam in FAMILIES:
        print("==", fam)
        for lab, t in res["families"][fam]["tests"].items():
            print(f"  {lab:46s} {t['a']:.4f} vs {t['b']:.4f}  d={t['diff']:+.4f}  p={t['p']:.4f}")
        for lab, a in res["families"][fam]["agreement"].items():
            print(
                f"  {lab}: n={a['n']} identical={a['identical']:.3f} flips@0.15={a['flips_0.15']} "
                f"({a['flip_rate_0.15']:.2%}; up {a['up_0.15']}, down {a['down_0.15']}) "
                f"signed dp={a['signed_mean_dp']:+.4f}"
            )
    return 0


if __name__ == "__main__":
    sys.exit(main())
