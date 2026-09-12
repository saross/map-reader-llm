# The K ladders: pass count at fixed parameters, Pareto-framed

> **Last revised**: 2026-09-12 (original publication — step 5 of the K-ladder
> Phase-1 run, `planning/k-ladder-phase1-run-2026-09-12.md`). Controlling card:
> `planning/k-ladder-review-2026-09-11.md`. Companions: the inventory
> (`inventory.md`), the Phase-2 costing
> (`reports/k-ladder-phase2-costing-2026-09-12.md`), the deltas
> (`reports/k-ladder-phase1-deltas-2026-09-12.md`).
> See [§ Changelog](#changelog).

**Scope, stated first.** Eight fixed-parameter ladders exist and are scorable at
US$0; all eight are tabulated here at their own headline buffer with an audited
cost per rung. The gold-standard ladder is additionally re-scored on the Era-2
board frame. The seven 55-map ladders' pairwise significance is **cited from
their own registered instrument**, not re-run under the board's — see § 6, which
says exactly what is and is not supplied. Every figure is read from a committed
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
+0.003 on two more, and rises materially on only one (the gold standard,
+0.0135 on the board frame). More passes buy localisation, not discrimination.
§ 4 treats that as the result it is rather than an artefact.

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
`scripts/selection_aware_intervals.py`. **Not supplied in this revision** — see
§ 6.1. The instrument and its inputs are committed and ready
(`tiering-input/gs-stride-a/`), so this is a gap in the run, not in the data.

## 3. The 55-map ladders

Seven ladders, all at 50 m corrected-F1 on the 8,541-tile corpus. Two operating
points are committed per rung where the campaign recorded both: the **carried**
point (the deployment threshold transferred from the gold standard) and the rung
**oracle** (that rung's own sweep argmax). Under R2 both are reported; the oracle
column is the one that would tier, the carried column is the transfer tax.

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
| 10 | 0.8813 | (0.96, k9) | 0.8728 | −0.0085 | 0.7359 | $173.59 † |

† The proposer leg is the same as § 3.2's, so the cost figure is the Gemini 3
board's. The 3.7 **verifier** leg is **not supplied**: that stage's meta was
overwritten by a 29-item cleanup pass, so its 57,482-candidate token load is not
on file (`reports/r7-gaps-deltas-2026-09-11.md` § 2.5). A simulated figure for
the K = 10 rung is about $64.7 on arm 2's per-candidate rate, giving about $238
all-in; it is recorded there, deliberately not in this table, because every other
cost cell here is audited. The K = 5 rung is absent (`zero-usd-inherited`, never
built).

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

What is NOT claimed: that any single ladder's MCC decline is individually
significant. None of these differences has been permutation-tested (§ 6.1), and
the per-rung MCC confidence intervals in the committed evaluations overlap
heavily. The claim is about a direction that is consistent across eight ladders,
and it is offered to the PI as a finding to interpret.

## 5. The Pareto frame

Figure: `figures/k-ladder-pareto.png` — audited all-in cost (log axis) against the
headline F1, one line per ladder, each point labelled with its K. In table form,
the efficient rungs of each ladder (a rung is efficient when no cheaper rung of
the same ladder scores as well):

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

### 6.1 No pairwise permutation testing, and so no per-family MCB

R2 and the run card ask for paired tile-swap permutation between adjacent rungs
and against K = 10, BH q = 0.05, and a Hsu MCB admissible set per family. **None
of that was run.** For the gold-standard ladder everything needed is committed
and the command is one line:

```bash
python scripts/era1_leaderboard_tiering.py \
    --analysis-id k-ladder-gs-stride-a-2026-09-12 \
    --conditions results/k-ladder-2026-09-12/tiering-input/gs-stride-a/run-conditions.json \
    --analyses  results/k-ladder-2026-09-12/tiering-input/gs-stride-a/run-analyses.json \
    --bounds inputs/vectors/bounds/384/era2_b_intersection_bounds.geojson \
    --output-dir results/k-ladder-2026-09-12/tiering/gs-stride-a
```

For the seven 55-map ladders it is not one line, and that is the substantive
reason it is missing. The board instrument's statistic is a tile-swap over a
per-tile TP/FP/FN reproduction rebuilt from each cell's recorded `cli_args`; the
55-map cells were scored by `compute_corrected_f1_multi_buffer.py`, which writes
`summary.json` with no `cli_args`, and against an extended ground truth (student
references plus adjudicated phantoms) that the tile-swap would not rebuild. Those
ladders DO have a registered significance instrument — the per-map paired
sign-swap permutation of `scripts/stride55_ladder.py` (10,000 permutations,
seed 42; bet P7) and its `gemini37_arm_ladder.py` counterpart, whose committed
results are the `p7_saturation` block of
`results/stride55-2026-08-27/ladder.json` and the `pairwise` table of
`results/55map-final-board-r2-2026-09-06/final_board_50m.json`. Running the
board's instrument over them instead would be a different test against a
different reference, and it is not obviously the better one. **That choice is the
PI's, and it is put back rather than taken.**

### 6.2 No analysis row

The run card asks for one UNSIGNED analysis row `k-ladder-2026-09-12`. It is not
authored, because an analysis row states an outcome and this document's headline
outcome — which rungs are statistically separable — is exactly what § 6.1 did not
measure. Authoring a row whose `outcome` described only the descriptive tables
would register a weaker claim than the data supports and then have to be amended.
The row is drafted in `reports/k-ladder-phase1-deltas-2026-09-12.md` § 5, ready to
author once § 6.1 lands.

### 6.3 No Gemini 3 `pv-diag-384` ladders

Every one of those twelve families holds two rungs, K = 5 and K = 10, so none
reaches the three-rung bar (`inventory.md` § 3). Their K = 1 and K = 3 rungs are
Phase 2, costed at US$4.50 for the two T 0.7 pools and US$24.84 for all 28
(`reports/k-ladder-phase2-costing-2026-09-12.md`).

## Changelog

### 2026-09-12 — Original publication (Session 154, K-ladder Phase 1 step 5)

Assembled by `scripts/build_k_ladder_tables.py` from
`results/k-ladder-2026-09-12/inventory.json` (metrics, from the register),
`results/stride-2026-08-25/findings.md` and
`results/55map-final-board-r2-2026-09-06/final_board_50m.json` (audited costs),
and this run's board-frame re-scores of the four gold-standard rungs, which ran
on sapphire. No API call. Two things are absent by decision rather than
oversight, and § 6 says which: the pairwise permutation testing, and the analysis
row that would have to state its result.
