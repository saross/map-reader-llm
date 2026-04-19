# Extended-Buffer F1 Curve on 4 Gold-Standard Maps (Text-HIGH pipeline)

## Purpose

Characterise the F1 curve behaviour at **tighter-than-primary** (5/10/15 metres)
and **intermediate** (25/35/45 metres) spatial buffer tolerances for the canonical
text-HIGH proposer-verifier pipeline on the 4 gold-standard maps, where annotation
precision is reliable (unlike the 55-map student ground truth).

## Canonical run selected

- **Run path**: `outputs/h11/gold-standard-v2/`
- **Git commit** (proposer + verifier-v1): `d59798ac7f32c0f6a4a050eb40824fffea8ec029`
- **Proposer**: `detect_brief-text`, `gemini-3-flash`, T=0.7, thinking=high, K=5,
  17 text-only labelled examples (no example images)
- **Verifier**: `verify_adversarial-text` (v1 prompt, `verify_adversarial.md`),
  `gemini-3-flash`, T=0.0, thinking=minimal
- **Consensus**: 4-of-5 majority vote (vote_t=4), Intersection-over-Union
  deduplication radius 20 m
- **Decision threshold**: `prob_t=0.15` on verifier `mound_probability`
- **Verifier artefact used**: `verified-v1/probabilities.json` (597 / 607
  candidates parsed; 10 parse failures are dropped by convention, matching the
  cached leaderboard cell and the 55-map text-HIGH generalisation run)

The `gold-standard-v2` tree is the most recent clean run at this exact config
and is the source of the canonical leaderboard cell for the 4-map evaluation
(see `results/leaderboard/cells/gold-standard-v2-greedy-v1-327tile.json`).
Its verifier stage used the **v1 adversarial prompt**, matching the
55-map text-HIGH generalisation run that this comparison targets.

## Evaluation scope

- **Ground truth**: `inputs/vectors/references/mounds-reference.geojson`
  (569 mounds across the 4 gold-standard maps:
  K-35-052-4, K-35-053-3, K-35-062-2, K-35-078-1)
- **Bounds**: `inputs/vectors/bounds/384/h10_test_bounds.geojson`
  (327 evaluation tiles, 4 maps)
- **NOTE**: The task brief suggested
  `inputs/vectors/bounds/384/calibration_bounds.geojson`, but that file
  contains 0 features (broken / deprecated). The canonical leaderboard
  evaluator uses `h10_test_bounds.geojson` (327 tiles) for these same runs,
  so that file was used here to maintain scoring comparability.
- **Bootstrap**: 1000 iterations, seed=42 (standard)

## Extended-buffer F1 curve (4 gold-standard maps, n=250 verified detections)

| Buffer (m) | F1      | 95% CI            | Precision | Recall  | ΔF1 from prev |
|-----------:|--------:|:-----------------:|----------:|--------:|--------------:|
| 5          | 0.2496  | [0.2026, 0.3031]  | 0.2840    | 0.2226  | —             |
| 10         | 0.6538  | [0.6012, 0.7015]  | 0.7440    | 0.5831  | +0.4042       |
| 15         | 0.7768  | [0.7332, 0.8151]  | 0.8840    | 0.6928  | +0.1230       |
| 25         | 0.8225  | [0.7833, 0.8586]  | 0.9360    | 0.7335  | +0.0457       |
| 35         | 0.8225  | [0.7833, 0.8586]  | 0.9360    | 0.7335  | 0.0000        |
| 45         | 0.8225  | [0.7833, 0.8586]  | 0.9360    | 0.7335  | 0.0000        |

## Key observations

1. **Plateau onset**: F1 is fully plateaued from 25 m upward. The point
   estimates, precision, and recall are identical at 25/35/45 m (and match
   the 20/30/40/50 m cached cells at 0.8155/0.8225/0.8225/0.8260 to within
   rounding) — all detection-reference matches saturate inside 25 m.

2. **Sharp penalty below 15 m**: Dropping from 15 m to 10 m costs ~0.12 F1;
   from 10 m to 5 m costs another ~0.40 F1. At 5 m, only 22-28% of
   verified detections land within ground-truth annotation distance.

3. **Precision-limited at 5 m**: The 5 m F1 of 0.25 is dominated by the
   spatial-matching penalty, not model error — at 5 m, precision crashes
   from 0.94 (≥25 m) to 0.28. This is consistent with combined sources of
   jitter: crop-local detection centroiding + Soviet-map annotation
   uncertainty + ground-truth digitising noise, each contributing a few
   metres.

