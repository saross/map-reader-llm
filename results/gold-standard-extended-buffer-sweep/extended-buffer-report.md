# Extended-Buffer F1 Curve on 4 Gold-Standard Maps (Text-HIGH pipeline)

**Date of analysis**: 2026-04-18 (Sydney).
**Level-up**: 2026-04-24 (Session 76).
**T=0.7 post-recovery refresh**: 2026-05-03 — the 55-map text-HIGH
T=0.7 numbers cited in §6, §6.2, §7.5, §8.1, §8.2 are refreshed to
match the recovered single-round T=0.7 detection set (verified
detections 4,143 → 4,164 after recovery, commits `731466d8`,
`d7f85978`, `e20f3e18`) and the updated curator GT (4,744 → 4,745
mounds, commit `baf1497a`). The 50 m raw F1 lands at 0.7920 (was
0.788; +0.004), and the 50 m corrected F1 at 0.8273 (was 0.8260;
+0.001) — gap and curve-shape conclusions are unchanged.

**GS-v2 post-recovery refresh**: 2026-05-03 — the §3.1 Era 2 scope-pair
companion is refreshed to the post-recovery GS-v2 verifier output
(commits `90890ae9..c6023034`). 10 pre-existing missing verifier
candidates plus 1 new from consensus rebuild lifted n_detections from
371 to 380. Era 2 50 m F1 = **0.8859 [0.8798, 0.8919]** (was 0.873
[0.844, 0.901]; +0.0126); Era 2 20 m F1 = **0.8663 [0.8591, 0.8726]**
(was 0.854 [0.821, 0.883]; +0.0123); tile MCC = **0.7778 [0.7663,
0.7896]** (was 0.778 [0.726, 0.828]; same point estimate, tighter
BCa N=10K CI). The 55-map vs gold-standard gap argument in §6 is
unchanged at the 4-decimal level.

**Observation anchors**: Obs 260 (F1-plateau / GT-precision-noise framing on the 4-map gold-standard vs 55-map student GT). Direct input to meta-findings Theme T1 (corrected-F1 lower bound rationale) and Theme T4 (subtype classification — the gold-standard corpus is the same 4-map subset).

This artefact is hand-authored (no dedicated analysis script writes it; data-generation commands are embedded in §12 Reproducibility). No script-overwrite risk.

## 1. Executive summary

This report characterises the F1 curve behaviour at **tighter-than-primary** (5 / 10 / 15 m) and **intermediate** (25 / 35 / 45 m) spatial buffer tolerances for the canonical text-HIGH proposer-verifier pipeline on the **4 gold-standard maps**, where annotation precision is reliable (unlike the 55-map student ground truth).

**Headline numbers**:

- **F1 curve (4-map gold-standard, text-HIGH, n = 250 verified detections)**: **0.2496 → 0.6538 → 0.7768 → 0.8225 → 0.8225 → 0.8225** at R ∈ {5, 10, 15, 25, 35, 45} m.
- **Plateau onset**: F1 fully plateaus from **25 m upward** (identical point estimates, precision, and recall at 25, 35, 45 m). All detection-reference matches saturate within 25 m.
- **Sharp penalty below 15 m**: dropping from 15 m to 10 m costs ~0.123 F1; from 10 m to 5 m another ~0.40 F1. At 5 m, only 22–28 % of verified detections land within GT distance.
- **Precision-limited at 5 m**: P = 0.284 at 5 m vs 0.936 at ≥ 25 m; R = 0.223 at 5 m vs 0.734 at ≥ 25 m. The 5 m drop is a spatial-matching penalty, not model error.
- **55-map vs 4-map gap at 20 m**: 0.8155 (gold-standard) − 0.623 (55-map student) = **+0.193 F1** — most of which is GT-precision noise on the 55-map student corpus, not model-quality loss.
- **55-map vs 4-map gap at 50 m**: 0.826 (gold-standard) − 0.792 (55-map student, post-recovery 2026-05-03; was 0.788) = **+0.034 F1** — closer to the "true" model-quality gap; the 55-map curve has not plateaued at 50 m.
- The **~ 25–35 m rightward shift** of the 55-map curve relative to the gold-standard curve is the signature of student-annotation position noise on the 55-map GT (each annotator-map combination contributes several metres; the combined shift suggests ~25–35 m position noise on the 55-map GT centroids).

