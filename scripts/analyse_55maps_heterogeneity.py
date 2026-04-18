#!/usr/bin/env python3
"""
Per-map heterogeneity analysis for the 55-map image generalisation run.

Produces per-map F1 / precision / recall at 20 / 30 / 40 / 50 m buffers
for each map in scope, together with aggregate distribution statistics
and a matched-configuration baseline on the 4-map Era 2 calibration
set. Supports the paper's discussion of whether the headline
F1 = 0.771 @ 50 m is uniform across maps or the average of highly
variable results.

Usage::

    python scripts/analyse_55maps_heterogeneity.py

Inputs (default paths; override via CLI):

- 55-map run: ``outputs/55maps-image-generalisation/verified/verified_detections.geojson``
- 55-map ground truth: ``inputs/vectors/references/student-mounds-55maps.geojson``
- 55-map bounds: ``inputs/vectors/bounds/384/55maps_evaluation_bounds.geojson``
- 55-map cost manifest: ``outputs/55maps-image-generalisation/cost_manifest.json``
- 4-map baseline (constructed in memory at the matched operating point
  from the Phase 3a image matrix verifier run): probabilities +
  candidate manifest under
  ``outputs/h11/pv-diag-384/flash-high-image-n5/image-t0.7/verified-v1-n5/``
- 4-map ground truth: ``inputs/vectors/references/mounds-reference.geojson``
- 4-map bounds: ``inputs/vectors/bounds/384/full_evaluation_bounds.geojson``

Outputs (all under ``results/55maps-image-generalisation/``):

- ``per_map_metrics.csv`` — one row per map × buffer (machine-readable)
- ``per_map_summary.md`` — distribution statistics + outliers
- ``heterogeneity_summary.json`` — aggregate stats + cost correlations

Author: Shawn Ross, Claude Code
Licence: Apache 2.0
"""

from __future__ import annotations

import argparse
import json
import logging
import statistics
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import geopandas as gpd

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR / "scripts"))

from evaluate_detections import load_geojson  # noqa: E402
from lib_advanced_metrics import (  # noqa: E402
    calculate_f1_internal,
    get_map_name,
)

__version__ = "1.0.0"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Defaults
# ---------------------------------------------------------------------------
DEFAULT_BUFFERS: tuple[int, ...] = (20, 30, 40, 50)
DEFAULT_OUTPUT_DIR = BASE_DIR / "results" / "55maps-image-generalisation"

# 55-map run artefacts
D55_DETECTIONS = (
    BASE_DIR / "outputs" / "55maps-image-generalisation" / "verified"
    / "verified_detections.geojson"
)
D55_GT = BASE_DIR / "inputs" / "vectors" / "references" / "student-mounds-55maps.geojson"
D55_BOUNDS = (
    BASE_DIR / "inputs" / "vectors" / "bounds" / "384"
    / "55maps_evaluation_bounds.geojson"
)
D55_COST = BASE_DIR / "outputs" / "55maps-image-generalisation" / "cost_manifest.json"

# 4-map baseline: matched K=5 + PV config (plus-hp HIGH T=0.7, vote_t=3, prob_t=0.15)
D4_VERIFIED_DIR = (
    BASE_DIR / "outputs" / "h11" / "pv-diag-384"
    / "flash-high-image-n5" / "image-t0.7" / "verified-v1-n5"
)
D4_GT = BASE_DIR / "inputs" / "vectors" / "references" / "mounds-reference.geojson"
D4_BOUNDS = (
    BASE_DIR / "inputs" / "vectors" / "bounds" / "384"
    / "full_evaluation_bounds.geojson"
)

# Matched operating point — from the paper's headline image config
VOTE_THRESHOLD = 3
PROB_THRESHOLD = 0.15


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
@dataclass
class MapMetrics:
    """Per-map evaluation metrics at a single buffer."""

    map_name: str
    buffer_m: int
    n_tiles: int
    n_refs: int
    n_dets: int
    precision: float
    recall: float
    f1: float


