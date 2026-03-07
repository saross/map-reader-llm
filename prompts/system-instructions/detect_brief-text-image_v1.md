# Burial Mound Identification

Identify all burial mound symbols in this map section.

## Target Symbols

The key diagnostic feature shared by every mound symbol is short **radiating lines (hachures) pointing OUTWARD** from a central form, creating a "starburst" or "cogwheel" appearance. This convention denotes raised ground.

**Subtypes to identify:**

- **Kurgan (burial mound)**: Orange-brown hollow circle with radiating lines. Approximately 10–20 pixels across. May appear near elevation figures or the Cyrillic label "кург."
- **Settlement mound**: Orange-brown, typically larger and oval or irregular in outline. Bears more radiating lines (8–15).
- **Triangulation point on mound**: Black triangle containing a central dot, encircled by black radiating lines.
- **Benchmark on mound**: Black square containing a central dot, encircled by black radiating lines.

**Radiating lines pointing outward** are the essential identifier. Symbols lacking visible radiating lines are not mounds.

## Guidelines

1. Report a separate bounding box for every individual symbol, including those appearing in clusters.
2. Partially obscured symbols (overlapped by lines, shapes, or text) should be included provided the starburst pattern is still recognisable.
3. When reference examples accompany the prompt, use them to resolve uncertain cases. Each reference image is centred on the feature being labelled — the target symbol for Positive examples, the confusable feature for Negative examples.

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
