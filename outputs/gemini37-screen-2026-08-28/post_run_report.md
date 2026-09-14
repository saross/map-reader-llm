<!-- GENERATED FILE — do not hand-edit. Projected from the registered manifests by scripts/generate_run_reports.py v1.1.0. Hand edits are destroyed on the next regeneration and fail the --check drift guard. -->
# Post-run report — gemini37-screen-2026-08-28

> **GENERATED FILE — do not hand-edit.** Projected from the registered manifests by `scripts/generate_run_reports.py` v1.1.0 at source commit `60b07ffcc`. This file carries provenance instead of a hand changelog, per the PI ruling of 2026-09-11 recorded in `docs/methodology/output-directory-standard.md` § "Documents in Revision Policy Scope": a generated document's history is its inputs' and its generator's git history, so "is this current?" is answered by the `--check` drift guard and its tier-1 test, not by a changelog. Regenerate after any manifest rebuild; put before/after notes in the commit message.

**Directory**: `outputs/gemini37-screen-2026-08-28` · **Registry status**: active · **Purpose**: Gemini 3.7 Flash screen on the leading 384 px / 50 % geometry: does a within-vendor model-family step clear the Gemini-3 GS plateau, and in which seat? Predictions G1-G4 committed at PI go (card planning/gemini37-screen-2026-08-28.md). Escalated to K=10 and to two verifier-role swaps (3.7, then 3.8 under card planning/gemini38-screen-2026-09-04.md).

## 1. Identity and registration

| Field | Value |
|---|---|
| Run id | `gemini37-screen-2026-08-28` |
| Directory | `outputs/gemini37-screen-2026-08-28` |
| Registry status | active |
| Purpose | Gemini 3.7 Flash screen on the leading 384 px / 50 % geometry: does a within-vendor model-family step clear the Gemini-3 GS plateau, and in which seat? Predictions G1-G4 committed at PI go (card planning/gemini37-screen-2026-08-28.md). Escalated to K=10 and to two verifier-role swaps (3.7, then 3.8 under card planning/gemini38-screen-2026-09-04.md). |
| Run type (derived) | proposer-verifier |
| Primary hypothesis | not supplied |
| Also informs | `H13` |
| Headline condition | gemini37-screen-2026-08-28::g37-text-k5-verified-swap37-p0.80-k5 |
| Headline rationale | The all-3.7 stack (F1@20 0.9265, tile-MCC 0.8078) — the study's first GS-resolvable model-swap margin (+0.0304 vs the anchor, p = 0.0105) and the only cell in the arc beating the anchor on F1 and MCC together. |
| Historical aliases | — |
| Working-notes Obs | — |
| Registry notes | Gemini 3.7 Flash GS screen (card planning/gemini37-screen-2026-08-28.md; predictions G1-G4 committed at PI go): detect\_brief-text on the leading 384/50% geometry, K=5 then an approved escalation to K=10, plus two verifier-role swaps over the same K=5 union (gemini-3.7-flash, and gemini-3.8-flash under card planning/gemini38-screen-2026-09-04.md). Registered S149. |

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

### 3.1 Proposer passes (10)

| Pool | Pass | Model used | Model requested | Modality | Thinking | Temp | Status | Tiles done | Dispatched | Retries |
|---|---:|---|---|---|---|---:|---|---:|---:|---:|
| `g384_ov192_g37` | 1 | gemini-3.7-flash | gemini-3.7-flash | text | low | 0.7 | ok | 1398 | 1398 | 2773 |
| `g384_ov192_g37` | 2 | gemini-3.7-flash | gemini-3.7-flash | text | low | 0.7 | ok | 1398 | 1398 | 2967 |
| `g384_ov192_g37` | 3 | gemini-3.7-flash | gemini-3.7-flash | text | low | 0.7 | ok | 1398 | 1398 | 2819 |
| `g384_ov192_g37` | 4 | gemini-3.7-flash | gemini-3.7-flash | text | low | 0.7 | ok | 1398 | 1398 | 2243 |
| `g384_ov192_g37` | 5 | gemini-3.7-flash | gemini-3.7-flash | text | low | 0.7 | ok | 1398 | 1398 | 1324 |
| `g384_ov192_g37` | 6 | gemini-3.7-flash | gemini-3.7-flash | text | low | 0.7 | ok | 1398 | 1398 | 1016 |
| `g384_ov192_g37` | 7 | gemini-3.7-flash | gemini-3.7-flash | text | low | 0.7 | ok | 1398 | 1398 | 893 |
| `g384_ov192_g37` | 8 | gemini-3.7-flash | gemini-3.7-flash | text | low | 0.7 | ok | 1398 | 1398 | 939 |
| `g384_ov192_g37` | 9 | gemini-3.7-flash | gemini-3.7-flash | text | low | 0.7 | ok | 1398 | 1398 | 1289 |
| `g384_ov192_g37` | 10 | gemini-3.7-flash | gemini-3.7-flash | text | low | 0.7 | ok | 1398 | 1398 | 1650 |

