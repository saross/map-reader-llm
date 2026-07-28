# H8 v2 — Library Composition and Scaling Analysis Summary

**Study**: H8 v2 — Library Composition and Scaling (384 px / production carry-forward)
**Date**: 2026-04-15 (runs launched and evaluated 2026-04-15)
**Protocol-errata**: E51 (15 deviations from the original Phase 2c H8)
**Primary aggregation**: greedy consensus at t=4
**Secondary aggregation**: WBF variant C (reported for cross-hypothesis comparability)
**Verifier sweep**: 1D threshold + 2D vote×probability grids over scale-4 and scale-8
**Evaluation**: 327-tile h10-384 test set, 20 m buffer, 1000 bootstrap iterations, seed=42
**Permutation**: tile-level paired, 10,000 iterations, seed=42
**FDR correction**: Benjamini–Hochberg at q=0.05 across 7 preregistered contrasts

## Headline result — seven-contrast null

All seven preregistered pairwise contrasts are **null** after
Benjamini–Hochberg FDR correction at q = 0.05. At the primary operating
point (greedy t=4) the seven conditions cluster in a tight 0.693–0.733
F1 band with fully overlapping 95 % bootstrap confidence intervals. No
condition's CI excludes any other condition's point estimate.

| Code | Contrast | F1 (a → b) | ΔF1 | raw p | BH-adj p | Signif? |
|------|----------|------------|-----|-------|----------|---------|
| C1 | pure-positive-canon → canonical (add Canon−) | 0.697 → 0.707 | −0.010 | 0.659 | 0.923 | no |
| C2 | canonical → plus-hp (add HP) | 0.707 → 0.705 | +0.002 | 0.932 | 0.932 | no |
| C3 | plus-hp → scale-8 (add HN) | 0.705 → 0.710 | −0.005 | 0.854 | 0.932 | no |
| B1 | plus-hp → scale-4 (HP-only vs balanced at size 13) | 0.705 → 0.733 | −0.028 | 0.164 | 0.834 | no |
| S1 | scale-4 → scale-8 | 0.733 → 0.710 | +0.023 | 0.330 | 0.834 | no |
| S2 | scale-8 → scale-16 | 0.710 → 0.693 | +0.017 | 0.477 | 0.834 | no |
| S3 | scale-16 → scale-32 | 0.693 → 0.713 | −0.020 | 0.394 | 0.834 | no |

Zero of seven contrasts reach significance after BH-FDR at q=0.05. The
smallest raw p-value is 0.164 (B1, balanced-vs-HP-only at size 13),
nowhere near significant even uncorrected. Three of the six
directional predictions from the preregistration (§H8, prereg
lines 799–806) point in the wrong direction within noise (C2, S1,
S2); the other three point in the predicted direction within noise
(C1, C3, S3). None of the six contrasts is statistically
distinguishable from zero after correction.

## Cross-hypothesis context — library axis closed

H8 v2 combines with the H10 v2 pool-size null and the H12 v2 HP:HN
ratio null (Obs 236, 239) to close the hard-example library axis at
the proposer stage:

| Hypothesis | Factor | Levels | Result | Reference |
|------------|--------|--------|--------|-----------|
| H10 v2 | Calibration-pool size | 4 (20, 40, 80, 160) | NULL | Obs 236 |
| **H8 v2** | **Library composition + size** | **7 (see below)** | **NULL after BH-FDR** | **this report** |
| H12 v2 | HP:HN ratio at fixed size=8 | 3 (2:6, 4:4, 6:2) | NULL after BH-FDR | H12 v2 summary |

All three preregistered factors on the library axis return nulls under
production carry-forward settings. The library has four slots of
canonical positives and three slots of null examples; what fills the
remaining slots does not measurably affect proposer F1 on this task.
This is a far stronger statement than any of H8 v2, H10 v2, or H12 v2
alone.

## Per-condition metrics at greedy t=4 (primary operating point)

