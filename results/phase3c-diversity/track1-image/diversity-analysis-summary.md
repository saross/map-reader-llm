# Phase 3c Diversity Analysis

**Generated**: 2026-03-25T07:28:36.787798+00:00  
**Track**: Retest: Phase 3c: H9 Diversity — Track 1 (Image)  
**Bootstrap iterations**: 1000  
**Buffer (spatial tolerance)**: 20 m  
**Permutation test iterations**: 10000

## Experimental Design

| Condition | Diversity | Sub-conditions |
|-----------|-----------|----------------|
| A | none (baseline) | h9-A-p1, h9-A-p2, h9-A-p3, h9-A-p4, h9-A-p5 |
| B | text | h9-B-v1, h9-B-v2, h9-B-v3, h9-B-v4, h9-B-v5 |
| C | image | h9-C-img1, h9-C-img2, h9-C-img3, h9-C-img4, h9-C-img5 |
| D | temperature | h9-D-t1, h9-D-t2, h9-D-t3, h9-D-t4, h9-D-t5 |
| E | text, image, temperature | h9-E-p1, h9-E-p2, h9-E-p3, h9-E-p4, h9-E-p5 |

## Per-Condition Optima

Best threshold (maximising mean F1 across replications):

| Condition | x* | F1 | ±SD | P | R | n_det |
|-----------|---:|----:|----:|---:|---:|------:|
| A | 3 | 0.6640 | 0.0153 | 0.6765 | 0.6519 | 519 |
| B | 3 | 0.6682 | 0.0134 | 0.6828 | 0.6542 | 516 |
| C | 3 | 0.6713 | 0.0176 | 0.6910 | 0.6527 | 509 |
| D | 3 | 0.6691 | 0.0143 | 0.6800 | 0.6586 | 522 |
| E | 3 | 0.6709 | 0.0082 | 0.6909 | 0.6519 | 509 |

## Comparisons vs Baseline (A)

Paired permutation test on per-replication F1 scores (at each condition's optimal threshold):

| Comparison | ΔF1 | p-value | Significant? |
|------------|----:|--------:|:------------:|
| B vs A | +0.0042 | 0.6893 | No |
| C vs A | +0.0073 | 0.6213 | No |
| D vs A | +0.0052 | 0.3750 | No |
| E vs A | +0.0069 | 0.3754 | No |

## Per-Replication F1 (at optimal threshold)

| Rep | A (x=3) | B (x=3) | C (x=3) | D (x=3) | E (x=3) |
|----:|-----:|-----:|-----:|-----:|-----:|
| 1 | 0.6559 | 0.6641 | 0.6802 | 0.6685 | 0.6698 |
| 2 | 0.6554 | 0.6880 | 0.6628 | 0.6705 | 0.6781 |
| 3 | 0.6528 | 0.6534 | 0.6978 | 0.6528 | 0.6571 |
| 4 | 0.6898 | 0.6743 | 0.6610 | 0.6916 | 0.6750 |
| 5 | 0.6660 | 0.6610 | 0.6546 | 0.6623 | 0.6743 |

## Key Finding

No diversity condition significantly outperforms the identical-pass baseline (A, F1=0.6640). Diversity does not improve consensus voting for this track.

## Methodology

1. For each condition, form replications by taking run_k from each sub-condition
2. Within each pass: deduplicate detections (20 m)
3. Across passes: cluster and count votes (20 m)
4. Apply vote threshold sweep (x=1 to x=5)
5. Evaluate F1 against ground truth (20 m tolerance)
6. Select optimal threshold per condition (maximising mean F1 across replications)
7. Compare conditions using paired permutation test (10000 permutations, two-sided, α=0.05)
