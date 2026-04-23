#!/usr/bin/env python3
"""Compute corrected F1/P/R at 50 m buffer using human-reviewed labels.

Replaces the Dawid-Skene aggregate posterior correction with per-item human
review. The review was conducted against the 1,028 VLM-only candidates from
the 55-map image generalisation run with a calibrated 50 m tolerance circle
UI (see `docs/notes/reflections/working-notes.md` Obs 263–266 for caveats).

This analysis is valid ONLY at the 50 m buffer because the review required
each candidate's symbol centre to fall inside the 50 m tolerance circle.
Reviewers did not record the symbol's pixel position within the circle, so
tighter-buffer corrections are not derivable from this output.

Uncertainty propagation: the measured F1/P/R already have bootstrap CIs from
the original pipeline evaluation. The corrected metrics' CIs are computed by
bootstrapping the human-review labels (resampling 1,028 rows with
replacement) — this captures the sampling variability introduced by the
review but keeps the pipeline counts fixed. The resulting CI is the
"human-review uncertainty" component only; the original pipeline CI is
complementary but not commensurable, so both are reported side-by-side.

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


def compute_metrics(
    tp: float, fp: float, fn: float,
) -> tuple[float, float, float]:
    """Return (precision, recall, F1) from raw counts. Safe for zero-division."""
    p = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    r = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    f1 = 2 * p * r / (p + r) if (p + r) > 0 else 0.0
    return p, r, f1


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--review-csv", required=True,
        help="Path to the human-review CSV.",
    )
    parser.add_argument(
        "--measured-json", required=True,
        help="Path to the original evaluation.json (for 50 m measured "
             "counts).",
    )
    parser.add_argument(
        "--output-dir", required=True,
        help="Directory to write the corrected-F1 report and JSON.",
    )
    parser.add_argument(
        "--buffer-metres", type=int, default=50,
        help="Buffer size this correction applies to (50 only; other "
             "values produce an invalid estimate — see module docstring).",
    )
    parser.add_argument(
        "--n-bootstrap", type=int, default=10000,
        help="Number of bootstrap iterations for human-review CI.",
    )
    parser.add_argument(
        "--seed", type=int, default=42,
        help="Random seed for reproducible bootstrap.",
    )
    args = parser.parse_args()

    if args.buffer_metres != 50:
        raise ValueError(
            f"--buffer-metres={args.buffer_metres}: this correction is "
            f"valid only at 50 m. See script docstring."
        )

    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    # ---------------------------------------------------------------
    # Load measured metrics and back out raw counts
    # ---------------------------------------------------------------
    measured = json.load(open(args.measured_json))
    buffer_row = next(
        b for b in measured["summary"]["buffers"]
        if b["buffer_metres"] == args.buffer_metres
    )
    n_det = measured["summary"]["n_detections"]
    p_m = buffer_row["precision"]
    r_m = buffer_row["recall"]
    f1_m = buffer_row["f1"]
    # Back out counts: TP = P * n_detections, FN = TP*(1-R)/R
    tp_m = p_m * n_det
    fp_m = n_det - tp_m
    fn_m = tp_m * (1 - r_m) / r_m if r_m > 0 else 0.0
    n_ref = tp_m + fn_m

    print(
        f"Measured at {args.buffer_metres} m: "
        f"F1={f1_m:.4f} P={p_m:.4f} R={r_m:.4f}"
    )
    print(
        f"Derived counts: TP={tp_m:.0f} FP={fp_m:.0f} FN={fn_m:.0f} "
        f"n_ref={n_ref:.0f}"
    )

    # ---------------------------------------------------------------
    # Load human review and compute phantom-TP count
    # ---------------------------------------------------------------
    review = pd.read_csv(args.review_csv)
    if "buffer_metres" in review.columns:
        buffers_present = review["buffer_metres"].dropna().unique()
        if list(buffers_present) != [args.buffer_metres]:
            raise ValueError(
                f"Review CSV has buffer_metres values "
                f"{buffers_present.tolist()}; expected only "
                f"{args.buffer_metres}."
            )

    n_reviewed = len(review)
    phantom_tp = int((review["human_label"] == "mound").sum())
    phantom_fp = n_reviewed - phantom_tp

    print(
        f"\nHuman review: {n_reviewed} candidates reviewed at "
        f"{args.buffer_metres} m tolerance"
    )
    print(f"Phantom TP: {phantom_tp} "
          f"({100*phantom_tp/n_reviewed:.1f}% of VLM-only set)")
    print(f"Confirmed FP: {phantom_fp} "
          f"({100*phantom_fp/n_reviewed:.1f}%)")

    # ---------------------------------------------------------------
    # Corrected counts (point estimate)
    # ---------------------------------------------------------------
    # Phantom TPs are real mounds the student GT missed. They become:
    #   - added to TP count (were unmatched, now count as matched to
    #     newly-discovered real mounds);
    #   - removed from FP count;
    #   - added to the denominator of recall (extended GT = student GT
    #     + phantom mounds) but NOT to FN, because they weren't missed.
    tp_c = tp_m + phantom_tp
    fp_c = fp_m - phantom_tp
    fn_c = fn_m  # unchanged — phantom TPs weren't in student GT
    n_ref_ext = n_ref + phantom_tp

    p_c, r_c, f1_c = compute_metrics(tp_c, fp_c, fn_c)
    print(
        f"\nCorrected at {args.buffer_metres} m (point estimate): "
        f"F1={f1_c:.4f} P={p_c:.4f} R={r_c:.4f}"
    )
    print(
        f"Delta from measured: "
        f"F1 {f1_c - f1_m:+.4f}, "
        f"P {p_c - p_m:+.4f}, "
        f"R {r_c - r_m:+.4f}"
    )

    # ---------------------------------------------------------------
    # Bootstrap over human-review labels for CI
    # ---------------------------------------------------------------
    rng = np.random.default_rng(args.seed)
    labels = (review["human_label"] == "mound").to_numpy().astype(int)
    n = len(labels)

    f1_samples = np.empty(args.n_bootstrap)
    p_samples = np.empty(args.n_bootstrap)
    r_samples = np.empty(args.n_bootstrap)

    for i in range(args.n_bootstrap):
        idx = rng.integers(0, n, size=n)
        phantom_tp_b = labels[idx].sum()
        tp_b = tp_m + phantom_tp_b
        fp_b = fp_m - phantom_tp_b
        p_b, r_b, f1_b = compute_metrics(tp_b, fp_b, fn_m)
        p_samples[i] = p_b
        r_samples[i] = r_b
        f1_samples[i] = f1_b

    def ci(samples: np.ndarray) -> tuple[float, float]:
        return (
            float(np.percentile(samples, 2.5)),
            float(np.percentile(samples, 97.5)),
        )

    p_ci = ci(p_samples)
    r_ci = ci(r_samples)
    f1_ci = ci(f1_samples)

    print(
        "\n95% bootstrap CIs (human-review sampling variability only):"
    )
    print(f"  F1: [{f1_ci[0]:.4f}, {f1_ci[1]:.4f}]")
    print(f"  P:  [{p_ci[0]:.4f}, {p_ci[1]:.4f}]")
    print(f"  R:  [{r_ci[0]:.4f}, {r_ci[1]:.4f}]")

    # ---------------------------------------------------------------
    # Save outputs
    # ---------------------------------------------------------------
    result = {
        "version": "1.0.0",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "provenance": {
            "review_csv": str(Path(args.review_csv).resolve()),
            "measured_json": str(Path(args.measured_json).resolve()),
            "n_bootstrap": args.n_bootstrap,
            "seed": args.seed,
        },
        "buffer_metres": args.buffer_metres,
        "validity_note": (
            "Corrected metrics are valid ONLY at 50 m buffer because the "
            "review required the symbol centre to fall inside the 50 m "
            "tolerance circle. Reviewers did not record symbol positions "
            "within the circle, so tighter-buffer corrections are not "
            "derivable. See docs/notes/reflections/working-notes.md "
            "Obs 263 for the underlying methodology discussion."
        ),
        "reviewer_bias_note": (
            "Reviewer decision policy is asymmetric — ambiguous cases are "
            "marked not-mound by default (Obs 263 follow-up). Corrected "
            "F1 should be read as a conservative estimate; the D-S "
            "aggregate-posterior F1 (0.795) is the complementary "
            "weighted-average estimate. The honest interval spans both."
        ),
        "measured": {
            "f1": f1_m, "precision": p_m, "recall": r_m,
            "tp": tp_m, "fp": fp_m, "fn": fn_m,
            "n_detections": n_det, "n_ref": n_ref,
            "f1_ci": [
                buffer_row["f1_ci_lower"],
                buffer_row["f1_ci_upper"],
            ],
            "precision_ci": [
                buffer_row["p_ci_lower"],
                buffer_row["p_ci_upper"],
            ],
            "recall_ci": [
                buffer_row["r_ci_lower"],
                buffer_row["r_ci_upper"],
            ],
            "ci_note": (
                "Original pipeline bootstrap CIs; capture matching and "
                "detection variability."
            ),
        },
        "human_review": {
            "n_reviewed": n_reviewed,
            "phantom_tp": phantom_tp,
            "confirmed_fp": phantom_fp,
            "phantom_tp_fraction": phantom_tp / n_reviewed,
        },
        "corrected": {
            "f1": f1_c, "precision": p_c, "recall": r_c,
            "tp": tp_c, "fp": fp_c, "fn": fn_c,
            "n_ref_extended": n_ref_ext,
            "f1_ci": list(f1_ci),
            "precision_ci": list(p_ci),
            "recall_ci": list(r_ci),
            "ci_note": (
                "Bootstrap CIs over human-review labels only; capture "
                "review-sampling variability. NOT commensurable with the "
                "measured CIs above — they quantify different uncertainty "
                "sources."
            ),
        },
        "dawid_skene_comparison": {
            "note": (
                "The previous Dawid-Skene aggregate posterior estimated "
                "~186 phantom TPs out of 1028 (18.1%), yielding corrected "
                "F1 of 0.795. The human-reviewed estimate of "
                f"{phantom_tp} phantom TPs ({100*phantom_tp/n_reviewed:.1f}%) "
                "is substantially higher — consistent with Obs 263's "
                "observation that crop review catches more than aggregate "
                "posterior methods."
            ),
        },
    }

    out_json = out_dir / "corrected-f1-human-reviewed.json"
    with open(out_json, "w") as f:
        json.dump(result, f, indent=2)
    print(f"\nWrote {out_json}")

    # Markdown report
    md = f"""# Corrected F1/P/R at 50 m — human-reviewed

