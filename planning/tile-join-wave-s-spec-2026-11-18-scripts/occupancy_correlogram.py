#!/usr/bin/env python3
"""
Reference-occupancy correlogram by tile lag (design information, not a result).

Wave S's block sizes must relate to plausible spatial dependence
(``planning/tile-join-wave-s-spec-2026-11-18.md`` § 3.3). The dependence that
matters is in the paired difference between two conditions' per-tile
outcomes, which cannot be consulted before the design is frozen. This script
describes the one pattern that can be read without any model output: where
the reference mounds themselves are. Its output is descriptive design
evidence, not an estimate of the dependence range of model contrasts.

A tile is reference-occupied if a reference recorded on the tile's own sheet
lies in it (the sheet-specific containment of D73 (2)). It takes pairs of
tiles in the same sheet whose pixel offsets differ by a **Chebyshev lag** of
``L`` strides, ``max(|di|, |dj|) = L``. A Chebyshev lag pools axial pairs
(centre distance ``L`` strides) with diagonal ones (up to ``L * sqrt(2)``
strides), so it is not a single distance. For each lag it reports three
statistics:

* **occupancy r pooled**: the Pearson correlation of occupancy over the list
  of pairs (means and variances taken over that list);
* **occupancy within-sheet cross-product**: NOT a Pearson correlation. Each
  tile's occupancy is centred on its own sheet's mean; the statistic is the
  mean, over the lag's pairs, of the product of the two centred values,
  divided by the whole-frame within-sheet variance (the mean squared
  centred occupancy over all tiles). Centring by sheet keeps sheets with
  many mounds and sheets with few from masquerading as long-range
  dependence, but the normaliser is not the variance of the paired values,
  so the value is not bounded like a correlation and must not be read as
  one (Astra, wave S review S3);
* **count r pooled**: the Pearson correlation of reference counts over the
  list of pairs.

Lag 1 includes tiles that physically overlap; from lag 2 no pair shares
ground. Small values at longer lags do not show that dependence ends there.

It reads only the bounds and reference GeoJSON files and imports nothing
beyond the standard library (D70). It reads every feature in the reference
file, whatever its grade; that matches neither scorer exactly and does not
need to, since this is a description of where mounds are, not a score.

Usage::

    python planning/tile-join-wave-s-spec-2026-11-18-scripts/occupancy_correlogram.py \
        > planning/tile-join-wave-s-spec-2026-11-18-scripts/occupancy_correlogram.txt

Created: 2026-11-18 (drafting for S169, amd-tower)
Revised: 2026-11-18 (Astra's round 1, S3: statistics labelled precisely)
Author: Shawn Ross, Claude Code
Licence: Apache 2.0
"""

from __future__ import annotations

import json
import math
import re
from collections import defaultdict
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]

#: (frame, reference file, the reference's sheet column). The columns are
#: the ones ``reference_map_column`` resolves (scripts/lib_advanced_metrics.py).
CASES: tuple[tuple[str, str, str], ...] = (
    ("inputs/vectors/bounds/384/era2_b_intersection_bounds.geojson",
     "inputs/vectors/references/mounds-reference.geojson", "Map"),
    ("inputs/vectors/bounds/384/55maps_evaluation_bounds.geojson",
     "inputs/vectors/references/best-available-gt-55maps-r2.geojson", "source_map"),
)

MAX_LAG = 8
TILE_NAME_RE = re.compile(r"_x(\d+)_y(\d+)\.png$")


def point_in_ring(x: float, y: float, ring: list[list[float]]) -> bool:
    """Ray-casting point-in-polygon test for one closed ring."""
    inside = False
    for (x1, y1), (x2, y2) in zip(ring, ring[1:], strict=False):
        if (y1 > y) != (y2 > y) and x < x1 + (y - y1) * (x2 - x1) / (y2 - y1):
            inside = not inside
    return inside


def pearson(pairs: list[tuple[float, float]]) -> float:
    """Pearson correlation of a list of pairs (NaN when undefined)."""
    n = len(pairs)
    if n < 3:
        return float("nan")
    ma = sum(a for a, _ in pairs) / n
    mb = sum(b for _, b in pairs) / n
    sab = sum((a - ma) * (b - mb) for a, b in pairs)
    sa = math.sqrt(sum((a - ma) ** 2 for a, _ in pairs))
    sb = math.sqrt(sum((b - mb) ** 2 for _, b in pairs))
    return sab / (sa * sb) if sa and sb else float("nan")


