#!/usr/bin/env python3
"""
W2.7 / D46: proposer-only consensus replicate floors from disjoint pass subsets.
================================================================================

For every replicate group of W2's calibration (replicate_sets.json) whose
members hold at least six passes within one execution, build consensus cells
from DISJOINT subsets of K passes (K in 3, 5, 10 where 2K <= n) with the
project's own voting algorithm (preregistration section 8.5 as merge_passes.py
implements it: within-pass greedy-star dedup at 20 m, cross-pass greedy-star
clustering at 20 m, vote = distinct passes, centroid = cluster mean), at every
vote threshold t = 1..K; score each cell per tile at the group's buffer with
the board's own scorer (the W2.3 path: assign_source_tiles -> _per_tile_one_set),
and run the paired tile-swap permutation test between every pair of disjoint
subsets at the same (K, t). The |dF1| of such a pair is a within-execution
consensus replicate difference for that corpus and aggregation.

Cross-execution consensus pairs (W7.6): for every group with two executions,
the first-K consensus of one execution against each disjoint K-subset of the
other, at every t, so the cross-execution gap is read at the consensus level
and not only at the single-pass level.

Gate: for one condition whose committed consensus sweep is on disk with its
pass list (consensus/voting_summary.json), the in-memory consensus over the
same passes reproduces the committed feature count at every threshold.

Zero API. Run on sapphire:
    .venv/bin/python w27_gs_consensus_floors.py --gate-only
    .venv/bin/python w27_gs_consensus_floors.py --workers 20 --out /tmp/w27

Author: Shawn Ross & Claude (Anthropic) | Created: 2026-10-06 | Apache 2.0
"""
from __future__ import annotations

import argparse
import csv
import itertools
import json
import os
import sys
import time
from multiprocessing import Pool
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd
from shapely.geometry import Point

REPO = Path(__file__).resolve().parents[2]
os.chdir(REPO)
sys.path.insert(0, str(REPO / "scripts"))

from era1_leaderboard_tiering import _per_tile_one_set, _read_detections_gdf  # noqa: E402
from lib_permutation import paired_permutation_test  # noqa: E402
from n1_baseline_leaderboard_tiering import TARGET_CRS, micro_f1  # noqa: E402
from pairwise_permutation_test import assign_source_tiles  # noqa: E402

SETS = REPO / "reports/retest-bootstrap-check-2026-10-05-scripts/replicate_sets.json"
RADIUS_M = 20.0  # merge_passes.DISTANCE_THRESHOLD_METRES
SCOPES = {
    "era1": ("inputs/vectors/references/mounds-reference.geojson",
             "inputs/vectors/bounds/full_evaluation_bounds.geojson", [20]),
    "px384": ("inputs/vectors/references/mounds-reference.geojson",
              "inputs/vectors/bounds/384/full_evaluation_bounds.geojson", [20]),
    "h10": ("inputs/vectors/references/mounds-reference.geojson",
            "inputs/vectors/bounds/384/h10_test_bounds.geojson", [20]),
    "maps55": ("inputs/vectors/references/best-available-gt-55maps-r2.geojson",
               "inputs/vectors/bounds/384/55maps_evaluation_bounds.geojson", [20, 50]),
}
GROUP_SCOPE = {g: "px384" for g in range(1, 9)}
GROUP_SCOPE.update({10: "h10", 11: "maps55", 12: "maps55"})
GROUP_SCOPE.update({g: "era1" for g in range(13, 25)})
KS = (3, 5, 10)
N_PERMS = 10_000
SEED = 42
_G: dict = {}


def greedy_star(xy: np.ndarray, owner: np.ndarray | None, radius: float):
    """Seed-order greedy star clustering (merge_passes / cluster_votes arithmetic).

    Returns (centroids [m, 2], votes [m]) where votes counts distinct owners
    (passes) per cluster, or members when owner is None.
    """
    n = len(xy)
    taken = np.zeros(n, dtype=bool)
    cents, votes = [], []
    for i in range(n):
        if taken[i]:
            continue
        d = np.hypot(xy[:, 0] - xy[i, 0], xy[:, 1] - xy[i, 1])
        members = np.flatnonzero((d <= radius) & ~taken)
        members = np.union1d(members, [i])
        taken[members] = True
        cents.append(xy[members].mean(axis=0))
        votes.append(len(set(owner[members].tolist())) if owner is not None else len(members))
    return np.asarray(cents).reshape(-1, 2), np.asarray(votes, dtype=int)


def load_pass_xy(files: list[str]) -> np.ndarray:
    """One pass's detections (all its files unioned) as UTM centroids, deduped at 20 m."""
    parts = [_read_detections_gdf(REPO / f) for f in files]
    gdf = parts[0] if len(parts) == 1 else gpd.GeoDataFrame(pd.concat(parts, ignore_index=True), crs=TARGET_CRS)
    xy = np.c_[gdf.geometry.centroid.x, gdf.geometry.centroid.y]
    cents, _ = greedy_star(xy, None, RADIUS_M)
    return cents


