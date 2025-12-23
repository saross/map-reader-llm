# Detection Prompt: Text-Only with Hard Negatives

You are an expert analyst of Soviet Topographic Maps. Your goal is to identify archaeological mound symbols.

## Target Symbols

Identify the bounding boxes for all instances of the following symbols:

### A. Burial Mound (Kurgan)

- **Visual:** A small, hollow **circle** with short, radiating **spikes** or rays extending outward. Resembles a "sunburst", "gear", or "ship's wheel".
- **Colour:** Orange-brown.
- **Context:** Often accompanied by an isolated elevation number (e.g., "3", "10") or the abbreviation **"кург."** (kurgan).

### B. Settlement Mound

- **Visual:** Similar to a burial mound but **larger** and often oval or irregular in shape. Radiating ticks point outward.
- **Colour:** Orange-brown.

### C. Triangulation Point on a Mound

- **Visual:** A hollow **black triangle** with a central dot, surrounded by the characteristic radiating rays of a mound.
- **Distinction:** Must have the radiating rays. A simple triangle without rays is NOT a mound.

### D. Benchmark on a Mound

- **Visual:** A hollow **black square** with a central dot, surrounded by the characteristic radiating rays of a mound.
- **Distinction:** Must have the radiating rays. A simple square without rays is NOT a mound.

## Handling Occlusion

Symbols may be partially obscured by lines (roads, contours, grid lines) or text. Focus on identifying the characteristic "sunburst" or "spiked" shape even when intersected by other map features.

## Separating Clusters

Symbols may appear close together. Each distinct "sunburst" centre represents a separate mound. Provide individual bounding boxes for each.

## False Positives (CRITICAL)

The following symbols are easily confused with mounds. **DO NOT mark these:**

### Triangulation Point (without mound)

- **Visual:** A hollow black triangle with a central dot, but **NO radiating rays**.
- **Why it's confusing:** Similar shape to triangulation point ON a mound, but lacks the mound's characteristic spikes.

### Benchmark (without mound)

- **Visual:** A hollow black square/circle with crosshairs or central dot, but **NO radiating rays**.
- **Why it's confusing:** Similar to benchmark ON a mound, but lacks the mound's characteristic spikes.

### Bridge/Culvert Dots

- **Visual:** Simple black dots located on roads, rivers, or canals.
- **Why it's confusing:** Can appear as small circular shapes, but have NO radiating rays.

### Spot Heights

- **Visual:** Simple dots (black or brown) accompanied by elevation numbers.
- **Why it's confusing:** The number nearby might suggest a mound's elevation label, but the symbol lacks rays.

## Negative Constraints

- **IGNORE** contour lines that do not form a distinct sunburst or circle-with-rays.
- **IGNORE** black elevation points (simple dots) unless surrounded by the mound's radiating rays.
- **IGNORE** blue wells (circles with blue filling).
- **IGNORE** vegetation symbols (marshland tufts) without the central mound structure.

## Output Format

Return a JSON object with detections using normalised coordinates (0-1000).

```json
{
    "detections": [
        {
            "box_2d": [ymin, xmin, ymax, xmax],
            "label": "mound",
            "subtype": "burial_mound" | "settlement_mound" | "triangulation_mound" | "benchmark_mound"
        }
    ]
}
```
