<!-- GENERATED FILE — do not hand-edit. Projected from the registered manifests by scripts/generate_run_reports.py v1.1.0. Hand edits are destroyed on the next regeneration and fail the --check drift guard. -->
# Post-run report — stride-55map-2026-08-25

> **GENERATED FILE — do not hand-edit.** Projected from the registered manifests by `scripts/generate_run_reports.py` v1.1.0 at source commit `a8c03bb9e`. This file carries provenance instead of a hand changelog, per the PI ruling of 2026-09-11 recorded in `docs/methodology/output-directory-standard.md` § "Documents in Revision Policy Scope": a generated document's history is its inputs' and its generator's git history, so "is this current?" is answered by the `--check` drift guard and its tier-1 test, not by a changelog. Regenerate after any manifest rebuild; put before/after notes in the commit message.

**Directory**: `outputs/stride-55map-2026-08-25` · **Registry status**: active · **Purpose**: 55-map deployment portfolio (card planning/55map-portfolio-2026-08-25.md, predictions P1-P8 registered by commit): Runs A (384/33.3%, stride 256) and B (384/50%, stride 192) at K=10 with the carry-forward verifier over the full unions — the calibrate-on-GS-then-deploy transfer measurement.

## 1. Identity and registration

| Field | Value |
|---|---|
| Run id | `stride-55map-2026-08-25` |
| Directory | `outputs/stride-55map-2026-08-25` |
| Registry status | active |
| Purpose | 55-map deployment portfolio (card planning/55map-portfolio-2026-08-25.md, predictions P1-P8 registered by commit): Runs A (384/33.3%, stride 256) and B (384/50%, stride 192) at K=10 with the carry-forward verifier over the full unions — the calibrate-on-GS-then-deploy transfer measurement. |
| Run type (derived) | proposer-verifier |
| Primary hypothesis | not supplied |
| Also informs | `H13` |
| Headline condition | stride-55map-2026-08-25::g384-ov192-55map-verified-carried-p0.15-k10-canonical-gt |
| Headline rationale | Run B's carried PRIMARY (corrected-F1@50 0.8422) — the committed deployment claim; B &gt; A BH-robust (final-board Pass 2 registers the standardised cells). |
| Historical aliases | — |
| Working-notes Obs | — |
| Registry notes | 55-map deployment portfolio Runs A/B + 96,195-call verifier. Registered S143 (Pass 1). |

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

### 3.1 Proposer passes (20)

| Pool | Pass | Model used | Model requested | Modality | Thinking | Temp | Status | Tiles done | Dispatched | Retries |
|---|---:|---|---|---|---|---:|---|---:|---:|---:|
| `g384_ov128_55map` | 1 | gemini-3-flash-preview | gemini-3-flash-preview | text | minimal | 0.7 | ok | 14160 | 14160 | 7 |
| `g384_ov128_55map` | 2 | gemini-3-flash-preview | gemini-3-flash-preview | text | minimal | 0.7 | ok | 14160 | 14160 | 37 |
| `g384_ov128_55map` | 3 | gemini-3-flash-preview | gemini-3-flash-preview | text | minimal | 0.7 | ok | 14160 | 14160 | 9 |
| `g384_ov128_55map` | 4 | gemini-3-flash-preview | gemini-3-flash-preview | text | minimal | 0.7 | ok | 14160 | 14160 | 2 |
| `g384_ov128_55map` | 5 | gemini-3-flash-preview | gemini-3-flash-preview | text | minimal | 0.7 | ok | 14160 | 14160 | 1 |
| `g384_ov128_55map` | 6 | gemini-3-flash-preview | gemini-3-flash-preview | text | minimal | 0.7 | ok | 14160 | 14160 | 24 |
| `g384_ov128_55map` | 7 | gemini-3-flash-preview | gemini-3-flash-preview | text | minimal | 0.7 | ok | 14160 | 14160 | 24 |
| `g384_ov128_55map` | 8 | gemini-3-flash-preview | gemini-3-flash-preview | text | minimal | 0.7 | ok | 14160 | 14160 | 6 |
| `g384_ov128_55map` | 9 | gemini-3-flash-preview | gemini-3-flash-preview | text | minimal | 0.7 | ok | 14160 | 14160 | 48 |
| `g384_ov128_55map` | 10 | gemini-3-flash-preview | gemini-3-flash-preview | text | minimal | 0.7 | ok | 14160 | 14160 | 64 |
| `g384_ov192_55map` | 1 | gemini-3-flash-preview | gemini-3-flash-preview | text | minimal | 0.7 | ok | 24561 | 24561 | 5300 |
| `g384_ov192_55map` | 2 | gemini-3-flash-preview | gemini-3-flash-preview | text | minimal | 0.7 | ok | 24561 | 24561 | 655 |
| `g384_ov192_55map` | 3 | gemini-3-flash-preview | gemini-3-flash-preview | text | minimal | 0.7 | ok | 24561 | 24561 | 279 |
| `g384_ov192_55map` | 4 | gemini-3-flash-preview | gemini-3-flash-preview | text | minimal | 0.7 | ok | 24561 | 24561 | 1851 |
| `g384_ov192_55map` | 5 | gemini-3-flash-preview | gemini-3-flash-preview | text | minimal | 0.7 | ok | 24561 | 24561 | 441 |
| `g384_ov192_55map` | 6 | gemini-3-flash-preview | gemini-3-flash-preview | text | minimal | 0.7 | ok | 24561 | 24561 | 233 |
| `g384_ov192_55map` | 7 | gemini-3-flash-preview | gemini-3-flash-preview | text | minimal | 0.7 | ok | 24561 | 24561 | 282 |
| `g384_ov192_55map` | 8 | gemini-3-flash-preview | gemini-3-flash-preview | text | minimal | 0.7 | ok | 24561 | 24561 | 104 |
| `g384_ov192_55map` | 9 | gemini-3-flash-preview | gemini-3-flash-preview | text | minimal | 0.7 | ok | 24561 | 24561 | 37 |
| `g384_ov192_55map` | 10 | gemini-3-flash-preview | gemini-3-flash-preview | text | minimal | 0.7 | ok | 24561 | 24561 | 30 |

### 3.2 Verifier passes (3)

