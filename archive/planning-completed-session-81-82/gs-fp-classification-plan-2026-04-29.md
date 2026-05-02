# Gold-standard FP-classification plan (Item #1, Obs 302 follow-up)

> **⚠️ SUPERSEDED 2026-05-01.** This planning document is preserved
> for historical reference. The work it describes was executed in
> Session 81 (commits `ee4f18cb`, `9fa6db4e`, `ec21c8ef`; Obs 306–308);
> see `planning/paper-writeup-continuity.md` §"Session 81 closure
> roll-up" (Item 1 row in the Items 1–16 status table) and the run
> output at `results/55maps-fp-classification/report.md` for the
> current state. Do not act on items in this file as if they are
> pending.

**Date**: 2026-04-29 (revised 2026-04-29 with corrected framing + four user-confirmed decisions).
**Author**: Claude Code (Opus 4.7) for Shawn Ross.
**Status**: APPROVED — ready for execution by a fresh executor agent (see §14).
**Specification source**: `planning/paper-writeup-continuity.md` lines 1437–1444.

## 1. Executive summary

This plan operationalises the gold-standard (GS) side of Observation 302's FP-class classification — the missing comparator that prevents the paper Discussion from making a clean cross-corpus asymmetric-failure-mode claim. The 55-map side ran on 1,119 human-reviewed FPs across four corrected runs (`results/55maps-fp-classification/report.md`); the GS side applies the same closed-list classifier to all 371 detections in the verified-v1 full-scope set, then partitions them into TP-side and FP-side buckets via distance-from-curator-GT against the curator-corrected reference (`mounds-reference.geojson`, 569 mounds, EPSG:32635).

The two corpora apply human judgement at different points in the pipeline (see §2), but with comparable rigour: the GS curator GT was triple-checked and manually re-centred to within ~1 px of each mound's true centre — sub-metre positional precision — for the 2022 Sobotkova paper and again for this project. Distance-from-curator-GT on the GS corpus is therefore a high-precision geometric filter, not a proxy.

Recommended approach: **a sibling script (`scripts/gs-fp-classify.py`)** copied from `scripts/55maps-fp-classify.py` and adapted for GS inputs (verified-v1 GeoJSON instead of review CSVs, top-level `inputs/rasters/` instead of `inputs/rasters/Russian1981_32635/`). The 55-map driver is **not modified**.

Four user-confirmed design decisions (2026-04-29):

1. **FP-filter distance threshold**: **50 m primary** plus a 5-point sensitivity sweep at {25, 50, 75, 100, 125} m, rationale §5.
2. **Sample size and sampling**: **classify ALL 371 GS detections** (TP-side and FP-side together — the TP bucket serves as a sanity check on classifier reliability), rationale §6.
3. **Script approach**: **sibling script** (`scripts/gs-fp-classify.py`) — copy-then-adapt, not refactor or wrapper, rationale §9.
4. **API spend**: **approved up to a $5 USD ceiling**; estimated ~$0.05 USD for all 371 detections at flex tier, rationale §10.3.

Expected output: 371 classifications via a single API pass, then a single FP-side aggregation at the 50 m primary plus four sensitivity columns at {25, 75, 100, 125} m. Cost ≤ $0.05 USD (well below the $5 ceiling); wall-clock ≤ 10 min at the planned 4 workers.

## 2. Framing — different mechanisms, comparable rigour

This section corrects an incomplete characterisation of the cross-corpus data flow that shaped the original (2026-04-29 morning) draft of this plan. The corrected framing was confirmed by the user 2026-04-29 and is the operating frame for everything below.

### 2.1 The 55-map FP-classification pipeline is two-layered

1. **Geometric step.** `scripts/evaluate_detections.py` runs Hungarian one-to-one matching against the student / crowdsourced GT (`inputs/vectors/references/student-mounds-55maps-reviewed.geojson`, 4,744 mounds) at a primary 50 m tolerance. Detections that do not match within tolerance become **geometric FPs**.
2. **Human review override.** `scripts/review_candidates.py` presents only the geometric-FP candidates in a Streamlit UI with five concentric tolerance rings at 50, 75, 100, 125, and 150 m (verified at `scripts/review_candidates.py` line 94: `_BUFFER_BANDS_DEFAULT: tuple[int, ...] = (50, 75, 100, 125, 150)`). A reviewer labels each as `mound` or `not_mound`; the human label fully overrides the geometric label.
3. **Final FP set on 55-map side.** Rows with `human_label == "not_mound"` in the five review CSVs across the four corrected 55-map runs (verified at `scripts/55maps-fp-classify.py` line 434: `if row.get("human_label", "").strip() != "not_mound": continue`).

### 2.2 The GS side has NO equivalent human-review pass on detections

Verified 2026-04-29: zero review CSVs exist under `results/gold-standard-*/` or `outputs/h11/gold-standard-v2/`. **BUT** the GS curator GT (`inputs/vectors/references/mounds-reference.geojson`, 569 mounds) was hand-curated by the user across two passes for the 2022 Sobotkova paper, then re-checked again for the present project — **triple-checked overall**, with each discovery point manually centred to within ~1 pixel of the mound's true centre. Sub-metre positional precision, deliberately eliminating jitter at the GT-creation stage. Provenance memory ids: `2026-04-29-d5a6332b0788` (GS curation history) and `2026-04-29-bedbb2494542` (55-map jitter clarification).

