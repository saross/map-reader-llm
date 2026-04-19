# Priority Backfill Plan — Results Documentation

**Plan Date**: 2026-04-18  
**Objective**: Close documentation gaps in support of paper submission (target: May 2026)  
**Constraint**: No re-runs; all backfill uses existing artefacts (results/, outputs/)

---

## TIER 1: PUBLICATION-BLOCKING (Must Close Before Submission)

### 1. 55maps-generalisation (text-high) — Add Pre-Launch Audit

**Current State**:
- Post-run report exists (retrospective, added 2026-04-14)
- Cost manifest missing ("unknown—ad-hoc first run")
- Pre-launch audit missing
- Dawid-Skene applied post-hoc (2026-04-14, not pre-registered)

**Backfill Action**:
1. Create `configs/run-configs/55maps_text_generalisation_pre_launch_audit.md` (retroactively)
   - Record the decision to proceed without formal audit ("first 55-map run; protocol formalized retrospectively")
   - Reference preregistration §4.1.1 (buffer 20 m primary, 50 m reported)
   - Acknowledge Dawid-Skene as post-hoc methodological addition (flag as "non-preregistered but justified")

2. Estimate cost manifest retroactively:
   - Launcher logs: check outputs/55maps-generalisation/launch_manifest.json for tile count + model
   - Formula: tiles × passes × cost_per_pass (use rates from 55maps-text-min as proxy: ~$0.02/tile/pass)
   - Insert "Cost estimate" section in post-run report with uncertainty bounds

**Effort**: 2–3 hours (archival + cost reconstruction)  
**Owner**: Shawn  
**Blockers**: None (all data exists; no recomputation needed)

---

### 2. h11 Two-Stage Design — Integrate Pipeline Results

**Current State**:
- 12 sub-runs across outputs/h11/ with no unified narrative
- Two "UNINTENDED-T1.0" runs marked but not formally excluded
- Threshold sweeps in results/h11-384-pv-diagnostic/ (bootstrap CIs present!)
- No paired (proposer vs verifier) statistical comparison
- No post-run report tying stages together

**Backfill Action**:
1. **Exclude "UNINTENDED" runs formally**:
   - Create a note in results/h11-384-pv-diagnostic/README.md explaining T=1.0 bug and decision to exclude
   - Mark outputs/h11/{single-pass-384-UNINTENDED-T1.0, consensus-384-UNINTENDED-T1.0} as "failed—see note"

2. **Compute paired proposer vs verifier test**:
   - Extract proposer detections from outputs/h11/proposer-verifier-384/run_*/
   - Extract verifier detections from outputs/h11/proposer-verifier-384/verified/
   - Use tile-level permutation test (matching h12-v2 protocol): tile_f1(prop) vs tile_f1(verif)
   - Record p-value + effect size in results/h11-384-pv-diagnostic/proposer_vs_verifier.json
   - Script: scripts/pairwise_permutation_test.py (already exists)

3. **Write post-run narrative**:
   - outputs/h11/post_run_report.md
   - Sections: objective (two-stage pipeline exploration), design (5 passes, 384px), stages (proposer F1→verifier F1), key finding (proposer vs verifier comparison: statistically tied / directionality?), implications
   - Reference working-notes Obs 250–251

**Effort**: 4–6 hours (permutation test computation + narrative)  
**Owner**: Shawn  
**Blockers**: Proposer/verifier breakout requires parsing outputs carefully

---

### 3. 55maps-generalisation — Harmonize with Min/High/Image Cohorts

**Current State**:
- Dawid-Skene results exist (results/dawid-skene/dawid-skene-results.md, shared across all cohorts)
- Post-run narrative exists but references different decision-point (April 10 vs April 15/18)
- No bootstrap-CIs (compute? or leave as-is due to retrospective status?)

