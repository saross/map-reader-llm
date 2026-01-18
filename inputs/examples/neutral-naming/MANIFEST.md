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

**Selection criteria** (from preregistration §8.4.2):

- Missed in ≥3/10 baseline passes
- Top M ranked by miss frequency

| Neutral Name | Actual File | Category | Provenance |
|--------------|-------------|----------|------------|
| example_05.png | *TBD after Phase 1* | hard_positive | Training tile FN analysis |
| example_06.png | *TBD after Phase 1* | hard_positive | Training tile FN analysis |
| example_07.png | *TBD after Phase 1* | hard_positive | Training tile FN analysis |
| example_08.png | *TBD after Phase 1* | hard_positive | Training tile FN analysis |

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

**Selection criteria** (from preregistration §8.4.2):

- Detected as mound in ≥3/5 baseline passes
- Top M ranked by false detection frequency

| Neutral Name | Actual File | Category | Provenance |
|--------------|-------------|----------|------------|
| example_11.png | *TBD after Phase 1* | hard_negative | Training tile FP analysis |
| example_12.png | *TBD after Phase 1* | hard_negative | Training tile FP analysis |
| example_13.png | *TBD after Phase 1* | hard_negative | Training tile FP analysis |
| example_14.png | *TBD after Phase 1* | hard_negative | Training tile FP analysis |

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
| 05-08 | Pending | Awaiting Phase 1 FN analysis |
| 09-10 | Created | Canonical negatives from legend |
| 11-14 | Pending | Awaiting Phase 1 FP analysis |
| 15-17 | Created | Null tiles selected |

**Last updated**: 2026-01-18

---

## Provenance Documentation

When hard examples are populated after Phase 1, document for each:

1. **Source tile**: Which training tile the crop came from
2. **Coordinates**: Pixel or geographic location within tile
3. **Selection metric**: Miss/detection frequency across passes
4. **Visual characteristics**: Why this example is "hard" (occlusion, degradation, etc.)

This provenance will be recorded in `docs/methodology/preregistration/decisions-log.md`.
