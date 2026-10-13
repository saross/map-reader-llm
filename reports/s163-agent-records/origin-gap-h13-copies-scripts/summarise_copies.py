#!/usr/bin/env python3
"""
Summarise the library-copy measurements (D62 (1) step 2) across three runs.

Reads ``copies/{new1,new2,old}/<section>.json`` written by
``measure_copies.py`` and reports, per section: whether the two runs of the
fixed code agree byte for byte; whether every arm built by origin/main's
code equals the fixed frame with its ``source_tiles`` dropped (scope
signature, scope counters, and P/R/F1), which shows that dropping the
column reproduces the pre-fix frame; and every arm the fix moves, with its
F1 before and after.

Usage::

    python summarise_copies.py <copies dir> <json out>

Author: Claude Code (Opus 5.5) for Shawn Ross
Licence: Apache 2.0
"""

from __future__ import annotations

import json
import sys
from pathlib import Path


def arms(section: str, data: dict) -> dict[str, dict]:
    """Flatten a section's records to ``{arm key: record}``.

    Args:
        section: Section name. data: The section's JSON.

    Returns:
        One record per arm (the pes section is keyed ``variant|condition``).
    """
    if section == "pes":
        return {f"{v}|{k}": r for v, d in data.items() for k, r in d.items()}
    return data


def main() -> int:
    """Print and write the summary.

    Returns:
        0 when both integrity checks pass, 1 otherwise.
    """
    root, out = Path(sys.argv[1]), Path(sys.argv[2])
    summary: dict = {}
    ok = True
    for section in ("diversity-track1", "diversity-track2", "pes", "p3a"):
        b1 = (root / "new1" / f"{section}.json").read_bytes()
        b2 = (root / "new2" / f"{section}.json").read_bytes()
        new = arms(section, json.loads(b1))
        old = arms(section, json.loads((root / "old" / f"{section}.json").read_text()))
        same_runs = b1 == b2
        construction = []
        moved = []
        n_scored = 0
        for key, rec in new.items():
            if "as_built" not in rec:
                continue
            n_scored += 1
            o = old[key]
            ref = rec.get("dropped", rec["as_built"])
            if o.get("as_built") != ref or o["n"] != rec["n"]:
                construction.append(key)
            if rec.get("moves") or (rec.get("dropped") and rec["dropped"] != rec["as_built"]):
                moved.append({
                    "arm": key, "n": rec["n"],
                    "scope_moves": rec.get("moves"),
                    "f1_before": rec["dropped"]["f1"], "f1_after": rec["as_built"]["f1"],
                    "p_before": rec["dropped"]["precision"],
                    "p_after": rec["as_built"]["precision"],
                    "r_before": rec["dropped"]["recall"], "r_after": rec["as_built"]["recall"],
                    "diag_before": rec["dropped"]["diag"], "diag_after": rec["as_built"]["diag"],
                    "committed_f1": rec.get("committed_f1"),
                })
        repro = None
        if section.startswith("diversity"):
            # Does origin/main's code reproduce the committed 4-dp F1?
            rows = [(r.get("committed_f1"), round(r["as_built"]["f1"], 4))
                    for r in old.values() if "as_built" in r]
            repro = {"arms": len(rows), "equal_at_4dp": sum(a == b for a, b in rows)}
        summary[section] = {
            "new1_new2_identical_bytes": same_runs,
            "arms": len(new), "arms_scored": n_scored,
            "old_equals_new_dropped_failures": construction,
            "moved": moved,
            "old_reproduces_committed_f1": repro,
        }
        ok = ok and same_runs and not construction
        print(section, json.dumps({k: (v if k != "moved" else len(v))
                                   for k, v in summary[section].items()}))
        for m in moved:
            print("   MOVED", m["arm"], m["n"], f"{m['f1_before']:.6f} -> {m['f1_after']:.6f}",
                  m["diag_after"])
    out.write_text(json.dumps(summary, indent=1, sort_keys=True))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
