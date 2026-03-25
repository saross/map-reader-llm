# Consensus Voting Sweep Analysis

**Generated**: 2026-03-25T07:24:44.205109+00:00  
**Bootstrap iterations**: 1000  
**Random seed**: 42  
**Baseline F1**: 0.5574

## Key Finding

Consensus voting **improves** over single-run baseline. Best configuration: image-t0.7 N=10 x=6 achieves F1=0.8182 (+0.2608 vs baseline).

## Per-Temperature Optima

| Temp | N | x | F1 | 95% CI | P | R | n_det | dF1 |
|------|---:|---:|----:|:------:|----:|----:|------:|----:|
| image-t0.7 | 10 | 6 | 0.8182 | [0.775, 0.856] | 0.7841 | 0.8554 | 462 | +0.2608 |

## Full Sweep Results

| Temp | N | x | F1 | 95% CI | P | R | n_det |
|------|---:|---:|----:|:------:|----:|----:|------:|
| image-t0.7 | 5 | 1 | 0.3435 | [0.291, 0.395] | 0.2097 | 0.9504 | 2017 |
| image-t0.7 | 5 | 2 | 0.6756 | [0.620, 0.726] | 0.5279 | 0.9380 | 741 |
| image-t0.7 | 5 | 3 | 0.8052 | [0.761, 0.846] | 0.7363 | 0.8884 | 506 |
| image-t0.7 | 5 | 4 | 0.7792 | [0.734, 0.827] | 0.8182 | 0.7438 | 388 |
| image-t0.7 | 5 | 5 | 0.6866 | [0.621, 0.748] | 0.8625 | 0.5702 | 282 |
| image-t0.7 | 10 | 1 | 0.2302 | [0.190, 0.272] | 0.1307 | 0.9669 | 3211 |
| image-t0.7 | 10 | 2 | 0.5239 | [0.469, 0.578] | 0.3616 | 0.9504 | 1112 |
| image-t0.7 | 10 | 3 | 0.6766 | [0.624, 0.723] | 0.5278 | 0.9421 | 752 |
| image-t0.7 | 10 | 4 | 0.7606 | [0.713, 0.805] | 0.6455 | 0.9256 | 609 |
| image-t0.7 | 10 | 5 | 0.7978 | [0.755, 0.837] | 0.7239 | 0.8884 | 519 |
| image-t0.7 | 10 | 6 | 0.8182 | [0.775, 0.856] | 0.7841 | 0.8554 | 462 |
| image-t0.7 | 10 | 7 | 0.8110 | [0.767, 0.858] | 0.8341 | 0.7893 | 405 |
| image-t0.7 | 10 | 8 | 0.7816 | [0.737, 0.832] | 0.8808 | 0.7025 | 344 |
| image-t0.7 | 10 | 9 | 0.7154 | [0.652, 0.776] | 0.9161 | 0.5868 | 281 |
| image-t0.7 | 10 | 10 | 0.6301 | [0.550, 0.705] | 0.9350 | 0.4752 | 206 |

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
