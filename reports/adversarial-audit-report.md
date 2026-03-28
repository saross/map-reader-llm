# Adversarial Results Audit Report

**Condition under audit:** `flash-high-text-16-of-30--flash-min-vf`
**Reported claim:** F1 > 0.9
**Actual point estimate:** F1 = 0.9044 at 30m spatial tolerance
**Bootstrap 95% CI:** [0.8779, 0.9277]
**Date:** 2026-03-27

---

## Phase 1 — Claims Inventory

### Layer 1: Ground Truth Integrity (5 claims)

1. Ground truth contains 569 annotations across 4 maps (136 + 217 + 196 + 20)
2. No duplicate annotations exist (no two points within 5m)
3. Annotation coordinates correctly align with tile pixel coordinates after tiling
4. Every ground truth point maps to exactly one tile at each tile size (384px, 512px)
5. The count of 569 is consistent across every report, script, and output file

### Layer 2: Tile Generation and Coverage (5 claims)

6. 384px and 512px tile sets cover the same geographic extent
7. 512px: stride=448, overlap=64; 384px: stride=336, overlap=48
8. No ground truth points fall in gaps between tiles
9. Calibration/training tiles are excluded from the production evaluation set
10. Tile counts: 512px = 360 (340 eval); 384px = 611 (487 eval)

### Layer 3: API Response Parsing (6 claims)

11. Raw API responses are archived with full metadata
12. The parser does not silently drop detections in ways that inflate F1
13. Verifier parse errors are handled conservatively (default to rejection)
14. The PV data flow is transparent with no hidden filtering
15. All 487 evaluation tiles have results across all 30 proposer runs
16. The consensus clustering algorithm correctly applies 16-of-30 threshold

### Layer 4: Spatial Matching (5 claims)

17. The Hungarian algorithm implementation is correct (one-to-one matching)
18. The pixel-to-metre conversion is correct (~5.01 m/pixel at 384px)
19. 30m tolerance = ~6 pixels at 384px; correctly computed in projected metres
20. The tolerance comparison is inclusive (<=)
21. The tolerance curve is monotonically non-decreasing

### Layer 5: Metric Calculation (5 claims)

22. F1 = 0.9044 is correctly computed from TP=383, FP=29, FN=52 (scoped GT=435)
23. Empty tiles (no GT, no detections) do not inflate F1
24. The 16-of-30 voting threshold is applied before spatial matching
25. Per-tile TP/FP/FN counts match manual spot-checks
26. Bootstrap CIs use tile-level resampling (1,000 iterations, seed=42)

### Layer 6: Configuration and Pipeline Integrity (5 claims)

27. The full parameter set is documented and traceable
28. No prompt files contain embedded images, base64 data, or ground truth coordinates
29. All proposer runs use the same model version (gemini-3-flash → gemini-3-flash-preview)
30. All output timestamps form a consistent sequential chain
31. Proposer and verifier configs differ only in the intended parameters

### Layer 7: Cross-Configuration Consistency (5 claims)

32. Performance increases monotonically: single-pass → consensus → PV
33. Text-only outperforms image, consistent across all pipeline stages
34. 384px outperforms 512px by 5–7 F1 points (significant, p ≤ 0.004)
35. The verifier improves both precision and recall over best consensus
36. No anomalous ordering among conditions

### Layer 8: Statistical Validity (5 claims)

37. The 30 consensus runs are truly independent API calls
38. Bootstrap CIs are correctly computed with tile-level resampling
39. Multiple comparison correction is applied via FDR at q = 0.05
40. The F1 > 0.9 result survives FDR correction
41. Paired permutation tests are correctly implemented

---

## Phase 2 — Verification

### Layer 1: Ground Truth Integrity

**Claims inventoried:** 5

