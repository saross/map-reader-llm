<!-- GENERATED FILE — do not hand-edit. Projected from the registered manifests by scripts/generate_run_reports.py v1.1.0. Hand edits are destroyed on the next regeneration and fail the --check drift guard. -->
# Post-run report — e47-propose-brief

> **GENERATED FILE — do not hand-edit.** Projected from the registered manifests by `scripts/generate_run_reports.py` v1.1.0 at source commit `9f5fec777`. This file carries provenance instead of a hand changelog, per the PI ruling of 2026-09-11 recorded in `docs/methodology/output-directory-standard.md` § "Documents in Revision Policy Scope": a generated document's history is its inputs' and its generator's git history, so "is this current?" is answered by the `--check` drift guard and its tier-1 test, not by a changelog. Regenerate after any manifest rebuild; put before/after notes in the commit message.

**Directory**: `outputs/h11/e47-propose-brief` · **Registry status**: active · **Purpose**: not supplied

## 1. Identity and registration

| Field | Value |
|---|---|
| Run id | `e47-propose-brief` |
| Directory | `outputs/h11/e47-propose-brief` |
| Registry status | active |
| Purpose | not supplied |
| Run type (derived) | mixed |
| Primary hypothesis | H11 |
| Also informs | — |
| Headline condition | not supplied |
| Headline rationale | not supplied |
| Historical aliases | `Era 2` |
| Working-notes Obs | — |
| Registry notes | H11 (propose-brief). |

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
| `propose_brief-text` | 1 | gemini-3-flash-preview | gemini-3-flash-preview | text | high | 0.7 | ok | 487 | not supplied | 0 |
| `propose_brief-text` | 2 | gemini-3-flash-preview | gemini-3-flash-preview | text | high | 0.7 | ok | 487 | not supplied | 0 |
| `propose_brief-text` | 3 | gemini-3-flash-preview | gemini-3-flash-preview | text | high | 0.7 | ok | 487 | not supplied | 0 |
| `propose_brief-text` | 4 | gemini-3-flash-preview | gemini-3-flash-preview | text | high | 0.7 | ok | 487 | 487 | 388 |
| `propose_brief-text` | 5 | gemini-3-flash-preview | gemini-3-flash-preview | text | high | 0.7 | ok | 487 | 487 | 473 |

### 3.2 Verifier passes (3)

| Pool | Pass | Model used | Modality | Thinking | Temp | Status | Candidates verified | Retries |
|---|---:|---|---|---|---:|---|---:|---:|
| `verified-flash-high-text-1of5` | 1 | gemini-3-flash-preview | text | minimal | 0.0 | ok | 57 | 0 |
| `verified-flash-high-text-1of5-recovery-2026-09-08` | 1 | gemini-3-flash-preview | text | minimal | 0.0 | ok | 4149 | 2 |
| `verified-text-baseline` | 1 | gemini-3-flash-preview | text | minimal | 0.0 | ok | 1180 | 0 |

Verifier rows report no tile count by design: verifier pass: operates on candidate crops, not tiles. The verifier meta records candidate ids (cand\_NNNN) in execution\_stats.completed\_items and candidate API items in per\_item\_metadata, so no tile-scale record exists to report. Completed crop count is in n\_candidates\_verified. (E71 Defect 2 / GAP-8, resolved E72 2026-08-02.)

## 4. Token load and recorded cost

| Field | Value |
|---|---|
| Passes on file | 8 |
| Input tokens (billed) | 11,138,456 |
| Input tokens (cached) | 0 |
| Output tokens | 1,069,452 |
| Thinking tokens | 2,853,033 |
| Total tokens | 15,060,941 |
| Passes with no token record | 0 |
| Sum of recorded `cost_usd` | US$8.7776 over 8 of 8 pass(es) |
| Passes with no `cost_usd` | 0 |
| Summed wall clock | 0.96 h over 8 pass(es) |

