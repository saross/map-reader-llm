#!/usr/bin/env python3
# ---------------------------------------------------------------------------
# analyse_ds_vs_human_review.py
# ---------------------------------------------------------------------------
# Purpose
# -------
# Cross-tabulate the Dawid-Skene (D-S) aggregate per-item posterior
# probability against the combined human-review labels on the 55-map
# image-generalisation VLM-only candidate set.
#
# Framing — "aggregate estimates rate, human disambiguates individuals":
# the D-S posterior is an aggregate probability of mound-vs-not across
# noisy annotators (student digitisers + VLM pipeline), whereas human
# review is a per-candidate adjudication. This script quantifies where
# they agree and where they diverge, and compares the D-S calibration to
# the verifier calibration numbers already reported in Observation 269
# (ECE = 0.269, AUC = 0.655, Brier = 0.323).
#
# Important structural note
# -------------------------
# The D-S model in this project has exactly two binary annotators
# (student digitiser vote vs. VLM pipeline vote). With only two annotators
# the model is **not identifiable at the item level within a response
# pattern** — every VLM-only item (student=0, vlm=1) receives the same
# posterior, P(true=1 | s=0, v=1) ≈ 0.186. See
# results/55maps-image-generalisation/dawid-skene/dawid-skene-results.md.
# All calibration / discrimination statistics reported here therefore
# measure the aggregate-rate claim, not an item-level discriminator.
#
# Inputs (relative to repo root)
# ------------------------------
# - results/55maps-image-generalisation/dawid-skene/item-posteriors.csv
#     Columns: item_id, student_label, vlm_label, vlm_probability,
#              map_name, category, x, y, posterior_p_true, latent_truth.
# - results/55maps-image-generalisation/human-review.csv
#     Yesterday's 1,028-row review (50 m tolerance). Join key:
#     (map_name, x, y).
# - results/55maps-image-generalisation/human-review-multi-buffer.csv
#     Today's 557-row re-review, with buffer_band in
#     {50, 75, 100, 125, 150, 200}. buffer_metres = 200 is the sentinel
#     for "mound visible beyond 150 m".
#
# Outputs (results/55maps-image-generalisation/ds-human-crosstab/)
# ---------------------------------------------------------------
# - crosstab_coarse.csv      2x2 table counts (D-S > 0.5 vs human mound).
# - reliability.csv          Per-bin counts, predicted, empirical, gap, CI.
# - buffer_band_vs_ds.csv    Per-buffer-band mean D-S posterior with CI.
# - summary.json             Machine-readable ECE, Brier, AUC, 2x2 P/R/F1,
#                            ambiguity-band isolation counts, provenance.
# - reliability_plot.png     Reliability diagram (x = mean predicted,
#                            y = empirical; bin-size scaled markers).
# - buffer_scatter.png       Scatter of D-S posterior vs buffer_band for
#                            mound candidates.
# - report.md                Narrative report with tables + interpretation.
#
# Methodology
# -----------
# Combined human-review label per candidate:
#   - Yesterday mound (all at 50 m)                       -> mound
#   - Yesterday not_mound; today mound at R in {50..200}  -> mound
#   - Yesterday not_mound; today not_mound                -> not_mound
#   - Yesterday not_mound; today uncertain                -> not_mound
#     (but reported separately in the summary).
#   - Today-only candidate (not in yesterday)             -> today's label.
#
# Join D-S posterior to the combined review on (map_name, x, y).
# The VLM-only subset of the D-S item table is the 1,028 items present
# in the human-review pipeline; expect 1,028 joined rows (with possibly
# one extra from today-only entries).
#
# Calibration metrics:
#   - Expected Calibration Error (ECE) with 10 equal-width bins.
#   - Brier score.
#   - Area Under the ROC Curve (AUC).
#   - 2x2 cross-tab at threshold 0.5 (precision / recall / F1).
#   - Reliability diagram (10-bin).
#   - Ambiguity-band isolation: counts and human-mound rate inside
#     [0.3, 0.7] vs. inside [0, 0.1) U (0.9, 1.0].
#
# Usage
# -----
#   python3 scripts/analyse_ds_vs_human_review.py \
#       --ds-csv results/55maps-image-generalisation/dawid-skene/item-posteriors.csv \
#       --review-yesterday results/55maps-image-generalisation/human-review.csv \
#       --review-today results/55maps-image-generalisation/human-review-multi-buffer.csv \
#       --out results/55maps-image-generalisation/ds-human-crosstab
#
# Language: UK/Australian English throughout.
# Compute: local workstation OK (< 1 second of arithmetic on < 1,200 rows).
# ---------------------------------------------------------------------------

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # headless backend
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.metrics import brier_score_loss, roc_auc_score

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# Today's "mound visible beyond 150 m" sentinel.
SENTINEL_BUFFER_EXCLUDED: float = 200.0

# Reliability diagram uses 10 equal-width bins.
N_RELIABILITY_BINS: int = 10

# Ambiguity-band thresholds.
AMBIGUOUS_LO: float = 0.30
AMBIGUOUS_HI: float = 0.70
CONFIDENT_LO: float = 0.10
CONFIDENT_HI: float = 0.90

# Observation 269 comparator numbers (verifier calibration on this set).
VERIFIER_ECE: float = 0.2689
VERIFIER_BRIER: float = 0.3226
VERIFIER_AUC: float = 0.6545


# ---------------------------------------------------------------------------
# Data assembly
# ---------------------------------------------------------------------------


