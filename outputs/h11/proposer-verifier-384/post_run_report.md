<!-- GENERATED FILE — do not hand-edit. Projected from the registered manifests by scripts/generate_run_reports.py v1.1.0. Hand edits are destroyed on the next regeneration and fail the --check drift guard. -->
# Post-run report — proposer-verifier-384

> **GENERATED FILE — do not hand-edit.** Projected from the registered manifests by `scripts/generate_run_reports.py` v1.1.0 at source commit `11e576e9c`. This file carries provenance instead of a hand changelog, per the PI ruling of 2026-09-11 recorded in `docs/methodology/output-directory-standard.md` § "Documents in Revision Policy Scope": a generated document's history is its inputs' and its generator's git history, so "is this current?" is answered by the `--check` drift guard and its tier-1 test, not by a changelog. Regenerate after any manifest rebuild; put before/after notes in the commit message.

**Directory**: `outputs/h11/proposer-verifier-384` · **Registry status**: active · **Purpose**: not supplied

## 1. Identity and registration

| Field | Value |
|---|---|
| Run id | `proposer-verifier-384` |
| Directory | `outputs/h11/proposer-verifier-384` |
| Registry status | active |
| Purpose | not supplied |
| Run type (derived) | proposer-verifier |
| Primary hypothesis | H11 |
| Also informs | `pv-strategy` |
| Headline condition | not supplied |
| Headline rationale | not supplied |
| Historical aliases | `Era 2` |
| Working-notes Obs | — |
| Registry notes | H11 (proposer-verifier, 384px). |

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

### 3.2 Verifier passes (8)

| Pool | Pass | Model used | Modality | Thinking | Temp | Status | Candidates verified | Retries |
|---|---:|---|---|---|---:|---|---:|---:|
| `verified-adversarial-image` | 1 | gemini-3-flash-preview | image | minimal | 0.0 | ok | 572 | 0 |
| `verified-adversarial-text` | 1 | gemini-3-flash-preview | text | minimal | 0.0 | ok | 572 | 0 |
| `verified-brief-image` | 1 | gemini-3-flash-preview | image | minimal | 0.0 | ok | 572 | 0 |
| `verified-brief-text` | 1 | gemini-3-flash-preview | text | minimal | 0.0 | ok | 572 | 0 |
| `verified-cascade-adversarial-checklist` | 1 | gemini-3-flash-preview | text | minimal | 0.0 | ok | 271 | 0 |
| `verified-cascade-checklist-adversarial` | 1 | gemini-3-flash-preview | image | minimal | 0.0 | ok | 326 | 0 |
| `verified-checklist-image` | 1 | gemini-3-flash-preview | image | minimal | 0.0 | ok | 572 | 0 |
| `verified-checklist-text` | 1 | gemini-3-flash-preview | text | minimal | 0.0 | ok | 572 | 0 |

Verifier rows report no tile count by design: verifier pass: operates on candidate crops, not tiles. The verifier meta records candidate ids (cand\_NNNN) in execution\_stats.completed\_items and candidate API items in per\_item\_metadata, so no tile-scale record exists to report. Completed crop count is in n\_candidates\_verified. (E71 Defect 2 / GAP-8, resolved E72 2026-08-02.)

## 4. Token load and recorded cost

| Field | Value |
|---|---|
| Passes on file | 8 |
| Input tokens (billed) | 27,066,363 |
| Input tokens (cached) | 0 |
| Output tokens | 563,081 |
| Thinking tokens | 0 |
| Total tokens | 27,629,444 |
| Passes with no token record | 0 |
| Sum of recorded `cost_usd` | US$2.9319 over 8 of 8 pass(es) |
| Passes with no `cost_usd` | 0 |
| Summed wall clock | 0.55 h over 8 pass(es) |

> **The recorded cost is NOT this run's cost.** Each `cost_usd` above is the pass meta's own `cost_estimate.total_cost_usd`, lifted verbatim by `scripts/generate_post_run_report.py`. The token-load audit of 2026-06-12 established that those self-reported estimates price at STANDARD rates although the audited runs executed at `--service-tier flex` (half price) and omit thinking tokens although Gemini bills thinking at the output rate (`reports/token-load-audit-2026-06-12.md` § 1, § 2). The sum is reproduced here as the recorded figure and as an input to a reconciliation, not as a total to cite.