> **The recorded cost is NOT this run's cost.** Each `cost_usd` above is the pass meta's own `cost_estimate.total_cost_usd`, lifted verbatim by `scripts/generate_post_run_report.py`. The token-load audit of 2026-06-12 established that those self-reported estimates price at STANDARD rates although the audited runs executed at `--service-tier flex` (half price) and omit thinking tokens although Gemini bills thinking at the output rate (`reports/token-load-audit-2026-06-12.md` § 1, § 2). The sum is reproduced here as the recorded figure and as an input to a reconciliation, not as a total to cite.

No cost audit on file names this run or its directory: an independently audited cost for this run is **not supplied**. The four audits checked are `reports/token-load-audit-2026-06-12.md`, `reports/r7-gaps-deltas-2026-09-11.md`, `reports/k-ladder-phase2-deltas-2026-09-12.md`, `reports/billing-reconciliation-2026-09-11.md`.

## 5. Registered conditions (12)

F1@20 m is the preregistered localisation buffer; F1@50 m is the deployment working buffer. Confidence intervals are those the evaluation recorded (method, iterations and seed per condition in the manifest). `mcc` is tile-level. A cell reading *not supplied* means the metric is absent from the condition's evaluation, not that it is zero; a tile-MCC reading *withheld* means the tile-join invariant REFUSED that condition's per-tile table on this frame, so the tile metrics and the bootstrap intervals were not computed — the condition's whole-frame F1 is unaffected and is reported in full (PI ruling 2026-09-13; the named reason is in the condition's manifest row).

| Condition | Architecture | Aggregation | Passes | Operating point | Detections | F1@20 m [CI] | F1@50 m [CI] | Tile MCC |
|---|---|---|---:|---|---:|---|---|---:|
| `baseline-single-pass` | single-pass | none | 1 | — | 1180 | 0.4706 [0.4157, 0.5273] | 0.4929 [0.4381, 0.5498] | 0.0101 |
| `consensus-1of5` | consensus | consensus | 5 | k=1 | 4149 | 0.1798 [0.1502, 0.2137] | 0.1859 [0.1556, 0.2206] | 0.0882 |
| `consensus-2of5` | consensus | consensus | 5 | k=2 | 1537 | 0.4128 [0.3606, 0.4657] | 0.4270 [0.3741, 0.4816] | 0.1971 |
| `consensus-3of5` | consensus | consensus | 5 | k=3 | 998 | 0.5471 [0.4899, 0.6015] | 0.5666 [0.5089, 0.6218] | 0.3374 |
| `consensus-4of5` | consensus | consensus | 5 | k=4 | 699 | 0.6543 [0.5986, 0.7047] | 0.6684 [0.6132, 0.7183] | 0.4049 |
| `consensus-5of5` | consensus | consensus | 5 | k=5 | 455 | 0.7326 [0.6843, 0.7755] | 0.7461 [0.6984, 0.7873] | 0.5262 |
| `single-pass-run_1` | single-pass | none | 1 | — | 1614 | 0.3709 [0.3221, 0.4234] | 0.3982 [0.3470, 0.4525] | 0.2940 |
| `single-pass-run_2` | single-pass | none | 1 | — | 1755 | 0.3416 [0.2934, 0.3919] | 0.3726 [0.3216, 0.4261] | 0.2347 |
| `single-pass-run_3` | single-pass | none | 1 | — | 1645 | 0.3683 [0.3163, 0.4230] | 0.3942 [0.3408, 0.4497] | 0.2864 |
| `single-pass-run_4` | single-pass | none | 1 | — | 1619 | 0.3544 [0.3056, 0.4046] | 0.3856 [0.3332, 0.4382] | 0.2287 |
| `single-pass-run_4-post-e71` | single-pass | none | 1 | — | 1641 | 0.3613 [0.3121, 0.4119] | 0.3921 [0.3399, 0.4446] | 0.2560 |
| `single-pass-run_5` | single-pass | none | 1 | — | 1694 | 0.3579 [0.3054, 0.4101] | 0.3852 [0.3303, 0.4389] | 0.2977 |

Buffers on file (metres), by how many conditions carry that set:

- 12 condition(s): 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 75, 100, 125, 150

Tile-level MCC is on file for 12 of 12 condition(s).

### 5.3 Decomposition note

