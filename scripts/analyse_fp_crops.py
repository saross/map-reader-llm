#!/usr/bin/env python3
"""
Analyse False Positives/Negatives and Extract Crops for Hard Example Library
=============================================================================

Clusters False Positive (FP) / False Negative (FN) detections from multiple runs
using distance-based matching (20 m) aligned with the F1-score evaluation spatial
tolerance, then extracts image crops for the most recurrent errors to build a hard
example library.

Usage:
    python scripts/analyse_fp_crops.py \\
        --input outputs/results/v4.2_temp_0_7_train/run_01_fn.geojson \\
        --output_dir outputs/hard-examples \\
        --mode fn \\
        --manifest inputs/tiles/calibration_manifest.json

Author: Shawn Ross, Claude Code
Licence: Apache 2.0
"""

import argparse
import json
import math
import sys
from pathlib import Path

import geopandas as gpd
from PIL import Image
from shapely.geometry import box

# Add project root to path for config import
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import config  # noqa: E402 -- must follow sys.path modification

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
DISTANCE_THRESHOLD_METRES = 20.0  # Aligns with F1-score evaluation spatial tolerance
DEFAULT_CROP_LIMIT = 10  # Maximum number of hard examples to extract
CROP_MARGIN_PX = 60  # Pixel margin around detection for context


# ---------------------------------------------------------------------------
# Geometry helpers
# ---------------------------------------------------------------------------


def get_centroid(geom_bounds: tuple[float, ...]) -> tuple[float, float]:
    """Return centroid (x, y) from geometry bounds [minx, miny, maxx, maxy]."""
    minx, miny, maxx, maxy = geom_bounds
    return ((minx + maxx) / 2, (miny + maxy) / 2)


def centroid_distance(bounds_a: tuple[float, ...], bounds_b: tuple[float, ...]) -> float:
    """
    Calculate Euclidean distance between centroids of two bounding boxes.

    Returns distance in coordinate units (metres for EPSG:32635).
    """
    cx_a, cy_a = get_centroid(bounds_a)
    cx_b, cy_b = get_centroid(bounds_b)
    return math.sqrt((cx_a - cx_b) ** 2 + (cy_a - cy_b) ** 2)


def geo_to_pixel(
    geo_bounds: tuple[float, ...],
    tile_bounds: tuple[float, ...],
    img_size: tuple[int, int],
) -> list[float]:
    """
    Convert geographic bounds to pixel coordinates.

    Args:
        geo_bounds: Geographic bounds [minx, miny, maxx, maxy].
        tile_bounds: Tile geographic bounds [minx, miny, maxx, maxy].
        img_size: Image dimensions (width, height).

    Returns:
        Pixel bounds [px_minx, px_miny, px_maxx, px_maxy].

    Raises:
        ValueError: If tile bounds have zero width or height.
    """
    g_minx, g_miny, g_maxx, g_maxy = geo_bounds
    t_minx, t_miny, t_maxx, t_maxy = tile_bounds
    w, h = img_size

    # Guard against degenerate tile bounds
    tile_width = t_maxx - t_minx
    tile_height = t_maxy - t_miny
    if tile_width == 0 or tile_height == 0:
        raise ValueError(
            f"Degenerate tile bounds: width={tile_width}, height={tile_height}"
        )

    scale_x = w / tile_width
    scale_y = h / tile_height
    px_minx = (g_minx - t_minx) * scale_x
    px_maxx = (g_maxx - t_minx) * scale_x
    px_miny = (t_maxy - g_maxy) * scale_y
    px_maxy = (t_maxy - g_miny) * scale_y
    return [px_minx, px_miny, px_maxx, px_maxy]


# ---------------------------------------------------------------------------
# Tile-bounds loading
# ---------------------------------------------------------------------------


