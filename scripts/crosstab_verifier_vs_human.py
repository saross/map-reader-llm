#!/usr/bin/env python3
# ---------------------------------------------------------------------------
# crosstab_verifier_vs_human.py
# ---------------------------------------------------------------------------
# Purpose
# -------
# Evaluate how well the pipeline's Vision Language Model (VLM) verifier
# probability discriminates real burial mounds from false positives on the
# 55-map image-generalisation VLM-only candidate set. Ground-truth signal is
# the per-candidate human-review label produced during the review session
# completed on 2026-04-20.
#
# Inputs
# ------
# - results/55maps-image-generalisation/human-review.csv
#     Required columns: candidate_id, verifier_probability, human_label,
#     symbol_type, buffer_metres, map_name, source_tile.
#
# Outputs (written to results/55maps-image-generalisation/
#          verifier-calibration-crosstab/)
# ------------------------------------------------------------------------
# - calibration.json          Machine-readable numbers + bootstrap CIs
# - calibration_autogen.md    Auto-generated tables + interpretation
#                              (hand-authored `calibration.md` is the
#                              paper-citation source; do NOT overwrite —
#                              Session 75 guardrail 6)
# - reliability-diagram.png   Bin-mean predicted vs empirical P(mound)
# - roc-curve.png             Receiver Operating Characteristic curve
# - pr-curve.png              Precision-recall curve
#
# Methodology notes
# -----------------
# - Binary target is human_label == "mound" (positive class).
# - Probability bins: (0.15, 0.3], (0.3, 0.5], (0.5, 0.7], (0.7, 0.9],
#   (0.9, 0.95], (0.95, 0.99], (0.99, 1.0]. The first bin is left-open at
#   0.15 because that is the pipeline's current accept threshold (anything
#   <= 0.15 was not written to the review CSV).
# - Bootstrap confidence intervals use 10,000 resamples with seed=42.
# - Reliability is summarised via Expected Calibration Error (ECE), a
#   weighted average of |empirical - predicted| across bins.
# - Run on sapphire per project convention.
#
# Usage
# -----
#   python3 scripts/crosstab_verifier_vs_human.py \
#       --csv results/55maps-image-generalisation/human-review.csv \
#       --out results/55maps-image-generalisation/verifier-calibration-crosstab
#
# Language: UK/Australian English throughout.
# ---------------------------------------------------------------------------

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # headless backend for sapphire / CI
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.metrics import (
    auc,
    brier_score_loss,
    precision_recall_curve,
    roc_auc_score,
    roc_curve,
)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# Probability bin edges. Left-open at 0.15 because the pipeline's current
# accept threshold excludes anything at or below 0.15.
BIN_EDGES: list[tuple[float, float]] = [
    (0.15, 0.30),
    (0.30, 0.50),
    (0.50, 0.70),
    (0.70, 0.90),
    (0.90, 0.95),
    (0.95, 0.99),
    (0.99, 1.00),
]

# Threshold sweep values for the precision-recall trade-off table.
SWEEP_THRESHOLDS: list[float] = [0.15, 0.20, 0.30, 0.50, 0.70, 0.90, 0.95]

# Bootstrap parameters.
N_BOOTSTRAP: int = 10_000
BOOTSTRAP_SEED: int = 42


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def load_data(csv_path: Path) -> pd.DataFrame:
    """Load human-review CSV and derive a binary mound label.

    Args:
        csv_path: Path to human-review.csv.

    Returns:
        DataFrame with an added ``y_true`` column (1 == mound, 0 == not mound).
    """
    df = pd.read_csv(csv_path)
    df["y_true"] = (df["human_label"] == "mound").astype(int)
    df["p"] = df["verifier_probability"].astype(float)
    return df


def bin_assignment(p: np.ndarray, edges: list[tuple[float, float]]) -> np.ndarray:
    """Assign each probability to a bin index (-1 if below the lowest edge).

    Bins are left-open, right-closed: (lo, hi]. The first bin starts at
    ``edges[0][0]`` inclusive so that the current accept threshold (0.15)
    sits at the left edge.
    """
    idx = np.full(p.shape, -1, dtype=int)
    for i, (lo, hi) in enumerate(edges):
        if i == 0:
            mask = (p >= lo) & (p <= hi)
        else:
            mask = (p > lo) & (p <= hi)
        idx[mask] = i
    return idx


