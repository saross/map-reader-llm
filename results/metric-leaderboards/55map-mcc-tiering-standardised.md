# 55-map standardised board — tile-MCC permutation tiering

> Alternate-metric (tile-MCC) statistical tiering for the eight standardised-reference cells (MCC is buffer-invariant on this reference): round-robin tile-swap permutation on the MCC statistic (10k, seed 42, two-sided) + BH-FDR q=0.05 + greedy-clique tiers — the same machinery as the F1-led board. 20/28 pairs significant -> 5 tier(s). 95% CIs are the scoring engine's BCa bootstrap CIs, carried from `summary.json`. Gate: rebuilt per-tile confusion matrices reproduce the committed evaluations exactly (8/8).

| rank | cell | tier | MCC | 95% CI | sens | spec | tp/fp/fn/tn |
|---:|---|---:|---:|---|---:|---:|---|
| 1 | IM-k3 | 1 | 0.7120 | [0.699, 0.725] | 0.705 | 0.965 | 2486/178/1038/4839 |
| 2 | T03-k3 (oracle) | 2 | 0.6888 | [0.675, 0.702] | 0.698 | 0.953 | 2459/238/1065/4779 |
| 3 | TH7-k3 | 2 | 0.6796 | [0.666, 0.693] | 0.688 | 0.952 | 2423/241/1101/4776 |
| 4 | TM-n10-k5 (uplift) | 3 | 0.6709 | [0.657, 0.684] | 0.654 | 0.965 | 2306/178/1218/4839 |
| 5 | T03-k4 | 3 | 0.6690 | [0.655, 0.682] | 0.651 | 0.965 | 2295/176/1229/4841 |
| 6 | TH7-k4 (carry-forward) | 3 | 0.6650 | [0.651, 0.679] | 0.641 | 0.968 | 2258/161/1266/4856 |
| 7 | TM-k3 | 4 | 0.6569 | [0.643, 0.671] | 0.645 | 0.960 | 2272/199/1252/4818 |
| 8 | TM-k4 | 5 | 0.6401 | [0.627, 0.654] | 0.610 | 0.968 | 2148/161/1376/4856 |

## Reading this board

**Confidence intervals vs significance.** The 95% intervals in the board table
are *marginal* per-cell BCa bootstrap intervals; the significance tests are
*paired* tile-swap permutations over the same tiles. Overlapping intervals are
therefore consistent with a significant paired difference — the paired test
removes between-tile variance that the marginal intervals retain. Read the
BH-adjusted pairwise table below, not interval overlap, for significance.

**Attribution resolution (55-map deployment corpus, standardised
reference).** The ruling-21 standardised reference replaces the legacy
ring-censored pairing. Two positional-quality classes remain:

1. *Student-digitised mounds* (n = 4,731 after standardisation): 641
   reviewed records carry marked centres (±2.5 m); the 4,090
   out-of-scope records keep as-digitised positions (median 8.6 m,
   p90 18.3 m from the true centre on the jitter sample).
2. *Extension mounds* (n = 279 — model-detected mounds the students
   missed, human-confirmed): ALL at marked centres (±2.5 m).

Because every extension record is exactly localised, the layer enters
the extended ground truth WHOLE at every buffer radius — the legacy
interval-censored ring gate (and its sub-50 m collapse onto the student
layer) no longer applies, and sub-50 m Track-2 figures are genuine.
Tile-level MCC is buffer-invariant by construction on this reference.
The reference is best-possible, not gold-standard: residual long-range
duplicates deflate F1 ≈ −0.03 and absent joint student+model misses
inflate it ≈ +0.011–0.012 (net ≈ −0.017, rank-preserving to first
order) — see the reference README and Obs 396.

## Pairwise (BH-adjusted)

| pair | ΔMCC | p | BH p | sig |
|---|---:|---:|---:|---|
| IM-k3 vs T03-k4 | +0.0430 | 0.0000 | 0.0000 | yes |
| IM-k3 vs TH7-k3 | +0.0323 | 0.0000 | 0.0000 | yes |
| IM-k3 vs TH7-k4 (carry-forward) | +0.0469 | 0.0000 | 0.0000 | yes |
| IM-k3 vs TM-k3 | +0.0550 | 0.0000 | 0.0000 | yes |
| IM-k3 vs TM-k4 | +0.0719 | 0.0000 | 0.0000 | yes |
| IM-k3 vs TM-n10-k5 (uplift) | +0.0411 | 0.0000 | 0.0000 | yes |
| T03-k3 (oracle) vs T03-k4 | +0.0198 | 0.0000 | 0.0000 | yes |
| T03-k3 (oracle) vs TH7-k4 (carry-forward) | +0.0238 | 0.0000 | 0.0000 | yes |
| T03-k3 (oracle) vs TM-k3 | +0.0319 | 0.0000 | 0.0000 | yes |
| T03-k3 (oracle) vs TM-k4 | +0.0487 | 0.0000 | 0.0000 | yes |
| T03-k4 vs TM-k4 | +0.0289 | 0.0000 | 0.0000 | yes |
| TH7-k3 vs TM-k4 | +0.0395 | 0.0000 | 0.0000 | yes |
| TM-k3 vs TM-k4 | +0.0168 | 0.0000 | 0.0000 | yes |
| TM-k4 vs TM-n10-k5 (uplift) | -0.0308 | 0.0000 | 0.0000 | yes |
| TH7-k3 vs TH7-k4 (carry-forward) | +0.0146 | 0.0001 | 0.0002 | yes |
| TH7-k4 (carry-forward) vs TM-k4 | +0.0250 | 0.0002 | 0.0003 | yes |
| TH7-k3 vs TM-k3 | +0.0227 | 0.0005 | 0.0008 | yes |
| IM-k3 vs T03-k3 (oracle) | +0.0232 | 0.0009 | 0.0014 | yes |
| T03-k3 (oracle) vs TM-n10-k5 (uplift) | +0.0179 | 0.0048 | 0.0071 | yes |
| TM-k3 vs TM-n10-k5 (uplift) | -0.0140 | 0.0079 | 0.0111 | yes |
| T03-k4 vs TM-k3 | +0.0121 | 0.0616 | 0.0821 | ns |
| T03-k4 vs TH7-k3 | -0.0106 | 0.0689 | 0.0877 | ns |
| T03-k3 (oracle) vs TH7-k3 | +0.0092 | 0.1099 | 0.1338 | ns |
| TH7-k3 vs TM-n10-k5 (uplift) | +0.0087 | 0.1774 | 0.2070 | ns |
| TH7-k4 (carry-forward) vs TM-k3 | +0.0081 | 0.2060 | 0.2307 | ns |
| TH7-k4 (carry-forward) vs TM-n10-k5 (uplift) | -0.0058 | 0.3602 | 0.3879 | ns |
| T03-k4 vs TH7-k4 (carry-forward) | +0.0039 | 0.4858 | 0.5038 | ns |
| T03-k4 vs TM-n10-k5 (uplift) | -0.0019 | 0.7609 | 0.7609 | ns |
