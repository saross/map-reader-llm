# Evaluation Tile Set Scopes

**Purpose**: Documents the three test tile sets used across the experimental
programme and their nesting relationships. Critical context for interpreting
F1 comparisons across project phases and for the paper write-up.

**Generated**: 2026-04-16
**Verified by**: spatial intersection analysis (zero-tolerance nesting check)

## The three test tile sets

All three sets cover 4 topographic map sheets from Bulgaria (1:25,000 Soviet
military series, UTM Zone 35N / EPSG:32635):

- K-35-052-4 (Razgrad area)
- K-35-053-3 (Elenovo area)
- K-35-062-2 (Rakovski area)
- K-35-078-1 (Lesovo area)

| Label | Era | Tile size | Stride | Test tiles | Area (sq km) | GT mounds | Calibration excluded | Manifest path |
|---|---|---|---|---|---|---|---|---|
| **Era 1** | Pre-H11 (H1–H9 retest) | 512 px | 448 px | **340** | 1751 | 539 | 20 tiles (original calibration seed area) | `inputs/vectors/bounds/full_evaluation_bounds.geojson` |
| **Era 2** | H11 | 384 px | 336 px | **487** | 1416 | 435 | Same 20-tile geographic area as Era 1, re-projected to the 384-px grid | `inputs/tiles_384/full_evaluation_manifest.json` + `inputs/vectors/bounds/384/full_evaluation_bounds.geojson` |
| **Era 3** | Post-H10 v2 (H8 v2, H10 v2, H12 v2) | 384 px | 336 px | **327** | 1034 | 319 | Era 2 exclusion **plus** 160 pool_160 tiles (hard-example mining area, geographically separate from the Era 1/2 calibration exclusion) | `inputs/calibration/h10-384/test_manifest.json` + `inputs/vectors/bounds/384/h10_test_bounds.geojson` |

### Physical tile counts (for reference)

| Tile size | Physical tiles on disk | Edge/boundary excluded | Evaluable tiles | Calibration excluded | Test tiles |
|---|---|---|---|---|---|
| 512 px | 360 | 0 | 360 | 20 | **340** |
| 384 px | 611 | 124 | 487 | 0 (Era 2) or 160 (Era 3) | **487** or **327** |

## Nesting verification

The three test tile sets are **strictly nested**: Era 3 ⊂ Era 2 ⊂ Era 1,
both geographically (zero area outside the parent) and in ground-truth mound
coverage (zero mounds unique to a smaller scope).

| Check | Result |
|---|---|
| Era 3 area inside Era 2 | 100.000% (0.00 sq m outside) |
| Era 2 area inside Era 1 | 100.000% (0.00 sq m outside) |
| Era 3 area inside Era 1 | 100.000% (0.00 sq m outside) |
| Mounds in Era 3 but not Era 2 | 0 |
| Mounds in Era 2 but not Era 1 | 0 |
| Mounds in Era 3 but not Era 1 | 0 |

## Comparative coverage

| Comparison | % area covered | % mounds covered |
|---|---|---|
| Era 2 within Era 1 | **80.8%** | **80.7%** |
| Era 3 within Era 2 | **73.0%** | **73.3%** |
| Era 3 within Era 1 | **59.0%** | **59.2%** |

Area and mound fractions track near-identically (within 0.3 percentage
points), indicating that the calibration exclusions do not preferentially
remove mound-rich or mound-poor regions. Mound density is approximately
uniform across all three scopes.

## Calibration exclusion rationale

### Era 1 exclusion (20 × 512-px tiles)

The original 20-tile calibration set was used in Phase 1 (library
construction) to build the canonical few-shot library (4 positive + 2
negative legend-derived examples, 3 null tiles). These tiles were excluded
from the evaluation set to prevent testing the model on the same map regions
used to construct its few-shot prompt. The 20 calibration tiles plus 340 test
tiles account for all 360 physical 512-px tiles.

### Era 2 exclusion (same geographic area, re-projected)