**Timestamp**: {result["timestamp"]}
**Review CSV**: `{args.review_csv}`
**Buffer**: {args.buffer_metres} m (the ONLY buffer at which this correction is valid)

## Headline numbers

| Metric | Measured | Measured 95% CI | Corrected | Corrected 95% CI (review-only) |
|--------|---------:|:---------------:|----------:|:------------------------------:|
| F1 | {f1_m:.4f} | [{buffer_row["f1_ci_lower"]:.4f}, {buffer_row["f1_ci_upper"]:.4f}] | **{f1_c:.4f}** | [{f1_ci[0]:.4f}, {f1_ci[1]:.4f}] |
| Precision | {p_m:.4f} | [{buffer_row["p_ci_lower"]:.4f}, {buffer_row["p_ci_upper"]:.4f}] | **{p_c:.4f}** | [{p_ci[0]:.4f}, {p_ci[1]:.4f}] |
| Recall | {r_m:.4f} | [{buffer_row["r_ci_lower"]:.4f}, {buffer_row["r_ci_upper"]:.4f}] | **{r_c:.4f}** | [{r_ci[0]:.4f}, {r_ci[1]:.4f}] |

**Delta from measured**: F1 {f1_c - f1_m:+.4f}, P {p_c - p_m:+.4f}, R {r_c - r_m:+.4f}.

