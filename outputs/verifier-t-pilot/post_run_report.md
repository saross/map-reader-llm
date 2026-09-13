<!-- GENERATED FILE — do not hand-edit. Projected from the registered manifests by scripts/generate_run_reports.py v1.1.0. Hand edits are destroyed on the next regeneration and fail the --check drift guard. -->
# Post-run report — verifier-t-pilot

> **GENERATED FILE — do not hand-edit.** Projected from the registered manifests by `scripts/generate_run_reports.py` v1.1.0 at source commit `2fa91cdb1`. This file carries provenance instead of a hand changelog, per the PI ruling of 2026-09-11 recorded in `docs/methodology/output-directory-standard.md` § "Documents in Revision Policy Scope": a generated document's history is its inputs' and its generator's git history, so "is this current?" is answered by the `--check` drift guard and its tier-1 test, not by a changelog. Regenerate after any manifest rebuild; put before/after notes in the commit message.

**Directory**: `outputs/verifier-t-pilot` · **Registry status**: active · **Purpose**: Verifier sampling-temperature pilot (T0.0/0.5/1.0); recommended T=0.5 as production verifier default.

## 1. Identity and registration

| Field | Value |
|---|---|
| Run id | `verifier-t-pilot` |
| Directory | `outputs/verifier-t-pilot` |
| Registry status | active |
| Purpose | Verifier sampling-temperature pilot (T0.0/0.5/1.0); recommended T=0.5 as production verifier default. |
| Run type (derived) | proposer-verifier |
| Primary hypothesis | H2 |
| Also informs | — |
| Headline condition | not supplied |
| Headline rationale | not supplied |
| Historical aliases | `Era 2` |
| Working-notes Obs | — |
| Registry notes | one run (verifier-temperature pilot, H2-exploratory; T0.0 baseline + T0.5/T1.0 = new verifier passes -&gt; conditions). Owns new API work, unlike wbf. GAP-10/E55: true verifier temp is in run.log ('Temperature override:'), not configuration.temperature (which reads 0.0); metas corrected non-destructively (temperature\_effective). Eval bounds=None -&gt; scope from another source. |

## 2. Scope and evaluation frame

| Field | Value |
|---|---|
| Tile size (px) | 384 |
| Corpus | 4-map-gs |
| Ground-truth reference | curator |
| Test set id | era-2-487 |
| Test tiles | 487 |
| Bounds | `inputs/vectors/bounds/384/full_evaluation_bounds.geojson` |
| Calibration set id | cal-20-384 |
| Calibration tiles | 20 |

## 3. Execution — passes on file

### 3.2 Verifier passes (2)

| Pool | Pass | Model used | Modality | Thinking | Temp | Status | Candidates verified | Retries |
|---|---:|---|---|---|---:|---|---:|---:|
| `t0-5` | 1 | gemini-3-flash-preview | text | minimal | 0.5 | ok | 627 | 0 |
| `t1-0` | 1 | gemini-3-flash-preview | text | minimal | 1.0 | ok | 614 | 0 |

Verifier rows report no tile count by design: verifier pass: operates on candidate crops, not tiles. The verifier meta records candidate ids (cand\_NNNN) in execution\_stats.completed\_items and candidate API items in per\_item\_metadata, so no tile-scale record exists to report. Completed crop count is in n\_candidates\_verified. (E71 Defect 2 / GAP-8, resolved E72 2026-08-02.)

## 4. Token load and recorded cost

| Field | Value |
|---|---|
| Passes on file | 2 |
| Input tokens (billed) | 2,175,488 |
| Input tokens (cached) | 0 |
| Output tokens | 206,342 |
| Thinking tokens | 0 |
| Total tokens | 2,381,830 |
| Passes with no token record | 0 |
| Sum of recorded `cost_usd` | US$1.7068 over 2 of 2 pass(es) |
| Passes with no `cost_usd` | 0 |
| Summed wall clock | 0.17 h over 2 pass(es) |

> **The recorded cost is NOT this run's cost.** Each `cost_usd` above is the pass meta's own `cost_estimate.total_cost_usd`, lifted verbatim by `scripts/generate_post_run_report.py`. The token-load audit of 2026-06-12 established that those self-reported estimates price at STANDARD rates although the audited runs executed at `--service-tier flex` (half price) and omit thinking tokens although Gemini bills thinking at the output rate (`reports/token-load-audit-2026-06-12.md` § 1, § 2). The sum is reproduced here as the recorded figure and as an input to a reconciliation, not as a total to cite.

Audit and reconciliation reports whose text names this run or its directory — consult these for audited figures; a mention is a pointer, not a claim that the report audits this run in full:

- `reports/k-ladder-phase2-deltas-2026-09-12.md`

## 5. Registered conditions (6)

F1@20 m is the preregistered localisation buffer; F1@50 m is the deployment working buffer. Confidence intervals are those the evaluation recorded (method, iterations and seed per condition in the manifest). `mcc` is tile-level. A cell reading *not supplied* means the metric is absent from the condition's evaluation, not that it is zero; a tile-MCC reading *withheld* means the tile-join invariant REFUSED that condition's per-tile table on this frame, so the tile metrics and the bootstrap intervals were not computed — the condition's whole-frame F1 is unaffected and is reported in full (PI ruling 2026-09-13; the named reason is in the condition's manifest row).

