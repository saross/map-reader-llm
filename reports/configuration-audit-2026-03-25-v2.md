# Comprehensive Run Configuration Audit (v2 -- Model Verification Correction)

**Date:** 2026-03-25 (v2)
**Auditor:** Claude Opus 4.6 (automated audit)
**Scope:** All production runs across outputs/h11/, outputs/phase*, outputs/retest/
**Supersedes:** `reports/configuration-audit-2026-03-25.md` (v1)

## Correction Summary

The v1 audit incorrectly concluded that "No Pro model was used in any run" and
that "All 'Pro' directories were renamed to 'flash-*' in Session 57." Both
claims were wrong due to a metadata bug:

**Root cause:** The v1 audit relied on `configuration.model` in meta.json,
which records the config JSON default (`gemini-3-flash`), not the resolved
model when a `--model` CLI override was used. The override mutated the
`config` dict at runtime, but the metadata tracker at the version used for Pro
runs (git `765cb232`, script v1.5.0) did not propagate the resolved model name
into the output metadata.

**Corrected verification method (priority order):**

1. **GeoJSON detection features** -- `properties.model` in the first feature
   of any detection GeoJSON file. This field is set from `model_name_cfg`
   AFTER `_resolve_model_name()` has resolved the actual API model.
2. **`cost_estimate.pricing_used.model`** in meta.json -- set by the pricing
   lookup which uses the resolved model name.
3. **Log files** -- grep for `"Model override:"` and `"resolved to"`.
4. **`configuration.model`** in meta.json -- **UNRELIABLE** when `--model`
   override was used. Records the config JSON default, not the resolved model.

**Key corrections:**

| v1 Claim | v2 Reality |
|----------|------------|
| "No Pro model was used in any run" | **12 runs used gemini-3.1-pro-preview** |
| "All 'Pro' dirs renamed to flash-*" | **Pro directories retain original names** |
| "E42 remediated by Session 57 rename" | **E42 was a misdiagnosis -- Pro runs genuinely used Pro** |
| "E40 not applicable (no Pro runs)" | **E40 not applicable (Pro runs used MEDIUM/HIGH, not MINIMAL)** |
| flash-high-text-n5-b (5 runs, Flash) | **Does not exist -- this is pro-high-text-n5 (5 runs, Pro)** |
| flash-high-image-n5-b (5 runs, Flash) | **Does not exist -- this is pro-high-image-n5 (5 runs, Pro)** |
| flash-medium-text-baseline (Flash) | **Does not exist -- this is pro-medium-text-baseline (Pro)** |
| flash-medium-image-baseline (Flash) | **Does not exist -- this is pro-medium-image-baseline (Pro)** |

---

## Section 1: Run Inventory Summary (Model-Corrected)

Only the H11 proposer runs and verifier runs are updated below. Phase 1-2,
Phase 3, and retest runs are unchanged from v1 -- all confirmed as
`gemini-3-flash-preview` via `cost_estimate.pricing_used.model` (1,532 Flash
runs, 0 Pro runs, 0 missing).

### H11 Proposer Runs