| Pool | Pass | Model used | Modality | Thinking | Temp | Status | Candidates verified | Retries |
|---|---:|---|---|---|---:|---|---:|---:|
| `g384_ov128_55map-union-k10-verify` | 1 | gemini-3-flash-preview | text | minimal | 0.0 | ok | 6 | 0 |
| `g384_ov192_55map-union-k10-verify` | 1 | gemini-3-flash-preview | text | minimal | 0.0 | ok | 57482 | 502 |
| `g384_ov192_55map-union-k10-verify37` | 1 | gemini-3.7-flash | text | low | 0.0 | ok | 29 | 50 |

Verifier rows report no tile count by design: verifier pass: operates on candidate crops, not tiles. The verifier meta records candidate ids (cand\_NNNN) in execution\_stats.completed\_items and candidate API items in per\_item\_metadata, so no tile-scale record exists to report. Completed crop count is in n\_candidates\_verified. (E71 Defect 2 / GAP-8, resolved E72 2026-08-02.)

## 4. Token load and recorded cost

| Field | Value |
|---|---|
| Passes on file | 23 |
| Input tokens (billed) | 684,559,250 |
| Input tokens (cached) | 0 |
| Output tokens | 52,354,427 |
| Thinking tokens | 4,406 |
| Total tokens | 736,918,083 |
| Passes with no token record | 0 |
| Sum of recorded `cost_usd` | US$288.8720 over 23 of 23 pass(es) |
| Passes with no `cost_usd` | 0 |
| Summed wall clock | 35.05 h over 23 pass(es) |

> **The recorded cost is NOT this run's cost.** Each `cost_usd` above is the pass meta's own `cost_estimate.total_cost_usd`, lifted verbatim by `scripts/generate_post_run_report.py`. The token-load audit of 2026-06-12 established that those self-reported estimates price at STANDARD rates although the audited runs executed at `--service-tier flex` (half price) and omit thinking tokens although Gemini bills thinking at the output rate (`reports/token-load-audit-2026-06-12.md` § 1, § 2). The sum is reproduced here as the recorded figure and as an input to a reconciliation, not as a total to cite.

Audit and reconciliation reports whose text names this run or its directory — consult these for audited figures; a mention is a pointer, not a claim that the report audits this run in full:

- `reports/r7-gaps-deltas-2026-09-11.md`

## 5. Registered conditions (40)

F1@20 m is the preregistered localisation buffer; F1@50 m is the deployment working buffer. Confidence intervals are those the evaluation recorded (method, iterations and seed per condition in the manifest). `mcc` is tile-level. A cell reading *not supplied* means the metric is absent from the condition's evaluation, not that it is zero; a tile-MCC reading *withheld* means the tile-join invariant REFUSED that condition's per-tile table on this frame, so the tile metrics and the bootstrap intervals were not computed — the condition's whole-frame F1 is unaffected and is reported in full (PI ruling 2026-09-13; the named reason is in the condition's manifest row).

