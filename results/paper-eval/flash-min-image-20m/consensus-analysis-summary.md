# Consensus Voting Sweep Analysis

**Generated**: 2026-03-26T12:47:46.564866+00:00  
**Bootstrap iterations**: 1000  
**Random seed**: 42  
**Baseline F1**: 0.5574

## Key Finding

Consensus voting **improves** over single-run baseline. Best configuration: image-t0.7 N=10 x=8 achieves F1=0.6803 (+0.1229 vs baseline).

## Per-Temperature Optima

| Temp | N | x | F1 | 95% CI | P | R | n_det | dF1 |
|------|---:|---:|----:|:------:|----:|----:|------:|----:|
| image-t0.7 | 10 | 8 | 0.6803 | [0.634, 0.723] | 0.6397 | 0.7264 | 494 | +0.1229 |

## Full Sweep Results

| Temp | N | x | F1 | 95% CI | P | R | n_det |
|------|---:|---:|----:|:------:|----:|----:|------:|
| image-t0.7 | 5 | 1 | 0.4801 | [0.440, 0.521] | 0.3330 | 0.8598 | 1123 |
| image-t0.7 | 5 | 2 | 0.5870 | [0.546, 0.627] | 0.4629 | 0.8023 | 754 |
| image-t0.7 | 5 | 3 | 0.6445 | [0.602, 0.683] | 0.5494 | 0.7793 | 617 |
| image-t0.7 | 5 | 4 | 0.6639 | [0.619, 0.706] | 0.6080 | 0.7310 | 523 |
| image-t0.7 | 5 | 5 | 0.6566 | [0.611, 0.699] | 0.6628 | 0.6506 | 427 |
| image-t0.7 | 10 | 1 | 0.4053 | [0.366, 0.445] | 0.2634 | 0.8782 | 1450 |
| image-t0.7 | 10 | 2 | 0.5407 | [0.500, 0.581] | 0.3939 | 0.8621 | 952 |
| image-t0.7 | 10 | 3 | 0.6040 | [0.563, 0.643] | 0.4710 | 0.8414 | 777 |
| image-t0.7 | 10 | 4 | 0.6360 | [0.595, 0.676] | 0.5165 | 0.8276 | 697 |
| image-t0.7 | 10 | 5 | 0.6604 | [0.617, 0.701] | 0.5600 | 0.8046 | 625 |
| image-t0.7 | 10 | 6 | 0.6759 | [0.633, 0.716] | 0.5927 | 0.7862 | 577 |
| image-t0.7 | 10 | 7 | 0.6784 | [0.634, 0.720] | 0.6150 | 0.7563 | 535 |
| image-t0.7 | 10 | 8 | 0.6803 | [0.634, 0.723] | 0.6397 | 0.7264 | 494 |
| image-t0.7 | 10 | 9 | 0.6697 | [0.624, 0.713] | 0.6637 | 0.6759 | 443 |
| image-t0.7 | 10 | 10 | 0.6307 | [0.585, 0.676] | 0.6953 | 0.5770 | 361 |

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
