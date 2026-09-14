"""Record whether a rebuilt tiering's F1 arm reproduced the committed one.

The Era-2 rebuild of 2026-09-13 carries three ruled changes, none of which
touches an F1 input: of the four cells the recovery-fragment fix re-scored,
three are already withheld from every statistic and the fourth re-scores
dict-identically. The F1 arm is therefore predicted to reproduce EXACTLY, and a
prediction that specific should be recorded as a checkable artefact rather than
asserted in prose.

Writes a verdict JSON naming, arm by arm, what is identical and what moved.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

before = json.loads(Path(sys.argv[1]).read_text())
after = json.loads(Path(sys.argv[2]).read_text())
out = Path(sys.argv[3])

#: Keys whose change is expected: the run stamp, the commit, and the whole new
#: MCC arm. Everything else in the F1 arm must match.
VOLATILE = {"generated_at_utc", "git_commit", "mcc_permutation"}


def same(lhs: object, rhs: object) -> bool:
    """Order-insensitive, content-sensitive comparison."""
    return json.dumps(lhs, sort_keys=True) == json.dumps(rhs, sort_keys=True)


arms = {k: same(before.get(k), after.get(k))
        for k in ("ranking", "tiers", "tie_set", "pairwise", "n_cells",
                  "n_cells_withheld", "n_tiles", "n_permutations", "seed",
                  "fdr_q", "replicate_handling", "metric", "buffer_metres")}
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
    "what": ("whether the F1 arm of the 2026-09-13 MCC-family rebuild "
             "reproduced the committed 2026-09-13 F1-only run"),
    # The "before" file is not kept in the job directory: it is 4.7 MB and git
    # already holds it. The blob hash below is what to re-extract, so the claim
    # stays checkable without a duplicate.
    "before": str(sys.argv[1]),
    "before_git_blob": (sys.argv[4] if len(sys.argv) > 4 else None),
    "after": str(sys.argv[2]),
    "f1_arm_identical": all(arms.values()),
    "arms": arms,
    "keys_that_moved": moved,
    "withheld_cells_field_changes": withheld_delta,
    "n_significant_before": sum(1 for r in before["pairwise"] if r["significant"]),
    "n_significant_after": sum(1 for r in after["pairwise"] if r["significant"]),
    "n_tiers_before": len(before["tiers"]),
    "n_tiers_after": len(after["tiers"]),
    "tie_set_before": before["tie_set"],
    "tie_set_after": after["tie_set"],
}
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(json.dumps(verdict, indent=1) + "\n")
print(f"f1_arm_identical = {verdict['f1_arm_identical']}; "
      f"moved = {moved}; wrote {out}")