def load_tile_bounds(
    results_dir: Path, run_id: str
) -> dict[str, tuple[float, ...]] | None:
    """
    Load tile geographic bounds from a GeoJSON bounds file.

    Tries the run-specific bounds file first, then falls back to any bounds
    file in the same directory.

    Args:
        results_dir: Directory containing result files.
        run_id: Run identifier used to locate the bounds file.

    Returns:
        Mapping of tile name to geographic bounds, or ``None`` if no bounds
        file could be loaded.
    """
    bounds_file = results_dir / f"{run_id}_bounds.geojson"

    print(f"Loading bounds from {bounds_file}...")
    if not bounds_file.exists():
        print(f"Bounds file not found: {bounds_file}")
        # Fall back to any bounds file in the directory
        bounds_file = next(results_dir.glob("*_bounds.geojson"), None)
        if not bounds_file:
            print("No bounds file found. Cannot proceed.")
            return None

    tile_bounds_map: dict[str, tuple[float, ...]] = {}
    try:
        bounds_gdf = gpd.read_file(bounds_file)
        for _, row in bounds_gdf.iterrows():
            tile_bounds_map[row["tile_name"]] = row.geometry.bounds
        print(
            f"Loaded {len(tile_bounds_map)} tiles from bounds: "
            f"{list(tile_bounds_map.keys())[:5]}"
        )
    except Exception as exc:
        print(f"Error loading bounds: {exc}")
        return None

    return tile_bounds_map


# ---------------------------------------------------------------------------
# Manifest lookup builder
# ---------------------------------------------------------------------------


def build_tile_lookup(manifest_path: Path, tiles_dir: Path) -> dict[str, Path]:
    """
    Build a mapping from tile stem to filesystem path using a manifest file.

    The manifest lists filenames such as ``K-35-052-4_32635_x1344_y2240.png``.
    Files are stored in subdirectories: ``tiles_dir/{map_name}/{tile_name}.png``.

    Args:
        manifest_path: Path to the JSON manifest file.
        tiles_dir: Root directory containing tile images.

    Returns:
        Mapping of tile stem (no extension) to resolved ``Path``.
    """
    with open(manifest_path) as fh:
        manifest = json.load(fh)

    tile_lookup: dict[str, Path] = {}
    for tile_filename in manifest:
        tile_stem = Path(tile_filename).stem
        # Extract map name: everything before ``_x{N}_y{N}``
        # e.g. "K-35-052-4_32635_x1344_y2240" -> "K-35-052-4_32635"
        parts = tile_stem.rsplit("_x", 1)
        if len(parts) != 2:
            continue
        map_name = parts[0]
        tile_path = tiles_dir / map_name / tile_filename
        if tile_path.exists():
            tile_lookup[tile_stem] = tile_path
        else:
            # Try alternative locations via recursive search
            found = list(tiles_dir.rglob(tile_filename))
            if found:
                tile_lookup[tile_stem] = found[0]

    print(f"Built tile lookup with {len(tile_lookup)} entries from manifest")
    return tile_lookup


# ---------------------------------------------------------------------------
# Tile-path resolution
# ---------------------------------------------------------------------------


def resolve_tile_path(tile_stem: str, tile_lookup: dict[str, Path], tiles_dir: Path) -> Path | None:
    """
    Resolve the filesystem path for a tile image.

    Uses the manifest lookup first, then falls back to recursive search and
    path construction from the tile-name pattern.

    Args:
        tile_stem: Tile name without extension.
        tile_lookup: Pre-built manifest lookup mapping.
        tiles_dir: Root directory containing tile images.

    Returns:
        Resolved ``Path`` to the tile image, or ``None`` if not found.
    """
    # 1. Manifest lookup
    tile_path = tile_lookup.get(tile_stem)
    if tile_path:
        return tile_path

    # 2. Fallback: recursive search by exact filename
    tile_path = next(tiles_dir.rglob(f"{tile_stem}.png"), None)
    if tile_path:
        return tile_path

    # 3. Construct path from tile-name pattern: {map_name}_x{N}_y{N}
    parts = tile_stem.rsplit("_x", 1)
    if len(parts) == 2:
        map_name = parts[0]
        candidate = tiles_dir / map_name / f"{tile_stem}.png"
        if candidate.exists():
            return candidate

    return None


# ---------------------------------------------------------------------------
# Bounds / image resolution for a single detection
# ---------------------------------------------------------------------------


