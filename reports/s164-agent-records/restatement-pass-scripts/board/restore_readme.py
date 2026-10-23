#!/usr/bin/env python3
"""Restore the Era-2 board README's banner, E86 block, and changelog by hand.

Usage: restore_readme.py <regenerated README> <committed README>
Edits the regenerated README in place (S164 restatement pass, record § 1.3).

Part of the S164 restatement pass (reports/s164-agent-records/
restatement-pass.md § 1.3, the Era-2 board lane).

Author: Shawn Ross, Claude Code (S164). Licence: Apache 2.0
"""
import sys
from pathlib import Path

reg_p, com_p = Path(sys.argv[1]), Path(sys.argv[2])
reg = reg_p.read_text().split("\n")
com = com_p.read_text().split("\n")

# 1. Banner: today's lead, then the committed banner's card/frame/instrument tail.
assert reg[2].startswith("> **Last revised**: 2026-10-15 (original publication).")
tail = com[2][com[2].index("Card: "):]
reg[2] = (
    "> **Last revised**: 2026-10-15 (**RESTATED** by the S164 restatement pass, PI "
    "ruling D65 (2): the ten members that read the D62 (1) re-verified wrong-sheet "
    "rows re-scored on this frame, and tier E's four K-ladder cells shown at their "
    "S9 re-scored evaluations; 8075/11175 pairs significant, 14 tiers, the same "
    "five-cell Tier 1 in the same order, F1 MCB admissible set 65 → 52; the PI's "
    "signature of 2026-09-16 attests the earlier numbers). " + tail
)

# 2. E86 disclosure: committed block, re-inserted before the tile-MCC section.
start = next(i for i, ln in enumerate(com) if ln.startswith("**Null-exemplar exposure"))
end = next(i for i, ln in enumerate(com) if ln.startswith("## Tile-level MCC"))
block = com[start:end]
assert block[-1] == ""
note = [
    "*Note (2026-10-15, S164 restatement pass): the figures in this disclosure are",
    "the null-exemplar sensitivity analysis's of 2026-09-13, which the pass did not",
    "re-run (it is outside the pass's scope). On the full frame the tile-MCC Tier 1",
    "it starts from is now 34 cells (33 when this was written), and the ten",
    "re-scored members moved; whether its reduced-frame readings move is",
    "unmeasured.*",
    "",
]
at = next(i for i, ln in enumerate(reg) if ln.startswith("## Tile-level MCC"))
assert not any(ln.startswith("**Null-exemplar exposure") for ln in reg)
reg[at:at] = block + note

# 3. Changelog: drop the old "(latest)" tag and add today's entry first.
old = next(i for i, ln in enumerate(reg) if ln.startswith("### 2026-09-14 (latest) — "))
reg[old] = reg[old].replace("### 2026-09-14 (latest) — ", "### 2026-09-14 — ", 1)
cl = reg.index("## Changelog")
entry = Path(sys.argv[3]).read_text().rstrip("\n").split("\n") + [""]
assert reg[cl + 1] == ""
reg[cl + 2:cl + 2] = entry
reg_p.write_text("\n".join(reg))
print("banner, E86 block (%d lines + note), changelog entry (%d lines)" % (len(block), len(entry)))
