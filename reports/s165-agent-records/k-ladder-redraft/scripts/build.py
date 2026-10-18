"""Build the k-ladder redraft from the register outcome by exact replacements.

Usage: python build.py <worktree> <outdir>
Writes register.txt, redraft.txt (one line each) and diff.txt (word diff,
[-removed-]{+added+}, wrapped at 72 columns).
"""
import difflib
import json
import sys
import textwrap
from pathlib import Path

W, OUT = Path(sys.argv[1]), Path(sys.argv[2])
reg = [a for a in json.loads((W / "results/run-analyses.json").read_text())["analyses"]
       if a["analysis_id"] == "k-ladder-2026-09-12"][0]["outcome"]

DATED = (
    "Restated 2026-10-15 (D62 (1), D50, D51, D57 (2), D65 (2), D67 (5)): each consensus "
    "cluster is now scored on the tiles it was seen on, which moves the grid study's "
    "consensus-only ladders; candidates the verifier had been shown on crops cut from the "
    "neighbouring map sheet, largely blank, were re-verified on crops from their own sheet "
    "(2026-10-13), which moves every rung of the gold-standard stride A ladder, tier E's "
    "K = 10 rung and the 3.7 gold-standard ladder's K = 5 and K = 10 rungs; the "
    "sheet-scoped scorer (D50) re-scores tier E's K = 1, 3 and 5 rungs and the 3.7 "
    "ladder's K = 1 and K = 3; and seven Phase 2 ladders (the 3.7 screen and six Gemini 3 "
    "ladders), and tier E's F1 gain below, are now compared on the area every rung "
    "searched (D51), a basis on which no tile-MCC has been computed, so the seven ladders' "
    "tile-MCC is withheld; "
    "figures on the earlier, unclipped basis are marked 'as evaluated'. No verdict moved; "
    "the verifier's share of K's F1 return changes size, and the text now carries the "
    "re-pricing and corrections in the two signature notes the PI approved on 2026-10-04 (the second "
    "under D25) and two counts that were wrong from first publication (K = 1's "
    "highest-tile-MCC count, and the ladders admitting nothing below K = 5). "
)