| Condition | Architecture | Aggregation | Passes | Operating point | Detections | F1@20 m [CI] | F1@50 m [CI] | Tile MCC |
|---|---|---|---:|---|---:|---|---|---:|
| `g384-ov128-55map-n1-oracle-p0.20-k1-r2-gt` | proposer-verifier | verified | 1 | k=1/pt=0.2 | 4879 | 0.6776 [0.6648, 0.6897] | 0.8227 [0.8139, 0.8313] | 0.7006 |
| `g384-ov128-55map-n1-oracle-p0.20-k1-standardised-gt` | proposer-verifier | verified | 1 | k=1/pt=0.2 | 4879 | 0.6777 [0.6650, 0.6901] | 0.8231 [0.8144, 0.8317] | 0.7010 |
| `g384-ov128-55map-n10-carried-p0.15-k8-r2-gt` | proposer-verifier | verified | 10 | k=8/pt=0.15 | 4475 | 0.7081 [0.6950, 0.7204] | 0.8391 [0.8302, 0.8478] | 0.6930 |
| `g384-ov128-55map-n10-carried-p0.15-k8-standardised-gt` | proposer-verifier | verified | 10 | k=8/pt=0.15 | 4475 | 0.7079 [0.6947, 0.7202] | 0.8392 [0.8303, 0.8479] | 0.6934 |
| `g384-ov128-55map-n10-oracle-p0.15-k7-r2-gt` | proposer-verifier | verified | 10 | k=7/pt=0.15 | 4639 | 0.7083 [0.6951, 0.7205] | 0.8419 [0.8330, 0.8502] | 0.6954 |
| `g384-ov128-55map-n10-oracle-p0.15-k7-standardised-gt` | proposer-verifier | verified | 10 | k=7/pt=0.15 | 4639 | 0.7081 [0.6949, 0.7203] | 0.8420 [0.8331, 0.8503] | 0.6958 |
| `g384-ov128-55map-n3-carried-posthoc-p0.15-k3-r2-gt` | proposer-verifier | verified | 3 | k=3/pt=0.15 | 4400 | 0.7027 [0.6896, 0.7150] | 0.8307 [0.8217, 0.8395] | 0.6876 |
| `g384-ov128-55map-n3-carried-posthoc-p0.15-k3-standardised-gt` | proposer-verifier | verified | 3 | k=3/pt=0.15 | 4400 | 0.7024 [0.6894, 0.7148] | 0.8308 [0.8218, 0.8396] | 0.6880 |
| `g384-ov128-55map-n3-oracle-p0.20-k2-r2-gt` | proposer-verifier | verified | 3 | k=2/pt=0.2 | 4796 | 0.6990 [0.6863, 0.7113] | 0.8321 [0.8233, 0.8405] | 0.7018 |
| `g384-ov128-55map-n3-oracle-p0.20-k2-standardised-gt` | proposer-verifier | verified | 3 | k=2/pt=0.2 | 4796 | 0.6992 [0.6864, 0.7113] | 0.8326 [0.8238, 0.8410] | 0.7022 |
| `g384-ov128-55map-n5-carried-p0.15-k4-r2-gt` | proposer-verifier | verified | 5 | k=4/pt=0.15 | 4597 | 0.7062 [0.6933, 0.7188] | 0.8383 [0.8294, 0.8468] | 0.6907 |
| `g384-ov128-55map-n5-carried-p0.15-k4-standardised-gt` | proposer-verifier | verified | 5 | k=4/pt=0.15 | 4597 | 0.7059 [0.6931, 0.7185] | 0.8383 [0.8294, 0.8469] | 0.6911 |
| `g384-ov128-55map-n5-oracle-p0.15-k4-r2-gt` | proposer-verifier | verified | 5 | k=4/pt=0.15 | 4597 | 0.7062 [0.6933, 0.7188] | 0.8383 [0.8294, 0.8468] | 0.6907 |
| `g384-ov128-55map-n5-oracle-p0.15-k4-standardised-gt` | proposer-verifier | verified | 5 | k=4/pt=0.15 | 4597 | 0.7059 [0.6931, 0.7185] | 0.8383 [0.8294, 0.8469] | 0.6911 |
| `g384-ov128-55map-verified-carried-p0.15-k8-canonical-gt` | proposer-verifier | verified | 10 | k=8/pt=0.15 | 4475 | 0.6689 [0.6549, 0.6825] | 0.8326 [0.8236, 0.8414] | 0.6934 |
| `g384-ov128-55map-verified-oracle-p0.15-k7-canonical-gt` | proposer-verifier | verified | 10 | k=7/pt=0.15 | 4639 | 0.6685 [0.6547, 0.6820] | 0.8362 [0.8274, 0.8447] | 0.6958 |
| `g384-ov192-55map-k10-verified37-p0.98-k10-canonical-gt` | proposer-verifier | verified | 10 | k=10/pt=0.98 | 4246 | 0.7084 [0.6950, 0.7218] | 0.8656 [0.8574, 0.8736] | 0.7268 |
| `g384-ov192-55map-k10-verified37-p0.98-k10-standardised-gt` | proposer-verifier | verified | 10 | k=10/pt=0.98 | 4246 | 0.7472 [0.7347, 0.7595] | 0.8732 [0.8649, 0.8810] | 0.7268 |
| `g384-ov192-55map-n1-oracle-p0.20-k1-r2-gt` | proposer-verifier | verified | 1 | k=1/pt=0.2 | 5655 | 0.6695 [0.6571, 0.6812] | 0.8013 [0.7925, 0.8096] | 0.7092 |
| `g384-ov192-55map-n1-oracle-p0.20-k1-standardised-gt` | proposer-verifier | verified | 1 | k=1/pt=0.2 | 5655 | 0.6693 [0.6569, 0.6809] | 0.8013 [0.7926, 0.8098] | 0.7097 |
| `g384-ov192-55map-n1-verified37-oracle-p0.96-k1-r2-gt` | proposer-verifier | verified | 1 | k=1/pt=0.96 | 5337 | 0.7023 [0.6902, 0.7138] | 0.8352 [0.8272, 0.8428] | 0.7471 |
| `g384-ov192-55map-n10-carried-p0.15-k10-r2-gt` | proposer-verifier | verified | 10 | k=10/pt=0.15 | 4505 | 0.7252 [0.7126, 0.7374] | 0.8497 [0.8410, 0.8579] | 0.6977 |
| `g384-ov192-55map-n10-carried-p0.15-k10-standardised-gt` | proposer-verifier | verified | 10 | k=10/pt=0.15 | 4505 | 0.7250 [0.7123, 0.7372] | 0.8498 [0.8411, 0.8581] | 0.6982 |
| `g384-ov192-55map-n10-oracle-p0.20-k9-r2-gt` | proposer-verifier | verified | 10 | k=9/pt=0.2 | 4639 | 0.7296 [0.7172, 0.7416] | 0.8560 [0.8477, 0.8638] | 0.7123 |
| `g384-ov192-55map-n10-oracle-p0.20-k9-standardised-gt` | proposer-verifier | verified | 10 | k=9/pt=0.2 | 4639 | 0.7292 [0.7167, 0.7414] | 0.8558 [0.8475, 0.8636] | 0.7127 |
| `g384-ov192-55map-n10-verified37-carried-p0.98-k10-r2-gt` | proposer-verifier | verified | 10 | k=10/pt=0.98 | 4246 | 0.7472 [0.7347, 0.7596] | 0.8728 [0.8646, 0.8808] | 0.7264 |
| `g384-ov192-55map-n10-verified37-oracle-p0.96-k9-r2-gt` | proposer-verifier | verified | 10 | k=9/pt=0.96 | 4495 | 0.7533 [0.7407, 0.7653] | 0.8813 [0.8736, 0.8886] | 0.7359 |
| `g384-ov192-55map-n3-carried-posthoc-p0.15-k3-r2-gt` | proposer-verifier | verified | 3 | k=3/pt=0.15 | 4971 | 0.7182 [0.7059, 0.7303] | 0.8477 [0.8395, 0.8556] | 0.7020 |
| `g384-ov192-55map-n3-carried-posthoc-p0.15-k3-standardised-gt` | proposer-verifier | verified | 3 | k=3/pt=0.15 | 4971 | 0.7178 [0.7055, 0.7298] | 0.8476 [0.8395, 0.8555] | 0.7025 |
| `g384-ov192-55map-n3-oracle-p0.20-k3-r2-gt` | proposer-verifier | verified | 3 | k=3/pt=0.2 | 4772 | 0.7211 [0.7089, 0.7333] | 0.8507 [0.8424, 0.8586] | 0.7128 |
| `g384-ov192-55map-n3-oracle-p0.20-k3-standardised-gt` | proposer-verifier | verified | 3 | k=3/pt=0.2 | 4772 | 0.7207 [0.7086, 0.7329] | 0.8505 [0.8423, 0.8584] | 0.7132 |
| `g384-ov192-55map-n3-verified37-oracle-p0.96-k3-r2-gt` | proposer-verifier | verified | 3 | k=3/pt=0.96 | 4626 | 0.7445 [0.7322, 0.7563] | 0.8747 [0.8670, 0.8820] | 0.7376 |
| `g384-ov192-55map-n5-carried-p0.15-k5-canonical-gt` | proposer-verifier | verified | 5 | k=5/pt=0.15 | 4736 | 0.6796 [0.6661, 0.6932] | 0.8438 [0.8353, 0.8521] | 0.7014 |
| `g384-ov192-55map-n5-carried-p0.15-k5-r2-gt` | proposer-verifier | verified | 5 | k=5/pt=0.15 | 4736 | 0.7209 [0.7082, 0.7332] | 0.8503 [0.8418, 0.8583] | 0.7010 |
| `g384-ov192-55map-n5-carried-p0.15-k5-standardised-gt` | proposer-verifier | verified | 5 | k=5/pt=0.15 | 4736 | 0.7205 [0.7077, 0.7328] | 0.8502 [0.8416, 0.8582] | 0.7014 |
| `g384-ov192-55map-n5-oracle-p0.20-k5-r2-gt` | proposer-verifier | verified | 5 | k=5/pt=0.2 | 4566 | 0.7222 [0.7094, 0.7346] | 0.8516 [0.8430, 0.8596] | 0.7098 |
| `g384-ov192-55map-n5-oracle-p0.20-k5-standardised-gt` | proposer-verifier | verified | 5 | k=5/pt=0.2 | 4566 | 0.7218 [0.7090, 0.7341] | 0.8515 [0.8430, 0.8595] | 0.7102 |
| `g384-ov192-55map-n5-verified37-oracle-p0.96-k5-r2-gt` | proposer-verifier | verified | 5 | k=5/pt=0.96 | 4434 | 0.7452 [0.7327, 0.7575] | 0.8758 [0.8679, 0.8832] | 0.7326 |
| `g384-ov192-55map-verified-carried-p0.15-k10-canonical-gt` | proposer-verifier | verified | 10 | k=10/pt=0.15 | 4505 | 0.6847 [0.6714, 0.6981] | 0.8422 [0.8335, 0.8506] | 0.6982 |
| `g384-ov192-55map-verified-oracle-p0.20-k9-canonical-gt` | proposer-verifier | verified | 10 | k=9/pt=0.2 | 4639 | 0.6883 [0.6751, 0.7017] | 0.8503 [0.8420, 0.8583] | 0.7127 |