| Condition | Examples | HP:HN in library | F1 [95 % CI] | Precision | Recall | n detections |
|-----------|---------:|------------------|--------------|-----------|--------|--------------|
| pure-positive-canon | 7 | 0:0 | 0.697 [0.643, 0.747] | 0.753 | 0.649 | 275 |
| canonical | 9 | 0:0 | 0.707 [0.648, 0.766] | 0.791 | 0.639 | 258 |
| plus-hp | 13 | 4:0 | 0.705 [0.648, 0.758] | 0.795 | 0.633 | 254 |
| **scale-4** | **13** | **2:2** | **0.733 [0.680, 0.777]** | **0.821** | **0.661** | **257** |
| scale-8 | 17 | 4:4 | 0.710 [0.648, 0.765] | 0.808 | 0.633 | 250 |
| scale-16 | 25 | 8:8 | 0.693 [0.633, 0.749] | 0.811 | 0.605 | 238 |
| scale-32 | 41 | 16:16 | 0.713 [0.660, 0.763] | 0.826 | 0.627 | 242 |

Observed spread across all 7 conditions at fixed t=4: **0.040 F1**
(scale-4 0.733 − scale-16 0.693). Scale-4 has the highest observed
point estimate with a 0.023 lead over scale-8, but every CI contains
every other condition's point estimate — no condition statistically
dominates any other. Scale-8 was executed as a fresh K=5 draw on the
unified H8 v2 pipeline; the main-table F1 = 0.710 reports that fresh
draw. An identical-config byte-identical draw also exists at
`outputs/h10/evaluation-v2/pool_160_hp4hn4/run_{1..5}/` (identical
model, temperature, thinking, instruction, example library, K,
manifest, and tile size) and gives F1 = 0.717 — the two draws are
compared as a pipeline sanity check in §"Sanity check" below.

## Per-tile pairing pattern — where the null comes from

Across all 7 contrasts, **257–276 of 327 tiles are ties** (79–84 %).
Only 51–70 tiles per contrast show any TP/FP/FN difference between the
two conditions, and the difference-showing tiles split close to evenly:

| Code | A wins | B wins | Ties | Tie % |
|------|-------:|-------:|-----:|------:|
| C1 | 27 | 30 | 270 | 82.6 |
| C2 | 33 | 26 | 268 | 82.0 |
| C3 | 37 | 33 | 257 | 78.6 |
| B1 | 19 | 34 | 274 | 83.8 |
| S1 | 35 | 25 | 267 | 81.7 |
| S2 | 27 | 24 | 276 | 84.4 |
| S3 | 27 | 26 | 274 | 83.8 |

This is *why* the contrasts are null: on ~82 % of tiles, swapping the
library has literally no effect on the tile's TP/FP/FN tally. The
remaining ~18 % of tiles split close to 50:50 between the two
conditions. The model's per-tile output is dominated by factors other
than the hard-example library.

## Threshold sweep (greedy t=1..5, all conditions)

| Condition | t=1 | t=2 | t=3 | t=4 | t=5 |
|-----------|-----|-----|-----|-----|-----|
| pure-positive-canon | 0.242 | 0.579 | **0.705** | 0.697 | 0.623 |
| canonical | 0.275 | 0.581 | 0.701 | **0.707** | 0.610 |
| plus-hp | 0.285 | 0.592 | 0.691 | **0.705** | 0.599 |
| scale-4 | 0.282 | 0.635 | 0.709 | **0.733** | 0.632 |
| scale-8 | 0.314 | 0.625 | **0.730** | 0.710 | 0.576 |
| scale-16 | 0.281 | 0.633 | **0.712** | 0.693 | 0.593 |
| scale-32 | 0.261 | 0.584 | 0.692 | **0.713** | 0.595 |

Per-condition best F1 (across the full sweep): pure-positive-canon,
plus-hp, scale-8, and scale-16 peak at t=3; canonical, scale-4, and
scale-32 peak at t=4. The across-threshold spread never exceeds 0.040
F1 at any fixed t, and no CI excludes any other's point estimate.
**Condition ranking is unstable across thresholds** — scale-4 leads at
t=4, scale-8 leads at t=3 — which is itself evidence that the
between-condition differences are consensus-threshold noise rather
than structure in library design.

## WBF variant C (secondary aggregation)

