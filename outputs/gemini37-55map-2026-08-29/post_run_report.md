<!-- GENERATED FILE — do not hand-edit. Projected from the registered manifests by scripts/generate_run_reports.py v1.1.0. Hand edits are destroyed on the next regeneration and fail the --check drift guard. -->
# Post-run report — gemini37-55map-2026-08-29

> **GENERATED FILE — do not hand-edit.** Projected from the registered manifests by `scripts/generate_run_reports.py` v1.1.0 at source commit `d9ea97c2e`. This file carries provenance instead of a hand changelog, per the PI ruling of 2026-09-11 recorded in `docs/methodology/output-directory-standard.md` § "Documents in Revision Policy Scope": a generated document's history is its inputs' and its generator's git history, so "is this current?" is answered by the `--check` drift guard and its tier-1 test, not by a changelog. Regenerate after any manifest rebuild; put before/after notes in the commit message.

**Directory**: `outputs/gemini37-55map-2026-08-29` · **Registry status**: active · **Purpose**: Does the 3.7 GS gain transfer to 55-map deployment, and in which seat? One K=5 3.7 proposer pool, two verifier arms (carried Gemini-3; all-3.7), both carried points committed before deployment scoring. With the fourth cell (registered under stride-55map-2026-08-25) this completes the proposer x verifier 2x2. Predictions D1-D7, card planning/gemini37-55map-2026-08-29.md.

## 1. Identity and registration

| Field | Value |
|---|---|
| Run id | `gemini37-55map-2026-08-29` |
| Directory | `outputs/gemini37-55map-2026-08-29` |
| Registry status | active |
| Purpose | Does the 3.7 GS gain transfer to 55-map deployment, and in which seat? One K=5 3.7 proposer pool, two verifier arms (carried Gemini-3; all-3.7), both carried points committed before deployment scoring. With the fourth cell (registered under stride-55map-2026-08-25) this completes the proposer x verifier 2x2. Predictions D1-D7, card planning/gemini37-55map-2026-08-29.md. |
| Run type (derived) | proposer-verifier |
| Primary hypothesis | not supplied |
| Also informs | `H13` |
| Headline condition | gemini37-55map-2026-08-29::arm2-n5-carried-p0.80-k5-canonical-gt |
| Headline rationale | Arm 2, the all-3.7 stack at its committed carried point (canonical corrected-F1@50 0.8763): the campaign's headline and the diagonal that reads +0.0325 over the canonical B N=5 incumbent (p = 0.0001). |
| Historical aliases | — |
| Working-notes Obs | — |
| Registry notes | Gemini 3.7 Flash 55-map deployment arms (card planning/gemini37-55map-2026-08-29.md; predictions D1-D7 committed before any deployment scoring): one K=5 proposer pool, two verifier arms (carried Gemini-3; all-3.7). Results tree is results/gemini37-55map-2026-08-31/ — the run-directory/results-directory skew is deliberate and directory\_path carries the truth. Registered S149. |

## 2. Scope and evaluation frame

| Field | Value |
|---|---|
| Tile size (px) | 384 |
| Corpus | 55-map |
| Ground-truth reference | combined |
| Test set id | 55maps-8541 |
| Test tiles | 8541 |
| Bounds | `inputs/vectors/bounds/384/55maps_evaluation_bounds.geojson` |
| Calibration set id | not supplied |
| Calibration tiles | not supplied |

## 3. Execution — passes on file

### 3.1 Proposer passes (5)

| Pool | Pass | Model used | Model requested | Modality | Thinking | Temp | Status | Tiles done | Dispatched | Retries |
|---|---:|---|---|---|---|---:|---|---:|---:|---:|
| `g384_ov192_55map_g37` | 1 | gemini-3.7-flash | gemini-3.7-flash | text | low | 0.7 | ok | 24561 | 24561 | 38045 |
| `g384_ov192_55map_g37` | 2 | gemini-3.7-flash | gemini-3.7-flash | text | low | 0.7 | ok | 24561 | 24561 | 30550 |
| `g384_ov192_55map_g37` | 3 | gemini-3.7-flash | gemini-3.7-flash | text | low | 0.7 | ok | 24561 | 24561 | 241834 |
| `g384_ov192_55map_g37` | 4 | gemini-3.7-flash | gemini-3.7-flash | text | low | 0.7 | ok | 24561 | 24561 | 21241 |
| `g384_ov192_55map_g37` | 5 | gemini-3.7-flash | gemini-3.7-flash | text | low | 0.7 | ok | 24561 | 24561 | 10568 |

