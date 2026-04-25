#!/usr/bin/env python3
"""
Augment per-architecture tier JSONs with tile-level MCC @ 20 m.

For each condition in each per-stratum tier JSON, compute tile-level MCC
(with bootstrap CI) at the 20 m buffer using the materialised/consensus
GeoJSON listed in the tier row. Writes `tile_classification` fields into
the evaluation record so the enrichment step can expose MCC in the
markdown.

Reuses `lib_advanced_metrics.calculate_tile_classification` +
`bootstrap_tile_classification_ci` so the methodology matches
`evaluate_detections.py --mcc`.

Usage:
    .venv/bin/python scripts/augment_per_arch_with_mcc.py \\
        --root results/leaderboard/per-architecture \\
        --workers 8

Run on sapphire (uses ~all cores for bootstrap).

Author: Shawn Ross, Claude Code
Licence: Apache 2.0
"""

from __future__ import annotations

import argparse
import json
import sys
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import geopandas as gpd  # noqa: E402
from lib_advanced_metrics import (  # noqa: E402
    bootstrap_tile_classification_ci,
    calculate_tile_classification,
)

ARCHITECTURES = ["single-pass", "consensus", "single-pass+PV", "pv"]
ERAS_BOUNDS = {
    1: REPO_ROOT / "inputs/vectors/bounds/full_evaluation_bounds.geojson",
    2: REPO_ROOT / "inputs/vectors/bounds/384/full_evaluation_bounds.geojson",
    3: REPO_ROOT / "inputs/vectors/bounds/384/h10_test_bounds.geojson",
}
GROUND_TRUTH = REPO_ROOT / "inputs/vectors/references/mounds-reference.geojson"
BUFFER_METRES = 20
N_BOOTSTRAP = 1000
SEED = 42


def compute_mcc_for_condition(
    geojson_path: str,
    bounds_path: str,
    gt_path: str,
    buffer_metres: int,
    n_bootstrap: int,
    seed: int,
) -> dict | None:
    """Worker: compute tile-level MCC + bootstrap CI for one condition."""
    try:
        gdf_det = gpd.read_file(geojson_path)
        gdf_ref = gpd.read_file(gt_path)
        gdf_bounds = gpd.read_file(bounds_path)

        # Reproject all to project CRS (EPSG:32635) so the spatial join
        # and centroid distance calculations are in metres. Without
        # this, GeoJSON files in EPSG:4326 (lat/lon) silently fail
        # tile-level matching.
        TARGET = "EPSG:32635"
        if gdf_det.crs is None:
            gdf_det = gdf_det.set_crs(TARGET)
        elif str(gdf_det.crs) != TARGET:
            gdf_det = gdf_det.to_crs(TARGET)
        if gdf_ref.crs is None:
            gdf_ref = gdf_ref.set_crs(TARGET)
        elif str(gdf_ref.crs) != TARGET:
            gdf_ref = gdf_ref.to_crs(TARGET)
        if gdf_bounds.crs is None:
            gdf_bounds = gdf_bounds.set_crs(TARGET)
        elif str(gdf_bounds.crs) != TARGET:
            gdf_bounds = gdf_bounds.to_crs(TARGET)

        # Ensure source_tile column exists (consensus GeoJSONs may lack it).
        if "source_tile" not in gdf_det.columns and not gdf_det.empty:
            joined = gpd.sjoin(
                gdf_det,
                gdf_bounds[["tile_name", "geometry"]],
                how="left",
                predicate="intersects",
            )
            joined = joined[~joined.index.duplicated(keep="first")]
            gdf_det["source_tile"] = joined["tile_name"]

        # MCC is tile-level (binary "empty vs populated"); the matching
        # buffer is fixed at 20 m inside calculate_tile_classification.
        # The buffer_metres argument is informational only.
        tile_class = calculate_tile_classification(
            gdf_det, gdf_ref, gdf_bounds,
        )
        tile_ci = bootstrap_tile_classification_ci(
            gdf_det, gdf_ref, gdf_bounds,
            n_iterations=n_bootstrap,
            random_seed=seed,
        )
        return {
            "confusion": {
                "tp": tile_class["tp"],
                "tn": tile_class["tn"],
                "fp": tile_class["fp"],
                "fn": tile_class["fn"],
            },
            "mcc": {
                "mean": tile_ci["mcc"]["mean"],
                "ci_lower": tile_ci["mcc"]["ci_lower"],
                "ci_upper": tile_ci["mcc"]["ci_upper"],
            },
            "sensitivity": {
                "mean": tile_ci["sensitivity"]["mean"],
                "ci_lower": tile_ci["sensitivity"]["ci_lower"],
                "ci_upper": tile_ci["sensitivity"]["ci_upper"],
            },
            "specificity": {
                "mean": tile_ci["specificity"]["mean"],
                "ci_lower": tile_ci["specificity"]["ci_lower"],
                "ci_upper": tile_ci["specificity"]["ci_upper"],
            },
        }
    except Exception as e:
        return {"error": str(e)}


