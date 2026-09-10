# Sweep optimism of the screen cells (Efron–Gong, argmax replayed per tile resample)

> **Last revised**: 2026-09-10 (original publication). Instrument: `scripts/selection_aware_intervals.py --sweep-union` (the verifier (prob_t × min_votes) sweep rebuilt in process as the candidate set; 10,000 tile resamples, seed 42, 20 m). Each cell is run on its committed frame (grid-common; gate: the screen's committed `sweep_20m.csv` reproduced row for row) and on the board frame (`era2-b-487`; gate: the argmax equals the board cell's evaluation to four decimals). See [§ Changelog](#changelog).

Optimism = apparent F1 − the mean out-of-resample F1 of the replayed argmax; corrected = apparent − optimism. Argmax stability = the share of resamples that pick the committed operating point.

| cell | frame | candidates | apparent F1 | optimism (MCSE) | corrected F1 | selection-aware 95 % | argmax stability | gates |
|---|---|---:|---:|---:|---:|---|---:|---|
| `gemini37-image-gs-2026-09-01__g37-image-k5-verified-carried-p0_10-k5` | committed | 75 | 0.9254 | +0.0016 (0.00012) | **0.9238** | [0.8995, 0.9457] | 0.772 (6 winners) | sweep 75 rows; anchor Δ +7.9e-06 |
| `gemini37-image-gs-2026-09-01__g37-image-k5-verified-carried-p0_10-k5` | board | 75 | 0.9179 | +0.0016 (0.00013) | **0.9163** | [0.8908, 0.9393] | 0.767 (6 winners) | anchor Δ +1.9e-05 |
| `gemini37-image-gs-2026-09-01__g37-image-k5-verified-swap37-p0_90-k5` | committed | 80 | 0.9308 | +0.0017 (0.00011) | **0.9291** | [0.9057, 0.9502] | 0.418 (11 winners) | sweep 80 rows; anchor Δ +3.2e-05 |
| `gemini37-image-gs-2026-09-01__g37-image-k5-verified-swap37-p0_90-k5` | board | 80 | 0.9233 | +0.0017 (0.00012) | **0.9215** | [0.8966, 0.9439] | 0.414 (14 winners) | anchor Δ -4.4e-05 |
| `gemini37-screen-2026-08-28__g37-text-k10-verified-carried-p0_10-k10` | committed | 130 | 0.9142 | +0.0013 (0.00013) | **0.9129** | [0.8865, 0.9359] | 0.884 (12 winners) | sweep 130 rows; anchor Δ +1.9e-05 |
| `gemini37-screen-2026-08-28__g37-text-k10-verified-carried-p0_10-k10` | board | 130 | 0.9068 | +0.0013 (0.00013) | **0.9054** | [0.8788, 0.9292] | 0.879 (12 winners) | anchor Δ -4.0e-05 |
| `gemini37-screen-2026-08-28__g37-text-k5-verified-carried-p0_10-k5` | committed | 75 | 0.9139 | +0.0007 (0.00012) | **0.9132** | [0.8882, 0.9349] | 0.942 (7 winners) | sweep 75 rows; anchor Δ -7.9e-06 |
| `gemini37-screen-2026-08-28__g37-text-k5-verified-carried-p0_10-k5` | board | 75 | 0.9066 | +0.0006 (0.00012) | **0.9060** | [0.8805, 0.9283] | 0.945 (7 winners) | anchor Δ +5.9e-06 |
| `gemini37-screen-2026-08-28__g37-text-k5-verified-swap37-p0_80-k5` | committed | 95 | 0.9265 | +0.0021 (0.00011) | **0.9244** | [0.9010, 0.9454] | 0.287 (12 winners) | sweep 95 rows; anchor Δ -1.2e-05 |
| `gemini37-screen-2026-08-28__g37-text-k5-verified-swap37-p0_80-k5` | board | 95 | 0.9190 | +0.0020 (0.00012) | **0.9169** | [0.8928, 0.9385] | 0.288 (12 winners) | anchor Δ -1.9e-05 |
| `gemini37-screen-2026-08-28__g37-text-k5-verified-swap38-p0_88-k5` | committed | 95 | 0.9258 | +0.0021 (0.00011) | **0.9237** | [0.9000, 0.9453] | 0.314 (14 winners) | sweep 95 rows; anchor Δ -4.9e-06 |
| `gemini37-screen-2026-08-28__g37-text-k5-verified-swap38-p0_88-k5` | board | 95 | 0.9182 | +0.0020 (0.00012) | **0.9162** | [0.8917, 0.9385] | 0.313 (14 winners) | anchor Δ +2.4e-05 |
| `grid-2026-08-18__g384-ov192-k10-verified-p0_15-k10` | committed | 140 | 0.8961 | +0.0017 (0.00013) | **0.8944** | [0.8664, 0.9194] | 0.548 (14 winners) | sweep 140 rows; anchor Δ +3.5e-05 |
| `grid-2026-08-18__g384-ov192-k10-verified-p0_15-k10` | board | 140 | 0.8886 | +0.0018 (0.00014) | **0.8869** | [0.8574, 0.9128] | 0.550 (14 winners) | anchor Δ +2.3e-05 |
| `grid-2026-08-18__g384-ov192-k10-verified37-p0_98-k10` | committed | 200 | 0.9140 | +0.0035 (0.00012) | **0.9105** | [0.8837, 0.9343] | 0.507 (19 winners) | sweep 200 rows; anchor Δ +4.9e-06 |
| `grid-2026-08-18__g384-ov192-k10-verified37-p0_98-k10` | board | 200 | 0.9062 | +0.0035 (0.00012) | **0.9027** | [0.8750, 0.9271] | 0.485 (18 winners) | anchor Δ +1.2e-05 |
| `image-b-gs-2026-08-28__g384-ov192-image-high-k10-verified-p0_20-k8` | committed | 190 | 0.8333 | +0.0056 (0.00017) | **0.8277** | [0.7939, 0.8602] | 0.419 (13 winners) | sweep 190 rows; anchor Δ +3.3e-05 |
| `image-b-gs-2026-08-28__g384-ov192-image-high-k10-verified-p0_20-k8` | board | 190 | 0.8263 | +0.0056 (0.00017) | **0.8208** | [0.7862, 0.8539] | 0.422 (13 winners) | anchor Δ +4.7e-05 |
| `image-b-gs-2026-08-28__g384-ov192-image-min-k10-verified-p0_15-k9` | committed | 140 | 0.8412 | +0.0046 (0.00017) | **0.8366** | [0.8003, 0.8699] | 0.489 (6 winners) | sweep 140 rows; anchor Δ +1.2e-05 |
| `image-b-gs-2026-08-28__g384-ov192-image-min-k10-verified-p0_15-k9` | board | 140 | 0.8341 | +0.0046 (0.00017) | **0.8295** | [0.7926, 0.8634] | 0.479 (6 winners) | anchor Δ +3.5e-05 |

Board frame: optimism ranges +0.0006 to +0.0056 over 10 cells (the board's own tier margins are in `tiering_20m.json`).

## Changelog

### 2026-09-10 — Original publication

Run on sapphire (S152) for the board's symmetry fix (card changelog 2026-09-10 later).