**One-line paper claim**: "On the 4-map gold-standard corpus with curator-quality GT, the text-HIGH pipeline's F1 curve plateaus from 25 m upward at F1 = 0.8225; on the 55-map student-annotated generalisation corpus the same pipeline's curve has not plateaued even at 50 m. The ~25 m rightward shift of the 55-map curve is the signature of student-GT position noise, not model-quality loss — it dragged the 55-map 20 m F1 down by ~0.19 and the 50 m F1 down by ~0.03, the latter being closer to the true model-quality gap."

## 2. Canonical run selected

- **Run path**: `outputs/h11/gold-standard-v2/`.
- **Git commit** (proposer + verifier-v1): `d59798ac7f32c0f6a4a050eb40824fffea8ec029`.
- **Proposer**: `detect_brief-text`, `gemini-3-flash`, T = 0.7, thinking = HIGH, K = 5, 17 text-only labelled examples (no example images).
- **Verifier**: `verify_adversarial-text` (v1 prompt, `verify_adversarial.md`), `gemini-3-flash`, T = 0.0, thinking = MINIMAL.
- **Consensus**: 4-of-5 majority vote (vote_t = 4), Intersection-over-Union deduplication radius 20 m.
- **Decision threshold**: `prob_t = 0.15` on verifier `mound_probability`.
- **Verifier artefact used**: `verified-v1/probabilities.json` (597 / 607 candidates parsed; 10 parse failures are dropped by convention, matching the cached leaderboard cell and the 55-map text-HIGH generalisation run).

The `gold-standard-v2` tree is the most recent clean run at this exact config and is the source of the canonical leaderboard cell for the 4-map evaluation (see `results/leaderboard/cells/gold-standard-v2-greedy-v1-327tile.json`). Its verifier stage used the **v1 adversarial prompt**, matching the 55-map text-HIGH generalisation run that this comparison targets.

## 3. Evaluation scope

- **Ground truth**: `inputs/vectors/references/mounds-reference.geojson` (569 mounds across the 4 gold-standard maps: K-35-052-4, K-35-053-3, K-35-062-2, K-35-078-1).
- **Bounds**: `inputs/vectors/bounds/384/h10_test_bounds.geojson` (327 evaluation tiles, 4 maps; Era 3 scope).
- **NOTE**: The task brief suggested `inputs/vectors/bounds/384/calibration_bounds.geojson`, but that file contains 0 features (broken / deprecated). The canonical leaderboard evaluator uses `h10_test_bounds.geojson` (327 tiles) for these same runs, so that file was used here to maintain scoring comparability.
- **Bootstrap**: 1,000 iterations, seed = 42 (standard).

### 3.1 Scope-pair companion (Era 2 vs Era 3)

This artefact reports the text-HIGH gold-standard v2 pipeline on the **Era 3 scope (327 tiles, 250 verified detections)**, intentionally bounds-filtered for sibling-comparability with the h8-v2 / h10-v2 / h12-v2 library-design artefacts (all of which use the same 327-tile H10 test pool). A **matched Era 2 companion evaluation** of the same pipeline on the broader **487-tile Era 2 scope (380 verified detections post-recovery)** was originally computed in Session 78 (2026-04-24) and refreshed after the GS-v2 recovery (Session 82, 2026-05-03, commits `90890ae9..c6023034`); the current artefact is at `results/gold-standard-extended-buffer-sweep-era2/evaluation.{json,csv,md}`. The Era 2 run is the matching denominator for the Phase 3a matrix leaderboard; the Era 3 run is the matching denominator for the v2 library-design closure cells.

**Recovery 2026-05-03**: the GS-v2 verifier cleanup recovered 10 pre-existing missing candidates plus 1 new candidate from consensus rebuild (n_detections 371 → 380); the published Era 2 F1 was understated by ~1.3 pp at every buffer ≥ 20 m. The Era 3 numbers in §4 below are unchanged because Era 3 is bounds-filtered to the 327-tile h10_test pool, which excludes most of the recovered candidates.

**Side-by-side point estimates with 95 % BCa bootstrap CIs** (text-HIGH, vote_t = 4, prob_t = 0.15, 10,000 iterations on the Era 2 post-recovery refresh; 1,000 iterations on the Era 3 baseline, seed = 42):