def build_4map_detections(
    verified_dir: Path,
    vote_threshold: int,
    prob_threshold: float,
) -> gpd.GeoDataFrame:
    """Materialise the 4-map final detections at the matched operating point.

    Mirrors the launcher's ``_build_verified_geojson`` logic so the
    comparison uses an identical post-filtering pipeline. Produces a
    GeoDataFrame in EPSG:32635 with ``source_tile`` populated.
    """
    manifest = json.loads(
        (verified_dir / "crops" / "candidate_manifest.json").read_text(
            encoding="utf-8",
        ),
    )
    probs_data = json.loads(
        (verified_dir / "probabilities.json").read_text(encoding="utf-8"),
    )
    results = probs_data.get("results", {})

    rows: list[dict[str, Any]] = []
    for cand in manifest.get("candidates", []):
        cid = cand["candidate_id"]
        vote = cand.get("properties", {}).get("vote_count", 0)
        entry = results.get(f"candidate_{cid:05d}")
        if entry is None:
            continue
        prob = entry.get("mound_probability")
        if prob is None:
            continue
        if vote < vote_threshold or prob < prob_threshold:
            continue
        rows.append({
            "candidate_id": cid,
            "vote_count": vote,
            "probability": prob,
            "source_tile": cand.get("source_tile"),
            "centroid_x": cand["centroid_x"],
            "centroid_y": cand["centroid_y"],
        })

    if not rows:
        return gpd.GeoDataFrame(
            columns=["candidate_id", "source_tile", "geometry"],
            geometry="geometry", crs="EPSG:32635",
        )

    gdf = gpd.GeoDataFrame(
        rows,
        geometry=gpd.points_from_xy(
            [r["centroid_x"] for r in rows], [r["centroid_y"] for r in rows],
        ),
        crs="EPSG:32635",
    )
    return gdf


def split_by_map(
    gdf_bounds: gpd.GeoDataFrame,
) -> dict[str, gpd.GeoDataFrame]:
    """Group tile bounds by map name.

    Args:
        gdf_bounds: Tile-level bounds GeoDataFrame with ``tile_name`` column.

    Returns:
        Dict mapping map_name → subset of bounds for tiles of that map.
    """
    gdf_bounds = gdf_bounds.copy()
    gdf_bounds["map_name"] = gdf_bounds["tile_name"].apply(get_map_name)
    return {
        m: sub.reset_index(drop=True)
        for m, sub in gdf_bounds.groupby("map_name", sort=True)
    }


def _ref_map_col(gdf_refs: gpd.GeoDataFrame) -> str:
    """Return the name of the reference GeoDataFrame's map column.

    Mirrors the auto-detection in ``calculate_f1_internal`` — ``Map``
    for the gold-standard 4-map reference, ``source_map`` for the
    55-map student ground truth.
    """
    for candidate in ("Map", "source_map"):
        if candidate in gdf_refs.columns:
            return candidate
    raise ValueError(
        "Reference GeoDataFrame has no 'Map' or 'source_map' column. "
        f"Available columns: {list(gdf_refs.columns)}"
    )


def count_per_map(
    map_name: str,
    gdf_dets: gpd.GeoDataFrame,
    gdf_refs: gpd.GeoDataFrame,
    ref_map_col: str,
) -> tuple[int, int]:
    """Return ``(n_dets, n_refs)`` attributed to ``map_name``.

    Uses the SAME filters that ``calculate_f1_internal`` applies
    internally (string prefix on ``source_tile`` for detections;
    map-column match for references), so the counts reported by this
    script agree exactly with the counts that feed the F1 calculation.
    Spatial pre-filtering was removed (see /audit 2026-04-18).
    """
    n_dets = (
        int(gdf_dets["source_tile"].str.startswith(map_name).sum())
        if "source_tile" in gdf_dets.columns else 0
    )
    n_refs = int((gdf_refs[ref_map_col] == map_name).sum())
    return n_dets, n_refs


