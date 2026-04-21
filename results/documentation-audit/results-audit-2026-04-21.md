# Results Documentation Audit — Full Run-by-Run Table (2026-04-22)

**Audit period**: repository state through commit `2165013c`
(`docs(doc-audit-plan): 2026-04-21 supplement`).
**Anti-hallucination commitment**: every numeric claim below cites a
source file and JSON key path (or Markdown line number). If a value
appears without a citation, it is a structural statement (e.g., "no
comparator condition in the run design") not a measurement.

---

## Scope exclusions

The following are NOT audited as active runs:

- Anything under `archive/` (categorical archive directory at repo
  root).
- `archive/v2-verifier-contamination/` — 100 files moved on 2026-04-21
  because the v2 verifier prompt was derived by analysing FPs on the
  4-map gold-standard set. Affected paths include
  `results/leaderboard/cells/gold-standard-v2-greedy-v2-327tile.json`,
  the entire `results/e47-v1-vs-v2/` tree, and seven raw-output
  subdirectories under `outputs/h11/`. Policy:
  `docs/methodology/v2-verifier-contamination-policy.md`.
- `outputs/results/` is an empty directory that exists in the tree;
  not audited.

---

## A. The four 55-map generalisation runs (Era 2)

### A1. `55maps-image-generalisation` (2026-04-18)

**Scope**: 55-map image-modality generalisation; gemini-3-flash at
HIGH thinking with context caching; 5-pass proposer + verifier v1.

**Cost manifest**: `outputs/55maps-image-generalisation/cost_manifest.json`

| Claim | Key path | Value |
|---|---|---|
| Total cost (USD) | `totals.cost_usd` | 364.6971 → 364.70 |
| Input tokens | `totals.input_tokens` | 682,800,923 |
| Cached tokens | `totals.cached_tokens` | 621,315,045 |
| Cache-hit rate | `totals.cache_hit_rate` | 0.91 |
| Wall-clock (s) | `totals.wall_clock_seconds` | 14,947.18 |
| Proposer cost (USD) | `by_stage.proposer.cost_usd` | 353.6201 |
| Tiles processed | `by_stage.proposer.tiles_processed` | 42,705 |

**F1 / precision / recall**: `outputs/55maps-image-generalisation/evaluation/evaluation.json`

| Buffer (m) | F1 | F1 CI | Precision | Recall | Key path prefix |
|---:|---:|:---:|---:|---:|:---|
| 20 | 0.506 | [0.492, 0.520] | 0.5117 | 0.5004 | `summary.buffers[0]` |
| 30 | 0.6855 | [0.6723, 0.6974] | 0.6932 | 0.678 | `summary.buffers[1]` |
| 40 | 0.7483 | [0.7372, 0.7595] | 0.7567 | 0.74 | `summary.buffers[2]` |
| 50 | 0.771 | [0.7604, 0.7817] | 0.7796 | 0.7625 | `summary.buffers[3]` |

**Bootstrap metadata**: `outputs/55maps-image-generalisation/evaluation/evaluation.metadata.json`

- `bootstrap.n_iterations = 1000`, `bootstrap.seed = 42`,
  `bootstrap.resampling_unit = "tile_level"`.
- `invocation.command` records the exact CLI invocation.

**Dawid-Skene**: `results/55maps-image-generalisation/dawid-skene/dawid-skene-results.json`

- `measured.f1` = 0.771 (matches the evaluation above at 50 m buffer)
- `dawid_skene.corrected_metrics.f1` = 0.7954 → rounds to **0.795**
- `dawid_skene.corrected_metrics.vlm_only_posterior` = 0.1862
- `parameters.buffer_metres` = 50

**D-S caveat (Obs 273)**: `docs/notes/reflections/working-notes.md:12840`
states "the 'D-S aggregate corrected F1 = 0.795' recorded in
`results/55maps-image-generalisation/human-reviewed-corrected/corrected-f1-human-reviewed.md`
is an artefact of this under-estimate, not an independent corroboration
of the human-review corrected F1." The figure stands as recorded; the
paper should cite the caveat.

**D-S v2 (data-driven prior sweep)**:
`results/55maps-image-generalisation/dawid-skene-v2-data-driven-prior/dawid-skene-results-v2.json`

- `dawid_skene.corrected_metrics.f1` = 0.8917 (at empirical prior;
  posterior degenerates to 1.0)
- `dawid_skene.corrected_metrics.vlm_only_posterior` = 1.0

This is the Obs 273 "pathology at every informative prior" finding.

**Paired permutation test**: no single 50 m paired test at the image-
run level against text HIGH re-run is stored under
`results/55maps-image-generalisation/`. Modality comparison lives
in working-notes Obs 256 (line 11206).

**Pre-launch audit**:
`configs/run-configs/55maps_image_generalisation_pre_launch_audit.md`
(present; 9,611 bytes).

**Post-run report**:
`configs/run-configs/55maps_image_generalisation_post_run_report.md`
(present; 11,323 bytes). Second copy filed at
`outputs/55maps-image-generalisation/post_run_report.md` per the
publishable-launcher convention.

**Working-notes observation cites**:

- Obs 256 (line 11206) — F1 = 0.771 measured, 0.795 D-S corrected.
- Obs 257 (line 11287) — per-map heterogeneity, 4× wider F1 distribution
  out-of-sample.
- Obs 262 (line 11780) — benchmark-on-settlement-mound feature-symbol
  hybrid.
- Obs 263 (line 11877) — review-UI decision noise.
- Obs 264 (line 12033) — label-pull as centroid-localisation failure.
- Obs 265 (line 12242) — contour-ring FP class.
- Obs 266 (line 12291) — subtype classification less reliable than
  detection.
- Obs 267 (line 12394) — human-reviewed corrected F1 = 0.830 at 50 m.
- Obs 268 (line 12490) — tolerance-circle UI tightening effect.
- Obs 269 (line 12550) — verifier over-confidence and quantisation.
- Obs 272 (line 12770) — attractor-pull scale ends at 125 m.
- Obs 273 (line 12840) — D-S structural inadequacy.

**Post-matrix analyses attached to this run**:

| Analysis | Primary artefact | Key headline |
|---|---|---|
| Human-reviewed corrected F1 (50 m) | `results/55maps-image-generalisation/human-reviewed-corrected/corrected-f1-human-reviewed.json` → `corrected.f1` | 0.8295 → 0.830 |
| Multi-buffer corrected F1 | `results/55maps-image-generalisation/corrected-f1-multi-buffer/summary.json` → `results[*].F1` | 0.832 at R=50 m → 0.855 at R=150 m |
| Buffer-band lift | `results/55maps-image-generalisation/buffer-band-lift/summary.json` → `cumulative[*].lift_ratio` | 118× at R=50 m; effect ends ~125 m |
| Buffer-100 m diagnostics | `results/55maps-image-generalisation/buffer-100m-diagnostics/summary.json` | GT clustering + pair-drift decomposition |
| Verifier calibration | `results/55maps-image-generalisation/verifier-calibration-crosstab/calibration.json` → `ece`, `auc.point` | ECE 0.269, AUC 0.655 |
| Uncalibrated vs calibrated review | `results/55maps-image-generalisation/uncalibrated-vs-calibrated-crosstab/crosstab.json` → `rates.disagreement_rate` | 21 % one-directional flip |
| D-S v1 cross-tab | `results/55maps-image-generalisation/ds-human-crosstab/summary.json` → `ece`, `auc` | ECE 0.539, AUC 0.500 (prior-invariant) |
| D-S v2 prior sweep | `results/55maps-image-generalisation/dawid-skene-v2-data-driven-prior/dawid-skene-results-v2.json` | Posterior collapses to 1.0 at empirical prior |
| Human-review multi-buffer CSV | `results/55maps-image-generalisation/human-review-multi-buffer.csv` | 557 rows |

---

### A2. `55maps-generalisation` (retrospective text HIGH, 2026-04-10)

**Scope**: Text-modality HIGH-thinking 5-pass generalisation. Launched
via session-specific bash (`scripts/55maps-overnight.sh`) before the
publishable launcher existed; documentation is retrospective.

**Cost manifest**: NOT PRESENT. The retrospective post-run report at
`configs/run-configs/55maps_text_generalisation_retrospective_post_run_report.md`
notes at lines 115–117: "Proposer estimate: 5 × (8541 / 487) × $0.70 ≈
"$61 (estimated)", "Verifier v1 (measured): $12.43", and "Total
estimated: ~$75 (v1-only); ~$88 including v2." The $12.43
verifier figure is measured from `outputs/55maps-generalisation/verified/run.meta.json`;
the proposer figure is an estimate by scaling from
`outputs/h11/pv-diag-384/flash-high-text-n5/`. No aggregate file
equivalent to `totals.cost_usd` exists.

**F1 / precision / recall**:
`results/55maps-generalisation/buffer_sensitivity.json`
(the retrospective evaluation)

| Buffer (m) | F1 | F1 CI | Key path |
|---:|---:|:---:|:---|
| 20 | 0.6232 | [0.6087, 0.6375] | `buffers[0].f1`, `.ci.f1.lower/upper` |
| 30 | 0.7551 | [0.7433, 0.7668] | `buffers[1]` |
| 40 | 0.7832 | [0.7723, 0.794] | `buffers[2]` |
| 50 | 0.7898 | [0.7793, 0.8005] | `buffers[3]` |

The retrospective report (line 42) also quotes F1 = 0.7902 at threshold
0.20 as the numerical optimum; the 0.15 value used for cross-modality
symmetry is 0.7898 → 0.790.

**Bootstrap metadata** (retrospective): the retrospective report at
line 37 records "bootstrap = 1,000, seed = 42, 50 m buffer, 1,000-
iteration tile-level resampling". `results/55maps-generalisation/`
does not carry a standalone `evaluation.metadata.json` sidecar; the
CI-metadata registry at `results/ci-metadata-registry.md` enumerates
any that exist.

**Dawid-Skene**: `results/dawid-skene/dawid-skene-results.json` (shared
location for the retrospective run; the three post-retrospective runs
each have their own `dawid-skene/` sub-directory under
`results/55maps-*/`)

- `measured.f1` = 0.7898 → rounds to 0.790
- `dawid_skene.corrected_metrics.f1` = 0.8144 → rounds to **0.814**
- `parameters.buffer_metres` = 50
- `parameters.threshold` = 0.15

**Paired permutation test**: no planned comparator. Later runs use
this as a comparator via
`results/55maps-text-high-generalisation/paired-vs-high-2026-04-10-50m/pairwise_permutation_result.json`
(tests the 2026-04-19 re-run against the retrospective run).

**Pre-launch audit**: NOT PRESENT (retrospective run).

**Post-run report**:
`configs/run-configs/55maps_text_generalisation_retrospective_post_run_report.md`
(present; 10,873 bytes). A second summary at
`outputs/55maps-generalisation/post_run_report_retrospective.md` also
exists.

**Working-notes observation cites**:

- The retrospective is the comparator for **Obs 258** (line 11378) —
  HIGH thinking on 55-map text generalisation, paired permutation vs
  text-min by buffer.

---

### A3. `55maps-text-min-generalisation` (2026-04-15)

**Scope**: Text-modality MINIMAL-thinking 5-pass generalisation.

**Cost manifest**: `outputs/55maps-text-min-generalisation/cost_manifest.json`

| Claim | Key path | Value |
|---|---|---|
| Total cost (USD) | `totals.cost_usd` | 60.7866 → 60.79 |
| Input tokens | `totals.input_tokens` | 82,297,662 |
| Cached tokens | `totals.cached_tokens` | 0 |
| Cache-hit rate | `totals.cache_hit_rate` | 0.0 |
| Wall-clock (s) | `totals.wall_clock_seconds` | 6,953.106 |
| Tiles processed | `by_stage.proposer.tiles_processed` | 42,705 |
| Tiles failed | `by_stage.proposer.tiles_failed` | 124 (failure rate 0.0029) |

The 0 cached tokens is the single biggest divergence from the image
run; text prompts are below the Flash minimum cache size so context
caching does not apply.

**F1 / precision / recall**: `outputs/55maps-text-min-generalisation/evaluation/evaluation.json`

| Buffer (m) | F1 | F1 CI | Precision | Recall | Key path prefix |
|---:|---:|:---:|---:|---:|:---|
| 20 | 0.618 | [0.6024, 0.6339] | 0.6908 | 0.5591 | `summary.buffers[0]` |
| 30 | 0.7274 | [0.714, 0.7399] | 0.813 | 0.6581 | `summary.buffers[1]` |
| 40 | 0.7538 | [0.7415, 0.7661] | 0.8425 | 0.682 | `summary.buffers[2]` |
| 50 | 0.7591 | [0.7469, 0.7715] | 0.8485 | 0.6868 | `summary.buffers[3]` |

**Bootstrap metadata**: `outputs/55maps-text-min-generalisation/evaluation/evaluation.metadata.json`
— `bootstrap.n_iterations = 1000`, `bootstrap.seed = 42`,
`bootstrap.resampling_unit = "tile_level"`.

**Dawid-Skene**:
`results/55maps-text-min-generalisation/dawid-skene/dawid-skene-results.json`

- `measured.f1` = 0.7591 (matches evaluation at 50 m)
- `dawid_skene.corrected_metrics.f1` = 0.7834 → rounds to **0.783**
- `dawid_skene.corrected_metrics.vlm_only_posterior` = 0.2947
- `parameters.buffer_metres` = 50

**Paired permutation tests**:
`results/55maps-text-min-generalisation/paired-vs-high/` and
`results/55maps-text-min-generalisation/paired-vs-high-20m/`. Each
holds one `pairwise_permutation_result.json`; these record
10,000-iteration permutation tests against the text HIGH comparator.

**Pre-launch audit**:
`configs/run-configs/55maps_text_min_generalisation_pre_launch_audit.md`
(present; 13,691 bytes).

**Post-run report**:
`configs/run-configs/55maps_text_min_generalisation_post_run_report.md`
(present; 17,112 bytes). Second copy at
`outputs/55maps-text-min-generalisation/post_run_report.md`.

**Working-notes observation cites**:

- Obs 258 (line 11378) — HIGH vs MINIMAL paired permutation test,
  buffer-dependent split.
- Obs 259 (line 11502) — text HIGH uses 20 % more thinking tokens per
  call than image HIGH.

---

### A4. `55maps-text-high-generalisation` (2026-04-19 re-run)

**Scope**: Text-modality HIGH-thinking 5-pass generalisation, re-run
under the publishable launcher to obtain a `cost_manifest.json`
companion to the 2026-04-10 retrospective text run.

**Cost manifest**: `outputs/55maps-text-high-generalisation/cost_manifest.json`

| Claim | Key path | Value |
|---|---|---|
| Total cost (USD) | `totals.cost_usd` | 69.6017 → 69.60 |
| Input tokens | `totals.input_tokens` | 80,505,662 |
| Output tokens | `totals.output_tokens` | 9,782,952 |
| Cached tokens | `totals.cached_tokens` | 0 |
| Thinking tokens | `totals.thinking_tokens` | 115,013,258 |
| Cache-hit rate | `totals.cache_hit_rate` | 0.0 |
| Wall-clock (s) | `totals.wall_clock_seconds` | 10,754.918 |
| Tiles processed | `by_stage.proposer.tiles_processed` | 42,545 |
| Tiles failed | `by_stage.proposer.tiles_failed` | 160 (failure rate 0.0037) |

The 115 M thinking tokens is the HIGH-thinking cost driver; the cost
is nonetheless comparable to text-min because no thinking-token cost
applies under the gemini-3-flash pricing as of the run date.

**F1 / precision / recall**: `outputs/55maps-text-high-generalisation/evaluation/evaluation.json`

| Buffer (m) | F1 | F1 CI | Precision | Recall | Key path prefix |
|---:|---:|:---:|---:|---:|:---|
| 20 | 0.6227 | [0.6078, 0.6379] | 0.6698 | 0.5818 | `summary.buffers[0]` |
| 30 | 0.7533 | [0.741, 0.7658] | 0.8103 | 0.7038 | `summary.buffers[1]` |
| 40 | 0.7829 | [0.7717, 0.7946] | 0.8421 | 0.7314 | `summary.buffers[2]` |
| 50 | 0.7883 | [0.7773, 0.8] | 0.8479 | 0.7365 | `summary.buffers[3]` |

**Bootstrap metadata**:
`outputs/55maps-text-high-generalisation/evaluation/evaluation.metadata.json`
— `bootstrap.n_iterations = 1000`, `bootstrap.seed = 42`.

**Dawid-Skene**:
`results/55maps-text-high-generalisation/dawid-skene/dawid-skene-results.json`

- `measured.f1` = 0.7883 (matches evaluation at 50 m)
- `dawid_skene.corrected_metrics.f1` = 0.8129 → rounds to **0.813**
- `dawid_skene.corrected_metrics.vlm_only_posterior` = 0.2935
- `parameters.buffer_metres` = 50

**Paired permutation tests**:
`results/55maps-text-high-generalisation/paired-vs-min-{20,30,40,50}m/pairwise_permutation_result.json`
plus `paired-vs-high-2026-04-10-50m/pairwise_permutation_result.json`
(comparing the re-run to the retrospective run).

| Buffer | Δ F1 | p (two-sided) | N permutations | Key path (each file) |
|---:|---:|---:|---:|---|
| 20 m | 0.004681 | 0.4647 | 10,000 | `permutation_test.{observed_f1_diff, p_value, n_permutations}` |
| 30 m | 0.025904 | 0.0 | 10,000 | same |
| 40 m | 0.029107 | 0.0 | 10,000 | same |
| 50 m | 0.029163 | 0.0 | 10,000 | same |

These tests underpin Obs 258 ("HIGH thinking helps approximate-match
retention, not precise localisation — paired permutation test on
55-map text generalisation reveals a buffer-dependent split").

**Pre-launch audit**:
`configs/run-configs/55maps_text_high_generalisation_pre_launch_audit.md`
(present; 16,677 bytes).

**Post-run report**:
`configs/run-configs/55maps_text_high_generalisation_post_run_report.md`
(present; 18,978 bytes). No copy inside the `outputs/` directory; the
only post-run report lives under `configs/run-configs/`.

**Working-notes observation cites**:

- Obs 258 (line 11378), Obs 259 (line 11502), Obs 260 (line 11584) —
  student-GT positional jitter quantified via F1-curve shift.

---

## B. Era 1: h-series hypothesis runs

Structural coverage is unchanged from the prior audit; the substantive
numbers are restated below with citations. Era 1 runs predate the
cost-accounting infrastructure and the Dawid-Skene pipeline; neither
is expected.

### B1. `h8-v2` library composition

| Artefact | Path | Notes |
|---|---|---|
| Greedy threshold sweep | `results/h8-v2/greedy/` | F1/P/R at 20 m buffer across thresholds |
| WBF sweep | `results/h8-v2/wbf/` | Weighted Box Fusion variant |
| Permutation tests | `results/h8-v2/permutation-t4/` | Tile-level permutation p-values |
| Verifier sweep | `results/h8-v2/verifier-sweep/` | Multi-fold verifier analysis |

**Gaps**: no multi-buffer curve (30/40/50 m missing), no pre-launch
audit, no cost manifest, no post-run report, no D-S (not applicable —
single-annotator gold-standard).

**Working-notes**: Obs 238 (three-way library null after BH-FDR).

### B2. `h10` calibration pool

| Artefact | Path | Notes |
|---|---|---|
| Statistical analysis | `results/h10/statistical_analysis.json` | Per-config optimum + ICC |
| K=5 replicate sweep | `results/h10/k5_replicate_sweep.json` | Variability bound |
| Pool-size permutation | `results/h10/h10_pv_permutation_020_vs_160.json` | Pool 20 vs 160 |
| Verifier independence | `results/h10/verifier_independence_probe.md` | ICC(2,1) diagnostic |

**Gaps**: multi-buffer curve missing (20 m only), no pre-launch audit,
no formal post-run report.

**Working-notes**: Obs 235 (formal retraction of the "library effect"
claim from the earlier Obs 227/234 analyses after the config-intent
mismatch was found). Obs 235 is a load-bearing note for h10.

### B3. `h11` two-stage design

| Artefact | Path | Notes |
|---|---|---|
| Proposer-verifier diagnostic | `results/h11-384-pv-diagnostic/` | Threshold sweep + bootstrap CIs |
| Single-pass t=0 re-run | `results/h11-384-single-pass-t0-rerun/` | |

**Active Era 1 subdirs under `outputs/h11/`** (after 2026-04-21
quarantine):

- `consensus-384-UNINTENDED-T1.0/` — accidental T=1.0 launch; NOT
  formally excluded or archived.
- `e47-propose-brief/` — proposer brief pilot.
- `gold-standard-v2/` — gold-standard generation (calibration mining).
- `n1-outstanding-384/` — N=1 diagnostic.
- `propose-brief-v1-test/` — brief prompt variant pilot.
- `proposer-verifier-384/` — canonical 384 px PV pipeline.
- `proposer-verifier-512/` — 512 px PV variant.
- `pv-diag-256/`, `pv-diag-384/` — diagnostic runs.
- `single-pass-384-UNINTENDED-T1.0/` — accidental T=1.0.
- `v2-proposer-test/` — v2 proposer prototype.
- `wbf/` — WBF consensus variant.

**Archived (quarantine)**: seven sub-directories moved to
`archive/v2-verifier-contamination/raw-outputs/`. These include
`e47-propose-brief--verified-v2`, `gold-standard-v2--verified-v2`,
and five others.

**Gaps**: no proposer-vs-verifier paired test; fragmented narrative
across the 12 unarchived subdirs; UNINTENDED runs unresolved.

**Working-notes**: Erratum E47 — Proposer Prompt Substitution (`detect_brief-text` used instead of preregistered `propose_brief`; `docs/notes/reflections/working-notes.md` line 6553). Note: this is distinct from protocol-errata E47 (`docs/methodology/preregistration/protocol-errata.md` line 1233, buffer-matching revert), which shares the identifier by historical re-numbering.

### B4. `h12-v2` HP:HN ratio

| Artefact | Path | Notes |
|---|---|---|
| Analysis summary | `results/h12-v2/analysis_summary.md` | Strongest Era 1 narrative (best single-hypothesis write-up) |
| Greedy cohort | `results/h12-v2/greedy/` | Bootstrap CIs, seed 42 |
| WBF cohort | `results/h12-v2/wbf/` | |
| Permutation (t=4) | `results/h12-v2/permutation-t4/` | Three-way contrast with BH-FDR |
| Permutation (WBF) | `results/h12-v2/permutation-wbf/` | |

**Gaps**: multi-buffer curve missing (20 m primary), no formal cost
manifest, no pre-launch audit.

**Working-notes**: analysis_summary.md is the narrative; Obs 239–245
(Era 1 findings in the HP:HN axis).

### B5. `retest` (Phase 2 and Phase 3 production rebuild)

| Artefact | Path | Notes |
|---|---|---|
| Phase 2 sub-runs | `outputs/retest/phase2{a..e}/` | Factorial design |
| Phase 3a matrix | `outputs/retest/phase3a/` plus high/replication | Consensus holdout |
| Phase 3c | `outputs/retest/phase3c/` | Diversity study |
| Evaluations | `results/retest/*.json` | Per-phase F1/P/R + pairwise bootstrap |
| Summary | `results/retest/retest-production-summary.md` | Strongest Era 1 narrative (matched by h12-v2's) |

**Gaps**: no cost manifest (internal development), no pre-launch
audits, multi-buffer coverage inconsistent.

---

## C. Analytical directories under `results/`

### C1. Cross-hypothesis / phase matrices

| Directory | Headline artefact | Notes |
|---|---|---|
| `results/phase3a-image-matrix/` | `all-evaluations.json` + sidecar | 2×4 thinking × temperature matrix (image) |
| `results/phase3a-text-matrix/` | `all-evaluations.json` | 2×4 thinking × temperature matrix (text) |
| `results/phase3c-diversity/` | `phase3c-comprehensive-results-report.md` + cross-track comparison | |
| `results/cross-hypothesis-library/permutation-t4/` | Permutation test across hypotheses | |
| `results/pairwise/` | Per-buffer pairwise matrices | 20/30/40/50 m coverage mixed |
| `results/factor-analysis/` | Factor analysis output | |
| `results/secondary-effects/` | `secondary_effects.json` + sidecar | |
| `results/tolerance-sensitivity/` | `tolerance-sensitivity.{csv,json}` | |
| `results/wbf-greedy-comparison/` | `wbf_vs_greedy_*` | Production fusion comparison |
| `results/pv/` | Proposer-verifier pipeline aggregates | |
| `results/e47-propose-brief/` | Five-of-five brief-prompt variants | |

### C2. Leaderboard

- `results/leaderboard/` — three tiers (era1, era2, era3) each holding
  `leaderboard_all_evaluations.json` + tier markdown + metadata sidecar.
- `results/leaderboard/cells/` — per-condition leaderboard cells; the
  v2-contaminated cell `gold-standard-v2-greedy-v2-327tile.json` was
  moved to `archive/v2-verifier-contamination/leaderboard-cells/` on
  2026-04-21.

### C3. Gold-standard corpus

| Directory | Artefact | Headline |
|---|---|---|
| `results/gold-standard-subtype-classification/` | `macro_weighted_summary.json` | Weighted-F1 0.8873 at 50 m (Obs 270, line 12649) |
| `results/gold-standard-extended-buffer-sweep/` | `evaluation.json` + metadata + markdown | Buffer sweep 5/10/15/25/35/45 m on gold standard |

### C4. Cleaned-ground-truth re-evaluation (2026-04-19)

`results/55maps-cleaned-gt-evaluation/{image, text-min, text-high}/evaluation.json`
— re-runs the three production-launcher runs against the cleaned GT
produced by `scripts/review_gt_duplicates.py`.

| Cohort | F1 @ 50 m measured (cleaned GT) | Key path |
|---|---:|---|
| image | 0.7729 | `summary.buffers[3].f1` |
| text-min | 0.7614 | `summary.buffers[3].f1` |
| text-high | 0.7906 | `summary.buffers[3].f1` |

These are close but not identical to the student-GT numbers; the
delta is the cleaning effect quantified in Obs 261 (line 11651).

### C5. GT investigation artefacts

- `results/gt-duplicate-review/` — reviewer decisions + diff.
- `results/gt-spacing-analysis/` — spacing structure on student and
  gold-standard GTs.

### C6. Paper-tables consolidation (2026-04-21)

`results/paper-tables/` — 26 files. Key artefacts with CI-metadata
sidecars: `metrics_master.{csv,json,metadata.json}`,
`pipeline_progression.{csv,json,metadata.json}`,
`pro_2x2_matrix.{json,md,metadata.json}`,
`tile_size_comparison.{json,metadata.json}`,
`cost_retrospective.{json,metadata.json}`,
`pairwise_hypothesis_table.{csv,md}`,
`gold-standard-spatial-tolerance.{csv,md}`,
`subtype-classification.{csv,md}`,
`leaderboard_tiers.{csv,md}`,
`leaderboard-20m-annotated.md`,
`leaderboard_tiers_20m.md`, `n1_leaderboard.csv`,
`spatial_tolerance_comparison.md`, `spatial_tolerance_curve.csv`.

---

## D. QGIS and validation directories

These are verification tools, not experimental runs, and are counted
the same way as in the prior audit:

- `outputs/qgis-sanity-check/`
- `outputs/qgis-dedup-check/`
- `outputs/qgis-wbf-check/`

No evaluation artefacts expected.

---

## E. CI-metadata registry and bootstrap provenance

`results/ci-metadata-registry.md` is the master registry for the 48
sidecar files that now accompany every bootstrap CI in the project.
The registry records, per artefact, the iteration count, seed,
resampling unit, library entry point, and generating-script commit.

Protocol errata E54 (`docs/methodology/preregistration/protocol-errata.md:1670`)
formalises the split:

- **1 000 iterations (preregistered)**: `evaluate_detections.py`,
  `compute-pairwise-effect-sizes.py`, `evaluate_pv_results.py`,
  `compare_wbf_vs_greedy.py`, `analyse_secondary_effects_text.py`,
  `analyse_buffer_band_lift.py` (permutation convention).
- **10 000 iterations (post-hoc)**:
  `compute_corrected_f1_human_reviewed.py`,
  `compute_corrected_f1_multi_buffer.py`,
  `analyse_subtype_classification.py`,
  `crosstab_uncalibrated_vs_calibrated.py`.

All headline paper numbers derive from 1 000-iteration preregistered
bootstraps; the 10 000-iteration runs tighten CIs on narrow-effect
post-hoc analyses where 2-3 decimal place precision is material.

---

## F. Cross-references

- `docs/notes/reflections/working-notes.md` — Observation log. Line
  numbers for the 18 observations cited by this audit:

  ```text
  11206  Obs 256  55-map image F1 = 0.771 measured, 0.795 D-S
  11287  Obs 257  Image per-map heterogeneity
  11378  Obs 258  Paired test HIGH vs MIN, buffer-dependent
  11502  Obs 259  Text HIGH uses 20 % more thinking tokens
  11584  Obs 260  Student GT ~25 m positional jitter
  11651  Obs 261  Student GT bimodal duplicates at ~50 m
  11780  Obs 262  Benchmark-on-burial-mound hybrid feature
  11877  Obs 263  Review-UI decision noise (revised)
  12033  Obs 264  Label-pull as centroid-localisation failure
  12242  Obs 265  Contour-ring FP class
  12291  Obs 266  VLM subtype less reliable than detection
  12394  Obs 267  Human-reviewed corrected F1 = 0.830
  12490  Obs 268  Tolerance-circle UI tightening
  12550  Obs 269  Verifier over-confidence, AUC 0.655
  12649  Obs 270  Subtype classification weighted-F1 = 0.887
  12711  Obs 271  Asymmetric within-compound confusion
  12770  Obs 272  Attractor-pull ends at ~125 m
  12840  Obs 273  D-S structural inadequacy, prior-invariant
  ```

- `docs/methodology/preregistration/protocol-errata.md` — E47, E52,
  E54.
- `docs/methodology/v2-verifier-contamination-policy.md` — quarantine
  policy.
- `archive/v2-verifier-contamination/MANIFEST.md` and
  `README.md` — quarantine inventory.
- `results/ci-metadata-registry.md` — master CI sidecar registry.
- `planning/doc-audit-rerun-plan.md` — plan document for this
  re-audit, including the known-correct anchor values and the
  known-errors list from the prior audit.

---

## G. What changed relative to the 2026-04-18 audit

1. **Text-min cost corrected**: $165.74 → $60.79 (per
   `outputs/55maps-text-min-generalisation/cost_manifest.json`
   `totals.cost_usd`).
2. **Text-min cache-hit corrected**: 90.2 % → 0.0 % (per
   `totals.cache_hit_rate` in the same file).
3. **Text-high conflation split**: a single "text-high at $359.53"
   entry is replaced by two distinct rows — the 2026-04-10
   retrospective run (~$75 estimate, no cost manifest) and the
   2026-04-19 re-run ($69.60 measured).
4. **Observation attributions corrected**: blanket "Obs 255" removed.
   The post-matrix observations are Obs 256 (image F1 headline) and
   Obs 258–260 (text paired-test findings), with Obs 262–273 covering
   the 2026-04-20/21 human-review day analyses.
5. **New analytical artefacts catalogued**: multi-buffer corrected F1,
   D-S v1/v2 cross-tabs, buffer-band lift, buffer-100 m diagnostics,
   verifier calibration, uncalibrated-vs-calibrated crosstab, subtype
   classification, human-review multi-buffer CSV, paper-tables
   consolidation.
6. **CI-metadata registry and E54 surfaced** as auditable infrastructure
   for every bootstrap CI in the project.
7. **v2-verifier quarantine noted**: 100 files excluded from active-run
   scope as of 2026-04-21.
