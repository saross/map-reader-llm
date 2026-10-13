#!/usr/bin/env python3
"""
Floors v2: all-subsets pass subsampling and vote-propensity simulation on the 55-map board.
==========================================================================================

For each 55-map family of W2.7 § 6, build the rung from EVERY K-subset of the
family's N passes with the W2.7 script's own ``cluster_subset`` + ``inherit``
(the board's rung mechanism; the family's verifier probabilities held fixed),
and score each subset at 50 m on reference r2 at every (prob_t, k <= K) the
family's board cells use. 10-pass families (A, B, FOURTH): K = 1..5;
five-pass families (ARM1, ARM2, the two image pools' arms): K = 1..4.

Then (``--sims``) the vote-propensity comparison: from the full N-pass union
(also the board's top rung, gated on its committed counts), simulate K-pass
rungs by (a) independent Binomial(K, v_i / N) votes per candidate, (b) a pass
bootstrap (K passes drawn with replacement, votes read off the union's
pass-membership matrix, so between-candidate correlation within a pass is
kept), and (c) all K-subsets without replacement on the union clusters (no
re-clustering), each scored like the real rungs.

Gates (stop on failure): fast clustering == committed ``cluster_votes``; fast
scorer == the live ``compute_per_tile_tp_fp_fn`` per tile on six cells; the six
committed rung counts of W2.7 § 2 and the N10 / N5 top-rung counts; and (after
the run, gate 4) every cell of ``floors2_scorer_gate.py``'s live-library gate --
every § 6 cell of the board families and a seeded random sample of the others --
reproduced exactly (n_det, tp, fp, fn, F1), with that gate passed under the same
library and scorer blob hashes as this run (PI ruling D60 (4), 2026-10-12).
Until 2026-10-12 gate 4 compared with the committed § 6 ``subset_cells.json``,
which the pre-D50 scorer had written, so it could not see the D50 rule.

Zero API. Run on sapphire (``REPO`` = the checkout these scripts sit in):
    REPO=<clone> PYTHONPYCACHEPREFIX=/tmp/floors2/pycache .venv/bin/python floors2_55map.py \
        --workers 8 --scorer-gate <gate dir> --out /tmp/floors2/out55 [--sims 200]

Author: Shawn Ross & Claude (Anthropic) | Created: 2026-10-07 | Gate 4 against the
live library: 2026-10-12 | Apache 2.0
"""

from __future__ import annotations

import argparse
import csv
import itertools
import json
import os
import sys
import time
import zlib
from multiprocessing import Pool
from pathlib import Path

import geopandas as gpd
import numpy as np

REPO = Path(os.environ.get("REPO", str(Path.home() / "Code/map-reader-llm")))
sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(REPO / "reports/w27-replicate-floors-2026-10-06-scripts"))
import w27_55map_subset_replicates as w27  # noqa: E402  (inserts REPO, REPO/scripts)

import floors2_lib as L  # noqa: E402
from scripts.build_55map_leaderboard import BOUNDS, reference_gt  # noqa: E402
from scripts.h13_k_sensitivity import cluster_votes as cluster_votes_committed  # noqa: E402
from scripts.h13_k_sensitivity import (  # noqa: E402
    cluster_votes_with_origins as cluster_votes_origins_committed,
)
from scripts.lib_advanced_metrics import compute_per_tile_tp_fp_fn  # noqa: E402

PROBS = {
    "A": (0.15, 0.20),
    "B": (0.15, 0.20),
    "FOURTH": (0.96, 0.98),
    "ARM1": (0.10, 0.15, 0.20),
    "ARM2": (0.80, 0.95, 0.98),
    "G37IMG-ARM1": (0.10,),
    "G37IMG-ARM2": (0.88, 0.90),
    "G3IMG-ARM1": (0.15,),
    "G3IMG-ARM2": (0.88, 0.95),
}
#: Top-rung cells (all N passes) the full union must reproduce (final_board_50m.json).
TOP_GATES = {
    ("A", 0.15, 8): 4475,
    ("A", 0.15, 7): 4639,
    ("B", 0.15, 10): 4505,
    ("B", 0.20, 9): 4639,
    ("FOURTH", 0.98, 10): 4246,
    ("FOURTH", 0.96, 9): 4495,
    ("ARM1", 0.10, 5): 5229,
    ("ARM1", 0.15, 5): 4616,
    ("ARM2", 0.80, 5): 5003,
    ("ARM2", 0.95, 5): 4924,
}
_G: dict = {}


def blob_hash(path: Path) -> str:
    """The file's git blob hash (``git hash-object``)."""
    import hashlib

    data = path.read_bytes()
    return hashlib.sha1(b"blob %d\0" % len(data) + data).hexdigest()


