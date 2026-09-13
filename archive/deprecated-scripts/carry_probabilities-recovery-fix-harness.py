#!/usr/bin/env python3
"""
Carry committed verifier probabilities onto a rebuilt union's candidate ids
==========================================================================

Description:
    A rebuilt consensus union re-numbers its candidates, so a committed
    ``probabilities.json`` keyed to the OLD numbering cannot be read against
    the NEW ``candidate_manifest.json``. This script re-keys the committed
    results onto the new numbering by matching candidate positions, and
    reports which new candidates the committed stage does not cover.

    Matching uses the manifests' own ``centroid_x``/``centroid_y``, which are
    already projected (EPSG:32635, metres), so no reprojection is involved.
    Matching is greedy nearest-neighbour under ``--tolerance``, one-to-one.

    It also re-derives, for every matched pair, the **integer pixel window**
    that ``extract_candidates._crop_from_raster`` would cut — ``src.index()``
    floors to whole pixels — so the claim "the carried probability is valid
    because the crop did not change" is measured rather than asserted. At the
    ~5.02 m/px ground resolution of these sheets, a sub-metre centroid shift
    is a sub-pixel shift and usually lands in the same window.

    The seeded ``probabilities.json`` is written in the exact schema
    ``run_pv.py`` reads for its resume filter (``results`` keyed
    ``candidate_NNNNN``), so a subsequent ``run_pv.py verify`` over the new
    crops directory calls the API for the uncovered candidates ONLY.

Usage::

    python carry_probabilities.py \
        --old-manifest  <committed crops>/candidate_manifest.json \
        --old-probs     <committed verify stage>/probabilities.json \
        --new-manifest  <rebuilt crops>/candidate_manifest.json \
        --out-dir       <new verify stage> \
        --rasters-dir   inputs/rasters \
        --label         k3

Outputs:
    <out-dir>/probabilities.json  — seeded with the carried results
    <out-dir>/carry_provenance.json — which candidates were carried, which
        are uncovered, and the pixel-window comparison

Author: Shawn Ross, Claude Code
Licence: Apache 2.0
"""

from __future__ import annotations

import argparse
import json
import math
import re
from pathlib import Path
from typing import Any

import rasterio

#: A tile filename embeds its raster sheet name before the ``_x<N>_y<N>`` offset.
_TILE_RE = re.compile(r"^(?P<sheet>.+?)_x\d+_y\d+\.png$")


def sheet_of(source_tile: str | None) -> str | None:
    """Return the raster sheet name a tile filename belongs to.

    Args:
        source_tile: A tile filename such as
            ``K-35-052-4_32635_x2880_y3072.png``.

    Returns:
        The sheet stem (``K-35-052-4_32635``), or ``None`` if the name does
        not match the tiling convention.
    """
    if not source_tile:
        return None
    match = _TILE_RE.match(source_tile)
    return match.group("sheet") if match else None


def pixel_window(
    rasters_dir: Path,
    sheet: str | None,
    cx: float,
    cy: float,
    padding: int,
    cache: dict[str, Any],
) -> tuple[int, int] | None:
    """Return the integer top-left pixel of the crop window, as rasterio cuts it.

    Mirrors ``scripts/extract_candidates._crop_from_raster``: ``src.index()``
    floors the projected centroid to a whole (row, col), and the window is
    offset by ``padding`` from there.

    Args:
        rasters_dir: Directory holding the GeoTIFF sheets.
        sheet: Sheet stem, from :func:`sheet_of`.
        cx: Projected easting of the candidate centroid.
        cy: Projected northing of the candidate centroid.
        padding: Half the crop edge, in pixels.
        cache: Open-dataset cache, mutated in place.

    Returns:
        ``(col_off, row_off)`` of the crop window, or ``None`` if the sheet
        could not be opened.
    """
    if sheet is None:
        return None
    if sheet not in cache:
        path = rasters_dir / f"{sheet}.tif"
        cache[sheet] = rasterio.open(path) if path.exists() else None
    src = cache[sheet]
    if src is None:
        return None
    row, col = src.index(cx, cy)
    return (int(col) - padding, int(row) - padding)


