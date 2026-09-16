<!-- GENERATED FILE — do not hand-edit. Projected from the registered manifests by scripts/generate_run_reports.py v1.1.0. Hand edits are destroyed on the next regeneration and fail the --check drift guard. -->
# Post-run report — gold-standard-v2

> **GENERATED FILE — do not hand-edit.** Projected from the registered manifests by `scripts/generate_run_reports.py` v1.1.0 at source commit `1f6826f5e`. This file carries provenance instead of a hand changelog, per the PI ruling of 2026-09-11 recorded in `docs/methodology/output-directory-standard.md` § "Documents in Revision Policy Scope": a generated document's history is its inputs' and its generator's git history, so "is this current?" is answered by the `--check` drift guard and its tier-1 test, not by a changelog. Regenerate after any manifest rebuild; put before/after notes in the commit message.

**Directory**: `outputs/gs/gold-standard-v2` · **Registry status**: active · **Purpose**: Canonical 4-map gold-standard pipeline (detect\_brief-text, HIGH, T=0.7, K=5); paper headline GS result.

## 1. Identity and registration

| Field | Value |
|---|---|
| Run id | `gold-standard-v2` |
| Directory | `outputs/gs/gold-standard-v2` |
| Registry status | active |
| Purpose | Canonical 4-map gold-standard pipeline (detect\_brief-text, HIGH, T=0.7, K=5); paper headline GS result. |
| Run type (derived) | mixed |
| Primary hypothesis | not supplied |
| Also informs | — |
| Headline condition | not supplied |
| Headline rationale | not supplied |
| Historical aliases | `Era 2`, `the v2 GS run` |
| Working-notes Obs | — |
| Registry notes | Populated vertical slice (Session 92). Paper headline GS run. |

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

### 3.1 Proposer passes (5)

| Pool | Pass | Model used | Model requested | Modality | Thinking | Temp | Status | Tiles done | Dispatched | Retries |
|---|---:|---|---|---|---|---:|---|---:|---:|---:|
| `detect_brief-text` | 1 | gemini-3-flash-preview | gemini-3-flash-preview | text | high | 0.7 | ok | 487 | 487 | 302 |
| `detect_brief-text` | 2 | gemini-3-flash-preview | gemini-3-flash-preview | text | high | 0.7 | ok | 487 | 487 | 302 |
| `detect_brief-text` | 3 | gemini-3-flash-preview | gemini-3-flash-preview | text | high | 0.7 | ok | 487 | 487 | 420 |
| `detect_brief-text` | 4 | gemini-3-flash-preview | gemini-3-flash-preview | text | high | 0.7 | ok | 487 | 487 | 205 |
| `detect_brief-text` | 5 | gemini-3-flash-preview | gemini-3-flash-preview | text | high | 0.7 | ok | 487 | 487 | 270 |

### 3.2 Verifier passes (1)

| Pool | Pass | Model used | Modality | Thinking | Temp | Status | Candidates verified | Retries |
|---|---:|---|---|---|---:|---|---:|---:|
| `verified-v1` | 1 | gemini-3-flash-preview | image | minimal | 0.0 | ok | 11 | 0 |

Verifier rows report no tile count by design: verifier pass: operates on candidate crops, not tiles. The verifier meta records candidate ids (cand\_NNNN) in execution\_stats.completed\_items and candidate API items in per\_item\_metadata, so no tile-scale record exists to report. Completed crop count is in n\_candidates\_verified. (E71 Defect 2 / GAP-8, resolved E72 2026-08-02.)

## 4. Token load and recorded cost

| Field | Value |
|---|---|
| Passes on file | 6 |
| Input tokens (billed) | 6,616,496 |
| Input tokens (cached) | 0 |
| Output tokens | 893,994 |
| Thinking tokens | 11,902,673 |
| Total tokens | 19,413,163 |
| Passes with no token record | 0 |
| Sum of recorded `cost_usd` | US$5.9902 over 6 of 6 pass(es) |
| Passes with no `cost_usd` | 0 |
| Summed wall clock | 1.39 h over 6 pass(es) |

> **The recorded cost is NOT this run's cost.** Each `cost_usd` above is the pass meta's own `cost_estimate.total_cost_usd`, lifted verbatim by `scripts/generate_post_run_report.py`. The token-load audit of 2026-06-12 established that those self-reported estimates price at STANDARD rates although the audited runs executed at `--service-tier flex` (half price) and omit thinking tokens although Gemini bills thinking at the output rate (`reports/token-load-audit-2026-06-12.md` § 1, § 2). The sum is reproduced here as the recorded figure and as an input to a reconciliation, not as a total to cite.

