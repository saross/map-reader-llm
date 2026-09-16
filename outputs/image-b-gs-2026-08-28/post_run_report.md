<!-- GENERATED FILE — do not hand-edit. Projected from the registered manifests by scripts/generate_run_reports.py v1.1.0. Hand edits are destroyed on the next regeneration and fail the --check drift guard. -->
# Post-run report — image-b-gs-2026-08-28

> **GENERATED FILE — do not hand-edit.** Projected from the registered manifests by `scripts/generate_run_reports.py` v1.1.0 at source commit `1f6826f5e`. This file carries provenance instead of a hand changelog, per the PI ruling of 2026-09-11 recorded in `docs/methodology/output-directory-standard.md` § "Documents in Revision Policy Scope": a generated document's history is its inputs' and its generator's git history, so "is this current?" is answered by the `--check` drift guard and its tier-1 test, not by a changelog. Regenerate after any manifest rebuild; put before/after notes in the commit message.

**Directory**: `outputs/image-b-gs-2026-08-28` · **Registry status**: active · **Purpose**: Image variant of the leading configuration on the GS corpus: the modality head-to-head under matched everything (vs the committed text-B anchor), plus the first matched MINIMAL-vs-HIGH image thinking pair. Card planning/image-b-gs-2026-08-28.md.

## 1. Identity and registration

| Field | Value |
|---|---|
| Run id | `image-b-gs-2026-08-28` |
| Directory | `outputs/image-b-gs-2026-08-28` |
| Registry status | active |
| Purpose | Image variant of the leading configuration on the GS corpus: the modality head-to-head under matched everything (vs the committed text-B anchor), plus the first matched MINIMAL-vs-HIGH image thinking pair. Card planning/image-b-gs-2026-08-28.md. |
| Run type (derived) | proposer-verifier |
| Primary hypothesis | not supplied |
| Also informs | `H1` |
| Headline condition | image-b-gs-2026-08-28::g384-ov192-image-min-k10-verified-p0.15-k9 |
| Headline rationale | The modality comparison's image side at MINIMAL — the like-for-like cell the paper claim rests on. |
| Historical aliases | — |
| Working-notes Obs | — |
| Registry notes | Image on the leading geometry (card planning/image-b-gs-2026-08-28.md): MINIMAL and HIGH cells, K=10 each on the text-B GS tiling, explicit context caching; pricing probes in probe/ and probe-high/. Registered S143 (Pass 3). |

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

### 3.1 Proposer passes (20)

| Pool | Pass | Model used | Model requested | Modality | Thinking | Temp | Status | Tiles done | Dispatched | Retries |
|---|---:|---|---|---|---|---:|---|---:|---:|---:|
| `g384_ov192_image` | 1 | gemini-3-flash-preview | gemini-3-flash-preview | image | minimal | 0.7 | ok | 1398 | 1398 | 0 |
| `g384_ov192_image` | 2 | gemini-3-flash-preview | gemini-3-flash-preview | image | minimal | 0.7 | ok | 1398 | 1398 | 0 |
| `g384_ov192_image` | 3 | gemini-3-flash-preview | gemini-3-flash-preview | image | minimal | 0.7 | ok | 1398 | 1398 | 0 |
| `g384_ov192_image` | 4 | gemini-3-flash-preview | gemini-3-flash-preview | image | minimal | 0.7 | ok | 1398 | 1398 | 0 |
| `g384_ov192_image` | 5 | gemini-3-flash-preview | gemini-3-flash-preview | image | minimal | 0.7 | ok | 1398 | 1398 | 0 |
| `g384_ov192_image` | 6 | gemini-3-flash-preview | gemini-3-flash-preview | image | minimal | 0.7 | ok | 1398 | 1398 | 0 |
| `g384_ov192_image` | 7 | gemini-3-flash-preview | gemini-3-flash-preview | image | minimal | 0.7 | ok | 1398 | 1398 | 0 |
| `g384_ov192_image` | 8 | gemini-3-flash-preview | gemini-3-flash-preview | image | minimal | 0.7 | ok | 1398 | 1398 | 0 |
| `g384_ov192_image` | 9 | gemini-3-flash-preview | gemini-3-flash-preview | image | minimal | 0.7 | ok | 1398 | 1398 | 0 |
| `g384_ov192_image` | 10 | gemini-3-flash-preview | gemini-3-flash-preview | image | minimal | 0.7 | ok | 1398 | 1398 | 0 |
| `g384_ov192_image_high` | 1 | gemini-3-flash-preview | gemini-3-flash-preview | image | high | 0.7 | ok | 1398 | 1398 | 33 |
| `g384_ov192_image_high` | 2 | gemini-3-flash-preview | gemini-3-flash-preview | image | high | 0.7 | ok | 1398 | 1398 | 27 |
| `g384_ov192_image_high` | 3 | gemini-3-flash-preview | gemini-3-flash-preview | image | high | 0.7 | ok | 1398 | 1398 | 25 |
| `g384_ov192_image_high` | 4 | gemini-3-flash-preview | gemini-3-flash-preview | image | high | 0.7 | ok | 1398 | 1398 | 37 |
| `g384_ov192_image_high` | 5 | gemini-3-flash-preview | gemini-3-flash-preview | image | high | 0.7 | ok | 1398 | 1398 | 35 |
| `g384_ov192_image_high` | 6 | gemini-3-flash-preview | gemini-3-flash-preview | image | high | 0.7 | ok | 1398 | 1398 | 31 |
| `g384_ov192_image_high` | 7 | gemini-3-flash-preview | gemini-3-flash-preview | image | high | 0.7 | ok | 1398 | 1398 | 37 |
| `g384_ov192_image_high` | 8 | gemini-3-flash-preview | gemini-3-flash-preview | image | high | 0.7 | ok | 1398 | 1398 | 22 |
| `g384_ov192_image_high` | 9 | gemini-3-flash-preview | gemini-3-flash-preview | image | high | 0.7 | ok | 1398 | 1398 | 37 |
| `g384_ov192_image_high` | 10 | gemini-3-flash-preview | gemini-3-flash-preview | image | high | 0.7 | ok | 1398 | 1398 | 22 |

