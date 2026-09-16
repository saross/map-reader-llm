<!-- GENERATED FILE — do not hand-edit. Projected from the registered manifests by scripts/generate_run_reports.py v1.1.0. Hand edits are destroyed on the next regeneration and fail the --check drift guard. -->
# Post-run report — 55maps-text-min-n10-uplift

> **GENERATED FILE — do not hand-edit.** Projected from the registered manifests by `scripts/generate_run_reports.py` v1.1.0 at source commit `c576dae8d`. This file carries provenance instead of a hand changelog, per the PI ruling of 2026-09-11 recorded in `docs/methodology/output-directory-standard.md` § "Documents in Revision Policy Scope": a generated document's history is its inputs' and its generator's git history, so "is this current?" is answered by the `--check` drift guard and its tier-1 test, not by a changelog. Regenerate after any manifest rebuild; put before/after notes in the commit message.

**Directory**: `outputs/55maps-text-min-n10-uplift` · **Registry status**: active · **Purpose**: Run B: does PASS COUNT close the -0.030 deployment thinking gap (Obs 362)? 10 minimal passes + band verifier vs TM-k3 and TH7-k3 at the canonical 50 m buffer.

## 1. Identity and registration

| Field | Value |
|---|---|
| Run id | `55maps-text-min-n10-uplift` |
| Directory | `outputs/55maps-text-min-n10-uplift` |
| Registry status | active |
| Purpose | Run B: does PASS COUNT close the -0.030 deployment thinking gap (Obs 362)? 10 minimal passes + band verifier vs TM-k3 and TH7-k3 at the canonical 50 m buffer. |
| Run type (derived) | proposer-verifier |
| Primary hypothesis | not supplied |
| Also informs | `deployment-uplift`, `pass-budget` |
| Headline condition | not supplied |
| Headline rationale | Single-condition run; the citable cell is verified-5of10-canonical-gt (0.8290 @ 50 m, 5of10/pt0.15): significantly above TM-k3 (+0.0163, p&lt;1e-4) and significantly below TH7-k3 (-0.0134, p=0.0026) — a priced cost/quality trade, not a tie (Obs 364). |
| Historical aliases | — |
| Working-notes Obs | — |
| Registry notes | Run B (Session 112-113, ~$60 flex, Shawn-approved): the min11 deployment uplift — 10 gemini-3-flash MINIMAL-thinking T=0.7 detect\_brief-text proposer passes over the 55-map corpus (8,541 tiles), the &gt;=3-of-10 band cropped (16,482 candidates) + the carry-forward n=1 verifier. Answers Obs 362's open question: pass count closes about HALF the deployment thinking gap (Obs 364). Scored vs the canonical extended GT at 50 m (results/55map-leaderboard/min11\_uplift\_cell.json; Track-2 eval results/55maps-extended-gt-2026-06-07/TM-n10-k5/). |

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
| `detect_brief-text-min-n10` | 6 | gemini-3-flash-preview | gemini-3-flash-preview | text | minimal | 0.7 | ok | 8541 | 8541 | 20 |
| `detect_brief-text-min-n10` | 7 | gemini-3-flash-preview | gemini-3-flash-preview | text | minimal | 0.7 | ok | 8541 | 8541 | 6 |
| `detect_brief-text-min-n10` | 8 | gemini-3-flash-preview | gemini-3-flash-preview | text | minimal | 0.7 | ok | 8541 | 8541 | 108 |
| `detect_brief-text-min-n10` | 9 | gemini-3-flash-preview | gemini-3-flash-preview | text | minimal | 0.7 | ok | 8541 | 8541 | 0 |
| `detect_brief-text-min-n10` | 10 | gemini-3-flash-preview | gemini-3-flash-preview | text | minimal | 0.7 | ok | 8541 | 8541 | 40 |

### 3.2 Verifier passes (1)

| Pool | Pass | Model used | Modality | Thinking | Temp | Status | Candidates verified | Retries |
|---|---:|---|---|---|---:|---|---:|---:|
| `verified-3of10` | 1 | gemini-3-flash-preview | text | minimal | 0.0 | ok | 16482 | 2 |

Verifier rows report no tile count by design: verifier pass: operates on candidate crops, not tiles. The verifier meta records candidate ids (cand\_NNNN) in execution\_stats.completed\_items and candidate API items in per\_item\_metadata, so no tile-scale record exists to report. Completed crop count is in n\_candidates\_verified. (E71 Defect 2 / GAP-8, resolved E72 2026-08-02.)

