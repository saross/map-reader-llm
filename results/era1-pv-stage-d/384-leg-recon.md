# 384 consensus+PV leg — recon and findings

> **Last revised**: 2026-06-09 (initial publication — 384 leg of the Stage-D
> consensus+PV head-to-head, scored at 14-buffer + tile-MCC on zbook).
> See [§ Changelog](#changelog) for revision history.

This document records the disambiguation, scoring, and head-to-head result for
the **384 px consensus + proposer-verifier (PV)** cell, completing the
**256 / 384 / 512 px consensus+PV** tile-size comparison. The 256 and 512 legs
were produced in Session 107 Stage-D; only the 384 leg was missing at the
**14-buffer + tile-MCC** scoring protocol.

**Zero API calls.** The 384 leg is a pure re-score of verifier outputs that
already existed on disk (the carry-forward adversarial verifier ran over the
pv-diag-384 consensus pools in March 2026). Compute ran on **zbook**
(`zbook-ubuntu`), repo at commit `0b0202da2`, Python 3.12.3, geopandas 1.1.2.

## 1. The matched 384 verified pool

**Pool used**: `outputs/h11/pv-diag-384/verified/flash-high-text-16of30/`
(candidate_manifest.json + probabilities.json — 729 candidates).

### Provenance proof (read from metadata, not the directory name)

The `flash-high-text-16of30` consensus pool is **derived** from the per-pass
union by a vote threshold, recorded in its `probabilities.json` header:

```json
{ "source": "outputs/h11/pv-diag-384/verified/flash-high-text-1of30/probabilities.json",
  "derived_from": "1-of-30 union", "vote_threshold": 16 }
```

The source pool's verifier provenance is in
`outputs/h11/pv-diag-384/verified/flash-high-text-1of30/run.meta.json`
(`configuration` block):

| field | value |
|---|---|
| `version` | `verify_adversarial-text` |
| `model` | `gemini-3-flash-preview` |
| `instruction_file` | `verify_adversarial.md` |
| `thinking_level` | `minimal` |
| `temperature` | `0.0` |
| `example_count` | `0` (`library_hash: no_examples`) |
| iterations / n | `1` |

This is an **exact match** to the Stage-D carry-forward verifier
(`prompts/configs/verify_adversarial-text.json`: gemini-3-flash,
`verify_adversarial.md`, T=0.0, minimal thinking, text-only labels, examples=[],
n=1) and to the registered `verifier_config` on the 256/512 Stage-D conditions
(which also record `gemini-3-flash-preview`, minimal, T=0.0).

### Pools explicitly EXCLUDED (different verifier — confirmed from metadata)

- `flash-high-text-high-vf-*` → sourced from
  `flash-high-text-1of5-flash-high-verifier`, whose `run.meta.json` records
  `model: gemini-3-flash-preview`, **`thinking_level: high`** — a different
  (HIGH-thinking) verifier, not the carry-forward.
- `*-medium-vf-*`, `*-pro-vf-*`, `*-pro-verifier`, `*-flash-medium-verifier`,
  `*-flash-high-verifier` → verifier-model/thinking variants, all excluded.

### Why this pool (the verifier-match + consensus-champion judgement call)

The 512 Stage-D consensus champion is `512-consensus-text-high` =
`outputs/retest/phase3a-high/track2-text/T1.0/consensus/consensus_t23.geojson`,
which is the **HIGH-thinking text proposer, N=30 passes, 23-of-30 vote**
(verified: every feature has `total_passes: 30`, `min vote_count = 23`). The
Era-1 plan (`planning/era1-leaderboard-plan-2026-06-08.md`, lines 100–103)
explicitly maps **"phase3a-high (512, HIGH text) ↔ pv-diag-384 flash-high-text
(384)"**. So the matched 384 cell is the **`flash-high-text` (HIGH-thinking,
N=30) consensus family**.

Within that N=30 HIGH-text family, the **best-F1 operating point** (from
`results/h11-384-pv-diagnostic/summary.json`, where the project established the
384 consensus champion) is **`flash-high-text-16of30`** (single-buffer optimal
F1 0.8902 at prob_t 0.2). Each tile size selects its own best vote threshold —
512 settled at 23-of-30, 384 at 16-of-30 — consistent with the project's
per-size champion-selection approach and with the known "Goldilocks vote-
threshold shifts with tile size" finding (Obs 179).

