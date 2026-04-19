#!/usr/bin/env python3
"""
Compute nearest-neighbour (NN) distance distribution for ground-truth burial
mounds on the four gold-standard reference maps.

Purpose
-------
On the 55-map text HIGH run, the F1 score plateaus at ~40-50 m IoU-buffer
diameter. This analysis quantifies how close the inter-mound spacing on the
gold-standard maps comes to the danger zone where match-zone overlap introduces
matching ambiguity (one prediction can legitimately match two nearby truths, or
vice versa).

Inputs (all EPSG:32635, UTM Zone 35N — metric, Bulgaria)
-------------------------------------------------------
- inputs/vectors/references/reference_K-35-052-4_32635.geojson   (136 mounds)
- inputs/vectors/references/reference_K-35-053-3_Elenovo.geojson (217 mounds)
- inputs/vectors/references/reference_K-35-062-2_Rakovski.geojson (196 mounds)
- inputs/vectors/references/reference_K-35-078-1_Lesovo.geojson   (20 mounds)

Outputs
-------
- spacing-summary.json  — structured data (per-map + pooled)
- spacing-report.md     — human-readable tables and commentary

Usage
-----
    /home/shawn/Code/map-reader-llm/.venv/bin/python compute_spacing.py

Notes
-----
- NN distance is defined *within each map* (pooled NN is the concatenation of
  those per-map NN distances, not cross-map distances which would be
  meaningless because each map is a disjoint geographic sheet).
- Geometries are MultiPoint with single-point members — we extract the
  representative point for distance calculations.
"""

from __future__ import annotations

import json
from pathlib import Path

import geopandas as gpd
import numpy as np
from scipy.spatial import cKDTree

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

REFERENCE_DIR = Path(
    "/home/shawn/Code/map-reader-llm/inputs/vectors/references"
)
OUTPUT_DIR = Path(
    "/home/shawn/Code/map-reader-llm/results/gt-spacing-analysis/gold-standard"
)

# Four gold-standard reference maps and their file paths.
PER_MAP_FILES: dict[str, str] = {
    "K-35-052-4": "reference_K-35-052-4_32635.geojson",
    "K-35-053-3_Elenovo": "reference_K-35-053-3_Elenovo.geojson",
    "K-35-062-2_Rakovski": "reference_K-35-062-2_Rakovski.geojson",
    "K-35-078-1_Lesovo": "reference_K-35-078-1_Lesovo.geojson",
}

# Buffer thresholds relevant to the match-zone overlap concern (metres).
BUFFER_THRESHOLDS_M = [20, 30, 50, 70, 100]

# Histogram bin edges (10 m bins from 0-200 m).
HIST_BIN_EDGES = np.arange(0, 210, 10)  # 0,10,20,...,200


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def extract_xy(gdf: gpd.GeoDataFrame) -> np.ndarray:
    """
    Extract (x, y) coordinate array from a GeoDataFrame whose geometries are
    MultiPoint (single-point) or Point.

    Parameters
    ----------
    gdf : geopandas.GeoDataFrame
        Input layer in a metric CRS.

    Returns
    -------
    numpy.ndarray of shape (n, 2)
        Coordinate array in metres.
    """
    coords = []
    for geom in gdf.geometry:
        if geom is None or geom.is_empty:
            continue
        if geom.geom_type == "Point":
            coords.append((geom.x, geom.y))
        elif geom.geom_type == "MultiPoint":
            # Use the first point — reference layers have singleton MultiPoints.
            pts = list(geom.geoms)
            if len(pts) != 1:
                # Defensive: record centroid instead if multipoint is genuine.
                c = geom.centroid
                coords.append((c.x, c.y))
            else:
                coords.append((pts[0].x, pts[0].y))
        else:
            # Fallback: use centroid
            c = geom.centroid
            coords.append((c.x, c.y))
    return np.asarray(coords, dtype=float)


def nearest_neighbour_distances(coords: np.ndarray) -> np.ndarray:
    """
    Compute nearest-neighbour distance for every point in ``coords``.

    Uses a kd-tree; the nearest neighbour is the second entry (k=2) because
    the first is the point itself at distance zero.

    Parameters
    ----------
    coords : numpy.ndarray of shape (n, 2)
        Planar coordinates in metres.

    Returns
    -------
    numpy.ndarray of shape (n,)
        NN distances in metres. Returns an empty array if n < 2.
    """
    if coords.shape[0] < 2:
        return np.array([], dtype=float)
    tree = cKDTree(coords)
    dists, _ = tree.query(coords, k=2)
    return dists[:, 1]


