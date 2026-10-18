# Redraft of the register outcome `k-ladder-2026-09-12`, version 2 (PR #52, § 4.12)

- **Drafter**: Claude (Anthropic), Claude Code, model lane Opus 5.5 (`claude-opus-5-5`),
  read-only sub-agent.
- **Date**: 2026-10-18.
- **Read from**: `/home/shawn/worktrees/map-reader-llm/claude-pr52-restate`, branch
  `restatement-pass-s164`, head `e3a0d490c`, working tree clean. During the work another
  session committed `c24d5a04f` ("apply 14 PI-approved outcome texts", D69) on the branch. It
  changes the other 14 rows' outcomes only: the `k-ladder-2026-09-12` row, `findings.md` and
  the MCB deltas report are byte-identical at both commits, so everything below holds at
  `c24d5a04f` too. Nothing in the worktree was written, staged or switched. No model API was called and no heavy computation was run: every
  figure below is a lookup in committed JSON or CSV, or arithmetic on such lookups.
- **Brief**: the coordinator's eight points on version 1, and the independent verifier's report
  `k-ladder-redraft-verify.md` (verdict PASS WITH FIXES, 56 of 59 numbers OK). § 8 maps every
  issue to its fix.
- **Method**: as in version 1, the outcome is built mechanically from the CURRENT REGISTER
  outcome (`results/run-analyses.json`, row `k-ladder-2026-09-12`, `outcome`), here by 25 exact
  replacements, each asserted to match once (`kl2/build2.py`). Every sentence not listed in § 3
  is therefore byte-identical to the signed text. Decision A's Option 2 text is built and
  checked the same way (`kl2/build2_opt2.py`). The companion edits in § 7 were applied to scratch
  copies of the committed files and linted (`kl2/companion.py`). Recounts: `kl/recount.py`.

## 1. The redrafted outcome (decision A, Option 1: clipped leads)

