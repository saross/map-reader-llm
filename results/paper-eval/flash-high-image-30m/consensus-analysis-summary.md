# Consensus Voting Sweep Analysis

**Generated**: 2026-03-26T12:41:51.201635+00:00  
**Bootstrap iterations**: 1000  
**Random seed**: 42  
**Baseline F1**: 0.5574

## Key Finding

Consensus voting **improves** over single-run baseline. Best configuration: image-t0.7 N=10 x=6 achieves F1=0.8116 (+0.2542 vs baseline).

## Per-Temperature Optima

| Temp | N | x | F1 | 95% CI | P | R | n_det | dF1 |
|------|---:|---:|----:|:------:|----:|----:|------:|----:|
| image-t0.7 | 10 | 6 | 0.8116 | [0.777, 0.841] | 0.7879 | 0.8368 | 462 | +0.2542 |

## Full Sweep Results

| Temp | N | x | F1 | 95% CI | P | R | n_det |
|------|---:|---:|----:|:------:|----:|----:|------:|
| image-t0.7 | 5 | 1 | 0.3344 | [0.293, 0.372] | 0.2033 | 0.9425 | 2017 |
| image-t0.7 | 5 | 2 | 0.6820 | [0.641, 0.717] | 0.5412 | 0.9218 | 741 |
| image-t0.7 | 5 | 3 | 0.7991 | [0.762, 0.829] | 0.7431 | 0.8644 | 506 |
| image-t0.7 | 5 | 4 | 0.7776 | [0.736, 0.814] | 0.8247 | 0.7356 | 388 |
| image-t0.7 | 5 | 5 | 0.6946 | [0.645, 0.742] | 0.8830 | 0.5724 | 282 |
| image-t0.7 | 10 | 1 | 0.2282 | [0.197, 0.258] | 0.1296 | 0.9563 | 3211 |
| image-t0.7 | 10 | 2 | 0.5262 | [0.483, 0.564] | 0.3660 | 0.9356 | 1112 |
| image-t0.7 | 10 | 3 | 0.6790 | [0.640, 0.716] | 0.5359 | 0.9264 | 752 |
| image-t0.7 | 10 | 4 | 0.7510 | [0.712, 0.785] | 0.6437 | 0.9011 | 609 |
| image-t0.7 | 10 | 5 | 0.7925 | [0.756, 0.822] | 0.7283 | 0.8690 | 519 |
| image-t0.7 | 10 | 6 | 0.8116 | [0.777, 0.841] | 0.7879 | 0.8368 | 462 |
| image-t0.7 | 10 | 7 | 0.8095 | [0.773, 0.843] | 0.8395 | 0.7816 | 405 |
| image-t0.7 | 10 | 8 | 0.7779 | [0.737, 0.814] | 0.8808 | 0.6966 | 344 |
| image-t0.7 | 10 | 9 | 0.7179 | [0.670, 0.761] | 0.9146 | 0.5908 | 281 |
| image-t0.7 | 10 | 10 | 0.6022 | [0.550, 0.658] | 0.9369 | 0.4437 | 206 |

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
