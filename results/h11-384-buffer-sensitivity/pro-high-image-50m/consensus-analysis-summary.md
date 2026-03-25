# Consensus Voting Sweep Analysis

**Generated**: 2026-03-25T07:25:21.619768+00:00  
**Bootstrap iterations**: 1000  
**Random seed**: 42  
**Baseline F1**: 0.5574

## Key Finding

Consensus voting **improves** over single-run baseline. Best configuration: image-t0.7 N=5 x=3 achieves F1=0.8516 (+0.2942 vs baseline).

## Per-Temperature Optima

| Temp | N | x | F1 | 95% CI | P | R | n_det | dF1 |
|------|---:|---:|----:|:------:|----:|----:|------:|----:|
| image-t0.7 | 5 | 3 | 0.8516 | [0.817, 0.882] | 0.8074 | 0.9008 | 471 | +0.2942 |

## Full Sweep Results

| Temp | N | x | F1 | 95% CI | P | R | n_det |
|------|---:|---:|----:|:------:|----:|----:|------:|
| image-t0.7 | 5 | 1 | 0.6534 | [0.612, 0.699] | 0.4978 | 0.9504 | 841 |
| image-t0.7 | 5 | 2 | 0.8078 | [0.772, 0.841] | 0.7094 | 0.9380 | 583 |
| image-t0.7 | 5 | 3 | 0.8516 | [0.817, 0.882] | 0.8074 | 0.9008 | 471 |
| image-t0.7 | 5 | 4 | 0.8172 | [0.769, 0.859] | 0.8520 | 0.7851 | 391 |
| image-t0.7 | 5 | 5 | 0.7312 | [0.679, 0.782] | 0.8830 | 0.6240 | 297 |

## Methodology

For each (temperature, pool_size, threshold) combination:

1. Detection GeoDataFrames are converted to GeoJSON features
2. Within-run deduplication (20 m tolerance) removes overlapping-tile duplicates
3. Cross-run clustering (20 m tolerance) groups detections and counts votes
4. Vote threshold filters clusters by minimum agreement
5. Consensus centroids are spatially joined to tile boundaries for F1 evaluation
6. F1 evaluation uses 50 m spatial matching tolerance
7. Bootstrapped 95% CIs use tile-level resampling (K=1000 iterations)

Pool selection follows the first-N convention (preregistration Section 3.8): N=5 uses runs 1-5, N=10 uses runs 1-10, etc.
