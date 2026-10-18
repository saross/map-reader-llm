# Redraft of the register outcome `k-ladder-2026-09-12`, version 3 (PR #52, § 4.12)

- **Drafter**: Claude (Anthropic), Claude Code, model lane Opus 5.5 (`claude-opus-5-5`),
  read-only sub-agent.
- **Date**: 2026-10-18.
- **Read from**: `/home/shawn/worktrees/map-reader-llm/claude-pr52-restate`, branch
  `restatement-pass-s164`, head `062f92239`, working tree clean. The `k-ladder-2026-09-12`
  register row, `findings.md` and the MCB deltas report are byte-identical at `e3a0d490c`
  (version 1), `c24d5a04f` and `062f92239`. Since version 2, `restatement-pass.md` has changed
  only in its banner, § 1.3, § 5 item 9 and changelog (a board-membership correction, D69).
  That shifts its line numbers, so it is cited here by section. Nothing in the worktree was written, staged or switched. No model
  API was called and no heavy computation was run.
- **Brief**: Astra's (GPT, Codex) cross-model review of version 2 at `26deb34a3`, verdict PASS
  WITH FIXES (`~/agent-mail/codex/outbox/claude/20261018T064500.000000Z-codex-k-ladder-restatement-review.md`).
  Version 2 as committed at `26deb34a3` is byte-identical to the scratchpad version 2, so
  Astra's line numbers apply to it. § 8 maps each of Astra's five items to its fix.
- **Method**: as before, the outcome is built mechanically from the CURRENT REGISTER outcome by
  25 exact replacements, each asserted to match the signed text once (`kl3/build3.py`), so
  every sentence not listed in § 3 is byte-identical to the signed text. Decision A's Option 2
  text is built from the same list by four checked swaps (`kl3/build3_opt2.py`). The companion
  edits in § 7 were applied to scratch copies of the committed files and linted with the
  repository's markdownlint config (`kl3/companion3.py`; edited copies in
  `kl3/comp/option-{1,2}/`). Recounts: `kl/recount.py`, unchanged.
- **Length**: the signed text has 1,853 words, version 2 had 2,832 and version 3 has 2,981.
  The increase is the requested reader aids: a 104-word plain-language lead and 59 words of
  definitions. Without them, version 3's audit text is 2,818 words, 14 fewer than version 2's
  (§ 4.12).

## 1. The redrafted outcome (decision A, Option 1: clipped leads)

```text
The pass-count ladder K (K is the number of detection passes whose
candidates are pooled before verification) at otherwise fixed
parameters, on 23 ladders: the gold-standard stride A ladder (the only
one whose every rung is an exact re-verification of its own first-N
union), the thirteen Gemini 3 pv-diag-384 families and the Gemini 3.7
gold-standard text ladder that Phase 2 completed to four rungs for
US$24.8065, the grid 384 px / 50 % MINIMAL text ladder tier E completed
for US$4.9595, and the seven 55-map deployment ladders. Restated
2026-10-15 (D62 (1), D50, D51, D57 (2) and (3), D65 (2), D67 (5)): each
consensus cluster is now scored on the tiles it was seen on, which moves
the grid study's consensus-only ladders; candidates the verifier had
been shown on crops cut from the neighbouring map sheet, largely blank,
were re-verified on crops from their own sheet (2026-10-13), which moves
every rung of the gold-standard stride A ladder, tier E's K = 10 rung
and the 3.7 gold-standard text ladder's K = 5 and K = 10 rungs; the
scorer now scores each detection on the map sheet it was found on (D50),
which moves tier E's K = 1, 3 and 5 rungs and the 3.7 gold-standard text
ladder's K = 1 and K = 3; and seven Phase 2 ladders (the 3.7
gold-standard text ladder and six Gemini 3 ladders), and tier E's gain
in F1 (the detection score, combining precision and recall; F1@20 counts
a match within 20 m), are now compared on the area every rung searched
(D51), a basis on which no tile-MCC (the Matthews correlation
coefficient over map tiles, which scores how well tiles with and without
a mound are told apart) has been computed, so the seven ladders'
tile-MCC is withheld; figures on the earlier, unclipped basis are marked
'as evaluated'. No verdict moved; the reduction in K's F1 gain after
verification changes size. The text also carries the re-pricing and
corrections the PI approved on 2026-10-04 (the second under D25), and
corrects statements that were wrong or too broad from first publication:
two counts (K = 1's highest-tile-MCC count; ten ladders, not nine, on
which every rung below K = 5 is ruled out as the best), the tile-MCC
rise and fall statements (now limited to K = 1 against the best rung,
the comparison tested), the tile-MCC Pareto reading (a cost preference,
not a statistical exclusion of larger rungs) and the 487-tile resolution
(two detection rates, not a threshold). IN BRIEF: this row asks what
extra detection passes buy. Much of the F1 gain comes from the first
three passes, the last step up a ladder is usually the poorest buy, and
how much extra passes help depends mainly on the proposer's thinking
level and temperature. Extra passes never significantly improve tile-MCC
over a single pass, and it falls on most ladders; on the one pool tested
with and without the verifier, verification cut the F1 gain from extra
passes by about half to three-fifths, depending on the scoring basis,
and, on the cells as evaluated, turned their tile-MCC gain into a loss.
SHAPE: the return is FRONT-LOADED and K = 3 is on the efficient set of
every ladder in the corpus (a rung is efficient when no cheaper rung of
the same ladder scores as well) — 37 % to 93 % of a ladder's total F1
gain for 31 % to 62 % of its top rung's cost — while the last step (K =
5 -> 10, or K = 3 -> 5 on the two 55-map 3.7 arms, which have no K = 10
rung) is the worst buy, the dearest per 0.001 F1 or a loss of F1, on 17
of the 23 ladders; on the other six (the gold-standard stride A ladder,
the two 55-map stride B ladders under the Gemini 3 verifier, stride B
under the 3.7 verifier, MINIMAL image T 0.3 and HIGH image T 1.0) the K
= 3 -> 5 step is worse. (The 17 counts stride B under the 3.7 verifier
with its K = 5 rung, a 55-map board cell, findings § 3.3, that the
ladder inventory lacks; without it, 18.) Where the last step gains F1 it
costs about US$0.20 (gold-standard stride A) to US$27 (55-map 3.7 arm 1)
per 0.001 F1 gained; on five ladders it loses F1 (MINIMAL text T 0.3 and
T 0.7, HIGH text T 0.3, HIGH image T 0.7, and tier E); the 3.7
gold-standard text ladder's K = 5 -> K = 10 step, for example, buys
+0.0004 F1@20 for US$8.68. WHAT GOVERNS THE RETURN: the proposer's
thinking level, and within a level its temperature. The K = 1 ->
best-rung F1 gain is significant on 7 of 7 HIGH-thinking ladders and 2
of 6 MINIMAL ones, and four ladders, every one of them MINIMAL,
greedy-clique into a SINGLE tier in which K buys nothing detectable
(both tested on the cells as evaluated); and on both HIGH tracks the
gain rises monotonically with temperature (text +0.0559 -> +0.0735 ->
+0.0955, image +0.0780 -> +0.0959 -> +0.1514 across T 0.3 -> 0.7 -> 1.0;
text T 1.0's +0.0955 is on D51's clipped basis, +0.0994 as evaluated).
Read as the diversity dividend (Obs 141) measured on a K ladder: K buys
sampling diversity, and pays in proportion to how much the configuration
already generates. TILE-MCC DOES NOT FOLLOW F1. Across the 15 verified
ladders of findings §§ 4 and 4.3 whose tile-MCC the restated tables
report (the gold-standard stride A ladder, the seven 55-map ladders, and
seven of the thirteen Gemini 3 Phase 2 ladders; the other six are on
D51's clipped basis, where tile-MCC is withheld, and tier E is tested
separately, § 8.4), F1 rises on all 15 and tile-MCC falls on 10, and as
evaluated it falls on all six withheld ladders too (16 of 21); NO ladder
shows a significant tile-MCC RISE from K = 1 to its best rung, and the
gold-standard ladder's +0.0130, § 4 of the findings' one apparent
counter-example, tests at BH p = 0.7633 (BH: a p value adjusted for
multiple comparisons by the Benjamini-Hochberg procedure). Significant
FALLS from K = 1 to the best rung are found on four ladders — the
3.7-verifier stride B (-0.0112), 3.7 arm 1 (-0.0099), 3.7 arm 2
(-0.0275) and HIGH image T 1.0 (-0.0637, BH p = 0.0420, the family with
the largest F1 gain). Between intermediate rungs, both 55-map stride A
ladders fall significantly from K = 3 to K = 5 (-0.0111, BH p = 0.0066)
and rise significantly from K = 5 to K = 10 (+0.0047, BH p = 0.0300), so
over every tested pair six ladders show a significant fall and two a
significant rise. More passes buy localisation inside already-positive
tiles, not tile-level discrimination, which matters for any application
whose unit is the tile rather than the mound. CAVEAT on the MCC column:
tile-MCC is computed by a string join on source_tile, and three cells of
the 3.7 gold-standard text ladder are scored on a frame whose tile
vocabulary is not their proposer's, so their tile-MCC is WITHHELD with a
named reason rather than reported (g37-text-k1-verified-opmax,
g37-text-k1-verified-carried-p0.10-k1, g37-text-k3-verified-opmax; the
regenerated tables no longer record a raw value). The corpus-wide
exposure is measured at 3 of 149 committed cells the Era-2 board reads,
no published board MCC is affected, and the repair is a corpus-wide
decision with the PI because the 384 px frames overlap
(reports/tile-mcc-geometric-join-2026-09-12.md). Their F1 is sound and
is reported in full. INSTRUMENT (PI ruling): the board's round-robin
tile-swap micro-F1 permutation is THE instrument — 10,000 permutations,
seed 42, BH q = 0.05 within each ladder's own round-robin, tile-MCC
swapped on byte-identical masks so a ΔF1 and a ΔMCC are two statistics
of one permutation — and the registered per-map paired sign-swap is the
CROSS-CHECK. Where both cover a pair (8 pairs, 2 ladders) all eight
tile-MCC significance calls AGREE, with ΔMCC estimates within 0.0006;
one marginal F1 call differs (stride A's K = 3 -> 5, BH p 0.0079 against
0.0655), so the instrument choice is live for marginal F1 claims and
immaterial to the MCC conclusion. THE TWO CORPORA AGREE once resolution
is accounted for. The deployment MINIMAL ladders' own cells, scored on
random 487-tile subsets of their own 8,541 tiles (200 draws, seed 42,
same instrument), keep BH significance in 197 of 200 draws at ΔF1
+0.0547 and in only 39 of 200 at +0.0192 — a subsampling standard
deviation of ~0.0114 either way: detection rates for two effects, not a
threshold (+0.0192 separates on all 8,541 tiles). On the gold-standard
ladders, as evaluated, every MINIMAL gain at or above +0.0546 separates
and every one at or below +0.0223 does not, while +0.0338 separates and
+0.0384 (BH p = 0.1236) does not; and the deployment range
+0.0192..+0.0547 sits INSIDE the gold-standard range +0.0139..+0.0600
(+0.0629 as evaluated). So 'K buys nothing detectable' on four MINIMAL
configurations is a statement about 487 tiles, not about K. PARETO MCC
SET: K = 1 is the cheapest member of every tile-MCC set of multiple
comparisons with the best (MCB, below), holds the highest tile-MCC on 7
of the 15 ladders above, and no K = 1 -> best-rung comparison shows a
significant MCC gain, so it is the cost-conscious choice for tile-level
discrimination when the rule is to take the cheapest rung not ruled out
as best; larger rungs are not excluded (the MCB admits one on 20 of 22
ladders). For F1, K = 3 is on every ladder's observed cost frontier but
is the cheapest MCB-admissible rung on only 10 of 22. The two objectives
favour different rungs, and that is the review's practical finding. A
GEOMETRY EFFECT, consensus-only: at fixed MINIMAL text T 0.7 the grid
study's K = 1 -> 10 gain is about 2.2x larger at 12.5 % overlap than at
50 % (+0.1441 against +0.0660 at 384 px; +0.0947 against +0.0425 at 512
px), and tile-MCC RISES with K on all four consensus-only cells
(+0.029..+0.132) — the opposite of the verified ladders, consistent with
the same mechanism. Overlap and pass count buy the same redundancy. The
pattern does not survive to the verified deployment ladders, which order
the other way. THE VERIFIER STAGE REVERSES tile-MCC's RESPONSE TO K, on
the cells as evaluated, and roughly halves K's observed F1 gain: 48.7 %
smaller with tier E's rungs compared on the area every rung searched
(D51), 60.3 % smaller as evaluated (§ 8.6, added on the PI's ruling
2026-09-13). On ONE pool and ONE geometry — the grid study's 384 px / 50
% B-geometry MINIMAL text pool, which is the deployment stride-B tiling
at gold-standard scale — K = 1 -> 10 raises F1@20 by +0.0660 with
tile-MCC RISING +0.0444 consensus-only
(results/grid-2026-08-18/sweep.csv, cell g384_ov192, best F1@20 per K
over the corroboration x vote grid: 0.6633/0.4465 at K = 1,
0.7293/0.4909 at K = 10), and raises F1@20 by only +0.0338 with tile-MCC
FALLING -0.0238 (as evaluated) once the same pool is verified. The
clipped F1@20 is 0.8604 at K = 1
(reports/scorer-frames-d50-d51-2026-10-08-scripts/out/ladders_new.json)
and 0.8942 at K = 10, the restated rung of tier-e/ladder.json, whose
union lies wholly in the common area so the clip removes nothing (that
file's own K = 10 row, 0.8886, predates the re-verification); as
evaluated, K = 1 reads 0.8680 and the gain is +0.0262. Tile-MCC (0.8211
at K = 1, 0.7973 at K = 10; tier-e/ladder.json and each rung's
evaluation) exists only as evaluated; clipped tile-MCC has not been
computed, so its sign and magnitude are unknown. The two stages share
the common footprint but not the reference set: the consensus-only side
is scored against the 428 mounds inside it, tier E against the frame's
435 (D51), 7 of which lie outside the clipped area. So, on these scoring
bases, the observed F1 gain from extra passes is 48.7 % smaller once the
pool is verified (one minus the ratio of the two gains, on unrounded
values; 60.3 % as evaluated), and on the cells as evaluated a tile-level
GAIN becomes a tile-level LOSS, a swing of 0.0682 MCC. This is
consistent with the mechanism proposed for the TILE-MCC DOES NOT FOLLOW
F1 finding above (the verifier was already removing much of what extra
passes remove) but does not measure it directly: on this pool,
tile-MCC's response to K depends on the PIPELINE STAGE, not on K alone.
Its limits are stated with it: one geometry, one thinking level, one
temperature, one modality, one corpus, and the ladder's own DMCC steps
are not individually significant (tile-MCC separates on none of its six
pairs), so the claim is about the sign and size of the shift BETWEEN
stages. NOT CLAIMED: no MCC RANKING of rungs, tiering stays on the
preregistered F1; and the MCC moves of the ladders whose K = 1 ->
best-rung change does not separate (11 of the 15; 17 of 21 as evaluated)
are not shown to be zero. HSU MCB ADMISSIBLE SETS (the rungs that cannot
be ruled out as their ladder's best; PI ruling 2026-09-13, 'wait for the
sets'): the review's last outstanding run-card requirement is supplied
for all 22 tiered ladders, on F1 at each ladder's own headline buffer
and on tile-MCC, with the Era-2 board's own MCB step verbatim
(scripts/selection_aware_intervals.py --board; Hsu's constrained
one-sided form on theta_i = stat_i - max_{j != i} stat_j, critical value
bootstrapped over 10,000 tile resamples, seed 42, m-out-of-n 1.0,
simultaneous 95 %), each ladder on its own frame and reference, driven
by scripts/k_ladder_mcb.py and gated on all 44 runs against the
committed tiering ranking (170 candidate rows, max abs delta 4.958e-05,
results/k-ladder-2026-09-12/mcb/summary.json). The sets are computed on
the cells as evaluated, so every MCB count below includes tier E and the
six Gemini 3 ladders whose tile-MCC the clipped basis withholds above;
that basis has no per-tile table to compute them on. ON THE SHAPE
FINDING: K = 3 is admissible on 12 of the 22 ladders and is the CHEAPEST
admissible rung on 10 of them, so the front-loaded Pareto reading is
endorsed by the simultaneous instrument on roughly half the corpus and
declined on the other half — on ten ladders nothing below K = 5 is
admissible (on nine the cheapest admissible rung is K = 5; on 55-map
stride B under the 3.7 verifier only K = 10 is) even though K = 3
remains the efficient buy, which makes 'K = 3 is on the efficient set' a
cost claim rather than a statistical one. ON THE LAST STEP: NO ladder's
F1-admissible set excludes K = 10 — all twenty ladders that have a K =
10 rung admit it — so the top rung is never statistically ruled out, and
whether it is worth its price is the cost question SHAPE above answers:
the last step is the worst buy on 17 of the 23 ladders, not on all. ON
THE TWO OBJECTIVES: K = 1 is ruled out on F1 on 20 of 22 ladders and is
admissible on tile-MCC on 22 of 22, holding the highest tile-MCC on 13
of them, so the simultaneous instrument agrees with the pairwise tests
that K = 1 is never ruled out on tile-MCC, while on F1 it almost always
is. ON TILE-MCC'S RESOLUTION: the MCC-admissible set is the WHOLE ladder
on 13 of 22 against 2 of 22 on F1 — the same weak resolution the
permutation arm found — but where it resolves it resolves against K: six
of the twenty ladders with a K = 10 rung exclude it on tile-MCC, and on
two (55-map stride B under the 3.7 verifier, and 3.7 arm 2) the
MCC-admissible set is {K = 1} alone. ON RESOLUTION GENERALLY: the
simultaneous F1 width w_upper is 0.0159-0.0326 on the 487-tile gold
standard and 0.0047-0.0056 on the 8,541-tile deployment corpus, three to
six times narrower, which is the tension analysis's resolution result in
the MCB's own units. INSTRUMENT DISAGREEMENT, FLAGGED: the admissible
set and the committed greedy-clique tie set differ in BOTH directions
(F1 set smaller than the tie set on two ladders, larger on six), exactly
as erratum E83 and defect D20 warn; of the four MINIMAL ladders that
greedy-clique into a SINGLE tier, only two are admissible whole, since
MINIMAL text T 0.3 and MINIMAL image T 1.0 both rule K = 1 out as best.
The single-tier statement stands as a within-ladder pairwise BH result
and is not withdrawn, but 'one tier' is not 'every rung could be the
best one'. WITHHELD: the 3.7 gold-standard text ladder has NO admissible
set on either metric, because the tile-join invariant refuses the
per-tile table of three cells on two of its four rungs (K = 1 and K = 3)
on this frame and the refusal falls on the F1 arm as well as the MCC
arm, leaving two sound rungs of four; its whole-frame F1 is unaffected
and reported in full. CARRIED CONVENTION (PI ruling 2026-09-13): the
gold-standard stride ladder's own vote shell (k = 1/3/4/8 at K =
1/3/5/10) is THE carried point and ruling R2's literal k = K stays as a
disclosed column; no number was recomputed, the two readings coincide at
K <= 3, and both stay committed in phase2/committed-carried/scores.json.
Reading that ruling back against the 55-map tables disclosed something
nothing had recorded: stride A's committed carried cells are the stride
shell (k = 3/4/8) while stride B's, stride B's 3.7-verifier cell and
both 3.7 arms' are k = K, so the transfer taxes of findings sections
3.2, 3.3 and 3.4 are k = K taxes and are an UPPER BOUND on the transfer
cost (each cell's vote_threshold in results/run-conditions.json;
findings section 3's disclosure table). MCB artefacts:
results/k-ladder-2026-09-12/mcb/; deltas
reports/k-ladder-mcb-deltas-2026-09-13.md. Findings:
results/k-ladder-2026-09-12/findings.md (all sections); tension analyses
results/k-ladder-2026-09-12/tension/; spend
reports/k-ladder-phase2-deltas-2026-09-12.md and
results/k-ladder-2026-09-12/tier-e/.
```

