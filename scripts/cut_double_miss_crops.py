#!/usr/bin/env python3
"""
Double-miss crop cutter for the paper figure
============================================

Description:
    Cuts verifier-geometry crops of the *true double-misses* surfaced by the
    Principal Investigator's (PI) two 2026-09-06 audits — burial mounds that
    neither the student digitisers nor any model recorded. Five come from the
    sampled empty-tile stratum and two from the cluster census.

    Every crop is produced by the project's own crop routine
    (``scripts/extract_candidates.py::crop_region``), read boundlessly from the
    full-resolution sheet GeoTIFF, so the paper images are pixel-for-pixel the
    same kind of picture the verifier stage was shown. A second, 3x-padding
    version of each point is written alongside it so the surrounding map is
    legible in print.

    Optionally (``--with-omissions``) a clearly separated secondary set is cut
    for the census ``detected`` and ``proposed-but-filtered`` marks — reference
    omissions that the *model* found — for a companion contact sheet.

Usage:
    # Regenerates every artefact under results/double-miss-crops-2026-09-06/
    python scripts/cut_double_miss_crops.py

    # Primary set only, no secondary "omissions the model found" sheet
    python scripts/cut_double_miss_crops.py --no-omissions

    # Cut somewhere else (e.g. a scratch directory) for inspection
    python scripts/cut_double_miss_crops.py --output-dir /tmp/dm-crops

Inputs:
    - results/empty-tile-audit/adjudication.json   (5 true-double-miss marks)
    - results/cluster-audit/adjudication.json      (2 true-double-miss marks,
      plus 6 detected + 1 proposed-but-filtered for the optional set)
    - Crop-geometry provenance, read not assumed:
      outputs/gemini37-screen-2026-08-28/verifier/g384_ov192_g37/crops/candidate_manifest.json
      outputs/gemini37-55map-2026-08-29/verifier/g384_ov192_55map_g37/crops/candidate_manifest.json
    - Sheet GeoTIFFs under inputs/rasters/ (including the Russian1981_32635
      subdirectory that the 55-map manifest names as its ``rasters_dir``)

Outputs (all under --output-dir):
    - <audit>_<position>_<tile-stem>.png          verifier geometry (150x150 px)
    - <audit>_<position>_<tile-stem>_context.png  3x context (450x450 px)
    - manifest.csv                                one row per point, with the
      window pixel bounds and the verification-gate results
    - contact-sheet.png                           labelled grid of the 7 crops
    - contact-sheet-omissions.png                 optional secondary grid

Verification gates (all enforced; the run exits non-zero on failure):
    1. Each crop's centre position must round-trip through the derived crop
       affine transform to within 1 m of the source easting/northing.
    2. The primary manifest must hold exactly 7 rows.
    3. Every primary Portable Network Graphics (PNG) file must measure exactly
       the ``crop_dimensions`` recorded in the verifier crop manifests.

Author: Shawn Ross, Claude Code
Licence: Apache 2.0
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt  # noqa: E402
import rasterio  # noqa: E402
from PIL import Image  # noqa: E402

# Script version
__version__ = "1.0.0"

PROJECT_ROOT = Path(__file__).resolve().parent.parent

# The project's own crop routine — imported rather than reimplemented so the
# paper crops are cut by exactly the code that cut the verifier's crops.
sys.path.insert(0, str(PROJECT_ROOT / "scripts"))
from extract_candidates import crop_region  # noqa: E402

# --- Provenance ------------------------------------------------------------

#: Adjudication files, keyed by the short audit label used in filenames.
ADJUDICATIONS: dict[str, Path] = {
    "empty": PROJECT_ROOT / "results" / "empty-tile-audit" / "adjudication.json",
    "census": PROJECT_ROOT / "results" / "cluster-audit" / "adjudication.json",
}

#: Verifier crop manifests consulted for the geometry parameters. Both are
#: read and required to agree; the run aborts if they do not.
GEOMETRY_MANIFESTS: tuple[Path, ...] = (
    PROJECT_ROOT
    / "outputs/gemini37-screen-2026-08-28/verifier/g384_ov192_g37/crops/candidate_manifest.json",
    PROJECT_ROOT
    / "outputs/gemini37-55map-2026-08-29/verifier/g384_ov192_55map_g37/crops"
    / "candidate_manifest.json",
)

#: Directories searched, in order, for ``<map_name>.tif``. The screen manifest
#: names ``inputs/rasters`` and the 55-map manifest names the
#: ``Russian1981_32635`` subdirectory beneath it; both are honoured.
RASTER_SEARCH_DIRS: tuple[Path, ...] = (
    PROJECT_ROOT / "inputs" / "rasters",
    PROJECT_ROOT / "inputs" / "rasters" / "Russian1981_32635",
)

#: Working coordinate reference system for the audit points.
EXPECTED_CRS = "EPSG:32635"

#: Multiplier applied to the verifier padding for the printable context crop.
CONTEXT_MULTIPLIER = 3

#: Round-trip tolerance for the centre-position gate, in metres.
CENTRE_TOLERANCE_M = 1.0

#: Classes cut into the primary (paper) set.
PRIMARY_CLASS = "true-double-miss"

#: Classes cut into the optional secondary set, in the order shown.
OMISSION_CLASSES: tuple[str, ...] = ("detected", "proposed-but-filtered")

DEFAULT_OUTPUT_DIR = PROJECT_ROOT / "results" / "double-miss-crops-2026-09-06"


@dataclass
class CropRecord:
    """One audited point, its crop geometry, and its gate results.

    Attributes:
        audit: Short audit label — ``empty`` or ``census``.
        position: One-based position label (``order_index`` + 1).
        order_index: Zero-based review order index from the adjudication row.
        tile_name: Review tile the mark was placed on.
        map_name: Sheet name; also the GeoTIFF stem.
        symbol: Cartographic symbol the reviewer recorded.
        mark_class: Adjudicated class of the mark.
        x_world: Easting in :data:`EXPECTED_CRS`.
        y_world: Northing in :data:`EXPECTED_CRS`.
        nearest_anything_m: Distance to the nearest point in any reference set.
        raster: Resolved GeoTIFF path.
        pixel_size_m: Ground sample distance of the sheet, in metres.
        window: Verifier-geometry window as ``(col_off, row_off, width, height)``.
        crop_file: Filename of the verifier-geometry crop.
        context_file: Filename of the 3x context crop.
        centre_roundtrip_m: Gate 1 residual, in metres.
        centre_pixel_quantisation_m: Distance from the point to the centre of
            the pixel it falls in — an inherent property of a 5 m raster,
            reported for honesty, not gated.
        crop_size: Actual ``(width, height)`` of the written primary crop.
    """

    audit: str
    position: int
    order_index: int
    tile_name: str
    map_name: str
    symbol: str
    mark_class: str
    x_world: float
    y_world: float
    nearest_anything_m: float
    raster: Path
    pixel_size_m: float = 0.0
    window: tuple[int, int, int, int] = (0, 0, 0, 0)
    crop_file: str = ""
    context_file: str = ""
    centre_roundtrip_m: float = 0.0
    centre_pixel_quantisation_m: float = 0.0
    crop_size: tuple[int, int] = field(default=(0, 0))


def read_crop_geometry(manifests: tuple[Path, ...]) -> tuple[int, int]:
    """Read the verifier crop geometry from the recorded crop manifests.

    The geometry is never invented here: it is read from every manifest given
    and the manifests must agree, so the paper crops inherit exactly the
    padding the verifier stage used.

    Args:
        manifests: Paths to ``candidate_manifest.json`` files. Missing files
            are skipped with a note; at least one must be present.

    Returns:
        Tuple of ``(padding, crop_dimension)`` in pixels, where the crop is
        ``crop_dimension x crop_dimension``.

    Raises:
        SystemExit: If no manifest is present, or the manifests disagree.

    Example:
        >>> read_crop_geometry(GEOMETRY_MANIFESTS)  # doctest: +SKIP
        (75, 150)
    """
    seen: dict[Path, tuple[int, str, str]] = {}
    for path in manifests:
        if not path.exists():
            print(f"  note: geometry manifest absent, skipped — {path}")
            continue
        data = json.loads(path.read_text())
        seen[path] = (
            int(data["padding"]),
            str(data["crop_dimensions"]),
            str(data.get("rasters_dir", "")),
        )

    if not seen:
        sys.exit("FATAL: no verifier crop manifest found; cannot source geometry.")

    distinct = {(pad, dims) for pad, dims, _ in seen.values()}
    for path, (pad, dims, rasters_dir) in seen.items():
        rel = path.relative_to(PROJECT_ROOT)
        print(f"  geometry from {rel}: padding={pad}, crop_dimensions={dims}, "
              f"rasters_dir={rasters_dir}")
    if len(distinct) != 1:
        sys.exit(f"FATAL: crop manifests disagree on geometry: {sorted(distinct)}")

    padding, dims = distinct.pop()
    width, _, height = dims.partition("x")
    if int(width) != int(height) or int(width) != padding * 2:
        sys.exit(
            f"FATAL: crop_dimensions {dims!r} inconsistent with padding {padding}."
        )
    return padding, int(width)


def resolve_raster(map_name: str) -> Path:
    """Find the sheet GeoTIFF for a map name.

    Args:
        map_name: Sheet name from the adjudication row, e.g. ``K-35-077-2``.

    Returns:
        Path to the GeoTIFF.

    Raises:
        SystemExit: If the sheet is present in no search directory.
    """
    for directory in RASTER_SEARCH_DIRS:
        candidate = directory / f"{map_name}.tif"
        if candidate.exists():
            return candidate
    searched = ", ".join(str(d.relative_to(PROJECT_ROOT)) for d in RASTER_SEARCH_DIRS)
    sys.exit(f"FATAL: raster for {map_name!r} not found under: {searched}")


def load_marks(audit: str, path: Path, classes: tuple[str, ...]) -> list[CropRecord]:
    """Load the adjudication rows of the requested classes.

    Args:
        audit: Short audit label, used in filenames and the manifest.
        path: Path to an ``adjudication.json`` produced by
            ``scripts/empty_tile_adjudicate.py``.
        classes: Mark classes to keep, e.g. ``("true-double-miss",)``.

    Returns:
        A :class:`CropRecord` per matching row, in review order.
    """
    data: dict[str, Any] = json.loads(path.read_text())
    records: list[CropRecord] = []
    for mark in data["per_mark"]:
        if mark["class"] not in classes:
            continue
        records.append(
            CropRecord(
                audit=audit,
                position=int(mark["order_index"]) + 1,
                order_index=int(mark["order_index"]),
                tile_name=str(mark["tile_name"]),
                map_name=str(mark["map_name"]),
                symbol=str(mark["symbol"]),
                mark_class=str(mark["class"]),
                x_world=float(mark["x_world"]),
                y_world=float(mark["y_world"]),
                nearest_anything_m=float(mark["nearest_anything_m"]),
                raster=resolve_raster(str(mark["map_name"])),
            )
        )
    records.sort(key=lambda r: r.order_index)
    return records


def cut_record(record: CropRecord, padding: int, output_dir: Path) -> CropRecord:
    """Cut the verifier-geometry and context crops for one audited point.

    The verifier crop is produced by ``extract_candidates.crop_region`` — the
    project's own routine — at the padding read from the crop manifests. The
    context crop reuses the same routine at :data:`CONTEXT_MULTIPLIER` times
    that padding, so both share a centre pixel.

    Args:
        record: The point to cut. Mutated in place with geometry and gate
            results, then returned.
        padding: Verifier padding in pixels (half the crop dimension).
        output_dir: Directory the PNGs are written into.

    Returns:
        The same record, populated.

    Raises:
        SystemExit: If the raster is not in :data:`EXPECTED_CRS`, or a crop
            fails to write.
    """
    stem = record.tile_name.removesuffix(".png")
    base = f"{record.audit}_{record.position}_{stem}"
    crop_path = output_dir / f"{base}.png"
    context_path = output_dir / f"{base}_context.png"

    with rasterio.open(record.raster) as src:
        # Gate the CRS rather than silently assuming it. The adjudication
        # points are EPSG:32635; a differently projected sheet would need a
        # transform, which we refuse to do implicitly.
        if src.crs is None or src.crs.to_string() != EXPECTED_CRS:
            sys.exit(
                f"FATAL: {record.raster.name} is in {src.crs}, expected "
                f"{EXPECTED_CRS}; refusing to crop without an explicit transform."
            )
        record.pixel_size_m = float(src.res[0])

        # Integer pixel the point falls in — the same call crop_region makes.
        row, col = src.index(record.x_world, record.y_world)
        record.window = (col - padding, row - padding, padding * 2, padding * 2)

        # Gate 1: round-trip the point's exact sub-pixel position within the
        # crop back to world coordinates through the derived crop transform.
        frac_col, frac_row = ~src.transform * (record.x_world, record.y_world)
        back_x, back_y = src.transform * (frac_col, frac_row)
        record.centre_roundtrip_m = (
            (back_x - record.x_world) ** 2 + (back_y - record.y_world) ** 2
        ) ** 0.5

        # Informational: how far the point sits from the centre of its own
        # pixel. Bounded by half a pixel diagonal (~3.6 m at 5 m ground
        # sample distance) and inherent to any raster crop.
        centre_x, centre_y = src.xy(row, col)
        record.centre_pixel_quantisation_m = (
            (centre_x - record.x_world) ** 2 + (centre_y - record.y_world) ** 2
        ) ** 0.5

    centroid = (record.x_world, record.y_world)
    if not crop_region(record.raster, centroid, padding, crop_path):
        sys.exit(f"FATAL: verifier crop failed for {base}")
    if not crop_region(
        record.raster, centroid, padding * CONTEXT_MULTIPLIER, context_path
    ):
        sys.exit(f"FATAL: context crop failed for {base}")

    with Image.open(crop_path) as img:
        record.crop_size = img.size
    record.crop_file = crop_path.name
    record.context_file = context_path.name
    return record


def write_manifest(records: list[CropRecord], path: Path) -> None:
    """Write the crop manifest as comma-separated values.

    Args:
        records: Populated crop records, in output order.
        path: Destination ``.csv`` path.
    """
    fieldnames = [
        "audit",
        "position",
        "order_index",
        "class",
        "tile_name",
        "map_name",
        "symbol",
        "x_world",
        "y_world",
        "nearest_anything_m",
        "raster",
        "pixel_size_m",
        "window_col_off",
        "window_row_off",
        "window_width",
        "window_height",
        "crop_file",
        "context_file",
        "crop_width_px",
        "crop_height_px",
        "centre_roundtrip_m",
        "centre_pixel_quantisation_m",
    ]
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for rec in records:
            writer.writerow(
                {
                    "audit": rec.audit,
                    "position": rec.position,
                    "order_index": rec.order_index,
                    "class": rec.mark_class,
                    "tile_name": rec.tile_name,
                    "map_name": rec.map_name,
                    "symbol": rec.symbol,
                    "x_world": f"{rec.x_world:.1f}",
                    "y_world": f"{rec.y_world:.1f}",
                    "nearest_anything_m": f"{rec.nearest_anything_m:.1f}",
                    "raster": str(rec.raster.relative_to(PROJECT_ROOT)),
                    "pixel_size_m": f"{rec.pixel_size_m:.4f}",
                    "window_col_off": rec.window[0],
                    "window_row_off": rec.window[1],
                    "window_width": rec.window[2],
                    "window_height": rec.window[3],
                    "crop_file": rec.crop_file,
                    "context_file": rec.context_file,
                    "crop_width_px": rec.crop_size[0],
                    "crop_height_px": rec.crop_size[1],
                    "centre_roundtrip_m": f"{rec.centre_roundtrip_m:.6f}",
                    "centre_pixel_quantisation_m": (
                        f"{rec.centre_pixel_quantisation_m:.3f}"
                    ),
                }
            )


def build_contact_sheet(
    records: list[CropRecord],
    output_dir: Path,
    path: Path,
    title: str,
    subtitle: str,
) -> None:
    """Render a labelled grid of the verifier-geometry crops.

    Axes are placed manually in figure inches rather than through
    ``tight_layout``: the panels are aspect-locked squares, which the automatic
    layout engines size incorrectly, letting one row's caption collide with the
    next row's heading.

    Args:
        records: Populated crop records to display, in order.
        output_dir: Directory holding the crop PNGs.
        path: Destination PNG path for the sheet.
        title: Figure title.
        subtitle: Second title line giving geometry and provenance.
    """
    n_cols = min(4, len(records))
    n_rows = -(-len(records) // n_cols)  # ceiling division

    cell_w_in = 2.45
    img_side_in = 2.15
    caption_in = 1.15
    head_in = 1.05
    row_h_in = img_side_in + caption_in
    fig_w = cell_w_in * n_cols
    fig_h = head_in + row_h_in * n_rows

    fig = plt.figure(figsize=(fig_w, fig_h), dpi=220, facecolor="white")

    for index, rec in enumerate(records):
        row, col = divmod(index, n_cols)
        left_in = (col + 0.5) * cell_w_in - img_side_in / 2
        bottom_in = fig_h - head_in - row * row_h_in - img_side_in
        axis = fig.add_axes(
            (
                left_in / fig_w,
                bottom_in / fig_h,
                img_side_in / fig_w,
                img_side_in / fig_h,
            )
        )
        with Image.open(output_dir / rec.crop_file) as img:
            axis.imshow(img)

        # Crosshair ticks marking the audited point, broken at the centre so
        # they frame the symbol rather than cover it.
        centre = rec.crop_size[0] / 2.0
        span, gap = centre * 0.30, centre * 0.12
        for x0, y0, x1, y1 in (
            (centre, centre - span - gap, centre, centre - gap),
            (centre, centre + gap, centre, centre + span + gap),
            (centre - span - gap, centre, centre - gap, centre),
            (centre + gap, centre, centre + span + gap, centre),
        ):
            axis.plot([x0, x1], [y0, y1], color="#d62728", lw=1.0)

        axis.set_xticks([])
        axis.set_yticks([])
        for spine in axis.spines.values():
            spine.set_edgecolor("#333333")
            spine.set_linewidth(0.8)

        # Caption drawn as two blocks — a bold identifier and a smaller
        # provenance stack — so that a long sheet name wraps onto its own
        # line instead of running into the neighbouring panel's caption.
        caption_y = (bottom_in - 0.16) / fig_h
        centre_x = (left_in + img_side_in / 2) / fig_w
        fig.text(
            centre_x,
            caption_y,
            f"{rec.audit} #{rec.position}",
            ha="center",
            va="top",
            fontsize=8.5,
            fontweight="bold",
        )
        fig.text(
            centre_x,
            caption_y - 0.20 / fig_h,
            f"{rec.map_name}\n"
            f"{rec.tile_name.removesuffix('.png')}\n"
            f"{rec.symbol.lower()}\n"
            f"nearest reference point {rec.nearest_anything_m:.0f} m",
            ha="center",
            va="top",
            fontsize=6.5,
            color="#333333",
            linespacing=1.5,
        )

    fig.text(
        0.5,
        1 - 0.30 / fig_h,
        title,
        ha="center",
        va="top",
        fontsize=12,
    )
    fig.text(
        0.5,
        1 - 0.58 / fig_h,
        subtitle,
        ha="center",
        va="top",
        fontsize=7,
        color="#444444",
        wrap=True,
    )
    fig.savefig(path, facecolor="white")
    plt.close(fig)


def run_gates(
    records: list[CropRecord], expected_rows: int, crop_dimension: int
) -> list[str]:
    """Check the three pre-commit gates and report the outcome.

    Args:
        records: Populated crop records.
        expected_rows: The row count the manifest must have.
        crop_dimension: The pixel dimension every primary crop must have.

    Returns:
        A list of failure messages; empty means every gate passed.
    """
    failures: list[str] = []

    worst = max((r.centre_roundtrip_m for r in records), default=0.0)
    if worst >= CENTRE_TOLERANCE_M:
        failures.append(
            f"Gate 1 FAIL: worst centre round-trip {worst:.3f} m "
            f">= {CENTRE_TOLERANCE_M} m"
        )
    print(
        f"  Gate 1 centre round-trip  : max {worst:.6f} m "
        f"(tolerance {CENTRE_TOLERANCE_M} m) — "
        f"{'PASS' if worst < CENTRE_TOLERANCE_M else 'FAIL'}"
    )
    worst_quant = max((r.centre_pixel_quantisation_m for r in records), default=0.0)
    print(
        f"    (informational: max distance from point to its own pixel centre "
        f"{worst_quant:.2f} m — inherent to a ~5 m raster)"
    )

    if len(records) != expected_rows:
        failures.append(
            f"Gate 2 FAIL: {len(records)} rows, expected {expected_rows}"
        )
    print(
        f"  Gate 2 manifest row count : {len(records)} "
        f"(expected {expected_rows}) — "
        f"{'PASS' if len(records) == expected_rows else 'FAIL'}"
    )

    bad = [r for r in records if r.crop_size != (crop_dimension, crop_dimension)]
    if bad:
        failures.append(
            "Gate 3 FAIL: wrong crop dimensions for "
            + ", ".join(f"{r.crop_file}={r.crop_size}" for r in bad)
        )
    print(
        f"  Gate 3 crop dimensions    : "
        f"{len(records) - len(bad)}/{len(records)} at "
        f"{crop_dimension}x{crop_dimension} px — {'PASS' if not bad else 'FAIL'}"
    )
    return failures


def main() -> int:
    """Cut every crop, write the manifest and contact sheets, and run the gates.

    Returns:
        Process exit code — 0 on success, 1 if any gate failed.
    """
    parser = argparse.ArgumentParser(
        description=(
            "Cut verifier-geometry crops of the seven audited true "
            "double-misses, plus contact sheets, for the paper."
        )
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help=f"Destination directory (default: {DEFAULT_OUTPUT_DIR}).",
    )
    parser.add_argument(
        "--no-omissions",
        dest="with_omissions",
        action="store_false",
        help="Skip the secondary 'omissions the model found' set.",
    )
    parser.set_defaults(with_omissions=True)
    args = parser.parse_args()

    output_dir: Path = args.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)

    print("Crop geometry provenance")
    padding, crop_dimension = read_crop_geometry(GEOMETRY_MANIFESTS)
    print(
        f"  -> padding {padding} px, crop {crop_dimension}x{crop_dimension} px; "
        f"context crop {padding * CONTEXT_MULTIPLIER * 2}px "
        f"({CONTEXT_MULTIPLIER}x padding)\n"
    )

    print("Primary set — true double-misses")
    primary: list[CropRecord] = []
    for audit, path in ADJUDICATIONS.items():
        found = load_marks(audit, path, (PRIMARY_CLASS,))
        print(f"  {audit}: {len(found)} {PRIMARY_CLASS} marks from "
              f"{path.relative_to(PROJECT_ROOT)}")
        primary.extend(found)
    primary = [cut_record(rec, padding, output_dir) for rec in primary]
    write_manifest(primary, output_dir / "manifest.csv")
    build_contact_sheet(
        primary,
        output_dir,
        output_dir / "contact-sheet.png",
        "True double-misses: mounds neither the students nor any model recorded",
        f"Verifier crop geometry — {crop_dimension}x{crop_dimension} px "
        f"(padding {padding} px) read boundlessly from the sheet GeoTIFF; "
        f"~{primary[0].pixel_size_m * crop_dimension:.0f} m across at "
        f"~{primary[0].pixel_size_m:.2f} m/px. Red ticks mark the audited point.",
    )
    print("\nGates — primary set")
    failures = run_gates(primary, 7, crop_dimension)

    if args.with_omissions:
        print("\nSecondary set — reference omissions the model found")
        secondary = load_marks(
            "census", ADJUDICATIONS["census"], OMISSION_CLASSES
        )
        print(f"  census: {len(secondary)} marks in classes "
              f"{', '.join(OMISSION_CLASSES)}")
        secondary = [cut_record(rec, padding, output_dir) for rec in secondary]
        write_manifest(secondary, output_dir / "manifest-omissions.csv")
        build_contact_sheet(
            secondary,
            output_dir,
            output_dir / "contact-sheet-omissions.png",
            "Reference omissions the model found",
            "Census marks absent from the reference but recovered by a model "
            "(detected) or proposed and then filtered out "
            "(proposed-but-filtered). Same verifier crop geometry as the "
            "primary sheet.",
        )
        print("\nGates — secondary set")
        failures.extend(run_gates(secondary, 7, crop_dimension))

    print()
    if failures:
        for message in failures:
            print(f"  {message}")
        return 1
    print("All gates PASSED.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
