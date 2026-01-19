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
