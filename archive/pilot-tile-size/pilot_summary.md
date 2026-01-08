# Tile Size Pilot: Analysis Summary

Generated: 2026-01-07T06:53:26.665948+00:00

## Overview

- Total tiles analysed: 210
- Tile sizes tested: 256px, 512px, 1024px
- Voting thresholds: 1/5 to 5/5
- Spatial tolerance: 20m
- Bootstrap iterations: 1000

**Note:** Ground truth filtered to valid comparison region (48px margins on 1024 tiles,
scaled proportionally for smaller tiles). This ensures fair comparison across tile sizes
by excluding edge mounds that smaller tile grids don't fully cover.

## Results by Tile Size

### 256px Tiles

| Threshold | Precision | Recall | F1 | TP | FP | FN |
|-----------|-----------|--------|----|----|----|----|
| 1/5 | 0.031 [0.015-0.051] | 0.903 [0.762-1.000] | 0.059 [0.030-0.097] | 19 | 603 | 2 |
| 2/5 | 0.098 [0.048-0.155] | 0.854 [0.682-1.000] | 0.174 [0.090-0.264] | 18 | 167 | 3 |
| 3/5 | 0.153 [0.070-0.247] | 0.810 [0.615-0.952] | 0.255 [0.128-0.383] | 17 | 95 | 4 |
| 4/5 | 0.226 [0.106-0.371] | 0.671 [0.458-0.857] | 0.333 [0.179-0.494] | 14 | 49 | 7 |
| 5/5 | 0.286 [0.119-0.500] | 0.481 [0.273-0.688] | 0.350 [0.175-0.531] | 10 | 26 | 11 |

### 512px Tiles

| Threshold | Precision | Recall | F1 | TP | FP | FN |
|-----------|-----------|--------|----|----|----|----|
| 1/5 | 0.060 [0.023-0.120] | 0.952 [0.864-1.000] | 0.112 [0.045-0.213] | 19 | 312 | 1 |
| 2/5 | 0.151 [0.042-0.317] | 0.736 [0.444-0.929] | 0.245 [0.077-0.447] | 15 | 91 | 5 |
| 3/5 | 0.261 [0.080-0.530] | 0.643 [0.389-0.857] | 0.360 [0.135-0.611] | 13 | 40 | 7 |
| 4/5 | 0.478 [0.150-0.792] | 0.492 [0.200-0.741] | 0.474 [0.182-0.710] | 10 | 11 | 10 |
| 5/5 | 0.839 [0.400-1.000] | 0.293 [0.100-0.455] | 0.427 [0.166-0.615] | 6 | 1 | 14 |

### 1024px Tiles

| Threshold | Precision | Recall | F1 | TP | FP | FN |
|-----------|-----------|--------|----|----|----|----|
| 1/5 | 0.031 [0.006-0.086] | 0.630 [0.462-0.800] | 0.057 [0.013-0.151] | 12 | 444 | 7 |
| 2/5 | 0.218 [0.048-0.474] | 0.461 [0.182-0.714] | 0.284 [0.078-0.479] | 9 | 33 | 10 |
| 3/5 | 0.471 [0.167-1.000] | 0.367 [0.154-0.714] | 0.380 [0.174-0.556] | 7 | 9 | 12 |
| 4/5 | 0.613 [0.000-1.000] | 0.154 [0.000-0.333] | 0.229 [0.000-0.414] | 3 | 2 | 16 |
| 5/5 | 0.640 [0.000-1.000] | 0.103 [0.000-0.200] | 0.173 [0.000-0.303] | 2 | 1 | 17 |

## Comparison at 2/5 Threshold

| Size | Precision | Recall | F1 |
|------|-----------|--------|-------|
| 256px | 0.098 | 0.854 | 0.174 |
| 512px | 0.151 | 0.736 | 0.245 |
| 1024px | 0.218 | 0.461 | 0.284 |

## Decision Criteria

Per the pre-registration:

| Comparison | Condition | Action |
|------------|-----------|--------|
| 256 vs 512 | 256px F1 ≥ 0.05 better | Switch to 256px |
| 256 vs 512 | Within 0.03 | Stay at 512px |
| 1024 vs 512 | 1024px F1 ≥ 0.10 worse | Confirms smaller better |
| 1024 vs 512 | Within 0.05 | Consider 1024px for context |

## Automated Assessment

- F1(256px) - F1(512px) = -0.0709
- F1(1024px) - F1(512px) = +0.0387

**Recommendation**: Stay with 512px tiles (512px performs better)
