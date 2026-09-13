<!-- GENERATED FILE — do not hand-edit. Projected from the registered manifests by scripts/generate_run_reports.py v1.1.0. Hand edits are destroyed on the next regeneration and fail the --check drift guard. -->
# Post-run report — gemini37-image-gs-2026-09-01

> **GENERATED FILE — do not hand-edit.** Projected from the registered manifests by `scripts/generate_run_reports.py` v1.1.0 at source commit `47e73b214`. This file carries provenance instead of a hand changelog, per the PI ruling of 2026-09-11 recorded in `docs/methodology/output-directory-standard.md` § "Documents in Revision Policy Scope": a generated document's history is its inputs' and its generator's git history, so "is this current?" is answered by the `--check` drift guard and its tier-1 test, not by a changelog. Regenerate after any manifest rebuild; put before/after notes in the commit message.

**Directory**: `outputs/gemini37-image-gs-2026-09-01` · **Registry status**: active · **Purpose**: Image variant of the 3.7 GS screen under matched everything, for the difference-in-differences against the Gemini-3 modality contrast (image-b-gs-2026-08-28). Predictions I1-I5 committed at PI go (card planning/gemini37-image-gs-2026-08-30.md). The escalation trigger was not met; no 55-map image extension followed.

## 1. Identity and registration

| Field | Value |
|---|---|
| Run id | `gemini37-image-gs-2026-09-01` |
| Directory | `outputs/gemini37-image-gs-2026-09-01` |
| Registry status | active |
| Purpose | Image variant of the 3.7 GS screen under matched everything, for the difference-in-differences against the Gemini-3 modality contrast (image-b-gs-2026-08-28). Predictions I1-I5 committed at PI go (card planning/gemini37-image-gs-2026-08-30.md). The escalation trigger was not met; no 55-map image extension followed. |
| Run type (derived) | proposer-verifier |
| Primary hypothesis | not supplied |
| Also informs | `H1` |
| Headline condition | gemini37-image-gs-2026-09-01::g37-image-k5-verified-swap37-p0.90-k5 |
| Headline rationale | The all-3.7 image stack (F1@20 0.9308, tile-MCC 0.8322) — the highest F1@20 anywhere in the 3.7 arc, and the cell that makes the modality gap vanish. |
| Historical aliases | — |
| Working-notes Obs | — |
| Registry notes | Gemini 3.7 Flash image-GS screen (card planning/gemini37-image-gs-2026-08-30.md; predictions I1-I5 committed at PI go): detect\_brief-text-image on the same geometry and reference as the text screen, two verifier arms. The escalation trigger was NOT met and no 55-map image extension followed; the negative decision is itself the registered outcome. Registered S149. |

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

### 3.1 Proposer passes (5)

| Pool | Pass | Model used | Model requested | Modality | Thinking | Temp | Status | Tiles done | Dispatched | Retries |
|---|---:|---|---|---|---|---:|---|---:|---:|---:|
| `g384_ov192_g37img` | 1 | gemini-3.7-flash | gemini-3.7-flash | image | low | 0.7 | ok | 1398 | 1398 | 3001 |
| `g384_ov192_g37img` | 2 | gemini-3.7-flash | gemini-3.7-flash | image | low | 0.7 | ok | 1398 | 1398 | 20932 |
| `g384_ov192_g37img` | 3 | gemini-3.7-flash | gemini-3.7-flash | image | low | 0.7 | ok | 1398 | 1398 | 20896 |
| `g384_ov192_g37img` | 4 | gemini-3.7-flash | gemini-3.7-flash | image | low | 0.7 | ok | 1398 | 1398 | 19976 |
| `g384_ov192_g37img` | 5 | gemini-3.7-flash | gemini-3.7-flash | image | low | 0.7 | ok | 1398 | 1398 | 5238 |

### 3.2 Verifier passes (2)

