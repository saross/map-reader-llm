# Mound Detection (Image-Only with Terse Exclusion)

Scan the Target Image. Mark all symbols that look like the Positive examples.

## Exclusion Guidance

Rays are key: Shapes without visible radiating rays are not mounds. Consider occlusion or degradation before excluding.

**DO NOT mark:**

- Standalone triangulation points (black triangle, NO rays)
- Standalone benchmarks (black square/circle, NO rays)
- Spot heights, bridge markers, or other simple dots

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
