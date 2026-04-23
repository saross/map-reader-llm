# 55-map cross-track comparison: image × text-HIGH × text-MIN

**Created**: 2026-04-24 (Session 76).
**Scope**: 55 topographic map sheets at 384 px (Era 2 bounds; 8,541 evaluation tiles).
**Purpose**: Side-by-side comparison of the three 55-map generalisation tracks — image-proposer, text-HIGH (HIGH thinking), text-MIN (MINIMAL thinking) — at matched buffer tolerances, with explicit notes on what paired-permutation testing is and is not available.

**This is a synthesis doc** (new in Session 76; not a data-generation pipeline). Numbers are lifted from the three per-track `evaluation.json` files and three `paired-vs-min-<buffer>/pairwise_permutation_result.json` paired-test JSONs; no new statistical tests were run.

## 1. Executive summary

The three 55-map generalisation tracks share the same evaluation scope (8,541 tiles at 384 px, Era 2 bounds), the same proposer model family (`gemini-3-flash-preview`), the same verifier (`gemini-3-flash` MINIMAL), and the same pipeline infrastructure — **with one pipeline-control difference**: the image track uses consensus vote threshold `vote_t = 3` whereas text-HIGH and text-MIN use `vote_t = 4` (per `outputs/<track>/resolved_config.yaml`). This is a lower bar for consensus on the image track; a matched-`vote_t` cross-track comparison would require re-processing. See §8 Caveat 8 for impact. They also differ in proposer input modality (image vs text) and thinking setting (HIGH vs MINIMAL for the two text tracks).

**Headline F1 numbers**:

| Track | F1 @ 20 m | F1 @ 30 m | F1 @ 40 m | F1 @ 50 m | Corrected F1 @ 50 m |
|-------|----------:|----------:|----------:|----------:|---------------------:|
| **image** | 0.506 | 0.686 | 0.748 | 0.771 | **0.830** (paper headline) |
| **text-HIGH** | 0.623 | 0.753 | 0.783 | 0.788 | — (not human-reviewed) |
| **text-MIN** | 0.618 | 0.727 | 0.754 | 0.759 | — (not human-reviewed) |

**Key findings**:

- **Text beats image at raw F1 at every buffer ≤ 50 m**: text-HIGH at 50 m is 0.788 vs image at 0.771 (ΔF1 = +0.017 raw); at 20 m the gap is +0.117. The image-track's raw F1 handicap at tight buffers is substantial.
- **Image wins after human-review correction at 50 m**: corrected F1 for the image track is **≥ 0.830** at 50 m (per `corrected-f1-multi-buffer/report.md`); neither text track has been human-reviewed so their corrected F1 is unknown. The image-track's per-candidate review rescued **472 phantom-TPs** that the student GT missed (single-buffer calibrated-UI review; the multi-buffer re-review added 2 more at 50 m, lifting the multi-buffer artefact's count to 474).
- **Cost per track**: image $364.70, text-HIGH $69.60, text-MIN $60.79 (per `outputs/<track>/cost_manifest.json`; verified 2026-04-24). Image is 5.2× the cost of text-HIGH and 6.0× the cost of text-MIN. The image track's 91 % prompt-caching hit rate (621.3 M cached tokens of 785.7 M total) partly offsets its larger per-call cost.
- **Only text-HIGH vs text-MIN paired permutation tests exist** at 20 / 30 / 40 / 50 m. At 20 m the gap is not significant (ΔF1 = +0.0047, p = 0.4647); at 30 / 40 / 50 m text-HIGH is significantly better than text-MIN (p = 0.0 on 10,000 permutations, seed 42). **No paired image-vs-text tests** have been run on this corpus; cross-modality claims must rely on raw F1 differences without paired significance.
- **Track-specific precision-recall trade-offs**: at 50 m, text-HIGH is the most precise (0.848), text-MIN is a close second (0.849), image is the least precise (0.780). Recall is flipped: text-HIGH 0.737, text-MIN 0.687, image 0.763. Image trades precision for recall; text-MIN is the most parsimonious (highest precision, lowest recall).

