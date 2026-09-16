<!-- GENERATED FILE — do not hand-edit. Projected from the registered manifests by scripts/generate_run_reports.py v1.1.0. Hand edits are destroyed on the next regeneration and fail the --check drift guard. -->
# Post-run report — h8-v2

> **GENERATED FILE — do not hand-edit.** Projected from the registered manifests by `scripts/generate_run_reports.py` v1.1.0 at source commit `1f6826f5e`. This file carries provenance instead of a hand changelog, per the PI ruling of 2026-09-11 recorded in `docs/methodology/output-directory-standard.md` § "Documents in Revision Policy Scope": a generated document's history is its inputs' and its generator's git history, so "is this current?" is answered by the `--check` drift guard and its tier-1 test, not by a changelog. Regenerate after any manifest rebuild; put before/after notes in the commit message.

**Directory**: `outputs/h8-v2` · **Registry status**: active · **Purpose**: not supplied

## 1. Identity and registration

| Field | Value |
|---|---|
| Run id | `h8-v2` |
| Directory | `outputs/h8-v2` |
| Registry status | active |
| Purpose | not supplied |
| Run type (derived) | mixed |
| Primary hypothesis | H8 |
| Also informs | `library-design` |
| Headline condition | not supplied |
| Headline rationale | not supplied |
| Historical aliases | `Era 3` |
| Working-notes Obs | — |
| Registry notes | one run. 7 proposer pools (canonical/plus-hp/pure-positive-canon/scale-4/8/16/32, each run\_1-5 = library-composition variants); greedy/ and wbf/ are aggregation-output collectors -&gt; conditions = composition x aggregation (greedy/wbf/consensus). Inventory: H8v2. Mixed eval scope: most on 487, verifier-stage on 327 -&gt; per-condition scope\_override in facts (beacon trap). |

## 2. Scope and evaluation frame

| Field | Value |
|---|---|
| Tile size (px) | 384 |
| Corpus | 4-map-gs |
| Ground-truth reference | curator |
| Test set id | era-3-327 |
| Test tiles | 327 |
| Bounds | `inputs/vectors/bounds/384/h10_test_bounds.geojson` |
| Calibration set id | pool_160 |
| Calibration tiles | 160 |

## 3. Execution — passes on file

### 3.1 Proposer passes (35)

