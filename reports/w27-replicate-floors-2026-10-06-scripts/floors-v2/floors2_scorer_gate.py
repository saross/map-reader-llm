#!/usr/bin/env python3
"""
Floors v2: the FastScorer's exactness gate against the LIVE library scorer (D60 (4)).
====================================================================================

PI ruling D60 (4) (``planning/pi-decisions-2026-09-20.md``): ``FastScorer`` is
rebuilt on the shared library's attribution and must reproduce the CURRENT
library scorer's cells exactly. This script is that gate. Its reference is
``lib_advanced_metrics.compute_per_tile_tp_fp_fn`` itself, called live on each
cell, not any committed table.

Cells checked (all at 50 m on reference r2, the board's scorer settings):

* **every § 6 cell**: the 466 (family, subset, prob_t, k) cells of
  ``w27_55map_subset_replicates.py`` (152 board-family subset frames and
  UPL's two five-pass frames);
* **a seeded simple random sample of the § 6b cells** that are not § 6 cells:
  ``--sample`` cells (default 1,000) drawn without replacement, with
  ``numpy.random.default_rng(--seed)`` (default 20261012), from the 16,260 cells
  ``floors2_55map.py`` scores, ordered by (family, K, subset, prob_t, k).

For each cell the library's per-tile table (every frame tile's tp, fp, fn) is
compared with each scorer under test:

* ``new``: ``floors2_lib.FastScorer`` (the gated scorer);
* ``legacy``: the pre-2026-10-12 ``FastScorer``, loaded from
  ``archive/superseded-w27-floors-2026-10-12/floors-v2/floors2_lib.py``. It is
  the red sentinel: it must FAIL on exactly the § 6 cells the current scorer
  moved (``--expect-legacy-moved``; four family B cells), which proves the gate
  can see the difference it guards.

With ``--w27-cells`` (the § 6 ``subset_cells.json`` written by
``w27_55map_subset_replicates.py`` under the same library), each § 6 cell's
library count and F1 must also equal that file's, which ties the gate's frames
to § 6's.

Outputs in ``--out``: ``scorer_gate.json`` (verdicts, mismatches, the sample's
definition, and the git blob hashes of the library and both scorers) and
``scorer_gate_cells.csv`` (one row per cell: the library's totals and F1, and
each scorer's totals and exact flag). ``floors2_55map.py`` reads both: its
gate 4 requires this gate's pass under the same blob hashes and compares every
cell listed here with its own run.

Exit 0 only if ``new`` equals the library on every cell, per tile, and the red
sentinel behaves as expected.

Zero API. Run on sapphire (about 25 minutes on 8 workers):
    REPO=<clone> PYTHONPATH=<clone> .venv/bin/python floors2_scorer_gate.py \
        --workers 8 --w27-cells <w27 out>/subset_cells.json --out <dir>

Author: Shawn Ross & Claude (Anthropic) | Created: 2026-10-12 | Apache 2.0
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import importlib.util
import itertools
import json
import os
import sys
import time
from multiprocessing import Pool
from pathlib import Path

import geopandas as gpd
import numpy as np

REPO = Path(os.environ.get("REPO", str(Path.home() / "Code/map-reader-llm")))
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(REPO / "reports/w27-replicate-floors-2026-10-06-scripts"))
import w27_55map_subset_replicates as w27  # noqa: E402  (inserts REPO, REPO/scripts)

import floors2_55map as f2  # noqa: E402
import floors2_lib as L  # noqa: E402
from scripts.build_55map_leaderboard import BOUNDS, reference_gt  # noqa: E402
from scripts.h13_k_sensitivity import cluster_votes as cluster_votes_committed  # noqa: E402
from scripts.h13_k_sensitivity import (  # noqa: E402
    cluster_votes_with_origins as cluster_votes_origins_committed,
)
from scripts.lib_advanced_metrics import compute_per_tile_tp_fp_fn  # noqa: E402
from scripts.n1_baseline_leaderboard_tiering import micro_f1  # noqa: E402

LEGACY = REPO / "archive/superseded-w27-floors-2026-10-12/floors-v2/floors2_lib.py"
LIBRARY = REPO / "scripts/lib_advanced_metrics.py"
#: The § 6 cells the current scorer moved (main session's check of 2026-10-12;
#: reports/s163-agent-records/d57-4-rescore-s4-q4.md flag 2).
EXPECT_LEGACY_MOVED = [
    ["B", [8], 0.15, 1],
    ["B", [8], 0.2, 1],
    ["B", [8, 9], 0.15, 1],
    ["B", [8, 9], 0.2, 1],
]
_G: dict = {}


def blob_hash(path: Path) -> str:
    """The file's git blob hash (``git hash-object``), to bind a gate to code versions."""
    data = path.read_bytes()
    return hashlib.sha1(b"blob %d\0" % len(data) + data).hexdigest()


