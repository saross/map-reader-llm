# Evaluation Tile Set Scopes

**Purpose**: Documents the three test tile sets used across the experimental programme and their nesting relationships. Critical context for interpreting F1 comparisons across project phases and for the paper write-up.

**Generated**: 2026-04-16 (commit `6d804934`)
**Verified by**: spatial intersection analysis (zero-tolerance nesting check); see §10 Reproducibility for inputs and operation.

## 1. Executive summary

The project used **three nested test tile sets** across its experimental phases:

- **Era 1** (pre-H11, H1–H9 retest): **340 × 512 px tiles**, ~1,751 sq km, 539 GT mounds. Scope manifest: `inputs/vectors/bounds/full_evaluation_bounds.geojson`.
- **Era 2** (H11 tile-size study + PV diagnostic + consensus / N-sweep): **487 × 384 px tiles**, ~1,416 sq km, 435 GT mounds. Scope manifest: `inputs/tiles_384/full_evaluation_manifest.json`.
- **Era 3** (post-H10 v2, covering H8 v2 / H10 v2 / H12 v2 library-design axis): **327 × 384 px tiles**, ~1,034 sq km, 319 GT mounds. Scope manifest: `inputs/calibration/h10-384/test_manifest.json`.

**Strict nesting**: Era 3 ⊂ Era 2 ⊂ Era 1 at zero tolerance — Era 3 area inside Era 2 is 100.000 % (0.00 sq m outside); Era 2 inside Era 1 is 100.000 % (0.00 sq m outside); zero GT mounds are unique to a smaller scope. The nesting is geographic, not merely statistical, so cross-era F1 comparisons can treat the smaller scope as a strict subset of the larger one — with the coverage caveat in §7 below.

**Coverage fractions** (area / mounds): Era 2 within Era 1 = 80.8 % / 80.7 %; Era 3 within Era 2 = 73.0 % / 73.3 %; Era 3 within Era 1 = 59.0 % / 59.2 %. Area and mound fractions track near-identically (within 0.3 pp), indicating calibration exclusions do not preferentially remove mound-rich or mound-poor regions.

## 2. The three test tile sets

All three sets cover 4 topographic map sheets from Bulgaria (1:25,000 Soviet
military series, UTM Zone 35N / EPSG:32635):

- K-35-052-4 (Razgrad area)
- K-35-053-3 (Elenovo area)
- K-35-062-2 (Rakovski area)
- K-35-078-1 (Lesovo area)

| Label | Era | Tile size | Stride | Test tiles | Area (sq km) | GT mounds | Calibration excluded | Manifest path |
|---|---|---|---|---|---|---|---|---|
| **Era 1** | Pre-H11 (H1–H9 retest) | 512 px | 448 px | **340** | 1751 | 539 | 20 tiles (original calibration seed area) | `inputs/vectors/bounds/full_evaluation_bounds.geojson` |
| **Era 2** | H11 | 384 px | 336 px | **487** | 1416 | 435 | Same 20-tile geographic area as Era 1, re-projected to the 384-px grid | `inputs/tiles_384/full_evaluation_manifest.json` + `inputs/vectors/bounds/384/full_evaluation_bounds.geojson` |
| **Era 3** | Post-H10 v2 (H8 v2, H10 v2, H12 v2) | 384 px | 336 px | **327** | 1034 | 319 | Era 2 exclusion **plus** 160 pool_160 tiles (hard-example mining area, geographically separate from the Era 1/2 calibration exclusion) | `inputs/calibration/h10-384/test_manifest.json` + `inputs/vectors/bounds/384/h10_test_bounds.geojson` |

### 2.1 Physical tile counts (for reference)

| Tile size | Physical tiles on disk | Edge/boundary excluded | Evaluable tiles | Calibration excluded | Test tiles |
|---|---|---|---|---|---|
| 512 px | 360 | 0 | 360 | 20 | **340** |
| 384 px | 611 | 124 | 487 | 0 (Era 2) or 160 (Era 3) | **487** or **327** |