| Condition | Runs | Study YAML | Config JSON | Actual Model | T | Thinking | JSONL |
|-----------|------|------------|-------------|-------------|---|----------|-------|
| pv-diag-384/text-baseline | 1 | h11-384-pv-diag-text-baseline.yaml | detect_brief-text.json | **Flash** | 0.0 | minimal | 1/1 |
| pv-diag-384/text-baseline-611tiles | 1 | -- | detect_brief-text.json | **Flash** | 0.0 | minimal | 1/1 |
| pv-diag-384/text-n10 | 10 | h11-384-pv-diag-text-n10.yaml | detect_brief-text.json | **Flash** | 0.7 | minimal | 10/10 |
| pv-diag-384/image-baseline | 1 | h11-384-pv-diag-image-baseline.yaml | library_plus-hp.json | **Flash** | 0.0 | minimal | 1/1 |
| pv-diag-384/image-n5 | 10 | h11-384-pv-diag-image-n5.yaml | library_plus-hp.json | **Flash** | 0.7 | minimal | 10/10 |
| pv-diag-384/flash-high-text-n5 | 30 | h11-384-flash-high-text-n5.yaml | detect_brief-text.json | **Flash** | 0.7 | high | 30/30 |
| **pv-diag-384/pro-high-text-n5** | **5** | **h11-384-pro-high-text-n5.yaml** | detect_brief-text.json | **Pro** | 0.7 | high | 5/5 |
| pv-diag-384/flash-high-image-n5 | 10 | h11-384-flash-high-image-n5.yaml | library_plus-hp.json | **Flash** | 0.7 | high | 10/10 |
| **pv-diag-384/pro-high-image-n5** | **5** | **h11-384-pro-high-image-n5.yaml** | library_plus-hp.json | **Pro** | 0.7 | high | 5/5 |
| **pv-diag-384/pro-medium-text-baseline** | **1** | **h11-384-pro-medium-text-baseline.yaml** | detect_brief-text.json | **Pro** | 0.0 | medium | 1/1 |
| **pv-diag-384/pro-medium-image-baseline** | **1** | **h11-384-pro-medium-image-baseline.yaml** | library_plus-hp.json | **Pro** | 0.0 | medium | 1/1 |
| pv-diag-384/flash-minimal-text-n30-t07 | 30 | h11-384-flash-minimal-text-n30-t07.yaml | detect_brief-text.json | **Flash** | 0.7 | minimal | 30/30 |
| consensus-384 | 30 | h11-384-consensus.yaml | detect_brief-text.json | **Flash** | **1.0** | minimal | 0/30 |
| single-pass-384 | 10 | h11-384-single-pass.yaml | detect_brief-text.json | **Flash** | **1.0** | minimal | 0/10 |
| pv-diag-256/text-baseline | 1 | h11-256-pv-diag-text-baseline.yaml | detect_brief-text.json | **Flash** | 0.0 | minimal | 1/1 |
| pv-diag-256/text-n5 | 5 | h11-256-pv-diag-text-n5.yaml | detect_brief-text.json | **Flash** | 0.7 | minimal | 5/5 |
| proposer-verifier-384 | 15 | h11-384-proposer-verifier.yaml | mixed (verifiers) | **Flash** | 0.0 | minimal | 0/15 |
| proposer-verifier-512 | 2 | h11-384-proposer-verifier.yaml | mixed (verifiers) | **Flash** | 0.0 | minimal | 0/2 |

### Model Verification Evidence for Pro Runs

Every Pro run was verified via all three reliable sources. All agree.

| Condition | Run | GeoJSON model | cost_estimate model | Log evidence |
|-----------|-----|---------------|---------------------|--------------|
| pro-high-text-n5 | run_1 | gemini-3.1-pro-preview | gemini-3.1-pro-preview | "Model override: gemini-3.1-pro" + resolved |
| pro-high-text-n5 | run_2 | gemini-3.1-pro-preview | gemini-3.1-pro-preview | resolved to gemini-3.1-pro-preview |
| pro-high-text-n5 | run_3 | gemini-3.1-pro-preview | gemini-3.1-pro-preview | resolved to gemini-3.1-pro-preview |
| pro-high-text-n5 | run_4 | gemini-3.1-pro-preview | gemini-3.1-pro-preview | resolved to gemini-3.1-pro-preview |
| pro-high-text-n5 | run_5 | gemini-3.1-pro-preview | gemini-3.1-pro-preview | resolved to gemini-3.1-pro-preview |
| pro-high-image-n5 | run_1 | gemini-3.1-pro-preview | gemini-3.1-pro-preview | "Model override: gemini-3.1-pro" + resolved |
| pro-high-image-n5 | run_2 | gemini-3.1-pro-preview | gemini-3.1-pro-preview | resolved to gemini-3.1-pro-preview |
| pro-high-image-n5 | run_3 | gemini-3.1-pro-preview | gemini-3.1-pro-preview | resolved to gemini-3.1-pro-preview |
| pro-high-image-n5 | run_4 | gemini-3.1-pro-preview | gemini-3.1-pro-preview | resolved to gemini-3.1-pro-preview |
| pro-high-image-n5 | run_5 | gemini-3.1-pro-preview | gemini-3.1-pro-preview | resolved to gemini-3.1-pro-preview |
| pro-medium-text-baseline | run_1 | gemini-3.1-pro-preview | gemini-3.1-pro-preview | (log not checked individually) |
| pro-medium-image-baseline | run_1 | gemini-3.1-pro-preview | gemini-3.1-pro-preview | (log not checked individually) |

