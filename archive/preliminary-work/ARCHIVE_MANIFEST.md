# Phase 2 Reset Archive

**Date**: 2025-12-23
**Reason**: Data provenance cleanup for scientific rigour

## Context

During preliminary development (Phase 1), iterative prompt engineering with Gemini
led to tile contamination — we cannot trace which tiles were used for few-shot
example mining, making train/test separation unreliable.

This archive preserves all materials from Phase 1 while we establish a clean
methodology with documented provenance.

## Archived Materials

### Reference Images (`references/`)

Images with unknown or contaminated provenance:

- `ref_variant_*.png` — positive variants (source tiles unknown)
- `ref_pos_*.png` — positive examples (mined from unknown tiles)
- `ref_negative_*.png` — noise examples (source unknown)
- `ref_neg_embankment_*.png` — negative examples (source unknown)
- `ref_neg_hard_*.png` — mined hard negatives
- `hard_positive_*.png` — mined hard positives (tile IDs in filename)
- `hard_negative_*.png` — mined hard negatives (tile IDs in filename)
- `neg_*.png` — background negatives (sparse/topo/urban — source unknown)

### Manifests (`manifests/`)

Old tile selections with undocumented selection criteria:

- `calibration_manifest.json` — early calibration tiles
- `target_tiles_manifest.json` — development/training tiles (20 tiles)
- `holdout_manifest.json` — holdout tiles (20 tiles)

### Scripts (`scripts/`)

- `create_stratified_holdout.py` — old tile selection script (no spatial separation)

## Retained Materials

The following remain in `inputs/references/` as canonical legend references:

**Positive examples (from map legend)**:
- `burial_mound.png`
- `settlement_mound.png`
- `triangulation_mound.png`
- `benchmark_mound.png`

**Negative examples (from map legend)**:
- `ref_neg_benchmark.png` — benchmark symbol without mound
- `ref_neg_triangulation.png` — triangulation point without mound

## Next Steps

1. Randomly select 20 new training tiles (5 per map) with documented seed
2. Randomly select 20 new holdout tiles with spatial separation from training
3. Rebuild few-shot library using only legend images + training tile crops
4. Document all example provenance explicitly