**One-line paper claim**: "At raw F1 on the 55-map generalisation corpus (n = 8,541 Era 2 tiles; `gemini-3-flash-preview` proposer), text-HIGH is the top-performing track at every buffer ≤ 50 m (F1 = 0.788 at 50 m vs 0.759 text-MIN vs 0.771 image). After per-candidate human review, the image track's corrected F1 rises to ≥ 0.830 at 50 m, exceeding the text tracks' uncorrected F1; equivalent human review was not conducted for the text tracks, so corrected-F1 comparison across tracks is not available."

## 2. Run metadata (the three tracks are paired on scope, not on modality)

| Track | Proposer | Verifier | Thinking | K | vote_t | PV | Tile set | Map count |
|-------|----------|----------|----------|---|-------:|-----|---------|----------:|
| image | gemini-3-flash-preview | gemini-3-flash | HIGH | 5 | **3** | adversarial v1 | 8,541 @ 384 px Era 2 | 55 |
| text-HIGH | gemini-3-flash-preview | gemini-3-flash | HIGH | 5 | **4** | adversarial v1 | 8,541 @ 384 px Era 2 | 55 |
| text-MIN | gemini-3-flash-preview | gemini-3-flash | MINIMAL | 5 | **4** | adversarial v1 | 8,541 @ 384 px Era 2 | 55 |

Model note: `run.meta.json` `configuration.model` fields carry the `-preview` suffix for both proposer and verifier stages (the inner `full_config_snapshot.model` drops it as `gemini-3-flash`). The realised-run stack is `gemini-3-flash-preview` on both stages; the `-preview` vs stable distinction is noted here for transparency.

All three tracks:

- Use the same 55-map evaluation bounds (`inputs/vectors/bounds/384/55maps_evaluation_bounds.geojson`; 8,541 tiles at 384 px).
- Use the same consensus K = 5 and verifier probability threshold prob_t = 0.15.
- **Differ on consensus vote threshold**: image uses `vote_t = 3`; text-HIGH and text-MIN use `vote_t = 4` (per `outputs/<track>/resolved_config.yaml`). See §8 Caveat 8.
- Use the same Hungarian one-to-one spatial-matching protocol at each buffer tolerance.
- Use the same student GT (`inputs/vectors/references/student-mounds-55maps-reviewed.geojson`; 4,744 mounds across 55 maps).

**Controls that differ across the three tracks**:

- Input modality: image crops (image-track) vs structured text descriptions (text-HIGH, text-MIN).
- Proposer thinking level: HIGH (image + text-HIGH) vs MINIMAL (text-MIN).

The image vs text-HIGH comparison is confounded with modality (image vs text input). Text-HIGH vs text-MIN isolates the thinking-level effect within the text modality.

## 3. Per-track headline metrics (20 – 50 m buffers)

### 3.1 20 m buffer

| Track | F1 | Precision | Recall |
|-------|-------:|----------:|-------:|
| image | 0.5060 | 0.5117 | 0.5004 |
| **text-HIGH** | **0.623** | 0.670 | 0.582 |
| text-MIN | 0.618 | 0.691 | 0.559 |

text-HIGH leads by 0.117 raw F1 over image; text-HIGH vs text-MIN differ by +0.0047 (paired permutation p = 0.4647; not significant).

### 3.2 30 m buffer

| Track | F1 | Precision | Recall |
|-------|-------:|----------:|-------:|
| image | 0.686 | 0.693 | 0.678 |
| **text-HIGH** | **0.753** | 0.810 | 0.704 |
| text-MIN | 0.727 | 0.813 | 0.658 |

text-HIGH leads by 0.068 raw F1 over image; text-HIGH vs text-MIN ΔF1 = +0.0259 (p = 0.0, significant).

### 3.3 40 m buffer

| Track | F1 | Precision | Recall |
|-------|-------:|----------:|-------:|
| image | 0.748 | 0.757 | 0.740 |
| **text-HIGH** | **0.783** | 0.842 | 0.731 |
| text-MIN | 0.754 | 0.843 | 0.682 |

text-HIGH leads by 0.035 raw F1 over image; text-HIGH vs text-MIN ΔF1 = +0.0291 (p = 0.0, significant).

### 3.4 50 m buffer

| Track | F1 | Precision | Recall |
|-------|-------:|----------:|-------:|
| image | 0.771 | 0.780 | 0.763 |
| **text-HIGH** | **0.788** | 0.848 | 0.737 |
| text-MIN | 0.759 | 0.849 | 0.687 |