## 4. Token load and recorded cost

| Field | Value |
|---|---|
| Passes on file | 6 |
| Input tokens (billed) | 93,680,156 |
| Input tokens (cached) | 0 |
| Output tokens | 7,408,086 |
| Thinking tokens | 0 |
| Total tokens | 101,088,242 |
| Passes with no token record | 0 |
| Sum of recorded `cost_usd` | US$69.0643 over 6 of 6 pass(es) |
| Passes with no `cost_usd` | 0 |
| Summed wall clock | 2.17 h over 6 pass(es) |

> **Audited: the token figures above are inflated by a measured factor.** `reports/token-load-audit-2026-06-12.md` § 3.5 recomputed this run's load from `per_item_metadata` and found its `usage_stats` block — which is exactly where the manifest takes a pass's `tokens` from (`_tokens_from_usage`) — **clean (factors ≤ 1.0001)**; its `cost_manifest.json` is **not assessed**. The trustworthy source is either. Audited clean figures, quoted from § 3.5: proposer runs 6–10: clean flex cost US$4.65/pass (mean US$4.6531); per pass input 12,828,582 (1,502/tile), output mean 963,967, thinking 0. Verifier (`verified-3of10/run.meta.json`): 16,482 calls, input 29,535,744 (exactly 1,792/call), output 2,588,179, flex US$11.27 (US$0.000684/call). No run total is derived here: the audit's pass count and this manifest's need not agree, so multiplying would manufacture a figure no file carries.
>
> **The recorded cost is NOT this run's cost.** Each `cost_usd` above is the pass meta's own `cost_estimate.total_cost_usd`, lifted verbatim by `scripts/generate_post_run_report.py`. The token-load audit of 2026-06-12 established that those self-reported estimates price at STANDARD rates although the audited runs executed at `--service-tier flex` (half price) and omit thinking tokens although Gemini bills thinking at the output rate (`reports/token-load-audit-2026-06-12.md` § 1, § 2). The sum is reproduced here as the recorded figure and as an input to a reconciliation, not as a total to cite.

Audit and reconciliation reports whose text names this run or its directory — consult these for audited figures; a mention is a pointer, not a claim that the report audits this run in full:

- `reports/token-load-audit-2026-06-12.md`

## 5. Registered conditions (3)

F1@20 m is the preregistered localisation buffer; F1@50 m is the deployment working buffer. Confidence intervals are those the evaluation recorded (method, iterations and seed per condition in the manifest). `mcc` is tile-level. A cell reading *not supplied* means the metric is absent from the condition's evaluation, not that it is zero; a tile-MCC reading *withheld* means the tile-join invariant REFUSED that condition's per-tile table on this frame, so the tile metrics and the bootstrap intervals were not computed — the condition's whole-frame F1 is unaffected and is reported in full (PI ruling 2026-09-13; the named reason is in the condition's manifest row).

| Condition | Architecture | Aggregation | Passes | Operating point | Detections | F1@20 m [CI] | F1@50 m [CI] | Tile MCC |
|---|---|---|---:|---|---:|---|---|---:|
| `verified-5of10-canonical-gt` | proposer-verifier | verified | 10 | k=5/pt=0.15 | 4361 | 0.6472 [0.6325, 0.6618] | 0.8290 [0.8190, 0.8385] | 0.6725 |
| `verified-5of10-r2-gt` | proposer-verifier | verified | 10 | k=5/pt=0.15 | 4361 | 0.6877 [0.6734, 0.7012] | 0.8274 [0.8174, 0.8367] | 0.6695 |
| `verified-5of10-standardised-gt` | proposer-verifier | verified | 10 | k=5/pt=0.15 | 4361 | 0.6879 [0.6738, 0.7016] | 0.8279 [0.8181, 0.8374] | 0.6709 |

Buffers on file (metres), by how many conditions carry that set:

- 3 condition(s): 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 75, 100, 125, 150

Tile-level MCC is on file for 3 of 3 condition(s).

### 5.1 Condition caveats (3 condition(s), 3 distinct caveat(s))

Grouped by identical text: a caveat written once for a family of sibling cells is reproduced once, with every cell it applies to named. Nothing is elided.

- `verified-5of10-r2-gt`
  TM-n10-k5 Reference-revision-r2 evaluation (card planning/reference-revision-2026-09-06.md): the standardised reference with the PI's cluster- and empty-tile-audit adjudications applied (-6 records, +14; 5,018 at marked centres, included whole at every R). Scored by evaluate\_detections.py (14 buffers, tile-level BCa 10,000 / seed 42, --mcc) -- one engine for the whole r2 chain.
