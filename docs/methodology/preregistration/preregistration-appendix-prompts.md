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

- **10 detection instruction files**: 3 image-using M/E levels × 3 H5 variants (base=Minimal, `_terse`, `_verbose`) + 2 text-only M/E levels × 1 variant (H5=Minimal only)
- **2 two-stage pipeline instruction files**: propose_image-only.md, verify_image-only.md
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
- `propose_image-only.json` and `verify_image-only.json` (H2)
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

---

### 1.1 Image-Only Instructions

#### 1.1.1 detect_image-only.md

**Purpose**: Baseline image-only detection with minimal text instruction.
**Used by**: M/E = Image-only; H5 = Minimal
**H9 note**: If image-only is the optimal base configuration, this template's structure will be used for H9 V1–V5 variants (with varied content per Section 8.3.3).

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

#### 1.1.2 detect_image-only_verbose.md

**Purpose**: Image-only detection with detailed exclusion guidance for hard negatives.
**Used by**: M/E = Image-only; H5 = Verbose

**Note**: This file was previously named `detect_image-only_hardneg.md`. Renamed to reflect H5 level naming.

```markdown
# Mound Detection (Image-Only)

Scan the Target Image. Mark all symbols that look like the Positive examples.

## Exclusion Guidance

The key diagnostic feature is **radiating rays** (hachures; spikes) extending OUTWARD from a central shape.

**DO NOT mark symbols without visible rays**, including:

- Standalone triangulation points (black triangle, NO rays)
- Standalone benchmarks (black square/circle, NO rays)
- Spot heights (simple dots with elevation numbers)
- Bridge/culvert markers (dots on roads/rivers)

Consider occlusion or degradation before excluding — partial rays still indicate a mound.

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
# Detection Prompt: Brief Text

You are an expert analyst of Soviet Topographic Maps and landscape archaeologist. Your goal is to identify burial mound symbols.

## Target Symbols

Create bounding boxes for all instances of the following symbols:

### A. Burial Mound (Kurgan)

- **Visual:** A small, hollow **circle** with short, radiating **rays** (hachures; spikes) extending outward. Resembles a "sunburst", "gear", or "ship's wheel".
- **Colour:** Orange-brown.
- **Context:** Often accompanied by an isolated elevation number (e.g., "3", "10") or the abbreviation **"кург."**

### B. Settlement Mound

- **Visual:** Similar to a burial mound but **larger** and often oval or irregular in shape.
- **Colour:** Orange-brown.

### C. Triangulation Point on a Mound

- **Visual:** A hollow **black triangle** with a central dot, surrounded by radiating rays of a mound.
- **Distinction:** Must have rays.

### D. Benchmark on a Mound

- **Visual:** A hollow **black square** with a central dot, surrounded by radiating rays of a mound.
- **Distinction:** Must have rays.

## Guidelines

- Symbols may be partially obscured by lines or text. Focus on the characteristic "sunburst" shape.
- Each distinct "sunburst" centre represents a separate mound. Provide individual bounding boxes.
- Include borderline cases rather than missing genuine mounds.

## Output Format

Return JSON with normalised coords (0-1000).

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
**H9 note**: If brief-text+image is the optimal base configuration, this template's structure will be used for H9 V1–V5 variants.

```markdown
# Detection Prompt: Brief Text+Image

You are an expert analyst of Soviet Topographic Maps and landscape archaeologist. Your goal is to find symbols that **visually match** the provided Positive examples.

## Reference Examples

You are provided with labelled images:

- **Positive examples** show mound symbols to detect (burial mounds, settlement mounds, and survey markers on mounds)
- **Negative examples** show areas or symbols that are NOT mounds

## Task

Scan the **Target Image** and create bounding boxes for all instances that visually match the Positive reference symbols.

## Guidelines

1. **Visual Match:** Symbols may be rotated, degraded, or intersected by lines. Focus on the "sunburst" shape with short rays (hachures; spikes) extending OUTWARD.

2. **Separate Clusters:** Provide individual boxes for each symbol.

3. **Refer to Examples:** Compare uncertain cases to Positive references.

4. **Default to inclusion:** Include borderline cases rather than missing genuine mounds.

## Output Format

Return JSON with normalised coords (0-1000).

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

#### 1.3.2 detect_brief-text-image_verbose.md

