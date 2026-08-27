# The final 55-map board @ 50 m — every run, carried and oracle

> **Last revised**: 2026-08-27 (original publication). Card:
> `planning/55map-final-board-2026-08-27.md`. Reference:
> ruling-21 standardised (4,731 student + 279 extension).
> Instrument: round-robin tile-swap micro-F1 permutation (10000, seed 42) + BH q=0.05 + greedy-clique tiers (the GS chain).
> 176/210 pairs significant.

| rank | cell | basis | tier | group | cost | point | F1@50 | 95% CI | P@50 | R@50 | tile-MCC | n |
|---:|---|---|---:|---|---:|---|---:|---|---:|---:|---:|---:|
| 1 | B-N10-oracle | oracle | 1 | a | $174 | (0.20, k9) | 0.8558 | [0.8475, 0.8636] | 0.8901 | 0.8242 | 0.713 | 4639 |
| 2 | B-N5-oracle | oracle | 2 | b | $97 | (0.20, k5) | 0.8515 | [0.8430, 0.8595] | 0.8929 | 0.8138 | 0.710 | 4566 |
| 3 | B-N3-oracle | oracle | 2 | b | $65 | (0.20, k3) | 0.8505 | [0.8423, 0.8584] | 0.8718 | 0.8303 | 0.713 | 4772 |
| 4 | B-N5-carried | carried | 2 | b | $97 | (0.15, k5) | 0.8502 | [0.8416, 0.8582] | 0.8748 | 0.8269 | 0.701 | 4736 |
| 5 | B-N10-carried | carried | 2 | bc | $174 | (0.15, k10) | 0.8498 | [0.8411, 0.8581] | 0.8974 | 0.8070 | 0.698 | 4505 |
| 6 | A-N10-oracle | oracle | 3 | cd | $104 | (0.15, k7) | 0.8420 | [0.8331, 0.8503] | 0.8756 | 0.8108 | 0.696 | 4639 |
| 7 | T03-oracle | oracle | 3 | def | $261 | (0.20, k3) | 0.8406 | [0.8318, 0.8490] | 0.8625 | 0.8198 | 0.695 | 4762 |
| 8 | A-N10-carried | carried | 4 | eg | $104 | (0.15, k8) | 0.8392 | [0.8303, 0.8479] | 0.8894 | 0.7944 | 0.693 | 4475 |
| 9 | TH7-oracle | oracle | 4 | def | $207 | (0.15, k3) | 0.8387 | [0.8295, 0.8474] | 0.8583 | 0.8200 | 0.680 | 4786 |
| 10 | A-N5-oracle | oracle | 4 | eg | $60 | (0.15, k4) | 0.8383 | [0.8294, 0.8469] | 0.8760 | 0.8038 | 0.691 | 4597 |
| 11 | A-N5-carried | carried | 4 | eg | $60 | (0.15, k4) | 0.8383 | [0.8294, 0.8469] | 0.8760 | 0.8038 | 0.691 | 4597 |
| 12 | A-N3-oracle | oracle | 5 | fh | $41 | (0.20, k2) | 0.8326 | [0.8238, 0.8410] | 0.8511 | 0.8148 | 0.702 | 4796 |
| 13 | T03-k4 | carried | 5 | ghi | $261 | (0.15, k4) | 0.8303 | [0.8210, 0.8394] | 0.8933 | 0.7756 | 0.669 | 4350 |
| 14 | UPL-oracle | oracle | 5 | hi | $58 | (0.15, k5) | 0.8279 | [0.8180, 0.8373] | 0.8895 | 0.7743 | 0.671 | 4361 |
| 15 | A-N1-oracle | oracle | 6 | ij | $21 | (0.20, k1) | 0.8231 | [0.8144, 0.8317] | 0.8342 | 0.8124 | 0.701 | 4879 |
| 16 | TH7-k4 | carried | 6 | jk | $207 | (0.15, k4) | 0.8169 | [0.8066, 0.8268] | 0.8999 | 0.7479 | 0.665 | 4164 |
| 17 | TM-oracle | oracle | 7 | kl | $23 | (0.20, k3) | 0.8110 | [0.8007, 0.8211] | 0.8944 | 0.7419 | 0.662 | 4156 |
| 18 | B-N1-oracle | oracle | 7 | l | $31 | (0.20, k1) | 0.8013 | [0.7926, 0.8098] | 0.7556 | 0.8529 | 0.710 | 5655 |
| 19 | IM-oracle | oracle | 7 | l | $195 | (0.15, k3) | 0.8010 | [0.7911, 0.8104] | 0.8293 | 0.7747 | 0.712 | 4680 |
| 20 | TM-k4 | carried | 8 | m | $23 | (0.15, k4) | 0.7833 | [0.7722, 0.7943] | 0.8994 | 0.6938 | 0.640 | 3865 |
| 21 | IM-k4 | carried | 9 | n | $195 | (0.15, k4) | 0.7400 | [0.7279, 0.7521] | 0.8935 | 0.6315 | 0.655 | 3541 |

**Reading the groups**: `tier` is the greedy-clique tier (disjoint
bands); `group` is the compact letter display — cells sharing ANY
letter are statistically indistinguishable under the BH-adjusted
pairwise tests, so letters show the overlaps the disjoint tiers
cannot. `cost` is the run's audited all-in flex spend (full
basis); a run's carried and oracle cells share it. See
`significance-groups.png` for the dot-and-CI plot and the full
pairwise significance matrix.

## Runs: as run versus theoretical maximum

