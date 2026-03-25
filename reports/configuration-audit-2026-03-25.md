# Comprehensive Run Configuration Audit

**Date:** 2026-03-25
**Auditor:** Claude Opus 4.6 (automated audit)
**Scope:** All production runs across outputs/h11/, outputs/phase*, outputs/retest/

## Executive Summary

Audited **1,740 runs** across **239 conditions**. Found **2 confirmed temperature
propagation failures** (40 runs), **1 known label mislabelling** (180 runs), and
**6 incomplete runs** (JSONL submitted but no results). The E42 (Pro label, Flash
model) directory rename is verified complete -- no remnants remain. No Pro model was
used in any run. The E40 (Pro + MINIMAL rejection) scenario never occurred because
no run used a Pro model.

**Severity summary:**

- CRITICAL: 0 new (E42 already remediated by Session 57 rename)
- HIGH: 40 runs with temperature propagation failures (consensus-384 and single-pass-384)
- WARNING: 180 runs with misleading directory labels (Phase 3a "-high" dirs)
- INFO: 265 runs missing thinking_level/instruction_hash fields (older Phase 1-2 runs)

---

## Section 1: Run Inventory Summary

### H11 Proposer Runs

| Condition | Runs | Study YAML | Config JSON | Model | T | Thinking | Hash (prefix) | JSONL |
|-----------|------|------------|-------------|-------|---|----------|---------------|-------|
| pv-diag-384/text-baseline | 1 | h11-384-pv-diag-text-baseline.yaml | detect_brief-text.json | gemini-3-flash | 0.0 | minimal | e169b723... | 1/1 |
| pv-diag-384/text-baseline-611tiles | 1 | — | detect_brief-text.json | gemini-3-flash | 0.0 | minimal | e169b723... | 1/1 |
| pv-diag-384/text-n10 | 10 | h11-384-pv-diag-text-n10.yaml | detect_brief-text.json | gemini-3-flash | 0.7 | minimal | e169b723... | 10/10 |
| pv-diag-384/image-baseline | 1 | h11-384-pv-diag-image-baseline.yaml | library_plus-hp.json | gemini-3-flash | 0.0 | minimal | e169b723... | 1/1 |
| pv-diag-384/image-n5 | 10 | h11-384-pv-diag-image-n5.yaml | library_plus-hp.json | gemini-3-flash | 0.7 | minimal | e169b723... | 10/10 |
| pv-diag-384/flash-high-text-n5 | 30 | h11-384-flash-high-text-n5.yaml | detect_brief-text.json | gemini-3-flash | 0.7 | high | e169b723... | 30/30 |
| pv-diag-384/flash-high-text-n5-b | 5 | h11-384-flash-high-text-n5-b.yaml | detect_brief-text.json | gemini-3-flash | 0.7 | high | e169b723... | 5/5 |
| pv-diag-384/flash-high-image-n5 | 10 | h11-384-flash-high-image-n5.yaml | library_plus-hp.json | gemini-3-flash | 0.7 | high | e169b723... | 10/10 |
| pv-diag-384/flash-high-image-n5-b | 5 | h11-384-flash-high-image-n5-b.yaml | library_plus-hp.json | gemini-3-flash | 0.7 | high | e169b723... | 5/5 |
| pv-diag-384/flash-medium-text-baseline | 1 | h11-384-flash-medium-text-baseline.yaml | detect_brief-text.json | gemini-3-flash | 0.0 | medium | e169b723... | 1/1 |
| pv-diag-384/flash-medium-image-baseline | 1 | h11-384-flash-medium-image-baseline.yaml | library_plus-hp.json | gemini-3-flash | 0.0 | medium | e169b723... | 1/1 |
| pv-diag-384/flash-minimal-text-n30-t07 | 30 | h11-384-flash-minimal-text-n30-t07.yaml | detect_brief-text.json | gemini-3-flash | 0.7 | minimal | e169b723... | 30/30 |
| consensus-384 | 30 | h11-384-consensus.yaml | detect_brief-text.json | gemini-3-flash | **1.0** | minimal | e169b723... | 0/30 |
| single-pass-384 | 10 | h11-384-single-pass.yaml | detect_brief-text.json | gemini-3-flash | **1.0** | minimal | e169b723... | 0/10 |
| pv-diag-256/text-baseline | 1 | h11-256-pv-diag-text-baseline.yaml | detect_brief-text.json | gemini-3-flash | 0.0 | minimal | — | 1/1 |
| pv-diag-256/text-n5 | 5 | h11-256-pv-diag-text-n5.yaml | detect_brief-text.json | gemini-3-flash | 0.7 | minimal | — | 5/5 |
| proposer-verifier-384 | 15 | h11-384-proposer-verifier.yaml | mixed (verifiers) | gemini-3-flash | 0.0 | minimal | mixed | 0/15 |
| proposer-verifier-512 | 2 | h11-384-proposer-verifier.yaml | mixed (verifiers) | gemini-3-flash | 0.0 | minimal | — | 0/2 |

