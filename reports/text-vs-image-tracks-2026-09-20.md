# Text track vs image track — Gemini 3.7 Flash, 55-map corpus, K/N = 1, 3, 5

> **Last revised**: 2026-09-20 (original publication). See [§ Changelog](#changelog) for revision history.

Prepared for the PI's question of 2026-09-20: what does adding the 17-exemplar
few-shot image library to the 3.7 Flash proposer buy on the 55-map corpus, at
K = 1, 3, and 5, carried and at the oracle, and what does each run cost. Every
number carries the path it was read from. Assembled by an Opus-class agent
under Session 156 (Fable) and spot-checked against the cited sources
(`results/55map-final-board-r2-2026-09-06/cells/ARM2-N5-carried/evaluation.md`,
`outputs/gemini37-image-55map-2026-09-13/post_run_report.md` lines 48–81,
`reports/r7-gaps-deltas-2026-09-11.md` line 183,
`results/gemini37-55map-2026-08-31/findings.md` lines 92–97).

## 0. Corrections to the brief's premises (read first)

| Premise in the brief | What the repository holds |
|---|---|
| Text campaign results at `results/gemini37-55map-2026-08-29/` | **Does not exist.** The results tree is `results/gemini37-55map-2026-08-31/`; only the *outputs* tree is `outputs/gemini37-55map-2026-08-29/`. The skew is deliberate and minuted: `outputs/gemini37-55map-2026-08-29/post_run_report.md:23`. |
| Text cells named `ARM2-N3-carried`, `ARM2-N5-oracle` etc. in a `cells/` dir with `cells_manifest.json` / `sweeps.json` | The text campaign has **no** `cells/` directory and no `cells_manifest.json`. Its rung results live in `results/gemini37-55map-2026-08-31/ladder/ladder.json`, `.../ladder/ladder_sweep_50m.csv`, `.../sweeps/sweep_oracle.json` and `.../grid-board/grid_board.json`. The `ARM2-N*` labels exist only as **r2-board** cells at `results/55map-final-board-r2-2026-09-06/cells/`. |
| "FOURTH" may be the N = 1 cell | **No.** FOURTH is the fourth cell of the 2 × 2 grid: **Gemini-3 Run B proposer pool × 3.7 verifier** (`results/gemini37-55map-2026-08-31/sweeps/sweep_oracle.json`, `runs.fourth.role` = "Gemini-3 Run B K=10 union + 3.7 verifier"; registered `proposer_pool: "g384_ov192_55map"`, `n_candidates: 57482` at `results/run-conditions.json:14361-14398`). `FOURTH-N1-oracle` is the N = 1 rung **of that Gemini-3 pool**, not of the 3.7 text track. The image campaign's P1 comparator is that cell, not a text-track cell. |
| Text track uses the same K convention | **Yes** — first-N pooled union, unanimity `k = N` at the carried point, same (prob_t, min_votes) sweep grid with min_votes < N allowed. Detail and the one real difference in § 4.1. |

**Reference mismatch is the governing caveat.** The text campaign's primary chain is the **canonical adjudicated extended GT** (5,160 references @ 50 m) with **corrected**-F1; the image campaign is scored entirely on the **r2** reference (`best-available-gt-55maps-r2.geojson`, 5,018 references) with plain micro-F1. The only like-for-like comparison runs through the four text cells that were re-scored on r2 by the same engine. Tables below are split accordingly.

## 1. Outcomes

### 1.1 r2 basis — same engine, same reference, directly comparable

`scripts/evaluate_detections.py`, 14 buffers, `best-available-gt-55maps-r2.geojson` (5,018 refs), 8,541-tile frame, tile-level BCa bootstrap 10,000 / seed 42, `--mcc`.

| Track | Rung | Point | Operating point (prob, min votes) | n det | P [95 % CI] | R [95 % CI] | F1@50 m [95 % CI] | tile-MCC [95 % CI] |
|---|---|---|---|---:|---|---|---|---|
| Text | N=1 | carried | — | — | — | — | **not scored on r2** | **not scored on r2** |
| Text | N=1 | F1-oracle | (0.98, k1) | 5021 | 0.8608 [0.8508, 0.8704] | 0.8613 [0.8506, 0.8718] | 0.8610 [0.8534, 0.8684] | 0.7422 [0.7298, 0.7551] |
| Text | N=1 | MCC-oracle | — | — | — | — | **no such cell** | **no such cell** |
| Text | N=3 | carried | — | — | — | — | **not scored on r2** | **not scored on r2** |
| Text | N=3 | F1-oracle | (0.95, k3) | 5097 | 0.8780 [0.8680, 0.8872] | 0.8918 [0.8816, 0.9012] | 0.8848 [0.8770, 0.8919] | 0.7163 [0.7017, 0.7307] |
| Text | N=3 | MCC-oracle | — | — | — | — | **no such cell** | **no such cell** |
| Text | N=5 | carried | (0.80, k5) | 5003 | 0.8841 [0.8744, 0.8933] | 0.8814 [0.8706, 0.8915] | **0.8827** [0.8749, 0.8899] | **0.7063** [0.6917, 0.7211] |
| Text | N=5 | F1-oracle | (0.95, k5) | 4924 | 0.8956 [0.8862, 0.9043] | 0.8788 [0.8679, 0.8890] | 0.8871 [0.8794, 0.8943] | 0.7147 [0.7004, 0.7288] |
| Text | N=5 | MCC-oracle | — | — | — | — | **no such cell** | **no such cell** |
| Image | K=1 | carried | (0.88, k1) | 5997 | 0.8007 [0.7903, 0.8109] | 0.9570 [0.9509, 0.9624] | **0.8719** [0.8650, 0.8784] | **0.7569** [0.7432, 0.7702] |
| Image | K=1 | F1-oracle | (0.95, k1) | 5938 | 0.8065 [0.7962, 0.8166] | 0.9544 [0.9482, 0.9600] | 0.8742 [0.8673, 0.8807] | 0.7594 [0.7459, 0.7725] |
| Image | K=1 | MCC-oracle | (0.98, k1) | 5322 | 0.8472 [0.8366, 0.8575] | 0.8986 [0.8897, 0.9069] | 0.8721 [0.8651, 0.8789] | 0.7614 [0.7491, 0.7737] |
| Image | K=3 | carried | (0.88, k3) | 5357 | 0.8908 [0.8820, 0.8993] | 0.9510 [0.9447, 0.9568] | **0.9199** [0.9142, 0.9254] | **0.7648** [0.7516, 0.7776] |
| Image | K=3 | F1-oracle | (0.90, k3) | 5343 | 0.8926 [0.8837, 0.9009] | 0.9504 [0.9441, 0.9562] | 0.9206 [0.9148, 0.9259] | 0.7654 [0.7524, 0.7784] |
| Image | K=3 | MCC-oracle | (0.96, **k2**) | 5167 | 0.8754 [0.8657, 0.8844] | 0.9014 [0.8928, 0.9099] | 0.8882 [0.8816, 0.8946] | 0.7656 [0.7534, 0.7780] |
| Image | K=5 | carried | (0.90, k5) | 5219 | 0.9092 [0.9010, 0.9172] | 0.9456 [0.9390, 0.9517] | **0.9270** [0.9215, 0.9322] | **0.7659** [0.7528, 0.7790] |
| Image | K=5 | F1-oracle | (0.95, k5) | 5197 | 0.9121 [0.9039, 0.9199] | 0.9446 [0.9381, 0.9507] | 0.9280 [0.9225, 0.9331] | 0.7681 [0.7552, 0.7811] |
| Image | K=5 | MCC-oracle | (0.95, k5) — coincides with F1-oracle | 5197 | 0.9121 [0.9039, 0.9199] | 0.9446 [0.9381, 0.9507] | 0.9280 [0.9225, 0.9331] | 0.7681 [0.7552, 0.7811] |

**Sources.**

- Text r2 cells: `results/55map-final-board-r2-2026-09-06/cells/ARM2-N1-oracle/evaluation.json`, `.../ARM2-N3-oracle/evaluation.json`, `.../ARM2-N5-carried/evaluation.json`, `.../ARM2-N5-oracle/evaluation.json` — key path `summary.buffers[buffer_metres==50]` (`f1`, `f1_ci_lower/upper`, `precision`, `p_ci_*`, `recall`, `r_ci_*`) and `summary.tile_classification.mcc.{point,ci_lower,ci_upper}`. Same numbers tabulated at `outputs/gemini37-55map-2026-08-29/post_run_report.md:80-91` (registered conditions `arm2-n1-oracle-p0.98-k1-r2-gt`, `arm2-n3-oracle-p0.95-k3-r2-gt`, `arm2-n5-carried-p0.80-k5-r2-gt`, `arm2-n5-oracle-p0.95-k5-r2-gt`), and the `evaluation.md` 50 m rows at line 17 of each cell directory.
- Image cells: `results/gemini37-image-55map-2026-09-13/cells/IMG-ARM2-K{1,3,5}-{carried,f1-oracle,mcc-oracle}/evaluation.json`, same key paths; `evaluation.md:17` in each; operating points and n from `results/gemini37-image-55map-2026-09-13/cells_manifest.json` (`cells[].point`, `cells[].n_detections`); tp/fp/fn and tile confusion from `results/gemini37-image-55map-2026-09-13/sweeps.json` (`rungs.IMG-ARM2-K*.{carried,f1_oracle,mcc_oracle}`); narrative table at `results/gemini37-image-55map-2026-09-13/findings.md:89-106`.
- Registered image labels: `results/run-conditions.json`, e.g. `img-arm2-k5-carried-p0.90-k5-r2-gt` (`n_candidates` 9173), `img-arm2-k3-carried-p0.88-k3-r2-gt` (8337), `img-arm2-k1-carried-p0.88-k1-r2-gt` (6985).

### 1.2 Text track, canonical chain — the only place a text **carried** point exists at N = 1 and N = 3

Corrected-F1 @ 50 m against the canonical adjudicated extended GT (5,160 refs). **No tile-MCC and no CIs on this chain for these rungs.**

| Rung | Point | Operating point | n det | tp | fp | fn | P | R | corrected-F1@50 |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| N=1 | carried-**analogue** | (0.80, k1) | 5936 | 4672 | 1264 | 488 | 0.7871 | 0.9054 | 0.8421 |
| N=1 | F1-oracle | (0.98, k1) | 5021 | 4359 | 662 | 801 | 0.8682 | 0.8448 | 0.8563 |
| N=3 | carried-**analogue** | (0.80, k3) | 5187 | 4524 | 663 | 636 | 0.8722 | 0.8767 | 0.8745 |
| N=3 | F1-oracle | (0.95, k3) | 5097 | 4508 | 589 | 652 | 0.8844 | 0.8736 | 0.8790 |
| N=5 | **carried** (committed) | (0.80, k5) | 5003 | 4453 | 550 | 707 | 0.8901 | 0.8630 | 0.8763 |
| N=5 | F1-oracle | (0.95, k5) | 4924 | 4440 | 484 | 720 | 0.9017 | 0.8605 | 0.8806 |

**Sources.** N = 1 / N = 3 rows: `results/gemini37-55map-2026-08-31/ladder/ladder_sweep_50m.csv` (rows `arm2,1,0.8,1,…`, `arm2,1,0.98,1,…`, `arm2,3,0.8,3,…`, `arm2,3,0.95,3,…`); oracles also at `results/gemini37-55map-2026-08-31/ladder/ladder.json` key `arms.arm2.{"1","3"}.oracle`. N = 5 rows: `results/gemini37-55map-2026-08-31/sweeps/sweep_oracle.json` key `runs.arm2.{carried,oracle}`. Labels, bases and tiers: `results/gemini37-55map-2026-08-31/grid-board/grid_board.json` `cells[]` — `arm2-N1-carried` (index 12, `basis: "carried-analogue"`), `arm2-N3-carried` (index 4, `"carried-analogue"`), `arm2-N5-carried` (index 2, `"carried"`), `arm2-N3-oracle` (1), `arm2-N5-oracle` (0), `arm2-N1-oracle` (8). Union sizes 8,426 / 11,079 / 12,715 at `results/gemini37-55map-2026-08-31/findings.md:101-103`.

Text N = 5 carried also exists on the **standardised** reference: F1@50 0.8825 [0.8746, 0.8897], tile-MCC 0.707 — `results/gemini37-55map-2026-08-31/arm2/g384_ov192_55map_g37/standardised-ref/evaluation.md:17`.

## 2. Costs (audited, USD)

All figures are audited per-response usage priced at flex (0.5 ×) with thinking billed at the output rate; rates `gemini-3.7-flash` 0.75 / 3.75 and `gemini-3-flash-preview` 0.50 / 3.00 per 1 M, `scripts/lib_llm_metadata.py:1045,1054-1055`. Method: `reports/r7-gaps-deltas-2026-09-11.md:47-77` (§ 2.1). **No `run.meta` `cost_estimate` is used anywhere below** — the text campaign's own recorded sum (US$82.6183, `outputs/gemini37-55map-2026-08-29/post_run_report.md:71`) is explicitly disclaimed in that file at line 73.

### 2.1 Proposer, per pass (not a block price — each pass audits separately)

| Pass | Text (3.7, brief-text, flex) | Image (3.7, brief-text-image) |
|---|---:|---:|
| 1 | 28.6890 | 81.9283 (flex) |
| 2 | 28.7708 | 81.8712 (flex) |
| 3 | 28.8562 | 81.8313 (flex) |
| 4 | 28.9153 | 61.8648 (**Batch API**) |
| 5 | 29.0426 | 61.9455 (**Batch API**) |
| **Total, 5 passes** | **144.2739** | **369.4409** |

Text per-pass figures are the sum of that pass's primary and recovery metas from the audited table at `reports/r7-gaps-deltas-2026-09-11.md:110-123` (`run_1` 28.30 + `run_1_recovery` 0.39; `run_2` 28.65 + 0.12; `run_3` 10.52 + `run_3_recovery` 18.32 + `run_3_recovery2` 0.01; `run_4` 28.90 + 0.01; `run_5` 29.04 + 0.00). Re-derived from the committed metas under `outputs/gemini37-55map-2026-08-29/g384_ov192_55map_g37/run_*/…meta.json` (`per_item_metadata[].tokens`, unique `item_id` with `finish_reason == "success"`), reproducing the published total to **US$144.2739** against the report's US$144.27.

Image per-pass figures: `outputs/gemini37-image-55map-2026-09-13/post_run_report.md:48,49,50,66,67`; three-pass subtotal line 51 (245.6307), five-pass pool line 69 (369.4409).

### 2.2 Verifier legs (arm 2 = 3.7 verifier)

| Track | Rung | Candidates | Audited USD | Source |
|---|---|---:|---:|---|
| Text | N=1 | — (inherited) | **0.00 incremental** | rung derived by probability inheritance, not re-verified — see note |
| Text | N=3 | — (inherited) | **0.00 incremental** | same |
| Text | N=5 | 12,715 | **14.3055** | `reports/r7-gaps-deltas-2026-09-11.md:145`; re-derived from `outputs/gemini37-55map-2026-08-29/verifier/g384_ov192_55map_g37/verify_arm2/run.meta.json` `usage_stats` (in 22,785,280 / out 1,608,503 / thoughts 1,464,066 / cached 0) → 0.5 × (22.78528 × 0.75 + 3.072569 × 3.75) = 14.3055 |
| Image | K=1 | 6,985 | **7.7028** | `outputs/gemini37-image-55map-2026-09-13/post_run_report.md:56`; = main 7.6875 + cleanup 0.0153, per lines 186-188 |
| Image | K=3 | 8,337 | **9.2650** | same file, line 58 |
| Image | K=5 | 9,173 | **10.1788** | same file, lines 73 and 244; re-derived from `outputs/gemini37-image-55map-2026-09-13/verifier/g384_ov192_55map_g37img/verify_k5_arm2/run.meta.json` `usage_stats` → 10.1788 exactly |

**The text track ran exactly one arm-2 verifier leg**, over the full N = 5 union of 12,715 candidates. Its N = 1 and N = 3 rungs were **not verified separately**: they are built by restricting that leg's per-candidate probabilities to the first-N union via ≤ 10 m inheritance (54 candidates unmatched at N = 1, 3 at N = 3) — `results/gemini37-55map-2026-08-31/findings.md:92-97`. The image track, by contrast, ran a **separate verifier leg per rung** over each rung's own union. Below the single US$14.3055 leg is charged to every text rung, because no text rung could exist without it; the alternative apportionment (0.00 at N = 1 and N = 3) is given in the delta table.

### 2.3 Per-rung totals

| Rung | Text proposer | Text verifier | **Text total** | Image proposer | Image verifier | **Image total** |
|---|---:|---:|---:|---:|---:|---:|
| K/N = 1 | 28.6890 | 14.3055 | **42.9945** | 81.9283 | 7.7028 | **89.6311** |
| K/N = 3 | 86.3160 | 14.3055 | **100.6215** | 245.6307 | 9.2650 | **254.8957** |
| K/N = 5 | 144.2739 | 14.3055 | **158.5794** | 369.4409 | 10.1788 | **379.6197** |

### 2.4 Campaign totals

| Campaign | Audited USD | Composition | Source |
|---|---:|---|---|
| Text (`gemini37-55map-2026-08-29`) | **167.47** | proposer 144.27 + arm-1 verifier 8.89 + arm-2 verifier 14.31 | `reports/r7-gaps-deltas-2026-09-11.md:183` (and §2.3 table line 145 for the arms) |
| Image (`gemini37-image-55map-2026-09-13`) | **415.3174** | 369.4409 proposer + 4.9626 + 7.7028 + 5.9058 + 9.2650 + 6.4896 + 10.1788 (six verifier legs) + 0.4417 + 0.6804 (GS calibration) + ≈0.025 (smoke) + 0.2248 (batch-vs-flex probe) — sums to 415.3174 exactly | `outputs/gemini37-image-55map-2026-09-13/post_run_report.md:81`; components at lines 44, 45, 47, 55-58, 69, 72, 73, 78 |

⚠ The text campaign's US$144.27 proposer figure, and hence US$167.47, are a **lower bound**: two aborted partial runs (`g384_ov192_55map_g37/archive-run2-partial-aborted-2026-08-30/`, `archive-run3-partial-aborted-2026-08-30/`) consumed tokens with no meta on file — `reports/r7-gaps-deltas-2026-09-11.md:210-219`.

⚠ The image K = 1 and K = 3 **arm-2 main-pass metas are absent from the working tree**: `.gitignore:140` excludes `outputs/**/*.pre-cleanup-*.backup`, and only the 13-item and 1-item cleanup metas (US$0.0153 and US$0.0012) survive on disk. US$7.7028 and US$9.2650 are therefore citable from `post_run_report.md:56,58,186-188` but **not re-derivable from committed files**. Every other leg in this report was re-derived from source.

## 3. Delta — image minus text

### 3.1 Like-for-like (r2), carried vs carried

| Rung | Δ F1@50 m | Δ tile-MCC | Δ cost (USD) |
|---|---:|---:|---:|
| 1 | **not available** (no text r2 carried cell) | **not available** | +46.6366 |
| 3 | **not available** (no text r2 carried cell) | **not available** | +154.2743 |
| 5 | 0.9270 − 0.8827 = **+0.0443** | 0.7659 − 0.7063 = **+0.0596** | +221.0405 |

### 3.2 Nearest available (r2): image **carried** vs text **F1-oracle** — flatters the text track

| Rung | Δ F1@50 m | Δ tile-MCC | Δ cost (USD), verifier charged to all text rungs | Δ cost, text verifier charged only at N = 5 |
|---|---:|---:|---:|---:|
| 1 | 0.8719 − 0.8610 = **+0.0109** | 0.7569 − 0.7422 = **+0.0147** | +46.6366 | +60.9421 |
| 3 | 0.9199 − 0.8848 = **+0.0351** | 0.7648 − 0.7163 = **+0.0485** | +154.2743 | +168.5797 |
| 5 | 0.9270 − 0.8871 = **+0.0399** | 0.7659 − 0.7147 = **+0.0512** | +221.0405 | +221.0405 |

The K = 3 row reproduces the image campaign's own preregistered P3 reading (+0.0351 against `ARM2-N3-oracle` 0.8848, BH *p* < 0.0001) — `results/gemini37-image-55map-2026-09-13/findings.md:31` (P3 row) and `:50`.

Proposer-only cost deltas, the library's raw price: +53.2393 (K = 1), +159.3148 (K = 3), +225.1672 (K = 5).

## 4. Caveats

**4.1 Reference and metric instruments differ between the tracks' primary chains.** The text campaign's headline chain is canonical adjudicated extended GT (5,160 refs, **corrected**-F1); the image campaign is r2 only (5,018 refs, plain micro-F1). Sources: `results/gemini37-55map-2026-08-31/findings.md:17-33`; `results/gemini37-image-55map-2026-09-13/findings.md:21-25`; `results/gemini37-image-55map-2026-09-13/sweeps.json` key `reference` = `"r2"`. Only § 1.1 is cross-track comparable. The instrument offset is not negligible: the same text N = 5 carried detections read 0.8763 canonical vs 0.8827 on r2.

**4.2 The text track has no carried cell on r2 at N = 1 or N = 3, and no MCC-oracle cells at all.** The r2 board (`results/55map-final-board-r2-2026-09-06/cells/`) holds `ARM2-N1-oracle`, `ARM2-N3-oracle`, `ARM2-N5-carried`, `ARM2-N5-oracle` — no `ARM2-N1-carried`, no `ARM2-N3-carried`, no MCC oracles. The text oracles are F1-argmax only (`ladder.json` and `sweep_oracle.json` carry no `tile_mcc` key at all), where the image sweeps carry `f1_oracle` **and** `mcc_oracle` per rung. Any "text MCC-oracle" row would have to be manufactured.

**4.3 "Carried" does not mean the same thing at every rung of the text track.** `grid_board.json` labels `arm2-N1-carried` and `arm2-N3-carried` as `basis: "carried-analogue"` — the single committed N = 5 threshold (0.80) applied downward, not a threshold calibrated at that rung. The image track calibrated per rung: (0.88, k3) from the GS K = 3 leg, and (0.90, k5) from the *separately registered* GS K = 5 cells `g37-image-k5-verified-carried-p0.10-k5` / `g37-image-k5-verified-swap37-p0.90-k5` — `outputs/gemini37-image-55map-2026-09-13/post_run_report.md:84-91`; `results/gemini37-image-55map-2026-09-13/findings.md:78-82`.

**4.4 Text rungs are inherited, image rungs are run.** See § 2.2. The text N = 1 / N = 3 rungs could not have been produced without paying for the full N = 5 verifier leg, and 54 (N = 1) / 3 (N = 3) candidates failed the ≤ 10 m inheritance match — `results/gemini37-55map-2026-08-31/findings.md:92-97`, also `ladder.json` key `arms.arm2.{"1","3"}.unmatched`.

**4.5 Serving route differs within the image track.** Image proposer passes 1–3 ran flex realtime (cached share 0.808–0.813); passes 4–5 ran through the **Batch API** with explicit context caching (cached share 0.945), auditing at US$61.9 against US$81.9 — `outputs/gemini37-image-55map-2026-09-13/post_run_report.md:66,67,106,218-227`. All five text proposer passes ran flex with **zero** cached input on every meta (`reports/r7-gaps-deltas-2026-09-11.md:57-60`; confirmed by re-derivation: `cached = 0` on all eleven metas). So the K = 5 image marginal is on a cheaper route than its own K = 1 / K = 3 marginals.

**4.6 The image K = 5 rung is EXPLORATORY and untested.** Not in the card, campaign analysis row **UNSIGNED** — `outputs/gemini37-image-55map-2026-09-13/post_run_report.md:8-10,35,79-80`; `results/run-conditions.json` `_note` for `img-arm2-k5-carried-p0.90-k5-r2-gt`. Every K = 5 comparison in § 3 inherits that status. (Session 156 has since run a paired permutation of K = 5 vs K = 3 carried on the pure 3.7 stack: F1 +0.0071, *p* < 0.0001; tile-MCC +0.0012, *p* = 0.61 — inside the E89 drift band, so not claimable without a replicate.) The text N = 1 / N = 3 rungs are likewise **descriptive** ("screening protocol — no carried claims below N = 5", `results/gemini37-55map-2026-08-31/findings.md:98`).

**4.7 Tile-join re-stamp on the image cells.** The proposer tiling (24,561 tiles, 192 px stride) and the scoring frame (8,541 tiles, 336 px stride) share only 660 tile names, so `source_tile` is re-stamped by `stride55_score.assign_standard_tile`; without it the id join credits 192 of 6,250 detections — `results/run-facts.json:1046`. The flag names the same writer as produced `ARM2-N3-oracle` and `ARM2-N5-oracle`, so it is applied consistently across both tracks' r2 cells, but every tile-MCC in § 1.1 depends on it.

**4.8 Union sizes differ sharply for the same proposer model.** Text N = 5 union 12,715; image K = 5 union 9,173 (`findings.md:101-103` and `post_run_report.md:70`). The image track proposes a tighter candidate set, which is part of why its verifier legs are cheaper despite the more expensive proposer.

**4.9 What is genuinely controlled.** The two tracks differ in the proposer prompt **only**: identical `system_instruction_hash` `e169b7237b853eeaad990fc2e54fbd7214afb435d85c8e444a4a784432200e12` on both, same model `gemini-3.7-flash`, thinking `low`, T = 0.7, 24,561 tiles/pass; `include_example_images` false vs true with a **17-entry** library (8 Positive / 9 Negative; `library_hash` `7c9bbcec…`) — read from `configuration` in `outputs/gemini37-55map-2026-08-29/g384_ov192_55map_g37/run_1/detections-detect_brief-text-3.7-flash-2026-08-29.meta.json` and `outputs/gemini37-image-55map-2026-09-13/g384_ov192_55map_g37img/run_1/detections-detect_brief-text-image-3.7-flash-2026-09-13.meta.json`. The library directory `inputs/examples/neutral-naming/` holds **30** PNGs; the campaign used 17 of them, per that `library_manifest`. Verifiers are byte-identical in configuration across both tracks: `gemini-3.7-flash`, `verify_adversarial.md`, hash `2518d5298d9b84bac6810bb0d11e59ef534c46853f65cb25dc1454af3497e15d`, thinking `low`, T = 0.0.

**4.10 A surprise for the PI's calibration** (per `docs/agent-guidance.md` § Research Finding Calibration): the image track's advantage is overwhelmingly a **recall** effect at a much looser precision — image K = 5 carried R 0.9456 / P 0.9092 against text N = 5 carried R 0.8814 / P 0.8841. At K = 1 the image carried point sits at P 0.8007 / R 0.9570, i.e. the library buys +0.10 recall and pays −0.06 precision, and its F1 edge over the text N = 1 oracle is only +0.0109 while costing roughly 1.5–2 × more. The library's return is strongly K-dependent and is smallest exactly where the cost argument for one pass is strongest.

## Changelog

### 2026-09-20 — Original publication

Assembled in Session 156 from committed cells, sweeps, ladder files, post-run reports, and the r7 deltas report; every figure carries its source path. No new API spend.
