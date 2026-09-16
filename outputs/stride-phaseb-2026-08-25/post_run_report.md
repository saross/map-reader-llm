<!-- GENERATED FILE — do not hand-edit. Projected from the registered manifests by scripts/generate_run_reports.py v1.1.0. Hand edits are destroyed on the next regeneration and fail the --check drift guard. -->
# Post-run report — stride-phaseb-2026-08-25

> **GENERATED FILE — do not hand-edit.** Projected from the registered manifests by `scripts/generate_run_reports.py` v1.1.0 at source commit `8649b0758`. This file carries provenance instead of a hand changelog, per the PI ruling of 2026-09-11 recorded in `docs/methodology/output-directory-standard.md` § "Documents in Revision Policy Scope": a generated document's history is its inputs' and its generator's git history, so "is this current?" is answered by the `--check` drift guard and its tier-1 test, not by a changelog. Regenerate after any manifest rebuild; put before/after notes in the commit message.

**Directory**: `outputs/stride-phaseb-2026-08-25` · **Registry status**: active · **Purpose**: Stride programme Phase B (post-hoc, E41-class): four iso-stride geometry cells (512/34.4, 384/33.3, 256/25, 512/62.5) at K=10, one configuration, testing whether geometry is a plateau or a winner and where the interior stride optimum sits. Includes the union-k10 verifications and the winner-ladder exact re-verifications (k1/k3/k5).

## 1. Identity and registration

| Field | Value |
|---|---|
| Run id | `stride-phaseb-2026-08-25` |
| Directory | `outputs/stride-phaseb-2026-08-25` |
| Registry status | active |
| Purpose | Stride programme Phase B (post-hoc, E41-class): four iso-stride geometry cells (512/34.4, 384/33.3, 256/25, 512/62.5) at K=10, one configuration, testing whether geometry is a plateau or a winner and where the interior stride optimum sits. Includes the union-k10 verifications and the winner-ladder exact re-verifications (k1/k3/k5). |
| Run type (derived) | proposer-verifier |
| Primary hypothesis | not supplied |
| Also informs | `H13` |
| Headline condition | stride-phaseb-2026-08-25::g384-ov128-k10-verified-p0.15-k8 |
| Headline rationale | 13-cell board point-leader (verified F1@20 0.8982), one statistical tier with the incumbents (plateau-not-winner, Obs 435). |
| Historical aliases | — |
| Working-notes Obs | — |
| Registry notes | Stride Phase B: 4 geometry cells x10 passes + union verifications + winner-ladder exact verifications. Registered S143 (Pass 1). |

## 2. Scope and evaluation frame

| Field | Value |
|---|---|
| Tile size (px) | not supplied |
| Corpus | 4-map-gs |
| Ground-truth reference | curator |
| Test set id | grid-common-487 |
| Test tiles | 487 |
| Bounds | `outputs/grid-2026-08-18/scoring/bounds/grid_common_bounds.geojson` |
| Calibration set id | not supplied |
| Calibration tiles | not supplied |

## 3. Execution — passes on file

### 3.1 Proposer passes (40)

