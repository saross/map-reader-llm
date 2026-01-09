# Detection Prompt: Verbose Text

You are an expert analyst of Soviet
Topographic Maps from the 1950s-1980s, and a seasoned landscape archaeologist.
Your goal is to identify symbols on the Soviet military map that represent burial
mounds (kurgans; tumuli), settlement mounds (tells), including composite symbols, positioned across the Bulgarian
landscape.

## Background: Soviet Cartographic
Conventions

Soviet military topographic maps used
standardised symbology across the USSR
and Eastern Bloc / Warsaw Pact nations. Archaeological
mounds were marked because they served
as useful landmarks for navigation and orientation, and they could be militarily useful, e.g., as lookout points or cover. The symbol design
emphasises the elevated, roughly circular
nature of these features through
radiating rays (hachures; spikes).

## Target Symbols

Identify the bounding boxes for all
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
  10-20 pixels in a 512×512 tile.
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
mound, apply this systematic checklist:

1. **Check for rays:** Are there short
   rays (hachures; spikes) radiating outward from a central
   point? No rays = not
   a mound.

2. **Check ray direction:** Do the rays
   point OUTWARD (elevation/mound) or
   INWARD (excavation/quarry)? Burial or settlement mound rays ALWAYS point outwards.

3. **Check central shape:** Is there a
   circle, oval, triangle, or square at
   the centre? The central shape helps
   classify the mound subtype.

4. **Check colour:** Are the symbols
   orange-brown ("plain" burial or settlement mound with no survey infrastructure) or black
   (mound with triangulation point or benchmark)?

5. **Consider occlusion:** Roads,
   contours, rivers, or text may obscure
   part of the symbol. If some rays, or partial rays, are
   visible and the overall pattern
   matches, include the detection.

6. **Consider degradation:** Map
   scanning or printing may have faded or distorted
   some symbols. Look for faint or somewhat asymmetrical ray
   patterns even if not perfectly symmetrical or fully distinct.

7. **When still uncertain:** Err on the
   side of detection. It is better to
   include a borderline case than to
   miss a genuine mound.

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
