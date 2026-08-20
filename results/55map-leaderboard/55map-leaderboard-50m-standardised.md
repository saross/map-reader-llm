# 55-map generalisation leaderboard — standardised reference @ 50 m

> Working buffer 50 m per the noise-floor derivation (`results/working-precision/55maps-csr-noise-floor.json`). Round-robin tile-swap permutation (10k, seed 42) + BH-FDR q=0.05 + greedy-clique tiers; 24/28 pairs significant.

| rank | cell | tier | F1@50 | 95% CI | P@50 | R@50 | tile-MCC | n |
|---:|---|---:|---:|---|---:|---:|---:|---:|
| 1 | T03-k3 (oracle) | 1 | 0.8393 | [0.8304, 0.8479] | 0.8483 | 0.8305 | 0.689 | 4905 |
| 2 | TH7-k3 | 1 | 0.8387 | [0.8297, 0.8475] | 0.8583 | 0.8200 | 0.680 | 4786 |
| 3 | T03-k4 | 2 | 0.8303 | [0.8210, 0.8394] | 0.8933 | 0.7756 | 0.669 | 4350 |
| 4 | TM-n10-k5 (uplift) | 2 | 0.8279 | [0.8181, 0.8374] | 0.8895 | 0.7743 | 0.671 | 4361 |
| 5 | TH7-k4 (carry-forward) | 3 | 0.8169 | [0.8066, 0.8268] | 0.8999 | 0.7479 | 0.665 | 4164 |
| 6 | TM-k3 | 3 | 0.8109 | [0.8006, 0.8210] | 0.8801 | 0.7517 | 0.657 | 4279 |
| 7 | IM-k3 | 4 | 0.8010 | [0.7911, 0.8105] | 0.8293 | 0.7747 | 0.712 | 4680 |
| 8 | TM-k4 | 5 | 0.7833 | [0.7722, 0.7943] | 0.8994 | 0.6938 | 0.640 | 3865 |

## Reading this board

**Confidence intervals vs significance.** The 95% intervals in the board table
are *marginal* per-cell percentile bootstrap intervals; the significance tests are
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
