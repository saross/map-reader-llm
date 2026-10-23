# Pairwise Permutation Test Results (FDR-Corrected)

Buffer: 30m | Permutations: 10000 | Seed: 42

## Confirmatory (18/26 significant)

### Group 1: PV vs consensus

| Condition A | Condition B | F1_A | F1_B | ΔF1 | p (raw) | p (adj) | Sig |
|---|---|---|---|---|---|---|---|
| Flash HIGH text 16-of-30 + PV | Flash HIGH text 26-of-30 | 0.904 | 0.828 | +0.0761 | 0.0000 | 0.0000 | *** |
| Flash HIGH text 9-of-10 + PV | Flash HIGH text 9-of-10 | 0.869 | 0.813 | +0.0562 | 0.0000 | 0.0000 | *** |
| Flash HIGH text 4-of-5 + PV | Flash HIGH text 5-of-5 | 0.891 | 0.791 | +0.1002 | 0.0000 | 0.0000 | *** |
| Flash HIGH text 4-of-5 + medium vf | Flash HIGH text 5-of-5 | 0.885 | 0.791 | +0.0944 | 0.0000 | 0.0000 | *** |
| Flash HIGH image 3-of-5 + PV | Flash HIGH image 3-of-5 | 0.851 | 0.801 | +0.0498 | 0.0003 | 0.0006 | *** |
| Pro HIGH text 3-of-5 + PV | Pro HIGH text 3-of-5 | 0.864 | 0.858 | +0.0066 | 0.3607 | 0.4077 | ns |
| Text baseline + PV | Single-pass text 5-of-5 | 0.832 | 0.557 | +0.2748 | 0.0000 | 0.0000 | *** |
| Image baseline + PV | Single-pass text 5-of-5 | 0.782 | 0.557 | +0.2250 | 0.0000 | 0.0000 | *** |

### Group 2: Text vs image

| Condition A | Condition B | F1_A | F1_B | ΔF1 | p (raw) | p (adj) | Sig |
|---|---|---|---|---|---|---|---|
| Flash HIGH text 5-of-5 | Flash HIGH image 3-of-5 | 0.791 | 0.801 | -0.0107 | 0.5601 | 0.6068 | ns |
| Flash HIGH text 9-of-10 | Flash HIGH image 6-of-10 | 0.813 | 0.814 | -0.0009 | 0.9577 | 0.9577 | ns |
| Flash MIN text 5-of-5 | Flash MIN image 4-of-5 | 0.649 | 0.727 | -0.0776 | 0.0013 | 0.0020 | ** |
| Flash HIGH text 4-of-5 + PV | Flash HIGH image 3-of-5 + PV | 0.891 | 0.851 | +0.0397 | 0.0120 | 0.0173 | * |

### Group 3: HIGH vs MINIMAL (text N=5)

| Condition A | Condition B | F1_A | F1_B | ΔF1 | p (raw) | p (adj) | Sig |
|---|---|---|---|---|---|---|---|
| Flash HIGH text 5-of-5 | Flash MIN text 5-of-5 | 0.791 | 0.649 | +0.1417 | 0.0000 | 0.0000 | *** |
| Flash HIGH text 9-of-10 | Flash MIN text 10-of-10 | 0.813 | 0.643 | +0.1697 | 0.0000 | 0.0000 | *** |
| Flash HIGH text 26-of-30 | Flash MIN text 29-of-30 | 0.828 | 0.672 | +0.1567 | 0.0000 | 0.0000 | *** |
| Flash HIGH image 3-of-5 | Flash MIN image 4-of-5 | 0.801 | 0.727 | +0.0748 | 0.0000 | 0.0000 | *** |

### Group 4: T=0.7 vs T=1.0 (N=5)

| Condition A | Condition B | F1_A | F1_B | ΔF1 | p (raw) | p (adj) | Sig |
|---|---|---|---|---|---|---|---|
| Flash MIN text T=0.7 5-of-5 | Flash MIN text T=1.0 5-of-5 | 0.649 | 0.482 | +0.1667 | 0.0001 | 0.0002 | *** |
| Flash MIN text T=0.7 10-of-10 | Flash MIN text T=1.0 9-of-10 | 0.643 | 0.472 | +0.1711 | 0.0000 | 0.0000 | *** |
| Flash MIN text T=0.7 29-of-30 | Flash MIN text T=1.0 22-of-30 | 0.672 | 0.479 | +0.1923 | 0.0000 | 0.0000 | *** |

### Group 5: Pro vs Flash (text consensus)

| Condition A | Condition B | F1_A | F1_B | ΔF1 | p (raw) | p (adj) | Sig |
|---|---|---|---|---|---|---|---|
| Pro HIGH text 3-of-5 | Flash HIGH text 5-of-5 | 0.858 | 0.791 | +0.0673 | 0.0009 | 0.0015 | ** |
| Pro HIGH image 3-of-5 | Flash HIGH image 3-of-5 | 0.821 | 0.801 | +0.0199 | 0.2971 | 0.3511 | ns |
| Pro HIGH text 3-of-5 + PV | Flash HIGH text 4-of-5 + PV | 0.864 | 0.891 | -0.0263 | 0.1131 | 0.1400 | ns |

### Group 7: N=10 vs N=5 (HIGH text)

| Condition A | Condition B | F1_A | F1_B | ΔF1 | p (raw) | p (adj) | Sig |
|---|---|---|---|---|---|---|---|
| Flash HIGH text 9-of-10 | Flash HIGH text 5-of-5 | 0.813 | 0.791 | +0.0223 | 0.0715 | 0.0930 | ns |
| Flash HIGH text 26-of-30 | Flash HIGH text 9-of-10 | 0.828 | 0.813 | +0.0153 | 0.0668 | 0.0914 | ns |
| Flash MIN text 10-of-10 | Flash MIN text 5-of-5 | 0.643 | 0.649 | -0.0057 | 0.6740 | 0.7010 | ns |
| Flash MIN text 29-of-30 | Flash MIN text 10-of-10 | 0.672 | 0.643 | +0.0283 | 0.0005 | 0.0009 | *** |

## Exploratory (3/6 significant)

### Group 6: Best vs runner-up 1

| Condition A | Condition B | F1_A | F1_B | ΔF1 | p (raw) | p (adj) | Sig |
|---|---|---|---|---|---|---|---|
| Flash HIGH text 16-of-30 + PV | Flash HIGH text 4-of-5 + PV | 0.904 | 0.891 | +0.0136 | 0.2098 | 0.2518 | ns |
| Flash HIGH text 16-of-30 + PV | Flash HIGH text 4-of-5 + medium vf | 0.904 | 0.885 | +0.0194 | 0.1162 | 0.1743 | ns |
| Flash HIGH text 16-of-30 + PV | Flash HIGH text 9-of-10 + PV | 0.904 | 0.869 | +0.0352 | 0.0009 | 0.0054 | ** |
| Flash HIGH text 16-of-30 + PV | Pro HIGH text 3-of-5 + PV | 0.904 | 0.864 | +0.0399 | 0.0106 | 0.0212 | * |
| Flash HIGH text 4-of-5 + PV | Flash HIGH text 4-of-5 + medium vf | 0.891 | 0.885 | +0.0058 | 0.4334 | 0.4334 | ns |
| Flash HIGH text 4-of-5 + PV | Flash HIGH text 9-of-10 + PV | 0.891 | 0.869 | +0.0217 | 0.0097 | 0.0212 | * |

## Summary

- **Total comparisons:** 32
- **Significant after FDR:** 21
- **Confirmatory:** 18/26 significant
- **Exploratory:** 3/6 significant
