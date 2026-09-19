# The image proposer x verifier 2x2 at deployment scale: test declaration

> **Last revised**: 2026-09-19 (original publication — declared before the
> primary rung's Gemini 3 arm 2 cells existed). See
> [§ Changelog](#changelog) for revision history.

**Declared**: 2026-09-19, 06:40 UTC, by the PI (Shawn Ross) with Claude
Code, session S155. **State of the data at declaration**: the 3.7 row
(`gemini37-image-55map-2026-09-13`) is scored at K = 1, 3, 5 on both arms;
the Gemini 3 row (`gemini3-image-55map-2026-09-16`) is scored at K = 1 on
both arms (`ba19eebd1`), its arm 1 K = 3 and K = 5 legs are verified but
unscored, and its **arm 2 K = 3 leg is in flight** (ten batch jobs, three
returned) and K = 5 not yet lodged. The primary rung's Gemini 3 arm 2 cell
therefore does not exist at declaration.

## 1. What the 2x2 is

Two proposer pools (rows) x two verifier arms (columns), all on the 55-map
corpus, the `g384_ov192` tiling (24,561 tiles), the `detect_brief-text-image`
configuration, and the stride-builder first-N unions:

| | arm 1: `gemini-3-flash-preview`, `minimal`, T 0.0 | arm 2: `gemini-3.7-flash`, `low`, T 0.0 |
|---|---|---|
| **row A**: 3.7 image pool (`gemini-3.7-flash`, `low`, T 0.7) | `IMG-ARM1-K{K}-carried` | `IMG-ARM2-K{K}-carried` |
| **row B**: Gemini 3 image pool (`gemini-3-flash-preview`, `minimal`, T 0.7) | `G3IMG-ARM1-K{K}-carried` | `G3IMG-ARM2-K{K}-carried` |

Every cell is materialised at its row's GS-carried operating point (row A:
`planning/gemini37-image-55map-2026-09-13.md` § 2 and the registered GS K = 5
cells; row B: `results/gemini3-image-55map-2026-09-16/gs-calibration/`), and
scored on the r2 board's instrument: corrected micro-F1 at 50 m and tile-MCC
on the 8,541-tile evaluation frame, `inputs/vectors/references/best-available-gt-55maps-r2.geojson`
(`scripts/gemini37_image_55map_r2.py`, `--campaign g37|g3`).

## 2. The primary rung and the two exploratory rungs

**K = 3 is the primary rung.** It is the 3.7 campaign's declared primary
(card § 4) and the rung whose row B arm 2 cell is unbuilt at declaration.

**K = 1 and K = 5 are exploratory replicates** of the same family. K = 1's
row B cells are already scored (`ba19eebd1`), so any K = 1 result is post
hoc whatever the family says; K = 5 is not preregistered on either row (the
3.7 card stops its ladder at K = 3; the K = 5 rung was added on 2026-09-16/17
for this 2x2). They are reported beside K = 3 as a coherent
three-rung reading, never as confirmatory results.

**The K = 3 → K = 5 contrast within the 3.7 row is exploratory** (PI ruling
2026-09-19): the K = 5 rung was added after the K = 3 results were known.

## 3. The family, per metric

Five tests at the primary rung, run separately on tile-MCC and on micro-F1
at 50 m, with Benjamini–Hochberg at q = 0.05 across the five within each
metric. All cells at the same K; `_c` is the carried cell.

| # | Name | Contrast | Question |
|---|---|---|---|
| T1 | proposer effect under arm 2 | `IMG-ARM2-K_c` vs `G3IMG-ARM2-K_c` | does the proposer family matter with the 3.7 verifier? |
| T2 | proposer effect under arm 1 | `IMG-ARM1-K_c` vs `G3IMG-ARM1-K_c` | does it matter with the Gemini 3 verifier? |
| T3 | verifier seat within row B | `G3IMG-ARM2-K_c` vs `G3IMG-ARM1-K_c` | does the 3.7 verifier help a Gemini 3 pool? (row A's is tested already: +0.0158 MCC at K = 3, `findings.md` § 4) |
| T4 | interaction | (A2 − A1) − (B2 − B1) | does the verifier's gain depend on the proposer family? |
| T5 | confound check | `G3IMG-ARM1-K3_c` vs `IM-k3` | with the five confounds removed (library, tiling, thinking, passes, tile convention), is the earlier Gemini 3 image cell reproduced? |

T5 is meaningful only at K = 3 (IM-k3 is a three-vote cell); at K = 1 and
K = 5 it is reported for completeness and labelled as such.

## 4. The instruments

**T1, T2, T3, T5**: the paired tile-swap permutation test already used by the
board and the 3.7 campaign — `n1_baseline_leaderboard_tiering.permutation_test_float`
for micro-F1 on per-tile TP/FP/FN and `mcc_tiering_55map.permutation_test_mcc`
for tile-MCC on per-tile predictions against a fixed truth vector — 10,000
permutations, `numpy.random.default_rng(42)`, probability-0.5 per-tile label
swap, two-sided p = mean(|null| ≥ |observed|).

**T4**: the same machinery lifted to four cells. Per tile *i* the four cells
contribute (A1, A2, B1, B2) — per-tile TP/FP/FN for micro-F1, per-tile
predictions for MCC. The statistic is

    D = [S(A2) − S(A1)] − [S(B2) − S(B1)]

with S the corpus-level statistic (micro-F1 from summed counts, or MCC from
the tile confusion). Under the null of no interaction the arm effect is the
same in both rows, so a tile's row-A pair and row-B pair are exchangeable:
each permutation draws a probability-0.5 mask over tiles and, for masked
tiles, swaps the (A1, A2) pair with the (B1, B2) pair; D is recomputed;
p = mean(|D_null| ≥ |D_obs|), two-sided, 10,000 permutations, seed 42. This
is the tile-swap test applied to the per-tile arm difference, and reduces to
T3-versus-row-A's-T3 for micro-F1's additive counts.

Implementation: `scripts/gemini37_image_55map_r2.py --stage tests-2x2 --rungs K`,
output `results/image-2x2-2026-09-19/tests_2x2_K{K}.json`, one file per rung.

## 5. Caveats declared with the family

1. **The E89 floor.** Independent re-invocations of these verifiers at T = 0
   differ in ~40 % of probabilities and flip 3.5–5.3 % of decisions at the
   operating point (erratum E89; the 2026-09-19 batch-vs-flex probe,
   `outputs/gemini37-image-55map-2026-09-13/verifier/g384_ov192_55map_g37img/probe-batch-vs-flex-2026-09-19/`).
   A tile-swap permutation tests sampling variation over tiles, not verifier
   nondeterminism, so a difference below that floor can be "significant"
   and still be drift. A null result is uninformative about small effects; a
   significant result smaller than the floor is not claimed without a
   replicate arm.
2. **Route.** Row A's arm 2 ran on realtime flex; row B's arm 2 runs on the
   Batch API (PI ruling 2026-09-18). The probe above found the route's
   effect indistinguishable from same-route re-invocation drift, so the
   route is not treated as a factor; it is recorded per cell.
3. **Operating points differ by row by design.** Each row is at its own
   GS-carried point, so T1 and T2 compare rows as deployed, not at a common
   threshold. The sweep oracles are reported beside the carried cells to
   show what a common-threshold reading would change.
4. **Row B at K = 1 over-generates** (F1 0.66 against row A's 0.87, tile-MCC
   0.71 against 0.76; `planning/observation-drafts-2026-09-19.md` Obs 485
   draft). The primary rung is K = 3 precisely because unanimity is the
   image pool's precision filter; the K = 1 replicate is expected to show
   the largest proposer effect and the K = 5 replicate the smallest.
5. **IM-k3's tile join** is not this chain's (83.65 % idempotent; `findings.md`
   § 7), so T5 inherits the caveat already recorded for the 3.7 campaign's
   IM-k3 comparison.
6. **Nothing here re-tiers a board or touches a signed row.** The 2x2's
   registration and signature are the PI's, after the tests are run.

## Changelog

### 2026-09-19 — Original publication

Declared with the Gemini 3 row's primary-rung arm 2 cell unbuilt (ten batch
jobs in flight, three returned at 06:27 UTC). Commit: `0e5985d83`.
