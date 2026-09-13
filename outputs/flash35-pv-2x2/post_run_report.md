<!-- GENERATED FILE — do not hand-edit. Projected from the registered manifests by scripts/generate_run_reports.py v1.1.0. Hand edits are destroyed on the next regeneration and fail the --check drift guard. -->
# Post-run report — flash35-pv-2x2

> **GENERATED FILE — do not hand-edit.** Projected from the registered manifests by `scripts/generate_run_reports.py` v1.1.0 at source commit `736c39c0e`. This file carries provenance instead of a hand changelog, per the PI ruling of 2026-09-11 recorded in `docs/methodology/output-directory-standard.md` § "Documents in Revision Policy Scope": a generated document's history is its inputs' and its generator's git history, so "is this current?" is answered by the `--check` drift guard and its tier-1 test, not by a changelog. Regenerate after any manifest rebuild; put before/after notes in the commit message.

**Directory**: `outputs/flash35-pv-2x2` · **Registry status**: active · **Purpose**: Model-role 2x2x2: is Flash 3.5 a better bare proposer, PV proposer, or verifier than Flash 3 at the minimal operating point? (The S110 parking note: bare proposer was the only angle a stronger model might win.)

## 1. Identity and registration

| Field | Value |
|---|---|
| Run id | `flash35-pv-2x2` |
| Directory | `outputs/flash35-pv-2x2` |
| Registry status | active |
| Purpose | Model-role 2x2x2: is Flash 3.5 a better bare proposer, PV proposer, or verifier than Flash 3 at the minimal operating point? (The S110 parking note: bare proposer was the only angle a stronger model might win.) |
| Run type (derived) | mixed |
| Primary hypothesis | not supplied |
| Also informs | `flash-vs-flash35`, `pv-strategy` |
| Headline condition | not supplied |
| Headline rationale | Deliberately none — a model comparison, not a champion search: Flash 3.5 wins in NO role (bare-proposer numerical tie 0.6196 vs 0.6204; PV proposer -0.0355, p=0.035 targeted tile-swap — the one resolved role gap; verifier -0.012..-0.015, within-noise ties, at 3x the price). The all-Flash-3 production stack stands (findings SS 14; results/flash35-2x2/flash35\_permutations.json). |
| Historical aliases | — |
| Working-notes Obs | — |
| Registry notes | Flash 3.5 model-role 2x2x2 (Sessions 111-112, ~$34 flex): 10 gemini-3.5-flash MINIMAL-thinking T=0.7 detect\_brief-text proposer passes on the GS 487 (384 px), three verifier legs (F3 vf over the F3.5 pool; F3.5 vf over the F3.5 pool; F3.5 vf over the cross-run F3 minimal pool), n in {5,10} via the verify-once shortcut (n=5 method-matched derivations are analysis-internal). Verdict: Flash 3.5 wins in NO role at the minimal operating point — the all-Flash-3 stack stands. Analysis: results/flash35-2x2/; findings verifier-robustness-findings.md SS 14; runbook scripts/run\_flash35\_tranche1.sh. |

## 2. Scope and evaluation frame

| Field | Value |
|---|---|
| Tile size (px) | 384 |
| Corpus | 4-map-gs |
| Ground-truth reference | curator |
| Test set id | era-2-487 |
| Test tiles | 487 |
| Bounds | `inputs/vectors/bounds/384/full_evaluation_bounds.geojson` |
| Calibration set id | not supplied |
| Calibration tiles | not supplied |

## 3. Execution — passes on file

### 3.1 Proposer passes (10)

