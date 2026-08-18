#!/usr/bin/env python3
"""
Prepare the 2026-08-18 tile-size x overlap grid for uniform, comparable scoring.

The grid (`outputs/grid-2026-08-18/`) is a post-hoc (E41-class) 2x2 crossing
tile size with tile overlap, proposer stage only, n = 10 passes per cell, one
configuration throughout (``detect_brief-text``, library
``8580ecb2258b64a0…``, ``gemini-3-flash-preview``, text modality, MINIMAL
thinking, T = 0.7):

=============  =========  ==========  ============  ==========
Cell           Tile (px)  Overlap     Tiles/pass    Directory
=============  =========  ==========  ============  ==========
512 / 12.5 %   512        64 px       296           ``g512_ov064``
512 / 50 %     512        256 px      832           ``g512_ov256``
384 / 12.5 %   384        48 px       487           ``g384_ov048``
384 / 50 %     384        192 px      1398          ``g384_ov192``
=============  =========  ==========  ============  ==========

Three hazards sit between the raw detections and a defensible 2x2, and this
script neutralises all three.

**Hazard 1 — additive recovery passes.** Six passes lost exactly one tile each
to a JSON-parse failure and were recovered as additive one-tile passes in
``run_<N>_recovery`` directories. ``lib_detection_paths.resolve_pool_passes``
deliberately EXCLUDES non-numeric run directories (they supplement a pass
rather than constituting one) and warns. Each recovery is therefore merged
into its parent pass here, exactly as ``prepare_h13_scoring.load_pass`` does
for H13 arm B. Left unmerged, the affected pass would cover N-1 of N tiles,
trip the evaluator's E72 partial-coverage guard, and convert that tile's
ground truth into an artificial false negative — asymmetrically, since
``g384_ov192`` lost three passes to the others' one.

**Hazard 2 — cross-tile duplicates.** ``scripts/evaluate_detections.py`` has
no deduplication step, so a mound visible in two overlapping tiles is emitted
twice and the second copy scores as a false positive under Hungarian matching.
Denser tilings duplicate more, so naive scoring would manufacture a spurious
"overlap hurts precision" result. Every pass in every cell is therefore passed
through the preregistered within-pass 20 m deduplication
(:func:`scripts.merge_passes.deduplicate_within_pass`, § 8.5 Step 1).

**Hazard 3 — divergent evaluation footprints.** All four manifests were pinned
against the same Era-2 384 px footprint by a footprint-majority rule (commit
``fe623a555``), and the 384 / 12.5 % cell reproduces the era-2-487 corpus
exactly. That does NOT make the four tile UNIONS equal: a majority-rule tile
that hangs half off the footprint is kept whole, so a denser tiling accretes
more marginal ground. Measured here, the unions run 1415.8 / 1534.5 / 1508.2 /
1640.6 km² holding 435 / 482 / 466 / 495 reference mounds — the same class of
tile-inclusion confound H13 caught. Every cell is therefore also scored on a
**common** footprint: the intersection of all four unions, carried on the
era-2-487 grid clipped to it.

Two scopes are emitted, following the H13 precedent:

``common``
    The four-way intersection, carried on the era-2-487 grid clipped to it.
    Every cell is scored over identical ground on an identical resampling
    unit, which is what makes tile-paired bootstrap deltas genuinely paired
    and what makes tile-level MCC comparable at all (MCC's classification
    units ARE the carrier tiles).

``native``
    Each cell scored against its own tile bounds. Retained for transparency;
    across-cell differences there are not attributable to geometry alone.

Usage::

    python scripts/grid_prepare_scoring.py \\
        --output-dir outputs/grid-2026-08-18/scoring

    # Bounds and footprint audit only (skip the per-pass dedup work)
    python scripts/grid_prepare_scoring.py --bounds-only

Inputs:
    - outputs/grid-2026-08-18/<cell>/run_{1..10}/detections-*.geojson
    - outputs/grid-2026-08-18/<cell>/run_<N>_recovery/detections-*.geojson
    - inputs/grid-2026-08-18/grid_<cell>_manifest.json
    - inputs/tiles{,_384,_384_ov192,_512_ov256}/<map>/metadata.json
    - inputs/vectors/bounds/384/full_evaluation_bounds.geojson (era-2-487)
    - inputs/vectors/references/mounds-reference.geojson

Outputs (under ``--output-dir``):
    - bounds/grid_<cell>_bounds.geojson  - native per-cell tile bounds
    - bounds/grid_common_bounds.geojson  - common (four-way intersection) scope
    - common/<cell>/run_N/detections_dedup.geojson
    - native/<cell>/run_N/detections_dedup.geojson
    - prepare_summary.json               - footprint audit + per-pass dedup stats

Created: 2026-08-18 (Session 136)
Author: Shawn Ross, Claude Code
Licence: Apache 2.0
"""

