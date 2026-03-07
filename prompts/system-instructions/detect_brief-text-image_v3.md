# Kurgan Symbol Recognition

Find all kurgan indicators in this image.

## Target Symbols

Kurgan and related mound symbols are distinguished by one consistent visual cue: short **ray-like marks (hachures) projecting OUTWARD** from a central shape, giving a "spoked" or "radiant" appearance. This marks a topographic rise.

**Subtypes to find:**

- **Kurgan**: Orange-brown open circle with outward-projecting ray marks. Size is typically 10–20 pixels. Often situated near height values or labelled "кург." in Cyrillic.
- **Settlement mound**: Orange-brown, usually larger, with an oval or irregular boundary. Surrounded by a greater number of ray marks (8–15).
- **Triangulation point on kurgan**: Black triangle with a central dot, bordered by black ray marks.
- **Benchmark on kurgan**: Black square with a central dot, bordered by black ray marks.

**Outward-projecting rays** are the defining characteristic. Symbols that lack visible rays are not kurgans.

## Guidelines

1. Supply a distinct bounding box for each symbol, including adjacent or clustered symbols.
2. Symbols partly concealed by overlying lines, shapes, or labels should be reported if the radiant pattern remains visible.
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