### H11 Verifier Runs (pv-diag-384/verified/)

All verifier runs used Flash, including those with "pro-" in the directory name.
The "pro-*" verifier directories contain Flash verifier runs that verified Pro
proposer outputs. This is the intended design (Flash verifier, Pro proposer).

| Condition | Model (cost_estimate) | T | Thinking |
|-----------|----------------------|---|----------|
| text-baseline | Flash | 0.0 | minimal |
| text-{1..5}of5 | Flash | 0.0 | minimal |
| text-{1..10}of10 | Flash | 0.0 | minimal |
| image-baseline | Flash | 0.0 | minimal |
| image-{1..5}of5 | Flash | 0.0 | minimal |
| image-1of10 | Flash | 0.0 | minimal |
| flash-high-text-1of5 | Flash | 0.0 | minimal |
| flash-minimal-text-medium-verifier | Flash | 0.0 | medium |
| flash-minimal-image-medium-verifier | Flash | 0.0 | medium |
| pro-high-text-1of5 | **Flash** (verifier) | 0.0 | medium |
| pro-text-medium-verifier | **Flash** (verifier) | 0.0 | medium |
| pro-text-minimal-verifier | **Flash** (verifier) | 0.0 | minimal |
| pro-image-medium-verifier | **Flash** (verifier) | 0.0 | medium |
| pro-image-minimal-verifier | **Flash** (verifier) | 0.0 | minimal |

### Grand Totals (Corrected)

| Category | Conditions | Runs | Actual Model | Has meta.json | Has JSONL |
|----------|------------|------|-------------|---------------|-----------|
| H11 Pro proposer | 4 | 12 | gemini-3.1-pro-preview | 12/12 | 12/12 |
| H11 Flash proposer | 43 | 193 | gemini-3-flash-preview | 193/193 | 99/193 |
| H11 verifier (all) | ~37 | ~37 | gemini-3-flash | ~24/37 | 0/37 |
| Phase 1-2 original | 34 | 335 | gemini-3-flash-preview | 335/335 | 0/335 |
| Phase 3 original | 57 | 585 | gemini-3-flash-preview | 585/585 | 0/585 |
| Retest (all) | 92 | 615 | gemini-3-flash-preview | 615/615 | 192/615 |
| **TOTAL** | **~239** | **~1,740** | **12 Pro + ~1,728 Flash** | **~1,740/1,740** | **~303/1,740** |

---

## Section 2: Discrepancy Table (Corrected)

### CRITICAL Discrepancies (NEW in v2)

| Condition | Runs Affected | Check | Severity | Expected (v1) | Actual (v2) | Detail |
|-----------|---------------|-------|----------|----------------|-------------|--------|
| pro-high-text-n5 | 5 (all) | meta.json model field | CRITICAL (metadata) | configuration.model = gemini-3.1-pro-preview | configuration.model = gemini-3-flash | **Bug in meta.json:** `configuration.model` records config JSON default, not resolved model. GeoJSON and cost_estimate both correctly show gemini-3.1-pro-preview. The data is correct; only the metadata field is wrong. |
| pro-high-image-n5 | 5 (all) | meta.json model field | CRITICAL (metadata) | configuration.model = gemini-3.1-pro-preview | configuration.model = gemini-3-flash | Same bug as above. |
| pro-medium-text-baseline | 1 | meta.json model field | CRITICAL (metadata) | configuration.model = gemini-3.1-pro-preview | configuration.model = gemini-3-flash | Same bug. |
| pro-medium-image-baseline | 1 | meta.json model field | CRITICAL (metadata) | configuration.model = gemini-3.1-pro-preview | configuration.model = gemini-3-flash | Same bug. |

