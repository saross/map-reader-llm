<!-- GENERATED FILE — do not hand-edit. Projected from the registered manifests by scripts/generate_run_reports.py v1.1.0. Hand edits are destroyed on the next regeneration and fail the --check drift guard. -->
# Post-run report — retest-h11-single-pass-384-t0

> **GENERATED FILE — do not hand-edit.** Projected from the registered manifests by `scripts/generate_run_reports.py` v1.1.0 at source commit `a8c03bb9e`. This file carries provenance instead of a hand changelog, per the PI ruling of 2026-09-11 recorded in `docs/methodology/output-directory-standard.md` § "Documents in Revision Policy Scope": a generated document's history is its inputs' and its generator's git history, so "is this current?" is answered by the `--check` drift guard and its tier-1 test, not by a changelog. Regenerate after any manifest rebuild; put before/after notes in the commit message.

**Directory**: `outputs/retest/h11-single-pass-384-t0` · **Registry status**: active · **Purpose**: H11 single-pass 384px baseline (T=0).

## 1. Identity and registration

| Field | Value |
|---|---|
| Run id | `retest-h11-single-pass-384-t0` |
| Directory | `outputs/retest/h11-single-pass-384-t0` |
| Registry status | active |
| Purpose | H11 single-pass 384px baseline (T=0). |
| Run type (derived) | single-pass |
| Primary hypothesis | H11 |
| Also informs | — |
| Headline condition | not supplied |
| Headline rationale | not supplied |
| Historical aliases | `Era 2` |
| Working-notes Obs | — |
| Registry notes | H11 single-pass baseline. |

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

### 3.1 Proposer passes (10)

| Pool | Pass | Model used | Model requested | Modality | Thinking | Temp | Status | Tiles done | Dispatched | Retries |
|---|---:|---|---|---|---|---:|---|---:|---:|---:|
| `brief-text-t0` | 1 | gemini-3-flash-preview | gemini-3-flash-preview | text | minimal | 0.0 | ok | 487 | not supplied | 0 |
| `brief-text-t0` | 2 | gemini-3-flash-preview | gemini-3-flash-preview | text | minimal | 0.0 | ok | 487 | not supplied | 0 |
| `brief-text-t0` | 3 | gemini-3-flash-preview | gemini-3-flash-preview | text | minimal | 0.0 | ok | 487 | not supplied | 0 |
| `brief-text-t0` | 4 | gemini-3-flash-preview | gemini-3-flash-preview | text | minimal | 0.0 | ok | 487 | not supplied | 0 |
| `brief-text-t0` | 5 | gemini-3-flash-preview | gemini-3-flash-preview | text | minimal | 0.0 | ok | 487 | not supplied | 0 |
| `brief-text-t0` | 6 | gemini-3-flash-preview | gemini-3-flash-preview | text | minimal | 0.0 | ok | 487 | not supplied | 0 |
| `brief-text-t0` | 7 | gemini-3-flash-preview | gemini-3-flash-preview | text | minimal | 0.0 | ok | 487 | not supplied | 0 |
| `brief-text-t0` | 8 | gemini-3-flash-preview | gemini-3-flash-preview | text | minimal | 0.0 | ok | 487 | not supplied | 0 |
| `brief-text-t0` | 9 | gemini-3-flash-preview | gemini-3-flash-preview | text | minimal | 0.0 | ok | 487 | not supplied | 0 |
| `brief-text-t0` | 10 | gemini-3-flash-preview | gemini-3-flash-preview | text | minimal | 0.0 | ok | 487 | not supplied | 0 |

## 4. Token load and recorded cost

| Field | Value |
|---|---|
| Passes on file | 10 |
| Input tokens (billed) | 0 |
| Input tokens (cached) | 0 |
| Output tokens | 0 |
| Thinking tokens | 0 |
| Total tokens | 0 |
| Passes with no token record | 0 |
| Sum of recorded `cost_usd` | US$0.0000 over 10 of 10 pass(es) |
| Passes with no `cost_usd` | 0 |
| Summed wall clock | 0.00 h over 10 pass(es) |

> **The recorded cost is NOT this run's cost.** Each `cost_usd` above is the pass meta's own `cost_estimate.total_cost_usd`, lifted verbatim by `scripts/generate_post_run_report.py`. The token-load audit of 2026-06-12 established that those self-reported estimates price at STANDARD rates although the audited runs executed at `--service-tier flex` (half price) and omit thinking tokens although Gemini bills thinking at the output rate (`reports/token-load-audit-2026-06-12.md` § 1, § 2). The sum is reproduced here as the recorded figure and as an input to a reconciliation, not as a total to cite.

