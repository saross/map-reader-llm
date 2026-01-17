# Instructions for CC: Naming Convention Enhancement

**Document:** `preregistration-appendix-prompts.md`  
**Section:** 1.0 Instruction File Summary  
**Location:** After line 193  
**Purpose:** Clarify the two-factor orthogonal structure to prevent confusion about filenames like `detect_verbose-text-image_terse.md`

---

## Task

Add explanatory text after the current naming convention description to clarify that the filename represents TWO INDEPENDENT factors.

## Current Text (lines 189-195)

```markdown
**Naming convention**: `detect_{modality}[_{h5_level}].md`

- `{modality}`: image-only, brief-text, brief-text-image, verbose-text, verbose-text-image
- `_{h5_level}`: suffix indicates H5 negative text treatment (omit for Minimal, `_terse` for Terse, `_verbose` for Verbose)
- **Text-only modalities** (brief-text, verbose-text) only have base (Minimal) variants since they cannot use example images for hard negatives

**Note on legacy naming**: The previous `_hardneg` suffix has been replaced with `_verbose` to better reflect the H5 redesign. The base instruction files (no suffix) now correspond to H5=Minimal rather than H5=None.
```

## Insert After Line 195

Add a new subsection:

```markdown
**Understanding the two-factor naming structure:**

The filename pattern reflects two **orthogonal experimental factors** (M/E and H5) that can be independently varied:

1. **First part** = M/E factor = **positive guidance** (what TO detect)
   - `image-only` → minimal text, visual examples only
   - `brief-text-image` → concise text + visual examples  
   - `verbose-text-image` → detailed text + visual examples

2. **Second part (suffix)** = H5 factor = **negative guidance** (what NOT to detect)
   - *(no suffix)* → H5=Minimal (no exclusion text)
   - `_terse` → H5=Terse (brief exclusion guidance, 1-2 sentences)
   - `_verbose` → H5=Verbose (detailed exclusion explanations)

**Examples:**
- `detect_verbose-text-image.md` = verbose positive + minimal negative (no suffix = H5=Minimal)
- `detect_verbose-text-image_terse.md` = verbose positive + terse negative
- `detect_image-only_verbose.md` = minimal positive + verbose negative
- `detect_brief-text-image_terse.md` = brief positive + terse negative

These factors are **independent**: any M/E level can be combined with any H5 level (for image-based M/E only). The "verbose" in `verbose-text-image` describes how to present POSITIVES (mound symbols). The "terse" in `_terse` describes how to present NEGATIVES (exclusion guidance). They control different aspects of the instruction.
```

## Result

After this insertion, the section should read:

```markdown
**Naming convention**: `detect_{modality}[_{h5_level}].md`

- `{modality}`: image-only, brief-text, brief-text-image, verbose-text, verbose-text-image
- `_{h5_level}`: suffix indicates H5 negative text treatment (omit for Minimal, `_terse` for Terse, `_verbose` for Verbose)
- **Text-only modalities** (brief-text, verbose-text) only have base (Minimal) variants since they cannot use example images for hard negatives

**Note on legacy naming**: The previous `_hardneg` suffix has been replaced with `_verbose` to better reflect the H5 redesign. The base instruction files (no suffix) now correspond to H5=Minimal rather than H5=None.

**Understanding the two-factor naming structure:**

The filename pattern reflects two **orthogonal experimental factors** (M/E and H5) that can be independently varied:

1. **First part** = M/E factor = **positive guidance** (what TO detect)
   - `image-only` → minimal text, visual examples only
   - `brief-text-image` → concise text + visual examples  
   - `verbose-text-image` → detailed text + visual examples

2. **Second part (suffix)** = H5 factor = **negative guidance** (what NOT to detect)
   - *(no suffix)* → H5=Minimal (no exclusion text)
   - `_terse` → H5=Terse (brief exclusion guidance, 1-2 sentences)
   - `_verbose` → H5=Verbose (detailed exclusion explanations)

**Examples:**
- `detect_verbose-text-image.md` = verbose positive + minimal negative (no suffix = H5=Minimal)
- `detect_verbose-text-image_terse.md` = verbose positive + terse negative
- `detect_image-only_verbose.md` = minimal positive + verbose negative
- `detect_brief-text-image_terse.md` = brief positive + terse negative

These factors are **independent**: any M/E level can be combined with any H5 level (for image-based M/E only). The "verbose" in `verbose-text-image` describes how to present POSITIVES (mound symbols). The "terse" in `_terse` describes how to present NEGATIVES (exclusion guidance). They control different aspects of the instruction.

---

### 1.1 Image-Only Instructions
[continues with existing content]
```

## Verification

After making this change:

1. Check that line breaks and markdown formatting are preserved
2. Verify the new subsection appears between the legacy naming note and Section 1.1
3. Confirm no other text was modified
4. Check that the examples clearly show the orthogonal two-factor structure

## Rationale

This enhancement directly addresses the potential confusion about filenames like `detect_verbose-text-image_terse.md` appearing to be both "verbose" and "terse" simultaneously. By explicitly explaining that these terms apply to DIFFERENT factors (positive vs negative guidance), we prevent misinterpretation and make the experimental design clearer to readers.
