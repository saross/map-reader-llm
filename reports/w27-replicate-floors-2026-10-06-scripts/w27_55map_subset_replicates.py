#!/usr/bin/env python3
"""
W2.7 / D46: consensus replicate floors on the 55-map board from disjoint pass subsets.
=======================================================================================

For every 55-map family whose proposer pool holds more passes than a rung
uses, build the rung from DISJOINT subsets of its passes with the board's own
rung mechanism (``stride55_ladder.cluster_first_n``: within-pass dedup at
20 m, greedy star clustering at 20 m, votes = distinct passes, standard-grid
tile assignment; verifier probabilities INHERITED from the family's K-union
verification within 10 m), score each subset cell per tile at 50 m on
reference r2 with the board's scorer, and run the board's paired tile-swap
permutation test between every pair of disjoint subsets at the same operating
point. The |dF1| between two subsets of ONE execution at ONE operating point
is a within-execution consensus replicate difference with the verifier held
fixed: the proposer-side floor D46 asks for.

The uplift family (UPL) is the exception that measures something else: its
ten passes are two executions 54 days apart (run_1-5 2026-04-18,
run_6-10 2026-06-11), so its first-five / last-five split is a CROSS-execution
replicate on the 55-map corpus itself (W7.6 item 2).

Gates (nothing is written unless they pass): the first-N subset at a family's
committed rung point must reproduce the committed cell's detection count
EXACTLY (B-N5-carried 4,736; A-N5-carried 4,597; ARM1-N3-carried 5,482;
ARM2-N3-carried 5,187; FOURTH-N5-carried 4,431; FOURTH-N3-carried 4,623),
because that is the proof that the subset builder IS the board's rung builder.

Zero API. Run on sapphire:
    .venv/bin/python w27_55map_subset_replicates.py --gate-only
    .venv/bin/python w27_55map_subset_replicates.py --workers 20 --out /tmp/w27

Author: Shawn Ross & Claude (Anthropic) | Created: 2026-10-06 | Apache 2.0
"""
from __future__ import annotations

import argparse
import itertools
import json
import sys
import time
from multiprocessing import Pool
from pathlib import Path

import geopandas as gpd
import numpy as np
from scipy.spatial import cKDTree
from shapely.geometry import Point

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / "scripts"))

from scripts.build_55map_leaderboard import BOUNDS, reference_gt  # noqa: E402
from scripts.compute_corrected_f1_multi_buffer import DEFAULT_CRS  # noqa: E402
from scripts.gemini37_arm_ladder import CELL_DIR as G37_CELL_DIR  # noqa: E402
from scripts.gemini37_sweep_oracle import CELLS as G37_CELLS  # noqa: E402
from scripts.gemini37_sweep_oracle import load_candidates as load_g37_candidates  # noqa: E402
from scripts.grid_prepare_scoring import load_pass  # noqa: E402
from scripts.h13_k_sensitivity import cluster_votes  # noqa: E402
from scripts.lib_advanced_metrics import compute_per_tile_tp_fp_fn  # noqa: E402
from scripts.lib_permutation import paired_permutation_test  # noqa: E402
from scripts.merge_passes import deduplicate_within_pass  # noqa: E402
from scripts.n1_baseline_leaderboard_tiering import micro_f1  # noqa: E402
from scripts.merge_passes import centroid_from_geometry  # noqa: E402
from scripts.pin_pass_provenance import PINNED_CELLS, tag_for_cell_dir, verify_pin  # noqa: E402
from scripts.stride55_ladder import INHERIT_TOL_M  # noqa: E402
from scripts.stride55_prepare_and_union import DEDUP_METRES, OUTROOT, resolve_pass_paths  # noqa: E402
from scripts.stride55_score import assign_standard_tile, build_map_constrained_index  # noqa: E402
from scripts.stride55_sweep_oracle import RUNS as STRIDE_RUNS  # noqa: E402
from scripts.stride55_sweep_oracle import load_candidates as load_stride_candidates  # noqa: E402

