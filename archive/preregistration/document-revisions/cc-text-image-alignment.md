# Text-Image Alignment: Library and Verbose Text Construction

**Purpose**: Update preregistration to specify aligned construction of hard example library and verbose text
**Date**: 2026-01-03
**Rationale**: Verbose text should describe the hard examples in the image library, not independently-derived text-only failures

---

## Summary

**Key decision**: Derive all hard example content (images AND text) from image-only baseline failures.

| Element | Source | Alignment |
|---------|--------|-----------|
| Hard positive images | Image-only FNs | — |
| Hard negative images | Image-only FPs | — |
| Verbose text additions | Same FPs/FNs | Text describes what's in image library |

**Rationale**:
- Image-based discovery is the primary optimization target
- Text-only modality is primarily for academic comparison
- Aligned text and images reinforce rather than contradict
- Operationally relevant: deployment will likely use images

---

## 1. Update Phase 1 Procedure

### Location: Section 8.4 (Few-Shot Library Construction) or equivalent

### Replace/Update Library Construction Section

```markdown
#### 8.4.1 Library and Verbose Text Construction

**Overview**: Hard examples (images) and verbose text additions are derived from the same source — image-only baseline failures on training tiles. This ensures text descriptions align with the visual examples shown to the model.

**Rationale**: 
- Image-based discovery is the primary optimization target
- Text-only conditions serve as academic baseline comparisons
- Aligned text and images reinforce rather than contradict
- Avoids potential confusion from text describing failures not shown in images

**Step 1: Image-Only Baseline**

Run baseline detection on training tiles:
- Prompt: Image-only (4 canonical positives + 3 null tiles, minimal text instruction)
- Passes: 5 × 20 training tiles = 100 API calls
- Temperature: T=1.0

**Step 2: Failure Analysis**

Identify systematic failures:
- **False Negatives (FNs)**: Ground truth mounds missed in ≥3/5 passes
- **False Positives (FPs)**: Detections in ≥3/5 passes with no matching ground truth

Rank by frequency and categorize by failure type.

**Step 3: Construct Hard Example Library**

Select hard examples based on frequency ranking:
- **Hard positives**: Top K FNs (target K=4)
- **Hard negatives**: Top M FPs (target M=3)

Document for each selected example:
- Source tile
- Frequency (passes where failure occurred)
- Failure category (e.g., "occluded mound", "benchmark confusion")

**Step 4: Construct Verbose Text**

Build verbose text by adding targeted guidance for each hard example:

| Component | Source | Content |
|-----------|--------|---------|
| Base | Legend descriptions | Brief text describing canonical mound types |
| Exclusion guidance | Hard negative images | Text describing why each FP is NOT a mound |
| Edge case guidance | Hard positive images | Text describing why each FN IS a mound |

**Alignment requirement**: Each hard example image must have corresponding text guidance. The verbose text directly describes the hard examples in the library.

**Example verbose text additions:**

If hard negative images include benchmarks (from FP analysis):
> "**Exclusion: Benchmark (standalone)** — A hollow black square with central dot but NO radiating rays. The absence of rays distinguishes this from a benchmark ON a mound. Do NOT mark."

If hard positive images include occluded mounds (from FN analysis):
> "**Edge case: Partially occluded mounds** — Mound symbols may be intersected by contour lines, roads, or grid lines. The characteristic sunburst shape remains identifiable even when partially obscured. DO mark these."

**Step 5: Construct Brief vs Verbose Text**

| Text Version | Content |
|--------------|---------|
| Brief text | Legend-based descriptions of canonical mound types only (~200-400 words) |
| Verbose text | Brief text + exclusion guidance + edge case guidance (~700-1400 words) |

**Text-modality consistency**: Identical text is used across modalities:
- Text-only brief = Text+image brief (same text)
- Text-only verbose = Text+image verbose (same text)

**Step 6: Document and Upload**

Before any holdout evaluation, upload to OSF:
- Few-shot library manifest (image filenames, labels, ordering)
- Brief text (full prompt)
- Verbose text (full prompt with annotations showing which additions address which hard examples)
- Mapping table: hard example image ↔ corresponding text guidance
```

---

## 2. Update H2 (Text Elaboration)

### Location: Section 5, H2

### Update H2 Description

