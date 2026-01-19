# Preregistration Appendix: Prompt Documentation

**Companion document to**: `preregistration.md`
**Purpose**: Complete documentation of all system instructions and configuration files
**Status**: Ready for Registration

---

## Overview

This appendix contains the complete text of all prompts used in the study. Prompts are organised into:

1. **System Instructions** — The text instructions provided to the Vision Language Model (VLM)
2. **Configuration Files** — JavaScript Object Notation (JSON) files specifying example images, labels, and parameters

All files are stored in the `prompts/` directory of the project repository.

### Design Summary

The prompt architecture reflects the sequential hypothesis design:

- **M/E Factor** (5 levels): Controls modality and text elaboration
  - Image-only, Brief-text, Brief-text+image, Verbose-text, Verbose-text+image
- **H5 Factor** (3 levels): Controls negative text treatment (given negatives are present)
  - Minimal, Terse, Verbose

This yields:

- **11 detection instruction files**: 3 image-using M/E levels × 3 H5 variants (base=Minimal, `_terse`, `_verbose`) + 2 text-only M/E levels × 1 variant (H5=Minimal only)
- **2 two-stage pipeline instruction files**: propose_brief.md, verify_brief.md
- **Configuration files**: See Section 2.2 for breakdown

**Note on text-only modalities**: Brief-text and Verbose-text cannot use H5=Terse or H5=Verbose since they have no example images for hard negatives. Therefore, text-only modalities are tested at H5=Minimal only and do not have `_terse` or `_verbose` instruction file variants.

**Note on H5 design change**: H5 no longer tests "whether negatives help" (that is answered by H8 contrast C3). H5 now tests the optimal level of text support for negative examples, given that negatives are always present. All H5 conditions use Scale-8 library composition (17 examples).

### Factor Separation

The design maintains separation between M/E levels (modality + elaboration, tested in H1) and H5 (negative text treatment):

| Factor | Controls | Content |
| ------ | -------- | ------- |
| M/E level (H1) | Detail level for **positives** (canonical symbols + HP edge cases) | Minimal = task only; Brief = terse descriptions + terse HP mention; Verbose = detailed descriptions + detailed HP guidance |
| H5 (Negative text) | Elaboration level for **negative** guidance | Minimal = "Negative" label only; Terse = brief "do not detect" instructions; Verbose = detailed exclusion explanations |

**Brief vs Verbose distinction** (M/E): Both brief and verbose include hard positive (HP) edge case guidance — the difference is detail level, not content coverage. Brief mentions edge case types tersely ("symbols may be partially occluded"); verbose provides detailed guidance on occlusion types, degradation patterns, clustering, and variants.

**H5 level distinction**: H5 tests how much text guidance is needed for negatives. Minimal provides only "Negative" labels (images speak for themselves). Terse adds concise exclusion instructions. Verbose provides full explanations of why each confusable symbol is not a mound.

### Library Composition by Condition

The example library composition differs between H5 conditions (which test negative text treatment) and H8 conditions (which test library composition and scaling).

#### H5 Conditions (Negative Text Treatment)

H5 tests text elaboration for negatives while holding library composition constant at Scale-8:

| H5 Level | Canon+ | Canon- | HP | HN | Null | Total | Text Treatment |
|----------|--------|--------|----|----|------|-------|----------------|
| Minimal | 4 | 2 | 4 | 4 | 3 | **17** | "Negative" label only |
| Terse | 4 | 2 | 4 | 4 | 3 | **17** | Brief exclusion guidance |
| Verbose | 4 | 2 | 4 | 4 | 3 | **17** | Detailed exclusion explanations |

**Note**: All H5 conditions use identical library composition (Scale-8). The only difference is the instruction file text treatment for negatives.

#### H8 Conditions (Library Composition and Scaling)

H8 tests two questions through a sequential design: (1) What is the marginal value of each library component? (2) What is the optimal library size?

| Condition | Canon+ | Canon- | HP | HN | Null | Total | Hard | Primary Purpose |
|-----------|--------|--------|----|----|------|-------|------|-----------------|
| Pure Positive Canon | 4 | 0 | 0 | 0 | 3 | **7** | 0 | Minimal baseline |
| Canonical | 4 | 2 | 0 | 0 | 3 | **9** | 0 | +Canon- effect (C1) |
| +HP | 4 | 2 | 4 | 0 | 3 | **13** | 4 | +HP effect (C2) |
| Scale-4 | 4 | 2 | 2 | 2 | 3 | **13** | 4 | 1:1 floor |
| Scale-8 | 4 | 2 | 4 | 4 | 3 | **17** | 8 | +HN effect (C3) / scaling baseline |
| Scale-16 | 4 | 2 | 8 | 8 | 3 | **25** | 16 | Scaling mid (S2) |
| Scale-32 | 4 | 2 | 16 | 16 | 3 | **41** | 32 | Scaling ceiling (S3) |

**Sequential addition contrasts**: C1 tests Canon- effect, C2 tests HP effect, C3 tests HN effect.

**Scaling contrasts**: S1 (Scale-4 → Scale-8), S2 (Scale-8 → Scale-16), S3 (Scale-16 → Scale-32) test diminishing returns.

**Key distinction from H5**: H8 tests library *composition and scaling* (which components and how many). H5 tests *text treatment* for negatives (how much explanation is needed).

---

## Pre-Holdout Finalisation

The following elements will be finalised before holdout evaluation:

### Empirically-Determined Content

#### Hard Negative Images (All H5 and H8 conditions with HN)

Configuration files with hard negative images currently use placeholder paths for empirically-derived examples. These will be populated via the procedure in preregistration.md Section 8.4.2:

1. Run image-only baseline on 20 training tiles (5 passes)
2. Identify False Positives (≥3/5 passes) → select top M as hard negatives
3. Document selected images with filenames, source tiles, and selection rationale

**Legend-derived hard negatives** (can be specified now):

- Standalone benchmark (no rays)
- Standalone triangulation point (no rays)

**Empirically-derived hard negatives** (TBD after Phase 1):

- Additional confusable symbols identified from FP analysis

#### Hard Positive Images (H5 and H8 conditions with HP)

Hard positive (HP) images represent edge cases: genuine mound symbols that may be missed due to occlusion, degradation, or atypical appearance.

HP images will be derived from False Negatives in Phase 1 baseline analysis (≥3/10 passes missed).

**HP inclusion by condition:**

| Condition Type | HP Included | Notes |
|----------------|-------------|-------|
| All H5 conditions (Minimal, Terse, Verbose) | Yes (4) | H5 uses Scale-8; HP constant |
| H8 Pure Positive Canon | No | Tests minimal baseline (Canon+ and null only) |
| H8 Canonical | No | Tests +Canon- effect |
| H8 +HP and Scale-4 through Scale-32 | Yes (varies) | HP count varies with library size |
| H9 diversity conditions C and E | Yes (varied) | Image diversity uses HP pool |

**Configs affected:**

- All H5 configs (`*_minimal.json`, `*_terse.json`, `*_verbose.json`)
- H8 library configs (`library_*.json`) where HP > 0
- `propose_brief.json` and `verify_brief.json` (H2)
- H9 diversity conditions C and E (varied images from HP pool)

### H9 Text Diversity Prompts

The 5 semantically equivalent prompt variants (V1–V5) will be constructed after the optimal base configuration is determined from the main factorial.

**Construction procedure:**

1. Identify winning configuration (M/E level, H5 level, temperature)
2. Use the corresponding instruction file as structural base
3. Create V1–V5 using Level 3 variation (content diversity, fixed structure):
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

### Finalisation Documentation

Before any holdout evaluation, the following will be uploaded to the connected Open Science Framework (OSF) project:

- Final image filenames for all hard examples
- Selection rationale (frequency counts from training evaluation)
- Complete H9 prompt variants (V1–V5)
- Exact ordering for each condition
- Random seeds used

---

## Part 1: System Instructions

### 1.0 Instruction File Summary

| Filename | M/E Level | H5 Level | Role |
|----------|-----------|----------|------|
| `detect_image-only.md` | Image-only | Minimal | H1 baseline / H5=Minimal |
| `detect_image-only_terse.md` | Image-only | Terse | H5=Terse |
| `detect_image-only_verbose.md` | Image-only | Verbose | H5=Verbose |
| `detect_brief-text.md` | Brief-text | Minimal | H1 text-only |
| `detect_brief-text-image.md` | Brief-text+image | Minimal | H1 baseline / H5=Minimal |
| `detect_brief-text-image_terse.md` | Brief-text+image | Terse | H5=Terse |
| `detect_brief-text-image_verbose.md` | Brief-text+image | Verbose | H5=Verbose |
| `detect_verbose-text.md` | Verbose-text | Minimal | H1 elaboration |
| `detect_verbose-text-image.md` | Verbose-text+image | Minimal | H1 elaboration / H5=Minimal |
| `detect_verbose-text-image_terse.md` | Verbose-text+image | Terse | H5=Terse |
| `detect_verbose-text-image_verbose.md` | Verbose-text+image | Verbose | H5=Verbose |

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

#### 1.1.1 detect_image-only.md

**Purpose**: Baseline image-only detection with minimal text instruction.
**Used by**: M/E = Image-only; H5 = Minimal

```markdown
# Mound Detection

Detect all burial mound symbols in this map tile. Target symbols have a "sunburst" pattern: a central shape with short rays (hachures) radiating OUTWARD.

If reference examples are provided, compare uncertain cases against them.

## Output Format

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

#### 1.1.2 detect_image-only_terse.md

**Purpose**: Image-only detection with brief exclusion guidance for hard negatives.
**Used by**: M/E = Image-only; H5 = Terse

```markdown
# Mound Detection

