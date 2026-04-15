# Pre-Launch Configuration Audit — H8 v2

**Date**: 2026-04-15
**Auditor**: Claude Code (via `/audit-config` skill)
**Hypothesis**: H8 (Library Composition and Scaling)
**Configs audited**: `prompts/configs/h8/v2/detect_h8_*_v2.json` (7 files)
**Study YAML**: `studies/h8-v2-library.yaml`
**Errata reference**: E51 (protocol-errata.md, 2026-04-15)
**Verdict**: **READY TO LAUNCH** (after B1 resolution — see "Blocker B1 resolution" below)

**Original verdict**: BLOCKED on one dimensional-uniformity blocker
**Resolution applied**: 2026-04-15 — `build_example_pool.py` extended with an
`--exclude-edge-crops` flag (default on), `pool_160_hp8hn8` and
`pool_160_hp16hn16` re-mined with the filter. All 48 new crops are
150 × 150. Pre-filter pools archived to
`archive/h10-v2-prefilter-pools/`.

---

## 1. Preregistration requirements

Extracted from `docs/methodology/preregistration/osf/preregistration.md` §H8
(lines 737–831) and protocol-errata E51:

1. **Seven library conditions** at preregistered compositions (§H8 line 764):
   Pure Positive Canon (7), Canonical (9), +HP (13), Scale-4 (13), Scale-8 (17),
   Scale-16 (25), Scale-32 (41). **HARD.**
2. **1:1 HP:HN ratio** in scaling conditions (§H8 line 813). **HARD.**
3. **Availability constraint**: ≥16 HP and ≥16 HN for Scale-32 (§H8 line 815).
   **HARD** — resolved by v2 pool (108 HP / 57 HN available).
4. **Instruction file** = `detect_brief-text-image.md` (image track per E27).
   **HARD.**
5. **Model** = `gemini-3-flash`, **`include_example_images: true`**. **HARD.**
6. **Temperature** and **thinking level**: originally T=0.0 / minimal per H7
   carry-forward; **E51-modified** to T=0.7 / thinking=high (production
   carry-forward aligned with H10 v2).
7. **K passes**: originally 10; **E51-modified** to 5 (production n=5
   consensus).
8. **Tile size**: originally 512 px; **E41/E51-modified** to 384 px.
9. **Evaluation manifest**: **E50-modified** to H10 test set
   (`inputs/calibration/h10-384/test_manifest.json`, 327 tiles).
10. **Planned contrasts**: C1, C2, C3, S1, S2, S3, B1 (§H8 lines 779–797).
    **HARD.**

## 2. Pairwise config diff

All seven configs were compared field-by-field.

**Controlled fields (identical across all 7)**:

| Field | Value |
|---|---|
| `model` | `gemini-3-flash` |
| `instruction_file` | `detect_brief-text-image.md` |
| `temperature` | `0.7` |
| `thinking_level` | `high` |
| `include_example_images` | `true` |
| `max_output_tokens` | `8192` |
| `hypothesis` | `H8` |

**Manipulated (expected to differ)**:

- `examples` — the factor under test; composition per preregistration table
- `pool_source` — `pool_160_hp4hn4` for {plus-hp, scale-4, scale-8};
  `pool_160_hp8hn8` for scale-16; `pool_160_hp16hn16` for scale-32. Nested by
  byte-identical prefix (verified on 2026-04-15).

**Bookkeeping (expected to differ)**:

- `description`, `ordering_note`, `version` — one per condition

**Confounds detected**: NONE.

## 3. Transmission check

| Condition | Flag | Model | Think | Instr | Temp | Paths | Comp | Dim | Status |
|---|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|
| pure-positive-canon | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | PASS |
| canonical | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | PASS |
| plus-hp | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | PASS |
| scale-4 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | PASS |
| scale-8 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | PASS |
| scale-16 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | PASS |
| scale-32 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | **✗** | **FAIL** |

