# Editing Instructions: H6 Text Diversity Specification

**Purpose**: Add detailed specification of text diversity methodology for H6
**Files to edit**: `preregistration.md`, `preregistration-appendix-prompts.md`

---

## 1. Edit preregistration.md

### 1.1 Add Section 8.3.3 (after Section 8.3.2)

Insert new section:

```markdown
#### 8.3.3 H6 Text Diversity Specification

**Variation level**: Level 3 (Content variation, fixed structure)

All 5 prompt variants maintain identical structure (same sections, same order, same output format) while varying:

1. **Task framing**: The opening instruction line using varied terminology:
   - Action verbs: identify, detect, find, locate, mark
   - Domain vocabulary: burial mound, tumuli, kurgan, mound features, cartographic symbols

2. **Instruction phrasing**: The task elaboration sentence following reference examples (semantically equivalent, differently worded)

3. **Guideline wording**: Semantically equivalent guidelines with varied phrasing (e.g., "focus on sunburst shape" vs "look for gear/ship's wheel pattern"; "include borderline cases" vs "favour inclusion over omission")

**Elements held constant across all variants:**

- Section headers and order
- Output format specification (JSON schema)
- Number and type of guidelines (3 guidelines in all variants)
- Reference example labelling convention
- Exclusion guidance text (if hard negatives in base config)

**Rationale**: This isolates content diversity from structural diversity, enabling clean attribution of any observed effect to semantic variation rather than prompt organisation.

**Potential extension**: If content diversity shows significant benefit, structural diversity (varied section headers, reorganised flow) may be explored as a follow-on investigation in Stage 2.

**Construction procedure**:

1. Identify optimal base configuration from main factorial (M, O, H, T) and H2 (E)
2. Use the winning prompt template as the structural base
3. Create V1-V5 by varying task framing, instruction phrasing, and guideline wording
4. Verify semantic equivalence across all 5 variants
5. Document final prompt text in pre-holdout specifications
```

---

### 1.2 Update H6 in Section 5 (around line 459-477)

Find this text:
```markdown
**Text variants** (semantically equivalent task instructions):

1. "Identify burial mound symbols in this map section"  
2. "Detect tumuli markers on this topographic map"  
3. "Find kurgan indicators in this image"  
4. "Locate ancient burial mound cartographic symbols"  
5. "Mark all mound features shown on this Soviet map"
```

Replace with:
```markdown
**Text variants** (semantically equivalent task instructions):

Task framing examples (opening lines):

1. "Identify burial mound symbols in this map section"  
2. "Detect tumuli markers on this topographic map"  
3. "Find kurgan indicators in this image"  
4. "Locate ancient burial mound cartographic symbols"  
5. "Mark all mound features shown on this Soviet map"

**Variation approach**: Content diversity with fixed structure (Level 3). All variants maintain identical prompt structure while varying task framing, instruction phrasing, and guideline wording. See Section 8.3.3 for full specification.
```

---

### 1.3 Update H6 Image diversity implementation (around line 473-474)

Find this text:
```markdown
* Canonical examples (legend-derived symbols) and null tiles remain fixed across all conditions and passes
**Replication**: Each condition (A, B, C, D) is run 5 times
```

Insert between these lines:
```markdown
* Canonical examples (legend-derived symbols) and null tiles remain fixed across all conditions and passes

**Text vs structure variation**: H6 tests content diversity (varied wording) not structural diversity (varied organisation). This isolates the effect of semantic variation from potential confounds introduced by prompt restructuring.

**Replication**: Each condition (A, B, C, D) is run 5 times
```

---

## 2. Edit preregistration-appendix-prompts.md

### 2.1 Add Pre-Holdout Finalization section (after Overview, around line 16)

Insert new section:

```markdown
---

## Pre-Holdout Finalization

The following elements will be finalized before holdout evaluation:

### Empirically-Determined Images

All configuration files that include hard examples (hard positives, hard negatives) currently use placeholder paths (e.g., `neutral/example_08.png`). These will be replaced with actual images selected via the procedure in preregistration.md Section 8.4.2:

1. Run baseline library (4 canonical positives + 3 null tiles) on 20 training tiles
2. Identify False Negatives (≥3/5 passes) → select top K as hard positives
3. Identify False Positives (≥3/5 passes) → select top M as hard negatives
4. Document selected images with filenames, source tiles, and selection rationale

**Configs affected:**
- All `*_hardneg.json` variants (H7)
- `propose_image-only.json` and `verify_image-only.json` (H3)
- H6 diversity conditions C and D (varied images)

### H6 Text Diversity Prompts

The 5 semantically equivalent prompt variants (V1-V5) will be constructed after the optimal base configuration is determined from the main factorial and H2 experiments.

**Construction procedure:**
1. Identify winning configuration (modality, elaboration, hard negatives, ordering, temperature)
2. Use the corresponding prompt template as structural base
3. Create V1-V5 using Level 3 variation (content diversity, fixed structure):
   - Vary task framing line
   - Vary instruction phrasing
   - Vary guideline wording
   - Keep structure, headers, output format identical
4. Document all 5 variants in pre-holdout specifications

**Task framing variants** (opening lines, documented in preregistration.md Section 8.3.2):
1. "Identify burial mound symbols in this map section"
2. "Detect tumuli markers on this topographic map"
3. "Find kurgan indicators in this image"
4. "Locate ancient burial mound cartographic symbols"
5. "Mark all mound features shown on this Soviet map"

See preregistration.md Section 8.3.3 for full specification of variation approach.

### Finalization Documentation

Before any holdout evaluation, the following will be uploaded to the connected OSF project:

- Final image filenames for all hard examples
- Selection rationale (frequency counts from training evaluation)  
- Complete H6 prompt variants (V1-V5)
- Exact ordering for each condition
- Random seeds used
```

---

### 2.2 Update Section 1.1.1 header comment

Find (around line 24-28):
```markdown
#### 1.1.1 detect_image-only.md

**Purpose**: Baseline image-only detection with minimal text instruction.
**Used by**: H1 (image-only condition), H5, H7 (baseline), H9
```

Add after "Used by" line:
```markdown
**H6 note**: If image-only is the optimal base configuration, this template's structure will be used for H6 V1-V5 variants (with varied content per Section 8.3.3).
```

---

### 2.3 Update Section 1.1.4 header comment

Find (around line 248-251):
```markdown
#### 1.1.4 detect_text-image.md

**Purpose**: Combined text and image prompt with reference examples.
**Used by**: H1 (text+image condition), H2 (brief)
```

Add after "Used by" line:
```markdown
**H6 note**: If text+image is the optimal base configuration, this template's structure will be used for H6 V1-V5 variants (with varied content per Section 8.3.3).
```

---

## 3. Verification Checklist

After edits, verify:

- [ ] Section 8.3.3 exists and fully specifies Level 3 variation
- [ ] H6 in Section 5 references Section 8.3.3
- [ ] H6 explicitly states "content diversity not structural diversity"
- [ ] Prompts appendix has Pre-Holdout Finalization section
- [ ] Prompts appendix explains H6 variants are constructed post-factorial
- [ ] Task framing examples (V1-V5 opening lines) appear in both documents
- [ ] Cross-references between documents are accurate

---

## 4. Additional Fix (from previous review)

### 4.1 Fix dangling reference in preregistration.md

Find (around line 403-405):
```markdown
targeted voting threshold testing at contrasting configurations may be warranted (see Section 8: Extended Coverage).
```

Replace with:
```markdown
targeted voting threshold testing at contrasting configurations may be warranted (see preregistration-coverage.md, Section 4).
```

---

*Instructions prepared 2026-01-02*
