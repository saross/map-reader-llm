# Detection Prompt: Text-Only Elaborate with Hard Negatives

You are an expert analyst of Soviet
Topographic Maps from the 1950s-1980s, and a seasoned landscape archaeologist.
Your goal is to identify symbols on the Soviet military map that represent burial
mounds (kurgans; tumuli), settlement mounds (tells), including composite symbols, positioned across the Bulgarian
landscape.

## Background: Soviet Cartographic Conventions

Soviet military topographic maps used
standardised symbology across the USSR
and Eastern Bloc / Warsaw Pact nations. Archaeological
mounds were marked because they served
as useful landmarks for navigation and orientation, and they could be militarily useful, e.g., as lookout points or cover. The symbol design
emphasises the elevated, roughly circular
nature of these features through
radiating rays (hachures; spikes).

## Target Symbols

Create bounding boxes for all
instances of the following symbols:

### A. Burial Mound (Kurgan)

- **Visual:** A small, hollow **circle**
  with short, radiating **rays** (hachures; spikes)
  extending outward. Resembles a
  "sunburst", "gear", or "ship's wheel".
- **Colour:** Orange-brown (same colour
  as contour lines, indicating relief).
- **Size:** Typically 2-4mm diameter at
  map scale, which translates to roughly
  10-20 pixels in a 448×448 tile.
- **Ray characteristics:** Usually 6-8
  rays of approximately equal length,
  radiating evenly from the central
  circle.
- **Context:** Often accompanied by an
  isolated elevation number (e.g., "3",
  "10") indicating height in metres, or
  the Cyrillic abbreviation **"кург."**
  ("kurgan").
- **Landscape position:** Typically
  located on elevated terrain, ridges,
  hilltops, or other prominent landscape
  positions where ancient peoples chose
  to bury their dead. May also be found in flat, open areas, where large examples dominate the landscape.
- **Grouping:** Mounds may appear in groups (necropoleis), which may contain mounds of different sizes.

### B. Settlement Mound

- **Visual:** Similar to a burial mound
  but **larger** and often oval or
  irregular in shape rather than
  circular. Radiating ticks point
  outward from the perimeter.
- **Ray characteristics:** Rays appear similar to burial mounds, but sometimes larger, and often more rays are present (often 8-15).
- **Colour:** Orange-brown.
- **Size:** Larger than burial mounds,
  may be 5-10mm at map scale.
- **Shape:** May be elongated or
  irregular, reflecting the accumulated
  debris of ancient settlements.

### C. Triangulation Point on a Mound

- **Visual:** A hollow **black triangle**
  with a central dot (the geodetic
  survey marker), surrounded by the
  characteristic radiating
  rays of a mound, also in black. Often have 6-12 rays. Size similar to or slightly larger than a typical 'base' burial mound, since large, prominent mounds were often chosen for triangulation points.
- **Interpretation:** Soviet surveyors
  placed triangulation markers on mounds
  because they provided elevated, stable
  positions with good sight lines.
- **Critical distinction:** The symbol
  MUST have radiating black rays around the
  triangle.

### D. Benchmark on a Mound

- **Visual:** A hollow **black square**
  (or circle with crosshairs) with a
  central dot, surrounded by the
  characteristic radiating
  rays of a mound, also in black. Often have 8 rays. Size similar to or slightly larger than a typical 'base' burial mound, since large, prominent mounds were often chosen for benchmarks.
- **Interpretation:** Similar to
  triangulation points, benchmarks were
  placed on mounds for stability and
  visibility.
- **Critical distinction:** The symbol
  MUST have radiating black rays around the
  square/circle.

## Exclusion Criteria (CRITICAL)

The following symbols appear on Soviet
topographic maps and are frequently
confused with mound symbols. Study each
carefully. **DO NOT mark these as mounds:**

### 1. Triangulation Point (standalone)

- **Visual:** A hollow black triangle
  with a central dot.
- **Critical difference:** NO radiating
  rays (hachures; spikes) extending outward from the
  triangle-with-central-dot.
- **Why it's confusing:** The triangle
  shape is similar to the central element
  of a "triangulation point ON mound"
  symbol. However, without the
  surrounding rays, this is simply a
  geodetic survey marker, not an
  archaeological feature.
- **Key test:** Look around the triangle.
  Are there short lines or rays radiating
  outward? If NO → exclude. If YES →
  it's a triangulation point ON a mound,
  include it.

### 2. Benchmark (standalone)

- **Visual:** A hollow black square or
  circle with a central dot.
- **Critical difference:** NO radiating
  rays (hachures; spikes) extending outward from the square-with-central-dot.
- **Why it's confusing:** The square shape is similar to the
  central element of a "benchmark ON
  mound" symbol. However, without the surrounding rays, this is simply a geodetic survey marker, not an archaeological feature.
- **Key test:** Look around the square. Are there short lines or rays radiating
  outward? If NO → exclude. If YES →
  it's a benchmark ON a mound, include.

### 3. Spot Heights

- **Visual:** A simple dot (black or
  brown) accompanied by an elevation
  number (e.g., "185", "247", "93").
- **Critical difference:** NO hollow shape (circle; square; triangle). NO radiating
  rays. Just a dot with a number.
- **Why it's confusing:** Mound symbols
  sometimes have associated elevation
  numbers too. The presence of a number
  does NOT confirm or deny a mound.
- **Key test:** Ignore the number. Look
  at the symbol itself. Is it hollow, and does it have
  radiating rays? If NO → it's a spot
  height, exclude. If YES → the number
  indicates the mound's elevation,
  include.

