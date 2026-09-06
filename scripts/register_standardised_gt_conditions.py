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

import argparse
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

#: Results home per reference vintage. Kept as a mapping rather than a single
#: module constant so that an r2 run CANNOT reach the r1 tree: the G3
#: regression gate in ``final_board_build.py`` reads r1's evaluation.json files
#: and compares them to the committed board at 1e-9, so overwriting them in
#: place would destroy the very artefacts that prove the mechanism still works
#: (MAJOR 6 of the r2-chain audit, Session 149 — elevated to a pre-step-3
#: blocker). ``adapt_one`` reads AND writes inside one vintage's home only.
OUT_BASE_BY_VINTAGE = {
    "standardised": REPO / "results/55maps-standardised-ref-2026-08-14",
    "r2": REPO / "results/55maps-r2-ref-2026-09-06",
}
#: Retained for callers that import the r1 home by name. New code should take
#: the home from :func:`vintage_home` so the vintage is always explicit.
OUT_BASE = OUT_BASE_BY_VINTAGE["standardised"]
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
#: Reference revision r2 (card ``planning/reference-revision-2026-09-06.md``):
#: the standardised union with the PI's audit adjudications applied (6 records
#: removed, 14 added). r2 ships as ONE merged file and enters the chain that
#: way — the same path the scorer takes (PI ruling, Session 149, adjudicating
#: MAJOR 5), so there is no second construction to keep in step.
R2_GT_REFERENCE = "inputs/vectors/references/best-available-gt-55maps-r2.geojson"
R2_GT_SOURCES = [
    GT_REFERENCE,
    "results/reference-revision-r2/audit-revision-instructions.csv",
]
R2_GT_NOTE = ("scored against reference revision r2 (4,726 student + 278 "
              "extension + 14 audit-reviewed marked centres, included whole "
              "at every R); derived from the standardised reference by the "
              "committed audit instruction set (-6 records, +14)")
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

R2_CROSSREF_NOTE = (
    "Reference-revision-r2 track (PI audit, Session 148-149): the -r2-gt "
    "conditions score the same detection sets against reference revision r2 "
    "(the standardised layers with the cluster- and empty-tile-audit "
    "adjudications applied: -6 records, +14; 5,018 total at marked centres). "
    "They supersede the -standardised-gt cells as the paper reference; see "
    "results/55maps-r2-ref-2026-09-06/ and "
    "planning/reference-revision-2026-09-06.md."
)


#: Per-vintage register facts. ``suffix`` is the condition-label suffix the
#: boards resolve cells by; ``reference`` the loadable single-file path the
#: evaluation records as its ground truth.
VINTAGES: dict[str, dict] = {
    "standardised": {
        "suffix": "-standardised-gt",
        "reference": GT_REFERENCE,
        "sources": GT_SOURCES,
        "note": GT_NOTE,
        "crossref": CROSSREF_NOTE,
    },
    "r2": {
        "suffix": "-r2-gt",
        "reference": R2_GT_REFERENCE,
        "sources": R2_GT_SOURCES,
        "note": R2_GT_NOTE,
        "crossref": R2_CROSSREF_NOTE,
    },
}


def vintage_home(vintage: str) -> Path:
    """The results home for one reference vintage.

    Args:
        vintage: ``standardised`` (r1) or ``r2``.

    Returns:
        The directory holding that vintage's per-cell scoring artefacts.

    Raises:
        KeyError: On an unknown vintage — better than defaulting to r1 and
            overwriting it.
    """
    return OUT_BASE_BY_VINTAGE[vintage]


def registration_for(cell_label: str, vintage: str) -> tuple[str, str, str]:
    """Resolve (run, label to clone, new label) for one cell and vintage.

    Every vintage clones the SAME ``-canonical-gt`` base spec rather than
    chaining off the previous vintage, so a defect in one vintage's row cannot
    propagate into the next.

    Args:
        cell_label: Board cell, e.g. ``TH7-k4``.
        vintage: ``standardised`` or ``r2``.

    Returns:
        The run family, the canonical label to clone, and the new label.
    """
    run, src_label, std_label = REGISTRATIONS[cell_label]
    if vintage == "standardised":
        return run, src_label, std_label
    return run, src_label, src_label.replace("-canonical-gt",
                                             VINTAGES[vintage]["suffix"])


