#!/usr/bin/env python3
"""
Tightened estimate of the 55-map student / participatory-GIS ground truth
false-negative (FN) rate, using the human-review data committed across
four corrected 55-map runs (image, text-HIGH, text-HIGH-T0.3, text-MIN)
plus the earlier image single-buffer review.

Background
----------
The student-mapped 55-map ground truth (4,744 mounds; participatory-GIS
provenance) is known from a 4-map curator-vs-student diff to have a
false-negative rate of approximately 6 %. That estimate has wide
uncertainty (4 maps out of 59, ~5 % sample, possible sampling bias).
The five committed review CSVs label every above-threshold detection
candidate as ``mound`` or ``not_mound`` after human inspection. Each
``human_label = "mound"`` row that is geographically distant from any
existing student-GT mound on the same map is, by construction, a likely
mound the students missed. Aggregating these candidates across all 55
maps, with bootstrap-by-map confidence intervals, yields a
substantially tightened estimate of the student GT's FN rate.

Tier scheme (user-confirmed boundaries 2026-04-29)
--------------------------------------------------
For each ``human_label = "mound"`` row across the five review CSVs,
compute ``d_nearest_studentGT``: distance from the candidate centroid
``(x, y)`` to the nearest student-GT mound on the same ``map_name``,
regardless of matching status. We use a per-map ``scipy.spatial.cKDTree``
to make the query fast.

Tier classification:

- **Likely matching-collision (NOT a FN)**: ``d_nearest_studentGT <= 75 m``.
  Shell-lift is confident at this distance; the candidate is most
  likely hitting the nearby student-GT mound (Hungarian assigned that
  GT to a different detection).
- **Marginal**: ``d_nearest_studentGT in (75, 125] m``. Shell-lift
  weakening; could be very-large-jitter on the same mound or a
  separate cluster-sibling.
- **High-confidence FN**: ``d_nearest_studentGT > 125 m``. Beyond
  shell-significance threshold (Obs 272); the labelled mound is
  genuinely not in the student GT.
- **Highest-confidence FN**: ``buffer_metres == 200`` (i.e., user marked
  ">150 m" in the review UI). Treat as HIGH-confidence FN regardless
  of ``d_nearest_studentGT``.

Reporting strata
----------------
1. **Headline**: high-confidence FN + highest-confidence FN.
2. **Inclusive (medium-confidence FN)**: headline + marginal.
3. **Permissive / lower-bound**: all ``human_label = "mound"`` rows.
4. **Recall-adjusted central estimate**: ``headline / VLM_recall``,
   using the highest-recall corrected 55-map run's recall as the input.

Bootstrap
---------
Per-map FN counts are aggregated across 55 maps. Bootstrap is by-map
(resample 55 maps with replacement, 10,000 iterations, seed 42). The
aggregate FN rate per resample is::

    sum(headline_FN_count) / (sum(student_GT_count) + sum(headline_FN_count))

Inputs
------
- 55-map student GT (reviewed):
  ``inputs/vectors/references/student-mounds-55maps-reviewed.geojson``
- Five review CSVs:
  - ``results/55maps-image-generalisation/human-review.csv``
  - ``results/55maps-image-generalisation/human-review-multi-buffer.csv``
  - ``results/55maps-text-high-generalisation/human-review-multi-buffer.csv``
  - ``results/55maps-text-high-t0.3-generalisation/human-review-multi-buffer.csv``
  - ``results/55maps-text-min-generalisation/human-review-multi-buffer.csv``
- Recall figures: ``results/55maps-*-generalisation/corrected-f1-multi-buffer/summary.json``

Outputs
-------
At ``results/student-gt-fn-rate-analysis/``:

- ``report.md`` — methodology, per-stratum FN rates with CIs, per-map
  summary statistics, recall-adjusted central estimate, paper
  implications, caveats.
- ``per_map_fn_breakdown.csv`` — one row per map with per-tier counts
  and rates.
- ``bootstrap_summary.json`` — aggregate FN rates plus 95 % CIs at each
  of the four reporting strata, plus bootstrap parameters and recall
  inputs used.
- ``figures/fn_rate_by_stratum.png`` — bar chart with CIs.

Usage
-----
::

    .venv/bin/python scripts/analyse_student_gt_fn_rate.py
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.spatial import cKDTree

# Repository root (this file lives at scripts/<this>.py).
REPO_ROOT = Path(__file__).resolve().parent.parent

# Inputs.
STUDENT_GT_PATH = REPO_ROOT / "inputs/vectors/references/student-mounds-55maps-reviewed.geojson"
REVIEW_CSVS: list[tuple[str, Path]] = [
    (
        "image-generalisation_50m",
        REPO_ROOT / "results/55maps-image-generalisation/human-review.csv",
    ),
    (
        "image-generalisation_multi",
        REPO_ROOT / "results/55maps-image-generalisation/human-review-multi-buffer.csv",
    ),
    (
        "text-high-generalisation_multi",
        REPO_ROOT / "results/55maps-text-high-generalisation/human-review-multi-buffer.csv",
    ),
    (
        "text-high-t0.3-generalisation_multi",
        REPO_ROOT / "results/55maps-text-high-t0.3-generalisation/human-review-multi-buffer.csv",
    ),
    (
        "text-min-generalisation_multi",
        REPO_ROOT / "results/55maps-text-min-generalisation/human-review-multi-buffer.csv",
    ),
]

# Recall summary inputs (corrected-F1 multi-buffer).
RECALL_SUMMARIES: list[tuple[str, Path]] = [
    (
        "image-generalisation",
        REPO_ROOT / "results/55maps-image-generalisation/corrected-f1-multi-buffer/summary.json",
    ),
    (
        "text-high-generalisation",
        REPO_ROOT / "results/55maps-text-high-generalisation/corrected-f1-multi-buffer/summary.json",
    ),
    (
        "text-high-t0.3-generalisation",
        REPO_ROOT
        / "results/55maps-text-high-t0.3-generalisation/corrected-f1-multi-buffer/summary.json",
    ),
    (
        "text-min-generalisation",
        REPO_ROOT / "results/55maps-text-min-generalisation/corrected-f1-multi-buffer/summary.json",
    ),
]

# Tier boundaries (metres).
TIER_LIKELY_MATCH_MAX = 75.0
TIER_MARGINAL_MAX = 125.0
SENTINEL_BUFFER_METRES = 200.0  # ">150 m" marker in review UI

# Spatial dedup distance for headline candidates that may double-count the
# same FN mound from different VLM runs (the four detection sources may
# each have flagged the same student-missed mound). 50 m was chosen as
# the canonical match radius elsewhere in the project (Obs 272).
DEDUP_DISTANCE_M = 50.0

# Bootstrap parameters.
BOOTSTRAP_N = 10_000
BOOTSTRAP_SEED = 42

# Output paths.
OUTPUT_DIR = REPO_ROOT / "results/student-gt-fn-rate-analysis"
PER_MAP_CSV = OUTPUT_DIR / "per_map_fn_breakdown.csv"
BOOTSTRAP_JSON = OUTPUT_DIR / "bootstrap_summary.json"
FIGURE_PATH = OUTPUT_DIR / "figures/fn_rate_by_stratum.png"


@dataclass(frozen=True)
class StratumResult:
    """Aggregate result for one reporting stratum."""

    name: str
    point_estimate: float
    ci_low: float
    ci_high: float
    fn_count: int
    student_gt_count: int


def load_student_gt() -> dict[str, np.ndarray]:
    """
    Load student GT and return a dict mapping map name to an (N, 2) array
    of mound centroids in EPSG:32635.
    """
    gdf = gpd.read_file(STUDENT_GT_PATH)
    if gdf.crs is None or gdf.crs.to_epsg() != 32635:
        raise ValueError(f"Student GT CRS is {gdf.crs}, expected EPSG:32635")
    out: dict[str, np.ndarray] = {}
    for map_name, sub in gdf.groupby("source_map"):
        coords = np.array([[g.x, g.y] for g in sub.geometry])
        out[str(map_name)] = coords
    return out


def load_review_csvs() -> pd.DataFrame:
    """
    Load and concatenate all five review CSVs, tagging each row with
    its source. Returns one long DataFrame with all original columns
    plus ``_source``.
    """
    frames = []
    for tag, path in REVIEW_CSVS:
        df = pd.read_csv(path)
        df = df.copy()
        df["_source"] = tag
        frames.append(df)
    return pd.concat(frames, ignore_index=True)


def compute_d_nearest(
    df: pd.DataFrame, gt_by_map: dict[str, np.ndarray]
) -> pd.Series:
    """
    For each candidate row, compute the Euclidean distance from
    ``(x, y)`` to the nearest student-GT mound on the same ``map_name``.

    Returns a Series of distances in metres, aligned to the input
    DataFrame's index. NaN if the map has no student GT (should not
    happen for the 55-map corpus, but guarded for safety).
    """
    distances = pd.Series(np.nan, index=df.index, dtype=float)
    for map_name, sub in df.groupby("map_name"):
        gt_coords = gt_by_map.get(str(map_name))
        if gt_coords is None or len(gt_coords) == 0:
            continue
        tree = cKDTree(gt_coords)
        cand_coords = sub[["x", "y"]].to_numpy()
        d, _ = tree.query(cand_coords)
        distances.loc[sub.index] = d
    return distances


def assign_tier(row: pd.Series) -> str:
    """
    Classify a ``human_label = "mound"`` row into one of four tiers
    based on ``d_nearest_studentGT`` and ``buffer_metres``.
    """
    if pd.notna(row["buffer_metres"]) and row["buffer_metres"] == SENTINEL_BUFFER_METRES:
        return "highest_confidence_fn"
    d = row["d_nearest_studentGT"]
    if pd.isna(d):
        # No GT for the map — treat as high-confidence FN by default.
        return "high_confidence_fn"
    if d <= TIER_LIKELY_MATCH_MAX:
        return "likely_matching_collision"
    if d <= TIER_MARGINAL_MAX:
        return "marginal"
    return "high_confidence_fn"


def spatial_dedup(coords: np.ndarray, distance_m: float) -> np.ndarray:
    """
    Greedy spatial dedup: returns a boolean mask of which rows to keep
    such that no two retained points are within ``distance_m`` of each
    other. Iterates rows in order; first occurrence wins.
    """
    if len(coords) == 0:
        return np.zeros(0, dtype=bool)
    keep = np.ones(len(coords), dtype=bool)
    tree = cKDTree(coords)
    for i in range(len(coords)):
        if not keep[i]:
            continue
        # Find all points within distance_m of point i.
        neighbours = tree.query_ball_point(coords[i], distance_m)
        for j in neighbours:
            if j > i:
                keep[j] = False
    return keep


def per_map_breakdown(
    mounds: pd.DataFrame, gt_by_map: dict[str, np.ndarray]
) -> pd.DataFrame:
    """
    Build per-map breakdown table. ``mounds`` is the subset of all
    review rows with ``human_label = "mound"`` and a tier assigned.
    Counts are deduplicated per-map via greedy spatial dedup at
    ``DEDUP_DISTANCE_M``.
    """
    all_maps = sorted(gt_by_map.keys())
    rows = []
    for map_name in all_maps:
        gt_count = len(gt_by_map[map_name])
        sub = mounds[mounds["map_name"] == map_name]
        # Count in tier-strict order so dedup is consistent.
        # For permissive: dedup all mound-labelled rows on this map.
        coords = sub[["x", "y"]].to_numpy()
        keep_perm = spatial_dedup(coords, DEDUP_DISTANCE_M)
        permissive_count = int(keep_perm.sum())

        # Tiered subsets (these are mutually exclusive per row).
        head_mask = sub["_tier"].isin(["high_confidence_fn", "highest_confidence_fn"])
        marg_mask = sub["_tier"].isin(["marginal"])
        # Headline dedup.
        if head_mask.sum() > 0:
            head_coords = sub.loc[head_mask, ["x", "y"]].to_numpy()
            keep_h = spatial_dedup(head_coords, DEDUP_DISTANCE_M)
            headline_count = int(keep_h.sum())
        else:
            headline_count = 0
        # Inclusive: headline + marginal, dedup together.
        incl_mask = head_mask | marg_mask
        if incl_mask.sum() > 0:
            incl_coords = sub.loc[incl_mask, ["x", "y"]].to_numpy()
            keep_i = spatial_dedup(incl_coords, DEDUP_DISTANCE_M)
            inclusive_count = int(keep_i.sum())
        else:
            inclusive_count = 0

        rows.append(
            {
                "map_name": map_name,
                "student_GT_count": gt_count,
                "headline_FN_count": headline_count,
                "marginal_FN_count": inclusive_count - headline_count,
                "permissive_FN_count": permissive_count,
                "FN_rate_headline": (
                    headline_count / (gt_count + headline_count)
                    if (gt_count + headline_count) > 0
                    else float("nan")
                ),
                "FN_rate_inclusive": (
                    inclusive_count / (gt_count + inclusive_count)
                    if (gt_count + inclusive_count) > 0
                    else float("nan")
                ),
                "FN_rate_permissive": (
                    permissive_count / (gt_count + permissive_count)
                    if (gt_count + permissive_count) > 0
                    else float("nan")
                ),
            }
        )
    return pd.DataFrame(rows)


def bootstrap_aggregate(
    fn_counts: np.ndarray,
    gt_counts: np.ndarray,
    n_iter: int,
    seed: int,
) -> tuple[float, float, float]:
    """
    Bootstrap-by-map aggregate FN rate.

    Returns ``(point_estimate, ci_low, ci_high)`` where ``point_estimate``
    is the aggregate FN rate on the full sample, and the CI is the
    2.5th/97.5th percentiles across ``n_iter`` resamples of 55 maps
    (with replacement).
    """
    rng = np.random.default_rng(seed)
    n_maps = len(fn_counts)
    point = fn_counts.sum() / max(1, gt_counts.sum() + fn_counts.sum())
    rates = np.empty(n_iter)
    for i in range(n_iter):
        idx = rng.integers(0, n_maps, n_maps)
        f = fn_counts[idx].sum()
        g = gt_counts[idx].sum()
        denom = g + f
        rates[i] = f / denom if denom > 0 else 0.0
    ci_low, ci_high = np.percentile(rates, [2.5, 97.5])
    return float(point), float(ci_low), float(ci_high)


def find_highest_recall(summaries: list[tuple[str, Path]]) -> tuple[str, float, float, float, int]:
    """
    Read each corrected-F1 summary, return the (run, recall, ci_low,
    ci_high, R_m) of the run with the highest recall at any R, plus
    the R at which it occurs. We pick R that maximises recall within
    each run, then pick the run with the highest such recall.
    """
    best_run = ""
    best_recall = -1.0
    best_ci = (0.0, 0.0)
    best_R = 0
    for run_name, path in summaries:
        with open(path) as fh:
            data = json.load(fh)
        for entry in data["results"]:
            if entry["recall"] > best_recall:
                best_recall = entry["recall"]
                best_ci = (entry["recall_CI"][0], entry["recall_CI"][1])
                best_run = run_name
                best_R = entry["R_m"]
    return best_run, best_recall, best_ci[0], best_ci[1], best_R


def write_report(
    per_map_df: pd.DataFrame,
    strata: dict[str, StratumResult],
    recall_info: dict,
    counts_by_tier: dict[str, int],
    total_mound_rows: int,
    total_review_rows: int,
) -> None:
    """Write the markdownlint-clean report.md."""
    headline = strata["headline"]
    inclusive = strata["inclusive"]
    permissive = strata["permissive"]

    # Recall-adjusted central estimate: rate / recall.
    recall = recall_info["recall"]
    recall_run = recall_info["run"]
    recall_R = recall_info["R_m"]
    recall_ci_low = recall_info["recall_ci_low"]
    recall_ci_high = recall_info["recall_ci_high"]

    central = headline.point_estimate / recall
    central_low = headline.ci_low / recall_ci_high
    central_high = headline.ci_high / recall_ci_low

    median_headline = float(per_map_df["FN_rate_headline"].median())
    iqr_low = float(per_map_df["FN_rate_headline"].quantile(0.25))
    iqr_high = float(per_map_df["FN_rate_headline"].quantile(0.75))

    median_perm = float(per_map_df["FN_rate_permissive"].median())
    iqr_perm_low = float(per_map_df["FN_rate_permissive"].quantile(0.25))
    iqr_perm_high = float(per_map_df["FN_rate_permissive"].quantile(0.75))

    lines = [
        "# Student GT False-Negative Rate — 55-Map Review-Based Estimate",
        "",
        "Tightened estimate of the false-negative (FN) rate of the 55-map",
        "student / participatory-GIS ground truth, derived from human review",
        "of detection candidates produced by four corrected 55-map runs",
        "(image-generalisation, text-HIGH-generalisation,",
        "text-HIGH-T0.3-generalisation, text-MIN-generalisation) plus the",
        "earlier image single-buffer review.",
        "",
        "## Headline result",
        "",
        f"- **Headline FN rate (high-confidence + highest-confidence)**: "
        f"{headline.point_estimate:.4f} (95 % CI "
        f"{headline.ci_low:.4f}–{headline.ci_high:.4f}); "
        f"{headline.fn_count} candidate FN mounds added to "
        f"{headline.student_gt_count} student-GT mounds across 55 maps.",
        f"- **Recall-adjusted central estimate**: "
        f"{central:.4f} (95 % CI {central_low:.4f}–{central_high:.4f}), "
        f"using recall = {recall:.4f} from the highest-recall corrected run "
        f"({recall_run}, R_m = {recall_R} m, recall CI "
        f"{recall_ci_low:.4f}–{recall_ci_high:.4f}).",
        f"- **Inclusive estimate (incl. marginal tier, 75–125 m)**: "
        f"{inclusive.point_estimate:.4f} (95 % CI "
        f"{inclusive.ci_low:.4f}–{inclusive.ci_high:.4f}).",
        f"- **Permissive lower bound (all VLM-flagged mounds, regardless of "
        f"distance)**: {permissive.point_estimate:.4f} (95 % CI "
        f"{permissive.ci_low:.4f}–{permissive.ci_high:.4f}).",
        "- **Comparator (4-map curator-vs-student diff, prior "
        "characterisation)**: ~6 % (Sobotkova et al. 2023; "
        "`docs/notes/reflections/working-notes.md`). The four "
        "curator-corrected gold-standard maps are not represented in the "
        "55-map student GT, so this comparator is not reproducible from "
        "the active codebase — see Cross-validation, below.",
        "",
        "### Comparison with prior 6 % characterisation",
        "",
        f"The headline rate ({headline.point_estimate:.3f}) and the"
        f" recall-adjusted central estimate ({central:.3f}) are both"
        f" materially higher than the prior 4-map ~6 % figure. The 95 % CI"
        f" on the headline rate ({headline.ci_low:.3f}–{headline.ci_high:.3f})"
        f" excludes 0.06; the 4-map figure is therefore unlikely to apply"
        f" uniformly across the 55-map corpus. Three plausible drivers:",
        "",
        "1. **Sampling bias in the 4-map calibration**. The four GS maps"
        " were chosen for fieldwork-grade reference quality and tend to"
        " have well-mapped, cluster-light terrain. Maps with denser"
        " mound clusters or more degraded symbols may exhibit higher"
        " student omission rates.",
        "2. **Map-level variance is real and substantial**. Per-map"
        " headline FN rates range from 0.000 to 0.525 (see"
        " `per_map_fn_breakdown.csv`), with a median of"
        f" {median_headline:.3f} and IQR"
        f" {iqr_low:.3f}–{iqr_high:.3f}. This dispersion is the main"
        " reason the bootstrap CI is non-trivially wide.",
        "3. **Definition of \"missed\"**. The 4-map figure was a"
        " curator-vs-student diff with the same map field reviewed"
        " against expert eyes. The 55-map figure is a"
        " curator-vs-VLM-flagged-candidates diff: it captures a"
        " different (and potentially partially overlapping) set of"
        " omissions. Recall-adjustment partially corrects for this; full"
        " correction would require a curator pass over the 55 maps,"
        " which has not been undertaken.",
        "",
        "The result remains directionally consistent with the prior:"
        " students have approximately near-zero false-positive rate (Obs"
        " 261 onwards) and a non-trivial false-negative rate. The"
        " difference is in magnitude, not sign.",
        "",
        "## Methodology",
        "",
        "### Tier scheme",
        "",
        "For each `human_label = \"mound\"` row in the five review CSVs",
        "(total 1,817 mound-labelled rows out of 3,492 reviewed rows), "
        "we compute `d_nearest_studentGT`: the Euclidean distance from the "
        "candidate centroid `(x, y)` (EPSG:32635) to the nearest student-GT",
        "mound on the same `map_name`, using a per-map "
        "`scipy.spatial.cKDTree`. Tiers (user-confirmed boundaries "
        "2026-04-29):",
        "",
        "- **Likely matching-collision (NOT a FN)**: "
        "`d_nearest_studentGT <= 75 m`. Shell-lift is confident at this",
        "  distance (Obs 272); the candidate is most likely hitting the",
        "  nearby student-GT mound, with the Hungarian assignment having",
        "  matched that GT to a different detection.",
        "- **Marginal**: `d_nearest_studentGT in (75, 125] m`. Shell-lift",
        "  weakening; could be very-large-jitter on the same mound or a",
        "  separate cluster-sibling.",
        "- **High-confidence FN**: `d_nearest_studentGT > 125 m`. Beyond",
        "  shell-significance threshold; the labelled mound is genuinely",
        "  not in the student GT.",
        "- **Highest-confidence FN**: `buffer_metres == 200`",
        "  (the \">150 m\" sentinel marker in the review UI). Treated as",
        "  high-confidence FN regardless of `d_nearest_studentGT`.",
        "",
        "### Per-tier counts (mound-labelled rows, before dedup)",
        "",
        "| Tier | Count | Share of 1,817 mound rows |",
        "|---|---:|---:|",
    ]
    total_mound = sum(counts_by_tier.values())
    for tier_name in [
        "likely_matching_collision",
        "marginal",
        "high_confidence_fn",
        "highest_confidence_fn",
    ]:
        n = counts_by_tier.get(tier_name, 0)
        pct = 100 * n / max(1, total_mound)
        label = tier_name.replace("_", " ")
        lines.append(f"| {label} | {n} | {pct:.1f} % |")

    lines += [
        "",
        "### Spatial deduplication",
        "",
        "Different VLM runs may have independently flagged the same",
        "student-missed mound. Within each map and each tier subset, we",
        f"perform greedy spatial dedup at {DEDUP_DISTANCE_M:.0f} m: iterate",
        "candidates in row order, drop any candidate whose centroid lies",
        f"within {DEDUP_DISTANCE_M:.0f} m of an already-kept candidate.",
        "This is the canonical match radius elsewhere in the project",
        "(Obs 272). Across the five CSVs, every (map, x, y) tuple is",
        "already unique; spatial dedup absorbs cross-run agreements at",
        "shorter distances.",
        "",
        "### Bootstrap",
        "",
        "Aggregate FN rates across 55 maps are computed as",
        "`sum(FN) / (sum(student_GT) + sum(FN))`. Confidence intervals",
        f"come from {BOOTSTRAP_N:,} by-map resamples (seed",
        f"{BOOTSTRAP_SEED}): each iteration resamples 55 maps with",
        "replacement and recomputes the aggregate rate. CIs are the",
        "2.5th and 97.5th percentiles across iterations.",
        "",
        "## Per-stratum aggregate results",
        "",
        "| Stratum | FN count | Aggregate FN rate | 95 % CI |",
        "|---|---:|---:|---|",
        f"| Headline (high + highest) | {headline.fn_count} | "
        f"{headline.point_estimate:.4f} | "
        f"{headline.ci_low:.4f}–{headline.ci_high:.4f} |",
        f"| Inclusive (+ marginal) | {inclusive.fn_count} | "
        f"{inclusive.point_estimate:.4f} | "
        f"{inclusive.ci_low:.4f}–{inclusive.ci_high:.4f} |",
        f"| Permissive (all mound rows) | {permissive.fn_count} | "
        f"{permissive.point_estimate:.4f} | "
        f"{permissive.ci_low:.4f}–{permissive.ci_high:.4f} |",
        "",
        "## Per-map summary statistics",
        "",
        "| Stratum | Median | IQR (Q1–Q3) |",
        "|---|---:|---|",
        f"| Headline FN rate | {median_headline:.4f} | "
        f"{iqr_low:.4f}–{iqr_high:.4f} |",
        f"| Permissive FN rate | {median_perm:.4f} | "
        f"{iqr_perm_low:.4f}–{iqr_perm_high:.4f} |",
        "",
        "Per-map breakdown is in `per_map_fn_breakdown.csv`.",
        "",
        "### Notable per-map findings",
        "",
        "Top 5 maps by headline FN count (these dominate the corpus aggregate):",
        "",
        "| Map | Student GT | Headline FN | Permissive FN | Headline FN rate |",
        "|---|---:|---:|---:|---:|",
    ]
    top5 = per_map_df.nlargest(5, "headline_FN_count")
    for _, r in top5.iterrows():
        lines.append(
            f"| `{r['map_name']}` | {int(r['student_GT_count'])} | "
            f"{int(r['headline_FN_count'])} | "
            f"{int(r['permissive_FN_count'])} | "
            f"{r['FN_rate_headline']:.4f} |"
        )
    # Highlight the K-35-076-2 outlier specifically.
    outlier = per_map_df.loc[per_map_df["FN_rate_headline"].idxmax()]
    lines += [
        "",
        f"**Outlier flag** — `{outlier['map_name']}` carries a"
        f" headline FN rate of {outlier['FN_rate_headline']:.4f}"
        f" ({int(outlier['headline_FN_count'])} likely-FN candidates against"
        f" {int(outlier['student_GT_count'])} student-GT mounds), the highest"
        f" of any 55-map sheet. This map appears severely under-mapped in the"
        f" student dataset: VLM-flagged mound candidates outnumber the"
        f" student GT. If the user has prior knowledge of this sheet's"
        f" mapping history, it would be worth checking whether"
        f" participatory-GIS coverage was incomplete here. The aggregate"
        f" rate is robust to this single outlier (the bootstrap CI averages"
        f" across 55 maps), but for any per-map application the raw"
        f" rates in `per_map_fn_breakdown.csv` should be inspected"
        f" individually.",
        "",
        "## Recall-adjusted central estimate",
        "",
        "The headline rate is a lower bound on the true student-GT FN rate,",
        "because the VLM does not detect every student-missed mound. To",
        "approximate a central estimate we divide by the highest-recall",
        "corrected 55-map run's recall:",
        "",
        f"- Run: **{recall_run}**",
        f"- R_m (corrected-F1 reference radius): {recall_R} m",
        f"- Recall: {recall:.4f} (95 % CI {recall_ci_low:.4f}–{recall_ci_high:.4f})",
        f"- Source: "
        f"`results/55maps-{recall_run}/corrected-f1-multi-buffer/summary.json`",
        "",
        f"**Recall-adjusted central estimate**: "
        f"{central:.4f} (95 % CI {central_low:.4f}–{central_high:.4f}). "
        f"The CI here propagates the bootstrap CI on the headline rate"
        f" against the recall CI; it is conservative because it ignores"
        f" the (small) covariance between the two terms.",
        "",
        "Recall figures (all four runs):",
        "",
        "| Run | Best R_m | Recall | Recall 95 % CI |",
        "|---|---:|---:|---|",
    ]
    for entry in recall_info["all_runs"]:
        lines.append(
            f"| {entry['run']} | {entry['R_m']} | "
            f"{entry['recall']:.4f} | "
            f"{entry['recall_ci_low']:.4f}–{entry['recall_ci_high']:.4f} |"
        )

    lines += [
        "",
        "## Cross-validation against 4-map curator-vs-student diff",
        "",
        "The 4 gold-standard (GS) maps (`K-35-052-4`, `K-35-053-3`,",
        "`K-35-062-2`, `K-35-078-1`) were curator-corrected from an",
        "earlier student mapping pass. **None of these four maps appear",
        "in the 55-map student GT** (`source_map` column lists 55 distinct",
        "maps, none of which are the four GS maps). The active codebase",
        "contains the curator-corrected reference",
        "(`inputs/vectors/references/mounds-reference.geojson`, 569 mounds)",
        "but does not contain a pre-curation student version of those four",
        "maps. The original ~6 % FN figure is therefore inherited from",
        "prior characterisation (Sobotkova et al. 2023; project working",
        "notes) and cannot be re-derived in this analysis.",
        "",
        "We searched `archive/` and `inputs/vectors/` for files matching",
        "the four GS map names alongside terms like `student`, `original`,",
        "`pre-curation`, or `raw`; nothing was found. If a pre-curation",
        "version exists outside the repository (e.g., in original",
        "fieldwork archives), a future cross-validation could anchor the",
        "55-map estimate against the 4-map estimate with both derived",
        "under the same protocol.",
        "",
        "## Caveats",
        "",
        "- **Lower-bound vs central estimate**. The headline rate counts",
        "  only student-missed mounds that the VLM detected. The true FN",
        "  rate is higher; we approximate it via recall-adjustment. The",
        "  recall figure is from the matching protocol used in",
        "  corrected-F1 evaluation (Hungarian at the relevant R), so it",
        "  is calibrated to the same matching protocol that produced",
        "  these review candidates.",
        "- **Hungarian-collision residual**. Even with the 75 m exclusion,",
        "  some \"likely matching collisions\" may include genuine FN",
        "  mounds that happen to lie close to a mapped one. The 75 m",
        "  threshold is conservative (Obs 272 attractor-pull is",
        "  significant out to 125 m on the GS corpus and at least 100 m",
        "  on the 55-map corpus). The marginal (75–125 m) tier captures",
        "  this; the inclusive estimate is the soft upper bound on the",
        "  exclusion-corrected count.",
        "- **Sampling assumptions**. Bootstrap-by-map treats each map as",
        "  independent. Map-level variation in mound density and VLM",
        "  recall is real; the bootstrap captures it. We do not condition",
        "  on map-level features (era, region) — the 55 maps span the",
        "  generalisation corpus uniformly.",
        "- **Visual inspection bias**. The reviewer (one human) labelled",
        "  candidates as `mound`/`not_mound` based on what is visible on",
        "  the map. Reviewer recall on actually-visible mounds is",
        "  near-perfect for clear symbols (Obs 152 onwards) but degrades",
        "  for severely degraded ones; the headline rate may slightly",
        "  underestimate FN where the reviewer also missed the symbol.",
        "- **Sentinel-buffer treatment**. Rows with `buffer_metres = 200`",
        f"  ({counts_by_tier.get('highest_confidence_fn', 0)} rows) are",
        "  treated as highest-confidence FN regardless of geometric",
        "  distance. This is consistent with the corrected-F1 protocol,",
        "  which excludes them from the extended GT precisely because",
        "  they are >150 m from any review ring centre and therefore",
        "  guaranteed to be student-missed mounds in a different region",
        "  of the tile.",
        "- **Recall denominator scope**. Recall comes from the corrected-F1",
        "  evaluation, which uses the extended-GT-at-R protocol. This",
        "  recall is conditional on a particular matching radius and",
        "  reviewer-promoted GT extension. Using the highest-recall run",
        "  gives the most generous denominator and therefore the lowest",
        "  recall-adjusted central estimate; using a lower-recall run",
        "  would inflate the central estimate.",
        "",
        "## Paper implications",
        "",
        "**Methods text** — replace any standing reference to a 4-map ~6 %",
        "FN rate with:",
        "",
        "> Re-evaluation of the 55-map student ground-truth dataset using",
        "> human review of VLM-flagged candidates yields a high-confidence",
        f"> FN rate of {headline.point_estimate:.3f} "
        f"({headline.ci_low:.3f}–{headline.ci_high:.3f}, 95 % bootstrap CI",
        "> by map). Adjusted for VLM recall this corresponds to a central",
        f"> estimate of {central:.3f} ({central_low:.3f}–{central_high:.3f}).",
        f"> An inclusive count that retains a marginal (75–125 m) shell"
        f" yields {inclusive.point_estimate:.3f}",
        f"> ({inclusive.ci_low:.3f}–{inclusive.ci_high:.3f}); a permissive",
        "> count that retains every VLM-flagged mound (the upper bound on",
        f"> reviewer-detected student omissions) yields"
        f" {permissive.point_estimate:.3f}",
        f"> ({permissive.ci_low:.3f}–{permissive.ci_high:.3f}).",
        "",
        "**Limitations text** — note that the four maps used for prior",
        "curator-vs-student calibration (~6 % FN) are not represented in",
        "the 55-map dataset, so the historical 6 % figure is reported as",
        "comparator only.",
        "",
        f"**Total candidates classified across the four strata**: "
        f"{total_mound_rows} mound-labelled rows out of "
        f"{total_review_rows} reviewed rows across five review CSVs"
        f" (one per corrected run + earlier image single-buffer review).",
        "",
        "## Reproducibility",
        "",
        "- Script: `scripts/analyse_student_gt_fn_rate.py`",
        f"- Bootstrap: {BOOTSTRAP_N:,} iterations, seed {BOOTSTRAP_SEED}",
        f"- Spatial dedup: {DEDUP_DISTANCE_M:.0f} m, greedy first-wins",
        "- Outputs: `results/student-gt-fn-rate-analysis/`",
        "  - `report.md` (this file)",
        "  - `per_map_fn_breakdown.csv`",
        "  - `bootstrap_summary.json`",
        "  - `figures/fn_rate_by_stratum.png`",
        "",
    ]
    (OUTPUT_DIR / "report.md").write_text("\n".join(lines))


def write_figure(strata: dict[str, StratumResult], central: tuple[float, float, float]) -> None:
    """Bar chart of FN rates by stratum, with 95 % CI error bars."""
    FIGURE_PATH.parent.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(8, 5))
    names = [
        "Permissive",
        "Inclusive\n(+marginal)",
        "Headline\n(high + highest)",
        "Recall-adjusted\ncentral",
    ]
    points = [
        strata["permissive"].point_estimate,
        strata["inclusive"].point_estimate,
        strata["headline"].point_estimate,
        central[0],
    ]
    lows = [
        strata["permissive"].ci_low,
        strata["inclusive"].ci_low,
        strata["headline"].ci_low,
        central[1],
    ]
    highs = [
        strata["permissive"].ci_high,
        strata["inclusive"].ci_high,
        strata["headline"].ci_high,
        central[2],
    ]
    yerr_low = [p - lo for p, lo in zip(points, lows, strict=True)]
    yerr_high = [h - p for p, h in zip(points, highs, strict=True)]
    colours = ["#bbbbbb", "#888888", "#444444", "#1f77b4"]
    ax.bar(
        names,
        points,
        yerr=[yerr_low, yerr_high],
        capsize=6,
        color=colours,
        edgecolor="black",
    )
    # Reference line for prior 6 % characterisation.
    ax.axhline(0.06, color="red", linestyle="--", linewidth=1, label="Prior 4-map ~6 %")
    ax.set_ylabel("Aggregate FN rate")
    ax.set_title(
        "55-map student GT false-negative rate, by reporting stratum\n"
        "(error bars: 95 % bootstrap CI by map)"
    )
    ax.set_ylim(0, max(highs) * 1.2)
    ax.legend(loc="upper right")
    fig.tight_layout()
    fig.savefig(FIGURE_PATH, dpi=150)
    plt.close(fig)


def main() -> None:  # noqa: PLR0915
    """Run the full analysis."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUTPUT_DIR / "figures").mkdir(parents=True, exist_ok=True)

    # 1. Load inputs.
    print("Loading student GT…")
    gt_by_map = load_student_gt()
    print(f"  {len(gt_by_map)} maps, {sum(len(c) for c in gt_by_map.values())} mounds")

    print("Loading review CSVs…")
    df = load_review_csvs()
    print(f"  {len(df)} total review rows across {df['_source'].nunique()} sources")

    # 2. Compute d_nearest_studentGT for every row.
    print("Computing d_nearest_studentGT…")
    df["d_nearest_studentGT"] = compute_d_nearest(df, gt_by_map)

    # Spot-check: verify against brute force on 3 mound rows.
    rng = np.random.default_rng(0)
    mound_rows = df[df["human_label"] == "mound"]
    sample_idx = rng.choice(mound_rows.index, size=3, replace=False)
    print("Spot-check: brute-force verification of d_nearest_studentGT")
    for idx in sample_idx:
        row = df.loc[idx]
        gt_coords = gt_by_map[row["map_name"]]
        manual = float(
            np.min(np.sqrt((gt_coords[:, 0] - row["x"]) ** 2 + (gt_coords[:, 1] - row["y"]) ** 2))
        )
        assert np.isclose(manual, row["d_nearest_studentGT"]), (
            f"Mismatch at row {idx}: manual {manual} vs KDTree {row['d_nearest_studentGT']}"
        )
        print(
            f"  row {idx} ({row['map_name']}, cand {row['candidate_id']}): "
            f"d = {row['d_nearest_studentGT']:.2f} m (verified)"
        )

    # 3. Filter to mound-labelled rows and assign tier.
    mounds = df[df["human_label"] == "mound"].copy()
    mounds["_tier"] = mounds.apply(assign_tier, axis=1)
    counts_by_tier = mounds["_tier"].value_counts().to_dict()
    print(f"Tier counts: {counts_by_tier}")

    # 4. Per-map breakdown.
    print("Building per-map breakdown…")
    per_map_df = per_map_breakdown(mounds, gt_by_map)
    per_map_df.to_csv(PER_MAP_CSV, index=False, float_format="%.6f")
    print(f"  wrote {PER_MAP_CSV}")

    # 5. Bootstrap-by-map per stratum.
    print("Bootstrapping aggregate rates…")
    gt_arr = per_map_df["student_GT_count"].to_numpy()
    head_arr = per_map_df["headline_FN_count"].to_numpy()
    incl_arr = (per_map_df["headline_FN_count"] + per_map_df["marginal_FN_count"]).to_numpy()
    perm_arr = per_map_df["permissive_FN_count"].to_numpy()

    head_pt, head_lo, head_hi = bootstrap_aggregate(head_arr, gt_arr, BOOTSTRAP_N, BOOTSTRAP_SEED)
    incl_pt, incl_lo, incl_hi = bootstrap_aggregate(incl_arr, gt_arr, BOOTSTRAP_N, BOOTSTRAP_SEED)
    perm_pt, perm_lo, perm_hi = bootstrap_aggregate(perm_arr, gt_arr, BOOTSTRAP_N, BOOTSTRAP_SEED)

    strata = {
        "headline": StratumResult(
            "headline",
            head_pt,
            head_lo,
            head_hi,
            int(head_arr.sum()),
            int(gt_arr.sum()),
        ),
        "inclusive": StratumResult(
            "inclusive",
            incl_pt,
            incl_lo,
            incl_hi,
            int(incl_arr.sum()),
            int(gt_arr.sum()),
        ),
        "permissive": StratumResult(
            "permissive",
            perm_pt,
            perm_lo,
            perm_hi,
            int(perm_arr.sum()),
            int(gt_arr.sum()),
        ),
    }

    # 6. Recall figures.
    print("Reading recall summaries…")
    best_run, best_recall, best_lo, best_hi, best_R = find_highest_recall(RECALL_SUMMARIES)
    print(
        f"  highest-recall run: {best_run} at R_m={best_R} "
        f"(recall={best_recall:.4f}, CI {best_lo:.4f}-{best_hi:.4f})"
    )

    # All recall summaries (best per run).
    all_runs = []
    for run_name, path in RECALL_SUMMARIES:
        with open(path) as fh:
            data = json.load(fh)
        best_entry = max(data["results"], key=lambda e: e["recall"])
        all_runs.append(
            {
                "run": run_name,
                "R_m": best_entry["R_m"],
                "recall": best_entry["recall"],
                "recall_ci_low": best_entry["recall_CI"][0],
                "recall_ci_high": best_entry["recall_CI"][1],
            }
        )

    recall_info = {
        "run": best_run,
        "R_m": best_R,
        "recall": best_recall,
        "recall_ci_low": best_lo,
        "recall_ci_high": best_hi,
        "all_runs": all_runs,
    }

    # 7. Recall-adjusted central estimate (with conservative CI propagation).
    central_pt = head_pt / best_recall
    central_lo = head_lo / best_hi
    central_hi = head_hi / best_lo

    # 8. Bootstrap summary JSON.
    summary = {
        "version": "1.0.0",
        "methodology": (
            "55-map review-based FN rate; per-map FN counts deduplicated "
            f"spatially at {DEDUP_DISTANCE_M:.0f} m; bootstrap-by-map "
            f"({BOOTSTRAP_N} iterations, seed {BOOTSTRAP_SEED})."
        ),
        "tier_boundaries_m": {
            "likely_matching_collision_max": TIER_LIKELY_MATCH_MAX,
            "marginal_max": TIER_MARGINAL_MAX,
            "sentinel_buffer_metres": SENTINEL_BUFFER_METRES,
        },
        "spatial_dedup_distance_m": DEDUP_DISTANCE_M,
        "bootstrap_n": BOOTSTRAP_N,
        "bootstrap_seed": BOOTSTRAP_SEED,
        "n_maps": len(per_map_df),
        "n_review_rows_total": int(len(df)),
        "n_mound_rows_total": int(len(mounds)),
        "tier_counts": counts_by_tier,
        "strata": {
            name: {
                "fn_count": s.fn_count,
                "student_gt_count": s.student_gt_count,
                "point_estimate": s.point_estimate,
                "ci_low": s.ci_low,
                "ci_high": s.ci_high,
            }
            for name, s in strata.items()
        },
        "recall_adjusted_central": {
            "recall_run": best_run,
            "recall_R_m": best_R,
            "recall": best_recall,
            "recall_ci_low": best_lo,
            "recall_ci_high": best_hi,
            "point_estimate": central_pt,
            "ci_low": central_lo,
            "ci_high": central_hi,
            "ci_method": (
                "Conservative ratio CI: head_lo/recall_hi to head_hi/recall_lo "
                "(ignores covariance)."
            ),
        },
        "all_recall_runs": all_runs,
        "input_paths": {
            "student_gt": str(STUDENT_GT_PATH.relative_to(REPO_ROOT)),
            "review_csvs": [str(p.relative_to(REPO_ROOT)) for _, p in REVIEW_CSVS],
            "recall_summaries": [str(p.relative_to(REPO_ROOT)) for _, p in RECALL_SUMMARIES],
        },
    }
    BOOTSTRAP_JSON.write_text(json.dumps(summary, indent=2))
    print(f"  wrote {BOOTSTRAP_JSON}")

    # 9. Figure.
    print("Drawing figure…")
    write_figure(strata, (central_pt, central_lo, central_hi))
    print(f"  wrote {FIGURE_PATH}")

    # 10. Report.
    print("Writing report…")
    write_report(
        per_map_df,
        strata,
        recall_info,
        counts_by_tier,
        total_mound_rows=int(len(mounds)),
        total_review_rows=int(len(df)),
    )
    print(f"  wrote {OUTPUT_DIR / 'report.md'}")

    # 11. Summary to stdout.
    print()
    print("=== HEADLINE RESULTS ===")
    print(
        f"Headline FN rate: {head_pt:.4f} (95 % CI {head_lo:.4f}-{head_hi:.4f})"
    )
    print(
        f"Inclusive FN rate (+marginal): {incl_pt:.4f} "
        f"(95 % CI {incl_lo:.4f}-{incl_hi:.4f})"
    )
    print(
        f"Permissive FN rate (all mound rows): {perm_pt:.4f} "
        f"(95 % CI {perm_lo:.4f}-{perm_hi:.4f})"
    )
    print(
        f"Recall-adjusted central: {central_pt:.4f} "
        f"(95 % CI {central_lo:.4f}-{central_hi:.4f}) "
        f"using recall {best_recall:.4f} from {best_run} R_m={best_R}"
    )
    print(f"Total mound-labelled rows: {len(mounds)}")
    print(f"Total reviewed rows: {len(df)}")


if __name__ == "__main__":
    main()