| Pool | Pass | Model used | Modality | Thinking | Temp | Status | Candidates verified | Retries |
|---|---:|---|---|---|---:|---|---:|---:|
| `g384_ov192_g37img-union-k5-verify-arm1` | 1 | gemini-3-flash-preview | text | minimal | 0.0 | ok | 674 | 1 |
| `g384_ov192_g37img-union-k5-verify-arm2` | 1 | gemini-3.7-flash | text | low | 0.0 | ok | 674 | 420 |

Verifier rows report no tile count by design: verifier pass: operates on candidate crops, not tiles. The verifier meta records candidate ids (cand\_NNNN) in execution\_stats.completed\_items and candidate API items in per\_item\_metadata, so no tile-scale record exists to report. Completed crop count is in n\_candidates\_verified. (E71 Defect 2 / GAP-8, resolved E72 2026-08-02.)

## 4. Token load and recorded cost

| Field | Value |
|---|---|
| Passes on file | 7 |
| Input tokens (billed) | 56,504,252 |
| Input tokens (cached) | 42,722,394 |
| Output tokens | 413,830 |
| Thinking tokens | 520,085 |
| Total tokens | 57,438,167 |
| Passes with no token record | 0 |
| Sum of recorded `cost_usd` | US$15.6508 over 7 of 7 pass(es) |
| Passes with no `cost_usd` | 0 |
| Summed wall clock | 8.37 h over 7 pass(es) |

> **The recorded cost is NOT this run's cost.** Each `cost_usd` above is the pass meta's own `cost_estimate.total_cost_usd`, lifted verbatim by `scripts/generate_post_run_report.py`. The token-load audit of 2026-06-12 established that those self-reported estimates price at STANDARD rates although the audited runs executed at `--service-tier flex` (half price) and omit thinking tokens although Gemini bills thinking at the output rate (`reports/token-load-audit-2026-06-12.md` § 1, § 2). The sum is reproduced here as the recorded figure and as an input to a reconciliation, not as a total to cite.

No cost audit on file names this run or its directory: an independently audited cost for this run is **not supplied**. The four audits checked are `reports/token-load-audit-2026-06-12.md`, `reports/r7-gaps-deltas-2026-09-11.md`, `reports/k-ladder-phase2-deltas-2026-09-12.md`, `reports/billing-reconciliation-2026-09-11.md`.

## 5. Registered conditions (4)

F1@20 m is the preregistered localisation buffer; F1@50 m is the deployment working buffer. Confidence intervals are those the evaluation recorded (method, iterations and seed per condition in the manifest). `mcc` is tile-level. A cell reading *not supplied* means the metric is absent from the condition's evaluation, not that it is zero.

| Condition | Architecture | Aggregation | Passes | Operating point | Detections | F1@20 m [CI] | F1@50 m [CI] | Tile MCC |
|---|---|---|---:|---|---:|---|---|---:|
| `g37-image-k5-verified-carried-p0.10-k5` | proposer-verifier | verified | 5 | k=5/pt=0.1 | 430 | 0.9254 [0.8989, 0.9457] | 0.9347 [0.9098, 0.9530] | 0.8192 |
| `g37-image-k5-verified-carried-p0.10-k5-era2b` | proposer-verifier | verified | 5 | k=5/pt=0.1 | 430 | 0.9179 [0.8901, 0.9391] | 0.9272 [0.9011, 0.9470] | 0.8133 |
| `g37-image-k5-verified-swap37-p0.90-k5` | proposer-verifier | verified | 5 | k=5/pt=0.9 | 425 | 0.9308 [0.9049, 0.9505] | 0.9402 [0.9158, 0.9578] | 0.8322 |
| `g37-image-k5-verified-swap37-p0.90-k5-era2b` | proposer-verifier | verified | 5 | k=5/pt=0.9 | 425 | 0.9233 [0.8963, 0.9439] | 0.9326 [0.9072, 0.9511] | 0.8264 |

Buffers on file (metres), by how many conditions carry that set:

- 4 condition(s): 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 75, 100, 125, 150

Tile-level MCC is on file for 4 of 4 condition(s).

### 5.1 Condition caveats (4 condition(s), 4 distinct caveat(s))

