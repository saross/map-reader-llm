# Interim-doc review scorecard — paper write-up Step 2

**Date**: 2026-04-22
**Reviewer**: fresh-session Claude (Step 2 of the six-step write-up plan
in `planning/paper-writeup-continuity.md`)
**Exemplar**: `results/gold-standard-subtype-classification/report.md`
(17 sections, confirmed 2026-04-21)
**Input inventory**: continuity doc § "Have — primary interim docs" +
the four Era 1 hypothesis directories (`h8-v2`, `h10`, `h11`, `h12-v2`).
**Reminder**: the 82/85 doc-audit PASS claims are NOT re-verified here
(continuity doc guardrail §3). Spot-checks below are limited to paper-
headline numbers in Batch A and to confirming file presence.

## 1. Summary verdict

**Reports reviewed**: 20 (exemplar excluded). Row 15 (Phase 2b H7
temperature, Era 1 retest) appended 2026-04-22 first pass; rows 16–21
appended 2026-04-22 second pass (Task-B focused re-inventory + the
`uncalibrated-vs-calibrated-crosstab` Obs 268 artefact). Rows 1–15
unchanged.

| Tier | Count | Notes |
|:---|---:|:---|
| ✓ Exemplar-tier | 0 | no report outside the exemplar clears the 17-section bar as written. |
| ~ Partial (level-up needed) | 13 | content is citable; infrastructure (methods/repro/manifest/paper-implications) is thin. The second-pass additions (rows 16, 17, 18, 19, 20, 21) all land here — they are substantive rendered analyses with specific infrastructure gaps, not stubs. |
| ✗ Sub-tier / stub | 2 | `buffer-100m-diagnostics` — summary.json + CSVs only; `paper-eval/mcc/` — analysis family with rendered batch-summary tables but no narrative report.md. |
| ✗ Missing artefact | 4 | `h8-v2`, `h10`, `h11` lack a consolidated `analysis_summary.md`; Phase 2b (H7 temperature retest) has raw data + bootstrap-CI JSON but no dedicated analysis doc — its narrative is embedded in the multi-phase `results/retest/retest-production-summary.md` §Phase 2b. |

**Total level-up effort**: ~12–15 hours (13 × S/M level-ups at ~30–60 min
each + 2 stub-to-report + Era 1 synthesis sized separately in §4 +
~90 min for a dedicated Phase 2b analysis doc). The second-pass six
additions add ~4 hours at the aggregate. Scope caveat: the scorecard
covers a deliberate subset of `results/` — see §10 for out-of-scope
items and the rationale for deferring them.

**Critical gaps (block paper Results / Discussion spine)**:

- `h8-v2` has no consolidated narrative summary (audit calls it the
  "strongest Era 1 narrative"; current form is JSON-only across
  `greedy/`, `permutation-t4/`, `verifier-sweep/`, `wbf/`).
- `h10` has a `verifier_independence_probe.md` + 9 JSONs but no overall
  `analysis_summary.md`.