from __future__ import annotations

import argparse
import json
import logging
import re
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

import geopandas as gpd

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.lib_advanced_metrics import (  # noqa: E402
    get_map_name,
    scope_references_to_tiles,
)
from scripts.lib_detection_paths import (  # noqa: E402
    find_pass_geojsons,
    pass_identity,
    run_sort_key,
)
from scripts.merge_passes import (  # noqa: E402
    DISTANCE_THRESHOLD_METRES,
    deduplicate_within_pass,
)
from scripts.prepare_h13_scoring import (  # noqa: E402
    MIN_CLIPPED_TILE_AREA_M2,
    write_dedup_geojson,
)

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

#: Root of the committed grid detections.
GRID_ROOT = PROJECT_ROOT / "outputs/grid-2026-08-18"

#: Pinned manifests, one per cell.
MANIFEST_DIR = PROJECT_ROOT / "inputs/grid-2026-08-18"

#: The era-2-487 evaluation grid. Both the footprint all four manifests were
#: pinned against and the carrier for the common scope; it is also, exactly,
#: the 384 / 12.5 % cell's own tiling (verified in :func:`build_common_bounds`).
ERA2_BOUNDS = PROJECT_ROOT / "inputs/vectors/bounds/384/full_evaluation_bounds.geojson"

#: Gold-standard reference mounds.
GROUND_TRUTH = PROJECT_ROOT / "inputs/vectors/references/mounds-reference.geojson"

#: Passes per cell. Used as the pass-resolution undercount guard.
N_PASSES = 10

#: A pass directory is ``run_<N>`` with a purely numeric suffix; additive
#: ``run_<N>_recovery`` fragments are handled separately by
#: :func:`resolve_cell_passes`.
_NUMERIC_RUN_RE = re.compile(r"^run_(\d+)$")

#: The four cells: label -> geometry, tile tree, and pinned manifest.
CELLS: dict[str, dict[str, Any]] = {
    "g512_ov064": {
        "tile_px": 512, "overlap_px": 64, "overlap_frac": 0.125,
        "tiles_dir": PROJECT_ROOT / "inputs/tiles",
        "manifest": MANIFEST_DIR / "grid_512_ov064_manifest.json",
    },
    "g512_ov256": {
        "tile_px": 512, "overlap_px": 256, "overlap_frac": 0.50,
        "tiles_dir": PROJECT_ROOT / "inputs/tiles_512_ov256",
        "manifest": MANIFEST_DIR / "grid_512_ov256_manifest.json",
    },
    "g384_ov048": {
        "tile_px": 384, "overlap_px": 48, "overlap_frac": 0.125,
        "tiles_dir": PROJECT_ROOT / "inputs/tiles_384",
        "manifest": MANIFEST_DIR / "grid_384_ov048_manifest.json",
    },
    "g384_ov192": {
        "tile_px": 384, "overlap_px": 192, "overlap_frac": 0.50,
        "tiles_dir": PROJECT_ROOT / "inputs/tiles_384_ov192",
        "manifest": MANIFEST_DIR / "grid_384_ov192_manifest.json",
    },
}