def main() -> None:
    """Re-key the committed results onto the rebuilt union's candidate ids."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--old-manifest", type=Path, required=True)
    parser.add_argument("--old-probs", type=Path, required=True)
    parser.add_argument("--new-manifest", type=Path, required=True)
    parser.add_argument("--out-dir", type=Path, required=True)
    parser.add_argument("--rasters-dir", type=Path, required=True)
    parser.add_argument("--label", type=str, required=True)
    parser.add_argument("--padding", type=int, default=75)
    parser.add_argument(
        "--tolerance",
        type=float,
        default=2.0,
        help="Positional match tolerance in metres (default: 2.0)",
    )
    args = parser.parse_args()

    old_manifest = json.loads(args.old_manifest.read_text())
    new_manifest = json.loads(args.new_manifest.read_text())
    old_probs = json.loads(args.old_probs.read_text())
    old_results: dict[str, dict] = old_probs["results"]

    old_cands = old_manifest["candidates"]
    new_cands = new_manifest["candidates"]

    # Bucket the old candidates so the nearest-neighbour search is local.
    cell = max(args.tolerance, 1.0)
    buckets: dict[tuple[int, int], list[int]] = {}
    for i, cand in enumerate(old_cands):
        key = (int(cand["centroid_x"] // cell), int(cand["centroid_y"] // cell))
        buckets.setdefault(key, []).append(i)

    cache: dict[str, Any] = {}
    taken: set[int] = set()
    carried: dict[str, dict] = {}
    carry_log: list[dict[str, Any]] = []
    uncovered: list[dict[str, Any]] = []

    for cand in new_cands:
        nx, ny = cand["centroid_x"], cand["centroid_y"]
        cx, cy = int(nx // cell), int(ny // cell)
        best_i, best_d = None, None
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                for i in buckets.get((cx + dx, cy + dy), ()):
                    if i in taken:
                        continue
                    dist = math.hypot(
                        nx - old_cands[i]["centroid_x"],
                        ny - old_cands[i]["centroid_y"],
                    )
                    if dist <= args.tolerance and (best_d is None or dist < best_d):
                        best_i, best_d = i, dist

        new_key = f"candidate_{cand['candidate_id']:05d}"
        if best_i is None:
            uncovered.append(
                {
                    "new_key": new_key,
                    "centroid_x": nx,
                    "centroid_y": ny,
                    "source_tile": cand.get("source_tile"),
                    "vote_count": cand.get("properties", {}).get("vote_count"),
                }
            )
            continue

        taken.add(best_i)
        old_cand = old_cands[best_i]
        old_key = f"candidate_{old_cand['candidate_id']:05d}"
        if old_key not in old_results:
            uncovered.append(
                {
                    "new_key": new_key,
                    "centroid_x": nx,
                    "centroid_y": ny,
                    "source_tile": cand.get("source_tile"),
                    "vote_count": cand.get("properties", {}).get("vote_count"),
                    "note": (
                        f"matched old {old_key} positionally but that key is "
                        "absent from the committed probabilities"
                    ),
                }
            )
            continue

        carried[new_key] = old_results[old_key]
        sheet = sheet_of(cand.get("source_tile"))
        old_window = pixel_window(
            args.rasters_dir,
            sheet_of(old_cand.get("source_tile")),
            old_cand["centroid_x"],
            old_cand["centroid_y"],
            args.padding,
            cache,
        )
        new_window = pixel_window(
            args.rasters_dir, sheet, nx, ny, args.padding, cache
        )
        carry_log.append(
            {
                "new_key": new_key,
                "old_key": old_key,
                "distance_m": round(best_d, 6),
                "old_window": old_window,
                "new_window": new_window,
                "window_identical": old_window == new_window,
                "mound_probability": old_results[old_key].get("mound_probability"),
            }
        )

    for src in cache.values():
        if src is not None:
            src.close()

    moved = [entry for entry in carry_log if entry["distance_m"] > 1e-9]
    window_changed = [
        entry for entry in carry_log if not entry["window_identical"]
    ]

    args.out_dir.mkdir(parents=True, exist_ok=True)
    (args.out_dir / "probabilities.json").write_text(
        json.dumps(
            {
                "version": "1.0",
                "mode": old_probs.get("mode", "realtime"),
                "verifier_config": old_probs.get("verifier_config", "unknown"),
                "iterations": old_probs.get("iterations", 1),
                "total_results": len(carried),
                "results": carried,
            }
        )
    )

    provenance = {
        "schema": "verifier-stage-carry/1",
        "label": args.label,
        "extends_stage": str(args.old_probs.parent),
        "extends_crops": str(args.old_manifest.parent),
        "new_crops": str(args.new_manifest.parent),
        "new_union": new_manifest.get("source_geojson"),
        "old_union": old_manifest.get("source_geojson"),
        "match_tolerance_m": args.tolerance,
        "old_candidates": len(old_cands),
        "new_candidates": len(new_cands),
        "carried": len(carried),
        "uncovered": len(uncovered),
        "carried_but_displaced": len(moved),
        "carried_with_changed_pixel_window": len(window_changed),
        "displaced_detail": sorted(
            moved, key=lambda entry: -entry["distance_m"]
        )[:60],
        "uncovered_detail": uncovered,
    }
    (args.out_dir / "carry_provenance.json").write_text(
        json.dumps(provenance, indent=2)
    )

    print(
        json.dumps(
            {
                key: provenance[key]
                for key in (
                    "label",
                    "old_candidates",
                    "new_candidates",
                    "carried",
                    "uncovered",
                    "carried_but_displaced",
                    "carried_with_changed_pixel_window",
                )
            },
            indent=2,
        )
    )
    print("uncovered:", json.dumps(uncovered, indent=2))


if __name__ == "__main__":
    main()
