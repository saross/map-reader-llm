# Tile size × overlap: a clean 2×2 at the proposer stage

> **Last revised**: 2026-08-24, twice (the verifier stage RAN — PI-approved
> $6.33 spend, 9,133/9,133 candidates, zero failures; the post-verifier board
> reverses the tile-size ranking and confirms the overlap reversal survives —
> then same-day audit corrections restated the reversal against the
> like-for-like K = 10 consensus baseline and repaired a stale B = 1,000
> table). See [§ Changelog](#changelog) for revision history.

**What this is.** A post-hoc (E41-class) 2 × 2 crossing tile size
(384 px, 512 px) with tile overlap (12.5 %, 50 %), n = 10 proposer
passes per cell, run on 2026-08-18 and committed at `e612f7ac0`. One
configuration throughout — `detect_brief-text`, library
`8580ecb2258b64a0…`, `gemini-3-flash-preview`, text modality, MINIMAL
thinking, T = 0.7 — so the only things that vary are the two geometry
factors. Scoring cost **$0**: every number below comes from the
committed detections.

**What this is not.** A registered hypothesis. §§ 2–10 are the
**consensus-only** board, written when the verifier stage was costed
but not yet run. The verifier stage has since RUN (PI-approved
2026-08-24, $6.33 costed / $6.27 expected billed) and its board is
[§ The verifier stage, run](#the-verifier-stage-run-2026-08-24).

## The headline, in one line

**At a single pass, both bigger tiles and less overlap win. Once you
aggregate, overlap reverses and becomes the single most valuable thing
in the grid — while tile size never reverses.** 512 px beats 384 px
everywhere; 50 % overlap loses badly at K = 1 and wins decisively once
the cross-tile corroboration filter that overlap itself creates is
switched on.

**Post-verifier addendum (2026-08-24): tile size DOES reverse once the
precision stage runs.** Under the full proposer-verifier pipeline
384 px beats 512 px at both overlaps (significantly at 12.5 %), the
overlap reversal survives at both tile sizes, and the best cell is
384 px / 50 % at **F1 0.8961**. The consensus-only tile-size claim
above is a truncated-pipeline artefact; see
[§ The verifier stage, run](#the-verifier-stage-run-2026-08-24).

## The 2 × 2

Mean of ten single passes, common footprint, 20 m matching, uniform
20 m within-pass deduplication. ± values are the standard deviation
across the ten passes.

| Cell | Tiles/pass | Precision | Recall | **F1** | **Tile MCC** | Dets/pass |
|---|---:|---:|---:|---:|---:|---:|
| **512 px / 12.5 %** | 296 | 0.4719 ± 0.0069 | 0.7769 ± 0.0127 | **0.5871 ± 0.0077** | **0.4415 ± 0.0128** | 704.6 |
| **512 px / 50 %** | 832 | 0.3157 ± 0.0066 | 0.8991 ± 0.0075 | **0.4672 ± 0.0074** | **0.3096 ± 0.0178** | 1219.5 |
| **384 px / 12.5 %** | 487 | 0.3615 ± 0.0089 | 0.8369 ± 0.0090 | **0.5049 ± 0.0091** | **0.1452 ± 0.0114** | 991.3 |
| **384 px / 50 %** | 1398 | 0.2308 ± 0.0040 | 0.9327 ± 0.0039 | **0.3700 ± 0.0053** | **0.2321 ± 0.0131** | 1730.2 |

Read as a 2 × 2 on F1:

| | 12.5 % overlap | 50 % overlap | Overlap effect |
|---|---:|---:|---:|
| **512 px** | 0.5871 | 0.4672 | −0.1200 |
| **384 px** | 0.5049 | 0.3700 | −0.1348 |
| **Tile-size effect (384 − 512)** | −0.0824 | −0.0972 | |

### Paired tile-bootstrap contrasts

Per-tile TP/FP/FN averaged over each cell's ten passes, then a paired
tile bootstrap — one resampled index set applied to both arms of a
contrast, seed 42, percentile CI95, **B = 10,000**, two-sided
p = max(2 · min tail, 1/B). The count follows the 2026-08-19 PI ruling
(erratum E82), which standardises the study on 10,000 rather than the
1,000 Decision 10 pre-specified. This resampler is the script's own and
was never on the D15 defective path, so the change is a reduction in
Monte Carlo noise and nothing more: every Δ is identical to five decimal
places, every CI width moves by under 5 %, and no verdict changes.

| Contrast | ΔF1 | CI95 | p | Excludes 0 |
|---|---:|---|---:|---|
| Overlap at 512 px (12.5 % − 50 %) | +0.1200 | [+0.0872, +0.1531] | 0.0001 (floor) | yes |
| Overlap at 384 px (12.5 % − 50 %) | +0.1348 | [+0.1058, +0.1636] | 0.0001 (floor) | yes |
| Tile size at 12.5 % (384 − 512) | −0.0824 | [−0.1243, −0.0429] | 0.0001 (floor) | yes |
| Tile size at 50 % (384 − 512) | −0.0972 | [−0.1196, −0.0753] | 0.0001 (floor) | yes |
| **Interaction** (overlap effect at 512 − at 384) | −0.0148 | [−0.0552, +0.0268] | 0.4902 | **no** |

**Both main effects are unambiguous; the interaction is not resolved.**
On single-pass F1 the two factors are additive to within the
instrument's resolution: 50 % overlap costs about 0.12–0.13 F1
regardless of tile size, and dropping from 512 px to 384 px costs about
0.08–0.10 F1 regardless of overlap.

The overlap direction reproduces H13's registered result (F1 falls
monotonically with overlap) on a different footprint, at a different
temperature, with ten passes instead of three. The tile-size direction
is the surprise; see [§ Surprises](#surprises-flagged-rather-than-smoothed).

## The mechanism: overlap manufactures its own consensus

Within-pass 20 m deduplication records how many overlapping tiles
independently reported the same location (`cluster_size`). That number
is the corroboration filter `c`, and it exists **only** where tiles
overlap:

| Cell | c = 1 | c = 2 | c = 3 | c ≥ 4 | **Corroborated (c ≥ 2)** |
|---|---:|---:|---:|---:|---:|
| 512 px / 12.5 % | 93.0 % | 6.6 % | 0.2 % | 0.2 % | **7.0 %** |
| 512 px / 50 % | 59.2 % | 18.8 % | 9.4 % | 12.6 % | **40.8 %** |
| 384 px / 12.5 % | 92.3 % | 7.5 % | 0.2 % | 0.0 % | **7.7 %** |
| 384 px / 50 % | 58.3 % | 21.3 % | 8.5 % | 11.9 % | **41.7 %** |

Overlap is the factor and corroboration is its by-product, so the two
cannot be separated — which is exactly why `c` is swept rather than
fixed. What the sweep shows is that **a 50 % overlap pass carries its
own internal consensus**. At 12.5 % overlap `c ≥ 2` is not a filter but
a demolition: it strips recall to 0.124 (512 px) and 0.159 (384 px)
because almost nothing is ever seen twice. At 50 % overlap the same
filter *keeps* recall near 0.87–0.89 while lifting precision from
0.156 → 0.531 (512 px) and 0.123 → 0.367 (384 px).

## Corroboration × consensus (c × k), K = 10

F1 at selected combinations of the within-pass corroboration filter `c`
and the across-pass consensus threshold `k`, pooling all ten passes.

| k | 512/12.5 c1 | 512/12.5 c2 | 512/50 c1 | 512/50 c2 | 512/50 c3 | 384/12.5 c1 | 384/50 c2 | 384/50 c3 |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 0.4077 | 0.2087 | 0.2675 | 0.6590 | 0.6743 | 0.3388 | 0.5194 | 0.6269 |
| 3 | 0.5772 | 0.1963 | 0.4446 | 0.7174 | 0.6895 | 0.4806 | 0.5850 | 0.6651 |
| 5 | 0.6464 | 0.1784 | 0.5282 | 0.7291 | 0.6809 | 0.5378 | 0.6404 | 0.6769 |
| 8 | **0.6759** | 0.1212 | 0.6166 | **0.7518** | 0.6351 | 0.5940 | 0.6855 | 0.6750 |
| 10 | 0.6429 | 0.0671 | 0.6805 | 0.7237 | 0.5629 | **0.6475** | **0.7205** | 0.6539 |

The full grid — all three `c` levels, every `k`, every K, with
precision, recall and MCC — is in `sweep.csv` (228 rows).

**The consensus-only board.** Best cell per configuration at K = 10:

| Rank | Cell | c | k | Precision | Recall | **F1** | Tile MCC |
|---:|---|---:|---:|---:|---:|---:|---:|
| 1 | 512 px / 50 % | 2 | 8 | 0.7535 | 0.7500 | **0.7518** | 0.5897 |
| 2 | 384 px / 50 % | 2 | 10 | 0.6762 | 0.7710 | **0.7205** | 0.4909 |
| 3 | 512 px / 12.5 % | 1 | 8 | 0.6233 | 0.7383 | **0.6759** | 0.5383 |
| 4 | 384 px / 12.5 % | 1 | 10 | 0.5619 | 0.7640 | **0.6475** | 0.3137 |

**The overlap ranking inverts under aggregation; the tile-size ranking
does not.** 50 % overlap goes from worst-by-0.12 at single pass to
best-by-0.08 under consensus, because the filter it enables recovers
more precision than the extra looks cost. 512 px stays ahead of 384 px
in both regimes and at every K.

Best tile MCC anywhere in the sweep is 0.6155 (512 px / 50 %, c ≥ 2,
k ≥ 10, F1 0.7237) — the same cell, one vote above the F1 optimum.

## K sensitivity: do passes substitute for overlap?

The K ladder sub-samples the first K of the same ten passes, so K = 3 ⊂
K = 5 ⊂ K = 10 and the comparison is nested. Spend is audited flex
(see [§ Cost](#cost)).

| Cell | K | Calls | Flex $ | Union recall (ceiling) | Best F1 | at c / k |
|---|---:|---:|---:|---:|---:|---|
| 512 / 12.5 % | 1 | 296 | 0.1902 | 0.7757 | 0.5845 | 1 / 1 |
| 512 / 12.5 % | 3 | 888 | 0.5707 | 0.8411 | 0.6763 | 1 / 3 |
| 512 / 12.5 % | 5 | 1,480 | 0.9511 | 0.8575 | 0.6736 | 1 / 4 |
| 512 / 12.5 % | 10 | 2,960 | 1.9022 | 0.8715 | 0.6759 | 1 / 8 |
| **512 / 50 %** | **1** | **832** | **0.5340** | **0.8972** | **0.7121** | **2 / 1** |
| 512 / 50 % | 3 | 2,496 | 1.6019 | 0.9229 | 0.7429 | 2 / 3 |
| 512 / 50 % | 5 | 4,160 | 2.6699 | 0.9393 | 0.7440 | 2 / 4 |
| 512 / 50 % | 10 | 8,320 | 5.3398 | 0.9416 | 0.7518 | 2 / 8 |
| 384 / 12.5 % | 1 | 487 | 0.2906 | 0.8364 | 0.5021 | 1 / 1 |
| 384 / 12.5 % | 3 | 1,461 | 0.8718 | 0.8645 | 0.5976 | 1 / 3 |
| 384 / 12.5 % | 5 | 2,435 | 1.4530 | 0.8762 | 0.6176 | 1 / 5 |
| 384 / 12.5 % | 10 | 4,870 | 2.9059 | 0.8925 | 0.6475 | 1 / 10 |
| 384 / 50 % | 1 | 1,398 | 0.8382 | 0.9346 | 0.6633 | 3 / 1 |
| 384 / 50 % | 3 | 4,194 | 2.5146 | 0.9439 | 0.6837 | 2 / 3 |
| 384 / 50 % | 5 | 6,990 | 4.1911 | 0.9486 | 0.7045 | 2 / 5 |
| 384 / 50 % | 10 | 13,980 | 8.3821 | 0.9509 | 0.7205 | 2 / 10 |

**The verdict: passes do not substitute for overlap.** The earlier,
scope-confounded reading was that 384 px / 12.5 % at K = 10 reached a
higher union-recall ceiling than 512 px / 50 % at K = 3, for less money.
On one footprint the comparison reverses on **both** counts:

| | Union recall | Best F1 | Flex $ |
|---|---:|---:|---:|
| 384 px / 12.5 %, K = 10 | 0.8925 | 0.6475 | $2.9059 |
| 512 px / 50 %, K = 3 | **0.9229** | **0.7429** | **$1.6019** |
| Δ (more passes − more overlap) | **−0.0304** | **−0.0953** | **+$1.3040** |

More overlap is better *and* cheaper. The result is stronger than that
head-to-head suggests: **one single pass of 512 px / 50 % ($0.5340,
F1 0.7121) beats ten passes of either 12.5 % cell** (F1 0.6759 at
$1.9022; F1 0.6475 at $2.9059). Overlap buys corroboration inside one
pass; extra passes buy the same kind of corroboration at K times the
price.

Two secondary readings of the ladder:

- **Diminishing returns in K are steep.** Union recall for 512 / 50 %
  moves 0.8972 → 0.9229 → 0.9393 → 0.9416 across K = 1, 3, 5, 10: the
  first two extra passes buy 0.026, the next seven buy 0.019.
- **The vote optimum sits at or near the grid edge everywhere.** At
  K = 3 every cell peaks at k = K; at K = 10 the 512 px cells peak at
  k = 8 (interior) but both 384 px cells still peak at k = 10. Even ten
  passes do not bracket the consensus optimum for 384 px.

## Cost

Audited spend, summed from the committed per-pass `cost_estimate`
blocks including the six additive one-tile recovery passes.

| Cell | Calls | List price | **Flex (billed)** | $/call flex |
|---|---:|---:|---:|---:|
| 512 px / 12.5 % | 2,960 | $3.8045 | **$1.9022** | $0.000643 |
| 512 px / 50 % | 8,320 | $10.6796 | **$5.3398** | $0.000642 |
| 384 px / 12.5 % | 4,870 | $5.8119 | **$2.9059** | $0.000597 |
| 384 px / 50 % | 13,980 | $16.7643 | **$8.3821** | $0.000600 |
| **Total** | **30,130** | **$37.0603** | **$18.5302** | |

**The `cost_estimate` blocks are list price and overstate billing by
2×.** Gemini real-time flex carries the same 50 % discount as the async
Batch API, so the flex column is the billed basis and is what every
dollar figure in this document uses. The $37.06 recorded in metadata is
not an overrun.

F1 per flex dollar at each cell's best K = 10 operating point:
512 / 12.5 % 0.3553, 384 / 12.5 % 0.2228, 512 / 50 % 0.1408,
384 / 50 % 0.0860 — which inverts the quality ranking, because F1 per
dollar rewards cheapness at K = 10 where quality has already plateaued.
The operationally useful reading is the K = 1 row of the ladder:
**512 px / 50 % at K = 1 returns F1 0.7121 for $0.5340 — 1.33 F1 per
dollar at a quality no 12.5 % cell reaches at any K in this grid.**

## Surprises, flagged rather than smoothed

1. **384 px is not the sweet spot here — 512 px is, at every overlap
   and every K.** The study's established 384 px preference comes from
   Era-2 work at T = 1.0 with a K = 10 consensus and a different
   scoring chain; this grid is T = 0.7, uniformly deduplicated, on a
   footprint intersection. The contrast is nonetheless clean within
   itself: both tile-size contrasts exclude zero, in the same direction,
   at both overlap levels, and the ordering survives every aggregation
   setting swept. **This does not by itself overturn the 384 px
   choice** — 512 px was never tested against it at T = 0.7 on one
   footprint before — but it is a direct challenge to it and should not
   be filed away.
2. **Tile MCC is non-monotone in both factors** (0.4415 / 0.3096 /
   0.1452 / 0.2321), and 384 px / 12.5 % is the *worst* cell on MCC
   despite ranking second on F1. The tile confusion matrix explains it.
   All four cells share the same carrier grid, hence the same 225
   populated and 262 empty tiles; only where detections land differs:

   | Cell | Tile TP | Tile TN | Tile FP | Tile FN | Sensitivity | Specificity |
   |---|---:|---:|---:|---:|---:|---:|
   | 512 px / 12.5 % | 199.0 | 140.3 | 121.7 | 26.0 | 0.8844 | 0.5355 |
   | 512 px / 50 % | 209.9 | 82.8 | 179.2 | 15.1 | 0.9329 | 0.3160 |
   | 384 px / 12.5 % | 208.3 | 44.8 | 217.2 | 16.7 | 0.9258 | 0.1710 |
   | 384 px / 50 % | 218.8 | 44.4 | 217.6 | 6.2 | 0.9724 | 0.1695 |

   At 384 px the model already fires on 217 of the 262 empty carrier
   tiles at 12.5 % overlap — specificity has effectively **saturated**,
   so raising overlap to 50 % adds almost no new false-positive tiles
   (217.2 → 217.6) while adding true-positive ones, and MCC *rises*.
   Tile MCC on a 487-tile carrier is therefore reading detection
   *spread* once specificity bottoms out, not discrimination. Report it;
   rank on F1. This echoes H13's conclusion that MCC should not carry an
   overlap claim.
3. **The four cells do not share one tile union**, despite all four
   manifests being pinned against the same Era-2 footprint (`fe623a555`).
   The footprint-majority rule keeps a tile whole when more than half of
   it falls inside, so a denser tiling accretes more marginal ground:
   the unions run 1415.8 / 1534.5 / 1508.2 / 1640.6 km² holding
   435 / 482 / 466 / 495 reference mounds. Verifying rather than
   assuming this is what turned a would-be tile-inclusion confound into
   a common-scope design (see [§ Method](#method)). The 384 px / 12.5 %
   cell *does* reproduce era-2-487 exactly — symmetric difference
   0.0 m², asserted in code.
4. **A resolver guard mis-fires on this corpus.**
   `lib_detection_paths.resolve_pool_passes(..., expected_passes=N)`
   counts distinct pass *identities* pool-wide, and real-time runs name
   their pass file after config, model and date — never the run number —
   so ten run directories holding an identically-named file collapse to
   one identity and the guard raises `PassCountMismatch` on a perfectly
   healthy pool. Reproduced against the committed H13 arm B and arm C
   pools as well as all four grid cells. The fix is to count identities
   *within* each run directory, which preserves the chunked-Batch-pass
   protection the guard was written for; this analysis does that locally
   in `grid_prepare_scoring.resolve_cell_passes` and does **not** modify
   `lib_detection_paths.py`, whose D6 hardening landed in the same
   session (`6b1cb87af`, `6fa658877`, `4c44e3fd6`, `9ecd47b94`).
   Flagged for that module's owner.

## What the verifier stage would cost (costed 2026-08-18; run 2026-08-24 — see [§ The verifier stage, run](#the-verifier-stage-run-2026-08-24))

A verifier pass scores one crop per surviving proposer candidate, so
adding it to any operating point costs that point's candidate count ×
$0.000693 (`results/verifier-robustness/pareto/pareto_v2.json`
`cost_model.vf_call_usd`, measured at Gemini flex rates in the
2026-06-12 token-load audit).

| Cell | Operating point | Candidates | Verifier $ | Consensus-only F1 |
|---|---|---:|---:|---:|
| 512 px / 12.5 % | K10 best (c ≥ 1, k ≥ 8) | 507 | $0.3514 | 0.6759 |
| 512 px / 50 % | K10 best (c ≥ 2, k ≥ 8) | 426 | $0.2952 | 0.7518 |
| 384 px / 12.5 % | K10 best (c ≥ 1, k ≥ 10) | 582 | $0.4033 | 0.6475 |
| 384 px / 50 % | K10 best (c ≥ 2, k ≥ 10) | 488 | $0.3382 | 0.7205 |
| 512 px / 12.5 % | K10 union (c ≥ 1, k ≥ 1) | 1,402 | $0.9716 | 0.4077 |
| 512 px / 50 % | K10 union (c ≥ 1, k ≥ 1) | 2,585 | $1.7914 | 0.2675 |
| 384 px / 12.5 % | K10 union (c ≥ 1, k ≥ 1) | 1,827 | $1.2661 | 0.3388 |
| 384 px / 50 % | K10 union (c ≥ 1, k ≥ 1) | 3,319 | $2.3001 | 0.2172 |

**Recommendation (not a spend authorisation).** Verify the four K = 10
*unions*, not the consensus-pruned sets: the verifier is the precision
stage, and handing it a set a consensus threshold has already pruned
throws away the recall the union bought. That costs **$6.33** in
verifier calls across the whole grid, on top of proposer spend already
incurred, and gives the honest comparison of the four geometries under
the study's actual pipeline. A cheaper first step is the two 50 % cells'
unions alone (**$4.09**), since those are the two candidates for a
production tiling.

## The verifier stage, run (2026-08-24)

The PI approved the costed stage on 2026-08-24 under an
exact-reproduction stop rule. `materialise_grid_unions.py` rebuilt the
four K = 10 unions through the sweep's own loader and clusterer, gated
on the documented counts (1,402 / 2,585 / 1,827 / 3,319 — all exact);
the adversarial text verifier (`verify_adversarial-text`,
gemini-3-flash-preview, T = 0.0, MINIMAL, n = 1 — the study's
carry-forward verifier) scored all **9,133 candidates with zero
failures** (committed at `8eda1e3a3`). Thresholding and scoring cost
$0: `scripts/grid_verifier_analysis.py` re-joins the committed
probabilities to the committed unions (join gates: contiguous
candidate keys, carrier-tile reassignment, and re-scoring each
unthresholded union to reproduce the committed sweep row), sweeps
every achievable (prob_t, k) operating point per cell (580 rows,
`verifier_sweep.csv`), and scores with the same machinery, footprint,
and B = 10,000 paired tile bootstrap as the consensus board.

**The post-verifier board** (best F1@20 m per cell; CI95 BCa at
B = 10,000 from each cell's registered evaluation):

| Rank | Cell | prob_t | k | n | Precision | Recall | **F1** | CI95 | Tile MCC |
|---:|---|---:|---:|---:|---:|---:|---:|---|---:|
| 1 | 384 px / 50 % | ≥ 0.15 | ≥ 10 | 400 | 0.9275 | 0.8668 | **0.8961** | [0.8657, 0.9198] | 0.7965 |
| 2 | 512 px / 50 % | ≥ 0.15 | ≥ 9 | 382 | 0.9346 | 0.8341 | **0.8815** | [0.8518, 0.9073] | 0.8011 |
| 3 | 384 px / 12.5 % | ≥ 0.20 | ≥ 7 | 358 | 0.9525 | 0.7967 | **0.8677** | [0.8335, 0.8957] | 0.7751 |
| 4 | 512 px / 12.5 % | ≥ 0.15 | ≥ 5 | 383 | 0.8799 | 0.7874 | **0.8311** | [0.7938, 0.8624] | 0.7937 |

The verifier lifts every cell's best F1 by +0.130 to +0.220 over the
consensus-only board, and the gain is largest exactly where
consensus-only was worst (the two 384 px cells: +0.220 and +0.176).

**Question 1 — the tile-size ranking does NOT survive: it reverses.**
Paired tile bootstrap, B = 10,000, seed 42. The pre-verifier arm here
is the **like-for-like baseline**: the registered K = 10 best
consensus-only operating points scored as single sets on the same
instrument — *not* the single-pass contrasts of § 3, which
run-average ten passes and hold a different estimand (each row's
baseline reproduction is gated at 5 × 10⁻⁴ against the committed
board).

| Contrast | K10 consensus baseline | Post-verifier | Post excludes 0 |
|---|---|---|---|
| Tile size at 12.5 % (384 − 512) | −0.0284 [−0.0813, +0.0233], p = 0.281 | **+0.0366 [+0.0026, +0.0717], p = 0.034** | **yes** |
| Tile size at 50 % (384 − 512) | −0.0312 [−0.0695, +0.0052], p = 0.089 | +0.0147 [−0.0093, +0.0393], p = 0.231 | no |
| Overlap at 512 px (12.5 % − 50 %) | −0.0758 [−0.1204, −0.0310], p = 0.0004 | −0.0504 [−0.0781, −0.0224], p = 0.0004 | yes |
| Overlap at 384 px (12.5 % − 50 %) | −0.0730 [−0.1185, −0.0284], p = 0.0026 | −0.0285 [−0.0530, −0.0045], p = 0.0208 | yes |
| Interaction (post-verifier) | — | −0.0220 [−0.0581, +0.0141], p = 0.234 | no |

Read precisely, the reversal is: **a non-significant 512 px lead at
the aggregated consensus stage (−0.028 / −0.031, both CIs spanning
zero) becomes a significant 384 px lead at 12.5 % overlap once the
verifier runs, and a sign-reversed but unresolved +0.015 at 50 %.**
The single-pass contrasts (−0.0824 / −0.0972, both excluding zero,
§ 3) are where 512 px's advantage is strong — but they measure mean
single-pass performance, and aggregation alone already erodes that
advantage to non-significance before the verifier flips the sign. The
mechanism is the one § Unresolved anticipated: 384 px lost to 512 px
almost entirely on precision, which the verifier recovers, while its
higher union-recall ceilings (0.8925 / 0.9509 vs 0.8715 / 0.9416) are
the resource the verifier cannot create. This **dissolves
Surprise 1** — the "512 px challenge" to the study's 384 px preference
was an artefact of the truncated (verifier-less) pipeline — and
repeats the Era-1 pattern in which the verifier rescued 256 px
(Obs 352): the verifier moves the optimum towards smaller,
recall-richer tilings. One honest caveat: each arm's operating point
is F1-selected on the same 487 tiles it is scored on, and the
post-verifier sweep offers ~4–5× the selection space of the consensus
sweep; the contrasts condition on that selection.

**Question 2 — the overlap reversal survives.** 50 % overlap wins at
both tile sizes under the full pipeline (−0.0504 at 512 px,
p = 0.0004; −0.0285 at 384 px, p = 0.0208), and it already won at the
K = 10 consensus baseline (−0.0758, p = 0.0004; −0.0730, p = 0.0026 —
table above). The margin roughly halves once the verifier runs, which
is the partial-redundancy outcome § Unresolved predicted: the
corroboration filter and the verifier overlap in function but are not
interchangeable, and what remains of the 50 % advantage tracks its
recall-ceiling edge.

**Consensus and verifier are complements, not substitutes.** Every
cell's best operating point retains a vote threshold (k ≥ 5 to
k ≥ 10) on top of the probability threshold. The pure-verifier board
(k = 1, best prob_t — the verifier as the *only* precision stage)
tops out at 0.8153 (384 px / 12.5 %, prob_t ≥ 0.2) and trails the
stacked optimum in every cell, by 0.052 to 0.203. Handing the
verifier the raw union and letting thresholds on votes and
probability act jointly is what buys the board above.

**Tile MCC saturation dissolves.** The consensus-only board's 384 px
MCC pathology (specificity saturated at 0.17) disappears once the
verifier strips false positives: all four cells sit at MCC
0.775–0.801, and the F1 ranking and MCC ranking broadly agree.

**Billing.** The four verifier `run.meta.json` cost blocks sum to
$12.5428 list; Gemini real-time flex bills at half list, so the
expected billed figure is **$6.2714** ($0.000687/call), against the
costed $6.33 ($0.000693/call) — a −$0.06 variance. The PI's
billing-console glance should expect ≈ $6.27.

**Registered conditions.** Each cell's best operating point is
materialised and scored at B = 10,000 (BCa) under a reproduction gate
(all four within 5 × 10⁻⁵ of the sweep):
`results/grid-2026-08-18/conditions-verified/<cell>/`, summarised in
`grid_verified_conditions.json`, registered as the four
`*-k10-verified-p*` conditions and the analysis row
`grid-postverifier-2026-08-18`.

**The incumbents, like for like (stride-programme Phase A,
2026-08-24).** The study's leading verified cells, clipped to this
common footprint under own-scope reproduction gates (all four
reproduce their registered F1@20 m exactly; each loses 5 detections
to the clip; `incumbents_common_footprint.json`, script
`grid_incumbent_rescore.py`):

| Set | F1@20 m | F1@30 m | Δ vs 384/50 @20 m (paired, B = 10,000) |
|---|---:|---:|---|
| **384 px / 50 % verified (this grid)** | **0.8961** | **0.9034** | — |
| opmax (16-of-30 HIGH + n = 5 T0.3 verifier) | 0.8842 | 0.9031 | +0.0120 [−0.0135, +0.0371], p = 0.350 |
| registered headline (16-of-30 HIGH + n = 1 verifier) | 0.8838 | 0.8958 | +0.0123 [−0.0117, +0.0358], p = 0.312 |
| min11 (min-6of10 + verifier) | 0.8719 | 0.8892 | +0.0242 [−0.0035, +0.0519], p = 0.080 |
| min6 (min-true-3of5 + verifier) | 0.8623 | 0.8743 | **+0.0339 [+0.0065, +0.0623], p = 0.015** |

On one evaluation, the grid's stride-192 cell is the point-estimate
leader at both buffers and statistically clears min6, but its edge
over opmax, the headline, and min11 is within noise: it **joins the
leading shelf as a tie at roughly a fifth of the incumbents' cost**
(~$10.7 vs the ~$50-class 30-pass HIGH pipelines), rather than
dethroning them. Configuration confound noted: the grid cell differs
from the incumbents in geometry AND proposer (MINIMAL T = 0.7
brief-text vs HIGH-thinking consensus), so this board motivates the
stride programme (`planning/stride-programme-2026-08-24.md`) rather
than settling attribution.

**Scope caveats carried forward.** Four map sheets, one proposer
configuration, one model, T = 0.7, one verifier configuration at
n = 1; E41-class post-hoc throughout. The best-F1 operating points are
selected on the same ground truth they are scored on (as on the
consensus board); the paired contrasts are the significance
instrument, and single-cell CIs are reported for the register only.

## What remains unresolved without the verifier stage

*Two of the five questions this section originally posed were settled
by the verifier stage above (2026-08-24); the original wording is
preserved in the [changelog](#changelog) entry.*

- ~~Whether the tile-size ranking survives a verifier~~ — **settled:
  it reverses.** See [§ The verifier stage, run](#the-verifier-stage-run-2026-08-24).
- ~~Whether the overlap reversal survives a verifier~~ — **settled: it
  survives**, at roughly half the consensus-only margin.
- **Whether the consensus optimum is interior at 384 px.** Ten passes
  still peak at k = 10 for both 384 px cells — post-verifier as well
  (384 px / 50 % best sits at k ≥ 10; 512 px / 50 % moves interior to
  k ≥ 9). Either the optimum lies beyond K = 10 or the F1 surface is
  flat near it; the grid cannot tell these apart.
- **The single-pass tile-size result versus the Era-2 384 px corpus.**
  Reconciling them needs either the 512 px geometry run at Era-2's
  T = 1.0, or the Era-2 conditions re-scored on this footprint — a
  scoring job, not an API job, but out of scope here. The
  post-verifier reversal reduces the urgency: under the full pipeline
  the grid now *agrees* with the Era-2 384 px preference.
- **Generalisation.** Four map sheets, one configuration, one model, one
  temperature.

## Method

- **Preparation**: `scripts/grid_prepare_scoring.py`. Each of the 40
  passes is loaded, its additive `run_<N>_recovery` fragment merged in
  where one exists (six passes: `g512_ov064/run_6`, `g512_ov256/run_3`,
  `g384_ov048/run_3`, and `g384_ov192/run_{4,8,10}`), and its coverage
  record asserted equal to the cell's pinned manifest before anything is
  scored. Without the merge the affected pass covers N−1 of N tiles,
  trips the evaluator's E72 partial-coverage guard, and converts that
  tile's ground truth into an artificial false negative —
  asymmetrically, since `g384_ov192` lost three passes to the others'
  one. All 40 coverage assertions pass.
- **Deduplication** (E80): within-pass 20 m greedy deduplication
  (`merge_passes.deduplicate_within_pass`, § 8.5 Step 1), cluster mean
  centroids carried as points, which is loss-free because the
  evaluator's Hungarian matcher reduces every geometry to its centroid.
  Removal rates track the geometry exactly: 6.4 % and 7.1 % at 12.5 %
  overlap, 41.2 % and 41.4 % at 50 %.
- **Scope**: the four cells' tile unions differ (Surprise 3), so every
  cell is scored on the **common** footprint — the four-way
  intersection, 1364.47 km², holding 428 reference mounds — carried on
  the era-2-487 grid clipped to it (487 carrier tiles). Clipping costs
  each cell 32–151 detections per pass. Native per-cell scopes are also
  materialised under `outputs/grid-2026-08-18/scoring/native/` for
  transparency; across-cell differences there are not attributable to
  geometry alone and are not reported here.
- **Scoring**: `scripts/grid_analysis.py`, via
  `lib_advanced_metrics.score_detection_set` at a 20 m buffer with tile
  MCC. An undefined MCC is reported as `null`, never as 0.0 (E81); two
  of the 228 swept cells are undefined, both 384 px / 12.5 % at K = 10
  with c ≥ 3 and k ≥ 9 or 10, where the filter leaves zero detections.
- **Clustering**: across-pass consensus uses the NumPy-vectorised
  restatement of the project's greedy star clustering
  (`h13_k_sensitivity.cluster_votes`) rather than
  `merge_passes.cluster_across_passes`, because K = 10 on the densest
  cell pools about 17,000 points and the pure-Python path is O(n²).
  Equivalence was checked, not assumed (see
  [§ Verification](#verification)).
- **Bootstrap**: per-tile resampling on the common carrier grid, seed 42,
  percentile CI95, **B = 10,000**, paired draws. The interaction is a
  difference-of-differences on the same paired draw. The resampling unit
  and method follow Decision 10; the iteration count follows erratum E82.

## Verification

Three independent cross-checks, all reproduced in this session:

1. **Two scoring paths agree.** Single-pass F1 computed per map by
   Hungarian matching (`calculate_f1_internal`) and pooled from the
   per-tile TP/FP/FN table (`compute_per_tile_tp_fp_fn`) agree to four
   decimal places on all four cells: 0.5871/0.5871, 0.4672/0.4671,
   0.5049/0.5048, 0.3700/0.3699. The two paths share no code below the
   reference-scoping helpers.
2. **The vectorised clusterer matches the library's.** At K = 3 on the
   two 12.5 % cells, `cluster_votes` and
   `h13_aggregation_sweep.aggregate` (which calls
   `merge_passes.cluster_across_passes`) return identical cluster counts
   and identical vote histograms: `g512_ov064` 998 clusters,
   {1: 346, 2: 178, 3: 474}; `g384_ov048` 1,306 clusters,
   {1: 370, 2: 196, 3: 740}.
3. **Cost reconciles to the run record.** Summing all 46 committed
   `*.meta.json` cost blocks (40 passes + 6 recovery passes) gives
   30,130 calls and $37.0603 list, i.e. **$18.5302 flex** — matching the
   figure recorded in the data commit `e612f7ac0` to the cent.

Tier-1 tests for the new code are in `tests/test_grid_analysis.py`
(14 tests): pass resolution with and without recovery fragments, the
short-pool guard, the identically-named-pass case, ground-truth scoping,
carrier-grid assignment, the undefined-MCC contract, and the paired
difference-of-differences bootstrap (determinism, degenerate null,
pooled point estimate, and recovery of a constructed interaction).

## Artefacts

- `grid_analysis.json` — every consensus-board number, machine-readable;
  the source for §§ 2–10 of this document.
- `sweep.csv` — the full K × corroboration × consensus sweep (228 rows).
- `per_tile_counts.json` — run-averaged per-tile TP/FP/FN on the carrier
  grid (the bootstrap input).
- `verifier_analysis.json` — every post-verifier number, machine-readable;
  the source for § The verifier stage, run.
- `verifier_sweep.csv` — the full prob_t × k post-verifier sweep
  (580 rows).
- `conditions-verified/<cell>/` — the four materialised best-operating-
  point verified sets with their B = 10,000 BCa evaluations, summarised
  in `conditions-verified/grid_verified_conditions.json`.
- `outputs/grid-2026-08-18/scoring/` — deduplicated per-pass detection
  sets in both scopes, the five bounds files, and `prepare_summary.json`
  (footprint audit plus per-pass dedup statistics).
- `outputs/grid-2026-08-18/verifier/<cell>/` — the four K = 10 union
  candidate sets (`union_k10.geojson`, per-candidate `vote_count`) and
  the committed verifier outputs (`verify/probabilities.json`,
  `verify/run.meta.json`).
- Register rows: consensus analysis `grid-tilesize-overlap-2026-08-18`
  (landed 2026-08-19, D16 closed) and post-verifier analysis
  `grid-postverifier-2026-08-18` (landed 2026-08-24) in
  `results/analyses-manifest.json`.

## See also

- **Preceding experiment(s)**: `results/h13-overlap-2026-08-18/findings.md`
  — the registered three-arm H13 overlap contrast at 512 px, whose
  monotone "F1 falls with overlap" result this grid reproduces at single
  pass, and whose Tier-0 aggregation sweep first suggested the reversal
  confirmed here.
- **Preceding experiment(s)**: `planning/h13-arms-bc-plan-2026-08-17.md`
  — the phase gate and the $0 scoring-chain pattern this analysis
  follows.
- **Follow-up experiment(s)**: the proposer-verifier stage, run
  2026-08-24 (recall-levers programme Phase 1;
  [§ The verifier stage, run](#the-verifier-stage-run-2026-08-24)).
  The 384-px-versus-512-px reconciliation at T = 1.0 remains open but
  de-urgented: the full pipeline already agrees with the Era-2 384 px
  preference.
- **Run output directory**: `outputs/grid-2026-08-18/` — the 40
  committed passes, six recovery passes, two smoke tests, the derived
  scoring sets under `scoring/`, and the verifier inputs and outputs
  under `verifier/`.
- **Working-notes Observations**: **Obs 433** (the post-verifier
  tile-size reversal and overlap survival, 2026-08-24). Consensus-board
  candidates raised at S136 close (the resolver defect, the
  specificity-saturation reading of tile MCC, and overlap as
  within-pass consensus).
- **Decisions / Errata**: E41 — post-hoc analysis classification.
  E72 — the partial-coverage guard the recovery merge exists to satisfy.
  E80 — missing within-pass deduplication in the scoring path.
  E81 — undefined tile MCC must not be published as 0.0.
  Decision 10 — tile-level resampling, percentile CI95.
  E82 — bootstrap iteration count standardised at 10,000.

## Changelog

### 2026-08-24 (later still) — Stride-programme Phase A: the incumbents join the board

**Trigger**: the PI directed the overlap/stride programme
(`planning/stride-programme-2026-08-24.md`); its $0 Phase A clips the
incumbent verified sets to this document's common footprint under
own-scope reproduction gates (all four exact). New § "The incumbents,
like for like" in the verifier-stage section. Headline: 384/50
verified leads at both buffers but ties opmax/headline/min11
statistically and beats min6 (p = 0.015) — a plateau of tied leaders
with the new geometry at ~1/5 the incumbents' cost. Nothing else in
this document changed.

### 2026-08-24 (later) — Audit corrections: the like-for-like baseline and a stale table

**Trigger**: the same-day two-lens audit of the scoring chain
(commits `57b7ad7ad` code, `0a6bde47f` rerun). Two corrections, one
addition; no post-verifier number changed.

1. **The pre/post framing was not like for like** (audit C1). The
   earlier entry below — and the section text as first published —
   benchmarked the post-verifier tile-size contrasts against the
   single-pass −0.0824 / −0.0972 (both significant), while
   benchmarking overlap against the K = 10 board. The proper
   pre-verifier arm for a single aggregated operating point is the
   registered K = 10 best consensus-only set on the same instrument,
   now computed and published
   (`verifier_analysis.json.bootstrap_contrasts_consensus_k10_baseline`):

   | Contrast | Single-pass (was cited) | K10 baseline (now cited) | Post-verifier |
   |---|---|---|---|
   | Tile size @ 12.5 % | −0.0824, sig | −0.0284, p = 0.281, NOT sig | +0.0366, p = 0.034, sig |
   | Tile size @ 50 % | −0.0972, sig | −0.0312, p = 0.089, NOT sig | +0.0147, p = 0.231, ns |

   The sign flip stands; the claim's stated strength does not:
   aggregation alone had already eroded 512 px's single-pass advantage
   to non-significance, and the verifier flips the sign from there.
   § Question 1 is restated accordingly, with a selection-space caveat
   added.
2. **The § 3 contrasts table carried B = 1,000 CIs under its
   B = 10,000 heading** (audit X2) — a leftover from the 2026-08-19
   re-run that updated the changelog but not the body table. Now the
   `grid_analysis.json` B = 10,000 values (deltas identical; CI edges
   move at the third decimal; p floors 0.0010 → 0.0001).
3. **Chain hardening** (same commits): billing counters, failure and
   retry counts now derived from the run metas (121 transient retries
   surfaced, items_failed 0 confirmed at source); the c = 1 union
   restriction declared on every verified board row; `K` added to the
   comparator board; `candidate_id` provenance added to the
   materialised conditions; the reproduction gate now refuses to write
   any summary artefact on failure. The four candidate manifests — the
   probability↔feature join witnesses — were committed and the join
   verified at source over all 9,133 candidates (ids contiguous in
   feature order; centroids agree to ≤ 0.069 m against 5.6–8.0 m
   minimum spacing).

**What did NOT change**: every board value, every post-verifier
contrast, both headline answers, the billing totals, and the
registered conditions (re-scored identically at B = 10,000).

### 2026-08-24 — The verifier stage runs; tile size reverses, overlap survives

**Trigger**: the PI approved the costed verifier stage on 2026-08-24
($6.33, the four K = 10 unions). `materialise_grid_unions.py` reproduced
the documented union counts exactly; the carry-forward adversarial text
verifier scored 9,133/9,133 candidates with zero failures (`8eda1e3a3`);
`scripts/grid_verifier_analysis.py` thresholded and scored the verified
sets for $0 (S142, sapphire).

**Both open questions settled** (new section: § The verifier stage, run):

| Claim | Consensus-only (was) | Post-verifier (now) |
|---|---|---|
| Tile size at 12.5 % (384 − 512) | −0.0824 [−0.1243, −0.0429] | **+0.0366 [+0.0026, +0.0717], p = 0.034 — REVERSED** |
| Tile size at 50 % (384 − 512) | −0.0972 [−0.1196, −0.0753] | +0.0147 [−0.0093, +0.0393], p = 0.231 — sign reversed, unresolved |
| Overlap at 512 px (12.5 % − 50 %) | best-point gap +0.0759 (50 % wins) | −0.0504 [−0.0781, −0.0224], p = 0.0004 — 50 % still wins |
| Overlap at 384 px (12.5 % − 50 %) | best-point gap +0.0730 (50 % wins) | −0.0285 [−0.0530, −0.0045], p = 0.021 — 50 % still wins |
| Best cell | 512 px / 50 % F1 0.7518 | **384 px / 50 % F1 0.8961 [0.8657, 0.9198]** |

Surprise 1 (the 512 px challenge to the 384 px preference) is dissolved
as a truncated-pipeline artefact. Headline and § Unresolved edited in
place; the superseded § Unresolved wording for the two settled bullets
is preserved here: they asked whether the tile-size ranking and the
overlap reversal would survive a verifier, flagged the 384 px recall
ceilings (0.8925 / 0.9509 vs 0.8715 / 0.9416) as the possible flip
mechanism (confirmed), and predicted the 50 % advantage would shrink
towards its recall-ceiling edge under filter-verifier redundancy
(confirmed: the margin roughly halves).

**What did NOT change**: every consensus-only number (§§ 2–10), both
single-pass main effects, the unresolved interaction, the audited
proposer spend, and the two remaining § Unresolved bullets
(the k = 10 grid-edge question and generalisation).

**Billing reconciliation**: metas $12.5428 list → $6.2714 expected flex
billed vs $6.33 costed (−$0.06); PI console glance pending.

**Registration**: four `*-k10-verified-p*` conditions (B = 10,000 BCa,
reproduction gate ≤ 5 × 10⁻⁵) + analysis row
`grid-postverifier-2026-08-18`. Commits `8f4ecdd82` (scoring chain),
`8d4ab3fd8` (results), plus this document refresh.

### 2026-08-19 — B = 10,000 standardisation and condition registration

**Trigger**: the 2026-08-19 PI ruling (erratum E82) standardises the study on
10,000 bootstrap iterations, and defect D16 required per-cell evaluations before
the grid could take a register row.

**Bootstrap re-run at B = 10,000.** `grid_analysis.py` implements its own paired
resampler and was never on the D15 defective path, so this is a precision change,
not a correction.

| Quantity | B = 1,000 | B = 10,000 |
|---|---|---|
| overlap @ 512 px | +0.12001 [+0.08538, +0.15263] | +0.12001 [+0.08722, +0.15313] |
| overlap @ 384 px | +0.13482 [+0.10577, +0.16493] | +0.13482 [+0.10576, +0.16358] |
| tile size @ 12.5 % | −0.08239 [−0.12405, −0.04520] | −0.08239 [−0.12429, −0.04287] |
| tile size @ 50 % | −0.09719 [−0.12048, −0.07401] | −0.09719 [−0.11963, −0.07529] |
| interaction | −0.01481 [−0.05495, +0.02690] | −0.01481 [−0.05520, +0.02684] |

**What did NOT change**: every Δ is identical, every point estimate across the
228-row sweep is identical, all four contrasts still exclude zero, and the
interaction still spans zero (p 0.488 → 0.4902, a resolution artefact of 1/B).
CI widths move by 0.954× to 1.033×. Both headline claims stand unaltered. The
superseded B = 1,000 artefacts are archived at
`archive/superseded-grid-analyses/`.

**Condition registration (D16 closed)**: each cell's published best-F1@20 m
operating point at K = 10 was rebuilt from the prepared deduplicated passes by
`scripts/grid_materialise_conditions.py`, written with E79 nearest-centroid tile
assignment against the common carrier, and scored by `evaluate_detections.py` at
B = 10,000. All four reproduce their published sweep F1 to under 5 × 10⁻⁴. The
run now carries four registered conditions and the analysis row
`grid-tilesize-overlap-2026-08-18`.

| Cell | Operating point | F1@20 m | CI95 (BCa, B = 10,000) | Tile MCC |
|---|---|---:|---|---:|
| 512 px / 12.5 % | c ≥ 1, k ≥ 8 | 0.6759 | [0.6239, 0.7237] | 0.5383 |
| 512 px / 50 % | c ≥ 2, k ≥ 8 | **0.7518** | [0.7026, 0.7938] | 0.5897 |
| 384 px / 12.5 % | c ≥ 1, k ≥ 10 | 0.6475 | [0.5935, 0.6966] | 0.3137 |
| 384 px / 50 % | c ≥ 2, k ≥ 10 | 0.7205 | [0.6749, 0.7618] | 0.4909 |

These single-condition intervals are not the significance instrument. Decision 10
defines significance on a *difference* CI, which is what the paired contrasts
above supply; the per-cell intervals are reported because the register requires
each condition to carry its own metrics.

### 2026-08-18 — Original publication

Session 136, executed on sapphire, **$0 API**. The $0 scoring chain for
the tile-size × overlap grid committed at `e612f7ac0`: uniform recovery
merge, uniform 20 m within-pass deduplication, a common four-way
footprint intersection built after verifying — not assuming — that the
four cells' tile unions diverge, the 2 × 2 with paired tile-bootstrap
contrasts and a difference-of-differences interaction, a K = 1/3/5/10
ladder, the full corroboration × consensus sweep, and a costed (not
run) verifier stage.

Headline results: both single-pass main effects exclude zero
(overlap −0.1200 / −0.1348 F1; tile size −0.0824 / −0.0972 F1) and the
interaction does not (CI95 [−0.0550, +0.0269]); the overlap ranking
**inverts** under aggregation while the tile-size ranking does not;
passes do **not** substitute for overlap (384 px / 12.5 % at K = 10
loses to 512 px / 50 % at K = 3 by 0.0304 union recall and 0.0953 best
F1, and costs $1.3040 more). Best cell overall: 512 px / 50 %, c ≥ 2,
k ≥ 8, K = 10 — F1 0.7518, tile MCC 0.5897.
