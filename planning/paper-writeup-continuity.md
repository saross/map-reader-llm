# Paper write-up continuity — handoff for a fresh session

**Created**: 2026-04-21 (late, end of Session 73 equivalent)
**Last updated**: 2026-04-25 (end of Session 76 — **Step 4 COMPLETE**; items 8–14 done across a single overnight autonomous session)
**Purpose**: Continuity message for a fresh Claude Code session to
pick up the paper write-up phase without re-reading the entire
project state.

---

## ⚡ Start here (Session 77+ entry point)

**You are on: Step 5 (mark superseded) + Step 6 (paper outline)**.
All 14 Step 4 items are DONE. The per-analysis reports are now at
uniform paper-citation quality; the two new synthesis docs (item 12
cross-track, item 13 limitations) exist as direct paper-section sources;
the Era 1 retest summary (item 11) and the h12-v2 closure (item 14) are
polished. Ready to hand to a paper outline.

**Previous entry point** (Session 76 opened here): Step 4 item 8,
`uncalibrated-vs-calibrated-crosstab/crosstab.md`. Closed Session 76
with items 8–14 complete; see §"Session 76 status" below for the
per-item commit table.

**Tree state at handoff**: 17 Session-76 commits, `f700acd9` → `b960a3cf`,
main-only, working tree clean, **NOT yet pushed to origin** (per user
directive: "I'll review in the morning" — user is to inspect then push).
Use `git log --oneline 8949dc00..HEAD` for the full log.

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

**Session 76 handoff (2026-04-25)**: working tree clean at commit
`b960a3cf`, `main` only (no stray branches), **NOT yet pushed to
`origin/main`** per user directive ("I'll review in the morning").
Session 76 added 17 commits: `f700acd9` → `b960a3cf`. Full log:
`git log --oneline 8949dc00..HEAD`.

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