def evaluate_per_map(
    gdf_dets: gpd.GeoDataFrame,
    gdf_refs: gpd.GeoDataFrame,
    gdf_bounds: gpd.GeoDataFrame,
    buffers: tuple[int, ...],
) -> list[MapMetrics]:
    """Compute Hungarian-matched F1/P/R per map at each buffer.

    Args:
        gdf_dets: Final filtered detections (one GeoDataFrame).
        gdf_refs: Ground-truth mounds.
        gdf_bounds: Tile-level bounds covering all maps of interest.
        buffers: Tolerance buffers in metres.

    Returns:
        List of MapMetrics, one per (map, buffer) pair.
    """
    by_map = split_by_map(gdf_bounds)
    ref_map_col = _ref_map_col(gdf_refs)
    results: list[MapMetrics] = []
    for i, (map_name, tiles) in enumerate(sorted(by_map.items()), 1):
        n_dets, n_refs = count_per_map(
            map_name, gdf_dets, gdf_refs, ref_map_col,
        )
        logger.info(
            "[%d/%d] %s: tiles=%d, refs=%d, dets=%d",
            i, len(by_map), map_name, len(tiles), n_refs, n_dets,
        )
        for buf in buffers:
            # calculate_f1_internal scopes both dets and refs internally
            # to the maps present in the tile bounds, so we pass the
            # FULL dets and refs GeoDataFrames with only the map's
            # tile bounds. Pre-filtering is neither necessary nor
            # desirable (see audit 2026-04-18).
            p, r, f1 = calculate_f1_internal(
                gdf_dets, gdf_refs, tiles, buffer_metres=buf,
            )
            results.append(MapMetrics(
                map_name=map_name, buffer_m=buf,
                n_tiles=len(tiles), n_refs=n_refs, n_dets=n_dets,
                precision=round(p, 4),
                recall=round(r, 4),
                f1=round(f1, 4),
            ))
    return results


def summarise_distribution(
    metrics: list[MapMetrics], buffer: int,
) -> dict[str, float]:
    """Compute min/max/mean/median/SD/IQR for F1 across maps at a buffer."""
    f1s = [m.f1 for m in metrics if m.buffer_m == buffer]
    if not f1s:
        return {}
    sorted_f1s = sorted(f1s)
    n = len(sorted_f1s)
    # Quartiles via the "exclusive" percentile method (statistics.quantiles)
    qs = statistics.quantiles(sorted_f1s, n=4, method="exclusive") if n >= 4 else [0, 0, 0]
    q1, median, q3 = qs[0], qs[1], qs[2]
    return {
        "n_maps": n,
        "mean": round(statistics.mean(f1s), 4),
        "median": round(median, 4),
        "sd": round(statistics.stdev(f1s), 4) if n > 1 else 0.0,
        "q1": round(q1, 4),
        "q3": round(q3, 4),
        "iqr": round(q3 - q1, 4),
        "min": round(min(f1s), 4),
        "max": round(max(f1s), 4),
        "range": round(max(f1s) - min(f1s), 4),
    }


def identify_outliers(
    metrics: list[MapMetrics], buffer: int,
) -> tuple[list[str], list[str]]:
    """Return (low_outliers, high_outliers) per 1.5 × IQR rule at given buffer.

    Low outliers are maps where F1 < Q1 − 1.5 × IQR.
    High outliers are maps where F1 > Q3 + 1.5 × IQR.
    """
    at_buf = [m for m in metrics if m.buffer_m == buffer]
    f1s = [m.f1 for m in at_buf]
    if len(f1s) < 4:
        return [], []
    qs = statistics.quantiles(sorted(f1s), n=4, method="exclusive")
    q1, q3 = qs[0], qs[2]
    iqr = q3 - q1
    low_bound = q1 - 1.5 * iqr
    high_bound = q3 + 1.5 * iqr
    low = [m.map_name for m in at_buf if m.f1 < low_bound]
    high = [m.map_name for m in at_buf if m.f1 > high_bound]
    return sorted(low), sorted(high)


