# Mound Detection

Detect all burial mound symbols in this map tile. Target symbols have a "sunburst" pattern: a central shape with short rays (hachures) radiating OUTWARD.

If reference examples are provided, compare uncertain cases against them. Each reference image is centred on the feature being labelled — the target symbol for Positive examples, the confusable feature for Negative examples.

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
