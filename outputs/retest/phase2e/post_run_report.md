<!-- GENERATED FILE — do not hand-edit. Projected from the registered manifests by scripts/generate_run_reports.py v1.1.0. Hand edits are destroyed on the next regeneration and fail the --check drift guard. -->
# Post-run report — retest-phase2e

> **GENERATED FILE — do not hand-edit.** Projected from the registered manifests by `scripts/generate_run_reports.py` v1.1.0 at source commit `2fa91cdb1`. This file carries provenance instead of a hand changelog, per the PI ruling of 2026-09-11 recorded in `docs/methodology/output-directory-standard.md` § "Documents in Revision Policy Scope": a generated document's history is its inputs' and its generator's git history, so "is this current?" is answered by the `--check` drift guard and its tier-1 test, not by a changelog. Regenerate after any manifest rebuild; put before/after notes in the commit message.

**Directory**: `outputs/retest/phase2e` · **Registry status**: active · **Purpose**: not supplied

## 1. Identity and registration

| Field | Value |
|---|---|
| Run id | `retest-phase2e` |
| Directory | `outputs/retest/phase2e` |
| Registry status | active |
| Purpose | not supplied |
| Run type (derived) | single-pass |
| Primary hypothesis | H4 |
| Also informs | — |
| Headline condition | not supplied |
| Headline rationale | not supplied |
| Historical aliases | `Era 1` |
| Working-notes Obs | — |
| Registry notes | H4. |

## 2. Scope and evaluation frame

| Field | Value |
|---|---|
| Tile size (px) | 512 |
| Corpus | 4-map-gs |
| Ground-truth reference | curator |
| Test set id | era-1-340 |
| Test tiles | 340 |
| Bounds | `inputs/vectors/bounds/full_evaluation_bounds.geojson` |
| Calibration set id | cal-20-512 |
| Calibration tiles | 20 |

## 3. Execution — passes on file

### 3.1 Proposer passes (4)

| Pool | Pass | Model used | Model requested | Modality | Thinking | Temp | Status | Tiles done | Dispatched | Retries |
|---|---:|---|---|---|---|---:|---|---:|---:|---:|
| `canonical-first` | 1 | gemini-3-flash | gemini-3-flash | image | minimal | 0.0 | ok | 340 | not supplied | 0 |
| `canonical-last` | 1 | gemini-3-flash | gemini-3-flash | image | minimal | 0.0 | ok | 340 | not supplied | 0 |
| `config-default` | 1 | gemini-3-flash | gemini-3-flash | image | minimal | 0.0 | ok | 340 | not supplied | 0 |
| `random` | 1 | gemini-3-flash | gemini-3-flash | image | minimal | 0.0 | ok | 340 | not supplied | 0 |

## 4. Token load and recorded cost

| Field | Value |
|---|---|
| Passes on file | 4 |
| Input tokens (billed) | 0 |
| Input tokens (cached) | 0 |
| Output tokens | 0 |
| Thinking tokens | 0 |
| Total tokens | 0 |
| Passes with no token record | 0 |
| Sum of recorded `cost_usd` | US$0.0000 over 4 of 4 pass(es) |
| Passes with no `cost_usd` | 0 |
| Summed wall clock | 0.00 h over 4 pass(es) |

> **The recorded cost is NOT this run's cost.** Each `cost_usd` above is the pass meta's own `cost_estimate.total_cost_usd`, lifted verbatim by `scripts/generate_post_run_report.py`. The token-load audit of 2026-06-12 established that those self-reported estimates price at STANDARD rates although the audited runs executed at `--service-tier flex` (half price) and omit thinking tokens although Gemini bills thinking at the output rate (`reports/token-load-audit-2026-06-12.md` § 1, § 2). The sum is reproduced here as the recorded figure and as an input to a reconciliation, not as a total to cite.

No cost audit on file names this run or its directory: an independently audited cost for this run is **not supplied**. The four audits checked are `reports/token-load-audit-2026-06-12.md`, `reports/r7-gaps-deltas-2026-09-11.md`, `reports/k-ladder-phase2-deltas-2026-09-12.md`, `reports/billing-reconciliation-2026-09-11.md`.

## 5. Registered conditions (4)

F1@20 m is the preregistered localisation buffer; F1@50 m is the deployment working buffer. Confidence intervals are those the evaluation recorded (method, iterations and seed per condition in the manifest). `mcc` is tile-level. A cell reading *not supplied* means the metric is absent from the condition's evaluation, not that it is zero; a tile-MCC reading *withheld* means the tile-join invariant REFUSED that condition's per-tile table on this frame, so the tile metrics and the bootstrap intervals were not computed — the condition's whole-frame F1 is unaffected and is reported in full (PI ruling 2026-09-13; the named reason is in the condition's manifest row).