Buffers on file (metres), by how many conditions carry that set:

- 34 condition(s): 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 75, 100, 125, 150
- 6 condition(s): 20, 30, 50

Tile-level MCC is on file for 40 of 40 condition(s).

### 5.1 Condition caveats (40 condition(s), 40 distinct caveat(s))

Grouped by identical text: a caveat written once for a family of sibling cells is reproduced once, with every cell it applies to named. Nothing is elided.

- `g384-ov192-55map-k10-verified37-p0.98-k10-canonical-gt`
  B5 — the 2x2 grid's fourth cell (this run's Gemini-3 K=10 union, 57,482 candidates, re-verified with gemini-3.7-flash), CANONICAL chain: corrected-F1@50 0.865618 [0.857387, 0.873612], P 0.9588 / R 0.7890, tile-MCC 0.7268, 4,246 detections — the grid's precision and tile-MCC crowns. +0.0234 over this run's own K=10 carried incumbent (p = 0.0001, BH-significant), the second verifier-axis test. Carried point (0.98, k10) fixed by the GS calibration leg (grid-2026-08-18::g384-ov192-k10-verified37-p0.98-k10) before deployment scoring. Registered here per PI ruling 6.
- `g384-ov192-55map-k10-verified37-p0.98-k10-standardised-gt`
  B6 — the same detections on the ruling-21 STANDARDISED reference: F1@50 0.8732 [0.8649, 0.8810], P 0.9517 / R 0.8066. Tile matrix identical to the canonical 50 m row (2358/4985/32/1166).
- `g384-ov192-55map-n5-carried-p0.15-k5-canonical-gt`
  Canonical-chain companion of the B N=5 carried cell (PI ruling 2026-09-06, planning/reference-revision-2026-09-06.md section 3a): the same first-5 union with inherited K=10 Gemini-3 verification at (0.15, k5), materialised by the r2 sweep (pass-pinned, geometry-gated to the committed primary) and scored on the canonical chain by the Track-2 engine (canonical review, buffers 20/30/50, B=10,000, seed 42). corrected-F1@50 0.8437752627 == results/stride55-2026-08-27/ladder.json N=5 carried, |d| 0 (gate 1e-6). Registered so the 3.7 campaign's canonical-chain comparisons (D1 dead heat; the Obs 444 five-test family) cite a registered condition.
- `g384-ov128-55map-n1-oracle-p0.20-k1-standardised-gt`
  Final-board cell A-N1-oracle (oracle (standardised-reference argmax), F1@50 0.8231, tier via final\_board\_50m.json). Standardised-reference (ruling 21) evaluation on the shared 8,541-tile frame; final-board cell (results/55map-final-board-2026-08-27/). Carry-forward verifier; probabilities inherited from K=10 for N&lt;10 rungs (GS-validated ±0.008).
- `g384-ov128-55map-n10-carried-p0.15-k8-standardised-gt`
  Final-board cell A-N10-carried (carried, F1@50 0.8392, tier via final\_board\_50m.json). Standardised-reference (ruling 21) evaluation on the shared 8,541-tile frame; final-board cell (results/55map-final-board-2026-08-27/). Carry-forward verifier; probabilities inherited from K=10 for N&lt;10 rungs (GS-validated ±0.008).
- `g384-ov128-55map-n10-oracle-p0.15-k7-standardised-gt`
  Final-board cell A-N10-oracle (oracle (standardised-reference argmax), F1@50 0.8420, tier via final\_board\_50m.json). Standardised-reference (ruling 21) evaluation on the shared 8,541-tile frame; final-board cell (results/55map-final-board-2026-08-27/). Carry-forward verifier; probabilities inherited from K=10 for N&lt;10 rungs (GS-validated ±0.008).
- `g384-ov128-55map-n3-carried-posthoc-p0.15-k3-standardised-gt`
  Final-board cell A-N3-carried (carried (post-hoc), F1@50 0.8308, tier via final\_board\_50m.json). Standardised-reference (ruling 21) evaluation on the shared 8,541-tile frame; final-board cell (results/55map-final-board-2026-08-27/). Carry-forward verifier; probabilities inherited from K=10 for N&lt;10 rungs (GS-validated ±0.008). EMERGENT post-hoc nomination (PI-directed 2026-08-28): the GS-ladder-selected point, evaluated after the N=3 oracle's frontier position emerged — see the board's post-hoc section.
- `g384-ov128-55map-n3-oracle-p0.20-k2-standardised-gt`
  Final-board cell A-N3-oracle (oracle (standardised-reference argmax), F1@50 0.8326, tier via final\_board\_50m.json). Standardised-reference (ruling 21) evaluation on the shared 8,541-tile frame; final-board cell (results/55map-final-board-2026-08-27/). Carry-forward verifier; probabilities inherited from K=10 for N&lt;10 rungs (GS-validated ±0.008).