**Note:** "CRITICAL (metadata)" means the metadata is wrong, not the data. The
actual API calls genuinely used Pro. The scientific results are valid; only the
`configuration.model` field in meta.json is misleading.

### HIGH Discrepancies (Unchanged from v1)

| Condition | Runs Affected | Check | Severity | Expected | Actual | Detail |
|-----------|---------------|-------|----------|----------|--------|--------|
| h11/consensus-384 | 30 (all) | 2: Intent<->Meta, 3: Propagation | HIGH | temperature=0.7 | temperature=1.0 | T=1.0 bug: YAML specifies T=0.7 but config JSON default T=1.0 was not overridden. |
| h11/single-pass-384 | 10 (all) | 2: Intent<->Meta, 3: Propagation | HIGH | temperature=0.0 | temperature=1.0 | Same T=1.0 bug. |

### WARNING Discrepancies (Unchanged from v1 except W2 corrected)

| Condition | Runs Affected | Check | Severity | Expected | Actual | Detail |
|-----------|---------------|-------|----------|----------|--------|--------|
| phase3a/track1-image-high | 90 (all) | 1: Label<->Meta | WARNING | thinking=high | thinking=minimal | Known mislabelling. |
| phase3a/track2-text-high | 90 (all) | 1: Label<->Meta | WARNING | thinking=high | thinking=minimal | Known mislabelling. |

### WARNING-2 (CORRECTED -- downgraded to INFO)

The v1 audit warned that pairwise test files reference deleted paths
(`pro-high-text-n5`, `pro-high-image-n5`). **This was wrong.** These paths
exist and are valid. The directories were never renamed. The pairwise test
`study_dir` fields correctly point to the Pro directories.

### INFO Discrepancies (Unchanged from v1)

Same as v1: 265 runs in Phases 1-2 missing `thinking_level`/`instruction_hash`
fields, plus 6 incomplete retest runs.

---

## Section 3: Confound Matrix (Corrected)

The critical correction: comparisons labelled "Pro vs Flash" in the pairwise
results ARE genuine model comparisons (Pro actually used Pro). The v1 audit
incorrectly treated all of these as "Flash vs Flash (same model)" after
wrongly concluding no run used Pro.

### Pairwise Comparisons Involving Pro (ALL GENUINELY Pro vs Flash)

| Comparison | Intended Variable | Config Parameters That Also Vary | Confounded? |
|------------|------------------|----------------------------------|-------------|
| **Pro HIGH text 3-of-5 vs Flash HIGH text 5-of-5** | model (Pro vs Flash) | consensus threshold (3 vs 5) | Minor (threshold) -- **VALID model comparison** |
| **Pro HIGH text 3-of-5 vs Flash MINIMAL-T0.7 text 5-of-5** | model + thinking_level | consensus threshold (3 vs 5) | **YES -- model AND thinking_level both vary** |
| **Pro HIGH text 3-of-5 vs Flash MINIMAL text 5-of-5 (consensus-384)** | model + thinking_level | **temperature (0.7 vs 1.0)**, threshold (3 vs 5) | **YES -- model, thinking_level, AND T=1.0 bug all confound** |
| **Pro HIGH text 3-of-5 vs Pro HIGH image 3-of-5** | modality (text vs image) | example_count (17 vs 13) | YES -- example_count differs (inherent design coupling) |
| **Pro HIGH image 3-of-5 vs Flash HIGH image 3-of-5** | model (Pro vs Flash) | None | **NO -- clean model comparison** |

### Flash-Only Comparisons (Unchanged from v1)

