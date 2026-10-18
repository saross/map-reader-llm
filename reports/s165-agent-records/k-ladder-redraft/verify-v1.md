# Verification of the k-ladder redraft (`k-ladder-redraft.md`, register row `k-ladder-2026-09-12`)

- **Verifier**: Claude (Anthropic), Claude Code, model lane Opus 5.5 (`claude-opus-5-5`),
  read-only sub-agent. Date 2026-10-18.
- **Read from**: `/home/shawn/worktrees/map-reader-llm/claude-pr52-restate`, branch
  `restatement-pass-s164`, head `e3a0d490c`, working tree clean. Nothing was written, staged
  or switched there. No model API was called. No heavy computation was run: only JSON and CSV
  lookups, plus arithmetic in my own scripts (`klv/shape.py`, `klv/wdiff.py` in this
  scratchpad). I read the redraft's `kl/build.py` and `kl/recount.py` to see its method, but
  did not run them.

**VERDICT: PASS WITH FIXES.** Every number in the fenced outcome reproduces from the committed
artefacts, apart from one inherited internal miscount. The word diff is complete and
truthful. The cause attributions match the re-score record. D51 does name tier E. One sentence
contradicts the corrected SHAPE clause, which is the same class of error as the earlier
"US$1,100-to-US$43,000" leftover. The new rise qualifier left the falls sentence beside it
unqualified. Merged on its own, the § 8.6 citation would point at findings text that
disagrees with it.

## 1. Every number in the redrafted outcome

"P1" is `results/k-ladder-2026-09-12/ladders.json` and "P2" is `phase2/ladders.json`. Paths
are under `results/k-ladder-2026-09-12/` unless they say otherwise. "Recomputed" means I
derived the value with my own code.

