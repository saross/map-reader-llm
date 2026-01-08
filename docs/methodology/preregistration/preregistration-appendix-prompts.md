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

The prompt architecture reflects the orthogonal factorial design:

- **M/E Factor** (5 levels): Controls modality and text elaboration
  - Image-only, Brief-text, Brief-text+image, Verbose-text, Verbose-text+image
- **H5 Factor** (3 levels): Controls hard negative guidance
  - None, Images-only, Text+Images

This yields:

- **10 detection instruction files**: 5 M/E levels × 2 exclusion variants (base, `_hardneg`)
- **2 two-stage pipeline instruction files**: propose_image-only.md, verify_image-only.md
- **16 configuration files**: See Section 2.2 for breakdown

**Note on config count**: Text-only modalities (Brief-text, Verbose-text) cannot use H5=Images-only or H5=Text+Images since they have no example images. This reduces the factorial from 5×3=15 to 9 valid combinations:

- 3 image-using modalities × 3 H5 levels = 9
- 2 text-only modalities × H5=None only = 2 (runtime variants, not separate configs)

### Orthogonal Factor Separation

The design maintains strict orthogonality between M/E levels (modality + elaboration, tested in H1) and H5 (hard negatives):

| Factor | Controls | Content |
| ------ | -------- | ------- |
| M/E level (H1) | Detail level for **positives** (canonical symbols + HP edge cases) | Minimal = task only; Brief = terse descriptions + terse HP mention; Verbose = detailed descriptions + detailed HP guidance |
| H5 (Hard negatives) | Presence of **negative** guidance | Exclusion text about what NOT to detect; HN images of confusable symbols |

**Brief vs Verbose distinction**: Both brief and verbose include hard positive (HP) edge case guidance — the difference is detail level, not content coverage. Brief mentions edge case types tersely ("symbols may be partially occluded"); verbose provides detailed guidance on occlusion types, degradation patterns, clustering, and variants.

**Critical distinction**: Neither brief nor verbose includes exclusion guidance for hard negatives. That is controlled exclusively by H5 via `_hardneg.md` instruction variants.

---

## Pre-Holdout Finalisation

The following elements will be finalised before holdout evaluation:

### Empirically-Determined Content

#### Hard Negative Images (H5 Images-only and Text+Images conditions)

Configuration files with hard negative images currently use placeholder paths for empirically-derived examples. These will be populated via the procedure in preregistration.md Section 8.4.2:

1. Run image-only baseline on 20 training tiles (5 passes)
2. Identify False Positives (≥3/5 passes) → select top M as hard negatives
3. Document selected images with filenames, source tiles, and selection rationale

**Legend-derived hard negatives** (can be specified now):

- Standalone benchmark (no rays)
- Standalone triangulation point (no rays)

**Empirically-derived hard negatives** (TBD after Phase 1):

- Additional confusable symbols identified from FP analysis

#### Hard Positive Images (H9 Diversity conditions)

Hard positive images for H9 diversity conditions will be derived from False Negatives in Phase 1 baseline analysis.

**Configs affected:**

- All `*_images.json` and `*_both.json` variants (H5)
- `propose_image-only.json` and `verify_image-only.json` (H2)
- H9 diversity conditions C and E (varied images)

### H9 Text Diversity Prompts

The 5 semantically equivalent prompt variants (V1–V5) will be constructed after the optimal base configuration is determined from the main factorial.

**Construction procedure:**

1. Identify winning configuration (M/E level, H7 level, temperature)
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

| Filename | M/E Level | Exclusion Guidance | H1 Role |
|----------|-----------|-------------------|---------|
| `detect_image-only.md` | Image-only | No | H1 baseline |
| `detect_image-only_hardneg.md` | Image-only | Yes | H1 + H5 |
| `detect_brief-text.md` | Brief-text | No | H1 text-only baseline |
| `detect_brief-text_hardneg.md` | Brief-text | Yes | H1 + H5 |
| `detect_brief-text-image.md` | Brief-text+image | No | H1 baseline |
| `detect_brief-text-image_hardneg.md` | Brief-text+image | Yes | H1 + H5 |
| `detect_verbose-text.md` | Verbose-text | No | H1 elaboration |
| `detect_verbose-text_hardneg.md` | Verbose-text | Yes | H1 + H5 |
| `detect_verbose-text-image.md` | Verbose-text+image | No | H1 elaboration |
| `detect_verbose-text-image_hardneg.md` | Verbose-text+image | Yes | H1 + H5 |

**Naming convention**: `detect_{modality}[_hardneg].md`

