# Printed mound-symbol footprint at 1:50,000 — direct measurement

> **Last revised**: 2026-08-22 (original publication). See
> [§ Changelog](#changelog) for revision history.

**Purpose**: Answer the Session 139 queued check for Seed 8 / Obs 425
prose: *is a 20–30 m matching tolerance within the printed mound
symbol's ground footprint at 1:50,000?* **Answer: yes, comfortably.**

**Method**: Direct measurement on the four gold-standard sheets
(`inputs/rasters/*.tif`, EPSG:32635, native resolution 5.019 m/px —
equivalent to ~0.100 mm on paper at 1:50,000, i.e. ~253 DPI scans).
For up to 20 ground-truth mounds per sheet
(`inputs/gis-map-mounds/Mounds32635.shp`, seeded sample), a
24 × 24 px window was cut around the point, ink pixels isolated
(brown/ochre OR black thresholds), 1-px gaps closed, and the
connected component nearest the window centre measured as a maximum
bounding extent. Components smaller than 20 px, farther than 4 px
from centre, or larger than 20 px extent (clutter-merged with leader
lines, numerals, or drainage) were excluded: **38 of 80 attempted
symbols were usable**. The maximum-extent statistic deliberately
includes the star symbol's ray tips — the full visual footprint is
what the question asks about.

**Results**:

| Quantity | Median | IQR | Range |
|---|---|---|---|
| Symbol extent (native px) | 14 | 13–17 | 12–20 |
| Ground diameter (m) | **73** | 65–85 | 60–100 |
| Ground radius (m) | **36** | 33–43 | — |
| On-paper diameter at 1:50k (mm) | 1.46 | 1.30–1.71 | — |

Two symbol families were observed in the sample, consistent with the
"symbol family" point among the Principal Investigator's five Obs 425
corrections: the brown six-pointed star (kurgan proper, measured
50–65 m across its rays) and a black square-with-central-dot carrying
a height annotation (~60 m core). Both fall in the same size band.

**Implication for the buffers**: the 20 m evaluation buffer is
~0.55 × the median symbol radius and the 30 m buffer ~0.83 × — both
demand localisation *within the symbol's own face*. A detection
placed at the printed symbol's edge would fail the 20 m gate and sit
at the margin of the 30 m gate. This grounds the Obs 425
"conservative buffers / tolerance alignment" framing empirically and
confirms the working-notes estimate (~15 px, ~75 m diameter, ~37 m
radius) used in the buffer-plateau analysis.

**Reproducing**: the measurement is a ~40-line rasterio + scipy
snippet over committed inputs (seeded samples, `random_state=7` for
the corpus sweep, `random_state=42` for the six-patch visual
inspection); US$0.00 API, local CPU seconds.

## Changelog

### 2026-08-22 — Original publication

Written in Session 140 to discharge the S139 queued symbol-diameter
check. Baseline for future diffs; no prior revision.