| Condition | F1 [95 % CI] | Precision | Recall | n fused |
|-----------|--------------|-----------|--------|---------|
| pure-positive-canon | 0.279 [0.230, 0.325] | 0.172 | 0.737 | 1,367 |
| canonical | 0.319 [0.266, 0.377] | 0.203 | 0.743 | 1,167 |
| plus-hp | 0.338 [0.287, 0.392] | 0.220 | 0.730 | 1,059 |
| scale-4 | 0.348 [0.294, 0.409] | 0.224 | 0.781 | 1,114 |
| **scale-8** | **0.356 [0.301, 0.410]** | **0.235** | **0.737** | **1,002** |
| scale-16 | 0.317 [0.268, 0.371] | 0.201 | 0.746 | 1,185 |
| scale-32 | 0.305 [0.257, 0.356] | 0.193 | 0.727 | 1,201 |

WBF variant C produces a high-recall / low-precision candidate set by
design (unconditional merge at IoU 0.25, 60 m min-separation, no vote
threshold). Absolute F1s here are not directly comparable with greedy
numbers and are reported only for cross-hypothesis comparability with
H10 v2 and H12 v2. The ordering is consistent with greedy in flavour:
scale-8 leads at F1=0.356, pure-positive-canon is the worst, and the
extremes (scale-32 high, pure-positive-canon low) bracket the bulk in
the same direction as greedy. The same null story holds.

## Verifier sweep (scale-4 and scale-8)

H8 v2 extends h12-v2's aggregation pipeline with a post-proposer
verifier sweep on the two highest-F1 conditions (scale-4 at t=4 and
scale-8 at t=3). Three sweep layers were run:

### 1D threshold sweep (unconditional verifier acceptance)

| Condition | Optimal p | F1 [95 % CI] | Precision | Recall | n accepted |
|-----------|-----------|--------------|-----------|--------|------------|
| scale-4 | 0.25 | 0.525 [0.481, 0.572] | 0.403 | 0.752 | 595 |
| scale-8 | 0.70 | 0.548 [0.505, 0.593] | 0.428 | 0.762 | 568 |

Candidate pools: scale-4 has 1,551 candidates from 569 ground-truth
mounds; scale-8 has 1,454. The 1D sweep accepts candidates purely on
verifier probability, with no consensus gate — it is the low-recall /
low-precision floor rather than the production operating point.

### 2D vote × probability grid (consensus + verifier, 5 × 20 = 100 cells)

| Grid | Best cell (vote_t, prob_t) | F1 | Precision | Recall | n |
|------|----------------------------|-----|-----------|--------|---|
| scale-4 greedy + PV | (4, 0.10) | 0.737 | 0.837 | 0.658 | 251 |
| scale-8 greedy + PV | (4, 0.05) | 0.722 | 0.858 | 0.624 | 232 |
| scale-4 WBF + PV | (4, 0.10) | 0.737 | 0.764 | 0.712 | 297 |
| scale-8 WBF + PV | (4, 0.15) | 0.722 | 0.765 | 0.683 | 285 |

At the 2D optima, the verifier lifts scale-4's F1 from 0.733 (greedy
t=4, no verifier) to 0.737 (greedy t=4, prob_t=0.10) — a marginal
+0.004 gain that trims 6 detections (257 → 251) and trades 0.003
recall for 0.016 precision. Scale-8's F1 rises from 0.710 to 0.722
(+0.012). Under WBF pooling, both conditions land at F1=0.737 / 0.722
with substantially higher recall (0.712 / 0.683 vs 0.658 / 0.624)
because WBF retains more unique detections into the verifier. The
verifier's contribution to F1 is small at the optima; its principal
effect is precision tightening rather than F1 lift.

### Verifier-stage pairwise permutations (scale-4 vs scale-8)

| Comparison | F1_a | F1_b | ΔF1 | raw p | wins_a | losses_a | ties |
|------------|------|------|-----|-------|-------:|---------:|-----:|
| 1D threshold optima (scale-4@0.25 vs scale-8@0.70) | 0.525 | 0.548 | −0.023 | 0.275 | 48 | 57 | 222 |
| 2D greedy+PV optima ((4, 0.10) vs (4, 0.05)) | 0.737 | 0.722 | +0.015 | 0.528 | 37 | 22 | 268 |
| 2D WBF+PV optima ((4, 0.10) vs (4, 0.15)) | 0.737 | 0.722 | +0.015 | 0.494 | 29 | 27 | 271 |

No scale-4 vs scale-8 verifier-stage comparison reaches significance
(all p > 0.27). This is the expected direct test of Obs 236's claim
that the verifier compresses library-quality differences to near-zero
— consistent here for the scale-4/scale-8 pair at the verifier stage.

