# Consensus Voting Sweep Analysis

**Generated**: 2026-03-26T12:42:31.308946+00:00  
**Bootstrap iterations**: 1000  
**Random seed**: 42  
**Baseline F1**: 0.5574

## Key Finding

Consensus voting **improves** over single-run baseline. Best configuration: text-t0.7 N=5 x=3 achieves F1=0.8554 (+0.2980 vs baseline).

## Per-Temperature Optima

| Temp | N | x | F1 | 95% CI | P | R | n_det | dF1 |
|------|---:|---:|----:|:------:|----:|----:|------:|----:|
| text-t0.7 | 5 | 3 | 0.8554 | [0.820, 0.887] | 0.9346 | 0.7885 | 367 | +0.2980 |

## Full Sweep Results

| Temp | N | x | F1 | 95% CI | P | R | n_det |
|------|---:|---:|----:|:------:|----:|----:|------:|
| text-t0.7 | 5 | 1 | 0.7859 | [0.744, 0.825] | 0.7321 | 0.8483 | 504 |
| text-t0.7 | 5 | 2 | 0.8412 | [0.807, 0.872] | 0.8680 | 0.8161 | 409 |
| text-t0.7 | 5 | 3 | 0.8554 | [0.820, 0.887] | 0.9346 | 0.7885 | 367 |
| text-t0.7 | 5 | 4 | 0.8368 | [0.792, 0.872] | 0.9585 | 0.7425 | 337 |
| text-t0.7 | 5 | 5 | 0.8097 | [0.767, 0.849] | 0.9804 | 0.6897 | 306 |

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
