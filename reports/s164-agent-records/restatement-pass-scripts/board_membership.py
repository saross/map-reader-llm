#!/usr/bin/env python3
"""
Refresh the Era-2 board's membership snapshot for the restatement pass.

Part of the S164 restatement pass (``reports/s164-agent-records/
restatement-pass.md`` § 1.3). The board's ``membership.json`` is written by
``build_gs_era2_board.py membership`` from the register as it stood on
2026-09-14. Re-deriving it today changes the membership itself (the derivation
rule now reads later register edits: 98 members instead of 110, and new
``track_basis`` routes), which is a board change this pass does not make. So
the membership is kept and only two kinds of field are refreshed, each
recorded in a top-level ``_restated`` block:

- every member's ``committed_f1_20``, re-read with the builder's own
  ``f1_at`` from the member's ``eval_path`` as it stands now (the restated
  GS evaluations and the S9 K-ladder cells);
- the 3.7 image carried arm's ``detections`` and ``eval_path``, from its
  register row, which PI ruling D65 (3) re-pointed to the registered set
  (``register_conditions.py``).

The file keeps its serialisation (indent 1, newline at end). The listing
``membership.txt`` is re-rendered with the builder's ``render_listing``.

Usage: python board_membership.py <repo_root>

Author: Shawn Ross, Claude Code (S164). Licence: Apache 2.0
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(sys.argv[1]).resolve()
sys.path.insert(0, str(ROOT))

from scripts import build_gs_era2_board as bb  # noqa: E402

assert bb.REPO_ROOT == ROOT, (bb.REPO_ROOT, ROOT)
BOARD = ROOT / bb.BOARD_DIR
PATH = BOARD / "membership.json"
ARM1 = "gemini37-image-gs-2026-09-01::g37-image-k5-verified-carried-p0.10-k5"

text = PATH.read_text(encoding="utf-8")
doc = json.loads(text)
register = json.loads((ROOT / "results/run-conditions.json").read_text())["decomposition"]
changed: list[dict] = []
for m in doc["members"]:
    if m["condition_id"] == ARM1:
        run, label = ARM1.split("::")
        row = next(c for c in register[run]["conditions"] if c["label"] == label)
        for field in ("detections", "eval_path"):
            if m[field] != row[field]:
                changed.append({"condition_id": m["condition_id"], "field": field,
                                "old": m[field], "new": row[field]})
                m[field] = row[field]
    new_f1 = bb.f1_at(bb._eval_meta(m["eval_path"]))
    if new_f1 != m.get("committed_f1_20"):
        changed.append({"condition_id": m["condition_id"], "field": "committed_f1_20",
                        "old": m.get("committed_f1_20"), "new": new_f1})
        m["committed_f1_20"] = new_f1
doc["_restated"] = {
    "date": "2026-10-15",
    "by": ("S164 restatement pass (reports/s164-agent-records/restatement-pass.md "
           "§ 1.3; driver restatement-pass-scripts/board_membership.py)"),
    "what": ("membership kept as derived on derived_at_utc; committed_f1_20 re-read from "
             "each member's eval_path after the D62 (1) re-verified rows and the S9 "
             "K-ladder re-scores; the 3.7 image carried arm re-pointed to its registered "
             "set under PI ruling D65 (3)"),
    "changed": changed,
}
PATH.write_text(json.dumps(doc, indent=1) + ("\n" if text.endswith("\n") else ""),
                encoding="utf-8")
(BOARD / "membership.txt").write_text(bb.render_listing(doc) + "\n", encoding="utf-8")
print(f"{len(changed)} field(s) refreshed")
for c in changed:
    print(c)
