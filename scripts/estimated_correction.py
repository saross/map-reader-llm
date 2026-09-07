#!/usr/bin/env python3
"""
The estimated-correction column: the reference error the reviewers did NOT see.

Step 6 of ``planning/reference-revision-2026-09-06.md`` (§ 2). The board's
"corrected F1" already removes the reference error the audits saw (r2 is
the standardised reference with the cluster and empty-tile adjudications
applied). This column estimates the error they did not see, from the rates
the audits measured, and carries the uncertainty. It is presented BESIDE the
r2 point estimate and is never used to re-tier (hardening H9): the
correction is corpus-level and applied uniformly, so it cannot re-order a
board -- which is exactly why it is a column and not a re-tiering.

Rates (each a count over a denominator; Clopper-Pearson-compatible Beta
posteriors with a flat prior are drawn in the Monte Carlo):

* ``p_dm_empty`` -- double-misses per empty tile, 5 / 470, applied to the
  4,676-tile empty frame: residual missed mounds M that today sit in
  neither TP nor FN of any condition.
* ``p_dm_cluster`` -- double-misses per clustered mound, 2 / 719: the
  cluster census is COMPLETE, its two double-misses are already in r2, so
  nothing is extrapolated from it; the rate is recorded, not applied.
* ``p_err`` -- reference points that are not mounds, 6 / 719, extrapolated
  to the 4,291 non-clustered, non-audited points: expected E_err GT errors
  that today count as FN (undetected) or TP (a detection on the wrong
  point).
* ``p_om`` -- reference omissions the model already found, 6 / 719, over
  the same 4,291: expected E_om model "false positives" that are real
  mounds.

Per condition, from its TP / FP / FN at 50 m (recovered from the committed
precision, recall and detection count), each Monte Carlo draw applies::

    conv = min(E_om, FP)                 # FPs that are really mounds
    TP'  = TP + conv - E_err * r         # r = TP / (TP + FN): the share of
    FP'  = FP - conv                     #   GT errors a condition detects
    FN'  = FN - E_err * (1 - r) + M      # M: the unseen double-misses

and reports P-hat, R-hat, F1-hat as the mean and 2.5-97.5 percentile
interval over 10,000 draws (seed 42), plus the value at the rate point
estimates. Assumptions stated with the output (§ 2): (i) p_err and p_om
outside the clusters are taken from the cluster census; (ii) the
per-condition split of E_om is not measured -- the correction is uniform;
(iii) a condition detects GT errors at its own recall (the r-split above).

Usage::

    python scripts/estimated_correction.py                # r2 final board
    python scripts/estimated_correction.py --out-dir /tmp/x   # scratch

Zero API; seconds.

Created: 2026-09-07 (Session 149-c)
Author: Shawn Ross, Claude Code
Licence: Apache 2.0
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path

import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.build_55map_leaderboard import BOARD_HOME_BY_REFERENCE  # noqa: E402

DEFAULT_BOARD = BOARD_HOME_BY_REFERENCE["r2"] / "final_board_50m.json"
DRAWS = 10_000
SEED = 42

#: The audit-measured rates (card § 2; results/empty-tile-audit and
#: results/cluster-audit adjudications) as (successes, trials) and the
#: population each is applied to. ``applied_to`` of 0 means recorded only.
RATES: dict[str, dict] = {
    "p_dm_empty": {"k": 5, "n": 470, "applied_to": 4676,
                   "meaning": "double-misses per empty tile -> unseen missed mounds M"},
    "p_dm_cluster": {"k": 2, "n": 719, "applied_to": 0,
                     "meaning": "double-misses per clustered mound (census complete; in r2 already)"},
    "p_err": {"k": 6, "n": 719, "applied_to": 4291,
              "meaning": "reference points that are not mounds -> E_err"},
    "p_om": {"k": 6, "n": 719, "applied_to": 4291,
             "meaning": "reference omissions the model already found -> E_om"},
}


@dataclass
class Counts:
    """A condition's 50 m counts, recovered from its committed P, R, n."""

    tp: float
    fp: float
    fn: float

    @classmethod
    def from_prn(cls, precision: float, recall: float, n_detections: int) -> Counts:
        tp = precision * n_detections
        fp = n_detections - tp
        fn = (tp / recall - tp) if recall > 0 else float("nan")
        return cls(tp, fp, fn)


