# Session 60+: Final Analysis To-Do

**Created**: 2026-03-28, end of Session 59
**Goal**: Complete all remaining analysis for paper submission.
**Status**: All API work complete. All remaining work is local
(sapphire) and documentation.

---

## 1. Spatial Tolerance Curve (NEW — from Opus review)

- [x] **Ensure F1, P, R with CIs at all 4 buffers (20/30/40/50m) for
  all paper-critical conditions** — Done (Session 60). Consensus, PV,
  and all N=1 conditions (384px 18 + 512px 33) now have complete
  evaluations at 20/30/40/50m. [2026-03-28]
- [x] **Produce plottable tolerance curve data** — 15 conditions × 4
  buffers in `results/paper-tables/spatial_tolerance_curve.csv`. Covers
  7 PV, 7 consensus, 1 N=1 baseline with short labels. [2026-03-28]
- [x] **Decide headline buffer** — 20m headline per preregistration.
  Feature tolerance curve prominently and argue 30m (~target symbol
  minimum radius) is more empirically grounded — that's where the
  text-track plateau begins. [2026-03-28]

## 2. MCC Completeness

- [x] **N=1 MCC at 384px** — 18 conditions. Done (Session 59).
- [x] **N=1 MCC at 512px** — 33 Phase 2 conditions. Done (Session 59).
- [x] **Consensus + PV MCC** — 12 conditions. Done (Session 59).
- [ ] **MCC for ALL consensus conditions at all pool sizes** — we did
  MCC for the best threshold at each pool size for 6 consensus
  conditions. May want MCC for additional consensus conditions
  (e.g., flash-min-text-t07, flash-min-text-t10, flash-min-image)
  to show how MCC varies across the full range. Quick on sapphire.
- [ ] **MCC for remaining PV conditions** — we did 3 PV + 3 N=1
  baselines. May want MCC for text-baseline + PV, image-baseline + PV,
  and the medium-verifier condition for completeness.

## 3. Pairwise Permutation Tests

- [x] **Write orchestration script** — `scripts/run_pairwise_tests.py`:
  YAML-driven, imports from `pairwise_permutation_test.py`, GDF caching,
  path validation, `--leaderboard` mode for round-robin. [2026-03-28]
- [x] **Run at 30m** (primary) — 32 comparisons in 107s. 21/32
  significant pre-FDR; 18/26 confirmatory + 3/6 exploratory after
  FDR. [2026-03-28]
- [x] **Run at 20m** (sensitivity) — 32 comparisons in 108s. 20/26
  confirmatory + 3/6 exploratory after FDR. Directionally consistent
  with 30m. [2026-03-28]
- [x] **Verify** — Group 4 (temperature) all *** p<0.001. Group 6
  top 3 indistinguishable (ns), #4 onward significant. Matches
  expectations. [2026-03-28]

## 4. FDR Correction

- [x] **Write FDR correction script** — `scripts/apply_fdr_correction.py`:
  BH correction by family, outputs JSON/CSV/Markdown tables.
  [2026-03-28]
- [x] **Run at 30m** — Confirmatory: 18/26 sig. Exploratory: 3/6 sig.
  Results in `results/pairwise/30m/fdr/`. [2026-03-28]
- [x] **Run at 20m** — Confirmatory: 20/26 sig. Exploratory: 3/6 sig.
  Results in `results/pairwise/20m/fdr/`. [2026-03-28]

## 5. Paper Tables

- [x] **Consolidated N=1 leaderboard** — 51 conditions (18 at 384px +
  33 at 512px) × 4 buffers = 204 rows. Pro models dominate top-4 at
  384px. In `results/paper-tables/n1_leaderboard.csv`. [2026-03-28]
- [x] **Pipeline progression table** — N=1 → consensus (N=5/10/30) →
  PV. F1 goes from 0.406 to 0.904 (+0.498). In
  `results/paper-tables/pipeline_progression.csv`. [2026-03-28]
- [x] **Pairwise comparison table** — `pairwise_hypothesis_table.csv/md`
  with 20m sensitivity cross-check. Plus `leaderboard_tiers.csv/md`:
  9 tiers from 25 conditions, top tier = 3 indistinguishable PV
  conditions (F1 0.885–0.904). [2026-03-28]
- [x] **Spatial tolerance table/figure** — Data in
  `spatial_tolerance_curve.csv` (15 conditions × 4 buffers). Ready
  for plotting. [2026-03-28]
- [x] **Pro 2×2 matrix table** — Temperature × thinking interaction for
  text and image. Strong crossover: MEDIUM+T=0.0 best, HIGH+T=0.7 best.
  In `results/paper-tables/pro_2x2_matrix.json`. [2026-03-28]

## 6. API Cost Retrospective

- [x] **Parse all meta.json cost_estimate fields** — $87.07 tracked
  real-time + ~$107-116 estimated batch = ~$195-203 total across
  353,863 tile inferences. [2026-03-28]
- [x] **Estimate Batch API savings** — 50% discount on 77% of tile
  inferences (~$107-116 saved). [2026-03-28]
- [x] **Estimate context caching savings** — 33% cache hit rate on
  452M input tokens. [2026-03-28]
- [x] **Produce cost table for paper** — Full JSON in
  `results/paper-tables/cost_retrospective.json`. Per-mound cost
  ~$0.34. [2026-03-28]

## 7. Documentation and Housekeeping

- [ ] **Commit all Session 59 changes** — substantial: bug fixes
  (tiles_dir, trailing comma, tile_size inference, pricing), new
  scripts (evaluate_detections.py, evaluate_tile_mcc.py,
  consolidate_paper_metrics.py), study YAMLs, evaluation results,
  working notes (Obs 196-202), erratum E46, context caching, configs.
  Break into logical commits.
- [ ] **Update to-do.md** — mark completed items, add new items from
  this session.
- [ ] **Copy plans to planning/** — session-60 plan should be in
  git-tracked `planning/` directory.
- [ ] **Clean up batch_working directories on sapphire** — may have
  accumulated from the outstanding runs.

## 8. Outstanding Items from Master To-Do

- [ ] **Phase 3c H9 diversity Track 1 vs Track 2 comparison** — data
  exists in `results/phase3c-diversity/`, just needs the comparison
  written up.
- [ ] **Add defensive model check to run_phase2.py and run_pv.py** —
  verify model name matches study dir/YAML before proceeding.
- [ ] **Buffer sensitivity table in paper** — Obs 190 findings, now
  superseded by the comprehensive multi-buffer evaluation.
- [ ] **Update bootstrap-cis-384px.json** — the old consolidated CI
  file. May be superseded by the new paper-eval results.

---

## Suggested Execution Order

1. Spatial tolerance curve data extraction (quick, local)
2. Pairwise tests + FDR (sapphire, ~10 min total)
3. Paper tables (local, uses all the above)
4. Commits (break into logical chunks)
5. Cost retrospective (local, parse meta.json files)
6. Any remaining MCC conditions (sapphire, quick)
7. H9 diversity comparison (local)
8. Documentation cleanup

Total estimated time: ~4-6 hours of active work.