- `verified-5of10-standardised-gt`
  TM-n10-k5 vs the ruling-21 standardised reference (student 4,731 + extension 279 at marked centres; F1 and tile MCC share the reference — queue items 2-3, Session 132)
- `verified-5of10-canonical-gt`
  min11 uplift, vote 5-of-10 (prob&gt;=0.15), vs canonical extended GT; best deployment op sat looser than the GS-best 6of10 — the k3 lesson recurring at n=10 (Obs 364)

### 5.3 Decomposition note

Verbatim from `results/run-conditions.json` — the hand-authored record of how this run was decomposed and what was adjudicated:

> Run B uplift: one citable condition at the best deployment operating point (5of10/pt0.15) vs the canonical extended GT. MIXED-PROVENANCE POOL (the n-passes-over WARN is the honest by-design signal, per the S106 settled position): passes 1-5 are the 55maps-text-min-generalisation deployment passes; passes 6-10 are this run's (proposer/run\_6..run\_10; uplift-full.log Stage P). The k(3..10) x prob\_t sweep lives in results/55map-leaderboard/min11-uplift-score.log and min11\_uplift\_cell.json. Standardised-reference track (ruling 21, Session 132): the -standardised-gt conditions score the same detection sets against canonical-gt/standardised/ (student 4,731 + extension 279 at marked centres, no ring gate). They supersede the -canonical-gt cells as the paper reference; see results/55maps-standardised-ref-2026-08-14/. Reference-revision-r2 track (Session 149): the -r2-gt conditions score the same detection sets against reference revision r2 and supersede the -standardised-gt cells as the paper reference; see results/55maps-r2-ref-2026-09-06/, results/55map-final-board-r2-2026-09-06/ and planning/reference-revision-2026-09-06.md.

### 5.4 Waived evaluations (2, 2 distinct reason(s))

Scored evaluations under this run that no condition claims, each waived in `results/run-conditions.json` rather than left silent. Grouped by identical reason; where a reason covers more than 12 paths the first 12 are named and the decomposition carries the rest.

- **1 evaluation(s)** — uplift-supplement K=1 anchor (planning/uplift-supplement-2026-08-28.md; scored 5bd514542): an input to the supplement's pairing tables, on the reference of the stratum it pairs with; not a registered condition and not cited by the paper. Waived by PI ruling 2026-09-07 (planning/reference-revision-2026-09-06.md, register-verifier debt).
  - `results/uplift-supplement/k1-gapfill/55maps-text-min-n10-uplift__verified-5of10-r2-gt/evaluation.json`
- **1 evaluation(s)** — uplift-supplement pairing/gap-fill anchor (planning/uplift-supplement-2026-08-28.md): an input to the supplement's pairing tables, scored on the reference, buffer, and frame of the stratum it pairs with; not a registered condition and not cited by the paper. Waived by PI ruling 2026-09-07 (planning/reference-revision-2026-09-06.md, register-verifier debt).
  - `results/uplift-supplement/verifier-pairing/55maps-text-min-n10-uplift__verified-5of10-r2-gt/evaluation.json`

## 6. Analyses that read this run (16)

A run is linked to an analysis when the analysis's `conditions_compared` names one of this run's conditions. *Cells* is how many of the analysis's compared conditions come from this run, out of its total. *Signed* is the register's `manually_verified_at` stamp.