| # | Text figure | Source and key | Recomputed / found | Result |
|---|---|---|---|---|
| 1 | 23 ladders | P1 `n_ladders` 8 + P2 `n_ladders` 14 + tier E | 23 | OK |
| 2 | thirteen Gemini 3 families; seven 55-map ladders | P2 families; P1 minus the GS ladder | 13; 7 | OK |
| 3 | US$24.8065 | `phase2/spend-ledger.json` `total.flex_usd` | 24.8065 | OK |
| 4 | US$4.9595 | `tier-e/scores.json` `audited_flex_usd` | 4.9595 | OK |
| 5 | seven Phase 2 ladders clipped (3.7 + six) | P2 `summary[*].score_basis` | 7 `clip-to-common-assessed-area` | OK |
| 6 | 37 % to 93 % of the gain | P2 `share_at_k3` minimum (HIGH image T 0.3); P1 3.7 arm 1 oracle rows | 0.3718 to 0.9299 (either basis) | OK |
| 7 | 31 % to 62 % of top-rung cost | P2 `cost_share_at_k3` minimum; P1 3.7 arm 2 `cost.usd` K3 / K5 | 0.3149 to 0.6245 | OK |
| 8 | last step worst on 17 of 23 | own recount, best F1 per K, `cost.usd` / `all_in_flex_usd` / findings § 8.4 tier E costs (US$2.09 / 4.21 / 6.20 / 10.66, verified at findings line 1406) | 17. The same on the GS own and board frames, on both Phase 2 bases, and for tier E clipped or not | OK (see issue 9: the count depends on the fourth cell's board K = 5 rung) |
| 9 | the six exceptions | same recount | GS A, B r2, B std, fourth cell, MINIMAL image T 0.3, HIGH image T 1.0 | OK |
| 10 | about US$0.20 (GS stride A) | P1 GS K5 0.8937 / 3.8056 to K10 0.9075 / 6.5445 | US$0.198 (board frame US$0.200) | OK |
| 11 | to US$27 (3.7 arm 1) | P1 arm 1 K3 oracle 0.8705 / 94.3107 to K5 oracle 0.8727 / 153.1642 | US$26.75 | OK |
| 12 | five ladders lose F1 at the last step | recount | MINIMAL text T 0.3 and T 0.7, HIGH text T 0.3, HIGH image T 0.7, tier E (on both bases) | OK |
| 13 | +0.0004 for US$8.68, about US$22 | P2 3.7 rungs K5 / K10 `opmax.f1_20`, `all_in_flex_usd` | 0.9165 to 0.9169; US$8.6827; US$21.71 | OK |
| 14 | 7 of 7 HIGH, 2 of 6 MINIMAL | `phase2/mcc-test/summary.json` `f1_p_bh_k1_to_best`; P2 `thinking_level` (scale-4-optimal is high) | 7/7; 2/6 (T 1.0 text 0.0012, T 0.7 image 0.0006) | OK |
| 15 | four MINIMAL ladders in a single tier | committed tiering via `mcb/summary.json` `committed_tiering` | `n_tiers` 1 on MINIMAL text T 0.3 and T 0.7, image T 0.3 and T 1.0 | OK |
| 16 | text +0.0559 / +0.0735 / +0.0955 (+0.0994 as evaluated) | P2 `summary[*].gain`, `historical_as_evaluated.gain` | as quoted | OK |
| 17 | image +0.0780 / +0.0959 / +0.1514 | P2 `summary[*].gain` | as quoted | OK |
| 18 | 15 ladders; F1 rises on 15; tile-MCC falls on 10 | P1 8 + P2 7 not withheld; `mcc-test/summary.json` and P2 `mcc_verdict` | 15; 15; 5 + 5 = 10 | OK |
| 19 | as evaluated, falls on all six withheld (16 of 21) | P2 `historical_as_evaluated.tile_mcc`, K = 1 to best; `phase2/mcc-test/summary.json` | 6 of 6 down; 16 of 21 | OK |
| 20 | +0.0130 at BH p 0.7633 | `mcc-test/gs-stride-a.json` K1-vs-K10 `mcc.delta`, `p_bh`; MCB unrounded 0.794812 to 0.807855 | 0.013043; 0.76332 | OK (endpoint rounding gives +0.0131) |
| 21 | no significant rise from K = 1 to the best rung | `mcc-test/*.json`, `phase2/mcc-test/*.json`, K1-to-best pairs | none significant | OK |
| 22 | counter-example: 55-map stride A K5 to K10 +0.0047, BH p 0.0300 | `mcc-test/55map-stride-a-r2.json` and `-standardised.json` K5-vs-K10 | +0.004676 / +0.004684, p_bh 0.03, significant | OK |
| 23 | significant falls on four: −0.0112, −0.0099, −0.0275, −0.0637 (BH p 0.0420) | K1-to-best pairs | −0.011152, −0.009904, −0.027536, −0.063742 at 0.042 | OK for K = 1 to best. Across all pairs, six ladders have a significant fall (issue 2) |
| 24 | HIGH image T 1.0 has the largest F1 gain | P2 `summary.gain` | 0.1514 (next: 0.1307) | OK |
| 25 | 3 of 149 cells | `reports/tile-mcc-geometric-join-2026-09-12.md` line 208 | 3 of 149 | OK |
| 26 | 10,000 permutations, seed 42, BH q 0.05 | tier E and mcc-test metadata | as quoted | OK |
| 27 | 8 pairs, 2 ladders; all eight MCC calls agree; within 0.0006 | `mcc-test/sign-swap/ladder_pairs.json` against `mcc-test/55map-stride-{a,b}-*.json` | 8/8 agree; maximum gap 0.00052 | OK |
| 28 | F1 BH p 0.0079 against 0.0655 | `55map-stride-a-r2.json` K3-vs-K5 `f1.p_bh`; sign-swap N3-vs-N5 | 0.0079; 0.0655 | OK (inherited; the standardised ladder reads 0.0132) |
| 29 | 200 draws, seed 42; 197 / 200 at +0.0547; 39 / 200 at +0.0192; SD ~0.0114 | `tension/subsample.json` | 197 and 39; SDs 0.01162 and 0.011275 | OK |
| 30 | "about 0.03 and above" | interpretation of row 29 | — | UNCHECKED (judgement) |
| 31 | at or above +0.0546 separate, at or below +0.0223 do not | `tension/effect-sizes.json`, P2 / mcc-test p values | true at 487-tile resolution. 55-map stride A's +0.0192 separates on its full 8,541 tiles | OK (inherited; the sentence means 487 tiles) |
| 32 | deployment +0.0192..+0.0547 inside GS +0.0139..+0.0600 (+0.0629 as evaluated) | `tension/effect-sizes.json` `delta_f1`; P2 `historical_as_evaluated.gain` | as quoted | OK |
| 33 | K = 1 highest tile-MCC on 7 of 15; 13 of 22 in the MCB sets | `mcb/summary.json` `ladders[*].mcc.best_K == 1` | 13 = 7 + 5 + tier E | OK |
| 34 | 2.2x; +0.1441 / +0.0660; +0.0947 / +0.0425 | `tension/grid-overlap.json` `delta_f1_k1_to_k10`; `results/grid-2026-08-18/sweep.csv` (my own argmax) | 2.185 and 2.228; 0.144102 / 0.065954 / 0.094703 / 0.042509 | OK |
| 35 | tile-MCC rises +0.029..+0.132 | `grid-overlap.json` `delta_mcc_k1_to_best` | 0.029126 to 0.13208 | OK |
| 36 | 48.7 % (clipped) | 1 − (0.8942 − 0.860360) / 0.065954 | 48.69 % (48.73 % on micro-F1 0.894174) | OK. Findings § 8.6 prints 48.8 % from rounded gains (decision B) |
| 37 | 60.3 % (as evaluated) | 1 − (0.8942 − 0.868009) / 0.065954 | 60.29 % (60.33 % with 0.026165) | OK |
| 38 | +0.0660, +0.0444; 0.6633 / 0.4465 at K = 1, 0.7293 / 0.4909 at K = 10 | `sweep.csv` g384_ov192, best F1 per K (c ≥ 3, k ≥ 1; c ≥ 2, k ≥ 10) | 0.663304 / 0.446497; 0.729258 / 0.490858 | OK |
| 39 | 0.8604 at K = 1 clipped | `reports/scorer-frames-d50-d51-2026-10-08-scripts/out/ladders_new.json` `tier_e.rungs[0].points.opmax.d51_clipped.f1` | 0.860360 (29 removed) | OK |
| 40 | 0.8942 at K = 10 on the clipped basis | `tier-e/ladder.json` `rungs[3].f1_20` and `ladders_new.json` `clip.area_removed_km2["K = 10"]` 0.0 | inferred; no committed artefact holds a clipped K = 10 value | OK (inferred; issue 5) |
| 41 | +0.0338; +0.0262; 0.8680 | the same | 0.03384; 0.026191; 0.868009 | OK |
| 42 | −0.0238; 0.8211 / 0.7973 | `tier-e/ladder.json` `pairwise_mcc` K1 vs K10, `rungs` | 0.023837; 0.821093 / 0.797257 | OK |
| 43 | swing 0.0682 | 0.044361 + 0.023837 | 0.068198 | OK |
| 44 | MCC separates on none of tier E's six pairs | `tier-e/ladder.json` `n_significant_mcc` | 0 of 6 | OK |
| 45 | MCB: 22 ladders; 10,000 resamples, seed 42, m 1.0, 95 % | `mcb/summary.json` `instrument` | as quoted | OK |
| 46 | 44 runs, 170 rows, 4.958e-05 | `mcb/summary.json` `ladders[*].gates` | 44; 170; 4.958e-05 | OK |
| 47 | K = 3 admissible on 12, cheapest on 10 | `f1.hsu_admissible_K` | 12; 10 | OK |
| 48 | ten admit nothing below K = 5 (nine at K = 5, one at K = 10) | min of `f1.hsu_admissible_K` | partition 3:10, 1:2, 5:9, 10:1 (`55map-stride-b-g37vf-r2`); also 10 at `b7e2821ba` | OK |
| 49 | no F1 set excludes K = 10; twenty ladders have K = 10 | as above | 0; 20 | OK |
| 50 | K = 1 out on F1 on 20 of 22; MCC-admissible on 22 of 22 | as above | 20; 22 | OK |
| 51 | MCC set is the whole ladder on 13 of 22, F1 on 2 of 22 | as above | 13; 2 | OK |
| 52 | six of twenty exclude K = 10 on MCC; {K = 1} alone on two | as above | 6 (HIGH image T 0.7 and T 1.0, scale-4, both 55-map A, fourth cell); 2 (fourth cell, arm 2) | OK |
| 53 | w_upper 0.0159-0.0326 and 0.0047-0.0056, three to six times narrower | `f1.hsu_w_upper` | 0.015867 to 0.032625; 0.004681 to 0.005639; ratios 3.4 and 5.8 | OK |
| 54 | F1 set smaller than the tie set on two, larger on six | tie sets in the committed tiering against `f1.hsu_admissible_K` | 2 smaller (MINIMAL text T 0.3, image T 1.0); 6 larger | OK |
| 55 | two single-tier ladders admissible whole | `roll_up` | MINIMAL text T 0.7, image T 0.3 | OK |
| 56 | "three of its four rungs" refused; "two sound rungs of four" | `mcb/summary.json` `withheld`: `n_rungs_withheld` 2, three cells | three cells on two rungs | **MISMATCH** (inherited, internal; issue 8a) |
| 57 | k = 1/3/4/8 at K = 1/3/5/10; stride A carried 3/4/8; others k = K | P1 `vote_threshold` | as quoted | OK |
| 58 | "the five non-separating ladders" | count, K = 1 to best, MCC | 11 of the 15; 17 of 21 as evaluated ("five" is findings § 4.1's Phase 1 frame) | **MISMATCH** in this text's frame (inherited; issue 8b) |
| 59 | signed "13 of 21" was 12 of 21 (dated clause, redraft § 4.4) | `git show b7e2821ba:…/mcb/summary.json` | best K = 1 on 13 including tier E; 12 without | OK |

## 2. The word diff (check 2)

I diffed the fenced text, joined into one line, against `results/run-analyses.json` →
`k-ladder-2026-09-12` → `outcome` at token level with my own script (`klv/wdiff.py`). There are
54 hunks. Every one appears in § 2, and every changed figure appears in § 3. No unlisted
sentence changed. The fenced text is byte-identical, after whitespace normalisation, to
`kl/redraft.txt`. The redraft's `kl/register.txt` equals the live register outcome. Small
wording carried with the listed changes ("RISE;" → "RISE … , and"; "3.7 family" → "3.7
gold-standard family") are visible in § 2. **PASS.**

## 3. Issues, most important first

### 1. "only never worth its price" contradicts the corrected SHAPE clause (must fix)

The MCB paragraph ON THE LAST STEP still reads: "so the top rung is never statistically ruled
out, only never worth its price, which is the formal counterpart of the last-step prices per
0.001 F1 under SHAPE above". SHAPE now says the last step is not the worst buy on six of 23
ladders. On gold-standard stride A it costs about US$0.20 per 0.001 F1, its cheapest step after
K = 1 → 3. On HIGH image T 1.0 it is cheaper than the K = 3 → 5 step. "Never worth its price"
was the signed sentence's companion to "worst buy on every ladder", which D25 corrected. This
is the same class of error as the "US$1,100-to-US$43,000" leftover the earlier verifier
caught: the redraft corrected the second half of the sentence and kept the first.

*Fix*: "… so the top rung is never statistically ruled out; whether it is worth its price is
the cost question SHAPE above prices (about US$0.20 to US$27 per 0.001 F1 where it gains F1,
and a loss on five ladders)".

### 2. The new rise qualifier leaves the falls sentence beside it unqualified (should fix)

"NO ladder shows a significant tile-MCC RISE from K = 1 to its best rung … Significant FALLS
are found on four ladders". The four falls are the K = 1 → best falls. Counting every tested
pair, six ladders show a significant fall: both 55-map stride A ladders' K = 3 → 5 step,
−0.011052 at BH p 0.0066 (`mcc-test/55map-stride-a-r2.json`, `-standardised.json`). Findings
§ 4.1 item 4 records it. The redraft justified the qualifier because the unqualified rise
sentence was false of those same ladders. The falls sentence needs the same frame.

*Fix*: "Significant FALLS from K = 1 to the best rung are found on four ladders — …".

### 3. Stale on arrival: the outcome and findings § 8.6 disagree until findings is revised (merge blocker)

The outcome says "absorbs about half … 48.7 % …" and cites "§ 8.6". Findings § 8.6 at
`e3a0d490c` has the heading "the verifier absorbs about 60 % of K's F1 return", leads with
60.3 %, and prints the clipped share as 48.8 % (line 1551). It also calls the clipped reading
one "the PI has not yet applied" to tier E. The redraft's § 5 A and B list this. It should be
a hard condition: whatever the PI decides, findings §§ 8.4 and 8.6 must change in the same PR
as the register text, or the citation points at a contradiction. The same applies to findings
§ 6.1 line 848 ("on nine ladders a K = 3 rung can be ruled out", which should be ten) and
`reports/k-ladder-mcb-deltas-2026-09-13.md` line 96.

### 4. Decision A's "like-for-like" argument is overstated (fix before the PI reads § 4.6 and § 5 A)

Redraft § 4.6 argues that the clipped tier E reading is like-for-like with the consensus-only
gain, because the grid study scores on the same 1,364.47 km² common footprint. The area
matches, but the reference sets do not:

- The consensus-only side is scored against 428 reference mounds
  (`results/grid-2026-08-18/grid_analysis.json` `scope.footprint_audit.common_ground_truth`
  428). `sweep.csv`'s g384_ov192 rows imply TP / recall = 428.0 at both K = 1 and K = 10.
- D51 keeps the frame's 435 references. On the clipped basis every tier E rung therefore
  carries 7 misses it cannot reach (`ladders_new.json`: clipped TP / recall = 435.0 on every
  rung).

The § 4.6 sentence "Unclipped, the K = 10 rung is charged with misses in a band it never
searched" also misstates the mechanism. Clipped, every rung is charged with those 7 misses.
What the clip changes is that K = 1, 3 and 5 lose credit for finds in a band K = 10 never
searched.

The recommendation can still rest on D51's text. The "measured fact" paragraph should say
that the areas match and the reference sets do not (428 against 435), so neither tier E
reading is exactly the consensus side's basis.

### 5. Anchor and provenance of the clipped share (should fix)

The 48.7 % rests on a clipped K = 10 value of 0.8942 that no committed artefact holds. The
redraft's § 4.7 and the restatement record's § 10 item 3 both say so. The outcome's anchor
for the clipped basis is `ladders_new.json`, which predates the 2026-10-13 re-verification.
Its tier E K = 10 row reads 0.8886 (d50 = d51), so a reader who follows the anchor gets a
clipped gain of 0.0283 and a share of 57.1 %, not 48.7 %.

*Fix*: in the parenthesis, say "(K = 1 from ladders_new.json, 2026-10-08, which predates the
re-verification; its K = 10 row is superseded by tier-e/ladder.json's 0.8942, whose union lies
wholly in the common area)". Better still, commit a clipped tier E reading before re-signing,
which is the redraft's decision C, Option 3.

### 6. The definition of "the 15" also fits tier E (should fix)

"the 15 verified ladders whose tile-MCC the restated tables report" also describes tier E:
`tier-e/ladder.json` reports its tile-MCC, and this same text uses it in § 8.6 (0.8211 →
0.7973). Tier E is in neither the 15 nor the 21. The parenthetical list is right, but the
defining clause is not.

*Fix*: "Across the 15 verified ladders of findings § 4 whose tile-MCC the restated tables
report (…; tier E is tested separately, § 8.4)".

### 7. The dated clause's disclosure is incomplete (should fix)

The clause discloses "two counts that were wrong from first publication". The redraft also
narrows a sentence that was false as worded at signing: the unqualified "NO ladder shows a
significant tile-MCC RISE". Both 55-map stride A ladders' K = 5 → 10 rise was in findings
§ 4.1 item 4, dated 2026-09-12.

*Fix*: append "…, and narrows one sentence to what was tested (no significant tile-MCC rise
from K = 1 to the best rung)".

### 8. Inherited errors in unchanged sentences (fix now, while the row is being re-signed)

- **(a) WITHHELD.** The text says "refuses the per-tile table of three of its four rungs …
  leaving two sound rungs of four". Three refused out of four would leave one.
  `mcb/summary.json` `withheld` records `n_rungs_withheld` 2: three cells, namely K = 1
  opmax, K = 1 carried and K = 3 opmax. *Fix*: "refuses the per-tile table of three cells on
  two of its four rungs (K = 1 and K = 3) …".
- **(b) NOT CLAIMED.** "the five non-separating ladders' MCC moves are not shown to be zero":
  "five" is findings § 4.1's eight-ladder Phase 1 frame. In this text's frame, 11 of the 15
  (17 of the 21 as evaluated) do not separate from K = 1 to the best rung. *Fix*: "the
  non-separating ladders' MCC moves …".
- **(c) Unmarked as-evaluated results.** The dated clause promises that unclipped figures are
  "marked 'as evaluated'". Two results come from as-evaluated tests on clipped ladders and are
  unmarked: "greedy-clique into a SINGLE tier" (MINIMAL text T 0.3, image T 0.3 and T 1.0 are
  clipped) and "every one at or above +0.0546 separates" (MINIMAL image T 0.7's test is at
  +0.0629). *Fix*: move "(tested on the cells as evaluated)" so it covers the whole
  significance-and-tier sentence, and add "as evaluated" after "separates".

### 9. Readability (check 6)

- "the basis D51's text extends to tier E" reads as an argument addressed to the PI. Once
  decision A is taken, replace it with "(D51)".
- The § 8.6 parenthesis is about 75 words, with two bases and a file path, so an outside
  reader loses the main clause. Split it into a separate sentence: "On the clipped basis …;
  as evaluated …; tile-MCC exists only as evaluated."
- "the sheet-scoped scorer (D50)" needs a gloss, for example: "the scorer now credits each
  detection only on its own map sheet (D50)".
- "(K = 1's highest-tile-MCC count, and the ladders admitting nothing below K = 5)" uses the
  MCB's language before MCB is introduced. Suggest "(how often K = 1 has the highest
  tile-MCC, and how many ladders' best-rung sets start at K = 5 or above)".
- One ladder has six names: "3.7 gold-standard text screen", "3.7 gold-standard ladder",
  "the 3.7 ladder", "the 3.7 screen", "3.7 gold-standard family" and "3.7 gold-standard text
  family". Pick one, for example "the 3.7 gold-standard text ladder".
- **The fourth cell's K = 5 rung.** SHAPE's "on the other six … the K = 3 -> 5 step is worse"
  uses the board's FOURTH-N5 cell (0.8758, US$116.15; findings §§ 3.3 and 5). `ladders.json`
  and the MCB ladder (`{1, 3, 10}`) do not have that rung. Without it the fourth cell's last
  step, K = 3 → 10 at US$17.69 per 0.001 F1, is its dearest, and the count would be 18 of 23.
  D25 approved 17 with this rung, so this is a disclosure, not an error. Suggest a few words:
  "(the fourth cell's K = 5 rung is the board cell of findings § 3.3)".
- The 3.7 family's "about US$22 per 0.001 F1" now falls inside the US$0.20-to-US$27 range,
  so the reason for singling it out is gone. Either drop it or add "(no longer the corpus's
  dearest last step)".
