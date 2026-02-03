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

1. **Check for rays**: Are there short marks radiating from a central point? No rays → not a mound.

2. **Check ray direction**: Do rays point OUTWARD (elevated terrain) or INWARD (excavation)? Inward → not a mound.

3. **Assess central shape**: Circle, oval, triangle, or square? This determines subtype classification.

4. **Check colour**: Orange-brown indicates plain mound; black indicates mound with survey marker.

5. **Consider occlusion**: Lines in various colours (black, red, brown, blue) or text labels may partially obscure symbols. Interference ranges from a partial clip of one or two rays to a line splitting the symbol in half. If the sunburst pattern remains discernible, include the detection.

6. **Consider degradation**: Map scanning may have faded or distorted symbols. Faint or slightly asymmetrical ray patterns still qualify if the overall sunburst structure is discernible.

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

## Exclusion Criteria

The following features are commonly confused with mound symbols. Study any negative reference images carefully.

### Spot Heights
- **Visual**: Simple dot (black or brown) with elevation number (e.g., "185", "247")
- **Key difference**: No hollow shape, no radiating rays — just a dot with a number
- **Test**: Ignore the number. Is there a hollow shape with rays? No → exclude.

### Standalone Triangulation Points
- **Visual**: Black triangle with central dot, but NO surrounding rays
- **Key difference**: No radiating rays extending outward from the triangle
- **Test**: Rays around the triangle? No → survey marker only, exclude. Yes → triangulation ON mound, include.

### Standalone Benchmarks
- **Visual**: Black square or circle with central dot, NO surrounding rays
- **Key difference**: No radiating rays extending outward from the shape
- **Test**: Rays around the shape? No → benchmark only, exclude. Yes → benchmark ON mound, include.

### Inward-Pointing Marks
- **Visual**: Circular or rounded shapes with short marks pointing INWARD toward centre. May appear in orange-brown, the same colour family as mound symbols.
- **Key difference**: Marks point inward, not outward
- **Test**: Which way do marks point? Inward → not a mound, exclude. Outward → mound, include.

### Closed Curved Line Patterns
- **Visual**: Closed curved lines forming roughly circular patterns
- **Key difference**: Smooth, continuous curves with no discrete rays
- **Test**: Discrete rays radiating outward? No → exclude. Yes → mound, include.

### Dots on Linear Features
- **Visual**: Dots positioned along linear features
- **Key difference**: Located on linear features; no rays
- **Test**: Simple dot on a linear feature? → exclude.

### Cyrillic Map Text
- **Visual**: Cyrillic characters (e.g., "могила", "кург.") appearing near a candidate shape
- **Key difference**: Map text near a candidate does not confirm or deny the visual diagnostic. The outward-radiating ray pattern is the sole detection criterion. Actively discount text as evidence when assessing candidates.
- **Test**: Does the shape itself have outward-radiating rays? Text alone never confirms a mound.

### Other Round Shapes in Mound-Like Colours
- **Visual**: Round or ovoid shapes in orange-brown or similar colours, without outward-radiating rays. Dark marks may sit within the shape rather than extending outward.
- **Key difference**: No discrete marks extending outward from the shape
- **Test**: Are there rays radiating outward from the shape? No → exclude, regardless of colour or nearby text.

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
