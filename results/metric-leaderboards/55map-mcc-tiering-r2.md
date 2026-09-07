# 55-map board, reference r2 — tile-MCC permutation tiering

> Alternate-metric (tile-MCC) statistical tiering for the eight reference-r2 cells (MCC is buffer-invariant on this reference): round-robin tile-swap permutation on the MCC statistic (10k, seed 42, two-sided) + BH-FDR q=0.05 + greedy-clique tiers — the same machinery as the F1-led board. 20/28 pairs significant -> 5 tier(s). 95% CIs are the scoring engine's BCa bootstrap CIs, carried from `evaluation.json`. Gate: rebuilt per-tile confusion matrices reproduce the committed evaluations exactly (8/8).

| rank | cell | tier | MCC | 95% CI | sens | spec | tp/fp/fn/tn |
|---:|---|---:|---:|---|---:|---:|---|
| 1 | IM-k3 | 1 | 0.7110 | [0.696, 0.725] | 0.704 | 0.965 | 2486/178/1043/4834 |
| 2 | T03-k3 (oracle) | 2 | 0.6889 | [0.674, 0.704] | 0.697 | 0.953 | 2461/236/1068/4776 |
| 3 | TH7-k3 | 2 | 0.6792 | [0.664, 0.694] | 0.687 | 0.952 | 2424/240/1105/4772 |
| 4 | TM-n10-k5 (uplift) | 3 | 0.6695 | [0.654, 0.684] | 0.653 | 0.964 | 2305/179/1224/4833 |
| 5 | T03-k4 | 3 | 0.6691 | [0.654, 0.684] | 0.651 | 0.965 | 2297/174/1232/4838 |
| 6 | TH7-k4 (carry-forward) | 3 | 0.6647 | [0.650, 0.680] | 0.640 | 0.968 | 2259/160/1270/4852 |
| 7 | TM-k3 | 4 | 0.6565 | [0.641, 0.671] | 0.644 | 0.961 | 2273/198/1256/4814 |
| 8 | TM-k4 | 5 | 0.6397 | [0.625, 0.654] | 0.609 | 0.968 | 2149/160/1380/4852 |

## Reading this board

**Confidence intervals vs significance.** The 95% intervals in the board table
are *marginal* per-cell BCa bootstrap intervals; the significance tests are
*paired* tile-swap permutations over the same tiles. Overlapping intervals are
therefore consistent with a significant paired difference — the paired test
removes between-tile variance that the marginal intervals retain. Read the
BH-adjusted pairwise table below, not interval overlap, for significance.

**Attribution resolution (55-map deployment corpus, reference r2).**
Revision r2 applies the PI's cluster- and empty-tile-audit adjudications
to the ruling-21 standardised reference: 6 records removed (points the
audit found not to be mounds) and 14 added (mounds the audit confirmed
that no layer carried). Three positional-quality classes:

1. *Student-digitised mounds* (n = 4,726): 641 reviewed records carry
   marked centres (±2.5 m); the remainder keep as-digitised positions
   (median 8.6 m, p90 18.3 m from the true centre on the jitter sample).
2. *Extension mounds* (n = 278 — model-detected mounds the students
   missed, human-confirmed): ALL at marked centres (±2.5 m).
3. *Audit-reviewed mounds* (n = 14 — found by the cluster and empty-tile
   audits, absent from both layers): at the reviewer's mark (±2.5 m),
   graded ``directly_reviewed``.

Total 5,018. Every class is exactly localised or better than the legacy
ring gate required, so the layer enters the extended ground truth WHOLE
at every buffer radius and tile-level MCC stays buffer-invariant, exactly
as on the standardised reference it revises.

r2 is a REVISION of a best-possible reference, not a gold standard. It
narrows two of the standardised reference's known biases — the removed
points were residual duplicates or GT errors, the added points were
joint student+model misses — but the empty-tile audit's own estimate is
that ≈ 50 mounds (≈ 1 % of GT) remain unseen by both channels. The
estimated-correction column, not the point estimate, carries that
residual. See the reference README, Obs 396, and the audit adjudications.


## Pairwise (BH-adjusted)

| pair | ΔMCC | p | BH p | sig |
|---|---:|---:|---:|---|
| IM-k3 vs T03-k4 | +0.0419 | 0.0000 | 0.0000 | yes |
| IM-k3 vs TH7-k3 | +0.0318 | 0.0000 | 0.0000 | yes |
| IM-k3 vs TH7-k4 (carry-forward) | +0.0463 | 0.0000 | 0.0000 | yes |
| IM-k3 vs TM-k3 | +0.0545 | 0.0000 | 0.0000 | yes |
| IM-k3 vs TM-k4 | +0.0713 | 0.0000 | 0.0000 | yes |
| IM-k3 vs TM-n10-k5 (uplift) | +0.0415 | 0.0000 | 0.0000 | yes |
| T03-k3 (oracle) vs T03-k4 | +0.0197 | 0.0000 | 0.0000 | yes |
| T03-k3 (oracle) vs TH7-k4 (carry-forward) | +0.0242 | 0.0000 | 0.0000 | yes |
| T03-k3 (oracle) vs TM-k3 | +0.0323 | 0.0000 | 0.0000 | yes |
| T03-k3 (oracle) vs TM-k4 | +0.0491 | 0.0000 | 0.0000 | yes |
| T03-k4 vs TM-k4 | +0.0294 | 0.0000 | 0.0000 | yes |
| TH7-k3 vs TM-k4 | +0.0394 | 0.0000 | 0.0000 | yes |
| TM-k3 vs TM-k4 | +0.0168 | 0.0000 | 0.0000 | yes |
| TM-k4 vs TM-n10-k5 (uplift) | -0.0297 | 0.0000 | 0.0000 | yes |
| TH7-k3 vs TH7-k4 (carry-forward) | +0.0145 | 0.0002 | 0.0003 | yes |
| TH7-k4 (carry-forward) vs TM-k4 | +0.0249 | 0.0002 | 0.0003 | yes |
| TH7-k3 vs TM-k3 | +0.0226 | 0.0005 | 0.0008 | yes |
| IM-k3 vs T03-k3 (oracle) | +0.0221 | 0.0013 | 0.0020 | yes |
| T03-k3 (oracle) vs TM-n10-k5 (uplift) | +0.0194 | 0.0020 | 0.0029 | yes |
| TM-k3 vs TM-n10-k5 (uplift) | -0.0129 | 0.0129 | 0.0181 | yes |
| T03-k4 vs TM-k3 | +0.0126 | 0.0509 | 0.0679 | ns |
| T03-k4 vs TH7-k3 | -0.0101 | 0.0824 | 0.1049 | ns |
| T03-k3 (oracle) vs TH7-k3 | +0.0097 | 0.0915 | 0.1114 | ns |
| TH7-k3 vs TM-n10-k5 (uplift) | +0.0097 | 0.1339 | 0.1562 | ns |
| TH7-k4 (carry-forward) vs TM-k3 | +0.0081 | 0.2059 | 0.2306 | ns |
| T03-k4 vs TH7-k4 (carry-forward) | +0.0044 | 0.4307 | 0.4638 | ns |
| TH7-k4 (carry-forward) vs TM-n10-k5 (uplift) | -0.0048 | 0.4536 | 0.4704 | ns |
| T03-k4 vs TM-n10-k5 (uplift) | -0.0003 | 0.9598 | 0.9598 | ns |
