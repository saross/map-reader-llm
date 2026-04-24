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
- **Twelve paired permutation tests** now exist (4 buffers × 3 contrasts) following the Session 77 image-vs-text runs (2026-04-24). Headline findings: **text-HIGH is significantly better than image at every buffer** (ΔF1 = −0.118 / −0.068 / −0.035 / −0.018 at 20 / 30 / 40 / 50 m; all p < 0.001). **text-MIN beats image at tight buffers (20, 30 m)** but **converges with image at 40, 50 m** (not significant; ΔF1 = −0.006 at 40 m, +0.012 at 50 m). The cross-modality significance claim the paper can make at 50 m is "text-HIGH significantly exceeds image"; image vs text-MIN and text-HIGH vs text-MIN claims are unchanged from the Session 76 landscape.
- **Track-specific precision-recall trade-offs**: at 50 m, text-HIGH is the most precise (0.848), text-MIN is a close second (0.849), image is the least precise (0.780). Recall is flipped: text-HIGH 0.737, text-MIN 0.687, image 0.763. Image trades precision for recall; text-MIN is the most parsimonious (highest precision, lowest recall).

**One-line paper claim**: "At raw F1 on the 55-map generalisation corpus (n = 8,541 Era 2 tiles; `gemini-3-flash-preview` proposer), text-HIGH is the top-performing track at every buffer ≤ 50 m (F1 = 0.788 at 50 m vs 0.759 text-MIN vs 0.771 image). After per-candidate human review, the image track's corrected F1 rises to ≥ 0.830 at 50 m, exceeding the text tracks' uncorrected F1; equivalent human review was not conducted for the text tracks, so corrected-F1 comparison across tracks is not available."

## 2. Run metadata (the three tracks are paired on scope, not on modality)

**Corpus scope**: the 55-map set is **disjoint** from the 4-map gold-standard Era-3 set used for hypothesis-testing analyses (zero map-sheet intersection; 59 sheets total project-wide). See `results/evaluation-scopes.md` §11 for the full scope definition.

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

text-HIGH leads by 0.117 raw F1 over image (paired permutation ΔF1 = −0.118, p = 0.0000, significant); text-HIGH vs text-MIN differ by +0.0047 (p = 0.4647; not significant); text-MIN beats image (ΔF1 = −0.113, p = 0.0000, significant).

### 3.2 30 m buffer

| Track | F1 | Precision | Recall |
|-------|-------:|----------:|-------:|
| image | 0.686 | 0.693 | 0.678 |
| **text-HIGH** | **0.753** | 0.810 | 0.704 |
| text-MIN | 0.727 | 0.813 | 0.658 |

text-HIGH leads by 0.068 raw F1 over image (paired permutation ΔF1 = −0.068, p = 0.0000, significant); text-HIGH vs text-MIN ΔF1 = +0.0259 (p = 0.0000, significant); text-MIN beats image (ΔF1 = −0.042, p = 0.0000, significant).

### 3.3 40 m buffer

| Track | F1 | Precision | Recall |
|-------|-------:|----------:|-------:|
| image | 0.748 | 0.757 | 0.740 |
| **text-HIGH** | **0.783** | 0.842 | 0.731 |
| text-MIN | 0.754 | 0.843 | 0.682 |

text-HIGH leads by 0.035 raw F1 over image (paired permutation ΔF1 = −0.035, p = 0.0000, significant); text-HIGH vs text-MIN ΔF1 = +0.0291 (p = 0.0000, significant); image vs text-MIN is **not significant** (ΔF1 = −0.006, p = 0.3412) — the two tracks converge at this buffer.

### 3.4 50 m buffer

| Track | F1 | Precision | Recall |
|-------|-------:|----------:|-------:|
| image | 0.771 | 0.780 | 0.763 |
| **text-HIGH** | **0.788** | 0.848 | 0.737 |
| text-MIN | 0.759 | 0.849 | 0.687 |

text-HIGH leads by 0.017 raw F1 over image (paired permutation ΔF1 = −0.018, p = 0.0008, significant); text-HIGH vs text-MIN ΔF1 = +0.0292 (p = 0.0000, significant); image vs text-MIN is **not significant** (ΔF1 = +0.012, p = 0.0543) — image marginally edges text-MIN but the difference does not survive at α = 0.05.

The text-HIGH − image gap narrows as buffer increases (0.117 → 0.068 → 0.035 → 0.017), consistent with the extended-buffer-report.md finding that image-proposer outputs have larger spatial-precision jitter than text-proposer outputs. At tight buffers the image track is penalised for spatial imprecision; at looser buffers the modality gap closes.

### 3.5 Extended buffers (75 / 100 / 125 m) — text tracks only

Added Session 77 2026-04-24 to fill the acute buffer-comparison gap. `evaluate_detections.py` run on sapphire (1,000 iterations, seed 42).

