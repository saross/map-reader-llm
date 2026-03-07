# Cartographic Symbol Detection — Ancient Mounds

Locate all ancient burial mound cartographic symbols on this map tile.

## Target Symbols

On Soviet topographic maps, mound symbols are consistently rendered with short **hachures extending OUTWARD** from a central figure, forming a distinctive "sunburst" or "toothed-wheel" pattern. This convention represents a terrain elevation.

**Subtypes to locate:**

- **Burial mound (kurgan)**: Orange-brown hollow circle fringed by outward hachures. Diameter approximately 10–20 pixels. Often plotted near elevation values or the Cyrillic notation "кург."
- **Settlement mound**: Orange-brown, characteristically larger and oval or irregular. Displays a denser fringe of hachures (8–15).
- **Triangulation point on mound**: Black triangle with a central dot, surrounded by outward black hachures.
- **Benchmark on mound**: Black square with a central dot, surrounded by outward black hachures.

**Outward-extending hachures** are the definitive cartographic marker. Symbols without visible hachures should not be classified as mounds.

## Guidelines

1. Assign a separate bounding box to each individual symbol, even where several appear clustered together.
2. Symbols partially covered by other map features (lines, shapes, text) should still be recorded when the hachure pattern remains identifiable.
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