**Purpose**: Brief text+image prompt with detailed exclusion guidance for hard negatives.
**Used by**: M/E = Brief-text+image; H5 = Verbose

**Note**: This file was previously named `detect_brief-text-image_hardneg.md`. Renamed to reflect H5 level naming.

```markdown
# Detection Prompt: Brief Text+Image with Exclusion Guidance

You are an expert analyst of Soviet Topographic Maps and landscape archaeologist. Your goal is to find symbols that **visually match** the provided Positive examples.

## Reference Examples

You are provided with labelled images:

- **Positive examples** show mound symbols to detect (burial mounds, settlement mounds, and survey markers on mounds)
- **Negative examples** show areas or symbols that are NOT mounds

## Task

Scan the **Target Image** and create bounding boxes for all instances that visually match the Positive reference symbols.

## Guidelines

1. **Visual Match:** Symbols may be rotated, degraded, or intersected by lines. Focus on the "sunburst" shape with short rays (hachures; spikes) extending OUTWARD.

2. **Separate Clusters:** Provide individual boxes for each symbol.

3. **Refer to Examples:** Compare uncertain cases to Positive references.

4. **Default to inclusion:** Include borderline cases rather than missing genuine mounds.

## Exclusion Guidance

Rays are key: Shapes without visible radiating rays are not mounds. Consider occlusion or degradation before excluding.

**DO NOT mark:**

- Standalone triangulation points (black triangle, NO rays)
- Standalone benchmarks (black square/circle, NO rays)
- Spot heights, bridge markers, or other simple dots

## Output Format

Return JSON with normalised coords (0-1000).

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

**Note on verbose text content**: Verbose text extends brief text with detailed descriptions and **edge case guidance for hard positives** (symbols that are genuine mounds but may be missed due to occlusion, degradation, or atypical appearance). Verbose text does NOT include exclusion guidance for hard negatives — that is controlled by the H5 level variants (`_terse`, `_verbose`).

#### 1.4.1 detect_verbose-text.md

**Purpose**: Extended text-only prompt with comprehensive symbol descriptions and decision procedures.
**Used by**: M/E = Verbose-text; H5 = Minimal (no images in text-only conditions)
**Word count**: ~800 words (vs ~200 for brief version)

```markdown
# Detection Prompt: Verbose Text

You are an expert analyst of Soviet Topographic Maps from the 1950s-1980s, and a seasoned landscape archaeologist. Your goal is to identify symbols on the Soviet military map that represent burial mounds (kurgans; tumuli), settlement mounds (tells), including composite symbols, positioned across the Bulgarian landscape.

## Background: Soviet Cartographic Conventions

Soviet military topographic maps used standardised symbology across the USSR and Eastern Bloc / Warsaw Pact nations. Archaeological mounds were marked because they served as useful landmarks for navigation and orientation, and they could be militarily useful, e.g., as lookout points or cover. The symbol design emphasises the elevated, roughly circular nature of these features through radiating rays (hachures; spikes).

## Target Symbols

Identify the bounding boxes for all instances of the following symbols:

### A. Burial Mound (Kurgan)

- **Visual:** A small, hollow **circle** with short, radiating **rays** (hachures; spikes) extending outward. Resembles a "sunburst", "gear", or "ship's wheel".
- **Colour:** Orange-brown (same colour as contour lines, indicating relief).
- **Size:** Typically 2-4mm diameter at map scale, which translates to roughly 10-20 pixels in a 512×512 tile.
- **Ray characteristics:** Usually 6-8 rays of approximately equal length, radiating evenly from the central circle.
- **Context:** Often accompanied by an isolated elevation number (e.g., "3", "10") indicating height in metres, or the Cyrillic abbreviation **"кург."** ("kurgan").
- **Landscape position:** Typically located on elevated terrain, ridges, hilltops, or other prominent landscape positions where ancient peoples chose to bury their dead. May also be found in flat, open areas, where large examples dominate the landscape.
- **Grouping:** Mounds may appear in groups (necropoleis), which may contain mounds of different sizes.

### B. Settlement Mound

- **Visual:** Similar to a burial mound but **larger** and often oval or irregular in shape rather than circular. Radiating ticks point outward from the perimeter.
- **Ray characteristics:** Rays appear similar to burial mounds, but sometimes larger, and often more rays are present (often 8-15).
- **Colour:** Orange-brown.
- **Size:** Larger than burial mounds, may be 5-10mm at map scale.
- **Shape:** May be elongated or irregular, reflecting the accumulated debris of ancient settlements.