Detect all burial mound symbols in this map tile. Target symbols have a "sunburst" pattern: a central shape with short rays (hachures) radiating OUTWARD.

If reference examples are provided, compare uncertain cases against them.

## Exclusion Guidance

Rays are essential: shapes without visible radiating rays are not mounds.

**Do NOT mark:**
- Standalone triangulation points (black triangle, no rays)
- Standalone benchmarks (black square/circle, no rays)
- Spot heights (dot with elevation number, no rays)
- Quarry/pit symbols (marks pointing INWARD, not outward)
- Infrastructure markers (dots on roads, bridges, rivers)

## Output Format

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

#### 1.1.3 detect_image-only_verbose.md

**Purpose**: Image-only detection with detailed exclusion guidance for hard negatives.
**Used by**: M/E = Image-only; H5 = Verbose

```markdown
# Mound Detection

Detect all burial mound symbols in this map tile. Target symbols have a "sunburst" pattern: a central shape with short rays (hachures) radiating OUTWARD.

If reference examples are provided, compare uncertain cases against them.

## Exclusion Criteria

The following symbols appear frequently on Soviet maps and are commonly confused with mound symbols. Study any negative reference images carefully.

### Spot Heights
- **Visual**: Simple dot (black or brown) with elevation number (e.g., "185", "247")
- **Key difference**: No hollow shape, no radiating rays—just a dot with a number
- **Test**: Ignore the number. Is there a hollow shape with rays? No → exclude.

### Standalone Triangulation Points
- **Visual**: Black triangle with central dot, but NO surrounding rays
- **Key difference**: No radiating rays extending outward from the triangle
- **Test**: Rays around the triangle? No → survey marker only, exclude. Yes → triangulation ON mound, include.

### Standalone Benchmarks
- **Visual**: Black square or circle with central dot, NO surrounding rays
- **Key difference**: No radiating rays extending outward from the shape
- **Test**: Rays around the shape? No → benchmark only, exclude. Yes → benchmark ON mound, include.

### Quarry and Pit Symbols
- **Visual**: Circular shapes with short marks pointing INWARD toward centre
- **Key difference**: Ray direction is reversed (inward = excavation, outward = elevation)
- **Test**: Which way do marks point? Inward → quarry/pit, exclude. Outward → mound, include.

### Contour Line Artefacts
- **Visual**: Closed contour lines on hilltops forming roughly circular patterns
- **Key difference**: Smooth, continuous curves with no discrete rays
- **Test**: Discrete rays radiating outward? No → contours, exclude. Yes → mound, include.

### Infrastructure Markers
- **Visual**: Dots positioned on roads, bridges, rivers, or canals
- **Key difference**: Located on linear features; no rays
- **Test**: Simple dot on a linear feature? → infrastructure, exclude.

## Output Format

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

### 1.2 Brief-Text Instructions

#### 1.2.1 detect_brief-text.md

**Purpose**: Text-only detection with concise symbol descriptions.
**Used by**: M/E = Brief-text; H5 = Minimal (no images in this condition)

```markdown
# Mound Detection

Detect all burial mound symbols in this Soviet topographic map tile.

## Target Symbols

All mound symbols share one diagnostic feature: short **rays (hachures) radiating OUTWARD** from a central shape, forming a "sunburst" or "gear" pattern. This indicates elevated terrain.

**Subtypes to detect:**

- **Burial mound (kurgan)**: Orange-brown hollow circle with rays. ~10-20 pixels diameter. Often accompanied by elevation numbers or "кург." label.
- **Settlement mound**: Orange-brown, larger and often oval/irregular. More rays (8-15).
- **Triangulation point on mound**: Black triangle with central dot, surrounded by black rays.
- **Benchmark on mound**: Black square with central dot, surrounded by black rays.

The **rays pointing outward** are essential. Symbols without visible rays are not mounds.

## Guidelines

1. Provide individual bounding boxes for each symbol, even in clusters.
2. Symbols may be partially occluded by roads, contours, or text. Include if rays are partially visible.
3. If reference examples are provided, compare uncertain cases against them.

## Output Format

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

### 1.3 Brief-Text+Image Instructions

#### 1.3.1 detect_brief-text-image.md

**Purpose**: Combined brief text and image prompt with reference examples.
**Used by**: M/E = Brief-text+image; H5 = Minimal
**Note**: This file is identical to detect_brief-text.md (text-modality consistency).

```markdown
# Mound Detection

Detect all burial mound symbols in this Soviet topographic map tile.

## Target Symbols

All mound symbols share one diagnostic feature: short **rays (hachures) radiating OUTWARD** from a central shape, forming a "sunburst" or "gear" pattern. This indicates elevated terrain.

**Subtypes to detect:**

- **Burial mound (kurgan)**: Orange-brown hollow circle with rays. ~10-20 pixels diameter. Often accompanied by elevation numbers or "кург." label.
- **Settlement mound**: Orange-brown, larger and often oval/irregular. More rays (8-15).
- **Triangulation point on mound**: Black triangle with central dot, surrounded by black rays.
- **Benchmark on mound**: Black square with central dot, surrounded by black rays.

The **rays pointing outward** are essential. Symbols without visible rays are not mounds.

## Guidelines

1. Provide individual bounding boxes for each symbol, even in clusters.
2. Symbols may be partially occluded by roads, contours, or text. Include if rays are partially visible.
3. If reference examples are provided, compare uncertain cases against them.

## Output Format

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

#### 1.3.2 detect_brief-text-image_terse.md

**Purpose**: Brief text+image prompt with brief exclusion guidance for hard negatives.
**Used by**: M/E = Brief-text+image; H5 = Terse

```markdown
# Mound Detection

Detect all burial mound symbols in this Soviet topographic map tile.

## Target Symbols

All mound symbols share one diagnostic feature: short **rays (hachures) radiating OUTWARD** from a central shape, forming a "sunburst" or "gear" pattern. This indicates elevated terrain.

**Subtypes to detect:**

- **Burial mound (kurgan)**: Orange-brown hollow circle with rays. ~10-20 pixels diameter. Often accompanied by elevation numbers or "кург." label.
- **Settlement mound**: Orange-brown, larger and often oval/irregular. More rays (8-15).
- **Triangulation point on mound**: Black triangle with central dot, surrounded by black rays.
- **Benchmark on mound**: Black square with central dot, surrounded by black rays.

The **rays pointing outward** are essential. Symbols without visible rays are not mounds.

## Guidelines

1. Provide individual bounding boxes for each symbol, even in clusters.
2. Symbols may be partially occluded by roads, contours, or text. Include if rays are partially visible.
3. If reference examples are provided, compare uncertain cases against them.

## Exclusion Guidance

Rays are essential: shapes without visible radiating rays are not mounds.

**Do NOT mark:**
- Standalone triangulation points (black triangle, no rays)
- Standalone benchmarks (black square/circle, no rays)
- Spot heights (dot with elevation number, no rays)
- Quarry/pit symbols (marks pointing INWARD, not outward)
- Infrastructure markers (dots on roads, bridges, rivers)

## Output Format

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

#### 1.3.3 detect_brief-text-image_verbose.md

**Purpose**: Brief text+image prompt with detailed exclusion guidance for hard negatives.
**Used by**: M/E = Brief-text+image; H5 = Verbose

```markdown
# Mound Detection

Detect all burial mound symbols in this Soviet topographic map tile.

## Target Symbols

All mound symbols share one diagnostic feature: short **rays (hachures) radiating OUTWARD** from a central shape, forming a "sunburst" or "gear" pattern. This indicates elevated terrain.

**Subtypes to detect:**

- **Burial mound (kurgan)**: Orange-brown hollow circle with rays. ~10-20 pixels diameter. Often accompanied by elevation numbers or "кург." label.
- **Settlement mound**: Orange-brown, larger and often oval/irregular. More rays (8-15).
- **Triangulation point on mound**: Black triangle with central dot, surrounded by black rays.
- **Benchmark on mound**: Black square with central dot, surrounded by black rays.

The **rays pointing outward** are essential. Symbols without visible rays are not mounds.

## Guidelines

1. Provide individual bounding boxes for each symbol, even in clusters.
2. Symbols may be partially occluded by roads, contours, or text. Include if rays are partially visible.
3. If reference examples are provided, compare uncertain cases against them.

## Exclusion Criteria

The following symbols appear frequently on Soviet maps and are commonly confused with mound symbols. Study any negative reference images carefully.

### Spot Heights
- **Visual**: Simple dot (black or brown) with elevation number (e.g., "185", "247")
- **Key difference**: No hollow shape, no radiating rays—just a dot with a number
- **Test**: Ignore the number. Is there a hollow shape with rays? No → exclude.

### Standalone Triangulation Points
- **Visual**: Black triangle with central dot, but NO surrounding rays
- **Key difference**: No radiating rays extending outward from the triangle
- **Test**: Rays around the triangle? No → survey marker only, exclude. Yes → triangulation ON mound, include.

### Standalone Benchmarks
- **Visual**: Black square or circle with central dot, NO surrounding rays
- **Key difference**: No radiating rays extending outward from the shape
- **Test**: Rays around the shape? No → benchmark only, exclude. Yes → benchmark ON mound, include.

### Quarry and Pit Symbols
- **Visual**: Circular shapes with short marks pointing INWARD toward centre
- **Key difference**: Ray direction is reversed (inward = excavation, outward = elevation)
- **Test**: Which way do marks point? Inward → quarry/pit, exclude. Outward → mound, include.

### Contour Line Artefacts
- **Visual**: Closed contour lines on hilltops forming roughly circular patterns
- **Key difference**: Smooth, continuous curves with no discrete rays
- **Test**: Discrete rays radiating outward? No → contours, exclude. Yes → mound, include.

### Infrastructure Markers
- **Visual**: Dots positioned on roads, bridges, rivers, or canals
- **Key difference**: Located on linear features; no rays
- **Test**: Simple dot on a linear feature? → infrastructure, exclude.

## Output Format

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

### 1.4 Verbose-Text Instructions

#### 1.4.1 detect_verbose-text.md

**Purpose**: Extended text-only prompt with comprehensive symbol descriptions and decision procedures.
**Used by**: M/E = Verbose-text; H5 = Minimal (no images in text-only conditions)
**Note**: This file is identical to detect_verbose-text-image.md (text-modality consistency).

```markdown
# Mound Detection

