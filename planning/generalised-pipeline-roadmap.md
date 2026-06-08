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

## WS2+ — other workstreams (to be identified)

Placeholder. As the generalised-pipeline design firms up, add workstreams here
(e.g. legend/symbol-set ingestion, per-dataset calibration-tile protocol,
operating-point auto-selection, packaging the trained extractor, cost/runtime
envelope for arbitrary corpora). Each should follow the WS1 pattern: why it's
needed, the principle/approach, staged tasks with trigger conditions.