No cost audit on file names this run or its directory: an independently audited cost for this run is **not supplied**. The four audits checked are `reports/token-load-audit-2026-06-12.md`, `reports/r7-gaps-deltas-2026-09-11.md`, `reports/k-ladder-phase2-deltas-2026-09-12.md`, `reports/billing-reconciliation-2026-09-11.md`.

## 5. Registered conditions (16)

F1@20 m is the preregistered localisation buffer; F1@50 m is the deployment working buffer. Confidence intervals are those the evaluation recorded (method, iterations and seed per condition in the manifest). `mcc` is tile-level. A cell reading *not supplied* means the metric is absent from the condition's evaluation, not that it is zero; a tile-MCC reading *withheld* means the tile-join invariant REFUSED that condition's per-tile table on this frame, so the tile metrics and the bootstrap intervals were not computed — the condition's whole-frame F1 is unaffected and is reported in full (PI ruling 2026-09-13; the named reason is in the condition's manifest row).

| Condition | Architecture | Aggregation | Passes | Operating point | Detections | F1@20 m [CI] | F1@50 m [CI] | Tile MCC |
|---|---|---|---:|---|---:|---|---|---:|
| `verified-adversarial-image` | proposer-verifier | verified | 1 | — | 261 | 0.4943 [0.4153, 0.5678] | 0.5115 [0.4332, 0.5831] | 0.4160 |
| `verified-adversarial-image-era2b` | proposer-verifier | verified | 1 | — | 261 | 0.4943 [0.4153, 0.5678] | 0.5115 [0.4332, 0.5831] | 0.4160 |
| `verified-adversarial-text` | proposer-verifier | verified | 1 | — | 215 | 0.4708 [0.3925, 0.5487] | 0.4831 [0.4056, 0.5599] | 0.4313 |
| `verified-adversarial-text-era2b` | proposer-verifier | verified | 1 | — | 215 | 0.4708 [0.3925, 0.5487] | 0.4831 [0.4056, 0.5599] | 0.4313 |
| `verified-brief-image` | proposer-verifier | verified | 1 | — | 326 | 0.5204 [0.4430, 0.5934] | 0.5361 [0.4591, 0.6084] | 0.3402 |
| `verified-brief-image-era2b` | proposer-verifier | verified | 1 | — | 326 | 0.5204 [0.4430, 0.5934] | 0.5361 [0.4591, 0.6084] | 0.3402 |
| `verified-brief-text` | proposer-verifier | verified | 1 | — | 269 | 0.5142 [0.4388, 0.5900] | 0.5284 [0.4530, 0.6040] | 0.3953 |
| `verified-brief-text-era2b` | proposer-verifier | verified | 1 | — | 269 | 0.5142 [0.4388, 0.5900] | 0.5284 [0.4530, 0.6040] | 0.3953 |
| `verified-cascade-adversarial-checklist` | proposer-verifier | verified | 1 | — | 264 | 0.5036 [0.4248, 0.5772] | 0.5207 [0.4422, 0.5925] | 0.4313 |
| `verified-cascade-adversarial-checklist-era2b` | proposer-verifier | verified | 1 | — | 264 | 0.5036 [0.4248, 0.5772] | 0.5207 [0.4422, 0.5925] | 0.4313 |
| `verified-cascade-checklist-adversarial` | proposer-verifier | verified | 1 | — | 260 | 0.4950 [0.4162, 0.5687] | 0.5122 [0.4342, 0.5842] | 0.4121 |
| `verified-cascade-checklist-adversarial-era2b` | proposer-verifier | verified | 1 | — | 260 | 0.4950 [0.4162, 0.5687] | 0.5122 [0.4342, 0.5842] | 0.4121 |
| `verified-checklist-image` | proposer-verifier | verified | 1 | — | 326 | 0.5309 [0.4505, 0.6060] | 0.5466 [0.4667, 0.6201] | 0.3873 |
| `verified-checklist-image-era2b` | proposer-verifier | verified | 1 | — | 326 | 0.5309 [0.4505, 0.6060] | 0.5466 [0.4667, 0.6201] | 0.3873 |
| `verified-checklist-text` | proposer-verifier | verified | 1 | — | 336 | 0.5214 [0.4443, 0.5954] | 0.5370 [0.4596, 0.6099] | 0.3154 |
| `verified-checklist-text-era2b` | proposer-verifier | verified | 1 | — | 336 | 0.5214 [0.4443, 0.5954] | 0.5370 [0.4596, 0.6099] | 0.3154 |

