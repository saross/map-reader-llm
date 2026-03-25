# Consensus Voting Sweep Analysis

**Generated**: 2026-03-24T10:26:34.535939+00:00  
**Bootstrap iterations**: 1000  
**Random seed**: 42  
**Baseline F1**: 0.5574

## Key Finding

Consensus voting **improves** over single-run baseline. Best configuration: image-t0.7 N=10 x=7 achieves F1=0.7516 (+0.1942 vs baseline).

## Per-Temperature Optima

| Temp | N | x | F1 | 95% CI | P | R | n_det | dF1 |
|------|---:|---:|----:|:------:|----:|----:|------:|----:|
| image-t0.7 | 10 | 7 | 0.7516 | [0.699, 0.803] | 0.7729 | 0.7314 | 405 | +0.1942 |

## Full Sweep Results

| Temp | N | x | F1 | 95% CI | P | R | n_det |
|------|---:|---:|----:|:------:|----:|----:|------:|
| image-t0.7 | 5 | 1 | 0.3211 | [0.269, 0.371] | 0.1960 | 0.8884 | 2017 |
| image-t0.7 | 5 | 2 | 0.6101 | [0.554, 0.661] | 0.4767 | 0.8471 | 741 |
| image-t0.7 | 5 | 3 | 0.7303 | [0.677, 0.781] | 0.6678 | 0.8058 | 506 |
| image-t0.7 | 5 | 4 | 0.7186 | [0.668, 0.774] | 0.7545 | 0.6860 | 388 |
| image-t0.7 | 5 | 5 | 0.6468 | [0.580, 0.711] | 0.8125 | 0.5372 | 282 |
| image-t0.7 | 10 | 1 | 0.2145 | [0.175, 0.256] | 0.1217 | 0.9008 | 3211 |
| image-t0.7 | 10 | 2 | 0.4829 | [0.427, 0.535] | 0.3333 | 0.8760 | 1112 |
| image-t0.7 | 10 | 3 | 0.6172 | [0.563, 0.668] | 0.4815 | 0.8595 | 752 |
| image-t0.7 | 10 | 4 | 0.6893 | [0.634, 0.739] | 0.5850 | 0.8388 | 609 |
| image-t0.7 | 10 | 5 | 0.7273 | [0.676, 0.777] | 0.6599 | 0.8099 | 519 |
| image-t0.7 | 10 | 6 | 0.7470 | [0.696, 0.795] | 0.7159 | 0.7810 | 462 |
| image-t0.7 | 10 | 7 | 0.7516 | [0.699, 0.803] | 0.7729 | 0.7314 | 405 |
| image-t0.7 | 10 | 8 | 0.7264 | [0.673, 0.779] | 0.8187 | 0.6529 | 344 |
| image-t0.7 | 10 | 9 | 0.6751 | [0.608, 0.739] | 0.8645 | 0.5537 | 281 |
| image-t0.7 | 10 | 10 | 0.5973 | [0.512, 0.674] | 0.8862 | 0.4504 | 206 |

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