| # | Claim | Evidence checked | Verdict | Impact on F1 |
|---|-------|-----------------|---------|--------------|
| 1 | 569 annotations across 4 maps | Counted features in each GeoJSON: 136+217+196+20=569. Aggregate `mounds-reference.geojson` also 569. Coordinate sets identical at 6 decimal places. | PASS | None |
| 2 | No duplicate annotations | All 569 points checked pairwise: zero pairs within 5m; zero within 20m | PASS | None |
| 3 | Coordinate alignment correct | 3 points from 3 maps traced through tiling transform via world files. All land on correct tiles at both 384px and 512px. | PASS | None |
| 4 | Every GT point maps to one tile | `scope_references_to_tiles()` uses `gpd.sjoin` with `predicate='intersects'`; `_assign_refs_to_primary_tiles()` assigns each reference to exactly one tile (nearest centroid). Zero points lost at boundaries. | PASS | None |
| 5 | Count of 569 consistent everywhere | Searched codebase: 569 in preregistration, methodology reports, methods outline, all threshold sweep JSONs. 435 correctly reported as scoped count for 384px. | PASS | None |

**Layer verdict:** PASS
**Reasoning:** Ground truth is clean, complete, and consistently referenced. No duplicates, no coordinate errors, no count discrepancies. The single nuance is that `ground_truth_mounds: 569` in result JSONs is the pre-scoped total, while the actual evaluation denominator is 435 (after scoping to the 487-tile evaluation bounds). This is a documentation nuance, not a computational error.

---

### Layer 2: Tile Generation and Coverage

**Claims inventoried:** 5

| # | Claim | Evidence checked | Verdict | Impact on F1 |
|---|-------|-----------------|---------|--------------|
| 6 | Same geographic extent | Both tile sizes source from the same 4 GeoTIFFs with `boundless=True`. Raw tiling covers identical area. BUT evaluation footprints differ: 384px evaluates 435 mounds across 487 tiles; 512px evaluates 539 mounds across 340 tiles. The 384px evaluation area is a strict subset. | CONCERN | Medium, direction unclear — different GT corpora complicates cross-tile-size comparison |
| 7 | Stride/overlap correct | 512px: stride=448, overlap=64 (from `config.py`). 384px: stride=336, overlap=48 (from tile coordinate analysis). Both verified from actual tile files. | PASS | None |
| 8 | No GT in gaps | Contiguous coverage within tiled area at both sizes. `scope_references_to_tiles()` correctly excludes points outside tile boundaries from denominator. | PASS | None |
| 9 | Calibration tiles excluded | 384px calibration manifest is empty (calibration was at 512px). 124 tiles excluded from 384px for geographic overlap with 512px calibration area. Zero overlap confirmed between excluded and evaluation sets. | PASS | None |
| 10 | Tile counts correct | 512px: 360 generated, 340 evaluated. 384px: 611 generated, 487 evaluated. All verified against directory listings and manifest files. | PASS | None |

**Layer verdict:** CONCERN
**Reasoning:** All tile generation and coverage mechanics are correct. The one concern is that the 384px evaluation (487 tiles, 435 mounds) and 512px evaluation (340 tiles, 539 mounds) cover different geographic regions and different ground truth corpora. The F1 for each tile size is internally valid, but direct F1 comparisons across tile sizes are on different subsets of mounds. This does not inflate F1 but could bias tile-size comparisons if detection difficulty varies spatially.

---

### Layer 3: API Response Parsing

**Claims inventoried:** 6

| # | Claim | Evidence checked | Verdict | Impact on F1 |
|---|-------|-----------------|---------|--------------|
| 11 | Responses archived | Each of 30 runs has `.meta.json` recording UUID, timestamps, git commit, model version, token counts. Verifier has `run.meta.json` with same fields. | PASS | None |
| 12 | Parser doesn't silently drop detections | JSON parse failures return `None` (tile failure, retried/excluded), not `[]` (empty). Malformed `box_2d` entries skipped with warning (direction: deflates F1). | PASS | None — bias is conservative |
| 13 | Verifier parse errors conservative | Parse errors get `mound_probability = 0.0` (`lib_verifier.py` lines 959–968). At threshold 0.2, this means rejection. Zero parse errors in actual data (729 candidates). | PASS | None |
| 14 | PV data flow transparent | Proposer → consensus clustering (20m, `cKDTree`) → candidate extraction (150×150 crops) → verifier (sees crop image + text labels only) → probability threshold. Verifier does NOT see coordinates, confidence, or vote count. | PASS | None |
| 15 | All tiles have results | 29/30 runs: 487/487 tiles. Run 27: 486/487 tiles (one tile short). Impact: one tile has max 29 votes instead of 30. Negligible effect on 16-of-30 threshold. | PASS | Negligible |
| 16 | Consensus threshold correct | `cluster_across_passes()` counts distinct contributing runs per cluster. `generate_consensus_gdf()` filters `vote_count >= threshold`. All 729 candidates in 16of30 manifest have vote_count ≥ 16. Verified as strict subset of 11,771 in 1of30. | PASS | None |