Buffers on file (metres), by how many conditions carry that set:

- 16 condition(s): 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 75, 100, 125, 150

Tile-level MCC is on file for 16 of 16 condition(s).

### 5.1 Condition caveats (8 condition(s), 8 distinct caveat(s))

Grouped by identical text: a caveat written once for a family of sibling cells is reproduced once, with every cell it applies to named. Nothing is elided.

- `verified-adversarial-image-era2b`
  GS Era-2 verified board cell (planning/gs-era2-verified-board-2026-09-08.md, PI frame ruling 2026-09-09): the registered cell verified-adversarial-image re-scored with its committed recipe on the Era-2 ∩ B-union frame (era2-b-487); the committed evaluation on full\_evaluation\_bounds.geojson stays the row's record.
- `verified-adversarial-text-era2b`
  GS Era-2 verified board cell (planning/gs-era2-verified-board-2026-09-08.md, PI frame ruling 2026-09-09): the registered cell verified-adversarial-text re-scored with its committed recipe on the Era-2 ∩ B-union frame (era2-b-487); the committed evaluation on full\_evaluation\_bounds.geojson stays the row's record.
- `verified-brief-image-era2b`
  GS Era-2 verified board cell (planning/gs-era2-verified-board-2026-09-08.md, PI frame ruling 2026-09-09): the registered cell verified-brief-image re-scored with its committed recipe on the Era-2 ∩ B-union frame (era2-b-487); the committed evaluation on full\_evaluation\_bounds.geojson stays the row's record.
- `verified-brief-text-era2b`
  GS Era-2 verified board cell (planning/gs-era2-verified-board-2026-09-08.md, PI frame ruling 2026-09-09): the registered cell verified-brief-text re-scored with its committed recipe on the Era-2 ∩ B-union frame (era2-b-487); the committed evaluation on full\_evaluation\_bounds.geojson stays the row's record.
- `verified-cascade-adversarial-checklist-era2b`
  GS Era-2 verified board cell (planning/gs-era2-verified-board-2026-09-08.md, PI frame ruling 2026-09-09): the registered cell verified-cascade-adversarial-checklist re-scored with its committed recipe on the Era-2 ∩ B-union frame (era2-b-487); the committed evaluation on full\_evaluation\_bounds.geojson stays the row's record.
- `verified-cascade-checklist-adversarial-era2b`
  GS Era-2 verified board cell (planning/gs-era2-verified-board-2026-09-08.md, PI frame ruling 2026-09-09): the registered cell verified-cascade-checklist-adversarial re-scored with its committed recipe on the Era-2 ∩ B-union frame (era2-b-487); the committed evaluation on full\_evaluation\_bounds.geojson stays the row's record.
- `verified-checklist-image-era2b`
  GS Era-2 verified board cell (planning/gs-era2-verified-board-2026-09-08.md, PI frame ruling 2026-09-09): the registered cell verified-checklist-image re-scored with its committed recipe on the Era-2 ∩ B-union frame (era2-b-487); the committed evaluation on full\_evaluation\_bounds.geojson stays the row's record.
- `verified-checklist-text-era2b`
  GS Era-2 verified board cell (planning/gs-era2-verified-board-2026-09-08.md, PI frame ruling 2026-09-09): the registered cell verified-checklist-text re-scored with its committed recipe on the Era-2 ∩ B-union frame (era2-b-487); the committed evaluation on full\_evaluation\_bounds.geojson stays the row's record.