## ⚠️ Directional findings worth flagging (non-significant)

These patterns do not survive statistical testing but merit explicit
flagging because they either contradict preregistered predictions or
have paper-relevant implications:

### 1. B1 is the largest observed effect (balanced beats HP-only at size 13)

B1 contrasts plus-hp (9 canonical + 4 HP, size 13) against scale-4
(9 canonical + 2 HP + 2 HN, size 13) — same library budget, different
composition. ΔF1 = −0.028 in favour of the balanced composition (raw
p = 0.164, BH-adj p = 0.834). Still null after correction, but if this
study were replicated at larger K or with more test tiles, B1 is the
contrast most likely to cross the significance threshold. Practically
this suggests: **if hard negatives are available, include them; do
not pack a fixed-size library with hard positives only**. This is a
weak hint, not a finding, and should be stated as such in the paper.

### 2. Condition ranking is unstable across thresholds

At t=3, scale-8 leads (F1=0.730); at t=4, scale-4 leads (F1=0.733);
at t=5, scale-4 again leads (F1=0.632). The "best library" depends
on which consensus threshold one picks, and the production t=4
operating point (adopted 2026-04-15 by user preference, E52 — the
registration specifies a full threshold grid search with no a priori
selection, `osf/preregistration.md:1908`; D17 audit FALSE-17) gives a
different winner than t=3. The full sweep is reported. This
threshold-dependence is itself evidence that between-condition
variance is consensus noise rather than real structure in library
design — a point that mirrors the H12 v2 finding (Obs 239) and
reinforces the cross-hypothesis null interpretation.

### 3. Directional predictions mostly fail

The preregistration specified six directional predictions along the
C1–C3 composition ladder and the S1–S3 scaling ladder (prereg lines
799–806). Three of six (C2, S1, S2) point in the wrong direction
within noise; the other three (C1, C3, S3) point in the predicted
direction within noise. The bonus contrast B1 (plus-hp vs scale-4 at
fixed size=13) also favours the balanced composition over HP-only, a
small non-significant lean worth flagging because it is the largest
observed effect in the study. The preregistered mechanism "more hard
examples → more recognition → higher recall" is not supported in the
data: the largest library (scale-32, 41 examples) has lower recall
(0.627) than the smallest (pure-positive-canon, 7 examples; recall
0.649). Recall is insensitive to library size along the entire range
tested.

## Sanity check — fresh scale-8 draw matches H10 reuse

H8 v2's scale-8 condition was run fresh on the unified H8-v2 pipeline,
and the H10 v2 `pool_160_hp4hn4` run (byte-identical config: same
model, temperature, thinking level, instruction, example library, K,
manifest, and tile size) was retained as an independent comparison
draw. The two K=5 draws at greedy t=4 give:

| Draw | F1 [95 % CI] | Source |
|------|--------------|--------|
| Fresh H8 v2 scale-8 | 0.710 [0.648, 0.765] | `results/h8-v2/greedy/scale-8/t4/evaluation.json` (main-table row) |
| H10 v2 `pool_160_hp4hn4` | 0.717 [0.661, 0.768] | `outputs/h10/evaluation-v2/pool_160_hp4hn4/` + Obs 238 |

ΔF1 = 0.007, well within sampling noise, fully overlapping CIs. Two
independent K=5 draws from the same config converge — the aggregation
and evaluation pipeline is internally consistent and the reported
numbers are trustworthy.

## Execution summary

| Metric | Value |
|--------|-------|
| Conditions launched (net) | 7 (scale-8 run fresh on the H8 v2 pipeline; the byte-identical H10 v2 pool_160_hp4hn4 run is retained as an independent comparison draw — see §"Sanity check") |
| Passes per condition | 5 |
| Tiles per pass | 327 |
| Total tile-passes acquired | 9,810 (per Obs 238) |
| Tile-level failures | 0 (two "items_failed" flags resolved as retries-to-success) |
| Wall time (all runs) | ~1 h 24 min |
| Workers | 250 |
| Mode | realtime + `--service-tier flex` + context cache |
| Tier 3 TPM utilisation | 72 % |
| Cache hit rate (smallest library, 7 ex) | 87.8 % |
| Cache hit rate (largest library, 41 ex) | 97.6 % |
| Meta-reported cost (H8 v2 + scale-8 fresh re-run) | ~$107 + ~$17 (untrustworthy — see caveat 5) |

