# Comparability inventory — Gemini 3.7-generation runs on the 55-map corpus

> **Last revised**: 2026-09-20 (original publication). See [§ Changelog](#changelog) for revision history.

Read-only survey commissioned by the PI on 2026-09-20 after
`reports/text-vs-image-tracks-2026-09-20.md` surfaced instrument
differences between the 3.7 text and image tracks. Assembled by an
Opus-class agent under Session 156 (Fable); the load-bearing claims
(§ 3.2's unmaterialised carried points, § 5 items 1, 6, 7) were
spot-checked against `results/55map-final-board-r2-2026-09-06/sweep_ARM2-N{1,3,5}.csv`,
`results/gemini37-image-55map-2026-09-13/findings.md:262-263`,
`results/run-conditions.json`, `results/run-facts.json`, and
`results/55map-final-board-r2-2026-09-06/final-board-50m.md` before filing.
Every cell names the file (and where practical the line or JSON key) it was
read from.

**Headline answer.** The text/image mismatch is real but it is **one of
five axes**, only two of which actually move a number, and the most
consequential one is **not** the reference. The reference/engine axis moves
F1@50 m by +0.006 to +0.007 on identical detections. What moves the 3.7
text-vs-image comparison by roughly **twice** the amount the morning report
allowed for is the **carried-point basis** — and the fix is free: the r2
board's own committed sweep CSVs already hold the missing text
carried-analogue points, unmaterialised and unpublished. Elsewhere the
problem is narrower than feared (the Gemini 3 image row is internally
consistent with the 3.7 image row on every scoring axis) but wider in one
respect: the Gemini 3 image row is **entirely unregistered** — no run-facts
entry, no run-conditions entry, no findings document, no post-run report,
no analysis row (known pending work: the beacon assigns its registration to
the PI).

## 0. What is in scope, and the naming

| Short name | Run id / results tree | Seat(s) using 3.7 Flash | Corpus |
|---|---|---|---|
| **T-canon** | `gemini37-55map-2026-08-29` → `results/gemini37-55map-2026-08-31/` (canonical chain) | arm 2 proposer + verifier; arm 1 proposer only | 55-map |
| **T-std** | same, `…/{arm1,arm2}/g384_ov192_55map_g37/standardised-ref/` | same | 55-map |
| **T-r2** | same, cells in `results/55map-final-board-r2-2026-09-06/cells/ARM{1,2}-N*/` | same | 55-map |
| **4th-canon / 4th-std / 4th-r2** | `results/gemini37-fourth-cell/`; registered under `stride-55map-2026-08-25` | 3.7 verifier over the Gemini-3 Run B K=10 pool | 55-map |
| **I37** | `gemini37-image-55map-2026-09-13` → `results/gemini37-image-55map-2026-09-13/` | arm 2 proposer + verifier; arm 1 proposer only | 55-map |
| **I3** | `gemini3-image-55map-2026-09-16` → `results/gemini3-image-55map-2026-09-16/` | arm 2 **verifier only** (proposer is `gemini-3-flash-preview`) | 55-map |
| **2x2** | `results/image-2x2-2026-09-19/tests_2x2_K{1,3,5}.json`; declaration `reports/image-2x2-tests-declaration-2026-09-19.md` | tests over I37 × I3 | 55-map |
| **GS37-text** | `gemini37-screen-2026-08-28` → `results/gemini37-screen-2026-08-28/` | source of T's carried points | 4-map GS |
| **GS37-image** | `gemini37-image-gs-2026-09-01` | source of I37's K=5 carried points | 4-map GS |
| **GS38** | `results/gemini38-screen-2026-09-04/armV/`; registered as a *condition* of `gemini37-screen-2026-08-28`, not as its own run id | 3.8 verifier vs the 3.7 arm | 4-map GS |

`docs/methodology/output-directory-standard.md` does not define reference or frame conventions; those live in `planning/reference-revision-2026-09-06.md` and in each campaign's `_flags` block in `results/run-facts.json`.

## 1. The axes of comparability

### 1.1 Reference, metric, frame

| Axis | T-canon | T-std | T-r2 | 4th-canon/std/r2 | I37 | I3 | GS37-text / GS37-image / GS38 |
|---|---|---|---|---|---|---|---|
| **Reference file** | built in-engine from `inputs/vectors/references/student-mounds-55maps-reviewed.geojson` (**4,746 feats, counted**) + reviewer promotions | `inputs/vectors/references/best-available-gt-55maps.geojson` (**5,010, counted**) | `…/best-available-gt-55maps-r2.geojson` (**5,018, counted**) | same three | r2 (5,018) | r2 (5,018) | `…/mounds-reference.geojson` (**569 in file**; 428 in scope at the 487-tile frame — derived from the anchor's P 0.9275 × n 400 = 371 TP, R 0.866822 ⇒ 428) |
| **Reference count is R-dependent?** | **Yes** — `…/arm2/…/primary/eval/summary.json` `results[]`: `n_ref_extended` 4,746 at R=20 and R=30, **5,160 at R=50** (`n_reviewer_promoted_at_R` 414) | No | No | Yes / No / No | No | No | No |
| **Engine** | `scripts/compute_corrected_f1_multi_buffer.py` ("Approach B — extended-GT-at-R Hungarian matching", docstring line 4); `evaluation.json` is an **adapter output** (`_metadata.adapted_by` = `scripts/register_gemini37_author.py`, "Deterministic transform … nothing recomputed") | `scripts/evaluate_detections.py` | `scripts/evaluate_detections.py` | same three | `scripts/evaluate_detections.py` | `scripts/evaluate_detections.py` | `scripts/evaluate_detections.py` |
| **F1 variant** | "corrected"-F1, micro (pooled TP/FP/FN — `scripts/stride55_ladder.py:287`), per-map Hungarian | plain micro-F1, per-map Hungarian (`scripts/lib_advanced_metrics.py:1595` `calculate_f1_internal`) | same | — | same | same | same |
| **Buffers on file** | **3** (20, 30, 50) — `summary.json` `results[]` | 14 | 14 | 3 / 14 / 14 | 14 | 14 | 14 |
| **Primary buffer** | 50 m | 50 m | 50 m | 50 m | 50 m | 50 m | **20 m** |
| **Scoring frame** | `inputs/vectors/bounds/384/55maps_evaluation_bounds.geojson`, **8,541 tiles (counted)** | same | same | same | same | same | `outputs/grid-2026-08-18/scoring/bounds/grid_common_bounds.geojson`, **487 tiles (counted)** |
| **`source_tile` re-stamped onto the frame?** | Yes — **5,003/5,003** book on the 8,541 frame (counted from `…/arm2/…/primary/verified_detections.geojson`) | same file | **5,003/5,003** | yes | **5,357/5,357**, plus `origin_source_tile` | **5,941/5,941**, plus `origin_source_tile` | n/a (proposer tiling *is* the frame) |
| **Re-stamp writer verified** | — | — | `stride55_score.assign_standard_tile`; idempotent **100.00 %** on `ARM2-N3-oracle`, `ARM2-N5-oracle`, `FOURTH-N1-oracle` (`reports/gemini37-image-55map-deltas-2026-09-13.md` § 10.7; gate 5 at `scripts/gemini37_image_55map_r2.py:1041-1077`) | same | same writer, gates 5/6 | same writer | — |
| **Tile confusion is R-dependent?** | **Yes** — `summary.json`: ARM2 (2425,4850,310,956) at R=20/30 but (2516,4798,219,1008) at R=50 | No | No | yes/no/no | No | No | No |
| **Bootstrap / CI** | tile-level, 10,000, seed 42, **percentile** (`f1_ci_method: "percentile"`) | tile-level, 10,000, seed 42, **BCa** | BCa, `_metadata.bootstrap` = `{n_iterations:10000, seed:42, resampling_unit:"tile_level", method:"BCa", library:"scipy.stats.bootstrap"}` | same | identical BCa block | identical BCa block | identical BCa block |
| **tile-MCC present** | **Yes at N=5** with percentile CI (ARM2 0.7073 [0.6926, 0.7219]; ARM1 0.6665 [0.6502, 0.6818]; FOURTH 0.7268 [0.7141, 0.7393] — `summary.json` `results[R=50].tile_classification.mcc_CI`). **Absent on the N=1/N=3 ladder rungs** (`ladder/ladder.json` has no `mcc` key; `ladder/ladder_sweep_50m.csv` header is `arm,N,prob_t,min_votes,n_detections,tp,fp,fn,precision,recall,corrected_f1`) | pinned to the 50 m row, no CI in the adapter | BCa CI | as left | BCa CI, all 18 cells | BCa CI, all 18 cells | BCa CI |

### 1.2 Verifier ladder, carried point, sweep space

| Axis | T (arm 1 / arm 2) | 4th cell | I37 | I3 |
|---|---|---|---|---|
| **Verifier legs actually run** | **One per arm**, over the K=5 union of **12,715** (`outputs/gemini37-55map-2026-08-29/verifier/g384_ov192_55map_g37/union_k5.geojson`, counted; `run.meta.json` `execution_stats.items_processed` 12,715 on both) | **One**, over 57,482 candidates (registered `n_candidates`) | **Six** — one per (arm × rung) over that rung's own union: **6,985 / 8,337 / 9,173** | **Six** — **22,785 / 36,389 / 45,786** |
| **Lower rungs** | **Inherited** — nearest K=5 candidate within **10 m** (`ladder/ladder.json` `inherit_tol_m: 10.0`); unmatched clusters **excluded from scoring, counted, included in cost** (`scripts/stride55_ladder.py:17`) | Inherited from the K=10 leg, same rule | **Own leg** | **Own leg** |
| **Rung unions / unmatched** | N=1 8,426 (**54** unmatched, 0.64 %); N=3 11,079 (**3**, 0.027 %); N=5 12,715 — `ladder.json` `arms.arm{1,2}.{"1","3"}` | N=1 25,586 (**663**, 2.59 %); N=3 36,757 (**285**, 0.78 %); N=5 43,909 (**119**, 0.27 %) — `results/gemini37-fourth-cell/55map/g384_ov192_55map/ladder.json` | n/a | n/a |
| **Inheritance displacement recorded** | **Not established** — `ladder.json` for the 3.7 arms carries no `match_dist_*` keys | Yes: p50/p95 = 2.447/7.724 m (N=1), 1.386/6.441 (N=3), 0.783/5.404 (N=5) | n/a | n/a |
| **Carried point, top rung** | arm 1 (0.10, k5); arm 2 (0.80, k5) — from **GS37-text**, `results/gemini37-screen-2026-08-28/swap37/analysis.json` `image_best` `{prob_t:0.8, min_votes:5, f1:0.92649}`, GS union 791 | (0.98, k10) from `results/gemini37-fourth-cell/gs-leg/analysis.json` | K=3: arm 1 (0.10, k3), arm 2 (0.88, k3) from its **own** GS K=3 leg (`results/gemini37-image-55map-2026-09-13/gs-calibration/arm{1,2}/analysis.json`, union 622). K=5: arm 1 (0.10, k5), arm 2 (**0.90**, k5) from **GS37-image** registered cells `g37-image-k5-verified-carried-p0.10-k5` / `…-swap37-p0.90-k5`, union 674 | K=3: arm 1 (0.15, k3), arm 2 (0.88, k3) from `results/gemini3-image-55map-2026-09-16/gs-calibration/k3/arm{1,2}/analysis.json`. K=5: arm 1 (0.15, k5), arm 2 (**0.95**, k5) from `…/gs-calibration/k5/arm{1,2}/analysis.json` |
| **Carried point, lower rungs** | **carried-analogue** — the N=5 threshold applied downward, labelled `basis: "carried-analogue"` for `arm1-N1-carried`, `arm1-N3-carried`, `arm2-N1-carried`, `arm2-N3-carried` in `results/gemini37-55map-2026-08-31/grid-board/grid_board.json` `cells[15,13,12,4]` | no carried cells below N=10 anywhere | K=1 is **also** a carried-analogue: the K=3 leg's probability "with `k` collapsing to 1 at the K = 1 rung" (`results/gemini37-image-55map-2026-09-13/findings.md:262-263`). **But `cells_manifest.json` labels it `basis: "carried"`, not `carried-analogue`** | K=1 likewise: no `gs-calibration/k1` directory exists (only `k3/` and `k5/`); `cells_manifest.json` also labels it `"carried"` |
| **Oracle basis** | **F1-argmax only.** `results/55map-final-board-r2-2026-09-06/sweeps.json` `families.ARM2-N5.argmax` keys are `[family, fn, fp, micro_f1_50, min_votes, n_detections, prob_t, tp]` — no MCC | same | **F1-oracle *and* MCC-oracle** — `sweeps.json` `rungs.*.{f1_oracle, mcc_oracle}` each carry `tile_mcc` | same as I37 |
| **Sweep points** | ARM1-N1 19 / N3 57 / N5 95; ARM2-N1 26 / N3 81 / N5 135 (`sweeps.json` `families.*.n_sweep_points`) | FOURTH-N1 27 / N3 81 / N5 135 / N10 270 | 20 / 63 / 100 (arm 1), 24 / 72 / 120 (arm 2) | 20 / 60 / 100 (arm 1), 26 / 84 / 145 (arm 2) |
| **Sweep scorer** | `scripts/final_board_sweeps.py` — "the light scorer", gated to the committed cells **within 0.003** (lines 21-25, 29-31, 42-44). Reproduces ARM2-N5 carried 0.8827, ARM2-N5 oracle 0.8871, ARM2-N3 oracle 0.8848, ARM2-N1 oracle 0.8610, ARM1-N5 carried 0.8551, FOURTH-N10 carried 0.8728 — all exact to 4 dp | same | `scripts/gemini37_image_55map_r2.py` (gate 2, F1 to 1e-4; gate 3, tile confusion exactly) | same script, `--campaign g3` |

### 1.3 Model, route, prompt

| Axis | T proposer | T arm1 vf | T arm2 vf | I37 proposer | I3 proposer | all image vf legs | 4th vf |
|---|---|---|---|---|---|---|---|
| **Model** | `gemini-3.7-flash` | `gemini-3-flash-preview` | `gemini-3.7-flash` | `gemini-3.7-flash` | `gemini-3-flash-preview` | arm 1 `gemini-3-flash-preview`, arm 2 `gemini-3.7-flash` | `gemini-3.7-flash` |
| **Thinking** | `low` | `minimal` | `low` | `low` | `minimal` (via `cli_overrides`) | `minimal` / `low` | `low` |
| **Temperature** | 0.7 | 0.0 | 0.0 | 0.7 | 0.7 | 0.0 | 0.0 |
| **Tiles/pass; passes** | 24,561; **5** | — | — | 24,561; **5** (1–3 + 4–5 added later) | 24,561; **5** | — | — |
| **`system_instruction_hash`** | `e169b7237b853eeaad990fc2e54fbd7214afb435d85c8e444a4a784432200e12` | `2518d5298d9b84ba…` | `2518d5298d9b84ba…` | **`e169b723…` identical to T** | **`e169b723…` identical** | **`2518d529…` identical on all 14 verifier metas read** | `2518d529…` |
| **Exemplar library** | `include_example_images: **false**`, `example_count: 17`, `library_hash: 8580ecb2…`, **no** `library_manifest` | `example_count: 0`, `library_hash: "no_examples"` | same | `include_example_images: **true**`, `library_hash: 7c9bbcec…`, `library_manifest` 17 entries = **8 Positive / 9 Negative** (4 canonical_positive, 4 hard_positive, 2 canonical_negative, 4 hard_negative, 3 null) | `library_manifest` **byte-equal to I37's** | `example_count: 0`, `"no_examples"` | `"no_examples"` |
| **Route / caching** | **All 5 passes flex realtime, `total_cached_tokens` = 0 on every one of the 11 metas** | flex (`cost_basis: "list"`, `discount: 1.0` — the known runner gotcha, `reports/r7-gaps-deltas-2026-09-11.md` § 2.3) | same | passes 1–3 **flex**, cached 0.808 / 0.810 / 0.811; passes **4–5 Batch API**, cached **0.945** | **all 5 flex**, cached 0.812 uniformly | **I37: all six legs flex**. **I3: arm 1 legs flex; all three arm-2 legs Batch API** — `batch_results.jsonl` / `batch_jobs.json` present in `verify_k{1,3,5}_arm2/` only | flex |
| **Verifier cost metas on disk** | complete | complete | complete | **K=1 and K=3 arm-2 main metas absent** (`run.meta.json` shows `items_processed` 13 and 1 — the cleanup passes; `.gitignore:140`). **K=5 arm 2 is intact** (`run.meta.pre-cleanup-1.json`, `-2.json` tracked) | complete (incl. `run.meta.pre-rerun-1.json` on k1/k5 arm 2) | — | **Lost** — `items_processed: 29`, the cleanup pass (`r7-gaps-deltas` § 2.5) |

**Verifier configuration is byte-identical across every campaign here.** All fourteen verifier `run.meta.json` files read record `version: "verify_adversarial-text"`, `instruction_file: "verify_adversarial.md"`, `system_instruction_hash: 2518d529…`, `example_count: 0`, `library_hash: "no_examples"`, T = 0.0. The verifier seat is a clean single-factor contrast (model + thinking as a package) in every campaign.

## 2. What is on r2, and what is not

`results/55map-final-board-r2-2026-09-06/cells/` holds **32** materialised+scored cells (+4 `committed_eval: true` cells living elsewhere = 36 in `cells_manifest.json`).

### 2.1 On r2 — same engine, same reference, same frame

| Cell | F1@50 [CI] | P | R | tile-MCC [CI] | n |
|---|---|---:|---:|---|---:|
| `ARM2-N5-oracle` | 0.8871 [0.8794, 0.8943] | 0.8956 | 0.8788 | 0.7147 [0.7004, 0.7288] | 4,924 |
| `ARM2-N3-oracle` | 0.8848 [0.8770, 0.8919] | 0.8780 | 0.8918 | 0.7163 [0.7017, 0.7307] | 5,097 |
| `ARM2-N5-carried` | 0.8827 [0.8749, 0.8899] | 0.8841 | 0.8814 | 0.7063 [0.6917, 0.7211] | 5,003 |
| `ARM2-N1-oracle` | 0.8610 [0.8534, 0.8684] | 0.8608 | 0.8613 | 0.7422 [0.7298, 0.7551] | 5,021 |
| `ARM1-N5-oracle` | 0.8727 [0.8644, 0.8803] | 0.9107 | 0.8378 | 0.7147 (board md) | 4,616 |
| `ARM1-N5-carried` | 0.8551 [0.8466, 0.8631] | 0.8378 | 0.8731 | 0.6655 | 5,229 |
| `ARM1-N3-oracle` | 0.8705 [0.8625, 0.8780] | 0.8929 | 0.8491 | 0.7179 [0.7040, 0.7318] | 4,772 |
| `ARM1-N1-oracle` | 0.8413 [0.8332, 0.8492] | 0.8251 | 0.8581 | 0.7246 [0.7109, 0.7384] | 5,219 |
| `FOURTH-N10-oracle` / `-carried` / `-N3-oracle` / `-N1-oracle` | 0.8813 / 0.8728 / 0.8747 / 0.8352 | — | — | 0.736 / 0.7264 / 0.7376 / 0.7471 | 4,495 / 4,246 / 4,626 / 5,337 |
| **`FOURTH-N5-oracle`** | **0.8758 [0.8679, 0.8832]** | 0.9335 | 0.8248 | **0.7326 [0.7200, 0.7453]** | 4,434 |
| all 18 `IMG-ARM{1,2}-K{1,3,5}-{carried,f1-oracle,mcc-oracle}` | see `results/gemini37-image-55map-2026-09-13/sweeps.json` | | | | |
| all 18 `G3IMG-ARM{1,2}-K{1,3,5}-{carried,f1-oracle,mcc-oracle}` | see `results/gemini3-image-55map-2026-09-16/sweeps.json` | | | | |

⚠ **`FOURTH-N5-oracle` is scored on r2 and registered** (`results/run-conditions.json` → `stride-55map-2026-08-25` condition `g384-ov192-55map-n5-verified37-oracle-p0.96-k5-r2-gt`) **but is absent from the published board**: `final_board_50m.json` has 35 cells, `final-board-50m.md` 35 rows and no `FOURTH-N5-oracle`; `cells_manifest.json` has 36.

### 2.2 Headline cells NOT on r2

| Missing on r2 | Exists where instead | Why it matters |
|---|---|---|
| `ARM2-N1-carried`, `ARM2-N3-carried` | canonical grid board only: `grid_board.json` `cells[12]` (0.80, k1) F1 0.8421 n 5,936; `cells[4]` (0.80, k3) F1 0.8745 n 5,187 — both `basis: "carried-analogue"` | **The two cells the image K=1 / K=3 carried cells should be compared against.** |
| `ARM1-N1-carried`, `ARM1-N3-carried` | `grid_board.json` `cells[15]` 0.7834 n 6,660; `cells[13]` 0.8418 n 5,482 | arm-1 (G3-verifier) leg of the same comparison |
| `FOURTH-N1-carried`, `-N3-carried`, `-N5-carried` | nowhere | fourth-cell ladder has carried only at N=10 |
| Any **MCC-oracle** on the text track or the fourth cell | nowhere; MCC was never swept (§ 1.2) | the image rows report `mcc_oracle` per rung; the text rows cannot |
| I37 / I3 cells on the **canonical** or **standardised** chain | nowhere — `sweeps.json` `reference: "r2"` for both | the image rows exist on one instrument only |
| T / 4th cells on the **image campaigns' MCC-sweep** footing | nowhere | asymmetric sweep spaces |

### 2.3 Which cross-campaign comparisons are clean *today*

**Clean** (same engine, reference, frame, and both cells exist):

- I37 vs I3, at K = 1, 3, 5, carried and both oracles — the 2x2, the cleanest block in the inventory.
- I37 or I3 vs any r2 board cell, including `ARM2-N{1,3,5}-oracle`, `ARM1-N{1,3,5}-oracle`, `FOURTH-N{1,3,10}-oracle`, `ARM2-N5-carried`, `ARM1-N5-carried`, `FOURTH-N10-carried`. (Exception inside the declared five-test family: `IM-k3`, whose own `source_tile` reproduces this writer at **83.65 %** — `deltas` § 10.7.)
- T vs 4th vs Gemini-3 incumbents on r2 — all 32 board cells share one engine.
- GS37-text vs GS37-image vs GS38 — all three `best-eval/evaluation.json` record the same reference, bounds, 14 buffers, BCa 10,000/42.

**Not clean:**

- **Image *carried* vs text *carried* at K/N = 1 and 3** — the text carried cells do not exist on r2. The morning report substituted the text **oracle**, which flatters the text track.
- **Any comparison quoting T-canon against an r2 cell** (e.g. arm 2's 0.8763 against the image 0.9199). Cross-instrument; offset measured in § 3.1.
- **Any MCC comparison between a text rung and an image rung at a *carried* point** — one side does not exist.
- **The 2x2's T3/T4 across the verifier seat in row B**: row B arm 2 is the only batch-served leg in the whole 2x2 (§ 1.3), so "verifier seat" and "serving route" are perfectly confounded in row B and not in row A. Recorded in the declaration § 5 caveat 2.
- **The 2x2's T1/T2 "proposer effect"**: row B's unions are **3.26× / 4.36× / 4.99×** row A's (22,785 vs 6,985; 36,389 vs 8,337; 45,786 vs 9,173). Rows are compared at their own GS-carried thresholds by design (declaration § 5 caveat 3), but the candidate-set sizes differ by a factor, not a margin.

## 3. Which axes actually bite

### 3.1 Reference + engine — bites at ~0.006 on F1@50, ~0.038 on F1@20, ~0.001 on tile-MCC

Same detection files, three instruments. Read from `summary.json` (canonical) and the two `evaluation.json` files per cell.

| Cell (identical detections) | F1@50 canonical | F1@50 std (r1) | F1@50 r2 | Δ canon→r2 | Δ r1→r2 | F1@20 canon → r2 | tile-MCC canon → r2 |
|---|---:|---:|---:|---:|---:|---|---|
| `ARM2-N5-carried` (n 5,003) | 0.876316 | 0.8825 | 0.8827 | **+0.0064** | +0.0002 | 0.746948 → 0.7846 (**+0.0377**) | 0.70729 → 0.7063 (−0.0010) |
| `ARM1-N5-carried` (n 5,229) | 0.849360 | 0.8550 | 0.8551 | **+0.0057** | +0.0001 | 0.722005 → 0.7592 (**+0.0372**) | 0.66647 → 0.6655 (−0.0010) |
| `FOURTH-N10-carried` (n 4,246) | 0.865618 | 0.8732 | 0.8728 | **+0.0072** | −0.0004 | 0.708407 → 0.7472 (**+0.0388**) | 0.72680 → 0.7264 (−0.0004) |

**Different by design and recorded** (`results/run-facts.json` `_flags` for `gemini37-55map-2026-08-29`: "TWO INSTRUMENTS…"; `findings.md` § "⚠ Reference instruments"). Essentially *all* the movement is the canonical→standardised step (engine + reference together); the r1→r2 reference revision alone moves F1@50 by ≤ 0.0004 and tile-MCC by ≤ 0.0010. Tile confusion is **identical** between canonical and standardised on all three cells, so the engine change does not touch tile-MCC.

**Verdict: bites for effects of order 0.006–0.013** (the campaign's own MDE80 is 0.013, `findings.md` § Headlines). It does **not** bite the +0.04 image-vs-text F1 gap. It bites hard at 20 m (+0.037), which matters for anything quoted at the preregistered localisation buffer.

### 3.2 Carried-point basis — bites hardest, and is the one to fix

`results/55map-final-board-r2-2026-09-06/sweep_ARM{1,2}-N{1,3}.csv` and `sweep_FOURTH-N{1,3,5}.csv` **already contain the carried-analogue points on r2**, swept but never materialised:

| Family | Point | n_det | tp | fp | fn | micro-F1@50 (r2) | Cell exists? |
|---|---|---:|---:|---:|---:|---:|---|
| `ARM2-N1` | (0.80, k1) | 5,936 | 4,633 | 1,303 | 385 | **0.8459** | **no** |
| `ARM2-N3` | (0.80, k3) | 5,187 | 4,491 | 696 | 527 | **0.8802** | **no** |
| `ARM1-N1` | (0.10, k1) | 6,660 | 4,589 | 2,071 | 429 | **0.7859** | **no** |
| `ARM1-N3` | (0.10, k3) | 5,482 | 4,446 | 1,036 | 572 | **0.8469** | **no** |
| `FOURTH-N1` | (0.98, k1) | 5,334 | 4,321 | 1,013 | 697 | **0.8348** | **no** |
| `FOURTH-N3` | (0.98, k3) | 4,623 | 4,215 | 408 | 803 | **0.8744** | **no** |
| `FOURTH-N5` | (0.98, k5) | 4,431 | 4,136 | 295 | 882 | **0.8754** | **no** |

(The same CSVs reproduce every committed cell exactly — ARM2-N5 (0.80,k5) 0.8827, (0.95,k5) 0.8871; ARM2-N3 (0.95,k3) 0.8848; ARM2-N1 (0.98,k1) 0.8610; ARM1-N5 (0.10,k5) 0.8551; FOURTH-N10 (0.98,k10) 0.8728 — so the sweep is on the same engine footing, within the board's documented 0.003 mechanism bound.)

Consequence — **image minus text, carried against carried, on r2**:

| Rung | arm 2 (3.7 verifier) | arm 1 (G3 verifier) | morning report's figure (image carried vs text **oracle**) |
|---|---:|---:|---:|
| K/N = 1 | 0.8719 − 0.8459 = **+0.0260** | 0.8477 − 0.7859 = **+0.0618** | +0.0109 |
| K/N = 3 | 0.9199 − 0.8802 = **+0.0397** | 0.9025 − 0.8469 = **+0.0556** | +0.0351 |
| K/N = 5 | 0.9270 − 0.8827 = **+0.0443** | 0.9130 − 0.8551 = **+0.0579** | +0.0443 |

The K = 1 row moves by a factor of 2.4. **This is the single biggest comparability consequence in the inventory.** The text track's carried-analogue tax at N=1 is large (canonical: 0.8563 oracle − 0.8421 analogue = 0.0142, `grid_board.json` `named_contrasts["arm2-N1: carried vs oracle"].delta_f1` −0.014196) while the image track's is small (r2: 0.8742 − 0.8719 = 0.0023). **Different by accident** — an artefact of which cells got materialised, not a design choice. The board itself sets the precedent: `A-N3-carried` and `B-N3-carried` exist with `basis: "carried (post-hoc)"` (`cells_manifest.json`; `final-board-50m.md` § "Post-hoc: the emergent N = 3 carried cells"). The same construction was **not** applied to ARM1/ARM2/FOURTH.

### 3.3 Inheritance vs own verifier leg — bites at about the E89 drift floor; unquantified for the text rungs

The closest measurement is `outputs/gemini37-image-55map-2026-09-13/verifier/g384_ov192_55map_g37img/probe-batch-vs-flex-2026-09-19/README.md` lines 12–14, comparing the same verifier on **the same mound's crop taken from a different rung's union** (matched within 5 m, median 0.57 m):

| comparison | n | identical p | flips at 0.90 | \|Δp\| > 0.5 |
|---|---:|---:|---:|---:|
| flex K5 vs flex K3 twin (same route, near-identical crop) | 171 | 61 % | **3.5 %** | 5 |
| batch K5 vs flex K5 (same crop, route differs) | 171 | 60 % | 5.3 % | 6 |

So substituting one rung's crop for another's changes ~39 % of probabilities and flips ~3.5 % of decisions at the operating point. Inheritance goes further: it **copies** the N=5 probability outright and **drops** unmatched clusters from scoring (`scripts/stride55_ladder.py:17`) — 54 of 8,426 at text N=1 (0.64 %), 3 of 11,079 at N=3, and 663 of 25,586 (2.59 %) at fourth-cell N=1. Dropped candidates can be neither TP nor FP, so the rung's precision is biased upward by an unmeasured amount. The board's r2 families are built the same way — `sweep_ARM2-N1.csv` at (0.0, k1) shows **8,372** = 8,426 − 54, and `scripts/final_board_sweeps.py:297` calls these rungs "zero-usd-inherited, never built".

**Different by design and recorded** (findings.md § "The N-ladder", lines 93–97), but the **magnitude is not established** for the text ladder: no `match_dist_*` was recorded for the 3.7 arms, and no head-to-head "inherited vs own leg" measurement exists on this corpus.

### 3.4 Serving route and caching — does not bite the numbers; does bite the cost

The batch-vs-flex probe found the batch route's drift **indistinguishable from same-route re-invocation drift** (5.3 % against a 3.5 % twin baseline). Recorded as a caveat, not a factor (declaration § 5 caveat 2; `findings.md` § 7). Cost-side: identical image payload, US$81.9 on flex (cached 0.808) against US$61.9 on batch (cached 0.945) — `outputs/gemini37-image-55map-2026-09-13/post_run_report.md:48-50,66-67`. **Different by design and recorded.**

### 3.5 Tile-join / scoring frame — does not bite between these campaigns

All four detection families book 100 % on the 8,541-tile frame (5,003/5,003 text, 5,003/5,003 ARM2-N5-carried r2 cell, 5,357/5,357 I37, 5,941/5,941 I3), and the re-stamp writer is idempotent at 100.00 % on the three committed 3.7 comparators. The single exception is `IM-k3` at 83.65 %, which affects only T5 of the 2x2 family and P-tests against `IM-k3`. **Different by design and recorded** (`results/run-facts.json:1046`; `deltas` § 10.7).

### 3.6 Bootstrap / CI method — does not bite

Percentile (canonical) vs BCa (r1 and r2), same detections, same n and seed. `ARM2-N5-carried` F1@50 CI widths: canonical **0.015116**, standardised **0.0151**, r2 **0.0150**. Difference ≤ 0.0002.

### 3.7 Oracle definition (F1-argmax vs MCC-argmax) — bites where it exists

Within I37 at K=3, the F1-oracle is (0.90, k3) at F1 0.9206 / MCC 0.7654 while the **MCC-oracle is (0.96, k2)** at F1 0.8882 / MCC 0.7656 — a 0.0324 F1 swing for a 0.0002 MCC gain, and not a unanimity point. In I3 the effect is extreme: `G3IMG-ARM2-K3.mcc_oracle` sits at **(0.98, k1)** — n 10,727, F1 **0.5772**, MCC 0.7706. The text track has no MCC oracle at all, so this axis is silently absent on one side.

## 4. What it would take to make each comparison clean

### 4.1 $0, on disk today (compute only; run on sapphire)

| Gap | Fix | Inputs that already exist | Result |
|---|---|---|---|
| **`ARM2-N1-carried`, `ARM2-N3-carried` on r2** | materialise at (0.80, k1) and (0.80, k3) from the board's own family frames, commit, score with `evaluate_detections.py` on the r2 recipe | `sweep_ARM2-N{1,3}.csv` rows already carry n/tp/fp/fn/F1; `build_g37_families()` rebuilds the frames | exact engine F1 + BCa CIs + **tile-MCC**. Expected F1 ≈ 0.8459 / 0.8802 |
| **`ARM1-N1-carried`, `ARM1-N3-carried`** | same | `sweep_ARM1-N{1,3}.csv` | ≈ 0.7859 / 0.8469 |
| **`FOURTH-N{1,3,5}-carried`** | same | `sweep_FOURTH-N{1,3,5}.csv` | ≈ 0.8348 / 0.8744 / 0.8754 |
| **`FOURTH-N5-oracle` missing from the board** | add the existing cell to `final_board_50m.json` / `final-board-50m.md`, or minute why it is excluded | cell + evaluation.json already committed | 36-cell board consistent with `cells_manifest.json` |
| **Text/fourth MCC-oracles** | extend `final_board_sweeps.py`'s sweep record to carry `tile_mcc` per point (the image script already does) and re-sweep the six 3.7 families | all probabilities and frames committed | MCC oracles symmetric with the image rows. 926 sweep points |
| **I37 / I3 on the canonical chain (secondary column)** | run `compute_corrected_f1_multi_buffer.py` over the 36 committed image `detections.geojson` | detections committed | the "secondary column" the deltas report § 10.3 offers |
| **Route-vs-arm confound in row B of the 2x2** | cannot be fixed on disk | — | see 4.2 |

### 4.2 Requires API spend — candidate counts only, no pricing

| Gap | Leg that would have to run | Candidates |
|---|---|---:|
| Text N=1 rung verified by its own leg (arm 2, `gemini-3.7-flash`) | re-extract crops from rasters (free) for the N=1 union, then verify | **8,426** |
| Text N=3 rung, own leg (arm 2) | same | **11,079** |
| Text N=1 / N=3, arm 1 (`gemini-3-flash-preview`) | same unions | **8,426** / **11,079** |
| Fourth-cell rungs, own legs (3.7 verifier) | N=1 / N=3 / N=5 unions | **25,586** / **36,757** / **43,909** |
| Row B arm 2 re-run on **flex** to de-confound route from verifier seat in the 2x2 | `verify_k3_arm2` (primary rung) | **36,389** (K=1 22,785; K=5 45,786 if all three rungs) |
| Row A arm 2 re-run on **batch** (the cheaper symmetric alternative) | `verify_k3_arm2` | **8,337** (K=1 6,985; K=5 9,173) |
| A replicate arm for any K=3→K=5 claim inside the E89 floor | a second arm-2 invocation over the K=5 union | **9,173** (row A) / **45,786** (row B) |
| Re-derive the lost I37 K=1 / K=3 arm-2 cost metas | not recoverable by re-running; would need a fresh leg | 6,985 / 8,337 |

Note on crops: the text campaign's verifier directory holds only `crops/candidate_manifest.json` (12,715 candidates); the PNGs are not in the working tree. Re-extraction from rasters is free (`post_run_report.md:71` prices "K = 5 union and crops" at US$0.00).

## 5. What the morning report (`reports/text-vs-image-tracks-2026-09-20.md`) got wrong or missed

**Wrong or overstated**

1. **§ 4.3, "The image track calibrated per rung."** Only partly. **K = 1 on both image rows is a carried-analogue too** — the K=3 leg's probability with `k` collapsed to 1 (`results/gemini37-image-55map-2026-09-13/findings.md:262-263`; no `gs-calibration/k1` directory exists in either image campaign). Only K=3 and K=5 have their own GS legs, and on row A K=3 and K=5 come from **two different GS campaigns** (union 622 vs 674).
2. **§ 1.2 header, "No tile-MCC and no CIs on this chain for these rungs."** True of the N=1/N=3 ladder rungs; **false of the N=5 rows in the same table**. `…/arm2/…/primary/eval/summary.json` carries `tile_classification.mcc` 0.7073 with `mcc_CI` [0.6926, 0.7219] at R=50, and the same for arm 1 (0.6665 [0.6502, 0.6818]) and the fourth cell (0.7268 [0.7141, 0.7393]).
3. **§ 3.1, the "not available" rows at K/N = 1 and 3.** They are available — § 3.2 above. The K = 1 delta the report gives (+0.0109, image carried vs text oracle) becomes **+0.0260** carried-vs-carried. § 4.10's calibration surprise ("the library's return is smallest exactly where the cost argument for one pass is strongest") **is the artefact, not the finding**: on a carried-vs-carried reading the K=1 edge is +0.0260 and the K-dependence is far weaker.
4. **§ 4.9, the exemplar library.** The text run's own `library_hash` is `8580ecb2…` with no `library_hash_basis` and no `library_manifest`; the image runs carry `7c9bbcec…` with `library_hash_basis: "example-bytes+path-label-category/1"`. The two hashes are on different bases and not comparable. The *substantive* claim survives and is stronger than stated: the `full_config_snapshot.examples` list is **identical entry-for-entry** (17 paths, labels, categories) across the text and both image pools — so `include_example_images` really is the only factor that moved.
5. **"Plain micro-F1" for the image chain.** Correct as to the engine, but the repository itself calls it "**corrected** micro-F1" in `reports/image-2x2-tests-declaration-2026-09-19.md:30` and `scripts/gemini37_image_55map_r2.py:50`. Neither invokes `compute_corrected_f1_multi_buffer.py`. Worth a terminology erratum.

**Missed**

6. **The Gemini 3 image row is entirely unregistered.** `gemini3-image-55map-2026-09-16` appears zero times in `results/run-conditions.json` and `results/run-facts.json`. No `findings.md`, no `post_run_report.md`, no planning card, no row in `results/analyses-manifest.json`. Row A's analysis row is present but **UNSIGNED** (`manually_verified_at: null`, 18 conditions). (Known pending: the beacon assigns the row's registration to the PI.)
7. **`FOURTH-N5-oracle` is scored, registered and off-board** (§ 2.1).
8. **Row B's unions are 3.3–5.0× row A's** — the declaration's caveat 4 mentions row B "over-generates" at K=1 only; the ratio actually *grows* with K.
9. **Row B arm 2 is the only Batch-served leg in the 2x2**, which makes route and verifier seat perfectly collinear inside row B, exactly where T3 and T4 live.
10. **Row B's MCC oracles abandon unanimity entirely**: `G3IMG-ARM1-K3.mcc_oracle` = (0.35, **k1**), `G3IMG-ARM2-K3.mcc_oracle` = (0.98, **k1**), `G3IMG-ARM1-K5` = (0.40, **k1**), `G3IMG-ARM2-K5` = (0.98, **k1**) — n 10,078 / 10,727 / 11,739 / 12,508, micro-F1 0.52–0.58. Any "MCC oracle" row read across the 2x2 compares a unanimity cell with a single-vote cell.
11. **The r2 board already contains the `carried (post-hoc)` precedent** (`A-N3-carried`, `B-N3-carried`) it did not apply to the 3.7 families — the mechanical cause of § 3.2.
12. **The registered `n_candidates` on every text r2 condition is 12,715**, including the N=1 and N=3 oracles whose rung unions are 8,426 and 11,079. Defensible as "the leg that paid for them", but mis-prices any per-candidate reading off the register.
13. **Verifier modality is mis-derived for the I37 campaign** in `results/run-conditions.json` (all six I37 `verifier_passes` say `"modality": "image"`; every other campaign's, including its own GS sibling with byte-identical metas, says `"text"`). No number moves; the register is internally inconsistent.
14. **Off-by-one in the canonical reference.** `inputs/vectors/references/canonical-gt-55maps-r50.geojson` holds **5,161** features against the 5,160 the engine books at R=50. Cause **not established**.
15. **The canonical chain's reference and tile-truth are buffer-dependent** (`n_ref_extended` 4,746 at R=20/30 but 5,160 at R=50). The r2 chain's are fixed across all 14 buffers. This is why the reference axis bites five times harder at 20 m than at 50 m.

## 6. Suggested order of work (no spend)

1. Materialise and score the **seven missing carried-analogue cells** on r2 (§ 4.1 rows 1–3). This alone repairs the image-vs-text comparison at K/N = 1 and 3 and gives them CIs and tile-MCC.
2. Add `tile_mcc` to `final_board_sweeps.py`'s sweep record and re-sweep the six 3.7 families, so the text track has MCC oracles (926 points).
3. Resolve `FOURTH-N5-oracle`'s board status.
4. Register the Gemini 3 image row (run-facts, run-conditions, analysis row) and write its findings/post-run report before the 2x2 is signed.
5. Erratum for "corrected micro-F1" at `reports/image-2x2-tests-declaration-2026-09-19.md:30` and `scripts/gemini37_image_55map_r2.py:50`, and for the verifier modality in `results/run-conditions.json`.
6. Only then decide whether the route de-confound in row B (36,389 candidates at the primary rung) is worth buying.

## Changelog

### 2026-09-20 — Original publication

Read-only survey; no API spend, nothing under `results/` or `outputs/` changed. Filed by Session 156 after spot-checking § 3.2, § 5.1, § 5.6, and § 5.7 against their sources.