**Judgement call, stated plainly for review**: I matched on *proposer config*
(gemini-3-flash, HIGH-thinking, text, N=30) + *verifier config* (carry-forward),
and let each size pick its own best vote threshold and prob_t — rather than
forcing an identical vote fraction across sizes. This mirrors how the 512 cell
itself was chosen (its own best vote). The residual cross-size mismatch is the
**proposer thinking level vs the 256 leg**: the 256 cell uses the *plain* `text`
family (5-of-5, N=5), because HIGH-thinking text was not separately run at 256
(pv-diag-256 is text-only with thin provenance). So 384 and 512 share the HIGH-
text N=30 lineage; 256 is its own anchor. This is the closest match the on-disk
material allows.

### prob_t sweep feasibility (NOT a HALT)

The pool carries per-candidate `mound_probability` for all 729 candidates, so
the prob_t sweep `[0.1, 0.15, 0.2, 0.3, 0.5]` is fully materialisable — the
re-score needed **no verifier re-run** and **no API spend**. (Acceptance counts
vary across prob_t: 502 / 418 / 412 / 391 / 373.) The HALT condition in the
brief did not trigger.

## 2. What the existing `proposer-verifier-384::verified-adversarial-text` (F1 0.471) actually is

The pre-existing condition (eval at
`results/rescore-2026-05-31/proposer-verifier-384/verified-adversarial-text-accepted/evaluation.json`,
**F1@20m 0.4708, MCC 0.4313**) is registered with:

- `proposer_pool: "detect_brief-text"`, `n_passes: 1`, `vote_threshold: null`

i.e. it is a **single-pass + PV** cell (the `detect_brief-text` single-pass
proposer, verified), **not a consensus+PV cell at all**. Its detections file
`outputs/h11/proposer-verifier-384/verified-adversarial-text-accepted.geojson`
holds 215 features. Its low F1 is exactly what one expects from un-consensused
single-pass proposals at a single (un-swept) operating point — it is the wrong
architecture for the consensus head-to-head, not a bad consensus number.

**Verdict**: it is **not superseded by** the new 384 consensus+PV cell — it
answers a different question (single-pass+PV at 384). The two coexist. The 0.471
number should **not** be used as "the 384 consensus+PV cell"; the new
`384-consensus-text-high` cell (F1 0.890) is that cell.

## 3. The completed 256 / 384 / 512 consensus+PV comparison

All three legs: consensus champion **verified** with the carry-forward
adversarial verifier, scored at **14-buffer + tile-MCC**, **F1@20 m** headline,
best prob_t operating point per cell. 256/512 read fresh from
`outputs/era1-pv-stage-d/stage_d_score_summary.json`; 384 from
`outputs/era1-pv-stage-d/stage_d_score_summary_384.json`.

| size | cell | proposer (model/think/N/vote) | F1@20 m | tile-MCC | prob_t | n_tiles |
|---:|---|---|---:|---:|---:|---:|
| 256 | `256-consensus-text-5of5` | flash / (thin) / N=5 / 5-of-5 | **0.8558** | 0.7448 | 0.2 | 1032 |
| **384** | **`384-consensus-text-high`** | **flash / HIGH / N=30 / 16-of-30** | **0.8902** | **0.7903** | **0.2** | **487** |
| 512 | `512-consensus-text-high` | flash / HIGH / N=30 / 23-of-30 | 0.7925 | 0.6765 | 0.1 | 340 |

384 detail at the chosen operating point (prob_t 0.2): precision 0.915,
recall 0.8667, 412 detections, n_tiles 487, eval CRS EPSG:32635.

Pipeline inputs (verified from the 384 eval `_metadata.cli_args`):

- detections: `outputs/era1-pv-stage-d/384-consensus-text-high/pass_1/accepted_t0.2.geojson`
- ground_truth: `inputs/vectors/references/mounds-reference.geojson` (curator GT)
- bounds: `inputs/vectors/bounds/384/full_evaluation_bounds.geojson` (**487 tiles**)
- buffers: `[5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 75, 100, 125, 150]`, `--mcc`

## 4. Verdict — does 384 still lead 256?