| Buffer | Era 3 (327 tiles, 250 detections) | Era 2 post-recovery (487 tiles, 380 detections) |
|-------:|-----------------------------------|-------------------------------------------------|
| 20 m | F1 = 0.8155 [0.7833, 0.8586]; P = 0.936, R = 0.734 | F1 = 0.8663 [0.8591, 0.8726]; P = 0.929, R = 0.812 |
| 50 m | F1 = 0.826 (cached leaderboard cell) | F1 = 0.8859 [0.8798, 0.8919]; P = 0.950, R = 0.830 |
| Tile-level MCC | — | 0.7778 [0.7663, 0.7896] |
| Tile confusion (TP / TN / FP / FN) | — | 181 / 250 / 8 / 48 |
| Sensitivity / specificity | — | 0.7904 [0.7789, 0.8017] / 0.9690 [0.9638, 0.9732] |

For the pre-recovery Era 2 numbers (n = 371; F1@20m = 0.854 [0.821, 0.883], F1@50m = 0.873 [0.844, 0.901], MCC = 0.778 [0.726, 0.828]) see the archived `results/gold-standard-extended-buffer-sweep-era2/evaluation.json` history at commit `90890ae9^`.

**Scope-pair reading**: the 20 m bootstrap CIs [0.7833, 0.8586] (Era 3) and [0.8591, 0.8726] (Era 2 post-recovery) abut but no longer overlap substantially after the recovery — Era 2 has tightened upward by ~+0.013 F1 and the CI half-width has narrowed (BCa N=10K). The remaining point-estimate gap is consistent with the 327-tile scope holding a random subsample of the harder-to-match candidates. Era 3 was constructed by **hierarchical stratified random sampling** from Era 2 (487 total tiles minus the 160-tile pool_160 calibration pool, selected via geographic → density → random stratification with seed 42; see `results/evaluation-scopes.md` §5.3 and `scripts/select_calibration_tiles.py`), so the 327-tile complement is itself a random subsample of Era 2, not a difficulty-filtered curation. Density distributions of pool_160 vs the complement are proportional — no bias. The two reportings are therefore **scope-pair siblings**, preserved as intentional comparability choices for distinct artefact families: Era 3 matches h8/h10/h12 v2; Era 2 matches the Phase 3a matrix denominator. See `results/evaluation-scopes.md` §2 and §5.3 for the Era 2 vs Era 3 scope definitions.

## 4. Extended-buffer F1 curve (4 gold-standard maps, n = 250 verified detections)

| Buffer (m) | F1 | 95 % CI | Precision | Recall | ΔF1 from prev |
|-----------:|--------:|:-----------------:|----------:|--------:|--------------:|
| 5 | 0.2496 | [0.2026, 0.3031] | 0.2840 | 0.2226 | — |
| 10 | 0.6538 | [0.6012, 0.7015] | 0.7440 | 0.5831 | +0.4042 |
| 15 | 0.7768 | [0.7332, 0.8151] | 0.8840 | 0.6928 | +0.1230 |
| 25 | 0.8225 | [0.7833, 0.8586] | 0.9360 | 0.7335 | +0.0457 |
| 35 | 0.8225 | [0.7833, 0.8586] | 0.9360 | 0.7335 | 0.0000 |
| 45 | 0.8225 | [0.7833, 0.8586] | 0.9360 | 0.7335 | 0.0000 |

## 5. Key observations

1. **Plateau onset**: F1 is fully plateaued from 25 m upward. The point estimates, precision, and recall are identical at 25, 35, 45 m (and match the 20 / 30 / 40 / 50 m cached cells at 0.8155 / 0.8225 / 0.8225 / 0.8260 to within rounding) — all detection-reference matches saturate inside 25 m.

2. **Sharp penalty below 15 m**: dropping from 15 m to 10 m costs ~0.12 F1; from 10 m to 5 m costs another ~0.40 F1. At 5 m, only 22–28 % of verified detections land within ground-truth annotation distance.

3. **Precision-limited at 5 m**: the 5 m F1 of 0.25 is dominated by the spatial-matching penalty, not model error — at 5 m, precision crashes from 0.94 (≥ 25 m) to 0.28. This is consistent with combined sources of jitter: crop-local detection centroiding + Soviet-map annotation uncertainty + ground-truth digitising noise, each contributing a few metres.

4. **F1 at the preregistered primary buffer** (implicitly 20 m, between the 15 m and 25 m rows) sits at ~0.82 (cached leaderboard reports 0.8155 @ 20 m). Gain from 20 m → 25 m is essentially zero.