```markdown
### H2: Text Elaboration Does Not Improve Performance

**Background**: Adding lengthy descriptive text instructions does not appear to improve performance over brief text instructions in preliminary testing.

**Prediction**: Verbose text instructions will not significantly improve F1 compared to brief instructions.

**Text construction methodology**: 
- **Brief text**: Legend-based descriptions of canonical mound symbol types
- **Verbose text**: Brief text + targeted additions addressing hard example failures (see Section 8.4.1)

Verbose text additions are derived from image-only baseline failures, ensuring text guidance describes the same edge cases and exclusions present in the hard example image library. This alignment means:
- In text+image conditions: verbose text reinforces the visual hard examples
- In text-only conditions: verbose text provides conceptual guidance without visual anchors

**Test**: Planned contrasts within the main factorial:
- Brief-text vs Verbose-text (text-only comparison)
- Brief-text+image vs Verbose-text+image (text+image comparison)

**Analysis**: One-tailed tests; H0: verbose ≤ brief; H1: verbose > brief. Prediction is that H0 will not be rejected (verbose does not significantly help).

**Interpretation note**: Text-only conditions serve primarily as academic baselines. The operationally-relevant comparison is Brief-text+image vs Verbose-text+image, as deployment will likely include visual examples.

**Advance to Stage 2 if**: Verbose text shows significant improvement in either comparison (would contradict preliminary findings).
```

---

## 3. Update H7 (Hard Negatives)

### Location: Section 5, H7

### Update H7 Description to Clarify Alignment

```markdown
### H7: Hard Negative Examples Improve Precision

**Background**: Hard negative mining is established in few-shot learning. Two channels could improve precision: (1) explicit text instructions describing what to exclude; (2) visual counter-examples showing confusable symbols. These may operate independently or synergistically.

**Prediction**: Including hard negative information (text and/or images) will improve precision without significantly harming recall.

**Test**: 2×2 factorial design comparing:

| Condition | Exclusion Text | Hard Neg Images | Description |
| ----- | ----- | ----- | ----- |
| A | No | No | Baseline: positive examples only, no exclusion guidance |
| B | Yes | No | Text-only: explicit exclusion instructions, no visual counter-examples |
| C | No | Yes | Image-only: hard negative images with minimal labels ("Negative") |
| D | Yes | Yes | Combined: hard negative images with explicit explanatory labels |

**Alignment of text and images**: 

The exclusion text in Conditions B and D describes the same failures as the hard negative images in Conditions C and D. Both are derived from False Positives in the image-only baseline (see Section 8.4.1).

This means:
- Condition B: Verbal description of FPs (no visual examples)
- Condition C: Visual examples of FPs (minimal labels)
- Condition D: Visual examples + verbal descriptions (reinforcement)

**What H7 tests**:
- Does the model need to *see* hard negatives (C), *read about* them (B), or both (D)?
- Is there redundancy (D ≈ B or C) or synergy (D > B and D > C)?

**Hard negative sources**:

1. **Legend-derived negatives**: Visually confusable symbols confirmed from Soviet topographic legend (benchmark standalone, triangulation point standalone)
2. **Empirically-derived negatives**: False positives with ≥3/5 occurrence during image-only baseline on training tiles

**Text implementation**:

- Condition A: No exclusion guidance in prompt  
- Condition B: Exclusion instructions describing hard negative categories (e.g., "Do NOT mark: benchmarks without radiating rays, isolated triangulation points...")
- Condition D: Same exclusion instructions as B, plus explanatory labels on hard negative images (e.g., "Negative: Benchmark ALONE — square with dot but NO radiating rays. NOT a mound.")

**Image label implementation**:

- Condition C: Minimal labels only ("Negative" or "Negative: Not a mound")  
- Condition D: Labels with distinguishing features matching the exclusion text

**Analysis**:

* Primary: 2×2 factorial ANOVA testing main effects (exclusion text, hard negative images) and interaction on precision  
* Secondary: Parallel analysis on recall to confirm no significant harm  
* Tertiary: Analysis on F1 to assess net benefit

**Advance to Stage 2 if**: Either main effect significantly improves precision AND recall does not significantly decrease.
```

---

## 4. Clarify Text-Only Role

### Add Clarifying Paragraph to Section 1 or Section 5 Preamble

```markdown
**Role of text-only conditions**: 

Text-only conditions (Brief-text, Verbose-text) serve primarily as academic baselines to assess VLM capability without visual examples. The primary optimization target is image-based discovery, as operational deployment will likely include few-shot visual examples.

Text-only results inform:
- Whether text guidance alone has any value (academic interest)
- Whether adding images to text improves performance (H1)
- Baseline comparison for text+image improvements

Text-only conditions are NOT separately optimized. The same text (brief and verbose) is used across all modalities to isolate the effect of adding images.
```

---

## 5. Update Execution Plan

### Update Phase 1 in execution-plan.md

