# Atomic map-symbol localisation benchmark

**Created**: 2026-08-19

**Status**: Approved planning direction; implementation deliberately paused

**Parent project**: `map-reader-llm` burial-mound extraction study

**Provisional framework**: Inspect AI

This document externalises the agreed design and implementation sequence for a
provider-neutral benchmark of atomic, single-tile map-symbol localisation. It
is a planning artefact, not an implementation specification. No benchmark code,
new repository, API run, or data transformation is authorised by this document.

The next action is an infrastructure and repository-design discussion, including
how to adapt useful Claude-oriented skills and scaffolding for shared use with
Codex. Implementation remains paused until that discussion is complete.

## 1. Purpose and first benchmark boundary

The first benchmark task is:

> Given one georeferenced map tile and one frozen description or exemplar set
> for a target symbol, return every instance of that symbol whose centre lies
> within the tile's scoring core.

"Atomic" describes the unit of inference and scoring: one tile, one model call,
and no consensus, verifier, cross-tile fusion, or deduplication. It does **not**
require depriving the model of realistic edge context. Input tiles may overlap
and include a halo, while non-overlapping scoring cores partition the evaluated
area exactly once.

This first boundary isolates visual recognition and localisation. Later tasks
may add repeated passes, overlapping-view fusion, consensus, proposer-verifier
architectures, automated configuration search, and end-to-end map extraction.

## 2. Scientific questions

The initial benchmark should support four questions without conflating them:

1. How accurately can a VLM recognise and localise the target symbols under a
   frozen, provider-neutral apparatus?
2. How does performance vary between text-defined and image-defined targets?
3. How do recognition, localisation, operational reliability, latency, and cost
   vary across models and configurations?
4. How does performance vary with map, symbol density, scan quality, and other
   observable image characteristics?

A later, separate benchmark track may ask what each model can achieve after an
equal calibration or optimisation budget. That is a system-adaptation question,
not the same question as fixed-apparatus model comparison.

## 3. Known corpus and provenance facts

### 3.1 Gold-standard corpus

- Four gold-standard map sheets were randomly selected from a 59-map source
  population.
- The four maps contain 569 expert-curated reference points in the complete
  reference corpus.
- The curator considers the references complete and accurate to expert-human
  visual standards, with centre uncertainty of approximately three pixels for
  distorted or asymmetric symbols.
- The four sheets span a meaningful range of symbol densities but are not the
  worst examples of digitisation degradation in the 59-map population.
- The remaining 55 maps constitute the student-ground-truth, production, or
  generalisation set and have a different reference-quality regime.

The four maps are therefore a strong initial measurement corpus but only four
fixed benchmark environments. Results do not, by themselves, estimate
performance over the full population of historical map sheets.

### 3.2 Original calibration and prompt provenance

The committed study record identifies 20 original 512 px calibration tiles,
five from each gold-standard map. The preregistration explicitly describes
these as the tiles used for prompt development and few-shot construction:

- [`preregistration.md`](../docs/methodology/preregistration/osf/preregistration.md)
  section 2.3: "Tiles used for prompt development and few-shot examples."
- [`phase1-library.yaml`](../studies/phase1-library.yaml): the Phase 1 hard-case
  extraction study reads `inputs/tiles/calibration_manifest.json`.
- Preregistration section 8.4: empirical prompt additions and hard examples are
  derived from image-only baseline failures on training tiles only.

Accordingly, the current understanding is:

- Empirical prompt wording and the original hard-positive and hard-negative
  examples were developed from the designated 20-tile calibration set, not from
  arbitrary additional tiles on the four maps.
- Canonical positive and negative images were derived from the map legend, not
  from calibration or evaluation tiles.
- Hard-example locations originated in calibration-tile errors, although E8
  records that centred 128 px crops were extracted from the full source GeoTIFF.
  A crop can therefore contain some neighbouring pixels beyond the originating
  calibration tile boundary.
- H10 later introduced nested calibration pools of 20, 40, 80, and 160 tiles to
  test whether larger pools found more useful or varied hard examples. Those
  expanded-pool artefacts must be distinguished from the original library.

One provenance inconsistency requires resolution before benchmark release:

- The null-example documentation says the three empty exemplars were selected
  from calibration tiles.