def compute_cost_correlation(
    metrics: list[MapMetrics], cost_per_map: dict[str, dict[str, Any]],
    buffer: int,
) -> dict[str, float]:
    """Pearson correlation of F1 with cost and candidate-count per map.

    Returns a dict with (coef_cost, coef_candidates, n) so that the
    heterogeneity summary can answer "does cost predict difficulty?".
    """
    at_buf = [m for m in metrics if m.buffer_m == buffer]
    costs: list[float] = []
    candidates: list[int] = []
    f1s: list[float] = []
    for m in at_buf:
        row = cost_per_map.get(m.map_name)
        if row is None:
            continue
        costs.append(float(row.get("total_cost_usd", 0.0)))
        candidates.append(int(row.get("candidates", 0)))
        f1s.append(m.f1)

    def pearson(xs: list[float], ys: list[float]) -> float:
        n = len(xs)
        if n < 2:
            return 0.0
        mx = sum(xs) / n
        my = sum(ys) / n
        num = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
        dx = sum((x - mx) ** 2 for x in xs) ** 0.5
        dy = sum((y - my) ** 2 for y in ys) ** 0.5
        if dx == 0 or dy == 0:
            return 0.0
        return num / (dx * dy)

    return {
        "coef_f1_vs_cost": round(pearson(costs, f1s), 4),
        "coef_f1_vs_candidates": round(pearson([float(c) for c in candidates], f1s), 4),
        "n": len(f1s),
    }