def augment_stratum(era: int, arch: str, tier_json: Path, workers: int) -> int:
    """Add tile_classification + per-buffer MCC fields to the tier JSON."""
    if not tier_json.is_file():
        return 0
    bounds = ERAS_BOUNDS[era]
    data = json.loads(tier_json.read_text())

    # Collect unique (label, geojson) pairs to avoid redundant compute.
    work: list[tuple[str, str]] = []
    seen: set[str] = set()
    for tier in data.get("tiers", []):
        for cond in tier["conditions"]:
            if cond["label"] in seen:
                continue
            seen.add(cond["label"])
            work.append((cond["label"], cond["geojson"]))

    print(f"  era{era}/{arch}: {len(work)} conditions to augment with MCC")
    results: dict[str, dict] = {}
    with ProcessPoolExecutor(max_workers=workers) as exe:
        fut_map = {
            exe.submit(
                compute_mcc_for_condition,
                gj, str(bounds), str(GROUND_TRUTH), BUFFER_METRES,
                N_BOOTSTRAP, SEED,
            ): label
            for label, gj in work
        }
        done = 0
        for fut in as_completed(fut_map):
            label = fut_map[fut]
            done += 1
            try:
                results[label] = fut.result()
            except Exception as e:
                results[label] = {"error": str(e)}
            if done % 5 == 0 or done == len(work):
                print(f"    [{done}/{len(work)}] ...")

    # Inject into the tier JSON.
    for tier in data.get("tiers", []):
        for cond in tier["conditions"]:
            mcc_row = results.get(cond["label"])
            if mcc_row is None or "error" in (mcc_row or {}):
                continue
            ev = cond.get("evaluations", {}).get("20") or cond.get("evaluations", {}).get(20)
            if ev is not None:
                ev["mcc"] = mcc_row["mcc"]["mean"]
                ev["mcc_ci_lower"] = mcc_row["mcc"]["ci_lower"]
                ev["mcc_ci_upper"] = mcc_row["mcc"]["ci_upper"]
                ev["tile_tp"] = mcc_row["confusion"]["tp"]
                ev["tile_tn"] = mcc_row["confusion"]["tn"]
                ev["tile_fp"] = mcc_row["confusion"]["fp"]
                ev["tile_fn"] = mcc_row["confusion"]["fn"]

    tier_json.write_text(json.dumps(data, indent=2))
    return len(work)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--root", type=Path,
        default=REPO_ROOT / "results/leaderboard/per-architecture",
    )
    parser.add_argument("--workers", type=int, default=8)
    args = parser.parse_args()

    total = 0
    for era in [1, 2, 3]:
        for arch in ARCHITECTURES:
            tier_json = args.root / f"era{era}" / arch / "leaderboard_tiers_20m.json"
            if tier_json.is_file():
                n = augment_stratum(era, arch, tier_json, args.workers)
                total += n
    print(f"Augmented {total} conditions with tile-level MCC.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
