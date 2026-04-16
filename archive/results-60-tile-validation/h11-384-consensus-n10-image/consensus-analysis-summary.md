# Consensus Voting Sweep Analysis

**Generated**: 2026-03-23T07:07:03.325626+00:00  
**Bootstrap iterations**: 1000  
**Random seed**: 42  
**Baseline F1**: 0.5574

## Key Finding

Consensus voting **improves** over single-run baseline. Best configuration: image-t0.7 N=10 x=8 achieves F1=0.6795 (+0.1221 vs baseline).

## Per-Temperature Optima

| Temp | N | x | F1 | 95% CI | P | R | n_det | dF1 |
|------|---:|---:|----:|:------:|----:|----:|------:|----:|
| image-t0.7 | 10 | 8 | 0.6795 | [0.616, 0.733] | 0.6377 | 0.7273 | 494 | +0.1221 |

## Full Sweep Results

| Temp | N | x | F1 | 95% CI | P | R | n_det |
|------|---:|---:|----:|:------:|----:|----:|------:|
| image-t0.7 | 10 | 1 | 0.4132 | [0.358, 0.461] | 0.2700 | 0.8802 | 1450 |
| image-t0.7 | 10 | 2 | 0.5502 | [0.495, 0.602] | 0.4019 | 0.8719 | 952 |
| image-t0.7 | 10 | 3 | 0.6042 | [0.545, 0.658] | 0.4721 | 0.8388 | 777 |
| image-t0.7 | 10 | 4 | 0.6399 | [0.577, 0.694] | 0.5237 | 0.8223 | 697 |
| image-t0.7 | 10 | 5 | 0.6565 | [0.593, 0.712] | 0.5559 | 0.8017 | 625 |
| image-t0.7 | 10 | 6 | 0.6667 | [0.606, 0.722] | 0.5793 | 0.7851 | 577 |
| image-t0.7 | 10 | 7 | 0.6752 | [0.616, 0.730] | 0.6073 | 0.7603 | 535 |
| image-t0.7 | 10 | 8 | 0.6795 | [0.616, 0.733] | 0.6377 | 0.7273 | 494 |
| image-t0.7 | 10 | 9 | 0.6667 | [0.604, 0.722] | 0.6560 | 0.6777 | 443 |
| image-t0.7 | 10 | 10 | 0.6230 | [0.553, 0.692] | 0.6866 | 0.5702 | 361 |

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
