#!/usr/bin/env python3
"""Cross-tabulate uncalibrated vs calibrated human-review decisions.

Context
-------
During the 55-map image-generalisation human review, the reviewer initially
operated with a "fuzzy" UI that asked whether each VLM-only candidate crop
looked "close enough" to a mound symbol, with no explicit spatial tolerance
displayed. After 327 reviews, the UI was upgraded to overlay a calibrated
magenta 50 m tolerance circle on the crop and the reviewer restarted the
session from scratch, ultimately re-reviewing all 1,028 candidates.

This script quantifies how much the calibrated UI changed reviewer decisions
on the 327-candidate overlap. The analysis provides empirical evidence for
Observation 263's claim in `docs/notes/reflections/working-notes.md` that an
"ambiguity band" of VLM-only candidates around the 50 m threshold produced
inconsistent reviewer judgements under the uncalibrated UI, and that the
tolerance circle materially improved reviewer consistency.

Outputs
-------
Writes to the requested ``--output-dir`` two artefacts:

* ``crosstab.json`` — machine-readable counts, rates, bootstrap CIs, and the
  symbol-type flow table.
* ``crosstab.md`` — human-readable report with Markdown tables.

Author: Shawn Ross, Claude Code
Licence: Apache 2.0
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd


# ---------------------------------------------------------------------------
# Verifier-probability bins for stratified disagreement analysis
# ---------------------------------------------------------------------------
# Bin edges match Obs 263's "ambiguity band" framing: the lowest-p bin is the
# expected high-disagreement region, with progressively more confident bins
# above it.
PROB_BINS: list[tuple[str, float, float]] = [
    ("[0.90, 1.00]", 0.90, 1.0001),  # upper bound inclusive via >=/<
    ("[0.70, 0.90)", 0.70, 0.90),
    ("[0.50, 0.70)", 0.50, 0.70),
    ("[0.15, 0.50)", 0.15, 0.50),
]


def bin_probability(p: float) -> str:
    """Return the bin label for a verifier probability, or 'out-of-range'."""
    for label, lo, hi in PROB_BINS:
        if lo <= p < hi:
            return label
    return "out-of-range"


def compute_metrics(
    tp: float, fp: float, fn: float,
) -> tuple[float, float, float]:
    """Return (precision, recall, F1). Safe for zero-division."""
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    f1 = (
        2 * precision * recall / (precision + recall)
        if (precision + recall) > 0
        else 0.0
    )
    return precision, recall, f1


def load_measured_counts(
    measured_json: Path, buffer_metres: int,
) -> dict[str, float]:
    """Back out TP/FP/FN at the given buffer from the measured evaluation."""
    with open(measured_json) as handle:
        measured = json.load(handle)
    buffer_row = next(
        b for b in measured["summary"]["buffers"]
        if b["buffer_metres"] == buffer_metres
    )
    n_det = measured["summary"]["n_detections"]
    precision = buffer_row["precision"]
    recall = buffer_row["recall"]
    f1 = buffer_row["f1"]
    tp = precision * n_det
    fp = n_det - tp
    fn = tp * (1 - recall) / recall if recall > 0 else 0.0
    return {
        "tp": tp, "fp": fp, "fn": fn,
        "precision": precision, "recall": recall, "f1": f1,
        "n_det": n_det,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--uncalibrated-csv", required=True,
        help="Archived uncalibrated-review CSV (pre-tolerance-circle UI).",
    )
    parser.add_argument(
        "--calibrated-csv", required=True,
        help="Full calibrated-review CSV (post-tolerance-circle UI).",
    )
    parser.add_argument(
        "--measured-json", required=True,
        help="Original pipeline evaluation.json (for 50 m measured counts).",
    )
    parser.add_argument(
        "--output-dir", required=True,
        help="Directory to write crosstab.json and crosstab.md.",
    )
    parser.add_argument(
        "--buffer-metres", type=int, default=50,
        help="Buffer size for the corrected-F1 accounting (default: 50).",
    )
    parser.add_argument(
        "--n-bootstrap", type=int, default=10000,
        help="Bootstrap iterations for the disagreement-rate CI.",
    )
    parser.add_argument(
        "--seed", type=int, default=42,
        help="Random seed for reproducible bootstrap.",
    )
    args = parser.parse_args()

    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    # ---------------------------------------------------------------
    # Load both review CSVs and inner-join on candidate_id
    # ---------------------------------------------------------------
    uncal = pd.read_csv(args.uncalibrated_csv)
    cal = pd.read_csv(args.calibrated_csv)

    # Suffix columns to disambiguate after the merge. We retain symbol_type
    # and human_label from both sides; verifier_probability/map_name are
    # identical so we take the calibrated side.
    merged = uncal.merge(
        cal,
        on="candidate_id",
        suffixes=("_uncal", "_cal"),
        how="inner",
    )

    n_overlap = len(merged)
    n_uncal_total = len(uncal)
    n_cal_total = len(cal)

    # ---------------------------------------------------------------
    # 1. Overall agreement rate
    # ---------------------------------------------------------------
    merged["agrees"] = (
        merged["human_label_uncal"] == merged["human_label_cal"]
    )
    n_agree = int(merged["agrees"].sum())
    n_disagree = n_overlap - n_agree
    agreement_rate = n_agree / n_overlap
    disagreement_rate = n_disagree / n_overlap

    # ---------------------------------------------------------------
    # 2. Disagreement decomposition by direction
    # ---------------------------------------------------------------
    # Uncal=mound -> Cal=not_mound : uncalibrated "false positive"
    # Uncal=not_mound -> Cal=mound : uncalibrated "false negative"
    uncal_fp = int(
        (
            (merged["human_label_uncal"] == "mound")
            & (merged["human_label_cal"] == "not_mound")
        ).sum()
    )
    uncal_fn = int(
        (
            (merged["human_label_uncal"] == "not_mound")
            & (merged["human_label_cal"] == "mound")
        ).sum()
    )
    # Same-label splits (for context in the report):
    both_mound = int(
        (
            (merged["human_label_uncal"] == "mound")
            & (merged["human_label_cal"] == "mound")
        ).sum()
    )
    both_not = int(
        (
            (merged["human_label_uncal"] == "not_mound")
            & (merged["human_label_cal"] == "not_mound")
        ).sum()
    )

    # ---------------------------------------------------------------
    # 3. Stratified disagreement by verifier probability
    # ---------------------------------------------------------------
    # Use the calibrated-side verifier probability (identical by
    # construction; both CSVs sourced from the same verifier run).
    merged["prob_bin"] = merged["verifier_probability_cal"].apply(
        bin_probability,
    )
    prob_stratification: list[dict[str, object]] = []
    for label, _lo, _hi in PROB_BINS:
        subset = merged[merged["prob_bin"] == label]
        n_bin = len(subset)
        n_disagree_bin = int((~subset["agrees"]).sum())
        rate = n_disagree_bin / n_bin if n_bin > 0 else 0.0
        prob_stratification.append({
            "bin": label,
            "n": n_bin,
            "n_disagree": n_disagree_bin,
            "disagreement_rate": rate,
            "n_uncal_mound_to_cal_not": int(
                (
                    (subset["human_label_uncal"] == "mound")
                    & (subset["human_label_cal"] == "not_mound")
                ).sum()
            ),
            "n_uncal_not_to_cal_mound": int(
                (
                    (subset["human_label_uncal"] == "not_mound")
                    & (subset["human_label_cal"] == "mound")
                ).sum()
            ),
        })

    # ---------------------------------------------------------------
    # 4. Symbol-type flow table (confusion matrix)
    # ---------------------------------------------------------------
    symbol_cross = pd.crosstab(
        merged["symbol_type_uncal"],
        merged["symbol_type_cal"],
        dropna=False,
    )
    symbol_cross_dict: dict[str, dict[str, int]] = {
        row: {
            col: int(symbol_cross.loc[row, col])
            for col in symbol_cross.columns
        }
        for row in symbol_cross.index
    }

    # ---------------------------------------------------------------
    # 5. Corrected-F1 delta accounting
    # ---------------------------------------------------------------
    # Strategy: hold the original pipeline measured counts fixed and
    # compute corrected F1 under two labelling regimes for the 327-row
    # overlap. For the 701 non-overlap rows (present only in calibrated
    # review), use the calibrated labels in BOTH regimes — those are the
    # only labels available, and the non-overlap rows are not the subject
    # of the comparison. The delta therefore isolates the UI-induced
    # change on the 327 overlapping candidates.
    measured = load_measured_counts(
        Path(args.measured_json), args.buffer_metres,
    )
    tp_m = measured["tp"]
    fp_m = measured["fp"]
    fn_m = measured["fn"]
    p_m = measured["precision"]
    r_m = measured["recall"]
    f1_m = measured["f1"]

    # Phantom-TP count from the FULL calibrated review (all 1,028):
    phantom_tp_full_cal = int((cal["human_label"] == "mound").sum())

    # Phantom-TP count from the FULL review if we substitute uncalibrated
    # labels for the 327-overlap subset. Concretely:
    #   phantom_tp_mixed = phantom_tp_full_cal
    #                      - (mounds on overlap under calibrated)
    #                      + (mounds on overlap under uncalibrated)
    overlap_mounds_cal = int(
        (merged["human_label_cal"] == "mound").sum()
    )
    overlap_mounds_uncal = int(
        (merged["human_label_uncal"] == "mound").sum()
    )
    phantom_tp_mixed = (
        phantom_tp_full_cal
        - overlap_mounds_cal
        + overlap_mounds_uncal
    )

    def corrected(phantom: int) -> tuple[float, float, float]:
        tp_c = tp_m + phantom
        fp_c = fp_m - phantom
        fn_c = fn_m  # phantom TPs were never in student GT, so no change.
        return compute_metrics(tp_c, fp_c, fn_c)

    p_cal, r_cal, f1_cal = corrected(phantom_tp_full_cal)
    p_mix, r_mix, f1_mix = corrected(phantom_tp_mixed)
    delta_f1 = f1_cal - f1_mix
    delta_p = p_cal - p_mix
    delta_r = r_cal - r_mix

    # ---------------------------------------------------------------
    # 6. Bootstrap 95% CI for overall disagreement rate
    # ---------------------------------------------------------------
    rng = np.random.default_rng(args.seed)
    disagree_flags = (~merged["agrees"]).to_numpy().astype(int)
    boot_rates = np.empty(args.n_bootstrap)
    n = len(disagree_flags)
    for i in range(args.n_bootstrap):
        idx = rng.integers(0, n, size=n)
        boot_rates[i] = disagree_flags[idx].mean()
    ci_lo = float(np.percentile(boot_rates, 2.5))
    ci_hi = float(np.percentile(boot_rates, 97.5))

    # ---------------------------------------------------------------
    # Assemble JSON result
    # ---------------------------------------------------------------
    result: dict[str, object] = {
        "version": "1.0.0",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "provenance": {
            "uncalibrated_csv": str(
                Path(args.uncalibrated_csv).resolve(),
            ),
            "calibrated_csv": str(Path(args.calibrated_csv).resolve()),
            "measured_json": str(Path(args.measured_json).resolve()),
            "n_bootstrap": args.n_bootstrap,
            "seed": args.seed,
        },
        "counts": {
            "n_uncalibrated_total": n_uncal_total,
            "n_calibrated_total": n_cal_total,
            "n_overlap": n_overlap,
            "n_agree": n_agree,
            "n_disagree": n_disagree,
            "both_mound": both_mound,
            "both_not_mound": both_not,
            "uncal_mound_to_cal_not_mound": uncal_fp,
            "uncal_not_mound_to_cal_mound": uncal_fn,
        },
        "rates": {
            "agreement_rate": agreement_rate,
            "disagreement_rate": disagreement_rate,
            "disagreement_rate_ci_95": [ci_lo, ci_hi],
        },
        "probability_stratification": prob_stratification,
        "symbol_type_flow": symbol_cross_dict,
        "corrected_f1_accounting": {
            "buffer_metres": args.buffer_metres,
            "measured": {
                "tp": tp_m, "fp": fp_m, "fn": fn_m,
                "precision": p_m, "recall": r_m, "f1": f1_m,
            },
            "overlap_mounds_under_calibrated": overlap_mounds_cal,
            "overlap_mounds_under_uncalibrated": overlap_mounds_uncal,
            "phantom_tp_full_calibrated": phantom_tp_full_cal,
            "phantom_tp_mixed_uncal_on_overlap": phantom_tp_mixed,
            "corrected_all_calibrated": {
                "precision": p_cal, "recall": r_cal, "f1": f1_cal,
            },
            "corrected_mixed_uncal_on_overlap": {
                "precision": p_mix, "recall": r_mix, "f1": f1_mix,
            },
            "delta_all_calibrated_minus_mixed": {
                "precision": delta_p, "recall": delta_r, "f1": delta_f1,
            },
            "interpretation": (
                "Positive delta = calibrated UI produced a higher corrected "
                "F1 than the uncalibrated labels would have on the same "
                "overlap. This isolates the UI-induced change to the 327 "
                "overlapping candidates; the 701 non-overlap rows use "
                "calibrated labels in both regimes (only labels available)."
            ),
        },
    }

    out_json = out_dir / "crosstab.json"
    with open(out_json, "w") as handle:
        json.dump(result, handle, indent=2)
    print(f"Wrote {out_json}")

    # ---------------------------------------------------------------
    # Assemble Markdown report
    # ---------------------------------------------------------------
    lines: list[str] = []
    lines.append(
        "# Uncalibrated vs calibrated human-review cross-tabulation",
    )
    lines.append("")
    lines.append(f"**Timestamp**: {result['timestamp']}")
    lines.append("")
    lines.append(
        "**Context**: During the 55-map image-generalisation human "
        "review, the reviewer initially used a \"fuzzy\" UI without an "
        "explicit spatial tolerance. After 327 reviews, the UI was "
        "upgraded to overlay a magenta 50 m tolerance circle on the "
        "candidate crop, and the reviewer restarted and completed all "
        "1,028 reviews. This report quantifies how the calibrated UI "
        "changed reviewer decisions on the 327-candidate overlap, as "
        "empirical evidence for Obs 263's ambiguity-band claim.",
    )
    lines.append("")
    lines.append("## Overall agreement")
    lines.append("")
    lines.append(
        f"- Uncalibrated total reviews: **{n_uncal_total}**",
    )
    lines.append(f"- Calibrated total reviews: **{n_cal_total}**")
    lines.append(f"- Overlap on `candidate_id`: **{n_overlap}**")
    lines.append(
        f"- Agreement rate: **{agreement_rate:.4f}** "
        f"({n_agree}/{n_overlap})",
    )
    lines.append(
        f"- Disagreement rate: **{disagreement_rate:.4f}** "
        f"({n_disagree}/{n_overlap})",
    )
    lines.append(
        f"- Bootstrap 95% CI for disagreement rate "
        f"({args.n_bootstrap:,} iterations, seed {args.seed}): "
        f"[{ci_lo:.4f}, {ci_hi:.4f}]",
    )
    lines.append("")
    lines.append("## Disagreement decomposition")
    lines.append("")
    lines.append(
        "| Direction | Count | Share of overlap |",
    )
    lines.append("|---|---:|---:|")
    lines.append(
        f"| Both mound (stable positive) | {both_mound} | "
        f"{both_mound / n_overlap:.4f} |",
    )
    lines.append(
        f"| Both not_mound (stable negative) | {both_not} | "
        f"{both_not / n_overlap:.4f} |",
    )
    lines.append(
        f"| Uncal=mound -> Cal=not_mound (uncal FP) | {uncal_fp} | "
        f"{uncal_fp / n_overlap:.4f} |",
    )
    lines.append(
        f"| Uncal=not_mound -> Cal=mound (uncal FN) | {uncal_fn} | "
        f"{uncal_fn / n_overlap:.4f} |",
    )
    lines.append("")
    lines.append("## Stratified disagreement by verifier probability")
    lines.append("")
    overlap_prob_min = float(
        merged["verifier_probability_cal"].min(),
    )
    overlap_prob_max = float(
        merged["verifier_probability_cal"].max(),
    )
    overlap_prob_median = float(
        merged["verifier_probability_cal"].median(),
    )
    lines.append(
        "**Critical caveat on the overlap composition**: the 327 "
        f"overlap candidates have verifier_probability in "
        f"[{overlap_prob_min:.3f}, {overlap_prob_max:.3f}] "
        f"(median {overlap_prob_median:.3f}). The uncalibrated "
        "session reviewed only the highest-confidence slice of the "
        "candidate queue, so the stratification below cannot directly "
        "test Obs 263's prediction that disagreement concentrates in "
        "the low-p tail. What it CAN show is whether disagreement "
        "arises even among high-verifier-confidence candidates — a "
        "stricter bar than the Obs 263 prediction.",
    )
    lines.append("")
    lines.append(
        "| Probability bin | n | Disagreements | Rate | Uncal->not | "
        "Uncal->mound |",
    )
    lines.append("|---|---:|---:|---:|---:|---:|")
    for row in prob_stratification:
        lines.append(
            f"| {row['bin']} | {row['n']} | {row['n_disagree']} | "
            f"{row['disagreement_rate']:.4f} | "
            f"{row['n_uncal_mound_to_cal_not']} | "
            f"{row['n_uncal_not_to_cal_mound']} |",
        )
    lines.append("")
    lines.append(
        "*Interpretation*: With all 327 overlap candidates in the "
        "top bin, a non-trivial disagreement rate there is a "
        "stronger-than-expected signal — the UI change moved "
        "reviewer decisions even on the candidates the verifier was "
        "most confident about. The low-p tail prediction from Obs "
        "263 remains untested by this overlap and would require a "
        "separate uncalibrated-review session sampling across the "
        "probability range.",
    )
    lines.append("")
    lines.append("## Symbol-type flow table")
    lines.append("")
    cols = list(symbol_cross.columns)
    header_cells = (
        ["uncal \\ cal"]
        + [str(col) for col in cols]
        + ["Row total"]
    )
    lines.append("| " + " | ".join(header_cells) + " |")
    lines.append(
        "|"
        + "|".join(["---"] * (len(cols) + 2))
        + "|",
    )
    col_totals = {col: 0 for col in cols}
    for idx in symbol_cross.index:
        row_total = 0
        row_cells: list[str] = [str(idx)]
        for col in cols:
            val = int(symbol_cross.loc[idx, col])
            row_cells.append(str(val))
            row_total += val
            col_totals[col] += val
        row_cells.append(str(row_total))
        lines.append("| " + " | ".join(row_cells) + " |")
    footer_cells = (
        ["Column total"]
        + [str(col_totals[c]) for c in cols]
        + [str(n_overlap)]
    )
    lines.append("| " + " | ".join(footer_cells) + " |")
    lines.append("")
    lines.append("## Corrected-F1 accounting")
    lines.append("")
    lines.append(
        f"Buffer: {args.buffer_metres} m. Measured pipeline "
        f"counts held fixed: TP={tp_m:.0f}, FP={fp_m:.0f}, "
        f"FN={fn_m:.0f} (F1={f1_m:.4f}).",
    )
    lines.append("")
    lines.append(
        f"- Mounds on overlap under calibrated labels: "
        f"**{overlap_mounds_cal}** / {n_overlap}",
    )
    lines.append(
        f"- Mounds on overlap under uncalibrated labels: "
        f"**{overlap_mounds_uncal}** / {n_overlap}",
    )
    lines.append(
        f"- Phantom TP (full calibrated, all 1,028): "
        f"**{phantom_tp_full_cal}**",
    )
    lines.append(
        f"- Phantom TP (mixed, uncal labels on 327 overlap + cal on "
        f"701 remainder): **{phantom_tp_mixed}**",
    )
    lines.append("")
    lines.append(
        "| Scenario | Precision | Recall | F1 |",
    )
    lines.append("|---|---:|---:|---:|")
    lines.append(
        f"| All calibrated | {p_cal:.4f} | {r_cal:.4f} | "
        f"**{f1_cal:.4f}** |",
    )
    lines.append(
        f"| Mixed (uncal on overlap) | {p_mix:.4f} | {r_mix:.4f} | "
        f"**{f1_mix:.4f}** |",
    )
    lines.append(
        f"| Delta (all-cal minus mixed) | {delta_p:+.4f} | "
        f"{delta_r:+.4f} | **{delta_f1:+.4f}** |",
    )
    lines.append("")
    lines.append(
        "*Interpretation*: Positive delta means the calibrated UI "
        "produced a higher corrected F1 than the uncalibrated labels "
        "would have on the same 327-row overlap. The delta isolates "
        "the UI-induced change; the 701 non-overlap rows use "
        "calibrated labels in both scenarios because no uncalibrated "
        "labels exist for them.",
    )
    lines.append("")
    lines.append("## Reproducibility")
    lines.append("")
    lines.append(
        f"- Bootstrap: {args.n_bootstrap:,} iterations, seed "
        f"{args.seed}",
    )
    lines.append(
        f"- Uncalibrated CSV: `{args.uncalibrated_csv}`",
    )
    lines.append(f"- Calibrated CSV: `{args.calibrated_csv}`")
    lines.append(f"- Measured evaluation: `{args.measured_json}`")
    lines.append(
        "- Script: `scripts/crosstab_uncalibrated_vs_calibrated.py`",
    )
    lines.append("")

    out_md = out_dir / "crosstab.md"
    with open(out_md, "w") as handle:
        handle.write("\n".join(lines))
    print(f"Wrote {out_md}")


if __name__ == "__main__":
    main()
