# Consensus Voting Sweep Analysis

**Generated**: 2026-03-25T07:25:01.364447+00:00  
**Bootstrap iterations**: 1000  
**Random seed**: 42  
**Baseline F1**: 0.5574

## Key Finding

Consensus voting **improves** over single-run baseline. Best configuration: image-t0.7 N=10 x=6 achieves F1=0.8458 (+0.2884 vs baseline).

## Per-Temperature Optima

| Temp | N | x | F1 | 95% CI | P | R | n_det | dF1 |
|------|---:|---:|----:|:------:|----:|----:|------:|----:|
| image-t0.7 | 10 | 6 | 0.8458 | [0.805, 0.880] | 0.8106 | 0.8843 | 462 | +0.2884 |

## Full Sweep Results

| Temp | N | x | F1 | 95% CI | P | R | n_det |
|------|---:|---:|----:|:------:|----:|----:|------:|
| image-t0.7 | 5 | 1 | 0.3540 | [0.302, 0.405] | 0.2160 | 0.9793 | 2017 |
| image-t0.7 | 5 | 2 | 0.7024 | [0.650, 0.751] | 0.5488 | 0.9752 | 741 |
| image-t0.7 | 5 | 3 | 0.8427 | [0.801, 0.880] | 0.7705 | 0.9298 | 506 |
| image-t0.7 | 5 | 4 | 0.8052 | [0.762, 0.848] | 0.8455 | 0.7686 | 388 |
| image-t0.7 | 5 | 5 | 0.7164 | [0.653, 0.777] | 0.9000 | 0.5950 | 282 |
| image-t0.7 | 10 | 1 | 0.2361 | [0.195, 0.279] | 0.1340 | 0.9917 | 3211 |
| image-t0.7 | 10 | 2 | 0.5399 | [0.484, 0.594] | 0.3726 | 0.9793 | 1112 |
| image-t0.7 | 10 | 3 | 0.7003 | [0.649, 0.745] | 0.5463 | 0.9752 | 752 |
| image-t0.7 | 10 | 4 | 0.7912 | [0.747, 0.830] | 0.6715 | 0.9628 | 609 |
| image-t0.7 | 10 | 5 | 0.8349 | [0.795, 0.868] | 0.7576 | 0.9298 | 519 |
| image-t0.7 | 10 | 6 | 0.8458 | [0.805, 0.880] | 0.8106 | 0.8843 | 462 |
| image-t0.7 | 10 | 7 | 0.8280 | [0.784, 0.870] | 0.8515 | 0.8058 | 405 |
| image-t0.7 | 10 | 8 | 0.7954 | [0.748, 0.845] | 0.8964 | 0.7149 | 344 |
| image-t0.7 | 10 | 9 | 0.7254 | [0.661, 0.786] | 0.9290 | 0.5950 | 281 |
| image-t0.7 | 10 | 10 | 0.6356 | [0.555, 0.710] | 0.9431 | 0.4793 | 206 |

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
