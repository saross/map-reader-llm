#!/usr/bin/env python3
"""
Registration Pass 1: adapt the four stride-55map engine evals.

The S105 adapter pattern (`adapt_track2_evals_for_manifest.py`),
applied to the Pass-1 conditions: rewrite each corrected-F1
`summary.json` (primary and oracle, Runs A and B) into the
generator-shape `evaluation.json` beside it — no recomputation, pure
deterministic transform. Headline tile-classification pinned to the
50 m deployment row, CI method recorded as percentile, CI flags
measured-exclusion-only — all exactly as the S105 adapter documents.

Also repoints the four conditions' `eval_path` in
`results/run-conditions.json` at the adapted files.

Usage::

    python scripts/register_pass1_adapt.py

Created: 2026-08-28 (Session 143)
Author: Shawn Ross, Claude Code
Licence: Apache 2.0
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
BASE = REPO / "results/stride55-2026-08-27"
HEADLINE_BUFFER = 50


def _rel(path: str | Path | None) -> str | None:
    """Repo-relative form of a recorded path (absolute scoring-host paths included)."""
    if not path:
        return None
    s = str(path)
    return s.split("map-reader-llm/", 1)[1] if "map-reader-llm/" in s else s


def _input_files(summary: dict, det: Path) -> dict:
    """The engine's recorded inputs, repo-relative, from ``metadata.input_paths``."""
    paths = (summary.get("metadata") or {}).get("input_paths") or {}
    return {
        "detections": [str(det.relative_to(REPO))],
        "engine_detections": _rel(paths.get("detections")),
        "ground_truth": _rel(paths.get("student_gt")),
        "review_today": _rel(paths.get("review_today")),
        "review_yesterday": _rel(paths.get("review_yesterday")),
        "bounds": _rel(paths.get("bounds")),
    }


def adapt(eval_dir: Path, det: Path) -> None:
    summary = json.loads((eval_dir / "summary.json").read_text())
    buffers = []
    headline_tc = None
    for row in summary["results"]:
        excludes = not (row["F1_CI"][0] <= row["F1"] <= row["F1_CI"][1])
        buffers.append({
            "buffer_metres": row["R_m"], "f1": row["F1"],
            "precision": row["precision"], "recall": row["recall"],
            "f1_ci_lower": row["F1_CI"][0],
            "f1_ci_upper": row["F1_CI"][1],
            "f1_ci_method": "percentile",
            "ci_unreliable": excludes,
            "ci_excludes_point": excludes,
            "ci_flag_basis": "measured-exclusion-only",
        })
        if row["R_m"] == HEADLINE_BUFFER:
            tc = row.get("tile_classification", {})
            headline_tc = {
                "mcc": tc.get("mcc"),
                "sensitivity": tc.get("sensitivity"),
                "specificity": tc.get("specificity"),
                "confusion": {"tp": tc.get("tp"), "tn": tc.get("tn"),
                              "fp": tc.get("fp"), "fn": tc.get("fn")},
            }
    n_det = len(json.loads(det.read_text())["features"])
    out = {
        "summary": {"buffers": buffers,
                    "tile_classification": headline_tc,
                    "n_detections": n_det},
        "_metadata": {
            "adapted_by": "scripts/register_pass1_adapt.py",
            "source": _rel(eval_dir / "summary.json"),
            # The inputs the Track-2 engine actually scored, carried through
            # so the register verifier can cross-check eval <-> detections and
            # scope (Session 149-c: the four stride canonical rows had no
            # provenance at all and read as wrong-source ERRORs).
            "script_path": "scripts/compute_corrected_f1_multi_buffer.py",
            "input_files": _input_files(summary, det),
            "note": ("Deterministic transform of the corrected-F1 engine "
                     "summary (S105 adapter pattern); tile_classification "
                     "pinned to the 50 m headline row; nothing "
                     "recomputed."),
        },
    }
    (eval_dir / "evaluation.json").write_text(
        json.dumps(out, indent=1) + "\n")
    b50 = next(b for b in buffers if b["buffer_metres"] == 50)
    print(f"  {_rel(eval_dir)}: F1@50 {b50['f1']:.6f} "
          f"n={n_det} tc={'ok' if headline_tc and headline_tc['confusion']['tp'] is not None else 'MISSING'}")


def main() -> int:
    for cell in ("g384_ov128_55map", "g384_ov192_55map"):
        for kind in ("primary", "oracle"):
            adapt(BASE / cell / kind / "eval",
                  BASE / cell / kind / "verified_detections.geojson")
    rc_path = REPO / "results/run-conditions.json"
    rc = json.loads(rc_path.read_text())
    n = 0
    for c in rc["decomposition"]["stride-55map-2026-08-25"]["conditions"]:
        old = c["eval_path"]
        if old.endswith("summary.json"):
            c["eval_path"] = old.replace("summary.json", "evaluation.json")
            n += 1
    rc_path.write_text(json.dumps(rc, indent=1) + "\n")
    print(f"run-conditions: {n} eval_paths repointed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
