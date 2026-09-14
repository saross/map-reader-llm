<!-- GENERATED FILE — do not hand-edit. Projected from the registered manifests by scripts/generate_run_reports.py v1.1.0. Hand edits are destroyed on the next regeneration and fail the --check drift guard. -->
# Post-run report — h10

> **GENERATED FILE — do not hand-edit.** Projected from the registered manifests by `scripts/generate_run_reports.py` v1.1.0 at source commit `b64ceae00`. This file carries provenance instead of a hand changelog, per the PI ruling of 2026-09-11 recorded in `docs/methodology/output-directory-standard.md` § "Documents in Revision Policy Scope": a generated document's history is its inputs' and its generator's git history, so "is this current?" is answered by the `--check` drift guard and its tier-1 test, not by a changelog. Regenerate after any manifest rebuild; put before/after notes in the commit message.

**Directory**: `outputs/h10` · **Registry status**: active · **Purpose**: not supplied

## 1. Identity and registration

| Field | Value |
|---|---|
| Run id | `h10` |
| Directory | `outputs/h10` |
| Registry status | active |
| Purpose | not supplied |
| Run type (derived) | mixed |
| Primary hypothesis | H10 |
| Also informs | `library-design` |
| Headline condition | not supplied |
| Headline rationale | not supplied |
| Historical aliases | `Era 3` |
| Working-notes Obs | — |
| Registry notes | one run (H10 library-pool-size study). Conditions = 4 evaluation-v2 pools (pool\_020/040/080/160\_hp4hn4, each run\_1-5, consensus\_t4). example-pools-v2 (few-shot library sets, incl. unscored hp8hn8/hp16hn16) and hard-cases-v2 (galleries) are diagnostics, not conditions. pool\_160\_hp4hn4 shared with h12-v2 r2 (E52). Inventory: H10v2. |

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

### 3.1 Proposer passes (20)

| Pool | Pass | Model used | Model requested | Modality | Thinking | Temp | Status | Tiles done | Dispatched | Retries |
|---|---:|---|---|---|---|---:|---|---:|---:|---:|
| `pool_020_hp4hn4` | 1 | gemini-3-flash-preview | gemini-3-flash-preview | image | high | 0.7 | ok | 327 | 327 | 4 |
| `pool_020_hp4hn4` | 2 | gemini-3-flash-preview | gemini-3-flash-preview | image | high | 0.7 | ok | 327 | 327 | 10 |
| `pool_020_hp4hn4` | 3 | gemini-3-flash-preview | gemini-3-flash-preview | image | high | 0.7 | ok | 327 | 327 | 4 |
| `pool_020_hp4hn4` | 4 | gemini-3-flash-preview | gemini-3-flash-preview | image | high | 0.7 | ok | 327 | 327 | 5 |
| `pool_020_hp4hn4` | 5 | gemini-3-flash-preview | gemini-3-flash-preview | image | high | 0.7 | ok | 327 | 327 | 11 |
| `pool_040_hp4hn4` | 1 | gemini-3-flash-preview | gemini-3-flash-preview | image | high | 0.7 | ok | 327 | 327 | 8 |
| `pool_040_hp4hn4` | 2 | gemini-3-flash-preview | gemini-3-flash-preview | image | high | 0.7 | ok | 327 | 327 | 9 |
| `pool_040_hp4hn4` | 3 | gemini-3-flash-preview | gemini-3-flash-preview | image | high | 0.7 | ok | 327 | 327 | 6 |
| `pool_040_hp4hn4` | 4 | gemini-3-flash-preview | gemini-3-flash-preview | image | high | 0.7 | ok | 327 | 327 | 4 |
| `pool_040_hp4hn4` | 5 | gemini-3-flash-preview | gemini-3-flash-preview | image | high | 0.7 | ok | 327 | 327 | 4 |
| `pool_080_hp4hn4` | 1 | gemini-3-flash-preview | gemini-3-flash-preview | image | high | 0.7 | ok | 327 | 327 | 6 |
| `pool_080_hp4hn4` | 2 | gemini-3-flash-preview | gemini-3-flash-preview | image | high | 0.7 | ok | 327 | 327 | 7 |
| `pool_080_hp4hn4` | 3 | gemini-3-flash-preview | gemini-3-flash-preview | image | high | 0.7 | ok | 327 | 327 | 6 |
| `pool_080_hp4hn4` | 4 | gemini-3-flash-preview | gemini-3-flash-preview | image | high | 0.7 | ok | 327 | 327 | 8 |
| `pool_080_hp4hn4` | 5 | gemini-3-flash-preview | gemini-3-flash-preview | image | high | 0.7 | ok | 327 | 327 | 14 |
| `pool_160_hp4hn4` | 1 | gemini-3-flash-preview | gemini-3-flash-preview | image | high | 0.7 | ok | 327 | 327 | 4 |
| `pool_160_hp4hn4` | 2 | gemini-3-flash-preview | gemini-3-flash-preview | image | high | 0.7 | ok | 327 | 327 | 6 |
| `pool_160_hp4hn4` | 3 | gemini-3-flash-preview | gemini-3-flash-preview | image | high | 0.7 | ok | 327 | 327 | 7 |
| `pool_160_hp4hn4` | 4 | gemini-3-flash-preview | gemini-3-flash-preview | image | high | 0.7 | ok | 327 | 327 | 7 |
| `pool_160_hp4hn4` | 5 | gemini-3-flash-preview | gemini-3-flash-preview | image | high | 0.7 | ok | 327 | 327 | 7 |