```text
The pass-count ladder K at otherwise fixed parameters, on 23 ladders:
the gold-standard stride A ladder (the only one whose every rung is an
exact re-verification of its own first-N union), the thirteen Gemini 3
pv-diag-384 families and the Gemini 3.7 gold-standard text ladder that
Phase 2 completed to four rungs for US$24.8065, the grid 384 px / 50 %
MINIMAL text ladder tier E completed for US$4.9595, and the seven 55-map
deployment ladders. Restated 2026-10-15 (D62 (1), D50, D51, D57 (2) and
(3), D65 (2), D67 (5)): each consensus cluster is now scored on the
tiles it was seen on, which moves the grid study's consensus-only
ladders; candidates the verifier had been shown on crops cut from the
neighbouring map sheet, largely blank, were re-verified on crops from
their own sheet (2026-10-13), which moves every rung of the
gold-standard stride A ladder, tier E's K = 10 rung and the 3.7
gold-standard text ladder's K = 5 and K = 10 rungs; the scorer now
scores each detection on the map sheet it was found on (D50), which
moves tier E's K = 1, 3 and 5 rungs and the 3.7 gold-standard text
ladder's K = 1 and K = 3; and seven Phase 2 ladders (the 3.7
gold-standard text ladder and six Gemini 3 ladders), and tier E's F1
gain below, are now compared on the area every rung searched (D51), a
basis on which no tile-MCC has been computed, so the seven ladders'
tile-MCC is withheld; figures on the earlier, unclipped basis are marked
'as evaluated'. No verdict moved; the verifier's share of K's F1 return
changes size, and the text now carries the re-pricing and corrections in
the two signature notes the PI approved on 2026-10-04 (the second under
D25), corrects two counts that were wrong from first publication (how
often K = 1 has the highest tile-MCC, and on how many ladders every rung
below K = 5 is ruled out as the best: ten, not nine), and limits the
tile-MCC rise and fall statements to the comparison they count, K = 1
against the best rung (as first written, 'no ladder shows a significant
tile-MCC rise' was untrue of both 55-map stride A ladders, which rise
significantly from K = 5 to K = 10). SHAPE: the return is FRONT-LOADED
and K = 3 is on the efficient set of every ladder in the corpus (a rung
is efficient when no cheaper rung of the same ladder scores as well) —
37 % to 93 % of a ladder's total F1 gain for 31 % to 62 % of its top
rung's cost — while the last step (K = 5 -> 10, or K = 3 -> 5 on the two
55-map 3.7 arms, which have no K = 10 rung) is the worst buy, the
dearest per 0.001 F1 or a loss of F1, on 17 of the 23 ladders; on the
other six (the gold-standard stride A ladder, the two 55-map stride B
ladders under the Gemini 3 verifier, stride B under the 3.7 verifier,
MINIMAL image T 0.3 and HIGH image T 1.0) the K = 3 -> 5 step is worse.
The 17 counts stride B under the 3.7 verifier with its K = 5 rung, a
55-map board cell (findings § 3.3) that the MCB sets below do not
include; without that rung its last step, K = 3 -> 10, is its dearest
and the count is 18. Where the last step gains F1 it costs about US$0.20
(gold-standard stride A) to US$27 (55-map 3.7 arm 1) per 0.001 F1
gained; on five ladders it loses F1 (MINIMAL text T 0.3 and T 0.7, HIGH
text T 0.3, HIGH image T 0.7, and tier E); the 3.7 gold-standard text
ladder's K = 5 -> K = 10 step, for example, buys +0.0004 F1@20 for
US$8.68. WHAT GOVERNS THE RETURN: the proposer's thinking level, and
within a level its temperature. The K = 1 -> best-rung F1 gain is
significant on 7 of 7 HIGH-thinking ladders and 2 of 6 MINIMAL ones, and
four ladders, every one of them MINIMAL, greedy-clique into a SINGLE
tier in which K buys nothing detectable (both tested on the cells as
evaluated); and on both HIGH tracks the gain rises monotonically with
temperature (text +0.0559 -> +0.0735 -> +0.0955, image +0.0780 ->
+0.0959 -> +0.1514 across T 0.3 -> 0.7 -> 1.0; text T 1.0's +0.0955 is
on D51's clipped basis, +0.0994 as evaluated). Read as the diversity
dividend (Obs 141) measured on a K ladder: K buys sampling diversity,
and pays in proportion to how much the configuration already generates.
TILE-MCC DOES NOT FOLLOW F1. Across the 15 verified ladders of findings
§§ 4 and 4.3 whose tile-MCC the restated tables report (the
gold-standard stride A ladder, the seven 55-map ladders, and seven of
the thirteen Gemini 3 Phase 2 ladders; the other six are on D51's
clipped basis, where tile-MCC is withheld, and tier E is tested
separately, § 8.4), F1 rises on all 15 and tile-MCC falls on 10, and as
evaluated it falls on all six withheld ladders too (16 of 21); NO ladder
shows a significant tile-MCC RISE from K = 1 to its best rung, and the
gold-standard ladder's +0.0130, § 4 of the findings' one apparent
counter-example, tests at BH p = 0.7633. Significant FALLS from K = 1 to
the best rung are found on four ladders — the 3.7-verifier stride B
(-0.0112), 3.7 arm 1 (-0.0099), 3.7 arm 2 (-0.0275) and HIGH image T 1.0
(-0.0637, BH p = 0.0420, the family with the largest F1 gain). Between
intermediate rungs, both 55-map stride A ladders fall significantly from
K = 3 to K = 5 (-0.0111, BH p = 0.0066) and rise significantly from K =
5 to K = 10 (+0.0047, BH p = 0.0300), so over every tested pair six
ladders show a significant fall and two a significant rise. More passes
buy localisation inside already-positive tiles, not tile-level
discrimination, which matters for any application whose unit is the tile
rather than the mound. CAVEAT on the MCC column: tile-MCC is computed by
a string join on source_tile, and three cells of the 3.7 gold-standard
text ladder are scored on a frame whose tile vocabulary is not their
proposer's, so their tile-MCC is WITHHELD with a named reason rather
than reported (g37-text-k1-verified-opmax,
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
deviation of ~0.0114 either way — so 487 tiles resolve a ΔF1 of about
0.03 and above and not below. The nine MINIMAL ladders sort by effect
size rather than by corpus (on the tests as evaluated, every one at or
above +0.0546 separates and every one at or below +0.0223 does not), and
the deployment range +0.0192..+0.0547 sits INSIDE the gold-standard
range +0.0139..+0.0600 (+0.0629 as evaluated). So 'K buys nothing
detectable' on four MINIMAL configurations is a statement about 487
tiles, not about K. PARETO MCC SET: on tile-MCC no rung above K = 1 is
ever the admissible choice — K = 1 holds the highest tile-MCC on 7 of
the 15 ladders above (13 of the 22 in the
multiple-comparisons-with-the-best (MCB) sets below, which are computed
on the cells as evaluated and so add tier E and the six withheld
ladders) and is never significantly beaten on it — so the MCC-efficient
rung is K = 1 wherever tile-level discrimination is the objective, while
the F1-efficient rung is K = 3. The two objectives select different
rungs, and that is the review's practical finding. A GEOMETRY EFFECT,
consensus-only: at fixed MINIMAL text T 0.7 the grid study's K = 1 -> 10
gain is about 2.2x larger at 12.5 % overlap than at 50 % (+0.1441
against +0.0660 at 384 px; +0.0947 against +0.0425 at 512 px), and
tile-MCC RISES with K on all four consensus-only cells (+0.029..+0.132)
— the opposite of the verified ladders, consistent with the same
mechanism. Overlap and pass count buy the same redundancy. The pattern
does not survive to the verified deployment ladders, which order the
other way. THE VERIFIER STAGE REVERSES tile-MCC's RESPONSE TO K, and
absorbs about half of K's F1 return: 48.7 % with tier E's rungs compared
on the area every rung searched (D51), and 60.3 % as evaluated (§ 8.6,
added on the PI's ruling 2026-09-13). On ONE pool and ONE geometry — the
grid study's 384 px / 50 % B-geometry MINIMAL text pool, which is the
deployment stride-B tiling at gold-standard scale — K = 1 -> 10 raises
F1@20 by +0.0660 with tile-MCC RISING +0.0444 consensus-only
(results/grid-2026-08-18/sweep.csv, cell g384_ov192, best F1@20 per K
over the corroboration x vote grid: 0.6633/0.4465 at K = 1,
0.7293/0.4909 at K = 10), and raises F1@20 by only +0.0338 with tile-MCC
FALLING -0.0238 once the same pool is verified. On the clipped basis
tier E's F1@20 is 0.8604 at K = 1
(reports/scorer-frames-d50-d51-2026-10-08-scripts/out/ladders_new.json)
and 0.8942 at K = 10, the restated rung of tier-e/ladder.json: that
rung's union lies wholly in the common area, so the clip removes nothing
from it, and the K = 10 row of ladders_new.json (0.8886) predates the
re-verification. As evaluated, K = 1 reads 0.8680 and the gain is
+0.0262. Tile-MCC exists only as evaluated: 0.8211 at K = 1 and 0.7973
at K = 10 (tier-e/ladder.json and each rung's evaluation). The two
stages share the common footprint but not the reference set: the
consensus-only side is scored against the 428 reference mounds inside
it, and tier E against the frame's 435, which D51 keeps, so each clipped
tier E rung is also scored against 7 mounds outside the area it was
clipped to. So the verifier takes 48.7 % of what extra passes buy on F1
(one minus the ratio of the verified to the consensus-only gain, on
unrounded values; 60.3 % as evaluated) — because it was already removing
much of what extra passes remove — and turns a tile-level GAIN into a
tile-level LOSS, a swing of 0.0682 MCC. This is the mechanism of the
TILE-MCC DOES NOT FOLLOW F1 finding above measured directly rather than
inferred: tile-MCC's response to K is a property of the PIPELINE STAGE,
not of K. Its limits are stated with it: one geometry, one thinking
level, one temperature, one modality, one corpus, and the ladder's own
DMCC steps are not individually significant (tile-MCC separates on none
of its six pairs), so the claim is about the sign and size of the shift
BETWEEN stages. NOT CLAIMED: no MCC RANKING of rungs, tiering stays on
the preregistered F1; and the MCC moves of the ladders whose K = 1 ->
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
of them (the 7 of the 15 above, five of the six withheld ladders, and
tier E), so the PARETO MCC SET claim above now rests on the canonical
simultaneous instrument rather than on a pairwise count. ON TILE-MCC'S
RESOLUTION: the MCC-admissible set is the WHOLE ladder on 13 of 22
against 2 of 22 on F1 — the same weak resolution the permutation arm
found — but where it resolves it resolves against K: six of the twenty
ladders with a K = 10 rung exclude it on tile-MCC, and on two (55-map
stride B under the 3.7 verifier, and 3.7 arm 2) the MCC-admissible set
is {K = 1} alone. ON RESOLUTION GENERALLY: the simultaneous F1 width
w_upper is 0.0159-0.0326 on the 487-tile gold standard and 0.0047-0.0056
on the 8,541-tile deployment corpus, three to six times narrower, which
is the tension analysis's resolution result in the MCB's own units.
INSTRUMENT DISAGREEMENT, FLAGGED: the admissible set and the committed
greedy-clique tie set differ in BOTH directions (F1 set smaller than the
tie set on two ladders, larger on six), exactly as erratum E83 and
defect D20 warn; of the four MINIMAL ladders that greedy-clique into a
SINGLE tier, only two are admissible whole, since MINIMAL text T 0.3 and
MINIMAL image T 1.0 both rule K = 1 out as best. The single-tier
statement stands as a within-ladder pairwise BH result and is not
withdrawn, but 'one tier' is not 'every rung could be the best one'.
WITHHELD: the 3.7 gold-standard text ladder has NO admissible set on
either metric, because the tile-join invariant refuses the per-tile
table of three cells on two of its four rungs (K = 1 and K = 3) on this
frame and the refusal falls on the F1 arm as well as the MCC arm,
leaving two sound rungs of four; its whole-frame F1 is unaffected and
reported in full. CARRIED CONVENTION (PI ruling 2026-09-13): the
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

## 2. Word diff against the current register outcome

Against `results/run-analyses.json` → `k-ladder-2026-09-12` → `outcome` as it stands on the branch (unchanged since signing). `[-removed-]{+added+}`, token level.

```text
The pass-count ladder K at otherwise fixed parameters, on 23 ladders:
the gold-standard stride A ladder (the only one whose every rung is an
exact re-verification of its own first-N union), the thirteen Gemini 3
pv-diag-384 families and the {+Gemini+} 3.7 gold-standard text
[-screen-] {+ladder+} that Phase 2 completed to four rungs for
US$24.8065, the grid 384 px / 50 % MINIMAL text ladder tier E completed
for US$4.9595, and the seven 55-map deployment ladders. {+Restated
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
gold-standard text ladder and six Gemini 3 ladders), and tier E's F1
gain below, are now compared on the area every rung searched (D51), a
basis on which no tile-MCC has been computed, so the seven ladders'
tile-MCC is withheld; figures on the earlier, unclipped basis are marked
'as evaluated'. No verdict moved; the verifier's share of K's F1 return
changes size, and the text now carries the re-pricing and corrections in
the two signature notes the PI approved on 2026-10-04 (the second under
D25), corrects two counts that were wrong from first publication (how
often K = 1 has the highest tile-MCC, and on how many ladders every rung
below K = 5 is ruled out as the best: ten, not nine), and limits the
tile-MCC rise and fall statements to the comparison they count, K = 1
against the best rung (as first written, 'no ladder shows a significant
tile-MCC rise' was untrue of both 55-map stride A ladders, which rise
significantly from K = 5 to K = 10).+} SHAPE: the return is FRONT-LOADED
and K = 3 is on the efficient set of every ladder in the corpus {+(a
rung is efficient when no cheaper rung of the same ladder scores as
well)+} — 37 % to 93 % of a ladder's total F1 gain for 31 % to [-64-]
{+62+} % of its top rung's cost — while the last step {+(K = 5 -> 10, or
K = 3 -> 5 on the two 55-map 3.7 arms, which have no K = 10 rung)+} is
the worst [-buy on every ladder, at US$1,100 to US$43,000-] {+buy, the
dearest+} per 0.001 F1 {+or a loss of F1, on 17 of the 23 ladders; on
the other six+} (the {+gold-standard stride A ladder, the two 55-map
stride B ladders under the Gemini 3 verifier, stride B under the+} 3.7
[-family's-] {+verifier, MINIMAL image T 0.3 and HIGH image T 1.0) the K
= 3 -> 5 step is worse. The 17 counts stride B under the 3.7 verifier
with its K = 5 rung, a 55-map board cell (findings § 3.3) that the MCB
sets below do not include; without that rung its last step, K = 3 -> 10,
is its dearest and the count is 18. Where the last step gains F1 it
costs about US$0.20 (gold-standard stride A) to US$27 (55-map 3.7 arm 1)
per 0.001 F1 gained; on five ladders it loses F1 (MINIMAL text T 0.3 and
T 0.7, HIGH text T 0.3, HIGH image T 0.7, and tier E); the 3.7
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
one apparent counter-example, tests at BH p = [-0.7678.-] {+0.7633.+}
Significant FALLS {+from K = 1 to the best rung+} are found on four
ladders — the 3.7-verifier stride B (-0.0112), 3.7 arm 1 (-0.0099), 3.7
arm 2 (-0.0275) and HIGH image T 1.0 (-0.0637, BH p = 0.0420, the family
with the largest F1 gain). {+Between intermediate rungs, both 55-map
stride A ladders fall significantly from K = 3 to K = 5 (-0.0111, BH p =
0.0066) and rise significantly from K = 5 to K = 10 (+0.0047, BH p =
0.0300), so over every tested pair six ladders show a significant fall
and two a significant rise.+} More passes buy localisation inside
already-positive tiles, not tile-level discrimination, which matters for
any application whose unit is the tile rather than the mound. CAVEAT on
the MCC column: tile-MCC is computed by a string join on source_tile,
and three cells of the 3.7 gold-standard text [-family-] {+ladder+} are
scored on a frame whose tile vocabulary is not their proposer's, so
their tile-MCC is WITHHELD with a named reason rather than reported
(g37-text-k1-verified-opmax, g37-text-k1-verified-carried-p0.10-k1,
g37-text-k3-verified-opmax; {+the regenerated tables no longer record
a+} raw [-0.1337 / 0.1422 / 0.1337).-] {+value).+} The corpus-wide
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
deviation of ~0.0114 either way — so 487 tiles resolve a ΔF1 of about
0.03 and above and not below. The nine MINIMAL ladders sort by effect
size rather than by corpus [-(every-] {+(on the tests as evaluated,
every+} one at or above +0.0546 [-separates,-] {+separates and+} every
one at or below +0.0223 does not), and the deployment range
+0.0192..+0.0547 sits INSIDE the gold-standard range
[-+0.0139..+0.0629.-] {++0.0139..+0.0600 (+0.0629 as evaluated).+} So 'K
buys nothing detectable' on four MINIMAL configurations is a statement
about 487 tiles, not about K. PARETO MCC SET: on tile-MCC no rung above
K = 1 is ever the admissible choice — K = 1 holds the highest tile-MCC
on [-13-] {+7+} of the [-21 interpretable-] {+15+} ladders {+above (13
of the 22 in the multiple-comparisons-with-the-best (MCB) sets below,
which are computed on the cells as evaluated and so add tier E and the
six withheld ladders)+} and is never significantly beaten on it — so the
MCC-efficient rung is K = 1 wherever tile-level discrimination is the
objective, while the F1-efficient rung is K = 3. The two objectives
select different rungs, and that is the review's practical finding. A
GEOMETRY EFFECT, consensus-only: at fixed MINIMAL text T 0.7 the grid
study's K = 1 -> 10 gain is about [-2.4x-] {+2.2x+} larger at 12.5 %
overlap than at 50 % [-(+0.1454-] {+(+0.1441+} against [-+0.0572-]
{++0.0660+} at 384 px; [-+0.0914-] {++0.0947+} against [-+0.0396-]
{++0.0425+} at 512 px), and tile-MCC RISES with K on all four
consensus-only cells [-(+0.038..+0.154)-] {+(+0.029..+0.132)+} — the
opposite of the verified ladders, consistent with the same mechanism.
Overlap and pass count buy the same redundancy. The pattern does not
survive to the verified deployment ladders, which order the other way.
THE VERIFIER STAGE REVERSES tile-MCC's RESPONSE TO K, and absorbs about
[-40 %-] {+half+} of K's F1 [-return-] {+return: 48.7 % with tier E's
rungs compared on the area every rung searched (D51), and 60.3 % as
evaluated+} (§ 8.6, added on the PI's ruling 2026-09-13). On ONE pool
and ONE geometry — the grid study's 384 px / 50 % B-geometry MINIMAL
text pool, which is the deployment stride-B tiling at gold-standard
scale — K = 1 -> 10 raises F1@20 by [-+0.0572-] {++0.0660+} with
tile-MCC RISING +0.0444 consensus-only
(results/grid-2026-08-18/sweep.csv, cell g384_ov192, best F1@20 per K
over the corroboration x vote grid: 0.6633/0.4465 at K = 1,
[-0.7205/0.4909-] {+0.7293/0.4909+} at K = 10), and raises F1@20 by only
[-+0.0340-] {++0.0338+} with tile-MCC FALLING [--0.0308-] {+-0.0238+}
once the same pool is [-verified-] {+verified. On the clipped basis tier
E's F1@20 is 0.8604 at K = 1
(reports/scorer-frames-d50-d51-2026-10-08-scripts/out/ladders_new.json)
and 0.8942 at K = 10, the restated rung of tier-e/ladder.json: that
rung's union lies wholly in the common area, so the clip removes nothing
from it, and the K = 10 row of ladders_new.json (0.8886) predates the
re-verification. As evaluated, K = 1 reads 0.8680 and the gain is
+0.0262. Tile-MCC exists only as evaluated: 0.8211 at K = 1 and 0.7973
at K = 10+} (tier-e/ladder.json and each rung's [-evaluation:
0.8546/0.8211 at K = 1, 0.8886/0.7903 at K = 10).-] {+evaluation). The
two stages share the common footprint but not the reference set: the
consensus-only side is scored against the 428 reference mounds inside
it, and tier E against the frame's 435, which D51 keeps, so each clipped
tier E rung is also scored against 7 mounds outside the area it was
clipped to.+} So the verifier takes [-40.6-] {+48.7+} % of what extra
passes buy on F1 {+(one minus the ratio of the verified to the
consensus-only gain, on unrounded values; 60.3 % as evaluated)+} —
because it was already removing much of what extra passes remove — and
turns a tile-level GAIN into a tile-level LOSS, a swing of [-0.0752-]
{+0.0682+} MCC. This is the mechanism of the TILE-MCC DOES NOT FOLLOW F1
finding above measured directly rather than inferred: tile-MCC's
response to K is a property of the PIPELINE STAGE, not of K. Its limits
are stated with it: one geometry, one thinking level, one temperature,
one modality, one corpus, and the ladder's own DMCC steps are not
individually significant (tile-MCC separates on none of its six pairs),
so the claim is about the sign and size of the shift BETWEEN stages. NOT
CLAIMED: no MCC RANKING of rungs, tiering stays on the preregistered F1;
and the [-five non-separating ladders'-] MCC moves {+of the ladders
whose K = 1 -> best-rung change does not separate (11 of the 15; 17 of
21 as evaluated)+} are not shown to be zero. HSU MCB ADMISSIBLE SETS
[-(PI-] {+(the rungs that cannot be ruled out as their ladder's best;
PI+} ruling 2026-09-13, 'wait for the sets'): the review's last
outstanding run-card requirement is supplied for all 22 tiered ladders,
on F1 at each ladder's own headline buffer and on tile-MCC, with the
Era-2 board's own MCB step verbatim
(scripts/selection_aware_intervals.py --board; Hsu's constrained
one-sided form on theta_i = stat_i - max_{j != i} stat_j, critical value
bootstrapped over 10,000 tile resamples, seed 42, m-out-of-n 1.0,
simultaneous 95 %), each ladder on its own frame and reference, driven
by scripts/k_ladder_mcb.py and gated on all 44 runs against the
committed tiering ranking (170 candidate rows, max abs delta 4.958e-05,
results/k-ladder-2026-09-12/mcb/summary.json). {+The sets are computed
on the cells as evaluated, so every MCB count below includes tier E and
the six Gemini 3 ladders whose tile-MCC the clipped basis withholds
above; that basis has no per-tile table to compute them on.+} ON THE
SHAPE FINDING: K = 3 is admissible on 12 of the 22 ladders and is the
CHEAPEST admissible rung on 10 of them, so the front-loaded Pareto
reading is endorsed by the simultaneous instrument on roughly half the
corpus and declined on the other half — on [-nine-] {+ten+} ladders
nothing below K = 5 is admissible {+(on nine the cheapest admissible
rung is K = 5; on 55-map stride B under the 3.7 verifier only K = 10
is)+} even though K = 3 remains the efficient buy, which makes 'K = 3 is
on the efficient set' a cost claim rather than a statistical one. ON THE
LAST STEP: NO ladder's F1-admissible set excludes K = 10 — all twenty
ladders that have a K = 10 rung admit it — so the top rung is never
statistically ruled out, [-only never-] {+and whether it is+} worth its
[-price, which-] {+price+} is the [-formal counterpart-] {+cost question
SHAPE above answers: the last step is the worst buy on 17+} of the
[-US$1,100-to-US$43,000 per 0.001 F1 figures above.-] {+23 ladders, not
on all.+} ON THE TWO OBJECTIVES: K = 1 is ruled out on F1 on 20 of 22
ladders and is admissible on tile-MCC on 22 of 22, holding the highest
tile-MCC on 13 of [-them,-] {+them (the 7 of the 15 above, five of the
six withheld ladders, and tier E),+} so the PARETO MCC SET claim above
now rests on the canonical simultaneous instrument rather than on a
pairwise count. ON TILE-MCC'S RESOLUTION: the MCC-admissible set is the
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

The "Issue" column uses the coordinator's v2 points as C1 to C8, the verifier's v1 report
issues as V1 to V9, and the original brief's items as 1 to 9. "conv." is the walk-through
convention. Paths are under `results/k-ladder-2026-09-12/` unless they start with `results/`,
`reports/` or `planning/`. "P1" is `ladders.json` and "P2" is `phase2/ladders.json`.

| # | Change (register → redraft) | Issue | Source and value |
|---|---|---|---|
| 1 | "the 3.7 gold-standard text screen" → "the Gemini 3.7 gold-standard text ladder", the one name used throughout (seven uses; CAVEAT's "text family" and WITHHELD's "text screen" changed too) | C8, V9 | wording only |
| 2 | Dated clause added after the ladder list | conv., C2, C8, V7 | Causes: `reports/s164-agent-records/rescore-repaired-gs.md` § 3.2 (COMMITTED → ORIGIN → REPAIRED: GS stride A and tier E K = 10 move only at REPAIRED, the re-verification; consensus-only +0.0572 → +0.0660 at ORIGIN, the origin route; tier E K = 1/3/5 at ORIGIN through S9, the D50 scorer; the 3.7 K = 5 → 10 step at REPAIRED). `restatement-pass.md` § 1.4 (the seven clipped ladders, D57 (2) and (3) for the six, D67 (5) for the 3.7) and § 2.3. D50's text in `planning/pi-decisions-2026-09-20.md` for the gloss ("scopes detections per sheet … with origin-sheet attribution") |
| 3 | SHAPE: "31 % to 64 %" → "31 % to 62 %" | 3 | Minimum P2 `summary[HIGH image T 1.0].cost_share_at_k3` 0.3149; maximum P1 3.7 arm 2 `cost.usd` 99.0293 / 158.5795 = 0.6245 |
| 3a | SHAPE: "worst buy on every ladder" → "on 17 of the 23", six exceptions named, and the meaning of "last step" on the 3.7 arms | 3 | Recount, § 4.1 |
| 3b | SHAPE: the fourth cell's K = 5 board rung disclosed; 18 without it | C8, V9 | `results/55map-final-board-r2-2026-09-06/cells/FOURTH-N5-oracle/evaluation.json` F1@50 0.8758; cost US$116.15 (findings § 3.3; `reports/wp4b-frontier-repricing-2026-10-04.md` line 54); without it, K = 3 → 10 is +0.0066 for US$116.76, US$17.69 per 0.001 F1, the ladder's dearest (§ 4.8) |
| 3c | SHAPE: "US$1,100 to US$43,000" → "about US$0.20 (gold-standard stride A) to US$27 (55-map 3.7 arm 1) per 0.001 F1 gained" | 3 | P1 GS stride A K5 0.8937 / 3.8056 → K10 0.9075 / 6.5445: US$0.198; P1 3.7 arm 1 K3 0.8705 / 94.3107 → K5 oracle 0.8727 / 153.1642: US$26.75 |
| 3d | SHAPE: five ladders lose F1 at the last step | 3 | P2 `opmax.f1_20` K5 → K10: 0.8778 → 0.873, 0.8739 → 0.8726, 0.8873 → 0.8722, 0.7868 → 0.7765; `tier-e/ladder.json` 0.9046 → 0.8942 |
| 3e | SHAPE: "+0.0002 … US$8.65" → "+0.0004 F1@20 for US$8.68"; "about US$22" dropped | C8, V9 | P2 3.7 ladder K5 0.9165 → K10 0.9169; `all_in_flex_usd` 9.1454 → 17.8281 |
| 3f | Gloss of "efficient set" | conv. | `findings.md` § 5, line 668 |
| 4 | "(both tested on the cells as evaluated)" now covers the significance counts and the single-tier result | C7, V8c | `phase2/mcc-test/summary.json` (`326181bcd`, before the clip); single tiers from the committed tiering (`mcb/summary.json` `committed_tiering`) |
| 5 | "+0.0994" → "+0.0955 … on D51's clipped basis, +0.0994 as evaluated" | 4 | P2 `summary[HIGH text T 1.0].gain` 0.0955, `historical_as_evaluated.gain` 0.0994 |
| 6 | "21 … 21 … 16" → "15 … 15 … 10", the 15 defined as findings §§ 4 and 4.3's ladders with a reported tile-MCC, tier E named as tested separately, and "16 of 21" as evaluated; "RISE" and "FALLS" both limited to K = 1 against the best rung | 2, 4, C2, C6, V2, V6 | P2 `summary[*].mcc_verdict` (7 not withheld: 5 down, 1 up, 1 flat); `mcc-test/summary.json` `mcc_direction_k1_to_best` negative on 5 of 8; the six withheld ladders as evaluated all down (P2 `historical_as_evaluated.tile_mcc`) |
| 7 | New sentence: the 55-map stride A ladders' intermediate MCC steps, with six ladders falling and two rising over every tested pair | C2, V2 | `mcc-test/55map-stride-a-r2.json` and `…-standardised.json`: K3-vs-K5 `mcc.delta` −0.011052 / −0.011053, `p_bh` 0.0066; K5-vs-K10 +0.004676 / +0.004684, `p_bh` 0.03. Every pair in `mcc-test/*.json` and `phase2/mcc-test/*.json` (four per ladder; three on the two arms and the fourth cell) and tier E's six (`tier-e/ladder.json` `n_significant_mcc` 0): significant falls on 3.7 arm 1, 3.7 arm 2, the fourth cell, HIGH image T 1.0 and both stride A ladders; significant rises on both stride A ladders only (§ 4.9) |
| 8 | "+0.0135 … 0.7678" → "+0.0130 … 0.7633" | 6 | `mcc-test/gs-stride-a.json` `pairs[0].mcc.delta` 0.013043, `p_bh` 0.76332 |
| 9 | "raw 0.1337 / 0.1422 / 0.1337" → "the regenerated tables no longer record a raw value" | 7 | `phase2/scores.json` rows 27 and 28, `tile_mcc` null |
| 10 | "+0.0546 separates" marked as the tests as evaluated | C7, V8c | `phase2/mcc-test/summary.json` `f1_p_bh_k1_to_best` (MINIMAL image T 0.7 tested at +0.0629) |
| 11 | "+0.0139..+0.0629" → "+0.0139..+0.0600 (+0.0629 as evaluated)" | 4 | `tension/effect-sizes.json` `rows[4].delta_f1` 0.06 (`62050794d`); P2 `historical_as_evaluated.gain` 0.0629 |
| 12 | "13 of the 21 interpretable" → "7 of the 15 … (13 of the 22 in the MCB sets …)" | 2, 4 | § 4.4 |
| 13 | Geometry: 2.4x → 2.2x; the four gains; +0.038..+0.154 → +0.029..+0.132 | carried | `tension/grid-overlap.json` `cells[*].delta_f1_k1_to_k10` 0.144102, 0.065954, 0.094703, 0.042509; `delta_mcc_k1_to_best` 0.029126 to 0.13208 |
| 14 | Headline: "about 40 %" → "about half: 48.7 % … (D51), and 60.3 % as evaluated" | 5, C8, V9 | § 4.7 |
| 15 | § 8.6 detail: the parenthesis split into sentences; the clipped inputs anchored and the stale K = 10 row named; the reference sets stated; the derivation of 48.7 % stated | C4, C5, C8, V4, V5, V9 | `reports/scorer-frames-d50-d51-2026-10-08-scripts/out/ladders_new.json` `tier_e.rungs[0].points.opmax.d51_clipped.f1` 0.86036, `assessed_area.clip.area_removed_km2["K = 10"]` 0.0, the K = 10 row 0.888623; `tier-e/ladder.json` `rungs[0]` 0.868 / 0.8211, `rungs[3]` 0.8942 / 0.7973; `results/grid-2026-08-18/grid_analysis.json` `scope.footprint_audit.common_ground_truth` 428 and `era2_487.ground_truth` 435; consensus gain 0.065954, MCC +0.044361; swing 0.044361 + 0.023837 = 0.068198 |
| 16 | NOT CLAIMED: "the five non-separating ladders" → the ladders whose K = 1 → best change does not separate, "(11 of the 15; 17 of 21 as evaluated)" | C7, V8b | Of the 15, four separate (row 6); of the 21 as evaluated, the same four (the six withheld: `phase2/mcc-test/summary.json` `mcc_p_bh_k1_to_best` 0.6044, 0.576, 0.8065, 0.9954, 0.9768, 0.6072) |
| 17 | MCB gloss at the heading; MCB defined at first use (PARETO) | conv. | — |
| 18 | MCB basis sentence | 4 | `mcb/summary.json`; findings § 6.1 "Restated 2026-10-15" |
| 19 | "nine ladders" → "ten ladders (nine … K = 5; … only K = 10 …)" | 9 | § 4.5 |
| 20 | ON THE LAST STEP: "only never worth its price, which is the formal counterpart of the US$1,100-to-US$43,000 …" → "whether it is worth its price is the cost question SHAPE above answers: the last step is the worst buy on 17 of the 23 ladders, not on all" | 1, C1, V1 | § 4.1 |
| 21 | "13 of them" → "13 of them (the 7 of the 15 above, five of the six withheld ladders, and tier E)" | 4 | § 4.4 |
| 22 | 12 → 13 of 22; seven → six; 0.0151 → 0.0159 | carried | `mcb/summary.json` `roll_up` (13); six ladders with 10 in their rungs and not in `mcc.hsu_admissible_K`; `f1.hsu_w_upper` minimum 0.015867 |
| 23 | WITHHELD: "three of its four rungs" → "three cells on two of its four rungs (K = 1 and K = 3)" | C7, V8a | `mcb/summary.json` `withheld`: `n_rungs` 4, `n_rungs_withheld` 2, three `cells_withheld` |

All unchanged figures were re-read in version 1, and the verifier reproduced them
independently (its § 1, rows 1 to 59). Version 2 adds no unchanged figure.

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
§ 3, row 3d). This is the same on either basis. Tier E's last step lost F1 before the
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
parenthesis; § 7 drafts the matching edits to findings § 6.1 and the MCB deltas report. `findings.md` § 6.1 item 1 has a second instance in the same sentence: "on nine
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

## 5. Decisions for the PI

**A. Which tier E reading leads in § 8.6.** D51's recorded text extends the clip to tier E, so
the draft leads with it: "about half … 48.7 % … (D51), and 60.3 % as evaluated".

- *Option 1 (the draft): clipped leads, with the as-evaluated reading beside it.* This follows
  D51 as recorded, and D67 (5)'s form for the 3.7 ladder.
- *Option 2: as evaluated leads, with the clipped reading beside it.* This is the restatement
  pass's choice, and how findings §§ 8.4 and 8.6 read today. The exact swap-in text, checked
  to apply (`kl2/build2_opt2.py`; full text in `kl2/opt2/redraft-opt2.txt`), makes three
  changes:
  1. In the dated clause, ", and tier E's F1 gain below," is removed.
  2. The headline becomes "and absorbs about 60 % of K's F1 return: 60.3 % as evaluated, and
     48.7 % with tier E's rungs compared on the area every rung searched, D51's basis (§ 8.6,
     added on the PI's ruling 2026-09-13)."
  3. The verified detail becomes "and raises F1@20 by only +0.0262 with tile-MCC FALLING
     -0.0238 once the same pool is verified (0.8680/0.8211 at K = 1 and 0.8942/0.7973 at
     K = 10, as evaluated; tier-e/ladder.json and each rung's evaluation). On the clipped
     basis K = 1 reads 0.8604 (reports/scorer-frames-d50-d51-2026-10-08-scripts/out/ladders_new.json)
     and K = 10 the same 0.8942, because that rung's union lies wholly in the common area and
     the clip removes nothing from it (the K = 10 row of ladders_new.json, 0.8886, predates
     the re-verification), so the clipped gain is +0.0338; tile-MCC exists only as evaluated.
     The two stages share the common footprint only on the clipped basis, and never the
     reference set: the consensus-only side is scored against the 428 reference mounds inside
     the footprint, and tier E against the frame's 435, with its K = 1, 3 and 5 rungs also
     searching a 37.94 km² band outside the footprint. So the verifier takes 60.3 % of what
     extra passes buy on F1 (one minus the ratio of the verified to the consensus-only gain,
     on unrounded values; 48.7 % on the clipped basis) —"

  § 7 carries both options' companion edits.
- *Recommendation: Option 1, on D51's text.* D51 as recorded names tier E. Unclipped, K = 1
  keeps credit for 6 band matches that K = 10 cannot earn (§ 4.6), so the as-evaluated share
  overstates what the verifier absorbs. The recommendation does not rest on the comparison
  being like for like. It is not: the reference sets differ (428 against 435), and the
  outcome says so. Because the PI's quoted words for D51 do not name tier E, his confirmation
  is the ruling that settles it.

**B. 48.7 % or 48.8 %.** *Option 1 (the draft):* 48.7 %, from unrounded values, the same
convention as +0.0130. *Option 2:* 48.8 %, which matches today's findings § 8.6 and is computed
from rounded gains. *Recommendation:* 48.7 %, which reproduces on either K = 10 value. § 7's
edits assume it.

**C. Tier E's tile-MCC on the clipped basis, the six withheld ladders in the MCB counts, and an
anchor for 48.7 %.** The Phase 2 builder withholds tile-MCC on every clipped ladder, including
six Gemini 3 ladders whose clips are about 2 km² (P2 `assessed_area.max_excess_km2` 2.0819 for
MINIMAL text T 0.3). Tier E's clip is 37.94 km², yet § 8.6 uses its as-evaluated tile-MCC. The
clip removes 29 of 482 K = 1 detections, and its effect on tile-MCC has not been measured. The
MCB counts likewise keep the six withheld ladders on their as-evaluated cells. Separately, no
committed artefact holds tier E's clipped K = 10 value (§ 4.7).

- *Option 1 (the draft):* report both on the as-evaluated cells, and say so.
- *Option 2:* withhold tier E's tile-MCC, as the builder does for the seven.
- *Option 3:* build and commit clipped readings: tier E's whole clipped ladder, with per-tile
  tables for it and the six, and re-run the MCB and tile-MCC tests. This is a re-score with no
  API spend (`restatement-pass.md` § 10 item 4).
- *Recommendation: Option 1 now, with Option 3 queued, and the clipped tier E F1 ladder
  committed before re-signing if possible.* **Committing a clipped tier E reading would give
  the 48.7 % a committed anchor.** Today its K = 10 input is inferred from a 0 km² clip, and
  the only committed clipped file has a stale K = 10 row that gives 57.1 %.

**D. "Nine" → "ten".** The draft says ten and keeps the nine / one partition in a parenthesis.
Keeping nine would leave the sentence's halves (12 and 9) short of the 22. *Recommendation:*
ten, with the matching companion edits in § 7 (findings § 6.1 lines 844 and 848, and the MCB
deltas report line 96).

**E. The K = 1 → best-rung qualifiers on both tile-MCC sentences, and the new
intermediate-steps sentence.** Without the qualifier, the rise sentence is false of both
55-map stride A ladders, and the falls sentence undercounts (six ladders across every pair,
§ 4.9). *Recommendation:* approve both qualifiers and the one-sentence disclosure. Each states
only what findings § 4.1 already records.

**F. Fixes to unchanged signed sentences.** Four are in scope:

- WITHHELD: "three of its four rungs" becomes three cells on two rungs, per
  `mcb/summary.json` `withheld`.
- NOT CLAIMED: "the five non-separating ladders" becomes 11 of the 15 (17 of 21 as
  evaluated). Five is findings § 4.1's eight-ladder frame.
- The as-evaluated marks on the single-tier and separation results.
- One name for the 3.7 ladder.

*Recommendation:* approve all four, which correct internal errors rather than results.

**G. Length.** The dated clause is now two long sentences, because it discloses four
causes, two count corrections and the qualifiers. *Recommendation:* keep it. The walk-through
favours disclosure over brevity, and a shorter clause would drop which cause moved what.

**H. Merge condition.** Findings §§ 6.1, 8.4 and 8.6 and the MCB deltas report must change in
the same PR as the register text (§ 7), whichever options the PI takes. Otherwise the
outcome's "§ 8.6" citation points at text that contradicts it. *Recommendation:* treat § 7 as
a merge blocker.

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
13. The companion edits to findings §§ 6.1, 8.4 and 8.6 and to the MCB deltas report landed
    with the re-signing (§ 7; cite their commit).
14. Branch commit hashes in the note (`64382beea`, `f53f6e97c`, `0fc2d6389`, `f6f10d605`,
    `376eb1d50`, and `62050794d` and `de998a94d` above) will not resolve from `main` if PR #52
    is squash-merged. Cite the merge commit or the record's paths.

## 7. Companion document edits

These keep the documents the outcome cites consistent with it, so the register text and
its sources land together in one PR (§ 5, decision H). Each edit is an exact old → new
replacement, applied in the order listed. Every one was checked against a scratch copy
of the committed file (`git show HEAD:<path>` at `e3a0d490c`): each `old` occurs exactly
once, both options apply cleanly in full, and the edited copies pass `markdownlint-cli2`
with the repository's `.markdownlint.json`. The script and the edited copies are in
`kl2/companion.py` and `kl2/comp/option-{1,2}/`.

**Placeholders the applying session must fill**: `DXX`, the number of the PI's ruling on
this re-signing; `<landing-commit>`, the commit that lands the edits; and the date
2026-10-18, if the edits land on a later day. Both documents are in the Document Revision
Policy's scope (`results/**.md`, `reports/**.md`; `docs/methodology/output-directory-standard.md`
§ "Documents in Revision Policy Scope"). Each already has a banner and a changelog, so each
gets a new banner lead and a new changelog entry, and no "Original publication" stub is
needed. Past changelog entries are not rewritten: for example, the 2026-10-15 entry's
"48.8 %" stays as the record of that date.

Decision B is assumed to take Option 1 (48.7 %). If the PI keeps 48.8 %, replace
"48.7 %" with "48.8 %" in every edit below, and the unrounded formula with
"1 − 0.0338 / 0.0660".

### 7.1 `results/k-ladder-2026-09-12/findings.md`

Not edited: the +0.0131 at lines 104, 382 and 522. Line 382's table prints it
beside its rounded endpoints (0.7948 → 0.8079), and lines 104 and 522 refer back to
that table, so it follows the endpoint convention. The register uses +0.0130 because
it quotes no endpoints.

**F-banner** (Option 1 (clipped leads; recommended))

Old:

```text
> **Last revised**: 2026-10-15 (S164 restatement pass, PI ruling D65 (2):
```

New:

```text
> **Last revised**: 2026-10-18 (re-signing of the register row
> `k-ladder-2026-09-12`, PI ruling DXX: §§ 8.4 and 8.6 now lead with tier E
> on PI ruling D51's clipped basis, so the verifier absorbs about half of K's
> F1 return, 48.7 %, with 60.3 % as evaluated beside it, and § 8.6 states that
> the two stages are scored against different reference sets (428 and 435
> mounds); § 6.1 corrected to ten ladders, not nine, on which a K = 3 rung can
> be ruled out as best, with its 'never worth its price' and withheld-rung
> wording corrected). Prior: 2026-10-15 (S164 restatement pass, PI ruling D65 (2):
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
> §§ 8.4 and 8.6, with D51's clipped share corrected to 48.7 % beside it and the
> two stages' different reference sets (428 and 435 mounds) stated; § 6.1
> corrected to ten ladders, not nine, on which a K = 3 rung can be ruled out as
> best, with its 'never worth its price' and withheld-rung wording corrected).
> Prior: 2026-10-15 (S164 restatement pass, PI ruling D65 (2):
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
2. **The verifier absorbs about half of K's F1 return and reverses tile-MCC's
   response to it.** § 8.3's consensus-only ladder on this same pool and
   geometry gains **+0.0660** F1 from K = 1 to K = 10 with tile-MCC **rising**
   +0.0444; verified, the same pool gains **+0.0338** on D51's clipped basis
   (+0.0262 as evaluated) with tile-MCC **falling** −0.0238 (as evaluated). So
   the verifier takes about half of what extra passes buy on F1 (48.7 %; about
   three-fifths, 60.3 %, as evaluated) — because it was already removing much
   of what extra passes remove — and turns a tile-level *gain* into a
   tile-level *loss*, a swing of 0.068 MCC. Before the 2026-10-15 restatement
   this read about 40 % (+0.0340 against +0.0572) with a swing of 0.075
   (§ 8.6).
```

**F-8.4-item2** (Option 2 (as evaluated leads))

Old:

```text
   against +0.0572) with a swing of 0.075; on D51's clipped basis the share is
   about 49 % (§ 8.6).
```

New:

```text
   against +0.0572) with a swing of 0.075; on D51's clipped basis the share is
   48.7 % (§ 8.6).
```

**F-8.6-heading** (Option 1 (clipped leads; recommended))

Old:

```text
### 8.6 CLAIM — the verifier absorbs about 60 % of K's F1 return and reverses the sign of its tile-MCC effect
```

New:

```text
### 8.6 CLAIM — the verifier absorbs about half of K's F1 return and reverses the sign of its tile-MCC effect
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

The verifier therefore **absorbs 48.7 % of K's F1 return** on D51's clipped
basis (1 − 0.033840 / 0.065954, on unrounded values; 60.3 % as evaluated,
1 − 0.026191 / 0.065954) and **reverses the sign of K's tile-MCC effect**, a
swing of **0.0682** MCC. Tile-MCC exists only as evaluated, so the swing is
the same on both readings.
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
+0.0338 (0.8604 → 0.8942) and the share **48.7 %** (§ 8.4 gives the anchors
and why the clipped K = 10 value is the restated rung's). The tile-MCC
figures are the unclipped cells' on either reading (no clipped tile-MCC
exists), so the sign reversal is the same on both.

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
(0.8604 → 0.8942) and the share **48.7 %** (1 − 0.033840 / 0.065954, on
unrounded values); the reading above is the unclipped one, which the PI ruled
(DXX) that tier E reports (§ 8.4). The tile-MCC figures are the unclipped
cells' on either reading (no clipped tile-MCC exists), so the sign reversal
is the same on both.

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
  read with it, the share would be 57.1 %.
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

### 2026-10-18 — Re-signing: tier E on D51's clipped basis, and four corrections

**Trigger**: the PI's re-signing of the register row `k-ladder-2026-09-12`
after the S164 restatement (PI ruling DXX). Its redrafted outcome leads with
tier E on PI ruling D51's clipped basis and corrects statements that were
wrong from first publication; this document is brought into line. Landed in
`<landing-commit>`.

| Claim | Before | After |
|---|---|---|
| § 8.6 heading; the share the verifier absorbs, leading reading | about 60 %; 60.3 % (unclipped) | about half; 48.7 % (D51's clipped basis), with 60.3 % as evaluated beside it |
| § 8.6 clipped share | 48.8 % (1 − 0.0338 / 0.0660, on rounded gains) | 48.7 % (1 − 0.033840 / 0.065954) |
| § 8.4 item 2, verified gain | +0.0262 (about 60 %) | +0.0338 clipped, +0.0262 as evaluated (about half) |
| § 6.1 item 1, ladders on which a K = 3 rung can be ruled out as best | nine | ten (nine whose cheapest admissible rung is K = 5, one with only K = 10) |
| § 6.1, the withheld family's refused rungs | three of its four rungs | three cells on two rungs (K = 1 and K = 3) |

**Also**: § 6.1 item 2's "it is only never *worth* its price" is replaced,
because the last step is not the worst buy on six of the 23 ladders (the row's
signature note of 2026-10-04, ruling D25). §§ 8.4 and 8.6 now state that the
consensus-only side is scored against 428 reference mounds and tier E against
435, anchor the clipped K = 1 value, and say why the clipped K = 10 value is
the restated rung's.

**What did NOT change**: every F1, tile-MCC, cost, tier, admissible set and
test; the sign reversal and the 0.0682 swing; § 8.4's table, which stays on
the unclipped readings. No artefact was regenerated.

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

### 2026-10-18 — Re-signing: tier E stays unclipped, and four corrections

**Trigger**: the PI's re-signing of the register row `k-ladder-2026-09-12`
after the S164 restatement (PI ruling DXX, which keeps tier E on the
unclipped reading with D51's clipped reading beside it). The redrafted
outcome corrects statements that were wrong from first publication; this
document is brought into line. Landed in `<landing-commit>`.

| Claim | Before | After |
|---|---|---|
| § 8.6 and § 8.4 item 2, clipped share | 48.8 % (1 − 0.0338 / 0.0660, on rounded gains); about 49 % | 48.7 % (1 − 0.033840 / 0.065954) |
| § 6.1 item 1, ladders on which a K = 3 rung can be ruled out as best | nine | ten (nine whose cheapest admissible rung is K = 5, one with only K = 10) |
| § 6.1, the withheld family's refused rungs | three of its four rungs | three cells on two rungs (K = 1 and K = 3) |

**Also**: § 6.1 item 2's "it is only never *worth* its price" is replaced,
because the last step is not the worst buy on six of the 23 ladders (the row's
signature note of 2026-10-04, ruling D25). §§ 8.4 and 8.6 record the PI's
choice, state that the consensus-only side is scored against 428 reference
mounds and tier E against 435, and anchor the clipped readings.

**What did NOT change**: every F1, tile-MCC, cost, tier, admissible set and
test; § 8.6's leading 60.3 %, the sign reversal and the 0.0682 swing. No
artefact was regenerated.

### 2026-10-15 — S164 restatement pass:
```

### 7.2 `reports/k-ladder-mcb-deltas-2026-09-13.md`

The restatement pass left this report as a dated record (`restatement-pass.md` § 9):
its claims table quotes the MCB as of 2026-09-13. The edits therefore correct only
statements that were wrong on the report's own date, and leave the table's three rows
that the restatement moved (12 → 13 of 22, 7 → 6, 0.0151 → 0.0159) as dated values.

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

## 8. Change log against version 1

| Issue (coordinator C; verifier V) | Fix in version 2 |
|---|---|
| C1 = V1, MUST FIX: "only never worth its price" contradicts SHAPE | ON THE LAST STEP rewritten: "whether it is worth its price is the cost question SHAPE above answers: the last step is the worst buy on 17 of the 23 ladders, not on all" (§ 3 row 20). The same phrase is corrected in findings § 6.1 item 2 and the MCB deltas report (b) (§ 7) |
| C2 = V2, V7: falls sentence unqualified; qualifiers not disclosed | "Significant FALLS from K = 1 to the best rung". A new sentence gives the stride A ladders' intermediate steps (−0.0111 at K = 3 → 5, +0.0047 at K = 5 → 10) and the all-pairs counts, six falls and two rises (§ 3 rows 6–7, § 4.9). The dated clause discloses that both statements are limited to K = 1 against the best rung, and that the unqualified rise statement was untrue as worded at signing |
| C3 = V3, MERGE BLOCKER: cited documents disagree with the outcome | § 7: 21 exact, validated replacements across findings §§ 6.1, 8.4 and 8.6 (heading, claim table, restated paragraph, anchors) and the MCB deltas report (line 96, (b), § 5). Each document gets a banner lead and a changelog entry. Option 1 and Option 2 variants are given, both checked to apply and lint-clean. Decision H makes it a merge condition |
| C4 = V4: like-for-like argument overstated; mechanism misstated | § 4.6 rewritten: the clip equalises by removing K = 1, 3 and 5's band credit (K = 1: 388 → 382 matched references), not by relieving K = 10. The consensus side is scored against 428 references, tier E against 435, so neither tier E reading is exactly its basis. The outcome's § 8.6 part says so (§ 3 row 15), as do the findings edits. Decision A's recommendation now rests on D51's text |
| C5 = V5: 48.7 % anchor; stale K = 10 row | The outcome names `ladders_new.json`'s K = 10 row (0.8886) as predating the re-verification, says why the clipped K = 10 value is the restated 0.8942, and states how 48.7 % is computed (§ 3 row 15, § 4.7: following the stale row gives 57.1 %). Decision C says plainly that a committed clipped tier E reading would anchor it |
| C6 = V6: "the 15" also fits tier E | "the 15 verified ladders of findings §§ 4 and 4.3 whose tile-MCC the restated tables report (…; tier E is tested separately, § 8.4)" (§ 3 row 6) |
| C7 = V8a–c: errors in unchanged sentences | WITHHELD: three cells on two rungs (row 23). NOT CLAIMED: 11 of the 15, 17 of 21 as evaluated (row 16). The single-tier and separation results are marked as evaluated (rows 4 and 10). Decision F covers all of these |
| C8 = V9: readability | "the basis D51's text extends to tier E" → "(D51)" (row 14). The § 8.6 parenthesis is split into four sentences (row 15). "Sheet-scoped scorer" glossed as "the scorer now scores each detection on the map sheet it was found on (D50)". The MCB-language count in the dated clause is reworded in plain words ("on how many ladders every rung below K = 5 is ruled out as the best"). One name for the 3.7 ladder, given in full once (row 1). The fourth cell's FOURTH-N5 rung disclosed, with 18 without it (row 3b, § 4.8). "About US$22" dropped (row 3e). D57 (2) and (3) both cited |

### Where I differ from the verifier, with evidence

1. **V4, the mechanism: partly.** Version 1's sentence "Unclipped, the K = 10 rung is charged
   with misses in a band it never searched, which understates its gain" is true of the
   unclipped reading. Unclipped, K = 1 matches 388 of 435 references and only 382 once its band
   detections are clipped away (`ladders_new.json` `tier_e.rungs[0].points.opmax`, recall
   0.891954 → 0.878161), credit K = 10 cannot earn. Its conclusion, that the unclipped gain is
   understated, also holds. The verifier is right that the sentence implied the clip relieves
   K = 10, which it does not; version 2 adopts its framing.
2. **V4, "7 misses it cannot reach": a wording caution, not a dispute.** A clipped detection
   within 20 m of the band's edge could still match a band mound, and nothing committed shows
   which of the 7 any rung matches. Version 2 says "scored against 7 mounds outside the area it
   was clipped to", which the 435-reference denominators (clipped TP / recall = 435.0 on every
   rung) establish.
3. **D51 and tier E.** The verifier notes that the PI's quoted words do not name tier E, only
   the log's summary of option 1. I agree, and § 5 A now asks the PI to confirm rather than
   treating D51 as settling it alone.

Nothing else in the verifier's report is disputed. Its two marked mismatches (§ 1 rows 56 and
58: WITHHELD's rungs and NOT CLAIMED's "five") and the inferred K = 10 value it flagged (row 40)
are each addressed above.
