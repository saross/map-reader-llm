# Leaderboard Tier Clustering (20m buffer, FDR-corrected)

Conditions within the same tier are statistically indistinguishable
(all pairwise adjusted p-values >= 0.05). Based on 325 pairwise
permutation tests (10,000 permutations, seed 42) among all 26
leaderboard conditions, FDR-corrected at q=0.05.

MCC, sensitivity, and specificity are tile-level metrics (does this
384px tile contain any mound?). These are independent of spatial buffer.
Two conditions (#13, #17) have MCC from the nearest evaluated threshold,
marked with ~.

**Scope unification note (2026-04-24)**: this document uses phase3a
condition labels (e.g. "FH text 16/30 + PV (min vf)") and is not a mirror
of `results/leaderboard/era2/leaderboard_tiers_20m.md`, which uses the
h11-series cell naming. The Session 78 gold-standard-v2 scope-unified cell
at Era 2 (487-tile) scope reports F1=0.854 at 20 m
(`results/leaderboard/cells/gold-standard-v2-greedy-v1-487tile.json`).
It would sit in Tier 2 here on F1 but is not inserted as a distinct row
because the tier discussion focuses on phase3a matrix conditions with
matched pairwise permutation statistics. The Era 3 (327-tile) scope-pair
sibling (`gold-standard-v2-greedy-v1-327tile.json`) is intentionally
preserved for comparability with the Era 3 h8-v2 / h10-v2 / h12-v2
library-design artefacts.

## Tier 1 (F1: 0.890)

| # | Condition | F1 | P | R | MCC | MCC CI | Sens | Spec |
|--:|---|:---:|:---:|:---:|:---:|---|:---:|:---:|
| 1 | FH text 16/30 + PV (min vf) | 0.890 | 0.915 | 0.867 | 0.790 | [0.733, 0.840] | 0.821 | 0.957 |

## Tier 2 (F1: 0.836–0.864)

| # | Condition | F1 | P | R | MCC | MCC CI | Sens | Spec |
|--:|---|:---:|:---:|:---:|:---:|---|:---:|:---:|
| 2 | FH text 4/5 + PV (min vf) | 0.864 | 0.915 | 0.818 | 0.769 | [0.716, 0.820] | 0.786 | 0.965 |
| 3 | FH text 4/5 + PV (med vf) | 0.859 | 0.878 | 0.841 | 0.739 | [0.679, 0.793] | 0.804 | 0.926 |
| 4 | FH text 9/10 + PV (min vf) | 0.856 | 0.957 | 0.775 | 0.749 | [0.696, 0.797] | 0.738 | 0.981 |
| 5 | Pro H text 3/5 + PV (min vf) | 0.849 | 0.957 | 0.763 | 0.730 | [0.676, 0.783] | 0.703 | 0.988 |
| 6 | Pro H text 3/5 (N=5 cons.) | 0.840 | 0.918 | 0.775 | 0.736 | [0.682, 0.788] | 0.747 | 0.965 |
| 7 | Pro H text 6/10 (N=10 cons.) | 0.837 | 0.921 | 0.767 | 0.710 | [0.654, 0.764] | 0.703 | 0.973 |

## Tier 3 (F1: 0.778–0.814)

| # | Condition | F1 | P | R | MCC | MCC CI | Sens | Spec |
|--:|---|:---:|:---:|:---:|:---:|---|:---:|:---:|
| 8 | Text baseline + PV | 0.814 | 0.789 | 0.841 | 0.833 | [0.783, 0.877] | 0.869 | 0.957 |
| 9 | FH text 26/30 (consensus) | 0.814 | 0.834 | 0.795 | 0.620 | [0.549, 0.691] | 0.777 | 0.841 |
| 10 | FH image 3/5 + PV | 0.778 | 0.800 | 0.756 | 0.827 | [0.777, 0.873] | 0.847 | 0.969 |

## Tier 4 (F1: 0.779–0.797)

| # | Condition | F1 | P | R | MCC | MCC CI | Sens | Spec |
|--:|---|:---:|:---:|:---:|:---:|---|:---:|:---:|
| 11 | FH text 9/10 (consensus) | 0.797 | 0.800 | 0.793 | 0.621 | [0.545, 0.691] | 0.795 | 0.826 |
| 12 | FH text 5/5 (consensus) | 0.779 | 0.798 | 0.761 | 0.600 | [0.529, 0.671] | 0.769 | 0.830 |

## Tier 5 (F1: 0.700–0.750)

| # | Condition | F1 | P | R | MCC | MCC CI | Sens | Spec |
|--:|---|:---:|:---:|:---:|:---:|---|:---:|:---:|
| 13 | FH image 7/10 (consensus) | 0.750 | 0.778 | 0.724 | ~0.675 | [0.604, 0.736] | 0.838 | 0.837 |
| 14 | FH image 3/5 (consensus) | 0.727 | 0.676 | 0.786 | 0.665 | [0.598, 0.724] | 0.856 | 0.810 |
| 15 | Image baseline + PV | 0.717 | 0.663 | 0.779 | 0.877 | [0.833, 0.919] | 0.943 | 0.934 |
| 16 | Pro H image 3/5 (consensus) | 0.700 | 0.673 | 0.729 | 0.761 | [0.706, 0.816] | 0.843 | 0.915 |

## Tier 6 (F1: 0.640–0.680)

| # | Condition | F1 | P | R | MCC | MCC CI | Sens | Spec |
|--:|---|:---:|:---:|:---:|:---:|---|:---:|:---:|
| 17 | FM image 8/10 (consensus) | 0.680 | 0.640 | 0.726 | ~0.361 | [0.283, 0.433] | 0.860 | 0.477 |
| 18 | FM image 4/5 (consensus) | 0.664 | 0.608 | 0.731 | 0.390 | [0.310, 0.469] | 0.843 | 0.531 |
| 19 | FM text T=0.7 29/30 | 0.661 | 0.602 | 0.733 | 0.381 | [0.302, 0.460] | 0.817 | 0.554 |
| 20 | FM text T=0.7 5/5 | 0.640 | 0.533 | 0.800 | 0.315 | [0.230, 0.395] | 0.860 | 0.426 |

## Tier 7 (F1: 0.633)

| # | Condition | F1 | P | R | MCC | MCC CI | Sens | Spec |
|--:|---|:---:|:---:|:---:|:---:|---|:---:|:---:|
| 21 | FM text T=0.7 10/10 | 0.633 | 0.562 | 0.724 | 0.366 | [0.284, 0.444] | 0.834 | 0.516 |

## Tier 8 (F1: 0.471–0.552)

| # | Condition | F1 | P | R | MCC | MCC CI | Sens | Spec |
|--:|---|:---:|:---:|:---:|:---:|---|:---:|:---:|
| 22 | Single-pass T=0 10/10 | 0.552 | 0.410 | 0.846 | 0.212 | [0.126, 0.293] | 0.913 | 0.248 |
| 23 | Single-pass T=0 5/5 | 0.544 | 0.396 | 0.867 | 0.178 | [0.096, 0.255] | 0.926 | 0.198 |
| 24 | FM text T=1.0 5/5 | 0.471 | 0.583 | 0.395 | 0.257 | [0.176, 0.338] | 0.454 | 0.787 |

## Tier 9 (F1: 0.462–0.467)

| # | Condition | F1 | P | R | MCC | MCC CI | Sens | Spec |
|--:|---|:---:|:---:|:---:|:---:|---|:---:|:---:|
| 25 | FM text T=1.0 22/30 | 0.467 | 0.499 | 0.439 | 0.208 | [0.122, 0.298] | 0.498 | 0.705 |
| 26 | FM text T=1.0 9/10 | 0.462 | 0.545 | 0.400 | 0.212 | [0.122, 0.303] | 0.467 | 0.736 |

## Statistics

- 325 pairwise comparisons (all 26 leaderboard conditions)
- 265/325 significant after FDR correction (q=0.05)
- 9 tiers identified via greedy clique-based clustering
- MCC values marked with ~ are from the nearest evaluated consensus
  threshold; the difference is minor