### 3.2 Verifier passes (2)

| Pool | Pass | Model used | Modality | Thinking | Temp | Status | Candidates verified | Retries |
|---|---:|---|---|---|---:|---|---:|---:|
| `pool_020-verified` | 1 | gemini-3-flash-preview | text | minimal | 0.0 | ok | 1763 | 0 |
| `pool_160-verified` | 1 | gemini-3-flash-preview | text | minimal | 0.0 | ok | 1454 | 0 |

Verifier rows report no tile count by design: verifier pass: operates on candidate crops, not tiles. The verifier meta records candidate ids (cand\_NNNN) in execution\_stats.completed\_items and candidate API items in per\_item\_metadata, so no tile-scale record exists to report. Completed crop count is in n\_candidates\_verified. (E71 Defect 2 / GAP-8, resolved E72 2026-08-02.)

## 4. Token load and recorded cost

| Field | Value |
|---|---|
| Passes on file | 22 |
| Input tokens (billed) | 136,674,409 |
| Input tokens (cached) | 123,650,145 |
| Output tokens | 1,381,981 |
| Thinking tokens | 12,931,282 |
| Total tokens | 150,987,672 |
| Passes with no token record | 0 |
| Sum of recorded `cost_usd` | US$72.4831 over 22 of 22 pass(es) |
| Passes with no `cost_usd` | 0 |
| Summed wall clock | 1.64 h over 22 pass(es) |

> **The recorded cost is NOT this run's cost.** Each `cost_usd` above is the pass meta's own `cost_estimate.total_cost_usd`, lifted verbatim by `scripts/generate_post_run_report.py`. The token-load audit of 2026-06-12 established that those self-reported estimates price at STANDARD rates although the audited runs executed at `--service-tier flex` (half price) and omit thinking tokens although Gemini bills thinking at the output rate (`reports/token-load-audit-2026-06-12.md` § 1, § 2). The sum is reproduced here as the recorded figure and as an input to a reconciliation, not as a total to cite.

No cost audit on file names this run or its directory: an independently audited cost for this run is **not supplied**. The four audits checked are `reports/token-load-audit-2026-06-12.md`, `reports/r7-gaps-deltas-2026-09-11.md`, `reports/k-ladder-phase2-deltas-2026-09-12.md`, `reports/billing-reconciliation-2026-09-11.md`.

## 5. Registered conditions (5)

F1@20 m is the preregistered localisation buffer; F1@50 m is the deployment working buffer. Confidence intervals are those the evaluation recorded (method, iterations and seed per condition in the manifest). `mcc` is tile-level. A cell reading *not supplied* means the metric is absent from the condition's evaluation, not that it is zero; a tile-MCC reading *withheld* means the tile-join invariant REFUSED that condition's per-tile table on this frame, so the tile metrics and the bootstrap intervals were not computed — the condition's whole-frame F1 is unaffected and is reported in full (PI ruling 2026-09-13; the named reason is in the condition's manifest row).

| Condition | Architecture | Aggregation | Passes | Operating point | Detections | F1@20 m [CI] | F1@50 m [CI] | Tile MCC |
|---|---|---|---:|---|---:|---|---|---:|
| `greedy-pool-020` | consensus | greedy | 5 | k=4 | 255 | 0.6934 [0.6367, 0.7475] | not supplied | 0.7092 |
| `greedy-pool-040` | consensus | greedy | 5 | k=4 | 242 | 0.6809 [0.6223, 0.7346] | not supplied | 0.6999 |
| `greedy-pool-080` | consensus | greedy | 5 | k=4 | 234 | 0.6618 [0.6067, 0.7176] | not supplied | 0.6919 |
| `greedy-pool-160` | consensus | greedy | 5 | k=4 | 236 | 0.7171 [0.6621, 0.7667] | not supplied | 0.7168 |
| `verified-pool-160` | proposer-verifier | verified | 5 | k=4/pt=0.05 | 232 | 0.7223 [0.6667, 0.7715] | 0.7913 [0.7410, 0.8347] | 0.7602 |

Buffers on file (metres), by how many conditions carry that set:

- 4 condition(s): 20
- 1 condition(s): 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 75, 100, 125, 150

Tile-level MCC is on file for 5 of 5 condition(s).

### 5.4 Waived evaluations (3, 2 distinct reason(s))

Scored evaluations under this run that no condition claims, each waived in `results/run-conditions.json` rather than left silent. Grouped by identical reason; where a reason covers more than 12 paths the first 12 are named and the decomposition carries the rest.