### C. Triangulation Point on a Mound

- **Visual:** A hollow **black triangle** with a central dot (the geodetic survey marker), surrounded by the characteristic radiating rays of a mound, also in black. Often have 6-12 rays. Size similar to or slightly larger than a typical 'base' burial mound, since large, prominent mounds were often chosen for triangulation points.
- **Interpretation:** Soviet surveyors placed triangulation markers on mounds because they provided elevated, stable positions with good sight lines.
- **Critical distinction:** The symbol MUST have radiating black rays around the triangle.

### D. Benchmark on a Mound

- **Visual:** A hollow **black square** (or circle with crosshairs) with a central dot, surrounded by the characteristic radiating rays of a mound, also in black. Often have 8 rays. Size similar to or slightly larger than a typical 'base' burial mound, since large, prominent mounds were often chosen for benchmarks.
- **Interpretation:** Similar to triangulation points, benchmarks were placed on mounds for stability and visibility.
- **Critical distinction:** The symbol MUST have radiating black rays around the square/circle.

## Detection Criteria

The **radiating rays** (hachures; spikes) are the primary and essential diagnostic feature. All mound symbols, of whatever type, share this characteristic regardless of what (if anything) is superimposed at the centre.

### Ray Pattern Analysis

1. **Direction:** Rays extend OUTWARD from a central point or oval, indicating elevated terrain (like contour hachures for hills).
2. **Count:** Typically 8-15 rays, roughly evenly spaced around the perimeter. Count depends on symbol type (burial mound, settlement mound, burial mound with triangulation point, burial mound with benchmark)
3. **Length:** Approximately equal to or slightly longer than the diameter of the central shape.
4. **Consistency:** Rays should be roughly equal in length and evenly spaced; highly irregular patterns may indicate other features (noting that some areas of the map scanned poorly and may have some distortion)

### Colour Analysis

- **Orange-brown symbol:** Indicates a "plain" burial or settlement mound.
- **Black symbol:** Indicates a burial mound with survey marker (triangulation point or benchmark) placed on top of the mound.
- Each symbol is a single colour, either orange-brown or black.

## Decision Procedure

When uncertain whether a feature is a mound, apply this systematic checklist:

1. **Check for rays:** Are there short rays (hachures; spikes) radiating outward from a central point? No rays = not a mound.

2. **Check ray direction:** Do the rays point OUTWARD (elevation/mound) or INWARD (excavation/quarry)? Burial or settlement mound rays ALWAYS point outwards.

3. **Check central shape:** Is there a circle, oval, triangle, or square at the centre? The central shape helps classify the mound subtype.

4. **Check colour:** Are the symbols orange-brown ("plain" burial or settlement mound with no survey infrastructure) or black (mound with triangulation point or benchmark)?

5. **Consider occlusion:** Roads, contours, rivers, or text may obscure part of the symbol. If some rays, or partial rays, are visible and the overall pattern matches, include the detection.

6. **Consider degradation:** Map scanning or printing may have faded or distorted some symbols. Look for faint or somewhat asymmetrical ray patterns even if not perfectly symmetrical or fully distinct.

7. **When still uncertain:** Err on the side of detection. It is better to include a borderline case than to miss a genuine mound.

## Handling Occlusion

Symbols are frequently intersected by other map features:

- **Roads:** Black or red lines may cross through a mound symbol.
- **Contour lines:** Brown lines at similar colour may partially merge with mound rays.
- **Grid lines:** Blue coordinate grid lines may overlay symbols.
- **Text labels:** Cyrillic place names or elevation numbers may obscure parts of symbols.

In all cases, focus on identifying the characteristic "sunburst" pattern. If you can see rays extending outward from a central point, even partially, mark the detection.

## Separating Clusters

Mounds often appear in groups (cemetery fields; necropoleis). When symbols are close together:

- Each distinct "sunburst" centre represents a separate mound.
- Provide individual bounding boxes for each symbol, even if they touch.
- Do not merge adjacent mounds into a single large box.

## Output Format

Return a JSON object with detections using normalised coordinates (0-1000).

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