No cost audit on file names this run or its directory: an independently audited cost for this run is **not supplied**. The four audits checked are `reports/token-load-audit-2026-06-12.md`, `reports/r7-gaps-deltas-2026-09-11.md`, `reports/k-ladder-phase2-deltas-2026-09-12.md`, `reports/billing-reconciliation-2026-09-11.md`.

## 5. Registered conditions (11)

F1@20 m is the preregistered localisation buffer; F1@50 m is the deployment working buffer. Confidence intervals are those the evaluation recorded (method, iterations and seed per condition in the manifest). `mcc` is tile-level. A cell reading *not supplied* means the metric is absent from the condition's evaluation, not that it is zero; a tile-MCC reading *withheld* means the tile-join invariant REFUSED that condition's per-tile table on this frame, so the tile metrics and the bootstrap intervals were not computed — the condition's whole-frame F1 is unaffected and is reported in full (PI ruling 2026-09-13; the named reason is in the condition's manifest row).

| Condition | Architecture | Aggregation | Passes | Operating point | Detections | F1@20 m [CI] | F1@50 m [CI] | Tile MCC |
|---|---|---|---:|---|---:|---|---|---:|
| `baseline-flash-text-minimal-t-0-0` | single-pass | none | 1 | — | not supplied | 0.5031 [0.4462, 0.5605] | 0.5205 [0.4626, 0.5783] | 0.0459 |
| `single-pass-run_1` | single-pass | none | 1 | — | 1093 | 0.5065 [0.4489, 0.5639] | 0.5236 [0.4654, 0.5814] | 0.0427 |
| `single-pass-run_10` | single-pass | none | 1 | — | 1090 | 0.4997 [0.4430, 0.5573] | 0.5167 [0.4595, 0.5746] | 0.0427 |
| `single-pass-run_2` | single-pass | none | 1 | — | 1107 | 0.4994 [0.4427, 0.5571] | 0.5162 [0.4588, 0.5741] | 0.0427 |
| `single-pass-run_3` | single-pass | none | 1 | — | 1113 | 0.4961 [0.4386, 0.5534] | 0.5129 [0.4553, 0.5702] | 0.0427 |
| `single-pass-run_4` | single-pass | none | 1 | — | 1090 | 0.5075 [0.4511, 0.5649] | 0.5233 [0.4659, 0.5812] | 0.0427 |
| `single-pass-run_5` | single-pass | none | 1 | — | 1093 | 0.5052 [0.4481, 0.5627] | 0.5236 [0.4647, 0.5820] | 0.0427 |
| `single-pass-run_6` | single-pass | none | 1 | — | 1104 | 0.5003 [0.4440, 0.5566] | 0.5185 [0.4605, 0.5764] | 0.0427 |
| `single-pass-run_7` | single-pass | none | 1 | — | 1098 | 0.5036 [0.4463, 0.5609] | 0.5205 [0.4625, 0.5782] | 0.0427 |
| `single-pass-run_8` | single-pass | none | 1 | — | 1087 | 0.5085 [0.4521, 0.5662] | 0.5256 [0.4683, 0.5833] | 0.0427 |
| `single-pass-run_9` | single-pass | none | 1 | — | 1089 | 0.5039 [0.4469, 0.5622] | 0.5236 [0.4654, 0.5814] | 0.0742 |

Buffers on file (metres), by how many conditions carry that set:

- 11 condition(s): 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 75, 100, 125, 150

Tile-level MCC is on file for 11 of 11 condition(s).

### 5.4 Waived evaluations (13, 1 distinct reason(s))

Scored evaluations under this run that no condition claims, each waived in `results/run-conditions.json` rather than left silent. Grouped by identical reason; where a reason covers more than 12 paths the first 12 are named and the decomposition carries the rest.