### 2.3 Implication: distance-from-curator-GT is NOT a proxy on the GS corpus

It is a high-precision geometric filter equivalent in rigour to the 55-map's per-detection human review. The two corpora apply human judgement at different points in the pipeline:

- **55-map**: human judgement applied per-detection AFTER VLM output (Streamlit review of borderline candidates). Necessary because student GT has ~25 m positional jitter that was characterised but **not corrected** during the review (only the offset rings were measured, not the centroids re-centred).
- **GS**: human judgement applied per-GT-mound BEFORE VLM output (during curator-corrected GT creation). The jitter was eliminated upstream during the user's manual centring pass.

**Different mechanisms, comparable rigour.** The Discussion / Methods of the paper should present this asymmetry honestly but should NOT frame the GS approach as a "geometric proxy" or "shortcut" — that framing belongs to the incomplete understanding the original plan-draft worked from. The GS-side filter operates on a triple-checked sub-metre reference; the 55-map-side filter operates on a noisy student GT plus a human-review override applied to mismatches. Both pipelines defensibly produce a curator-grade FP set; the GS path simply moved the human work upstream.

## 3. Background

**Obs 302 caveat** (`docs/notes/reflections/working-notes.md` ≈ line 15000):

> No GS-side comparator. This diagnostic measured 55-map only. The GS half of Shawn's hypothesis (spot-heights / water-features dominant) cannot be directly tested here without running the same classifier on GS FPs. A natural follow-up; estimated cost ~$0.05 (GS has ~80 FPs at canonical operating point per Obs 295 / Obs 298).

**Obs 296 framing** (line ≈ 14555): the cross-corpus per-detection mid-distance pull rate at (50, 75] m is 5–10× higher on the 55-map corpus than on the GS corpus. Shawn's manual-review intuition was that 55-map FPs concentrate on numbers / benchmarks (distractor-pull) while GS FPs concentrate on spot-heights / water-features (a different generalisation regime, post-calibration). Obs 302 partially refuted Shawn's 55-map hypothesis (contour-rings dominate at 41 %, not numbers / benchmarks at 23 %), but the GS-side question is open: **what categories actually dominate GS FPs?** Without GS data the paper cannot say whether GS shows the predicted spot-height / water-feature concentration, the same contour-ring pattern as 55-map, or something else entirely.

**Asymmetry being closed**: the Discussion currently has detailed FP-class data on the 55-map side but only Shawn's manual-review intuition on the GS side. After this run, both corpuses will have empirical category distributions tabulated under the same prompt and the same closed list.

## 4. Existing pipeline review (`scripts/55maps-fp-classify.py`)

Read in full: 1,603 lines, complete and committed (Obs 302 driver commit `5040f5b4`).

### 4.1 Input format

`load_fps_for_run` (lines 413–452) reads a per-run review CSV with columns `candidate_id, verifier_probability, human_label, symbol_type, source_tile, map_name, x, y, buffer_metres, timestamp`. FP filter: `human_label == "not_mound"`. Each row produces an `FPRecord(run, candidate_id, map_name, x, y, source_tile)` — only the (x, y) UTM coordinates and `source_tile` are used downstream by the crop renderer and classifier. The `buffer_metres` column is empty for FPs (verified by spot-check).

### 4.2 Crop renderer (lines 257–389)

