#!/usr/bin/env python3
"""
Re-estimate the student (novice) baseline at 55-map corpus level on reference r2.

Step 9 of ``planning/reference-revision-2026-09-06.md`` (§ 2b). The novice
baseline was measured directly only on the four Gold Standard sheets
against the curator reference (Obs 316, 443: P 1.000 / R 0.9473 /
F1 0.9729 at 50 m), where the students made no false positives. On the
55-map corpus the student layer IS the reference's backbone, so student
precision was unmeasurable there -- until the cluster census flagged five
of the 686 clustered student points as not mounds. The audits therefore
support a corpus-level re-estimate:

* **precision** from the flagged share of student points (5 / 686,
  extrapolated to every student record);
* **recall** from the mounds the students missed: the reviewer-confirmed
  extension mounds (278 on r2), the audit additions (14), the estimated
  unrecovered double-misses in the empty frame (p_dm(empty) x 4,676), and
  the estimated model-found omissions outside the clusters
  (p_om x 4,291) -- the last two are the extrapolated terms;

with the same Monte Carlo propagation as the estimated-correction column
(``scripts/estimated_correction.py``: Beta(k+1, n-k+1) posteriors, 10,000
draws, seed 42). It reports three rows -- the corpus-level estimate, the
same without the two extrapolated terms, and the GS-4 direct figure -- and
never replaces the direct measurement: the two estimate different things
(a 4-sheet direct measurement on a curated reference versus a 55-sheet
model-assisted reconstruction), and their agreement is itself a result
for D.7.

Usage::

    python scripts/student_baseline_reestimate.py
    python scripts/student_baseline_reestimate.py --out-dir /tmp/x

Zero API; seconds.

Created: 2026-09-07 (Session 149-c)
Author: Shawn Ross, Claude Code
Licence: Apache 2.0
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import UTC, datetime
from pathlib import Path

import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.estimated_correction import DRAWS, RATES, SEED, draw_rates  # noqa: E402

DEFAULT_OUT_DIR = PROJECT_ROOT / "results/student-baseline-2026-09-01"

#: r2 layer sizes (inputs/vectors/references/best-available-gt-55maps-r2.geojson,
#: read 2026-09-06: 4,726 student + 278 extension + 14 audit-reviewed) and the
#: census's student-precision observation (results/cluster-audit/adjudication).
#: ``student_records`` counts what the students digitised INCLUDING the five
#: points the census flagged -- those are their false positives, so they
#: belong in the students' output, not in the reference.
INPUTS = {
    "student_records": 4731,
    "student_clustered": 686,
    "student_flagged": 5,
    "extension_mounds_r2": 278,
    "audit_additions": 14,
}

#: Obs 316 / 443: the GS-4 direct measurement (curator reference, 50 m).
GS4_DIRECT = {"precision": 1.000, "recall": 0.9473, "f1": 0.9729,
              "fn_pct": 5.27, "fn_ci_pct": [2.9, 8.8],
              "basis": "4 sheets, curator GT, 50 m (Obs 316/443)"}


def reestimate(draws: int = DRAWS, seed: int = SEED) -> dict:
    """Corpus-level student P / R / F1 with and without the extrapolated terms."""
    rng = np.random.default_rng(seed)
    rd = draw_rates(rng, draws)
    i = INPUTS
    # precision: the flagged share, Beta(k+1, n-k+1) over the clustered sample,
    # applied to every student record
    p_flag = rng.beta(i["student_flagged"] + 1,
                      i["student_clustered"] - i["student_flagged"] + 1, size=draws)
    fp = p_flag * i["student_records"]
    tp = i["student_records"] - fp
    missed_reviewed = i["extension_mounds_r2"] + i["audit_additions"]
    m_unseen = rd["p_dm_empty"] * RATES["p_dm_empty"]["applied_to"]
    om_unseen = rd["p_om"] * RATES["p_om"]["applied_to"]

    def row(fn_extra, label, basis):
        fn = missed_reviewed + fn_extra
        p = tp / (tp + fp)
        r = tp / (tp + fn)
        f = 2 * p * r / (p + r)
        s = lambda x: {"mean": float(np.mean(x)), "ci_lower": float(np.percentile(x, 2.5)),  # noqa: E731
                       "ci_upper": float(np.percentile(x, 97.5))}
        return {"row": label, "basis": basis, "precision": s(p), "recall": s(r), "f1": s(f),
                "expected_student_fp": s(fp), "expected_missed": s(np.broadcast_to(fn, fp.shape))}

    rows = [
        row(m_unseen + om_unseen, "55-map corpus-level (this estimate)",
            "r2 + audit rates, two extrapolated terms"),
        row(0.0, "— without the extrapolated terms",
            "directly reviewed misses only (278 + 14)"),
        {"row": "GS-4 direct (Obs 316/443)", "basis": GS4_DIRECT["basis"],
         "precision": {"mean": GS4_DIRECT["precision"]},
         "recall": {"mean": GS4_DIRECT["recall"], "fn_pct": GS4_DIRECT["fn_pct"],
                    "fn_ci_pct": GS4_DIRECT["fn_ci_pct"]},
         "f1": {"mean": GS4_DIRECT["f1"]}},
    ]
    return {
        "generated_at_utc": datetime.now(UTC).isoformat(),
        "reference": "r2",
        "method": ("Beta(k+1, n-k+1) posteriors (flat prior) on the flagged share and "
                   "the audit rates; Monte Carlo propagation; same machinery as "
                   "scripts/estimated_correction.py"),
        "draws": draws, "seed": seed,
        "inputs": i,
        "extrapolated_terms_point": {
            "unseen_double_misses_M": RATES["p_dm_empty"]["k"] / RATES["p_dm_empty"]["n"]
            * RATES["p_dm_empty"]["applied_to"],
            "model_found_omissions_E_om": RATES["p_om"]["k"] / RATES["p_om"]["n"]
            * RATES["p_om"]["applied_to"],
        },
        "rows": rows,
    }


def render_md(payload: dict) -> str:
    def fmt(m):
        if "ci_lower" in m:
            return f"{m['mean']:.3f} ({m['ci_lower']:.3f}–{m['ci_upper']:.3f})"
        return f"{m['mean']:.3f}"
    i = payload["inputs"]
    t = payload["extrapolated_terms_point"]
    lines = [
        "# The student baseline re-estimated on r2 (55-map corpus level)",
        "",
        f"> **Last revised**: {payload['generated_at_utc'][:10]} (original publication). "
        "Card: `planning/reference-revision-2026-09-06.md` § 2b. Generated by "
        "`scripts/student_baseline_reestimate.py`; inputs printed below.",
        "",
        "| | P | R | F1 | Basis |",
        "|---|---:|---:|---:|---|",
    ]
    for r in payload["rows"]:
        rec = fmt(r["recall"])
        if "fn_pct" in r["recall"]:
            rec += (f" (FN {r['recall']['fn_pct']} %, CI "
                    f"{r['recall']['fn_ci_pct'][0]}–{r['recall']['fn_ci_pct'][1]} %)")
        lines.append(f"| {r['row']} | {fmt(r['precision'])} | {rec} | {fmt(r['f1'])} | {r['basis']} |")
    lines += [
        "",
        "## Inputs",
        "",
        f"- Student records {i['student_records']:,} (the five census-flagged points included: "
        f"they are the students' false positives); clustered {i['student_clustered']}, "
        f"flagged {i['student_flagged']}.",
        f"- Missed by students, reviewed: {i['extension_mounds_r2']} extension mounds (r2) + "
        f"{i['audit_additions']} audit additions.",
        f"- Extrapolated terms at the point rates: unseen double-misses M = "
        f"{t['unseen_double_misses_M']:.1f}; model-found omissions E_om = "
        f"{t['model_found_omissions_E_om']:.1f}.",
        f"- Draws {payload['draws']}, seed {payload['seed']}; flat-prior Beta posteriors.",
        "",
        "Reading: the corpus-level and GS-4 rows estimate different things (a 55-sheet",
        "model-assisted reconstruction versus a 4-sheet direct measurement on a",
        "curated reference); the gap between them is itself a result for D.7.",
    ]
    return "\n".join(lines)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    ap.add_argument("--draws", type=int, default=DRAWS)
    ap.add_argument("--seed", type=int, default=SEED)
    args = ap.parse_args()
    payload = reestimate(args.draws, args.seed)
    args.out_dir.mkdir(parents=True, exist_ok=True)
    (args.out_dir / "reestimate-r2.json").write_text(json.dumps(payload, indent=2) + "\n")
    (args.out_dir / "reestimate-r2.md").write_text(render_md(payload) + "\n")
    for r in payload["rows"]:
        print(f"  {r['row']:40s} P {r['precision']['mean']:.3f}  R {r['recall']['mean']:.3f}  "
              f"F1 {r['f1']['mean']:.3f}")
    print(f"wrote {args.out_dir / 'reestimate-r2.{json,md}'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
