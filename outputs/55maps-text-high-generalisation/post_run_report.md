<!-- GENERATED FILE — do not hand-edit. Projected from the registered manifests by scripts/generate_run_reports.py v1.1.0. Hand edits are destroyed on the next regeneration and fail the --check drift guard. -->
# Post-run report — 55maps-text-high-generalisation

> **GENERATED FILE — do not hand-edit.** Projected from the registered manifests by `scripts/generate_run_reports.py` v1.1.0 at source commit `5570447b9`. This file carries provenance instead of a hand changelog, per the PI ruling of 2026-09-11 recorded in `docs/methodology/output-directory-standard.md` § "Documents in Revision Policy Scope": a generated document's history is its inputs' and its generator's git history, so "is this current?" is answered by the `--check` drift guard and its tier-1 test, not by a changelog. Regenerate after any manifest rebuild; put before/after notes in the commit message.

**Directory**: `outputs/55maps-text-high-generalisation` · **Registry status**: active · **Purpose**: 55-map generalisation: text HIGH

## 1. Identity and registration

| Field | Value |
|---|---|
| Run id | `55maps-text-high-generalisation` |
| Directory | `outputs/55maps-text-high-generalisation` |
| Registry status | active |
| Purpose | 55-map generalisation: text HIGH |
| Run type (derived) | proposer-verifier |
| Primary hypothesis | not supplied |
| Also informs | — |
| Headline condition | not supplied |
| Headline rationale | not supplied |
| Historical aliases | `55-map generalisation` |
| Working-notes Obs | — |
| Registry notes | Generalisation programme (text, HIGH thinking). |

## 2. Scope and evaluation frame

| Field | Value |
|---|---|
| Tile size (px) | 384 |
| Corpus | 55-map |
| Ground-truth reference | student |
| Test set id | 55maps-8541 |
| Test tiles | 8541 |
| Bounds | `inputs/vectors/bounds/384/55maps_evaluation_bounds.geojson` |
| Calibration set id | not supplied |
| Calibration tiles | not supplied |

## 3. Execution — passes on file

### 3.1 Proposer passes (5)

| Pool | Pass | Model used | Model requested | Modality | Thinking | Temp | Status | Tiles done | Dispatched | Retries |
|---|---:|---|---|---|---|---:|---|---:|---:|---:|
| `detect_brief-text` | 1 | gemini-3-flash-preview | gemini-3-flash-preview | text | high | 0.7 | ok | 8541 | 8541 | 1266 |
| `detect_brief-text` | 2 | gemini-3-flash-preview | gemini-3-flash-preview | text | high | 0.7 | ok | 8541 | 8541 | 1196 |
| `detect_brief-text` | 3 | gemini-3-flash-preview | gemini-3-flash-preview | text | high | 0.7 | ok | 8541 | 8541 | 1238 |
| `detect_brief-text` | 4 | gemini-3-flash-preview | gemini-3-flash-preview | text | high | 0.7 | ok | 8541 | 8541 | 1322 |
| `detect_brief-text` | 5 | gemini-3-flash-preview | gemini-3-flash-preview | text | high | 0.7 | ok | 8541 | 8541 | 1241 |

### 3.2 Verifier passes (1)

| Pool | Pass | Model used | Modality | Thinking | Temp | Status | Candidates verified | Retries |
|---|---:|---|---|---|---:|---|---:|---:|
| `verified` | 1 | gemini-3-flash-preview | text | minimal | 0.0 | ok | 74 | 0 |

Verifier rows report no tile count by design: verifier pass: operates on candidate crops, not tiles. The verifier meta records candidate ids (cand\_NNNN) in execution\_stats.completed\_items and candidate API items in per\_item\_metadata, so no tile-scale record exists to report. Completed crop count is in n\_candidates\_verified. (E71 Defect 2 / GAP-8, resolved E72 2026-08-02.)

## 4. Token load and recorded cost