### 3.2 Verifier passes (2)

| Pool | Pass | Model used | Modality | Thinking | Temp | Status | Candidates verified | Retries |
|---|---:|---|---|---|---:|---|---:|---:|
| `g384_ov192_55map_g37-union-k5-verify-arm1` | 1 | gemini-3-flash-preview | text | minimal | 0.0 | ok | 12715 | 5 |
| `g384_ov192_55map_g37-union-k5-verify-arm2` | 1 | gemini-3.7-flash | text | low | 0.0 | ok | 12715 | 4084 |

Verifier rows report no tile count by design: verifier pass: operates on candidate crops, not tiles. The verifier meta records candidate ids (cand\_NNNN) in execution\_stats.completed\_items and candidate API items in per\_item\_metadata, so no tile-scale record exists to report. Completed crop count is in n\_candidates\_verified. (E71 Defect 2 / GAP-8, resolved E72 2026-08-02.)

## 4. Token load and recorded cost

| Field | Value |
|---|---|
| Passes on file | 7 |
| Input tokens (billed) | 206,305,588 |
| Input tokens (cached) | 0 |
| Output tokens | 9,361,724 |
| Thinking tokens | 30,579,369 |
| Total tokens | 246,246,681 |
| Passes with no token record | 0 |
| Sum of recorded `cost_usd` | US$82.6183 over 7 of 7 pass(es) |
| Passes with no `cost_usd` | 0 |
| Summed wall clock | 48.92 h over 7 pass(es) |

> **The recorded cost is NOT this run's cost.** Each `cost_usd` above is the pass meta's own `cost_estimate.total_cost_usd`, lifted verbatim by `scripts/generate_post_run_report.py`. The token-load audit of 2026-06-12 established that those self-reported estimates price at STANDARD rates although the audited runs executed at `--service-tier flex` (half price) and omit thinking tokens although Gemini bills thinking at the output rate (`reports/token-load-audit-2026-06-12.md` § 1, § 2). The sum is reproduced here as the recorded figure and as an input to a reconciliation, not as a total to cite.

Audit and reconciliation reports whose text names this run or its directory — consult these for audited figures; a mention is a pointer, not a claim that the report audits this run in full:

- `reports/r7-gaps-deltas-2026-09-11.md`
- `reports/billing-reconciliation-2026-09-11.md`

## 5. Registered conditions (12)

F1@20 m is the preregistered localisation buffer; F1@50 m is the deployment working buffer. Confidence intervals are those the evaluation recorded (method, iterations and seed per condition in the manifest). `mcc` is tile-level. A cell reading *not supplied* means the metric is absent from the condition's evaluation, not that it is zero; a tile-MCC reading *withheld* means the tile-join invariant REFUSED that condition's per-tile table on this frame, so the tile metrics and the bootstrap intervals were not computed — the condition's whole-frame F1 is unaffected and is reported in full (PI ruling 2026-09-13; the named reason is in the condition's manifest row).