def load_legacy():
    """The archived pre-2026-10-12 ``floors2_lib`` (old ``FastScorer``) as a module."""
    spec = importlib.util.spec_from_file_location("floors2_lib_legacy", LEGACY)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def w27_cells(fam: dict) -> list[tuple]:
    """Every § 6 cell, keyed (family, subset, prob_t, k), as w27's ``main`` builds them."""
    cells = []
    for f, spec in fam.items():
        for subs in w27.subsets_for(spec["n"]).values():
            for s in subs:
                for p in w27.PROBS[f]:
                    for k in w27.ks_for(len(s)):
                        cells.append((f, s, p, k))
    for s in ((0, 1, 2, 3, 4), (5, 6, 7, 8, 9)):
        for p in w27.PROBS["UPL"]:
            for k in w27.ks_for(len(s)):
                cells.append(("UPL", s, p, k))
    return cells


def f2_cells(fam: dict) -> list[tuple]:
    """Every § 6b cell, keyed as above, in floors2_55map.py's enumeration."""
    psets: dict[str, dict] = {}
    for f, spec in fam.items():
        key = str(id(spec["passes"]))
        psets.setdefault(key, {"N": spec["n"], "families": []})["families"].append(f)
    cells = []
    for ps in psets.values():
        kmax = 5 if ps["N"] == 10 else ps["N"] - 1
        for K in range(1, kmax + 1):
            for s in itertools.combinations(range(ps["N"]), K):
                for f in ps["families"]:
                    for p in f2.PROBS[f]:
                        for k in range(1, K + 1):
                            cells.append((f, s, p, k))
    return sorted(cells, key=lambda c: (c[0], len(c[1]), c[1], c[2], c[3]))


def build_frame(f: str, s: tuple) -> gpd.GeoDataFrame:
    """The cell's frame: w27's subset rung (clustered, inherited), or a UPL half."""
    if f == "UPL":
        return _G["upl"][s]
    spec = _G["fam"][f]
    return w27.inherit(w27.cluster_subset(spec["passes"], s, spec["index"]), spec["union"])