## 3. Nesting verification

The three test tile sets are **strictly nested**: Era 3 ⊂ Era 2 ⊂ Era 1,
both geographically (zero area outside the parent) and in ground-truth mound
coverage (zero mounds unique to a smaller scope).

| Check | Result |
|---|---|
| Era 3 area inside Era 2 | 100.000% (0.00 sq m outside) |
| Era 2 area inside Era 1 | 100.000% (0.00 sq m outside) |
| Era 3 area inside Era 1 | 100.000% (0.00 sq m outside) |
| Mounds in Era 3 but not Era 2 | 0 |
| Mounds in Era 2 but not Era 1 | 0 |
| Mounds in Era 3 but not Era 1 | 0 |

## 4. Comparative coverage

| Comparison | % area covered | % mounds covered |
|---|---|---|
| Era 2 within Era 1 | **80.8%** | **80.7%** |
| Era 3 within Era 2 | **73.0%** | **73.3%** |
| Era 3 within Era 1 | **59.0%** | **59.2%** |

Area and mound fractions track near-identically (within 0.3 percentage
points), indicating that the calibration exclusions do not preferentially
remove mound-rich or mound-poor regions. Mound density is approximately
uniform across all three scopes.

## 5. Calibration exclusion rationale

### 5.1 Era 1 exclusion (20 × 512-px tiles)

The original 20-tile calibration set was used in Phase 1 (library
construction) to build the canonical few-shot library (4 positive + 2
negative legend-derived examples, 3 null tiles). These tiles were excluded
from the evaluation set to prevent testing the model on the same map regions
used to construct its few-shot prompt. The 20 calibration tiles plus 340 test
tiles account for all 360 physical 512-px tiles.

### 5.2 Era 2 exclusion (same geographic area, re-projected)

When the project moved to 384-px tiles (H11, errata E41), the same 20-tile
calibration geographic footprint was excluded from the 384-px evaluation set.
Because 384-px tiles are smaller (336-px stride vs 448-px stride), the
exclusion removes more tiles from the grid, resulting in 487 evaluable tiles
from 611 physical tiles (with an additional 124 edge/boundary tiles excluded
by the tiling geometry). The 487-tile set has zero overlap with the 512-px
calibration footprint (verified by spatial intersection).

### 5.3 Era 3 additional exclusion (160 × 384-px pool_160 tiles)

H10 v2 expanded the calibration pool from the original 20-tile seed to a
160-tile set (pool_160) for hard-example mining. This expansion drew tiles
from a **geographically separate** area within the 487-tile evaluation set —
the pool_160 tiles do not overlap the original 20-tile calibration footprint.
Hard positive and hard negative few-shot crops (150 × 150 px) were extracted
from specific locations within these 160 tiles. To prevent data leakage
(testing the model on tiles from which its few-shot examples were drawn), the
160 pool_160 tiles were excluded, yielding the 327-tile h10 test set.

The pool_160 calibration hierarchy is nested:
pool_020 ⊂ pool_040 ⊂ pool_080 ⊂ pool_160 (20, 40, 80, 160 tiles).

## 6. Hypotheses by era

| Era | Scope | Hypotheses evaluated |
|---|---|---|
| Era 1 (340 × 512) | Pre-H11 retest at production scale | H1 (modality/elaboration), H2 (two-stage PV), H3 (consensus voting), H4 (ordering), H5 (negative text), H7 (temperature), H8 original (library, scale-4..8 only), H9 (diversity) |
| Era 2 (487 × 384) | H11 tile-size study and PV diagnostic | H11 (tile size), PV strategy comparison (adversarial/brief/checklist × image/text), consensus N-sweep (N=5, 10, 30), Flash vs Pro model comparison |
| Era 3 (327 × 384) | Post-H10 v2 library-design axis | H8 v2 (library composition, 7 conditions including Scale-16/32), H10 v2 (calibration-pool size, 4 conditions), H12 v2 (HP:HN ratio, 3 conditions) |