- The six clipped Gemini 3 ladders' clip rests on D57 (2) and D57 (3). The dated clause cites
  only D57 (2).
- **Stale-on-arrival scan.** The fenced text contains no "draft", "pending", "PR #", branch
  name or commit hash. Every path it cites exists on `origin/main`. The tile-join sentence
  ("a corpus-wide decision with the PI") is still accurate: no ruling exists, and
  `mcb/summary.json` `withheld.lifted_by` says "still open with the PI". The only
  stale-on-arrival risk is issue 3.

## 4. Bases (check 3)

Every count states its basis, apart from the two unmarked results in issue 8c:

- **The 15 / 10 and 7-of-15 counts** are on the restated (clipped D51) tables, with the six
  clipped ladders excluded.
- **16 of 21 and 13 of 22** are marked as evaluated.
- **The MCB counts** have a blanket statement that they are computed on the as-evaluated
  cells.
- **The SHAPE counts** (17 of 23, five losses, 37-93 %, 31-62 %) come out the same on either
  basis. My recount checked both.

The § 8.6 clause pairs a clipped F1 gain with an as-evaluated MCC fall and says so. Its swing
mixes the grid's common-footprint MCC with tier E's unclipped MCC, which is disclosed as "no
clipped tile-MCC exists" (see also issue 4 on the reference sets).