- `{modality}`: image-only, brief-text, brief-text-image, verbose-text, verbose-text-image
- `_hardneg`: suffix indicates exclusion guidance for hard negatives (H5 conditions)

---

### 1.1 Image-Only Instructions

#### 1.1.1 detect_image-only.md

**Purpose**: Baseline image-only detection with minimal text instruction.
**Used by**: M/E = Image-only; H5 = None or Images-only
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

#### 1.1.2 detect_image-only_hardneg.md

**Purpose**: Image-only detection with exclusion guidance for hard negatives.
**Used by**: M/E = Image-only; H5 = Text+Images

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
**Used by**: M/E = Brief-text; H5 = None (no images in this condition)

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

#### 1.2.2 detect_brief-text_hardneg.md

**Purpose**: Brief text-only detection with exclusion guidance for hard negatives.
**Used by**: M/E = Brief-text; H5 = None (text-only condition)

```markdown
# Detection Prompt: Brief Text with Exclusion Guidance

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

## Exclusion Criteria (CRITICAL)

The following symbols are easily confused with mounds. **DO NOT mark:**

### Triangulation Point (standalone)

- **Visual:** Hollow black triangle with central dot, but **NO radiating rays**.

### Benchmark (standalone)

- **Visual:** Hollow black square/circle with crosshairs, but **NO radiating rays**.

### Bridge/Culvert Dots

- **Visual:** Simple black dots on roads, rivers, or canals. NO rays.

### Spot Heights

- **Visual:** Simple dots (black/brown) with elevation numbers. NO rays.

### Quarry/Pit Symbols

- **Visual:** Circular shapes with rays pointing **INWARD**. Mound rays always point OUTWARD.

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
**Used by**: M/E = Brief-text+image; H5 = None or Images-only
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

#### 1.3.2 detect_brief-text-image_hardneg.md

**Purpose**: Brief text+image prompt with exclusion guidance for hard negatives.
**Used by**: M/E = Brief-text+image; H5 = Text+Images

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

**Note on verbose text content**: Verbose text extends brief text with detailed descriptions and **edge case guidance for hard positives** (symbols that are genuine mounds but may be missed due to occlusion, degradation, or atypical appearance). Verbose text does NOT include exclusion guidance for hard negatives — that is controlled by the `_hardneg` variant and H7 factor.

#### 1.4.1 detect_verbose-text.md

**Purpose**: Extended text-only prompt with comprehensive symbol descriptions and edge case guidance.
**Used by**: M/E = Verbose-text; H5 = None (no images in text-only conditions)
**Word count**: ~700 words (vs ~200 for brief version)

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
2. **Count:** Typically 8-15 rays, roughly evenly spaced around the perimeter. Count depends on symbol type.
3. **Length:** Approximately equal to or slightly longer than the diameter of the central shape.
4. **Consistency:** Rays should be roughly equal in length and evenly spaced; highly irregular patterns may indicate other features (noting that some areas of the map scanned poorly and may have some distortion).

### Colour Analysis

- **Orange-brown symbol:** Indicates a "plain" burial or settlement mound.
- **Black symbol:** Indicates a burial mound with survey marker (triangulation point or benchmark) placed on top of the mound.
- Each symbol is a single colour, either orange-brown or black.

## Edge Cases: Hard-to-Detect Mounds

The following situations may cause genuine mounds to be missed. Pay special attention to these cases:

### Occluded Mounds

Symbols frequently intersected by other map features:

- **Roads:** Black or red lines may cross through a mound symbol.
- **Contour lines:** Brown lines at similar colour may partially merge with mound rays.
- **Grid lines:** Blue coordinate grid lines may overlay symbols.
- **Text labels:** Cyrillic place names or elevation numbers may obscure parts of symbols.

In all cases, focus on identifying the characteristic "sunburst" pattern. If you can see rays extending outward from a central point, even partially, mark the detection.

### Degraded or Faded Symbols

Map scanning or printing may have faded or distorted some symbols. Look for faint or somewhat asymmetrical ray patterns even if not perfectly symmetrical or fully distinct.

### Clustered Mounds

Mounds often appear in groups (cemetery fields; necropoleis). When symbols are close together:

- Each distinct "sunburst" centre represents a separate mound.
- Provide individual bounding boxes for each symbol, even if they touch.
- Do not merge adjacent mounds into a single large box.

## Decision Procedure

When uncertain whether a feature is a mound, apply this systematic checklist:

1. **Check for rays:** Are there short rays (hachures; spikes) radiating outward from a central point? No rays = not a mound.

2. **Check ray direction:** Do the rays point OUTWARD (elevation/mound) or INWARD (excavation/quarry)? Burial or settlement mound rays ALWAYS point outwards.

3. **Check central shape:** Is there a circle, oval, triangle, or square at the centre? The central shape helps classify the mound subtype.

4. **Check colour:** Are the symbols orange-brown ("plain" burial or settlement mound with no survey infrastructure) or black (mound with triangulation point or benchmark)?

5. **Consider occlusion:** Roads, contours, rivers, or text may obscure part of the symbol. If some rays, or partial rays, are visible and the overall pattern matches, include the detection.

6. **Consider degradation:** Map scanning or printing may have faded or distorted some symbols. Look for faint ray patterns.

7. **When still uncertain:** Err on the side of detection. It is better to include a borderline case than to miss a genuine mound.

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

#### 1.4.2 detect_verbose-text_hardneg.md

**Purpose**: Extended text-only prompt with edge case guidance AND exclusion criteria.
**Used by**: M/E = Verbose-text; H7 = Text-only (no images in text-only conditions)
**Word count**: ~1,200 words

*[Extends detect_verbose-text.md with the following additional section after "Decision Procedure":]*

```markdown
## Exclusion Criteria (CRITICAL)