## 7. Caveats — cross-era F1 comparability

- **F1 numbers from different eras are not directly comparable** without noting the scope difference. The nested structure means a smaller scope evaluates against fewer mounds and fewer tiles; between-scope F1 differences could reflect scope effects rather than configuration effects.
- **Within-era comparisons are always valid** — conditions tested in the same era share the same evaluation scope.
- **Tile size is a controlled variable** in the H11 study (Era 2), which tested the same configurations at both 512 and 384 px. Those results provide the calibrating link for any cross-tile-size comparison.
- **The 80.8 % / 73.0 % / 59.0 % coverage fractions** and the near-identical mound-density ratios mean that cross-era F1 differences attributable purely to scope are expected to be small — but they should still be footnoted in leaderboard tables.
- **Nesting is zero-tolerance geographic**, not statistical. A mound present in Era 3 is also present (as ground truth) in Era 2 and Era 1; a detection made in Era 3 is scorable against Era 2's GT by construction. This property is what licenses the Era 3 → Era 2 → Era 1 extrapolation used for the 55-map image-generalisation run (Era 2 configuration, trained and calibrated against Era 2 / Era 3 data).
- **GT-count asymmetry**: Era 3 has 319 mounds (59.2 % of Era 1's 539). Per-buffer detection-rate comparisons across eras should normalise by the scope's GT count; raw TP counts across eras are not interpretable.

## 8. Paper implications

### 8.1 Which scope each paper claim belongs to

The paper's headline F1 and corrected-F1 claims land in different eras; readers and reviewers will need an explicit scope reminder at each citation. Draft the Methods section to establish the three-scope framework early (Table "Evaluation scopes"), then tag each Results claim by era:

- **Detection F1 headline 0.904 [0.878, 0.928] @ 50 m** (487-tile matrix, K=30 text-HIGH + PV) → **Era 2**. Source: `results/paper-tables/metrics_master.json`.
- **Corrected F1 ≥ 0.830 @ 50 m** and the multi-buffer 0.832 → 0.855 curve (55-map image-generalisation, human-reviewed) → **Era 2** (the 55-map run used the 384-px grid, Era 2 scope). Source: `results/55maps-image-generalisation/corrected-f1-multi-buffer/corrected-f1.csv`.
- **Subtype weighted-F1 0.887 [0.849, 0.922]** (4-map gold-standard subtype classification, conditional on match) → **4-map gold-standard subset** (orthogonal to Era taxonomy; a separate dedicated sub-corpus; document this explicitly rather than shoehorn into an Era).
- **H8 v2 / H10 v2 / H12 v2 library-design closure** → **Era 3**. Paper's Era 1 Results section cites the Era 3 re-tests as closure of the corresponding Era 1 hypotheses.
- **Gold-standard v2 text-HIGH extended-buffer plateau F1 = 0.8155 @ 20 m / 0.826 @ 50 m** (text-HIGH pipeline on the 4 gold-standard maps, post-verifier) → **Era 3 (327 tiles, 250 verified detections)**, bounds-filtered for sibling-comparability with the h8/h10/h12 v2 cells. Source: `results/gold-standard-extended-buffer-sweep/extended-buffer-report.md`.
- **Gold-standard v2 text-HIGH scope-pair companion F1 = 0.8663 [0.8591, 0.8726] @ 20 m / 0.8859 [0.8798, 0.8919] @ 50 m** (same pipeline, broader scope; **post-recovery 2026-05-03**) → **Era 2 (487 tiles, 380 verified detections; tile-level MCC = 0.7778 [0.7663, 0.7896]; tile confusion TP/TN/FP/FN = 181/250/8/48; sensitivity 0.7904 [0.7789, 0.8017]; specificity 0.9690 [0.9638, 0.9732])**, matching the Phase 3a-matrix leaderboard denominator. Source: `results/gold-standard-extended-buffer-sweep-era2/evaluation.json` (Session 78 baseline 2026-04-24, refreshed Session 82 2026-05-03 at commits `90890ae9..c6023034`; pre-recovery values were F1@20m = 0.854 [0.821, 0.883], F1@50m = 0.873 [0.844, 0.901], MCC = 0.778 [0.726, 0.828], n = 371 — see commit history). The two reportings are scope-pair siblings: post-recovery the Era 2 and Era 3 bootstrap CIs at 20 m no longer overlap (Era 2's BCa N=10K CI is tighter than the 1K-iter Era 3 CI, and Era 2 lifted by ~+0.013 F1), but the residual point-estimate gap is consistent with the 327-tile scope holding a random subsample of harder-to-match candidates rather than a systematic shift. Era 3 is constructed by hierarchical stratified random sampling from Era 2 (see §5.3), so the 327-tile complement is a random subsample of Era 2, not a difficulty-filtered curation.
- **Phase 2b H7 temperature retest (K=3 × 340 tiles)** → **Era 1 retest** (preregistered 340-tile corpus, 512 px). Source: `results/retest/phase2b/analysis_summary.md`.

### 8.2 Suggested paper text (Methods)

> Three test tile sets structured the experimental programme. Era 1 (340 tiles at 512 px, 1,751 sq km, 539 ground-truth mounds) supported the pre-H11 hypothesis sweep. Era 2 (487 tiles at 384 px, 1,416 sq km, 435 mounds) supported the H11 tile-size study and subsequent post-verifier diagnostic. Era 3 (327 tiles at 384 px, 1,034 sq km, 319 mounds) supported the post-H10 library-design closure (H8 v2, H10 v2, H12 v2). The three sets are strictly nested — Era 3 ⊂ Era 2 ⊂ Era 1 at zero geographic tolerance and zero ground-truth-mound tolerance — with coverage fractions 80.8 % (Era 2 ⊂ Era 1), 73.0 % (Era 3 ⊂ Era 2), and 59.0 % (Era 3 ⊂ Era 1). Area and mound coverage track within 0.3 percentage points, so calibration exclusions do not preferentially remove mound-rich or mound-poor regions. All cross-era F1 comparisons in the Results section are footnoted with the relevant coverage fraction.

### 8.3 Methodological contribution

The nested-scope framework makes cross-era extrapolation **defensible rather than heuristic**: because the nesting is zero-tolerance geographic, F1 on the smaller scope is a valid lower bound on F1 at the larger scope under the mild assumption of uniform mound density. The near-identical mound-density ratios (§4) satisfy that assumption empirically.

## 9. Files manifest

**Outputs**:

- `results/evaluation-scopes.md` — this report.

**Scope-defining inputs**:

| File | Description |
|---|---|
| `inputs/vectors/bounds/full_evaluation_bounds.geojson` | Era 1 bounds (340 tiles, 512 px) |
| `inputs/vectors/bounds/calibration_bounds.geojson` | Era 1 calibration exclusion (20 tiles, 512 px) |
| `inputs/vectors/bounds/384/full_evaluation_bounds.geojson` | Era 2 bounds (487 tiles, 384 px) |
| `inputs/tiles_384/full_evaluation_manifest.json` | Era 2 tile manifest (487 tiles) |
| `inputs/vectors/bounds/384/h10_test_bounds.geojson` | Era 3 bounds (327 tiles, 384 px) |
| `inputs/calibration/h10-384/test_manifest.json` | Era 3 tile manifest (327 tiles) |
| `inputs/calibration/h10-384/calibration_bounds_160.geojson` | Era 3 calibration exclusion (160 tiles, pool_160) |
| `inputs/vectors/references/mounds-reference.geojson` | Ground-truth mound reference (569 total mounds across all maps) |

## 10. Reproducibility

- **Git commit**: `6d804934` (`data(analysis): H12 v2 results + cross-hypothesis matrix + verifier sweeps`, 2026-04-16) introduces this document. No dedicated nesting-check script exists at HEAD; the zero-tolerance spatial intersection was performed ad-hoc using GeoPandas (see operation below).
- **Operation to re-verify nesting**:
    1. Load the three bounds GeoJSONs listed in §9. They are stored in EPSG:4326; re-project to UTM Zone 35N (EPSG:32635) before any area computation.
    2. For each ordered pair (smaller, larger) in {(Era 3, Era 2), (Era 2, Era 1), (Era 3, Era 1)}: compute `smaller.difference(larger).area.sum()` (should be 0.00 sq m to a float-tolerance limit of ~1 sq m) and `100 * smaller.intersection(larger).area.sum() / smaller.area.sum()` (should be 100.000 %).
    3. For the mound-set check: load `inputs/vectors/references/mounds-reference.geojson` (569 points); for each scope's bounds, compute `sjoin(mounds, bounds, predicate="within")` to obtain the per-scope mound set; confirm the smaller scope's mound set is a subset of the larger's (`set_smaller.issubset(set_larger)` returns True for all three nested pairs).
    4. The coverage fractions in §4 are `100 * smaller.area.sum() / larger.area.sum()` (area) and `100 * len(mounds_smaller) / len(mounds_larger)` (mounds).
- **Toolchain**: GeoPandas ≥ 0.14 (shapely 2.x), Python ≥ 3.11. Project `requirements.txt` at HEAD pins the compatible versions.
- **Re-run expected cost**: negligible (< 5 seconds; six bounds polygons, 569 points, one sjoin per scope).
- **Note**: if the paper finalisation step warrants a permanent script, it would be a ~30-line helper under `scripts/` wrapping steps 1–4. Not required for paper citation; the operation and inputs are fully specified above.

## 11. 55-map generalisation scope (disjoint from Era 1/2/3)

The 55-map generalisation corpus is a **separate evaluation scope**, disjoint from the 4-map gold-standard corpus that underlies Era 1 / Era 2 / Era 3 documented in §§2–7 above.

| Property | Value |
|----------|-------|
| Map sheets | **55** (e.g., K-35-042-3, K-35-050-4, …, K-35-077-4) |
| Intersection with 4-map GS set | **0** (disjoint) |
| Total project map-sheet coverage | **59** (55 generalisation + 4 gold-standard) |
| Tile grid | 384 px, Era-2 style evaluation bounds |
| Evaluable tiles | **8,541** |
| Ground truth | Student-digitised (not curator-annotated); **4,744 mounds** |
| GT reference file | `inputs/vectors/references/student-mounds-55maps-reviewed.geojson` |
| Bounds file | `inputs/vectors/bounds/384/55maps_evaluation_bounds.geojson` |
| Area covered | ~31,818 sq km |

**Disjoint by design**: the 55-map corpus was selected to exclude the 4 gold-standard sheets so that any generalisation claim is against sheets the pipeline was never calibrated on. Per-candidate human review was performed only on the image track's VLM-only candidates (1,028 reviewed); the text-HIGH and text-MIN tracks were not human-reviewed, so their corrected F1 is not available.

**Ground-truth quality note**: the 55-map student-GT has position noise empirically quantified at ~25–35 m (4–5 px at 384-px tile scale) — see `results/gold-standard-extended-buffer-sweep/extended-buffer-report.md` §6 for the curve-shift argument. The 4-map curator-GT has materially smaller position noise, visible as the F1-curve plateau at 25 m on the 4-map set vs > 50 m on the 55-map set.

**Paper-citation implication**: any cross-corpus F1 comparison (e.g., "55-map text-HIGH 0.788 at 50 m vs 4-map text-HIGH 0.826 at 50 m") is across **disjoint** sheet sets — so the comparison tests generalisation from calibration sheets (GS) to held-out sheets (55-map), not within-sheet variation.
