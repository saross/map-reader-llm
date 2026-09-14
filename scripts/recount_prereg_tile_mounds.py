#!/usr/bin/env python3
"""
Post-hoc recomputation of the preregistration's per-tile mound counts (E87).

Preregistration sections 2.3-2.5 publish a mound count for each of the 20
calibration and 60 holdout tiles, summarised as "20 tiles, 36 mounds total" and
"60 tiles, 79 mounds total". Those counts were produced by
``scripts/select_tiles_phase2.py``, whose ``load_map_georef`` estimates each
sheet's map extent from the **bounding box of that sheet's reference points**
and its pixel dimensions from tile filenames; it never reads the raster affine.
Because the references do not reach the sheet edges, the inferred extent is
smaller than the sheet, so every tile's map-coordinate window is shifted and
scaled, and the counts are wrong.

This script publishes the affine-correct counts beside the published ones, and
demonstrates the mechanism by re-running the superseded approximation:

* **affine-correct** — each tile's window is read from
  ``inputs/tiles/<sheet>/metadata.json``, which records
  ``[min_x, min_y, pixel_size_x, pixel_size_y]`` derived from the GeoTIFF
  affine at tiling time. This is the georeferencing that
  ``scripts/generate_tile_bounds.py`` uses for every bounds file the evaluation
  pipeline scores against, so it is the project's own definition of where a
  tile is. Two window sizes are reported: the **full 512 px tile**, and the
  **448 px core**, which is the tile minus its overlap with the next tile.
  Cores tile the sheet without overlap, so their counts sum to the reference
  total exactly — the script asserts this as a self-check.
* **approximation** — computed by importing ``load_map_georef``,
  ``get_map_dimensions`` and ``count_mounds_in_tile`` from
  ``select_tiles_phase2`` itself, so no re-implementation can drift from the
  script that wrote the tables.

Two counting conventions matter for the totals. A **sum** of per-tile counts
double-counts a reference that falls in two tiles' 64 px overlap; a **union**
counts distinct references. Both are reported: for the 20 calibration tiles the
512 px windows hold 50 distinct references (52 as a sum), and the 448 px cores
hold 39. Neither is 36.

Outputs, both clearly labelled as post-hoc corrections and neither replacing
the lodged text (the Open Science Framework registration is immutable; the
errata register is the correction channel):

* ``docs/methodology/preregistration/osf/tile-mound-counts-recomputed-2026-09-13.json``
* ``docs/methodology/preregistration/osf/tile-mound-counts-recomputed-2026-09-13.md``

Usage::

    python scripts/recount_prereg_tile_mounds.py             # write both files
    python scripts/recount_prereg_tile_mounds.py --dry-run   # summary only
    python scripts/recount_prereg_tile_mounds.py --check     # exit 1 on drift

Inputs:
    - ``docs/methodology/preregistration/osf/preregistration.md`` (sections 2.3
      and 2.4 tables — the published counts are parsed, not transcribed)
    - ``inputs/tiles/<sheet>/metadata.json`` (affine-derived tile origins)
    - ``inputs/vectors/references/mounds-reference.geojson`` (569 symbols)
    - ``inputs/tiles/{calibration,validation}_manifest.json``

Created: 2026-09-13 (E87 remediation 2)
Author: Shawn Ross, Claude Code
Licence: Apache 2.0
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path
from typing import Any

#: Era-1 tile side in pixels, and the stride between tile origins. The
#: difference is the 64 px overlap; the stride is the "core" width.
TILE_PX = 512
CORE_PX = 448

SHEETS = (
    "K-35-052-4_32635",
    "K-35-053-3_Elenovo",
    "K-35-062-2_Rakovski",
    "K-35-078-1_Lesovo",
)

PREREG = "docs/methodology/preregistration/osf/preregistration.md"
REFERENCE = "inputs/vectors/references/mounds-reference.geojson"
OUT_STEM = (
    "docs/methodology/preregistration/osf/"
    "tile-mound-counts-recomputed-2026-09-13"
)

#: The two registered sets, as ``(label, manifest path, prereg section)``.
SETS = (
    ("calibration", "inputs/tiles/calibration_manifest.json", "2.3"),
    ("holdout", "inputs/tiles/validation_manifest.json", "2.4"),
)

_ROW_RE = re.compile(
    r"^\|\s*(?P<tile>[A-Za-z0-9_\\.-]+\.png)\s*\|\s*(?P<count>\d+)\s*\|"
)


def repo_root() -> Path:
    """Return the repository root (the parent of this script's directory)."""
    return Path(__file__).resolve().parent.parent


# ---------------------------------------------------------------------------
# The published counts, parsed from the lodged text
# ---------------------------------------------------------------------------


def parse_published_counts(root: Path) -> dict[str, dict[str, int]]:
    """Parse the per-tile counts out of preregistration sections 2.3 and 2.4.

    Parsing rather than transcribing keeps this script honest: if the lodged
    tables were ever edited the parsed values would move with them, and the
    ``--check`` mode would notice.

    Args:
        root: Repository root.

    Returns:
        ``{"calibration": {tile: count}, "holdout": {tile: count}}``.

    Raises:
        SystemExit: If either section yields an unexpected number of rows.
    """
    text = (root / PREREG).read_text(encoding="utf-8")
    lines = text.splitlines()
    # Section bounds: 2.3 runs to the 2.4 heading, 2.4 to the 2.5 heading.
    def index_of(prefix: str) -> int:
        for i, line in enumerate(lines):
            if line.startswith(prefix):
                return i
        sys.exit(f"ERROR: heading not found in {PREREG}: {prefix}")

    spans = {
        "calibration": (index_of("### 2.3 "), index_of("### 2.4 ")),
        "holdout": (index_of("### 2.4 "), index_of("### 2.5 ")),
    }
    expected = {"calibration": 20, "holdout": 60}
    parsed: dict[str, dict[str, int]] = {}
    for label, (start, end) in spans.items():
        counts: dict[str, int] = {}
        for line in lines[start:end]:
            match = _ROW_RE.match(line)
            if match:
                tile = match.group("tile").replace("\\", "")
                counts[tile] = int(match.group("count"))
        if len(counts) != expected[label]:
            sys.exit(
                f"ERROR: parsed {len(counts)} {label} rows from section "
                f"{spans[label]}, expected {expected[label]}"
            )
        parsed[label] = counts
    return parsed


# ---------------------------------------------------------------------------
# The affine-correct counts
# ---------------------------------------------------------------------------


def load_reference_points(root: Path) -> dict[str, list[tuple[int, float, float]]]:
    """Load reference mound coordinates, grouped by sheet and identified.

    Each point carries ``(feature_id, x, y)`` so a union over overlapping
    windows can count distinct references rather than distinct hits.

    Args:
        root: Repository root.

    Returns:
        ``{sheet: [(feature_key, x, y), ...]}``.
    """
    data = json.loads((root / REFERENCE).read_text(encoding="utf-8"))
    points: dict[str, list[tuple[int, float, float]]] = {}
    for index, feature in enumerate(data["features"]):
        sheet = feature["properties"]["Map"]
        geometry = feature["geometry"]
        coords = (
            geometry["coordinates"] if geometry["type"] == "MultiPoint"
            else [geometry["coordinates"]]
        )
        for part, coord in enumerate(coords):
            key = index * 1000 + part
            points.setdefault(sheet, []).append((key, coord[0], coord[1]))
    return points


def load_tile_affines(root: Path) -> dict[str, list[float]]:
    """Load every tile's affine-derived origin and pixel size.

    ``inputs/tiles/<sheet>/metadata.json`` maps a tile filename to
    ``[min_x, min_y, pixel_size_x, pixel_size_y]``, where ``min_y`` is the
    tile's **bottom** edge (the convention ``generate_tile_bounds.py``
    validates against, after erratum E4's y-axis inversion).

    Args:
        root: Repository root.

    Returns:
        ``{tile_filename: [min_x, min_y, px_x, px_y]}``.
    """
    affines: dict[str, list[float]] = {}
    for sheet in SHEETS:
        path = root / "inputs" / "tiles" / sheet / "metadata.json"
        affines.update(json.loads(path.read_text(encoding="utf-8")))
    return affines


def sheet_of(tile: str) -> str:
    """Return the sheet name a tile filename belongs to."""
    return tile.rsplit("_x", 1)[0]


def affine_window(
    tile: str, affines: dict[str, list[float]], size_px: int,
) -> tuple[float, float, float, float]:
    """Return ``(min_x, max_x, min_y, max_y)`` for a window at a tile's origin.

    The window is anchored at the tile's top-left corner and extends *size_px*
    pixels right and down, so ``size_px=512`` is the whole tile and
    ``size_px=448`` its core (the tile minus the overlap it shares with the
    next tile along each axis).

    Args:
        tile: Tile filename.
        affines: Output of :func:`load_tile_affines`.
        size_px: Window side in pixels.

    Returns:
        The window's map-coordinate bounds in EPSG:32635.
    """
    min_x, min_y, px_x, px_y = affines[tile]
    # The recorded min_y is the tile's bottom edge; the window hangs from the
    # tile's top edge, which is one full tile height above it.
    top_y = min_y + TILE_PX * px_y
    left = min_x
    right = min_x + size_px * px_x
    upper = top_y
    lower = top_y - size_px * px_y
    return left, right, lower, upper


def count_in_window(
    points: list[tuple[int, float, float]],
    bounds: tuple[float, float, float, float],
) -> list[int]:
    """Return the keys of the reference points inside *bounds* (inclusive)."""
    left, right, lower, upper = bounds
    return [
        key for key, x, y in points
        if left <= x <= right and lower <= y <= upper
    ]


# ---------------------------------------------------------------------------
# The superseded approximation, run through the original script
# ---------------------------------------------------------------------------


def approximation_counts(root: Path, tiles: list[str]) -> dict[str, int]:
    """Re-run the superseded bounding-box approximation for *tiles*.

    Imports ``select_tiles_phase2`` and calls its own ``load_map_georef``,
    ``get_map_dimensions`` and ``count_mounds_in_tile``, so the reproduction
    cannot drift from the script that wrote the published tables. That module
    resolves ``inputs/`` relative to the process working directory, so the
    directory is changed for the duration and restored afterwards.

    Args:
        root: Repository root.
        tiles: Tile filenames to count.

    Returns:
        ``{tile: count}``.
    """
    sys.path.insert(0, str(root / "scripts"))
    previous = Path.cwd()
    try:
        os.chdir(root)
        import select_tiles_phase2 as legacy  # noqa: PLC0415

        mounds = legacy.load_ground_truth()
        georefs = {s: legacy.load_map_georef(s) for s in SHEETS}
        dims = {s: legacy.get_map_dimensions(s) for s in SHEETS}
        return {
            tile: legacy.count_mounds_in_tile(
                tile, mounds.get(sheet_of(tile), []),
                georefs[sheet_of(tile)], *dims[sheet_of(tile)],
            )
            for tile in tiles
        }
    finally:
        os.chdir(previous)


# ---------------------------------------------------------------------------
# Assembly
# ---------------------------------------------------------------------------


def build_payload(root: Path) -> dict[str, Any]:
    """Compute the whole recomputation payload.

    Args:
        root: Repository root.

    Returns:
        The payload dict, ready to serialise.

    Raises:
        SystemExit: If the 448 px cores do not account for every reference
            exactly once (the geometry self-check).
    """
    published = parse_published_counts(root)
    points = load_reference_points(root)
    affines = load_tile_affines(root)
    reference_total = sum(len(v) for v in points.values())

    # Self-check: the 448 px cores tile each sheet without overlap, so every
    # reference must fall in exactly one core across all 360 physical tiles.
    core_total = 0
    for tile in affines:
        core_total += len(count_in_window(
            points[sheet_of(tile)], affine_window(tile, affines, CORE_PX),
        ))
    if core_total != reference_total:
        sys.exit(
            f"ERROR: geometry self-check failed — the 448 px cores of all "
            f"{len(affines)} tiles hold {core_total} references, but the "
            f"reference layer has {reference_total}."
        )

    sets: dict[str, Any] = {}
    for label, manifest_path, section in SETS:
        tiles = json.loads((root / manifest_path).read_text(encoding="utf-8"))
        approx = approximation_counts(root, tiles)
        rows = []
        union_512: set[int] = set()
        union_core: set[int] = set()
        for tile in tiles:
            pts = points[sheet_of(tile)]
            keys_512 = count_in_window(pts, affine_window(tile, affines, TILE_PX))
            keys_core = count_in_window(pts, affine_window(tile, affines, CORE_PX))
            union_512.update(keys_512)
            union_core.update(keys_core)
            rows.append({
                "tile": tile,
                "published": published[label][tile],
                "affine_512px": len(keys_512),
                "affine_448px_core": len(keys_core),
                "approximation_reproduced": approx[tile],
            })
        rows.sort(key=lambda r: r["tile"])
        sets[label] = {
            "prereg_section": section,
            "manifest": manifest_path,
            "n_tiles": len(tiles),
            "totals": {
                "published": sum(published[label].values()),
                "affine_512px_sum": sum(r["affine_512px"] for r in rows),
                "affine_512px_union": len(union_512),
                "affine_448px_core_sum": sum(r["affine_448px_core"] for r in rows),
                "affine_448px_core_union": len(union_core),
                "approximation_reproduced_sum":
                    sum(r["approximation_reproduced"] for r in rows),
            },
            "exact_row_agreement_with_published": {
                "approximation": sum(
                    1 for r in rows
                    if r["approximation_reproduced"] == r["published"]
                ),
                "affine_512px": sum(
                    1 for r in rows if r["affine_512px"] == r["published"]
                ),
                "affine_448px_core": sum(
                    1 for r in rows if r["affine_448px_core"] == r["published"]
                ),
            },
            "rows": rows,
        }

    return {
        "schema": "prereg-tile-mound-counts-recomputed/1",
        "erratum": "E87",
        "status": (
            "POST-HOC CORRECTION. The Open Science Framework registration is "
            "immutable; these counts do not replace the lodged tables of "
            "preregistration sections 2.3-2.5, they correct them on the "
            "errata register."
        ),
        "generated_by": "scripts/recount_prereg_tile_mounds.py",
        "reference_layer": REFERENCE,
        "reference_total": reference_total,
        "geometry_self_check": (
            f"the 448 px cores of all {len(affines)} physical tiles account "
            f"for {core_total} of {reference_total} references exactly once"
        ),
        "sets": sets,
    }


def render_markdown(payload: dict[str, Any]) -> str:
    """Render the labelled post-hoc table.

    Args:
        payload: Output of :func:`build_payload`.

    Returns:
        The Markdown document text.
    """
    lines = [
        "# Preregistration per-tile mound counts — post-hoc recomputation",
        "",
        "> **GENERATED** by `scripts/recount_prereg_tile_mounds.py`. Do not"
        " hand-edit; regenerate.",
        ">",
        "> **Last revised**: 2026-09-13 (first publication, under erratum"
        " E87). See [§ Changelog](#changelog) for revision history.",
        "",
        "**POST-HOC CORRECTION.** The Open Science Framework (OSF)"
        " registration is immutable. The counts below do **not** replace the"
        " lodged tables of preregistration §§ 2.3–2.5; they correct them on"
        " the errata register (**E87**). The tile *selections* are unchanged"
        " and no measured result reads these counts.",
        "",
        "## Why the lodged counts are wrong",
        "",
        "`scripts/select_tiles_phase2.py` estimates each sheet's map extent"
        " from the **bounding box of that sheet's reference points** and its"
        " pixel size from tile filenames; it never reads the raster affine."
        " Because the references do not reach the sheet edges, the inferred"
        " extent is smaller than the sheet and every tile's map-coordinate"
        " window is shifted and scaled.",
        "",
        "Two window sizes are reported. The **512 px** window is the whole"
        " tile; adjacent tiles share a 64 px overlap, so a sum of per-tile"
        " counts double-counts references in that band and a **union** counts"
        " distinct references. The **448 px core** is the tile minus its"
        " overlap; cores tile each sheet exactly, so their counts partition"
        " the reference layer — the generator asserts this"
        f" ({payload['geometry_self_check']}).",
        "",
        "## Totals",
        "",
        "| Set | § | Tiles | Published | Affine 512 px (union) | Affine 512 px"
        " (sum) | Affine 448 px core |",
        "| :-- | :-- | --: | --: | --: | --: | --: |",
    ]
    for label, data in payload["sets"].items():
        t = data["totals"]
        lines.append(
            f"| {label} | {data['prereg_section']} | {data['n_tiles']} | "
            f"{t['published']} | {t['affine_512px_union']} | "
            f"{t['affine_512px_sum']} | {t['affine_448px_core_union']} |"
        )
    lines += [
        "",
        "## The mechanism, demonstrated",
        "",
        "Re-running the superseded approximation reproduces the published"
        " per-tile counts far better than the affine-correct computation does,"
        " which identifies it as the method that wrote the tables.",
        "",
        "| Set | Rows | Approximation matches | Affine 512 px matches |"
        " Affine 448 px core matches |",
        "| :-- | --: | --: | --: | --: |",
    ]
    total_rows = 0
    total_approx = 0
    total_512 = 0
    for label, data in payload["sets"].items():
        agree = data["exact_row_agreement_with_published"]
        total_rows += data["n_tiles"]
        total_approx += agree["approximation"]
        total_512 += agree["affine_512px"]
        lines.append(
            f"| {label} | {data['n_tiles']} | {agree['approximation']} | "
            f"{agree['affine_512px']} | {agree['affine_448px_core']} |"
        )
    lines.append(
        f"| **all** | **{total_rows}** | **{total_approx}** | "
        f"**{total_512}** | — |"
    )

    for label, data in payload["sets"].items():
        lines += [
            "",
            f"## Per-tile counts — {label} set (preregistration"
            f" § {data['prereg_section']})",
            "",
            "| Tile | Published | Affine 512 px | Affine 448 px core |"
            " Approximation reproduced |",
            "| :-- | --: | --: | --: | --: |",
        ]
        for row in data["rows"]:
            lines.append(
                f"| `{row['tile']}` | {row['published']} | "
                f"{row['affine_512px']} | {row['affine_448px_core']} | "
                f"{row['approximation_reproduced']} |"
            )

    lines += [
        "",
        "## Changelog",
        "",
        "### 2026-09-13 — Original publication",
        "",
        "Published under erratum **E87** (E87 remediation 2), alongside the"
        " machine-readable"
        " `tile-mound-counts-recomputed-2026-09-13.json`. Counts computed from"
        " the affine-derived tile origins in `inputs/tiles/<sheet>/"
        "metadata.json` against"
        f" `{payload['reference_layer']}` ({payload['reference_total']}"
        " symbols); the approximation column was produced by importing"
        " `select_tiles_phase2.load_map_georef` /"
        " `get_map_dimensions` / `count_mounds_in_tile` rather than"
        " re-implementing them.",
        "",
    ]
    return "\n".join(lines)


def _build_parser() -> argparse.ArgumentParser:
    """Construct the command-line interface parser."""
    parser = argparse.ArgumentParser(
        description=(
            "Recompute the preregistration's per-tile mound counts from the "
            "raster affine and publish them as a post-hoc correction (E87)."
        ),
    )
    parser.add_argument("--root", type=Path, default=None,
                        help="Repository root.")
    parser.add_argument("--dry-run", action="store_true",
                        help="Print the totals without writing.")
    parser.add_argument("--check", action="store_true",
                        help="Exit 1 if the committed outputs differ.")
    return parser


def main(argv: list[str] | None = None) -> int:
    """Command-line entry point. Returns a process exit code."""
    args = _build_parser().parse_args(argv)
    root = args.root.resolve() if args.root else repo_root()
    payload = build_payload(root)

    for label, data in payload["sets"].items():
        t = data["totals"]
        print(
            f"{label:12s} n={data['n_tiles']:3d}  published={t['published']:4d}"
            f"  affine512(union)={t['affine_512px_union']:4d}"
            f"  affine512(sum)={t['affine_512px_sum']:4d}"
            f"  core448={t['affine_448px_core_union']:4d}"
            f"  approx={t['approximation_reproduced_sum']:4d}"
        )
        agree = data["exact_row_agreement_with_published"]
        print(
            f"{'':12s} exact row matches vs published: "
            f"approximation {agree['approximation']}/{data['n_tiles']}, "
            f"affine512 {agree['affine_512px']}/{data['n_tiles']}, "
            f"core448 {agree['affine_448px_core']}/{data['n_tiles']}"
        )

    json_path = root / f"{OUT_STEM}.json"
    md_path = root / f"{OUT_STEM}.md"
    json_text = json.dumps(payload, indent=1, ensure_ascii=False) + "\n"
    md_text = render_markdown(payload)

    if args.check:
        problems = []
        for path, text in ((json_path, json_text), (md_path, md_text)):
            if not path.is_file():
                problems.append(f"absent: {path}")
            elif path.read_text(encoding="utf-8") != text:
                problems.append(f"drifted: {path}")
        if problems:
            print("\n--check FAILED: " + "; ".join(problems), file=sys.stderr)
            return 1
        print("\n--check OK: both outputs match a fresh computation")
        return 0

    if args.dry_run:
        return 0

    json_path.write_text(json_text, encoding="utf-8")
    md_path.write_text(md_text, encoding="utf-8")
    print(f"\nwrote {json_path}\nwrote {md_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
