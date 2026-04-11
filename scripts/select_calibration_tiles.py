#!/usr/bin/env python3
"""Generalised calibration/test tile selector.

Splits a set of ground-truthed tiles into calibration and test subsets
using hierarchical stratified sampling (geographic → density → random),
with optional nested sub-pool generation for the H10 training-pool-size
experiment.

The selector is tile-size-agnostic: it operates on geographic bounds
polygons and reference point GeoJSONs, not pixel coordinates. It works
with any tile grid (384px, 512px, etc.) as long as a bounds GeoJSON
and corresponding ground truth exist.

Usage:
    # Basic split: 160 calibration + rest as test
    python scripts/select_calibration_tiles.py \\
        --bounds inputs/vectors/bounds/384/full_evaluation_bounds.geojson \\
        --reference inputs/vectors/references/mounds-reference.geojson \\
        --calibration-size 160 \\
        --seed 42 \\
        --output-dir inputs/calibration/h10-384

    # Nested pools for H10 (A⊂B⊂C⊂D):
    python scripts/select_calibration_tiles.py \\
        --bounds inputs/vectors/bounds/384/full_evaluation_bounds.geojson \\
        --reference inputs/vectors/references/mounds-reference.geojson \\
        --calibration-size 160 \\
        --nested 20,40,80,160 \\
        --seed 42 \\
        --output-dir inputs/calibration/h10-384

Author: Shawn Ross, Claude Code
Licence: Apache 2.0
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from datetime import datetime, timezone
from pathlib import Path

import geopandas as gpd

# ---------------------------------------------------------------------------
# Path setup — allow imports from scripts/
# ---------------------------------------------------------------------------
_SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(_SCRIPT_DIR))

from lib_calibration import (  # noqa: E402
    enrich_bounds_with_mound_counts,
    nested_subsample,
    stratified_sample,
)

logger = logging.getLogger(__name__)

# =========================================================================
# Core logic
# =========================================================================


def select_and_split(
    bounds_path: Path,
    reference_path: Path,
    calibration_size: int,
    seed: int,
    nested_sizes: list[int] | None = None,
) -> dict:
    """Select calibration and test tiles with optional nesting.

    Enriches the bounds with mound counts, selects a calibration pool
    via stratified sampling, assigns the remainder as the test set, and
    optionally generates nested sub-pools.

    Args:
        bounds_path: Path to tile bounds GeoJSON.
        reference_path: Path to ground-truth reference GeoJSON.
        calibration_size: Number of tiles in the largest calibration
            pool.
        seed: Random seed for reproducibility.
        nested_sizes: Optional sorted list of nested pool sizes (e.g.,
            ``[20, 40, 80, 160]``). The largest must equal
            ``calibration_size``.

    Returns:
        Dict with keys:
            - ``enriched_gdf``: Full enriched GeoDataFrame.
            - ``calibration``: Dict mapping pool size → GeoDataFrame.
            - ``test``: Test set GeoDataFrame.
            - ``metadata``: Provenance dict for serialisation.
    """
    # Enrich bounds with mound counts and density
    logger.info("Enriching bounds with mound counts...")
    enriched = enrich_bounds_with_mound_counts(bounds_path, reference_path)

    total_tiles = len(enriched)
    if calibration_size >= total_tiles:
        raise ValueError(
            f"Calibration size ({calibration_size}) must be less than "
            f"total tiles ({total_tiles})"
        )

    # Select the largest calibration pool
    logger.info(
        "Selecting %d calibration tiles (seed=%d)...",
        calibration_size, seed,
    )
    cal_largest = stratified_sample(enriched, calibration_size, seed)

    # Test set = everything not in calibration
    test_mask = ~enriched.index.isin(cal_largest.index)
    test_set = enriched.loc[test_mask].copy()

    logger.info(
        "Split: %d calibration + %d test = %d total",
        len(cal_largest), len(test_set), total_tiles,
    )

    # Build nested pools (top-down: largest → smallest)
    calibration_pools: dict[int, gpd.GeoDataFrame] = {
        calibration_size: cal_largest,
    }

    if nested_sizes:
        # Validate nesting spec
        sorted_sizes = sorted(nested_sizes, reverse=True)
        if sorted_sizes[0] != calibration_size:
            raise ValueError(
                f"Largest nested size ({sorted_sizes[0]}) must equal "
                f"calibration_size ({calibration_size})"
            )

        parent = cal_largest
        for i, size in enumerate(sorted_sizes[1:], start=1):
            child_seed = seed + i
            child = nested_subsample(parent, size, child_seed)
            calibration_pools[size] = child
            logger.info(
                "  Nested pool %d: %d tiles (seed=%d)",
                size, len(child), child_seed,
            )
            parent = child

    # Validate nesting invariant
    if len(calibration_pools) > 1:
        pool_sizes = sorted(calibration_pools.keys())
        for i in range(len(pool_sizes) - 1):
            smaller = set(calibration_pools[pool_sizes[i]].index)
            larger = set(calibration_pools[pool_sizes[i + 1]].index)
            if not smaller.issubset(larger):
                raise RuntimeError(
                    f"Nesting invariant violated: pool {pool_sizes[i]} "
                    f"is not a subset of pool {pool_sizes[i + 1]}"
                )

    # Build metadata
    metadata = _build_metadata(
        enriched, calibration_pools, test_set,
        bounds_path, reference_path,
        calibration_size, seed, nested_sizes,
    )

    return {
        "enriched_gdf": enriched,
        "calibration": calibration_pools,
        "test": test_set,
        "metadata": metadata,
    }


def _build_metadata(
    enriched: gpd.GeoDataFrame,
    calibration_pools: dict[int, gpd.GeoDataFrame],
    test_set: gpd.GeoDataFrame,
    bounds_path: Path,
    reference_path: Path,
    calibration_size: int,
    seed: int,
    nested_sizes: list[int] | None,
) -> dict:
    """Build provenance metadata for serialisation."""

    def _density_dist(gdf: gpd.GeoDataFrame) -> dict:
        counts = gdf["density"].value_counts().to_dict()
        return {
            "empty": counts.get("empty", 0),
            "sparse": counts.get("sparse", 0),
            "dense": counts.get("dense", 0),
        }

    def _per_map_counts(gdf: gpd.GeoDataFrame) -> dict:
        return gdf["map_name"].value_counts().sort_index().to_dict()

    pool_meta = {}
    for size, pool_gdf in sorted(calibration_pools.items()):
        pool_meta[str(size)] = {
            "n_tiles": len(pool_gdf),
            "mounds_per_tile_sum": int(pool_gdf["mound_count"].sum()),
            "density_distribution": _density_dist(pool_gdf),
            "per_map": _per_map_counts(pool_gdf),
        }

    nesting_chain = None
    if nested_sizes:
        sorted_sizes = sorted(nested_sizes)
        nesting_chain = " ⊂ ".join(str(s) for s in sorted_sizes)

    return {
        "created": datetime.now(timezone.utc).isoformat(),
        "parameters": {
            "bounds_path": str(bounds_path),
            "reference_path": str(reference_path),
            "calibration_size": calibration_size,
            "seed": seed,
            "nested_sizes": nested_sizes,
        },
        "totals": {
            "total_tiles": len(enriched),
            "total_mounds_per_tile_sum": int(
                enriched["mound_count"].sum()
            ),
            "density_distribution": _density_dist(enriched),
            "per_map": _per_map_counts(enriched),
        },
        "calibration_pools": pool_meta,
        "nesting_chain": nesting_chain,
        "test_set": {
            "n_tiles": len(test_set),
            "mounds_per_tile_sum": int(test_set["mound_count"].sum()),
            "density_distribution": _density_dist(test_set),
            "per_map": _per_map_counts(test_set),
        },
    }


# =========================================================================
# Output writing
# =========================================================================


def write_outputs(
    result: dict,
    output_dir: Path,
) -> None:
    """Write all manifests, bounds, and metadata to the output directory.

    Args:
        result: Dict from ``select_and_split``.
        output_dir: Target directory (created if needed).
    """
    output_dir.mkdir(parents=True, exist_ok=True)

    calibration_pools = result["calibration"]
    test_set = result["test"]
    metadata = result["metadata"]

    # Write calibration manifests and bounds for each pool size
    for size, pool_gdf in sorted(calibration_pools.items()):
        # Manifest (sorted tile names)
        manifest_path = output_dir / f"calibration_manifest_{size:03d}.json"
        tiles = sorted(pool_gdf["tile_name"].tolist())
        manifest_path.write_text(
            json.dumps(tiles, indent=2) + "\n", encoding="utf-8",
        )
        logger.info("Wrote %s (%d tiles)", manifest_path.name, len(tiles))

        # Bounds GeoJSON
        bounds_path = output_dir / f"calibration_bounds_{size:03d}.geojson"
        pool_gdf.to_file(bounds_path, driver="GeoJSON")
        logger.info("Wrote %s", bounds_path.name)

    # Write test manifest and bounds
    test_manifest_path = output_dir / "test_manifest.json"
    test_tiles = sorted(test_set["tile_name"].tolist())
    test_manifest_path.write_text(
        json.dumps(test_tiles, indent=2) + "\n", encoding="utf-8",
    )
    logger.info(
        "Wrote %s (%d tiles)", test_manifest_path.name, len(test_tiles),
    )

    test_bounds_path = output_dir / "test_bounds.geojson"
    test_set.to_file(test_bounds_path, driver="GeoJSON")
    logger.info("Wrote %s", test_bounds_path.name)

    # Write metadata
    metadata_path = output_dir / "tile_selection_metadata.json"
    metadata_path.write_text(
        json.dumps(metadata, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    logger.info("Wrote %s", metadata_path.name)


# =========================================================================
# CLI
# =========================================================================


def main(argv: list[str] | None = None) -> None:
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Generalised calibration/test tile selector.",
    )
    parser.add_argument(
        "--bounds", type=Path, required=True,
        help="Path to tile bounds GeoJSON",
    )
    parser.add_argument(
        "--reference", type=Path, required=True,
        help="Path to ground-truth reference GeoJSON",
    )
    parser.add_argument(
        "--calibration-size", type=int, required=True,
        help="Number of tiles in the largest calibration pool",
    )
    parser.add_argument(
        "--seed", type=int, default=None,
        help="Random seed (default: current UTC timestamp)",
    )
    parser.add_argument(
        "--nested", type=str, default=None,
        help="Comma-separated nested pool sizes "
             "(e.g., '20,40,80,160')",
    )
    parser.add_argument(
        "--output-dir", type=Path, required=True,
        help="Output directory for manifests and bounds",
    )
    parser.add_argument(
        "--verbose", "-v", action="store_true",
        help="Enable verbose logging",
    )
    args = parser.parse_args(argv)

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )

    # Resolve seed
    seed = args.seed if args.seed is not None else int(
        datetime.now(timezone.utc).timestamp()
    )

    # Parse nested sizes
    nested_sizes = None
    if args.nested:
        nested_sizes = sorted(
            int(s.strip()) for s in args.nested.split(",")
        )
        if nested_sizes[-1] != args.calibration_size:
            parser.error(
                f"Largest nested size ({nested_sizes[-1]}) must equal "
                f"--calibration-size ({args.calibration_size})"
            )

    # Run selection
    result = select_and_split(
        bounds_path=args.bounds,
        reference_path=args.reference,
        calibration_size=args.calibration_size,
        seed=seed,
        nested_sizes=nested_sizes,
    )

    # Write outputs
    write_outputs(result, args.output_dir)

    # Console summary
    cal_pools = result["calibration"]
    test = result["test"]
    print(f"\nCalibration/test split complete (seed={seed})")
    print(f"  Total tiles: {len(result['enriched_gdf'])}")
    for size in sorted(cal_pools):
        pool = cal_pools[size]
        print(
            f"  Calibration {size:>3d}: {len(pool)} tiles, "
            f"{int(pool['mound_count'].sum())} mounds (per-tile)"
        )
    print(
        f"  Test:           {len(test)} tiles, "
        f"{int(test['mound_count'].sum())} mounds (per-tile)"
    )
    print(f"  Output: {args.output_dir}")


if __name__ == "__main__":
    main()