- **2 evaluation(s)** — not supplied — a bare-string entry, written before the waiver register carried reasons
  - `results/condition-scoring-backfill-2026-05-30/h10-evaluation-v2-t0.70/evaluation.json`
  - `results/condition-scoring-backfill-2026-05-30/h10-evaluation-v2-vt4-pt0.05/evaluation.json`
- **1 evaluation(s)** — uplift-supplement K=1 anchor (planning/uplift-supplement-2026-08-28.md; scored 5bd514542): an input to the supplement's pairing tables, on the reference of the stratum it pairs with; not a registered condition and not cited by the paper. Waived by PI ruling 2026-09-07 (planning/reference-revision-2026-09-06.md, register-verifier debt).
  - `results/uplift-supplement/k1-gapfill/h10__verified-pool-160/evaluation.json`

## 6. Analyses that read this run (3)

A run is linked to an analysis when the analysis's `conditions_compared` names one of this run's conditions. *Cells* is how many of the analysis's compared conditions come from this run, out of its total. *Signed* is the register's `manually_verified_at` stamp.

| Analysis | Cells | Type | Hypotheses | Registration | Paper section | Deviations | Signed | Output |
|---|---|---|---|---|---|---|---|---|
| `h10-pool-size` | 5 of 5 | comparison | `H10` | registered-exploratory | Results | `E49`, `E50`, `E13`, `E37`, `E45` | 2026-08-17T03:50:21Z | `results/h10/analysis_summary.md` |
| `uplift-supplement-flatten` | 5 of 441 | diagnostic | — | post-hoc | Appendix | — | 2026-09-10T22:55:40Z | `results/uplift-supplement/conditions.csv` |
| `verifier-uplift-pairing` | 1 of 170 | comparison | `H2` | post-hoc | Appendix | — | 2026-09-12T06:04:30Z | `results/uplift-supplement/verifier-uplift.csv` |

## 7. Findings documents (1)

| Document | Named by |
|---|---|
| `results/h10/analysis_summary.md` | `h10-pool-size` |

## 8. Protocol errata

### 8.1 Registered as deviations (5)

Listed in the `deviations` field of an analysis that reads this run:

- **E13** — H12 (HP:HN ratio) deferred to post-H10
- **E37** — Proposer-Verifier (PV) pipeline — production implementation of registered H2 Condition B (corrected 2026-07-28)
- **E45** — Unregistered inference method — tile-swap permutation testing (corrected 2026-07-28; originally "test statistic changed from macro-average to micro-average")
- **E49** — H10 calibration uses cold-start production config instead of preregistered image-only baseline
- **E50** — H10 holdout expanded from 60 to 327 tiles

### 8.2 Mentioning this run (5)

The entry's text names this run id or its directory path. A mention is a pointer to read the entry, not a claim that the erratum is about this run:

- **E51** — H8 library composition re-run under production carry-forward (384 px / v2 pipeline)
- **E52** — H12 HP:HN ratio re-run under production carry-forward (384 px / v2 pipeline)
- **E56** — Verifier probability-threshold operating points are in-sample (test-set-selected), not calibrated
- **E64** — Five internal contradictions in the lodged registration — operative readings adopted, reasoning stated, post-facto status acknowledged
- **E86** — The three null exemplars were selected from a superseded training set and never rebuilt when the calibration tiles were re-selected — the exemplars are themselves evaluation tiles, and 25 of the 340 Era-1 tiles overlap null-exemplar pixels

## 9. Documents and structure in the run directory

| Document class | Filename | Count |
|---|---|---:|
| per-pass/per-run intent | `experiment_intent.md` | 20 |

These classes are in Revision-Policy scope going forward (`docs/methodology/output-directory-standard.md` § "Documents in Revision Policy Scope").

### 9.1 Registered pools

| Proposer pool | Modality | Path within the run directory |
|---|---|---|
| `pool_020_hp4hn4` | image | `evaluation-v2/pool_020_hp4hn4` |
| `pool_040_hp4hn4` | image | `evaluation-v2/pool_040_hp4hn4` |
| `pool_080_hp4hn4` | image | `evaluation-v2/pool_080_hp4hn4` |
| `pool_160_hp4hn4` | image | `evaluation-v2/pool_160_hp4hn4` |

2 registered verifier-pass directory/directories; see `results/run-conditions.json` for the full list.

## 10. Provenance of this report

This report is a projection. Every figure above is read from one of the committed inputs below; nothing is estimated, and a figure that is not on file is written **not supplied** with its reason.

| Field | Value |
|---|---|
| Generator | `scripts/generate_run_reports.py` v1.1.0 |
| Source commit | `b64ceae00` |
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
- `inputs/vectors/bounds/384/h10_test_bounds.geojson`

Regenerate and drift-check with:

```bash
python3 scripts/generate_run_reports.py --all --write
python3 scripts/generate_run_reports.py --check
```