# ---------------------------------------------------------------------------
# Output formatters
# ---------------------------------------------------------------------------
def write_csv(path: Path, metrics: list[MapMetrics], dataset_label: str) -> None:
    """Write per-map × per-buffer metrics to a CSV file."""
    lines = [
        "dataset,map_name,buffer_m,n_tiles,n_refs,n_dets,"
        "precision,recall,f1",
    ]
    for m in metrics:
        lines.append(
            f"{dataset_label},{m.map_name},{m.buffer_m},"
            f"{m.n_tiles},{m.n_refs},{m.n_dets},"
            f"{m.precision},{m.recall},{m.f1}",
        )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def append_csv(path: Path, metrics: list[MapMetrics], dataset_label: str) -> None:
    """Append to an existing CSV (no header) so 55-map + 4-map share a file."""
    lines = []
    for m in metrics:
        lines.append(
            f"{dataset_label},{m.map_name},{m.buffer_m},"
            f"{m.n_tiles},{m.n_refs},{m.n_dets},"
            f"{m.precision},{m.recall},{m.f1}",
        )
    with path.open("a", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")


def write_summary_markdown(
    path: Path,
    d55_metrics: list[MapMetrics],
    d4_metrics: list[MapMetrics],
    d55_cost_corr: dict[int, dict[str, float]],
    buffers: tuple[int, ...],
) -> None:
    """Write a human-readable summary markdown with distributions + outliers."""
    lines: list[str] = [
        "# Per-Map Heterogeneity — 55-Map Image Generalisation",
        "",
        "Matched-configuration comparison between the 55 out-of-sample",
        "maps (headline run) and the 4 Era 2 calibration maps. Both use",
        f"plus-hp + HIGH + T=0.7 + K=5 + vote_t={VOTE_THRESHOLD} +",
        f"prob_t={PROB_THRESHOLD}.",
        "",
        "## 55-map distribution",
        "",
        "| Buffer | n | Mean F1 | Median | SD | IQR | Min | Max | Range |",
        "|-------:|--:|--------:|-------:|---:|----:|----:|----:|------:|",
    ]
    for buf in buffers:
        s = summarise_distribution(d55_metrics, buf)
        if not s:
            continue
        lines.append(
            f"| {buf} m | {s['n_maps']} | {s['mean']:.3f} | "
            f"{s['median']:.3f} | {s['sd']:.3f} | {s['iqr']:.3f} | "
            f"{s['min']:.3f} | {s['max']:.3f} | {s['range']:.3f} |"
        )
    lines.append("")

    lines += [
        "## 4-map baseline (Era 2 calibration)",
        "",
        "| Buffer | n | Mean F1 | Median | SD | IQR | Min | Max | Range |",
        "|-------:|--:|--------:|-------:|---:|----:|----:|----:|------:|",
    ]
    for buf in buffers:
        s = summarise_distribution(d4_metrics, buf)
        if not s:
            continue
        lines.append(
            f"| {buf} m | {s['n_maps']} | {s['mean']:.3f} | "
            f"{s['median']:.3f} | {s['sd']:.3f} | {s['iqr']:.3f} | "
            f"{s['min']:.3f} | {s['max']:.3f} | {s['range']:.3f} |"
        )
    lines.append("")

    lines += [
        "## Outliers in the 55-map set (1.5 × IQR rule)",
        "",
    ]
    for buf in buffers:
        lo, hi = identify_outliers(d55_metrics, buf)
        lines.append(f"**@ {buf} m buffer**")
        lines.append(
            f"- Low (struggling) maps: {', '.join(lo) if lo else '(none)'}"
        )
        lines.append(
            f"- High (easy) maps: {', '.join(hi) if hi else '(none)'}"
        )
        lines.append("")

    lines += [
        "## Cost / difficulty correlation (55-map run)",
        "",
        "| Buffer | Pearson r (F1 vs total cost) | Pearson r (F1 vs candidates) |",
        "|-------:|-----------------------------:|-----------------------------:|",
    ]
    for buf in buffers:
        corr = d55_cost_corr.get(buf, {})
        lines.append(
            f"| {buf} m | {corr.get('coef_f1_vs_cost', 0):+.3f} | "
            f"{corr.get('coef_f1_vs_candidates', 0):+.3f} |"
        )
    lines.append("")

    # Per-map F1 table at the tightest and loosest buffers requested
    # (typically 20 m and 50 m, but handles arbitrary --buffers flags).
    tight_buf = min(buffers)
    loose_buf = max(buffers)
    lines += [
        f"## Per-map F1 table ({tight_buf} m and {loose_buf} m buffers)",
        "",
        f"| Dataset | Map | Tiles | Refs | Dets | F1@{tight_buf}m | F1@{loose_buf}m |",
        "|---------|-----|------:|-----:|-----:|------:|------:|",
    ]
    for dataset_label, metrics in (("55-map", d55_metrics), ("4-map", d4_metrics)):
        by_map: dict[str, dict[int, MapMetrics]] = {}
        for m in metrics:
            by_map.setdefault(m.map_name, {})[m.buffer_m] = m
        for map_name in sorted(by_map):
            m_tight = by_map[map_name].get(tight_buf)
            m_loose = by_map[map_name].get(loose_buf)
            if m_tight is None or m_loose is None:
                continue
            lines.append(
                f"| {dataset_label} | {map_name} | {m_tight.n_tiles} | "
                f"{m_tight.n_refs} | {m_tight.n_dets} | "
                f"{m_tight.f1:.3f} | {m_loose.f1:.3f} |"
            )
    lines.append("")

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def write_summary_json(
    path: Path,
    d55_metrics: list[MapMetrics],
    d4_metrics: list[MapMetrics],
    d55_cost_corr: dict[int, dict[str, float]],
    buffers: tuple[int, ...],
) -> None:
    """Write a machine-readable summary alongside the markdown."""
    payload = {
        "version": __version__,
        "vote_threshold": VOTE_THRESHOLD,
        "prob_threshold": PROB_THRESHOLD,
        "buffers": list(buffers),
        "dataset_55map": {
            "n_maps": len({m.map_name for m in d55_metrics}),
            "distribution": {
                buf: summarise_distribution(d55_metrics, buf) for buf in buffers
            },
            "outliers_by_buffer": {
                buf: {
                    "low": identify_outliers(d55_metrics, buf)[0],
                    "high": identify_outliers(d55_metrics, buf)[1],
                }
                for buf in buffers
            },
            "cost_correlation": d55_cost_corr,
        },
        "dataset_4map": {
            "n_maps": len({m.map_name for m in d4_metrics}),
            "distribution": {
                buf: summarise_distribution(d4_metrics, buf) for buf in buffers
            },
        },
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main() -> int:
    parser = argparse.ArgumentParser(
        description="Per-map heterogeneity analysis for the 55-map "
                    "image generalisation run.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument(
        "--buffers", type=int, nargs="+", default=list(DEFAULT_BUFFERS),
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    args = parser.parse_args()

    buffers = tuple(args.buffers)
    args.output_dir.mkdir(parents=True, exist_ok=True)

    # -----------------------------------------------------------------
    # 55-map analysis
    # -----------------------------------------------------------------
    logger.info("Loading 55-map artefacts...")
    d55_dets = load_geojson(D55_DETECTIONS)
    d55_refs = load_geojson(D55_GT)
    d55_bounds = load_geojson(D55_BOUNDS)
    logger.info(
        "55-map: %d detections, %d references, %d tile bounds",
        len(d55_dets), len(d55_refs), len(d55_bounds),
    )

    d55_metrics = evaluate_per_map(
        d55_dets, d55_refs, d55_bounds, buffers,
    )

    # Cost correlation — only applies to the 55-map run
    cost_manifest = json.loads(D55_COST.read_text(encoding="utf-8"))
    cost_per_map = {row["map_id"]: row for row in cost_manifest.get("per_map", [])}
    d55_cost_corr = {
        buf: compute_cost_correlation(d55_metrics, cost_per_map, buf)
        for buf in buffers
    }

    # -----------------------------------------------------------------
    # 4-map baseline
    # -----------------------------------------------------------------
    logger.info("Building 4-map baseline at matched operating point...")
    d4_dets = build_4map_detections(
        D4_VERIFIED_DIR, VOTE_THRESHOLD, PROB_THRESHOLD,
    )
    d4_refs = load_geojson(D4_GT)
    d4_bounds = load_geojson(D4_BOUNDS)
    logger.info(
        "4-map: %d detections (after vote+prob filter), %d references, "
        "%d tile bounds", len(d4_dets), len(d4_refs), len(d4_bounds),
    )

    d4_metrics = evaluate_per_map(d4_dets, d4_refs, d4_bounds, buffers)

    # -----------------------------------------------------------------
    # Write outputs
    # -----------------------------------------------------------------
    csv_path = args.output_dir / "per_map_metrics.csv"
    md_path = args.output_dir / "per_map_summary.md"
    json_path = args.output_dir / "heterogeneity_summary.json"

    write_csv(csv_path, d55_metrics, "55-map")
    append_csv(csv_path, d4_metrics, "4-map")
    logger.info("CSV: %s", csv_path)

    write_summary_markdown(
        md_path, d55_metrics, d4_metrics, d55_cost_corr, buffers,
    )
    logger.info("Markdown: %s", md_path)

    write_summary_json(
        json_path, d55_metrics, d4_metrics, d55_cost_corr, buffers,
    )
    logger.info("JSON: %s", json_path)

    # -----------------------------------------------------------------
    # Console summary
    # -----------------------------------------------------------------
    print("\n=== 55-map F1 distribution ===")
    for buf in buffers:
        s = summarise_distribution(d55_metrics, buf)
        print(
            f"  @ {buf:>2} m: mean={s.get('mean', 0):.3f}  "
            f"median={s.get('median', 0):.3f}  "
            f"SD={s.get('sd', 0):.3f}  "
            f"range=[{s.get('min', 0):.3f}, {s.get('max', 0):.3f}]"
        )
    print("\n=== 4-map F1 distribution ===")
    for buf in buffers:
        s = summarise_distribution(d4_metrics, buf)
        print(
            f"  @ {buf:>2} m: mean={s.get('mean', 0):.3f}  "
            f"median={s.get('median', 0):.3f}  "
            f"SD={s.get('sd', 0):.3f}  "
            f"range=[{s.get('min', 0):.3f}, {s.get('max', 0):.3f}]"
        )
    print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
