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

If reference examples are provided, compare uncertain cases against them. Each reference image is centred on the feature being labelled — the target symbol for Positive examples, the confusable feature for Negative examples. Positive examples demonstrate the target symbols; negative examples show features that are NOT mounds.

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
