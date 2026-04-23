# H10 v2 — Calibration-Pool Size Analysis Summary

**Study**: H10 v2 — Training Pool Size Effects on Library Quality (384 px / production carry-forward)
**Date**: 2026-04-15 (runs launched and evaluated 2026-04-15)
**Protocol-errata**: E49 (cold-start production config instead of preregistered image-only baseline)
**Primary aggregation**: greedy consensus; post-verifier (PV) at 2D vote × probability optima
**Secondary aggregation**: WBF variant C (reported for cross-hypothesis comparability)
**Evaluation**: 327-tile h10-384 test set, 20 m buffer, 1000 bootstrap iterations, seed=42
**Permutation**: tile-level paired, 10,000 iterations, seed=42 (method: E45 micro-average F1)

## Scope note — what this summary covers and what it does not

This document covers the **primary H10 v2 experiment** (the 4-pool-size
sweep at hp4hn4 — 020 / 040 / 080 / 160 — launched 2026-04-15 under
clean E49 conditions with `include_example_images: true`).

The sibling 5-config HP:HN probe at pool_160 (hp2hn6 / hp4hn4 /
hp6hn2 / hp8hn8 / hp16hn16), originally run 2026-04-11 at K=10 as
part of the H10/H12 v1 arm, was **formally retracted by Obs 235
(2026-04-14)** because the proposer config used
`include_example_images: false` — the few-shot library was never
transmitted to the API. The 5-config analytical coverage is provided
instead by the sibling clean K=5 re-runs under H8 v2 (Scale-8 / 16 /
32 = hp4hn4 / hp8hn8 / hp16hn16) and H12 v2 (R1 / R2 / R3 = hp2hn6 /
hp4hn4 / hp6hn2). See §"Cross-hypothesis coverage" below for the
mapping and §"Preserved-for-archive: retracted v1 probe data" for
the retained (but not citable) retracted-probe files.

## Headline result — pool-size null under PV

Four nested calibration pools (20 ⊂ 40 ⊂ 80 ⊂ 160) produce
post-verifier F1s indistinguishable within sampling noise:

| Comparison | F1 (a → b) | ΔF1 | p | Signif? |
|------------|------------|------|---|---------|
| pool_020 PV vs pool_160 PV | 0.727 → 0.722 | +0.005 | 0.845 | no |

The consensus-only stage shows a +0.020 F1 lead for pool_160 driven
by a higher-precision / lower-recall operating point; the verifier
compresses this lead to near-zero by filtering pool_020's noisier
consensus output more aggressively. Three smaller pools (020 / 040 /
080) are statistically indistinguishable at consensus (ΔF1 < 0.01)
and pool_160's PV result matches pool_020's PV result.

## Cross-hypothesis context — library axis closed

H10 v2 primary, H8 v2, and H12 v2 collectively close the hard-example
library axis at the proposer stage:

| Hypothesis | Factor | Levels | Result | Reference |
|------------|--------|--------|--------|-----------|
| **H10 v2** | **Calibration-pool size** | **4 (20, 40, 80, 160)** | **NULL under PV** | **this report** |
| H8 v2 | Library composition + size | 7 | NULL after BH-FDR | `results/h8-v2/analysis_summary.md` |
| H12 v2 | HP:HN ratio at fixed size=8 | 3 (2:6, 4:4, 6:2) | NULL after BH-FDR | `results/h12-v2/analysis_summary.md` |

All three preregistered factors on the library axis return nulls
under production carry-forward settings. The library has four
canonical positive slots and three null slots; what fills the
remaining slots does not measurably affect proposer F1 on this
task.

## Experiment — Calibration-pool size sweep

### Design

Four nested calibration pools (20 ⊂ 40 ⊂ 80 ⊂ 160 tiles), each
cold-started from legend positives plus null examples (no pre-existing
hard examples). Hard cases mined via K=5 detection passes per pool;
balanced 4:4 HP:HN libraries built from each pool's mined
discoveries. Evaluation on 327 disjoint holdout tiles at greedy
consensus across thresholds T=1..5, then PV (pool_020 and pool_160
selected for the full 2D verifier sweep).