BUFFER_M = 50
N_PERMS = 10_000
SEED = 42

#: Committed cells the subset builder must reproduce exactly (board tables,
#: results/55map-final-board-r2-2026-09-06/final-board-50m.md, read 2026-10-06).
GATES = {
    ("B", (0, 1, 2, 3, 4), 0.15, 5): 4736,       # B-N5-carried
    ("A", (0, 1, 2, 3, 4), 0.15, 4): 4597,       # A-N5-carried
    ("ARM1", (0, 1, 2), 0.10, 3): 5482,          # ARM1-N3-carried (addendum)
    ("ARM2", (0, 1, 2), 0.80, 3): 5187,          # ARM2-N3-carried (addendum)
    ("FOURTH", (0, 1, 2, 3, 4), 0.98, 5): 4431,  # FOURTH-N5-carried (addendum)
    ("FOURTH", (0, 1, 2), 0.98, 3): 4623,        # FOURTH-N3-carried (addendum)
}

#: Probability thresholds swept per family: the carried and oracle thresholds
#: the board publishes for that family's cells (cells_manifest.json).
PROBS = {
    "A": (0.15, 0.20), "B": (0.15, 0.20), "FOURTH": (0.96, 0.98),
    "ARM1": (0.10, 0.15), "ARM2": (0.80, 0.95),
    "G37IMG-ARM1": (0.10,), "G37IMG-ARM2": (0.88, 0.90),
    "G3IMG-ARM1": (0.15,), "G3IMG-ARM2": (0.88, 0.95),
    "UPL": (0.15,),
}

IMG = {
    "G37IMG": REPO / "outputs/gemini37-image-55map-2026-09-13/verifier/g384_ov192_55map_g37img",
    "G3IMG": REPO / "outputs/gemini3-image-55map-2026-09-16/verifier/g384_ov192_55map_g3img",
}
UPL = REPO / "outputs/55maps-text-min-n10-uplift"

_G: dict = {}
CACHE = Path("/tmp/w27/passes")


def dedup_fast(features: list[dict], distance_thresh: float = DEDUP_METRES) -> list[dict]:
    """``merge_passes.deduplicate_within_pass``, vectorised; same arithmetic.

    Seed-order greedy star: each unvisited detection seeds a cluster and
    absorbs every later unvisited detection within ``distance_thresh``
    (``sqrt(dx**2 + dy**2) <= thresh``, as ``euclidean_distance`` computes
    it); centroid = mean of members; source tiles = sorted set; cluster_size
    = member count. Equality with the committed function is a gate below.
    """
    if not features:
        return []
    cents = np.asarray([centroid_from_geometry(f.get("geometry", {})) for f in features], dtype=float)
    tiles = [(f.get("properties") or {}).get("source_tile") or (f.get("properties") or {}).get("tile_id", "unknown")
             for f in features]
    labels = [(f.get("properties") or {}).get("subtype", "mound") for f in features]
    n = len(cents)
    taken = np.zeros(n, dtype=bool)
    out = []
    for i in range(n):
        if taken[i]:
            continue
        d = np.sqrt((cents[:, 0] - cents[i, 0]) ** 2 + (cents[:, 1] - cents[i, 1]) ** 2)
        members = np.flatnonzero((d <= distance_thresh) & ~taken)
        members = np.union1d(members, [i])
        taken[members] = True
        from collections import Counter
        # The built-in ``sum`` over Python floats in member order, exactly as
        # the committed function's ``sum(xs) / len(xs)`` (Python >= 3.12 sums
        # floats with Neumaier compensation, so neither numpy's mean nor a
        # plain loop reproduces its last bit; the equality gate caught both).
        cx = sum(float(cents[m, 0]) for m in members) / len(members)
        cy = sum(float(cents[m, 1]) for m in members) / len(members)
        out.append({"centroid": (cx, cy),
                    "label": Counter(labels[m] for m in members).most_common(1)[0][0],
                    "source_tiles": sorted({tiles[m] for m in members}),
                    "cluster_size": int(len(members))})
    return out


