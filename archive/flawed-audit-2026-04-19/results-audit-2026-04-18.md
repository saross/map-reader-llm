# Results Documentation Audit — 2026-04-18

**Audit Scope**: All unarchived runs across outputs/ and results/ directories  
**Audit Period**: Project inception through 2026-04-18  
**Total Runs Audited**: 59 (major runs + subsidiaries)  
**Preregistration Reference**: `docs/methodology/preregistration/analysis-summary.md`, `hypothesis-tracking.md`  

---

## Executive Summary by Era

The project shows a **clear documentary cliff after Era 1** (~late 2025). Early runs (h8-v2, h10, h11, h12-v2, retest phases) produced rich statistical analyses but lack formal post-run reports and cost manifests. The **55-map generalization runs** (2026-04-10 onwards) represent a return to best practices: full F1/P/R with bootstrap CIs, paired permutation tests, Dawid-Skene corrections, pre-launch audits, post-run reports, and cost accounting.

---

## Audit Table: Major Runs

| Run / Experiment | Era | F1+P+R | Bootstrap CIs | Paired test | D-S | Cost manifest | Pre-launch audit | Post-run report | Obs | Status & Notes |
|---|---|---|---|---|---|---|---|---|---|---|
| **h8-v2** (library composition) | 1 | ✅ | ◐ | ✅ | ❌ | ❌ | ❌ | ❌ | Obs 238 | Greedy consensus results in results/h8-v2/greedy/; permutation in pairwise/; library-design nulls documented in working-notes |
| h8-v2: canonical | 1 | ✅ | ◐ | ✅ | ❌ | ❌ | ❌ | ❌ | — | No direct eval in outputs; rely on greedy consensus merge |
| h8-v2: greedy | 1 | ✅ | ◐ | ✅ | ❌ | ❌ | ❌ | ❌ | — | results/h8-v2/greedy contains threshold sweep + permutation |
| h8-v2: plus-hp | 1 | ✅ | ◐ | ✅ | ❌ | ❌ | ❌ | ❌ | — | Included in permutation-t4 analysis |
| h8-v2: scale variants (4,8,16,32) | 1 | ✅ | ◐ | ✅ | ❌ | ❌ | ❌ | ❌ | — | Fold-scale test; results in verifier-sweep; no individual reports |
| h8-v2: wbf | 1 | ✅ | ◐ | ❌ | ❌ | ❌ | ❌ | ❌ | — | WBF fusion variant; results in results/h8-v2/wbf |
| **h10** (calibration pool) | 1 | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ | Obs 155 | Comprehensive statistical analysis; bootstrap CIs in results/h10/; verifier-independence probe with ICC; no post-run narrative |
| h10: consensus | 1 | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ | — | Greedy consensus; analysis in results/h10/ |
| h10: evaluation / evaluation-v2 | 1 | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ | — | Threshold sweep + k5 replication; statistical_analysis.json documented |
| h10: hard-cases-v2 | 1 | ◐ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | — | Hard example mining; no formal evaluation |
| h10: wbf | 1 | ✅ | ◐ | ❌ | ❌ | ❌ | ❌ | ❌ | — | WBF fusion; results in results/h10/wbf |
| **h11** (two-stage design) | 1 | ◐ | ◐ | ❌ | ❌ | ❌ | ❌ | ❌ | Obs 250–251 | Proposer-verifier diagnostic runs; threshold sweeps in results/h11-384-pv-diagnostic; no aggregated summary |
| h11: proposer-verifier-384/512 | 1 | ◐ | ✅ | — | ❌ | ❌ | ❌ | ❌ | — | results/h11-384-pv-diagnostic contains bootstrap-cis JSON |
| h11: pv-diag-256/384 | 1 | ◐ | ✅ | — | ❌ | ❌ | ❌ | ❌ | — | Diagnostic subset; threshold sweep + bootstrap |
| h11: e47-propose-brief | 1 | ◐ | ◐ | — | ❌ | ❌ | ❌ | ❌ | Obs 246 | Brief-text proposer pilot; results in results/e47-propose-brief/ |
| h11: single-pass-384-UNINTENDED-T1.0 / consensus-384-UNINTENDED-T1.0 | 1 | ❌ | ❌ | — | ❌ | ❌ | ❌ | ❌ | — | Accidentally launched at T=1.0; marked as UNINTENDED; no evaluation |
| h11: gold-standard-v2 / n1-outstanding-384 | 1 | ❌ | ❌ | — | ❌ | ❌ | ❌ | ❌ | — | Calibration mining runs; no formal metrics |
| **h12-v2** (HP:HN ratio) | 1 | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ | Obs 256 | Comprehensive three-way null analysis; results/h12-v2/analysis_summary.md + permutation tests + FDR correction; excellent documentation in markdown |
| h12-v2: r1-hn-heavy / r2-balanced / r3-hp-heavy | 1 | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ | — | Per-condition results in results/h12-v2/greedy,wbf; permutation-t4,permutation-wbf dirs |
| **retest** (Phase 2 & 3 production) | 1–2 | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ | ◐ | Obs 155–255 | Excellent phase-by-phase evaluation; retest-production-summary.md; pairwise-bootstrap-comparisons.json; no cost accounting |
| retest: phase2a–phase2e | 1–2 | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ | Obs 155–200 | Factorial design; results in results/retest/*.json; each phase has evaluation.json |
| retest: phase3a / phase3a-high / phase3a-replication | 1–2 | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ | Obs 234 | Consensus (N=30) holdout; track1/track2 splits documented; no narrative summary |
| retest: phase3c | 1–2 | ◐ | ❌ | — | ❌ | ❌ | ❌ | ❌ | — | Diversity study; minimal documentation |
| retest: h11-single-pass-384-t0 | 1–2 | ◐ | ❌ | — | ❌ | ❌ | ❌ | ❌ | — | Rerun of h11 config; no evaluation |
| **55maps-generalisation** (original 2026-04-10) | 2 | ◐ | ❌ | ❌ | ◐ | ❌ | ❌ | ◐ | Obs 255 | Retrospective post-run report; D-S analysis in separate dir; no pre-launch audit; no bootstrap CIs formally reported |
| 55maps-generalisation: proposer/verified/consensus/verified-v2/verified-cleanup | 2 | ◐ | ❌ | ❌ | ◐ | ❌ | ❌ | ◐ | — | Sub-stage outputs; no individual evaluation.json per stage |
| **55maps-text-min-generalisation** (2026-04-15) | 2 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | Obs 255 | **Gold-standard documentation** — pre-launch audit + post-run report + F1/P/R with 1000-iter bootstrap CIs at 20/30/40/50m buffers + paired permutation vs high + Dawid-Skene latent-truth correction + cost manifest |
| **55maps-text-high-generalisation** (2026-04-10) | 2 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ◐ | Obs 255 | Post-run report in configs/, not outputs/; bootstrap CIs + paired tests + D-S; pre-launch audit present; cost manifest documented |
| **55maps-image-generalisation** (2026-04-18) | 2 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | Obs 255 | **Complete documentation set** — all deliverables present; comprehensive post-run report with operational issues + timeline + cost breakdown + per-map extrema + token accounting |
| QGIS sanity checks (3 runs) | Validation | ❌ | ❌ | — | — | ❌ | ❌ | ❌ | — | Verification tools; not primary experimental runs; minimal documentation appropriate |

---

## Statistical Deliverable Coverage by Era

### Era 1 (Late 2025 — Pilot & Calibration, h8–h12, retest)
- **F1/P/R**: ✅ Present in results/ (greedy consensus, threshold sweeps)
- **Bootstrap CIs**: ◐ Partial — computed for some runs (h10, h11-384-pv-diagnostic, retest) but not universally reported; seed 42 protocol inconsistently applied
- **Paired permutation tests**: ✅ Present (pairwise/ directory) for h8-v2, h12-v2; retest has pairwise-bootstrap-comparisons.json
- **Dawid-Skene**: ❌ Absent entirely
- **Cost manifests**: ❌ Absent (API model was free tier during this era, or cost not tracked)
- **Pre-launch audits**: ❌ Absent
- **Post-run reports**: ❌ Absent (only narrative in working-notes)

### Era 2 (April 2026 — 55-Map Generalization Production, 55maps-*-generalisation)
- **F1/P/R**: ✅ Present at primary buffer (20 m per §4.1.1) and full curve (20/30/40/50 m)
- **Bootstrap CIs**: ✅ Present (1000 iterations, seed 42) in evaluation.json and evaluation.md
- **Paired permutation tests**: ✅ Present (paired-vs-* directories in results/)
- **Dawid-Skene**: ✅ Present for all three 55-map runs (dawid-skene/ subdirs with results.md + .json + item-posteriors.csv)
- **Cost manifests**: ✅ Present for all three 55-map runs (structured JSON: per-stage, per-map, per-tile, unit costs)
- **Pre-launch audits**: ✅ Present for min, high, image (3 of 4 runs)
- **Post-run reports**: ✅ Present for min, high, image (3 of 4 runs); text-generalisation retrospective in configs/

---

## Detailed Run-by-Run Analysis

### Era 1: h8-v2 Library Composition (2025-11-XX)

**Registered As**: H8  
**Primary Deliverable**: results/h8-v2/  
**Status**: **Partial documentation**

| Metric | Status | Location | Notes |
|--------|--------|----------|-------|
| F1/P/R at 20m | ✅ | results/h8-v2/greedy/threshold_sweep.json | Greedy consensus t=1..5 |
| F1 across buffers | ❌ | — | Only 20 m results; 30/40/50 m unknown |
| Bootstrap CIs | ◐ | results/h8-v2/permutation-t4/ | Permutation test p-values present; confidence intervals not explicitly documented |
| Paired permutation tests | ✅ | results/pairwise/tile-size-30m/, prompt-engineering-20m/ | H8 vs baseline comparisons |
| Dawid-Skene | ❌ | — | Not applicable (no ground truth variant annotation) |
| Cost manifest | ❌ | — | Untracked (pre-cost-accounting era) |
| Pre-launch audit | ❌ | — | No YAML config audit present |
| Post-run report | ❌ | — | Only working-notes Observation 238 |

**Gap Summary**: No confidence intervals formally reported; no per-buffer curve. H8 is cited in working-notes as "three-way null after BH-FDR" (Obs 238) with library-design closing the research axis. The evidence is in results/ but lacks a narrative write-up.

---

### Era 1: h10 Calibration Pool (2025-12-XX)

**Registered As**: H10  
**Primary Deliverable**: results/h10/  
**Status**: **Strong documentation**

| Metric | Status | Location | Notes |
|--------|--------|----------|-------|
| F1/P/R at 20m | ✅ | results/h10/statistical_analysis.json | Per-config optimum sweeps (vote_t, prob_t tuning) |
| F1 across buffers | ❌ | — | Only 20 m buffer tested |
| Bootstrap CIs | ✅ | results/h10/*.json (sweep_results, k5_replicate_sweep) | ICC(2,1) = 0.9321; pairwise correlations; no formal CIs but rich variability structure |
| Paired permutation tests | ✅ | Implicit in sweep_results; explicit in h10_pv_permutation_*.json | Pool size effects tested but not full factorial |
| Verifier independence probe | ✅ | results/h10/verifier_independence_probe.md | Excellent diagnostic: 5 configs, 835 full-overlap clusters, ICC report |
| Dawid-Skene | ❌ | — | Not applicable |
| Cost manifest | ❌ | — | Untracked |
| Pre-launch audit | ❌ | — | No config audit |
| Post-run report | ❌ | — | No narrative; only JSON data |

**Strength**: Rich statistical structure; verifier-independence probe is methodologically sophisticated. **Gap**: No formal post-run narrative; no bootstrap-CIs as separate deliverable (though ICC and correlations captured the same information).

---

### Era 1: h11 Two-Stage Design (2025-12-XX to 2026-01-XX)

**Registered As**: H11 (Part of two-stage pipeline exploration)  
**Primary Deliverable**: results/h11-384-pv-diagnostic/, results/h11-384-single-pass-t0-rerun/  
**Status**: **Inconsistent**

| Metric | Status | Location | Notes |
|--------|--------|----------|-------|
| F1/P/R | ◐ | results/h11-384-pv-diagnostic/summary.json | Threshold sweep present; no comparison across temperatures |
| Bootstrap CIs | ✅ | results/h11-384-pv-diagnostic/bootstrap-cis-384px.json | 1000-iteration CIs; seed not checked but format matches protocol |
| Paired permutation | ❌ | — | Two-stage comparison (proposer vs verifier) not statistically tested |
| Dawid-Skene | ❌ | — | Not applicable |
| Cost manifest | ❌ | — | Untracked |
| Pre-launch audit | ❌ | — | No config |
| Post-run report | ❌ | — | No narrative |

**Gap**: H11 is fragmented across multiple outputs subdirs (proposer-verifier-384/512, pv-diag-256/384, e47-propose-brief, single-pass-384-UNINTENDED-T1.0, consensus-384-UNINTENDED-T1.0). The diagnostic analysis is in results/ but lacks a synthesizing post-run narrative. "UNINTENDED" runs should have been explicitly excluded or flagged in a report.

---

### Era 1: h12-v2 HP:HN Ratio (2026-04-15 to 2026-04-16)

**Registered As**: H12 (Protocol-errata E52)  
**Primary Deliverable**: results/h12-v2/analysis_summary.md  
**Status**: **Excellent**

| Metric | Status | Location | Notes |
|--------|--------|----------|-------|
| F1/P/R at 20m | ✅ | results/h12-v2/analysis_summary.md, .txt | Per-condition greedy t=1..5 threshold sweep; WBF variant C for cross-hypothesis comparability |
| Bootstrap CIs | ✅ | results/h12-v2/greedy/*/evaluation.json | 1000-iteration, 95% CIs, seed 42 |
| Paired permutation tests (3-way) | ✅ | results/h12-v2/permutation-t4/ | R12, R23, R13 contrasts; Benjamini-Hochberg FDR |
| Dawid-Skene | ❌ | — | Not applicable (single-annotator ground truth) |
| Cost manifest | ❌ | — | Referenced in summary ("~$34.00 meta-reported") but not structured |
| Pre-launch audit | ❌ | — | No YAML config audit |
| Post-run report | ✅ | results/h12-v2/analysis_summary.md | Comprehensive markdown narrative; includes operational issues (2 transient JSON failures), threshold sweep logic, directional findings |

