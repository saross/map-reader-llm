# Pairwise Permutation Test Results (FDR-Corrected)

Buffer: 20m | Permutations: 10000 | Seed: 42

## Confirmatory (20/26 significant)

### Group 1: PV vs consensus

| Condition A | Condition B | F1_A | F1_B | ΔF1 | p (raw) | p (adj) | Sig |
|---|---|---|---|---|---|---|---|
| Flash HIGH text 16-of-30 + PV | Flash HIGH text 26-of-30 | 0.890 | 0.816 | +0.0737 | 0.0000 | 0.0000 | *** |
| Flash HIGH text 9-of-10 + PV | Flash HIGH text 9-of-10 | 0.856 | 0.799 | +0.0573 | 0.0000 | 0.0000 | *** |
| Flash HIGH text 4-of-5 + PV | Flash HIGH text 5-of-5 | 0.864 | 0.781 | +0.0829 | 0.0000 | 0.0000 | *** |
| Flash HIGH text 4-of-5 + medium vf | Flash HIGH text 5-of-5 | 0.859 | 0.781 | +0.0780 | 0.0000 | 0.0000 | *** |
| Flash HIGH image 3-of-5 + PV | Flash HIGH image 3-of-5 | 0.778 | 0.729 | +0.0488 | 0.0004 | 0.0007 | *** |
| Pro HIGH text 3-of-5 + PV | Pro HIGH text 3-of-5 | 0.849 | 0.843 | +0.0062 | 0.4128 | 0.4293 | ns |
| Text baseline + PV | Single-pass text 5-of-5 | 0.814 | 0.547 | +0.2671 | 0.0000 | 0.0000 | *** |
| Image baseline + PV | Single-pass text 5-of-5 | 0.717 | 0.547 | +0.1695 | 0.0000 | 0.0000 | *** |

### Group 2: Text vs image

| Condition A | Condition B | F1_A | F1_B | ΔF1 | p (raw) | p (adj) | Sig |
|---|---|---|---|---|---|---|---|
| Flash HIGH text 5-of-5 | Flash HIGH image 3-of-5 | 0.781 | 0.729 | +0.0522 | 0.0141 | 0.0193 | * |
| Flash HIGH text 9-of-10 | Flash HIGH image 6-of-10 | 0.799 | 0.742 | +0.0566 | 0.0050 | 0.0072 | ** |
| Flash MIN text 5-of-5 | Flash MIN image 4-of-5 | 0.642 | 0.666 | -0.0244 | 0.3554 | 0.4018 | ns |
| Flash HIGH text 4-of-5 + PV | Flash HIGH image 3-of-5 + PV | 0.864 | 0.778 | +0.0863 | 0.0000 | 0.0000 | *** |

### Group 3: HIGH vs MINIMAL (text N=5)

| Condition A | Condition B | F1_A | F1_B | ΔF1 | p (raw) | p (adj) | Sig |
|---|---|---|---|---|---|---|---|
| Flash HIGH text 5-of-5 | Flash MIN text 5-of-5 | 0.781 | 0.642 | +0.1396 | 0.0000 | 0.0000 | *** |
| Flash HIGH text 9-of-10 | Flash MIN text 10-of-10 | 0.799 | 0.635 | +0.1639 | 0.0000 | 0.0000 | *** |
| Flash HIGH text 26-of-30 | Flash MIN text 29-of-30 | 0.816 | 0.663 | +0.1533 | 0.0000 | 0.0000 | *** |
| Flash HIGH image 3-of-5 | Flash MIN image 4-of-5 | 0.729 | 0.666 | +0.0630 | 0.0003 | 0.0006 | *** |

### Group 4: T=0.7 vs T=1.0 (N=5)

| Condition A | Condition B | F1_A | F1_B | ΔF1 | p (raw) | p (adj) | Sig |
|---|---|---|---|---|---|---|---|
| Flash MIN text T=0.7 5-of-5 | Flash MIN text T=1.0 5-of-5 | 0.642 | 0.474 | +0.1676 | 0.0000 | 0.0000 | *** |
| Flash MIN text T=0.7 10-of-10 | Flash MIN text T=1.0 9-of-10 | 0.635 | 0.464 | +0.1710 | 0.0000 | 0.0000 | *** |
| Flash MIN text T=0.7 29-of-30 | Flash MIN text T=1.0 22-of-30 | 0.663 | 0.469 | +0.1938 | 0.0000 | 0.0000 | *** |

### Group 5: Pro vs Flash (text consensus)

| Condition A | Condition B | F1_A | F1_B | ΔF1 | p (raw) | p (adj) | Sig |
|---|---|---|---|---|---|---|---|
| Pro HIGH text 3-of-5 | Flash HIGH text 5-of-5 | 0.843 | 0.781 | +0.0617 | 0.0041 | 0.0063 | ** |
| Pro HIGH image 3-of-5 | Flash HIGH image 3-of-5 | 0.700 | 0.729 | -0.0292 | 0.2630 | 0.3108 | ns |
| Pro HIGH text 3-of-5 + PV | Flash HIGH text 4-of-5 + PV | 0.849 | 0.864 | -0.0150 | 0.4002 | 0.4293 | ns |

### Group 7: N=10 vs N=5 (HIGH text)

| Condition A | Condition B | F1_A | F1_B | ΔF1 | p (raw) | p (adj) | Sig |
|---|---|---|---|---|---|---|---|
| Flash HIGH text 9-of-10 | Flash HIGH text 5-of-5 | 0.799 | 0.781 | +0.0179 | 0.1413 | 0.1749 | ns |
| Flash HIGH text 26-of-30 | Flash HIGH text 9-of-10 | 0.816 | 0.799 | +0.0174 | 0.0357 | 0.0464 | * |
| Flash MIN text 10-of-10 | Flash MIN text 5-of-5 | 0.635 | 0.642 | -0.0064 | 0.6431 | 0.6431 | ns |
| Flash MIN text 29-of-30 | Flash MIN text 10-of-10 | 0.663 | 0.635 | +0.0280 | 0.0005 | 0.0008 | *** |

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
