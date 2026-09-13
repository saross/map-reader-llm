# The K ladders: pass count at fixed parameters, Pareto-framed

> **Last revised**: 2026-09-13 (latest — **§ 7.3 amended** after the
> recovery-fragment fix `75d7c8d4c` rebuilt the three refused rungs' proposer
> unions: **no number in this document moves**, and the amendment records the
> sharper finding that the tile-join refusal now **blocks correction** as well as
> reporting, because `evaluate_detections.py` cannot run on those three cells at
> all — so the open tile-join ruling is a prerequisite for repairing them. The
> one figure that did move, the K = 3 rung's F1@20 0.8870 → 0.8860, is not quoted
> anywhere here. Measured:
> `results/k-ladder-2026-09-12/recovery-fix-2026-09-13/`; reported:
> `reports/recovery-drop-fix-2026-09-13.md`. Earlier that day — the PI's two rulings of 2026-09-13
> executed, and **the row is ready for signature**: **§ 6.1 gains the per-family
> Hsu MCB admissible sets** for all 22 tiered ladders on F1 and tile-MCC, run
> with the Era-2 board's own MCB step on each ladder's own frame — K = 3
> admissible on 12 of 22 and the cheapest admissible rung on 10, **no** ladder's
> F1 set excludes K = 10, K = 1 ruled out on F1 on 20 of 22 and admissible on
> tile-MCC on **22 of 22**, three 3.7 GS text rungs withheld by the tile-join
> invariant; and **the carried convention is settled** — the stride ladder's own
> vote shell is the carried point, `k = K` stays as a disclosed column, no number
> recomputed (§ 7.5, § 3's new disclosure table, `phase2/ladder-tables.md`).
> Prior: 2026-09-13 (**§ 8.6 added** on the PI's ruling: the
> verifier-stage reversal stated as a claim with per-number anchors — K = 1 → 10
> raises F1 by +0.0572 consensus-only with tile-MCC rising +0.0444, and by
> +0.0340 verified with tile-MCC falling −0.0308, so the verifier absorbs 40.6 %
> of K's F1 return and reverses the sign of its tile-MCC effect; and **§ 3.3's
> K = 5 row filled** for stride B under the 3.7 verifier. Prior: 2026-09-12
> (**§ 8 added**: the MINIMAL-ladder
> tension measured rather than described. The two corpora agree once resolution
> is accounted for — 487 tiles resolve a ΔF1 of about 0.03 and above, and the
> nine MINIMAL ladders sort by effect size rather than by corpus — and § 8.4 adds
> the verified B-geometry ladder tier E bought for US$4.9595, which is the
> corpus's 23rd and the first verified MINIMAL ladder on the deployment
> geometry. Before that: **§ 7.3 amended**: the withheld
> tile-MCC question is now measured across all 149 committed cells the board
> reads, only these three are affected, the scorer refuses rather than
> emitting, and repair is confirmed to be a corpus-wide decision — see
> `reports/tile-mcc-geometric-join-2026-09-12.md`)). Before that: **§ 7 added:
> the fourteen four-rung
> ladders Phase 2 bought** for US$24.81 over 28 rungs, which closes § 6.3's gap
> and takes the document from eight ladders to twenty-two; § 4.3 extends § 4's
> F1-against-MCC table to them, § 5 points at their Pareto table and figure).
> Prior same-day revisions: § 4.1 added (the § 4 tile-MCC direction
> permutation-tested on all eight ladders, per the PI's ruling), § 4.2 added (the
> same question under the other registered instrument, which agrees), § 2.1 and
> § 6.1 corrected where they described that test as missing; before that,
> original publication — step 5 of the K-ladder
> Phase-1 run, `planning/k-ladder-phase1-run-2026-09-12.md`. Controlling card:
> `planning/k-ladder-review-2026-09-11.md`. Companions: the inventory
> (`inventory.md`), the Phase-2 costing
> (`reports/k-ladder-phase2-costing-2026-09-12.md`), the deltas
> (`reports/k-ladder-phase1-deltas-2026-09-12.md`,
> `reports/k-ladder-phase2-deltas-2026-09-12.md`).
> See [§ Changelog](#changelog).

**Scope, stated first.** Eight fixed-parameter ladders exist and are scorable at
US$0; all eight are tabulated here at their own headline buffer with an audited
cost per rung. The gold-standard ladder is additionally re-scored on the Era-2
board frame. The seven 55-map ladders' descriptive tables are **cited from their
own campaign artefacts**; their pairwise significance is **tested in § 4.1 under
the board instrument** — which is the instrument that tiered those very cells and
holds a committed F1 p-value for every pair, and is therefore the one that can be
gated — and, for the two ladders that also have a registered per-map sign-swap,
**under that instrument too** in § 4.2. § 6 says exactly what is and is not
supplied; the PI's choice between the two instruments stays open, and both
answers agree on tile-MCC. Every figure is read from a committed
artefact named beside it; the machine-readable form of every table is
`ladders.json`.

## 1. What the ladders say, in one paragraph

**The return on a proposer pass is spent mostly between K = 1 and K = 3, and
tile-level discrimination does not improve with K at all.** On the gold standard,
K = 1 → 3 buys +0.0229 F1@20 on the board frame and K = 3 → 10 buys a further
+0.0071 for 2.5 × the money. Across all eight ladders K = 3 takes **49 % to 93 %
of the ladder's total F1 gain** — above 85 % on six of the eight — for **38 % to
64 % of the top rung's cost**. Meanwhile tile-MCC, the buffer-free measure of
*which tiles* hold a mound, **falls on five of the eight ladders**, moves by
+0.003 on two more, and rises by +0.0135 on only one (the gold standard, on the
board frame) — a rise that **does not survive permutation testing** (§ 4.1,
BH p = 0.77), while the MCC FALL is significant on three ladders and **no ladder
shows a significant MCC rise**. More passes buy localisation, not
discrimination. § 4 treats that as the result it is rather than an artefact, and
§ 4.1 tests it.

**What Phase 2 adds to that paragraph (§ 7).** Fourteen more four-rung ladders,
all on one frame and one recipe, turn the statement above from a description
into a conditional one. **The size of K's return is governed by the proposer's
thinking level, and within a thinking level by its temperature.** Across the
thirteen Gemini 3 ladders the K = 1 → best-rung F1 gain is **+0.0139 to
+0.1514**; it is significant on **7 of 7 HIGH-thinking ladders and only 2 of 6
MINIMAL** ones, and **four ladders — every one of them MINIMAL — collapse to a
single statistical tier, where K buys nothing detectable at all**. On both HIGH
tracks the gain rises monotonically with temperature. The MCC story survives
intact and gains its first significant instance: the direction is negative on
11 of 13, and one ladder (HIGH image T 1.0) now shows a **significant** MCC
decline (−0.0637, BH p = 0.0420) where § 4.1 found none among the eight.

## 2. The gold-standard ladder, on the board frame

`stride-phaseb-2026-08-25`, pool `g384_ov128`, 4-map gold standard, curator
reference, prob_t fixed at 0.15, one verifier (`verify_adversarial.md` /
`gemini-3-flash-preview` / MINIMAL / T 0.0 / n 1), and an **exact
re-verification of each rung's own first-N union** — not inherited
probabilities. The only fixed-parameter K ladder in the corpus with that
property.

| K | k | F1@20, board frame | F1@20, grid-common | frame tax | tile-MCC, board frame | n | all-in flex | 55-map, projected | 55-map, measured |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 1 | 0.8605 | 0.8677 | −0.0072 | 0.7834 | 411 | **$1.38** | $24.20 | $20.53 |
| 3 | 3 | **0.8834** | 0.8911 | −0.0077 | 0.7762 | 380 | **$2.64** | $46.30 | $41.22 |
| 5 | 4 | 0.8782 | 0.8856 | −0.0074 | 0.7751 | 394 | **$3.81** | $66.82 | $59.75 |
| 10 | 8 | **0.8905** | 0.8982 | −0.0077 | 0.7969 | 387 | **$6.56** | $115.05 | $103.91 |

Anchors: board-frame columns from `board-frame/*/evaluation.json` (this run, on
sapphire: 14 buffers, 10,000 BCa draws, seed 42, MCC, `era2-b-487`);
grid-common columns from
`results/stride-2026-08-25/conditions-verified/*/eval/evaluation.json`; cost from
`results/stride-2026-08-25/findings.md`, "Exact winner ladder" ("$3.407 flex
measured vs $3.41 priced"); measured 55-map cost from
`results/55map-final-board-r2-2026-09-06/final_board_50m.json`, cells
`A-N1/3/5/10-oracle`.

**Three things to read off it.**

1. **The frame tax is uniform: −0.0072 to −0.0077.** It sits inside the −0.0070
   to −0.0078 the board's other grid-geometry cells already show (the board
   `README.md`, Δ frame column), which is the cross-check that the swap measures
   the frame and not the cell. Because it is uniform, **the ladder's shape is
   frame-invariant** — every conclusion below holds on either frame.
2. **K = 3 is 99.2 % of K = 10's F1 for 40 % of its cost** (0.8834 / 0.8905;
   $2.64 / $6.56). K = 5 is *below* K = 3 by 0.0052, an inversion the stride
   programme already recorded as noise-level (CI half-widths ≈ ±0.025, and the
   inheritance estimates it was first read from were accurate to ±0.008).
3. **The 8,541 / 487 projection overstates by 11 %.** `pass-budget-pareto-v2`
   projected gold-standard rungs to the 55-map corpus by the tile factor
   8,541 / 487 = 17.54. For THIS geometry that is wrong: `g384_ov128` runs **820
   tiles per pass** on the gold standard, not 487, so the projection ($115.05 at
   K = 10) exceeds the measured 55-map cost of the same geometry ($103.91) by
   10.7 %. The projection column is kept for comparability with the registered
   Pareto row; the measured column is the one to cite.

### 2.1 Statistical separation, board instrument, board frame

`scripts/era1_leaderboard_tiering.py` over the four rungs (round-robin tile-swap
micro-F1 permutation, 10,000 permutations, seed 42, BH q = 0.05, greedy-clique
tiers, 487 tiles), plus the Hsu-constrained MCB admissible set from
`scripts/selection_aware_intervals.py`.

**The permutation half is now supplied** (§ 4.1): the one-line command below was
run on sapphire with `--permute-mcc`, and the full round-robin over the four
rungs — F1 at 20 m and tile-MCC, on identical swap masks — is committed at
`mcc-test/tiering/gs-stride-a/tiering_20m.{json,md}`. **Only K = 1 versus K = 10
separates**, on F1 (+0.0300, BH p = 0.0072); no other pair separates on either
metric (1/6 F1 pairs and 0/6 MCC pairs significant at BH q = 0.05), so on this
frame the ladder greedy-cliques into **two tiers: Tier 1 = {K = 10, K = 3,
K = 5}, Tier 2 = {K = 1}**. Note that the greedy-clique tier-1 membership is a
rank band, not an admissible set (defect D20, erratum E83).

**The Hsu MCB admissible set is now supplied too** (2026-09-13, § 6.1): on this
ladder's F1 it is **{K = 3, K = 5, K = 10}** at `w_upper` 0.0160, and on tile-MCC
it is the **whole ladder** at `w_upper` 0.0242 —
`mcb/gs-stride-a/k-ladder-gs-stride-a-2026-09-12{,_mcc}_b20_m1.json`. On this
ladder the two instruments agree: the admissible set and the greedy-clique
Tier 1 hold the same three rungs, which they need not, and § 6.1 records two
ladders where they do not.

## 3. The 55-map ladders

Seven ladders, all at 50 m corrected-F1 on the 8,541-tile corpus. Two operating
points are committed per rung where the campaign recorded both: the **carried**
point (the deployment threshold transferred from the gold standard) and the rung
**oracle** (that rung's own sweep argmax). Under R2 both are reported; the oracle
column is the one that would tier, the carried column is the transfer tax.

**Which reading of "carried" these tables use, disclosed 2026-09-13.** The PI
ruled on 2026-09-13 that the gold-standard stride ladder's own vote shell —
k = 1 / 3 / 4 / 8 at K = 1 / 3 / 5 / 10 — is *the* carried point, with `k = K`
kept as a disclosed column (§ 7.5). Reading that ruling back against these
tables' committed cells shows the two 55-map stride ladders were built on
**different readings of it**, which had not been recorded anywhere before:

| table | committed carried cells | reading |
|---|---|---|
| § 3.1 stride A | `…-n3-carried-posthoc-p0.15-k3`, `…-n5-carried-p0.15-k4`, `…-n10-carried-p0.15-k8` | **the stride shell** |
| § 3.2 stride B | `…-n3-carried-posthoc-p0.15-k3`, `…-n5-carried-p0.15-k5`, `…-n10-carried-p0.15-k10` | **`k = K`** |
| § 3.3 stride B, 3.7 vf | `…-n10-verified37-carried-p0.98-k10` only | **`k = K`** |
| § 3.4 arms 1 and 2 | `arm1-n5-carried-p0.10-k5`, `arm2-n5-carried-p0.80-k5` | **`k = K`** |

Anchor: each cell's `vote_threshold` in `results/run-conditions.json` under
`stride-55map-2026-08-25` and `gemini37-55map-2026-08-29`. **No number in
§§ 3.1–3.4 is changed or recomputed**, because a shell-reading carried cell does
not exist for stride B or for the arms and building one is an API-free rescore
the PI has not asked for. The consequence is stated rather than hidden: **the
transfer taxes in § 3.2, § 3.3 and § 3.4 are `k = K` taxes and the ruling's
convention would make them smaller**, so they should be read as an upper bound on
the transfer cost, exactly as the Phase 2 disclosure column shows (`k = K` costs
up to −0.2566 F1@20 where the shell costs at most −0.0735). Stride A's are
already on the ruling's convention.

### 3.1 Stride A (`g384_ov128_55map`), r2 reference

| K | oracle F1@50 | oracle (prob_t, k) | carried F1@50 | transfer tax | oracle tile-MCC | all-in flex |
|---:|---:|---|---:|---:|---:|---:|
| 1 | 0.8227 | (0.20, k1) | — | — | 0.7006 | $20.53 |
| 3 | 0.8321 | (0.20, k2) | 0.8307 | −0.0014 | 0.7018 | $41.22 |
| 5 | 0.8383 | (0.15, k4) | 0.8383 | 0.0000 | 0.6907 | $59.75 |
| 10 | 0.8419 | (0.15, k7) | 0.8391 | −0.0028 | 0.6954 | $103.91 |

### 3.2 Stride B (`g384_ov192_55map`), r2 reference

| K | oracle F1@50 | oracle (prob_t, k) | carried F1@50 | transfer tax | oracle tile-MCC | all-in flex |
|---:|---:|---|---:|---:|---:|---:|
| 1 | 0.8013 | (0.20, k1) | — | — | 0.7092 | $30.99 |
| 3 | 0.8507 | (0.20, k3) | 0.8477 | −0.0030 | 0.7128 | $65.48 |
| 5 | 0.8516 | (0.20, k5) | 0.8503 | −0.0013 | 0.7098 | $97.22 |
| 10 | 0.8560 | (0.20, k9) | 0.8497 | −0.0063 | 0.7123 | $173.59 |

### 3.3 Stride B under the Gemini 3.7 verifier, r2 reference (R1-non-compliant)

Reported separately because it varies the verifier as well as K, so it is not a
ladder of the review's question. It is the only 55-map ladder that isolates K
under a 3.7 verifier.

| K | oracle F1@50 | oracle (prob_t, k) | carried F1@50 | transfer tax | oracle tile-MCC | all-in flex |
|---:|---:|---|---:|---:|---:|---:|
| 1 | 0.8352 | (0.96, k1) | — | — | 0.7471 | $30.99 † |
| 3 | 0.8747 | (0.96, k3) | — | — | 0.7376 | $65.48 † |
| 5 | 0.8758 | (0.96, k5) | — ‡ | — ‡ | **0.7326** | $97.22 † |
| 10 | 0.8813 | (0.96, k9) | 0.8728 | −0.0085 | 0.7359 | $173.59 † |

† The proposer leg is the same as § 3.2's, so the cost figure is the Gemini 3
board's. The 3.7 **verifier** leg is **not supplied**: that stage's meta was
overwritten by a 29-item cleanup pass, so its 57,482-candidate token load is not
on file (`reports/r7-gaps-deltas-2026-09-11.md` § 2.5). A simulated figure for
the K = 10 rung is about $64.7 on arm 2's per-candidate rate, giving about $238
all-in; it is recorded there, deliberately not in this table, because every other
cost cell here is audited.

‡ **The K = 5 rung, built 2026-09-13 on the PI's ruling.** It was absent from this
table as `zero-usd-inherited, never built` until then, for a reason that turned
out to be a one-line asymmetry rather than a data limit:
`scripts/final_board_sweeps.py`'s `build_g37_families` looped `for n in (1, 3)`,
which is right for the two five-pass arms (a rung at N = 5 would *be* their full
union) and wrong for this cell, which re-verified stride B's **ten** passes. The
rungs are now derived from each family's own `k_max`, so the arms keep exactly
the rungs they had and this cell gains N = 5. The rung is
`stride-55map-2026-08-25::g384-ov192-55map-n5-verified37-oracle-p0.96-k5-r2-gt`,
`results/55map-final-board-r2-2026-09-06/cells/FOURTH-N5-oracle/evaluation.json`
— F1@50 **0.8758** (BCa 95 % CI 0.8679–0.8832), tile-MCC **0.7326**, 4,434
detections, r2 reference, the chain's one engine. Its verifier leg is **not
supplied** for the same reason as every other row here. **No carried figure is
given**, because this family's rungs have no carried cells: the carried column is
"—" at K = 1 and K = 3 too, and the only post-hoc carried nominations on this
board are Runs A and B at N = 3 (PI direction 2026-08-28,
`scripts/final_board_n3_carried.py`). For a reader who wants the transferred
point anyway, `sweep_FOURTH-N5.csv` scores (0.98, k5) — the K = 10 rung's
committed point with k scaled to the rung — at micro-F1@50 **0.8754** over 4,431
detections, against the oracle's micro-F1@50 0.8758; that is a sweep row on the
light scorer, not a registered cell, and it is not a claim.

**What the rung says.** F1 rises 0.8352 → 0.8747 → 0.8758 → 0.8813: the step from
K = 3 to K = 5 buys **+0.0011**, less than a tenth of the +0.0395 that K = 1 → 3
bought, so this ladder saturates between K = 3 and K = 5 exactly as the other
twenty-two do. Tile-MCC is **0.7326**, the *lowest* of the four rungs — below even
K = 10's 0.7359 — so the family's tile-MCC does not fall monotonically, but it is
below K = 1's 0.7471 at every rung above K = 1, which is § 4's pattern. Neither
step is separation-tested: this sub-table is R1-non-compliant and reported
outside the review's instrument, and **the 55-map final board was not re-tiered**
(`results/55map-final-board-r2-2026-09-06/final_board_50m.json`, its tiering and
its 595-pair BH family are untouched; `scripts/final_board_build.py` was not
run), per the PI's ruling on close-out question 5.

### 3.4 Gemini 3.7 arms, r2 reference

Arm 1 carries the Gemini 3 verifier (R1-compliant); arm 2 the 3.7 verifier (not).
Both arms share one five-pass proposer, so their costs are not additive.

| arm | K | oracle F1@50 | carried F1@50 | transfer tax | oracle tile-MCC | all-in flex ‡ |
|---|---:|---:|---:|---:|---:|---:|
| 1 (Gemini 3 vf) | 1 | 0.8413 | — | — | 0.7246 | $37.74 |
| 1 | 3 | 0.8705 | — | — | 0.7179 | $95.45 |
| 1 | 5 | 0.8727 | 0.8551 | **−0.0176** | 0.7147 | $153.16 |
| 2 (3.7 vf) | 1 | 0.8610 | — | — | 0.7422 | $43.16 |
| 2 | 3 | 0.8848 | — | — | 0.7163 | $100.87 |
| 2 | 5 | 0.8871 | 0.8827 | −0.0044 | 0.7147 | $158.58 |

‡ Part-audited, part-simulated and an **upper bound**: the proposer leg is the
audited US$144.27 over five passes (`reports/r7-gaps-deltas-2026-09-11.md`
§ 2.2) scaled to K, and the verifier leg is the arm's audited figure over the
FULL K = 5 union of 12,715 candidates (arm 1 $8.89, arm 2 $14.31, § 2.3) — not
over the rung's smaller union. The rung's own union would be cheaper, so the
K = 1 and K = 3 figures overstate the verifier leg. Flagged rather than silently
scaled: the rung's verifier was never run at all (the ladder inherited
probabilities), so there is no audited figure to scale.

The K = 10 rung of both arms cannot be built: the arms hold five proposer passes.

### 3.5 The standardised-reference ladders

Stride A and Stride B against `best-available-gt-55maps.geojson` reproduce their
r2 siblings to within 0.0005 F1@50 at every rung (A: 0.8231 / 0.8326 / 0.8383 /
0.8420 against 0.8227 / 0.8321 / 0.8383 / 0.8419; B: 0.8013 / 0.8505 / 0.8515 /
0.8558 against 0.8013 / 0.8507 / 0.8516 / 0.8560). They are tabulated in
`ladders.json` and not repeated here: **the ladder's shape does not depend on
which of the two 55-map references it is read against**, which is worth saying
once and then not saying again.

## 4. The result that needs flagging: F1 rises with K, tile-MCC does not

Per `docs/agent-guidance.md` § "Research Finding Calibration", this is raised
explicitly rather than explained away.

Each row compares the ladder's lowest rung with its best rung, on the same
reference and frame.

| ladder | F1, K = 1 → best rung | tile-MCC over the same two rungs | MCC verdict |
|---|---|---|---|
| GS stride A (20 m, board frame) | 0.8605 → 0.8905 (**+0.0300**) | 0.7834 → 0.7969 (+0.0135) | up |
| GS stride A (20 m, grid-common) | 0.8677 → 0.8982 (**+0.0305**) | 0.7894 → 0.8022 (+0.0128) | up |
| 55-map stride A, r2 | 0.8227 → 0.8419 (**+0.0192**) | 0.7006 → 0.6954 (**−0.0052**) | **down** |
| 55-map stride A, standardised | 0.8231 → 0.8420 (**+0.0189**) | 0.7010 → 0.6958 (**−0.0052**) | **down** |
| 55-map stride B, r2 | 0.8013 → 0.8560 (**+0.0547**) | 0.7092 → 0.7123 (+0.0031) | flat |
| 55-map stride B, standardised | 0.8013 → 0.8558 (**+0.0545**) | 0.7097 → 0.7127 (+0.0030) | flat |
| 55-map stride B, 3.7 vf | 0.8352 → 0.8813 (**+0.0461**) | 0.7471 → 0.7359 (**−0.0112**) | **down** |
| 3.7 arm 1 | 0.8413 → 0.8727 (**+0.0314**) | 0.7246 → 0.7147 (**−0.0099**) | **down** |
| 3.7 arm 2 | 0.8610 → 0.8871 (**+0.0261**) | 0.7422 → 0.7147 (**−0.0275**) | **down** |

(The two gold-standard rows are the same four cells on two frames, and count once.)

**All eight ladders gain F1 with K. Five lose tile-MCC over the same range**, two
move by +0.003, and only the gold-standard ladder gains materially. The largest
divergence is arm 2: **+0.0261 F1 against −0.0275 MCC**, almost equal and
opposite.

**This is the expected consequence of what the two metrics measure, not an
error.** F1@20/50 is matching-based and counts detections against reference
points; tile-MCC is a per-tile binary classification of "does this tile contain a
mound". Extra proposer passes add candidates, and the verifier keeps the ones it
believes. Additional true positives land overwhelmingly in tiles ALREADY counted
positive — they raise F1 and move no tile — while additional false positives can
only land in tiles that were negative, each of which flips a tile and costs MCC.
So the pass-count lever buys point recall inside known-positive tiles and pays
for it in tile-level specificity.

**Three reasons to take it seriously rather than file it.**

1. It is **why the pass-count lever looks cheaper than it is** for any
   application whose unit is the map sheet or the tile rather than the individual
   mound — survey triage, for instance, where the question is which tiles a human
   should look at.
2. It is **direction-consistent across two corpora, two geometries, two model
   families and two verifiers**.
3. It **complicates the natural reading of the registered pass-budget Pareto**,
   which is stated on F1 alone. Nothing in that analysis is wrong; it simply does
   not carry the MCC column, and the standing preference is to report MCC
   alongside F1 wherever the inputs allow.

These differences are now permutation-tested — § 4.1 — so the paragraph that
used to stand here, disclaiming any per-ladder significance, has been replaced by
the test rather than kept beside it.

## 4.1 The direction, tested

**The PI's ruling (2026-09-12): the § 4 direction is to be tested, not
described.** It now is, on all eight ladders, for the pair § 4's table compares
(K = 1 against the ladder's best rung) and for every adjacent-rung pair.

**Instrument.** Each ladder is tested with the instrument registered for it:
the **round-robin tile-swap permutation** — the board chain, 10,000 permutations,
seed 42, two-sided, BH q = 0.05 within each ladder's own round-robin —
run through `scripts/era1_leaderboard_tiering.py --permute-mcc`. The harness
was extended so tile-MCC is a permutation statistic rather than a reported
column: each rung's per-tile one-hot (TP, TN, FP, FN) classification is rebuilt
through the house definition (`lib_advanced_metrics.
compute_per_tile_classification`), hard-gated against that cell's committed
`tile_classification` confusion and MCC point estimate, and swapped by
`pairwise_permutation_test.permutation_test_mcc_arrays`. Both kernels draw one
`rng.random(n_tiles) < 0.5` mask per iteration from `default_rng(42)`, so **the
F1 and MCC tests see byte-identical swap masks**: a ΔF1 and a ΔMCC on one rung
pair are two statistics of one permutation, not two experiments. Tile-MCC is
buffer-invariant here (tile truth is intersection with any reference, tile
prediction is any detection assigned to the tile — no matching tolerance
enters), so the MCC column is the same number at 20 m and at 50 m; the F1 column
is at each ladder's own headline buffer. Rungs are the **oracle** basis, the
basis § 4 tabulates. Artefacts: `mcc-test/<ladder>.json` (per-ladder, with raw
and BH p-values, the permutation parameters, the gate record and the instrument
used) and `mcc-test/summary.json`; the underlying round-robins are
`mcc-test/tiering/<ladder>/tiering_<buffer>m.{json,md}`.

**The gate, first.** For the seven 55-map ladders every rung is a cell of a
committed final board whose `pairwise` table records the same tile-swap micro-F1
permutation, so the F1 side is reproducible against a committed number: **all 25
gated pairs reproduce the committed `f1_a`, `f1_b`, `observed_diff` and raw
`p_value` to the recorded precision** (6 dp on the F1 quantities, 4 dp on the
p-value) — `results/55map-final-board-r2-2026-09-06/final_board_50m.json` for the
r2 ladders and `results/55map-final-board-2026-08-27/final_board_50m.json` for
the standardised siblings. `bh_adjusted_p` is deliberately not gated: the board
adjusts over its own 595-pair family, this run adjusts within each ladder. The
gold-standard ladder's four pairs have **no committed pairwise table to gate
against** — that is precisely the § 6.1 gap — so its gate is the harness's own:
each rung's rebuilt micro-F1 equals its committed evaluation F1 to 4 dp
(gap +0.0000 on all four) and each rung's rebuilt tile confusion and MCC equal
its committed `tile_classification` exactly. No MCC number below was read before
its ladder's gate passed.

| ladder | pair | ΔF1 (BH p) | ΔMCC (BH p) | verdict |
|---|---|---:|---:|---|
| GS stride A (20 m, board frame) | K1 → K10 (best) | **+0.0300** (0.0072) | +0.0134 (0.7678) | F1 up; MCC move does not separate |
| GS stride A | K1 → K3 | +0.0229 (0.1056) | −0.0072 (0.8081) | neither separates |
| GS stride A | K3 → K5 | −0.0053 (0.4693) | −0.0011 (1.0000) | neither separates |
| GS stride A | K5 → K10 | +0.0123 (0.1296) | +0.0217 (0.1947) | neither separates |
| 55-map stride A, r2 | K1 → K10 (best) | **+0.0192** (<0.0001) | −0.0052 (0.1984) | F1 up; MCC move does not separate |
| 55-map stride A, r2 | K1 → K3 | **+0.0094** (<0.0001) | +0.0012 (0.6391) | F1 up; MCC move does not separate |
| 55-map stride A, r2 | K3 → K5 | **+0.0062** (0.0079) | **−0.0111** (0.0066) | F1 up, **MCC down** — both separate |
| 55-map stride A, r2 | K5 → K10 | **+0.0036** (0.0079) | **+0.0047** (0.0300) | F1 up, **MCC up** — both separate |
| 55-map stride A, standardised | K1 → K10 (best) | **+0.0188** (<0.0001) | −0.0052 (0.1984) | F1 up; MCC move does not separate |
| 55-map stride A, standardised | K1 → K3 | **+0.0094** (<0.0001) | +0.0012 (0.6391) | F1 up; MCC move does not separate |
| 55-map stride A, standardised | K3 → K5 | **+0.0058** (0.0132) | **−0.0111** (0.0066) | F1 up, **MCC down** — both separate |
| 55-map stride A, standardised | K5 → K10 | **+0.0036** (0.0092) | **+0.0047** (0.0300) | F1 up, **MCC up** — both separate |
| 55-map stride B, r2 | K1 → K10 (best) | **+0.0547** (<0.0001) | +0.0031 (0.5592) | F1 up; MCC move does not separate |
| 55-map stride B, r2 | K1 → K3 | **+0.0494** (<0.0001) | +0.0035 (0.5592) | F1 up; MCC move does not separate |
| 55-map stride B, r2 | K3 → K5 | +0.0010 (0.5086) | −0.0030 (0.4122) | neither separates |
| 55-map stride B, r2 | K5 → K10 | **+0.0043** (0.0035) | +0.0025 (0.4395) | F1 up; MCC move does not separate |
| 55-map stride B, standardised | K1 → K10 (best) | **+0.0545** (<0.0001) | +0.0031 (0.5832) | F1 up; MCC move does not separate |
| 55-map stride B, standardised | K1 → K3 | **+0.0492** (<0.0001) | +0.0035 (0.5686) | F1 up; MCC move does not separate |
| 55-map stride B, standardised | K3 → K5 | +0.0010 (0.5156) | −0.0030 (0.4122) | neither separates |
| 55-map stride B, standardised | K5 → K10 | **+0.0043** (0.0035) | +0.0025 (0.4395) | F1 up; MCC move does not separate |
| 55-map stride B, 3.7 vf | K1 → K10 (best) | **+0.0462** (<0.0001) | **−0.0112** (<0.0001) | F1 up, **MCC down** — both separate |
| 55-map stride B, 3.7 vf | K1 → K3 | **+0.0396** (<0.0001) | **−0.0095** (<0.0001) | F1 up, **MCC down** — both separate |
| 55-map stride B, 3.7 vf | K3 → K10 | **+0.0066** (<0.0001) | −0.0017 (0.2644) | F1 up; MCC move does not separate |
| 3.7 arm 1 | K1 → K5 (best) | **+0.0315** (<0.0001) | **−0.0099** (0.0168) | F1 up, **MCC down** — both separate |
| 3.7 arm 1 | K1 → K3 | **+0.0292** (<0.0001) | **−0.0067** (0.0498) | F1 up, **MCC down** — both separate |
| 3.7 arm 1 | K3 → K5 | +0.0023 (0.1088) | **−0.0032** (0.0498) | **MCC down** separates, F1 does not |
| 3.7 arm 2 | K1 → K5 (best) | **+0.0261** (<0.0001) | **−0.0275** (<0.0001) | F1 up, **MCC down** — both separate |
| 3.7 arm 2 | K1 → K3 | **+0.0238** (<0.0001) | **−0.0258** (<0.0001) | F1 up, **MCC down** — both separate |
| 3.7 arm 2 | K3 → K5 | +0.0023 (0.1208) | −0.0017 (0.3580) | neither separates |

ΔF1 and ΔMCC are both oriented as **(higher K) − (lower K)**. Bold marks a
BH-significant difference at q = 0.05. `<0.0001` is a BH-adjusted p below the
1/10,000 permutation floor. § 4's grid-common gold-standard row is not tested
separately: it is the same four cells on a different frame, and the ladder is
tested on the board frame R2 tiers on.

### What survives

**The direction survives; the one counter-example does not.**

1. **F1 rises with K on every ladder, and the rise is significant on all
   eight** for K = 1 → best rung (the gold standard's +0.0300 at BH p = 0.0072
   included). Nothing in § 4's F1 column is weakened.
2. **No ladder shows a significant tile-MCC RISE from K = 1 to its best rung.**
   Five of the eight move MCC by less than the instrument can resolve;
   **three show a significant MCC FALL** — the 3.7-verifier stride B
   (−0.0112), 3.7 arm 1 (−0.0099) and 3.7 arm 2 (−0.0275), all at
   BH p ≤ 0.0168. So "more passes do not buy tile-level discrimination" is
   testable and holds, and on the three ladders where the instrument resolves,
   more passes measurably COST discrimination.
3. **The gold standard's MCC gain does not survive.** § 4 called +0.0135 the one
   material rise; on 487 tiles it tests at BH p = 0.7678, and no gold-standard
   pair separates on either metric except K = 1 → K = 10 on F1. The 4-map
   instrument cannot resolve a ΔMCC of this size — which is the same
   power limitation § 2 records for its F1 CIs (half-widths ≈ ±0.025) — so the
   honest reading is that the gold-standard exception was never evidence of a
   rise, and the eight-ladder direction has no tested counter-example.
4. **The within-ladder path is not monotonic, and that is new.** On both stride
   A ladders the K = 3 → K = 5 step loses MCC significantly (−0.0111,
   BH p = 0.0066) while the K = 5 → K = 10 step regains it significantly
   (+0.0047, BH p = 0.0300) — two significant, opposite-signed MCC steps inside
   one ladder whose end-to-end ΔMCC (−0.0052) does not separate. § 4's
   endpoint-to-endpoint framing hides that. On 3.7 arm 1 the K = 3 → K = 5 step
   is the mirror image of the headline trade: **MCC falls significantly
   (−0.0032) while ΔF1 does not separate at all** — the only pair in the table
   where the MCC test resolves and the F1 test does not.
5. **The mechanism § 4 proposes is consistent with the test.** The three
   ladders whose MCC falls significantly are the three with a Gemini 3.7
   component, which are also the three with the largest MCC movements; the
   mechanism (extra true positives land in already-positive tiles, extra false
   positives flip negative tiles) predicts exactly a metric divergence whose
   size tracks how many new false positives the extra passes contribute.

**What is still NOT claimed.** That the five non-separating ladders' MCC moves
are zero — five of eight are simply below this instrument's resolution, and a
non-significant −0.0052 is not a demonstrated absence of decline. Nor is any
MCC *ranking* of rungs claimed: tiering stays on the preregistered F1, and the
MCC round-robins are reported as tests of named pairs, not as a board.

## 4.2 The same question under the other registered instrument

§ 6.1 records that the PI's ruling on which instrument the 55-map ladders should
be tested under is pending. **Two of the seven have a second registered
instrument** — the per-map paired sign-swap of `scripts/stride55_ladder.py`
(bet P7) — so those two are reported under both, and the ruling can be made
knowing what turns on it.

**The instrument.** Per-map paired sign-swap over the **55 map sheets** as
pairing units, 10,000 permutations, seed 42, two-sided with a 1/10,000 floor,
BH q = 0.05 within each cell's ladder. Statistic pair: corrected-F1 at 50 m from
pooled per-map TP/FP/FN (`paired_permutation`, registered) and tile-MCC from
pooled per-map tile confusion (`paired_permutation_mcc`, added 2026-09-12 as its
sibling — same pairing units, same seed, same permutation count, therefore the
same per-map swap masks). It scores against the **in-process extended ground
truth** (student references plus canonical adjudicated phantoms gated at 50 m),
not the board's materialised r2 reference, which is why its rung F1 values differ
from the board cells'. Artefacts: `mcc-test/sign-swap/ladder_pairs.json`, with
the rung rebuild at `mcc-test/sign-swap/rebuild/ladder.json`; the committed
2026-08-27 artefacts were not touched.

**Its gate.** The rebuild reproduces the committed K = 10 union (38,713 and
57,482 candidates; votes identical; max centroid drift 0.069 m), the committed
primary F1 to 1e-6, **each rung's committed oracle corrected-F1 to 1e-6**, and
**all four committed `p7_saturation` F1 results to ten decimal places on the
delta and exactly on the p-value** (stride A carried −0.0003664980 / p = 0.8239
and oracle −0.0039847569 / p = 0.0131; stride B carried +0.0015610879 /
p = 0.3243 and oracle −0.0053391701 / p = 0.0003).

| ladder | pair | board tile-swap: ΔF1 (BH p) | sign-swap: ΔF1 (BH p) | board: ΔMCC (BH p) | sign-swap: ΔMCC (BH p) |
|---|---|---:|---:|---:|---:|
| 55-map stride A | K1 → K10 | **+0.0192** (<0.0001) | **+0.0176** (0.0004) | −0.0052 (0.1984) | −0.0052 (0.1176) |
| 55-map stride A | K1 → K3 | **+0.0094** (<0.0001) | **+0.0088** (0.0006) | +0.0012 (0.6391) | +0.0006 (0.8201) |
| 55-map stride A | K3 → K5 | **+0.0062** (0.0079) | +0.0048 (0.0655) | **−0.0111** (0.0066) | **−0.0105** (0.0184) |
| 55-map stride A | K5 → K10 | **+0.0036** (0.0079) | **+0.0040** (0.0175) | **+0.0047** (0.0300) | **+0.0047** (0.0262) |
| 55-map stride B | K1 → K10 | **+0.0547** (<0.0001) | **+0.0499** (0.0002) | +0.0031 (0.5592) | +0.0036 (0.3236) |
| 55-map stride B | K1 → K3 | **+0.0494** (<0.0001) | **+0.0446** (0.0002) | +0.0035 (0.5592) | +0.0040 (0.3236) |
| 55-map stride B | K3 → K5 | +0.0010 (0.5086) | +0.0000 (0.9966) | −0.0030 (0.4122) | −0.0030 (0.3236) |
| 55-map stride B | K5 → K10 | **+0.0043** (0.0035) | **+0.0053** (0.0004) | +0.0025 (0.4395) | +0.0025 (0.3236) |

**The ruling does not change the MCC answer.** Across the eight pairs both
instruments cover, **all eight tile-MCC significance calls agree** — the same two
pairs separate (stride A's K = 3 → 5 fall and K = 5 → 10 rise) and the same six
do not, with ΔMCC estimates agreeing to 0.0006 or better. **One F1 call differs**:
stride A's K = 3 → 5 step is significant on the board tile-swap (+0.0062,
BH p = 0.0079) and not on the sign-swap (+0.0048, BH p = 0.0655) — expected, since
55 map sheets are far fewer pairing units than 8,541 tiles, and the sign-swap's
reference is the pre-r2 one. So the instrument question is live for marginal F1
claims and **immaterial to the § 4.1 conclusion**.

**Not available for the other five.** Three 55-map ladders (the 3.7-verifier
stride B and the two 3.7 arms) have no registered sign-swap at all —
`scripts/gemini37_arm_ladder.py` and `scripts/gemini37_fourth_cell_ladder.py`
carry no permutation test (§ 6.1) — and the two standardised-reference siblings
are the same detections against the other 55-map reference, which the sign-swap
does not score. Those five are reported under the board instrument only.

## 4.3 The same table for the fourteen Phase 2 ladders

Same construction as § 4 — each family's lowest rung against its best rung, on
one reference and one frame — for the fourteen ladders § 7 adds. All are gold
standard, board frame `era2-b-487`, 20 m, sweep-optimal operating point.

| ladder | F1@20, K = 1 → best rung | tile-MCC over the same two rungs | MCC verdict |
|---|---|---|---|
| MINIMAL text T 0.3 | 0.8555 → 0.8778 (**+0.0223**) | 0.7986 → 0.7735 (**−0.0251**) | **down** |
| MINIMAL text T 0.7 | 0.8575 → 0.8739 (**+0.0164**) | 0.7881 → 0.7957 (+0.0076) | up |
| MINIMAL text T 1.0 | 0.8235 → 0.8781 (**+0.0546**) | 0.8095 → 0.7881 (**−0.0214**) | **down** |
| HIGH text T 0.3 | 0.8314 → 0.8873 (**+0.0559**) | 0.8068 → 0.7805 (**−0.0263**) | **down** |
| HIGH text T 0.7 | 0.8009 → 0.8744 (**+0.0735**) | 0.7737 → 0.7641 (−0.0096) | **down** |
| HIGH text T 1.0 | 0.7810 → 0.8804 (**+0.0994**) | 0.8162 → 0.7910 (**−0.0252**) | **down** |
| MINIMAL image T 0.3 | 0.7680 → 0.7819 (**+0.0139**) | 0.8443 → 0.8377 (−0.0065) | **down** |
| MINIMAL image T 0.7 | 0.7252 → 0.7881 (**+0.0629**) | 0.8437 → 0.8223 (**−0.0214**) | **down** |
| MINIMAL image T 1.0 | 0.7044 → 0.7428 (**+0.0384**) | 0.8360 → 0.8078 (**−0.0282**) | **down** |
| HIGH image T 0.3 | 0.6925 → 0.7705 (**+0.0780**) | 0.8270 → 0.8294 (+0.0024) | flat |
| HIGH image T 0.7 | 0.6909 → 0.7868 (**+0.0959**) | 0.8435 → 0.8359 (−0.0076) | **down** |
| HIGH image T 1.0 | 0.6119 → 0.7633 (**+0.1514**) | 0.8640 → 0.8002 (**−0.0637**) | **down, and SIGNIFICANT** |
| scale-4-optimal 487 | 0.6376 → 0.7683 (**+0.1307**) | 0.8726 → 0.8154 (**−0.0572**) | **down** (BH p = 0.076) |
| 3.7 text, GS B geometry | 0.8495 → 0.9068 (**+0.0573**) | — (withheld, § 7.3) | — |

**All fourteen gain F1. Eleven of the thirteen with an interpretable MCC lose
it**, one is flat and one gains — the same direction § 4 reported on the eight,
now on fourteen more ladders, two model families, two thinking levels, two
modalities and three temperatures. § 4.1 found **no** significant MCC change
among the eight; here **one is significant** (HIGH image T 1.0, −0.0637, BH
p = 0.0420) and one is a near miss (scale-4-optimal, −0.0572, BH p = 0.0762).
So the count of significant MCC declines in the corpus moves from zero to one,
and the direction is now supported by twenty-two ladders rather than eight.

The 3.7 family's MCC is **withheld rather than reported** at K = 1 and K = 3;
§ 7.3 gives the reason, which is an instrument property and not a measurement.

## 5. The Pareto frame

Figure: `figures/k-ladder-pareto.png` — audited all-in cost (log axis) against the
headline F1, one line per ladder, each point labelled with its K. The fourteen
Phase 2 ladders have their own figure, `figures/k-ladder-pareto-phase2.png`, and
their own efficient-rung table in
`phase2/ladder-tables.md` § "Pareto"; § 7.4 reads the result off it. In table
form, the efficient rungs of each Phase 1 ladder (a rung is efficient when no
cheaper rung of the same ladder scores as well):

| ladder | efficient rungs (K @ US$ → F1) |
|---|---|
| GS stride A (20 m, board frame) | 1 @ $1.38 → 0.8605; 3 @ $2.64 → 0.8834; 10 @ $6.56 → 0.8905 |
| 55-map stride A, r2 (50 m) | 1 @ $20.53 → 0.8227; 3 @ $41.22 → 0.8321; 5 @ $59.75 → 0.8383; 10 @ $103.91 → 0.8419 |
| 55-map stride B, r2 (50 m) | 1 @ $30.99 → 0.8013; 3 @ $65.48 → 0.8507; 5 @ $97.22 → 0.8516; 10 @ $173.59 → 0.8560 |
| 55-map stride B, 3.7 vf (50 m) | 1 → 0.8352; 3 → 0.8747; 10 → 0.8813 (verifier cost not supplied) |
| 3.7 arm 1 (50 m) | 1 @ $37.74 → 0.8413; 3 @ $95.45 → 0.8705; 5 @ $153.16 → 0.8727 |
| 3.7 arm 2 (50 m) | 1 @ $43.16 → 0.8610; 3 @ $100.87 → 0.8848; 5 @ $158.58 → 0.8871 |

**K = 5 is off the efficient set on the gold standard** (0.8782 for $3.81, below
K = 3's 0.8834 for $2.64) and on it, barely, everywhere else. **K = 10 is on every
efficient set it exists in, and always by the smallest margin on its ladder**:
+0.0071 F1 for $3.92 more on the gold standard, +0.0036 for $44.16 more on 55-map
stride A, +0.0044 for $76.37 more on stride B. On stride B that last step is
**about US$17,400 per 0.001 F1** (76.37 / 0.0044) — which is the number to put
beside a deployment decision, and it is the sense in which "the ladder
saturates" is an economic statement rather than a statistical one.

## 6. What is NOT in this document

Named, not glossed. Each is a gap in this run, not in the data.

### 6.1 The pairwise permutation testing and the MCB — both now run

R2 and the run card ask for paired tile-swap permutation between adjacent rungs
and against K = 10, BH q = 0.05, and a Hsu MCB admissible set per family.
**The permutation testing was not run in the original revision; it was run on
2026-09-12 and is § 4.1.** **The MCB admissible sets were run on 2026-09-13, on
the PI's ruling to "wait for the sets" before signing the review's row, and are
the table below.** For the gold-standard ladder everything needed was committed
and the command is one line (now with the `--permute-mcc` flag the § 4.1 run
added):

```bash
python scripts/era1_leaderboard_tiering.py \
    --analysis-id k-ladder-gs-stride-a-2026-09-12 \
    --conditions results/k-ladder-2026-09-12/tiering-input/gs-stride-a/run-conditions.json \
    --analyses  results/k-ladder-2026-09-12/tiering-input/gs-stride-a/run-analyses.json \
    --bounds inputs/vectors/bounds/384/era2_b_intersection_bounds.geojson \
    --permute-mcc \
    --output-dir results/k-ladder-2026-09-12/mcc-test/tiering/gs-stride-a
```

**Correction, 2026-09-12.** The original revision of this section stated that
the 55-map cells "were scored by `compute_corrected_f1_multi_buffer.py`, which
writes `summary.json` with no `cli_args`", and so could not be rebuilt for a
tile-swap. **That is not what is on disk.** All 31 cells of
`results/55map-final-board-r2-2026-09-06/cells/` and all 19 of
`results/55map-final-board-2026-08-27/cells/` carry a `detections.geojson`
alongside an `evaluation.json` written by `scripts/evaluate_detections.py` with
complete `_metadata.cli_args` — detections, ground truth
(`best-available-gt-55maps-r2.geojson`, the MATERIALISED extended reference),
bounds, `mcc: true`, 10,000 bootstrap draws, seed 42 — and a
`summary.tile_classification` block with the confusion cells. A tile-swap over
them is therefore a one-line rebuild too, which is how § 4.1 ran.

**Second correction.** The same paragraph named two artefacts as the registered
per-map sign-swap's committed results. Only one is: the `p7_saturation` block of
`results/stride55-2026-08-27/ladder.json`. The `pairwise` table of
`final_board_50m.json` is **not** a sign-swap — its own `instrument` field reads
"round-robin tile-swap micro-F1 permutation (10000, seed 42) + BH q=0.05 +
greedy-clique tiers (the GS chain)", over 8,541 tiles. And
`scripts/gemini37_arm_ladder.py` carries **no permutation test at all**: it
writes rung oracles and a sweep CSV, nothing inferential. So the two instruments
actually registered over these ladders are:

- **The board's round-robin tile-swap** (`final_board_build.py`, the GS chain),
  which tiered every one of these cells and holds a committed F1 p-value for
  **every pair § 4.1 asks about**, on all seven 55-map ladders. This is the
  instrument § 4.1 runs, and reproducing those committed F1 p-values is its gate.
- **The per-map paired sign-swap** (`scripts/stride55_ladder.py`, 10,000
  permutations, seed 42; bet P7), which exists for **two** of the seven ladders
  (the Gemini-3 stride A and B cells) and, as committed, for **one pair** of each
  (N = 5 versus N = 10), against the pre-r2 extended ground truth built in
  process from student references plus adjudicated phantoms — which is why its
  rung F1 values (0.8186 / 0.8274 / 0.8322 on stride A) differ from the board
  cells' (0.8227 / 0.8321 / 0.8383).

**The PI's choice between them stands open, and § 4.1 does not take it.** The
board instrument is reported for all eight ladders because it is the only one
that covers all of them and the only one with a committed F1 gate; the sign-swap
is reported separately, extended to the same pair set and to tile-MCC, for the
two ladders where it is registered (`mcc-test/sign-swap/`). Where both are
available they answer slightly different questions — a tile-swap over 8,541 tiles
against the materialised r2 reference versus a sign-swap over 55 map sheets
against the in-process extended reference — so the ruling is a real one, and it
is put back rather than taken.

#### The Hsu MCB admissible sets, supplied 2026-09-13

**The instrument, first.** The Era-2 board's own MCB step verbatim —
`scripts/selection_aware_intervals.py --board`, which targets Hsu's quantity
`theta_i = stat_i - max(j != i) stat_j` and rules a rung out as best only when
its simultaneous **upper** bound falls at or below zero, with the critical value
bootstrapped over **tiles** (10,000 resamples, seed 42, m-out-of-n 1.0,
simultaneous 95 %) rather than read from Dunnett's table, which assumes normal
homoscedastic means that micro-F1 on correlated tiles does not satisfy. Each
ladder is run **on its own frame, reference and headline buffer**, the ones its
committed tiering used: the gold-standard and tier E ladders on the board frame
by override at 20 m, the thirteen Phase 2 families on the board frame at 20 m,
the seven 55-map ladders on the 8,541-tile deployment frame against their own r2
or standardised reference at 50 m. Driver: `scripts/k_ladder_mcb.py`; artefacts
`mcb/<ladder>/` with the roll-up in `mcb/summary.json` and this table in
`mcb/table.md`.

**The gate, before any set is read.** Every one of the **44 runs** (22 ladders
x 2 metrics) had to reproduce its ladder's committed `tiering_<buffer>m.json`
ranking: the candidate label set exactly, each rung's `observed_micro_f1`, and
each rung's `mcc`. **170 candidate rows gated, all passed, maximum absolute
deviation 4.958e-05** (`mcb/summary.json` key `gate_all_passed`, and each
ladder's `gates`). The reference is the committed tiering rather than the ladder
inventories on purpose: `ladders.json` records the gold-standard ladder's
tile-MCC on its **grid-common** frame (0.7894 at K = 1) while this MCB runs it on
the **board** frame (0.7834), so gating against the inventory would have refused
a correct run.

| ladder | rungs (K) | F1-admissible set | tile-MCC-admissible set | w_upper (F1 / MCC) |
|---|---|---|---|---|
| GS stride A, exact re-verification (board frame) | 1, 3, 5, 10 | **3**, **5**, **10** | **1**, **3**, **5**, **10** | 0.0160 / 0.0242 |
| Grid 384 px / 50 % MINIMAL text, verified (tier E) | 1, 3, 5, 10 | **3**, **5**, **10** | **1**, **3**, **5** | 0.0151 / 0.0259 |
| Gemini 3 MINIMAL text 384 px, T 0.3 | 1, 3, 5, 10 | **3**, **5**, **10** | **1**, **3**, **10** | 0.0185 / 0.0270 |
| Gemini 3 MINIMAL text 384 px, T 0.7 | 1, 3, 5, 10 | **1**, **3**, **5**, **10** | **1**, **3**, **5**, **10** | 0.0181 / 0.0253 |
| Gemini 3 MINIMAL text 384 px, T 1.0 | 1, 3, 5, 10 | **3**, **5**, **10** | **1**, **3**, **5**, **10** | 0.0231 / 0.0313 |
| Gemini 3 HIGH text 384 px, T 0.3 | 1, 3, 5, 10 | **3**, **5**, **10** | **1**, **3**, **5**, **10** | 0.0185 / 0.0392 |
| Gemini 3 HIGH text 384 px, T 0.7 | 1, 3, 5, 10 | **5**, **10** | **1**, **3**, **5**, **10** | 0.0246 / 0.0419 |
| Gemini 3 HIGH text 384 px, T 1.0 | 1, 3, 5, 10 | **3**, **5**, **10** | **1**, **3**, **5**, **10** | 0.0284 / 0.0385 |
| Gemini 3 MINIMAL image 384 px, T 0.3 | 1, 3, 5, 10 | **1**, **3**, **5**, **10** | **1**, **3**, **5**, **10** | 0.0198 / 0.0276 |
| Gemini 3 MINIMAL image 384 px, T 0.7 | 1, 3, 5, 10 | **5**, **10** | **1**, **3**, **5**, **10** | 0.0280 / 0.0279 |
| Gemini 3 MINIMAL image 384 px, T 1.0 | 1, 3, 5, 10 | **3**, **5**, **10** | **1**, **3**, **5**, **10** | 0.0268 / 0.0405 |
| Gemini 3 HIGH image 384 px, T 0.3 | 1, 3, 5, 10 | **5**, **10** | **1**, **3**, **5**, **10** | 0.0324 / 0.0336 |
| Gemini 3 HIGH image 384 px, T 0.7 | 1, 3, 5, 10 | **3**, **5**, **10** | **1**, **3**, **5** | 0.0309 / 0.0329 |
| Gemini 3 HIGH image 384 px, T 1.0 | 1, 3, 5, 10 | **5**, **10** | **1**, **3**, **5** | 0.0326 / 0.0453 |
| Gemini 3 scale-4-optimal 487 | 1, 3, 5, 10 | **5**, **10** | **1**, **3**, **5** | 0.0287 / 0.0427 |
| 55-map stride A, r2 | 1, 3, 5, 10 | **5**, **10** | **1**, **3** | 0.0047 / 0.0059 |
| 55-map stride A, standardised | 1, 3, 5, 10 | **5**, **10** | **1**, **3** | 0.0047 / 0.0059 |
| 55-map stride B, r2 | 1, 3, 5, 10 | **5**, **10** | **1**, **3**, **5**, **10** | 0.0047 / 0.0049 |
| 55-map stride B, standardised | 1, 3, 5, 10 | **5**, **10** | **1**, **3**, **5**, **10** | 0.0047 / 0.0049 |
| 55-map stride B, 3.7 verifier | 1, 3, 10 | **10** | **1** | 0.0047 / 0.0043 |
| 3.7 arm 1 | 1, 3, 5 | **3**, **5** | **1**, **3** | 0.0048 / 0.0071 |
| 3.7 arm 2 | 1, 3, 5 | **3**, **5** | **1** | 0.0056 / 0.0096 |

Bold marks a rung that **cannot be ruled out as the best rung of its own
ladder** at simultaneous 95 %. `w_upper` is the one-sided simultaneous width the
bootstrap put on that ladder's deviations, and is the resolution figure to read
the set against.

**Five things to read off it.**

1. **K = 3 is admissible on 12 of the 22 ladders, and is the CHEAPEST
   admissible rung on 10 of them.** Two more admit K = 1 as well (so their
   cheapest admissible rung is K = 1), nine admit nothing below K = 5, and one
   admits nothing below K = 10. So the review's Pareto reading — K = 3 is on the
   efficient set of every ladder — is a *cost* statement that the simultaneous
   instrument endorses on roughly half the corpus and declines on the other
   half: on nine ladders a K = 3 rung **can** be ruled out as best, even though
   it remains the efficient buy.
2. **No ladder's F1-admissible set excludes K = 10.** All twenty ladders that
   have a K = 10 rung admit it. That is the formal counterpart of § 7.4's
   economic finding: the top rung is never statistically *excluded*, it is only
   never *worth* its price.
3. **K = 1 is ruled out on F1 on 20 of 22 ladders, and admissible on tile-MCC on
   22 of 22.** It holds the highest tile-MCC on 13 of the 22 and is never ruled
   out on it. This is the review's "the two objectives select different rungs"
   finding stated by the canonical simultaneous instrument instead of by a
   pairwise count: **on F1 the cheapest rung is almost always ruled out; on
   tile-level discrimination it never is.**
4. **The MCC sets are much larger than the F1 sets** — the whole ladder on 12 of
   22, against 2 of 22 on F1 — which is § 4.1's result in another form: tile-MCC
   moves rarely separate. Where MCC does resolve it resolves sharply and against
   K: tier E, both HIGH image T 0.7 and T 1.0, scale-4-optimal, both stride A
   ladders and stride B under the 3.7 verifier all exclude K = 10 on tile-MCC
   (7 of the 20 that have it), and on two ladders — 55-map stride B under the
   3.7 verifier, and 3.7 arm 2 — the MCC-admissible set is **{K = 1} alone**.
5. **Resolution tracks the corpus, exactly as § 8 measured it.** The
   simultaneous F1 width is 0.0151 to 0.0326 on the 487-tile gold standard and
   0.0047 to 0.0056 on the 8,541-tile deployment corpus — three to six times
   narrower — so a deployment ladder's smaller admissible set reflects its
   tighter band and not a different response to K.

**The MCB and the greedy clique disagree in BOTH directions, which is what
erratum E83 warns of.** The committed tie set is a rank band from pairwise
permutation plus BH plus a greedy clique; the admissible set is simultaneous by
construction. Compared cell for cell, the F1-admissible set is **smaller** than
the committed tie set on two ladders and **larger** on six. The sharpest case is
instructive: § 7.1 reports four MINIMAL ladders that "greedy-clique into a
single tier, where K buys nothing detectable at all", and under MCB only **two
of those four** are admissible whole — MINIMAL text T 0.3 and MINIMAL image
T 1.0 both rule K = 1 out as best ({3, 5, 10}) while their clique retained all
four rungs. **§ 7.1's statement is not wrong and is not withdrawn**: a
within-ladder pairwise BH family and a simultaneous comparison against the best
answer different questions, and the pairwise one is the registered tiering
instrument. But "one tier" must not be read as "every rung could be the best
one", and on two of those four ladders it is not.

**Withheld, and listed.** The twenty-third ladder — the Gemini 3.7
gold-standard text screen (`g384_ov192_g37`) — has **no admissible set on
either metric**. The tile-join invariant refuses the per-tile TP/FP/FN table of
three of its four rungs on this frame
(`gemini37-screen-2026-08-28::g37-text-k1-verified-opmax`,
`…::g37-text-k1-verified-carried-p0.10-k1`, `…::g37-text-k3-verified-opmax`),
and the refusal falls on the **F1** arm as well as the MCC arm, leaving two
sound rungs of four — below the review's three-rung bar. Its whole-frame F1 is
unaffected and is reported in full in § 4.3 and `phase2/ladder-tables.md`. The
withholding is the board's own (its README's 2026-09-13 entry, "Admitted but
WITHHELD") and is lifted only by the corpus-wide tile-join decision, still open
(§ 7.3; `reports/tile-mcc-geometric-join-2026-09-12.md`).

### 6.2 No analysis row

The run card asks for one UNSIGNED analysis row `k-ladder-2026-09-12`. It is not
authored, because an analysis row states an outcome and this document's headline
outcome — which rungs are statistically separable — is exactly what § 6.1 did not
measure. Authoring a row whose `outcome` described only the descriptive tables
would register a weaker claim than the data supports and then have to be amended.
The row is drafted in `reports/k-ladder-phase1-deltas-2026-09-12.md` § 5, ready to
author once § 6.1 lands.

**Still not authored, 2026-09-12.** § 6.1's permutation half has landed (§ 4.1),
but the MCB admissible sets have not, and the drafted row's outcome is about
which rungs are separable — so authoring it now would register the same
partially-measured claim the original decision avoided. The § 4.1 result is
committed under `mcc-test/` and cited from this document; the row waits on the
MCB.

**Authored, and now complete — 2026-09-13.** The row
`results/run-analyses.json` → `k-ladder-2026-09-12` was authored UNSIGNED by the
close-out job of 2026-09-12, with its `_signature_note` recording that the MCB
sets were still missing. § 6.1's MCB half landed on 2026-09-13 and the row's
outcome now states it. **Both halves of § 6.1 are therefore supplied and the row
is ready for the PI's signature**; `manually_verified_at` is still `null`,
because only the PI signs an outcome that is the review's headline claim.

### 6.3 The Gemini 3 `pv-diag-384` ladders — GAP CLOSED by Phase 2

This section recorded that every one of those families held two rungs, K = 5
and K = 10, so none reached the three-rung bar (`inventory.md` § 3), and that
their K = 1 and K = 3 rungs were Phase 2, costed at US$24.84 for all 28
(`reports/k-ladder-phase2-costing-2026-09-12.md`).

**The PI approved all four tiers on 2026-09-12 and the run executed them for
US$24.8065.** All thirteen `pv-diag-384` families and the 3.7 gold-standard
screen now carry four rungs at K = 1, 3, 5, 10. They are § 7.

## 7. The fourteen ladders Phase 2 bought

**What was purchased.** The PI approved tiers A–D of
`reports/k-ladder-phase2-costing-2026-09-12.md` on 2026-09-12 at US$24.84: one
pass of the carried Gemini 3 verifier over each of 28 first-N consensus unions,
which is the K = 1 and K = 3 rung of thirteen `pv-diag-384` families and of the
3.7 gold-standard text screen. It ran for **US$24.8065** audited flex —
35,844 candidates offered, 35,844 verified, **0 failed** — and every family
named in § 6.3 now carries **four rungs at K = 1, 3, 5, 10** on one frame
(`era2-b-487`), one reference (the Gold Standard curator reference), one
verifier (ruling R1), one evaluation recipe (14 buffers, 10,000 BCa draws,
seed 42, MCC) and one operating-point rule.

Full per-family tables, both operating points, cost per rung and every anchor
are in `phase2/ladder-tables.md`; the machine-readable form is
`phase2/ladders.json`, the spend in `phase2/spend-ledger.json`, and the run's
report is `reports/k-ladder-phase2-deltas-2026-09-12.md`. This section states
what the fourteen ladders mean.

### 7.1 The result: K's return is governed by the thinking level

Ruling R2's sweep-optimal point, board frame, K = 1 against the best rung, with
the board's own instrument (`scripts/era1_leaderboard_tiering.py`, round-robin
tile-swap permutation, 10,000 permutations, seed 42, BH q = 0.05,
`--permute-mcc`) run over the thirteen ladders whose rungs are all
register-resolvable:

| thinking | ladders | ΔF1 range, K = 1 → best | ΔF1 significant | ladders that are ONE tier |
|---|---:|---|---:|---:|
| MINIMAL | 6 | +0.0139 to +0.0629 | **2 of 6** | **4 of 6** |
| HIGH | 7 | +0.0559 to +0.1514 | **7 of 7** | 0 of 7 |

**With HIGH thinking, more proposer passes always pay; with MINIMAL thinking,
usually they do not.** Four ladders greedy-clique into a **single tier** — all
four rungs statistically indistinguishable, so K buys nothing detectable at
all — and every one of the four is MINIMAL: text T 0.3 (BH p = 0.28), text
T 0.7 (p = 0.58), image T 0.3 (p = 0.78), image T 1.0 (p = 0.12). The seven
HIGH-thinking ladders all separate, and the number of distinguishable tiers
rises with temperature on the text track (T 0.3 → 2 tiers, T 0.7 → 3,
T 1.0 → 3).

**Temperature modifies it within a thinking level, monotonically on both HIGH
tracks**: HIGH text +0.0559 → +0.0735 → +0.0994 and HIGH image
+0.0780 → +0.0959 → +0.1514 as T goes 0.3 → 0.7 → 1.0. On the MINIMAL tracks
the gain is smaller and not ordered by temperature.

**The reading, offered rather than asserted.** Extra passes can only help to the
extent that they differ from each other, and both HIGH thinking and higher
temperature make a pass more different from its siblings. That is the diversity
dividend (Obs 141) measured on a K ladder for the first time: K is not a
free-standing lever but a way of buying sampling diversity, and it pays in
proportion to how much diversity the configuration already generates. It also
explains a result the corpus already held without explaining — that the
registered `pass-budget-pareto-v2` efficient set contains both a cheap
MINIMAL rung and an expensive HIGH one.

### 7.2 Tile-MCC: the direction holds, and now has one significant case

§ 4.3 carries the table. Across the fourteen: F1 rises on all fourteen,
tile-MCC falls on eleven of the thirteen that have an interpretable one, and
for the first time in the corpus **one MCC decline is statistically
significant** — HIGH image T 1.0, −0.0637, BH p = 0.0420 — with
scale-4-optimal a near miss at −0.0572, BH p = 0.0762. Twelve of thirteen show
no significant MCC change, which is what § 4.1 found on the eight.

Note the shape of the exception: it is the family with the **largest** F1 gain
(+0.1514). The ladders where K buys the most localisation are the ladders where
it costs the most tile-level specificity, which is exactly the mechanism § 4
proposed — extra true positives land in tiles already counted positive, extra
false positives flip negative tiles.

### 7.3 One family's tile-MCC is withheld, and why

**The 3.7 gold-standard family's K = 1 and K = 3 rungs report no tile-MCC.**
This is an instrument property, found while checking the numbers, and it is
worth stating in full because it fails silently.

`scripts/lib_advanced_metrics.py:2079` decides whether a tile contains a
detection with a **string** comparison —
`gdf_det[gdf_det['source_tile'] == tile_name]` — not geometrically. So a
detection counts towards a tile only when its `source_tile` property is
byte-equal to a `tile_name` in the bounds file. Point matching is geometric, so
F1 at every buffer is unaffected.

The 3.7 screen's proposer ran on the `ov192` tile set, whose names
(`…_x0_y1920.png`) are **absent** from the board frame's 336-stride vocabulary
(`…_x0_y2016.png`). Measured with `scripts/check_tile_vocabulary_match.py`:
of the 47 materialised Phase 2 cells, **44 match the frame and exactly 3 do
not**, all three this family's new rungs — 21 of 502 detections land in a frame
tile, giving tp 10 / fn 219 and MCC 0.1337 beside an F1@20 of 0.8495. The
family's committed K = 5 and K = 10 rungs are sound (tp 185, MCC 0.7651)
because their unions carry frame-vocabulary names.

Two consequences, both conservative. The three cells' tile-MCC is **withheld
rather than printed**, because 0.13 beside a sibling's 0.77 invites reading an
instrument artefact as "K destroys tile discrimination". And this family is
**excluded from the permutation testing**: the instrument runs the F1 and MCC
arms on one set of swap masks, so tiering it would compare a meaningless MCC
against a sound one and manufacture a large spurious drop. **Its F1 ladder is
reported in full** and is unaffected.

No re-keying was attempted. Assigning these detections to frame tiles by
spatial containment would work and would reproduce what the family's committed
unions already do, but choosing which tile wins where tiles overlap is a
methodological decision for the PI, not for a gap-fill run. **The general
question is put back too**: any cell in the corpus scored on a frame whose tile
vocabulary differs from its proposer's tiling has this problem, and nothing in
the pipeline warns of it — the board's own confusion gate reproduces the same
wrong confusion and passes.

**Amended 2026-09-12 (later).** Both questions above are now answered by
measurement, and the withholding stands — but on a firmer footing and for a
sharper reason. `reports/tile-mcc-geometric-join-2026-09-12.md` is the full
account; three things belong here.

1. **The general question is closed for this corpus.** All **149** committed
   cells the Era-2 board reads — its own 103 plus this run's 46 — were
   re-scored under the legacy string join and both geometric joins
   (`scripts/audit_tile_join_variants.py`, on sapphire;
   `results/tile-join-audit/`). **146 reproduce their committed confusion and
   MCC exactly, and exactly these three are refused — no other cell in either
   corpus, the signed board included.** No published MCC outside these three
   was ever affected.
2. **It can no longer fail silently.** The join is now a named parameter at one
   place in the library, and the scorer refuses to emit an MCC when any point
   inside the frame's tile union was booked to no tile — 21 of 475 here. The
   board's confusion gate now checks the confusion against the frame's
   polygons rather than against a rebuild of itself, which is why it passed
   these cells before. A wider exposure also surfaced: the same string join
   booked TPs and FPs in the per-tile table the bootstrap CIs and permutation
   tests resample, so a mismatched cell lost **every** TP and FP there too —
   this family escaped that only because it was already excluded from the
   permutation testing.
3. **Repair is a larger decision than it looked, so it is still the PI's.**
   The premise that a geometric join reproduces the string join where the
   vocabulary matches is **false**: the 384 px frames overlap on a 336 px
   stride (the 487 tile areas sum to 1.2783x their union; a median 30.6 % of
   detections lie inside more than one tile), so a geometric join raises MCC
   on **146 of 146** sound cells, by +0.106 mean under `geometric-primary` and
   +0.075 under `geometric-contains`. These three cells would read **0.9535 /
   0.9059 / 0.9121** under the first rule and **0.9262 / 0.8761 / 0.8903**
   under the second. Restoring them at either value while their sound K = 5
   sibling stays at 0.7651 would invite the same misreading this section
   withheld them to avoid, with the arrow reversed — so a coherent restoration
   re-scores the family, which means re-scoring the board.

**Amended 2026-09-13.** The three refused rungs' proposer unions have since been
rebuilt: `scripts/merge_passes.py` had been silently skipping
`run_<N>_recovery` storm-recovery fragments, and the fix
(`75d7c8d4cd55b6ec8d2a40abff70a31f62b67725`) took `consensus-n3` from 757
candidates to 759 and left `consensus-n1` at 640. **No number in this section
moves**: the F1@20 of 0.8495 quoted above, its 502 detections, and the tp 10 /
fn 219 / MCC 0.1337 confusion all belong to the K = 1 opmax rung, whose scored
detection set is unchanged. The K = 3 rung — whose F1 this section does not
quote — moves 0.8870 → **0.8860**, one added false positive
(`results/k-ladder-2026-09-12/recovery-fix-2026-09-13/`;
`reports/recovery-drop-fix-2026-09-13.md`).

**What the rebuild revealed about this invariant is more consequential than the
−0.0010.** The refusal does not merely withhold a statistic — **it blocks
correction.** Because the F1 bootstrap resamples *tiles*, the refusal raises
inside `bootstrap_ci` and aborts the whole evaluation, so
`scripts/evaluate_detections.py` **cannot be run at all** on these three cells at
HEAD. Their committed evaluations predate the invariant (`7ba47b63b`) and can no
longer be reproduced, let alone refreshed. The consequence is concrete: the K = 3
rung's F1 has genuinely changed, and its `evaluation.json` — and therefore its
`results/conditions-manifest.json` row, still reading 0.8870 / 494 — cannot be
brought up to date until the tile-join question is ruled on. The open ruling of
point 3 above is now not only a reporting decision but a **prerequisite for
repairing any of these three cells**, which raises its priority.

### 7.4 Pareto: K = 10 is almost never worth it, and the 3.7 family shows why

Efficient rungs per family are tabulated in `phase2/ladder-tables.md`; the
figure is `figures/k-ladder-pareto-phase2.png`. Two things to read off them.

**K = 3 takes 37 % to 92 % of each ladder's total F1 gain for 31 % to 44 % of
its top rung's cost.** Every one of the fourteen has K = 3 on its efficient set.

**The last step is the worst buy on every ladder, and on the 3.7 family it is
the worst in the corpus.** Its K = 5 → K = 10 step buys **+0.0002 F1 for
US$8.65** — about **US$43,000 per 0.001 F1**, two and a half times the
US$17,400 that § 5 records for 55-map stride B, and the cleanest statement yet
that "the ladder saturates" is an economic claim rather than a statistical one.
For comparison the HIGH text T 1.0 ladder's last step buys +0.0116 for
US$12.94, or about US$1,100 per 0.001 F1.

### 7.5 What § 7 does not claim

- **No rung joined the Era-2 board when § 7 was written.** **Superseded
  2026-09-13**: the PI authorised the admission by route (a) and all 46 Phase 2
  rungs plus the 4 tier E rungs are now on the board — 103 → **153 cells
  admitted, 150 tiered, 3 withheld**, Tier 1 and its five members unchanged, the
  board awaiting the PI's re-signature
  (`results/leaderboard/era2/gs-era2-verified-board-2026-09-10/README.md`,
  2026-09-13 entry; `reports/k-ladder-admission-deltas-2026-09-13.md`).
- **No analysis row was authored or signed when § 7 was written.** The tiering
  read its cell sets from scratch analyses files, so the register gained no
  placeholder row. **Superseded**: the row `k-ladder-2026-09-12` was authored
  UNSIGNED on 2026-09-12 and is now complete and awaiting signature (§ 6.2).
- **The Hsu MCB admissible set is supplied as of 2026-09-13** — § 6.1's table,
  `mcb/summary.json`, on the PI's ruling to wait for the sets before signing.
- **The carried convention is settled (PI ruling, 2026-09-13).** The corpus holds
  two readings of "the carried point" and they diverge sharply above K = 3 —
  `k = K` taxes F1@20 by up to −0.2566 on the committed rungs while the
  gold-standard stride ladder's own 1/3/4/8 vote shell taxes at most −0.0735.
  **The stride ladder's own vote shell IS the carried point; `k = K` stays as a
  disclosed column.** Both readings remain computed and committed
  (`phase2/committed-carried/scores.json`), and they coincide at K ≤ 3, so **no
  number moved** — every ladder table's `carried F1@20` column is now the shell
  reading and `carried F1@20, k = K (disclosed)` sits beside it
  (`phase2/ladder-tables.md`, regenerated by
  `scripts/build_k_ladder_phase2_tables.py` v1.1.0, whose `carried_convention`
  block in `phase2/ladders.json` records the ruling). Only the committed K = 5
  and K = 10 rungs of the thirteen `pv-diag-384` families are affected, and for
  them the two columns swapped places rather than changing value.
- **Nothing in §§ 2–6 moved** when § 7 was written. Since then § 2.1 and § 6.1
  gained their MCB sets and § 6.2 records the row; no Phase 1 ladder gained a
  rung and no Phase 1 F1 or tile-MCC number changed.

## 8. Tension: MINIMAL ladders on the two corpora

**The tension, stated first.** §§ 3.1–3.2 report that the two deployment
MINIMAL stride ladders gain a lot from K and gain it decisively — stride B
+0.0547 F1@50 from K = 1 to K = 10 at BH p < 0.0001, stride A +0.0192 at
BH p < 0.0001. § 7.1 reports that on the gold standard the MINIMAL ladders gain
+0.0139 to +0.0629 and **four of six are a single statistical tier** in which K
buys nothing detectable. Two readings compete, and the corpus as it stood could
not choose between them:

- **the scale reading** — the effect is the same size on both corpora, and the
  gold standard has 17.5x fewer tiles, so its instrument cannot resolve it;
- **the corpus reading** — K really pays more at deployment, where the proposer
  meets 55 unseen sheets rather than the 4 its examples were drawn from, so
  extra passes have more left to find.

Three analyses settle the first and qualify it. All cost US$0 and ran on
sapphire; the machine-readable forms are `tension/subsample.json`,
`tension/effect-sizes.json` and `tension/grid-overlap.json`.

### 8.1 The subsample test: the gold standard's tile count, on the deployment cells

The comparison across corpora confounds tile count with everything else. This
one does not: it takes the **deployment ladders' own cells**, on their own
reference and their own buffer, and scores them on random **487-tile** subsets
of their own 8,541 tiles — the gold standard's exact tile count — 200 draws,
seed 42, with the ladder's own instrument (round-robin tile-swap permutation
over the four rungs, 10,000 permutations, BH q = 0.05 within each draw's six
pairs). Corpus, reference, recipe and cells are held fixed; **only the number of
tiles scored varies**.

**The gate first.** Each rung's per-tile table was rebuilt from its committed
detections and its micro-F1 compared with its committed board F1 before any
subset was drawn: all eight rungs reproduce to within 2.6e-5 (the committed
values are published at four decimals). The first run of this analysis
**failed** that gate at micro-F1 0.0000 on all eight rungs, which is the
signature § 7.3 describes — and the cause was the projection, not the tile
names: the committed cells' detections are EPSG:4326 while the reference and
frame are EPSG:32635, so a 50 m tolerance was being applied in degrees. The
names were never in question (`source_tile` matches the frame 2,579 of 2,579).
Recorded because the gate is the only reason the first numbers were not
published.

| ladder | full corpus (8,541 tiles) | draws BH-significant at 487 tiles | ΔF1 across draws: mean (sd) | p05 … p95 | draws with ΔF1 < 0 |
|---|---:|---:|---|---|---:|
| 55-map stride A, r2 | **+0.0192** (p < 0.0001) | **39 of 200 — 19.5 %** | +0.0191 (0.0113) | +0.0012 … +0.0377 | 8 |
| 55-map stride B, r2 | **+0.0547** (p < 0.0001) | **197 of 200 — 98.5 %** | +0.0537 (0.0116) | +0.0329 … +0.0723 | 0 |

**Read the two rows together and the mechanism is arithmetic.** The subsampling
standard deviation of ΔF1 is the same on both ladders, ≈ 0.0114, because it is a
property of scoring 487 tiles rather than of the ladder. An effect of +0.019
therefore sits about 1.7 standard deviations from zero and is detected in fewer
than one draw in five; an effect of +0.055 sits about 4.7 out and is detected in
almost every draw. **At 487 tiles this instrument resolves a ΔF1 of roughly
0.03 and above, and does not resolve one below it** — and that is measured on
cells whose full-corpus p-value is below the permutation floor.

### 8.2 The effect sizes, both corpora side by side

Every MINIMAL-thinking K ladder in the corpus, K = 1 to its best rung, ordered
by effect size rather than by corpus. Figures are re-read from the committed
ladder inventories and permutation summaries, not recomputed.

| ladder | corpus | tiles | K = 1 → best | ΔF1 | BH p | separates? |
|---|---|---:|---|---:|---:|:---:|
| MINIMAL image T 0.7 | gold standard | 487 | 1 → 10 | **+0.0629** | 0.0006 | **yes** |
| stride B | deployment | 8,541 | 1 → 10 | **+0.0547** | < 0.0001 | **yes** |
| MINIMAL text T 1.0 | gold standard | 487 | 1 → 10 | **+0.0546** | 0.0012 | **yes** |
| MINIMAL image T 1.0 | gold standard | 487 | 1 → 10 | +0.0384 | 0.1236 | no |
| GS stride A (exact) | gold standard | 487 | 1 → 10 | **+0.0305** | 0.0072 | **yes** |
| MINIMAL text T 0.3 | gold standard | 487 | 1 → 5 | +0.0223 | 0.2768 | no |
| stride A | deployment | 8,541 | 1 → 10 | **+0.0192** | < 0.0001 | **yes** |
| MINIMAL text T 0.7 | gold standard | 487 | 1 → 5 | +0.0164 | 0.5780 | no |
| MINIMAL image T 0.3 | gold standard | 487 | 1 → 10 | +0.0139 | 0.7803 | no |

**Two things this table makes plain.**

1. **The gold-standard ladders sort by effect size, not by anything else.**
   Every one at or above +0.0546 separates; every one at or below +0.0223 does
   not; the two in between straddle the resolution § 8.1 measured, and they
   straddle it in both directions (+0.0384 does not separate, +0.0305 does),
   which is what a resolution limit rather than a threshold looks like.
2. **The two corpora's MINIMAL ranges are not different — the deployment range
   sits INSIDE the gold standard's.** Gold standard +0.0139 to +0.0629;
   deployment +0.0192 to +0.0547. There is no effect at deployment larger than
   the largest on the gold standard.

### 8.3 Does K's return depend on the geometry? The grid ladders say yes — before the verifier

The grid study holds K = 1/3/5/10 ladders at four (tile size x overlap)
geometries at **fixed MINIMAL text T 0.7 on one corpus**, which isolates
geometry from everything the two-corpora comparison confounds. They are
**consensus-only** — no verifier stage — and each rung is the best F1@20 over
the (corroboration, vote) grid, which is how `results/grid-2026-08-18/findings.md`
reads that sweep. On the grid-common 487-tile footprint:

| geometry | K = 1 | K = 3 | K = 5 | K = 10 | ΔF1, K = 1 → 10 | ΔMCC |
|---|---:|---:|---:|---:|---:|---:|
| 384 px / 50 % | 0.6633 | 0.6837 | 0.7045 | 0.7205 | **+0.0572** | +0.0444 |
| 512 px / 50 % | 0.7121 | 0.7429 | 0.7440 | 0.7518 | **+0.0396** | +0.0382 |
| 384 px / 12.5 % | 0.5021 | 0.5976 | 0.6176 | 0.6475 | **+0.1454** | +0.1543 |
| 512 px / 12.5 % | 0.5845 | 0.6763 | 0.6736 | 0.6759 | **+0.0914** | +0.0597 |

**Overlap governs K's consensus-only return, and by a factor of about 2.4.**
At both tile sizes the low-overlap cell gains far more from K than the
high-overlap one (+0.1454 against +0.0572 at 384 px; +0.0914 against +0.0396 at
512 px). The reading offered: **overlap and pass count buy the same thing.** A
50 % overlap already shows each mound to the proposer in several tiles within a
single pass, so extra passes add less that the geometry has not already
supplied; at 12.5 % overlap a mound is seen once, and extra passes are the only
redundancy available. This is the same substitution the grid's own registered
analysis found between consensus and the verifier
(`grid-postverifier-2026-08-18`: "consensus and verifier are complements, not
substitutes"), now between consensus and *overlap*.

**But the pattern does not survive to the verified deployment ladders, and that
is worth stating rather than smoothing.** Stride A runs a 128 px overlap of 384
(33 %) and stride B a 192 px overlap (50 %), so the grid's rule predicts stride
A should gain MORE from K. It gains **less** (+0.0192 against +0.0547). The
difference between the two settings is the verifier, which the grid ladders
above do not have — and § 8.4 is the measurement that isolates it.

Note also the ΔMCC column: on these consensus-only ladders tile-MCC **rises**
with K at every geometry, by +0.038 to +0.154. That is the opposite of §§ 4
and 4.3, where tile-MCC falls on 16 of 21 verified ladders. The two are
consistent under § 4's mechanism: a consensus-only union at a tuned vote
threshold is precision-starved, so extra passes still add true positives in
tiles that were negative, which raises MCC; once a verifier has already removed
most false positives, extra passes mostly add false positives, which lowers it.
**Tile-MCC's response to K reverses across the verifier stage.**

### 8.4 The verified B-geometry ladder tier E bought

**What it is, and why it is the term the tension was missing.** The grid study's
384 px / 50 % overlap pool is the **B geometry** — the same tiling the deployment
stride-B ladder runs on — at gold-standard scale, and it already held a verified
K = 10 cell (the committed `grid-postverifier-2026-08-18` 384/50 cell). Tier E
bought its K = 1, K = 3 and K = 5 siblings for **US$4.9595** audited flex (7,239
of 7,239 candidates verified, 0 failed), so the corpus now has a **verified
MINIMAL-text ladder on the deployment geometry**, which is what no gold-standard
MINIMAL ladder previously supplied.

All four rungs on the board frame `era2-b-487`, curator reference, 14 buffers,
10,000 BCa draws, seed 42, MCC; sweep-optimal basis per ruling R2. Machine-
readable form: `tier-e/ladder.json`, `tier-e/scores.json`, spend in
`tier-e/spend-ledger.json`.

| K | candidates | opmax (k, p) | n | F1@20 | tile-MCC | verifier leg, audited flex |
|---:|---:|---|---:|---:|---:|---:|
| 1 | 1,826 | (1, 0.20) | 482 | 0.8546 | **0.8211** | **$1.2531** |
| 3 | 2,481 | (3, 0.15) | 450 | 0.8840 | 0.8167 | **$1.6989** |
| 5 | 2,932 | (5, 0.15) | 435 | **0.8905** | 0.8139 | **$2.0074** |
| 10 | 3,319 | (10, 0.15) | 400 | 0.8886 | **0.7903** | ≈ $2.28 † |

† The K = 10 rung's verifier leg is not separately audited: it is part of the
committed grid verifier run's US$6.2714 flex over 9,133 candidates across four
geometries, so US$2.28 is that figure pro-rated by its 3,319 candidates. The
proposer leg is US$0.8377 flex per pass on this pool
(`outputs/grid-2026-08-18/g384_ov192/run_1/…meta.json`, `cost_estimate`
US$1.675407 at list, halved), so the all-in flex figures are about $2.09, $4.21,
$6.20 and $10.66.

**The statistical result**, board instrument verbatim
(`scripts/era1_leaderboard_tiering.py --permute-mcc`, 487 tiles, 10,000
permutations, seed 42, BH q = 0.05 within the ladder's own six pairs; every
rung's rebuilt micro-F1 reproduced its committed evaluation at gap ±0.0000
before any p-value was read):

| pair | ΔF1@20 | BH p | ΔMCC | BH p |
|---|---:|---:|---:|---:|
| K = 1 → 3 | **+0.0294** | **0.0039** | −0.0044 | 1.0000 |
| K = 1 → 5 | **+0.0359** | **0.0006** | −0.0072 | 1.0000 |
| K = 1 → 10 | **+0.0340** | **0.0046** | −0.0308 | 0.3960 |
| K = 3 → 5 | +0.0065 | 0.5772 | −0.0028 | 1.0000 |
| K = 3 → 10 | +0.0046 | 0.7248 | −0.0264 | 0.3960 |
| K = 5 → 10 | −0.0019 | 0.8288 | −0.0236 | 0.3960 |

**Two tiers: Tier 1 = {K = 3, K = 5, K = 10}, Tier 2 = {K = 1}.** F1 separates on
3 of 6 pairs — every pair involving K = 1 and no other — and **tile-MCC separates
on none**, while falling **monotonically across all four rungs**: 0.8211 →
0.8167 → 0.8139 → 0.7903. The best rung is K = 5, and K = 10 is *below* it by
0.0019.

**Three things to read off it.**

1. **It is the corpus's pattern again, on a fifth gold-standard MINIMAL family
   and the first on the deployment geometry.** F1 rises significantly from
   K = 1 and saturates immediately after; tile-MCC falls at every step and never
   significantly. § 4's mechanism predicts exactly this, and the monotone MCC
   decline across four rungs is the cleanest instance of it in the corpus —
   every one of the three MCC steps is negative.
2. **The verifier absorbs about 40 % of K's F1 return and reverses tile-MCC's
   response to it.** § 8.3's consensus-only ladder on this same pool and
   geometry gains **+0.0572** F1 from K = 1 to K = 10 with tile-MCC **rising**
   +0.0444; verified, the same pool gains **+0.0340** with tile-MCC **falling**
   −0.0308. So the verifier takes roughly two-fifths of what extra passes buy on
   F1 — because it was already removing much of what extra passes remove — and
   turns a tile-level *gain* into a tile-level *loss*, a swing of 0.075 MCC.
   This is the measurement § 8.3 asked for, and it is consistent with the grid
   study's own registered finding that consensus and the verifier are partial
   substitutes.
3. **It refines § 8.1's resolution estimate rather than confirming it exactly.**
   This ladder resolves **+0.0294** at BH p = 0.0039, below the ≈ 0.03 § 8.1
   measured, while MINIMAL image T 1.0 does not resolve **+0.0384**. So the
   487-tile limit is a band, not a threshold, and it varies between ladders with
   their variance — which is what § 8.5 says and why it is stated as a
   resolution rather than a cut-off.

**One caveat the reader must carry, and it is not in the numbers above.** The
K = 10 rung's candidate universe was assembled by a different rule from the
other three: the committed union (3,319) is filtered to the grid study's common
487-tile carrier footprint by `scripts/materialise_grid_unions.py`, while tier
E's rungs are `merge_passes` unions on the pool's native footprint (a
`merge_passes` K = 10 union holds 3,591, of which 3,325 survive that filter).
Scoring every rung on the board frame excludes the out-of-frame candidates
either way, so the F1 and MCC comparisons above are like for like; what differs
is the universe each verifier pass priced. `reports/k-ladder-closeout-deltas-2026-09-12.md`
§ 2.2 measures it and puts it to the PI.

**And one instrument note, because it nearly cost the ladder its MCC column.**
The tile-join invariant refused all six tier E cells on the first scoring
attempt: the grid pool's proposer ran on the 192 px stride `ov192` tiling, and
only **12 of 308** of its distinct tile names appear in the board frame's 336 px
stride vocabulary — the same defect § 7.3 describes for the 3.7 family. Unlike
that family, this one has a settled remedy already in use on it: the committed
K = 10 rung is re-keyed to the carrier grid before scoring, so tier E's cells are
re-keyed the same way and all four rungs are joined identically. The MCC column
above is therefore sound, and the invariant is why we know that rather than
hoping it.

### 8.5 Which reading the data favour

**The scale reading, for the tension as posed — with the geometry qualification
of § 8.3 standing beside it, and without claiming the corpora are identical.**

What is established:

1. **The gold standard's null results are a resolution limit, not a finding
   about K.** § 8.1 shows that the deployment stride A gain — below the
   permutation floor on 8,541 tiles — goes undetected in 80.5 % of 487-tile
   draws of its own cells. A gold-standard ladder reporting "one tier" at
   ΔF1 +0.0139 to +0.0384 is reporting that 487 tiles cannot see an effect that
   size, which is the same statement.
2. **There is no evidence that K pays more at deployment.** § 8.2's deployment
   range sits inside the gold-standard range, and the two gold-standard MINIMAL
   ladders whose effects are deployment-sized (+0.0546, +0.0629) both separate.
   The corpus reading predicts a shift the data do not show.
3. **"K buys nothing detectable on four MINIMAL configurations" stands as
   written** — it is a claim about detectability at 487 tiles, and § 8.1 is its
   warrant rather than its refutation. What must not be said is that K buys
   nothing *on those configurations*: four effects between +0.0139 and +0.0384
   are consistent both with nothing and with the +0.019 the deployment corpus
   resolves.

What is **not** established, stated so the reading is not over-claimed:

- **Two deployment ladders against seven gold-standard ones.** § 8.1's
  resolution estimate rests on two ladders, and both are stride geometries under
  the Gemini 3 verifier. A third would test it.
- **§ 8.1 measures the instrument on the deployment cells, not on the gold
  standard's.** The deployment ladders are scored against the r2 reference at
  50 m, the gold standard against the curator reference at 20 m. The ≈ 0.0114
  subsampling standard deviation is therefore a deployment-cell figure imported
  to the gold standard's tile count, not a gold-standard measurement. It is the
  closest available like-for-like, and it is not identical.
- **A resolution limit is not a power calculation.** 19.5 % and 98.5 % are
  detection rates at two effect sizes, not a curve; nothing here says what
  ΔF1 the gold standard detects half the time.
- **§ 8.3's geometry effect is consensus-only and unverified as a claim about
  the verified ladders.** It is measured at one thinking level, one temperature,
  one corpus and one modality, and the verified ladders order the other way.

### 8.6 CLAIM — the verifier absorbs about 40 % of K's F1 return and reverses the sign of its tile-MCC effect

Stated as a claim of its own on the PI's ruling of 2026-09-13, because § 8.3 and
§ 8.4 each measure one half of it and neither is the comparison. The four
numbers were re-read at source before this section was written, and the anchors
are given so the next reader need not trust the prose.

**The claim.** On the same candidate pool and the same B geometry (384 px tiles,
50 % overlap), going from K = 1 to K = 10 proposer passes:

| stage | ΔF1@20, K = 1 → 10 | Δtile-MCC, K = 1 → 10 |
|---|---:|---:|
| **consensus only** (no verifier) | **+0.0572** | **+0.0444** |
| **verified** (Gemini 3 verifier) | **+0.0340** | **−0.0308** |

The verifier therefore **absorbs 40.6 % of K's F1 return** (1 − 0.0340 / 0.0572)
and **reverses the sign of K's tile-MCC effect**, a swing of **0.0752** MCC.

**Anchors, one per number.**

- Consensus-only — `results/grid-2026-08-18/sweep.csv`, cell `g384_ov192`, best
  F1@20 over the (corroboration, vote) grid per K, which is the rule
  `results/grid-2026-08-18/findings.md` reads that sweep by: **K = 1** F1
  **0.6633**, tile-MCC **0.4465** at (c ≥ 3, k ≥ 1); **K = 10** F1 **0.7205**,
  tile-MCC **0.4909** at (c ≥ 2, k ≥ 10). These are the 384 px / 50 % row of
  § 8.3's table.
- Verified — `results/k-ladder-2026-09-12/tier-e/ladder.json` (`rungs`) and each
  rung's own committed evaluation: **K = 1**
  `results/k-ladder-2026-09-12/tier-e/cells/grid-2026-08-18__g384-ov192-k1-verified-opmax/evaluation.json`,
  F1@20 **0.8546**, `summary.tile_classification.mcc.point` **0.8211**, 482
  detections; **K = 10**
  `results/k-ladder-2026-09-12/tier-e/cells/grid-2026-08-18__g384-ov192-k10-verified-p0_15-k10-boardframe/evaluation.json`,
  F1@20 **0.8886**, `summary.tile_classification.mcc.point` **0.7903**, 400
  detections. These are the first and last rows of § 8.4's table.

**The mechanism, in two sentences.** A consensus-only union at a tuned vote
threshold is precision-starved, so an extra pass mostly adds true positives in
tiles that were predicted negative, which raises F1 and tile-MCC together. Once
a verifier has already removed most of the false positives that extra passes
would have removed, the same extra pass buys less F1, and what it now adds is
disproportionately false positives in tiles that were correctly negative — so
tile-MCC falls while F1 still rises.

**What it is evidence for, and its limits.** This is the corpus's cleanest
evidence that **tile-MCC's response to K is a property of the pipeline stage
rather than of K** — compare § 4 and § 4.3, where tile-MCC falls on 16 of 21
verified ladders, against § 8.3's four consensus-only ladders, where it rises at
every geometry. It is also the first measurement on a K ladder of the partial
substitution the grid study's registered `grid-postverifier-2026-08-18` analysis
found between consensus and the verifier. The limits: one geometry, one thinking
level, one temperature, one modality, one corpus; and the ΔMCC values are **not**
statistically separated (§ 8.4 — tile-MCC separates on none of the ladder's six
pairs), so the claim is about the sign and the size of the shift **between
stages**, not about either ladder's own MCC trend being significant. § 8.4's
caveat about the K = 10 rung's construction applies to the verified row.

## Changelog

### 2026-09-13 (latest) — § 7.3 amended: the refused rungs' unions rebuilt, no number here moves, and the refusal is now shown to block correction

**Trigger**: the PI's "fix properly" ruling of 2026-09-13 on
`reports/recovery-fragment-drop-2026-09-13.md`. `scripts/merge_passes.py` had
been deriving a pass number by casting the text after `run_`, so
`int("2_recovery")` raised and the `except ValueError: continue` silently dropped
every storm-recovery fragment. The fix
(`75d7c8d4cd55b6ec8d2a40abff70a31f62b67725`) folds each fragment into its parent
pass. Five committed consensus unions were rebuilt, four registered conditions
read them, and three of those four are this run's own Phase 2 rungs.

**Nothing in §§ 2–8 changed.** The claims that were at risk and were checked:

| claim | before | after |
|---|---|---|
| § 7.3 F1@20 of the refused K = 1 rung | 0.8495 | 0.8495 — **unchanged** |
| § 7.3 detections / confusion of that rung | 502 / tp 10, fn 219, MCC 0.1337 | **unchanged** |
| § 4.3 "3.7 text, GS B geometry" ladder | 0.8495 → 0.9068 (+0.0573) | **unchanged** (both ends are K = 1 and K = 10) |
| § 8.4 tier-E ladder K = 5 row | 2,932 / (5, 0.15) / 435 / 0.8905 / 0.8139 | **unchanged, dict-identically** |
| § 7.1 table, §§ 7.2, 7.4, 7.5 | — | **unchanged**; § 7.1's table is aggregated by thinking level and has no per-rung row |
| the K = 3 GS text rung's F1@20 | 0.8870 | **0.8860** — and this document never quotes it |

The K = 3 movement is one added false positive: `candidate_00049`, promoted from
2 votes to 3 by a recovery fragment, clearing the rung's vote ≥ 3 gate at
probability 1.0, so detections go 494 → 495 and precision falls 0.8340 → 0.8323
while recall holds at 0.9471 exactly. No operating point migrated on any of the
four cells — 0 ties, and the board and Era-2 frames still agree. The tier-E K = 5
cell's re-evaluation is **dict-identical** to what is committed, because the
candidate the fix promoted to 5 votes carries probability 0.10 against that
rung's prob ≥ 0.15 gate.

**A methodological finding the amendment records, and the reason for this
entry.** The tile-join refusal is worse than a withheld statistic: because the F1
bootstrap resamples *tiles*, the refusal raises inside `bootstrap_ci` and aborts
the entire evaluation, so `scripts/evaluate_detections.py` **cannot be run on
these three cells at HEAD at all**. Their committed evaluations predate the
invariant (`7ba47b63b`) and are no longer reproducible. So the K = 3 rung's F1 has
genuinely moved while its `evaluation.json` — and its
`results/conditions-manifest.json` row, still 0.8870 / 494 — **cannot be
refreshed**. The open ruling in § 7.3 point 3 is therefore a prerequisite for
repairing these cells, not only for reporting them, which raises its priority.
The three cells were re-scored on the F1 arm of their recorded recipe, with the
confidence intervals and per-tile block named WITHHELD rather than omitted; every
"before" was re-derived in the same process as its "after" and reproduces the
committed value exactly, so a difference is a difference in detections and not in
the scorer.

**Cost**: 4 verifier calls, **US$0.002784** audited on the corpus flex basis —
exactly what the PI approved and nothing more.

**Landed in** the branch `worktree-agent-a41b647e2345bdb44`; the rebuild at
`e9d1db0d0`, the extended verifier stages at `f8e0eb600`, the re-scores at
`20c0a053f`, the board note at `6291e9938`.

**What did NOT change**: every F1, precision, recall, tile-MCC and cost figure in
this document; every permutation result, BH p-value and MCB admissible set; the
22 tiered ladders and the withheld twenty-third; the Era-2 board's ranks, tiers,
MCB set and every signature field (the PI ruled the next rebuild picks these cells
up, so the board carries a note only); the uplift supplement, whose board-frame
exclusion keys on `scope_override.test_set_id`; and the signed
`k-ladder-2026-09-12` register row, whose `outcome` prose an agent must not amend.

### 2026-09-13 (earlier) — § 6.1 gains the per-family Hsu MCB admissible sets; the carried convention settled; the row ready for signature

**Trigger**: the PI's two rulings of 2026-09-13 (afternoon) — (1) "wait for the
sets", i.e. supply the per-family Hsu multiple-comparisons-with-the-best
admissible sets before the review's analysis row is signed, and (2) the carried
convention: the stride ladder's own vote shell is *the* carried point and
`k = K` stays as a disclosed column. Both executed at US$0 with zero API calls,
all compute on sapphire in an isolated worktree. Closing report:
`reports/k-ladder-mcb-deltas-2026-09-13.md`.

**Ruling 1 — the MCB sets.** § 6.1 gains a new subsection with a 22-row table
(ladder, rungs, F1-admissible set, tile-MCC-admissible set, `w_upper`) and the
five readings, generated by `scripts/k_ladder_mcb.py` from the Era-2 board's own
MCB step (`scripts/selection_aware_intervals.py --board`; 10,000 tile bootstrap
resamples, seed 42, m-out-of-n 1.0, simultaneous 95 %), each ladder on its own
frame, reference and headline buffer. § 2.1's "still not supplied" is replaced by
the gold-standard ladder's own two sets; § 6.2 records that the row is ready for
signature; § 7.5's MCB bullet is replaced.

| claim | before | after |
|---|---|---|
| Hsu MCB admissible sets | **not supplied** (§ 2.1, § 6.1, § 6.2, § 7.5) | **supplied for all 22 tiered ladders**, on F1 and tile-MCC |
| MCB runs, and their gate | — | **44 runs, 170 candidate rows gated, all passed**, max abs delta 4.958e-05 |
| ladders whose F1 set contains K = 3 | — | **12 of 22** (the cheapest admissible rung on 10) |
| ladders whose F1 set excludes K = 10 | — | **0 of the 20 that have a K = 10 rung** |
| ladders whose F1 set contains K = 1 | — | **2 of 22** |
| ladders whose tile-MCC set contains K = 1 | — | **22 of 22** |
| ladders admissible WHOLE on F1 / on tile-MCC | — | **2 of 22 / 12 of 22** |
| ladders with no admissible set | — | **1** (the 3.7 GS text screen; 3 rungs withheld) |

**Ruling 2 — the carried convention.** `scripts/build_k_ladder_phase2_tables.py`
goes to v1.1.0: the tables' `carried F1@20` column is now the **stride-shell**
reading and `carried F1@20, k = K (disclosed)` sits beside it, the compatibility
inventory's carried basis reads the shell reading, and `phase2/ladders.json`
carries a `carried_convention` block recording the ruling. **No number was
recomputed** — the two columns swapped places on the committed K = 5 and K = 10
rungs of the thirteen `pv-diag-384` families and coincide at K ≤ 3 — and both
readings stay committed in `phase2/committed-carried/scores.json`.

**One thing the ruling surfaced that nothing had recorded.** Read back against
§ 3's committed cells, the two 55-map stride ladders were built on **different
readings** of "carried": stride A's cells are the stride shell (k = 3 / 4 / 8)
while stride B's, stride B's 3.7-verifier cell and both 3.7 arms' are `k = K`
(anchor: each cell's `vote_threshold` in `results/run-conditions.json`). § 3 now
carries a disclosure table saying so, and says plainly that §§ 3.2–3.4's transfer
taxes are therefore `k = K` taxes and should be read as an **upper bound** on the
transfer cost. No § 3 number changed, because no shell-reading carried cell
exists for those ladders and building one is a rescore the PI has not asked for.

**A second, methodological finding, flagged rather than smoothed over.** The
admissible set and the committed greedy-clique tie set disagree in **both**
directions — the F1 set is smaller than the tie set on two ladders and larger on
six — which is what erratum E83 and defect D20 warn of. The sharp case: of the
four MINIMAL ladders § 7.1 reports as a **single tier** where "K buys nothing
detectable at all", only **two** are admissible whole under MCB; MINIMAL text
T 0.3 and MINIMAL image T 1.0 both rule K = 1 out as best. § 7.1 is not withdrawn
— a within-ladder pairwise BH family and a simultaneous comparison against the
best answer different questions — but § 6.1 now records that "one tier" must not
be read as "every rung could be the best one".

**Landed in** `b7e2821ba` (driver and tests in `ab778ad10`, `ef5cc813b` and
`cebae7868`).

**What did NOT change**: every F1 and tile-MCC point estimate in §§ 2–8; every
cost figure (this job spent **US$0**); § 4.1's and § 4.2's permutation results
and their BH p-values; the tiering, tiers and tie sets of all 22 committed
ladders; § 8 in its entirety including § 8.6; the Era-2 board (not re-tiered, not
re-signed, not re-scored); the 55-map final board; and every signature field —
the row's `manually_verified_at` is still `null`, because only the PI signs it.

### 2026-09-13 — § 8.6 added (the verifier-stage reversal, as a claim); § 3.3's K = 5 row filled

**Trigger**: the PI's rulings of 2026-09-13 (morning), items 3 and 4 of the
close-out list in `reports/k-ladder-closeout-deltas-2026-09-12.md` § 10.

**§ 8.6 — new.** The verifier-stage reversal was previously a paragraph inside
§ 8.4's reading, resting on numbers stated in § 8.3's table. The PI ruled it
should stand as a claim of its own with an anchor per number. All four were
re-read at source before the section was written; none moved:

| number | value | source re-read |
|---|---:|---|
| consensus-only ΔF1, K = 1 → 10 | +0.0572 | `results/grid-2026-08-18/sweep.csv`, cell `g384_ov192` (0.6633 → 0.7205) |
| consensus-only Δtile-MCC | +0.0444 | the same rows (0.4465 → 0.4909) |
| verified ΔF1, K = 1 → 10 | +0.0340 | `tier-e/ladder.json` + the two rung evaluations (0.8546 → 0.8886) |
| verified Δtile-MCC | −0.0308 | the same two evaluations, `summary.tile_classification.mcc.point` (0.8211 → 0.7903) |

Derived and stated for the first time: the verifier absorbs **40.6 %** of K's
F1 return (1 − 0.0340 / 0.0572) and the tile-MCC swing between stages is
**0.0752**. Cross-referenced to § 4 and § 4.3, whose 16-of-21 falling tile-MCC
this explains as a stage property rather than a K property.

**§ 3.3 — the K = 5 row.** Filled from the completed stride-B-under-3.7 sweep
(PI ruling item 3). The R1-non-compliant flag on the whole sub-table and the
"not supplied" verifier cost cell are kept, and the 55-map final board
(`55map-final-board-r2-2026-09-06`) was NOT re-tiered.

**What did NOT change**: every other number in the document; § 8.3's and § 8.4's
tables, which § 8.6 only re-reads; the tiering of any board; the analysis row's
signature status (still UNSIGNED, so its `outcome` was extended with the § 8.6
claim rather than left for the PI).

### 2026-09-12 — § 8: the tension measured, and tier E's ladder

**Trigger**: the PI's closeout brief. § 7.1 and §§ 3.1–3.2 disagreed about what
K buys on a MINIMAL configuration, and the document recorded the disagreement
without resolving it; the brief asked for the three analyses that could.

**What was added.** § 8, in five subsections: the subsample test (§ 8.1), the
effect-size table across both corpora (§ 8.2), the grid overlap comparison
(§ 8.3), the verified B-geometry ladder tier E bought (§ 8.4), and the verdict
with its limits (§ 8.5). Artefacts:
`results/k-ladder-2026-09-12/tension/{subsample,effect-sizes,grid-overlap}.json`
and `results/k-ladder-2026-09-12/tier-e/`.

**The document's ladder count moves 22 → 23**, and its scope note's "eight
fixed-parameter ladders … all eight are tabulated here" now describes § 2–§ 3
only.

| claim | before | after |
|---|---|---|
| Why four MINIMAL ladders are one tier | unexplained; two readings offered | **a resolution limit, measured**: the deployment ladders' own cells lose BH significance in 80.5 % of 487-tile draws at ΔF1 +0.0192 and keep it in 98.5 % at +0.0547 |
| Whether K pays more at deployment | open | **no evidence that it does** — the deployment range +0.0192…+0.0547 sits inside the gold-standard range +0.0139…+0.0629 |
| Whether K's return depends on geometry | not asked | **yes, consensus-only**: ≈ 2.4x larger at 12.5 % overlap than at 50 %, at fixed MINIMAL text T 0.7 |
| tile-MCC's response to K | falls on the verified ladders | **reverses across the verifier stage** — it RISES with K on all four consensus-only grid cells (+0.038…+0.154) and falls once a verifier is in front of it |
| Verified MINIMAL ladders on the B geometry | none | **one**, four rungs: F1 0.8546 → 0.8840 → 0.8905 → 0.8886, tile-MCC falling monotonically 0.8211 → 0.7903 |

**What did NOT change.** No figure in §§ 1–7 moved. No committed evaluation was
rewritten. The three withheld tile-MCC cells of § 7.3 are still withheld, and
`TILE_JOIN_DEFAULT` is still `id`. The Hsu MCB admissible sets are still not
supplied (§ 6.1).

**One instrument event worth recording.** Two gates refused a number before it
was published: the per-tile rebuild gate caught that the committed 55-map cells'
detections are EPSG:4326 against an EPSG:32635 reference and frame (§ 8.1), and
the tile-join invariant refused all six tier E cells over a 192 px-against-336 px
stride vocabulary mismatch (§ 8.4). Both were repaired and both are recorded.

Landed on branch `worktree-agent-ae1e65fd9508397ec`. Closing report:
`reports/k-ladder-closeout-deltas-2026-09-12.md`.

### 2026-09-12 (later still) — § 7.3: the withheld tile-MCC, measured

**Trigger**: the PI's 2026-09-12 ruling on
`reports/k-ladder-phase2-deltas-2026-09-12.md` § 6.3 — make the tile assignment
geometric, re-score the withheld cells, and generalise so the error cannot
recur. Full account: `reports/tile-mcc-geometric-join-2026-09-12.md`.

**What moved**: § 7.3 gains an amendment. No table, figure or number elsewhere
in this document changed.

| Claim | before | after |
|---|---|---|
| Cells in the corpus with a vocabulary mismatch | unknown, "put back to the PI" | **3 of 149** committed cells the board reads; 146 reproduce exactly |
| Published MCCs affected outside these three | unknown | **none** — 0 of the signed board's 103 cells |
| The three cells' tile-MCC | withheld (raw 0.1337 / 0.1337) | **still withheld**; raw third value recorded as 0.1422; geometric candidates 0.9535 / 0.9059 / 0.9121 (`geometric-primary`) or 0.9262 / 0.8761 / 0.8903 (`geometric-contains`) |
| Whether a geometric join reproduces the string join on matched cells | assumed yes | **no** — higher on 146 of 146, +0.106 mean; the frames overlap |
| Exposure of the defect | tile-MCC | tile-MCC **and** the per-tile TP/FP/FN table the bootstrap CIs and permutation tests resample |

**What did NOT change**: §§ 2–7.2 and 7.4–7.5 in full; every F1 in the
document (F1 is geometric and never consulted a tile name); the exclusion of the
3.7 family from the permutation testing; the withholding itself.

Landed on branch `worktree-agent-a5339796998dcf596`.

### 2026-09-12 (later) — § 7: the fourteen ladders Phase 2 bought

**Trigger**: the PI approved tiers A–D of the Phase 2 costing at US$24.84 and
the run executed all 28 rungs for US$24.8065 audited flex. Closing report:
`reports/k-ladder-phase2-deltas-2026-09-12.md`.

**What moved**: the document's scope, from eight ladders to twenty-two. § 7 is
new; § 4.3 extends § 4's F1-against-MCC table by fourteen rows; § 5 points at
the new Pareto table and figure; § 1 gains a paragraph; § 6.3's gap is closed.

| Claim | before | after |
|---|---|---|
| Fixed-parameter ladders reported | 8 | **22** |
| Gemini 3 `pv-diag-384` ladders | none reach the three-rung bar (§ 6.3) | **13 four-rung ladders** |
| Significant tile-MCC declines in the corpus | 0 (§ 4.1, over 8 ladders) | **1** (HIGH image T 1.0, BH p = 0.0420) |
| Ladders where K buys nothing detectable | not measurable — no family had enough rungs | **4 of 13**, all MINIMAL thinking |
| Worst last-step buy on record | US$17,400 per 0.001 F1 (55-map stride B, § 5) | **US$43,000** per 0.001 F1 (3.7 GS, K = 5 → 10) |

**What did NOT change**: every number in §§ 2, 3, 4, 4.1, 4.2 and 5's Phase 1
table; the eight Phase 1 ladders' membership and rungs; the signed Era-2 board;
every analysis row; the pending instrument ruling for the 55-map ladders; and
the § 6.1 MCB gap, which is still outstanding. The § 4 tile-MCC direction is
corroborated, not revised.

Landed on branch `worktree-agent-ae87367bcee3e0e5c`.

### 2026-09-12 — §§ 4.1–4.2: the tile-MCC direction, tested

**Refresh trigger**: the PI's ruling that § 4's metric-divergence finding be
TESTED rather than described. Both ladder instruments were extended to carry
tile-MCC through the same permutation machinery as F1 (same seed, same
permutation count, byte-identical swap masks) and run on sapphire at US$0, zero
API calls.

**Gate, before any MCC number was read**: all 25 gated pairs reproduced the
committed board `pairwise` F1 permutation — `f1_a`, `f1_b`, `observed_diff` to
6 dp and raw `p_value` to 4 dp — against
`results/55map-final-board-r2-2026-09-06/final_board_50m.json` and
`results/55map-final-board-2026-08-27/final_board_50m.json`. The gold-standard
ladder's four pairs have no committed pairwise table, so their gate was the
harness's own micro-F1 and tile-confusion reproduction (exact on all four cells).

**What moved** — claims about the § 4 direction, not the numbers themselves (no
committed metric changed):

| claim | before | after |
|---|---|---|
| § 1, gold-standard MCC | "rises materially on only one (+0.0135)" | rise does not survive testing (BH p = 0.7678) |
| § 4, per-ladder significance | "None of these differences has been permutation-tested" | all 29 pairs tested; 3 ladders show a significant MCC fall, none a significant rise |
| § 2.1, GS tiering | "Not supplied in this revision" | supplied: 1/6 F1 pairs and 0/6 MCC pairs significant → 2 tiers |
| § 6.1, 55-map cells | "scored by `compute_corrected_f1_multi_buffer.py`… no `cli_args`" | corrected: all 31 (r2) and 19 (standardised) cells were scored by `evaluate_detections.py` with full `cli_args`, `mcc: true`, and a `tile_classification` block |
| § 6.1, sign-swap artefacts | `final_board_50m.json` `pairwise` cited as sign-swap results; `gemini37_arm_ladder.py` cited as a sign-swap instrument | corrected: that table is a tile-swap (its own `instrument` field says so) and that script carries no permutation test at all |

**What did NOT change**: every committed F1, MCC, cost and n_detections figure
in §§ 2–5; the ladder shape and its frame-invariance; the Pareto efficient sets
of § 5; § 4's mechanism account, which the test is consistent with; the PI's open
choice of instrument for the seven 55-map ladders, which § 4.1 reports under both
where both are registered rather than resolving.

**Cross-instrument check (§ 4.2)**: the two ladders that also have a registered
per-map sign-swap were tested under it as well, after it reproduced all four
committed `p7_saturation` F1 results exactly. Across the eight pairs both
instruments cover, **all eight tile-MCC significance calls agree**; one F1 call
differs (stride A's K = 3 → 5, significant on the tile-swap and not on the
sign-swap). The PI's instrument ruling is therefore material to marginal F1
claims and immaterial to the § 4.1 MCC conclusion.

**Still outstanding**: the Hsu MCB admissible sets (§ 6.1), the analysis row
(§ 6.2, which waits on them), and the `pv-diag-384` Phase-2 ladders (§ 6.3).

Artefacts: `mcc-test/` (per-ladder JSON, `summary.json`, the per-ladder
round-robins under `tiering/`, the sign-swap under `sign-swap/`). Instruments:
`scripts/era1_leaderboard_tiering.py --permute-mcc`,
`scripts/stride55_ladder.py --pairs-output-dir`, driver
`scripts/k_ladder_mcc_test.py`. Landed in commits `156bddf36`, `d10137595` and `d900ed1d5`.

### 2026-09-12 — Original publication (Session 154, K-ladder Phase 1 step 5)

Assembled by `scripts/build_k_ladder_tables.py` from
`results/k-ladder-2026-09-12/inventory.json` (metrics, from the register),
`results/stride-2026-08-25/findings.md` and
`results/55map-final-board-r2-2026-09-06/final_board_50m.json` (audited costs),
and this run's board-frame re-scores of the four gold-standard rungs, which ran
on sapphire. No API call. Two things are absent by decision rather than
oversight, and § 6 says which: the pairwise permutation testing, and the analysis
row that would have to state its result.