- The three filenames in
  [`null_tiles_manifest.json`](../inputs/examples/null-tiles/null_tiles_manifest.json)
  do not occur in the committed 20-tile
  [`calibration_manifest.json`](../inputs/tiles/calibration_manifest.json).

This may reflect an earlier meaning of "training pool" or a documentation or
manifest inconsistency. It must be investigated and documented rather than
silently normalised.

### 3.3 What the holdout supports

The existing prompt apparatus was developed on calibration tiles from the same
four map sheets as the evaluation tiles. This is a valid within-map spatial
holdout, subject to the documented exclusion geometry. It is not an unseen-map
generalisation test.

That distinction does not invalidate the proposed benchmark, but it constrains
its claims and motivates explicit prompt tracks and a later external-validation
track.

## 4. Task geometry: input halo and scoring core

The benchmark should distinguish input overlap from per-edge halo explicitly.
For a square tile of width `T`, stride `S`, and adjacent-tile overlap `O`:

```text
O = T - S
halo_per_edge = (T - S) / 2
```

The project's established 384 px geometry is:

```text
input tile:       384 x 384 px
stride:           336 px
adjacent overlap:  48 px = 12.5% of input width
scoring core:     336 x 336 px
halo per edge:     24 px = 6.25% of input width
```

This is the provisional v1 geometry. It retains the project's existing 12.5%
overlap while scoring every location once. A detection is owned by the core
containing its predicted centre; a reference is owned by the core containing its
curated centre. Predictions in the halo remain in raw logs but do not enter the
atomic score.

Halo width is not yet a settled scientific constant. The H13 analysis confirms
a real, localised edge effect, but its low-margin subgroup is small. Candidate
5%, 6.25%, 10%, and 12.5% per-edge halos should be considered on development
data before v1 is frozen. Definitions must always record pixels per edge,
stride, and pairwise overlap so percentages cannot be confused.

The generated core polygons must cover the declared evaluation footprint
exactly once, with no gaps or double ownership. Boundary padding, shifting, or
clipping rules must be explicit and accompanied by a valid-data mask.

## 5. Sample and geospatial metadata contract

Each benchmark sample should carry comprehensive GIS-readable metadata. Values
that are easily derived but frequently used, especially metres-per-pixel, should
still be stored and cross-validated.

### 5.1 Identity and provenance

- Stable sample, map, source-raster, dataset-version, and split identifiers.
- Source-raster, input-tile, prompt, example-library, and metadata checksums.
- Source and derivative licences or access constraints.
- Pixel window within the source raster.
- Ground-truth source, curator, version, and estimated centre uncertainty.

### 5.2 Coordinate reference and transform

- Six-parameter tile-to-map affine transform.
- Explicit pixel-centre versus pixel-corner convention.
- Source CRS as EPSG identifier where available and WKT2 in all cases.
- CRS units, axis order, and declared analysis CRS.
- Input-tile and scoring-core bounds in native CRS and EPSG:4326.
- Input-tile and scoring-core polygons where bounds alone are insufficient.

### 5.3 Resolution

- Metres-per-pixel in the x and y directions.
- Nominal or geometric-mean metres-per-pixel.
- Derivation method and location of evaluation.
- For geographic CRSs, local geodesic resolution at the tile centre.

### 5.4 Raster characteristics

- Width, height, band count, data type, colour space, nodata, and valid-data
  fraction.
- Resampling, colour conversion, normalisation, compression, and other
  preprocessing steps.
- Source scan resolution where known.
- Padding and valid-data mask at source-map boundaries.

### 5.5 Benchmark geometry

- Input dimensions, scoring-core pixel window, and core area.
- Stride, pairwise overlap, and halo on all four edges in pixels and fractions.
- Interior versus source-boundary status.
- Visible references in the full input and owned references in the core, stored
  in scorer-only targets rather than model-visible fields.

## 6. Prompt and adaptation tracks

### 6.1 Frozen retrospective track

Run the established paper text and image conditions without model-specific
rewriting. This asks how models transfer into the Gemini-developed apparatus and
preserves continuity with the text-versus-image headline result.

This track must be labelled as apparatus transfer, not each model's optimum.

### 6.2 Clean canonical track

Construct matched task definitions that use no empirically mined map examples:

- A generic text condition describing the symbols.
- A canonical-image condition using legend-derived positive and confusable
  symbols, with only operational text required to specify the output task.

The exact semantic parity and treatment of null examples remain open decisions.

### 6.3 Empirical few-shot track

Treat the original calibration-derived library as a separately named condition.
Expanded H10 libraries must carry their calibration-pool identity and cannot be
silently substituted for the original library.

### 6.4 Future equal-tuning-budget track

A later track may give every model the same labelled calibration set, declared
search space, and optimisation budget. The selected configuration must be frozen
before hidden-test evaluation. Candidate variables include prompt, exemplar set,
temperature, reasoning effort, tile size, halo, and repetition count.

This track requires more calibration data or a robust nested-validation design;
twenty tiles are vulnerable to configuration overfitting.

## 7. Output and parsing contract

The portable output should be a small versioned JSON schema containing tile-local
bounding boxes and optional class labels. The canonical scorer converts each box
to its centre and then to map coordinates.

Two output protocols may be useful:

1. A portable JSON-instruction track with the same tolerant parser for every
   provider.
2. A provider-native structured-output track where supported.

They must be reported separately because constrained decoding can change both
format reliability and task performance.

## 8. Metrics and spatial-tolerance profile

### 8.1 Detection metrics

Use maximum-cardinality, one-to-one reference matching, with total distance as
the tie-break. Recompute matching over a fixed tolerance grid, provisionally:

```text
5, 10, 15, 20, 25, 30, 40, 50, and 60 metres
```

For each tolerance report:

- Micro precision, recall, and F1.
- Per-map precision, recall, and F1.
- Macro-average across the four maps.
- TP, FP, FN, reference count, and detection count.

Also report the equivalent pixel-radius profile, matched-distance distribution,
median localisation error, upper quantiles, and localisation-error cumulative
distribution. The approximately three-pixel reference uncertainty should be
shown explicitly when interpreting small-radius performance.

The benchmark should expose the full `F1(r)` curve. A single leaderboard radius
will still be required and must be selected from human repeatability, GIS or
archaeological utility, and map resolution rather than the most favourable model
result. The project's 20 m convention remains provisional.

### 8.2 Occupancy metrics

MCC is defined over scoring-core occupancy, not over continuous detection space:

- Reference-positive core: at least one owned reference.
- Prediction-positive core: at least one owned predicted centre.

Report `tile_occupancy_mcc`, sensitivity, specificity, and the full occupancy
confusion matrix. The core grid must be identical across compared conditions.

### 8.3 Confidence intervals

The intended default is 10,000 bootstrap iterations with a recorded seed for
precision, recall, F1, localisation summaries, MCC, sensitivity, and specificity
where the statistic supports bootstrap estimation.

The final resampling unit is deliberately unresolved. Candidate primary design:

- Paired, map-stratified resampling.
- Non-overlapping scoring cores or larger spatial blocks rather than overlapping
  input tiles.
- Identical resamples across compared conditions.

Spatial-block size should be selected after examining spatial dependence,
density, and map geometry. With only four maps, a map-level population bootstrap
cannot provide a stable estimate of generalisation across map sheets. CIs must
state whether they condition on the four observed maps.

For later leaderboard formation, use paired permutation tests that swap model or
configuration labels within matched spatial units and recompute the metric.
Ten thousand permutations is the provisional default. Pairwise effect CIs can
come from paired bootstrap differences; permutation tests provide the inferential
p-values. Multiplicity correction and tier-formation rules must be specified
before the leaderboard is inspected.

All bootstrap and permutation computation belongs on `sapphire` under the
project's compute policy.

## 9. Scan quality, density, and performance slices

Map quality and density are central benchmark characteristics. They should first
be used for corpus description, stratification, and performance slicing rather
than treated as covariates to be statistically "controlled away."

The candidate feature list must be investigated before it is frozen.

### 9.1 Density and spatial context

- References per map, square kilometre, scoring core, and local neighbourhood.
- Fraction of empty, sparse, moderate, and dense cores.
- Distance to nearest neighbouring reference.
- Distance to input edge, core edge, map margin, and nodata region.
- Core land-area and valid-data fraction.

### 9.2 Radiometric and scan-quality candidates