| Condition | Architecture | Aggregation | Passes | Operating point | Detections | F1@20 m [CI] | F1@50 m [CI] | Tile MCC |
|---|---|---|---:|---|---:|---|---|---:|
| `verified-t0-0` | proposer-verifier | verified | 5 | k=4/pt=0.2 | 369 | 0.8507 [0.8163, 0.8799] | 0.8706 [0.8374, 0.8973] | 0.7778 |
| `verified-t0-0-era2b` | proposer-verifier | verified | 5 | k=4/pt=0.2 | 369 | 0.8507 [0.8163, 0.8799] | 0.8706 [0.8374, 0.8973] | 0.7778 |
| `verified-t0-5` | proposer-verifier | verified | 5 | k=4/pt=0.2 | 371 | 0.8561 [0.8206, 0.8849] | 0.8784 [0.8464, 0.9041] | 0.7714 |
| `verified-t0-5-era2b` | proposer-verifier | verified | 5 | k=4/pt=0.2 | 371 | 0.8561 [0.8206, 0.8849] | 0.8784 [0.8464, 0.9041] | 0.7714 |
| `verified-t1-0` | proposer-verifier | verified | 5 | k=4/pt=0.2 | 370 | 0.8422 [0.8056, 0.8737] | 0.8646 [0.8306, 0.8928] | 0.7562 |
| `verified-t1-0-era2b` | proposer-verifier | verified | 5 | k=4/pt=0.2 | 370 | 0.8422 [0.8056, 0.8737] | 0.8646 [0.8306, 0.8928] | 0.7562 |

Buffers on file (metres), by how many conditions carry that set:

- 6 condition(s): 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 75, 100, 125, 150

Tile-level MCC is on file for 6 of 6 condition(s).

### 5.1 Condition caveats (3 condition(s), 3 distinct caveat(s))

Grouped by identical text: a caveat written once for a family of sibling cells is reproduced once, with every cell it applies to named. Nothing is elided.

- `verified-t0-0-era2b`
  GS Era-2 verified board cell (planning/gs-era2-verified-board-2026-09-08.md, PI frame ruling 2026-09-09): the registered cell verified-t0-0 re-scored with its committed recipe on the Era-2 ∩ B-union frame (era2-b-487); the committed evaluation on full\_evaluation\_bounds.geojson stays the row's record.
- `verified-t0-5-era2b`
  GS Era-2 verified board cell (planning/gs-era2-verified-board-2026-09-08.md, PI frame ruling 2026-09-09): the registered cell verified-t0-5 re-scored with its committed recipe on the Era-2 ∩ B-union frame (era2-b-487); the committed evaluation on full\_evaluation\_bounds.geojson stays the row's record.
- `verified-t1-0-era2b`
  GS Era-2 verified board cell (planning/gs-era2-verified-board-2026-09-08.md, PI frame ruling 2026-09-09): the registered cell verified-t1-0 re-scored with its committed recipe on the Era-2 ∩ B-union frame (era2-b-487); the committed evaluation on full\_evaluation\_bounds.geojson stays the row's record.

### 5.2 Scope overrides (3 condition(s), 1 distinct frame(s))

These conditions are scored on a frame other than the run's nominal scope in § 2 — the 327-vs-487 leakage trap the verifier exists to catch, disclosed per condition:

- `verified-t0-0-era2b`, `verified-t0-5-era2b`, `verified-t1-0-era2b`
  bounds\_path = inputs/vectors/bounds/384/era2\_b\_intersection\_bounds.geojson, calibration\_set\_id = None, n\_calibration\_tiles = None, n\_test\_tiles = 487, test\_set\_id = era2-b-487

### 5.3 Decomposition note

Verbatim from `results/run-conditions.json` — the hand-authored record of how this run was decomposed and what was adjudicated:

> Batch E (tractable part). H2 verifier-TEMPERATURE pilot at era-2-487 (exploratory, revisits Phase 3d; Obs 286/287). 3 verified conditions = verifier T=0.0 / 0.5 / 1.0 at the chosen vote4 / prob0.20 operating point, scored 14-buffer+MCC. E55/GAP-10: the swept temperature lives in configuration.temperature\_effective (cfg.temperature reads 0.0); the verifier\_config.temperature here is the EFFECTIVE value. Condition labels are slug-safe (verified-t0-0 etc.); the real cell dirs are T0.0/T0.5/T1.0. T0.5/T1.0 are local dir-form verifier passes (slug keys t0-5/t1-0 -&gt; real paths T0.5/T1.0); the T0.0 verifier baseline has NO local meta and reuses gold-standard-v2's verified-v1. proposer\_pools EMPTY: the proposer is cross-run from gs-v2 (detect\_brief-text, 5-pass consensus 4of5); conditions reference it by string -&gt; benign pool-unresolved WARN. CAVEATS (run-facts flag): self-eval-bias (GT partly built from T=0.0 verified output); the T0.0 baseline is gs-v2's IMAGE verifier whereas T0.5/T1.0 use the text verifier (verify\_adversarial-text) -&gt; temperature/modality partly confounded; interpret per Obs 286/287. The verifier prob sweep (prob0.05..0.50) + other vote points collapse to vote4/prob0.20 per Q2 -&gt; deferred \_ignored\_evals close-out sweep.

