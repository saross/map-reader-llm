# Neutral Filename Mapping

Symlinks with neutral names to prevent semantic leakage in image-only prompts.

## Scale-8 Library Composition (17 Examples)

The Scale-8 library (`library_scale-8.json`) uses the following structure:

| Category | Count | Example Range | Description |
|----------|-------|---------------|-------------|
| Canonical Positive | 4 | 01-04 | Legend-derived mound symbols |
| Hard Positive | 4 | 05-08 | Edge cases mined from training FNs |
| Canonical Negative | 2 | 09-10 | Legend-derived confusable symbols |
| Hard Negative | 4 | 11-14 | Confusables mined from training FPs |
| Null | 3 | 15-17 | Empty tiles (no mounds present) |

---

## Canonical Positives (Examples 01-04)

Legend-derived exemplar mound symbols from official Soviet cartographic standards.

| Neutral Name | Actual File | Category | Source |
|--------------|-------------|----------|--------|
| example_01.png | legend-positive/burial_mound.png | canonical_positive | Legend |
| example_02.png | legend-positive/settlement_mound.png | canonical_positive | Legend |
| example_03.png | legend-positive/triangulation_mound.png | canonical_positive | Legend |
| example_04.png | legend-positive/benchmark_mound.png | canonical_positive | Legend |

---

## Hard Positives (Examples 05-08)

Edge cases: genuine mound symbols that may be missed due to occlusion, degradation, or
atypical appearance. Derived from False Negatives in Phase 1 baseline analysis.

**Selection criteria** (adapted from preregistration §8.4.2, revised Session 7):

- All 24 FNs were complete misses (0/5 passes detected them)
- Ranked by two dimensions: (1) frequency, (2) distance to nearest detection
- **Recognition failures prioritised** (>50m from any detection) over localisation failures (20-50m), since localisation failures would be hits at production tolerances (~50m / 10px)
- Minimum ~5px edge clearance required (truncated symbols excluded)
- One-per-sheet stratification relaxed: Lesovo and K-35-052-4 had no recognition failures among calibration FNs, so examples double up on Rakovski (2) and Elenovo (2)
- **Crop size**: 128×128 pixels. At ~5m/px, a 15-20px mound symbol occupies ~1-2.5% of crop area — sufficient context without drowning the feature. Flagged as future OFAT variable (64, 128, 256, 512px).
- **Crop source**: Centred on reference mound coordinate, extracted from full map GeoTIFF (`inputs/rasters/*.tif`), not from detection tiles. Target symbol is always at the crop centre. See errata E8 for rationale.
- See `outputs/phase1-library/fp-fn-register.md` for full ranking and Decision 4 for rationale

| Neutral Name | Actual File | Category | Crop Source | FN Tile | fid | Map | Nearest Det. |
|--------------|-------------|----------|-------------|---------|-----|-----|-------------|
| example_05.png | hard-positive/example_05_rakovski.png | hard_positive | K-35-062-2_Rakovski.tif | x448_y2688 | 399 | Rakovski | 1243.1m |
| example_06.png | hard-positive/example_06_elenovo.png | hard_positive | K-35-053-3_Elenovo.tif | x896_y1344 | 99 | Elenovo | 1047.1m |
| example_07.png | hard-positive/example_07_rakovski.png | hard_positive | K-35-062-2_Rakovski.tif | x896_y2688 | 15 | Rakovski | 905.6m |
| example_08.png | hard-positive/example_08_elenovo.png | hard_positive | K-35-053-3_Elenovo.tif | x896_y1344 | 105 | Elenovo | 243.6m |

---

## Canonical Negatives (Examples 09-10)

Legend-derived symbols that visually resemble mound markers but represent standalone
survey markers (triangulation point, bench mark) without an associated mound.

| Neutral Name | Actual File | Category | Source |
|--------------|-------------|----------|--------|
| example_09.png | legend-negative/standalone_triangulation.png | canonical_negative | Legend |
| example_10.png | legend-negative/standalone_benchmark.png | canonical_negative | Legend |

---

## Hard Negatives (Examples 11-14)

Confusable symbols identified from False Positives in Phase 1 analysis. These are map
features that the model mistakenly identifies as mounds.

**Selection criteria** (adapted from preregistration §8.4.2, revised Session 8):