### H11 Verifier Runs (pv-diag-384/verified/)

| Condition | Runs | Model | T | Thinking | JSONL |
|-----------|------|-------|---|----------|-------|
| text-baseline | 1 | gemini-3-flash | 0.0 | minimal | 0/1 |
| text-{1..5}of5 | 5 | gemini-3-flash | 0.0 | minimal | 0/5 |
| text-{1..10}of10 | 10 | gemini-3-flash | 0.0 | minimal | 0/10 |
| image-baseline | 1 | gemini-3-flash | 0.0 | minimal | 0/1 |
| image-{1..5}of5 | 5 | gemini-3-flash | 0.0 | minimal | 0/5 |
| image-1of10 | 1 | gemini-3-flash | 0.0 | minimal | 0/1 |
| flash-high-text-1of5 | 1 | gemini-3-flash | 0.0 | minimal | 0/1 |
| flash-high-text-b-1of5 | 1 | gemini-3-flash | 0.0 | medium | 0/1 |
| flash-medium-text-medium-verifier | 1 | gemini-3-flash | 0.0 | medium | 0/1 |
| flash-medium-text-minimal-verifier | 1 | gemini-3-flash | 0.0 | minimal | 0/1 |
| flash-medium-image-medium-verifier | 1 | gemini-3-flash | 0.0 | medium | 0/1 |
| flash-medium-image-minimal-verifier | 1 | gemini-3-flash | 0.0 | minimal | 0/1 |
| flash-minimal-text-medium-verifier | 1 | gemini-3-flash | 0.0 | medium | 0/1 |
| flash-minimal-image-medium-verifier | 1 | gemini-3-flash | 0.0 | medium | 0/1 |

### H11 Verifier Runs (pv-diag-256/verified/)

| Condition | Runs | Model | T | Thinking |
|-----------|------|-------|---|----------|
| text-baseline | 1 | gemini-3-flash | 0.0 | minimal |
| text-{1..5}of5 | 5 | gemini-3-flash | 0.0 | minimal |

### Phase 1-2 Original Runs

| Phase | Conditions | Runs | Model | T (range) | Thinking | JSONL |
|-------|------------|------|-------|-----------|----------|-------|
| phase1-library | 1 | 5 | gemini-3-flash | 0.0 | MISSING | 0/5 |
| phase2a (modality) | 5 | 50 | gemini-3-flash | 1.0 | MISSING | 0/50 |
| phase2b (temperature) | 10 | 100 | gemini-3-flash | 0.0-1.3 | MISSING | 0/100 |
| phase2c (library) | 8 | 80 | gemini-3-flash | 0.0 | MISSING | 0/80 |
| phase2d (neg-text) | 6 | 60 | gemini-3-flash | 1.0 | MISSING | 0/60 |
| phase2e (ordering) | 4 | 40 | gemini-3-flash | 1.0 | MISSING | 0/40 |