def report(frame: str, references: str, column: str) -> None:
    """Print the occupancy correlogram of one frame and reference set."""
    tiles = []
    for feature in json.loads((REPO / frame).read_text())["features"]:
        props = feature["properties"]
        match = TILE_NAME_RE.search(props["tile_name"])
        ring = feature["geometry"]["coordinates"][0]
        tiles.append({
            "sheet": props["map_name"], "xpx": int(match.group(1)), "ypx": int(match.group(2)),
            "ring": ring, "bbox": (min(c[0] for c in ring), max(c[0] for c in ring),
                                   min(c[1] for c in ring), max(c[1] for c in ring)),
        })
    stride = min(t["xpx"] for t in tiles if t["xpx"] > 0)
    points: dict[str, list[tuple[float, float]]] = defaultdict(list)
    for feature in json.loads((REPO / references).read_text())["features"]:
        geom = feature["geometry"]
        coords = [geom["coordinates"]] if geom["type"] == "Point" else geom["coordinates"]
        for c in coords:
            points[feature["properties"][column]].append((c[0], c[1]))
    sheets = {t["sheet"] for t in tiles}
    for t in tiles:
        x0, x1, y0, y1 = t["bbox"]
        t["count"] = sum(1 for (x, y) in points.get(t["sheet"], ())
                         if x0 <= x <= x1 and y0 <= y <= y1 and point_in_ring(x, y, t["ring"]))
        t["occ"] = 1 if t["count"] else 0
    by_sheet: dict[str, dict[tuple[int, int], dict]] = defaultdict(dict)
    for t in tiles:
        by_sheet[t["sheet"]][(t["xpx"] // stride, t["ypx"] // stride)] = t
    for grid in by_sheet.values():
        mean_occ = sum(t["occ"] for t in grid.values()) / len(grid)
        for t in grid.values():
            t["occ_c"] = t["occ"] - mean_occ
    within_var = sum(t["occ_c"] ** 2 for t in tiles) / len(tiles)

    n_points = sum(len(v) for v in points.values())
    n_occ = sum(t["occ"] for t in tiles)
    print(f"\n## {frame}\nreferences: {references} ({n_points} points, sheet column "
          f"{column!r}; {sum(1 for k in points if k not in sheets)} sheet values not in "
          f"the frame)")
    print(f"tiles {len(tiles)}; reference-occupied {n_occ} ({100 * n_occ / len(tiles):.1f} %)")
    rates = sorted(sum(t["occ"] for t in g.values()) / len(g) for g in by_sheet.values())
    print(f"per-sheet occupancy rate min/median/max {rates[0]:.3f}/"
          f"{rates[len(rates) // 2]:.3f}/{rates[-1]:.3f} over {len(rates)} sheets")
    print("lag (Chebyshev, strides) | axial centre spacing | pairs | occupancy r pooled | "
          "occupancy within-sheet cross-product (not a correlation) | count r pooled")
    for lag in range(1, MAX_LAG + 1):
        occ, cnt, centred = [], [], []
        for grid in by_sheet.values():
            for (i, j), t in grid.items():
                for di in range(-lag, lag + 1):
                    for dj in range(-lag, lag + 1):
                        if max(abs(di), abs(dj)) != lag or (i + di, j + dj) <= (i, j):
                            continue
                        u = grid.get((i + di, j + dj))
                        if u is None:
                            continue
                        occ.append((t["occ"], u["occ"]))
                        cnt.append((t["count"], u["count"]))
                        centred.append((t["occ_c"], u["occ_c"]))
        # Mean-centred cross-product normalised by the whole-frame
        # within-sheet variance; not a Pearson correlation (see the header).
        within = (sum(a * b for a, b in centred) / len(centred)) / within_var
        print(f"{lag} | {lag * stride} px | {len(occ)} | {pearson(occ):.3f} | "
              f"{within:.3f} | {pearson(cnt):.3f}")


def main() -> None:
    """Report both corpora."""
    print("Reference-occupancy correlogram for wave S (design information; "
          "no detection or model output read).")
    for case in CASES:
        report(*case)


if __name__ == "__main__":
    main()
