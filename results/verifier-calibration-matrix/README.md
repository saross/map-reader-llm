# Verifier-Calibration Matrix

**Anchor observations**: Obs 277 (canonical Pareto-dominant verifier-prompt
selection); Obs 290 (Wave 3 refresh confirmed canonical-aligned).

**Canonical regeneration**: Phase C of the Session 78 re-run
(commit `fc7784158b04cbdd764a56fbf201666dede5f4c2`, short `fc778415`,
2026-04-25). Buffer-elasticity addendum: commit `2a928cf7` (2026-04-27,
Wave 3 of Session 80, Theme 6).

## Purpose

This matrix tests whether any of seven verifier-prompt variants can rescue
the image-track verifier miscalibration first observed in Obs 269. The
matrix is the falsification test that distinguishes between two candidate
explanations of that miscalibration — *prompt-specific* vs
*input-distribution-specific* — and is the basis for Obs 277's
Pareto-dominance claim for the canonical `verify_adversarial-text` prompt.

## Scope

| Axis | Value |
|:---|:---|
| Corpus | 487-tile Era 2 evaluation scope |
| Tile bounds | `inputs/vectors/bounds/384/full_evaluation_bounds.geojson` |
| Ground truth | `inputs/vectors/references/mounds-reference.geojson` |
| Buffers (deep evaluation) | 5, 10, 15, 20, 25, 30, 35, 40, 45, 50 m |
| Operating buffer | 20 m (per-cell `vote_t`, `prob_t` optimised here) |
| Bootstrap | 10 000 iterations, seed=42, tile-level resampling |
| Tile-level metrics | MCC, sensitivity, specificity (alongside F1, P, R) |

The 487-tile Era 2 scope is preferred for 384 px analyses on this corpus
(see global preference `feedback_384px_scope_preference`).

Image-track candidates are drawn from `flash-high-image-n5 @ T=0.7`
(2 017 candidates, 1-of-5 raw pool); text-track from
`flash-high-text-n5 @ T=0.7` (~3 700-candidate pool, exact count varies
by re-run wave).

## Matrix axes

**Two axes; 7 × 2 = 14 cells**:

1. **Modality (proposer pool)** — 2 levels:
   - `image` — image-track proposer (`flash-high-image-n5`)
   - `text`  — text-track proposer (`flash-high-text-n5`)

2. **Verifier-prompt variant** — 7 levels:
   - `adversarial-text` — *canonical*; text-only verifier; 6-example library
   - `adversarial`      — with-images twin of canonical
   - `brief`            — terse with-images variant
   - `brief-text`       — text-only twin of brief
   - `checklist`        — structured with-images variant
   - `checklist-text`   — text-only twin of checklist
   - `comparative`      — positively-framed with-images variant authored in
     Session 78 specifically to test whether removing adversarial framing
     improves calibration (Obs 277 falsifies this hypothesis)

The canonical `verify_adversarial-text` prompt config lives at
`prompts/configs/verify_adversarial-text.json`. All 14 cell directories
follow the naming convention `{pool}-{variant}/`.

## Methodology and provenance

### Phase A — Verifier API runs

Per-variant verifier API runs against the shared candidate-crop pool for
each modality (`outputs/h11/pv-diag-384/flash-high-{image,text}-n5/
{image,text}-t0.7/session-78-matrix/`). Phase A used Gemini 2.5 Flash with
HIGH thinking, flex tier; produces `verified-{variant}/probabilities.json`.

Phase A was originally executed in Session 78 (commit `6d1cad27`, then
`88d6b55b`); after a 2026-04-25 confabulation cascade required
re-derivation, the canonical Phase A is commit `b10aa7e1` with crop-set
parity now applying to the canonical `adversarial-text` cell as well as
the six alternatives. See
`docs/methodology/data-reproduction-2026-04-25.md` for the provenance
chain and per-cell drift table (max |ΔAUC| 0.009; max |ΔECE| 0.009;
max |ΔF1| 0.035 in `text-brief-text`).

### Phase B — Threshold sweeps

`scripts/score_leaderboard_cells.py` sweeps the (`vote_t` ∈ 1–5,
`prob_t` ∈ 0.0/0.05/.../0.6) grid at buffers 20/30/40/50 m for each cell
and selects the per-cell optimum at the 20 m buffer.