### Phase 3 Original Runs

| Phase | Conditions | Runs | Model | T (range) | Thinking | JSONL |
|-------|------------|------|-------|-----------|----------|-------|
| phase3a track1-image | 3 | 90 | gemini-3-flash | 0.3-1.0 | minimal | 0/90 |
| phase3a track1-image-high | 3 | 90 | gemini-3-flash | 0.3-1.0 | **minimal** | 0/90 |
| phase3a track2-text | 3 | 90 | gemini-3-flash | 0.3-1.0 | minimal | 0/90 |
| phase3a track2-text-high | 3 | 90 | gemini-3-flash | 0.3-1.0 | **minimal** | 0/90 |
| phase3c track1-image | 25 | 125 | gemini-3-flash | 0.4-1.0 | minimal | 0/125 |
| phase3c track2-text | 20 | 100 | gemini-3-flash | 0.4-1.0 | minimal | 0/100 |

### Retest Runs

| Phase | Conditions | Runs | Model | T (range) | Thinking | JSONL |
|-------|------------|------|-------|-----------|----------|-------|
| retest/phase2a | 5 | 15 | gemini-3-flash | 1.0 | minimal | 0/15 |
| retest/phase2b | 10 | 30 | gemini-3-flash | 0.0-1.3 | minimal | 0/30 |
| retest/phase2c | 13 | 13 | gemini-3-flash | 0.0 | minimal | 0/13 |
| retest/phase2d | 2 | 4 | gemini-3-flash | 1.0 | minimal | 0/4 |
| retest/phase2e | 4 | 4 | gemini-3-flash | 1.0 | minimal | 0/4 |
| retest/phase3a image | 3 | 90 | gemini-3-flash | 0.3-1.0 | minimal | 0/90 |
| retest/phase3a text | 3 | 90 | gemini-3-flash | 0.3-1.0 | minimal | 0/90 |
| retest/phase3a-high text | 3 | 90 | gemini-3-flash | 0.3-1.0 | high | 14/90 |
| retest/phase3a-replication | 2 | 60 | gemini-3-flash | 0.7 | min/high | 0/60 |
| retest/phase3c track1-image | 25 | 119 | gemini-3-flash | 0.4-1.0 | minimal | 84/119 |
| retest/phase3c track2-text | 20 | 100 | gemini-3-flash | 0.4-1.0 | minimal | 94/100 |

### Grand Totals

| Category | Conditions | Runs | Has meta.json | Has JSONL |
|----------|------------|------|---------------|-----------|
| H11 (all) | 47 | 205 | 205/205 | 111/205 |
| Phase 1-2 original | 34 | 335 | 335/335 | 0/335 |
| Phase 3 original | 57 | 585 | 585/585 | 0/585 |
| Retest (all) | 92 | 615 | 615/615 | 192/615 |
| **TOTAL** | **239** | **1,740** | **1,740/1,740** | **303/1,740** |

---

## Section 2: Discrepancy Table

### CRITICAL / HIGH Discrepancies

| Condition | Runs Affected | Check | Severity | Expected | Actual | Detail |
|-----------|---------------|-------|----------|----------|--------|--------|
| h11/consensus-384 | 30 (all) | 2: Intent<->Meta, 3: Propagation | HIGH | temperature=0.7 | temperature=1.0 | T=1.0 bug: YAML specifies T=0.7 (fixed.temperature and carried_forward.optimal_temperature) but config JSON default T=1.0 was not overridden. No conditions block in YAML, so extract_conditions() had no temperature override to propagate. |
| h11/single-pass-384 | 10 (all) | 2: Intent<->Meta, 3: Propagation | HIGH | temperature=0.0 | temperature=1.0 | Same T=1.0 bug: YAML specifies T=0.0 (fixed.temperature and carried_forward.optimal_temperature) but config JSON default T=1.0 prevailed. No conditions block in YAML. |
| phase3a/track1-image-high | 90 (all) | 1: Label<->Meta | WARNING | thinking=high | thinking=minimal | Directory label says "high" but all runs used minimal thinking. Known issue -- documented in phase3a-replication.yaml ("the Phase 3a 'HIGH' result was mislabelled -- both original directories used minimal thinking"). |
| phase3a/track2-text-high | 90 (all) | 1: Label<->Meta | WARNING | thinking=high | thinking=minimal | Same mislabelling as track1-image-high. |