def consensus(pass_xys: list[np.ndarray]) -> tuple[np.ndarray, np.ndarray]:
    xy = np.vstack(pass_xys)
    owner = np.concatenate([np.full(len(p), i) for i, p in enumerate(pass_xys)])
    return greedy_star(xy, owner, RADIUS_M)


def scope_data(scope):
    if scope not in _G:
        gt, bd, _ = SCOPES[scope]
        ref = gpd.read_file(gt).to_crs(TARGET_CRS)
        bounds = gpd.read_file(bd).to_crs(TARGET_CRS)
        _G[scope] = (ref, bounds, list(bounds["tile_name"].unique()))
    return _G[scope]


def _score(task):
    """Score one consensus cell: centroids at vote >= t -> per-tile arrays per buffer."""
    scope, cents, votes, t, key = task["scope"], task["cents"], task["votes"], task["t"], task["key"]
    ref, bounds, order = scope_data(scope)
    keep = cents[votes >= t]
    det = gpd.GeoDataFrame(geometry=[Point(xy) for xy in keep], crs=TARGET_CRS)
    det = assign_source_tiles(det, bounds)
    out = {"key": key, "t": t, "n_det": int(len(keep))}
    for buf in SCOPES[scope][2]:
        tp, fp, fn = _per_tile_one_set(det, ref, bounds, order, buf)
        out[buf] = np.stack([tp, fp, fn], axis=1)
        out[f"f1_{buf}"] = micro_f1(int(tp.sum()), int(fp.sum()), int(fn.sum()))
    return out


def _test(job):
    a, b = job["a"], job["b"]
    r = paired_permutation_test({"tp": a[:, 0], "fp": a[:, 1], "fn": a[:, 2]},
                                {"tp": b[:, 0], "fp": b[:, 1], "fn": b[:, 2]},
                                n_permutations=N_PERMS, seed=SEED)
    m = r["metrics"]["f1"]
    return {**job["meta"], "f1_a": m["a"], "f1_b": m["b"], "dF1": m["observed_diff"],
            "abs_dF1": abs(m["observed_diff"]), "perm_p": m["p_value"], "null_std": m["null_std"],
            "n_discordant": r["n_discordant_tiles"]}


