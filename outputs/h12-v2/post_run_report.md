<!-- GENERATED FILE — do not hand-edit. Projected from the registered manifests by scripts/generate_run_reports.py v1.1.0. Hand edits are destroyed on the next regeneration and fail the --check drift guard. -->
# Post-run report — h12-v2

> **GENERATED FILE — do not hand-edit.** Projected from the registered manifests by `scripts/generate_run_reports.py` v1.1.0 at source commit `47e73b214`. This file carries provenance instead of a hand changelog, per the PI ruling of 2026-09-11 recorded in `docs/methodology/output-directory-standard.md` § "Documents in Revision Policy Scope": a generated document's history is its inputs' and its generator's git history, so "is this current?" is answered by the `--check` drift guard and its tier-1 test, not by a changelog. Regenerate after any manifest rebuild; put before/after notes in the commit message.

**Directory**: `outputs/h12-v2` · **Registry status**: active · **Purpose**: not supplied

## 1. Identity and registration

| Field | Value |
|---|---|
| Run id | `h12-v2` |
| Directory | `outputs/h12-v2` |
| Registry status | active |
| Purpose | not supplied |
| Run type (derived) | consensus |
| Primary hypothesis | H12 |
| Also informs | `library-design` |
| Headline condition | not supplied |
| Headline rationale | not supplied |
| Historical aliases | `Era 3` |
| Working-notes Obs | — |
| Registry notes | one run (H12 HP:HN ratio study). Conditions = {r1-hn-heavy, r2-balanced, r3-hp-heavy} x {greedy, wbf}; r1/r3 own run\_1-5, greedy/ and wbf/ are aggregation collectors. r2-balanced is a CROSS-RUN condition reusing outputs/h10/evaluation-v2/pool\_160\_hp4hn4 (E52, GAP-6). Inventory: H12v2. |

## 2. Scope and evaluation frame

| Field | Value |
|---|---|
| Tile size (px) | 384 |
| Corpus | 4-map-gs |
| Ground-truth reference | curator |
| Test set id | era-3-327 |
| Test tiles | 327 |
| Bounds | `inputs/vectors/bounds/384/h10_test_bounds.geojson` |
| Calibration set id | pool_160 |
| Calibration tiles | 160 |

## 3. Execution — passes on file

### 3.1 Proposer passes (10)

| Pool | Pass | Model used | Model requested | Modality | Thinking | Temp | Status | Tiles done | Dispatched | Retries |
|---|---:|---|---|---|---|---:|---|---:|---:|---:|
| `r1-hn-heavy` | 1 | gemini-3-flash-preview | gemini-3-flash-preview | image | high | 0.7 | ok | 327 | 327 | 10 |
| `r1-hn-heavy` | 2 | gemini-3-flash-preview | gemini-3-flash-preview | image | high | 0.7 | ok | 327 | 327 | 10 |
| `r1-hn-heavy` | 3 | gemini-3-flash-preview | gemini-3-flash-preview | image | high | 0.7 | ok | 327 | 327 | 9 |
| `r1-hn-heavy` | 4 | gemini-3-flash-preview | gemini-3-flash-preview | image | high | 0.7 | ok | 327 | 327 | 3 |
| `r1-hn-heavy` | 5 | gemini-3-flash-preview | gemini-3-flash-preview | image | high | 0.7 | ok | 327 | 327 | 11 |
| `r3-hp-heavy` | 1 | gemini-3-flash-preview | gemini-3-flash-preview | image | high | 0.7 | ok | 327 | 327 | 3 |
| `r3-hp-heavy` | 2 | gemini-3-flash-preview | gemini-3-flash-preview | image | high | 0.7 | ok | 327 | 327 | 7 |
| `r3-hp-heavy` | 3 | gemini-3-flash-preview | gemini-3-flash-preview | image | high | 0.7 | partial | 326 | 327 | 3 |
| `r3-hp-heavy` | 4 | gemini-3-flash-preview | gemini-3-flash-preview | image | high | 0.7 | ok | 327 | 327 | 4 |
| `r3-hp-heavy` | 5 | gemini-3-flash-preview | gemini-3-flash-preview | image | high | 0.7 | ok | 327 | 327 | 10 |

