<!-- GENERATED FILE — do not hand-edit. Projected from the registered manifests by scripts/generate_run_reports.py v1.1.0. Hand edits are destroyed on the next regeneration and fail the --check drift guard. -->
# Post-run report — stride-phasec-2026-08-25

> **GENERATED FILE — do not hand-edit.** Projected from the registered manifests by `scripts/generate_run_reports.py` v1.1.0 at source commit `11e576e9c`. This file carries provenance instead of a hand changelog, per the PI ruling of 2026-09-11 recorded in `docs/methodology/output-directory-standard.md` § "Documents in Revision Policy Scope": a generated document's history is its inputs' and its generator's git history, so "is this current?" is answered by the `--check` drift guard and its tier-1 test, not by a changelog. Regenerate after any manifest rebuild; put before/after notes in the commit message.

**Directory**: `outputs/stride-phasec-2026-08-25` · **Registry status**: active · **Purpose**: Stride programme Phase C: the 384/62.5% rung-144 cell at K=10 — the densest-overlap 384 px point, completing the stride ladder.

## 1. Identity and registration

| Field | Value |
|---|---|
| Run id | `stride-phasec-2026-08-25` |
| Directory | `outputs/stride-phasec-2026-08-25` |
| Registry status | active |
| Purpose | Stride programme Phase C: the 384/62.5% rung-144 cell at K=10 — the densest-overlap 384 px point, completing the stride ladder. |
| Run type (derived) | proposer-verifier |
| Primary hypothesis | not supplied |
| Also informs | `H13` |
| Headline condition | stride-phasec-2026-08-25::g384-ov240-k10-verified-p0.15-k10 |
| Headline rationale | The cell's verified best point (F1@20 0.8860). |
| Historical aliases | — |
| Working-notes Obs | — |
| Registry notes | Stride Phase C: g384\_ov240 x10 + verification. Registered S143 (Pass 1). |

## 2. Scope and evaluation frame

| Field | Value |
|---|---|
| Tile size (px) | 384 |
| Corpus | 4-map-gs |
| Ground-truth reference | curator |
| Test set id | grid-common-487 |
| Test tiles | 487 |
| Bounds | `outputs/grid-2026-08-18/scoring/bounds/grid_common_bounds.geojson` |
| Calibration set id | not supplied |
| Calibration tiles | not supplied |

## 3. Execution — passes on file

### 3.1 Proposer passes (10)

| Pool | Pass | Model used | Model requested | Modality | Thinking | Temp | Status | Tiles done | Dispatched | Retries |
|---|---:|---|---|---|---|---:|---|---:|---:|---:|
| `g384_ov240` | 1 | gemini-3-flash-preview | gemini-3-flash-preview | text | minimal | 0.7 | ok | 2483 | 2483 | 37 |
| `g384_ov240` | 2 | gemini-3-flash-preview | gemini-3-flash-preview | text | minimal | 0.7 | ok | 2483 | 2483 | 45 |
| `g384_ov240` | 3 | gemini-3-flash-preview | gemini-3-flash-preview | text | minimal | 0.7 | ok | 2483 | 2483 | 22 |
| `g384_ov240` | 4 | gemini-3-flash-preview | gemini-3-flash-preview | text | minimal | 0.7 | ok | 2483 | 2483 | 41 |
| `g384_ov240` | 5 | gemini-3-flash-preview | gemini-3-flash-preview | text | minimal | 0.7 | ok | 2483 | 2483 | 9 |
| `g384_ov240` | 6 | gemini-3-flash-preview | gemini-3-flash-preview | text | minimal | 0.7 | ok | 2483 | 2483 | 36 |
| `g384_ov240` | 7 | gemini-3-flash-preview | gemini-3-flash-preview | text | minimal | 0.7 | ok | 2483 | 2483 | 29 |
| `g384_ov240` | 8 | gemini-3-flash-preview | gemini-3-flash-preview | text | minimal | 0.7 | ok | 2483 | 2483 | 36 |
| `g384_ov240` | 9 | gemini-3-flash-preview | gemini-3-flash-preview | text | minimal | 0.7 | ok | 2483 | 2483 | 31 |
| `g384_ov240` | 10 | gemini-3-flash-preview | gemini-3-flash-preview | text | minimal | 0.7 | ok | 2483 | 2483 | 22 |

