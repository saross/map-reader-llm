# Preregistration Appendix: Prompt Documentation

**Companion document to**: `preregistration.md`
**Purpose**: Complete documentation of all system instructions and configuration files
**Status**: Ready for Registration

---

## Overview

This appendix contains the complete text of all prompts used in the study. Prompts are organised into:

1. **System Instructions** — The text instructions provided to the VLM
2. **Configuration Files** — JSON files specifying example ordering, labels, and parameters

All files are stored in the `prompts/` directory of the project repository.

---

## Pre-Holdout Finalisation

The following elements will be finalised before holdout evaluation:

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

The 5 semantically equivalent prompt variants (V1–V5) will be constructed after the optimal base configuration is determined from the main factorial and H2 experiments.

**Construction procedure:**

1. Identify winning configuration (modality, elaboration, hard negatives, ordering, temperature)
2. Use the corresponding prompt template as structural base
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

Before any holdout evaluation, the following will be uploaded to the connected OSF project:

- Final image filenames for all hard examples
- Selection rationale (frequency counts from training evaluation)
- Complete H6 prompt variants (V1–V5)
- Exact ordering for each condition
- Random seeds used

---

## Part 1: System Instructions

### 1.1 Single-Stage Detection Prompts

#### 1.1.1 detect_image-only.md

**Purpose**: Baseline image-only detection with minimal text instruction.
**Used by**: H1 (image-only condition), H5, H7 (baseline), H9
**H6 note**: If image-only is the optimal base configuration, this template's structure will be used for H6 V1–V5 variants (with varied content per Section 8.3.3).

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

#### 1.1.2 detect_text-only.md

**Purpose**: Text-only detection with detailed symbol descriptions but no visual examples.
**Used by**: H1 (text condition), H2 (brief text)

```markdown
# Detection Prompt: Text-Only Baseline

You are an expert analyst of Soviet
Topographic Maps and landscape archaeologist. Your goal is to
identify burial mound symbols.

## Target Symbols

Create bounding boxes for all
instances of the following symbols:

### A. Burial Mound (Kurgan)

- **Visual:** A small, hollow **circle**
  with short, radiating **rays** (hachures; spikes) extending outward. Resembles a
  "sunburst", "gear", or "ship's wheel".
- **Colour:** Orange-brown.
- **Context:** Often accompanied by an
  isolated elevation number (e.g., "3",
  "10") or the abbreviation **"кург."**

### B. Settlement Mound

- **Visual:** Similar to a burial mound
  but **larger** and often oval or
  irregular in shape.
- **Colour:** Orange-brown.

### C. Triangulation Point on a Mound

- **Visual:** A hollow **black triangle**
  with a central dot, surrounded by
  radiating rays of a mound.
- **Distinction:** Must have rays.

### D. Benchmark on a Mound

- **Visual:** A hollow **black square**
  with a central dot, surrounded by
  radiating rays of a mound.
- **Distinction:** Must have rays.

## Handling Occlusion

Symbols may be partially obscured by
lines (roads, contours, grid lines) or
text. Focus on identifying the
characteristic "sunburst" shape.

## Separating Clusters

Symbols may appear close together. Each
distinct "sunburst" centre represents a
separate mound. Provide individual
bounding boxes for each.

## When Uncertain

Include borderline cases rather than
missing genuine mounds.

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

#### 1.1.3 detect_text-only_hardneg.md

**Purpose**: Text-only detection with hard negative exclusion criteria.
**Used by**: H7 (text-only + hard negatives)

```markdown
# Detection Prompt: Text-Only with Hard Negatives

You are an expert analyst of Soviet
Topographic Maps and landscape archaeologist. Your goal is to
identify burial mound symbols.

## Target Symbols

Create bounding boxes for all
instances of the following symbols:

### A. Burial Mound (Kurgan)

- **Visual:** A small, hollow **circle**
  with short, radiating **rays** (hachures; spikes) extending outward. Resembles a
  "sunburst", "gear", or "ship's wheel".