## 2. Word diff against the signed register outcome

Against `results/run-analyses.json` → `k-ladder-2026-09-12` → `outcome` at `062f92239` (unchanged since signing). `[-removed-]{+added+}`, token level.

```text
The pass-count ladder K {+(K is the number of detection passes whose
candidates are pooled before verification)+} at otherwise fixed
parameters, on 23 ladders: the gold-standard stride A ladder (the only
one whose every rung is an exact re-verification of its own first-N
union), the thirteen Gemini 3 pv-diag-384 families and the {+Gemini+}
3.7 gold-standard text [-screen-] {+ladder+} that Phase 2 completed to
four rungs for US$24.8065, the grid 384 px / 50 % MINIMAL text ladder
tier E completed for US$4.9595, and the seven 55-map deployment ladders.
{+Restated 2026-10-15 (D62 (1), D50, D51, D57 (2) and (3), D65 (2), D67
(5)): each consensus cluster is now scored on the tiles it was seen on,
which moves the grid study's consensus-only ladders; candidates the
verifier had been shown on crops cut from the neighbouring map sheet,
largely blank, were re-verified on crops from their own sheet
(2026-10-13), which moves every rung of the gold-standard stride A
ladder, tier E's K = 10 rung and the 3.7 gold-standard text ladder's K =
5 and K = 10 rungs; the scorer now scores each detection on the map
sheet it was found on (D50), which moves tier E's K = 1, 3 and 5 rungs
and the 3.7 gold-standard text ladder's K = 1 and K = 3; and seven Phase
2 ladders (the 3.7 gold-standard text ladder and six Gemini 3 ladders),
and tier E's gain in F1 (the detection score, combining precision and
recall; F1@20 counts a match within 20 m), are now compared on the area
every rung searched (D51), a basis on which no tile-MCC (the Matthews
correlation coefficient over map tiles, which scores how well tiles with
and without a mound are told apart) has been computed, so the seven
ladders' tile-MCC is withheld; figures on the earlier, unclipped basis
are marked 'as evaluated'. No verdict moved; the reduction in K's F1
gain after verification changes size. The text also carries the
re-pricing and corrections the PI approved on 2026-10-04 (the second
under D25), and corrects statements that were wrong or too broad from
first publication: two counts (K = 1's highest-tile-MCC count; ten
ladders, not nine, on which every rung below K = 5 is ruled out as the
best), the tile-MCC rise and fall statements (now limited to K = 1
against the best rung, the comparison tested), the tile-MCC Pareto
reading (a cost preference, not a statistical exclusion of larger rungs)
and the 487-tile resolution (two detection rates, not a threshold). IN
BRIEF: this row asks what extra detection passes buy. Much of the F1
gain comes from the first three passes, the last step up a ladder is
usually the poorest buy, and how much extra passes help depends mainly
on the proposer's thinking level and temperature. Extra passes never
significantly improve tile-MCC over a single pass, and it falls on most
ladders; on the one pool tested with and without the verifier,
verification cut the F1 gain from extra passes by about half to
three-fifths, depending on the scoring basis, and, on the cells as
evaluated, turned their tile-MCC gain into a loss.+} SHAPE: the return
is FRONT-LOADED and K = 3 is on the efficient set of every ladder in the
corpus {+(a rung is efficient when no cheaper rung of the same ladder
scores as well)+} — 37 % to 93 % of a ladder's total F1 gain for 31 % to
[-64-] {+62+} % of its top rung's cost — while the last step {+(K = 5 ->
10, or K = 3 -> 5 on the two 55-map 3.7 arms, which have no K = 10
rung)+} is the worst [-buy on every ladder, at US$1,100 to US$43,000-]
{+buy, the dearest+} per 0.001 F1 {+or a loss of F1, on 17 of the 23
ladders; on the other six+} (the {+gold-standard stride A ladder, the
two 55-map stride B ladders under the Gemini 3 verifier, stride B under
the+} 3.7 [-family's-] {+verifier, MINIMAL image T 0.3 and HIGH image T
1.0) the K = 3 -> 5 step is worse. (The 17 counts stride B under the 3.7
verifier with its K = 5 rung, a 55-map board cell, findings § 3.3, that
the ladder inventory lacks; without it, 18.) Where the last step gains
F1 it costs about US$0.20 (gold-standard stride A) to US$27 (55-map 3.7
arm 1) per 0.001 F1 gained; on five ladders it loses F1 (MINIMAL text T
0.3 and T 0.7, HIGH text T 0.3, HIGH image T 0.7, and tier E); the 3.7
gold-standard text ladder's+} K = 5 -> K = 10 [-step-] {+step, for
example,+} buys [-+0.0002-] {++0.0004+} F1@20 for [-US$8.65).-]
{+US$8.68.+} WHAT GOVERNS THE RETURN: the proposer's thinking level, and
within a level its temperature. The K = 1 -> best-rung F1 gain is
significant on 7 of 7 HIGH-thinking ladders and 2 of 6 MINIMAL [-ones;-]
{+ones, and+} four ladders, every one of them MINIMAL, greedy-clique
into a SINGLE tier in which K buys nothing [-detectable;-] {+detectable
(both tested on the cells as evaluated);+} and on both HIGH tracks the
gain rises monotonically with temperature (text +0.0559 -> +0.0735 ->
[-+0.0994,-] {++0.0955,+} image +0.0780 -> +0.0959 -> +0.1514 across T
0.3 -> 0.7 -> [-1.0).-] {+1.0; text T 1.0's +0.0955 is on D51's clipped
basis, +0.0994 as evaluated).+} Read as the diversity dividend (Obs 141)
measured on a K ladder: K buys sampling diversity, and pays in
proportion to how much the configuration already generates. TILE-MCC
DOES NOT FOLLOW F1. Across the [-21-] {+15+} verified ladders [-with an
interpretable tile-MCC,-] {+of findings §§ 4 and 4.3 whose tile-MCC the
restated tables report (the gold-standard stride A ladder, the seven
55-map ladders, and seven of the thirteen Gemini 3 Phase 2 ladders; the
other six are on D51's clipped basis, where tile-MCC is withheld, and
tier E is tested separately, § 8.4),+} F1 rises on all [-21-] {+15+} and
tile-MCC falls on [-16,-] {+10,+} and {+as evaluated it falls on all six
withheld ladders too (16 of 21);+} NO ladder shows a significant
tile-MCC [-RISE;-] {+RISE from K = 1 to its best rung, and+} the
gold-standard ladder's [-+0.0135,-] {++0.0130,+} § 4 of the findings'
one apparent counter-example, tests at BH p = [-0.7678.-] {+0.7633 (BH:
a p value adjusted for multiple comparisons by the Benjamini-Hochberg
procedure).+} Significant FALLS {+from K = 1 to the best rung+} are
found on four ladders — the 3.7-verifier stride B (-0.0112), 3.7 arm 1
(-0.0099), 3.7 arm 2 (-0.0275) and HIGH image T 1.0 (-0.0637, BH p =
0.0420, the family with the largest F1 gain). {+Between intermediate
rungs, both 55-map stride A ladders fall significantly from K = 3 to K =
5 (-0.0111, BH p = 0.0066) and rise significantly from K = 5 to K = 10
(+0.0047, BH p = 0.0300), so over every tested pair six ladders show a
significant fall and two a significant rise.+} More passes buy
localisation inside already-positive tiles, not tile-level
discrimination, which matters for any application whose unit is the tile
rather than the mound. CAVEAT on the MCC column: tile-MCC is computed by
a string join on source_tile, and three cells of the 3.7 gold-standard
text [-family-] {+ladder+} are scored on a frame whose tile vocabulary
is not their proposer's, so their tile-MCC is WITHHELD with a named
reason rather than reported (g37-text-k1-verified-opmax,
g37-text-k1-verified-carried-p0.10-k1, g37-text-k3-verified-opmax; {+the
regenerated tables no longer record a+} raw [-0.1337 / 0.1422 /
0.1337).-] {+value).+} The corpus-wide exposure is measured at 3 of 149
committed cells the Era-2 board reads, no published board MCC is
affected, and the repair is a corpus-wide decision with the PI because
the 384 px frames overlap
(reports/tile-mcc-geometric-join-2026-09-12.md). Their F1 is sound and
is reported in full. INSTRUMENT (PI ruling): the board's round-robin
tile-swap micro-F1 permutation is THE instrument — 10,000 permutations,
seed 42, BH q = 0.05 within each ladder's own round-robin, tile-MCC
swapped on byte-identical masks so a ΔF1 and a ΔMCC are two statistics
of one permutation — and the registered per-map paired sign-swap is the
CROSS-CHECK. Where both cover a pair (8 pairs, 2 ladders) all eight
tile-MCC significance calls AGREE, with ΔMCC estimates within 0.0006;
one marginal F1 call differs (stride A's K = 3 -> 5, BH p 0.0079 against
0.0655), so the instrument choice is live for marginal F1 claims and
immaterial to the MCC conclusion. THE TWO CORPORA AGREE once resolution
is accounted for. The deployment MINIMAL ladders' own cells, scored on
random 487-tile subsets of their own 8,541 tiles (200 draws, seed 42,
same instrument), keep BH significance in 197 of 200 draws at ΔF1
+0.0547 and in only 39 of 200 at +0.0192 — a subsampling standard
deviation of ~0.0114 either [-way — so 487 tiles resolve-] {+way:
detection rates for two effects, not+} a [-ΔF1 of about 0.03 and above
and not below. The nine-] {+threshold (+0.0192 separates on all 8,541
tiles). On the gold-standard ladders, as evaluated, every+} MINIMAL
[-ladders sort by effect size rather than by corpus (every one-]
{+gain+} at or above +0.0546 [-separates,-] {+separates and+} every one
at or below +0.0223 does [-not),-] {+not, while +0.0338 separates and
+0.0384 (BH p = 0.1236) does not;+} and the deployment range
+0.0192..+0.0547 sits INSIDE the gold-standard range
[-+0.0139..+0.0629.-] {++0.0139..+0.0600 (+0.0629 as evaluated).+} So 'K
buys nothing detectable' on four MINIMAL configurations is a statement
about 487 tiles, not about K. PARETO MCC SET: [-on tile-MCC no rung
above-] K = 1 is [-ever-] the [-admissible choice — K = 1-] {+cheapest
member of every tile-MCC set of multiple comparisons with the best (MCB,
below),+} holds the highest tile-MCC on [-13-] {+7+} of the [-21
interpretable-] {+15+} ladders {+above,+} and [-is never significantly
beaten on it — so the MCC-efficient rung is-] {+no+} K = 1 [-wherever-]
{+-> best-rung comparison shows a significant MCC gain, so it is the
cost-conscious choice for+} tile-level discrimination {+when the rule is
to take the cheapest rung not ruled out as best; larger rungs are not
excluded (the MCB admits one on 20 of 22 ladders). For F1, K = 3 is on
every ladder's observed cost frontier but+} is the [-objective, while
the F1-efficient-] {+cheapest MCB-admissible+} rung [-is K = 3.-] {+on
only 10 of 22.+} The two objectives [-select-] {+favour+} different
rungs, and that is the review's practical finding. A GEOMETRY EFFECT,
consensus-only: at fixed MINIMAL text T 0.7 the grid study's K = 1 -> 10
gain is about [-2.4x-] {+2.2x+} larger at 12.5 % overlap than at 50 %
[-(+0.1454-] {+(+0.1441+} against [-+0.0572-] {++0.0660+} at 384 px;
[-+0.0914-] {++0.0947+} against [-+0.0396-] {++0.0425+} at 512 px), and
tile-MCC RISES with K on all four consensus-only cells
[-(+0.038..+0.154)-] {+(+0.029..+0.132)+} — the opposite of the verified
ladders, consistent with the same mechanism. Overlap and pass count buy
the same redundancy. The pattern does not survive to the verified
deployment ladders, which order the other way. THE VERIFIER STAGE
REVERSES tile-MCC's RESPONSE TO K, {+on the cells as evaluated,+} and
[-absorbs about 40-] {+roughly halves K's observed F1 gain: 48.7+} %
[-of K's F1 return-] {+smaller with tier E's rungs compared on the area
every rung searched (D51), 60.3 % smaller as evaluated+} (§ 8.6, added
on the PI's ruling 2026-09-13). On ONE pool and ONE geometry — the grid
study's 384 px / 50 % B-geometry MINIMAL text pool, which is the
deployment stride-B tiling at gold-standard scale — K = 1 -> 10 raises
F1@20 by [-+0.0572-] {++0.0660+} with tile-MCC RISING +0.0444
consensus-only (results/grid-2026-08-18/sweep.csv, cell g384_ov192, best
F1@20 per K over the corroboration x vote grid: 0.6633/0.4465 at K = 1,
[-0.7205/0.4909-] {+0.7293/0.4909+} at K = 10), and raises F1@20 by only
[-+0.0340-] {++0.0338+} with tile-MCC FALLING [--0.0308-] {+-0.0238 (as
evaluated)+} once the same pool is [-verified (tier-e/ladder.json-]
{+verified. The clipped F1@20 is 0.8604 at K = 1
(reports/scorer-frames-d50-d51-2026-10-08-scripts/out/ladders_new.json)+}
and [-each rung's evaluation: 0.8546/0.8211-] {+0.8942 at K = 10, the
restated rung of tier-e/ladder.json, whose union lies wholly in the
common area so the clip removes nothing (that file's own K = 10 row,
0.8886, predates the re-verification); as evaluated, K = 1 reads 0.8680
and the gain is +0.0262. Tile-MCC (0.8211+} at K = 1, [-0.8886/0.7903-]
{+0.7973+} at K = [-10). So-] {+10; tier-e/ladder.json and each rung's
evaluation) exists only as evaluated; clipped tile-MCC has not been
computed, so its sign and magnitude are unknown. The two stages share+}
the [-verifier takes 40.6 %-] {+common footprint but not the reference
set: the consensus-only side is scored against the 428 mounds inside it,
tier E against the frame's 435 (D51), 7+} of [-what-] {+which lie
outside the clipped area. So, on these scoring bases, the observed F1
gain from+} extra passes [-buy-] {+is 48.7 % smaller once the pool is
verified (one minus the ratio of the two gains,+} on {+unrounded values;
60.3 % as evaluated), and on the cells as evaluated a tile-level GAIN
becomes a tile-level LOSS, a swing of 0.0682 MCC. This is consistent
with the mechanism proposed for the TILE-MCC DOES NOT FOLLOW+} F1 [-—
because it-] {+finding above (the verifier+} was already removing much
of what extra passes [-remove — and turns a tile-level GAIN into a
tile-level LOSS, a swing of 0.0752 MCC. This is the mechanism of the
TILE-MCC DOES NOT FOLLOW F1 finding above measured directly rather than
inferred:-] {+remove) but does not measure it directly: on this pool,+}
tile-MCC's response to K [-is a property of-] {+depends on+} the
PIPELINE STAGE, not [-of K.-] {+on K alone.+} Its limits are stated with
it: one geometry, one thinking level, one temperature, one modality, one
corpus, and the ladder's own DMCC steps are not individually significant
(tile-MCC separates on none of its six pairs), so the claim is about the
sign and size of the shift BETWEEN stages. NOT CLAIMED: no MCC RANKING
of rungs, tiering stays on the preregistered F1; and the [-five
non-separating ladders'-] MCC moves {+of the ladders whose K = 1 ->
best-rung change does not separate (11 of the 15; 17 of 21 as
evaluated)+} are not shown to be zero. HSU MCB ADMISSIBLE SETS [-(PI-]
{+(the rungs that cannot be ruled out as their ladder's best; PI+}
ruling 2026-09-13, 'wait for the sets'): the review's last outstanding
run-card requirement is supplied for all 22 tiered ladders, on F1 at
each ladder's own headline buffer and on tile-MCC, with the Era-2
board's own MCB step verbatim (scripts/selection_aware_intervals.py
--board; Hsu's constrained one-sided form on theta_i = stat_i - max_{j
!= i} stat_j, critical value bootstrapped over 10,000 tile resamples,
seed 42, m-out-of-n 1.0, simultaneous 95 %), each ladder on its own
frame and reference, driven by scripts/k_ladder_mcb.py and gated on all
44 runs against the committed tiering ranking (170 candidate rows, max
abs delta 4.958e-05, results/k-ladder-2026-09-12/mcb/summary.json).
{+The sets are computed on the cells as evaluated, so every MCB count
below includes tier E and the six Gemini 3 ladders whose tile-MCC the
clipped basis withholds above; that basis has no per-tile table to
compute them on.+} ON THE SHAPE FINDING: K = 3 is admissible on 12 of
the 22 ladders and is the CHEAPEST admissible rung on 10 of them, so the
front-loaded Pareto reading is endorsed by the simultaneous instrument
on roughly half the corpus and declined on the other half — on [-nine-]
{+ten+} ladders nothing below K = 5 is admissible {+(on nine the
cheapest admissible rung is K = 5; on 55-map stride B under the 3.7
verifier only K = 10 is)+} even though K = 3 remains the efficient buy,
which makes 'K = 3 is on the efficient set' a cost claim rather than a
statistical one. ON THE LAST STEP: NO ladder's F1-admissible set
excludes K = 10 — all twenty ladders that have a K = 10 rung admit it —
so the top rung is never statistically ruled out, [-only never-] {+and
whether it is+} worth its [-price, which-] {+price+} is the [-formal
counterpart-] {+cost question SHAPE above answers: the last step is the
worst buy on 17+} of the [-US$1,100-to-US$43,000 per 0.001 F1 figures
above.-] {+23 ladders, not on all.+} ON THE TWO OBJECTIVES: K = 1 is
ruled out on F1 on 20 of 22 ladders and is admissible on tile-MCC on 22
of 22, holding the highest tile-MCC on 13 of them, so the [-PARETO MCC
SET claim above now rests on the canonical-] simultaneous instrument
[-rather than-] {+agrees with the pairwise tests that K = 1 is never
ruled out+} on [-a pairwise count.-] {+tile-MCC, while on F1 it almost
always is.+} ON TILE-MCC'S RESOLUTION: the MCC-admissible set is the
WHOLE ladder on [-12-] {+13+} of 22 against 2 of 22 on F1 — the same
weak resolution the permutation arm found — but where it resolves it
resolves against K: [-seven-] {+six+} of the twenty ladders with a K =
10 rung exclude it on tile-MCC, and on two (55-map stride B under the
3.7 verifier, and 3.7 arm 2) the MCC-admissible set is {K = 1} alone. ON
RESOLUTION GENERALLY: the simultaneous F1 width w_upper is
[-0.0151-0.0326-] {+0.0159-0.0326+} on the 487-tile gold standard and
0.0047-0.0056 on the 8,541-tile deployment corpus, three to six times
narrower, which is the tension analysis's resolution result in the MCB's
own units. INSTRUMENT DISAGREEMENT, FLAGGED: the admissible set and the
committed greedy-clique tie set differ in BOTH directions (F1 set
smaller than the tie set on two ladders, larger on six), exactly as
erratum E83 and defect D20 warn; of the four MINIMAL ladders that
greedy-clique into a SINGLE tier, only two are admissible whole, since
MINIMAL text T 0.3 and MINIMAL image T 1.0 both rule K = 1 out as best.
The single-tier statement stands as a within-ladder pairwise BH result
and is not withdrawn, but 'one tier' is not 'every rung could be the
best one'. WITHHELD: the 3.7 gold-standard text [-screen-] {+ladder+}
has NO admissible set on either metric, because the tile-join invariant
refuses the per-tile table of three {+cells on two+} of its four rungs
{+(K = 1 and K = 3)+} on this frame and the refusal falls on the F1 arm
as well as the MCC arm, leaving two sound rungs of four; its whole-frame
F1 is unaffected and reported in full. CARRIED CONVENTION (PI ruling
2026-09-13): the gold-standard stride ladder's own vote shell (k =
1/3/4/8 at K = 1/3/5/10) is THE carried point and ruling R2's literal k
= K stays as a disclosed column; no number was recomputed, the two
readings coincide at K <= 3, and both stay committed in
phase2/committed-carried/scores.json. Reading that ruling back against
the 55-map tables disclosed something nothing had recorded: stride A's
committed carried cells are the stride shell (k = 3/4/8) while stride
B's, stride B's 3.7-verifier cell and both 3.7 arms' are k = K, so the
transfer taxes of findings sections 3.2, 3.3 and 3.4 are k = K taxes and
are an UPPER BOUND on the transfer cost (each cell's vote_threshold in
results/run-conditions.json; findings section 3's disclosure table). MCB
artefacts: results/k-ladder-2026-09-12/mcb/; deltas
reports/k-ladder-mcb-deltas-2026-09-13.md. Findings:
results/k-ladder-2026-09-12/findings.md (all sections); tension analyses
results/k-ladder-2026-09-12/tension/; spend
reports/k-ladder-phase2-deltas-2026-09-12.md and
results/k-ladder-2026-09-12/tier-e/.
```