| Comparison | Intended Variable | Config Parameters That Also Vary | Confounded? |
|------------|------------------|----------------------------------|-------------|
| Flash HIGH image 3-of-5 vs Flash MINIMAL image 3-of-5 | thinking_level | None | NO |
| Flash HIGH image 7-of-10 vs Flash MINIMAL image 8-of-10 | thinking_level | consensus threshold (7 vs 8) | Minor (threshold) |
| Flash HIGH text 26-of-30 vs Flash HIGH text 9-of-10 | consensus params (pool+threshold) | None (same underlying data) | NO (same condition) |
| Flash HIGH text 26-of-30 vs Flash MINIMAL-T0.7 text 29-of-30 | thinking_level | consensus threshold (26 vs 29) | Minor (threshold) |
| Flash HIGH text 5-of-5 vs Flash HIGH image 3-of-5 | modality (text vs image) | example_count (17 vs 13), threshold (5 vs 3) | YES -- example_count differs |
| Flash HIGH text 5-of-5 vs Flash MINIMAL-T0.7 text 5-of-5 | thinking_level | None | NO |
| Flash HIGH text 5-of-5 vs Flash MINIMAL text 5-of-5 (consensus-384) | thinking_level | **temperature (0.7 vs 1.0)** | **YES -- T=1.0 bug confounds** |
| Flash HIGH text 9-of-10 vs Flash HIGH image 7-of-10 | modality | example_count (17 vs 13), threshold (9 vs 7) | YES -- example_count differs |
| Flash HIGH text 9-of-10 vs Flash HIGH text 5-of-5 | consensus params | None (same underlying data) | NO (same condition) |
| Flash HIGH text 9-of-10 vs Flash MINIMAL-T0.7 text 10-of-10 | thinking_level | consensus threshold (9 vs 10) | Minor (threshold) |
| Flash MINIMAL text T0.7 10-of-10 vs Flash MINIMAL text T1.0 9-of-10 | temperature | consensus threshold (10 vs 9) | T=1.0 was unintentional but data is valid |
| Flash MINIMAL text T0.7 29-of-30 vs Flash MINIMAL text T1.0 28-of-30 | temperature | consensus threshold (29 vs 28) | Same as above |
| Flash MINIMAL text T0.7 5-of-5 vs Flash MINIMAL text T1.0 5-of-5 | temperature | None | Partially valid (T=1.0 unintentional) |
| Image MINIMAL N=10 6-of-10 vs Image MINIMAL N=30 14-of-30 | consensus params (pool size) | None (same underlying data) | NO (same condition) |

### Summary of Confound Status

**Clean comparisons (single intended variable):**

- Pro HIGH image vs Flash HIGH image (model only) -- **NEW, valid**
- Flash HIGH vs Flash MINIMAL same-modality pairs (thinking_level only)
- Temperature T0.7 vs T1.0 (temperature only, though T1.0 unintentional)
- Same-condition pool-size comparisons

**Confounded comparisons:**

- Pro HIGH text vs Flash MINIMAL-T0.7 text (model + thinking_level)
- Pro HIGH text vs Flash MINIMAL text consensus-384 (model + thinking + temperature)
- All cross-modality text-vs-image comparisons (example_count confound)
- Flash HIGH text vs consensus-384 (T=1.0 bug)

**Partially confounded (minor):**

- Pro HIGH text vs Flash HIGH text (model + threshold 3 vs 5)

---

## Section 4: Cross-Run Consistency Exceptions

Unchanged from v1. The proposer-verifier-384 exceptions (different instruction
hashes and example counts) are expected across different verifier configurations.
All other conditions are internally consistent.

Additionally confirmed: all 5 runs within pro-high-text-n5 are mutually
consistent (same model, temperature, thinking level), and all 5 runs within
pro-high-image-n5 are mutually consistent.

---

## Section 5: Recommendations (Corrected)

### CRITICAL-1: meta.json `configuration.model` Bug (12 runs)

**Status:** Bug confirmed. The `configuration.model` field in meta.json for
all 12 Pro runs reads `gemini-3-flash` (the config JSON default) instead of
`gemini-3.1-pro-preview` (the actual model used).

**Root cause:** At the code version used for Pro runs (git `765cb232`,
script v1.5.0), the `LLMMetadataTracker` was initialised without the
`model_override` parameter. The fix (passing `model_override` to the tracker)
exists in the current code but was not yet wired up when these runs executed.

**Impact on analysis:** None. The GeoJSON features and `cost_estimate` fields
correctly identify the model. Any analysis that reads the model from GeoJSON
(which is the standard for evaluation scripts) is unaffected. Only tooling
that reads `configuration.model` from meta.json would misidentify these runs.