Grouped by identical text: a caveat written once for a family of sibling cells is reproduced once, with every cell it applies to named. Nothing is elided.

- `g37-image-k5-verified-carried-p0.10-k5`
  A7 — image under the carried Gemini-3 verifier (F1@20 0.925408, tile-MCC 0.8192, 430 detections), +0.0842 over the 0.8412 Gemini-3 image anchor. Its within-family text pair is A1: (text - image) = -0.0115, p = 0.2533 (gap\_test.json).
- `g37-image-k5-verified-swap37-p0.90-k5`
  A8 — the all-3.7 image stack (F1@20 0.930832, tile-MCC 0.8322, 425 detections), the highest F1@20 in the 3.7 arc, +0.0896 over the Gemini-3 image anchor. Its within-family text pair is A3: (text - image) = -0.0043, p = 0.6767. Sweep argmax tie at prob\_t 0.90 / 0.95.
- `g37-image-k5-verified-carried-p0.10-k5-era2b`
  GS Era-2 verified board cell (planning/gs-era2-verified-board-2026-09-08.md, PI frame ruling 2026-09-09): the registered cell g37-image-k5-verified-carried-p0.10-k5 re-scored with its committed recipe on the Era-2 ∩ B-union frame (era2-b-487); the committed evaluation on grid\_common\_bounds.geojson stays the row's record.
- `g37-image-k5-verified-swap37-p0.90-k5-era2b`
  GS Era-2 verified board cell (planning/gs-era2-verified-board-2026-09-08.md, PI frame ruling 2026-09-09): the registered cell g37-image-k5-verified-swap37-p0.90-k5 re-scored with its committed recipe on the Era-2 ∩ B-union frame (era2-b-487); the committed evaluation on grid\_common\_bounds.geojson stays the row's record.

### 5.2 Scope overrides (2 condition(s), 1 distinct frame(s))

These conditions are scored on a frame other than the run's nominal scope in § 2 — the 327-vs-487 leakage trap the verifier exists to catch, disclosed per condition:

- `g37-image-k5-verified-carried-p0.10-k5-era2b`, `g37-image-k5-verified-swap37-p0.90-k5-era2b`
  bounds\_path = inputs/vectors/bounds/384/era2\_b\_intersection\_bounds.geojson, calibration\_set\_id = None, n\_calibration\_tiles = None, n\_test\_tiles = 487, test\_set\_id = era2-b-487

### 5.3 Decomposition note

Verbatim from `results/run-conditions.json` — the hand-authored record of how this run was decomposed and what was adjudicated:

> Image variant of the 3.7 GS screen on the same geometry, footprint and reference (detect\_brief-text-image; K=5; 674-candidate union). Two verifier arms over that one union: arm 1 the carried gemini-3-flash-preview, arm 2 gemini-3.7-flash. GOTCHA: scripts/image\_b\_analysis.py:79 hard-codes ANCHOR\_F1\_20 = 0.8961, so the built-in head\_to\_head\_20m blocks in arm{1,2}/analysis.json pair a 3.7 IMAGE cell against a GEMINI-3 TEXT cell and mix the family step into the modality contrast — never quote them as a modality delta; results/gemini37-image-gs-2026-09-01/gap\_test.json is the instrument. Both arms' sweep argmaxes are ties the analysis JSON does not flag (arm 2: prob\_t 0.90 and 0.95 give identical F1 0.9308323563892146 and 425 detections in arm2/sweep\_20m.csv).

### 5.4 Waived evaluations (4, 3 distinct reason(s))

Scored evaluations under this run that no condition claims, each waived in `results/run-conditions.json` rather than left silent. Grouped by identical reason; where a reason covers more than 12 paths the first 12 are named and the decomposition carries the rest.