Verbatim from `results/run-conditions.json` — the hand-authored record of how this run was decomposed and what was adjudicated:

> Verifier-stage refresh (2026-09-08, S151; card planning/verifier-stage-refresh-2026-09-08.md): first verifier\_passes row. The text-only adversarial v1 stage on the pool's rebuilt vote&gt;=1 consensus (4,149 candidates) at verified/flash-high-text-1of5-recovery-2026-09-08 is complete; the pre-recovery verified/flash-high-text-1of5 stage (4,358 of 4,358 verified, complete after the 2026-05-06 cleanup 6683952ac, never swept) stays unregistered pending a PI call. No condition cites either. Comparison: reports/recovery-consistency-audit-2026-09-08.md § 6.1. | PI ruling 2026-09-08 (S151, 'yes, register'): the April stages verified/flash-high-text-1of5 (4,358 of 4,358, complete after the 2026-05-06 cleanup; the pre-recovery record of the refreshed stage) and verified/text-baseline (the same text-only adversarial v1 verifier on the N=1 propose\_brief pass's 1,180 detections, 2026-04-08) are registered as inventory rows. The 2of5-5of5 directories are CPU-derived vote-threshold subsets of the 1of5 probabilities, not verifier runs, and stay unregistered. No condition cites either. Like-for-like sweep of the April 1of5 stage: results/recovery-reeval-2026-09-08/e47-propose-brief/. | Completeness waivers (2026-09-13, S153 Batch 1 item 2): the five rescore-2026-05-31 consensus\_t{1..5} evaluations are the PRE-RECOVERY scoring of the same consensus geojsons the registered consensus-{1..5}of5 conditions now score at recovery-reeval-2026-09-08; waived with reasons. The pinned-vintage WARN on single-pass-run\_4 is left standing: it is the ruling-3a disclosure working as designed, not a defect. No metric changed.

### 5.4 Waived evaluations (7, 6 distinct reason(s))

Scored evaluations under this run that no condition claims, each waived in `results/run-conditions.json` rather than left silent. Grouped by identical reason; where a reason covers more than 12 paths the first 12 are named and the decomposition carries the rest.

- **2 evaluation(s)** — not supplied — a bare-string entry, written before the waiver register carried reasons
  - `results/rescore-2026-05-31/e47-propose-brief/consensus/flash-high-text-1of5/evaluation.json`
  - `results/rescore-2026-05-31/e47-propose-brief/flash-high-text-n5/propose_brief-text/run_5/detections_propose_brief-text_run05/evaluation.json`
- **1 evaluation(s)** — Superseded pre-recovery scoring. This 2026-05-31 rescore scored outputs/h11/e47-propose-brief/flash-high-text-n5/propose\_brief-text/consensus/consensus\_t1.geojson — the same detections the registered condition consensus-1of5 now scores at results/recovery-reeval-2026-09-08/e47-propose-brief/consensus-1of5/evaluation.json after the E71 dead-tile recovery (99ae28ec4) rewrote the file. Kept as the pre-recovery record per ruling 3a (PI, 2026-09-07); not a second condition.
  - `results/rescore-2026-05-31/e47-propose-brief/flash-high-text-n5/propose_brief-text/consensus/consensus_t1/evaluation.json`
- **1 evaluation(s)** — Superseded pre-recovery scoring. This 2026-05-31 rescore scored outputs/h11/e47-propose-brief/flash-high-text-n5/propose\_brief-text/consensus/consensus\_t2.geojson — the same detections the registered condition consensus-2of5 now scores at results/recovery-reeval-2026-09-08/e47-propose-brief/consensus-2of5/evaluation.json after the E71 dead-tile recovery (99ae28ec4) rewrote the file. Kept as the pre-recovery record per ruling 3a (PI, 2026-09-07); not a second condition.
  - `results/rescore-2026-05-31/e47-propose-brief/flash-high-text-n5/propose_brief-text/consensus/consensus_t2/evaluation.json`