## 3. Changes, the issue each fixes, and the source of every new or changed number

Row numbers follow the 25 replacements in `kl3/build3.py`. In the Issue column, A1 to A5 are
Astra's v2 items (1 to 3 are its P2 items; 4 and 5 are its two editorial recommendations),
C1 to C8 are the coordinator's v2 points, V1 to V9 are the first verifier's v1 issues, and 1 to
9 are the original brief's items. "conv." is the walk-through convention. Paths are under
`results/k-ladder-2026-09-12/` unless they start with `results/`, `reports/` or `planning/`.
"P1" is `ladders.json` and "P2" is `phase2/ladders.json`.

| # | Change (signed register → v3) | Issue | Source and value |
|---|---|---|---|
| 1 | K defined at first use: "(K is the number of detection passes whose candidates are pooled before verification)" | A5 | wording |
| 2 | "the 3.7 gold-standard text screen" → "the Gemini 3.7 gold-standard text ladder", one name throughout | C8 | wording |
| 3a | Dated clause. v3 changes: F1 (with F1@20) and tile-MCC defined at first use; "share" → "reduction" (A4); the corrections now listed in one sentence, including the two signed readings Astra found too broad (the tile-MCC Pareto reading, A1; the 487-tile resolution, A2) | conv., C2, C8, A1, A2, A4, A5 | Causes as in v2: `reports/s164-agent-records/rescore-repaired-gs.md` § 3.2; `restatement-pass.md` §§ 1.4 and 2.3; rulings D50, D51, D57, D62 (1), D65 (2), D67 (5) |
| 3b | New: the plain-language lead, "IN BRIEF", three sentences | A5 | No new claim. Each sentence restates SHAPE (17 of 23; K = 3 on every frontier), WHAT GOVERNS, TILE-MCC (no significant gain over K = 1 in any tested K = 1 pair, § 4.9; falls on 10 of 15) and § 8.6 (48.7 % and 60.3 %, given as "about half to three-fifths, depending on the scoring basis", so the lead is the same under both options of decision A) |
| 4a | SHAPE: "31 % to 64 %" → "31 % to 62 %" | 3 | P2 `summary[HIGH image T 1.0].cost_share_at_k3` 0.3149; P1 3.7 arm 2 `cost.usd` 99.0293 / 158.5795 = 0.6245 |
| 4b | SHAPE: "worst buy on every ladder" → "on 17 of the 23", with the six exceptions | 3 | § 4.1 |
| 4c | SHAPE: the fourth cell's K = 5 board rung disclosed in a parenthesis, shortened from v2 and without the undefined "MCB" | C8 | `results/55map-final-board-r2-2026-09-06/cells/FOURTH-N5-oracle/evaluation.json` F1@50 0.8758; US$116.15 (findings § 3.3); 18 without it (§ 4.8) |
| 4d | SHAPE: about US$0.20 to US$27 per 0.001 F1 gained | 3 | P1 GS stride A K5 → K10: US$0.198; P1 3.7 arm 1 K3 → K5 oracle: US$26.75 |
| 4e | SHAPE: five ladders lose F1 at the last step | 3 | P2 `opmax.f1_20` K5 → K10: 0.8778 → 0.873, 0.8739 → 0.8726, 0.8873 → 0.8722, 0.7868 → 0.7765; `tier-e/ladder.json` 0.9046 → 0.8942 |
| 4f | SHAPE: "+0.0002 … US$8.65" → "+0.0004 F1@20 for US$8.68" | carried | P2 3.7 ladder K5 0.9165 → K10 0.9169; `all_in_flex_usd` 9.1454 → 17.8281 |
| 4g | SHAPE: "efficient set" glossed | conv. | `findings.md` § 5 |
| 5 | "(both tested on the cells as evaluated)" | C7 | `phase2/mcc-test/summary.json` (`326181bcd`); committed tiering |
| 6 | "+0.0994" → "+0.0955 … on D51's clipped basis, +0.0994 as evaluated" | 4 | P2 `summary[HIGH text T 1.0].gain` 0.0955; `historical_as_evaluated.gain` 0.0994 |
| 7 | The 15 defined, with tier E named as tested separately; rise and fall limited to K = 1 → best; +0.0130 / 0.7633; BH defined at first use | 2, 4, 6, C2, C6, A5 | P2 `summary[*].mcc_verdict`; `mcc-test/summary.json`; `mcc-test/gs-stride-a.json` `pairs[0].mcc.delta` 0.013043, `p_bh` 0.76332 |
| 8 | Intermediate steps over every tested pair (six falls, two rises) | C2 | `mcc-test/55map-stride-a-r2.json` and `…-standardised.json` K3-vs-K5 −0.011052 / −0.011053 (`p_bh` 0.0066), K5-vs-K10 +0.004676 / +0.004684 (`p_bh` 0.03); § 4.9 |
| 9 | "raw 0.1337 / 0.1422 / 0.1337" → "the regenerated tables no longer record a raw value" | 7 | `phase2/scores.json` rows 27 and 28, `tile_mcc` null |
| 10 | CAVEAT: one name for the 3.7 ladder | C8 | wording |
| 11 | THE TWO CORPORA AGREE: "487 tiles resolve a ΔF1 of about 0.03 and above and not below" → "detection rates for two effects, not a threshold (+0.0192 separates on all 8,541 tiles)"; "the nine MINIMAL ladders sort …" → restricted to the gold-standard ladders, as evaluated, with the two in-between effects named; "+0.0629" → "+0.0600 (+0.0629 as evaluated)" | A2, C7, 4 | `tension/subsample.json` (39 and 197 of 200); `tension/effect-sizes.json` (deployment stride A +0.0192, `p_bh` 0.0; GS stride A +0.0338, `p_bh` 0.0024; MINIMAL image T 0.7 `delta_f1` 0.06); `phase2/mcc-test/summary.json` MINIMAL image T 1.0 `f1_p_bh_k1_to_best` 0.1236, `f1_delta` +0.038344; findings § 8.2 item 1 (the gold-standard restriction) |
| 12 | PARETO MCC SET rewritten: K = 1 is the cheapest member of every tile-MCC MCB set, highest on 7 of 15, never significantly beaten from K = 1 to the best rung, and so the cost-conscious choice under a cheapest-admissible rule; larger rungs not excluded (20 of 22); for F1, K = 3 on every observed cost frontier but cheapest admissible on 10 of 22. MCB defined at first use | A1, 2, 4 | `mcb/summary.json`: `min(mcc.hsu_admissible_K)` = 1 on 22 of 22; `max` > 1 on 20 of 22 (all but `55map-stride-b-g37vf-r2` and `37arm2-r2`, both `[1]`); `gs-stride-a` `mcc.hsu_admissible_K` [1, 3, 5, 10], K = 10 highest (0.807855 against 0.794812); `min(f1.hsu_admissible_K)` = 3 on 10. K = 3 on every frontier: its F1 exceeds K = 1's on all 23 ladders (§ 4.1 table, every K = 1 → 3 step positive), and K = 1 is the only cheaper rung |
| 13 | Geometry: 2.2x; the four gains; +0.029..+0.132 | carried | `tension/grid-overlap.json` |
| 14 | Verifier headline: "REVERSES … on the cells as evaluated, and roughly halves K's observed F1 gain: 48.7 % smaller … (D51), 60.3 % smaller as evaluated" | A3, A4, 5 | § 4.7 |
| 15 | Verifier detail: "(as evaluated)" beside the first −0.0238; the clipped inputs anchored; "clipped tile-MCC has not been computed, so its sign and magnitude are unknown"; the swing stated once, "on the cells as evaluated"; the reference sets (428 against 435) in a shortened sentence; the percentage described as "the observed F1 gain from extra passes is 48.7 % smaller once the pool is verified … on these scoring bases"; "measured directly rather than inferred" → "consistent with the mechanism proposed … but does not measure it directly", and "is a property of the PIPELINE STAGE" → "on this pool … depends on the PIPELINE STAGE, not on K alone" | A3, A4, C4, C5 | `reports/scorer-frames-d50-d51-2026-10-08-scripts/out/ladders_new.json` (`d51_clipped.f1` 0.86036; K = 10 `area_removed_km2` 0.0; K = 10 row 0.888623); `tier-e/ladder.json` rungs 0.868 / 0.8211 and 0.8942 / 0.7973; `results/grid-2026-08-18/grid_analysis.json` `common_ground_truth` 428, `era2_487.ground_truth` 435; swing 0.044361 + 0.023837 = 0.068198 |
| 16 | NOT CLAIMED: "the five non-separating ladders" → "(11 of the 15; 17 of 21 as evaluated)" | C7 | four of the 15 separate K = 1 → best (row 7); none of the six withheld does |
| 17 | MCB heading gloss | conv. | — |
| 18 | MCB basis sentence | 4 | `mcb/summary.json` |
| 19 | "nine" → "ten (…)" | 9 | § 4.5 |
| 20 | ON THE LAST STEP made consistent with SHAPE | C1 | § 4.1 |
| 21 | ON THE TWO OBJECTIVES: "so the PARETO MCC SET claim above now rests on the canonical simultaneous instrument rather than on a pairwise count" → "so the simultaneous instrument agrees with the pairwise tests that K = 1 is never ruled out on tile-MCC, while on F1 it almost always is". v2's breakdown "(the 7 of the 15 above, five of the six withheld ladders, and tier E)" is cut; the MCB basis sentence (row 18) carries the disclosure | A1, A5 | `mcb/summary.json` `roll_up.ladders_whose_MCC_admissible_set_contains_K1` (22); K = 1 in the F1 set on 2 of 22 |
| 22–24 | 12 → 13 of 22; seven → six; 0.0151 → 0.0159 | carried | `mcb/summary.json` |
| 25 | WITHHELD: three cells on two rungs; one name | C7, C8 | `mcb/summary.json` `withheld` |

