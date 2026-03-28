# Pairwise Permutation Test Results (FDR-Corrected)

Buffer: 20m | Permutations: 10000 | Seed: 42

## Confirmatory (20/26 significant)

### Group 1: PV vs consensus

| Condition A | Condition B | F1_A | F1_B | ΔF1 | p (raw) | p (adj) | Sig |
|---|---|---|---|---|---|---|---|
| Flash HIGH text 16-of-30 + PV | Flash HIGH text 26-of-30 | 0.890 | 0.814 | +0.0761 | 0.0000 | 0.0000 | *** |
| Flash HIGH text 9-of-10 + PV | Flash HIGH text 9-of-10 | 0.856 | 0.797 | +0.0597 | 0.0000 | 0.0000 | *** |
| Flash HIGH text 4-of-5 + PV | Flash HIGH text 5-of-5 | 0.864 | 0.779 | +0.0853 | 0.0000 | 0.0000 | *** |
| Flash HIGH text 4-of-5 + medium vf | Flash HIGH text 5-of-5 | 0.859 | 0.779 | +0.0803 | 0.0000 | 0.0000 | *** |
| Flash HIGH image 3-of-5 + PV | Flash HIGH image 3-of-5 | 0.778 | 0.727 | +0.0509 | 0.0004 | 0.0007 | *** |
| Pro HIGH text 3-of-5 + PV | Pro HIGH text 3-of-5 | 0.849 | 0.840 | +0.0087 | 0.2580 | 0.3049 | ns |
| Text baseline + PV | Single-pass text 5-of-5 | 0.814 | 0.544 | +0.2702 | 0.0000 | 0.0000 | *** |
| Image baseline + PV | Single-pass text 5-of-5 | 0.717 | 0.544 | +0.1727 | 0.0000 | 0.0000 | *** |

### Group 2: Text vs image

| Condition A | Condition B | F1_A | F1_B | ΔF1 | p (raw) | p (adj) | Sig |
|---|---|---|---|---|---|---|---|
| Flash HIGH text 5-of-5 | Flash HIGH image 3-of-5 | 0.779 | 0.727 | +0.0519 | 0.0143 | 0.0196 | * |
| Flash HIGH text 9-of-10 | Flash HIGH image 6-of-10 | 0.797 | 0.740 | +0.0565 | 0.0054 | 0.0078 | ** |
| Flash MIN text 5-of-5 | Flash MIN image 4-of-5 | 0.640 | 0.664 | -0.0242 | 0.3604 | 0.3904 | ns |
| Flash HIGH text 4-of-5 + PV | Flash HIGH image 3-of-5 + PV | 0.864 | 0.778 | +0.0863 | 0.0000 | 0.0000 | *** |

### Group 3: HIGH vs MINIMAL (text N=5)

| Condition A | Condition B | F1_A | F1_B | ΔF1 | p (raw) | p (adj) | Sig |
|---|---|---|---|---|---|---|---|
| Flash HIGH text 5-of-5 | Flash MIN text 5-of-5 | 0.779 | 0.640 | +0.1391 | 0.0000 | 0.0000 | *** |
| Flash HIGH text 9-of-10 | Flash MIN text 10-of-10 | 0.797 | 0.633 | +0.1636 | 0.0000 | 0.0000 | *** |
| Flash HIGH text 26-of-30 | Flash MIN text 29-of-30 | 0.814 | 0.661 | +0.1530 | 0.0000 | 0.0000 | *** |
| Flash HIGH image 3-of-5 | Flash MIN image 4-of-5 | 0.727 | 0.664 | +0.0630 | 0.0003 | 0.0006 | *** |

### Group 4: T=0.7 vs T=1.0 (N=5)

| Condition A | Condition B | F1_A | F1_B | ΔF1 | p (raw) | p (adj) | Sig |
|---|---|---|---|---|---|---|---|
| Flash MIN text T=0.7 5-of-5 | Flash MIN text T=1.0 5-of-5 | 0.640 | 0.471 | +0.1685 | 0.0000 | 0.0000 | *** |
| Flash MIN text T=0.7 10-of-10 | Flash MIN text T=1.0 9-of-10 | 0.633 | 0.462 | +0.1716 | 0.0000 | 0.0000 | *** |
| Flash MIN text T=0.7 29-of-30 | Flash MIN text T=1.0 22-of-30 | 0.661 | 0.467 | +0.1941 | 0.0000 | 0.0000 | *** |

### Group 5: Pro vs Flash (text consensus)

| Condition A | Condition B | F1_A | F1_B | ΔF1 | p (raw) | p (adj) | Sig |
|---|---|---|---|---|---|---|---|
| Pro HIGH text 3-of-5 | Flash HIGH text 5-of-5 | 0.840 | 0.779 | +0.0616 | 0.0042 | 0.0064 | ** |
| Pro HIGH image 3-of-5 | Flash HIGH image 3-of-5 | 0.700 | 0.727 | -0.0271 | 0.2939 | 0.3322 | ns |
| Pro HIGH text 3-of-5 + PV | Flash HIGH text 4-of-5 + PV | 0.849 | 0.864 | -0.0150 | 0.4002 | 0.4162 | ns |

### Group 7: N=10 vs N=5 (HIGH text)

| Condition A | Condition B | F1_A | F1_B | ΔF1 | p (raw) | p (adj) | Sig |
|---|---|---|---|---|---|---|---|
| Flash HIGH text 9-of-10 | Flash HIGH text 5-of-5 | 0.797 | 0.779 | +0.0179 | 0.1404 | 0.1738 | ns |
| Flash HIGH text 26-of-30 | Flash HIGH text 9-of-10 | 0.814 | 0.797 | +0.0174 | 0.0375 | 0.0488 | * |
| Flash MIN text 10-of-10 | Flash MIN text 5-of-5 | 0.633 | 0.640 | -0.0065 | 0.6338 | 0.6338 | ns |
| Flash MIN text 29-of-30 | Flash MIN text 10-of-10 | 0.661 | 0.633 | +0.0280 | 0.0005 | 0.0008 | *** |

## Exploratory (3/6 significant)

### Group 6: Best vs runner-up 1

| Condition A | Condition B | F1_A | F1_B | ΔF1 | p (raw) | p (adj) | Sig |
|---|---|---|---|---|---|---|---|
| Flash HIGH text 16-of-30 + PV | Flash HIGH text 4-of-5 + PV | 0.890 | 0.864 | +0.0261 | 0.0398 | 0.0597 | ns |
| Flash HIGH text 16-of-30 + PV | Flash HIGH text 4-of-5 + medium vf | 0.890 | 0.859 | +0.0310 | 0.0207 | 0.0414 | * |
| Flash HIGH text 16-of-30 + PV | Flash HIGH text 9-of-10 + PV | 0.890 | 0.856 | +0.0338 | 0.0017 | 0.0102 | * |
| Flash HIGH text 16-of-30 + PV | Pro HIGH text 3-of-5 + PV | 0.890 | 0.849 | +0.0411 | 0.0119 | 0.0357 | * |
| Flash HIGH text 4-of-5 + PV | Flash HIGH text 4-of-5 + medium vf | 0.864 | 0.859 | +0.0049 | 0.4701 | 0.4701 | ns |
| Flash HIGH text 4-of-5 + PV | Flash HIGH text 9-of-10 + PV | 0.864 | 0.856 | +0.0077 | 0.4656 | 0.4701 | ns |

## Summary

- **Total comparisons:** 32
- **Significant after FDR:** 23
- **Confirmatory:** 20/26 significant
- **Exploratory:** 3/6 significant