### 5.2 Scope overrides (8 condition(s), 1 distinct frame(s))

These conditions are scored on a frame other than the run's nominal scope in § 2 — the 327-vs-487 leakage trap the verifier exists to catch, disclosed per condition:

- `verified-adversarial-image-era2b`, `verified-adversarial-text-era2b`, `verified-brief-image-era2b`, `verified-brief-text-era2b`, `verified-cascade-adversarial-checklist-era2b`, `verified-cascade-checklist-adversarial-era2b`, `verified-checklist-image-era2b`, `verified-checklist-text-era2b`
  bounds\_path = inputs/vectors/bounds/384/era2\_b\_intersection\_bounds.geojson, calibration\_set\_id = None, n\_calibration\_tiles = None, n\_test\_tiles = 487, test\_set\_id = era2-b-487

### 5.3 Decomposition note

Verbatim from `results/run-conditions.json` — the hand-authored record of how this run was decomposed and what was adjudicated:

> Batch A residual (H11 + pv-strategy). Verifier-strategy matrix over ONE shared proposer pool (detect\_brief-text, flash, single pass, 572 candidates at era-2-487). 8 canonical verified conditions = adversarial/brief/checklist x text/image (6) + 2 cascade orderings, each scored at its verifier-accepted operating point (Session 100, user-confirmed grain). proposer\_pools intentionally EMPTY: the on-disk proposer meta (proposer/detections-detect\_brief-text-3-flash-2026-03-15.meta.json) is a degenerate stub (items\_processed=1, items\_failed=1, 1 tile) although the geojson holds 572 features, so no faithful proposer PASS can be extracted; conditions reference the pool by string -&gt; benign pool-unresolved WARN (pv-diag-384 precedent). The 8 verifier\_passes are real sidecar metas (verified-&lt;strategy&gt;.meta.json, 572 items, 0 failures). The v2 / v1-prompt replicates (identical T=0.0 config re-runs, ~10h apart) and the n=572 pre-verifier 'full' scorings are deliberately excluded; they register in \_ignored\_evals at the deferred 3b close-out sweep. Cascade instruction\_file = the final stage the single sidecar meta records (stage 1 not separately captured). | Pool annotation (2026-09-13, S153 Batch 1 item 2): the run's single proposer pass was written straight into proposer/ with no run\_N directory, so proposer\_pools is empty and the conditions name the pool by prompt string. source\_run records this run as the pool's home (pv-512 / pv-256 precedent). No metric, eval or detection changed.

### 5.4 Waived evaluations (36, 10 distinct reason(s))

Scored evaluations under this run that no condition claims, each waived in `results/run-conditions.json` rather than left silent. Grouped by identical reason; where a reason covers more than 12 paths the first 12 are named and the decomposition carries the rest.

