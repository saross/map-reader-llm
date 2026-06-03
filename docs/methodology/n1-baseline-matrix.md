# The N=1 baseline matrix — what it is, how it is scored, and how it enters the manifest

> **Last revised**: 2026-06-03 (Session 98 — **E57 genuine-Pro replace**: the four
> anti-diagonal "Pro" cells were found to have been dispatched as **Flash** and were
> replaced by a genuine-Pro re-run (`n1-pro-rerun-384`). Re-tiered → **7 tiers**,
> `tie_set` collapses to a **single leader** `pro-text-high-t-0-0` (genuine Pro,
> F1 0.804). See [§ Changelog](#changelog) for revision history.

**Purpose**: a single legible map of the **N=1 baseline matrix** — the
cross-architecture single-pass leaderboard at 384 px on the 4-map gold-standard
corpus — so a reader (or future-self) understands what each of its 18 cells is,
how the cells are scored, how they relate to the per-pass single-pass conditions,
and exactly how they are modelled in the experimental manifest.

---

## 1. What the matrix is

The N=1 baseline matrix is the **expected single-pass performance** of each
proposer configuration, with no aggregation and no verifier. It spans the
cross-architecture grid:

- **model** — Gemini 3 Flash, Gemini 3 Pro
- **modality** — text (OCR-style structured prompt), image (vision crop)
- **thinking level** — minimal, medium, high
- **temperature** — 0.0, 0.3, 0.7

Not every grid point was run; the matrix is the **18 cells that exist on disk**.
It is the headline "how good is a single pass?" baseline against which the
consensus (vote-threshold) and proposer-verifier architectures are compared.

The 18 cells are **not** a single experimental run. They were collected across
four real source runs and are deliberately modelled as conditions **on those
runs** (not as a synthetic pseudo-run), consistent with the leaderboard / WBF /
GAP-6 precedent:

| source run | cells | why the cells live here |
|---|:---:|---|
| `pv-diag-384` | 10 | the proposer-verifier diagnostic run carries the bulk of the matrix as its single-pass baselines |
| `n1-outstanding-384` | 3 | the "outstanding cells" run — its Flash T=0.3 cells + the 487-tile Flash image baseline |
| `n1-pro-rerun-384` | 4 | the **genuine-Pro re-run** of the four anti-diagonal corners (E57): text/image × {HIGH-T=0.0, MEDIUM-T=0.7} |
| `retest-h11-single-pass-384-t0` | 1 | the Flash text MINIMAL T=0.0 repeated-single-pass run |

The four corners `n1-outstanding-384` was *meant* to supply as Pro (text/image ×
{HIGH-T=0.0, MEDIUM-T=0.7}) were dispatched as **Flash** (errata E57) and are now
**off-board**: they are preserved on `n1-outstanding-384` with a corrected Flash
model-of-record — genuine Flash data at otherwise-untested thinking/temperature
corners — while the leaderboard's four Pro anti-diagonal cells now come from the
genuine-Pro re-run `n1-pro-rerun-384`.

---

## 2. How a cell is scored (the eval protocol)

Each cell is scored by `scripts/evaluate_detections.py` from the batch config
`configs/n1-eval-384px-14buf-mcc.yaml`, against the 487-tile full evaluation
bounds (`inputs/vectors/bounds/384/full_evaluation_bounds.geojson`) and the
curator ground truth (`inputs/vectors/references/mounds-reference.geojson`).

Two things about the protocol are easy to misread, so they are stated plainly:

### 2.1 The point estimate is a MEAN over replicate single passes

A cell's `detections_dir` globs **all** of that configuration's replicate single
passes (1, 3, 5, 10, or 30 of them — see the table in §4). The scorer evaluates
**each pass individually** and reports the **mean** across passes, with a
tile-level bootstrap confidence interval. So a cell's F1 (per buffer) and its MCC
are the **expected performance of one pass** — *not* a union, vote, or consensus
over passes. This is why the architecture is `single-pass` even where the cell
averages 30 replicates: the replicate structure is used to *estimate* single-pass
performance precisely, not to *combine* passes into one detection set.

The single-pass **mean ± σ** and the pass-to-pass spread are, in the four-entity
model, properly an *analysis* over the per-pass conditions (Decision 2,
Session 94). The matrix cell records the headline point estimate so that the
(forthcoming) leaderboard analysis has a first-class, metric-owning condition to
point at — an analysis compares conditions, so the cells must be conditions.

### 2.2 F1 is per-buffer; MCC is buffer-agnostic (one value per cell)

There are two different scoring questions, and they behave differently with
respect to the spatial **buffer** (the point-matching tolerance, in metres):

- **Detection metrics (F1, precision, recall)** match each predicted *point* to a
  reference mound within the buffer radius. They are reported **per buffer**
  because the score depends on the tolerance. The 14 uniform buffers are
  `5 10 15 20 25 30 35 40 45 50 75 100 125 150` m. The **headline buffer is the
  preregistered 20 m**; 50 m is the lenient comparison; 75–150 m are the
  saturation tail (detections become noisy past ~100 m, so the tail is reported
  for completeness, never as a headline).
- **Tile-level classification (MCC + confusion tp/tn/fp/fn)** has **no buffer at
  all** (`scripts/lib_advanced_metrics.py::calculate_tile_classification`;
  preregistration §4.2). It classifies each *tile* by presence/absence — a tile
  is a true positive if it contains a reference mound **and** the model emitted
  any detection in that tile (by `source_tile`, i.e. the crop the detection came
  from — no distance test). So there is exactly **one MCC per cell**, identical at
  every buffer. The 30 m label on the old MCC eval was irrelevant to the MCC
  value.

**Consequence — the two metrics are complementary**: MCC measures tile-level
discrimination ("did we flag the right tiles?"); F1@20 m measures localisation
accuracy at the preregistered tolerance ("did we pin the mound to within 20 m?").
A detection that lands in the right tile but far from the mound helps MCC but not
F1@20 m. This is exactly the MCC-alongside-F1 pairing the project standardised on.

**Nothing downstream averages across buffers.** Each buffer is reported in its own
`per_buffer` slot; the only averaging is across replicate passes *within* a
buffer.

For the multi-pass cells, the scorer reports the **mean** per-pass MCC; the
confusion block (`tp/tn/fp/fn`) is taken from the first pass (a known scorer
behaviour — it is one tile-set's worth, summing to 487; the MCC is the
replicate mean, so MCC and the confusion block need not be exactly
inter-derivable for the multi-pass cells).

### 2.3 Why this re-score exists (the 14-buffer + MCC standard)

The original baseline matrix (`results/paper-eval/n1/384px-all-buffers/`, archived)
was scored at only **4 buffers (20/30/40/50 m) with MCC switched off**. That
predates two project standards adopted 2026-05-31:

1. the **14 uniform buffers** for all runs (`scripts/rescore_conditions.py`
   `BUFFERS_STANDARD`), and
2. the **MCC-always** preference.

The conditions schema also *requires* non-null `tp/tn/fp/fn`, so a no-MCC eval
cannot back a valid condition row. The re-score to
`results/paper-eval/n1/384px-14buf-mcc/` brings the matrix onto the same eval
footing as every other condition and supplies the MCC block. The re-score is
**evaluation-only** (no detection API; CPU on zbook); the detection geometries are
unchanged.

---

## 3. How the cells are modelled in the manifest

Each cell is one **single-pass condition** in `results/run-conditions.json`:

- `architecture: single-pass`, `aggregation: none`, `n_passes: 1`
- `vote_threshold: null`, `prob_threshold: null`, `verifier_config: null`
- `eval_path` → the cell's `results/paper-eval/n1/384px-14buf-mcc/<slug>/evaluation.json`
- `label: baseline-<eval-slug>` (e.g. `baseline-pro-text-high-t-0-7`); the
  `baseline-` prefix distinguishes the matrix cell from the granular per-pass
  conditions.

### 3.1 Headline aggregate vs per-pass granular conditions

`n1-outstanding-384` and `retest-h11-single-pass-384-t0` **already** carry
per-pass single-pass conditions (`<pool>-single-pass-run_N`, scored at the
14-buffer rescore standard, `results/rescore-2026-05-31/`). So those two runs now
hold **two** single-pass representations of the same passes, and this is
**intentional, not double-counting**:

- the **per-pass** conditions answer "what is the pass-to-pass reproducibility
  spread?" (each scores one geojson, `n=1`);
- the **baseline-matrix** condition answers "what is the headline expected
  single-pass performance?" (the replicate mean, the leaderboard cell).

They live under distinct labels and distinct eval protocols.

### 3.2 `pv-diag-384` is aggregate-only for now

`pv-diag-384` had no conditions before this work; its 10 baseline cells are its
first. Its `proposer_pools` and `verifier_passes` are left **empty** on purpose:
the full pass + consensus + verified decomposition of `pv-diag-384` is **Batch E**
(GAP-7, the many-verifier-pass run). The 10 baseline conditions therefore
reference their pools by **relative pool-dir path** (e.g.
`pro-high-text-n5/text-t0.7`) rather than a declared `proposer_pool`; Batch E will
declare those pools and add the per-pass / consensus / verified conditions. The
audit verifier (`scripts/verify_run_conditions.py`) will WARN about the
undeclared pools — that is the expected "not yet fully decomposed" signal, not an
error.

### 3.3 Expected audit-verifier WARNs

`scripts/verify_run_conditions.py` (the audit instrument) reports these runs as
**partial** (WARNs, no ERRORs) — all expected for a partially-decomposed state:

- `geojson-missing` (one per baseline cell): the cell's `detections` points at the
  pass **directory** it aggregates, not a single geojson, so the per-feature check is
  skipped; the metric comes from `eval_path`.
- `pool-unresolved` / `pool-dir-not-found`: pv-diag-384's pools are not declared
  (Batch E), and n1/retest pools sit at `<pool>/` rather than the verifier's assumed
  `proposer/<pool>/` (the same layout gap that defers their pass emission to the
  pass-publishing step).
- `unclaimed-eval`: evals not yet authored as conditions (pv-diag-384's
  consensus/verified/sweep evals → Batch E; the superseded `384px-all-buffers` and
  `mcc/384px` siblings).

ERRORs (e.g. non-portable absolute eval paths) are NOT expected and were resolved
before landing — the 14-buffer evals record repo-relative provenance.

### 3.4 Model-of-record (errata E57 — billing reconciliation, RESOLVED)

The E57 billing reconciliation (2026-06-03) settled which "Pro" cells actually ran
Pro. The authoritative field for *what dispatched* is `per_item_metadata.model_version`
/ `pricing_used.model` — **never** `config.model` (a Flash template default on *both*
groups) and never the directory slug or study YAML (which record *intent*). The verdict
splits the eight "Pro" cells:

- **`pv-diag-384`'s four Pro cells are genuinely Pro** — `pricing_used.model =
  gemini-3.1-pro-preview` at $2/$12 rates; the per-study `--model` override took there.
- **`n1-outstanding-384`'s four anti-diagonal "Pro" cells were dispatched as Flash** —
  `model_version = gemini-3-flash-preview` on every response (the runner never threaded
  the `--model` override, so the base-config Flash ran). Their `model_of_record` in
  `run-conditions.json` was therefore **corrected from `gemini-3.1-pro` to
  `gemini-3-flash-preview`** (document-don't-rename: dirs and slugs unchanged). These
  four are now **off-board** (genuine Flash data, preserved).
- **`n1-pro-rerun-384` is the genuine-Pro re-dispatch** of those four corners —
  `model_version = gemini-3.1-pro-preview` verified on all 8 passes; its pools carry
  `model_of_record = gemini-3.1-pro-preview`. These are the four Pro anti-diagonal
  cells the board now uses.

This affects **passes**, not conditions (a condition carries no model field). The
passes-manifest now shows the 8 `n1-outstanding-384` pro-* passes as
`gemini-3-flash-preview` and the 8 `n1-pro-rerun-384` passes as `gemini-3.1-pro-preview`.
See errata E57 § "Update (2026-06-03)".

---

## 4. The 18 cells — provenance map

`slug` is the per-pool eval subdirectory (identical under both
`384px-all-buffers/` and `384px-14buf-mcc/`). `replicates` is the number of single
passes averaged. `proposer_pool` is the manifest identifier (a declared pool for
n1 / retest; a relative pool-dir path for pv-diag-384).

<!-- AUTHORING NOTE: results columns (F1@20m, F1@50m, MCC) filled from the fresh
     14-buffer + MCC evals after the re-score completes; see § Changelog. -->

| source run | cell (slug) | replicates | proposer_pool | condition label |
|---|---|:---:|---|---|
| pv-diag-384 | flash-image-high-t-0-7 | 10 | flash-high-image-n5/image-t0.7 | baseline-flash-image-high-t-0-7 |
| pv-diag-384 | flash-image-minimal-t-0-0 | 1 | image-baseline/image-t0.0 | baseline-flash-image-minimal-t-0-0 |
| pv-diag-384 | flash-image-minimal-t-0-7 | 10 | image-n5/image-t0.7 | baseline-flash-image-minimal-t-0-7 |
| pv-diag-384 | flash-text-high-t-0-7 | 30 | flash-high-text-n5/text-t0.7 | baseline-flash-text-high-t-0-7 |
| pv-diag-384 | flash-text-minimal-t-0-0-pv-baseline | 1 | text-baseline/text-t0.0 | baseline-flash-text-minimal-t-0-0-pv-baseline |
| pv-diag-384 | flash-text-minimal-t-0-7 | 30 | flash-minimal-text-n30-t07/text-t0.7 | baseline-flash-text-minimal-t-0-7 |
| pv-diag-384 | pro-image-high-t-0-7 | 5 | pro-high-image-n5/image-t0.7 | baseline-pro-image-high-t-0-7 |
| pv-diag-384 | pro-image-medium-t-0-0 | 1 | pro-medium-image-baseline/image-t0.0 | baseline-pro-image-medium-t-0-0 |
| pv-diag-384 | pro-text-high-t-0-7 | 10 | pro-high-text-n5/text-t0.7 | baseline-pro-text-high-t-0-7 |
| pv-diag-384 | pro-text-medium-t-0-0 | 1 | pro-medium-text-baseline/text-t0.0 | baseline-pro-text-medium-t-0-0 |
| n1-outstanding-384 | flash-image-minimal-t-0-0-487-tiles | 3 | image-t0 | baseline-flash-image-minimal-t-0-0-487-tiles |
| n1-outstanding-384 | flash-image-minimal-t-0-3 | 3 | image-t03 | baseline-flash-image-minimal-t-0-3 |
| n1-outstanding-384 | flash-text-minimal-t-0-3 | 3 | brief-text-t03 | baseline-flash-text-minimal-t-0-3 |
| n1-pro-rerun-384 | pro-rerun/pro-image-high-t-0-0 | 3 | pro-image-high-t0 | baseline-pro-image-high-t-0-0 |
| n1-pro-rerun-384 | pro-rerun/pro-image-medium-t-0-7 | 1 | pro-image-medium-t07 | baseline-pro-image-medium-t-0-7 |
| n1-pro-rerun-384 | pro-rerun/pro-text-high-t-0-0 | 3 | pro-text-high-t0 | baseline-pro-text-high-t-0-0 |
| n1-pro-rerun-384 | pro-rerun/pro-text-medium-t-0-7 | 1 | pro-text-medium-t07 | baseline-pro-text-medium-t-0-7 |
| retest-h11-single-pass-384-t0 | flash-text-minimal-t-0-0 | 10 | brief-text-t0 | baseline-flash-text-minimal-t-0-0 |

The four `n1-pro-rerun-384` cells' evals live under the `pro-rerun/` subdirectory of
`384px-14buf-mcc/` (the genuine-Pro re-run is realtime-style, glob
`*/detections-*.geojson`); the off-board Flash dispatches of the same corners remain
scored at `384px-14buf-mcc/{pro-image-high-t-0-0,…}` on `n1-outstanding-384`.

Run → pool provenance was verified from each eval's
`_metadata.input_files.detections` (the authoritative ground truth for run
identity per E57).

---

## 5. Results (14-buffer + MCC re-score)

Quoted directly from `results/paper-eval/n1/384px-14buf-mcc/<slug>/evaluation.json`
(bootstrap 10 000, seed 42, BCa, tile-level resampling). F1 is the per-pass mean at
the headline 20 m and lenient 50 m buffers; MCC is the buffer-agnostic per-pass-mean
tile-classification value; the confusion block is one tile-set's worth (sums to 487).

| source run | cell (slug) | F1@20 m | F1@50 m | MCC | confusion (tp/tn/fp/fn) |
|---|---|:---:|:---:|:---:|:---:|
| pv-diag-384 | flash-image-high-t-0-7 | 0.499 | 0.622 | +0.602 | 225/153/105/4 |
| pv-diag-384 | flash-image-minimal-t-0-0 | 0.600 | 0.681 | +0.312 | 228/51/207/1 |
| pv-diag-384 | flash-image-minimal-t-0-7 | 0.553 | 0.666 | +0.330 | 228/54/204/1 |
| pv-diag-384 | flash-text-high-t-0-7 | 0.387 | 0.416 | +0.331 | 227/62/196/2 |
| pv-diag-384 | flash-text-minimal-t-0-0-pv-baseline | 0.520 | 0.536 | -0.003 | 228/1/257/1 |
| pv-diag-384 | flash-text-minimal-t-0-7 | 0.488 | 0.513 | +0.078 | 229/3/255/0 |
| pv-diag-384 | pro-image-high-t-0-7 | 0.591 | 0.809 | +0.852 | 221/228/30/8 |
| pv-diag-384 | pro-image-medium-t-0-0 | 0.606 | 0.778 | +0.734 | 202/220/38/27 |
| pv-diag-384 | pro-text-high-t-0-7 | 0.745 | 0.799 | +0.747 | 175/247/11/54 |
| pv-diag-384 | pro-text-medium-t-0-0 | 0.763 | 0.802 | +0.751 | 179/246/12/50 |
| n1-outstanding-384 | flash-image-minimal-t-0-0-487-tiles | 0.598 | 0.680 | +0.314 | 228/51/207/1 |
| n1-outstanding-384 | flash-image-minimal-t-0-3 | 0.593 | 0.677 | +0.305 | 227/52/206/2 |
| n1-outstanding-384 | flash-text-minimal-t-0-3 | 0.499 | 0.523 | +0.039 | 229/1/257/0 |
| n1-pro-rerun-384 | pro-image-high-t-0-0 | 0.666 | 0.834 | +0.868 | 218/237/21/11 |
| n1-pro-rerun-384 | pro-image-medium-t-0-7 | 0.593 | 0.836 | +0.913 | 216/250/8/13 |
| n1-pro-rerun-384 | pro-text-high-t-0-0 | 0.804 | 0.828 | +0.790 | 188/247/11/41 |
| n1-pro-rerun-384 | pro-text-medium-t-0-7 | 0.764 | 0.826 | +0.787 | 181/252/6/48 |
| retest-h11-single-pass-384-t0 | flash-text-minimal-t-0-0 | 0.503 | 0.520 | +0.046 | 229/1/257/0 |

The four `n1-pro-rerun-384` rows are the **genuine-Pro** anti-diagonal (evals under
`384px-14buf-mcc/pro-rerun/`). The off-board **Flash** dispatches of the same configs
(E57) scored far lower — F1@20 m 0.528 / 0.452 / 0.494 / 0.416 — so genuine Pro adds
**+0.14 to +0.35 F1** at these corners (full before→after table in errata E57).

Reading the matrix (single-pass, no aggregation, no verifier):

- **F1@20 m leader** is genuine Pro text with HIGH thinking at T=0.0:
  `pro-text-high-t-0-0` (0.804), ahead of a cluster of other Pro-text passes
  (`pro-text-medium-t-0-7` 0.764, `pro-text-medium-t-0-0` 0.763, `pro-text-high-t-0-7`
  0.745). **MCC leader** is now genuine Pro **image**: `pro-image-medium-t-0-7`
  (+0.913, confusion 216/250/8/13), with `pro-image-high-t-0-0` (+0.868) second —
  both above the former MCC leader `pro-image-high-t-0-7` (+0.852).
- **Flash text MINIMAL massively over-detects**: it flags almost every tile
  (`fp`≈257, `tn`≈1), so its MCC collapses to ≈0 (even slightly negative for the
  T=0.0 PV baseline). F1 stays moderate (~0.50) because recall is near-total, but the
  tile-level discrimination is essentially nil — exactly the case MCC is meant to
  expose and F1 alone would hide.
- **Cross-run consistency check**: the same Flash Image MINIMAL T=0.0 configuration
  appears in both pv-diag-384 (1 pass, MCC +0.312) and n1-outstanding-384 (3 passes,
  MCC +0.314, near-identical confusion) — reassuringly stable across the two source
  runs.
- These are **single-pass** numbers; the consensus (vote-threshold) and
  proposer-verifier architectures are scored separately and compared against this
  baseline. The statistical ranking and tiering of these 18 cells — and the
  `tie_set` — are the leaderboard **finding** in § 6 (analysis
  `n1-baseline-matrix-384`).

---

## 6. The leaderboard finding — statistical tiering

The 18 cells are ranked by the headline **F1@20 m** and grouped into
statistically distinguishable **tiers** by the project's canonical leaderboard
method, run here as `scripts/n1_baseline_leaderboard_tiering.py` (results:
`results/paper-eval/n1/384px-14buf-mcc/tiering/tiering_20m.{json,md}`; computed
on sapphire, $0 API):

- **Round-robin paired permutation** — all C(18, 2) = 153 pairs, a tile-swap
  permutation on the **pass-averaged per-tile** TP/FP/FN (the expected
  single-pass micro-F1 — the same statistic the bootstrap CIs use), 10 000
  permutations, seed 42, two-sided. This is the canonical
  `pairwise_permutation_test.run_permutation_test` algorithm (micro-average F1,
  erratum E45), extended from integer single-pass counts to **float replicate
  means** (see the script header). Cross-check: the permutation's observed
  micro-F1-of-the-mean matches each cell's mean-of-per-pass board F1 (§ 5) to
  within **≤0.0003** at every replicate count (1–30 passes), so the test ranks
  exactly what the leaderboard reports.
- **Benjamini–Hochberg FDR** at q = 0.05 over the 153 raw p-values, then
  **greedy clique tiering** (identical to
  `build_tiered_leaderboard.apply_fdr_and_tier`): cells are processed in
  F1-descending order, each joining the current tier iff indistinguishable from
  **all** current members. 120/153 pairs significant → **7 tiers**.

**Why a permutation and not CI-overlap.** The most precise detectors at the top of
the board (the genuine Pro-text leaders) are flagged `ci_unreliable`
(`sparse_cross_grid`, § 2.2): being high-precision they leave >50 % of tiles empty,
so their bootstrap F1 CIs are unreliable — exactly at the decisive top comparison.
The tile-swap permutation sidesteps this: empty tiles are inert under label-swapping,
so the test does not depend on the flagged CIs. It gives the top-of-board separation
on firmer ground than CI-overlap would.

### The tiers (F1@20 m)

| tier | members (F1@20 m) |
|---:|---|
| **1 — `tie_set`** | `pro-text-high-t-0-0` (0.804) — genuine Pro, **sole leader** |
| 2 | `pro-text-medium-t-0-7` (0.764), `pro-text-medium-t-0-0` (0.763), `pro-text-high-t-0-7` (0.745) |
| 3 | `pro-image-high-t-0-0` (0.666) |
| 4 | `pro-image-medium-t-0-0` (0.606), `flash-image-minimal-t-0-0` (0.600), `flash-image-minimal-t-0-0-487-tiles` (0.598), `flash-image-minimal-t-0-3` (0.593), `pro-image-medium-t-0-7` (0.593), `pro-image-high-t-0-7` (0.591) |
| 5 | `flash-image-minimal-t-0-7` (0.553), `flash-text-minimal-t-0-0-pv-baseline` (0.520) |
| 6 | `flash-text-minimal-t-0-0` (0.503), `flash-text-minimal-t-0-3` (0.499), `flash-image-high-t-0-7` (0.499), `flash-text-minimal-t-0-7` (0.488) |
| 7 | `flash-text-high-t-0-7` (0.387) |

(`pro-text-high-t-0-0`, `pro-text-medium-t-0-7`, `pro-image-high-t-0-0`,
`pro-image-medium-t-0-7` are the genuine-Pro re-run cells; see § 3.4 / E57.)

**The finding.** **Tier 1 — the `tie_set` — is the single cell
`pro-text-high-t-0-0`** (genuine Gemini 3 Pro text, HIGH thinking, T=0.0; F1 0.804),
statistically clear of every other configuration. It is significantly separated from
the Tier-2 trio of other Pro-text passes (`pro-text-medium-t-0-7` 0.764,
`pro-text-medium-t-0-0` 0.763, `pro-text-high-t-0-7` 0.745), which are mutually
indistinguishable. The top four cells are all Pro text and the top five all genuine
Pro. (This supersedes the pre-E57 board, whose Tier 1 was a two-member tie at
0.763/0.745 — computed before the four anti-diagonal cells were found to be Flash and
replaced by the genuine-Pro re-run.) Two cross-cutting reads:

- **F1 leader ≠ MCC leader (the winner is metric-dependent).** The Tier-1 cell
  leads *localisation* (F1@20 m) but is not the *tile-discrimination* leader: that
  is genuine Pro **image** — `pro-image-medium-t-0-7` (MCC +0.913, but only 10th on
  F1 at 0.593) and `pro-image-high-t-0-0` (MCC +0.868) — which sit in Tiers 4 / 3 on
  F1. Text wins precise localisation; image wins flagging the right tiles — the
  MCC-alongside-F1 split (§ 2.2) made concrete, and *sharper* than the pre-E57 board
  (the genuine Pro-image cells reach MCC +0.91, above the former leader's +0.852).
- **H6 (Pro vs Flash) holds at the top and uniformly.** The top five cells are all
  genuine Pro; every Pro-text cell beats the best Flash cell (`flash-image-minimal-t-0-0`,
  F1 0.600), and the genuine Pro-image cells match Flash on F1 while dominating MCC.
  The pre-E57 board's apparent "Flash image-MINIMAL beats weak Pro" was an **artefact
  of the Flash-misdispatched anti-diagonal** (E57): those four cells were Flash, not
  Pro, and genuine Pro at the same corners scores 0.59–0.80. **H7's preregistered
  T=0.0 optimum now appears at the apex** — the sole Tier-1 leader is T=0.0 — though
  Tier 2 mixes T=0.0 and T=0.7 indistinguishably.

**Manifest linkage and preregistration.** The finding is recorded in the
analyses manifest row `n1-baseline-matrix-384` (`tie_set`, `outcome`,
`predicted_outcome`). It is framed **`exploratory`** (`hypothesis_refs`
H1 / H6 / H7): the within-board contrasts recapitulate preregistered directions
as convergent evidence, but the 18-cell ranked board was not itself in the
preregistered analysis plan — it operationalises the **single-pass baseline
arm** that the consensus (H3) and proposer-verifier (H2) architectures are
measured against. See `planning/leaderboard-construction-plan.md` (Update
2026-06-03) for the architecture-baseline prereg-framing template this analysis
sets.

---

## 7. Cross-references

- `configs/n1-eval-384px-14buf-mcc.yaml` — the re-score recipe (supersedes
  `configs/n1-eval-384px-all-buffers.yaml`).
- `results/paper-eval/n1/384px-14buf-mcc/` — the 18 per-cell evals (current).
- `results/paper-eval/n1/384px-all-buffers/` — the superseded 4-buffer, no-MCC
  evals, **marked superseded in place** (`SUPERSEDED.md`), not deleted and not
  moved: errata E57 and several working docs cite this exact path as a reference
  artefact, so relocating it would orphan those citations.
- `results/run-conditions.json` — the 18 baseline conditions (the
  `baseline-<slug>` entries on pv-diag-384 / n1-outstanding-384 /
  **n1-pro-rerun-384** / retest-h11-single-pass-384-t0).
- `results/run-analyses.json` → `results/analyses-manifest.json` — the leaderboard
  analysis (`analysis_id n1-baseline-matrix-384`, `type=leaderboard`) over the 18
  cells. **Finding authored 2026-06-03, revised same day for the E57 genuine-Pro
  replace** (`tie_set` = the sole Tier-1 leader `pro-text-high-t-0-0`, `outcome`,
  `predicted_outcome`, `preregistered=exploratory`, `hypothesis_refs` H1/H6/H7,
  `deviations` E57; `manually_verified_at` null pending sign-off on the revised text);
  see § 6.
- `scripts/n1_baseline_leaderboard_tiering.py` — the round-robin permutation +
  BH-FDR + greedy-clique tiering script that produced the § 6 finding (replicate-mean
  per-tile; reuses `compute_per_tile_tp_fp_fn`, `apply_bh_correction`).
- `results/paper-eval/n1/384px-14buf-mcc/tiering/tiering_20m.{json,md}` — the
  tiering result: per-pair p-values (raw + BH-adjusted), the 7-tier structure, the
  per-cell board-F1-vs-observed cross-check, and the `tie_set`.
- `results/paper-eval/n1/384px-14buf-mcc/pro-rerun/` — the four genuine-Pro re-run
  evals (`n1-pro-rerun-384`); `configs/n1-pro-rerun-eval-384px-14buf-mcc.yaml` is the
  recipe (hyphen glob).
- `docs/methodology/preregistration/protocol-errata.md` — E57 (Pro-pool
  model-of-record + the 2026-06-03 billing reconciliation: four "Pro" cells were
  Flash, genuine-Pro re-run, finding change), E56 (verifier threshold provenance —
  not applicable to these no-verifier baselines).
- `planning/manifest-3b-conditions-plan.md` — the decomposition plan (Batch E for
  the full pv-diag-384 decomposition).
- `planning/performance-shape-availability-map-2026-05-31.md` — the per-run
  performance-shape 2×2 map.

---

## Changelog

### 2026-06-03 — E57 genuine-Pro replace + re-tier (Session 98)

The E57 billing reconciliation found the four anti-diagonal "Pro" cells from
`n1-outstanding-384` were dispatched as **Flash**; they were re-run as genuine Pro
(`n1-pro-rerun-384`) and **replace** the Flash cells on the board (user decision).

- **Trigger**: `per_item_metadata.model_version = gemini-3-flash-preview` on the four
  `n1-outstanding-384` "Pro" cells (the `--model` override never threaded); genuine-Pro
  re-run committed `1cdf9438`, scored at 14-buffer + MCC (`pro-rerun/`).
- **Board**: `conditions_compared` swaps the 4 `n1-outstanding-384::pro-*` refs for
  `n1-pro-rerun-384::pro-*` (18 cells, all genuine-model); model-of-record corrected
  to `gemini-3-flash-preview` (n1-outstanding, off-board, preserved) and
  `gemini-3.1-pro-preview` (re-run). Manifests: 27→28 runs, 110→114 conditions,
  68→76 passes.

  | claim | before (pre-E57) | after (genuine Pro) |
  |---|---|---|
  | tiers | 6 (112/153 sig) | **7** (120/153 sig) |
  | `tie_set` | 2-member tie: `pro-text-medium-t-0-0` (0.763) + `pro-text-high-t-0-7` (0.745) | **single leader** `pro-text-high-t-0-0` (0.804) |
  | "weak Pro" anti-diagonal F1 | 0.42–0.53 (were Flash) | 0.59–0.80 (genuine Pro) |
  | MCC leader | `pro-image-high-t-0-7` (+0.852) | `pro-image-medium-t-0-7` (+0.913) |
  | H6 (Pro ≥ Flash) | "not uniform" (Flash beat weak Pro) | **uniform** (top 5 all genuine Pro) |

- **What did NOT change**: the eval protocol (14-buffer + MCC, bootstrap 10 000, seed
  42); the permutation/FDR/tiering method; the detection geometries; the genuine
  pv-diag-384 Pro cells. The tiering script now reads board membership from
  `conditions_compared` (single source of truth) and tries both pass-file globs
  (underscore + hyphen). Tiering computed on **sapphire**.
- Commits: `e1f20da4` (structural + model-of-record), `59727c8a` (re-tier),
  `c06aceee` (finding rewrite). Cross-ref Obs 337, errata E57 § Update (2026-06-03).

### 2026-06-03 — Leaderboard finding (Session 97)

Lifted the `n1-baseline-matrix-384` analysis from stub to **finding**.

- **Method**: round-robin paired tile-swap permutation (replicate-mean
  per-tile, 10 000 perms, seed 42, two-sided) + Benjamini–Hochberg FDR
  (q = 0.05) + greedy-clique tiering at 20 m, on zbook ($0 API). New script:
  `scripts/n1_baseline_leaderboard_tiering.py`; artefacts under
  `results/paper-eval/n1/384px-14buf-mcc/tiering/`.
- **Result**: 112/153 pairs significant → **6 tiers**; **`tie_set` (Tier 1) =
  `pro-text-medium-t-0-0` + `pro-text-high-t-0-7`** (BH-adjusted p = 0.50
  between them; both adj-p = 0.0000 vs rank 3). New § 6 "The leaderboard
  finding"; Cross-references renumbered § 6 → § 7.
- **Manifest**: `run-analyses.json` human fields authored (`tie_set`,
  `outcome`, `predicted_outcome`, `preregistered=exploratory`, `hypothesis_refs`
  H1/H6/H7, `deviations` E57, `manually_verified_at`); `analyses-manifest.{json,md}`
  regenerated (ALL VALID: 27 runs + 110 conditions + 68 passes + 1 analysis).
- **What did NOT change**: the 18 cells' F1/MCC values (§ 5) or the detection
  geometries — the tiering formalises the § 5 ordering. The permutation (robust
  to the `sparse_cross_grid` flag) confirms the CI-overlap read.
- Commit: landed this session (see `git log` for `results/run-analyses.json`).

### 2026-06-02 — Original publication (Session 96)

Created alongside the re-score of the 18 N=1 baseline pools to the 14-buffer
(`5…150 m`) + MCC standard and their authoring as single-pass conditions.

- **Re-score**: `results/paper-eval/n1/384px-all-buffers/` (4 buffers, no MCC) →
  `results/paper-eval/n1/384px-14buf-mcc/` (14 buffers + MCC), eval-only, on
  zbook. Old dir marked superseded in place (`SUPERSEDED.md`), retained because
  E57 cites its path.
- **Conditions**: +18 single-pass conditions in `results/run-conditions.json`
  (pv-diag-384 ×10 as a new conditions-only entry; n1-outstanding-384 ×7;
  retest-h11-single-pass-384-t0 ×1). Manifest conditions: 92 → 110.
- **What did NOT change**: the detection geometries (re-score is eval-only); the
  per-pass single-pass conditions on n1 / retest (the new cells are the headline
  aggregate, complementary to them); the F1 headline buffer (20 m, preregistered).
- Landed across two commits (eval provenance → repo-relative; conditions +
  manifest + doc); see `git log` for `results/run-conditions.json` and this file.