def resolve_bounds_and_image(
    tile_stem: str,
    tile_path: Path,
    geo_bounds: tuple[float, ...],
    tile_bounds_map: dict[str, tuple[float, ...]],
    tiles_dir: Path,
) -> tuple[tuple[float, ...] | None, Path | None]:
    """
    Resolve geographic bounds and image path for a detection's tile.

    Tries exact name match (with and without ``.png``), then falls back to
    spatial containment search across all known tile bounds.

    Args:
        tile_stem: Tile name without extension.
        tile_path: Default tile image path.
        geo_bounds: Geographic bounds of the detection.
        tile_bounds_map: Mapping of tile name to geographic bounds.
        tiles_dir: Root directory containing tile images.

    Returns:
        Tuple of (tile_bounds, image_path), either of which may be ``None``.
    """
    # Exact match (with and without .png extension)
    if tile_stem in tile_bounds_map:
        return tile_bounds_map[tile_stem], tile_path
    tile_stem_png = f"{tile_stem}.png"
    if tile_stem_png in tile_bounds_map:
        return tile_bounds_map[tile_stem_png], tile_path

    # Spatial containment: find the sub-tile whose bounds contain the detection centre
    det_centre = box(*geo_bounds).centroid
    for bounds_name, bounds_coords in tile_bounds_map.items():
        bounds_box = box(*bounds_coords)
        if not bounds_box.contains(det_centre):
            continue

        # Found the containing sub-tile -- locate its image file
        possible_path = next(tiles_dir.rglob(bounds_name), None)
        if not possible_path:
            possible_path = next(tiles_dir.rglob(f"{bounds_name}.png"), None)
        if possible_path:
            print(f"Resolved {tile_stem} -> {bounds_name}")
            return bounds_coords, possible_path

    return None, None


# ---------------------------------------------------------------------------
# Detection loading and clustering
# ---------------------------------------------------------------------------


def load_detections(
    results_dir: Path, mode_suffix: str
) -> list[dict[str, object]]:
    """
    Load all FP or FN detection entries from GeoJSON files in *results_dir*.

    Args:
        results_dir: Directory containing GeoJSON result files.
        mode_suffix: File suffix to match (e.g. ``_fn.geojson``).

    Returns:
        List of detection dicts with ``geo_bounds``, ``source_tile``, and ``run_id``.
    """
    files = list(results_dir.glob(f"*{mode_suffix}"))
    print(f"Found {len(files)} {mode_suffix.replace('.geojson', '').strip('_').upper()} files.")

    all_detections: list[dict[str, object]] = []
    stem_suffix = mode_suffix.replace(".geojson", "")

    for filepath in files:
        run_id = filepath.stem.replace(stem_suffix, "")
        try:
            gdf = gpd.read_file(filepath)
            for _, row in gdf.iterrows():
                all_detections.append({
                    "geo_bounds": row.geometry.bounds,
                    "source_tile": row.get("source_tile") or row.get("Map", ""),
                    "run_id": run_id,
                })
        except Exception as exc:
            print(f"Skipping {filepath}: {exc}")

    print(f"Total entries loaded: {len(all_detections)}")
    return all_detections


def cluster_detections(
    detections: list[dict[str, object]],
) -> list[dict[str, object]]:
    """
    Cluster detections by spatial proximity using single-linkage distance matching.

    Detections on different source tiles are never clustered together. The distance
    threshold is ``DISTANCE_THRESHOLD_METRES`` (20 m), aligned with the F1-score
    evaluation spatial tolerance.

    Args:
        detections: List of detection dicts (from :func:`load_detections`).

    Returns:
        Cluster statistics sorted by descending recurrence count. Each entry
        has ``count`` (unique runs), ``tile``, and ``geo_bounds``.
    """
    clusters: list[list[dict[str, object]]] = []
    used_indices: set[int] = set()

    for i, det in enumerate(detections):
        if i in used_indices:
            continue
        current_cluster = [det]
        used_indices.add(i)
        for j, candidate in enumerate(detections):
            if j in used_indices:
                continue
            if candidate["source_tile"] != det["source_tile"]:
                continue
            dist = centroid_distance(det["geo_bounds"], candidate["geo_bounds"])
            if dist <= DISTANCE_THRESHOLD_METRES:
                current_cluster.append(candidate)
                used_indices.add(j)
        clusters.append(current_cluster)

    print(f"Unique clusters: {len(clusters)}")

    # Build per-cluster statistics and sort by recurrence (descending)
    cluster_stats = []
    for cluster in clusters:
        unique_runs = len({c["run_id"] for c in cluster})
        cluster_stats.append({
            "count": unique_runs,
            "tile": cluster[0]["source_tile"],
            "geo_bounds": cluster[0]["geo_bounds"],
        })

    return sorted(cluster_stats, key=lambda x: x["count"], reverse=True)