### 5.4 Waived evaluations (6, 4 distinct reason(s))

Scored evaluations under this run that no condition claims, each waived in `results/run-conditions.json` rather than left silent. Grouped by identical reason; where a reason covers more than 12 paths the first 12 are named and the decomposition carries the rest.

- **3 evaluation(s)** — uplift-supplement pairing/gap-fill anchor (planning/uplift-supplement-2026-08-28.md): an input to the supplement's pairing tables, scored on the reference, buffer, and frame of the stratum it pairs with; not a registered condition and not cited by the paper. Waived by PI ruling 2026-09-07 (planning/reference-revision-2026-09-06.md, register-verifier debt).
  - `results/uplift-supplement/verifier-pairing/verifier-t-pilot__verified-t0-0/evaluation.json`
  - `results/uplift-supplement/verifier-pairing/verifier-t-pilot__verified-t0-5/evaluation.json`
  - `results/uplift-supplement/verifier-pairing/verifier-t-pilot__verified-t1-0/evaluation.json`
- **1 evaluation(s)** — GS Era-2 board gate G2 (planning/gs-era2-verified-board-2026-09-08.md): verified-t0-0's committed recipe re-run on its committed frame with a 200-draw bootstrap to prove the evaluator reproduces the committed evaluation; a gate artefact, not a condition.
  - `results/leaderboard/era2/gs-era2-verified-board-2026-09-10/g2/verifier-t-pilot__verified-t0-0/evaluation.json`
- **1 evaluation(s)** — GS Era-2 board gate G2 (planning/gs-era2-verified-board-2026-09-08.md): verified-t0-5's committed recipe re-run on its committed frame with a 200-draw bootstrap to prove the evaluator reproduces the committed evaluation; a gate artefact, not a condition.
  - `results/leaderboard/era2/gs-era2-verified-board-2026-09-10/g2/verifier-t-pilot__verified-t0-5/evaluation.json`
- **1 evaluation(s)** — GS Era-2 board gate G2 (planning/gs-era2-verified-board-2026-09-08.md): verified-t1-0's committed recipe re-run on its committed frame with a 200-draw bootstrap to prove the evaluator reproduces the committed evaluation; a gate artefact, not a condition.
  - `results/leaderboard/era2/gs-era2-verified-board-2026-09-10/g2/verifier-t-pilot__verified-t1-0/evaluation.json`

## 6. Analyses that read this run (3)

A run is linked to an analysis when the analysis's `conditions_compared` names one of this run's conditions. *Cells* is how many of the analysis's compared conditions come from this run, out of its total. *Signed* is the register's `manually_verified_at` stamp.

| Analysis | Cells | Type | Hypotheses | Registration | Paper section | Deviations | Signed | Output |
|---|---|---|---|---|---|---|---|---|
| `gs-era2-verified-board-2026-09-10` | 3 of 103 | leaderboard | `H2`, `H1` | post-hoc | Results | — | 2026-09-12T06:04:30Z | `results/leaderboard/era2/gs-era2-verified-board-2026-09-10/tiering_20m.json` |
| `uplift-supplement-flatten` | 3 of 441 | diagnostic | — | post-hoc | Appendix | — | 2026-09-10T22:55:40Z | `results/uplift-supplement/conditions.csv` |
| `verifier-uplift-pairing` | 3 of 170 | comparison | `H2` | post-hoc | Appendix | — | 2026-09-12T06:04:30Z | `results/uplift-supplement/verifier-uplift.csv` |

## 7. Findings documents (0)

No findings document on disk is named by an analysis that reads this run: a findings write-up for this run is **not supplied** from the register. § 6's `output_path` column gives each analysis's artefact directory.

## 8. Protocol errata

### 8.2 Mentioning this run (3)

The entry's text names this run id or its directory path. A mention is a pointer to read the entry, not a claim that the erratum is about this run:

- **E55** — Verifier-t-pilot T0.5/T1.0 metadata under-recorded the swept temperature (corrected 2026-07-30)
- **E56** — Verifier probability-threshold operating points are in-sample (test-set-selected), not calibrated
- **E62** — Three unregistered proposer-verifier extension studies (`flash35-pv-2x2`, `pv-diag-256`, `verifier-robustness`) and four unregistered verifier-parameter levels — additional exploratory extensions of the registered PV contingency

## 9. Documents and structure in the run directory

No `experiment_intent.md`, `evaluation.md`, `pre_launch_audit.md` or retrospective report under this directory.

### 9.1 Registered pools

2 registered verifier-pass directory/directories; see `results/run-conditions.json` for the full list.

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
- `inputs/vectors/bounds/384/full_evaluation_bounds.geojson`

Regenerate and drift-check with:

```bash
python3 scripts/generate_run_reports.py --all --write
python3 scripts/generate_run_reports.py --check
```
