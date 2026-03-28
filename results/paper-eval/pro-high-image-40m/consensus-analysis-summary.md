# Consensus Voting Sweep Analysis

**Generated**: 2026-03-26T12:43:01.903901+00:00  
**Bootstrap iterations**: 1000  
**Random seed**: 42  
**Baseline F1**: 0.5574

## Key Finding

Consensus voting **improves** over single-run baseline. Best configuration: image-t0.7 N=5 x=3 achieves F1=0.8521 (+0.2947 vs baseline).

## Per-Temperature Optima

| Temp | N | x | F1 | 95% CI | P | R | n_det | dF1 |
|------|---:|---:|----:|:------:|----:|----:|------:|----:|
| image-t0.7 | 5 | 3 | 0.8521 | [0.823, 0.881] | 0.8195 | 0.8874 | 471 | +0.2947 |

## Full Sweep Results

| Temp | N | x | F1 | 95% CI | P | R | n_det |
|------|---:|---:|----:|:------:|----:|----:|------:|
| image-t0.7 | 5 | 1 | 0.6489 | [0.614, 0.683] | 0.4923 | 0.9517 | 841 |
| image-t0.7 | 5 | 2 | 0.7976 | [0.768, 0.828] | 0.6964 | 0.9333 | 583 |
| image-t0.7 | 5 | 3 | 0.8521 | [0.823, 0.881] | 0.8195 | 0.8874 | 471 |
| image-t0.7 | 5 | 4 | 0.8208 | [0.784, 0.852] | 0.8670 | 0.7793 | 391 |
| image-t0.7 | 5 | 5 | 0.7240 | [0.682, 0.765] | 0.8923 | 0.6092 | 297 |

## Methodology

For each (temperature, pool_size, threshold) combination:

1. Detection GeoDataFrames are converted to GeoJSON features
2. Within-run deduplication (20 m tolerance) removes overlapping-tile duplicates
3. Cross-run clustering (20 m tolerance) groups detections and counts votes
4. Vote threshold filters clusters by minimum agreement
5. Consensus centroids are spatially joined to tile boundaries for F1 evaluation
6. F1 evaluation uses 40 m spatial matching tolerance
7. Bootstrapped 95% CIs use tile-level resampling (K=1000 iterations)

Pool selection follows the first-N convention (preregistration Section 3.8): N=5 uses runs 1-5, N=10 uses runs 1-10, etc.