```markdown
## Phase 1: Library and Verbose Text Construction

**Duration**: 0.5 days
**Estimated cost**: ~$0.15 (Flash)
**Prerequisite for**: All subsequent phases

### Purpose

Run image-only baseline on training tiles to:
1. Identify hard examples for the few-shot library
2. Derive verbose text additions from the same failures

### Procedure

**Step 1: Image-Only Baseline**
- Prompt: Image-only (4 canonical + 3 null, minimal text)
- Runs: 5 passes × 20 training tiles = 100 API calls
- Temperature: T=1.0

**Step 2: Failure Analysis**
- Identify FNs: Ground truth mounds missed in ≥3/5 passes
- Identify FPs: Detections in ≥3/5 passes with no matching ground truth
- Rank by frequency, categorize by failure type

**Step 3: Construct Hard Example Library**
- Hard positives: Top 4 FNs by frequency
- Hard negatives: Top 3 FPs by frequency
- Document: source tile, frequency, failure category

**Step 4: Construct Verbose Text**
- Base: Brief text (legend descriptions)
- Add: Exclusion guidance for each hard negative (why it's NOT a mound)
- Add: Edge case guidance for each hard positive (why it IS a mound)
- Verify: Each hard example image has corresponding text

**Step 5: Construct Brief Text**
- Legend-based descriptions only
- No exclusion or edge case guidance
- Same text used for text-only and text+image conditions

### Outputs

- [ ] `inputs/few-shot-library/hard-positives/` (4 images)
- [ ] `inputs/few-shot-library/hard-negatives/` (3 images)
- [ ] `inputs/few-shot-library/library-manifest.json`
- [ ] `prompts/brief-text.md` (identical for text-only and text+image)
- [ ] `prompts/verbose-text.md` (identical for text-only and text+image)
- [ ] `prompts/text-image-alignment.md` (mapping of hard examples to text)
- [ ] Upload all to OSF before Phase 2

### Decision Point

If <4 distinct FNs or <3 distinct FPs are found:
- Option A: Proceed with smaller hard example set (document)
- Option B: Lower frequency threshold (≥2/5 instead of ≥3/5)
- Document decision and rationale
```

---

## 6. Update Prompts Appendix

### Add Alignment Documentation Section

```markdown
## Text-Image Alignment

### Principle

Verbose text additions are derived from the same failures as hard example images. This ensures text and images reinforce rather than contradict.

### Mapping Table (Template)

| Hard Example | Type | Image File | Text Addition |
|--------------|------|------------|---------------|
| Benchmark (standalone) | Hard negative | `hardneg_01_benchmark.png` | "Do NOT mark: Benchmarks without radiating rays..." |
| Triangulation (standalone) | Hard negative | `hardneg_02_triangulation.png` | "Do NOT mark: Triangulation points without radiating rays..." |
| [FP from training] | Hard negative | `hardneg_03_[type].png` | "[Description of why this is NOT a mound]" |
| Occluded mound | Hard positive | `hardpos_01_occluded.png` | "Mound symbols may be partially obscured..." |
| [FN from training] | Hard positive | `hardpos_02_[type].png` | "[Description of why this IS a mound]" |

*Table populated during Phase 1 library construction*

### Brief vs Verbose Text Structure

**Brief text** contains:
- Task framing
- Canonical symbol descriptions (from legend)
- Output format

**Verbose text** contains:
- Everything in brief text
- Exclusion guidance (one paragraph per hard negative type)
- Edge case guidance (one paragraph per hard positive type)

### Consistency Across Modalities

| Modality | Text Version | Images |
|----------|--------------|--------|
| Image-only | Minimal (task + output format) | Yes |
| Brief-text | Brief | No |
| Brief-text+image | Brief | Yes |
| Verbose-text | Verbose | No |
| Verbose-text+image | Verbose | Yes |

The brief and verbose text files are identical regardless of whether images are included.
```

---

## 7. Verification Checklist

After implementing all changes:

- [ ] Section 8.4.1: Library construction derives text from image-only failures
- [ ] Section 8.4.1: Alignment requirement explicitly stated
- [ ] H2: Notes that verbose text is derived from image-only baseline
- [ ] H2: Notes text-only is primarily academic baseline
- [ ] H7: Clarifies exclusion text describes same failures as hard negative images
- [ ] H7: Notes alignment between conditions B/D text and conditions C/D images
- [ ] Section 1 or 5: Clarifies role of text-only conditions
- [ ] Execution plan: Phase 1 includes verbose text construction
- [ ] Prompts appendix: Includes alignment documentation section
- [ ] No references to independent text-only baseline runs for text development

---

*Document version: 1.0*
*Created: 2026-01-03*
