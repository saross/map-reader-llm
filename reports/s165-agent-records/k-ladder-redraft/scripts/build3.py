"""Build version 3 of the k-ladder redraft from the register outcome by exact replacements.

Usage: python build3.py <worktree> <outdir>
Writes register.txt, redraft.txt (one line each), redraft-wrapped.txt and diff.txt (word
diff, [-removed-]{+added+}, wrapped at 72 columns). Every replacement must match the signed
register text exactly once, so unlisted sentences stay byte-identical. Version 3 answers
Astra's review of version 2 (items 1-5); see the change log in k-ladder-redraft-v3.md § 8.
"""
import difflib
import json
import sys
import textwrap
from pathlib import Path

W, OUT = Path(sys.argv[1]), Path(sys.argv[2])
reg = [a for a in json.loads((W / "results/run-analyses.json").read_text())["analyses"]
       if a["analysis_id"] == "k-ladder-2026-09-12"][0]["outcome"]

L37 = "the 3.7 gold-standard text ladder"

DATED = (
    "Restated 2026-10-15 (D62 (1), D50, D51, D57 (2) and (3), D65 (2), D67 (5)): each "
    "consensus cluster is now scored on the tiles it was seen on, which moves the grid "
    "study's consensus-only ladders; candidates the verifier had been shown on crops cut "
    "from the neighbouring map sheet, largely blank, were re-verified on crops from their "
    "own sheet (2026-10-13), which moves every rung of the gold-standard stride A ladder, "
    f"tier E's K = 10 rung and {L37}'s K = 5 and K = 10 rungs; the scorer now scores each "
    "detection on the map sheet it was found on (D50), which moves tier E's K = 1, 3 and 5 "
    f"rungs and {L37}'s K = 1 and K = 3; and seven Phase 2 ladders ({L37} and six Gemini 3 "
    "ladders), and tier E's gain in F1 (the detection score, combining precision and "
    "recall; F1@20 counts a match within 20 m), are now compared on the area every rung searched "
    "(D51), a basis on which no "
    "tile-MCC (the Matthews correlation coefficient over map tiles, which scores how well "
    "tiles with and without a mound are told apart) has been computed, so the seven "
    "ladders' tile-MCC is withheld; figures on the earlier, unclipped basis are marked 'as "
    "evaluated'. No verdict moved; the reduction in K's F1 gain after verification "
    "changes size. The "
    "text also carries the re-pricing and corrections the PI approved on 2026-10-04 (the "
    "second under D25), and corrects statements that were wrong or too broad from first "
    "publication: two counts (K = 1's highest-tile-MCC count; ten ladders, not nine, on "
    "which every rung below K = 5 is ruled out as the best), the tile-MCC rise and fall "
    "statements (now limited to K = 1 against the best rung, the comparison tested), the "
    "tile-MCC Pareto reading (a cost preference, not a statistical exclusion of larger "
    "rungs) and the 487-tile resolution (two detection rates, not a threshold). "
)

LEAD = (
    "IN BRIEF: this row asks what extra detection passes buy. Much of the F1 gain comes "
    "from the first three passes, the last step up a ladder is usually the poorest buy, "
    "and how much extra passes help depends mainly on the proposer's thinking level and "
    "temperature. Extra passes never significantly improve tile-MCC over a single pass, "
    "and it falls on most ladders; on the one pool tested with and without the verifier, "
    "verification cut the F1 gain from extra passes by about half to three-fifths, "
    "depending on the scoring basis, and, on the cells as evaluated, turned their tile-MCC "
    "gain into a loss. "
)