### 3.2 Verifier passes (6)

| Pool | Pass | Model used | Modality | Thinking | Temp | Status | Candidates verified | Retries |
|---|---:|---|---|---|---:|---|---:|---:|
| `g384_ov192_g37-union-k1-verify` | 1 | gemini-3-flash-preview | text | minimal | 0.0 | ok | 640 | 0 |
| `g384_ov192_g37-union-k10-verify` | 1 | gemini-3-flash-preview | text | minimal | 0.0 | ok | 913 | 0 |
| `g384_ov192_g37-union-k3-verify` | 1 | gemini-3-flash-preview | text | minimal | 0.0 | ok | 757 | 0 |
| `g384_ov192_g37-union-k5-verify` | 1 | gemini-3-flash-preview | text | minimal | 0.0 | ok | 791 | 0 |
| `g384_ov192_g37-union-k5-verify-swap37` | 1 | gemini-3.7-flash | text | low | 0.0 | ok | 2 | 14 |
| `g384_ov192_g37-union-k5-verify-swap38` | 1 | gemini-3.8-flash | text | low | 0.0 | ok | 1 | 0 |

Verifier rows report no tile count by design: verifier pass: operates on candidate crops, not tiles. The verifier meta records candidate ids (cand\_NNNN) in execution\_stats.completed\_items and candidate API items in per\_item\_metadata, so no tile-scale record exists to report. Completed crop count is in n\_candidates\_verified. (E71 Defect 2 / GAP-8, resolved E72 2026-08-02.)

## 4. Token load and recorded cost

| Field | Value |
|---|---|
| Passes on file | 16 |
| Input tokens (billed) | 26,524,280 |
| Input tokens (cached) | 0 |
| Output tokens | 1,595,873 |
| Thinking tokens | 3,891,436 |
| Total tokens | 32,011,589 |
| Passes with no token record | 0 |
| Sum of recorded `cost_usd` | US$11.2103 over 16 of 16 pass(es) |
| Passes with no `cost_usd` | 0 |
| Summed wall clock | 9.74 h over 16 pass(es) |

> **The recorded cost is NOT this run's cost.** Each `cost_usd` above is the pass meta's own `cost_estimate.total_cost_usd`, lifted verbatim by `scripts/generate_post_run_report.py`. The token-load audit of 2026-06-12 established that those self-reported estimates price at STANDARD rates although the audited runs executed at `--service-tier flex` (half price) and omit thinking tokens although Gemini bills thinking at the output rate (`reports/token-load-audit-2026-06-12.md` § 1, § 2). The sum is reproduced here as the recorded figure and as an input to a reconciliation, not as a total to cite.

Audit and reconciliation reports whose text names this run or its directory — consult these for audited figures; a mention is a pointer, not a claim that the report audits this run in full:

- `reports/k-ladder-phase2-deltas-2026-09-12.md`
- `reports/billing-reconciliation-2026-09-11.md`

## 5. Registered conditions (11)

F1@20 m is the preregistered localisation buffer; F1@50 m is the deployment working buffer. Confidence intervals are those the evaluation recorded (method, iterations and seed per condition in the manifest). `mcc` is tile-level. A cell reading *not supplied* means the metric is absent from the condition's evaluation, not that it is zero; a tile-MCC reading *withheld* means the tile-join invariant REFUSED that condition's per-tile table on this frame, so the tile metrics and the bootstrap intervals were not computed — the condition's whole-frame F1 is unaffected and is reported in full (PI ruling 2026-09-13; the named reason is in the condition's manifest row).

