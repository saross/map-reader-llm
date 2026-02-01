# Protocol Errata

**Purpose**: Record of corrections, clarifications, and deviations from the preregistered protocol identified during execution. This document is maintained for transparency and reproducibility.

**Associated preregistration**: `preregistration.md` v4.7 (2026-01-31)

**See also**: `osf/execution-checklist.md` for execution tracking

---

## Classification

- **Correction**: Fix to implementation that brings it into alignment with the preregistered protocol (no protocol change)
- **Clarification**: Interpretation of an ambiguous point in the preregistration
- **Deviation**: Substantive change from the preregistered protocol (requires justification)

---

## Entries

### E1: Stale version/date in OSF companion README

| Field | Value |
|-------|-------|
| Date | 2026-01-31 |
| Type | Correction |
| Commit | `a9ed78b` |
| Impact | None (cosmetic) |

**Description**: The `osf/README.md` file contained a stale date (`2026-01-14`) that did not match the current preregistration version (v4.7, 2026-01-31). Updated to `2026-01-31` along with version alignment across all three OSF companion documents (`f037a9d`).

**Protocol impact**: None. These are companion metadata files, not the preregistration document itself.

---

### E2: Missing execution fields in Phase 1 config

| Field | Value |
|-------|-------|
| Date | 2026-02-01 |
| Type | Correction |
| File | `prompts/configs/library_pure-positive-canon.json` |
| Impact | Would have prevented execution or produced non-preregistered results |

**Description**: The library config file used by Phase 1 (`run_phase1.py`) was missing five execution fields required by the batch detection script (`4_detect_mounds_batch.py`):

