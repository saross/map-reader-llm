"""Rebuild the gitignored leak-filtered detection copies of the null-exemplar analysis.

Frames blast-radius measurement, Session 163 (2026-10-07). Read-only with respect to the
repository: the copies are written under ``--dest``, never into the checkout.

``results/null-exemplar-sensitivity-2026-09-13/detections_manifest.json`` records, per cell,
each source detection file and the filtered copy that
``scripts/analyse_null_exemplar_sensitivity.py --stage filter`` wrote (gitignored). The
filter (``filter_one``) drops every feature whose booking tile (its ``source_tile``, or, when
the file has none, the first frame tile it intersects) is one of the frame's null-exemplar
overlap tiles (``overlap_tiles.json``). This script re-implements that rule line for line,
writes the copies under ``--dest`` mirroring the recorded paths, and checks every kept count
against the manifest, so the 235 reduced-frame evaluations can be re-scored.

Usage::

    PYTHONDONTWRITEBYTECODE=1 .venv/bin/python rebuild_null_exemplar.py \
        --repo ~/Code/map-reader-llm --dest out/nx
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import geopandas as gpd

NX = "results/null-exemplar-sensitivity-2026-09-13"
TARGET_CRS = "EPSG:32635"


def main() -> int:
    """Rebuild every filtered copy and verify its kept-feature count."""
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--repo", type=Path, required=True)
    ap.add_argument("--dest", type=Path, required=True)
    args = ap.parse_args()
    repo = args.repo.expanduser().resolve()
    manifest = json.loads((repo / NX / "detections_manifest.json").read_text())
    overlap = json.loads((repo / NX / "overlap_tiles.json").read_text())
    frames = {f["frame_id"]: f for f in overlap["frames"]}
    bounds_cache: dict[str, gpd.GeoDataFrame] = {}
    n_files = n_ok = 0
    bad = []
    for cell in manifest["cells"]:
        frame = frames[cell["frame_id"]]
        drop = set(frame["overlap_tiles"])
        if frame["bounds"] not in bounds_cache:
            bounds_cache[frame["bounds"]] = gpd.read_file(repo / frame["bounds"]).to_crs(
                TARGET_CRS)
        full_bounds = bounds_cache[frame["bounds"]]
        for entry in cell["files"]:
            payload = json.loads((repo / entry["source"]).read_text())
            features = payload.get("features") or []
            if features and "source_tile" in (features[0].get("properties") or {}):
                booked = [(f.get("properties") or {}).get("source_tile") for f in features]
            elif features:
                gdf = gpd.read_file(repo / entry["source"])
                if gdf.crs is None:
                    gdf = gdf.set_crs("EPSG:4326")
                gdf = gdf.to_crs(TARGET_CRS)
                joined = gpd.sjoin(gdf, full_bounds[["tile_name", "geometry"]],
                                   how="left", predicate="intersects")
                joined = joined[~joined.index.duplicated(keep="first")]
                booked = [None if v is None or v != v else str(v)
                          for v in joined["tile_name"].tolist()]
            else:
                booked = []
            keep = [i for i, tile in enumerate(booked) if tile not in drop]
            payload["features"] = [features[i] for i in keep]
            dest = args.dest / entry["filtered"]
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_text(json.dumps(payload) + "\n")
            n_files += 1
            if len(keep) == entry["n_kept"]:
                n_ok += 1
            else:
                bad.append((entry["filtered"], len(keep), entry["n_kept"]))
    print(f"rebuilt {n_files} files; kept counts match the manifest for {n_ok}")
    for b in bad[:20]:
        print("MISMATCH", b)
    return 0 if not bad else 1


if __name__ == "__main__":
    raise SystemExit(main())