text-HIGH leads by 0.017 raw F1 over image; text-HIGH vs text-MIN ΔF1 = +0.0292 (p = 0.0, significant).

The text-HIGH − image gap narrows as buffer increases (0.117 → 0.068 → 0.035 → 0.017), consistent with the extended-buffer-report.md finding that image-proposer outputs have larger spatial-precision jitter than text-proposer outputs. At tight buffers the image track is penalised for spatial imprecision; at looser buffers the modality gap closes.

**No evaluations at 100 m buffer** exist for any of the three tracks in the per-track `evaluation.json` files; buffers sweep 20 / 30 / 40 / 50 m only. For image-track buffers > 50 m see `corrected-f1-multi-buffer/report.md` (R ∈ {50, 75, 100, 125, 150} m; corrected-F1 only).

## 4. Corrected-F1 availability

**Only the image track has been human-reviewed**:

| Track | Corrected F1 @ 50 m | Multi-buffer corrected F1 | n human-reviewed | Source |
|-------|--------------------:|:-------------------------:|-----------------:|--------|
| image | **0.830** [0.826, 0.833] | 0.832 → 0.855 @ 50 → 150 m | 1,028 candidates (calibrated UI, 50 m single-buffer) + same 1,028 re-reviewed multi-buffer with 74 sentinel additions | `corrected-f1-human-reviewed.md` + `corrected-f1-multi-buffer/report.md` |
| text-HIGH | — | — | 0 | — |
| text-MIN | — | — | 0 | — |

**This asymmetry is a major scope caveat for cross-track claims**. The image-track's headline corrected-F1 of ≥ 0.830 at 50 m exceeds the text tracks' uncorrected F1, but the comparison is not like-for-like: the text tracks would almost certainly have some phantom-TP rescue under equivalent human review — likely moving their corrected F1 toward 0.85 — 0.88 given their starting uncorrected F1 of 0.76 – 0.79 and a comparable FP pool to correct.

**Paper citation rule**:

- The **paper's detection-performance headline** for the 55-map corpus is the **image track's corrected F1 ≥ 0.830 at 50 m** (see `human-reviewed-corrected/corrected-f1-human-reviewed.md` §1).
- Cross-track claims should use the **uncorrected F1** (§3 tables above) — these are apples-to-apples across the three tracks.
- Do **not** cite the image-track's corrected F1 against the text tracks' uncorrected F1 as a "cross-track leader" claim — that comparison is confounded by the correction asymmetry.

## 5. Paired permutation tests (text-HIGH vs text-MIN only)

Four paired-permutation tests exist, all at text-HIGH vs text-MIN contrast:

| Contrast | Buffer | Observed ΔF1 | p-value | Wins_A / Losses_A / Ties | Significant (α = 0.05) |
|----------|:------:|------------:|:-------:|:------------------------:|:----------------------:|
| text-HIGH vs text-MIN | 20 m | +0.0047 | 0.4647 | 496 / 464 / 7,581 | no |
| text-HIGH vs text-MIN | 30 m | +0.0259 | 0.0 | 534 / 393 / 7,614 | yes |
| text-HIGH vs text-MIN | 40 m | +0.0291 | 0.0 | 535 / 362 / 7,644 | yes |
| text-HIGH vs text-MIN | 50 m | +0.0292 | 0.0 | 532 / 359 / 7,650 | yes |

All tests: 10,000 permutations, seed 42, tile-level paired bootstrap on tile-level F1. The 7,500+ ties per test reflect the long tail of tiles with zero detections and zero GT mounds in both tracks — tiles with identical behaviour under both conditions.

**At 20 m the text-HIGH vs text-MIN difference is not significant** (p = 0.4647), but at 30 / 40 / 50 m the gap is significant at p < 0.0001 (reported as p = 0.0 with 10,000 permutations). The HIGH-thinking advantage on the text track grows with buffer tolerance from +0.005 (not significant) to +0.029 (significant).