- **1 evaluation(s)** — Superseded pre-recovery scoring. This 2026-05-31 rescore scored outputs/h11/e47-propose-brief/flash-high-text-n5/propose\_brief-text/consensus/consensus\_t3.geojson — the same detections the registered condition consensus-3of5 now scores at results/recovery-reeval-2026-09-08/e47-propose-brief/consensus-3of5/evaluation.json after the E71 dead-tile recovery (99ae28ec4) rewrote the file. Kept as the pre-recovery record per ruling 3a (PI, 2026-09-07); not a second condition.
  - `results/rescore-2026-05-31/e47-propose-brief/flash-high-text-n5/propose_brief-text/consensus/consensus_t3/evaluation.json`
- **1 evaluation(s)** — Superseded pre-recovery scoring. This 2026-05-31 rescore scored outputs/h11/e47-propose-brief/flash-high-text-n5/propose\_brief-text/consensus/consensus\_t4.geojson — the same detections the registered condition consensus-4of5 now scores at results/recovery-reeval-2026-09-08/e47-propose-brief/consensus-4of5/evaluation.json after the E71 dead-tile recovery (99ae28ec4) rewrote the file. Kept as the pre-recovery record per ruling 3a (PI, 2026-09-07); not a second condition.
  - `results/rescore-2026-05-31/e47-propose-brief/flash-high-text-n5/propose_brief-text/consensus/consensus_t4/evaluation.json`
- **1 evaluation(s)** — Superseded pre-recovery scoring. This 2026-05-31 rescore scored outputs/h11/e47-propose-brief/flash-high-text-n5/propose\_brief-text/consensus/consensus\_t5.geojson — the same detections the registered condition consensus-5of5 now scores at results/recovery-reeval-2026-09-08/e47-propose-brief/consensus-5of5/evaluation.json after the E71 dead-tile recovery (99ae28ec4) rewrote the file. Kept as the pre-recovery record per ruling 3a (PI, 2026-09-07); not a second condition.
  - `results/rescore-2026-05-31/e47-propose-brief/flash-high-text-n5/propose_brief-text/consensus/consensus_t5/evaluation.json`

## 6. Analyses that read this run (1)

A run is linked to an analysis when the analysis's `conditions_compared` names one of this run's conditions. *Cells* is how many of the analysis's compared conditions come from this run, out of its total. *Signed* is the register's `manually_verified_at` stamp.

| Analysis | Cells | Type | Hypotheses | Registration | Paper section | Deviations | Signed | Output |
|---|---|---|---|---|---|---|---|---|
| `uplift-supplement-flatten` | 12 of 441 | diagnostic | — | post-hoc | Appendix | — | 2026-09-10T22:55:40Z | `results/uplift-supplement/conditions.csv` |

## 7. Findings documents (0)

No findings document on disk is named by an analysis that reads this run: a findings write-up for this run is **not supplied** from the register. § 6's `output_path` column gives each analysis's artefact directory.

## 8. Protocol errata

### 8.2 Mentioning this run (1)

The entry's text names this run id or its directory path. A mention is a pointer to read the entry, not a claim that the erratum is about this run:

- **E71** — `n\_tiles\_processed` manifest column carries two semantics (dispatched vs completed) plus a verifier-row placeholder (GAP-8) — 15 passes with genuine coverage shortfalls, two live conditions carrying dead tiles as artificial false negatives

## 9. Documents and structure in the run directory

No `experiment_intent.md`, `evaluation.md`, `pre_launch_audit.md` or retrospective report under this directory.

### 9.1 Registered pools

| Proposer pool | Modality | Path within the run directory |
|---|---|---|
| `propose_brief-text` | text | `flash-high-text-n5/propose_brief-text` |

3 registered verifier-pass directory/directories; see `results/run-conditions.json` for the full list.

## 10. Provenance of this report

This report is a projection. Every figure above is read from one of the committed inputs below; nothing is estimated, and a figure that is not on file is written **not supplied** with its reason.

| Field | Value |
|---|---|
| Generator | `scripts/generate_run_reports.py` v1.1.0 |
| Source commit | `9f5fec777` |
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

Regenerate and drift-check with:

```bash
python3 scripts/generate_run_reports.py --all --write
python3 scripts/generate_run_reports.py --check
```
