#!/usr/bin/env python3
"""
Significance for the student-vs-model ranking on identical ground.

Upgrades the descriptive footprint-basis ranking
(`results/student-baseline-2026-09-01/per-student-gs4/`) to
statistical claims using the project's GS board instrument: per-tile
TP/FP/FN via per-map Hungarian distribution
(`lib_advanced_metrics.compute_per_tile_tp_fp_fn`), tile-swap
micro-F1 permutation (10,000, seed 42;
`n1_baseline_leaderboard_tiering.permutation_test_float`), and
Benjamini–Hochberg q = 0.05 across the declared family.

Family (14 tests): at each of 20 m and 50 m — students-pooled vs
each model config over all five zones (2), and the zone's own
student vs the all-3.7 model per zone (5).

REPLICATION GATE per contender and zone: the per-tile counts must
sum to the committed zone-level confusion counts in `analysis.json`
exactly, or nothing is written.

Usage::

    python scripts/student_ranking_significance.py

Zero API, seconds of compute (local is fine).

Created: 2026-09-01 (Session 145)
Author: Shawn Ross, Claude Code
Licence: Apache 2.0
"""

from __future__ import annotations

import json
import logging
import sys
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd
from scipy.spatial import cKDTree

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.apply_fdr_correction import apply_bh_correction  # noqa: E402
from scripts.lib_advanced_metrics import (  # noqa: E402
    compute_per_tile_tp_fp_fn,
)
from scripts.n1_baseline_leaderboard_tiering import (  # noqa: E402
    permutation_test_float,
)
from scripts.student_perstudent_gs4 import (  # noqa: E402
    ACTIVE_AREA,
    CRS,
    CURATOR,
    EVAL_FOOTPRINT,
    MODEL_CELLS,
    REVIEWED,
    STAGED,
)

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

OUT_DIR = PROJECT_ROOT / "results/student-baseline-2026-09-01/per-student-gs4"
RADII = (20, 50)
BH_Q = 0.05


