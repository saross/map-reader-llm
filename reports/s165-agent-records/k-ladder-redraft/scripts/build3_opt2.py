"""Build decision A's Option 2 variant (as evaluated leads) of the v3 outcome.

Usage: python build3_opt2.py <worktree> <outdir>
Builds the v3 Option 1 text with build3.py's edit list, then applies four swaps, each of
which must match exactly once. Writes redraft-opt2.txt and opt2-swaps.json.
"""
import importlib.util
import json
import sys
from pathlib import Path

HERE = Path(__file__).parent
spec = importlib.util.spec_from_file_location("build3", HERE / "build3.py")
b3 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(b3)  # build3 reads sys.argv[1:3] for the worktree and outdir

GLOSS = "(the detection score, combining precision and recall; F1@20 counts a match within 20 m)"
SWAPS = [
    # the dated clause: tier E is not on the clipped basis under Option 2 ...
    (f"ladders), and tier E's gain in F1 {GLOSS}, are now compared",
     "ladders) are now compared"),
    # ... so the F1 gloss moves to the next use of F1
    ("the reduction in K's F1 gain after verification changes size",
     f"the reduction in K's gain in F1 {GLOSS} after verification changes size"),
    # the headline
    ("and roughly halves K's observed F1 gain: 48.7 % smaller with tier E's rungs compared "
     "on the area every rung searched (D51), 60.3 % smaller as evaluated (§ 8.6, added on "
     "the PI's ruling 2026-09-13).",
     "and cuts K's observed F1 gain by about three-fifths: 60.3 % as evaluated, 48.7 % with "
     "tier E's rungs compared on the area every rung searched, D51's basis (§ 8.6, added on "
     "the PI's ruling 2026-09-13)."),
]
DET1_START = "and raises F1@20 by only +0.0338 with tile-MCC FALLING -0.0238 (as evaluated)"
DET1_END = "60.3 % as evaluated),"
DET2 = ("and raises F1@20 by only +0.0262 with tile-MCC FALLING -0.0238 once the same pool is "
        "verified (0.8680/0.8211 at K = 1 and 0.8942/0.7973 at K = 10, as evaluated; "
        "tier-e/ladder.json and each rung's evaluation). On the clipped basis K = 1 reads "
        "0.8604 (reports/scorer-frames-d50-d51-2026-10-08-scripts/out/ladders_new.json) and "
        "K = 10 the same 0.8942, because that rung's union lies wholly in the common area and "
        "the clip removes nothing (that file's own K = 10 row, 0.8886, predates the "
        "re-verification), so the clipped gain is +0.0338; clipped tile-MCC has not been "
        "computed, so its sign and magnitude are unknown. The two stages share the common "
        "footprint only on the clipped basis, and never the reference set: the consensus-only "
        "side is scored against the 428 mounds inside the footprint, tier E against the "
        "frame's 435, and its K = 1, 3 and 5 rungs also searched a 37.94 km² band outside the "
        "footprint. So, on these scoring bases, the observed F1 gain from extra passes is "
        "60.3 % smaller once the pool is verified (one minus the ratio of the two gains, on "
        "unrounded values; 48.7 % on the clipped basis),")

text = b3.build(b3.EDITS)
i = text.index(DET1_START)
j = text.index(DET1_END, i) + len(DET1_END)
swaps = SWAPS + [(text[i:j], DET2)]
for old, new in swaps:
    assert text.count(old) == 1, old[:70]
    text = text.replace(old, new)
out = Path(sys.argv[2])
(out / "redraft-opt2.txt").write_text(text + "\n")
(out / "opt2-swaps.json").write_text(json.dumps([dict(old=o, new=n) for o, n in swaps],
                                                ensure_ascii=False, indent=1))
print("option 2 built; swaps", len(swaps), "words", len(text.split()))