- Vote 5/5 (detected in all passes) — most systematic false alarms
- Ranked by two dimensions: (1) vote count, (2) distance to nearest reference
- **Hallucinations prioritised** (>500m from any ground truth reference) over near-misses/marginal FPs, since near-misses are localisation errors rather than genuine recognition errors (analogous to the hard positive selection principle)
- One per map sheet for diversity
- **Crop size**: 128×128 pixels, consistent with hard positives. At ~5m/px, crops cover ~640m × 640m — sufficient context to show what confused the model.
- **Crop source**: Centred on FP detection coordinate, extracted from full map GeoTIFF (`inputs/rasters/*.tif`), not from detection tiles. The confusing feature is at or near the crop centre. See errata E8 for rationale.
- See `outputs/phase1-library/fp-fn-register.md` for full ranking

| Neutral Name | Actual File | Category | Crop Source | FP Tile | Subtype | Map | Nearest Ref. |
|--------------|-------------|----------|-------------|---------|---------|-----|-------------|
| example_11.png | hard-negative/example_11_rakovski.png | hard_negative | K-35-062-2_Rakovski.tif | x0_y3136 | burial_mound | Rakovski | 1896.0m |
| example_12.png | hard-negative/example_12_lesovo.png | hard_negative | K-35-078-1_Lesovo.tif | x1344_y896 | triangulation_mound | Lesovo | 1807.8m |
| example_13.png | hard-negative/example_13_k-35-052-4.png | hard_negative | K-35-052-4_32635.tif | x1344_y1344 | burial_mound | K-35-052-4 | 872.9m |
| example_14.png | hard-negative/example_14_elenovo.png | hard_negative | K-35-053-3_Elenovo.tif | x3136_y3136 | burial_mound | Elenovo | 725.0m |

---

## Null Tiles (Examples 15-17)

Training tiles containing no mound symbols. Selected from regions with typical map
features (contours, roads, settlements) but confirmed empty.

| Neutral Name | Actual File | Category | Source |
|--------------|-------------|----------|--------|
| example_15.png | null-tiles/null_lesovo.png | null | Training tile (empty) |
| example_16.png | null-tiles/null_elenovo.png | null | Training tile (empty) |
| example_17.png | null-tiles/null_32635.png | null | Training tile (empty) |

---

## Expanded Hard Negative Pool (Examples 18-29)

Additional hard negative crops for H9 diversity rotation. These are NOT used in Scale-8
or other fixed library configs — they expand the rotation pool so that H9-C (image
diversity) can present different HN subsets across voting passes.

**Selection criteria**: Same two-dimensional ranking as core HNs (vote count descending,
distance to nearest reference descending), filtered to >50m from nearest ground truth
reference. Extends from where the core set (examples 11-14) leaves off.

**Crop source**: 128×128 pixels centred on FP detection coordinate, extracted from full
map GeoTIFF. Same methodology as core HNs (see errata E8).

| Neutral Name | Actual File | Category | Crop Source | FP Tile | Subtype | Map | Vote | Nearest Ref. |
|--------------|-------------|----------|-------------|---------|---------|-----|------|-------------|
| example_18.png | hard-negative/example_18_elenovo.png | hard_negative_pool | K-35-053-3_Elenovo.tif | x2240_y2240 | burial_mound | Elenovo | 4/5 | 1117.8m |
| example_19.png | hard-negative/example_19_elenovo.png | hard_negative_pool | K-35-053-3_Elenovo.tif | x2240_y3584 | benchmark_mound | Elenovo | 4/5 | 916.3m |
| example_20.png | hard-negative/example_20_lesovo.png | hard_negative_pool | K-35-078-1_Lesovo.tif | x3136_y2688 | burial_mound | Lesovo | 3/5 | 5922.4m |
| example_21.png | hard-negative/example_21_lesovo.png | hard_negative_pool | K-35-078-1_Lesovo.tif | x896_y3136 | burial_mound | Lesovo | 3/5 | 2259.4m |
| example_22.png | hard-negative/example_22_k-35-052-4.png | hard_negative_pool | K-35-052-4_32635.tif | x1344_y1344 | burial_mound | K-35-052-4 | 3/5 | 57.8m |
| example_23.png | hard-negative/example_23_k-35-052-4.png | hard_negative_pool | K-35-052-4_32635.tif | x1344_y1344 | burial_mound | K-35-052-4 | 3/5 | 50.3m |
| example_24.png | hard-negative/example_24_lesovo.png | hard_negative_pool | K-35-078-1_Lesovo.tif | x3584_y3136 | burial_mound | Lesovo | 2/5 | 7901.1m |
| example_25.png | hard-negative/example_25_lesovo.png | hard_negative_pool | K-35-078-1_Lesovo.tif | x896_y3136 | burial_mound | Lesovo | 2/5 | 2224.9m |
| example_26.png | hard-negative/example_26_lesovo.png | hard_negative_pool | K-35-078-1_Lesovo.tif | x896_y3136 | burial_mound | Lesovo | 2/5 | 2134.4m |
| example_27.png | hard-negative/example_27_elenovo.png | hard_negative_pool | K-35-053-3_Elenovo.tif | x896_y1344 | settlement_mound | Elenovo | 2/5 | 68.3m |
| example_28.png | hard-negative/example_28_elenovo.png | hard_negative_pool | K-35-053-3_Elenovo.tif | x896_y1344 | burial_mound | Elenovo | 2/5 | 57.8m |
| example_29.png | hard-negative/example_29_lesovo.png | hard_negative_pool | K-35-078-1_Lesovo.tif | x3584_y3136 | burial_mound | Lesovo | 1/5 | 8773.3m |