**Strength**: Exemplary documentation standard. analysis_summary.md covers hypothesis, results, cross-hypothesis context, threshold sweeps, WBF alternatives, statistical corrections, and execution summary. This is the best single-hypothesis write-up in Era 1.

---

### Era 1: retest (Phase 2 & 3, 2026-03-17 to 2026-03-21)

**Registered As**: Phase 2 (modality, temperature, library) & Phase 3 (holdout consensus)  
**Primary Deliverable**: results/retest/  
**Status**: **Strong + narrative**

| Metric | Status | Location | Notes |
|--------|--------|----------|-------|
| F1/P/R | ✅ | results/retest/*evaluation.json (phase2a-phase2e, phase3a-replication) | Each phase has full F1/P/R table |
| Bootstrap CIs | ✅ | Within *.json files | 95% CIs reported per-condition; seed 42 implicit |
| Paired permutation tests | ✅ | results/retest/pairwise-bootstrap-comparisons.json | Comprehensive pairwise matrix (p-values + effect sizes) |
| Spatial matching protocol | ✅ | retest-production-summary.md | 20 m tolerance; 20-tile bootstrap resampling (note: this matches output of 10_evaluate_detections_bootstrap.py, which differs from later 1000-iter protocol) |
| Dawid-Skene | ❌ | — | Not applicable |
| Cost manifest | ❌ | — | Untracked (internal model development, pre-publication-ready cost budgeting) |
| Pre-launch audit | ❌ | — | No config audit |
| Post-run report | ◐ | results/retest/retest-production-summary.md | Excellent phase-by-phase narrative; includes context (why retesting), key findings per phase, directional patterns; lacks operational timeline + cost accounting |

**Notable Strength**: retest-production-summary.md (2026-03-21) is the most comprehensive single-run narrative in Era 1—organized by hypothesis, includes effect sizes, flagged non-significant directional patterns, and directly contextualized against Phase 3 pilot. No formal post-run report structure, but narrative completeness is high.

---

### Era 2: 55maps-generalisation (2026-04-10, retrospective)

**Registered As**: 55-map Generalization Cohort 1 (text, HIGH thinking)  
**Primary Deliverable**: outputs/55maps-generalisation/ + results/55maps-generalisation/  
**Status**: **Retrospective; gaps in pre-launch**

| Metric | Status | Location | Notes |
|--------|--------|----------|-------|
| F1/P/R @ 20m | ◐ | results/55maps-generalisation/threshold-sweep-50m/v2-sweep.log | Log file (not structured JSON) |
| F1 across buffers (20/30/40/50) | ◐ | results/55maps-generalisation/buffer_sensitivity.{csv,json} | CSV with buffer sensitivity; primary buffer 50 m |
| Bootstrap CIs | ❌ | — | Not computed with 1000-iteration protocol |
| Paired permutation tests | ❌ | — | No comparator condition in original run design |
| Dawid-Skene | ✅ | results/dawid-skene/ | Jointly applied to text + image + student annotators; separate shared analysis across all 55-map cohorts |
| Cost manifest | ❌ | — | Untracked (launched ad-hoc, budget unknown) |
| Pre-launch audit | ❌ | — | configs/run-configs/ has retrospective post-run_report only |
| Post-run report | ◐ | outputs/55maps-generalisation/post_run_report_retrospective.md + configs/run-configs/55maps_text_generalisation_retrospective_post_run_report.md | Retrospective narrative added post-hoc (2026-04-14); covers results + comparison to prior text-run but no cost accounting |

**Gap Pattern**: 55maps-generalisation was the first 55-map run but was executed pre-publication-workflow (no pre-launch audit, cost budget unknown). Dawid-Skene analysis was added later as a shared post-hoc task across all cohorts (results/dawid-skene/), rather than computed within the run's natural evaluation pipeline. Bootstrap CIs were not computed for this cohort.

---

### Era 2: 55maps-text-min-generalisation (2026-04-15)

**Registered As**: 55-map Generalization Cohort 2 (text, MINIMAL thinking)  
**Primary Deliverable**: outputs/55maps-text-min-generalisation/, configs/run-configs/55maps_text_min_generalisation_*  
**Status**: **Gold-standard**

| Metric | Status | Location | Notes |
|--------|--------|----------|-------|
| F1/P/R @ 20m | ✅ | outputs/55maps-text-min-generalisation/evaluation/evaluation.md (table) + .json | F1 0.564 [0.550, 0.577], P 0.567, R 0.562 |
| F1 across buffers | ✅ | evaluation.md table rows (20/30/40/50 m) | Complete curve from 0.564 @ 20m to 0.680 @ 50m |
| Bootstrap CIs | ✅ | evaluation.json | 1000 iterations, 95% CIs, seed 42 |
| Paired permutation tests | ✅ | results/55maps-text-min-generalisation/paired-vs-high/ (vs text-high) | Multi-buffer pairwise comparison (20/30/40/50 m); p-values + effect sizes |
| Dawid-Skene | ✅ | results/55maps-text-min-generalisation/dawid-skene/ | Latent-truth posterior; item-posteriors.csv; VLM-only assessment |
| Cost manifest | ✅ | outputs/55maps-text-min-generalisation/cost_manifest.json | Full accounting: per-stage (proposer/verifier), per-map, unit costs ($0.0196/tile, $0.0310/detection) |
| Pre-launch audit | ✅ | configs/run-configs/55maps_text_min_generalisation_pre_launch_audit.md | Config validation against preregistration (§4.1.1 buffer protocol, thinking level, K-pass design) |
| Post-run report | ✅ | outputs/55maps-text-min-generalisation/post_run_report.md | Full narrative: top-line results (table), D-S correction (δF1 +0.024), cost breakdown (per-proposer-pass, token analysis), operational issues (e.g., edge exclusion), per-map extrema, reproducibility script, paper artefacts list |

**Exemplar Status**: This run meets all 8 deliverables. The post-run report explicitly notes the 1000-iteration bootstrap protocol, seed 42, tile-level resampling, and spatial matching buffer. Cost manifest shows cache-hit efficiency (90.2% cache hit rate saved ~$500). The pre-launch audit references specific decision numbers (E47, E52).

---

### Era 2: 55maps-text-high-generalisation (2026-04-10)

**Registered As**: 55-map Generalization Cohort 3 (text, HIGH thinking)  
**Primary Deliverable**: outputs/55maps-text-high-generalisation/, configs/run-configs/55maps_text_high_generalisation_*  
**Status**: **Near-gold-standard (post-run report location mismatch)**

| Metric | Status | Location | Notes |
|--------|--------|----------|-------|
| F1/P/R @ 20m | ✅ | evaluation.md + .json | F1 0.540 [0.524, 0.553] |
| F1 across buffers | ✅ | evaluation.md rows | 20/30/40/50 m curve |
| Bootstrap CIs | ✅ | evaluation.json | 1000 iterations, seed 42 |
| Paired permutation tests | ✅ | results/55maps-text-high-generalisation/paired-vs-min-* + paired-vs-high-* | Multiple comparators (vs min, vs min @20m, two-way @50m) |
| Dawid-Skene | ✅ | results/55maps-text-high-generalisation/dawid-skene/ | Posterior correction (δF1 +0.023) |
| Cost manifest | ✅ | outputs/55maps-text-high-generalisation/cost_manifest.json | Cost accounting present |
| Pre-launch audit | ✅ | configs/run-configs/55maps_text_high_generalisation_pre_launch_audit.md | Config audit present |
| Post-run report | ◐ | configs/run-configs/55maps_text_high_generalisation_post_run_report.md (not in outputs/) | Located in configs/, not outputs/. Content is comprehensive but organizational inconsistency vs image/min runs |

**Minor Issue**: Post-run report is in configs/run-configs/ instead of outputs/55maps-text-high-generalisation/—a filing inconsistency. Content quality is excellent; narrative includes cost accounting ($359.53), operational issues, and decision traceback.

---

### Era 2: 55maps-image-generalisation (2026-04-18)

**Registered As**: 55-map Generalization Cohort 4 (image, HIGH thinking)  
**Primary Deliverable**: outputs/55maps-image-generalisation/, configs/run-configs/55maps_image_generalisation_*  
**Status**: **Gold-standard (most recent)**

| Metric | Status | Location | Notes |
|--------|--------|----------|-------|
| F1/P/R @ 20m | ✅ | evaluation.md + .json | F1 0.506 [0.492, 0.520], P 0.512, R 0.500 |
| F1 across buffers | ✅ | evaluation.md rows | 20/30/40/50 m; primary buffer 50 m (per preregistration) |
| Bootstrap CIs | ✅ | evaluation.json | 1000 iterations, tile-level resampling, seed 42 |
| Paired permutation tests | ✅ | Results alongside text-high (paired cohort comparison) | Image-text modality comparison documented in working-notes Obs 255 |
| Dawid-Skene | ✅ | results/55maps-image-generalisation/dawid-skene/ | Latent-truth posterior (δF1 +0.024 after correction) |
| Cost manifest | ✅ | outputs/55maps-image-generalisation/cost_manifest.json | $364.70 total; detailed per-pass cost + token breakdown (including cached input: 621.3M tokens @ 91% hit rate) |
| Pre-launch audit | ✅ | configs/run-configs/55maps_image_generalisation_pre_launch_audit.md | Full config validation |
| Post-run report | ✅ | outputs/55maps-image-generalisation/post_run_report.md | Exemplary narrative covering operational issues (3 launcher-side bugs + recovery), timeline (UTC), per-map cost extrema, token accounting, reproducibility script, artefacts manifest |

**Exemplar Status**: Most recent and most detailed post-run report in the corpus. Includes granular operational logging (subprocess orphan, pass-skip check, safety-gate bug) with recovery descriptions—valuable for reproducibility. Cost manifest shows cache efficiency (91% hit rate) and per-worker concurrency tuning (60→250 workers, 40% wall-clock reduction).

---

## Statistical Completeness by Axis

### F1 Score (Primary Outcome)

- **Era 1 runs**: ✅ All major runs have F1 at some buffer (mostly 20 m)
- **Era 2 runs**: ✅ All have F1 at multiple buffers (20/30/40/50 m per preregistration §4.1.1)
- **Issue**: 55maps-generalisation (text-high) uses 50 m as primary (matching preregistration), while h8–h12 and retest use 20 m (pre-preregistration baseline)

### Bootstrap Confidence Intervals (Decision 10 / Protocol E52)

- **Era 1 runs**: ◐ Partial adoption
  - ✅ h10 (ICC reported), h11-384-pv-diagnostic, h12-v2, retest
  - ❌ h8-v2 (permutation p-values but no CIs)
- **Era 2 runs**: ✅ All 55-map runs use 1000 iterations, seed 42
- **Issue**: Pre-Era-2 runs used inconsistent bootstrap protocols (h10: ICC; retest: ~20-tile resampling vs later 1000-iteration standard)

### Paired Permutation Tests (Hypothesis Testing)

- **Era 1**: ✅ Present for h8-v2, h10, h12-v2, retest (tile-level pairwise permutation with p-values)
- **Era 2**: ✅ Present for all 55-map runs (multi-buffer pairwise matrices)
- **Strength**: The methodology is mature and consistently applied across both eras

### Dawid-Skene Latent-Truth Correction (E47)

- **Era 1**: ❌ Zero instances
- **Era 2**: ✅ Applied to all three 55-map text/image runs (shared analysis in results/dawid-skene/) **but not 55maps-generalisation (text-high, the first run)**
  - Retrospectively applied to text-high after min + image runs completed
  - Text-min and image both show δF1 = +0.024
- **Gap**: Decision to apply D-S was made post-facto (not pre-registered in run config), creating a slight methodological inconsistency with 55maps-generalisation

### Cost Manifests

- **Era 1**: ❌ Absent (pre-publication era; costs not budgeted or tracked)
- **Era 2**: ✅ Present for all three 55-map runs (min, high, image)
- **Breakthrough**: Introduction of cost-conscious launchers + context caching (April 2026) enabled fine-grained cost accounting as a standard publishable artefact

### Pre-Launch Audits

- **Era 1**: ❌ Zero instances (protocols were developed iteratively during runs)
- **Era 2**: ✅ Present for 55maps-text-min, 55maps-text-high, 55maps-image (3 of 4)
- **Missing**: 55maps-generalisation (first 55-map run, pre-formalized workflow)

### Post-Run Reports

- **Era 1**: ❌ Formal reports absent (narratives embedded in working-notes Observations)
- **Era 2**: ✅ Present for 55maps-text-min, 55maps-image (full structure); 55maps-text-high (in configs/); 55maps-generalisation (retrospective)

---

## Working-Notes Observation Cross-Reference

| Observation | Run | F1 | CIs | Paired | D-S | Cost | Pre | Post | Obs doc | Status |
|---|---|---|---|---|---|---|---|---|---|---|
| 238 | h8-v2 | ✅ | ◐ | ✅ | ❌ | ❌ | ❌ | ❌ | ✅ | Three-way null after BH-FDR; library-design axis closed |
| 155–200 | retest phases | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ | ◐ | ✅ | Comprehensive phase-by-phase; pairwise-bootstrap-comparisons.json |
| 250–251 | h11 two-stage | ◐ | ◐ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ | Pipeline exploration; diagnostic in results/h11-384-pv-diagnostic/ |
| 255 | 55maps-generalisation (text) | ◐ | ❌ | ❌ | ◐ | ❌ | ❌ | ◐ | ✅ | Retrospective; D-S applied post-hoc |
| 255 | 55maps-text-min | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | Gold-standard; vs-high paired test |
| 255 | 55maps-text-high | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | Text modality champion (F1 0.791 @ 50m); HIGH thinking cost-effective |
| 255 | 55maps-image | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | Image modality baseline (F1 0.771 @ 50m); −0.020 vs text |
| 256 | h12-v2 ratio | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ | ✅ | ✅ | HP:HN library ratio; analysis_summary.md exemplary |

---

## Gaps Summary Table

| Run | Missing Deliverables | Count | Severity | Reason |
|---|---|---|---|---|
| h8-v2 | Bootstrap CIs (formal), multi-buffer curve, pre-launch, post-run | 3–4 | **Medium** | Pre-formalized-workflow; results exist but unstructured |
| h10 | Multi-buffer curve, pre-launch, post-run | 3 | **Medium** | Methodologically sophisticated but no narrative synthesis |
| h11 | Paired comparison (proposer vs verifier), pre-launch, post-run, integration of "UNINTENDED" runs | 4 | **Medium-High** | Fragmentary results; unintended runs not flagged formally |
| h12-v2 | Multi-buffer curve, D-S (N/A but worth noting), cost manifest | 1–2 | **Low** | Single-hypothesis study; analysis_summary.md compensates |
| retest phases | Cost manifest, multi-buffer curve (except 50m for phase3a), pre-launch | 2–3 | **Low-Medium** | Internal development; strong narrative compensates |
| 55maps-generalisation | Pre-launch audit, bootstrap CIs, multi-buffer formal reporting, D-S applied pre-launch | 3–4 | **Medium** | First 55-map run; retrospective fixes applied |
| 55maps-text-high | Post-run location mismatch (configs/ vs outputs/), minor | 0–1 | **Low** | Content complete; filing issue only |
| 55maps-text-min | None | 0 | — | **Gold-standard** |
| 55maps-image | None | 0 | — | **Gold-standard** |

---

## Notes on Scope & Applicability

- **QGIS checks** (sanity-check, dedup-check, wbf-check): Not counted in primary audit; these are validation tools, not experimental runs
- **Archive directory**: Excluded per scope (e.g., `outputs/archive/`, `results/archive/`)
- **Consensus vs individual runs**: H11 and H12 include sub-stages (proposer, verifier, consensus) with no per-stage evaluation.json; evaluation lives in results/ directory as aggregates
- **Retest vs Phase 3 holdout**: retest runs are internal development; the "holdout" reference (Obs 155) refers to a separate holdout set (60 tiles) used in Phase 3 pilot
- **Paired tests**: "Comparator condition" for a run is context-dependent (e.g., h8-v2 vs baseline, h12-v2 three-way contrast, 55maps-min vs 55maps-high)