| Condition | Architecture | Aggregation | Passes | Operating point | Detections | F1@20 m [CI] | F1@50 m [CI] | Tile MCC |
|---|---|---|---:|---|---:|---|---|---:|
| `arm1-n1-oracle-p0.20-k1-r2-gt` | proposer-verifier | verified | 1 | k=1/pt=0.2 | 5219 | 0.7481 [0.7367, 0.7591] | 0.8413 [0.8332, 0.8492] | 0.7246 |
| `arm1-n3-oracle-p0.15-k3-r2-gt` | proposer-verifier | verified | 3 | k=3/pt=0.15 | 4772 | 0.7739 [0.7621, 0.7853] | 0.8705 [0.8625, 0.8780] | 0.7179 |
| `arm1-n5-carried-p0.10-k5-canonical-gt` | proposer-verifier | verified | 5 | k=5/pt=0.1 | 5229 | 0.7220 [0.7092, 0.7346] | 0.8494 [0.8410, 0.8574] | 0.6665 |
| `arm1-n5-carried-p0.10-k5-r2-gt` | proposer-verifier | verified | 5 | k=5/pt=0.1 | 5229 | 0.7592 [0.7475, 0.7708] | 0.8551 [0.8466, 0.8631] | 0.6655 |
| `arm1-n5-carried-p0.10-k5-standardised-gt` | proposer-verifier | verified | 5 | k=5/pt=0.1 | 5229 | 0.7591 [0.7473, 0.7705] | 0.8550 [0.8465, 0.8630] | 0.6665 |
| `arm1-n5-oracle-p0.15-k5-r2-gt` | proposer-verifier | verified | 5 | k=5/pt=0.15 | 4616 | 0.7754 [0.7635, 0.7869] | 0.8727 [0.8644, 0.8803] | 0.7147 |
| `arm2-n1-oracle-p0.98-k1-r2-gt` | proposer-verifier | verified | 1 | k=1/pt=0.98 | 5021 | 0.7664 [0.7549, 0.7775] | 0.8610 [0.8534, 0.8684] | 0.7422 |
| `arm2-n3-oracle-p0.95-k3-r2-gt` | proposer-verifier | verified | 3 | k=3/pt=0.95 | 5097 | 0.7870 [0.7754, 0.7982] | 0.8848 [0.8770, 0.8919] | 0.7163 |
| `arm2-n5-carried-p0.80-k5-canonical-gt` | proposer-verifier | verified | 5 | k=5/pt=0.8 | 5003 | 0.7469 [0.7345, 0.7595] | 0.8763 [0.8686, 0.8837] | 0.7073 |
| `arm2-n5-carried-p0.80-k5-r2-gt` | proposer-verifier | verified | 5 | k=5/pt=0.8 | 5003 | 0.7846 [0.7731, 0.7960] | 0.8827 [0.8749, 0.8899] | 0.7063 |
| `arm2-n5-carried-p0.80-k5-standardised-gt` | proposer-verifier | verified | 5 | k=5/pt=0.8 | 5003 | 0.7840 [0.7725, 0.7954] | 0.8825 [0.8746, 0.8897] | 0.7073 |
| `arm2-n5-oracle-p0.95-k5-r2-gt` | proposer-verifier | verified | 5 | k=5/pt=0.95 | 4924 | 0.7888 [0.7774, 0.8002] | 0.8871 [0.8794, 0.8943] | 0.7147 |

Buffers on file (metres), by how many conditions carry that set:

- 10 condition(s): 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 75, 100, 125, 150
- 2 condition(s): 20, 30, 50

Tile-level MCC is on file for 12 of 12 condition(s).

### 5.1 Condition caveats (12 condition(s), 12 distinct caveat(s))

Grouped by identical text: a caveat written once for a family of sibling cells is reproduced once, with every cell it applies to named. Nothing is elided.

- `arm1-n5-carried-p0.10-k5-canonical-gt`
  B1 — arm 1 (3.7 proposer + carried Gemini-3 verifier) at its committed carried point, CANONICAL chain: corrected-F1@50 0.849360 [0.841013, 0.857383], P 0.8438 / R 0.8550, tile-MCC 0.6665, 5,229 detections. Against the canonical B N=5 incumbent 0.8438 this is +0.0056, p = 0.3488 — below the 55-map MDE80 of 0.013, which is D1's pre-named informative failure.
- `arm1-n5-carried-p0.10-k5-standardised-gt`
  B2 — the same detections on the ruling-21 STANDARDISED reference: F1@50 0.8550 [0.8465, 0.8630], P 0.8371 / R 0.8737. The tile confusion matrix is identical to the canonical chain's 50 m row (2533/4632/385/991), so the two rows share one tile-MCC.
- `arm2-n5-carried-p0.80-k5-canonical-gt`
  B3 — arm 2 (all-3.7) at its committed carried point, CANONICAL chain: corrected-F1@50 0.876316 [0.868574, 0.883690], P 0.8901 / R 0.8630, tile-MCC 0.7073, 5,003 detections. The campaign headline: +0.0270 over arm 1 (p = 0.0001, BH-significant) — the family gain sits in the verifier seat. Also the model arm of the student-baseline programme (planning/student-baseline-2026-08-31.md).
- `arm2-n5-carried-p0.80-k5-standardised-gt`
  B4 — the same detections on the STANDARDISED reference: F1@50 0.8825 [0.8746, 0.8897], P 0.8831 / R 0.8818 — above the entire 2026-08-27 final board including its oracles (ceiling B-N10-oracle 0.8558). Tile matrix identical to the canonical 50 m row (2516/4798/219/1008).
