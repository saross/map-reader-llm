# Phase 3c Diversity Analysis

**Generated**: 2026-03-08T05:24:47.305466+00:00  
**Track**: Phase 3c: H9 Diversity — Track 2 (Text-Only)  
**Bootstrap iterations**: 1000  
**Buffer (spatial tolerance)**: 20 m  
**Permutation test iterations**: 10000

## Experimental Design

| Condition | Diversity | Sub-conditions |
|-----------|-----------|----------------|
| A | none (baseline) | h9-A-p1, h9-A-p2, h9-A-p3, h9-A-p4, h9-A-p5 |
| B | text | h9-B-v1, h9-B-v2, h9-B-v3, h9-B-v4, h9-B-v5 |
| D | temperature | h9-D-t1, h9-D-t2, h9-D-t3, h9-D-t4, h9-D-t5 |
| E | text, temperature | h9-E-p1, h9-E-p2, h9-E-p3, h9-E-p4, h9-E-p5 |

## Per-Condition Optima

Best threshold (maximising mean F1 across replications):

| Condition | x* | F1 | ±SD | P | R | n_det |
|-----------|---:|----:|----:|---:|---:|------:|
| A | 4 | 0.7026 | 0.0376 | 0.7204 | 0.6866 | 92 |
| B | 4 | 0.6681 | 0.0631 | 0.7214 | 0.6227 | 84 |
| D | 4 | 0.6690 | 0.0611 | 0.6752 | 0.6639 | 95 |
| E | 4 | 0.6649 | 0.0414 | 0.7218 | 0.6165 | 83 |

## Comparisons vs Baseline (A)

Paired permutation test on per-replication F1 scores (at each condition's optimal threshold):

| Comparison | ΔF1 | p-value | Significant? |
|------------|----:|--------:|:------------:|
| B vs A | -0.0345 | 0.1208 | No |
| D vs A | -0.0336 | 0.4957 | No |
| E vs A | -0.0377 | 0.2450 | No |

## Per-Replication F1 (at optimal threshold)

| Rep | A (x=4) | B (x=4) | D (x=4) | E (x=4) |
|----:|-----:|-----:|-----:|-----:|
| 1 | 0.7435 | 0.7487 | 0.6667 | 0.6556 |
| 2 | 0.6559 | 0.6369 | 0.6559 | 0.6145 |
| 3 | 0.7179 | 0.6780 | 0.5789 | 0.6813 |
| 4 | 0.6703 | 0.5810 | 0.6984 | 0.7253 |
| 5 | 0.7254 | 0.6961 | 0.7449 | 0.6477 |

## Key Finding

No diversity condition significantly outperforms the identical-pass baseline (A, F1=0.7026). Diversity does not improve consensus voting for this track.

## Methodology

1. For each condition, form replications by taking run_k from each sub-condition
2. Within each pass: deduplicate detections (20 m)
3. Across passes: cluster and count votes (20 m)
4. Apply vote threshold sweep (x=1 to x=5)
5. Evaluate F1 against ground truth (20 m tolerance)
6. Select optimal threshold per condition (maximising mean F1 across replications)
7. Compare conditions using paired permutation test (10000 permutations, two-sided, α=0.05)