**Yes. 384 leads 256 (F1@20 m 0.8902 vs 0.8558, Δ +0.0344) when both are scored
consensus+PV the same way (14-buffer + tile-MCC, 4 GS maps + curator GT).** 512
sits below both at 0.7925. The order at 20 m is **512 < 256 < 384** — 384 is the
sweet spot, consistent with the project's prior "Goldilocks zone" finding.

**Not a surprise — it confirms the prior.** Obs 179's original-eval estimate
(F1 ≈ 0.883, a 487-tile eval, NOT 14-buffer+MCC) predicted 384 would still lead;
the re-scored 14-buffer+MCC value (0.890) lands right next to it. Two
independent sanity checks that the pipeline is correct (right GT, right 487-tile
bounds, right verifier, right operating point, EPSG:32635 eval CRS, no double-
reprojection): (a) the 14-buffer F1@20 m (0.8902) reproduces the diagnostic's
single-buffer optimal F1 (0.8902 at prob_t 0.2) to four decimals, and (b) it
matches the Obs 179 prior. No wildly-different value (e.g. near 0) appeared.

**Comparability note (carry forward into the paper):**

- **F1@20 m IS cross-size comparable** — the three sizes are different tilings of
  the same four Gold-Standard maps + the same curator ground-truth mounds, so
  mound-level localisation F1 compares directly.
- **tile-MCC is NOT differenced across sizes** — the true-negative base differs
  with tile count (256→1032, 384→487, 512→340 tiles), so MCC is reported per
  size, never subtracted across sizes.
- Tile size is confounded with tile set (smaller tiles ⇒ more tiles), so the Δ
  is the combined "smaller-tile + more-tiles" operational effect, not a pure
  tile-size isolation.

## 5. Registration block for the foreground to apply

Add this condition object to the **`pv-diag-384`** run's `conditions` array in
`results/run-conditions.json` (NOT applied here — the foreground owns that file).
The field shape mirrors `pv-diag-256::verified-adv-text-consensus-5of5`:

```json
{
  "label": "verified-adv-text-consensus-16of30",
  "architecture": "proposer-verifier",
  "aggregation": "verified",
  "proposer_pool": "flash-high-text-consensus-16of30",
  "source_run": "pv-diag-384",
  "n_passes": 1,
  "vote_threshold": null,
  "prob_threshold": 0.2,
  "verifier_config": {
    "variant": "v1",
    "instruction_file": "verify_adversarial.md",
    "model": "gemini-3-flash-preview",
    "thinking_level": "minimal",
    "temperature": 0.0
  },
  "eval_path": "results/era1-pv-stage-d/384-consensus-text-high/evaluation.json",
  "detections": "outputs/era1-pv-stage-d/384-consensus-text-high/pass_1/accepted_t0.2.geojson"
}
```

Notes on field choices (matched to the 256 cell):

- `n_passes: 1`, `vote_threshold: null` — these describe the **verifier** pass (a
  single verifier pass over the already-consensused pool), exactly as on the 256
  cell. The proposer consensus (N=30, 16-of-30) is carried in `proposer_pool`.
- `prob_threshold: 0.2` — the best-F1@20 m prob_t operating point for this cell.
- `proposer_pool: "flash-high-text-consensus-16of30"` — the HIGH-text N=30
  consensus champion at 384 (analogue of the 256 cell's `text-consensus-5of5`).

`scripts/tile_size_sweep.py`'s new **View 3** (`PV_MATCHED`) already references
`pv-diag-384::verified-adv-text-consensus-16of30`; until this block is applied it
renders the 384 cell as an em-dash (graceful no-op). Once applied, re-running
`python scripts/tile_size_sweep.py` will populate the 384 PV cell (0.890) and
flip the View-3 direction annotation to `best=384px`.

## Changelog

### 2026-06-09 — Original publication

Initial 384 leg of the Stage-D consensus+PV head-to-head. Identified the matched
verified pool (`flash-high-text-16of30`), confirmed the carry-forward verifier
from `flash-high-text-1of30/run.meta.json`, scored it at 14-buffer + tile-MCC on
zbook (best prob_t 0.2 → F1@20 m 0.8902, MCC 0.7903, n_tiles 487), and
established that **384 leads 256** consensus+PV (0.890 vs 0.856), confirming the
Obs 179 prior. Landed in commit (this report's commit — see `git log`).