- `g384-ov128-55map-n5-carried-p0.15-k4-standardised-gt`
  Final-board cell A-N5-carried (carried, F1@50 0.8383, tier via final\_board\_50m.json). Standardised-reference (ruling 21) evaluation on the shared 8,541-tile frame; final-board cell (results/55map-final-board-2026-08-27/). Carry-forward verifier; probabilities inherited from K=10 for N&lt;10 rungs (GS-validated ±0.008).
- `g384-ov128-55map-n5-oracle-p0.15-k4-standardised-gt`
  Final-board cell A-N5-oracle (oracle (standardised-reference argmax), F1@50 0.8383, tier via final\_board\_50m.json). Standardised-reference (ruling 21) evaluation on the shared 8,541-tile frame; final-board cell (results/55map-final-board-2026-08-27/). Carry-forward verifier; probabilities inherited from K=10 for N&lt;10 rungs (GS-validated ±0.008).
- `g384-ov192-55map-n1-oracle-p0.20-k1-standardised-gt`
  Final-board cell B-N1-oracle (oracle (standardised-reference argmax), F1@50 0.8013, tier via final\_board\_50m.json). Standardised-reference (ruling 21) evaluation on the shared 8,541-tile frame; final-board cell (results/55map-final-board-2026-08-27/). Carry-forward verifier; probabilities inherited from K=10 for N&lt;10 rungs (GS-validated ±0.008).
- `g384-ov192-55map-n10-carried-p0.15-k10-standardised-gt`
  Final-board cell B-N10-carried (carried, F1@50 0.8498, tier via final\_board\_50m.json). Standardised-reference (ruling 21) evaluation on the shared 8,541-tile frame; final-board cell (results/55map-final-board-2026-08-27/). Carry-forward verifier; probabilities inherited from K=10 for N&lt;10 rungs (GS-validated ±0.008).
- `g384-ov192-55map-n10-oracle-p0.20-k9-standardised-gt`
  Final-board cell B-N10-oracle (oracle (standardised-reference argmax), F1@50 0.8558, tier via final\_board\_50m.json). Standardised-reference (ruling 21) evaluation on the shared 8,541-tile frame; final-board cell (results/55map-final-board-2026-08-27/). Carry-forward verifier; probabilities inherited from K=10 for N&lt;10 rungs (GS-validated ±0.008).
- `g384-ov192-55map-n3-carried-posthoc-p0.15-k3-standardised-gt`
  Final-board cell B-N3-carried (carried (post-hoc), F1@50 0.8476, tier via final\_board\_50m.json). Standardised-reference (ruling 21) evaluation on the shared 8,541-tile frame; final-board cell (results/55map-final-board-2026-08-27/). Carry-forward verifier; probabilities inherited from K=10 for N&lt;10 rungs (GS-validated ±0.008). EMERGENT post-hoc nomination (PI-directed 2026-08-28): the GS-ladder-selected point, evaluated after the N=3 oracle's frontier position emerged — see the board's post-hoc section.
- `g384-ov192-55map-n3-oracle-p0.20-k3-standardised-gt`
  Final-board cell B-N3-oracle (oracle (standardised-reference argmax), F1@50 0.8505, tier via final\_board\_50m.json). Standardised-reference (ruling 21) evaluation on the shared 8,541-tile frame; final-board cell (results/55map-final-board-2026-08-27/). Carry-forward verifier; probabilities inherited from K=10 for N&lt;10 rungs (GS-validated ±0.008).
- `g384-ov192-55map-n5-carried-p0.15-k5-standardised-gt`
  Final-board cell B-N5-carried (carried, F1@50 0.8502, tier via final\_board\_50m.json). Standardised-reference (ruling 21) evaluation on the shared 8,541-tile frame; final-board cell (results/55map-final-board-2026-08-27/). Carry-forward verifier; probabilities inherited from K=10 for N&lt;10 rungs (GS-validated ±0.008).
- `g384-ov192-55map-n5-oracle-p0.20-k5-standardised-gt`
  Final-board cell B-N5-oracle (oracle (standardised-reference argmax), F1@50 0.8515, tier via final\_board\_50m.json). Standardised-reference (ruling 21) evaluation on the shared 8,541-tile frame; final-board cell (results/55map-final-board-2026-08-27/). Carry-forward verifier; probabilities inherited from K=10 for N&lt;10 rungs (GS-validated ±0.008).
- `g384-ov128-55map-verified-carried-p0.15-k8-canonical-gt`
  Run A PRIMARY (the carried deployment claim, committed before the sweep). Corrected-F1 vs canonical extended GT. Carry-forward verifier (verify\_adversarial-text, T=0.0, MINIMAL, n=1) over the full K=10 union.
- `g384-ov128-55map-verified-oracle-p0.15-k7-canonical-gt`
  Run A deployment ORACLE (sweep argmax @50m, corrected-F1 0.8362; post-hoc basis, labelled). Carry-forward verifier (verify\_adversarial-text, T=0.0, MINIMAL, n=1) over the full K=10 union.
- `g384-ov192-55map-verified-carried-p0.15-k10-canonical-gt`
  Run B PRIMARY (the carried deployment claim, committed before the sweep). Corrected-F1 vs canonical extended GT. Carry-forward verifier (verify\_adversarial-text, T=0.0, MINIMAL, n=1) over the full K=10 union.
- `g384-ov192-55map-verified-oracle-p0.20-k9-canonical-gt`
  Run B deployment ORACLE (sweep argmax @50m, corrected-F1 0.8503; post-hoc basis, labelled). Carry-forward verifier (verify\_adversarial-text, T=0.0, MINIMAL, n=1) over the full K=10 union.
- `g384-ov128-55map-n1-oracle-p0.20-k1-r2-gt`
  r2 board cell A-N1-oracle (oracle (r2-reference argmax), F1@50 0.8227, tier via final\_board\_50m.json). Reference-revision-r2 evaluation (card planning/reference-revision-2026-09-06.md): the standardised reference with the PI's cluster- and empty-tile-audit adjudications applied (-6 records, +14; 5,018 at marked centres, included whole at every R). Scored by evaluate\_detections.py (14 buffers, tile-level BCa 10,000 / seed 42, --mcc) -- one engine for the whole r2 chain.
- `g384-ov128-55map-n10-carried-p0.15-k8-r2-gt`
  r2 board cell A-N10-carried (carried, F1@50 0.8391, tier via final\_board\_50m.json). Reference-revision-r2 evaluation (card planning/reference-revision-2026-09-06.md): the standardised reference with the PI's cluster- and empty-tile-audit adjudications applied (-6 records, +14; 5,018 at marked centres, included whole at every R). Scored by evaluate\_detections.py (14 buffers, tile-level BCa 10,000 / seed 42, --mcc) -- one engine for the whole r2 chain.
