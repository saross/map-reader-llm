# Consensus Voting Sweep Analysis

**Generated**: 2026-03-24T05:43:32.151215+00:00  
**Bootstrap iterations**: 1000  
**Random seed**: 42  
**Baseline F1**: 0.5574

## Key Finding

Consensus voting **improves** over single-run baseline. Best configuration: image-t0.7 N=5 x=3 achieves F1=0.7303 (+0.1729 vs baseline).

## Per-Temperature Optima

| Temp | N | x | F1 | 95% CI | P | R | n_det | dF1 |
|------|---:|---:|----:|:------:|----:|----:|------:|----:|
| image-t0.7 | 5 | 3 | 0.7303 | [0.677, 0.781] | 0.6678 | 0.8058 | 506 | +0.1729 |

## Full Sweep Results

| Temp | N | x | F1 | 95% CI | P | R | n_det |
|------|---:|---:|----:|:------:|----:|----:|------:|
| image-t0.7 | 5 | 1 | 0.3211 | [0.269, 0.371] | 0.1960 | 0.8884 | 2017 |
| image-t0.7 | 5 | 2 | 0.6101 | [0.554, 0.661] | 0.4767 | 0.8471 | 741 |
| image-t0.7 | 5 | 3 | 0.7303 | [0.677, 0.781] | 0.6678 | 0.8058 | 506 |
| image-t0.7 | 5 | 4 | 0.7186 | [0.668, 0.774] | 0.7545 | 0.6860 | 388 |
| image-t0.7 | 5 | 5 | 0.6468 | [0.580, 0.711] | 0.8125 | 0.5372 | 282 |

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
