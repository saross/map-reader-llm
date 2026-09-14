<!-- GENERATED FILE — do not hand-edit. Projected from the registered manifests by scripts/generate_run_reports.py v1.1.0. Hand edits are destroyed on the next regeneration and fail the --check drift guard. -->
# Post-run report — verifier-robustness

> **GENERATED FILE — do not hand-edit.** Projected from the registered manifests by `scripts/generate_run_reports.py` v1.1.0 at source commit `5570447b9`. This file carries provenance instead of a hand changelog, per the PI ruling of 2026-09-11 recorded in `docs/methodology/output-directory-standard.md` § "Documents in Revision Policy Scope": a generated document's history is its inputs' and its generator's git history, so "is this current?" is answered by the `--check` drift guard and its tier-1 test, not by a changelog. Regenerate after any manifest rebuild; put before/after notes in the commit message.

**Directory**: `outputs/verifier-robustness` · **Registry status**: active · **Purpose**: Verifier-robustness programme: determinism (n=1 vindicated), proposer-input band, temperature/thinking matrix, model roles, compute allocation, operational maximum, pass-budget Pareto. Meta-rule: on a within-noise tie, take the cheaper config.

## 1. Identity and registration

| Field | Value |
|---|---|
| Run id | `verifier-robustness` |
| Directory | `outputs/verifier-robustness` |
| Registry status | active |
| Purpose | Verifier-robustness programme: determinism (n=1 vindicated), proposer-input band, temperature/thinking matrix, model roles, compute allocation, operational maximum, pass-budget Pareto. Meta-rule: on a within-noise tie, take the cheaper config. |
| Run type (derived) | proposer-verifier |
| Primary hypothesis | H2 |
| Also informs | `H3` |
| Headline condition | not supplied |
| Headline rationale | Deliberately none — NO new champion. The carry-forward headline pv-diag-384::verified-adv-text-consensus-16of30 (0.890) stands: the operational maximum here (verified-384-16of30-t0-3-n5-opmax, 0.8951) is NOT significant over it (paired tile-swap permutation p=0.363, results/verifier-robustness/opmax\_vs\_headline\_permutation.json), so per the cost meta-rule (Obs 357) it is a numerical high only. |
| Historical aliases | — |
| Working-notes Obs | — |
| Registry notes | Verifier-robustness programme (Sessions 109-110, ~$53 flex): Stage 1 N=5 determinism on the 384/256 1-of-5 unions (T=0.0), Stage 2 temperature snowball (ge3of5 band, stalled at T=0.3), Stage 3 thinking x temperature matrix + the 16of30 operational maximum. Verifier-only API run; ALL proposer pools are cross-run (pv-diag-384 / pv-diag-256, recorded per-condition via source\_run). Findings: results/verifier-robustness/verifier-robustness-findings.md. |

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

No pass rows in `results/passes-manifest.json` for this run. A run is decomposed into passes only where its proposer/verifier metas were materialised as resolvable pass files; where they were not, the decomposition records pools and conditions without passes. See § 5 for the registered conditions and § 1 for the registry note.

## 4. Token load and recorded cost

No pass rows, so no recorded token load. not supplied: this run's spend is not reconstructable from the passes manifest.

Audit and reconciliation reports whose text names this run or its directory — consult these for audited figures; a mention is a pointer, not a claim that the report audits this run in full:

- `reports/token-load-audit-2026-06-12.md`
- `reports/r7-gaps-deltas-2026-09-11.md`

## 5. Registered conditions (14)

F1@20 m is the preregistered localisation buffer; F1@50 m is the deployment working buffer. Confidence intervals are those the evaluation recorded (method, iterations and seed per condition in the manifest). `mcc` is tile-level. A cell reading *not supplied* means the metric is absent from the condition's evaluation, not that it is zero; a tile-MCC reading *withheld* means the tile-join invariant REFUSED that condition's per-tile table on this frame, so the tile metrics and the bootstrap intervals were not computed — the condition's whole-frame F1 is unaffected and is reported in full (PI ruling 2026-09-13; the named reason is in the condition's manifest row).