```markdown
# Detection Prompt: Verbose Text+Image

You are an expert analyst of Soviet
Topographic Maps from the 1950s-1980s, and a seasoned landscape archaeologist.
Your goal is to find symbols on the Soviet military map that **visually match** the
provided Positive examples, representing burial
mounds (kurgans; tumuli), settlement mounds (tells), and composite symbols.

## Reference Examples

You are provided with labelled reference
images demonstrating the target symbols:

- **Positive examples** show mound
  symbols to detect. These include
  burial mounds (kurgans), settlement
  mounds (tells), and survey markers
  (triangulation points, benchmarks)
  placed ON mounds.
- **Negative examples** show areas or
  symbols that are NOT mounds. Study
  these to understand what to exclude.

Pay close attention to the visual
characteristics that distinguish
positive from negative examples.

## Task

Scan the **Target Image** systematically
and create bounding boxes for all instances that visually
match the Positive reference symbols.

## Detection Criteria

Mound symbols on Soviet 1:50,000 maps
share these characteristics:

- **Shape:** Small circular or oval
  forms, 2-4mm diameter at map scale
  (~10-20 pixels in tile)
- **Rays:** Short radiating rays
  (hachures; spikes) extending OUTWARD,
  indicating elevated terrain. Usually 6-8 rays for burial mounds, 8-15 for settlement mounds.
- **Pattern:** The "sunburst" or
  "ship's wheel" pattern is the
  essential diagnostic feature
- **Colour:** Orange-brown for plain mounds
  (same as contour lines); all-black for survey markers (triangulation or benchmark) ON a mound
- **Grouping:** May appear individually
  or in groups (necropoleis)

## Decision Procedure

When uncertain whether a feature matches
the positive examples:

1. **Check for radiating rays:** The
   outward-pointing pattern is essential.
   No rays = not a mound.

2. **Compare to examples:** Hold the
   candidate feature mentally against
   the positive references. Similar
   overall pattern?

3. **Check ray direction:** Outward =
   elevated terrain = mound. Inward =
   excavated terrain = quarry/pit.

4. **Consider degradation:** Map
   scanning may have faded or distorted symbols.
   If some rays are visible and the
   pattern matches examples, include.

5. **Consider occlusion:** Roads,
   contours, and text may obscure
   parts of symbols. Partial matches
   are acceptable.

6. **Refer to negative examples:** Does
   the feature look more like a negative
   example than a positive? If so,
   exclude.

7. **When still uncertain:** Err on the
   side of detection. Include borderline
   cases rather than missing genuine
   mounds.

## Guidelines

1. **Separate Clusters:** Mounds often
   appear in groups (necropoleis). Provide individual
   bounding boxes for each distinct
   symbol, even if they touch or overlap.

2. **Systematic Scanning:** Work through
   the target image methodically to
   avoid missing symbols in busy areas.

## Output Format

Return a JSON object with detections
using normalised coordinates (0-1000).

{
    "detections": [
        {
            "box_2d": [ymin, xmin,
                       ymax, xmax],
            "label": "mound",
            "subtype": "burial_mound" |
                "settlement_mound" |
                "triangulation_mound" |
                "benchmark_mound"
        }
    ]
}
```

---

#### 1.5.2 detect_verbose-text-image_verbose.md

**Purpose**: Extended text+image prompt with edge case guidance AND detailed exclusion criteria.
**Used by**: M/E = Verbose-text+image; H5 = Verbose

**Note**: This file was previously named `detect_verbose-text-image_hardneg.md`. Renamed to reflect H5 level naming.

