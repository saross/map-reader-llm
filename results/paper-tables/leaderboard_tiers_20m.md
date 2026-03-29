# Leaderboard Tier Clustering (20m buffer, FDR-corrected)

Conditions within the same tier are statistically indistinguishable
(all pairwise adjusted p-values >= 0.05). Based on 253 pairwise
permutation tests (10,000 permutations, seed 42) among 23 of 25
leaderboard conditions, FDR-corrected at q=0.05.

Two conditions excluded: FH image N=10 (7-of-10) and FM image N=10
(8-of-10) — their optimal thresholds at 20m differ from the
condition-registry built for 30m. Both have N=5 variants included.

## Tier 1 (F1: 0.890)

| Condition | F1 | P | R |
|---|---|---|---|
| FH text 16/30 + PV (min vf) | 0.890 | 0.915 | 0.867 |

## Tier 2 (F1: 0.840–0.864)

| Condition | F1 | P | R |
|---|---|---|---|
| FH text 4/5 + PV (min vf) | 0.864 | 0.915 | 0.818 |
| FH text 4/5 + PV (med vf) | 0.859 | 0.878 | 0.841 |
| FH text 9/10 + PV (min vf) | 0.856 | 0.957 | 0.775 |
| Pro H text 3/5 + PV (min vf) | 0.849 | 0.957 | 0.763 |
| Pro H text 3/5 (consensus) | 0.840 | 0.918 | 0.775 |

## Tier 3 (F1: 0.778–0.814)

| Condition | F1 | P | R |
|---|---|---|---|
| Text baseline + PV | 0.814 | 0.789 | 0.841 |
| FH text 26/30 (consensus) | 0.814 | 0.834 | 0.795 |
| FH image 3/5 + PV | 0.778 | 0.800 | 0.756 |

## Tier 4 (F1: 0.779–0.797)

| Condition | F1 | P | R |
|---|---|---|---|
| FH text 9/10 (consensus) | 0.797 | 0.800 | 0.793 |
| FH text 5/5 (consensus) | 0.779 | 0.798 | 0.761 |

## Tier 5 (F1: 0.700–0.727)

| Condition | F1 | P | R |
|---|---|---|---|
| FH image 3/5 (consensus) | 0.727 | 0.676 | 0.786 |
| Image baseline + PV | 0.717 | 0.663 | 0.779 |
| Pro H image 3/5 (consensus) | 0.700 | 0.673 | 0.729 |

## Tier 6 (F1: 0.640–0.664)

| Condition | F1 | P | R |
|---|---|---|---|
| FM image 4/5 | 0.664 | 0.608 | 0.731 |
| FM text T=0.7 29/30 | 0.661 | 0.602 | 0.733 |
| FM text T=0.7 5/5 | 0.640 | 0.533 | 0.800 |

## Tier 7 (F1: 0.633)

| Condition | F1 | P | R |
|---|---|---|---|
| FM text T=0.7 10/10 | 0.633 | 0.562 | 0.724 |

## Tier 8 (F1: 0.471–0.552)

| Condition | F1 | P | R |
|---|---|---|---|
| Single-pass T=0 10/10 | 0.552 | 0.410 | 0.846 |
| Single-pass T=0 5/5 | 0.544 | 0.396 | 0.867 |
| FM text T=1.0 5/5 | 0.471 | 0.583 | 0.395 |

## Tier 9 (F1: 0.462–0.467)

| Condition | F1 | P | R |
|---|---|---|---|
| FM text T=1.0 22/30 | 0.467 | 0.499 | 0.439 |
| FM text T=1.0 9/10 | 0.462 | 0.545 | 0.400 |

## Key comparison with 30m tiers

At 30m, the top 3 conditions formed a single indistinguishable tier.
At 20m, the best condition (FH text 16/30 + PV) **separates as a
solitary Tier 1**, with the next 5 conditions forming Tier 2. This
confirms 20m provides greater discrimination, as expected from the
tighter spatial tolerance.

## Statistics

- 253 pairwise comparisons (23 conditions, 2 excluded for registry mismatch)
- 213/253 significant after FDR correction (q=0.05)
- 9 tiers identified via greedy clique-based clustering