- **Colour:** Orange-brown.
- **Context:** Often accompanied by an
  isolated elevation number (e.g., "3",
  "10") or the abbreviation **"кург."**

### B. Settlement Mound

- **Visual:** Similar to a burial mound
  but **larger** and often oval or
  irregular in shape.
- **Colour:** Orange-brown.

### C. Triangulation Point on a Mound

- **Visual:** A hollow **black triangle**
  with a central dot, surrounded by
  radiating rays of a mound.
- **Distinction:** Must have rays.

### D. Benchmark on a Mound

- **Visual:** A hollow **black square**
  with a central dot, surrounded by
  radiating rays of a mound.
- **Distinction:** Must have rays.

## Exclusion Criteria (CRITICAL)

The following symbols are easily
confused with mounds. **DO NOT mark:**

### Triangulation Point (standalone)

- **Visual:** Hollow black triangle with
  central dot, but **NO radiating rays**.

### Benchmark (standalone)

- **Visual:** Hollow black square/circle
  with crosshairs, but **NO radiating rays**.

### Bridge/Culvert Dots

- **Visual:** Simple black dots on roads,
  rivers, or canals. NO rays.

### Spot Heights

- **Visual:** Simple dots (black/brown)
  with elevation numbers. NO rays.

### Quarry/Pit Symbols

- **Visual:** Circular shapes with rays
  pointing **INWARD**. Mound rays always point
  OUTWARD.

## Handling Occlusion

Symbols may be partially obscured by
lines (roads, contours, grid lines) or
text. Focus on identifying the
characteristic "sunburst" shape.

## Separating Clusters

Symbols may appear close together. Each
distinct "sunburst" centre represents a
separate mound. Provide individual
bounding boxes for each.

## When Uncertain

Include borderline cases rather than
missing genuine mounds.

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

#### 1.1.4 detect_text-image.md

**Purpose**: Combined text and image prompt with reference examples.
**Used by**: H1 (text+image condition), H2 (brief)
**H6 note**: If text+image is the optimal base configuration, this template's structure will be used for H6 V1–V5 variants (with varied content per Section 8.3.3).

```markdown
# Detection Prompt: Text+Image Baseline

You are an expert analyst of Soviet
Topographic Maps and landscape archaeologist. Your goal is to find symbols that **visually
match** the provided Positive examples.

## Reference Examples

You are provided with labelled images:

- **Positive examples** show mound symbols
  to detect (burial mounds, settlement
  mounds, and survey markers on mounds)
- **Negative examples** show areas or
  symbols that are NOT mounds

## Task

Scan the **Target Image** and create
bounding boxes for all instances that
visually match the Positive reference
symbols.

## Guidelines

1. **Visual Match:** Symbols may be
   rotated, degraded, or intersected by
   lines. Focus on the "sunburst" shape
   with short rays (hachures; spikes) extending OUTWARD.

2. **Separate Clusters:** Provide
   individual boxes for each symbol.

3. **Refer to Examples:** Compare uncertain
   cases to Positive references.

4. **Default to inclusion:** Include borderline
   cases rather than missing genuine mounds.

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

#### 1.1.5 detect_text-image_hardneg.md

**Purpose**: Combined text and image prompt with hard negative guidance.
**Used by**: H7 (text+image + hard negatives)

```markdown
# Detection Prompt: Text+Image with Hard Negatives

You are an expert analyst of Soviet
Topographic Maps and landscape archaeologist. Your goal is to find symbols that **visually
match** the provided Positive examples.

## Reference Examples

You are provided with labelled images:

- **Positive examples** show mound symbols
  to detect (burial mounds, settlement
  mounds, and survey markers on mounds)
- **Negative examples** show areas or
  symbols that are NOT mounds

## Task

Scan the **Target Image** and create
bounding boxes for all instances that
visually match the Positive reference
symbols.

## Guidelines

