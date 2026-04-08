#!/usr/bin/env python3
"""
Export QGIS Sanity Check Layers
===============================

Reads verified Proposer-Verifier detection output, applies a probability
threshold, matches detections against the curated reference mounds using
the Hungarian algorithm, and writes classified GeoJSON layers for visual
inspection in QGIS.

Outputs (all EPSG:32635):
    - qgis_tp.geojson — True positive detections (matched to reference)
    - qgis_fp.geojson — False positive detections (no matching reference)
    - qgis_fn.geojson — False negative reference mounds (missed by VLM)
    - qgis_rejected.geojson — Candidates below verifier threshold (context)

Each feature carries classification metadata, verifier score, source tile,
and match distance (where applicable).

Usage::

    python scripts/export_qgis_sanity_check.py
    python scripts/export_qgis_sanity_check.py --threshold 0.20
    python scripts/export_qgis_sanity_check.py --verified path/to/verified.geojson

Author: Shawn Ross, Claude Code
Licence: Apache 2.0
"""

import argparse
import json
import sys
from pathlib import Path

import geopandas as gpd
import numpy as np
from scipy.optimize import linear_sum_assignment
from shapely.geometry import Point, mapping

# Default paths
DEFAULT_VERIFIED = (
    "outputs/h11/proposer-verifier-384/verified-adversarial-text.geojson"
)
DEFAULT_MANIFEST = (
    "outputs/h11/proposer-verifier-384/candidates/candidate_manifest.json"
)
DEFAULT_REFERENCE = "inputs/vectors/references/mounds-reference.geojson"
DEFAULT_TILE_BOUNDS = "inputs/vectors/bounds/384/full_evaluation_bounds.geojson"
DEFAULT_OUTPUT_DIR = "outputs/qgis-sanity-check"
DEFAULT_THRESHOLD = 0.15  # Optimal from threshold sweep
DEFAULT_BUFFER = 20.0  # Preregistered matching distance in metres
CRS = "EPSG:32635"


def load_verified_detections(
    verified_geojson_path: Path,
    manifest_path: Path,
) -> gpd.GeoDataFrame:
    """
    Load verified PV detections with precise centroid coordinates.

    The verified GeoJSON stores crop-region polygons, but the evaluation
    pipeline uses candidate manifest centroids for spatial matching. This
    function merges verifier scores from the GeoJSON with precise point
    locations from the manifest.
    """
    # Load verifier scores from GeoJSON, indexed by tile + polygon centroid
    # for spatial matching against manifest candidates (different ordering).
    with open(verified_geojson_path) as f:
        verified = json.load(f)

    verified_records: list[dict] = []
    for feat in verified["features"]:
        props = feat["properties"]
        tile = props.get("source_tile", "")
        vr = props.get("verifier_results", [])
        if isinstance(vr, str):
            vr = json.loads(vr)
        score = vr[0].get("score", 0.0) if vr else 0.0
        reason = vr[0].get("reason", "") if vr else ""

        # Compute polygon centroid for spatial matching
        coords = feat["geometry"]["coordinates"][0]
        cx = sum(c[0] for c in coords) / len(coords)
        cy = sum(c[1] for c in coords) / len(coords)

        verified_records.append({
            "tile": tile,
            "cx": cx,
            "cy": cy,
            "score": score,
            "reason": reason,
            "used": False,
        })

    # Load precise centroids from manifest
    with open(manifest_path) as f:
        manifest = json.load(f)

    # Match manifest candidates to verified records by tile + nearest centroid
    rows = []
    for candidate in manifest["candidates"]:
        cid = candidate["candidate_id"]
        cx = candidate["centroid_x"]
        cy = candidate["centroid_y"]
        tile = candidate["source_tile"]
        props = candidate.get("properties", {})

        # Find nearest unused verified record from same tile
        best_dist = float("inf")
        best_idx = -1
        for i, vr in enumerate(verified_records):
            if vr["used"] or vr["tile"] != tile:
                continue
            dist = ((vr["cx"] - cx) ** 2 + (vr["cy"] - cy) ** 2) ** 0.5
            if dist < best_dist:
                best_dist = dist
                best_idx = i

        score = 0.0
        reason = ""
        if best_idx >= 0:
            verified_records[best_idx]["used"] = True
            score = verified_records[best_idx]["score"]
            reason = verified_records[best_idx]["reason"]

        rows.append({
            "candidate_id": cid,
            "source_tile": tile,
            "verifier_score": score,
            "verifier_reason": reason,
            "subtype": props.get("subtype", ""),
            "label": props.get("label", ""),
            "confidence": props.get("confidence", ""),
            "geometry": Point(cx, cy),
        })

    gdf = gpd.GeoDataFrame(rows, geometry="geometry", crs=CRS)
    return gdf