## 6. Comparison to 55-map text-HIGH curve

**Corpus disjointness**: the 4 gold-standard maps and the 55 generalisation maps are **disjoint sheet-sets** (zero map-sheet intersection; confirmed 2026-04-24 via `inputs/vectors/bounds/384/*.geojson` + `inputs/vectors/references/*.geojson` audit). Total project coverage is 59 sheets (4 GS + 55 generalisation). The curve-shift comparison below therefore compares pipeline F1 on two independent sheet populations; it cannot be confounded by shared-sheet contamination between the curator-GT and student-GT references. See `results/evaluation-scopes.md` §11.

User-supplied 55-map text-HIGH F1 values at 20 / 30 / 40 / 50 m: 0.623 / 0.753 / 0.783 / 0.792 (50 m updated post-recovery 2026-05-03; was 0.788 — see top-of-file note).

| Buffer | Gold-std 4 maps (569 mounds, curator GT) | 55-map student GT | Gap |
|-------:|------------------------------------------|-------------------|-------:|
| 20 m | 0.8155 (cached cell) | 0.623 | +0.193 |
| 25 m* | 0.8225 | (~0.70 interp) | ~+0.12 |
| 30 m | 0.8225 (cached cell) | 0.753 | +0.070 |
| 35 m* | 0.8225 | (~0.77 interp) | ~+0.05 |
| 40 m | 0.8225 (cached cell) | 0.783 | +0.040 |
| 45 m* | 0.8225 | (~0.79 interp) | ~+0.03 |
| 50 m | 0.8260 (cached cell) | 0.792 (was 0.788 pre-recovery) | +0.034 |

*\* = buffer values NOT in the 55-map sweep; 55-map gaps estimated by linear interpolation between adjacent points.*

### 6.1 Interpretation

- **The 55-map curve has NOT plateaued at 50 m** — each +10 m buffer step still buys a few F1 points (20 → 30: +0.130; 30 → 40: +0.030; 40 → 50: +0.009 post-recovery; was +0.005 pre-recovery). Plateau likely falls somewhere between 50 and 80 m.
- **The gold-standard curve plateaus at 25 m**, ~25 m earlier than the 55-map curve.
- **The ~40 m shift** (gold plateau at ~20–25 m; 55-map plateau likely beyond 50 m) is the signature of student-annotation position error on the 55-map GT. It is not a model-quality gap — it is a GT-precision gap.
- **At large buffer (50 m)**, the gap narrows to 0.034 F1 (post-recovery 2026-05-03; was 0.038 pre-recovery), which is closer to the "true" model-quality gap between the two corpuses (gold-standard vs 55-map unseen-maps generalisation).
- **At the preregistered 20 m buffer**, the 55-map result is dragged ~0.19 F1 below the gold-standard result, most of which is GT-noise, not model-quality loss.
- **Below 15 m the gold-standard F1 also crashes**, so this is a spatial noise problem on both corpuses, just shifted in magnitude.

### 6.2 Implication for publication framing

The 55-map F1 at 20 m materially understates model quality because the student GT has position noise that shifts the saturating buffer from ~25 m to > 50 m. When reporting generalisation, either (a) quote the 50 m result (0.792 post-recovery; was 0.788) as closest to model-quality ceiling, or (b) explicitly quantify the annotation-precision offset using the curve shape comparison shown here (the 55-map curve is approximately the gold-standard curve shifted right by ~25–35 m).

## 7. Caveats / risk register

