#!/usr/bin/env python3
"""
TP-only localisation precision — diagnostic test #1 from Obs 296.

Compute the centroid-to-nearest-GT-centroid distance distribution for
**True Positives only** on each of five corpus conditions, and test
whether the cap difference identified between the 4-map gold-standard
(GS) corpus and the 4-run 55-map corpus (Obs 295: 25 m on GS vs 100 m
most-permissive on 55-map per Obs 298) is driven by detector spatial
precision differences or by False-Positive (FP) anchoring differences.

Reasoning
---------

Obs 295 read the GS 25 m attractor-pull cap as the detector's
"fundamental spatial precision" and the 55-map 100/125 m caps as
"GT-jitter and density-saturation inflated". Obs 296 reframes this as a
"failure of generalisation" — the GS 4 maps were the calibration corpus
and the 55-map sample is unfamiliar, so the cap differences may instead
reflect different FP-anchoring failure modes (spot-heights / water on
GS; numbers / benchmarks / distractor-pull on 55-map). The cap is set
by whichever failure mode dominates that corpus.

This diagnostic separates the two readings by stripping out FPs:

- **If GS True Positives (TPs) cluster within ~10 m and 55-map TPs
  cluster within ~30 m**, the spatial-precision difference is real even
  after FPs are removed → calibration tightened TP localisation as well
  as FP suppression.
- **If GS TPs and 55-map TPs overlap tightly** (e.g., both centred near
  5–15 m), the cap difference is purely FP-driven → detector spatial
  precision is constant across corpuses; only the FP-anchoring failure
  modes differ.

Method
------

For each of the 5 conditions:

1. Load detection centroids in EPSG:32635:
   - **GS, text-HIGH-T0.7 (K=5)**: PV-materialised verified detections
     ``results/leaderboard/era2/pv-materialised/pv-high-text-t0.7-n5.geojson``
     (392 detections; reproject from EPSG:4326).
   - **55-map, T=0.3 / T=0.7 / image / text-MIN**: per-row (x, y) from
     the run's ``human-review-multi-buffer.csv`` (already EPSG:32635;
     these are the verified detection centroids that fed Obs 294 / 298).
     For the **image** run, combine yesterday's mound calls
     (``human-review.csv``, 472 mound rows pinned at 50 m) with today's
     re-review (``human-review-multi-buffer.csv``, 274 mound + 283
     not_mound rows), deduplicating on ``candidate_id`` (matches the
     load logic of ``analyse_attractor_pull_v2.py``).
2. Load the canonical reference set in EPSG:32635:
   - **GS**: ``inputs/vectors/references/mounds-reference.geojson``
     (curator-corrected, 569 features — MultiPoint singletons exploded
     to per-point Points).
   - **55-map**: ``inputs/vectors/references/student-mounds-55maps-reviewed.geojson``
     (post-review, 4 744 Points).
3. For each detection, query nearest reference centroid via
   ``scipy.spatial.cKDTree`` (k=1).
4. **TP filter**: keep detections with ``d_min ≤ 25 m`` (the GS-cap
   threshold per Obs 295). Using 25 m **uniformly** keeps the matching
   scope identical across conditions, so any distribution difference
   reflects detector precision not differential cap selection.
5. For the TP subset, descriptors:
   - mean, median, std
   - 25th, 50th, 75th, 90th, 95th percentiles
   - histogram in 5 m bins from 0 to 25 m
6. **Pairwise Kolmogorov–Smirnov tests** between GS and each 55-map
   condition to test whether the TP distance distributions differ.

Outputs at ``results/55maps-vs-gs-tp-localisation/``:

- ``tp_localisation.json`` — per-condition descriptors, K-S pairwise
  table, and metadata (paths, counts, methodological note).
- ``report.md`` — summary table + interpretation paragraph.
- ``figures/tp_distance_histogram.png`` — 5-condition overlay
  histogram in 5 m bins.

Methodological caveat (per task brief)
--------------------------------------

This is a **one-sided test of detector precision**. It does NOT
distinguish "tight detector + bad FP-anchoring" from "loose detector +
good FP-anchoring" — that requires the FP-class diagnostic, which has
no suitable data on existing reviews per Shawn's 2026-04-29 catch. But
it is the cleanest single number on detector precision available from
existing data.

Compute: ~5 s (KDTree queries, no permutations). Local-safe but the
script is run on sapphire by default per repo policy.

Usage
-----

    python scripts/analyse_tp_localisation_55maps_vs_gs.py
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd
from scipy.spatial import cKDTree
from scipy.stats import ks_2samp

# --- Configuration ---
CRS = "EPSG:32635"
TP_CUTOFF_M = 25.0  # GS-cap threshold per Obs 295; uniform across all conditions.
HIST_BIN_M = 5.0  # 5 m bins (0, 5, 10, 15, 20, 25).

REPO_ROOT = Path(__file__).resolve().parent.parent
GS_REFERENCE = REPO_ROOT / "inputs/vectors/references/mounds-reference.geojson"
M55_REFERENCE = REPO_ROOT / "inputs/vectors/references/student-mounds-55maps-reviewed.geojson"
GS_DETECTION = REPO_ROOT / "results/leaderboard/era2/pv-materialised/pv-high-text-t0.7-n5.geojson"

M55_DIR = REPO_ROOT / "results"
OUT_DIR = REPO_ROOT / "results/55maps-vs-gs-tp-localisation"


@dataclass
class CondSpec:
    """Definition of one of the five conditions."""

    key: str  # short ID used in JSON / figure
    label: str  # display label for tables / report
    corpus: str  # "gs" or "55map"
    # Either a single detection geojson (GS path) or a list of review
    # CSVs to combine (55-map path). The 55-map path replicates the
    # candidate-loading semantics of analyse_attractor_pull_v2.py:
    # single-CSV runs (T=0.3, T=0.7, text-MIN) take all rows; the image
    # run merges yesterday + today by candidate_id.
    detection_geojson: Path | None = None
    review_csvs: tuple[Path, ...] = field(default_factory=tuple)


CONDITIONS: tuple[CondSpec, ...] = (
    CondSpec(
        key="gs-text-high-t0.7",
        label="GS text-HIGH-T0.7 (K=5)",
        corpus="gs",
        detection_geojson=GS_DETECTION,
    ),
    CondSpec(
        key="55map-t0.3",
        label="55-map T=0.3 text-HIGH",
        corpus="55map",
        review_csvs=(
            M55_DIR
            / "55maps-text-high-t0.3-generalisation/human-review-multi-buffer.csv",
        ),
    ),
    CondSpec(
        key="55map-t0.7",
        label="55-map T=0.7 text-HIGH",
        corpus="55map",
        review_csvs=(
            M55_DIR
            / "55maps-text-high-generalisation/human-review-multi-buffer.csv",
        ),
    ),
    CondSpec(
        key="55map-image",
        label="55-map image (T=0.7)",
        corpus="55map",
        review_csvs=(
            M55_DIR / "55maps-image-generalisation/human-review.csv",
            M55_DIR
            / "55maps-image-generalisation/human-review-multi-buffer.csv",
        ),
    ),
    CondSpec(
        key="55map-text-min",
        label="55-map text-MIN",
        corpus="55map",
        review_csvs=(
            M55_DIR
            / "55maps-text-min-generalisation/human-review-multi-buffer.csv",
        ),
    ),
)


# --- Reference loading ---


def load_reference_kdtree(path: Path) -> tuple[cKDTree, int]:
    """
    Build a KDTree on the reference mound centroids in EPSG:32635.

    The GS reference stores mounds as MultiPoint singletons (569 rows,
    each a 1-point MultiPoint); the 55-map reference is per-Point
    (4 744 rows). Calling ``.explode`` is a no-op on the 55-map case
    and resolves the GS MultiPoints into per-point Points.
    """
    gdf = gpd.read_file(path).to_crs(CRS)
    pts = gdf.explode(index_parts=False).reset_index(drop=True)
    coords = np.array([[g.x, g.y] for g in pts.geometry])
    return cKDTree(coords), len(coords)


# --- Detection loading ---


def _load_gs_detections(spec: CondSpec) -> np.ndarray:
    """Load GS detections (geojson) and reproject to EPSG:32635."""
    gdf = gpd.read_file(spec.detection_geojson).to_crs(CRS)
    coords = np.array([[g.x, g.y] for g in gdf.geometry])
    return coords


def _load_55map_detections(spec: CondSpec) -> np.ndarray:
    """
    Load 55-map verified detection centroids from review CSVs.

    Mirrors ``analyse_attractor_pull_v2.load_combined_candidates``:

    - **Single-CSV runs** (T=0.3, T=0.7, text-MIN): every row is a
      verified detection; take all (x, y).
    - **Image run**: combine yesterday's mound rows (50 m calls) with
      today's full multi-buffer re-review (mound + not_mound), then
      deduplicate on ``candidate_id`` keeping the latest entry — which
      matches what the v2 attractor-pull analysis used for image's
      n=557 candidate set.

    Returns
    -------
    numpy.ndarray
        Shape (N, 2) of (x, y) in EPSG:32635.
    """
    if len(spec.review_csvs) == 1:
        df = pd.read_csv(spec.review_csvs[0])
        return df[["x", "y"]].to_numpy(dtype=float)
    # Image run — yesterday + today merge with dedupe on candidate_id.
    yesterday = pd.read_csv(spec.review_csvs[0])
    today = pd.read_csv(spec.review_csvs[1])
    y_mound = yesterday[yesterday["human_label"] == "mound"][
        ["candidate_id", "x", "y"]
    ].copy()
    today_keep = today[["candidate_id", "x", "y"]].copy()
    combined = pd.concat([y_mound, today_keep], ignore_index=True)
    combined = combined.drop_duplicates(subset="candidate_id", keep="last")
    return combined[["x", "y"]].to_numpy(dtype=float)


def load_detections(spec: CondSpec) -> np.ndarray:
    """Dispatch detection loading by corpus type."""
    if spec.corpus == "gs":
        return _load_gs_detections(spec)
    return _load_55map_detections(spec)


# --- Distribution descriptors ---


def descriptors(distances_m: np.ndarray) -> dict:
    """
    Distribution descriptors for an array of TP-to-GT distances.

    Computes mean, median, std, the 25/50/75/90/95 th percentiles, and
    a 5 m-binned histogram from 0 to ``TP_CUTOFF_M``.
    """
    if len(distances_m) == 0:
        return {
            "n_tp": 0,
            "mean_m": None,
            "median_m": None,
            "std_m": None,
            "p25_m": None,
            "p50_m": None,
            "p75_m": None,
            "p90_m": None,
            "p95_m": None,
            "histogram_5m_bins": [],
        }
    bins = np.arange(0.0, TP_CUTOFF_M + HIST_BIN_M, HIST_BIN_M)
    counts, _ = np.histogram(distances_m, bins=bins)
    return {
        "n_tp": int(len(distances_m)),
        "mean_m": round(float(np.mean(distances_m)), 3),
        "median_m": round(float(np.median(distances_m)), 3),
        "std_m": round(float(np.std(distances_m, ddof=1)), 3)
        if len(distances_m) > 1
        else 0.0,
        "p25_m": round(float(np.percentile(distances_m, 25)), 3),
        "p50_m": round(float(np.percentile(distances_m, 50)), 3),
        "p75_m": round(float(np.percentile(distances_m, 75)), 3),
        "p90_m": round(float(np.percentile(distances_m, 90)), 3),
        "p95_m": round(float(np.percentile(distances_m, 95)), 3),
        "histogram_5m_bins": [
            {
                "bin_lo_m": float(bins[i]),
                "bin_hi_m": float(bins[i + 1]),
                "count": int(counts[i]),
            }
            for i in range(len(counts))
        ],
    }


# --- Per-condition analysis ---


def analyse_condition(
    spec: CondSpec,
    gs_tree: cKDTree,
    m55_tree: cKDTree,
) -> dict:
    """
    Compute TP-only nearest-GT distance distribution for one condition.

    Returns a dict suitable for the aggregate JSON output, including the
    raw TP distance array (so K-S tests can run downstream without
    re-querying the trees).
    """
    print(f"[run] {spec.label}")
    coords = load_detections(spec)
    n_total = len(coords)
    tree = gs_tree if spec.corpus == "gs" else m55_tree
    dist, _ = tree.query(coords, k=1)

    tp_mask = dist <= TP_CUTOFF_M
    tp_dist = dist[tp_mask]
    n_tp = int(tp_mask.sum())
    tp_rate = float(n_tp / n_total) if n_total else 0.0
    print(
        f"  n_detections={n_total}  n_tp_at_25m={n_tp}"
        f"  tp_rate={tp_rate:.3f}"
    )

    desc = descriptors(tp_dist)
    return {
        "key": spec.key,
        "label": spec.label,
        "corpus": spec.corpus,
        "n_detections": int(n_total),
        "n_tp_at_25m": n_tp,
        "tp_rate_at_25m": round(tp_rate, 4),
        "descriptors": desc,
        "_tp_distances_m": tp_dist.tolist(),  # consumed by K-S, dropped at JSON-write time
    }


# --- Pairwise Kolmogorov-Smirnov tests ---


def ks_pairwise(per_cond: list[dict]) -> list[dict]:
    """
    Pairwise K-S tests between GS and each 55-map condition.

    K-S is two-sided: tests whether the empirical CDFs of two TP
    distance samples are drawn from the same distribution. Reported
    statistic + p-value are non-corrected; with 4 pairs (GS vs each
    55-map) the Bonferroni-corrected α is 0.0125.
    """
    gs_record = next(r for r in per_cond if r["corpus"] == "gs")
    gs_dist = np.array(gs_record["_tp_distances_m"])
    out: list[dict] = []
    for r in per_cond:
        if r["corpus"] == "gs":
            continue
        other = np.array(r["_tp_distances_m"])
        if len(gs_dist) == 0 or len(other) == 0:
            stat, pvalue = float("nan"), float("nan")
        else:
            ks_result = ks_2samp(gs_dist, other, alternative="two-sided")
            stat = float(ks_result.statistic)
            pvalue = float(ks_result.pvalue)
        out.append(
            {
                "pair": f"{gs_record['key']} vs {r['key']}",
                "gs_n": int(len(gs_dist)),
                "other_n": int(len(other)),
                "ks_statistic": round(stat, 4) if np.isfinite(stat) else None,
                "p_value": round(pvalue, 6) if np.isfinite(pvalue) else None,
                "significant_alpha_0.05": bool(pvalue < 0.05)
                if np.isfinite(pvalue)
                else False,
                "significant_bonferroni_4pairs": bool(pvalue < 0.05 / 4)
                if np.isfinite(pvalue)
                else False,
            }
        )
    return out


# --- Output writers ---


def write_json(
    per_cond: list[dict],
    ks_results: list[dict],
    n_gs_ref: int,
    n_55map_ref: int,
    out_path: Path,
) -> None:
    """Write the aggregate per-condition + K-S JSON output."""
    # Strip the in-memory raw-distance arrays before serialising — they
    # are only needed for the K-S tests which already consumed them.
    serialisable = []
    for r in per_cond:
        rec = {k: v for k, v in r.items() if k != "_tp_distances_m"}
        serialisable.append(rec)
    payload = {
        "method": "tp-only-localisation-precision",
        "obs_anchor": "Obs 296 diagnostic test #1; companion to Obs 295 / Obs 298",
        "tp_cutoff_m": TP_CUTOFF_M,
        "histogram_bin_m": HIST_BIN_M,
        "n_gs_reference_mounds": int(n_gs_ref),
        "n_55map_reference_mounds": int(n_55map_ref),
        "conditions": serialisable,
        "ks_pairwise": ks_results,
        "methodological_note": (
            "TP-only diagnostic. One-sided test of detector spatial"
            " precision; does not separate 'tight detector + bad"
            " FP-anchoring' from 'loose detector + good FP-anchoring'."
            " Cleanest single number on detector precision available"
            " from existing data per Obs 296 brief."
        ),
    }
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)


def write_report(
    per_cond: list[dict],
    ks_results: list[dict],
    n_gs_ref: int,
    n_55map_ref: int,
    out_path: Path,
) -> None:
    """Synthesise the report.md with table + interpretation paragraph."""
    lines: list[str] = []
    lines.append("# TP-only localisation precision — Obs 296 diagnostic #1")
    lines.append("")
    lines.append(
        "**Anchor**: Obs 296 (`docs/notes/reflections/working-notes.md`,"
        " 2026-04-28) reframed Obs 295's GS 25 m attractor-pull cap as"
        " 'post-calibration precision on the calibration corpus' rather"
        " than 'fundamental detector spatial precision', and the"
        " 55-map 100/125 m caps (Obs 298) as 'native unfamiliar-map"
        " precision'. This diagnostic separates detector spatial"
        " precision (TP localisation) from FP-anchoring failure modes,"
        " by computing TP-to-GT distance distributions across the five"
        " corpus conditions at a uniform 25 m matching scope."
    )
    lines.append("")
    lines.append(
        f"Reference sets: GS curator-corrected n={n_gs_ref};"
        f" 55-map post-review n={n_55map_ref}. TP filter: nearest-GT"
        f" distance ≤ {TP_CUTOFF_M:.0f} m, applied uniformly across"
        " all five conditions (no per-corpus cap difference)."
    )
    lines.append("")

    # Per-condition descriptor table
    lines.append("## 1. Per-condition TP distance descriptors")
    lines.append("")
    rows = []
    for r in per_cond:
        d = r["descriptors"]
        rows.append(
            {
                "condition": r["label"],
                "n_detections": r["n_detections"],
                "n_tp_at_25m": r["n_tp_at_25m"],
                "tp_rate": round(r["tp_rate_at_25m"], 3),
                "mean_m": d["mean_m"],
                "median_m": d["median_m"],
                "p75_m": d["p75_m"],
                "p90_m": d["p90_m"],
                "p95_m": d["p95_m"],
            }
        )
    df = pd.DataFrame(rows)
    lines.append(df.to_markdown(index=False))
    lines.append("")

    # Histogram
    lines.append("## 2. Histogram counts (5 m bins)")
    lines.append("")
    bin_labels = [
        f"({int(b['bin_lo_m'])}, {int(b['bin_hi_m'])}]"
        for b in per_cond[0]["descriptors"]["histogram_5m_bins"]
    ]
    hist_rows = []
    for r in per_cond:
        rec = {"condition": r["label"]}
        for label, b in zip(
            bin_labels, r["descriptors"]["histogram_5m_bins"]
        ):
            rec[label] = b["count"]
        hist_rows.append(rec)
    lines.append(pd.DataFrame(hist_rows).to_markdown(index=False))
    lines.append("")

    # K-S pairwise table
    lines.append("## 3. Pairwise Kolmogorov–Smirnov tests (GS vs each 55-map)")
    lines.append("")
    lines.append(pd.DataFrame(ks_results).to_markdown(index=False))
    lines.append("")

    # Interpretation
    lines.append("## 4. Interpretation")
    lines.append("")
    gs_record = next(r for r in per_cond if r["corpus"] == "gs")
    gs_med = gs_record["descriptors"]["median_m"]
    gs_p90 = gs_record["descriptors"]["p90_m"]
    m55 = [r for r in per_cond if r["corpus"] == "55map"]
    m55_med = [r["descriptors"]["median_m"] for r in m55]
    m55_p90 = [r["descriptors"]["p90_m"] for r in m55]

    # Compare distributions: GS narrower if both median and p90 are
    # lower than every 55-map condition's; tighter overlap if 55-map
    # medians fall within ~3 m of the GS median.
    if gs_med is None or any(x is None for x in m55_med + m55_p90):
        verdict = (
            "Insufficient data to render a verdict (some conditions"
            " yielded zero TPs at 25 m)."
        )
    else:
        gs_strictly_tighter = all(
            gs_med < med and gs_p90 < p90
            for med, p90 in zip(m55_med, m55_p90)
        )
        m55_close_to_gs = all(abs(med - gs_med) <= 3.0 for med in m55_med)
        if gs_strictly_tighter and not m55_close_to_gs:
            verdict = (
                f"**Verdict — detector spatial precision genuinely"
                f" differs.** GS median TP distance ({gs_med:.2f} m,"
                f" p90 {gs_p90:.2f} m) is tighter than every 55-map"
                f" condition (medians"
                f" {min(m55_med):.2f}–{max(m55_med):.2f} m, p90"
                f" {min(m55_p90):.2f}–{max(m55_p90):.2f} m). The GS"
                " calibration tightened TP localisation, not just FP"
                " suppression. Obs 296's failure-of-generalisation"
                " framing is partly correct but spatial precision is"
                " also a real component of the cap difference."
            )
        elif m55_close_to_gs:
            verdict = (
                f"**Verdict — spatial precision is approximately"
                f" constant across corpuses.** GS median TP distance"
                f" ({gs_med:.2f} m) and 55-map medians"
                f" ({min(m55_med):.2f}–{max(m55_med):.2f} m) overlap"
                " within ±3 m. The cap difference between GS and"
                " 55-map is therefore driven by FP-anchoring, not by"
                " detector spatial precision. Obs 296's"
                " failure-of-generalisation framing is fully supported"
                " by this diagnostic."
            )
        else:
            verdict = (
                "**Verdict — mixed.** Some 55-map conditions overlap"
                f" GS (median {gs_med:.2f} m,"
                f" 55-map medians {min(m55_med):.2f}"
                f"–{max(m55_med):.2f} m); others diverge. Detector"
                " precision varies by 55-map run. Cap difference is"
                " partly FP-anchoring and partly spatial precision."
            )
    lines.append(verdict)
    lines.append("")

    lines.append("## 5. Reproducibility")
    lines.append("")
    lines.append(
        "Script: `scripts/analyse_tp_localisation_55maps_vs_gs.py`"
        " (ruff-clean). KDTree query only — no permutations, no random"
        " seed required. Rerun with"
        " `python scripts/analyse_tp_localisation_55maps_vs_gs.py`"
        " from the repo root."
    )
    lines.append("")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")


def render_figure(per_cond: list[dict], out_path: Path) -> None:
    """
    5-condition overlay histogram of TP-to-GT distances in 5 m bins.

    Plots the **proportion** of each condition's TPs in each bin so
    different sample sizes can be compared on equal footing. GS is the
    only condition in its corpus and uses a distinct colour; the four
    55-map conditions share a colour family for visual grouping.
    """
    try:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        print("  matplotlib not available; skipping figure")
        return

    fig, ax = plt.subplots(figsize=(9.0, 5.4))
    bin_lo = [
        b["bin_lo_m"]
        for b in per_cond[0]["descriptors"]["histogram_5m_bins"]
    ]
    bin_hi = [
        b["bin_hi_m"]
        for b in per_cond[0]["descriptors"]["histogram_5m_bins"]
    ]
    bin_centres = np.array(
        [(lo + hi) / 2 for lo, hi in zip(bin_lo, bin_hi)]
    )
    n_conds = len(per_cond)
    width_each = HIST_BIN_M / (n_conds + 1)

    colours = {
        "gs-text-high-t0.7": "C3",  # red — GS singleton
        "55map-t0.3": "C0",
        "55map-t0.7": "C1",
        "55map-image": "C2",
        "55map-text-min": "C4",
    }

    for i, r in enumerate(per_cond):
        n_tp = r["descriptors"]["n_tp"]
        if n_tp == 0:
            continue
        proportions = [
            b["count"] / n_tp
            for b in r["descriptors"]["histogram_5m_bins"]
        ]
        offset = (i - (n_conds - 1) / 2) * width_each
        ax.bar(
            bin_centres + offset,
            proportions,
            width=width_each,
            color=colours.get(r["key"], "grey"),
            label=f"{r['label']} (n_TP={n_tp})",
            edgecolor="black",
            linewidth=0.4,
        )

    ax.set_xlabel("TP-to-nearest-GT distance (m)")
    ax.set_ylabel("Proportion of TPs in bin")
    ax.set_title(
        f"TP-only localisation precision (≤ {int(TP_CUTOFF_M)} m matching"
        " scope)\nGS vs 4 corrected 55-map conditions"
    )
    ax.set_xticks(bin_centres)
    ax.set_xticklabels(
        [f"({int(lo)}, {int(hi)}]" for lo, hi in zip(bin_lo, bin_hi)]
    )
    ax.grid(True, axis="y", alpha=0.3)
    ax.legend(loc="upper right", fontsize=9)
    fig.tight_layout()
    fig.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close(fig)


# --- Main driver ---


def main() -> int:
    """Drive end-to-end: load references, analyse 5 conditions, write outputs."""
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / "figures").mkdir(parents=True, exist_ok=True)

    print("[1/3] Loading reference inputs...")
    gs_tree, n_gs_ref = load_reference_kdtree(GS_REFERENCE)
    m55_tree, n_55map_ref = load_reference_kdtree(M55_REFERENCE)
    print(f"  GS ref: {n_gs_ref} mounds; 55-map ref: {n_55map_ref} mounds")

    print("[2/3] Per-condition analyses...")
    per_cond: list[dict] = []
    for spec in CONDITIONS:
        per_cond.append(analyse_condition(spec, gs_tree, m55_tree))

    print("[3/3] K-S tests + writing outputs...")
    ks_results = ks_pairwise(per_cond)

    write_json(
        per_cond,
        ks_results,
        n_gs_ref,
        n_55map_ref,
        OUT_DIR / "tp_localisation.json",
    )
    write_report(
        per_cond,
        ks_results,
        n_gs_ref,
        n_55map_ref,
        OUT_DIR / "report.md",
    )
    render_figure(per_cond, OUT_DIR / "figures/tp_distance_histogram.png")

    # Console summary
    summary = {
        "per_condition": [
            {
                "key": r["key"],
                "n_tp_at_25m": r["n_tp_at_25m"],
                "median_m": r["descriptors"]["median_m"],
                "p90_m": r["descriptors"]["p90_m"],
            }
            for r in per_cond
        ],
        "ks_pairwise": ks_results,
    }
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