def calibration_table(df: pd.DataFrame) -> list[dict]:
    """Compute per-bin calibration statistics.

    Returns a list of dicts, one per bin, with count, n_mound, n_not_mound,
    mean predicted probability, empirical P(mound), and the bin range.
    """
    p = df["p"].to_numpy()
    y = df["y_true"].to_numpy()
    idx = bin_assignment(p, BIN_EDGES)
    rows: list[dict] = []
    for i, (lo, hi) in enumerate(BIN_EDGES):
        mask = idx == i
        count = int(mask.sum())
        n_mound = int(y[mask].sum()) if count > 0 else 0
        n_not_mound = count - n_mound
        mean_p = float(p[mask].mean()) if count > 0 else float("nan")
        emp = float(n_mound / count) if count > 0 else float("nan")
        rows.append(
            {
                "bin": f"({lo:.2f}, {hi:.2f}]" if i > 0 else f"[{lo:.2f}, {hi:.2f}]",
                "lo": lo,
                "hi": hi,
                "count": count,
                "n_mound": n_mound,
                "n_not_mound": n_not_mound,
                "mean_predicted": mean_p,
                "empirical_p_mound": emp,
            }
        )
    return rows


def expected_calibration_error(rows: list[dict], total: int) -> float:
    """Weighted average of |empirical - predicted| across populated bins."""
    ece = 0.0
    for r in rows:
        if r["count"] == 0:
            continue
        gap = abs(r["empirical_p_mound"] - r["mean_predicted"])
        ece += (r["count"] / total) * gap
    return float(ece)


def threshold_sweep(df: pd.DataFrame) -> list[dict]:
    """Precision-focused threshold sweep on the VLM-only set.

    For each threshold t, count accepted candidates (p >= t), true positives
    (accepted AND human_label == mound), and false positives (accepted AND
    human_label == not_mound). Since this is the VLM-only set (no full corpus
    denominator), report precision but not recall/F1 directly — instead
    report the "corrected-precision delta" relative to the current 0.15
    threshold so that the trade-off is visible.
    """
    y = df["y_true"].to_numpy()
    p = df["p"].to_numpy()
    # Baseline at t = 0.15.
    baseline_mask = p >= 0.15
    baseline_tp = int(y[baseline_mask].sum())
    baseline_n = int(baseline_mask.sum())
    baseline_prec = baseline_tp / baseline_n if baseline_n else float("nan")

    rows: list[dict] = []
    for t in SWEEP_THRESHOLDS:
        mask = p >= t
        n_accepted = int(mask.sum())
        tp = int(y[mask].sum())
        fp = n_accepted - tp
        precision = tp / n_accepted if n_accepted else float("nan")
        # Recall is computed against mounds present in the VLM-only set (not
        # the full ground-truth corpus). This is an upper bound on recall
        # achievable without retrieving additional candidates.
        total_mounds_in_set = int(y.sum())
        recall_within_set = tp / total_mounds_in_set if total_mounds_in_set else float("nan")
        # Corrected-F1 on the VLM-only set (precision and recall both measured
        # within this slice). Useful for relative comparison across thresholds
        # only; not comparable to full-corpus F1.
        if precision + recall_within_set > 0:
            f1_within_set = 2 * precision * recall_within_set / (precision + recall_within_set)
        else:
            f1_within_set = float("nan")
        rows.append(
            {
                "threshold": t,
                "n_accepted": n_accepted,
                "tp_mound": tp,
                "fp_not_mound": fp,
                "precision": precision,
                "precision_delta_vs_0_15": precision - baseline_prec,
                "recall_within_set": recall_within_set,
                "f1_within_set": f1_within_set,
            }
        )
    return rows


def bootstrap_ci(
    stat_fn,
    n: int,
    n_boot: int = N_BOOTSTRAP,
    seed: int = BOOTSTRAP_SEED,
) -> tuple[float, float, float]:
    """Percentile bootstrap 95% CI for a scalar statistic.

    Args:
        stat_fn: callable taking a numpy index array of resampled row indices
            and returning a scalar.
        n: sample size (rows in the dataframe).
        n_boot: number of bootstrap resamples.
        seed: RNG seed for reproducibility.

    Returns:
        (point, lo, hi) — point estimate on the full sample, 2.5% and 97.5%
        percentiles of the bootstrap distribution.
    """
    rng = np.random.default_rng(seed)
    point = stat_fn(np.arange(n))
    samples = np.empty(n_boot, dtype=float)
    for b in range(n_boot):
        idx = rng.integers(0, n, size=n)
        samples[b] = stat_fn(idx)
    lo, hi = np.nanpercentile(samples, [2.5, 97.5])
    return float(point), float(lo), float(hi)