def prf(tp, fp, fn):
    """Precision, recall, F1 (vectorised; NaN-safe on empty denominators)."""
    with np.errstate(divide="ignore", invalid="ignore"):
        p = np.where(tp + fp > 0, tp / (tp + fp), np.nan)
        r = np.where(tp + fn > 0, tp / (tp + fn), np.nan)
        f = np.where(p + r > 0, 2 * p * r / (p + r), np.nan)
    return p, r, f


def apply_correction(c: Counts, m, e_err, e_om):
    """The § 2 correction for one condition, vectorised over draws.

    Args:
        c: The condition's counts.
        m: Unseen missed mounds per draw (array or scalar).
        e_err: Expected GT errors per draw.
        e_om: Expected model-found omissions per draw.

    Returns:
        (P-hat, R-hat, F1-hat) arrays.
    """
    m, e_err, e_om = (np.asarray(x, dtype=float) for x in (m, e_err, e_om))
    r = c.tp / (c.tp + c.fn)  # the share of GT errors this condition detects
    conv = np.minimum(e_om, c.fp)
    tp2 = c.tp + conv - e_err * r
    fp2 = c.fp - conv
    fn2 = c.fn - e_err * (1 - r) + m
    return prf(tp2, fp2, fn2)


def draw_rates(rng: np.random.Generator, draws: int) -> dict[str, np.ndarray]:
    """Beta(k+1, n-k+1) draws (flat prior) for every rate."""
    return {name: rng.beta(spec["k"] + 1, spec["n"] - spec["k"] + 1, size=draws)
            for name, spec in RATES.items()}


def point_rates() -> dict[str, float]:
    return {name: spec["k"] / spec["n"] for name, spec in RATES.items()}


def estimate_board(board: dict, draws: int = DRAWS, seed: int = SEED) -> dict:
    """The column for every cell of a final board."""
    rng = np.random.default_rng(seed)
    rd = draw_rates(rng, draws)
    pr = point_rates()
    terms = lambda rates: (  # noqa: E731 -- one-line mapping of rates to counts
        rates["p_dm_empty"] * RATES["p_dm_empty"]["applied_to"],
        rates["p_err"] * RATES["p_err"]["applied_to"],
        rates["p_om"] * RATES["p_om"]["applied_to"],
    )
    m_d, err_d, om_d = terms(rd)
    m_p, err_p, om_p = terms(pr)
    rows = []
    for cell in board["cells"]:
        c = Counts.from_prn(cell["precision_50"], cell["recall_50"], cell["n_detections"])
        p, r, f = apply_correction(c, m_d, err_d, om_d)
        pp, rp, fp_ = apply_correction(c, m_p, err_p, om_p)

        def summ(x, point):
            return {"point": float(point), "mean": float(np.nanmean(x)),
                    "ci_lower": float(np.nanpercentile(x, 2.5)),
                    "ci_upper": float(np.nanpercentile(x, 97.5))}
        rows.append({
            "label": cell["label"], "basis": cell.get("basis"), "point_r2": cell["point"],
            "f1_50_r2": cell["f1_50"], "precision_50_r2": cell["precision_50"],
            "recall_50_r2": cell["recall_50"], "n_detections": cell["n_detections"],
            "counts_50": asdict(c),
            "precision_hat": summ(p, pp), "recall_hat": summ(r, rp), "f1_hat": summ(f, fp_),
            "delta_f1_hat_minus_r2": float(fp_ - cell["f1_50"]),
        })
    return {
        "generated_at_utc": datetime.now(UTC).isoformat(),
        "reference": board.get("reference"),
        "board": str(DEFAULT_BOARD.relative_to(PROJECT_ROOT)),
        "method": ("Monte Carlo propagation of Beta(k+1, n-k+1) posteriors on the "
                   "audit rates through the section-2 correction; uniform "
                   "corpus-level application; never used to re-tier (H9)"),
        "draws": draws, "seed": seed,
        "rates": {name: {**spec, "point": spec["k"] / spec["n"],
                         "ci95_beta": [float(np.percentile(rd[name], 2.5)),
                                       float(np.percentile(rd[name], 97.5))]}
                  for name, spec in RATES.items()},
        "expected_terms_point": {"M_unseen_missed": float(m_p), "E_err": float(err_p),
                                 "E_om": float(om_p)},
        "assumptions": [
            "(i) p_err and p_om outside the clusters are the cluster census's rates",
            "(ii) the per-condition split of E_om and E_err is not measured; the "
            "correction is corpus-level and uniform, so it cannot re-order a board",
            "(iii) a condition detects reference errors at its own recall (r-split)",
            "counts at 50 m are recovered from the committed precision, recall and "
            "detection count, so they carry that rounding",
        ],
        "cells": rows,
    }


