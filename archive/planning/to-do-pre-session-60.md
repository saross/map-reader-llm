# To-Do Items

## Urgent

- [x] **Document Phase 2e carry-forward parameters** — Phase 2e (H4 ordering)
  was executed in Session 33 (2026-02-12) with result "no significant ordering
  effect after FDR correction; config-default ordering carried forward." Results
  are in the session log and git history (commits `8f34ed4`, `de6ac2e`,
  `8118eb5`, `7a038b6`) but no `results/phase2e-carry-forward-parameters.md`
  was created. Needed for completeness alongside the 2a–2d carry-forward docs.
  *(Completed 2026-03-09, Session 43)*

## Pending

### Next Session: Systematic Review and Remaining Work

**Priority**: Start of next session — before launching new runs.

The project is in the final experimentation stages before write-up.
Next session should begin with a systematic review of what's done and
what remains, covering both API runs and local analyses.

#### Immediate priorities (in order)

1. **Commit all Session 57 changes** — bug fixes (22), errata updates,
   renamed directories, new analysis results, audit reports
2. **Audit correctives** — rename T=1.0 directories, re-run single-pass
   at T=0.0, regenerate stale pairwise JSONs, update Obs 186–187
3. **Complete PV baseline** — run Flash minimal verifier on the 5
   conditions with crops ready (22,088 candidates, ~$1.23 Batch API)
4. **Buffer distance sensitivity** — re-evaluate top conditions at
   30, 40, 50 m (sapphire, no API)
5. **Review gap matrix** — what comparisons are needed for the paper?

#### Remaining API work

- PV baseline verifier runs (5 conditions, Flash minimal) — crops ready
- Proposer × Verifier model matrix: 10 new verifier runs needed (4
  Pro verifier on baselines, 4 on HIGH consensus, 2 thinking experiments)
