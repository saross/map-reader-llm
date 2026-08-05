# Precise-location (point-marking) app — build specification

> **Last revised**: 2026-08-05 (built in Session 129; scope widened to 906
> items at a 50 m cut; imagery pointer corrected). See
> [§ Changelog](#changelog) for revision history.

**Why this exists**: ruling 21 makes a fixed reference the gate for every
reference-tainted re-analysis, and ruling 20(d) makes this app step 1 of the
sequence. Five queued analyses wait on it
(`reports/verification/reference-standardisation-queue.md`).

**Scope**: ruling 21c set this at the **773 promoted phantoms only**. The PI
widened it on 2026-08-05 to sweep up every possible conflation in the same
pass, at a **50 m** cut — mound symbols run ~12–18 px across at ~5 m/px, so
two mounds 50 m apart are nearly touching, and the proximity audit showed the
widening from 40 m to 50 m cost only ~25 further items.

The queue is **1,006 items**, built by `scripts/build_marking_queue.py`:

| Item type | Count | Why it is in the queue |
|---|---:|---|
| `phantom` | 773 | Original scope; every one needs a centre for Obs 371 |
| `student_conflation` | 105 | Within 50 m of a phantom (incl. 4 inside the 5 m de-duplication tolerance) |
| `merge_site` | 26 | The merged centroids separating layer 2 from layer 1 |
| `student_pair` | 6 | Within 50 m of another student point |
| `curator_addition` | 2 | The two layer-2 additions with no layer-1 antecedent |
| `jitter_sample` | 100 | Random unconflicted student mounds, to measure placement error |

Counts sum to more than 1,006 because an item qualifying under several
headings is emitted **once**, with its reasons joined. Distinct student
items: 233.

The remaining ~4,600 student mounds are still not re-marked. The proximity
audit found layer 2 essentially clean at this range — 3 pairs within 50 m,
minimum separation 38.14 m — so there is nothing there to adjudicate. The
resulting reference is mixed-provenance by design.

**Budget**: ≈ 1.3 hours of PI review. No API spend. The build is agent work.

## Why not mark every mound visible in one window?

Considered and rejected on 2026-08-05. Marking all mounds per screen would
save less than it appears — queue items are mostly isolated (median phantom
nearest-neighbour ≈ 1,236 m), so at the default 200 m window **572 of 906
items had no other queue item in view**, and a greedy cover needs 724 screens
against 906 items: a ~20% saving before accounting for the extra clicks and
decisions per screen.

The deciding argument is correctness rather than effort. With one click per
screen the click unambiguously belongs to the item under review. Multi-marking
requires assigning clicks back to items by proximity, which is least reliable
exactly where the review matters most: the 1.7 m merged pair, the 0.98 m
phantom-student conflation. That trades ambiguity in the highest-value rows
for a modest time saving.

The jitter measurement that motivated the idea is served instead by
`jitter_sample`, drawn **at random**. The ~400 student mounds that happen to
fall in view of a queue item are there *because* they sit near a phantom —
terrain where the model found mounds students missed — so a jitter figure
estimated from them would be biased toward the hard cases. The random sample
is verified conflation-free (nearest phantom 55.2 m, nearest other student
58.4 m, both beyond the 50 m cut) and seeded so rebuilds are stable.

## What the app has to do

For each of 773 confirmed mounds, show the map imagery around its recorded
position, let the reviewer **click the true centre**, and record that click.
Everything else — mound type, map, label — inherits from the existing row.
Three things resolve at once (ruling 20d step 2):

1. **Obs 371** — match distances were recorded as 25 m rings anchored at 50 m
   rather than measured from marked centres, so sub-50 m Track-2 figures
   penalise correct detections of student-missed mounds.
2. **The borderline conflations** — pairs between 7.3 m and 15 m from a
   student point, closer than the ≳15–20 m "genuinely distinct mounds" floor
   and further than the 5 m de-duplication tolerance. They cannot be settled
   from coordinates; they have to be seen.

   > **Count queried 2026-08-05.** This document previously said "4–6". A
   > direct scan of all 773 rows against
   > `inputs/vectors/references/student-mounds-55maps-reviewed.geojson`
   > (4,746 features) finds **12** in the 7.3–15 m band and **17** in the
   > wider 5–15 m band, not 4–6. The gap is most likely a *reference-layer*
   > difference — ruling 19 makes the ground truth four layers, and the
   > register records both a 4,745 reviewed layer and a 4,770 fixed base —
   > which is the same class of defect as W7-D9. The provenance of "4–6" is
   > unestablished, so treat it as unverified and do not cite it; the marking
   > pass makes the count recomputable against whichever layer is fixed as
   > canonical. Row indices of the 17, nearest-first: 358 (5.05 m), 110, 100,
   > 148, 205, 147 (9.13 m), 124, 151, 207, 390, 356, 340, 55, 125, 126, 113,
   > 442 (14.68 m).
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

**Imagery** — `inputs/rasters/Russian1981_32635/*.tif` (2.4 GB, 55 sheets,
georeferenced EPSG:32635, e.g. `K-35-050-4.tif`), with pre-cut tiles under
`inputs/tiles/`, `inputs/tiles_256/` and `inputs/tiles_384/`. Rendering a
window directly from the GeoTIFF around `(x, y)` avoids depending on any
particular tile cut, and the rasters are already on disk.

> **Corrected 2026-08-05.** The original text named `inputs/rasters/*.tif`
> (top level). That directory holds only the four **GS corpus** sheets, which
> ruling 21 puts explicitly out of scope, and it covers **0 of the 55**
> `map_name` values in `canonical-review.csv`. `Russian1981_32635/` covers
> **55 of 55**. This is the same `--rasters-dir` that
> `scripts/launch_canonical_gt_rereview.sh` already passes.

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

**Narrowed 2026-08-05**: the hazard is real at the *raw-text* level (confirmed
by `cut -d, -f3 | sort | uniq -c`), but `pd.read_csv` already coerces the mixed
column to `float64`, so pandas consumers see 415 without doing anything. The
exposed readers are `csv.reader`, shell `cut`/`awk`, and anything treating the
column as a category. `load_phantoms()` casts explicitly anyway, so the
guarantee survives a future change of reader.

### Two constraints measured during the build (2026-08-05)

**1. Crop framing displaces the reference by up to one pixel.** A crop centred
via `src.index()` is framed on the pixel *corner* the recorded point floors to,
not on the point itself. Measured across all 773 rows: median **4.02 m**, max
**7.00 m**, bounded by one pixel diagonal (**7.09 m**); **176 rows (22.8%)**
exceed the 5 m de-duplication tolerance. An app treating the image centre as
the recorded position would therefore misplace nearly a quarter of marks by
more than the tolerance that defines a duplicate. `mark_mound_centres.py`
converts clicks through the raster's affine transform instead, which
round-trips at 0.00 m (`CropGeometry`, tier-1 tested).

**2. The imagery bounds achievable precision at about ±2.5 m.** All 55 sheets
are ~5 m/px (4.995–5.064 m/px), and no higher-resolution source exists in the
repository — the other `inputs/` directories are vector-only. A marked centre
therefore carries roughly half a pixel of irreducible quantisation regardless
of on-screen magnification. This is comfortably below the 25 m/50 m rings that
Obs 371 is about, but it is a fifth to a third of the 7.3–15 m separations the
borderline conflations turn on, so those remain **visual** judgements ("is that
the same mound symbol?") rather than metric ones. The app states the figure on
screen, and it belongs in the reference artefact's header alongside the
existing not-a-gold-standard caveat.

Related hazard already on record: `uuid` in the student base layer is a
**symbol code, not an identifier** — 4,770 features share 833 distinct values.
Never key on it (`wave7-open-items-2026-08-04.json` `_meta.census_hazard_note`).

## Adjudication rule (PI, 2026-08-05)

Settled during the pass itself, after the first ~130 items showed that
"is this the same mound?" needs a decision procedure rather than
case-by-case judgement. Stated as the reviewer stated it:

1. **A clear symbol on the map that has been falsely tagged as a mound is
   a false positive** (`x`). The detector fired on something real but
   wrong — the object exists, it simply is not a mound.
2. **An attractor that pulls the extracted point away from a nearby mound
   into a relatively clear area, or into a generally messy area with no
   clear mark, is a displacement** (`c`, or `d` where the point is the
   first record of that mound). The mound exists and is already counted;
   the detector mislocated it.
3. **Beyond roughly 200 m, treat it as a false positive** and the nearby
   mound as coincidence, not as the source of a pull.

The 200 m ceiling is a judgement call, and deliberately a blunt one. It is
not derived from the data, because the data cannot yet support it: the
attractor-pull distance distribution is one of the things this pass exists
to measure, so using it to set the cut would be circular. Independent
support that 200 m is not unreasonable: under a uniform-density model
(0.22 mounds/km², mean spacing ~2.1 km) the chance of a student mound
within 200 m of an arbitrary point is ~2.7%, against 55.9% of phantoms
having one within 126.5 m — so coincidence is a weak explanation well
past 100 m, but not a negligible one at 200 m. That model ignores
clustering and so understates the true coincidence rate; a
clustering-aware version belongs in the paper.

**Consistency is the property being optimised, not correctness.** A rule
applied uniformly is auditable and can be revised wholesale afterwards
from the recorded displacements; a better rule applied unevenly cannot.
The rule was therefore applied retroactively to the marks made before it
was settled, using the app's "Revisit earliest marks" navigation mode —
those marks are scattered through the re-sorted queue rather than
contiguous, so they are reachable by marking time, not by position.

**Known limitation to carry into Methods**: rules 2 and 3 partition the
same evidence on distance alone, and the boundary is set by judgement.
Every ingredient for re-cutting it later is preserved — `displacement_m`,
`resolved_partner_layer`, `resolved_partner_m`, and the verdict — so the
threshold can be moved and its effect measured without re-reviewing.

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

## As built (2026-08-05)

- **`scripts/mark_mound_centres.py`** — Streamlit, reusing the "bullseye"
  reviewer's framework (`scripts/review_candidates.py`) at Shawn's suggestion:
  its `_best_raster_for_point` sheet-picker is imported directly, and its
  key-binding JavaScript is carried over. Click capture uses
  `streamlit-image-coordinates` (MIT, added to `requirements.txt`); Streamlit
  1.56 has no native image-click widget, and Altair selections cannot return
  an arbitrary continuous position.
- **`scripts/launch_point_marking.sh`** — supplies every path, including the
  corrected `--rasters-dir`. Re-running resumes at the first unmarked row.
- **Not** a verbatim reuse of `render_candidate_context_crop`: that returns an
  image and nothing else, which is insufficient once clicks must be
  georeferenced. `render_base_crop` returns a `CropGeometry` alongside the
  image — see constraint 1 above.
- **Checkpointing is per-mark**, not every N: an atomic temp-then-rename after
  every decision, which costs nothing at 773 rows.
- **Deviation from "pre-render up front"**: crops are rendered lazily and
  cached by Streamlit (`@st.cache_data`). A cold render measures ~0.2 s and
  cached re-renders are free, so the batch pre-render the spec suggested buys
  little and would delay first use. Revisit only if the review feels slow.
- **Tests** — `tests/test_mark_mound_centres.py`, 21 tier-1 plus 1
  tier-2/integration (Streamlit's own `AppTest` harness runs the script
  end-to-end against the real corpus, skipping when the rasters are absent).
  All 22 pass; `ruff check` clean.
- **Reviewer verdicts**: `d` distinct · `c` same as student point · `u`
  uncertain · `s` skip; `n`/`b` navigate. A click is required before `d`/`c`
  and recorded even when the verdict is `u`.

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

### 2026-08-05 (c) — Jitter sample added; multi-marking considered and rejected

Refresh trigger: the PI asked whether all mounds in a window could be marked
at once, to save time and to pick up incidental student-only mounds as a
measure of "student sloppiness".

Measured rather than assumed: multi-marking saves ~20% of screens (906 items
→ 724 under a greedy cover at the 200 m default), because 572 items have no
co-visible neighbour. Rejected on correctness — click-to-item assignment is
ambiguous precisely at the tight pairs the pass exists to adjudicate. Full
reasoning in § "Why not mark every mound visible in one window?".

The jitter goal is met instead by a random, seeded, verified-conflation-free
sample of **100** student mounds (queue 906 → **1,006**, ≈ +7 min). Random
rather than incidental because the ~400 student mounds visible beside a queue
item are selected for proximity to a phantom and would bias the estimate.

### 2026-08-05 (b) — Scope widened to all conflations at a 50 m cut

Refresh trigger: the PI widened the pass — "I'm hoping to simply sweep all of
that up in this pass… I'd widen out to 50 m, it's not that many more" — after
`scripts/audit_mound_proximity.py` priced the options.

| Claim | Before | After |
|---|---|---|
| Scope | 773 phantoms | **906 items** (773 + 133 student) |
| Cut | n/a (15 m borderline band) | **50 m**, all layers |
| Budget | ≈ 1 h | ≈ 1.2 h |
| Student-side coverage | none | conflations, near-pairs, 26 merge sites, 2 curator additions |

Three build consequences. The app now consumes a **queue** rather than
`canonical-review.csv` directly, so phantom and student items share one
cursor and one output schema. Overlays gained two layers — orange for other
phantoms (so a phantom-phantom pair is visible as such) and red for the
superseded layer-1 positions a merged centroid replaced (so a merge can be
checked rather than inherited). And zoom became a per-item control: the 26
merged pairs are separated by between **1.7 m and 49.2 m**, 11 of them under
10 m, so no single window width serves them — at 200 m a 1.7 m separation is
about six display pixels, at 50 m it is 23.

What did **not** change: the output contract, the ±2.5 m precision floor, the
framing-offset correction, and the cumulative buffer series.

### 2026-08-05 (a) — Built; imagery pointer corrected; two constraints measured

Refresh trigger: Session 129 built the app from this spec, and the build's
dry-run gap analysis contradicted the spec in one place and sharpened it in
three others.

| Claim | Before | After |
|---|---|---|
| Imagery directory | `inputs/rasters/*.tif` | `inputs/rasters/Russian1981_32635/*.tif` |
| Map coverage of that directory | implied complete | **0/55** before, **55/55** after |
| Corpus size | 2.7 GB | 2.4 GB (55 sheets) |
| Borderline conflations | "4–6" | **12** at 7.3–15 m, **17** at 5–15 m — provenance of "4–6" unestablished |
| Framing offset | not recorded | median **4.02 m**, max **7.00 m**, 22.8% over the 5 m tolerance |
| Precision floor | not recorded | **±2.5 m**, set by ~5 m/px imagery |

What did **not** change: the scope ruling (773 phantoms only, ruling 21c), the
output contract, the `buffer_metres` per-buffer correction table, and the
cumulative series **415 / 594 / 685 / 729 / 763 / 773** — independently
reproduced from the file during the build, so W7-U2's sharpened state stands
unaltered and 474/672 remain uncited.

Landed in commit `TBD` (fill inside the merge pass, per the rule-14 note in
the Session 129 continuity block).

### 2026-08-04 — Original publication

Written in Session 128 after reconnaissance of the input data, ahead of any
build. Records the scope ruling (773 only), the actual column schema, the
`buffer_metres` mixed-format hazard and its per-buffer correction table, the
imagery options, the output contract, and the sharpened state of W7-U2. No code
written yet.