def _job(job):
    """Score one frame's listed cells with the library and with every scorer under test."""
    (f, s), cells = job
    frame = build_frame(f, s)
    prob = frame["mound_probability"].to_numpy(dtype=float)
    votes = frame["vote_count"].to_numpy(dtype=int)
    new = _G["new"]
    prep = new.prepare(frame)
    xy = np.c_[frame.geometry.x.to_numpy(), frame.geometry.y.to_numpy()]
    tiles = frame["source_tile"].to_numpy(dtype=object)
    out = []
    for p, k, origin in cells:
        m = (prob >= p) & (votes >= k)
        tm = compute_per_tile_tp_fp_fn(
            frame[m], _G["ref"], _G["bounds"], buffer_metres=w27.BUFFER_M
        )
        lib = {r.tile_name: (int(r.tp), int(r.fp), int(r.fn)) for r in tm.itertuples()}
        lt = tuple(int(x) for x in np.sum(list(lib.values()), axis=0)) if lib else (0, 0, 0)
        rec = {
            "family": f, "subset": "-".join(map(str, s)), "K": len(s), "prob_t": p, "k": k,
            "origin": origin, "n_det": int(m.sum()),
            "lib_tp": lt[0], "lib_fp": lt[1], "lib_fn": lt[2], "lib_f1": micro_f1(*lt),
        }
        for name, fn in (
            ("new", lambda m=m: new.per_tile(prep, m)),
            ("legacy", lambda m=m: _G["legacy"].per_tile(xy[m], tiles[m])),
        ):
            sc = new if name == "new" else _G["legacy"]
            try:
                arr = fn()
                got = {t: tuple(int(x) for x in arr[i]) for t, i in sc.tile_pos.items()}
                tot = tuple(int(x) for x in arr.sum(axis=0))
                rec[f"{name}_exact"] = got == lib
                rec[f"{name}_tp"], rec[f"{name}_fp"], rec[f"{name}_fn"] = tot
                rec[f"{name}_error"] = ""
            except (KeyError, ValueError) as exc:
                rec[f"{name}_exact"] = False
                rec[f"{name}_tp"] = rec[f"{name}_fp"] = rec[f"{name}_fn"] = None
                rec[f"{name}_error"] = f"{type(exc).__name__}: {exc}"[:200]
        out.append(rec)
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--sample", type=int, default=1000)
    ap.add_argument("--seed", type=int, default=20261012)
    ap.add_argument("--w27-cells", type=Path, default=None)
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    t0 = time.time()

    fam = w27.build_families(gate_only=False)
    # The restated clustering, after the same equality check floors2_55map.py runs.
    for f, s in (("A", (0, 1, 2)), ("ARM1", (1, 3))):
        sub = [fam[f]["passes"][i] for i in s]
        c0, v0 = cluster_votes_committed(sub, 1)
        c1, v1 = L.cluster_votes_fast(sub, 1)
        if not (np.array_equal(c0, c1) and np.array_equal(v0, v1)):
            print(f"GATE FAILURE: cluster_votes_fast != committed on {f} {s}", flush=True)
            return 1
        # The contributing tiles cluster_subset carries (PI ruling D62 (1)).
        c2, v2, o2 = cluster_votes_origins_committed(sub, 1)
        c3, v3, o3 = L.cluster_votes_fast_origins(sub, 1)
        if not (np.array_equal(c0, c2) and np.array_equal(v0, v2) and np.array_equal(c2, c3)
                and np.array_equal(v2, v3) and o2 == o3):
            print(f"GATE FAILURE: cluster_votes_fast_origins != committed on {f} {s}",
                  flush=True)
            return 1
    w27.cluster_votes_origins = L.cluster_votes_fast_origins
    upl = w27.load_upl_frame()
    _G["upl"] = {}
    for s in ((0, 1, 2, 3, 4), (5, 6, 7, 8, 9)):
        runs = {f"run_{i + 1}" for i in s}
        g = upl.copy()
        g["vote_count"] = [sum(r in runs for r in c) for c in g["contrib"]]
        _G["upl"][s] = g[g["vote_count"] >= 3]

    ref = reference_gt("r2")
    bounds = gpd.read_file(BOUNDS)
    bounds = (bounds.set_crs("EPSG:4326") if bounds.crs is None else bounds).to_crs("EPSG:32635")
    legacy_mod = load_legacy()
    _G.update(
        fam=fam, ref=ref, bounds=bounds,
        new=L.FastScorer(ref, bounds, w27.BUFFER_M),
        legacy=legacy_mod.FastScorer(ref, bounds, w27.BUFFER_M),
    )

    sec6 = w27_cells(fam)
    all6b = f2_cells(fam)
    sec6_set = set(sec6)
    pool6b = [c for c in all6b if c not in sec6_set]
    rng = np.random.default_rng(args.seed)
    pick = sorted(rng.choice(len(pool6b), size=min(args.sample, len(pool6b)), replace=False))
    sample = [pool6b[i] for i in pick]
    print(
        f"§ 6 cells {len(sec6)}; § 6b cells {len(all6b)} ({len(all6b) - len(pool6b)} coincide "
        f"with § 6); sampled {len(sample)} of {len(pool6b)} (seed {args.seed})", flush=True,
    )
    by_frame: dict[tuple, list] = {}
    for c in sec6:
        by_frame.setdefault((c[0], c[1]), []).append((c[2], c[3], "sec6"))
    for c in sample:
        by_frame.setdefault((c[0], c[1]), []).append((c[2], c[3], "sec6b-sample"))
    jobs = sorted(by_frame.items(), key=lambda j: -len(j[1]))
    with Pool(args.workers) as pool:
        res = pool.map(_job, jobs, chunksize=1)
    recs = sorted(
        (r for rr in res for r in rr),
        key=lambda r: (r["origin"], r["family"], r["K"], r["subset"], r["prob_t"], r["k"]),
    )
    with open(args.out / "scorer_gate_cells.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(recs[0].keys()))
        w.writeheader()
        w.writerows(recs)

    def key(r):
        return [r["family"], [int(x) for x in r["subset"].split("-")], r["prob_t"], r["k"]]

    summary: dict = {}
    for origin in ("sec6", "sec6b-sample"):
        rows = [r for r in recs if r["origin"] == origin]
        summary[origin] = {
            "cells": len(rows),
            **{
                f"{name}_mismatches": [
                    {"cell": key(r), "lib": [r["lib_tp"], r["lib_fp"], r["lib_fn"]],
                     name: [r[f"{name}_tp"], r[f"{name}_fp"], r[f"{name}_fn"]],
                     "error": r[f"{name}_error"]}
                    for r in rows if not r[f"{name}_exact"]
                ]
                for name in ("new", "legacy")
            },
        }
    new_ok = all(not summary[o]["new_mismatches"] for o in summary)
    legacy_moved = sorted(m["cell"] for m in summary["sec6"]["legacy_mismatches"])
    sentinel_ok = legacy_moved == sorted(EXPECT_LEGACY_MOVED)
    w27_check: dict = {"checked": 0, "mismatches": []}
    if args.w27_cells:
        have = {
            (r["family"], r["subset"], r["prob_t"], r["k"]): r
            for r in recs if r["origin"] == "sec6"
        }
        for o in json.loads(args.w27_cells.read_text()):
            r = have.get((o["family"], "-".join(map(str, o["subset"])), o["prob_t"], o["k"]))
            if r is None:
                w27_check["mismatches"].append({"missing": [o["family"], o["subset"]]})
                continue
            w27_check["checked"] += 1
            if r["n_det"] != o["n_det"] or r["lib_f1"] != o["f1"]:
                w27_check["mismatches"].append({
                    "cell": key(r),
                    "w27": [o["n_det"], o["f1"]],
                    "gate": [r["n_det"], r["lib_f1"]],
                })
    w27_ok = not args.w27_cells or (
        not w27_check["mismatches"] and w27_check["checked"] == len(sec6)
    )
    gate = {
        "pass": bool(new_ok and sentinel_ok and w27_ok),
        "new_exact_on_every_cell": new_ok,
        "red_sentinel_legacy_fails_on_expected_cells": sentinel_ok,
        "legacy_sec6_mismatch_cells": legacy_moved,
        "expected_legacy_sec6_mismatch_cells": EXPECT_LEGACY_MOVED,
        "w27_subset_cells_crosscheck": {"file": str(args.w27_cells), **w27_check},
        "sample": {
            "population": "§ 6b cells (floors2_55map.py enumeration) not among the § 6 cells",
            "population_size": len(pool6b), "n": len(sample), "seed": args.seed,
            "rng": "numpy.random.default_rng(seed).choice(population_size, n, replace=False)",
            "order": "sorted by (family, K, subset, prob_t, k)",
        },
        "comparison": "per tile: every frame tile's (tp, fp, fn) against the live "
                      "compute_per_tile_tp_fp_fn at 50 m on r2",
        "blob_hashes": {
            "scripts/lib_advanced_metrics.py": blob_hash(LIBRARY),
            "floors2_lib.py": blob_hash(HERE / "floors2_lib.py"),
            "legacy floors2_lib.py": blob_hash(LEGACY),
        },
        "summary": summary,
        "wall_seconds": round(time.time() - t0),
    }
    (args.out / "scorer_gate.json").write_text(json.dumps(gate, indent=1, default=str) + "\n")
    print(
        f"GATE new exact on all {len(recs)} cells: {new_ok}; red sentinel (legacy fails on "
        f"{legacy_moved}): {sentinel_ok}; w27 cross-check: {w27_ok}; "
        f"legacy mismatches in sample: {len(summary['sec6b-sample']['legacy_mismatches'])}; "
        f"{time.time() - t0:.0f}s",
        flush=True,
    )
    return 0 if gate["pass"] else 1


if __name__ == "__main__":
    sys.exit(main())