- Re-run single-pass-384 at T=0.0 (10 runs, ~$0.50)
- Phase 3c H9 diversity Track 1 completion (nohup'd, check status)

#### Remaining local analysis (sapphire, no API)

- PV threshold derivation + sweep for each new verifier run
- PV pairwise comparisons (after PV pipeline done)
- Buffer distance sensitivity (30, 40, 50 m)
- Phase 3c H9 diversity analysis
- Update bootstrap-cis-384px.json
- Write findings summary for working notes
- Produce complete gap matrix for paper

---

### Session 56 Follow-Up: Analyse Completed Batch Runs

**Priority**: High — ~~do at start of next session~~ mostly complete.

**Context**: Session 56 submitted multiple batch API runs that should be
complete by next session. All local analysis MUST run on sapphire.

#### Check completion and patch failures

- [x] **Verify all proposer runs completed** — *(Completed 2026-03-25, Session 57)*
  - `flash-high-text-n5`: 30/30 complete (batch resumed overnight, all 487 tiles OK)
  - `flash-high-image-n5`: 10/10 complete
  - `pro-high-image-n5`: 5/5 complete
  - `flash-minimal-text-n30-t07`: 30/30 complete
  - Phase 3c H9 diversity Track 1: 117/125 complete, batch resumed with nohup
- [x] **Patch any tile failures** — no tile failures found in any condition
  (all runs: 487/487 tiles succeeded) *(Verified 2026-03-25, Session 57)*

#### Simple consensus sweeps (sapphire, no API)

- [x] **Flash HIGH text N=5/10/30 sweeps** — *(Completed 2026-03-25, Session 57)*
  N=5: F1=0.776 (5-of-5, replicates). N=10: F1=0.805 (9-of-10). N=30: F1=0.814
  (26-of-30, best consensus result). See `results/h11-384-consensus-flash-high-text-n30/`
- [x] **Flash HIGH image N=5/10 sweep** — *(Completed 2026-03-24, Session 57)*
  N=5: F1=0.730 (3-of-5). N=10: F1=0.752 (7-of-10).
  See `results/h11-384-consensus-flash-high-image-n10/`
- [x] **Pro HIGH image N=5 sweep** — *(Completed 2026-03-24, Session 57)*
  F1=0.703 (3-of-5). See `results/h11-384-consensus-pro-high-image-n5/`
- [x] **Flash MINIMAL text N=5/10/30 sweeps at T=0.7** — *(Completed 2026-03-24, Session 57)*
  N=5: F1=0.637 (5-of-5). N=10: F1=0.633 (10-of-10). N=30: F1=0.657 (29-of-30).
  See `results/h11-384-consensus-flash-minimal-text-t07/`
- [x] **Flash MINIMAL text N=5/10/30 sweeps at T=1.0** — *(Completed 2026-03-25, Session 57)*
  N=5: F1=0.644 (5-of-5, replicates). N=10: F1=0.624 (9-of-10). N=30: F1=0.637 (28-of-30).
  See `results/h11-384-consensus-flash-minimal-text-t10/`
- [x] **Flash MINIMAL image N=5/10 sweep** — *(Completed 2026-03-25, Session 57)*
  N=5: F1=0.658 (4-of-5). N=10: F1=0.680 (8-of-10, replicates).
  See `results/h11-384-consensus-flash-minimal-image/`

#### PV pipeline (Batch API verifier + sapphire evaluation)

For each condition, the pipeline is: generate 1-of-N union → extract crops →
run verifier (Batch API) → derive x-of-N results → threshold sweep (sapphire).

Use the `derive_vote_threshold_results.py` script to derive x-of-N results
from a single 1-of-N union verifier run (saves ~80% of verifier API calls).

**Verifier jobs already complete** (derive thresholds + evaluate on sapphire):
- [x] **Flash HIGH text N=5 + Flash PV** — *(Completed 2026-03-25, Session 57)*
  Best: 4-of-5 at t=0.15, F1=0.864 [0.833, 0.893], P=0.915, R=0.818.
  Full sweep at all 5 vote thresholds. See `results/h11-384-pv-diagnostic/flash-high-text-*of5/`
- [x] **Pro HIGH text N=5 + Flash PV** — *(Completed 2026-03-25, Session 57)*
  **NOTE**: Verifier used Flash (gemini-3-flash, thinking=medium), NOT Pro.
  Config hardcodes Flash; `--model` override was not passed. See errata below.
  Best: 3-of-5 at t=0.05, F1=0.850 [0.812, 0.883], P=0.954, R=0.766.
  See `results/h11-384-pv-diagnostic/pro-high-text-*of5/`

#### Verifier model error (discovered Session 57)

**All verifier runs used gemini-3-flash** — confirmed via `cost_estimate.
pricing_used.model` in every run.meta.json (31 verified directories).
The "medium-verifier" runs (formerly labelled "pro-verifier") used Flash
with `thinking=medium`, not Pro. The verifier config hardcodes Flash and
`--model gemini-3.1-pro` was never passed for any verifier invocation.

These runs are still valuable as a **verifier thinking-level comparison**
(Flash minimal vs Flash medium, p=0.001 on text), but the intended
proposer × verifier model matrix is incomplete.

#### Proposer × Verifier model matrix (Batch API)

**Intended 2×2 matrix** across Flash and Pro for both proposer and
verifier stages, on single-pass baseline data (text + image tracks):

**Text track (single-pass proposer baseline):**

|  | Flash verifier (minimal) | Flash verifier (medium) | Pro verifier (medium) |
|--|--------------------------|------------------------|-----------------------|
| **Flash proposer** | ✓ `text-baseline` | ✓ `flash-minimal-text-medium-verifier` | ✗ MISSING |
| **Pro proposer** | ✓ `pro-text-minimal-verifier` | ✓ `pro-text-medium-verifier` | ✗ MISSING |

**Image track (single-pass proposer baseline):**

|  | Flash verifier (minimal) | Flash verifier (medium) | Pro verifier (medium) |
|--|--------------------------|------------------------|-----------------------|
| **Flash proposer** | ✓ `image-baseline` | ✓ `flash-minimal-image-medium-verifier` | ✗ MISSING |
| **Pro proposer** | ✓ `pro-image-minimal-verifier` | ✓ `pro-image-medium-verifier` | ✗ MISSING |

**HIGH consensus (text, N=5 1-of-5 union):**

|  | Flash verifier (minimal) | Flash verifier (medium) | Pro verifier (medium) |
|--|--------------------------|------------------------|-----------------------|
| **Flash HIGH** | ✓ `flash-high-text-1of5` | ✗ MISSING | ✗ MISSING |
| **Pro HIGH** | ✗ MISSING | ✓ `pro-high-text-1of5` | ✗ MISSING |

**New verifier runs needed** (all use `--model gemini-3.1-pro
--thinking-level medium` for Pro verifier; Batch API):

Single-pass baseline matrix (4 runs):
- [ ] **Flash text baseline + Pro verifier** — reuse existing crops
  from `crops/text-baseline/`
- [ ] **Flash image baseline + Pro verifier** — reuse existing crops
  from `crops/image-baseline/`
- [ ] **Pro text baseline + Pro verifier** — reuse existing crops
  from `crops/pro-medium-text-baseline/`
- [ ] **Pro image baseline + Pro verifier** — reuse existing crops
  from `crops/pro-medium-image-baseline/`

HIGH consensus matrix (4 runs):
- [ ] **Flash HIGH text N=5 + Pro verifier** — reuse crops from
  `crops/flash-high-text-1of5/`
- [ ] **Flash HIGH text N=5 + Flash medium verifier** — reuse crops,
  `--thinking-level medium`
- [ ] **Pro HIGH text N=5 + Pro verifier** — reuse crops from
  `crops/pro-high-text-1of5/`
- [ ] **Pro HIGH text N=5 + Flash minimal verifier** — reuse crops,
  fills the gap in the HIGH consensus matrix

Verifier thinking experiments (2 runs):
- [ ] **Flash HIGH text N=5 + Flash HIGH verifier** — `--thinking-level
  high`, test whether HIGH thinking helps the verifier on consensus-
  filtered candidates (prior Obs 185 suggests it may hurt on noisier data)

**Need full PV pipeline** (consensus union → crops → verifier → derive → eval):
- [ ] **Flash HIGH image N=5 + Flash PV**
- [ ] **Flash HIGH image N=10 + Flash PV** (union approach)
- [ ] **Flash HIGH text N=10 + Flash PV** (union approach)
- [ ] **Flash HIGH text N=30 + Flash PV** (union approach)
- [ ] **Pro HIGH image N=5 + Pro PV** (`--model gemini-3.1-pro --thinking-level medium`)
- [ ] **Flash MINIMAL text T=0.7 N=5/10/30 + Flash PV** (union approach for each)

#### Pairwise comparisons (sapphire, no API)

Run on sapphire with `--bounds inputs/vectors/bounds/384/full_evaluation_bounds.geojson`.
Use `paired_permutation_consensus.py` with `--bounds` flag.

**Already done** (session 56, 487 tiles):
- Flash HIGH vs Flash MINIMAL text: dF1=+0.149, p<0.0001 ***
- Pro HIGH vs Flash MINIMAL text: dF1=+0.150, p<0.0001 ***
- Pro HIGH vs Flash HIGH text: dF1=+0.002, p=0.874 ns
- Flash HIGH vs Flash MINIMAL image: dF1=+0.009, p=0.324 ns

**Completed Session 57** (2026-03-25, 16 new comparisons, 20 total):
- [x] Flash HIGH image vs Pro HIGH image N=5: dF1=-0.028, p=0.018 * (Flash better)
- [x] Flash HIGH vs MINIMAL T=0.7 text N=5: dF1=-0.016, p=0.131 ns
- [x] Flash HIGH vs MINIMAL T=0.7 text N=10: dF1=+0.018, p=0.059 ns (trend)
- [x] Flash HIGH vs MINIMAL T=0.7 text N=30: dF1=+0.016, p=0.094 ns (trend)
- [x] Pro HIGH vs MINIMAL T=0.7 text N=5: dF1=-0.014, p=0.165 ns
- [x] Flash HIGH text vs image N=5: dF1=-0.009, p=0.432 ns
- [x] Flash HIGH text vs image N=10: dF1=+0.019, p=0.083 ns (trend)
- [x] Pro HIGH text vs image N=5: dF1=+0.021, p=0.111 ns
- [x] Flash HIGH text N=10 vs N=5: dF1=+0.016, p=0.025 *
- [x] Flash HIGH text N=30 vs N=10: dF1=-0.001, p=0.852 ns
- [x] Flash HIGH vs MINIMAL image N=10: dF1=+0.002, p=0.867 ns
- [x] MINIMAL T=0.7 vs T=1.0 text N=5: dF1=+0.164, p<0.0001 ***
- [x] MINIMAL T=0.7 vs T=1.0 text N=10: dF1=+0.143, p<0.0001 ***
- [x] MINIMAL T=0.7 vs T=1.0 text N=30: dF1=+0.151, p<0.0001 ***

**Still needed**:
- [ ] **PV pairwise comparisons** — repeat key comparisons using PV-filtered
  results (after PV pipeline is done)

#### T=0.7 vs T=1.0 comparison (unexpected data from bug)

Per the "unexpected data as discovery opportunities" policy: the original
consensus-384 text runs executed at T=1.0 (bug), and the corrected re-run
provides T=0.7. Both are N=30, MINIMAL thinking, 384px — identical except
temperature. This is an unplanned but free comparison of consensus
temperature at the optimal tile size.

- [x] **Compare Flash MINIMAL text N=30 at T=0.7 vs T=1.0** —
  *(Completed 2026-03-25, Session 57)*. T=0.7 dramatically better than
  T=1.0 at all pool sizes: N=5 dF1=+0.164 (p<0.0001), N=10 dF1=+0.143
  (p<0.0001), N=30 dF1=+0.151 (p<0.0001). Not a subtle effect — T=0.7
  wins 94-101 tiles vs 12-19 losses. The temperature bug hid ~15 F1
  points of performance. **Add to paper as sensitivity analysis.**
- [x] **If interesting, add to paper** — YES, highly significant.
  Consensus sweeps for both temperatures at N=5/10/30 complete.
  See `results/h11-384-consensus-flash-minimal-text-t07/` and
  `results/h11-384-consensus-flash-minimal-text-t10/`.

#### 512px PV pipeline (low priority)

Proposer data exists from Phase 3a. Needs verifier batch jobs + sapphire eval.

- [ ] **512px Flash MINIMAL text N=5 + Flash PV**
- [ ] **512px Flash MINIMAL image N=5 + Flash PV**
- [ ] **512px Flash HIGH text N=5 + Flash PV**
- [ ] **512px Flash HIGH image N=5 + Flash PV**

#### Phase 3c H9 Diversity analysis

- [x] **Verify Phase 3c H9 Track 1 complete** — 125/125 units, 0 failures.
  *(Completed 2026-03-25, Session 58)*
- [x] **Run diversity analysis** — both Track 1 (image) and Track 2 (text)
  re-analysed on sapphire. Results in `results/phase3c-diversity/`.
  *(Completed 2026-03-25, Session 58)*
- [ ] **Compare with Phase 3c Track 2** (text, already complete from prior session)

#### Buffer distance sensitivity analysis (sapphire, no API)

All experiments to date used a strict 20 m spatial matching buffer. For
the paper and for practical deployment, we should also report metrics at
relaxed thresholds. At 384px tile size with ~15 px symbols, 40–50 m
corresponds to ~10–12 px — a reasonable "hit" radius for production use.

- [x] **Re-evaluate high-performing conditions at 30, 40, and 50 m buffers** —
  *(Completed 2026-03-25, Session 58)*. 15 runs on sapphire (5 conditions
  × 3 buffers). Results in `results/h11-384-buffer-sensitivity/`. Key finding:
  image tracks gain 0.09–0.15 F1 from 20→50m; text tracks gain only 0.01.
  See Obs 190 for distance distribution analysis. PV buffer sensitivity
  deferred — `evaluate_pv_results.py` lacks `--buffer-metres` support.
- [ ] **Report as sensitivity table in paper** — one table showing F1/P/R
  at 20, 30, 40, 50 m for the top conditions.
- [ ] **Create standalone PV buffer sensitivity script** —
  `scripts/analyse_pv_buffer_sensitivity.py` that takes a verified PV
  output dir (probabilities.json + candidate_manifest.json), a threshold,
  and evaluates at multiple buffer distances (default 20, 30, 40, 50 m).
  Keep `evaluate_pv_results.py` focused on threshold sweeps; buffer
  sensitivity is a separate analytical concern. Should support batch mode
  (multiple conditions in one invocation) for the paper sensitivity table.

#### Consolidation and review

- [ ] **Update bootstrap-cis-384px.json** with all new PV results
- [x] **Write session 56–57 key findings summary** — Obs 191 added to
  working notes. *(Completed 2026-03-25, Session 58)* Content:
  - HIGH thinking is the key differentiator for consensus
  - Pro HIGH text N=5 F1=0.849 (genuine Pro, confirmed via deep dive);
    Flash HIGH text N=5 F1=0.776 — Pro outperforms at N=5 but pairwise
    test ns (p=0.874) at tile level
  - Flash HIGH text N=30 consensus F1=0.814 is best consensus-only result
  - Flash HIGH text 4-of-5 + Flash PV F1=0.864 is best overall result
  - Pro HIGH text 3-of-5 + Flash PV F1=0.850 — Pro close but Flash wins
  - Medium thinking significantly helps Flash verifier (p=0.001)
  - True Pro verifier never tested (all verifiers used Flash)
  - T=0.7 >> T=1.0 at all pool sizes (dF1 ~+0.15, p<0.0001)
  - single-pass-384 also has T=1.0 bug (newly discovered in audit)
  - Metadata bug in `lib_llm_metadata.py` — `configuration.model` field
    was unreliable when `--model` override used (fixed Session 57)
- [ ] **Review**: do we have all comparisons needed for the paper? Produce a
  complete matrix of what exists and what gaps remain

#### API cost retrospective

- [ ] **Estimate savings from context caching and Batch API** — Retrospective
  cost analysis for the paper. Parse all `cost_estimate` fields from `.meta.json`
  files across the project to compute (a) actual spend, (b) what Batch API saved
  vs real-time, (c) what context caching *would have* saved on image-track runs
  (90% discount on ~4,400 cacheable input tokens per call), (d) what the
  combined optimal strategy (Batch API + context caching where available) would
  have cost. Report as a table in the paper's cost analysis section. See Obs 199.

#### Preregistered statistical analyses (outstanding)

- [ ] **Tile-level MCC (Matthews Correlation Coefficient)** — preregistered
  secondary outcome (Section 3.5, narrative-summary.md). Binary tile-level
  classification: does the tile contain mounds or not? Compute for all
  top conditions (consensus-only and PV). Addresses the practical question
  "can the method identify when there's nothing to find?" Run on sapphire.
- [ ] **FDR correction (q=0.05) across all pairwise comparisons** —
  preregistered requirement (execution-plan.md, multiple references).
  Apply Benjamini-Hochberg False Discovery Rate correction across all
  pairwise permutation tests within each analysis family. Currently 17+
  tests without correction; some p-values near significance thresholds
  may not survive. The `bootstrap_effect_size_ci()` function already
  supports `return_p_values=True` for FDR input. Run on sapphire.

### Comprehensive Run Audit

- [x] **Audit all completed runs against preregistration and carry-forward
  values** — *(Completed 2026-03-25, Session 57)*. Audited 1,740 runs
  across 239 conditions. See `reports/configuration-audit-2026-03-25-v2.md`.
  Key findings:
  - E42 was a misdiagnosis: `configuration.model` metadata field is
    unreliable due to bug in `lib_llm_metadata.py`. Pro proposer runs
    genuinely used gemini-3.1-pro-preview (confirmed via GeoJSON features,
    cost_estimate, and logs). All verifier runs used Flash (confirmed).
  - consensus-384 T=1.0 bug: confirmed, corrected replacement verified
  - **single-pass-384 T=1.0 bug (NEW)**: 10 runs at T=1.0 not T=0.0
  - Phase 3a "-high" mislabelling: 180 runs, known and documented
  - 12 runs used Pro (proposers only); 1,728 used Flash
  - 173/174 multi-run conditions internally consistent
  - 3 pairwise comparisons confounded by T=1.0 bug

### Audit Correctives (from Session 57 audit)

**Priority**: High — complete before writing paper results sections.

#### Temperature bug correctives

- [x] **Rename consensus-384 to clearly indicate T=1.0 error** — renamed
  to `outputs/h11/consensus-384-UNINTENDED-T1.0/` with README.md. Pairwise
  JSON paths updated (3 files). Protocol errata E43 added.
  *(Completed 2026-03-25, Session 58)*
- [x] **Rename single-pass-384 to clearly indicate T=1.0 error** — renamed
  to `outputs/h11/single-pass-384-UNINTENDED-T1.0/` with README.md.
  Protocol errata E44 added. Corrected T=0.0 rerun in progress at
  `outputs/retest/h11-single-pass-384-t0/`.
  *(Completed 2026-03-25, Session 58)*
- [ ] **Re-run single-pass-384 at T=0.0** — 10 runs, Flash MINIMAL,
  T=0.0, 384px. This is the deterministic single-pass baseline needed
  for the tile-size comparison. Estimated cost: ~$0.50 via Batch API.
  Use explicit `--temperature 0.0` on CLI to avoid config default.

#### Pairwise comparison fixes

- [x] **Regenerate 3 confounded pairwise comparisons** — audit found both
  confounded comparisons already superseded by corrected `*-t0.7-*`
  versions (Session 57). Superseded files archived to
  `archive/superseded-pairwise/`. 3 intentional T=0.7 vs T=1.0
  comparisons confirmed correct (they use consensus-384 AS T=1.0 data).
  *(Verified and archived 2026-03-25, Session 58)*
- [x] **Regenerate stale pairwise JSON files** — comprehensive audit of
  all 19 pairwise JSONs found no stale `study_dir` paths. All paths
  resolve to existing directories. E42 rename cycle did not leave stale
  references. *(Verified 2026-03-25, Session 58)*

#### Documentation updates

- [x] **Update working notes Obs 186–187** — verified already correct.
  Both observations were corrected in-session after E42 deep dive
  confirmed Pro genuine. Content accurately describes Flash vs Pro
  findings. *(Verified 2026-03-25, Session 58)*

#### Minor cleanup
- [x] **Complete 6 incomplete retest Phase 3c runs** — all picked up by
  nohup'd diversity resumption. Final batch completed 125/125 units,
  0 failures. *(Completed 2026-03-25, Session 58)*
- [ ] **Add defensive model check to run_phase2.py and run_pv.py** — when
  a study YAML or directory name implies a specific model (e.g., "pro"),
  verify the resolved model name matches before proceeding. Prevents
  recurrence of E42.

### Code Audit Bug Fixes (Session 57)

- [x] **All 22 bugs fixed** *(Completed 2026-03-25, Session 57)*:
  4 critical (C1–C4), 9 medium (M1–M9), 9 low (L1–L9). Linting clean,
  tier1 tests pass (13 pre-existing failures unrelated to changes).
  Files modified: `lib_llm_metadata.py`, `lib_batch_api.py`, `run_pv.py`,
  `run_phase2.py`, `4_detect_mounds_batch.py`, `5_verify_crops.py`,
  `derive_vote_threshold_results.py`, `extract_candidates.py`,
  `merge_passes.py`, `paired_permutation_consensus.py`,
  `evaluate_pv_results.py`.

### Two-Stage Pipeline Optimisation (Post Phase 3d Pilot)

**Context**: Phase 3d pilot showed two-stage proposer→verifier architecture
achieves F1=0.711 (image) / 0.796 (text) with adversarial verifier,
substantially exceeding single-stage baselines. These tasks explore how
to push performance further with purpose-built proposer and verifier
configurations.

#### Free analyses (no API calls)

- [x] **Plot precision-recall curves** from existing Phase 3d pilot probability
  data — reveals optimal thresholds more precisely than 0.1-step grid, and
  visualises the trade-off space for each verifier strategy × track.
  *(Completed 2026-03-09, Session 44)*. Results: adversarial verifier
  optimal at t=0.21 (image F1=0.711) and t=0.16 (text F1=0.796);
  standard/checklist are step functions due to bimodal distributions.
  See `results/figures/phase3d-pr-curves.png` and `results/phase3d-pr-curves.csv`
- [x] **Cross-modal overlap analysis** — match Phase 3d proposer outputs (132
  image candidates, 140 text candidates) to ground truth. *(Completed
  2026-03-09, Session 44)*. Key finding: **union recall = 0.866 (84/97)**;
  65 mounds found by both, 6 image-only, 13 text-only, 13 by neither.
  Cross-modal union proposer is strongly supported.
  See `results/figures/phase3d-cross-modal-venn.png`
- [x] **Multi-verifier ensemble** (revised from "reconstruct consensus") —
  original item was wrong: pilot had K=1 verifier passes, not K=10.
  Instead tested ensemble of 3 verifier strategies (average, majority,
  union vote). *(Completed 2026-03-09, Session 44)*. Finding: standard
  and checklist are 100% redundant on image track; ensemble adds marginal
  +0.007 F1 over adversarial alone. Not worth pursuing.

#### Low-cost experiments (~$7 each)

- [ ] **Pilot high-recall text proposer** — T=0.7, HIGH thinking,
  recall-biased prompt ("flag anything plausible"), no negative examples,
  single pass; target: recall > 0.85 even at precision ~0.35
- [ ] **Pilot high-recall image proposer** — same approach for image track;
  may also test reduced/no visual examples to avoid anchoring
- [x] **HIGH-thinking verifier test** — run adversarial verifier with HIGH
  thinking on existing pilot candidates; compare to MINIMAL-thinking
  baseline. *(Completed 2026-03-10, Session 45)*. NEGATIVE RESULT:
  F1 dropped from 0.768 to 0.747. See `results/phase3d-high-thinking-results.md`

#### Medium-cost experiments (~$35 each)

- [ ] **Full 1-of-5 union proposer + adversarial verifier** (text track) —
  5 passes at T=0.7 + HIGH thinking with recall-biased prompt, union all
  candidates, then adversarial verifier filters; target F1 > 0.80
- [x] **Cross-modal union proposer + verifier** — union of image-track and
  text-track proposer candidates, then single adversarial verifier; exploits
  complementary detection profiles across modalities. *(Completed 2026-03-10,
  Session 45)*. Results: F1=0.768 (P=0.711, R=0.835) at t=0.11 — recall
  exceeds both single tracks (0.784 text, 0.711 image) but F1 is −0.028
  below text-only (0.796). Provenance: both-track candidates strongest
  (P=0.867), image-only weakest (P=0.318). Cost: ~$2 (184 API calls).
  See `results/phase3d-union-results.md`
- [ ] **Multi-pass verifier for borderline candidates** — first verifier pass
  on all candidates, second pass (different framing) only on borderline
  candidates (probability 0.3–0.7); targets recall preservation

#### Verifier improvement experiments (planned)

See `planning/phase3d-verifier-experiments.md` for full details.

- [x] **A: Provenance-informed verification** (~$1) — tell verifier that
  text track did NOT flag image-only candidates. *(Completed 2026-03-10,
  Session 46)*. Best result: ΔF1=+0.011, removed 3 FPs. Did not reach
  F1>0.796 target. See `results/phase3d-verifier-experiments-abc.md`
- [x] **B: Visual examples for image-only** (~$0.50) — test
  include_examples=True on 44 image-only candidates. *(Completed
  2026-03-10, Session 46)*. Paradoxical: best image-only P (+0.073) but
  worst whole-pool F1 (−0.004) due to greedy matching non-additivity.
- [x] **C: Temperature variation + majority vote** (~$1.50) — T=0.5,
  3 samples per candidate, test whether T=0 confidence is genuine.
  *(Completed 2026-03-10, Session 46)*. Negative result at both T=0.5
  (ΔF1=+0.004) and T=1.0 (ΔF1=0.000). Errors are systematic, not
  stochastic.
- [ ] **D: Cascaded verification** (~$0.50) — second-stage comparative
  verifier on candidates that pass first stage
- [ ] **E: High-recall text proposer** (~$3.50 via Batch API) —
  recall-biased proposer config targeting R>0.85

#### Design tasks

- [ ] **Draft proposer-specific prompt** — modify system instructions for
  high-recall mode: remove negative examples, add explicit "err on the side
  of inclusion" framing, consider removing or reducing example images
- [ ] **Draft text-only verifier for image-track candidates** — test whether
  text-only adversarial verification works as well on image-originated
  candidates as on text-originated ones