**Backfill Action**:
1. **Decision point**: Should 55maps-generalisation have 1000-iter bootstrap CIs retroactively computed?
   - Option A (preferred): "This run predates bootstrap-CI protocol; reported as-is with flag"
   - Option B: Compute CIs now (requires re-evaluation script run)
   - **Recommendation**: Option A (document the methodological timeline; don't retrofit)

2. **Update post-run report**:
   - Add note: "Completed 2026-04-10 before bootstrap-CI protocol formalization. D-S correction applied post-hoc (2026-04-14) using unified annotation model with text-min and text-high cohorts. See results/dawid-skene-results.md."
   - Clarify buffer choices: primary buffer = 50 m (per preregistration); 20/30/40 reported for completeness

3. **Cross-reference in 55maps-text-min and 55maps-image post-run reports**:
   - Link to text-high as "Cohort 1" (earliest, higher-latency model; retrospective D-S)
   - Explain why D-S is shared across cohorts (2-annotator limit requires pooling)

**Effort**: 1–2 hours (documentation only)  
**Owner**: Shawn  
**Blockers**: None

---

## TIER 2: METHODOLOGICAL SUPPORT (Strengthen Paper Arguments)

### 4. h8-v2 Library Composition — Multi-Buffer Curves

**Current State**:
- F1 at 20 m present (results/h8-v2/greedy/threshold_sweep.json)
- No 30/40/50 m curves
- Permutation tests present (pairwise/)
- Narrative: Obs 238 (three-way null after BH-FDR)

**Backfill Action**:
1. **Compute F1/P/R at 30/40/50 m**:
   - Use scripts/evaluate_detections.py with buffers [30, 40, 50]
   - Requires greedy consensus GeoJSONs (outputs/h8-v2/greedy/consensus_t*.geojson) + ground truth
   - Output: results/h8-v2/greedy/buffer_sensitivity.{json,csv}

2. **Test whether null holds across buffers**:
   - Plot F1 curve across buffers for each condition
   - Check if interaction exists (library effect size depends on buffer?)
   - Update Obs 238 / write appendix note if pattern differs by buffer

3. **Minimum viable narrative**:
   - Create results/h8-v2/buffer_analysis.md summarizing curve shapes + null stability

**Effort**: 2–3 hours (evaluation script + analysis)  
**Owner**: Shawn  
**Timeline**: Low priority (h8 closes a research axis; curves are confirmatory, not hypothesis-testing)

---

### 5. h10 Calibration Pool — Multi-Buffer + Narrative

**Current State**:
- Comprehensive statistical analysis (results/h10/statistical_analysis.json, sweep_results.json, verifier_independence_probe.md)
- Missing: 30/40/50 m buffer curves
- Missing: Post-run narrative integrating pool-size effect with verifier calibration

**Backfill Action**:
1. **Compute multi-buffer sweeps**:
   - Similar to h8-v2: evaluate_detections.py at [20, 30, 40, 50]
   - Results: results/h10/buffer_sensitivity.{json,csv}

2. **Test pool-size effect across buffers**:
   - Does larger pool (more examples) help more at tight buffers or loose buffers?
   - Check ICC stability (should stay high ~0.93 across all buffers)

3. **Write h10 post-run narrative** (outputs/h10/post_run_report.md):
   - Objective: calibration pool size for verifier (H10 hypothesis)
   - Design: 4 pool sizes, per-config threshold sweeps
   - Results: pool-size effect null at 20 m; curves at 30/40/50 m
   - Verifier independence: ICC=0.93, full pairwise correlation table
   - Implication: verifier is robust to example-set size; limits over-fitting risk

**Effort**: 3–4 hours  
**Owner**: Shawn  
**Timeline**: Medium priority (methodological rigor; h10 is cited in paper as "calibration validation")

---

### 6. h12-v2 — Multi-Buffer Curves + Cost Estimate

**Current State**:
- Excellent analysis_summary.md (threshold sweeps, FDR correction, directional patterns)
- Missing: 30/40/50 m curves (only t=1..5 at 20 m reported)
- Missing: Formal cost manifest (only "~$34.00 meta-reported")

**Backfill Action**:
1. **Compute multi-buffer sweeps** (3 conditions × 5 thresholds × 4 buffers = 60 evaluation runs):
   - Script: scripts/evaluate_detections.py --sweep-thresholds --sweep-buffers
   - Output: results/h12-v2/{greedy,wbf}/buffer_sensitivity.{json,csv}

2. **Re-test three-way null at each buffer**:
   - Run 3 pairwise permutation tests (R12, R23, R13) at each buffer
   - Apply BH-FDR correction pooled across buffers (15 tests total; q=0.05)
   - Check: does null hold robustly? Or is H12 significant at loose buffers?

3. **Reconstruct cost manifest**:
   - Query launcher logs: outputs/h12-v2/*/launch_manifest.json
   - Aggregate: Σ(cost per tile) × tiles across r1-hn-heavy + r3-hp-heavy (r2 reused from h10)
   - Estimate: ~$34 (r1 + r3 = ~2×$17); document as "meta-reported + reconstructed"

**Effort**: 3–4 hours  
**Owner**: Shawn  
**Timeline**: Medium priority (h12 is major hypothesis test; multi-buffer check strengthens null claim)

---

## TIER 3: DEVELOPMENT RUNS (Archive or Flag)

### 7. h11 "UNINTENDED" Runs — Archive Decision

**Action**: 
- Formally decide: Archive or exclude?
- If archive: Move outputs/h11/{single-pass-384-UNINTENDED-T1.0, consensus-384-UNINTENDED-T1.0} to outputs/archive/h11/
- If exclude: Add .gitignore entry + README note
- **Recommendation**: Archive (preserve reproducibility; flag in README)

**Effort**: 0.5 hours

---

### 8. h10 & h11 Exploratory Sub-Runs

**Runs**:
- h10: hard-cases-v2, example-pools-v2, verifier-crops (hard-example mining; no evaluation needed)
- h11: gold-standard-v2, n1-outstanding-384 (gold-standard generation; no evaluation needed)

**Action**:
- Create outputs/{h10,h11}/mining/README.md explaining purpose (hard-example mining for later library enrichment)
- No evaluation needed; document as "exploratory data collection"

**Effort**: 1 hour

---

### 9. retest Phase 3c Diversity Study

**Current State**:
- Minimal documentation (only outputs/retest/phase3c/)
- No evaluation.json; no post-run narrative

**Action**:
- **If relevant to paper**: Compute evaluation.json and write post-run narrative
- **If exploratory only**: Create outputs/retest/phase3c/README.md explaining scope (diversity study, not in main analysis path)

**Effort**: 1–2 hours (depends on relevance)

---

## Implementation Schedule

| Priority | Task | Owner | Start | End | Effort (h) | Blocker? |
|---|---|---|---|---|---|---|
| **T1** | 55maps-generalisation pre-launch audit | Shawn | 2026-04-18 | 2026-04-19 | 2–3 | NO |
| **T1** | h11 post-run narrative + proposer vs verifier test | Shawn | 2026-04-19 | 2026-04-21 | 4–6 | NO |
| **T1** | 55maps-generalisation harmonization | Shawn | 2026-04-22 | 2026-04-22 | 1–2 | NO |
| **T2** | h8-v2 multi-buffer curves | Shawn | 2026-04-23 | 2026-04-24 | 2–3 | NO |
| **T2** | h10 multi-buffer + narrative | Shawn | 2026-04-24 | 2026-04-26 | 3–4 | NO |
| **T2** | h12-v2 multi-buffer + permutation retests | Shawn | 2026-04-26 | 2026-04-28 | 3–4 | NO |
| **T3** | Archive decisions (UNINTENDED runs) | Shawn | 2026-04-29 | 2026-04-29 | 0.5 | NO |
| **T3** | Mining runs README + phase3c decision | Shawn | 2026-04-29 | 2026-04-30 | 1–2 | NO |

**Total Effort**: ~18–25 person-hours  
**Timeline**: 1–2 weeks (non-blocking to paper submission if Tier 1 completes by 2026-04-22)

---

## Validation Checklist (Post-Backfill)

- [ ] All 59 runs have at least F1/P/R at 20 m buffer documented
- [ ] All hypothesis-testing runs (H8, H10, H11, H12, 55-maps) have paired permutation tests with p-values
- [ ] All production runs (55-maps) have post-run reports + pre-launch audits + cost manifests
- [ ] All runs with >10 tiles have bootstrap CIs (1000 iterations, seed 42) or explicit rationale for absence
- [ ] No runs labeled "UNINTENDED" remain active; flagged or archived
- [ ] All Dawid-Skene results (55-maps cohorts) are documented with shared methodology notes
- [ ] Working-notes observations are cross-referenced to runs (forward-referencing: "see results/")

---

## Ongoing Standards (Post-Backfill)

**For all future runs**:
1. Pre-launch audit (configs/run-configs/{run}_pre_launch_audit.md)
2. Post-run report (outputs/{run}/post_run_report.md) within 24 hours of completion
3. Evaluation at all buffers (20/30/40/50 m) with bootstrap CIs (1000 iter, seed 42)
4. Paired permutation tests for any multi-condition design (p-values + effect size)
5. Cost manifest (automated by launcher; review for accuracy)
6. Working-notes observation (if hypothesis-testing run; reference other run's working-notes)