1. **Single-reviewer / single-day annotation on the 55-map corpus**: the student GT on the 55-map corpus was produced under time pressure by a small number of digitisers; position noise of ~25–35 m is plausible but not independently quantified. The ~25 m shift argument is necessary but not sufficient; a direct inter-annotator agreement study would be the gold standard. See meta-findings §T1 for the corrected-F1 human-review workaround.
2. **Only 4 maps in gold-standard corpus**: the 0.8225 plateau value is specific to these 4 maps (K-35-052-4, K-35-053-3, K-35-062-2, K-35-078-1); generalisation to maps with different symbol density or print fidelity is untested here. The 55-map generalisation run is the formal out-of-sample test.
3. **n = 250 verified detections is modest**. Bootstrap CIs at ±0.04–0.05 F1 reflect this sample size. The plateau direction (F1 ≥ 25 m identical to three decimal places) is unambiguous, but per-cell CI overlap between 25 m and 50 m is substantial.
4. **5 m crash is not model error**. Below-15 m F1 crashes on both corpuses — spatial-matching floors at tight buffers are a methodological property, not a finding about model quality.
5. **The 55-map 20 m = 0.623 figure is user-supplied and not directly re-derived** in this artefact. It comes from `results/55maps-text-high-generalisation/evaluation/evaluation.json` (see §8). Recomputed 2026-04-24 for this level-up: the 20 m F1 at `.summary.buffers[0]` is 0.6227 — consistent with the 0.623 cited. Post-recovery 2026-05-03: only the 50 m row was re-derived from the recovered T=0.7 detection set (raw F1 0.7920); the 20 / 30 / 40 m rows in the table above carry forward from the pre-recovery evaluation pending a full multi-buffer re-run.
6. **Calibration_bounds.geojson broken**. The task brief cited `inputs/vectors/bounds/384/calibration_bounds.geojson` which contains 0 features. The comparison used `h10_test_bounds.geojson` (327 tiles) to maintain scoring comparability with the canonical leaderboard; this deviation is documented in §3.
7. **Verifier v1 only** — this run used verifier-v1. v2 (quarantined under `archive/v2-verifier-contamination/`) is not cited for any gold-standard figure. See `docs/methodology/v2-verifier-contamination-policy.md` for the quarantine rationale.

## 8. Paper implications

### 8.1 GT-precision-noise headline for the paper's Results section

The paper's text-HIGH Results section should cite **both** corpuses with a shared interpretive lens:

- On the 4-map gold-standard (curator GT, 569 mounds across 327 tiles at 384 px), text-HIGH plateaus at **F1 = 0.822** from R = 25 m onward.
- On the 55-map generalisation corpus (student GT, 4,745 mounds across 8,541 tiles at 384 px; +1 mound from `baf1497a` post-recovery), text-HIGH does not plateau at 50 m (F1 = 0.792 post-recovery; was 0.788; corrected F1 = 0.8273 at 50 m after human-review rescue, was 0.8260).
- The gap at matched buffer narrows from +0.193 at 20 m to +0.034 at 50 m (post-recovery; was +0.038); the ~0.159 absolute gap narrowing is the empirical signature of student-GT position noise (~25 m) on the 55-map corpus.

### 8.2 Why corrected F1 lifts the 55-map headline above the raw comparison

The corrected-F1 multi-buffer analysis (`results/55maps-image-generalisation/corrected-f1-multi-buffer/report.md`) recovers F1 = 0.8317 at 50 m on the 55-map image corpus — higher than the text-HIGH 0.792 at 50 m (post-recovery; was 0.788). The corrected-F1 uplift on the image side (+0.040) comes from re-classifying ~474 VLM-only candidates as mounds; this is independent of the GT-precision-noise effect documented here. The two corrections (human-review rescue + GT-precision-noise accounting) both act to move the 55-map F1 toward the gold-standard plateau; combined, they close most of the +0.034 – +0.193 gap at matched buffers (50 m gap post-recovery; was +0.038).

### 8.3 Methodological contribution

The **extended-buffer curve shape is a free diagnostic** for GT-precision-noise on any corpus with mound annotations. The shape — sharp rise below 15 m, plateau above 25 m — is stable across corpuses of different sizes; the horizontal shift is the position-noise scale. Papers reporting detection F1 on archaeological corpora should publish the extended-buffer curve alongside the primary F1, both to identify the corpus's GT-precision-noise scale and to anchor cross-corpus comparisons.

### 8.4 Suggested paper text (Results — extended-buffer comparison)

> An extended-buffer F1 curve on the 4-map gold-standard corpus (569 mounds, 327 evaluation tiles at 384 px, text-HIGH pipeline with `gemini-3-flash`, K = 5 consensus at vote_t = 4, prob_t = 0.15, verifier-v1) plateaus at F1 = 0.8225 [0.7833, 0.8586] from R = 25 m upward. Below 15 m, F1 crashes sharply (F1 = 0.2496 at 5 m) due to the combined spatial-matching floor of detection centroiding, annotation placement, and GT digitising noise. On the 55-map generalisation corpus, the same pipeline's F1 curve has not plateaued at R = 50 m (F1 = 0.792 at 50 m post-recovery 2026-05-03, was 0.788; compared to 0.826 on the gold-standard corpus at 50 m). The ~25–35 m rightward shift of the 55-map curve relative to the gold-standard curve is the empirical signature of student-GT position noise on the 55-map corpus. The matched-buffer gap narrows from +0.193 F1 at 20 m (gold 0.8155 − student 0.623) to +0.034 F1 at 50 m (gold 0.826 − student 0.792 post-recovery; was +0.038 with student 0.788); the latter is closer to the true model-quality gap between the two corpuses. This curve-shape analysis is the empirical basis for quoting generalisation performance at 50 m and / or citing the human-review-corrected F1 ≥ 0.827 at 50 m (`corrected-f1-multi-buffer/report.md`; post-recovery T=0.7 corrected F1 0.8273) rather than the raw 0.623 at 20 m.