| Pool | Pass | Model used | Model requested | Modality | Thinking | Temp | Status | Tiles done | Dispatched | Retries |
|---|---:|---|---|---|---|---:|---|---:|---:|---:|
| `flash35-min-text-1of10` | 1 | gemini-3.5-flash | gemini-3.5-flash | text | minimal | 0.7 | ok | 487 | 487 | 177 |
| `flash35-min-text-1of10` | 2 | gemini-3.5-flash | gemini-3.5-flash | text | minimal | 0.7 | ok | 487 | 487 | 294 |
| `flash35-min-text-1of10` | 3 | gemini-3.5-flash | gemini-3.5-flash | text | minimal | 0.7 | ok | 487 | 487 | 880 |
| `flash35-min-text-1of10` | 4 | gemini-3.5-flash | gemini-3.5-flash | text | minimal | 0.7 | ok | 487 | 487 | 470 |
| `flash35-min-text-1of10` | 5 | gemini-3.5-flash | gemini-3.5-flash | text | minimal | 0.7 | ok | 487 | 487 | 839 |
| `flash35-min-text-1of10` | 6 | gemini-3.5-flash | gemini-3.5-flash | text | minimal | 0.7 | ok | 487 | 487 | 347 |
| `flash35-min-text-1of10` | 7 | gemini-3.5-flash | gemini-3.5-flash | text | minimal | 0.7 | ok | 487 | 487 | 579 |
| `flash35-min-text-1of10` | 8 | gemini-3.5-flash | gemini-3.5-flash | text | minimal | 0.7 | ok | 487 | 487 | 1369 |
| `flash35-min-text-1of10` | 9 | gemini-3.5-flash | gemini-3.5-flash | text | minimal | 0.7 | ok | 487 | 487 | 360 |
| `flash35-min-text-1of10` | 10 | gemini-3.5-flash | gemini-3.5-flash | text | minimal | 0.7 | ok | 487 | 487 | 0 |

### 3.2 Verifier passes (3)

| Pool | Pass | Model used | Modality | Thinking | Temp | Status | Candidates verified | Retries |
|---|---:|---|---|---|---:|---|---:|---:|
| `min-f3-verified-f35vf` | 1 | gemini-3.5-flash | text | minimal | 0.0 | ok | 1939 | 0 |
| `verified-f35vf` | 1 | gemini-3.5-flash | text | minimal | 0.0 | ok | 1132 | 0 |
| `verified-f3vf` | 1 | gemini-3-flash-preview | text | minimal | 0.0 | ok | 1 | 0 |

Verifier rows report no tile count by design: verifier pass: operates on candidate crops, not tiles. The verifier meta records candidate ids (cand\_NNNN) in execution\_stats.completed\_items and candidate API items in per\_item\_metadata, so no tile-scale record exists to report. Completed crop count is in n\_candidates\_verified. (E71 Defect 2 / GAP-8, resolved E72 2026-08-02.)

## 4. Token load and recorded cost

| Field | Value |
|---|---|
| Passes on file | 13 |
| Input tokens (billed) | 12,842,294 |
| Input tokens (cached) | 0 |
| Output tokens | 1,028,278 |
| Thinking tokens | 0 |
| Total tokens | 13,870,572 |
| Passes with no token record | 0 |
| Sum of recorded `cost_usd` | US$9.5060 over 13 of 13 pass(es) |
| Passes with no `cost_usd` | 0 |
| Summed wall clock | 3.41 h over 13 pass(es) |

> **The recorded cost is NOT this run's cost.** Each `cost_usd` above is the pass meta's own `cost_estimate.total_cost_usd`, lifted verbatim by `scripts/generate_post_run_report.py`. The token-load audit of 2026-06-12 established that those self-reported estimates price at STANDARD rates although the audited runs executed at `--service-tier flex` (half price) and omit thinking tokens although Gemini bills thinking at the output rate (`reports/token-load-audit-2026-06-12.md` § 1, § 2). The sum is reproduced here as the recorded figure and as an input to a reconciliation, not as a total to cite.

No cost audit on file names this run or its directory: an independently audited cost for this run is **not supplied**. The four audits checked are `reports/token-load-audit-2026-06-12.md`, `reports/r7-gaps-deltas-2026-09-11.md`, `reports/k-ladder-phase2-deltas-2026-09-12.md`, `reports/billing-reconciliation-2026-09-11.md`.

