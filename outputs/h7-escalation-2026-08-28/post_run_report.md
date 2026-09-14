<!-- GENERATED FILE — do not hand-edit. Projected from the registered manifests by scripts/generate_run_reports.py v1.1.0. Hand edits are destroyed on the next regeneration and fail the --check drift guard. -->
# Post-run report — h7-escalation-2026-08-28

> **GENERATED FILE — do not hand-edit.** Projected from the registered manifests by `scripts/generate_run_reports.py` v1.1.0 at source commit `60b07ffcc`. This file carries provenance instead of a hand changelog, per the PI ruling of 2026-09-11 recorded in `docs/methodology/output-directory-standard.md` § "Documents in Revision Policy Scope": a generated document's history is its inputs' and its generator's git history, so "is this current?" is answered by the `--check` drift guard and its tier-1 test, not by a changelog. Regenerate after any manifest rebuild; put before/after notes in the commit message.

**Directory**: `outputs/h7-escalation-2026-08-28` · **Registry status**: active · **Purpose**: Discharge of the H7 temperature-escalation trigger (osf:731): T=1.6 and T=2.0 at the optimal configuration, characterising the upper bound of the temperature-performance curve.

## 1. Identity and registration

| Field | Value |
|---|---|
| Run id | `h7-escalation-2026-08-28` |
| Directory | `outputs/h7-escalation-2026-08-28` |
| Registry status | active |
| Purpose | Discharge of the H7 temperature-escalation trigger (osf:731): T=1.6 and T=2.0 at the optimal configuration, characterising the upper bound of the temperature-performance curve. |
| Run type (derived) | single-pass |
| Primary hypothesis | H7 |
| Also informs | — |
| Headline condition | h7-escalation-2026-08-28::text-t1.6 |
| Headline rationale | The first registered escalation level; the monotone-decline verdict. |
| Historical aliases | — |
| Working-notes Obs | — |
| Registry notes | H7 temperature-escalation discharge (prereg osf:731; card planning/run-predictions/h7-escalation-t1.6.md): T=1.6 and T=2.0, three replicates each, era-1-340. Registered S143 (Pass 3). |

## 2. Scope and evaluation frame

| Field | Value |
|---|---|
| Tile size (px) | 512 |
| Corpus | 4-map-gs |
| Ground-truth reference | curator |
| Test set id | era-1-340 |
| Test tiles | 340 |
| Bounds | `inputs/vectors/bounds/full_evaluation_bounds.geojson` |
| Calibration set id | not supplied |
| Calibration tiles | not supplied |

## 3. Execution — passes on file

### 3.1 Proposer passes (6)

| Pool | Pass | Model used | Model requested | Modality | Thinking | Temp | Status | Tiles done | Dispatched | Retries |
|---|---:|---|---|---|---|---:|---|---:|---:|---:|
| `t1.6` | 1 | gemini-3-flash-preview | gemini-3-flash-preview | text | minimal | 1.6 | ok | 340 | 340 | 0 |
| `t1.6` | 2 | gemini-3-flash-preview | gemini-3-flash-preview | text | minimal | 1.6 | ok | 340 | 340 | 0 |
| `t1.6` | 3 | gemini-3-flash-preview | gemini-3-flash-preview | text | minimal | 1.6 | ok | 340 | 340 | 0 |
| `t2.0` | 1 | gemini-3-flash-preview | gemini-3-flash-preview | text | minimal | 2.0 | ok | 340 | 340 | 1 |
| `t2.0` | 2 | gemini-3-flash-preview | gemini-3-flash-preview | text | minimal | 2.0 | ok | 340 | 340 | 1 |
| `t2.0` | 3 | gemini-3-flash-preview | gemini-3-flash-preview | text | minimal | 2.0 | ok | 340 | 340 | 2 |

## 4. Token load and recorded cost

| Field | Value |
|---|---|
| Passes on file | 6 |
| Input tokens (billed) | 3,064,080 |
| Input tokens (cached) | 0 |
| Output tokens | 404,126 |
| Thinking tokens | 0 |
| Total tokens | 3,468,206 |
| Passes with no token record | 0 |
| Sum of recorded `cost_usd` | US$1.3722 over 6 of 6 pass(es) |
| Passes with no `cost_usd` | 0 |
| Summed wall clock | 0.08 h over 6 pass(es) |

> **The recorded cost is NOT this run's cost.** Each `cost_usd` above is the pass meta's own `cost_estimate.total_cost_usd`, lifted verbatim by `scripts/generate_post_run_report.py`. The token-load audit of 2026-06-12 established that those self-reported estimates price at STANDARD rates although the audited runs executed at `--service-tier flex` (half price) and omit thinking tokens although Gemini bills thinking at the output rate (`reports/token-load-audit-2026-06-12.md` § 1, § 2). The sum is reproduced here as the recorded figure and as an input to a reconciliation, not as a total to cite.