- `g384-ov128-55map-n10-oracle-p0.15-k7-r2-gt`
  r2 board cell A-N10-oracle (oracle (r2-reference argmax), F1@50 0.8419, tier via final\_board\_50m.json). Reference-revision-r2 evaluation (card planning/reference-revision-2026-09-06.md): the standardised reference with the PI's cluster- and empty-tile-audit adjudications applied (-6 records, +14; 5,018 at marked centres, included whole at every R). Scored by evaluate\_detections.py (14 buffers, tile-level BCa 10,000 / seed 42, --mcc) -- one engine for the whole r2 chain.
- `g384-ov128-55map-n3-carried-posthoc-p0.15-k3-r2-gt`
  r2 board cell A-N3-carried (carried (post-hoc), F1@50 0.8307, tier via final\_board\_50m.json). Reference-revision-r2 evaluation (card planning/reference-revision-2026-09-06.md): the standardised reference with the PI's cluster- and empty-tile-audit adjudications applied (-6 records, +14; 5,018 at marked centres, included whole at every R). Scored by evaluate\_detections.py (14 buffers, tile-level BCa 10,000 / seed 42, --mcc) -- one engine for the whole r2 chain.
- `g384-ov128-55map-n3-oracle-p0.20-k2-r2-gt`
  r2 board cell A-N3-oracle (oracle (r2-reference argmax), F1@50 0.8321, tier via final\_board\_50m.json). Reference-revision-r2 evaluation (card planning/reference-revision-2026-09-06.md): the standardised reference with the PI's cluster- and empty-tile-audit adjudications applied (-6 records, +14; 5,018 at marked centres, included whole at every R). Scored by evaluate\_detections.py (14 buffers, tile-level BCa 10,000 / seed 42, --mcc) -- one engine for the whole r2 chain.
- `g384-ov128-55map-n5-carried-p0.15-k4-r2-gt`
  r2 board cell A-N5-carried (carried, F1@50 0.8383, tier via final\_board\_50m.json). Reference-revision-r2 evaluation (card planning/reference-revision-2026-09-06.md): the standardised reference with the PI's cluster- and empty-tile-audit adjudications applied (-6 records, +14; 5,018 at marked centres, included whole at every R). Scored by evaluate\_detections.py (14 buffers, tile-level BCa 10,000 / seed 42, --mcc) -- one engine for the whole r2 chain.
- `g384-ov128-55map-n5-oracle-p0.15-k4-r2-gt`
  r2 board cell A-N5-oracle (oracle (r2-reference argmax), F1@50 0.8383, tier via final\_board\_50m.json). Reference-revision-r2 evaluation (card planning/reference-revision-2026-09-06.md): the standardised reference with the PI's cluster- and empty-tile-audit adjudications applied (-6 records, +14; 5,018 at marked centres, included whole at every R). Scored by evaluate\_detections.py (14 buffers, tile-level BCa 10,000 / seed 42, --mcc) -- one engine for the whole r2 chain.
- `g384-ov192-55map-n1-oracle-p0.20-k1-r2-gt`
  r2 board cell B-N1-oracle (oracle (r2-reference argmax), F1@50 0.8013, tier via final\_board\_50m.json). Reference-revision-r2 evaluation (card planning/reference-revision-2026-09-06.md): the standardised reference with the PI's cluster- and empty-tile-audit adjudications applied (-6 records, +14; 5,018 at marked centres, included whole at every R). Scored by evaluate\_detections.py (14 buffers, tile-level BCa 10,000 / seed 42, --mcc) -- one engine for the whole r2 chain.
- `g384-ov192-55map-n10-carried-p0.15-k10-r2-gt`
  r2 board cell B-N10-carried (carried, F1@50 0.8497, tier via final\_board\_50m.json). Reference-revision-r2 evaluation (card planning/reference-revision-2026-09-06.md): the standardised reference with the PI's cluster- and empty-tile-audit adjudications applied (-6 records, +14; 5,018 at marked centres, included whole at every R). Scored by evaluate\_detections.py (14 buffers, tile-level BCa 10,000 / seed 42, --mcc) -- one engine for the whole r2 chain.
- `g384-ov192-55map-n10-oracle-p0.20-k9-r2-gt`
  r2 board cell B-N10-oracle (oracle (r2-reference argmax), F1@50 0.8560, tier via final\_board\_50m.json). Reference-revision-r2 evaluation (card planning/reference-revision-2026-09-06.md): the standardised reference with the PI's cluster- and empty-tile-audit adjudications applied (-6 records, +14; 5,018 at marked centres, included whole at every R). Scored by evaluate\_detections.py (14 buffers, tile-level BCa 10,000 / seed 42, --mcc) -- one engine for the whole r2 chain.
- `g384-ov192-55map-n3-carried-posthoc-p0.15-k3-r2-gt`
  r2 board cell B-N3-carried (carried (post-hoc), F1@50 0.8477, tier via final\_board\_50m.json). Reference-revision-r2 evaluation (card planning/reference-revision-2026-09-06.md): the standardised reference with the PI's cluster- and empty-tile-audit adjudications applied (-6 records, +14; 5,018 at marked centres, included whole at every R). Scored by evaluate\_detections.py (14 buffers, tile-level BCa 10,000 / seed 42, --mcc) -- one engine for the whole r2 chain.
- `g384-ov192-55map-n3-oracle-p0.20-k3-r2-gt`
  r2 board cell B-N3-oracle (oracle (r2-reference argmax), F1@50 0.8507, tier via final\_board\_50m.json). Reference-revision-r2 evaluation (card planning/reference-revision-2026-09-06.md): the standardised reference with the PI's cluster- and empty-tile-audit adjudications applied (-6 records, +14; 5,018 at marked centres, included whole at every R). Scored by evaluate\_detections.py (14 buffers, tile-level BCa 10,000 / seed 42, --mcc) -- one engine for the whole r2 chain.