1. **Visual Match:** Symbols may be
   rotated, degraded, or intersected by
   lines. Focus on the "sunburst" shape
   with short rays (hachures; spikes) extending OUTWARD.

2. **Separate Clusters:** Provide
   individual boxes for each symbol.

3. **Refer to Examples:** Compare uncertain
   cases to Positive references.

4. **Default to inclusion:** Include borderline
   cases rather than missing genuine mounds.

## Exclusion Guidance

Rays are key: Shapes without visible
radiating rays are not mounds.
Consider occlusion or degradation before
excluding.

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

### 1.2 Elaborate Prompts (H2)

#### 1.2.1 detect_text-only_elaborate.md

**Purpose**: Extended text-only prompt with comprehensive symbol descriptions and decision procedures.
**Used by**: H2 (elaborate text condition)
**Word count**: ~700 words (vs ~200 for brief version)

```markdown
# Detection Prompt: Text-Only Elaborate

You are an expert analyst of Soviet
Topographic Maps from the 1950s-1980s, and a seasoned landscape archaeologist.
Your goal is to identify symbols on the Soviet military map that represent burial
mounds (kurgans; tumuli), settlement mounds (tells), including composite symbols, positioned across the Bulgarian
landscape.

## Background: Soviet Cartographic
Conventions

Soviet military topographic maps used
standardised symbology across the USSR
and Eastern Bloc / Warsaw Pact nations. Archaeological
mounds were marked because they served
as useful landmarks for navigation and orientation, and they could be militarily useful, e.g., as lookout points or cover. The symbol design
emphasises the elevated, roughly circular
nature of these features through
radiating rays (hachures; spikes).

## Target Symbols

Identify the bounding boxes for all
instances of the following symbols:

### A. Burial Mound (Kurgan)

- **Visual:** A small, hollow **circle**
  with short, radiating **rays** (hachures; spikes)
  extending outward. Resembles a
  "sunburst", "gear", or "ship's wheel".
- **Colour:** Orange-brown (same colour
  as contour lines, indicating relief).
- **Size:** Typically 2-4mm diameter at
  map scale, which translates to roughly
  10-20 pixels in a 448×448 tile.
- **Ray characteristics:** Usually 6-8
  rays of approximately equal length,
  radiating evenly from the central
  circle.
- **Context:** Often accompanied by an
  isolated elevation number (e.g., "3",
  "10") indicating height in metres, or
  the Cyrillic abbreviation **"кург."**
  ("kurgan").
- **Landscape position:** Typically
  located on elevated terrain, ridges,
  hilltops, or other prominent landscape
  positions where ancient peoples chose
  to bury their dead. May also be found in flat, open areas, where large examples dominate the landscape.
- **Grouping:** Mounds may appear in groups (necropoleis), which may contain mounds of different sizes.

### B. Settlement Mound

- **Visual:** Similar to a burial mound
  but **larger** and often oval or
  irregular in shape rather than
  circular. Radiating ticks point
  outward from the perimeter.
- **Ray characteristics:** Rays appear similar to burial mounds, but sometimes larger, and often more rays are present (often 8-15).
- **Colour:** Orange-brown.
- **Size:** Larger than burial mounds,
  may be 5-10mm at map scale.
- **Shape:** May be elongated or
  irregular, reflecting the accumulated
  debris of ancient settlements.

### C. Triangulation Point on a Mound

- **Visual:** A hollow **black triangle**
  with a central dot (the geodetic
  survey marker), surrounded by the
  characteristic radiating
  rays of a mound, also in black. Often have 6-12 rays. Size similar to or slightly larger than a typical 'base' burial mound, since large, prominent mounds were often chosen for triangulation points.
- **Interpretation:** Soviet surveyors
  placed triangulation markers on mounds
  because they provided elevated, stable
  positions with good sight lines.
- **Critical distinction:** The symbol
  MUST have radiating black rays around the
  triangle.

### D. Benchmark on a Mound

- **Visual:** A hollow **black square**
  (or circle with crosshairs) with a
  central dot, surrounded by the
  characteristic radiating
  rays of a mound, also in black. Often have 8 rays. Size similar to or slightly larger than a typical 'base' burial mound, since large, prominent mounds were often chosen for benchmarks.
- **Interpretation:** Similar to
  triangulation points, benchmarks were
  placed on mounds for stability and
  visibility.
- **Critical distinction:** The symbol
  MUST have radiating black rays around the
  square/circle.

## Detection Criteria

The **radiating rays** (hachures; spikes) are the primary
and essential diagnostic feature. All
mound symbols, of whatever type, share this characteristic
regardless of what (if anything) is
superimposed at the centre.

### Ray Pattern Analysis

1. **Direction:** Rays extend OUTWARD
   from a central point or oval,
   indicating elevated terrain (like
   contour hachures for hills).
2. **Count:** Typically 8-15 rays,
   roughly evenly spaced around the
   perimeter. Count depends on symbol type (burial mound, settlement mound, burial mound with triangulation point, burial mound with benchmark)
3. **Length:** Approximately equal to
   or slightly longer than the diameter
   of the central shape.
4. **Consistency:** Rays should be
   roughly equal in length and evenly spaced; highly
   irregular patterns may indicate other
   features (noting that some areas of the map scanned poorly and may have some distortion)

### Colour Analysis

- **Orange-brown symbol:** Indicates a "plain" burial or settlement mound.
- **Black symbol:** Indicates a burial mound with
  survey marker (triangulation point or
  benchmark) placed on top of the mound.
- Each symbol is a single colour, either orange-brown or black.

## Decision Procedure

When uncertain whether a feature is a
mound, apply this systematic checklist:

1. **Check for rays:** Are there short
   rays (hachures; spikes) radiating outward from a central
   point? No rays = not
   a mound.

2. **Check ray direction:** Do the rays
   point OUTWARD (elevation/mound) or
   INWARD (excavation/quarry)? Burial or settlement mound rays ALWAYS point outwards.

3. **Check central shape:** Is there a
   circle, oval, triangle, or square at
   the centre? The central shape helps
   classify the mound subtype.

4. **Check colour:** Are the symbols
   orange-brown ("plain" burial or settlement mound with no survey infrastructure) or black
   (mound with triangulation point or benchmark)?

5. **Consider occlusion:** Roads,
   contours, rivers, or text may obscure
   part of the symbol. If some rays, or partial rays, are
   visible and the overall pattern
   matches, include the detection.

6. **Consider degradation:** Map
   scanning or printing may have faded or distorted
   some symbols. Look for faint or somewhat asymmetrical ray
   patterns even if not perfectly symmetrical or fully distinct.

7. **When still uncertain:** Err on the
   side of detection. It is better to
   include a borderline case than to
   miss a genuine mound.

## Handling Occlusion

Symbols are frequently intersected by
other map features:

- **Roads:** Black or red lines may
  cross through a mound symbol.
- **Contour lines:** Brown lines at
  similar colour may partially merge
  with mound rays.
- **Grid lines:** Blue coordinate grid
  lines may overlay symbols.
- **Text labels:** Cyrillic place names
  or elevation numbers may obscure parts
  of symbols.

In all cases, focus on identifying the
characteristic "sunburst" pattern. If
you can see rays extending outward from
a central point, even partially, mark
the detection.

## Separating Clusters

Mounds often appear in groups (cemetery
fields; necropoleis). When symbols are close together:

- Each distinct "sunburst" centre
  represents a separate mound.
- Provide individual bounding boxes for
  each symbol, even if they touch.
- Do not merge adjacent mounds into a
  single large box.

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

#### 1.2.2 detect_text-only_elaborate_hardneg.md

**Purpose**: Extended text-only prompt with comprehensive exclusion criteria.
**Used by**: H2 (elaborate text + hard negatives)
**Word count**: ~1,200 words

*[Full content available in repository — extends detect_text-only_elaborate.md with detailed exclusion criteria for 8 confusable symbol types: triangulation points, benchmarks, spot heights, quarry/pit symbols, bridge/culvert markers, contour artefacts, vegetation symbols, and well symbols]*

---

#### 1.2.3 detect_text-image_elaborate.md

**Purpose**: Extended text+image prompt with decision procedures.
**Used by**: H2 (elaborate text+image)

```markdown
# Detection Prompt: Text+Image Elaborate

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

