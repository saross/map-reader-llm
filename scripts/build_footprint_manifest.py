#!/usr/bin/env python3
"""
Build a footprint-majority tile manifest for an overlap-arm tile tree.

An overlap arm re-tiles the same ground at a shorter stride, so its raw tile
tree includes tiles that hang off the edge of the study footprint. The H13
arms resolved this with a **footprint-majority** rule: a tile is included when
**more than half** its area falls inside the Era-1 evaluation footprint (the
union of the committed 340-tile 512 px evaluation bounds).

That rule was applied ad hoc when the H13 arm B and arm C manifests were built,
so it existed only in those two committed JSON files and had to be
reverse-engineered before it could be reused. This script makes it
reproducible, and ``--verify`` re-derives both committed manifests as a
regression gate so the rule cannot drift silently.

**The exactly-one-half boundary is decided by floating-point luck**, and the
two committed manifests fall on opposite sides of it. Arm C excludes
``K-35-053-3_Elenovo_x2048_y2048.png``, whose fraction computes to exactly
0.5; arm B includes ``K-35-078-1_Lesovo_x3456_y3072.png``, whose fraction
computes to 0.4999999999998276 here — about 1.7e-13 below a true half, so the
ad hoc build's arithmetic evidently landed a hair above it. The underlying
rule is the same in both; only the tie-break differs. This script resolves the
tie DETERMINISTICALLY by excluding exactly-half tiles (matching arm C, and the
strict reading of "majority"), and ``--verify`` records arm B's single
boundary tile as a known, named exception rather than silently tolerating a
mismatch. The practical impact is one tile in 440.

Usage::

    # Verify the rule against the committed H13 manifests (no writes)
    python scripts/build_footprint_manifest.py --verify

    # Build a manifest for a new tile tree
    python scripts/build_footprint_manifest.py \\
        --tiles-dir inputs/tiles_384_ov192 --tile-size 384 \\
        --output inputs/tiles_384_ov192/grid_384_ov192_manifest.json

Inputs:
    - A tile tree of ``<tiles-dir>/<map_name>/*.png`` with per-map metadata
    - The footprint: ``inputs/vectors/bounds/full_evaluation_bounds.geojson``

Outputs:
    - A JSON array of tile filenames, sorted, ready for ``--manifest`` use

Created: 2026-08-18 (Session 136)
Author: Shawn Ross, Claude Code
Licence: Apache 2.0
"""

from __future__ import annotations

import argparse
import json
import logging
import subprocess
import sys
import tempfile
from pathlib import Path

import geopandas as gpd

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

#: Default footprint: the Era-1 512 px evaluation set, which is what the H13
#: arm manifests were built against and what --verify reproduces.
FOOTPRINT = PROJECT_ROOT / "inputs/vectors/bounds/full_evaluation_bounds.geojson"

#: The Era-2 384 px evaluation set. Preferred for new multi-geometry grids:
#: it is a strict subset of Era-1 and has zero area overlap with the
#: calibration footprint, whereas Era-1 shares the usual overlap bands with
#: it. Both exclude calibration tiles at the tile level; Era-2 additionally
#: buffers the calibration ground out entirely.
FOOTPRINT_ERA2 = PROJECT_ROOT / "inputs/vectors/bounds/384/full_evaluation_bounds.geojson"

#: Fraction of a tile's area that must fall inside the footprint. The
#: comparison is STRICT (>), so an exactly-half tile is excluded.
MAJORITY_FRACTION = 0.5

#: Tiles within this distance of the half boundary are reported by --verify,
#: because their inclusion is not numerically stable across implementations.
BOUNDARY_EPSILON = 1e-9

#: Known boundary tile whose committed arm-B membership disagrees with the
#: strict rule by ~1.7e-13 of area fraction. Named so the gate stays honest:
#: this is a documented floating-point tie, not an unexplained mismatch.
KNOWN_BOUNDARY_EXCEPTIONS = {
    "inputs/tiles_512_ov128/h13_armB_manifest.json":
        {"K-35-078-1_Lesovo_x3456_y3072.png"},
}

#: Committed manifests the --verify gate must reproduce exactly.
VERIFY_CASES = [
    ("inputs/tiles_512_ov128", 512, "inputs/tiles_512_ov128/h13_armB_manifest.json"),
    ("inputs/tiles_512_ov256", 512, "inputs/tiles_512_ov256/h13_armC_manifest.json"),
]