| Condition | Architecture | Aggregation | Passes | Operating point | Detections | F1@20 m [CI] | F1@50 m [CI] | Tile MCC |
|---|---|---|---:|---|---:|---|---|---:|
| `canonical-first` | single-pass | none | 1 | — | 771 | 0.5985 [0.5503, 0.6494] | 0.7298 [0.6911, 0.7682] | 0.0942 |
| `canonical-last` | single-pass | none | 1 | — | 785 | 0.6314 [0.5866, 0.6753] | 0.7236 [0.6839, 0.7609] | 0.2132 |
| `config-default` | single-pass | none | 1 | — | 752 | 0.6057 [0.5608, 0.6519] | 0.7343 [0.6977, 0.7702] | 0.2132 |
| `random` | single-pass | none | 1 | — | 821 | 0.5706 [0.5217, 0.6194] | 0.6971 [0.6494, 0.7388] | 0.0665 |

Buffers on file (metres), by how many conditions carry that set:

- 4 condition(s): 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 75, 100, 125, 150

Tile-level MCC is on file for 4 of 4 condition(s).

### 5.3 Decomposition note

Verbatim from `results/run-conditions.json` — the hand-authored record of how this run was decomposed and what was adjudicated:

> Era-1 retest, H4 (phase2e). Single-pass replicate conditions (K passes per condition, metric = replicate-mean over runs), scored at the 14-buffer+MCC standard (Session 102 re-score, results/paper-eval/phase2/512px-14buf-mcc/). Era-1 340-tile, curator GT, 512px. Model of record: gemini-3-flash. detections points at the condition dir (the replicate-mean eval has no single geojson); n\_detections=None is expected. proposer\_pools = the leaf condition dirs (run\_\* = replicates).

### 5.4 Waived evaluations (12, 1 distinct reason(s))

Scored evaluations under this run that no condition claims, each waived in `results/run-conditions.json` rather than left silent. Grouped by identical reason; where a reason covers more than 12 paths the first 12 are named and the decomposition carries the rest.

- **12 evaluation(s)** — not supplied — a bare-string entry, written before the waiver register carried reasons
  - `results/paper-eval/mcc/512px/p2e-canonical-first/evaluation.json`
  - `results/paper-eval/mcc/512px/p2e-canonical-last/evaluation.json`
  - `results/paper-eval/mcc/512px/p2e-config-default/evaluation.json`
  - `results/paper-eval/mcc/512px/p2e-random/evaluation.json`
  - `results/paper-eval/n1/512px-all-buffers/p2e-canonical-first/evaluation.json`
  - `results/paper-eval/n1/512px-all-buffers/p2e-canonical-last/evaluation.json`
  - `results/paper-eval/n1/512px-all-buffers/p2e-config-default/evaluation.json`
  - `results/paper-eval/n1/512px-all-buffers/p2e-random/evaluation.json`
  - `results/paper-eval/n1/512px/p2e-canonical-first/evaluation.json`
  - `results/paper-eval/n1/512px/p2e-canonical-last/evaluation.json`
  - `results/paper-eval/n1/512px/p2e-config-default/evaluation.json`
  - `results/paper-eval/n1/512px/p2e-random/evaluation.json`

## 6. Analyses that read this run (5)

A run is linked to an analysis when the analysis's `conditions_compared` names one of this run's conditions. *Cells* is how many of the analysis's compared conditions come from this run, out of its total. *Signed* is the register's `manually_verified_at` stamp.

| Analysis | Cells | Type | Hypotheses | Registration | Paper section | Deviations | Signed | Output |
|---|---|---|---|---|---|---|---|---|
| `era1-leaderboard` | 4 of 82 | leaderboard | `H2`, `H1`, `H3`, `H4`, `H5`, `H7`, `H8`, `H9` | post-hoc | Results | `E25`, `E27`, `E28`, `E29`, `E30`, `E31`, `E36`, `E37`, `E58` | 2026-06-09T01:22:50Z | `results/era1-leaderboard` |
| `era1-single-pass-baseline-matrix` | 4 of 36 | leaderboard | `H1`, `H4`, `H5`, `H7`, `H8` | post-hoc | Results | `E25`, `E27`, `E28`, `E29`, `E30`, `E31`, `E36` | 2026-06-09T01:22:50Z | `results/paper-eval/n1/512px-14buf-mcc` |
| `family-bh-fdr-confirmatory` | 2 of 12 | comparison | `H1`, `H2`, `H3`, `H4`, `H5`, `H7`, `H8` | confirmatory-with-deviation | Results | `E28`, `E30`, `E36`, `E41`, `E45`, `E51`, `E53`, `E54`, `E58`, `E59`, `E60`, `E64` | 2026-08-14T23:32:30Z | `results/family-fdr/family_fdr.json` |
| `tile-size-sweep` | 1 of 35 | sweep | `H11` | registered-exploratory | Results | `E36`, `E41`, `E43`, `E44`, `E56`, `E57`, `E62` | 2026-06-09T01:52:52Z | `results/tile-size-sweep` |
| `uplift-supplement-flatten` | 4 of 441 | diagnostic | — | post-hoc | Appendix | — | 2026-09-10T22:55:40Z | `results/uplift-supplement/conditions.csv` |

