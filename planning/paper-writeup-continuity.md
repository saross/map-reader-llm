# Paper write-up continuity — handoff for a fresh session

**Created**: 2026-04-21 (late, end of Session 73 equivalent)
**Last updated**: 2026-05-03 (Session 83 closure — T=0.7 55-map text-high recovery completed; 160/160 failed tile-passes recovered; full downstream propagation chain through D-S re-aggregation; 3 new bugs fixed (parser realtime-vs-batch, D-S row-position, cost_manifest cleanup-overwrites-meta); Obs 318 + 319 added; 7 docs updated; 3 outstanding recoveries queued)
**Purpose**: Continuity message for a fresh Claude Code session to
pick up the paper write-up phase without re-reading the entire
project state.

---

## ⚡ Start here (Session 78+ entry point)

**You are on: Step 6 (paper outline)**. Step 4 (14 items) and Step 5
(mark-superseded sweep) are both DONE. Batch A Session-77 follow-ups
resolved the two data-generation gaps flagged in item 12 §9.4 (image-vs-
text paired permutation tests at 20/30/40/50 m; extended buffer sweeps
for text-HIGH and text-MIN at 75/100/125 m). The only remaining Session-
77 follow-up is text-track human review (~17 reviewer-hours, human
time — not for me to execute). Ready to hand to a paper outline.

**Previous entry points**:

- Session 76 opened at Step 4 item 8 (crosstab level-up); closed with
  items 8-14 complete (see §"Session 76 status" below).
- Session 77 opened at "Step 5 + Step 6"; closed mid-session with Batch
  A (data-gen follow-ups) + Batch B1 (Step 5 archive reorg) complete.
  Batch B2 (reflections) added in the same Session 77.

**Tree state at handoff**: mid-Session-77. ~24 Session-76 + Session-77
commits total, from `f700acd9` through `80025eaf`, main-only, working
tree clean, **NOT yet pushed to origin** (per user directive: review
before push). Use `git log --oneline 8949dc00..HEAD` for the full log.

**Batch A commits** (Session 77 data-gen, 3 commits):

- `dfbf88a5` — 8 image-vs-text paired permutation tests (all buffers).
- `1220f339` — text-HIGH + text-MIN extended-buffer eval at 75/100/125 m.
- `eaf6c8ba` — incorporated A1 + A2 results into cross-track-comparison
  doc (item 12); follow-ups #1 and #3 now DONE.

**Batch B1 commits** (Session 77 Step 5, 2 commits):

- `34074873` — archive reorganisation: 17 files moved from `planning/`
  and audit locations into 6 new themed `archive/` subdirs. Pure moves
  (no content changes) + 6 new README files explaining each subdir.
- `b33a818a` — SUPERSEDED banners added to the 17 moved files + trivial
  lint fixes (bare URLs, list blanks, table-column-count).

**Batch B2 commit** (Session 77 reflections, 1 commit):

- `80025eaf` — Session 76 reflection entries appended to
  `session-reflection.md` and `llm-observations.md`. Formal /reflect
  skill will run at end-of-session-77.

**Continuity-doc update + lint** (2 commits):

- `1ad0f8a1` — continuity doc: Session 78+ entry point = Step 6.
- `34322433` — MD032 lint fix on continuity doc (blanks around lists).

**Batch C commit** (Session 77 meta-findings refresh, 1 commit):

- `ad93c806` — Session 76 / 77 findings folded into
  `results/meta-findings-summary.md` as light additions: T1 §3.4
  (cross-track + position-noise + cross-modality-paired bullets); T3
  §5.4 (cross-track verifier scope); T5 §7.4 (D-S prior-invariance
  empirical confirmation); §2.3 canonical numbers table extended
  with 6 new rows (text-track F1, paired tests, buffer plateaus).
  Existing Themes T1-T5 structure intact; no change to suggested
  paper texts.