**Recommendation:** Either:

1. Patch the 12 meta.json files to correct `configuration.model` to
   `gemini-3.1-pro-preview`, or
2. Document the bug and always use GeoJSON `properties.model` or
   `cost_estimate.pricing_used.model` as the authoritative model source.

Option 2 is safer (no data mutation) and sufficient for analysis purposes.

### CRITICAL-2: v1 Audit's E42 Conclusion Was Wrong

**Status:** The v1 audit concluded E42 was "remediated by Session 57 rename."
This was incorrect. The Pro directories were never renamed; they retain their
original `pro-*` names. The Pro runs genuinely used Pro. E42 (Pro label but
Flash model) **did not occur** for these runs -- the labels are correct.

**Impact:** The v1 audit's entire model section must be disregarded. The
corrected model inventory is in this document (v2).

### HIGH-1: consensus-384 T=1.0 Bug (30 runs)

**Status:** Unchanged from v1. Known issue, corrected replacement exists
(`flash-minimal-text-n30-t07`).

### HIGH-2: single-pass-384 T=1.0 Bug (10 runs)

**Status:** Unchanged from v1. No corrected replacement exists yet.

### WARNING-1: Phase 3a "-high" Directory Mislabelling (180 runs)

**Status:** Unchanged from v1.

### WARNING-2: Pairwise Test Files Reference Deleted Paths

**Status:** CORRECTED -- this warning was wrong in v1. The paths exist. The
pairwise test files correctly reference `pro-high-text-n5` and
`pro-high-image-n5`, which are valid directories containing genuine Pro data.

### NEW: Scientific Implications of Corrected Model Identification

The discovery that 12 runs genuinely used Pro has significant implications:

1. **Pro vs Flash comparisons are real.** The pairwise tests
   `permutation-pro-high-text-3-of-5-vs-flash-high-text-5-of-5-20m.json`
   (p=0.874, no significant difference) and
   `permutation-pro-high-image-3-of-5-vs-flash-high-image-3-of-5-20m.json`
   (p=0.018, Flash significantly better) are genuine cross-model comparisons,
   not batch-identity tests.

2. **Pro HIGH text consensus F1=0.849** (3-of-5 threshold) is a real Pro
   result, not a mislabelled Flash result. This is close to but not clearly
   better than Flash HIGH text (F1=0.840 at 3-of-5 from the same comparison).

3. **Pro HIGH image consensus F1=0.703** (3-of-5 threshold) is genuinely
   worse than Flash HIGH image (F1=0.727 at 3-of-5, p=0.018). This is a
   real finding: Flash outperforms Pro on image-track detection.

4. **Pro MEDIUM baselines** (text F1, image F1) are real Pro baseline data
   that can be compared against the Flash baselines.

5. **E40 is genuinely not applicable** -- but for the right reason. The Pro
   runs used MEDIUM thinking (baselines) and HIGH thinking (n5 conditions).
   No Pro run attempted MINIMAL thinking, so no silent downgrade could have
   occurred. The study YAML for pro-medium-text-baseline explicitly notes
   "MINIMAL not supported by 3.1 Pro."

---

## Known Issue Verification (Corrected)

### E42: Pro Label But Flash Model

**Status: DID NOT OCCUR.** The v1 audit misdiagnosed E42 as having affected
these runs. In reality:

- 4 directories with "pro" in the name (`pro-high-text-n5`,
  `pro-high-image-n5`, `pro-medium-text-baseline`, `pro-medium-image-baseline`)
  genuinely used `gemini-3.1-pro-preview`.
- The `configuration.model` bug in meta.json made it appear as though they
  used Flash, but GeoJSON features, cost_estimate, and log files all confirm
  Pro.
- No directory rename occurred. The pro-* directories remain with their
  original names.

### T=1.0 Temperature Bug

**Status:** Unchanged from v1. Confirmed in consensus-384 (30 runs) and
single-pass-384 (10 runs).

### E40: Pro + MINIMAL Thinking Rejection

