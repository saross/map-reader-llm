# Consensus Voting Sweep Analysis

**Generated**: 2026-03-25T07:25:14.572693+00:00  
**Bootstrap iterations**: 1000  
**Random seed**: 42  
**Baseline F1**: 0.5574

## Key Finding

Consensus voting **improves** over single-run baseline. Best configuration: image-t0.7 N=5 x=3 achieves F1=0.8164 (+0.2590 vs baseline).

## Per-Temperature Optima

| Temp | N | x | F1 | 95% CI | P | R | n_det | dF1 |
|------|---:|---:|----:|:------:|----:|----:|------:|----:|
| image-t0.7 | 5 | 3 | 0.8164 | [0.777, 0.856] | 0.7741 | 0.8636 | 471 | +0.2590 |

## Full Sweep Results

| Temp | N | x | F1 | 95% CI | P | R | n_det |
|------|---:|---:|----:|:------:|----:|----:|------:|
| image-t0.7 | 5 | 1 | 0.6420 | [0.604, 0.687] | 0.4892 | 0.9339 | 841 |
| image-t0.7 | 5 | 2 | 0.7758 | [0.734, 0.819] | 0.6813 | 0.9008 | 583 |
| image-t0.7 | 5 | 3 | 0.8164 | [0.777, 0.856] | 0.7741 | 0.8636 | 471 |
| image-t0.7 | 5 | 4 | 0.7957 | [0.748, 0.845] | 0.8296 | 0.7645 | 391 |
| image-t0.7 | 5 | 5 | 0.7167 | [0.663, 0.770] | 0.8655 | 0.6116 | 297 |

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