## 4. Token load and recorded cost

| Field | Value |
|---|---|
| Passes on file | 10 |
| Input tokens (billed) | 65,462,130 |
| Input tokens (cached) | 61,832,430 |
| Output tokens | 400,619 |
| Thinking tokens | 6,090,486 |
| Total tokens | 71,953,235 |
| Passes with no token record | 0 |
| Sum of recorded `cost_usd` | US$33.9329 over 10 of 10 pass(es) |
| Passes with no `cost_usd` | 0 |
| Summed wall clock | 0.47 h over 10 pass(es) |

> **The recorded cost is NOT this run's cost.** Each `cost_usd` above is the pass meta's own `cost_estimate.total_cost_usd`, lifted verbatim by `scripts/generate_post_run_report.py`. The token-load audit of 2026-06-12 established that those self-reported estimates price at STANDARD rates although the audited runs executed at `--service-tier flex` (half price) and omit thinking tokens although Gemini bills thinking at the output rate (`reports/token-load-audit-2026-06-12.md` § 1, § 2). The sum is reproduced here as the recorded figure and as an input to a reconciliation, not as a total to cite.

No cost audit on file names this run or its directory: an independently audited cost for this run is **not supplied**. The four audits checked are `reports/token-load-audit-2026-06-12.md`, `reports/r7-gaps-deltas-2026-09-11.md`, `reports/k-ladder-phase2-deltas-2026-09-12.md`, `reports/billing-reconciliation-2026-09-11.md`.

## 5. Registered conditions (6)

F1@20 m is the preregistered localisation buffer; F1@50 m is the deployment working buffer. Confidence intervals are those the evaluation recorded (method, iterations and seed per condition in the manifest). `mcc` is tile-level. A cell reading *not supplied* means the metric is absent from the condition's evaluation, not that it is zero.

| Condition | Architecture | Aggregation | Passes | Operating point | Detections | F1@20 m [CI] | F1@50 m [CI] | Tile MCC |
|---|---|---|---:|---|---:|---|---|---:|
| `greedy-r1-hn-heavy` | consensus | greedy | 5 | k=4 | 240 | 0.7084 [0.6487, 0.7612] | not supplied | 0.6956 |
| `greedy-r2-balanced` | consensus | greedy | 5 | k=4 | 236 | 0.7171 [0.6621, 0.7667] | not supplied | 0.7168 |
| `greedy-r3-hp-heavy` | consensus | greedy | 5 | k=4 | 254 | 0.6876 [0.6335, 0.7390] | not supplied | 0.7169 |
| `wbf-r1-hn-heavy` | consensus | wbf | 5 | k=4 | 330 | 0.6934 [0.6375, 0.7434] | not supplied | 0.7185 |
| `wbf-r2-balanced` | consensus | wbf | 5 | k=4 | 323 | 0.6854 [0.6252, 0.7393] | not supplied | 0.7181 |
| `wbf-r3-hp-heavy` | consensus | wbf | 5 | k=4 | 328 | 0.6832 [0.6226, 0.7368] | not supplied | 0.7122 |

Buffers on file (metres), by how many conditions carry that set:

- 6 condition(s): 20

Tile-level MCC is on file for 6 of 6 condition(s).

### 5.4 Waived evaluations (18, 1 distinct reason(s))

Scored evaluations under this run that no condition claims, each waived in `results/run-conditions.json` rather than left silent. Grouped by identical reason; where a reason covers more than 12 paths the first 12 are named and the decomposition carries the rest.

