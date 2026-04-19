#!/usr/bin/env python3
"""
Compute the nearest-neighbour (NN) distance distribution among ground-truth
burial mounds on the 55-map student-annotated generalisation corpus.

Purpose
-------
On the 55-map text HIGH generalisation run, the F1 score plateaus at ~40-50 m
IoU-buffer diameter. The user has hypothesised that match-zone overlap could
kick in if inter-mound spacing is small enough. A parallel analysis on the
four gold-standard reference maps found sparse spacing (pooled median 449 m,
p05 83 m, 0% of mounds within 50 m). This analysis applies the same
methodology to the 55-map student-annotated GT — the corpus the text HIGH
run was actually evaluated against — to determine whether the 55-map data
tells a different story.

Inputs
------
- inputs/vectors/references/student-mounds-55maps.geojson
  Point geometries in EPSG:32635 (UTM Zone 35N), 4,770 rows across 55 maps.
  Rows are grouped by the ``source_map`` property (no bounds-based spatial
  assignment needed). Note that FeatureType is mostly "Mound" but includes
  a small number of "Surface feature" / "Other" / "NA" rows — the full 4,770
  rows are retained because the evaluation pipeline does not filter by
  FeatureType and F1 is measured against the same union.

Outputs
-------
- spacing-summary.json  — structured data (per-map + pooled)
- spacing-report.md     — human-readable tables + commentary

Usage
-----
    /home/shawn/Code/map-reader-llm/.venv/bin/python compute_spacing.py

Notes
-----
- NN distance is defined *within each map*. The pooled NN distribution is
  the concatenation of per-map NN vectors; no cross-map pairs are computed
  (distinct sheets are geographically disjoint and cross-map distances would
  be an artefact of sheet layout).
- The histogram uses 10 m bins from 0-500 m plus an overflow bin (>=500 m).
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

GT_PATH = Path(
    "/home/shawn/Code/map-reader-llm/inputs/vectors/references/"
    "student-mounds-55maps.geojson"
)
OUTPUT_DIR = Path(
    "/home/shawn/Code/map-reader-llm/results/gt-spacing-analysis/55maps-student"
)

# Column in the GT GeoJSON used to partition points into per-map groups.
MAP_ID_COL = "source_map"

# Buffer thresholds relevant to the match-zone overlap concern (metres).
BUFFER_THRESHOLDS_M = [20, 30, 50, 70, 100]

# Histogram bin edges (10 m bins from 0-500 m, plus an overflow bin >=500 m).
HIST_BIN_EDGES = np.arange(0, 510, 10)  # 0,10,...,500

# Number of "tightest" maps to list in the summary.
TIGHTEST_N = 5


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def extract_xy(gdf: gpd.GeoDataFrame) -> np.ndarray:
    """
    Extract (x, y) coordinate array from a GeoDataFrame whose geometries are
    Point, MultiPoint (single-point), or polygonal (falls back to centroid).

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
            pts = list(geom.geoms)
            if len(pts) != 1:
                c = geom.centroid
                coords.append((c.x, c.y))
            else:
                coords.append((pts[0].x, pts[0].y))
        else:
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
        Summary statistics (all metres; ``n`` is dimensionless).
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
    Produce histogram counts for 10 m bins 0-500 m plus an overflow bin.

    Parameters
    ----------
    nn : numpy.ndarray
        NN distances in metres.
    bin_edges : numpy.ndarray
        Bin edges (left-inclusive, right-exclusive).

    Returns
    -------
    dict
        ``bin_edges_m``, ``counts`` (list of 50), ``overflow_ge_500m``.
    """
    in_range = nn[nn < bin_edges[-1]]
    counts, _ = np.histogram(in_range, bins=bin_edges)
    overflow = int(np.sum(nn >= bin_edges[-1]))
    return {
        "bin_edges_m": bin_edges.tolist(),
        "counts": counts.astype(int).tolist(),
        "overflow_ge_500m": overflow,
    }


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    """Compute NN statistics per map and pooled, then write outputs."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    gdf_all = gpd.read_file(GT_PATH)

    # Confirm metric CRS; reproject if the file turns out to be geographic.
    # The student GT is known to be EPSG:32635, but the guard documents intent.
    crs_str = str(gdf_all.crs)
    if gdf_all.crs is None or gdf_all.crs.is_geographic:
        gdf_all = gdf_all.to_crs("EPSG:32635")
        crs_str = f"{crs_str} -> EPSG:32635 (reprojected)"

    # FeatureType breakdown — documented because the pool is not pure "Mound".
    feature_type_counts = (
        gdf_all["FeatureType"].value_counts(dropna=False).to_dict()
    )
    feature_type_counts = {str(k): int(v) for k, v in feature_type_counts.items()}

    per_map_results: dict[str, dict] = {}
    pooled_nn: list[np.ndarray] = []
    pooled_counts = 0

    # Process each map individually; sort for stable JSON ordering.
    map_ids = sorted(gdf_all[MAP_ID_COL].unique())
    for map_id in map_ids:
        gdf_map = gdf_all[gdf_all[MAP_ID_COL] == map_id]
        coords = extract_xy(gdf_map)
        nn = nearest_neighbour_distances(coords)
        pooled_nn.append(nn)
        pooled_counts += coords.shape[0]

        per_map_results[map_id] = {
            "n_mounds": int(coords.shape[0]),
            "n_nn_observations": int(nn.size),
            "summary": percentile_summary(nn),
            "threshold_counts": threshold_counts(nn, BUFFER_THRESHOLDS_M),
            "histogram": histogram_counts(nn, HIST_BIN_EDGES),
        }

    # Pooled distribution = concatenation of per-map NN distances.
    pooled = (
        np.concatenate(pooled_nn) if pooled_nn else np.array([], dtype=float)
    )
    pooled_block = {
        "n_mounds": int(pooled_counts),
        "n_nn_observations": int(pooled.size),
        "summary": percentile_summary(pooled),
        "threshold_counts": threshold_counts(pooled, BUFFER_THRESHOLDS_M),
        "histogram": histogram_counts(pooled, HIST_BIN_EDGES),
    }

    # Tightest maps: lowest p05, restricted to maps with enough points to
    # compute a meaningful p05 (n >= 2 is sufficient for the kd-tree, but p05
    # is only informative once n >= 20 or so — we still rank all n>=2 maps
    # and document the n alongside).
    tightest = rank_tightest_maps(per_map_results, n=TIGHTEST_N)

    output = {
        "analysis": "Ground-truth nearest-neighbour spacing (55-map student GT)",
        "source_file": str(GT_PATH.relative_to(GT_PATH.parents[4])),
        "crs": crs_str,
        "nn_definition": (
            "Within-map nearest-neighbour distance in metres. Pooled NN "
            "distribution concatenates per-map NN vectors (no cross-map pairs)."
        ),
        "feature_type_breakdown": feature_type_counts,
        "feature_type_note": (
            "The analysis retains all 4,770 rows (including 'Surface feature', "
            "'Other', 'NA') because the evaluation pipeline does not filter by "
            "FeatureType — the F1 scores under review measure predictions "
            "against this same union."
        ),
        "buffer_thresholds_m": BUFFER_THRESHOLDS_M,
        "n_maps": len(map_ids),
        "per_map": per_map_results,
        "pooled": pooled_block,
        "tightest_maps_by_p05": tightest,
    }

    json_path = OUTPUT_DIR / "spacing-summary.json"
    json_path.write_text(json.dumps(output, indent=2))
    print(f"Wrote {json_path}")

    md_path = OUTPUT_DIR / "spacing-report.md"
    md_path.write_text(render_report(output))
    print(f"Wrote {md_path}")