## 4. Recounts and investigations

### 4.1 The last step: still 17 of 23, the same six exceptions

**Method.** For every ladder, each step between consecutive rungs is priced as its added
all-in cost divided by its F1 gain, per 0.001 F1. A step that loses or holds F1 is ranked worst
of all. The last step counts as the worst buy when no earlier step is dearer. Rungs:
P1's best F1 per K at the ladder's headline buffer (the oracle rows, as `findings.md` § 5's
efficient-rung table uses) and `cost.usd`, plus the fourth cell's K = 5 rung, which P1 omits
(F1@50 0.8758 from `results/55map-final-board-r2-2026-09-06/cells/FOURTH-N5-oracle/evaluation.json`,
cost US$116.15 from `findings.md` § 3.3 and `reports/wp4b-frontier-repricing-2026-10-04.md`
line 54). P2's `opmax.f1_20` and `all_in_flex_usd` on each ladder's reported basis. Tier E's
`f1_20` from `tier-e/ladder.json` and the approximate all-in costs of `findings.md` § 8.4
(US$2.09, 4.21, 6.20, 10.66).

**Result.** 17 of 23. The exceptions are GS stride A, the two 55-map stride B ladders under the
Gemini 3 verifier, the fourth cell (stride B under the 3.7 verifier), MINIMAL image T 0.3 and
HIGH image T 1.0, exactly D25's list, and in each the worse step is K = 3 → 5. The count and
the list do not change with GS stride A on its own frame or on the board frame, with Phase 2 on
the clipped or as-evaluated basis, or with tier E clipped or not.

| Ladder | Steps: ΔF1 / added US$ = US$ per 0.001 F1 | Last step worst | Last step loses F1 | K = 3 share of gain | K = 3 share of top cost |
|---|---|---|---|---:|---:|
| 3.7 arm 1 | 1→3 +0.0292 / 59.56 = 2.04; 3→5 +0.0022 / 58.85 = 26.75 | yes | no | 93.0 % | 61.6 % |
| 3.7 arm 2 | 1→3 +0.0238 / 60.69 = 2.55; 3→5 +0.0023 / 59.55 = 25.89 | yes | no | 91.2 % | 62.4 % |
| 55-map stride A r2 | 1→3 +0.0094 / 20.60 = 2.19; 3→5 +0.0062 / 18.45 = 2.98; 5→10 +0.0036 / 43.97 = 12.21 | yes | no | 49.0 % | 39.6 % |
| 55-map stride A std | 1→3 +0.0095 / 20.60 = 2.17; 3→5 +0.0057 / 18.45 = 3.24; 5→10 +0.0037 / 43.97 = 11.88 | yes | no | 50.3 % | 39.6 % |
| GS stride A (own frame) | 1→3 +0.0256 / 1.26 = 0.05; 3→5 −0.0056 / 1.16 = loss; 5→10 +0.0138 / 2.74 = 0.20 | **no** | no | 75.7 % | 40.4 % |
| 55-map stride B r2 | 1→3 +0.0494 / 34.31 = 0.69; 3→5 +0.0009 / 31.57 = 35.08; 5→10 +0.0044 / 76.00 = 17.27 | **no** | no | 90.3 % | 37.7 % |
| fourth cell (stride B, 3.7 vf) | 1→3 +0.0395 / 39.27 = 0.99; 3→5 +0.0011 / 34.75 = 31.59; 5→10 +0.0055 / 82.02 = 14.91 | **no** | no | 85.7 % | 41.1 % |
| 55-map stride B std | 1→3 +0.0492 / 34.31 = 0.70; 3→5 +0.0010 / 31.57 = 31.57; 5→10 +0.0043 / 76.00 = 17.67 | **no** | no | 90.3 % | 37.7 % |
| MINIMAL text T 0.3 ‡ | 1→3 +0.0153 / 0.78 = 0.05; 3→5 +0.0070 / 0.67 = 0.10; 5→10 −0.0048 / 1.55 = loss | yes | **yes** | 68.6 % | 43.5 % |
| MINIMAL text T 0.7 | 1→3 +0.0150 / 0.81 = 0.05; 3→5 +0.0014 / 0.74 = 0.53; 5→10 −0.0013 / 1.68 = loss | yes | **yes** | 91.5 % | 42.5 % |
| MINIMAL text T 1.0 ‡ | 1→3 +0.0412 / 0.96 = 0.02; 3→5 +0.0067 / 0.82 = 0.12; 5→10 +0.0067 / 1.82 = 0.27 | yes | no | 75.5 % | 42.6 % |
| HIGH text T 0.3 | 1→3 +0.0469 / 5.88 = 0.13; 3→5 +0.0090 / 5.82 = 0.65; 5→10 −0.0151 / 14.16 = loss | yes | **yes** | 83.9 % | 32.1 % |
| HIGH text T 0.7 | 1→3 +0.0483 / 5.73 = 0.12; 3→5 +0.0142 / 5.49 = 0.39; 5→10 +0.0110 / 13.45 = 1.22 | yes | no | 65.7 % | 32.4 % |
| HIGH text T 1.0 ‡ | 1→3 +0.0691 / 5.22 = 0.08; 3→5 +0.0147 / 4.95 = 0.34; 5→10 +0.0117 / 12.23 = 1.05 | yes | no | 72.4 % | 32.8 % |
| MINIMAL image T 0.3 ‡ | 1→3 +0.0094 / 1.25 = 0.13; 3→5 −0.0007 / 1.21 = loss; 5→10 +0.0052 / 2.95 = 0.57 | **no** | no | 67.6 % | 35.9 % |
| MINIMAL image T 0.7 ‡ | 1→3 +0.0318 / 1.32 = 0.04; 3→5 +0.0135 / 1.26 = 0.09; 5→10 +0.0147 / 3.09 = 0.21 | yes | no | 53.0 % | 35.4 % |
| MINIMAL image T 1.0 ‡ | 1→3 +0.0244 / 1.41 = 0.06; 3→5 +0.0096 / 1.33 = 0.14; 5→10 +0.0044 / 3.24 = 0.74 | yes | no | 63.5 % | 35.7 % |
| HIGH image T 0.3 | 1→3 +0.0290 / 5.17 = 0.18; 3→5 +0.0260 / 5.05 = 0.19; 5→10 +0.0230 / 12.50 = 0.54 | yes | no | 37.2 % | 31.6 % |
| HIGH image T 0.7 | 1→3 +0.0757 / 4.83 = 0.06; 3→5 +0.0202 / 4.65 = 0.23; 5→10 −0.0103 / 11.60 = loss | yes | **yes** | 78.9 % | 31.6 % |
| HIGH image T 1.0 | 1→3 +0.1126 / 4.58 = 0.04; 3→5 +0.0092 / 4.62 = 0.50; 5→10 +0.0296 / 11.14 = 0.38 | **no** | no | 74.4 % | 31.5 % |
| scale-4-optimal 487 | 1→3 +0.0920 / 4.35 = 0.05; 3→5 +0.0339 / 4.24 = 0.13; 5→10 +0.0048 / 10.53 = 2.19 | yes | no | 70.4 % | 31.6 % |
| 3.7 gold-standard text ladder ‡ | 1→3 +0.0391 / 3.52 = 0.09; 3→5 +0.0092 / 3.45 = 0.38; 5→10 +0.0004 / 8.68 = 21.71 | yes | no | 80.3 % | 31.9 % |
| tier E (as evaluated) | 1→3 +0.0299 / 2.12 = 0.07; 3→5 +0.0067 / 1.99 = 0.30; 5→10 −0.0104 / 4.46 = loss | yes | **yes** | 81.7 % | 39.5 % |

‡ Reported on D51's clipped basis.

### 4.2 K = 3's cost share and gain share

- **Cost share: 31.49 % to 62.45 %, so "31 % to 62 %"** (the verifier's 31–62 %, and the
  PI-approved second note of 2026-10-04). The low end is HIGH image T 1.0 (P2 `cost_share_at_k3`
  0.3149) and the high end 3.7 arm 2 (99.0293 / 158.5795). The register's "64 %" was the
  pre-re-pricing figure.
- **Gain share: 37.18 % to 92.99 %, so "37 % to 93 %", unchanged.** The low end is HIGH image
  T 0.3 (P2 `share_at_k3` 0.3718) and the high end 3.7 arm 1 ((0.8705 − 0.8413) / (0.8727 −
  0.8413)). Tier E (81.7 %, 81.9 % clipped) and the restated 3.7 gold-standard text ladder (80.3 %,
  91.9 % as evaluated) lie inside the range.

### 4.3 The ladders whose last step loses F1: five, confirmed

MINIMAL text T 0.3, MINIMAL text T 0.7, HIGH text T 0.3, HIGH image T 0.7 and tier E (values in
§ 3, row 4e). This is the same on either basis. Tier E's last step lost F1 before the
restatement too (0.8905 → 0.8886, `findings.md` changelog, line 1637), so the first 2026-10-04
note's "four ladders' last steps lose F1" counts only the Phase 2 ladders, which is how
`findings.md` § 7.4 counts them ("on four of those"); across the 23 it is five. The 3.7 arm 1
carried K = 5 cell (0.8551) also loses F1 against K = 3, but the ladder convention takes each
K's best (oracle) rung, 0.8727, so arm 1 is not among the five.

### 4.4 "K = 1 holds the highest tile-MCC": 7 of the 15, not 8

**The 15.** The eight Phase 1 ladders (GS stride A and the seven 55-map ladders) and the seven
Phase 2 ladders whose `mcc_verdict` is not `withheld` (MINIMAL text T 0.7, HIGH text T 0.3 and
T 0.7, HIGH image T 0.3, T 0.7 and T 1.0, scale-4-optimal). The six Gemini 3 ladders the D51
clip reports clipped are left out because their reported basis carries no tile-MCC. The 3.7
gold-standard text ladder was never in the count (tile-join withholding), and neither was tier E.

**Count.** `mcb/summary.json` `ladders[*].mcc.best_K == 1` lists 13 ladders: tier E; five of the
six withheld Gemini 3 ladders (MINIMAL text T 1.0, HIGH text T 1.0, MINIMAL image T 0.3, T 0.7
and T 1.0; MINIMAL text T 0.3's best is K = 3); and seven of the 15 (3.7 arm 1, 3.7 arm 2, 55-map
stride B under the 3.7 verifier, HIGH text T 0.3, HIGH image T 0.7, HIGH image T 1.0,
scale-4-optimal). So 13 = 7 + 5 + 1. The lapse note's 8 is 13 minus the five withheld, which
leaves tier E in a numerator whose denominator excludes it. The own-frame MCCs of P1 and P2 give
the same 7 (HIGH image T 0.7 ties K = 1 and K = 3 at 0.8435 to four places; the MCB's unrounded
values put K = 1 ahead).

