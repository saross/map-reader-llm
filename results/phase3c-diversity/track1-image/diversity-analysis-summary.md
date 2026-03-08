# Phase 3c Diversity Analysis

**Generated**: 2026-03-08T05:51:18.273803+00:00  
**Track**: Phase 3c: H9 Diversity — Track 1 (Image)  
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
| A | 3 | 0.6437 | 0.0406 | 0.6618 | 0.6268 | 92 |
| B | 3 | 0.6344 | 0.0700 | 0.6523 | 0.6186 | 92 |
| C | 3 | 0.6472 | 0.0084 | 0.6816 | 0.6165 | 88 |
| D | 3 | 0.6575 | 0.0178 | 0.6773 | 0.6392 | 92 |
| E | 3 | 0.6434 | 0.0140 | 0.6637 | 0.6248 | 91 |

## Comparisons vs Baseline (A)

Paired permutation test on per-replication F1 scores (at each condition's optimal threshold):

| Comparison | ΔF1 | p-value | Significant? |
|------------|----:|--------:|:------------:|
| B vs A | -0.0093 | 0.8155 | No |
| C vs A | +0.0035 | 0.9419 | No |
| D vs A | +0.0138 | 0.6263 | No |
| E vs A | -0.0003 | 1.0000 | No |

## Per-Replication F1 (at optimal threshold)

| Rep | A (x=3) | B (x=3) | C (x=3) | D (x=3) | E (x=3) |
|----:|-----:|-----:|-----:|-----:|-----:|
| 1 | 0.6596 | 0.6186 | 0.6486 | 0.6277 | 0.6378 |
| 2 | 0.6989 | 0.6630 | 0.6593 | 0.6562 | 0.6630 |
| 3 | 0.6064 | 0.6806 | 0.6374 | 0.6667 | 0.6250 |
| 4 | 0.6010 | 0.6907 | 0.6413 | 0.6737 | 0.6492 |
| 5 | 0.6526 | 0.5193 | 0.6492 | 0.6632 | 0.6421 |

## Key Finding

No diversity condition significantly outperforms the identical-pass baseline (A, F1=0.6437). Diversity does not improve consensus voting for this track.

## Methodology

1. For each condition, form replications by taking run_k from each sub-condition
2. Within each pass: deduplicate detections (20 m)
3. Across passes: cluster and count votes (20 m)
4. Apply vote threshold sweep (x=1 to x=5)
5. Evaluate F1 against ground truth (20 m tolerance)
6. Select optimal threshold per condition (maximising mean F1 across replications)
7. Compare conditions using paired permutation test (10000 permutations, two-sided, α=0.05)