- `g384-ov192-55map-n5-carried-p0.15-k5-r2-gt`
  r2 board cell B-N5-carried (carried, F1@50 0.8503, tier via final\_board\_50m.json). Reference-revision-r2 evaluation (card planning/reference-revision-2026-09-06.md): the standardised reference with the PI's cluster- and empty-tile-audit adjudications applied (-6 records, +14; 5,018 at marked centres, included whole at every R). Scored by evaluate\_detections.py (14 buffers, tile-level BCa 10,000 / seed 42, --mcc) -- one engine for the whole r2 chain.
- `g384-ov192-55map-n5-oracle-p0.20-k5-r2-gt`
  r2 board cell B-N5-oracle (oracle (r2-reference argmax), F1@50 0.8516, tier via final\_board\_50m.json). Reference-revision-r2 evaluation (card planning/reference-revision-2026-09-06.md): the standardised reference with the PI's cluster- and empty-tile-audit adjudications applied (-6 records, +14; 5,018 at marked centres, included whole at every R). Scored by evaluate\_detections.py (14 buffers, tile-level BCa 10,000 / seed 42, --mcc) -- one engine for the whole r2 chain.
- `g384-ov192-55map-n1-verified37-oracle-p0.96-k1-r2-gt`
  r2 board cell FOURTH-N1-oracle (oracle (r2-reference argmax), F1@50 0.8352, tier via final\_board\_50m.json). Reference-revision-r2 evaluation (card planning/reference-revision-2026-09-06.md): the standardised reference with the PI's cluster- and empty-tile-audit adjudications applied (-6 records, +14; 5,018 at marked centres, included whole at every R). Scored by evaluate\_detections.py (14 buffers, tile-level BCa 10,000 / seed 42, --mcc) -- one engine for the whole r2 chain.
- `g384-ov192-55map-n10-verified37-carried-p0.98-k10-r2-gt`
  r2 board cell FOURTH-N10-carried (carried, F1@50 0.8728, tier via final\_board\_50m.json). Reference-revision-r2 evaluation (card planning/reference-revision-2026-09-06.md): the standardised reference with the PI's cluster- and empty-tile-audit adjudications applied (-6 records, +14; 5,018 at marked centres, included whole at every R). Scored by evaluate\_detections.py (14 buffers, tile-level BCa 10,000 / seed 42, --mcc) -- one engine for the whole r2 chain.
- `g384-ov192-55map-n10-verified37-oracle-p0.96-k9-r2-gt`
  r2 board cell FOURTH-N10-oracle (oracle (r2-reference argmax), F1@50 0.8813, tier via final\_board\_50m.json). Reference-revision-r2 evaluation (card planning/reference-revision-2026-09-06.md): the standardised reference with the PI's cluster- and empty-tile-audit adjudications applied (-6 records, +14; 5,018 at marked centres, included whole at every R). Scored by evaluate\_detections.py (14 buffers, tile-level BCa 10,000 / seed 42, --mcc) -- one engine for the whole r2 chain.
- `g384-ov192-55map-n3-verified37-oracle-p0.96-k3-r2-gt`
  r2 board cell FOURTH-N3-oracle (oracle (r2-reference argmax), F1@50 0.8747, tier via final\_board\_50m.json). Reference-revision-r2 evaluation (card planning/reference-revision-2026-09-06.md): the standardised reference with the PI's cluster- and empty-tile-audit adjudications applied (-6 records, +14; 5,018 at marked centres, included whole at every R). Scored by evaluate\_detections.py (14 buffers, tile-level BCa 10,000 / seed 42, --mcc) -- one engine for the whole r2 chain.
- `g384-ov192-55map-n5-verified37-oracle-p0.96-k5-r2-gt`
  r2 board cell FOURTH-N5-oracle (oracle (r2-reference argmax), tier via final\_board\_50m.json). Reference-revision-r2 evaluation (card planning/reference-revision-2026-09-06.md): the standardised reference with the PI's cluster- and empty-tile-audit adjudications applied (-6 records, +14; 5,018 at marked centres, included whole at every R). Scored by evaluate\_detections.py (14 buffers, tile-level BCa 10,000 / seed 42, --mcc) -- one engine for the whole r2 chain.

### 5.3 Decomposition note

Verbatim from `results/run-conditions.json` — the hand-authored record of how this run was decomposed and what was adjudicated:

> 55-map deployment portfolio (card planning/55map-portfolio-2026-08-25.md; predictions P1-P8 registered by commit before launch). Runs A (384/33.3%, 141,600 calls) and B (384/50%, 245,610) + the 96,195-call carry-forward verifier. Canonical extended-GT evaluations; the standardised-reference final-board cells register in Pass 2. Sweeps/ladders live under their analyses (PI ruling 2026-08-28). Reference-revision-r2 track (Session 149): the -r2-gt conditions score the same detection sets against reference revision r2 and supersede the -standardised-gt cells as the paper reference; see results/55maps-r2-ref-2026-09-06/, results/55map-final-board-r2-2026-09-06/ and planning/reference-revision-2026-09-06.md.

### 5.4 Waived evaluations (38, 1 distinct reason(s))

Scored evaluations under this run that no condition claims, each waived in `results/run-conditions.json` rather than left silent. Grouped by identical reason; where a reason covers more than 12 paths the first 12 are named and the decomposition carries the rest.