### 3.2 Verifier passes (2)

| Pool | Pass | Model used | Modality | Thinking | Temp | Status | Candidates verified | Retries |
|---|---:|---|---|---|---:|---|---:|---:|
| `g384_ov192_image-union-k10-verify` | 1 | gemini-3-flash-preview | text | minimal | 0.0 | ok | 4065 | 20 |
| `g384_ov192_image_high-union-k10-verify` | 1 | gemini-3-flash-preview | text | minimal | 0.0 | ok | 9189 | 30 |

Verifier rows report no tile count by design: verifier pass: operates on candidate crops, not tiles. The verifier meta records candidate ids (cand\_NNNN) in execution\_stats.completed\_items and candidate API items in per\_item\_metadata, so no tile-scale record exists to report. Completed crop count is in n\_candidates\_verified. (E71 Defect 2 / GAP-8, resolved E72 2026-08-02.)

## 4. Token load and recorded cost

| Field | Value |
|---|---|
| Passes on file | 22 |
| Input tokens (billed) | 583,482,408 |
| Input tokens (cached) | 528,695,640 |
| Output tokens | 5,635,181 |
| Thinking tokens | 26,070,604 |
| Total tokens | 615,188,193 |
| Passes with no token record | 0 |
| Sum of recorded `cost_usd` | US$163.4343 over 22 of 22 pass(es) |
| Passes with no `cost_usd` | 0 |
| Summed wall clock | 4.02 h over 22 pass(es) |

> **The recorded cost is NOT this run's cost.** Each `cost_usd` above is the pass meta's own `cost_estimate.total_cost_usd`, lifted verbatim by `scripts/generate_post_run_report.py`. The token-load audit of 2026-06-12 established that those self-reported estimates price at STANDARD rates although the audited runs executed at `--service-tier flex` (half price) and omit thinking tokens although Gemini bills thinking at the output rate (`reports/token-load-audit-2026-06-12.md` § 1, § 2). The sum is reproduced here as the recorded figure and as an input to a reconciliation, not as a total to cite.

No cost audit on file names this run or its directory: an independently audited cost for this run is **not supplied**. The four audits checked are `reports/token-load-audit-2026-06-12.md`, `reports/r7-gaps-deltas-2026-09-11.md`, `reports/k-ladder-phase2-deltas-2026-09-12.md`, `reports/billing-reconciliation-2026-09-11.md`.

## 5. Registered conditions (4)

F1@20 m is the preregistered localisation buffer; F1@50 m is the deployment working buffer. Confidence intervals are those the evaluation recorded (method, iterations and seed per condition in the manifest). `mcc` is tile-level. A cell reading *not supplied* means the metric is absent from the condition's evaluation, not that it is zero; a tile-MCC reading *withheld* means the tile-join invariant REFUSED that condition's per-tile table on this frame, so the tile metrics and the bootstrap intervals were not computed — the condition's whole-frame F1 is unaffected and is reported in full (PI ruling 2026-09-13; the named reason is in the condition's manifest row).