#### 1.2.4 detect_text-image_elaborate_hardneg.md

**Purpose**: Extended text+image prompt with explicit exclusion criteria.
**Used by**: H2 (elaborate text+image + hard negatives)

*[Full content available in repository — extends detect_text-image_elaborate.md with exclusion criteria for 6 confusable symbol types]*

---

### 1.3 Two-Stage Pipeline Prompts (H3)

#### 1.3.1 propose_image-only.md

**Purpose**: High-recall proposer stage for two-stage pipeline.
**Used by**: H3 (Stage 1)

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

#### 1.3.2 verify_image-only.md

**Purpose**: Precision-focused verifier stage for two-stage pipeline.
**Used by**: H3 (Stage 2)

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
    "reasoning": "Brief description of visual features observed.",
    "mound_probability": 0.0
}

## Scoring Guide

- **0.9-1.0**: Clear mound symbol with radiating rays (hachures; spikes).
- **0.6-0.8**: Likely mound, some ambiguity or occlusion.
- **0.3-0.5**: Uncertain, could be mound or similar feature.
- **0.0-0.2**: Not a mound (noise, text, isolated marker, building).
```

---

## Part 2: Configuration Files

### 2.1 Configuration Schema

All configuration files follow this JSON schema:

```json
{
    "version": "string — unique identifier",
    "description": "string — human-readable description",
    "hypothesis": "string — optional, which hypothesis this tests",
    "model": "string — model identifier (e.g., 'gemini-3-flash')",
    "instruction_file": "string — path to system instruction .md file",
    "temperature": "number — generation temperature",
    "max_output_tokens": "number — maximum output tokens",
    "examples": [
        {
            "path": "string — path to example image",
            "label": "string — label shown to model",
            "category": "string — optional, 'canonical'/'null'/'hard_positive'/'hard_negative'"
        }
    ],
    "ordering_note": "string — optional, explains example ordering"
}
```

---

### 2.2 Baseline Configurations

#### detect_image-only.json

**Hypothesis**: H5-A (Canonical-first ordering)

```json
{
    "version": "detect_image-only",
    "description": "H5-A: Canonical-first ordering. Legend positives first, then nulls. Hard examples (when added) follow legend positives/negatives respectively.",
    "hypothesis": "H5-A",
    "model": "gemini-3-flash",
    "instruction_file": "detect_image-only.md",
    "temperature": 1.0,
    "max_output_tokens": 8192,
    "examples": [
        {"path": "neutral/example_01.png", "label": "Positive", "category": "canonical"},
        {"path": "neutral/example_02.png", "label": "Positive", "category": "canonical"},
        {"path": "neutral/example_03.png", "label": "Positive", "category": "canonical"},
        {"path": "neutral/example_04.png", "label": "Positive", "category": "canonical"},
        {"path": "neutral/example_05.png", "label": "Negative", "category": "null"},
        {"path": "neutral/example_06.png", "label": "Negative", "category": "null"},
        {"path": "neutral/example_07.png", "label": "Negative", "category": "null"}
    ],
    "ordering_note": "Canonical-first: legend positives, then nulls. Hard examples (when added) inserted after legend items of same polarity."
}
```

---

#### detect_text-image.json

**Hypothesis**: H1 (Text+image condition)

```json
{
    "version": "detect_text-image",
    "description": "Text + Image baseline. Neutral filenames, descriptive labels, no hard negatives.",
    "model": "gemini-3-flash",
    "instruction_file": "detect_text-image.md",
    "temperature": 1.0,
    "max_output_tokens": 8192,
    "examples": [
        {"path": "neutral/example_01.png", "label": "Positive: Burial Mound (Kurgan). Sunburst/gear shape with radiating spikes."},
        {"path": "neutral/example_02.png", "label": "Positive: Settlement Mound. Larger, irregular shape with radiating ticks."},
        {"path": "neutral/example_03.png", "label": "Positive: Triangulation Point ON Mound. Black triangle surrounded by mound rays."},
        {"path": "neutral/example_04.png", "label": "Positive: Benchmark ON Mound. Black square surrounded by mound rays."},
        {"path": "neutral/example_05.png", "label": "Negative: Empty tile. No mounds present."},
        {"path": "neutral/example_06.png", "label": "Negative: Empty tile. No mounds present."},
        {"path": "neutral/example_07.png", "label": "Negative: Empty tile. No mounds present."}
    ]
}
```

---

### 2.3 Ordering Variant Configurations (H5)

#### detect_image-only_canonical-last.json

**Hypothesis**: H5-B (Canonical-last ordering)

```json
{
    "version": "detect_image-only_canonical-last",
    "description": "H5-B: Canonical-last ordering. Hard examples (when added) first, then legend positives/negatives. Skeleton uses reversed block order.",
    "hypothesis": "H5-B",
    "model": "gemini-3-flash",
    "instruction_file": "detect_image-only.md",
    "temperature": 1.0,
    "max_output_tokens": 8192,
    "examples": [
        {"path": "neutral/example_05.png", "label": "Negative", "category": "null"},
        {"path": "neutral/example_06.png", "label": "Negative", "category": "null"},
        {"path": "neutral/example_07.png", "label": "Negative", "category": "null"},
        {"path": "neutral/example_01.png", "label": "Positive", "category": "canonical"},
        {"path": "neutral/example_02.png", "label": "Positive", "category": "canonical"},
        {"path": "neutral/example_03.png", "label": "Positive", "category": "canonical"},
        {"path": "neutral/example_04.png", "label": "Positive", "category": "canonical"}
    ],
    "ordering_note": "When hard examples are added: [hard_positive..., hard_negative..., null..., canonical_positive...]"
}
```

---

#### detect_image-only_random-order.json

**Hypothesis**: H5-C (Random ordering)

*[Uses documented random seed to shuffle all examples]*

---

### 2.4 Hard Negative Configurations (H7)

#### detect_image-only_hardneg.json

```json
{
    "version": "detect_image-only_hardneg",
    "description": "Image-only with hard negatives. Minimal text, neutral filenames.",
    "model": "gemini-3-flash",
    "instruction_file": "detect_image-only.md",
    "temperature": 1.0,
    "max_output_tokens": 8192,
    "examples": [
        {"path": "neutral/example_01.png", "label": "Positive"},
        {"path": "neutral/example_02.png", "label": "Positive"},
        {"path": "neutral/example_03.png", "label": "Positive"},
        {"path": "neutral/example_04.png", "label": "Positive"},
        {"path": "neutral/example_05.png", "label": "Negative"},
        {"path": "neutral/example_06.png", "label": "Negative"},
        {"path": "neutral/example_07.png", "label": "Negative"},
        {"path": "neutral/example_08.png", "label": "Negative"},
        {"path": "neutral/example_09.png", "label": "Negative"}
    ]
}
```

---

#### detect_text-image_hardneg.json

```json
{
    "version": "detect_text-image_hardneg",
    "description": "Text + Image with hard negatives. Neutral filenames, descriptive labels.",
    "model": "gemini-3-flash",
    "instruction_file": "detect_text-image_hardneg.md",
    "temperature": 1.0,
    "max_output_tokens": 8192,
    "examples": [
        {"path": "neutral/example_01.png", "label": "Positive: Burial Mound (Kurgan). Sunburst/gear shape with radiating spikes."},
        {"path": "neutral/example_02.png", "label": "Positive: Settlement Mound. Larger, irregular shape with radiating ticks."},
        {"path": "neutral/example_03.png", "label": "Positive: Triangulation Point ON Mound. Black triangle surrounded by mound rays."},
        {"path": "neutral/example_04.png", "label": "Positive: Benchmark ON Mound. Black square surrounded by mound rays."},
        {"path": "neutral/example_05.png", "label": "Negative: Empty tile. No mounds present."},
        {"path": "neutral/example_06.png", "label": "Negative: Empty tile. No mounds present."},
        {"path": "neutral/example_07.png", "label": "Negative: Empty tile. No mounds present."},
        {"path": "neutral/example_08.png", "label": "Negative: Benchmark ALONE (no mound). Square with dot but NO radiating rays. NOT a mound."},
        {"path": "neutral/example_09.png", "label": "Negative: Triangulation Point ALONE (no mound). Triangle with dot but NO radiating rays. NOT a mound."}
    ]
}
```

---

### 2.5 Two-Stage Pipeline Configurations (H3)

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
    "description": "Two-Stage Verifier (Stage 2). Precision-focused verification of proposals.",
    "model": "gemini-3-flash",
    "instruction_file": "verify_image-only.md",
    "temperature": 1.0,
    "max_output_tokens": 8192,
    "verification_threshold": 0.51,
    "majority_vote_fraction": 0.5,
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

### 2.6 Complete Configuration File List

| Configuration File | Hypothesis | Modality | Hard Neg | Ordering |
|--------------------|------------|----------|----------|----------|
| `detect_image-only.json` | H5-A | image-only | no | canonical-first |
| `detect_image-only_canonical-last.json` | H5-B | image-only | no | canonical-last |
| `detect_image-only_random-order.json` | H5-C | image-only | no | random |
| `detect_image-only_hardneg.json` | H7 | image-only | yes | canonical-first |
| `detect_image-only_canonical-last_hardneg.json` | H5-B, H7 | image-only | yes | canonical-last |
| `detect_image-only_random-order_hardneg.json` | H5-C, H7 | image-only | yes | random |
| `detect_text-only.json` | H1 | text-only | no | canonical-first |
| `detect_text-only_hardneg.json` | H7 | text-only | yes | canonical-first |
| `detect_text-only_elaborate.json` | H2 | text-only | no | canonical-first |
| `detect_text-only_elaborate_hardneg.json` | H2, H7 | text-only | yes | canonical-first |
| `detect_text-image.json` | H1 | text+image | no | canonical-first |
| `detect_text-image_canonical-last.json` | H5-B | text+image | no | canonical-last |
| `detect_text-image_random-order.json` | H5-C | text+image | no | random |
| `detect_text-image_hardneg.json` | H7 | text+image | yes | canonical-first |
| `detect_text-image_canonical-last_hardneg.json` | H5-B, H7 | text+image | yes | canonical-last |
| `detect_text-image_random-order_hardneg.json` | H5-C, H7 | text+image | yes | random |
| `detect_text-image_elaborate.json` | H2 | text+image | no | canonical-first |
| `detect_text-image_elaborate_hardneg.json` | H2, H7 | text+image | yes | canonical-first |
| `propose_image-only.json` | H3 | image-only | yes | canonical-first |
| `verify_image-only.json` | H3 | image-only | yes | canonical-first |

---

## Part 3: Runtime Parameters

The following parameters are controlled at runtime rather than in configuration files:

| Parameter | Values | Hypothesis | Notes |
|-----------|--------|------------|-------|
| Temperature | 0.0, 0.3, 0.7, 1.0 | H9 | Overrides config file value |
| Model | gemini-3-flash, gemini-3-pro, claude-4.5-sonnet, gpt-5.2-thinking | H8, H12 | Overrides config file value |
| Passes | 1, 5, 10, 30 | H4 | Number of detection runs per tile |
| Voting threshold | 1 to N | H4 | Minimum votes for detection acceptance |

---

*Document version: 1.0*
*Created: 2026-01-02*