def low_p_deep_dive(df: pd.DataFrame, cutoff: float = 0.25) -> dict:
    """Analyse the p <= cutoff tail for the under-confidence hypothesis.

    Returns counts, P(mound | p <= cutoff), symbol-type breakdown of mounds
    within the tail, and the five maps with most mounds in the tail.
    """
    tail = df[df["p"] <= cutoff]
    n = int(len(tail))
    n_mound = int(tail["y_true"].sum())
    p_mound = n_mound / n if n else float("nan")
    mound_tail = tail[tail["y_true"] == 1]
    symbol_breakdown = Counter(mound_tail["symbol_type"].tolist())
    map_breakdown = Counter(mound_tail["map_name"].tolist())
    return {
        "cutoff": cutoff,
        "n_total_in_tail": n,
        "n_mound_in_tail": n_mound,
        "p_mound_in_tail": p_mound,
        "symbol_type_of_mounds_in_tail": dict(symbol_breakdown),
        "top_maps_with_mounds_in_tail": dict(map_breakdown.most_common(5)),
    }


def per_class_brier(df: pd.DataFrame) -> dict:
    """Brier score computed separately for each symbol_type group.

    For the not_mound symbol_type, all y_true are 0 (these are the false
    positives from detection). Reporting per-class Brier helps surface
    whether any mound subclass is systematically mis-scored.
    """
    result: dict[str, dict] = {}
    for stype, sub in df.groupby("symbol_type"):
        if len(sub) == 0:
            continue
        brier = float(brier_score_loss(sub["y_true"].to_numpy(), sub["p"].to_numpy()))
        result[stype] = {
            "n": int(len(sub)),
            "n_mound": int(sub["y_true"].sum()),
            "mean_predicted": float(sub["p"].mean()),
            "empirical_p_mound": float(sub["y_true"].mean()),
            "brier": brier,
        }
    return result


# ---------------------------------------------------------------------------
# Plotting
# ---------------------------------------------------------------------------


def plot_reliability(rows: list[dict], out_path: Path) -> None:
    """Scatter bin-mean predicted vs empirical P(mound) with y=x reference."""
    xs = [r["mean_predicted"] for r in rows if r["count"] > 0]
    ys = [r["empirical_p_mound"] for r in rows if r["count"] > 0]
    sizes = [max(20, r["count"]) for r in rows if r["count"] > 0]
    labels = [r["bin"] for r in rows if r["count"] > 0]

    fig, ax = plt.subplots(figsize=(7, 6))
    ax.plot([0, 1], [0, 1], linestyle="--", color="grey", label="perfect calibration (y=x)")
    sc = ax.scatter(xs, ys, s=sizes, alpha=0.7, edgecolor="black", zorder=3)
    for x, y, lab in zip(xs, ys, labels, strict=False):
        ax.annotate(lab, (x, y), textcoords="offset points", xytext=(6, -4), fontsize=8)
    ax.set_xlabel("Mean predicted P(mound) within bin")
    ax.set_ylabel("Empirical P(mound) within bin")
    ax.set_title(
        "Verifier reliability diagram\n"
        "(point size proportional to bin count; points above y=x == under-confident)"
    )
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.grid(True, alpha=0.3)
    ax.legend(loc="lower right")
    fig.tight_layout()
    fig.savefig(out_path, dpi=150)
    plt.close(fig)
    del sc


def plot_roc(y: np.ndarray, p: np.ndarray, auc_val: float, out_path: Path) -> None:
    """Plot the receiver operating characteristic curve."""
    fpr, tpr, _ = roc_curve(y, p)
    fig, ax = plt.subplots(figsize=(6, 6))
    ax.plot(fpr, tpr, label=f"ROC (AUC = {auc_val:.3f})", linewidth=2)
    ax.plot([0, 1], [0, 1], linestyle="--", color="grey", label="chance")
    ax.set_xlabel("False positive rate")
    ax.set_ylabel("True positive rate")
    ax.set_title("Verifier ROC curve (VLM-only candidates, 55-map set)")
    ax.grid(True, alpha=0.3)
    ax.legend(loc="lower right")
    fig.tight_layout()
    fig.savefig(out_path, dpi=150)
    plt.close(fig)


