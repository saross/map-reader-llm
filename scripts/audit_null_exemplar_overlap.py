#!/usr/bin/env python3
"""
Which evaluation tiles overlap the three null-exemplar windows (erratum E86).

The three empty ("null") few-shot exemplars — examples 15-17 of the
`neutral-naming` library — are whole 512 x 512 px tiles, transmitted to the
model as images wherever a configuration is image-modality. They were selected
on 2025-12-23 from the then-current training set and never regenerated when
that set was re-selected on 2026-01-04, so they were never entered into the
calibration exclusion geometry that every later evaluation frame was built
from. Erratum E86 records the mechanism; this script measures the exposure.

**What "overlap" means here.** Every tile filename carries its pixel offset
within its own sheet (`..._x2240_y2688.png`), and all frames are cut from the
same rasters, so overlap is decided in that shared pixel space. A frame tile of
side *S* at offset (x, y) overlaps a null exemplar at (nx, ny) when their
axis-aligned 512 px / *S* px windows intersect. No georeferencing is needed and
none is read: the comparison is exact integer arithmetic on the filenames, and
a tile is counted when it shares **any** pixel with a null window.

Two geometries are in play. The Era-1 frames are 512 px tiles on a 448 px
stride, so a null exemplar is itself a frame member and its eight immediate
neighbours overlap it (448 < 512) while the next ring out does not. The 384 px
frames step 336 px, so up to nine tiles overlap each null window.

Outputs a sidecar — ``inputs/examples/null-tiles/null_overlap_by_frame.json``
by default — recording, per frame, the total tile count, the overlapping tile
ids, and the geometry used. The sidecar lets a sensitivity check (the same
scoring with those tiles excluded) run offline with no re-inference.

Usage::

    # Write the sidecar
    python scripts/audit_null_exemplar_overlap.py

    # Print without writing
    python scripts/audit_null_exemplar_overlap.py --dry-run

    # Fail (exit 1) if the committed sidecar disagrees with a fresh computation
    python scripts/audit_null_exemplar_overlap.py --check

Inputs:
    - ``inputs/examples/null-tiles/null_tiles_manifest.json`` — the three
      exemplar tile filenames
    - the frame manifests named in :data:`FRAMES`

Outputs:
    - ``inputs/examples/null-tiles/null_overlap_by_frame.json``

Created: 2026-09-13 (E86 remediation 3)
Author: Shawn Ross, Claude Code
Licence: Apache 2.0
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

#: Side length in pixels of a null exemplar's own window. The exemplars are
#: whole Era-1 tiles, which are 512 px square (``config.TILE_SIZE``).
NULL_TILE_PX = 512

#: The frames to measure: ``(label, manifest path, tile side in px, role)``.
#: ``role`` says whether the frame's tiles are scored (``evaluation``) or are
#: themselves excluded from scoring (``calibration``); a calibration frame is
#: reported for completeness, since an overlap there is by design, not leakage.
FRAMES: tuple[tuple[str, str, int, str], ...] = (
    ("era1-512-full-evaluation",
     "inputs/tiles/full_evaluation_manifest.json", 512, "evaluation"),
    ("era1-512-validation",
     "inputs/tiles/validation_manifest.json", 512, "evaluation"),
    ("era1-512-verification",
     "inputs/tiles/verification_manifest.json", 512, "evaluation"),
    ("era1-512-calibration",
     "inputs/tiles/calibration_manifest.json", 512, "calibration"),
    ("era2-384-full-evaluation",
     "inputs/tiles_384/full_evaluation_manifest.json", 384, "evaluation"),
    ("era2-384-validation",
     "inputs/tiles_384/validation_manifest.json", 384, "evaluation"),
    ("h10-384-test",
     "inputs/calibration/h10-384/test_manifest.json", 384, "evaluation"),
)

#: Where the sidecar lands.
DEFAULT_SIDECAR = "inputs/examples/null-tiles/null_overlap_by_frame.json"

#: Where the null exemplars are declared.
NULL_MANIFEST = "inputs/examples/null-tiles/null_tiles_manifest.json"

_TILE_RE = re.compile(r"^(?P<map>.+)_x(?P<x>\d+)_y(?P<y>\d+)\.png$")


def repo_root() -> Path:
    """Return the repository root (the parent of this script's directory)."""
    return Path(__file__).resolve().parent.parent


def parse_tile(filename: str) -> tuple[str, int, int]:
    """Split a tile filename into its sheet name and pixel offset.

    Args:
        filename: e.g. ``K-35-078-1_Lesovo_x2240_y2688.png``.

    Returns:
        ``(sheet, x, y)``.

    Raises:
        ValueError: If the filename does not carry a pixel offset.

    Example:
        >>> parse_tile("K-35-078-1_Lesovo_x2240_y2688.png")
        ('K-35-078-1_Lesovo', 2240, 2688)
    """
    match = _TILE_RE.match(filename)
    if not match:
        raise ValueError(f"cannot parse a pixel offset from {filename!r}")
    return match.group("map"), int(match.group("x")), int(match.group("y"))


def windows_overlap(
    x: int, y: int, size: int,
    null_x: int, null_y: int, null_size: int = NULL_TILE_PX,
) -> bool:
    """Whether a *size* px tile at (x, y) shares any pixel with a null window.

    Both windows are axis-aligned and half-open: ``[x, x + size)``. Tiles that
    merely abut (one window's last pixel beside the other's first) do not
    overlap.

    Args:
        x: Tile's left pixel offset within its sheet.
        y: Tile's top pixel offset within its sheet.
        size: Tile side length in pixels.
        null_x: Null exemplar's left pixel offset.
        null_y: Null exemplar's top pixel offset.
        null_size: Null exemplar's side length (default 512).

    Returns:
        ``True`` when the windows intersect.

    Example:
        >>> windows_overlap(2688, 2688, 512, 2240, 2688)   # stride-448 neighbour
        True
        >>> windows_overlap(3136, 2688, 512, 2240, 2688)   # next ring out
        False
    """
    return (
        x < null_x + null_size and null_x < x + size
        and y < null_y + null_size and null_y < y + size
    )


def load_null_windows(root: Path) -> dict[str, tuple[int, int]]:
    """Read the null exemplars' sheet and pixel offset from their manifest.

    Args:
        root: Repository root.

    Returns:
        ``{sheet: (x, y)}`` — one entry per null exemplar.

    Raises:
        SystemExit: If two exemplars come from the same sheet, which would make
            a sheet-keyed lookup lossy (the registered stratification is one per
            sheet, so this is a corruption check, not a supported case).
    """
    manifest = json.loads((root / NULL_MANIFEST).read_text(encoding="utf-8"))
    windows: dict[str, tuple[int, int]] = {}
    for entry in manifest["tiles"]:
        sheet, x, y = parse_tile(entry["filename"])
        if sheet in windows:
            sys.exit(f"ERROR: two null exemplars on sheet {sheet}")
        windows[sheet] = (x, y)
    return windows


def measure_frame(
    root: Path, manifest_path: str, size: int,
    null_windows: dict[str, tuple[int, int]],
) -> dict[str, Any]:
    """Measure one frame's overlap with the null windows.

    Args:
        root: Repository root.
        manifest_path: Repository-relative manifest path.
        size: Tile side length in pixels for this frame.
        null_windows: Output of :func:`load_null_windows`.

    Returns:
        A dict with the frame's total tile count, the sorted overlapping tile
        ids, and a per-sheet breakdown.
    """
    tiles = json.loads((root / manifest_path).read_text(encoding="utf-8"))
    overlapping: list[str] = []
    by_sheet: dict[str, int] = {}
    for name in tiles:
        sheet, x, y = parse_tile(name)
        window = null_windows.get(sheet)
        if window and windows_overlap(x, y, size, *window):
            overlapping.append(name)
            by_sheet[sheet] = by_sheet.get(sheet, 0) + 1
    return {
        "manifest": manifest_path,
        "tile_size_px": size,
        "n_tiles": len(tiles),
        "n_overlapping": len(overlapping),
        "overlapping_by_sheet": dict(sorted(by_sheet.items())),
        "overlapping_tiles": sorted(overlapping),
    }


def build_sidecar(root: Path) -> dict[str, Any]:
    """Compute the whole sidecar payload from the manifests on disk.

    Args:
        root: Repository root.

    Returns:
        The sidecar dict, ready to serialise.
    """
    null_windows = load_null_windows(root)
    frames: dict[str, Any] = {}
    for label, manifest_path, size, role in FRAMES:
        frame = measure_frame(root, manifest_path, size, null_windows)
        frame["role"] = role
        frames[label] = frame
    return {
        "schema": "null-exemplar-overlap-by-frame/1",
        "erratum": "E86",
        "generated_by": "scripts/audit_null_exemplar_overlap.py",
        "purpose": (
            "Tiles of each frame whose pixel window intersects one of the "
            "three null-exemplar windows. Supports an offline sensitivity "
            "check (re-score with these tiles excluded) without re-inference."
        ),
        "method": (
            "Half-open axis-aligned intersection in each sheet's own pixel "
            "space, from the pixel offsets in the tile filenames. A tile is "
            "counted when it shares any pixel with a null window. Era-1 "
            "frames are 512 px on a 448 px stride; the 384 px frames step "
            "336 px. No georeferencing is read."
        ),
        "null_exemplars": {
            sheet: {"x": x, "y": y, "size_px": NULL_TILE_PX}
            for sheet, (x, y) in sorted(null_windows.items())
        },
        "frames": frames,
    }


def _build_parser() -> argparse.ArgumentParser:
    """Construct the command-line interface parser."""
    parser = argparse.ArgumentParser(
        description=(
            "Record which evaluation tiles overlap the three null-exemplar "
            "windows (erratum E86)."
        ),
    )
    parser.add_argument(
        "--out", type=Path, default=None,
        help=f"Sidecar path (default: {DEFAULT_SIDECAR})",
    )
    parser.add_argument(
        "--root", type=Path, default=None,
        help="Repository root the manifest paths resolve against.",
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Print the summary without writing the sidecar.",
    )
    parser.add_argument(
        "--check", action="store_true",
        help="Exit 1 if the committed sidecar differs from a fresh computation.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    """Command-line entry point. Returns a process exit code."""
    args = _build_parser().parse_args(argv)
    root = args.root.resolve() if args.root else repo_root()
    out = args.out if args.out else root / DEFAULT_SIDECAR

    payload = build_sidecar(root)

    for label, frame in payload["frames"].items():
        role = "" if frame["role"] == "evaluation" else f"  [{frame['role']}]"
        print(
            f"{label:28s} {frame['n_overlapping']:3d} / {frame['n_tiles']:3d}"
            f"  ({frame['tile_size_px']} px){role}"
        )

    if args.check:
        if not out.is_file():
            print(f"\n--check FAILED: sidecar absent: {out}", file=sys.stderr)
            return 1
        committed = json.loads(out.read_text(encoding="utf-8"))
        if committed != payload:
            print(
                f"\n--check FAILED: {out} disagrees with a fresh computation",
                file=sys.stderr,
            )
            return 1
        print(f"\n--check OK: {out} matches")
        return 0

    if args.dry_run:
        return 0

    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(
        json.dumps(payload, indent=1, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(f"\nwrote {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