| Condition | Architecture | Aggregation | Passes | Operating point | Detections | F1@20 m [CI] | F1@50 m [CI] | Tile MCC |
|---|---|---|---:|---|---:|---|---|---:|
| `verified-256-ge3of5-t0-3-n5` | proposer-verifier | verified | 5 | k=5/pt=0.2 | 401 | 0.8582 [0.8247, 0.8874] | 0.8702 [0.8385, 0.8967] | 0.7301 |
| `verified-256-union-t0-0-n5` | proposer-verifier | verified | 5 | k=5/pt=0.15 | 398 | 0.8637 [0.8296, 0.8919] | 0.8758 [0.8440, 0.9020] | 0.7497 |
| `verified-384-16of30-t0-3-n5-opmax` | proposer-verifier | verified | 1 | pt=0.15 | 423 | 0.8951 [0.8663, 0.9182] | 0.9161 [0.8912, 0.9361] | 0.7941 |
| `verified-384-16of30-t0-3-n5-opmax-era2b` | proposer-verifier | verified | 1 | pt=0.15 | 423 | 0.8951 [0.8663, 0.9182] | 0.9161 [0.8912, 0.9361] | 0.7941 |
| `verified-384-ge3of5-t0-3-high-n5` | proposer-verifier | verified | 5 | k=4/pt=0.3 | 398 | 0.8764 [0.8453, 0.9031] | 0.9028 [0.8750, 0.9253] | 0.7890 |
| `verified-384-ge3of5-t0-3-high-n5-era2b` | proposer-verifier | verified | 5 | k=4/pt=0.3 | 398 | 0.8764 [0.8453, 0.9031] | 0.9028 [0.8750, 0.9253] | 0.7890 |
| `verified-384-ge3of5-t0-3-n5` | proposer-verifier | verified | 5 | k=4/pt=0.15 | 398 | 0.8739 [0.8426, 0.9009] | 0.9004 [0.8725, 0.9225] | 0.7713 |
| `verified-384-ge3of5-t0-3-n5-era2b` | proposer-verifier | verified | 5 | k=4/pt=0.15 | 398 | 0.8739 [0.8426, 0.9009] | 0.9004 [0.8725, 0.9225] | 0.7713 |
| `verified-384-ge3of5-t0-7-high-n5` | proposer-verifier | verified | 5 | k=4/pt=0.4 | 398 | 0.8739 [0.8432, 0.9007] | 0.9004 [0.8725, 0.9227] | 0.7927 |
| `verified-384-ge3of5-t0-7-high-n5-era2b` | proposer-verifier | verified | 5 | k=4/pt=0.4 | 398 | 0.8739 [0.8432, 0.9007] | 0.9004 [0.8725, 0.9227] | 0.7927 |
| `verified-384-ge3of5-t0-7-n5` | proposer-verifier | verified | 5 | k=4/pt=0.2 | 394 | 0.8709 [0.8393, 0.8982] | 0.8951 [0.8660, 0.9185] | 0.7713 |
| `verified-384-ge3of5-t0-7-n5-era2b` | proposer-verifier | verified | 5 | k=4/pt=0.2 | 394 | 0.8709 [0.8393, 0.8982] | 0.8951 [0.8660, 0.9185] | 0.7713 |
| `verified-384-union-t0-0-n5` | proposer-verifier | verified | 5 | k=4/pt=0.15 | 402 | 0.8722 [0.8406, 0.8991] | 0.8984 [0.8704, 0.9214] | 0.7621 |
| `verified-384-union-t0-0-n5-era2b` | proposer-verifier | verified | 5 | k=4/pt=0.15 | 402 | 0.8722 [0.8406, 0.8991] | 0.8984 [0.8704, 0.9214] | 0.7621 |

Buffers on file (metres), by how many conditions carry that set:

- 14 condition(s): 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 75, 100, 125, 150

Tile-level MCC is on file for 14 of 14 condition(s).

### 5.1 Condition caveats (6 condition(s), 6 distinct caveat(s))

Grouped by identical text: a caveat written once for a family of sibling cells is reproduced once, with every cell it applies to named. Nothing is elided.

- `verified-384-16of30-t0-3-n5-opmax-era2b`
  GS Era-2 verified board cell (planning/gs-era2-verified-board-2026-09-08.md, PI frame ruling 2026-09-09): the registered cell verified-384-16of30-t0-3-n5-opmax re-scored with its committed recipe on the Era-2 ∩ B-union frame (era2-b-487); the committed evaluation on full\_evaluation\_bounds.geojson stays the row's record.