- **20 evaluation(s)** — not supplied — a bare-string entry, written before the waiver register carried reasons
  - `results/rescore-2026-05-31/proposer-verifier-384/verified-adversarial-image-v2-accepted/evaluation.json`
  - `results/rescore-2026-05-31/proposer-verifier-384/verified-adversarial-image-v2/evaluation.json`
  - `results/rescore-2026-05-31/proposer-verifier-384/verified-adversarial-image/evaluation.json`
  - `results/rescore-2026-05-31/proposer-verifier-384/verified-adversarial-text-v2-accepted/evaluation.json`
  - `results/rescore-2026-05-31/proposer-verifier-384/verified-adversarial-text-v2/evaluation.json`
  - `results/rescore-2026-05-31/proposer-verifier-384/verified-adversarial-text/evaluation.json`
  - `results/rescore-2026-05-31/proposer-verifier-384/verified-brief-image-v2-accepted/evaluation.json`
  - `results/rescore-2026-05-31/proposer-verifier-384/verified-brief-image-v2/evaluation.json`
  - `results/rescore-2026-05-31/proposer-verifier-384/verified-brief-image/evaluation.json`
  - `results/rescore-2026-05-31/proposer-verifier-384/verified-brief-text-v2-accepted/evaluation.json`
  - `results/rescore-2026-05-31/proposer-verifier-384/verified-brief-text-v2/evaluation.json`
  - `results/rescore-2026-05-31/proposer-verifier-384/verified-brief-text/evaluation.json`
  - … and 8 more under the same waiver (full list in `results/run-conditions.json`, this run's `_ignored_evals`)
- **8 evaluation(s)** — uplift-supplement pairing/gap-fill anchor (planning/uplift-supplement-2026-08-28.md): an input to the supplement's pairing tables, scored on the reference, buffer, and frame of the stratum it pairs with; not a registered condition and not cited by the paper. Waived by PI ruling 2026-09-07 (planning/reference-revision-2026-09-06.md, register-verifier debt).
  - `results/uplift-supplement/verifier-pairing/proposer-verifier-384__verified-adversarial-image/evaluation.json`
  - `results/uplift-supplement/verifier-pairing/proposer-verifier-384__verified-adversarial-text/evaluation.json`
  - `results/uplift-supplement/verifier-pairing/proposer-verifier-384__verified-brief-image/evaluation.json`
  - `results/uplift-supplement/verifier-pairing/proposer-verifier-384__verified-brief-text/evaluation.json`
  - `results/uplift-supplement/verifier-pairing/proposer-verifier-384__verified-cascade-adversarial-checklist/evaluation.json`
  - `results/uplift-supplement/verifier-pairing/proposer-verifier-384__verified-cascade-checklist-adversarial/evaluation.json`
  - `results/uplift-supplement/verifier-pairing/proposer-verifier-384__verified-checklist-image/evaluation.json`
  - `results/uplift-supplement/verifier-pairing/proposer-verifier-384__verified-checklist-text/evaluation.json`
- **1 evaluation(s)** — GS Era-2 board gate G2 (planning/gs-era2-verified-board-2026-09-08.md): verified-adversarial-image's committed recipe re-run on its committed frame with a 200-draw bootstrap to prove the evaluator reproduces the committed evaluation; a gate artefact, not a condition.
  - `results/leaderboard/era2/gs-era2-verified-board-2026-09-10/g2/proposer-verifier-384__verified-adversarial-image/evaluation.json`
- **1 evaluation(s)** — GS Era-2 board gate G2 (planning/gs-era2-verified-board-2026-09-08.md): verified-adversarial-text's committed recipe re-run on its committed frame with a 200-draw bootstrap to prove the evaluator reproduces the committed evaluation; a gate artefact, not a condition.
  - `results/leaderboard/era2/gs-era2-verified-board-2026-09-10/g2/proposer-verifier-384__verified-adversarial-text/evaluation.json`
- **1 evaluation(s)** — GS Era-2 board gate G2 (planning/gs-era2-verified-board-2026-09-08.md): verified-brief-image's committed recipe re-run on its committed frame with a 200-draw bootstrap to prove the evaluator reproduces the committed evaluation; a gate artefact, not a condition.
  - `results/leaderboard/era2/gs-era2-verified-board-2026-09-10/g2/proposer-verifier-384__verified-brief-image/evaluation.json`
- **1 evaluation(s)** — GS Era-2 board gate G2 (planning/gs-era2-verified-board-2026-09-08.md): verified-brief-text's committed recipe re-run on its committed frame with a 200-draw bootstrap to prove the evaluator reproduces the committed evaluation; a gate artefact, not a condition.
  - `results/leaderboard/era2/gs-era2-verified-board-2026-09-10/g2/proposer-verifier-384__verified-brief-text/evaluation.json`
- **1 evaluation(s)** — GS Era-2 board gate G2 (planning/gs-era2-verified-board-2026-09-08.md): verified-cascade-adversarial-checklist's committed recipe re-run on its committed frame with a 200-draw bootstrap to prove the evaluator reproduces the committed evaluation; a gate artefact, not a condition.
  - `results/leaderboard/era2/gs-era2-verified-board-2026-09-10/g2/proposer-verifier-384__verified-cascade-adversarial-checklist/evaluation.json`
- **1 evaluation(s)** — GS Era-2 board gate G2 (planning/gs-era2-verified-board-2026-09-08.md): verified-cascade-checklist-adversarial's committed recipe re-run on its committed frame with a 200-draw bootstrap to prove the evaluator reproduces the committed evaluation; a gate artefact, not a condition.
  - `results/leaderboard/era2/gs-era2-verified-board-2026-09-10/g2/proposer-verifier-384__verified-cascade-checklist-adversarial/evaluation.json`
- **1 evaluation(s)** — GS Era-2 board gate G2 (planning/gs-era2-verified-board-2026-09-08.md): verified-checklist-image's committed recipe re-run on its committed frame with a 200-draw bootstrap to prove the evaluator reproduces the committed evaluation; a gate artefact, not a condition.
  - `results/leaderboard/era2/gs-era2-verified-board-2026-09-10/g2/proposer-verifier-384__verified-checklist-image/evaluation.json`
- **1 evaluation(s)** — GS Era-2 board gate G2 (planning/gs-era2-verified-board-2026-09-08.md): verified-checklist-text's committed recipe re-run on its committed frame with a 200-draw bootstrap to prove the evaluator reproduces the committed evaluation; a gate artefact, not a condition.
  - `results/leaderboard/era2/gs-era2-verified-board-2026-09-10/g2/proposer-verifier-384__verified-checklist-text/evaluation.json`

## 6. Analyses that read this run (4)

A run is linked to an analysis when the analysis's `conditions_compared` names one of this run's conditions. *Cells* is how many of the analysis's compared conditions come from this run, out of its total. *Signed* is the register's `manually_verified_at` stamp.

| Analysis | Cells | Type | Hypotheses | Registration | Paper section | Deviations | Signed | Output |
|---|---|---|---|---|---|---|---|---|
| `gs-era2-verified-board-2026-09-10` | 8 of 103 | leaderboard | `H2`, `H1` | post-hoc | Results | — | 2026-09-16T02:58:00Z | `results/leaderboard/era2/gs-era2-verified-board-2026-09-10/tiering_20m.json` |
| `null-exemplar-sensitivity-2026-09-13` | 8 of 235 | comparison | — | post-hoc | Appendix | — | 2026-09-16T06:43:40Z | `results/null-exemplar-sensitivity-2026-09-13/findings.md` |
| `uplift-supplement-flatten` | 8 of 441 | diagnostic | — | post-hoc | Appendix | — | 2026-09-10T22:55:40Z | `results/uplift-supplement/conditions.csv` |
| `verifier-uplift-pairing` | 8 of 170 | comparison | `H2` | post-hoc | Appendix | — | 2026-09-12T06:04:30Z | `results/uplift-supplement/verifier-uplift.csv` |

## 7. Findings documents (1)

| Document | Named by |
|---|---|
| `results/null-exemplar-sensitivity-2026-09-13/findings.md` | `null-exemplar-sensitivity-2026-09-13` |

## 8. Protocol errata

### 8.2 Mentioning this run (2)

The entry's text names this run id or its directory path. A mention is a pointer to read the entry, not a claim that the erratum is about this run:

- **E65** — Registered verifier prompt `verify\_brief.md` edited post-lodgement (commit `5e7601d77`) — the one prompt-divergence commit with no contemporaneous erratum
- **E88** — Modality — a preregistered factor — was assigned by a substring test on the condition label in four scripts; eight conditions and one pool were mislabelled, and two registered outcomes quote an image-group range that moves

## 9. Documents and structure in the run directory

No `experiment_intent.md`, `evaluation.md`, `pre_launch_audit.md` or retrospective report under this directory.

### 9.1 Registered pools

8 registered verifier-pass directory/directories; see `results/run-conditions.json` for the full list.

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
- `inputs/vectors/bounds/384/full_evaluation_bounds.geojson`
- `outputs/h11/proposer-verifier-384/proposer/detections-detect_brief-text-3-flash-2026-03-15.meta.json`

Regenerate and drift-check with:

```bash
python3 scripts/generate_run_reports.py --all --write
python3 scripts/generate_run_reports.py --check
```