def adapt_one(label: str, det_rel: str, vintage: str = "standardised") -> Path:
    """Transform one cell's scored summary.json into evaluation.json.

    Args:
        label: Board cell label, e.g. ``TH7-k4``.
        det_rel: Repo-relative path to the cell's detections GeoJSON.
        vintage: Reference vintage — ``standardised`` (r1, default: unchanged
            behaviour) or ``r2``. Reads and writes inside that vintage's home
            ONLY, so an r2 run cannot touch the r1 artefacts the G3 regression
            gate reads.

    Returns:
        Path to the written ``evaluation.json``.
    """
    v = VINTAGES[vintage]
    cell_dir = vintage_home(vintage) / label
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
            "gt_reference": v["reference"],
            "metric": (
                f"corrected-F1 @ R (extended-GT Hungarian, {vintage} "
                f"reference), tile-MCC on the SAME reference"
            ),
            "tile_classification_buffer_metres": HEADLINE_BUFFER,
            "tile_classification_note": (
                f"Under the {vintage} reference the extended GT is "
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
                "ground_truth": v["reference"],
                "ground_truth_sources": v["sources"],
                "ground_truth_note": v["note"],
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


def register_one(dec: dict, cell_label: str,
                 vintage: str = "standardised") -> str:
    """Clone the run's -canonical-gt spec into one for the given vintage.

    Args:
        dec: The ``decomposition`` block of run-conditions.json, mutated in
            place.
        cell_label: Board cell label, e.g. ``TH7-k4``.
        vintage: ``standardised`` (default) or ``r2``.

    Returns:
        A one-line status string (registered, or skipped as already present).
    """
    v = VINTAGES[vintage]
    run, src_label, new_label = registration_for(cell_label, vintage)
    run_spec = dec[run]
    conds = run_spec["conditions"]
    if any(c.get("label") == new_label for c in conds):
        return f"  {run}::{new_label} already present — skipped"
    src = next(c for c in conds if c.get("label") == src_label)
    new = json.loads(json.dumps(src))  # deep copy
    new["label"] = new_label
    new["eval_path"] = str(
        (vintage_home(vintage) / cell_label / "evaluation.json")
        .relative_to(REPO)
    )
    new["_note"] = f"{cell_label} {v['note']}"
    conds.append(new)
    note = run_spec.get("_note", "")
    # The crossref is appended once per run per vintage; its opening phrase is
    # the idempotency key, so re-running never duplicates it.
    key = v["crossref"].split(":")[0]
    if key not in note:
        run_spec["_note"] = (note + " " + v["crossref"]).strip()
    return f"  {run}::{new_label} registered"


def main(vintage: str = "standardised") -> None:
    """Adapt every cell's summary, then register its condition row.

    Args:
        vintage: ``standardised`` (r1, default) or ``r2``.

    Raises:
        SystemExit: If the vintage's home does not exist. For r2 that means
            step 3 has not been run: this script ADAPTS scored summaries, it
            does not score, so an absent home would otherwise surface as a
            confusing per-cell FileNotFoundError.
    """
    home = vintage_home(vintage)
    if not home.is_dir():
        sys.exit(
            f"{vintage} home {home.relative_to(REPO)} does not exist — "
            f"score the cells into it first (step 3 precedes step 7a)."
        )
    print(f"Adapting {vintage} summaries to generator shape "
          f"({home.relative_to(REPO)})...")
    for cell in CELLS:
        p = adapt_one(cell["label"], cell["det"], vintage)
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
        print(register_one(rc["decomposition"], cell["label"], vintage))
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
    _ap = argparse.ArgumentParser(description=__doc__)
    _ap.add_argument(
        "--reference",
        choices=sorted(VINTAGES),
        default="standardised",
        help="Reference vintage to adapt and register: standardised (r1, "
             "default — unchanged behaviour) or r2 (the 2026-09 audit "
             "revision; reads and writes results/55maps-r2-ref-2026-09-06/ "
             "and registers -r2-gt rows). Step 7a: run this BEFORE the "
             "boards, which resolve cells by registered label.",
    )
    main(_ap.parse_args().reference)