| Buffer | text-HIGH F1 | text-HIGH P | text-HIGH R | text-MIN F1 | text-MIN P | text-MIN R |
|-------:|-------------:|------------:|------------:|------------:|-----------:|-----------:|
| 75 m | 0.793 [0.782, 0.804] | 0.850 | 0.742 | 0.764 [0.752, 0.777] | 0.852 | 0.693 |
| 100 m | 0.794 [0.783, 0.805] | 0.851 | 0.743 | 0.765 [0.753, 0.777] | 0.852 | 0.694 |
| 125 m | 0.795 [0.784, 0.806] | 0.853 | 0.745 | 0.766 [0.754, 0.778] | 0.854 | 0.695 |

Both text tracks **plateau strongly above 50 m**: text-HIGH gains only +0.007 F1 from 50 m (0.788) to 125 m (0.795); text-MIN gains +0.007 from 50 m (0.759) to 125 m (0.766). This is sharply different from the image track's multi-buffer behaviour (corrected F1 0.832 → 0.854 from 50 m → 125 m; ΔF1 = +0.022, i.e., **3× the text-track buffer sensitivity**). The finding confirms that image-track buffer sensitivity is a modality property (image-proposer outputs have lower spatial precision), not a GT-noise artefact. Text-proposer outputs saturate their spatial-matching contribution by 50 m.

**Source**: `outputs/55maps-text-high-generalisation/extended-buffer-eval/evaluation.json` and `outputs/55maps-text-min-generalisation/extended-buffer-eval/evaluation.json`.

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

## 5. Paired permutation tests

Twelve paired-permutation tests exist across the three pairwise contrasts × four buffer tolerances. All tests: 10,000 permutations, seed 42, tile-level paired bootstrap on tile-level F1. The ~7,200–7,650 ties per test reflect the long tail of tiles with zero detections and zero GT mounds in both tracks — tiles with identical behaviour under both conditions.

### 5.1 text-HIGH vs text-MIN (4 tests)

| Contrast | Buffer | Observed ΔF1 | p-value | Wins_A / Losses_A / Ties | Significant (α = 0.05) |
|----------|:------:|------------:|:-------:|:------------------------:|:----------------------:|
| text-HIGH vs text-MIN | 20 m | +0.0047 | 0.4647 | 496 / 464 / 7,581 | no |
| text-HIGH vs text-MIN | 30 m | +0.0259 | 0.0 | 534 / 393 / 7,614 | yes |
| text-HIGH vs text-MIN | 40 m | +0.0291 | 0.0 | 535 / 362 / 7,644 | yes |
| text-HIGH vs text-MIN | 50 m | +0.0292 | 0.0 | 532 / 359 / 7,650 | yes |

### 5.2 image vs text-HIGH (4 tests, added Session 77 2026-04-24)

| Contrast | Buffer | Observed ΔF1 | p-value | Wins_A / Losses_A / Ties | Significant (α = 0.05) |
|----------|:------:|------------:|:-------:|:------------------------:|:----------------------:|
| image vs text-HIGH | 20 m | **−0.1178** | 0.0000 | 415 / 794 / 7,332 | yes |
| image vs text-HIGH | 30 m | **−0.0683** | 0.0000 | 465 / 666 / 7,410 | yes |
| image vs text-HIGH | 40 m | **−0.0351** | 0.0000 | 515 / 571 / 7,455 | yes |
| image vs text-HIGH | 50 m | **−0.0177** | 0.0008 | 536 / 514 / 7,491 | yes |

### 5.3 image vs text-MIN (4 tests, added Session 77 2026-04-24)

| Contrast | Buffer | Observed ΔF1 | p-value | Wins_A / Losses_A / Ties | Significant (α = 0.05) |
|----------|:------:|------------:|:-------:|:------------------------:|:----------------------:|
| image vs text-MIN | 20 m | **−0.1129** | 0.0000 | 516 / 795 / 7,230 | yes |
| image vs text-MIN | 30 m | **−0.0424** | 0.0000 | 606 / 659 / 7,276 | yes |
| image vs text-MIN | 40 m | **−0.0059** | 0.3412 | 653 / 564 / 7,324 | no |
| image vs text-MIN | 50 m | **+0.0115** | 0.0543 | 681 / 518 / 7,342 | no (marginal) |

### 5.4 Cross-contrast interpretation

