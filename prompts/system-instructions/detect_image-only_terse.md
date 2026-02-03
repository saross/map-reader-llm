# Mound Detection

Detect all burial mound symbols in this map tile. Target symbols have a "sunburst" pattern: a central shape with short rays (hachures) radiating OUTWARD.

If reference examples are provided, compare uncertain cases against them. Each reference image is centred on the feature being labelled — the target symbol for Positive examples, the confusable feature for Negative examples.

## Exclusion Guidance

Rays are essential: shapes without visible radiating rays are not mounds.

**Do NOT mark:**
- Standalone triangulation points (black triangle, no rays)
- Standalone benchmarks (black square/circle, no rays)
- Spot heights (dot with elevation number, no rays)
- Shapes with marks pointing INWARD toward centre, not outward — may appear in orange-brown, same colour family as mound symbols
- Dots positioned along linear features (no rays)
- Cyrillic map text (e.g., "могила", "кург.") near a shape does not confirm a mound — the sunburst pattern with outward-radiating rays is required
- Round or ovoid shapes in mound-like colours without outward-radiating rays — dark marks may sit within the shape rather than extending outward

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
