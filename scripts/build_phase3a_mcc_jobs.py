#!/usr/bin/env python3
"""Build a jobs.tsv for the phase3a MCC re-evaluation sweep.

Walks results/phase3a-{text,image}-matrix/ leaf cells (excluding the
with-mcc reference directory), decodes each cell's slug to recover the
threshold and K, then resolves the consensus GeoJSON path using the
mapping established in scripts/run_phase3a_{text,image}_analysis.sh.

Outputs a TSV with three columns:
  detections_geojson \\t output_dir \\t label

Designed for consumption by GNU parallel:
  parallel -j 8 --joblog ... --colsep '\\t' '...' :::: jobs.tsv

Usage:
  python scripts/build_phase3a_mcc_jobs.py > /tmp/jobs.tsv
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

# Source roots (mirrors the bash drivers).
TEXT_ROOTS = {
    "high": "outputs/h11/pv-diag-384/flash-high-text-n5",
    "minimal": "outputs/h11/pv-diag-384/flash-minimal-text-n30-t07",
}
IMAGE_ROOTS = {
    "high": "outputs/h11/pv-diag-384/flash-high-image-n5",
    "minimal": "outputs/h11/pv-diag-384/image-n5",
}
# Special case: image MINIMAL t0.0 lives in n1-outstanding-384.
IMAGE_MINIMAL_T00 = "outputs/h11/n1-outstanding-384/image-t0"

# Cell slug regex: e.g., high-t0-7-7of10, minimal-t0-0-1of3, high-t0-7-26of30.
SLUG_RE = re.compile(
    r"^(?P<thinking>high|minimal)-t(?P<a>\d+)-(?P<b>\d+)-(?P<t>\d+)of(?P<k>\d+)$"
)


def temp_string(a: str, b: str) -> str:
    """Reconstruct the dotted temperature label from two slug fragments.

    The bash driver applies ``sed 's/[^a-z0-9]/-/g'`` so ``t0.7`` becomes
    ``t0-7``. We invert: ``a='0'`` and ``b='7'`` → ``t0.7``.
    """

    return f"t{a}.{b}"


def resolve_pool_subdir(temp: str, pool: str, k: int, track: str) -> str:
    """Map (temp, pool, K, track) to the consensus subdirectory name.

    Text track:
      - n3 → consensus (only for T=0.0, K=3)
      - n5 → consensus-n5
      - n10 (T=0.7 K=30 only) → consensus-n10
      - n10 (other temps) → consensus (full K=10 sweep)
      - n30 → consensus (full K=30 sweep, T=0.7)

    Image track:
      - n3 → consensus (MINIMAL t0.0 only, K=3)
      - n5 → consensus-n5
      - n10 → consensus (full sweep, K=3 for T=0.0 OR K=10 otherwise)
    """

    if pool == "n3":
        return "consensus"
    if pool == "n5":
        return "consensus-n5"
    if pool == "n30":
        return "consensus"
    if pool == "n10":
        # Only the text track has a "consensus-n10" directory, and only for
        # T=0.7 K=30 conditions where K=10 represents a 10-of-30 subset.
        if track == "text" and temp == "t0.7" and k == 10:
            return "consensus-n10"
        return "consensus"
    raise ValueError(f"unknown pool subdir: {pool}")


def resolve_geojson(track: str, thinking: str, temp: str, pool: str,
                    threshold: int, k: int) -> Path:
    """Resolve a cell's consensus GeoJSON path on disk."""

    if track == "image" and thinking == "minimal" and temp == "t0.0":
        # Special case under n1-outstanding-384.
        sub = resolve_pool_subdir(temp, pool, k, track)
        base = REPO_ROOT / IMAGE_MINIMAL_T00 / sub
    else:
        roots = TEXT_ROOTS if track == "text" else IMAGE_ROOTS
        root = REPO_ROOT / roots[thinking]
        sub = resolve_pool_subdir(temp, pool, k, track)
        base = root / f"{track}-{temp}" / sub

    return base / f"consensus_t{threshold}.geojson"


def cell_to_job(cell_dir: Path, track: str) -> tuple[str, str, str]:
    """Convert a single cell directory into (geojson, output_dir, label)."""

    slug = cell_dir.name
    match = SLUG_RE.match(slug)
    if not match:
        raise ValueError(f"cell slug did not match regex: {slug}")

    thinking = match.group("thinking")
    temp = temp_string(match.group("a"), match.group("b"))
    threshold = int(match.group("t"))
    k = int(match.group("k"))

    # Pool is the parent directory name.
    pool = cell_dir.parent.name

    geojson = resolve_geojson(track, thinking, temp, pool, threshold, k)

    # Recover label using the same convention as the original drivers.
    # Note: use UPPERCASE thinking and dotted temp for the human-friendly
    # label as the drivers did.
    label = f"{thinking.upper()}-{temp}-{threshold}of{k}"

    output_dir = cell_dir
    return (str(geojson.relative_to(REPO_ROOT)),
            str(output_dir.relative_to(REPO_ROOT)),
            label)


def find_cells(matrix_root: Path) -> list[Path]:
    """Find every leaf cell under matrix_root, excluding with-mcc/."""

    cells: list[Path] = []
    if not matrix_root.is_dir():
        return cells
    for thinking_dir in sorted(matrix_root.iterdir()):
        if not thinking_dir.is_dir() or thinking_dir.name == "with-mcc":
            continue
        for pool_dir in sorted(thinking_dir.iterdir()):
            if not pool_dir.is_dir():
                continue
            for cell_dir in sorted(pool_dir.iterdir()):
                if cell_dir.is_dir():
                    cells.append(cell_dir)
    return cells


def main() -> int:
    text_cells = find_cells(REPO_ROOT / "results" / "phase3a-text-matrix")
    image_cells = find_cells(REPO_ROOT / "results" / "phase3a-image-matrix")

    missing: list[str] = []
    rows: list[tuple[str, str, str]] = []

    for cells, track in [(text_cells, "text"), (image_cells, "image")]:
        for cell in cells:
            try:
                geojson, out_dir, label = cell_to_job(cell, track)
            except ValueError as exc:
                missing.append(f"slug-error: {cell} — {exc}")
                continue

            geojson_abs = REPO_ROOT / geojson
            if not geojson_abs.exists():
                missing.append(f"missing-geojson: {cell} → {geojson}")
                continue

            rows.append((geojson, out_dir, label))

    # Print TSV to stdout.
    for geojson, out_dir, label in rows:
        print(f"{geojson}\t{out_dir}\t{label}")

    # Print diagnostics to stderr so they don't pollute the TSV.
    print(f"text_cells={len(text_cells)} image_cells={len(image_cells)} "
          f"jobs={len(rows)} missing={len(missing)}", file=sys.stderr)
    for line in missing:
        print(f"  {line}", file=sys.stderr)

    return 0 if not missing else 1


if __name__ == "__main__":
    raise SystemExit(main())