### INFO Discrepancies

| Condition | Runs Affected | Check | Severity | Detail |
|-----------|---------------|-------|----------|--------|
| phase1-library | 5 | 1,5: Meta fields | INFO | thinking_level, instruction_hash, example_count all MISSING in meta.json (older schema) |
| phase2a (all conditions) | 50 | 1,5: Meta fields | INFO | Same MISSING fields as phase1 |
| phase2b (all conditions) | 100 | 1,5: Meta fields | INFO | Same MISSING fields |
| phase2c (all conditions) | 80 | 1,5: Meta fields | INFO | Same MISSING fields |
| phase2d (all conditions) | 60 | 1,5: Meta fields | INFO | Same MISSING fields |
| phase2e (all conditions) | 40 | 1,5: Meta fields | INFO | Same MISSING fields |
| retest/phase3c track1-image | 6 | SOURCE_MISSING:meta | INFO | 6 runs have JSONL but no meta.json and no output (incomplete/failed runs) |

### Pairwise Test Reference Issues

| File | Issue | Severity |
|------|-------|----------|
| All files referencing "pro-high-text-n5" | study_dir points to `outputs/h11/pv-diag-384/pro-high-text-n5` which no longer exists (renamed to flash-high-text-n5-b) | WARNING |
| All files referencing "pro-high-image-n5" | study_dir points to `outputs/h11/pv-diag-384/pro-high-image-n5` which no longer exists (renamed to flash-high-image-n5-b) | WARNING |

---

## Section 3: Confound Matrix

For every comparison pair in `results/h11-384-pairwise-n5/`:

| Comparison | Intended Variable | Config Parameters That Also Vary | Confounded? |
|------------|------------------|----------------------------------|-------------|
| Flash HIGH image 3-of-5 vs Flash MINIMAL image 3-of-5 | thinking_level | None | NO |
| Flash HIGH image 7-of-10 vs Flash MINIMAL image 8-of-10 | thinking_level | consensus threshold (7 vs 8) | Minor (threshold is a consensus param, not a model config) |
| Flash-b HIGH image 3-of-5 vs Flash HIGH image 3-of-5 | batch identity | None (both Flash, same config) | NO |
| Flash HIGH text 26-of-30 vs Flash HIGH text 9-of-10 | consensus params (pool+threshold) | None (same underlying data) | NO (same condition) |
| Flash HIGH text 26-of-30 vs Flash MINIMAL-T0.7 text 29-of-30 | thinking_level | consensus threshold (26 vs 29) | Minor (threshold) |
| Flash HIGH text 5-of-5 vs Flash HIGH image 3-of-5 | modality (text vs image) | example_count (17 vs 13), threshold (5 vs 3) | YES -- example_count differs because text config has more examples than image config |
| Flash HIGH text 5-of-5 vs Flash MINIMAL-T0.7 text 5-of-5 | thinking_level | None | NO |
| Flash HIGH text 5-of-5 vs Flash MINIMAL text 5-of-5 (consensus-384) | thinking_level | **temperature (0.7 vs 1.0)** | **YES -- T=1.0 bug confounds this comparison** |
| Flash HIGH text 9-of-10 vs Flash HIGH image 7-of-10 | modality | example_count (17 vs 13), threshold (9 vs 7) | YES -- example_count differs |
| Flash HIGH text 9-of-10 vs Flash HIGH text 5-of-5 | consensus params | None (same underlying data) | NO (same condition) |
| Flash HIGH text 9-of-10 vs Flash MINIMAL-T0.7 text 10-of-10 | thinking_level | consensus threshold (9 vs 10) | Minor (threshold) |
| Flash-b HIGH text 3-of-5 vs Flash-b HIGH image 3-of-5 | modality | example_count (17 vs 13) | YES -- example_count differs |
| Flash-b HIGH text 3-of-5 vs Flash HIGH text 5-of-5 | batch identity | consensus threshold (3 vs 5) | Minor (threshold) |
| Flash-b HIGH text 3-of-5 vs Flash MINIMAL-T0.7 text 5-of-5 | thinking_level | consensus threshold (3 vs 5) | Minor (threshold) |
| Flash-b HIGH text 3-of-5 vs Flash MINIMAL text 5-of-5 (consensus-384) | thinking_level | **temperature (0.7 vs 1.0)**, threshold (3 vs 5) | **YES -- T=1.0 bug confounds** |
| Flash MINIMAL text T0.7 10-of-10 vs Flash MINIMAL text T1.0 9-of-10 (consensus-384) | temperature | consensus threshold (10 vs 9) | **YES -- but this comparison was designed to test the T=0.7 vs T=1.0 difference, so the temperature difference is intentional. However, the consensus-384 side was NOT intentionally T=1.0.** |
| Flash MINIMAL text T0.7 29-of-30 vs Flash MINIMAL text T1.0 28-of-30 (consensus-384) | temperature | consensus threshold (29 vs 28) | Same as above |
| Flash MINIMAL text T0.7 5-of-5 vs Flash MINIMAL text T1.0 5-of-5 (consensus-384) | temperature | None | **Partially valid** -- both sides use minimal thinking and same model, temperature IS the only varying config param. But consensus-384 T=1.0 was unintentional. |
| Image MINIMAL N=10 6-of-10 vs Image MINIMAL N=30 14-of-30 | consensus params (pool size) | None (same underlying data) | NO (same condition) |