def assign_source_tiles(det: gpd.GeoDataFrame,
                        bounds: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """Nearest-tile-centroid ``source_tile`` for point sets lacking one.

    Students digitised sheet-wide, so their points carry no tiling;
    the board instrument distributes TPs/FPs by the detection's
    tile, so one is assigned by nearest footprint-tile centroid (the
    same primary-tile convention the instrument uses for FNs).
    """
    cent = bounds.geometry.centroid
    tree = cKDTree(np.c_[cent.x, cent.y])
    _, idx = tree.query(np.c_[det.geometry.x, det.geometry.y], k=1)
    out = det.copy()
    out["source_tile"] = bounds["tile_name"].to_numpy()[idx]
    return out


def per_tile(det: gpd.GeoDataFrame, ref: gpd.GeoDataFrame,
             bounds: gpd.GeoDataFrame, radius: int) -> pd.DataFrame:
    """Per-tile counts on the zone's tile universe, gap tiles zeroed."""
    counts = compute_per_tile_tp_fp_fn(det, ref, bounds, radius)
    return counts.set_index("tile_name").reindex(
        bounds["tile_name"], fill_value=0)


def main() -> int:
    committed = json.loads((OUT_DIR / "analysis.json").read_text())
    zone_rows = {(r["unit"], r["radius_m"]): r
                 for r in committed["rows"] if r["basis"] == "footprint"}

    reviewed = gpd.read_file(REVIEWED).to_crs(CRS)
    active = gpd.read_file(ACTIVE_AREA).to_crs(CRS)
    reviewed = gpd.sjoin(reviewed, active[["geometry"]], how="inner",
                         predicate="within").drop(columns="index_right")
    curator = gpd.read_file(CURATOR).to_crs(CRS)
    bounds = gpd.read_file(EVAL_FOOTPRINT).to_crs(CRS)
    areas = gpd.read_file(STAGED / "assignment-areas.geojson").to_crs(CRS)
    audit = areas[areas["area_role"] == "audit_area"]
    cells = {name: gpd.read_file(path).to_crs(CRS)
             for name, path in MODEL_CELLS.items()}

    # Per-zone, per-contender per-tile count frames.
    frames: dict[tuple[str, str, int], pd.DataFrame] = {}
    zones: list[tuple[str, str]] = []
    footprint = bounds.union_all()
    for rec in audit.itertuples():
        zone = rec.geometry.intersection(footprint)
        # Tile universe: footprint tiles touching the zone, SAME SHEET
        # only. Both constraints were gate-caught on first runs: a
        # centroid-within universe silently dropped a boundary tile's
        # outcomes, and including the neighbouring sheet's abutting
        # tiles let nearest-centroid assignment send 3 Elenovo points
        # to K-35-052-4 tiles, where the per-map loop cannot match
        # them (3 phantom FP+FN pairs).
        zbounds = bounds[bounds.geometry.intersects(rec.geometry)
                         & bounds["tile_name"].str.startswith(rec.sheet_id)]
        zlabel = f"{rec.sheet_id}[{rec.student_code}]"
        zones.append((zlabel, f"student:{rec.student_code}@{rec.sheet_id}"))
        ref = curator[curator.within(zone)]
        # Uniform convention for every contender: source_tile by
        # nearest same-sheet footprint tile (models' native tiling
        # differs from the footprint naming, so theirs is replaced
        # too — the distribution convention must not differ by
        # contender).
        sdet = assign_source_tiles(reviewed[reviewed.within(zone)], zbounds)
        for radius in RADII:
            frames[("students", zlabel, radius)] = per_tile(
                sdet, ref, zbounds, radius)
        for name, cell in cells.items():
            det = assign_source_tiles(cell[cell.within(zone)], zbounds)
            for radius in RADII:
                frames[(name, zlabel, radius)] = per_tile(
                    det, ref, zbounds, radius)

    # Gate: per-tile sums reproduce the committed zone confusion counts.
    for (who, zlabel, radius), frame in frames.items():
        sheet = zlabel.split("[")[0]
        code = zlabel.split("[")[1].rstrip("]")
        unit = (f"student:{code}@{sheet}" if who == "students"
                else f"{who}@{sheet}[{code}]")
        want = zone_rows[(unit, radius)]
        got = frame[["tp", "fp", "fn"]].sum()
        if not (got["tp"] == want["tp"] and got["fp"] == want["fp"]
                and got["fn"] == want["fn"]):
            raise RuntimeError(
                f"gate FAILED {unit}@{radius}m — per-tile "
                f"{got.to_dict()} vs committed "
                f"{ {k: want[k] for k in ('tp', 'fp', 'fn')} }")
    logger.info("replication gate OK — %d frames match committed counts",
                len(frames))

    def stack(who: str, radius: int) -> pd.DataFrame:
        return pd.concat(
            [frames[(who, z, radius)] for z, _ in zones])

    tests: list[dict] = []
    for radius in RADII:
        for name in cells:
            a, b = stack("students", radius), stack(name, radius)
            r = permutation_test_float(
                a["tp"].to_numpy(float), a["fp"].to_numpy(float),
                a["fn"].to_numpy(float), b["tp"].to_numpy(float),
                b["fp"].to_numpy(float), b["fn"].to_numpy(float))
            tests.append({"test": f"pooled: students vs {name} @{radius}m",
                          **{k: r[k] for k in
                             ("f1_a", "f1_b", "observed_diff", "p_value",
                              "n_tiles")}})
        for zlabel, _ in zones:
            a = frames[("students", zlabel, radius)]
            b = frames[("model:all-3.7-swap-best", zlabel, radius)]
            r = permutation_test_float(
                a["tp"].to_numpy(float), a["fp"].to_numpy(float),
                a["fn"].to_numpy(float), b["tp"].to_numpy(float),
                b["fp"].to_numpy(float), b["fn"].to_numpy(float))
            tests.append({"test": f"zone {zlabel}: student vs all-3.7 "
                          f"@{radius}m",
                          **{k: r[k] for k in
                             ("f1_a", "f1_b", "observed_diff", "p_value",
                              "n_tiles")}})

    adjusted = apply_bh_correction([t["p_value"] for t in tests], q=BH_Q)
    for t, adj in zip(tests, adjusted):
        t["bh_adjusted_p"] = round(float(adj), 6)
        t["significant"] = bool(adj < BH_Q)
        logger.info("%s: d=%+.4f p=%.4f adj=%.4f %s", t["test"],
                    t["observed_diff"], t["p_value"], t["bh_adjusted_p"],
                    "SIG" if t["significant"] else "ns")

    (OUT_DIR / "significance.json").write_text(json.dumps({
        "instrument": ("per-tile tile-swap micro-F1 permutation "
                       "(10000, seed 42) + BH q=0.05, family of "
                       f"{len(tests)}"),
        "convention": "diff = students - model (positive = humans ahead)",
        "tests": tests}, indent=2) + "\n")
    logger.info("SIGNIFICANCE COMPLETE -> %s",
                OUT_DIR.relative_to(PROJECT_ROOT))
    return 0


if __name__ == "__main__":
    sys.exit(main())
