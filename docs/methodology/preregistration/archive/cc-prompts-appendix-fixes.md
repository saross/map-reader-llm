# Prompts Appendix Final Review Fixes

**Purpose**: Correct errors, inconsistencies, and omissions identified in final review
**Date**: 2026-01-04
**Document**: preregistration-appendix-prompts.md

---

## Priority: HIGH

### 1. Config Count — 20 vs 16

**Location**: Lines 29-30

**Problem**: States "20 configuration files" but text-only modalities can't have H7=Images-only or H7=Both, so actual count is 16.

**Find**:
```markdown
This yields:

- **10 instruction files**: 5 M/E levels × 2 exclusion variants (base, `_hardneg`)
- **20 configuration files**: 5 M/E levels × 4 H7 levels
```

**Replace with**:
```markdown
This yields:

- **10 detection instruction files**: 5 M/E levels × 2 exclusion variants (base, `_hardneg`)
- **2 two-stage pipeline instruction files**: propose_image-only.md, verify_image-only.md
- **16 configuration files**: See Section 2.2 for breakdown

**Note on config count**: Text-only modalities (Brief-text, Verbose-text) cannot use H7=Images-only or H7=Both since they have no example images. This reduces the factorial from 5×4=20 to 16 valid combinations:
- 3 image-using modalities × 4 H7 levels = 12
- 2 text-only modalities × 2 H7 levels (None, Text-only) = 4
```

---

### 2. Phase 1 Baseline Runs — Align with Preregistration

**Location**: Lines 55-56

**Problem**: Says "K=10 runs" and "≥3/10 runs" but preregistration Section 8.4.1 specifies 5 passes and ≥3/5 threshold.

**Find**:
```markdown
1. Run image-only baseline on 20 training tiles (K=10 runs)
2. Identify False Positives (≥3/10 runs) → select top M as hard negatives
```

**Replace with**:
```markdown
1. Run image-only baseline on 20 training tiles (5 passes)
2. Identify False Positives (≥3/5 passes) → select top M as hard negatives
```

---

### 3. Hard Negative Labels — Minimal for Images-Only Condition

**Location**: Section 2.5 (detect_image-only_images.json), lines 975-977

**Problem**: H7=Images-only should use minimal labels ("Negative"), not detailed explanatory labels. Detailed labels are for H7=Text+Images only.

**Find** (in Section 2.5, detect_image-only_images.json):
```json
        {"path": "examples/hardneg_standalone_benchmark.png", "label": "Negative: Benchmark ALONE (no mound). NO radiating rays.", "category": "hard_negative"},
        {"path": "examples/hardneg_standalone_triangulation.png", "label": "Negative: Triangulation Point ALONE (no mound). NO radiating rays.", "category": "hard_negative"},
        {"path": "examples/hardneg_empirical_TBD_01.png", "label": "Negative: [TBD from Phase 1 FP analysis]", "category": "hard_negative"}
```

**Replace with**:
```json
        {"path": "examples/hardneg_standalone_benchmark.png", "label": "Negative", "category": "hard_negative"},
        {"path": "examples/hardneg_standalone_triangulation.png", "label": "Negative", "category": "hard_negative"},
        {"path": "examples/hardneg_empirical_TBD_01.png", "label": "Negative", "category": "hard_negative"}
```

**Also add explanatory note** after the config (around line 980):

```markdown
**Label convention for H7 conditions:**

| H7 Level | Hard Negative Label Style |
|----------|---------------------------|
| Images-only | Minimal: `"Negative"` |
| Text+Images | Detailed: `"Negative: Benchmark ALONE (no mound). NO radiating rays."` |

This distinction tests whether the model needs explicit textual explanation of why examples are negative, or whether visual examples alone suffice.
```

---

## Priority: MEDIUM

### 4. Missing Hard Positive Examples in Configs

**Location**: All example configs (Sections 2.4-2.8)

**Problem**: Library composition should include hard positives (FNs) per preregistration Section 8.4.2, but example configs only show canonical positives, nulls, and hard negatives.

**Add to Section 2.4** (detect_image-only_none.json), after the null tiles and before `ordering_note`:

```json
        {"path": "examples/hardpos_empirical_TBD_01.png", "label": "Positive: [TBD from Phase 1 FN analysis]", "category": "hard_positive"},
        {"path": "examples/hardpos_empirical_TBD_02.png", "label": "Positive: [TBD from Phase 1 FN analysis]", "category": "hard_positive"}
```

**Update ordering_note**:
```json
    "ordering_note": "Canonical-first: legend positives, hard positives, nulls."
```

**Apply similar changes to all example configs** (Sections 2.5, 2.6, 2.7, 2.8), adjusting ordering_note as appropriate:
- For configs with hard negatives: `"Canonical-first: legend positives, hard positives, nulls, then hard negatives."`

---

### 5. Config Naming Alignment with Preregistration

**Location**: Section 2.2 and throughout

**Problem**: Need to ensure naming pattern matches what preregistration specifies.

**Confirm pattern** (this should match preregistration after its fixes are applied):

```markdown
**Pattern**: `detect_{modality}_{hardneg}.json`

Where:

- `{modality}`: image-only, brief-text, brief-text-image, verbose-text, verbose-text-image
- `{hardneg}`: none, text, images, both
```

**Note**: If the preregistration CC instructions used different naming (e.g., `hardneg-text` vs `text`), align both documents to use the same pattern. The simpler pattern (`none`, `text`, `images`, `both`) is recommended.

---

### 6. Standardise "hachures; spikes" Throughout

**Location**: All prompt text

**Problem**: Inconsistent use of "rays (hachures)" vs "rays (hachures; spikes)".

**Find all instances of**:
- `rays (hachures)` 
- `radiating rays`
- `short rays`

**Replace with** (where parenthetical is used):
- `rays (hachures; spikes)`

**Specific locations to check and update**:

**Line 179** (detect_image-only_hardneg.md):
- Find: `radiating rays` → Keep as is (no parenthetical needed here)

**Line 225** (detect_brief-text.md):
- Find: `radiating **rays** (hachures; spikes)` → Already correct

**Line 375** (detect_brief-text-image.md):
- Find: `short rays (hachures; spikes)` → Already correct

**Line 433** (detect_brief-text-image_hardneg.md):
- Find: `short rays (hachures; spikes)` → Already correct

**Line 476** (detect_verbose-text.md):
- Find: `radiating rays (hachures; spikes)` → Already correct

**Scan all prompts** and ensure that wherever the parenthetical explanation appears, it includes both terms: `(hachures; spikes)`

---

## Priority: LOW

### 7. Verifier Prompt — Fix Misleading Default Value

**Location**: Line 819

**Problem**: Showing `0.0` as example suggests "not a mound."

**Find**:
```json
{
    "reasoning": "Brief description of visual features observed.",
    "mound_probability": 0.0
}
```

**Replace with**:
```json
{
    "reasoning": "<Brief description of visual features observed>",
    "mound_probability": "<0.0-1.0>"
}
```

---

### 8. Add H10 Verification Prompt Placeholder

**Location**: After Section 1.6 (Two-Stage Pipeline Prompts)

**Add new section**:

```markdown
### 1.7 Fine-to-Coarse Verification Prompt (H10)

**Status**: Exploratory — prompt to be finalised if H10 is conducted.

#### 1.7.1 verify_context-expanded.md

**Purpose**: Focused verification for uncertain detections with expanded spatial context.
**Used by**: H10 (Stage 2 re-query for 2/5 or 3/5 consensus cases)

```markdown
# Context-Expanded Verification

Examine the centre of this image. Is there a burial mound symbol at that location?

The image shows an expanded view (~896×896 pixels) centred on a candidate detection from initial analysis.

## Task

Determine whether the feature at the centre matches burial mound symbols:
- Look for radiating rays (hachures; spikes) extending outward
- Consider the surrounding context for disambiguation

## Output Format

Return a JSON object:

{
    "is_mound": true | false,
    "confidence": "<low | medium | high>",
    "reasoning": "<Brief explanation>"
}
```

**Note**: This prompt will be refined based on Stage 1 results before H10 testing.
```

---

### 9. Add H5 Ordering Example Config

**Location**: After Section 2.9 (line 1086)

**Add complete example**:

