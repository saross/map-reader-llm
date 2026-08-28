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

## 8. Cost vocabulary

| Term | Meaning |
|---|---|
| list vs flex | Google list price vs the 50 % real-time flex/batch tier (all campaign spends are flex) |
| audited (basis) | Recomputed from meta token counts at the token-load-audit rates (cached input discounted) — the citable figure; the runner's live estimator over-records cached-heavy runs |
| full (cost) | proposer × N/K + verification of the ENTIRE vote ≥ 1 union (buys sweep/oracle/ladder analyses) |
| lean-deploy (cost) | proposer × N/K + verification of only the carried vote-shell — what deployment actually needs |
| $/mound | Run cost per true-positive detection at the operating point (the per-mound economics) |

## Changelog

### 2026-08-29 — Original publication

PI-commissioned canonical key (S143); consolidates the portfolio
card's § 3b terminology note, the basis vocabulary that grew across
the final-board work, and the column inventories of the standard
artefact formats. The uplift-supplement CSV builder is required to
validate against § 6–7.