**Layer verdict:** PASS
**Reasoning:** The parsing pipeline is robust and conservatively biased. Parse failures result in tile exclusion or retry, not silent zero-detection counting. The verifier defaults to rejection on parse errors. The PV data flow is clean — the verifier operates independently with no access to proposer scores or coordinates.

---

### Layer 4: Spatial Matching (Hungarian Algorithm)

**Claims inventoried:** 5

| # | Claim | Evidence checked | Verdict | Impact on F1 |
|---|-------|-----------------|---------|--------------|
| 17 | Hungarian algorithm correct | `scipy.optimize.linear_sum_assignment` called on `(n_det, n_ref)` cost matrix with `inf_cost = max_distance * 1000` for beyond-tolerance pairs. Post-filter retains only pairs ≤ `max_distance`. One-to-one guaranteed by algorithm + filtering. | PASS | None |
| 18 | Pixel-to-metre conversion | All spatial operations in projected UTM metres (EPSG:32635). World file confirms pixel size = 5.01 m/pixel. Detections converted from normalised coordinates (0–1000) → pixel → UTM via rasterio affine transform. | PASS | None |
| 19 | 30m = ~6 pixels | 30m / 5.01 m/pixel = 5.99 pixels. 20m / 5.01 = 3.99 pixels. Both physically reasonable (mound symbols span 10–20 pixels). | PASS | None |
| 20 | Inclusive boundary | Both cost matrix construction (line 203) and post-filter (line 213) use `<=`. Consistent. | PASS | None |
| 21 | Tolerance curve monotonic | `buffer_sensitivity.json`: F1 = 0.890 (20m), 0.904 (30m), 0.904 (40m), 0.904 (50m). Monotonically non-decreasing. Plateau at 30m means zero additional matches between 30–50m. | PASS | None |

**Layer verdict:** PASS
**Reasoning:** The spatial matching implementation is textbook correct. One-to-one assignment via Hungarian algorithm with proper post-filtering. All operations in projected metres. The tolerance curve's plateau at 30m confirms that the 30m buffer captures all viable matches without artificial inflation.

---

### Layer 5: Metric Calculation

**Claims inventoried:** 5

| # | Claim | Evidence checked | Verdict | Impact on F1 |
|---|-------|-----------------|---------|--------------|
| 22 | F1 arithmetic correct | TP=383, FP=29, FN=52. P=383/412=0.9296, R=383/435=0.8805. F1=2×0.9296×0.8805/(0.9296+0.8805)=0.9044. TP+FN=435 matches scoped GT. TP+FP=412 matches `n_accepted`. | PASS | None |
| 23 | Empty tiles don't inflate F1 | `calculate_f1_internal` calls `continue` when both `det_scope` and `ref_scope` are empty. F1 returns 0.0 when P+R=0, not 1.0. 279 of 487 tiles are true empties contributing (0,0,0). Micro-averaging immune to empty-tile padding. | PASS | None |
| 24 | Voting threshold before matching | Sequence verified: 30 runs → consensus clustering → 1-of-30 union (11,771) → candidate extraction → verifier → 16-of-30 filter (729) → probability threshold (412) → Hungarian matching. Threshold applied at steps 6–7, matching at step 8. | PASS | None |
| 25 | Spot-check matches | 3 tiles checked. Matched pairs at 2.0–15.9m (well within 30m). Unmatched GT at 85–737m (genuine misses). No suspicious near-boundary matches. | PASS | None |
| 26 | Bootstrap CI sound | Tile-level resampling (`rng.choice(tiles, n_tiles, replace=True)`). 1,000 iterations, seed=42. Percentile method (2.5th/97.5th). Pre-computed per-tile TP/FP/FN (errata E26 fix prevents deduplication bias). CI width 0.050 plausible for 487 tiles. | PASS | None |

**Layer verdict:** PASS
**Reasoning:** The metric calculation is verified end-to-end. F1 arithmetic checks out from raw counts. Empty tiles are handled correctly. The voting threshold is applied before spatial matching. Spot-checks confirm genuine matches at short distances. Bootstrap CIs use methodologically sound tile-level resampling.