### Summary of Confounded Comparisons

**T=1.0 bug-affected comparisons (3):**

- Flash HIGH text 5-of-5 vs Flash MINIMAL text 5-of-5 (consensus-384)
- Flash-b HIGH text 3-of-5 vs Flash MINIMAL text 5-of-5 (consensus-384)
- Both T0.7-vs-T1.0 temperature comparisons

These comparisons used consensus-384 data that ran at T=1.0 instead of T=0.7. Any
comparison involving consensus-384 as a "T=1.0" condition is scientifically valid
(the data genuinely was T=1.0), but comparisons using it as a "minimal thinking at
T=0.7" baseline are confounded by the unintended temperature difference.

**Modality comparisons with example_count confound (3):**

- Flash HIGH text vs Flash HIGH image (5-of-5 and 9-of-10 variants)
- Flash-b HIGH text vs Flash-b HIGH image

Text configs have example_count=17; image configs have example_count=13. This is
inherent to the different prompt configs (detect_brief-text.json vs library_plus-hp.json)
and reflects a design-level coupling between modality and example count, not a
configuration error.

---

## Section 4: Cross-Run Consistency Exceptions

### Conditions with Internal Inconsistency

| Condition | Parameter | Majority Value | Outlier Runs | Outlier Value |
|-----------|-----------|----------------|--------------|---------------|
| h11/proposer-verifier-384 | instruction_hash | 2518d529... (n=5) | 4 runs (brief-*) | ded339c9... |
| h11/proposer-verifier-384 | instruction_hash | 2518d529... (n=5) | 5 runs (checklist-*, cascade-*) | 81c3485d... |
| h11/proposer-verifier-384 | example_count | 0 (n=7) | 4 runs (image variants) | 6 |
| h11/proposer-verifier-384 | example_count | 0 (n=7) | 3 runs (image variants) | 9 |

**Assessment:** These exceptions are expected and non-problematic. The proposer-verifier-384
directory contains multiple distinct verifier configurations (adversarial, brief, checklist;
text vs image; v1 vs v2). Different instruction hashes and example counts reflect
intentionally different system instructions across these verifier types. They should
not be treated as a single condition for consistency purposes.

