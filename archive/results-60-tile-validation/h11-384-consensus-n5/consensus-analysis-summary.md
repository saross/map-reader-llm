# Consensus Voting Sweep Analysis

**Generated**: 2026-03-23T05:05:03.821250+00:00  
**Bootstrap iterations**: 1000  
**Random seed**: 42  
**Baseline F1**: 0.5574

## Key Finding

Consensus voting **improves** over single-run baseline. Best configuration: 384 N=5 x=5 achieves F1=0.6443 (+0.0869 vs baseline).

## Per-Temperature Optima

| Temp | N | x | F1 | 95% CI | P | R | n_det | dF1 |
|------|---:|---:|----:|:------:|----:|----:|------:|----:|
| 384 | 5 | 5 | 0.6443 | [0.568, 0.712] | 0.5864 | 0.7149 | 295 | +0.0869 |

## Full Sweep Results

| Temp | N | x | F1 | 95% CI | P | R | n_det |
|------|---:|---:|----:|:------:|----:|----:|------:|
| 384 | 5 | 1 | 0.3536 | [0.281, 0.430] | 0.2207 | 0.8884 | 974 |
| 384 | 5 | 2 | 0.4895 | [0.405, 0.572] | 0.3409 | 0.8678 | 616 |
| 384 | 5 | 3 | 0.5510 | [0.468, 0.631] | 0.4132 | 0.8264 | 484 |
| 384 | 5 | 4 | 0.5965 | [0.516, 0.670] | 0.4810 | 0.7851 | 395 |
| 384 | 5 | 5 | 0.6443 | [0.568, 0.712] | 0.5864 | 0.7149 | 295 |

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