| Condition | Architecture | Aggregation | Passes | Operating point | Detections | F1@20 m [CI] | F1@50 m [CI] | Tile MCC |
|---|---|---|---:|---|---:|---|---|---:|
| `g384-ov192-image-high-k10-verified-p0.20-k8` | proposer-verifier | verified | 10 | k=8/pt=0.2 | 400 | 0.8333 [0.7973, 0.8638] | 0.8696 [0.8388, 0.8948] | 0.7993 |
| `g384-ov192-image-high-k10-verified-p0.20-k8-era2b` | proposer-verifier | verified | 10 | k=8/pt=0.2 | 400 | 0.8263 [0.7896, 0.8575] | 0.8623 [0.8310, 0.8887] | 0.7937 |
| `g384-ov192-image-min-k10-verified-p0.15-k9` | proposer-verifier | verified | 10 | k=9/pt=0.15 | 397 | 0.8412 [0.8011, 0.8720] | 0.8776 [0.8482, 0.9022] | 0.7985 |
| `g384-ov192-image-min-k10-verified-p0.15-k9-era2b` | proposer-verifier | verified | 10 | k=9/pt=0.15 | 397 | 0.8341 [0.7942, 0.8657] | 0.8702 [0.8401, 0.8954] | 0.7927 |

Buffers on file (metres), by how many conditions carry that set:

- 4 condition(s): 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 75, 100, 125, 150

Tile-level MCC is on file for 4 of 4 condition(s).

### 5.1 Condition caveats (4 condition(s), 4 distinct caveat(s))

Grouped by identical text: a caveat written once for a family of sibling cells is reproduced once, with every cell it applies to named. Nothing is elided.

- `g384-ov192-image-high-k10-verified-p0.20-k8-era2b`
  GS Era-2 verified board cell (planning/gs-era2-verified-board-2026-09-08.md, PI frame ruling 2026-09-09): the registered cell g384-ov192-image-high-k10-verified-p0.20-k8 re-scored with its committed recipe on the Era-2 ∩ B-union frame (era2-b-487); the committed evaluation on grid\_common\_bounds.geojson stays the row's record.
- `g384-ov192-image-min-k10-verified-p0.15-k9-era2b`
  GS Era-2 verified board cell (planning/gs-era2-verified-board-2026-09-08.md, PI frame ruling 2026-09-09): the registered cell g384-ov192-image-min-k10-verified-p0.15-k9 re-scored with its committed recipe on the Era-2 ∩ B-union frame (era2-b-487); the committed evaluation on grid\_common\_bounds.geojson stays the row's record.
- `g384-ov192-image-high-k10-verified-p0.20-k8`
  Image-HIGH verified best (F1@20 0.8333; union 9,189, +126% over MINIMAL). HP1 confirmed: the verifier absorbs the thinking dividend (-0.0079 vs MINIMAL, p=0.62, at 2.91x cost).
- `g384-ov192-image-min-k10-verified-p0.15-k9`
  Image-MINIMAL verified best (F1@20 0.8412, tile-MCC 0.7985; union 4,065). Text beats it +0.0549 @20m p=0.0010 with MCC parity — the modality verdict (IP1-IP4 confirmed).

### 5.2 Scope overrides (2 condition(s), 1 distinct frame(s))

These conditions are scored on a frame other than the run's nominal scope in § 2 — the 327-vs-487 leakage trap the verifier exists to catch, disclosed per condition:

- `g384-ov192-image-high-k10-verified-p0.20-k8-era2b`, `g384-ov192-image-min-k10-verified-p0.15-k9-era2b`
  bounds\_path = inputs/vectors/bounds/384/era2\_b\_intersection\_bounds.geojson, calibration\_set\_id = None, n\_calibration\_tiles = None, n\_test\_tiles = 487, test\_set\_id = era2-b-487

### 5.3 Decomposition note

Verbatim from `results/run-conditions.json` — the hand-authored record of how this run was decomposed and what was adjudicated:

> Both cells byte-matched to the committed text-B anchor except the declared bundles (modality; one thinking flag). Predictions IP1-IP5 and HP1-HP5 registered by commit before each launch (card planning/image-b-gs-2026-08-28.md). Findings: results/image-b-gs-2026-08-28/findings.md.

### 5.4 Waived evaluations (6, 3 distinct reason(s))

Scored evaluations under this run that no condition claims, each waived in `results/run-conditions.json` rather than left silent. Grouped by identical reason; where a reason covers more than 12 paths the first 12 are named and the decomposition carries the rest.

- **4 evaluation(s)** — uplift-supplement K=1 anchor (planning/uplift-supplement-2026-08-28.md; scored 5bd514542): an input to the supplement's pairing tables, on the reference of the stratum it pairs with; not a registered condition and not cited by the paper. Waived by PI ruling 2026-09-07 (planning/reference-revision-2026-09-06.md, register-verifier debt).
  - `results/uplift-supplement/k1-gapfill/image-b-gs-2026-08-28__g384-ov192-image-high-k10-verified-p0_20-k8/evaluation.json`
  - `results/uplift-supplement/k1-gapfill/image-b-gs-2026-08-28__g384-ov192-image-min-k10-verified-p0_15-k9/evaluation.json`
  - `results/uplift-supplement/verifier-pairing/image-b-gs-2026-08-28__g384-ov192-image-high-k10-verified-p0_20-k8/evaluation.json`
  - `results/uplift-supplement/verifier-pairing/image-b-gs-2026-08-28__g384-ov192-image-min-k10-verified-p0_15-k9/evaluation.json`