**The signed text had the same overcount.** At `718d0ee08`, the MCB's 13 included tier E, and
the 21 (8 Phase 1 + 13 Gemini 3) did not: on those 21 the count was 3 + 9 = 12, not 13. The
correction belongs in the re-signing attestation (§ 6, item 3).

### 4.5 "On nine ladders nothing below K = 5 is admissible": the qualifier, and the count is ten

The qualifier is in `findings.md` § 6.1, item 1 (line 844), which partitions the 22 ladders by
the cheapest rung in each F1-admissible set: "K = 3 … the CHEAPEST admissible rung on 10 …
Two more admit K = 1 … nine admit nothing below K = 5, and one admits nothing below K = 10."
`mcb/summary.json`, minimum of each `f1.hsu_admissible_K`, gives exactly that partition:
K = 3 on 10, K = 1 on 2, K = 5 on 9, K = 10 on 1 (`55map-stride-b-g37vf-r2`, set `[10]`). The
same partition holds at `b7e2821ba`, where the MCB landed, and at `718d0ee08`.

So "nine" counts the ladders whose cheapest admissible rung is exactly K = 5. The sentence's
words, "nothing below K = 5 is admissible", are true of ten: the nine plus 55-map stride B
under the 3.7 verifier, whose set is {K = 10}. "Ten" is also the count the sentence's own logic
needs: K = 3 is admissible on 12 of 22 and declined on the other 10, which is "the other
half". The verifier's 10 is right. The redraft says ten and keeps the partition in a
parenthesis; § 7 drafts the matching edits to findings § 6.1 and the MCB deltas report.
`findings.md` § 6.1 item 1 has a second instance in the same sentence: "on nine
ladders a K = 3 rung can be ruled out as best" (line 848) is ten for the same reason.
`reports/k-ladder-mcb-deltas-2026-09-13.md` line 96 carries the outcome's wording.

### 4.6 The tier E basis: what D51 decides, and what the comparison can and cannot claim

**The ruling.** D51 (`planning/pi-decisions-2026-09-20.md` line 75, RULED 2026-10-07) records:
"where rungs' candidate pools cover different areas … the larger-area rungs are clipped to the
common area and the frame's reference set is kept. … the tier E ladder takes the same rule."
The verifier adds a nuance, and it is right: those are the decisions log's summary words for
option 1. The PI's quoted words ("with only 7 mounds in question, we can go with option 1;
please do generalise this …") do not name tier E. The option he chose did place tier E's K = 10
rung in the same universe question (`reports/frames-blast-radius-2026-10-07.md` line 519: "Tier
E's K = 10 rung likewise"), and no later ruling narrows it. So D51 decides the basis as
recorded, and the draft follows it. The PI should confirm, because his own words do not name
tier E and the restatement pass left the choice open (`restatement-pass.md` § 10 item 3).

**What the clip does (corrected from version 1).** Version 1 said "unclipped, the K = 10 rung
is charged with misses in a band it never searched". That is true of the unclipped reading,
but it implied that the clip relieves K = 10, and it does not. The mechanism:

- Tier E's K = 1, 3 and 5 rungs searched 37.94 km² more than the K = 10 union, whose candidates
  were filtered upstream to the grid study's common footprint (`ladders_new.json`
  `tier_e.assessed_area.max_excess_km2` 37.9354; the K = 10 pool's `effective_area_km2`
  1364.4713).
- Unclipped, K = 1 earns credit for mounds in that band. Its matched references fall from 388
  to 382 of 435 when it is clipped: recall 0.891954 → 0.878161 in `ladders_new.json`
  `tier_e.rungs[0].points.opmax` `d50` and `d51_clipped`. K = 10 cannot earn that credit.
- Clipped, the lower rungs lose that credit. D51 keeps the frame's 435 references, so every
  clipped rung, K = 10 included, is scored against the 7 mounds in the band, outside the area
  it was clipped to (clipped TP / recall = 435.0 on every rung).

So the clip equalises the rungs by removing the lower rungs' band credit, not by relieving
K = 10. The unclipped gain is understated, and the unclipped share overstated, because K = 1
keeps band credit that K = 10 cannot have.

**The comparison with the consensus-only side.** The grid study scores the consensus-only
ladder on its common footprint, 1,364.47 km² (`results/grid-2026-08-18/grid_analysis.json`
`scope.footprint_audit.common_km2` 1364.4713), against the 428 reference mounds inside it
(`common_ground_truth` 428; `sweep.csv`'s g384_ov192 best rows give TP / recall = 428.0 at
K = 1 and K = 10). Tier E is scored against 435 on either reading. The clipped reading
therefore matches the consensus side's area but not its references, and the unclipped
reading matches neither. Neither tier E reading is exactly the consensus side's basis. The
outcome now says so where it makes the comparison, and the recommendation in § 5 A rests on
D51's text, not on a like-for-like claim.

### 4.7 The verifier's share: 60.3 % as evaluated, 48.7 % clipped, and where 48.7 % comes from

- Consensus-only gain: 0.065954 (`tension/grid-overlap.json` `cells[0].delta_f1_k1_to_k10`).
- As evaluated: 1 − (0.8942 − 0.868009) / 0.065954 = 60.29 %, or with the permutation
  micro-F1, 1 − 0.026165 / 0.065954 = 60.33 %. Either way, **60.3 %**.
- Clipped: 1 − (0.8942 − 0.860360) / 0.065954 = 48.69 %, or with the micro-F1 0.894174,
  48.73 %. Either way, **48.7 %** on unrounded inputs. Findings § 8.6 prints 48.8 %, which is
  1 − 0.0338 / 0.0660 on gains rounded to four places (decision B).
- **Provenance of the inputs.** K = 1 clipped, 0.860360, is committed
  (`reports/scorer-frames-d50-d51-2026-10-08-scripts/out/ladders_new.json`, 2026-10-08). K = 10
  clipped is **inferred, not committed**. The same file records that the clip removes 0 km² at
  K = 10 (`assessed_area.clip.area_removed_km2["K = 10"]` 0.0), so the restated K = 10 rung's
  clipped F1 equals its as-evaluated 0.8942 (`tier-e/ladder.json` `rungs[3].f1_20`). But that
  file's own K = 10 row is 0.888623. It predates the 2026-10-13 re-verification, and a reader
  who follows the anchor gets 1 − (0.888623 − 0.860360) / 0.065954 = **57.1 %**. The outcome
  now names that stale row and says which value replaces it. A committed clipped tier E
  reading would give 48.7 % a proper anchor (§ 5 C).

### 4.8 The fourth cell's K = 5 rung decides one of the six exceptions

The last-step recount (§ 4.1) uses the 55-map board's FOURTH-N5 cell for stride B under the
3.7 verifier (0.8758, US$116.15), as findings §§ 3.3 and 5 do and as D25 did. P1 and the MCB
ladder (`{1, 3, 10}`) do not have that rung. Without it the ladder's steps are K = 1 → 3 at
US$0.99 per 0.001 F1 and K = 3 → 10 at US$17.69 (+0.0066 for US$116.76). Its last step is
then its dearest, and the count becomes **18 of 23** (`kl/recount.py` with the rung removed).
The outcome now discloses this.

### 4.9 Significant tile-MCC moves over every tested pair: six ladders fall, two rise

Every pair in `mcc-test/*.json` and `phase2/mcc-test/*.json` was tested: four per ladder
(K = 1 → best, 1 → 3, 3 → 5, 5 → 10), three on the two 3.7 arms and the fourth cell. Tier E's
six pairs come from `tier-e/ladder.json`. The significant MCC pairs are these:

- **3.7 arm 1**: K1-vs-K5 −0.0099, K1-vs-K3 −0.0067, K3-vs-K5 −0.0032.
- **3.7 arm 2**: K1-vs-K5 −0.0275, K1-vs-K3 −0.0258.
- **Fourth cell (stride B under the 3.7 verifier)**: K1-vs-K10 −0.0112, K1-vs-K3 −0.0095.
- **HIGH image T 1.0**: K1-vs-K10 −0.0637.
- **Both 55-map stride A ladders**: K3-vs-K5 −0.011052 / −0.011053 (BH p 0.0066), and
  K5-vs-K10 +0.004676 / +0.004684 (BH p 0.0300).

So six ladders have a significant fall somewhere on the ladder, and two a significant rise,
both at an intermediate step. From K = 1 to the best rung there are four falls and no rise,
which is what the outcome counts. Findings § 4.1 item 4 already records the stride A steps.
The unqualified signed sentence "NO ladder shows a significant tile-MCC RISE" was untrue as
worded at signing, and the dated clause now says so.

### 4.10 Astra item 1: admissibility, cost preference and the frontier, re-read at source

Every clause of Astra's suggested replacement holds in `mcb/summary.json` and the ladder
tables:

- **"K = 1 is the cheapest member of every tile-MCC admissible set"**: the minimum of
  `mcc.hsu_admissible_K` is 1 on all 22 ladders.
- **"no K = 1-to-best-rung comparison shows a significant MCC gain"**: none of the K = 1 → best
  pairs in `mcc-test/*.json`, `phase2/mcc-test/*.json` or `tier-e/ladder.json` has a
  significant positive MCC delta. The only significant rises, both 55-map stride A K = 5 → 10,
  do not involve K = 1 (§ 4.9).
- **"this does not exclude all larger rungs statistically"**: 20 of the 22 MCC sets contain a
  rung above K = 1, all but `55map-stride-b-g37vf-r2` and `37arm2-r2` (both `[1]`), and 13
  are the whole ladder. On `gs-stride-a` the set is `[1, 3, 5, 10]` and K = 10 has the highest
  point estimate (0.807855 against 0.794812).
- **"For F1, K = 3 lies on every observed cost frontier"**: a rung is on the frontier when no
  cheaper rung scores as well. K = 1 is K = 3's only cheaper rung, and K = 3's F1 exceeds
  K = 1's on all 23 ladders on either basis (the K = 1 → 3 column of § 4.1's table is
  positive throughout).
- **"cheapest MCB-admissible rung on only 10 of 22"**: the minimum of `f1.hsu_admissible_K`
  is 3 on 10 ladders (§ 4.5).

The signed sentence's two errors were these. "No rung above K = 1 is ever the admissible
choice" is false, because larger rungs are admissible on 20 of 22. "The F1-efficient rung is
K = 3" treats one member of a multi-rung frontier as the frontier. Findings § 6.1 item 3 and
the MCB deltas report (c) state the MCB result correctly ("on F1 the cheapest rung is almost
always ruled out; on tile-level discrimination it never is"), so item 1 needs no companion
edit.

### 4.11 Astra item 2: the resolution reading, re-read at source

- **The counterexample.** In `tension/effect-sizes.json` the deployment stride A row has
  `delta_f1` 0.0192 and `p_bh` 0.0 (full corpus). `mcc-test/summary.json` `55map-stride-a-r2`
  gives `f1_delta_k1_to_best` 0.019203 with `f1_p_bh_k1_to_best` 0.0. So "every one at or
  below +0.0223 does not [separate]" is false of the nine as worded. It holds of the
  gold-standard rows, which is how findings § 8.2 item 1 states it.
- **The rates.** `tension/subsample.json`: 39 and 197 of 200 draws significant at 487 tiles,
  for stride A (+0.019203) and stride B (+0.054685). These are two detection rates, which
  findings § 8.5 already calls "not a curve". "487 tiles resolve a ΔF1 of about 0.03 and above
  and not below" does not follow from them.
- **Effect size alone is not enough.** On the gold standard, as evaluated, +0.0338 (GS stride A,
  BH p 0.0024) separates and +0.0384 (MINIMAL image T 1.0, BH p 0.1236) does not
  (`phase2/mcc-test/summary.json`, `f1_delta_k1_to_best` 0.038344).
- **Where else the threshold appears.** Findings § 8.1's bold sentence (line 1273), the
  banner's summary of the 2026-09-12 revision (line 55), and § 8.4 item 3, which refers to
  "the ≈ 0.03 § 8.1 measured" (line 1453). § 7 edits all three under both options. The banner
  line is part of the revision history, so it gets a dated correction tag rather than a
  rewrite.

**A nuance, not a disagreement.** Version 1 read "separates" in that sentence as "at 487-tile
resolution", where deployment stride A does not separate (39 of 200 draws). Read that way,
the sentence was defensible, but nothing in its wording says so, and Astra's reading is the
natural one. Version 3 removes the ambiguity.

### 4.12 Length, and which version 2 additions were cut

Word counts (whitespace-delimited): signed 1,853; v2 2,832; v3 2,981. Of v3's text, 163 words
are reader aids that Astra and the coordinator asked for: the lead (104) and the definitions
of K, F1 with F1@20, tile-MCC and BH (59). Version 3's audit text, without them, is 2,818
words, 14 fewer than version 2's. The added corrections for Astra's items 1 to 4 are paid for
by these cuts to v2 additions, none of which loses a disclosure:

- **ON THE TWO OBJECTIVES**: v2's breakdown "(the 7 of the 15 above, five of the six withheld
  ladders, and tier E)". The MCB basis sentence already discloses that MCB counts include tier
  E and the six withheld ladders.
- **PARETO**: v2's parenthesis repeating the MCB basis ("which are computed on the cells as
  evaluated and so add tier E and the six withheld ladders"), which duplicated the MCB basis
  sentence.