- `verified-384-ge3of5-t0-3-high-n5-era2b`
  GS Era-2 verified board cell (planning/gs-era2-verified-board-2026-09-08.md, PI frame ruling 2026-09-09): the registered cell verified-384-ge3of5-t0-3-high-n5 re-scored with its committed recipe on the Era-2 ∩ B-union frame (era2-b-487); the committed evaluation on full\_evaluation\_bounds.geojson stays the row's record.
- `verified-384-ge3of5-t0-3-n5-era2b`
  GS Era-2 verified board cell (planning/gs-era2-verified-board-2026-09-08.md, PI frame ruling 2026-09-09): the registered cell verified-384-ge3of5-t0-3-n5 re-scored with its committed recipe on the Era-2 ∩ B-union frame (era2-b-487); the committed evaluation on full\_evaluation\_bounds.geojson stays the row's record.
- `verified-384-ge3of5-t0-7-high-n5-era2b`
  GS Era-2 verified board cell (planning/gs-era2-verified-board-2026-09-08.md, PI frame ruling 2026-09-09): the registered cell verified-384-ge3of5-t0-7-high-n5 re-scored with its committed recipe on the Era-2 ∩ B-union frame (era2-b-487); the committed evaluation on full\_evaluation\_bounds.geojson stays the row's record.
- `verified-384-ge3of5-t0-7-n5-era2b`
  GS Era-2 verified board cell (planning/gs-era2-verified-board-2026-09-08.md, PI frame ruling 2026-09-09): the registered cell verified-384-ge3of5-t0-7-n5 re-scored with its committed recipe on the Era-2 ∩ B-union frame (era2-b-487); the committed evaluation on full\_evaluation\_bounds.geojson stays the row's record.
- `verified-384-union-t0-0-n5-era2b`
  GS Era-2 verified board cell (planning/gs-era2-verified-board-2026-09-08.md, PI frame ruling 2026-09-09): the registered cell verified-384-union-t0-0-n5 re-scored with its committed recipe on the Era-2 ∩ B-union frame (era2-b-487); the committed evaluation on full\_evaluation\_bounds.geojson stays the row's record.

### 5.2 Scope overrides (8 condition(s), 2 distinct frame(s))

These conditions are scored on a frame other than the run's nominal scope in § 2 — the 327-vs-487 leakage trap the verifier exists to catch, disclosed per condition:

- `verified-384-16of30-t0-3-n5-opmax-era2b`, `verified-384-ge3of5-t0-3-high-n5-era2b`, `verified-384-ge3of5-t0-3-n5-era2b`, `verified-384-ge3of5-t0-7-high-n5-era2b`, `verified-384-ge3of5-t0-7-n5-era2b`, `verified-384-union-t0-0-n5-era2b`
  bounds\_path = inputs/vectors/bounds/384/era2\_b\_intersection\_bounds.geojson, calibration\_set\_id = None, n\_calibration\_tiles = None, n\_test\_tiles = 487, test\_set\_id = era2-b-487
- `verified-256-ge3of5-t0-3-n5`, `verified-256-union-t0-0-n5`
  bounds\_path = inputs/vectors/bounds/256/full\_evaluation\_bounds.geojson, calibration\_set\_id = None, n\_calibration\_tiles = None, n\_test\_tiles = 1032, test\_set\_id = px256-1032

### 5.3 Decomposition note

Verbatim from `results/run-conditions.json` — the hand-authored record of how this run was decomposed and what was adjudicated:

> Verifier-only run: re-verifies pv-diag-384 / pv-diag-256 proposer pools under varied verifier configs (S109-110). One citable condition per verifier config at its best F1@20m operating point (the settled decomposition pattern); the full sweeps live in results/verifier-robustness/robustness\_grid\_\*.json. NO new champion (see run-facts headline\_rationale).

### 5.4 Waived evaluations (14, 7 distinct reason(s))

Scored evaluations under this run that no condition claims, each waived in `results/run-conditions.json` rather than left silent. Grouped by identical reason; where a reason covers more than 12 paths the first 12 are named and the decomposition carries the rest.

