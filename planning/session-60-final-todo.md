# Session 60+: Final Analysis To-Do

**Created**: 2026-03-28, end of Session 59
**Goal**: Complete all remaining analysis for paper submission.
**Status**: All API work complete. All remaining work is local
(sapphire) and documentation.

---

## 1. Spatial Tolerance Curve (NEW — from Opus review)

- [ ] **Ensure F1, P, R with CIs at all 4 buffers (20/30/40/50m) for
  all paper-critical conditions** — the multi-buffer evaluation
  (`results/paper-eval/`) has this for consensus and PV conditions.
  Check that CIs for P and R are in the JSON outputs (they should be —
  `bootstrap_ci()` returns all three).
- [ ] **Produce plottable tolerance curve data** — extract F1, P, R at
  each buffer for the top ~10 conditions. Format as CSV suitable for
  plotting (condition × buffer × metric).
- [ ] **Decide headline buffer** — Opus recommends 20m as headline
  with 30m as "more empirically grounded for future work" and the
  tolerance curve as a prominent figure. Consider this vs our current
  30m-primary decision (E46). Either way, we need complete results at
  both buffers.

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

- [ ] **Write orchestration script** — YAML-driven Python script that
  reads `configs/pairwise-comparisons.yaml` (32 comparisons, 7 groups),
  builds GeoDataFrames for each side, runs permutation tests via
  `pairwise_permutation_test.py` logic, outputs per-comparison JSONs.
  Must handle cross-mode comparisons (PV vs consensus) by pre-exporting
  to GeoJSON.
- [ ] **Run at 30m** (primary) — 32 comparisons, ~3 min on sapphire.
- [ ] **Run at 20m** (sensitivity) — same 32 comparisons, ~3 min.
- [ ] **Verify** — temperature comparisons (Group 4) should be highly
  significant; top-N (Group 6) should mostly be non-significant.

## 4. FDR Correction

- [ ] **Write FDR correction script** (`apply_fdr_correction.py`) —
  reads all pairwise result JSONs, separates confirmatory (26) and
  exploratory (6) families, applies Benjamini-Hochberg at q=0.05,
  outputs consolidated table with raw p, adjusted p, significance
  indicators.
- [ ] **Run at 30m** — the primary analysis.
- [ ] **Report 20m without FDR** — as sensitivity table.

## 5. Paper Tables

- [ ] **Consolidated N=1 leaderboard** — merge the three N=1 evaluation
  batches (384px existing, 384px outstanding, 512px Phase 2) into one
  sorted table with F1, P, R, MCC, all with CIs.
- [ ] **Pipeline progression table** — the Obs 202 table: N=1 → consensus
  → PV showing F1 and MCC at each stage. With CIs.
- [ ] **Pairwise comparison table** — grouped by research question, with
  ΔF1, CI, raw p, adjusted p, significance.
- [ ] **Spatial tolerance table/figure** — F1 at 20/30/40/50m for top
  conditions. For paper figure.
- [ ] **Pro 2×2 matrix table** — the temperature × thinking interaction
  (Obs 200).

## 6. API Cost Retrospective

- [ ] **Parse all meta.json cost_estimate fields** — compute total
  actual spend across the project.
- [ ] **Estimate Batch API savings** — what we saved vs all-real-time.
- [ ] **Estimate context caching savings** — what we would have saved
  on image-track runs.
- [ ] **Produce cost table for paper** — actual cost, optimal cost,
  per-mound cost at different pipeline stages.

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