- `arm1-n1-oracle-p0.20-k1-r2-gt`
  r2 board cell ARM1-N1-oracle (oracle (r2-reference argmax), F1@50 0.8413, tier via final\_board\_50m.json). Reference-revision-r2 evaluation (card planning/reference-revision-2026-09-06.md): the standardised reference with the PI's cluster- and empty-tile-audit adjudications applied (-6 records, +14; 5,018 at marked centres, included whole at every R). Scored by evaluate\_detections.py (14 buffers, tile-level BCa 10,000 / seed 42, --mcc) -- one engine for the whole r2 chain.
- `arm1-n3-oracle-p0.15-k3-r2-gt`
  r2 board cell ARM1-N3-oracle (oracle (r2-reference argmax), F1@50 0.8705, tier via final\_board\_50m.json). Reference-revision-r2 evaluation (card planning/reference-revision-2026-09-06.md): the standardised reference with the PI's cluster- and empty-tile-audit adjudications applied (-6 records, +14; 5,018 at marked centres, included whole at every R). Scored by evaluate\_detections.py (14 buffers, tile-level BCa 10,000 / seed 42, --mcc) -- one engine for the whole r2 chain.
- `arm1-n5-carried-p0.10-k5-r2-gt`
  r2 board cell ARM1-N5-carried (carried, F1@50 0.8551, tier via final\_board\_50m.json). Reference-revision-r2 evaluation (card planning/reference-revision-2026-09-06.md): the standardised reference with the PI's cluster- and empty-tile-audit adjudications applied (-6 records, +14; 5,018 at marked centres, included whole at every R). Scored by evaluate\_detections.py (14 buffers, tile-level BCa 10,000 / seed 42, --mcc) -- one engine for the whole r2 chain.
- `arm1-n5-oracle-p0.15-k5-r2-gt`
  r2 board cell ARM1-N5-oracle (oracle (r2-reference argmax), F1@50 0.8727, tier via final\_board\_50m.json). Reference-revision-r2 evaluation (card planning/reference-revision-2026-09-06.md): the standardised reference with the PI's cluster- and empty-tile-audit adjudications applied (-6 records, +14; 5,018 at marked centres, included whole at every R). Scored by evaluate\_detections.py (14 buffers, tile-level BCa 10,000 / seed 42, --mcc) -- one engine for the whole r2 chain.
- `arm2-n1-oracle-p0.98-k1-r2-gt`
  r2 board cell ARM2-N1-oracle (oracle (r2-reference argmax), F1@50 0.8610, tier via final\_board\_50m.json). Reference-revision-r2 evaluation (card planning/reference-revision-2026-09-06.md): the standardised reference with the PI's cluster- and empty-tile-audit adjudications applied (-6 records, +14; 5,018 at marked centres, included whole at every R). Scored by evaluate\_detections.py (14 buffers, tile-level BCa 10,000 / seed 42, --mcc) -- one engine for the whole r2 chain.
- `arm2-n3-oracle-p0.95-k3-r2-gt`
  r2 board cell ARM2-N3-oracle (oracle (r2-reference argmax), F1@50 0.8848, tier via final\_board\_50m.json). Reference-revision-r2 evaluation (card planning/reference-revision-2026-09-06.md): the standardised reference with the PI's cluster- and empty-tile-audit adjudications applied (-6 records, +14; 5,018 at marked centres, included whole at every R). Scored by evaluate\_detections.py (14 buffers, tile-level BCa 10,000 / seed 42, --mcc) -- one engine for the whole r2 chain.
- `arm2-n5-carried-p0.80-k5-r2-gt`
  r2 board cell ARM2-N5-carried (carried, F1@50 0.8827, tier via final\_board\_50m.json). Reference-revision-r2 evaluation (card planning/reference-revision-2026-09-06.md): the standardised reference with the PI's cluster- and empty-tile-audit adjudications applied (-6 records, +14; 5,018 at marked centres, included whole at every R). Scored by evaluate\_detections.py (14 buffers, tile-level BCa 10,000 / seed 42, --mcc) -- one engine for the whole r2 chain.