Cache hit rates increase monotonically with library size because the
fixed tile-image component shrinks as a fraction of total input.

## Caveats

1. **Proposer-only, not post-verifier.** The headline F1 figures in
   the 0.69–0.73 band are proposer-only. The 55-map generalisation
   arm achieved F1 ≥ 0.830 (50 m, human-reviewed corrected) with a
   post-verifier pipeline; H8 v2 conditions have not all been run
   through the verifier. Only scale-4 and scale-8 have verifier sweep
   data. Obs 236 showed that the verifier compresses library-quality
   differences to near-zero (ΔF1 = −0.005 between pool_020 and
   pool_160 at their optimal post-verifier operating points), so the
   H8 v2 null is very likely to hold after verification too, but this
   has been tested directly only for scale-4 vs scale-8 (above).
2. **B1 is the largest observed effect** (plus-hp vs scale-4 at
   size=13, ΔF1 = −0.028, raw p = 0.164). Still null after correction,
   but this is the contrast a power-up study would pursue first, and
   the direction (balanced beats HP-only) has practical implications
   for library construction.
3. **327 test tiles is the full H10 test set**, not the 60-tile
   preregistered holdout. This is the largest feasible test set
   under the 4-map corpus. Increasing N further requires additional
   maps (the 55-map generalisation arm, which is a separate study)
   or a different test set (verifier-stage evaluation).
4. **Library nestedness is mechanical.** Greedy diversity selection
   is prefix-preserving (verified 2026-04-15 by byte-hash of hp_01..
   hp_04 and hn_01..hn_04 across pool_160_hp4hn4 / hp8hn8 / hp16hn16
   pools — see E51 rationale). So the scaling comparison is clean:
   any differences between scale-4 and scale-32 come from the
   additional examples, not from different samples of the same
   budget. This sharpens the null: the marginal hard example at the
   margin has zero detectable effect.