**Reading order (in sequence, don't skim)**:

1. This file — the current orientation layer (you are reading it).
2. `planning/interim-docs-review.md` **§6 Step 4 sequencing** —
   the canonical Step 4 work-plan. **All 14 items DONE**; see
   §"Session 76 status" below for per-item commit table.
3. `docs/notes/reflections/session-reflection.md` §"Session 76
   Reflection" (write at start of new session if not present). Key
   carry-over lessons from Session 76:
   - **Script-hardening-before-level-up is now a standard Session 76
     pattern**. 8 scripts hardened in S76 to route auto-generated
     Markdown to `_autogen.md` siblings, protecting hand-authored
     level-ups from dry-run overwrite. Extends the Session 75
     precedent (`collect-factor-analysis.py` → `_autogen.md`).
   - **Cross-pipeline context bleed caught in flight** (Session 75
     Guardrail, Added 2026-04-24 item 2): Session 76 caught a model-
     attribution error across Targets 4 + 5 (initial "Gemini 2.5 Pro"
     corrected to "Gemini 3 Flash" by cross-referencing
     `results/paper-eval/mcc/consensus-pv/batch_mcc_summary.md` row
     labels). The anomaly-investigation pattern works.
   - **Item-12 cross-track doc caught a vote_t mismatch**
     (image = 3, text = 4); re-verified against
     `outputs/<track>/resolved_config.yaml` and fixed in commit
     `b960a3cf`. Cross-track claims must cite the `resolved_config.yaml`
     for pipeline-control parity, not assume it.
4. `docs/notes/reflections/llm-observations.md` §"Session 76
   Observations" (write at start of new session if not present).
   Distinctive Session-76 findings:
   - 8 scripts hardened for Session-75-G6 in a single session
     (see §"Session 76 status" for the full list).
   - Agent 2 confabulation: a background dossier-assembly agent
     returned "Claude 3.5 Sonnet" as the proposer model for the
     55-map tracks; the correct model is `gemini-3-flash-preview`
     (verified from `outputs/*/verified/run.meta.json`). Dossier
     output from sub-agents must be spot-checked for model strings
     against authoritative meta files.
   - New synthesis docs (items 12 + 13) have inherent higher
     confabulation risk than additive level-ups — run full verifier
     passes on them.
5. `results/meta-findings-summary.md` — Step 3's output. Still the
   Discussion-spine reference.
6. `results/gold-standard-subtype-classification/report.md` — still
   the exemplar for per-analysis report structure.
7. Now begin Step 5 (mark superseded) or Step 6 (paper outline).

**Canonical numbers table for paper claims** — see §"Canonical numbers"
below. Verified 2026-04-21 by a fresh-context verifier agent; do not
re-verify.

**Load-bearing guardrails** (details in §"Critical guardrails" +
§"Added 2026-04-23" + new §"Added 2026-04-24" below):

1. Sub-agent verdicts are **drafts, not verdicts** — verify any
   load-bearing agent claim against the filesystem before acting.
2. No citations from `archive/v2-verifier-contamination/`,
   `archive/flawed-audit-2026-04-19/`, or
   **`archive/h10-h12-v1-retracted-probe/`** (new Session-75
   archive; Obs 235 retracted data moved from `outputs/h10/` +
   `results/h10/` subtrees on 2026-04-24).
3. UK / Australian English throughout (analyse, behaviour, prioritise,
   synthesise, finalise, recognise).
4. E47 disambiguation required whenever referenced: `protocol-errata.md:1233`
   (buffer revert) vs `working-notes.md:6553` (proposer prompt
   substitution).
5. **Main-thread propose + verifier-agent check is mandatory for
   every new/level-up analysis doc.** Pattern established in
   Session 75: the verifier caught errors in 7 of 7 items. Do not
   skip for token economy.
6. **Aggregator scripts can overwrite hand-authored narrative at
   the same path.** Before running any script in `scripts/` that
   calls `write_outputs`, `write_master_json`, or a similar
   consolidation function, check whether the destination file is a
   hand-authored level-up. If yes, either route to an `_autogen.md`
   sibling path (as done for `collect-factor-analysis.py`) or
   revert the overwrite after the dry-run.
7. **Paper-table regeneration is a deliberate act, not a side
   effect.** Aggregator dry-runs during hardening/debugging must
   `git checkout` any output file changes unless regeneration is
   scoped as the explicit task. See `results/paper-tables/` drift
   logged in §"Step 6 polish-pass backlog" for an active instance.

---

## Session 76 status (2026-04-25) — Step 4 items 8–14 + verifier-fix pass

### Step 4 items completed (DONE 2026-04-25)

| Item | Target | Commit(s) | Notes |
|------|--------|-----------|-------|
| 8 | `crosstab.md` level-up | `f700acd9` | Obs 268 anchor, flip-rate definition, paper implications, files manifest. |
| 9 | `evaluation-scopes.md` level-up | `01db8fe5` | Methods keystone; era-tagging for each paper-headline F1 claim; ad-hoc nesting-check operation documented. |
| 10 target 1 | `buffer-band-lift/report.md` | `cb940cfb` | Script hardened: `analyse_buffer_band_lift.py` now writes `report_autogen.md`. |
| 10 target 2 | `verifier-calibration-crosstab/calibration.md` | `55ddda00` | Script hardened: `crosstab_verifier_vs_human.py` → `calibration_autogen.md`. Verifier-fix: Obs 269 under-confidence hypothesis FALSIFIED framing. |
| 10 target 3 | `human-reviewed-corrected/corrected-f1-human-reviewed.md` | `08d5aef6` | Script hardened: `compute_corrected_f1_human_reviewed.py` → `corrected-f1-human-reviewed_autogen.md`. Headline 0.830 lower-bound framing explicit. |
| 10 target 4 | `phase3a-text-matrix/secondary_effects.md` | `92cc9fa5` | Script hardened: `analyse_secondary_effects_text.py` → `secondary_effects_autogen.md`. Title corrected "Image → Text Track". |
| 10 target 5 | `secondary-effects/secondary_effects.md` (image-track) | `c7bfd579` | Script hardened: `analyse_secondary_effects.py` → `secondary_effects_autogen.md`. Metric-anchored headline (SCALE4-T0.7 MCC 0.746 leader; HIGH-T0.7 F1 0.750 leader). |
| 10 target 6 + Targets 4/5 model fix | `phase3a-image-matrix/consensus-analysis-summary.md` + model corrections for Targets 4/5 | `82254d16` | Script hardened: `summarise_phase3a_matrix.py` → `consensus-analysis-summary_autogen.md`. Retrospective correction: Targets 4/5 initially said "Gemini 2.5 Pro"; correct is "Gemini 3 Flash" per batch_mcc_summary.md "Flash HIGH" row labels. |
| 10 target 7 | `ds-human-crosstab/report.md` | `50e506c0` | Hand-authored; Obs 273 structural-inadequacy framing front-loaded. |
| 10 target 8 | `dawid-skene-v2-data-driven-prior/report.md` | `6c3aef23` | Hand-authored; empirical-prior-pathology + calibrated-prior-at-0.17 finding; AUC=0.500 invariance across priors. |
| 10 target 9 | `corrected-f1-multi-buffer/report.md` | `e60aadb4` | Script hardened: `compute_corrected_f1_multi_buffer.py` → `report_autogen.md`. Three-tier headline framing (0.8317 / 0.8538 / 0.8551 at 50 / 125 / 150 m). |
| 10 target 10 | `gold-standard-extended-buffer-sweep/extended-buffer-report.md` | `87afb3cc` | Polish of strong existing content; added exec summary + caveats + paper implications on the GT-precision-noise argument. |
| 11 | `retest-production-summary.md` | `b0b35ecb` | Era 1 multi-phase cross-cutting exec + caveats + paper implications; Obs 155/240/272 back-references. |
| 12 | `55maps-cross-track-comparison/report.md` (NEW) | `6bcbf6e0` (+ `b960a3cf` verifier fixes) | Image × text-HIGH × text-MIN synthesis doc; 472 / 474 phantom-TP framing made explicit; vote_t = 3 vs 4 difference caught + documented in verifier pass. |
| 13 | `limitations-consolidation/report.md` (NEW) | `ae460ef1` (+ `b960a3cf` verifier fixes) | 4 first-order + 15 second-order limitations catalogued; all Obs + errata anchors verified. |
| 14 | `h12-v2/analysis_summary.md` polish | `a3f30552` | Exec summary + cross-hypothesis-closure paper implications + caveats (E52 preregistered-but-post-errata framing). |

### Verifier-fix commits (DONE 2026-04-25)

- `b960a3cf` — Applied verifier-caught P1/P2 corrections to items 12 + 13. Six fixes on item 12 (vote_t = 3 vs 4; 474→472; §4 n_reviewed cell; §3.1 rounding; §6 uncached-token figure; preview-vs-stable model note). Three fixes on item 13 (474→472; Obs 235 attribution; §4.5 heading E50–E54). No numerical tables changed; annotations and scope caveats tightened.

### Script-hardening summary — 8 scripts in Session 76

Extending the Session 75 pattern (`collect-factor-analysis.py` → `factor_analysis_results_autogen.md`):

| Script | New output path (from / to) | Commit |
|---|---|---|
| `scripts/analyse_buffer_band_lift.py` | `report.md` → `report_autogen.md` | `cb940cfb` |
| `scripts/crosstab_verifier_vs_human.py` | `calibration.md` → `calibration_autogen.md` | `55ddda00` |
| `scripts/compute_corrected_f1_human_reviewed.py` | `corrected-f1-human-reviewed.md` → `corrected-f1-human-reviewed_autogen.md` | `08d5aef6` |
| `scripts/analyse_secondary_effects_text.py` | `secondary_effects.md` → `secondary_effects_autogen.md` | `92cc9fa5` |
| `scripts/analyse_secondary_effects.py` | `secondary_effects.md` → `secondary_effects_autogen.md` | `c7bfd579` |
| `scripts/summarise_phase3a_matrix.py` | `consensus-analysis-summary.md` → `consensus-analysis-summary_autogen.md` | `82254d16` |
| `scripts/compute_corrected_f1_multi_buffer.py` | `report.md` → `report_autogen.md` | `e60aadb4` |

**Impact**: 8 hand-authored paper-citation docs now protected against accidental dry-run overwrite. Each `_autogen.md` sibling is regenerated by the script on re-run; the hand-authored doc is not touched. Future aggregator scripts should follow the same pattern from the start.

### Distinctive Session-76 findings (load-bearing carry-overs)

1. **Cross-pipeline context bleed is a real failure mode, caught in flight**. The Session-75 guardrail "Added 2026-04-24 item 2" (cross-pipeline context bleed) was exercised successfully in Session 76: Targets 4 + 5 initially cited "Gemini 2.5 Pro" as the proposer model; cross-referencing the MCC batch summary (`results/paper-eval/mcc/consensus-pv/batch_mcc_summary.md` rows "Flash HIGH text 26-of-30" and "Flash HIGH image 6-of-10") caught the error; retrospectively corrected in commit `82254d16`. The pattern: before writing a model-version claim in a level-up, spot-check against a cross-artefact row label.
2. **Item-12 vote_t = 3 / vote_t = 4 asymmetry**. The verifier-agent pass on the new cross-track comparison doc caught that image uses `vote_t = 3` while text-HIGH and text-MIN use `vote_t = 4`. Cross-track comparability claims must cite the `resolved_config.yaml` for each track, not assume parity.
3. **Agent 2 dossier confabulation: "Claude 3.5 Sonnet" for Gemini-3-Flash runs**. A background dossier-assembly agent returned the wrong model string; the correct model was verified from `outputs/<track>/verified/run.meta.json`. Dossier outputs from sub-agents must be spot-checked for model strings against authoritative meta files.
4. **474 vs 472 phantom-TP distinction**. The single-buffer corrected-F1 uses 472 (`corrected-f1-human-reviewed.json`); the multi-buffer artefact uses 474 (adds 2 candidates from today's multi-buffer re-review at the 50 m shell). Both valid; both round to 0.830 at the advertised precision. Do NOT conflate the two counts in cross-doc synthesis.
5. **Verifier-agent pattern catch-rate — Session 76 evidence**: 6 items dispatched per-doc verifiers (8, 9, T1–T4 of item 10); 2 new-synthesis items dispatched verifiers (12, 13). Verifier-agent caught 0–4 P1/P2 items per doc; the new synthesis docs (items 12, 13) had the highest P1 error rate (4 P1 on item 12, 0 P1 on item 13). New-content-per-doc = higher verifier catch rate; pure-lift level-ups = lower catch rate. Pattern stable.

### Scorecard state after Session 76

`planning/interim-docs-review.md` §6 Step 4 sequencing — **14 of 14 items DONE**. Step 4 is complete.

---

### Added 2026-04-25 (Session 76)

The following three items extend the earlier guardrails and are specific
to the post-Session-76 landscape.

1. **Script-hardening before level-up is now standard**. For any analysis
   script that writes a paper-citation Markdown file, the Session 75 / 76
   pattern is to route the script's output to a `_autogen.md` sibling
   path, leaving the unsuffixed path free for a hand-authored level-up.
   8 scripts were hardened in Session 76 on this pattern (see table above).
   New analysis scripts should adopt the pattern from the start rather
   than retrofit after a level-up.
2. **Cross-reference `outputs/<track>/resolved_config.yaml` for
   pipeline-control parity**. Item 12 caught a `vote_t = 3` vs `vote_t = 4`
   asymmetry across the three 55-map tracks that was not obvious from
   the evaluation JSONs or `run.meta.json`. Cross-track comparability
   claims must cite the per-track `resolved_config.yaml` for pipeline
   control parameters (consensus vote threshold, PV probability threshold,
   dedup radius, etc.) — assuming parity is not safe.
3. **New synthesis docs need full verifier-agent passes**. Additive
   level-ups of existing docs (where tables are lifted verbatim and new
   sections add exec summary / methods / caveats / paper implications)
   have a lower confabulation risk than new synthesis docs (items 12, 13
   in this session). For new synthesis docs, run the verifier pattern
   with explicit numeric-cross-check instructions; expect higher P1
   error rates on these than on pure-lift level-ups.

---

## Session 75 status (2026-04-24) — Step 4 items 1–7 + close-out

### Step 4 items completed (DONE 2026-04-24)

| Item | Target | Commit(s) | Notes |
|------|--------|-----------|-------|
| 1 | `results/h8-v2/analysis_summary.md` | `f6d1cdb4` + `ce075d5a` | Library-composition null (7-contrast BH-FDR). Obs 238 editorial note added for the "four of six → three of six" arithmetic error. |
| 2 | `results/h10/analysis_summary.md` + retracted-probe archive | `52404476` + `4b20b427` | Clean 4-pool-size null (Obs 236). Discovered + physically moved Obs 235 retracted H10/H12 v1 arm to `archive/h10-h12-v1-retracted-probe/` (7,988 tracked files). Scorecard §3.11 marked superseded. |
| 3 | `results/retest/phase2b/analysis_summary.md` + Option B residual | `e8c46809` | T=0.0 optimal on both tracks (340-tile K=3). Full Option B: new retest-era `phase2b-carry-forward-parameters.md`, phase2c:126 repoint, pre-retest archive. |
| 4 | `results/h11/analysis_summary.md` | `bb156aab` | Tile-size inverted-U (F1=0.883 at 384 px 6-of-10 text + PV). UNINTENDED-T1.0 (E43 + E44) disposition settled. |
| 5 | `results/55maps-image-generalisation/buffer-100m-diagnostics/report.md` | `334c6cb4` | 50→100m recall gain is TP admission (71 new, 0 lost, 0.10% drift). |
| 6 | `results/paper-eval/mcc/report.md` | `9df2f169` | 89-condition MCC family consolidated; Phase 2b MCC inversion (Obs 274) flagged. |
| 7 | `results/factor-analysis/factor_analysis_results.md` level-up | `a5c4c325` + `043fca18` + `6cf99660` + `9f9f98c3` | 5-family pairwise permutation report (29/61 sig). Option A data-recovery fix for 2 mislabelled "512 px" rows (actually Phase 2b N=1 at 384 px; schema-mismatch `global_a` vs `condition_a`). Script hardened. |

### Close-out commits (DONE 2026-04-24)

- `71033ff6` — Step 6 backlog entry logged (later resolved).
- `23ddfdf6` — `evaluate_pv_results.py` hardening (D2a raise on missing consensus).
- `9f7bfe0f` — `consolidate_pv_bootstrap_cis.py` hardening (D2b observability + provenance).
- `f623652d` — `consolidate_paper_metrics.py` hardening (D2c schema validation + provenance).
- `783f37c2` — Doc hygiene: h11 model-version line; 50m TP reconciliation notes in two 55-map reports.
- `8949dc00` — Continuity-doc close-out: S6.1 RESOLVED, new metrics_master drift entry logged.

### Distinctive Session-75 findings (load-bearing carry-overs)

1. **Retracted-data physical isolation**. Session 75 discovered that
   `results/h10/{sweep_results.json, statistical_analysis.json,
   verifier_independence_probe.{json,md}, k5_replicate_sweep.json,
   consensus_dedup_magnitude_diagnostic.json, wbf/*}` + the entire
   `outputs/h10/{consensus, evaluation, verified, verifier-crops, wbf}/`
   subtrees were derived from the Obs 235 retracted H10/H12 v1 arm
   (text-only proposer, `include_example_images: false`,
   2026-04-11). Those files had sat unflagged in the working tree
   for seven months. They are now at
   `archive/h10-h12-v1-retracted-probe/` with an explicit
   retraction README. Future sessions must NOT cite anything from
   that archive as evidence of library composition / HP:HN / pool
   size; the clean cross-hypothesis coverage is in H8 v2 + H12 v2.
2. **Schema-mismatch + mislabelling in a single bug**. The
   `collect-factor-analysis.py` aggregator read `global_a`/`global_b`
   from permutation JSONs that use `condition_a`/`condition_b`,
   silently zeroing two rows. Those two rows were additionally
   mislabelled "512 px" when the source data is Phase 2b retest at
   384 px N=1. Both fixed (recovery at `043fca18`, schema helper +
   7 other audit items at `9f9f98c3`).
3. **Verifier-catch rate is steady at 2–3 errors per item**. All 7
   Step-4 items had at least one verifier-caught error. Model-name
   confusion (`gemini-3-flash-preview` vs `gemini-3-flash`) was
   particularly frequent across item 3 and item 6 — watch for
   cross-pipeline context bleed when the session touches multiple
   model-family trees.
4. **A single dry-run can overwrite hand-authored narrative**.
   `collect-factor-analysis.py`'s `write_outputs` used to target
   `factor_analysis_results.md` with auto-generated tables; the
   Item-7 level-up replaced that file with a 390-line narrative;
   then my dry-run during Commit 1 of the close-out regenerated the
   tables-only file over the narrative. Guard added (script now
   writes to `factor_analysis_results_autogen.md`) and the pattern
   is now documented in the §"Critical guardrails" block above
   (item 6). Check other aggregator scripts for the same risk.
5. **Aggregator-script metadata provenance added**. All four
   aggregators (`collect-factor-analysis.py`,
   `evaluate_pv_results.py`, `consolidate_pv_bootstrap_cis.py`,
   `consolidate_paper_metrics.py`) now emit `script_version`,
   `source_files` / `source_files_processed`, and `input_dir` in
   their output JSON metadata. Schema drift in any upstream source
   now fails loudly instead of silently zero-filling.

### Sweep coverage (Session 75 end-of-session parallel agents)

Four Explore agents swept four scopes for latent errors analogous to
the factor-analysis bug:

- Agent A (`results/factor-analysis/`, `results/phase3a-*/`,
  `results/paper-eval/`, `results/pairwise/`): only the
  already-fixed factor-analysis bug; otherwise clean.
- Agent B (`results/h8-v2/`, `results/h10*`, `results/h11*`,
  `results/h12-v2/`, `results/retest/`): three Priority-1 narrative
  consistency issues (h8-v2 line 264, h8-v2 line 398, h10 line 97
  sign convention) — all fixed in `6cf99660`.
- Agent C (`results/55maps-*/`, `results/gold-standard-*/`,
  `results/paper-tables/`): zero Priority-1 findings. Corrected-F1
  headline 0.830, subtype-weighted-F1 0.887, ECE 0.269, AUC 0.655,
  attractor-pull p=0.381 all verified clean. Exemplar
  `gold-standard-subtype-classification/report.md` also clean.
- Agent D (`scripts/`): confirmed the factor-analysis bug + 3
  risk patterns in other aggregators — all addressed in the
  close-out commits (`23ddfdf6`, `9f7bfe0f`, `f623652d`).

**Net result**: all hypothesis-level analysis_summaries, the 55-map
and gold-standard reports, and all four aggregator scripts are now
verified clean. Any future session that finds a Priority-1 error
should raise it as a red flag — Session 75 closed the known error
surface.

### Step 6 polish-pass backlog state

- S6.1 (4,108 vs 4,110 TP-at-50m): **RESOLVED** 2026-04-24. Not a
  bug; methodological GT-input difference. Reconciliation notes in
  both 55-map reports.
- **New entry**: `results/paper-tables/metrics_master.csv` (104
  rows) and `metrics_master.json` (100 rows) are out of sync at
  HEAD. Not fixed in Session 75 per output-regeneration non-goal.
  Deliberate re-run of `scripts/consolidate_paper_metrics.py`
  during paper finalisation will bring to parity.

### Scorecard state after Session 75

`planning/interim-docs-review.md` §6 Step 4 sequencing — 7 of 14
items DONE. Remaining 7 items in order:

- **8** — `uncalibrated-vs-calibrated-crosstab/crosstab.md`
  level-up (S, 25–35 min). **← Next session entry.**
- 9 — `results/evaluation-scopes.md` level-up (S, 20–30 min).
- 10 — Batch-level-up the 8 partial per-analysis reports (~3.5–4.5 h).
- 11 — `results/retest/retest-production-summary.md` level-up
  (M, 45–60 min).
- 12 — 55-map cross-track comparison doc (new, from Need list).
- 13 — Limitations consolidation doc (new, from Need list).
- 14 — h12-v2 exec-summary + paper-implications polish (S, 20–30 min).

---

### Added 2026-04-24 (Session 75)

The following five items extend the earlier guardrails and are
specific to the post-Session-75 landscape.

1. **Retracted-data discipline**. When touching any
   `results/h10/*` or `outputs/h10/*` path, first check
   `archive/h10-h12-v1-retracted-probe/README.md` to confirm the
   retraction scope. The clean sibling trees
   (`outputs/h10/evaluation-v2/`, `outputs/h10/example-pools-v2/`,
   `outputs/h10/hard-cases-v2/`) are valid; everything else under
   `outputs/h10/` was moved to the archive on 2026-04-24.
2. **Cross-pipeline context bleed is a real failure mode**. When a
   session touches multiple analysis trees (MCC + F1, or Phase 2b
   + H8 v2, etc.), cite numbers only from the correct tree. Item 3
   and item 6 of Session 75 both had errors where a 55-map F1 got
   pulled into a 384 px MCC row, or a `gemini-3-flash-preview` was
   cited for a `gemini-3-flash` Phase 2b run. Check the meta.json
   of the specific run before citing the model name.
3. **Aggregator outputs have a provenance contract now**. Any
   aggregator that writes a consolidated JSON/CSV should include
   `_metadata.script_version`, `_metadata.source_files*`, and
   where applicable `_metadata.input_dir`. The four scripts
   hardened in Session 75 all follow this pattern; new aggregators
   should too. If a downstream consumer reports an ambiguity about
   which input produced a given row, the answer should be in the
   metadata block, not in a code-archaeology expedition.
4. **Verifier-agent pattern is now baseline, not optional**.
   Establish the pattern for every new/level-up analysis doc:
   main-thread propose → dispatch fresh-context verifier agent with
   authoritative source paths → apply flagged corrections → commit.
   Session 75's 7-of-7 error-catch rate makes this a bright line.
5. **Step 6 must regenerate the paper tables deliberately**. The
   committed CSV/JSON drift in `results/paper-tables/` is not a
   bug to fix in the current commit — it's a planned regeneration
   step at paper finalisation. Do NOT run
   `scripts/consolidate_paper_metrics.py` in a dry-run without
   reverting the output files afterwards, and do NOT commit the
   regenerated files as a side effect of hardening work.

---

## Session 74 status (2026-04-23) — what's new since the original handoff

### Steps completed (DONE 2026-04-23)

- **Step 1 — Context warm-up** (✅ DONE 2026-04-23).
- **Step 2 — Interim-doc review pass** (✅ DONE 2026-04-23) →
  `planning/interim-docs-review.md` (1,281 lines, 21 rows, 9
  directory groups in §10 "known out-of-scope", markdownlint-clean).
  **Note**: §6 Step 4 sequencing in that file is now the canonical
  Step 4 plan and supersedes the "Need" list in this file's
  §"Documentation state — what we have vs what we need" section
  below.
- **Step 3 — Meta-findings consolidation** (✅ DONE 2026-04-23) →
  `results/meta-findings-summary.md` (1,158 lines, 5 themes, each
  with a "Suggested paper text" block + full Trace; all 9 headline
  canonical numbers spot-checked present; markdownlint-clean).

### New artefacts from Session 74

- **Obs 274** in `docs/notes/reflections/working-notes.md` — Phase
  2b tile-level MCC inverts the F1 ordering (image 0.089 → 0.368
  monotonic across T=0.0 → T=1.3; mechanism is flat sensitivity +
  climbing specificity). Reconciles (does not contradict) Obs 116 /
  177 / 209. Ready to cite in Discussion if the paper addresses
  metric-choice tradeoffs; not required for any Step 3 theme.
- **Phase 2b tile-level MCC** at `results/paper-eval/mcc/phase2b/`
  (10 conditions × K=3 × 340 tiles, patched pipeline).
- **CRS bugfix** (commit `eb2cf23c`): `scripts/analyse_consensus_sweep.py::consensus_to_gdf`
  now constructs the GeoDataFrame in EPSG:4326 then `to_crs(TARGET_CRS)`.
  Contamination scope verified narrow — Phase 2b MCC was the only
  post-2026-04-11 consumer that hit the bug. **No active artefacts
  required re-compute.** `load_geojson` consumers dodge the bug via
  GeoPandas' default 4326 auto-assignment for CRS-less GeoJSON; the
  `ensure_utm_crs` helper in `lib_consensus` is immune by construction.
- **Option A pre-retest phase2b archive pass** (commit `16ee3ae5`):
  six orphan 60-tile K=10 pilot docs moved from `results/` to
  `archive/outputs-pre-retest-60-tile/phase2b/`. Ci-metadata-registry
  updated. `phase2b-carry-forward-parameters.md` **retained** with a
  retention banner because `phase2c-carry-forward-parameters.md:126`
  depends on it — **Option B residual MANDATORY for Step 4** (see
  §"Critical guardrails" item 5 above).
- **UNINTENDED-T1.0 disposition** (commit `5ae94041`): both
  `outputs/h11/{consensus,single-pass}-384-UNINTENDED-T1.0/README.md`
  banners rewritten to reflect dual role (origin = E43 deviation;
  retention = serendipitous Era 2 / 487-tile T=1.0 coverage for 157
  downstream references where Phase 2b at 340 tiles cannot extend).

### Scorecard coverage gap caveat

The original §"Documentation state — what we have vs what we need"
list in this file was a strict subset of the actual `results/`
tree. Session 74's re-inventory discovered ~10 directories that
belong in-scope and added 6 of them as scorecard rows (phase3a-image-
matrix, secondary-effects, factor-analysis, retest-production-summary,
evaluation-scopes, uncalibrated-vs-calibrated-crosstab; plus Phase 2b
retest as row 15). 9 directory groups remain in scorecard §10 "known
out-of-scope". **Use `planning/interim-docs-review.md` §6 as the
authoritative Step 4 plan**; this file's §"Need" list is
superseded-but-preserved-for-reference (see DONE-annotations below).

---

## Executive state

- **Analysis freeze reached**: all LLM extraction runs complete. No
  more API spend planned. If a paper-claim-driven recalculation
  surfaces during write-up, it's a known possibility but not
  blocking.
- **Documentation audit complete and verified** (2026-04-21):
  `results/documentation-audit/` — the authoritative index to every
  run, deliverable, and citation source. 82 / 85 claims verified by
  a fresh-context verifier agent; 0 dead citations.
- **Interim docs are the primary source** for paper mining.
  Working-notes observations (Obs 1–273) and raw results are the
  deep-dive layer when interim docs are insufficient or suspect.
- **v2 verifier work is quarantined** to
  `archive/v2-verifier-contamination/`. Do NOT cite any figure
  traceable to that directory — the v2 prompt was calibrated on
  gold-standard FPs (calibration-on-test).
- **Paper-headline detection F1 = 0.904** at 50 m on the 487-tile
  matrix uses verifier v1 (confirmed during quarantine). Headline is
  clean.

## Write-up strategy (user-approved)

1. Mine interim documentation first (from `results/documentation-audit/`
   and the per-analysis `report.md` files).
2. Mark superseded interim docs as `SUPERSEDED`.
3. Level-up any interim doc below the exemplar's quality bar.
4. Then draft the paper, referencing interim docs as primary sources,
   descending to raw results / working-notes observations only when
   an interim doc is insufficient or contested.

### Exemplar (quality template) — CONFIRMED 2026-04-21

`results/gold-standard-subtype-classification/report.md` — 17
sections, full citation pattern, methods block, paper implications,
relationship to prior Obs, reproducibility section. Any other
interim doc that matches this structural bar is "finished".

User confirmed this nomination on 2026-04-21 end-of-session. Treat
it as the authoritative template for interim-doc quality from here.

### Two suggested refinements on the user's strategy

1. Before quality-levelling, list existing interim docs against the
   exemplar's structure — produces a concrete gap-list instead of a
   subjective "best" moving target.
2. Write one new meta-consolidation: `results/meta-findings-summary.md`
   at the exemplar's quality level, synthesising Obs 264 / 265 / 266
   (failure taxonomies) + Obs 269 (verifier calibration) + Obs 271
   (benchmark→triangulation) + Obs 272 (attractor-pull) + Obs 273
   (D-S inadequacy) into the paper's Discussion-section spine.
   ~2 hours. Front-loads the synthesis and avoids five-way
   cross-referencing during the main writing pass.

## Documentation state — what we have vs what we need

### Have — primary interim docs (citation-ready)

**Per-analysis reports** (use these as first-pass paper content):

- `results/gold-standard-subtype-classification/report.md` (exemplar)
- `results/55maps-image-generalisation/buffer-band-lift/report.md`
- `results/55maps-image-generalisation/corrected-f1-multi-buffer/report.md`
- `results/55maps-image-generalisation/ds-human-crosstab/report.md`
- `results/55maps-image-generalisation/dawid-skene-v2-data-driven-prior/report.md`
- `results/55maps-image-generalisation/human-reviewed-corrected/corrected-f1-human-reviewed.md`
- `results/55maps-image-generalisation/verifier-calibration-crosstab/` (calibration.md)
- `results/55maps-image-generalisation/buffer-100m-diagnostics/` (summary.json + report)
- `results/gold-standard-extended-buffer-sweep/extended-buffer-report.md`
- `results/h8-v2/analysis_summary.md` (per audit, strongest Era 1
  narrative)

**Paper-tables consolidation (paper-ready, with suggested citations)**:

- `results/paper-tables/metrics_master.{json,csv}` — consolidated
  487-tile-matrix F1/P/R
- `results/paper-tables/leaderboard-20m-annotated.md` — tiered
  leaderboard with annotation
- `results/paper-tables/gold-standard-spatial-tolerance.{md,csv}`
  (suggested citation embedded)
- `results/paper-tables/subtype-classification.{md,csv}` (suggested
  citation embedded)
- `results/paper-tables/spatial_tolerance_comparison.md`
- `results/paper-tables/pipeline_progression.{json,csv}`
- `results/paper-tables/n1_leaderboard.csv` (single-pass K=1 cells)

**Working notes (research trajectory / citation source for Discussion)**:

- `docs/notes/reflections/working-notes.md` Obs 1–273. Key Obs for
  the paper:
  - Obs 262 / 263 / 268 — review-UI calibration
  - Obs 264 / 265 / 266 — failure-mode taxonomies (70 figures)
  - Obs 267 — corrected F1 headline
  - Obs 269 — verifier miscalibration
  - Obs 270 — subtype-classification headline
  - Obs 271 — benchmark→triangulation asymmetric confusion
  - Obs 272 — attractor-pull scale ends at ~125 m
  - Obs 273 — D-S aggregate structurally inadequate

**Methodology / reproducibility**:

- `docs/methodology/preregistration/decisions-log.md` — preregistered
  decisions
- `docs/methodology/preregistration/protocol-errata.md` — E1-E54
- `docs/methodology/v2-verifier-contamination-policy.md` — quarantine
  policy
- `results/ci-metadata-registry.md` — every CI's bootstrap metadata

### Need — gaps worth filling before paper write-up starts

> **⚠️ Superseded 2026-04-23 by `planning/interim-docs-review.md` §6
> Step 4 sequencing**, which is the authoritative ordered 10-item
> Step 4 work-plan. Items below retained for historical context and
> annotated DONE / see-§6 where applicable.

1. **Meta-findings summary** (the suggested refinement above) —
   synthesises Obs 262-273 into a paper-Discussion-shaped narrative.
   **✅ DONE 2026-04-23** → `results/meta-findings-summary.md`
   (1,158 lines, 5 themes, markdownlint-clean, commit `0fccf455`).
2. **Era-scoped hypothesis summaries**. Era 1 (`h10/h11/h12-v2`) has
   `analysis_summary.md` for h8-v2 but probably not uniform coverage
   across hypotheses. Check during the interim-doc review.
   **→ see scorecard §6 items 1, 2, 3, 4**: h8-v2 synthesise (L,
   ~90 min); h10 synthesise (L, ~90 min); Phase 2b retest synthesise
   (L, ~90 min, with Option B residual sub-task); h11 consolidate
   (M, 60–75 min). The "Era 1 has analysis_summary.md for h8-v2" line
   was wrong — scorecard row 10 confirms h8-v2 has NO dedicated
   summary; narrative is in working-notes Obs 238.
3. **55-map cross-track comparison doc**. The three tracks (image /
   text-HIGH / text-MIN) each have evaluation.json; the pairwise
   permutation tests exist under `paired-vs-*`. A one-page
   consolidation of "image vs text-HIGH vs text-MIN" with the paired
   tests cited would make the Results-section narrative cleaner.
   **→ see scorecard §6 item (cross-track)**: not in the current
   §6 top-10 (which is scoped to interim-doc level-ups rather than
   new synthesis docs). This item is still open; consider slotting
   after item 4 in Step 4 or as a late-Step-4 / early-Step-6 task.
4. **A "limitations" consolidation doc**. Scattered limitations
   (v2 quarantine, 14 % reviewer-promoted in extended GT, student-GT
   positional noise ~25 m, AUC=0.5 D-S, Pro+MINIMAL cell untested).
   Would become the Limitations section directly.
   **→ still open**. Like item 3, not explicitly in §6 top-10 but
   needed before paper outline. Suggested slot: after §6 items 1–6
   (i.e., after the Era 1 consolidations and the two new reports),
   so the Limitations doc can cite them directly.

### Mark-as-superseded candidates

Quick scan:

- `planning/*.md` — many are historical planning docs. The
  doc-audit-rerun-plan.md is DONE (keep as record). Others may be
  superseded. Review and append `**Status: SUPERSEDED — <reason>**`
  to stale entries. Don't delete.
- `archive/cc-sessions/` already handled.
- `archive/v2-verifier-contamination/` already has NOTE.md and
  README.md; no action.
- `archive/flawed-audit-2026-04-19/` already has NOTE.md; no action.
- Anything `pre-launch-audit.md` for a run that completed should be
  annotated `**Status: SUPERSEDED — see <run>_post_run_report.md**`
  (optional polish; not load-bearing).

## Canonical numbers (from the verified doc audit)

Paper will cite these. All verified 2026-04-21:

| Claim | Value | Source |
|---|---|---|
| Total project map-sheet coverage | **59 sheets** = 4 gold-standard (K-35-052-4, K-35-053-3, K-35-062-2, K-35-078-1) + 55 generalisation (disjoint; 0 intersection) | `results/evaluation-scopes.md` §11; `inputs/vectors/bounds/384/*.geojson` audit 2026-04-24 |
| Detection F1 headline (487-tile matrix, K=30 text-HIGH + PV) | **0.904** [0.878, 0.928] @ 50 m | `results/paper-tables/metrics_master.json` |
| Detection F1 K=5 companion (487-tile matrix) | 0.891 [0.863, 0.916] @ 50 m | same |
| Corrected F1 lower bound (55-map, human-reviewed) | ≥ **0.830** @ 50 m | `results/55maps-image-generalisation/human-reviewed-corrected/corrected-f1-human-reviewed.json` |
| Multi-buffer corrected F1 curve | 0.832 → 0.848 → 0.852 → 0.854 → **0.855** across 50-150 m | `results/55maps-image-generalisation/corrected-f1-multi-buffer/corrected-f1.csv` |
| Subtype weighted-F1 (4-map GS, conditional on match) | **0.887** [0.849, 0.922] | `results/gold-standard-subtype-classification/macro_weighted_summary.json` |
| Attractor-pull scale ends at | ~**125 m** (shell lift becomes non-significant at p=0.381 in the 125-150 m shell) | `results/55maps-image-generalisation/buffer-band-lift/shell.csv` |
| Verifier calibration | ECE **0.269**, AUC **0.655** | `results/55maps-image-generalisation/verifier-calibration-crosstab/calibration.json` |
| D-S aggregate (VLM-only slice) | Degenerate at any prior; AUC **0.500** regardless | `results/55maps-image-generalisation/dawid-skene-v2-data-driven-prior/summary.json` |
| Review set size | 1,028 VLM-only candidates (472 @50 m, 556 re-reviewed → 274 mound, 283 confirmed FP) | `results/55maps-image-generalisation/human-review.csv` and `.../human-review-multi-buffer.csv` |
| Cost (55-map image generalisation) | $364.70 | `outputs/55maps-image-generalisation/cost_manifest.json` |
| Cost (55-map text-HIGH re-run) | $69.60 | `outputs/55maps-text-high-generalisation/cost_manifest.json` |
| Cost (55-map text-MIN) | $60.79 | `outputs/55maps-text-min-generalisation/cost_manifest.json` |

## Suggested fresh-session plan

### Step 1 — Context warm-up (~15 min) — ✅ DONE 2026-04-23

Read in this order:

1. This file (`planning/paper-writeup-continuity.md`) — handoff
   context.
2. `results/documentation-audit/audit-summary.md` — authoritative
   inventory.
3. `results/documentation-audit/results-audit-2026-04-21.md` §A (the
   four 55-map runs) — detailed run-level citations.
4. The exemplar: `results/gold-standard-subtype-classification/report.md`.

### Step 2 — Interim-doc review pass (~1 hour) — ✅ DONE 2026-04-23

For each per-analysis `report.md` under `results/`, score against
the exemplar's 17-section structure:

- ✓ Complete (matches exemplar quality)
- ~ Partial (identify specific gaps)
- ✗ Missing / stub

Output: `planning/interim-docs-review.md` with the scorecard.

**Actually produced**: 21-row scorecard covering the continuity doc's
"Have" list + 6 re-inventory additions + 1 Phase 2b retest row, plus
a §10 "known out-of-scope" section covering 9 directory groups. Final
tier breakdown: 0 ✓ / 13 ~ / 2 ✗ stub / 4 ✗ missing. Commit `f0287747`.

### Step 3 — Write the meta-findings consolidation (~2 hours) — ✅ DONE 2026-04-23

`results/meta-findings-summary.md` — synthesises Obs 262-273 into
paper-Discussion-shaped narrative. Uses the exemplar's structural
pattern. Cites each source Obs + analytical artefact. Output must
pass markdownlint and have "Suggested paper text" block for each
major finding.

**Actually produced**: 1,158-line synthesis with 13 sections covering
5 themes (T1 human-review calibration / T2 failure taxonomies / T3
verifier miscalibration / T4 subtype asymmetry / T5 attractor-pull +
D-S inadequacy). Each theme has a "Suggested paper text" block with
full Trace (≥ 1 Obs anchor + ≥ 1 artefact path). All 9 headline
canonical numbers spot-checked present. Commit `0fccf455`.

### Step 4 — Fill identified gaps (variable — 11–15 hours comprehensive) — 🔄 IN PROGRESS (7 of 14 DONE)

**Authoritative plan**: `planning/interim-docs-review.md` §6 Step 4
sequencing — 14 ordered items with effort estimates. User has
confirmed the comprehensive pass (NOT minimum-viable). Supersedes the
four original "Need" items above; see the DONE annotations in that
section for mapping.

Items 1–7 were completed in Session 75 — see the Session-75 status
table at the top of this file for per-item commit references. Short
summary with status:

1. ✅ `results/h8-v2/analysis_summary.md` synthesise (L, ~90 min) — DONE 2026-04-24
2. ✅ `results/h10/analysis_summary.md` synthesise (L, ~90 min) — DONE 2026-04-24 (plus Obs 235 retracted-probe archive — a scope discovery)
3. ✅ `results/retest/phase2b/analysis_summary.md` synthesise (L, ~90 min)
   **+ Option B residual** (retest-era carry-forward doc, phase2c
   repoint, pre-retest archive) — DONE 2026-04-24
4. ✅ `results/h11/analysis_summary.md` consolidate (M, 60–75 min) — DONE 2026-04-24
5. ✅ `buffer-100m-diagnostics/report.md` write (M, 45–60 min) — DONE 2026-04-24
6. ✅ `results/paper-eval/mcc/report.md` write (M, 45–60 min) — DONE 2026-04-24
7. ✅ `factor-analysis/factor_analysis_results.md` level-up (M, ~45–60 min
   + Option A data-recovery + aggregator hardening + /audit) — DONE 2026-04-24
8. ⏸ **← NEXT** — `uncalibrated-vs-calibrated-crosstab/crosstab.md` level-up (S, 25–35 min)
9. ⏸ `results/evaluation-scopes.md` level-up (S, 20–30 min)
10. ⏸ Batch-level-up the eight partial per-analysis reports (~3.5–4.5 h)
11. ⏸ `results/retest/retest-production-summary.md` level-up (M, 45–60 min)
12. ⏸ 55-map cross-track comparison doc (new; from "Need" list)
13. ⏸ Limitations consolidation doc (new; from "Need" list)
14. ⏸ h12-v2 exec-summary + paper-implications polish (S, 20–30 min)

### Step 5 — Mark superseded (~30 min) — ⏸ PENDING

Append `**Status: SUPERSEDED — <reason>**` to stale planning /
pre-launch-audit / early-analysis docs. Don't delete.

**Session 74 note**: Option A of the phase2b archive pass (six orphan
pre-retest docs moved to `archive/outputs-pre-retest-60-tile/phase2b/`,
commit `16ee3ae5`) was the Session-74 equivalent of an ad-hoc
"SUPERSEDED" pass. Step 5 should cover remaining stale planning and
pre-launch-audit docs; scorecard §5 mark-as-superseded candidates
list is still valid.

### Step 6 — Hand to paper outline (next session or same session) — ⏸ PENDING

With interim docs at uniform quality, draft a paper outline mapping
each section to 1-3 interim docs. Proceed to write-up.

#### Step 6 polish-pass backlog

Items surfaced during Step 4 that are not load-bearing for the current
item's claim but warrant a polish pass before paper finalisation:

- **50 m TP count discrepancy (buffer-100m-diagnostics vs corrected-F1
  multi-buffer, noted 2026-04-24 during Session 75 Item 5
  verification)** — **RESOLVED 2026-04-24 (Session 75 close-out)**:
  investigated by an Explore agent as part of the end-of-session
  clearance pass. Root cause is **not** a matching-algorithm
  difference; both pipelines use the same Hungarian one-to-one
  matcher. The 2-pair gap arises from different ground-truth inputs:
  the diagnostic consumes `human-review.csv` (472 mounds at 50 m
  from yesterday's single-buffer review) while corrected-F1 consumes
  `human-review.csv` + `human-review-multi-buffer.csv` (474 at 50 m,
  adding candidate IDs 5641 and 5777 from today's multi-buffer
  re-review). Both pipelines are internally correct. Reconciliation
  notes added to both reports in commit `783f37c2`; paper-citation
  rule: use 4,110 (corrected-F1) for headline claims; 4,108
  (diagnostic) is descriptive-only for the 50 → 100 m recall-gain
  decomposition. No code/data fix needed.

- **metrics_master.csv vs metrics_master.json row-count drift (noted
  2026-04-24 during the consolidate_paper_metrics.py dry-run)**:
  committed `results/paper-tables/metrics_master.csv` has 104 rows;
  `metrics_master.json` has 100 rows. The two output files were
  generated at different times and are out of sync at HEAD. A
  deliberate re-run of `scripts/consolidate_paper_metrics.py` during
  paper finalisation will bring them back to parity (100 rows each).
  Not urgent — the JSON is the authoritative source; the 4 extra
  rows in the CSV are stale pro-high-text pool_size=10 entries from
  an earlier run. Not addressed in the Session-75 close-out because
  the plan's non-goal explicitly deprioritises output regeneration.

- **Deferred Session 77+: upgrade all bootstrap CIs from 1,000 to
  10,000 iterations** (noted 2026-04-24, mid-Session 77). The
  current 55-map + GS extended-buffer sweeps use 1,000 iterations
  for speed; the corrected-F1-multi-buffer artefact uses 10,000
  iterations. Full consistency across the paper's CI citations
  would require upgrading the 1,000-iter outputs to 10,000. Self-
  contained overnight/weekend task on sapphire. Estimated ~4× the
  current 25-min wall-clock = ~1.5 hours for the current scope;
  if combined with the "full MCC backfill" below, larger.

- **Deferred Session 77+: run MCC + 1,000-iter CIs on all 338
  F1-having analysis cells** (noted 2026-04-24, mid-Session 77;
  audit report at `/tmp/claude-1000/.../tasks/aea2ba1808115eb03.output`
  while that session's context persists, otherwise re-audit). The
  current "Option A" run covers the ~30 paper-citable cells; the
  remaining ~300 are supplementary matrix cells across
  phase3a-text-matrix (155 of 158), phase3a-image-matrix (91 of 96),
  h8-v2 (36 of 43), h12-v2 (21 of 24), retest/phase3a-consensus (14
  of 17), and h10 (1 of 5). Self-contained overnight/weekend task
  on sapphire; estimated ~11 hours serial or ~1.5 hours at 8x
  parallel. Would close the F1-without-MCC gap project-wide.

- **Script-hygiene audit: silent tile_allowlist / missing-CRS
  pathologies** (added 2026-04-24, mid-Session 78). Obs 276 surfaced
  that `scripts/score_leaderboard_cells.py` applies `--bounds` as a
  silent `tile_allowlist` hard filter on detections, without warning
  or scope-manifest output. The same session also caught that
  `scripts/materialise_pv_geojson.py` was emitting GeoJSONs without a
  CRS header — geopandas defaults these to EPSG:4326 (RFC 7946)
  while the content is actually UTM 32635, causing downstream
  reprojection to garbage (F1=0, MCC survives because tile-level MCC
  keys off the `source_tile` string, not geometry). Fix committed in
  `e1ef2190` (CRS header) + `b514ecb6` (defensive hardening).
  Broader concern: ALL proposer consensus GeoJSONs at
  `outputs/h11/*/consensus/consensus-*.geojson` exhibit the same
  silent-4326 pathology. A repo-wide sweep
  (`grep -rn "to_crs\|set_crs\|read_file" scripts/`) would catch all
  consumers that need `set_crs` (when `crs is None`) rather than
  `to_crs`. Also: a parallel audit of `results/leaderboard/cells/`
  for dimension mismatches between a cell's `n_detections` and its
  source detection GeoJSON's feature count would catch any OTHER
  artefacts of the `tile_allowlist` silent-filter pattern. Not
  urgent; can run before paper finalisation.

- **Unevaluated-consensus-geojsons audit: systematic N-subpool gap
  in tier-builder** (added 2026-04-24 (Session 78)). A systematic
  agent audit of all 1,006 non-archived consensus GeoJSONs on disk
  found that **938 (93%) have never been evaluated against ground
  truth**. Of these, **85 sit in `consensus-n*/` subdirectories** —
  a clean systematic gap caused by
  `scripts/build_tiered_leaderboard.py` globbing only `consensus/`,
  `greedy/`, and `voting/` directories and explicitly skipping
  `consensus-n{5,10}/` subpool variants. This means all N=5 subsets
  of every N=10 pool, and all N=10 subsets of every N=30 pool, were
  never scored — despite existing on disk alongside matching
  `verified-v1-n*/probabilities.json` siblings that would let them
  be evaluated immediately with no API cost. The remaining **853
  unevaluated GeoJSONs** are mostly exploratory runs under
  `h8-v2/greedy/`, `retest/`, `55maps-*`, and other non-canonical
  paths; most are unlikely to be paper-relevant, but any
  paper-citation drawn from them would first require an explicit
  evaluation. One concrete gap was filled in Session 78: Flash HIGH
  image N=5 @ T=0.7 consensus_t3 (506 features) was evaluated
  directly (F1=0.727 @ 20 m, MCC=0.664); artefacts committed to
  `results/verifier-calibration-audit/flash-high-image-N5-consensus-t3/`.
  **Recommended fix**: (a) extend the tier-builder glob in
  `scripts/build_tiered_leaderboard.py` to include `consensus-n*/`
  subdirectories so future N-subpool variants are auto-scored; and
  (b) run a one-shot batch evaluation of the 85 systematic-gap
  GeoJSONs against `mounds-reference.geojson` +
  `full_evaluation_bounds.geojson` using `evaluate_detections.py`
  (~a few minutes of CPU for all 85, no API cost). Audit evidence
  and per-file listings live with the Session 78 agent-audit output;
  a future reader can re-derive them via a recursive glob of
  `outputs/**/consensus*/consensus*.geojson` cross-referenced
  against `results/leaderboard/cells/`. Not urgent; before paper
  finalisation.

- **Build per-architecture leaderboards** (added 2026-04-24
  (Session 78); scheduled for 2026-04-25). The current leaderboard
  at `results/paper-tables/leaderboard-20m-annotated.md` and
  `results/leaderboard/era2/leaderboard_tiers_{20,30,50}m.{md,json}`
  **mixes all architectures into one ranked table** — consensus-only
  entries sit alongside Proposer + Verifier (PV) entries with no
  separation. This caused the Session 78 Q2 comparability bug where
  GS-v2 at PV-F1 = 0.854 was inserted into a consensus-only tier
  list (commit `7ab7d7fa`); that bug would not have occurred with
  per-architecture tables. **Six distinct architectures** exist in
  the project with completed evaluations but no dedicated tier
  tables: (1) N = 1 single-pass (raw); (2) consensus-only (greedy
  voting); (3) PV (Proposer + Verifier, greedy) — the canonical
  paper-headline pipeline; (4) consensus + Weighted Box Fusion
  (WBF); (5) consensus + Dawid–Skene (probabilistic); (6)
  single-pass + PV. The tier JSON schema **already has a `category`
  field** (currently populated as `"consensus"` for all Era 2
  entries). Re-purposing it to distinguish `consensus` / `pv` /
  `single-pass` / `wbf` / `ds` would be the cleanest structural fix
  — the machinery is there, just unused. The existing planning doc
  `planning/leaderboard-construction-plan.md` treats architecture as
  a **metadata field**, not a **leaderboard-stratification
  dimension**; that design decision produced the current
  mixed-architecture tables and should be revisited. **Recommended
  minimal set** for the paper: (1) consensus-only tier table (20 /
  30 / 40 / 50 m) — extractable from current mixed JSON, near-zero
  compute; (2) PV tier table (20 / 30 / 40 / 50 m) — 30 cells
  already scored, some materialised at
  `results/leaderboard/era2/pv-materialised/`, image PV anchor being
  established in Session 78 (commit pending); (3) single-pass
  baseline tier table — 28 raw N = 1 conditions would need uniform
  scoring (~1 – 2 hours local CPU); (4) [optional] cross-architecture
  comparison matrix at 20 m — F1 of same model / track across all
  six architectures, high-level story, ~30 min post-hoc.
  **Estimated effort**: 1 – 3 hours total for the three core tables;
  entirely local compute (no API spend). **Recommended fix**: (a)
  extend `scripts/build_tiered_leaderboard.py` to stratify by the
  existing `category` field, emitting one tier table per
  architecture; (b) re-run it to generate per-architecture tables;
  (c) update `leaderboard-20m-annotated.md` to cite both combined
  and per-architecture tables; (d) revisit
  `planning/leaderboard-construction-plan.md` to formalise
  architecture as a leaderboard-stratification dimension.

- **Run pairwise permutation tests across verifier calibration
  matrix** (added 2026-04-24 Session 78). The Session 78 verifier
  calibration matrix (commit landing shortly) compared 7 verifier
  variants (6 alternative prompts plus canonical `adversarial-text`)
  on 2 candidate pools (flash-high-image-n5 @ T = 0.7 and
  flash-high-text-n5 @ T = 0.7) at 487-tile Era 2 scope, reporting
  F1 / P / R / MCC at the optimum (vote_t, prob_t) along with
  calibration metrics (AUC / Brier / ECE). The matrix shows F1
  differences between variants that are often within bootstrap CIs
  (e.g. all 6 image variants cluster in F1 = 0.77 – 0.79 with
  overlapping CIs). To draw defensible conclusions about
  verifier-variant effects, we need **paired permutation tests**
  that account for shared candidate space and test whether ΔF1
  between variants is significant. Current state: each cell has
  `results/verifier-calibration-matrix/<pool>-<variant>/evaluation.json`
  (10k-bootstrap CIs) and
  `results/leaderboard/cells/session-78-<pool>-<variant>-487tile.json`
  (sweep data). The existing `scripts/pairwise_permutation.py` (or
  equivalent in the repo) is the tool — it already handled the
  Session 76 / 77 cross-track × buffer pairwise tests.
  **Recommended scope**: (1) within-track pairwise: 7 variants ×
  (7 − 1) / 2 = 21 pairs per track × 2 tracks = 42 tests at 20 m
  buffer, with False Discovery Rate (FDR) controlled at q = 0.05
  via Benjamini–Hochberg; (2) across-pool canonical vs alternatives:
  6 alternative variants vs canonical × 2 pools = 12 tests (subset
  of the above 42, just the canonical-paired ones); (3) extend to
  30 / 40 / 50 m buffers if the 20 m result is ambiguous.
  **Recommended fix / execution**: a wrapper script that (a) reads
  the 14 materialised GeoJSONs at
  `results/verifier-calibration-matrix/<pool>-<variant>-opt-20m.geojson`,
  (b) runs `pairwise_permutation.py` on each pair at each buffer
  (10k permutations, seed 42), and (c) emits a tiers +
  pairwise-test markdown (similar to the Era 2 leaderboard tier
  file) at
  `results/verifier-calibration-matrix/pairwise-permutations-20m.md`.
  **Estimated effort**: ~30 min local CPU for 42 tests × 4 buffers
  = ~170 tests; trivial API cost (none). **Why not tonight**:
  matrix artefacts are still being finalised (rsync + commit
  pending); best to run this once the matrix is stable and
  committed so the permutation tests reference stable input
  GeoJSONs.

- **Re-run canonical `verify_adversarial-text` on session-78-matrix
  shared-crops** (added 2026-04-24 Session 78). The Session 78
  verifier calibration matrix (commits `6d1cad27`, `88d6b55b`, Obs 277
  in commit `303d4f21`) compared 7 verifier prompts × 2 candidate
  pools. The canonical `verify_adversarial-text` baseline used
  existing
  `outputs/h11/pv-diag-384/flash-high-<pool>-n5/<pool>-t0.7/verified-v1-n5/probabilities.json`
  files from prior sessions — NOT the session-78-matrix shared-crops
  that the 6 alternative variants ran against. **Risk**: crop-for-crop
  parity is not guaranteed. If the canonical's crops differ from the
  shared-crops in any way (cropping geometry, PNG encoding, file
  ordering), the canonical's probabilities are not strictly comparable
  to the 6 alternatives at the candidate level. **Fix**: re-run
  `verify_adversarial-text` on the session-78-matrix shared-crops
  explicitly (same `shared-crops/candidate_manifest.json` that the 6
  alternatives used). Application Programming Interface (API) spend
  ~$8 at flex tier (2,017 image + 3,736 text candidates × Flash
  minimal thinking text-only pricing). **Importance**: matters if the
  prompt-invariance claim (Obs 277) is paper-load-bearing. At present
  the claim is robust because all 6 alternatives degrade image-track
  calibration regardless of crop set; canonical parity would tighten
  this further. **Estimated effort**: ~30 min wall-clock + $8 API.
  Requires explicit user approval per API Call Review Gate.

- **Investigate `cand_01563` parser bug in verifier response
  handling** (added 2026-04-24 Session 78). During Session 78 tile
  recovery (agent `a24ab205daa5b0cd5`), candidate `cand_01563` in the
  image-checklist cell failed deterministically with `'list' object
  has no attribute 'get'` on every retry (3 attempts × 2 cleanup
  rounds = 6 attempts, all same error). This is a **real code bug**
  in the verifier response-handling pipeline (likely
  `scripts/run_pv.py` or `scripts/lib_*.py`), triggered when the
  Gemini API returns a particular JSON shape the parser doesn't
  expect — specifically, the top-level parsed object is a `list`
  rather than the expected `dict`, and a downstream `.get()` call
  fails. **Scope of impact**: 1 candidate out of 5,753 in Session 78
  (~0.017%). Calibration metrics are unaffected, but the bug is
  latent and will recur on any candidate that elicits the same API
  response shape. **Fix direction**: add a type-check on the parsed
  JavaScript Object Notation (JSON) in `run_pv.py`'s response-handling
  path; if it's a list, either unwrap the first element or log a
  `parse_failure` with the raw response for later triage. Paired with
  a unit test that exercises the list-shape branch. **Estimated
  effort**: ~1 hour (identify the parser code, add type guard + test,
  verify against cand_01563's stored response).

- **Scope-version the `results/verifier-calibration-matrix/`
  directory** (added 2026-04-24 Session 78). Current directory layout
  is flat: `results/verifier-calibration-matrix/<pool>-<variant>/` and
  `<pool>-<variant>-opt-20m.geojson` files directly under the top
  directory. All 14 Session 78 cells share this flat root.
  **Problem**: any future verifier calibration matrix (different
  proposer pool, different scope, different buffer) will collide on
  the same flat paths. **Fix**: rename the directory to
  `results/verifier-calibration-matrix/session-78-flash-high-n5-t0.7-487tile/`
  (or similar scope-encoding subdir name) and move all Session 78
  artefacts under it. Update Obs 277 and any other doc that cites the
  flat paths. **Importance**: housekeeping — prevents path collisions
  in future sessions running similar matrices. Should be done before
  Session 79 if another calibration matrix is planned. **Estimated
  effort**: ~20 min (`git mv` + update any internal path references in
  committed JSON files; no compute).

- **[x] Clean up exact-duplicate files in
  `archive/pre-session-78-pull-2026-04-24/` on sapphire** (added
  2026-04-24 Session 78). During Session 78 matrix launch (commit
  `9ebe7346`), sapphire's working tree had 10 untracked files
  (Session-78 outputs generated on sapphire and not yet registered
  with git on that machine) that blocked `git pull`. These were
  archived to `archive/pre-session-78-pull-2026-04-24/` on sapphire to
  allow the pull to succeed. Every archived file is an **exact
  duplicate** of a file already committed to `origin/main` in its
  canonical location (Session 78 commits `aa36b638`, `4cc95e80`,
  `651b8ab4`). Zero data loss; zero recovery value. **Fix**: once
  verified safe, remove the archive dir on sapphire:
  `ssh sapphire 'rm -rf ~/Code/map-reader-llm/archive/pre-session-78-pull-2026-04-24/'`.
  Verification step: hash-compare every archived file against the
  canonical path before removal
  (`sha256sum <archived> <canonical>`); only remove if all hashes
  match. **Importance**: ~1 MB of disk + avoids confusion about what
  the archive represents. Low urgency. **Estimated effort**: ~10 min
  (hash-compare script + `rm -rf`). **DONE 2026-04-27**: directory was
  already absent from sapphire when audited (`find` returned
  `NOT_FOUND`); provenance migration note written at
  `archive/MIGRATION-pre-session-78-pull-2026-04-24.md`. No git
  movement was required because the archive was never tracked.

- **Configure GitHub identity on sapphire** (added 2026-04-24
  Session 78). During Session 78 Phase E commit step, `git commit` on
  sapphire failed with "Author identity unknown" because sapphire has
  no `user.email` / `user.name` / GitHub auth configured. Matrix
  artefacts had to be `rsync`'d back to amd-tower and committed from
  there. **Fix**: configure sapphire with `git config --global
  user.email` / `user.name` matching Shawn's GitHub identity, plus
  Secure Shell (SSH) key for `origin` push/pull access.
  **Importance**: future long-running sapphire computes could commit
  and push directly, eliminating the rsync-back step and reducing
  handover friction between machines. Useful for any future
  overnight-pipeline work. **Estimated effort**: ~10 min (user
  action — configure git + add SSH key to GitHub account). One-off.

## Session 79 entry-point queue (drafted end-of-Session-78 2026-04-25)

**You are on**: Step 6 (paper outline). Session 78 diverged into a
verifier calibration matrix; that is now complete with a strong
paper-ready finding. Backlog has grown; decide whether to run
prerequisites before the outline.

### Read first (in order)

1. This message.
2. `docs/notes/reflections/working-notes.md:13215` — **Obs 277**
   (Session 78 headline: verifier-prompt variation cannot rescue
   image-track miscalibration; canonical `verify_adversarial-text`
   is Pareto-dominant across 7 prompts).
3. `docs/notes/reflections/working-notes.md:12595` — **Obs 269**
   (motivating image-track miscalibration finding; Obs 277
   falsifies the prompt-specificity hypothesis).
4. This file — §"Step 6 polish-pass backlog" starts at line 741.
5. `archive/planning-historical-session-78/session-78-verifier-calibration-matrix-summary.md`
   (F1/P/R/MCC for 14 cells at 20 m optimum; archived 2026-05-01 — see file's SUPERSEDED banner).
6. `archive/planning-historical-session-78/session-78-matrix-calibration-summary.md`
   (AUC/Brier/ECE for 14 cells; archived 2026-05-01 — see file's SUPERSEDED banner).

### Session 78 headline findings

- **Architecture dominates prompt.** Obs 277 (commit `303d4f21`;
  numbers refreshed in Session 79 Phase A re-run, commit `b10aa7e1`)
  shows all 6 alternative prompt variants fail to rescue image-track
  calibration; canonical wins ECE on both pools. Combined with
  Session 78 Q3 cross-track calibration contrast (commit `1b7143c5`),
  the input-distribution hypothesis is supported from two
  independent tests.
- **Canonical `verify_adversarial-text` is validated as the
  production choice for calibration.** Updated post-re-run
  (2026-04-25, shared-crops parity): Pareto-dominant on **image** for
  AUC (0.857), ECE (0.179), Brier. On **text**, best ECE (0.071) and
  best Brier; AUC slightly edged by `adversarial` with images
  (0.968 vs 0.956). Pre-re-run numbers (verified-v1-n5: image AUC
  0.863 / ECE 0.188; text AUC 0.959 / ECE 0.067) were close but
  different crop set — see Obs 277 addendum.
- **F1 tier-flip on text track at crop parity.** With shared-crops
  canonical, four with-image variants (`comparative`, `adversarial`,
  `checklist`, `brief`) statistically outperform canonical on
  F1 @ 20 m by 0.013–0.023 (BH-FDR q=0.05; pairwise permutation
  tests, 10 000 iters). Canonical now sits in tier 2 of the per-arch
  Era 2 PV leaderboard at 20 m. Pareto-dominance still holds on the
  image track on AUC / ECE / Brier (all 7 image variants
  statistically indistinguishable on F1, all in image tier 3).
- **Underestimate caveat for *-text variants** (added 2026-04-25):
  the original Phase A had elevated API failure rates on the four
  text-only verifier variants, biasing their F1 numbers low by
  0.022–0.035 in pre-re-run docs. Re-run captured the full pools.

### Commits since Session 77 close

17 commits, all on origin/main, from `6b57364c` (script fix)
through `cf192345` (5-item backlog expansion). Run
`git log --oneline 6b57364c^..cf192345` for the full list.

### Matrix artefacts — paths next-session needs

- Leaderboard cells: `results/leaderboard/cells/session-78-<pool>-<variant>-487tile.json` (14 files)
- Deep evaluations: `results/verifier-calibration-matrix/<pool>-<variant>/evaluation.json`
  (F1/P/R/MCC + 10 000-iter bootstrap CIs, 14 files)
- Calibration crosstabs: `results/verifier-calibration-matrix/<pool>-<variant>/calibration.json`
  (AUC/Brier/ECE, 14 files)
- Materialised PV geojsons at 20 m optimum:
  `results/verifier-calibration-matrix/<pool>-<variant>-opt-20m.geojson`
  (14 files; UTM coords after the Session 78 CRS fix in commit
  `6b57364c`)
- Overnight pipeline script: `scripts/session-78-matrix-overnight.sh`
- Calibration computation script: `scripts/compute_session78_calibration_matrix.py`

### Step 6 backlog state (Session 79 update — most items DONE)

Carry-over items plus 6 added in Session 78. **Status updated
2026-04-25/26 (Session 79)**:

1. Script-hygiene audit: silent `tile_allowlist` filter + CRS-header
   pathologies (Obs 276). **Pending — low priority.**
2. Audit unevaluated consensus geojsons (93 % of 1 006 files).
   **Pending — low priority; the per-arch rebuild surfaced no
   downstream consumers needing them.**
3. Build per-architecture leaderboards. **DONE** (commit range
   `03bf71c8..a80a9de9` initial 12-stratum build; `ccc320ea`
   per-buffer F1 refinement). 60+ tier tables across 7 populated
   strata × 2 metrics × 5 buffers × 2 q-levels.
4. Run pairwise permutation tests across verifier calibration matrix.
   **DONE** at crop parity (commit `fffecb7d` after Phase A re-run).
5. Re-run canonical `verify_adversarial-text` on session-78-matrix
   shared-crops. **DONE** — actually re-ran the entire 14-cell
   matrix Phase A at shared-crops parity in Session 79
   (~$56-80 flex Flash; commit `b10aa7e1`). The original $8 estimate
   was canonical-only; the full re-run scope expanded after the
   2026-04-25 02:40 UTC data-loss event (see
   `docs/methodology/data-reproduction-2026-04-25.md`).
6. Investigate `cand_01563` parser bug in verifier response handling.
   **DONE (Session 80) — root cause was `data.get(...)` called on
   the parsed JSON when the model occasionally returns a
   single-element list ``[{...}]`` instead of a top-level object;
   ``AttributeError: 'list' object has no attribute 'get'`` fell
   through to the bare ``except Exception`` retry path in
   ``_call_verifier_api`` and the deterministic shape exhausted all
   retries. Fix adds an ``_unwrap_verdict_payload`` helper in
   ``scripts/lib_verifier.py`` that unwraps the first dict from a
   list-shaped payload and is invoked from both the realtime and
   batch parsing paths. Regression tests in
   ``tests/test_lib_verifier.py::TestParseVerifierResults`` and
   ``::TestUnwrapVerdictPayload``.**
7. Scope-version the `results/verifier-calibration-matrix/` directory.
   **Pending — bookkeeping only.**
8. Clean up exact-duplicate files in
   `archive/pre-session-78-pull-2026-04-24/` on sapphire.
   **[x] DONE 2026-04-27** — see
   `archive/MIGRATION-pre-session-78-pull-2026-04-24.md`.
9. Configure GitHub identity on sapphire.

Details at §"Step 6 polish-pass backlog" (line 741).

### Session 79 entry-point options

| Option | Rationale | Cost | Blocks paper? |
|--------|-----------|------|:---:|
| **A. Paper outline (Step 6)** | Main deliverable; Session 78 findings are ready for it | — | — |
| B. Pairwise permutation tests (backlog #4) | Sharpens Obs 277 "significant differences" claims before paper cites them | 30 min local | Weakly |
| C. Per-architecture leaderboards (backlog #3) | Fixes the Proposer-Verifier-versus-consensus-only comparability bug; was scheduled for 2026-04-25 | 1–3 hrs local | Weakly |
| D. Re-run canonical on session-78 shared-crops (backlog #5) | Tightens Obs 277 prompt-invariance claim from crop-set parity angle | ~$8 API + 30 min | No |

**Recommended**: **B → C → A.** Pairwise permutations and
per-architecture leaderboards are both cheap, both sharpen
paper-ready claims, and neither requires API spend. Then paper
outline with all supporting evidence verified.

### Things to NOT do without checking

- Don't trust agent outputs without adversarial verification —
  Session 78 caught two confabulations (a "missing manifests" agent
  miscounted and wrongly claimed no consensus backing; an earlier
  agent confabulated verifier-variant identifiers that don't exist).
- Don't re-run the LLM extraction pipeline without user approval.
- The canonical `verify_adversarial-text` run on the session-78-matrix
  shared-crops has NOT been done (backlog #5). Cite Obs 277
  carefully if prompt-invariance crop-parity matters.

### Guardrails carried over

- UK/Australian English (Oxford comma always).
- **Anti-confabulation rule** (new in `~/.claude/CLAUDE.md`): re-read
  source files before citing specifics; memory and scratchpad are
  pointers, not authorities. Apply especially to agent outputs.
- API Call Review Gate — get approval before any batch.
- Sapphire for heavy compute. **Note**: sapphire still has no git
  identity configured (backlog item 9); commits must return via
  amd-tower rsync until that is fixed.
- `/phase-gate` skill before scaling to a new experimental phase.

---

## Session 80 entry-point queue (composed end-of-Session 79, 2026-04-27)

> **Status update 2026-04-28 (end of Session 80)**: most queue items DONE.
> See §"Session 80 closure" immediately below this section for a roll-up
> summary, and §"Step 6 starting-state" for the paper-outline reading list.
> Original queue text preserved verbatim below for history.

Session 79 completed the per-architecture × per-Era × per-buffer × per-metric leaderboard rebuild, the cross-architecture combined leaderboard, the 55-map T=0.3 generalisation re-run, and the post-run recovery + MCC patch. Session 80 opens at **Step 6 (paper outline)**, the original deliverable.

### Read first

1. This file — the orientation layer (you are reading it).
2. `docs/notes/reflections/working-notes.md` Obs 277–281 — the substantive new findings:
   - Obs 277: verifier-prompt invariance (canonical Pareto-dominant on calibration); refreshed 2026-04-25 with crop-parity numbers
   - Obs 278: PV-architecture benefit scoped to 384-px Era 2 (paper-framing caveat)
   - Obs 279: per-buffer F1 tier-stability — broad stability (median rho 0.956) + two paper-relevant exceptions (era1/single-pass collapse 30→40 m; era3/consensus oscillation)
   - Obs 280: F1/MCC text-vs-image tier-leader divergence (5 of 7 strata; paper-load-bearing methodology decision)
   - Obs 281: temperature failure-rate hypothesis NOT supported by T=0.3 vs T=0.7 cross-run; pre-investigation "6% verifier failure" framing was a misreading
3. `results/leaderboard/per-architecture/README.md` — the 12-stratum per-arch tier tree
4. `results/leaderboard/combined/README.md` — the cross-architecture combined tier tree (Era 2 Tier 1 = **100 % PV** is the strongest paper headline)
5. `results/leaderboard/per-architecture/headlines{,_50m,_100m}.md` — top-3 per stratum at primary + parallel buffers
6. `outputs/55maps-text-high-t0.3-generalisation/cost_manifest.json` + `evaluation/evaluation.json` — the new T=0.3 generalisation run results (post-recovery; F1@50m=0.802, MCC=0.654, $67.82 total)

### Step 6 paper outline — the main deliverable

> **Status 2026-04-28**: NOW UNBLOCKED. Wave 1–4 secondary analyses,
> verifier-T pilot, phase3a MCC re-eval, and 4-run text-track analysis
> grid all DONE this session. See §"Step 6 starting-state" below for
> the curated Obs reading list ordered by paper-section relevance.

- Map each paper section (Methods / Results / Discussion / Limitations) to 1–3 interim docs from the now-comprehensive `results/` tree.
- **F1/MCC framing**: per Shawn's 2026-04-26 decision, both a methods paragraph AND a parallel-tables appendix. Methods paragraph explains the metric trade-off (F1 favours text-track recall; MCC favours image-track selectivity); appendix presents F1 + MCC tier tables side-by-side per stratum.
- **Era 2 Tier 1 = 100% PV** finding (commit `e511e2e2`) is the strongest single paper headline — should anchor the architecture-comparison section.
- **Per-buffer tier-stability findings** (Obs 279) — methods footnotes on era1/single-pass 30→40 m collapse and era3/consensus oscillation.
- **PV scope caveat** (Obs 278) — methodological footnote when introducing the cross-architecture paired analysis ("PV benefit was evaluated on the 384-px Era 2 scope...").
- **Temperature × failure-rate observation** (Obs 281) — a secondary methods note if the paper discusses run reliability; otherwise omittable.
- **55-map T=0.3 result** (~$68, F1@50m=0.802 raw vs T=0.7's 0.788) — the post-leaderboard re-run that demonstrates the leaderboard's predictive value at the chosen operating point.

### Pending user action (not for an agent)

- **Manual review of T=0.3 generalisation candidates** for corrected F1. The Streamlit review workflow (`scripts/launch_55maps_text_high_review.sh` pattern) takes the 4,349 verified detections + reviews each VLM-only candidate for promote/reject decisions. Expected corrected F1@50m ≈ 0.840 (raw 0.802 + text-HIGH correction delta +0.038, per pre-launch audit estimate). Output: `results/55maps-text-high-t0.3-generalisation/corrected-f1-multi-buffer/corrected-f1.csv`. Once landed, the analogous Dawid-Skene + paired-permutation analyses (compute_corrected_f1_multi_buffer.py + crosstab_verifier_vs_human.py) close the comparison-with-T=0.7 loop. **DONE 2026-04-28** (commit `73b7aa68` corrected-F1, `0b14e4fc` D-S aggregation; later folded into 4-run paired-permutation v2 grid via commits `a5bc9df6`, `3453ecc7`, `9a5d4461`). A second manual review for **text-MIN** also completed (commit `30088974` corrected-F1, `e344db93` D-S). All four corrected 55-map runs (T=0.3, T=0.7, image, text-MIN) now have full corrected-F1 + D-S + paired-permutation + MCC + attractor-pull coverage.

### Carry-over backlog (in priority order)

1. **Step 6 paper outline** (Task #5 still pending). The original session goal; deferred while building analytical infrastructure. **UNBLOCKED 2026-04-28** — see §"Step 6 starting-state" below.
2. **Cost-estimator overstatement bug** (Task #4 housekeeping addition): `launch_manifest.json`'s `expected_cost_usd` is consistently a 5× overstatement (T=0.7 estimate $355 → actual $69.60; T=0.3 estimate $355 → actual $67.79). Worth a one-line patch to `scripts/run_generalisation.py` so future audits don't see false-positive cost flags. Likely cause: estimator assumes max_output_tokens (8192) per call when actual averages ~500. **DONE 2026-04-28** (commit `c738c60e` — mode-aware cost + idempotent aggregate, combined with #5).
3. **`evaluation.md` and `evaluation.csv` MCC rendering gap**: `scripts/evaluate_detections.py` only writes MCC into `evaluation.json` even when `--mcc` is passed. The markdown and CSV emitters omit it. ~30 min CPU patch. **DONE 2026-04-28** (commit `bdd61bcc`).
4. **`4_detect_mounds_batch.py` resume mode breaks meta.json provenance**: the resume invocation overwrites `*.meta.json` with only the resume-batch stats, breaking `cost_manifest.json` aggregation. Recovery agent worked around this via `scripts/merge_recovery_meta.py`; the underlying script needs fixing so future recoveries don't need a workaround. **DONE 2026-04-28** (commit `1ce1a982` — preserve meta.json on resume).
5. **`run_generalisation.py aggregate-cost` rewrites launch_manifest.json + experiment_intent.md**: this clobbers the original launch metadata if invoked post-recovery. Recovery agent worked around via `git checkout` restore. Should be patched to APPEND/UPDATE rather than rewrite. **DONE 2026-04-28** (commit `c738c60e` — combined with #2; aggregate-cost now idempotent).
6. **N<10K MC-precision-flagged tests rerun at N=100K** (low priority; 2,748 tests across the per-arch leaderboard tree). User flagged as low-priority project-wide consistency cleanup. ~3-5 hr CPU at N=100K. **PENDING — low priority.**
7. **6% verifier "error" rate at T=0.3 is in-run-recovered, not unrecovered** (Obs 281 corrects this) — but the proposer 18 unrecovered failures + verifier 1 unrecovered are the true post-pipeline residual. **CLOSED 2026-04-28 via Obs 286 (verifier-T pilot Stage A)**: at T=0.0 verifier failure rate is 1.65% deterministic; at T=0.5/T=1.0 it is 0.00%. Production-default recommendation T=0.5 (Obs 287, Stage B). The pre-investigation framing was a misreading; the genuine signal is verifier-temperature-dependent.
8. **Sapphire `archive/pre-session-78-pull-2026-04-24/` cleanup** (Step 6 backlog item from earlier sessions, low priority). **DONE 2026-04-27** — directory had already been removed from sapphire's working tree in an earlier session; provenance migration note written at `archive/MIGRATION-pre-session-78-pull-2026-04-24.md`. No git movement needed; archive shadowed already-canonical commits `aa36b638`, `4cc95e80`, `651b8ab4`.
9. **Scope-version `results/verifier-calibration-matrix/` directory** (low priority bookkeeping). **IN PROGRESS 2026-04-28** (parallel agent during Session 80 close-out).
10. **`cand_01563` parser bug investigation in `run_pv.py`** — DONE (Session 80). Fix landed in `scripts/lib_verifier.py` (helper `_unwrap_verdict_payload`) with regression tests in `tests/test_lib_verifier.py`. **IN PROGRESS 2026-04-28** (parallel agent during Session 80 close-out).

### Things to NOT redo

- The T=0.3 55-map run is COMPLETE and recovered. Do not re-launch.
- The MCC re-eval is COMPLETE (commit `291715b4`). Do not re-launch.
- The recovery is COMPLETE (commit `548604d9`). Do not re-launch.
- The per-arch + combined leaderboards are COMPLETE through Session 79. Do not re-launch unless adding new conditions.
- All 5 deferred citation locations are now SWEPT (commit `16bede22`).
- **Added Session 80 (2026-04-28)**: The phase3a 252-cell MCC re-eval is COMPLETE (commit `163161a4`); off-matrix `with-mcc/` cells archived (commit `f052a92a`, Obs 288). Do not re-run.
- **Added Session 80**: All four 55-map manual reviews are COMPLETE (T=0.3 commit `73b7aa68`; text-MIN commit `30088974`; T=0.7 + image done in earlier sessions). All four corrected-F1 + D-S + paired-permutation + MCC + attractor-pull artefacts exist. Do not re-launch.
- **Added Session 80**: The verifier-T pilot Stage A + Stage B are COMPLETE (commits `f27842a5`, `b9f73bbf`, `74edfb16`). T=0.5 production-default recommendation is empirically supported but no config has been changed. Do not re-run unless validating on a new corpus.
- **Added Session 80**: Wave 1 secondary analyses (kappa, token efficiency, vote-fraction, K-consensus SD shrinkage v1 + v2) are COMPLETE. Do not re-run.
- **Added Session 80**: Wave 3 stale-analysis refresh of the 8 themes (Obs 290) is a verified canonical-aligned no-op. Do not re-audit.

### Guardrails carried over (from earlier sessions)

- **Anti-confabulation**: re-read source files before citing specifics; memory and scratchpad are pointers, not authorities. Apply especially to agent outputs.
- **Verify git-tracked status before any deletion** (Session 79 lesson — `feedback_verify_git_tracked_before_delete.md`).
- **All API outputs MUST be committed** (Session 79 lesson — `feedback_commit_api_outputs.md`).
- **No credential bytes in chat output** including SSH public keys (Session 79 lesson — `feedback_no_credentials_in_chat.md`).
- API Call Review Gate before any batch.
- Sapphire for heavy compute; sapphire git push works (configured Session 79).
- UK / Australian English; Oxford comma.

### Commit state at handoff

Working tree clean on `main`, in sync with `origin/main`. Recent work spans commits `dcd36515..548604d9` (Session 79 + recovery). All artefacts committed; no uncommitted state to carry over besides whatever final commits land in this winding-down phase.

> **Session 80 update (2026-04-28)**: ~60 commits since Session 79 close (`31aa8fda` → end of Session 80). Most recent paper-load-bearing commits: `e2ceef58` (F1 tier-ranking tables), `2bceb78c` (Obs 299 D-S calibration convergence), `9a5d4461` (4-run pairwise-permutation v2 summary), `0832acf9` (Obs 296 cap reinterpretation), `e83445d3` (Obs 291–293 cross-run findings), `dcae1596` (Obs 287 verifier-T Stage B verdict). See §"Session 80 closure" for the curated commit roll-up.

---

## Session 80 closure (2026-04-28)

### Roll-up summary

- **Total observations added this session**: 18 (Obs 282–299), plus retrospective forward-pointer updates to Obs 281 and Obs 293.
- **Total commits since Session 80 start** (after `31aa8fda` handover commit): ~60 commits, all on `main`, in sync with `origin/main`.
- **Headline deliverables**:
  - **5 backlog code fixes landed** (cost-estimator mode-aware + idempotent aggregate `c738c60e`; evaluation.md/csv MCC rendering `bdd61bcc`; resume-mode meta.json merge `1ce1a982`).
  - **Wave 1 secondary analyses** complete (kappa Obs 282; vote-fraction Obs 283; token efficiency Obs 284; K-consensus SD v1 → v2 Obs 285 → Obs 289 with shared-mode signal in 5/13 strata).
  - **Verifier-T pilot** complete (Stage A Obs 286: T=0.0 has 1.65 % deterministic verifier failures vs 0.00 % at T>0; Stage B Obs 287: F1/MCC NOT degraded; T=0.5 recommended as production default — empirically supported, no config change applied).
  - **Wave 2 phase3a MCC re-eval** complete (252 conditions canonicalised at `results/phase3a-{text,image}-matrix/<cell>/evaluation.{json,md,csv}`; off-matrix `with-mcc/` cells archived per Obs 288).
  - **Wave 3 staleness refresh** complete (Obs 290: 8 themes audited; all canonical-aligned no-ops).
  - **Wave 4: 4-run text-track analysis grid** complete (Obs 297: HIGH thinking earns its tokens at 55-map scope, T=0.7 vs T=MIN paired Δ +0.0296 BH p<0.001 at R=50 m; Obs 298: 4-run attractor-pull cap clarification 100 m most-permissive, 125 m majority; Obs 299: D-S calibration converges across text-track configs, image isolated as modality-specific).
  - **Cap analyses** (Obs 294: 55-map 125 m practitioner cap; Obs 295: GS 25 m cap, 5× tighter; Obs 296: failure-of-generalisation reinterpretation — cap difference is calibration-vs-native, not GT-precision-driven).
  - **Manual reviews** for T=0.3 and text-MIN landed; all four corrected 55-map runs (T=0.3, T=0.7, image, text-MIN) now have full corrected-F1 + D-S + MCC + paired-permutation + attractor-pull coverage.
  - **Infrastructure**: `obs-writer` agent + `/observe` slash command added in `~/personal-assistant/`.
- **4-run analysis grid completeness** (text track at corrected-F1 R=50 m anchor):
  - T=0.3 text-HIGH ✓ corrected-F1 ✓ D-S ✓ MCC ✓ attractor-pull ✓
  - T=0.7 text-HIGH ✓ corrected-F1 ✓ D-S ✓ MCC ✓ attractor-pull ✓
  - image (T=0.7) ✓ corrected-F1 ✓ D-S ✓ MCC ✓ attractor-pull ✓
  - text-MIN ✓ corrected-F1 ✓ D-S ✓ MCC ✓ attractor-pull ✓
  - 6 pairwise permutation tests across all four runs at 10 buffers each (10 K perms; commits `3453ecc7` + `9a5d4461`).
- **Things still in-flight at close** (parallel agents):
  - Sapphire `archive/pre-session-78-pull-2026-04-24/` cleanup.
  - Scope-version `results/verifier-calibration-matrix/`.
  - `cand_01563` parser bug investigation.
  - Obs 296 diagnostic tests: TP-only localisation, per-map (50,75]m variance.

### Read first if returning fresh

1. **Obs 297** (`docs/notes/reflections/working-notes.md` line 14606) — the headline 4-run paired-permutation v2 finding: HIGH thinking earns its tokens at 55-map scope. Obs 297 is the load-bearing claim for the paper's HIGH-vs-MIN comparison.
2. **Obs 296** (`working-notes.md` line 14532) — the cap reinterpretation: GS-vs-55-map cap difference is failure-of-generalisation, not GT-precision-driven.
3. **Obs 287** (`working-notes.md` line 14032) — verifier-T pilot Stage B verdict: T=0.5 production-default recommendation. Methodological note for the paper's reliability/operational section.
4. **Obs 280** (`working-notes.md` line 13642) — F1/MCC tier-leader divergence (already in Session 79 queue but still load-bearing for the parallel-tables appendix decision).
5. **Obs 289** (`working-notes.md` line 14120) — K-consensus SD shrinkage v2: shared-mode signal in 5/13 strata; supersedes Obs 285's i.i.d. proxy result.

---

## Step 6 starting-state (2026-04-28)

**Status**: NOW UNBLOCKED. All Wave 1–4 secondary analyses, the verifier-T pilot, the phase3a MCC re-eval, and the 4-run text-track analysis grid are committed. The 5 carry-over code fixes (#2–#5) are landed. Remaining backlog items are low-priority bookkeeping that does not block paper drafting.

**Recommended next action**: begin the paper-section-to-interim-doc mapping using the curated Obs reading list below.

### Obs reading list — ordered by paper section

#### Methods (verifier choice, temperature, calibration, prompt invariance)

1. **Obs 277** (`working-notes.md` line ~13215) — verifier-prompt invariance: canonical `verify_adversarial-text` Pareto-dominant on calibration metrics across 7 prompts. Methods justification for verifier-prompt selection.
2. **Obs 286, 287** (`working-notes.md` lines 13988, 14032) — verifier-T pilot Stage A + B. Stage A: T=0.0 has 1.65 % deterministic verifier failures vs 0.00 % at T>0; Stage B: F1/MCC NOT degraded by T>0. Methods note + production-default recommendation T=0.5.
3. **Obs 281** (`working-notes.md` line 13768) — temperature failure-rate hypothesis NOT supported on the proposer (T=0.3 vs T=0.7); pre-investigation "6 % verifier failure" framing was a misreading of in-run-retried transient errors. Methods footnote on what `finish_reason_counts.error` does and does not measure.
4. **Obs 269 + Obs 277 + Obs 283** as a cluster — the input-distribution hypothesis: image-track miscalibration is verifier-specific, not system-wide; canonical prompt cannot be rescued by alternatives. Methods justification for the verifier-architecture choice.

#### Results (4-run grid, leaderboard, paired tests, F1 + MCC)

1. **Obs 297** (`working-notes.md` line 14606) — the 4-run paired-permutation v2 grid headline: T=0.7 vs T=MIN paired Δ +0.0296 (BH p<0.001) at R=50 m; HIGH thinking earns its tokens at 55-map scope; T=MIN is bottom of all four corrected runs at every R≥25 m. **Most paper-load-bearing single observation in Session 80.**
2. **Obs 280** (`working-notes.md` line 13642) — pervasive F1/MCC tier-leader divergence across populated strata. Drives the parallel-tables appendix decision and the Methods paragraph on metric choice.
3. **Obs 291** (`working-notes.md` line 14246) — T=0.3 operationally optimal at canonical R=50 m on 55-map corrected corpus; paired-permutation Δ +0.018 vs T=0.7 (BH p<0.001) and +0.012 vs image (BH p=0.017); text-vs-image rank reverses across buffer.
4. **Obs 292** (`working-notes.md` line 14303) — F1/MCC tier-leader divergence reproduces on the corrected 55-map runs. Image leads MCC by 0.037; F1 leader at R=50 m (T=0.3) is NOT the MCC leader.
5. **Obs 284** (`working-notes.md` line 13902) — HIGH thinking has NEGATIVE per-token efficiency at T=0.0 image (−0.0347 ΔF1 / 1k thinking tokens); modality divergence — text-track barely positive at the same condition. Connects to Obs 297's "HIGH earns its tokens out-of-sample" via the diversity-dividend mechanism.
6. **Obs 282** (`working-notes.md` line 13830) — inter-pass candidate-match kappa is a diversity metric, not a quality metric. MIN > HIGH at matched K; T inverts the F1/MCC ranking; HIGH+T fragility corroborates the variance hypothesis (Obs 245).
7. **Obs 278** (`working-notes.md`, Session 79 commit `e511e2e2`) — PV-architecture benefit scoped to 384-px Era 2; Era 2 Tier 1 = 100 % PV is the strongest single paper headline.
8. **Obs 279** (`working-notes.md`, Session 79) — per-buffer F1 tier-stability: broad stability (median rho 0.956) + two paper-relevant exceptions (era1/single-pass collapse 30→40 m; era3/consensus oscillation).

#### Discussion (mechanisms, generalisation, calibration coupling)

1. **Obs 296** (`working-notes.md` line 14532) — GS-vs-55-map cap difference is a failure-of-generalisation effect, NOT a fundamental detector-precision shift. Per-detection mid-distance pull is 5–10× lower on the calibration corpus, with asymmetric failure modes between corpora. Reinterprets the cap gap as calibration-vs-native, not GT-precision-driven. Discussion-load-bearing for the cross-corpus generalisation argument.
2. **Obs 298** (`working-notes.md` line 14698) — 4-run attractor-pull consensus refines the 55-map cap to 100 m (most-permissive); 125 m is the majority cap. Text-MIN cleanly corroborates T=0.3's previously thin-sample 100 m floor. Discussion of the practitioner cap.
3. **Obs 299** (`working-notes.md` line 14761) — D-S calibration gap monotonic across all four corrected 55-map runs; text-MIN ≈ T=0.7 in calibration despite very different prompt configurations; image's penalty isolated as modality-specific. Discussion of D-S calibration coupling.
4. **Obs 289** (`working-notes.md` line 14120) — K-consensus SD shrinkage IS heterogeneous; v2 reveals shared-mode signal in 5/13 strata. Supersedes Obs 285's proxy-bound i.i.d. result. Discussion of consensus-stability scaling.

#### Limitations (caps, calibration ceiling, off-matrix housekeeping)

1. **Obs 294** (`working-notes.md` line 14419) — 125 m is the maximum buffer at which detection density is distinguishable from random within-tile occurrence on the corrected 55-map runs. Limitations citation for the practitioner-cap floor.
2. **Obs 295** (`working-notes.md` line 14473) — 25 m is the maximum buffer on the 4-map gold-standard; five-fold tighter than the 55-map cap. Limitations citation for the calibration-vs-native gap.
3. **Obs 288** (`working-notes.md` line 14080) — pre-existing `with-mcc/` reference cells were off-matrix one-offs, not canonical truth; archived. Limitations footnote on prior tile-level MCC narrative being matrix-canonical-aligned post-Wave-2.
4. **Obs 290** (`working-notes.md` line 14190) — Wave 3 staleness refresh: 0 substantive corrections from Phase C / Wave 2 source updates; 8 of 9 themes verified canonical-aligned. Methods/limitations note that prior narratives were already canonical-aligned.

### Suggested first writing-pass order

1. Open with **Obs 297** as the headline result + **Obs 280 / Obs 292** for the F1/MCC framing decision.
2. **Obs 286 + Obs 287** — verifier-T pilot — slot into Methods early so the production-default recommendation is set before Results.
3. **Obs 296** — generalisation-vs-calibration cap reinterpretation — anchor the Discussion.
4. **Obs 277 + Obs 281 + Obs 283** — input-distribution-specific calibration claim — slot into Methods footnotes or a focused Methods subsection.
5. **Obs 278 + Obs 279** — PV-architecture scope + per-buffer tier-stability — slot into the Architecture-Comparison Results section.

---

## Daylight follow-up sweep — 165-cell N=10K standardisation (spec for next session)

**Status**: spec'd; ready to launch under user supervision.
**Why**: Session-80 overnight standardisation upgraded 351/540 `evaluation.json` files to N=10,000 + 24 verifier-t-pilot cells via a different-shape metadata path (effective: 375/540). The remaining **165 cells** were deferred per `feedback_feature_count_crosscheck.md` because per-cell detection paths required manual reconstruction. **The post-overnight Explore audit (2026-04-28) confirmed all 165 ARE recoverable with HIGH confidence** via heterogeneous metadata mechanisms. Completing the sweep is recommended for cross-cell methodological symmetry per Obs 303 (the N=10K rationale is reproducibility, not narrower CIs; mixing N=1K and N=10K cells across the same paper creates an awkward asymmetry).

### Scope (165 cells, 4 groups)

| Group | Cells | Recovery mechanism |
|---|---:|---|
| **paper-eval** | 156 | Parent `results/paper-eval/.metadata.json` + `scripts/sapphire-paper-eval.sh` (hardcodes all conditions; line refs 44–84) + creating commit `22592f94` |
| **pairwise tile-size-30m** | 5 | Parent `results/pairwise/tile-size-30m/.metadata.json` + `configs/tile-size-comparison.yaml` (lines 22–36 have explicit detections paths per condition) |
| **55maps-cleaned-gt-evaluation** | 3 | Individual `evaluation.metadata.json` sidecar per cell (image / text-high / text-min — full CLI command shape) |
| **gold-standard-extended-buffer-sweep** | 1 root | `evaluation.metadata.json` + `extended-buffer-report.md` §3-4 (documents non-standard buffer range `[5, 10, 15, 25, 35, 45]` and 4-of-5 consensus + prob_t=0.15) |

The `with-mcc/` cell at `gold-standard-extended-buffer-sweep/with-mcc/` was already upgraded by the overnight sweep (commit `76b6592f`); not in deferred set.

### Pre-flight checklist (~5 minutes)

1. Validate `results/paper-eval/.metadata.json` and `results/pairwise/tile-size-30m/.metadata.json` parse as JSON; bootstrap section matches expected defaults (n=1000, seed=42).
2. Spot-check 3 paths exist on disk: `outputs/h11/pv-diag-384/image-n5/`, `outputs/retest/phase2b/`, `inputs/vectors/references/mounds-reference.geojson`.
3. Confirm `scripts/run_bootstrap_10k.py` (added in commit `a9fe1c1d`) can be extended to parse parent `.metadata.json` files (or write a sibling runner that handles the heterogeneous metadata sources).
4. Dry-run on one cell from each group before the full sweep — confirm CLI is correctly recovered and the output overwrites cleanly.
5. Fresh backup tag: `pre-bootstrap-10k-followup-2026-MM-DD` against current HEAD.

### Compute estimate

~30–60 min wall on sapphire at `xargs -P 16` (per-cell estimates: paper-eval cells are mostly N=1 single-pass at 384 / 512 px so per-cell ~2-5 s CPU; pairwise 5 cells at buffer 30 m only; 55maps-cleaned-gt 3 cells against the 8541-tile 55-map bounds — these are the slow ones; gold-standard 1 cell). Total CPU work substantially smaller than the overnight sweep's 361 cells; should comfortably complete in a daylight session.

### Workflow

**Plan-first per yesterday's lesson**:

1. Dispatch a Plan agent to design the recovery + sweep + verify workflow:
   - How to extend `run_bootstrap_10k.py` to handle 4 different metadata source patterns (parent sidecar / per-cell sidecar / config file lookup / report-md inference)
   - Dry-run sample selection
   - Verification queries (count expected vs actual at N=10K)
   - Per-group commit chunks
2. **Surface plan for user approval** before launch.
3. Implement agent runs the sweep, verifies, commits + pushes.
4. Update Obs 303 with a forward-pointer to the completion commit (or write a brief Obs 304 marking the standardisation complete across all 540 cells).

### Expected outcome

All 540 `evaluation.json` cells at N=10,000 bootstrap iterations. Cross-cell methodological symmetry restored. Paper methodology section can cite N=10,000 uniformly without per-cell exceptions.

### Lessons from the overnight run to apply here

1. **Orchestrator final-step robustness** — yesterday's overnight orchestrator stalled at the rebase+push step when sapphire's branch had diverged from origin (FP-class commits landed on origin while the sweep was running). The next implement agent should explicitly handle push failures with retry-on-conflict and structured error logging if auto-rebase can't resolve cleanly. ETA messaging should account for this.
2. **CI-width expectations** — Obs 303 confirms bootstrap-N controls Monte Carlo noise, not CI width. Verification spot-checks should look for N=10K presence, not for ~√10 CI tightening.
3. **Plan-first for autonomous overnight work** — even when the implement agent is well-prompted, a Plan agent first surfaces edge cases for user approval before launch.

### Cross-references

- **Obs 303** (`working-notes.md` line ~15019) — why N=10K matters (reproducibility, not narrower CIs). Forward-points to this spec.
- **Bootstrap-10K commit chain**: `4b31aae0..51f438bd` (11 commits); rollback tag `pre-bootstrap-10k-2026-04-28` → commit `5040f5b4`.
- **Metadata-investigation Explore audit**: 2026-04-28 finding that all 165 deferred cells are recoverable with HIGH confidence (logged in Session 80 closing chat transcript).

---

## Outstanding to-dos for next session (audit 2026-04-28)

> **⚠️ Largely superseded** — items 1, 2, 3, 5 closed in Session 81; items 10, 11 closed in Session 82 (commit `10bcf376`). Authoritative current-state is the §"Session 81 closure roll-up" Items 1–16 status table below. Section preserved for narrative continuity.

Identified by an Explore agent surveying planning docs, working-notes (Obs 282–303), recent `report.md` files, repo-cleanup-backlog, and detector-confidence planning docs immediately before Session 80 close-out. Items below are **NOT** already covered in the Session 80 closure / Step 6 starting-state / daylight follow-up sweep sections above. The paper outline itself is the main deliverable for next session and is excluded from this list. Items are ordered by priority within band; user should sequence per their judgement.

### High priority (paper-load-bearing)

#### 1. GS-side FP classification via VLM (closes Obs 302's missing comparator)

- **Source**: Obs 302 caveat + `results/55maps-fp-classification/report.md`.
- **Description**: Obs 296 Test #2 (FP categorisation) ran on the 4 corrected 55-map runs but lacks a gold-standard (GS) comparator. The hypothesis that the GS corpus has water-feature / spot-height FP modes (your manual-review intuition) cannot be directly tested without running the same Gemini classification on ~80 GS false positives.
- **Cost**: ~$0.05 USD, < 30 min wall.
- **Unblocks**: Discussion cross-corpus asymmetry claim with empirical FP-class data on both sides.
- **Approach**: mirror `scripts/55maps-fp-classify.py` against GS verified-detections; identify FPs (no human review on GS, so use distance-from-curator-GT > some threshold as the FP filter); same prompt + Soviet-topo vocabulary anchor.

#### 2. Audit secondary-effects reports for surviving `with-mcc/` citations

- **Source**: Obs 288 operational implications §1–3.
- **Description**: Obs 288 found the phase3a `with-mcc/` cells were off-matrix one-offs (worst case: image high-T0.7 K=10 t=7 corrected MCC 0.3831 → 0.6765 at +0.29 absolute). The matrix sweep is now canonical, but earlier narratives may still cite the off-matrix numbers. Audit `results/secondary-effects/`, `results/phase3a-image-matrix/`, and `results/paper-eval/` reports for any surviving citations and redirect to matrix-canonical.
- **Cost**: audit-only, ~30 min.
- **Unblocks**: paper citation cleanliness; closes Obs 288 operational follow-up.

#### 3. Characterise high-pull FP maps (per-map distractor tail)

- **Source**: Obs 301 follow-up question.
- **Description**: Per-map FP-anchoring rates on the 55-map text-track are heavily right-skewed (median 0 %, with 2–3 maps driving the corpus rate). Which specific maps? What shared features? If the high-pull tail shares an identifiable cartographic feature (dense numeric labels, vegetation hatching, a specific stylistic variant), the Discussion gains specificity beyond "the detector is sometimes bad on some maps".
- **Cost**: < 1 hour ad-hoc diagnostic; reuse `scripts/analyse_55maps_per_map_shell_variance.py` outputs + manual map inspection on the top-3 high-pull maps per run.
- **Unblocks**: actionability of Obs 301's right-skew finding for paper Discussion.

### Medium priority (strengthening claims)

#### 4. Detector-confidence calibration pilot (vote-fraction-as-proxy validation)

- **Source**: `planning/detector-confidence-calibration-pilot.md` (spec'd in Wave 1; not yet executed).
- **Description**: H-a (Obs 283) proposed vote-fraction as a behavioural proxy for detector confidence. The pilot (zero API cost; uses an existing K=30 cell on the 4-map gold-standard corpus) tests whether Spearman ρ between `vote_count` and observed P(TP) ≥ 0.7 (proxy sound) vs < 0.5 (proxy unreliable; escalate to flag-scoping per `planning/detector-confidence-flag-scoping.md`).
- **Cost**: ~1 hour compute; $0 API.
- **Conditional**: only execute if the paper plans to discuss detector confidence as a graded quantity.
- **Unblocks**: vote-fraction reportability decision; H-a paper scope.

#### 5. Verify citation metadata in secondary-effects / phase3a-image-matrix reports

- **Source**: Obs 288 operational implications §2–3 (related to but distinct from item #2).
- **Description**: Spot-check that any prior image-high-T0.7 MCC citations in secondary-effects analyses have been redirected to matrix-canonical cells. Item #2 is about `with-mcc/` citations specifically; this item is about other paper-cited MCC values that may have shifted post-Wave-2.
- **Cost**: audit-only, ~30 min.
- **Unblocks**: paper-cited MCC numbers are matrix-canonical-aligned.

### Low priority / optional / deferred

#### 6. Multi-condition vote-fraction calibration extension

- **Source**: `planning/detector-confidence-calibration-pilot.md` line 92.
- **Description**: A single-condition pilot (item #4) does not guarantee vote-fraction soundness on image conditions or low-T deterministic regimes. A multi-condition extension would characterise K-dependence and condition-family generality.
- **Cost**: 2–4 hours per condition; varies.
- **Defer unless**: pilot passes AND the paper wants to scope calibration robustness across conditions.

#### 7. K-consensus SD shrinkage heterogeneity footnote

- **Source**: Obs 289 paper-framing discussion.
- **Description**: Obs 289 reveals 5/13 strata depart from i.i.d. variance reduction (strongest: image-MIN-T1.0, β₁ = −0.118). If the paper cites K=N consensus as a noise-reduction strategy, a footnote should flag these strata as shared-mode failure regions.
- **Cost**: 20 min narrative addition; no code.
- **Unblocks**: paper's K-consensus framing accuracy.

#### 8. Durable metadata mitigation for `evaluate_detections.py` + `build_tiered_leaderboard.py`

- **Source**: `planning/repo-cleanup-backlog.md` and `archive/planning-completed-session-81-82/ci-rerun-todo.md` lines 96–116.
- **Description**: Add a `_metadata` block embedding to `scripts/evaluate_detections.py` `evaluate_single_condition()` and `build_tiered_leaderboard.py` so that future `evaluation.json` outputs auto-include bootstrap parameters + CLI args. Prevents recurrence of the metadata-recovery work the daylight follow-up sweep needed.
- **Cost**: 15 min dev + smoke test.
- **Defer unless**: significant new evaluations are anticipated post-paper.

#### 9. TP-only localisation bias check (Obs 296 diagnostic test follow-up)

- **Source**: Obs 296 diagnostic tests (Test #1 done; this is a refinement).
- **Description**: A strengthening test for the cap-as-calibration-vs-native claim — demonstrate that FP-anchoring is not caused by TP mis-localisation in the (50, 75] m band. Re-use existing TP-only output + a new filter on the (50, 75] m sub-cohort.
- **Cost**: re-use outputs, < 1 hour.
- **Unblocks**: deeper sub-band analysis if the Discussion needs it; otherwise the existing TP-only diagnostic (Obs 300) suffices.

#### 10. Fix Niculiță misattribution as "Meylemans et al."

- **Source**: User report 2026-04-29 (turned up while using the project as a teaching example).
- **File**: `docs/methodology/research/claude-burial-mound-vlm-methodology.md` line 45 (and references section line 298).
- **Description**: Line 45 currently reads *"Only the Romanian Random Forest study (Meylemans et al.) meets gold-standard validation criteria:"*. Verified 2026-04-29 by Explore agent: the cited DOI `10.3390/s20041192` resolves to **Niculiță, M. (2020). "Geomorphometric Methods for Burial Mound Recognition and Extraction from High-Resolution LiDAR DEMs". *Sensors* 20(4): 1192** (single author, Alexandru Ioan Cuza University, Iași). Methodology matches (Random Forest on LiDAR DEMs, Romanian, externally validated, 93 % detection rate). "Meylemans et al." is a pure misattribution with no apparent basis in the literature. The references section at line 298 also lacks author attribution and should be expanded to the full citation.
- **Cost**: ~5 min edit.
- **Unblocks**: research-integrity hygiene before any paper text cites or paraphrases this methodology document.
- **Approach**: (a) line 45 — replace "Meylemans et al." with "Niculiță, 2020"; (b) line 298 — expand the bullet to the full citation `Niculiță, M. (2020). "Geomorphometric Methods for Burial Mound Recognition and Extraction from High-Resolution LiDAR DEMs". *Sensors* 20(4): 1192. doi:10.3390/s20041192`.

#### 11. Fix Guyot table-row mischaracterisation (method + metric labelling)

- **Source**: User report 2026-04-29 (turned up while using the project as a teaching example).
- **File**: `docs/methodology/research/claude-optimising-symbol-detection-benchmarks.md` line 68 (in the benchmarks comparison table; header at line 61).
- **Description**: Line 68 currently reads `| Random Forest + U-Net | Neolithic mounds (LiDAR) | — | 98% | 98% | LiDAR derived | ~2 hours |` against the header `| Method | Application | F1 | Precision | Recall | Training Data | Training Time |`. Verified 2026-04-29 by Explore agent: the cited DOI `10.3390/rs10020225` and the cross-reference at `claude-tile-size-and-overlap.md:63` both confirm the actual study is **Guyot, A., Hubert-Moy, L., & Lorho, T. (2018). *Remote Sensing* 10(2): 225**, and the actual method is **MSTP (Multi-Scale Topographic Position) + Random Forest** — NOT "Random Forest + U-Net". Additionally, the headline metric is **Cohen's kappa = 0.98** (a single integrated metric), not separate 98 % precision and recall — the duplicated 98 % cells appear to be a kappa-decomposed-into-two-columns labelling artefact.
- **Cost**: ~5 min edit.
- **Unblocks**: research-integrity hygiene; the benchmarks comparison table is potentially paper-Discussion-cited.
- **Approach**: (a) replace "Random Forest + U-Net" with "MSTP + Random Forest"; (b) replace `— | 98% | 98%` with `— | — | —` and add a footnote noting the headline metric is Cohen's kappa = 0.98 (or extend the table with a "kappa" column if other rows also report kappa-style metrics).

### Recommendation: priority sequencing for next session (after paper outline)

1. **Daylight follow-up sweep** (already in spec above) — execute first; unblocks methodological uniformity.
2. **Item #1 GS-side FP classification** ($0.05, ~30 min) — completes the asymmetric-failure-mode discussion-block evidence.
3. **Item #2 `with-mcc/` citation audit** + **Item #5 broader MCC citation audit** (~1 hour combined) — paper-citation cleanliness.
4. **Item #3 high-pull FP map characterisation** (< 1 hour) — actionability of Obs 301.
5. **Item #4 detector-confidence pilot** (conditional on paper's detector-confidence framing).
6. **Items #10 + #11** — citation-correction edits (~10 min combined); can be done any time before paper drafting cites these methodology documents.
7. Items #6, #7, #8, #9 — defer unless paper drafting surfaces a specific need.

---

## Session 81 closure roll-up (2026-04-29)

### Items 1-16 status reference (after Session 81 closures + Session 82 closures 2026-05-01)

| # | Title | Status |
|---|---|---|
| 1 | GS-side FP classification | ✅ **DONE Session 81** |
| 2 | `with-mcc/` citation audit | ✅ **DONE Session 81** — clean (zero surviving off-matrix citations) |
| 3 | High-pull FP map characterisation | ✅ **DONE 2026-04-29** (Obs 304 — strong shared-feature hypothesis REJECTED) |
| 4 | Detector-confidence calibration pilot | Pending; conditional |
| 5 | Broader MCC citation audit | ✅ **DONE Session 81** — clean (0 of 6 spot-checked diverged) |
| 6 | Multi-condition vote-fraction calibration | Pending; conditional |
| 7 | K-consensus SD heterogeneity footnote | Pending |
| 8 | Durable metadata mitigation | Pending; partly superseded (BCa fix added schema 1.1 with `_metadata.bootstrap.method`, `coverage_status`, etc.) |
| 9 | TP-only localisation bias check | Pending |
| 10 | Niculiță citation fix | ✅ **DONE Session 82** — commit `10bcf376` |
| 11 | Guyot citation fix | ✅ **DONE Session 82** — commit `10bcf376` |
| 12 | BCa re-run all evaluation cells | ✅ **DONE Session 81 close-out** — commits `014d6248..4eea8768` (2026-04-30); doc was stale, audit confirmed 526/526 in-scope cells at BCa N=10K |
| 13 | Bet-test inspection app | ✅ **DONE Session 81** — Obs 312 (0 / 177 review errors) |
| 14 | K-35-076-2 participatory-GIS coverage history | ✅ **CLOSED 2026-05-01** by Obs 317 — premise superseded; corrected per-map breakdown locates the within-corpus outlier at K-35-062-2 (Rakovski, 9.18 %), explained by inter-student-skill variance — no investigation required |
| 15 | GS >125 m FP-side 6-crop manual inspection | Pending — user-driven, deferred (will handle in a later session) |
| 16 | Two timed-out cells N=10K re-run | ✅ **DONE 2026-04-30 17:07** — `flash-text-high-t-0-7` and `flash-text-minimal-t-0-7` in `results/paper-eval/n1/384px-all-buffers/`; both at `n_iterations=10000, method=BCa` |

### Items closed this session — Session 81 detail

- **#1 GS-side FP classification** — Commits `ee4f18cb` (v1, FP-only closed list) → `9fa6db4e` (v2 with burial-mound categories added after the v1 TP-side calibration check surfaced the FP-only-list design issue). Findings: Obs 306 (TP-side calibration validation; v1's 60 % `contour-ring` leakage was a closed-list design artefact, not classifier hallucination), Obs 307 (cross-corpus chi-square Monte Carlo p = 0.0028 at >125 m; different failure modes by corpus), Obs 308 (55-map v2 reclassification 15.8 %, provisional pending bet-test). v1 archived to `archive/gs-fp-classification-v1-pre-burial-mound-list/`. 55-map FP-classification also re-run with v2 closed list at commit `ec21c8ef`; v1 archived to `archive/55maps-fp-classification-v1-pre-burial-mound-list/`. Total cost ~$0.78 ($0.17 GS v1 + $0.19 GS v2 + $0.58 55-map v2).
- **#2 `with-mcc/` citation audit** — Audit-only Explore agent found zero surviving off-matrix citations; all narratives cite matrix-canonical values (image HIGH-T0.7 K=10 t=7 at MCC 0.678; text HIGH-T0.7 K=30 t=26 at MCC 0.620). The archival in commit `f052a92a` was clean.
- **#3 High-pull FP map characterisation** — Commit `6d798e83`, Obs 304. Strong form of shared-cartographic-feature hypothesis REJECTED via qualitative inspection of 9 high-pull + 3 low-pull control maps. Parsimonious explanation: small-denominator arithmetic + reference-point density variance. Paper Discussion implication: report per-map distribution shape (median + IQR) without attributing right-skew to identifiable features.
- **#5 Broader MCC citation audit** — Audit-only Explore agent found 0 of 6 spot-checked MCC citations divergent from matrix-canonical (≥0.005 threshold). One off-matrix value flagged but correctly framed in source as a single-cell library-variant probe (SCALE4-T0.7 in `secondary-effects.md:19`).

### New items added this session — Session 81

#### 12. BCa re-run all evaluation cells (migration pass under new bootstrap method)

- **Source**: Obs 309 (BCa + Mit-3 fix, commit `2026999a`).
- **Description**: The bootstrap method change from percentile to BCa is committed as code, but existing eval.json files retain pre-change percentile CIs. For methodological consistency, all paper-cited evaluation cells need re-running under BCa. Point estimates are deterministic-given-seed (unchanged); only CI bounds shift (typically <0.005 absolute on F1). The new method also populates the Mit-3 sparse-coverage flag (`coverage_status`, `ci_unreliable`) in eval.json metadata, suppresses CI display in eval.md/csv for the 5 cross-grid pairwise cells.
- **Cost**: zero API; estimated 30-60 min sapphire CPU at 16-way parallelism for ~540 cells.
- **Approach**: extend `scripts/build_bootstrap_10k_queue_followup.py` (or write a sibling) to enumerate ALL committed eval.json files; re-run via the standard pipeline; per-group commits mirroring the daylight sweep structure (`b774238b..6b611174`).
- **Sequencing**: dispatch after the 2 timed-out cells (item #16) finish; or include them in the migration if they haven't landed.
- **Unblocks**: methodological consistency; closes the "code change committed, data pending" status from Obs 309.

#### 13. Bet-test inspection app implementation (177 v2-burial-mound crops)

- **Source**: Plan APPROVED at commit `8d2f7f47` (`archive/planning-completed-session-81-82/v2-burial-mound-bet-test-app-plan-2026-04-29.md`).
- **Description**: Implement the Streamlit re-review app for the 177 v2-burial-mound reclassifications (Obs 308). Bet: review-error rate < 2 % of 1,675 (the `not_mound` corpus reviewed) → < 34 errors among 177 (= 19 % of reclassifications). Three verdicts (`real_mound_my_error`, `v2_overclaim`, `edge_case_ambiguous`) + skip; calibration-sample blinding sample default ON; re-review at exact classifier view (~150 m / 768 px); persist verdicts to CSV; resume support.
- **Cost**: zero API; ~2-3 hours dev (per plan §8 effort estimate). User wall time: 60-90 min for 177 candidates.
- **Sequencing**: implement then run; result resolves Obs 308's "provisional" status into a definitive review-error rate finding for the paper.

#### 14. Investigate K-35-076-2 participatory-GIS coverage history (FN-rate outlier)

✅ **CLOSED 2026-05-01** by Obs 317 — premise superseded.

- **Source (original)**: Obs 305 outlier flag (52.5 % FN rate; 52 likely-FN against only 47 student-GT mounds).
- **Closure note**: Obs 316 (trapezoidal-graticule active-area correction) and Obs 317 (per-map breakdown) supersede the Obs 305 framing. Under the corrected analysis, the within-4-GS per-map FN range is **2.76 %–9.18 %**, with K-35-062-2 (Rakovski, 9.18 %) — not K-35-076-2 — as the within-corpus outlier. The explanation is **inter-student-skill variance** (each map digitised by exactly one student, with no double-marking or consensus signal), not a structural participatory-GIS coverage problem. No further investigation needed.

#### 15. Manual inspection of GS >125 m FP-side burial-mound classifications (6 of 14)

- **Source**: Obs 307 caveat (6 / 14 = 42.9 % of strict GS FPs classified as `burial-mound` or `triangulation-point-on-burial-mound`).
- **Description**: Could reflect curator missed-mounds (despite triple-checking) OR v2 prompt over-claim. Manual inspection of those 6 crops would distinguish. Each crop is a single 150 m-window image, fast to assess.
- **Cost**: zero compute; user wall time ~20 min for 6 crops.
- **Conditional**: if any of the 6 are genuine missed mounds, this becomes a paper Limitations note about the inherent fallibility of even triple-checked curator GT. If all 6 are v2 over-claims, the prompt-bias caveat in Obs 307 strengthens.

#### 16. Two timed-out cells N=10K re-run

✅ **DONE 2026-04-30 17:07**.

- **Source**: Obs 310 (daylight sweep close-out).
- **Description**: `flash-text-minimal-t-0-7` and `flash-text-high-t-0-7` (in `paper-eval/n1/384px-all-buffers/`) timed out at 3600 s wall under 16-way parallelism on the daylight sweep. Re-run on sapphire with no-timeout.
- **Outcome**: Both cells landed 2026-04-30 17:07 with `_metadata.bootstrap.n_iterations = 10000` and `method = "BCa"`. Paths:
  - `results/paper-eval/n1/384px-all-buffers/flash-text-high-t-0-7/evaluation.json`
  - `results/paper-eval/n1/384px-all-buffers/flash-text-minimal-t-0-7/evaluation.json`
- **Closure**: daylight follow-up sweep is now complete across the deferred 165-cell set; methodological symmetry with the rest of the BCa migration (item #12) is intact.

### Updated recommendation: priority sequencing for next session

Now that the GS classification + v2 work landed, the new sequencing reflects what's left:

> **⚠️ Updated 2026-05-01 in light of Session 82 closures.** Items #13, #14, #16 are CLOSED. Items #10, #11, #12 are in flight (separate agents dispatched today). The remaining post-Session-82 sequence is correspondingly shorter — see §"Session 82 closure (2026-05-01)" below for the consolidated post-closure to-do list.

1. **Step 6 paper outline** — the original deliverable; further unblocked by cross-corpus chi-square evidence (Obs 307), FN-rate refinement (Obs 305 → Obs 316/317), and the 4-GS canonical analysis (Obs 316/317).
2. ~~**Item #12 BCa re-run all cells**~~ — ✅ DONE in Session 81 close-out (commits `014d6248..4eea8768`); audit confirmed 2026-05-01.
3. ~~**Item #16 two timed-out cells**~~ — DONE 2026-04-30 17:07.
4. ~~**Item #13 bet-test app**~~ — DONE Session 81 (Obs 312, 0/177).
5. ~~**Items #10 + #11 citation fixes** (~10 min)~~ — ✅ DONE Session 82 (commit `10bcf376`).
6. **Item #15 GS 6-crop manual inspection** (~20 min) — pending; user-driven, deferred to a later session.
7. ~~**Item #14 K-35-076-2 history**~~ — CLOSED 2026-05-01 by Obs 317 (premise superseded).
8. **Items #4, #6, #7, #8, #9** — defer per original priority.

### Session 81 deliverables roll-up

- **6 new Obs entries (305-310)** committed at `73b21b6b`.
- **~25 commits** total (range `dd0693c4..73b21b6b`); ~$0.78 API spend ($0.36 GS FP-class v1+v2, $0.58 55-map FP-class v2, near-zero on plans/audits).
- **Major code change**: BCa + Mit-3 sparse-coverage flag in `scripts/lib_advanced_metrics.py` (commit `2026999a`); rollback tag `pre-bca-mit3-2026-04-29` pushed; 24 new tests added; all 839 tier-1 tests pass.
- **Daylight sweep N=10K standardisation completed** (162 of 165 cells; 2 timed out, re-running): 4 per-group commits `b774238b..6b611174`; pro-n10 evaluation.json gap recovered at commit `f1cf5086`; closes Obs 303 forward-pointer (Obs 310).
- **Plans approved this session**: bet-test app plan (`8d2f7f47`); pairwise CI fix plan (`4da5c254`); GS FP-classification plan revised (`edd2ecce`).
- **Three citation-related artefacts**: Niculiță + Guyot misattributions confirmed (added to to-do as items #10 + #11, commit `dd0693c4`); audit reports for input-expansion (`29b8cc64`) and Sobotkova 2023 historical decomposition (in Obs 305).
- **Working-notes updated**: Obs entries 305-310 (`73b21b6b`); llm-observations.md Session 81 entry (this commit).

### Things to NOT redo in next session

- The GS FP-classification is COMPLETE at v2 with burial-mound categories; do NOT re-run unless adding new conditions.
- The 55-map FP-classification is COMPLETE at v2; do NOT re-run.
- The BCa code change is COMPLETE; the migration re-run (item #12) is the only remaining work in that loop.
- The pairwise CI bug is METHODOLOGICALLY CLOSED; the 5 sparse-coverage cells will get the `ci_unreliable` flag automatically when item #12 runs.
- The Sobotkova 2023 reference has been read; do NOT re-fetch unless the paper Methods needs more from it.

---

## Session 82 closure (2026-05-01)

### Headline

The 4-GS student-vs-curator FN/FP analysis was re-run under Pulkovo-1942 trapezoidal-graticule active-area bounds, eliminating 17 spurious FPs that were artefacts of students digitising into the black-collar padding outside the cartographic neat-line. **Corrected counts: TP = 539, FP = 0, FN = 30, F1 = 0.9729, FN rate 5.27 % (95 % CI 2.92–8.80 %, bootstrap-by-sheet, 10 K iterations, seed 42).** This **vindicates Sobotkova 2023's published 5.0 % FN / 0.1 % FP**, replacing Session 81's "we disagree with Sobotkova" framing. The follow-up Obs 317 reframes the 4-GS-vs-55-map gap (5.27 % vs 8.87 %) as **inter-student-skill variance + small-N**, not a structural cartographic difference between corpora — within-corpus per-map range is **2.76 %–9.18 %** (spread 6.4 pp), wider than the 3.6 pp cross-corpus mean gap.

### Today's commits (2026-05-01)

Range `33bce297..6f15b8c9` (8 commits):

- `a0ee28c6` — `data(gs-4maps): filter Hairy + reuse review UI for manual dedup`
- `983aac5e` — `chore(gs-4maps): make dedup-review launcher accept threshold arg`
- `a8b576d5` — `data(gs-4maps): apply student-GT dedup review (23 decisions; 4 merges)`
- `01f57133` — `analysis(gs-4maps): student-vs-curator GT FN/FP/TP — Sobotkova comparator`
- `794ac446` — `tooling(gs-4maps): Streamlit review for 17 student-GT false positives`
- `0bb7c448` — `analysis(gs-4maps): correct FP via trapezoidal graticule bounds` ← key correction
- `eff34bfd` — `docs(reflection): Obs 316 — trapezoidal active-area correction vindicates Sobotkova 2023`
- `6f15b8c9` — `docs(reflection): Obs 317 — 4-GS-vs-55-map gap explained by variance`

### Closures landed today

- **4-GS FN-rate thread** — corrected analysis is paper-Methods-ready; Sobotkova 2023 vindicated; lower-bound framing demoted to footnote.
- **K-35-062-2 (Rakovski) outlier** (Session-82 review thread §8 question 2) — closed by Obs 317; explanation is single-student-per-map variance, no structural cartographic problem; curator-records lookup not needed.
- **Non-Hairy provenance** (Session-82 review thread §8 question 1) — closed by user's domain answer: students were asked to digitise all benchmarks and triangulation points NOT on mounds, alongside the burial-mound symbols; the working theory at the time was that some unmarked benchmarks might sit on mounds the cartographers had missed; the theory turned out wrong (cartographers were accurate), and the 262 non-Hairy features are genuinely off-mound infrastructure. Hairy filter correctly excludes them. **Paper-Methods sentence**: *"the student dataset includes ~32 % features outside the Russian 1:50k mound-symbol class — naked benchmarks and triangulation points captured under a contemporaneous working theory; we exclude them from the FP-rate denominator."*
- **Item #16 (two timed-out N=10K cells)** — verified DONE 2026-04-30 17:07: `flash-text-high-t-0-7` and `flash-text-minimal-t-0-7` in `results/paper-eval/n1/384px-all-buffers/`; both at `n_iterations=10000, method=BCa`. Daylight follow-up sweep is now complete across all 165 deferred cells.

### Pending before paper outline (post-Session-82)

- **Item #12 BCa re-run all evaluation cells** — ✅ DONE in Session 81 close-out (`014d6248..4eea8768`, 2026-04-30); audit run on 2026-05-01 confirmed 526/526 in-scope cells at BCa N=10K. Continuity-doc roll-up was simply stale.
- **Items #10 + #11 citation fixes** (Niculiță; Guyot) — ✅ DONE Session 82 (commit `10bcf376`).
- **Item #15 GS >125 m FP-side 6-crop manual inspection** — user-driven, deferred (will handle in a later session).
- **Step 6 paper outline** — the original post-Step-4 deliverable; **NOW UNBLOCKED**. The next major user-driven task.

### Things to NOT redo in Session 82+ (addendum)

- **The 4-GS Hairy filter + dedup + active-area-clipped FN/FP analysis is CANONICAL** (Obs 316 + 317; commits `a0ee28c6..6f15b8c9`); do NOT re-run. Outputs at `results/student-gt-fn-rate-analysis-gs4/` with `bootstrap_summary.json` + `per_sheet_confusion.csv` are the paper-Methods-ready references.
- **Trapezoidal-graticule active-area bounds are the definitive sheet bounds** for the 4 GS maps (Pulkovo-1942 / EPSG:4284, datum offset ~130 m vs WGS84). Pre-fix rectangular-bounds artefacts archived; do NOT cite the retracted 3.06 % FP rate or the 9.1 % cumulative FN rate.

---

## Session 83 closure (2026-05-03)

### Headline

The T=0.7 55-map text-high generalisation run was fully recovered: **160 of 160 originally-failed proposer tile-passes recovered (100 %)**; downstream consensus / verifier cleanup / cost-manifest / evaluation / Dawid-Skene / corrected-F1 / MCC / paired-permutation / attractor-pull all rebuilt against the post-recovery candidate set. Verified detections went 4,143 → 4,164 (+21); F1 raw @50 m 0.7896 → 0.7920; F1 corrected @50 m 0.8260 → 0.8273; D-S F1 0.8129 → 0.8142; MCC @50 m 0.648 [0.633, 0.662]. **Total run cost 2026-04-18 launch ($69.60) + 2026-05-02 recovery ($57.10) + 2026-05-03 verifier cleanup ($0.10) + FP-classify share ($0.01) = $126.81** (per `outputs/55maps-text-high-generalisation/cost_manifest.json::totals.cost_usd`).

The recovery propagation arc surfaced and fixed **three bugs** worth flagging at paper-Methods-Discussion-meta level (parser realtime-vs-batch asymmetry, D-S row-position, `cost_manifest` cleanup-overwrites-meta) and identified **three outstanding recoveries** under the same realtime-parser fix (image HIGH, text-MIN, GS-v2; ~163 tiles total) — now added to the "Pending before paper outline" queue.

### Today's commits (2026-05-02 to 2026-05-03)

The full propagation chain spans roughly 21 commits from `1ea92b9c` (recovery driver) through `e07dae37` (final D-S re-runs). Major commits, in chronological order:

- `f5df7a09` — `docs(reflection): Obs 318 — T=0.7 proposer failure-rate magnitude correction` (25 → 160)
- `1ea92b9c` — `analysis(t0.7-recovery): add T=0.7 single-round recovery driver`
- **`731466d8`** — `analysis(t0.7-recovery): proposer recovery for 160 failed tiles + meta merge` ← stage-2 recovery (160/160 recovered; +612 net new detections; cost overrun $57.10 vs $0.50 cap)
- `c913b69b`, `3219aa76` — Obs 319 (T=0.7 vs T=0.3 recovery-cost asymmetry)
- **`d7f85978`** — `analysis(t0.7-recovery): consensus + verifier cleanup + cost-manifest + verified rebuild` (consensus 9,131 → 9,206; 74 new candidates verified; verified geojson rebuilt)
- **`e3aef6fa`** — `fix(parser): add 3-tier JSON repair to realtime proposer` (root-cause fix; ports the canonical Tier 1 trailing-comma strip from batch to realtime; +163 outstanding tiles across 3 other runs recoverable)
- `e20f3e18` — `analysis(t0.7-recovery): N=10K BCa evaluation re-run (baseline + full-buffer + extended-buffer)`
- `aeb9fb7f` — `analysis(t0.7-recovery): pairwise-permutation v2 — 3 pairs touching T=0.7`
- **`a9e280a3`** — `fix(dawid-skene): use stable candidate_id instead of row position (safe under re-cluster)`
- **`7f05f529`** — `fix(aggregate-cost): merge pre-recovery verifier-meta backups (handles cleanup-overwrite case)` (surfaces the full $126.81 by reading both primary and `*.pre-recovery-*.backup` siblings)
- `baf1497a` — `data(gt): add missing curator GT mound — second of two touching mounds at K-35-064-3 cand 4264` (GT 4,744 → 4,745 features)
- `9b80621e` — `data(review): T=0.7 55-map review-app — 7 entries from 2026-05-03`
- `f533fda5` — `analysis(t0.7-recovery): re-evaluate against updated GT (4745 features, baf1497a)`
- `f6eaeca9` — `analysis(t0.7-recovery): corrected-F1 multi-buffer with 6 new reviews + 1 new GT mound`
- **`33435aab`** — `analysis(t0.7-recovery): attractor-pull v2 + FP-classify + TP-localisation + per-map shell + student-GT-FN` (Phase 4-6 propagation; FP-classify $0.5821 across all 4 corpora)
- `366f9c66` — `analysis(t0.7-recovery): re-aggregate D-S on text-high (post-recovery + new GT)`
- **`e07dae37`** — `analysis(t0.7-recovery): re-run DS-vs-human cross-tab on text-high` ← final propagation step

### Bug discoveries surfaced and fixed

1. **JSON parser realtime-vs-batch asymmetry** — fixed at `e3aef6fa`. The realtime proposer in `scripts/4_detect_mounds_batch.py` previously called `json.loads()` directly and treated any `JSONDecodeError` as unrecoverable. The canonical Tier 1 trailing-comma strip already existed in the batch path at `scripts/lib_batch_api.py:920`. The patch ports it as a public helper `parse_response_with_repair()` with three tiers (regex strip → permissive json5 → bracket-balance fallback), recovering ~92 % of historical failures (per the audit logged in the commit message).
2. **Dawid-Skene row-position bug** — fixed at `a9e280a3`. D-S indexing relied on row position, which is unsafe under re-cluster (the recovery added new consensus rows, shifting positions). Patched to use stable `candidate_id` indexing.
3. **`cost_manifest` cleanup-overwrites-meta** — fixed at `7f05f529`. `aggregate_cost_manifest` previously read the post-cleanup `verified/run.meta.json` and silently dropped the original verifier meta (preserved per Session 80 convention as `*.pre-recovery-*.backup`). Patch teaches the script to glob for backup siblings of every meta file it reads (verifier and proposer per-pass) and sum costs / tokens / wall-clock / item counts across primary + backups; merged backups are recorded under `cost_manifest._metadata.cleanup_recovery_metas_merged` for audit trails.
4. **Obs 281 magnitude correction** (Obs 318, commit `f5df7a09`) — the previously-cited 25/42,545 figure was a Pass 1 only count; the audit total across all 5 passes is 160/42,705. Documentation updates downstream propagated the corrected denominator.

### Documentation updates landed today

Seven docs were updated in a single commit to propagate the post-recovery state across the documentation surface:

1. **`configs/run-configs/55maps_text_high_generalisation_post_run_report.md`** — refreshed top-line F1 / D-S / cost / token / unit-cost / scope tables with post-recovery values; added a "Recovery 2026-05-02/03" subsection covering the propagation chain, bug discoveries, outcomes, and outstanding recoveries.
2. **`results/documentation-audit/README.md`** — added a 2026-05-03 post-recovery annotation flagging that the audit's `text-high` figures are pre-recovery and pointing to the post-run-report's recovery subsection.
3. **`results/documentation-audit/audit-summary.md`** — light annotation noting the post-recovery numbers and the corrected $552.30 three-run total measured spend.
4. **`results/documentation-audit/priority-backfill.md`** — light annotation; surfaces the 3 outstanding recoveries (image HIGH, text-MIN, GS-v2) as new backfill targets.
5. **`results/documentation-audit/results-audit-2026-04-21.md`** — light annotation noting that §A4 cells cite pre-recovery state.
6. **`results/documentation-audit/verification-2026-04-21.md`** — light annotation noting that the verification's claims were correct as of the verification date.
7. **`planning/paper-writeup-continuity.md`** — this file; Session 83 closure section added.

### Pending before paper outline (post-Session-83)

- **Three outstanding recoveries under the realtime-parser fix** (commit `e3aef6fa` audit identified 163 tiles total recoverable; none yet actioned):
  - `outputs/55maps-image-generalisation/` (image HIGH)
  - `outputs/55maps-text-min-generalisation/` (text MIN)
  - `outputs/h11/gold-standard-v2/` (GS-v2)

  Each requires the same propagation pattern as the T=0.7 recovery executed today: proposer recovery driver → consensus rebuild → verifier cleanup → `aggregate_cost_manifest` (with `7f05f529`'s backup-merge) → re-evaluation → D-S re-aggregation (with `a9e280a3`'s stable-id fix) → corrected-F1 + MCC + paired-permutation + attractor-pull. Cost is expected to be modest under the 3-tier parser fix (~92 % of failures recoverable on the first attempt without retry storms; the T=0.7 $57 overrun was a worst-case scenario for stubborn parse-failures).

- **Item #15 GS >125 m FP-side 6-crop manual inspection** — user-driven, deferred (carried over from Session 82).
- **Step 6 paper outline** — the original post-Step-4 deliverable; **NOW UNBLOCKED** (post-Session 82) modulo the 3 outstanding recoveries above. Whether to outline the paper now or after the 3 recoveries is a sequencing call for the next session.

### Things to NOT redo in Session 83+ (addendum)

- **The T=0.7 55-map recovery is COMPLETE** (commits `731466d8..e07dae37`); do NOT re-launch the proposer or re-aggregate downstream artefacts. The 4,164 verified detections + F1 0.7920 / 0.8273-corrected / 0.8142-D-S / 0.648-MCC at 50 m are the canonical post-recovery values.
- **The three bug fixes are COMMITTED** (`e3aef6fa` parser, `a9e280a3` D-S row-position, `7f05f529` cost-manifest backup-merge); do NOT revisit unless adding regression tests or extending the patches to new code paths.
- **Obs 318 + 319 are COMMITTED** to working-notes; do NOT modify (refinements should come as new Obs per project policy).
- **The pre-recovery `*.pre-recovery-*.backup` and `*.pre-gtupdate-*.backup` files in `outputs/55maps-text-high-generalisation/` and `results/55maps-text-high-generalisation/` are preserved by design** (per the cost-manifest fix's design and the project's "archive, never delete" policy); do NOT clean them up.

---

## Session 82 entry-point queue (composed end-of-Session-81-review 2026-04-30)

> **⚠️ Largely superseded 2026-05-01** — the FN-rate thread that this section was scoped around closed today via Obs 316 + 317 (4-GS trapezoidal-graticule correction → Sobotkova 2023 vindicated; cross-corpus heterogeneity small; gap dominated by inter-student-skill variance). The read-first list and recommended Session-82 sequence (A–C) below are RESOLVED. See §"Session 82 closure (2026-05-01)" immediately above for the headline + commit chain. Open questions 1–3 are CLOSED inline below; questions 4–5 are non-blocking.
>
> *Original Session-82 plan-state preserved below for the audit trail. The plan was executed and the FN-rate thread closed via Obs 316 + 317; see §"Session 82 closure" above for canonical current state. Sobotkova 2023's 5.0 % was vindicated, not contradicted — the 4-GS estimator under proper trapezoidal-graticule bounds is **5.27 % FN / 0.00 % FP**, matching Sobotkova's published 5.0 % / 0.1 %. Stale Session-81 framings ("calculation issue", "estimators converge at 9–11 %", "we disagree with Sobotkova") have been pruned from the prose below.*

Session 81 ran a long follow-up review thread covering: bet-test inspection (Obs 312), settlement-mound re-inspection (Obs 313 — three-category result + two-mechanism framework), Cat 2 symbol-ID search (Obs 314 → Obs 315 — closed with negative result), the 4-map raw student-data audit (planning + smoke-test in `archive/planning-completed-session-81-82/dedupe-raw-gs-student-data-plan-2026-04-30.md`, commit `d5dc0e87`), and the FN-rate framing thread (closed Session 82 by Obs 316 + 317; see banner above). The full failure-mode taxonomy is now at paper-Discussion-quality level. Next-session pickup is mostly small high-value items.

### Read-first for Session 82

1. **This file's `## Session 81 closure roll-up`** above (current state of the to-do list)
2. **Obs 312-315** (`docs/notes/reflections/working-notes.md`) — bet-test resolution + failure-mode taxonomy + symbol-ID closure
3. **`archive/planning-completed-session-81-82/dedupe-raw-gs-student-data-plan-2026-04-30.md`** (commit `d5dc0e87`) — the dedup plan + the §8 open questions on the 4 GS maps' raw student data
4. **GS student-maps review thread** (this section, immediately below)

### GS student-maps review thread — status + next-session approach

**Where we are**: the **raw pre-curation student data** for the 4 GS maps lives at `inputs/raw-student-review-production-maps/Mapmounds/` (dual-projection shapefiles; ~10,825 features total across the 55-map and 4-map work). Within the 4 GS sheet bounds: **822 student-marked features**.

**Audit findings from Session 81** (see §"Session 82 closure" above for the corrected canonical numbers; bullets below preserved as historical plan-state with stale FN-rate framings pruned):

- **Two student-feature populations** in the 822: **560 "Hairy" (Russian 1:50k mound symbols)** with 97 % match to curator GT; **262 non-Hairy** with 3 % match, spatially disjoint (median 1.2 km from any Hairy point) — different feature class entirely, NOT duplicates.
- **Dedup smoke-test (50 m radius, Hairy-only)**: 4 / 560 = 0.7 % — minimal duplication, contradicting the user's recall of "lots of duplicates". The `scripts/review_gt_duplicates.py` (commit `dea1155f`) prior dedup methodology is preserved as reference but is unnecessary on this corpus.
- **TM 30-548's published 0.1 % FP rate** for student data is consistent with the Hairy-only subset; the 38.7 % apparent FP rate from earlier audits was an artefact of including non-Hairy features in the FP denominator.
- ~~**Cumulative FN rate across the 4 GS maps: 9.1 %**~~ — **SUPERSEDED 2026-05-01**: Session 81's 9.1 % was an artefact of rectangular-bounds clipping that included the black-collar padding outside the cartographic neat-line. Re-run under Pulkovo-1942 trapezoidal-graticule active-area bounds gives **FN = 5.27 %, FP = 0.00 %** (Obs 316), vindicating Sobotkova 2023's published 5.0 % / 0.1 %.
- ~~**4-map and 55-map FN-rate estimators converge at 9-11 %**~~ — **SUPERSEDED 2026-05-01**: under the corrected 4-GS estimator (5.27 %), the 55-map estimator (8.87 %) is now ~3.6 pp higher; Obs 317 reframes the gap as inter-student-skill variance + small-N (within-corpus per-map range 2.76–9.18 %, spread 6.4 pp, wider than the cross-corpus mean gap), not a structural cartographic difference between corpora.

**Five open questions** (from `archive/planning-completed-session-81-82/dedupe-raw-gs-student-data-plan-2026-04-30.md` §8, in priority order):

1. **Non-Hairy provenance** (highest paper-Methods-relevance) — ✅ **CLOSED 2026-05-01** (user domain answer). Students were asked to digitise **all benchmarks and triangulation points NOT on mounds** alongside the Russian 1:50k burial-mound symbols. The contemporaneous working theory was that some unmarked benchmarks might sit on mounds the cartographers had missed; the theory turned out **wrong — cartographers were accurate**, the 262 non-Hairy features are genuinely off-mound infrastructure (naked benchmarks + triangulation points). The Hairy filter correctly excludes them; this is data-by-design, not a data-quality issue. **Paper Methods sentence** (one-line): *"the student dataset includes ~32 % features outside the Russian 1:50k mound-symbol class — naked benchmarks and triangulation points captured under a contemporaneous working theory; we exclude them from the FP-rate denominator."*
2. **K-35-062-2 outlier at 15.88 % FN** — ✅ **CLOSED 2026-05-01** by Obs 317. Per the corrected per-map breakdown (range 2.76 %–9.18 % across the 4 GS maps; spread of 6.4 pp wider than the 4-GS-vs-55-map mean gap of 3.6 pp), Rakovski's elevated rate is **single-student-per-map variance**, not a structural cartographic problem. No curator-records lookup needed.
3. **Update Obs 305** with the 4-map cross-validation finding — ✅ **CLOSED 2026-05-01**. Subsumed by Obs 316 (active-area-corrected 4-GS analysis vindicates Sobotkova 2023's 5.0 % FN / 0.1 % FP) and Obs 317 (per-map breakdown + variance reframing). Obs 316/317 cross-reference Obs 305 internally; no in-place edit to Obs 305 required (working-notes is append-only by project policy).
4. **822 vs 848 count discrepancy** — ✅ **RESOLVED, non-blocking**. Was a methodology-difference noise between two audits during Session 81; not load-bearing on any paper finding.
5. **Dedup pass on Hairy data** — **SKIP** (originally low-value at 0.7 % dupe rate; reconfirmed not worth running).

**Recommended Session-82 sequence**: ✅ **RESOLVED 2026-05-01**. (A), (B), (C) all closed via Obs 316 + 317 in a single thread; the FN-rate paper-Methods-ready framing landed in `working-notes.md` Obs 316 (line ~15300) and Obs 317 (line ~15400). The original sequence is preserved below for narrative continuity.

- (A) ~~**Investigate the 262 non-Hairy points** (~30 min): geographic inspection + cross-reference user's curator-process records. Output: a single Obs entry (or Obs 305 amendment) explaining the non-Hairy population.~~
- (B) ~~**K-35-062-2 brief investigation** (~20 min): user's curator records likely have notes on which student digitised which maps; correlate with FN rate.~~
- (C) ~~**Update Obs 305** with the cross-validation + non-Hairy framing (~15 min, paper-Methods-ready).~~

After (A)-(C), the FN-rate thread is closed paper-ready. The remaining items 12-16 from the Session 81 closure-roll-up to-do list (BCa migration done; bet-test app implemented; etc.) are mostly closure work or low-priority bookkeeping.

### Failure-mode catalogue is paper-Discussion-ready (no Session-82 action needed)

Per Obs 313 + 315, the failure-mode catalogue is at mechanism level:

- **Mechanism A — colour-veto failure** (~75 % of v2 reclassifications): square + rounded black features with hachures
- **Mechanism B — central-glyph anchor** (~25 %): closed contour + benchmark / spot-height / triangulation glyph
- **Mechanism C — source-domain ambiguity** (small, illustrative): mud-geyser crater (item 285) is the cleanest example

No symbol-identity dependence; the paper writes the catalogue mechanically. **Mechanism A and Mechanism C have specific testable methodological fixes** (colour-as-hard-veto in proposer prompt; benchmark-as-spatial-join post-classification) — usable as future-work bullets.

### Outstanding paper-text decisions (for drafting time, not Session 82)

- ~~**Sobotkova 2023 correction**~~: **DROPPED 2026-05-01** — Obs 316 vindicated Sobotkova's 5.0 % FN / 0.1 % FP; the 4-GS estimator at 5.27 % FN / 0.00 % FP matches. No correction story needed; paper Methods can cite Sobotkova as a converging independent estimate.
- **K-35-062-2 by name**: name in paper, or anonymise as e.g. "one map with elevated FN"? Specificity vs discretion call. (Note: under the corrected per-map breakdown the spread is 2.76–9.18 %, not the originally-cited 15.88 % outlier — see Obs 317.)
- **Recall-anchor**: image-track / R = 150 m or a more conservative anchor? Currently the most-generous; happy to revisit. (The 11.15 % recall-adjusted central from Obs 305 is unaffected on the 55-map side, but cross-corpus framing now uses the 4-GS 5.27 % vs 55-map 8.87 % gap per Obs 317.)
- **Dedup mention in Methods**: include the "0.7 % dedup rate" as a corpus-quality statistic, or omit?
- **Hairy / non-Hairy framing**: how prominently to flag in Methods? Single sentence vs supplementary table.

These don't block Session 82; they're paper-drafting-time decisions.

### Things to NOT redo in Session 82

- The bet-test inspection is COMPLETE (0/177); do NOT re-launch the Streamlit app
- The settlement-mound re-inspection is COMPLETE (87/29/1/0 split); do NOT re-launch
- The TM 30-548 ≤425 search is COMPLETE with negative result for Cat 2; do NOT re-search via TM 30-548 (a primary Russian-language guide would be a different effort, and is deferred)
- Obs 312, 313, 314, 315 are committed; do NOT modify (refinements should come as new Obs per project policy)
- The dedup pass on the 4-map student data is NOT WORTH RUNNING (0.7 % rate); do NOT execute `scripts/review_gt_duplicates.py` on this corpus
- **The 4-GS Hairy filter + dedup + active-area-clipped FN/FP analysis is CANONICAL** (Obs 316 + 317, commits `a0ee28c6..6f15b8c9`); do NOT re-run. TP=539 / FP=0 / FN=30 / F1=0.9729 / FN rate 5.27 % (95 % CI 2.92–8.80 %) under Pulkovo-1942 trapezoidal-graticule bounds is the paper-Methods-ready finding.

---

## Session 78 entry-point queue (approved mid-Session 77 2026-04-24)

Paste these into the next session; all are approved and scoped.

### Q1 — GS text-HIGH Era 2 companion artefact (cheap, ~10 min sapphire)

Context: the existing `gold-standard-extended-buffer-sweep/verified_detections.geojson` (250 features, Era 3 scope) was intentionally bounds-filtered to the 327-tile allowlist to match the canonical leaderboard cell `gold-standard-v2-greedy-v1-327tile.json`. This is documented in `extended-buffer-report.md` §3. It is **not a bug** — it is a scope choice for tile-level comparability with h8-v2 / h10 v2 / h12 v2 (all Era 3 by data-hygiene). See forensic audit trail in Session 77 log (search for "forensic" / "250-feature anomaly").

Task:

1. **Materialise** full-scope PV GeoJSON for GS v2 text-HIGH (371 features; no bounds filter):

    ```bash
    python scripts/materialise_pv_geojson.py \
        --consensus outputs/h11/gold-standard-v2/consensus/consensus-4of5.geojson \
        --probabilities outputs/h11/gold-standard-v2/verified-v1/probabilities.json \
        --vote-t 4 --prob-t 0.15 \
        --output outputs/h11/gold-standard-v2/verified-v1/verified_detections_full-scope.geojson
    ```

    Note: consensus-4of5 has 607 features; probabilities.json indexes map to those 607 (597 parsed, 10 failed). materialise_pv_geojson.py's "threshold-1 consensus" docstring is misleading for this run — use consensus-4of5 with `--vote-t 4` and it produces the correct 371 features. Confirmed by forensic audit 2026-04-24.

2. **Evaluate** at Era 2 bounds with MCC + 1000-iter CIs:

    ```bash
    python scripts/evaluate_detections.py \
        --detections outputs/h11/gold-standard-v2/verified-v1/verified_detections_full-scope.geojson \
        --ground-truth inputs/vectors/references/mounds-reference.geojson \
        --bounds inputs/vectors/bounds/384/full_evaluation_bounds.geojson \
        --buffers 5 10 15 20 25 30 35 40 45 50 --bootstrap 1000 --seed 42 --mcc \
        --output-dir results/gold-standard-extended-buffer-sweep-era2 \
        --label "gold-standard-text-high-era2"
    ```

    ~~Expected headline: F1 ≈ 0.722 at 20 m, F1 ≈ 0.736 at 50 m (from forensic audit's preview evaluation). These are LOWER than the existing Era 3 numbers (F1 = 0.815 at 20 m, 0.826 at 50 m) because pool_160 contributes 116 additional GT mounds and 121 detections that were excluded under Era 3.~~

    **Retracted 2026-04-24 (Session 78 Q1 actual result)**: Era 2 GS text-HIGH gives F1 = 0.854 [0.821, 0.883] at 20 m, F1 = 0.873 [0.844, 0.901] at 50 m, MCC = 0.778 [0.726, 0.828]. See `results/gold-standard-extended-buffer-sweep-era2/evaluation.json`. Independent cross-check via `score_leaderboard_cells.py` on the same 487-tile scope gives F1 = 0.8536 at 20 m / 0.8734 at 50 m (vote≥1 prob≥0.15, n = 371) — two scripts agree. The pre-run "forensic audit" 0.722/0.736 estimate was a hand-calculation, not a logged run; it assumed a specific decomposition of what adding pool_160 detections would do to precision/recall that the actual computation does not bear out. The Era 3 CI [0.7833, 0.8586] and Era 2 CI [0.821, 0.883] overlap at 20 m, so the difference between point estimates is within sampling variance on different tile subsets (the Era 3 327-tile pool is a hierarchical stratified random subset of the 487-tile universe per `scripts/select_calibration_tiles.py:73-77`; no difficulty bias).

3. **Scope-pair narrative**: add a note to the existing Era 3 `gold-standard-extended-buffer-sweep/extended-buffer-report.md` §3 explaining that (a) the existing artefact is Era 3 scope to match h8-v2/h10-v2/h12-v2 sibling comparability, (b) the new Era 2 companion is at `results/gold-standard-extended-buffer-sweep-era2/` with F1 = 0.873 at 50 m, (c) CIs overlap with Era 3 → difference is within sampling variance on different random tile subsets. Update the 4 downstream citation sites to be scope-qualified (labels only; do NOT re-interpret the narrative):

    - `meta-findings-summary.md` T1 §3.4 (Batch C "Student-GT position noise" bullet).
    - `55maps-cross-track-comparison/report.md` §6 (where it cites 0.8225 as the GS plateau).
    - `limitations-consolidation/report.md` §2.3 (student-GT position noise caveat).
    - `evaluation-scopes.md` §8.1 (paper-claim era tagging).

    ~~The cross-corpus curve-shift narrative (GS plateaus fast vs 55-map doesn't) survives intact — the magnitude just tightens (Era 3 gap was +0.193 at 20 m; Era 2 gap is +0.099 at 20 m). Still real, methodologically cleaner when reported at matched scope.~~ Cross-corpus gap direction is unchanged but do not re-characterise the magnitude — scope labels change, analysis does not.

### Q2 — Uniform-scope leaderboard (cheap, ~10 min sapphire + 5 min doc)

Re-run the gold-standard-v2 leaderboard cell at Era 2 (487 tiles) so the paper's leaderboard is uniformly Era 2 rather than mixed-scope. The phase3a matrix cells are already Era 2 (487 tiles, 405 / 415 features); only the gold-standard cell is still at 327 tiles. Producing an Era 2 gold-standard cell aligns the leaderboard across all paper-citable conditions.

Task:

1. Run `scripts/score_leaderboard_cells.py` with Era 2 bounds (`full_evaluation_bounds.geojson`) and the same vote_t = 4 / prob_t = 0.15 thresholds.
2. Save the new cell as `results/leaderboard/cells/gold-standard-v2-greedy-v1-487tile.json`, preserving the existing 327-tile cell.
3. Update the primary `leaderboard-20m-annotated.md` to use the 487-tile cell at tier 1. ~~F1 at 20 m will drop from 0.890 (327-tile) to ~0.72 (487-tile); the condition's leaderboard rank may shift.~~ **Updated 2026-04-24 (actual Session 78 Q2 result)**: F1 at 20 m changes from 0.890 (327-tile, vote≥4 prob≥0.15) to **0.8536** (487-tile, vote≥1 prob≥0.15, n = 371); at vote≥4 prob≥0.15 the 487-tile cell gives the same 0.8536 (all consensus-4of5 candidates have vote_count ≥ 4). Leaderboard rank impact to be assessed during the doc update. The top-of-leaderboard text-HIGH 16-of-30 + PV condition at 0.890 is a different cell (phase3a-matrix, already 487-tile) and is NOT affected.
4. Add a "scope unification 2026-04-25" note to `leaderboard-20m-annotated.md` explaining the re-scoping and preservation of the 327-tile sibling.

Non-blocking for the Q1 task; can be done in the same session.

### Q3 — text-HIGH manual review downstream compute (on-demand, ~30 min)

When the user completes the text-HIGH multi-buffer review (Streamlit app launched via `scripts/launch_55maps_text_high_review.sh`; output at `results/55maps-text-high-generalisation/human-review-multi-buffer.csv`), run the parallel analyses that the image track has:

1. `compute_corrected_f1_multi_buffer.py` — with `--review-today results/55maps-text-high-generalisation/human-review-multi-buffer.csv --review-yesterday ""` (no yesterday file for text-HIGH). Output to `results/55maps-text-high-generalisation/corrected-f1-multi-buffer/`.
2. Replicate Obs 269 verifier-calibration-crosstab on text-HIGH (same `scripts/crosstab_verifier_vs_human.py` pattern). Expected result similar to image track since same verifier v1 prompt; confirm.
3. Update `55maps-cross-track-comparison/report.md` §4 to add text-HIGH corrected F1 (closes the "only image is human-reviewed" scope caveat flagged in that doc).
4. Update `limitations-consolidation/report.md` §2.3 (same closure).

Not blocking — depends on user's review being complete.

### Q4 — Step 6 paper outline (the main deliverable)

With the metric suite now uniformly populated (MCC everywhere there's F1, after Q1 / Q2 land; ~30 paper-citable cells covered in Option A), all per-analysis reports at exemplar-equivalent quality, and the new Era 2 scope pair, the project is ready to hand to a paper outline. Session 78 entry: **Step 6 paper outline** mapping each paper section (Methods / Results / Discussion / Limitations) to 1 – 3 interim docs.

### Context that should survive into Session 78

- **Audit-fallout finding (Session 77)**: my "F1 = 0.904 is Pro image HIGH T=0.7" chat error was caught by three verifier agents before it propagated into any committed doc. The guardrail pattern works. Load-bearing lessons captured in memory (`feedback_feature_count_crosscheck.md`, `feedback_384px_scope_preference.md`, `feedback_mcc_with_f1.md`).
- **The 59-map disjointness finding (commit `267134b2`)**: 4-map GS + 55-map generalisation are disjoint sheet-sets, 59 sheets total. Documented in `evaluation-scopes.md` §11.
- **Three new memories saved this session** (all in `~/.claude/projects/-home-shawn-Code-map-reader-llm/memory/`): MCC-with-F1, 384-px-scope-preference, feature-count-crosscheck.
- **Open investigation item (lower priority)**: are there other pre-Session-77 artefacts that used `score_leaderboard_cells.py`'s `tile_allowlist` silent-filter? The GS extended-buffer-sweep was intentional, but the pattern could have been applied elsewhere too. An audit across `results/leaderboard/cells/*.json` for cells with dimension mismatches vs their source detection GeoJSONs would catch this. Not urgent; can run before paper finalisation.
- **Script-hygiene item**: `scripts/score_leaderboard_cells.py` silently applies its `--bounds` as a hard filter via `tile_allowlist`. The docstring doesn't obviously warn that candidates outside bounds get dropped from the materialised detection set. A 2-line docstring addition and/or a scope-manifest output field would prevent repeat confusion.

## User decisions (2026-04-21 end-of-session)

Explicit user confirmations recorded here so the next session doesn't
relitigate them:

1. **Exemplar nominated**: gold-standard-subtype-classification
   report (see above).
2. **Meta-findings consolidation IS next**: synthesise Obs 262-273
   into a single paper-Discussion-shaped doc per Step 3 in the plan.
3. **Parsimonious deep-dives**: trust the interim-doc citations by
   default. Descend to raw results / working-notes ONLY when (a) an
   interim doc citation is missing, (b) a causal / mechanism claim
   needs scrutiny, or (c) a paper-headline number is being drafted
   for the final manuscript. Do NOT re-verify 82/85 doc-audit PASS
   claims — they've been verified.
4. **Fact-check-agent for the paper draft (deferred)**: when the
   paper is near complete, build a dedicated adversarial fact-check
   agent that reads ONLY the paper draft + source-of-truth files
   and pass/fails each numeric claim. Modelled on the
   documentation-audit verifier pattern already committed
   (`verification-2026-04-21.md`), but scoped to the paper text
   rather than the interim audit. NOT a task for the opening of the
   next session — a later-stage QA step.

## Critical guardrails for the next session

1. **Do NOT cite figures from `archive/v2-verifier-contamination/`
   or `archive/flawed-audit-2026-04-19/`**. They're preserved for
   methodology transparency, NOT as authoritative sources.
2. **Do NOT re-run the LLM extraction pipeline**. No more API spend.
   If a paper claim requires a number we don't have, flag as a
   potential-recalculation item; do not add to a batch without
   user approval.
3. **Do NOT trust a "fluent prose" interim doc claim without a
   citation**. The flawed-audit-2026-04-19 taught us this. Spot-check
   a claim any time it matters for a paper-headline number.
4. **Distinguish the two "E47" entries**: `protocol-errata.md` line
   1233 is "Primary spatial matching buffer reverted to preregistered
   20 m"; `working-notes.md` line 6553 is "Erratum E47: Proposer
   Prompt Substitution". Shared ID from historical re-numbering —
   clearly cite which file when referencing.
5. **Use UK / Australian English throughout**: analyse (not
   analyze), behaviour, colour, etc.

### Added 2026-04-23 (Session 74)

The following five items extend the original five guardrails above
and are specific to Step 4 work.

1. **Sub-agent outputs are drafts, not verdicts**. Session 74
   dispatched seven background Explore / general-purpose agents;
   three returned wrong or mis-calibrated verdicts that would have
   caused wasted compute or mis-cited papers if acted on unchecked
   (Phase 2b tile count wrong by a factor of 22; Phase 3a
   contamination verdict completely reversed on direct sjoin test;
   subtype-MCC contamination flagged where `ensure_utm_crs` helper
   makes it immune). For any load-bearing claim from a background
   agent, run a direct-evidence check against the filesystem or
   actual code execution BEFORE relaying it to the user or acting on
   it. See `docs/notes/reflections/session-reflection.md` §Session 74
   and `docs/notes/reflections/llm-observations.md` §Session 74 for
   the full framing.
2. **Phase 2b carry-forward Option B residual is MANDATORY for Step
   4 item 3**. When synthesising
   `results/retest/phase2b/analysis_summary.md` you must ALSO
   (a) create a retest-era
   `results/phase2b-carry-forward-parameters.md` equivalent based on
   the 340-tile K=3 retest data, (b) repoint
   `results/phase2c-carry-forward-parameters.md:126` to the new
   retest-era doc, (c) archive the pre-retest
   `results/phase2b-carry-forward-parameters.md` to
   `archive/outputs-pre-retest-60-tile/phase2b/` alongside the six
   files already archived 2026-04-23 (commit `16ee3ae5`). Tracked
   redundantly in four places: retention banner in the file itself;
   scorecard §3.15 "Superseded pre-retest artefacts"; scorecard §3.15
   level-up notes sub-task; scorecard §6 sequencing item 3.
3. **CRS patch is prophylactic; no active re-compute needed**. The
   `scripts/analyse_consensus_sweep.py::consensus_to_gdf` fix (commit
   `eb2cf23c`) protects against future consensus-path computes but
   was only hit by today's Phase 2b MCC. Other consumers
   (`evaluate_detections.py::load_geojson`,
   `lib_consensus.ensure_utm_crs`) use different paths that dodge the
   bug. Contamination scope verified narrow by three background
   agents; do not re-check unless a new consensus-rebuild-path
   compute is added. A future hardening (refactor `consensus_to_gdf`
   to use `ensure_utm_crs`) is a Step 4 nice-to-have, not a blocker.
4. **UNINTENDED-T1.0 retention is by design**. The two
   `outputs/h11/{consensus,single-pass}-384-UNINTENDED-T1.0/`
   directories are retained with dual-role framing: origin = E43
   deviation; retention = serendipitous Era 2 / 487-tile T=1.0
   coverage for 157 downstream references where preregistered Phase 2b
   (340 tiles) cannot extend. Do NOT archive; the READMEs
   (commit `5ae94041`) document the framing. Scientific T=1.0
   evidence rests on Phase 2b (Obs 116 / 177 / 209), not E43 data.
5. **Scorecard §6 is the Step 4 work-plan**; this file's §"Need"
   list is superseded-but-preserved. If §6 and this file disagree
   about Step 4 order, §6 wins.

## Context-budget note

> **⚠️ Superseded 2026-04-23** — Steps 1-3 used more context than this
> estimate anticipated (Session 74 spent most of its budget on the
> Step 2 re-inventory cascade and the CRS-bugfix / contamination-
> investigation thread). Updated estimates below.

Original Session 73 estimate, preserved for reference:

- Step 1-2 alone: ~15 % context
- Step 3 (meta-findings): ~25 % context
- Steps 4-5: ~20 % context
- Retains ~40 % headroom for the paper-outline and first section
  drafts.

Revised estimates after Session 74 actuals:

- Steps 1-3 actual: ~60-70 % context (one session, though the session
  had several tangential threads — CRS bugfix, UNINTENDED disposition,
  phase2b archive — that a more disciplined Step-3-focused session
  might avoid).
- Step 4 comprehensive (10 items, 11-15 h): probably 2-3 sessions, not
  one. The four L-effort synthesis items (h8-v2, h10, phase2b, h11) are
  each context-heavy because they span many JSON files. Consider doing
  one or two per session with commit + sync between.
- Step 5 (~30 min) and Step 6 (paper outline) can probably share a
  single session after Step 4 completes.

Rule of thumb that held across Sessions 73 and 74: checkpoint-commit
at natural boundaries and start a new session rather than pushing
past ~75 % context. Session 74 pushed close to that ceiling by the
end (several agent dispatches, several file-read cycles); next session
should aim for fewer concurrent threads.

## Commit state at handoff

**Session 77 mid-session handoff (2026-04-24)**: working tree clean at
commit `80025eaf`, `main` only (no stray branches), **NOT yet pushed to
`origin/main`**. Session 77 added 6 commits beyond Session 76:
`dfbf88a5`, `1220f339`, `eaf6c8ba` (Batch A data-gen),
`34074873`, `b33a818a` (Batch B1 archive reorg), `80025eaf` (Batch B2
reflections). Combined Session-76+77 log:
`git log --oneline 8949dc00..HEAD`.

**Session 76 handoff (earlier in this chain)**: was clean at commit
`b960a3cf` after 17 Session-76-only commits from `f700acd9` → `b960a3cf`.
See §"Session 76 status" below for the per-item table.

Session 76 commit sequence (bottom-up on `git log`):

- `f700acd9` docs(crosstab): level-up — exec summary, Obs 268 anchor, paper implications, files manifest
- `01db8fe5` docs(evaluation-scopes): level-up — exec summary, paper implications, repro, caveats, manifest
- `cb940cfb` docs(buffer-band-lift): level-up + harden script against overwrite (Session 75 G6)
- `55ddda00` docs(verifier-calibration): level-up + harden script (Session 75 G6)
- `08d5aef6` docs(corrected-f1-human-reviewed): level-up + harden script (Session 75 G6)
- `92cc9fa5` docs(phase3a-text): secondary_effects level-up + harden script (Session 75 G6)
- `c7bfd579` docs(phase3a-image): secondary_effects level-up + harden script (Session 75 G6)
- `82254d16` docs(phase3a-image): consensus-analysis level-up + model correction for Targets 4/5
- `50e506c0` docs(ds-human-crosstab): level-up — structural inadequacy finding explicit
- `6c3aef23` docs(dawid-skene-v2): level-up — structural rank failure front-loaded
- `e60aadb4` docs(corrected-f1-multi-buffer): level-up + harden script (Session 75 G6)
- `87afb3cc` docs(extended-buffer): level-up — exec summary, caveats, paper implications
- `b0b35ecb` docs(retest-production-summary): level-up — cross-cutting exec + caveats + paper implications
- `6bcbf6e0` docs(55maps-cross-track): new synthesis doc — image x text-HIGH x text-MIN comparison
- `ae460ef1` docs(limitations-consolidation): new paper-citation synthesis of study limitations
- `a3f30552` docs(h12-v2): polish — exec summary, paper implications, caveats
- `b960a3cf` fix(items 12-13): apply verifier-caught corrections

### Session 75 handoff (preserved for reference)

Working tree was clean at commit `8949dc00`, `main` only (no stray
branches), pushed to `origin/main`. Session 75 pushed 15 commits:
`f6d1cdb4` → `8949dc00`. Full log: `git log --oneline ab50b22b..8949dc00`.

Session 75 commit sequence (bottom-up on `git log`):

- `f6d1cdb4` docs(h8-v2): synthesise analysis_summary — library-composition null
- `ce075d5a` docs(obs-238): editorial note — directional-prediction count is 3 of 6
- `52404476` chore(archive): physically move Obs 235 retracted H10/H12 v1 probe data
- `4b20b427` docs(h10): synthesise analysis_summary — pool-size null + retracted-probe scope
- `e8c46809` docs(phase2b): synthesise analysis_summary + retest-era carry-forward
- `bb156aab` docs(h11): synthesise analysis_summary — tile-size inverted-U + UNINTENDED disposition
- `334c6cb4` docs(buffer-100m): render diagnostic report — 50→100m recall gain is TP admission
- `71033ff6` docs(continuity): add Step 6 polish-pass backlog — 50m TP count discrepancy
- `9df2f169` docs(mcc): consolidated report — tile-level MCC analysis family
- `a5c4c325` docs(factor-analysis): level-up — exec summary, methods, caveats, paper implications
- `043fca18` fix(factor-analysis): recover 2 mislabelled Phase 2b N=1 rows + patch aggregator schema
- `6cf99660` fix(cross-ref): correct 3 Agent-B-flagged issues in h8-v2 + h10 summaries
- `9f9f98c3` harden(collect-factor-analysis): 8 audit items + protect hand-authored MD
- `23ddfdf6` harden(evaluate-pv-results): raise on missing consensus.json instead of silent all-zero
- `9f7bfe0f` harden(consolidate-pv-bootstrap-cis): D2b observability + D3a/b provenance
- `f623652d` harden(consolidate-paper-metrics): D2c schema validation + D3a-c provenance
- `783f37c2` docs(hygiene): h11 model-version line + 50m TP reconciliation notes
- `8949dc00` docs(continuity): resolve S6.1 backlog entry + log new metrics_master drift

### Session 74 handoff (preserved for reference)

Working tree clean at commit `c1170229`, `main` only (no stray
branches), amd-tower and zbook in sync. Session 74 pushed 11 commits:
`eb2cf23c` → `c1170229`. Full log: `git log --oneline 4a866d33..c1170229`.

Session 74 commit sequence (bottom-up on `git log`):

- `eb2cf23c` fix(crs): reproject consensus centroids in consensus_to_gdf
- `de5b1214` feat(mcc): compute Phase 2b tile-level MCC for H7 temperature sweep
- `5ae94041` docs(unintended): clarify dual-role disposition for UNINTENDED-T1.0 dirs
- `f0287747` docs(scorecard): Step 2 interim-doc review — 21 rows + known-out-of-scope
- `44990e97` obs(mcc): Obs 274 — Phase 2b tile-level MCC orthogonal to F1 headline
- `b323f045` obs(mcc): tighten Obs 274 cross-references — cite Obs 116 as F1 root
- `16ee3ae5` chore(archive): Option A — archive pre-retest phase2b pilot docs
- `0fccf455` docs(meta-findings): synthesise Obs 262–273 into paper-Discussion spine
- `c1170229` reflect(session-74): end-of-session reflection for 2026-04-23
- `ab50b22b` docs(continuity): Session 74 handoff update + Step 4 reading order

### Session 73 handoff (preserved for reference)

Working tree clean as of commit `c48f639e` (doc-audit replacement).
Eight commits pushed 2026-04-21 (`edfc27f5` through `c48f639e`). Full
log: `git log --oneline e038bfe8..c48f639e`.