| Field | Value |
|---|---|
| Passes on file | 6 |
| Input tokens (billed) | 128,658,748 |
| Input tokens (cached) | 0 |
| Output tokens | 16,579,028 |
| Thinking tokens | 230,497,393 |
| Total tokens | 375,735,169 |
| Passes with no token record | 0 |
| Sum of recorded `cost_usd` | US$114.0665 over 6 of 6 pass(es) |
| Passes with no `cost_usd` | 0 |
| Summed wall clock | 5.36 h over 6 pass(es) |

> **Audited: the token figures above are inflated by a measured factor.** `reports/token-load-audit-2026-06-12.md` § 3.2 recomputed this run's load from `per_item_metadata` and found its `usage_stats` block — which is exactly where the manifest takes a pass's `tokens` from (`_tokens_from_usage`) — **2.0× inflated (factors 2.003–2.016 across axes)**; its `cost_manifest.json` is **2.0× inflated**. The trustworthy source is `per_item_metadata`. Audited clean figures, quoted from § 3.2: 5 passes; clean flex cost US$40.19/pass (range US$39.92–40.45), of which thinking is ~US$34.51; clean per pass input 12,828,582, output mean 1,647,744, thinking mean 23,005,025 (2,693/tile). No run total is derived here: the audit's pass count and this manifest's need not agree, so multiplying would manufacture a figure no file carries.
>
> **The recorded cost is NOT this run's cost.** Each `cost_usd` above is the pass meta's own `cost_estimate.total_cost_usd`, lifted verbatim by `scripts/generate_post_run_report.py`. The token-load audit of 2026-06-12 established that those self-reported estimates price at STANDARD rates although the audited runs executed at `--service-tier flex` (half price) and omit thinking tokens although Gemini bills thinking at the output rate (`reports/token-load-audit-2026-06-12.md` § 1, § 2). The sum is reproduced here as the recorded figure and as an input to a reconciliation, not as a total to cite.

Audit and reconciliation reports whose text names this run or its directory — consult these for audited figures; a mention is a pointer, not a claim that the report audits this run in full:

- `reports/token-load-audit-2026-06-12.md`

## 5. Registered conditions (7)

F1@20 m is the preregistered localisation buffer; F1@50 m is the deployment working buffer. Confidence intervals are those the evaluation recorded (method, iterations and seed per condition in the manifest). `mcc` is tile-level. A cell reading *not supplied* means the metric is absent from the condition's evaluation, not that it is zero; a tile-MCC reading *withheld* means the tile-join invariant REFUSED that condition's per-tile table on this frame, so the tile metrics and the bootstrap intervals were not computed — the condition's whole-frame F1 is unaffected and is reported in full (PI ruling 2026-09-13; the named reason is in the condition's manifest row).

| Condition | Architecture | Aggregation | Passes | Operating point | Detections | F1@20 m [CI] | F1@50 m [CI] | Tile MCC |
|---|---|---|---:|---|---:|---|---|---:|
| `verified` | proposer-verifier | verified | 5 | k=4 | 4164 | 0.6260 [0.6113, 0.6408] | 0.7921 [0.7811, 0.8029] | 0.6480 |
| `verified-k3-canonical-gt` | proposer-verifier | verified | 5 | k=3/pt=0.15 | 4786 | 0.6307 [0.6164, 0.6449] | 0.8425 [0.8335, 0.8512] | 0.6796 |
| `verified-k3-r2-gt` | proposer-verifier | verified | 5 | k=3/pt=0.15 | 4786 | 0.6720 [0.6584, 0.6849] | 0.8380 [0.8287, 0.8467] | 0.6792 |
| `verified-k3-standardised-gt` | proposer-verifier | verified | 5 | k=3/pt=0.15 | 4786 | 0.6725 [0.6591, 0.6855] | 0.8387 [0.8297, 0.8475] | 0.6796 |
| `verified-k4-canonical-gt` | proposer-verifier | verified | 5 | k=4 | 4164 | 0.6260 [0.6113, 0.6408] | 0.8152 [0.8051, 0.8251] | 0.6666 |
| `verified-k4-r2-gt` | proposer-verifier | verified | 5 | k=4 | 4164 | 0.6652 [0.6512, 0.6789] | 0.8162 [0.8059, 0.8261] | 0.6647 |
| `verified-k4-standardised-gt` | proposer-verifier | verified | 5 | k=4 | 4164 | 0.6658 [0.6518, 0.6794] | 0.8169 [0.8066, 0.8268] | 0.6650 |

