# Mound Detection (Image-Only with Terse Exclusion)

Scan the Target Image. Mark all symbols that look like the Positive examples.

## Exclusion Guidance

Do not mark symbols without visible radiating rays. Standalone triangulation points, benchmarks, spot heights, and bridge markers are NOT mounds.

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