- **8 evaluation(s)** — uplift-supplement pairing/gap-fill anchor (planning/uplift-supplement-2026-08-28.md): an input to the supplement's pairing tables, scored on the reference, buffer, and frame of the stratum it pairs with; not a registered condition and not cited by the paper. Waived by PI ruling 2026-09-07 (planning/reference-revision-2026-09-06.md, register-verifier debt).
  - `results/uplift-supplement/verifier-pairing/verifier-robustness__verified-256-ge3of5-t0-3-n5/evaluation.json`
  - `results/uplift-supplement/verifier-pairing/verifier-robustness__verified-256-union-t0-0-n5/evaluation.json`
  - `results/uplift-supplement/verifier-pairing/verifier-robustness__verified-384-16of30-t0-3-n5-opmax/evaluation.json`
  - `results/uplift-supplement/verifier-pairing/verifier-robustness__verified-384-ge3of5-t0-3-high-n5/evaluation.json`
  - `results/uplift-supplement/verifier-pairing/verifier-robustness__verified-384-ge3of5-t0-3-n5/evaluation.json`
  - `results/uplift-supplement/verifier-pairing/verifier-robustness__verified-384-ge3of5-t0-7-high-n5/evaluation.json`
  - `results/uplift-supplement/verifier-pairing/verifier-robustness__verified-384-ge3of5-t0-7-n5/evaluation.json`
  - `results/uplift-supplement/verifier-pairing/verifier-robustness__verified-384-union-t0-0-n5/evaluation.json`
- **1 evaluation(s)** — GS Era-2 board gate G2 (planning/gs-era2-verified-board-2026-09-08.md): verified-384-16of30-t0-3-n5-opmax's committed recipe re-run on its committed frame with a 200-draw bootstrap to prove the evaluator reproduces the committed evaluation; a gate artefact, not a condition.
  - `results/leaderboard/era2/gs-era2-verified-board-2026-09-10/g2/verifier-robustness__verified-384-16of30-t0-3-n5-opmax/evaluation.json`
- **1 evaluation(s)** — GS Era-2 board gate G2 (planning/gs-era2-verified-board-2026-09-08.md): verified-384-ge3of5-t0-3-high-n5's committed recipe re-run on its committed frame with a 200-draw bootstrap to prove the evaluator reproduces the committed evaluation; a gate artefact, not a condition.
  - `results/leaderboard/era2/gs-era2-verified-board-2026-09-10/g2/verifier-robustness__verified-384-ge3of5-t0-3-high-n5/evaluation.json`
- **1 evaluation(s)** — GS Era-2 board gate G2 (planning/gs-era2-verified-board-2026-09-08.md): verified-384-ge3of5-t0-3-n5's committed recipe re-run on its committed frame with a 200-draw bootstrap to prove the evaluator reproduces the committed evaluation; a gate artefact, not a condition.
  - `results/leaderboard/era2/gs-era2-verified-board-2026-09-10/g2/verifier-robustness__verified-384-ge3of5-t0-3-n5/evaluation.json`
- **1 evaluation(s)** — GS Era-2 board gate G2 (planning/gs-era2-verified-board-2026-09-08.md): verified-384-ge3of5-t0-7-high-n5's committed recipe re-run on its committed frame with a 200-draw bootstrap to prove the evaluator reproduces the committed evaluation; a gate artefact, not a condition.
  - `results/leaderboard/era2/gs-era2-verified-board-2026-09-10/g2/verifier-robustness__verified-384-ge3of5-t0-7-high-n5/evaluation.json`
- **1 evaluation(s)** — GS Era-2 board gate G2 (planning/gs-era2-verified-board-2026-09-08.md): verified-384-ge3of5-t0-7-n5's committed recipe re-run on its committed frame with a 200-draw bootstrap to prove the evaluator reproduces the committed evaluation; a gate artefact, not a condition.
  - `results/leaderboard/era2/gs-era2-verified-board-2026-09-10/g2/verifier-robustness__verified-384-ge3of5-t0-7-n5/evaluation.json`
- **1 evaluation(s)** — GS Era-2 board gate G2 (planning/gs-era2-verified-board-2026-09-08.md): verified-384-union-t0-0-n5's committed recipe re-run on its committed frame with a 200-draw bootstrap to prove the evaluator reproduces the committed evaluation; a gate artefact, not a condition.
  - `results/leaderboard/era2/gs-era2-verified-board-2026-09-10/g2/verifier-robustness__verified-384-union-t0-0-n5/evaluation.json`

