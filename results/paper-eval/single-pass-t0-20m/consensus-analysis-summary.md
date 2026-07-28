# Consensus Voting Sweep Analysis

**Generated**: 2026-03-26T12:48:33.763458+00:00  
**Bootstrap iterations**: 1000  
**Random seed**: 42  
**Baseline F1**: 0.5574

## Key Finding

Consensus voting does **not** improve over single-run baseline (F1=0.5574). Best consensus F1=0.5521 (-0.0053).

## Per-Temperature Optima

| Temp | N | x | F1 | 95% CI | P | R | n_det | dF1 |
|------|---:|---:|----:|:------:|----:|----:|------:|----:|
| brief-text-t0 | 10 | 10 | 0.5521 | [0.491, 0.610] | 0.4098 | 0.8460 | 898 | -0.0053 |

## Full Sweep Results

| Temp | N | x | F1 | 95% CI | P | R | n_det |
|------|---:|---:|----:|:------:|----:|----:|------:|
| brief-text-t0 | 5 | 1 | 0.5111 | [0.448, 0.567] | 0.3563 | 0.9034 | 1103 |
| brief-text-t0 | 5 | 2 | 0.5290 | [0.466, 0.585] | 0.3760 | 0.8920 | 1032 |
| brief-text-t0 | 5 | 3 | 0.5330 | [0.471, 0.591] | 0.3817 | 0.8828 | 1006 |
| brief-text-t0 | 5 | 4 | 0.5342 | [0.472, 0.591] | 0.3834 | 0.8805 | 999 |
| brief-text-t0 | 5 | 5 | 0.5440 | [0.481, 0.602] | 0.3964 | 0.8667 | 951 |
| brief-text-t0 | 10 | 1 | 0.4934 | [0.431, 0.550] | 0.3394 | 0.9034 | 1158 |
| brief-text-t0 | 10 | 2 | 0.5187 | [0.456, 0.576] | 0.3657 | 0.8920 | 1061 |
| brief-text-t0 | 10 | 3 | 0.5287 | [0.467, 0.585] | 0.3761 | 0.8897 | 1029 |
| brief-text-t0 | 10 | 4 | 0.5304 | [0.469, 0.588] | 0.3791 | 0.8828 | 1013 |
| brief-text-t0 | 10 | 5 | 0.5322 | [0.470, 0.590] | 0.3810 | 0.8828 | 1008 |
| brief-text-t0 | 10 | 6 | 0.5322 | [0.470, 0.590] | 0.3810 | 0.8828 | 1008 |
| brief-text-t0 | 10 | 7 | 0.5330 | [0.471, 0.590] | 0.3817 | 0.8828 | 1006 |
| brief-text-t0 | 10 | 8 | 0.5342 | [0.472, 0.592] | 0.3834 | 0.8805 | 999 |
| brief-text-t0 | 10 | 9 | 0.5416 | [0.480, 0.599] | 0.3920 | 0.8759 | 972 |
| brief-text-t0 | 10 | 10 | 0.5521 | [0.491, 0.610] | 0.4098 | 0.8460 | 898 |

## Methodology

For each (temperature, pool_size, threshold) combination:

1. Detection GeoDataFrames are converted to GeoJSON features
2. Within-run deduplication (20 m tolerance) removes overlapping-tile duplicates
3. Cross-run clustering (20 m tolerance) groups detections and counts votes
4. Vote threshold filters clusters by minimum agreement
5. Consensus centroids are spatially joined to tile boundaries for F1 evaluation
6. F1 evaluation uses 20 m spatial matching tolerance
7. Bootstrapped 95% CIs use tile-level resampling (K=1000 iterations)

Pool selection uses the first-N convention: N=5 uses runs 1-5, N=10 uses runs 1-10, and larger N take the first N runs. The preregistration (§3.8) specifies first-N pooling for N=5 and N=10 within a K=10 design and additionally specifies a second N=5 pool (runs 6-10) for an independent estimate; sub-pooling of larger run pools, and the omission of the second N=5 pool, are unregistered extensions (D17 audit U2).
