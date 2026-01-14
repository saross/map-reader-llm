# Mound Detection (Image-Only with Verbose Exclusion)

Scan the Target Image. Mark all symbols that look like the Positive examples.

## Exclusion Criteria (CRITICAL)

The following symbols appear frequently on Soviet maps and are commonly confused with mound symbols. Study the negative reference images carefully, and actively avoid marking these features:

### 1. Spot Heights

- **Visual:** Simple dots (black or brown) accompanied by elevation numbers (e.g., "185", "247").
- **Critical difference:** NO hollow shape. NO radiating rays (hachures; spikes). Just a dot with a number.
- **Key test:** Ignore the number; check the symbol. Is it hollow, with rays? No → exclude.

### 2. Triangulation Points (standalone)

- **Visual:** Black triangles with a central dot, but NO surrounding rays.
- **Critical difference:** NO radiating rays (hachures; spikes) extending outward from the triangle-with-central-dot.
- **Key test:** Rays around the triangle? No → survey marker only, exclude. Yes → triangulation ON mound, include.

### 3. Benchmarks (standalone)

- **Visual:** Black squares or circles with a central dot, NO surrounding rays.
- **Critical difference:** NO radiating rays (hachures; spikes) extending outward from the square-with-central-dot.
- **Key test:** Rays around the shape? No → benchmark only, exclude. Yes → benchmark ON mound, include.

### 4. Quarry and Pit Symbols

- **Visual:** Circular shapes with short marks pointing INWARD toward centre.
- **Critical difference:** Ray direction reversed (inward = excavation, outward = elevation).
- **Key test:** Which way do marks point? Inward → quarry/pit, exclude. Outward → mound, include.

### 5. Contour Line Artefacts

- **Visual:** Closed contour lines on hilltops forming roughly circular patterns or patterns similar to a settlement mound.
- **Critical difference:** Smooth, continuous curves with NO rays (hachures; spikes).
- **Key test:** Rays radiating outward? No → contours, exclude. Yes → mound, include.

### 6. Infrastructure Markers

- **Visual:** Dots on roads, bridges, rivers, or canals.
- **Critical difference:** Located on linear features; no rays.
- **Key test:** Dot only on a road/river line? → infrastructure, exclude. Dot within a square or triangle that has rays (hachures; spikes) → mound, include.

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