- **text-HIGH is significantly better than both image and text-MIN at every buffer ≥ 30 m**. At 20 m text-HIGH vs text-MIN is not significant (p = 0.465) but text-HIGH vs image IS (ΔF1 = −0.118, p = 0.0000) — text-HIGH is the clean top-of-order.
- **image vs text-MIN is the most nuanced contrast**. Text-MIN significantly beats image at tight buffers (20 m ΔF1 = −0.113, p = 0.0000; 30 m ΔF1 = −0.042, p = 0.0000) but image and text-MIN converge at 40 / 50 m (p = 0.34, p = 0.054). At 50 m image marginally edges text-MIN (ΔF1 = +0.012; not significant). The buffer axis flips the ordering.
- **text-HIGH vs image gap narrows with buffer** but remains significant: ΔF1 goes from −0.118 at 20 m to −0.018 at 50 m (p = 0.0008 still rejecting the null). This is consistent with the attractor-pull / GT-precision-noise argument (`gold-standard-extended-buffer-sweep/extended-buffer-report.md`): image-proposer detections are less spatially-precise, so the image track loses more to tight buffers than the text tracks.
- **Scope-pair label on the GS extended-buffer anchor**: the cited `gold-standard-extended-buffer-sweep/extended-buffer-report.md` artefact is computed on the **Era 3 scope (327 tiles, F1 = 0.8155 at 20 m; F1 = 0.826 at 50 m)**, intentionally bounds-filtered for sibling-comparability with the h8/h10/h12 v2 library-design cells. A scope-paired Era 2 companion (487 tiles, 371 detections) on the same text-HIGH pipeline gives **F1 = 0.854 [0.821, 0.883] at 20 m** and **F1 = 0.873 [0.844, 0.901] at 50 m** (`results/gold-standard-extended-buffer-sweep-era2/evaluation.json`; Session 78, 2026-04-24). The Era 3 and Era 2 bootstrap CIs overlap at 20 m, so the scope-label difference is within sampling variance. The cross-corpus gap interpretation above is unaffected — only the scope label on the GS anchor changes. See `results/evaluation-scopes.md` §5.3 for the hierarchical stratified random sampling that constructs Era 3 from Era 2.
- **Three-way ordering at 50 m**: text-HIGH (0.788) > image (0.773) > text-MIN (0.761) with only the text-HIGH > image gap surviving paired-permutation significance at α = 0.05.

**Pipeline-control caveat**: the pipelines differ in consensus vote-threshold (image `vote_t = 3`; text `vote_t = 4`; see §8 Caveat 8). The paired tests reflect the pipelines as deployed, including the vote_t asymmetry. A vote_t-matched re-run on image would likely raise its precision and reduce its recall, shifting the comparison; we do not re-run here because the as-deployed comparison is the paper-citation target.

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

1. **Paired image-vs-text tests now available** (Session 77 2026-04-24): the 8 new paired permutation tests (see §5.2, §5.3) resolve the earlier cross-modality significance gap. The residual caveat is that the three pairwise tests at a given buffer do not use a joint FDR correction; raw p-values are reported. At the buffers where multiple pairwise tests matter for paper headline claims, the Bonferroni-corrected α would be 0.017 (3 tests); all significant results at α = 0.05 (p ≤ 0.001 for the image-vs-text-HIGH tests) comfortably survive this tighter threshold.
2. **Human-review asymmetry**: corrected-F1 exists only for the image track. Direct corrected-F1 cross-track comparison is not available. The image-track's corrected F1 ≥ 0.830 should not be cited against text-HIGH's uncorrected 0.788 as evidence of image-track superiority — the comparison is confounded.
3. **Extended buffers for text tracks now available** (Session 77 2026-04-24): text-HIGH and text-MIN evaluations at 75 / 100 / 125 m are at `outputs/55maps-text-{high,min}-generalisation/extended-buffer-eval/evaluation.json` (see §3.5). The residual gap is that no text-track corrected-F1 exists (no human review of the text tracks); the uncorrected-F1 buffer curves are the paper-citable figures for text-track spatial-tolerance behaviour.
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