def percentile_summary(nn: np.ndarray) -> dict:
    """
    Summarise a vector of NN distances with common descriptive statistics.

    Parameters
    ----------
    nn : numpy.ndarray
        NN distances in metres.

    Returns
    -------
    dict
        Summary statistics (all metres; ``n`` and counts are dimensionless).
    """
    if nn.size == 0:
        return {"n": 0}
    pcts = [5, 10, 25, 50, 75, 90, 95]
    out = {
        "n": int(nn.size),
        "min_m": float(np.min(nn)),
        "max_m": float(np.max(nn)),
        "mean_m": float(np.mean(nn)),
        "std_m": float(np.std(nn, ddof=1)) if nn.size > 1 else 0.0,
    }
    for p in pcts:
        out[f"p{p:02d}_m"] = float(np.percentile(nn, p))
    return out


def threshold_counts(nn: np.ndarray, thresholds: list[int]) -> dict:
    """
    Count and fraction of NN distances strictly below each threshold.

    Parameters
    ----------
    nn : numpy.ndarray
        NN distances in metres.
    thresholds : list of int
        Threshold values in metres.

    Returns
    -------
    dict
        Keyed by ``'lt_{t}m'`` for each threshold.
    """
    out = {}
    n = nn.size
    for t in thresholds:
        cnt = int(np.sum(nn < t))
        out[f"lt_{t}m"] = {
            "count": cnt,
            "fraction": float(cnt / n) if n > 0 else 0.0,
        }
    return out