- **38 evaluation(s)** — uplift-supplement K=1 anchor (planning/uplift-supplement-2026-08-28.md; scored 5bd514542): an input to the supplement's pairing tables, on the reference of the stratum it pairs with; not a registered condition and not cited by the paper. Waived by PI ruling 2026-09-07 (planning/reference-revision-2026-09-06.md, register-verifier debt).
  - `results/uplift-supplement/k1-gapfill/stride-55map-2026-08-25__g384-ov128-55map-n10-carried-p0_15-k8-r2-gt/evaluation.json`
  - `results/uplift-supplement/k1-gapfill/stride-55map-2026-08-25__g384-ov128-55map-n10-carried-p0_15-k8-standardised-gt/evaluation.json`
  - `results/uplift-supplement/k1-gapfill/stride-55map-2026-08-25__g384-ov128-55map-n10-oracle-p0_15-k7-r2-gt/evaluation.json`
  - `results/uplift-supplement/k1-gapfill/stride-55map-2026-08-25__g384-ov128-55map-n10-oracle-p0_15-k7-standardised-gt/evaluation.json`
  - `results/uplift-supplement/k1-gapfill/stride-55map-2026-08-25__g384-ov128-55map-n3-carried-posthoc-p0_15-k3-r2-gt/evaluation.json`
  - `results/uplift-supplement/k1-gapfill/stride-55map-2026-08-25__g384-ov128-55map-n3-carried-posthoc-p0_15-k3-standardised-gt/evaluation.json`
  - `results/uplift-supplement/k1-gapfill/stride-55map-2026-08-25__g384-ov128-55map-n3-oracle-p0_20-k2-r2-gt/evaluation.json`
  - `results/uplift-supplement/k1-gapfill/stride-55map-2026-08-25__g384-ov128-55map-n3-oracle-p0_20-k2-standardised-gt/evaluation.json`
  - `results/uplift-supplement/k1-gapfill/stride-55map-2026-08-25__g384-ov128-55map-n5-carried-p0_15-k4-r2-gt/evaluation.json`
  - `results/uplift-supplement/k1-gapfill/stride-55map-2026-08-25__g384-ov128-55map-n5-carried-p0_15-k4-standardised-gt/evaluation.json`
  - `results/uplift-supplement/k1-gapfill/stride-55map-2026-08-25__g384-ov128-55map-n5-oracle-p0_15-k4-r2-gt/evaluation.json`
  - `results/uplift-supplement/k1-gapfill/stride-55map-2026-08-25__g384-ov128-55map-n5-oracle-p0_15-k4-standardised-gt/evaluation.json`
  - … and 26 more under the same waiver (full list in `results/run-conditions.json`, this run's `_ignored_evals`)

## 6. Analyses that read this run (12)

A run is linked to an analysis when the analysis's `conditions_compared` names one of this run's conditions. *Cells* is how many of the analysis's compared conditions come from this run, out of its total. *Signed* is the register's `manually_verified_at` stamp.

| Analysis | Cells | Type | Hypotheses | Registration | Paper section | Deviations | Signed | Output |
|---|---|---|---|---|---|---|---|---|
| `55map-final-board-2026-08-27` | 14 of 23 | leaderboard | `H13`, `H3` | post-hoc | Results | — | 2026-08-28T12:22:08Z | `results/55map-final-board-2026-08-27/final_board_50m.json` |
| `55map-final-board-r2-2026-09-06` | 18 of 35 | leaderboard | `H13`, `H3` | post-hoc | Results | — | 2026-09-07T08:36:56Z | `results/55map-final-board-r2-2026-09-06/final_board_50m.json` |
| `estimated-correction-r2` | 18 of 35 | diagnostic | `H13` | post-hoc | Results | — | 2026-09-07T08:36:56Z | `results/55map-final-board-r2-2026-09-06/estimated-correction.json` |
| `gemini37-55map-grid-2026-08-31` | 4 of 8 | comparison | — | post-hoc | Results | — | 2026-09-12T09:03:09Z | `results/gemini37-55map-2026-08-31` |
| `gemini37-55map-gridboard-2026-08-31` | 2 of 4 | leaderboard | — | post-hoc | Results | — | 2026-09-12T09:03:09Z | `results/gemini37-55map-2026-08-31/grid-board` |
| `k-ladder-2026-09-12` | 32 of 94 | comparison | `H3`, `H13` | post-hoc | Results | `E56`, `E85` | 2026-09-13T06:58:12Z | `results/k-ladder-2026-09-12/findings.md` |
| `sensitivity-mde-r2` | 18 of 35 | diagnostic | `H8`, `H9`, `H10`, `H12` | post-hoc | Appendix | — | 2026-09-07T08:36:56Z | `results/sensitivity-mde-2026-08-28/sensitivity-r2.json` |
| `stride55-a5-vs-b5-2026-08-27` | 2 of 2 | comparison | `H13` | post-hoc | Results | `Post-hoc to the card's declared comparison family; BH-adjusted within the expanded seven-test family (survives, rank 3).` | 2026-08-28T12:16:45Z | `results/stride55-2026-08-27/a5_vs_b5.json` |
| `stride55-ladder-2026-08-27` | 2 of 2 | comparison | `H13`, `H3` | registered-exploratory | Results | — | 2026-08-28T12:16:45Z | `results/stride55-2026-08-27/ladder.json` |
| `stride55-sweep-oracle-2026-08-27` | 4 of 4 | comparison | `H13` | registered-exploratory | Results | — | 2026-08-28T12:16:45Z | `results/stride55-2026-08-27/sweep_oracle.json` |
| `uplift-supplement-flatten` | 39 of 441 | diagnostic | — | post-hoc | Appendix | — | 2026-09-10T22:55:40Z | `results/uplift-supplement/conditions.csv` |
| `verifier-uplift-pairing` | 39 of 170 | comparison | `H2` | post-hoc | Appendix | — | 2026-09-12T06:04:30Z | `results/uplift-supplement/verifier-uplift.csv` |

## 7. Findings documents (2)

| Document | Named by |
|---|---|
| `results/k-ladder-2026-09-12/findings.md` | `k-ladder-2026-09-12` |
| `results/stride55-2026-08-27/findings.md` | `stride55-sweep-oracle-2026-08-27` |

## 8. Protocol errata

### 8.1 Registered as deviations (3)

Listed in the `deviations` field of an analysis that reads this run:

- **E56** — Verifier probability-threshold operating points are in-sample (test-set-selected), not calibrated
- **E85** — The temperature study's five consensus conditions were labelled N = 30 but read a 5-pass union — relabelled `consensus-{1..5}of5`; no measured value changes
- **Post-hoc to the card's declared comparison family; BH-adjusted within the expanded seven-test family (survives, rank 3).** — not supplied

## 9. Documents and structure in the run directory

| Document class | Filename | Count |
|---|---|---:|
| per-pass/per-run intent | `experiment_intent.md` | 38 |

These classes are in Revision-Policy scope going forward (`docs/methodology/output-directory-standard.md` § "Documents in Revision Policy Scope").

### 9.1 Registered pools

| Proposer pool | Modality | Path within the run directory |
|---|---|---|
| `g384_ov128_55map` | text | `g384_ov128_55map` |
| `g384_ov192_55map` | text | `g384_ov192_55map` |

3 registered verifier-pass directory/directories; see `results/run-conditions.json` for the full list.

## 10. Provenance of this report

This report is a projection. Every figure above is read from one of the committed inputs below; nothing is estimated, and a figure that is not on file is written **not supplied** with its reason.

| Field | Value |
|---|---|
| Generator | `scripts/generate_run_reports.py` v1.1.0 |
| Source commit | `a8c03bb9e` |
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
