# Prompt Standardisation Plan

**Created**: 2026-01-01
**Purpose**: Use `h2-text-elaboration-comparison.md` as the master source for all detection prompts

---

## Overview

The comparison document contains carefully designed brief and elaborate prompts with:

- Consistent terminology: "rays (hachures; spikes)"
- Matched uncertainty guidance across all conditions
- Standardised structure and formatting
- Explicit direction cues ("extending OUTWARD")

All detection prompts should derive from this master source to ensure experimental validity.

---

## Current State

### System Instructions (11 files)

| File | Status | Action |
| :--- | :--- | :--- |
| `detect_text-only.md` | Outdated | **Update** from comparison Section 1 Brief |
| `detect_text-only-hardneg.md` | Outdated | **Update** from comparison Section 2 Brief |
| `detect_text-image.md` | Outdated | **Update** from comparison Section 3 Brief |
| `detect_text-image-hardneg.md` | Outdated | **Update** from comparison Section 4 Brief |
| `detect_text-only-elaborate.md` | ✅ Current | Already created from comparison |
| `detect_text-only-elaborate-hardneg.md` | ✅ Current | Already created from comparison |
| `detect_text-image-elaborate.md` | ✅ Current | Already created from comparison |
| `detect_text-image-elaborate-hardneg.md` | ✅ Current | Already created from comparison |
| `detect_image-only.md` | Minimal | **Review** for consistency |
| `propose_image-only.md` | H3 specific | **Review** terminology |
| `verify_image-only.md` | H3 specific | **Review** terminology |

### Configs (20 files)

All configs point to instruction files. No content changes needed, but verify after instruction updates.

---

## Phase 1: Update Brief System Instructions

Replace existing brief prompts with content from comparison doc.

### 1.1 Text-Only Brief

**Source**: Section 1 Brief (~320 words)
**Target**: `prompts/system-instructions/detect_text-only.md`

Key elements to include:

- Title: "Detection Prompt: Text-Only Baseline"
- Target Symbols A-D with standardised descriptions
- "rays (hachures; spikes)" terminology throughout
- Exclusion Criteria section (brief version)
- Handling Occlusion section
- Separating Clusters section
- When Uncertain section
- JSON output format

### 1.2 Text-Only Brief with Hard Negatives

**Source**: Section 2 Brief (~420 words)
**Target**: `prompts/system-instructions/detect_text-only-hardneg.md`

Same as 1.1 plus:

- Expanded Exclusion Criteria with 4 false positive categories
- When Uncertain section

### 1.3 Text+Image Brief

**Source**: Section 3 Brief (~190 words)
**Target**: `prompts/system-instructions/detect_text-image.md`

Key elements:

- Title: "Detection Prompt: Text+Image Baseline"
- Reference Examples section
- Task section
- 4 Guidelines (Visual Match, Separate Clusters, Refer to Examples, Default to inclusion)
- "extending OUTWARD" direction cue
- JSON output format

### 1.4 Text+Image Brief with Hard Negatives

**Source**: Section 4 Brief (~220 words)
**Target**: `prompts/system-instructions/detect_text-image-hardneg.md`

Same as 1.3 plus:

- Exclusion Guidance section

---

## Phase 2: Review Image-Only Prompt

The image-only prompt is intentionally minimal (testing pure visual matching without text guidance). Current content:

```markdown
# Mound Detection (Image-Only)

Scan the Target Image. Mark all symbols that look like the Positive examples.

Return JSON with normalised coordinates (0-1000):
{"detections": [{"box_2d": [ymin, xmin, ymax, xmax], "label": "mound"}]}
```

### Decision Required

**Option A**: Keep minimal (current)

- Pros: Clean test of image-only modality, no text interference
- Cons: No subtype field, inconsistent output format

**Option B**: Add subtype and consistent output format

- Align JSON output with other prompts (include subtype field)
- Keep instruction text minimal

**Recommendation**: Option B - update output format only

```markdown
# Mound Detection (Image-Only)

Scan the Target Image. Mark all symbols that look like the Positive examples.

Return JSON with normalised coordinates (0-1000):

{
    "detections": [
        {
            "box_2d": [ymin, xmin, ymax, xmax],
            "label": "mound",
            "subtype": "burial_mound" | "settlement_mound" | "triangulation_mound" | "benchmark_mound"
        }
    ]
}
```

---

## Phase 3: Review Propose/Verify Prompts (H3)

These prompts test the two-stage pipeline hypothesis (H3). They should maintain their current structure but use consistent terminology.

### 3.1 Propose (Stage 1)

Current issues:

- Uses "spikes" without "(hachures)" synonym
- Otherwise structurally appropriate

Update: Replace "spikes/hachures" → "rays (hachures; spikes)" where applicable

### 3.2 Verify (Stage 2)

Current issues:

- Scoring guide uses "spikes/hachures"

Update: Standardise terminology

---

## Phase 4: Update Comparison Doc Status

After all updates, mark the "Files to Create" section in comparison doc as complete.

---

## Execution Checklist

### Phase 1: Brief Instructions

- [ ] Update `detect_text-only.md` from Section 1 Brief
- [ ] Update `detect_text-only-hardneg.md` from Section 2 Brief
- [ ] Update `detect_text-image.md` from Section 3 Brief
- [ ] Update `detect_text-image-hardneg.md` from Section 4 Brief

### Phase 2: Image-Only

- [ ] Update `detect_image-only.md` output format (add subtype)

### Phase 3: Propose/Verify

- [ ] Update `propose_image-only.md` terminology
- [ ] Update `verify_image-only.md` terminology

### Phase 4: Documentation

- [ ] Update comparison doc "Files to Create" section
- [ ] Verify all configs still point to correct files

### Phase 5: Commit

- [ ] Commit with message: `refactor(prompts): Standardise all detection prompts from master comparison doc`

---

## Verification

After updates, run grep to verify consistency:

```bash
# Should find "rays (hachures; spikes)" in all text prompts
grep -r "rays (hachures; spikes)" prompts/system-instructions/

# Should NOT find orphaned "spikes" without context
grep -r "spikes" prompts/system-instructions/ | grep -v "hachures"
```

---

*Plan ready for execution.*