The following symbols are easily confused with mounds. **DO NOT mark:**

### Triangulation Point (standalone)

- **Visual:** Hollow black triangle with central dot, but **NO radiating rays**.
- **Key distinction:** Mound-based triangulation points have rays; standalone ones do not.

### Benchmark (standalone)

- **Visual:** Hollow black square/circle with crosshairs, but **NO radiating rays**.
- **Key distinction:** Mound-based benchmarks have rays; standalone ones do not.

### Bridge/Culvert Dots

- **Visual:** Simple black dots on roads, rivers, or canals. NO rays.
- **Location:** Always on linear features (roads, waterways).

### Spot Heights

- **Visual:** Simple dots (black/brown) with elevation numbers. NO rays.
- **Function:** Mark elevation at a point, not a mound.

### Quarry/Pit Symbols

- **Visual:** Circular shapes with rays pointing **INWARD**. Mound rays always point OUTWARD.
- **Colour:** Often orange-brown like mounds.
- **Key distinction:** Ray direction — inward = excavation, outward = elevation.

### Contour Artefacts

- **Visual:** Dense contour lines may create ray-like patterns.
- **Key distinction:** Contours are continuous lines; mound rays are discrete ticks.

### Vegetation Symbols

- **Visual:** Some vegetation symbols have radiating elements.
- **Colour:** Usually green or grey, not orange-brown.

### Well Symbols

- **Visual:** Small circles, sometimes with short ticks.
- **Colour:** Usually blue (water features).
- **Key distinction:** Fewer, shorter ticks than mound rays.
```

---

### 1.5 Verbose-Text+Image Instructions

#### 1.5.1 detect_verbose-text-image.md

**Purpose**: Extended text+image prompt with decision procedures and edge case guidance.
**Used by**: M/E = Verbose-text+image; H5 = None or Images-only

```markdown
# Detection Prompt: Verbose Text+Image

You are an expert analyst of Soviet Topographic Maps from the 1950s-1980s, and a seasoned landscape archaeologist. Your goal is to find symbols on the Soviet military map that **visually match** the provided Positive examples, representing burial mounds (kurgans; tumuli), settlement mounds (tells), and composite symbols.

## Reference Examples

You are provided with labelled reference images demonstrating the target symbols:

- **Positive examples** show mound symbols to detect. These include burial mounds (kurgans), settlement mounds (tells), and survey markers (triangulation points, benchmarks) placed ON mounds.
- **Negative examples** show areas or symbols that are NOT mounds. Study these to understand what to exclude.

Pay close attention to the visual characteristics that distinguish positive from negative examples.

## Task

Scan the **Target Image** systematically and create bounding boxes for all instances that visually match the Positive reference symbols.

## Detection Criteria

Mound symbols on Soviet 1:50,000 maps share these characteristics:

- **Shape:** Small circular or oval forms, 2-4mm diameter at map scale (~10-20 pixels in tile)
- **Rays:** Short radiating rays (hachures; spikes) extending OUTWARD, indicating elevated terrain. Usually 6-8 rays for burial mounds, 8-15 for settlement mounds.
- **Pattern:** The "sunburst" or "ship's wheel" pattern is the essential diagnostic feature
- **Colour:** Orange-brown for plain mounds (same as contour lines); all-black for survey markers (triangulation or benchmark) ON a mound
- **Grouping:** May appear individually or in groups (necropoleis)