def build_combined_review(
    review_yesterday: pd.DataFrame,
    review_today: pd.DataFrame,
) -> pd.DataFrame:
    """Construct the single-definitive per-candidate human-review label.

    Logic (see module docstring for full spec):
    - Yesterday mound (frozen 50 m TP)                      -> mound.
    - Yesterday not_mound, today mound (any buffer_band)    -> mound.
    - Yesterday not_mound, today not_mound                  -> not_mound.
    - Yesterday not_mound, today uncertain                  -> not_mound
      (but counted in ``n_today_uncertain`` for transparency).
    - Today-only (candidate not in yesterday's review)      -> today's label.

    Args:
        review_yesterday: Yesterday's 1,028-row review DataFrame.
        review_today: Today's 557-row multi-buffer review DataFrame.

    Returns:
        DataFrame with columns:
          candidate_id, map_name, x, y, symbol_type, combined_label,
          buffer_band, source (``yesterday_mound`` / ``today_mound`` /
          ``today_not_mound`` / ``today_uncertain`` / ``today_only``).
    """
    y = review_yesterday.set_index("candidate_id")
    t = review_today.set_index("candidate_id")

    combined_rows: list[dict] = []

    # Pass 1: every candidate from yesterday's review.
    for cid, row in y.iterrows():
        y_label = row["human_label"]
        if y_label == "mound":
            combined_rows.append(
                {
                    "candidate_id": cid,
                    "map_name": row["map_name"],
                    "x": row["x"],
                    "y": row["y"],
                    "symbol_type": row["symbol_type"],
                    "combined_label": "mound",
                    "buffer_band": 50.0,
                    "source": "yesterday_mound",
                }
            )
            continue
        # Yesterday not_mound (or uncertain — not observed in practice).
        if cid in t.index:
            t_row = t.loc[cid]
            t_label = t_row["human_label"]
            if t_label == "mound":
                combined_rows.append(
                    {
                        "candidate_id": cid,
                        "map_name": row["map_name"],
                        "x": row["x"],
                        "y": row["y"],
                        "symbol_type": t_row["symbol_type"],
                        "combined_label": "mound",
                        "buffer_band": float(t_row["buffer_metres"]),
                        "source": "today_mound",
                    }
                )
            elif t_label == "not_mound":
                combined_rows.append(
                    {
                        "candidate_id": cid,
                        "map_name": row["map_name"],
                        "x": row["x"],
                        "y": row["y"],
                        "symbol_type": row["symbol_type"],
                        "combined_label": "not_mound",
                        "buffer_band": float("nan"),
                        "source": "today_not_mound",
                    }
                )
            else:  # "uncertain"
                combined_rows.append(
                    {
                        "candidate_id": cid,
                        "map_name": row["map_name"],
                        "x": row["x"],
                        "y": row["y"],
                        "symbol_type": row["symbol_type"],
                        "combined_label": "not_mound",
                        "buffer_band": float("nan"),
                        "source": "today_uncertain",
                    }
                )
        else:
            # Yesterday not_mound without today re-review — keep as not_mound.
            combined_rows.append(
                {
                    "candidate_id": cid,
                    "map_name": row["map_name"],
                    "x": row["x"],
                    "y": row["y"],
                    "symbol_type": row["symbol_type"],
                    "combined_label": "not_mound",
                    "buffer_band": float("nan"),
                    "source": "yesterday_not_mound_only",
                }
            )

    # Pass 2: any candidate in today-only (not in yesterday).
    today_only_ids = set(t.index) - set(y.index)
    for cid in sorted(today_only_ids):
        t_row = t.loc[cid]
        t_label = t_row["human_label"]
        if t_label == "mound":
            combined_label = "mound"
            buffer_band = float(t_row["buffer_metres"])
        elif t_label == "not_mound":
            combined_label = "not_mound"
            buffer_band = float("nan")
        else:
            combined_label = "not_mound"  # today-uncertain -> not_mound
            buffer_band = float("nan")
        combined_rows.append(
            {
                "candidate_id": cid,
                "map_name": t_row["map_name"],
                "x": t_row["x"],
                "y": t_row["y"],
                "symbol_type": t_row["symbol_type"],
                "combined_label": combined_label,
                "buffer_band": buffer_band,
                "source": "today_only",
            }
        )

    combined = pd.DataFrame(combined_rows)
    return combined


def join_ds_to_review(
    ds_posteriors: pd.DataFrame,
    combined_review: pd.DataFrame,
) -> pd.DataFrame:
    """Inner-join D-S posteriors to the combined review on (map_name, x, y).

    candidate_id in the review CSVs and item_id in the D-S CSV are
    different index schemes, so we key on the (map_name, x, y) triple
    which is identical across the two pipelines for VLM-only items.

    Args:
        ds_posteriors: D-S per-item posterior DataFrame.
        combined_review: Combined-label DataFrame from build_combined_review.

    Returns:
        DataFrame containing review rows with added columns:
          ``ds_item_id``, ``ds_posterior``, ``ds_student_label``,
          ``ds_vlm_label``, ``ds_vlm_probability``.
    """
    ds_keyed = ds_posteriors.copy()
    ds_keyed = ds_keyed.rename(
        columns={
            "item_id": "ds_item_id",
            "student_label": "ds_student_label",
            "vlm_label": "ds_vlm_label",
            "vlm_probability": "ds_vlm_probability",
            "posterior_p_true": "ds_posterior",
        }
    )
    # Round keys to avoid float-equality issues — the CSVs preserve full
    # precision so string comparison would work too, but rounding to 3 dp
    # is safer and sufficient for this spatial precision.
    ds_keyed["_x_round"] = ds_keyed["x"].round(3)
    ds_keyed["_y_round"] = ds_keyed["y"].round(3)
    combined = combined_review.copy()
    combined["_x_round"] = combined["x"].round(3)
    combined["_y_round"] = combined["y"].round(3)

    merged = combined.merge(
        ds_keyed[
            [
                "ds_item_id",
                "ds_student_label",
                "ds_vlm_label",
                "ds_vlm_probability",
                "ds_posterior",
                "map_name",
                "_x_round",
                "_y_round",
            ]
        ],
        on=["map_name", "_x_round", "_y_round"],
        how="left",
    )
    merged = merged.drop(columns=["_x_round", "_y_round"])
    return merged