class CoverageError(RuntimeError):
    """Raised when a merged pass does not resolve its cell's full manifest.

    This is the E72 guard made explicit at preparation time rather than left
    to the evaluator: a pass short of its manifest silently converts the
    missing tile's ground truth into false negatives.
    """


def resolve_cell_passes(cell: str) -> dict[str, list[Path]]:
    """Resolve one cell's ten passes, merging any additive recovery fragment.

    Two deliberate departures from
    :func:`scripts.lib_detection_paths.resolve_pool_passes`:

    1. **Recovery fragments are merged.** The resolver walks numeric
       ``run_<N>`` directories only and *warns* about ``run_<N>_recovery``.
       This function takes that warning seriously, looking each fragment up
       explicitly and appending it to its parent pass's file list.
    2. **Pass identity is counted per run directory, not pool-wide.** The
       resolver's ``expected_passes`` guard counts ``{pass_identity(p)}``
       across the whole pool, which collapses to 1 whenever every run
       directory holds an identically-named file. That is the *normal* case
       for real-time runs, whose filenames encode config, model and date but
       not the run number — so the guard raises ``PassCountMismatch`` on
       every same-day multi-pass real-time pool, this grid and the committed
       H13 arms B and C included (defect logged for the resolver's owner;
       ``lib_detection_paths.py`` is not touched here). Counting identities
       within each run directory keeps the chunked-Batch-pass protection the
       guard was written for while restoring a correct pool total.

    Args:
        cell: Cell label, a key of :data:`CELLS`.

    Returns:
        Mapping ``run_<N>`` -> ordered detection GeoJSON paths making up that
        pass (main file first, recovery fragment second where one exists).

    Raises:
        CoverageError: If the cell does not resolve exactly :data:`N_PASSES`
            numeric passes, or a run directory holds no or several pass files.
    """
    cell_dir = GRID_ROOT / cell
    run_dirs = sorted(
        (d for d in cell_dir.glob("run_*")
         if d.is_dir() and _NUMERIC_RUN_RE.match(d.name)),
        key=run_sort_key,
    )

    passes: dict[str, list[Path]] = {}
    for run_dir in run_dirs:
        found = find_pass_geojsons(run_dir)
        if not found:
            raise CoverageError(f"{run_dir} holds no per-pass detection GeoJSON.")
        if len({pass_identity(p) for p in found}) != 1:
            raise CoverageError(
                f"{run_dir} holds {len(found)} distinct pass identities "
                f"({', '.join(p.name for p in found)}); refusing to guess."
            )
        passes[run_dir.name] = sorted(found, key=lambda p: p.name)

    if len(passes) != N_PASSES:
        raise CoverageError(
            f"{cell_dir} resolved {len(passes)} pass(es), expected {N_PASSES}."
        )

    for recovery_dir in sorted(cell_dir.glob("run_*_recovery")):
        parent = recovery_dir.name.removesuffix("_recovery")
        found = find_pass_geojsons(recovery_dir)
        if not found:
            raise CoverageError(
                f"{recovery_dir} holds no pass-shaped detection GeoJSON; the "
                f"recovery fragment cannot be merged into {parent}."
            )
        if parent not in passes:
            raise CoverageError(
                f"{recovery_dir} has no parent pass {parent} in {cell_dir}."
            )
        passes[parent].extend(found)
        logger.info("%s %s: merging recovery fragment %s",
                    cell, parent, found[0].parent.name)

    return dict(sorted(passes.items(), key=lambda kv: int(kv[0].split("_")[1])))


