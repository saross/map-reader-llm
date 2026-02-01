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

**Selection criteria** (adapted from preregistration §8.4.2):

- All 24 FNs were complete misses (0/5 passes detected them)
- Ranked by two dimensions: (1) frequency, (2) distance to nearest detection
- Selected recognition failures (>50m from any detection), one per map sheet
- See `outputs/phase1-library/fp-fn-register.md` for full ranking

| Neutral Name | Actual File | Category | Source Tile | fid | Map | Nearest Det. |
|--------------|-------------|----------|-------------|-----|-----|-------------|
| example_05.png | hard-positive/example_05_rakovski.png | hard_positive | K-35-062-2_Rakovski_x0_y1344.png | 354 | Rakovski | 2449.9m |
| example_06.png | hard-positive/example_06_lesovo.png | hard_positive | K-35-078-1_Lesovo_x1344_y448.png | 249 | Lesovo | 1807.8m |
| example_07.png | hard-positive/example_07_k-35-052-4.png | hard_positive | K-35-052-4_32635_x2240_y3136.png | 556 | K-35-052-4 | 572.1m |
| example_08.png | hard-positive/example_08_elenovo.png | hard_positive | K-35-053-3_Elenovo_x896_y1344.png | 105 | Elenovo | 243.6m |

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

**Selection criteria** (adapted from preregistration §8.4.2):

- Vote 5/5 (detected in all passes) — most systematic false alarms
- Ranked by two dimensions: (1) vote count, (2) distance to nearest reference
- Selected hallucinations (>500m from any ground truth reference), one per map sheet
- See `outputs/phase1-library/fp-fn-register.md` for full ranking

| Neutral Name | Actual File | Category | Source Tile | Subtype | Map | Nearest Ref. |
|--------------|-------------|----------|-------------|---------|-----|-------------|
| example_11.png | hard-negative/example_11_rakovski.png | hard_negative | K-35-062-2_Rakovski_x0_y3136.png | burial_mound | Rakovski | 1896.0m |
| example_12.png | hard-negative/example_12_lesovo.png | hard_negative | K-35-078-1_Lesovo_x1344_y896.png | triangulation_mound | Lesovo | 1807.8m |
| example_13.png | hard-negative/example_13_k-35-052-4.png | hard_negative | K-35-052-4_32635_x1344_y1344.png | burial_mound | K-35-052-4 | 872.9m |
| example_14.png | hard-negative/example_14_elenovo.png | hard_negative | K-35-053-3_Elenovo_x3136_y3136.png | burial_mound | Elenovo | 725.0m |

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

## Usage

Library configs reference examples by neutral name:

| Config | Examples Used | Purpose |
|--------|---------------|---------|
| `library_pure-positive-canon.json` | 01-04, 15-17 | Minimal baseline (Canon+ and null only) |
| `library_canonical.json` | 01-04, 09-10, 15-17 | Tests +Canon- effect |
| `library_plus-hp.json` | 01-08, 09-10, 15-17 | Tests +HP effect |
| `library_scale-4.json` | 01-04, 09-10, 11-12, 15-17 | Scale-4: 2 HN |
| `library_scale-8.json` | 01-17 (all) | Scale-8: 4 HP, 4 HN (default) |
| `library_scale-16.json` | Extended pool | Scale-16: 8 HP, 8 HN |
| `library_scale-32.json` | Extended pool | Scale-32: 16 HP, 16 HN |

### H5 Testing

All H5 conditions (Minimal, Terse, Verbose) use the Scale-8 library by default. The
text treatment varies but the visual examples remain constant.

### H8 Testing

H8 tests library composition effects by varying the number of hard examples. See
`prompts/configs/library_*.json` for exact compositions.

---

## Symlink Status

| Examples | Status | Notes |
|----------|--------|-------|
| 01-04 | Created | Canonical positives from legend |
| 05-08 | Created (2026-02-01) | Hard positives from Phase 1 FN analysis — recognition failures, one per sheet |
| 09-10 | Created | Canonical negatives from legend |
| 11-14 | Created (2026-02-01) | Hard negatives from Phase 1 FP analysis — vote 5/5 hallucinations, one per sheet |
| 15-17 | Created | Null tiles selected |

**Last updated**: 2026-02-01 (hard examples populated from Phase 1 analysis)

---

## Provenance Documentation

When hard examples are populated after Phase 1, document for each:

1. **Source tile**: Which training tile the crop came from
2. **Coordinates**: Pixel or geographic location within tile
3. **Selection metric**: Miss/detection frequency across passes
4. **Visual characteristics**: Why this example is "hard" (occlusion, degradation, etc.)

This provenance will be recorded in `docs/methodology/preregistration/decisions-log.md`.
