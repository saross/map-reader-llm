# Gold-standard FP-classification plan (Item #1, Obs 302 follow-up)

**Date**: 2026-04-29.
**Author**: Claude Code (Opus 4.7) for Shawn Ross.
**Status**: PLAN — awaiting user review and approval before any execution.
**Specification source**: `planning/paper-writeup-continuity.md` lines 1437–1444.

## 1. Executive summary

This plan operationalises the gold-standard (GS) side of Observation 302's FP-class classification — the missing comparator that prevents the paper Discussion from making a clean cross-corpus asymmetric-failure-mode claim. The 55-map side ran on 1,119 human-reviewed FPs across four corrected runs (`results/55maps-fp-classification/report.md`); the GS side has no human-review labels, so we substitute a synthetic distance-based FP filter against the curator-corrected reference (`mounds-reference.geojson`, 569 mounds, EPSG:32635).

Recommended approach: **a sibling script (`scripts/gs-fp-classify.py`)** that imports the prompt, crop renderer, classification call, and aggregation helpers from `scripts/55maps-fp-classify.py` but rebinds the inputs (verified-v1 GeoJSON instead of review CSVs, top-level `inputs/rasters/` instead of `inputs/rasters/Russian1981_32635/`).

Four design-decision verdicts:

1. **FP-filter distance threshold**: **50 m** (single value), rationale §4.
2. **Sample size and sampling**: **classify all FPs at the 50 m threshold** (~16 detections; no subsampling), rationale §5.
3. **Output path**: **`results/gs-fp-classification/`** (sibling to `results/55maps-fp-classification/`), rationale §6.
4. **Distance metric**: **Euclidean planar in EPSG:32635** via `scipy.spatial.cKDTree`, rationale §7.

Expected output: at the recommended 50 m threshold, ~16 FPs (per spot-check) — **trivially small**, well below the spec's "~80" estimate. A sensitivity sweep at 25 m / 75 m / 100 m / 125 m thresholds is included in the plan to bracket the result; total combined N ≈ 22 unique FPs (no double counting via union). Cost stays under $0.05 USD; wall-clock ≤ 10 min on a single worker.

## 2. Background

**Obs 302 caveat** (`docs/notes/reflections/working-notes.md` ≈ line 15000):

> No GS-side comparator. This diagnostic measured 55-map only. The GS half of Shawn's hypothesis (spot-heights / water-features dominant) cannot be directly tested here without running the same classifier on GS FPs. A natural follow-up; estimated cost ~$0.05 (GS has ~80 FPs at canonical operating point per Obs 295 / Obs 298).

**Obs 296 framing** (line ≈ 14555): the cross-corpus per-detection mid-distance pull rate at (50, 75] m is 5–10× higher on the 55-map corpus than on the GS corpus. Shawn's manual-review intuition was that 55-map FPs concentrate on numbers / benchmarks (distractor-pull) while GS FPs concentrate on spot-heights / water-features (a different generalisation regime, post-calibration). Obs 302 partially refuted Shawn's 55-map hypothesis (contour-rings dominate at 41 %, not numbers / benchmarks at 23 %), but the GS-side question is open: **what categories actually dominate GS FPs?** Without GS data the paper cannot say whether GS shows the predicted spot-height / water-feature concentration, the same contour-ring pattern as 55-map, or something else entirely.

**Asymmetry being closed**: the Discussion currently has detailed FP-class data on the 55-map side but only Shawn's manual-review intuition on the GS side. After this run, both corpuses will have empirical category distributions tabulated under the same prompt and the same closed list.

## 3. Existing pipeline review (`scripts/55maps-fp-classify.py`)

Read in full: 1,603 lines, complete and committed (Obs 302 driver commit `5040f5b4`).

### 3.1 Input format

