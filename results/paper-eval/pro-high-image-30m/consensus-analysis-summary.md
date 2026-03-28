# Consensus Voting Sweep Analysis

**Generated**: 2026-03-26T12:42:55.563237+00:00  
**Bootstrap iterations**: 1000  
**Random seed**: 42  
**Baseline F1**: 0.5574

## Key Finding

Consensus voting **improves** over single-run baseline. Best configuration: image-t0.7 N=5 x=3 achieves F1=0.8212 (+0.2638 vs baseline).

## Per-Temperature Optima

| Temp | N | x | F1 | 95% CI | P | R | n_det | dF1 |
|------|---:|---:|----:|:------:|----:|----:|------:|----:|
| image-t0.7 | 5 | 3 | 0.8212 | [0.787, 0.851] | 0.7898 | 0.8552 | 471 | +0.2638 |

## Full Sweep Results

| Temp | N | x | F1 | 95% CI | P | R | n_det |
|------|---:|---:|----:|:------:|----:|----:|------:|
| image-t0.7 | 5 | 1 | 0.6332 | [0.599, 0.668] | 0.4804 | 0.9287 | 841 |
| image-t0.7 | 5 | 2 | 0.7701 | [0.739, 0.802] | 0.6724 | 0.9011 | 583 |
| image-t0.7 | 5 | 3 | 0.8212 | [0.787, 0.851] | 0.7898 | 0.8552 | 471 |
| image-t0.7 | 5 | 4 | 0.7918 | [0.750, 0.827] | 0.8363 | 0.7517 | 391 |
| image-t0.7 | 5 | 5 | 0.7049 | [0.660, 0.748] | 0.8687 | 0.5931 | 297 |

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