| Pool | Pass | Model used | Model requested | Modality | Thinking | Temp | Status | Tiles done | Dispatched | Retries |
|---|---:|---|---|---|---|---:|---|---:|---:|---:|
| `canonical` | 1 | gemini-3-flash-preview | gemini-3-flash-preview | image | high | 0.7 | ok | 327 | 327 | 4 |
| `canonical` | 2 | gemini-3-flash-preview | gemini-3-flash-preview | image | high | 0.7 | ok | 327 | 327 | 4 |
| `canonical` | 3 | gemini-3-flash-preview | gemini-3-flash-preview | image | high | 0.7 | ok | 327 | 327 | 11 |
| `canonical` | 4 | gemini-3-flash-preview | gemini-3-flash-preview | image | high | 0.7 | ok | 327 | 327 | 10 |
| `canonical` | 5 | gemini-3-flash-preview | gemini-3-flash-preview | image | high | 0.7 | ok | 327 | 327 | 12 |
| `plus-hp` | 1 | gemini-3-flash-preview | gemini-3-flash-preview | image | high | 0.7 | ok | 327 | 327 | 8 |
| `plus-hp` | 2 | gemini-3-flash-preview | gemini-3-flash-preview | image | high | 0.7 | ok | 327 | 327 | 5 |
| `plus-hp` | 3 | gemini-3-flash-preview | gemini-3-flash-preview | image | high | 0.7 | ok | 327 | 327 | 9 |
| `plus-hp` | 4 | gemini-3-flash-preview | gemini-3-flash-preview | image | high | 0.7 | ok | 327 | 327 | 9 |
| `plus-hp` | 5 | gemini-3-flash-preview | gemini-3-flash-preview | image | high | 0.7 | ok | 327 | 327 | 7 |
| `pure-positive-canon` | 1 | gemini-3-flash-preview | gemini-3-flash-preview | image | high | 0.7 | ok | 327 | 327 | 7 |
| `pure-positive-canon` | 2 | gemini-3-flash-preview | gemini-3-flash-preview | image | high | 0.7 | ok | 327 | 327 | 5 |
| `pure-positive-canon` | 3 | gemini-3-flash-preview | gemini-3-flash-preview | image | high | 0.7 | ok | 327 | 327 | 6 |
| `pure-positive-canon` | 4 | gemini-3-flash-preview | gemini-3-flash-preview | image | high | 0.7 | ok | 327 | 327 | 8 |
| `pure-positive-canon` | 5 | gemini-3-flash-preview | gemini-3-flash-preview | image | high | 0.7 | ok | 327 | 327 | 12 |
| `scale-16` | 1 | gemini-3-flash-preview | gemini-3-flash-preview | image | high | 0.7 | ok | 327 | 327 | 9 |
| `scale-16` | 2 | gemini-3-flash-preview | gemini-3-flash-preview | image | high | 0.7 | ok | 327 | 327 | 6 |
| `scale-16` | 3 | gemini-3-flash-preview | gemini-3-flash-preview | image | high | 0.7 | ok | 327 | 327 | 4 |
| `scale-16` | 4 | gemini-3-flash-preview | gemini-3-flash-preview | image | high | 0.7 | ok | 327 | 327 | 8 |
| `scale-16` | 5 | gemini-3-flash-preview | gemini-3-flash-preview | image | high | 0.7 | ok | 327 | 327 | 4 |
| `scale-32` | 1 | gemini-3-flash-preview | gemini-3-flash-preview | image | high | 0.7 | ok | 327 | 327 | 9 |
| `scale-32` | 2 | gemini-3-flash-preview | gemini-3-flash-preview | image | high | 0.7 | ok | 327 | 327 | 7 |
| `scale-32` | 3 | gemini-3-flash-preview | gemini-3-flash-preview | image | high | 0.7 | ok | 327 | 327 | 11 |
| `scale-32` | 4 | gemini-3-flash-preview | gemini-3-flash-preview | image | high | 0.7 | ok | 327 | 327 | 9 |
| `scale-32` | 5 | gemini-3-flash-preview | gemini-3-flash-preview | image | high | 0.7 | ok | 327 | 327 | 9 |
| `scale-4` | 1 | gemini-3-flash-preview | gemini-3-flash-preview | image | high | 0.7 | ok | 327 | 327 | 2 |
| `scale-4` | 2 | gemini-3-flash-preview | gemini-3-flash-preview | image | high | 0.7 | ok | 327 | 327 | 5 |
| `scale-4` | 3 | gemini-3-flash-preview | gemini-3-flash-preview | image | high | 0.7 | ok | 327 | 327 | 6 |
| `scale-4` | 4 | gemini-3-flash-preview | gemini-3-flash-preview | image | high | 0.7 | ok | 327 | 327 | 8 |
| `scale-4` | 5 | gemini-3-flash-preview | gemini-3-flash-preview | image | high | 0.7 | ok | 327 | 327 | 13 |
| `scale-8` | 1 | gemini-3-flash-preview | gemini-3-flash-preview | image | high | 0.7 | ok | 327 | 327 | 5 |
| `scale-8` | 2 | gemini-3-flash-preview | gemini-3-flash-preview | image | high | 0.7 | ok | 327 | 327 | 3 |
| `scale-8` | 3 | gemini-3-flash-preview | gemini-3-flash-preview | image | high | 0.7 | ok | 327 | 327 | 6 |
| `scale-8` | 4 | gemini-3-flash-preview | gemini-3-flash-preview | image | high | 0.7 | ok | 327 | 327 | 9 |
| `scale-8` | 5 | gemini-3-flash-preview | gemini-3-flash-preview | image | high | 0.7 | ok | 327 | 327 | 4 |

### 3.2 Verifier passes (3)

| Pool | Pass | Model used | Modality | Thinking | Temp | Status | Candidates verified | Retries |
|---|---:|---|---|---|---:|---|---:|---:|
| `scale-4-verified` | 1 | gemini-3-flash-preview | text | minimal | 0.0 | ok | 1551 | 0 |
| `wbf-scale-4-verified` | 1 | gemini-3-flash-preview | text | minimal | 0.0 | ok | 15 | 0 |
| `wbf-scale-8-verified` | 1 | gemini-3-flash-preview | text | minimal | 0.0 | ok | 1053 | 0 |