```markdown
# Detection Prompt: Verbose Text+Image with Exclusion Guidance

You are an expert analyst of Soviet
Topographic Maps from the 1950s-1980s, and a seasoned landscape archaeologist.
Your goal is to find symbols on the Soviet military map that **visually match** the
provided Positive examples, representing burial
mounds (kurgans; tumuli), settlement mounds (tells), and composite symbols.

## Reference Examples

You are provided with labelled reference
images demonstrating the target symbols:

- **Positive examples** show mound
  symbols to detect. These include
  burial mounds (kurgans), settlement
  mounds (tells), and survey markers
  (triangulation points, benchmarks)
  placed ON mounds.
- **Negative examples** show areas or
  symbols that are NOT mounds. Study
  these carefully to understand what
  to exclude.

Pay close attention to the visual
characteristics that distinguish
positive from negative examples.

## Task

Scan the **Target Image** systematically
and create bounding boxes for all instances that visually
match the Positive reference symbols.

## Detection Criteria

Mound symbols on Soviet 1:50,000 maps
share these characteristics:

- **Shape:** Small circular or oval
  forms, 2-4mm diameter at map scale
  (~10-20 pixels in tile)
- **Rays:** Short radiating rays
  (hachures; spikes) extending OUTWARD,
  indicating elevated terrain. Usually 6-8 rays for burial mounds, 8-15 for settlement mounds.
- **Pattern:** The "sunburst" or
  "ship's wheel" pattern is the
  essential diagnostic feature
- **Colour:** Orange-brown for plain mounds
  (same as contour lines); all-black for survey markers (triangulation or benchmark) ON a mound
- **Grouping:** May appear individually
  or in groups (necropoleis)

## Exclusion Criteria (CRITICAL)

The following symbols appear frequently
on Soviet maps and are commonly confused
with mound symbols. Study the negative
reference images carefully, and actively
avoid marking these features:

### 1. Spot Heights

- **Visual:** Simple dots (black or
  brown) accompanied by elevation numbers
  (e.g., "185", "247").
- **Critical difference:** NO hollow shape. NO radiating
  rays (hachures; spikes). Just a dot with a number.
- **Key test:** Ignore the number; check
  the symbol. Is it hollow, with rays? No → exclude.

### 2. Triangulation Points (standalone)

- **Visual:** Black triangles with a
  central dot, but NO surrounding rays.
- **Critical difference:** NO radiating
  rays (hachures; spikes) extending outward from the
  triangle-with-central-dot.
- **Key test:** Rays around the triangle?
  No → survey marker only, exclude.
  Yes → triangulation ON mound, include.

### 3. Benchmarks (standalone)

- **Visual:** Black squares or circles
  with a central dot, NO surrounding rays.
- **Critical difference:** NO radiating
  rays (hachures; spikes) extending outward from the
  square-with-central-dot.
- **Key test:** Rays around the shape?
  No → benchmark only, exclude.
  Yes → benchmark ON mound, include.

### 4. Quarry and Pit Symbols

- **Visual:** Circular shapes with short
  marks pointing INWARD toward centre.
- **Critical difference:** Ray direction
  reversed (inward = excavation, outward
  = elevation).
- **Key test:** Which way do marks point?
  Inward → quarry/pit, exclude.
  Outward → mound, include.

### 5. Contour Line Artefacts

- **Visual:** Closed contour lines on
  hilltops forming roughly circular
  patterns or patterns similar to a settlement mound.
- **Critical difference:** Smooth,
  continuous curves with NO rays (hachures; spikes).
- **Key test:** Rays radiating outward?
  No → contours, exclude.
  Yes → mound, include.

### 6. Infrastructure Markers

- **Visual:** Dots on roads, bridges,
  rivers, or canals.
- **Critical difference:** Located on
  linear features; no rays.
- **Key test:** Dot only on a road/river line?
  → infrastructure, exclude. Dot within a
  square or triangle that has rays
  (hachures; spikes) → mound, include.

## Decision Procedure

When uncertain whether a feature matches
the positive examples:

1. **Check for radiating rays:** The
   outward-pointing pattern is essential.
   No rays = not a mound.

2. **Compare to examples:** Hold the
   candidate feature mentally against
   the positive references. Similar
   overall pattern?

3. **Check ray direction:** Outward =
   elevated terrain = mound. Inward =
   excavated terrain = quarry/pit.

4. **Consider degradation:** Map
   scanning may have faded or distorted symbols.
   If some rays are visible and the
   pattern matches examples, include.

5. **Consider occlusion:** Roads,
   contours, and text may obscure
   parts of symbols. Partial matches
   are acceptable.

6. **Refer to negative examples:** Does
   the feature look more like a negative
   example than a positive? If so,
   exclude.

7. **When still uncertain:** Err on the
   side of detection. Include borderline
   cases rather than missing genuine
   mounds.

## Guidelines

1. **Separate Clusters:** Mounds often
   appear in groups (necropoleis). Provide individual
   bounding boxes for each distinct
   symbol, even if they touch or overlap.

2. **Systematic Scanning:** Work through
   the target image methodically to
   avoid missing symbols in busy areas.

## Output Format

Return a JSON object with detections
using normalised coordinates (0-1000).

{
    "detections": [
        {
            "box_2d": [ymin, xmin,
                       ymax, xmax],
            "label": "mound",
            "subtype": "burial_mound" |
                "settlement_mound" |
                "triangulation_mound" |
                "benchmark_mound"
        }
    ]
}
```