---

### Layer 6: Configuration and Pipeline Integrity

**Claims inventoried:** 5

| # | Claim | Evidence checked | Verdict | Impact on F1 |
|---|-------|-----------------|---------|--------------|
| 27 | Full parameters documented | Proposer: gemini-3-flash, HIGH thinking, T=0.7, text-only (`detect_brief-text.json`), 384px, N=30, 17 text-only examples. Verifier: gemini-3-flash, MINIMAL thinking, T=0.0 (`verify_adversarial-text.json`), 6 text labels, no examples. PV threshold: 0.2. Consensus: 16-of-30. Buffer: 30m. All confirmed in meta.json files. | PASS | None |
| 28 | No GT in prompts | `detect_brief-text.md`: clean detection instructions. `verify_adversarial.md`: clean adversarial instructions. Both config JSONs: no base64, no coordinate data, no GT file paths. Regex search for `base64`, `data:image`, coordinate patterns: zero matches. | PASS | None |
| 29 | Model version consistent | Runs 1, 15, 30 all report `gemini-3-flash` (resolving to `gemini-3-flash-preview`). Verifier also `gemini-3-flash-preview`. Resolution via `lib_batch_api.py` lines 1944–1958. | PASS | None |
| 30 | Timestamps consistent | Proposer: 24 Mar 2026 03:47–19:20 UTC (30 batch runs). Verifier: 25 Mar 18:20 UTC. Derived 16of30: 25 Mar 21:37. Evaluation: 26 Mar 12:49 UTC. Sequential, no gaps or reversals. | PASS | None |
| 31 | Only intended params differ | Proposer vs verifier: system instruction (detect vs adversarial), temperature (0.7 vs 0.0), thinking (HIGH vs MINIMAL). All intentional. Model, max_output_tokens, text-only mode: same. | PASS | None |

**Layer verdict:** PASS
**Reasoning:** Every parameter is traceable from study YAML through meta.json to API response metadata. No prompt contamination. Consistent model versions. Timestamps form a clean sequential chain. The proposer–verifier configuration differences are exactly and only the intended ones.

---

### Layer 7: Cross-Configuration Consistency

**Claims inventoried:** 5

| # | Claim | Evidence checked | Verdict | Impact on F1 |
|---|-------|-----------------|---------|--------------|
| 32 | Monotonic pipeline progression | Single-pass best: F1=0.563. Consensus best: F1=0.826. PV best: F1=0.904. Each stage adds ~0.13–0.26 over the previous. | PASS | None |
| 33 | Text > image consistent | Consensus: text F1=0.826 vs image F1=0.821 (small gap). PV: text F1=0.904 vs image F1=0.851 (larger gap). Pairwise permutation test: diff=0.110, CI [0.073, 0.148], p=0.001. Gap widens through pipeline. | PASS | None |
| 34 | 384px > 512px significant | Three pairwise comparisons: loose consensus +0.070 (p=0.004), goldilocks +0.061 (p=0.002), best-vs-best +0.063 (p=0.002). 384px wins all three. | PASS | None |
| 35 | Verifier improves over consensus | Same proposer lineage: Flash-high-text consensus F1=0.826 → PV F1=0.904 (+0.078). Verifier improves precision (+0.084) and recall (+0.074). The precision gain is slightly larger, consistent with adversarial verification design. | PASS | None |
| 36 | No anomalous ordering | Single-pass < consensus < PV. MINIMAL < HIGH thinking. Larger pools ≥ smaller pools. T=0.7 > T=1.0. No condition performs worse than a strictly inferior configuration. | PASS | None |

**Layer verdict:** PASS
**Reasoning:** All cross-configuration comparisons are directionally consistent with expectations. The pipeline progression is monotonic. Text outperforms image (confirmed statistically). 384px outperforms 512px (confirmed statistically). No anomalous patterns detected.

---

### Layer 8: Statistical Validity

**Claims inventoried:** 5

