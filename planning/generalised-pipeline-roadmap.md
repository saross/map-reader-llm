# Generalised extractor pipeline — roadmap

**Created**: 2026-06-08 (Session 106)
**Status**: Post-publication product direction. **Not** current paper scope —
this is the parking place for the "bring-your-own-maps" pipeline vision and the
workstreams that feed into it. Items here are scoped but deliberately deferred
until after the current manuscript.

**Vision**: turn the project's burial-mound detection method into a generalised
service —

> *"Give us your maps, your legend/symbol set, and a small set of
> calibration/test tiles, and we'll build you a detector/extractor."*

i.e. a pipeline that ingests an arbitrary map corpus + a target symbol +
ground-truth tiles, runs the proposer → consensus → verifier → scoring stack,
calibrates the operating point, and returns a deployable extractor + an honest
performance characterisation.

**How to use this doc**: each workstream below is a prerequisite or component of
that pipeline, with enough context that a future revisit does not re-derive the
rationale. When a workstream becomes active, move its tasks into a dedicated
session plan and back-link here. New workstreams: add a section as they're
identified.

---

## WS1 — CRS contract (generalisation prerequisite)

**Why it's first**: the current code tracks coordinate reference systems (CRS)
*out-of-band* and hard-codes the Bulgaria analysis CRS (**EPSG:32635**, UTM 35N)
in **~89 scripts**. A generalised pipeline receives maps in *arbitrary* CRSs
(any UTM zone, any country), and the core metric tolerance (the 20 m
dedup/cluster/buffer-match radius) is only meaningful in the *correct* metric
CRS for *that* region. So an explicit, parametrised CRS contract is load-bearing,
not polish.

**Origin**: Session 106 found a latent CRS bug — `analyse_diversity.consensus_to_gdf`
mislabelled `apply_threshold`'s output (a 2026-04-11 change to the output CRS
silently broke a downstream consumer a month later, undetected because the
published outputs predated the break). Full analysis:
[`docs/methodology/spatial-reference.md`](../docs/methodology/spatial-reference.md)
§ "The consensus voting path" and
[`reports/diversity-crs-mislabel-investigation-2026-06-08.md`](../reports/diversity-crs-mislabel-investigation-2026-06-08.md).

**The principle** (the durable contract):

1. **Geometry carries its CRS** — GeoDataFrames with a populated `.crs` as the
   internal currency, never bare dicts/tuples. Reprojection is always explicit
   (`.to_crs`); a label-vs-coordinates mismatch becomes impossible to introduce
   silently.
2. **One analysis CRS, resolved once and threaded** — never assumed/hard-coded.
3. **Separate storage egress (→ EPSG:4326, RFC 7946) from analysis (stay in the
   analysis CRS)** — analysis never round-trips through 4326.
4. **Respect the declared CRS; never guess** from coordinate magnitude (kill the
   vestigial `coords_are_geographic`/`geojson_coords_to_utm` heuristics).
5. **Test the contract** at every producer/consumer boundary.

### Stage 0 — ✅ DONE (Session 106, PR #10)

Made the broken boundary honest + tested, scoped to the consensus path:
`consensus_to_gdf` declares 4326 and reprojects to the analysis CRS; regression
test `tests/test_analyse_diversity_crs.py`; contract documented in
`spatial-reference.md` + `scripts/README.md` + in-code. Published Phase 3c CSVs
left authoritative-as-is (not regenerated). The reference implementation of the
"good" pattern already exists: `evaluate_detections.load_geojson` (reads the
declared CRS, reprojects to the target).

### Stage 1 — centralise + parametrise the contract (deferred)

- A small shared `lib_crs` (or extend an existing lib): `to_analysis_crs(...)`,
  `to_interchange(...)` (→ 4326), and a single `analysis_crs` resolved once per
  run (from config/CLI).
- Migrate `merge_passes`, `analyse_diversity`, the scorer, and the other metric
  consumers onto it; carry GeoDataFrames (with `.crs`) rather than bare dicts at
  the boundaries.
- Retire the vestigial CRS-detection helpers and begin replacing the ~89
  hard-coded `EPSG:32635` literals with the resolved `analysis_crs`.
- **Trigger**: starting the generalised-pipeline build (or any second study in a
  different UTM zone).

### Stage 2 — derive the analysis CRS from the data (deferred)

- Auto-select the analysis CRS per dataset (e.g. UTM zone from the data
  centroid) or accept it explicitly; thread it through every metric operation.
- **Trigger**: first non-Bulgarian / multi-zone corpus.

---

## WS2 — Spatial identity: one seamless reference, provenance carried, one request builder

**Added**: 2026-10-13 (Session 163), at the PI's request after a week of defects
that all traced to how the pipeline identifies places. **Not** current paper
scope: the D50, D62, and D63 fixes bring the existing pipeline to correct
behaviour, and re-scoring measures what moved. This workstream is how a
generalised pipeline, or a version 2 of this one, should be built so that the
class of defect cannot arise.