def render_md(payload: dict) -> str:
    """The column as a markdown table beside the r2 point estimate."""
    t = payload["expected_terms_point"]
    lines = [
        "# The estimated-correction column — r2 final board @ 50 m",
        "",
        f"> **Last revised**: {payload['generated_at_utc'][:10]} (original publication). "
        "Card: `planning/reference-revision-2026-09-06.md` § 2. Generated by "
        "`scripts/estimated_correction.py`; this JSON's inputs are printed below.",
        "",
        "Beside the r2 point estimate — never in place of it, and never used to",
        "re-tier (H9). The correction is corpus-level and uniform; its width, not",
        "its direction, is the information.",
        "",
        "## Inputs",
        "",
        "| rate | k / n | point | 95 % (Beta) | applied to | meaning |",
        "|---|---:|---:|---|---:|---|",
    ]
    for name, spec in payload["rates"].items():
        lo, hi = spec["ci95_beta"]
        lines.append(f"| `{name}` | {spec['k']} / {spec['n']} | {spec['point']:.4f} | "
                     f"[{lo:.4f}, {hi:.4f}] | {spec['applied_to'] or 'recorded only'} | {spec['meaning']} |")
    lines += [
        "",
        f"Expected terms at the point rates: M (unseen missed) = {t['M_unseen_missed']:.1f}, "
        f"E_err = {t['E_err']:.1f}, E_om = {t['E_om']:.1f}. Draws {payload['draws']}, seed {payload['seed']}.",
        "",
        "## The column",
        "",
        "| cell | basis | F1@50 r2 | F1̂ | 95 % | P̂ | R̂ | ΔF1̂ |",
        "|---|---|---:|---:|---|---:|---:|---:|",
    ]
    for c in payload["cells"]:
        f, p, r = c["f1_hat"], c["precision_hat"], c["recall_hat"]
        lines.append(f"| {c['label']} | {c['basis']} | {c['f1_50_r2']:.4f} | {f['point']:.4f} | "
                     f"[{f['ci_lower']:.4f}, {f['ci_upper']:.4f}] | {p['point']:.4f} | "
                     f"{r['point']:.4f} | {c['delta_f1_hat_minus_r2']:+.4f} |")
    lines += ["", "## Assumptions", ""] + [f"- {a}" for a in payload["assumptions"]]
    return "\n".join(lines)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--board", type=Path, default=DEFAULT_BOARD)
    ap.add_argument("--out-dir", type=Path, default=DEFAULT_BOARD.parent)
    ap.add_argument("--draws", type=int, default=DRAWS)
    ap.add_argument("--seed", type=int, default=SEED)
    args = ap.parse_args()
    board = json.loads(args.board.read_text())
    payload = estimate_board(board, args.draws, args.seed)
    args.out_dir.mkdir(parents=True, exist_ok=True)
    (args.out_dir / "estimated-correction.json").write_text(json.dumps(payload, indent=2) + "\n")
    (args.out_dir / "estimated-correction.md").write_text(render_md(payload) + "\n")
    for c in payload["cells"][:5]:
        f = c["f1_hat"]
        print(f"  {c['label']:20s} r2 {c['f1_50_r2']:.4f}  F1^ {f['point']:.4f} "
              f"[{f['ci_lower']:.4f}, {f['ci_upper']:.4f}]  d {c['delta_f1_hat_minus_r2']:+.4f}")
    print(f"wrote {args.out_dir / 'estimated-correction.{json,md}'} ({len(payload['cells'])} cells)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
