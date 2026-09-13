# Preregistration per-tile mound counts — post-hoc recomputation

> **GENERATED** by `scripts/recount_prereg_tile_mounds.py`. Do not hand-edit; regenerate.
>
> **Last revised**: 2026-09-13 (first publication, under erratum E87). See [§ Changelog](#changelog) for revision history.

**POST-HOC CORRECTION.** The Open Science Framework (OSF) registration is immutable. The counts below do **not** replace the lodged tables of preregistration §§ 2.3–2.5; they correct them on the errata register (**E87**). The tile *selections* are unchanged and no measured result reads these counts.

## Why the lodged counts are wrong

`scripts/select_tiles_phase2.py` estimates each sheet's map extent from the **bounding box of that sheet's reference points** and its pixel size from tile filenames; it never reads the raster affine. Because the references do not reach the sheet edges, the inferred extent is smaller than the sheet and every tile's map-coordinate window is shifted and scaled.

Two window sizes are reported. The **512 px** window is the whole tile; adjacent tiles share a 64 px overlap, so a sum of per-tile counts double-counts references in that band and a **union** counts distinct references. The **448 px core** is the tile minus its overlap; cores tile each sheet exactly, so their counts partition the reference layer — the generator asserts this (the 448 px cores of all 360 physical tiles account for 569 of 569 references exactly once).

## Totals

| Set | § | Tiles | Published | Affine 512 px (union) | Affine 512 px (sum) | Affine 448 px core |
| :-- | :-- | --: | --: | --: | --: | --: |
| calibration | 2.3 | 20 | 36 | 50 | 52 | 39 |
| holdout | 2.4 | 60 | 79 | 97 | 106 | 82 |

## The mechanism, demonstrated

Re-running the superseded approximation reproduces the published per-tile counts far better than the affine-correct computation does, which identifies it as the method that wrote the tables.

| Set | Rows | Approximation matches | Affine 512 px matches | Affine 448 px core matches |
| :-- | --: | --: | --: | --: |
| calibration | 20 | 10 | 7 | 7 |
| holdout | 60 | 35 | 24 | 28 |
| **all** | **80** | **45** | **31** | — |

## Per-tile counts — calibration set (preregistration § 2.3)

| Tile | Published | Affine 512 px | Affine 448 px core | Approximation reproduced |
| :-- | --: | --: | --: | --: |
| `K-35-052-4_32635_x1344_y1344.png` | 0 | 7 | 5 | 0 |
| `K-35-052-4_32635_x1344_y2240.png` | 2 | 2 | 2 | 3 |
| `K-35-052-4_32635_x2240_y2240.png` | 1 | 1 | 1 | 2 |
| `K-35-052-4_32635_x2240_y3584.png` | 3 | 2 | 2 | 3 |
| `K-35-052-4_32635_x3136_y896.png` | 0 | 3 | 1 | 0 |
| `K-35-053-3_Elenovo_x1792_y2240.png` | 4 | 10 | 9 | 6 |
| `K-35-053-3_Elenovo_x2240_y2240.png` | 11 | 1 | 1 | 13 |
| `K-35-053-3_Elenovo_x2240_y3584.png` | 1 | 0 | 0 | 3 |
| `K-35-053-3_Elenovo_x3136_y3136.png` | 0 | 1 | 1 | 0 |
| `K-35-053-3_Elenovo_x896_y1344.png` | 2 | 8 | 3 | 2 |
| `K-35-062-2_Rakovski_x0_y1792.png` | 2 | 1 | 1 | 4 |
| `K-35-062-2_Rakovski_x0_y3136.png` | 0 | 0 | 0 | 0 |
| `K-35-062-2_Rakovski_x448_y2688.png` | 3 | 2 | 2 | 5 |
| `K-35-062-2_Rakovski_x896_y2688.png` | 1 | 3 | 2 | 2 |
| `K-35-062-2_Rakovski_x896_y3136.png` | 4 | 8 | 8 | 7 |
| `K-35-078-1_Lesovo_x1344_y0.png` | 2 | 3 | 1 | 2 |
| `K-35-078-1_Lesovo_x1344_y896.png` | 0 | 0 | 0 | 1 |
| `K-35-078-1_Lesovo_x3136_y2688.png` | 0 | 0 | 0 | 0 |
| `K-35-078-1_Lesovo_x3584_y3136.png` | 0 | 0 | 0 | 0 |
| `K-35-078-1_Lesovo_x896_y3136.png` | 0 | 0 | 0 | 0 |

## Per-tile counts — holdout set (preregistration § 2.4)

| Tile | Published | Affine 512 px | Affine 448 px core | Approximation reproduced |
| :-- | --: | --: | --: | --: |
| `K-35-052-4_32635_x0_y0.png` | 1 | 1 | 1 | 1 |
| `K-35-052-4_32635_x0_y1344.png` | 1 | 4 | 3 | 1 |
| `K-35-052-4_32635_x0_y2240.png` | 9 | 13 | 11 | 13 |
| `K-35-052-4_32635_x1344_y3136.png` | 0 | 0 | 0 | 0 |
| `K-35-052-4_32635_x2240_y1344.png` | 1 | 0 | 0 | 1 |
| `K-35-052-4_32635_x2688_y0.png` | 0 | 0 | 0 | 0 |
| `K-35-052-4_32635_x3136_y0.png` | 0 | 0 | 0 | 0 |
| `K-35-052-4_32635_x3136_y2240.png` | 1 | 3 | 2 | 1 |
| `K-35-052-4_32635_x3136_y3584.png` | 0 | 1 | 1 | 0 |
| `K-35-052-4_32635_x3584_y3136.png` | 2 | 0 | 0 | 5 |
| `K-35-052-4_32635_x3584_y3584.png` | 3 | 0 | 0 | 3 |
| `K-35-052-4_32635_x448_y1344.png` | 1 | 4 | 4 | 3 |
| `K-35-052-4_32635_x448_y3136.png` | 0 | 0 | 0 | 0 |
| `K-35-052-4_32635_x448_y896.png` | 0 | 3 | 1 | 0 |
| `K-35-052-4_32635_x896_y3136.png` | 0 | 1 | 0 | 0 |
| `K-35-053-3_Elenovo_x0_y0.png` | 0 | 2 | 0 | 2 |
| `K-35-053-3_Elenovo_x0_y1344.png` | 0 | 1 | 0 | 1 |
| `K-35-053-3_Elenovo_x0_y2688.png` | 0 | 0 | 0 | 1 |
| `K-35-053-3_Elenovo_x0_y3136.png` | 0 | 0 | 0 | 0 |
| `K-35-053-3_Elenovo_x1792_y448.png` | 2 | 2 | 2 | 2 |
| `K-35-053-3_Elenovo_x2240_y448.png` | 1 | 1 | 1 | 2 |
| `K-35-053-3_Elenovo_x2688_y1344.png` | 0 | 2 | 0 | 0 |
| `K-35-053-3_Elenovo_x3136_y1344.png` | 0 | 1 | 1 | 0 |
| `K-35-053-3_Elenovo_x3584_y2240.png` | 3 | 7 | 6 | 6 |
| `K-35-053-3_Elenovo_x448_y0.png` | 1 | 5 | 3 | 3 |
| `K-35-053-3_Elenovo_x448_y2688.png` | 8 | 4 | 2 | 10 |
| `K-35-053-3_Elenovo_x448_y3136.png` | 3 | 2 | 2 | 4 |
| `K-35-053-3_Elenovo_x448_y448.png` | 4 | 4 | 3 | 4 |
| `K-35-053-3_Elenovo_x896_y2240.png` | 3 | 1 | 1 | 5 |
| `K-35-053-3_Elenovo_x896_y448.png` | 1 | 2 | 2 | 2 |
| `K-35-062-2_Rakovski_x1792_y0.png` | 5 | 5 | 4 | 7 |
| `K-35-062-2_Rakovski_x1792_y3584.png` | 0 | 0 | 0 | 1 |
| `K-35-062-2_Rakovski_x2240_y2240.png` | 5 | 5 | 5 | 6 |
| `K-35-062-2_Rakovski_x2240_y448.png` | 1 | 0 | 0 | 2 |
| `K-35-062-2_Rakovski_x2688_y1344.png` | 4 | 5 | 5 | 5 |
| `K-35-062-2_Rakovski_x2688_y2240.png` | 1 | 0 | 0 | 2 |
| `K-35-062-2_Rakovski_x2688_y2688.png` | 0 | 3 | 3 | 1 |
| `K-35-062-2_Rakovski_x3136_y1344.png` | 2 | 1 | 0 | 3 |
| `K-35-062-2_Rakovski_x3136_y1792.png` | 2 | 3 | 3 | 3 |
| `K-35-062-2_Rakovski_x3136_y2240.png` | 0 | 0 | 0 | 0 |
| `K-35-062-2_Rakovski_x3136_y3136.png` | 3 | 2 | 2 | 3 |
| `K-35-062-2_Rakovski_x3136_y896.png` | 2 | 1 | 1 | 2 |
| `K-35-062-2_Rakovski_x3584_y1344.png` | 0 | 4 | 3 | 1 |
| `K-35-062-2_Rakovski_x3584_y448.png` | 2 | 1 | 1 | 3 |
| `K-35-062-2_Rakovski_x448_y896.png` | 4 | 5 | 4 | 5 |
| `K-35-078-1_Lesovo_x0_y2688.png` | 0 | 0 | 0 | 0 |
| `K-35-078-1_Lesovo_x0_y3136.png` | 2 | 3 | 3 | 2 |
| `K-35-078-1_Lesovo_x1344_y2240.png` | 0 | 0 | 0 | 0 |
| `K-35-078-1_Lesovo_x2240_y1344.png` | 0 | 0 | 0 | 0 |
| `K-35-078-1_Lesovo_x2240_y3136.png` | 0 | 0 | 0 | 0 |
| `K-35-078-1_Lesovo_x2688_y1792.png` | 0 | 1 | 1 | 0 |
| `K-35-078-1_Lesovo_x2688_y896.png` | 0 | 0 | 0 | 0 |
| `K-35-078-1_Lesovo_x3136_y1344.png` | 0 | 0 | 0 | 0 |
| `K-35-078-1_Lesovo_x3136_y1792.png` | 1 | 0 | 0 | 1 |
| `K-35-078-1_Lesovo_x3136_y448.png` | 0 | 0 | 0 | 0 |
| `K-35-078-1_Lesovo_x3584_y0.png` | 0 | 2 | 1 | 0 |
| `K-35-078-1_Lesovo_x3584_y1344.png` | 0 | 0 | 0 | 0 |
| `K-35-078-1_Lesovo_x3584_y448.png` | 0 | 1 | 0 | 0 |
| `K-35-078-1_Lesovo_x448_y1792.png` | 0 | 0 | 0 | 0 |
| `K-35-078-1_Lesovo_x896_y1792.png` | 0 | 0 | 0 | 0 |

## Changelog

### 2026-09-13 — Original publication

Published under erratum **E87** (E87 remediation 2), alongside the machine-readable `tile-mound-counts-recomputed-2026-09-13.json`. Counts computed from the affine-derived tile origins in `inputs/tiles/<sheet>/metadata.json` against `inputs/vectors/references/mounds-reference.geojson` (569 symbols); the approximation column was produced by importing `select_tiles_phase2.load_map_georef` / `get_map_dimensions` / `count_mounds_in_tile` rather than re-implementing them.
