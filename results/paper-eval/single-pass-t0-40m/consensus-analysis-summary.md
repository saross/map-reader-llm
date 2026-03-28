# Consensus Voting Sweep Analysis

**Generated**: 2026-03-26T12:48:59.702100+00:00  
**Bootstrap iterations**: 1000  
**Random seed**: 42  
**Baseline F1**: 0.5574

## Key Finding

Consensus voting **improves** over single-run baseline. Best configuration: brief-text-t0 N=10 x=10 achieves F1=0.5671 (+0.0097 vs baseline).

## Per-Temperature Optima

| Temp | N | x | F1 | 95% CI | P | R | n_det | dF1 |
|------|---:|---:|----:|:------:|----:|----:|------:|----:|
| brief-text-t0 | 10 | 10 | 0.5671 | [0.505, 0.625] | 0.4209 | 0.8690 | 898 | +0.0097 |

## Full Sweep Results

| Temp | N | x | F1 | 95% CI | P | R | n_det |
|------|---:|---:|----:|:------:|----:|----:|------:|
| brief-text-t0 | 5 | 1 | 0.5267 | [0.462, 0.585] | 0.3672 | 0.9310 | 1103 |
| brief-text-t0 | 5 | 2 | 0.5453 | [0.481, 0.602] | 0.3876 | 0.9195 | 1032 |
| brief-text-t0 | 5 | 3 | 0.5482 | [0.483, 0.607] | 0.3926 | 0.9080 | 1006 |
| brief-text-t0 | 5 | 4 | 0.5495 | [0.484, 0.609] | 0.3944 | 0.9057 | 999 |
| brief-text-t0 | 5 | 5 | 0.5584 | [0.493, 0.617] | 0.4069 | 0.8897 | 951 |
| brief-text-t0 | 10 | 1 | 0.5097 | [0.446, 0.570] | 0.3506 | 0.9333 | 1158 |
| brief-text-t0 | 10 | 2 | 0.5361 | [0.472, 0.595] | 0.3779 | 0.9218 | 1061 |
| brief-text-t0 | 10 | 3 | 0.5451 | [0.480, 0.602] | 0.3878 | 0.9172 | 1029 |
| brief-text-t0 | 10 | 4 | 0.5470 | [0.481, 0.606] | 0.3909 | 0.9103 | 1013 |
| brief-text-t0 | 10 | 5 | 0.5489 | [0.483, 0.608] | 0.3929 | 0.9103 | 1008 |
| brief-text-t0 | 10 | 6 | 0.5489 | [0.483, 0.608] | 0.3929 | 0.9103 | 1008 |
| brief-text-t0 | 10 | 7 | 0.5496 | [0.484, 0.608] | 0.3936 | 0.9103 | 1006 |
| brief-text-t0 | 10 | 8 | 0.5509 | [0.485, 0.608] | 0.3954 | 0.9080 | 999 |
| brief-text-t0 | 10 | 9 | 0.5586 | [0.494, 0.616] | 0.4043 | 0.9034 | 972 |
| brief-text-t0 | 10 | 10 | 0.5671 | [0.505, 0.625] | 0.4209 | 0.8690 | 898 |

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
