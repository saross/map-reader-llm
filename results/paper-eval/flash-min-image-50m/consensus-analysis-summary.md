# Consensus Voting Sweep Analysis

**Generated**: 2026-03-26T12:48:20.643011+00:00  
**Bootstrap iterations**: 1000  
**Random seed**: 42  
**Baseline F1**: 0.5574

## Key Finding

Consensus voting **improves** over single-run baseline. Best configuration: image-t0.7 N=10 x=6 achieves F1=0.7530 (+0.1956 vs baseline).

## Per-Temperature Optima

| Temp | N | x | F1 | 95% CI | P | R | n_det | dF1 |
|------|---:|---:|----:|:------:|----:|----:|------:|----:|
| image-t0.7 | 10 | 6 | 0.7530 | [0.713, 0.787] | 0.6603 | 0.8759 | 577 | +0.1956 |

## Full Sweep Results

| Temp | N | x | F1 | 95% CI | P | R | n_det |
|------|---:|---:|----:|:------:|----:|----:|------:|
| image-t0.7 | 5 | 1 | 0.5289 | [0.487, 0.570] | 0.3669 | 0.9471 | 1123 |
| image-t0.7 | 5 | 2 | 0.6695 | [0.627, 0.707] | 0.5279 | 0.9149 | 754 |
| image-t0.7 | 5 | 3 | 0.7376 | [0.698, 0.772] | 0.6288 | 0.8920 | 617 |
| image-t0.7 | 5 | 4 | 0.7495 | [0.708, 0.785] | 0.6864 | 0.8253 | 523 |
| image-t0.7 | 5 | 5 | 0.7169 | [0.677, 0.756] | 0.7237 | 0.7103 | 427 |
| image-t0.7 | 10 | 1 | 0.4393 | [0.399, 0.480] | 0.2855 | 0.9517 | 1450 |
| image-t0.7 | 10 | 2 | 0.5912 | [0.550, 0.631] | 0.4307 | 0.9425 | 952 |
| image-t0.7 | 10 | 3 | 0.6716 | [0.634, 0.708] | 0.5238 | 0.9356 | 777 |
| image-t0.7 | 10 | 4 | 0.7102 | [0.672, 0.744] | 0.5768 | 0.9241 | 697 |
| image-t0.7 | 10 | 5 | 0.7396 | [0.701, 0.776] | 0.6272 | 0.9011 | 625 |
| image-t0.7 | 10 | 6 | 0.7530 | [0.713, 0.787] | 0.6603 | 0.8759 | 577 |
| image-t0.7 | 10 | 7 | 0.7464 | [0.707, 0.781] | 0.6766 | 0.8322 | 535 |
| image-t0.7 | 10 | 8 | 0.7470 | [0.706, 0.784] | 0.7024 | 0.7977 | 494 |
| image-t0.7 | 10 | 9 | 0.7289 | [0.689, 0.767] | 0.7223 | 0.7356 | 443 |
| image-t0.7 | 10 | 10 | 0.6834 | [0.639, 0.723] | 0.7535 | 0.6253 | 361 |

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