## Caveats

- **50 m only**: this correction is valid only at the 50 m buffer. Reviewers
  judged each candidate against the 50 m tolerance circle and did not record
  symbol positions within the circle; tighter-buffer corrections are not
  derivable from this output. See Obs 263 in
  `docs/notes/reflections/working-notes.md`.
- **Conservative bias**: the reviewer's decision policy is asymmetric —
  ambiguous cases default to not-mound (Obs 263 follow-up). The corrected F1
  is therefore a **lower bound**, not a point estimate. The Dawid-Skene
  aggregate-posterior F1 (0.795, see `results/55maps-image-generalisation/dawid-skene/`)
  is the complementary weighted-average estimate and represents a tentative
  upper-bound for the comparison.
- **CI incompatibility**: the measured CI and the corrected CI capture
  different uncertainty sources. Measured CI bootstraps over pipeline
  matching variability; corrected CI bootstraps over human-review labels.
  They are not commensurable — do not compute a single "combined" CI by
  intersection or union without a joint bootstrap.

## Counts

### Measured (at 50 m)
- TP: {tp_m:.0f}
- FP: {fp_m:.0f}
- FN: {fn_m:.0f}
- n_detections: {n_det}
- n_ref: {n_ref:.0f}

### Human review
- Reviewed: {n_reviewed} VLM-only candidates
- Phantom TP (marked as real mound): **{phantom_tp}** ({100*phantom_tp/n_reviewed:.1f}%)
- Confirmed FP (marked not-mound): {phantom_fp} ({100*phantom_fp/n_reviewed:.1f}%)