| Condition | Architecture | Aggregation | Passes | Operating point | Detections | F1@20 m [CI] | F1@50 m [CI] | Tile MCC |
|---|---|---|---:|---|---:|---|---|---:|
| `g37-text-k1-verified-carried-p0.10-k1` | proposer-verifier | verified | 1 | k=1/pt=0.1 | 558 | 0.8338 [0.3684, 0.7709] | 0.8520 [0.4615, 0.8493] | 0.1422 |
| `g37-text-k1-verified-opmax` | proposer-verifier | verified | 1 | k=1/pt=0.15 | 502 | 0.8495 [0.2712, 0.6667] | 0.8709 [0.3333, 0.7317] | 0.1337 |
| `g37-text-k10-verified-carried-p0.10-k10` | proposer-verifier | verified | 10 | k=10/pt=0.1 | 423 | 0.9142 [0.8862, 0.9361] | 0.9377 [0.9147, 0.9550] | 0.7817 |
| `g37-text-k10-verified-carried-p0.10-k10-era2b` | proposer-verifier | verified | 10 | k=10/pt=0.1 | 423 | 0.9068 [0.8783, 0.9293] | 0.9301 [0.9062, 0.9481] | 0.7675 |
| `g37-text-k3-verified-opmax` | proposer-verifier | verified | 3 | k=3/pt=0.1 | 495 | 0.8860 | 0.9011 | withheld |
| `g37-text-k5-verified-carried-p0.10-k5` | proposer-verifier | verified | 5 | k=5/pt=0.1 | 443 | 0.9139 [0.8874, 0.9342] | 0.9277 [0.9049, 0.9453] | 0.7797 |
| `g37-text-k5-verified-carried-p0.10-k5-era2b` | proposer-verifier | verified | 5 | k=5/pt=0.1 | 443 | 0.9066 [0.8792, 0.9279] | 0.9203 [0.8971, 0.9393] | 0.7651 |
| `g37-text-k5-verified-swap37-p0.80-k5` | proposer-verifier | verified | 5 | k=5/pt=0.8 | 429 | 0.9265 [0.9010, 0.9461] | 0.9405 [0.9192, 0.9568] | 0.8078 |
| `g37-text-k5-verified-swap37-p0.80-k5-era2b` | proposer-verifier | verified | 5 | k=5/pt=0.8 | 429 | 0.9190 [0.8929, 0.9393] | 0.9329 [0.9104, 0.9502] | 0.7937 |
| `g37-text-k5-verified-swap38-p0.88-k5` | proposer-verifier | verified | 5 | k=5/pt=0.88 | 421 | 0.9258 [0.8995, 0.9458] | 0.9399 [0.9172, 0.9566] | 0.8218 |
| `g37-text-k5-verified-swap38-p0.88-k5-era2b` | proposer-verifier | verified | 5 | k=5/pt=0.88 | 421 | 0.9182 [0.8913, 0.9389] | 0.9322 [0.9087, 0.9499] | 0.8079 |

Buffers on file (metres), by how many conditions carry that set:

- 11 condition(s): 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 75, 100, 125, 150

Tile-level MCC is on file for 10 of 11 condition(s). Of the 1 without one, 1 is WITHHELD by the tile-join invariant (tile_join_detection_shortfall); its whole-frame F1 is unaffected.

### 5.1 Condition caveats (11 condition(s), 11 distinct caveat(s))

Grouped by identical text: a caveat written once for a family of sibling cells is reproduced once, with every cell it applies to named. Nothing is elided.

- `g37-text-k5-verified-carried-p0.10-k5`
  A1 — the standalone K=5 screen best (F1@20 0.913892, tile-MCC 0.7797, 443 detections) on the K=5 union's own 791-item verification. Distinct from the K=10-vintage ladder N=5 rung (0.913094, 435 detections), which reads the same five passes through the 913-item re-verification and is not registered (PI ruling 4/7).
- `g37-text-k10-verified-carried-p0.10-k10`
  A2 — the approved K=10 escalation (F1@20 0.914219, tile-MCC 0.7817, 423 detections). Five extra proposer passes (~$5.4 billed) bought +0.0003; the ladder's own N5-N10 contrast is -0.0011 at p = 0.7928.