`render_crop(centroid_x, centroid_y, context_m=150, display_px=768)` opens the source GeoTIFF (resolved via `best_raster_for_point`, which scans `RASTERS_DIR`'s top-level `*.tif` files), reads a 150 m × 150 m window centred on the FP centroid (`boundless=True, fill_value=0` so edge-of-sheet candidates produce a correctly-sized image), and upscales to 768 px LANCZOS. Returns `None` if no raster covers the point.

`RASTERS_DIR` is hard-coded to `inputs/rasters/Russian1981_32635/` — the 55-map corpus directory. The 4 GS rasters live at `inputs/rasters/` (top level) under names `K-35-052-4_32635.tif`, `K-35-053-3_Elenovo.tif`, `K-35-062-2_Rakovski.tif`, `K-35-078-1_Lesovo.tif`. All four are EPSG:32635, ~5 m/px resolution. **The GS pipeline must override `RASTERS_DIR`** (verified by `rasterio.open` spot-check; see §8 for source).

### 4.3 Prompt (lines 206–238) — vocabulary anchor

Closed list of 10 categories: `number`, `benchmark`, `water-feature`, `contour-ring`, `vegetation`, `settlement`, `road-or-track`, `scale-bar-or-grid`, `none`, `other`. The prompt names Soviet 1980s topographic conventions explicitly, includes a Cyrillic example (БМ for benchmark), and asks for a single-JSON response with `category`, `confidence` (0.0–1.0), and `rationale` (one sentence). This prompt is reused **verbatim** for the GS side — symmetric methodology is required for cross-corpus comparability.

### 4.4 Distance metric

The 55-map pipeline does **not** use a distance metric. The FP filter is the human reviewer's `human_label == "not_mound"` decision, mediated through the review-candidates CSV. Distance never enters the 55-map FP enumeration. The GS side is structurally different (§2): the human work was done upstream during GT centring, so the FP filter on the GS side is geometric distance against a curator-corrected reference (see §5 and §8).

### 4.5 Output format

- `fp_classifications.json` — per-FP record list with `run, candidate_id, map_name, x, y, source_tile, category, raw_category, confidence, rationale, success, error, input_tokens, output_tokens`.
- `category_distribution.json` — per-corpus / aggregate counts and percentages, confidence-weighted distribution, chi-square test (image vs text-track for the 55-map version).
- `cost_summary.json` — per-run and total token counts plus cost in USD (flex tier discount applied).
- `report.md` — synthesised report with per-corpus distribution, distractor-pull share, water-feature share, chi-square test, verdict, caveats.
- `figures/category_distribution.png` — stacked-bar chart per corpus.

### 4.6 Configuration constants

- Model: `gemini-3-flash` (with `gemini-3-flash-preview` fallback).
- Temperature: 0.0; thinking_level: MINIMAL; service tier: flex (50 % discount).
- Workers: 20 (ThreadPoolExecutor); retries: 3 with backoff [2, 4, 8] s.
- Cost hard cap: $5.00 USD.

## 5. Design decision 1 — FP-filter distance threshold

**User-confirmed (2026-04-29)**: accept the original recommendation as-is — **50 m primary** plus a 5-point sensitivity sweep at {25, 50, 75, 100, 125} m. Anchored to Obs 295 (GS attractor-pull cap = 25/50 m by stratum) and Obs 260 (F1 plateau at 25 m on curator-corrected GS). No change from the prior verdict.

The sub-sections below preserve the rationale unchanged.

### 5.1 Threshold sensitivity table

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

### 5.2 Why 50 m as primary

Three converging anchors:

1. **GS attractor-pull cap (Obs 295)**: the deepest contiguous-from-zero shell significant on the GS corpus is **(0, 25] m** for text-HIGH-T0.7 and **(0, 50] m** for image-HIGH-T0.7 and SCALE4. Beyond 50 m, observed detection-mound co-occurrence on the GS corpus is statistically indistinguishable from random within-tile placement. A detection >50 m from any reference is therefore not associated with that reference under the within-tile null — i.e. the detection has no plausible reference-mound interpretation.
2. **GS F1 plateau (Obs 260 / extended-buffer-sweep)**: F1 plateaus at R = 25 m on the curator-corrected GS corpus. **Recall at 50 m equals recall at 25 m** (`results/gold-standard-extended-buffer-sweep-era2/evaluation.csv`: F1 0.871 at 25 m, 0.873 at 50 m — point estimates within 0.002, CIs overlap completely). Anything beyond 50 m cannot recover further TPs on this corpus.
3. **Symmetry with the 55-map side**: the 55-map pipeline accepts FPs labelled `not_mound` by a human reviewer who saw the 150 m crop. The 50 m threshold maps roughly to the same geometric scope a reviewer applied — rejecting candidates that obviously sit far from any visible mound.

Choosing 25 m would over-include the 22 / 16 difference (8 detections) where the model-vs-curator disagreement is plausibly mis-localisation rather than true FP. Choosing >75 m would under-count by excluding the 8 detections in the (50, 75] band — the very band Obs 296 identified as the 5–10× pull-rate gap between corpuses. **50 m is the principled break.**

### 5.3 Why a sweep

The 50 m primary verdict relies on independent anchors (Obs 260, Obs 295, F1-plateau geometry) that all converge but each carry methodological caveats. A sensitivity sweep at thresholds {25, 50, 75, 100, 125} m demonstrates whether the FP-class distribution is threshold-stable. If the dominant categories at 50 m and 25 m differ by more than ~15 percentage points, the result is threshold-fragile and must be reported as such. If they agree, we have stronger ground to stand on. Cost is trivial: at the union of all five thresholds, total unique FPs is bounded above by 22 (the 25 m FP-set is the union — every FP at any larger threshold is also an FP at 25 m).

### 5.4 Single value vs sweep — framing

**SUPERSEDED 2026-04-29 by Decision 2** (§6): the operating set is now **all 371 detections, not the 25 m FP-set**. The original framing here was: "Run a single classification pass on the 25 m FP-set (22 detections), then re-aggregate at each threshold." That logic still holds for the FP-side aggregation — once 371 detections are classified, post-hoc partitioning at any threshold ≤ 150 m is free — but the input set is now the full detection list, not a distance-filtered subset. See §6 for rationale.

## 6. Design decision 2 — sample size and sampling strategy

**User-confirmed (2026-04-29)**: **classify ALL 371 GS detections** in the verified-v1 full-scope set — both the TP-side bucket (≤25 m, n ≈ 349) and the FP-side bucket (>25 m, n ≈ 22). No subsampling, no stratification.

> **Prior verdict (SUPERSEDED 2026-04-29)**: "classify ALL 22 detections in the 25 m FP-set (no subsampling, no stratification)". The original plan restricted the input to the 25 m FP-set on the assumption that classifying TPs added cost without information. The user's reasoning for the larger scope is recorded below.

### 6.1 User's reasoning for classifying TPs as well as FPs

At sub-metre GT precision (§2), classifying the TP bucket is a real sanity check on classifier reliability. The Soviet 1980s topographic vocabulary has no "burial mound" category — the closed list is `number`, `benchmark`, `water-feature`, `contour-ring`, `vegetation`, `settlement`, `road-or-track`, `scale-bar-or-grid`, `none`, `other`. If the classifier is well-calibrated against that vocabulary, the TP bucket should classify predominantly as `none` (the prompt's intended fallback when no symbol-vocabulary match exists) or `other`. A TP bucket dominated by, say, `contour-ring` would indicate the classifier is hallucinating Soviet-vocabulary categories onto correctly-detected mounds — a finding that would change how the FP-side categories are interpreted.

The cost difference between the 22-FP design and the 371-detection design is ~$0.04 USD (estimated below in §10.3). Trivial against a $5 USD ceiling.

### 6.2 Sampling strategy

None. This is a census of every detection in the verified-v1 full-scope set. No random seed required.

### 6.3 Confidence threshold

None. Filter only by distance for the post-classification aggregation. The verified-v1 set already represents the canonical operating point (4-of-5 vote_t, prob_t = 0.15 from `gold-standard-v2-greedy-v1-327tile.json`; verifier-v1 adversarial-text prompt). Subsetting further on `mound_probability` would deviate from the operating point used in the paper's headline GS results (per `extended-buffer-report.md` §2). **The detection set is fixed by the paper's existing operating-point decision.**

### 6.4 Stratification by map

Distribution of the 371 detections across the 4 maps (verified by `source_tile` parse): K-35-062-2 (143), K-35-053-3 (128), K-35-052-4 (89), K-35-078-1 (11). The Lesovo sheet (K-35-078-1) has only 11 detections total — likely <2 FPs at any threshold. Per-map FP-side analysis is not viable at this N; per-corpus analysis is. **Report per-corpus; flag per-map analysis as not statistically meaningful and skip.**

### 6.5 TP-side reporting expectation

The TP-side (≤25 m) report should tabulate the category distribution of the ~349 TP detections under the same closed list, with the explicit hypothesis that `none` and `other` should dominate. Any non-trivial frequency of vocabulary categories (e.g. `contour-ring` > 10 % of TPs) is a finding worth flagging — it would reshape the interpretation of the FP-side numbers.

## 7. Design decision 3 — output path convention

**User-confirmed (2026-04-29, implicit via decision 3)**: `results/gs-fp-classification/` — sibling to `results/55maps-fp-classification/`. Carried forward unchanged from the original plan; the user's "sibling script" decision (§9) likewise implies a sibling output directory.

### 7.1 Rationale

Three output-path candidates were considered:

| Path | Pros | Cons |
|:--|:--|:--|
| `results/gs-fp-classification/` | Siblings 55-map dir (`results/55maps-fp-classification/`); easy to cross-reference in paper text ("see `results/{55maps,gs}-fp-classification/`") | Slightly opaque ("gs" abbreviation) |
| `results/h11/gold-standard-v2/fp-classification/` | Embeds inside the verified-v1 hypothesis tree where the source detections live | Asymmetric with the 55-map path; deeper; harder to see at a glance which results sit at the same analytical tier |
| `results/gold-standard-fp-classification/` | Verbose, follows the existing `results/gold-standard-*/` family | Longer; slightly off from `55maps-` prefix convention |

The first option wins on cross-referencing simplicity and analytical-tier symmetry, which is the primary use case (paper Discussion comparing the two distributions side-by-side). The "gs" prefix matches the existing `results/55maps-vs-gs-tp-localisation/` and `results/gold-standard-attractor-pull/` directories where "gs" is the project's accepted abbreviation. **Verified by the existing path family in `ls results/`.**

### 7.2 Files produced inside the directory

Mirroring the 55-map pipeline (filenames suggest "fp_" but include the TP-side bucket per Decision 2):

- `fp_classifications.json` — per-detection records for all 371 detections, including a `nearest_reference_distance_m` field and a `bucket` field (`tp_le25` or `fp_gt25`) computed at the 25 m primary; per-threshold buckets are computed in the aggregation step, not stored per-record.
- `category_distribution.json` — TP-side and FP-side distributions, per-threshold FP-side aggregates at {25, 50, 75, 100, 125} m, plus the cross-corpus chi-square test against `results/55maps-fp-classification/category_distribution.json`.
- `cost_summary.json` — per-run token counts and cost.
- `report.md` — synthesised report with TP-side reliability check, FP-side per-threshold tables, cross-corpus comparison, and Obs 302 follow-up framing.
- `figures/category_distribution.png` — stacked-bar chart with TP-side and per-threshold FP-side columns plus a 55-map aggregate reference bar.
- `figures/cross_corpus_comparison.png` — direct side-by-side 55-map-aggregate vs GS-FP-aggregate (50 m primary) stacked bars (the headline cross-corpus figure).

## 8. Distance metric (no design choice — methodological precedent)

**Carried forward unchanged from the original plan**: **Euclidean planar distance in EPSG:32635** via `scipy.spatial.cKDTree`. This is not one of the four user-confirmed decisions because there is no real choice to make — it follows from the project precedent (`scripts/analyse_attractor_pull_gs.py`) and the native CRS of the inputs.

### 8.1 Rationale

Three points converge:

1. **Project precedent**: `scripts/analyse_attractor_pull_gs.py` (Obs 295 driver, commit `430693bc`) uses exactly this approach — `cKDTree` over the curator-corrected reference (569 MultiPoints exploded to 569 single Points in EPSG:32635), `tree.query(k=1)` against detection centroids in the same projection. The script's docstring explicitly notes: "the curator GT is precise enough to support [direct geometric query]". Reusing the same distance definition gives the FP-filter geometric continuity with the attractor-pull analysis that derived the 25 m / 50 m thresholds in §5.
2. **CRS native to detections and reference**: both the verified-v1 GeoJSON (`outputs/h11/gold-standard-v2/verified-v1/verified_detections_full-scope.geojson`) and the reference (`inputs/vectors/references/mounds-reference.geojson`) are stored in EPSG:32635 — verified by reading the `crs` field of each file at session start. The 4 GS rasters are also EPSG:32635 at ~5 m/px resolution. **No reprojection needed.** UTM zone 35N is a metre-accurate planar projection across the 4-map extent (the 4 maps span L=314 011 to R=479 169 easting; B=4 631 256 to T=4 706 006 northing — well within zone 35N's distortion-free band).
3. **Geodetic precision over the area is sub-metre**: at the latitude of the GS corpus (~42°N), planar UTM distances differ from geodetic distances by <1 ppm at distances under 1 km. Threshold sensitivity in §5 uses 25 m increments, so the planar-vs-geodetic difference is far below the resolvable threshold. **Geodetic distance buys nothing here.**

### 8.2 Implementation

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
# Decision 2: classify ALL 371 detections; partition post-hoc.
# fp_mask is computed for reporting/aggregation only:
fp_mask = distances > FP_DISTANCE_THRESHOLD_M  # 25 m primary buckets the union
```

This block is added to the new sibling script (§9) ahead of the classification step, but the result is used only for record annotation (`bucket`, `nearest_reference_distance_m`) and post-hoc aggregation. Every one of the 371 detections is classified, regardless of bucket. Raster-pixel distance (an alternative considered) was rejected because it would force a reprojection step that adds nothing (~5 m/px raster resolution × 5 m/px planar metre = direct correspondence; rounding to whole pixels would lose precision the bare metric already preserves).

## 9. Design decision 4 — adaptation approach (sibling script)

**User-confirmed (2026-04-29)**: **SIBLING SCRIPT**. Copy `scripts/55maps-fp-classify.py` as `scripts/gs-fp-classify.py` and adapt for GS inputs. Do NOT refactor the 55-map script and do NOT write a wrapper. Rationale (user, paraphrased): the GS pipeline has no `human_label` step; copy-then-adapt avoids tangling the two pipelines.

> **Note on implementation pattern**: the original plan suggested *importing* helpers from the 55-map driver. The user's confirmed decision is to **copy-then-adapt**, i.e. duplicate the helper functions into the new script and edit them locally. This is more code-duplication but keeps the two scripts fully independent (no cross-imports to maintain when either side evolves). The lists in §9.2 below describe what to copy from the 55-map driver, not what to import.

### 9.1 What changes between 55-map driver and GS sibling

Five things change between the 55-map driver and the GS-side sibling:

1. **Input**: read `outputs/h11/gold-standard-v2/verified-v1/verified_detections_full-scope.geojson` instead of four review CSVs.
2. **FP filter**: distance-based against `inputs/vectors/references/mounds-reference.geojson` (§5, §8) instead of `human_label == "not_mound"`. Applied **post-classification** (Decision 2): all 371 detections classified, partitioned by distance for aggregation only.
3. **Raster directory**: `inputs/rasters/` instead of `inputs/rasters/Russian1981_32635/`. (`best_raster_for_point` already iterates by glob, so the only change is the directory constant.)
4. **Run labelling**: the 55-map driver labels by run (T0.3, T0.7, image, text-MIN). The GS driver has only one operating point. Use a single `run="GS_full"` label per record; per-threshold and TP/FP-side bucketing happens in the aggregation step from the `nearest_reference_distance_m` field.
5. **Statistical test**: drop the image-vs-text chi-square test (irrelevant on the GS side; only one operating point). Replace with a chi-square test of the **GS-FP aggregate (50 m primary) vs the 55-map aggregate** — the cross-corpus headline test that Obs 302 was missing.

### 9.2 What is copied (then adapted in place) from the 55-map driver

- `CLASSIFICATION_PROMPT` (verbatim — the cross-corpus comparability hinge).
- `CATEGORIES`, `DISTRACTOR_PULL_CATEGORIES`, `GS_FAILURE_MODE_CATEGORIES` (constants).
- `render_crop`, `best_raster_for_point` (rebind `RASTERS_DIR` to `inputs/rasters/`).
- `unwrap_payload`, `normalise_category`, `call_gemini_classify`, `render_and_classify` (the API integration layer; verbatim).
- `compute_cost`, `write_classifications_json`, `write_distribution_json`, `write_distribution_figure`, `write_cost_summary` (output writers; minor schema additions for the `bucket`, `nearest_reference_distance_m`, and per-threshold fields).

### 9.3 What is new in the sibling script

- A `load_gs_detections(detection_path, reference_path)` function that reads the verified-v1 geojson, computes nearest-reference distances via `cKDTree`, and returns a list of records carrying the distance and detection geometry. **No threshold-based filter**: every detection is returned, per Decision 2.
- A `bucket_records(records, threshold_m)` helper used at aggregation time to partition records into TP-side (≤ threshold) and FP-side (> threshold) for reporting at each of {25, 50, 75, 100, 125} m.
- A new `chi_square_gs_vs_55map(gs_fp_counts, fifty_five_map_counts_path)` helper that pools the 55-map aggregate from `results/55maps-fp-classification/category_distribution.json` and runs a chi-square test with corpus-level rows (GS-FP-aggregate at 50 m primary vs 55-map aggregate).
- A new `write_cross_corpus_figure` that renders the side-by-side stacked bars.
- A new `write_report_md_gs` that frames the result against Obs 296 / Obs 302 explicitly, includes the TP-side reliability check (§6.5), and includes a row-by-row comparison table of the GS-FP aggregate vs the 55-map aggregate per category.

### 9.4 Why a sibling script, not a wrapper or a refactor

A wrapper around `scripts/55maps-fp-classify.py` would require modifying its CLI to accept the new input mode, which violates the user's stated decision. A refactor that pulls shared helpers into a new module (`lib_fp_classify.py`) is methodologically cleaner but creates code-churn risk in the published 55-map artefacts at exactly the moment the paper is being drafted. **Sibling script is the lowest-risk, lowest-surface-area choice** — both scripts can re-run independently, and the 55-map result remains reproducible from its existing commit hash.

## 10. Execution plan

### 10.1 Pre-launch validation (no API calls)

- Run the detection-loading step alone, log the count and the distance-bucket histogram (TP ≤ 25 m, FP > 25 m at thresholds 25/50/75/100/125 m). Confirm total = 371 and the 25 m FP-set ≈ 22.
- Sanity-check that `best_raster_for_point` resolves a raster for every record (the 4 GS rasters span the corpus extent without gaps).
- Render and save (to a scratch directory) the first 3 crops as PNGs — one TP-side and two FP-side; spot-check that they look like sensible 150 m crops centred on real map content.
- Confirm `config.GOOGLE_API_KEY` is in environment; confirm `gemini-3-flash` (or `-preview`) is in the `client.models.list()` output.

### 10.2 Execution command

```bash
python scripts/gs-fp-classify.py \
  --output-dir results/gs-fp-classification \
  --workers 4 \
  --thresholds 25,50,75,100,125
```

`--workers 4` (vs the 55-map driver's default of 20) reflects the modest N (371 detections); higher concurrency on flex tier risks 429s without saving meaningful wall time. The `--thresholds` flag drives only the post-classification aggregation step; the API call set is fixed at 371 regardless.

### 10.3 Expected runtime and cost

- 371 detections × 1 classification call each = 371 calls (single classification pass; the threshold sweep is post-hoc aggregation).
- Per-call cost from `cost_summary.json` of the 55-map run: $0.5071 / 1119 calls ≈ $0.00045 per call, flex tier.
- Expected total: 371 × $0.00045 ≈ **$0.17 USD** under the per-call rate. The user's $0.05 estimate (recorded above as "~$0.05 USD" in §1) reflects an expectation that GS crops are slightly cheaper per call than 55-map crops; either figure is well within the **$5 USD ceiling approved by the user 2026-04-29**.
- Expected wall-clock: ~5–10 min at 4 workers (55-map driver throughput ≈ 1.7 calls/s with similar concurrency settings; 371 / 1.7 ≈ 220 s ≈ 4 min steady-state plus ramp-up).

> **API Call Review Gate satisfied (2026-04-29)**: model = Gemini 3 Flash (`gemini-3-flash`, fallback `gemini-3-flash-preview`); mode = real-time (not Batch API, given the small N); calls = 371; expected cost $0.05–$0.17 USD with flex-tier discount; user-approved ceiling $5.00 USD; in-script cost hard cap $5.00 USD.

### 10.4 Error handling

Same retry / backoff regime as the 55-map driver: 3 retries with [2, 4, 8] s backoff per call; `BLOCKED_OR_EMPTY` failures recorded as `success=False` in the JSON; cost hard cap remains $5.00 (will not trigger at this N). NO_RASTER_COVERAGE failures recorded with `success=False, error="NO_RASTER_COVERAGE"` — at this point the pre-launch validation should have flagged any such cases.

### 10.5 Post-execution validation

- Confirm `len(fp_classifications.json)` equals 371 and `failed == 0` (or document any failures).
- Confirm the categories sum to 100 % within rounding for the TP-side column and each FP-side threshold column in `category_distribution.json`.
- Spot-check 3 random rows of `fp_classifications.json` against the matching crop image (manually): does the `category` agree with what the crop visually shows?
- TP-side sanity check (§6.5): is the TP bucket dominated by `none` / `other`? Flag any vocabulary-category frequency > 10 % on the TP side.
- Run `ruff check scripts/gs-fp-classify.py` on the new script.
- Run `npx markdownlint-cli2 results/gs-fp-classification/report.md` (and on this plan).

## 11. Verification and integration

### 11.1 Cross-corpus comparison

The headline output is a 2-row × 10-column contingency table: GS-FP aggregate (sum across the FP-side bucket at threshold = 50 m primary) versus 55-map aggregate (1,119 classified FPs from Obs 302). Chi-square test on this table directly tests the asymmetric-failure-mode hypothesis — both arms (Shawn's prediction and the alternative). Pearson residuals per category identify which categories drive any cross-corpus difference.

### 11.2 Integration into Obs 302's follow-up

- A new working-notes entry (Obs 305 or next free number — Obs 304 was committed at `6d798e83` after this plan was drafted; check the head of `working-notes.md` at integration time) documenting the GS-side result. Title pattern: `Observation N: GS FP-class distribution under the same prompt — [headline finding]`.
- Update Obs 302's "Caveats" section to remove the "No GS-side comparator" caveat and replace it with a forward reference to the new Obs.
- Update `planning/paper-writeup-continuity.md` Item #1's status (mark as `[x] done` with the date and a one-line summary; do **not** delete per the global "checklists are append-only" rule).
- The paper Discussion's cross-corpus failure-mode paragraph can now cite both sides empirically. If the GS-side result confirms Shawn's water-feature / spot-height intuition, the asymmetric-failure-mode framing is supported. If GS also shows contour-ring dominance, the paper should report this convergence as a stronger conclusion: contour-ring confusion is a corpus-invariant detector failure mode, not a 55-map-specific generalisation gap.

### 11.3 Integration into the paper Discussion

A single small paragraph: "Applying the same Soviet-1980s topographic-symbol prompt to the GS-side false positives (n = X at distance > 50 m from any curator-corrected reference mound, on a triple-checked sub-metre GT) produced category distribution Y. The cross-corpus chi-square test ... [supports / refutes / does not statistically distinguish] the asymmetric-failure-mode reading proposed in the Discussion's [section reference]." The Methods should describe the **different-mechanisms-comparable-rigour** framing from §2 above so reviewers do not read the GS approach as a shortcut.

## 12. Pre-launch checklist

Most items below were resolved by the user's 2026-04-29 decisions. Items still pending are flagged.

1. **RESOLVED 2026-04-29**: The 50 m primary FP-filter distance threshold is acceptable; the {25, 50, 75, 100, 125} m sweep is acceptable as the sensitivity analysis (Decision 2).
2. **RESOLVED 2026-04-29**: Classifying ALL 371 GS detections (TP-side + FP-side together) is acceptable (Decision 1; supersedes the earlier 22-FP plan).
3. **RESOLVED 2026-04-29 (implicit)**: Results location `results/gs-fp-classification/` is acceptable as the sibling-script's natural sibling output (Decision 3).
4. **RESOLVED 2026-04-29 (no choice required)**: Euclidean planar distance in EPSG:32635 follows from project precedent and native CRS — not a user-decision branch.
5. **RESOLVED 2026-04-29**: The sibling-script approach — copy `scripts/55maps-fp-classify.py` to `scripts/gs-fp-classify.py` and adapt for GS inputs — is the user-confirmed implementation pattern (Decision 3).
6. **RESOLVED 2026-04-29**: API Call Review Gate satisfied — Gemini 3 Flash, real-time, 371 calls, $0.05–0.17 USD expected under a $5 USD ceiling, flex tier (Decision 4). See §10.3 for the formal gate record.
7. **PENDING (executor agent)**: Pre-launch validation (§10.1) must be completed and reported back to the user before the API call begins. The executor agent should pause for confirmation between validation and the production classification run.
8. **PENDING (executor agent + user, post-run)**: Verification and integration steps in §11 (Obs entry, plan-doc update, paper-Discussion paragraph) execute after the run completes. Plan in this section is the user-confirmed approach.

## 13. Risks and mitigations

### 13.1 GS detections without raster coverage

- **Risk**: A detection might lie in a region where no raster covers the (x, y) point — `best_raster_for_point` returns `None` and the detection is skipped.
- **Mitigation**: Pre-launch validation §10.1 enumerates the detection set and renders sample crops as a smoke test; full crop rendering for all 371 detections runs as part of execution and any `NO_RASTER_COVERAGE` failure is logged with `success=False, error="NO_RASTER_COVERAGE"` and visible in the report. Given the 4 GS rasters' bounds (verified at session start) span the corpus extent contiguously and the verified-v1 GeoJSON's source-tile field references rasters within this set, no coverage gap is anticipated. If one occurs, document it in the report and exclude from the aggregate.

### 13.2 Threshold sensitivity (the FP-side result depends on the cutoff choice)

- **Risk**: At 25 m the dominant FP-side category might differ markedly from at 50 m (because 8 detections in the 25–50 m band are likely the geometrically ambiguous ones).
- **Mitigation**: Run the sensitivity sweep (§5.3) and report all five thresholds in `report.md`. If the dominant category changes by >15 percentage points across thresholds, flag the result as threshold-fragile and recommend the paper Discussion cite the 50 m primary alongside a sensitivity-range footnote.

### 13.3 N too small for chi-square

- **Risk**: Chi-square test against 55-map aggregate (1,119) may have expected counts <5 in some cells of the GS-FP row (~22 N at 50 m primary spread across 10 categories means several cells will have expected counts ~2–3). Note: the *TP-side* row has n ≈ 349 and is not chi-square-bounded.
- **Mitigation**: Use Fisher's exact test (or Monte Carlo permutation test on the chi-square statistic) instead of asymptotic chi-square if expected counts <5 in >20 % of cells. Standard fallback; `scipy.stats.chi2_contingency` reports expected counts so the decision is data-driven post-classification.

### 13.4 API failure of the entire batch (unlikely)

- **Risk**: Flex-tier rate limit, transient outage, model deprecation.
- **Mitigation**: Same retry / backoff regime as the 55-map driver; failure logged per-call with `success=False`. A second invocation (cost still ~$0.05–0.17) is cheap if the first fails partly. Cost hard cap $5.00 prevents runaway.

### 13.5 Cross-corpus prompt drift (the 55-map prompt was tuned to 55-map content)

- **Risk**: The closed-list categories (e.g. `contour-ring`, `vegetation`) were chosen empirically from 55-map FP review; a GS FP might fall outside this list (e.g. if "spot-height" is the right category but the prompt forces it into `number`).
- **Mitigation**: Per Obs 302 caveat 3, the `number` / spot-height confound is already documented as a known interpretability limit. The closed list is reused **verbatim** for cross-corpus comparability — drift would be the alternative (re-tune for GS, lose comparability). Report the rationale-string distribution alongside the category counts in the JSON output so a second-pass review can disambiguate `number`-as-distractor vs `number`-as-spot-height post-hoc.

### 13.6 Distance threshold may misclassify edge cases

- **Risk**: Some detections within 50 m of a reference might still be true FPs (the detection lies near a real mound by chance, but the detector triggered on a different visible feature in the crop). Conversely, a small fraction of detections >50 m might be TPs that the detector localised loosely.
- **Mitigation**: With a sub-metre triple-checked GT (§2), residual mis-localisation is bounded by the detector's centroid precision (typically tens of metres at this resolution), not by GT noise. The 50 m threshold is therefore a tight, principled boundary, not a noisy one. The paper Discussion should describe the GS-side FP definition as "detections farther than 50 m from any curator-corrected reference mound on a sub-metre GT" — accurate, not apologetic. The 55-map side has the analogous bias (human reviewers may label ambiguous detections inconsistently); both biases are documented.

### 13.7 TP-side vocabulary leakage (new with Decision 1)

- **Risk**: If the classifier assigns vocabulary categories (e.g. `contour-ring`) to TP detections at substantial frequency, the FP-side numbers become harder to interpret — the categories would not be cleanly "what the classifier saw when it wasn't a mound" but "what the classifier's calibration draws everything towards".
- **Mitigation**: Report the TP-side distribution explicitly in `report.md` (§6.5). If `none`/`other` < 80 % of the TP bucket, the paper Discussion must temper the FP-side categorical interpretation. This is exactly the sanity check that motivated Decision 1.

## 14. Next step (plan ready for execution)

This plan is **APPROVED for execution** as of 2026-04-29 (all four user-confirmed decisions recorded above; API spend approved up to $5 USD ceiling).

**Recommended next move**: dispatch a fresh executor agent with the following scope.

1. **Write** `scripts/gs-fp-classify.py` by copying `scripts/55maps-fp-classify.py` and adapting per §9. Do NOT modify the 55-map driver.
2. **Pre-launch validate** per §10.1; report counts, sample crops, and any anomalies back before any API call.
3. **Run** the production classification on all 371 detections at flex tier per §10.2, observing the in-script cost cap of $5.00 and the user-approved $5.00 ceiling.
4. **Write** outputs to `results/gs-fp-classification/` per §7.2 (including the TP-side reliability check from §6.5).
5. **Commit** the new script and the results directory in two logical commits (one for the script, one for the outputs); **push** both before any review per project policy.
6. **Report** back to the user: (a) the headline GS-FP category distribution at 50 m primary, (b) the TP-side sanity-check result, (c) the cross-corpus chi-square outcome, (d) any threshold-sensitivity flags from §13.2.
7. **Defer** the working-notes Obs entry, the paper-writeup-continuity tick, and the paper-Discussion paragraph (§11) to a subsequent session — these depend on the user reviewing the run output before they should be written.

The plan document above is auditable (all superseded verdicts marked with date stamps, prior reasoning preserved). The executor should treat §1, §2, and §5–§9 (decisions and adaptation requirements) as authoritative, and §10–§11 as the operational and integration playbook.

## 15. References

- Specification: `planning/paper-writeup-continuity.md` lines 1437–1444.
- Obs 302 (FP-class diagnostic — 55-map side): `docs/notes/reflections/working-notes.md` ≈ line 14947.
- Obs 296 (failure-of-generalisation reinterpretation): `docs/notes/reflections/working-notes.md` ≈ line 14532.
- Obs 295 (GS attractor-pull cap = 25 m): `docs/notes/reflections/working-notes.md` ≈ line 14473.
- Obs 260 (student-GT positional jitter ~25 m): cited in Obs 295 §4.3, Obs 296 §4.
- Existing 55-map driver: `scripts/55maps-fp-classify.py` (1,603 lines, commit `5040f5b4`).
- 55-map review-candidates UI (concentric tolerance rings 50/75/100/125/150 m): `scripts/review_candidates.py` line 94.
- Existing 55-map results: `results/55maps-fp-classification/` (commit `e552ad46`).
- GS attractor-pull driver (distance-metric precedent): `scripts/analyse_attractor_pull_gs.py` (commit `430693bc`).
- GS detection set: `outputs/h11/gold-standard-v2/verified-v1/verified_detections_full-scope.geojson` (371 features; commit `d59798ac` per `run.meta.json`).
- Student / 55-map crowdsourced GT: `inputs/vectors/references/student-mounds-55maps-reviewed.geojson` (4,744 mounds).
- Curator reference: `inputs/vectors/references/mounds-reference.geojson` (569 mounds, EPSG:32635 MultiPoint; triple-checked sub-metre — see §2.2).
- Memory references (provenance): `2026-04-29-d5a6332b0788` (GS curation history); `2026-04-29-bedbb2494542` (55-map jitter clarification). Stored at `~/personal-assistant/memories/memories.jsonl`.