Detect all burial mound symbols in this Soviet topographic map tile.

This is a Soviet 1:50,000 military topographic map from the Cold War era. Archaeological mounds were marked as navigation landmarks using standardised symbology.

## Core Diagnostic

All mound symbols share one essential feature: **short rays (hachures) radiating OUTWARD** from a central shape. This "sunburst" or "gear" pattern indicates elevated terrain, distinguishing mounds from excavations (which have inward-pointing marks).

The rays are the primary diagnostic. Any symbol with outward-radiating rays is a mound candidate, regardless of central shape.

## Target Symbols

### Burial Mound (Kurgan)
- **Visual**: Orange-brown hollow circle with 6-8 short rays radiating outward
- **Size**: ~10-20 pixels diameter in a 512×512 tile
- **Context**: Often accompanied by an elevation number (e.g., "3", "10") or the Cyrillic abbreviation "кург."
- **Grouping**: May appear individually or in clusters (necropoleis)

### Settlement Mound (Tell)
- **Visual**: Orange-brown, larger than burial mounds, often oval or irregular rather than circular
- **Rays**: More numerous (typically 8-15) due to larger perimeter
- **Size**: Larger than burial mounds, may be 20-40+ pixels

### Triangulation Point on Mound
- **Visual**: Black hollow triangle with central dot, surrounded by black radiating rays
- **Interpretation**: Soviet surveyors placed triangulation markers on existing mounds for elevation and sight lines
- **Key distinction**: Must have rays around the triangle. Triangle alone without rays is NOT a mound.

### Benchmark on Mound
- **Visual**: Black hollow square (or circle with crosshairs) with central dot, surrounded by black radiating rays
- **Interpretation**: Benchmarks placed on mounds for stability
- **Key distinction**: Must have rays around the square. Square alone without rays is NOT a mound.

## Decision Procedure

For each candidate feature:

1. **Check for rays**: Are there short marks radiating from a central point? No rays → not a mound.

2. **Check ray direction**: Do rays point OUTWARD (elevated terrain) or INWARD (excavation)? Inward → not a mound.

3. **Assess central shape**: Circle, oval, triangle, or square? This determines subtype classification.

4. **Check colour**: Orange-brown indicates plain mound; black indicates mound with survey marker.

5. **Consider occlusion**: Roads (black/red lines), contour lines (brown), grid lines (blue), or text labels may partially obscure symbols. If some rays are visible and the pattern matches, include the detection.

6. **Consider degradation**: Map scanning may have faded or distorted symbols. Faint or slightly asymmetrical ray patterns still qualify if the overall sunburst structure is discernible.

## Handling Edge Cases

### Partially Occluded Symbols
Linear features frequently cross mound symbols:
- Roads and tracks (black or red lines)
- Contour lines (brown, may merge with orange-brown symbols)
- Coordinate grid lines (blue)
- Text labels and elevation numbers

If you can identify rays extending outward from a central point, even partially, mark the detection.

### Clustered Mounds
Mounds often appear in groups (cemetery fields). Each distinct sunburst centre is a separate mound. Provide individual bounding boxes even if symbols touch or overlap. Do not merge adjacent mounds into a single box.

### Faded or Degraded Symbols
Scanning artefacts may cause:
- Incomplete ray patterns (some rays faint or missing)
- Colour bleeding or fading
- Slight geometric distortion

Look for the characteristic sunburst structure even if imperfect.

## Reference Examples

If reference examples are provided, compare uncertain cases against them. Positive examples demonstrate the target symbols; negative examples show features that are NOT mounds.

## Output Format

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

### 1.5 Verbose-Text+Image Instructions

#### 1.5.1 detect_verbose-text-image.md

**Purpose**: Extended text+image prompt with decision procedures and edge case guidance.
**Used by**: M/E = Verbose-text+image; H5 = Minimal
**Note**: This file is identical to detect_verbose-text.md (text-modality consistency).

```markdown
# Mound Detection

Detect all burial mound symbols in this Soviet topographic map tile.

This is a Soviet 1:50,000 military topographic map from the Cold War era. Archaeological mounds were marked as navigation landmarks using standardised symbology.

## Core Diagnostic

All mound symbols share one essential feature: **short rays (hachures) radiating OUTWARD** from a central shape. This "sunburst" or "gear" pattern indicates elevated terrain, distinguishing mounds from excavations (which have inward-pointing marks).

The rays are the primary diagnostic. Any symbol with outward-radiating rays is a mound candidate, regardless of central shape.

## Target Symbols

### Burial Mound (Kurgan)
- **Visual**: Orange-brown hollow circle with 6-8 short rays radiating outward
- **Size**: ~10-20 pixels diameter in a 512×512 tile
- **Context**: Often accompanied by an elevation number (e.g., "3", "10") or the Cyrillic abbreviation "кург."
- **Grouping**: May appear individually or in clusters (necropoleis)

### Settlement Mound (Tell)
- **Visual**: Orange-brown, larger than burial mounds, often oval or irregular rather than circular
- **Rays**: More numerous (typically 8-15) due to larger perimeter
- **Size**: Larger than burial mounds, may be 20-40+ pixels

### Triangulation Point on Mound
- **Visual**: Black hollow triangle with central dot, surrounded by black radiating rays
- **Interpretation**: Soviet surveyors placed triangulation markers on existing mounds for elevation and sight lines
- **Key distinction**: Must have rays around the triangle. Triangle alone without rays is NOT a mound.

### Benchmark on Mound
- **Visual**: Black hollow square (or circle with crosshairs) with central dot, surrounded by black radiating rays
- **Interpretation**: Benchmarks placed on mounds for stability
- **Key distinction**: Must have rays around the square. Square alone without rays is NOT a mound.

## Decision Procedure

For each candidate feature:

1. **Check for rays**: Are there short marks radiating from a central point? No rays → not a mound.

2. **Check ray direction**: Do rays point OUTWARD (elevated terrain) or INWARD (excavation)? Inward → not a mound.

3. **Assess central shape**: Circle, oval, triangle, or square? This determines subtype classification.

4. **Check colour**: Orange-brown indicates plain mound; black indicates mound with survey marker.

5. **Consider occlusion**: Roads (black/red lines), contour lines (brown), grid lines (blue), or text labels may partially obscure symbols. If some rays are visible and the pattern matches, include the detection.

6. **Consider degradation**: Map scanning may have faded or distorted symbols. Faint or slightly asymmetrical ray patterns still qualify if the overall sunburst structure is discernible.

## Handling Edge Cases

### Partially Occluded Symbols
Linear features frequently cross mound symbols:
- Roads and tracks (black or red lines)
- Contour lines (brown, may merge with orange-brown symbols)
- Coordinate grid lines (blue)
- Text labels and elevation numbers

If you can identify rays extending outward from a central point, even partially, mark the detection.

### Clustered Mounds
Mounds often appear in groups (cemetery fields). Each distinct sunburst centre is a separate mound. Provide individual bounding boxes even if symbols touch or overlap. Do not merge adjacent mounds into a single box.

### Faded or Degraded Symbols
Scanning artefacts may cause:
- Incomplete ray patterns (some rays faint or missing)
- Colour bleeding or fading
- Slight geometric distortion

Look for the characteristic sunburst structure even if imperfect.

## Reference Examples

If reference examples are provided, compare uncertain cases against them. Positive examples demonstrate the target symbols; negative examples show features that are NOT mounds.

## Output Format

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

#### 1.5.2 detect_verbose-text-image_terse.md

**Purpose**: Extended text+image prompt with edge case guidance AND brief exclusion criteria.
**Used by**: M/E = Verbose-text+image; H5 = Terse

```markdown
# Mound Detection

Detect all burial mound symbols in this Soviet topographic map tile.

This is a Soviet 1:50,000 military topographic map from the Cold War era. Archaeological mounds were marked as navigation landmarks using standardised symbology.

## Core Diagnostic

All mound symbols share one essential feature: **short rays (hachures) radiating OUTWARD** from a central shape. This "sunburst" or "gear" pattern indicates elevated terrain, distinguishing mounds from excavations (which have inward-pointing marks).

The rays are the primary diagnostic. Any symbol with outward-radiating rays is a mound candidate, regardless of central shape.

## Target Symbols

### Burial Mound (Kurgan)
- **Visual**: Orange-brown hollow circle with 6-8 short rays radiating outward
- **Size**: ~10-20 pixels diameter in a 512×512 tile
- **Context**: Often accompanied by an elevation number (e.g., "3", "10") or the Cyrillic abbreviation "кург."
- **Grouping**: May appear individually or in clusters (necropoleis)

### Settlement Mound (Tell)
- **Visual**: Orange-brown, larger than burial mounds, often oval or irregular rather than circular
- **Rays**: More numerous (typically 8-15) due to larger perimeter
- **Size**: Larger than burial mounds, may be 20-40+ pixels