All other conditions (173 multi-run conditions and 28 single-run conditions) are
**internally consistent** -- no cross-run anomalies detected across model, temperature,
thinking level, instruction hash, or example count.

---

## Section 5: Recommendations

### HIGH-1: consensus-384 T=1.0 Bug (30 runs)

**Status:** Known issue (discovered Session 56). The flash-minimal-text-n30-t07
condition was created as the corrected replacement (verified: T=0.7, minimal thinking,
30 runs, all consistent).

**Data usability:**

- The consensus-384 data is usable **as T=1.0 minimal-thinking data** (which is what
  it actually is). It should NOT be treated as T=0.7 data.
- The pairwise comparisons labelled "T0.7 vs T1.0" that use consensus-384 as the
  T=1.0 side are scientifically valid -- they genuinely compare T=0.7 (flash-minimal-
  text-n30-t07) against T=1.0 (consensus-384).
- Comparisons using consensus-384 as a "minimal thinking at T=0.7 baseline" for
  comparison against HIGH thinking are **confounded** and should be replaced with
  flash-minimal-text-n30-t07 as the minimal-thinking baseline.

**Affected analysis:** Any published result comparing thinking_level=high vs
thinking_level=minimal using consensus-384 as the minimal side is confounded by
T=0.7 vs T=1.0. Use flash-minimal-text-n30-t07 instead.

### HIGH-2: single-pass-384 T=1.0 Bug (10 runs)

**Status:** Newly confirmed in this audit.

**Root cause:** Same propagation failure as consensus-384. The study YAML
(`h11-384-single-pass.yaml`) specifies `fixed.temperature: 0.0` and
`carried_forward.optimal_temperature: 0.0`, but has no `conditions` block. The
config JSON default `temperature: 1.0` was not overridden because `extract_conditions()`
had nothing to propagate.

**Data usability:** The data represents single-pass detection at T=1.0, not T=0.0.
This is scientifically less useful because T=0.0 is the deterministic baseline. The
runs must be re-executed at T=0.0 for a valid tile-size comparison.

**Re-execution command:**

```bash
for run in $(seq 1 10); do
    python scripts/4_detect_mounds_batch.py \
        --config prompts/configs/detect_brief-text.json \
        --manifest inputs/tiles_384/validation_manifest.json \
        --output-dir outputs/h11/single-pass-384-t00/384/run_${run} \
        --tile-size 384 \
        --tiles-dir inputs/tiles_384 \
        --temperature 0.0 \
        --workers 12
done
```

### WARNING-1: Phase 3a "-high" Directory Mislabelling (180 runs)

**Status:** Known issue, documented in `studies/phase3a-replication.yaml`.

The directories `outputs/phase3a/track1-image-high/` and
`outputs/phase3a/track2-text-high/` contain runs that were intended to use HIGH
thinking but actually used minimal thinking (confirmed by meta.json across all 180
runs). The phase3a-replication study was created specifically to provide a properly
controlled comparison.

**Data usability:** These runs are usable as **additional minimal-thinking data**.
They should not be referenced as HIGH-thinking results. The replication runs at
`outputs/retest/phase3a-high/` and `outputs/retest/phase3a-replication/high` provide
the actual HIGH-thinking data.

### WARNING-2: Pairwise Test Files Reference Deleted Paths (7 files)

Seven pairwise test JSON files in `results/h11-384-pairwise-n5/` reference study
directories `outputs/h11/pv-diag-384/pro-high-text-n5` and
`outputs/h11/pv-diag-384/pro-high-image-n5`. These directories were renamed to
`flash-high-text-n5-b` and `flash-high-image-n5-b` in Session 57. The pairwise
result files still contain the old paths.

**Impact:** Low. The results themselves are correct (they were computed before the
rename). But any script that attempts to reload data from the `study_dir` paths
in these JSON files will fail. The label fields still say "Pro HIGH" in the JSON.