def histogram_counts(nn: np.ndarray, bin_edges: np.ndarray) -> dict:
    """
    Produce histogram counts for the 10 m bins spanning 0-200 m plus an
    overflow bin for distances >= 200 m.

    Parameters
    ----------
    nn : numpy.ndarray
        NN distances in metres.
    bin_edges : numpy.ndarray
        Bin edges (left-inclusive, right-exclusive except the last).

    Returns
    -------
    dict
        ``bin_edges``, ``counts`` (list of 20), ``overflow_ge_200m``.
    """
    # np.histogram treats the last bin as right-inclusive; we want a separate
    # overflow count for distances >= 200 m, so clip the main histogram.
    in_range = nn[nn < bin_edges[-1]]
    counts, _ = np.histogram(in_range, bins=bin_edges)
    overflow = int(np.sum(nn >= bin_edges[-1]))
    return {
        "bin_edges_m": bin_edges.tolist(),
        "counts": counts.astype(int).tolist(),
        "overflow_ge_200m": overflow,
    }


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    """Compute NN statistics per map and pooled, then write outputs."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    per_map_results: dict[str, dict] = {}
    pooled_nn: list[np.ndarray] = []
    pooled_counts = 0

    for map_key, filename in PER_MAP_FILES.items():
        path = REFERENCE_DIR / filename
        gdf = gpd.read_file(path)

        # Confirm metric CRS; reproject if needed (shouldn't be — all inputs
        # are EPSG:32635 — but the guard documents the intent).
        crs_str = str(gdf.crs)
        if gdf.crs is None or gdf.crs.is_geographic:
            gdf = gdf.to_crs("EPSG:32635")
            crs_str = f"{crs_str} -> EPSG:32635 (reprojected)"

        coords = extract_xy(gdf)
        nn = nearest_neighbour_distances(coords)
        pooled_nn.append(nn)
        pooled_counts += coords.shape[0]

        per_map_results[map_key] = {
            "source_file": str(path.relative_to(REFERENCE_DIR.parents[2])),
            "crs": crs_str,
            "n_mounds": int(coords.shape[0]),
            "summary": percentile_summary(nn),
            "threshold_counts": threshold_counts(nn, BUFFER_THRESHOLDS_M),
            "histogram": histogram_counts(nn, HIST_BIN_EDGES),
        }

    # Pooled distribution = concatenation of per-map NN distances.
    # (Cross-map distances are meaningless; each map is a disjoint sheet.)
    pooled = np.concatenate(pooled_nn) if pooled_nn else np.array([])
    pooled_block = {
        "n_mounds": int(pooled_counts),
        "n_nn_observations": int(pooled.size),
        "summary": percentile_summary(pooled),
        "threshold_counts": threshold_counts(pooled, BUFFER_THRESHOLDS_M),
        "histogram": histogram_counts(pooled, HIST_BIN_EDGES),
    }

    output = {
        "analysis": "Ground-truth nearest-neighbour spacing (gold-standard maps)",
        "crs": "EPSG:32635 (UTM Zone 35N — metric)",
        "nn_definition": (
            "Within-map nearest-neighbour distance in metres. Pooled NN "
            "distribution concatenates per-map NN vectors (no cross-map pairs)."
        ),
        "buffer_thresholds_m": BUFFER_THRESHOLDS_M,
        "per_map": per_map_results,
        "pooled": pooled_block,
    }

    json_path = OUTPUT_DIR / "spacing-summary.json"
    json_path.write_text(json.dumps(output, indent=2))
    print(f"Wrote {json_path}")

    md_path = OUTPUT_DIR / "spacing-report.md"
    md_path.write_text(render_report(output))
    print(f"Wrote {md_path}")


def render_report(output: dict) -> str:
    """
    Render a Markdown report summarising the NN distribution.

    Parameters
    ----------
    output : dict
        The structured summary returned by :func:`main`.

    Returns
    -------
    str
        Markdown text.
    """
    lines: list[str] = []
    lines.append("# Ground-truth nearest-neighbour spacing — gold-standard maps")
    lines.append("")
    lines.append(
        "Inter-mound nearest-neighbour (NN) distances on the four gold-standard "
        "reference maps. All coordinates are in EPSG:32635 (UTM Zone 35N, metric, "
        "Bulgaria). NN distances are computed *within each map*; the pooled "
        "distribution concatenates per-map NN vectors."
    )
    lines.append("")
    lines.append(
        "**Motivation.** On the 55-map text HIGH run the F1 score plateaus at "
        "~40-50 m IoU-buffer diameter. If inter-mound spacing approaches the "
        "buffer diameter, match-zone overlap introduces matching ambiguity "
        "(one prediction may legitimately sit inside two truth buffers). This "
        "analysis quantifies how close we are to that danger zone."
    )
    lines.append("")

    # ---- Summary table (percentiles) ------------------------------------
    lines.append("## Distribution summary (metres)")
    lines.append("")
    lines.append(
        "| Map | n | min | p05 | p10 | p25 | p50 | p75 | p90 | p95 | max | mean | std |"
    )
    lines.append(
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |"
    )
    for map_key, block in output["per_map"].items():
        s = block["summary"]
        if s["n"] == 0:
            lines.append(f"| {map_key} | 0 | - | - | - | - | - | - | - | - | - | - | - |")
            continue
        lines.append(
            "| {map} | {n} | {mn:.1f} | {p05:.1f} | {p10:.1f} | {p25:.1f} | {p50:.1f} "
            "| {p75:.1f} | {p90:.1f} | {p95:.1f} | {mx:.1f} | {mean:.1f} | {std:.1f} |".format(
                map=map_key,
                n=s["n"],
                mn=s["min_m"],
                p05=s["p05_m"],
                p10=s["p10_m"],
                p25=s["p25_m"],
                p50=s["p50_m"],
                p75=s["p75_m"],
                p90=s["p90_m"],
                p95=s["p95_m"],
                mx=s["max_m"],
                mean=s["mean_m"],
                std=s["std_m"],
            )
        )
    ps = output["pooled"]["summary"]
    if ps["n"] > 0:
        lines.append(
            "| **Pooled** | **{n}** | **{mn:.1f}** | **{p05:.1f}** | **{p10:.1f}** "
            "| **{p25:.1f}** | **{p50:.1f}** | **{p75:.1f}** | **{p90:.1f}** "
            "| **{p95:.1f}** | **{mx:.1f}** | **{mean:.1f}** | **{std:.1f}** |".format(
                n=ps["n"],
                mn=ps["min_m"],
                p05=ps["p05_m"],
                p10=ps["p10_m"],
                p25=ps["p25_m"],
                p50=ps["p50_m"],
                p75=ps["p75_m"],
                p90=ps["p90_m"],
                p95=ps["p95_m"],
                mx=ps["max_m"],
                mean=ps["mean_m"],
                std=ps["std_m"],
            )
        )
    lines.append("")

    # ---- Threshold table ------------------------------------------------
    lines.append("## Mounds with NN distance below buffer thresholds")
    lines.append("")
    lines.append(
        "Counts (and fraction of map total) of mounds whose nearest neighbour "
        "lies within each buffer threshold. A mound with NN < buffer diameter "
        "shares its match zone with at least one other ground-truth mound."
    )
    lines.append("")
    thresholds = output["buffer_thresholds_m"]
    header = "| Map | n |" + "".join(f" < {t} m |" for t in thresholds)
    lines.append(header)
    sep = "| --- | ---: |" + " ---: |" * len(thresholds)
    lines.append(sep)
    for map_key, block in output["per_map"].items():
        n = block["n_mounds"]
        row = f"| {map_key} | {n} |"
        for t in thresholds:
            c = block["threshold_counts"][f"lt_{t}m"]
            row += f" {c['count']} ({c['fraction']*100:.1f}%) |"
        lines.append(row)
    # Pooled row
    pn = output["pooled"]["n_nn_observations"]
    row = f"| **Pooled** | **{pn}** |"
    for t in thresholds:
        c = output["pooled"]["threshold_counts"][f"lt_{t}m"]
        row += f" **{c['count']} ({c['fraction']*100:.1f}%)** |"
    lines.append(row)
    lines.append("")

    # ---- Histogram table ------------------------------------------------
    lines.append("## NN distance histogram — 10 m bins")
    lines.append("")
    lines.append(
        "Counts per 10 m bin from 0-200 m. The final column reports the "
        "overflow (NN >= 200 m)."
    )
    lines.append("")
    bin_edges = output["pooled"]["histogram"]["bin_edges_m"]
    bin_labels = [
        f"{int(bin_edges[i])}-{int(bin_edges[i+1])}"
        for i in range(len(bin_edges) - 1)
    ]
    header = "| Map |" + "".join(f" {lab} |" for lab in bin_labels) + " >=200 |"
    lines.append(header)
    sep = "| --- |" + " ---: |" * (len(bin_labels) + 1)
    lines.append(sep)
    for map_key, block in output["per_map"].items():
        counts = block["histogram"]["counts"]
        overflow = block["histogram"]["overflow_ge_200m"]
        row = f"| {map_key} |" + "".join(f" {c} |" for c in counts) + f" {overflow} |"
        lines.append(row)
    counts = output["pooled"]["histogram"]["counts"]
    overflow = output["pooled"]["histogram"]["overflow_ge_200m"]
    row = "| **Pooled** |" + "".join(f" **{c}** |" for c in counts) + f" **{overflow}** |"
    lines.append(row)
    lines.append("")

    # ---- Commentary -----------------------------------------------------
    lines.append("## Headline interpretation")
    lines.append("")
    if ps["n"] > 0:
        p50 = ps["p50_m"]
        p05 = ps["p05_m"]
        frac_lt_50 = output["pooled"]["threshold_counts"]["lt_50m"]["fraction"] * 100
        frac_lt_100 = output["pooled"]["threshold_counts"]["lt_100m"]["fraction"] * 100
        lines.append(
            f"- Pooled median NN distance: **{p50:.1f} m**; tight tail (5th "
            f"percentile): **{p05:.1f} m**."
        )
        lines.append(
            f"- **{frac_lt_50:.1f}%** of mounds have a nearest neighbour within "
            f"50 m (the operating point where the F1 plateau emerges); "
            f"**{frac_lt_100:.1f}%** are within 100 m."
        )
    lines.append("")
    lines.append(
        "Interpret the match-zone overlap risk by comparing the NN distance "
        "against twice the buffer radius (i.e. the buffer *diameter*). For a "
        "50 m buffer diameter (25 m radius), truth buffers begin to overlap "
        "when NN < 50 m; at NN < 25 m, truth centres lie inside each other's "
        "buffers."
    )
    lines.append("")
    return "\n".join(lines)


if __name__ == "__main__":
    main()