> **Threshold provenance (E56, 2026-06-02)**: this per-cell optimum is selected
> on the **487-tile test set** — there is no calibration-tile verifier data to
> select on (the verifier never ran on the 20 held-out calibration tiles). So a
> single `prob_t`-thresholded F1 from this matrix is an **in-sample** quantity.
> Report these as **threshold-sensitivity curves**, not calibrated operating
> points; the headline proposer-verifier result uses the binary verdict
> (`prob_t = null`). See `docs/methodology/preregistration/protocol-errata.md` E56.

### Phase C — Materialisation and deep evaluation (canonical)

Per-cell post-verifier detection sets are materialised at each cell's
20 m optimum via `scripts/build_post_verifier_geojson.py`, producing the
`{pool}-{variant}-opt-20m.geojson` files at the matrix root (14 of these).

`scripts/evaluate_detections.py` then evaluates each materialised geojson
at 5 m increments from 5 to 50 m (`--bootstrap 10000 --seed 42 --mcc`),
producing the `{pool}-{variant}/evaluation.{json,csv,md}` triple in each
cell directory.

Orchestrated by `scripts/session-78-matrix-rerun-phases-bcd.sh`.

### Phase D — Calibration metrics

`scripts/compute_session78_calibration_matrix.py` computes per-cell AUC,
Brier score, ECE, per-bin empirical P(mound), and low-tail miscalibration
(threshold 0.25), with 10 000-iteration bootstrap CIs. Writes
`{pool}-{variant}/calibration.json` (14 files).

### Wave 3 buffer-elasticity addendum (2026-04-27)

`buffer-elasticity-5m.md` at the matrix root captures the F1 vs buffer
behaviour at 5 m granularity for all 14 cells. All cells are
F1-monotonic in buffer at 5 m granularity. Image-track elasticity
(20 → 50 m) is 12.5–13.8 %; text-track is 2.9–3.1 % — the ~4× modality
split observed at the pre-PV consensus stage (Obs 252) persists through
the verifier.

## File guide

### Per-cell files (14 directories: `{image,text}-{variant}/`)

| File | Contents |
|:---|:---|
| `evaluation.json` | F1/P/R per buffer (5–50 m at 5 m); 95 % CIs; tile-level confusion matrix; MCC, sensitivity, specificity. Includes full `_metadata` block (script path, git commit, CLI args, input-file paths). |
| `evaluation.csv`  | Per-buffer F1/P/R as a flat CSV (machine-readable). |
| `evaluation.md`   | Human-readable summary table. |
| `calibration.json` | AUC, Brier, ECE point estimates + 95 % CIs; 10-bin reliability diagram (mean predicted vs empirical P(mound)); low-tail miscalibration (threshold 0.25); bootstrap parameters. |

### Matrix-root files

| File | Contents |
|:---|:---|
| `{pool}-{variant}-opt-20m.geojson` (×14) | Per-cell post-verifier detection set materialised at the 20 m-optimal `(vote_t, prob_t)`. EPSG:4326, RFC 7946. Inputs to `evaluate_detections.py`. |
| `buffer-elasticity-5m.md` | Wave 3 5 m-granularity F1 vs buffer summary across all 14 cells (commit `2a928cf7`). |
| `README.md` | This file. |

## Cross-references

- **Obs 277** (`docs/notes/reflections/working-notes.md` line 13215):
  canonical `verify_adversarial-text` is Pareto-dominant on calibration
  metrics across all seven prompt variants. Image: best AUC (0.857) +
  best ECE (0.179). Text: best ECE (0.071). No prompt variant materially
  improves image-track calibration — all stay in the miscalibrated
  regime (ECE 0.19–0.27). Tier-flip caveat for the text track:
  with-image variants (`adversarial`, `comparative`, `checklist`,
  `brief`) beat canonical on F1@20 m by 0.013–0.023 while losing on
  calibration.
- **Obs 290** (`docs/notes/reflections/working-notes.md` line 14190):
  Wave 3 refresh of the 14-cell matrix produced **zero substantive
  corrections**; canonical `adversarial-text` retains lowest ECE on both
  pools after Phase C re-derivation.
- **Per-architecture leaderboard tier files**:
  `results/leaderboard/per-architecture/cross-architecture-paired-era2_f1.md`,
  `results/leaderboard/per-architecture/cross-architecture-paired-era2_mcc.md`
  — Era 2 paired tier rankings reference these matrix cells.
- **Buffer-elasticity comparison**:
  `results/secondary-effects/secondary_effects.md` §6 (phase3a image
  consensus, 10 m granularity) and
  `results/phase3a-text-matrix/secondary_effects.md` §6 (phase3a text
  consensus, 10 m granularity).