| Pool | Pass | Model used | Model requested | Modality | Thinking | Temp | Status | Tiles done | Dispatched | Retries |
|---|---:|---|---|---|---|---:|---|---:|---:|---:|
| `g256_ov064` | 1 | gemini-3-flash-preview | gemini-3-flash-preview | text | minimal | 0.7 | ok | 1403 | 1403 | 59 |
| `g256_ov064` | 2 | gemini-3-flash-preview | gemini-3-flash-preview | text | minimal | 0.7 | ok | 1403 | 1403 | 15 |
| `g256_ov064` | 3 | gemini-3-flash-preview | gemini-3-flash-preview | text | minimal | 0.7 | ok | 1403 | 1403 | 22 |
| `g256_ov064` | 4 | gemini-3-flash-preview | gemini-3-flash-preview | text | minimal | 0.7 | ok | 1403 | 1403 | 24 |
| `g256_ov064` | 5 | gemini-3-flash-preview | gemini-3-flash-preview | text | minimal | 0.7 | ok | 1403 | 1403 | 18 |
| `g256_ov064` | 6 | gemini-3-flash-preview | gemini-3-flash-preview | text | minimal | 0.7 | ok | 1403 | 1403 | 11 |
| `g256_ov064` | 7 | gemini-3-flash-preview | gemini-3-flash-preview | text | minimal | 0.7 | ok | 1403 | 1403 | 16 |
| `g256_ov064` | 8 | gemini-3-flash-preview | gemini-3-flash-preview | text | minimal | 0.7 | ok | 1403 | 1403 | 12 |
| `g256_ov064` | 9 | gemini-3-flash-preview | gemini-3-flash-preview | text | minimal | 0.7 | ok | 1403 | 1403 | 20 |
| `g256_ov064` | 10 | gemini-3-flash-preview | gemini-3-flash-preview | text | minimal | 0.7 | ok | 1403 | 1403 | 16 |
| `g384_ov128` | 1 | gemini-3-flash-preview | gemini-3-flash-preview | text | minimal | 0.7 | ok | 820 | 820 | 32 |
| `g384_ov128` | 2 | gemini-3-flash-preview | gemini-3-flash-preview | text | minimal | 0.7 | ok | 820 | 820 | 24 |
| `g384_ov128` | 3 | gemini-3-flash-preview | gemini-3-flash-preview | text | minimal | 0.7 | ok | 820 | 820 | 19 |
| `g384_ov128` | 4 | gemini-3-flash-preview | gemini-3-flash-preview | text | minimal | 0.7 | ok | 820 | 820 | 33 |
| `g384_ov128` | 5 | gemini-3-flash-preview | gemini-3-flash-preview | text | minimal | 0.7 | ok | 820 | 820 | 32 |
| `g384_ov128` | 6 | gemini-3-flash-preview | gemini-3-flash-preview | text | minimal | 0.7 | ok | 820 | 820 | 27 |
| `g384_ov128` | 7 | gemini-3-flash-preview | gemini-3-flash-preview | text | minimal | 0.7 | ok | 820 | 820 | 34 |
| `g384_ov128` | 8 | gemini-3-flash-preview | gemini-3-flash-preview | text | minimal | 0.7 | ok | 820 | 820 | 30 |
| `g384_ov128` | 9 | gemini-3-flash-preview | gemini-3-flash-preview | text | minimal | 0.7 | ok | 820 | 820 | 13 |
| `g384_ov128` | 10 | gemini-3-flash-preview | gemini-3-flash-preview | text | minimal | 0.7 | ok | 820 | 820 | 18 |
| `g512_ov176` | 1 | gemini-3-flash-preview | gemini-3-flash-preview | text | minimal | 0.7 | ok | 494 | 494 | 9 |
| `g512_ov176` | 2 | gemini-3-flash-preview | gemini-3-flash-preview | text | minimal | 0.7 | ok | 494 | 494 | 8 |
| `g512_ov176` | 3 | gemini-3-flash-preview | gemini-3-flash-preview | text | minimal | 0.7 | ok | 494 | 494 | 14 |
| `g512_ov176` | 4 | gemini-3-flash-preview | gemini-3-flash-preview | text | minimal | 0.7 | ok | 494 | 494 | 6 |
| `g512_ov176` | 5 | gemini-3-flash-preview | gemini-3-flash-preview | text | minimal | 0.7 | ok | 494 | 494 | 7 |
| `g512_ov176` | 6 | gemini-3-flash-preview | gemini-3-flash-preview | text | minimal | 0.7 | ok | 494 | 494 | 13 |
| `g512_ov176` | 7 | gemini-3-flash-preview | gemini-3-flash-preview | text | minimal | 0.7 | ok | 494 | 494 | 11 |
| `g512_ov176` | 8 | gemini-3-flash-preview | gemini-3-flash-preview | text | minimal | 0.7 | ok | 494 | 494 | 11 |
| `g512_ov176` | 9 | gemini-3-flash-preview | gemini-3-flash-preview | text | minimal | 0.7 | ok | 494 | 494 | 21 |
| `g512_ov176` | 10 | gemini-3-flash-preview | gemini-3-flash-preview | text | minimal | 0.7 | ok | 494 | 494 | 14 |
| `g512_ov320` | 1 | gemini-3-flash-preview | gemini-3-flash-preview | text | minimal | 0.7 | ok | 1408 | 1408 | 18 |
| `g512_ov320` | 2 | gemini-3-flash-preview | gemini-3-flash-preview | text | minimal | 0.7 | ok | 1408 | 1408 | 32 |
| `g512_ov320` | 3 | gemini-3-flash-preview | gemini-3-flash-preview | text | minimal | 0.7 | ok | 1408 | 1408 | 58 |
| `g512_ov320` | 4 | gemini-3-flash-preview | gemini-3-flash-preview | text | minimal | 0.7 | ok | 1408 | 1408 | 64 |
| `g512_ov320` | 5 | gemini-3-flash-preview | gemini-3-flash-preview | text | minimal | 0.7 | ok | 1408 | 1408 | 152 |
| `g512_ov320` | 6 | gemini-3-flash-preview | gemini-3-flash-preview | text | minimal | 0.7 | ok | 1408 | 1408 | 34 |
| `g512_ov320` | 7 | gemini-3-flash-preview | gemini-3-flash-preview | text | minimal | 0.7 | ok | 1408 | 1408 | 35 |
| `g512_ov320` | 8 | gemini-3-flash-preview | gemini-3-flash-preview | text | minimal | 0.7 | ok | 1408 | 1408 | 43 |
| `g512_ov320` | 9 | gemini-3-flash-preview | gemini-3-flash-preview | text | minimal | 0.7 | ok | 1408 | 1408 | 18 |
| `g512_ov320` | 10 | gemini-3-flash-preview | gemini-3-flash-preview | text | minimal | 0.7 | ok | 1408 | 1408 | 14 |

