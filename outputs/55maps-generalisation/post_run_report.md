<!-- GENERATED FILE — do not hand-edit. Projected from the registered manifests by scripts/generate_run_reports.py v1.1.0. Hand edits are destroyed on the next regeneration and fail the --check drift guard. -->
# Post-run report — 55maps-generalisation

> **GENERATED FILE — do not hand-edit.** Projected from the registered manifests by `scripts/generate_run_reports.py` v1.1.0 at source commit `f307c1932`. This file carries provenance instead of a hand changelog, per the PI ruling of 2026-09-11 recorded in `docs/methodology/output-directory-standard.md` § "Documents in Revision Policy Scope": a generated document's history is its inputs' and its generator's git history, so "is this current?" is answered by the `--check` drift guard and its tier-1 test, not by a changelog. Regenerate after any manifest rebuild; put before/after notes in the commit message.

**Directory**: `outputs/55maps-generalisation` · **Registry status**: active · **Purpose**: 55-map generalisation: text, paired verifier

## 1. Identity and registration

| Field | Value |
|---|---|
| Run id | `55maps-generalisation` |
| Directory | `outputs/55maps-generalisation` |
| Registry status | active |
| Purpose | 55-map generalisation: text, paired verifier |
| Run type (derived) | proposer-verifier |
| Primary hypothesis | not supplied |
| Also informs | — |
| Headline condition | not supplied |
| Headline rationale | not supplied |
| Historical aliases | `55-map generalisation` |
| Working-notes Obs | — |
| Registry notes | Generalisation programme (text, paired verifier). Absent from condition-inventory; facts from configs/report. Carry-forward #10 (verified\_detections\_paired) lives here. |

## 2. Scope and evaluation frame

| Field | Value |
|---|---|
| Tile size (px) | 384 |
| Corpus | 55-map |
| Ground-truth reference | student |
| Test set id | 55maps-8541 |
| Test tiles | 8541 |
| Bounds | `inputs/vectors/bounds/384/55maps_evaluation_bounds.geojson` |
| Calibration set id | not supplied |
| Calibration tiles | not supplied |

## 3. Execution — passes on file

### 3.1 Proposer passes (5)

| Pool | Pass | Model used | Model requested | Modality | Thinking | Temp | Status | Tiles done | Dispatched | Retries |
|---|---:|---|---|---|---|---:|---|---:|---:|---:|
| `detect_brief-text` | 1 | gemini-3-flash-preview | gemini-3-flash-preview | text | high | 0.7 | ok | 1 | 1 | 1 |
| `detect_brief-text` | 2 | gemini-3-flash-preview | gemini-3-flash-preview | text | high | 0.7 | ok | 7 | 7 | 5 |
| `detect_brief-text` | 3 | not supplied | gemini-3-flash-preview | text | high | 0.7 | ok | 1 | 1 | 5 |
| `detect_brief-text` | 4 | gemini-3-flash-preview | gemini-3-flash-preview | text | high | 0.7 | ok | 3 | 3 | 2 |
| `detect_brief-text` | 5 | gemini-3-flash-preview | gemini-3-flash-preview | text | high | 0.7 | ok | 4 | 4 | 3 |

### 3.2 Verifier passes (2)

| Pool | Pass | Model used | Modality | Thinking | Temp | Status | Candidates verified | Retries |
|---|---:|---|---|---|---:|---|---:|---:|
| `verified` | 1 | gemini-3-flash-preview | text | minimal | 0.0 | ok | 10154 | 0 |
| `verified-v2` | 1 | gemini-3-flash-preview | text | minimal | 0.0 | ok | 3 | 0 |

Verifier rows report no tile count by design: verifier pass: operates on candidate crops, not tiles. The verifier meta records candidate ids (cand\_NNNN) in execution\_stats.completed\_items and candidate API items in per\_item\_metadata, so no tile-scale record exists to report. Completed crop count is in n\_candidates\_verified. (E71 Defect 2 / GAP-8, resolved E72 2026-08-02.)

## 4. Token load and recorded cost

| Field | Value |
|---|---|
| Passes on file | 7 |
| Input tokens (billed) | 16,005,669 |
| Input tokens (cached) | 0 |
| Output tokens | 1,487,990 |
| Thinking tokens | 58,724 |
| Total tokens | 17,552,383 |
| Passes with no token record | 0 |
| Sum of recorded `cost_usd` | US$12.4668 over 7 of 7 pass(es) |
| Passes with no `cost_usd` | 0 |
| Summed wall clock | 1.30 h over 7 pass(es) |

> **The recorded cost is NOT this run's cost.** Each `cost_usd` above is the pass meta's own `cost_estimate.total_cost_usd`, lifted verbatim by `scripts/generate_post_run_report.py`. The token-load audit of 2026-06-12 established that those self-reported estimates price at STANDARD rates although the audited runs executed at `--service-tier flex` (half price) and omit thinking tokens although Gemini bills thinking at the output rate (`reports/token-load-audit-2026-06-12.md` § 1, § 2). The sum is reproduced here as the recorded figure and as an input to a reconciliation, not as a total to cite.

No cost audit on file names this run or its directory: an independently audited cost for this run is **not supplied**. The four audits checked are `reports/token-load-audit-2026-06-12.md`, `reports/r7-gaps-deltas-2026-09-11.md`, `reports/k-ladder-phase2-deltas-2026-09-12.md`, `reports/billing-reconciliation-2026-09-11.md`.

## 5. Registered conditions (1)

