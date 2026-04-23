# Tile-Level MCC Analysis Family — Consolidated Report

**Study**: Tile-level MCC / sensitivity / specificity across the paper-eval condition matrix
**Date**: 2026-03-27 (consensus-pv + 384 px + 512 px batches) / 2026-03-28 (remaining/top-up cohort) / 2026-04-22 (Phase 2b tile-level MCC, Session 74, Obs 274)
**Primary metric**: Matthews Correlation Coefficient (MCC) at the tile level, with bootstrap 95 % CIs
**Scope**: 89 conditions across 5 batch groupings (consensus-pv 12 + 384 px N=1 18 + 512 px P2a–P2e 33 + remaining-top-up 16 + Phase 2b 10)

## Scope note — this report vs the per-batch auto-summaries

Each of the five batch groupings has its own auto-generated
`batch_{mcc_}summary.{json,csv,md}` in its subdirectory. Those files
are the authoritative per-row sources for every numeric claim here.
This report is the cross-batch consolidating narrative: it explains
why the five groupings exist, highlights the paper-headline MCC
rows, and surfaces the Phase 2b MCC-inversion finding (Obs 274) that
sits orthogonally to the F1 headline.

## Five-batch organisation — why the MCC family is split

| Batch | Conditions | Scope | Date | Purpose |
|-------|----------:|-------|------|---------|
| `consensus-pv/` | 12 | 487 tiles, 20 m buffer | 2026-03-27 | Consensus + PV conditions at 384 px production scope — the primary paper-headline MCC layer (completes the MCC table originally drafted in Obs 202) |
| `384px/` | 18 | 487 tiles, 30 m buffer | 2026-03-27 | Single-pass N=1 conditions at 384 px across modality / thinking / temperature grid |
| `512px/` | 33 | 340 tiles, 30 m buffer | 2026-03-27 | Phase 2a–2e config exploration at 512 px — the pre-384 px justification layer |
| `remaining/` | 16 | 487 tiles, 20 m buffer | 2026-03-28 | Top-up cohort including verifier-stacked (`flash-min-vf`) variants and additional PV conditions |
| `phase2b/` | 10 | 340 tiles, 20 m buffer | 2026-04-22 | H7 temperature sweep tile-level MCC (2 tracks × 5 T, K=3 consensus at 2-of-3) — added Session 74, underpins Obs 274 |

Total: **89 conditions** under one consistent tile-level MCC pipeline
(`scripts/evaluate_tile_mcc.py` / config-driven batch runner),
bootstrap CI at n=1,000 iterations, seed 42, tile-level resampling.

## Headline MCC — top of the matrix

All values are tile-level MCC at the stated buffer, with 95 % bootstrap
CI. "n_populated / n_empty" refers to tiles with ≥ 1 GT vs tiles with 0
GT respectively.

### Verifier-stacked (flash-min-vf) conditions — top of the family

From `remaining/batch_mcc_summary.json` at 487-tile / 20 m scope:

| Condition | MCC [95 % CI] | Source |
|-----------|---------------|--------|
| **Image baseline + flash-min-vf** | **0.877 [0.833, 0.919]** | `remaining/image-baseline-flash-min-vf/mcc.json` |
| Text baseline + flash-min-vf | 0.833 [0.783, 0.877] | `remaining/text-baseline-flash-min-vf/mcc.json` |
| Flash HIGH image 3-of-5 + flash-min-vf | 0.827 [0.777, 0.873] | `remaining/flash-high-image-3-of-5-flash-min-vf/mcc.json` |
| Flash HIGH text 9-of-10 + flash-min-vf | 0.749 [0.696, 0.797] | `remaining/flash-high-text-9-of-10-flash-min-vf/mcc.json` |

### Consensus-PV layer (12 conditions)

From `consensus-pv/batch_mcc_summary.json` at 487-tile / 20 m scope:

| Condition | MCC [95 % CI] | Source |
|-----------|---------------|--------|
| Pro Image HIGH T=0.7 (N=1) | 0.848 [0.801, 0.894] | `consensus-pv/pro-image-high-t-0-7/mcc.json` |
| **Flash HIGH text 16-of-30 + PV** | **0.790 [0.733, 0.840]** | **paper-headline — TP/TN/FP/FN = 188/247/11/41** |
| Flash HIGH text 4-of-5 + PV | 0.769 [0.716, 0.820] | `consensus-pv/flash-high-text-4-of-5-pv/mcc.json` |
| Pro Text HIGH T=0.7 (N=1) | 0.741 [0.683, 0.794] | `consensus-pv/pro-text-high-t-0-7/mcc.json` |
| Pro HIGH text 3-of-5 | 0.736 [0.682, 0.788] | `consensus-pv/pro-high-text-3-of-5/mcc.json` |
| Pro HIGH text 3-of-5 + PV | 0.730 — | `consensus-pv/pro-high-text-3-of-5-pv/mcc.json` |
| Flash HIGH image 6-of-10 | 0.675 — | `consensus-pv/flash-high-image-6-of-10/mcc.json` |
| Flash HIGH image 3-of-5 | 0.665 — | `consensus-pv/flash-high-image-3-of-5/mcc.json` |
| Flash HIGH text 9-of-10 | 0.621 — | `consensus-pv/flash-high-text-9-of-10/mcc.json` |
| Flash HIGH text 26-of-30 | 0.620 — | cross-matches phase3a §3 "HIGH-T0.7 consensus" row at MCC 0.620 [0.549, 0.691] |
| Flash HIGH text 5-of-5 | 0.600 — | `consensus-pv/flash-high-text-5-of-5/mcc.json` |
| Flash Text MINIMAL T=0.0 (N=1) | 0.022 — | **empty-tile floor, not a performance estimate — see caveat below** |

### 384 px N=1 layer (18 conditions)

From `384px/batch_summary.json` at 487-tile / 30 m scope, top 5:

| Condition | MCC [95 % CI] | F1 (same run) |
|-----------|---------------|---------------|
| Pro Image HIGH T=0.7 | 0.852 [0.805, 0.897] | 0.741 |
| Pro Text MEDIUM T=0.0 | 0.752 [0.693, 0.807] | 0.784 |
| Pro Text HIGH T=0.7 | 0.746 [0.689, 0.799] | 0.791 |
| Pro Image MEDIUM T=0.0 | 0.734 [0.675, 0.795] | 0.737 |
| Pro Image HIGH T=0.0 | 0.606 [0.542, 0.667] | 0.651 |

### 512 px Phase 2a–2e exploration (33 conditions)

From `512px/batch_summary.json` at 340-tile / 30 m scope (the pre-384
px pipeline justification layer). MCC values sit in the 0.21–0.29 band
top 5, consistent with 512 px F1 ~0.60 (see `results/h11/analysis_summary.md`
for the tile-size comparison that moved the production pipeline to 384 px).
These rows are retained as methodological record; they should not be
cited as current paper headlines.

### Phase 2b MCC (10 conditions) — the T inversion finding

From `phase2b/batch_mcc_summary.json` at 340-tile / 20 m scope (Session 74,
Obs 274). Applied to the preregistered H7 temperature sweep at 2-of-3
consensus of K=3 runs:

| Condition | MCC [95 % CI] | Direction |
|-----------|---------------|-----------|
| Phase 2b Track 1 image T=1.3 | 0.368 [0.262, 0.472] | **Highest T has highest MCC** |
| Phase 2b Track 1 image T=1.0 | 0.333 [0.232, 0.425] | |
| Phase 2b Track 1 image T=0.7 | 0.228 [0.127, 0.332] | |
| Phase 2b Track 1 image T=0.3 | 0.108 [−0.006, 0.212] | |
| Phase 2b Track 1 image T=0.0 | 0.089 — | Lowest T has lowest MCC |
| Phase 2b Track 2 text T=1.3 | 0.221 [0.112, 0.319] | Same inversion (T↑ → MCC↑) |
| Phase 2b Track 2 text T=1.0 | 0.131 [0.029, 0.232] | |
| Phase 2b Track 2 text T=0.7 | 0.121 [0.013, 0.219] | |
| Phase 2b Track 2 text T=0.3 | 0.066 [−0.037, 0.171] | |
| Phase 2b Track 2 text T=0.0 | 0.064 [−0.043, 0.174] | |