Buffers on file (metres), by how many conditions carry that set:

- 7 condition(s): 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 75, 100, 125, 150

Tile-level MCC is on file for 7 of 7 condition(s).

### 5.1 Condition caveats (6 condition(s), 6 distinct caveat(s))

Grouped by identical text: a caveat written once for a family of sibling cells is reproduced once, with every cell it applies to named. Nothing is elided.

- `verified-k3-r2-gt`
  TH7-k3 Reference-revision-r2 evaluation (card planning/reference-revision-2026-09-06.md): the standardised reference with the PI's cluster- and empty-tile-audit adjudications applied (-6 records, +14; 5,018 at marked centres, included whole at every R). Scored by evaluate\_detections.py (14 buffers, tile-level BCa 10,000 / seed 42, --mcc) -- one engine for the whole r2 chain.
- `verified-k3-standardised-gt`
  TH7-k3 vs the ruling-21 standardised reference (student 4,731 + extension 279 at marked centres; F1 and tile MCC share the reference — queue items 2-3, Session 132)
- `verified-k4-r2-gt`
  TH7-k4 Reference-revision-r2 evaluation (card planning/reference-revision-2026-09-06.md): the standardised reference with the PI's cluster- and empty-tile-audit adjudications applied (-6 records, +14; 5,018 at marked centres, included whole at every R). Scored by evaluate\_detections.py (14 buffers, tile-level BCa 10,000 / seed 42, --mcc) -- one engine for the whole r2 chain.
- `verified-k4-standardised-gt`
  TH7-k4 vs the ruling-21 standardised reference (student 4,731 + extension 279 at marked centres; F1 and tile MCC share the reference — queue items 2-3, Session 132)
- `verified-k4-canonical-gt`
  carry-forward (text HIGH T0.7, vote 4-of-5) re-scored vs canonical extended GT
- `verified-k3-canonical-gt`
  text HIGH T0.7, vote 3-of-5 (Session-104 vote=3 shell, prob&gt;=0.15)

### 5.3 Decomposition note

Verbatim from `results/run-conditions.json` — the hand-authored record of how this run was decomposed and what was adjudicated:

> Batch B. text HIGH thinking, T=0.7 (the publishable recovered successor of 55maps-generalisation). Out-of-sample generalisation on the 55-map student corpus (8541 tiles, reviewed student GT). detect\_brief-text proposer x text adversarial verifier. 1 verified condition at the standardised 14-buffer+MCC re-score (consensus operating point 4of5). Consensus-4of5 + non-canonical sibling evals -&gt; deferred \_ignored\_evals. See docs/methodology/55maps-generalisation-runs.md. | Session 105: also carries the canonical extended-GT (Track-2) conditions 'verified-k4-canonical-gt'/'verified-k3-canonical-gt' (paper reference; see results/55maps-extended-gt-2026-06-07/ and results/deployment-oracle-2026-06-06/deployment-oracle-findings.md). The existing 'verified' condition is the historical reviewed-student-GT (Track-1) score. Standardised-reference track (ruling 21, Session 132): the -standardised-gt conditions score the same detection sets against canonical-gt/standardised/ (student 4,731 + extension 279 at marked centres, no ring gate). They supersede the -canonical-gt cells as the paper reference; see results/55maps-standardised-ref-2026-08-14/. Reference-revision-r2 track (Session 149): the -r2-gt conditions score the same detection sets against reference revision r2 and supersede the -standardised-gt cells as the paper reference; see results/55maps-r2-ref-2026-09-06/, results/55map-final-board-r2-2026-09-06/ and planning/reference-revision-2026-09-06.md.