- **18 evaluation(s)** — not supplied — a bare-string entry, written before the waiver register carried reasons
  - `results/h12-v2/greedy/r1-hn-heavy/t1/evaluation.json`
  - `results/h12-v2/greedy/r1-hn-heavy/t2/evaluation.json`
  - `results/h12-v2/greedy/r1-hn-heavy/t3/evaluation.json`
  - `results/h12-v2/greedy/r1-hn-heavy/t4/evaluation.json`
  - `results/h12-v2/greedy/r1-hn-heavy/t5/evaluation.json`
  - `results/h12-v2/greedy/r2-balanced/t1/evaluation.json`
  - `results/h12-v2/greedy/r2-balanced/t2/evaluation.json`
  - `results/h12-v2/greedy/r2-balanced/t3/evaluation.json`
  - `results/h12-v2/greedy/r2-balanced/t4/evaluation.json`
  - `results/h12-v2/greedy/r2-balanced/t5/evaluation.json`
  - `results/h12-v2/greedy/r3-hp-heavy/t1/evaluation.json`
  - `results/h12-v2/greedy/r3-hp-heavy/t2/evaluation.json`
  - … and 6 more under the same waiver (full list in `results/run-conditions.json`, this run's `_ignored_evals`)

## 6. Analyses that read this run (2)

A run is linked to an analysis when the analysis's `conditions_compared` names one of this run's conditions. *Cells* is how many of the analysis's compared conditions come from this run, out of its total. *Signed* is the register's `manually_verified_at` stamp.

| Analysis | Cells | Type | Hypotheses | Registration | Paper section | Deviations | Signed | Output |
|---|---|---|---|---|---|---|---|---|
| `h12-v2-hp-hn-ratio` | 6 of 6 | comparison | `H12` | registered-exploratory | Results | `E13`, `E52`, `E49`, `E50`, `E51`, `E45` | 2026-08-17T03:50:21Z | `results/h12-v2/analysis_summary.md` |
| `uplift-supplement-flatten` | 6 of 441 | diagnostic | — | post-hoc | Appendix | — | 2026-09-10T22:55:40Z | `results/uplift-supplement/conditions.csv` |

## 7. Findings documents (1)

| Document | Named by |
|---|---|
| `results/h12-v2/analysis_summary.md` | `h12-v2-hp-hn-ratio` |

## 8. Protocol errata

### 8.1 Registered as deviations (6)

Listed in the `deviations` field of an analysis that reads this run:

- **E13** — H12 (HP:HN ratio) deferred to post-H10
- **E45** — Unregistered inference method — tile-swap permutation testing (corrected 2026-07-28; originally "test statistic changed from macro-average to micro-average")
- **E49** — H10 calibration uses cold-start production config instead of preregistered image-only baseline
- **E50** — H10 holdout expanded from 60 to 327 tiles
- **E51** — H8 library composition re-run under production carry-forward (384 px / v2 pipeline)
- **E52** — H12 HP:HN ratio re-run under production carry-forward (384 px / v2 pipeline)

### 8.2 Mentioning this run (2)

The entry's text names this run id or its directory path. A mention is a pointer to read the entry, not a claim that the erratum is about this run:

- **E71** — `n\_tiles\_processed` manifest column carries two semantics (dispatched vs completed) plus a verifier-row placeholder (GAP-8) — 15 passes with genuine coverage shortfalls, two live conditions carrying dead tiles as artificial false negatives
- **E83** — Tier-1 membership was decided by an order-dependent sequential rule, not by the clique its docstring promised — eight boards' tie sets revised to Hsu MCB, including one that published a sole leader it does not have

## 9. Documents and structure in the run directory

| Document class | Filename | Count |
|---|---|---:|
| per-pass/per-run intent | `experiment_intent.md` | 10 |

These classes are in Revision-Policy scope going forward (`docs/methodology/output-directory-standard.md` § "Documents in Revision Policy Scope").

### 9.1 Registered pools

| Proposer pool | Modality | Path within the run directory |
|---|---|---|
| `r1-hn-heavy` | image | `r1-hn-heavy` |
| `r3-hp-heavy` | image | `r3-hp-heavy` |

## 10. Provenance of this report

This report is a projection. Every figure above is read from one of the committed inputs below; nothing is estimated, and a figure that is not on file is written **not supplied** with its reason.

| Field | Value |
|---|---|
| Generator | `scripts/generate_run_reports.py` v1.1.0 |
| Source commit | `47e73b214` |
| Manifest extractor | `0.7.1` |
| Run row last extracted | `2026-08-03T02:32:37Z` |

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
- `inputs/vectors/bounds/384/h10_test_bounds.geojson`

Regenerate and drift-check with:

```bash
python3 scripts/generate_run_reports.py --all --write
python3 scripts/generate_run_reports.py --check
```