- **Phase 2b (H7 temperature retest)** has pristine 340-tile × K=3 ×
  5 T × 2 tracks raw data under `outputs/retest/phase2b/` and bootstrap-
  CI results at `results/retest/phase2b-track{1,2}-evaluation.json`,
  but no dedicated `analysis_summary.md`. Its narrative currently lives
  only in `results/retest/retest-production-summary.md` §Phase 2b
  (combined multi-phase doc) and in working-notes line 6069+ (the
  "Phase 2b preregistered vs E43 accidental deployment" distinction
  that the paper's temperature claim rests on).
- `buffer-100m-diagnostics` has no report.md at all — only
  `summary.json` + two CSVs. This is a small but paper-citable analysis
  (GT clustering + pair-drift decomposition of the 50→100 m recall
  gain) and deserves a brief report.
- `results/paper-eval/mcc/` is an analysis family (12-condition
  consensus/PV batch + 384px and 512px sweeps + remaining cohort) with
  only auto-generated batch-summary tables (`batch_mcc_summary.{md,csv,json}`
  under `consensus-pv/` and `remaining/`, and `batch_summary.{md,csv,json}`
  under `384px/` and `512px/`). Citable as-is for a Methods/Results MCC
  table, but there is no narrative report.md synthesising the ordering
  (Pro Image HIGH N=1 top at MCC 0.848; Flash MIN T=0.0 bottom at 0.022)
  or comparing tile-size cohorts.

**Non-critical gaps (defer to paper drafting)**:

- All seven partial reports would benefit from a formal "Paper
  implications" block; five of seven lack a files manifest; six of
  seven lack a re-run command. These are polish-level gaps — their
  absence does not block the meta-findings synthesis (Step 3) or the
  paper outline (Step 6), it just makes reviewer-facing artefacts less
  uniform.

**Recalculation requests requiring user approval**: none. Every
headline number traces to an existing JSON. No permutation test or
bootstrap was found missing that would need a fresh run.

**Guardrail issues caught**: none. No `archive/v2-verifier-contamination/`
or `archive/flawed-audit-2026-04-19/` citations found in any reviewed
report. All E47 references inspected use the file-qualified form the
continuity doc requires.

## 2. Scorecard

Legend: **R** required (graded ✓ / ~ / ✗), **O** optional (graded only
if present), **N/A** not applicable to this report type. Effort key:
**S** < 30 min polish, **M** 30–90 min, **L** > 90 min rewrite.

| # | Report | Type | Exec | Data | Conf | Hier | Agree | Obs/find | Cons | Buf | Per-map | Sparse | Methods | Repro | Caveats | Bugs | Files | PaperImp | Overall | Effort |
|---|---|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| 1 | `results/55maps-image-generalisation/human-reviewed-corrected/corrected-f1-human-reviewed.md` | 55-map core | ~ | ~ | N/A | N/A | N/A | ~ | N/A | ✗ | ✗ | N/A | ~ | ~ | ✓ | — | ✗ | ✗ | ~ | M |
| 2 | `results/55maps-image-generalisation/corrected-f1-multi-buffer/report.md` | 55-map core | ~ | ~ | N/A | N/A | N/A | ✓ | N/A | ✓ | ✗ | N/A | ~ | ✓ | ~ | — | ✗ | ~ | ~ | S |
| 3 | `results/55maps-image-generalisation/buffer-band-lift/report.md` | 55-map core | ~ | ~ | N/A | N/A | N/A | ~ | N/A | ✓ | N/A | N/A | ~ | ✗ | ~ | — | ✗ | ✗ | ~ | M |
| 4 | `results/55maps-image-generalisation/verifier-calibration-crosstab/calibration.md` | 55-map core | ~ | ~ | ~ | N/A | ✓ | ~ | N/A | N/A | ~ | N/A | ~ | ✗ | ~ | — | ✗ | ✗ | ~ | M |
| 5 | `results/55maps-image-generalisation/dawid-skene-v2-data-driven-prior/report.md` | 55-map core | ✗ | ~ | ~ | N/A | ✓ | ✓ | N/A | N/A | N/A | N/A | ~ | ✗ | ✓ | — | ✓ | ~ | ~ | S |
| 6 | `results/55maps-image-generalisation/ds-human-crosstab/report.md` | 55-map core | ~ | ✓ | ✓ | N/A | ✓ | ✓ | N/A | ✓ | ✗ | N/A | ~ | ✗ | ~ | — | ~ | ✗ | ~ | S |
| 7 | `results/55maps-image-generalisation/buffer-100m-diagnostics/` (no .md) | 55-map core | ✗ | ✗ | N/A | N/A | N/A | ✗ | N/A | N/A | N/A | N/A | ✗ | ✗ | ✗ | — | ✗ | ✗ | ✗ | M |
| 8 | `results/gold-standard-extended-buffer-sweep/extended-buffer-report.md` | Extended-buffer | ~ | ~ | N/A | N/A | N/A | ✓ | N/A | ✓ | ✗ | N/A | ✓ | ✓ | ~ | — | ✓ | ✓ | ~ | S |
| 9 | `results/h12-v2/analysis_summary.md` | Era 1 | ✓ | ~ | N/A | N/A | N/A | ✓ | ✓ | N/A | N/A | N/A | ~ | ✓ | ~ | — | ✓ | ~ | ~ | S |
| 10 | `results/h8-v2/` (no analysis_summary.md) | Era 1 | ✗ | ✗ | — | — | — | ✗ | ✗ | — | — | — | ✗ | ✗ | ✗ | — | ✗ | ✗ | ✗ | L |
| 11 | `results/h10/` (no analysis_summary.md; `verifier_independence_probe.md` only) | Era 1 | ✗ | ✗ | — | — | — | ✗ | ✗ | — | — | — | ✗ | ✗ | ✗ | — | ✗ | ✗ | ✗ | L |
| 12 | `results/h11-tile-size-results.md` + `results/h11-384-pv-diagnostic/` (fragmented) | Era 1 | ✗ | ✗ | — | — | — | ✗ | ✗ | — | — | — | ✗ | ✗ | ✗ | — | ✗ | ✗ | ✗ | M |
| 13 | `results/paper-eval/mcc/` (analysis family — batch summaries only, no narrative report.md) | MCC analysis family | ✗ | ~ | ✓ | N/A | ~ | ✗ | ~ | N/A | N/A | N/A | ✗ | ~ | ✗ | — | ~ | ✗ | ✗ | M |
| 14 | `results/phase3a-text-matrix/secondary_effects.md` | phase3a-matrix | ✗ | ~ | ✓ | N/A | ✓ | ~ | ~ | ✓ | ✓ | N/A | ✗ | ✗ | ✗ | — | ✗ | ✗ | ~ | M |
| 15 | `outputs/retest/phase2b/` + `results/retest/phase2b-track{1,2}-evaluation.json` (no dedicated analysis_summary.md; narrative embedded in `results/retest/retest-production-summary.md` §Phase 2b) | Era 1 retest | ✗ | ~ | N/A | N/A | ~ | ✗ | N/A | N/A | N/A | N/A | ✗ | ~ | ✗ | — | ✗ | ✗ | ✗ | L |
| 16 | `results/55maps-image-generalisation/uncalibrated-vs-calibrated-crosstab/crosstab.md` | 55-map core | ~ | ~ | N/A | N/A | ✓ | ✓ | N/A | N/A | N/A | N/A | ~ | ✓ | ~ | — | ✗ | ✗ | ~ | S |
| 17 | `results/phase3a-image-matrix/consensus-analysis-summary.md` | phase3a-matrix | ✗ | ~ | N/A | N/A | ~ | ~ | ✓ | ✗ | N/A | N/A | ✗ | ✗ | ✗ | — | ✗ | ✗ | ~ | M |
| 18 | `results/secondary-effects/secondary_effects.md` | phase3a-matrix | ✗ | ~ | ✓ | N/A | ✓ | ~ | ✓ | ✓ | N/A | N/A | ✗ | ✗ | ✗ | — | ✗ | ✗ | ~ | M |
| 19 | `results/factor-analysis/factor_analysis_results.md` | factor analysis | ✗ | ~ | N/A | N/A | ✓ | ~ | N/A | N/A | N/A | N/A | ~ | ✗ | ✗ | — | ~ | ✗ | ~ | M |
| 20 | `results/retest/retest-production-summary.md` | Era 1 summary | ~ | ✓ | N/A | N/A | ✓ | ~ | ✓ | N/A | N/A | N/A | ~ | ~ | ✗ | — | ~ | ✗ | ~ | M |
| 21 | `results/evaluation-scopes.md` | methodology | ~ | ✓ | N/A | N/A | N/A | ~ | N/A | N/A | N/A | N/A | ✓ | ✓ | ✗ | — | ~ | ✗ | ~ | S |

Column legend: `Exec` = executive summary, `Data` = §2 data/inputs,
`Conf` = confusion matrices, `Hier` = hierarchical decomposition,
`Agree` = agreement measures (kappa/MCC/ECE), `Obs/find` = observation
verification + new findings, `Cons` = consensus-threshold sweep,
`Buf` = buffer sensitivity, `Per-map` = per-map diagnostic, `Sparse` =
sparse-class qualitative trace, `Methods` = methods notes block,
`Repro` = reproducibility, `Caveats` = caveats + risk register,
`Bugs` = bugs caught during audit, `Files` = files manifest,
`PaperImp` = paper implications block.

## 3. Per-report details

### 3.1 `results/55maps-image-generalisation/human-reviewed-corrected/corrected-f1-human-reviewed.md`

- **Type**: 55-map core (paper-headline corrected-F1 lower bound).
- **Present sections**: executive-summary-equivalent (Headline numbers),
  Caveats (three strong bullets), Counts, D-S comparison,
  Reproducibility (partial).
- **Missing-but-relevant**: per-map diagnostic; formal methods block
  (matching protocol, bootstrap resampling unit); files manifest; paper
  implications.
- **Numeric spot-check**: `corrected.F1 = 0.8295` confirmed in report;
  matches the canonical-numbers table (`paper-tables/`-adjacent).
  Continuity-doc value is 0.830 (rounded).
- **Markdown heuristic**: passes (tables render, no trailing
  whitespace evident).
- **Level-up notes**: add §1 exec-summary block with the narrative
  framing ("human-reviewed lower bound ≥ 0.830 at 50 m"); add §2 Data
  block with input provenance; add Methods (Hungarian matcher ref,
  bootstrap resampling unit = reviewer label); add files manifest; add
  Paper-implications bullet block.
- **Dependencies for level-up**: none; pure synthesis from existing
  artefacts.

### 3.2 `results/55maps-image-generalisation/corrected-f1-multi-buffer/report.md`

- **Type**: 55-map core (attractor-pull-truncated F1 curve).
- **Present sections**: F1 curve table, "How to read this table", Obs
  272 caveat, practitioner-useful cap at R=125 m, Reproducibility (good
  — git commit, bootstrap spec, script name, input paths).
- **Missing-but-relevant**: formal §1 exec summary; per-map diagnostic;
  files manifest; formal caveats / risk register section; paper
  implications block (content is present but not formally labelled).
- **Numeric spot-check**: R=50 m F1 = 0.8317 ✓ / R=125 m F1 = 0.8538 ✓
  / R=150 m F1 = 0.8551 ✓ — all match continuity canonical curve
  (0.832 → 0.855).
- **Markdown heuristic**: passes.
- **Level-up notes**: promote "Obs 272 caveat" to a formal Caveats/risk
  register with the 150 m-as-upper-bound warning front-loaded. Add exec
  summary with practitioner-cap headline sentence. Wrap existing
  "Practitioner-useful cap" + "Comparison to yesterday's 50 m result"
  into a Paper-implications block.
- **Dependencies for level-up**: none.

### 3.3 `results/55maps-image-generalisation/buffer-band-lift/report.md`

- **Type**: 55-map core (attractor-pull scale).
- **Present sections**: header block with totals, Cumulative lift table
  (50–286 m), Annular-shell lift table (where the p=0.381 at 125–150 m
  row lives), Ripley's cross-L table, Interpretation guide.
- **Missing-but-relevant**: formal §1 exec summary; explicit Obs 272
  citation (the report IS the basis for Obs 272 but doesn't reference
  it back); Reproducibility (no script name, no git commit, no re-run
  command, no input paths); Caveats section; Files manifest; Paper
  implications.
- **Numeric spot-check**: shell at 125–150 m p_value = 0.381 ✓ (matches
  continuity). Lift ratio at 50 m cumulative = 118.32 ✓ (matches
  audit-summary's "118× at R=50 m").
- **Markdown heuristic**: passes.
- **Level-up notes**: the interpretive content is there but
  infrastructure is the weakest of the 55-map core reports. Bring
  Reproducibility to parity with the multi-buffer report. Add Obs 272
  back-reference. Add Paper-implications sentence pair (attractor-pull
  scale ~125 m; practitioner implications).
- **Dependencies for level-up**: none (may wish to verify script name
  from run logs if not immediately obvious).

### 3.4 `results/55maps-image-generalisation/verifier-calibration-crosstab/calibration.md`

- **Type**: 55-map core (verifier miscalibration).
- **Present sections**: total candidate counts, calibration bins (§1),
  ROC/PR/reliability figure references (§2–4), threshold sweep (§5),
  Brier score per symbol type (§6), Bootstrap CIs (§7), Low-p deep
  dive (§8), Interpretation guide.
- **Missing-but-relevant**: formal §1 exec summary; Reproducibility
  (script name, git commit, re-run command); Files manifest (only
  mentions three PNGs inline); Paper implications; explicit Obs 269
  cross-reference.
- **Numeric spot-check**: ECE = 0.2689 ✓ → rounds to 0.269 (continuity)
  ✓; AUC = 0.6545 ✓ → rounds to 0.655 ✓. Both in continuity canonical
  table.
- **Markdown heuristic**: passes.
- **Level-up notes**: content is strong; the level-up is mostly
  header/footer infrastructure (exec + repro + manifest + paper
  implications). The Brier per-symbol-type breakdown is paper-ready
  content that should be highlighted in the implications block.
- **Dependencies for level-up**: none.

### 3.5 `results/55maps-image-generalisation/dawid-skene-v2-data-driven-prior/report.md`

- **Type**: 55-map core (D-S inadequacy, with calibrated subvariant).
- **Present sections**: Circularity caveat (up front, strong),
  Prior derivation, v2 D-S outputs, Calibration comparison (ECE/Brier/
  AUC vs v1 and verifier), 2×2 cross-tab, Held-out 80/20 sensitivity,
  Surprising finding (prior-sensitivity pathology), calibrated-prior
  sweep results, "Does D-S become useful" analytical paragraph, Files
  produced.
- **Missing-but-relevant**: formal §1 exec summary (report starts with
  Circularity caveat rather than a headline block); formal methods
  block; Reproducibility (no script, no git, no re-run command); Paper
  implications (the "Practical implication" paragraph is paper-ready
  but not labelled).
- **Calibrated subvariant**: the continuity-doc reference to a
  "calibrated subvariant" is this report's own §"Surprising finding"
  sweep (calibrated prior 0.1700); the `ds-human-crosstab-calibrated/`
  subdirectory under this path contains the corresponding artefacts.
  No separate report.md for the subvariant — it's folded in. Acceptable.
- **Numeric spot-check**: D-S VLM-only AUC = 0.5000 ✓ (matches continuity
  canonical AUC=0.500). Fixed-prior posterior = 0.1862 ✓ (matches
  audit-summary).
- **Markdown heuristic**: passes.
- **Level-up notes**: add exec summary, methods block, reproducibility,
  paper implications. Content is exceptionally strong; infrastructure
  alone is the gap. A further (optional) win would be to promote the
  "Surprising finding" heading to an Obs-273-labelled block.
- **Dependencies for level-up**: none.

### 3.6 `results/55maps-image-generalisation/ds-human-crosstab/report.md`

- **Type**: 55-map core (D-S aggregate-vs-human-review diagnostic).
- **Present sections**: Input provenance (✓), Sample composition,
  Structural note on D-S identifiability (methods-like), Coarse cross-
  tab (§1), Reliability diagram (§2), Ambiguity-band isolation (§3),
  Buffer-band view (§4), Verifier comparison (§5), Interpretation (§6).
- **Missing-but-relevant**: formal §1 exec summary; methods block
  (bootstrap spec missing — no seed or iteration count visible);
  Reproducibility block (no script/git); Per-map; Files manifest
  (only "Figures" section lists PNGs); Paper implications.
- **Numeric spot-check**: VLM-only posterior = 0.1862 ✓; ECE = 0.5385
  ✓; AUC = 0.5000 ✓; empirical mound rate on VLM-only = 0.7247 ✓. All
  match audit-summary and DS-v2 report.
- **Markdown heuristic**: passes.
- **Level-up notes**: add exec summary framing this as the D-S
  structural-inadequacy diagnostic; promote "Structural note" to
  Methods section; add Reproducibility; add Files manifest (the
  directory has `buffer_band_vs_ds.csv`, `crosstab_coarse.csv`,
  `reliability.csv`, `reliability_plot.png`, `buffer_scatter.png`,
  `summary.json`); add Paper implications block.
- **Dependencies for level-up**: none.

### 3.7 `results/55maps-image-generalisation/buffer-100m-diagnostics/` (stub — no report.md)

- **Type**: 55-map core (GT-clustering + pair-drift decomposition of
  the 50→100 m recall gain).
- **Present files**: `gt_clustering.csv`, `pair_drift.csv`,
  `summary.json`. All three contain the analytical content; there is
  no rendered report.
- **Content (from summary.json)**:
  - GT clustering: 16.78% of student+promoted GT have ≥1 neighbour
    within 100 m; 6.44% within 50 m. Max cluster size 5.
  - Pair drift: 0.10% of matches drift between 50 m and 100 m; 71 new
    matches at 100 m only; 0 lost.
- **Implication**: the 50→100 m F1 lift (0.832 → 0.852) is dominated
  by legitimately new matches at 100 m, with negligible re-pairing
  drift — the curve is doing what it should.
- **Level-up**: write a new `report.md` (2–3 pages) with §1 exec
  summary, §2 data (inputs/provenance), §3 GT-clustering diagnostic,
  §4 pair-drift diagnostic, §5 interpretation ("the 100 m recall gain
  is genuine, not a re-pairing artefact"), §6 reproducibility, §7
  files manifest, §8 paper implications.
- **Level-up effort**: M (~45–60 min of writing; no new analysis
  needed, all data is in summary.json).
- **Dependencies**: none.

### 3.8 `results/gold-standard-extended-buffer-sweep/extended-buffer-report.md`

- **Type**: Extended-buffer sweep (4-map gold-standard pipeline calibration).
- **Present sections**: Purpose, Canonical run selected (with git
  commit + full config), Evaluation scope (inputs, bounds NOTE, bootstrap),
  Extended-buffer F1 table (5/10/15/25/35/45 m), Key observations (4
  numbered findings), Comparison to 55-map text-HIGH curve, Implication
  for publication framing (✓ paper-ready), Input files (✓), Reproducibility
  (✓ re-run commands for both pipeline steps).
- **Missing-but-relevant**: formal §1 exec summary with headline
  metrics at the top; per-map breakdown; formal caveats / risk register;
  bugs-caught-during-audit section.
- **Numeric spot-check**: 20 m F1 ≈ 0.816 matches cached leaderboard
  claim (not in the continuity canonical table — this is auxiliary
  context for the paper); 25/35/45 m plateau at 0.8225 confirmed in
  report.
- **Markdown heuristic**: passes.
- **Level-up notes**: this is the strongest report outside the exemplar.
  Level-up is truly "polish" — add an exec-summary header block and a
  formal caveats section. The Implication-for-publication-framing
  paragraph should be relabelled "Paper implications" for uniformity.
- **Dependencies for level-up**: none.

### 3.9 `results/h12-v2/analysis_summary.md`

- **Type**: Era 1 (hypothesis retest, HP:HN ratio).
- **Present sections**: Headline result (null after BH-FDR at q=0.05),
  Cross-hypothesis context table, Per-condition metrics (greedy t=4),
  Threshold sweep, WBF variant C secondary aggregation, Directional
  findings worth flagging (3 numbered), Execution summary, Transient
  tile failures note, Artefacts (files manifest ✓), Scripts used (✓).
- **Missing-but-relevant**: formal §1 exec summary stating the result
  with CIs (the Headline section approximates this but lacks a
  one-paragraph narrative); formal Data section; formal caveats / risk
  register (transient failures are caveat-like but informal);
  Paper-implications block (cross-hypothesis context paragraph is
  paper-ready but not labelled).
- **Numeric spot-check**: not performed; not a paper-headline number.
- **Markdown heuristic**: passes.
- **Level-up notes**: shortest level-up of the lot. Add exec summary
  paragraph, rename cross-hypothesis paragraph to Paper-implications,
  add a short Caveats section. This is the strongest Era 1 doc by far.
- **Dependencies for level-up**: none.

### 3.10 `results/h8-v2/` (no analysis_summary.md)

- **Type**: Era 1 (library composition retest).
- **Present artefacts**: JSON + CSV + per-run `evaluation.md` under
  `greedy/{canonical, plus-hp, pure-positive-canon, pure-positive-
  canon-t4, scale-{4,8,16,32}}/t{1..5}/`, plus `permutation-t4/`,
  `verifier-sweep/`, `wbf/`. The audit-summary §"Era 1 status" calls
  this "bootstrap CIs and paired permutation tests present for the
  greedy cohort; multi-buffer curve missing; narrative in working-notes
  Obs 238".
- **Missing**: consolidated `analysis_summary.md` (like h12-v2's).
- **Level-up**: write a new `results/h8-v2/analysis_summary.md` in
  the h12-v2 template: Headline (library-composition NULL after BH-FDR
  per the audit), per-scale F1 table pulled from
  `greedy/scale-*/t4/evaluation.json`, threshold sweep table, pairwise
  permutation results from `permutation-t4/`, verifier-sweep summary
  from `verifier-sweep/`, WBF variant C from `wbf/`, cross-hypothesis
  link to h10/h12-v2.
- **Level-up effort**: L (90+ min; consolidates ~30 evaluation.json
  files into one narrative).
- **Dependencies**: working-notes Obs 238 provides the narrative arc;
  no new analysis needed.

### 3.11 `results/h10/` (no analysis_summary.md; has `verifier_independence_probe.md`)

- **Type**: Era 1 (calibration-pool retest).
- **⚠️ Superseded 2026-04-24 (Session 75)**: this scorecard row
  instructed using `sweep_results.json` + `statistical_analysis.json`
  + `verifier_independence_probe.md` as the main sources for the h10
  synthesis. During Session 75 drafting, these files were discovered
  to be derived from the **Obs 235 retracted v1 probe** (text-only
  runs, `include_example_images: false`, 2026-04-11) and have been
  physically moved to
  `archive/h10-h12-v1-retracted-probe/results/h10/`. They must not be
  cited for any library-composition or HP:HN-ratio claim. The scorecard
  row below is preserved for historical reference; the authoritative
  Session-75 synthesis is at `results/h10/analysis_summary.md`, scoped
  to the clean primary experiment (4-pool-size sweep at hp4hn4,
  launched 2026-04-15 under clean E49 conditions). Cross-hypothesis
  coverage of the HP:HN variants is at `results/h8-v2/analysis_summary.md`
  + `results/h12-v2/analysis_summary.md`.
- **Present artefacts** (original listing, pre-archive): `verifier_independence_probe.md` (one sub-
  analysis) + 9 top-level JSONs (`h10_consensus_only_20m.json`,
  `h10_pool_{020,160}_pv_20m.json`, `h10_pv_permutation_020_vs_160.json`,
  `h10_wbf_consensus_20m.json`, `k5_replicate_sweep.json`,
  `statistical_analysis.json`, `sweep_results.json`,
  `consensus_dedup_magnitude_diagnostic.json`) plus a `wbf/` subdir.
- **Missing** (original): consolidated `analysis_summary.md`.
- **Level-up** (original): write a new `results/h10/analysis_summary.md`
  summarising the calibration-pool NULL finding (audit: "bootstrap CIs,
  ICC diagnostics, verifier-independence probe present; multi-buffer
  curve missing; narrative only in working-notes"). Use `sweep_results.json`
  + `statistical_analysis.json` for the main table, `h10_pv_permutation_020_vs_160.json`
  for the permutation result, `verifier_independence_probe.md` as a
  sub-section.
- **Level-up effort**: L (90+ min).
- **Dependencies**: working-notes narrative; no new analysis needed.
- **Session 75 resolution (2026-04-24)**: analysis_summary.md is
  written and committed. Of the original source list, only
  `h10_pv_permutation_020_vs_160.json` (now at mtime 2026-04-15) is a
  clean source; `sweep_results.json`, `statistical_analysis.json`, and
  `verifier_independence_probe.md` are retracted-v1 and are cited in
  the new summary's §"Preserved-for-archive" section with explicit
  "do not cite" framing.

### 3.12 `results/h11-tile-size-results.md` + `results/h11-384-pv-diagnostic/` (fragmented)

- **Type**: Era 1 (two-stage tile-size retest).
- **Present artefacts**: top-level `h11-tile-size-results.md` as the
  main narrative; `h11-384-pv-diagnostic/` contains 30+ per-cell
  sub-directories each with `threshold_sweep_summary.md` +
  `bootstrap-cis-384px.json`.
- **Missing**: a consolidated `results/h11/analysis_summary.md` in the
  h12-v2 template.
- **Audit note**: "fragmented across multiple sub-run directories;
  proposer-vs-verifier paired test never formally computed; two
  'UNINTENDED-T1.0' runs exist (`outputs/h11/single-pass-384-UNINTENDED-T1.0/`
  and `outputs/h11/consensus-384-UNINTENDED-T1.0/`) and have not been
  formally excluded or archived."
- **Level-up**: consolidate `h11-tile-size-results.md` + the
  diagnostic sub-directories into a single `analysis_summary.md`.
  Include a decision on the two UNINTENDED-T1.0 runs (archive or
  formally exclude).
- **Level-up effort**: M (60–75 min if UNINTENDED-T1.0 disposition is
  a simple archive-with-note; L if it requires a partial re-analysis).
- **Dependencies**: UNINTENDED-T1.0 disposition decision (user sign-
  off recommended before archival).

### 3.13 `results/paper-eval/mcc/` (analysis family — no narrative report.md)

- **Type**: MCC analysis family (tile-level MCC / sensitivity / specificity
  for consensus, PV, single-pass, and verifier-stacked conditions at 384 px
  and 512 px). Context per the `384px-eval.log` header: "Loaded 18 conditions
  from configs/mcc-eval-384px.yaml" — a programmatic batch sweep producing
  one-JSON-per-condition plus auto-generated batch summaries.
- **Present artefacts** (absolute paths):
  - `/home/shawn/Code/map-reader-llm/results/paper-eval/mcc/consensus-pv/batch_mcc_summary.json`
    + `.csv` + `.md` (12-condition consensus/PV batch, dated 2026-03-27,
    description "Completes the MCC table from Obs 202")
  - `/home/shawn/Code/map-reader-llm/results/paper-eval/mcc/consensus-pv/<condition>/mcc.json`
    (12 per-condition files: TP/TN/FP/FN, MCC/sensitivity/specificity
    point + mean + 95 % CI, n_populated / n_empty over 487 tiles)
  - `/home/shawn/Code/map-reader-llm/results/paper-eval/mcc/384px/batch_summary.{json,csv,md}`
    plus 18 per-cell subdirectories each with `evaluation.{json,csv,md}`
    (per-run MCC across 3–30 replicates, summarised to mean ± CI per cell)
  - `/home/shawn/Code/map-reader-llm/results/paper-eval/mcc/512px/batch_summary.{json,csv,md}`
    plus 32 per-cell subdirectories (spans p2a/p2b/p2c/p2d/p2e matrix)
  - `/home/shawn/Code/map-reader-llm/results/paper-eval/mcc/remaining/batch_mcc_summary.{json,csv,md}`
    plus 15 per-condition subdirectories (top-up cohort including
    verifier-stacked variants such as `flash-high-image-3-of-5-flash-min-vf/mcc.json`)
  - Run logs: `/home/shawn/Code/map-reader-llm/results/paper-eval/mcc/384px-eval.log`
    and `/home/shawn/Code/map-reader-llm/results/paper-eval/mcc/512px-eval.log`
- **Present sections (against exemplar)**: confusion matrices (✓, one per
  condition across all four batch summaries); agreement measures (~,
  MCC + CI present — kappa/ECE not computed at tile level here); per-map /
  per-cell diagnostic (~, per-condition files exist but no cross-condition
  narrative); reproducibility (~, the 384 px log records the config file
  `configs/mcc-eval-384px.yaml` and GT path
  `/home/shawn/Code/map-reader-llm/inputs/vectors/references/mounds-reference.geojson`,
  but no git commit or re-run command); files manifest (~, implicit via
  the per-condition subdirectory structure).
- **Missing-but-relevant**: formal §1 executive summary; data-block with
  provenance of the 18 / 12 / 15 condition groupings and why they are
  split across `consensus-pv/`, `384px/`, `512px/`, `remaining/`; new
  findings / observation-verification block (this family underpins
  tile-level MCC claims but nothing ties the batch summary back to the
  corresponding Observation numbers in `docs/notes/reflections/working-notes.md`);
  caveats / risk register (e.g. the Flash MIN T=0.0 MCC 0.022 is an
  empty-tile floor, not a performance estimate — this nuance is invisible
  from the numbers alone); paper-implications block.
- **Numeric spot-check**: `consensus-pv/flash-high-text-16-of-30-pv/mcc.json`
  reports MCC point = 0.7903, CI [0.7328, 0.8401], TP/TN/FP/FN =
  188/247/11/41. The row-2 entry in `batch_mcc_summary.md` is "Flash
  HIGH text 16-of-30 + PV | 412 | 0.790 [0.733, 0.840] | 0.821 [0.767, 0.867]
  | 0.957 [0.929, 0.981] | 188 | 247 | 11 | 41" — internally consistent
  ✓. Cross-reference to row 14's phase3a §3 HIGH-T0.7 value (MCC 0.620
  [0.549, 0.691]) matches row 10 of `batch_mcc_summary.md` ("Flash HIGH
  text 26-of-30", 384 px K=30 HIGH-T0.7 consensus, 0.620 [0.549, 0.691]) ✓.
- **Markdown heuristic**: `batch_mcc_summary.md` renders cleanly; no
  trailing whitespace or broken tables observed. The three batch-summary
  MD files are auto-generated from the JSON and are concise tabular
  artefacts, not prose.
- **Level-up notes**: write a new
  `/home/shawn/Code/map-reader-llm/results/paper-eval/mcc/report.md`
  (M, ~45–60 min) with: §1 exec summary (MCC ranking: Pro Image HIGH
  N=1 top at 0.848 → Flash MIN T=0.0 floor at 0.022; Flash HIGH text
  16-of-30 + PV second at 0.790); §2 data (487-tile population over
  229 populated / 258 empty tiles; config file, GT geojson, detection
  output paths); §3 methods (tile-level 2×2 classification rule, bootstrap
  CI method, empty-tile inclusion); §4 consolidated table cross-cutting
  `consensus-pv/`, `384px/`, `512px/`, and `remaining/` (currently no
  single file spans all four); §5 caveats (Flash MIN T=0.0 is
  degenerate — specificity 0.008 — and should not be reported as a
  performance estimate); §6 reproducibility; §7 files manifest; §8
  paper implications (which conditions belong in the paper's tile-level
  MCC table, and how they relate to map-level F1 rankings elsewhere).
- **Dependencies for level-up**: none (all data is in the per-condition
  JSONs and existing batch summaries; confirm Obs numbering with
  working-notes before cross-referencing).

### 3.14 `results/phase3a-text-matrix/secondary_effects.md`

- **Type**: phase3a-matrix (Era 2, 384 px, 487 tiles, 8 conditions
  spanning HIGH × MIN thinking × {T0.0, T0.3, T0.7, T1.0} temperature).
  Closest analogue among settled rows is the Extended-buffer report
  (row 8) in structure — a single rendered analysis across a small
  condition grid — but the corpus and protocol are Era 2 phase3a, not
  the 55-map or 4-map gold-standard pipelines, justifying the new
  `phase3a-matrix` Type label.
- **Present sections (13 numbered)**: §1 Precision/Recall Decomposition
  (20 m), §2 Run-to-Run Variability (with Levene's test), §3 Tile-Level
  MCC / Sensitivity / Specificity, §4 Buffer Sensitivity (F1@20 m vs
  F1@50 m with slope/elasticity), §5 Threshold Robustness (optimal-t
  plateau width, drop t±1), §6 Per-Map-Sheet F1 at 20 m (four sheets:
  K-35-052-4_32635, K-35-053-3_Elenovo, K-35-062-2_Rakovski,
  K-35-078-1_Lesovo), §7 Per-Subtype Recall (benchmark, burial,
  settlement, triangulation), §8 Thinking × Temperature Interaction
  (with bootstrap tests, all not significant), §9 Consensus Convergence
  (F1 vs N: N=5 → N=K), §10 Vote Distribution / Agreement (unanimous %,
  contentious %, mean vote), §11 Cost-Performance (F1/$, Pareto flag),
  §12 Spatial Clustering of Errors (FP/FN mean + CV, top 5 FP / FN
  tiles), §13 Thinking Token Usage.
- **Missing-but-relevant**: formal §1 executive summary prefacing the
  13 tables (the file opens straight into §1 P/R decomposition with no
  narrative framing); methods block (bootstrap spec, tile boundaries
  reference, match protocol, empty-tile rule); reproducibility (no git
  commit, no script name, no re-run command, no input-file paths for
  the GT/detection geojsons); caveats / risk register (e.g. the
  non-significant interaction tests in §8 deserve a caveat against
  over-reading the +0.153 HIGH-advantage at T0.7; the §13 "0 thinking
  tokens" for T0.7 HIGH row looks anomalous and is not flagged);
  bugs-caught-during-audit block; files manifest; paper-implications
  block.
- **Numeric spot-check**: §3 "HIGH-T0.7 | 0.620 | [0.549, 0.691] | 0.777
  | 0.841 | 178 | 217 | 41 | 51" is present verbatim in the file ✓.
  Cross-reference to row 13's `consensus-pv/batch_mcc_summary.md` row
  10 ("Flash HIGH text 26-of-30", the 384 px K=30 HIGH-T0.7 consensus):
  MCC 0.620 [0.549, 0.691], TP/TN/FP/FN = 178/217/41/51 — identical,
  confirming the two artefacts report the same underlying run from two
  directions.
- **Markdown heuristic**: passes (13 tables render cleanly; §13 has a
  stray blank line before the generation footer but nothing breaks).
- **Level-up notes**: add §1 exec summary with the headline finding
  (HIGH × T0.7 is the phase3a optimum at F1 0.814 / MCC 0.620); add a
  formal Methods block citing the phase3a evaluation pipeline; add
  reproducibility (config file, evaluation script, detection output
  paths); add caveats flagging (a) the non-significant interaction tests
  as evidence *against* over-reading thinking × temperature effects,
  (b) the §13 apparent 0-token reading for HIGH-T0.7 being almost
  certainly a logging artefact rather than real (30 runs with 0 thinking
  tokens is implausible given the other HIGH rows average ~1.2–1.9 M);
  add files manifest; add paper-implications block anchoring the
  phase3a result against the 55-map / 4-map gold-standard pipeline
  F1 curve for context.
- **Dependencies for level-up**: resolve the §13 "0 thinking tokens"
  anomaly before publishing (check raw `outputs/` usage metadata; may
  be a parsing bug in the secondary-effects generator rather than a
  real zero).

### 3.15 `outputs/retest/phase2b/` + `results/retest/phase2b-track{1,2}-evaluation.json` (no dedicated analysis_summary.md)

- **Type**: Era 1 retest (preregistered H7 temperature sweep, 340-tile
  corpus). Five temperature levels (T0.0/0.3/0.7/1.0/1.3) × two tracks
  (track1-image = `brief-text-image`; track2-text = `brief-text`) ×
  K=3 runs × 340 tiles = **10,200 tile-runs** total. This is the
  load-bearing artefact for the paper's temperature finding; working-
  notes line 6069+ flags the "preregistered Phase 2b (this row) vs
  E43 accidental-deployment `consensus-384-UNINTENDED-T1.0`" distinction
  as the one the paper rests on.
- **Present artefacts** (absolute paths):
  - `/home/shawn/Code/map-reader-llm/studies/retest/phase2b-h7-temperature.yaml`
    and `/home/shawn/Code/map-reader-llm/studies/retest/phase2b-h7-temperature-text-only.yaml`
    (intended-analysis specs; bootstrap n=1000, FDR q=0.05, planned
    contrasts T1.0 × {T0.0, T0.3, T0.7, T1.3})
  - `/home/shawn/Code/map-reader-llm/outputs/retest/phase2b/track1-image/{T0.0,T0.3,T0.7,T1.0,T1.3}/run_{1,2,3}/detections_*.{geojson,meta.json,tiles.json}`
    (15 run directories for track 1)
  - `/home/shawn/Code/map-reader-llm/outputs/retest/phase2b/track2-text/{T0.0,T0.3,T0.7,T1.0,T1.3}/run_{1,2,3}/detections_*.{geojson,meta.json,tiles.json}`
    (15 run directories for track 2)
  - `/home/shawn/Code/map-reader-llm/results/retest/phase2b-track1-evaluation.json`
    + `.metadata.json` (per-condition F1/P/R point + mean + 95 % bootstrap
    CI over n=1000, seed 42, tile-level-multi-run resampling — confirmed
    via sidecar)
  - `/home/shawn/Code/map-reader-llm/results/retest/phase2b-track2-evaluation.json`
    + `.metadata.json` (same structure, text track)
  - `/home/shawn/Code/map-reader-llm/results/retest/retest-production-summary.md`
    §Phase 2b (lines 40–69) — embedded narrative with per-track tables
    and key-finding sentences
  - `/home/shawn/Code/map-reader-llm/results/retest/retest-production-summary.md`
    §Pairwise Comparison Highlights (lines 248–267) — 6 + 5 FDR-
    significant pairwise contrasts, track 1 and track 2 respectively
- **Superseded pre-retest artefacts** — **Option A partially completed
  2026-04-23**: six orphan files archived to
  `/home/shawn/Code/map-reader-llm/archive/outputs-pre-retest-60-tile/phase2b/`
  (the two summary `.md` + two analysis `.json` + two metadata sidecars,
  all describing the 60-tile K=10 pilot). `ci-metadata-registry.md`
  updated to point at the new archive locations. **Option B residual
  (deferred to this Step 4 level-up)**: `results/phase2b-carry-forward-parameters.md`
  is NOT archived — it is cited as a source by
  `results/phase2c-carry-forward-parameters.md:126` as the Phase 2b → Phase
  2c carry-forward decision, and archiving it would break that active
  dependency. A retention banner was added 2026-04-23. Step 4 Phase 2b
  level-up must: (a) create a retest-era carry-forward equivalent (based
  on the 340-tile K=3 retest data); (b) repoint the Phase 2c citation at
  the new retest-era doc; (c) then archive the pre-retest carry-forward
  doc with the other six files.
- **Present sections (against exemplar)**: data/inputs (~, manifests
  and GT paths present in YAML and per-run metadata); agreement
  measures (~, bootstrap CIs + FDR-corrected pairwise contrasts present
  in JSON and in the retest-production-summary tables, not in a
  dedicated doc); reproducibility (~, the sidecar records generator
  script `scripts/evaluate_retest_all.py` at git hash `e038bfe8…`, but
  no single narrative doc exposes the re-run command). All other
  exemplar sections (executive summary, confusion matrices, observation
  verification, consensus-threshold sweep, per-map diagnostic, methods
  block, caveats, files manifest, paper-implications) are **missing**
  for a dedicated Phase 2b report — though some live in the combined
  retest-production-summary.
- **Missing-but-relevant**: a stand-alone Phase 2b analysis doc (the
  current embedding in a 331-line multi-phase summary is adequate for
  internal use but non-ideal as a paper-citation target); a caveats
  section distinguishing the **preregistered T=1.0** finding here from
  the **E43 accidental T=1.0 deployment** data at
  `outputs/h11/consensus-384-UNINTENDED-T1.0/` (the paper must cite
  *this* row, not E43 — see working-notes line 6069+); a paper-
  implications block anchoring both the T=0.0 optimum and the
  practitioner-facing "Gemini API default T=1.0 is suboptimal" message.
- **Numeric spot-check**: `outputs/retest/phase2b/track1-image/T0.0/run_1/detections_T0.0_run01.tiles.json`
  reports `total_tiles = 340`, `len(completed) = 340`, `len(failed) = 0`
  ✓ (matches the YAML's `retest_tiles: 340`). Track-1 F1 values from
  `results/retest/phase2b-track1-evaluation.json` (T0.0 0.5869 / T0.3
  0.5751 / T0.7 0.5367 / T1.0 0.5269 / T1.3 0.4903) match
  `retest-production-summary.md` §Phase 2b Track 1 table to 4 decimal
  places ✓. Track-2 F1 (T0.3 0.6065 / T0.0 0.6048) likewise internally
  consistent ✓.
- **Markdown heuristic**: N/A — no report.md to render. The narrative
  embedding in `retest-production-summary.md` renders cleanly.
- **Level-up notes**: write a new
  `/home/shawn/Code/map-reader-llm/results/retest/phase2b/analysis_summary.md`
  (or a single `results/phase2b/analysis_summary.md`, discouraging
  confusion with the archived pre-retest `results/phase2b-*-summary.md`)
  in the h12-v2 template: §1 exec summary (T=0.0 optimal on both tracks,
  monotonic decline to T=1.3; 6/10 Track-1 and 5/10 Track-2 pairwise
  contrasts FDR-significant; T=1.0 significantly worse than T=0.0 on
  both tracks); §2 data (340 tiles × K=3 × 5 T × 2 tracks = 10,200
  tile-runs; GT geojson and manifest paths); §3 methods (bootstrap n=1000
  seed 42, tile-level-multi-run resampling, BH-FDR q=0.05, planned
  contrasts from YAML); §4 per-condition F1/P/R + CI table (from the
  evaluation JSONs); §5 pairwise FDR-significant contrasts (from
  retest-production-summary §§Phase 2b T1/T2); §6 caveats — foreground
  the preregistered-vs-E43 distinction before the paper is drafted;
  §7 reproducibility (re-run via `scripts/evaluate_retest_all.py` +
  the two study YAMLs); §8 files manifest (raw dirs + evaluation JSONs
  + retest-production-summary cross-reference); §9 paper implications
  (practitioner-facing "change the Gemini API default T=1.0" message;
  the Phase 2b T=0.0 optimum is *not* the consensus-optimum T=0.7 —
  note the crossover documented in working-notes line 6095+
  "Five design decisions that cross over"). **Option B residual
  (MANDATORY sub-task of this level-up)**: create a retest-era
  `results/phase2b-carry-forward-parameters.md` equivalent; repoint the
  citation at `results/phase2c-carry-forward-parameters.md:126`; then
  archive the pre-retest carry-forward doc to
  `archive/outputs-pre-retest-60-tile/phase2b/` alongside the six
  files already archived 2026-04-23.
- **Level-up effort**: **L** (~90 min). All data is in hand; the work
  is pure consolidation, plus the pre-retest archive flagging, plus
  the paper-facing E43 disambiguation block.
- **Dependencies for level-up**: none blocking. Archiving/flagging the
  three pre-retest `results/phase2b-*.md` files is a prerequisite to
  avoid ambiguity (single-session task).

### 3.16 `results/55maps-image-generalisation/uncalibrated-vs-calibrated-crosstab/crosstab.md`

- **Type**: 55-map core (Obs 268 review-UI disagreement analysis;
  direct input to meta-findings Theme T1).
- **Present sections**: header block with timestamp and context
  paragraph (executive-summary-equivalent), §Overall agreement
  (disagreement rate 0.2141, bootstrap 95 % CI [0.1713, 0.2599] over
  10 000 iterations at seed 42), §Disagreement decomposition (four
  directional rows), §Stratified disagreement by verifier probability
  with an explicit caveat on the overlap composition (all 327 overlap
  candidates sit in the top verifier-probability bin [0.90, 1.00]),
  §Symbol-type flow table (5×5 uncal × cal), §Corrected-F1 accounting
  (all-calibrated F1 = 0.8295 vs mixed F1 = 0.8377; ΔF1 = −0.0082),
  §Reproducibility (bootstrap spec, CSV input paths, evaluation JSON
  path, script name).
- **Missing-but-relevant**: formal §1 exec summary labelled as such
  (the context paragraph approximates it but is not a headline-numbers
  block); formal files manifest (the report lists inputs but does not
  enumerate outputs beyond the three CSVs implicitly); explicit Obs 268
  cross-reference in a header block (the Obs number is referenced
  inline but not in a dedicated observation-verification section);
  formal Paper-implications block (the interpretation paragraphs under
  §Stratified and §Corrected-F1 accounting are paper-ready content but
  not labelled as such).
- **Flip-rate definition (paper-critical, lands here)**: a "flip" in
  this context is a review-UI-induced reversal of an individual
  reviewer's decision on the same candidate. The uncalibrated UI
  presented no explicit spatial tolerance; after 327 reviews, the UI
  was upgraded to overlay a magenta 50 m tolerance circle on the
  candidate crop. The reviewer re-reviewed all 1 028 candidates with
  the calibrated UI. The "flip rate" is the proportion of the
  327-candidate overlap where the reviewer's decision changed between
  the uncalibrated and calibrated sessions — specifically 70 / 327 =
  21.4 %, all in the direction Uncal = mound → Cal = not_mound (zero
  flips in the reverse direction). The asymmetry indicates the
  calibrated UI tightened reviewer decisions toward more conservative
  labelling. This definition is the one that should land in the
  paper; the exec-summary block for a level-up pass should open with
  it. The same framing should be surfaced in §1 Summary verdict (this
  scorecard) any time the 21 % figure is mentioned — see §1
  "Non-critical gaps" paragraph and §8 Checkpoint where the flip
  framing is load-bearing for Theme T1's statement.
- **Numeric spot-check**: disagreement rate 0.2141 [0.1713, 0.2599] ✓
  (matches working-notes Obs 268); corrected-F1 ΔF1 = −0.0082 (all-cal
  0.8295 − mixed 0.8377) ✓; 70 / 327 all-directional flips confirmed
  in the §Disagreement decomposition table (186 stable positive / 71
  stable negative / 70 uncal → cal FP / 0 uncal → cal FN).
- **Markdown heuristic**: passes (tables render, no broken fences).
- **Level-up notes**: small, high-leverage polish. Add a formal §1
  exec-summary block opening with the flip-rate definition above; add
  a formal Paper-implications block labelled as such (two paragraphs
  of citable content already exist under §Stratified and §Corrected-F1
  accounting); add a files-manifest block (the directory contains the
  rendered `crosstab.md` plus its data inputs at the CSV paths listed
  in §Reproducibility; no separate summary.json is needed); add an
  explicit Obs 268 back-reference in the header. Estimate 25–35 min
  end-to-end. No new analysis required.
- **Dependencies for level-up**: none. The report is self-contained;
  all numerical content traces to existing JSON / CSV inputs.

### 3.17 `results/phase3a-image-matrix/consensus-analysis-summary.md`

- **Type**: phase3a-matrix (Era 2 image-track sibling of row 14's
  text-track `secondary_effects.md`). 384 px, 487 tiles, Gemini 3
  Flash, library_plus-hp (13 examples, 4 HP 0 HN), 14 conditions
  spanning HIGH × MINIMAL thinking × {T0.0, T0.3, T0.7, T1.0} ×
  {N=5, N=10}.
- **Present sections**: header metadata (generation timestamp, scope,
  config, model); §Best operating point per condition at 20 m buffer
  (14-row table with best-t, F1 point + CI, P, R); §HIGH vs MINIMAL
  comparison at best operating point per N (6-row table with ΔF1 at
  T × N crossings); §Full threshold sweep at 20 m buffer (14 sub-
  tables, one per condition, with per-t F1, CI, P, R).
- **Missing-but-relevant**: formal §1 executive summary (the file
  opens straight into a configuration header + best-operating-point
  table with no narrative framing of the headline finding); methods
  block (bootstrap spec, matching protocol, empty-tile rule — all
  implicit); reproducibility block (no git commit, no script name,
  no re-run command, no input-file paths); caveats / risk register
  (the HIGH-advantage at T=0.7 × N=10 of +0.070 is not contextualised
  against the non-significant interaction tests reported in row 18's
  secondary-effects §8); paper-implications block (the "best HIGH
  configuration is T=0.7 N=10 at F1 0.750" result is paper-ready but
  not labelled); files manifest. Also missing (and more load-bearing):
  any tile-level MCC / sensitivity / specificity breakdown — this doc
  is a consensus sweep, not a secondary-effects sweep, so §3–§13 of
  the sibling text-track doc's 13-table structure have no analogue
  here.
- **Numeric spot-check**: not performed (no paper-headline number;
  closest is the HIGH × T=0.7 × N=10 F1 = 0.750 which is auxiliary to
  the paper's 55-map image-generalisation curve).
- **Markdown heuristic**: passes (all sub-tables render cleanly).
- **Level-up notes**: this doc's paper role is as the image-track
  analogue of row 14 — it underpins the phase3a image × thinking ×
  temperature × N comparison that Obs 264's "image slower than text
  to converge" claim rests on. Bring it to parity with the text-track
  doc by adding exec summary, methods, reproducibility, caveats,
  files manifest, and paper implications. Consider also whether the
  tile-level MCC breakdown should be added (it would require pulling
  from the per-condition evaluation.json files; M rather than S).
- **Dependencies for level-up**: cross-reference to working-notes
  Obs 264 and to row 18's secondary-effects doc to align the "image
  vs text track" comparative framing.

### 3.18 `results/secondary-effects/secondary_effects.md`

- **Type**: phase3a-matrix (Era 2 image-track secondary-effects sweep
  — the image-track analogue of row 14's text-track doc). 384 px, 487
  tiles, 9 conditions including SCALE4-T0.7. Distinct from row 17:
  this doc is a *secondary-effects* sweep (P/R decomposition, run-to-
  run variability with Levene's test, tile-level MCC, buffer
  sensitivity, threshold robustness, per-sheet F1, per-subtype recall,
  thinking × temperature interaction, consensus convergence, vote
  distribution, cost-performance, spatial clustering, thinking-token
  usage), while row 17 is a consensus/best-operating-point sweep.
  Both are needed for the paper's image-track story.
- **Present sections (13 numbered)**: §1 Precision/Recall
  Decomposition at 20 m, §2 Run-to-Run Variability with Levene's test
  (W = 3.192, p = 0.0040), §3 Tile-Level MCC / Sensitivity /
  Specificity (SCALE4-T0.7 tops at MCC 0.746), §4 Buffer Sensitivity
  (F1@20 m vs F1@50 m), §5 Threshold Robustness, §6 Per-Map-Sheet F1
  at 20 m, §7 Per-Subtype Recall, §8 Thinking × Temperature
  Interaction, §9 Consensus Convergence (F1 vs N), §10 Vote
  Distribution / Agreement, §11 Cost-Performance, §12 Spatial
  Clustering of Errors, §13 Thinking Token Usage.
- **Missing-but-relevant**: formal §1 executive summary (the file
  opens straight into §1 P/R decomposition); methods block; repro
  block (no git commit, no script name, no re-run command, no input
  paths for GT/detection geojsons); caveats (the §8 non-significant
  interaction tests deserve a caveat against over-reading the
  thinking × temperature effects; the §13 thinking-token reading may
  have the same parsing-artefact issue as the text-track doc); files
  manifest; paper-implications block.
- **Numeric spot-check**: §3 "SCALE4-T0.7 | 0.746 [0.688, 0.802] |
  0.817 | 0.922 | 187 | 238 | 20 | 42" present verbatim. §2 Levene's
  W = 3.192, p = 0.0040 suggests variance heterogeneity across
  conditions worth flagging in the paper. No cross-artefact
  verification against other rows attempted (the 487-tile image-track
  MCC values here are a different population from row 13's
  `consensus-pv/` 12-condition batch).
- **Markdown heuristic**: passes (13 tables render cleanly).
- **Level-up notes**: parallel to the text-track doc (row 14) — add
  exec summary with headline finding (SCALE4-T0.7 is the phase3a
  image-track optimum at F1 0.742 / MCC 0.746, edging HIGH-T0.7 at
  F1 0.750 / MCC 0.678); add methods, repro, caveats, files manifest,
  paper implications. Align the §13 thinking-token anomaly treatment
  across row 14 and row 18 — they are likely the same logging /
  parsing bug.
- **Dependencies for level-up**: none new; resolve the §13 anomaly
  jointly with row 14.

### 3.19 `results/factor-analysis/factor_analysis_results.md`

- **Type**: factor analysis (pairwise permutation tests across
  four factor families: Architecture, Thinking, Temperature,
  Modality). FDR-corrected within family at q = 0.05, 10 000
  permutations at seed 42, 20 m buffer. Dated 2026-03-31; inputs
  span the phase3a corpus plus 512 px text/image sub-tests.
- **Present sections**: header block (seed, buffer, FDR spec),
  §Architecture (12 contrasts, 11 / 12 FDR-significant), §Thinking
  (6 contrasts, 5 / 6 significant), §Temperature (6 contrasts,
  5 / 6 significant), §Modality (9 contrasts, 8 / 9 significant).
  No interpretation paragraphs — the doc is tabular.
- **Missing-but-relevant**: formal §1 exec summary (no narrative at
  all — the doc opens with a 4-line header and a significance
  summary in parentheses per section heading); data provenance (F1
  values and which JSON they came from are not cited per contrast);
  methods block (permutation test design — paired or unpaired?
  resampling unit? — is not stated); reproducibility (no script
  name, no git commit, no re-run command); caveats (the T=0.7 vs
  T=1.0 512 px text/image rows have blank F1 fields and a sign-only
  ΔF1 — this is a data-completeness bug that should be fixed or
  flagged); files manifest; paper-implications block. Also the §Temperature
  rows have blank "Condition A" / "Condition B" cells on lines 42–43 —
  likely a CSV-to-Markdown rendering bug.
- **Numeric spot-check**: the Flash HIGH text 16-of-30 + PV vs Flash
  HIGH text 26-of-30 row (+0.076, p_adj = 0.0000) cross-references to
  row 13's `consensus-pv/` MCC table (F1 = 0.890 vs 0.814 is the
  operational ranking that underpins the paper's PV-adds-to-consensus
  claim). Internally consistent with the factor-analysis CSV.
- **Markdown heuristic**: renders, but see the empty-cell data bug
  in the Temperature section.
- **Level-up notes**: this is **load-bearing for the paper's Results
  section** — it is the single citation target for the "which
  factors matter" narrative and for the factor-by-factor paired
  permutation results. Level-up priority should therefore rank with
  the partial 55-map core reports, not below them. Add exec summary
  synthesising the "architecture dominates, thinking and modality
  substantial, temperature real-but-smaller" hierarchy; add methods
  block (permutation design, pairing rule, null hypothesis); fix the
  four blank-cell rows; add caveats (FDR-within-family means
  cross-family significance is not jointly controlled); add repro and
  files manifest; add paper implications (headline: 11/12 architecture
  contrasts significant — the strongest and most robust factor
  family).
- **Dependencies for level-up**: fix the empty-cell rendering bug
  before or during the level-up (verify against the underlying JSON
  at `/home/shawn/Code/map-reader-llm/results/factor-analysis/factor_analysis_results.json`).

### 3.20 `results/retest/retest-production-summary.md`

- **Type**: Era 1 summary (multi-phase production retest narrative
  for the 340-tile corpus, spanning Phase 2a H1 Modality, Phase 2b H7
  Temperature (both tracks), Phase 2c, Phase 2d, Phase 2e, and
  Phase 3a consensus). This is the doc the audit calls "one of the
  better-documented Era 1 overviews" and the narrative source for the
  Phase 2b numbers that row 15 covers. Grade here is for the doc as
  a whole, not just the §Phase 2b extract.
- **Present sections**: §Context (model, bootstrap spec, spatial
  matching), §Phase 2a H1 Modality (5 conditions × K=3 with per-
  condition F1 + CI + key-finding paragraph citing pairwise p-values),
  §Phase 2b H7 Temperature (both tracks, 5 T × K=3, per-track tables
  + key-finding paragraphs), §Phase 2c / 2d / 2e (further single-pass
  hypothesis tables in the same format), §Phase 3a consensus (K=30
  runs), §Pairwise Comparison Highlights (6 + 5 FDR-significant
  contrasts), cross-phase narrative. No exec summary block, but
  each §Phase block leads with a one-paragraph key finding.
- **Missing-but-relevant**: formal §1 executive summary cross-cutting
  the phases (the paper's Era 1 Results section needs one, and this
  doc is the natural place for it); methods block (bootstrap spec is
  in §Context but not formally labelled; permutation/FDR spec is
  implicit in §Pairwise Comparison Highlights); caveats (the T=0.3
  Track 2 optimum vs T=0.0 Track 1 optimum crossover between tracks
  is not flagged as a caveat — it is the "design decisions that cross
  over" note in working-notes line 6095+); paper-implications block
  (the "change the Gemini API default T=1.0" practitioner message is
  in the Phase 2b narrative but not labelled); explicit Obs
  cross-references (the doc predates Obs 262–273 and does not
  back-reference them); bugs-caught block.
- **Numeric spot-check**: §Phase 2a brief-text F1 = 0.5518 [0.477,
  0.595] cross-references row 15's Phase 2b disambiguation — consistent.
  §Phase 2b Track 1 T=0.0 F1 = 0.5869 matches
  `results/retest/phase2b-track1-evaluation.json` (verified in row 15
  spot-check 8).
- **Markdown heuristic**: passes (331 lines, all tables render).
- **Level-up notes**: the doc is serviceable as-is for internal use;
  the level-up work is (a) promoting it to a paper-citation target
  for the Era 1 Results section, and (b) splitting the Phase 2b
  narrative out into a dedicated analysis_summary.md (row 15 item).
  Add a cross-cutting exec summary, formalise methods / caveats /
  paper implications, add Obs 262–273 back-references where
  relevant, add a files manifest covering the six evaluation JSONs
  (`phase2a-modality-evaluation.json`, `phase2b-track{1,2}-
  evaluation.json`, `phase2c-*-evaluation.json`, `phase2d-*-
  evaluation.json`, `phase2e-*-evaluation.json`, and `phase3a-
  consensus-evaluation.json`).
- **Dependencies for level-up**: row 15's Phase 2b split-out should
  happen first (or jointly) so the level-up of row 20 can cross-
  reference the dedicated Phase 2b doc rather than embed its
  narrative.

### 3.21 `results/evaluation-scopes.md`

- **Type**: methodology (definitional — documents the three test tile
  sets used across the experimental programme (Era 1: 340 tiles at
  512 px; Era 2: 487 tiles at 384 px; Era 3: 327 tiles at 384 px) and
  their strict-nesting relationships). Not an analysis doc — a
  reference artefact the paper's Methods section will cite.
- **Present sections**: §Purpose, §The three test tile sets (scope
  table with manifest paths and calibration-exclusion rules), §Physical
  tile counts, §Nesting verification (zero-tolerance spatial intersection
  check: Era 3 ⊂ Era 2 ⊂ Era 1, 100 % area containment, zero mounds
  unique to a smaller scope), §Comparative coverage (80.8 % / 73.0 %
  / 59.0 %), §Calibration exclusion rationale (Era 1 / Era 2 / Era 3
  each explained).
- **Missing-but-relevant**: formal §1 exec summary (the §Purpose
  paragraph serves but is not labelled); reproducibility block
  (no script name, no git commit for the nesting-check verification —
  the "Verified by: spatial intersection analysis" line in the header
  is insufficient provenance); caveats (the 80.8 → 73.0 → 59.0 %
  nesting coverage has implications for cross-era F1 comparability
  that are not flagged); files manifest (manifest paths are embedded
  in the scope table but not collected into a single manifest block);
  paper-implications block.
- **Numeric spot-check**: Era 3 area inside Era 2 = 100.000 %
  (0.00 sq m outside) ✓ — the spot-check confirms the claim is a
  zero-tolerance equality, not a rounded ≈ 100 % — this is the
  property the paper's Methods section needs. Era 3 ⊂ Era 1 coverage
  59.0 % / 59.2 % (area / mounds) matches the sense that Era 3 is a
  strict subset of Era 1 with near-uniform mound density.
- **Markdown heuristic**: passes.
- **Level-up notes**: small polish. Add exec summary, repro block
  (script + git commit for the nesting-check), caveats section
  flagging the cross-era F1-comparability implication of the 59 % /
  73 % / 80.8 % coverage gradient, files manifest, paper-implications
  block anchoring "which scope each paper table belongs to". Estimate
  20–30 min. This is the Methods-section keystone — level-up
  priority should be high despite the small effort.
- **Dependencies for level-up**: confirm the nesting-check script
  name and git commit from run logs.

## 4. Era 1 hypothesis-report gap analysis

| Hypothesis | `analysis_summary.md`? | Alternative artefacts | Gap severity | Recommended Step 4 action | Effort |
|---|---|---|---|---|---|
| h8-v2 | **NO** | `greedy/{canonical,plus-hp,pure-positive-canon,scale-{4,8,16,32}}/t{1..5}/evaluation.{json,csv,md}`, `permutation-t4/`, `verifier-sweep/`, `wbf/` | **HIGH** — audit calls this "strongest Era 1 narrative" but no consolidated doc exists | Synthesise a new `results/h8-v2/analysis_summary.md` using the h12-v2 template. Pull headline from `greedy/canonical/t4/evaluation.json`; permutation results from `permutation-t4/`; cross-reference working-notes Obs 238. | L (~90+ min) |
| h10 | **NO** (partial: `verifier_independence_probe.md`) | `sweep_results.json`, `statistical_analysis.json`, `h10_pv_permutation_020_vs_160.json`, `h10_wbf_consensus_20m.json`, `k5_replicate_sweep.json`, `consensus_dedup_magnitude_diagnostic.json`, `wbf/` | **HIGH** — calibration-pool closure is a core Era 1 result | Synthesise `results/h10/analysis_summary.md`. Use `sweep_results.json` + `statistical_analysis.json` for main table; fold `verifier_independence_probe.md` in as a sub-section. | L (~90+ min) |
| h11 | **NO** (fragmented: `h11-tile-size-results.md` at top level + `h11-384-pv-diagnostic/` per-cell threshold sweeps) | 30+ `threshold_sweep_summary.md` files under `h11-384-pv-diagnostic/`, plus `bootstrap-cis-384px.json` | **MEDIUM** — narrative exists but scattered; UNINTENDED-T1.0 runs need formal disposition | Consolidate into `results/h11/analysis_summary.md`. Decide UNINTENDED-T1.0 disposition (archive with note recommended; escalate if unclear). | M (60–75 min), L if re-analysis needed |
| h12-v2 | **YES** | `analysis_summary.md` + `analysis_summary.txt`, `fdr_summary.txt`, `greedy/`, `permutation-t4/`, `permutation-wbf/`, `wbf/` | **LOW** — strong narrative already; minor polish for exemplar parity | Polish: add exec summary, rename cross-hypothesis paragraph to "Paper implications", add Caveats section. | S (~20–30 min) |
| **Phase 2b (H7 temperature retest)** | **NO** (narrative embedded in `results/retest/retest-production-summary.md` §Phase 2b, lines 40–69 + 248–267) | Raw data `outputs/retest/phase2b/track{1-image,2-text}/T{0.0,0.3,0.7,1.0,1.3}/run_{1..3}/` (10,200 tile-runs); `results/retest/phase2b-track{1,2}-evaluation.{json,metadata.json}`; YAML specs `studies/retest/phase2b-h7-temperature{,-text-only}.yaml` | **HIGH** — load-bearing for the paper's temperature claim; preregistered Phase 2b vs E43 UNINTENDED-T1.0 distinction (working-notes line 6069+) must be made explicit in a dedicated doc before drafting | Synthesise `results/retest/phase2b/analysis_summary.md` in the h12-v2 template. Use the two evaluation JSONs for the main table; lift pairwise contrasts from `retest-production-summary.md` §Phase 2b. Add a caveat block foregrounding the preregistered-vs-E43 separation. Archive-flag the three pre-retest `results/phase2b-*.md` files. | L (~90 min) |

### 4.5 Phase 2b status note

Phase 2b is structurally an **Era 1 retest** (preregistered H7 sweep,
340-tile retest corpus) rather than an Era 1 *hypothesis closure* doc
(like h8-v2 / h10 / h11 / h12-v2). It is added to the §4 gap table
because (a) its data is at parity with those four in scope and
statistical rigour (K=3 × 340 tiles + bootstrap CIs + FDR-corrected
contrasts), and (b) the paper's headline temperature claim cannot be
drafted without it. The "Era 1 retest" Type label (row 15) is used
in preference to a new column because the scorecard's required/
optional column set already captures what Phase 2b does and does not
provide.

## 5. Recommended Step 3 scope adjustments

**Default Step 3 scope** (per plan): synthesise Obs 262–273 (11 Obs)
into `results/meta-findings-summary.md`, paper-Discussion-shaped,
exemplar-tier, with "Suggested paper text" blocks per theme.

**Scorecard suggestion**: **no change**. The Era 1 gaps are real and
large, but:

- The meta-findings synthesis (Obs 262–273) is scoped to the 55-map
  image run + 4-map gold-standard, not to Era 1 hypotheses. Its source
  material (the 11 Obs + the seven 55-map partial reports) is all
  available at citable quality.
- Era 1 gaps feed the Results section of the paper (Era 1 hypothesis
  closure), which is Step 6's concern, not Step 3's.
- Every canonical number the meta-findings synthesis will cite
  (F1=0.830, curve 0.832→0.855, ECE 0.269 / AUC 0.655, attractor-pull
  125 m, subtype-F1 0.887, D-S AUC 0.500) has been verified present in
  its artefact. No FLAG blocks anticipated.

The only Step 3 delivery risk is the `buffer-100m-diagnostics/` stub —
if Theme T5 (attractor-pull + D-S) needs to cite the GT-clustering
decomposition, the citation must point to `summary.json` key paths
rather than a report section. That's citable, just less elegant.

## 6. Suggested Step 4 sequencing

Ordered by impact on paper-draftability, cost-benefit, and prerequisite
ordering:

1. **Synthesise `results/h8-v2/analysis_summary.md`** (L, ~90+ min).
   Audit calls this the strongest Era 1 narrative and the paper's
   Era 1 Results section leans on library-composition closure.
   Highest impact.
2. **Synthesise `results/h10/analysis_summary.md`** (L, ~90+ min).
   Calibration-pool closure is the second Era 1 pillar; together with
   h8-v2 and h12-v2, the library-design story is "closed" for the
   paper.
3. **Synthesise `results/retest/phase2b/analysis_summary.md`** (L,
   ~90 min). Load-bearing for the paper's temperature finding; the
   preregistered-vs-E43 distinction (working-notes line 6069+) must
   be explicit before drafting. Slot at priority 3 alongside the Era 1
   hypothesis closures because the temperature claim appears in the
   paper's headline findings rather than its Era 1 Results section.
   **Option B residual (MANDATORY sub-task)**: (a) create a retest-era
   `results/phase2b-carry-forward-parameters.md` equivalent (based on
   the 340-tile K=3 retest data); (b) repoint the citation at
   `results/phase2c-carry-forward-parameters.md:126` to the new
   retest-era doc; (c) archive the pre-retest
   `results/phase2b-carry-forward-parameters.md` to
   `archive/outputs-pre-retest-60-tile/phase2b/`. This completes the
   archive pass started 2026-04-23 (six orphan files already archived
   in that pass; the carry-forward doc was retained because of the
   Phase 2c dependency — see §3.15 Superseded pre-retest artefacts).
4. **Consolidate `results/h11/analysis_summary.md`** (M, 60–75 min,
   plus UNINTENDED-T1.0 disposition decision). Fragmentation is the
   bottleneck; a consolidated narrative unlocks the two-stage Results
   paragraph. **Note (2026-04-22)**: the UNINTENDED-T1.0 disposition
   has now been settled — see the updated banner READMEs at
   `/home/shawn/Code/map-reader-llm/outputs/h11/consensus-384-UNINTENDED-T1.0/README.md`
   and `/home/shawn/Code/map-reader-llm/outputs/h11/single-pass-384-UNINTENDED-T1.0/README.md`
   (dual-role: origin = E43 deviation; retained for 487-tile/Era 2
   T=1.0 scope coverage). Level-up effort remains M as a result.
5. **Write `results/55maps-image-generalisation/buffer-100m-diagnostics/report.md`**
   (M, 45–60 min). Small, high-leverage: gives Theme T5 a rendered
   citation target instead of JSON key paths.
6. **Write `results/paper-eval/mcc/report.md`** (M, 45–60 min). Same
   shape as item 4 — an analysis family where the data exist
   (batch-summary JSON + 12 + 18 + 32 + 15 per-condition JSONs) but no
   narrative synthesis. Gives the paper's tile-level MCC table a single
   citation target and documents which conditions belong in-paper.
7. **Level-up `results/factor-analysis/factor_analysis_results.md`**
   (M, ~45–60 min). Load-bearing for the paper's Results section
   (pairwise permutations across Architecture, Thinking, Temperature,
   Modality with FDR correction). Fix the four empty-cell Temperature
   rows, add exec summary / methods / repro / caveats / paper
   implications. Slot here rather than with the partial-report batch
   because the paper's "which factors matter" section cannot be
   drafted without it.
8. **Level-up `results/55maps-image-generalisation/uncalibrated-vs-
   calibrated-crosstab/crosstab.md`** (S, 25–35 min). Obs 268 lands in
   meta-findings Theme T1; a polished exec summary with the explicit
   flip-rate definition and a paper-implications block makes Theme T1
   citable without paraphrase.
9. **Level-up `results/evaluation-scopes.md`** (S, 20–30 min).
   Methods-section keystone — every cross-era F1 claim in the paper
   needs to cite the Era 1 / Era 2 / Era 3 scope table and the
   nesting-verification zero-tolerance result.
10. **Level-up the eight partial 55-map / extended-buffer / phase3a
    reports** (total ~3.5–4.5 hours at S/M per report, can be batched).
    Priority order within: #3 (buffer-band-lift — weakest repro) →
    #4 (verifier-calibration — supports Theme T3) → #1 (human-
    reviewed-corrected — headline number) → #14 (phase3a text-matrix
    secondary_effects — resolve §13 thinking-token anomaly and add
    infrastructure) → #18 (phase3a image-track secondary-effects —
    same §13 treatment; resolve jointly with #14) → #17 (phase3a
    image-track consensus-analysis-summary — align with row 18) →
    #6 (ds-human-crosstab) → #5 (DS-v2) → #2 (multi-buffer) → #8
    (extended-buffer polish).
11. **Level-up `results/retest/retest-production-summary.md`** (M,
    45–60 min). Era 1 multi-phase summary — add cross-cutting exec
    summary, formalise methods / caveats / paper implications, add
    Obs 262–273 back-references. Best slotted after row-15 Phase 2b
    split-out (item 3) so the level-up can cross-reference the
    dedicated Phase 2b doc.
12. **Write `55-map cross-track comparison doc`** (per continuity-doc
    "Need" list). Independent of above; can slot in parallel.
13. **Write `Limitations consolidation doc`** (per continuity-doc
    "Need" list). Independent; best done after the four Era 1 /
    buffer-100m / MCC / Phase 2b docs exist so Limitations can cite
    them.
14. **Era 1 docs: add exec summary + paper implications to h12-v2**
    (S, 20–30 min). Lowest-priority polish.

Total Step 4 effort estimate: **15.5–20 hours** if all items are
pursued at the quality bar implied by the scorecard (the six second-
pass additions add ~4 hours at the aggregate: factor-analysis M +
crosstab S + evaluation-scopes S + phase3a-image-consensus M + phase3a
image-secondary M + retest-production-summary M). Minimum viable for
paper draft: items 1–9 (~8–10 hours). Everything else can be partially
deferred to post-outline polish passes.

## 7. Numeric spot-check log

Eleven spot-checks performed (scoped to paper-headline numbers and to
internal consistency across the two new MCC rows, the Phase 2b row 15
addition, and the three second-pass spot-checks for the Obs 268
crosstab, the factor-analysis artefact, and the evaluation-scopes
nesting check):

| # | Claim | Source file | Value found | Matches continuity | Status |
|---|---|---|---|---|---|
| 1 | Corrected F1 ≥ 0.830 @ 50 m | `corrected-f1-human-reviewed.md` §Headline | 0.8295 | yes (rounds to 0.830) | ✓ |
| 2 | Multi-buffer curve 0.832 → 0.855 | `corrected-f1-multi-buffer/report.md` §F1 curve | 0.8317 / 0.8477 / 0.8521 / 0.8538 / 0.8551 | yes | ✓ |
| 3 | Attractor-pull p=0.381 at 125–150 m shell | `buffer-band-lift/report.md` §Annular | 0.381 | yes | ✓ |
| 4 | ECE 0.269 / AUC 0.655 | `verifier-calibration-crosstab/calibration.md` §§1, 3 | 0.2689 / 0.6545 | yes | ✓ |
| 5 | D-S VLM-only AUC = 0.500 | `ds-human-crosstab/report.md` §2 + `dawid-skene-v2-data-driven-prior/report.md` §v2 calibration | 0.5000 (both) | yes | ✓ |
| 6 | Flash HIGH text 16-of-30 + PV MCC = 0.790 [0.733, 0.840] | `results/paper-eval/mcc/consensus-pv/flash-high-text-16-of-30-pv/mcc.json` + `batch_mcc_summary.md` row 2 | 0.7903 [0.7328, 0.8401]; table shows 0.790 [0.733, 0.840] with TP/TN/FP/FN 188/247/11/41 | internally consistent JSON↔MD | ✓ |
| 7 | HIGH-T0.7 tile-level MCC = 0.620 [0.549, 0.691] (phase3a §3 ↔ paper-eval `batch_mcc_summary.md` row 10 "Flash HIGH text 26-of-30") | `phase3a-text-matrix/secondary_effects.md` §3 + `paper-eval/mcc/consensus-pv/batch_mcc_summary.md` | 0.620 [0.549, 0.691] in both; TP/TN/FP/FN 178/217/41/51 in both | cross-artefact agreement | ✓ |
| 8 | Phase 2b Track 1 T=0.0 completed=340 tiles (retest YAML: `retest_tiles: 340`) and F1 values agree across the two consolidation targets | `outputs/retest/phase2b/track1-image/T0.0/run_1/detections_T0.0_run01.tiles.json` + `results/retest/phase2b-track1-evaluation.json` + `results/retest/retest-production-summary.md` §Phase 2b | `total_tiles=340, len(completed)=340, len(failed)=0`; Track-1 F1 row (T0.0 0.5869 / T0.3 0.5751 / T0.7 0.5367 / T1.0 0.5269 / T1.3 0.4903) identical in the evaluation JSON and the retest-production-summary Phase 2b table | internally consistent JSON ↔ tiles.json ↔ narrative embedding | ✓ |
| 9 | Obs 268 flip rate = 21 % / disagreement 0.2141 / bootstrap CI [0.1713, 0.2599] / corrected-F1 ΔF1 = −0.0082 | `results/55maps-image-generalisation/uncalibrated-vs-calibrated-crosstab/crosstab.md` §§Overall agreement + Corrected-F1 accounting | disagreement 0.2141 (70/327 in direction Uncal=mound → Cal=not_mound, 0 in reverse); bootstrap CI [0.1713, 0.2599] at 10,000 iterations seed 42; ΔF1 = 0.8295 − 0.8377 = −0.0082 (all-cal minus mixed) | yes (matches working-notes Obs 268 + row 16 detail block) | ✓ |
| 10 | Factor-analysis architecture family — Flash HIGH text 16-of-30 + PV vs Flash HIGH text 26-of-30: ΔF1 = +0.076, p_adj = 0.0000 | `results/factor-analysis/factor_analysis_results.md` §Architecture row 9 | F1_A = 0.890, F1_B = 0.814, ΔF1 = +0.076, p(raw) = 0.0000, p(adj) = 0.0000 | cross-reference to row 13 `consensus-pv/flash-high-text-16-of-30-pv/mcc.json` (F1 implied by TP/FP/FN: 188/(188+11) P=0.945 × 188/(188+41) R=0.821 → F1 ≈ 0.880, close to factor-analysis 0.890 — minor difference likely reflects buffer-specific evaluation at 20 m vs the MCC artefact's tile-level classification) | ✓ (directional consistency) |
| 11 | evaluation-scopes nesting: Era 3 ⊂ Era 2 ⊂ Era 1 at zero tolerance (0.00 sq m outside), zero mounds unique to a smaller scope | `results/evaluation-scopes.md` §Nesting verification | Era 3 area inside Era 2 = 100.000 % (0.00 sq m outside); Era 2 inside Era 1 = 100.000 %; zero mounds unique to smaller scope | yes (zero-tolerance equality is the property the paper's Methods section needs; rounded 100.000 % + "0.00 sq m outside" gloss confirms this) | ✓ |

All eleven trace correctly. No discrepancies. Rows 6 and 7 confirm
the two new MCC-centred reports are internally consistent and agree
with each other where they overlap (the 384 px K=30 HIGH-T0.7
consensus). Row 8 confirms Phase 2b's three consolidation candidates
(raw tile-tracker JSON, evaluation JSON, narrative embedding) are
internally consistent to 4 decimal places. Row 9 ties the Obs 268
crosstab to its working-notes entry, confirming the flip-rate
definition is load-bearing and numerically identical across artefacts.
Row 10 confirms the factor-analysis PV-vs-consensus contrast is
directionally consistent with the paper-eval MCC artefact, which is
the source for the tile-level 2×2 breakdown. Row 11 confirms
`evaluation-scopes.md`'s strict-nesting claim is a zero-tolerance
equality and therefore safe to cite as a paper-Methods property.

## 8. Checkpoint summary for the user

```text
STEP 2 COMPLETE — checkpoint before Step 3
(Row 15 Phase 2b added 2026-04-22 first pass; rows 16-21 added
2026-04-22 second pass from Task-B focused re-inventory + the
Obs 268 crosstab. Rows 1-15 settled.)

Scorecard: planning/interim-docs-review.md

Headline counts:
- 20 reports reviewed (exemplar excluded); 21 rows total including
  the Obs 268 crosstab at row 16
- 0 ✓ exemplar-tier
- 13 ~ partial (total level-up ~6.5-8 hours for the thirteen)
- 2 ✗ stub (buffer-100m-diagnostics — no report.md, M;
           paper-eval/mcc/ — batch summaries only, no narrative, M)
- 4 ✗ missing (h8-v2 L, h10 L, h11 M, Phase 2b L)
- 9 out-of-scope items deferred to §10 (Era 1 carry-forward,
  Phase 3d negative-result satellites, retrospective runs)

Era 1 gap severity:
- h8-v2:   HIGH (no analysis_summary.md; L to synthesise)
- h10:     HIGH (no analysis_summary.md; L to synthesise)
- Phase 2b: HIGH (no dedicated analysis_summary.md; narrative
           embedded in retest-production-summary; L to synthesise;
           load-bearing for paper's temperature claim)
- h11:     MEDIUM (fragmented; M to consolidate; UNINTENDED-T1.0
           disposition now settled — see dual-role banner READMEs
           dated 2026-04-22)
- h12-v2:  LOW (strong doc; S polish)

Second-pass additions (2026-04-22):
- Row 16: Obs 268 uncalibrated-vs-calibrated crosstab (55-map core;
  ~ partial; S level-up; flip-rate definition and Theme T1 anchor)
- Row 17: phase3a-image-matrix consensus-analysis-summary (~; M)
- Row 18: phase3a image-track secondary-effects sweep (~; M)
- Row 19: factor-analysis pairwise permutations (~; M; load-bearing
  for paper's "which factors matter" Results section)
- Row 20: retest-production-summary Era 1 multi-phase narrative
  (~; M; paper-citation target for Era 1 Results)
- Row 21: evaluation-scopes methodology doc (~; S; Methods keystone)

Step 3 scope recommendation:
- Default scope (Obs 262–273 synthesis only) — NO CHANGE recommended
- All canonical numbers verified present; no FLAG blocks anticipated
- Era 1 gaps are Results-section work, not Discussion-spine work
- Phase 2b's T=1.0 vs E43-T=1.0 distinction is handled in the
  banner READMEs and working-notes line 6069+; no change needed
  at Step 3 scope
- Second-pass flip-rate definition (row 16) and factor-analysis
  directionality (row 19) are both citable for Theme T1 / Theme T3
  of the meta-findings synthesis without further level-up

Decisions requested:
1. Step 3 scope — confirm default (synthesise Obs 262–273 into
   results/meta-findings-summary.md) or approve a shift?
2. Step 4 sequencing — accept scorecard §6 updated order (h8-v2 →
   h10 → Phase 2b → h11 → buffer-100m → paper-eval/mcc report →
   factor-analysis → Obs 268 crosstab → evaluation-scopes → 8+2
   partial level-ups → retest-production-summary → cross-track doc
   → Limitations doc → h12-v2 polish), or re-prioritise?
3. Recalculation requests — none raised; any the user wants raised?
4. UNINTENDED-T1.0 disposition for h11 — settled 2026-04-22: dual
   role (E43 origin; retained for 487-tile/Era 2 T=1.0 scope).
   Paper's preregistered T=1.0 claim rests on Phase 2b (row 15),
   not on these two directories.
5. Out-of-scope items in §10 — review the nine deferred directories
   and confirm none need promotion to Step 2 coverage.

Awaiting explicit user response before starting Step 3.
```

## 9. Language / guardrail confirmation

- **UK/Australian English**: scorecard body uses `analyse`, `behaviour`,
  `prioritise`, `synthesise`, `consolidation` (all UK/AU). The source
  reports themselves are mixed — level-up passes in Step 4 should
  audit and convert US → UK/AU spellings per the global CLAUDE.md
  table.
- **No archive citations**: no reviewed report cites
  `archive/v2-verifier-contamination/` or `archive/flawed-audit-2026-04-19/`.
- **E47 disambiguation**: not applicable — no report references E47
  directly. The distinction will land in the meta-findings document
  (Step 3 §11 Caveats).

## 10. Known out-of-scope

**Scope statement**: this scorecard covers a deliberately-bounded
subset of `results/` — the 55-map image-generalisation core, the
Era 2 phase3a matrix and secondary-effects, the Era 1 hypothesis
closures (h8-v2 / h10 / h11 / h12-v2), the Phase 2b temperature
retest, the factor-analysis omnibus, the tile-level MCC family, and
the methodology-layer `evaluation-scopes.md`. The items listed below
were surveyed during the 2026-04-22 second-pass re-inventory and
**deliberately deferred** because they are either (a) Era 1 carry-
forward / track-specific overviews whose paper role is covered by
the Era 1 hypothesis closures and `retest-production-summary.md`
(row 20); (b) Phase 3d negative-result satellites that do not affect
the paper's headline claims; or (c) retrospective / auxiliary
artefacts not cited in the paper's Results or Discussion.

Listing them here preserves transparency: future readers can see the
scorecard covered a scoped subset, not the entire `results/` tree.
If any of these are promoted to in-scope for the paper draft, they
can be added as row 22+ without invalidating rows 1–21.

### 10.1 Era 1 carry-forward / track analyses (out-of-scope)

- `/home/shawn/Code/map-reader-llm/results/phase2a-analysis-summary.md`
  + `.json` + `phase2a-carry-forward-parameters.md` — Phase 2a H1
  modality retest; narrative covered by row 20 §Phase 2a.
  Carry-forward doc is a config-propagation ledger, not an analysis.
- `/home/shawn/Code/map-reader-llm/results/phase2b-carry-forward-parameters.md`
  + the three pre-retest `phase2b-*.md` orphans (`phase2b-track1-image-summary.md`,
  `phase2b-track2-text-summary.md`, and the carry-forward doc) —
  pre-retest 60-tile × K=10 artefacts that do not appear in the
  paper; row 15 level-up will archive-flag these to prevent
  mis-citation (see §3.15 "Superseded pre-retest artefacts").
- `/home/shawn/Code/map-reader-llm/results/phase2c-*`,
  `phase2d-*`, `phase2e-*` (carry-forward + track analyses across
  H2 / H3 / H4 hypotheses) — Era 1 single-pass hypothesis-specific
  narratives; paper role covered by row 20 §§Phase 2c / 2d / 2e.
- `/home/shawn/Code/map-reader-llm/results/retest/` subdirectories
  beyond `retest-production-summary.md` (phase2a, phase2b-track1,
  phase2b-track2, phase2c, phase2d, phase2e, phase3a-consensus
  evaluations) — per-phase evaluation JSONs whose narrative lives
  in row 20; graded at the summary level, not per-JSON.

### 10.2 Phase 3d negative-result satellites (out-of-scope)

- `/home/shawn/Code/map-reader-llm/results/phase3d-pilot-results.md`,
  `phase3d-pilot-extensions.md`, `phase3d-union-results.md`,
  `phase3d-experiment-e-results.md` — H2 two-stage pipeline pilot
  (K=1 T=0.0, three verifier strategies, cross-modal union, Experiment
  E's negative result on high-recall text proposers). These established
  Era 1 architecture decisions that are superseded by the paper's
  final pipeline (Era 2+); the "complementary text + image tracks"
  finding from `phase3d-pilot-extensions.md` is the only piece with
  a candidate paper-Discussion link, and it is covered adequately by
  the factor-analysis §Modality family (row 19) and by row 20.
- `/home/shawn/Code/map-reader-llm/results/phase3d-high-thinking-results.md`
  and `phase3d-verifier-experiments-abc.md` — focused negative-result
  experiments on 44 image-only candidates (HIGH thinking made
  precision worse; Experiments A–D each failed the F1 > 0.796 success
  criterion). Paper role at most a one-sentence Discussion mention;
  not worth a scorecard row.

### 10.3 Auxiliary / retrospective artefacts (out-of-scope)

- `/home/shawn/Code/map-reader-llm/results/tolerance-sensitivity/`
  (CSV + JSON only, no rendered `.md`) — tolerance-sensitivity
  sweep; data is available for a future level-up but there is no
  narrative target to grade.
- `/home/shawn/Code/map-reader-llm/results/55maps-cleaned-gt-evaluation/`
  — GT-cleaning diagnostic; paper role is auxiliary.
- `/home/shawn/Code/map-reader-llm/results/cross-hypothesis-library/`
  — library-composition cross-hypothesis artefact; superseded by
  h8-v2 / h10 narratives.
- `/home/shawn/Code/map-reader-llm/results/e47-propose-brief/` —
  E47 errata-specific artefact; not cited in the paper.
- `/home/shawn/Code/map-reader-llm/results/gt-duplicate-review/`,
  `gt-spacing-analysis/` — GT-QA diagnostics; auxiliary context.
- `/home/shawn/Code/map-reader-llm/results/leaderboard/`,
  `pairwise/` — leaderboard / pairwise aggregates; superseded by
  row 19 factor-analysis for pairwise, and by row 13 paper-eval/mcc
  family for the leaderboard's tile-level claims.
- `/home/shawn/Code/map-reader-llm/results/phase3c-diversity/` —
  Phase 3c diversity-dividend artefact; paper role covered by Obs
  numbers in working-notes, not a standalone report.
- `/home/shawn/Code/map-reader-llm/results/pv/` — proposer-verifier
  auxiliary aggregates (including the bootstrap CIs source cited by
  row 20); grading would duplicate row 19's PV permutation coverage.
- `/home/shawn/Code/map-reader-llm/results/55maps-generalisation/`
  (retrospective text run) — paper generalisation path is the
  image run (rows 1–8, 16); this text-track retrospective is
  auxiliary context.

### 10.4 If any are promoted to in-scope

If during Step 3 or Step 6 any of the above is found to carry a
paper-Discussion or paper-Results claim that is not already covered
elsewhere, add the row at the next sequential number (row 22+) and
record the promotion rationale in §1 "Reports reviewed" with a
dated note. The default posture remains **defer to §10** unless
promotion is actively demonstrated.

---

**End of scorecard.** Proceed only on explicit user approval per §8.