### 5.4 Waived evaluations (6, 2 distinct reason(s))

Scored evaluations under this run that no condition claims, each waived in `results/run-conditions.json` rather than left silent. Grouped by identical reason; where a reason covers more than 12 paths the first 12 are named and the decomposition carries the rest.

- **5 evaluation(s)** — uplift-supplement K=1 anchor (planning/uplift-supplement-2026-08-28.md; scored 5bd514542): an input to the supplement's pairing tables, on the reference of the stratum it pairs with; not a registered condition and not cited by the paper. Waived by PI ruling 2026-09-07 (planning/reference-revision-2026-09-06.md, register-verifier debt).
  - `results/uplift-supplement/k1-gapfill/55maps-text-high-generalisation__verified-k3-r2-gt/evaluation.json`
  - `results/uplift-supplement/k1-gapfill/55maps-text-high-generalisation__verified-k4-r2-gt/evaluation.json`
  - `results/uplift-supplement/k1-gapfill/55maps-text-high-generalisation__verified/evaluation.json`
  - `results/uplift-supplement/verifier-pairing/55maps-text-high-generalisation__verified-k4-r2-gt/evaluation.json`
  - `results/uplift-supplement/verifier-pairing/55maps-text-high-generalisation__verified/evaluation.json`
- **1 evaluation(s)** — uplift-supplement pairing/gap-fill anchor (planning/uplift-supplement-2026-08-28.md): an input to the supplement's pairing tables, scored on the reference, buffer, and frame of the stratum it pairs with; not a registered condition and not cited by the paper. Waived by PI ruling 2026-09-07 (planning/reference-revision-2026-09-06.md, register-verifier debt).
  - `results/uplift-supplement/verifier-pairing/55maps-text-high-generalisation__verified-k3-r2-gt/evaluation.json`

## 6. Analyses that read this run (16)

A run is linked to an analysis when the analysis's `conditions_compared` names one of this run's conditions. *Cells* is how many of the analysis's compared conditions come from this run, out of its total. *Signed* is the register's `manually_verified_at` stamp.

