# Precise-location (point-marking) app — build specification

> **Last revised**: 2026-08-04 (original publication — reconnaissance done in
> Session 128, build not started). See [§ Changelog](#changelog) for revision
> history.

**Why this exists**: ruling 21 makes a fixed reference the gate for every
reference-tainted re-analysis, and ruling 20(d) makes this app step 1 of the
sequence. Five queued analyses wait on it
(`reports/verification/reference-standardisation-queue.md`).

**Scope** (ruling 21c): the **773 promoted phantoms only**. The 4,746 student
mounds are *not* re-marked — that option was priced at ≈ 6 hours and declined.
The resulting reference is mixed-provenance by design.

**Budget**: ≈ 1 hour of PI review. No API spend. The build is agent work.

## What the app has to do

For each of 773 confirmed mounds, show the map imagery around its recorded
position, let the reviewer **click the true centre**, and record that click.
Everything else — mound type, map, label — inherits from the existing row.
Three things resolve at once (ruling 20d step 2):

1. **Obs 371** — match distances were recorded as 25 m rings anchored at 50 m
   rather than measured from marked centres, so sub-50 m Track-2 figures
   penalise correct detections of student-missed mounds.
2. **The 4–6 borderline conflations** — pairs between 7.3 m and 15 m from a
   student point, closer than the ≳15–20 m "genuinely distinct mounds" floor
   and further than the 5 m de-duplication tolerance. They cannot be settled
   from coordinates; they have to be seen.
3. **Row sorting** — `canonical-review.csv` re-sorted on exact position.

## The data, as it actually is

**Primary input** —
`results/deployment-oracle-2026-06-06/canonical-gt/canonical-review.csv`,
773 rows, every one `human_label = mound`:

| Column | Example | Note |
|---|---|---|
| `candidate_id` | `0` | not unique across runs — scope it to this file |
| `human_label` | `mound` | constant; all 773 |
| `buffer_metres` | `50`, `200.0` | **see the format hazard below** |
| `x`, `y` | `322769.12281904556` | projected metres, matching the run CRS |
| `map_name` | `K-35-050-4` | joins to the raster |

**Richer sibling** —
`results/deployment-oracle-2026-06-06/canonical-gt/re-review/human-review.csv`
carries `source_tile` (e.g. `K-35-053-2_x3360_y2688.png`), which encodes the
tile's pixel offset in its filename and is the cheapest route from a row to a
rendered window. It also carries `verifier_probability`, `symbol_type` and a
`timestamp`. It does not cover all 773 — treat it as an enrichment join, not
the spine.

**Imagery** — `inputs/rasters/*.tif` (2.7 GB, georeferenced, e.g.
`K-35-052-4_32635.tif`), with pre-cut tiles under `inputs/tiles/`,
`inputs/tiles_256/` and `inputs/tiles_384/`. Rendering a window directly from
the GeoTIFF around `(x, y)` avoids depending on any particular tile cut, and
the rasters are already on disk.

### Data hazard found during reconnaissance — fix before grouping

`buffer_metres` is stored in **two string formats**. Grouping by the raw
string silently undercounts:

| Buffer | as `'N'` | as `'N.0'` | true total |
|---:|---:|---:|---:|
| 50 | 410 | 5 | **415** |
| 75 | 173 | 6 | 179 |
| 100 | 85 | 6 | 91 |
| 125 | 42 | 2 | 44 |
| 150 | 30 | 4 | 34 |
| 200 | — | 10 | 10 |

Twenty-three rows carry the `.0` form. **Cast to float before any grouping or
gating.** Anything that buckets on the raw string reports 410 at R = 50 m
instead of 415 — a plausible-looking number that is simply wrong.

Related hazard already on record: `uuid` in the student base layer is a
**symbol code, not an identifier** — 4,770 features share 833 distinct values.
Never key on it (`wave7-open-items-2026-08-04.json` `_meta.census_hazard_note`).

## Output contract

Write a **new** file; do not mutate `canonical-review.csv` in place. Each row
should carry, at minimum:

- `candidate_id` and the original `x`, `y` (so the displacement is recoverable)
- `x_marked`, `y_marked` — the clicked centre
- `displacement_m` — derived, and the headline diagnostic
- `marked_by`, `marked_at`
- a reviewer verdict field able to express **"this is the same mound as a
  nearby student point"**, which is what settles the borderline conflations
- `skipped` / `uncertain`, so an ambiguous case is recorded rather than forced

Nothing downstream should consume it until the sort in ruling 20(d) step 3
lands.

## Build notes

- **Local and offline.** No API, no external hosts. A small local web app or a
  matplotlib/Qt click handler both work; the deciding factor is how fast 773
  points can be got through, so **keyboard-first navigation** (next / back /
  skip) matters more than visual polish.
- **Pre-render, don't render on click.** 773 windows generated up front makes
  the review itself instant, which is the difference between one hour and
  three.
- **Show the buffer context.** Draw the recorded position and a scale bar so
  the reviewer can see the 7.3–15 m borderline cases for what they are, and
  overlay nearby student-GT points — the conflation judgement is exactly
  "is that the same mound?"
- **Checkpoint every N marks.** An hour of clicking must survive a crash.
- **Tests** — `tests/` per the tier1/tier2 marker pattern. Tier 1 should cover
  the float-cast hazard, the coordinate round-trip (raster CRS ↔ pixel), and
  resume-from-checkpoint.

## Open question carried in from W7-U2 — now better characterised

Ruling 19 states the promoted set enters analysis gated per buffer, "474 qualify
at R = 50 m, rising to 672 at 150 m". The canonical CSV's own cumulative series,
float-normalised, is:

| ≤ 50 | ≤ 75 | ≤ 100 | ≤ 125 | ≤ 150 | ≤ 200 |
|---:|---:|---:|---:|---:|---:|
| 415 | 594 | 685 | 729 | 763 | 773 |

That series does **not** contain 474 or 672, so the two are demonstrably
different objects rather than a rounding or off-by-one difference. W7-U2 is
therefore no longer conjecture in one direction — 415 at R = 50 m is confirmed
from the file — but the provenance of 474/672 is still unestablished and must
not be cited in Methods until it is. Establishing it is cheap once the app
exists, because the re-marked file makes the gating recomputable from scratch.

## Changelog

### 2026-08-04 — Original publication

Written in Session 128 after reconnaissance of the input data, ahead of any
build. Records the scope ruling (773 only), the actual column schema, the
`buffer_metres` mixed-format hazard and its per-buffer correction table, the
imagery options, the output contract, and the sharpened state of W7-U2. No code
written yet.