### 3.2 Verifier passes (7)

| Pool | Pass | Model used | Modality | Thinking | Temp | Status | Candidates verified | Retries |
|---|---:|---|---|---|---:|---|---:|---:|
| `g256_ov064-union-k10-verify` | 1 | gemini-3-flash-preview | text | minimal | 0.0 | ok | 3570 | 89 |
| `g384_ov128-union-k1-verify` | 1 | gemini-3-flash-preview | text | minimal | 0.0 | ok | 1290 | 14 |
| `g384_ov128-union-k10-verify` | 1 | gemini-3-flash-preview | text | minimal | 0.0 | ok | 2387 | 142 |
| `g384_ov128-union-k3-verify` | 1 | gemini-3-flash-preview | text | minimal | 0.0 | ok | 1700 | 0 |
| `g384_ov128-union-k5-verify` | 1 | gemini-3-flash-preview | text | minimal | 0.0 | ok | 1968 | 12 |
| `g512_ov176-union-k10-verify` | 1 | gemini-3-flash-preview | text | minimal | 0.0 | ok | 1981 | 41 |
| `g512_ov320-union-k10-verify` | 1 | gemini-3-flash-preview | text | minimal | 0.0 | ok | 3778 | 35 |

Verifier rows report no tile count by design: verifier pass: operates on candidate crops, not tiles. The verifier meta records candidate ids (cand\_NNNN) in execution\_stats.completed\_items and candidate API items in per\_item\_metadata, so no tile-scale record exists to report. Completed crop count is in n\_candidates\_verified. (E71 Defect 2 / GAP-8, resolved E72 2026-08-02.)

## 4. Token load and recorded cost

| Field | Value |
|---|---|
| Passes on file | 47 |
| Input tokens (billed) | 91,837,308 |
| Input tokens (cached) | 0 |
| Output tokens | 9,015,635 |
| Thinking tokens | 0 |
| Total tokens | 100,852,943 |
| Passes with no token record | 0 |
| Sum of recorded `cost_usd` | US$47.9185 over 47 of 47 pass(es) |
| Passes with no `cost_usd` | 0 |
| Summed wall clock | 5.73 h over 47 pass(es) |

