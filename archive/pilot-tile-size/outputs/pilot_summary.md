# Tile Size Pilot: Analysis Summary

Generated: 2026-01-07T12:23:10.006291+00:00

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
| 1/5 | 0.032 [0.009-0.063] | 0.949 [0.857-1.000] | 0.062 [0.019-0.118] | 18 | 556 | 1 |
| 2/5 | 0.096 [0.031-0.176] | 0.901 [0.823-1.000] | 0.171 [0.059-0.292] | 17 | 164 | 2 |
| 3/5 | 0.159 [0.049-0.290] | 0.901 [0.823-1.000] | 0.265 [0.094-0.439] | 17 | 93 | 2 |
| 4/5 | 0.249 [0.073-0.458] | 0.797 [0.700-1.000] | 0.367 [0.133-0.576] | 15 | 48 | 4 |
| 5/5 | 0.347 [0.091-0.643] | 0.632 [0.400-0.833] | 0.429 [0.163-0.650] | 12 | 25 | 7 |

### 512px Tiles

| Threshold | Precision | Recall | F1 | TP | FP | FN |
|-----------|-----------|--------|----|----|----|----|
| 1/5 | 0.061 [0.017-0.124] | 0.947 [0.833-1.000] | 0.114 [0.033-0.221] | 18 | 294 | 1 |
| 2/5 | 0.163 [0.044-0.333] | 0.792 [0.643-1.000] | 0.263 [0.083-0.469] | 15 | 86 | 4 |
| 3/5 | 0.258 [0.083-0.478] | 0.688 [0.464-1.000] | 0.363 [0.149-0.593] | 13 | 39 | 6 |
| 4/5 | 0.442 [0.091-0.792] | 0.508 [0.187-0.880] | 0.459 [0.133-0.750] | 10 | 12 | 9 |
| 5/5 | 0.812 [0.000-1.000] | 0.301 [0.000-0.500] | 0.431 [0.000-0.645] | 6 | 1 | 13 |

### 1024px Tiles

| Threshold | Precision | Recall | F1 | TP | FP | FN |
|-----------|-----------|--------|----|----|----|----|
| 1/5 | 0.066 [0.014-0.146] | 0.634 [0.389-1.000] | 0.117 [0.027-0.247] | 12 | 182 | 7 |
| 2/5 | 0.284 [0.100-0.414] | 0.371 [0.143-0.636] | 0.311 [0.125-0.425] | 7 | 17 | 12 |
| 3/5 | 0.576 [0.000-1.000] | 0.264 [0.000-0.625] | 0.340 [0.000-0.615] | 5 | 4 | 14 |
| 4/5 | 0.376 [0.000-0.600] | 0.147 [0.000-0.462] | 0.202 [0.000-0.522] | 3 | 2 | 16 |
| 5/5 | 0.627 [0.000-1.000] | 0.049 [0.000-0.154] | 0.089 [0.000-0.267] | 1 | 0 | 18 |

## Comparison at 2/5 Threshold

| Size | Precision | Recall | F1 |
|------|-----------|--------|-------|
| 256px | 0.096 | 0.901 | 0.171 |
| 512px | 0.163 | 0.792 | 0.263 |
| 1024px | 0.284 | 0.371 | 0.311 |

## Decision Criteria

Per the pre-registration:

| Comparison | Condition | Action |
|------------|-----------|--------|
| 256 vs 512 | 256px F1 ≥ 0.05 better | Switch to 256px |
| 256 vs 512 | Within 0.03 | Stay at 512px |
| 1024 vs 512 | 1024px F1 ≥ 0.10 worse | Confirms smaller better |
| 1024 vs 512 | Within 0.05 | Consider 1024px for context |

## Automated Assessment

- F1(256px) - F1(512px) = -0.0916
- F1(1024px) - F1(512px) = +0.0485

**Recommendation**: Stay with 512px tiles (512px performs better)
