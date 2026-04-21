#!/usr/bin/env python3
# ---------------------------------------------------------------------------
# analyse_dawid_skene_v2.py
# ---------------------------------------------------------------------------
# Purpose
# -------
# Re-run the Dawid-Skene (D-S) latent-truth model on the 55-map image-
# generalisation run with a **data-driven** student false-negative (FN)
# prior, rather than the fixed 5 % prior used in the v1 analysis. Under a
# two-annotator D-S model, the posterior collapses to a single value per
# response pattern, so the student-FN prior is the only lever controlling
# the location of that single value — changing it is a pure calibration
# exercise at the cohort level.
#
# Motivation
# ----------
# The v1 D-S run (fixed 5 % prior) produced a catastrophically
# miscalibrated VLM-only posterior of 0.186, against an empirical
# human-confirmed mound rate of ~0.725 on the same slice. The prior was
# off by an order of magnitude. This script re-runs the model with the
# empirical rate plugged in as the student-FN prior and cross-tabs the new
# posteriors against the same human-review labels, to show what D-S is
# capable of when its scalar prior is not mis-specified.
#
# Circularity caveat
# ------------------
# The "data-driven" prior is derived from the same human-review labels
# used to evaluate the resulting posteriors. This is a **single-pass
# circular** estimate: calibration gains on this evaluation cannot be
# assumed to generalise to a held-out population. An 80 / 20 held-out
# sensitivity check is run as well (see ``run_holdout_check``).
#
# Inputs
# ------
# - Consensus GeoJSON + verifier probabilities JSON for the 55-map image
#   run (same defaults the v1 run used).
# - Combined human-review labels (yesterday + today multi-buffer), used
#   both to derive the prior and to evaluate calibration.
#
# Outputs (written to --output-dir)
# ---------------------------------
# - item-posteriors.csv        Per-item D-S posteriors (v2).
# - dawid-skene-results-v2.json
# - dawid-skene-results-v2.md
# - summary.json               Calibration + cross-tab vs human review.
# - reliability_v2.png         Reliability diagram.
# - comparison.md              v1 vs v2 side-by-side comparison.
# - report.md                  Narrative with circularity caveat.
# - holdout.json               80 / 20 held-out sensitivity check (optional).
#
# Usage
# -----
#   python3 scripts/analyse_dawid_skene_v2.py \
#       --student-fn-prior 0.7247 \
#       --consensus outputs/55maps-image-generalisation/consensus/consensus-3of5.geojson \
#       --probs outputs/55maps-image-generalisation/verified/probabilities.json \
#       --output-dir results/55maps-image-generalisation/dawid-skene-v2-data-driven-prior
#
# Language: UK/Australian English throughout.
# Compute: local workstation OK — EM converges in < 30 s on this dataset.
# ---------------------------------------------------------------------------

from __future__ import annotations

import argparse
import json
import logging
import math
import sys
from pathlib import Path

import geopandas as gpd
import matplotlib

matplotlib.use("Agg")  # headless backend
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.metrics import brier_score_loss, roc_auc_score

_SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(_SCRIPT_DIR))

# Re-use the v1 implementation (the EM routine and item-set builder).
from analyse_dawid_skene import (  # noqa: E402
    _BOUNDS_PATH,
    _STUDENT_GT_PATH,
    _TARGET_CRS,
    STUDENT_SPECIFICITY_DEFAULT,
    build_shared_item_set,
    compute_corrected_metrics,
    compute_simple_correction,
    dawid_skene_em,
    load_detections,
)

logger = logging.getLogger(__name__)

# Reliability diagram uses 10 equal-width bins (matches v1 cross-tab).
N_RELIABILITY_BINS: int = 10

# Observation 269 comparator numbers (verifier calibration on this set).
VERIFIER_ECE: float = 0.2689
VERIFIER_BRIER: float = 0.3226
VERIFIER_AUC: float = 0.6545

# v1 reference (from results/55maps-image-generalisation/ds-human-crosstab).
V1_POSTERIOR: float = 0.186207
V1_ECE: float = 0.5385006866301707
V1_BRIER: float = 0.4894892272943188
V1_AUC: float = 0.5


# ---------------------------------------------------------------------------
# Combined-review label assembly (mirrors analyse_ds_vs_human_review.py)
# ---------------------------------------------------------------------------


def build_combined_review(
    review_yesterday: pd.DataFrame,
    review_today: pd.DataFrame,
) -> pd.DataFrame:
    """Combine yesterday + today human-review CSVs into a single label set.

    Logic:
      - Yesterday mound (frozen 50 m TP)                      -> mound.
      - Yesterday not_mound, today mound (any buffer_band)    -> mound.
      - Yesterday not_mound, today not_mound / uncertain      -> not_mound.
      - Today-only (candidate not in yesterday)               -> today label.
    """
    y_idx = review_yesterday.set_index("candidate_id")
    t_idx = review_today.set_index("candidate_id")

    rows: list[dict] = []
    for cid, row in y_idx.iterrows():
        if row["human_label"] == "mound":
            rows.append(
                {
                    "candidate_id": cid,
                    "map_name": row["map_name"],
                    "x": row["x"],
                    "y": row["y"],
                    "combined_label": "mound",
                    "buffer_band": 50.0,
                    "source": "yesterday_mound",
                }
            )
            continue
        # Yesterday not_mound — look up today if present.
        if cid in t_idx.index:
            t_row = t_idx.loc[cid]
            if t_row["human_label"] == "mound":
                rows.append(
                    {
                        "candidate_id": cid,
                        "map_name": row["map_name"],
                        "x": row["x"],
                        "y": row["y"],
                        "combined_label": "mound",
                        "buffer_band": float(t_row["buffer_metres"]),
                        "source": "today_mound",
                    }
                )
            else:  # not_mound or uncertain
                rows.append(
                    {
                        "candidate_id": cid,
                        "map_name": row["map_name"],
                        "x": row["x"],
                        "y": row["y"],
                        "combined_label": "not_mound",
                        "buffer_band": float("nan"),
                        "source": (
                            "today_not_mound"
                            if t_row["human_label"] == "not_mound"
                            else "today_uncertain"
                        ),
                    }
                )
        else:
            rows.append(
                {
                    "candidate_id": cid,
                    "map_name": row["map_name"],
                    "x": row["x"],
                    "y": row["y"],
                    "combined_label": "not_mound",
                    "buffer_band": float("nan"),
                    "source": "yesterday_not_mound_only",
                }
            )

    # Pass 2: today-only candidates.
    today_only_ids = set(t_idx.index) - set(y_idx.index)
    for cid in sorted(today_only_ids):
        t_row = t_idx.loc[cid]
        label = (
            "mound" if t_row["human_label"] == "mound" else "not_mound"
        )
        rows.append(
            {
                "candidate_id": cid,
                "map_name": t_row["map_name"],
                "x": t_row["x"],
                "y": t_row["y"],
                "combined_label": label,
                "buffer_band": (
                    float(t_row["buffer_metres"])
                    if label == "mound" else float("nan")
                ),
                "source": "today_only",
            }
        )

    return pd.DataFrame(rows)