> **The recorded cost is NOT this run's cost.** Each `cost_usd` above is the pass meta's own `cost_estimate.total_cost_usd`, lifted verbatim by `scripts/generate_post_run_report.py`. The token-load audit of 2026-06-12 established that those self-reported estimates price at STANDARD rates although the audited runs executed at `--service-tier flex` (half price) and omit thinking tokens although Gemini bills thinking at the output rate (`reports/token-load-audit-2026-06-12.md` § 1, § 2). The sum is reproduced here as the recorded figure and as an input to a reconciliation, not as a total to cite.

No cost audit on file names this run or its directory: an independently audited cost for this run is **not supplied**. The four audits checked are `reports/token-load-audit-2026-06-12.md`, `reports/r7-gaps-deltas-2026-09-11.md`, `reports/k-ladder-phase2-deltas-2026-09-12.md`, `reports/billing-reconciliation-2026-09-11.md`.

## 5. Registered conditions (7)

F1@20 m is the preregistered localisation buffer; F1@50 m is the deployment working buffer. Confidence intervals are those the evaluation recorded (method, iterations and seed per condition in the manifest). `mcc` is tile-level. A cell reading *not supplied* means the metric is absent from the condition's evaluation, not that it is zero; a tile-MCC reading *withheld* means the tile-join invariant REFUSED that condition's per-tile table on this frame, so the tile metrics and the bootstrap intervals were not computed — the condition's whole-frame F1 is unaffected and is reported in full (PI ruling 2026-09-13; the named reason is in the condition's manifest row).

| Condition | Architecture | Aggregation | Passes | Operating point | Detections | F1@20 m [CI] | F1@50 m [CI] | Tile MCC |
|---|---|---|---:|---|---:|---|---|---:|
| `g256-ov064-k10-verified-p0.15-k8` | proposer-verifier | verified | 10 | k=8/pt=0.15 | 427 | 0.8795 [0.8503, 0.9036] | not supplied | 0.7959 |
| `g384-ov128-k10-verified-p0.15-k8` | proposer-verifier | verified | 10 | k=8/pt=0.15 | 387 | 0.8982 [0.8698, 0.9213] | not supplied | 0.8022 |
| `g384-ov128-ladder-n1-verified-p0.15-k1` | proposer-verifier | verified | 1 | k=1/pt=0.15 | 411 | 0.8677 [0.8369, 0.8953] | not supplied | 0.7894 |
| `g384-ov128-ladder-n3-verified-p0.15-k3` | proposer-verifier | verified | 3 | k=3/pt=0.15 | 380 | 0.8911 [0.8615, 0.9161] | not supplied | 0.7814 |
| `g384-ov128-ladder-n5-verified-p0.15-k4` | proposer-verifier | verified | 5 | k=4/pt=0.15 | 394 | 0.8856 [0.8554, 0.9113] | not supplied | 0.7805 |
| `g512-ov176-k10-verified-p0.15-k6` | proposer-verifier | verified | 10 | k=6/pt=0.15 | 390 | 0.8655 [0.8305, 0.8934] | not supplied | 0.7964 |
| `g512-ov320-k10-verified-p0.15-k10` | proposer-verifier | verified | 10 | k=10/pt=0.15 | 397 | 0.8800 [0.8478, 0.9055] | not supplied | 0.8023 |

Buffers on file (metres), by how many conditions carry that set:

- 7 condition(s): 20

Tile-level MCC is on file for 7 of 7 condition(s).

### 5.1 Condition caveats (7 condition(s), 7 distinct caveat(s))

Grouped by identical text: a caveat written once for a family of sibling cells is reproduced once, with every cell it applies to named. Nothing is elided.

- `g512-ov176-k10-verified-p0.15-k6`
  Stride-programme verified best point (13-cell board member, F1@20 0.8655). Carry-forward verifier (verify\_adversarial-text, T=0.0, MINIMAL, n=1) over the full K=10 union.
