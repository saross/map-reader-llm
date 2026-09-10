#!/usr/bin/env python3
"""G1 drift bisect: re-score the archived Era-2 PV board's one moved input.

Context
-------
Gate G1 of the GS Era-2 verified board
(``planning/gs-era2-verified-board-2026-09-08.md`` § 6) rebuilt the
archived 44-cell Era-2 PV board from its archived inputs with the retired
builder and found one cell, ``pv-high-image-t0.3-n5``, moved
F1@20 m 0.7460 → 0.7475. This script bisects that movement by scoring
two blobs of the same file under today's evaluator, with the retired
builder's own evaluation worker (``_evaluate_single_threshold``: ground
truth ``mounds-reference.geojson``, buffers 20/30/40/50/100 m,
bootstrap 1,000, seed 42) on the bounds the archived board recorded:

* OLD = blob ``456dd9bf`` (372 features, WGS 84 degrees, no ``crs``
  member; committed at ``bd24293d4`` 2026-04-19; the content the archived
  cache entry was computed from at ``f8d755790`` 2026-04-25).
* NEW = blob ``9d65ac84`` (373 features, EPSG:32635 metres with a ``crs``
  member; re-materialised and committed at ``d6cdb648b`` 2026-05-06; the
  content that survives under ``archive/`` today).

It also identifies the feature(s) present in NEW but absent from OLD by
reprojecting OLD and nearest-matching within 1 m.

Result (2026-09-10, sapphire): OLD reproduces every archived number to
four decimals at all five buffers (F1@20 0.7460, tile MCC 0.8049); NEW
scores 0.7475 with recall up by one true positive. The movement is a
stale label-keyed evaluation cache served at the 2026-05-06 build, not
evaluator drift. Record: ``results/leaderboard/era2/
gs-era2-verified-board-2026-09-10/g1-regression.json`` (``bisect`` block)
and the sidecar ``g1-bisect-rescore.json`` beside it.

Usage
-----
Run from the repository root, on sapphire (bootstrap 1,000 × 5 buffers × 2)::

    git show 005e6c71:results/leaderboard/era2/pv-materialised/\\
        pv-high-image-t0.3-n5.geojson > /tmp/g1/old-456dd9bf.geojson
    python3 scripts/g1_drift_bisect_rescore.py \\
        /tmp/g1/old-456dd9bf.geojson \\
        archive/superseded-leaderboards/leaderboard/era2/pv-materialised/\\
            pv-high-image-t0.3-n5.geojson \\
        /tmp/g1/g1-bisect-rescore.json \\
        inputs/vectors/bounds/384/full_evaluation_bounds.geojson

The bounds argument is explicit because the builder's ``DEFAULT_BOUNDS``
is the 340-tile Era-1 file, not the 487-tile ``384/`` file the archived
board's metadata records.
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import geopandas as gpd  # noqa: E402
from build_tiered_leaderboard import (  # noqa: E402
    DEFAULT_BOUNDS,
    DEFAULT_GROUND_TRUTH,
    _evaluate_single_threshold,
)

BUFFERS = [20, 30, 40, 50, 100]
N_BOOTSTRAP = 1000
SEED = 42
MATCH_TOLERANCE_M = 1.0


def score_blob(path: Path, bounds: Path, label: str) -> dict:
    """Score one detection GeoJSON with the retired builder's worker.

    Args:
        path: Detection GeoJSON (any CRS the loader accepts).
        bounds: Evaluation bounds GeoJSON (tile polygons).
        label: Human-readable label for logging.

    Returns:
        Per-buffer F1/precision/recall, n_detections, tile MCC point and
        the tile confusion matrix.
    """
    result = _evaluate_single_threshold(
        path, DEFAULT_GROUND_TRUTH, bounds, BUFFERS, N_BOOTSTRAP, SEED, label,
    )
    keep: dict = {}
    # ``result["buffers"]`` is a list of per-buffer dicts (see
    # ``build_tiered_leaderboard._write_eval_cache``).
    for buffer_result in result.get("buffers", []):
        keep[f'{buffer_result["buffer_metres"]}m'] = {
            k: buffer_result.get(k) for k in ("f1", "precision", "recall")
        }
    keep["n_detections"] = result.get("n_detections")
    tile_class = result.get("tile_classification")
    if tile_class:
        keep["mcc_point"] = tile_class.get("mcc", {}).get("point")
        keep["confusion"] = tile_class.get("confusion")
    return keep


def features_only_in_new(old_path: Path, new_path: Path) -> list[dict]:
    """Return NEW features with no OLD feature within ``MATCH_TOLERANCE_M``.

    OLD is WGS 84 without a ``crs`` member; NEW carries EPSG:32635. Both
    are compared in EPSG:32635.
    """
    g_old = (
        gpd.read_file(old_path)
        .set_crs("EPSG:4326", allow_override=True)
        .to_crs("EPSG:32635")
    )
    g_new = gpd.read_file(new_path)
    if g_new.crs is None:
        g_new = g_new.set_crs("EPSG:32635")
    g_new = g_new.to_crs("EPSG:32635")
    joined = gpd.sjoin_nearest(
        g_new, g_old[["geometry"]], how="left", distance_col="d",
    )
    joined = joined[~joined.index.duplicated(keep="first")]
    unmatched = joined[joined["d"] > MATCH_TOLERANCE_M]
    return [
        {
            "x": float(geom.x),
            "y": float(geom.y),
            "nearest_old_m": float(dist),
            "vote_count": int(votes),
            "subtype": str(subtype),
            "source_tiles": [str(t) for t in tiles],
        }
        for geom, dist, votes, subtype, tiles in zip(
            unmatched.geometry, unmatched["d"], unmatched["vote_count"],
            unmatched["subtype"], unmatched["source_tiles"],
        )
    ]


def main() -> None:
    """Score both blobs, diff their feature sets, and write the record."""
    if len(sys.argv) != 5:
        sys.exit(__doc__)
    old_path, new_path, out_path, bounds_path = map(Path, sys.argv[1:5])
    record = {
        "gt": str(DEFAULT_GROUND_TRUTH),
        "bounds": str(bounds_path),
        "builder_default_bounds_unused": str(DEFAULT_BOUNDS),
        "buffers": BUFFERS,
        "bootstrap": N_BOOTSTRAP,
        "seed": SEED,
        "blobs": {},
    }
    for name, path in (("old_456dd9bf", old_path), ("new_9d65ac84", new_path)):
        record["blobs"][name] = score_blob(path, bounds_path, name)
        print(name, json.dumps(record["blobs"][name]), flush=True)
    record["new_minus_old"] = features_only_in_new(old_path, new_path)
    record["n_old"] = len(gpd.read_file(old_path))
    record["n_new"] = len(gpd.read_file(new_path))
    print("new-minus-old:", json.dumps(record["new_minus_old"]), flush=True)
    out_path.write_text(json.dumps(record, indent=2))


if __name__ == "__main__":
    main()