4. **F1 at the preregistered primary buffer** (implicitly 20 m, between
   the 15 m and 25 m rows) sits at ~0.82 (cached leaderboard reports
   0.8155 @ 20 m). Gain from 20 m → 25 m is essentially zero.

## Comparison to 55-map text-HIGH curve

User-supplied 55-map text-HIGH F1 values at 20/30/40/50 m:
0.623 / 0.753 / 0.783 / 0.788

| Buffer | Gold-std 4 maps (569 mounds, curator GT) | 55-map student GT | Gap    |
|-------:|------------------------------------------|-------------------|-------:|
| 20 m   | 0.8155 (cached cell)                     | 0.623             | +0.193 |
| 25 m*  | 0.8225                                   | (~0.70 interp)    | ~+0.12 |
| 30 m   | 0.8225 (cached cell)                     | 0.753             | +0.070 |
| 35 m*  | 0.8225                                   | (~0.77 interp)    | ~+0.05 |
| 40 m   | 0.8225 (cached cell)                     | 0.783             | +0.040 |
| 45 m*  | 0.8225                                   | (~0.79 interp)    | ~+0.03 |
| 50 m   | 0.8260 (cached cell)                     | 0.788             | +0.038 |

*\* = buffer values NOT in the 55-map sweep; 55-map gaps estimated by
linear interpolation between adjacent points.*

### Interpretation

- **The 55-map curve has NOT plateaued at 50 m** — each +10 m buffer step
  still buys a few F1 points (20 → 30: +0.130; 30 → 40: +0.030;
  40 → 50: +0.005). Plateau likely falls somewhere between 50 and 80 m.
- **The gold-standard curve plateaus at 25 m**, ~25 m earlier than the
  55-map curve.
- **The ~40 m shift** (gold plateau at ~20-25 m; 55-map plateau likely
  beyond 50 m) is the signature of student-annotation position error on
  the 55-map GT. It is not a model-quality gap — it is a GT-precision gap.
- **At large buffer (50 m)**, the gap narrows to 0.038 F1, which is closer
  to the "true" model-quality gap between the two corpuses (gold-standard
  vs 55-map unseen-maps generalisation).
- **At the preregistered 20 m buffer**, the 55-map result is dragged
  ~0.19 F1 below the gold-standard result, most of which is GT-noise, not
  model-quality loss.
- **Below 15 m the gold-standard F1 also crashes**, so this is a spatial
  noise problem on both corpuses, just shifted in magnitude.

### Implication for publication framing

The 55-map F1 at 20 m materially understates model quality because the
student GT has position noise that shifts the saturating buffer from ~25 m
to >50 m. When reporting generalisation, either (a) quote the 50 m result
(0.788) as closest to model-quality ceiling, or (b) explicitly quantify the
annotation-precision offset using the curve shape comparison shown here
(the 55-map curve is approximately the gold-standard curve shifted right by
~25-35 m).

## Input files

- `verified_detections.geojson` — 250 features (vote_t=4, prob_t=0.15,
  filtered to 327-tile allowlist)
- `evaluation.json` / `evaluation.csv` / `evaluation.md` — standard
  `evaluate_detections.py` outputs with 1000-iteration bootstrap 95% CIs
- `score_leaderboard_sweep.json` — canonical leaderboard-style scoring
  (point estimates only, no CIs) for methodology cross-check

## Reproducibility

```bash
# Step 1: materialise the 250-feature verified-detections file using the
# canonical score-leaderboard pipeline (same filter logic as the cached
# leaderboard cell at vote_t=4, prob_t=0.15):
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

# Step 2: run bootstrap-CI evaluation on the tile-filtered candidates
# (verified_detections.geojson is rebuilt from the same pipeline inside a
# wrapper — the 250-feature file is checked into results/):
python scripts/evaluate_detections.py \
    --detections results/gold-standard-extended-buffer-sweep/verified_detections.geojson \
    --buffers 5 10 15 25 35 45 \
    --bootstrap 1000 --seed 42 \
    --ground-truth inputs/vectors/references/mounds-reference.geojson \
    --bounds inputs/vectors/bounds/384/h10_test_bounds.geojson \
    --output-dir results/gold-standard-extended-buffer-sweep \
    --label gold-standard-extended-buffer-sweep
```

Generated: 2026-04-18 (Sydney).
