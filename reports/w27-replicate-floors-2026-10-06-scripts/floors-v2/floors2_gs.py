#!/usr/bin/env python3
"""
Floors v2: validate the corrected subsampling floor on the gold-standard 30-pass pools.
======================================================================================

For each W2 replicate member holding 30 passes of one execution (nine pools:
two 384-px GS pools of ``pv-diag-384`` and seven Era-1 ``retest-phase3a*``
pools), treat each disjoint 10-pass slice (passes 1-10, 11-20, 21-30) as if it
were the only 10 passes in existence, build proposer-only consensus cells from
EVERY K-subset of the slice (K = 1..5; C(10, K) subsets) with the W2.7 GS
script's own voting algorithm, and score each at every vote threshold t <= K at
20 m with the board's scorer (gated restatement). The corrected subsampling
estimate from one slice is then compared (``floors2_analyse.py``) with the
empirical disjoint-subset spread from all 30 passes (W2.7's
``gs_consensus_cells.csv``: six disjoint 5-subsets, ten 3-subsets, three
10-subsets per pool).

Gates (stop on failure): KD-shortlisted greedy star == the GS script's
``consensus``; fast scorer == ``_per_tile_one_set``; every slice subset that
coincides with a W2.7 disjoint subset reproduces its committed F1 and count.

Zero API. Run on sapphire:
    PYTHONPYCACHEPREFIX=/tmp/floors2/pycache .venv/bin/python floors2_gs.py \
        --workers 20 --out /tmp/floors2/outgs

Author: Shawn Ross & Claude (Anthropic) | Created: 2026-10-07 | Apache 2.0
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
from scipy.spatial import cKDTree
from shapely.geometry import Point

REPO = Path(os.environ.get("REPO", str(Path.home() / "Code/map-reader-llm")))
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / "reports/w27-replicate-floors-2026-10-06-scripts"))
import w27_gs_consensus_floors as gs  # noqa: E402  (chdirs to REPO, inserts REPO/scripts)

import floors2_lib as L  # noqa: E402

W27_CELLS = REPO / "reports/w27-replicate-floors-2026-10-06-scripts/gs_consensus_cells.csv"
_G: dict = {}


def consensus_fast(pass_xys: list[np.ndarray]) -> tuple[np.ndarray, np.ndarray]:
    """``gs.consensus`` (greedy star at 20 m, votes = distinct passes) with a KD shortlist."""
    xy = np.vstack(pass_xys)
    owner = np.concatenate([np.full(len(p), i) for i, p in enumerate(pass_xys)])
    n = len(xy)
    neigh = cKDTree(xy).query_ball_point(xy, r=gs.RADIUS_M + 1e-6)
    taken = np.zeros(n, dtype=bool)
    cents, votes = [], []
    for i in range(n):
        if taken[i]:
            continue
        cand = np.asarray(neigh[i], dtype=np.intp)
        cand = cand[~taken[cand]]
        d = np.hypot(xy[cand, 0] - xy[i, 0], xy[cand, 1] - xy[i, 1])
        members = np.union1d(cand[d <= gs.RADIUS_M], [i])
        taken[members] = True
        cents.append(xy[members].mean(axis=0))
        votes.append(len(set(owner[members].tolist())))
    return np.asarray(cents).reshape(-1, 2), np.asarray(votes, dtype=int)


def _load(job):
    key, files = job
    return key, gs.load_pass_xy(files)


def score_cell(
    scope: str, cents: np.ndarray, votes: np.ndarray, t: int
) -> tuple[int, int, int, int]:
    """Score centroids at vote >= t exactly as ``gs._score`` (source tiles by sjoin)."""
    ref, bounds, _ = gs.scope_data(scope)
    keep = cents[votes >= t]
    det = gpd.GeoDataFrame(geometry=[Point(xy) for xy in keep], crs=gs.TARGET_CRS)
    det = gs.assign_source_tiles(det, bounds)
    xy = np.c_[det.geometry.x.to_numpy(), det.geometry.y.to_numpy()]
    tp, fp, fn = _G["scorers"][scope].totals(xy, det["source_tile"].to_numpy(dtype=object))
    return int(len(keep)), tp, fp, fn


def _job(job):
    member, scope, sl, s = job
    xys = _G["xys"][member]
    cents, votes = consensus_fast([xys[i] for i in s])
    out = []
    for t in range(1, len(s) + 1):
        n, tp, fp, fn = score_cell(scope, cents, votes, t)
        out.append(
            {
                "member": member,
                "scope": scope,
                "slice": sl,
                "K": len(s),
                "subset": json.dumps(list(s)),
                "t": t,
                "n_det": n,
                "tp": tp,
                "fp": fp,
                "fn": fn,
                "f1_20": L.f1_of(tp, fp, fn),
            }
        )
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=20)
    ap.add_argument("--out", type=Path, default=Path("/tmp/floors2/outgs"))
    ap.add_argument("--kmax", type=int, default=5)
    args = ap.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    sets = json.loads(gs.SETS.read_text())
    members = {}
    for g, ms in sets.items():
        for m in ms:
            if len(m["passes"]) >= 30:
                members[f"{m['run_id']}::{m['arm']}"] = (gs.GROUP_SCOPE[int(g)], m["passes"])
    print(f"{len(members)} 30-pass pools: {list(members)}", flush=True)
    jobs = [((k, i), p["files"]) for k, (_, ps) in members.items() for i, p in enumerate(ps)]
    with Pool(args.workers) as pool:
        loaded = dict(pool.map(_load, jobs, chunksize=1))
    _G["xys"] = {k: [loaded[(k, i)] for i in range(len(ps))] for k, (_, ps) in members.items()}
    print(f"passes loaded {time.time() - t0:.0f}s", flush=True)
    _G["scorers"] = {}
    for scope in sorted({sc for sc, _ in members.values()}):
        ref, bounds, _ = gs.scope_data(scope)
        _G["scorers"][scope] = L.FastScorer(ref, bounds, gs.SCOPES[scope][2][0])

    gates = {}
    # Gate 1: shortlisted greedy star == committed consensus.
    for k in list(members)[:2]:
        sub = [_G["xys"][k][i] for i in (0, 1, 2, 3, 4)]
        c0, v0 = gs.consensus(sub)
        c1, v1 = consensus_fast(sub)
        ok = c0.shape == c1.shape and bool(np.array_equal(c0, c1)) and bool(np.array_equal(v0, v1))
        gates[f"consensus_fast == gs.consensus ({k})"] = {"pass": ok, "n": int(len(v0))}
        print(f"GATE consensus {k}: {ok}", flush=True)
    # Gate 2: fast scorer == _per_tile_one_set (exact per tile) on one cell per scope.
    for k, (scope, _) in (
        list(members.items())[:2] + [x for x in members.items() if x[1][0] == "era1"][:1]
    ):
        cents, votes = gs.consensus([_G["xys"][k][i] for i in (5, 6, 7)])
        ref, bounds, order = gs.scope_data(scope)
        keep = cents[votes >= 2]
        det = gs.assign_source_tiles(
            gpd.GeoDataFrame(geometry=[Point(xy) for xy in keep], crs=gs.TARGET_CRS), bounds
        )
        tp, fp, fn = gs._per_tile_one_set(det, ref, bounds, order, gs.SCOPES[scope][2][0])
        sc = _G["scorers"][scope]
        arr = sc.per_tile(
            np.c_[det.geometry.x, det.geometry.y], det["source_tile"].to_numpy(dtype=object)
        )
        fast = {t: tuple(arr[i]) for t, i in sc.tile_pos.items()}
        slow = {t: (tp[i], fp[i], fn[i]) for i, t in enumerate(order)}
        ok = all(tuple(float(x) for x in fast[t]) == slow[t] for t in order) and set(fast) == set(
            order
        )
        gates[f"FastScorer == _per_tile_one_set ({k}, t2)"] = {"pass": ok, "n_det": int(len(keep))}
        print(f"GATE scorer {k} ({scope}): {ok}", flush=True)
    if not all(g["pass"] for g in gates.values()):
        (args.out / "gates.json").write_text(json.dumps(gates, indent=1))
        return 1

    jobs = []
    for k, (scope, ps) in members.items():
        for sl in range(3):
            idx = range(10 * sl, 10 * sl + 10)
            for K in range(1, args.kmax + 1):
                jobs += [(k, scope, sl, s) for s in itertools.combinations(idx, K)]
    jobs.sort(key=lambda j: -len(j[3]))
    print(f"{len(jobs)} consensus jobs", flush=True)
    with Pool(args.workers) as pool:
        res = pool.map(_job, jobs, chunksize=2)
    recs = [r for rr in res for r in rr]
    with open(args.out / "gs_slice_cells.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(recs[0].keys()))
        w.writeheader()
        w.writerows(recs)
    print(f"{len(recs)} cells {time.time() - t0:.0f}s", flush=True)

    # Gate 3: coincident subsets reproduce W2.7's committed cells exactly.
    have = {(r["member"], r["K"], r["subset"], r["t"]): r for r in recs}
    n_chk, bad = 0, []
    with open(W27_CELLS) as fh:
        for o in csv.DictReader(fh):
            key = (o["member"], int(o["K"]), o["subset"], int(o["t"]))
            r = have.get(key)
            if r is None:
                continue
            n_chk += 1
            if r["n_det"] != int(o["n_det"]) or repr(r["f1_20"]) != o["f1_20"]:
                bad.append(
                    {"key": key, "old": [o["n_det"], o["f1_20"]], "new": [r["n_det"], r["f1_20"]]}
                )
    gates["W2.7 gs_consensus_cells.csv reproduced"] = {
        "checked": n_chk,
        "mismatches": bad[:20],
        "pass": not bad and n_chk > 0,
    }
    print(f"GATE W2.7 GS cells: checked {n_chk}, mismatches {len(bad)}", flush=True)
    (args.out / "gates.json").write_text(json.dumps(gates, indent=1, default=str))
    print(f"done {time.time() - t0:.0f}s", flush=True)
    return 0 if not bad else 1


if __name__ == "__main__":
    sys.exit(main())