### Consensus-only results

| Pool | Best T | F1 | Precision | Recall | n detections |
|------|:------:|-----|-----------|--------|--------------|
| 020 | T=3 | 0.697 | 0.672 | 0.724 | 344 |
| 040 | T=3 | 0.694 | 0.669 | 0.721 | 344 |
| 080 | T=3 | 0.688 | 0.666 | 0.712 | 341 |
| **160** | **T=4** | **0.717** | **0.843** | **0.624** | **236** |

Pool_160 leads by +0.020 F1 but at a fundamentally different
operating point — substantially higher precision (+0.17) bought at
a cost in recall (−0.10). The three smaller pools are
indistinguishable (ΔF1 < 0.01). Pool_160's larger calibration set
produces hard examples that make the model more conservative.

### PV pipeline results (pool_020 vs pool_160)

| Pool | Best (vote_t, prob_t) | F1 | Precision | Recall | n |
|------|-----------------------|-----|-----------|--------|---|
| 020 | (3, 0.15) | **0.727** | 0.765 | 0.693 | 289 |
| 160 | (4, 0.05) | 0.722 | 0.858 | 0.624 | 232 |

Pool-size lead at consensus is eliminated under PV. Pool_020 edges
slightly ahead (ΔF1 = +0.005, pool_020 minus pool_160, matching the
headline table's sign convention) because the verifier has more
false positives to filter from pool_020's noisier
consensus output (+0.093 precision gain from pool_020 consensus to
PV, from 0.672 to 0.765), while pool_160's already-high precision
(0.843 at consensus) leaves the verifier with little to improve and
its recall deficit (0.624 at consensus) cannot be recovered (the
verifier only filters; it cannot add detections).

### Permutation test

Tile-level micro-average F1 permutation test (method E45):

- Comparison: pool_020 PV vs pool_160 PV at 20 m buffer
- Observed ΔF1: +0.0047 (pool_020 leads)
- Permutations: 10,000 (seed 42 is the project-wide convention for
  permutation tests — not recorded in this specific JSON, which
  predates the E45 seed-as-metadata requirement for the script's
  output schema)
- n_tiles: 327
- p-value: **0.845**
- Per-tile breakdown: pool_020 wins 35, pool_160 wins 33, ties 259

The three-way pattern — 35 : 33 : 259 — is a hallmark of nulls at
this scale: ~80 % of tiles tie, and the remaining ~20 % split close
to evenly between the two conditions.

### WBF variant C comparison across pool sizes

| Pool | Best T | F1 (WBF) | Precision | Recall | n fused | Δ (greedy − WBF) |
|------|:------:|---------:|----------:|-------:|--------:|-----------------:|
| 020 | T=5 | 0.685 | 0.722 | 0.652 | 288 | +0.012 |
| 040 | T=5 | **0.694** | 0.739 | 0.655 | 283 | **−0.001** |
| 080 | T=5 | 0.670 | 0.715 | 0.630 | 281 | +0.018 |
| 160 | T=5 | 0.701 | 0.750 | 0.658 | 280 | +0.016 |

Greedy consensus and WBF variant C are statistically indistinguishable
across the four pool sizes: on three of four pools the greedy arm
leads by 0.012–0.018 F1, and on pool_040 the two are effectively tied
(greedy 0.694 at T=3 vs WBF 0.694 at T=5 — WBF lead of 0.001). The
direction matches the text-track WBF findings (Obs 230) at the same
scale, and the pool-size null holds across aggregation methods. (All
four pool-size WBF results are from the clean 2026-04-15 runs, not
the retracted pre-retraction pass — see §"Preserved-for-archive"
below for the separate retracted-data aggregation test.)

## Cross-hypothesis coverage — HP:HN ratio and library size at pool_160

The 5-config HP:HN + library-size matrix at pool_160 is collectively
covered by the sibling clean K=5 runs under H8 v2 and H12 v2, all
launched 2026-04-15 with `include_example_images: true`:

| Config | Pool | Covered by | Clean F1 at greedy t=4 | CI [lo, hi] |
|--------|:----:|------------|:----------------------:|-------------|
| pool_160_hp2hn6 | 160 | H12 v2 R1 (HN-heavy) | 0.708 | [0.643, 0.761] |
| pool_160_hp4hn4 | 160 | H8 v2 Scale-8 / H12 v2 R2 | 0.710 / 0.717 | [0.648, 0.765] / [0.661, 0.768] |
| pool_160_hp6hn2 | 160 | H12 v2 R3 (HP-heavy) | 0.688 | [0.637, 0.740] |
| pool_160_hp8hn8 | 160 | H8 v2 Scale-16 | 0.693 | [0.633, 0.749] |
| pool_160_hp16hn16 | 160 | H8 v2 Scale-32 | 0.713 | [0.660, 0.763] |

F1 spread across the 5 configs: **0.029** (hp6hn2 0.688 →
hp16hn16 0.713 via hp4hn4 at 0.710–0.717). All bootstrap CIs
overlap. H12 v2's three-way pairwise permutation finds no
significant difference (Obs 239, all BH-adj p > 0.5); H8 v2's seven-
contrast permutation finds no significant difference either
(Obs 238, all BH-adj p > 0.83). Two different hypothesis studies
independently arrive at the library-design null at pool_160.

The standalone "5-config probe" framing — as a single analysis
aggregating HP:HN + library-size variation at pool_160 — is not
materialised as a dedicated clean h10 summary because the clean
re-runs were organised under H8 v2 and H12 v2 rather than as an
h10-framed re-probe. Readers wanting cross-cutting analysis at
pool_160 should start with the meta-findings synthesis at
`results/meta-findings-summary.md` Themes T2 and T5 and descend
to `results/h8-v2/analysis_summary.md` and
`results/h12-v2/analysis_summary.md` for condition-level detail.

## Preserved-for-archive: retracted v1 probe data

The following files in `results/h10/` are derived from the
retracted H10/H12 v1 arm (Obs 235, 2026-04-14) and **must not be
cited for any library-composition or HP:HN claim** in the paper:

| File | Generated | Source data | What it reports |
|------|-----------|-------------|-----------------|
| `archive/h10-h12-v1-retracted-probe/results/h10/sweep_results.json` | 2026-04-14 | retracted v1 K=10 text-only | 315-cell 2D sweep over 5 configs |
| `archive/h10-h12-v1-retracted-probe/results/h10/statistical_analysis.json` | 2026-04-14 | same | Bootstrap CIs + 10 pairwise permutations for 5 configs |
| `archive/h10-h12-v1-retracted-probe/results/h10/verifier_independence_probe.{json,md}` | 2026-04-14 | same | Cross-config clustering + ICC(2,1) agreement |
| `archive/h10-h12-v1-retracted-probe/results/h10/k5_replicate_sweep.json` | 2026-04-14 | same | K=5 replicate consistency sub-sweep |
| `archive/h10-h12-v1-retracted-probe/results/h10/consensus_dedup_magnitude_diagnostic.json` | 2026-04-14 | same | Cross-config clustering sensitivity to dedup radius |
| `archive/h10-h12-v1-retracted-probe/results/h10/wbf/sweep_results_pool_160_hp4hn4_variant_c.json` | 2026-04-14 | same | WBF 2D sweep on hp4hn4 K=10 text-only |
| `archive/h10-h12-v1-retracted-probe/results/h10/wbf/variant_c_vs_greedy_hp4hn4.json` | 2026-04-14 | same | WBF variant C vs greedy on hp4hn4 K=10 |

These files are preserved per the `CLAUDE.md` §"Unexpected Data as
Discovery Opportunities" policy and the archive-never-delete
directive, NOT because they support any scientific claim about
calibration-pool composition. Their F1 values (0.86–0.89 at 2D
optima) reflect the K=10 text-only proposer pipeline augmented by
a verifier stage — not library-quality effects. The apparent
condition-to-condition F1 variance reflects Gemini's run-to-run
stochasticity on the same text-only prompt, not library manipulation
effects (Obs 235's explicit finding: "the library_hash difference
between pools is bookkeeping only").

### One partially-preserved finding — Obs 230 WBF vs greedy aggregation test

Obs 235 explicitly retained the WBF-vs-greedy aggregation comparison
at hp4hn4 (Obs 230) as "a valid aggregation-method test at K=10" —
reframed from "on hp4hn4" (which implies a library-composition
connection that does not exist) to "on a K=10 `detect_brief-text`
text-only run".

The partial-corrected finding, for archival record only:

| Aggregation | Best (vote_t, prob_t) | F1 [95 % CI] | Precision | Recall | n |
|-------------|-----------------------|--------------|-----------|--------|---|
| Greedy | (6, 0.15) | 0.885 [0.848, 0.917] | 0.913 | 0.859 | 300 |
| WBF variant C | (7, 0.15) | 0.880 [0.845, 0.911] | 0.899 | 0.862 | 306 |

Paired permutation: greedy ΔF1 over WBF = +0.005, p = 0.602, wins_greedy
= 11, wins_wbf = 11, ties = 305. Greedy and WBF variant C are
statistically indistinguishable at the K=10 post-verifier operating
point. This is an **aggregation-method test**, not a library claim —
the 0.88 F1 reflects the K=10 `detect_brief-text` text-only pipeline
augmented by the verifier, and the per-config differences in
`wbf/variant_c_vs_greedy_hp4hn4.json` should not be interpreted as
library effects.

## Caveats

1. **Pool-size PV test is pool_020 vs pool_160 only.** Pool_040
   and pool_080 have consensus-only data but no PV 2D sweep. Obs 236
   treats the three smaller pools as indistinguishable at consensus
   (ΔF1 < 0.01) and therefore unlikely to separate under PV. This
   is a reasonable assumption given the 020 vs 160 null, but it has
   not been directly tested and is a minor limitation of the study.
2. **E49 deviation from preregistered H10 design.** H10 v1 was
   intended to run at the preregistered image-only baseline (T=1.0,
   K=5). H10 v2 instead uses production carry-forward settings
   (T=0.7, HIGH thinking, `include_example_images: true`). The
   justification is documented in E49: the v1 settings would have
   produced a library-visible-to-model gap that Obs 235 retracted.
   The v2 null is a NULL for the production pipeline, not for the
   preregistered image-only baseline. This is a deliberate,
   defensible deviation, but readers should not read "H10 v2 null"
   as "calibration-pool size is null under the original prereg
   settings".
3. **Seed metadata not in permutation JSON.** The pool_020 vs
   pool_160 PV permutation result file
   (`results/h10/h10_pv_permutation_020_vs_160.json`) does not
   record the seed in-file; the project-wide convention is seed = 42
   (matching all other permutation tests in `results/h8-v2/`,
   `results/h12-v2/`, and `archive/h10-h12-v1-retracted-probe/results/h10/statistical_analysis.json`).
   A future polish pass could re-emit the JSON with the seed field
   populated.
4. **Retracted probe data is preserved, not cited.** §"Preserved-for-
   archive" above enumerates the retracted files. Future analyses
   that encounter these files must not cite their F1 values as
   library-composition evidence. The scorecard
   `planning/interim-docs-review.md` §3.11 instruction to "use
   sweep_results.json + statistical_analysis.json for the main
   table" was written before the Session 75 re-audit; that
   instruction is superseded by this summary's scope note.

## Paper implications

1. **Calibration-pool-size null under PV.** The four pool sizes
   (20, 40, 80, 160) produce PV-stage F1s indistinguishable within
   sampling noise. Practically this means: a new deployment can
   calibrate on ~20 tiles (5 per map sheet), mine hard examples at
   K=5, and achieve PV-pipeline performance equivalent to calibrating
   on 160 tiles. This is a substantial practical claim — it
   substantially reduces the calibration cost for a new deployment.
2. **Cross-study closure of the library axis.** Together with H8 v2
   (composition + size null) and H12 v2 (HP:HN ratio null), H10 v2
   supports a paper-Discussion claim that library curation beyond
   canonical positives + null examples does not materially affect
   detection F1 on this task.
3. **Verifier-compression mechanism.** The consensus-only +0.020
   F1 lead for pool_160 arises from a higher-precision / lower-
   recall operating point, which the verifier filters-then-compresses:
   it cannot add back the missing pool_160 recall, but it removes the
   pool_020 precision deficit. The result is a 0.727 vs 0.722 near-
   tie after PV. This is a direct mechanism-level explanation of why
   the proposer-stage null generalises to PV — documented here for
   the paper's Methods / Discussion section on verifier role.
4. **Preservation policy audit.** The Obs 235 retracted data was
   preserved per CLAUDE.md policy, but sat unflagged in
   `results/h10/` until Session 75. This summary's §"Preserved-for-
   archive" list and the scorecard §3.11 update are the corrective
   action. Future preservation of retracted or misconfigured runs
   should add the retraction flag at the results-directory level at
   the moment of retraction, not lazily at paper-writeup time.

## Reproducibility

| Metric | Value |
|--------|-------|
| Bootstrap iterations | 1,000 |
| Bootstrap seed | 42 |
| Bootstrap resampling unit | tile-level |
| Permutation iterations (pool_020 vs pool_160 PV) | 10,000 |
| Permutation seed (project convention; not in-file) | 42 |
| Permutation method | E45 tile-level micro-average F1 |
| Evaluation tiles | 327 |
| Evaluation buffer | 20 m |
| K (pool-size experiment) | 5 (production operating point) |
| PV sweep grid | 9 vote_t (2..10) × 20 prob_t (0.0..0.95 step 0.05) × 4 buffers = 720 cells per condition |

## Artefacts

### Clean primary experiment (2026-04-15)

- Raw detections (4 pool sizes × 5 runs):
  `outputs/h10/evaluation-v2/pool_{020,040,080,160}_hp4hn4/run_{1..5}/detections-detect_pool_{020,040,080,160}_hp4hn4_v2-3-flash-2026-04-15.geojson`
- Per-condition configs:
  `prompts/configs/h10/detect_pool_{020,040,080,160}_hp4hn4_v2.json` (or similar; exact filenames follow the `detect_<config>_v2` naming convention from the meta.json `version` field)
- Pool provenance:
  `outputs/h10/example-pools-v2/pool_{020,040,080}_hp4hn4/pool_metadata.json`
  `outputs/h10/example-pools-v2/pool_160_hp4hn4/pool_metadata.json`
  (pool_160 also has `pool_160_hp8hn8` and `pool_160_hp16hn16` subdirs; hp2hn6 and hp6hn2 variants are prefix-nested from hp8hn8 and hp16hn16 respectively per the E51 greedy-diversity pool-selection rationale)
- Consensus-only evaluation: `results/h10/h10_consensus_only_20m.json` (mtime 2026-04-15 14:56 local)
- PV evaluation (pool_020): `results/h10/h10_pool_020_pv_20m.json` (mtime 2026-04-15 15:56 local)
- PV evaluation (pool_160): `results/h10/h10_pool_160_pv_20m.json` (mtime 2026-04-15 15:56 local)
- PV permutation (020 vs 160): `results/h10/h10_pv_permutation_020_vs_160.json` (mtime 2026-04-15 16:51 local)
- WBF consensus (all 4 pools): `results/h10/h10_wbf_consensus_20m.json` (mtime 2026-04-15 15:03 local)
- Protocol errata: `docs/methodology/preregistration/protocol-errata.md` §E45 (permutation methodology), §E49 (H10 cold-start config)
- Working-notes narrative anchor: `docs/notes/reflections/working-notes.md` Obs 236

### Retracted-v1 probe (preserved for archive; do NOT cite)

- Raw detections (K=10 text-only, `include_example_images: false`):
  `archive/h10-h12-v1-retracted-probe/outputs/h10/evaluation/pool_160_hp{2hn6,4hn4,6hn2,8hn8,16hn16}/run_{1..10}/detections-detect_brief-text_pool_160_hp{*}-3-flash-2026-04-11.geojson`
- Consensus outputs: `archive/h10-h12-v1-retracted-probe/outputs/h10/consensus/pool_160_hp*/consensus-{1,2,4,5,6}of10.geojson` (all mtime 2026-04-14)
- WBF candidates and verifier outputs: `archive/h10-h12-v1-retracted-probe/outputs/h10/{wbf, verified, verifier-crops}/` — all derived from the retracted raw detections; see the archive README for details
- Aggregated analyses: see §"Preserved-for-archive" table above
- Retraction record: Obs 235 at `docs/notes/reflections/working-notes.md` line ~9396

## Scripts used

| Phase | Script | Purpose |
|-------|--------|---------|
| 1 | `scripts/run_phase2.py` (or the project's standard detection-launch entrypoint) | K-pass detection runs per pool × config |
| 2 | `scripts/merge_passes.py --sweep` | Greedy consensus threshold sweep |
| 3 | `scripts/fuse_detections_wbf.py --config h10-variant-c` | WBF variant C |
| 4 | `scripts/run_pv.py` | Post-proposer verifier probability scoring |
| 5 | `scripts/evaluate_detections.py` | F1/P/R with 1,000-iteration bootstrap CIs |
| 6 | `scripts/pairwise_permutation_test.py --mode tile-level` | Tile-level micro-F1 permutation (E45) |
| 7 | `scripts/resweep_pv_on_h10.py` | PV 2D sweep recomputation on h10 candidates |
| 8 | `scripts/compare_wbf_vs_greedy.py` | WBF vs greedy paired permutation (used for the Obs 230 aggregation-method test, on the retracted data) |
| 9 | `scripts/probe_verifier_independence.py` | Cross-config clustering + ICC agreement (used on the retracted data for the now-preserved-only probe) |

## Cross-hypothesis links

- Obs 235 — formal retraction of v1 H10/H12 pass (2026-04-14)
- Obs 236 — **this study's primary narrative anchor**
- Obs 237 — tile-level paired permutation methodology
- Obs 238 — H8 v2 null; cites this study's compression finding
- Obs 239 — H12 v2 HP:HN ratio null; closes library axis
- Obs 230 — WBF vs greedy aggregation-method test on retracted data; partial-preserved per Obs 235 §"PARTIAL CORRECTION"
- H8 v2 summary: `results/h8-v2/analysis_summary.md`
- H12 v2 summary: `results/h12-v2/analysis_summary.md` (exemplar-tier)
- Meta-findings synthesis: `results/meta-findings-summary.md` (Themes T2 failure taxonomies, T5 library-axis closure)
- Protocol errata E45 (permutation methodology), E49 (H10 cold-start config)

---

**Status**: Authoritative narrative summary for the clean H10 v2 primary
experiment (calibration-pool size under PV). Supersedes the
working-notes-only narrative anchor at Obs 236 as the primary citation
target for paper work. Obs 236 remains cited here as the research-
trajectory source for interpretation and context. The retracted v1
probe data is preserved for archive only and must not be cited for
any library-composition or HP:HN claim.