- `arm2-n5-oracle-p0.95-k5-r2-gt`
  r2 board cell ARM2-N5-oracle (oracle (r2-reference argmax), F1@50 0.8871, tier via final\_board\_50m.json). Reference-revision-r2 evaluation (card planning/reference-revision-2026-09-06.md): the standardised reference with the PI's cluster- and empty-tile-audit adjudications applied (-6 records, +14; 5,018 at marked centres, included whole at every R). Scored by evaluate\_detections.py (14 buffers, tile-level BCa 10,000 / seed 42, --mcc) -- one engine for the whole r2 chain.

### 5.3 Decomposition note

Verbatim from `results/run-conditions.json` — the hand-authored record of how this run was decomposed and what was adjudicated:

> 55-map deployment arms for the Gemini 3.7 proposer (card planning/gemini37-55map-2026-08-29.md). One K=5 proposer pool (union 12,715 candidates), two verifier arms over it, both carried operating points committed on the card at :140-141 before any deployment scoring. TWO INSTRUMENTS, one row each per cell (Obs 444 § (b); results/gemini37-55map-2026-08-31/findings.md § 'Reference instruments'): the canonical adjudicated extended Ground Truth (5,160 references at 50 m, corrected-F1 engine, the campaign's committed primary) and the ruling-21 standardised reference inputs/vectors/references/best-available-gt-55maps.geojson (5,010 references, scripts/evaluate\_detections.py). The canonical eval\_paths point at evaluation.json files written by this script's adapter from the engine's summary.json (deterministic transform; nothing recomputed). Nothing here is scored against the r2 reference. The 16-cell grid board's oracle and N=1/N=3 rungs are NOT registered (no materialised detections or evaluations; deferred to the r2 recompute chain per PI ruling 4). Reference-revision-r2 track (Session 149): the -r2-gt conditions score the same detection sets against reference revision r2 and supersede the -standardised-gt cells as the paper reference; see results/55maps-r2-ref-2026-09-06/, results/55map-final-board-r2-2026-09-06/ and planning/reference-revision-2026-09-06.md.

### 5.4 Waived evaluations (12, 1 distinct reason(s))

Scored evaluations under this run that no condition claims, each waived in `results/run-conditions.json` rather than left silent. Grouped by identical reason; where a reason covers more than 12 paths the first 12 are named and the decomposition carries the rest.

- **12 evaluation(s)** — uplift-supplement K=1 anchor (planning/uplift-supplement-2026-08-28.md; scored 5bd514542): an input to the supplement's pairing tables, on the reference of the stratum it pairs with; not a registered condition and not cited by the paper. Waived by PI ruling 2026-09-07 (planning/reference-revision-2026-09-06.md, register-verifier debt).
  - `results/uplift-supplement/k1-gapfill/gemini37-55map-2026-08-29__arm1-n3-oracle-p0_15-k3-r2-gt/evaluation.json`
  - `results/uplift-supplement/k1-gapfill/gemini37-55map-2026-08-29__arm1-n5-carried-p0_10-k5-r2-gt/evaluation.json`
  - `results/uplift-supplement/k1-gapfill/gemini37-55map-2026-08-29__arm1-n5-oracle-p0_15-k5-r2-gt/evaluation.json`
  - `results/uplift-supplement/k1-gapfill/gemini37-55map-2026-08-29__arm2-n3-oracle-p0_95-k3-r2-gt/evaluation.json`
  - `results/uplift-supplement/k1-gapfill/gemini37-55map-2026-08-29__arm2-n5-carried-p0_80-k5-r2-gt/evaluation.json`
  - `results/uplift-supplement/k1-gapfill/gemini37-55map-2026-08-29__arm2-n5-oracle-p0_95-k5-r2-gt/evaluation.json`
  - `results/uplift-supplement/verifier-pairing/gemini37-55map-2026-08-29__arm1-n5-carried-p0_10-k5-r2-gt/evaluation.json`
  - `results/uplift-supplement/verifier-pairing/gemini37-55map-2026-08-29__arm1-n5-carried-p0_10-k5-standardised-gt/evaluation.json`
  - `results/uplift-supplement/verifier-pairing/gemini37-55map-2026-08-29__arm1-n5-oracle-p0_15-k5-r2-gt/evaluation.json`
  - `results/uplift-supplement/verifier-pairing/gemini37-55map-2026-08-29__arm2-n5-carried-p0_80-k5-r2-gt/evaluation.json`
  - `results/uplift-supplement/verifier-pairing/gemini37-55map-2026-08-29__arm2-n5-carried-p0_80-k5-standardised-gt/evaluation.json`
  - `results/uplift-supplement/verifier-pairing/gemini37-55map-2026-08-29__arm2-n5-oracle-p0_95-k5-r2-gt/evaluation.json`

## 6. Analyses that read this run (8)

A run is linked to an analysis when the analysis's `conditions_compared` names one of this run's conditions. *Cells* is how many of the analysis's compared conditions come from this run, out of its total. *Signed* is the register's `manually_verified_at` stamp.

| Analysis | Cells | Type | Hypotheses | Registration | Paper section | Deviations | Signed | Output |
|---|---|---|---|---|---|---|---|---|
| `55map-final-board-r2-2026-09-06` | 8 of 35 | leaderboard | `H13`, `H3` | post-hoc | Results | — | 2026-09-07T08:36:56Z | `results/55map-final-board-r2-2026-09-06/final_board_50m.json` |
| `estimated-correction-r2` | 8 of 35 | diagnostic | `H13` | post-hoc | Results | — | 2026-09-07T08:36:56Z | `results/55map-final-board-r2-2026-09-06/estimated-correction.json` |
| `gemini37-55map-grid-2026-08-31` | 4 of 8 | comparison | — | post-hoc | Results | — | 2026-09-12T09:03:09Z | `results/gemini37-55map-2026-08-31` |
| `gemini37-55map-gridboard-2026-08-31` | 2 of 4 | leaderboard | — | post-hoc | Results | — | 2026-09-12T09:03:09Z | `results/gemini37-55map-2026-08-31/grid-board` |
| `k-ladder-2026-09-12` | 8 of 94 | comparison | `H3`, `H13` | post-hoc | Results | `E56`, `E85` | 2026-09-13T06:58:12Z | `results/k-ladder-2026-09-12/findings.md` |
| `sensitivity-mde-r2` | 8 of 35 | diagnostic | `H8`, `H9`, `H10`, `H12` | post-hoc | Appendix | — | 2026-09-07T08:36:56Z | `results/sensitivity-mde-2026-08-28/sensitivity-r2.json` |
| `uplift-supplement-flatten` | 12 of 441 | diagnostic | — | post-hoc | Appendix | — | 2026-09-10T22:55:40Z | `results/uplift-supplement/conditions.csv` |
| `verifier-uplift-pairing` | 12 of 170 | comparison | `H2` | post-hoc | Appendix | — | 2026-09-12T06:04:30Z | `results/uplift-supplement/verifier-uplift.csv` |

## 7. Findings documents (1)

| Document | Named by |
|---|---|
| `results/k-ladder-2026-09-12/findings.md` | `k-ladder-2026-09-12` |

## 8. Protocol errata

### 8.1 Registered as deviations (2)

Listed in the `deviations` field of an analysis that reads this run:

- **E56** — Verifier probability-threshold operating points are in-sample (test-set-selected), not calibrated
- **E85** — The temperature study's five consensus conditions were labelled N = 30 but read a 5-pass union — relabelled `consensus-{1..5}of5`; no measured value changes

## 9. Documents and structure in the run directory

| Document class | Filename | Count |
|---|---|---:|
| per-pass/per-run intent | `experiment_intent.md` | 14 |

These classes are in Revision-Policy scope going forward (`docs/methodology/output-directory-standard.md` § "Documents in Revision Policy Scope").

### 9.1 Registered pools

| Proposer pool | Modality | Path within the run directory |
|---|---|---|
| `g384_ov192_55map_g37` | text | `g384_ov192_55map_g37` |

2 registered verifier-pass directory/directories; see `results/run-conditions.json` for the full list.

## 10. Provenance of this report

This report is a projection. Every figure above is read from one of the committed inputs below; nothing is estimated, and a figure that is not on file is written **not supplied** with its reason.

| Field | Value |
|---|---|
| Generator | `scripts/generate_run_reports.py` v1.1.0 |
| Source commit | `d9ea97c2e` |
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

Regenerate and drift-check with:

```bash
python3 scripts/generate_run_reports.py --all --write
python3 scripts/generate_run_reports.py --check
```
