# Consensus Voting Sweep Analysis

**Generated**: 2026-03-26T12:47:58.103976+00:00  
**Bootstrap iterations**: 1000  
**Random seed**: 42  
**Baseline F1**: 0.5574

## Key Finding

Consensus voting **improves** over single-run baseline. Best configuration: image-t0.7 N=10 x=6 achieves F1=0.7332 (+0.1758 vs baseline).

## Per-Temperature Optima

| Temp | N | x | F1 | 95% CI | P | R | n_det | dF1 |
|------|---:|---:|----:|:------:|----:|----:|------:|----:|
| image-t0.7 | 10 | 6 | 0.7332 | [0.692, 0.770] | 0.6430 | 0.8529 | 577 | +0.1758 |

## Full Sweep Results

| Temp | N | x | F1 | 95% CI | P | R | n_det |
|------|---:|---:|----:|:------:|----:|----:|------:|
| image-t0.7 | 5 | 1 | 0.5173 | [0.476, 0.559] | 0.3589 | 0.9264 | 1123 |
| image-t0.7 | 5 | 2 | 0.6426 | [0.598, 0.680] | 0.5066 | 0.8782 | 754 |
| image-t0.7 | 5 | 3 | 0.7053 | [0.664, 0.741] | 0.6013 | 0.8529 | 617 |
| image-t0.7 | 5 | 4 | 0.7244 | [0.681, 0.763] | 0.6635 | 0.7977 | 523 |
| image-t0.7 | 5 | 5 | 0.7030 | [0.661, 0.744] | 0.7096 | 0.6966 | 427 |
| image-t0.7 | 10 | 1 | 0.4308 | [0.391, 0.472] | 0.2800 | 0.9333 | 1450 |
| image-t0.7 | 10 | 2 | 0.5811 | [0.538, 0.621] | 0.4233 | 0.9264 | 952 |
| image-t0.7 | 10 | 3 | 0.6535 | [0.613, 0.690] | 0.5097 | 0.9103 | 777 |
| image-t0.7 | 10 | 4 | 0.6890 | [0.649, 0.725] | 0.5595 | 0.8966 | 697 |
| image-t0.7 | 10 | 5 | 0.7170 | [0.675, 0.758] | 0.6080 | 0.8736 | 625 |
| image-t0.7 | 10 | 6 | 0.7332 | [0.692, 0.770] | 0.6430 | 0.8529 | 577 |
| image-t0.7 | 10 | 7 | 0.7278 | [0.687, 0.765] | 0.6598 | 0.8115 | 535 |
| image-t0.7 | 10 | 8 | 0.7277 | [0.685, 0.765] | 0.6842 | 0.7770 | 494 |
| image-t0.7 | 10 | 9 | 0.7175 | [0.675, 0.756] | 0.7111 | 0.7241 | 443 |
| image-t0.7 | 10 | 10 | 0.6734 | [0.630, 0.714] | 0.7424 | 0.6161 | 361 |

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
