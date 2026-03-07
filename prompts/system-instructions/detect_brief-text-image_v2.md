# Tumulus Detection

Detect all tumulus markers on this topographic map.

## Target Symbols

Every tumulus symbol on Soviet topographic maps displays one unmistakable trait: short **hachure strokes radiating OUTWARD** from a central shape, producing a "sun" or "gear-tooth" motif. This cartographic convention signals elevated terrain.

**Subtypes to detect:**

- **Tumulus (kurgan)**: Orange-brown unfilled circle surrounded by hachure strokes. Roughly 10–20 pixels in diameter. Frequently found alongside spot heights or the annotation "кург."
- **Settlement tell**: Orange-brown, generally larger with an oval or irregular perimeter. Displays numerous hachure strokes (8–15).
- **Triangulation station on tumulus**: Black triangle with a dot at its centre, ringed by black hachure strokes.
- **Benchmark on tumulus**: Black square with a dot at its centre, ringed by black hachure strokes.

The **outward-pointing hachure strokes** are mandatory. Any symbol without visible hachure strokes should not be classified as a tumulus.

## Guidelines

1. Each symbol requires its own bounding box, even when symbols appear in tight groups.
2. Include symbols that are partially hidden behind lines, shapes, or text, as long as the hachure pattern can still be discerned.
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