- `g256-ov064-k10-verified-p0.15-k8`
  Stride-programme verified best point (13-cell board member, F1@20 0.8795). Carry-forward verifier (verify\_adversarial-text, T=0.0, MINIMAL, n=1) over the full K=10 union.
- `g512-ov320-k10-verified-p0.15-k10`
  Stride-programme verified best point (13-cell board member, F1@20 0.8800). Carry-forward verifier (verify\_adversarial-text, T=0.0, MINIMAL, n=1) over the full K=10 union.
- `g384-ov128-k10-verified-p0.15-k8`
  Stride-programme verified best point (13-cell board member, F1@20 0.8982). Carry-forward verifier (verify\_adversarial-text, T=0.0, MINIMAL, n=1) over the full K=10 union.
- `g384-ov128-ladder-n1-verified-p0.15-k1`
  Winner-ladder exact rung (first-1 passes, exact re-verification; F1@20 0.8677, union 1290). Carry-forward verifier (verify\_adversarial-text, T=0.0, MINIMAL, n=1) over the full K=10 union.
- `g384-ov128-ladder-n3-verified-p0.15-k3`
  Winner-ladder exact rung (first-3 passes, exact re-verification; F1@20 0.8911, union 1700). Carry-forward verifier (verify\_adversarial-text, T=0.0, MINIMAL, n=1) over the full K=10 union.
- `g384-ov128-ladder-n5-verified-p0.15-k4`
  Winner-ladder exact rung (first-5 passes, exact re-verification; F1@20 0.8856, union 1968). Carry-forward verifier (verify\_adversarial-text, T=0.0, MINIMAL, n=1) over the full K=10 union.

### 5.3 Decomposition note

Verbatim from `results/run-conditions.json` — the hand-authored record of how this run was decomposed and what was adjudicated:

> Stride programme Phase B (overnight 2026-08-25, PI-approved): four iso-stride geometry cells, K=10 brief-text MINIMAL T=0.7 flex. Winner-ladder exact verifications (k1/k3/k5, ~$3.4, PI-approved) nest here. Sweep interiors live under the stride-plateau analyses (PI ruling 2026-08-28).

### 5.4 Waived evaluations (13, 1 distinct reason(s))

Scored evaluations under this run that no condition claims, each waived in `results/run-conditions.json` rather than left silent. Grouped by identical reason; where a reason covers more than 12 paths the first 12 are named and the decomposition carries the rest.