def load_pass(paths: list[Path]) -> tuple[list[dict], set[str]]:
    """Load and concatenate one logical pass from one or more GeoJSON files.

    Mirrors :func:`scripts.prepare_h13_scoring.load_pass`. Concatenating a
    main file with its additive recovery fragment reconstructs the complete
    pass without mutating either committed artefact.

    Args:
        paths: Detection GeoJSON paths making up the pass, in merge order.

    Returns:
        Tuple of (features, processed_tiles), where ``processed_tiles`` is the
        union of the files' top-level coverage records.

    Raises:
        FileNotFoundError: If any path does not exist.
    """
    features: list[dict] = []
    processed: set[str] = set()
    for path in paths:
        if not path.exists():
            raise FileNotFoundError(f"Detection GeoJSON missing: {path}")
        data = json.loads(path.read_text())
        features.extend(data.get("features", []))
        processed.update(data.get("processed_tiles") or [])
    return features, processed


def build_native_bounds(output_dir: Path) -> dict[str, Path]:
    """Materialise each cell's own tile-bounds GeoJSON from its pinned manifest.

    Geometry is generated by ``scripts/generate_tile_bounds.py`` so it comes
    from the same code path the evaluator's committed bounds do; a second
    implementation here would be a silent divergence risk.

    Args:
        output_dir: Root output directory; bounds land in ``output_dir/bounds``.

    Returns:
        Mapping of cell label to the written bounds path.

    Raises:
        RuntimeError: If a bounds generation subprocess fails.
    """
    bounds_dir = output_dir / "bounds"
    bounds_dir.mkdir(parents=True, exist_ok=True)
    written: dict[str, Path] = {}

    for cell, spec in CELLS.items():
        target = bounds_dir / f"grid_{cell}_bounds.geojson"
        with tempfile.TemporaryDirectory() as tmp:
            cmd = [
                sys.executable, str(PROJECT_ROOT / "scripts/generate_tile_bounds.py"),
                "--manifest", str(spec["manifest"]),
                "--name", f"grid_{cell}",
                "--tiles-dir", str(spec["tiles_dir"]),
                "--tile-size", str(spec["tile_px"]),
                "--output-dir", tmp,
            ]
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode != 0:
                raise RuntimeError(
                    f"generate_tile_bounds.py failed for {cell}:\n{result.stderr}"
                )
            target.write_text((Path(tmp) / f"grid_{cell}_bounds.geojson").read_text())

        n_tiles = len(json.loads(target.read_text())["features"])
        n_manifest = len(json.loads(spec["manifest"].read_text()))
        if n_tiles != n_manifest:
            raise CoverageError(
                f"{cell}: bounds hold {n_tiles} tiles but the pinned manifest "
                f"lists {n_manifest}."
            )
        logger.info("%s native bounds: %d tiles -> %s", cell, n_tiles, target.name)
        written[cell] = target

    return written


def count_ground_truth(grid: gpd.GeoDataFrame, gdf_ref: gpd.GeoDataFrame) -> int:
    """Count reference mounds falling inside a tile grid, map sheet by map sheet.

    Reproduces the evaluator's scoping rule
    (:func:`scripts.lib_advanced_metrics.scope_references_to_tiles` applied per
    map), which is what sets the recall denominator.

    Args:
        grid: Tile bounds with a ``tile_name`` column.
        gdf_ref: Gold-standard references with a ``Map`` column.

    Returns:
        Number of in-scope reference mounds.
    """
    total = 0
    for map_name in sorted({get_map_name(n) for n in grid["tile_name"]}):
        map_bounds = grid[grid["tile_name"].str.startswith(map_name)]
        refs = gdf_ref[gdf_ref["Map"] == map_name]
        if not refs.empty:
            total += len(scope_references_to_tiles(refs, map_bounds))
    return total