def frame_arrays(cell: gpd.GeoDataFrame) -> dict:
    """An inherited rung frame attributed once by the library, with its threshold arrays.

    ``prep`` is the scorer's :class:`floors2_lib.PreparedFrame`: every row's sheet
    under the library's detection scope (D50), so each (prob_t, k) cell is a row
    mask of it.
    """
    return {
        "prep": _G["scorer"].prepare(cell),
        "prob": cell["mound_probability"].to_numpy(dtype=float),
        "votes": cell["vote_count"].to_numpy(dtype=int),
    }


def score_ops(fam: str, K: int, fa: dict, votes: np.ndarray | None = None, ks=None) -> list[dict]:
    """Score one frame at every (prob_t, k) of ``fam`` with k in ``ks`` (default 1..K)."""
    v = fa["votes"] if votes is None else votes
    out = []
    for p in PROBS[fam]:
        for k in ks or range(1, K + 1):
            m = (fa["prob"] >= p) & (v >= k)
            tp, fp, fn = _G["scorer"].totals(fa["prep"], m)
            out.append(
                {
                    "family": fam,
                    "K": K,
                    "prob_t": p,
                    "k": k,
                    "n_det": int(m.sum()),
                    "tp": tp,
                    "fp": fp,
                    "fn": fn,
                    "f1": L.f1_of(tp, fp, fn),
                }
            )
    return out


def _subset_job(job):
    """Cluster one pass subset once; inherit and score it for every family on these passes."""
    pset, s = job
    spec = _G["psets"][pset]
    gdf = w27.cluster_subset(spec["passes"], s, _G["index"])
    recs = []
    for fam in spec["families"]:
        fa = frame_arrays(w27.inherit(gdf, _G["fam"][fam]["union"]))
        for r in score_ops(fam, len(s), fa):
            r["subset"] = "-".join(map(str, s))
            recs.append(r)
    return recs