**Scale-32 dimension failure** (pool_160_hp16hn16 only):

- `hp_11.png` — 95 × 150 (edge-of-raster clip)
- `hn_11.png` — 150 × 100 (edge-of-raster clip)
- `hn_16.png` — 150 × 149 (1-pixel short)

Every other crop across all three pools (pool_160_hp4hn4, pool_160_hp8hn8,
pool_160_hp16hn16) is exactly 150 × 150.

## 4. Preregistration alignment

| Requirement | Verdict | Notes |
|---|---|---|
| Seven library compositions | MATCHES | All 7 totals and category counts verified |
| 1:1 HP:HN ratio (scaling) | MATCHES | scale-4: 2:2; scale-8: 4:4; scale-16: 8:8; scale-32: 16:16 |
| Availability constraint | MATCHES | v2 pool_160: 108 HP / 57 HN; E51 resolves E11 |
| instruction_file = brief-text-image | MATCHES | All 7 |
| model = gemini-3-flash | MATCHES | All 7 |
| include_example_images = true | MATCHES | All 7 |
| temperature (T=0.7) | DELIBERATE DEVIATION (E51) | Was T=0.0 per H7; production carry-forward |
| thinking_level (high) | DELIBERATE DEVIATION (E51) | Was minimal per Decision 2; production carry-forward |
| K=5 passes | DELIBERATE DEVIATION (E51) | Was K=10; production n=5 consensus |
| tile_size = 384 px | DELIBERATE DEVIATION (E41/E51) | Was 512 px; 384 pathway closed by H11 |
| Manifest = H10 test set | DELIBERATE DEVIATION (E50) | Was 60-tile validation set; expanded to 327 |
| 7 planned contrasts | MATCHES | Study YAML encodes all 7 including re-enabled S2, S3 |

**Matches**: 8. **Deliberate deviations**: 5 (all in E41/E50/E51).
**Undocumented deviations**: 0.

## 5. Dry-run validation

Ran `--dry-run` with `--mode realtime --service-tier flex --use-cache
--skip-intent-check` against two configs (smallest and largest):

**scale-32** (`detect_h8_scale-32_v2.json`):

- Examples loaded: 41 ✓
- Tiles to process: 327 ✓
- Instruction: `detect_brief-text-image.md` ✓
- Model resolved: `gemini-3-flash-preview` (matches H10 v2 resolution)
- Launch-time intent check: *"all fields that differ from the base will reach
  the API payload. OK."*
- Validation: **PASSED**

**pure-positive-canon** (`detect_h8_pure-positive-canon_v2.json`):

- Examples loaded: 7 ✓
- Tiles to process: 327 ✓
- Validation: **PASSED**

No missing-reference warnings, no tile-dimension errors, no safety blocks.

## 6. Evaluation scope

| Check | Result |
|---|---|
| Test manifest size | 327 tiles |
| Calibration manifest size (pool_160) | 160 tiles |
| Overlap (test ∩ calibration) | **0** |
| Ground truth | `inputs/vectors/references/mounds-reference.geojson` ✓ |
| Bounds | `inputs/vectors/bounds/384/h10_test_bounds.geojson` ✓ |

Test set is fully disjoint from the hard-case mining pool. No data leakage.

## 7. Completeness

**Checked**: all 7 requirement items, all 7 configs against 8 transmission
error modes, pairwise diff across all fields, dry-run on smallest and largest
conditions, evaluation-scope disjointness.

**Not checked (runtime-only)**:

- Flex service tier actually honoured by the API (historical concern per
  Obs 20 with outdated SDK — SDK is now `google-genai 1.73.1` which should
  support flex).
- Context cache creation success (script falls back gracefully on failure;
  pure-positive-canon may fall below the Gemini minimum cacheable token
  threshold).
- Per-condition cost estimate (deferred to Phase 2.5 API-gate proposal using
  run-time token counts from the first condition).