EDITS = [
    # 1. dated clause (walk-through convention)
    ("and the seven 55-map deployment ladders. SHAPE:",
     "and the seven 55-map deployment ladders. " + DATED + "SHAPE:"),
    # 2. SHAPE: D25 corrections, units, efficient-set gloss, losses
    ("in the corpus — 37 % to 93 % of a ladder's total F1 gain for 31 % to 64 % of its top "
     "rung's cost — while the last step is the worst buy on every ladder, at US$1,100 to "
     "US$43,000 per 0.001 F1 (the 3.7 family's K = 5 -> K = 10 step buys +0.0002 F1@20 for "
     "US$8.65).",
     "in the corpus (a rung is efficient when no cheaper rung of the same ladder scores as "
     "well) — 37 % to 93 % of a ladder's total F1 gain for 31 % to 62 % of its top rung's "
     "cost — while the last step (K = 5 -> 10, or K = 3 -> 5 on the two 55-map 3.7 arms, "
     "which have no K = 10 rung) is the worst buy, the dearest per 0.001 F1 or a loss of "
     "F1, on 17 of the 23 ladders; on the other six (the gold-standard stride A ladder, the "
     "two 55-map stride B ladders under the Gemini 3 verifier, stride B under the 3.7 "
     "verifier, MINIMAL image T 0.3 and HIGH image T 1.0) the K = 3 -> 5 step is worse. "
     "Where the last step gains F1 it costs about US$0.20 (gold-standard stride A) to US$27 "
     "(55-map 3.7 arm 1) per 0.001 F1 gained; on "
     "five ladders it loses F1 (MINIMAL text T 0.3 and T 0.7, HIGH text T 0.3, HIGH image "
     "T 0.7, and tier E); and the 3.7 gold-standard family's K = 5 -> K = 10 step buys "
     "+0.0004 F1@20 for US$8.68, about US$22 per 0.001 F1."),
    # 3. basis of the significance counts
    ("and 2 of 6 MINIMAL ones;",
     "and 2 of 6 MINIMAL ones (tested on the cells as evaluated);"),
    # 4. HIGH text T 1.0 gain under the clip
    ("(text +0.0559 -> +0.0735 -> +0.0994, image +0.0780 -> +0.0959 -> +0.1514 across "
     "T 0.3 -> 0.7 -> 1.0)",
     "(text +0.0559 -> +0.0735 -> +0.0955, image +0.0780 -> +0.0959 -> +0.1514 across "
     "T 0.3 -> 0.7 -> 1.0; text T 1.0's +0.0955 is on D51's clipped basis, +0.0994 as "
     "evaluated)"),
    # 5. the 15, both bases; the rise qualifier; GS delta from the artefact
    ("Across the 21 verified ladders with an interpretable tile-MCC, F1 rises on all 21 and "
     "tile-MCC falls on 16, and NO ladder shows a significant tile-MCC RISE; the "
     "gold-standard ladder's +0.0135, § 4 of the findings' one apparent counter-example, "
     "tests at BH p = 0.7678.",
     "Across the 15 verified ladders whose tile-MCC the restated tables report (the "
     "gold-standard stride A ladder, the seven 55-map ladders, and seven of the thirteen "
     "Gemini 3 Phase 2 ladders; the other six are on D51's clipped basis, where tile-MCC is "
     "withheld), F1 rises on all 15 and tile-MCC falls on 10, and as evaluated it falls on "
     "all six withheld ladders too (16 of 21); NO ladder shows a significant tile-MCC RISE "
     "from K = 1 to its best rung, and the gold-standard ladder's +0.0130, § 4 of the "
     "findings' one apparent counter-example, tests at BH p = 0.7633."),
    # 6. raw values
    ("raw 0.1337 / 0.1422 / 0.1337).",
     "the regenerated tables no longer record a raw value)."),
    # 7. GS MINIMAL range
    ("gold-standard range +0.0139..+0.0629.",
     "gold-standard range +0.0139..+0.0600 (+0.0629 as evaluated)."),
    # 8. 7 of 15, both bases
    ("K = 1 holds the highest tile-MCC on 13 of the 21 interpretable ladders and is never "
     "significantly beaten on it",
     "K = 1 holds the highest tile-MCC on 7 of the 15 ladders above (13 of the 22 in the "
     "multiple-comparisons-with-the-best (MCB) sets below, which are computed on the cells "
     "as evaluated and so add tier E and the six withheld ladders) and is never "
     "significantly beaten on it"),
    # 9. geometry effect (origin route)
    ("about 2.4x larger at 12.5 % overlap than at 50 % (+0.1454 against +0.0572 at 384 px; "
     "+0.0914 against +0.0396 at 512 px), and tile-MCC RISES with K on all four "
     "consensus-only cells (+0.038..+0.154)",
     "about 2.2x larger at 12.5 % overlap than at 50 % (+0.1441 against +0.0660 at 384 px; "
     "+0.0947 against +0.0425 at 512 px), and tile-MCC RISES with K on all four "
     "consensus-only cells (+0.029..+0.132)"),
    # 10. verifier share headline, D51 basis leading
    ("and absorbs about 40 % of K's F1 return (§ 8.6, added on the PI's ruling 2026-09-13).",
     "and absorbs about half of K's F1 return: 48.7 % with tier E's rungs compared on the "
     "area every rung searched, the basis D51's text extends to tier E, and 60.3 % as "
     "evaluated (§ 8.6, added on the PI's ruling 2026-09-13)."),
    # 11. verifier detail
    ("K = 1 -> 10 raises F1@20 by +0.0572 with tile-MCC RISING +0.0444 consensus-only "
     "(results/grid-2026-08-18/sweep.csv, cell g384_ov192, best F1@20 per K over the "
     "corroboration x vote grid: 0.6633/0.4465 at K = 1, 0.7205/0.4909 at K = 10), and "
     "raises F1@20 by only +0.0340 with tile-MCC FALLING -0.0308 once the same pool is "
     "verified (tier-e/ladder.json and each rung's evaluation: 0.8546/0.8211 at K = 1, "
     "0.8886/0.7903 at K = 10). So the verifier takes 40.6 % of what extra passes buy on "
     "F1 — because it was already removing much of what extra passes remove — and turns a "
     "tile-level GAIN into a tile-level LOSS, a swing of 0.0752 MCC.",
     "K = 1 -> 10 raises F1@20 by +0.0660 with tile-MCC RISING +0.0444 consensus-only "
     "(results/grid-2026-08-18/sweep.csv, cell g384_ov192, best F1@20 per K over the "
     "corroboration x vote grid: 0.6633/0.4465 at K = 1, 0.7293/0.4909 at K = 10), and "
     "raises F1@20 by only +0.0338 with tile-MCC FALLING -0.0238 once the same pool is "
     "verified (F1@20 0.8604 at K = 1 on the clipped basis, "
     "reports/scorer-frames-d50-d51-2026-10-08-scripts/out/ladders_new.json, and 0.8942 at "
     "K = 10, whose union was already limited to the common area; as evaluated, K = 1 reads 0.8680 "
     "and the gain +0.0262; tile-MCC 0.8211 at K = 1 and 0.7973 at K = 10, as evaluated, "
     "since no clipped tile-MCC exists; tier-e/ladder.json and each rung's evaluation). So "
     "the verifier takes 48.7 % (60.3 % as evaluated) of what extra passes buy on F1 — "
     "because it was already removing much of what extra passes remove — and turns a "
     "tile-level GAIN into a tile-level LOSS, a swing of 0.0682 MCC."),
    # 12. MCB gloss
    ("HSU MCB ADMISSIBLE SETS (PI ruling 2026-09-13, 'wait for the sets'):",
     "HSU MCB ADMISSIBLE SETS (the rungs that cannot be ruled out as their ladder's best; "
     "PI ruling 2026-09-13, 'wait for the sets'):"),
    # 13. MCB basis
    ("results/k-ladder-2026-09-12/mcb/summary.json). ON THE SHAPE FINDING:",
     "results/k-ladder-2026-09-12/mcb/summary.json). The sets are computed on the cells as "
     "evaluated, so every MCB count below includes tier E and the six Gemini 3 ladders "
     "whose tile-MCC the clipped basis withholds above; that basis has no per-tile table to "
     "compute them on. ON THE SHAPE FINDING:"),
    # 14. nine -> ten
    ("on nine ladders nothing below K = 5 is admissible even though",
     "on ten ladders nothing below K = 5 is admissible (on nine the cheapest admissible "
     "rung is K = 5; on 55-map stride B under the 3.7 verifier only K = 10 is) even "
     "though"),
    # 15. prices cross-reference
    ("which is the formal counterpart of the US$1,100-to-US$43,000 per 0.001 F1 figures "
     "above.",
     "which is the formal counterpart of the last-step prices per 0.001 F1 under SHAPE "
     "above."),
    # 16. 13 of 22, tied to the 15
    ("holding the highest tile-MCC on 13 of them, so",
     "holding the highest tile-MCC on 13 of them (the 7 of the 15 above, five of the six "
     "withheld ladders, and tier E), so"),
    # 17-19. MCB counts moved by tier E's restated rungs
    ("WHOLE ladder on 12 of 22", "WHOLE ladder on 13 of 22"),
    ("seven of the twenty ladders with a K = 10 rung exclude it",
     "six of the twenty ladders with a K = 10 rung exclude it"),
    ("w_upper is 0.0151-0.0326", "w_upper is 0.0159-0.0326"),
]

text = reg
for old, new in EDITS:
    n = text.count(old)
    assert n == 1, (n, old[:80])
    text = text.replace(old, new)

(OUT / "register.txt").write_text(reg + "\n")
(OUT / "redraft.txt").write_text(text + "\n")

a, b = reg.split(), text.split()
sm = difflib.SequenceMatcher(a=a, b=b, autojunk=False)
parts = []
for op, i1, i2, j1, j2 in sm.get_opcodes():
    if op == "equal":
        parts.extend(a[i1:i2])
    else:
        if i2 > i1:
            parts.append("[-" + " ".join(a[i1:i2]) + "-]")
        if j2 > j1:
            parts.append("{+" + " ".join(b[j1:j2]) + "+}")
diff = " ".join(parts)
wrap = textwrap.TextWrapper(width=72, break_long_words=False, break_on_hyphens=False)
(OUT / "diff.txt").write_text(wrap.fill(diff) + "\n")
(OUT / "redraft-wrapped.txt").write_text(wrap.fill(text) + "\n")
print("register words", len(a), "redraft words", len(b))
