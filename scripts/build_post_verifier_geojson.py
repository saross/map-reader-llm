"""Build a post-verifier detection GeoJSON at a given probability threshold.

Given a ``candidate_manifest.json`` + ``probabilities.json`` pair from the PV
pipeline, filter candidates whose ``mound_probability`` meets the threshold
and write them as a GeoJSON ``FeatureCollection`` in EPSG:4326 (RFC 7946).

Used as input to ``pairwise_permutation_test.py --mode geojson`` so that
post-verifier detection sets from different conditions can be compared
tile-level.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

import geopandas as gpd
from shapely.geometry import Point


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--manifest", type=Path, required=True)
    p.add_argument("--probabilities", type=Path, required=True)
    p.add_argument("--threshold", type=float, required=True)
    p.add_argument("--output", type=Path, required=True)
    args = p.parse_args()

    manifest = json.load(open(args.manifest))
    probs_raw = json.load(open(args.probabilities))
    # results is a dict keyed by zero-padded candidate key (e.g. "candidate_00005")
    results = probs_raw["results"]

    candidates = manifest["candidates"]
    kept_features = []
    for c in candidates:
        cid = c["candidate_id"]
        key = f"candidate_{cid:05d}"
        entry = results.get(key)
        if entry is None:
            continue
        prob = entry.get("mound_probability")
        if prob is None or prob < args.threshold:
            continue
        x, y = c["centroid_x"], c["centroid_y"]
        kept_features.append({
            "type": "Feature",
            "geometry": {"type": "Point", "coordinates": [float(x), float(y)]},
            "properties": {
                "candidate_id": str(cid),
                "mound_probability": float(prob),
                "source_tile": c.get("source_tile", ""),
            }
        })

    # Reproject to EPSG:4326 for RFC 7946 compliance via geopandas
    if kept_features:
        gdf = gpd.GeoDataFrame.from_features(kept_features, crs="EPSG:32635").to_crs("EPSG:4326")
        gdf.to_file(args.output, driver="GeoJSON")
    else:
        with open(args.output, "w") as f:
            json.dump({"type": "FeatureCollection", "features": []}, f)

    print(f"Wrote {len(kept_features)} features to {args.output} (threshold={args.threshold})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
