# Consensus Voting Sweep Analysis

**Generated**: 2026-03-24T05:20:17.924791+00:00  
**Bootstrap iterations**: 1000  
**Random seed**: 42  
**Baseline F1**: 0.5574

## Key Finding

Consensus voting **improves** over single-run baseline. Best configuration: text-t0.7 N=5 x=5 achieves F1=0.7761 (+0.2187 vs baseline).

## Per-Temperature Optima

| Temp | N | x | F1 | 95% CI | P | R | n_det | dF1 |
|------|---:|---:|----:|:------:|----:|----:|------:|----:|
| text-t0.7 | 5 | 5 | 0.7761 | [0.723, 0.824] | 0.8018 | 0.7521 | 415 | +0.2187 |

## Full Sweep Results

| Temp | N | x | F1 | 95% CI | P | R | n_det |
|------|---:|---:|----:|:------:|----:|----:|------:|
| text-t0.7 | 5 | 1 | 0.1988 | [0.154, 0.252] | 0.1111 | 0.9421 | 3736 |
| text-t0.7 | 5 | 2 | 0.4313 | [0.358, 0.515] | 0.2835 | 0.9008 | 1376 |
| text-t0.7 | 5 | 3 | 0.6034 | [0.527, 0.677] | 0.4557 | 0.8926 | 855 |
| text-t0.7 | 5 | 4 | 0.7215 | [0.655, 0.780] | 0.6261 | 0.8512 | 584 |
| text-t0.7 | 5 | 5 | 0.7761 | [0.723, 0.824] | 0.8018 | 0.7521 | 415 |

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