- **1 evaluation(s)** — GS Era-2 board gate G2 (planning/gs-era2-verified-board-2026-09-08.md): g384-ov192-image-high-k10-verified-p0.20-k8's committed recipe re-run on its committed frame with a 200-draw bootstrap to prove the evaluator reproduces the committed evaluation; a gate artefact, not a condition.
  - `results/leaderboard/era2/gs-era2-verified-board-2026-09-10/g2/image-b-gs-2026-08-28__g384-ov192-image-high-k10-verified-p0_20-k8/evaluation.json`
- **1 evaluation(s)** — GS Era-2 board gate G2 (planning/gs-era2-verified-board-2026-09-08.md): g384-ov192-image-min-k10-verified-p0.15-k9's committed recipe re-run on its committed frame with a 200-draw bootstrap to prove the evaluator reproduces the committed evaluation; a gate artefact, not a condition.
  - `results/leaderboard/era2/gs-era2-verified-board-2026-09-10/g2/image-b-gs-2026-08-28__g384-ov192-image-min-k10-verified-p0_15-k9/evaluation.json`

## 6. Analyses that read this run (7)

A run is linked to an analysis when the analysis's `conditions_compared` names one of this run's conditions. *Cells* is how many of the analysis's compared conditions come from this run, out of its total. *Signed* is the register's `manually_verified_at` stamp.

| Analysis | Cells | Type | Hypotheses | Registration | Paper section | Deviations | Signed | Output |
|---|---|---|---|---|---|---|---|---|
| `gemini37-image-gs-2026-09-01` | 1 of 6 | comparison | `H1` | post-hoc | Results | — | 2026-09-12T09:03:09Z | `results/gemini37-image-gs-2026-09-01` |
| `gs-era2-verified-board-2026-09-10` | 2 of 103 | leaderboard | `H2`, `H1` | post-hoc | Results | — | 2026-09-16T02:58:00Z | `results/leaderboard/era2/gs-era2-verified-board-2026-09-10/tiering_20m.json` |
| `image-b-modality-2026-08-28` | 1 of 2 | comparison | `H1` | registered-exploratory | Results | — | 2026-08-28T12:43:12Z | `results/image-b-gs-2026-08-28/analysis.json` |
| `image-b-thinking-pair-2026-08-28` | 2 of 2 | comparison | `H1` | registered-exploratory | Results | — | 2026-08-28T12:43:12Z | `results/image-b-gs-2026-08-28/high/pair_verdicts.json` |
| `null-exemplar-sensitivity-2026-09-13` | 2 of 235 | comparison | — | post-hoc | Appendix | — | 2026-09-16T06:43:40Z | `results/null-exemplar-sensitivity-2026-09-13/findings.md` |
| `uplift-supplement-flatten` | 2 of 441 | diagnostic | — | post-hoc | Appendix | — | 2026-09-10T22:55:40Z | `results/uplift-supplement/conditions.csv` |
| `verifier-uplift-pairing` | 2 of 170 | comparison | `H2` | post-hoc | Appendix | — | 2026-09-12T06:04:30Z | `results/uplift-supplement/verifier-uplift.csv` |

## 7. Findings documents (2)

| Document | Named by |
|---|---|
| `results/image-b-gs-2026-08-28/findings.md` | `image-b-modality-2026-08-28` |
| `results/null-exemplar-sensitivity-2026-09-13/findings.md` | `null-exemplar-sensitivity-2026-09-13` |

## 8. Protocol errata

No erratum in `docs/methodology/preregistration/protocol-errata.md` is registered against an analysis of this run, and none mentions the run or its directory.

## 9. Documents and structure in the run directory

| Document class | Filename | Count |
|---|---|---:|
| per-pass/per-run intent | `experiment_intent.md` | 32 |

These classes are in Revision-Policy scope going forward (`docs/methodology/output-directory-standard.md` § "Documents in Revision Policy Scope").

### 9.1 Registered pools

| Proposer pool | Modality | Path within the run directory |
|---|---|---|
| `g384_ov192_image` | image | `g384_ov192_image` |
| `g384_ov192_image_high` | image | `g384_ov192_image_high` |

2 registered verifier-pass directory/directories; see `results/run-conditions.json` for the full list.

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
- `outputs/grid-2026-08-18/scoring/bounds/grid_common_bounds.geojson`

Regenerate and drift-check with:

```bash
python3 scripts/generate_run_reports.py --all --write
python3 scripts/generate_run_reports.py --check
```