### 3.2 Verifier passes (1)

| Pool | Pass | Model used | Modality | Thinking | Temp | Status | Candidates verified | Retries |
|---|---:|---|---|---|---:|---|---:|---:|
| `g384_ov240-union-k10-verify` | 1 | gemini-3-flash-preview | text | minimal | 0.0 | ok | 5250 | 17 |

Verifier rows report no tile count by design: verifier pass: operates on candidate crops, not tiles. The verifier meta records candidate ids (cand\_NNNN) in execution\_stats.completed\_items and candidate API items in per\_item\_metadata, so no tile-scale record exists to report. Completed crop count is in n\_candidates\_verified. (E71 Defect 2 / GAP-8, resolved E72 2026-08-02.)

## 4. Token load and recorded cost

| Field | Value |
|---|---|
| Passes on file | 11 |
| Input tokens (billed) | 46,702,660 |
| Input tokens (cached) | 0 |
| Output tokens | 4,525,281 |
| Thinking tokens | 0 |
| Total tokens | 51,227,941 |
| Passes with no token record | 0 |
| Sum of recorded `cost_usd` | US$22.0359 over 11 of 11 pass(es) |
| Passes with no `cost_usd` | 0 |
| Summed wall clock | 1.52 h over 11 pass(es) |

> **The recorded cost is NOT this run's cost.** Each `cost_usd` above is the pass meta's own `cost_estimate.total_cost_usd`, lifted verbatim by `scripts/generate_post_run_report.py`. The token-load audit of 2026-06-12 established that those self-reported estimates price at STANDARD rates although the audited runs executed at `--service-tier flex` (half price) and omit thinking tokens although Gemini bills thinking at the output rate (`reports/token-load-audit-2026-06-12.md` § 1, § 2). The sum is reproduced here as the recorded figure and as an input to a reconciliation, not as a total to cite.

No cost audit on file names this run or its directory: an independently audited cost for this run is **not supplied**. The four audits checked are `reports/token-load-audit-2026-06-12.md`, `reports/r7-gaps-deltas-2026-09-11.md`, `reports/k-ladder-phase2-deltas-2026-09-12.md`, `reports/billing-reconciliation-2026-09-11.md`.

## 5. Registered conditions (1)

F1@20 m is the preregistered localisation buffer; F1@50 m is the deployment working buffer. Confidence intervals are those the evaluation recorded (method, iterations and seed per condition in the manifest). `mcc` is tile-level. A cell reading *not supplied* means the metric is absent from the condition's evaluation, not that it is zero; a tile-MCC reading *withheld* means the tile-join invariant REFUSED that condition's per-tile table on this frame, so the tile metrics and the bootstrap intervals were not computed — the condition's whole-frame F1 is unaffected and is reported in full (PI ruling 2026-09-13; the named reason is in the condition's manifest row).

| Condition | Architecture | Aggregation | Passes | Operating point | Detections | F1@20 m [CI] | F1@50 m [CI] | Tile MCC |
|---|---|---|---:|---|---:|---|---|---:|
| `g384-ov240-k10-verified-p0.15-k10` | proposer-verifier | verified | 10 | k=10/pt=0.15 | 423 | 0.8860 [0.8588, 0.9093] | not supplied | 0.7910 |

Buffers on file (metres), by how many conditions carry that set:

- 1 condition(s): 20

Tile-level MCC is on file for 1 of 1 condition(s).

### 5.1 Condition caveats (1 condition(s), 1 distinct caveat(s))

Grouped by identical text: a caveat written once for a family of sibling cells is reproduced once, with every cell it applies to named. Nothing is elided.