`load_fps_for_run` (lines 413–452) reads a per-run review CSV with columns `candidate_id, verifier_probability, human_label, symbol_type, source_tile, map_name, x, y, buffer_metres, timestamp`. FP filter: `human_label == "not_mound"`. Each row produces an `FPRecord(run, candidate_id, map_name, x, y, source_tile)` — only the (x, y) UTM coordinates and `source_tile` are used downstream by the crop renderer and classifier. The `buffer_metres` column is empty for FPs (verified by spot-check).

### 3.2 Crop renderer (lines 257–389)

`render_crop(centroid_x, centroid_y, context_m=150, display_px=768)` opens the source GeoTIFF (resolved via `best_raster_for_point`, which scans `RASTERS_DIR`'s top-level `*.tif` files), reads a 150 m × 150 m window centred on the FP centroid (`boundless=True, fill_value=0` so edge-of-sheet candidates produce a correctly-sized image), and upscales to 768 px LANCZOS. Returns `None` if no raster covers the point.

`RASTERS_DIR` is hard-coded to `inputs/rasters/Russian1981_32635/` — the 55-map corpus directory. The 4 GS rasters live at `inputs/rasters/` (top level) under names `K-35-052-4_32635.tif`, `K-35-053-3_Elenovo.tif`, `K-35-062-2_Rakovski.tif`, `K-35-078-1_Lesovo.tif`. All four are EPSG:32635, ~5 m/px resolution. **The GS pipeline must override `RASTERS_DIR`** (verified by `rasterio.open` spot-check; see §5 for source).

### 3.3 Prompt (lines 206–238) — vocabulary anchor

Closed list of 10 categories: `number`, `benchmark`, `water-feature`, `contour-ring`, `vegetation`, `settlement`, `road-or-track`, `scale-bar-or-grid`, `none`, `other`. The prompt names Soviet 1980s topographic conventions explicitly, includes a Cyrillic example (БМ for benchmark), and asks for a single-JSON response with `category`, `confidence` (0.0–1.0), and `rationale` (one sentence). This prompt is reused **verbatim** for the GS side — symmetric methodology is required for cross-corpus comparability.

### 3.4 Distance metric

The 55-map pipeline does **not** use a distance metric. The FP filter is the human reviewer's `human_label == "not_mound"` decision, mediated through the review-candidates CSV. Distance never enters the 55-map FP enumeration. This is the key methodological asymmetry forced by the absence of GS-side human review (see §4).

### 3.5 Output format

- `fp_classifications.json` — per-FP record list with `run, candidate_id, map_name, x, y, source_tile, category, raw_category, confidence, rationale, success, error, input_tokens, output_tokens`.
- `category_distribution.json` — per-corpus / aggregate counts and percentages, confidence-weighted distribution, chi-square test (image vs text-track for the 55-map version).
- `cost_summary.json` — per-run and total token counts plus cost in USD (flex tier discount applied).
- `report.md` — synthesised report with per-corpus distribution, distractor-pull share, water-feature share, chi-square test, verdict, caveats.
- `figures/category_distribution.png` — stacked-bar chart per corpus.

### 3.6 Configuration constants

- Model: `gemini-3-flash` (with `gemini-3-flash-preview` fallback).
- Temperature: 0.0; thinking_level: MINIMAL; service tier: flex (50 % discount).
- Workers: 20 (ThreadPoolExecutor); retries: 3 with backoff [2, 4, 8] s.
- Cost hard cap: $5.00 USD.

## 4. Design decision 1 — FP-filter distance threshold

**Verdict**: **50 m as the primary threshold**. Run a sensitivity sweep at 25 m, 75 m, 100 m, and 125 m thresholds for transparency.

### 4.1 Threshold sensitivity table

Spot-check on the 371 verified-v1 full-scope detections vs the 569-mound reference (verified by `cKDTree` query at session start):

| Threshold (m) | TP-side count | FP-side count |
|:-:|:-:|:-:|
| 25 | 349 | 22 |
| 50 | 355 | **16** |
| 75 | 357 | 14 |
| 100 | 357 | 14 |
| 125 | 357 | 14 |
| 150 | 357 | 14 |

The FP set **plateaus at 14** from 75 m onwards — those 14 detections are >150 m from any reference mound on the 4-map corpus. Between 25 m and 75 m the count drops by 8 (from 22 to 14) — i.e. 8 detections sit in the 25–75 m band, where attribution is genuinely ambiguous (could be detector mis-localisation of a real mound, or a true FP near another visible feature).

### 4.2 Why 50 m as primary

Three converging anchors:

1. **GS attractor-pull cap (Obs 295)**: the deepest contiguous-from-zero shell significant on the GS corpus is **(0, 25] m** for text-HIGH-T0.7 and **(0, 50] m** for image-HIGH-T0.7 and SCALE4. Beyond 50 m, observed detection-mound co-occurrence on the GS corpus is statistically indistinguishable from random within-tile placement. A detection >50 m from any reference is therefore not associated with that reference under the within-tile null — i.e. the detection has no plausible reference-mound interpretation.
2. **GS F1 plateau (Obs 260 / extended-buffer-sweep)**: F1 plateaus at R = 25 m on the curator-corrected GS corpus. **Recall at 50 m equals recall at 25 m** (`results/gold-standard-extended-buffer-sweep-era2/evaluation.csv`: F1 0.871 at 25 m, 0.873 at 50 m — point estimates within 0.002, CIs overlap completely). Anything beyond 50 m cannot recover further TPs on this corpus.
3. **Symmetry with the 55-map side**: the 55-map pipeline accepts FPs labelled `not_mound` by a human reviewer who saw the 150 m crop. The 50 m threshold maps roughly to the same geometric scope a reviewer applied — rejecting candidates that obviously sit far from any visible mound.

Choosing 25 m would over-include the 22 / 16 difference (8 detections) where the model-vs-curator disagreement is plausibly mis-localisation rather than true FP. Choosing >75 m would under-count by excluding the 8 detections in the (50, 75] band — the very band Obs 296 identified as the 5–10× pull-rate gap between corpuses. **50 m is the principled break.**

### 4.3 Why a sweep

The 50 m primary verdict relies on independent anchors (Obs 260, Obs 295, F1-plateau geometry) that all converge but each carry methodological caveats. A sensitivity sweep at thresholds {25, 50, 75, 100, 125} m demonstrates whether the FP-class distribution is threshold-stable. If the dominant categories at 50 m and 25 m differ by more than ~15 percentage points, the result is threshold-fragile and must be reported as such. If they agree, we have stronger ground to stand on. Cost is trivial: at the union of all five thresholds, total unique FPs is bounded above by 22 (the 25 m FP-set is the union — every FP at any larger threshold is also an FP at 25 m).

### 4.4 Single value vs sweep — framing

**Run a single classification pass on the 25 m FP-set (22 detections), then re-aggregate at each threshold.** The 25 m FP-set is a strict superset of every larger-threshold FP-set on a one-dimensional distance line, so a single pass classifies every detection that could appear at any threshold; per-threshold aggregations are derived without re-querying the API. This is the cheapest and most thorough design.

## 5. Design decision 2 — sample size and sampling strategy

**Verdict**: **classify ALL 22 detections in the 25 m FP-set (no subsampling, no stratification)**.

### 5.1 Why no subsampling

The spec's "~80 GS FPs" estimate likely came from `(1 − precision) × n_detections` at the canonical operating point (precision ≈ 0.95 at 50 m on the era2 sweep × 414 image detections ≈ 21 expected FPs by definition; expansion to ~80 may have been a confused multiplication across all three pv-materialised conditions in Obs 295's analysis). Direct geometric query confirms only 14–22 detections lie >25 m from any reference. **N is one to two orders of magnitude smaller than the spec assumed.** No subsampling needed.