# ---------------------------------------------------------------------------
# Calibration analysis
# ---------------------------------------------------------------------------


def wilson_ci(k: int, n: int, z: float = 1.96) -> tuple[float, float]:
    """Wilson 95 % confidence interval for a binomial proportion.

    Args:
        k: number of successes (e.g. mounds in bin).
        n: sample size in bin.
        z: normal-distribution critical value (default 1.96 for 95 %).

    Returns:
        (lo, hi) — Wilson interval; returns (nan, nan) for n = 0.
    """
    if n == 0:
        return float("nan"), float("nan")
    p = k / n
    denom = 1 + (z**2) / n
    centre = p + (z**2) / (2 * n)
    halfwidth = z * math.sqrt((p * (1 - p) / n) + (z**2) / (4 * n**2))
    lo = (centre - halfwidth) / denom
    hi = (centre + halfwidth) / denom
    return float(lo), float(hi)


def reliability_bins(
    p: np.ndarray,
    y: np.ndarray,
    n_bins: int = N_RELIABILITY_BINS,
) -> pd.DataFrame:
    """Compute per-bin calibration statistics across equal-width bins.

    Edges are ``[0, 1/n_bins, 2/n_bins, ..., 1]``. The last bin is
    right-closed to include posterior = 1.0 exactly.

    Returns:
        DataFrame with one row per bin and columns:
          bin_idx, bin_lo, bin_hi, n, n_mound, mean_predicted,
          empirical_p, gap, wilson_lo, wilson_hi.
    """
    edges = np.linspace(0, 1, n_bins + 1)
    rows: list[dict] = []
    for i in range(n_bins):
        lo = float(edges[i])
        hi = float(edges[i + 1])
        if i == n_bins - 1:
            mask = (p >= lo) & (p <= hi)
        else:
            mask = (p >= lo) & (p < hi)
        n = int(mask.sum())
        n_mound = int(y[mask].sum()) if n > 0 else 0
        mean_p = float(p[mask].mean()) if n > 0 else float("nan")
        emp = float(n_mound / n) if n > 0 else float("nan")
        gap = mean_p - emp if n > 0 else float("nan")
        w_lo, w_hi = wilson_ci(n_mound, n) if n > 0 else (float("nan"), float("nan"))
        rows.append(
            {
                "bin_idx": i,
                "bin_lo": lo,
                "bin_hi": hi,
                "n": n,
                "n_mound": n_mound,
                "mean_predicted": mean_p,
                "empirical_p": emp,
                "gap_pred_minus_emp": gap,
                "wilson_lo": w_lo,
                "wilson_hi": w_hi,
            }
        )
    return pd.DataFrame(rows)


def expected_calibration_error(bins: pd.DataFrame, total: int) -> float:
    """Weighted average of |empirical - predicted| across populated bins."""
    ece = 0.0
    for _, r in bins.iterrows():
        if r["n"] == 0:
            continue
        ece += (r["n"] / total) * abs(r["empirical_p"] - r["mean_predicted"])
    return float(ece)


def coarse_crosstab(
    p: np.ndarray, y: np.ndarray, threshold: float = 0.5
) -> tuple[dict, dict]:
    """2x2 cross-tab of (D-S > threshold) vs. human mound label.

    Returns:
        (counts_dict, metrics_dict) — counts for TP/FP/FN/TN plus
        precision / recall / F1 of the thresholded D-S posterior as a
        classifier against ``y_true == mound``.
    """
    pred_mound = p > threshold
    actual_mound = y == 1
    tp = int(np.sum(pred_mound & actual_mound))
    fp = int(np.sum(pred_mound & ~actual_mound))
    fn = int(np.sum(~pred_mound & actual_mound))
    tn = int(np.sum(~pred_mound & ~actual_mound))
    counts = {"tp": tp, "fp": fp, "fn": fn, "tn": tn, "threshold": threshold}
    precision = tp / (tp + fp) if (tp + fp) > 0 else float("nan")
    recall = tp / (tp + fn) if (tp + fn) > 0 else float("nan")
    f1 = (
        2 * precision * recall / (precision + recall)
        if (
            not math.isnan(precision)
            and not math.isnan(recall)
            and (precision + recall) > 0
        )
        else float("nan")
    )
    metrics = {"precision": precision, "recall": recall, "f1": f1}
    return counts, metrics