EDITS = [
    # 1. K defined at first use (Astra 5)
    ("The pass-count ladder K at otherwise fixed parameters, on 23 ladders:",
     "The pass-count ladder K (K is the number of detection passes whose candidates are "
     "pooled before verification) at otherwise fixed parameters, on 23 ladders:"),
    # 2. one name for the 3.7 gold-standard ladder (v2)
    ("and the 3.7 gold-standard text screen that Phase 2 completed to four rungs",
     "and the Gemini 3.7 gold-standard text ladder that Phase 2 completed to four rungs"),
    # 3. dated clause, then the plain-language lead (Astra 5), before SHAPE
    ("and the seven 55-map deployment ladders. SHAPE:",
     "and the seven 55-map deployment ladders. " + DATED + LEAD + "SHAPE:"),
    # 4. SHAPE (v2, with the fourth-cell disclosure shortened)
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
     "(The 17 counts stride B under the 3.7 verifier with its K = 5 rung, a 55-map board "
     "cell, findings § 3.3, that the ladder inventory lacks; without it, 18.) Where the "
     "last step gains F1 it costs about US$0.20 (gold-standard stride A) to US$27 (55-map "
     "3.7 arm 1) per 0.001 F1 gained; on five ladders it loses F1 (MINIMAL text T 0.3 and "
     "T 0.7, HIGH text T 0.3, HIGH image T 0.7, and tier E); "
     f"{L37}'s K = 5 -> K = 10 step, for example, buys +0.0004 F1@20 for US$8.68."),
    # 5. basis of the significance and single-tier results (v2)
    ("The K = 1 -> best-rung F1 gain is significant on 7 of 7 HIGH-thinking ladders and "
     "2 of 6 MINIMAL ones; four ladders, every one of them MINIMAL, greedy-clique into a "
     "SINGLE tier in which K buys nothing detectable;",
     "The K = 1 -> best-rung F1 gain is significant on 7 of 7 HIGH-thinking ladders and "
     "2 of 6 MINIMAL ones, and four ladders, every one of them MINIMAL, greedy-clique into a "
     "SINGLE tier in which K buys nothing detectable (both tested on the cells as "
     "evaluated);"),
    # 6. HIGH text T 1.0 gain under the clip
    ("(text +0.0559 -> +0.0735 -> +0.0994, image +0.0780 -> +0.0959 -> +0.1514 across "
     "T 0.3 -> 0.7 -> 1.0)",
     "(text +0.0559 -> +0.0735 -> +0.0955, image +0.0780 -> +0.0959 -> +0.1514 across "
     "T 0.3 -> 0.7 -> 1.0; text T 1.0's +0.0955 is on D51's clipped basis, +0.0994 as "
     "evaluated)"),
    # 7. the 15; rise and fall qualified; BH defined at first use (Astra 5)
    ("Across the 21 verified ladders with an interpretable tile-MCC, F1 rises on all 21 and "
     "tile-MCC falls on 16, and NO ladder shows a significant tile-MCC RISE; the "
     "gold-standard ladder's +0.0135, § 4 of the findings' one apparent counter-example, "
     "tests at BH p = 0.7678. Significant FALLS are found on four ladders",
     "Across the 15 verified ladders of findings §§ 4 and 4.3 whose tile-MCC the restated "
     "tables report (the gold-standard stride A ladder, the seven 55-map ladders, and seven "
     "of the thirteen Gemini 3 Phase 2 ladders; the other six are on D51's clipped basis, "
     "where tile-MCC is withheld, and tier E is tested separately, § 8.4), F1 rises on all "
     "15 and tile-MCC falls on 10, and as evaluated it falls on all six withheld ladders too "
     "(16 of 21); NO ladder shows a significant tile-MCC RISE from K = 1 to its best rung, "
     "and the gold-standard ladder's +0.0130, § 4 of the findings' one apparent "
     "counter-example, tests at BH p = 0.7633 (BH: a p value adjusted for multiple "
     "comparisons by the Benjamini-Hochberg procedure). Significant FALLS from K = 1 to the "
     "best rung are found on four ladders"),
    # 8. intermediate steps over every tested pair (v2)
    ("(-0.0637, BH p = 0.0420, the family with the largest F1 gain).",
     "(-0.0637, BH p = 0.0420, the family with the largest F1 gain). Between intermediate "
     "rungs, both 55-map stride A ladders fall significantly from K = 3 to K = 5 (-0.0111, "
     "BH p = 0.0066) and rise significantly from K = 5 to K = 10 (+0.0047, BH p = 0.0300), "
     "so over every tested pair six ladders show a significant fall and two a significant "
     "rise."),
    # 9. raw values
    ("raw 0.1337 / 0.1422 / 0.1337).",
     "the regenerated tables no longer record a raw value)."),
    # 10. one name for the 3.7 ladder (CAVEAT)
    ("three cells of the 3.7 gold-standard text family are scored",
     f"three cells of {L37} are scored"),
    # 11. resolution as two detection rates; the sorting restricted to the gold standard
    #     (Astra 2)
    ("+0.0547 and in only 39 of 200 at +0.0192 — a subsampling standard deviation of "
     "~0.0114 either way — so 487 tiles resolve a ΔF1 of about 0.03 and above and not "
     "below. The nine MINIMAL ladders sort by effect size rather than by corpus (every one "
     "at or above +0.0546 separates, every one at or below +0.0223 does not), and the "
     "deployment range +0.0192..+0.0547 sits INSIDE the gold-standard range "
     "+0.0139..+0.0629.",
     "+0.0547 and in only 39 of 200 at +0.0192 — a subsampling standard deviation of "
     "~0.0114 either way: detection rates for two effects, not a threshold (+0.0192 "
     "separates on all 8,541 tiles). On the gold-standard ladders, as evaluated, every "
     "MINIMAL gain at or above +0.0546 separates and every one at or below +0.0223 does "
     "not, while +0.0338 separates and +0.0384 (BH p = 0.1236) does not; and the deployment "
     "range +0.0192..+0.0547 sits INSIDE the gold-standard range +0.0139..+0.0600 (+0.0629 "
     "as evaluated)."),
    # 12. PARETO: admissibility, cost preference and frontier kept apart (Astra 1)
    ("PARETO MCC SET: on tile-MCC no rung above K = 1 is ever the admissible choice — K = 1 "
     "holds the highest tile-MCC on 13 of the 21 interpretable ladders and is never "
     "significantly beaten on it — so the MCC-efficient rung is K = 1 wherever tile-level "
     "discrimination is the objective, while the F1-efficient rung is K = 3. The two "
     "objectives select different rungs, and that is the review's practical finding.",
     "PARETO MCC SET: K = 1 is the cheapest member of every tile-MCC set of multiple "
     "comparisons with the best (MCB, below), holds the highest tile-MCC on 7 of the 15 "
     "ladders above, and no K = 1 -> best-rung comparison shows a significant MCC gain, so "
     "it is the cost-conscious choice for tile-level discrimination when the rule is to "
     "take the cheapest rung not ruled out as best; larger rungs are not excluded (the MCB "
     "admits one on 20 of 22 ladders). For F1, K = 3 is on every ladder's observed cost "
     "frontier but is the cheapest MCB-admissible rung on only 10 of 22. The two "
     "objectives favour different rungs, and that is the review's practical finding."),
    # 13. geometry effect (origin route)
    ("about 2.4x larger at 12.5 % overlap than at 50 % (+0.1454 against +0.0572 at 384 px; "
     "+0.0914 against +0.0396 at 512 px), and tile-MCC RISES with K on all four "
     "consensus-only cells (+0.038..+0.154)",
     "about 2.2x larger at 12.5 % overlap than at 50 % (+0.1441 against +0.0660 at 384 px; "
     "+0.0947 against +0.0425 at 512 px), and tile-MCC RISES with K on all four "
     "consensus-only cells (+0.029..+0.132)"),
    # 14. verifier headline: as evaluated; observed gain reduction (Astra 3, 4)
    ("and absorbs about 40 % of K's F1 return (§ 8.6, added on the PI's ruling 2026-09-13).",
     "on the cells as evaluated, and roughly halves K's observed F1 gain: 48.7 % smaller "
     "with tier E's rungs compared on the area every rung searched (D51), 60.3 % smaller as "
     "evaluated (§ 8.6, added on the PI's ruling 2026-09-13)."),
    # 15. verifier detail (Astra 3, 4; v2 anchors, reference sets, derivation)
    ("K = 1 -> 10 raises F1@20 by +0.0572 with tile-MCC RISING +0.0444 consensus-only "
     "(results/grid-2026-08-18/sweep.csv, cell g384_ov192, best F1@20 per K over the "
     "corroboration x vote grid: 0.6633/0.4465 at K = 1, 0.7205/0.4909 at K = 10), and "
     "raises F1@20 by only +0.0340 with tile-MCC FALLING -0.0308 once the same pool is "
     "verified (tier-e/ladder.json and each rung's evaluation: 0.8546/0.8211 at K = 1, "
     "0.8886/0.7903 at K = 10). So the verifier takes 40.6 % of what extra passes buy on "
     "F1 — because it was already removing much of what extra passes remove — and turns a "
     "tile-level GAIN into a tile-level LOSS, a swing of 0.0752 MCC. This is the mechanism "
     "of the TILE-MCC DOES NOT FOLLOW F1 finding above measured directly rather than "
     "inferred: tile-MCC's response to K is a property of the PIPELINE STAGE, not of K.",
     "K = 1 -> 10 raises F1@20 by +0.0660 with tile-MCC RISING +0.0444 consensus-only "
     "(results/grid-2026-08-18/sweep.csv, cell g384_ov192, best F1@20 per K over the "
     "corroboration x vote grid: 0.6633/0.4465 at K = 1, 0.7293/0.4909 at K = 10), and "
     "raises F1@20 by only +0.0338 with tile-MCC FALLING -0.0238 (as evaluated) once the "
     "same pool is verified. The clipped F1@20 is 0.8604 at K = 1 "
     "(reports/scorer-frames-d50-d51-2026-10-08-scripts/out/ladders_new.json) and 0.8942 at "
     "K = 10, the restated rung of tier-e/ladder.json, whose union lies wholly in the common "
     "area so the clip removes nothing (that file's own K = 10 row, 0.8886, predates the "
     "re-verification); as evaluated, K = 1 reads 0.8680 and the gain is +0.0262. Tile-MCC "
     "(0.8211 at K = 1, 0.7973 at K = 10; tier-e/ladder.json and each rung's evaluation) "
     "exists only as evaluated; clipped tile-MCC has not been computed, so its sign and "
     "magnitude are unknown. The two stages share the common footprint but not the "
     "reference set: the consensus-only side is scored against the 428 mounds inside it, "
     "tier E against the frame's 435 (D51), 7 of which lie outside the clipped area. So, on "
     "these scoring bases, the observed F1 gain from extra passes is 48.7 % smaller once "
     "the pool is verified (one minus the ratio of the two gains, on unrounded values; "
     "60.3 % as evaluated), and on the cells as evaluated a tile-level GAIN becomes a "
     "tile-level LOSS, a swing of 0.0682 MCC. This is consistent with the mechanism "
     "proposed for the TILE-MCC DOES NOT FOLLOW F1 finding above (the verifier was already "
     "removing much of what extra passes remove) but does not measure it directly: on this "
     "pool, tile-MCC's response to K depends on the PIPELINE STAGE, not on K alone."),
    # 16. NOT CLAIMED: the count in this text's frame (v2)
    ("and the five non-separating ladders' MCC moves are not shown to be zero.",
     "and the MCC moves of the ladders whose K = 1 -> best-rung change does not separate "
     "(11 of the 15; 17 of 21 as evaluated) are not shown to be zero."),
    # 17. MCB gloss at the heading (v2)
    ("HSU MCB ADMISSIBLE SETS (PI ruling 2026-09-13, 'wait for the sets'):",
     "HSU MCB ADMISSIBLE SETS (the rungs that cannot be ruled out as their ladder's best; "
     "PI ruling 2026-09-13, 'wait for the sets'):"),
    # 18. MCB basis (v2)
    ("results/k-ladder-2026-09-12/mcb/summary.json). ON THE SHAPE FINDING:",
     "results/k-ladder-2026-09-12/mcb/summary.json). The sets are computed on the cells as "
     "evaluated, so every MCB count below includes tier E and the six Gemini 3 ladders "
     "whose tile-MCC the clipped basis withholds above; that basis has no per-tile table to "
     "compute them on. ON THE SHAPE FINDING:"),
    # 19. nine -> ten (v1)
    ("on nine ladders nothing below K = 5 is admissible even though",
     "on ten ladders nothing below K = 5 is admissible (on nine the cheapest admissible "
     "rung is K = 5; on 55-map stride B under the 3.7 verifier only K = 10 is) even "
     "though"),
    # 20. ON THE LAST STEP, consistent with SHAPE (v2)
    ("so the top rung is never statistically ruled out, only never worth its price, which "
     "is the formal counterpart of the US$1,100-to-US$43,000 per 0.001 F1 figures above.",
     "so the top rung is never statistically ruled out, and whether it is worth its price "
     "is the cost question SHAPE above answers: the last step is the worst buy on 17 of "
     "the 23 ladders, not on all."),
    # 21. ON THE TWO OBJECTIVES: what the MCB adds to PARETO (Astra 1); v2's breakdown cut
    ("holding the highest tile-MCC on 13 of them, so the PARETO MCC SET claim above now "
     "rests on the canonical simultaneous instrument rather than on a pairwise count.",
     "holding the highest tile-MCC on 13 of them, so the simultaneous instrument agrees "
     "with the pairwise tests that K = 1 is never ruled out on tile-MCC, while on F1 it "
     "almost always is."),
    # 22-24. MCB counts moved by tier E's restated rungs
    ("WHOLE ladder on 12 of 22", "WHOLE ladder on 13 of 22"),
    ("seven of the twenty ladders with a K = 10 rung exclude it",
     "six of the twenty ladders with a K = 10 rung exclude it"),
    ("w_upper is 0.0151-0.0326", "w_upper is 0.0159-0.0326"),
    # 25. WITHHELD: three cells on two rungs; one name (v2)
    ("WITHHELD: the 3.7 gold-standard text screen has NO admissible set on either metric, "
     "because the tile-join invariant refuses the per-tile table of three of its four rungs "
     "on this frame",
     f"WITHHELD: {L37} has NO admissible set on either metric, because the tile-join "
     "invariant refuses the per-tile table of three cells on two of its four rungs (K = 1 "
     "and K = 3) on this frame"),
]


def build(edits):
    """Apply the edits in order to the signed text; each must match exactly once."""
    text = reg
    for old, new in edits:
        n = text.count(old)
        assert n == 1, (n, old[:80])
        text = text.replace(old, new)
    return text


if __name__ == "__main__":
    text = build(EDITS)
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
    wrap = textwrap.TextWrapper(width=72, break_long_words=False, break_on_hyphens=False)
    (OUT / "diff.txt").write_text(wrap.fill(" ".join(parts)) + "\n")
    (OUT / "redraft-wrapped.txt").write_text(wrap.fill(text) + "\n")
    print("edits", len(EDITS), "register words", len(a), "redraft words", len(b))