## Edge Cases: Hard-to-Detect Mounds

### Occluded Mounds

Roads, contours, grid lines, and text may obscure parts of symbols. If you can see rays extending outward from a central point, even partially, mark the detection.

### Degraded or Faded Symbols

Map scanning may have faded or distorted symbols. If some rays are visible and the pattern matches examples, include.

### Clustered Mounds

Mounds often appear in groups. Provide individual bounding boxes for each distinct symbol, even if they touch or overlap.

## Decision Procedure

When uncertain whether a feature matches the positive examples:

1. **Check for radiating rays:** The outward-pointing pattern is essential. No rays = not a mound.

2. **Compare to examples:** Hold the candidate feature mentally against the positive references. Similar overall pattern?

3. **Check ray direction:** Outward = elevated terrain = mound. Inward = excavated terrain = quarry/pit.

4. **Consider degradation:** Map scanning may have faded or distorted symbols. If some rays are visible and the pattern matches examples, include.

5. **Consider occlusion:** Roads, contours, and text may obscure parts of symbols. Partial matches are acceptable.

6. **Refer to negative examples:** Does the feature look more like a negative example than a positive? If so, exclude.

7. **When still uncertain:** Err on the side of detection. Include borderline cases rather than missing genuine mounds.

## Guidelines

1. **Separate Clusters:** Mounds often appear in groups (necropoleis). Provide individual bounding boxes for each distinct symbol, even if they touch or overlap.

2. **Systematic Scanning:** Work through the target image methodically to avoid missing symbols in busy areas.

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

#### 1.5.2 detect_verbose-text-image_hardneg.md

**Purpose**: Extended text+image prompt with edge case guidance AND exclusion criteria.
**Used by**: M/E = Verbose-text+image; H5 = Text+Images

*[Extends detect_verbose-text-image.md with the following additional section after "Decision Procedure":]*

```markdown
## Exclusion Guidance

Rays are key: Shapes without visible radiating rays are not mounds. Consider occlusion or degradation before excluding.

**DO NOT mark:**

- **Standalone triangulation points:** Black triangle, NO rays
- **Standalone benchmarks:** Black square/circle, NO rays
- **Spot heights:** Simple dots with elevation numbers
- **Bridge/culvert markers:** Dots on roads or waterways
- **Quarry/pit symbols:** Rays pointing INWARD (mound rays point OUTWARD)
- **Contour artefacts:** Dense contour lines creating ray-like patterns
```

---

### 1.6 Two-Stage Pipeline Prompts (H2)

#### 1.6.1 propose_image-only.md

**Purpose**: High-recall proposer stage for two-stage pipeline.
**Used by**: H2 (Stage 1)

```markdown
# Two-Stage Detection: Proposer (Stage 1)

You are an expert landscape archaeologist analysing Soviet Topographic Maps.
Your goal is to find symbols that **visually match** the provided Positive examples.

## Task

Scan the **Target Image** and identify all instances that look like the Positive reference symbols.
When uncertain whether a feature is a mound or noise, **include it** (err on the side of detection).

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

#### 1.6.2 verify_image-only.md

**Purpose**: Precision-focused verifier stage for two-stage pipeline.
**Used by**: H2 (Stage 2)

```markdown
# Two-Stage Detection: Verifier (Stage 2)

You are an expert landscape archaeologist verifying candidate detections from Soviet Topographic Maps.
Your goal is to determine whether the **candidate symbol in the centre** of the crop visually matches the provided Positive examples.

## Task

Examine the **Target Candidate** and decide if it is a mound symbol.
Base your decision on visual similarity to the Positive reference examples.

## Output Format

Return a JSON object with your assessment.

{
    "reasoning": "<Brief description of visual features observed>",
    "mound_probability": "<0.0-1.0>"
}

## Scoring Guide

