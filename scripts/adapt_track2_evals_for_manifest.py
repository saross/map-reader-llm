#!/usr/bin/env python3
"""
Adapt the Track-2 canonical-GT ``summary.json`` files into generator-compatible
``evaluation.json`` files for manifest registration (Session 105).
===========================================================================

The conditions-manifest generator (``generate_post_run_report.py``,
``_metrics_from_eval``) lifts metrics from each condition's ``eval_path`` assuming
the standard ``evaluation.json`` shape:

* ``summary.buffers[]`` — each with ``buffer_metres``, ``f1``, ``precision``,
  ``recall``, ``f1_ci_lower``/``f1_ci_upper``, ``f1_ci_method``, ``ci_unreliable``;
* ``summary.tile_classification`` — ``mcc``/``sensitivity``/``specificity`` plus a
  nested ``confusion.{tp,tn,fp,fn}`` (a SINGLE, buffer-agnostic block);
* ``summary.n_detections`` — the scored detection count.

The Track-2 driver emits a different schema
(``compute_corrected_f1_multi_buffer``: ``results[]`` with ``R_m``/``F1``/
``F1_CI`` and a per-buffer ``tile_classification``). This adapter rewrites each
cell's ``summary.json`` into the generator shape **without recomputing anything**:

* ``buffers[]`` ← every ``results[]`` row (corrected-F1, all 14 buffers);
* ``tile_classification`` ← the **50 m headline** row's MCC block (the manifest
  slot is buffer-agnostic; Track-2 MCC varies with R via the gated GT, so we pin
  the reported MCC to the 50 m deployment headline — the full per-buffer MCC
  lives in the Track-2 ``summary.json`` / ``consolidated-track2.csv``);
* ``n_detections`` ← the cell's verified detection geojson feature count.

The CI method is recorded as ``percentile`` (the corrected-F1 bootstrap uses
percentile CIs, not BCa) so the manifest does not mislabel it.

Pure deterministic transform; NO API, NO recompute.

Usage::

    python scripts/adapt_track2_evals_for_manifest.py
    # writes results/55maps-extended-gt-2026-06-07/<cell>/evaluation.json

Author: Shawn Ross, Claude Code
Licence: Apache 2.0
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import geopandas as gpd

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))
from score_55maps_extended_gt_canonical import (  # noqa: E402
    BOUNDS,
    BUFFERS,
    CELLS,
    REPO,
)

OUT_BASE = REPO / "results/55maps-extended-gt-2026-06-07"

#: Cells scored into this directory that are NOT members of the shared
#: seven-cell ``CELLS`` list. The Session-113 uplift arm was added after that
#: list was fixed, and adding it there would change the seven-cell leaderboards,
#: so it is carried here instead. Without this entry the adapter silently skips
#: the cell, which is how it came to be the one condition in the register with
#: no declared bootstrap count (D17).
EXTRA_CELLS: list[dict] = [
    {
        "label": "TM-n10-k5",
        "det": "results/55map-leaderboard/min11-uplift-5of10-pt0.15.geojson",
    },
]
BOUNDS_REL = str(BOUNDS.relative_to(REPO))
HEADLINE_BUFFER = 50  # the 55-map deployment headline (jitter-matched, Obs 260)

# Rendered wherever a tile-level metric is not computable
# (erratum E81). Matches ``evaluate_detections.UNDEFINED_DISPLAY``.
UNDEFINED_DISPLAY = "undefined"
GT_REFERENCE = (
    "results/deployment-oracle-2026-06-06/canonical-gt/canonical-review.csv "
    "(773 phantoms, per-buffer gated) + "
    "inputs/vectors/references/student-mounds-55maps-reviewed.geojson (4,746)"
)


def adapt_one(label: str, det_rel: str) -> Path:
    """Transform one cell's Track-2 summary.json into an evaluation.json."""
    cell_dir = OUT_BASE / label
    summary = json.loads((cell_dir / "summary.json").read_text())

    buffers = []
    headline_tc: dict | None = None
    for row in summary["results"]:
        r = row["R_m"]
        excludes = not (row["F1_CI"][0] <= row["F1"] <= row["F1_CI"][1])
        buffers.append({
            "buffer_metres": r,
            "f1": row["F1"],
            "precision": row["precision"],
            "recall": row["recall"],
            "f1_ci_lower": row["F1_CI"][0],
            "f1_ci_upper": row["F1_CI"][1],
            "f1_ci_method": "percentile",
            # MEASURED, not asserted (defect D37/D28): the flag is the
            # exclusion test on the one CI this adapter carries. Coverage is
            # not evaluable from the Track-2 summary, so the basis says so.
            "ci_unreliable": excludes,
            "ci_excludes_point": excludes,
            "ci_flag_basis": "measured-exclusion-only",
        })
        if r == HEADLINE_BUFFER:
            tc = row.get("tile_classification", {})
            headline_tc = {
                "mcc": tc.get("mcc"),
                "sensitivity": tc.get("sensitivity"),
                "specificity": tc.get("specificity"),
                "confusion": {
                    "tp": tc.get("tp"), "tn": tc.get("tn"),
                    "fp": tc.get("fp"), "fn": tc.get("fn"),
                },
            }
    if headline_tc is None:
        raise ValueError(f"{label}: no {HEADLINE_BUFFER} m row in summary.json")

    n_detections = int(len(gpd.read_file(REPO / det_rel)))

    out = {
        "_metadata": {
            "adapter": "scripts/adapt_track2_evals_for_manifest.py",
            "source_summary": f"results/55maps-extended-gt-2026-06-07/{label}/summary.json",
            "gt_reference": GT_REFERENCE,
            "metric": "corrected-F1 @ R (extended-GT-at-R Hungarian), tile-MCC",
            "tile_classification_buffer_metres": HEADLINE_BUFFER,
            "tile_classification_note": (
                "MCC is reported at the 50 m deployment headline; it varies with R "
                "via the per-buffer gated extended GT — see the Track-2 summary.json "
                "/ consolidated-track2.csv for the full per-buffer MCC."
            ),
            "buffers": list(BUFFERS),
            # The bootstrap parameters the source summary actually recorded.
            # These cells have always run at 10,000 iterations, but they wrote
            # the count as `metadata.bootstrap_n` in summary.json, which the
            # manifest extractor does not read, so the register could not see it
            # and D17's fix correctly omitted the field. Restating it here in the
            # shape every other evaluation uses closes that gap without a re-run:
            # nothing is recomputed, a true value is declared where the register
            # can find it.
            "bootstrap": {
                "n_iterations": summary["metadata"]["bootstrap_n"],
                "seed": summary["metadata"].get("seed"),
                "resampling_unit": "tile_level",
                "method": "percentile",
                "source": "metadata.bootstrap_n of the source summary.json",
            },
            # input_files are what scripts/verify_run_conditions.py reads to confirm
            # the eval scored this condition's detections and on the right scope.
            "input_files": {
                "detections": [det_rel],
                "bounds": BOUNDS_REL,
                "ground_truth": GT_REFERENCE,
            },
        },
        "summary": {
            "n_detections": n_detections,
            "buffers": buffers,
            "tile_classification": headline_tc,
        },
    }
    out_path = cell_dir / "evaluation.json"
    out_path.write_text(json.dumps(out, indent=2))
    return out_path


def main() -> None:
    """Adapt all 7 Track-2 cells."""
    for cell in CELLS + EXTRA_CELLS:
        p = adapt_one(cell["label"], cell["det"])
        s = json.loads(p.read_text())["summary"]
        b50 = next(b for b in s["buffers"] if b["buffer_metres"] == HEADLINE_BUFFER)
        # Erratum E81: the tile MCC is ``None`` when the 2 x 2 tile
        # confusion matrix is degenerate. Print the word rather than a
        # number — "0.0000" here would read as a chance-level result.
        mcc = s["tile_classification"]["mcc"]
        mcc_str = UNDEFINED_DISPLAY if mcc is None else f"{mcc:.4f}"
        print(
            f"  {cell['label']:8s} → {p.relative_to(REPO)}  "
            f"n_det={s['n_detections']}  F1@50={b50['f1']:.4f}  MCC@50={mcc_str}"
        )


if __name__ == "__main__":
    main()
