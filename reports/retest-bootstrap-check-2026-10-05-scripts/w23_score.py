"""W2.3 step 2: per-tile TP/FP/FN for every replicate pass (read-only).

Scores each pass with the BOARD's own per-tile path
(era1_leaderboard_tiering._read_detections_gdf -> assign_source_tiles ->
_per_tile_one_set -> lib_advanced_metrics.compute_per_tile_tp_fp_fn), which is
the array both tests consume. A validation arm re-scores Era-1 passes with the
HISTORICAL library (fc832dfa9) exactly as the March session loaded them, to
show the arrays the retest bootstrap saw are the same.
Output: /tmp/w2/pertile_<scope>_<buffer>m.npz + /tmp/w2/pass_index.json
"""
import importlib.util
import json
import os
import sys
from multiprocessing import Pool
from pathlib import Path

import numpy as np

REPO = Path.home() / "Code/map-reader-llm"
os.chdir(REPO)
sys.path.insert(0, str(REPO / "scripts"))

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

_cache = {}


def scope_data(scope):
    if scope not in _cache:
        import geopandas as gpd
        from n1_baseline_leaderboard_tiering import TARGET_CRS
        gt, bd, _ = SCOPES[scope]
        ref = gpd.read_file(gt).to_crs(TARGET_CRS)
        bounds = gpd.read_file(bd).to_crs(TARGET_CRS)
        _cache[scope] = (ref, bounds, list(bounds["tile_name"].unique()))
    return _cache[scope]


def score(job):
    import geopandas as gpd
    import pandas as pd
    from era1_leaderboard_tiering import _per_tile_one_set, _read_detections_gdf
    from n1_baseline_leaderboard_tiering import TARGET_CRS
    from pairwise_permutation_test import assign_source_tiles
    scope, files = job["scope"], job["files"]
    ref, bounds, order = scope_data(scope)
    parts = [_read_detections_gdf(REPO / f) for f in files]
    det = parts[0] if len(parts) == 1 else gpd.GeoDataFrame(
        pd.concat(parts, ignore_index=True), crs=TARGET_CRS)
    det = assign_source_tiles(det, bounds)
    out = {"key": job["key"], "n_det": int(len(det))}
    for buf in SCOPES[scope][2]:
        try:
            tp, fp, fn = _per_tile_one_set(det, ref, bounds, order, buf)
            out[buf] = np.stack([tp, fp, fn], axis=1)
        except Exception as e:  # tile-join refusal etc.
            out[buf] = None
            out[f"err{buf}"] = repr(e)[:300]
    return out


def score_old(job):
    """Historical path: fc832dfa9 lib + the March session's load_det."""
    import geopandas as gpd
    spec = importlib.util.spec_from_file_location("oldlib", "/tmp/w2/lib_advanced_metrics_fc832dfa9.py")
    old = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(old)
    _, bounds, ref = old.load_data("inputs/vectors/references/mounds-reference.geojson",
                                   "inputs/vectors/bounds/full_evaluation_bounds.geojson")
    gdf = gpd.read_file(REPO / job["files"][0])
    gdf.set_crs(old.DEFAULT_CRS, allow_override=True, inplace=True)
    if "source_tile" not in gdf.columns and "source_tiles" in gdf.columns:
        gdf["source_tile"] = gdf["source_tiles"].apply(
            lambda x: x[0] if hasattr(x, "__getitem__") and len(x) > 0 else str(x))
    tm = old.compute_per_tile_tp_fp_fn(gdf, ref, bounds, buffer_metres=20).set_index("tile_name")
    order = list(bounds["tile_name"].unique())
    return {"key": job["key"], "arr": tm.loc[order, ["tp", "fp", "fn"]].to_numpy(float)}


if __name__ == "__main__":
    sets = json.loads(Path("/tmp/w2/replicate_sets.json").read_text())
    jobs, index = [], []
    for g, members in sets.items():
        scope = GROUP_SCOPE[int(g)]
        for m in members:
            temps = sorted({json.loads(s).get("temperature_eff") for s in m["signatures"]}, key=str)
            for p in m["passes"]:
                key = f"{m['run_id']}::{m['arm']}::{Path(p['run_dir']).name}"
                index.append({"key": key, "group": int(g), "scope": scope,
                              "run_id": m["run_id"], "arm": m["arm"],
                              "run_dir": p["run_dir"], "files": p["files"],
                              "temperature": temps, "signatures": m["signatures"]})
                jobs.append({"key": key, "scope": scope, "files": p["files"]})
    print(len(jobs), "passes", flush=True)
    with Pool(20) as pool:
        res = pool.map(score, jobs, chunksize=1)
    by_key = {r["key"]: r for r in res}
    for scope, (_, bd, bufs) in SCOPES.items():
        keys = [j["key"] for j in jobs if j["scope"] == scope]
        for buf in bufs:
            ok = [k for k in keys if by_key[k][buf] is not None]
            arr = np.stack([by_key[k][buf] for k in ok]) if ok else np.zeros((0,))
            np.savez_compressed(f"/tmp/w2/pertile_{scope}_{buf}m.npz", keys=np.array(ok), arr=arr)
            print(scope, buf, "scored", len(ok), "of", len(keys), arr.shape, flush=True)
    for row in index:
        r = by_key[row["key"]]
        row["n_det"] = r["n_det"]
        row["errors"] = {k: v for k, v in r.items() if str(k).startswith("err")}
    Path("/tmp/w2/pass_index.json").write_text(json.dumps(index, indent=1))
    # Validation: historical scorer on Era-1 passes (all of them; cheap enough).
    era1 = [j for j in jobs if j["scope"] == "era1"]
    with Pool(20) as pool:
        old_res = pool.map(score_old, era1, chunksize=1)
    new = np.load("/tmp/w2/pertile_era1_20m.npz")
    newmap = dict(zip(new["keys"], new["arr"]))
    n_same = sum(np.array_equal(newmap[o["key"]], o["arr"]) for o in old_res if o["key"] in newmap)
    diffs = [o["key"] for o in old_res if o["key"] in newmap and not np.array_equal(newmap[o["key"]], o["arr"])]
    Path("/tmp/w2/validation_old_vs_new.json").write_text(json.dumps(
        {"n_compared": len(old_res), "n_identical": int(n_same), "differing": diffs}, indent=1))
    print("old-vs-new identical:", n_same, "of", len(old_res), "differing:", diffs[:10], flush=True)
