# Production Retest Summary (340-Tile Corpus)

> **Last revised**: 2026-10-06 (the Phase 2c text-track library contrast withdrawn, its five arms having sent identical requests, E90; every p-value restated on the paired tile-swap permutation test, D42, which also flips two raw-α verdicts; Phase 2c's H8 null is the image track's alone; the retest's example orders recorded, E92; § 14.5's "Gemini 2.0 Flash" corrected). Prior: 2026-06-05 (model-of-record corrected `gemini-2.0-flash` → `gemini-3-flash`). See [§ Changelog](#changelog) for revision history.

**Generated**: 2026-03-21. **Level-up**: 2026-04-24 (Session 76).
**Corpus**: 340 tiles (569 ground truth mounds, 4 map sheets; Era 1 scope — see `results/evaluation-scopes.md`).
**Baseline**: Phase 3 holdout set (60 tiles) — see `results/phase3d-pilot-results.md`.
**Model**: Gemini 3 Flash (`gemini-3-flash`, resolved to `gemini-3-flash-preview`). **Same model family as the Era 2 / 3 runs** — the cross-era difference is **tile scope, not model version** (see §12 Caveat 3 and `results/evaluation-scopes.md`).
**Bootstrap**: 1,000 iterations, tile-level resampling, seed 42.
**Spatial matching**: 20 m tolerance (Hungarian one-to-one).

**Cross-reference** — Phase 2b has its own dedicated narrative: `results/retest/phase2b/analysis_summary.md` (Session 75 item 3; commit `e8c46809`). Phase 2b numbers in §4 below are preserved for narrative continuity; the dedicated analysis_summary is the paper-citation source for Phase 2b-specific claims.

## 1. Executive summary

This is the multi-phase production retest on the Era 1 340-tile corpus, spanning Phase 2a (H1 Modality), Phase 2b (H7 Temperature, two tracks), Phase 2c (H8 Library Composition), Phase 2d (H5 Negation Text), Phase 2e (H4 Example Ordering), Phase 3a (Consensus Voting, both tracks + HIGH-text replication), Phase 3a-HIGH Text Track, and Phase 3c (H9 Diversity Text Track, partial). All single-pass phases run K = 1–3 replicates per condition; Phase 3a consensus phases run K = 30.

**Headline findings across the retest**:

- **Best non-PV operating point of the entire retest**: **Replication HIGH consensus 21-of-30 at F1 = 0.7705** [0.725, 0.811]. This is the highest F1 in the 340-tile retest and comes from the HIGH-thinking + consensus combination.
- **Phase 2a H1 Modality**: text-only conditions outperform image-only. Best single-pass: **brief-text at F1 = 0.5518** [0.477, 0.595]; brief-text > image-only is significant (ΔF1 = +0.088, p = 0.0055).
- **Phase 2b H7 Temperature**: optimum is T = 0.0 on the image track (F1 = 0.5869 [0.541, 0.633]) and T = 0.0 or T = 0.3 tied on the text track (F1 = 0.6048 / 0.6065; ΔF1 = −0.003, p = 0.916). Clear monotonic decline on image track from T = 0.0 to T = 1.3. See the dedicated `phase2b/analysis_summary.md` for the paper-facing narrative.
- **Phase 2c H8 Library**: no significant library-composition differences on the image track, the only track whose library reached the model. ~~Single-track significant: scale-4 > plus-hp on text (ΔF1 = +0.013, p = 0.001).~~ [WITHDRAWN 2026-10-06: a text-only request transmits no exemplar, so the five text arms sent identical requests and the text track tested no library (E90; Obs 496, Obs 498). This contrast is between two runs of one configuration, and its p = 0.001 was a false positive of the retired bootstrap (paired tile-swap permutation p = 0.0588, BH within phase 0.588; D42).] The image-track null is the preregistered origin of the library-design-axis closure reported in `h8-v2/analysis_summary.md`.
- **Phase 2d H5 Negation Text**: no significant F1 differences on either track; terse > verbose on recall only (text track, p = 0.003).
- **Phase 2e H4 Example Ordering**: **canonical-last is the best single-pass F1 of the entire retest at 0.6314** [0.587, 0.672], from a single run; canonical-last > random is significant (ΔF1 = +0.060, p = 0.0019). Attention-recency bias hypothesis supported. [Qualified 2026-10-06: H4's registered contrast, canonical-last against canonical-first, is not significant (p = 0.137; H4 not rejected in the family), and on the Era-1 board canonical-last shares Tier 1 with 14 other cells. The orders did reach the model (`reports/phase2e-ordering-check-2026-10-05.md`); canonical-last was sent as nulls, hard positives, then canonical examples (E92).]
- **Phase 3a Consensus**: consensus voting improves F1 by +0.11 to +0.21 over single-pass baselines. Image + text consensus both peak at ~F1 = 0.69; image-track peak at T = 0.7 (F1 = 0.6909), text-track peak at T = 0.3 (F1 = 0.6921).
- **Phase 3a HIGH Text Track (single-pass)**: HIGH-thinking *degrades* single-pass F1 by ~0.13 vs MINIMAL (T = 0.3: 0.478 HIGH vs 0.610 MINIMAL) — the over-inclusive-detection cost of HIGH thinking without consensus.
- **Phase 3a Replication** (HIGH-thinking with consensus): the same HIGH-thinking that hurt single-pass *recovers* under K = 30 consensus, producing the top-of-table F1 = 0.7705. The diversity of HIGH-thinking runs provides the variance consensus filters need.

**Paper-facing headline claim**: "On the Era 1 340-tile corpus at 20 m matching tolerance, the production retest validates a canonical best-configuration stack: canonical-last example ordering (F1 = 0.631, one single-pass run), T = 0.0 temperature on image and T = 0.0–0.3 on text, and K = 30 HIGH-thinking consensus voting (F1 = 0.771). Library composition (tested on the image track only: the text arms transmitted no library, E90) and negation-text style have no significant effect. HIGH-thinking degrades single-pass F1 but recovers dramatically under consensus — a diversity-dividend finding that carries to Phase 3a image and text consensus in the paper's detection-pipeline Results section."

## 2. Methods

- **Evaluation corpus**: 340 tiles at 512 px (Era 1 scope). 569 ground-truth mounds across 4 map sheets.
- **Matching protocol**: Hungarian one-to-one candidate-to-GT matching at 20 m spatial tolerance (`scripts/10_evaluate_detections_bootstrap.py`).
- **Bootstrap**: 1,000 iterations, tile-level resampling, seed 42. Bootstrap CIs for individual runs are drawn from `results/pv/all-bootstrap-cis.json` where available; otherwise computed per-run.
- **Pairwise comparisons**: paired contrasts per phase, on the first run of each condition. The p-values in this document are the paired tile-swap permutation test's (10,000 permutations, seed 42, 20 m), restated on 2026-10-06 under PI ruling D42 from the `permutation_retest` blocks of `pairwise-bootstrap-comparisons.json`. The p-values first published here were read off the bootstrap (twice the minority tail, floored at 1/B), which D42 retired: it rejects between outputs that differ on a few tiles in one direction, identical requests included (`reports/retest-bootstrap-check-2026-10-05.md`). Bootstrap CIs remain in use. Raw p-values are reported in §11 with BH within each phase: 21 / 70 F1 comparisons are significant at raw p < 0.05 (24 under the retired bootstrap), and all 21 survive BH.
- **Example order** (added 2026-10-06): the image arms of Phases 2a-2d were sent in canonical-first order (canonical examples, then hard, then null), not the configuration order the February 60-tile programme used, and Phase 2e's `canonical-last` was sent as nulls, hard positives, then canonical examples (erratum E92).
- **Consensus protocol**: each Phase 3a run aggregates K = 30 replicates at the condition's temperature; consensus vote thresholds t ∈ {1, …, K} are swept and the best F1 per condition is reported. N = 5, N = 10, N = 30 variants are in per-track `consensus-analysis-summary.md` artefacts.

## 3. Phase 2a: H1 Modality (5 conditions)

| Condition | F1 | 95 % CI | P | R | K |
|-----------|----:|:------:|----:|----:|---:|
| brief-text | 0.5518 | [0.477, 0.595] | 0.4336 | 0.7588 | 3 |
| brief-text-image | 0.5220 | [0.469, 0.564] | 0.4392 | 0.6432 | 3 |
| verbose-text | 0.5016 | [0.443, 0.556] | 0.3928 | 0.6939 | 3 |
| verbose-text-image | 0.5169 | [0.467, 0.560] | 0.4343 | 0.6382 | 3 |
| image-only | 0.4693 | [0.401, 0.502] | 0.3829 | 0.6061 | 3 |

**Key finding**: Text-only conditions outperform image-only, consistent with Phase 3 pilot results. Brief-text achieves the highest mean F1 (0.5518). The brief-text vs image-only difference is significant (ΔF1 = +0.088, p = 0.0055). Adding images to text does not improve F1 and tends to reduce recall. No significant difference between brief-text and verbose-text (p = 0.105), though brief-text trends higher.

## 4. Phase 2b: H7 Temperature (2 tracks × 5 temperatures)

**See dedicated analysis summary**: `results/retest/phase2b/analysis_summary.md` (Session 75 item 3; commit `e8c46809`) — paper-citation source for Phase 2b claims.

### 4.1 Track 1 — Image

| Temperature | F1 | 95 % CI | P | R | K |
|-------------|----:|:------:|----:|----:|---:|
| T0.0 | 0.5869 | [0.541, 0.633] | 0.4987 | 0.7130 | 3 |
| T0.3 | 0.5751 | [0.528, 0.612] | 0.4883 | 0.6994 | 3 |
| T0.7 | 0.5367 | [0.489, 0.580] | 0.4523 | 0.6599 | 3 |
| T1.0 | 0.5269 | [0.474, 0.561] | 0.4396 | 0.6574 | 3 |
| T1.3 | 0.4903 | [0.459, 0.540] | 0.4062 | 0.6184 | 3 |

**Key finding**: T = 0.0 achieves the best image-track F1. T = 0.0 is significantly better than T = 0.7 (p = 0.0026), T = 1.0 (p = 0.0008), and T = 1.3 (p < 0.0001). T = 0.0 vs T = 0.3 is not significant (p = 0.32). Clear monotonic decline from T = 0.0 to T = 1.3.

### 4.2 Track 2 — Text

| Temperature | F1 | 95 % CI | P | R | K |
|-------------|----:|:------:|----:|----:|---:|
| T0.3 | 0.6065 | [0.553, 0.654] | 0.4908 | 0.7934 | 3 |
| T0.0 | 0.6048 | [0.547, 0.655] | 0.4870 | 0.7978 | 3 |
| T0.7 | 0.5842 | [0.521, 0.636] | 0.4606 | 0.7984 | 3 |
| T1.3 | 0.5442 | [0.487, 0.603] | 0.4252 | 0.7557 | 3 |
| T1.0 | 0.5335 | [0.432, 0.583] | 0.4148 | 0.7483 | 3 |

**Key finding**: T = 0.0 and T = 0.3 are essentially tied at the top (ΔF1 = −0.003, p = 0.916). Both significantly outperform T = 1.0 (p = 0.0002–0.0008) and T = 1.3 (p = 0.0018–0.0034). T = 0.7 is not significantly different from T = 0.0 or T = 0.3 but is significantly better than T = 1.0 (p = 0.0055). Optimal text-track temperature: T = 0.0–0.3.

## 5. Phase 2c: H8 Library Composition (2 tracks + exploratory)

### 5.1 Track 1 — Image (5 conditions)

| Condition | F1 | 95 % CI | P | R | K |
|-----------|----:|:------:|----:|----:|---:|
| plus-hp | 0.5983 | [0.546, 0.646] | 0.5091 | 0.7254 | 1 |
| scale-8 | 0.5872 | [0.542, 0.633] | 0.4993 | 0.7124 | 1 |
| scale-4 | 0.5841 | [0.534, 0.631] | 0.4864 | 0.7310 | 1 |
| canonical | 0.5755 | [0.528, 0.623] | 0.5056 | 0.6679 | 1 |
| pure-positive-canon | 0.5656 | [0.520, 0.608] | 0.4905 | 0.6679 | 1 |

**Key finding**: No significant pairwise F1 differences among any image-track library conditions (all p > 0.09; first published as "all p > 0.19", which the bootstrap's own lowest value, 0.076 for plus-hp vs pure-positive-canon, did not support). The pipeline is robust to library composition on the image track.

### 5.2 Track 2 — Text (5 conditions)

| Condition | F1 | 95 % CI | P | R | K |
|-----------|----:|:------:|----:|----:|---:|
| scale-4 | 0.6089 | [0.552, 0.659] | 0.4909 | 0.8015 | 1 |
| scale-8 | 0.6065 | [0.548, 0.656] | 0.4892 | 0.7978 | 1 |
| canonical | 0.6039 | [0.545, 0.654] | 0.4838 | 0.8033 | 1 |
| pure-positive-canon | 0.6039 | [0.546, 0.653] | 0.4859 | 0.7978 | 1 |
| plus-hp | 0.5963 | [0.540, 0.648] | 0.4802 | 0.7866 | 1 |

~~**Key finding**: Minimal sensitivity to library composition on the text track. The only significant comparison is plus-hp vs scale-4 (ΔF1 = −0.013, p = 0.001), a tiny effect driven by scale-4's marginally higher recall. All five conditions cluster within a 0.013 F1 range.~~

[WITHDRAWN 2026-10-06: this is not a library test. With `include_example_images: false` a request transmits no exemplar, so these five arms sent identical requests (one instruction, T = 0.0, minimal thinking, `gemini-3-flash`, commit `5a57f586e`), which also repeat Phase 2b's T0.0 text arm (§ 4.2): six runs of one configuration (E90; `reports/manipulation-check-2026-10-05.md` § B.1). The table above is a run-to-run spread, 0.5963–0.6089 F1, and the plus-hp vs scale-4 contrast is a false positive of the retired bootstrap between replicates: the two runs differ on five tiles, all in one direction (paired tile-swap permutation p = 0.0588, BH within phase 0.588; D42; Obs 498). Decision 16 had already called this test meaningless, and the February programme skipped it.]

### 5.3 Exploratory — HP Scaling (Image, pure-positive variants)

| Condition | F1 | 95 % CI | P | R | K |
|-----------|----:|:------:|----:|----:|---:|
| pure-positive-4hp | 0.5985 | [0.550, 0.646] | 0.5084 | 0.7273 | 1 |
| pure-positive-2hp | 0.5721 | [0.521, 0.618] | 0.4738 | 0.7217 | 1 |
| pure-positive-canon | 0.5676 | [0.521, 0.609] | 0.4945 | 0.6660 | 1 |

**Key finding**: No significant F1 differences (all p > 0.14). Increasing hard-positive examples does not reliably improve detection.

## 6. Phase 2d: H5 Negation Text (2 tracks)

### 6.1 Track 1 — Image

| Condition | F1 | 95 % CI | P | R | K |
|-----------|----:|:------:|----:|----:|---:|
| terse | 0.6056 | [0.564, 0.646] | 0.5142 | 0.7365 | 1 |
| verbose | 0.6027 | [0.554, 0.647] | 0.5202 | 0.7161 | 1 |

**Key finding**: No significant difference (ΔF1 = +0.003, p = 0.88). Negation text style has negligible effect on the image track.

### 6.2 Track 2 — Text

| Condition | F1 | 95 % CI | P | R | K |
|-----------|----:|:------:|----:|----:|---:|
| terse | 0.5984 | [0.537, 0.651] | 0.4850 | 0.7811 | 1 |
| verbose | 0.5834 | [0.525, 0.636] | 0.4887 | 0.7236 | 1 |

**Key finding**: No significant F1 difference (ΔF1 = +0.016, p = 0.426), though terse negation text achieves significantly higher recall (p = 0.003). Terse trends better but the F1 difference does not reach significance.

## 7. Phase 2e: H4 Example Ordering (4 conditions)

| Condition | F1 | 95 % CI | P | R | K |
|-----------|----:|:------:|----:|----:|---:|
| canonical-last | 0.6314 | [0.587, 0.672] | 0.5325 | 0.7755 | 1 |
| config-default | 0.6047 | [0.559, 0.653] | 0.5193 | 0.7236 | 1 |
| canonical-first | 0.5983 | [0.546, 0.646] | 0.5091 | 0.7254 | 1 |
| random | 0.5710 | [0.519, 0.618] | 0.4732 | 0.7199 | 1 |

**Key finding**: Canonical-last achieves the best single-run F1 of 0.6314 — the highest non-consensus score in the entire production retest. Canonical-last is significantly better than random (ΔF1 = +0.060, p = 0.0019). ~~Config-default also significantly beats random (ΔF1 = +0.034, p = 0.046).~~ [WITHDRAWN 2026-10-06: on the paired tile-swap permutation test, p = 0.0563 (BH within phase 0.169; D42); not significant.] Canonical-last vs config-default and canonical-first are not significant (p = 0.186 and p = 0.137 respectively). Placing the canonical example last in the few-shot sequence improves performance, consistent with recency bias in the attention mechanism. [Qualified 2026-10-06: each arm is a single run, and the canonical-last vs canonical-first contrast, H4's registered test, is not significant; "improves performance" holds against random only. On the Era-1 board canonical-last leads numerically and shares Tier 1 with 14 other cells.]

**How the arms were sent** (added 2026-10-06; erratum E92). The four orderings reached the model: an offline replay of the recorded commit's batch builder gives four requests differing only in example order, and the arms' outputs agree on at most 5 % of tiles, against 91–99 % for identical requests (`reports/phase2e-ordering-check-2026-10-05.md`). `canonical-last` was sent as `[null×3, HP×4, C+×4, C−×2]`, not the study definition's `[HP, null, C+, C−]`; the canonical examples were last, as registered. The study definition's "baseline used in all prior phases" and "reused from Phase 2c" hold for the February 60-tile programme only: in this retest, the prior phases' image arms ran canonical-first, so the arm continuous with them is `canonical-first` (Phase 2c `plus-hp` and Phase 2e `canonical-first` are one request, and their outputs agree on 99.7 % of tiles), and `config-default` was run afresh.

## 8. Phase 3a: Consensus Voting

Detailed sweep results are in the per-track consensus analysis summaries:

- Image track: `results/retest/phase3a-consensus/track1-image/consensus-analysis-summary.md`.
- Text track: `results/retest/phase3a-consensus/track2-text/consensus-analysis-summary.md`.
- Replication (HIGH vs minimal thinking): `results/retest/phase3a-consensus/replication/consensus-analysis-summary.md`.

### 8.1 Cross-Track Comparison (Best N = 30 consensus per track)

| Track | Temp | Threshold | F1 | 95 % CI | P | R |
|-------|------|-----------|----:|:------:|----:|----:|
| Replication HIGH | — | 21-of-30 | 0.7705 | [0.725, 0.811] | 0.7846 | 0.7570 |
| Replication HIGH | — | 25-of-30 | 0.7583 | [0.710, 0.801] | 0.8646 | 0.6753 |
| Replication minimal | — | 25-of-30 | 0.7033 | [0.652, 0.750] | 0.6729 | 0.7365 |
| Text | T0.3 | 23-of-30 | 0.6921 | [0.637, 0.739] | 0.6261 | 0.7737 |
| Text | T0.7 | 24-of-30 | 0.6915 | [0.639, 0.741] | 0.6488 | 0.7403 |
| Image | T0.7 | 18-of-30 | 0.6909 | [0.649, 0.730] | 0.6935 | 0.6883 |
| Text | T1.0 | 22-of-30 | 0.6860 | [0.633, 0.735] | 0.6506 | 0.7254 |
| Image | T1.0 | 18-of-30 | 0.6803 | [0.636, 0.721] | 0.7166 | 0.6475 |
| Image | T0.3 | 22-of-30 | 0.6661 | [0.625, 0.706] | 0.6519 | 0.6809 |

**Key findings**:

- Consensus voting consistently improves over single-run baselines (+0.11 to +0.21 ΔF1).
- **Best consensus: Replication HIGH 21-of-30 at F1 = 0.7705** — the highest F1 in the entire study (non-PV). HIGH thinking with consensus produces a large gain over minimal thinking consensus (ΔF1 = +0.068, p = 0.0004).
- Text and image tracks achieve comparable consensus F1 (~0.69), but via different precision-recall trade-offs: image consensus is higher precision, text consensus is higher recall.
- Image-track consensus peaks at T = 0.7 (F1 = 0.6909), while text-track consensus peaks at T = 0.3 (F1 = 0.6921) — both outperforming T = 1.0.
- Consensus significantly outperforms the best single-pass condition: image consensus T = 0.7 18-of-30 vs canonical-last single-pass gives ΔF1 = +0.060 (p = 0.0014).

## 9. Phase 3a-HIGH Text Track

**Status**: 90 / 90 runs complete (30 runs × 3 temperatures). Bootstrap CIs computed for all 90 runs.

| Temperature | Mean F1 | P | R | K |
|-------------|--------:|----:|----:|---:|
| T0.3 | 0.4776 | 0.3450 | 0.7797 | 30 |
| T0.7 | 0.4248 | 0.2948 | 0.7641 | 30 |
| T1.0 | 0.4107 | 0.2829 | 0.7534 | 30 |

**Key finding**: HIGH-thinking single-pass runs on the text track produce *substantially worse* F1 than minimal-thinking runs (cf. Phase 3a text T = 0.3 at F1 = 0.610 vs HIGH T = 0.3 at F1 = 0.478). This replicates the Phase 3d pilot finding that HIGH thinking degrades single-pass precision by generating verbose, over-inclusive detections. However, the replication consensus results (above) show that HIGH thinking *recovers dramatically* under consensus voting — the diversity of HIGH-thinking runs provides the variance that consensus needs to filter signal from noise.

## 10. Phase 3c: H9 Diversity (Text Track)

**Status**: 100 / 100 output runs complete (20 profiles × 5 runs). Bootstrap CIs computed for 60 / 100 runs. Image track: 83 / 100 output runs complete.

Partial results from the 60 bootstrapped text-track runs across 20 diversity profiles (4 strategy groups: A = prompt permutation, B = vocabulary substitution, D = temperature diversity, E = example permutation):

| Strategy Group | Profiles | Runs (bootstrapped) | Mean F1 |
|----------------|----------|---------------------|--------:|
| A (prompt) | h9-A-p1 to p5 | 15 | 0.4227 |
| B (vocabulary) | h9-B-v1 to v5 | 14 | 0.4105 |
| D (temperature) | h9-D-t1 to t5 | 18 | 0.4335 |
| E (example) | h9-E-p1 to p5 | 13 | 0.4217 |

**Key finding**: All diversity profiles produce single-run F1 values substantially below the canonical single-pass conditions (F1 ~0.42 vs ~0.55–0.61), as expected since diversity profiles deliberately deviate from optimised parameters. The value of these runs lies in their consensus-voting potential — whether diverse pools outperform homogeneous pools at the same pool size remains to be tested once all bootstrap CIs are available (Obs 148 re: variance stabilisation). Full analysis is deferred until all 100 runs are bootstrapped.

[PENDING: Consensus voting sweep over diversity pools]
[PENDING: Bootstrap CIs for remaining 40 text-track runs]

## 11. Pairwise Comparison Highlights

21 significant F1 comparisons (raw p < 0.05, paired tile-swap permutation
test) out of 70 total pairwise tests, and all 21 survive Benjamini–Hochberg
(BH) correction within their phase. As first published (2026-03-21), this
section read 24 significant on the bootstrap p-value that PI ruling D42
retired; those values are kept in the last column of each table. Three
verdicts change: § 11.2's T0.7 > T1.3, § 11.4's only row (withdrawn: its
arms are replicates, E90) and § 11.5's config-default > random. Source:
`pairwise-bootstrap-comparisons.json`, each row's `permutation_retest` block
(10,000 permutations, seed 42, 20 m, the March inputs;
`reports/retest-bootstrap-check-2026-10-05.md` § W2.4). A p of 0 is written
"< 0.0001".

### 11.1 Phase 2a — H1 Modality (3 significant)

| Comparison | ΔF1 | p | BH within phase | p, retired bootstrap |
|------------|----:|---:|---:|---:|
| brief-text > image-only | +0.088 | 0.0055 | 0.030 | 0.004 |
| brief-text-image > image-only | +0.065 | 0.0090 | 0.030 | 0.006 |
| verbose-text-image > image-only | +0.063 | 0.0069 | 0.030 | 0.004 |

### 11.2 Phase 2b T1 — H7 Temperature, Image (5 significant; 6 as first published)

| Comparison | ΔF1 | p | BH within phase | p, retired bootstrap |
|------------|----:|---:|---:|---:|
| T0.0 > T0.7 | +0.050 | 0.0026 | 0.0065 | 0.002 |
| T0.0 > T1.0 | +0.064 | 0.0008 | 0.0027 | 0.001 |
| T0.0 > T1.3 | +0.085 | < 0.0001 | < 0.0001 | 0.001 |
| T0.3 > T1.0 | +0.050 | 0.0083 | 0.017 | 0.006 |
| T0.3 > T1.3 | +0.071 | 0.0006 | 0.0027 | 0.001 |
| T0.7 > T1.3 (not significant; first published as significant) | +0.035 | 0.0588 | 0.094 | 0.042 |

### 11.3 Phase 2b T2 — H7 Temperature, Text (5 significant)

| Comparison | ΔF1 | p | BH within phase | p, retired bootstrap |
|------------|----:|---:|---:|---:|
| T0.0 > T1.0 | +0.093 | 0.0008 | 0.004 | 0.001 |
| T0.0 > T1.3 | +0.057 | 0.0034 | 0.0085 | 0.004 |
| T0.3 > T1.0 | +0.096 | 0.0002 | 0.002 | 0.001 |
| T0.3 > T1.3 | +0.060 | 0.0018 | 0.006 | 0.006 |
| T0.7 > T1.0 | +0.072 | 0.0055 | 0.011 | 0.004 |

### 11.4 Phase 2c T2 — H8 Library, Text (WITHDRAWN 2026-10-06; first published as 1 significant)

| Comparison | ΔF1 | p | BH within phase | p, retired bootstrap |
|------------|----:|---:|---:|---:|
| ~~scale-4 > plus-hp~~ | +0.013 | 0.0588 | 0.588 | 0.001 |

[WITHDRAWN 2026-10-06: not a library contrast. A text-only request
transmits no exemplar, so the five Phase 2c text arms sent identical
requests, which also repeat Phase 2b's T0.0 text arm (E90; Obs 496,
Obs 498). This row compares two runs of one configuration that differ on
five of 340 tiles, all in one direction; the retired bootstrap floors its p
at 1/B whenever that happens, and the exact tile-swap null gives 2/32.]

### 11.5 Phase 2e — H4 Ordering (1 significant; 2 as first published)

| Comparison | ΔF1 | p | BH within phase | p, retired bootstrap |
|------------|----:|---:|---:|---:|
| canonical-last > random | +0.061 | 0.0019 | 0.011 | 0.002 |
| config-default > random (not significant; first published as significant) | +0.034 | 0.0563 | 0.169 | 0.046 |

### 11.6 Phase 3a T1 — Consensus Voting, Image (2 significant)

| Comparison | ΔF1 | p | BH within phase | p, retired bootstrap |
|------------|----:|---:|---:|---:|
| T0.3 > T1.0 | +0.075 | 0.0005 | 0.0015 | 0.001 |
| T0.7 > T1.0 | +0.054 | 0.0070 | 0.0105 | 0.008 |

### 11.7 Phase 3a T2 — Consensus Voting, Text (2 significant)

| Comparison | ΔF1 | p | BH within phase | p, retired bootstrap |
|------------|----:|---:|---:|---:|
| T0.3 > T0.7 | +0.038 | 0.024 | 0.036 | 0.024 |
| T0.3 > T1.0 | +0.071 | 0.0001 | 0.0003 | 0.001 |

### 11.8 Phase 3a — Cross-Condition (3 significant)

| Comparison | ΔF1 | p | BH within phase | p, retired bootstrap |
|------------|----:|---:|---:|---:|
| minimal > high (single-run) | +0.139 | < 0.0001 | (one test) | 0.001 |
| consensus image T0.7 18-of-30 > canonical-last single-pass | +0.060 | 0.0014 | (one test) | 0.001 |
| HIGH consensus 21-of-30 > minimal consensus 25-of-30 | +0.068 | 0.0004 | (one test) | 0.001 |

## 12. Caveats / risk register

1. **T = 0.0 (image) vs T = 0.3 (text) crossover**: the tracks have different optimal temperatures (working-notes §"Five design decisions that cross over", line 6095+). This is one of the paper's practitioner-relevant findings — temperature should not be set by a global rule; track-specific optima matter.
2. **FDR correction deferred**: §11 reports 24 / 70 raw p < 0.05 comparisons. [Updated 2026-10-06: §11 now reports 21 / 70 on the permutation test (D42), each with its BH-adjusted p within phase; all 21 survive.] FDR-corrected contrasts are **not yet in this doc**; they appear in per-phase permutation analyses (e.g., `results/cross-hypothesis-library/permutation-t4/fdr_summary.json` for the Phase 2c library-composition axis). Paper text should cite FDR-corrected results from those artefacts rather than the raw p-values here.
3. **Model version (corrected 2026-06-05)**: this retest used **`gemini-3-flash`** (resolved to `gemini-3-flash-preview`), the **same model family** as the Era 2 / Era 3 runs — confirmed by every run meta (`configuration.model` + `cost_estimate.pricing_used.model`) and the source config `prompts/configs/detect_brief-text.json` (`gemini-3-flash` since 2026-01-09); **zero** retest artefacts record any 2.x model, and the project post-dates Gemini 3's 2025-11-18 release. The earlier claim that this retest used `gemini-2.0-flash` was an unsourced prose error (see [§ Changelog](#changelog)). **Consequence**: cross-era comparisons are **not** confounded by model version — the only cross-era difference is **tile scope** (Era 1 = 340 × 512 px; Era 2 / 3 are smaller, strictly nested subsets). See `results/evaluation-scopes.md`.
4. **Pending sections** (§13): Phase 3a-HIGH image-track consensus, Phase 3c image-track diversity, Phase 3c consensus sweep over diversity pools. Not blocking for paper if the paper's Phase 3a discussion rests on the Era 2 consensus sweeps (`results/phase3a-image-matrix/consensus-analysis-summary.md`, `results/phase3a-text-matrix/secondary_effects.md`) rather than this Era 1 retest — a choice about **tile scope and recency**, not model (both eras are `gemini-3-flash`).
5. **K = 1 single-pass rows**: Phase 2c / 2d / 2e use K = 1 (single replicate) per condition; the per-condition CIs are tile-level only, not replicate-level. Phase 2a / 2b use K = 3.
6. **[PENDING] sections in §13** are genuine open items, not level-up gaps. They do not block paper finalisation because the Era 2 / Era 3 analyses on `gemini-3-flash` are the paper's citation target.
7. **Dedicated Phase 2b artefact supersedes narrative §4**: `results/retest/phase2b/analysis_summary.md` is the paper-citation source for Phase 2b claims; §4 here is retained for continuity with the rest of the retest narrative but is not paper-primary.
8. **Level-up preserved all existing content**: §§3–11 tables and key-finding paragraphs are preserved verbatim from the pre-level-up version. The level-up added §§1, 2, 12, 14, 15, 16, 17 only.
9. **The Phase 2c text track is not a library test** (added 2026-10-06): its five arms are replicates of one configuration (E90). The Era-1 single-pass board's 36 cells are 26 transmitted configurations, its 15-cell Tier 1 is 9, and six Tier-1 cells are this one text configuration (`reports/manipulation-check-2026-10-05.md` § B.5).
10. **p-values compare two outputs, not two configurations** (added 2026-10-06): the permutation test treats each arm's single run as fixed, so a significant p says the two outputs differ; whether the configurations differ needs the run-to-run floor (PI rulings D45, D46; tracker W2.7). Every § 11 row but the two consensus rows compares one run per arm.

## 13. Observation cross-references

This document predates Obs 262–273 (Session 74 era). Relevant back-references for paper triangulation:

- **Obs 155** (Phase 3 holdout-set statistical-power shortage): the motivating observation for running this production retest; cited in §Context of the original doc.
- **Obs 116 / 177 / 209** (T = 1.0 sweep closure): the narrative line from §4.1 (T = 0.0 image optimum; monotonic decline through T = 1.3) is the Era 1 precursor to the Era 2 / UNINTENDED-T1.0 disposition (see `outputs/h11/consensus-384-UNINTENDED-T1.0/README.md`).
- **Obs 240** (45-pair cross-hypothesis library-design null): the §5 H8 library-composition null is the Era 1 precursor; Era 3's h8-v2 / h10-v2 / h12-v2 closure (`results/cross-hypothesis-library/permutation-t4/fdr_summary.json`) is the paper-citation source.
- **Obs 269** (verifier over-confidence) and **Obs 272** (attractor-pull 125 m cap): apply to the downstream verifier + spatial-tolerance framing; not invoked by this retest directly but the 20 m matching buffer here is the preregistered primary that these downstream analyses question and re-frame.
- **Obs 155 + Obs 148** (variance stabilisation under Phase 3c diversity pools): §10 Phase 3c is the planned Era 1 test; [PENDING] (§10).
- **Obs 496, Obs 498** (added 2026-10-06): a text-only request transmits no exemplar; the Phase 2c text arms are six runs of one configuration, and § 11.4's contrast was a bootstrap false positive. **Obs 499**: three further statistical records corrected under D42.

## 14. Paper implications

### 14.1 Canonical best-configuration stack (Era 1)

- Example ordering: **canonical-last** (Phase 2e; F1 = 0.631, one single-pass run; ΔF1 = +0.060 vs random, p = 0.0019; not significant against canonical-first or config-default, so the ordering is not separable from those two; sent as nulls, hard positives, then canonicals, E92).
- Temperature: **T = 0.0 on image**, **T = 0.0–0.3 on text** (Phase 2b; note cross-track crossover).
- Library composition: any of {canonical, plus-hp, scale-4, scale-8, pure-positive-canon} on the image track — not paper-decidable from Phase 2c (Era 3 h8-v2 closure is the paper-citation source for library claims). On the text track the choice is moot: no library is sent (E90).
- Negation text style: any (Phase 2d null; no paper-citable effect).
- Consensus: **K = 30 HIGH-thinking at threshold ≥ 21** (Phase 3a replication; F1 = 0.7705 at 21-of-30; diversity-dividend).

### 14.2 Practitioner message — change the Gemini API default

The Gemini API defaults temperature to 1.0. Both tracks show T = 1.0 is **significantly suboptimal**: image track T = 0.0 > T = 1.0 ΔF1 = +0.064 (p = 0.0008); text track T = 0.0 > T = 1.0 ΔF1 = +0.093 (p = 0.0008). Practitioner-facing paper text should explicitly recommend setting T = 0.0 for image-channel detection and T = 0.0–0.3 for text-channel detection.

### 14.3 Diversity-dividend is a reportable phenomenon

HIGH-thinking single-pass is 0.13 F1 *worse* than MINIMAL (§9); HIGH-thinking consensus 21-of-30 is 0.07 F1 *better* than MINIMAL consensus 25-of-30 (§8). The same configuration flips from worst to best depending on consensus vs single-pass. This is a distinctive methodological finding worth one paragraph in the paper: the diversity of HIGH-thinking generations is counterproductive at K = 1 but productive at K = 30.

### 14.4 Library-composition null is preregistered (not exploratory)

Phase 2c (§5) is the Era 1 preregistered library-composition test and finds no significant effect on the image track. [Corrected 2026-10-06: first written "on either track (except for a tiny plus-hp vs scale-4 gap on text)". The text track tested nothing, its five arms being identical requests, and that gap is a withdrawn false positive (§ 5.2; E90, D42).] This null is the preregistered prior that the Era 3 h8-v2 / h10-v2 / h12-v2 re-tests later confirmed under tighter CI (45-pair cross-hypothesis BH-FDR null at p_adj ≥ 0.966; see `results/cross-hypothesis-library/permutation-t4/fdr_summary.json`). The paper's library-composition-axis claim rests on both artefacts; this Era 1 retest is the chronologically-first evidence.

### 14.5 Suggested paper text (Methods / Results — Era 1 retest)

> An Era 1 production retest on a 340-tile corpus (569 ground-truth mounds, 4 map sheets, Gemini 3 Flash, `gemini-3-flash`) evaluated the preregistered factorial design across Phase 2a–2e (single-pass) and Phase 3a (consensus voting; K = 30). The best single-pass configuration is canonical-last example ordering (F1 = 0.631 [0.587, 0.672], one run, not significantly above canonical-first); the best consensus configuration is HIGH-thinking × 21-of-30 voting (F1 = 0.771 [0.725, 0.811]) — the highest F1 in the retest. H1 modality replicates the Phase 3 pilot finding that text-only outperforms image-only (ΔF1 = +0.088; p = 0.0055). H7 temperature shows T = 0.0 optimal on the image track and T = 0.0–0.3 tied on the text track; both tracks show a significant degradation at T = 1.0, the Gemini API default. H8 library composition is null on the image track, the only track whose example library reaches the model, and H5 negation style is null on both tracks. The consensus voting analysis reveals a "diversity dividend": HIGH-thinking is 0.14 F1 worse than MINIMAL at single-pass (K = 1) but 0.07 F1 better at K = 30 consensus, because the extra generation diversity of HIGH-thinking runs provides the variance consensus-filtering needs.

## 15. Best Configurations (Non-PV)

Top 10 configurations across all phases, ranked by F1:

| Rank | Configuration | F1 | 95 % CI | P | R |
|-----:|---------------|----:|:------:|----:|----:|
| 1 | Replication HIGH consensus 21-of-30 | 0.7705 | [0.725, 0.811] | 0.7846 | 0.7570 |
| 2 | Replication HIGH consensus 25-of-30 | 0.7583 | [0.710, 0.801] | 0.8646 | 0.6753 |
| 3 | Replication minimal consensus 25-of-30 | 0.7033 | [0.652, 0.750] | 0.6729 | 0.7365 |
| 4 | Text consensus T0.3 23-of-30 | 0.6921 | [0.637, 0.739] | 0.6261 | 0.7737 |
| 5 | Text consensus T0.7 24-of-30 | 0.6915 | [0.639, 0.741] | 0.6488 | 0.7403 |
| 6 | Image consensus T0.7 18-of-30 | 0.6909 | [0.649, 0.730] | 0.6935 | 0.6883 |
| 7 | Text consensus T1.0 22-of-30 | 0.6860 | [0.633, 0.735] | 0.6506 | 0.7254 |
| 8 | Image consensus T1.0 18-of-30 | 0.6803 | [0.636, 0.721] | 0.7166 | 0.6475 |
| 9 | Image consensus T0.3 22-of-30 | 0.6661 | [0.625, 0.706] | 0.6519 | 0.6809 |
| 10 | Single-pass canonical-last | 0.6314 | [0.587, 0.672] | 0.5325 | 0.7755 |

## 16. [PENDING] Sections

- **Phase 3a-HIGH image track consensus**: 90 runs complete, bootstrap CIs not yet computed. Consensus voting sweep pending.
- **Phase 3c diversity image track**: 83 / 100 output runs complete, not yet bootstrapped.
- **Phase 3c diversity text track consensus**: All 100 output runs complete, 60 / 100 bootstrapped. Consensus sweep pending once all CIs available.
- **FDR-corrected pairwise comparisons**: Deferred until all experimental data are available. Currently reporting raw p-values only (24 / 70 significant at p < 0.05). [Updated 2026-10-06: §11 now gives BH within each phase, on the permutation test (D42): 21 / 70 significant, all surviving BH.]
- **Proposer-Verifier (PV) pipeline results**: Separate analysis — see `results/pv/` for PV batch verification outputs.

These are open items but **not blocking for paper finalisation** because the paper's headline detection metrics come from Era 2 / Era 3 `gemini-3-flash` analyses, not this Era 1 retest (see §12 Caveat 4).

## 17. Files manifest

**Outputs (this directory + siblings)**:

- `retest-production-summary.md` — this report (hand-authored).
- `phase2b/analysis_summary.md` — dedicated Phase 2b narrative (Session 75 item 3; commit `e8c46809`).
- `phase2b-track1-evaluation.json` + `phase2b-track2-evaluation.json` — Phase 2b per-track JSONs.
- `phase2b-carry-forward-parameters.md` — Phase 2b carry-forward decisions (retest-era; Session 75 item 3 Option B residual).
- `phase3a-consensus/track1-image/consensus-analysis-summary.md` — Phase 3a image-track consensus (§8 detail).
- `phase3a-consensus/track2-text/consensus-analysis-summary.md` — Phase 3a text-track consensus (§8 detail).
- `phase3a-consensus/replication/consensus-analysis-summary.md` — Phase 3a HIGH-replication consensus (§8 detail; top of §15 leaderboard).

**Inputs / cross-references**:

- `results/phase3d-pilot-results.md` — 60-tile Phase 3 holdout (baseline Obs 155).
- `results/pv/all-bootstrap-cis.json` — bootstrap CIs for individual runs.
- `results/cross-hypothesis-library/permutation-t4/fdr_summary.json` — Era 3 library-composition-axis null (cross-reference for §5 and §14.4).
- `results/retest/retest-production-final-report.md` — any later synthesis of this retest (if present; check the directory if the paper finalisation needs a post-retest summary).

## 18. Reproducibility

- **Script**: `scripts/10_evaluate_detections_bootstrap.py` (pipeline evaluator; 20 m Hungarian matching + 1,000-iteration tile-level bootstrap, seed 42).
- **Data-generation commits**: the production retest was a multi-commit run across Feb – Mar 2026; the 2026-03-21 timestamp in the header is the final retest-summary commit.
- **Bootstrap**: 1,000 iterations, seed 42, tile-level resampling.
- **Re-run**: this summary is assembled from the per-phase evaluation JSONs listed in §17. The summary itself is hand-authored; there is no single "regenerate" script. To refresh a specific phase's tables, re-run the phase's evaluation pipeline (standard `10_evaluate_detections_bootstrap.py` invocation on the phase's detection outputs) and lift the resulting F1 / P / R / CI values into the relevant §3–§10 table.
- **Toolchain**: Python ≥ 3.11, NumPy, pandas, GeoPandas ≥ 0.14, scikit-learn (MCC helper, bootstrap CI); pinned versions in `requirements.txt`.
- **Git commit of this level-up**: see this file's `git log` entry at 2026-04-24.

## Changelog

### 2026-10-06 — Phase 2c text contrast withdrawn; p-values restated under D42; H8's null is the image track's; example orders recorded

**Refresh trigger**: tracker W1 (`planning/text-track-transmission-2026-10-05.md`,
claims C-01, C-02, C-17, C-21, C-23, C-24, C-25). Three upstream findings.
(1) Erratum **E90** and the manipulation check
(`reports/manipulation-check-2026-10-05.md`): a text-only request transmits
no exemplar, so the five Phase 2c text arms sent identical requests, and the
text track tested no library. (2) PI ruling **D42**: no p-value is read from
the bootstrap; every contrast is tested by the paired tile-swap permutation
test, re-run on the March inputs (`reports/retest-bootstrap-check-2026-10-05.md`
§ W2.4; `permutation_retest` blocks in `pairwise-bootstrap-comparisons.json`).
(3) Erratum **E92** and the Phase 2e ordering check
(`reports/phase2e-ordering-check-2026-10-05.md`): the orderings reached the
model; the retest's Phase 2a-2d image arms ran canonical-first, and
`canonical-last` was sent as nulls, hard positives, then canonicals.

**Verdicts that changed**:

| Claim | Before | After |
|---|---|---|
| Phase 2c text: scale-4 > plus-hp (§§ 1, 5.2, 11.4) | significant, ΔF1 +0.013, p = 0.001 | **withdrawn**: identical requests (E90); permutation p = 0.0588, BH 0.588 |
| Phase 2b image: T0.7 > T1.3 (§ 11.2) | significant, p = 0.042 | not significant, p = 0.0588 (BH 0.094) |
| Phase 2e: config-default > random (§§ 7, 11.5) | significant, p = 0.046 | not significant, p = 0.0563 (BH 0.169) |
| H8 library null (§§ 1, 14.1, 14.4, 14.5, headline) | "on either track" / "on both tracks" | the image track only; the text arms tested nothing |
| § 5.1 "all p > 0.19" | as published | a reporting error: the lowest image-track library p was 0.076 on the bootstrap and is 0.091 on the permutation test |
| Significant F1 comparisons (§§ 2, 11, 12, 16) | 24 / 70 (raw) | 21 / 70 (raw); all 21 survive BH within phase |
| § 14.5 model | "Gemini 2.0 Flash" (missed by the 2026-06-05 correction) | Gemini 3 Flash (`gemini-3-flash`) |

**p-values restated** (bootstrap → permutation; verdict unchanged unless
listed above): § 3 brief-text > image-only 0.004 → 0.0055 and brief-text vs
verbose-text 0.106 → 0.105; § 4.1 T0.0 against T0.7, T1.0, T1.3 and T0.3:
0.002 → 0.0026, 0.001 → 0.0008, 0.001 → < 0.0001, 0.30 → 0.32; § 4.2 T0.0 vs
T0.3 0.862 → 0.916, the T1.0 contrasts 0.001 → 0.0002-0.0008, the T1.3
contrasts 0.004-0.006 → 0.0018-0.0034, T0.7 > T1.0 0.004 → 0.0055; § 5.3 all
p > 0.09 → all p > 0.14; § 6.1 0.85 → 0.88; § 6.2 0.376 → 0.426 (F1) and
0.001 → 0.003 (recall); § 7 canonical-last against random, config-default
and canonical-first 0.002 → 0.0019, 0.158 → 0.186, 0.124 → 0.137; § 8
0.001 → 0.0004 and 0.001 → 0.0014; § 14.2 0.001 → 0.0008 (both tracks);
every § 11 row, with the retired value kept in its own column.

**Also added**: § 2's example-order bullet and § 7's ordering note (E92;
the Phase 2e study definition's "baseline used in all prior phases" and
"reused from Phase 2c" are in `studies/retest/phase2e-h4-ordering.yaml`, not
in this document, and hold for the February programme only); § 12 caveats
9 and 10; § 13's Obs 498 and Obs 499; "single run" and "shares Tier 1" for
canonical-last, with "recency bias hypothesis supported" qualified, since
H4's registered contrast is not significant.

**What did NOT change**: every F1, precision, recall and CI in §§ 3-10 and
15, and every ranking; the image-track Phase 2c null; the H-family verdicts
({H2, H3, H7} rejected; H4, H5, H8 not); the ten verdicts the paper relies
on (A[1], A[25], A[27], A[53]-A[55], A[59], A[67]-A[69]; report § W2.4). The
withdrawn and qualified sentences are kept, struck through or bracketed.

**Commit**: see `git log` for this entry's date.

### 2026-06-05 — Model-of-record corrected: `gemini-2.0-flash` → `gemini-3-flash`

**Refresh trigger**: Session 101 model-anomaly resolution. The Era-1 retest's
model-of-record was investigated because the run metas (`gemini-3-flash`)
contradicted this document's prose (`gemini-2.0-flash`). Decisive evidence,
all re-read at source:

- **All** retest metas (phase2 *and* phase3) record `configuration.model =
  gemini-3-flash` and `cost_estimate.pricing_used.model =
  gemini-3-flash-preview` (runtime snapshots frozen 2026-03-15, not editable
  retroactively).
- The source config `prompts/configs/detect_brief-text.json` has specified
  `gemini-3-flash` since 2026-01-09 (git blame); it was **never**
  `gemini-2.0-flash`.
- **Zero** retest artefacts (configs, metas, geojsons) record any 2.x model;
  `config.py`'s default is `gemini-3-pro-preview`, and there is no
  `gemini-2.0-flash` anywhere in the code path.
- The project began (December 2025) **after** Gemini 3's 2025-11-18 release, so
  there was never a window in which a 2.x model ran (user-confirmed: no 2.x
  model was ever run after that date).

The `gemini-2.0-flash` claim was hand-authored at this doc's creation
(2026-03-21, commit `245b9468`) with **no cited source** and was hardened into
the §12 cross-era caveat at the 2026-04-24 level-up. These Era-1 batch metas are
GAP-9 (no per-item `model_version` survived), so the API-returned model cannot be
re-confirmed directly — but every machine-generated artefact agrees on
`gemini-3-flash`, against a single unsourced prose line (E57 doctrine: trust
machine config/meta over prose).

| Claim | Before | After |
|---|---|---|
| Header **Model** | `gemini-2.0-flash` | `gemini-3-flash` (→ `gemini-3-flash-preview`) |
| §12 Caveat 3 | "cross-era F1 comparisons should acknowledge the **model-version** difference" | "cross-era difference is **tile scope only**; no model-version confound" |

**What did NOT change**: all F1 / precision / recall / CI tables, rankings, and
findings (§§3–11, 14) — the correction is a model *label*, not a result. The
within-era comparisons were already model-homogeneous and remain so.

**Consequence for the paper**: the cross-era model-comparability caveat is
*removed*, not weakened — Era 1 ↔ Era 2/3 comparisons are confounded only by
tile scope (strictly nested; see `results/evaluation-scopes.md`), which is
cleaner than the prior framing implied.

### 2026-03-21 — Original publication

Document first authored 2026-03-21 (commit `245b9468`); levelled up 2026-04-24
(Session 76, §§1, 2, 12, 14–17 added). This banner and changelog were added
2026-06-05 (the first Revision-Policy stub for this document) as part of the
model-of-record correction above.
