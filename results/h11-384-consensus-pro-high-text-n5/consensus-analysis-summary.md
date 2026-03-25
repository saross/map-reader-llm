# Consensus Voting Sweep Analysis

**Generated**: 2026-03-24T05:20:30.063747+00:00  
**Bootstrap iterations**: 1000  
**Random seed**: 42  
**Baseline F1**: 0.5574

## Key Finding

Consensus voting **improves** over single-run baseline. Best configuration: text-t0.7 N=5 x=3 achieves F1=0.8489 (+0.2915 vs baseline).

## Per-Temperature Optima

| Temp | N | x | F1 | 95% CI | P | R | n_det | dF1 |
|------|---:|---:|----:|:------:|----:|----:|------:|----:|
| text-t0.7 | 5 | 3 | 0.8489 | [0.799, 0.888] | 0.9183 | 0.7893 | 367 | +0.2915 |

## Full Sweep Results

| Temp | N | x | F1 | 95% CI | P | R | n_det |
|------|---:|---:|----:|:------:|----:|----:|------:|
| text-t0.7 | 5 | 1 | 0.7527 | [0.697, 0.809] | 0.6721 | 0.8554 | 504 |
| text-t0.7 | 5 | 2 | 0.8285 | [0.782, 0.869] | 0.8390 | 0.8182 | 409 |
| text-t0.7 | 5 | 3 | 0.8489 | [0.799, 0.888] | 0.9183 | 0.7893 | 367 |
| text-t0.7 | 5 | 4 | 0.8383 | [0.791, 0.878] | 0.9340 | 0.7603 | 337 |
| text-t0.7 | 5 | 5 | 0.8058 | [0.754, 0.853] | 0.9600 | 0.6942 | 306 |

## Methodology

For each (temperature, pool_size, threshold) combination:

1. Detection GeoDataFrames are converted to GeoJSON features
2. Within-run deduplication (20 m tolerance) removes overlapping-tile duplicates
3. Cross-run clustering (20 m tolerance) groups detections and counts votes
4. Vote threshold filters clusters by minimum agreement
5. Consensus centroids are spatially joined to tile boundaries for F1 evaluation
6. F1 evaluation uses 20 m spatial matching tolerance
7. Bootstrapped 95% CIs use tile-level resampling (K=1000 iterations)

Pool selection follows the first-N convention (preregistration Section 3.8): N=5 uses runs 1-5, N=10 uses runs 1-10, etc.