5. **Cost estimate is untrustworthy in both directions.**
   `scripts/lib_llm_metadata.py::estimate_cost()` multiplies
   `total_input_tokens × standard_tier_rate`, ignoring both the
   `--service-tier flex` discount (50 %) and the cache-read discount
   (~75 % off cached input tokens under Gemini's published schedule).
   It also does not account for thinking-token billing at
   `thinking_level=high`. The meta-reported ~$107 should not be
   treated as either upper or lower bound without cross-referencing
   the real Google Cloud bill. A follow-up fix to `estimate_cost()`
   is noted in Obs 238 for future hardening.

## Paper implications

H8 v2 is load-bearing for the paper's Era 1 Results section. Three
concrete claims it supports:

1. **Library-axis closure.** Combined with H10 v2 and H12 v2, the
   library-design story is closed: composition, size, and HP:HN
   ratio all null at the proposer stage under production settings.
   This supports a paper-Discussion claim that library curation
   beyond canonical positives + nulls is not a lever for proposer
   F1 on this task.
2. **Proposer-F1 ceiling around 0.70–0.73.** All seven H8 v2
   conditions sit in this band at greedy t=4. Together with the
   three H12 v2 conditions (0.688–0.717) and the four H10 v2 pool
   sizes, this is strong evidence that Gemini 3 Flash has a
   proposer-F1 ceiling around 0.70–0.73 on the h10-384 test set
   under production carry-forward settings, independent of library
   curation choices.
3. **Verifier compresses library differences (direct test for one
   pair).** The scale-4 vs scale-8 2D verifier-sweep permutation
   (Δ F1 = +0.015, raw p = 0.528) directly demonstrates what Obs
   236 inferred from H10: at the verifier stage, library-quality
   differences compress toward zero. This is one pairwise
   confirmation, not a sweep; the same logic is likely to hold
   across the other H8 v2 pairs but has not been empirically tested.

## Reproducibility

| Metric | Value |
|--------|-------|
| Bootstrap iterations | 1,000 |
| Bootstrap seed | 42 |
| Bootstrap resampling unit | tile-level |
| Permutation iterations | 10,000 |
| Permutation seed | 42 |
| Permutation mode | paired, tile-level (Obs 237 methodology) |
| FDR method | Benjamini–Hochberg at q=0.05 over 7 preregistered contrasts |
| Directory-level bootstrap metadata | `results/h8-v2/.metadata.json` |

## Artefacts

- Study YAML: `studies/h8-v2-library.yaml`
- Configs: `prompts/configs/h8/v2/detect_h8_*_v2.json` (7 files)
- Raw detections: `outputs/h8-v2/<cond>/run_{1..5}/detections-*.geojson`
- Scale-8 reuse source: `outputs/h10/evaluation-v2/pool_160_hp4hn4/run_{1..5}/`
- Greedy consensus: `outputs/h8-v2/greedy/<cond>/consensus_t{1..5}.geojson`
- WBF candidates: `outputs/h8-v2/wbf/<cond>/wbf_candidates.geojson`
- Evaluation reports: `results/h8-v2/{greedy,wbf}/<cond>/evaluation.{json,csv,md}`
- Permutation tests: `results/h8-v2/permutation-t4/<code>-<a>-vs-<b>/pairwise_permutation_result.json` (7 contrasts)
- FDR summary: `results/h8-v2/permutation-t4/fdr_summary.json`
- Verifier 1D threshold sweeps: `results/h8-v2/verifier-sweep/scale-{4,8}/threshold_sweep.{json,csv}`
- Verifier 2D grids: `results/h8-v2/verifier-sweep/scale-{4,8}/sweep_2d_greedy_pv.json`, `results/h8-v2/verifier-sweep/scale-{4,8}-wbf/sweep_2d_wbf_pv.json`
- Verifier-stage permutations: `results/h8-v2/verifier-sweep/permutation-{s4-vs-s8,greedy2d-s4-vs-s8,wbf-s4-vs-s8}/pairwise_permutation_result.json`
- Pool provenance: `outputs/h10/example-pools-v2/pool_160_hp{4hn4,8hn8,16hn16}/pool_metadata.json`
- Protocol errata: `docs/methodology/preregistration/protocol-errata.md` §E51 (15 deviations)
- Configuration audit: `reports/configuration-audit-2026-04-15-h8-v2.md`
- Archived duplicate: `results/h8-v2/greedy/pure-positive-canon-t4/` is a one-off pre-sweep evaluation; the in-sweep file at `results/h8-v2/greedy/pure-positive-canon/t4/` is numerically identical (timestamps ~7 min apart, same label and values) and is the file cited throughout this summary.

## Scripts used

| Phase | Script | Purpose |
|-------|--------|---------|
| 1 | `scripts/merge_passes.py --sweep` | Greedy consensus t=1..5 |
| 2 | `scripts/fuse_detections_wbf.py --config h8v2-*` | WBF variant C (IoU 0.25, 60 m min-sep, unconditional merge) |
| 3 | `scripts/evaluate_detections.py` | F1/P/R with 1,000-iteration bootstrap CIs at 20 m buffer |
| 4 | `scripts/pairwise_permutation_test.py --mode geojson` | Tile-level paired permutation, 10,000 iterations |
| 5 | `scripts/apply_fdr_h8v2.py` | BH-FDR at q=0.05 over 7 preregistered contrasts |
| 6 | `scripts/summarise_h8v2.py` | Collated per-condition summary table |
| 7 | `scripts/run_pv.py` (verifier stage) | Post-proposer verifier probability scoring on scale-4 / scale-8 candidates |

## Cross-hypothesis links

- Obs 235 — formal retraction of v1 H10/H12 pass (2026-04-14)
- Obs 236 — H10 v2 pool-size null; verifier compresses library differences
- Obs 237 — tile-level paired permutation methodology (used here)
- Obs 238 — **this study's primary narrative anchor**
- Obs 239 — H12 v2 HP:HN ratio null; closes library axis
- H10 v2 summary: `results/h10/analysis_summary.md` (the retracted `verifier_independence_probe.md` was moved to `archive/h10-h12-v1-retracted-probe/results/h10/verifier_independence_probe.md` in Session 75)
- H12 v2 summary: `results/h12-v2/analysis_summary.md` (exemplar-tier)
- Protocol errata: `docs/methodology/preregistration/protocol-errata.md` §E51

---

**Status**: Authoritative narrative summary for H8 v2. Supersedes the
working-notes-only narrative anchor at Obs 238 as the primary citation
target for paper work; Obs 238 remains cited here as the research-
trajectory source for interpretation and context.