- `g37-text-k5-verified-swap37-p0.80-k5`
  A3 — the all-3.7 stack: the SAME 791 candidates re-verified with gemini-3.7-flash (F1@20 0.926488, P 0.9254 / R 0.9276, tile-MCC 0.8078, 429 detections) for ~$0.9 token-basis. The study's first GS-resolvable model-swap margin (+0.0304 vs the 0.8961 anchor, p = 0.0105). The sweep argmax is a TIE the analysis JSON does not flag: prob\_t 0.80 and 0.85 give identical F1 and 429 detections in swap37/sweep\_20m.csv; the card commits (0.80, k5).
- `g37-text-k1-verified-carried-p0.10-k1`
  CARRIED POINT (the transfer-tax column of ruling R2): prob\_t 0.1, k = K = 1, fixed before this evaluation rather than selected on it. At K = 1 and K = 3 the corpus's two readings of the carried vote threshold coincide (k = K, and the gold-standard stride ladder's 1/3/4/8 shell), so this point is unambiguous; they diverge only at K = 5 and K = 10. K-LADDER PHASE 2 (approved by the PI 2026-09-12 at US$24.84 for 28 rungs; controlling card planning/k-ladder-review-2026-09-11.md, costing reports/k-ladder-phase2-costing-2026-09-12.md row 27, tier D). First-N rung: the union is passes run\_1 of pool outputs/gemini37-screen-2026-08-28/g384\_ov192\_g37, built at US$0 by scripts/merge\_passes.py --passes 1 --sweep (union 640 candidates at vote &gt;= 1, reproducing the costing table's figure of 640 exactly). Verified by one pass of the carried Gemini 3 verifier (ruling R1: no verifier swaps) at real-time flex tier, US$0.4521 on the audited flex basis (input x 0.25 + (output + thinking) x 1.50 per million). NOTE the verify path stamps cost\_basis 'list' with discount 1.0 even under flex and records the tier nowhere, so the stage meta's total\_cost\_usd is about twice the invoice (reports/r7-gaps-deltas-2026-09-11.md § 2.3). Scored on the board frame era2-b-487 with the family's recipe: curator reference, 14 buffers, 10,000 BCa draws, seed 42, MCC.
- `g37-text-k10-verified-carried-p0.10-k10-era2b`
  GS Era-2 verified board cell (planning/gs-era2-verified-board-2026-09-08.md, PI frame ruling 2026-09-09): the registered cell g37-text-k10-verified-carried-p0.10-k10 re-scored with its committed recipe on the Era-2 ∩ B-union frame (era2-b-487); the committed evaluation on grid\_common\_bounds.geojson stays the row's record.
- `g37-text-k5-verified-carried-p0.10-k5-era2b`
  GS Era-2 verified board cell (planning/gs-era2-verified-board-2026-09-08.md, PI frame ruling 2026-09-09): the registered cell g37-text-k5-verified-carried-p0.10-k5 re-scored with its committed recipe on the Era-2 ∩ B-union frame (era2-b-487); the committed evaluation on grid\_common\_bounds.geojson stays the row's record.
- `g37-text-k5-verified-swap37-p0.80-k5-era2b`
  GS Era-2 verified board cell (planning/gs-era2-verified-board-2026-09-08.md, PI frame ruling 2026-09-09): the registered cell g37-text-k5-verified-swap37-p0.80-k5 re-scored with its committed recipe on the Era-2 ∩ B-union frame (era2-b-487); the committed evaluation on grid\_common\_bounds.geojson stays the row's record.
- `g37-text-k5-verified-swap38-p0.88-k5-era2b`
  GS Era-2 verified board cell (planning/gs-era2-verified-board-2026-09-08.md, PI frame ruling 2026-09-09): the registered cell g37-text-k5-verified-swap38-p0.88-k5 re-scored with its committed recipe on the Era-2 ∩ B-union frame (era2-b-487); the committed evaluation on grid\_common\_bounds.geojson stays the row's record.
- `g37-text-k5-verified-swap38-p0.88-k5`
  Gemini 3.8 Arm V (card planning/gemini38-screen-2026-09-04.md; PI ruling 9): the SAME 791-candidate K=5 union re-verified with gemini-3.8-flash at thinking=low (F1@20 0.9258, P 0.9335 / R 0.9182, tile-MCC 0.8218, 421 detections) for ~$0.85 flex token-basis. Registered under this run because it re-verifies this run's union; the campaign tree outputs/gemini38-screen-2026-09-04/ holds only the proposer probe, and the verification itself lives at outputs/gemini37-screen-2026-08-28/verifier/g384\_ov192\_g37/verify\_swap38/. Obs 448.
- `g37-text-k1-verified-opmax`
  IN-SAMPLE OPTIMUM (E56 class): the F1@20 argmax of this rung's own sweep, taken on the BOARD frame per ruling R2. The sweep was also run on the Era-2 frame full\_evaluation\_bounds.geojson (the frame the committed -opmax cells' optima were selected on) and the two frames agree on the argmax for this rung. Tie-break where needed: highest F1@20, then lowest vote\_t, then lowest prob\_t (0 point(s) tied here). K-LADDER PHASE 2 (approved by the PI 2026-09-12 at US$24.84 for 28 rungs; controlling card planning/k-ladder-review-2026-09-11.md, costing reports/k-ladder-phase2-costing-2026-09-12.md row 27, tier D). First-N rung: the union is passes run\_1 of pool outputs/gemini37-screen-2026-08-28/g384\_ov192\_g37, built at US$0 by scripts/merge\_passes.py --passes 1 --sweep (union 640 candidates at vote &gt;= 1, reproducing the costing table's figure of 640 exactly). Verified by one pass of the carried Gemini 3 verifier (ruling R1: no verifier swaps) at real-time flex tier, US$0.4521 on the audited flex basis (input x 0.25 + (output + thinking) x 1.50 per million). NOTE the verify path stamps cost\_basis 'list' with discount 1.0 even under flex and records the tier nowhere, so the stage meta's total\_cost\_usd is about twice the invoice (reports/r7-gaps-deltas-2026-09-11.md § 2.3). Scored on the board frame era2-b-487 with the family's recipe: curator reference, 14 buffers, 10,000 BCa draws, seed 42, MCC.
- `g37-text-k3-verified-opmax`
  IN-SAMPLE OPTIMUM (E56 class): the F1@20 argmax of this rung's own sweep, taken on the BOARD frame per ruling R2. The sweep was also run on the Era-2 frame full\_evaluation\_bounds.geojson (the frame the committed -opmax cells' optima were selected on) and the two frames agree on the argmax for this rung. Tie-break where needed: highest F1@20, then lowest vote\_t, then lowest prob\_t (0 point(s) tied here). K-LADDER PHASE 2 (approved by the PI 2026-09-12 at US$24.84 for 28 rungs; controlling card planning/k-ladder-review-2026-09-11.md, costing reports/k-ladder-phase2-costing-2026-09-12.md row 28, tier D). First-N rung: the union is passes run\_1, run\_2, run\_3 of pool outputs/gemini37-screen-2026-08-28/g384\_ov192\_g37, built at US$0 by scripts/merge\_passes.py --passes 1,2,3 --sweep (union 757 candidates at vote &gt;= 1, reproducing the costing table's figure of 757 exactly). Verified by one pass of the carried Gemini 3 verifier (ruling R1: no verifier swaps) at real-time flex tier, US$0.5329 on the audited flex basis (input x 0.25 + (output + thinking) x 1.50 per million). NOTE the verify path stamps cost\_basis 'list' with discount 1.0 even under flex and records the tier nowhere, so the stage meta's total\_cost\_usd is about twice the invoice (reports/r7-gaps-deltas-2026-09-11.md § 2.3). Scored on the board frame era2-b-487 with the family's recipe: curator reference, 14 buffers, 10,000 BCa draws, seed 42, MCC. THIS ROW IS ALSO THE CARRIED CELL: the sweep argmax lands exactly on the carried point (prob\_t 0.1, k = 3), so one cell serves both operating points and the transfer tax is 0.0000 by construction, not by measurement. No separate carried row is registered, because it would be the same detections file and the same evaluation.

### 5.2 Scope overrides (7 condition(s), 1 distinct frame(s))

These conditions are scored on a frame other than the run's nominal scope in § 2 — the 327-vs-487 leakage trap the verifier exists to catch, disclosed per condition:

- `g37-text-k1-verified-carried-p0.10-k1`, `g37-text-k1-verified-opmax`, `g37-text-k10-verified-carried-p0.10-k10-era2b`, `g37-text-k3-verified-opmax`, `g37-text-k5-verified-carried-p0.10-k5-era2b`, `g37-text-k5-verified-swap37-p0.80-k5-era2b`, `g37-text-k5-verified-swap38-p0.88-k5-era2b`
  bounds\_path = inputs/vectors/bounds/384/era2\_b\_intersection\_bounds.geojson, calibration\_set\_id = None, n\_calibration\_tiles = None, n\_test\_tiles = 487, test\_set\_id = era2-b-487

### 5.3 Decomposition note

Verbatim from `results/run-conditions.json` — the hand-authored record of how this run was decomposed and what was adjudicated:

> GS screen on the 487-tile common footprint, curator reference, 20 m primary. The proposer config is the committed text-B anchor's detect\_brief-text, byte-identical but for two command-line overrides (--model gemini-3.7-flash --thinking-level low). Four verifier passes over two unions: verify (K=5, 791 candidates) and verify\_k10 (K=10, 913) with the carried gemini-3-flash-preview verifier; verify\_swap37 and verify\_swap38 re-verify the SAME 791-candidate K=5 union with gemini-3.7-flash and gemini-3.8-flash. Disclosed deviation (card planning/gemini37-screen-2026-08-28.md changelog): the K=10 escalation re-verified the FULL union rather than increment-stitching the new candidates. GOTCHA: these are TEXT cells whose best operating point sits under the JSON key 'image\_best' — the campaign reused scripts/image\_b\_analysis.py; the key name is not a modality claim. The N=1/3/5 ladder rungs in k10/analysis.json are NOT registered (no materialised detections; deferred to the r2 recompute chain per PI ruling 4).

### 5.4 Waived evaluations (8, 5 distinct reason(s))

Scored evaluations under this run that no condition claims, each waived in `results/run-conditions.json` rather than left silent. Grouped by identical reason; where a reason covers more than 12 paths the first 12 are named and the decomposition carries the rest.

- **4 evaluation(s)** — uplift-supplement K=1 anchor (planning/uplift-supplement-2026-08-28.md; scored 5bd514542): an input to the supplement's pairing tables, on the reference of the stratum it pairs with; not a registered condition and not cited by the paper. Waived by PI ruling 2026-09-07 (planning/reference-revision-2026-09-06.md, register-verifier debt).
  - `results/uplift-supplement/verifier-pairing/gemini37-screen-2026-08-28__g37-text-k10-verified-carried-p0_10-k10/evaluation.json`
  - `results/uplift-supplement/verifier-pairing/gemini37-screen-2026-08-28__g37-text-k5-verified-carried-p0_10-k5/evaluation.json`
  - `results/uplift-supplement/verifier-pairing/gemini37-screen-2026-08-28__g37-text-k5-verified-swap37-p0_80-k5/evaluation.json`
  - `results/uplift-supplement/verifier-pairing/gemini37-screen-2026-08-28__g37-text-k5-verified-swap38-p0_88-k5/evaluation.json`
- **1 evaluation(s)** — GS Era-2 board gate G2 (planning/gs-era2-verified-board-2026-09-08.md): g37-text-k10-verified-carried-p0.10-k10's committed recipe re-run on its committed frame with a 200-draw bootstrap to prove the evaluator reproduces the committed evaluation; a gate artefact, not a condition.
  - `results/leaderboard/era2/gs-era2-verified-board-2026-09-10/g2/gemini37-screen-2026-08-28__g37-text-k10-verified-carried-p0_10-k10/evaluation.json`
- **1 evaluation(s)** — GS Era-2 board gate G2 (planning/gs-era2-verified-board-2026-09-08.md): g37-text-k5-verified-carried-p0.10-k5's committed recipe re-run on its committed frame with a 200-draw bootstrap to prove the evaluator reproduces the committed evaluation; a gate artefact, not a condition.
  - `results/leaderboard/era2/gs-era2-verified-board-2026-09-10/g2/gemini37-screen-2026-08-28__g37-text-k5-verified-carried-p0_10-k5/evaluation.json`
- **1 evaluation(s)** — GS Era-2 board gate G2 (planning/gs-era2-verified-board-2026-09-08.md): g37-text-k5-verified-swap37-p0.80-k5's committed recipe re-run on its committed frame with a 200-draw bootstrap to prove the evaluator reproduces the committed evaluation; a gate artefact, not a condition.
  - `results/leaderboard/era2/gs-era2-verified-board-2026-09-10/g2/gemini37-screen-2026-08-28__g37-text-k5-verified-swap37-p0_80-k5/evaluation.json`
- **1 evaluation(s)** — GS Era-2 board gate G2 (planning/gs-era2-verified-board-2026-09-08.md): g37-text-k5-verified-swap38-p0.88-k5's committed recipe re-run on its committed frame with a 200-draw bootstrap to prove the evaluator reproduces the committed evaluation; a gate artefact, not a condition.
  - `results/leaderboard/era2/gs-era2-verified-board-2026-09-10/g2/gemini37-screen-2026-08-28__g37-text-k5-verified-swap38-p0_88-k5/evaluation.json`

## 6. Analyses that read this run (8)

A run is linked to an analysis when the analysis's `conditions_compared` names one of this run's conditions. *Cells* is how many of the analysis's compared conditions come from this run, out of its total. *Signed* is the register's `manually_verified_at` stamp.

| Analysis | Cells | Type | Hypotheses | Registration | Paper section | Deviations | Signed | Output |
|---|---|---|---|---|---|---|---|---|
| `gemini37-image-gs-2026-09-01` | 2 of 6 | comparison | `H1` | post-hoc | Results | — | 2026-09-12T09:03:09Z | `results/gemini37-image-gs-2026-09-01` |
| `gemini37-screen-2026-08-28` | 3 of 4 | comparison | — | post-hoc | Results | — | 2026-09-12T09:03:09Z | `results/gemini37-screen-2026-08-28` |
| `gemini38-screen-armv-2026-09-04` | 3 of 3 | comparison | — | post-hoc | Results | — | 2026-09-12T09:03:09Z | `results/gemini38-screen-2026-09-04/armV` |
| `gs-era2-verified-board-2026-09-10` | 4 of 103 | leaderboard | `H2`, `H1` | post-hoc | Results | — | 2026-09-12T06:04:30Z | `results/leaderboard/era2/gs-era2-verified-board-2026-09-10/tiering_20m.json` |
| `k-ladder-2026-09-12` | 3 of 94 | comparison | `H3`, `H13` | post-hoc | Results | `E56`, `E85` | 2026-09-13T06:58:12Z | `results/k-ladder-2026-09-12/findings.md` |
| `null-exemplar-sensitivity-2026-09-13` | 7 of 235 | comparison | — | post-hoc | Appendix | — | not supplied | `results/null-exemplar-sensitivity-2026-09-13/findings.md` |
| `uplift-supplement-flatten` | 4 of 441 | diagnostic | — | post-hoc | Appendix | — | 2026-09-10T22:55:40Z | `results/uplift-supplement/conditions.csv` |
| `verifier-uplift-pairing` | 4 of 170 | comparison | `H2` | post-hoc | Appendix | — | 2026-09-12T06:04:30Z | `results/uplift-supplement/verifier-uplift.csv` |

## 7. Findings documents (2)

| Document | Named by |
|---|---|
| `results/k-ladder-2026-09-12/findings.md` | `k-ladder-2026-09-12` |
| `results/null-exemplar-sensitivity-2026-09-13/findings.md` | `null-exemplar-sensitivity-2026-09-13` |

## 8. Protocol errata

### 8.1 Registered as deviations (2)

Listed in the `deviations` field of an analysis that reads this run:

- **E56** — Verifier probability-threshold operating points are in-sample (test-set-selected), not calibrated
- **E85** — The temperature study's five consensus conditions were labelled N = 30 but read a 5-pass union — relabelled `consensus-{1..5}of5`; no measured value changes

## 9. Documents and structure in the run directory

| Document class | Filename | Count |
|---|---|---:|
| per-pass/per-run intent | `experiment_intent.md` | 27 |

These classes are in Revision-Policy scope going forward (`docs/methodology/output-directory-standard.md` § "Documents in Revision Policy Scope").

### 9.1 Registered pools

| Proposer pool | Modality | Path within the run directory |
|---|---|---|
| `g384_ov192_g37` | text | `g384_ov192_g37` |

6 registered verifier-pass directory/directories; see `results/run-conditions.json` for the full list.

## 10. Provenance of this report

This report is a projection. Every figure above is read from one of the committed inputs below; nothing is estimated, and a figure that is not on file is written **not supplied** with its reason.

| Field | Value |
|---|---|
| Generator | `scripts/generate_run_reports.py` v1.1.0 |
| Source commit | `60b07ffcc` |
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