| Analysis | Cells | Type | Hypotheses | Registration | Paper section | Deviations | Signed | Output |
|---|---|---|---|---|---|---|---|---|
| `55map-canonical-leaderboard-50m` | 1 of 8 | leaderboard | — | post-hoc | Results | — | 2026-06-12T06:59:01Z | `results/55map-leaderboard` |
| `55map-canonical-leaderboard-mcc-50m` | 1 of 8 | leaderboard | — | post-hoc | Results | — | 2026-07-27T05:28:40Z | `results/metric-leaderboards` |
| `55map-final-board-2026-08-27` | 1 of 23 | leaderboard | `H13`, `H3` | post-hoc | Results | — | 2026-08-28T12:22:08Z | `results/55map-final-board-2026-08-27/final_board_50m.json` |
| `55map-final-board-r2-2026-09-06` | 1 of 35 | leaderboard | `H13`, `H3` | post-hoc | Results | — | 2026-09-07T08:36:56Z | `results/55map-final-board-r2-2026-09-06/final_board_50m.json` |
| `55map-r2-leaderboard-50m` | 1 of 8 | leaderboard | `H13` | post-hoc | Results | — | 2026-09-07T08:36:56Z | `results/55map-leaderboard/55map_leaderboard_50m_r2.json` |
| `55map-r2-leaderboard-mcc-50m` | 1 of 8 | leaderboard | `H13` | post-hoc | Results | — | 2026-09-07T08:36:56Z | `results/metric-leaderboards/55map-mcc-tiering-r2.json` |
| `55map-standardised-leaderboard-50m` | 1 of 8 | leaderboard | — | post-hoc | Results | — | 2026-08-14T22:45:49Z | `results/55map-leaderboard` |
| `55map-standardised-leaderboard-mcc-50m` | 1 of 8 | leaderboard | — | post-hoc | Results | — | 2026-08-14T22:45:49Z | `results/metric-leaderboards` |
| `estimated-correction-r2` | 1 of 35 | diagnostic | `H13` | post-hoc | Results | — | 2026-09-07T08:36:56Z | `results/55map-final-board-r2-2026-09-06/estimated-correction.json` |
| `obs280-shared-reference` | 1 of 8 | comparison | — | post-hoc | not supplied | — | 2026-08-14T22:45:49Z | `results/55maps-standardised-ref-2026-08-14/obs280-remeasurement.md` |
| `obs280-shared-reference-r2` | 1 of 8 | comparison | `H13` | post-hoc | Results | — | 2026-09-07T08:36:56Z | `results/55maps-r2-ref-2026-09-06/obs280-shared-reference-r2.json` |
| `sensitivity-mde-r2` | 1 of 35 | diagnostic | `H8`, `H9`, `H10`, `H12` | post-hoc | Appendix | — | 2026-09-07T08:36:56Z | `results/sensitivity-mde-2026-08-28/sensitivity-r2.json` |
| `tile-level-f1` | 1 of 10 | comparison | — | post-hoc | Results | — | 2026-09-12T09:03:09Z | `results/tile-level-f1` |
| `tile-level-f1-r2` | 1 of 10 | comparison | `H13` | post-hoc | Appendix | — | 2026-09-07T08:36:56Z | `results/tile-level-f1-r2/tile_level_f1.json` |
| `uplift-supplement-flatten` | 3 of 441 | diagnostic | — | post-hoc | Appendix | — | 2026-09-10T22:55:40Z | `results/uplift-supplement/conditions.csv` |
| `verifier-uplift-pairing` | 3 of 170 | comparison | `H2` | post-hoc | Appendix | — | 2026-09-12T06:04:30Z | `results/uplift-supplement/verifier-uplift.csv` |

## 7. Findings documents (2)

| Document | Named by |
|---|---|
| `results/55maps-standardised-ref-2026-08-14/obs280-remeasurement.md` | `obs280-shared-reference` |
| `results/tile-level-f1/findings.md` | `tile-level-f1` |

## 8. Protocol errata

### 8.2 Mentioning this run (1)

The entry's text names this run id or its directory path. A mention is a pointer to read the entry, not a claim that the erratum is about this run:

- **E71** — `n\_tiles\_processed` manifest column carries two semantics (dispatched vs completed) plus a verifier-row placeholder (GAP-8) — 15 passes with genuine coverage shortfalls, two live conditions carrying dead tiles as artificial false negatives

## 9. Documents and structure in the run directory

| Document class | Filename | Count |
|---|---|---:|
| per-pass/per-run intent | `experiment_intent.md` | 5 |

These classes are in Revision-Policy scope going forward (`docs/methodology/output-directory-standard.md` § "Documents in Revision Policy Scope").

### 9.1 Registered pools

| Proposer pool | Modality | Path within the run directory |
|---|---|---|
| `detect_brief-text-min-n10` | text | `proposer` |

1 registered verifier-pass directory/directories; see `results/run-conditions.json` for the full list.

## 10. Provenance of this report

This report is a projection. Every figure above is read from one of the committed inputs below; nothing is estimated, and a figure that is not on file is written **not supplied** with its reason.

| Field | Value |
|---|---|
| Generator | `scripts/generate_run_reports.py` v1.1.0 |
| Source commit | `c576dae8d` |
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
- `outputs/55maps-text-min-n10-uplift/proposer/run_10/detections-detect_brief-text-3-flash-2026-06-11.meta.json`

Regenerate and drift-check with:

```bash
python3 scripts/generate_run_reports.py --all --write
python3 scripts/generate_run_reports.py --check
```