def ambiguity_band_isolation(p: np.ndarray, y: np.ndarray) -> dict:
    """Compare human-mound rates inside the ambiguous and confident bands.

    Ambiguous band: ``AMBIGUOUS_LO <= p <= AMBIGUOUS_HI``
                    (default [0.3, 0.7]).
    Confident band: ``p < CONFIDENT_LO or p > CONFIDENT_HI``
                    (default [0, 0.1) U (0.9, 1.0]).
    """
    amb_mask = (p >= AMBIGUOUS_LO) & (p <= AMBIGUOUS_HI)
    conf_mask = (p < CONFIDENT_LO) | (p > CONFIDENT_HI)

    amb_n = int(amb_mask.sum())
    amb_mounds = int(y[amb_mask].sum()) if amb_n > 0 else 0
    amb_rate = amb_mounds / amb_n if amb_n > 0 else float("nan")
    amb_lo, amb_hi = wilson_ci(amb_mounds, amb_n)

    conf_n = int(conf_mask.sum())
    conf_mounds = int(y[conf_mask].sum()) if conf_n > 0 else 0
    conf_rate = conf_mounds / conf_n if conf_n > 0 else float("nan")
    conf_lo, conf_hi = wilson_ci(conf_mounds, conf_n)

    middle_n = int(len(p) - amb_n - conf_n)
    middle_mounds = int(y.sum() - amb_mounds - conf_mounds)
    middle_rate = middle_mounds / middle_n if middle_n > 0 else float("nan")

    return {
        "ambiguous_band": {
            "range_lo": AMBIGUOUS_LO,
            "range_hi": AMBIGUOUS_HI,
            "n": amb_n,
            "n_mound": amb_mounds,
            "human_mound_rate": amb_rate,
            "wilson_lo": amb_lo,
            "wilson_hi": amb_hi,
        },
        "confident_band": {
            "range_lo": CONFIDENT_LO,
            "range_hi": CONFIDENT_HI,
            "n": conf_n,
            "n_mound": conf_mounds,
            "human_mound_rate": conf_rate,
            "wilson_lo": conf_lo,
            "wilson_hi": conf_hi,
        },
        "middle_band": {
            "n": middle_n,
            "n_mound": middle_mounds,
            "human_mound_rate": middle_rate,
        },
    }


def buffer_band_summary(joined: pd.DataFrame) -> pd.DataFrame:
    """Per-buffer-band mean D-S posterior + 95 % CI for mound candidates.

    Groups mound rows by buffer_band (50, 75, 100, 125, 150, 200) and
    returns mean posterior, n, standard deviation, and normal-theory
    95 % CI on the mean.
    """
    mounds = joined[joined["combined_label"] == "mound"].copy()
    rows: list[dict] = []
    for band, sub in mounds.groupby("buffer_band", dropna=False):
        n = int(len(sub))
        mean_p = float(sub["ds_posterior"].mean()) if n > 0 else float("nan")
        sd = float(sub["ds_posterior"].std(ddof=1)) if n > 1 else 0.0
        se = sd / math.sqrt(n) if n > 0 else float("nan")
        ci_lo = mean_p - 1.96 * se if n > 0 else float("nan")
        ci_hi = mean_p + 1.96 * se if n > 0 else float("nan")
        rows.append(
            {
                "buffer_band": float(band) if not pd.isna(band) else float("nan"),
                "n": n,
                "mean_ds_posterior": mean_p,
                "sd": sd,
                "ci_lo": ci_lo,
                "ci_hi": ci_hi,
            }
        )
    return pd.DataFrame(rows).sort_values("buffer_band").reset_index(drop=True)


# ---------------------------------------------------------------------------
# Plotting
# ---------------------------------------------------------------------------


def plot_reliability(bins: pd.DataFrame, out_path: Path) -> None:
    """Save the reliability diagram (scatter vs y = x reference)."""
    populated = bins[bins["n"] > 0].copy()
    if populated.empty:
        return
    xs = populated["mean_predicted"].to_numpy()
    ys = populated["empirical_p"].to_numpy()
    sizes = np.clip(populated["n"].to_numpy() / 2, 30, 600)

    fig, ax = plt.subplots(figsize=(7, 6))
    ax.plot([0, 1], [0, 1], linestyle="--", color="grey",
            label="perfect calibration (y = x)")
    sc = ax.scatter(
        xs, ys, s=sizes, alpha=0.75, edgecolor="black", zorder=3,
        label="D-S posterior bins",
    )
    # Error bars from Wilson CI on empirical.
    lo = populated["wilson_lo"].to_numpy()
    hi = populated["wilson_hi"].to_numpy()
    ax.errorbar(
        xs, ys, yerr=[ys - lo, hi - ys], fmt="none",
        color="black", alpha=0.5, capsize=3, zorder=2,
    )
    for _, r in populated.iterrows():
        ax.annotate(
            f"n = {int(r['n'])}",
            (r["mean_predicted"], r["empirical_p"]),
            textcoords="offset points", xytext=(8, -4), fontsize=8,
        )
    ax.set_xlabel("Mean predicted P(mound) within bin (D-S posterior)")
    ax.set_ylabel("Empirical P(mound) within bin (human review)")
    ax.set_title(
        "Dawid-Skene posterior reliability diagram\n"
        "(point size proportional to bin count; 95 % Wilson CI on empirical)"
    )
    ax.set_xlim(-0.02, 1.02)
    ax.set_ylim(-0.02, 1.02)
    ax.grid(True, alpha=0.3)
    ax.legend(loc="lower right")
    fig.tight_layout()
    fig.savefig(out_path, dpi=150)
    plt.close(fig)
    del sc


