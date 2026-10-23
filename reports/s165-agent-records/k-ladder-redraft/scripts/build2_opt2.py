"""Build decision A's Option 2 variant (as evaluated leads) of the v2 outcome.

Usage: python build2_opt2.py <worktree> <outdir>
Loads build2.py's edit list, swaps three replacements, rebuilds, and writes
opt2-swaps.json with the exact Option 2 texts (old = Option 1 text in the v2 outcome).
"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).parent
src = (HERE / "build2.py").read_text()
src = src.split("text = reg\nfor old, new in EDITS:")[0]
ns = {"__name__": "x"}
sys_argv = sys.argv[:]
exec(compile(src, "build2.py", "exec"), ns)
EDITS, reg = ns["EDITS"], ns["reg"]

v1_dated_bit = ("and seven Phase 2 ladders (the 3.7 gold-standard text ladder and six Gemini 3 "
                "ladders), and tier E's F1 gain below, are now compared")
v2_dated_bit = ("and seven Phase 2 ladders (the 3.7 gold-standard text ladder and six Gemini 3 "
                "ladders) are now compared")
HEAD1 = ("and absorbs about half of K's F1 return: 48.7 % with tier E's rungs compared on the "
         "area every rung searched (D51), and 60.3 % as evaluated (§ 8.6, added on the PI's "
         "ruling 2026-09-13).")
HEAD2 = ("and absorbs about 60 % of K's F1 return: 60.3 % as evaluated, and 48.7 % with tier "
         "E's rungs compared on the area every rung searched, D51's basis (§ 8.6, added on the "
         "PI's ruling 2026-09-13).")
DET1_START = "and raises F1@20 by only +0.0338 with tile-MCC FALLING -0.0238 once the same pool"
DET1_END = "60.3 % as evaluated) —"
DET2 = ("and raises F1@20 by only +0.0262 with tile-MCC FALLING -0.0238 once the same pool is "
        "verified (0.8680/0.8211 at K = 1 and 0.8942/0.7973 at K = 10, as evaluated; "
        "tier-e/ladder.json and each rung's evaluation). On the clipped basis K = 1 reads "
        "0.8604 (reports/scorer-frames-d50-d51-2026-10-08-scripts/out/ladders_new.json) and "
        "K = 10 the same 0.8942, because that rung's union lies wholly in the common area and "
        "the clip removes nothing from it (the K = 10 row of ladders_new.json, 0.8886, predates "
        "the re-verification), so the clipped gain is +0.0338; tile-MCC exists only as "
        "evaluated. The two stages share the common footprint only on the clipped basis, and "
        "never the reference set: the consensus-only side is scored against the 428 reference "
        "mounds inside the footprint, and tier E against the frame's 435, with its K = 1, 3 "
        "and 5 rungs also searching a 37.94 km² band outside the footprint. So the verifier "
        "takes 60.3 % of what extra passes buy on F1 (one minus the ratio of the verified to "
        "the consensus-only gain, on unrounded values; 48.7 % on the clipped basis) —")

text = reg
for old, new in EDITS:
    assert text.count(old) == 1
    text = text.replace(old, new)
opt1 = text
i = opt1.index(DET1_START)
j = opt1.index(DET1_END, i) + len(DET1_END)
DET1 = opt1[i:j]
swaps = [(v1_dated_bit, v2_dated_bit), (HEAD1, HEAD2), (DET1, DET2)]
for old, new in swaps:
    assert text.count(old) == 1, old[:60]
    text = text.replace(old, new)
out = Path(sys.argv[2])
(out / "redraft-opt2.txt").write_text(text + "\n")
(out / "opt2-swaps.json").write_text(json.dumps([dict(old=o, new=n) for o, n in swaps],
                                                ensure_ascii=False, indent=1))
print("option 2 built; swaps", len(swaps))