**No image-vs-text paired tests** exist. Cross-modality significance claims are therefore not directly supported on this corpus. The raw F1 gap at 50 m between text-HIGH and image is +0.017, which is comparable in magnitude to the text-HIGH vs text-MIN +0.029 gap that the 10,000-permutation test resolves at p = 0.0; a paired image-vs-text test would likely resolve an ordering but this is not directly evidenced.

## 6. Cost comparison

| Track | Total USD | Proposer USD | Verifier USD | Total tokens | Prompt-cache hit rate |
|-------|----------:|-------------:|-------------:|-------------:|----------------------:|
| image | $364.70 | $353.62 | $11.08 | 785.7 M | 91 % (621.3 M cached) |
| text-HIGH | $69.60 | $56.86 | $12.74 | 205.3 M | 0 % (no caching) |
| text-MIN | $60.79 | $46.72 | $14.06 | 88.8 M | 0 % (no caching) |

All three verified 2026-04-24 from `outputs/<track>/cost_manifest.json`.

Key cost notes:

- Image is 5.2× the cost of text-HIGH despite the 91 % prompt-cache hit rate — the ~47 M uncached input tokens (668.7 M input − 621.3 M cached) plus ~95 M thinking tokens dominate.
- text-HIGH's verifier cost ($12.74) is comparable to image's verifier cost ($11.08). The image-track savings are entirely in the verifier stage (fewer candidates survive the image-proposer stage despite its precision deficit).
- text-MIN's 88.8 M total tokens reflect the MINIMAL thinking setting eliminating thinking-token output on the proposer side.