No cost audit on file names this run or its directory: an independently audited cost for this run is **not supplied**. The four audits checked are `reports/token-load-audit-2026-06-12.md`, `reports/r7-gaps-deltas-2026-09-11.md`, `reports/k-ladder-phase2-deltas-2026-09-12.md`, `reports/billing-reconciliation-2026-09-11.md`.

## 5. Registered conditions (4)

F1@20 m is the preregistered localisation buffer; F1@50 m is the deployment working buffer. Confidence intervals are those the evaluation recorded (method, iterations and seed per condition in the manifest). `mcc` is tile-level. A cell reading *not supplied* means the metric is absent from the condition's evaluation, not that it is zero; a tile-MCC reading *withheld* means the tile-join invariant REFUSED that condition's per-tile table on this frame, so the tile metrics and the bootstrap intervals were not computed — the condition's whole-frame F1 is unaffected and is reported in full (PI ruling 2026-09-13; the named reason is in the condition's manifest row).

| Condition | Architecture | Aggregation | Passes | Operating point | Detections | F1@20 m [CI] | F1@50 m [CI] | Tile MCC |
|---|---|---|---:|---|---:|---|---|---:|
| `consensus-3of5` | consensus | consensus | 5 | k=3 | 868 | 0.5925 [0.5387, 0.6421] | 0.6140 [0.5602, 0.6638] | 0.2964 |
| `consensus-4of5` | consensus | consensus | 5 | k=4 | 608 | 0.6999 [0.6486, 0.7455] | 0.7210 [0.6708, 0.7652] | 0.4557 |
| `consensus-5of5` | consensus | consensus | 5 | k=5 | 420 | 0.7649 [0.7192, 0.8040] | 0.7813 [0.7365, 0.8185] | 0.5791 |
| `verified-v1` | proposer-verifier | verified | 5 | k=4 | 380 | 0.8663 [0.8317, 0.8942] | 0.8859 [0.8536, 0.9115] | 0.7778 |

Buffers on file (metres), by how many conditions carry that set:

- 3 condition(s): 5, 10, 15, 20, 25, 30, 35, 40, 45, 50
- 1 condition(s): 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 75, 100, 125, 150

Tile-level MCC is on file for 4 of 4 condition(s).

## 6. Analyses that read this run (2)

A run is linked to an analysis when the analysis's `conditions_compared` names one of this run's conditions. *Cells* is how many of the analysis's compared conditions come from this run, out of its total. *Signed* is the register's `manually_verified_at` stamp.

| Analysis | Cells | Type | Hypotheses | Registration | Paper section | Deviations | Signed | Output |
|---|---|---|---|---|---|---|---|---|
| `uplift-supplement-flatten` | 4 of 441 | diagnostic | — | post-hoc | Appendix | — | 2026-09-10T22:55:40Z | `results/uplift-supplement/conditions.csv` |
| `verifier-uplift-pairing` | 1 of 170 | comparison | `H2` | post-hoc | Appendix | — | 2026-09-12T06:04:30Z | `results/uplift-supplement/verifier-uplift.csv` |

## 7. Findings documents (0)

No findings document on disk is named by an analysis that reads this run: a findings write-up for this run is **not supplied** from the register. § 6's `output_path` column gives each analysis's artefact directory.

## 8. Protocol errata

### 8.2 Mentioning this run (2)

The entry's text names this run id or its directory path. A mention is a pointer to read the entry, not a claim that the erratum is about this run:

- **E56** — Verifier probability-threshold operating points are in-sample (test-set-selected), not calibrated
- **E79** — Order-dependent tile assignment in `evaluate\_detections.py` — a scoring sensitivity of ~0.01 F1 on the 123 conditions whose detection artefact carries no `source\_tile`

## 9. Documents and structure in the run directory

| Document class | Filename | Count |
|---|---|---:|
| per-pass/per-run intent | `experiment_intent.md` | 4 |

These classes are in Revision-Policy scope going forward (`docs/methodology/output-directory-standard.md` § "Documents in Revision Policy Scope").

### 9.1 Registered pools

| Proposer pool | Modality | Path within the run directory |
|---|---|---|
| `detect_brief-text` | text | not supplied (string-form pool; resolved as `proposer/detect_brief-text`) |

1 registered verifier-pass directory/directories; see `results/run-conditions.json` for the full list.

## 10. Provenance of this report

This report is a projection. Every figure above is read from one of the committed inputs below; nothing is estimated, and a figure that is not on file is written **not supplied** with its reason.

| Field | Value |
|---|---|
| Generator | `scripts/generate_run_reports.py` v1.1.0 |
| Source commit | `1f6826f5e` |
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
- `outputs/gs/gold-standard-v2/proposer/detect_brief-text/run_1/detections-detect_brief-text-3-flash-2026-04-10.meta.json`

Regenerate and drift-check with:

```bash
python3 scripts/generate_run_reports.py --all --write
python3 scripts/generate_run_reports.py --check
```