- **13 evaluation(s)** — not supplied — a bare-string entry, written before the waiver register carried reasons
  - `results/paper-eval/mcc/384px/flash-text-minimal-t-0-0/evaluation.json`
  - `results/paper-eval/n1/384px-all-buffers/flash-text-minimal-t-0-0/evaluation.json`
  - `results/paper-eval/single-pass-n1/evaluation.json`
  - `results/rescore-2026-05-31/retest-h11-single-pass-384-t0/brief-text-t0/consensus/consensus_t1/evaluation.json`
  - `results/rescore-2026-05-31/retest-h11-single-pass-384-t0/brief-text-t0/consensus/consensus_t10/evaluation.json`
  - `results/rescore-2026-05-31/retest-h11-single-pass-384-t0/brief-text-t0/consensus/consensus_t2/evaluation.json`
  - `results/rescore-2026-05-31/retest-h11-single-pass-384-t0/brief-text-t0/consensus/consensus_t3/evaluation.json`
  - `results/rescore-2026-05-31/retest-h11-single-pass-384-t0/brief-text-t0/consensus/consensus_t4/evaluation.json`
  - `results/rescore-2026-05-31/retest-h11-single-pass-384-t0/brief-text-t0/consensus/consensus_t5/evaluation.json`
  - `results/rescore-2026-05-31/retest-h11-single-pass-384-t0/brief-text-t0/consensus/consensus_t6/evaluation.json`
  - `results/rescore-2026-05-31/retest-h11-single-pass-384-t0/brief-text-t0/consensus/consensus_t7/evaluation.json`
  - `results/rescore-2026-05-31/retest-h11-single-pass-384-t0/brief-text-t0/consensus/consensus_t8/evaluation.json`
  - … and 1 more under the same waiver (full list in `results/run-conditions.json`, this run's `_ignored_evals`)

## 6. Analyses that read this run (3)

A run is linked to an analysis when the analysis's `conditions_compared` names one of this run's conditions. *Cells* is how many of the analysis's compared conditions come from this run, out of its total. *Signed* is the register's `manually_verified_at` stamp.

| Analysis | Cells | Type | Hypotheses | Registration | Paper section | Deviations | Signed | Output |
|---|---|---|---|---|---|---|---|---|
| `diversity-dividend-384` | 1 of 22 | leaderboard | `H3` | confirmatory-with-deviation | Results | `None for the operating-point selection: the registered H3 analysis plan (osf/preregistration.md:519-521) specifies 'Generate threshold sweep curves', 'Identify optimal (N, threshold)', and 'Compare single-pass mean F1 vs voted F1' against the test tiles, so the best-operating- point characterisation is the preregistered method (not in-sample/E56 -- that rule governs the verifier prob_t diagnostics, a distinct case; see E56 Update 2026-06-06).`, `E49/E51 (T=0.7 production carry-forward temperature; HIGH thinking) -- the characterised configurations, carried forward from Phase 2b.`, `Production operating point reported alongside best: text 4-of-5, image 3-of-5 (the 55maps deployment thresholds); the best-minus-N5 delta is the within-test operating-point sensitivity.` | 2026-06-06T00:07:40Z | `results/diversity-dividend-384` |
| `n1-baseline-matrix-384` | 1 of 18 | leaderboard | `H1`, `H7` | post-hoc | Results | `E57` | 2026-06-04T02:05:31Z | `results/paper-eval/n1/384px-14buf-mcc` |
| `uplift-supplement-flatten` | 11 of 441 | diagnostic | — | post-hoc | Appendix | — | 2026-09-10T22:55:40Z | `results/uplift-supplement/conditions.csv` |

## 7. Findings documents (0)

No findings document on disk is named by an analysis that reads this run: a findings write-up for this run is **not supplied** from the register. § 6's `output_path` column gives each analysis's artefact directory.

## 8. Protocol errata

### 8.1 Registered as deviations (4)

Listed in the `deviations` field of an analysis that reads this run:

- **E57** — H11 384px Pro/baseline detection metadata — model template default and output\_dir overrides
- **E49/E51 (T=0.7 production carry-forward temperature; HIGH thinking) -- the characterised configurations, carried forward from Phase 2b.** — not supplied
- **None for the operating-point selection: the registered H3 analysis plan (osf/preregistration.md:519-521) specifies 'Generate threshold sweep curves', 'Identify optimal (N, threshold)', and 'Compare single-pass mean F1 vs voted F1' against the test tiles, so the best-operating- point characterisation is the preregistered method (not in-sample/E56 -- that rule governs the verifier prob_t diagnostics, a distinct case; see E56 Update 2026-06-06).** — not supplied
- **Production operating point reported alongside best: text 4-of-5, image 3-of-5 (the 55maps deployment thresholds); the best-minus-N5 delta is the within-test operating-point sensitivity.** — not supplied

### 8.2 Mentioning this run (1)

The entry's text names this run id or its directory path. A mention is a pointer to read the entry, not a claim that the erratum is about this run:

- **E44** — single-pass-384 executed at T=1.0 instead of T=0.0

## 9. Documents and structure in the run directory

No `experiment_intent.md`, `evaluation.md`, `pre_launch_audit.md` or retrospective report under this directory.

### 9.1 Registered pools

| Proposer pool | Modality | Path within the run directory |
|---|---|---|
| `brief-text-t0` | text | `brief-text-t0` |

## 10. Provenance of this report

This report is a projection. Every figure above is read from one of the committed inputs below; nothing is estimated, and a figure that is not on file is written **not supplied** with its reason.

| Field | Value |
|---|---|
| Generator | `scripts/generate_run_reports.py` v1.1.0 |
| Source commit | `a8c03bb9e` |
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