## 5. Cause attribution in the dated clause (check 4)

Against `reports/s164-agent-records/rescore-repaired-gs.md` § 3.2 (COMMITTED → ORIGIN →
REPAIRED) and `restatement-pass.md` §§ 1.4 and 2.3, every named cause is right:

- **Origin route ("scored on the tiles it was seen on").** The consensus-only ladders move at
  ORIGIN, for example +0.0572 → +0.0660 (0.7205 → 0.7293). GS stride A does not move at
  ORIGIN.
- **Re-verification on own-sheet crops.** Every GS stride A rung moves only at REPAIRED (0.8605
  / 0.8834 / 0.8782 / 0.8905 = ORIGIN → 0.8665 / 0.8916 / 0.8862 / 0.8999). So do tier E's
  K = 10 (0.8886 → 0.8942) and the 3.7 ladder's K = 5 and K = 10 (0.9066 / 0.9068 → 0.9165 /
  0.9169).
- **D50 scorer.** Tier E's K = 1, 3 and 5 move at ORIGIN, matching D65's S9 list of eight
  cells. So do the 3.7 ladder's K = 1 and K = 3 (also in D50's own text).
- **D51 clip.** It covers the seven Phase 2 ladders (P2 `score_basis`). Tier E's F1 gain is
  the redraft's proposal (decision A), not something the restatement pass did; the clause
  says "now compared", which is accurate only if decision A takes Option 1.

