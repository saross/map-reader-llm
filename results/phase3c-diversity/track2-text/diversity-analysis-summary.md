# Phase 3c Diversity Analysis

**Generated**: 2026-03-25T07:29:29.265580+00:00  
**Track**: Retest: Phase 3c: H9 Diversity — Track 2 (Text-Only)  
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
| A | 4 | 0.7163 | 0.0119 | 0.7050 | 0.7280 | 557 |
| B | 4 | 0.6862 | 0.0046 | 0.6974 | 0.6753 | 522 |
| D | 4 | 0.7301 | 0.0081 | 0.7227 | 0.7380 | 551 |
| E | 4 | 0.6943 | 0.0111 | 0.6985 | 0.6902 | 533 |

## Comparisons vs Baseline (A)

Paired permutation test on per-replication F1 scores (at each condition's optimal threshold):

| Comparison | ΔF1 | p-value | Significant? |
|------------|----:|--------:|:------------:|
| B vs A | -0.0301 | 0.0610 | No |
| D vs A | +0.0138 | 0.1812 | No |
| E vs A | -0.0221 | 0.0610 | No |

## Per-Replication F1 (at optimal threshold)

| Rep | A (x=4) | B (x=4) | D (x=4) | E (x=4) |
|----:|-----:|-----:|-----:|-----:|
| 1 | 0.7269 | 0.6873 | 0.7395 | 0.7049 |
| 2 | 0.7177 | 0.6876 | 0.7238 | 0.7006 |
| 3 | 0.7030 | 0.6785 | 0.7334 | 0.6966 |
| 4 | 0.7288 | 0.6868 | 0.7198 | 0.6761 |
| 5 | 0.7052 | 0.6907 | 0.7340 | 0.6931 |

## Key Finding

No diversity condition significantly outperforms the identical-pass baseline (A, F1=0.7163). Diversity does not improve consensus voting for this track.

## Methodology

1. For each condition, form replications by taking run_k from each sub-condition
2. Within each pass: deduplicate detections (20 m)
3. Across passes: cluster and count votes (20 m)
4. Apply vote threshold sweep (x=1 to x=5)
5. Evaluate F1 against ground truth (20 m tolerance)
6. Select optimal threshold per condition (maximising mean F1 across replications)
7. Compare conditions using paired permutation test (10000 permutations, two-sided, α=0.05)
