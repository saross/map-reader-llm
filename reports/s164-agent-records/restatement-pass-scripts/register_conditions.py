#!/usr/bin/env python3
"""
Point the 3.7 image carried arm's register rows at its registered set (D65 (3)).

Part of the S164 restatement pass (``reports/s164-agent-records/
restatement-pass.md`` § 1.1, decision 1). With the D62 (1) re-verified rows
the arm's sweep argmax moved from its registered (0.10, k5) to (0.05, k5), so
``image_b_analysis.py`` writes ``verified_best_20m.geojson`` at (0.05, k5)
and, with ``--operating-point 0.10,5``, the registered set as
``verified_op_20m.geojson``; ``gs_conditions.py`` scores it into
``op-eval/``. PI ruling D65 (3) keeps a registered (carried) condition at its
registered point, so its two register rows are re-pointed:

- ``gemini37-image-gs-2026-09-01::g37-image-k5-verified-carried-p0.10-k5``:
  ``detections`` → ``arm1/verified_op_20m.geojson``, ``eval_path`` →
  ``arm1/op-eval/evaluation.json``;
- its Era-2 board copy ``…-era2b``: ``detections`` →
  ``arm1/verified_op_20m.geojson`` (its ``eval_path`` stays the board-frame
  cell, which the board lane re-scores on that set).

Each row's ``_note`` gains a dated sentence. Nothing else in the file
changes; the file keeps its serialisation (indent 1, ASCII-escaped).

Usage: python register_conditions.py <repo_root>

Author: Shawn Ross, Claude Code (S164). Licence: Apache 2.0
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(sys.argv[1]).resolve()
PATH = ROOT / "results/run-conditions.json"
RUN = "gemini37-image-gs-2026-09-01"
ARM1 = "results/gemini37-image-gs-2026-09-01/arm1"
NOTE = (" [RESTATED 2026-10-15, S164 restatement pass (reports/s164-agent-records/"
        "restatement-pass.md): with the D62 (1) re-verified rows this arm's sweep argmax "
        "moved from its registered (0.10, k5) to (0.05, k5); under PI ruling D65 (3) the "
        "condition keeps its registered point, so it now reads the registered set "
        "arm1/verified_op_20m.geojson (written by image_b_analysis.py --operating-point "
        "0.10,5; F1@20 0.9353, 438 detections), not the argmax set verified_best_20m.geojson.]")

text = PATH.read_text()
doc = json.loads(text)
rows = {c["label"]: c for c in doc["decomposition"][RUN]["conditions"]}
main = rows["g37-image-k5-verified-carried-p0.10-k5"]
board = rows["g37-image-k5-verified-carried-p0.10-k5-era2b"]
assert main["detections"] == f"{ARM1}/verified_best_20m.geojson", main["detections"]
assert main["eval_path"] == f"{ARM1}/best-eval/evaluation.json", main["eval_path"]
assert board["detections"] == f"{ARM1}/verified_best_20m.geojson", board["detections"]
for row in (main, board):
    assert (row["prob_threshold"], row["vote_threshold"]) == (0.1, 5)
    row["detections"] = f"{ARM1}/verified_op_20m.geojson"
    row["_note"] = (row.get("_note") or "") + NOTE
main["eval_path"] = f"{ARM1}/op-eval/evaluation.json"
out = json.dumps(doc, indent=1, ensure_ascii=True) + ("\n" if text.endswith("\n") else "")
PATH.write_text(out)
print("re-pointed:", main["label"], "and", board["label"])