### 5.2 Sampling strategy

None. This is a census of every detection in the verified-v1 full-scope set whose nearest-reference distance exceeds 25 m. No random seed required (deterministic geometric query, EPSG:32635 planar distances, `cKDTree.query(k=1)`).

### 5.3 Confidence threshold

None. Filter only by distance. The verified-v1 set already represents the canonical operating point (4-of-5 vote_t, prob_t = 0.15 from `gold-standard-v2-greedy-v1-327tile.json`; verifier-v1 adversarial-text prompt). Subsetting further on `mound_probability` would deviate from the operating point used in the paper's headline GS results (per `extended-buffer-report.md` §2). **The detection set is fixed by the paper's existing operating-point decision.**

### 5.4 Stratification by map

Distribution of the 371 detections across the 4 maps (verified by `source_tile` parse): K-35-062-2 (143), K-35-053-3 (128), K-35-052-4 (89), K-35-078-1 (11). The Lesovo sheet (K-35-078-1) has only 11 detections total — likely <2 FPs at any threshold. Per-map analysis is not viable at this N; per-corpus analysis is. **Report per-corpus; flag per-map analysis as not statistically meaningful and skip.**

## 6. Design decision 3 — output path convention

**Verdict**: `results/gs-fp-classification/` — sibling to `results/55maps-fp-classification/`.

