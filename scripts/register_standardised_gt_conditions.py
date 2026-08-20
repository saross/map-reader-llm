#!/usr/bin/env python3
"""Register the eight standardised-reference cells in the conditions manifest.

Session 132, queue items 2–3 (reference-standardisation-queue.md):
mirrors the Session-105 canonical-GT registration flow
(``adapt_track2_evals_for_manifest.py`` + ``add_canonical_gt_conditions.py``)
in one idempotent script:

1. **Adapt** each cell's standardised-scoring ``summary.json``
   (``results/55maps-standardised-ref-2026-08-14/<cell>/``) into a
   generator-compatible ``evaluation.json`` — ``summary.buffers[]`` from
   every corrected-F1 row, a single buffer-agnostic
   ``tile_classification`` block (exactly right here: under the
   standardised reference the extended GT is identical at every R, so
   tile MCC is buffer-invariant by construction, not a 50 m pin), and
   ``n_detections`` recounted from the detection GeoJSON.
2. **Register** one ``-standardised-gt`` condition per cell in
   ``results/run-conditions.json``, cloned from the run's existing
   ``-canonical-gt`` spec (same architecture/aggregation/verifier
   provenance — only the reference changed) with the new ``eval_path``
   and note. Idempotent: existing labels are skipped.

Afterwards regenerate the manifest and drift-check::

    python scripts/generate_post_run_report.py --all
    python scripts/generate_post_run_report.py --drift-check

Pure deterministic transform; NO API, NO recompute.

Usage::

    python scripts/register_standardised_gt_conditions.py

Author: Shawn Ross, Claude Code
Licence: Apache 2.0
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))
from score_55maps_standardised_reference import (  # noqa: E402
    BOUNDS,
    BUFFERS,
    CELLS,
    REPO,
)

OUT_BASE = REPO / "results/55maps-standardised-ref-2026-08-14"
RUN_CONDITIONS = REPO / "results/run-conditions.json"
BOUNDS_REL = str(BOUNDS.relative_to(REPO))
HEADLINE_BUFFER = 50  # the 55-map deployment headline (Obs 260)

# Rendered wherever a tile-level metric is not computable
# (erratum E81). Matches ``evaluate_detections.UNDEFINED_DISPLAY``.
UNDEFINED_DISPLAY = "undefined"
# The reference the cells were scored against, recorded as a LOADABLE path
# (defect D33: the previous prose sentence here made 8 register conditions
# unreproducible from their own metadata). The merged single-file reference is
# buffer-invariant and reproduces every cell exactly (E83 re-tiering gate,
# gap 0.0000); the two source layers it merges are kept alongside.
GT_REFERENCE = "inputs/vectors/references/best-available-gt-55maps.geojson"
GT_SOURCES = [
    "results/deployment-oracle-2026-06-06/canonical-gt/standardised/"
    "student-mounds-55maps-standardised.geojson",
    "results/deployment-oracle-2026-06-06/canonical-gt/standardised/"
    "extension-mounds-standardised.csv",
]
GT_NOTE = ("scored against the two standardised layers (4,731 student + 279 "
           "extension marked centres, included whole at every R — ruling 21); "
           "the merged best-available reference reproduces every cell")

# cell label → (run family, canonical label to clone, new label)
REGISTRATIONS = {
    "TH7-k4": ("55maps-text-high-generalisation",
               "verified-k4-canonical-gt", "verified-k4-standardised-gt"),
    "TH7-k3": ("55maps-text-high-generalisation",
               "verified-k3-canonical-gt", "verified-k3-standardised-gt"),
    "T03-k4": ("55maps-text-high-t0-3-generalisation",
               "verified-k4-canonical-gt", "verified-k4-standardised-gt"),
    "T03-k3": ("55maps-text-high-t0-3-generalisation",
               "verified-k3-canonical-gt", "verified-k3-standardised-gt"),
    "TM-k4": ("55maps-text-min-generalisation",
              "verified-k4-canonical-gt", "verified-k4-standardised-gt"),
    "TM-k3": ("55maps-text-min-generalisation",
              "verified-k3-canonical-gt", "verified-k3-standardised-gt"),
    "IM-k3": ("55maps-image-generalisation",
              "verified-k3-canonical-gt", "verified-k3-standardised-gt"),
    "TM-n10-k5": ("55maps-text-min-n10-uplift",
                  "verified-5of10-canonical-gt",
                  "verified-5of10-standardised-gt"),
}

CROSSREF_NOTE = (
    "Standardised-reference track (ruling 21, Session 132): the "
    "-standardised-gt conditions score the same detection sets against "
    "canonical-gt/standardised/ (student 4,731 + extension 279 at marked "
    "centres, no ring gate). They supersede the -canonical-gt cells as "
    "the paper reference; see "
    "results/55maps-standardised-ref-2026-08-14/."
)


def adapt_one(label: str, det_rel: str) -> Path:
    """Transform one cell's standardised summary.json into evaluation.json."""
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

    with open(REPO / det_rel, encoding="utf-8") as fh:
        n_detections = len(json.load(fh)["features"])

    out = {
        "_metadata": {
            "adapter": "scripts/register_standardised_gt_conditions.py",
            "source_summary": str(
                (cell_dir / "summary.json").relative_to(REPO)
            ),
            "gt_reference": GT_REFERENCE,
            "metric": (
                "corrected-F1 @ R (extended-GT Hungarian, standardised "
                "reference), tile-MCC on the SAME reference"
            ),
            "tile_classification_buffer_metres": HEADLINE_BUFFER,
            "tile_classification_note": (
                "Under the standardised reference the extended GT is "
                "identical at every R (marked centres, no ring gate), so "
                "tile MCC is buffer-invariant by construction — the "
                "single block is exact at every buffer, not a 50 m pin."
            ),
            "buffers": list(BUFFERS),
            # The bootstrap parameters the source summary actually recorded.
            # These cells have always run at 10,000 iterations, but they wrote
            # the count as `metadata.bootstrap_n` in summary.json, which the
            # manifest extractor does not read, so the register could not see
            # it and D17's fix correctly omitted the field. Restating it here in
            # the shape every other evaluation uses closes that gap without a
            # re-run: nothing is recomputed, a true value is simply declared
            # where the register can find it.
            "bootstrap": {
                "n_iterations": summary["metadata"]["bootstrap_n"],
                "seed": summary["metadata"].get("seed"),
                "resampling_unit": "tile_level",
                "method": "percentile",
                "source": "metadata.bootstrap_n of the source summary.json",
            },
            "input_files": {
                "detections": [det_rel],
                "bounds": BOUNDS_REL,
                "ground_truth": GT_REFERENCE,
                "ground_truth_sources": GT_SOURCES,
                "ground_truth_note": GT_NOTE,
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


def register_one(dec: dict, cell_label: str) -> str:
    """Clone the run's -canonical-gt spec into a -standardised-gt one."""
    run, src_label, new_label = REGISTRATIONS[cell_label]
    run_spec = dec[run]
    conds = run_spec["conditions"]
    if any(c.get("label") == new_label for c in conds):
        return f"  {run}::{new_label} already present — skipped"
    src = next(c for c in conds if c.get("label") == src_label)
    new = json.loads(json.dumps(src))  # deep copy
    new["label"] = new_label
    new["eval_path"] = str(
        (OUT_BASE / cell_label / "evaluation.json").relative_to(REPO)
    )
    new["_note"] = (
        f"{cell_label} vs the ruling-21 standardised reference "
        "(student 4,731 + extension 279 at marked centres; F1 and tile "
        "MCC share the reference — queue items 2-3, Session 132)"
    )
    conds.append(new)
    note = run_spec.get("_note", "")
    if "Standardised-reference track" not in note:
        run_spec["_note"] = (note + " " + CROSSREF_NOTE).strip()
    return f"  {run}::{new_label} registered"


def main() -> None:
    """Adapt all 8 cells, then register their conditions."""
    print("Adapting standardised summaries to generator shape...")
    for cell in CELLS:
        p = adapt_one(cell["label"], cell["det"])
        s = json.loads(p.read_text())["summary"]
        b50 = next(
            b for b in s["buffers"] if b["buffer_metres"] == HEADLINE_BUFFER
        )
        # Erratum E81: the tile MCC is ``None`` when the 2 x 2 tile
        # confusion matrix is degenerate. Print the word rather than a
        # number — "0.0000" here would read as a chance-level result.
        mcc = s["tile_classification"]["mcc"]
        mcc_str = UNDEFINED_DISPLAY if mcc is None else f"{mcc:.4f}"
        print(
            f"  {cell['label']:10s} → {p.relative_to(REPO)}  "
            f"n_det={s['n_detections']}  F1@50={b50['f1']:.4f}  "
            f"MCC={mcc_str}"
        )

    print("Registering conditions...")
    rc = json.loads(RUN_CONDITIONS.read_text())
    for cell in CELLS:
        print(register_one(rc["decomposition"], cell["label"]))
    # Match the file's canonical serialisation (indent=1, non-ASCII kept) so the
    # diff is only the added conditions. The trailing newline is PRESERVED from
    # what is on disk rather than assumed: this comment used to assert there was
    # none, the file has since gained one, and the round-trip guard in
    # tests/test_author_e43_matched_temperature.py detects the trailing sequence
    # adaptively, so it cannot catch the assumption going stale.
    _existing = RUN_CONDITIONS.read_text()
    _trailing = "\n" if _existing.endswith("\n") else ""
    RUN_CONDITIONS.write_text(
        json.dumps(rc, indent=1, ensure_ascii=False) + _trailing
    )
    print(f"Wrote {RUN_CONDITIONS.relative_to(REPO)}")


if __name__ == "__main__":
    main()