Verifier rows report no tile count by design: verifier pass: operates on candidate crops, not tiles. The verifier meta records candidate ids (cand\_NNNN) in execution\_stats.completed\_items and candidate API items in per\_item\_metadata, so no tile-scale record exists to report. Completed crop count is in n\_candidates\_verified. (E71 Defect 2 / GAP-8, resolved E72 2026-08-02.)

## 4. Token load and recorded cost

| Field | Value |
|---|---|
| Passes on file | 38 |
| Input tokens (billed) | 244,412,211 |
| Input tokens (cached) | 227,106,405 |
| Output tokens | 1,860,822 |
| Thinking tokens | 21,396,650 |
| Total tokens | 267,669,683 |
| Passes with no token record | 0 |
| Sum of recorded `cost_usd` | US$127.7886 over 38 of 38 pass(es) |
| Passes with no `cost_usd` | 0 |
| Summed wall clock | 2.01 h over 38 pass(es) |

> **The recorded cost is NOT this run's cost.** Each `cost_usd` above is the pass meta's own `cost_estimate.total_cost_usd`, lifted verbatim by `scripts/generate_post_run_report.py`. The token-load audit of 2026-06-12 established that those self-reported estimates price at STANDARD rates although the audited runs executed at `--service-tier flex` (half price) and omit thinking tokens although Gemini bills thinking at the output rate (`reports/token-load-audit-2026-06-12.md` § 1, § 2). The sum is reproduced here as the recorded figure and as an input to a reconciliation, not as a total to cite.

No cost audit on file names this run or its directory: an independently audited cost for this run is **not supplied**. The four audits checked are `reports/token-load-audit-2026-06-12.md`, `reports/r7-gaps-deltas-2026-09-11.md`, `reports/k-ladder-phase2-deltas-2026-09-12.md`, `reports/billing-reconciliation-2026-09-11.md`.

## 5. Registered conditions (17)

F1@20 m is the preregistered localisation buffer; F1@50 m is the deployment working buffer. Confidence intervals are those the evaluation recorded (method, iterations and seed per condition in the manifest). `mcc` is tile-level. A cell reading *not supplied* means the metric is absent from the condition's evaluation, not that it is zero; a tile-MCC reading *withheld* means the tile-join invariant REFUSED that condition's per-tile table on this frame, so the tile metrics and the bootstrap intervals were not computed — the condition's whole-frame F1 is unaffected and is reported in full (PI ruling 2026-09-13; the named reason is in the condition's manifest row).

| Condition | Architecture | Aggregation | Passes | Operating point | Detections | F1@20 m [CI] | F1@50 m [CI] | Tile MCC |
|---|---|---|---:|---|---:|---|---|---:|
| `greedy-canonical` | consensus | greedy | 5 | k=4 | 258 | 0.7071 [0.6454, 0.7610] | not supplied | 0.6785 |
| `greedy-plus-hp` | consensus | greedy | 5 | k=4 | 254 | 0.7051 [0.6472, 0.7602] | not supplied | 0.7306 |
| `greedy-pure-positive-canon` | consensus | greedy | 5 | k=4 | 275 | 0.6970 [0.6400, 0.7487] | not supplied | 0.6502 |
| `greedy-scale-16` | consensus | greedy | 5 | k=4 | 238 | 0.6930 [0.6345, 0.7488] | not supplied | 0.7194 |
| `greedy-scale-32` | consensus | greedy | 5 | k=4 | 242 | 0.7130 [0.6585, 0.7619] | not supplied | 0.7168 |
| `greedy-scale-4` | consensus | greedy | 5 | k=4 | 257 | 0.7326 [0.6788, 0.7828] | not supplied | 0.7714 |
| `greedy-scale-8` | consensus | greedy | 5 | k=4 | 250 | 0.7100 [0.6511, 0.7641] | not supplied | 0.7500 |
| `verified-scale-4` | proposer-verifier | verified | 5 | k=4/pt=0.1 | 251 | 0.7368 [0.6853, 0.7866] | 0.8175 [0.7746, 0.8562] | 0.8030 |
| `verified-wbf-scale-4` | proposer-verifier | verified | 5 | k=4/pt=0.1 | 297 | 0.7370 [0.6852, 0.7829] | 0.8669 [0.8297, 0.8959] | 0.8052 |
| `verified-wbf-scale-8` | proposer-verifier | verified | 5 | k=4/pt=0.15 | 285 | 0.7219 [0.6677, 0.7728] | 0.8775 [0.8357, 0.9088] | 0.8133 |
| `wbf-canonical` | consensus | wbf | 5 | k=4 | 349 | 0.6796 [0.6151, 0.7341] | not supplied | 0.6380 |
| `wbf-plus-hp` | consensus | wbf | 5 | k=4 | 344 | 0.6727 [0.6172, 0.7267] | not supplied | 0.6654 |
| `wbf-pure-positive-canon` | consensus | wbf | 5 | k=4 | 373 | 0.6590 [0.6018, 0.7097] | not supplied | 0.6200 |
| `wbf-scale-16` | consensus | wbf | 5 | k=4 | 325 | 0.6894 [0.6282, 0.7450] | not supplied | 0.7059 |
| `wbf-scale-32` | consensus | wbf | 5 | k=4 | 345 | 0.6657 [0.6063, 0.7167] | not supplied | 0.6950 |
| `wbf-scale-4` | consensus | wbf | 5 | k=4 | 332 | 0.7373 [0.6839, 0.7842] | not supplied | 0.7062 |
| `wbf-scale-8` | consensus | wbf | 5 | k=4 | 324 | 0.6998 [0.6440, 0.7509] | not supplied | 0.7302 |