### 6.1 Rationale

Three output-path candidates were considered:

| Path | Pros | Cons |
|:--|:--|:--|
| `results/gs-fp-classification/` | Siblings 55-map dir (`results/55maps-fp-classification/`); easy to cross-reference in paper text ("see `results/{55maps,gs}-fp-classification/`") | Slightly opaque ("gs" abbreviation) |
| `results/h11/gold-standard-v2/fp-classification/` | Embeds inside the verified-v1 hypothesis tree where the source detections live | Asymmetric with the 55-map path; deeper; harder to see at a glance which results sit at the same analytical tier |
| `results/gold-standard-fp-classification/` | Verbose, follows the existing `results/gold-standard-*/` family | Longer; slightly off from `55maps-` prefix convention |

The first option wins on cross-referencing simplicity and analytical-tier symmetry, which is the primary use case (paper Discussion comparing the two distributions side-by-side). The "gs" prefix matches the existing `results/55maps-vs-gs-tp-localisation/` and `results/gold-standard-attractor-pull/` directories where "gs" is the project's accepted abbreviation. **Verified by the existing path family in `ls results/`.**

### 6.2 Files produced inside the directory

Mirroring the 55-map pipeline:

- `fp_classifications.json` — per-FP records.
- `category_distribution.json` — per-threshold and aggregate distributions, plus cross-corpus chi-square test against `results/55maps-fp-classification/category_distribution.json`.
- `cost_summary.json` — per-run token counts and cost.
- `report.md` — synthesised report with per-threshold tables, cross-corpus comparison, and Obs 302 follow-up framing.
- `figures/category_distribution.png` — stacked-bar chart with one bar per threshold + a 55-map aggregate reference bar.
- `figures/cross_corpus_comparison.png` — direct side-by-side 55-map-aggregate vs GS-aggregate stacked bars (the headline cross-corpus figure).

## 7. Design decision 4 — distance metric

**Verdict**: **Euclidean planar distance in EPSG:32635** via `scipy.spatial.cKDTree`.

### 7.1 Rationale

Three points converge:

1. **Project precedent**: `scripts/analyse_attractor_pull_gs.py` (Obs 295 driver, commit `430693bc`) uses exactly this approach — `cKDTree` over the curator-corrected reference (569 MultiPoints exploded to 569 single Points in EPSG:32635), `tree.query(k=1)` against detection centroids in the same projection. The script's docstring explicitly notes: "the curator GT is precise enough to support [direct geometric query]". Reusing the same distance definition gives the FP-filter geometric continuity with the attractor-pull analysis that derived the 25 m / 50 m thresholds in §4.
2. **CRS native to detections and reference**: both the verified-v1 GeoJSON (`outputs/h11/gold-standard-v2/verified-v1/verified_detections_full-scope.geojson`) and the reference (`inputs/vectors/references/mounds-reference.geojson`) are stored in EPSG:32635 — verified by reading the `crs` field of each file at session start. The 4 GS rasters are also EPSG:32635 at ~5 m/px resolution. **No reprojection needed.** UTM zone 35N is a metre-accurate planar projection across the 4-map extent (the 4 maps span L=314 011 to R=479 169 easting; B=4 631 256 to T=4 706 006 northing — well within zone 35N's distortion-free band).
3. **Geodetic precision over the area is sub-metre**: at the latitude of the GS corpus (~42°N), planar UTM distances differ from geodetic distances by <1 ppm at distances under 1 km. Threshold sensitivity in §4 uses 25 m increments, so the planar-vs-geodetic difference is far below the resolvable threshold. **Geodetic distance buys nothing here.**

### 7.2 Implementation

```python
from scipy.spatial import cKDTree
import geopandas as gpd

# Reference: explode MultiPoint to Point.
ref = gpd.read_file("inputs/vectors/references/mounds-reference.geojson")
ref = ref.explode(index_parts=False).reset_index(drop=True)
coords = np.column_stack([ref.geometry.x.values, ref.geometry.y.values])
tree = cKDTree(coords)

# Detections: already Point geometry in EPSG:32635.
det = gpd.read_file(
    "outputs/h11/gold-standard-v2/verified-v1/verified_detections_full-scope.geojson"
)
det_coords = np.column_stack([det.geometry.x.values, det.geometry.y.values])
distances, _ = tree.query(det_coords, k=1)
fp_mask = distances > FP_DISTANCE_THRESHOLD_M  # 25 m to capture the union
```

This block is added to the new sibling script (§8) ahead of the FP enumeration step. Raster-pixel distance (an alternative considered) was rejected because it would force a reprojection step that adds nothing (~5 m/px raster resolution × 5 m/px planar metre = direct correspondence; rounding to whole pixels would lose precision the bare metric already preserves).

## 8. Adaptation requirements

**Verdict**: write a sibling script `scripts/gs-fp-classify.py` that imports the prompt, crop renderer, classification call, aggregation helpers, output writers, and cost accounting from `scripts/55maps-fp-classify.py`. Do **not** modify `scripts/55maps-fp-classify.py` itself (per task constraint and per the principle that the published 55-map results in `results/55maps-fp-classification/` must remain reproducible from a clean checkout).

### 8.1 What changes

Five things change between the 55-map driver and the GS-side sibling:

1. **Input**: read `outputs/h11/gold-standard-v2/verified-v1/verified_detections_full-scope.geojson` instead of four review CSVs.
2. **FP filter**: distance-based (§4) instead of `human_label == "not_mound"`.
3. **Raster directory**: `inputs/rasters/` instead of `inputs/rasters/Russian1981_32635/`. (`best_raster_for_point` already iterates by glob, so the only change is the directory.)
4. **Run labelling**: the 55-map driver labels by run (T0.3, T0.7, image, text-MIN). The GS driver has only one operating point. Use threshold values as the "run" axis: `T25`, `T50`, `T75`, `T100`, `T125` — i.e. the same FP-set classified once but tabulated five times by threshold. This preserves the existing `per_run_distribution` output schema with no logic changes.
5. **Statistical test**: drop the image-vs-text chi-square test (irrelevant on the GS side; only one operating point). Replace with a chi-square test of the **GS aggregate vs the 55-map aggregate** — the cross-corpus headline test that Obs 302 was missing.

### 8.2 What is reused (imported, not duplicated)

Direct imports from `scripts.55maps_fp_classify` (note: the script's filename uses hyphens, not underscores; Python needs `importlib` for hyphenated module names, or we copy the helper list and call them by re-importing through a direct file load):

- `CLASSIFICATION_PROMPT` (verbatim — the cross-corpus comparability hinge).
- `CATEGORIES`, `DISTRACTOR_PULL_CATEGORIES`, `GS_FAILURE_MODE_CATEGORIES` (constants).
- `render_crop`, `best_raster_for_point` (with `RASTERS_DIR` overridden via module-level monkey-patch or a thin wrapper).
- `unwrap_payload`, `normalise_category`, `call_gemini_classify`, `render_and_classify` (the API integration layer).
- `compute_cost`, `write_classifications_json`, `write_distribution_json`, `write_distribution_figure`, `write_cost_summary` (output writers).

### 8.3 What is new in the sibling script

- A `load_gs_fps(detection_path, reference_path, threshold_m)` function that reads the verified-v1 geojson, computes nearest-reference distances via `cKDTree`, applies the threshold, and returns a list of `FPRecord` objects with `run` set to `f"T{threshold_m:.0f}"`.
- A new `chi_square_gs_vs_55map(gs_counts, fifty_five_map_counts_path)` helper that pools the 55-map aggregate from `results/55maps-fp-classification/category_distribution.json` and runs the same chi-square test pattern as `chi_square_image_vs_text` but with corpus-level rows (GS aggregate vs 55-map aggregate).
- A new `write_cross_corpus_figure` that renders the side-by-side stacked bars.
- A new `write_report_md_gs` that frames the result against Obs 296 / Obs 302 explicitly, including a row-by-row comparison table of the GS aggregate vs the 55-map aggregate per category.

### 8.4 Why a sibling script, not a wrapper or a refactor

A wrapper around `scripts/55maps-fp-classify.py` would require modifying its CLI to accept the new input mode, which violates the task constraint ("do NOT modify the existing classification script"). A refactor that pulls shared helpers into a new module (`lib_fp_classify.py`) is methodologically cleaner but creates code-churn risk in the published 55-map artefacts at exactly the moment the paper is being drafted. **Sibling script is the lowest-risk, lowest-surface-area choice** — both scripts can re-run independently, and the 55-map result remains reproducible from its existing commit hash.

## 9. Execution plan

### 9.1 Pre-launch validation (no API calls)

- Run the FP enumeration step alone, log the `FPRecord` list to stdout, confirm count equals 22 (or current value at run-time). Sanity-check that `best_raster_for_point` resolves a raster for every record (the 4 GS rasters span the corpus extent without gaps).
- Render and save (to a scratch directory) the first 3 crops as PNGs; spot-check that they look like sensible 150 m crops centred on real map content.
- Confirm `config.GOOGLE_API_KEY` is in environment; confirm `gemini-3-flash` (or `-preview`) is in the `client.models.list()` output.

### 9.2 Execution command

```bash
python scripts/gs-fp-classify.py \
  --output-dir results/gs-fp-classification \
  --workers 4 \
  --thresholds 25,50,75,100,125
```

`--workers 4` (vs the 55-map driver's default of 20) reflects the small N (22 detections); higher concurrency saves negligible wall time and risks hitting the flex-tier rate limit on a single small batch.

### 9.3 Expected runtime and cost

- 22 detections × 1 classification call each = 22 calls (single classification pass; the threshold sweep is post-hoc aggregation).
- Per-call cost from `cost_summary.json` of the 55-map run: $0.5071 / 1119 calls ≈ $0.00045 per call, flex tier.
- Expected total: 22 × $0.00045 ≈ **$0.01 USD** (well below the spec's $0.05 estimate; the spec was based on the now-known-wrong N≈80).
- Expected wall-clock: ~30–60 s (the 55-map driver hit 1.7 calls/s; at 4 workers and 22 calls, wall is dominated by the slowest call, probably ~10 s plus ramp-up).

### 9.4 Error handling

Same retry / backoff regime as the 55-map driver: 3 retries with [2, 4, 8] s backoff per call; `BLOCKED_OR_EMPTY` failures recorded as `success=False` in the JSON; cost hard cap remains $5.00 (will not trigger at this N). NO_RASTER_COVERAGE failures recorded with `success=False, error="NO_RASTER_COVERAGE"` — at this point the pre-launch validation should have flagged any such cases.

### 9.5 Post-execution validation

- Confirm `len(fp_classifications.json)` equals the 25 m FP count and `failed == 0`.
- Confirm the categories sum to 100 % within rounding for each threshold's column in `category_distribution.json`.
- Spot-check 3 random rows of `fp_classifications.json` against the matching crop image (manually): does the `category` agree with what the crop visually shows?
- Run `ruff check scripts/gs-fp-classify.py` on the new script.
- Run `npx markdownlint-cli2 results/gs-fp-classification/report.md` (and on this plan).

## 10. Verification and integration

### 10.1 Cross-corpus comparison

The headline output is a 2-row × 10-column contingency table: GS aggregate (sum across all classified GS FPs at threshold = 50 m primary) versus 55-map aggregate (1,119 classified FPs from Obs 302). Chi-square test on this table directly tests the asymmetric-failure-mode hypothesis — both arms (Shawn's prediction and the alternative). Pearson residuals per category identify which categories drive any cross-corpus difference.

### 10.2 Integration into Obs 302's follow-up

- A new working-notes entry (Obs 305 or next free number — Obs 304 was committed at `6d798e83` after this plan was drafted; check the head of `working-notes.md` at integration time) documenting the GS-side result. Title pattern: `Observation N: GS FP-class distribution under the same prompt — [headline finding]`.
- Update Obs 302's "Caveats" section to remove the "No GS-side comparator" caveat and replace it with a forward reference to the new Obs.
- Update `planning/paper-writeup-continuity.md` Item #1's status (mark as `[x] done` with the date and a one-line summary; do **not** delete per the global "checklists are append-only" rule).
- The paper Discussion's cross-corpus failure-mode paragraph can now cite both sides empirically. If the GS-side result confirms Shawn's water-feature / spot-height intuition, the asymmetric-failure-mode framing is supported. If GS also shows contour-ring dominance, the paper should report this convergence as a stronger conclusion: contour-ring confusion is a corpus-invariant detector failure mode, not a 55-map-specific generalisation gap.

### 10.3 Integration into the paper Discussion

A single small paragraph: "Applying the same Soviet-1980s topographic-symbol prompt to the GS-side false positives (n = X at distance > 50 m from any reference mound) produced category distribution Y. The cross-corpus chi-square test ... [supports / refutes / does not statistically distinguish] the asymmetric-failure-mode reading proposed in the Discussion's [section reference]."

## 11. Pre-launch checklist

The user should confirm each of the following before approving execution:

1. The 50 m primary FP-filter distance threshold is acceptable; the {25, 50, 75, 100, 125} m sweep is acceptable as the sensitivity analysis.
2. Classifying the full 25 m FP-set (~22 detections, no subsampling, no stratification) is acceptable.
3. Results location `results/gs-fp-classification/` is acceptable; the user does not prefer the alternative under `results/h11/gold-standard-v2/`.
4. Euclidean planar distance in EPSG:32635 is acceptable as the distance metric (matches `scripts/analyse_attractor_pull_gs.py` precedent).
5. The sibling-script approach (`scripts/gs-fp-classify.py` reusing the 55-map driver's helpers without modifying it) is acceptable, and the new script may be committed alongside results.
6. **API Call Review Gate** (per global CLAUDE.md): the run uses Gemini 3 Flash, real-time (not Batch API, given the small N), ~22 calls, expected cost $0.01–0.05 USD with flex-tier discount; hard cap $5.00.
7. Pre-launch validation (§9.1) is completed and reported back to the user before the API call begins.
8. The plan to mirror the verification + integration steps in §10 (Obs entry, plan-doc update, paper-Discussion paragraph) is acceptable.

## 12. Risks and mitigations

### 12.1 GS detections without raster coverage

- **Risk**: A detection might lie in a region where no raster covers the (x, y) point — `best_raster_for_point` returns `None` and the detection is skipped.
- **Mitigation**: Pre-launch validation §9.1 enumerates the FP set and renders the first 3 crops as a smoke test; full crop rendering for all 22 FPs runs as part of execution and any `NO_RASTER_COVERAGE` failure is logged with `success=False, error="NO_RASTER_COVERAGE"` and visible in the report. Given the 4 GS rasters' bounds (verified at session start) span the corpus extent contiguously and the verified-v1 GeoJSON's source-tile field references rasters within this set, no coverage gap is anticipated. If one occurs, document it in the report and exclude from the aggregate.

### 12.2 Threshold sensitivity (the result depends on the cutoff choice)

- **Risk**: At 25 m the dominant category might differ markedly from at 50 m (because 8 detections in the 25–50 m band are likely the geometrically ambiguous ones).
- **Mitigation**: Run the sensitivity sweep (§4.4) and report all five thresholds in `report.md`. If the dominant category changes by >15 percentage points across thresholds, flag the result as threshold-fragile and recommend the paper Discussion cite the 50 m primary alongside a sensitivity-range footnote.

### 12.3 N too small for chi-square

- **Risk**: Chi-square test against 55-map aggregate (1,119) may have expected counts <5 in some cells of the GS row (~22 N spread across 10 categories means several cells will have expected counts ~2–3).
- **Mitigation**: Use Fisher's exact test (or Monte Carlo permutation test on the chi-square statistic) instead of asymptotic chi-square if expected counts <5 in >20 % of cells. Standard fallback; `scipy.stats.chi2_contingency` reports expected counts so the decision is data-driven post-classification.

### 12.4 API failure of the entire batch (unlikely)

- **Risk**: Flex-tier rate limit, transient outage, model deprecation.
- **Mitigation**: Same retry / backoff regime as the 55-map driver; failure logged per-call with `success=False`. A second invocation (cost still ~$0.01) is cheap if the first fails partly. Cost hard cap $5.00 prevents runaway.

### 12.5 Cross-corpus prompt drift (the 55-map prompt was tuned to 55-map content)

- **Risk**: The closed-list categories (e.g. `contour-ring`, `vegetation`) were chosen empirically from 55-map FP review; a GS FP might fall outside this list (e.g. if "spot-height" is the right category but the prompt forces it into `number`).
- **Mitigation**: Per Obs 302 caveat 3, the `number` / spot-height confound is already documented as a known interpretability limit. The closed list is reused **verbatim** for cross-corpus comparability — drift would be the alternative (re-tune for GS, lose comparability). Report the rationale-string distribution alongside the category counts in the JSON output so a second-pass review can disambiguate `number`-as-distractor vs `number`-as-spot-height post-hoc.

### 12.6 Threshold under-counts true FPs

- **Risk**: Some detections within 50 m of a reference might still be true FPs (the detection lies near a real mound by chance, but the detector triggered on a different visible feature in the crop).
- **Mitigation**: This is the unavoidable cost of synthetic distance-based FP labelling without human review. The paper Discussion must state explicitly that the GS-side FP set is a distance-defined under-approximation of the true FP set. The 55-map side has the analogous opposite bias (human reviewers may label ambiguous detections inconsistently). Both biases are documented.

## 13. References

- Specification: `planning/paper-writeup-continuity.md` lines 1437–1444.
- Obs 302 (FP-class diagnostic — 55-map side): `docs/notes/reflections/working-notes.md` ≈ line 14947.
- Obs 296 (failure-of-generalisation reinterpretation): `docs/notes/reflections/working-notes.md` ≈ line 14532.
- Obs 295 (GS attractor-pull cap = 25 m): `docs/notes/reflections/working-notes.md` ≈ line 14473.
- Obs 260 (student-GT positional jitter ~25 m): cited in Obs 295 §4.3, Obs 296 §4.
- Existing 55-map driver: `scripts/55maps-fp-classify.py` (1,603 lines, commit `5040f5b4`).
- Existing 55-map results: `results/55maps-fp-classification/` (commit `e552ad46`).
- GS attractor-pull driver (distance-metric precedent): `scripts/analyse_attractor_pull_gs.py` (commit `430693bc`).
- GS detection set: `outputs/h11/gold-standard-v2/verified-v1/verified_detections_full-scope.geojson` (371 features; commit `d59798ac` per `run.meta.json`).
- Curator reference: `inputs/vectors/references/mounds-reference.geojson` (569 mounds, EPSG:32635 MultiPoint).