One row per run: the carried ("as run / GS-chosen") result and
the oracle (standardised-reference argmax within the verified
sweep space). Tiers from the 21-cell board above.

| run | carried F1@50 (tier) | oracle F1@50 (tier) | oracle point |
|---|---|---|---|
| B, N = 10 (384/50 %) | 0.8498 (T2) | 0.8558 (T1) | (0.20, k9) |
| B, N = 5 | 0.8502 (T2) | 0.8515 (T2) | (0.20, k5) |
| B, N = 3 | — | 0.8505 (T2) | (0.20, k3) |
| B, N = 1 | — | 0.8013 (T7) | (0.20, k1) |
| A, N = 10 (384/33 %) | 0.8392 (T4) | 0.8420 (T3) | (0.15, k7) |
| A, N = 5 | 0.8383 (T4) | 0.8383 (T4) | (0.15, k4) |
| A, N = 3 | — | 0.8326 (T5) | (0.20, k2) |
| A, N = 1 | — | 0.8231 (T6) | (0.20, k1) |
| T0.3 (HIGH, K = 5) | 0.8303 (T5) | 0.8406 (T3) | (0.20, k3) |
| T0.7 (HIGH, K = 5) | 0.8169 (T6) | 0.8387 (T4) | (0.15, k3) |
| min-uplift (K = 10) | — | 0.8279 (T5) | (0.15, k5) |
| text-min (K = 5) | 0.7833 (T8) | 0.8110 (T7) | (0.20, k3) |
| image (HIGH, K = 5) | 0.7400 (T9) | 0.8010 (T7) | (0.15, k3) |

## Cost efficiency: what a dollar buys

One row per run at its DEPLOYMENT basis (carried where one
exists, otherwise the rung oracle, marked). `$/mound` is the
run's full flex cost per true-positive mound at 50 m — the
project's established per-mound economics. `marginal $/+0.01 F1`
prices each step UP the cost-sorted Pareto frontier (— =
dominated: a cheaper run scores higher). Plain F1-per-dollar is
deliberately omitted — it is maximised by the cheapest run
almost regardless of quality.

| run | basis | cost | F1@50 (tier) | TP mounds | $/mound | frontier | marginal $/+0.01 F1 |
|---|---|---:|---|---:|---:|---|---:|
| A, N = 1 | oracle | $21 | 0.8231 (T6) | 4,070 | $0.0050 | YES | — |
| text-min (K = 5) | carried | $23 | 0.7833 (T8) | 3,476 | $0.0067 | — | — |
| B, N = 1 | oracle | $31 | 0.8013 (T7) | 4,273 | $0.0073 | — | — |
| A, N = 3 | oracle | $41 | 0.8326 (T5) | 4,082 | $0.0101 | YES | $21.78 |
| min-uplift (K = 10) | oracle | $58 | 0.8279 (T5) | 3,879 | $0.0149 | — | — |
| A, N = 5 | carried | $60 | 0.8383 (T4) | 4,027 | $0.0148 | YES | $32.51 |
| B, N = 3 | oracle | $65 | 0.8505 (T2) | 4,160 | $0.0157 | YES | $4.70 |
| B, N = 5 | carried | $97 | 0.8502 (T2) | 4,143 | $0.0235 | — | — |
| A, N = 10 (384/33 %) | carried | $104 | 0.8392 (T4) | 3,980 | $0.0261 | — | — |
| B, N = 10 (384/50 %) | carried | $174 | 0.8498 (T2) | 4,043 | $0.0429 | — | — |
| image (HIGH, K = 5) | carried | $195 | 0.7400 (T9) | 3,164 | $0.0618 | — | — |
| T0.7 (HIGH, K = 5) | carried | $207 | 0.8169 (T6) | 3,747 | $0.0554 | — | — |
| T0.3 (HIGH, K = 5) | carried | $261 | 0.8303 (T5) | 3,886 | $0.0672 | — | — |

## Provenance and gates

- Stage 1 (`final_board_sweeps.py`): G4 scorer gate ×9 exact;
  identity gates ×9 exact counts; mechanism gates ×5 exact
  (TP, FP, FN) triples; A/B geometry gates 0.0000 m. Oracle
  argmaxes re-derived on the standardised reference — 11 of 13
  equal the previously selected points (T03 and TM nudge
  prob 0.15 → 0.20 by +0.0013 / +0.0001).
- Stage 2: `evaluate_detections.py`, 14 buffers, tile-level BCa
  bootstrap 10,000 / seed 42, `--mcc`, per cell.
- Stage 3 (this build): G3 board-regression gate — the 8-cell
  committed standardised board reproduced exactly (f1, all 28
  pairwise p-values, tiers); coincidence gates — TH7/IM/uplift
  oracles landed on committed detection sets and reproduce the
  committed evaluations exactly; per-cell mechanism bound 0.003.
- Incumbent oracles are best-within-VERIFIED-space (vote ≥ 3
  shells / the ≥ 3-of-10 band); A/B oracles search the full
  vote ≥ 1 unions. N = 1/3 rungs are oracle-only (no carried
  point was ever registered there).

## Changelog

### 2026-08-27 (later) — Groups, costs, and efficiency

PI request (interactive): compact-letter-display `group` column
and the two-panel significance figure
(`significance-groups.png`); run-cost column; the
cost-efficiency section ($/mound + marginal frontier pricing).
Board membership, tiers, and all cell values unchanged.

### 2026-08-27 — Original publication

Built by Session 143 per the signed card; $0 API, sapphire.
