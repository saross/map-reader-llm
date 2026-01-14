# Detection Prompt: Verbose Text+Image with Terse Exclusion Guidance

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

## Exclusion Guidance

Rays are key: Shapes without visible radiating rays are not mounds. Consider occlusion or degradation before excluding.

**DO NOT mark:**

- Standalone triangulation points (black triangle, NO rays)
- Standalone benchmarks (black square/circle, NO rays)
- Spot heights, bridge markers, or other simple dots

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