**Status: NOT APPLICABLE (correct reason).** The 12 Pro runs used MEDIUM
(2 baseline runs) and HIGH (10 n5 runs) thinking levels. No Pro run
attempted MINIMAL. The study designs explicitly accounted for Pro's MINIMAL
rejection by using MEDIUM for baselines.

---

## Metadata Bug Technical Detail

For future reference, the `configuration.model` bug in meta.json exists
because:

1. The config JSON file (`detect_brief-text.json`) contains
   `"model": "gemini-3-flash"` as a static default.
2. When `--model gemini-3.1-pro` is passed on the CLI, the detection script
   sets `config["model"] = "gemini-3.1-pro"` (line 676).
3. The model name is then resolved via `_resolve_model_name()` to
   `gemini-3.1-pro-preview` (line 727), but this resolution updates
   `model_name_cfg`, not `config["model"]`.
4. At script version 1.5.0, the `LLMMetadataTracker` was initialised with
   `config=config` but without `model_override=model_name_cfg`, so
   `configuration.model` in the output recorded `config.get("model")` which
   was `"gemini-3.1-pro"` -- wait, that should show "gemini-3.1-pro", not
   "gemini-3-flash".

**Further investigation:** The actual value in meta.json is `gemini-3-flash`,
not `gemini-3.1-pro`. This suggests the config dict mutation at line 676 was
either not effective (perhaps a copy was made) or the metadata tracker
captured the config before the override was applied. The `full_config_snapshot`
also shows `gemini-3-flash`, confirming the tracker saw the un-overridden
config. The most likely explanation is that the study orchestrator loaded
a fresh config per run rather than reusing the CLI-mutated dict.

Regardless of the exact mechanism, the outcome is clear: `configuration.model`
is unreliable for any run where `--model` was used, and the three alternative
sources (GeoJSON, cost_estimate, logs) are all consistent and correct.

---

## Final Completeness Check

1. **Total runs inventoried:** 1,740 across ~239 conditions. Same as v1.

2. **Model verification scope:** All 12 Pro-labelled runs individually
   verified via GeoJSON features and cost_estimate. All 1,532 non-H11 runs
   verified via cost_estimate (none are Pro). All Flash H11 runs verified
   via cost_estimate (none are Pro).

3. **Conditions entirely skipped:** None. All conditions with meta.json files
   were audited.

4. **Corrections from v1:** Model identification for 12 runs changed from
   "gemini-3-flash" to "gemini-3.1-pro-preview". E42 status changed from
   "remediated by rename" to "did not occur." WARNING-2 (deleted paths)
   downgraded to non-issue.

**Audit completion: 1,740/1,740 runs audited. Model field corrected for 12
runs via GeoJSON/cost_estimate verification. Temperature and thinking level
findings unchanged from v1.**

## Dated rider (2026-08-03, Session-126 C4 triage)

Two findings from the blind-verified wave-5 triage
(`reports/verification/c4-triage/mismatch-triage-2026-08-03.json`);
the body above is a dated snapshot and is unchanged.

1. **Era scope of the "12 Pro runs" figure.** Correct as at
   2026-03-25. The pro-high-text-n5 pool was extended to N=10 on
   2026-03-29 (runs 6–10; `study_manifest.json` rewritten in place),
   so a present-day recount from the manifests gives 17, and a
   directory census gives 21 (the two Pro MEDIUM baselines each
   gained runs 2–3 on 2026-06-03). Era arithmetic from run-start
   timestamps confirms 5+5+1+1 = 12 at audit time.
2. **Correction to "Scientific Implications" item 2 (lines
   313–315).** The Flash comparator quoted as "F1=0.840 at 3-of-5
   from the same comparison" is neither Flash nor 3-of-5: the cited
   pairwise record's Flash arm is Flash HIGH text 5-of-5 at
   global F1 0.7788, and Flash HIGH text at 3-of-5 is 0.6034; 0.840
   is the rounded **Pro** arm value 0.8404 from that same record. The
   sentence's qualitative conclusion is unaffected (the paired
   permutation gives p=0.874 on a per-tile mean difference of
   0.001772), but the quoted comparator must not be cited as a Flash
   figure.
