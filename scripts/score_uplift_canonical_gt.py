#!/usr/bin/env python3
# ============================================================================
# score_uplift_canonical_gt.py
# ----------------------------------------------------------------------------
# Session 113 ($0): full Track-2 canonical-GT evaluation of the min11 uplift
# cell (Run B: 10 minimal T0.7 proposer passes + carry-forward n=1 verifier,
# best op 5of10/pt0.15) so it can join the 55-map canonical board and the
# manifest with the same artefact shape as the seven S105 cells.
#
# Shells the SAME trusted engine the S105 driver used
# (compute_corrected_f1_multi_buffer.run via score_55maps_extended_gt_
# canonical, full 14 buffers, n_bootstrap 10,000, seed 42, --compute-mcc),
# writing results/55maps-extended-gt-2026-06-07/TM-n10-k5/, then adapts the
# summary into the generator-compatible evaluation.json with the SAME adapter
# (adapt_track2_evals_for_manifest.adapt_one).
#
# VALIDATION GATE: the engine's corrected-F1 @ 50 m must reproduce the
# committed sweep value (results/55map-leaderboard/min11_uplift_cell.json,
# scored by score_min11_uplift.py with the board's canonical_gt_at machinery)
# within 0.003 — the same mechanism-equivalence tolerance the 55-map board
# build applies. A FAIL aborts before the adapter writes anything.
#
# Compute: sapphire (8,541-tile Hungarian x 14 buffers x 10k bootstrap).
#
# Usage (sapphire):  .venv/bin/python scripts/score_uplift_canonical_gt.py
#
# Author: Shawn Ross & Claude (Anthropic) | Created: 2026-06-11 | Apache 2.0
# ============================================================================
from __future__ import annotations

import json
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))
from adapt_track2_evals_for_manifest import adapt_one  # noqa: E402
from score_55maps_extended_gt_canonical import (  # noqa: E402
    BUFFERS,
    REPO,
    ensure_empty_yesterday,
    score_one_cell,
)

LABEL = "TM-n10-k5"
DET_REL = "results/55map-leaderboard/min11-uplift-5of10-pt0.15.geojson"
OUT_BASE = REPO / "results/55maps-extended-gt-2026-06-07"
CELL_RECORD = REPO / "results/55map-leaderboard/min11_uplift_cell.json"
GATE_TOL = 0.003  # the 55-map board's mechanism-equivalence tolerance


def main() -> int:
    """Score, gate against the committed sweep value, then adapt."""
    record = json.loads(CELL_RECORD.read_text())
    # The unrounded committed value (the rounded f1_50 is 0.829).
    expect_f1 = record["permutations"]["TM-k3"]["f1_a"]
    out_dir = OUT_BASE / LABEL
    review_yesterday = ensure_empty_yesterday(OUT_BASE)

    print(f"=== Track-2 engine: {LABEL} ({DET_REL}) ===", flush=True)
    score_one_cell(
        label=LABEL,
        det_path=REPO / DET_REL,
        review_yesterday=review_yesterday,
        output_dir=out_dir,
        buffers=list(BUFFERS),
        n_bootstrap=10_000,
        seed=42,
    )

    summary = json.loads((out_dir / "summary.json").read_text())
    f1_50 = next(r["F1"] for r in summary["results"] if r["R_m"] == 50)
    delta = abs(f1_50 - expect_f1)
    if delta > GATE_TOL:
        sys.exit(f"GATE FAIL: engine corrected-F1@50 {f1_50:.6f} vs committed "
                 f"sweep {expect_f1:.6f} (|delta| {delta:.6f} > {GATE_TOL})")
    print(f"gate ok: corrected-F1@50 {f1_50:.6f} vs committed {expect_f1:.6f} "
          f"(|delta| {delta:.6f})", flush=True)

    ev_path = adapt_one(LABEL, DET_REL)
    s = json.loads(ev_path.read_text())["summary"]
    b50 = next(b for b in s["buffers"] if b["buffer_metres"] == 50)
    print(f"adapted: {ev_path.relative_to(REPO)}  n_det={s['n_detections']}  "
          f"F1@50={b50['f1']:.4f}  MCC@50={s['tile_classification']['mcc']:.4f}",
          flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