def gate(sets) -> dict:
    """Reproduce committed consensus sweeps' feature counts from the same passes.

    The committed ``consensus/voting_summary.json`` of the older builds records
    only ``total_passes`` and ``thresholds``; the gate therefore requires the
    member's pass count to equal ``total_passes`` (so the pool is the same) and
    compares the in-memory consensus count at every threshold with the
    committed ``consensus_t<t>.geojson`` feature count. Passes are taken in
    numeric run order, as ``merge_passes.resolve_pass_files`` orders them.
    """
    checks = {}
    for g, members in sets.items():
        for m in members:
            for parent in m.get("pool_parents", []):
                vs = REPO / parent / "consensus/voting_summary.json"
                if not vs.exists():
                    continue
                summary = json.loads(vs.read_text())
                if int(summary.get("total_passes", -1)) != len(m["passes"]):
                    continue
                xys = [load_pass_xy(p["files"]) for p in m["passes"]]
                committed = {}
                for t in range(1, len(xys) + 1):
                    f = REPO / parent / f"consensus/consensus_t{t}.geojson"
                    if f.exists():
                        committed[t] = len(json.loads(f.read_text())["features"])
                got = {}
                # The April builds iterated run_* directories in LEXICOGRAPHIC
                # order (run_1, run_10, run_11, ...); the current loader orders
                # them numerically. Greedy-star output depends on seed order,
                # so both orders are tried and either exact match passes.
                orders = {"numeric": list(range(len(xys))),
                          "lexicographic": sorted(range(len(xys)), key=lambda i: m["passes"][i]["run_dir"].rsplit("/", 1)[1])}
                for oname, order in orders.items():
                    cents, votes = consensus([xys[i] for i in order])
                    trial = {t: int((votes >= t).sum()) for t in committed}
                    if all(trial[t] == committed[t] for t in committed):
                        got = {t: {"committed": committed[t], "rebuilt": trial[t], "pass": True, "order": oname} for t in committed}
                        break
                    got = {t: {"committed": committed[t], "rebuilt": trial[t], "pass": trial[t] == committed[t], "order": oname} for t in committed}
                if got:
                    checks[f"{m['run_id']}::{m['arm']}"] = got
                    print(f"GATE {m['run_id']}::{m['arm']} [{next(iter(got.values()))['order']}]: " + " ".join(
                        f"t{t}:{v['committed']}/{v['rebuilt']}{'' if v['pass'] else '!'}"
                        for t, v in got.items()), flush=True)
                if len(checks) >= 4:
                    return checks
    return checks


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--gate-only", action="store_true")
    ap.add_argument("--workers", type=int, default=20)
    ap.add_argument("--out", type=Path, default=Path("/tmp/w27"))
    args = ap.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    sets = json.loads(SETS.read_text())
    checks = gate(sets)
    (args.out / "gs_gates.json").write_text(json.dumps(checks, indent=1))
    ok = bool(checks) and all(v["pass"] for c in checks.values() for v in c.values())
    print(f"gates: {'PASS' if ok else 'FAIL'} ({len(checks)} conditions)", flush=True)
    if not ok:
        return 1
    if args.gate_only:
        return 0

    # Load every pass once.
    members = []
    for g, ms in sets.items():
        for m in ms:
            key = f"{m['run_id']}::{m['arm']}"
            xys = [load_pass_xy(p["files"]) for p in m["passes"]]
            members.append({"group": int(g), "scope": GROUP_SCOPE[int(g)], "key": key, "xys": xys})
    print(f"{len(members)} members' passes loaded in {time.time() - t0:.0f}s", flush=True)

    # Within-execution disjoint subsets + first-K for cross-execution.
    tasks, index = [], []
    for m in members:
        n = len(m["xys"])
        subsets = {}
        for K in KS:
            if n >= 2 * K:
                subsets[K] = [tuple(range(i, i + K)) for i in range(0, n - K + 1, K)]
            elif n >= K:
                subsets[K] = [tuple(range(K))]  # first-K only (cross-execution use)
        for K, subs in subsets.items():
            for s in subs:
                cents, votes = consensus([m["xys"][i] for i in s])
                for t in range(1, K + 1):
                    key = (m["key"], K, s, t)
                    index.append({"group": m["group"], "scope": m["scope"], "member": m["key"], "K": K, "subset": s, "t": t})
                    tasks.append({"scope": m["scope"], "cents": cents, "votes": votes, "t": t, "key": key})
    print(f"{len(tasks)} consensus cells to score", flush=True)
    small = [t for t in tasks if t["scope"] != "maps55"]
    big = [t for t in tasks if t["scope"] == "maps55"]
    with Pool(args.workers) as pool:
        scored = pool.map(_score, small, chunksize=2)
    with Pool(min(args.workers, 8)) as pool:
        scored += pool.map(_score, big, chunksize=1)
    by = {r["key"]: r for r in scored}
    print(f"scored in {time.time() - t0:.0f}s", flush=True)
    rows = []
    for r in scored:
        member, K, s, t = r["key"]
        rows.append({"member": member, "K": K, "subset": json.dumps(list(s)), "t": t, "n_det": r["n_det"],
                     **{f"f1_{b}": r[f"f1_{b}"] for b in (20, 50) if f"f1_{b}" in r}})
    with open(args.out / "gs_consensus_cells.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=["member", "K", "subset", "t", "n_det", "f1_20", "f1_50"])
        w.writeheader()
        w.writerows(rows)

    # Pairs: within (disjoint subsets of one member) and across (first-K of one
    # member against every K-subset of another member of the same group).
    jobs = []
    by_group: dict[int, list] = {}
    for m in members:
        by_group.setdefault(m["group"], []).append(m)
    for g, ms in by_group.items():
        scope = ms[0]["scope"]
        bufs = SCOPES[scope][2]
        for m in ms:
            keys = [k for k in by if k[0] == m["key"]]
            for K in KS:
                subs = sorted({k[2] for k in keys if k[1] == K})
                for sa, sb in itertools.combinations(subs, 2):
                    if set(sa) & set(sb):
                        continue
                    for t in range(1, K + 1):
                        for buf in bufs:
                            ra, rb = by[(m["key"], K, sa, t)], by[(m["key"], K, sb, t)]
                            jobs.append({"a": ra[buf], "b": rb[buf], "meta": {
                                "group": g, "scope": scope, "buffer": buf, "kind": "within",
                                "member_a": m["key"], "member_b": m["key"], "K": K, "t": t,
                                "subset_a": json.dumps(list(sa)), "subset_b": json.dumps(list(sb)),
                                "n_det_a": ra["n_det"], "n_det_b": rb["n_det"]}})
        for ma, mb in itertools.combinations(ms, 2):
            for K in KS:
                sa_list = sorted({k[2] for k in by if k[0] == ma["key"] and k[1] == K})
                sb_list = sorted({k[2] for k in by if k[0] == mb["key"] and k[1] == K})
                for sa in sa_list:
                    for sb in sb_list:
                        for t in range(1, K + 1):
                            for buf in bufs:
                                ra, rb = by[(ma["key"], K, sa, t)], by[(mb["key"], K, sb, t)]
                                jobs.append({"a": ra[buf], "b": rb[buf], "meta": {
                                    "group": g, "scope": scope, "buffer": buf, "kind": "across",
                                    "member_a": ma["key"], "member_b": mb["key"], "K": K, "t": t,
                                    "subset_a": json.dumps(list(sa)), "subset_b": json.dumps(list(sb)),
                                    "n_det_a": ra["n_det"], "n_det_b": rb["n_det"]}})
    print(f"{len(jobs)} pairs to test", flush=True)
    with Pool(args.workers) as pool:
        res = pool.map(_test, jobs, chunksize=8)
    with open(args.out / "gs_consensus_pairs.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(res[0].keys()))
        w.writeheader()
        w.writerows(res)
    print(f"done in {time.time() - t0:.0f}s -> {args.out}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