def join_posteriors_to_review(
    posteriors_df: pd.DataFrame,
    combined_review: pd.DataFrame,
) -> pd.DataFrame:
    """Inner-join D-S item-posteriors to combined review on (map, x, y)."""
    ds = posteriors_df.copy()
    ds["_x_round"] = ds["x"].round(3)
    ds["_y_round"] = ds["y"].round(3)

    rev = combined_review.copy()
    rev["_x_round"] = rev["x"].round(3)
    rev["_y_round"] = rev["y"].round(3)

    merged = rev.merge(
        ds[["map_name", "_x_round", "_y_round", "posterior_p_true",
            "item_id", "category"]],
        on=["map_name", "_x_round", "_y_round"],
        how="left",
    )
    merged = merged.drop(columns=["_x_round", "_y_round"])
    return merged


# ---------------------------------------------------------------------------
# Calibration primitives
# ---------------------------------------------------------------------------


def wilson_ci(k: int, n: int, z: float = 1.96) -> tuple[float, float]:
    """Wilson 95 % confidence interval for a binomial proportion."""
    if n == 0:
        return float("nan"), float("nan")
    p = k / n
    denom = 1 + (z**2) / n
    centre = p + (z**2) / (2 * n)
    halfwidth = z * math.sqrt((p * (1 - p) / n) + (z**2) / (4 * n**2))
    return (centre - halfwidth) / denom, (centre + halfwidth) / denom


def reliability_bins(
    p: np.ndarray, y: np.ndarray, n_bins: int = N_RELIABILITY_BINS,
) -> pd.DataFrame:
    """Per-bin reliability statistics on equal-width [0, 1] bins."""
    edges = np.linspace(0, 1, n_bins + 1)
    rows: list[dict] = []
    for i in range(n_bins):
        lo, hi = float(edges[i]), float(edges[i + 1])
        if i == n_bins - 1:
            mask = (p >= lo) & (p <= hi)
        else:
            mask = (p >= lo) & (p < hi)
        n = int(mask.sum())
        n_mound = int(y[mask].sum()) if n > 0 else 0
        mean_p = float(p[mask].mean()) if n > 0 else float("nan")
        emp = float(n_mound / n) if n > 0 else float("nan")
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
                "gap_pred_minus_emp": (
                    mean_p - emp if n > 0 else float("nan")
                ),
                "wilson_lo": w_lo,
                "wilson_hi": w_hi,
            }
        )
    return pd.DataFrame(rows)


def expected_calibration_error(bins: pd.DataFrame, total: int) -> float:
    """Sum over populated bins of (bin weight) * |empirical - predicted|."""
    ece = 0.0
    for _, r in bins.iterrows():
        if r["n"] == 0:
            continue
        ece += (r["n"] / total) * abs(r["empirical_p"] - r["mean_predicted"])
    return float(ece)


def coarse_crosstab(p: np.ndarray, y: np.ndarray, t: float = 0.5) -> dict:
    """2 x 2 cross-tab plus precision / recall / F1."""
    pred = p > t
    act = y == 1
    tp = int(np.sum(pred & act))
    fp = int(np.sum(pred & ~act))
    fn = int(np.sum(~pred & act))
    tn = int(np.sum(~pred & ~act))
    precision = tp / (tp + fp) if (tp + fp) > 0 else float("nan")
    recall = tp / (tp + fn) if (tp + fn) > 0 else float("nan")
    f1 = (
        2 * precision * recall / (precision + recall)
        if (not math.isnan(precision) and not math.isnan(recall)
            and (precision + recall) > 0)
        else float("nan")
    )
    return {
        "tp": tp, "fp": fp, "fn": fn, "tn": tn, "threshold": t,
        "precision": precision, "recall": recall, "f1": f1,
    }


def plot_reliability(
    bins: pd.DataFrame, out_path: Path, title_suffix: str = "",
) -> None:
    """Save the reliability diagram."""
    populated = bins[bins["n"] > 0].copy()
    if populated.empty:
        return
    xs = populated["mean_predicted"].to_numpy()
    ys = populated["empirical_p"].to_numpy()
    sizes = np.clip(populated["n"].to_numpy() / 2, 30, 600)

    fig, ax = plt.subplots(figsize=(7, 6))
    ax.plot([0, 1], [0, 1], linestyle="--", color="grey",
            label="perfect calibration (y = x)")
    ax.scatter(xs, ys, s=sizes, alpha=0.75, edgecolor="black", zorder=3,
               label="D-S posterior bins")
    lo = populated["wilson_lo"].to_numpy()
    hi = populated["wilson_hi"].to_numpy()
    ax.errorbar(xs, ys, yerr=[ys - lo, hi - ys], fmt="none",
                color="black", alpha=0.5, capsize=3, zorder=2)
    for _, r in populated.iterrows():
        ax.annotate(
            f"n = {int(r['n'])}",
            (r["mean_predicted"], r["empirical_p"]),
            textcoords="offset points", xytext=(8, -4), fontsize=8,
        )
    ax.set_xlabel("Mean predicted P(mound) within bin (D-S v2 posterior)")
    ax.set_ylabel("Empirical P(mound) within bin (human review)")
    ax.set_title(
        "Dawid-Skene v2 posterior reliability diagram\n"
        "(data-driven prior; degenerate — all items share one posterior)"
        + title_suffix
    )
    ax.set_xlim(-0.02, 1.02)
    ax.set_ylim(-0.02, 1.02)
    ax.grid(True, alpha=0.3)
    ax.legend(loc="lower right")
    fig.tight_layout()
    fig.savefig(out_path, dpi=150)
    plt.close(fig)


# ---------------------------------------------------------------------------
# Main pipeline
# ---------------------------------------------------------------------------


def run_ds_with_prior(
    item_set: pd.DataFrame,
    student_fn_prior: float,
    max_iter: int = 100,
    tol: float = 1e-6,
) -> dict:
    """Thin wrapper around ``dawid_skene_em`` with a specified FN prior.

    Keeps all EM hyperparameters identical to v1 apart from
    ``student_sens_init`` which becomes ``1 - student_fn_prior``.
    """
    student_sens = 1.0 - student_fn_prior
    return dawid_skene_em(
        item_set["student_label"].values,
        item_set["vlm_label"].values,
        student_sens_init=student_sens,
        student_spec_init=STUDENT_SPECIFICITY_DEFAULT,
        max_iter=max_iter,
        tol=tol,
    )


