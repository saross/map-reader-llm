# Mound Detection

Detect all burial mound symbols in this Soviet topographic map tile.

## Target Symbols

All mound symbols share one diagnostic feature: short **rays (hachures) radiating OUTWARD** from a central shape, forming a "sunburst" or "gear" pattern. This indicates elevated terrain.

**Subtypes to detect:**

- **Burial mound (kurgan)**: Orange-brown hollow circle with rays. ~10-20 pixels diameter. Often accompanied by elevation numbers or "кург." label.
- **Settlement mound**: Orange-brown, larger and often oval/irregular. More rays (8-15).
- **Triangulation point on mound**: Black triangle with central dot, surrounded by black rays.
- **Benchmark on mound**: Black square with central dot, surrounded by black rays.

The **rays pointing outward** are essential. Symbols without visible rays are not mounds.

## Guidelines

1. Provide individual bounding boxes for each symbol, even in clusters.
2. Symbols may be partially occluded by lines, shapes, or text. Include if the sunburst pattern remains discernible.
3. If reference examples are provided, compare uncertain cases against them. Each reference image is centred on the feature being labelled — the target symbol for Positive examples, the confusable feature for Negative examples.

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
