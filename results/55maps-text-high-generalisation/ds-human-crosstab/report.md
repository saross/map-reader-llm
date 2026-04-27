# Dawid-Skene aggregate posterior vs. human review (55-map text HIGH T=0.7 generalisation)

Cross-tabulation of the Dawid-Skene (D-S) per-item posterior against the combined human-review labels on the VLM-only candidate set. Framing: the D-S posterior is an **aggregate** probabilistic estimate derived from two noisy annotators (student digitisers and the VLM pipeline); human review is a per-candidate adjudication. This analysis quantifies where the aggregate and the individual adjudications agree or diverge.

## Input provenance

- **ds_posteriors**: `results/55maps-text-high-generalisation/dawid-skene/item-posteriors.csv`
- **review_yesterday**: `/tmp/empty-review-yesterday.csv`
- **review_today**: `results/55maps-text-high-generalisation/human-review-multi-buffer.csv`

## Sample composition

- Combined review rows: **630**
- Rows successfully joined to D-S posterior: **630**
- Unjoined rows (no D-S posterior found): **0**
- Human-mound prevalence in joined set: **0.559** (352/630)

### Combined-label source breakdown

| Source | Count |
|--------|------:|
| today_only | 630 |

## Structural note — D-S 2-annotator identifiability

With only two binary annotators (student vote, VLM vote) the Dawid-Skene model assigns an **identical posterior** to every item that shares the same annotator response pattern. All 630 VLM-only items (student = 0, VLM = 1) receive the same posterior value (0.2935). Consequently:

- The D-S posterior on this slice is a single point estimate of the **aggregate rate** of true mounds in the VLM-only cohort, not an item-level discriminator.
- The reliability diagram has exactly one populated bin.
- The AUC of the D-S posterior as a classifier is undefined (degenerate ordering) and defaults to 0.5.
- The 2 x 2 cross-tab at threshold 0.5 collapses (posterior < 0.5 for all rows).

**Framing check.** The expected pattern was ‘aggregate estimates rate, human disambiguates individuals’. On this slice, the D-S aggregate is *not* close to the empirical rate (0.293 predicted vs. 0.559 observed) — see interpretation section 6 for the prior-misspecification diagnosis. The identifiability argument still holds — the D-S posterior cannot rank individuals by construction — but the aggregate itself is badly miscalibrated here, so the framing needs qualification rather than confirmation.

## 1. Coarse cross-tab (D-S > 0.5 vs. human mound)

| | Human mound | Human not_mound |
|---|---:|---:|
| **D-S > 0.5** | 0 | 0 |
| **D-S ≤ 0.5** | 352 | 278 |

- Precision: nan
- Recall:    0.0000
- F1:        nan

## 2. Reliability diagram (10 equal-width bins)

| Bin | n | n_mound | Mean predicted P | Empirical P | Gap (pred − emp) | 95 % Wilson CI on empirical |
|-----|---:|---:|---:|---:|---:|---|
| [0.2, 0.3] | 630 | 352 | 0.2935 | 0.5587 | -0.2652 | [0.520, 0.597] |

- **Expected Calibration Error (ECE, 10 bins):** 0.2652
- **Brier score:** 0.3169
- **AUC (D-S posterior as mound classifier):** 0.5000 *(degenerate — all inputs share one posterior; no rank information.)*

## 3. Ambiguity-band isolation

Evidence for ‘human disambiguates individuals, D-S estimates rate’.

| Band | Range | n | n_mound | Human-mound rate | 95 % Wilson CI |
|------|-------|---:|---:|---:|---|
| Ambiguous | [0.3, 0.7] | 0 | 0 | nan | [nan, nan] |
| Confident | [0, 0.1) ∪ (0.9, 1] | 0 | 0 | nan | [nan, nan] |
| Middle remainder | elsewhere | 630 | 352 | 0.5587 | — |

## 4. Buffer-band view (D-S posterior vs. review band)

| Buffer band | n | Mean D-S posterior | 95 % CI |
|------------:|---:|-------------------:|---|
| 50 | 268 | 0.2935 | [0.2935, 0.2935] |
| 75 | 18 | 0.2935 | [0.2935, 0.2935] |
| 100 | 18 | 0.2935 | [0.2935, 0.2935] |
| 125 | 11 | 0.2935 | [0.2935, 0.2935] |
| 150 | 5 | 0.2935 | [0.2935, 0.2935] |
| 200 (sentinel) | 32 | 0.2935 | [0.2935, 0.2935] |

## 5. Comparison to the verifier (Observation 269)

| Metric | D-S posterior | Verifier | Better-calibrated? |
|--------|--------------:|---------:|-------------------|
| ECE (lower is better) | 0.2652 | 0.2689 | D-S (aggregate calibration) |
| Brier (lower is better) | 0.3169 | 0.3226 | D-S |
| AUC (higher is better) | 0.5000 | 0.6545 | Verifier (D-S has no item-level rank) |

## 6. Interpretation

- **D-S aggregate is badly wrong here — flagged as surprising.** The D-S posterior predicts an aggregate mound rate of 0.2935 for the VLM-only cohort; the combined human-review label finds 0.5587 (352/630). The absolute gap is 0.265; the empirical rate is 1.90× the D-S estimate. This is the reverse of the expected framing: rather than ‘aggregate estimates rate well, human disambiguates individuals’, the D-S aggregate is systematically under-counting real mounds at the cohort level.
- **Prior-driven artefact.** The D-S run used a fixed prior of 5 % student false-negative rate (see `dawid-skene-results.json`). The data imply the student FN rate on the VLM-only slice is much higher — the VLM independently flagged 630+ locations that students had not digitised, and human review confirms a substantial fraction are real mounds at some buffer. A D-S fit with an honest, data-driven student-FN prior — or with more than two annotators — would land much closer to the empirical rate.
- **Aggregate vs. individual — revised.** With only two binary annotators, the D-S posterior collapses to a single value per response pattern, so it cannot rank individuals by design. Human review is the only per-candidate signal available on this slice. The verifier probability (Obs 269) is a graded item-level signal but is itself poorly calibrated at the high end. Downstream use should treat D-S as a (currently miscalibrated) cohort-rate estimator and rely on the verifier plus human review for item-level discrimination.
- **Buffer-band view.** Because the D-S posterior is degenerate, mean posterior is identical across every buffer band (0.2935 at all bands). It carries no information about buffer-band separation, which is consistent with Obs 268 — the signal for ‘wider-buffer mounds are genuinely lower-signal’ lives entirely in the verifier probability, not in the D-S posterior.

## Figures

- `reliability_plot.png` — reliability diagram.
- `buffer_scatter.png` — D-S posterior vs. buffer band for mound candidates.
