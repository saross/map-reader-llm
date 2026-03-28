# Pairwise Permutation Test Results (FDR-Corrected)

Buffer: 30m | Permutations: 10000 | Seed: 42

## Confirmatory (18/26 significant)

### Group 1: PV vs consensus

| Condition A | Condition B | F1_A | F1_B | ΔF1 | p (raw) | p (adj) | Sig |
|---|---|---|---|---|---|---|---|
| Flash HIGH text 16-of-30 + PV | Flash HIGH text 26-of-30 | 0.904 | 0.826 | +0.0785 | 0.0000 | 0.0000 | *** |
| Flash HIGH text 9-of-10 + PV | Flash HIGH text 9-of-10 | 0.869 | 0.811 | +0.0585 | 0.0000 | 0.0000 | *** |
| Flash HIGH text 4-of-5 + PV | Flash HIGH text 5-of-5 | 0.891 | 0.788 | +0.1025 | 0.0000 | 0.0000 | *** |
| Flash HIGH text 4-of-5 + medium vf | Flash HIGH text 5-of-5 | 0.885 | 0.788 | +0.0967 | 0.0000 | 0.0000 | *** |
| Flash HIGH image 3-of-5 + PV | Flash HIGH image 3-of-5 | 0.851 | 0.799 | +0.0519 | 0.0002 | 0.0004 | *** |
| Pro HIGH text 3-of-5 + PV | Pro HIGH text 3-of-5 | 0.864 | 0.855 | +0.0091 | 0.2174 | 0.2569 | ns |
| Text baseline + PV | Single-pass text 5-of-5 | 0.832 | 0.554 | +0.2779 | 0.0000 | 0.0000 | *** |
| Image baseline + PV | Single-pass text 5-of-5 | 0.782 | 0.554 | +0.2281 | 0.0000 | 0.0000 | *** |

### Group 2: Text vs image

| Condition A | Condition B | F1_A | F1_B | ΔF1 | p (raw) | p (adj) | Sig |
|---|---|---|---|---|---|---|---|
| Flash HIGH text 5-of-5 | Flash HIGH image 3-of-5 | 0.788 | 0.799 | -0.0109 | 0.5589 | 0.6055 | ns |
| Flash HIGH text 9-of-10 | Flash HIGH image 6-of-10 | 0.811 | 0.812 | -0.0010 | 0.9561 | 0.9561 | ns |
| Flash MIN text 5-of-5 | Flash MIN image 4-of-5 | 0.647 | 0.724 | -0.0774 | 0.0013 | 0.0020 | ** |
| Flash HIGH text 4-of-5 + PV | Flash HIGH image 3-of-5 + PV | 0.891 | 0.851 | +0.0397 | 0.0120 | 0.0173 | * |

### Group 3: HIGH vs MINIMAL (text N=5)

| Condition A | Condition B | F1_A | F1_B | ΔF1 | p (raw) | p (adj) | Sig |
|---|---|---|---|---|---|---|---|
| Flash HIGH text 5-of-5 | Flash MIN text 5-of-5 | 0.788 | 0.647 | +0.1412 | 0.0000 | 0.0000 | *** |
| Flash HIGH text 9-of-10 | Flash MIN text 10-of-10 | 0.811 | 0.641 | +0.1694 | 0.0000 | 0.0000 | *** |
| Flash HIGH text 26-of-30 | Flash MIN text 29-of-30 | 0.826 | 0.669 | +0.1565 | 0.0000 | 0.0000 | *** |
| Flash HIGH image 3-of-5 | Flash MIN image 4-of-5 | 0.799 | 0.724 | +0.0747 | 0.0000 | 0.0000 | *** |

### Group 4: T=0.7 vs T=1.0 (N=5)

| Condition A | Condition B | F1_A | F1_B | ΔF1 | p (raw) | p (adj) | Sig |
|---|---|---|---|---|---|---|---|
| Flash MIN text T=0.7 5-of-5 | Flash MIN text T=1.0 5-of-5 | 0.647 | 0.479 | +0.1676 | 0.0001 | 0.0002 | *** |
| Flash MIN text T=0.7 10-of-10 | Flash MIN text T=1.0 9-of-10 | 0.641 | 0.469 | +0.1717 | 0.0000 | 0.0000 | *** |
| Flash MIN text T=0.7 29-of-30 | Flash MIN text T=1.0 22-of-30 | 0.669 | 0.477 | +0.1927 | 0.0000 | 0.0000 | *** |

### Group 5: Pro vs Flash (text consensus)

| Condition A | Condition B | F1_A | F1_B | ΔF1 | p (raw) | p (adj) | Sig |
|---|---|---|---|---|---|---|---|
| Pro HIGH text 3-of-5 | Flash HIGH text 5-of-5 | 0.855 | 0.788 | +0.0671 | 0.0010 | 0.0016 | ** |
| Pro HIGH image 3-of-5 | Flash HIGH image 3-of-5 | 0.821 | 0.799 | +0.0220 | 0.2507 | 0.2834 | ns |
| Pro HIGH text 3-of-5 + PV | Flash HIGH text 4-of-5 + PV | 0.864 | 0.891 | -0.0263 | 0.1131 | 0.1400 | ns |

### Group 7: N=10 vs N=5 (HIGH text)

| Condition A | Condition B | F1_A | F1_B | ΔF1 | p (raw) | p (adj) | Sig |
|---|---|---|---|---|---|---|---|
| Flash HIGH text 9-of-10 | Flash HIGH text 5-of-5 | 0.811 | 0.788 | +0.0224 | 0.0607 | 0.0831 | ns |
| Flash HIGH text 26-of-30 | Flash HIGH text 9-of-10 | 0.826 | 0.811 | +0.0153 | 0.0671 | 0.0872 | ns |
| Flash MIN text 10-of-10 | Flash MIN text 5-of-5 | 0.641 | 0.647 | -0.0059 | 0.6704 | 0.6972 | ns |
| Flash MIN text 29-of-30 | Flash MIN text 10-of-10 | 0.669 | 0.641 | +0.0282 | 0.0005 | 0.0009 | *** |

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