Buffers on file (metres), by how many conditions carry that set:

- 14 condition(s): 20
- 3 condition(s): 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 75, 100, 125, 150

Tile-level MCC is on file for 17 of 17 condition(s).

### 5.4 Waived evaluations (50, 2 distinct reason(s))

Scored evaluations under this run that no condition claims, each waived in `results/run-conditions.json` rather than left silent. Grouped by identical reason; where a reason covers more than 12 paths the first 12 are named and the decomposition carries the rest.

- **47 evaluation(s)** — not supplied — a bare-string entry, written before the waiver register carried reasons
  - `results/condition-scoring-backfill-2026-05-30/h8-v2-scale4-t0.25/evaluation.json`
  - `results/condition-scoring-backfill-2026-05-30/h8-v2-scale4-vt4-pt0.10/evaluation.json`
  - `results/condition-scoring-backfill-2026-05-30/h8-v2-wbf-scale4-vt4-pt0.10/evaluation.json`
  - `results/condition-scoring-backfill-2026-05-30/h8-v2-wbf-scale8-vt4-pt0.15/evaluation.json`
  - `results/h8-v2/greedy/canonical/t1/evaluation.json`
  - `results/h8-v2/greedy/canonical/t2/evaluation.json`
  - `results/h8-v2/greedy/canonical/t3/evaluation.json`
  - `results/h8-v2/greedy/canonical/t4/evaluation.json`
  - `results/h8-v2/greedy/canonical/t5/evaluation.json`
  - `results/h8-v2/greedy/plus-hp/t1/evaluation.json`
  - `results/h8-v2/greedy/plus-hp/t2/evaluation.json`
  - `results/h8-v2/greedy/plus-hp/t3/evaluation.json`
  - … and 35 more under the same waiver (full list in `results/run-conditions.json`, this run's `_ignored_evals`)
- **3 evaluation(s)** — uplift-supplement K=1 anchor (planning/uplift-supplement-2026-08-28.md; scored 5bd514542): an input to the supplement's pairing tables, on the reference of the stratum it pairs with; not a registered condition and not cited by the paper. Waived by PI ruling 2026-09-07 (planning/reference-revision-2026-09-06.md, register-verifier debt).
  - `results/uplift-supplement/k1-gapfill/h8-v2__verified-scale-4/evaluation.json`
  - `results/uplift-supplement/k1-gapfill/h8-v2__verified-wbf-scale-4/evaluation.json`
  - `results/uplift-supplement/k1-gapfill/h8-v2__verified-wbf-scale-8/evaluation.json`

## 6. Analyses that read this run (4)

A run is linked to an analysis when the analysis's `conditions_compared` names one of this run's conditions. *Cells* is how many of the analysis's compared conditions come from this run, out of its total. *Signed* is the register's `manually_verified_at` stamp.

| Analysis | Cells | Type | Hypotheses | Registration | Paper section | Deviations | Signed | Output |
|---|---|---|---|---|---|---|---|---|
| `family-bh-fdr-confirmatory` | 2 of 12 | comparison | `H1`, `H2`, `H3`, `H4`, `H5`, `H7`, `H8` | confirmatory-with-deviation | Results | `E28`, `E30`, `E36`, `E41`, `E45`, `E51`, `E53`, `E54`, `E58`, `E59`, `E60`, `E64` | 2026-08-14T23:32:30Z | `results/family-fdr/family_fdr.json` |
| `sensitivity-mde-2026-08-28` | 17 of 17 | diagnostic | `H8`, `H9`, `H10`, `H12` | post-hoc | Appendix | — | 2026-08-28T12:22:08Z | `results/sensitivity-mde-2026-08-28/sensitivity.json` |
| `uplift-supplement-flatten` | 17 of 441 | diagnostic | — | post-hoc | Appendix | — | 2026-09-10T22:55:40Z | `results/uplift-supplement/conditions.csv` |
| `verifier-uplift-pairing` | 3 of 170 | comparison | `H2` | post-hoc | Appendix | — | 2026-09-12T06:04:30Z | `results/uplift-supplement/verifier-uplift.csv` |

## 7. Findings documents (0)

No findings document on disk is named by an analysis that reads this run: a findings write-up for this run is **not supplied** from the register. § 6's `output_path` column gives each analysis's artefact directory.

## 8. Protocol errata

### 8.1 Registered as deviations (12)

Listed in the `deviations` field of an analysis that reads this run:

- **E28** — H5 instruction text adapted for Phase 2d (HN image references removed, OFAT simplification)
- **E30** — Phase 2e tests 4 ordering conditions instead of preregistered 3
- **E36** — 340-tile production retest replaces 60-tile holdout evaluation (corrected 2026-07-30)
- **E41** — 384px tile size and full evaluation set used for Pro comparison
- **E45** — Unregistered inference method — tile-swap permutation testing (corrected 2026-07-28; originally "test statistic changed from macro-average to micro-average")
- **E51** — H8 library composition re-run under production carry-forward (384 px / v2 pipeline)
- **E53** — Phase 3a-HIGH image track moved from 512 px (Era 1) to 384 px (Era 2)
- **E54** — Bootstrap iteration count — preregistered 1 000 for primary F1, post-hoc 10 000 for narrow-effect analyses
- **E58** — Registered H2 proposer prompt (`propose\_brief`) never used — `detect\_brief-text` substituted in all PV experiments
- **E59** — H2 Condition C (fine-to-coarse) — registered confirmatory condition never executed, never formally dropped
- **E60** — H7 escalation trigger — fired as written on the expanded corpus; escalation judged uninformative and not run
- **E64** — Five internal contradictions in the lodged registration — operative readings adopted, reasoning stated, post-facto status acknowledged

### 8.2 Mentioning this run (1)

The entry's text names this run id or its directory path. A mention is a pointer to read the entry, not a claim that the erratum is about this run:

- **E56** — Verifier probability-threshold operating points are in-sample (test-set-selected), not calibrated

## 9. Documents and structure in the run directory

| Document class | Filename | Count |
|---|---|---:|
| per-pass/per-run intent | `experiment_intent.md` | 35 |

These classes are in Revision-Policy scope going forward (`docs/methodology/output-directory-standard.md` § "Documents in Revision Policy Scope").

### 9.1 Registered pools

| Proposer pool | Modality | Path within the run directory |
|---|---|---|
| `canonical` | image | `canonical` |
| `plus-hp` | image | `plus-hp` |
| `pure-positive-canon` | image | `pure-positive-canon` |
| `scale-16` | image | `scale-16` |
| `scale-32` | image | `scale-32` |
| `scale-4` | image | `scale-4` |
| `scale-8` | image | `scale-8` |

3 registered verifier-pass directory/directories; see `results/run-conditions.json` for the full list.

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
- `inputs/vectors/bounds/384/h10_test_bounds.geojson`

Regenerate and drift-check with:

```bash
python3 scripts/generate_run_reports.py --all --write
python3 scripts/generate_run_reports.py --check
```
