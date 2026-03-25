# Consensus Voting Sweep Analysis

**Generated**: 2026-03-25T07:24:52.916017+00:00  
**Bootstrap iterations**: 1000  
**Random seed**: 42  
**Baseline F1**: 0.5574

## Key Finding

Consensus voting **improves** over single-run baseline. Best configuration: image-t0.7 N=10 x=6 achieves F1=0.8379 (+0.2805 vs baseline).

## Per-Temperature Optima

| Temp | N | x | F1 | 95% CI | P | R | n_det | dF1 |
|------|---:|---:|----:|:------:|----:|----:|------:|----:|
| image-t0.7 | 10 | 6 | 0.8379 | [0.795, 0.873] | 0.8030 | 0.8760 | 462 | +0.2805 |

## Full Sweep Results

| Temp | N | x | F1 | 95% CI | P | R | n_det |
|------|---:|---:|----:|:------:|----:|----:|------:|
| image-t0.7 | 5 | 1 | 0.3510 | [0.300, 0.401] | 0.2142 | 0.9711 | 2017 |
| image-t0.7 | 5 | 2 | 0.6935 | [0.640, 0.742] | 0.5419 | 0.9628 | 741 |
| image-t0.7 | 5 | 3 | 0.8315 | [0.788, 0.870] | 0.7603 | 0.9174 | 506 |
| image-t0.7 | 5 | 4 | 0.8052 | [0.762, 0.848] | 0.8455 | 0.7686 | 388 |
| image-t0.7 | 5 | 5 | 0.7114 | [0.648, 0.772] | 0.8938 | 0.5909 | 282 |
| image-t0.7 | 10 | 1 | 0.2341 | [0.193, 0.276] | 0.1329 | 0.9835 | 3211 |
| image-t0.7 | 10 | 2 | 0.5353 | [0.479, 0.590] | 0.3695 | 0.9711 | 1112 |
| image-t0.7 | 10 | 3 | 0.6973 | [0.646, 0.743] | 0.5440 | 0.9711 | 752 |
| image-t0.7 | 10 | 4 | 0.7810 | [0.734, 0.822] | 0.6628 | 0.9504 | 609 |
| image-t0.7 | 10 | 5 | 0.8237 | [0.782, 0.860] | 0.7475 | 0.9174 | 519 |
| image-t0.7 | 10 | 6 | 0.8379 | [0.795, 0.873] | 0.8030 | 0.8760 | 462 |
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
6. F1 evaluation uses 40 m spatial matching tolerance
7. Bootstrapped 95% CIs use tile-level resampling (K=1000 iterations)

Pool selection follows the first-N convention (preregistration Section 3.8): N=5 uses runs 1-5, N=10 uses runs 1-10, etc.