---

### 1.6 Two-Stage Pipeline Prompts (H2)

#### 1.6.1 propose_image-only.md

**Purpose**: High-recall proposer stage for two-stage pipeline.
**Used by**: H2 (Stage 1)

~~~markdown
# Two-Stage Detection: Proposer (Stage 1)

You are an expert landscape archaeologist analysing Soviet Topographic Maps.
Your goal is to find symbols that **visually match** the provided Positive examples.

## Task

Scan the **Target Image** and identify all instances that look like the Positive reference symbols.
When uncertain whether a feature is a mound or noise, **include it** (err on the side of detection).

## Output Format

Return a JSON object with detections using normalised coordinates (0-1000).

```json
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
~~~

---

#### 1.6.2 verify_image-only.md

**Purpose**: Precision-focused verifier stage for two-stage pipeline.
**Used by**: H2 (Stage 2)

~~~markdown
# Two-Stage Detection: Verifier (Stage 2)

You are an expert landscape archaeologist verifying candidate detections from Soviet Topographic Maps.
Your goal is to determine whether the **candidate symbol in the centre** of the crop visually matches the provided Positive examples.

## Task

Examine the **Target Candidate** and decide if it is a mound symbol.
Base your decision on visual similarity to the Positive reference examples.

## Output Format

Return a JSON object with your assessment.

```json
{
    "reasoning": "Brief description of visual features observed.",
    "mound_probability": 0.0
}
```

## Scoring Guide

- **0.9-1.0**: Clear mound symbol with radiating rays (hachures; spikes).
- **0.6-0.8**: Likely mound, some ambiguity or occlusion.
- **0.3-0.5**: Uncertain, could be mound or similar feature.
- **0.0-0.2**: Not a mound (noise, text, isolated marker, building).
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
            "category": "string — 'canonical'/'null'/'hard_positive'/'hard_negative'"
        }
    ],
    "ordering_note": "string — optional, explains example ordering"
}
```

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
| `propose_image-only.json` | H2 Stage 1 (Proposer) | propose_image-only.md |
| `verify_image-only.json` | H2 Stage 2 (Verifier) | verify_image-only.md |

#### Pilot Config (1 file)