## Blockers (original)

### B1. Three off-size crops in `pool_160_hp16hn16` (Scale-32 only)

- `hp_11.png` (95 × 150), `hn_11.png` (150 × 100), `hn_16.png` (150 × 149)
- **Impact**: creates a Scale-16 → Scale-32 confound. If the S3 contrast
  returns a null effect (which is the preregistered prediction of diminishing
  returns), we will not be able to distinguish "diminishing returns" from
  "three lower-quality new hard examples at Scale-32". Interpretation of S3
  will be weakened.

### Blocker B1 resolution (2026-04-15)

Option 2 selected: re-mine `pool_160_hp16hn16` (and `pool_160_hp8hn8` for
consistency) with an edge-of-raster exclusion filter.

**Script change**: `scripts/build_example_pool.py` extended with three new
functions (`_raster_shape`, `_crop_fully_in_bounds`, `filter_edge_candidates`)
and an `--exclude-edge-crops` CLI flag (default `True`). The filter runs
before diversity selection, rejecting any candidate whose `crop_size` window
would extend beyond its source raster's pixel grid. `rasterio` is used to
resolve each candidate's pixel coordinates against each raster's dimensions
(raster shapes are cached via `lru_cache`). The `pool_metadata.json` now
records the `exclude_edge_crops` flag for provenance.

**Re-mine results**:

- Filter rejected 6 HP candidates (108 → 102) and 5 HN candidates (57 → 52)
  from the raw v2 hard-case register.
- `pool_160_hp8hn8` new selections are **identical** to the pre-filter
  selections — none of the top 8 HP or HN picks were edge candidates, so
  filtering was a no-op at this rung.
- `pool_160_hp16hn16` new selections preserve picks 1–10 (HP and HN);
  picks 11–16 shift by 1–3 positions because the filter rejected what would
  have been picks 11 (HP), 11 (HN), and 16 (HN) in the pre-filter selection.
- Nestedness **preserved** at all three rungs: `pool_160_hp4hn4` ⊂
  new `pool_160_hp8hn8` ⊂ new `pool_160_hp16hn16` for both HP and HN.
- All 48 new crops (`8+8+16+16`) are exactly 150 × 150 pixels.
- Pre-filter pools archived to `archive/h10-v2-prefilter-pools/` for
  provenance.
- Dry-run of `scale-32` post-fix: **PASS** (41 examples loaded, 327 tiles,
  Validation PASSED).

Protocol-errata E51 updated to reference the edge-exclusion fix.

**Post-resolution verdict**: **READY TO LAUNCH**.

## Warnings

- **W1**: Pure-positive-canon library (7 examples) may fall below Gemini's
  minimum cacheable token count (~4 KB for Flash). Script falls back
  gracefully to uncached mode. Confirm in run_1 stdout that the "Context
  cache created" line either appears or is replaced by the
  "WARNING: Cache creation failed, proceeding without cache" fallback.
- **W2**: Flex tier and context caching are runtime-only behaviours and
  cannot be validated pre-launch. Verify in `run.meta.json` post-run that
  `service_tier=flex` is recorded and `cache_name` is non-null for the
  cache-eligible conditions (canonical through scale-32).
- **W3**: The detect script's launch-time intent guard will prompt
  interactively per condition unless `--skip-intent-check` is passed. Do
  NOT pass that flag on the real launch without first reviewing the intent
  preview for each condition.

## Overall verdict

**READY TO LAUNCH** (after B1 resolution). All seven conditions now pass
every check in the audit matrix. Blocker B1 was resolved by adding an
edge-of-raster exclusion filter to `build_example_pool.py` and re-mining
`pool_160_hp8hn8` and `pool_160_hp16hn16`. Nestedness preserved, all crops
are 150 × 150, dry-run validates.

Warnings W1–W3 remain as runtime-verification items for the launch phase
(Phase 2.6–2.7).