## 6. Does D51 decide tier E's basis? (check 5)

**Yes, as recorded.** `planning/pi-decisions-2026-09-20.md` line 75, D51 (RULED 2026-10-07):
"where rungs' candidate pools cover different areas … the larger-area rungs are clipped to the
common area and the frame's reference set is kept. The 3.7 GS ladder reads 0.8682 / 0.9073 /
0.9066 / 0.9068 (K = 1/3/5/10; gain +0.0386, not +0.0573); **the tier E ladder takes the same
rule**."

Nuances:

- These are the decisions log's summary words for option 1. The PI's quoted words ("with only
  7 mounds in question, we can go with option 1; please do generalise this …") do not name
  tier E. The option put to him did place tier E's K = 10 rung in the same universe question
  (`reports/frames-blast-radius-2026-10-07.md` line 519: "Tier E's K = 10 rung likewise").
- No later ruling narrows it. Tier E appears only in D50, D51 and D65's S9 note, and D67 (5)
  rules on the 3.7 ladder alone.
- The restatement pass chose the unclipped reading because of its brief (`restatement-pass.md`
  § 1.4; § 10 item 3, which leaves it for the PI). The redraft's § 4.6 is therefore correct
  on the ruling. Its supporting "like-for-like" paragraph needs issue 4's correction.

## 7. Internal consistency (check 7)

Apart from issue 1 ("never worth its price" against the corrected SHAPE) and issue 2 (the
asymmetric qualifier), I found no sentence that contradicts another:

- No old figure survives in the fenced text. I grepped for each of the lapse note's "STALE"
  figures: zero hits.
- "every ladder" survives once, correctly ("K = 3 is on the efficient set of every ladder").
- The inherited miscounts in 8a and 8b are internal to their own sentences.

## 8. Spot-checks of the redraft's § 6 (attestation corrections)

- **Items 1, 2 and 4 are correct.** `62050794d` rebuilt `tension/effect-sizes.json`
  (MINIMAL image T 0.7 at 0.06; `n_withheld` 5). `de998a94d` restated `findings.md`. Findings
  prints +0.0131 at lines 104, 382 and 522.
- **Item 3 is correct.** Both `b7e2821ba` and `718d0ee08` give 13 including tier E, and 12
  of 21 without it.
- **Item 8 is correct.** Ten at `b7e2821ba`.