def match_detections(
    det_geoms: list,
    ref_geoms: list,
    max_distance: float,
) -> tuple[list[int], list[int], list[int], list[int], dict[int, float]]:
    """
    Hungarian-algorithm one-to-one matching with distance tracking.

    Returns matched/unmatched indices plus a dict mapping matched
    detection index to match distance.
    """
    n_det = len(det_geoms)
    n_ref = len(ref_geoms)

    if n_det == 0 or n_ref == 0:
        return ([], [], list(range(n_det)), list(range(n_ref)), {})

    inf_cost = max_distance * 1000
    cost_matrix = np.full((n_det, n_ref), inf_cost)

    for i, det_geom in enumerate(det_geoms):
        det_pt = det_geom.centroid if det_geom.geom_type != "Point" else det_geom
        for j, ref_geom in enumerate(ref_geoms):
            ref_pt = (
                ref_geom.centroid if ref_geom.geom_type != "Point" else ref_geom
            )
            dist = det_pt.distance(ref_pt)
            if dist <= max_distance:
                cost_matrix[i, j] = dist

    det_idx, ref_idx = linear_sum_assignment(cost_matrix)

    matched_det = []
    matched_ref = []
    distances = {}
    for d, r in zip(det_idx, ref_idx):
        if cost_matrix[d, r] <= max_distance:
            matched_det.append(d)
            matched_ref.append(r)
            distances[d] = float(cost_matrix[d, r])

    unmatched_det = [i for i in range(n_det) if i not in matched_det]
    unmatched_ref = [i for i in range(n_ref) if i not in matched_ref]

    return (matched_det, matched_ref, unmatched_det, unmatched_ref, distances)


def build_point_feature(
    geom,
    classification: str,
    properties: dict,
) -> dict:
    """Create a GeoJSON feature with centroid point geometry."""
    if geom.geom_type == "MultiPoint":
        pt = geom.centroid
    elif geom.geom_type != "Point":
        pt = geom.centroid
    else:
        pt = geom
    return {
        "type": "Feature",
        "geometry": mapping(pt),
        "properties": {**properties, "classification": classification},
    }


def export_layers(
    verified_path: Path,
    manifest_path: Path,
    reference_path: Path,
    tile_bounds_path: Path,
    output_dir: Path,
    threshold: float,
    buffer_m: float,
) -> dict:
    """
    Main export logic.

    Returns summary statistics dict.
    """
    output_dir.mkdir(parents=True, exist_ok=True)

    # Load data
    print(f"Loading verified detections from {verified_path}")
    print(f"  Using manifest centroids from {manifest_path}")
    gdf_det = load_verified_detections(verified_path, manifest_path)
    print(f"  {len(gdf_det)} candidates loaded")

    print(f"Loading reference mounds from {reference_path}")
    gdf_ref = gpd.read_file(reference_path)
    print(f"  {len(gdf_ref)} reference mounds loaded")

    # Scope references to tile evaluation bounds (avoids counting mounds
    # outside the tiled area as false negatives)
    print(f"Scoping references to tile bounds from {tile_bounds_path}")
    gdf_bounds = gpd.read_file(tile_bounds_path)
    in_scope = gpd.sjoin(gdf_ref, gdf_bounds, how="inner", predicate="intersects")
    gdf_ref = gdf_ref.loc[gdf_ref.index.isin(in_scope.index)].copy()
    print(f"  {len(gdf_ref)} in-scope references ({len(in_scope.index.unique())} unique)")

    # Ensure CRS match
    if gdf_det.crs is None:
        gdf_det = gdf_det.set_crs(CRS)
    if gdf_det.crs != gdf_ref.crs:
        print(f"  Reprojecting detections from {gdf_det.crs} to {gdf_ref.crs}")
        gdf_det = gdf_det.to_crs(gdf_ref.crs)

    # Apply threshold
    accepted = gdf_det[gdf_det["verifier_score"] >= threshold].copy()
    rejected = gdf_det[gdf_det["verifier_score"] < threshold].copy()
    print(f"  {len(accepted)} accepted (score >= {threshold})")
    print(f"  {len(rejected)} rejected (score < {threshold})")

    # Match accepted detections against reference
    print(f"Matching at {buffer_m}m buffer using Hungarian algorithm...")
    det_geoms = list(accepted.geometry)
    ref_geoms = list(gdf_ref.geometry)
    (
        matched_det, matched_ref, unmatched_det, unmatched_ref, distances
    ) = match_detections(det_geoms, ref_geoms, buffer_m)

    n_tp = len(matched_det)
    n_fp = len(unmatched_det)
    n_fn = len(unmatched_ref)
    precision = n_tp / (n_tp + n_fp) if (n_tp + n_fp) > 0 else 0
    recall = n_tp / (n_tp + n_fn) if (n_tp + n_fn) > 0 else 0
    f1 = (
        2 * precision * recall / (precision + recall)
        if (precision + recall) > 0
        else 0
    )

    print(f"\n  TP: {n_tp}  FP: {n_fp}  FN: {n_fn}")
    print(f"  Precision: {precision:.3f}  Recall: {recall:.3f}  F1: {f1:.3f}")

    # Build classified feature collections
    tp_features = []
    fp_features = []
    fn_features = []
    rejected_features = []

    # True positives — accepted detections that matched a reference
    for i, det_idx in enumerate(matched_det):
        row = accepted.iloc[det_idx]
        ref_row = gdf_ref.iloc[matched_ref[i]]
        props = {
            "source_tile": row.get("source_tile", ""),
            "verifier_score": float(row["verifier_score"]),
            "verifier_reason": row.get("verifier_reason", ""),
            "match_distance_m": round(distances.get(det_idx, -1), 1),
            "matched_ref_symbol": ref_row.get("Symbol", ""),
            "subtype": row.get("subtype", ""),
            "map": ref_row.get("Map", ""),
        }
        tp_features.append(
            build_point_feature(row.geometry, "TP", props)
        )

    # False positives — accepted detections with no matching reference
    for det_idx in unmatched_det:
        row = accepted.iloc[det_idx]
        props = {
            "source_tile": row.get("source_tile", ""),
            "verifier_score": float(row["verifier_score"]),
            "verifier_reason": row.get("verifier_reason", ""),
            "subtype": row.get("subtype", ""),
        }
        fp_features.append(
            build_point_feature(row.geometry, "FP", props)
        )

    # False negatives — reference mounds with no matching detection
    for ref_idx in unmatched_ref:
        row = gdf_ref.iloc[ref_idx]
        props = {
            "symbol": row.get("Symbol", ""),
            "map": row.get("Map", ""),
            "author": row.get("Author", ""),
        }
        fn_features.append(
            build_point_feature(row.geometry, "FN", props)
        )

    # Rejected candidates — below threshold, for context
    for _, row in rejected.iterrows():
        props = {
            "source_tile": row.get("source_tile", ""),
            "verifier_score": float(row["verifier_score"]),
            "verifier_reason": row.get("verifier_reason", ""),
            "subtype": row.get("subtype", ""),
        }
        rejected_features.append(
            build_point_feature(row.geometry, "REJECTED", props)
        )

    # Write GeoJSON files
    crs_block = {
        "type": "name",
        "properties": {"name": "urn:ogc:def:crs:EPSG::32635"},
    }

    for name, features in [
        ("qgis_tp", tp_features),
        ("qgis_fp", fp_features),
        ("qgis_fn", fn_features),
        ("qgis_rejected", rejected_features),
    ]:
        fc = {
            "type": "FeatureCollection",
            "crs": crs_block,
            "features": features,
        }
        out_path = output_dir / f"{name}.geojson"
        with open(out_path, "w") as f:
            json.dump(fc, f, indent=2)
        print(f"  Wrote {out_path} ({len(features)} features)")

    summary = {
        "threshold": threshold,
        "buffer_m": buffer_m,
        "total_candidates": len(gdf_det),
        "accepted": len(accepted),
        "rejected": len(rejected),
        "tp": n_tp,
        "fp": n_fp,
        "fn": n_fn,
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "f1": round(f1, 4),
        "verified_source": str(verified_path),
        "reference_source": str(reference_path),
    }

    summary_path = output_dir / "sanity_check_summary.json"
    with open(summary_path, "w") as f:
        json.dump(summary, f, indent=2)
    print(f"  Wrote {summary_path}")

    return summary


