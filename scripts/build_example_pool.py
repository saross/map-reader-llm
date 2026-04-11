#!/usr/bin/env python3
"""Automated example pool builder with diversity optimisation.

Selects hard-positive (HP) and hard-negative (HN) examples from the
hard-case register produced by ``discover_hard_cases.py``, optimising
for spatial and map-level diversity. Crops example images from source
rasters for use in VLM prompts.

The pool builder supports configurable HP:HN ratios for the H12
experiment (e.g., 2:6, 4:4, 6:2 at constant total=8).

Usage:
    # Balanced pool (4 HP + 4 HN):
    python scripts/build_example_pool.py \\
        --hard-cases outputs/h10/hard-cases/pool_160/hard_cases_register.json \\
        --hp-count 4 --hn-count 4 \\
        --rasters-dir inputs/rasters \\
        --seed 42 \\
        --output-dir outputs/h10/example-pools/pool_160_hp4hn4/

    # HP-heavy for H12 (6 HP + 2 HN):
    python scripts/build_example_pool.py \\
        --hard-cases outputs/h10/hard-cases/pool_160/hard_cases_register.json \\
        --hp-count 6 --hn-count 2 \\
        --rasters-dir inputs/rasters \\
        --seed 42 \\
        --output-dir outputs/h10/example-pools/pool_160_hp6hn2/

Author: Shawn Ross, Claude Code
Licence: Apache 2.0
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Path setup — allow imports from scripts/
# ---------------------------------------------------------------------------
_SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(_SCRIPT_DIR))

from mine_hard_cases import crop_candidate  # noqa: E402

logger = logging.getLogger(__name__)

# =========================================================================
# Constants
# =========================================================================

_REPO_ROOT = _SCRIPT_DIR.parent
_DEFAULT_RASTERS_DIR = _REPO_ROOT / "inputs" / "rasters"
_DEFAULT_CROP_SIZE = 128

# Diversity penalty parameters
_SPATIAL_PENALTY_RADIUS = 500.0   # metres — penalise nearby candidates
_SPATIAL_PENALTY_FACTOR = 0.5     # reduce score by 50% within radius
_SAME_TILE_PENALTY_FACTOR = 0.2   # reduce score by 80% for same tile


# =========================================================================
# Selection with diversity optimisation
# =========================================================================


def select_diverse_examples(
    candidates: list[dict],
    count: int,
    seed: int,
) -> list[dict]:
    """Select examples from ranked candidates with diversity penalties.

    Uses greedy selection: pick the highest-scoring candidate, then
    penalise nearby candidates before selecting the next. This ensures
    spatial spread and map-level representation.

    Penalty rules:
    - Candidates within 500 m of a selected candidate have their score
      reduced by 50%.
    - Candidates from the same tile have their score reduced by 80%.
    - Penalties stack multiplicatively.

    Args:
        candidates: List of candidate dicts from the hard-case register,
            each with ``x``, ``y``, ``difficulty_score``, ``map_name``,
            and either ``source_tiles`` (for HNs) or ``ref_index``
            (for HPs). Must be pre-sorted by difficulty_score descending.
        count: Number of examples to select.
        seed: Random seed (reserved for tie-breaking; deterministic
            greedy selection doesn't use it currently).

    Returns:
        List of selected candidate dicts (length = min(count, available)).
    """
    if count <= 0 or not candidates:
        return []

    # Work on copies with mutable adjusted scores
    pool = []
    for c in candidates:
        pool.append({
            **c,
            "_adj_score": c["difficulty_score"],
            "_source_tile": _get_source_tile(c),
        })

    selected = []
    for _ in range(min(count, len(pool))):
        # Pick the highest adjusted score
        best_idx = max(range(len(pool)), key=lambda i: pool[i]["_adj_score"])
        chosen = pool.pop(best_idx)
        selected.append(chosen)

        # Apply diversity penalties to remaining candidates
        cx, cy = chosen["x"], chosen["y"]
        chosen_tile = chosen["_source_tile"]

        for p in pool:
            dist = (
                (p["x"] - cx) ** 2 + (p["y"] - cy) ** 2
            ) ** 0.5
            if dist < _SPATIAL_PENALTY_RADIUS:
                p["_adj_score"] *= _SPATIAL_PENALTY_FACTOR
            if p["_source_tile"] == chosen_tile:
                p["_adj_score"] *= _SAME_TILE_PENALTY_FACTOR

    # Strip internal fields before returning
    for s in selected:
        s.pop("_adj_score", None)
        s.pop("_source_tile", None)

    return selected


def _get_source_tile(candidate: dict) -> str:
    """Extract a tile-level identifier from a candidate.

    For HN candidates (from FP register), returns the actual source
    tile name. For HP candidates (from mound register, no source_tiles
    field), synthesises a tile-level ID from map name + grid position
    to avoid over-penalising at map level.
    """
    tiles = candidate.get("source_tiles", [])
    if tiles:
        return tiles[0]
    # Synthesise tile-level ID from coordinates — two candidates on
    # the same ~336m grid cell share an ID; different cells don't.
    # Uses integer division by 336 (384px stride) as grid quantiser.
    x = candidate.get("x", 0)
    y = candidate.get("y", 0)
    map_name = candidate.get("map_name", "unknown")
    gx = int(x) // 336
    gy = int(y) // 336
    return f"{map_name}_g{gx}_{gy}"


# =========================================================================
# Image cropping
# =========================================================================


def crop_examples(
    selected: list[dict],
    rasters_dir: Path,
    output_dir: Path,
    crop_size: int = _DEFAULT_CROP_SIZE,
    prefix: str = "",
) -> list[dict]:
    """Crop example images from source rasters.

    For each selected example, locates the source raster and extracts
    a square crop centred on the candidate coordinates. Uses the
    existing ``crop_candidate`` function from ``mine_hard_cases.py``.

    Args:
        selected: List of selected candidate dicts with ``x``, ``y``,
            and ``map_name`` fields.
        rasters_dir: Directory containing source GeoTIFF rasters.
        output_dir: Directory for cropped images.
        crop_size: Crop dimensions in pixels (default 128).
        prefix: Filename prefix (e.g., ``"hp"`` or ``"hn"``).

    Returns:
        Updated list with ``crop_path`` field added to each dict.
        Candidates where cropping failed have ``crop_path = None``.
    """
    output_dir.mkdir(parents=True, exist_ok=True)

    for i, candidate in enumerate(selected):
        crop_filename = f"{prefix}_{i + 1:02d}.png"
        crop_path = output_dir / crop_filename

        # Build a geometry dict for crop_candidate
        geom_dict = {
            "type": "Point",
            "coordinates": [candidate["x"], candidate["y"]],
        }

        # Find the source raster
        map_name = candidate.get("map_name", "unknown")
        raster_path = _find_raster(map_name, rasters_dir)

        if raster_path is None:
            logger.warning(
                "No raster found for %s (map=%s); skipping crop",
                crop_filename, map_name,
            )
            candidate["crop_path"] = None
            continue

        img = crop_candidate(raster_path, geom_dict, crop_size)
        if img is not None:
            img.save(crop_path, "PNG")
            candidate["crop_path"] = str(crop_path)
            logger.debug("Cropped %s from %s", crop_filename, raster_path)
        else:
            logger.warning(
                "Crop failed for %s at (%.0f, %.0f)",
                crop_filename, candidate["x"], candidate["y"],
            )
            candidate["crop_path"] = None

    return selected


def _find_raster(map_name: str, rasters_dir: Path) -> Path | None:
    """Find a source raster for a map name.

    Searches for GeoTIFF files matching the map name in the rasters
    directory.

    Args:
        map_name: Map name prefix (e.g., ``K-35-052-4_32635``).
        rasters_dir: Directory containing source rasters.

    Returns:
        Path to the raster file, or None if not found.
    """
    if not rasters_dir.exists():
        return None

    # Search recursively — rasters may be in subdirectories
    # (e.g., inputs/rasters/Russian1981_32635/K-35-052-4_32635.tif)
    for pattern in [f"{map_name}.tif", f"{map_name}*.tif"]:
        matches = sorted(rasters_dir.rglob(pattern))
        if matches:
            if len(matches) > 1:
                logger.warning(
                    "Multiple rasters match '%s': %s; using %s",
                    pattern,
                    [m.name for m in matches],
                    matches[0].name,
                )
            return matches[0]

    return None


# =========================================================================
# Output writing
# =========================================================================


def write_outputs(
    hp_selected: list[dict],
    hn_selected: list[dict],
    output_dir: Path,
    metadata: dict,
) -> None:
    """Write pool selection outputs.

    Args:
        hp_selected: Selected hard-positive examples.
        hn_selected: Selected hard-negative examples.
        output_dir: Target directory.
        metadata: Provenance dict.
    """
    output_dir.mkdir(parents=True, exist_ok=True)

    # Selected examples JSON
    examples_path = output_dir / "selected_examples.json"
    examples_path.write_text(
        json.dumps({
            "hard_positives": hp_selected,
            "hard_negatives": hn_selected,
        }, indent=2, ensure_ascii=False, default=str) + "\n",
        encoding="utf-8",
    )
    logger.info("Wrote %s", examples_path)

    # Pool metadata
    meta_path = output_dir / "pool_metadata.json"
    meta_path.write_text(
        json.dumps(metadata, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    logger.info("Wrote %s", meta_path)


# =========================================================================
# CLI
# =========================================================================


def main(argv: list[str] | None = None) -> None:
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Automated example pool builder with diversity "
                    "optimisation.",
    )
    parser.add_argument(
        "--hard-cases", type=Path, required=True,
        help="Path to hard_cases_register.json from discovery",
    )
    parser.add_argument(
        "--hp-count", type=int, required=True,
        help="Number of hard-positive examples to select",
    )
    parser.add_argument(
        "--hn-count", type=int, required=True,
        help="Number of hard-negative examples to select",
    )
    parser.add_argument(
        "--rasters-dir", type=Path, default=_DEFAULT_RASTERS_DIR,
        help="Directory containing source GeoTIFF rasters "
             f"(default: {_DEFAULT_RASTERS_DIR})",
    )
    parser.add_argument(
        "--crop-size", type=int, default=_DEFAULT_CROP_SIZE,
        help=f"Crop size in pixels (default: {_DEFAULT_CROP_SIZE})",
    )
    parser.add_argument(
        "--seed", type=int, default=42,
        help="Random seed (default: 42)",
    )
    parser.add_argument(
        "--output-dir", type=Path, required=True,
        help="Output directory for selected examples and crops",
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

    # Load hard-case register
    with open(args.hard_cases, encoding="utf-8") as f:
        register = json.load(f)

    # Extract HP and HN candidate lists (already ranked in register)
    hp_candidates = [
        m for m in register["mound_register"]
        if m["classification"] in ("borderline_tp", "consistent_fn")
    ]
    hp_candidates.sort(
        key=lambda m: m["difficulty_score"], reverse=True,
    )

    hn_candidates = [
        f for f in register["fp_register"]
        if f["classification"] == "consistent_fp"
    ]
    hn_candidates.sort(
        key=lambda f: f["difficulty_score"], reverse=True,
    )

    logger.info(
        "Available candidates: %d HP, %d HN",
        len(hp_candidates), len(hn_candidates),
    )

    # Check availability
    if len(hp_candidates) < args.hp_count:
        logger.warning(
            "Requested %d HPs but only %d available; selecting all",
            args.hp_count, len(hp_candidates),
        )
    if len(hn_candidates) < args.hn_count:
        logger.warning(
            "Requested %d HNs but only %d available; selecting all",
            args.hn_count, len(hn_candidates),
        )

    # Select with diversity optimisation
    hp_selected = select_diverse_examples(
        hp_candidates, args.hp_count, args.seed,
    )
    hn_selected = select_diverse_examples(
        hn_candidates, args.hn_count, args.seed,
    )

    logger.info(
        "Selected: %d HP, %d HN", len(hp_selected), len(hn_selected),
    )

    # Crop images
    crops_dir = args.output_dir / "crops"
    hp_selected = crop_examples(
        hp_selected, args.rasters_dir, crops_dir,
        crop_size=args.crop_size, prefix="hp",
    )
    hn_selected = crop_examples(
        hn_selected, args.rasters_dir, crops_dir,
        crop_size=args.crop_size, prefix="hn",
    )

    # Metadata
    metadata = {
        "hp_requested": args.hp_count,
        "hn_requested": args.hn_count,
        "hp_selected": len(hp_selected),
        "hn_selected": len(hn_selected),
        "hp_available": len(hp_candidates),
        "hn_available": len(hn_candidates),
        "seed": args.seed,
        "crop_size": args.crop_size,
        "hard_cases_source": str(args.hard_cases),
        "diversity_params": {
            "spatial_penalty_radius_m": _SPATIAL_PENALTY_RADIUS,
            "spatial_penalty_factor": _SPATIAL_PENALTY_FACTOR,
            "same_tile_penalty_factor": _SAME_TILE_PENALTY_FACTOR,
        },
    }

    write_outputs(hp_selected, hn_selected, args.output_dir, metadata)

    # Console summary
    hp_cropped = sum(
        1 for h in hp_selected if h.get("crop_path") is not None
    )
    hn_cropped = sum(
        1 for h in hn_selected if h.get("crop_path") is not None
    )
    print("\nExample pool built:")
    print(f"  HP: {len(hp_selected)} selected, {hp_cropped} cropped")
    print(f"  HN: {len(hn_selected)} selected, {hn_cropped} cropped")
    print(f"  Output: {args.output_dir}")


if __name__ == "__main__":
    main()
