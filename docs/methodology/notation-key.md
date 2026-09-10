# Notation and abbreviation key (canonical)

> **Last revised**: 2026-08-29 (original publication; PI-commissioned
> — "codify it a little more strongly than a terminology note").
> This is the SINGLE canonical key for symbols, abbreviations, labels,
> and dataset column names across the paper, supplements, findings
> documents, and published CSVs/datasets. New tables and dataset
> builders must conform to it or extend it here first (the uplift
> supplement's CSV builder validates its columns against this file).
> See [§ Changelog](#changelog).

## 1. Core experiment symbols

| Symbol | Meaning | Notes |
|---|---|---|
| **K** (capital) | Total passes RUN in a campaign (a property of the spend) | K = 5 incumbents; K = 10 portfolio |
| **N** | Passes USED in a derived set, by the preregistered first-N rule; N ≤ K | ladder rungs N ∈ {1, 3, 5, 10}; when N = K they coincide |
| **k** (lower case) | Consensus VOTE THRESHOLD: a detection must appear in ≥ k of the N passes | one of the two operating-point dials |
| **x-of-N** | Prose form of the vote threshold ("4-of-5", "5-of-10") — x IS k | prefer this phrasing in running text; symbols in tables |
| **prob_t** | Verifier probability threshold: keep candidates with `mound_probability` ≥ prob_t | the other operating-point dial |
| **(prob_t, k)** | An OPERATING POINT — both dials, everything else pinned by protocol | e.g. (0.15, k8) |
| **T** | Sampling temperature | T = 0.7 the carried default; H7 swept 0.0–2.0 |
| **R** / R_m | Evaluation buffer radius in metres (spatial match tolerance) | GS-primary 20 m; 55-map operational 50 m |
| **c** | Cluster corroboration parameter in union building | c = 1 throughout the modern campaigns |

Case matters: "k = 10 of N = 10 of K = 10" is a coherent (and real)
cell. Historical cell labels use lower-case k for the THRESHOLD:
TH7-k3 is the 3-of-5 cell of a K = 5 run, not a 3-pass run.

## 2. Config and run abbreviations

| Abbrev. | Meaning |
|---|---|
| TH7 | text HIGH-thinking T = 0.7 (K = 5 incumbent) |
| T03 | text HIGH-thinking T = 0.3 (K = 5 incumbent) |
| TM | text MINIMAL-thinking T = 0.7 (K = 5 incumbent) |
| IM | image (17-example library), HIGH thinking (K = 5 incumbent) |
| UPL / min-uplift | text MINIMAL 10-pass standard-grid run (5 original + 5 uplift passes) |
| A | 384 px / 33.3 % overlap (stride 256) deployment run, K = 10 |
| B | 384 px / 50 % overlap (stride 192) deployment run, K = 10 — the leading geometry |
| g\<px\>_ov\<o\> | Geometry cell: tile size px, overlap o px (stride = px − o); e.g. g384_ov192 = 384 px tiles, 192 px overlap, stride 192 |
| MIN / MINIMAL, HIGH, low | Thinking levels (Gemini 3 family: minimal/high; Gemini 3.7: low/medium/high) |
| PV | proposer–verifier (two-stage architecture) |

## 3. Basis vocabulary (how a number was chosen)

| Term | Meaning |
|---|---|
| **carried** | Operating point committed BEFORE evaluation on the target data (calibrated elsewhere, e.g. on the GS) — the honest deployment claim |
| **oracle** | Post-hoc argmax of a sweep on the target data — the theoretical maximum, never a deployment claim |
| **carried (post-hoc)** | A pre-existing committed selection whose EVALUATION was post-hoc nominated (the emergent N = 3 cells) |
| **as-shipped** | The cell a run originally materialised (image's k3) |
| **comparability** | A cell derived later purely for like-for-like comparison (IM-k4, E82) |
| **registered-exploratory** | Predictions committed by git commit before launch (the P/IP/HP/G slates) |
| **transfer tax** | Oracle minus carried on the same run — what freezing the calibration cost |

## 4. Ground truth and reference vocabulary

| Term | Meaning |
|---|---|
| curator GT | The GS 4-map curated reference (`mounds-reference.geojson`) |
| student GT | The 55-map reviewed student digitisation (4,746 points) |
| canonical (extended) GT | student + adjudicated reviewer-promoted phantoms, per-buffer gated (the deployment-era reference) — schema class "combined" |
| standardised reference | Ruling 21: student 4,731 + extension 279 at marked centres, no ring gate — the paper reference for 55-map cells |
| phantom | A reviewer-confirmed mound absent from the student layer |
| extension mounds | Model-found, human-confirmed additions in the standardised reference |

## 5. Metrics and statistics

| Term / column | Meaning |
|---|---|
| F1, P (precision), R (recall) | Symbol-level detection metrics at buffer R_m |
| corrected-F1 | F1 against an extended GT whose phantom additions are per-buffer gated (55-map two-reference protocol) |
| micro-F1 | F1 from summed per-tile TP/FP/FN (the board/tiering mechanism; within 0.003 of the evaluation F1 — the "mechanism bound") |
| MCC / tile-MCC | Matthews Correlation Coefficient on per-tile presence/absence (buffer-invariant on the standardised reference) |
| sensitivity / specificity | Tile-level companion rates to MCC |
| CI, BCa, percentile | 95 % bootstrap confidence intervals; BCa for evaluate_detections outputs, percentile for corrected-F1 outputs (each eval records its method) |
| tile-swap permutation | Paired round-robin per-tile permutation test (10,000, seed 42) — the board instrument since the GS |
| per-sheet sign-swap | Paired permutation over the 55 map sheets — the deployment pairwise instrument |
| BH-FDR q | Benjamini–Hochberg false-discovery correction across a declared family (q = 0.05) |
| tier | Greedy-clique tier from BH-adjusted pairwise tests (disjoint bands) |
| group (CLD) | Compact letter display: cells sharing ANY letter are statistically indistinguishable (overlapping cliques) |
| MDE (50 %/80 %) | Minimum detectable effect of an instrument at that power (z × permutation null SD) |
| TOST / equivalence margin Δ | Two one-sided tests: "effects, if any, are smaller than Δ" |
| null SD (null_std) | Permutation null standard deviation — the instrument's noise floor |

## 6. Corpora and evaluation frames

| Frame id | Tiles | Corpus | Typical buffer |
|---|---:|---|---|
| era-1-340 | 340 | GS 4 maps, 512 px frame | 20 m |
| grid-common-487 | 487 | GS 4 maps, common footprint of the grid/stride campaigns | 20 m |
| 55maps-8541 | 8,541 | 55-sheet deployment corpus, standard 384 grid | 50 m |
| era-2-487 | 487 | GS 4 maps, 384 px Era-2 frame (`inputs/vectors/bounds/384/full_evaluation_bounds.geojson`) | 20 m |
| era-3-327 | 327 | GS 4 maps, 384 px Era-3 frame (`inputs/vectors/bounds/384/h10_test_bounds.geojson`; the pool_160 exclusion) | 20 m |
| px256-1032 | 1,032 | GS 4 maps, 256 px diagnostic frame (`inputs/vectors/bounds/256/full_evaluation_bounds.geojson`) | 20 m |
| h13-common-338 | 338 (id) / 340 (recorded) | GS 4 maps, 512 px H13 overlap/stride common frame (`outputs/h13/scoring/bounds/h13_common_bounds.geojson`); the id and the recorded count disagree — open | 20 m |
| era2-b-487 | 487 | GS 4 maps, Era-2 carrier tiles clipped to the B tiling's union (`inputs/vectors/bounds/384/era2_b_intersection_bounds.geojson`) — a **leaderboard scoring frame** (the GS Era-2 verified board), not a stratum frame: rows scored on it are board artefacts and are excluded from the uplift supplement (rule 2026-09-10) | 20 m |
| stratum_id | — | Composite key corpus × reference × buffer × frame (the uplift dataset's mandatory grouping key; cross-stratum aggregation only as explicit transfer pairs) | — |

## 7. Standard dataset column names

Sweep/ladder CSVs (`sweep_*.csv`, `ladder_sweep_50m.csv`): `cell`,
`N`, `prob_t`, `min_votes` (= k), `n_detections`, `tp`, `fp`, `fn`,
`precision`, `recall`, `corrected_f1` (or `micro_f1_50` where the
board scorer produced it).

Corrected-F1 evaluations (`corrected-f1.csv`): `R_m`, `TP`, `FP`,
`FN`, `n_ref_student_only`, `n_reviewer_promoted_at_R`,
`n_phantom_duplicates_dropped`, `n_ref_extended`, `precision`/`recall`
/`F1` with `_CI_lo`/`_CI_hi`, `MCC` + CI, `tile_TP`/`tile_TN`/
`tile_FP`/`tile_FN`, `sensitivity`, `specificity`.

Board JSONs (`final_board_50m.json` and kin): `label`, `basis`,
`point`, `f1_50`, `ci`, `precision_50`, `recall_50`, `mcc`,
`n_detections`, `tier` (via `tiers`), `group` (CLD letters),
`cost_usd`; `pairwise[]` rows carry `observed_diff`, `p_value`,
`n_permutations`, `n_tiles`, `null_mean`, `null_std`,
`bh_adjusted_p`, `significant`.

Registry ids: conditions are `run_id::label` (kebab-case); passes are
`run_id::pool::runN`.

### 7.1 Uplift-supplement dataset columns

Sanctioned 2026-09-10 (PI ruling 2(i) of the supplement's registration walk-through) from the builder's declared extensions (`results/uplift-supplement/notation-extension-proposal.md`, 2026-08-29 → 2026-09-10). Each column names the key section it extends; "anti-confabulation" marks an operational provenance column with no symbol behind it.

| Column | Extends | Rationale |
|---|---|---|
| `K` | § 1 (K) | Passes RUN in the pool. The key defines the symbol; this is the column. |
| `aggregation` | conditions-manifest schema | none / greedy / wbf / consensus / verified. |
| `architecture` | conditions-manifest schema | single-pass / consensus / proposer-verifier — the evaluable architecture. |
| `blocked_reason` | anti-confabulation | Why a blocked job cannot run; never a placeholder, always a measured fact. |
| `bounds_path` | § 6 | The evaluation bounds defining the frame. |
| `buffer_m` | § 1 (R / R_m) | Third component, as an integer column; `R_m` is the corrected-F1 CSV's name. |
| `ci_method` | § 5 (CI, BCa, percentile) | The CI method the source evaluation recorded; omitted where it recorded none. |
| `ci_unreliable` | conditions-manifest schema | The measured D28/E72 reliability verdict carried through from the source. |
| `command` | anti-confabulation | The exact invocation the operator runs on sapphire. |
| `condition_id` | § 7 (registry ids) | The `run_id::label` composite spelled as a column name. |
| `corpus` | § 6 | First component of stratum_id: 4-map-gs or 55-map, from run-facts.json. |
| `cost_basis` | § 8 (audited / list / flex) | Which cost basis `cost_usd` carries; NOT the audited basis (see build report). |
| `delta` | § 3 (transfer tax) | target_value - source_value; a transfer tax when the sign is negative. |
| `detections_path` | anti-confabulation | The detection set scored. |
| `engine` | anti-confabulation | Which scorer the job needs: evaluate_detections or corrected_f1_multi_buffer. |
| `eval_path` | anti-confabulation | The evaluation artefact the metrics came from. |
| `frame_id` | § 6 | Fourth component: the evaluation frame id (era-1-340, era-2-487, ...). |
| `geometry` | § 2 (geometry cell) | The geometry cell label the key defines, as a column. |
| `geometry_basis` | § 2 | Which rule resolved the geometry: pool-name, label, or run-facts-tile-size. |
| `is_primary_buffer` | § 1 (R) | True where buffer_m is the corpus headline buffer (20 m GS / 50 m 55-map). |
| `job_id` | anti-confabulation | Primary key of a scoring job in a worklist. |
| `k1_with_verifier` | § 2 (PV) | derivable / blocked / not-applicable — the card's disclosed K = 1 PV anchor. |
| `k1_with_verifier_reason` | anti-confabulation | The measured ground for that verdict; never an approximation. |
| `materialise_command` | anti-confabulation | Prelude that builds the twin with the source_tile the engine scopes by. |
| `materialise_filter` | § 1 (k) | The vote_count predicate that turns the union into the paired shell. |
| `mde_50` | § 5 (MDE 50 %/80 %) | Minimum detectable effect at 50 % power, joined from sensitivity.json. |
| `mde_80` | § 5 (MDE 50 %/80 %) | Minimum detectable effect at 80 % power, joined from sensitivity.json. |
| `mde_instrument` | § 5 | The named permutation instrument the MDE and null SD describe. |
| `mde_join_basis` | § 5 | The join key used (n_tiles + buffer_m) and any ambiguity it carries. |
| `mde_source` | § 5 | The artefact the instrument's null SD was measured from. |
| `metric` | § 5 | Which metric the delta is on (F1, MCC, precision, recall). |
| `metrics_source` | anti-confabulation | conditions-manifest or evaluation-json — where this row's metrics were read. |
| `modality` | § 2 (image / text) | Proposer input modality; the key names the values, not a column. |
| `model_used` | passes-manifest schema | Authoritative model identity, read from per-item metadata, never a name. |
| `n_comparisons` | § 5 | Pairwise comparisons the instrument's null SD was measured over. |
| `n_conditions` | § 6 | How many registered conditions resolve into the stratum. |
| `n_refs` | § 4 | Reference mounds in the stratum's reference file; the key gives no column name. |
| `notes` | anti-confabulation | Free text recording any gap or caveat attached to this row. |
| `null_sd_hi` | § 5 (null SD) | High end of the instrument's observed null-SD range. |
| `null_sd_lo` | § 5 (null SD) | Low end of the instrument's observed null-SD range. |
| `output_dir` | anti-confabulation | Where the job writes its evaluation. |
| `overlap_px` | § 2 (geometry cell) | Overlap in pixels, the second half of the geometry cell. |
| `pair_id` | § 6 (stratum_id) | Primary key of a transfer pair; the key defines the object, not the column. |
| `pairing_basis` | anti-confabulation | Which rule located the pre-verifier twin: registered, consensus-file, union. |
| `proposer_pool` | § 7 (registry ids: run_id::pool::runN) | The pool component of the pass id, as a column. |
| `rationale` | anti-confabulation | Why this pair is a meaningful comparison despite spanning strata. |
| `reference` | § 4 | Second component: curator / student / canonical / standardised. |
| `reference_basis` | § 4 | Which rule resolved `reference`: eval-ground-truth, label-suffix, or run-facts. |
| `reference_consumed_path` | anti-confabulation | The path the evaluation literally recorded, where it differs from the anchor. |
| `reference_path` | § 4 | The ground-truth GeoJSON the evaluation consumed (the re-verify anchor). |
| `registered_analysis_id` | analyses-manifest schema | The registered analysis this pair belongs to, where one exists. |
| `run_id` | § 7 (registry ids) | Foreign key to the run registry; the key names the composite, not the part. |
| `rung` | § 1 (N) | Which ladder rung the job scores (N = 1 for the K = 1 gap-fill). |
| `source_condition` | § 7 (registry ids) | The K >= 3 consensus cell whose K = 1 rung this job supplies. |
| `source_condition_id` | § 7 (registry ids) | The cell a calibration or claim came FROM. |
| `source_stratum_id` | § 6 | Its stratum — necessarily different from the target's. |
| `source_value` | § 5 | The metric's value in the source cell. |
| `status` | anti-confabulation | ready / blocked / already-registered — whether the job can run at all. |
| `stride_px` | § 2 (geometry cell) | tile_px - overlap_px, which the key defines as the stride. |
| `target_condition_id` | § 7 (registry ids) | The cell the claim was carried TO. |
| `target_stratum_id` | § 6 | The target cell's stratum; the delta is a transfer across the two. |
| `target_value` | § 5 | The metric's value in the target cell. |
| `tax_kind` | § 3 (transfer tax) | Which tax the pair isolates: geometry, reference, corpus, buffer, or frame. |
| `temperature` | § 1 (T) | Sampling temperature. `T` alone is too short to be a safe CSV header. |
| `thinking` | § 2 (MIN / HIGH / low) | Thinking level; the key names the levels, not a column. |
| `tile_px` | § 2 (geometry cell) | Tile size in pixels, the first half of the geometry cell. |
| `transfer` | heterogeneity design § 3 | Always TRUE here: the flag that licenses a cross-stratum number. |
| `union_path` | anti-confabulation | The committed vote >= 1 union the vote shell must be filtered out of. |
| `unverified_condition_id` | § 7 (registry ids) | The registered pre-verifier cell, where one already exists. |
| `unverified_detections_path` | anti-confabulation | The pre-verifier consensus set at the same vote threshold. |
| `unverified_eval_path` | anti-confabulation | That cell's committed evaluation, where one already exists. |
| `unverified_stratum_basis` | anti-confabulation | Whether the twin's stratum was derived from its own cell or from the recipe. |
| `unverified_stratum_id` | § 6 | The twin's stratum, keyed independently; a tripwire, not a lineage check. |
| `unverified_value` | § 5 | The paired unverified cell's metric value. |
| `uplift` | § 3 | verified minus unverified on the same metric, same stratum. |
| `uplift_metric` | § 5 | Which metric the uplift column is computed on. |
| `verified` | § 2 (PV) | Boolean: a verifier stage ran. The key names the architecture, not a flag. |
| `verified_condition_id` | § 7 (registry ids) | The verified cell of a with/without-verifier pair. |
| `verified_stratum_id` | § 6 | The verified cell's own stratum, keyed from its own evidence. |
| `verified_value` | § 5 | The verified cell's metric value. |
| `verifier_crop_manifest` | anti-confabulation | The candidate manifest that measurement came from. |
| `verifier_floor_basis` | anti-confabulation | How the cell's verifier stage was matched: lineage, shell, sole, or ambiguous. |
| `verifier_min_vote_seen` | § 1 (k) | Lowest vote_count the verifier actually saw, measured from the crop manifest. |
| `verifier_variant` | § 2 (PV) | Verifier variant id from the condition's verifier_config. |

## 8. Cost vocabulary

| Term | Meaning |
|---|---|
| list vs flex | Google list price vs the 50 % real-time flex/batch tier (all campaign spends are flex) |
| audited (basis) | Recomputed from meta token counts at the token-load-audit rates (cached input discounted) — the citable figure; the runner's live estimator over-records cached-heavy runs |
| full (cost) | proposer × N/K + verification of the ENTIRE vote ≥ 1 union (buys sweep/oracle/ladder analyses) |
| lean-deploy (cost) | proposer × N/K + verification of only the carried vote-shell — what deployment actually needs |
| $/mound | Run cost per true-positive detection at the operating point (the per-mound economics) |

## Changelog

### 2026-09-10 — § 6 frames completed; § 7.1 uplift-supplement columns sanctioned

PI ruling 2(i), S152. § 6 gains the five frames the registered runs use beyond the original three (era-2-487, era-3-327, px256-1032, h13-common-338 with its id/count discrepancy left open, and the board frame era2-b-487 marked as a leaderboard scoring frame). § 7.1 sanctions the uplift-supplement builder's declared column extensions as proposed. Nothing else changed.

### 2026-08-29 — Original publication

PI-commissioned canonical key (S143); consolidates the portfolio
card's § 3b terminology note, the basis vocabulary that grew across
the final-board work, and the column inventories of the standard
artefact formats. The uplift-supplement CSV builder is required to
validate against § 6–7.