def build_common_bounds(
    native: dict[str, Path], output_dir: Path, gdf_ref: gpd.GeoDataFrame,
) -> tuple[Path, Any, dict[str, Any]]:
    """Build the common scope and audit how far the four native footprints diverge.

    The carrier is the era-2-487 grid clipped to the four-way intersection of
    the cells' tile unions. era-2-487 is the right carrier for three reasons:
    it is the footprint all four manifests were pinned against, it is the
    grid the study's 384 px body of work already uses, and it is exactly the
    384 / 12.5 % cell's own tiling — asserted here rather than assumed.

    Args:
        native: Mapping of cell label to native bounds path.
        output_dir: Root output directory.
        gdf_ref: Gold-standard references, for the in-scope counts.

    Returns:
        Tuple of (common bounds path, common footprint geometry, audit dict).

    Raises:
        CoverageError: If the 384 / 12.5 % union is not identical to era-2-487,
            or if the intersection is not contained in the carrier's union.
    """
    unions = {cell: gpd.read_file(path).geometry.union_all()
              for cell, path in native.items()}

    era2 = gpd.read_file(ERA2_BOUNDS)
    u_era2 = era2.geometry.union_all()

    # The commit message for the grid claims the 384 / 12.5 % cell reproduces
    # era-2-487 exactly. Verify it: everything downstream leans on the carrier
    # covering the intersection.
    sym_diff_m2 = unions["g384_ov048"].symmetric_difference(u_era2).area
    if sym_diff_m2 > MIN_CLIPPED_TILE_AREA_M2:
        raise CoverageError(
            f"g384_ov048's tile union differs from era-2-487 by "
            f"{sym_diff_m2:.3f} m²; the carrier assumption does not hold."
        )

    common = u_era2
    for union in unions.values():
        common = common.intersection(union)

    grid = era2.copy()
    grid["geometry"] = grid.geometry.intersection(common)
    grid = grid[grid.geometry.notna() & ~grid.geometry.is_empty].copy()
    grid = grid[grid.geometry.area > MIN_CLIPPED_TILE_AREA_M2].copy()

    carrier_union_area = grid.geometry.union_all().area
    if abs(carrier_union_area - common.area) > 1.0:
        raise CoverageError(
            f"Clipped carrier covers {carrier_union_area / 1e6:.4f} km² but the "
            f"intersection is {common.area / 1e6:.4f} km²."
        )

    target = output_dir / "bounds" / "grid_common_bounds.geojson"
    grid.to_file(target, driver="GeoJSON")

    audit = {
        "carrier": "era-2-487 grid clipped to the four-way tile-union intersection",
        "carrier_tiles": int(len(grid)),
        "common_km2": common.area / 1e6,
        "common_ground_truth": count_ground_truth(grid, gdf_ref),
        "era2_487": {
            "tiles": int(len(era2)),
            "union_km2": u_era2.area / 1e6,
            "ground_truth": count_ground_truth(era2, gdf_ref),
        },
        "g384_ov048_equals_era2_487": True,
        "g384_ov048_symmetric_difference_m2": float(sym_diff_m2),
        "native": {},
    }
    for cell, path in native.items():
        cell_grid = gpd.read_file(path)
        area = unions[cell].area
        audit["native"][cell] = {
            "tiles": int(len(cell_grid)),
            "union_km2": area / 1e6,
            "ground_truth": count_ground_truth(cell_grid, gdf_ref),
            "outside_common_km2": (area - common.area) / 1e6,
            "outside_common_frac": (area - common.area) / area,
        }
        logger.info(
            "%s native: %d tiles, %.2f km², %d mounds; %.2f km² (%.2f %%) "
            "outside the common scope",
            cell, len(cell_grid), area / 1e6,
            audit["native"][cell]["ground_truth"],
            audit["native"][cell]["outside_common_km2"],
            100 * audit["native"][cell]["outside_common_frac"],
        )
    logger.info(
        "common scope: %.2f km², %d carrier tiles, %d mounds",
        audit["common_km2"], audit["carrier_tiles"], audit["common_ground_truth"],
    )
    return target, common, audit