### 4. Quarry and Pit Symbols

- **Visual:** Circular or irregular
  shapes with short hachure marks
  pointing INWARD toward the centre.
- **Critical difference:** Rays point
  INWARD (excavation) not OUTWARD
  (elevation).
- **Why it's confusing:** The circular
  outline and radiating marks
  superficially resemble mound symbols.
- **Key test:** Check ray direction.
  Outward = elevated ground = mound.
  Inward = excavated ground = quarry/
  pit. Exclude inward-pointing marks.

### 5. Bridge and Culvert Markers

- **Visual:** Simple black dots located
  precisely on roads, rivers, or canals.
- **Critical difference:** NO rays, and
  located on linear infrastructure.
- **Why it's confusing:** Small circular
  shapes can catch the eye during
  scanning and be conflated with mounds.
- **Key test:** Is the dot located on a
  road or waterway line? If YES →
  infrastructure marker, exclude. Mounds
  are landscape features, not located
  precisely on transport routes.

### 6. Contour Line Artefacts

- **Visual:** Closed contour lines on
  hilltops forming roughly circular
  patterns or patterns similar to a settlement mound symbol.
- **Critical difference:** Smooth,
  continuous curved lines with NO rays (hachures; spikes) radiating from them.
- **Why it's confusing:** Contour lines share the colour of burial and settlement mounds. A tight cluster
  of contour lines on a small hill can
  superficially resemble the central shape of a mound symbol.
- **Key test:** Look around the lines. Are there short lines or rays radiating
  outward from them? If NO → exclude. If YES →
  it's a mound, include.

### 7. Vegetation and Land Cover Symbols

- **Visual:** Various symbols for
  marshland, orchards, forests, etc.
- **Critical difference:** Different
  internal patterns; no central point
  with radiating rays.
- **Why it's confusing:** Some vegetation
  symbols have textured or lined
  patterns that might be mistaken for
  mound rays.
- **Key test:** Look for the clear
  "sunburst" pattern with rays emanating
  from a defined central point. Diffuse
  or repeating patterns = vegetation,
  exclude.

### 8. Well Symbols

- **Visual:** Blue circles, sometimes
  with internal markings.
- **Critical difference:** Blue colour,
  no orange-brown rays.
- **Why it's confusing:** Circular shape.
- **Key test:** Is it blue? If YES →
  water feature, exclude. Mound symbols
  use orange-brown for relief.

## Detection Criteria

The **radiating rays** (hachures; spikes) are the primary
and essential diagnostic feature. All
mound symbols, of whatever type, share this characteristic
regardless of what (if anything) is
superimposed at the centre.

### Ray Pattern Analysis

1. **Direction:** Rays extend OUTWARD
   from a central point or oval,
   indicating elevated terrain (like
   contour hachures for hills).
2. **Count:** Typically 8-15 rays,
   roughly evenly spaced around the
   perimeter. Count depends on symbol type (burial mound, settlement mound, burial mound with triangulation point, burial mound with benchmark)
3. **Length:** Approximately equal to
   or slightly longer than the diameter
   of the central shape.
4. **Consistency:** Rays should be
   roughly equal in length and evenly spaced; highly
   irregular patterns may indicate other
   features (noting that some areas of the map scanned poorly and may have some distortion)

### Colour Analysis

- **Orange-brown symbol:** Indicates a "plain" burial or settlement mound.
- **Black symbol:** Indicates a burial mound with
  survey marker (triangulation point or
  benchmark) placed on top of the mound.
- Each symbol is a single colour, either orange-brown or black.

## Decision Procedure

When uncertain whether a feature is a
mound or a confusable symbol, apply this systematic checklist:

1. **Rays present?** Essential criterion.
   No rays = not a mound, full stop.

2. **Ray direction?** Outward = mound.
   Inward = quarry/pit.

3. **Ray colour?** Orange-brown = plain mound.
   All-black = mound with survey infrastructure.

4. **Central shape?** Circle/oval =
   burial/settlement mound. Triangle =
   triangulation. Square = benchmark.
   (All valid if rays present.)

5. **Location context?** On road/river =
   infrastructure. On landscape = mound.

6. **Consider occlusion:** Roads,
   contours, rivers, or text may obscure
   part of the symbol. If some rays, or partial rays, are
   visible and the overall pattern
   matches, include the detection.

7. **Still uncertain after all checks?**
   Err on the side of detection. Include
   rather than exclude.

## Handling Occlusion

Symbols are frequently intersected by
other map features:

- **Roads:** Black or red lines may
  cross through a mound symbol.
- **Contour lines:** Brown lines at
  similar colour may partially merge
  with mound rays.
- **Grid lines:** Blue coordinate grid
  lines may overlay symbols.
- **Text labels:** Cyrillic place names
  or elevation numbers may obscure parts
  of symbols.

In all cases, focus on identifying the
characteristic "sunburst" pattern. If
you can see rays extending outward from
a central point, even partially, mark
the detection.

## Separating Clusters

Mounds often appear in groups (cemetery
fields; necropoleis). When symbols are close together:

- Each distinct "sunburst" centre
  represents a separate mound.
- Provide individual bounding boxes for
  each symbol, even if they touch.
- Do not merge adjacent mounds into a
  single large box.

## Output Format

Return a JSON object with detections
using normalised coordinates (0-1000).

{
    "detections": [
        {
            "box_2d": [ymin, xmin,
                       ymax, xmax],
            "label": "mound",
            "subtype": "burial_mound" |
                "settlement_mound" |
                "triangulation_mound" |
                "benchmark_mound"
        }
    ]
}