def derive_empirical_prior(
    combined_review: pd.DataFrame,
    item_set: pd.DataFrame,
) -> dict:
    """Derive the empirical student-FN prior from VLM-only human labels.

    The empirical mound rate among VLM-only candidates is used as the
    student-FN prior: if ~72 % of candidates the students missed but the
    VLM flagged are real mounds, then the student false-negative rate
    among real mounds flagged by the VLM alone is ~72 %.

    Returns a diagnostic dict.
    """
    # Isolate the VLM-only subset of the D-S item set.
    vlm_only = item_set[item_set["category"] == "vlm_only"].copy()
    vlm_only["_x_round"] = vlm_only["x"].round(3)
    vlm_only["_y_round"] = vlm_only["y"].round(3)

    rev = combined_review.copy()
    rev["_x_round"] = rev["x"].round(3)
    rev["_y_round"] = rev["y"].round(3)
    rev["_y_true"] = (rev["combined_label"] == "mound").astype(int)

    joined = vlm_only.merge(
        rev[["map_name", "_x_round", "_y_round", "_y_true"]],
        on=["map_name", "_x_round", "_y_round"], how="inner",
    )
    n = int(len(joined))
    n_mound = int(joined["_y_true"].sum())
    empirical_rate = float(n_mound / n) if n > 0 else float("nan")
    return {
        "vlm_only_joined": n,
        "vlm_only_human_mound": n_mound,
        "empirical_vlm_only_mound_rate": empirical_rate,
    }


def render_comparison_md(
    v1_posterior: float,
    v2_posterior: float,
    v1_metrics: dict,
    v2_metrics: dict,
    v1_crosstab: dict,
    v2_crosstab: dict,
    prior_info: dict,
    student_fn_prior: float,
    ds_result: dict,
    calibrated_prior: float,
    calibrated_metrics: dict,
    sweep_df: pd.DataFrame,
) -> str:
    """Side-by-side v1 (fixed 5 %) vs v2 (data-driven) comparison."""
    lines: list[str] = []
    lines.append("# Dawid-Skene v1 (fixed 5 % prior) vs v2 (data-driven prior)")
    lines.append("")
    lines.append("Side-by-side comparison of the two D-S runs on the 55-map")
    lines.append("image-generalisation VLM-only candidate slice. Everything")
    lines.append("other than the student false-negative prior is identical")
    lines.append("between the two runs.")
    lines.append("")
    lines.append("## Prior provenance")
    lines.append("")
    lines.append(
        "- **v1 student-FN prior**: 0.05 (fixed, Sobotkova et al. 2023)."
    )
    lines.append(
        f"- **v2 student-FN prior**: {student_fn_prior:.4f} "
        f"(= empirical mound rate on VLM-only slice: "
        f"{prior_info['vlm_only_human_mound']}/"
        f"{prior_info['vlm_only_joined']})."
    )
    lines.append("")
    lines.append("## Posterior comparison")
    lines.append("")
    lines.append("| Quantity | v1 (fixed 5 %) | v2 (data-driven) |")
    lines.append("|----------|---------------:|-----------------:|")
    lines.append(
        f"| VLM-only posterior P(true=1 \\| s=0, v=1) | "
        f"{v1_posterior:.4f} | {v2_posterior:.4f} |"
    )
    lines.append(
        f"| Estimated prevalence | 0.8557 | "
        f"{ds_result['prevalence']:.4f} |"
    )
    lines.append(
        f"| Estimated VLM sensitivity | 0.7716 | "
        f"{ds_result['vlm_sensitivity']:.4f} |"
    )
    lines.append(
        f"| Estimated VLM specificity | 0.0000 | "
        f"{ds_result['vlm_specificity']:.4f} |"
    )
    lines.append(
        f"| Iterations to convergence | 11 | "
        f"{ds_result['n_iterations']} |"
    )
    lines.append("")
    lines.append("## Calibration against human review (VLM-only slice only)")
    lines.append("")
    lines.append("| Metric | v1 | v2 | Change |")
    lines.append("|--------|---:|---:|-------:|")
    for key, name in [
        ("ece", "ECE (lower is better)"),
        ("brier", "Brier (lower is better)"),
        ("auc", "AUC (higher is better)"),
    ]:
        v1 = v1_metrics[key]
        v2 = v2_metrics[key]
        lines.append(f"| {name} | {v1:.4f} | {v2:.4f} | {v2 - v1:+.4f} |")
    lines.append("")
    lines.append("## 2 x 2 cross-tab at threshold 0.5")
    lines.append("")
    lines.append("### v1 (fixed 5 % prior)")
    lines.append("")
    lines.append("| | Human mound | Human not_mound |")
    lines.append("|---|---:|---:|")
    lines.append(
        f"| **D-S > 0.5** | {v1_crosstab['tp']} | {v1_crosstab['fp']} |"
    )
    lines.append(
        f"| **D-S ≤ 0.5** | {v1_crosstab['fn']} | {v1_crosstab['tn']} |"
    )
    lines.append("")
    lines.append("### v2 (data-driven prior)")
    lines.append("")
    lines.append("| | Human mound | Human not_mound |")
    lines.append("|---|---:|---:|")
    lines.append(
        f"| **D-S > 0.5** | {v2_crosstab['tp']} | {v2_crosstab['fp']} |"
    )
    lines.append(
        f"| **D-S ≤ 0.5** | {v2_crosstab['fn']} | {v2_crosstab['tn']} |"
    )
    lines.append("")
    for name, cs in [("v1", v1_crosstab), ("v2", v2_crosstab)]:
        lines.append(
            f"- **{name}**: precision = "
            f"{cs['precision'] if isinstance(cs['precision'], float) and not math.isnan(cs['precision']) else 'n/a'}"
            f", recall = {cs['recall']:.4f}, "
            f"F1 = "
            f"{cs['f1'] if isinstance(cs['f1'], float) and not math.isnan(cs['f1']) else 'n/a'}"
        )
    lines.append("")
    lines.append("## Best-calibrated-prior variant (grid search)")
    lines.append("")
    lines.append(
        "The D-S posterior is a non-linear function of the student-FN"
        " prior — feeding in the empirical rate (0.7247) does **not**"
        " produce a posterior equal to the empirical rate. A grid"
        " search across prior values identifies the prior at which"
        " the VLM-only posterior is closest to the empirical rate."
    )
    lines.append("")
    lines.append("| Quantity | v2 (empirical prior 0.725) | v2 (calibrated prior) |")
    lines.append("|----------|--------------------------:|----------------------:|")
    lines.append(
        f"| Student-FN prior | {student_fn_prior:.4f} | "
        f"{calibrated_prior:.4f} |"
    )
    lines.append(
        f"| VLM-only posterior | {v2_posterior:.4f} | "
        f"{calibrated_metrics['vlm_only_posterior']:.4f} |"
    )
    lines.append(
        f"| ECE | {v2_metrics['ece']:.4f} | "
        f"{calibrated_metrics['ece']:.4f} |"
    )
    lines.append(
        f"| Brier | {v2_metrics['brier']:.4f} | "
        f"{calibrated_metrics['brier']:.4f} |"
    )
    lines.append(
        f"| AUC | {v2_metrics['auc']:.4f} | "
        f"{calibrated_metrics['auc']:.4f} |"
    )
    cal_cross = calibrated_metrics["crosstab_at_0p5"]
    lines.append(
        f"| 2x2 @ 0.5 TP/FP/FN/TN | "
        f"{v2_crosstab['tp']}/{v2_crosstab['fp']}/"
        f"{v2_crosstab['fn']}/{v2_crosstab['tn']} | "
        f"{cal_cross['tp']}/{cal_cross['fp']}/"
        f"{cal_cross['fn']}/{cal_cross['tn']} |"
    )
    lines.append("")

    lines.append("## Prior sensitivity sweep")
    lines.append("")
    lines.append(
        "Selected rows from the full sweep "
        "(`prior_sensitivity_sweep.csv`):"
    )
    lines.append("")
    lines.append(
        "| Student-FN prior | pi (est.) | VLM sens | VLM spec | "
        "VLM-only posterior | |posterior − empirical| |"
    )
    lines.append(
        "|-----------------:|----------:|---------:|---------:|"
        "-------------------:|-----------------------:|"
    )
    for _, r in sweep_df.iterrows():
        lines.append(
            f"| {r['student_fn_prior']:.4f} | {r['prevalence']:.4f} | "
            f"{r['vlm_sensitivity']:.4f} | {r['vlm_specificity']:.4f} | "
            f"{r['vlm_only_posterior']:.4f} | "
            f"{r['abs_gap_vs_empirical']:.4f} |"
        )
    lines.append("")

    lines.append("## Interpretation")
    lines.append("")
    lines.append(
        "- **AUC is unchanged (0.5) because the D-S posterior remains "
        "degenerate under a 2-annotator design.** All 1,028 VLM-only "
        "items share the same posterior — so the posterior carries zero "
        "rank information about individual candidates regardless of"
        " the prior."
    )
    lines.append(
        "- **Calibration (ECE / Brier) is what the prior controls,"
        " but non-linearly.** Feeding in the empirical mound rate"
        " (0.725) does not produce a posterior equal to 0.725."
        " Above a student-FN prior of roughly 0.22 the EM snaps into"
        " a degenerate regime where the estimated prevalence pi"
        " collapses to 1 and every item posterior becomes 1.0."
    )
    lines.append(
        "- **The v2 (prior = 0.725) run is therefore pathological"
        " in the opposite direction to v1.** v1 under-predicted"
        " mounds; v2 over-predicts them. Neither is useful as a"
        " calibrated probability. The only genuine reduction in"
        " miscalibration comes from the grid-searched prior near"
        " 0.17, which produces a VLM-only posterior near 0.725 —"
        " numerically matching the empirical rate by construction."
    )
    lines.append(
        "- **The 2 x 2 cross-tab at 0.5 is not meaningful here.**"
        " Because the posterior is degenerate, the cell counts are"
        " deterministic given whether the single posterior is above"
        " or below 0.5. Precision and recall reflect prevalence,"
        " not model skill."
    )
    lines.append("")
    return "\n".join(lines)


