# Consensus Voting Sweep Analysis

**Generated**: 2026-03-26T12:48:46.733971+00:00  
**Bootstrap iterations**: 1000  
**Random seed**: 42  
**Baseline F1**: 0.5574

## Key Finding

Consensus voting **improves** over single-run baseline. Best configuration: brief-text-t0 N=10 x=10 achieves F1=0.5626 (+0.0052 vs baseline).

## Per-Temperature Optima

| Temp | N | x | F1 | 95% CI | P | R | n_det | dF1 |
|------|---:|---:|----:|:------:|----:|----:|------:|----:|
| brief-text-t0 | 10 | 10 | 0.5626 | [0.500, 0.621] | 0.4176 | 0.8621 | 898 | +0.0052 |

## Full Sweep Results

| Temp | N | x | F1 | 95% CI | P | R | n_det |
|------|---:|---:|----:|:------:|----:|----:|------:|
| brief-text-t0 | 5 | 1 | 0.5202 | [0.457, 0.577] | 0.3626 | 0.9195 | 1103 |
| brief-text-t0 | 5 | 2 | 0.5385 | [0.473, 0.595] | 0.3828 | 0.9080 | 1032 |
| brief-text-t0 | 5 | 3 | 0.5427 | [0.479, 0.600] | 0.3887 | 0.8989 | 1006 |
| brief-text-t0 | 5 | 4 | 0.5439 | [0.479, 0.601] | 0.3904 | 0.8966 | 999 |
| brief-text-t0 | 5 | 5 | 0.5541 | [0.490, 0.611] | 0.4038 | 0.8828 | 951 |
| brief-text-t0 | 10 | 1 | 0.5035 | [0.440, 0.559] | 0.3463 | 0.9218 | 1158 |
| brief-text-t0 | 10 | 2 | 0.5294 | [0.465, 0.587] | 0.3732 | 0.9103 | 1061 |
| brief-text-t0 | 10 | 3 | 0.5396 | [0.475, 0.596] | 0.3839 | 0.9080 | 1029 |
| brief-text-t0 | 10 | 4 | 0.5414 | [0.477, 0.600] | 0.3870 | 0.9011 | 1013 |
| brief-text-t0 | 10 | 5 | 0.5433 | [0.479, 0.601] | 0.3889 | 0.9011 | 1008 |
| brief-text-t0 | 10 | 6 | 0.5433 | [0.479, 0.601] | 0.3889 | 0.9011 | 1008 |
| brief-text-t0 | 10 | 7 | 0.5441 | [0.479, 0.602] | 0.3897 | 0.9011 | 1006 |
| brief-text-t0 | 10 | 8 | 0.5453 | [0.480, 0.602] | 0.3914 | 0.8989 | 999 |
| brief-text-t0 | 10 | 9 | 0.5529 | [0.488, 0.611] | 0.4002 | 0.8943 | 972 |
| brief-text-t0 | 10 | 10 | 0.5626 | [0.500, 0.621] | 0.4176 | 0.8621 | 898 |

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
