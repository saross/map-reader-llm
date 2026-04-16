# Consensus Voting Sweep Analysis

**Generated**: 2026-03-24T10:26:30.054778+00:00  
**Bootstrap iterations**: 1000  
**Random seed**: 42  
**Baseline F1**: 0.5574

## Key Finding

Consensus voting **improves** over single-run baseline. Best configuration: image-t0.7 N=5 x=3 achieves F1=0.7031 (+0.1457 vs baseline).

## Per-Temperature Optima

| Temp | N | x | F1 | 95% CI | P | R | n_det | dF1 |
|------|---:|---:|----:|:------:|----:|----:|------:|----:|
| image-t0.7 | 5 | 3 | 0.7031 | [0.647, 0.758] | 0.6667 | 0.7438 | 471 | +0.1457 |

## Full Sweep Results

| Temp | N | x | F1 | 95% CI | P | R | n_det |
|------|---:|---:|----:|:------:|----:|----:|------:|
| image-t0.7 | 5 | 1 | 0.5710 | [0.527, 0.616] | 0.4351 | 0.8306 | 841 |
| image-t0.7 | 5 | 2 | 0.6726 | [0.619, 0.727] | 0.5906 | 0.7810 | 583 |
| image-t0.7 | 5 | 3 | 0.7031 | [0.647, 0.758] | 0.6667 | 0.7438 | 471 |
| image-t0.7 | 5 | 4 | 0.7011 | [0.643, 0.759] | 0.7309 | 0.6736 | 391 |
| image-t0.7 | 5 | 5 | 0.6538 | [0.594, 0.711] | 0.7895 | 0.5579 | 297 |

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