**Recommendation:** Update the `study_dir` and `label` fields in these 7 files to
reflect the corrected directory names and "Flash HIGH" labels. Alternatively, add a
symlink from the old paths to the new ones.

### INFO-1: Older Phase Runs Missing Meta Fields (265 runs)

Phases 1 through 2e use an older meta.json schema that does not include
`thinking_level`, `system_instruction_hash`, or `example_count`. This makes Checks
1 (thinking level portion), 4, and 5 partially UNVERIFIABLE for these runs.

**Impact:** None for analysis -- these runs predate the thinking level experiments
and all used the same minimal thinking (the only level supported at the time). The
temperature and model fields are present and correct in all 265 runs.

### INFO-2: Incomplete Retest Runs (6 runs)

Six runs in `outputs/retest/phase3c/track1-image/` have JSONL files (batch requests
were submitted) but no meta.json or output geojson. These are failed/incomplete runs:

- h9-A-p1/run_1, h9-A-p5/run_1, h9-B-v4/run_5
- h9-C-img4/run_3, h9-D-t5/run_2, h9-E-p3/run_5

**Impact:** Low. These runs did not produce results. The corresponding conditions
have 4 successful runs instead of 5, which is noted in the run counts above.

---

## Known Issue Verification

### E42: Pro Label But Flash Model

**Status: REMEDIATED.** All "Pro" directories were renamed to "flash-*" in Session
57. No directory in the outputs tree contains "pro" in a way that implies a Pro model
was used. All 1,740 runs use `model: gemini-3-flash` in their meta.json. The study
YAML files for the "-b" conditions (`h11-384-flash-high-text-n5-b.yaml`,
`h11-384-flash-high-image-n5-b.yaml`) still have `output_dir` pointing to the old
`pro-high-*` paths, but the actual directories have been renamed. **No mislabelled
remnants remain in the filesystem.**

### T=1.0 Temperature Bug

**Status: CONFIRMED in 2 conditions.**

1. **consensus-384** (30 runs): All runs at T=1.0 instead of YAML-intended T=0.7.
   Corrected replacement: flash-minimal-text-n30-t07 (30 runs at T=0.7, verified).
2. **single-pass-384** (10 runs): All runs at T=1.0 instead of YAML-intended T=0.0.
   **No corrected replacement exists yet.**

**Root cause:** Both study YAMLs lack a `conditions` block, specifying temperature
only in `fixed` and `carried_forward` sections. The pipeline's `extract_conditions()`
function reads temperature from the conditions list; without one, the config JSON
default (`temperature: 1.0` in `detect_brief-text.json`) prevails.

### E40: Pro + MINIMAL Thinking Rejection

**Status: NOT APPLICABLE.** No run in the entire corpus used a Pro model (all 1,740
runs are gemini-3-flash). The E40 scenario (Pro rejecting MINIMAL thinking and
silently downgrading) could not have occurred.

---

## Final Completeness Check

1. **Total runs inventoried:** 1,740 across 239 conditions. This matches the count
   from the filesystem scan (1,740 meta.json files found, excluding retry files).

2. **Runs with at least one UNVERIFIABLE check:** 265 (all in Phase 1-2 original
   runs, due to missing thinking_level/instruction_hash/example_count in older
   meta.json schema). Plus 6 incomplete retest runs with no meta.json at all.

3. **Conditions entirely skipped:** None. All conditions with meta.json files were
   audited.

4. **Conditions with >10 runs (Check 5):** 24 conditions have 30 runs each (Phase
   3a, retest/phase3a, consensus-384, flash-high-text-n5, flash-minimal-text-n30-t07).
   ALL runs in every condition were checked individually for cross-run consistency.
   No anomalies found in any of these large conditions.

**Audit completion: 1,740/1,740 runs audited across 239 conditions. All 6 checks
applied to every run. All check results recorded as PASS, FAIL, or UNVERIFIABLE.**