def render_report_md(
    prior_info: dict,
    student_fn_prior: float,
    ds_result: dict,
    v2_metrics: dict,
    v2_crosstab: dict,
    holdout: dict | None,
    unique_v2_posts: list[float],
    calibrated_prior: float,
    calibrated_metrics: dict,
) -> str:
    """Narrative v2 report with circularity caveat prominent."""
    lines: list[str] = []
    lines.append(
        "# Dawid-Skene with data-driven student-FN prior (v2)"
    )
    lines.append("")
    lines.append(
        "This report documents the v2 Dawid-Skene run — identical to v1"
        " apart from the student false-negative prior, which is now"
        " derived from the combined human-review labels on the VLM-only"
        " candidate slice rather than the 5 % global estimate of"
        " Sobotkova et al. (2023)."
    )
    lines.append("")
    lines.append("## Circularity caveat — read first")
    lines.append("")
    lines.append(
        "The v2 prior is derived from the **same human-review labels"
        " used to evaluate the v2 posterior**. This is a deliberately"
        " circular set-up: it shows what D-S is capable of if its"
        " scalar prior matched reality, but the calibration metrics"
        " reported here cannot be taken as evidence that a similar"
        " calibration would hold on a held-out sample from the same"
        " population. The numbers illustrate the upper bound of D-S"
        " performance under a well-specified prior, not the expected"
        " performance of D-S in a prospective workflow."
    )
    lines.append("")
    lines.append(
        "An 80 / 20 held-out sensitivity check is included below to"
        " partially address this caveat."
    )
    lines.append("")

    lines.append("## Prior derivation")
    lines.append("")
    lines.append(
        f"- VLM-only candidates joined to human review: "
        f"**{prior_info['vlm_only_joined']}**"
    )
    lines.append(
        f"- Human-confirmed mounds among those: "
        f"**{prior_info['vlm_only_human_mound']}**"
    )
    lines.append(
        f"- Empirical mound rate on VLM-only slice: "
        f"**{prior_info['empirical_vlm_only_mound_rate']:.4f}**"
    )
    lines.append(
        f"- Student-FN prior used for v2 EM: "
        f"**{student_fn_prior:.4f}** "
        f"(student sensitivity = {1 - student_fn_prior:.4f})"
    )
    lines.append("")

    lines.append("## v2 D-S model outputs")
    lines.append("")
    lines.append(
        f"- Converged: {ds_result['converged']} "
        f"({ds_result['n_iterations']} iterations)"
    )
    lines.append(
        f"- Estimated prevalence: {ds_result['prevalence']:.4f}"
    )
    lines.append(
        f"- Estimated VLM sensitivity: "
        f"{ds_result['vlm_sensitivity']:.4f}"
    )
    lines.append(
        f"- Estimated VLM specificity: "
        f"{ds_result['vlm_specificity']:.4f}"
    )
    lines.append(
        f"- VLM-only posterior P(true=1): "
        f"**{unique_v2_posts[0]:.4f}**"
    )
    lines.append(
        f"- Unique posterior values on VLM-only slice: "
        f"{len(unique_v2_posts)}"
    )
    lines.append("")

    lines.append("## v2 calibration vs. human review")
    lines.append("")
    lines.append("| Metric | v1 (fixed 5 %) | v2 (data-driven) | Verifier |")
    lines.append("|--------|---------------:|-----------------:|---------:|")
    lines.append(
        f"| ECE | {V1_ECE:.4f} | {v2_metrics['ece']:.4f} | "
        f"{VERIFIER_ECE:.4f} |"
    )
    lines.append(
        f"| Brier | {V1_BRIER:.4f} | {v2_metrics['brier']:.4f} | "
        f"{VERIFIER_BRIER:.4f} |"
    )
    lines.append(
        f"| AUC | {V1_AUC:.4f} | {v2_metrics['auc']:.4f} | "
        f"{VERIFIER_AUC:.4f} |"
    )
    lines.append("")
    lines.append(
        "The AUC comparison is the key diagnostic: D-S remains rank-"
        "uninformative at the item level, whereas the verifier — albeit"
        " imperfectly calibrated — provides graded per-item scores."
    )
    lines.append("")

    lines.append("## 2 x 2 cross-tab at threshold 0.5 (v2)")
    lines.append("")
    lines.append("| | Human mound | Human not_mound |")
    lines.append("|---|---:|---:|")
    lines.append(
        f"| **D-S > 0.5** | {v2_crosstab['tp']} | {v2_crosstab['fp']} |"
    )
    lines.append(
        f"| **D-S ≤ 0.5** | {v2_crosstab['fn']} | {v2_crosstab['tn']} |"
    )
    lines.append("")

    if holdout is not None:
        lines.append("## Held-out sensitivity check (80 / 20, seed 42)")
        lines.append("")
        lines.append(
            f"- Train set size: {holdout['n_train']} VLM-only items"
        )
        lines.append(
            f"- Test set size: {holdout['n_test']} VLM-only items"
        )
        lines.append(
            f"- Train-derived prior (empirical rate on 80 %): "
            f"{holdout['train_prior']:.4f}"
        )
        lines.append(
            f"- Test-set empirical rate (20 %): "
            f"{holdout['test_empirical_rate']:.4f}"
        )
        lines.append(
            f"- D-S posterior fit with train prior: "
            f"{holdout['posterior_under_train_prior']:.4f}"
        )
        lines.append(
            f"- Absolute gap (posterior − test rate): "
            f"{holdout['gap_posterior_vs_test']:+.4f}"
        )
        lines.append(
            f"- Test-set ECE: {holdout['test_ece']:.4f} "
            f"(v1 was {V1_ECE:.4f})"
        )
        lines.append(
            f"- Test-set Brier: {holdout['test_brier']:.4f} "
            f"(v1 was {V1_BRIER:.4f})"
        )
        lines.append("")
        lines.append(
            "**Interpretation.** The gap between the train-derived"
            " prior and the test empirical rate is the genuine"
            " held-out calibration error. If it is small relative to"
            " v1's ECE (0.539), the v2 calibration gain is robust to"
            " the 80 / 20 split; if it is close to v1's ECE, the v2"
            " gain is mostly a circular artefact."
        )
        lines.append("")

    lines.append(
        "## Surprising finding — the empirical prior is pathological"
    )
    lines.append("")
    lines.append(
        "The brief asked to plug the empirical VLM-only mound rate"
        f" ({prior_info['empirical_vlm_only_mound_rate']:.4f}) in as"
        " the student-FN prior. The intuition was that a posterior"
        " close to that empirical rate would indicate D-S can recover"
        " the cohort rate when the prior matches reality. It does"
        " not: the two-annotator D-S posterior is a **non-linear"
        " function of the prior**, and above a student-FN prior of"
        " roughly 0.22 the estimated prevalence snaps to 1.0 and"
        " every item's posterior becomes 1.0. The v2 run with"
        f" prior = {student_fn_prior:.4f} falls into this collapsed"
        " regime (posterior = 1.0 for every item, including the"
        " VLM-only slice)."
    )
    lines.append("")
    lines.append(
        "A grid search across student-FN priors (see"
        " `prior_sensitivity_sweep.csv`) identifies the calibrated"
        " prior — the prior at which the VLM-only posterior most"
        " closely matches the empirical rate:"
    )
    lines.append("")
    lines.append(
        f"- **Calibrated prior**: {calibrated_prior:.4f}"
    )
    lines.append(
        f"- **VLM-only posterior at calibrated prior**: "
        f"{calibrated_metrics['vlm_only_posterior']:.4f}"
    )
    lines.append(
        f"- **ECE at calibrated prior**: "
        f"{calibrated_metrics['ece']:.4f}"
    )
    lines.append(
        f"- **Brier at calibrated prior**: "
        f"{calibrated_metrics['brier']:.4f}"
    )
    lines.append(
        f"- **AUC at calibrated prior**: "
        f"{calibrated_metrics['auc']:.4f} "
        f"({'degenerate' if calibrated_metrics['auc_degenerate'] else 'graded'})"
    )
    lines.append("")
    lines.append(
        "The calibrated prior is about half the empirical VLM-only"
        " mound rate — a reminder that the D-S student-FN prior is"
        " not a direct rate parameter, it is a likelihood term that"
        " interacts with pi, v_sens, and v_spec during EM."
    )
    lines.append("")

    lines.append("## Does D-S become useful with a better prior?")
    lines.append("")
    lines.append(
        "- **As an item-level discriminator, no.** Two-annotator D-S"
        " is mathematically degenerate — every VLM-only item receives"
        " the same posterior, so AUC stays at 0.5 regardless of prior."
        " The verifier probability (AUC 0.65 on this slice) remains"
        " the only graded item-level signal."
    )
    lines.append(
        "- **As a cohort-rate estimator, yes, but only when the prior"
        " is already close to the truth.** D-S with a data-driven"
        " prior returns a single probability close to the empirical"
        " rate — which is informative if that empirical rate is known"
        " from an external source (e.g. a pilot review). Without an"
        " external source, the prior must be pulled from the very"
        " labels we want to evaluate, which makes the exercise"
        " circular."
    )
    lines.append(
        "- **Practical implication for this project.** D-S with the"
        " fixed 5 % prior understated the VLM-only mound rate by"
        " roughly a factor of four. With a slice-specific human-"
        "review-derived prior it is roughly right, but it adds no"
        " value beyond reporting the empirical rate itself. The"
        " project should rely on the verifier + human review for"
        " item-level decisions and on the empirical review rate for"
        " cohort-level rate claims."
    )
    lines.append("")
    lines.append("## Files produced")
    lines.append("")
    lines.append("- `item-posteriors.csv` — v2 per-item posteriors.")
    lines.append(
        "- `dawid-skene-results-v2.json` / `.md` — raw model outputs."
    )
    lines.append(
        "- `summary.json` — calibration + cross-tab machine-readable."
    )
    lines.append(
        "- `reliability_v2.png` — reliability diagram (10 equal-width"
        " bins)."
    )
    lines.append(
        "- `comparison.md` — v1 vs v2 side-by-side comparison."
    )
    if holdout is not None:
        lines.append(
            "- `holdout.json` — 80 / 20 held-out sensitivity check."
        )
    lines.append("")
    return "\n".join(lines)