### Triangulation Point on Mound
- **Visual**: Black hollow triangle with central dot, surrounded by black radiating rays
- **Interpretation**: Soviet surveyors placed triangulation markers on existing mounds for elevation and sight lines
- **Key distinction**: Must have rays around the triangle. Triangle alone without rays is NOT a mound.

### Benchmark on Mound
- **Visual**: Black hollow square (or circle with crosshairs) with central dot, surrounded by black radiating rays
- **Interpretation**: Benchmarks placed on mounds for stability
- **Key distinction**: Must have rays around the square. Square alone without rays is NOT a mound.

## Decision Procedure

For each candidate feature:

1. **Check for rays**: Are there short marks radiating from a central point? No rays → not a mound.

2. **Check ray direction**: Do rays point OUTWARD (elevated terrain) or INWARD (excavation)? Inward → not a mound.

3. **Assess central shape**: Circle, oval, triangle, or square? This determines subtype classification.

4. **Check colour**: Orange-brown indicates plain mound; black indicates mound with survey marker.

5. **Consider occlusion**: Roads (black/red lines), contour lines (brown), grid lines (blue), or text labels may partially obscure symbols. If some rays are visible and the pattern matches, include the detection.

6. **Consider degradation**: Map scanning may have faded or distorted symbols. Faint or slightly asymmetrical ray patterns still qualify if the overall sunburst structure is discernible.

## Handling Edge Cases

### Partially Occluded Symbols
Linear features frequently cross mound symbols:
- Roads and tracks (black or red lines)
- Contour lines (brown, may merge with orange-brown symbols)
- Coordinate grid lines (blue)
- Text labels and elevation numbers

If you can identify rays extending outward from a central point, even partially, mark the detection.

### Clustered Mounds
Mounds often appear in groups (cemetery fields). Each distinct sunburst centre is a separate mound. Provide individual bounding boxes even if symbols touch or overlap. Do not merge adjacent mounds into a single box.

### Faded or Degraded Symbols
Scanning artefacts may cause:
- Incomplete ray patterns (some rays faint or missing)
- Colour bleeding or fading
- Slight geometric distortion

Look for the characteristic sunburst structure even if imperfect.

## Reference Examples

If reference examples are provided, compare uncertain cases against them. Positive examples demonstrate the target symbols; negative examples show features that are NOT mounds.

## Exclusion Guidance

Rays are essential: shapes without visible radiating rays are not mounds.

**Do NOT mark:**
- Standalone triangulation points (black triangle, no rays)
- Standalone benchmarks (black square/circle, no rays)
- Spot heights (dot with elevation number, no rays)
- Quarry/pit symbols (marks pointing INWARD, not outward)
- Infrastructure markers (dots on roads, bridges, rivers)

## Output Format

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

#### 1.5.3 detect_verbose-text-image_verbose.md

**Purpose**: Extended text+image prompt with edge case guidance AND detailed exclusion criteria.
**Used by**: M/E = Verbose-text+image; H5 = Verbose

