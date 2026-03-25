# Consensus Voting Sweep Analysis

**Generated**: 2026-03-25T07:25:11.058008+00:00  
**Bootstrap iterations**: 1000  
**Random seed**: 42  
**Baseline F1**: 0.5574

## Key Finding

Consensus voting **improves** over single-run baseline. Best configuration: text-t0.7 N=5 x=3 achieves F1=0.8622 (+0.3048 vs baseline).

## Per-Temperature Optima

| Temp | N | x | F1 | 95% CI | P | R | n_det | dF1 |
|------|---:|---:|----:|:------:|----:|----:|------:|----:|
| text-t0.7 | 5 | 3 | 0.8622 | [0.815, 0.898] | 0.9327 | 0.8017 | 367 | +0.3048 |

## Full Sweep Results

| Temp | N | x | F1 | 95% CI | P | R | n_det |
|------|---:|---:|----:|:------:|----:|----:|------:|
| text-t0.7 | 5 | 1 | 0.7818 | [0.726, 0.833] | 0.6981 | 0.8884 | 504 |
| text-t0.7 | 5 | 2 | 0.8536 | [0.811, 0.888] | 0.8644 | 0.8430 | 409 |
| text-t0.7 | 5 | 3 | 0.8622 | [0.815, 0.898] | 0.9327 | 0.8017 | 367 |
| text-t0.7 | 5 | 4 | 0.8519 | [0.808, 0.889] | 0.9492 | 0.7727 | 337 |
| text-t0.7 | 5 | 5 | 0.8201 | [0.771, 0.866] | 0.9771 | 0.7066 | 306 |

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