def main() -> None:
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Export classified detection layers for QGIS inspection.",
    )
    parser.add_argument(
        "--verified",
        type=Path,
        default=Path(DEFAULT_VERIFIED),
        help="Path to verified PV GeoJSON (default: adversarial-text 384px)",
    )
    parser.add_argument(
        "--manifest",
        type=Path,
        default=Path(DEFAULT_MANIFEST),
        help="Path to candidate manifest JSON with precise centroids",
    )
    parser.add_argument(
        "--reference",
        type=Path,
        default=Path(DEFAULT_REFERENCE),
        help="Path to reference mounds GeoJSON",
    )
    parser.add_argument(
        "--tile-bounds",
        type=Path,
        default=Path(DEFAULT_TILE_BOUNDS),
        help="Path to tile evaluation bounds GeoJSON",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path(DEFAULT_OUTPUT_DIR),
        help="Output directory for QGIS layers",
    )
    parser.add_argument(
        "--threshold",
        type=float,
        default=DEFAULT_THRESHOLD,
        help=f"Verifier probability threshold (default: {DEFAULT_THRESHOLD})",
    )
    parser.add_argument(
        "--buffer",
        type=float,
        default=DEFAULT_BUFFER,
        help=f"Matching distance in metres (default: {DEFAULT_BUFFER})",
    )
    args = parser.parse_args()

    for label, path in [
        ("verified", args.verified),
        ("manifest", args.manifest),
        ("reference", args.reference),
        ("tile-bounds", args.tile_bounds),
    ]:
        if not path.exists():
            print(f"Error: {label} file not found: {path}", file=sys.stderr)
            sys.exit(1)

    export_layers(
        verified_path=args.verified,
        manifest_path=args.manifest,
        reference_path=args.reference,
        tile_bounds_path=args.tile_bounds,
        output_dir=args.output_dir,
        threshold=args.threshold,
        buffer_m=args.buffer,
    )


if __name__ == "__main__":
    main()