**Pool composition by vote count**: 4/5 × 2, 3/5 × 4, 2/5 × 5, 1/5 × 1

**Pool composition by map sheet**: Lesovo × 6, Elenovo × 4, K-35-052-4 × 2

---

## Usage

Library configs reference examples by neutral name:

| Config | Examples Used | Purpose |
|--------|---------------|---------|
| `library_pure-positive-canon.json` | 01-04, 15-17 | Minimal baseline (Canon+ and null only) |
| `library_canonical.json` | 01-04, 09-10, 15-17 | Tests +Canon- effect |
| `library_plus-hp.json` | 01-08, 09-10, 15-17 | Tests +HP effect |
| `library_scale-4.json` | 01-04, 09-10, 11-12, 15-17 | Scale-4: 2 HN |
| `library_scale-8.json` | 01-17 (all) | Scale-8: 4 HP, 4 HN (default) |
| `library_scale-16.json` | Extended pool | Scale-16: 8 HP, 8 HN (deferred) |
| `library_scale-32.json` | Extended pool | Scale-32: 16 HP, 16 HN (deferred) |

### H5 Testing

All H5 conditions (Minimal, Terse, Verbose) use the Scale-8 library by default. The
text treatment varies but the visual examples remain constant.

### H8 Testing

H8 tests library composition effects by varying the number of hard examples. See
`prompts/configs/library_*.json` for exact compositions.

### H9 Diversity Rotation

H9-C (image diversity) rotates HN examples across voting passes. The rotation pool
comprises all 16 HN crops (examples 11-14 core + examples 18-29 expanded pool). Each
pass receives 4 HN examples drawn from this pool subject to the preregistered frequency
constraints (each HN appears in ≥1 and ≤3 of 5 passes). HP examples (05-08) are frozen:
all 4 appear in every pass due to pool exhaustion.

---

## Symlink Status

| Examples | Status | Notes |
|----------|--------|-------|
| 01-04 | Created | Canonical positives from legend |
| 05-08 | Revised (2026-02-02) | Hard positives from Phase 1 FN analysis — recognition failures; 2 Rakovski, 2 Elenovo (see Decision 4) |
| 09-10 | Created | Canonical negatives from legend |
| 11-14 | Revised (2026-02-02) | Hard negatives (core) from Phase 1 FP analysis — vote 5/5 hallucinations, one per sheet; re-extracted as 128×128 crops from GeoTIFFs centred on FP detection coordinates |
| 15-17 | Created | Null tiles selected |
| 18-29 | Created (2026-02-02) | Hard negatives (expanded pool) for H9 diversity rotation — vote 4/5 to 1/5 FPs ranked by vote count and distance, >50m from nearest reference |

**Last updated**: 2026-02-02 (expanded HN pool extracted for H9 diversity rotation; 12 new crops added as examples 18-29)

---

## Provenance Documentation

When hard examples are populated after Phase 1, document for each:

1. **Source tile**: Which training tile the crop came from
2. **Coordinates**: Pixel or geographic location within tile
3. **Selection metric**: Miss/detection frequency across passes
4. **Visual characteristics**: Why this example is "hard" (occlusion, degradation, etc.)

This provenance will be recorded in `docs/methodology/preregistration/decisions-log.md`.
