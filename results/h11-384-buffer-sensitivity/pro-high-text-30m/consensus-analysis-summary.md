# Consensus Voting Sweep Analysis

**Generated**: 2026-03-25T07:25:04.613446+00:00  
**Bootstrap iterations**: 1000  
**Random seed**: 42  
**Baseline F1**: 0.5574

## Key Finding

Consensus voting **improves** over single-run baseline. Best configuration: text-t0.7 N=5 x=3 achieves F1=0.8578 (+0.3004 vs baseline).

## Per-Temperature Optima

| Temp | N | x | F1 | 95% CI | P | R | n_det | dF1 |
|------|---:|---:|----:|:------:|----:|----:|------:|----:|
| text-t0.7 | 5 | 3 | 0.8578 | [0.809, 0.898] | 0.9279 | 0.7975 | 367 | +0.3004 |

## Full Sweep Results

| Temp | N | x | F1 | 95% CI | P | R | n_det |
|------|---:|---:|----:|:------:|----:|----:|------:|
| text-t0.7 | 5 | 1 | 0.7745 | [0.717, 0.827] | 0.6916 | 0.8802 | 504 |
| text-t0.7 | 5 | 2 | 0.8452 | [0.802, 0.882] | 0.8559 | 0.8347 | 409 |
| text-t0.7 | 5 | 3 | 0.8578 | [0.809, 0.898] | 0.9279 | 0.7975 | 367 |
| text-t0.7 | 5 | 4 | 0.8474 | [0.802, 0.887] | 0.9442 | 0.7686 | 337 |
| text-t0.7 | 5 | 5 | 0.8153 | [0.765, 0.862] | 0.9714 | 0.7025 | 306 |

## Methodology

For each (temperature, pool_size, threshold) combination:

1. Detection GeoDataFrames are converted to GeoJSON features
2. Within-run deduplication (20 m tolerance) removes overlapping-tile duplicates
3. Cross-run clustering (20 m tolerance) groups detections and counts votes
4. Vote threshold filters clusters by minimum agreement
5. Consensus centroids are spatially joined to tile boundaries for F1 evaluation
6. F1 evaluation uses 30 m spatial matching tolerance
7. Bootstrapped 95% CIs use tile-level resampling (K=1000 iterations)

Pool selection follows the first-N convention (preregistration Section 3.8): N=5 uses runs 1-5, N=10 uses runs 1-10, etc.