- Intensity percentiles, dynamic range, and light or dark clipping.
- Global and local contrast.
- Sharpness or blur proxies, potentially Laplacian or gradient based.
- Local entropy and high-frequency energy.
- Noise and compression-artifact proxies.
- Colourfulness, saturation, and channel imbalance where applicable.
- Blank, damaged, stained, folded, seamed, or missing-data area where these can
  be detected reliably.

### 9.3 Cartographic-complexity candidates

- Edge, line, and texture density.
- Text or label density.
- Contour-line or relief complexity proxies.
- Road, settlement, vegetation, and other symbol-confusable content where it can
  be characterised without a large new annotation effort.
- Local target-to-background contrast in scorer-only reference crops.
- Symbol occlusion, truncation, distortion, and legibility from a compact human
  rubric on a sampled subset.

Feature selection should favour interpretability, stability under small image
transformations, low redundancy, and a plausible relationship to VLM perception.
Automated proxies must not be described as direct measurements of human
legibility without validation.

Primary reporting should include micro results, macro-average across maps,
per-map results, and prespecified density and quality slices. Natural maps are
not randomised treatments, so slice findings are descriptive unless a later
study supports stronger causal inference.

## 10. Operational metrics and failure policy

Every leaderboard row represents a model-configuration pair. Record at least:

- Provider, requested and resolved model identifiers, model snapshot, API and
  SDK versions, endpoint, service tier, and run date.
- Prompt, schema, exemplar, and example-order hashes.
- Temperature, top-p, top-k, seed where supported, reasoning effort or thinking
  budget, maximum output, image-detail setting, safety settings, and response
  format.
- Input, cached, output, reasoning, image, and total tokens where reported.
- Per-attempt and per-success cost under an explicit price basis.
- Queue time, latency, throughput, and total wall time.
- Attempt count, retry cause, error category, parse status, and completion status.
- For local models: hardware, precision or quantisation, serving engine, batch
  size, peak memory, and available power or energy measurements.

Failure categories:

1. Transient infrastructure failure: retry under a fixed policy, provisionally
   three attempts with backoff.
2. Terminal provider failure after retries or provider refusal.
3. Model-output failure: malformed schema, truncation, refusal, or invalid
   coordinates.

Failed attempts remain in cost and latency totals. No failed tile may be dropped
from the run manifest. Baseline capability runs should not automatically retry
malformed model output, since output validity is part of model behaviour.

Report recognition metrics, completion rate, format-validity rate, and a clearly
labelled operational sensitivity that treats terminal or invalid outputs as
empty detections. Do not combine availability and recognition into a single
utility score without an explicit stakeholder-derived cost function.

## 11. Implementation sequence

### Stage 0 — benchmark charter

Freeze the intended claim, task unit, prompt tracks, benchmark audience, and
explicit exclusions. This is the construct-validity stage: define what the score
means before building the runner.

### Stage 1 — provenance and split audit

Inventory every reference, calibration tile, prompt revision, canonical image,
hard example, null example, and expanded H10 pool. Produce a model-visible-data
and geographic-overlap matrix. Resolve or formally record the null-example
provenance inconsistency. Check redistribution and licensing constraints.

### Stage 2 — spatial and metadata specification

Specify the core-halo geometry, source-boundary policy, CRS contract, affine and
metres-per-pixel fields, sample IDs, checksums, and schema validation. Prove that
cores cover the intended evaluation footprint once and that each reference has
one owner.

### Stage 3 — ground-truth repeatability study

Re-click a sample of clear, distorted, dense, and degraded symbols without
consulting the stored centres. Estimate the annotation-error distribution in
pixels and metres. Use it with archaeological utility to choose the reference
matching radius and interpret the tolerance curve.

### Stage 4 — dataset characterisation

Generate candidate density, scan-quality, and cartographic-complexity features.
Inspect their distributions, redundancy, interpretability, and within-map versus
between-map variation. Freeze only justified features and slice boundaries.

### Stage 5 — pure scoring package

Build provider-independent parsing, coordinate conversion, multi-radius
one-to-one matching, localisation summaries, occupancy metrics, and bootstrap
inputs. Add synthetic and real-fixture tests for boundaries, empty sets,
overlapping candidates, CRS conversion, monotonic tolerance curves, and undefined
metrics.

### Stage 6 — prompt and output contracts