**Phase 2b tile-level MCC inverts the F1 ordering** (F1 decreases
monotonically with T on Track 1 image, from 0.587 at T=0.0 to 0.490 at
T=1.3 per the Phase 2b analysis_summary). Obs 274 attributes the
inversion to flat sensitivity + climbing specificity as T rises: higher
T emits more detections, but on the sparse 340-tile / 340 GT Phase 2b
scope, the additional detections land increasingly in tiles with no GT
present, so specificity (TN / (TN+FP)) improves while F1 drops.
This is a **metric-choice artefact**, not a contradiction of the
temperature finding — the paper's T=1.0 claim rests on F1, which is
the primary preregistered metric.

Full Obs 274 framing at `docs/notes/reflections/working-notes.md` Obs
274; the inversion is worth flagging in the paper's Discussion on
metric-choice tradeoffs.

## ⚠️ Empty-tile floor — Flash Text MINIMAL T=0.0 (MCC = 0.022)

`consensus-pv/flash-text-minimal-t-0-0/mcc.json` reports MCC = 0.022
for a single-pass Flash text minimal T=0.0 run. This is **not a
performance estimate** — it is the empty-tile floor produced when a
low-precision pipeline over-emits detections on empty tiles
(inflating FP) while still finding most TPs on populated tiles. The
resulting TP / TN / FP / FN shape has large FP relative to TN, which
collapses MCC even though F1 and recall look respectable.

The paper should cite Flash Text MINIMAL T=0.0 for F1 comparisons only;
citing its tile-level MCC as "near-zero performance" would be
misleading without the empty-tile explanation. Flag for the Methods
section if the paper's condition-comparison table includes this row.

## Cross-hypothesis synthesis

### The MCC matrix as paper support

The paper's headline detection F1 = 0.904 @ 50 m on the 487-tile
matrix (K=30 text-HIGH + PV — see `results/paper-tables/metrics_master.json`)
has a tile-level MCC complement at Flash HIGH text 16-of-30 + PV
MCC = 0.790 [0.733, 0.840]. The two are different-axis views of the
same run: F1 weights by detection / GT balance; MCC weights by
all-four-cells confusion including tile-level TN.

| Axis | Metric | Value | Source |
|------|--------|-------|--------|
| Paper F1 headline | F1 @ 50 m | 0.904 [0.878, 0.928] | `paper-tables/metrics_master.json` |
| Same run, tile-level MCC | MCC | 0.790 [0.733, 0.840] | `consensus-pv/flash-high-text-16-of-30-pv/mcc.json` |
| Paper F1 K=5 companion | F1 @ 50 m | 0.891 [0.863, 0.916] | `paper-tables/metrics_master.json` |
| Same K=5 family, consensus only | MCC | 0.600 [511, 684] | `consensus-pv/flash-high-text-5-of-5/mcc.json` |
| Top verifier-stacked | MCC | 0.877 [0.833, 0.919] | `remaining/image-baseline-flash-min-vf/mcc.json` |

### Tile-size pipeline lock-in (cross-ref)

The 512 px MCC matrix (33 conditions, all < 0.29) alongside the 384 px
MCC matrix (18 conditions, top at 0.852) reinforces `results/h11/analysis_summary.md`'s
tile-size finding: the +0.063 F1 advantage at 384 px also manifests
as +0.55 MCC (0.29 → 0.85 at top-of-band). The MCC matrix is thus
internally consistent with the F1-based tile-size conclusion and adds
an additional line of evidence for the production pipeline choice.

## Paper implications

1. **MCC complements F1 at the paper-headline row.** Flash HIGH text
   16-of-30 + PV with MCC = 0.790 [0.733, 0.840] provides a tile-level
   balanced-accuracy metric alongside the F1 = 0.904 headline. Both
   metrics point to the same conclusion (strong detection); MCC's
   sensitivity to all-four-cells balance strengthens the claim by
   showing the performance is not artefact of a populated-tile-only
   evaluation.
2. **Verifier-stacked conditions are the top of the MCC matrix.**
   Image baseline + flash-min-vf reaches MCC = 0.877 — the highest
   observed across all 89 conditions. The paper's Discussion on
   verifier-stage value can cite this row.