| Configuration File | Purpose |
|--------------------|---------|
| `pilot_tilesize.json` | Tile size pilot study |

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
    "ordering_note": "Canonical-first: Canon+ (4), HP (4), Canon- (2), HN (4), null (3). Total: 17 examples (Scale-8)."
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
    "description": "H5=Terse: Brief exclusion guidance. Same Scale-8 library as Minimal/Verbose.",
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
    "ordering_note": "Canonical-first: Canon+ (4), HP (4), Canon- (2), HN (4), null (3). Total: 17 examples (Scale-8)."
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
    "description": "H5=Verbose: Detailed exclusion guidance with explanations for each confusable symbol.",
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
    "ordering_note": "Canonical-first: Canon+ (4), HP (4), Canon- (2), HN (4), null (3). Total: 17 examples (Scale-8)."
}
```

**Key difference from H5=Terse**: Same Scale-8 library (17 examples) with detailed exclusion text in `_verbose` instruction file explaining why each confusable symbol is not a mound. Tests whether verbose explanations improve precision over brief guidance.

---

### 2.7 Example Configuration: H4 Canonical-Last Ordering

#### detect_verbose-text-image_canonical-last_{optimal-h5}.json

**M/E**: Optimal from H1 (likely Verbose-text+image) | **H5**: Optimal from H5 | **H4**: Canonical-last

```json
{
    "version": "detect_verbose-text-image_canonical-last_terse",
    "description": "H4-B: Canonical-last ordering at optimal M/E and H5.",
    "hypothesis": "H4-B",
    "model": "gemini-3-flash",
    "instruction_file": "detect_verbose-text-image_terse.md",
    "temperature": 1.0,
    "max_output_tokens": 8192,
    "examples": [
        {"path": "neutral/example_11.png", "label": "Negative", "category": "hard_negative"},
        {"path": "neutral/example_12.png", "label": "Negative", "category": "hard_negative"},
        {"path": "neutral/example_13.png", "label": "Negative", "category": "hard_negative"},
        {"path": "neutral/example_14.png", "label": "Negative", "category": "hard_negative"},
        {"path": "neutral/example_09.png", "label": "Negative", "category": "canonical_negative"},
        {"path": "neutral/example_10.png", "label": "Negative", "category": "canonical_negative"},
        {"path": "neutral/example_15.png", "label": "Negative", "category": "null"},
        {"path": "neutral/example_16.png", "label": "Negative", "category": "null"},
        {"path": "neutral/example_17.png", "label": "Negative", "category": "null"},
        {"path": "neutral/example_05.png", "label": "Positive", "category": "hard_positive"},
        {"path": "neutral/example_06.png", "label": "Positive", "category": "hard_positive"},
        {"path": "neutral/example_07.png", "label": "Positive", "category": "hard_positive"},
        {"path": "neutral/example_08.png", "label": "Positive", "category": "hard_positive"},
        {"path": "neutral/example_01.png", "label": "Positive", "category": "canonical_positive"},
        {"path": "neutral/example_02.png", "label": "Positive", "category": "canonical_positive"},
        {"path": "neutral/example_03.png", "label": "Positive", "category": "canonical_positive"},
        {"path": "neutral/example_04.png", "label": "Positive", "category": "canonical_positive"}
    ],
    "ordering_note": "Canonical-last: HN (4), Canon- (2), null (3), HP (4), Canon+ (4). Total: 17 examples (Scale-8)."
}
```

**Note**: Canonical-last tests recency bias by placing the most informative examples (canonical positives) in final positions. H4 is now tested at optimal M/E only (3 cells total).

---

### 2.8 Example Configuration: H4 Random Ordering

#### detect_verbose-text-image_random-order_{optimal-h5}.json

**M/E**: Optimal from H1 | **H5**: Optimal from H5 | **H4**: Random

```json
{
    "version": "detect_verbose-text-image_random-order_terse",
    "description": "H4-C: Random ordering at optimal M/E and H5.",
    "hypothesis": "H4-C",
    "model": "gemini-3-flash",
    "instruction_file": "detect_verbose-text-image_terse.md",
    "temperature": 1.0,
    "max_output_tokens": 8192,
    "random_seed": 42,
    "examples": [
        {"path": "neutral/example_13.png", "label": "Negative", "category": "hard_negative"},
        {"path": "neutral/example_02.png", "label": "Positive", "category": "canonical_positive"},
        {"path": "neutral/example_04.png", "label": "Positive", "category": "canonical_positive"},
        {"path": "neutral/example_12.png", "label": "Negative", "category": "hard_negative"},
        {"path": "neutral/example_15.png", "label": "Negative", "category": "null"},
        {"path": "neutral/example_05.png", "label": "Positive", "category": "hard_positive"},
        {"path": "neutral/example_14.png", "label": "Negative", "category": "null"},
        {"path": "neutral/example_01.png", "label": "Positive", "category": "canonical_positive"},
        {"path": "neutral/example_08.png", "label": "Positive", "category": "hard_positive"},
        {"path": "neutral/example_10.png", "label": "Negative", "category": "canonical_negative"},
        {"path": "neutral/example_09.png", "label": "Negative", "category": "canonical_negative"},
        {"path": "neutral/example_03.png", "label": "Positive", "category": "canonical_positive"},
        {"path": "neutral/example_16.png", "label": "Negative", "category": "null"},
        {"path": "neutral/example_07.png", "label": "Positive", "category": "hard_positive"},
        {"path": "neutral/example_11.png", "label": "Negative", "category": "hard_negative"},
        {"path": "neutral/example_17.png", "label": "Negative", "category": "null"},
        {"path": "neutral/example_06.png", "label": "Positive", "category": "hard_positive"}
    ],
    "ordering_note": "Permutation generated with seed 42. Total: 17 examples (Scale-8). Multiple seeds tested; results averaged."
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
    "description": "H4-B + H5-C: Canonical-last ordering with verbose negative guidance.",
    "hypothesis": "H4-B, H5-C",
    "model": "gemini-3-flash",
    "instruction_file": "detect_image-only_verbose.md",
    "temperature": 1.0,
    "max_output_tokens": 8192,
    "examples": [
        {"path": "neutral/example_11.png", "label": "Negative", "category": "hard_negative"},
        {"path": "neutral/example_12.png", "label": "Negative", "category": "hard_negative"},
        {"path": "neutral/example_13.png", "label": "Negative", "category": "hard_negative"},
        {"path": "neutral/example_14.png", "label": "Negative", "category": "hard_negative"},
        {"path": "neutral/example_09.png", "label": "Negative", "category": "canonical_negative"},
        {"path": "neutral/example_10.png", "label": "Negative", "category": "canonical_negative"},
        {"path": "neutral/example_15.png", "label": "Negative", "category": "null"},
        {"path": "neutral/example_16.png", "label": "Negative", "category": "null"},
        {"path": "neutral/example_17.png", "label": "Negative", "category": "null"},
        {"path": "neutral/example_05.png", "label": "Positive", "category": "hard_positive"},
        {"path": "neutral/example_06.png", "label": "Positive", "category": "hard_positive"},
        {"path": "neutral/example_07.png", "label": "Positive", "category": "hard_positive"},
        {"path": "neutral/example_08.png", "label": "Positive", "category": "hard_positive"},
        {"path": "neutral/example_01.png", "label": "Positive", "category": "canonical_positive"},
        {"path": "neutral/example_02.png", "label": "Positive", "category": "canonical_positive"},
        {"path": "neutral/example_03.png", "label": "Positive", "category": "canonical_positive"},
        {"path": "neutral/example_04.png", "label": "Positive", "category": "canonical_positive"}
    ],
    "ordering_note": "Canonical-last: HN (4), Canon- (2), null (3), HP (4), Canon+ (4). Total: 17 examples (Scale-8)."
}
```

**Note**: Combined H4 and H5 conditions test whether ordering effects interact with negative text elaboration.

---

### 2.10 Two-Stage Pipeline Configurations (H2)

#### propose_image-only.json

```json
{
    "version": "propose_image-only",
    "description": "Two-Stage Proposer (Stage 1). High-recall detection, use with verify_image-only.",
    "model": "gemini-3-flash",
    "instruction_file": "propose_image-only.md",
    "temperature": 1.0,
    "max_output_tokens": 8192,
    "examples": [
        {"path": "neutral/example_01.png", "label": "Positive: Burial Mound (Kurgan)"},
        {"path": "neutral/example_02.png", "label": "Positive: Settlement Mound"},
        {"path": "neutral/example_03.png", "label": "Positive: Triangulation Point ON Mound"},
        {"path": "neutral/example_04.png", "label": "Positive: Benchmark ON Mound"},
        {"path": "neutral/example_05.png", "label": "Negative: Empty tile (no mounds)"},
        {"path": "neutral/example_06.png", "label": "Negative: Empty tile (no mounds)"},
        {"path": "neutral/example_07.png", "label": "Negative: Empty tile (no mounds)"},
        {"path": "neutral/example_08.png", "label": "Negative: Benchmark ALONE (no mound)"},
        {"path": "neutral/example_09.png", "label": "Negative: Triangulation Point ALONE (no mound)"}
    ]
}
```

---

#### verify_image-only.json

```json
{
    "version": "verify_image-only",
    "description": "Two-Stage Verifier (Stage 2). Precision-focused verification.",
    "model": "gemini-3-flash",
    "instruction_file": "verify_image-only.md",
    "temperature": 1.0,
    "max_output_tokens": 8192,
    "examples": [
        {"path": "neutral/example_01.png", "label": "Positive: Burial Mound (Kurgan)"},
        {"path": "neutral/example_02.png", "label": "Positive: Settlement Mound"},
        {"path": "neutral/example_03.png", "label": "Positive: Triangulation Point ON Mound"},
        {"path": "neutral/example_04.png", "label": "Positive: Benchmark ON Mound"},
        {"path": "neutral/example_05.png", "label": "Negative: Empty tile (no mounds)"},
        {"path": "neutral/example_06.png", "label": "Negative: Empty tile (no mounds)"},
        {"path": "neutral/example_07.png", "label": "Negative: Empty tile (no mounds)"},
        {"path": "neutral/example_08.png", "label": "Negative: Benchmark ALONE (no mound)"},
        {"path": "neutral/example_09.png", "label": "Negative: Triangulation Point ALONE (no mound)"}
    ]
}
```

**Note**: Pipeline configs use descriptive labels since they are separate from the base detection experiment.

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

*Document version: 2.10*
*Created: 2026-01-02*
*Updated: 2026-01-12*

**Changelog:**

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