| Field | Missing default | Preregistered value |
|-------|----------------|---------------------|
| `model` | `None` (crash) | `gemini-3-flash` |
| `temperature` | `0.1` (wrong) | `1.0` |
| `instruction_file` | `v3.0_system_instruction.md` (doesn't exist) | `detect_image-only.md` |
| `thinking_level` | omitted | `minimal` |
| `max_output_tokens` | `8192` | `8192` |

**Root cause**: The library config files (`library_*.json`) were designed as examples-only compositions for use with `run_study.py`, which supplies execution parameters from its own `defaults` section. However, `run_phase1.py` passes the config directly to the batch script, requiring it to be self-contained.

**Fix**: Added the five fields to `library_pure-positive-canon.json`, matching the values specified in the preregistration (Section 8.9) and the pattern established in other detection configs (e.g., `detect_image-only.json`).

**Protocol impact**: None. The preregistered parameters are unchanged; this corrects the implementation to match them. Without the fix, either the script would crash (`model=None`, missing instruction file) or silently use wrong parameters (`temperature=0.1` instead of `1.0`).

---

### E3: SDK migration for Gemini ThinkingConfig support

| Field | Value |
|-------|-------|
| Date | 2026-02-01 |
| Type | Correction |
| File | `scripts/4_detect_mounds_batch.py` |
| Impact | Would have prevented all detections (100% failure rate) |

**Description**: The batch detection script used the deprecated `google-generativeai` SDK (v0.8.6) which does not support `ThinkingConfig`. All API calls failed with `Unknown field for GenerationConfig: thinkingLevel`. Migrated to the `google-genai` SDK (v1.56.0) which supports `types.ThinkingConfig` natively.

Additionally, the preregistered model name `gemini-3-flash` does not exist as an API endpoint — the current API name is `gemini-3-flash-preview`. Added model name resolution logic to map the preregistered name to the API-available variant.

**Protocol impact**: None. The model is the same (Gemini 3 Flash); the `-preview` suffix is Google's API naming convention for models not yet promoted to stable. All preregistered parameters (temperature, thinking level, instruction file) are unchanged.

---

### E4: Tile bounds generation Y-axis inversion

| Field | Value |
|-------|-------|
| Date | 2026-02-01 |
| Type | Correction |
| Files | `scripts/generate_tile_bounds.py`, `inputs/vectors/bounds/calibration_bounds.geojson` |
| Impact | Evaluation reported near-zero F1 due to misscoped references |

**Description**: The tile metadata format is `[minX, minY, pixel_size_x, pixel_size_y]` but the bounds generation script treated `metadata[1]` as `maxY`, computing `min_y = maxY - height`. This shifted all tile bounds one tile height south (~2565m), causing the F1 evaluation to scope ground truth references to incorrect spatial areas.

Additionally, the property names in the generated GeoJSON used `tile` and `map` instead of `tile_name` and `map_name` as expected by the evaluation pipeline.

**Fix**: Corrected the metadata interpretation (`metadata[1]` is `minY`), fixed property names, and regenerated `calibration_bounds.geojson` from the current calibration manifest.

**Protocol impact**: None. The preregistered evaluation methodology (20m spatial tolerance, Hungarian matching) is unchanged. This corrects the implementation infrastructure.

---

### E5: Evaluation pipeline reference path and column name bugs

| Field | Value |
|-------|-------|
| Date | 2026-02-01 |
| Type | Correction |
| Files | `scripts/lib_advanced_metrics.py`, `scripts/6_accuracy_report.py`, `scripts/analyse_study_effects.py` |
| Impact | Evaluation silently returned no references, reporting near-zero metrics |

**Description**: Three bugs in the evaluation pipeline:

1. Reference file loading looked in `inputs/vectors/` but files are in `inputs/vectors/references/`
2. Merged consensus GeoJSON uses `source_tiles` (list) but evaluation expected `source_tile` (string)
3. Same path issue in `analyse_study_effects.py`

**Protocol impact**: None. These are implementation bugs in evaluation infrastructure; the preregistered evaluation methodology is unchanged.

---

### E6: Pipeline contract validation (post-Phase 1 hardening)

| Field | Value |
|-------|-------|
| Date | 2026-02-01 |
| Type | Correction |
| Files | `scripts/lib_advanced_metrics.py`, `scripts/6_accuracy_report.py`, `scripts/generate_tile_bounds.py`, `tests/test_integration_pipeline_contracts.py` |
| Impact | Prevents recurrence of E4-E5 silent failures in Phase 2+ |

**Description**: Phase 1 execution exposed five cascading silent failures (E3-E5) where pipeline stages accepted bad input and produced valid-looking but incorrect output. Each bug was individually minor but chained together to produce misleading near-zero F1 scores. To prevent recurrence in Phase 2 (~15,000 API calls per sub-phase, ~$286 total), three categories of contract validation were added:

1. **Reference loading assertion** (`lib_advanced_metrics.py`, `6_accuracy_report.py`): `load_data()` now validates that the reference directory exists before attempting glob, logs directory contents on failure (elevated from `warning` to `error` level), and the accuracy report script fails loudly with a clear message when references are `None` or empty. Previously, a wrong reference path silently returned `None`, and evaluation reported near-zero metrics without error.

2. **Bounds metadata validation** (`generate_tile_bounds.py`): Added `validate_bounds()` function that spot-checks generated tile polygons against source metadata after generation. Verifies that polygon minY equals `metadata[1]` (catching Y-axis inversions like E4), and that polygon dimensions equal `TILE_SIZE * pixel_size`. Script exits with error if validation fails.

3. **Pipeline contract integration tests** (`tests/test_integration_pipeline_contracts.py`): Seven new pytest tests exercising stage-boundary contracts:
   - `source_tiles` list → `source_tile` string normalisation (E5b regression)
   - Reference loading fails loudly on missing/empty directory (E5a regression)
   - Bounds metadata correctly interprets `metadata[1]` as minY (E4 regression)
   - End-to-end merge → evaluate produces non-zero F1 on synthetic data
   - Vote counts and threshold filtering work correctly through the full path

**Protocol impact**: None. These are infrastructure hardening measures that do not change the preregistered methodology. The evaluation algorithms, spatial tolerance (20m), Hungarian matching, and statistical analysis are unchanged. The additions ensure that the same pipeline code will fail loudly rather than silently if similar interface bugs are introduced.

---

*End of errata. New entries should be appended above this line.*