def plot_pr(y: np.ndarray, p: np.ndarray, out_path: Path) -> None:
    """Plot the precision-recall curve (recall measured within the VLM-only set)."""
    precision, recall, _ = precision_recall_curve(y, p)
    pr_auc = auc(recall, precision)
    fig, ax = plt.subplots(figsize=(6, 6))
    ax.plot(recall, precision, linewidth=2, label=f"PR (AUC = {pr_auc:.3f})")
    # Baseline precision = prevalence.
    prev = float(y.mean())
    ax.axhline(prev, linestyle="--", color="grey", label=f"prevalence = {prev:.3f}")
    ax.set_xlabel("Recall (within VLM-only set)")
    ax.set_ylabel("Precision")
    ax.set_title("Verifier precision-recall curve (VLM-only candidates)")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.grid(True, alpha=0.3)
    ax.legend(loc="lower left")
    fig.tight_layout()
    fig.savefig(out_path, dpi=150)
    plt.close(fig)


# ---------------------------------------------------------------------------
# Markdown rendering
# ---------------------------------------------------------------------------


def render_markdown(report: dict) -> str:
    """Produce the calibration_autogen.md human-readable report."""
    lines: list[str] = []
    lines.append("# Verifier calibration crosstab (55-map image generalisation)")
    lines.append("")
    lines.append(
        "Evaluation of the Vision Language Model (VLM) verifier's probability output "
        "against per-candidate human-review labels on the 55-map image-generalisation "
        "VLM-only candidate set."
    )
    lines.append("")
    lines.append(f"- Total candidates reviewed: **{report['n_total']}**")
    lines.append(f"- Mounds (human-confirmed): **{report['n_mound']}**")
    lines.append(f"- Non-mounds: **{report['n_not_mound']}**")
    lines.append(f"- Mound prevalence in VLM-only set: **{report['prevalence']:.3f}**")
    lines.append("- All candidates: buffer_metres = 50")
    lines.append("")

    lines.append("## 1. Probability-binned calibration table")
    lines.append("")
    lines.append(
        "| Bin | Count | n_mound | n_not_mound | Mean predicted P | Empirical P(mound) | Gap |"
    )
    lines.append("|-----|-------|---------|-------------|------------------|--------------------|-----|")
    for r in report["calibration_bins"]:
        if r["count"] == 0:
            continue
        gap = r["empirical_p_mound"] - r["mean_predicted"]
        lines.append(
            f"| {r['bin']} | {r['count']} | {r['n_mound']} | {r['n_not_mound']} | "
            f"{r['mean_predicted']:.3f} | {r['empirical_p_mound']:.3f} | {gap:+.3f} |"
        )
    lines.append("")
    lines.append(f"**Expected Calibration Error (ECE):** {report['ece']:.4f}")
    lines.append("")
    lines.append(
        "Positive gap (empirical > predicted) indicates the verifier is "
        "**under-confident** in that bin; negative gap indicates over-confidence."
    )
    lines.append("")

    lines.append("## 2. Reliability diagram")
    lines.append("")
    lines.append("See `reliability-diagram.png`. Points above the y=x line are under-confident bins.")
    lines.append("")

    lines.append("## 3. ROC curve and AUC")
    lines.append("")
    auc_ci = report["auc"]
    lines.append(
        f"- **AUC:** {auc_ci['point']:.4f} "
        f"(95% bootstrap CI: {auc_ci['lo']:.4f}, {auc_ci['hi']:.4f})"
    )
    lines.append("See `roc-curve.png`.")
    lines.append("")

    lines.append("## 4. Precision-Recall curve")
    lines.append("")
    lines.append("See `pr-curve.png`.")
    lines.append("")

    lines.append("## 5. Threshold-sweep table (VLM-only set)")
    lines.append("")
    lines.append(
        "Precision and recall are measured within this slice only; they are not "
        "comparable to full-corpus F1. `precision_delta_vs_0_15` shows the absolute "
        "change from the current 0.15 threshold."
    )
    lines.append("")
    lines.append(
        "| Threshold | n_accepted | TP (mound) | FP (not_mound) | Precision | "
        "Precision delta vs 0.15 | Recall (within set) | F1 (within set) |"
    )
    lines.append(
        "|-----------|------------|------------|----------------|-----------|"
        "-------------------------|---------------------|-----------------|"
    )
    for r in report["threshold_sweep"]:
        lines.append(
            f"| {r['threshold']:.2f} | {r['n_accepted']} | {r['tp_mound']} | "
            f"{r['fp_not_mound']} | {r['precision']:.3f} | "
            f"{r['precision_delta_vs_0_15']:+.3f} | "
            f"{r['recall_within_set']:.3f} | {r['f1_within_set']:.3f} |"
        )
    lines.append("")

    lines.append("## 6. Brier score")
    lines.append("")
    br = report["brier"]
    lines.append(
        f"- **Overall Brier score:** {br['point']:.4f} "
        f"(95% bootstrap CI: {br['lo']:.4f}, {br['hi']:.4f})"
    )
    lines.append("")
    lines.append("### Per-symbol-type Brier score")
    lines.append("")
    lines.append("| Symbol type | n | n_mound | Mean predicted P | Empirical P(mound) | Brier |")
    lines.append("|-------------|---|---------|------------------|--------------------|-------|")
    for stype, vals in report["per_symbol_brier"].items():
        lines.append(
            f"| {stype} | {vals['n']} | {vals['n_mound']} | "
            f"{vals['mean_predicted']:.3f} | {vals['empirical_p_mound']:.3f} | "
            f"{vals['brier']:.4f} |"
        )
    lines.append("")

    lines.append("## 7. Bootstrap confidence intervals (10,000 resamples, seed 42)")
    lines.append("")
    lines.append("| Statistic | Point | 95% CI lo | 95% CI hi |")
    lines.append("|-----------|-------|-----------|-----------|")
    lines.append(
        f"| AUC | {auc_ci['point']:.4f} | {auc_ci['lo']:.4f} | {auc_ci['hi']:.4f} |"
    )
    lines.append(f"| Brier | {br['point']:.4f} | {br['lo']:.4f} | {br['hi']:.4f} |")
    p_low = report["p_mound_low_tail"]
    lines.append(
        f"| P(mound \\| p ≤ 0.25) | {p_low['point']:.4f} | "
        f"{p_low['lo']:.4f} | {p_low['hi']:.4f} |"
    )
    lines.append("")

    lines.append("## 8. Low-p deep dive (p ≤ 0.25)")
    lines.append("")
    dd = report["low_p_deep_dive"]
    lines.append(f"- Candidates in tail: **{dd['n_total_in_tail']}**")
    lines.append(f"- Mounds in tail: **{dd['n_mound_in_tail']}**")
    lines.append(
        f"- P(mound | p ≤ 0.25) = **{dd['p_mound_in_tail']:.4f}** "
        f"(bootstrap 95% CI: {p_low['lo']:.4f}, {p_low['hi']:.4f})"
    )
    lines.append("")
    lines.append("### Symbol-type breakdown of mounds in the tail")
    lines.append("")
    lines.append("| Symbol type | Count |")
    lines.append("|-------------|-------|")
    for stype, c in sorted(
        dd["symbol_type_of_mounds_in_tail"].items(), key=lambda x: -x[1]
    ):
        lines.append(f"| {stype} | {c} |")
    lines.append("")
    lines.append("### Top 5 maps by mound count in the tail")
    lines.append("")
    lines.append("| Map | Mounds in tail |")
    lines.append("|-----|----------------|")
    for m, c in dd["top_maps_with_mounds_in_tail"].items():
        lines.append(f"| {m} | {c} |")
    lines.append("")

    lines.append("## Interpretation guide")
    lines.append("")
    lines.append(
        "- **Under-confidence hypothesis**: the spot-check of 4/4 low-p mounds "
        "suggested the verifier systematically underweights faint/low-contrast "
        "real mounds. See the deep-dive P(mound | p ≤ 0.25) and its CI."
    )
    lines.append(
        "- **Threshold choice**: precision rises monotonically with threshold; "
        "recall (within-set) falls. The choice depends on downstream use — "
        "archaeology prioritises recall at the cost of manual review, so the "
        "0.15 accept threshold may still be preferred even if precision is low."
    )
    lines.append(
        "- **Per-class Brier**: large per-symbol Brier scores flag a subclass "
        "the verifier handles poorly (e.g. settlement_mound with n=13 may be "
        "noisy; burial_mound is the dominant positive class)."
    )
    lines.append("")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--csv",
        type=Path,
        default=Path(
            "results/55maps-image-generalisation/human-review.csv"
        ),
        help="Path to human-review CSV.",
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=Path(
            "results/55maps-image-generalisation/verifier-calibration-crosstab"
        ),
        help="Output directory (created if missing).",
    )
    parser.add_argument(
        "--n-boot",
        type=int,
        default=N_BOOTSTRAP,
        help="Number of bootstrap resamples.",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=BOOTSTRAP_SEED,
        help="RNG seed for bootstrap reproducibility.",
    )
    args = parser.parse_args()

    args.out.mkdir(parents=True, exist_ok=True)

    df = load_data(args.csv)
    n = len(df)
    y = df["y_true"].to_numpy()
    p = df["p"].to_numpy()

    # Calibration table + ECE.
    cal_rows = calibration_table(df)
    ece = expected_calibration_error(cal_rows, total=n)

    # Threshold sweep.
    sweep = threshold_sweep(df)

    # Per-symbol Brier.
    per_symbol = per_class_brier(df)

    # Low-p deep dive.
    dd = low_p_deep_dive(df, cutoff=0.25)

    # Bootstrap CIs for AUC, Brier, P(mound | p <= 0.25).
    def _auc(idx: np.ndarray) -> float:
        y_b = y[idx]
        p_b = p[idx]
        # AUC is undefined if only one class present in the resample.
        if len(set(y_b.tolist())) < 2:
            return float("nan")
        return float(roc_auc_score(y_b, p_b))

    def _brier(idx: np.ndarray) -> float:
        return float(brier_score_loss(y[idx], p[idx]))

    def _p_low(idx: np.ndarray) -> float:
        p_b = p[idx]
        y_b = y[idx]
        mask = p_b <= 0.25
        if mask.sum() == 0:
            return float("nan")
        return float(y_b[mask].mean())

    auc_point, auc_lo, auc_hi = bootstrap_ci(_auc, n, n_boot=args.n_boot, seed=args.seed)
    brier_point, brier_lo, brier_hi = bootstrap_ci(
        _brier, n, n_boot=args.n_boot, seed=args.seed
    )
    p_low_point, p_low_lo, p_low_hi = bootstrap_ci(
        _p_low, n, n_boot=args.n_boot, seed=args.seed
    )

    # Plots.
    plot_reliability(cal_rows, args.out / "reliability-diagram.png")
    plot_roc(y, p, auc_point, args.out / "roc-curve.png")
    plot_pr(y, p, args.out / "pr-curve.png")

    report = {
        "n_total": int(n),
        "n_mound": int(y.sum()),
        "n_not_mound": int(n - y.sum()),
        "prevalence": float(y.mean()),
        "calibration_bins": cal_rows,
        "ece": ece,
        "threshold_sweep": sweep,
        "brier": {
            "point": brier_point,
            "lo": brier_lo,
            "hi": brier_hi,
        },
        "auc": {
            "point": auc_point,
            "lo": auc_lo,
            "hi": auc_hi,
        },
        "p_mound_low_tail": {
            "point": p_low_point,
            "lo": p_low_lo,
            "hi": p_low_hi,
        },
        "per_symbol_brier": per_symbol,
        "low_p_deep_dive": dd,
        "config": {
            "n_bootstrap": args.n_boot,
            "seed": args.seed,
            "bin_edges": BIN_EDGES,
            "sweep_thresholds": SWEEP_THRESHOLDS,
        },
    }

    # Write outputs.
    with (args.out / "calibration.json").open("w") as f:
        json.dump(report, f, indent=2, default=float)
    with (args.out / "calibration_autogen.md").open("w") as f:
        f.write(render_markdown(report))

    # Console summary.
    print(f"n={n}, mounds={int(y.sum())}, prevalence={y.mean():.3f}")
    print(f"AUC = {auc_point:.4f} (95% CI {auc_lo:.4f}-{auc_hi:.4f})")
    print(f"Brier = {brier_point:.4f} (95% CI {brier_lo:.4f}-{brier_hi:.4f})")
    print(
        f"P(mound | p<=0.25) = {p_low_point:.4f} "
        f"(95% CI {p_low_lo:.4f}-{p_low_hi:.4f})"
    )
    print(f"ECE = {ece:.4f}")
    print(f"Outputs written to: {args.out}")


if __name__ == "__main__":
    main()