F1@20 m is the preregistered localisation buffer; F1@50 m is the deployment working buffer. Confidence intervals are those the evaluation recorded (method, iterations and seed per condition in the manifest). `mcc` is tile-level. A cell reading *not supplied* means the metric is absent from the condition's evaluation, not that it is zero; a tile-MCC reading *withheld* means the tile-join invariant REFUSED that condition's per-tile table on this frame, so the tile metrics and the bootstrap intervals were not computed — the condition's whole-frame F1 is unaffected and is reported in full (PI ruling 2026-09-13; the named reason is in the condition's manifest row).

| Condition | Architecture | Aggregation | Passes | Operating point | Detections | F1@20 m [CI] | F1@50 m [CI] | Tile MCC |
|---|---|---|---:|---|---:|---|---|---:|
| `verified-paired` | proposer-verifier | verified | 5 | k=4 | 4068 | 0.6254 [0.6106, 0.6400] | 0.7921 [0.7809, 0.8027] | 0.6509 |

Buffers on file (metres), by how many conditions carry that set:

- 1 condition(s): 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 75, 100, 125, 150

Tile-level MCC is on file for 1 of 1 condition(s).

### 5.3 Decomposition note

Verbatim from `results/run-conditions.json` — the hand-authored record of how this run was decomposed and what was adjudicated:

> Batch B. SUPERSEDED ORIGINAL of 55maps-text-high-generalisation (same experiment: text, HIGH thinking, T=0.7; pre-recovery, executed 2026-04-10 via bash scripts before run\_generalisation.py). Kept as a CITED ORIGINAL (not folded as a historical\_alias, Session 100 decision) because its verified set (verified\_detections\_paired) is referenced by the paired-permutation analyses; archive-don't-delete. 1 verified condition at the standardised 14-buffer+MCC re-score vs the reviewed student GT (student-mounds-55maps-reviewed.geojson), era 55maps-8541. Two verifier\_passes: 'verified' (the paired output) and 'verified-v2' (a verify\_adversarial\_v2.md prompt re-run that produced no scored geojson here). Consensus-4of5 + non-canonical sibling evals -&gt; deferred \_ignored\_evals. See docs/methodology/55maps-generalisation-runs.md.

### 5.4 Waived evaluations (2, 1 distinct reason(s))

Scored evaluations under this run that no condition claims, each waived in `results/run-conditions.json` rather than left silent. Grouped by identical reason; where a reason covers more than 12 paths the first 12 are named and the decomposition carries the rest.

- **2 evaluation(s)** — uplift-supplement K=1 anchor (planning/uplift-supplement-2026-08-28.md; scored 5bd514542): an input to the supplement's pairing tables, on the reference of the stratum it pairs with; not a registered condition and not cited by the paper. Waived by PI ruling 2026-09-07 (planning/reference-revision-2026-09-06.md, register-verifier debt).
  - `results/uplift-supplement/k1-gapfill/55maps-generalisation__verified-paired/evaluation.json`
  - `results/uplift-supplement/verifier-pairing/55maps-generalisation__verified-paired/evaluation.json`

## 6. Analyses that read this run (2)

A run is linked to an analysis when the analysis's `conditions_compared` names one of this run's conditions. *Cells* is how many of the analysis's compared conditions come from this run, out of its total. *Signed* is the register's `manually_verified_at` stamp.

| Analysis | Cells | Type | Hypotheses | Registration | Paper section | Deviations | Signed | Output |
|---|---|---|---|---|---|---|---|---|
| `uplift-supplement-flatten` | 1 of 441 | diagnostic | — | post-hoc | Appendix | — | 2026-09-10T22:55:40Z | `results/uplift-supplement/conditions.csv` |
| `verifier-uplift-pairing` | 1 of 170 | comparison | `H2` | post-hoc | Appendix | — | 2026-09-12T06:04:30Z | `results/uplift-supplement/verifier-uplift.csv` |

## 7. Findings documents (0)

No findings document on disk is named by an analysis that reads this run: a findings write-up for this run is **not supplied** from the register. § 6's `output_path` column gives each analysis's artefact directory.

## 8. Protocol errata

No erratum in `docs/methodology/preregistration/protocol-errata.md` is registered against an analysis of this run, and none mentions the run or its directory.

## 9. Documents and structure in the run directory

| Document class | Filename | Count |
|---|---|---:|
| retrospective post-run report | `post_run_report_retrospective.md` | 1 |

These classes are in Revision-Policy scope going forward (`docs/methodology/output-directory-standard.md` § "Documents in Revision Policy Scope").

### 9.1 Registered pools

| Proposer pool | Modality | Path within the run directory |
|---|---|---|
| `detect_brief-text` | text | `proposer/detect_brief-text` |

2 registered verifier-pass directory/directories; see `results/run-conditions.json` for the full list.

## 10. Provenance of this report

This report is a projection. Every figure above is read from one of the committed inputs below; nothing is estimated, and a figure that is not on file is written **not supplied** with its reason.

| Field | Value |
|---|---|
| Generator | `scripts/generate_run_reports.py` v1.1.0 |
| Source commit | `f307c1932` |
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
- `inputs/vectors/bounds/384/55maps_evaluation_bounds.geojson`
- `outputs/55maps-generalisation/proposer/detect_brief-text/run_1/detections-detect_brief-text-3-flash-2026-04-09.meta.json`

Regenerate and drift-check with:

```bash
python3 scripts/generate_run_reports.py --all --write
python3 scripts/generate_run_reports.py --check
```