No cost audit on file names this run or its directory: an independently audited cost for this run is **not supplied**. The four audits checked are `reports/token-load-audit-2026-06-12.md`, `reports/r7-gaps-deltas-2026-09-11.md`, `reports/k-ladder-phase2-deltas-2026-09-12.md`, `reports/billing-reconciliation-2026-09-11.md`.

## 5. Registered conditions (2)

F1@20 m is the preregistered localisation buffer; F1@50 m is the deployment working buffer. Confidence intervals are those the evaluation recorded (method, iterations and seed per condition in the manifest). `mcc` is tile-level. A cell reading *not supplied* means the metric is absent from the condition's evaluation, not that it is zero; a tile-MCC reading *withheld* means the tile-join invariant REFUSED that condition's per-tile table on this frame, so the tile metrics and the bootstrap intervals were not computed — the condition's whole-frame F1 is unaffected and is reported in full (PI ruling 2026-09-13; the named reason is in the condition's manifest row).

| Condition | Architecture | Aggregation | Passes | Operating point | Detections | F1@20 m [CI] | F1@50 m [CI] | Tile MCC |
|---|---|---|---:|---|---:|---|---|---:|
| `text-t1.6` | single-pass | none | 3 | — | not supplied | 0.4738 [0.4138, 0.5322] | 0.5649 [0.5015, 0.6236] | 0.0850 |
| `text-t2.0` | single-pass | none | 3 | — | not supplied | 0.4744 [0.4166, 0.5323] | 0.5680 [0.5050, 0.6261] | 0.0942 |

Buffers on file (metres), by how many conditions carry that set:

- 2 condition(s): 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 75, 100, 125, 150

Tile-level MCC is on file for 2 of 2 condition(s).

### 5.1 Condition caveats (2 condition(s), 2 distinct caveat(s))

Grouped by identical text: a caveat written once for a family of sibling cells is reproduced once, with every cell it applies to named. Nothing is elided.

- `text-t1.6`
  Replicate-mean F1@20 ~0.474 (phase2b grain); per-run 0.4806/0.4884/0.4524, all below their T=1.3 counterparts.
- `text-t2.0`
  Replicate-mean F1@20 ~0.474; per-run 0.4752/0.4714/0.4765, all significantly below T=1.3 (p=0.0013-0.0064). The degraded plateau.

### 5.3 Decomposition note

Verbatim from `results/run-conditions.json` — the hand-authored record of how this run was decomposed and what was adjudicated:

> Discharges the fired H7 escalation trigger at the letter (both registered levels; PI-approved 2026-08-28; ~$1.37 flex). Replication gate: the committed T1.0-vs-T1.3 check reproduced exactly before any new comparison. Outcome recorded in the prediction card and the hypothesis ledger.

## 6. Analyses that read this run (2)

A run is linked to an analysis when the analysis's `conditions_compared` names one of this run's conditions. *Cells* is how many of the analysis's compared conditions come from this run, out of its total. *Signed* is the register's `manually_verified_at` stamp.

| Analysis | Cells | Type | Hypotheses | Registration | Paper section | Deviations | Signed | Output |
|---|---|---|---|---|---|---|---|---|
| `h7-escalation-2026-08-28` | 2 of 4 | comparison | `H7` | registered-exploratory | Appendix | `Era-1 340-tile corpus per E36 (registered H7 ran the 60-tile holdout); real-time flex vs Batch (both 50% of list).` | 2026-08-28T12:43:12Z | `results/h7-escalation-2026-08-28` |
| `uplift-supplement-flatten` | 2 of 441 | diagnostic | — | post-hoc | Appendix | — | 2026-09-10T22:55:40Z | `results/uplift-supplement/conditions.csv` |

## 7. Findings documents (0)

No findings document on disk is named by an analysis that reads this run: a findings write-up for this run is **not supplied** from the register. § 6's `output_path` column gives each analysis's artefact directory.

## 8. Protocol errata

### 8.1 Registered as deviations (1)

Listed in the `deviations` field of an analysis that reads this run:

- **Era-1 340-tile corpus per E36 (registered H7 ran the 60-tile holdout); real-time flex vs Batch (both 50% of list).** — not supplied

## 9. Documents and structure in the run directory

| Document class | Filename | Count |
|---|---|---:|
| per-pass/per-run intent | `experiment_intent.md` | 6 |

These classes are in Revision-Policy scope going forward (`docs/methodology/output-directory-standard.md` § "Documents in Revision Policy Scope").

### 9.1 Registered pools

| Proposer pool | Modality | Path within the run directory |
|---|---|---|
| `t1.6` | text | `T1.6` |
| `t2.0` | text | `T2.0` |

## 10. Provenance of this report

This report is a projection. Every figure above is read from one of the committed inputs below; nothing is estimated, and a figure that is not on file is written **not supplied** with its reason.

| Field | Value |
|---|---|
| Generator | `scripts/generate_run_reports.py` v1.1.0 |
| Source commit | `60b07ffcc` |
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