- **13 evaluation(s)** — uplift-supplement K=1 anchor (planning/uplift-supplement-2026-08-28.md; scored 5bd514542): an input to the supplement's pairing tables, on the reference of the stratum it pairs with; not a registered condition and not cited by the paper. Waived by PI ruling 2026-09-07 (planning/reference-revision-2026-09-06.md, register-verifier debt).
  - `results/uplift-supplement/k1-gapfill/stride-phaseb-2026-08-25__g256-ov064-k10-verified-p0_15-k8/evaluation.json`
  - `results/uplift-supplement/k1-gapfill/stride-phaseb-2026-08-25__g384-ov128-k10-verified-p0_15-k8/evaluation.json`
  - `results/uplift-supplement/k1-gapfill/stride-phaseb-2026-08-25__g384-ov128-ladder-n3-verified-p0_15-k3/evaluation.json`
  - `results/uplift-supplement/k1-gapfill/stride-phaseb-2026-08-25__g384-ov128-ladder-n5-verified-p0_15-k4/evaluation.json`
  - `results/uplift-supplement/k1-gapfill/stride-phaseb-2026-08-25__g512-ov176-k10-verified-p0_15-k6/evaluation.json`
  - `results/uplift-supplement/k1-gapfill/stride-phaseb-2026-08-25__g512-ov320-k10-verified-p0_15-k10/evaluation.json`
  - `results/uplift-supplement/verifier-pairing/stride-phaseb-2026-08-25__g256-ov064-k10-verified-p0_15-k8/evaluation.json`
  - `results/uplift-supplement/verifier-pairing/stride-phaseb-2026-08-25__g384-ov128-k10-verified-p0_15-k8/evaluation.json`
  - `results/uplift-supplement/verifier-pairing/stride-phaseb-2026-08-25__g384-ov128-ladder-n1-verified-p0_15-k1/evaluation.json`
  - `results/uplift-supplement/verifier-pairing/stride-phaseb-2026-08-25__g384-ov128-ladder-n3-verified-p0_15-k3/evaluation.json`
  - `results/uplift-supplement/verifier-pairing/stride-phaseb-2026-08-25__g384-ov128-ladder-n5-verified-p0_15-k4/evaluation.json`
  - `results/uplift-supplement/verifier-pairing/stride-phaseb-2026-08-25__g512-ov176-k10-verified-p0_15-k6/evaluation.json`
  - … and 1 more under the same waiver (full list in `results/run-conditions.json`, this run's `_ignored_evals`)

## 6. Analyses that read this run (5)

A run is linked to an analysis when the analysis's `conditions_compared` names one of this run's conditions. *Cells* is how many of the analysis's compared conditions come from this run, out of its total. *Signed* is the register's `manually_verified_at` stamp.

| Analysis | Cells | Type | Hypotheses | Registration | Paper section | Deviations | Signed | Output |
|---|---|---|---|---|---|---|---|---|
| `k-ladder-2026-09-12` | 4 of 94 | comparison | `H3`, `H13` | post-hoc | Results | `E56`, `E85` | 2026-09-13T06:58:12Z | `results/k-ladder-2026-09-12/findings.md` |
| `stride-plateau-2026-08-25` | 4 of 9 | leaderboard | `H13` | post-hoc | Results | — | 2026-08-28T12:16:45Z | `results/stride-2026-08-25/plateau_analyses.json` |
| `stride-winner-ladder-exact-2026-08-25` | 4 of 4 | comparison | `H13`, `H3` | post-hoc | Results | — | 2026-08-28T12:16:45Z | `results/stride-2026-08-25/plateau_analyses.json` |
| `uplift-supplement-flatten` | 7 of 441 | diagnostic | — | post-hoc | Appendix | — | 2026-09-10T22:55:40Z | `results/uplift-supplement/conditions.csv` |
| `verifier-uplift-pairing` | 7 of 170 | comparison | `H2` | post-hoc | Appendix | — | 2026-09-12T06:04:30Z | `results/uplift-supplement/verifier-uplift.csv` |

## 7. Findings documents (2)

| Document | Named by |
|---|---|
| `results/k-ladder-2026-09-12/findings.md` | `k-ladder-2026-09-12` |
| `results/stride-2026-08-25/findings.md` | `stride-plateau-2026-08-25` |

## 8. Protocol errata

### 8.1 Registered as deviations (2)

Listed in the `deviations` field of an analysis that reads this run:

- **E56** — Verifier probability-threshold operating points are in-sample (test-set-selected), not calibrated
- **E85** — The temperature study's five consensus conditions were labelled N = 30 but read a 5-pass union — relabelled `consensus-{1..5}of5`; no measured value changes

## 9. Documents and structure in the run directory

| Document class | Filename | Count |
|---|---|---:|
| per-pass/per-run intent | `experiment_intent.md` | 43 |

These classes are in Revision-Policy scope going forward (`docs/methodology/output-directory-standard.md` § "Documents in Revision Policy Scope").

### 9.1 Registered pools

| Proposer pool | Modality | Path within the run directory |
|---|---|---|
| `g256_ov064` | text | `g256_ov064` |
| `g384_ov128` | text | `g384_ov128` |
| `g512_ov176` | text | `g512_ov176` |
| `g512_ov320` | text | `g512_ov320` |

7 registered verifier-pass directory/directories; see `results/run-conditions.json` for the full list.

## 10. Provenance of this report

This report is a projection. Every figure above is read from one of the committed inputs below; nothing is estimated, and a figure that is not on file is written **not supplied** with its reason.

| Field | Value |
|---|---|
| Generator | `scripts/generate_run_reports.py` v1.1.0 |
| Source commit | `8649b0758` |
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