- **THE TWO CORPORA AGREE**: a restatement of the 197 and 39 of 200 rates in words.
- **§ 8.6 detail**: the swing is stated once rather than twice, and the reference-set sentence
  is shortened ("…, tier E against the frame's 435 (D51), 7 of which lie outside the clipped
  area").
- **SHAPE**: the fourth-cell disclosure is shortened to a parenthesis.
- **Dated clause**: the qualifier note "(as first written, 'no ladder shows a significant
  tile-MCC rise' was untrue …)" is folded into the list of corrected statements.

**Further cuts the PI could make, each at a small cost to disclosure:**

- The intermediate-steps sentence (§ 3 row 8, 55 words) could shrink to "over every tested
  pair, six ladders show a significant fall and two a significant rise (findings § 4.1)". It
  would lose the stride A values.
- The fourth-cell parenthesis in SHAPE (§ 3 row 4c, 30 words) could move to the attestation
  alone. The count's basis would then not be visible in the register.

I recommend neither, because both disclose something a reader of the register would otherwise
miss.

## 5. Decisions for the PI

None of the decisions changed in substance from version 2. Astra agrees with A's
recommendation, on D51's recorded policy, and with B's 48.7 %. E and F now also cover the two
signed readings Astra found too broad, and a new decision, I, covers the lead and the
definitions.

**A. Which tier E reading leads in § 8.6.** D51's recorded text extends the clip to tier E
(`planning/pi-decisions-2026-09-20.md` line 75; the PI's own quoted words do not name tier E),
so the draft leads with it.

- *Option 1 (the draft):* clipped leads, with the as-evaluated reading beside it.
- *Option 2:* as evaluated leads, with the clipped reading beside it. The exact text is built
  and checked by `kl3/build3_opt2.py`; the full Option 2 outcome is `kl3/opt2/redraft-opt2.txt`.
  It makes four swaps to the v3 text:

  1. Dated clause: tier E is not on the clipped basis under Option 2. Replace

     ```text
     ladders), and tier E's gain in F1 (the detection score, combining precision and recall;
     F1@20 counts a match within 20 m), are now compared
     ```

     with

     ```text
     ladders) are now compared
     ```

  2. Dated clause: the F1 definition moves to F1's next use. Replace

     ```text
     the reduction in K's F1 gain after verification changes size
     ```

     with

     ```text
     the reduction in K's gain in F1 (the detection score, combining precision and recall;
     F1@20 counts a match within 20 m) after verification changes size
     ```

  3. Headline. Replace

     ```text
     and roughly halves K's observed F1 gain: 48.7 % smaller with tier E's rungs compared on
     the area every rung searched (D51), 60.3 % smaller as evaluated (§ 8.6, added on the
     PI's ruling 2026-09-13).
     ```

     with

     ```text
     and cuts K's observed F1 gain by about three-fifths: 60.3 % as evaluated, 48.7 % with
     tier E's rungs compared on the area every rung searched, D51's basis (§ 8.6, added on
     the PI's ruling 2026-09-13).
     ```

  4. Verified detail. Replace

     ```text
     and raises F1@20 by only +0.0338 with tile-MCC FALLING -0.0238 (as evaluated) once the
     same pool is verified. The clipped F1@20 is 0.8604 at K = 1
     (reports/scorer-frames-d50-d51-2026-10-08-scripts/out/ladders_new.json) and 0.8942 at K
     = 10, the restated rung of tier-e/ladder.json, whose union lies wholly in the common
     area so the clip removes nothing (that file's own K = 10 row, 0.8886, predates the
     re-verification); as evaluated, K = 1 reads 0.8680 and the gain is +0.0262. Tile-MCC
     (0.8211 at K = 1, 0.7973 at K = 10; tier-e/ladder.json and each rung's evaluation)
     exists only as evaluated; clipped tile-MCC has not been computed, so its sign and
     magnitude are unknown. The two stages share the common footprint but not the reference
     set: the consensus-only side is scored against the 428 mounds inside it, tier E against
     the frame's 435 (D51), 7 of which lie outside the clipped area. So, on these scoring
     bases, the observed F1 gain from extra passes is 48.7 % smaller once the pool is
     verified (one minus the ratio of the two gains, on unrounded values; 60.3 % as
     evaluated),
     ```

     with

     ```text
     and raises F1@20 by only +0.0262 with tile-MCC FALLING -0.0238 once the same pool is
     verified (0.8680/0.8211 at K = 1 and 0.8942/0.7973 at K = 10, as evaluated;
     tier-e/ladder.json and each rung's evaluation). On the clipped basis K = 1 reads 0.8604
     (reports/scorer-frames-d50-d51-2026-10-08-scripts/out/ladders_new.json) and K = 10 the
     same 0.8942, because that rung's union lies wholly in the common area and the clip
     removes nothing (that file's own K = 10 row, 0.8886, predates the re-verification), so
     the clipped gain is +0.0338; clipped tile-MCC has not been computed, so its sign and
     magnitude are unknown. The two stages share the common footprint only on the clipped
     basis, and never the reference set: the consensus-only side is scored against the 428
     mounds inside the footprint, tier E against the frame's 435, and its K = 1, 3 and 5
     rungs also searched a 37.94 km² band outside the footprint. So, on these scoring bases,
     the observed F1 gain from extra passes is 60.3 % smaller once the pool is verified (one
     minus the ratio of the two gains, on unrounded values; 48.7 % on the clipped basis),
     ```

  The lead is the same under both options, because it gives the reduction as "about half to
  three-fifths, depending on the scoring basis". § 7 carries both options' companion edits.
- *Recommendation: Option 1, on D51's recorded text, with the PI's confirmation.* Unclipped,
  K = 1 keeps credit for 6 band matches that K = 10 cannot earn (§ 4.6), so the as-evaluated
  reduction overstates what verification removes. Neither reading is like for like: the
  reference sets differ (428 against 435), and the outcome says so wherever it makes the
  comparison. Astra concurs that Option 1 is supported by the recorded D51 policy.

**B. 48.7 % or 48.8 %.** *Recommendation:* 48.7 %, from unrounded values. Astra reproduces
48.6919 % from the stated inputs and 48.7313 % with the MCB K = 10 statistic. § 7 assumes it.

**C. Tier E's tile-MCC on the clipped basis, the six withheld ladders in the MCB counts, and an
anchor for 48.7 %.** Unchanged from version 2: Option 1 now (report on the as-evaluated cells,
and say so), with Option 3 queued (build and commit clipped readings, a re-score with no API
spend). **Committing a clipped tier E reading would give the 48.7 % a committed anchor.** Today
its K = 10 input is inferred, and the only committed clipped file's stale K = 10 row gives
57.1 %. Version 3 also stops the text and the findings from implying that the as-evaluated
tile-MCC holds on the clipped basis: the reversal is stated for the as-evaluated cells only,
and the clipped sign and magnitude as unknown (Astra item 3). That is consistent with Option 1
here.

**D. "Nine" → "ten".** Unchanged: ten, with the partition in a parenthesis.

**E. Narrowing signed readings to what was tested.** Version 2 limited the tile-MCC rise and
fall statements to K = 1 against the best rung. Version 3 adds two more narrowings, both
disclosed in the dated clause:

- PARETO MCC SET now separates admissibility from cost preference and the frontier (Astra
  item 1, § 4.10). In particular, "no rung above K = 1 is ever the admissible choice" was
  false (20 of 22).
- THE TWO CORPORA AGREE now gives detection rates instead of a 0.03 threshold, and restricts
  the effect-size sorting to the gold-standard ladders (Astra item 2, § 4.11).

*Recommendation:* approve all of them. Each states only what the artefacts and findings
§§ 4.1, 8.2 and 8.5 already support.

**F. Fixes to unchanged signed sentences.** As in version 2: WITHHELD (three cells on two
rungs), NOT CLAIMED (11 of 15; 17 of 21 as evaluated), the as-evaluated marks, and one name
for the 3.7 ladder. Version 3 adds the § 8.6 wording: "measured directly rather than
inferred" becomes "consistent with … but does not measure it directly", "is a property of the
PIPELINE STAGE" becomes "on this pool … depends on the PIPELINE STAGE, not on K alone", and
the percentage is described as the reduction in the observed F1 gain under the stated scoring
bases (Astra item 4). *Recommendation:* approve.

**G. Length and order.** The dated clause is now three sentences, and the outcome is 2,981
words (§ 4.12). *Recommendation:* keep the audit detail as drafted; § 4.12 lists two further
cuts, neither recommended.

**H. Merge condition.** Unchanged: findings §§ 6.1, 8.1, 8.4 and 8.6 and the MCB deltas report
change in the same PR as the register text (§ 7).

**I. The plain-language lead and definitions (new; Astra item 5).** The lead ("IN BRIEF", three
sentences) follows the dated clause, as the coordinator specified. Because the dated clause
uses "F1" and "tile-MCC", those two are defined inside it at first use, with K defined in the
opening sentence and BH at its first use.

- *Option 1 (the draft):* this order.
- *Option 2:* move the lead to directly after the opening sentence, before the dated clause.
  An outside reader would then meet the explanation before the audit trail, and the
  definitions of F1 and tile-MCC could move into the lead, leaving the dated clause shorter.
  It would put the dated clause second rather than first among the additions, which departs
  from the order used on the other 14 rows.

*Recommendation:* Option 1 for consistency with the approved rows, unless the PI prefers
reader-first for this, the longest entry. Option 2 is a mechanical move.

## 6. Corrections the re-signing attestation should carry

The 2026-10-15 lapse note in `signature.attests` is not edited here. When the PI re-signs, the
attestation (or a superseding note) should carry the following corrections:

1. "(tension/effect-sizes.json is not rebuilt and still records 0.0629)": rebuilt in
   `62050794d`; it now records 0.06 for MINIMAL image T 0.7 on the clipped basis, with five
   rows' unclipped-basis fields withheld (`score_basis.n_withheld` 5).
2. "findings.md is not yet restated at 376eb1d50", and `signature.presentation`'s
   "findings.md not yet restated (last revised 2026-10-07)": restated in `de998a94d`.
3. "'… 13 of the 21' -> 8 of the 15" should read 7 of the 15. The signed 13 of 21 was 12 of 21
   from first publication, because tier E was counted on top (§ 4.4).
4. "+0.0131 (0.7948 -> 0.8079)": the artefact delta is 0.013043, so +0.0130. +0.0131 is the
   difference of rounded endpoints.
5. "the last step dearest on 12 of the 14 Phase 2 ladders (17 of 23 per that note)": now
   re-derived on the restated tables. It is 17 of 23 with the same six exceptions on either
   basis, counting the fourth cell's FOURTH-N5 board rung, and 18 without it (§ 4.8).
6. The first 2026-10-04 note's "four ladders' last steps lose F1": five across the 23, with
   tier E's last step losing F1 before and after the restatement (§ 4.3).
7. § 8.6's share: record the PI's choice of leading basis (decision A) and that D51's recorded
   text extends the clip to tier E. Give 48.7 % (decision B), and say that its K = 10 input is
   inferred: `ladders_new.json`'s K = 10 row (0.8886) predates the re-verification (§ 4.7).
   Record that the two stages are scored against 428 and 435 reference mounds.
8. "on nine ladders nothing below K = 5 is admissible" (listed as UNCHANGED) should read ten,
   wrong as worded since `b7e2821ba` (decision D).
9. "whether 'withheld' should remove those ladders from the MCB counts is for the PI": record
   the PI's ruling (decision C).
10. "STALE IN THE OUTCOME TEXT, left unchanged for the PI's wording: …": replace this with the
    date of approval of the redrafted text, and keep the before → after list as the record.
11. "no significant tile-MCC rise" and "the four significant falls" (listed as UNCHANGED): both
    now say "from K = 1 to the best rung". The unqualified rise statement was untrue as worded
    at signing, and over every tested pair it is six falls and two rises (decision E).
12. Inherited errors corrected in unchanged sentences (decision F): WITHHELD's "three of its
    four rungs" (three cells on two rungs) and NOT CLAIMED's "five" (11 of 15; 17 of 21 as
    evaluated).
13. The companion edits to findings §§ 6.1, 8.1, 8.4 and 8.6 and to the MCB deltas report landed
    with the re-signing (§ 7; cite their commit).
14. Branch commit hashes in the note (`64382beea`, `f53f6e97c`, `0fc2d6389`, `f6f10d605`,
    `376eb1d50`, and `62050794d` and `de998a94d` above) will not resolve from `main` if PR #52
    is squash-merged. Cite the merge commit or the record's paths.
15. The tile-MCC Pareto reading, unchanged in the lapse note, was too broad as signed (decision
    E, § 4.10). "No rung above K = 1 is ever the admissible choice" is false: the MCB admits a
    larger rung on 20 of 22 ladders. "The F1-efficient rung is K = 3" names one member of a
    multi-rung frontier. The re-signed text separates the cost-conscious choice (K = 1, the
    cheapest admissible tile-MCC rung everywhere) from statistical exclusion.
16. The 487-tile resolution, unchanged in the lapse note, was too broad as signed (decision E,
    § 4.11). "487 tiles resolve a ΔF1 of about 0.03 and above and not below" is a threshold
    that two detection rates (39 and 197 of 200) do not establish. "Every one at or below
    +0.0223 does not [separate]" is false of deployment stride A (+0.0192, BH p < 0.0001 on
    8,541 tiles). The re-signed text restricts the sorting to the gold-standard ladders. The
    same correction lands in findings §§ 8.1 and 8.4 and on the banner's history line (§ 7).
17. § 8.6's claim (decisions C and F): the 0.0682 swing and the sign reversal are the
    as-evaluated cells' alone, and the clipped tile-MCC's sign and magnitude are unknown. The
    comparison is consistent with the proposed mechanism but does not measure it directly. The
    percentage is the reduction in the observed F1 gain under stated scoring bases, which use
    different reference sets (428 and 435 mounds).

## 7. Companion document edits (both options of decision A)

These edits keep the documents the outcome cites consistent with it. They land in the same PR
as the register text (decision H). Each edit is an exact old → new replacement, applied in
the order listed. Each was checked against a scratch copy of the committed file (`git show
HEAD:<path>` at `062f92239`; both files are byte-identical at `e3a0d490c`): every `old`
occurs exactly once, and each option applies cleanly in full (21 replacements for each).
The edited copies pass `markdownlint-cli2` with the repository's `.markdownlint.json`. The
script and edited copies are `kl3/companion3.py` and `kl3/comp/option-{1,2}/`.

**What is new in version 3**:

- Astra item 2: F-banner-history, F-8.1 and F-8.4-item3.
- Astra item 3: F-8.6-claim (now under both options, with Astra's wording) and both
  F-8.6-restated variants.
- Astra item 4: F-8.6-heading (now under both options), F-8.4-item2 (both options),
  F-8.6-mechanism and F-8.6-evidence.
- Both banners and both changelog entries are rewritten to match.
- Astra item 1 needs no companion edit: findings § 6.1 item 3 and the deltas report (c)
  already state the MCB result correctly (§ 4.10).
- The deltas report's five edits are unchanged from version 2.

**Placeholders the applying session must fill**: `DXX`, the number of the PI's ruling on this
re-signing; `<landing-commit>`; and the date 2026-10-18, if the edits land later. Both
documents are in the Document Revision Policy's scope and already have a banner and a
changelog, so each gets a new banner lead and a new changelog entry. Past changelog entries
are not rewritten. The banner's history line about § 8 gets a dated correction tag, not a
rewrite. Decision B is assumed to be 48.7 %.

### 7.1 `results/k-ladder-2026-09-12/findings.md`

Not edited: the +0.0131 at lines 104, 382 and 522, which follows the § 4 table's endpoint
convention (0.7948 → 0.8079). The register uses +0.0130 because it quotes no endpoints.

**F-banner** (Option 1 (clipped leads; recommended))

Old:

```text
> **Last revised**: 2026-10-15 (S164 restatement pass, PI ruling D65 (2):
```

New:

```text
> **Last revised**: 2026-10-18 (re-signing of the register row
> `k-ladder-2026-09-12`, PI ruling DXX: §§ 8.4 and 8.6 now lead with tier E on
> PI ruling D51's clipped basis, on which verification makes K's observed F1
> gain 48.7 % smaller, with 60.3 % as evaluated beside it; § 8.6 states that
> its tile-MCC reversal is the as-evaluated cells' alone, that the two stages
> are scored against different reference sets (428 and 435 mounds), and that
> the comparison is consistent with the proposed mechanism rather than a
> direct measurement of it; § 8.1 restates the 487-tile resolution as two
> detection rates, not a threshold; § 6.1 corrected to ten ladders, not nine,
> on which a K = 3 rung can be ruled out as best, with its 'never worth its
> price' and withheld-rung wording corrected). Prior: 2026-10-15 (S164
> restatement pass, PI ruling D65 (2):
```

**F-banner** (Option 2 (as evaluated leads))

Old:

```text
> **Last revised**: 2026-10-15 (S164 restatement pass, PI ruling D65 (2):
```

New:

```text
> **Last revised**: 2026-10-18 (re-signing of the register row
> `k-ladder-2026-09-12`, PI ruling DXX: tier E keeps the unclipped reading in
> §§ 8.4 and 8.6, on which verification makes K's observed F1 gain 60.3 %
> smaller, with D51's clipped reading, corrected to 48.7 %, beside it; § 8.6
> states that its tile-MCC reversal is the as-evaluated cells' alone, that the
> two stages are scored against different reference sets (428 and 435
> mounds), and that the comparison is consistent with the proposed mechanism
> rather than a direct measurement of it; § 8.1 restates the 487-tile
> resolution as two detection rates, not a threshold; § 6.1 corrected to ten
> ladders, not nine, on which a K = 3 rung can be ruled out as best, with its
> 'never worth its price' and withheld-rung wording corrected). Prior:
> 2026-10-15 (S164 restatement pass, PI ruling D65 (2):
```

**F-banner-history** (both options)

Old:

```text
> is accounted for — 487 tiles resolve a ΔF1 of about 0.03 and above, and the
> nine MINIMAL ladders sort by effect size rather than by corpus — and § 8.4 adds
```

New:

```text
> is accounted for — 487 tiles resolve a ΔF1 of about 0.03 and above, and the
> nine MINIMAL ladders sort by effect size rather than by corpus (both corrected
> 2026-10-18: § 8.1 measures two detection rates, not a threshold, and the
> sorting holds on the gold-standard ladders, § 8.2) — and § 8.4 adds
```

**F-6.1-item1** (both options)

Old:

```text
   cheapest admissible rung is K = 1), nine admit nothing below K = 5, and one
   admits nothing below K = 10. So the review's Pareto reading — K = 3 is on the
   efficient set of every ladder — is a *cost* statement that the simultaneous
   instrument endorses on roughly half the corpus and declines on the other
   half: on nine ladders a K = 3 rung **can** be ruled out as best, even though
   it remains the efficient buy.
```

New:

```text
   cheapest admissible rung is K = 1), nine have K = 5 as their cheapest
   admissible rung, and one admits nothing below K = 10. So the review's Pareto
   reading — K = 3 is on the efficient set of every ladder — is a *cost*
   statement that the simultaneous instrument endorses on roughly half the
   corpus and declines on the other half: on ten ladders a K = 3 rung **can** be
   ruled out as best, even though it remains the efficient buy.
```

**F-6.1-item2** (both options)

Old:

```text
   have a K = 10 rung admit it. That is the formal counterpart of § 7.4's
   economic finding: the top rung is never statistically *excluded*, it is only
   never *worth* its price.
```

New:

```text
   have a K = 10 rung admit it. That is the formal counterpart of § 7.4's
   economic finding: the top rung is never statistically *excluded*, and
   whether it is *worth* its price is a cost question, which §§ 5 and 7.4 answer
   ladder by ladder (the last step is the worst buy on most ladders, not all).
```

**F-6.1-withheld** (both options)

Old:

```text
The tile-join invariant refuses the per-tile TP/FP/FN table of
three of its four rungs on this frame
```

New:

```text
The tile-join invariant refuses the per-tile TP/FP/FN table of
three cells on two of its four rungs, K = 1 and K = 3, on this frame
```

**F-8.1** (both options)

Old:

```text
almost every draw. **At 487 tiles this instrument resolves a ΔF1 of roughly
0.03 and above, and does not resolve one below it** — and that is measured on
cells whose full-corpus p-value is below the permutation floor.
```

New:

```text
almost every draw. **These are detection rates for two effects, not a
threshold**: at 487 tiles a gain of +0.055 is detected in 98.5 % of draws and
one of +0.019 in 19.5 %, both measured on cells whose full-corpus p-value is
below the permutation floor. They place the 487-tile resolution limit between
the two effects without fixing it, and § 8.2's gold-standard ladders show
effects between them falling on either side (+0.0338 separates, +0.0384 does
not). Until 2026-10-18 this paragraph read the two rates as a threshold,
"roughly 0.03 and above", which they do not establish.
```

**F-8.4-restated** (Option 1 (clipped leads; recommended))

Old:

```text
These are the unclipped readings, which this pass restates. Tier E's rungs
searched different areas, and D51's text extends its clip to tier E; on that
clipped basis K = 1 / 3 / 5 / 10 read 0.8604 / 0.8902 / 0.8968 / 0.8942
(K = 1 to 5: `reports/scorer-frames-d50-d51-2026-10-08-scripts/out/ladders_new.json`,
`tier_e` → `d51_clipped`; K = 10, whose clip removes nothing, is recorded in
`reports/s164-agent-records/restatement-pass.md` § 1.4). Which reading tier E
reports is for the PI; the tile-MCC column and the tests below are unclipped.
```

New:

```text
These are the unclipped readings, which this pass restates. Tier E's rungs
searched different areas: K = 1, 3 and 5 searched a 37.94 km² band that the
K = 10 union, filtered upstream to the grid study's common footprint, does not
cover. PI ruling D51 compares a ladder's rungs on the area every rung searched
and extends that rule to tier E, so § 8.6 leads with the clipped reading (PI
ruling DXX): K = 1 / 3 / 5 / 10 read 0.8604 / 0.8902 / 0.8968 / 0.8942
(K = 1 to 5: `reports/scorer-frames-d50-d51-2026-10-08-scripts/out/ladders_new.json`,
`tier_e` → `d51_clipped`; that file's K = 10 row, 0.8886, predates the
re-verification, and the restated K = 10 rung's clip removes nothing, since
its `area_removed_km2` is 0, so its clipped value is the 0.8942 below). No
committed artefact yet holds the clipped ladder whole. D51 keeps the frame's
435 reference mounds, 7 of which lie in the band, so every clipped rung is
also scored against 7 mounds outside the area it was clipped to. The table,
the tile-MCC column and the tests below are the unclipped readings, because
no clipped per-tile table exists.
```

**F-8.4-restated** (Option 2 (as evaluated leads))

Old:

```text
`tier_e` → `d51_clipped`; K = 10, whose clip removes nothing, is recorded in
`reports/s164-agent-records/restatement-pass.md` § 1.4). Which reading tier E
reports is for the PI; the tile-MCC column and the tests below are unclipped.
```

New:

```text
`tier_e` → `d51_clipped`; that file's K = 10 row, 0.8886, predates the
re-verification, and the restated K = 10 rung's clip removes nothing, since
its `area_removed_km2` is 0, so its clipped value is the 0.8942 below; no
committed artefact yet holds the clipped ladder whole). The PI ruled (DXX)
that tier E reports the unclipped reading, with the clipped one beside it;
the tile-MCC column and the tests below are unclipped.
```

**F-8.4-item2** (Option 1 (clipped leads; recommended))

Old:

```text
2. **The verifier absorbs about 60 % of K's F1 return and reverses tile-MCC's
   response to it.** § 8.3's consensus-only ladder on this same pool and
   geometry gains **+0.0660** F1 from K = 1 to K = 10 with tile-MCC **rising**
   +0.0444; verified, the same pool gains **+0.0262** with tile-MCC **falling**
   −0.0238. So the verifier takes roughly three-fifths of what extra passes buy
   on F1 — because it was already removing much of what extra passes remove —
   and turns a tile-level *gain* into a tile-level *loss*, a swing of 0.068
   MCC. Before the 2026-10-15 restatement this read about 40 % (+0.0340
   against +0.0572) with a swing of 0.075; on D51's clipped basis the share is
   about 49 % (§ 8.6).
```

New:

```text
2. **After the verifier, K's observed F1 gain is about half as large, and its
   tile-MCC effect reverses on the cells as evaluated.** § 8.3's consensus-only
   ladder on this same pool and geometry gains **+0.0660** F1 from K = 1 to
   K = 10 with tile-MCC **rising** +0.0444; verified, the same pool gains
   **+0.0338** on D51's clipped basis (+0.0262 as evaluated) with tile-MCC
   **falling** −0.0238 (as evaluated). So the observed F1 gain from extra
   passes is 48.7 % smaller once verified (60.3 % as evaluated), consistent
   with the verifier already removing much of what extra passes remove, and
   on the cells as evaluated a tile-level *gain* becomes a tile-level *loss*,
   a swing of 0.068 MCC. Before the 2026-10-15 restatement this read about
   40 % (+0.0340 against +0.0572) with a swing of 0.075 (§ 8.6).
```

**F-8.4-item2** (Option 2 (as evaluated leads))

Old:

```text
2. **The verifier absorbs about 60 % of K's F1 return and reverses tile-MCC's
   response to it.** § 8.3's consensus-only ladder on this same pool and
   geometry gains **+0.0660** F1 from K = 1 to K = 10 with tile-MCC **rising**
   +0.0444; verified, the same pool gains **+0.0262** with tile-MCC **falling**
   −0.0238. So the verifier takes roughly three-fifths of what extra passes buy
   on F1 — because it was already removing much of what extra passes remove —
   and turns a tile-level *gain* into a tile-level *loss*, a swing of 0.068
   MCC. Before the 2026-10-15 restatement this read about 40 % (+0.0340
   against +0.0572) with a swing of 0.075; on D51's clipped basis the share is
   about 49 % (§ 8.6).
```

New:

```text
2. **After the verifier, K's observed F1 gain is about three-fifths smaller,
   and its tile-MCC effect reverses on the cells as evaluated.** § 8.3's
   consensus-only ladder on this same pool and geometry gains **+0.0660** F1
   from K = 1 to K = 10 with tile-MCC **rising** +0.0444; verified, the same
   pool gains **+0.0262** with tile-MCC **falling** −0.0238 (both as
   evaluated). So the observed F1 gain from extra passes is 60.3 % smaller
   once verified, consistent with the verifier already removing much of what
   extra passes remove, and on the cells as evaluated a tile-level *gain*
   becomes a tile-level *loss*, a swing of 0.068 MCC. Before the 2026-10-15
   restatement this read about 40 % (+0.0340 against +0.0572) with a swing of
   0.075; on D51's clipped basis the reduction is 48.7 % (§ 8.6).
```

**F-8.4-item3** (both options)

Old:

```text
   **+0.0262** at BH p = 0.0292, both below the ≈ 0.03 § 8.1 measured,
   while MINIMAL image T 1.0 does not resolve **+0.0384**.
```

New:

```text
   **+0.0262** at BH p = 0.0292, both between § 8.1's two measured effects
   (+0.019 and +0.055), while MINIMAL image T 1.0 does not resolve **+0.0384**.
```

**F-8.6-heading** (Option 1 (clipped leads; recommended))

Old:

```text
### 8.6 CLAIM — the verifier absorbs about 60 % of K's F1 return and reverses the sign of its tile-MCC effect
```

New:

```text
### 8.6 CLAIM — after the verifier, K's observed F1 gain is about half as large and its tile-MCC effect reverses (as evaluated)
```

**F-8.6-heading** (Option 2 (as evaluated leads))

Old:

```text
### 8.6 CLAIM — the verifier absorbs about 60 % of K's F1 return and reverses the sign of its tile-MCC effect
```

New:

```text
### 8.6 CLAIM — after the verifier, K's observed F1 gain is about three-fifths smaller and its tile-MCC effect reverses (as evaluated)
```

**F-8.6-claim** (Option 1 (clipped leads; recommended))

Old:

```text
| **verified** (Gemini 3 verifier) | **+0.0262** | **−0.0238** |

The verifier therefore **absorbs 60.3 % of K's F1 return** (1 − 0.0262 / 0.0660)
and **reverses the sign of K's tile-MCC effect**, a swing of **0.0682** MCC.
```

New:

```text
| **verified** (Gemini 3 verifier), D51's clipped basis | **+0.0338** | **−0.0238** (as evaluated) |
| verified, as evaluated | +0.0262 | −0.0238 |

On these scoring bases the observed F1 gain from extra passes is therefore
**48.7 % smaller** once verified (1 − 0.033840 / 0.065954, on unrounded values;
60.3 % as evaluated, 1 − 0.026191 / 0.065954), and on the cells as evaluated
**the sign of K's tile-MCC effect reverses**, a swing of **0.0682** MCC. The
0.0682 MCC swing and sign reversal refer only to the as-evaluated cells.
Clipped tile-MCC has not been computed, so its sign and magnitude are unknown.
```

**F-8.6-claim** (Option 2 (as evaluated leads))

Old:

```text
| **verified** (Gemini 3 verifier) | **+0.0262** | **−0.0238** |

The verifier therefore **absorbs 60.3 % of K's F1 return** (1 − 0.0262 / 0.0660)
and **reverses the sign of K's tile-MCC effect**, a swing of **0.0682** MCC.
```

New:

```text
| **verified** (Gemini 3 verifier), as evaluated | **+0.0262** | **−0.0238** |

On these scoring bases the observed F1 gain from extra passes is therefore
**60.3 % smaller** once verified (1 − 0.026191 / 0.065954, on unrounded values;
48.7 % on D51's clipped basis, § 8.4), and **the sign of K's tile-MCC effect
reverses**, a swing of **0.0682** MCC. The 0.0682 MCC swing and sign reversal
refer only to the as-evaluated cells. Clipped tile-MCC has not been computed,
so its sign and magnitude are unknown.
```

**F-8.6-restated** (Option 1 (clipped leads; recommended))

Old:

```text
(0.8886 → 0.8942; tile-MCC 0.7903 → 0.7973). On PI ruling D51's clipped
basis, which D51's text extends to tier E and which the PI has not yet
applied to it, the verified gain is +0.0338 (0.8604 → 0.8942) and the share
**48.8 %** (1 − 0.0338 / 0.0660); the reading above is the unclipped one, as
this pass restates tier E (§ 8.4), and the choice between them is the PI's.
The tile-MCC figures are the unclipped cells' on either reading (no clipped
tile-MCC exists), so the sign reversal is the same on both.
```

New:

```text
(0.8886 → 0.8942; tile-MCC 0.7903 → 0.7973). The 2026-10-15 restatement led
with the unclipped reading. PI ruling D51 compares a ladder's rungs on the
area every rung searched and extends that rule to tier E, so this section
now leads with the clipped reading (PI ruling DXX): the verified gain is
+0.0338 (0.8604 → 0.8942) and the reduction **48.7 %** (§ 8.4 gives the
anchors and why the clipped K = 10 value is the restated rung's).
The tile-MCC figures are the as-evaluated cells' on either reading: clipped
tile-MCC has not been computed, so whether the sign reversal holds on the
clipped basis is unknown.

**The two stages are not scored against the same reference set.** The
consensus-only side is scored on the grid study's common footprint against
the 428 reference mounds inside it
(`results/grid-2026-08-18/grid_analysis.json`,
`scope.footprint_audit.common_ground_truth`); tier E is scored against the
frame's 435, which D51 keeps, so each clipped tier E rung is also scored
against 7 mounds outside the area it was clipped to. The clipped reading
matches the consensus side's area but not its references, and the unclipped
reading matches neither.
```

**F-8.6-restated** (Option 2 (as evaluated leads))

Old:

```text
basis, which D51's text extends to tier E and which the PI has not yet
applied to it, the verified gain is +0.0338 (0.8604 → 0.8942) and the share
**48.8 %** (1 − 0.0338 / 0.0660); the reading above is the unclipped one, as
this pass restates tier E (§ 8.4), and the choice between them is the PI's.
The tile-MCC figures are the unclipped cells' on either reading (no clipped
tile-MCC exists), so the sign reversal is the same on both.
```

New:

```text
basis, which D51 extends to tier E, the verified gain is +0.0338
(0.8604 → 0.8942) and the reduction **48.7 %** (1 − 0.033840 / 0.065954, on
unrounded values); the reading above is the unclipped one, which the PI ruled
(DXX) that tier E reports (§ 8.4).
The tile-MCC figures are the as-evaluated cells' on either reading: clipped
tile-MCC has not been computed, so whether the sign reversal holds on the
clipped basis is unknown.

**The two stages are not scored against the same reference set.** The
consensus-only side is scored on the grid study's common footprint against
the 428 reference mounds inside it
(`results/grid-2026-08-18/grid_analysis.json`,
`scope.footprint_audit.common_ground_truth`); tier E is scored against the
frame's 435, and its K = 1, 3 and 5 rungs also searched the 37.94 km² band
outside that footprint. The clipped reading matches the consensus side's area
but not its references, and the unclipped reading matches neither.
```

**F-8.6-anchor** (both options)

Old:

```text
  detections. These are the first and last rows of § 8.4's table.
```

New:

```text
  detections. These are the first and last rows of § 8.4's table.
- Verified, D51's clipped basis — **K = 1**
  `reports/scorer-frames-d50-d51-2026-10-08-scripts/out/ladders_new.json`,
  `tier_e.rungs[0].points.opmax.d51_clipped.f1` **0.8604** (453 detections,
  29 removed); **K = 10** the restated rung above, **0.8942**, whose clip
  removes nothing (`tier_e.assessed_area.clip.area_removed_km2` is 0 at
  K = 10). That file's own K = 10 row (0.8886) predates the re-verification;
  read with it, the reduction would be 57.1 %.
```

**F-8.6-mechanism** (both options)

Old:

```text
**The mechanism, in two sentences.**
```

New:

```text
**The proposed mechanism, in two sentences.**
```

**F-8.6-evidence** (both options)

Old:

```text
**What it is evidence for, and its limits.** This is the corpus's cleanest
evidence that **tile-MCC's response to K is a property of the pipeline stage
rather than of K** — compare
```

New:

```text
**What it is evidence for, and its limits.** This is the corpus's cleanest
evidence that, on this pool, **tile-MCC's response to K depends on the pipeline
stage rather than on K alone**. It is consistent with the proposed mechanism
above but does not measure it directly, and its tile-MCC half rests on the
as-evaluated cells — compare
```

**F-changelog** (Option 1 (clipped leads; recommended))

Old:

```text
## Changelog

### 2026-10-15 — S164 restatement pass:
```

New:

```text
## Changelog

### 2026-10-18 — Re-signing: tier E on D51's clipped basis; claims qualified

**Trigger**: the PI's re-signing of the register row `k-ladder-2026-09-12`
after the S164 restatement (PI ruling DXX). Its redrafted outcome leads with
tier E on PI ruling D51's clipped basis and corrects statements that were
wrong or too broad from first publication; this document is brought into
line. Landed in `<landing-commit>`.

| Claim | Before | After |
|---|---|---|
| § 8.6 heading and claim | the verifier absorbs about 60 % (60.3 %, unclipped); the sign reversal "the same on both" readings | K's observed F1 gain about half as large: 48.7 % smaller on D51's clipped basis, 60.3 % as evaluated; the reversal stated for the as-evaluated cells only |
| § 8.6 clipped reduction | 48.8 % (1 − 0.0338 / 0.0660, on rounded gains) | 48.7 % (1 − 0.033840 / 0.065954) |
| § 8.4 item 2, verified gain | +0.0262 (about 60 %) | +0.0338 clipped, +0.0262 as evaluated (about half) |
| § 8.1, 487-tile resolution | "resolves a ΔF1 of roughly 0.03 and above, and does not resolve one below it" | two detection rates, 98.5 % at +0.055 and 19.5 % at +0.019, not a threshold |
| § 6.1 item 1, ladders on which a K = 3 rung can be ruled out as best | nine | ten (nine whose cheapest admissible rung is K = 5, one with only K = 10) |
| § 6.1, the withheld family's refused rungs | three of its four rungs | three cells on two rungs (K = 1 and K = 3) |

**Also**: § 6.1 item 2's "it is only never *worth* its price" is replaced,
because the last step is not the worst buy on six of the 23 ladders (the row's
signature note of 2026-10-04, ruling D25). § 8.6 calls its mechanism proposed
and the comparison consistent with it rather than a direct measurement, and
with § 8.4 states that the consensus-only side is scored against 428
reference mounds and tier E against 435. § 8.4 item 3 refers to § 8.1's two
measured effects. The banner's 2026-09-12 summary of § 8 carries a
correction tag rather than a rewrite.

**What did NOT change**: every F1, tile-MCC, cost, tier, admissible set and
test; the 0.0682 swing on the as-evaluated cells; § 8.4's table, which stays
on the unclipped readings. No artefact was regenerated.

### 2026-10-15 — S164 restatement pass:
```

**F-changelog** (Option 2 (as evaluated leads))

Old:

```text
## Changelog

### 2026-10-15 — S164 restatement pass:
```

New:

```text
## Changelog

### 2026-10-18 — Re-signing: tier E stays unclipped; claims qualified

**Trigger**: the PI's re-signing of the register row `k-ladder-2026-09-12`
after the S164 restatement (PI ruling DXX, which keeps tier E on the
unclipped reading with D51's clipped reading beside it). The redrafted
outcome corrects statements that were wrong or too broad from first
publication; this document is brought into line. Landed in
`<landing-commit>`.

| Claim | Before | After |
|---|---|---|
| § 8.6 heading and claim | the verifier absorbs about 60 %; the sign reversal "the same on both" readings | K's observed F1 gain about three-fifths smaller (60.3 %); the reversal stated for the as-evaluated cells only |
| § 8.6 and § 8.4 item 2, clipped reduction | 48.8 % (1 − 0.0338 / 0.0660, on rounded gains); about 49 % | 48.7 % (1 − 0.033840 / 0.065954) |
| § 8.1, 487-tile resolution | "resolves a ΔF1 of roughly 0.03 and above, and does not resolve one below it" | two detection rates, 98.5 % at +0.055 and 19.5 % at +0.019, not a threshold |
| § 6.1 item 1, ladders on which a K = 3 rung can be ruled out as best | nine | ten (nine whose cheapest admissible rung is K = 5, one with only K = 10) |
| § 6.1, the withheld family's refused rungs | three of its four rungs | three cells on two rungs (K = 1 and K = 3) |

**Also**: § 6.1 item 2's "it is only never *worth* its price" is replaced,
because the last step is not the worst buy on six of the 23 ladders (the row's
signature note of 2026-10-04, ruling D25). §§ 8.4 and 8.6 record the PI's
choice; § 8.6 calls its mechanism proposed and the comparison consistent with
it rather than a direct measurement, and states that the consensus-only side
is scored against 428 reference mounds and tier E against 435. § 8.4 item 3
refers to § 8.1's two measured effects. The banner's 2026-09-12 summary of
§ 8 carries a correction tag rather than a rewrite.

**What did NOT change**: every F1, tile-MCC, cost, tier, admissible set and
test; § 8.6's leading 60.3 % and the 0.0682 swing on the as-evaluated cells.
No artefact was regenerated.

### 2026-10-15 — S164 restatement pass:
```

### 7.2 `reports/k-ladder-mcb-deltas-2026-09-13.md`

A dated record by the restatement pass's choice (`restatement-pass.md` § 9). Only statements
wrong on its own date are corrected, and its § 2 claims table stays as of 2026-09-13.

**D-banner** (both options)

Old:

```text
> **Last revised**: 2026-10-04 (the quoted last-step prices corrected for the K-ladder's 1,000x units slip). Prior: 2026-09-13 (original publication). See
```

New:

```text
> **Last revised**: 2026-10-18 (three statements corrected that were wrong on their own date: ten ladders, not nine, admit nothing below K = 5; the top rung is not "only never worth its price"; and the withheld family's refusal falls on three cells on two rungs, not three rungs. § 2's claims table stays as of 2026-09-13). Prior: 2026-10-04 (the quoted last-step prices corrected for the K-ladder's 1,000x units slip). Prior: 2026-09-13 (original publication). See
```

**D-2a-nine** (both options)

Old:

```text
roughly half the corpus and declined on the other half: on nine ladders nothing
below K = 5 is admissible, even though K = 3 remains the efficient *buy*, so
```

New:

```text
roughly half the corpus and declined on the other half: on ten ladders nothing
below K = 5 is admissible (nine whose cheapest admissible rung is K = 5, and
one with only K = 10), even though K = 3 remains the efficient *buy*, so
```

**D-2b-worth** (both options)

Old:

```text
*(b)* The top rung is never statistically excluded, only never worth its price —
the formal counterpart of § 7.4's
```

New:

```text
*(b)* The top rung is never statistically excluded; whether it is worth its price
is the cost question answered by § 7.4's
```

**D-5-withheld** (both options)

Old:

```text
- **The withheld cells stay withheld.** The three Gemini 3.7 gold-standard text
  rungs' per-tile table is still refused on this frame,
```

New:

```text
- **The withheld cells stay withheld.** The per-tile table of three Gemini 3.7
  gold-standard text cells, on two rungs (K = 1 and K = 3), is still refused on
  this frame,
```

**D-changelog** (both options)

Old:

```text
## Changelog

### 2026-10-04 — WP4b straggler correction
```

New:

```text
## Changelog

### 2026-10-18 — Three statements wrong on their own date

**Trigger**: the re-signing of the register row `k-ladder-2026-09-12` (PI
ruling DXX), whose redrafted outcome corrects the first two. Landed in
`<landing-commit>`.

| Claim | Before | After |
|---|---|---|
| ladders on which nothing below K = 5 is admissible, § 2 (a) | nine | ten: nine whose cheapest admissible rung is K = 5, and one with only K = 10 (`summary.json` at `b7e2821ba`) |
| the withheld family's refusal, § 5 | three rungs | three cells on two rungs (K = 1 and K = 3) |

Reading (b)'s "only never worth its price" is replaced: on this document's own
figures the last step was not the worst buy on six of the 23 ladders (the
row's signature note of 2026-10-04, ruling D25). **What did NOT change**:
§ 2's claims table, which stays as of 2026-09-13 (the S164 restatement moved
three of its rows, and the restated values are in
`results/k-ladder-2026-09-12/findings.md` § 6.1), and every MCB set.

### 2026-10-04 — WP4b straggler correction
```

## 8. Change log against version 2

| Astra item | Fix in version 3 |
|---|---|
| 1 (P2): admissibility, cost preference and frontier conflated in PARETO MCC SET | PARETO rewritten on Astra's suggested lines, each clause re-read at source (§ 4.10; § 3 row 12). "K = 1 is the cheapest member of every tile-MCC set …", "no K = 1 -> best-rung comparison shows a significant MCC gain", "the cost-conscious choice … when the rule is to take the cheapest rung not ruled out as best; larger rungs are not excluded (the MCB admits one on 20 of 22 ladders)", "For F1, K = 3 is on every ladder's observed cost frontier but is the cheapest MCB-admissible rung on only 10 of 22". ON THE TWO OBJECTIVES no longer says the MCB "establishes" PARETO: "the simultaneous instrument agrees with the pairwise tests that K = 1 is never ruled out on tile-MCC, while on F1 it almost always is" (row 21). Disclosed in the dated clause. No companion edit is needed, because findings § 6.1 and the deltas report state the MCB result correctly |
| 2 (P2): the nine-ladder sorting has a counterexample; the 0.03 threshold is too categorical | THE TWO CORPORA AGREE now gives "detection rates for two effects, not a threshold (+0.0192 separates on all 8,541 tiles)" and restricts the sorting to the gold-standard ladders, as evaluated, naming the two in-between effects (+0.0338 separates; +0.0384, BH p = 0.1236, does not) (§ 3 row 11, § 4.11). Disclosed in the dated clause. Companion edits under both options: findings § 8.1 (F-8.1), the banner's 2026-09-12 history line (F-banner-history, a dated correction tag) and § 8.4 item 3 (F-8.4-item3) |
| 3 (P2): unmeasured clipped tile-MCC described as invariant | The outcome now says "(as evaluated)" beside the first −0.0238, and "clipped tile-MCC has not been computed, so its sign and magnitude are unknown". The swing and reversal are stated "on the cells as evaluated" (§ 3 rows 14–15). In § 7, F-8.6-claim (both options) carries Astra's wording verbatim, and both F-8.6-restated variants say "whether the sign reversal holds on the clipped basis is unknown"; neither says "the same on both" any longer. The § 8.6 heading and § 8.4 item 2 say "(as evaluated)" too |
| 4 (editorial): "measured directly rather than inferred"; the percentage | The outcome now reads "consistent with the mechanism proposed … but does not measure it directly", and "on this pool … depends on the PIPELINE STAGE, not on K alone". The percentage is "the observed F1 gain from extra passes is 48.7 % smaller once the pool is verified … on these scoring bases". The headline says "roughly halves K's observed F1 gain", and the dated clause says "reduction". The reference-set caveat is kept. The same qualification in findings: the § 8.6 heading, the claim sentence, "The proposed mechanism" (F-8.6-mechanism), "What it is evidence for" (F-8.6-evidence) and § 8.4 item 2, under both options |
| 5 (editorial): a plain-language lead and definitions | "IN BRIEF", three sentences, after the dated clause (no new claim; § 3 row 3b). K is defined in the opening sentence; F1 (with F1@20) and tile-MCC at their first use, in the dated clause; BH at its first use. The audit detail is 14 words shorter than version 2's, and the v2 additions that were cut are listed in § 4.12. Decision I offers the reader-first order |

**Also changed.** In SHAPE, "MCB" had been used before its definition (version 2's
fourth-cell sentence); version 3 says "the ladder inventory" there. In Option 2, the dated
clause's F1 definition moves to F1's next use. The restatement record is cited by section,
because its line numbers moved at `062f92239`.

### Where I differ from Astra, with evidence

1. **Item 2: a nuance, not a disagreement.** The signed "every one at or below +0.0223 does
   not" can be read at 487-tile resolution, where deployment stride A does not separate (39 of
   200 draws, `tension/subsample.json`). Version 1 read it that way. The words do not say so,
   though, and the natural reading is false of stride A on its full 8,541 tiles (`p_bh` 0.0).
   I adopted Astra's fix.
2. **Item 5's placement.** The coordinator asked for the lead after the dated clause and for
   definitions at first use. The dated clause uses F1 and tile-MCC, so they are defined there,
   which weighs on it. Astra's rationale (the audit trail should not be the reader's first
   explanation) points to the lead first. I followed the coordinator and put the alternative
   to the PI as decision I.
3. **Nothing else is disputed.** Astra's reproduced figures all match mine: 17/23, five losing
   last steps, 31.49–62.45 %, 37.18–92.99 %, US$0.198–26.752, 7/15 and 13/22, the 2/10/9/1
   partition, six falls and two rises across all pairs, 48.6919 % and 60.2888 %, and the
   0.06819685 swing. Its counts of companion replacements (16 for Option 1 and 14 for Option
   2 in version 2) match `kl2/companion.py`. Version 3 has 21 for each.