```markdown
# Mound Detection

Detect all burial mound symbols in this Soviet topographic map tile.

This is a Soviet 1:50,000 military topographic map from the Cold War era. Archaeological mounds were marked as navigation landmarks using standardised symbology.

## Core Diagnostic

All mound symbols share one essential feature: **short rays (hachures) radiating OUTWARD** from a central shape. This "sunburst" or "gear" pattern indicates elevated terrain, distinguishing mounds from excavations (which have inward-pointing marks).

The rays are the primary diagnostic. Any symbol with outward-radiating rays is a mound candidate, regardless of central shape.

## Target Symbols

### Burial Mound (Kurgan)
- **Visual**: Orange-brown hollow circle with 6-8 short rays radiating outward
- **Size**: ~10-20 pixels diameter in a 512×512 tile
- **Context**: Often accompanied by an elevation number (e.g., "3", "10") or the Cyrillic abbreviation "кург."
- **Grouping**: May appear individually or in clusters (necropoleis)

### Settlement Mound (Tell)
- **Visual**: Orange-brown, larger than burial mounds, often oval or irregular rather than circular
- **Rays**: More numerous (typically 8-15) due to larger perimeter
- **Size**: Larger than burial mounds, may be 20-40+ pixels

### Triangulation Point on Mound
- **Visual**: Black hollow triangle with central dot, surrounded by black radiating rays
- **Interpretation**: Soviet surveyors placed triangulation markers on existing mounds for elevation and sight lines
- **Key distinction**: Must have rays around the triangle. Triangle alone without rays is NOT a mound.

### Benchmark on Mound
- **Visual**: Black hollow square (or circle with crosshairs) with central dot, surrounded by black radiating rays
- **Interpretation**: Benchmarks placed on mounds for stability
- **Key distinction**: Must have rays around the square. Square alone without rays is NOT a mound.

## Decision Procedure

For each candidate feature:

1. **Check for rays**: Are there short marks radiating from a central point? No rays → not a mound.

2. **Check ray direction**: Do rays point OUTWARD (elevated terrain) or INWARD (excavation)? Inward → not a mound.

3. **Assess central shape**: Circle, oval, triangle, or square? This determines subtype classification.

4. **Check colour**: Orange-brown indicates plain mound; black indicates mound with survey marker.

5. **Consider occlusion**: Roads (black/red lines), contour lines (brown), grid lines (blue), or text labels may partially obscure symbols. If some rays are visible and the pattern matches, include the detection.

6. **Consider degradation**: Map scanning may have faded or distorted symbols. Faint or slightly asymmetrical ray patterns still qualify if the overall sunburst structure is discernible.

## Handling Edge Cases

### Partially Occluded Symbols
Linear features frequently cross mound symbols:
- Roads and tracks (black or red lines)
- Contour lines (brown, may merge with orange-brown symbols)
- Coordinate grid lines (blue)
- Text labels and elevation numbers

If you can identify rays extending outward from a central point, even partially, mark the detection.

### Clustered Mounds
Mounds often appear in groups (cemetery fields). Each distinct sunburst centre is a separate mound. Provide individual bounding boxes even if symbols touch or overlap. Do not merge adjacent mounds into a single box.

### Faded or Degraded Symbols
Scanning artefacts may cause:
- Incomplete ray patterns (some rays faint or missing)
- Colour bleeding or fading
- Slight geometric distortion

Look for the characteristic sunburst structure even if imperfect.

## Reference Examples

If reference examples are provided, compare uncertain cases against them. Positive examples demonstrate the target symbols; negative examples show features that are NOT mounds.

## Exclusion Criteria

The following symbols appear frequently on Soviet maps and are commonly confused with mound symbols. Study any negative reference images carefully.

### Spot Heights
- **Visual**: Simple dot (black or brown) with elevation number (e.g., "185", "247")
- **Key difference**: No hollow shape, no radiating rays—just a dot with a number
- **Test**: Ignore the number. Is there a hollow shape with rays? No → exclude.

### Standalone Triangulation Points
- **Visual**: Black triangle with central dot, but NO surrounding rays
- **Key difference**: No radiating rays extending outward from the triangle
- **Test**: Rays around the triangle? No → survey marker only, exclude. Yes → triangulation ON mound, include.

### Standalone Benchmarks
- **Visual**: Black square or circle with central dot, NO surrounding rays
- **Key difference**: No radiating rays extending outward from the shape
- **Test**: Rays around the shape? No → benchmark only, exclude. Yes → benchmark ON mound, include.

### Quarry and Pit Symbols
- **Visual**: Circular shapes with short marks pointing INWARD toward centre
- **Key difference**: Ray direction is reversed (inward = excavation, outward = elevation)
- **Test**: Which way do marks point? Inward → quarry/pit, exclude. Outward → mound, include.

### Contour Line Artefacts
- **Visual**: Closed contour lines on hilltops forming roughly circular patterns
- **Key difference**: Smooth, continuous curves with no discrete rays
- **Test**: Discrete rays radiating outward? No → contours, exclude. Yes → mound, include.

### Infrastructure Markers
- **Visual**: Dots positioned on roads, bridges, rivers, or canals
- **Key difference**: Located on linear features; no rays
- **Test**: Simple dot on a linear feature? → infrastructure, exclude.

## Output Format

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

### 1.6 Two-Stage Pipeline Prompts (H2)

#### 1.6.1 propose_brief.md

**Purpose**: High-recall proposer stage for two-stage pipeline.
**Used by**: H2 (Stage 1)

~~~markdown
# Two-Stage Detection: Proposer

Detect all candidate burial mound symbols in this Soviet topographic map tile. This is Stage 1 of a two-stage pipeline; a verifier will filter false positives.

## Target Symbols

All mound symbols share one diagnostic feature: short **rays (hachures) radiating OUTWARD** from a central shape, forming a "sunburst" or "gear" pattern. This indicates elevated terrain.

**Subtypes to detect:**

- **Burial mound (kurgan)**: Orange-brown hollow circle with rays. ~10-20 pixels diameter. Often accompanied by elevation numbers or "кург." label.
- **Settlement mound**: Orange-brown, larger and often oval/irregular. More rays (8-15).
- **Triangulation point on mound**: Black triangle with central dot, surrounded by black rays.
- **Benchmark on mound**: Black square with central dot, surrounded by black rays.

The **rays pointing outward** are essential. Symbols without visible rays are not mounds.

## Guidelines

1. Provide individual bounding boxes for each symbol, even in clusters.
2. Symbols may be partially occluded by roads, contours, or text. Include if rays are partially visible.
3. If reference examples are provided, compare uncertain cases against them.

## Output Format

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
~~~

---

#### 1.6.2 verify_brief.md

**Purpose**: Precision-focused verifier stage for two-stage pipeline.
**Used by**: H2 (Stage 2)

~~~markdown
# Two-Stage Detection: Verifier

Classify whether the candidate symbol at the centre of this crop is a burial mound.

## Diagnostic Criteria

Mound symbols have **rays (hachures) radiating OUTWARD** from a central shape ("sunburst" pattern). This indicates elevated terrain.

**Key tests:**

1. Are there rays radiating from a central point? No rays → not a mound.
2. Do rays point OUTWARD (mound) or INWARD (quarry/pit)? Inward → not a mound.
3. Check central shape: circle/oval (plain mound), triangle (triangulation on mound), square (benchmark on mound).
4. Check colour: orange-brown (plain mound) or black (survey marker on mound).

If reference examples are provided, compare the candidate against them.

## Output Format

Return JSON:

{
    "reasoning": "Brief description of visual features observed.",
    "mound_probability": 0.0
}

## Scoring Guide

- **0.9-1.0**: Clear sunburst pattern with outward-radiating rays
- **0.6-0.8**: Likely mound, some ambiguity or occlusion
- **0.3-0.5**: Uncertain, could be mound or similar feature
- **0.0-0.2**: Not a mound (no rays, wrong direction, noise, isolated marker)
~~~

---

### 1.7 Fine-to-Coarse Verification Prompt (H2 Context Expansion)

**Status**: Confirmatory — prompt to be used in H2 fine-to-coarse direction testing.

#### 1.7.1 verify_context-expanded.md

**Purpose**: Focused verification for uncertain detections with expanded spatial context.
**Used by**: H2 fine-to-coarse (Stage 2 re-query for 2/5 or 3/5 consensus cases)

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

**Note**: This prompt will be refined based on Stage 1 results before H2 fine-to-coarse testing.

---

## Part 2: Configuration Files

### 2.1 Configuration Schema

All configuration files follow this JSON schema:

```json
{
    "version": "string — unique identifier",
    "description": "string — human-readable description",
    "hypothesis": "string — which hypothesis/factor levels this tests",
    "model": "string — model identifier (e.g., 'gemini-3-flash')",
    "instruction_file": "string — path to system instruction .md file",
    "temperature": "number — default generation temperature (overridden at runtime for H7)",
    "max_output_tokens": "number — maximum output tokens",
    "examples": [
        {
            "path": "string — path to example image",
            "label": "string — label shown to model",
            "category": "string — 'canonical_positive'/'canonical_negative'/'hard_positive'/'hard_negative'/'null'"
        }
    ],
    "ordering_note": "string — optional, explains example ordering"
}
```

**Gemini thinking level**: All Gemini configurations use `thinking_level: minimal`, calibrated via pilot study (see preregistration.md Section 8.9). The pilot found that minimal thinking achieves equivalent F1 to high at one-third the latency.

---

### 2.2 Configuration File Naming Convention

**Base pattern**: `detect_{modality}[_{h5_level}].json`

Where:

- `{modality}`: image-only, brief-text, brief-text-image, verbose-text, verbose-text-image
- `_{h5_level}`: optional suffix for H5 level (omit for Minimal, `_terse` for Terse, `_verbose` for Verbose)

**H4 ordering variants**: `detect_{modality}_{ordering}[_{h5_level}].json`

Where:

- `{ordering}`: canonical-last, random-order (canonical-first is the default, no suffix needed)

**H8 library configs**: `library_{condition}.json`

Where:

- `{condition}`: pure-positive-canon, canonical, plus-hp, scale-4, scale-8, scale-16, scale-32

**Detection config structure** (H5 runs at optimal M/E only, likely verbose-text-image):

| M/E Level | H5=Minimal | H5=Terse | H5=Verbose |
|-----------|------------|----------|------------|
| Image-only | ✓ (base) | ✓ (`_terse`) | ✓ (`_verbose`) |
| Brief-text | ✓ (base) | — | — |
| Brief-text+image | ✓ (base) | ✓ (`_terse`) | ✓ (`_verbose`) |
| Verbose-text | ✓ (base) | — | — |
| Verbose-text+image | ✓ (base) | ✓ (`_terse`) | ✓ (`_verbose`) |

**H4 ordering variants** (at optimal M/E + optimal H5 only):

| Ordering | Config Suffix |
|----------|---------------|
| Canonical-first | (no suffix) |
| Canonical-last | `_canonical-last` |
| Random | `_random-order` |

**Notes**:

- H5=Minimal uses the base instruction file (no exclusion text) with HN images labelled simply as "Negative"
- H5=Terse uses `_terse` instruction files with brief exclusion guidance
- H5=Verbose uses `_verbose` instruction files with detailed exclusion explanations
- Text-only modalities (brief-text, verbose-text) have only H5=Minimal configs since they cannot use HN images
- H4 ordering is tested at optimal M/E and optimal H5 only (3 conditions vs original 12)

---

### 2.3 Complete Configuration File List

#### Base Detection Configs (11 files)

| Configuration File | M/E Level | H5 Level | Instruction File |
|--------------------|-----------|----------|------------------|
| `detect_image-only.json` | Image-only | Minimal | detect_image-only.md |
| `detect_image-only_terse.json` | Image-only | Terse | detect_image-only_terse.md |
| `detect_image-only_verbose.json` | Image-only | Verbose | detect_image-only_verbose.md |
| `detect_brief-text.json` | Brief-text | Minimal | detect_brief-text.md |
| `detect_brief-text-image.json` | Brief-text+image | Minimal | detect_brief-text-image.md |
| `detect_brief-text-image_terse.json` | Brief-text+image | Terse | detect_brief-text-image_terse.md |
| `detect_brief-text-image_verbose.json` | Brief-text+image | Verbose | detect_brief-text-image_verbose.md |
| `detect_verbose-text.json` | Verbose-text | Minimal | detect_verbose-text.md |
| `detect_verbose-text-image.json` | Verbose-text+image | Minimal | detect_verbose-text-image.md |
| `detect_verbose-text-image_terse.json` | Verbose-text+image | Terse | detect_verbose-text-image_terse.md |
| `detect_verbose-text-image_verbose.json` | Verbose-text+image | Verbose | detect_verbose-text-image_verbose.md |

**Note**: H5=Minimal configs use the base instruction file (no exclusion text) with HN images labelled simply as "Negative". All H5 conditions use Scale-8 library composition (17 examples).

#### H4 Ordering Variant Configs (at optimal M/E only)

H4 ordering is tested at optimal M/E + optimal H5 only (3 conditions total, not 12):

| Configuration File | Ordering | Notes |
|--------------------|----------|-------|
| `detect_{optimal-me}_{optimal-h5}.json` | Canonical-first | Base config (no ordering suffix) |
| `detect_{optimal-me}_canonical-last_{optimal-h5}.json` | Canonical-last | Canonical examples at end |
| `detect_{optimal-me}_random-order_{optimal-h5}.json` | Random | Shuffled with documented seed |

**Example** (if optimal M/E = verbose-text-image, optimal H5 = Terse):

| Configuration File | Ordering |
|--------------------|----------|
| `detect_verbose-text-image_terse.json` | Canonical-first |
| `detect_verbose-text-image_canonical-last_terse.json` | Canonical-last |
| `detect_verbose-text-image_random-order_terse.json` | Random |

#### H8 Library Configs (7 files)

| Configuration File | Composition | Total Examples |
|--------------------|-------------|----------------|
| `library_pure-positive-canon.json` | Canon+ (4) + Null (3) | 7 |
| `library_canonical.json` | + Canon- (2) | 9 |
| `library_plus-hp.json` | + HP (4) | 13 |
| `library_scale-4.json` | HP (2) + HN (2) | 13 |
| `library_scale-8.json` | HP (4) + HN (4) | 17 |
| `library_scale-16.json` | HP (8) + HN (8) | 25 |
| `library_scale-32.json` | HP (16) + HN (16) | 41 |

**Note**: H8 library configs specify example composition only. M/E level and instruction file are determined at runtime based on H1 results.

#### Pipeline Configs (2 files)

| Configuration File | Purpose | Instruction File |
|--------------------|---------|------------------|
| `propose_brief.json` | H2 Stage 1 (Proposer) | propose_brief.md |
| `verify_brief.json` | H2 Stage 2 (Verifier) | verify_brief.md |

#### Pilot Configs (4 files)

| Configuration File | Purpose |
|--------------------|---------|
| `pilot_tilesize.json` | Tile size pilot study (512px selected) |
| `pilot_thinking-minimal.json` | Gemini thinking level calibration |
| `pilot_thinking-low.json` | Gemini thinking level calibration |
| `pilot_thinking-high.json` | Gemini thinking level calibration |

**Note**: Thinking level pilot (2026-01-15) tested minimal, low, and high thinking across 20 calibration tiles. Result: `thinking_level: minimal` selected for all Gemini configs (equivalent F1, lower latency). See preregistration.md Section 8.9.

---

### 2.4 Example Configuration: Verbose-Text-Image, H5=Minimal (Base)

#### detect_verbose-text-image.json

**M/E**: Verbose-text+image | **H5**: Minimal | **H4**: Canonical-first

```json
{
    "version": "detect_verbose-text-image",
    "description": "H1 baseline. M/E=Verbose-text+image, H5=Minimal, canonical-first ordering.",
    "hypothesis": "H1",
    "model": "gemini-3-flash",
    "instruction_file": "detect_verbose-text-image.md",
    "temperature": 1.0,
    "max_output_tokens": 8192,
    "examples": [
        {"path": "neutral/example_01.png", "label": "Positive", "category": "canonical_positive"},
        {"path": "neutral/example_02.png", "label": "Positive", "category": "canonical_positive"},
        {"path": "neutral/example_03.png", "label": "Positive", "category": "canonical_positive"},
        {"path": "neutral/example_04.png", "label": "Positive", "category": "canonical_positive"},
        {"path": "neutral/example_05.png", "label": "Positive", "category": "hard_positive"},
        {"path": "neutral/example_06.png", "label": "Positive", "category": "hard_positive"},
        {"path": "neutral/example_07.png", "label": "Positive", "category": "hard_positive"},
        {"path": "neutral/example_08.png", "label": "Positive", "category": "hard_positive"},
        {"path": "neutral/example_09.png", "label": "Negative", "category": "canonical_negative"},
        {"path": "neutral/example_10.png", "label": "Negative", "category": "canonical_negative"},
        {"path": "neutral/example_11.png", "label": "Negative", "category": "hard_negative"},
        {"path": "neutral/example_12.png", "label": "Negative", "category": "hard_negative"},
        {"path": "neutral/example_13.png", "label": "Negative", "category": "hard_negative"},
        {"path": "neutral/example_14.png", "label": "Negative", "category": "hard_negative"},
        {"path": "neutral/example_15.png", "label": "Negative", "category": "null"},
        {"path": "neutral/example_16.png", "label": "Negative", "category": "null"},
        {"path": "neutral/example_17.png", "label": "Negative", "category": "null"}
    ],
    "ordering_note": "Canonical-first: Canon+ (4), HP (4), Canon- (2), HN (4), null (3). Total: 17 examples (Scale-8).",
    "thinking_level": "minimal"
}
```

**Note on neutral filenames**: Example images use neutral filenames (`example_01.png` etc.) rather than semantic names to avoid biasing the model through filename leakage.

**Note on H5=Minimal**: The base instruction file (`detect_verbose-text-image.md`) has no exclusion text. Hard negatives are included in the library with simple "Negative" labels — the images speak for themselves.

---

### 2.5 Example Configuration: Verbose-Text-Image, H5=Terse

#### detect_verbose-text-image_terse.json

**M/E**: Verbose-text+image | **H5**: Terse

```json
{
    "version": "detect_verbose-text-image_terse",
    "description": "H5-B: Terse exclusion guidance. Brief list of confusable symbols to avoid.",
    "hypothesis": "H5-B",
    "model": "gemini-3-flash",
    "instruction_file": "detect_verbose-text-image_terse.md",
    "temperature": 1.0,
    "max_output_tokens": 8192,
    "examples": [
        {"path": "neutral/example_01.png", "label": "Positive", "category": "canonical_positive"},
        {"path": "neutral/example_02.png", "label": "Positive", "category": "canonical_positive"},
        {"path": "neutral/example_03.png", "label": "Positive", "category": "canonical_positive"},
        {"path": "neutral/example_04.png", "label": "Positive", "category": "canonical_positive"},
        {"path": "neutral/example_05.png", "label": "Positive", "category": "hard_positive"},
        {"path": "neutral/example_06.png", "label": "Positive", "category": "hard_positive"},
        {"path": "neutral/example_07.png", "label": "Positive", "category": "hard_positive"},
        {"path": "neutral/example_08.png", "label": "Positive", "category": "hard_positive"},
        {"path": "neutral/example_09.png", "label": "Negative", "category": "canonical_negative"},
        {"path": "neutral/example_10.png", "label": "Negative", "category": "canonical_negative"},
        {"path": "neutral/example_11.png", "label": "Negative", "category": "hard_negative"},
        {"path": "neutral/example_12.png", "label": "Negative", "category": "hard_negative"},
        {"path": "neutral/example_13.png", "label": "Negative", "category": "hard_negative"},
        {"path": "neutral/example_14.png", "label": "Negative", "category": "hard_negative"},
        {"path": "neutral/example_15.png", "label": "Negative", "category": "null"},
        {"path": "neutral/example_16.png", "label": "Negative", "category": "null"},
        {"path": "neutral/example_17.png", "label": "Negative", "category": "null"}
    ],
    "ordering_note": "Canonical-first: Canon+ (4), HP (4), Canon- (2), HN (4), null (3). Total: 17 examples (Scale-8).",
    "thinking_level": "minimal"
}
```

**Note**: H5=Terse uses `_terse` instruction file with brief exclusion guidance (1-2 sentences: "Do not detect triangulation points, benchmarks, or similar symbols"). Same Scale-8 library as Minimal and Verbose.

---

### 2.6 Example Configuration: Verbose-Text-Image, H5=Verbose

#### detect_verbose-text-image_verbose.json

**M/E**: Verbose-text+image | **H5**: Verbose

```json
{
    "version": "detect_verbose-text-image_verbose",
    "description": "H5-C: Verbose exclusion guidance. Detailed explanations of confusable symbols.",
    "hypothesis": "H5-C",
    "model": "gemini-3-flash",
    "instruction_file": "detect_verbose-text-image_verbose.md",
    "temperature": 1.0,
    "max_output_tokens": 8192,
    "examples": [
        {"path": "neutral/example_01.png", "label": "Positive", "category": "canonical_positive"},
        {"path": "neutral/example_02.png", "label": "Positive", "category": "canonical_positive"},
        {"path": "neutral/example_03.png", "label": "Positive", "category": "canonical_positive"},
        {"path": "neutral/example_04.png", "label": "Positive", "category": "canonical_positive"},
        {"path": "neutral/example_05.png", "label": "Positive", "category": "hard_positive"},
        {"path": "neutral/example_06.png", "label": "Positive", "category": "hard_positive"},
        {"path": "neutral/example_07.png", "label": "Positive", "category": "hard_positive"},
        {"path": "neutral/example_08.png", "label": "Positive", "category": "hard_positive"},
        {"path": "neutral/example_09.png", "label": "Negative", "category": "canonical_negative"},
        {"path": "neutral/example_10.png", "label": "Negative", "category": "canonical_negative"},
        {"path": "neutral/example_11.png", "label": "Negative", "category": "hard_negative"},
        {"path": "neutral/example_12.png", "label": "Negative", "category": "hard_negative"},
        {"path": "neutral/example_13.png", "label": "Negative", "category": "hard_negative"},
        {"path": "neutral/example_14.png", "label": "Negative", "category": "hard_negative"},
        {"path": "neutral/example_15.png", "label": "Negative", "category": "null"},
        {"path": "neutral/example_16.png", "label": "Negative", "category": "null"},
        {"path": "neutral/example_17.png", "label": "Negative", "category": "null"}
    ],
    "ordering_note": "Canonical-first: Canon+ (4), HP (4), Canon- (2), HN (4), null (3). Total: 17 examples (Scale-8).",
    "thinking_level": "minimal"
}
```

**Key difference from H5=Terse**: Same Scale-8 library (17 examples) with detailed exclusion text in `_verbose` instruction file explaining why each confusable symbol is not a mound. Tests whether verbose explanations improve precision over brief guidance.

---

### 2.7 Example Configuration: H4 Canonical-Last Ordering

#### detect_verbose-text-image_canonical-last_{optimal-h5}.json

**M/E**: Optimal from H1 (likely Verbose-text+image) | **H5**: Optimal from H5 | **H4**: Canonical-last

```json
{
    "version": "detect_verbose-text-image_canonical-last",
    "description": "H4-B: Canonical-last ordering at optimal M/E. Tests recency bias.",
    "hypothesis": "H4-B",
    "model": "gemini-3-flash",
    "instruction_file": "detect_verbose-text-image.md",
    "temperature": 1.0,
    "max_output_tokens": 8192,
    "examples": [
        {"path": "neutral/example_15.png", "label": "Negative", "category": "null"},
        {"path": "neutral/example_16.png", "label": "Negative", "category": "null"},
        {"path": "neutral/example_17.png", "label": "Negative", "category": "null"},
        {"path": "neutral/example_11.png", "label": "Negative", "category": "hard_negative"},
        {"path": "neutral/example_12.png", "label": "Negative", "category": "hard_negative"},
        {"path": "neutral/example_13.png", "label": "Negative", "category": "hard_negative"},
        {"path": "neutral/example_14.png", "label": "Negative", "category": "hard_negative"},
        {"path": "neutral/example_09.png", "label": "Negative", "category": "canonical_negative"},
        {"path": "neutral/example_10.png", "label": "Negative", "category": "canonical_negative"},
        {"path": "neutral/example_05.png", "label": "Positive", "category": "hard_positive"},
        {"path": "neutral/example_06.png", "label": "Positive", "category": "hard_positive"},
        {"path": "neutral/example_07.png", "label": "Positive", "category": "hard_positive"},
        {"path": "neutral/example_08.png", "label": "Positive", "category": "hard_positive"},
        {"path": "neutral/example_01.png", "label": "Positive", "category": "canonical_positive"},
        {"path": "neutral/example_02.png", "label": "Positive", "category": "canonical_positive"},
        {"path": "neutral/example_03.png", "label": "Positive", "category": "canonical_positive"},
        {"path": "neutral/example_04.png", "label": "Positive", "category": "canonical_positive"}
    ],
    "ordering_note": "Canonical-last: null (3), HN (4), Canon- (2), HP (4), Canon+ (4). Total: 17 examples (Scale-8).",
    "thinking_level": "minimal"
}
```

**Note**: Canonical-last tests recency bias by placing the most informative examples (canonical positives) in final positions. H4 is now tested at optimal M/E only (3 cells total).

---

### 2.8 Example Configuration: H4 Random Ordering

#### detect_verbose-text-image_random-order_{optimal-h5}.json

**M/E**: Optimal from H1 | **H5**: Optimal from H5 | **H4**: Random

```json
{
    "version": "detect_verbose-text-image_random-order",
    "description": "H4-C: Random ordering at optimal M/E. Tests whether example ordering matters.",
    "hypothesis": "H4-C",
    "model": "gemini-3-flash",
    "instruction_file": "detect_verbose-text-image.md",
    "temperature": 1.0,
    "max_output_tokens": 8192,
    "random_seed": 42,
    "examples": [
        {"path": "neutral/example_14.png", "label": "Negative", "category": "hard_negative"},
        {"path": "neutral/example_03.png", "label": "Positive", "category": "canonical_positive"},
        {"path": "neutral/example_17.png", "label": "Negative", "category": "null"},
        {"path": "neutral/example_08.png", "label": "Positive", "category": "hard_positive"},
        {"path": "neutral/example_11.png", "label": "Negative", "category": "hard_negative"},
        {"path": "neutral/example_01.png", "label": "Positive", "category": "canonical_positive"},
        {"path": "neutral/example_16.png", "label": "Negative", "category": "null"},
        {"path": "neutral/example_06.png", "label": "Positive", "category": "hard_positive"},
        {"path": "neutral/example_09.png", "label": "Negative", "category": "canonical_negative"},
        {"path": "neutral/example_04.png", "label": "Positive", "category": "canonical_positive"},
        {"path": "neutral/example_12.png", "label": "Negative", "category": "hard_negative"},
        {"path": "neutral/example_07.png", "label": "Positive", "category": "hard_positive"},
        {"path": "neutral/example_15.png", "label": "Negative", "category": "null"},
        {"path": "neutral/example_02.png", "label": "Positive", "category": "canonical_positive"},
        {"path": "neutral/example_10.png", "label": "Negative", "category": "canonical_negative"},
        {"path": "neutral/example_13.png", "label": "Negative", "category": "hard_negative"},
        {"path": "neutral/example_05.png", "label": "Positive", "category": "hard_positive"}
    ],
    "ordering_note": "Permutation generated with seed 42. Total: 17 examples (Scale-8: Canon+ 4, HP 4, Canon- 2, HN 4, null 3).",
    "thinking_level": "minimal"
}
```

**Note**: Random ordering controls for position effects. Multiple seeds are tested and results averaged to reduce variance from any particular permutation.

---

### 2.9 Example Configuration: H4 Canonical-Last with Verbose Negatives

#### detect_image-only_canonical-last_verbose.json

**M/E**: Image-only | **H5**: Verbose | **H4**: Canonical-last

```json
{
    "version": "detect_image-only_canonical-last_verbose",
    "description": "H4-B + H5-C: Canonical-last ordering with verbose exclusion guidance.",
    "hypothesis": "H4-B, H5-C",
    "model": "gemini-3-flash",
    "instruction_file": "detect_image-only_verbose.md",
    "temperature": 1.0,
    "max_output_tokens": 8192,
    "examples": [
        {"path": "neutral/example_15.png", "label": "Negative", "category": "null"},
        {"path": "neutral/example_16.png", "label": "Negative", "category": "null"},
        {"path": "neutral/example_17.png", "label": "Negative", "category": "null"},
        {"path": "neutral/example_11.png", "label": "Negative", "category": "hard_negative"},
        {"path": "neutral/example_12.png", "label": "Negative", "category": "hard_negative"},
        {"path": "neutral/example_13.png", "label": "Negative", "category": "hard_negative"},
        {"path": "neutral/example_14.png", "label": "Negative", "category": "hard_negative"},
        {"path": "neutral/example_09.png", "label": "Negative", "category": "canonical_negative"},
        {"path": "neutral/example_10.png", "label": "Negative", "category": "canonical_negative"},
        {"path": "neutral/example_05.png", "label": "Positive", "category": "hard_positive"},
        {"path": "neutral/example_06.png", "label": "Positive", "category": "hard_positive"},
        {"path": "neutral/example_07.png", "label": "Positive", "category": "hard_positive"},
        {"path": "neutral/example_08.png", "label": "Positive", "category": "hard_positive"},
        {"path": "neutral/example_01.png", "label": "Positive", "category": "canonical_positive"},
        {"path": "neutral/example_02.png", "label": "Positive", "category": "canonical_positive"},
        {"path": "neutral/example_03.png", "label": "Positive", "category": "canonical_positive"},
        {"path": "neutral/example_04.png", "label": "Positive", "category": "canonical_positive"}
    ],
    "ordering_note": "Canonical-last: null (3), HN (4), Canon- (2), HP (4), Canon+ (4). Total: 17 examples (Scale-8).",
    "thinking_level": "minimal"
}
```

**Note**: Combined H4 and H5 conditions test whether ordering effects interact with negative text elaboration.

---

### 2.10 Two-Stage Pipeline Configurations (H2)

**Template status**: These configs are templates that will be finalised after earlier phases complete. Temperature will use the H7-optimal value from Phase 2b. Library composition will use the H8-optimal from Phase 2c.

**H2 protocol**: Each of the K=10 runs is independent (one proposer pass → one verifier pass). The verifier returns raw `mound_probability` scores used directly for evaluation — no binary thresholding or voting within the verification step.

#### propose_brief.json

```json
{
    "version": "propose_brief",
    "description": "Two-Stage Proposer (Stage 1). High-recall detection using brief text, use with verify_brief.",
    "hypothesis": "H2",
    "model": "gemini-3-flash",
    "instruction_file": "propose_brief.md",
    "temperature": 1.0,
    "max_output_tokens": 8192,
    "thinking_level": "minimal",
    "_config_notes": {
        "template_status": "This config is a template. Parameters will be finalised after earlier phases complete.",
        "temperature": "Placeholder - will use H7-optimal from Phase 2b (or 1.0 if T=1.0 proves optimal)",
        "library": "Placeholder - will use H8-optimal from Phase 2c (likely Scale-8, Scale-16, or Scale-32)",
        "thinking_level": "Fixed at minimal based on calibration pilot (2026-01-15)",
        "proposer_strategy": "Uses brief-level diagnostic text. Subtypes (burial_mound, settlement_mound, triangulation_mound, benchmark_mound) are for diagnostics; all count as positive detections for F1."
    },
    "examples": [
        {"path": "neutral/example_01.png", "label": "Positive: Burial Mound (Kurgan)", "category": "canonical_positive"},
        {"path": "neutral/example_02.png", "label": "Positive: Settlement Mound", "category": "canonical_positive"},
        {"path": "neutral/example_03.png", "label": "Positive: Triangulation Point ON Mound", "category": "canonical_positive"},
        {"path": "neutral/example_04.png", "label": "Positive: Benchmark ON Mound", "category": "canonical_positive"},
        {"path": "neutral/example_09.png", "label": "Negative: Triangulation Point ALONE (no mound)", "category": "canonical_negative"},
        {"path": "neutral/example_10.png", "label": "Negative: Benchmark ALONE (no mound)", "category": "canonical_negative"},
        {"path": "neutral/example_15.png", "label": "Negative: Empty tile (no mounds)", "category": "null"},
        {"path": "neutral/example_16.png", "label": "Negative: Empty tile (no mounds)", "category": "null"},
        {"path": "neutral/example_17.png", "label": "Negative: Empty tile (no mounds)", "category": "null"}
    ],
    "_library_note": "Current examples are Canonical library (placeholder). Will be updated to H8-optimal composition after Phase 2c."
}
```

---

#### verify_brief.json

```json
{
    "version": "verify_brief",
    "description": "Two-Stage Verifier (Stage 2). Precision-focused verification using brief text.",
    "hypothesis": "H2",
    "model": "gemini-3-flash",
    "instruction_file": "verify_brief.md",
    "temperature": 1.0,
    "max_output_tokens": 8192,
    "thinking_level": "minimal",
    "_config_notes": {
        "template_status": "This config is a template. Parameters will be finalised after earlier phases complete.",
        "temperature": "Placeholder - will use H7-optimal from Phase 2b (or 1.0 if T=1.0 proves optimal)",
        "library": "Placeholder - will use H8-optimal from Phase 2c (likely Scale-8, Scale-16, or Scale-32)",
        "thinking_level": "Fixed at minimal based on calibration pilot (2026-01-15)",
        "usage": "Run with --iterations 1 for H2 testing. Each K=10 run is independent (one proposer pass, one verifier pass). Raw mound_probability scores used for evaluation, no binary thresholding."
    },
    "examples": [
        {"path": "neutral/example_01.png", "label": "Positive: Burial Mound (Kurgan)", "category": "canonical_positive"},
        {"path": "neutral/example_02.png", "label": "Positive: Settlement Mound", "category": "canonical_positive"},
        {"path": "neutral/example_03.png", "label": "Positive: Triangulation Point ON Mound", "category": "canonical_positive"},
        {"path": "neutral/example_04.png", "label": "Positive: Benchmark ON Mound", "category": "canonical_positive"},
        {"path": "neutral/example_09.png", "label": "Negative: Triangulation Point ALONE (no mound)", "category": "canonical_negative"},
        {"path": "neutral/example_10.png", "label": "Negative: Benchmark ALONE (no mound)", "category": "canonical_negative"},
        {"path": "neutral/example_15.png", "label": "Negative: Empty tile (no mounds)", "category": "null"},
        {"path": "neutral/example_16.png", "label": "Negative: Empty tile (no mounds)", "category": "null"},
        {"path": "neutral/example_17.png", "label": "Negative: Empty tile (no mounds)", "category": "null"}
    ],
    "_library_note": "Current examples are Canonical library (placeholder). Will be updated to H8-optimal composition after Phase 2c."
}
```

**Note**: Pipeline configs use Canonical library as placeholder. Will be updated to H8-optimal composition after Phase 2c determines the optimal library.

---

## Part 3: Runtime Parameters

The following parameters are controlled at runtime rather than in configuration files:

| Parameter | Values | Hypothesis | Notes |
|-----------|--------|------------|-------|
| Temperature | 0.0, 0.3, 0.7, 1.0, 1.3 | H7 | Overrides config file default |
| Model | gemini-3-flash, gemini-3-pro, claude-4.5-sonnet, gpt-5.2-thinking | H6, H14 | Overrides config file value |
| Passes | 1, 5, 10, 30 | H3 | Number of detection runs per tile |
| Voting threshold | 1 to N | H3 | Minimum votes for detection acceptance |

**Note**: Temperature escalation trigger (H7): If T=1.3 outperforms T=1.0, additional tests at higher temperatures may be conducted. T=0.3 added based on evidence that low temperatures (0.2-0.3) improve accuracy for visual detection tasks.

---

## Part 4: Legend-Derived vs Empirically-Derived Content

### 4.1 Legend-Derived Hard Negatives (Specified)

The following hard negative examples can be specified from the map legend prior to empirical testing:

| Hard Negative Type | Description | Example Path |
|--------------------|-------------|--------------|
| Standalone benchmark | Black square/circle with dot, NO rays | `hardneg_standalone_benchmark.png` |
| Standalone triangulation | Black triangle with dot, NO rays | `hardneg_standalone_triangulation.png` |

These are visually similar to mound-based survey markers but lack the diagnostic radiating rays.

### 4.2 Empirically-Derived Content (TBD)

The following content will be derived from Phase 1 baseline analysis and finalised before holdout evaluation:

| Content Type | Source | Placeholder |
|--------------|--------|-------------|
| Additional hard negative images | FPs from Phase 1 (≥3/10 runs) | `hardneg_empirical_TBD_*.png` |
| Hard positive images (H9) | FNs from Phase 1 (≥3/5 passes) | `hardpos_empirical_TBD_*.png` |

---

*Document version: 2.17*
*Created: 2026-01-02*
*Updated: 2026-01-20*

**Changelog:**

- v2.17: Config example synchronisation — added `thinking_level: "minimal"` field to all example configs in Sections 2.4-2.9 (matching actual config files); updated description fields in Sections 2.5 and 2.6 to match actual configs exactly ("H5-B: Terse exclusion guidance. Brief list of confusable symbols to avoid." and "H5-C: Verbose exclusion guidance. Detailed explanations of confusable symbols.")
- v2.16: Fixed example numbering inconsistencies — corrected propose_brief.json and verify_brief.json configs to use standard numbering scheme per MANIFEST.md (Canon-: example_09-10, null: example_15-17); corrected symlinks in `inputs/examples/neutral-naming/` to match MANIFEST (removed incorrect 05-09 symlinks, created correct 09-10 and 15-17 symlinks); slots 05-08 (HP) and 11-14 (HN) remain reserved for Phase 1 mining
- v2.15: Major prompt library synchronisation — replaced all 11 detection instruction prompts with actual file content (action-first opening, no recall bias language, conditional reference framing "If reference examples are provided..."); updated two-stage pipeline prompts renamed from `propose_image-only.md`/`verify_image-only.md` to `propose_brief.md`/`verify_brief.md`; updated config examples to match; added text-modality consistency notes (detect_brief-text.md = detect_brief-text-image.md); reordered H5 variant sections consistently (base → terse → verbose)
- v2.14: Three-way consistency check — corrected instruction file count from "10" to "11" in Design Summary (matches preregistration.md and actual file count: 3 image-using × 3 H5 + 2 text-only = 11)
- v2.13: Standardised exclusion guidance templates — updated Section 1.3.2 (brief-text-image_verbose) to use full 6-subsection "Exclusion Criteria (CRITICAL)" format matching actual file; updated Sections 1.3.3 (brief-text-image_terse) and 1.5.3 (verbose-text-image_terse) to use standardised 3-bullet terse template ("Rays are key..." + DO NOT mark list) matching actual files; ensured positive guidance sections are identical across H5 variants within each M/E level
- v2.12: Instruction file content alignment — added missing terse sections (1.1.3 detect_image-only_terse.md, 1.3.3 detect_brief-text-image_terse.md, 1.5.3 detect_verbose-text-image_terse.md) with full content matching actual prompt library files; fixed verbose instruction file titles to match actual files (Section 1.1.2 "with Verbose Exclusion"/"Exclusion Guidance (Detailed)", Section 1.3.2 "with Verbose Exclusion Guidance", Section 1.5.2 "with Verbose Exclusion Guidance")
- v2.11: Consistency fixes — updated schema category values to include all 5 types (canonical_positive, canonical_negative, hard_positive, hard_negative, null); fixed canonical-last ordering in Sections 2.7 and 2.9 to match actual configs (null first, then HN, Canon-, HP, Canon+); fixed random-order permutation in Section 2.8 to match actual seed-42 output; updated H4 example configs to use base instruction files (not _terse which doesn't exist for H4 variants)
- v2.10: Major H5/H8/H4 redesign alignment — H5 now tests text treatment only (Minimal/Terse/Verbose) given negatives are always present; H8 expanded to 7 conditions with sequential addition contrasts (C1-C3) and scaling contrasts (S1-S3); H4 simplified to optimal M/E only (3 cells); instruction file naming changed from `_hardneg` to `_verbose`, added `_terse`, base = Minimal; H7 temperature levels now 5 (added T=0.3); all example configs updated to Scale-8 (17 examples); see h5-h8-redesign-consolidated.md for full rationale
- v2.9: Fixed H8 library composition table — added missing Canonical condition; corrected A-D to use 1:1 HP:HN ratio (2:2, 4:4, 8:8, 16:16) with constant Canon+/Canon- (4/2); added Hard Examples column; corrected totals (13, 17, 25, 41); added key distinction note explaining H8 vs H5
- v2.8: HP clarification and library composition tables — clarified HP (4 examples) included in ALL H5 conditions (not H9-only); added Library Composition by Condition section with H5 vs H8 tables; updated all example configs to show correct counts (H5=None: 11, H5=Images-only/Text+Images: 16); renamed category field from "canonical"/"null" to "canonical_positive"/"canonical_negative"/"hard_positive"/"hard_negative"/"null" for clarity; aligned with preregistration.md v4.4
- v2.7: Synchronised Section 1.5 verbose-text+image prompts with actual instruction files — updated Section 1.5.1 (detect_verbose-text-image.md) to match actual file structure (removed separate "Edge Cases" section; guidance integrated into Decision Procedure); updated Section 1.5.2 (detect_verbose-text-image_hardneg.md) to include full "Exclusion Criteria (CRITICAL)" section with 6 detailed subsections matching actual file
- v2.6: Added missing H5=Images-only configs — 3 new base configs (`_images.json` variants) for image-using modalities; updated config count from 23 to 26; clarified H5=Images-only uses same instruction file as H5=None but includes hard negative images with minimal labels; added example config for H5=Images-only; restructured config table to show H5 levels clearly
- v2.5: Comprehensive alignment with actual prompt library — fixed instruction file count from 10 to 8 (text-only modalities don't have `_hardneg` variants per preregistration); removed sections 1.2.2 and 1.4.2 (non-existent files); updated config naming to match actual files (base/`_hardneg` pattern, H4 ordering suffixes); rewrote Section 2.3 to reflect 23 configs (8 base + 12 H4 variants + 2 pipeline + 1 pilot); updated example configs to use neutral filenames; synced verbose-text section structure with actual file; added JSON code fences to pipeline prompts
- v2.4: Final synchronisation with preregistration.md v4.2 — fixed remaining H7→H5 references in text (construction procedure, verbose text note, config headers); label convention now references H5 correctly
- v2.3: Hypothesis renumbering alignment with preregistration.md v4.0 — H7→H5 (hard negatives now 3 levels), H9→H7 (temperature now 4 levels), H5→H4 (ordering), H3→H2 (two-stage), H6→H9 (diversity exploratory), H8→H6 (transfer), H4→H3 (voting), H10 merged into H2; config count reduced from 16 to 9; text-only tested at T=1.0 only
- v2.2: H2 elaboration clarification — both brief and verbose include HP edge case guidance at different detail levels (brief = terse mention, verbose = detailed guidance); orthogonality is H2 (detail level for positives) vs H7 (presence of negatives); aligned with preregistration.md v3.5 factorial restructure
- v2.1: Final review fixes — corrected config count explanation (20→16 due to text-only constraints); aligned Phase 1 baseline with preregistration (5 passes, ≥3/5 threshold); fixed hard negative labels for Images-only condition (minimal "Negative" labels); added hard positive placeholders to example configs; added H10 verification prompt placeholder (Section 1.7); added H5 canonical-last example config; fixed verifier prompt to use placeholder notation
- v2.0: Major restructure — 10 instruction files (5 M/E × 2 exclusion variants), 16 config files (reflecting text-only constraints); renamed "elaborate" to "verbose"; clarified orthogonal separation between H2 (edge case guidance for FNs) and H7 (exclusion guidance for FPs); added legend-derived hard negatives; flagged empirically-derived content as TBD
- v1.1: Added T=1.3 to temperature values; removed stale H2 reference from H6 construction procedure
- v1.0: Initial documentation