def plot_buffer_scatter(joined: pd.DataFrame, out_path: Path) -> None:
    """Scatter D-S posterior against buffer_band for mound candidates."""
    mounds = joined[joined["combined_label"] == "mound"].copy()
    if mounds.empty or mounds["buffer_band"].isna().all():
        return
    fig, ax = plt.subplots(figsize=(7, 5))
    # Tiny horizontal jitter so overlapping points are visible.
    rng = np.random.default_rng(42)
    jitter = rng.uniform(-0.02, 0.02, size=len(mounds))
    ax.scatter(
        mounds["ds_posterior"] + jitter,
        mounds["buffer_band"],
        alpha=0.5, s=25, edgecolor="black", linewidth=0.4,
    )
    ax.set_xlabel("D-S posterior P(true mound)")
    ax.set_ylabel("Buffer band (m) at which human confirmed mound")
    ax.set_title(
        "D-S posterior vs. review buffer band (human-confirmed mounds)\n"
        "buffer = 200 is the sentinel for ‘visible beyond 150 m’"
    )
    ax.set_xlim(-0.02, 1.02)
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(out_path, dpi=150)
    plt.close(fig)


# ---------------------------------------------------------------------------
# Reporting
# ---------------------------------------------------------------------------


def render_report_md(
    summary: dict,
    bins: pd.DataFrame,
    coarse_counts: dict,
    coarse_metrics: dict,
    buffer_df: pd.DataFrame,
    ambiguity: dict,
    degenerate: bool,
    unique_posterior_values: list[float],
) -> str:
    """Produce the human-readable Markdown report."""
    # Derive a run label from the D-S posteriors path so the title is
    # accurate when the script is invoked on text or T=0.3 runs as well
    # as the original image run.
    ds_path = str(summary["inputs"].get("ds_posteriors", ""))
    if "55maps-image" in ds_path:
        run_label = "55-map image generalisation"
    elif "55maps-text-high-t0.3" in ds_path:
        run_label = "55-map text HIGH T=0.3 generalisation"
    elif "55maps-text-high" in ds_path:
        run_label = "55-map text HIGH T=0.7 generalisation"
    elif "55maps-text-min" in ds_path:
        run_label = "55-map text MIN generalisation"
    else:
        run_label = "(run label unknown — see provenance)"

    lines: list[str] = []
    lines.append(
        "# Dawid-Skene aggregate posterior vs. human review "
        f"({run_label})"
    )
    lines.append("")
    lines.append(
        "Cross-tabulation of the Dawid-Skene (D-S) per-item posterior "
        "against the combined human-review labels on the VLM-only "
        "candidate set. Framing: the D-S posterior is an **aggregate** "
        "probabilistic estimate derived from two noisy annotators "
        "(student digitisers and the VLM pipeline); human review is a "
        "per-candidate adjudication. This analysis quantifies where the "
        "aggregate and the individual adjudications agree or diverge."
    )
    lines.append("")
    lines.append("## Input provenance")
    lines.append("")
    for k, v in summary["inputs"].items():
        lines.append(f"- **{k}**: `{v}`")
    lines.append("")

    lines.append("## Sample composition")
    lines.append("")
    lines.append(f"- Combined review rows: **{summary['n_combined']}**")
    lines.append(f"- Rows successfully joined to D-S posterior: "
                 f"**{summary['n_joined']}**")
    lines.append(f"- Unjoined rows (no D-S posterior found): "
                 f"**{summary['n_unjoined']}**")
    lines.append(f"- Human-mound prevalence in joined set: "
                 f"**{summary['prevalence']:.3f}** "
                 f"({summary['n_mound']}/{summary['n_joined']})")
    lines.append("")
    lines.append("### Combined-label source breakdown")
    lines.append("")
    lines.append("| Source | Count |")
    lines.append("|--------|------:|")
    for src, c in summary["source_counts"].items():
        lines.append(f"| {src} | {c} |")
    lines.append("")

    lines.append("## Structural note — D-S 2-annotator identifiability")
    lines.append("")
    if degenerate:
        # Use the actual joined-row count from the summary so this
        # paragraph is accurate for non-image runs as well.
        n_joined = int(summary.get("n_joined", 0))
        lines.append(
            "With only two binary annotators (student vote, VLM vote) "
            "the Dawid-Skene model assigns an **identical posterior** "
            "to every item that shares the same annotator response "
            f"pattern. All {n_joined:,} VLM-only items "
            "(student = 0, VLM = 1) receive the same posterior value "
            f"({unique_posterior_values[0]:.4f}). Consequently:"
        )
        lines.append("")
        lines.append(
            "- The D-S posterior on this slice is a single point "
            "estimate of the **aggregate rate** of true mounds in the "
            "VLM-only cohort, not an item-level discriminator."
        )
        lines.append(
            "- The reliability diagram has exactly one populated bin."
        )
        lines.append(
            "- The AUC of the D-S posterior as a classifier is "
            "undefined (degenerate ordering) and defaults to 0.5."
        )
        lines.append(
            "- The 2 x 2 cross-tab at threshold 0.5 collapses "
            "(posterior < 0.5 for all rows)."
        )
        lines.append("")
        # Use this run's posterior + prevalence so the diagnostic line
        # is accurate for every run, not just the original image run.
        post_val = (
            unique_posterior_values[0] if unique_posterior_values else 0.0
        )
        prev_val = float(summary.get("prevalence", 0.0))
        lines.append(
            "**Framing check.** The expected pattern was ‘aggregate "
            "estimates rate, human disambiguates individuals’. On this "
            "slice, the D-S aggregate is *not* close to the empirical "
            f"rate ({post_val:.3f} predicted vs. {prev_val:.3f} "
            "observed) — see interpretation section 6 for the prior-"
            "misspecification diagnosis. The identifiability argument "
            "still holds — the D-S posterior cannot rank individuals "
            "by construction — but the aggregate itself is badly "
            "miscalibrated here, so the framing needs qualification "
            "rather than confirmation."
        )
    else:
        lines.append(
            f"{len(unique_posterior_values)} distinct D-S posterior "
            "values were observed on the joined VLM-only slice; the "
            "model therefore has some item-level discrimination on "
            "this subset."
        )
    lines.append("")

    lines.append("## 1. Coarse cross-tab (D-S > 0.5 vs. human mound)")
    lines.append("")
    lines.append("| | Human mound | Human not_mound |")
    lines.append("|---|---:|---:|")
    lines.append(f"| **D-S > 0.5** | {coarse_counts['tp']} | "
                 f"{coarse_counts['fp']} |")
    lines.append(f"| **D-S ≤ 0.5** | {coarse_counts['fn']} | "
                 f"{coarse_counts['tn']} |")
    lines.append("")
    lines.append(f"- Precision: {coarse_metrics['precision']:.4f}")
    lines.append(f"- Recall:    {coarse_metrics['recall']:.4f}")
    lines.append(f"- F1:        {coarse_metrics['f1']:.4f}")
    lines.append("")

    lines.append("## 2. Reliability diagram (10 equal-width bins)")
    lines.append("")
    lines.append(
        "| Bin | n | n_mound | Mean predicted P | Empirical P | "
        "Gap (pred − emp) | 95 % Wilson CI on empirical |"
    )
    lines.append(
        "|-----|---:|---:|---:|---:|---:|---|"
    )
    for _, r in bins.iterrows():
        if r["n"] == 0:
            continue
        ci = f"[{r['wilson_lo']:.3f}, {r['wilson_hi']:.3f}]"
        lines.append(
            f"| [{r['bin_lo']:.1f}, {r['bin_hi']:.1f}] | "
            f"{int(r['n'])} | {int(r['n_mound'])} | "
            f"{r['mean_predicted']:.4f} | {r['empirical_p']:.4f} | "
            f"{r['gap_pred_minus_emp']:+.4f} | {ci} |"
        )
    lines.append("")
    lines.append(f"- **Expected Calibration Error (ECE, 10 bins):** "
                 f"{summary['ece']:.4f}")
    lines.append(f"- **Brier score:** {summary['brier']:.4f}")
    lines.append(
        f"- **AUC (D-S posterior as mound classifier):** "
        f"{summary['auc']:.4f}" + (
            " *(degenerate — all inputs share one posterior; "
            "no rank information.)*" if summary["auc_degenerate"] else ""
        )
    )
    lines.append("")

    lines.append("## 3. Ambiguity-band isolation")
    lines.append("")
    lines.append(
        "Evidence for ‘human disambiguates individuals, D-S estimates rate’."
    )
    lines.append("")
    lines.append(
        "| Band | Range | n | n_mound | Human-mound rate | 95 % Wilson CI |"
    )
    lines.append(
        "|------|-------|---:|---:|---:|---|"
    )
    amb = ambiguity["ambiguous_band"]
    conf = ambiguity["confident_band"]
    mid = ambiguity["middle_band"]
    lines.append(
        f"| Ambiguous | [{amb['range_lo']:.1f}, {amb['range_hi']:.1f}] | "
        f"{amb['n']} | {amb['n_mound']} | "
        f"{(amb['human_mound_rate'] if not (isinstance(amb['human_mound_rate'], float) and math.isnan(amb['human_mound_rate'])) else float('nan')):.4f} | "
        f"[{amb['wilson_lo']:.3f}, {amb['wilson_hi']:.3f}] |"
    )
    lines.append(
        f"| Confident | [0, {conf['range_lo']:.1f}) ∪ "
        f"({conf['range_hi']:.1f}, 1] | {conf['n']} | {conf['n_mound']} | "
        f"{(conf['human_mound_rate'] if not (isinstance(conf['human_mound_rate'], float) and math.isnan(conf['human_mound_rate'])) else float('nan')):.4f} | "
        f"[{conf['wilson_lo']:.3f}, {conf['wilson_hi']:.3f}] |"
    )
    lines.append(
        f"| Middle remainder | elsewhere | {mid['n']} | {mid['n_mound']} | "
        f"{(mid['human_mound_rate'] if not (isinstance(mid['human_mound_rate'], float) and math.isnan(mid['human_mound_rate'])) else float('nan')):.4f} | — |"
    )
    lines.append("")

    lines.append("## 4. Buffer-band view (D-S posterior vs. review band)")
    lines.append("")
    lines.append(
        "| Buffer band | n | Mean D-S posterior | 95 % CI |"
    )
    lines.append(
        "|------------:|---:|-------------------:|---|"
    )
    for _, r in buffer_df.iterrows():
        band = "200 (sentinel)" if r["buffer_band"] == 200 else f"{int(r['buffer_band'])}"
        ci = f"[{r['ci_lo']:.4f}, {r['ci_hi']:.4f}]"
        lines.append(
            f"| {band} | {int(r['n'])} | {r['mean_ds_posterior']:.4f} | {ci} |"
        )
    lines.append("")

    lines.append("## 5. Comparison to the verifier (Observation 269)")
    lines.append("")
    lines.append(
        "| Metric | D-S posterior | Verifier | Better-calibrated? |"
    )
    lines.append(
        "|--------|--------------:|---------:|-------------------|"
    )
    verdict_ece = (
        "D-S (aggregate calibration)" if summary["ece"] < VERIFIER_ECE
        else "Verifier"
    )
    verdict_brier = (
        "D-S" if summary["brier"] < VERIFIER_BRIER else "Verifier"
    )
    verdict_auc = (
        "Verifier (D-S has no item-level rank)"
        if summary["auc_degenerate"]
        else ("D-S" if summary["auc"] > VERIFIER_AUC else "Verifier")
    )
    lines.append(
        f"| ECE (lower is better) | {summary['ece']:.4f} | "
        f"{VERIFIER_ECE:.4f} | {verdict_ece} |"
    )
    lines.append(
        f"| Brier (lower is better) | {summary['brier']:.4f} | "
        f"{VERIFIER_BRIER:.4f} | {verdict_brier} |"
    )
    lines.append(
        f"| AUC (higher is better) | {summary['auc']:.4f} | "
        f"{VERIFIER_AUC:.4f} | {verdict_auc} |"
    )
    lines.append("")

    lines.append("## 6. Interpretation")
    lines.append("")
    post_val = (
        unique_posterior_values[0] if unique_posterior_values else 0.0
    )
    prev_val = float(summary.get("prevalence", 0.0))
    n_joined = int(summary.get("n_joined", 0))
    n_mound = int(summary.get("n_mound", 0))
    ece_gap = abs(post_val - prev_val)
    ratio = (prev_val / post_val) if post_val > 0 else float("inf")
    lines.append(
        "- **D-S aggregate is badly wrong here — flagged as surprising.** "
        f"The D-S posterior predicts an aggregate mound rate of "
        f"{post_val:.4f} for the VLM-only cohort; the combined human-"
        f"review label finds {prev_val:.4f} ({n_mound:,}/{n_joined:,}). "
        f"The absolute gap is {ece_gap:.3f}; the empirical rate is "
        f"{ratio:.2f}× the D-S estimate. This is the reverse of the "
        "expected framing: rather than ‘aggregate estimates rate well, "
        "human disambiguates individuals’, the D-S aggregate is "
        "systematically under-counting real mounds at the cohort level."
    )
    lines.append(
        "- **Prior-driven artefact.** The D-S run used a fixed prior of "
        "5 % student false-negative rate (see "
        f"`dawid-skene-results.json`). The data imply the student FN "
        f"rate on the VLM-only slice is much higher — the VLM "
        f"independently flagged {n_joined:,}+ locations that students "
        "had not digitised, and human review confirms a substantial "
        "fraction are real mounds at some buffer. A D-S fit with an "
        "honest, data-driven student-FN prior — or with more than two "
        "annotators — would land much closer to the empirical rate."
    )
    lines.append(
        "- **Aggregate vs. individual — revised.** With only two binary "
        "annotators, the D-S posterior collapses to a single value per "
        "response pattern, so it cannot rank individuals by design. "
        "Human review is the only per-candidate signal available on "
        "this slice. The verifier probability (Obs 269) is a graded "
        "item-level signal but is itself poorly calibrated at the high "
        "end. Downstream use should treat D-S as a (currently "
        "miscalibrated) cohort-rate estimator and rely on the verifier "
        "plus human review for item-level discrimination."
    )
    lines.append(
        "- **Buffer-band view.** Because the D-S posterior is "
        "degenerate, mean posterior is identical across every "
        f"buffer band ({post_val:.4f} at all bands). It carries no "
        "information about buffer-band separation, which is "
        "consistent with Obs 268 — the signal for ‘wider-buffer mounds "
        "are genuinely lower-signal’ lives entirely in the verifier "
        "probability, not in the D-S posterior."
    )
    lines.append("")

    lines.append("## Figures")
    lines.append("")
    lines.append("- `reliability_plot.png` — reliability diagram.")
    lines.append(
        "- `buffer_scatter.png` — D-S posterior vs. buffer band for "
        "mound candidates."
    )
    lines.append("")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--ds-csv",
        type=Path,
        default=Path(
            "results/55maps-image-generalisation/dawid-skene/item-posteriors.csv"
        ),
        help="D-S item-posterior CSV.",
    )
    parser.add_argument(
        "--review-yesterday",
        type=Path,
        default=Path(
            "results/55maps-image-generalisation/human-review.csv"
        ),
        help="Yesterday's 1,028-row human-review CSV.",
    )
    parser.add_argument(
        "--review-today",
        type=Path,
        default=Path(
            "results/55maps-image-generalisation/human-review-multi-buffer.csv"
        ),
        help="Today's 557-row multi-buffer human-review CSV.",
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=Path(
            "results/55maps-image-generalisation/ds-human-crosstab"
        ),
        help="Output directory (created if missing).",
    )
    args = parser.parse_args()

    args.out.mkdir(parents=True, exist_ok=True)

    # ----- Load inputs --------------------------------------------------
    ds = pd.read_csv(args.ds_csv)
    ry = pd.read_csv(args.review_yesterday)
    rt = pd.read_csv(args.review_today)

    # ----- Build combined review label ---------------------------------
    combined = build_combined_review(ry, rt)
    source_counts = dict(combined["source"].value_counts())

    # How many today-uncertain rows would have flipped a not_mound?
    n_today_uncertain = int((combined["source"] == "today_uncertain").sum())

    # ----- Join D-S posterior on (map_name, x, y) ----------------------
    joined = join_ds_to_review(ds, combined)
    n_joined_rows = int(joined["ds_posterior"].notna().sum())
    n_unjoined = int(joined["ds_posterior"].isna().sum())
    joined_ok = joined[joined["ds_posterior"].notna()].copy()

    # Add binary truth column.
    joined_ok["y_true"] = (joined_ok["combined_label"] == "mound").astype(int)

    p = joined_ok["ds_posterior"].to_numpy()
    y = joined_ok["y_true"].to_numpy()
    unique_posts = sorted({round(float(v), 6) for v in p.tolist()})
    degenerate = len(unique_posts) == 1

    # ----- Reliability + ECE + Brier + AUC ------------------------------
    bins = reliability_bins(p, y)
    ece = expected_calibration_error(bins, total=len(p))
    brier = float(brier_score_loss(y, p))

    # AUC is undefined when there is no rank information; surface 0.5 with
    # a flag.
    if degenerate or len(set(y.tolist())) < 2:
        auc_val = 0.5
        auc_degenerate = True
    else:
        auc_val = float(roc_auc_score(y, p))
        auc_degenerate = False

    # ----- 2x2 crosstab at threshold 0.5 --------------------------------
    coarse_counts, coarse_metrics = coarse_crosstab(p, y, threshold=0.5)

    # ----- Ambiguity-band isolation -------------------------------------
    ambiguity = ambiguity_band_isolation(p, y)

    # ----- Buffer-band view ---------------------------------------------
    buffer_df = buffer_band_summary(joined_ok)

    # ----- Write CSV outputs --------------------------------------------
    # crosstab_coarse.csv
    pd.DataFrame(
        [
            {"cell": "D-S > 0.5 & human mound", "count": coarse_counts["tp"]},
            {"cell": "D-S > 0.5 & human not_mound", "count": coarse_counts["fp"]},
            {"cell": "D-S <= 0.5 & human mound", "count": coarse_counts["fn"]},
            {"cell": "D-S <= 0.5 & human not_mound", "count": coarse_counts["tn"]},
        ]
    ).to_csv(args.out / "crosstab_coarse.csv", index=False)

    # reliability.csv
    bins.to_csv(args.out / "reliability.csv", index=False)

    # buffer_band_vs_ds.csv
    buffer_df.to_csv(args.out / "buffer_band_vs_ds.csv", index=False)

    # ----- Plots --------------------------------------------------------
    plot_reliability(bins, args.out / "reliability_plot.png")
    plot_buffer_scatter(joined_ok, args.out / "buffer_scatter.png")

    # ----- summary.json and report.md -----------------------------------
    summary = {
        "inputs": {
            "ds_posteriors": str(args.ds_csv),
            "review_yesterday": str(args.review_yesterday),
            "review_today": str(args.review_today),
        },
        "n_combined": int(len(combined)),
        "n_joined": n_joined_rows,
        "n_unjoined": n_unjoined,
        "n_mound": int(y.sum()),
        "n_not_mound": int(len(y) - y.sum()),
        "prevalence": float(y.mean()) if len(y) else float("nan"),
        "n_today_uncertain_counted_as_not_mound": n_today_uncertain,
        "source_counts": {k: int(v) for k, v in source_counts.items()},
        "unique_ds_posteriors": unique_posts,
        "degenerate_posterior": bool(degenerate),
        "ece": ece,
        "brier": brier,
        "auc": auc_val,
        "auc_degenerate": auc_degenerate,
        "coarse_crosstab": coarse_counts,
        "coarse_metrics": coarse_metrics,
        "ambiguity_band_isolation": ambiguity,
        "verifier_reference_obs_269": {
            "ece": VERIFIER_ECE,
            "brier": VERIFIER_BRIER,
            "auc": VERIFIER_AUC,
            "source": (
                "results/55maps-image-generalisation/"
                "verifier-calibration-crosstab/calibration.md"
            ),
        },
    }
    with (args.out / "summary.json").open("w") as f:
        json.dump(summary, f, indent=2, default=float)
    with (args.out / "report.md").open("w") as f:
        f.write(
            render_report_md(
                summary=summary,
                bins=bins,
                coarse_counts=coarse_counts,
                coarse_metrics=coarse_metrics,
                buffer_df=buffer_df,
                ambiguity=ambiguity,
                degenerate=degenerate,
                unique_posterior_values=unique_posts,
            )
        )

    # ----- Console summary ---------------------------------------------
    print(f"n_combined = {len(combined)}")
    print(f"n_joined   = {n_joined_rows}  (unjoined = {n_unjoined})")
    print(f"prevalence (joined) = {y.mean():.4f}  "
          f"({int(y.sum())}/{len(y)})")
    print(f"unique D-S posteriors on joined set: {len(unique_posts)}")
    print(f"ECE   = {ece:.4f}")
    print(f"Brier = {brier:.4f}")
    print(f"AUC   = {auc_val:.4f}"
          + ("  (degenerate — all items share one posterior)"
             if auc_degenerate else ""))
    print(
        f"2x2 at 0.5: TP={coarse_counts['tp']} FP={coarse_counts['fp']} "
        f"FN={coarse_counts['fn']} TN={coarse_counts['tn']}  "
        f"P={coarse_metrics['precision']:.3f} "
        f"R={coarse_metrics['recall']:.3f} "
        f"F1={coarse_metrics['f1']:.3f}"
    )
    amb = ambiguity["ambiguous_band"]
    conf = ambiguity["confident_band"]
    print(
        f"Ambiguous band [{AMBIGUOUS_LO}, {AMBIGUOUS_HI}]: "
        f"n={amb['n']}, mound_rate={amb['human_mound_rate']:.3f}"
    )
    print(
        f"Confident band [<{CONFIDENT_LO}) U (>{CONFIDENT_HI}]: "
        f"n={conf['n']}, mound_rate={conf['human_mound_rate']:.3f}"
    )
    print(f"Outputs written to {args.out}")


if __name__ == "__main__":
    main()
