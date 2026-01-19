# Prompt Revision Instructions for Claude Code

**Document purpose**: Complete specification for revising the 11 detection instruction files to achieve text-modality consistency and optimal prompt construction.

**Prepared by**: Opus 4.5 in consultation with Shawn Ross
**Date**: 2026-01-20

---

## 1. Design Requirements

### 1.1 Experimental Constraints

The H1 hypothesis tests whether modality and elaboration level affect detection performance. This requires:

1. **Text-modality consistency**: Identical positive-guidance text across modalities
   - `detect_brief-text.md` must equal `detect_brief-text-image.md` (and its H5 variants)
   - `detect_verbose-text.md` must equal `detect_verbose-text-image.md` (and its H5 variants)

2. **H5 orthogonality**: Exclusion guidance is controlled separately
   - Base files (no suffix): No exclusion text
   - `_terse` suffix: Terse exclusion block added
   - `_verbose` suffix: Verbose exclusion block added

3. **Word count targets** (for 3-4× elaboration ratio):
   - Minimal (image-only): ~50 words
   - Brief: 150-200 words
   - Verbose: 500-700 words

### 1.2 Prompt Construction Principles

Based on current prompt engineering evidence:

1. **Action-first opening**: Lead with the detection task, not background context
2. **Model-oriented descriptions**: Use pixel measurements (~10-20 pixels), not physical units (2-4mm)
3. **Unified diagnostic**: "Sunburst with outward-radiating rays" is the core criterion; subtypes are secondary classification
4. **Conditional reference framing**: "If reference examples are provided..." works in both text-only and text+image conditions
5. **No recall bias**: Remove "default to inclusion" / "err on the side of detection" to measure natural precision-recall tradeoff
6. **No role preamble**: Except brief contextual sentence in verbose variant only
7. **Output format at end**: Recency effect keeps schema salient

---

## 2. Base Templates

### 2.1 Minimal Template (Image-Only Base)

**Target**: ~50 words
**Used by**: `detect_image-only.md`, `detect_image-only_terse.md`, `detect_image-only_verbose.md`

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

**Word count**: ~65 words (excluding JSON example)

---

### 2.2 Brief Template

**Target**: 150-200 words
**Used by**: `detect_brief-text.md`, `detect_brief-text-image.md`, `detect_brief-text-image_terse.md`, `detect_brief-text-image_verbose.md`

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

**Word count**: ~185 words (excluding JSON example)

---

### 2.3 Verbose Template

**Target**: 500-700 words
**Used by**: `detect_verbose-text.md`, `detect_verbose-text-image.md`, `detect_verbose-text-image_terse.md`, `detect_verbose-text-image_verbose.md`

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

**Word count**: ~580 words (excluding JSON example)

---

## 3. Exclusion Blocks

These blocks are **appended** to the base templates for `_terse` and `_verbose` H5 variants. They are inserted immediately before the "Output Format" section.

### 3.1 Terse Exclusion Block

**Used by**: `detect_image-only_terse.md`, `detect_brief-text-image_terse.md`, `detect_verbose-text-image_terse.md`

```markdown
## Exclusion Guidance

Rays are essential: shapes without visible radiating rays are not mounds.

**Do NOT mark:**
- Standalone triangulation points (black triangle, no rays)
- Standalone benchmarks (black square/circle, no rays)
- Spot heights (dot with elevation number, no rays)
- Quarry/pit symbols (marks pointing INWARD, not outward)
- Infrastructure markers (dots on roads, bridges, rivers)
```

**Word count**: ~55 words

---

### 3.2 Verbose Exclusion Block

**Used by**: `detect_image-only_verbose.md`, `detect_brief-text-image_verbose.md`, `detect_verbose-text-image_verbose.md`

```markdown
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
```

**Word count**: ~275 words

---

## 4. File Assembly Matrix

| Output File | Base Template | Exclusion Block |
|-------------|---------------|-----------------|
| `detect_image-only.md` | Minimal | None |
| `detect_image-only_terse.md` | Minimal | Terse |
| `detect_image-only_verbose.md` | Minimal | Verbose |
| `detect_brief-text.md` | Brief | None |
| `detect_brief-text-image.md` | Brief | None |
| `detect_brief-text-image_terse.md` | Brief | Terse |
| `detect_brief-text-image_verbose.md` | Brief | Verbose |
| `detect_verbose-text.md` | Verbose | None |
| `detect_verbose-text-image.md` | Verbose | None |
| `detect_verbose-text-image_terse.md` | Verbose | Terse |
| `detect_verbose-text-image_verbose.md` | Verbose | Verbose |

**Assembly rule**: Insert exclusion block immediately before "## Output Format" section.

---

## 5. Verification Checklist

After implementation, verify:

- [ ] `detect_brief-text.md` is character-for-character identical to `detect_brief-text-image.md`
- [ ] `detect_verbose-text.md` is character-for-character identical to `detect_verbose-text-image.md`
- [ ] All three `_terse` files have identical exclusion blocks
- [ ] All three `_verbose` files have identical exclusion blocks
- [ ] Word counts are within targets:
  - Minimal base: 50-80 words
  - Brief base: 150-200 words
  - Verbose base: 500-700 words
  - Terse exclusion: ~50-60 words
  - Verbose exclusion: ~250-300 words
- [ ] No "default to inclusion" or "err on the side of detection" language
- [ ] No role preambles except contextual sentence in verbose
- [ ] All files have identical JSON output format block

---

## 6. Preregistration Documentation

Add the following section to `preregistration.md` (suggested location: Section 8.3 or new subsection):

```markdown
#### 8.3.X Prompt Construction Rationale

The detection prompts were constructed following evidence-based prompt engineering principles:

**Action-first structure**: All prompts lead with the detection task ("Detect all burial mound symbols...") rather than role preambles or background context. Research indicates that VLMs attend strongly to opening content, making task-first framing more effective than persona-based approaches.

**Model-oriented descriptions**: Visual descriptions use pixel measurements (~10-20 pixels) rather than physical units (2-4mm at map scale) since the model processes pixel data directly.

**Unified diagnostic**: All mound types share a single diagnostic feature (outward-radiating rays forming a "sunburst" pattern). Prompts emphasise this unified criterion rather than fragmenting attention across parallel symbol descriptions. Subtype classification is secondary to detection.

**Conditional reference framing**: To maintain identical text across text-only and text+image modalities, reference examples are handled with conditional phrasing: "If reference examples are provided, compare uncertain cases against them." This statement is true in both conditions and provides appropriate guidance when images are present.

**No recall bias**: Prompts do not include instructions to "err on the side of detection" or "default to inclusion." This allows measurement of the model's natural precision-recall tradeoff at each M/E level. The consensus voting mechanism (H3) provides recall recovery for operational deployment.

**Elaboration ratio**: Brief (~175 words) and verbose (~580 words) prompts maintain a ~3.3× ratio, within the 2.5-4.5× range recommended for detecting elaboration effects in prompt engineering studies.

**H5 orthogonality**: Exclusion guidance for hard negatives is controlled entirely by the H5 factor (instruction file suffix: `_terse`, `_verbose`), not by the M/E elaboration level. Base prompts at all M/E levels contain no exclusion guidance, ensuring clean separation of positive guidance (H1) from negative guidance (H5).
```

---

## 7. Implementation Notes

1. All files are in `/prompts/` directory
2. Preserve the exact JSON format block (normalised coordinates 0-1000)
3. Use consistent markdown formatting (## for main sections, ### for subsections)
4. Ensure consistent line endings (LF, not CRLF)
5. No trailing whitespace

---

*End of specification*