**Paper implication**: for a cost-constrained deployment, the text-MIN track is the Pareto floor at $60.79 / F1 = 0.759 at 50 m; the text-HIGH track is $69.60 for F1 = 0.788 (+0.029 F1 for +$8.81); the image track is $364.70 for corrected F1 ≥ 0.830 (+0.04 – 0.07 corrected-F1 over text-HIGH's *uncorrected* F1 but at 5× the cost).

## 7. Detection volumes and human-review coverage

| Track | VLM candidates (post-PV) | Human-reviewed at 50 m | Human-review scope |
|-------|--------------------------:|-----------------------:|-------------------|
| image | 4,665 | 1,028 | VLM-only (pipeline-flagged, not-in-student-GT) slice; calibrated UI |
| text-HIGH | 4,143 | 0 | not reviewed |
| text-MIN | 3,861 | 0 | not reviewed |

The human-review process on the image track produced the 472 / 556 mound / not-mound split that underpins the corrected-F1 analyses. Equivalent review for text-HIGH and text-MIN would take an estimated 3–4 reviewer-days each given the per-candidate-crop review cost — out of scope for this paper.

## 8. Caveats / risk register

1. **No paired image-vs-text significance tests**: the four paired permutation tests are all text-HIGH vs text-MIN. Cross-modality significance claims (image vs text) are not directly supported on this corpus and must rely on raw F1 differences plus CI overlap heuristics.
2. **Human-review asymmetry**: corrected-F1 exists only for the image track. Direct corrected-F1 cross-track comparison is not available. The image-track's corrected F1 ≥ 0.830 should not be cited against text-HIGH's uncorrected 0.788 as evidence of image-track superiority — the comparison is confounded.
3. **No 100 m buffer for uncorrected F1**: the three `evaluation.json` files sweep 20 / 30 / 40 / 50 m only. For the 100 m buffer see `corrected-f1-multi-buffer/report.md` (image-track corrected only; no text-track equivalent).
4. **Thinking × modality confound**: the image-track uses HIGH thinking, matching text-HIGH. If a text-MIN image-track variant existed (MINIMAL thinking with image input), a 2 × 2 modality × thinking factorial would be directly testable. This is not in scope.
5. **PV threshold identical (prob_t = 0.15) across tracks** but not centrally recalibrated per track. A per-track threshold sweep would likely improve each track's standalone F1 by small amounts; see the phase3a-image-matrix / phase3a-text-matrix consensus-analysis summaries for the within-track threshold-robustness picture on the Era 2 scope.
6. **All three tracks use the same verifier prompt (adversarial v1)**. The paper's verifier-quarantine policy (`docs/methodology/v2-verifier-contamination-policy.md`) applies: v2-verifier results are not cited for any track.
7. **Attractor-pull scope** (Obs 272): the corrected-F1 ≥ 0.830 headline is at 50 m, inside the 125 m attractor-pull cap. Text-track corrected-F1 (if ever computed) would share the same scope limit.
8. **Consensus vote-threshold not matched across tracks**: image uses `vote_t = 3` (of K = 5); text-HIGH and text-MIN use `vote_t = 4` (confirmed from `outputs/<track>/resolved_config.yaml`). Image's lower threshold accepts detections with less consensus agreement, favouring recall over precision relative to the text tracks at matched K. A matched-vote-threshold cross-track comparison at `vote_t = 4` would require re-aggregating image detections at the higher threshold; out of scope here. Paper text citing cross-track precision/recall trade-offs should flag this difference.

## 9. Paper implications

### 9.1 Track selection decision tree

For the paper's Methods / Deployment section, the three-track selection maps to three deployment scenarios:

- **Highest raw F1 at matched scope**: text-HIGH (F1 = 0.788 @ 50 m). No post-hoc human review needed; the pipeline's outputs can be cited directly. Cost $69.60 for the 55-map corpus.
- **Cheapest adequate pipeline**: text-MIN (F1 = 0.759 @ 50 m). Sacrifices 0.029 F1 vs text-HIGH for a $8.81 / 12.7 % cost reduction and 4.6× fewer total tokens.
- **Highest post-review F1**: image (corrected F1 ≥ 0.830 @ 50 m). Requires a ~1,028-candidate human review step; the effort of human review is comparable to the pipeline cost itself, so this path is only chosen when paper-grade corrected-F1 is the target.

### 9.2 Methodological contribution — raw vs corrected F1 gap is a track-specific property

The image track's raw-to-corrected F1 gap (+0.059 from 0.771 to 0.830 at 50 m) is larger than any plausible cross-track raw F1 gap within the three tracks. This suggests that the student-GT incompleteness on the 55-map corpus affects all three tracks but is currently quantified only for the image track. Paper text should make this asymmetry explicit rather than imply the 0.830 corrected F1 is achievable only by the image track.

### 9.3 Suggested paper text (Results — cross-track)

> On the 55-map generalisation corpus (8,541 Era 2 tiles, `gemini-3-flash-preview` proposer, `gemini-3-flash` verifier, K = 5 consensus at prob_t = 0.15; vote_t = 3 for the image track and vote_t = 4 for both text tracks), the raw F1 at a 50 m matching buffer is 0.771 (image), 0.788 (text-HIGH), and 0.759 (text-MIN). text-HIGH is significantly better than text-MIN at buffers ≥ 30 m (paired permutation p = 0.0 at 10,000 permutations, seed 42; 20 m gap not significant at p = 0.4647). No paired image-vs-text tests were performed on this corpus. The image track's corrected F1 after per-candidate human review of the 1,028 VLM-only candidates is ≥ 0.830 [0.826, 0.833] at 50 m (`human-reviewed-corrected/corrected-f1-human-reviewed.md`); text-HIGH and text-MIN were not human-reviewed, so their corrected F1 is not available. The image track's raw-to-corrected F1 gap (+0.059) reflects the 45.9 % phantom-TP rate on the VLM-only slice; a comparable review on the text tracks would likely lift their corrected F1 by a similar amount but has not been conducted. Cost per track: image $364.70 (5.2 × the text-HIGH cost of $69.60 and 6.0 × the text-MIN cost of $60.79).

### 9.4 Follow-up priority ordering

If one follow-up evaluation budget is available for the 55-map corpus:

1. **Paired image-vs-text-HIGH permutation test at 50 m** — fills the most salient gap in §5; 10,000 permutations on the existing per-tile detections is ~10 minutes of CPU, zero API cost.
2. **Text-HIGH human review** — lifts text-HIGH's corrected F1 to the same paper-citable status as image's. Roughly 1,000-candidate review at ~1 minute / candidate ≈ 17 reviewer-hours.
3. **100 m buffer sweep for text-HIGH and text-MIN** — extends the buffer-comparison below to match the image-track multi-buffer availability. ~10 minutes of pipeline re-evaluation; zero API cost.

None of the three follow-ups are blocking for the current paper; all three would strengthen specific cross-track claims.

## 10. Files manifest

**Outputs (this directory)**:

- `report.md` — this report (synthesis, new 2026-04-24 Session 76).

**Inputs — per-track evaluation JSONs**:

- `outputs/55maps-image-generalisation/evaluation/evaluation.json` — image track F1 / P / R at 20 / 30 / 40 / 50 m.
- `outputs/55maps-text-high-generalisation/evaluation/evaluation.json` — text-HIGH F1 / P / R.
- `outputs/55maps-text-min-generalisation/evaluation/evaluation.json` — text-MIN F1 / P / R.

**Inputs — paired permutation JSONs** (all text-HIGH vs text-MIN, 10,000 permutations seed 42):

- `results/55maps-text-high-generalisation/paired-vs-min-20m/pairwise_permutation_result.json` — p = 0.4647 (n.s.).
- `results/55maps-text-high-generalisation/paired-vs-min-30m/pairwise_permutation_result.json` — p = 0.0.
- `results/55maps-text-high-generalisation/paired-vs-min-40m/pairwise_permutation_result.json` — p = 0.0.
- `results/55maps-text-high-generalisation/paired-vs-min-50m/pairwise_permutation_result.json` — p = 0.0.

**Inputs — cost manifests**:

- `outputs/55maps-image-generalisation/cost_manifest.json` — $364.70.
- `outputs/55maps-text-high-generalisation/cost_manifest.json` — $69.60.
- `outputs/55maps-text-min-generalisation/cost_manifest.json` — $60.79.

**Inputs — run metadata** (for §2):

- `outputs/55maps-image-generalisation/verified/run.meta.json` — confirms `gemini-3-flash-preview` proposer + `gemini-3-flash` verifier.
- `outputs/55maps-text-high-generalisation/verified/run.meta.json` — same.
- `outputs/55maps-text-min-generalisation/verified/run.meta.json` — same.

**Cross-references**:

- `results/55maps-image-generalisation/human-reviewed-corrected/corrected-f1-human-reviewed.md` — image-track corrected F1 @ 50 m.
- `results/55maps-image-generalisation/corrected-f1-multi-buffer/report.md` — image-track multi-buffer corrected F1.
- `results/gold-standard-extended-buffer-sweep/extended-buffer-report.md` — text-HIGH cross-corpus comparison (4-map GS vs 55-map student GT).

## 11. Reproducibility

This doc is a hand-authored synthesis of pre-existing per-track outputs; no new data-generation or statistical tests were run. To regenerate the numbers:

- **Per-track F1 / P / R** (§3): read `outputs/<track>/evaluation/evaluation.json` → `.summary.buffers[]`.
- **Paired permutation p-values** (§5): read `results/55maps-text-high-generalisation/paired-vs-min-<buffer>/pairwise_permutation_result.json` → `.permutation_test.p_value` + `.observed_f1_diff`.
- **Cost** (§6): read `outputs/<track>/cost_manifest.json` → `.totals.cost_usd` + `.by_stage`.
- **Run metadata** (§2): read `outputs/<track>/verified/run.meta.json`.

The three paired permutation tests that already exist were produced by `scripts/pairwise_permutation_test.py` (version 1.0.0 per the `metadata.script` field in each JSON). To run a new paired test (e.g., the image-vs-text-HIGH follow-up flagged in §9.4), follow the same invocation pattern:

```bash
python scripts/pairwise_permutation_test.py \
    --mode geojson \
    --geojson-a outputs/55maps-image-generalisation/verified/verified_detections.geojson \
    --label-a "image-K5-PV" \
    --geojson-b outputs/55maps-text-high-generalisation/verified/verified_detections.geojson \
    --label-b "text-HIGH-K5-PV" \
    --ground-truth inputs/vectors/references/student-mounds-55maps-reviewed.geojson \
    --bounds inputs/vectors/bounds/384/55maps_evaluation_bounds.geojson \
    --buffer-metres 50 \
    --n-permutations 10000 \
    --seed 42 \
    --out results/55maps-cross-track-comparison/paired-image-vs-text-high-50m
```

Compute: ~10 minutes on sapphire (tile-level shuffle on 8,541 tiles × 10,000 permutations). Zero API cost.

**Toolchain**: Python ≥ 3.11, GeoPandas ≥ 0.14, NumPy, pandas. Pinned versions in `requirements.txt`.