| Analysis | Cells | Type | Hypotheses | Registration | Paper section | Deviations | Signed | Output |
|---|---|---|---|---|---|---|---|---|
| `55map-canonical-leaderboard-50m` | 2 of 8 | leaderboard | — | post-hoc | Results | — | 2026-06-12T06:59:01Z | `results/55map-leaderboard` |
| `55map-canonical-leaderboard-mcc-50m` | 2 of 8 | leaderboard | — | post-hoc | Results | — | 2026-07-27T05:28:40Z | `results/metric-leaderboards` |
| `55map-final-board-2026-08-27` | 2 of 23 | leaderboard | `H13`, `H3` | post-hoc | Results | — | 2026-08-28T12:22:08Z | `results/55map-final-board-2026-08-27/final_board_50m.json` |
| `55map-final-board-r2-2026-09-06` | 2 of 35 | leaderboard | `H13`, `H3` | post-hoc | Results | — | 2026-09-07T08:36:56Z | `results/55map-final-board-r2-2026-09-06/final_board_50m.json` |
| `55map-r2-leaderboard-50m` | 2 of 8 | leaderboard | `H13` | post-hoc | Results | — | 2026-09-07T08:36:56Z | `results/55map-leaderboard/55map_leaderboard_50m_r2.json` |
| `55map-r2-leaderboard-mcc-50m` | 2 of 8 | leaderboard | `H13` | post-hoc | Results | — | 2026-09-07T08:36:56Z | `results/metric-leaderboards/55map-mcc-tiering-r2.json` |
| `55map-standardised-leaderboard-50m` | 2 of 8 | leaderboard | — | post-hoc | Results | — | 2026-08-14T22:45:49Z | `results/55map-leaderboard` |
| `55map-standardised-leaderboard-mcc-50m` | 2 of 8 | leaderboard | — | post-hoc | Results | — | 2026-08-14T22:45:49Z | `results/metric-leaderboards` |
| `estimated-correction-r2` | 2 of 35 | diagnostic | `H13` | post-hoc | Results | — | 2026-09-07T08:36:56Z | `results/55map-final-board-r2-2026-09-06/estimated-correction.json` |
| `obs280-shared-reference` | 2 of 8 | comparison | — | post-hoc | not supplied | — | 2026-08-14T22:45:49Z | `results/55maps-standardised-ref-2026-08-14/obs280-remeasurement.md` |
| `obs280-shared-reference-r2` | 2 of 8 | comparison | `H13` | post-hoc | Results | — | 2026-09-07T08:36:56Z | `results/55maps-r2-ref-2026-09-06/obs280-shared-reference-r2.json` |
| `sensitivity-mde-r2` | 2 of 35 | diagnostic | `H8`, `H9`, `H10`, `H12` | post-hoc | Appendix | — | 2026-09-07T08:36:56Z | `results/sensitivity-mde-2026-08-28/sensitivity-r2.json` |
| `tile-level-f1` | 2 of 10 | comparison | — | post-hoc | Results | — | 2026-09-12T09:03:09Z | `results/tile-level-f1` |
| `tile-level-f1-r2` | 2 of 10 | comparison | `H13` | post-hoc | Appendix | — | 2026-09-07T08:36:56Z | `results/tile-level-f1-r2/tile_level_f1.json` |
| `uplift-supplement-flatten` | 7 of 441 | diagnostic | — | post-hoc | Appendix | — | 2026-09-10T22:55:40Z | `results/uplift-supplement/conditions.csv` |
| `verifier-uplift-pairing` | 7 of 170 | comparison | `H2` | post-hoc | Appendix | — | 2026-09-12T06:04:30Z | `results/uplift-supplement/verifier-uplift.csv` |

## 7. Findings documents (2)

| Document | Named by |
|---|---|
| `results/55maps-standardised-ref-2026-08-14/obs280-remeasurement.md` | `obs280-shared-reference` |
| `results/tile-level-f1/findings.md` | `tile-level-f1` |

## 8. Protocol errata

### 8.2 Mentioning this run (1)

The entry's text names this run id or its directory path. A mention is a pointer to read the entry, not a claim that the erratum is about this run:

- **E63** — `retest-phase3c` (H9 diversity) executed at HIGH thinking level — unregistered departure from the §8.9 `minimal` decision, configuration-verified but not token-corroborated

## 9. Documents and structure in the run directory

| Document class | Filename | Count |
|---|---|---:|
| per-pass/per-run intent | `experiment_intent.md` | 6 |
| evaluation summary | `evaluation.md` | 3 |

These classes are in Revision-Policy scope going forward (`docs/methodology/output-directory-standard.md` § "Documents in Revision Policy Scope").

### 9.1 Registered pools

| Proposer pool | Modality | Path within the run directory |
|---|---|---|
| `detect_brief-text` | text | `proposer/detect_brief-text` |

1 registered verifier-pass directory/directories; see `results/run-conditions.json` for the full list.

## 10. Provenance of this report

This report is a projection. Every figure above is read from one of the committed inputs below; nothing is estimated, and a figure that is not on file is written **not supplied** with its reason.

| Field | Value |
|---|---|
| Generator | `scripts/generate_run_reports.py` v1.1.0 |
| Source commit | `5570447b9` |
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
- `inputs/vectors/bounds/384/55maps_evaluation_bounds.geojson`
- `outputs/55maps-text-high-generalisation/proposer/detect_brief-text/run_1/detections-detect_brief-text-3-flash-2026-04-18.meta.json`

Regenerate and drift-check with:

```bash
python3 scripts/generate_run_reports.py --all --write
python3 scripts/generate_run_reports.py --check
```