# ---------------------------------------------------------------------------
# Main extraction workflow
# ---------------------------------------------------------------------------


def extract_crops(args: argparse.Namespace) -> None:
    """
    End-to-end pipeline: load detections, cluster, and extract hard-example crops.

    Reads FP/FN GeoJSON files from the directory containing the ``--input`` file,
    clusters spatially proximate detections, and saves image crops for the most
    recurrent error locations.

    Args:
        args: Parsed command-line arguments with ``input``, ``output_dir``,
              ``mode``, and ``manifest``.
    """
    input_file = Path(args.input)
    results_dir = input_file.parent
    mode_suffix = "_fn.geojson" if args.mode == "fn" else "_fp.geojson"

    print(f"--- Analysing {args.mode.upper()}s ---")

    # 1. Load tile geographic bounds
    run_id = input_file.stem.replace("_fn", "").replace("_fp", "")
    tile_bounds_map = load_tile_bounds(results_dir, run_id)
    if tile_bounds_map is None:
        return

    # 2. Load and cluster detections
    all_detections = load_detections(results_dir, mode_suffix)
    sorted_clusters = cluster_detections(all_detections)

    # 3. Prepare manifest-based tile lookup
    manifest_path = Path(args.manifest)
    if not manifest_path.exists():
        print(f"Manifest not found: {manifest_path}")
        return

    tiles_dir = config.TILES_DIR
    tile_lookup = build_tile_lookup(manifest_path, tiles_dir)

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # 4. Extract top N hard-example crops
    extracted_count = 0

    for i, item in enumerate(sorted_clusters):
        if extracted_count >= DEFAULT_CROP_LIMIT:
            break

        rank = i + 1
        tile_name = item["tile"]
        print(f"Processing Rank {rank}: {tile_name} (Count: {item['count']})")

        # Normalise tile name (remove .png extension for lookup)
        tile_stem = tile_name.replace(".png", "")

        tile_path = resolve_tile_path(tile_stem, tile_lookup, tiles_dir)
        if not tile_path:
            print(f"Tile image not found for {tile_name}")
            continue

        try:
            t_bounds, img_path_resolved = resolve_bounds_and_image(
                tile_stem, tile_path, item["geo_bounds"],
                tile_bounds_map, tiles_dir,
            )
            if not t_bounds or not img_path_resolved:
                print(f"Could not resolve bounds/image for {tile_name}")
                continue

            # Open the resolved sub-tile image and extract the crop
            with Image.open(img_path_resolved) as img:
                px_bounds = geo_to_pixel(item["geo_bounds"], t_bounds, img.size)
                p_minx, p_miny, p_maxx, p_maxy = px_bounds

                # Expand crop area with context margin, clamped to image bounds
                crop_box = (
                    max(0, int(p_minx) - CROP_MARGIN_PX),
                    max(0, int(p_miny) - CROP_MARGIN_PX),
                    min(img.width, int(p_maxx) + CROP_MARGIN_PX),
                    min(img.height, int(p_maxy) + CROP_MARGIN_PX),
                )
                crop = img.crop(crop_box)

                # FN -> hard_positive (mound the model missed)
                # FP -> hard_negative (non-mound the model flagged)
                type_prefix = "hard_positive" if args.mode == "fn" else "hard_negative"
                out_name = f"{type_prefix}_{rank}_{tile_stem}.png"
                crop.save(output_dir / out_name)
                print(f"Saved {out_name}")
                extracted_count += 1

        except Exception as exc:
            print(f"Error cropping: {exc}")


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Analyse FP/FN detections and extract hard-example crops."
    )
    parser.add_argument(
        "--input", required=True,
        help="Path to one input GeoJSON file (used to locate the results directory)",
    )
    parser.add_argument(
        "--output_dir", required=True,
        help="Directory in which to save extracted crop images",
    )
    parser.add_argument(
        "--mode", choices=["fp", "fn"], required=True,
        help="Error type to analyse: 'fp' (false positives) or 'fn' (false negatives)",
    )
    parser.add_argument(
        "--manifest", required=True,
        help="Path to the tile manifest JSON file",
    )
    args = parser.parse_args()

    extract_crops(args)