### Corrected (at 50 m)
- TP_corrected: {tp_c:.0f} (measured + {phantom_tp} phantom)
- FP_corrected: {fp_c:.0f} (measured − {phantom_tp} reassigned)
- FN_corrected: {fn_c:.0f} (unchanged — phantom TPs weren't in student GT)
- n_ref_extended: {n_ref_ext:.0f} (student GT + {phantom_tp} newly-discovered mounds)

## Dawid-Skene comparison

| Method | Phantom-TP estimate | Corrected F1 |
|--------|--------------------:|-------------:|
| Measured (no correction) | 0 | {f1_m:.4f} |
| Dawid-Skene aggregate posterior | ~186 (18.1%) | 0.7950 |
| **Human review (per-item)** | **{phantom_tp} ({100*phantom_tp/n_reviewed:.1f}%)** | **{f1_c:.4f}** |

The human-reviewed estimate is {100*phantom_tp/n_reviewed - 18.1:+.1f} percentage
points higher than the D-S aggregate posterior. Consistent with Obs 263: crop
review catches more than aggregate posterior methods because it can identify
individual phantom mounds rather than only estimating their aggregate rate.

## Reproducibility

- Bootstrap: {args.n_bootstrap:,} iterations, seed {args.seed}
- Inputs: `{args.review_csv}`, `{args.measured_json}`
- Script: `scripts/compute_corrected_f1_human_reviewed.py`
"""

    # Session 76 guardrail: hand-authored corrected-f1-human-reviewed.md is
    # the paper-citation source. Script writes to _autogen.md sibling so the
    # hand-authored level-up is protected against dry-run overwrites (Session
    # 75 Guardrail 6).
    out_md = out_dir / "corrected-f1-human-reviewed_autogen.md"
    with open(out_md, "w") as f:
        f.write(md)
    print(f"Wrote {out_md}")


if __name__ == "__main__":
    main()