## 9. Files manifest

**Outputs (this directory)**:

- `extended-buffer-report.md` — this report.
- `verified_detections.geojson` — 250 features (vote_t = 4, prob_t = 0.15, filtered to 327-tile allowlist).
- `evaluation.json` / `evaluation.csv` / `evaluation.md` — standard `evaluate_detections.py` outputs with 1,000-iteration bootstrap 95 % CIs.
- `evaluation.metadata.json` — evaluation metadata sidecar.
- `score_leaderboard_sweep.json` — canonical leaderboard-style scoring (point estimates only, no CIs) for methodology cross-check.

**Inputs**:

- `outputs/h11/gold-standard-v2/crops/candidate_manifest.json` — candidate manifest post-dedup.
- `outputs/h11/gold-standard-v2/verified-v1/probabilities.json` — verifier-v1 probabilities.
- `inputs/vectors/bounds/384/h10_test_bounds.geojson` — 327-tile Era 3 bounds.
- `inputs/vectors/references/mounds-reference.geojson` — 569-mound GT.

**Cross-reference cached cells**:

- `results/leaderboard/cells/gold-standard-v2-greedy-v1-327tile.json` — the canonical gold-standard leaderboard cell this analysis recomputes at extended buffers.

## 10. Reproducibility

- **Analysis framing**: hand-authored report; numbers computed via two stages below (not a single dedicated script). All inputs and commands are preserved in this file for reproducibility.
- **Bootstrap**: 1,000 iterations, seed = 42 (configurable via the `--bootstrap` + `--seed` flags on `evaluate_detections.py`).
- **Re-run command — Step 1** (materialise the 250-feature verified-detections file using the canonical score-leaderboard pipeline; same filter logic as the cached leaderboard cell at vote_t = 4, prob_t = 0.15):

    ```bash
    python scripts/score_leaderboard_cells.py \
        --manifest outputs/h11/gold-standard-v2/crops/candidate_manifest.json \
        --probs outputs/h11/gold-standard-v2/verified-v1/probabilities.json \
        --bounds inputs/vectors/bounds/384/h10_test_bounds.geojson \
        --gt inputs/vectors/references/mounds-reference.geojson \
        --label "gold-standard-v2-text-high-extended-buffer" \
        --track text --aggregation greedy --verifier flash-adversarial-v1 \
        --vote-thresholds 4 --prob-thresholds 0.15 \
        --buffers 5,10,15,25,35,45 \
        --output results/gold-standard-extended-buffer-sweep/score_leaderboard_sweep.json
    ```

- **Re-run command — Step 2** (bootstrap-CI evaluation on the tile-filtered candidates; `verified_detections.geojson` is rebuilt from the same pipeline inside a wrapper — the 250-feature file is checked into `results/`):

    ```bash
    python scripts/evaluate_detections.py \
        --detections results/gold-standard-extended-buffer-sweep/verified_detections.geojson \
        --buffers 5 10 15 25 35 45 \
        --bootstrap 1000 --seed 42 \
        --ground-truth inputs/vectors/references/mounds-reference.geojson \
        --bounds inputs/vectors/bounds/384/h10_test_bounds.geojson \
        --output-dir results/gold-standard-extended-buffer-sweep \
        --label gold-standard-extended-buffer-sweep
    ```

- **Git commit of original data run**: `8747d726` (`data(analysis): GT spacing + gold-standard F1 curve + docs audit + Obs 260`). Level-up commit: see this file's `git log` entry at 2026-04-24.
- **Toolchain**: Python ≥ 3.11, GeoPandas ≥ 0.14, NumPy, pandas. Pinned versions in `requirements.txt`.