## 5. Registered conditions (7)

F1@20 m is the preregistered localisation buffer; F1@50 m is the deployment working buffer. Confidence intervals are those the evaluation recorded (method, iterations and seed per condition in the manifest). `mcc` is tile-level. A cell reading *not supplied* means the metric is absent from the condition's evaluation, not that it is zero; a tile-MCC reading *withheld* means the tile-join invariant REFUSED that condition's per-tile table on this frame, so the tile metrics and the bootstrap intervals were not computed — the condition's whole-frame F1 is unaffected and is reported in full (PI ruling 2026-09-13; the named reason is in the condition's manifest row).

| Condition | Architecture | Aggregation | Passes | Operating point | Detections | F1@20 m [CI] | F1@50 m [CI] | Tile MCC |
|---|---|---|---:|---|---:|---|---|---:|
| `f35prop-bare-10of10` | consensus | consensus | 10 | k=10 | 598 | 0.6196 [0.5652, 0.6698] | 0.6273 [0.5735, 0.6770] | 0.2899 |
| `f35prop-f35vf-4of10` | proposer-verifier | verified | 10 | k=4/pt=0.25 | 371 | 0.8362 [0.7968, 0.8708] | 0.8437 [0.8063, 0.8765] | 0.7369 |
| `f35prop-f35vf-4of10-era2b` | proposer-verifier | verified | 10 | k=4/pt=0.25 | 371 | 0.8362 [0.7968, 0.8708] | 0.8437 [0.8063, 0.8765] | 0.7369 |
| `f35prop-f3vf-4of10` | proposer-verifier | verified | 10 | k=4/pt=0.15 | 374 | 0.8480 [0.8099, 0.8804] | 0.8578 [0.8213, 0.8881] | 0.7675 |
| `f35prop-f3vf-4of10-era2b` | proposer-verifier | verified | 10 | k=4/pt=0.15 | 374 | 0.8480 [0.8099, 0.8804] | 0.8578 [0.8213, 0.8881] | 0.7675 |
| `f3prop-f35vf-6of10` | proposer-verifier | verified | 10 | k=6/pt=0.25 | 389 | 0.8689 [0.8388, 0.8961] | 0.8908 [0.8626, 0.9146] | 0.7666 |
| `f3prop-f35vf-6of10-era2b` | proposer-verifier | verified | 10 | k=6/pt=0.25 | 389 | 0.8689 [0.8388, 0.8961] | 0.8908 [0.8626, 0.9146] | 0.7666 |

Buffers on file (metres), by how many conditions carry that set:

- 7 condition(s): 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 75, 100, 125, 150

Tile-level MCC is on file for 7 of 7 condition(s).

### 5.1 Condition caveats (3 condition(s), 3 distinct caveat(s))

Grouped by identical text: a caveat written once for a family of sibling cells is reproduced once, with every cell it applies to named. Nothing is elided.

- `f35prop-f35vf-4of10-era2b`
  GS Era-2 verified board cell (planning/gs-era2-verified-board-2026-09-08.md, PI frame ruling 2026-09-09): the registered cell f35prop-f35vf-4of10 re-scored with its committed recipe on the Era-2 ∩ B-union frame (era2-b-487); the committed evaluation on full\_evaluation\_bounds.geojson stays the row's record.
- `f35prop-f3vf-4of10-era2b`
  GS Era-2 verified board cell (planning/gs-era2-verified-board-2026-09-08.md, PI frame ruling 2026-09-09): the registered cell f35prop-f3vf-4of10 re-scored with its committed recipe on the Era-2 ∩ B-union frame (era2-b-487); the committed evaluation on full\_evaluation\_bounds.geojson stays the row's record.
