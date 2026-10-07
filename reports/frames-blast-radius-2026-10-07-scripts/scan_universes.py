"""Count out-of-frame candidates in every verifier candidate universe, against every frame.

Frames blast-radius measurement, Session 163 (2026-10-07). Read-only.

A threshold sweep (``sweep_f1_greedy_pv.py``, ``sweep_f1_wbf.py``, the K-ladder and tier E
sweeps) scores subsets of one candidate universe: the ``candidate_manifest.json`` written by
``run_pv.py extract``. A sweep row can move under a geometric detection scope only if its
universe holds candidates that the name-prefix scope books but the reference rule drops.
This script loads each manifest's candidates (centroid in EPSG:32635, ``source_tile`` as
recorded, exactly as ``sweep_f1_wbf.load_candidates_as_gdf`` builds them, but without the
probability join so the full universe is counted) and reports, for every frame whose maps
the universe touches, the number of such candidates.

Usage::

    PYTHONDONTWRITEBYTECODE=1 .venv/bin/python scan_universes.py \
        --repo ~/Code/map-reader-llm --out out/universes.jsonl --workers 16
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path
from typing import Any

import geopandas as gpd
from shapely.geometry import Point

sys.path.insert(0, str(Path(__file__).resolve().parent))
import blast_lib as bl  # noqa: E402

#: Frames a gold-standard universe is checked against.
GS_FRAMES = {
    "era2-full-487": "inputs/vectors/bounds/384/full_evaluation_bounds.geojson",
    "board-era2b-487": "inputs/vectors/bounds/384/era2_b_intersection_bounds.geojson",
    "grid-common-487": "outputs/grid-2026-08-18/scoring/bounds/grid_common_bounds.geojson",
    "era3-h10-327": "inputs/vectors/bounds/384/h10_test_bounds.geojson",
    "era1-512-340": "inputs/vectors/bounds/full_evaluation_bounds.geojson",
    "px256-1032": "inputs/vectors/bounds/256/full_evaluation_bounds.geojson",
}
#: Frame a 55-map universe is checked against.
MAP55_FRAMES = {
    "55map-8541": "inputs/vectors/bounds/384/55maps_evaluation_bounds.geojson",
}


def load_universe(path: Path) -> gpd.GeoDataFrame:
    """Build the candidate GeoDataFrame the sweeps build, minus the probability join."""
    manifest = json.loads(path.read_text())
    rows = []
    for c in manifest.get("candidates", []):
        props = c.get("properties", {}) or {}
        rows.append({
            "candidate_id": c["candidate_id"],
            "source_tile": c.get("source_tile", ""),
            "vote_count": int(props.get("vote_count", 0)),
            "geometry": Point(float(c["centroid_x"]), float(c["centroid_y"])),
        })
    return gpd.GeoDataFrame(rows, crs=bl.EVAL_CRS)


def scan(repo_s: str, rel: str) -> dict[str, Any]:
    """Worker: count prefix-scoped and out-of-frame candidates per frame for one universe."""
    repo = Path(repo_s)
    bl.add_repo_to_path(repo)
    out: dict[str, Any] = {"manifest": rel}
    try:
        uni = load_universe(repo / rel)
        out["n_candidates"] = len(uni)
        maps = sorted({bl.LIB.get_map_name(str(t)) for t in uni["source_tile"] if t})
        out["n_maps"] = len(maps)
        frames = GS_FRAMES if len(maps) <= 4 else MAP55_FRAMES
        out["frames"] = {}
        for name, bpath in frames.items():
            bounds = bl.load_geojson(repo / bpath)
            if not set(maps) & set(bl.frame_maps(bounds)):
                continue
            scoped, diag = bl.geometric_detection_scope(uni, bounds)
            # Out-of-frame candidates by vote count, so a sweep's vote floor can be checked.
            dropped = uni.loc[~uni.index.isin(scoped.index)]
            diag["dropped_by_vote"] = {
                str(k): int(v) for k, v in dropped["vote_count"].value_counts().items()
            }
            out["frames"][name] = diag
        out["status"] = "ok"
    except Exception as exc:  # noqa: BLE001
        out["status"] = "error"
        out["error"] = f"{type(exc).__name__}: {exc}"
    return out


def main() -> int:
    """Find every committed or on-disk candidate manifest and scan it."""
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--repo", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--workers", type=int, default=16)
    args = ap.parse_args()
    repo = args.repo.expanduser().resolve()
    found = subprocess.check_output(
        ["find", "outputs", "results", "-name", "candidate_manifest.json"], cwd=repo, text=True,
    ).split()
    tracked = set(subprocess.check_output(
        ["git", "-C", str(repo), "ls-files", "*candidate_manifest.json"], text=True,
    ).split())
    with args.out.open("w") as fh, ProcessPoolExecutor(max_workers=args.workers) as pool:
        futs = {pool.submit(scan, str(repo), rel): rel for rel in sorted(found)}
        for fut in as_completed(futs):
            res = fut.result()
            res["git_tracked"] = res["manifest"] in tracked
            fh.write(json.dumps(res) + "\n")
    print(f"DONE {len(found)} manifests -> {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
