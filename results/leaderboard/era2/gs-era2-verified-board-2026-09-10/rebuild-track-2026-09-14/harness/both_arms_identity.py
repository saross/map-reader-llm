#!/usr/bin/env python3
"""Record whether a rebuilt tiering reproduced BOTH arms of the committed one.

The Era-2 rebuild of 2026-09-14 (erratum E88, ruling 4) corrects seven
membership ``track`` labels and adds a ``track_basis`` field. ``track`` is
metadata: neither ``scripts/era1_leaderboard_tiering.py`` nor
``scripts/selection_aware_intervals.py`` reads it, and ``tiering_20m.json``
carries no ``track`` field at all. So BOTH the F1 arm and the tile-MCC arm are
predicted to reproduce exactly — a stronger prediction than the 2026-09-13
rebuild's, whose sibling harness deliberately exempted the (then brand-new)
``mcc_permutation`` block. A prediction that specific is recorded as a checkable
artefact rather than asserted in prose.

Usage::

    python3 both_arms_identity.py <before.json> <after.json> <out.json> [blob]
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

before = json.loads(Path(sys.argv[1]).read_text())
after = json.loads(Path(sys.argv[2]).read_text())
out = Path(sys.argv[3])

#: Only the run stamp and the commit may move. Unlike the 2026-09-13 sibling,
#: the whole MCC arm is IN scope here.
VOLATILE = {"generated_at_utc", "git_commit"}


def same(lhs: object, rhs: object) -> bool:
    """Order-insensitive, content-sensitive comparison."""
    return json.dumps(lhs, sort_keys=True) == json.dumps(rhs, sort_keys=True)


F1_KEYS = ("ranking", "tiers", "tie_set", "pairwise", "n_cells",
           "n_cells_withheld", "n_tiles", "n_permutations", "seed",
           "fdr_q", "replicate_handling", "metric", "buffer_metres")
arms = {k: same(before.get(k), after.get(k)) for k in F1_KEYS}

mcc_before = before.get("mcc_permutation") or {}
mcc_after = after.get("mcc_permutation") or {}
mcc_arms = {k: same(mcc_before.get(k), mcc_after.get(k))
            for k in sorted(set(mcc_before) | set(mcc_after))}

moved = [k for k in sorted(set(before) | set(after))
         if k not in VOLATILE and not same(before.get(k), after.get(k))]

withheld_delta = []
b = {w["label"]: w for w in before.get("withheld_cells", [])}
a = {w["label"]: w for w in after.get("withheld_cells", [])}
for label in sorted(set(b) | set(a)):
    for field in ("eval_f1", "recorded_mcc"):
        lhs, rhs = (b.get(label) or {}).get(field), (a.get(label) or {}).get(field)
        if not same(lhs, rhs):
            withheld_delta.append({"label": label, "field": field,
                                   "before": lhs, "after": rhs})

verdict = {
    "what": ("whether the 2026-09-14 derived-track rebuild reproduced BOTH arms "
             "of the committed 2026-09-13 MCC-family run; `track` is metadata "
             "the tiering never reads, so both are predicted identical"),
    "before": str(sys.argv[1]),
    "before_git_blob": (sys.argv[4] if len(sys.argv) > 4 else None),
    "after": str(sys.argv[2]),
    "f1_arm_identical": all(arms.values()),
    "mcc_arm_identical": all(mcc_arms.values()) if mcc_arms else None,
    "both_arms_identical": all(arms.values()) and bool(mcc_arms) and all(mcc_arms.values()),
    "arms": arms,
    "mcc_arms": mcc_arms,
    "keys_that_moved": moved,
    "withheld_cells_field_changes": withheld_delta,
    "n_significant_before": sum(1 for r in before["pairwise"] if r["significant"]),
    "n_significant_after": sum(1 for r in after["pairwise"] if r["significant"]),
    "n_tiers_before": len(before["tiers"]),
    "n_tiers_after": len(after["tiers"]),
    "tie_set_before": before["tie_set"],
    "tie_set_after": after["tie_set"],
    "n_mcc_significant_before": sum(
        1 for r in (mcc_before.get("pairwise") or []) if r["significant"]),
    "n_mcc_significant_after": sum(
        1 for r in (mcc_after.get("pairwise") or []) if r["significant"]),
    "n_mcc_tiers_before": len(mcc_before.get("tiers") or []),
    "n_mcc_tiers_after": len(mcc_after.get("tiers") or []),
    "mcc_tie_set_size_before": len(mcc_before.get("tie_set") or []),
    "mcc_tie_set_size_after": len(mcc_after.get("tie_set") or []),
}
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(json.dumps(verdict, indent=1) + "\n")
print(f"f1_arm_identical = {verdict['f1_arm_identical']}; "
      f"mcc_arm_identical = {verdict['mcc_arm_identical']}; "
      f"moved = {moved}; wrote {out}")
