#!/usr/bin/env python3
"""
Fair 384px vs 512px pairwise comparison.

Evaluates both tile sizes on the same geographic footprint (384px tile
polygons) using the same tile grid for bootstrap resampling. This ensures
a truly paired comparison where the only difference is tile size.

512px PV detections are spatial-joined to 384px tile polygons so that
``compute_per_tile_tp_fp_fn()`` uses the same spatial units for both.

Usage::

    # On sapphire:
    PYTHONPATH=. python3 scripts/compare-384-vs-512.py

Output:
    results/h11-384-pv-diagnostic/pairwise/fair-384-vs-512.json

Created: 2026-03-22
Author: Shawn Ross, Claude Code
Licence: Apache 2.0
"""

from __future__ import annotations

import json
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import geopandas as gpd
from shapely.geometry import Point

from scripts.lib_advanced_metrics import bootstrap_effect_size_ci
from scripts.lib_consensus import load_shared_data

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger(__name__)

BASE = Path(__file__).resolve().parent.parent
TARGET_CRS = "EPSG:32635"


def make_serialisable(obj: object) -> object:
    """Convert numpy types for JSON serialisation."""
    if isinstance(obj, dict):
        return {k: make_serialisable(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [make_serialisable(v) for v in obj]
    if hasattr(obj, "item"):
        return obj.item()
    return obj


def load_probs(probs_path: Path) -> dict:
    """Load probabilities, handling the nested 'results' key."""
    data = json.load(open(probs_path, encoding="utf-8"))
    if "results" in data and isinstance(data["results"], dict):
        return data["results"]
    return {k: v for k, v in data.items() if k.startswith("candidate")}


def build_pv_gdf(
    probs: dict,
    manifest: dict,
    threshold: float,
) -> gpd.GeoDataFrame:
    """Build GeoDataFrame from PV results at a probability threshold."""
    feats = []
    for c in manifest.get("candidates", []):
        cid = f"candidate_{int(c['candidate_id']):05d}"
        prob = probs.get(cid, {})
        mp = (
            prob.get("mound_probability", 0.0)
            if isinstance(prob, dict)
            else float(prob or 0)
        )
        if mp >= threshold:
            feats.append({
                "geometry": Point(c["centroid_x"], c["centroid_y"]),
                "mound_probability": mp,
                "source_tile": c.get("source_tile", ""),
            })
    if not feats:
        return gpd.GeoDataFrame(
            {"geometry": [], "source_tile": [], "mound_probability": []},
            crs=TARGET_CRS,
        )
    return gpd.GeoDataFrame(feats, crs=TARGET_CRS)


def reassign_to_384_tiles(
    gdf: gpd.GeoDataFrame,
    bounds_384: gpd.GeoDataFrame,
) -> gpd.GeoDataFrame:
    """
    Spatial-join detections to 384px tile polygons.

    Assigns each detection to the 384px tile polygon containing it.
    Detections outside all 384px polygons are dropped. The
    ``source_tile`` column is overwritten with the 384px tile name.

    Args:
        gdf: Detection GeoDataFrame (any tile size).
        bounds_384: 384px tile bounds with ``tile_name`` column.

    Returns:
        GeoDataFrame with ``source_tile`` set to 384px tile names.
    """
    if len(gdf) == 0:
        return gdf

    # Ensure matching CRS
    if gdf.crs != bounds_384.crs:
        gdf = gdf.to_crs(bounds_384.crs)

    # Spatial join: keep only detections within a 384px polygon
    joined = gpd.sjoin(
        gdf, bounds_384[["geometry", "tile_name"]],
        how="inner", predicate="within",
    )

    # Overwrite source_tile with the 384px tile name
    joined["source_tile"] = joined["tile_name"]

    # Drop join artifacts and duplicates (a point on a tile boundary
    # could match two overlapping tiles; keep the first match)
    joined = joined.drop(columns=["index_right", "tile_name"])
    joined = joined.drop_duplicates(subset=["geometry"])

    return joined


def load_512_pv(
    phase_dir: str,
    pv_name: str,
) -> tuple[gpd.GeoDataFrame, float] | None:
    """
    Load 512px PV results at the optimal threshold.

    Returns:
        Tuple of (GeoDataFrame, best_f1) or None if files missing.
    """
    sweep_path = BASE / "results" / "pv" / phase_dir / pv_name / "threshold_sweep.json"
    if not sweep_path.exists():
        log.warning("  512px %s: sweep not found at %s", pv_name, sweep_path)
        return None

    sweep_data = json.load(open(sweep_path, encoding="utf-8"))
    if isinstance(sweep_data, dict) and "optimal" in sweep_data:
        best_t = sweep_data["optimal"]["threshold"]
        best_f1 = sweep_data["optimal"]["f1"]
    elif isinstance(sweep_data, list):
        best_entry = max(
            sweep_data,
            key=lambda x: x.get("f1", {}).get("mean", 0),
        )
        best_t = best_entry["threshold"]
        best_f1 = best_entry["f1"]["mean"]
    else:
        log.warning("  512px %s: unknown sweep format", pv_name)
        return None

    # Load probabilities and manifest
    probs_path = (
        BASE / "outputs" / "pv" / "results"
        / phase_dir.split("/")[0] / pv_name / "probabilities.json"
    )
    manifest_path = (
        BASE / "outputs" / "pv" / "crops-150"
        / pv_name / "candidate_manifest.json"
    )
    if not probs_path.exists() or not manifest_path.exists():
        log.warning("  512px %s: missing probs or manifest", pv_name)
        return None

    probs = load_probs(probs_path)
    manifest = json.load(open(manifest_path, encoding="utf-8"))
    gdf = build_pv_gdf(probs, manifest, best_t)
    return gdf, best_f1


def load_384_pv(config: str) -> tuple[gpd.GeoDataFrame, float] | None:
    """
    Load 384px PV results at the optimal threshold.

    Returns:
        Tuple of (GeoDataFrame, best_f1) or None if files missing.
    """
    sweep_path = (
        BASE / "results" / "h11-384-pv-diagnostic"
        / config / "threshold_sweep.json"
    )
    if not sweep_path.exists():
        log.warning("  384px %s: sweep not found", config)
        return None

    sweep = json.load(open(sweep_path, encoding="utf-8"))
    best = max(sweep, key=lambda x: x.get("f1", {}).get("mean", 0))
    best_t = best["threshold"]
    best_f1 = best["f1"]["mean"]

    probs_path = (
        BASE / "outputs" / "h11" / "pv-diag-384"
        / "verified" / config / "probabilities.json"
    )
    manifest_path = (
        BASE / "outputs" / "h11" / "pv-diag-384"
        / "crops" / config / "candidate_manifest.json"
    )
    if not probs_path.exists() or not manifest_path.exists():
        log.warning("  384px %s: missing probs or manifest", config)
        return None

    probs = load_probs(probs_path)
    manifest = json.load(open(manifest_path, encoding="utf-8"))
    gdf = build_pv_gdf(probs, manifest, best_t)
    return gdf, best_f1


def main() -> None:
    """Run all fair 384px vs 512px comparisons."""
    # Load shared data
    gdf_ref, _ = load_shared_data(BASE / "outputs")
    gdf_bounds_384 = gpd.read_file(
        BASE / "inputs" / "vectors" / "bounds" / "384"
        / "full_evaluation_bounds.geojson",
    )
    if str(gdf_bounds_384.crs) != TARGET_CRS:
        gdf_bounds_384 = gdf_bounds_384.to_crs(TARGET_CRS)

    log.info("384px evaluation footprint: %d tiles", len(gdf_bounds_384))

    # Scope ground truth to 384px bounds
    bounds_union = gdf_bounds_384.union_all()
    gt_in_scope = gdf_ref[gdf_ref.geometry.within(bounds_union)]
    log.info("Ground truth mounds in 384px footprint: %d", len(gt_in_scope))

    # Define comparisons
    comparisons = [
        ("I1:loose_consensus", "text-1of10", "phase2", "06-text-1of10",
         "Loose consensus (1-of-10): 384px vs 512px"),
        ("I2:goldilocks", "text-5of10", "phase2", "09-text-5of10",
         "Goldilocks zone (5-of-10): 384px vs 512px"),
        ("I3:best_vs_best", "text-6of10", "phase2", "09-text-5of10",
         "384px best (6-of-10) vs 512px best (5-of-10)"),
        ("I4:deterministic", "text-baseline", "phase2", "01-adversarial-text",
         "Deterministic baseline (N=1 T=0.0): 384px vs 512px"),
        ("I5:image_moderate", "image-3of5", "phase2", "12-image-3of10",
         "Image moderate consensus: 384px vs 512px"),
        ("I6:image_baseline", "image-baseline", "phase2", "17-image-t0.0",
         "Image baseline (N=1 T=0.0): 384px vs 512px"),
    ]

    results = {}

    for name, cfg_384, phase_dir, pv_name, desc in comparisons:
        log.info("")
        log.info("%s: %s", name, desc)

        # Load 384px
        result_384 = load_384_pv(cfg_384)
        if result_384 is None:
            log.warning("  SKIP — 384px data missing")
            continue
        gdf_384, f1_384 = result_384
        log.info(
            "  384px %s: F1=%.3f (%d det)",
            cfg_384, f1_384, len(gdf_384),
        )

        # Load 512px
        result_512 = load_512_pv(phase_dir, pv_name)
        if result_512 is None:
            log.warning("  SKIP — 512px data missing")
            continue
        gdf_512_raw, f1_512 = result_512
        log.info(
            "  512px %s: F1=%.3f (%d det, before clipping)",
            pv_name, f1_512, len(gdf_512_raw),
        )

        # Reassign 512px detections to 384px tile grid
        gdf_512 = reassign_to_384_tiles(gdf_512_raw, gdf_bounds_384)
        log.info(
            "  512px after spatial join to 384px tiles: %d det "
            "(%d dropped outside footprint)",
            len(gdf_512), len(gdf_512_raw) - len(gdf_512),
        )

        if len(gdf_384) == 0 or len(gdf_512) == 0:
            log.warning("  SKIP — empty GDF after filtering")
            continue

        # Paired bootstrap comparison on 384px tile grid
        log.info("  Running paired bootstrap (1000 iterations)...")
        effect = bootstrap_effect_size_ci(
            gdf_det_a=gdf_384,
            gdf_bounds_a=gdf_bounds_384,
            gdf_det_b=gdf_512,
            gdf_bounds_b=gdf_bounds_384,
            gdf_ref=gdf_ref,
            n_iterations=1000,
            random_seed=42,
            return_p_values=True,
        )

        f1d = effect.get("f1_difference", {})
        log.info(
            "  dF1=%+.4f [%+.4f, %+.4f] p=%s "
            "(positive = 384px better)",
            f1d.get("mean", 0),
            f1d.get("ci_lower", 0),
            f1d.get("ci_upper", 0),
            f1d.get("p_value", "N/A"),
        )

        results[name] = {
            "description": desc,
            "config_384": cfg_384,
            "config_512": pv_name,
            "f1_384": f1_384,
            "f1_512": f1_512,
            "det_384": len(gdf_384),
            "det_512_raw": len(gdf_512_raw),
            "det_512_clipped": len(gdf_512),
            "result": effect,
        }

    # Save results
    out_dir = BASE / "results" / "h11-384-pv-diagnostic" / "pairwise"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "fair-384-vs-512.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(make_serialisable(results), f, indent=2)

    log.info("")
    log.info("=" * 60)
    log.info("COMPLETE: %d comparisons → %s", len(results), out_path)
    log.info("=" * 60)


if __name__ == "__main__":
    main()