| # | Claim | Evidence checked | Verdict | Impact on F1 |
|---|-------|-----------------|---------|--------------|
| 37 | 30 runs are independent | Each run has unique UUID, distinct timestamps spanning ~16 hours (batch API). Log confirms "Runs per condition: 30", execution mode: "BATCH". T=0.7 provides stochastic variation. | PASS | None |
| 38 | Bootstrap CI correct | Tile-level resampling, 1,000 iterations, seed=42, percentile method. Pre-computed per-tile counts (E26 fix). CI = [0.878, 0.928]. **Lower bound does not exceed 0.9.** | CONCERN | The claim "F1 > 0.9" is a point estimate, not a statistical guarantee |
| 39 | FDR correction applied | `analyse_phase2_results.py` (lines 199–210) uses pseudo-p-values derived from CI bounds via ad hoc formula: `pseudo_p = max(0.001, 0.05 - ci_lower)`. This is **not a valid statistical procedure** — it does not preserve the properties required by Benjamini-Hochberg. The separate `pairwise_permutation_test.py` computes real p-values correctly but was not applied to the paper-eval conditions. | CONCERN | Pseudo-p-value FDR is methodologically flawed; real permutation tests not applied at paper-eval level |
| 40 | F1 > 0.9 survives FDR | No pairwise test exists between the target (F1=0.904) and runner-up (F1=0.891). Gap is 0.014. CIs overlap: target [0.878, 0.928] vs runner-up [0.863, 0.916]. Analogous gaps in 512px data (~0.009–0.012) were non-significant. | CONCERN | No formal significance test between top-2 conditions; claim that this specific condition is best is not established |
| 41 | Permutation tests correct | `pairwise_permutation_test.py`: paired, two-sided, 10,000 permutations, micro-average F1, seed=42. Implementation is sound. | PASS | None |

**Layer verdict:** CONCERN
**Reasoning:** The bootstrap and permutation test implementations are methodologically sound. The concerns are about the claims derived from them: (1) the 95% CI lower bound is 0.878, not 0.9 — the "F1 > 0.9" claim is a point estimate, not a statistical guarantee; (2) the pseudo-p-value FDR in one analysis script is flawed; (3) no pairwise significance test exists between the top-2 PV conditions at paper-eval level. None of these inflate F1, but they affect how the result should be reported.

---

## Specific Failure Hypotheses

| # | Hypothesis | Evidence FOR inflation | Evidence AGAINST inflation | Verdict |
|---|-----------|----------------------|--------------------------|---------|
| 1 | Ground truth leakage | None found | API requests contain only tile image + text instructions. No GT data in prompts, configs, filenames, or metadata. Verifier sees only crop image + text labels. | REJECTED |
| 2 | Tolerance inflation | F1 > 0.9 holds at 30m but not at preregistered 20m (F1=0.890) | 30m = ~6 pixels (~1 symbol width), physically reasonable. Plateau at 30m (no further gain at 40–50m). 20m→30m gain is only +0.014. | REJECTED |
| 3 | Double-counting TPs | None found | `linear_sum_assignment` guarantees one-to-one. Post-filter removes beyond-tolerance pairs. Per-tile distribution assigns each reference to exactly one primary tile. | REJECTED |
| 4 | Selective tile exclusion | None found | 487/487 tiles processed with 0 failures across all 30 runs (29/30 runs; 1 run has 486). No correlation between difficulty and exclusion. | REJECTED |
| 5 | PV contamination | Verifier knows it is evaluating a "candidate" (framing, not leakage) | Verifier receives only crop image + 6 text labels. No coordinates, confidence, or vote count. Adversarial framing: "find reasons it is NOT a burial mound." 44% rejection rate. | REJECTED |
| 6 | Empty tile inflation | None found | Micro-averaged F1: empty tiles contribute (0,0,0). F1 returns 0.0 when P+R=0, not 1.0. 279 empty tiles have zero effect on numerator or denominator. | REJECTED |
| 7 | Training tile inclusion | None found | 384px calibration manifest is empty. Calibration was on 512px tiles. 124 tiles excluded from 384px for geographic overlap with 512px calibration area. Zero overlap between excluded and evaluation sets. | REJECTED |
| 8 | Stale results | None found | Sequential timestamps: proposer (24 Mar) → verifier (25 Mar) → evaluation (26 Mar). 16of30 is verified subset of 1of30 (729/11,771 with identical probability values). | REJECTED |
| 9 | Configuration mismatch | None found | All meta.json files match study YAML overrides. Proposer: Flash HIGH T=0.7 text-only. Verifier: Flash MINIMAL T=0.0 adversarial-text. Labels accurate. | REJECTED |