When the project moved to 384-px tiles (H11, errata E41), the same 20-tile
calibration geographic footprint was excluded from the 384-px evaluation set.
Because 384-px tiles are smaller (336-px stride vs 448-px stride), the
exclusion removes more tiles from the grid, resulting in 487 evaluable tiles
from 611 physical tiles (with an additional 124 edge/boundary tiles excluded
by the tiling geometry). The 487-tile set has zero overlap with the 512-px
calibration footprint (verified by spatial intersection).

### Era 3 additional exclusion (160 × 384-px pool_160 tiles)

H10 v2 expanded the calibration pool from the original 20-tile seed to a
160-tile set (pool_160) for hard-example mining. This expansion drew tiles
from a **geographically separate** area within the 487-tile evaluation set —
the pool_160 tiles do not overlap the original 20-tile calibration footprint.
Hard positive and hard negative few-shot crops (150 × 150 px) were extracted
from specific locations within these 160 tiles. To prevent data leakage
(testing the model on tiles from which its few-shot examples were drawn), the
160 pool_160 tiles were excluded, yielding the 327-tile h10 test set.

The pool_160 calibration hierarchy is nested:
pool_020 ⊂ pool_040 ⊂ pool_080 ⊂ pool_160 (20, 40, 80, 160 tiles).

## Hypotheses by era

| Era | Scope | Hypotheses evaluated |
|---|---|---|
| Era 1 (340 × 512) | Pre-H11 retest at production scale | H1 (modality/elaboration), H2 (two-stage PV), H3 (consensus voting), H4 (ordering), H5 (negative text), H7 (temperature), H8 original (library, scale-4..8 only), H9 (diversity) |
| Era 2 (487 × 384) | H11 tile-size study and PV diagnostic | H11 (tile size), PV strategy comparison (adversarial/brief/checklist × image/text), consensus N-sweep (N=5, 10, 30), Flash vs Pro model comparison |
| Era 3 (327 × 384) | Post-H10 v2 library-design axis | H8 v2 (library composition, 7 conditions including Scale-16/32), H10 v2 (calibration-pool size, 4 conditions), H12 v2 (HP:HN ratio, 3 conditions) |

## Cross-era comparison notes

- **F1 numbers from different eras are not directly comparable** without
  noting the scope difference. The nested structure means a smaller scope
  evaluates against fewer mounds and fewer tiles; between-scope F1
  differences could reflect scope effects rather than configuration effects.
- **Within-era comparisons are always valid** — conditions tested in the same
  era share the same evaluation scope.
- **Tile size is a controlled variable** in the H11 study (Era 2), which
  tested the same configurations at both 512 and 384 px. Those results
  provide the calibrating link for any cross-tile-size comparison.
- **The 80.8% / 73.0% / 59.0% coverage fractions** and the near-identical
  mound-density ratios mean that cross-era F1 differences attributable purely
  to scope are expected to be small — but they should still be footnoted
  in leaderboard tables.

## File reference

| File | Description |
|---|---|
| `inputs/vectors/bounds/full_evaluation_bounds.geojson` | Era 1 bounds (340 tiles, 512 px) |
| `inputs/vectors/bounds/calibration_bounds.geojson` | Era 1 calibration exclusion (20 tiles, 512 px) |
| `inputs/vectors/bounds/384/full_evaluation_bounds.geojson` | Era 2 bounds (487 tiles, 384 px) |
| `inputs/tiles_384/full_evaluation_manifest.json` | Era 2 tile manifest (487 tiles) |
| `inputs/vectors/bounds/384/h10_test_bounds.geojson` | Era 3 bounds (327 tiles, 384 px) |
| `inputs/calibration/h10-384/test_manifest.json` | Era 3 tile manifest (327 tiles) |
| `inputs/calibration/h10-384/calibration_bounds_160.geojson` | Era 3 calibration exclusion (160 tiles, pool_160) |
| `inputs/vectors/references/mounds-reference.geojson` | Ground-truth mound reference (569 total mounds across all maps) |
