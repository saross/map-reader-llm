# Two-Stage Detection: Proposer

Detect all candidate burial mound symbols in this Soviet topographic map tile. This is Stage 1 of a two-stage pipeline; a verifier will filter false positives.

## Target Symbols

All mound symbols share one diagnostic feature: short **rays (hachures) radiating OUTWARD** from a central shape, forming a "sunburst" or "gear" pattern. This indicates elevated terrain.

**Subtypes to detect:**

- **Burial mound (kurgan)**: Orange-brown hollow circle with rays. ~10-20 pixels diameter. Often accompanied by elevation numbers or "кург." label.
- **Settlement mound**: Orange-brown, larger and often oval/irregular. More rays (8-15).
- **Triangulation point on mound**: Black triangle with central dot, surrounded by black rays.
- **Benchmark on mound**: Black square with central dot, surrounded by black rays.

The **rays pointing outward** are essential. Symbols without visible rays are not mounds.

## Exclusions

- **Spot heights**: Small black dots (~5-7 pixels) with a nearby elevation number. These are much smaller than mound symbols (≥12 pixels) and have no rays. Do not detect.
- **Water features**: Blue circles or concentric blue rings (wells, springs). Mound symbols are never blue. Do not detect.

## Guidelines

1. Provide individual bounding boxes for each symbol, even in clusters.
2. Symbols may be partially occluded by lines, shapes, or text. Include if the sunburst pattern remains discernible.
3. If reference examples are provided, compare uncertain cases against them. Each reference image is centred on the feature being labelled — the target symbol for Positive examples, the confusable feature for Negative examples.

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