---

## Completeness Check

1. **Every layer received a verdict:**
   - Layer 1: PASS | Layer 2: CONCERN | Layer 3: PASS | Layer 4: PASS
   - Layer 5: PASS | Layer 6: PASS | Layer 7: PASS | Layer 8: CONCERN

2. **Every failure hypothesis received a verdict:** All 9 REJECTED.

3. **BLOCKED checks:** None. All checks were performable from the codebase and archived outputs.

4. **Layer with least time spent:** Layer 6 (Configuration/Pipeline Integrity) received thorough attention — all 5 checks verified with multiple meta.json files and config diffs. No layer was rushed.

5. **"If the error is in the one place I didn't look carefully, where would that be?"**
   The consensus clustering algorithm in `lib_consensus.py` uses a greedy single-linkage approach where iteration order affects cluster membership. While the algorithm is consistently applied, the 20m clustering threshold is the same as the evaluation distance in some analyses, which means the clustering and evaluation share a parameter. This is not an error but could introduce a subtle coupling. Checked: the paper-eval condition uses a 30m evaluation buffer (larger than the 20m clustering radius), so clustering does not constrain the evaluation distance.

---

## Overall Assessment

### Confidence level: 85% that F1 > 0.9 is genuine at 30m tolerance

The pipeline is well-engineered and correctly implemented across all 8 layers. All 9 inflation hypotheses are rejected. The F1 = 0.9044 at 30m buffer is arithmetically correct, computed from verified TP=383, FP=29, FN=52 against a properly scoped ground truth of 435 mounds.

The 15% residual uncertainty comes from:

- **Tolerance dependency (primary):** F1 > 0.9 holds at 30m but not at the preregistered 20m tolerance, where F1 = 0.890 [0.863, 0.915]. The choice of 30m over 20m adds 8 additional TPs. While 30m is a physically defensible tolerance (~6 pixels, ~1 symbol diameter), the result is tolerance-dependent and this must be transparently reported.

- **Statistical uncertainty:** The 95% CI lower bound at 30m is 0.878, which does not exclude values below 0.9. The point estimate exceeds 0.9 but this is not statistically guaranteed.

- **Unverified claims at layer boundaries:** The greedy consensus clustering and the choice of 16-of-30 as the optimal threshold were selected from a sweep — the multiple comparisons implicit in this selection are not formally corrected.

### Most likely source of F1 inflation: None confirmed

No computational error, data leakage, or methodological flaw was found. The F1 = 0.9044 appears to be a legitimate measurement.

### Weakest link: Layer 8 (Statistical Validity)

The statistical reporting infrastructure has two weaknesses:

1. **The pseudo-p-value FDR** in `analyse_phase2_results.py` (lines 199–210) converts bootstrap CI bounds to p-values via an ad hoc formula that is not a valid statistical procedure. This script should use the real permutation test p-values from `pairwise_permutation_test.py` instead.

2. **No head-to-head significance test** exists between the best condition (F1=0.904) and the runner-up (F1=0.891) at 384px paper-eval level. Their CIs overlap, and analogous 512px comparisons at similar gap sizes were non-significant.

### Recommendations

1. **Report the result precisely:** "F1 = 0.90 [0.88, 0.93] at 30m spatial tolerance" rather than "F1 > 0.9." Note that at the preregistered 20m tolerance, F1 = 0.89 [0.86, 0.92].

2. **Run a paired permutation test** between the top-2 PV conditions (`flash-high-text-16-of-30--flash-min-vf` vs `flash-high-text-4-of-5--flash-min-vf`) at the 384px paper-eval level to establish whether the difference is statistically significant.

3. **Replace the pseudo-p-value FDR** in `analyse_phase2_results.py` with real p-values from the permutation test infrastructure. The current implementation is not defensible in a methods section.

4. **Document the 384px vs 512px evaluation footprint asymmetry.** The two tile sizes evaluate different subsets of ground truth (435 vs 539 mounds). This does not inflate F1 but limits the interpretability of cross-tile-size comparisons.

5. **Report the `ground_truth_mounds` metadata correctly.** The JSON files report 569 (total) but the scoped evaluation count is 435. Either fix the metadata or add a `ground_truth_mounds_scoped` field to prevent misinterpretation.
