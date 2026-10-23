# Sweep optimism of the screen cells (Efron–Gong, argmax replayed per tile resample)

> **Last revised**: 2026-10-15 (original publication). Instrument: `scripts/selection_aware_intervals.py --sweep-union` (the verifier (prob_t × min_votes) sweep rebuilt in process as the candidate set; 10,000 tile resamples, seed 42, 20 m). Each cell is run on its committed frame (grid-common; gate: the screen's committed `sweep_20m.csv` reproduced row for row) and on the board frame (`era2-b-487`; gate: the argmax equals the board cell's evaluation to four decimals). See [§ Changelog](#changelog).

Optimism = apparent F1 − the mean out-of-resample F1 of the replayed argmax; corrected = apparent − optimism. Argmax stability = the share of resamples that pick the committed operating point.

| cell | frame | candidates | apparent F1 | optimism (MCSE) | corrected F1 | selection-aware 95 % | argmax stability | gates |
|---|---|---:|---:|---:|---:|---|---:|---|
| `gemini37-image-gs-2026-09-01__g37-image-k5-verified-carried-p0_10-k5` | committed | 75 | 0.9381 | +0.0011 (0.00010) | **0.9369** | [0.9157, 0.9557] | 0.512 (6 winners) | sweep 75 rows; anchor Δ -2.7e-05 |
| `gemini37-image-gs-2026-09-01__g37-image-k5-verified-carried-p0_10-k5` | board | 75 | 0.9306 | +0.0011 (0.00011) | **0.9295** | [0.9068, 0.9496] | 0.512 (6 winners) | — |
| `gemini37-image-gs-2026-09-01__g37-image-k5-verified-swap37-p0_90-k5` | committed | 80 | 0.9408 | +0.0018 (0.00010) | **0.9390** | [0.9179, 0.9581] | 0.422 (10 winners) | sweep 80 rows; anchor Δ -3.3e-05 |
| `gemini37-image-gs-2026-09-01__g37-image-k5-verified-swap37-p0_90-k5` | board | 80 | 0.9332 | +0.0018 (0.00011) | **0.9314** | [0.9092, 0.9517] | 0.420 (12 winners) | anchor Δ -2.0e-05 |
| `gemini37-screen-2026-08-28__g37-text-k10-verified-carried-p0_10-k10` | committed | 130 | 0.9243 | +0.0024 (0.00011) | **0.9219** | [0.8972, 0.9429] | 0.615 (14 winners) | sweep 130 rows; anchor Δ +3.1e-05 |
| `gemini37-screen-2026-08-28__g37-text-k10-verified-carried-p0_10-k10` | board | 130 | 0.9169 | +0.0024 (0.00011) | **0.9144** | [0.8896, 0.9361] | 0.604 (14 winners) | anchor Δ -4.1e-05 |
| `gemini37-screen-2026-08-28__g37-text-k5-verified-carried-p0_10-k5` | committed | 75 | 0.9238 | +0.0009 (0.00011) | **0.9229** | [0.9009, 0.9425] | 0.921 (7 winners) | sweep 75 rows; anchor Δ -2.3e-05 |
| `gemini37-screen-2026-08-28__g37-text-k5-verified-carried-p0_10-k5` | board | 75 | 0.9165 | +0.0008 (0.00011) | **0.9157** | [0.8924, 0.9360] | 0.924 (7 winners) | anchor Δ -2.1e-05 |
| `gemini37-screen-2026-08-28__g37-text-k5-verified-swap37-p0_80-k5` | committed | 95 | 0.9364 | +0.0020 (0.00010) | **0.9344** | [0.9134, 0.9531] | 0.290 (12 winners) | sweep 95 rows; anchor Δ +1.6e-05 |
| `gemini37-screen-2026-08-28__g37-text-k5-verified-swap37-p0_80-k5` | board | 95 | 0.9289 | +0.0020 (0.00010) | **0.9269** | [0.9051, 0.9465] | 0.291 (12 winners) | anchor Δ -9.2e-07 |
| `gemini37-screen-2026-08-28__g37-text-k5-verified-swap38-p0_88-k5` | committed | 95 | 0.9358 | +0.0021 (0.00010) | **0.9337** | [0.9126, 0.9530] | 0.315 (15 winners) | sweep 95 rows; anchor Δ +2.3e-05 |
| `gemini37-screen-2026-08-28__g37-text-k5-verified-swap38-p0_88-k5` | board | 95 | 0.9282 | +0.0021 (0.00011) | **0.9262** | [0.9041, 0.9462] | 0.315 (15 winners) | anchor Δ +4.1e-05 |
| `grid-2026-08-18__g384-ov192-k10-verified-p0_15-k10` | committed | 140 | 0.9017 | +0.0021 (0.00013) | **0.8995** | [0.8725, 0.9237] | 0.512 (15 winners) | sweep 140 rows; anchor Δ -2.1e-05 |
| `grid-2026-08-18__g384-ov192-k10-verified-p0_15-k10` | board | 140 | 0.8942 | +0.0021 (0.00013) | **0.8920** | [0.8639, 0.9173] | 0.511 (15 winners) | anchor Δ -2.6e-05 |
| `grid-2026-08-18__g384-ov192-k10-verified37-p0_98-k10` | committed | 200 | 0.9220 | +0.0039 (0.00011) | **0.9180** | [0.8936, 0.9405] | 0.430 (23 winners) | sweep 200 rows; anchor Δ -4.9e-05 |
| `grid-2026-08-18__g384-ov192-k10-verified37-p0_98-k10` | board | 200 | 0.9144 | +0.0039 (0.00011) | **0.9104** | [0.8864, 0.9313] | 0.404 (23 winners) | — |
| `image-b-gs-2026-08-28__g384-ov192-image-high-k10-verified-p0_20-k8` | committed | 190 | 0.8389 | +0.0062 (0.00016) | **0.8327** | [0.7996, 0.8647] | 0.372 (12 winners) | sweep 190 rows; anchor Δ +4.2e-05 |
| `image-b-gs-2026-08-28__g384-ov192-image-high-k10-verified-p0_20-k8` | board | 190 | 0.8319 | +0.0062 (0.00016) | **0.8258** | [0.7918, 0.8586] | 0.374 (13 winners) | anchor Δ +4.3e-05 |
| `image-b-gs-2026-08-28__g384-ov192-image-min-k10-verified-p0_15-k9` | committed | 140 | 0.8458 | +0.0044 (0.00017) | **0.8414** | [0.8063, 0.8741] | 0.509 (7 winners) | sweep 140 rows; anchor Δ -1.7e-05 |
| `image-b-gs-2026-08-28__g384-ov192-image-min-k10-verified-p0_15-k9` | board | 140 | 0.8387 | +0.0045 (0.00017) | **0.8342** | [0.7982, 0.8679] | 0.498 (7 winners) | anchor Δ +9.7e-06 |

Board frame: optimism ranges +0.0008 to +0.0062 over 10 cells (the board's own tier margins are in `tiering_20m.json`).

## Changelog

### 2026-10-15 — Original publication

Run on sapphire (S152) for the board's symmetry fix (card changelog 2026-09-10 later).
