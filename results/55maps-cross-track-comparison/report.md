# 55-map cross-track comparison: image × text-HIGH × text-MIN

> **Last revised**: 2026-08-03 (Session-126 C4 wave-6 repair — audited-cost refresh, recovery-value refresh, method-text corrections). See [§ Changelog](#changelog) for revision history.

**Created**: 2026-04-24 (Session 76).
**Scope**: 55 topographic map sheets at 384 px (Era 2 bounds; 8,541 evaluation tiles).
**Purpose**: Side-by-side comparison of the three 55-map generalisation tracks — image-proposer, text-HIGH (HIGH thinking), text-MIN (MINIMAL thinking) — at matched buffer tolerances, with explicit notes on what paired-permutation testing is and is not available.

**This is a synthesis doc** (new in Session 76; not a data-generation pipeline). Numbers are lifted from the three per-track `evaluation.json` files and three `paired-vs-min-<buffer>/pairwise_permutation_result.json` paired-test JSONs; no new statistical tests were run.

## 1. Executive summary

The three 55-map generalisation tracks share the same evaluation scope (8,541 tiles at 384 px, Era 2 bounds), the same proposer model family (`gemini-3-flash-preview`), the same verifier (`gemini-3-flash` MINIMAL), and the same pipeline infrastructure — **with one pipeline-control difference**: the image track uses consensus vote threshold `vote_t = 3` whereas text-HIGH and text-MIN use `vote_t = 4` (per `outputs/<track>/resolved_config.yaml`). This is a lower bar for consensus on the image track; a matched-`vote_t` cross-track comparison would require re-processing. See §8 Caveat 8 for impact. They also differ in proposer input modality (image vs text) and thinking setting (HIGH vs MINIMAL for the two text tracks).

**Headline F1 numbers** (image + text-HIGH + text-MIN all refreshed
post-recovery 2026-05-03; cross-track-v2 commit `42ed1d32`):

| Track | F1 @ 20 m | F1 @ 30 m | F1 @ 40 m | F1 @ 50 m | Corrected F1 @ 50 m |
|-------|----------:|----------:|----------:|----------:|---------------------:|
| **image** | 0.508 | 0.689 | 0.752 | 0.774 | **0.833** [0.824, 0.842] (paper headline) |
| **text-HIGH** | 0.626 | 0.757 | 0.787 | 0.792 | **0.827** [0.817, 0.837] |
| **text-MIN** | 0.620 | 0.730 | 0.756 | 0.762 | **0.797** [0.786, 0.808] (added cross-track-v2; 585-row multi-buffer review) |

A fourth corrected run — text-HIGH at decoding temperature T=0.3 — has been completed in parallel as part of the corrected-run matrix (4-run cross-track family; see `results/55maps-mcc-v2-summary/report.md`, `results/55maps-pairwise-permutation-v2/summary.md`, `results/55maps-attractor-pull-v2/report.md`, `results/55maps-ds-summary-v2/report.md`, `results/55maps-fp-classification/report.md`). T=0.3's corrected F1 @ 50 m is **0.844** [0.834, 0.852], the leader of the four. T=0.3 is intentionally out of scope for this 3-track image × text-HIGH × text-MIN doc (which targets the modality / thinking-budget axes); the 4-run cross-track artefacts are the canonical reference for the temperature axis.

**Key findings**:

- **Text beats image at raw F1 at every buffer ≤ 50 m**: text-HIGH at 50 m is 0.792 vs image at 0.774 (ΔF1 = +0.018 raw, post-recovery; at 20 m the gap is +0.118). The image-track's raw F1 handicap at tight buffers is substantial.
- **Image and text-HIGH converge after human-review correction at 50 m**: corrected F1 for the image track is **0.833** [0.824, 0.842] (post-recovery; +0.001 from pre-recovery 0.832 reflecting the +1 phantom-promoted cand 2397) and for text-HIGH is **0.827** [0.817, 0.837] at 50 m — overlapping CIs, ΔF1 = +0.006 (image − text-HIGH). The text-HIGH corrected-F1 artefact (Session 78, 2026-04-24; refreshed post-recovery 2026-05-03) closes the earlier image-only-reviewed gap. The image-track's per-candidate review rescued **474 phantom-TPs** that the student GT missed at the 50 m buffer (single-buffer calibrated-UI review of 1,028 candidates plus the cross-track-v2 cand 2397 promotion; multi-buffer re-review: 474 at 50 m). text-MIN now also has a corrected F1 (added in cross-track-v2, 585-row multi-buffer review): **0.797** [0.786, 0.808] at 50 m. See §4 for the side-by-side comparison.
- **Cost per track**: image $200.83, text-HIGH $207.34, text-MIN $30.44 (per `outputs/<track>/cost_manifest.json`, all three from the 2026-06-12 audited-flex regeneration at commit `8e142df9c`). Image and text-HIGH sit at **approximately equal API cost** — ratio 0.97 ×, a 3.1 % difference, inside the ~5 % approximate-equality band — while text-MIN is materially cheaper at ≈ 6.6 × / 6.8 × less than image / text-HIGH respectively. The image track's 92.87 % prompt-caching hit rate (621.1 M cached tokens of 770.3 M total) is what holds its bill down to text-HIGH parity despite carrying ≈ 4 × the token load.
- **Twelve paired permutation tests** now exist (4 buffers × 3 contrasts) following the Session 77 image-vs-text runs (2026-04-24). Headline findings (v1, uncorrected GT): **text-HIGH is significantly better than image at every buffer** (ΔF1 = −0.118 / −0.068 / −0.035 / −0.018 at 20 / 30 / 40 / 50 m; all p < 0.001). **text-MIN beats image at tight buffers (20, 30 m)** but **converges with image at 40, 50 m** (not significant; ΔF1 = −0.006 at 40 m, +0.011 at 50 m). For the post-recovery, corrected-GT v2 paired-permutation results (10 buffers × 6 contrasts across all four corrected runs), see `results/55maps-pairwise-permutation-v2/summary.md`; v2 results preserve the sign and significance of every pair at R=50 m: T=0.3 vs T=0.7 ΔF1 = +0.0162 \*\*\*, T=0.3 vs image +0.0102 \*, T=0.7 vs image −0.0060 ns, T=0.3 vs T=MIN +0.0467 \*\*\*, T=0.7 vs T=MIN +0.0305 \*\*\*, image vs T=MIN +0.0365 \*\*\*. The cross-modality significance claim the paper can make at R = 50 m is "text-HIGH significantly exceeds image" (uncorrected v1) but "text-HIGH and image are statistically indistinguishable" (corrected-GT v2 — the v2 finding is the apples-to-apples comparison and supersedes v1 for paper headlines). Image vs text-MIN and text-HIGH vs text-MIN remain significant across both v1 and v2.
- **Track-specific precision-recall trade-offs**: at 50 m raw, text-HIGH is the most precise (0.847), text-MIN is a close second (0.849), image is the least precise (0.780). Recall is flipped: text-HIGH 0.744, text-MIN 0.691, image 0.769. Image trades precision for recall; text-MIN is the most parsimonious (highest precision, lowest recall).

**One-line paper claim**: "At raw F1 on the 55-map generalisation corpus (n = 8,541 Era 2 tiles; `gemini-3-flash-preview` proposer), text-HIGH is the top-performing track at every buffer ≤ 50 m (F1 = 0.792 at 50 m vs 0.762 text-MIN vs 0.774 image). After per-candidate human review, the image and text-HIGH tracks **converge** at F1 ≈ 0.83 at 50 m (image 0.833 [0.824, 0.842]; text-HIGH 0.827 [0.817, 0.837]; ΔF1 = +0.006 with overlapping CIs) — a cross-track consistency finding that strengthens the generalisation claim. text-MIN's corrected F1 sits below at 0.797 [0.786, 0.808] (585-row multi-buffer review added in cross-track-v2)."

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
| image | 0.508 | 0.512 | 0.505 |
| **text-HIGH** | **0.626** | 0.670 | 0.588 |
| text-MIN | 0.620 | 0.691 | 0.563 |

text-HIGH leads by 0.118 raw F1 over image (paired permutation ΔF1 = −0.118, p = 0.0000, significant — v1 against pre-recovery T=0.7); text-HIGH vs text-MIN differ by +0.006 (p = 0.4647 v1; not significant); text-MIN beats image (ΔF1 = −0.112, p = 0.0000, significant).

### 3.2 30 m buffer

| Track | F1 | Precision | Recall |
|-------|-------:|----------:|-------:|
| image | 0.689 | 0.693 | 0.684 |
| **text-HIGH** | **0.757** | 0.810 | 0.710 |
| text-MIN | 0.730 | 0.813 | 0.662 |

text-HIGH leads by 0.068 raw F1 over image (paired permutation ΔF1 = −0.068, p = 0.0000, significant — v1 against pre-recovery T=0.7); text-HIGH vs text-MIN ΔF1 = +0.027 (p = 0.0000 v1, significant); text-MIN beats image (ΔF1 = −0.042, p = 0.0000, significant).

### 3.3 40 m buffer

| Track | F1 | Precision | Recall |
|-------|-------:|----------:|-------:|
| image | 0.752 | 0.757 | 0.747 |
| **text-HIGH** | **0.787** | 0.842 | 0.739 |
| text-MIN | 0.756 | 0.842 | 0.686 |

text-HIGH leads by 0.035 raw F1 over image (paired permutation ΔF1 = −0.035, p = 0.0000, significant — v1 against pre-recovery T=0.7); text-HIGH vs text-MIN ΔF1 = +0.030 (p = 0.0000 v1, significant); image vs text-MIN is **not significant** (ΔF1 = −0.005, p = 0.3412 v1; corrected-GT v2 confirms ns at R=40 m) — the two tracks converge at this buffer.

### 3.4 50 m buffer

| Track | F1 | Precision | Recall |
|-------|-------:|----------:|-------:|
| image | 0.774 | 0.780 | 0.769 |
| **text-HIGH** | **0.792** | 0.847 | 0.744 |
| text-MIN | 0.762 | 0.849 | 0.691 |

text-HIGH leads by 0.018 raw F1 over image (paired permutation v1 ΔF1 = −0.018, p = 0.0008, significant — against pre-recovery T=0.7); however, **the corrected-GT v2 paired-permutation test inverts the sign and removes significance**: at R=50 m, T=0.7 vs image gives ΔF1 = −0.0060 [−0.0156, +0.0035] (ns; image marginally edges text-HIGH after extended-GT correction; see `results/55maps-pairwise-permutation-v2/summary.md`). The v2 corrected-GT result is the apples-to-apples comparison; the v1 raw-F1 ΔF1 of +0.018 is pipeline-as-deployed. text-HIGH vs text-MIN raw ΔF1 = +0.030 (p = 0.0000 v1, significant; v2 confirms +0.0305 \*\*\*); image vs text-MIN raw ΔF1 = +0.011 (p = 0.0543 v1, marginal; v2 confirms +0.0365 \*\*\*) — image significantly edges text-MIN under corrected GT.

The text-HIGH − image raw F1 gap narrows as buffer increases (0.118 → 0.068 → 0.035 → 0.018), consistent with the extended-buffer-report.md finding that image-proposer outputs have larger spatial-precision jitter than text-proposer outputs. At tight buffers the image track is penalised for spatial imprecision; at looser buffers the modality gap closes — and inverts under corrected GT.

### 3.5 Extended buffers (75 / 100 / 125 m) — text tracks only

Added Session 77 2026-04-24 to fill the acute buffer-comparison gap. `evaluate_detections.py` run on sapphire (10,000 iterations, BCa, seed 42).

| Buffer | text-HIGH F1 | text-HIGH P | text-HIGH R | text-MIN F1 | text-MIN P | text-MIN R |
|-------:|-------------:|------------:|------------:|------------:|-----------:|-----------:|
| 75 m | 0.794 [0.784, 0.804] | 0.850 | 0.746 | 0.764 [0.752, 0.777] | 0.852 | 0.693 |
| 100 m | 0.796 [0.786, 0.805] | 0.851 | 0.747 | 0.765 [0.753, 0.777] | 0.852 | 0.694 |
| 125 m | 0.797 [0.787, 0.806] | 0.852 | 0.748 | 0.766 [0.754, 0.778] | 0.854 | 0.695 |

Both text tracks **plateau strongly above 50 m**: text-HIGH gains only +0.005 F1 from 50 m (0.792) to 125 m (0.797); text-MIN gains +0.005 from 50 m (0.762) to 125 m (0.767). This is sharply different from the image track's multi-buffer behaviour (corrected F1 0.832 → 0.854 from 50 m → 125 m; ΔF1 = +0.022, i.e., **4× the text-track buffer sensitivity**). The finding confirms that image-track buffer sensitivity is a modality property (image-proposer outputs have lower spatial precision), not a GT-noise artefact. Text-proposer outputs saturate their spatial-matching contribution by 50 m.

**Source**: `outputs/55maps-text-high-generalisation/extended-buffer-eval/evaluation.json` and `outputs/55maps-text-min-generalisation/extended-buffer-eval/evaluation.json`.

### 3.6 Tile-level MCC (buffer-independent)

Tile-level classification metrics complement mound-level F1: they answer "does each 384 px tile contain *any* mound?" rather than "is each mound matched?". MCC is buffer-independent because it does not depend on centroid-to-centroid matching (pre-registration §4.2). 10,000-iter BCa bootstrap CIs, seed 42.

| Track | MCC | MCC 95% CI | Sensitivity | Specificity | TP / TN / FP / FN |
|-------|:---:|:---:|:---:|:---:|:---:|
| image | **0.692** | [0.678, 0.706] | 0.708 | 0.948 | 2,394 / 4,891 / 270 / 986 |
| text-HIGH | 0.648 | [0.633, 0.662] | 0.644 | 0.953 | 2,176 / 4,918 / 243 / 1,204 |
| text-MIN | 0.626 | [0.611, 0.641] | 0.614 | 0.955 | 2,075 / 4,927 / 234 / 1,305 |

**Tile-level MCC ordering inverts the mound-level F1 ordering.** Image leads on tile-level MCC (0.692, post-recovery) while text-HIGH leads on mound-level corrected F1 (0.827). Image's tile-level sensitivity (0.708) is notably higher than the text tracks' (0.644 / 0.614) — image catches a higher fraction of mound-bearing tiles, then localises within them imprecisely (the source of its tight-buffer F1 penalty). Text tracks achieve marginally higher tile-level specificity (≈0.95 vs 0.95) but sacrifice sensitivity. The cross-metric tension is the same pattern flagged in the leaderboard-20m-annotated Tier 5 analysis (row #15 "Image baseline + PV" has the highest tile-level MCC of any condition, 0.877, alongside low mound-level F1=0.717 at 20 m).

**Paper-framing implication**: a track-selection recommendation based on mound-level F1 alone would pick text-HIGH (or T=0.3 text-HIGH; see `results/55maps-mcc-v2-summary/report.md`); a recommendation based on tile-level coverage (e.g. "flag every mound-bearing tile for human inspection") would pick image. Both are defensible and serve different downstream use cases.

**Source**: `outputs/55maps-{image,text-high,text-min}-generalisation/full-buffer-eval/evaluation.json` → `summary.tile_classification`.

## 4. Corrected-F1 availability

**All three tracks have now been human-reviewed** (text-HIGH human review completed 2026-04-24, Session 78; corrected-F1 artefact at `results/55maps-text-high-generalisation/corrected-f1-multi-buffer/`. text-MIN multi-buffer review added in cross-track-v2 commit `42ed1d32`; 585-row review CSV at `results/55maps-text-min-generalisation/human-review-multi-buffer.csv`).

| Track | Corrected F1 @ 50 m | Multi-buffer corrected F1 | n human-reviewed | Source |
|-------|--------------------:|:-------------------------:|-----------------:|--------|
| image | **0.833** [0.824, 0.842] | 0.833 → 0.856 @ 50 → 150 m | 1,028 candidates (calibrated UI, 50 m single-buffer) + 557 re-reviewed multi-buffer + 74 sentinel additions + 1 cand 2397 promoted in cross-track-v2 | `corrected-f1-human-reviewed.md` + `corrected-f1-multi-buffer/report.md` |
| text-HIGH | **0.827** [0.817, 0.837] | 0.827 → 0.835 @ 50 → 150 m | 630 candidates (multi-buffer review; 32 `>150 m` sentinels excluded; refreshed post-recovery 2026-05-03) | `results/55maps-text-high-generalisation/corrected-f1-multi-buffer/` |
| text-MIN | **0.797** [0.786, 0.808] | 0.797 → 0.802 @ 50 → 150 m | 585 candidates (multi-buffer review added in cross-track-v2; 250 reviewer-promoted at R=50 m) | `results/55maps-text-min-generalisation/corrected-f1-multi-buffer/` |

### 4.1 Text-HIGH multi-buffer corrected F1 (Session 78 2026-04-24; refreshed post-recovery 2026-05-03)

Approach B (extended-GT-at-R Hungarian matching); 10,000-iter bootstrap; seed 42; 630 reviewed candidates with 32 excluded as `>150 m` sentinel-shell labels.

| R (m) | TP | FP | FN | Precision | Recall | F1 | F1 95 % CI |
|---:|---:|---:|---:|---:|---:|---:|:---:|
| 50 | 3,797 | 367 | 1,218 | 0.9119 | 0.7571 | **0.8273** | [0.8173, 0.8370] |
| 75 | 3,817 | 347 | 1,217 | 0.9167 | 0.7582 | 0.8300 | [0.8199, 0.8395] |
| 100 | 3,836 | 328 | 1,217 | 0.9212 | 0.7592 | 0.8324 | [0.8225, 0.8418] |
| 125 | 3,847 | 317 | 1,217 | 0.9239 | 0.7597 | 0.8338 | [0.8240, 0.8432] |
| 150 | 3,853 | 311 | 1,216 | 0.9253 | 0.7601 | 0.8346 | [0.8248, 0.8440] |

### 4.2 Image vs text-HIGH corrected F1 — side-by-side at paper-primary anchors

| R (m) | Image F1 (corrected) | text-HIGH F1 (corrected) | ΔF1 (image − text-HIGH) | CI overlap? |
|---:|---:|---:|---:|:---:|
| 50 | 0.833 [0.824, 0.842] | 0.827 [0.817, 0.837] | +0.006 | yes (substantial) |
| 100 | 0.853 [0.845, 0.862] | 0.832 [0.822, 0.842] | +0.021 | yes (partial) |

**Convergence finding**: after per-candidate human review, both tracks reach **F1 ≈ 0.83 at 50 m** — the image track's single-buffer headline (0.833, post-recovery) and text-HIGH's multi-buffer 50 m value (0.827) differ by only +0.006 F1, well inside overlapping bootstrap 95 % CIs. This cross-track convergence under human review is a substantive finding: it indicates that the uncorrected-F1 gap between modalities (text-HIGH > image at ≤ 50 m; see §3) largely reflects student-GT incompleteness and attractor-pull differences, **not** a modality-intrinsic detection-quality gap. At wider buffers (100 m) the image track pulls ahead by +0.021 F1, consistent with its larger buffer-sensitivity (see §3.5). The corrected-GT v2 paired-permutation test confirms the no-significant-difference reading at R=50 m (T=0.7 vs image ΔF1 = −0.0060 ns; image marginally edges by 0.006).

### 4.3 Verifier calibration — cross-track

Both tracks share the same verifier (`flash-adversarial-v1`); Obs 269-equivalent calibration crosstab on the text-HIGH review subset is new in Session 78.

| Metric | Image track | text-HIGH track |
|---|:---:|:---:|
| n reviewed | 1,028 | 630 |
| Prevalence (p_mound) | 0.459 | 0.559 |
| AUC | 0.655 [0.622, 0.687] | **0.829 [0.796, 0.860]** |
| Brier | 0.323 [0.297, 0.348] | **0.167 [0.145, 0.189]** |
| ECE | 0.269 | **0.081** |
| P(mound \| p ≤ 0.25) | 0.174 [0.126, 0.224] | 0.207 [0.153, 0.262] |

**Calibration divergence, not convergence**: despite sharing the verifier prompt, the text-HIGH track's verifier behaviour on its own review subset is **substantially better-calibrated** than on the image-track subset (AUC +0.17, Brier halved, ECE cut by two-thirds). This is not the identity result the verifier-prompt-is-shared intuition would predict. Two likely drivers: (i) the text-HIGH candidate pool has a different symbol-class mix and higher base-rate prevalence (55.9 % vs 45.9 %), making the binary decision easier; (ii) the image-track candidates include a larger `not_mound` mass in the saturated `p = 1.0` bin (167 / 370 = 45.1 %), a failure mode absent from text-HIGH (23 / 155 = 14.8 %). Paper text should therefore cite per-track calibration separately rather than presenting a single verifier-calibration claim. See `results/55maps-text-high-generalisation/verifier-calibration-crosstab/calibration_autogen.md` for the full text-HIGH breakdown.

### 4.4 Paper citation rule (updated)

- The **paper's detection-performance headline** for the 55-map corpus can now cite **three convergent corrected-F1 values at 50 m**: image = 0.833 [0.824, 0.842], text-HIGH = 0.827 [0.817, 0.837], text-MIN = 0.797 [0.786, 0.808] (all refreshed post-recovery 2026-05-03 via cross-track-v2 commit `42ed1d32`). For corrected-GT cross-track significance, cite the v2 paired-permutation results (`results/55maps-pairwise-permutation-v2/summary.md`) — image and text-HIGH are statistically indistinguishable at R = 50 m; both significantly exceed text-MIN.
- Cross-track **uncorrected** F1 comparisons (§3 tables) remain the apples-to-apples ΔF1 source for **v1** paired-permutation significance claims (§5.1 – §5.3), not for paper headlines (use v2 corrected-GT results instead).
- Calibration metrics (AUC, Brier, ECE) must be cited per-track — the verifier is the same prompt but its behaviour varies markedly by candidate pool.

## 5. Paired permutation tests

Twelve paired-permutation tests exist across the three pairwise contrasts × four buffer tolerances. All tests: 10,000 permutations, seed 42, tile-level paired bootstrap on tile-level F1. The ~7,200–7,650 ties per test reflect the long tail of tiles with zero detections and zero GT mounds in both tracks — tiles with identical behaviour under both conditions.

**Source-of-truth note (post-recovery 2026-05-03; cross-track-v2 commit `42ed1d32`)**: the 12 v1 tests below were computed against the pre-recovery T=0.7 detection set (4,143 detections; uncorrected GT). The post-recovery detection sets — T=0.7 = 4,164 (+21), image = 4,680 (+15 incl. cand 2397), text-MIN = 3,865 (+4) — were used to regenerate a v2 corrected-GT pairwise-permutation suite at 10 buffers × 6 contrasts (the family includes T=0.3 as the fourth corrected run); see `results/55maps-pairwise-permutation-v2/summary.md`. v2 headline at R = 50 m, all six pairs:

| Pair | ΔF1 | 95 % CI | BH-FDR sig (q=0.05) |
|------|-----:|:-------:|:---:|
| T=0.3 vs T=0.7 | +0.0162 | [+0.0089, +0.0238] | \*\*\* |
| T=0.3 vs image | +0.0102 | [+0.0009, +0.0193] | \* |
| T=0.7 vs image | −0.0060 | [−0.0156, +0.0035] | ns |
| T=0.3 vs T=MIN | +0.0467 | [+0.0374, +0.0562] | \*\*\* |
| T=0.7 vs T=MIN | +0.0305 | [+0.0210, +0.0400] | \*\*\* |
| image vs T=MIN | +0.0365 | [+0.0256, +0.0476] | \*\*\* |

All six pairs preserve sign and significance vs the pre-recovery v2 baseline. The cross-track-v2 refresh is paper-citable for corrected-GT significance claims; use the v1 tables below only for the uncorrected-GT comparison footnote. The v1 tables remain valid for their stated scope (uncorrected GT, pre-recovery T=0.7) but should not be cited as the apples-to-apples cross-track significance claim.

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
- **image vs text-MIN is the most nuanced contrast**. Text-MIN significantly beats image at tight buffers (20 m ΔF1 = −0.113, p = 0.0000; 30 m ΔF1 = −0.042, p = 0.0000) but image and text-MIN converge at 40 / 50 m (p = 0.34, p = 0.054). At 50 m image marginally edges text-MIN (ΔF1 = +0.011; not significant). The buffer axis flips the ordering.
- **text-HIGH vs image gap narrows with buffer** but remains significant: ΔF1 goes from −0.118 at 20 m to −0.018 at 50 m (p = 0.0008 still rejecting the null). This is consistent with the attractor-pull / GT-precision-noise argument (`gold-standard-extended-buffer-sweep/extended-buffer-report.md`): image-proposer detections are less spatially-precise, so the image track loses more to tight buffers than the text tracks.
- **Scope-pair label on the GS extended-buffer anchor**: the cited `gold-standard-extended-buffer-sweep/extended-buffer-report.md` artefact is computed on the **Era 3 scope (327 tiles, F1 = 0.8155 at 20 m; F1 = 0.826 at 50 m)**, intentionally bounds-filtered for sibling-comparability with the h8/h10/h12 v2 library-design cells. A scope-paired Era 2 companion (487 tiles, **380 detections post-recovery 2026-05-03**; was 371) on the same text-HIGH pipeline gives **F1 = 0.8663 [0.8591, 0.8726] at 20 m** and **F1 = 0.8859 [0.8798, 0.8919] at 50 m** (`results/gold-standard-extended-buffer-sweep-era2/evaluation.json`; Session 78 baseline 2026-04-24, refreshed Session 82 2026-05-03 at commits `90890ae9..c6023034`; pre-recovery values were 0.854 [0.821, 0.883] @ 20 m and 0.873 [0.844, 0.901] @ 50 m). The Era 3 and Era 2 bootstrap CIs no longer overlap at 20 m post-recovery (the BCa N=10K CI on the refreshed Era 2 evaluation is tighter than the 1K-iter Era 3 CI, and Era 2 lifted by ~+0.013 F1), but the residual gap is consistent with random scope sampling rather than a systematic shift. The cross-corpus gap interpretation above is unaffected — only the scope label on the GS anchor changes. See `results/evaluation-scopes.md` §5.3 for the hierarchical stratified random sampling that constructs Era 3 from Era 2.
- **Three-way raw F1 ordering at 50 m (uncorrected GT, post-recovery)**: text-HIGH (0.792) > image (0.774) > text-MIN (0.762) with only the text-HIGH > image gap surviving paired-permutation v1 significance at α = 0.05. Under corrected-GT v2 (the paper-headline framing), the ordering at R = 50 m flips to image (0.833) ≈ text-HIGH (0.827) > text-MIN (0.797), with image vs text-HIGH non-significant and both significantly above text-MIN — see the v2 summary table immediately above.

**Pipeline-control caveat**: the pipelines differ in consensus vote-threshold (image `vote_t = 3`; text `vote_t = 4`; see §8 Caveat 8). The paired tests reflect the pipelines as deployed, including the vote_t asymmetry. A vote_t-matched re-run on image would likely raise its precision and reduce its recall, shifting the comparison; we do not re-run here because the as-deployed comparison is the paper-citation target.

## 6. Cost comparison

| Track | Total USD | Proposer USD | Verifier USD | Total tokens | Prompt-cache hit rate |
|-------|----------:|-------------:|-------------:|-------------:|----------------------:|
| image | $200.83 | $195.35 | $5.48 | 770.3 M | 92.87 % (621.1 M cached) |
| text-HIGH | $207.34 | $200.93 | $6.41 | 187.6 M | 0 % (no caching) |
| text-MIN | $30.44 | $23.36 | $7.08 | 69.1 M | 0 % (no caching) |

**Vintage (single, all three tracks)**: every figure in this section comes from the 2026-06-12 token-load-audit regeneration of `outputs/<track>/cost_manifest.json` (commit `8e142df9c`), which prices all stages at the audited flex rates ($0.25 / M input, $1.50 / M output, $0.05 / M cached input) and bills thinking tokens as output. Stage decomposition, read from `.by_stage` and summing exactly to each stated total: image $195.35 proposer + $5.48 verifier = $200.83; text-HIGH $200.93 + $6.41 = $207.34; text-MIN $23.36 + $7.08 = $30.44. The `extract_crops`, `consensus` and `evaluate` stages carry no API cost, so proposer + verifier is the whole bill on every track. (The mixed-vintage figures this section previously carried, and the recovery-era decomposition that did not sum, are recorded in the [Changelog](#changelog).)

Key cost notes:

- **Image and text-HIGH are approximately equal in cost** ($200.83 vs $207.34; ratio 0.97 ×, a 3.1 % difference — within the ~5 % approximate-equality band), reached by two different routes. The image track carries ≈ 4 × the token load (770.3 M vs 187.6 M) but caches 92.87 % of it: only ≈ 47.7 M of its input tokens are billed at the full input rate (668,719,361 total input − 621,058,706 cached), and its 95.2 M thinking tokens, billed as output, are the single largest line in the $195.35 proposer bill ($142.75 of it). The text-HIGH track has no caching at all, and its 115.0 M thinking tokens plus 8.2 M output tokens at $1.50 / M account for $184.90 of its $200.93 proposer bill.
- **Verifier cost tracks candidate volume, not modality**: the audited reconstruction prices every verifier call at $0.000696, so image $5.48 (7,878 candidates), text-HIGH $6.41 (9,205) and text-MIN $7.08 (10,170) simply rank by how many candidates each proposer emitted. The verifier stage is 2.7 % / 3.1 % / 23.3 % of each track's total bill.
- **text-MIN's 69.1 M total tokens** reflect the MINIMAL thinking setting eliminating thinking-token output on the proposer side entirely (`totals.thinking_tokens = 0`, against 115.0 M for text-HIGH). Its proposer input-token count is identical to text-HIGH's (64,142,910 — same prompts, same 42,705 tile-passes), so the whole cost gap between the two text tracks is thinking-plus-output tokens.

**Paper implication**: for a cost-constrained deployment, the text-MIN track is the Pareto floor at $30.44 / raw F1 = 0.762 at 50 m (corrected F1 = 0.797 post-cross-track-v2); the text-HIGH track is $207.34 for raw F1 = 0.792 (corrected F1 = 0.827; +0.030 corrected F1 for +$176.90); the image track is $200.83 for corrected F1 = 0.833 (≈ +0.006 corrected-F1 over text-HIGH at approximately equal API cost). Under the audited manifests image and text-HIGH are separated neither on cost nor on corrected-F1 ceiling (statistically indistinguishable per cross-track-v2), so the material cost decision on this corpus is text-MIN versus the two HIGH-thinking tracks, not image versus text-HIGH.

## 7. Detection volumes and human-review coverage

| Track | VLM candidates (post-PV) | Human-reviewed at 50 m | Human-review scope |
|-------|--------------------------:|-----------------------:|-------------------|
| image | 4,680 (post-recovery; +15 incl. cand 2397) | 1,030 (single-buffer 1,028 + cands 2397 and 5641 from the multi-buffer re-review) | VLM-only (pipeline-flagged, not-in-student-GT) slice; calibrated UI |
| text-HIGH | 4,164 (post-recovery; +21) | 630 | VLM-only slice; multi-buffer review (Session 78 2026-04-24; corrected-GT counts refreshed post-recovery 2026-05-03); 32 `>150 m` sentinel labels excluded |
| text-MIN | 3,865 (post-recovery; +4) | 585 | VLM-only slice; multi-buffer review added in cross-track-v2 commit `42ed1d32` (250 reviewer-promoted at R = 50 m) |

**Derivation of the "Human-reviewed at 50 m" column** (no tracked artefact holds these as scalars): the image figure is the **union** of `results/55maps-image-generalisation/human-review.csv` (1,028 rows, all at `buffer_metres == 50`) and `results/55maps-image-generalisation/human-review-multi-buffer.csv` restricted to `buffer_metres == 50` (286 rows), which adds candidates 2397 and 5641 and carries candidate 5777's `not_mound → mound` label flip from the multi-buffer file — 1,030 reviewed, 475 mound, 555 not-mound. The text-HIGH figure is `verifier-calibration-crosstab/calibration.json` `n_total` = 630. The text-MIN figure is the 585 **data rows** of `results/55maps-text-min-generalisation/human-review-multi-buffer.csv` (a header-inclusive `wc -l` gives 586, which was the source of the superseded figure); `calibration.json` `n_total` = 585 agrees.

The human-review process produced a 475 / 555 mound / not-mound split on the image track (underpinning its corrected-F1 analysis post cand 2397 promotion), a 352 / 278 split on text-HIGH (prevalence 55.9 %), and a 324 / 261 split on text-MIN (prevalence 55.4 %; cross-track-v2 review). Note that the image track's **475** reviewed-mound labels are a different quantity from the **474** `n_reviewer_promoted_at_R` recorded in `corrected-f1-multi-buffer/corrected-f1.csv` at R = 50 m (the figure cited in §1): the latter counts promotions into the extended GT as computed by the corrected-F1 pipeline. The one-candidate difference between the two has not been traced.

## 8. Caveats / risk register

1. **Paired image-vs-text tests now available** (Session 77 2026-04-24): the 8 new paired permutation tests (see §5.2, §5.3) resolve the earlier cross-modality significance gap. The residual caveat is that the three pairwise tests at a given buffer do not use a joint FDR correction; raw p-values are reported. At the buffers where multiple pairwise tests matter for paper headline claims, the Bonferroni-corrected α would be 0.017 (3 tests); all significant results at α = 0.05 (p ≤ 0.001 for the image-vs-text-HIGH tests) comfortably survive this tighter threshold.
2. **Human-review asymmetry (resolved)**: corrected-F1 now exists for all three tracks (text-HIGH added Session 78, 2026-04-24; text-MIN added cross-track-v2, 2026-05-03). Image vs text-HIGH corrected F1 at 50 m converges at ≈ 0.83 (§4.2); text-MIN sits below at 0.797. All cross-track claims can now use corrected F1; cross-track-v2 paired-permutation results are the apples-to-apples paper-citable significance reference.
3. **Extended buffers for text tracks now available** (Session 77 2026-04-24): text-HIGH and text-MIN evaluations at 75 / 100 / 125 m are at `outputs/55maps-text-{high,min}-generalisation/extended-buffer-eval/evaluation.json` (see §3.5). The residual gap is that no text-track corrected-F1 exists (no human review of the text tracks); the uncorrected-F1 buffer curves are the paper-citable figures for text-track spatial-tolerance behaviour.
4. **Thinking × modality confound**: the image-track uses HIGH thinking, matching text-HIGH. If a text-MIN image-track variant existed (MINIMAL thinking with image input), a 2 × 2 modality × thinking factorial would be directly testable. This is not in scope.
5. **PV threshold identical (prob_t = 0.15) across tracks** but not centrally recalibrated per track. A per-track threshold sweep would likely improve each track's standalone F1 by small amounts; see the phase3a-image-matrix / phase3a-text-matrix consensus-analysis summaries for the within-track threshold-robustness picture on the Era 2 scope.
6. **All three tracks use the same verifier prompt (adversarial v1)**. The paper's verifier-quarantine policy (`docs/methodology/v2-verifier-contamination-policy.md`) applies: v2-verifier results are not cited for any track.
7. **Attractor-pull scope** (Obs 272): the corrected-F1 ≥ 0.830 headline is at 50 m, inside the 125 m attractor-pull cap. Text-track corrected-F1 (if ever computed) would share the same scope limit.
8. **Consensus vote-threshold not matched across tracks**: image uses `vote_t = 3` (of K = 5); text-HIGH and text-MIN use `vote_t = 4` (confirmed from `outputs/<track>/resolved_config.yaml`). Image's lower threshold accepts detections with less consensus agreement, favouring recall over precision relative to the text tracks at matched K. A matched-vote-threshold cross-track comparison at `vote_t = 4` would require re-aggregating image detections at the higher threshold; out of scope here. Paper text citing cross-track precision/recall trade-offs should flag this difference.

## 9. Paper implications

### 9.1 Track selection decision tree

For the paper's Methods / Deployment section, the three-track selection maps to three deployment scenarios:

- **Highest raw F1 at matched scope**: text-HIGH (F1 = 0.792 @ 50 m, post-recovery). No post-hoc human review needed; the pipeline's outputs can be cited directly. Cost $207.34 for the 55-map corpus (2026-06-12 audited manifest).
- **Cheapest adequate pipeline**: text-MIN (raw F1 = 0.762 @ 50 m, corrected 0.797). Sacrifices 0.030 raw F1 vs text-HIGH for a $176.90 / 85.3 % cost reduction and 2.71× fewer total tokens.
- **Highest post-review F1**: image (corrected F1 = 0.833 [0.824, 0.842] @ 50 m, post-recovery) or text-HIGH (corrected F1 = 0.827 [0.817, 0.837] @ 50 m, post-recovery) — the two tracks converge under human review (§4.2; cross-track-v2 confirms statistical indistinguishability). Requires a 630 – 1,028-candidate human review step; the effort of human review is comparable to the pipeline cost itself, so this path is only chosen when paper-grade corrected-F1 is the target. **API cost does not discriminate between the two**: under the 2026-06-12 audited manifests the image track is $200.83 and text-HIGH $207.34 — approximately equal (ratio 0.97 ×, a 3.1 % difference, within the ~5 % band) — so the choice between them should rest on operational rather than API-spend grounds. text-MIN remains materially cheaper at $30.44 but does not reach the same corrected-F1 ceiling (0.797).

### 9.2 Methodological contribution — raw vs corrected F1 gap is a track-specific property

The image track's raw-to-corrected F1 gap (+0.059 from 0.771 to 0.830 at 50 m) is larger than any plausible cross-track raw F1 gap within the three tracks. This suggests that the student-GT incompleteness on the 55-map corpus affects all three tracks but is currently quantified only for the image track. Paper text should make this asymmetry explicit rather than imply the 0.830 corrected F1 is achievable only by the image track.

### 9.3 Suggested paper text (Results — cross-track)

> On the 55-map generalisation corpus (8,541 Era 2 tiles, `gemini-3-flash-preview` proposer, `gemini-3-flash` verifier, K = 5 consensus at prob_t = 0.15; vote_t = 3 for the image track and vote_t = 4 for both text tracks), the raw F1 at a 50 m matching buffer is 0.774 (image), 0.792 (text-HIGH), and 0.762 (text-MIN). After per-candidate human review (1,030 candidates image; 630 candidates text-HIGH; 585 candidates text-MIN), the corrected F1 at 50 m is 0.833 [0.824, 0.842] (image), 0.827 [0.817, 0.837] (text-HIGH), and 0.797 [0.786, 0.808] (text-MIN). Cross-track-v2 paired-permutation tests on the corrected ground truth (`results/55maps-pairwise-permutation-v2/summary.md`) find image and text-HIGH statistically indistinguishable at R = 50 m (ΔF1 = −0.0060 ns); both significantly exceed text-MIN (ΔF1 = +0.0365 \*\*\* image vs text-MIN; ΔF1 = +0.0305 \*\*\* text-HIGH vs text-MIN). Cost per track (2026-06-12 audited-flex manifests): image $200.83, text-HIGH $207.34, text-MIN $30.44 — image and text-HIGH are at approximately equal API cost (ratio 0.97 ×, a 3.1 % difference), and both are ≈ 6.6 – 6.8 × the text-MIN cost; the image track's 92.87 % cache-hit rate offsets its ≈ 4 × larger token load.

### 9.4 Follow-up priority ordering

If one follow-up evaluation budget is available for the 55-map corpus:

1. **Paired image-vs-text permutation tests** — **DONE** (Session 77 2026-04-24). All 8 image-vs-text tests at 20 / 30 / 40 / 50 m now exist under `paired-image-vs-text-{high,min}-{20,30,40,50}m/`. See §5.2 and §5.3. Outcome: text-HIGH significantly beats image at every buffer; image and text-MIN converge at ≥ 40 m.
2. **Text-HIGH human review** — **DONE** (Session 78 2026-04-24). 630 candidates reviewed; multi-buffer corrected-F1 artefact at `results/55maps-text-high-generalisation/corrected-f1-multi-buffer/`. Text-HIGH corrected F1 at 50 m = 0.826 [0.816, 0.836], converging with image-track corrected 0.832 [0.822, 0.841] (ΔF1 = +0.006, overlapping CIs). Outcome confirmed the a priori estimate of 0.82 – 0.85 from the image-track gap. See §4.1 – §4.3.
3. **Extended buffer sweep for text tracks** — **DONE** (Session 77 2026-04-24). Text-HIGH and text-MIN at 75 / 100 / 125 m now exist at `outputs/55maps-text-{high,min}-generalisation/extended-buffer-eval/`. See §3.5. Outcome: both text tracks plateau by 75 m; buffer sensitivity is 3× lower than image track's corrected multi-buffer curve.

Remaining outstanding follow-up: none for the three tracks covered here. text-MIN human review (585-row multi-buffer; corrected F1 = 0.797) was added in cross-track-v2 commit `42ed1d32` (2026-05-03), closing the cross-track corrected-F1 parity gap. Future work would extend the comparison to the fourth corrected run (T=0.3 text-HIGH; corrected F1 = 0.844) — the canonical 4-run cross-track artefacts at `results/55maps-{mcc-v2-summary,pairwise-permutation-v2,attractor-pull-v2,ds-summary-v2,fp-classification}/` cover the temperature axis.

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

- `outputs/55maps-image-generalisation/cost_manifest.json` — $200.83.
- `outputs/55maps-text-high-generalisation/cost_manifest.json` — $207.34.
- `outputs/55maps-text-min-generalisation/cost_manifest.json` — $30.44.

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
    --bootstrap 10000 --seed 42 \
    --output-dir outputs/55maps-text-high-generalisation/extended-buffer-eval \
    --label "text-HIGH-K5-PV-extended"
```

Compute: ~4 minutes on sapphire for all 8 image-vs-text paired tests; ~1 minute for both extended-buffer evaluations. Zero API cost.

**Toolchain**: Python ≥ 3.11, GeoPandas ≥ 0.14, NumPy, pandas. Pinned versions in `requirements.txt`.

## Changelog

### 2026-08-03 — Session-126 C4 wave-6 repair

**Trigger**: the C4 wave-6 triage of this document (blind passes P1, P2 and P4, archived at
`reports/verification/c4-triage/blind-passes/wave6-pass-{P1,P2,P4}-2026-08-03.json`) adjudicated three
independent defect classes here: cost figures superseded by the 2026-06-12 token-load audit, recovery-era
values carried at the wrong third decimal, and reproducibility method text that no longer matches the
artefacts it describes. Repairs executed under **ruling 16** (differences within ~5 % are presented as
approximate equality, not as a new ordering) and **ruling 17** (living documents under the Document Revision
Policy are refreshed in place with a changelog entry; the historical SNAPSHOT-DIVERGENCE verdict stands in
the triage ledger). Rulings at `reports/verification/phase3-rulings-2026-07-31.md`.

**Cost and token figures — refreshed to the 2026-06-12 audited-flex manifests** (commit `8e142df9c`; §1, §6,
§9.1, §9.3, §10):

| Claim | Before | After |
|---|---:|---:|
| image total API cost | $364.70 | **$200.83** |
| image proposer / verifier | $353.62 / $11.08 | **$195.35 / $5.48** |
| image total tokens | 785.7 M | **770.3 M** |
| image cached tokens | 621.3 M | **621.1 M** |
| image prompt-cache hit rate | 91 % | **92.87 %** |
| image uncached input tokens | ~47 M | **≈ 47.7 M** |
| text-HIGH total API cost | $126.81 | **$207.34** |
| text-HIGH proposer / verifier | $113.96 / $12.84 | **$200.93 / $6.41** |
| text-HIGH total tokens | 393.6 M | **187.6 M** |
| text-MIN total API cost | $60.79 | **$30.44** |
| text-MIN proposer / verifier | $46.72 / $14.06 | **$23.36 / $7.08** |
| text-MIN total tokens | 88.8 M | **69.1 M** |
| image ÷ text-HIGH cost ratio | 2.9 × | **0.97 × — approximately equal (ruling 16)** |
| image ÷ text-MIN cost ratio | 6.0 × | **6.60 ×** |
| text-HIGH − text-MIN cost increment | +$66.02 | **+$176.90** |
| text-MIN saving vs text-HIGH | 52 % | **85.3 %** |
| text-HIGH ÷ text-MIN token ratio | 4.4 × | **2.71 ×** |
| §10 files-manifest line, text-HIGH manifest | $69.60 | **$207.34** |

**The conclusion that moved.** §9.1 and §9.3 previously concluded that text-HIGH delivered the same
corrected-F1 ceiling "at 2.9× lower API cost … making it the cost-efficient Pareto choice". Under the audited
manifests that ordering does not survive: image $200.83 and text-HIGH $207.34 differ by 3.1 %, inside the
~5 % approximate-equality band, so the corrected claim is **approximately equal API cost** — not a reversed
ranking in image's favour. text-MIN ($30.44) remains materially cheaper than both. API spend therefore no
longer discriminates between image and text-HIGH; the material cost decision on this corpus is text-MIN
versus the two HIGH-thinking tracks.

**Vintage history preserved** (§6's note previously read "Image and text-MIN verified 2026-04-24; text-HIGH
refreshed post-recovery 2026-05-03", which was honest about the document's mixed vintage and is the reason
the triage booked these rows as divergence rather than defect). The three tracks' manifests moved through
three generations:

1. **2026-04-18 / 04-19 originals** — image $364.6971 (`4c147af65`), text-MIN $60.7866 (`f0f7158e7`),
   text-HIGH $69.6017 (`4e5c5e5a3`). These are the figures this document quoted for image and text-MIN.
   They survive only in git.
2. **2026-05-03 post-recovery re-aggregation** — text-HIGH $126.8051 (`7f05f5298`, 10:49), text-MIN $93.4995
   (`b4a928d25`, 12:02), image $1061.0781 (`8699f456b`, 12:45). The document propagated only the text-HIGH
   value (`01b5441fb`, 11:26) and was never refreshed for the other two. Archived at
   `archive/superseded-cost-manifests-2026-06-12/`.
3. **2026-06-12 token-load audit** (`8e142df9c`) — all four 55-map manifests regenerated at audited flex
   pricing with thinking tokens billed as output. These are the figures now in the body. The audit's own
   propagation set (`reports/token-load-audit-2026-06-12.md` § 7) did not include this document, which is
   why the gap went unregistered for seven weeks.

**Stage-decomposition defect noted and removed.** §1 and §6 previously decomposed the text-HIGH total as
"pre-recovery $69.60 + $57.10 recovery + $0.10 cleanup + $0.58 FP-classify = $126.81". Those four addends sum
to $127.38, a $0.577 overshoot almost exactly equal to the $0.58 FP-classify term — an internal-arithmetic
defect independent of era, and one no mechanical recompute row could have caught (all four addends were
recompute-SKIPPED as anchor-unknown). The decomposition has been replaced wholesale by the audited
`.by_stage` figures, which sum exactly to each stated total on all three tracks.

**Recovery-value and rounding corrections** (P2 R5, R6; per P2 R9 the third-column note records whether the
3-decimal-place form a downstream document would cite actually moved):

| Claim | Location | Before | After | 3 d.p. form changed? |
|---|---|---:|---:|:---:|
| image vs text-MIN ΔF1 @ 50 m (v1 paired permutation) | §1, §3.4, §5.4 | +0.012 | **+0.011** | yes |
| image vs text-MIN ΔF1 @ 30 m (v1 paired permutation) | §3.2 | −0.041 | **−0.042** | yes (§5.4 already read −0.042) |
| image corrected F1 @ 150 m | §4 table | 0.857 | **0.856** | yes |
| image corrected F1 @ 100 m | §4.2 table | 0.854 | **0.853** | yes |
| text-HIGH corrected F1 CI lower bound @ 100 m | §4.2 table | 0.823 | **0.822** | yes |
| ΔF1 (image − text-HIGH) @ 100 m | §4.2 table and prose | +0.022 | **+0.021** | yes |
| image corrected F1 @ 50 m | §1, §4, §4.2, §9 | 0.833 | 0.833 | **no** — the sibling `corrected-f1-multi-buffer/report.md` 4 d.p. fix (0.8333 → 0.8332) does not move it |
| image candidates human-reviewed at 50 m | §7 table, §9.3 | 1,029 | **1,030** | n/a |
| image mound labels at 50 m | §7 | 474 | **475** | n/a |
| image not-mound labels at 50 m | §7 | 555 | 555 | **no change** |
| text-MIN candidates human-reviewed | §1, §4, §7, §9.3, §9.4 | 586 | **585** | n/a |

The §7 count repairs are coupled: 1,030 / 475 / 555 is the union of `human-review.csv` and
`human-review-multi-buffer.csv` at `buffer_metres == 50`, including candidate 5777's `not_mound → mound`
flip; the not-mound side is invariant across candidate 2397's promotion, which is why 555 does not move. The
text-MIN 586 was a header-inclusive `wc -l` of a 585-row CSV; the swap was applied to every restatement in
this document, not only §7, because §1, §4, §9.3 and §9.4 all quote the same count. A derivation note has
been added to the §7 table because none of these three numbers exists as a scalar in any tracked artefact
(ruling 15 named-family case).

**Reproducibility method text** (P4 R3): §3.5 "(1,000 iterations, seed 42)" → "(10,000 iterations, BCa, seed
42)"; §3.6 "1,000-iter bootstrap CIs" → "10,000-iter BCa bootstrap CIs"; §11 `--bootstrap 1000` →
`--bootstrap 10000`. The CI tables in both sections were refreshed to N = 10,000 BCa values on 2026-05-03
while the method sentences and the copy-pasteable command were not, so the document had been instructing a
replicator to run a configuration that cannot reproduce the intervals printed beside it. Verified against
`_metadata.bootstrap` in `outputs/55maps-{image,text-high,text-min}-generalisation/{full,extended}-buffer-eval/evaluation.json`,
all of which record `{n_iterations: 10000, seed: 42, method: BCa, library: scipy.stats.bootstrap}`.

**What did NOT change**: every F1, precision, recall, MCC and confidence-interval figure other than the six
third-decimal corrections listed above; every paired-permutation p-value and every significance verdict
(v1 and v2 alike); the raw-F1 ordering at 50 m (text-HIGH 0.792 > image 0.774 > text-MIN 0.762); the
corrected-GT ordering at 50 m (image 0.833 ≈ text-HIGH 0.827 > text-MIN 0.797) and the finding that image
and text-HIGH are statistically indistinguishable there; the detection volumes; the tile-level MCC ordering;
and the §8 caveat register. The 2026-06-12 audit moved only the dollar axis.

**Residues flagged but NOT repaired in this pass** (outside the adjudicated mandate; recorded here so a
later pass can pick them up): §3.5's image clause "corrected F1 0.832 → 0.854 from 50 m → 125 m" still
carries pre-recovery endpoints (post-recovery: 0.833 → 0.855; the stated ΔF1 = +0.022 is correct either
way); §9.2's "+0.059 from 0.771 to 0.830 at 50 m" likewise quotes pre-recovery endpoints (post-recovery:
0.774 → 0.833, same +0.059); §9.4 item 2 still quotes the pre-recovery pair 0.826 [0.816, 0.836] and 0.832
[0.822, 0.841]; and §4.2's "CI overlap? yes (partial)" cell at R = 100 m is incorrect at both the old and
the new values — image [0.845, 0.862] and text-HIGH [0.822, 0.842] are disjoint — but changing it would move
a conclusion, which this pass is not authorised to do.

**Commit**: (this commit).

### 2026-05-03 — Original publication

Document created 2026-04-24 (Session 76) as a hand-authored synthesis of three per-track `evaluation.json`
files and the twelve paired-permutation JSONs; no new data generation or statistical testing. It reached the
state frozen here through the 2026-05-03 cross-track-v2 refresh (commit `42ed1d32`, body last touched at
`95111a3f1`), which added the text-MIN corrected-F1 track, propagated the post-recovery T=0.7 detection set,
and rewrote §4 – §5 for corrected-GT significance. Cost figures at that point were mixed-vintage (see the
2026-08-03 entry) and the document carried neither a revision banner nor a changelog.