- **0.9-1.0**: Clear mound symbol with radiating rays (hachures; spikes).
- **0.6-0.8**: Likely mound, some ambiguity or occlusion.
- **0.3-0.5**: Uncertain, could be mound or similar feature.
- **0.0-0.2**: Not a mound (noise, text, isolated marker, building).
```

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

**Pattern**: `detect_{modality}_{hardneg}.json`

Where:

- `{modality}`: image-only, brief-text, brief-text-image, verbose-text, verbose-text-image
- `{hardneg}`: none, text, images, both

This yields 9 configuration files (3 image-using modalities × 3 H5 levels).

**Note on text-only modalities**: Brief-text and Verbose-text conditions do not use example images and cannot use H5=Images-only or H5=Text+Images. Text-only modalities are tested at T=1.0 only as runtime variants.

**Structure for image-using modalities:**

| M/E Level | H5 = None | H5 = Images-only | H5 = Text+Images |
|-----------|-----------|------------------|------------------|
| Image-only | ✓ | ✓ | ✓ |
| Brief-text+image | ✓ | ✓ | ✓ |
| Verbose-text+image | ✓ | ✓ | ✓ |

This yields **9 valid configurations**:

- 3 image-using modalities × 3 H5 levels = 9

---

### 2.3 Complete Configuration File List

| Configuration File | M/E Level | H5 Level | Instruction File |
|--------------------|-----------|----------|------------------|
| `detect_image-only_none.json` | Image-only | None | detect_image-only.md |
| `detect_image-only_text.json` | Image-only | Text-only | detect_image-only_hardneg.md |
| `detect_image-only_images.json` | Image-only | Images-only | detect_image-only.md |
| `detect_image-only_both.json` | Image-only | Text+Images | detect_image-only_hardneg.md |
| `detect_brief-text_none.json` | Brief-text | None | detect_brief-text.md |
| `detect_brief-text_text.json` | Brief-text | Text-only | detect_brief-text_hardneg.md |
| `detect_brief-text-image_none.json` | Brief-text+image | None | detect_brief-text-image.md |
| `detect_brief-text-image_text.json` | Brief-text+image | Text-only | detect_brief-text-image_hardneg.md |
| `detect_brief-text-image_images.json` | Brief-text+image | Images-only | detect_brief-text-image.md |
| `detect_brief-text-image_both.json` | Brief-text+image | Text+Images | detect_brief-text-image_hardneg.md |
| `detect_verbose-text_none.json` | Verbose-text | None | detect_verbose-text.md |
| `detect_verbose-text_text.json` | Verbose-text | Text-only | detect_verbose-text_hardneg.md |
| `detect_verbose-text-image_none.json` | Verbose-text+image | None | detect_verbose-text-image.md |
| `detect_verbose-text-image_text.json` | Verbose-text+image | Text-only | detect_verbose-text-image_hardneg.md |
| `detect_verbose-text-image_images.json` | Verbose-text+image | Images-only | detect_verbose-text-image.md |
| `detect_verbose-text-image_both.json` | Verbose-text+image | Text+Images | detect_verbose-text-image_hardneg.md |

**Additional pipeline configurations:**

| Configuration File | Purpose | Instruction File |
|--------------------|---------|------------------|
| `propose_image-only.json` | H3 Stage 1 (Proposer) | propose_image-only.md |
| `verify_image-only.json` | H3 Stage 2 (Verifier) | verify_image-only.md |

---

### 2.4 Example Configuration: Image-Only, No Hard Negatives

#### detect_image-only_none.json

**M/E**: Image-only | **H7**: None

```json
{
    "version": "detect_image-only_none",
    "description": "Image-only baseline. Minimal text, canonical examples only.",
    "hypothesis": "M/E=Image-only, H5=None",
    "model": "gemini-3-flash",
    "instruction_file": "detect_image-only.md",
    "temperature": 1.0,
    "max_output_tokens": 8192,
    "examples": [
        {"path": "examples/canonical_burial_mound.png", "label": "Positive", "category": "canonical"},
        {"path": "examples/canonical_settlement_mound.png", "label": "Positive", "category": "canonical"},
        {"path": "examples/canonical_triangulation_mound.png", "label": "Positive", "category": "canonical"},
        {"path": "examples/canonical_benchmark_mound.png", "label": "Positive", "category": "canonical"},
        {"path": "examples/null_tile_01.png", "label": "Negative", "category": "null"},
        {"path": "examples/null_tile_02.png", "label": "Negative", "category": "null"},
        {"path": "examples/null_tile_03.png", "label": "Negative", "category": "null"},
        {"path": "examples/hardpos_empirical_TBD_01.png", "label": "Positive: [TBD from Phase 1 FN analysis]", "category": "hard_positive"},
        {"path": "examples/hardpos_empirical_TBD_02.png", "label": "Positive: [TBD from Phase 1 FN analysis]", "category": "hard_positive"}
    ],
    "ordering_note": "Canonical-first: legend positives, hard positives, nulls."
}
```

---

### 2.5 Example Configuration: Image-Only, Images-Only Hard Negatives

#### detect_image-only_images.json

**M/E**: Image-only | **H7**: Images-only

```json
{
    "version": "detect_image-only_images",
    "description": "Image-only with hard negative IMAGES (no exclusion text).",
    "hypothesis": "M/E=Image-only, H5=Images-only",
    "model": "gemini-3-flash",
    "instruction_file": "detect_image-only.md",
    "temperature": 1.0,
    "max_output_tokens": 8192,
    "examples": [
        {"path": "examples/canonical_burial_mound.png", "label": "Positive", "category": "canonical"},
        {"path": "examples/canonical_settlement_mound.png", "label": "Positive", "category": "canonical"},
        {"path": "examples/canonical_triangulation_mound.png", "label": "Positive", "category": "canonical"},
        {"path": "examples/canonical_benchmark_mound.png", "label": "Positive", "category": "canonical"},
        {"path": "examples/null_tile_01.png", "label": "Negative", "category": "null"},
        {"path": "examples/null_tile_02.png", "label": "Negative", "category": "null"},
        {"path": "examples/null_tile_03.png", "label": "Negative", "category": "null"},
        {"path": "examples/hardpos_empirical_TBD_01.png", "label": "Positive", "category": "hard_positive"},
        {"path": "examples/hardpos_empirical_TBD_02.png", "label": "Positive", "category": "hard_positive"},
        {"path": "examples/hardneg_standalone_benchmark.png", "label": "Negative", "category": "hard_negative"},
        {"path": "examples/hardneg_standalone_triangulation.png", "label": "Negative", "category": "hard_negative"},
        {"path": "examples/hardneg_empirical_TBD_01.png", "label": "Negative", "category": "hard_negative"}
    ],
    "ordering_note": "Canonical-first: legend positives, hard positives, nulls, then hard negatives."
}
```

**Label convention for H7 conditions:**

| H5 Level | Hard Negative Label Style |
|----------|---------------------------|
| Images-only | Minimal: `"Negative"` |
| Text+Images | Detailed: `"Negative: Benchmark ALONE (no mound). NO radiating rays."` |

This distinction tests whether the model needs explicit textual explanation of why examples are negative, or whether visual examples alone suffice.

---

### 2.6 Example Configuration: Image-Only, Text+Images Hard Negatives

#### detect_image-only_both.json

**M/E**: Image-only | **H7**: Text+Images

```json
{
    "version": "detect_image-only_both",
    "description": "Image-only with hard negative TEXT (exclusion guidance) AND IMAGES.",
    "hypothesis": "M/E=Image-only, H5=Text+Images",
    "model": "gemini-3-flash",
    "instruction_file": "detect_image-only_hardneg.md",
    "temperature": 1.0,
    "max_output_tokens": 8192,
    "examples": [
        {"path": "examples/canonical_burial_mound.png", "label": "Positive", "category": "canonical"},
        {"path": "examples/canonical_settlement_mound.png", "label": "Positive", "category": "canonical"},
        {"path": "examples/canonical_triangulation_mound.png", "label": "Positive", "category": "canonical"},
        {"path": "examples/canonical_benchmark_mound.png", "label": "Positive", "category": "canonical"},
        {"path": "examples/null_tile_01.png", "label": "Negative", "category": "null"},
        {"path": "examples/null_tile_02.png", "label": "Negative", "category": "null"},
        {"path": "examples/null_tile_03.png", "label": "Negative", "category": "null"},
        {"path": "examples/hardpos_empirical_TBD_01.png", "label": "Positive: [TBD from Phase 1 FN analysis]", "category": "hard_positive"},
        {"path": "examples/hardpos_empirical_TBD_02.png", "label": "Positive: [TBD from Phase 1 FN analysis]", "category": "hard_positive"},
        {"path": "examples/hardneg_standalone_benchmark.png", "label": "Negative: Benchmark ALONE (no mound). NO radiating rays.", "category": "hard_negative"},
        {"path": "examples/hardneg_standalone_triangulation.png", "label": "Negative: Triangulation Point ALONE (no mound). NO radiating rays.", "category": "hard_negative"},
        {"path": "examples/hardneg_empirical_TBD_01.png", "label": "Negative: [TBD from Phase 1 FP analysis]", "category": "hard_negative"}
    ],
    "ordering_note": "Canonical-first: legend positives, hard positives, nulls, then hard negatives."
}
```

---

### 2.7 Example Configuration: Brief-Text (No Images)

#### detect_brief-text_none.json

**M/E**: Brief-text | **H7**: None

```json
{
    "version": "detect_brief-text_none",
    "description": "Brief text-only baseline. No example images.",
    "hypothesis": "M/E=Brief-text, H5=None",
    "model": "gemini-3-flash",
    "instruction_file": "detect_brief-text.md",
    "temperature": 1.0,
    "max_output_tokens": 8192,
    "examples": [],
    "ordering_note": "Text-only condition: no example images."
}
```

---

### 2.8 Example Configuration: Verbose-Text+Image, Text-Only Hard Negatives

#### detect_verbose-text-image_text.json

**M/E**: Verbose-text+image | **H7**: Text-only

```json
{
    "version": "detect_verbose-text-image_text",
    "description": "Verbose text+image with hard negative TEXT (exclusion guidance) but no hard negative images.",
    "hypothesis": "M/E=Verbose-text+image, H5=Text+Images",
    "model": "gemini-3-flash",
    "instruction_file": "detect_verbose-text-image_hardneg.md",
    "temperature": 1.0,
    "max_output_tokens": 8192,
    "examples": [
        {"path": "examples/canonical_burial_mound.png", "label": "Positive: Burial Mound (Kurgan). Sunburst/gear shape with radiating spikes.", "category": "canonical"},
        {"path": "examples/canonical_settlement_mound.png", "label": "Positive: Settlement Mound. Larger, irregular shape with radiating ticks.", "category": "canonical"},
        {"path": "examples/canonical_triangulation_mound.png", "label": "Positive: Triangulation Point ON Mound. Black triangle surrounded by mound rays.", "category": "canonical"},
        {"path": "examples/canonical_benchmark_mound.png", "label": "Positive: Benchmark ON Mound. Black square surrounded by mound rays.", "category": "canonical"},
        {"path": "examples/null_tile_01.png", "label": "Negative: Empty tile. No mounds present.", "category": "null"},
        {"path": "examples/null_tile_02.png", "label": "Negative: Empty tile. No mounds present.", "category": "null"},
        {"path": "examples/null_tile_03.png", "label": "Negative: Empty tile. No mounds present.", "category": "null"},
        {"path": "examples/hardpos_empirical_TBD_01.png", "label": "Positive: [TBD from Phase 1 FN analysis]", "category": "hard_positive"},
        {"path": "examples/hardpos_empirical_TBD_02.png", "label": "Positive: [TBD from Phase 1 FN analysis]", "category": "hard_positive"}
    ],
    "ordering_note": "Canonical-first: legend positives, hard positives, nulls. Text-only hard negatives in instruction file."
}
```

---

### 2.9 H4 Ordering Variant Configurations

For H4 (ordering hypothesis), three ordering variants are tested at selected M/E levels:

| Ordering | Description |
|----------|-------------|
| Canonical-first | Legend positives first, then nulls, then hard negatives (if any) |
| Canonical-last | Hard negatives first (if any), then nulls, then legend positives |
| Random | All examples shuffled with documented random seed |

**H4 partial cross**: 3 orderings × 3 M/E levels (Image-only, Brief-text+image, Verbose-text+image) at fixed H5 and T.

Example ordering variant files would follow the pattern:

- `detect_image-only_none_canonical-last.json`
- `detect_image-only_none_random.json`

#### Example: Canonical-Last Ordering

**detect_image-only_none_canonical-last.json**

```json
{
    "version": "detect_image-only_none_canonical-last",
    "description": "Image-only baseline with canonical-LAST ordering (H4 variant).",
    "hypothesis": "M/E=Image-only, H5=None, O=Canonical-last",
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

---

### 2.10 Two-Stage Pipeline Configurations (H2)

#### propose_image-only.json

```json
{
    "version": "propose_image-only",
    "description": "Two-Stage Proposer (Stage 1). High-recall detection.",
    "hypothesis": "H2",
    "model": "gemini-3-flash",
    "instruction_file": "propose_image-only.md",
    "temperature": 1.0,
    "max_output_tokens": 8192,
    "examples": [
        {"path": "examples/canonical_burial_mound.png", "label": "Positive: Burial Mound (Kurgan)", "category": "canonical"},
        {"path": "examples/canonical_settlement_mound.png", "label": "Positive: Settlement Mound", "category": "canonical"},
        {"path": "examples/canonical_triangulation_mound.png", "label": "Positive: Triangulation Point ON Mound", "category": "canonical"},
        {"path": "examples/canonical_benchmark_mound.png", "label": "Positive: Benchmark ON Mound", "category": "canonical"},
        {"path": "examples/null_tile_01.png", "label": "Negative: Empty tile (no mounds)", "category": "null"},
        {"path": "examples/null_tile_02.png", "label": "Negative: Empty tile (no mounds)", "category": "null"},
        {"path": "examples/null_tile_03.png", "label": "Negative: Empty tile (no mounds)", "category": "null"},
        {"path": "examples/hardneg_standalone_benchmark.png", "label": "Negative: Benchmark ALONE (no mound)", "category": "hard_negative"},
        {"path": "examples/hardneg_standalone_triangulation.png", "label": "Negative: Triangulation Point ALONE (no mound)", "category": "hard_negative"}
    ]
}
```

---

#### verify_image-only.json

```json
{
    "version": "verify_image-only",
    "description": "Two-Stage Verifier (Stage 2). Precision-focused verification.",
    "hypothesis": "H2",
    "model": "gemini-3-flash",
    "instruction_file": "verify_image-only.md",
    "temperature": 1.0,
    "max_output_tokens": 8192,
    "verification_threshold": 0.51,
    "majority_vote_fraction": 0.5,
    "examples": [
        {"path": "examples/canonical_burial_mound.png", "label": "Positive: Burial Mound (Kurgan)", "category": "canonical"},
        {"path": "examples/canonical_settlement_mound.png", "label": "Positive: Settlement Mound", "category": "canonical"},
        {"path": "examples/canonical_triangulation_mound.png", "label": "Positive: Triangulation Point ON Mound", "category": "canonical"},
        {"path": "examples/canonical_benchmark_mound.png", "label": "Positive: Benchmark ON Mound", "category": "canonical"},
        {"path": "examples/null_tile_01.png", "label": "Negative: Empty tile (no mounds)", "category": "null"},
        {"path": "examples/null_tile_02.png", "label": "Negative: Empty tile (no mounds)", "category": "null"},
        {"path": "examples/null_tile_03.png", "label": "Negative: Empty tile (no mounds)", "category": "null"},
        {"path": "examples/hardneg_standalone_benchmark.png", "label": "Negative: Benchmark ALONE (no mound)", "category": "hard_negative"},
        {"path": "examples/hardneg_standalone_triangulation.png", "label": "Negative: Triangulation Point ALONE (no mound)", "category": "hard_negative"}
    ]
}
```

---

## Part 3: Runtime Parameters

The following parameters are controlled at runtime rather than in configuration files:

| Parameter | Values | Hypothesis | Notes |
|-----------|--------|------------|-------|
| Temperature | 0.0, 0.7, 1.0, 1.3 | H7 | Overrides config file default |
| Model | gemini-3-flash, gemini-3-pro, claude-4.5-sonnet, gpt-5.2-thinking | H6, H14 | Overrides config file value |
| Passes | 1, 5, 10, 30 | H3 | Number of detection runs per tile |
| Voting threshold | 1 to N | H3 | Minimum votes for detection acceptance |

**Note**: Temperature escalation trigger (H7): If T=1.3 outperforms T=1.0, additional tests at T=1.6 and T=2.0 will be conducted.

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

*Document version: 2.3*
*Created: 2026-01-02*
*Updated: 2026-01-07*

**Changelog:**

- v2.3: Hypothesis renumbering alignment with preregistration.md v4.0 — H7→H5 (hard negatives now 3 levels), H9→H7 (temperature now 4 levels), H5→H4 (ordering), H3→H2 (two-stage), H6→H9 (diversity exploratory), H8→H6 (transfer), H4→H3 (voting), H10 merged into H2; config count reduced from 16 to 9; text-only tested at T=1.0 only
- v2.2: H2 elaboration clarification — both brief and verbose include HP edge case guidance at different detail levels (brief = terse mention, verbose = detailed guidance); orthogonality is H2 (detail level for positives) vs H7 (presence of negatives); aligned with preregistration.md v3.5 factorial restructure
- v2.1: Final review fixes — corrected config count explanation (20→16 due to text-only constraints); aligned Phase 1 baseline with preregistration (5 passes, ≥3/5 threshold); fixed hard negative labels for Images-only condition (minimal "Negative" labels); added hard positive placeholders to example configs; added H10 verification prompt placeholder (Section 1.7); added H5 canonical-last example config; fixed verifier prompt to use placeholder notation
- v2.0: Major restructure — 10 instruction files (5 M/E × 2 exclusion variants), 16 config files (reflecting text-only constraints); renamed "elaborate" to "verbose"; clarified orthogonal separation between H2 (edge case guidance for FNs) and H7 (exclusion guidance for FPs); added legend-derived hard negatives; flagged empirically-derived content as TBD
- v1.1: Added T=1.3 to temperature values; removed stale H2 reference from H6 construction procedure
- v1.0: Initial documentation