- **2 evaluation(s)** — uplift-supplement K=1 anchor (planning/uplift-supplement-2026-08-28.md; scored 5bd514542): an input to the supplement's pairing tables, on the reference of the stratum it pairs with; not a registered condition and not cited by the paper. Waived by PI ruling 2026-09-07 (planning/reference-revision-2026-09-06.md, register-verifier debt).
  - `results/uplift-supplement/verifier-pairing/gemini37-image-gs-2026-09-01__g37-image-k5-verified-carried-p0_10-k5/evaluation.json`
  - `results/uplift-supplement/verifier-pairing/gemini37-image-gs-2026-09-01__g37-image-k5-verified-swap37-p0_90-k5/evaluation.json`
- **1 evaluation(s)** — GS Era-2 board gate G2 (planning/gs-era2-verified-board-2026-09-08.md): g37-image-k5-verified-carried-p0.10-k5's committed recipe re-run on its committed frame with a 200-draw bootstrap to prove the evaluator reproduces the committed evaluation; a gate artefact, not a condition.
  - `results/leaderboard/era2/gs-era2-verified-board-2026-09-10/g2/gemini37-image-gs-2026-09-01__g37-image-k5-verified-carried-p0_10-k5/evaluation.json`
- **1 evaluation(s)** — GS Era-2 board gate G2 (planning/gs-era2-verified-board-2026-09-08.md): g37-image-k5-verified-swap37-p0.90-k5's committed recipe re-run on its committed frame with a 200-draw bootstrap to prove the evaluator reproduces the committed evaluation; a gate artefact, not a condition.
  - `results/leaderboard/era2/gs-era2-verified-board-2026-09-10/g2/gemini37-image-gs-2026-09-01__g37-image-k5-verified-swap37-p0_90-k5/evaluation.json`

## 6. Analyses that read this run (4)

A run is linked to an analysis when the analysis's `conditions_compared` names one of this run's conditions. *Cells* is how many of the analysis's compared conditions come from this run, out of its total. *Signed* is the register's `manually_verified_at` stamp.

| Analysis | Cells | Type | Hypotheses | Registration | Paper section | Deviations | Signed | Output |
|---|---|---|---|---|---|---|---|---|
| `gemini37-image-gs-2026-09-01` | 2 of 6 | comparison | `H1` | post-hoc | Results | — | 2026-09-12T09:03:09Z | `results/gemini37-image-gs-2026-09-01` |
| `gs-era2-verified-board-2026-09-10` | 2 of 103 | leaderboard | `H2`, `H1` | post-hoc | Results | — | 2026-09-12T06:04:30Z | `results/leaderboard/era2/gs-era2-verified-board-2026-09-10/tiering_20m.json` |
| `uplift-supplement-flatten` | 2 of 441 | diagnostic | — | post-hoc | Appendix | — | 2026-09-10T22:55:40Z | `results/uplift-supplement/conditions.csv` |
| `verifier-uplift-pairing` | 2 of 170 | comparison | `H2` | post-hoc | Appendix | — | 2026-09-12T06:04:30Z | `results/uplift-supplement/verifier-uplift.csv` |

## 7. Findings documents (0)

No findings document on disk is named by an analysis that reads this run: a findings write-up for this run is **not supplied** from the register. § 6's `output_path` column gives each analysis's artefact directory.

## 8. Protocol errata

No erratum in `docs/methodology/preregistration/protocol-errata.md` is registered against an analysis of this run, and none mentions the run or its directory.

## 9. Documents and structure in the run directory

No `experiment_intent.md`, `evaluation.md`, `pre_launch_audit.md` or retrospective report under this directory.

### 9.1 Registered pools

| Proposer pool | Modality | Path within the run directory |
|---|---|---|
| `g384_ov192_g37img` | image | `g384_ov192_g37img` |

2 registered verifier-pass directory/directories; see `results/run-conditions.json` for the full list.

## 10. Provenance of this report

This report is a projection. Every figure above is read from one of the committed inputs below; nothing is estimated, and a figure that is not on file is written **not supplied** with its reason.

| Field | Value |
|---|---|
| Generator | `scripts/generate_run_reports.py` v1.1.0 |
| Source commit | `47e73b214` |
| Manifest extractor | `0.7.1` |
| Run row last extracted | `2026-09-06T05:11:51Z` |

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