def main() -> int:
    """Run the preparation stage and write the audit + dedup summary.

    Returns:
        Process exit status (0 on success).
    """
    parser = argparse.ArgumentParser(
        description="Prepare the tile-size x overlap grid for uniform scoring.",
    )
    parser.add_argument(
        "--output-dir", type=Path,
        default=GRID_ROOT / "scoring",
        help="Root output directory (default: outputs/grid-2026-08-18/scoring)",
    )
    parser.add_argument(
        "--bounds-only", action="store_true",
        help="Generate bounds and the footprint audit only; skip deduplication.",
    )
    parser.add_argument(
        "--dedup-metres", type=float, default=DISTANCE_THRESHOLD_METRES,
        help=f"Within-pass dedup radius (default: {DISTANCE_THRESHOLD_METRES} m)",
    )
    args = parser.parse_args()

    out: Path = args.output_dir
    out.mkdir(parents=True, exist_ok=True)

    gdf_ref = gpd.read_file(GROUND_TRUTH)
    native_paths = build_native_bounds(out)
    common_path, common_geom, audit = build_common_bounds(native_paths, out, gdf_ref)

    summary: dict[str, Any] = {
        "dedup_metres": args.dedup_metres,
        "n_passes_per_cell": N_PASSES,
        "footprint_audit": audit,
        "passes": [],
    }

    if args.bounds_only:
        (out / "prepare_summary.json").write_text(json.dumps(summary, indent=2))
        logger.info("Bounds only — stopping before deduplication.")
        return 0

    native_gdfs = {cell: gpd.read_file(p) for cell, p in native_paths.items()}
    common_gdf = gpd.read_file(common_path)
    common_tiles = sorted(common_gdf["tile_name"].tolist())

    for cell, spec in CELLS.items():
        manifest = set(json.loads(spec["manifest"].read_text()))
        for run, paths in resolve_cell_passes(cell).items():
            raw, processed = load_pass(paths)

            # E72 made explicit: a pass short of its manifest would turn the
            # missing tile's ground truth into artificial false negatives.
            missing = manifest - processed
            extra = processed - manifest
            if missing or extra:
                raise CoverageError(
                    f"{cell}/{run}: coverage does not match the pinned manifest "
                    f"({len(processed)} tiles processed, {len(manifest)} pinned; "
                    f"{len(missing)} missing, {len(extra)} unexpected). "
                    f"Missing: {sorted(missing)[:5]}"
                )

            deduped = deduplicate_within_pass(raw, distance_thresh=args.dedup_metres)

            native_stats = write_dedup_geojson(
                deduped, native_gdfs[cell], sorted(processed),
                out / "native" / cell / run / "detections_dedup.geojson",
                clip_geom=None,
            )
            # Every cell's tiling fully covers the intersection by construction,
            # so in the common scope the coverage record is the carrier grid.
            common_stats = write_dedup_geojson(
                deduped, common_gdf, common_tiles,
                out / "common" / cell / run / "detections_dedup.geojson",
                clip_geom=common_geom,
            )

            summary["passes"].append({
                "cell": cell,
                "run": run,
                "tile_px": spec["tile_px"],
                "overlap_frac": spec["overlap_frac"],
                "files": [str(p.relative_to(PROJECT_ROOT)) for p in paths],
                "recovery_merged": len(paths) > 1,
                "tiles_processed": len(processed),
                "n_raw": len(raw),
                "n_dedup": len(deduped),
                "n_removed": len(raw) - len(deduped),
                "removed_frac": (len(raw) - len(deduped)) / len(raw) if raw else 0.0,
                "native": native_stats,
                "common": common_stats,
            })
            logger.info(
                "%s %s: tiles %d, raw %d -> dedup %d (-%.1f %%); common %d "
                "(clipped %d, unassigned %d)",
                cell, run, len(processed), len(raw), len(deduped),
                100 * (len(raw) - len(deduped)) / len(raw) if raw else 0.0,
                common_stats["n_out"], common_stats["n_clipped"],
                common_stats["n_unassigned"],
            )

    (out / "prepare_summary.json").write_text(json.dumps(summary, indent=2))
    logger.info("Wrote %s", out / "prepare_summary.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