## 7. Findings documents (0)

No findings document on disk is named by an analysis that reads this run: a findings write-up for this run is **not supplied** from the register. § 6's `output_path` column gives each analysis's artefact directory.

## 8. Protocol errata

### 8.1 Registered as deviations (22)

Listed in the `deviations` field of an analysis that reads this run:

- **E25** — Modality manipulation not implemented — text-only conditions received images
- **E27** — Dual-track carry-forward from Phase 2a (OFAT deviation)
- **E28** — H5 instruction text adapted for Phase 2d (HN image references removed, OFAT simplification)
- **E29** — `reorder\_examples()` canonical-first was a no-op
- **E30** — Phase 2e tests 4 ordering conditions instead of preregistered 3
- **E31** — Deterministic runs at T=0.0 copied instead of re-executed
- **E36** — 340-tile production retest replaces 60-tile holdout evaluation (corrected 2026-07-30)
- **E37** — Proposer-Verifier (PV) pipeline — production implementation of registered H2 Condition B (corrected 2026-07-28)
- **E41** — 384px tile size and full evaluation set used for Pro comparison
- **E43** — consensus-384 executed at T=1.0 instead of T=0.7
- **E44** — single-pass-384 executed at T=1.0 instead of T=0.0
- **E45** — Unregistered inference method — tile-swap permutation testing (corrected 2026-07-28; originally "test statistic changed from macro-average to micro-average")
- **E51** — H8 library composition re-run under production carry-forward (384 px / v2 pipeline)
- **E53** — Phase 3a-HIGH image track moved from 512 px (Era 1) to 384 px (Era 2)
- **E54** — Bootstrap iteration count — preregistered 1 000 for primary F1, post-hoc 10 000 for narrow-effect analyses
- **E56** — Verifier probability-threshold operating points are in-sample (test-set-selected), not calibrated
- **E57** — H11 384px Pro/baseline detection metadata — model template default and output\_dir overrides
- **E58** — Registered H2 proposer prompt (`propose\_brief`) never used — `detect\_brief-text` substituted in all PV experiments
- **E59** — H2 Condition C (fine-to-coarse) — registered confirmatory condition never executed, never formally dropped
- **E60** — H7 escalation trigger — fired as written on the expanded corpus; escalation judged uninformative and not run
- **E62** — Three unregistered proposer-verifier extension studies (`flash35-pv-2x2`, `pv-diag-256`, `verifier-robustness`) and four unregistered verifier-parameter levels — additional exploratory extensions of the registered PV contingency
- **E64** — Five internal contradictions in the lodged registration — operative readings adopted, reasoning stated, post-facto status acknowledged

### 8.2 Mentioning this run (1)

The entry's text names this run id or its directory path. A mention is a pointer to read the entry, not a claim that the erratum is about this run:

- **E81** — Undefined tile-level MCC published as `0.0` — nine conditions reported at the value the scale calls "random" where the metric is not computable, four more depressed by averaging an undefined pass into a mean

## 9. Documents and structure in the run directory

No `experiment_intent.md`, `evaluation.md`, `pre_launch_audit.md` or retrospective report under this directory.

### 9.1 Registered pools

| Proposer pool | Modality | Path within the run directory |
|---|---|---|
| `canonical-first` | image | `canonical-first` |
| `canonical-last` | image | `canonical-last` |
| `config-default` | image | `config-default` |
| `random` | image | `random` |

## 10. Provenance of this report

This report is a projection. Every figure above is read from one of the committed inputs below; nothing is estimated, and a figure that is not on file is written **not supplied** with its reason.

| Field | Value |
|---|---|
| Generator | `scripts/generate_run_reports.py` v1.1.0 |
| Source commit | `2fa91cdb1` |
| Manifest extractor | `0.7.1` |
| Run row last extracted | `2026-09-13T09:02:37Z` |

Inputs:

- `results/run-registry.json`
- `results/runs-manifest.json`
- `results/conditions-manifest.json`
- `results/passes-manifest.json`
- `results/analyses-manifest.json`
- `results/run-conditions.json`
- `results/run-analyses.json`
- `docs/methodology/preregistration/protocol-errata.md`

The run row's own upstream sources, as the manifest records them:

- `results/run-facts.json`
- `inputs/vectors/bounds/full_evaluation_bounds.geojson`

Regenerate and drift-check with:

```bash
python3 scripts/generate_run_reports.py --all --write
python3 scripts/generate_run_reports.py --check
```