## 6. Analyses that read this run (8)

A run is linked to an analysis when the analysis's `conditions_compared` names one of this run's conditions. *Cells* is how many of the analysis's compared conditions come from this run, out of its total. *Signed* is the register's `manually_verified_at` stamp.

| Analysis | Cells | Type | Hypotheses | Registration | Paper section | Deviations | Signed | Output |
|---|---|---|---|---|---|---|---|---|
| `gs-era2-verified-board-2026-09-10` | 6 of 103 | leaderboard | `H2`, `H1` | post-hoc | Results | — | 2026-09-12T06:04:30Z | `results/leaderboard/era2/gs-era2-verified-board-2026-09-10/tiering_20m.json` |
| `min-vs-high-thinking-pv` | 1 of 7 | leaderboard | `H2`, `H3` | post-hoc | Results | `E56`, `E62` | 2026-06-12T06:59:01Z | `results/verifier-robustness` |
| `null-exemplar-sensitivity-2026-09-13` | 6 of 235 | comparison | — | post-hoc | Appendix | — | not supplied | `results/null-exemplar-sensitivity-2026-09-13/findings.md` |
| `pass-budget-pareto` | 2 of 5 | leaderboard | `H2`, `H3` | post-hoc | Results | `E56`, `E62` | 2026-06-12T06:59:01Z | `results/verifier-robustness/pareto` |
| `pass-budget-pareto-v2` | 2 of 7 | leaderboard | `H2`, `H3` | post-hoc | Results | `E56`, `E62` | 2026-09-12T09:03:09Z | `results/verifier-robustness/pareto` |
| `uplift-supplement-flatten` | 8 of 441 | diagnostic | — | post-hoc | Appendix | — | 2026-09-10T22:55:40Z | `results/uplift-supplement/conditions.csv` |
| `verifier-robustness-matrix` | 5 of 6 | leaderboard | `H2` | post-hoc | Results | `E56`, `E62` | 2026-06-12T06:59:01Z | `results/verifier-robustness` |
| `verifier-uplift-pairing` | 8 of 170 | comparison | `H2` | post-hoc | Appendix | — | 2026-09-12T06:04:30Z | `results/uplift-supplement/verifier-uplift.csv` |

## 7. Findings documents (2)

| Document | Named by |
|---|---|
| `results/null-exemplar-sensitivity-2026-09-13/findings.md` | `null-exemplar-sensitivity-2026-09-13` |
| `results/verifier-robustness/verifier-robustness-findings.md` | `verifier-robustness-matrix` |

## 8. Protocol errata

### 8.1 Registered as deviations (2)

Listed in the `deviations` field of an analysis that reads this run:

- **E56** — Verifier probability-threshold operating points are in-sample (test-set-selected), not calibrated
- **E62** — Three unregistered proposer-verifier extension studies (`flash35-pv-2x2`, `pv-diag-256`, `verifier-robustness`) and four unregistered verifier-parameter levels — additional exploratory extensions of the registered PV contingency

### 8.2 Mentioning this run (2)

The entry's text names this run id or its directory path. A mention is a pointer to read the entry, not a claim that the erratum is about this run:

- **E69** — Unregistered Flash-verifier thinking levels in `pv-diag-384` (MEDIUM on six conditions, HIGH on one) — a deliberate exploratory verifier-variant matrix
- **E83** — Tier-1 membership was decided by an order-dependent sequential rule, not by the clique its docstring promised — eight boards' tie sets revised to Hsu MCB, including one that published a sole leader it does not have

## 9. Documents and structure in the run directory

| Document class | Filename | Count |
|---|---|---:|
| per-pass/per-run intent | `experiment_intent.md` | 1 |

These classes are in Revision-Policy scope going forward (`docs/methodology/output-directory-standard.md` § "Documents in Revision Policy Scope").

### 9.1 Registered pools

8 registered verifier-pass directory/directories; see `results/run-conditions.json` for the full list.

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
- `inputs/vectors/bounds/384/full_evaluation_bounds.geojson`

Regenerate and drift-check with:

```bash
python3 scripts/generate_run_reports.py --all --write
python3 scripts/generate_run_reports.py --check
```
