# Consensus Voting Sweep Analysis

**Generated**: 2026-03-26T12:42:25.534242+00:00  
**Bootstrap iterations**: 1000  
**Random seed**: 42  
**Baseline F1**: 0.5574

## Key Finding

Consensus voting **improves** over single-run baseline. Best configuration: text-t0.7 N=5 x=3 achieves F1=0.8404 (+0.2830 vs baseline).

## Per-Temperature Optima

| Temp | N | x | F1 | 95% CI | P | R | n_det | dF1 |
|------|---:|---:|----:|:------:|----:|----:|------:|----:|
| text-t0.7 | 5 | 3 | 0.8404 | [0.800, 0.875] | 0.9183 | 0.7747 | 367 | +0.2830 |

## Full Sweep Results

| Temp | N | x | F1 | 95% CI | P | R | n_det |
|------|---:|---:|----:|:------:|----:|----:|------:|
| text-t0.7 | 5 | 1 | 0.7689 | [0.728, 0.811] | 0.7163 | 0.8299 | 504 |
| text-t0.7 | 5 | 2 | 0.8223 | [0.785, 0.856] | 0.8484 | 0.7977 | 409 |
| text-t0.7 | 5 | 3 | 0.8404 | [0.800, 0.875] | 0.9183 | 0.7747 | 367 |
| text-t0.7 | 5 | 4 | 0.8264 | [0.783, 0.863] | 0.9466 | 0.7333 | 337 |
| text-t0.7 | 5 | 5 | 0.8016 | [0.758, 0.843] | 0.9706 | 0.6828 | 306 |

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
