# Mound Detection (Image-Only with Verbose Exclusion)

Scan the Target Image. Mark all symbols that look like the Positive examples.

## Exclusion Guidance (Detailed)

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
