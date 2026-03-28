# Consensus Voting Sweep Analysis

**Generated**: 2026-03-26T12:42:19.698575+00:00  
**Bootstrap iterations**: 1000  
**Random seed**: 42  
**Baseline F1**: 0.5574

## Key Finding

Consensus voting **improves** over single-run baseline. Best configuration: image-t0.7 N=10 x=6 achieves F1=0.8339 (+0.2765 vs baseline).

## Per-Temperature Optima

| Temp | N | x | F1 | 95% CI | P | R | n_det | dF1 |
|------|---:|---:|----:|:------:|----:|----:|------:|----:|
| image-t0.7 | 10 | 6 | 0.8339 | [0.799, 0.862] | 0.8095 | 0.8598 | 462 | +0.2765 |

## Full Sweep Results

| Temp | N | x | F1 | 95% CI | P | R | n_det |
|------|---:|---:|----:|:------:|----:|----:|------:|
| image-t0.7 | 5 | 1 | 0.3442 | [0.303, 0.383] | 0.2092 | 0.9701 | 2017 |
| image-t0.7 | 5 | 2 | 0.7024 | [0.662, 0.737] | 0.5574 | 0.9494 | 741 |
| image-t0.7 | 5 | 3 | 0.8268 | [0.793, 0.856] | 0.7688 | 0.8943 | 506 |
| image-t0.7 | 5 | 4 | 0.7922 | [0.754, 0.827] | 0.8402 | 0.7494 | 388 |
| image-t0.7 | 5 | 5 | 0.7113 | [0.663, 0.756] | 0.9043 | 0.5862 | 282 |
| image-t0.7 | 10 | 1 | 0.2348 | [0.203, 0.264] | 0.1333 | 0.9839 | 3211 |
| image-t0.7 | 10 | 2 | 0.5404 | [0.498, 0.578] | 0.3759 | 0.9609 | 1112 |
| image-t0.7 | 10 | 3 | 0.6992 | [0.659, 0.734] | 0.5519 | 0.9540 | 752 |
| image-t0.7 | 10 | 4 | 0.7778 | [0.740, 0.810] | 0.6667 | 0.9333 | 609 |
| image-t0.7 | 10 | 5 | 0.8218 | [0.789, 0.848] | 0.7553 | 0.9011 | 519 |
| image-t0.7 | 10 | 6 | 0.8339 | [0.799, 0.862] | 0.8095 | 0.8598 | 462 |
| image-t0.7 | 10 | 7 | 0.8238 | [0.788, 0.857] | 0.8543 | 0.7954 | 405 |
| image-t0.7 | 10 | 8 | 0.7882 | [0.750, 0.825] | 0.8924 | 0.7057 | 344 |
| image-t0.7 | 10 | 9 | 0.7235 | [0.676, 0.767] | 0.9217 | 0.5954 | 281 |
| image-t0.7 | 10 | 10 | 0.6053 | [0.552, 0.661] | 0.9417 | 0.4460 | 206 |

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