- `f3prop-f35vf-6of10-era2b`
  GS Era-2 verified board cell (planning/gs-era2-verified-board-2026-09-08.md, PI frame ruling 2026-09-09): the registered cell f3prop-f35vf-6of10 re-scored with its committed recipe on the Era-2 ∩ B-union frame (era2-b-487); the committed evaluation on full\_evaluation\_bounds.geojson stays the row's record.

### 5.2 Scope overrides (3 condition(s), 1 distinct frame(s))

These conditions are scored on a frame other than the run's nominal scope in § 2 — the 327-vs-487 leakage trap the verifier exists to catch, disclosed per condition:

- `f35prop-f35vf-4of10-era2b`, `f35prop-f3vf-4of10-era2b`, `f3prop-f35vf-6of10-era2b`
  bounds\_path = inputs/vectors/bounds/384/era2\_b\_intersection\_bounds.geojson, calibration\_set\_id = None, n\_calibration\_tiles = None, n\_test\_tiles = 487, test\_set\_id = era2-b-487

### 5.3 Decomposition note

Verbatim from `results/run-conditions.json` — the hand-authored record of how this run was decomposed and what was adjudicated:

> Flash 3.5 2x2x2 at the n=10 grain: one citable condition per registered corner at its best (k, prob\_t) operating point (the settled decomposition pattern). The F3-proposer x F3-verifier corner is NOT duplicated here — it is pv-diag-384::verified-adv-text-min-6of10 (min11, 0.8835), which the tranche reproduced exactly (harness self-validation). The n=5 cells are method-matched first-5 derivations, analysis-internal (results/flash35-2x2/analysis-full.json). The f3prop pool is cross-run (pv-diag-384 text-n10 minimal lineage).

### 5.4 Waived evaluations (6, 4 distinct reason(s))

Scored evaluations under this run that no condition claims, each waived in `results/run-conditions.json` rather than left silent. Grouped by identical reason; where a reason covers more than 12 paths the first 12 are named and the decomposition carries the rest.

- **3 evaluation(s)** — uplift-supplement pairing/gap-fill anchor (planning/uplift-supplement-2026-08-28.md): an input to the supplement's pairing tables, scored on the reference, buffer, and frame of the stratum it pairs with; not a registered condition and not cited by the paper. Waived by PI ruling 2026-09-07 (planning/reference-revision-2026-09-06.md, register-verifier debt).
  - `results/uplift-supplement/verifier-pairing/flash35-pv-2x2__f35prop-f35vf-4of10/evaluation.json`
  - `results/uplift-supplement/verifier-pairing/flash35-pv-2x2__f35prop-f3vf-4of10/evaluation.json`
  - `results/uplift-supplement/verifier-pairing/flash35-pv-2x2__f3prop-f35vf-6of10/evaluation.json`
- **1 evaluation(s)** — GS Era-2 board gate G2 (planning/gs-era2-verified-board-2026-09-08.md): f35prop-f35vf-4of10's committed recipe re-run on its committed frame with a 200-draw bootstrap to prove the evaluator reproduces the committed evaluation; a gate artefact, not a condition.
  - `results/leaderboard/era2/gs-era2-verified-board-2026-09-10/g2/flash35-pv-2x2__f35prop-f35vf-4of10/evaluation.json`
- **1 evaluation(s)** — GS Era-2 board gate G2 (planning/gs-era2-verified-board-2026-09-08.md): f35prop-f3vf-4of10's committed recipe re-run on its committed frame with a 200-draw bootstrap to prove the evaluator reproduces the committed evaluation; a gate artefact, not a condition.
  - `results/leaderboard/era2/gs-era2-verified-board-2026-09-10/g2/flash35-pv-2x2__f35prop-f3vf-4of10/evaluation.json`
- **1 evaluation(s)** — GS Era-2 board gate G2 (planning/gs-era2-verified-board-2026-09-08.md): f3prop-f35vf-6of10's committed recipe re-run on its committed frame with a 200-draw bootstrap to prove the evaluator reproduces the committed evaluation; a gate artefact, not a condition.
  - `results/leaderboard/era2/gs-era2-verified-board-2026-09-10/g2/flash35-pv-2x2__f3prop-f35vf-6of10/evaluation.json`

