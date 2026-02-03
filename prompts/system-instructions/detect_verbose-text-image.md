# Mound Detection

Detect all burial mound symbols in this Soviet topographic map tile.

This is a Soviet 1:50,000 military topographic map from the Cold War era. Archaeological mounds were marked as navigation landmarks using standardised symbology.

## Core Diagnostic

All mound symbols share one essential feature: **short rays (hachures) radiating OUTWARD** from a central shape. This "sunburst" or "gear" pattern indicates elevated terrain, distinguishing mounds from excavations (which have inward-pointing marks).

The rays are the primary diagnostic. Any symbol with outward-radiating rays is a mound candidate, regardless of central shape.

Base all detections on the visual sunburst diagnostic only. Map text, labels, and abbreviations near a candidate do not confirm or deny the presence of a mound.

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

**Phase 1 — Identify sunburst pattern:**

1. **Check for rays**: Are there short marks radiating from a central point? No rays → not a mound.

2. **Check ray direction**: Do rays point OUTWARD (elevated terrain) or INWARD (excavation)? Inward → not a mound.

3. **Consider occlusion**: Lines in various colours (black, red, brown, blue) or text labels may partially obscure symbols. Interference ranges from a partial clip of one or two rays to a line splitting the symbol in half. If the sunburst pattern remains discernible, include the detection.

4. **Consider degradation**: Map scanning may have faded or distorted symbols. Faint or slightly asymmetrical ray patterns still qualify if the overall sunburst structure is discernible.

**Phase 2 — Classify subtype:**

5. **Assess central shape**: Circle, oval, triangle, or square? This determines subtype classification.

6. **Check colour**: Orange-brown indicates plain mound; black indicates mound with survey marker.

## Handling Edge Cases

### Partially Occluded Symbols
Lines and text frequently cross mound symbols:
- Black or red lines may clip or split the symbol
- Brown lines may merge with orange-brown symbols, obscuring the boundary
- Blue lines may bisect the symbol, separating rays on either side
- Text characters or numbers may overlap the central shape or rays

Interference ranges from a partial clip of one or two rays to a line splitting the entire symbol in half. Look for rays on either side of the interfering feature — if the sunburst pattern remains discernible, mark the detection.

### Clustered Mounds
Mounds commonly appear in groups where individual symbols vary in prominence — apply the ray diagnostic independently to each candidate. Each distinct sunburst centre is a separate mound. Provide individual bounding boxes even if symbols touch or overlap. Do not merge adjacent mounds into a single box.

### Faded or Degraded Symbols
Scanning artefacts may cause:
- Incomplete ray patterns (some rays faint or missing)
- Colour bleeding or fading
- Slight geometric distortion

Look for the characteristic sunburst structure even if imperfect.

### Symbols Amid Dense Features
Mound symbols may appear amid visually complex surroundings — near other map symbols, at intersections of lines, or in areas with dense annotation. Apply the outward-radiating ray diagnostic regardless of surrounding context. A symbol that satisfies the sunburst pattern is a detection even if neighbouring features are visually prominent.

## Reference Examples

If reference examples are provided, compare uncertain cases against them. Each reference image is centred on the feature being labelled — the target symbol for Positive examples, the confusable feature for Negative examples. Positive examples demonstrate the target symbols; negative examples show features that are NOT mounds.

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