```markdown
#### Example: Canonical-Last Ordering

**detect_image-only_none_canonical-last.json**

```json
{
    "version": "detect_image-only_none_canonical-last",
    "description": "Image-only baseline with canonical-LAST ordering (H5 variant).",
    "hypothesis": "M/E=Image-only, H7=None, O=Canonical-last",
    "model": "gemini-3-flash",
    "instruction_file": "detect_image-only.md",
    "temperature": 1.0,
    "max_output_tokens": 8192,
    "examples": [
        {"path": "examples/hardpos_empirical_TBD_01.png", "label": "Positive", "category": "hard_positive"},
        {"path": "examples/hardpos_empirical_TBD_02.png", "label": "Positive", "category": "hard_positive"},
        {"path": "examples/null_tile_01.png", "label": "Negative", "category": "null"},
        {"path": "examples/null_tile_02.png", "label": "Negative", "category": "null"},
        {"path": "examples/null_tile_03.png", "label": "Negative", "category": "null"},
        {"path": "examples/canonical_burial_mound.png", "label": "Positive", "category": "canonical"},
        {"path": "examples/canonical_settlement_mound.png", "label": "Positive", "category": "canonical"},
        {"path": "examples/canonical_triangulation_mound.png", "label": "Positive", "category": "canonical"},
        {"path": "examples/canonical_benchmark_mound.png", "label": "Positive", "category": "canonical"}
    ],
    "ordering_note": "Canonical-LAST: hard positives first, nulls, then legend positives in final positions (testing recency bias)."
}
```

**Note**: For conditions with hard negatives, the canonical-last ordering places hard negatives before nulls and canonical examples last.
```

---

### 10. Update Document Version

**Location**: Lines 1186-1188

**Find**:
```markdown
*Document version: 2.0*
*Created: 2026-01-02*
*Updated: 2026-01-04*
```

**Replace with**:
```markdown
*Document version: 2.1*
*Created: 2026-01-02*
*Updated: 2026-01-04*
```

**Add to changelog** (after line 1192):
```markdown
- v2.1: Final review fixes — corrected config count (20→16); aligned Phase 1 baseline with preregistration (5 passes, ≥3/5); fixed hard negative labels for Images-only condition (minimal labels); added hard positive placeholders to example configs; added H10 verification prompt placeholder; added H5 ordering example config; standardised "hachures; spikes" throughout
```

---

## Alignment Note for Preregistration

The preregistration CC instructions (cc-preregistration-final-fixes.md) specified config naming as:

```
detect_{modality}_{hardneg}.json
Examples: detect_text-brief_hardneg-text.json
```

But this appendix uses:

```
detect_{modality}_{hardneg}.json
Examples: detect_brief-text_text.json
```

**Two differences**:
1. Modality order: `text-brief` vs `brief-text`
2. Hardneg naming: `hardneg-text` vs `text`

**Recommendation**: Use the appendix pattern (simpler):
- Modality: `brief-text`, `brief-text-image`, `verbose-text`, `verbose-text-image`
- Hardneg: `none`, `text`, `images`, `both`

**Update the preregistration CC instructions** Section 2 (Config Naming) to match:

```markdown
| Config Pattern | M/E | H7 |
| :--- | :--- | :--- |
| `detect_image-only_none.json` | Image-only | None |
| `detect_brief-text_text.json` | Brief-text | Text-only |
| `detect_brief-text-image_images.json` | Brief-text+image | Images-only |
| `detect_verbose-text-image_both.json` | Verbose-text+image | Text+Images |
```

---

## Verification Checklist

After implementing all changes:

- [ ] Lines 29-30: Config count is 16, not 20, with explanation
- [ ] Lines 55-56: Phase 1 is "5 passes" and "≥3/5"
- [ ] Section 2.5: Hard negative labels are minimal ("Negative") for Images-only
- [ ] Section 2.6: Hard negative labels are detailed for Text+Images (unchanged)
- [ ] All example configs include hard_positive placeholders
- [ ] H10 verification prompt section added (Section 1.7)
- [ ] H5 canonical-last example config added
- [ ] All prompts use "hachures; spikes" consistently
- [ ] Verifier prompt uses placeholder notation
- [ ] Version updated to 2.1 with changelog
- [ ] Naming pattern aligned with preregistration

---

*Instructions prepared 2026-01-04*