def _sim_job(job):
    """One simulated K-pass rung for the vote-propensity comparison."""
    fam, model, K, draw = job
    U = _G["unions"][fam]
    N = U["N"]
    if model != "union-sub":
        rng = np.random.default_rng(
            [20261007, zlib.crc32(fam.encode()), K, draw, 1 if model == "binom" else 2]
        )
    if model == "binom":
        votes = rng.binomial(K, U["votes_full"] / N)
    elif model == "boot":
        votes = U["M"][:, rng.integers(0, N, K)].sum(axis=1)
    else:  # "union-sub": draw is a subset tuple
        votes = U["M"][:, list(draw)].sum(axis=1)
    ks = [k for k in range(max(1, K - 2), K + 1)]
    recs = score_ops(fam, K, U["fa"], votes=votes, ks=ks)
    for r in recs:
        r.update(
            {"model": model, "draw": draw if model != "union-sub" else "-".join(map(str, draw))}
        )
    return recs


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=20)
    ap.add_argument("--out", type=Path, default=Path("/tmp/floors2/out55"))
    ap.add_argument("--sims", type=int, default=0)
    ap.add_argument("--max-k10", type=int, default=5)
    ap.add_argument(
        "--scorer-gate",
        type=Path,
        required=True,
        help="directory holding floors2_scorer_gate.py's scorer_gate.json and cells CSV",
    )
    args = ap.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    gates: dict = {}

    fam = w27.build_families(gate_only=False)
    index = next(iter(fam.values()))["index"]
    print(f"families loaded {time.time() - t0:.0f}s", flush=True)

    # Gate 1: fast clustering == committed cluster_votes on two real subsets.
    for f, s in (("A", (0, 1, 2)), ("ARM1", (1, 3))):
        sub = [fam[f]["passes"][i] for i in s]
        c0, v0 = cluster_votes_committed(sub, 1)
        c1, v1 = L.cluster_votes_fast(sub, 1)
        ok = c0.shape == c1.shape and bool(np.array_equal(c0, c1)) and bool(np.array_equal(v0, v1))
        gates[f"cluster_votes_fast == committed ({f} {s})"] = {"pass": ok, "n": int(len(v0))}
        print(f"GATE cluster {f} {s}: {ok} ({len(v0)} clusters)", flush=True)
        # The same for the contributing tiles cluster_subset now carries (PI ruling
        # D62 (1)): the fast restatement's centroids, votes and tiles equal the
        # committed cluster_votes_with_origins, whose centroids and votes equal
        # cluster_votes's.
        c2, v2, o2 = cluster_votes_origins_committed(sub, 1)
        c3, v3, o3 = L.cluster_votes_fast_origins(sub, 1)
        ok_o = (
            bool(np.array_equal(c0, c2)) and bool(np.array_equal(v0, v2))
            and bool(np.array_equal(c2, c3)) and bool(np.array_equal(v2, v3)) and o2 == o3
        )
        gates[f"cluster_votes_fast_origins == committed ({f} {s})"] = {
            "pass": ok_o, "n": int(len(v2)),
            "n_multi_sheet_origin": sum(len({t.split("_x")[0] for t in o}) > 1 for o in o2),
        }
        print(f"GATE cluster origins {f} {s}: {ok_o}", flush=True)
        if not (ok and ok_o):
            (args.out / "gates.json").write_text(json.dumps(gates, indent=1))
            return 1
    # cluster_subset now uses the gated restatement, contributing tiles included.
    w27.cluster_votes_origins = L.cluster_votes_fast_origins

    ref = reference_gt("r2")
    bounds = gpd.read_file(BOUNDS)
    bounds = (bounds.set_crs("EPSG:4326") if bounds.crs is None else bounds).to_crs("EPSG:32635")
    _G.update(scorer=L.FastScorer(ref, bounds, w27.BUFFER_M), index=index, fam=fam)

    # Gate 2: fast scorer == the live library's per-tile table (exact), on six cells,
    # through the production path (the whole frame attributed once, the cell a mask).
    for f, s, p, k in (
        ("B", (0, 1, 2, 3, 4), 0.15, 5),
        ("A", (2,), 0.20, 1),
        ("ARM2", (0, 1, 2), 0.95, 3),
        ("G3IMG-ARM1", (0, 4), 0.15, 1),
        ("FOURTH", (5, 6, 7), 0.96, 2),
        ("ARM1", (3,), 0.10, 1),
    ):
        cell = w27.inherit(w27.cluster_subset(fam[f]["passes"], s, index), fam[f]["union"])
        m = ((cell["mound_probability"] >= p) & (cell["vote_count"] >= k)).to_numpy()
        sub = cell[m]
        tm = compute_per_tile_tp_fp_fn(sub, ref, bounds, buffer_metres=w27.BUFFER_M)
        slow = {r.tile_name: (int(r.tp), int(r.fp), int(r.fn)) for r in tm.itertuples()}
        fast_arr = _G["scorer"].per_tile(frame_arrays(cell)["prep"], m)
        fast = {t: tuple(int(x) for x in fast_arr[i]) for t, i in _G["scorer"].tile_pos.items()}
        ok = slow == fast
        gates[f"FastScorer == compute_per_tile_tp_fp_fn ({f} {s} {p} k{k})"] = {
            "pass": ok,
            "n_det": int(len(sub)),
            "totals": [int(x) for x in fast_arr.sum(0)],
        }
        print(
            f"GATE scorer {f} {s} ({p},k{k}): {ok} n={len(sub)} totals={fast_arr.sum(0).tolist()}",
            flush=True,
        )
        if not ok:
            (args.out / "gates.json").write_text(json.dumps(gates, indent=1))
            return 1

    # Gate 3: committed rung counts (W2.7 § 2) with the restated clustering.
    for (f, s, p, k), exp in w27.GATES.items():
        cell = w27.inherit(w27.cluster_subset(fam[f]["passes"], s, index), fam[f]["union"])
        n = int(((cell["mound_probability"] >= p) & (cell["vote_count"] >= k)).sum())
        gates[f"{f} {s} ({p}, k{k})"] = {"expected": exp, "got": n, "pass": n == exp}
        print(f"GATE {f} {s} ({p},k{k}): expected {exp} got {n}", flush=True)
    if not all(g["pass"] for g in gates.values()):
        (args.out / "gates.json").write_text(json.dumps(gates, indent=1))
        return 1
    print(f"gates 1-3 passed {time.time() - t0:.0f}s", flush=True)

    # Pass sets shared between families (B and FOURTH share passes; so do the arms).
    psets: dict[str, dict] = {}
    for f, spec in fam.items():
        key = str(id(spec["passes"]))
        psets.setdefault(key, {"passes": spec["passes"], "families": [], "N": spec["n"]})[
            "families"
        ].append(f)
    _G["psets"] = psets
    jobs = []
    for key, ps in psets.items():
        kmax = args.max_k10 if ps["N"] == 10 else ps["N"] - 1
        for K in range(1, kmax + 1):
            jobs += [(key, s) for s in itertools.combinations(range(ps["N"]), K)]
    jobs.sort(key=lambda j: -len(j[1]))  # largest first for load balance
    print(f"{len(jobs)} subset jobs over {len(psets)} pass sets", flush=True)
    with Pool(args.workers) as pool:
        res = pool.map(_subset_job, jobs, chunksize=1)
    recs = [r for rr in res for r in rr]
    with open(args.out / "subset_cells_all.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(recs[0].keys()))
        w.writeheader()
        w.writerows(recs)
    print(f"{len(recs)} subset cells scored {time.time() - t0:.0f}s", flush=True)

    # Gate 4: every cell the live-library gate scored is reproduced exactly, and that
    # gate passed under this run's library and scorer (D60 (4)).
    gate = json.loads((args.scorer_gate / "scorer_gate.json").read_text())
    here = Path(__file__).resolve().parent
    blobs_now = {
        "scripts/lib_advanced_metrics.py": blob_hash(REPO / "scripts/lib_advanced_metrics.py"),
        "floors2_lib.py": blob_hash(here / "floors2_lib.py"),
    }
    blobs_ok = all(gate["blob_hashes"].get(k) == v for k, v in blobs_now.items())
    have = {(r["family"], r["subset"], r["prob_t"], r["k"]): r for r in recs}
    n_chk, n_listed, bad = 0, 0, []
    with open(args.scorer_gate / "scorer_gate_cells.csv") as fh:
        for o in csv.DictReader(fh):
            if o["family"] == "UPL":
                continue
            n_listed += 1
            key = (o["family"], o["subset"], float(o["prob_t"]), int(o["k"]))
            r = have.get(key)
            if r is None:
                bad.append({"key": key, "missing": True})
                continue
            n_chk += 1
            lib = [int(o["n_det"]), int(o["lib_tp"]), int(o["lib_fp"]), int(o["lib_fn"])]
            got = [r["n_det"], r["tp"], r["fp"], r["fn"]]
            if got != lib or r["f1"] != float(o["lib_f1"]):
                bad.append({"key": key, "library": lib + [o["lib_f1"]], "run": got + [r["f1"]]})
    gates["live-library gate cells reproduced (floors2_scorer_gate.py)"] = {
        "gate_pass": bool(gate["pass"]),
        "blob_hashes_match": blobs_ok,
        "blob_hashes": blobs_now,
        "listed": n_listed,
        "checked": n_chk,
        "mismatches": bad[:20],
        "pass": bool(gate["pass"]) and blobs_ok and not bad and n_chk == n_listed > 0,
    }
    print(
        f"GATE live-library cells: gate pass {gate['pass']}, blobs match {blobs_ok}, "
        f"checked {n_chk} of {n_listed}, mismatches {len(bad)}",
        flush=True,
    )
    (args.out / "gates.json").write_text(json.dumps(gates, indent=1, default=str))
    if not all(g["pass"] for g in gates.values()):
        return 1

    if args.sims:
        # Full-N unions with pass membership (the board's top rung), gated on counts.
        unions = {}
        for key, ps in psets.items():
            allp = tuple(range(ps["N"]))
            gdf = w27.cluster_subset(ps["passes"], allp, index)
            masks = np.asarray(L.LAST_MEMBERS["masks"], dtype=np.int64)
            M = ((masks[:, None] >> np.arange(ps["N"])[None, :]) & 1).astype(np.int8)
            for f in ps["families"]:
                cell = w27.inherit(gdf, fam[f]["union"])
                pos = gdf.index.get_indexer(cell.index)
                fa = frame_arrays(cell)
                unions[f] = {"fa": fa, "M": M[pos], "votes_full": M[pos].sum(1), "N": ps["N"]}
                assert np.array_equal(unions[f]["votes_full"], fa["votes"])
        for (f, p, k), exp in TOP_GATES.items():
            fa = unions[f]["fa"]
            n = int(((fa["prob"] >= p) & (fa["votes"] >= k)).sum())
            gates[f"top rung {f} ({p}, k{k})"] = {"expected": exp, "got": n, "pass": n == exp}
            print(f"GATE top {f} ({p},k{k}): expected {exp} got {n}", flush=True)
        (args.out / "gates.json").write_text(json.dumps(gates, indent=1, default=str))
        if not all(g["pass"] for g in gates.values()):
            print(
                "WARNING: a top-rung count differs (recorded in gates.json); sims continue",
                flush=True,
            )
        _G["unions"] = unions
        sjobs = []
        for f, U in unions.items():
            for K in (1, 3, 5):
                for model in ("binom", "boot"):
                    sjobs += [(f, model, K, d) for d in range(args.sims)]
                if K < U["N"]:
                    sjobs += [
                        (f, "union-sub", K, s) for s in itertools.combinations(range(U["N"]), K)
                    ]
        print(f"{len(sjobs)} simulation jobs", flush=True)
        with Pool(args.workers) as pool:
            sres = pool.map(_sim_job, sjobs, chunksize=4)
        srecs = [r for rr in sres for r in rr]
        with open(args.out / "sim_cells.csv", "w", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=list(srecs[0].keys()))
            w.writeheader()
            w.writerows(srecs)
        print(f"{len(srecs)} simulated cells {time.time() - t0:.0f}s", flush=True)
    print(f"done {time.time() - t0:.0f}s", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