def rank_tightest_maps(per_map: dict, n: int) -> list[dict]:
    """
    Return the ``n`` maps with the lowest p05 NN distance.

    Maps with fewer than two mounds (no NN distance computable) are excluded.
    Ties are broken by lower median, then lower minimum, then map id.

    Parameters
    ----------
    per_map : dict
        The per-map results block.
    n : int
        Number of tightest maps to return.

    Returns
    -------
    list of dict
        Each entry carries ``map_id``, ``n_mounds``, ``p05_m``, ``p50_m``,
        ``min_m``, ``frac_lt_50m``, ``frac_lt_100m``.
    """
    rows: list[tuple] = []
    for map_id, block in per_map.items():
        s = block["summary"]
        if s.get("n", 0) < 1:
            continue
        p05 = s.get("p05_m")
        p50 = s.get("p50_m")
        mn = s.get("min_m")
        if p05 is None:
            continue
        rows.append((p05, p50, mn, map_id, block))
    rows.sort(key=lambda r: (r[0], r[1], r[2], r[3]))
    out: list[dict] = []
    for p05, p50, mn, map_id, block in rows[:n]:
        out.append({
            "map_id": map_id,
            "n_mounds": block["n_mounds"],
            "min_m": float(mn),
            "p05_m": float(p05),
            "p50_m": float(p50),
            "frac_lt_50m": (
                block["threshold_counts"]["lt_50m"]["fraction"]
            ),
            "frac_lt_100m": (
                block["threshold_counts"]["lt_100m"]["fraction"]
            ),
        })
    return out


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
    lines.append("# Ground-truth nearest-neighbour spacing — 55-map student GT")
    lines.append("")
    lines.append(
        "Inter-mound nearest-neighbour (NN) distances on the 55-map "
        "student-annotated ground truth used to evaluate the 55-map text HIGH "
        "generalisation run. All coordinates are in EPSG:32635 (UTM Zone 35N, "
        "metric, Bulgaria). NN distances are computed *within each map*; the "
        "pooled distribution concatenates per-map NN vectors."
    )
    lines.append("")
    lines.append(
        "**Motivation.** On the 55-map text HIGH run the F1 score plateaus at "
        "~40-50 m IoU-buffer diameter. A parallel analysis on the four "
        "gold-standard reference maps found very sparse spacing (pooled "
        "median 449.5 m, p05 83.2 m, 0.0% of mounds within 50 m, 10.0% within "
        "100 m). If the 55-map student GT exhibits tighter spacing, match-zone "
        "overlap becomes a credible explanation for the plateau."
    )
    lines.append("")

    # ---- FeatureType breakdown ------------------------------------------
    lines.append("## Input summary")
    lines.append("")
    ft = output["feature_type_breakdown"]
    lines.append(f"- Source: `{output['source_file']}`")
    lines.append(f"- CRS: `{output['crs']}`")
    lines.append(f"- Maps: **{output['n_maps']}**")
    lines.append(f"- Total rows: **{output['pooled']['n_mounds']}**")
    lines.append("- FeatureType breakdown: " + ", ".join(
        f"`{k}`={v}" for k, v in sorted(ft.items(), key=lambda kv: -kv[1])
    ))
    lines.append("")
    lines.append(output["feature_type_note"])
    lines.append("")

    # ---- Pooled summary up front ----------------------------------------
    ps = output["pooled"]["summary"]
    lines.append("## Pooled distribution (headline)")
    lines.append("")
    lines.append(
        "| n | min | p05 | p10 | p25 | p50 | p75 | p90 | p95 | max | mean | std |"
    )
    lines.append(
        "| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |"
    )
    if ps["n"] > 0:
        lines.append(
            "| **{n}** | **{mn:.1f}** | **{p05:.1f}** | **{p10:.1f}** "
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

    # ---- Threshold table (pooled + per-map) ------------------------------
    lines.append("## Mounds with NN distance below buffer thresholds")
    lines.append("")
    lines.append(
        "Counts (and fraction of map total) of mounds whose nearest neighbour "
        "lies strictly within each buffer threshold. A mound with NN < buffer "
        "diameter shares its match zone with at least one other ground-truth "
        "mound."
    )
    lines.append("")
    thresholds = output["buffer_thresholds_m"]
    header = "| Map | n |" + "".join(f" < {t} m |" for t in thresholds)
    lines.append(header)
    sep = "| --- | ---: |" + " ---: |" * len(thresholds)
    lines.append(sep)
    # Pooled first for at-a-glance headline.
    pn = output["pooled"]["n_nn_observations"]
    row = f"| **Pooled** | **{pn}** |"
    for t in thresholds:
        c = output["pooled"]["threshold_counts"][f"lt_{t}m"]
        row += f" **{c['count']} ({c['fraction']*100:.1f}%)** |"
    lines.append(row)
    for map_id, block in output["per_map"].items():
        n = block["n_mounds"]
        row = f"| {map_id} | {n} |"
        for t in thresholds:
            c = block["threshold_counts"][f"lt_{t}m"]
            row += f" {c['count']} ({c['fraction']*100:.1f}%) |"
        lines.append(row)
    lines.append("")

    # ---- Per-map percentile table ---------------------------------------
    lines.append("## Distribution summary (metres) — per map")
    lines.append("")
    lines.append(
        "| Map | n | min | p05 | p10 | p25 | p50 | p75 | p90 | p95 | max | mean | std |"
    )
    lines.append(
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |"
    )
    for map_id, block in output["per_map"].items():
        s = block["summary"]
        if s["n"] == 0:
            lines.append(
                f"| {map_id} | 0 | - | - | - | - | - | - | - | - | - | - | - |"
            )
            continue
        lines.append(
            "| {map} | {n} | {mn:.1f} | {p05:.1f} | {p10:.1f} | {p25:.1f} | {p50:.1f} "
            "| {p75:.1f} | {p90:.1f} | {p95:.1f} | {mx:.1f} | {mean:.1f} | {std:.1f} |".format(
                map=map_id,
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
    lines.append("")

    # ---- Tightest-5 highlight -------------------------------------------
    lines.append(
        f"## Top {len(output['tightest_maps_by_p05'])} tightest maps "
        "(lowest p05)"
    )
    lines.append("")
    lines.append(
        "These are the maps where match-zone overlap is most likely to distort "
        "F1 evaluation at the operating-point buffer diameter."
    )
    lines.append("")
    lines.append(
        "| Rank | Map | n | min | p05 | p50 | < 50 m | < 100 m |"
    )
    lines.append(
        "| ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: |"
    )
    for i, entry in enumerate(output["tightest_maps_by_p05"], start=1):
        lines.append(
            "| {rank} | {map} | {n} | {mn:.1f} | {p05:.1f} | {p50:.1f} "
            "| {f50} ({f50p:.1f}%) | {f100} ({f100p:.1f}%) |".format(
                rank=i,
                map=entry["map_id"],
                n=entry["n_mounds"],
                mn=entry["min_m"],
                p05=entry["p05_m"],
                p50=entry["p50_m"],
                f50=int(round(entry["frac_lt_50m"] * entry["n_mounds"])),
                f50p=entry["frac_lt_50m"] * 100,
                f100=int(round(entry["frac_lt_100m"] * entry["n_mounds"])),
                f100p=entry["frac_lt_100m"] * 100,
            )
        )
    lines.append("")

    # ---- Pooled histogram (counts per 10 m bin, 0-500 m) ----------------
    lines.append("## Pooled NN distance histogram — 10 m bins, 0-500 m")
    lines.append("")
    lines.append(
        "Counts per 10 m bin from 0-500 m. The final column reports the "
        "overflow (NN >= 500 m). Per-map histograms are in the JSON output."
    )
    lines.append("")
    bin_edges = output["pooled"]["histogram"]["bin_edges_m"]
    counts = output["pooled"]["histogram"]["counts"]
    overflow = output["pooled"]["histogram"]["overflow_ge_500m"]
    # Render as rows to avoid an extremely wide table.
    lines.append("| Bin (m) | Count |")
    lines.append("| --- | ---: |")
    for i in range(len(counts)):
        lines.append(
            f"| {int(bin_edges[i])}-{int(bin_edges[i+1])} | {counts[i]} |"
        )
    lines.append(f"| >=500 | {overflow} |")
    lines.append("")

    # ---- Headline interpretation ----------------------------------------
    lines.append("## Headline interpretation")
    lines.append("")
    if ps["n"] > 0:
        p50 = ps["p50_m"]
        p05 = ps["p05_m"]
        tc = output["pooled"]["threshold_counts"]
        frac_lt_50 = tc["lt_50m"]["fraction"] * 100
        frac_lt_70 = tc["lt_70m"]["fraction"] * 100
        frac_lt_100 = tc["lt_100m"]["fraction"] * 100
        lines.append(
            f"- **55-map student GT** — pooled median NN: **{p50:.1f} m**; "
            f"p05: **{p05:.1f} m**; "
            f"< 50 m: **{frac_lt_50:.1f}%**; "
            f"< 70 m: **{frac_lt_70:.1f}%**; "
            f"< 100 m: **{frac_lt_100:.1f}%**."
        )
        lines.append(
            "- **Gold-standard reference maps (for comparison)** — pooled "
            "median NN: **449.5 m**; p05: **83.2 m**; < 50 m: **0.0%**; "
            "< 70 m: **0.4%**; < 100 m: **10.0%**."
        )
    lines.append("")
    lines.append(
        "Interpret match-zone overlap risk by comparing NN distance against "
        "twice the buffer radius (i.e. the buffer *diameter*). For a 50 m "
        "buffer diameter (25 m radius), truth buffers begin to overlap when "
        "NN < 50 m; at NN < 25 m, truth centres lie inside each other's "
        "buffers. If the student GT exhibits materially more sub-50 m "
        "spacing than the gold-standard corpus, the F1 plateau at ~40-50 m "
        "could plausibly reflect a ceiling imposed by matching ambiguity "
        "rather than VLM capability."
    )
    lines.append("")
    return "\n".join(lines)


if __name__ == "__main__":
    main()
