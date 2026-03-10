# Mound Detection — High-Recall Mode

Detect all burial mound symbols in this Soviet topographic map tile.

**Flag any feature that could plausibly be a burial mound, even if uncertain. It is better to include a doubtful candidate than to miss a real one.**

## Target Symbols

All mound symbols share one diagnostic feature: short **rays (hachures) radiating OUTWARD** from a central shape, forming a "sunburst" or "gear" pattern. This indicates elevated terrain.

**Subtypes to detect:**

- **Burial mound (kurgan)**: Orange-brown hollow circle with rays. ~10-20 pixels diameter. Often accompanied by elevation numbers or "кург." label.
- **Settlement mound**: Orange-brown, larger and often oval/irregular. More rays (8-15).
- **Triangulation point on mound**: Black triangle with central dot, surrounded by black rays.
- **Benchmark on mound**: Black square with central dot, surrounded by black rays.

The **rays pointing outward** are the primary diagnostic feature. However, rays may be faint, partially occluded, or degraded. If a symbol has the right central shape in the expected colour and you can see *any* suggestion of outward marks — even incomplete — include it.

## When in Doubt, Include

The following cases should be flagged as detections rather than skipped:

- Faded or low-contrast symbols with the right shape but weak colour
- Partially occluded symbols where lines or text cross the mound
- Small or atypical symbols resembling mound subtypes
- Features near "кург." labels even without a clear symbol

The verifier stage will reject false positives. Your job is to ensure no real mound is missed.

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