Freeze retrospective and clean-canonical text and image conditions, semantic
parity rules, exemplar order, portable JSON schema, structured-output variant,
and hashes.

### Stage 7 — Inspect harness

Implement one Inspect task whose dataset, solver, scorer, metrics, model options,
and logs remain separable. Connect OpenAI, Google, Anthropic, and one local or
open-weight route without embedding provider logic in the scorer.

### Stage 8 — telemetry and retry layer

Implement attempt-level provenance, usage, cost, latency, failure taxonomy,
retry policy, and completed-run validation. Extend the existing manifest concepts
rather than creating an incompatible provenance vocabulary.

### Stage 9 — smoke test

Use a small, non-headline set containing positive, empty, dense, degraded, and
edge-near cases. Verify prompts, coordinate transforms, raw outputs, parser,
scores, logs, retries, and cost accounting manually. Spend no more than necessary
to validate contracts.

### Stage 10 — development pilot

Use calibration or development data only to evaluate halo candidates, output
protocol, provisional radius, failure policy, and practical run configuration.
Do not optimise against benchmark test labels.

### Stage 11 — freeze benchmark v1

Version and hash the dataset, metadata, prompts, exemplars, schemas, scorer,
model-config policy, bootstrap design, slice definitions, and analysis plan.
Create a benchmark card describing intended and unsupported claims.

### Stage 12 — full cross-model evaluation

Run frozen model-configuration pairs over identical samples, with enough repeated
epochs to characterise stochasticity. Interleave run order where practical to
reduce temporal provider drift. Preserve raw and normalised output.

### Stage 13 — analysis and reporting

Report tolerance curves, precision, recall, F1, occupancy MCC, localisation,
micro and macro results, per-map and quality or density slices, CIs, completion,
cost, and latency. Use offline rescoring when the scorer changes; never spend on
inference merely to recalculate metrics.

### Stage 14 — extensions

Possible extensions include the equal-tuning-budget track, halo sensitivity,
full overlapping-view fusion, consensus and verifier architectures, 55-map
distribution shift, additional expert-curated maps, and a VLMEvalKit adapter.

## 12. Repository and infrastructure decision gate

Planning and provenance work belongs in this repository because the source data,
study history, prompts, scorer, calibration record, and methodological audit are
here. Executable benchmark development should not begin until repository
placement and shared agent infrastructure are agreed.

The provisional recommendation is:

1. Keep Stages 0-4 and this provenance record in `map-reader-llm`.
2. After the task, metadata, and scorer contracts are sufficiently stable,
   create a new sibling repository for the reusable benchmark package and
   Inspect harness.
3. Do **not** start with a Git submodule. A submodule would couple two changing
   repositories while adding clone, branch, CI, and path-management friction.
4. Link the repositories by immutable dataset and code versions, checksums, and
   explicit provenance rather than by an early submodule.
5. Reconsider packaging or a submodule only if one repository later becomes a
   stable dependency of the other.

The new repository would provide a clean provider-neutral architecture, focused
CI, simpler installation, and a stronger independent benchmark portfolio. This
research repository would remain the authoritative provenance and source-study
record. No new repository should be created before the infrastructure session.

That session should inventory the existing Claude instructions, skills,
commands, hooks, session archiving, phase gates, and experiment guards; classify
them as project-specific or tool-agnostic; and decide which should become shared
repository instructions, Codex skills, ordinary scripts, or CI checks. Existing
infrastructure should be adapted deliberately rather than copied wholesale.

## 13. Open decisions before implementation

- Final benchmark repository name, ownership, licence, and public/private status.
- Shared `AGENTS.md` or equivalent cross-agent instruction strategy.
- Which Claude skills and commands should be adapted for Codex.
- Whether 6.25% per-edge halo is frozen directly or preceded by a small pilot.
- Exact scoring-core boundary and source-map padding policy.
- Primary reference radius and tolerance-grid maximum.
- Human repeatability sample and protocol.
- Bootstrap resampling unit and spatial-block definition.
- Pairwise permutation, multiplicity correction, and leaderboard-tier rules.
- Clean-canonical handling of null examples.
- Final scan-quality and cartographic-complexity feature set.
- Failure treatment in operational sensitivity results.
- Dataset redistribution and map-image licensing.

Implementation is paused at this decision gate.