def tile_bounds_for_tree(tiles_dir: Path, tile_size: int) -> gpd.GeoDataFrame:
    """Generate polygon bounds for every tile in a tree.

    Delegates to ``scripts/generate_tile_bounds.py`` so the geometry comes
    from the same code path the evaluator's bounds do — a second
    implementation here would be a silent divergence risk.

    Args:
        tiles_dir: Tile tree root containing ``<map_name>/*.png``.
        tile_size: Tile edge in pixels, for the extent calculation.

    Returns:
        GeoDataFrame of tile polygons with a ``tile_name`` column.

    Raises:
        RuntimeError: If bounds generation fails.
    """
    tiles = sorted(tiles_dir.glob("*/*.png"))
    if not tiles:
        raise RuntimeError(f"No tiles found under {tiles_dir}")

    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        manifest = tmp_path / "all.json"
        manifest.write_text(json.dumps([p.name for p in tiles]))
        result = subprocess.run(
            [sys.executable, str(PROJECT_ROOT / "scripts/generate_tile_bounds.py"),
             "--manifest", str(manifest), "--name", "all",
             "--tiles-dir", str(tiles_dir), "--tile-size", str(tile_size),
             "--output-dir", str(tmp_path)],
            capture_output=True, text=True,
        )
        if result.returncode != 0:
            raise RuntimeError(
                f"generate_tile_bounds.py failed for {tiles_dir}:\n{result.stderr}")
        return gpd.read_file(tmp_path / "all_bounds.geojson")


def select_majority_tiles(
    tiles_dir: Path, tile_size: int, footprint_path: Path | None = None,
) -> tuple[list[str], int]:
    """Select the tiles whose area lies mostly inside the study footprint.

    Args:
        tiles_dir: Tile tree root.
        tile_size: Tile edge in pixels.
        footprint_path: Footprint to select against; defaults to Era-1.

    Returns:
        Tuple of (sorted tile filenames, total tiles in the tree).
    """
    footprint = gpd.read_file(footprint_path or FOOTPRINT).geometry.union_all()
    bounds = tile_bounds_for_tree(tiles_dir, tile_size)
    frac = bounds.geometry.intersection(footprint).area / bounds.geometry.area
    keep = frac > MAJORITY_FRACTION
    borderline = bounds.loc[
        (frac - MAJORITY_FRACTION).abs() < BOUNDARY_EPSILON, "tile_name"].tolist()
    for name in borderline:
        logger.warning(
            "tile %s sits within %g of the half boundary — its inclusion is not "
            "numerically stable; excluded under the strict rule", name, BOUNDARY_EPSILON)
    return sorted(bounds.loc[keep, "tile_name"].tolist()), len(bounds)


def verify() -> int:
    """Re-derive the committed H13 manifests as a regression gate.

    Returns:
        0 when both reproduce exactly, else 1.
    """
    failures = 0
    for tdir, px, mpath in VERIFY_CASES:
        tiles_dir = PROJECT_ROOT / tdir
        committed_path = PROJECT_ROOT / mpath
        if not tiles_dir.exists():
            logger.warning("SKIP %s — tile tree absent on this machine "
                           "(regenerable; see the H13 plan)", tdir)
            continue
        selected, total = select_majority_tiles(tiles_dir, px)
        committed = sorted(json.loads(committed_path.read_text()))
        allowed = KNOWN_BOUNDARY_EXCEPTIONS.get(mpath, set())
        only_derived = sorted(set(selected) - set(committed))
        only_committed = sorted(set(committed) - set(selected))
        unexplained = (set(only_derived) | set(only_committed)) - allowed
        ok = not unexplained
        failures += 0 if ok else 1
        detail = "exact match" if selected == committed else (
            f"differs by {len(only_derived) + len(only_committed)} tile(s), "
            "all documented boundary ties" if ok else "UNEXPLAINED MISMATCH")
        logger.info(
            "%s %s: derived %d of %d, committed %d — %s",
            "PASS" if ok else "FAIL", Path(mpath).name,
            len(selected), total, len(committed), detail,
        )
        if only_committed:
            logger.info("  committed-only (boundary tie): %s", only_committed)
        if only_derived:
            logger.info("  derived-only: %s", only_derived)
        if unexplained:
            logger.error("  unexplained: %s", sorted(unexplained)[:5])
    return 1 if failures else 0


def main() -> int:
    """Build a manifest, or run the verification gate.

    Returns:
        Process exit status (0 on success).
    """
    parser = argparse.ArgumentParser(
        description="Build a footprint-majority tile manifest.")
    parser.add_argument(
        "--verify", action="store_true",
        help="Re-derive the committed H13 manifests as a regression gate, then exit.")
    parser.add_argument("--tiles-dir", type=Path, help="Tile tree root.")
    parser.add_argument("--tile-size", type=int, help="Tile edge in pixels.")
    parser.add_argument("--output", type=Path, help="Manifest output path.")
    parser.add_argument(
        "--footprint", type=Path, default=None,
        help="Footprint GeoJSON to select against (default: the Era-1 512 px "
             "evaluation bounds; pass the Era-2 384 px bounds for new grids).")
    args = parser.parse_args()

    if args.verify:
        return verify()

    if not (args.tiles_dir and args.tile_size and args.output):
        parser.error("--tiles-dir, --tile-size and --output are required "
                     "unless --verify is given")

    selected, total = select_majority_tiles(
        args.tiles_dir, args.tile_size, args.footprint)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(selected, indent=1) + "\n")
    logger.info("Selected %d of %d tiles (%.1f %% of the tree) -> %s",
                len(selected), total, 100 * len(selected) / total, args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
