# 55-map generalisation leaderboard — reference r2 @ 50 m

> Working buffer 50 m per the noise-floor derivation (`results/working-precision/55maps-csr-noise-floor.json`). Round-robin tile-swap permutation (10k, seed 42) + BH-FDR q=0.05 + greedy-clique tiers; 24/28 pairs significant.

| rank | cell | tier | F1@50 | 95% CI | P@50 | R@50 | tile-MCC | n |
|---:|---|---:|---:|---|---:|---:|---:|---:|
| 1 | T03-k3 (oracle) | 1 | 0.8387 | [0.8297, 0.8472] | 0.8483 | 0.8292 | 0.689 | 4905 |
| 2 | TH7-k3 | 1 | 0.8380 | [0.8287, 0.8467] | 0.8583 | 0.8187 | 0.679 | 4786 |
| 3 | T03-k4 | 2 | 0.8294 | [0.8199, 0.8384] | 0.8931 | 0.7742 | 0.669 | 4350 |
| 4 | TM-n10-k5 (uplift) | 2 | 0.8274 | [0.8174, 0.8367] | 0.8897 | 0.7732 | 0.669 | 4361 |
| 5 | TH7-k4 (carry-forward) | 3 | 0.8162 | [0.8059, 0.8261] | 0.8999 | 0.7467 | 0.665 | 4164 |
| 6 | TM-k3 | 3 | 0.8102 | [0.7998, 0.8202] | 0.8801 | 0.7505 | 0.656 | 4279 |
| 7 | IM-k3 | 4 | 0.8008 | [0.7907, 0.8102] | 0.8297 | 0.7738 | 0.711 | 4680 |
| 8 | TM-k4 | 5 | 0.7826 | [0.7713, 0.7936] | 0.8994 | 0.6927 | 0.640 | 3865 |

## Reading this board

**Confidence intervals vs significance.** The 95% intervals in the board table
are *marginal* per-cell percentile bootstrap intervals; the significance tests are
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