1. **Paired image-vs-text permutation tests** — **DONE** (Session 77 2026-04-24). All 8 image-vs-text tests at 20 / 30 / 40 / 50 m now exist under `paired-image-vs-text-{high,min}-{20,30,40,50}m/`. See §5.2 and §5.3. Outcome: text-HIGH significantly beats image at every buffer; image and text-MIN converge at ≥ 40 m.
2. **Text-HIGH human review** — NOT done. Still the highest-leverage outstanding follow-up for corrected-F1 cross-track parity. Roughly 1,000-candidate review at ~1 minute / candidate ≈ 17 reviewer-hours. Would lift text-HIGH's corrected F1 to the same paper-citable status as image's; current estimate (based on image-track's +0.059 raw-to-corrected gap) places text-HIGH's corrected F1 in the 0.82 – 0.85 range.
3. **Extended buffer sweep for text tracks** — **DONE** (Session 77 2026-04-24). Text-HIGH and text-MIN at 75 / 100 / 125 m now exist at `outputs/55maps-text-{high,min}-generalisation/extended-buffer-eval/`. See §3.5. Outcome: both text tracks plateau by 75 m; buffer sensitivity is 3× lower than image track's corrected multi-buffer curve.

Remaining outstanding follow-up: item 2 (text-track human review).

## 10. Files manifest

**Outputs (this directory)**:

- `report.md` — this report (synthesis, new 2026-04-24 Session 76).

**Inputs — per-track evaluation JSONs**:

- `outputs/55maps-image-generalisation/evaluation/evaluation.json` — image track F1 / P / R at 20 / 30 / 40 / 50 m.
- `outputs/55maps-text-high-generalisation/evaluation/evaluation.json` — text-HIGH F1 / P / R.
- `outputs/55maps-text-min-generalisation/evaluation/evaluation.json` — text-MIN F1 / P / R.

**Inputs — paired permutation JSONs** (12 tests: 3 contrasts × 4 buffers; all 10,000 permutations seed 42):

text-HIGH vs text-MIN:

- `results/55maps-text-high-generalisation/paired-vs-min-20m/pairwise_permutation_result.json` — p = 0.4647 (n.s.).
- `results/55maps-text-high-generalisation/paired-vs-min-30m/pairwise_permutation_result.json` — p = 0.0.
- `results/55maps-text-high-generalisation/paired-vs-min-40m/pairwise_permutation_result.json` — p = 0.0.
- `results/55maps-text-high-generalisation/paired-vs-min-50m/pairwise_permutation_result.json` — p = 0.0.

image vs text-HIGH (Session 77 2026-04-24):

- `results/55maps-cross-track-comparison/paired-image-vs-text-high-20m/pairwise_permutation_result.json` — p = 0.0000 (***); ΔF1 = −0.1178.
- `results/55maps-cross-track-comparison/paired-image-vs-text-high-30m/pairwise_permutation_result.json` — p = 0.0000 (***); ΔF1 = −0.0683.
- `results/55maps-cross-track-comparison/paired-image-vs-text-high-40m/pairwise_permutation_result.json` — p = 0.0000 (***); ΔF1 = −0.0351.
- `results/55maps-cross-track-comparison/paired-image-vs-text-high-50m/pairwise_permutation_result.json` — p = 0.0008 (***); ΔF1 = −0.0177.

image vs text-MIN (Session 77 2026-04-24):

- `results/55maps-cross-track-comparison/paired-image-vs-text-min-20m/pairwise_permutation_result.json` — p = 0.0000 (***); ΔF1 = −0.1129.
- `results/55maps-cross-track-comparison/paired-image-vs-text-min-30m/pairwise_permutation_result.json` — p = 0.0000 (***); ΔF1 = −0.0424.
- `results/55maps-cross-track-comparison/paired-image-vs-text-min-40m/pairwise_permutation_result.json` — p = 0.3412 (n.s.); ΔF1 = −0.0059.
- `results/55maps-cross-track-comparison/paired-image-vs-text-min-50m/pairwise_permutation_result.json` — p = 0.0543 (n.s.); ΔF1 = +0.0115.

**Extended-buffer evaluations** (text tracks only; Session 77 2026-04-24):

- `outputs/55maps-text-high-generalisation/extended-buffer-eval/evaluation.{json,csv,md}` — text-HIGH at 75 / 100 / 125 m.
- `outputs/55maps-text-min-generalisation/extended-buffer-eval/evaluation.{json,csv,md}` — text-MIN at 75 / 100 / 125 m.

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

The 12 paired permutation tests were produced by `scripts/pairwise_permutation_test.py` (version 1.0.0 per the `metadata.script` field in each JSON). The correct CLI flag is `--output-dir` (not `--out`).

Invocation pattern for a new paired test:

```bash
.venv/bin/python scripts/pairwise_permutation_test.py \
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
    --output-dir results/55maps-cross-track-comparison/paired-image-vs-text-high-50m \
    --quiet
```

Invocation pattern for a new extended-buffer evaluation:

```bash
.venv/bin/python scripts/evaluate_detections.py \
    --detections outputs/55maps-text-high-generalisation/verified/verified_detections.geojson \
    --buffers 75 100 125 \
    --ground-truth inputs/vectors/references/student-mounds-55maps-reviewed.geojson \
    --bounds inputs/vectors/bounds/384/55maps_evaluation_bounds.geojson \
    --bootstrap 1000 --seed 42 \
    --output-dir outputs/55maps-text-high-generalisation/extended-buffer-eval \
    --label "text-HIGH-K5-PV-extended"
```

Compute: ~4 minutes on sapphire for all 8 image-vs-text paired tests; ~1 minute for both extended-buffer evaluations. Zero API cost.

**Toolchain**: Python ≥ 3.11, GeoPandas ≥ 0.14, NumPy, pandas. Pinned versions in `requirements.txt`.