## 6. Analyses that read this run (4)

A run is linked to an analysis when the analysis's `conditions_compared` names one of this run's conditions. *Cells* is how many of the analysis's compared conditions come from this run, out of its total. *Signed* is the register's `manually_verified_at` stamp.

| Analysis | Cells | Type | Hypotheses | Registration | Paper section | Deviations | Signed | Output |
|---|---|---|---|---|---|---|---|---|
| `flash35-model-roles` | 4 of 5 | leaderboard | `H2` | post-hoc | Results | `E56`, `E62` | 2026-06-12T06:59:01Z | `results/flash35-2x2` |
| `gs-era2-verified-board-2026-09-10` | 3 of 103 | leaderboard | `H2`, `H1` | post-hoc | Results | — | 2026-09-12T06:04:30Z | `results/leaderboard/era2/gs-era2-verified-board-2026-09-10/tiering_20m.json` |
| `uplift-supplement-flatten` | 4 of 441 | diagnostic | — | post-hoc | Appendix | — | 2026-09-10T22:55:40Z | `results/uplift-supplement/conditions.csv` |
| `verifier-uplift-pairing` | 3 of 170 | comparison | `H2` | post-hoc | Appendix | — | 2026-09-12T06:04:30Z | `results/uplift-supplement/verifier-uplift.csv` |

## 7. Findings documents (0)

No findings document on disk is named by an analysis that reads this run: a findings write-up for this run is **not supplied** from the register. § 6's `output_path` column gives each analysis's artefact directory.

## 8. Protocol errata

### 8.1 Registered as deviations (2)

Listed in the `deviations` field of an analysis that reads this run:

- **E56** — Verifier probability-threshold operating points are in-sample (test-set-selected), not calibrated
- **E62** — Three unregistered proposer-verifier extension studies (`flash35-pv-2x2`, `pv-diag-256`, `verifier-robustness`) and four unregistered verifier-parameter levels — additional exploratory extensions of the registered PV contingency

### 8.2 Mentioning this run (2)

The entry's text names this run id or its directory path. A mention is a pointer to read the entry, not a claim that the erratum is about this run:

- **E71** — `n\_tiles\_processed` manifest column carries two semantics (dispatched vs completed) plus a verifier-row placeholder (GAP-8) — 15 passes with genuine coverage shortfalls, two live conditions carrying dead tiles as artificial false negatives
- **E77** — H15 (cross-model consensus voting) — registered as deferred; gated on H14, which never ran

## 9. Documents and structure in the run directory

| Document class | Filename | Count |
|---|---|---:|
| per-pass/per-run intent | `experiment_intent.md` | 11 |

These classes are in Revision-Policy scope going forward (`docs/methodology/output-directory-standard.md` § "Documents in Revision Policy Scope").

### 9.1 Registered pools

| Proposer pool | Modality | Path within the run directory |
|---|---|---|
| `f3-min-text-1of10` | text | `consensus/f3-min-text-1of10-with-passes.geojson` |
| `flash35-min-text-1of10` | text | `proposer` |

3 registered verifier-pass directory/directories; see `results/run-conditions.json` for the full list.

## 10. Provenance of this report

This report is a projection. Every figure above is read from one of the committed inputs below; nothing is estimated, and a figure that is not on file is written **not supplied** with its reason.

| Field | Value |
|---|---|
| Generator | `scripts/generate_run_reports.py` v1.1.0 |
| Source commit | `736c39c0e` |
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
- `outputs/flash35-pv-2x2/proposer/run_1/detections-detect_brief-text-3.5-flash-2026-06-10.meta.json`

Regenerate and drift-check with:

```bash
python3 scripts/generate_run_reports.py --all --write
python3 scripts/generate_run_reports.py --check
```