def _cached(name: str, builder):
    import pickle
    CACHE.mkdir(parents=True, exist_ok=True)
    f = CACHE / f"{name}.pkl"
    if f.exists():
        return pickle.loads(f.read_bytes())
    v = builder()
    f.write_bytes(pickle.dumps(v))
    return v


def load_stride_passes(cell: str) -> list[list[dict]]:
    """``stride55_ladder.load_deduped_passes`` with the fast dedup (pin-gated)."""
    def build():
        cell_dir = OUTROOT / cell
        verify_pin(tag_for_cell_dir(cell_dir), PINNED_CELLS[tag_for_cell_dir(cell_dir)])
        passes = []
        for i in range(1, 11):
            raw, _ = load_pass(resolve_pass_paths(cell_dir, f"run_{i}"))
            passes.append(dedup_fast(raw))
        return passes
    return _cached(f"stride_{cell}", build)


def load_g37_passes() -> list[list[dict]]:
    """``gemini37_arm_ladder.load_deduped_passes`` with the fast dedup (pin-gated)."""
    def build():
        verify_pin(tag_for_cell_dir(G37_CELL_DIR), PINNED_CELLS[tag_for_cell_dir(G37_CELL_DIR)])
        passes = []
        for i in range(1, 6):
            raw, _ = load_pass(resolve_pass_paths(G37_CELL_DIR, f"run_{i}"))
            passes.append(dedup_fast(raw))
        return passes
    return _cached("g37_arms", build)


def dedup_equality_gate() -> dict:
    """The fast dedup equals the committed one on a real pass (exact)."""
    raw, _ = load_pass(resolve_pass_paths(G37_CELL_DIR, "run_1"))
    slow = deduplicate_within_pass(raw, distance_thresh=DEDUP_METRES)
    fast = dedup_fast(raw)
    same = len(slow) == len(fast) and all(
        a["centroid"] == b["centroid"] and a["source_tiles"] == b["source_tiles"]
        and a["cluster_size"] == b["cluster_size"] for a, b in zip(slow, fast))
    return {"pass": bool(same), "n_raw": len(raw), "n_slow": len(slow), "n_fast": len(fast)}


def cluster_subset(passes: list[list[dict]], idxs: tuple[int, ...], index: dict) -> gpd.GeoDataFrame:
    """``stride55_ladder.cluster_first_n`` over an arbitrary pass subset.

    Identical arithmetic: ``cluster_votes`` at min_corroboration 1 over the
    subset in index order, standard-grid tile from the nearest pooled
    detection's origin tile.
    """
    subset = [passes[i] for i in idxs]
    centroids, votes = cluster_votes(subset, 1)
    tiles_flat = [d["source_tiles"][0] for p in subset for d in p]
    pooled = np.asarray([d["centroid"] for p in subset for d in p], dtype=float)
    gdf = gpd.GeoDataFrame({"vote_count": np.asarray(votes)},
                           geometry=[Point(xy) for xy in centroids], crs=DEFAULT_CRS)
    _, j = cKDTree(pooled).query(np.c_[gdf.geometry.x, gdf.geometry.y], k=1)
    gdf["source_tile"] = [assign_standard_tile(index, tiles_flat[i], x, y)
                          for i, x, y in zip(j, gdf.geometry.x, gdf.geometry.y)]
    return gdf