def run_holdout_check(
    item_set: pd.DataFrame,
    combined_review: pd.DataFrame,
    seed: int = 42,
    train_frac: float = 0.8,
) -> dict:
    """80 / 20 held-out sensitivity check for the data-driven prior.

    Splits the 1,028 VLM-only candidates into train / test, derives the
    prior from the train-fold empirical rate, re-runs the full D-S EM
    on all 5,798 items with that prior, then evaluates calibration on
    the 20 % test fold only.

    Parameters
    ----------
    item_set
        Full D-S item set (matched + student_only + vlm_only).
    combined_review
        Combined human-review labels (yesterday + today).
    seed
        Random seed for the shuffle.
    train_frac
        Train fraction (default 0.8).

    Returns
    -------
    dict
        Diagnostic metrics for the held-out check.
    """
    # Subset VLM-only items with human review labels.
    vlm_only = item_set[item_set["category"] == "vlm_only"].copy()
    vlm_only["_x_round"] = vlm_only["x"].round(3)
    vlm_only["_y_round"] = vlm_only["y"].round(3)

    rev = combined_review.copy()
    rev["_x_round"] = rev["x"].round(3)
    rev["_y_round"] = rev["y"].round(3)
    rev["_y_true"] = (rev["combined_label"] == "mound").astype(int)

    labelled = vlm_only.merge(
        rev[["map_name", "_x_round", "_y_round", "_y_true"]],
        on=["map_name", "_x_round", "_y_round"], how="inner",
    )
    labelled = labelled.reset_index(drop=True)
    n_total = len(labelled)

    rng = np.random.default_rng(seed)
    perm = rng.permutation(n_total)
    n_train = int(round(train_frac * n_total))
    train_idx = perm[:n_train]
    test_idx = perm[n_train:]

    train_rate = float(labelled.iloc[train_idx]["_y_true"].mean())
    test_rate = float(labelled.iloc[test_idx]["_y_true"].mean())

    # Re-run D-S using the train-derived prior.
    ds_holdout = run_ds_with_prior(item_set, student_fn_prior=train_rate)

    # Posterior on VLM-only items (same for every item by construction).
    vlm_only_posts = ds_holdout["posteriors"][
        (item_set["category"] == "vlm_only").values
    ]
    posterior_under_train_prior = float(np.unique(vlm_only_posts)[0])

    # Calibration on the test fold only.
    test_rows = labelled.iloc[test_idx].copy()
    p_test = np.full(len(test_rows), posterior_under_train_prior)
    y_test = test_rows["_y_true"].to_numpy()
    test_bins = reliability_bins(p_test, y_test)
    test_ece = expected_calibration_error(test_bins, total=len(p_test))
    test_brier = float(brier_score_loss(y_test, p_test))

    return {
        "seed": seed,
        "train_frac": train_frac,
        "n_train": int(n_train),
        "n_test": int(n_total - n_train),
        "train_prior": train_rate,
        "test_empirical_rate": test_rate,
        "posterior_under_train_prior": posterior_under_train_prior,
        "gap_posterior_vs_test": posterior_under_train_prior - test_rate,
        "test_ece": test_ece,
        "test_brier": test_brier,
    }


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--consensus", type=Path, required=True,
        help="Consensus GeoJSON for the detection run.",
    )
    parser.add_argument(
        "--probs", type=Path, required=True,
        help="Verifier probabilities JSON for the detection run.",
    )
    parser.add_argument(
        "--ground-truth", type=Path, default=_STUDENT_GT_PATH,
        help="Student ground-truth GeoJSON (default: 55-map student GT).",
    )
    parser.add_argument(
        "--bounds", type=Path, default=_BOUNDS_PATH,
        help="Evaluation bounds GeoJSON (default: 55-map bounds).",
    )
    parser.add_argument(
        "--threshold", type=float, default=0.15,
        help="Verifier probability threshold (default: %(default)s).",
    )
    parser.add_argument(
        "--buffer", type=int, default=50,
        help="Matching tolerance in metres (default: %(default)s).",
    )
    parser.add_argument(
        "--student-fn-prior", type=float, default=None,
        help=(
            "Student false-negative prior in [0, 1). If omitted, the "
            "empirical VLM-only mound rate is computed from the review "
            "CSVs and used."
        ),
    )
    parser.add_argument(
        "--review-yesterday", type=Path,
        default=Path(
            "results/55maps-image-generalisation/human-review.csv"
        ),
        help="Yesterday's human-review CSV.",
    )
    parser.add_argument(
        "--review-today", type=Path,
        default=Path(
            "results/55maps-image-generalisation/human-review-multi-buffer.csv"
        ),
        help="Today's multi-buffer human-review CSV.",
    )
    parser.add_argument(
        "--output-dir", type=Path, required=True,
        help="Directory to write v2 artefacts into.",
    )
    parser.add_argument(
        "--no-holdout", action="store_true",
        help="Skip the 80 / 20 held-out sensitivity check.",
    )
    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Debug logging.",
    )
    args = parser.parse_args(argv)

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )

    args.output_dir.mkdir(parents=True, exist_ok=True)

    # ----- Load detection data -----------------------------------------
    logger.info(
        "Loading detections: consensus=%s probs=%s",
        args.consensus, args.probs,
    )
    gdf_det = load_detections(args.consensus, args.probs, args.threshold)
    gdf_ref = gpd.read_file(args.ground_truth)
    if gdf_ref.crs != _TARGET_CRS:
        gdf_ref = gdf_ref.to_crs(_TARGET_CRS)
    gdf_bounds = gpd.read_file(args.bounds)
    if gdf_bounds.crs != _TARGET_CRS:
        gdf_bounds = gdf_bounds.to_crs(_TARGET_CRS)

    # ----- Build item set ----------------------------------------------
    logger.info("Building shared item set (buffer=%dm)", args.buffer)
    item_set = build_shared_item_set(
        gdf_det, gdf_ref, gdf_bounds, buffer_metres=args.buffer,
    )

    # ----- Load human-review CSVs and compile combined labels ----------
    logger.info(
        "Loading human-review CSVs: %s, %s",
        args.review_yesterday, args.review_today,
    )
    ry = pd.read_csv(args.review_yesterday)
    rt = pd.read_csv(args.review_today)
    combined_review = build_combined_review(ry, rt)

    # ----- Derive empirical prior (or use CLI override) ---------------
    prior_info = derive_empirical_prior(combined_review, item_set)
    empirical_rate = prior_info["empirical_vlm_only_mound_rate"]
    if args.student_fn_prior is not None:
        student_fn_prior = float(args.student_fn_prior)
        logger.info(
            "Using CLI-supplied student-FN prior: %.4f "
            "(empirical would be %.4f)", student_fn_prior, empirical_rate,
        )
    else:
        student_fn_prior = float(empirical_rate)
        logger.info(
            "Using empirical VLM-only mound rate as student-FN prior: "
            "%.4f", student_fn_prior,
        )

    # ----- Run D-S EM with data-driven prior ---------------------------
    logger.info("Running D-S EM with student-FN prior = %.4f",
                student_fn_prior)
    ds_result = run_ds_with_prior(item_set, student_fn_prior=student_fn_prior)
    posteriors = ds_result["posteriors"]

    # ----- Prior sensitivity sweep -------------------------------------
    # Because the 2-annotator D-S posterior is a non-linear function of
    # the prior, identifying the prior at which the posterior matches
    # the empirical rate is a useful diagnostic. This grid also reveals
    # a "collapse" regime above FN ~0.2 where pi snaps to 1 and every
    # item posterior becomes 1.
    logger.info("Running prior sensitivity sweep")
    sweep_rows: list[dict] = []
    sweep_priors = [
        0.05, 0.08, 0.10, 0.11, 0.12, 0.13, 0.14, 0.15, 0.16, 0.17,
        0.18, 0.19, 0.20, 0.22, 0.25, 0.30, 0.40, 0.50, 0.60,
        0.70, student_fn_prior, 0.80, 0.90, 0.95,
    ]
    sweep_priors = sorted(set(round(p, 4) for p in sweep_priors))
    vlm_only_mask_vec = (item_set["category"] == "vlm_only").values
    for fn_p in sweep_priors:
        r = run_ds_with_prior(item_set, student_fn_prior=fn_p)
        vlm_post = float(np.unique(r["posteriors"][vlm_only_mask_vec])[0])
        sweep_rows.append({
            "student_fn_prior": fn_p,
            "student_sensitivity": 1.0 - fn_p,
            "converged": bool(r["converged"]),
            "n_iter": int(r["n_iterations"]),
            "prevalence": float(r["prevalence"]),
            "vlm_sensitivity": float(r["vlm_sensitivity"]),
            "vlm_specificity": float(r["vlm_specificity"]),
            "vlm_only_posterior": vlm_post,
            # Calibration proxy: |posterior - empirical rate|.
            "abs_gap_vs_empirical": abs(vlm_post - empirical_rate),
        })
    sweep_df = pd.DataFrame(sweep_rows)
    sweep_df.to_csv(
        args.output_dir / "prior_sensitivity_sweep.csv", index=False,
    )
    # Identify the prior that minimises |posterior - empirical rate|.
    best_row = sweep_df.loc[sweep_df["abs_gap_vs_empirical"].idxmin()]
    calibrated_prior = float(best_row["student_fn_prior"])
    calibrated_posterior = float(best_row["vlm_only_posterior"])
    logger.info(
        "Best-calibrated prior from sweep: FN=%.4f -> posterior=%.4f "
        "(empirical=%.4f)",
        calibrated_prior, calibrated_posterior, empirical_rate,
    )

    # ----- Persist v2 item-posteriors & raw D-S outputs ----------------
    posteriors_df = item_set.copy()
    posteriors_df["posterior_p_true"] = posteriors
    posteriors_df["latent_truth"] = (posteriors >= 0.5).astype(int)
    posteriors_df.to_csv(
        args.output_dir / "item-posteriors.csv", index=False,
    )

    # Also persist the "best-calibrated" posteriors — the prior that
    # produces a VLM-only posterior closest to the empirical rate.
    ds_calibrated = run_ds_with_prior(
        item_set, student_fn_prior=calibrated_prior,
    )
    posteriors_calibrated = ds_calibrated["posteriors"]
    posteriors_calibrated_df = item_set.copy()
    posteriors_calibrated_df["posterior_p_true"] = posteriors_calibrated
    posteriors_calibrated_df["latent_truth"] = (
        posteriors_calibrated >= 0.5
    ).astype(int)
    posteriors_calibrated_df.to_csv(
        args.output_dir / "item-posteriors-calibrated.csv", index=False,
    )

    # ----- Corrected metrics (reused from v1 pipeline) -----------------
    ds_corrected = compute_corrected_metrics(item_set, posteriors)
    simple = compute_simple_correction(
        item_set, student_fn_rate=student_fn_prior,
    )

    raw_json = {
        "parameters": {
            "threshold": args.threshold,
            "buffer_metres": args.buffer,
            "student_fn_rate_prior": student_fn_prior,
            "prior_source": (
                "cli_override" if args.student_fn_prior is not None
                else "empirical_vlm_only_mound_rate"
            ),
            "consensus": str(args.consensus),
            "probabilities": str(args.probs),
        },
        "item_counts": {
            "matched": int((item_set["category"] == "matched").sum()),
            "student_only": int(
                (item_set["category"] == "student_only").sum()
            ),
            "vlm_only": int((item_set["category"] == "vlm_only").sum()),
            "total": int(len(item_set)),
        },
        "dawid_skene": {
            "corrected_metrics": ds_corrected,
            "simple_correction": simple,
            "model_estimates": {
                "prevalence": ds_result["prevalence"],
                "student_sensitivity": ds_result["student_sensitivity"],
                "student_specificity": ds_result["student_specificity"],
                "vlm_sensitivity": ds_result["vlm_sensitivity"],
                "vlm_specificity": ds_result["vlm_specificity"],
                "n_iterations": ds_result["n_iterations"],
                "converged": ds_result["converged"],
            },
        },
        "empirical_prior_derivation": prior_info,
    }
    (args.output_dir / "dawid-skene-results-v2.json").write_text(
        json.dumps(raw_json, indent=2) + "\n", encoding="utf-8",
    )

    # ----- Cross-tab v2 posteriors against human review ---------------
    joined = join_posteriors_to_review(posteriors_df, combined_review)
    joined_ok = joined[joined["posterior_p_true"].notna()].copy()
    joined_ok["y_true"] = (
        joined_ok["combined_label"] == "mound"
    ).astype(int)

    p = joined_ok["posterior_p_true"].to_numpy()
    y = joined_ok["y_true"].to_numpy()
    unique_v2_posts = sorted({round(float(v), 6) for v in p.tolist()})
    degenerate = len(unique_v2_posts) == 1

    bins = reliability_bins(p, y)
    ece = expected_calibration_error(bins, total=len(p))
    brier = float(brier_score_loss(y, p))
    if degenerate or len(set(y.tolist())) < 2:
        auc_val = 0.5
        auc_degenerate = True
    else:
        auc_val = float(roc_auc_score(y, p))
        auc_degenerate = False
    crosstab = coarse_crosstab(p, y, t=0.5)

    bins.to_csv(args.output_dir / "reliability.csv", index=False)
    plot_reliability(bins, args.output_dir / "reliability_v2.png")

    v2_metrics = {"ece": ece, "brier": brier, "auc": auc_val,
                  "auc_degenerate": auc_degenerate}

    # ----- Cross-tab the best-calibrated v2 posteriors -----------------
    joined_cal = join_posteriors_to_review(
        posteriors_calibrated_df, combined_review,
    )
    joined_cal_ok = joined_cal[joined_cal["posterior_p_true"].notna()].copy()
    joined_cal_ok["y_true"] = (
        joined_cal_ok["combined_label"] == "mound"
    ).astype(int)
    p_cal = joined_cal_ok["posterior_p_true"].to_numpy()
    y_cal = joined_cal_ok["y_true"].to_numpy()
    bins_cal = reliability_bins(p_cal, y_cal)
    ece_cal = expected_calibration_error(bins_cal, total=len(p_cal))
    brier_cal = float(brier_score_loss(y_cal, p_cal))
    unique_cal_posts = sorted(
        {round(float(v), 6) for v in p_cal.tolist()}
    )
    cal_degenerate = len(unique_cal_posts) == 1
    if cal_degenerate or len(set(y_cal.tolist())) < 2:
        auc_cal = 0.5
        auc_cal_deg = True
    else:
        auc_cal = float(roc_auc_score(y_cal, p_cal))
        auc_cal_deg = False
    crosstab_cal = coarse_crosstab(p_cal, y_cal, t=0.5)
    bins_cal.to_csv(
        args.output_dir / "reliability-calibrated.csv", index=False,
    )
    plot_reliability(
        bins_cal,
        args.output_dir / "reliability_v2_calibrated.png",
        title_suffix="\n(calibrated prior from grid search)",
    )
    v2_calibrated_metrics = {
        "ece": ece_cal, "brier": brier_cal, "auc": auc_cal,
        "auc_degenerate": auc_cal_deg,
        "vlm_only_posterior": (
            unique_cal_posts[0] if unique_cal_posts else float("nan")
        ),
        "crosstab_at_0p5": crosstab_cal,
    }

    # v1 reference cross-tab (from results/.../ds-human-crosstab/summary.json)
    v1_crosstab = {
        "tp": 0, "fp": 0, "fn": 745, "tn": 283, "threshold": 0.5,
        "precision": float("nan"), "recall": 0.0, "f1": float("nan"),
    }

    # ----- Held-out sensitivity check ----------------------------------
    holdout = None
    if not args.no_holdout:
        logger.info("Running 80 / 20 held-out sensitivity check "
                    "(seed=42)")
        holdout = run_holdout_check(item_set, combined_review)
        (args.output_dir / "holdout.json").write_text(
            json.dumps(holdout, indent=2, default=float) + "\n",
            encoding="utf-8",
        )

    # ----- Write summary.json, comparison.md, report.md ---------------
    summary = {
        "student_fn_prior_v2": student_fn_prior,
        "prior_source": raw_json["parameters"]["prior_source"],
        "empirical_prior_derivation": prior_info,
        "n_joined": int(len(joined_ok)),
        "n_unjoined": int(len(joined) - len(joined_ok)),
        "n_mound": int(y.sum()),
        "prevalence_joined": float(y.mean()) if len(y) else float("nan"),
        "unique_v2_posteriors": unique_v2_posts,
        "degenerate_v2_posterior": bool(degenerate),
        "v2_calibration": v2_metrics,
        "v2_coarse_crosstab": crosstab,
        "calibrated_prior_search": {
            "calibrated_student_fn_prior": calibrated_prior,
            "calibrated_vlm_only_posterior": calibrated_posterior,
            "empirical_rate": empirical_rate,
            "metrics": v2_calibrated_metrics,
        },
        "v1_reference": {
            "posterior": V1_POSTERIOR,
            "ece": V1_ECE,
            "brier": V1_BRIER,
            "auc": V1_AUC,
            "coarse_crosstab": v1_crosstab,
        },
        "verifier_reference_obs_269": {
            "ece": VERIFIER_ECE, "brier": VERIFIER_BRIER,
            "auc": VERIFIER_AUC,
        },
        "holdout": holdout,
    }
    (args.output_dir / "summary.json").write_text(
        json.dumps(summary, indent=2, default=float) + "\n",
        encoding="utf-8",
    )

    comparison_md = render_comparison_md(
        v1_posterior=V1_POSTERIOR,
        v2_posterior=unique_v2_posts[0],
        v1_metrics={"ece": V1_ECE, "brier": V1_BRIER, "auc": V1_AUC},
        v2_metrics=v2_metrics,
        v1_crosstab=v1_crosstab,
        v2_crosstab=crosstab,
        prior_info=prior_info,
        student_fn_prior=student_fn_prior,
        ds_result=ds_result,
        calibrated_prior=calibrated_prior,
        calibrated_metrics=v2_calibrated_metrics,
        sweep_df=sweep_df,
    )
    (args.output_dir / "comparison.md").write_text(
        comparison_md, encoding="utf-8",
    )

    report_md = render_report_md(
        prior_info=prior_info,
        student_fn_prior=student_fn_prior,
        ds_result=ds_result,
        v2_metrics=v2_metrics,
        v2_crosstab=crosstab,
        holdout=holdout,
        unique_v2_posts=unique_v2_posts,
        calibrated_prior=calibrated_prior,
        calibrated_metrics=v2_calibrated_metrics,
    )
    (args.output_dir / "report.md").write_text(
        report_md, encoding="utf-8",
    )

    # Also write a shortened v2 markdown alongside the raw JSON, to
    # mirror the v1 dawid-skene-results.md layout.
    v2_result_md_lines = [
        "# Dawid-Skene Latent Truth Model — v2 (data-driven prior)",
        "",
        "## Summary",
        "",
        (
            f"Identical to v1 except the student false-negative prior, "
            f"which is {student_fn_prior:.4f} (source: "
            f"{raw_json['parameters']['prior_source']})."
        ),
        "",
        "## Item counts",
        "",
        "| Category | Count |",
        "|----------|------:|",
        f"| Matched | {raw_json['item_counts']['matched']:,} |",
        f"| Student-only | {raw_json['item_counts']['student_only']:,} |",
        f"| VLM-only | {raw_json['item_counts']['vlm_only']:,} |",
        f"| **Total** | **{raw_json['item_counts']['total']:,}** |",
        "",
        "## D-S outputs",
        "",
        f"- Converged: {ds_result['converged']} "
        f"({ds_result['n_iterations']} iterations)",
        f"- Estimated prevalence: {ds_result['prevalence']:.4f}",
        f"- Student sensitivity (fixed): "
        f"{ds_result['student_sensitivity']:.4f}",
        f"- Student specificity (fixed): "
        f"{ds_result['student_specificity']:.4f}",
        f"- VLM sensitivity: {ds_result['vlm_sensitivity']:.4f}",
        f"- VLM specificity: {ds_result['vlm_specificity']:.4f}",
        f"- VLM-only posterior: {unique_v2_posts[0]:.4f}",
        "",
        "See `comparison.md` for v1 vs v2 side-by-side, and `report.md` "
        "for the narrative interpretation and circularity caveat.",
        "",
    ]
    (args.output_dir / "dawid-skene-results-v2.md").write_text(
        "\n".join(v2_result_md_lines), encoding="utf-8",
    )

    # ----- Console summary ---------------------------------------------
    print("=" * 60)
    print("Dawid-Skene v2 (data-driven prior) — Summary")
    print("=" * 60)
    print(f"Prior (student FN): {student_fn_prior:.4f}")
    print(f"VLM-only posterior: {unique_v2_posts[0]:.4f}")
    print(f"Joined rows: {len(joined_ok)}  "
          f"(prevalence = {float(y.mean()):.4f})")
    print(f"ECE   v1: {V1_ECE:.4f}  ->  v2: {ece:.4f}")
    print(f"Brier v1: {V1_BRIER:.4f}  ->  v2: {brier:.4f}")
    print(f"AUC   v1: {V1_AUC:.4f}  ->  v2: {auc_val:.4f}"
          + ("  (degenerate)" if auc_degenerate else ""))
    print(f"2x2 @ 0.5: TP={crosstab['tp']} FP={crosstab['fp']} "
          f"FN={crosstab['fn']} TN={crosstab['tn']}")
    if holdout is not None:
        print(
            f"Holdout (80/20, seed 42): train_prior="
            f"{holdout['train_prior']:.4f}  "
            f"test_empirical={holdout['test_empirical_rate']:.4f}  "
            f"posterior={holdout['posterior_under_train_prior']:.4f}  "
            f"test_ECE={holdout['test_ece']:.4f}"
        )
    print(f"Outputs: {args.output_dir}")


if __name__ == "__main__":
    main()
