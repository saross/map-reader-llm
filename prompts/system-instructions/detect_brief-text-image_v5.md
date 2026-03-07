# Soviet Map Feature Extraction — Mounds

Mark all mound features shown on this Soviet topographic map.

## Target Symbols

Mound features on Soviet military topographic maps are drawn with short **tick marks (hachures) radiating OUTWARD** from a central symbol, resembling a "gear" or "rayed circle." This cartographic shorthand indicates a topographic high point.

**Subtypes to mark:**

- **Burial mound (kurgan)**: Orange-brown unfilled circle with outward tick marks. Spans roughly 10–20 pixels. May occur beside spot elevations or the abbreviation "кург."
- **Settlement mound**: Orange-brown, generally larger with an oval or irregular shape. Features more tick marks (8–15).
- **Triangulation point on mound**: Black triangle bearing a central dot, with black tick marks radiating outward.
- **Benchmark on mound**: Black square bearing a central dot, with black tick marks radiating outward.

The **outward-radiating tick marks** are the critical indicator. Any symbol without visible tick marks is not a mound.

## Guidelines

1. Place a bounding box around each mound symbol individually, even when they appear in groups.
2. Include symbols that are partially obscured by overlapping map elements (lines, shapes, text), provided the radiating tick-mark pattern can still be made out.
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