def inherit(gdf: gpd.GeoDataFrame, union: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """Inherit verifier probabilities from the family's K-union within 10 m."""
    tree = cKDTree(np.c_[union.geometry.x, union.geometry.y])
    probs = union["mound_probability"].to_numpy()
    d, idx = tree.query(np.c_[gdf.geometry.x, gdf.geometry.y], k=1)
    gdf = gdf.copy()
    gdf["mound_probability"] = probs[idx]
    gdf["inherit_d"] = d
    return gdf[d <= INHERIT_TOL_M].copy()


def load_img_passes(camp: str) -> list[list[dict]]:
    """The image campaign's five deduped passes from its union provenance."""
    prov = json.loads((IMG[camp] / "union_k5_pass_provenance.json").read_text())
    by_pass: dict[str, list[Path]] = {}
    for rec in prov["pass_provenance"]:
        by_pass.setdefault(rec["pass_id"], []).append(REPO / rec["path"])
    passes = []
    for pid in prov["pass_ids"]:
        raw, _ = load_pass(by_pass[pid])
        passes.append(dedup_fast(raw))
    return passes


def load_upl_frame() -> gpd.GeoDataFrame:
    """UPL's verified band (>= 3 of 10) with each candidate's contributing passes."""
    from scripts.final_board_sweeps import load_manifest_probs, prob_key  # noqa: F401
    cands = json.loads((UPL / "crops-3of10/candidate_manifest.json").read_text())["candidates"]
    probs = json.loads((UPL / "verified-3of10/probabilities.json").read_text())["results"]
    gdf = gpd.GeoDataFrame({
        "contrib": [tuple(c["properties"]["contributing_passes"]) for c in cands],
        "vote_count": [c["properties"]["vote_count"] for c in cands],
        "mound_probability": [float(probs[prob_key(c["candidate_id"])]["mound_probability"]) for c in cands],
        "source_tile": [c["source_tile"] for c in cands],
    }, geometry=gpd.points_from_xy([c["centroid_x"] for c in cands], [c["centroid_y"] for c in cands]),
        crs="EPSG:32635")
    return gdf


def build_families(gate_only: bool) -> dict:
    """Family -> {passes, union (with probabilities), probs, n_passes, kind}."""
    index = build_map_constrained_index()
    bounds = gpd.read_file(BOUNDS).to_crs("EPSG:32635")
    fam: dict[str, dict] = {}
    b_passes = load_stride_passes("g384_ov192_55map")
    a_passes = load_stride_passes("g384_ov128_55map")
    fam["A"] = {"passes": a_passes, "union": load_stride_candidates("g384_ov128_55map", STRIDE_RUNS["g384_ov128_55map"], bounds)}
    fam["B"] = {"passes": b_passes, "union": load_stride_candidates("g384_ov192_55map", STRIDE_RUNS["g384_ov192_55map"], bounds)}
    fam["FOURTH"] = {"passes": b_passes, "union": load_g37_candidates("fourth", G37_CELLS["fourth"])}
    arm = load_g37_passes()
    fam["ARM1"] = {"passes": arm, "union": load_g37_candidates("arm1", G37_CELLS["arm1"])}
    fam["ARM2"] = {"passes": arm, "union": load_g37_candidates("arm2", G37_CELLS["arm2"])}
    if not gate_only:
        from scripts.final_board_sweeps import load_manifest_probs
        for camp, root in IMG.items():
            passes = _cached(f"img_{camp}", lambda camp=camp: load_img_passes(camp))
            for a in ("arm1", "arm2"):
                raw = load_manifest_probs(root / "crops_k5", root / f"verify_k5_{a}")
                fam[f"{camp}-{a.upper()}"] = {"passes": passes, "union": raw}
    for f in fam.values():
        f["n"] = len(f["passes"])
        f["index"] = index
    return fam


def subsets_for(n: int) -> dict[int, list[tuple[int, ...]]]:
    """Disjoint-capable subsets per rung size N (consecutive partitions; all
    2-subsets for N = 2 so disjoint pairs can be enumerated)."""
    out: dict[int, list[tuple[int, ...]]] = {1: [(i,) for i in range(n)]}
    out[2] = [c for c in itertools.combinations(range(n), 2)] if n <= 5 else [(i, i + 1) for i in range(0, n - 1, 2)]
    if n >= 6:
        out[3] = [tuple(range(i, i + 3)) for i in range(0, n - 2, 3)]
    if n >= 10:
        out[5] = [tuple(range(0, 5)), tuple(range(5, 10))]
    return out


def ks_for(n_rung: int) -> list[int]:
    return list(range(1, n_rung + 1)) if n_rung <= 3 else [3, 4, 5]


def _build_frame(job):
    f, s = job
    spec = _G["fam"][f]
    return inherit(cluster_subset(spec["passes"], s, spec["index"]), spec["union"])


def _init(ref, bounds, tile_order):
    _G["ref"], _G["bounds"], _G["order"] = ref, bounds, tile_order


def _score(task):
    fam, subset, prob_t, k, det = task
    sub = det[(det["mound_probability"] >= prob_t) & (det["vote_count"] >= k)]
    tm = compute_per_tile_tp_fp_fn(sub, _G["ref"], _G["bounds"], buffer_metres=BUFFER_M)
    idx = {t: i for i, t in enumerate(_G["order"])}
    n = len(idx)
    tp, fp, fn = np.zeros(n), np.zeros(n), np.zeros(n)
    for _, r in tm.iterrows():
        i = idx.get(r["tile_name"])
        if i is not None:
            tp[i], fp[i], fn[i] = float(r["tp"]), float(r["fp"]), float(r["fn"])
    return {"family": fam, "subset": subset, "prob_t": prob_t, "k": k, "n_det": int(len(sub)),
            "f1": micro_f1(int(tp.sum()), int(fp.sum()), int(fn.sum())),
            "arr": np.stack([tp, fp, fn], axis=1)}


def _test(job):
    a, b = job["a"], job["b"]
    r = paired_permutation_test({"tp": a[:, 0], "fp": a[:, 1], "fn": a[:, 2]},
                                {"tp": b[:, 0], "fp": b[:, 1], "fn": b[:, 2]},
                                n_permutations=N_PERMS, seed=SEED)
    m = r["metrics"]["f1"]
    return {**job["meta"], "f1_a": m["a"], "f1_b": m["b"], "dF1": m["observed_diff"], "abs_dF1": abs(m["observed_diff"]),
            "perm_p": m["p_value"], "null_std": m["null_std"], "n_discordant": r["n_discordant_tiles"]}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--gate-only", action="store_true")
    ap.add_argument("--workers", type=int, default=20)
    ap.add_argument("--out", type=Path, default=Path("/tmp/w27"))
    args = ap.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    eq = dedup_equality_gate()
    print(f"GATE dedup_fast == deduplicate_within_pass on g37 run_1: {eq}", flush=True)
    if not eq["pass"]:
        print("GATE FAILURE: nothing written", flush=True)
        return 1
    fam = build_families(args.gate_only)
    print(f"families loaded in {time.time() - t0:.0f}s: " + ", ".join(f"{k}(n={v['n']})" for k, v in fam.items()), flush=True)

    # Gates: first-N subsets reproduce committed rung cells exactly.
    gates = {}
    for (f, subset, prob_t, k), expected in GATES.items():
        cell = inherit(cluster_subset(fam[f]["passes"], subset, fam[f]["index"]), fam[f]["union"])
        n = int(((cell["mound_probability"] >= prob_t) & (cell["vote_count"] >= k)).sum())
        gates[f"{f} {subset} ({prob_t}, k{k})"] = {"expected": expected, "got": n, "pass": n == expected}
        print(f"GATE {f} {subset} ({prob_t}, k{k}): expected {expected}, got {n} -> {'PASS' if n == expected else 'FAIL'}", flush=True)
    gates["dedup_fast equality (g37 run_1)"] = eq
    (args.out / "gates.json").write_text(json.dumps(gates, indent=1))
    if not all(g["pass"] for g in gates.values()):
        print("GATE FAILURE: nothing written", flush=True)
        return 1
    if args.gate_only:
        return 0

    # Build every subset cell frame (clustered + inherited) in parallel: the
    # families are placed in a module global before the pool forks, so the
    # workers inherit them without pickling (fork start method on Linux).
    _G["fam"] = fam
    frame_jobs = [(f, s) for f, spec in fam.items() for subs in subsets_for(spec["n"]).values() for s in subs]
    with Pool(args.workers) as pool:
        built = pool.map(_build_frame, frame_jobs, chunksize=1)
    frames: dict[tuple, gpd.GeoDataFrame] = dict(zip(frame_jobs, built))
    upl = load_upl_frame()
    for s, name in (((0, 1, 2, 3, 4), "first5"), ((5, 6, 7, 8, 9), "last5")):
        runs = {f"run_{i + 1}" for i in s}
        g = upl.copy()
        g["vote_count"] = [sum(r in runs for r in c) for c in g["contrib"]]
        g = g[g["vote_count"] >= 3]  # within the verified >= 3-of-10 band by construction
        frames[("UPL", s)] = g
    print(f"{len(frames)} subset frames built in {time.time() - t0:.0f}s", flush=True)

    ref = reference_gt("r2")
    bounds = gpd.read_file(BOUNDS)
    bounds = (bounds.set_crs("EPSG:4326") if bounds.crs is None else bounds).to_crs("EPSG:32635")
    order = sorted(bounds["tile_name"].tolist())
    tasks = []
    for (f, s), det in frames.items():
        n_rung = len(s)
        for prob_t in PROBS[f]:
            for k in ks_for(n_rung):
                tasks.append((f, s, prob_t, k, det))
    print(f"{len(tasks)} scoring tasks", flush=True)
    with Pool(args.workers, initializer=_init, initargs=(ref, bounds, order)) as pool:
        scored = pool.map(_score, tasks, chunksize=1)
    print(f"scored in {time.time() - t0:.0f}s", flush=True)
    by = {(r["family"], r["subset"], r["prob_t"], r["k"]): r for r in scored}
    np.savez_compressed(args.out / "subset_cells.npz",
                        keys=np.array([json.dumps([r["family"], list(r["subset"]), r["prob_t"], r["k"]]) for r in scored]),
                        arr=np.stack([r["arr"] for r in scored]))
    cells = [{k: v for k, v in r.items() if k != "arr"} for r in scored]
    (args.out / "subset_cells.json").write_text(json.dumps(cells, indent=1, default=list))

    jobs = []
    for f in sorted({r["family"] for r in scored}):
        subs = sorted({r["subset"] for r in scored if r["family"] == f}, key=lambda s: (len(s), s))
        for sa, sb in itertools.combinations(subs, 2):
            if len(sa) != len(sb) or set(sa) & set(sb):
                continue
            for prob_t in PROBS[f]:
                for k in ks_for(len(sa)):
                    ra, rb = by[(f, sa, prob_t, k)], by[(f, sb, prob_t, k)]
                    jobs.append({"a": ra["arr"], "b": rb["arr"],
                                 "meta": {"family": f, "n_rung": len(sa), "subset_a": sa, "subset_b": sb,
                                          "prob_t": prob_t, "k": k, "n_det_a": ra["n_det"], "n_det_b": rb["n_det"],
                                          "kind": "cross-execution (04-18 vs 06-11)" if f == "UPL" else "within-execution"}})
    print(f"{len(jobs)} disjoint pairs to test", flush=True)
    with Pool(args.workers) as pool:
        res = pool.map(_test, jobs, chunksize=4)
    import csv
    with open(args.out / "subset_pairs.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(res[0].keys()))
        w.writeheader()
        for r in res:
            w.writerow({k: (json.dumps(v) if isinstance(v, (tuple, list)) else v) for k, v in r.items()})
    print(f"done in {time.time() - t0:.0f}s -> {args.out}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