- `g384-ov240-k10-verified-p0.15-k10`
  Stride-programme verified best point (13-cell board member, F1@20 0.8860). Carry-forward verifier (verify\_adversarial-text, T=0.0, MINIMAL, n=1) over the full K=10 union.

### 5.3 Decomposition note

Verbatim from `results/run-conditions.json` — the hand-authored record of how this run was decomposed and what was adjudicated:

> Stride programme Phase C (2026-08-25): the 384/62.5% rung-144 cell, K=10, same protocol as Phase B.

### 5.4 Waived evaluations (2, 1 distinct reason(s))

Scored evaluations under this run that no condition claims, each waived in `results/run-conditions.json` rather than left silent. Grouped by identical reason; where a reason covers more than 12 paths the first 12 are named and the decomposition carries the rest.

- **2 evaluation(s)** — uplift-supplement K=1 anchor (planning/uplift-supplement-2026-08-28.md; scored 5bd514542): an input to the supplement's pairing tables, on the reference of the stratum it pairs with; not a registered condition and not cited by the paper. Waived by PI ruling 2026-09-07 (planning/reference-revision-2026-09-06.md, register-verifier debt).
  - `results/uplift-supplement/k1-gapfill/stride-phasec-2026-08-25__g384-ov240-k10-verified-p0_15-k10/evaluation.json`
  - `results/uplift-supplement/verifier-pairing/stride-phasec-2026-08-25__g384-ov240-k10-verified-p0_15-k10/evaluation.json`

## 6. Analyses that read this run (3)

A run is linked to an analysis when the analysis's `conditions_compared` names one of this run's conditions. *Cells* is how many of the analysis's compared conditions come from this run, out of its total. *Signed* is the register's `manually_verified_at` stamp.

| Analysis | Cells | Type | Hypotheses | Registration | Paper section | Deviations | Signed | Output |
|---|---|---|---|---|---|---|---|---|
| `stride-plateau-2026-08-25` | 1 of 9 | leaderboard | `H13` | post-hoc | Results | — | 2026-08-28T12:16:45Z | `results/stride-2026-08-25/plateau_analyses.json` |
| `uplift-supplement-flatten` | 1 of 441 | diagnostic | — | post-hoc | Appendix | — | 2026-09-10T22:55:40Z | `results/uplift-supplement/conditions.csv` |
| `verifier-uplift-pairing` | 1 of 170 | comparison | `H2` | post-hoc | Appendix | — | 2026-09-12T06:04:30Z | `results/uplift-supplement/verifier-uplift.csv` |

## 7. Findings documents (1)

| Document | Named by |
|---|---|
| `results/stride-2026-08-25/findings.md` | `stride-plateau-2026-08-25` |

## 8. Protocol errata

No erratum in `docs/methodology/preregistration/protocol-errata.md` is registered against an analysis of this run, and none mentions the run or its directory.

## 9. Documents and structure in the run directory

| Document class | Filename | Count |
|---|---|---:|
| per-pass/per-run intent | `experiment_intent.md` | 11 |

These classes are in Revision-Policy scope going forward (`docs/methodology/output-directory-standard.md` § "Documents in Revision Policy Scope").

### 9.1 Registered pools

| Proposer pool | Modality | Path within the run directory |
|---|---|---|
| `g384_ov240` | text | `g384_ov240` |

1 registered verifier-pass directory/directories; see `results/run-conditions.json` for the full list.

## 10. Provenance of this report

This report is a projection. Every figure above is read from one of the committed inputs below; nothing is estimated, and a figure that is not on file is written **not supplied** with its reason.

| Field | Value |
|---|---|
| Generator | `scripts/generate_run_reports.py` v1.1.0 |
| Source commit | `11e576e9c` |
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
- `outputs/grid-2026-08-18/scoring/bounds/grid_common_bounds.geojson`

Regenerate and drift-check with:

```bash
python3 scripts/generate_run_reports.py --all --write
python3 scripts/generate_run_reports.py --check
```