**Why it's needed: the root cause.** The pipeline identified places by a string,
the tile file name, and re-derived "which sheet" at every stage, instead of
holding coordinates on one partitioned map. Each sheet is a separate raster with
black no-data margins, and neighbouring sheets' padded tiles overlap at the seams,
so a point near a seam lies in two sheets' tiles with no rule for which sheet owns
the ground. The defects found in S163, each traced to that choice or to
duplicated code:

| Defect | Mechanism | Record |
|---|---|---|
| Sheet-name prefix collision | Sheet read from the tile name by bare `startswith` | PR #33 (D50 review finding 2) |
| Origin gap | Clustering kept bare centroids, dropping members' tiles; later stages re-guessed the nearest tile, sometimes on the neighbouring sheet | D50; D62 (1); PR #42; `reports/s163-agent-records/plateau-recorded-sheet-check-2026-10-13/` (signed plateau incumbents +0.007 to +0.017 F1 on their recorded sheets) |
| Wrong-sheet crops | The same wrong tile sent the cropper to the neighbouring sheet's raster, past its map edge; the verifier saw black squares and rejected real mounds (and twice described features that are not there) | `reports/s163-agent-records/wrong-sheet-crops-sweep-2026-10-13.md` (1,515 verifier rows, 275 places, 43 within 20 m of a gold-standard mound) |
| Real-time and batch request builders diverged | Batch with `--use-cache` sent a text-only config's 17 example images (20,020 input tokens per text request against 1,502); earlier, the cached path dropped the flex tier | D64 smoke run (commit `19f7413a2`); `cached_call_config` docstring in `scripts/4_detect_mounds_batch.py` |
| Scorer copies drifted | `FastScorer`, `per_map_counts()`, `consensus_to_gdf` restated the scorer and fell behind it | `reports/s163-agent-records/scorer-restatement-inventory.md`; PRs #37, #38, #39 |
| Hash-ordered resampling | Paired bootstraps resampled a list built from a set of tile names, so intervals followed `PYTHONHASHSEED` | D63 |
| A dry run created a billed cache | Setup ran before the dry-run exit | PR #34 |

The errors were small (thousandths of F1) and concentrated at seams, so they
surfaced only where margins were thin, and each was found by comparing two
independent routes (H2 against H3; black crops against the K-ladder's
correct crops; batch against real-time token counts).

**Principles for the generalised pipeline:**

1. **One seamless georeferenced reference.** Mosaic every sheet into a single
   reference (a GDAL virtual raster, VRT), each sheet clipped to its map frame
   (neatline), so the sheets partition the ground: every point belongs to
   exactly one sheet by point-in-polygon, never by tile name or nearest tile
   centre.
2. **Tiles are views on that reference,** with stable identifiers and a lookup
   table (identifier → sheet, bounds, pixel transform). Nothing parses meaning
   out of a file name.
3. **Detections become ground coordinates once,** at parse time, and carry their
   provenance (pass, tile, sheet) as structured fields through every stage.
   Clustering always keeps its members; a record without provenance is refused,
   not re-guessed.
4. **Crops are cut from the reference by coordinate,** so a crop cannot come
   from the wrong sheet, and a cheap gate refuses any crop that is mostly
   no-data before a model sees it.
5. **One request builder for every execution mode,** with a test asserting that
   each condition's payload (token count and content hash) is identical in
   real-time, flex, and batch, cached or not.
6. **One scorer.** Any fast or specialised copy must reproduce the live scorer
   in the test suite (the pattern PR #38's gate now follows).
7. **Seam fixtures in the tests:** synthetic detections on sheet edges and in
   overlaps, through every stage from parse to crop to score.
8. **Determinism by construction:** no resampling or permutation consumes an
   order that comes from a set or dictionary of strings; sort by a natural key.

**Tasks (staged):**

- Stage 1 (when a version 2 or the generalised pipeline starts): the seamless
  reference and the tile lookup table; detections in ground coordinates with
  provenance; crops cut by coordinate with the no-data gate.
- Stage 2: the single request builder and the cross-mode payload test; the seam
  fixtures.
- Stage 3: retire every scorer copy, or gate it against the live scorer.
- **Trigger**: the first new corpus, or any decision to rebuild the tiling.
- **Shared with**: map-reader-bench, which was told of these lessons by agent
  mail on 2026-10-13.

---

## WS3+ — other workstreams (to be identified)

Placeholder. As the generalised-pipeline design firms up, add workstreams here
(e.g. legend/symbol-set ingestion, per-dataset calibration-tile protocol,
operating-point auto-selection, packaging the trained extractor, cost/runtime
envelope for arbitrary corpora). Each should follow the WS1 pattern: why it's
needed, the principle/approach, staged tasks with trigger conditions.