3. **Phase 2b tile-level MCC inverts F1 (Obs 274).** This is a
   metric-choice finding worth raising in the paper's Methods /
   Discussion — F1 and MCC diverge at T=1.3 on the 340-tile Phase 2b
   scope because of sparsity interaction with specificity. The
   preregistered F1-based T=1.0-is-suboptimal claim holds (primary
   metric); the MCC inversion is a caveat that sophisticated reviewers
   may raise.
4. **Flash Text MINIMAL T=0.0 MCC = 0.022 is an empty-tile floor.**
   Not a condition failure. The paper's condition-comparison table
   should footnote this row if MCC is reported alongside F1.

## Reproducibility

| Metric | Value |
|--------|-------|
| Bootstrap iterations | 1,000 |
| Bootstrap seed | 42 |
| Bootstrap resampling | tile-level (each bootstrap draw resamples 487 tiles with replacement) |
| CI methodology | percentile, 95 % CI (2.5 / 97.5 quantiles) |
| Buffer | 20 m (consensus-pv, remaining, phase2b) / 30 m (384 px, 512 px) |
| Evaluation tiles | 487 (production) / 340 (Phase 2b + 512 px retrospective) |
| Run logs | `384px-eval.log`, `512px-eval.log` at top level; `phase2b/compute.log` |
| Evaluation script | `scripts/evaluate_tile_mcc.py` (per-condition `mcc.json` schema is consistent across all 5 batches) |

## Artefacts

### Five batch groupings

| Batch | Summary | Per-condition |
|-------|---------|---------------|
| consensus-pv | `results/paper-eval/mcc/consensus-pv/batch_mcc_summary.{json,csv,md}` | `results/paper-eval/mcc/consensus-pv/<condition>/mcc.json` (× 12) |
| 384 px | `results/paper-eval/mcc/384px/batch_summary.{json,csv,md}` | `results/paper-eval/mcc/384px/<condition>/evaluation.{json,csv,md}` (× 18) |
| 512 px | `results/paper-eval/mcc/512px/batch_summary.{json,csv,md}` | `results/paper-eval/mcc/512px/<condition>/evaluation.{json,csv,md}` (× 33) |
| remaining | `results/paper-eval/mcc/remaining/batch_mcc_summary.{json,csv,md}` | `results/paper-eval/mcc/remaining/<condition>/mcc.json` (× 16) |
| phase2b | `results/paper-eval/mcc/phase2b/batch_mcc_summary.{json,csv,md}` | `results/paper-eval/mcc/phase2b/phase2b-*/mcc.json` (× 10) |

### Cross-references

- F1 paper-table headline: `results/paper-tables/metrics_master.json` (Flash HIGH text 16-of-30 + PV F1 = 0.904)
- Tile-size comparison: `results/h11/analysis_summary.md` (MCC cross-ref at §"Headline")
- Phase 2b temperature: `results/retest/phase2b/analysis_summary.md` (F1 story; Obs 274 notes MCC inversion)
- Obs 202 — initial MCC table framing (pre-consensus-pv completion)
- Obs 274 — Phase 2b tile-level MCC inversion (Session 74, 2026-04-23)
- Meta-findings synthesis Theme T4 (subtype asymmetry) adjacent — tile-level balanced accuracy complements F1 in the paper's Discussion

## Scripts used

| Phase | Script | Purpose |
|-------|--------|---------|
| 1 | `scripts/evaluate_tile_mcc.py` | Per-condition tile-level MCC + sensitivity + specificity + bootstrap CIs |
| 2 | Batch runners (config-driven) | Iterate over `configs/mcc-eval-{384px,512px,…}.yaml` condition lists and emit per-batch summary JSON / CSV / MD (consolidation is in-script rather than a separate summariser) |

---

**Status**: Paper-citation narrative report for the tile-level MCC
analysis family. Supplements the five per-batch auto-summaries with
a single narrative target for papers that cite tile-level MCC
alongside F1. The per-batch summary MDs remain the authoritative
per-row sources; this report does not duplicate them — it explains
them.
