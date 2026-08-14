# Dawid-Skene aggregate posterior vs. human review (55-map text MIN generalisation)

Cross-tabulation of the Dawid-Skene (D-S) per-item posterior against the combined human-review labels on the VLM-only candidate set. Framing: the D-S posterior is an **aggregate** probabilistic estimate derived from two noisy annotators (student digitisers and the VLM pipeline); human review is a per-candidate adjudication. This analysis quantifies where the aggregate and the individual adjudications agree or diverge.

## Input provenance

- **ds_posteriors**: `results/55maps-text-min-generalisation/dawid-skene-standardised/item-posteriors.csv`
- **review_yesterday**: `results/55maps-extended-gt-2026-06-07/empty-yesterday-review.csv`
- **review_today**: `results/55maps-text-min-generalisation/human-review-multi-buffer.csv`

## Sample composition

- Combined review rows: **585**
- Rows successfully joined to D-S posterior: **577**
- Unjoined rows (no D-S posterior found): **8**
- Human-mound prevalence in joined set: **0.548** (316/577)

### Combined-label source breakdown

| Source | Count |
|--------|------:|
| today_only | 585 |

## Structural note — D-S 2-annotator identifiability

With only two binary annotators (student vote, VLM vote) the Dawid-Skene model assigns an **identical posterior** to every item that shares the same annotator response pattern. All 577 VLM-only items (student = 0, VLM = 1) receive the same posterior value (0.2945). Consequently:

- The D-S posterior on this slice is a single point estimate of the **aggregate rate** of true mounds in the VLM-only cohort, not an item-level discriminator.
- The reliability diagram has exactly one populated bin.
- The AUC of the D-S posterior as a classifier is undefined (degenerate ordering) and defaults to 0.5.
- The 2 x 2 cross-tab at threshold 0.5 collapses (posterior < 0.5 for all rows).

**Framing check.** The expected pattern was ‘aggregate estimates rate, human disambiguates individuals’. On this slice, the D-S aggregate is *not* close to the empirical rate (0.295 predicted vs. 0.548 observed) — see interpretation section 6 for the prior-misspecification diagnosis. The identifiability argument still holds — the D-S posterior cannot rank individuals by construction — but the aggregate itself is badly miscalibrated here, so the framing needs qualification rather than confirmation.

## 1. Coarse cross-tab (D-S > 0.5 vs. human mound)

| | Human mound | Human not_mound |
|---|---:|---:|
| **D-S > 0.5** | 0 | 0 |
| **D-S ≤ 0.5** | 316 | 261 |

- Precision: nan
- Recall:    0.0000
- F1:        nan

## 2. Reliability diagram (10 equal-width bins)

| Bin | n | n_mound | Mean predicted P | Empirical P | Gap (pred − emp) | 95 % Wilson CI on empirical |
|-----|---:|---:|---:|---:|---:|---|
| [0.2, 0.3] | 577 | 316 | 0.2945 | 0.5477 | -0.2532 | [0.507, 0.588] |

- **Expected Calibration Error (ECE, 10 bins):** 0.2532
- **Brier score:** 0.3118
- **AUC (D-S posterior as mound classifier):** 0.5000 *(degenerate — all inputs share one posterior; no rank information.)*

## 3. Ambiguity-band isolation

Evidence for ‘human disambiguates individuals, D-S estimates rate’.

| Band | Range | n | n_mound | Human-mound rate | 95 % Wilson CI |
|------|-------|---:|---:|---:|---|
| Ambiguous | [0.3, 0.7] | 0 | 0 | nan | [nan, nan] |
| Confident | [0, 0.1) ∪ (0.9, 1] | 0 | 0 | nan | [nan, nan] |
| Middle remainder | elsewhere | 577 | 316 | 0.5477 | — |

## 4. Buffer-band view (D-S posterior vs. review band)

| Buffer band | n | Mean D-S posterior | 95 % CI |
|------------:|---:|-------------------:|---|
| 50 | 243 | 0.2945 | [0.2945, 0.2945] |
| 75 | 19 | 0.2945 | [0.2945, 0.2945] |
| 100 | 7 | 0.2945 | [0.2945, 0.2945] |
| 125 | 5 | 0.2945 | [0.2945, 0.2945] |
| 150 | 7 | 0.2945 | [0.2945, 0.2945] |
| 200 (sentinel) | 35 | 0.2945 | [0.2945, 0.2945] |

## 5. Comparison to the verifier (Observation 269)

| Metric | D-S posterior | Verifier | Better-calibrated? |
|--------|--------------:|---------:|-------------------|
| ECE (lower is better) | 0.2532 | 0.2689 | D-S (aggregate calibration) |
| Brier (lower is better) | 0.3118 | 0.3226 | D-S |
| AUC (higher is better) | 0.5000 | 0.6545 | Verifier (D-S has no item-level rank) |

## 6. Interpretation

- **D-S aggregate is badly wrong here — flagged as surprising.** The D-S posterior predicts an aggregate mound rate of 0.2945 for the VLM-only cohort; the combined human-review label finds 0.5477 (316/577). The absolute gap is 0.253; the empirical rate is 1.86× the D-S estimate. This is the reverse of the expected framing: rather than ‘aggregate estimates rate well, human disambiguates individuals’, the D-S aggregate is systematically under-counting real mounds at the cohort level.
- **Prior-driven artefact.** The D-S run used a fixed prior of 5 % student false-negative rate (see `dawid-skene-results.json`). The data imply the student FN rate on the VLM-only slice is much higher — the VLM independently flagged 577+ locations that students had not digitised, and human review confirms a substantial fraction are real mounds at some buffer. A D-S fit with an honest, data-driven student-FN prior — or with more than two annotators — would land much closer to the empirical rate.
- **Aggregate vs. individual — revised.** With only two binary annotators, the D-S posterior collapses to a single value per response pattern, so it cannot rank individuals by design. Human review is the only per-candidate signal available on this slice. The verifier probability (Obs 269) is a graded item-level signal but is itself poorly calibrated at the high end. Downstream use should treat D-S as a (currently miscalibrated) cohort-rate estimator and rely on the verifier plus human review for item-level discrimination.
- **Buffer-band view.** Because the D-S posterior is degenerate, mean posterior is identical across every buffer band (0.2945 at all bands). It carries no information about buffer-band separation, which is consistent with Obs 268 — the signal for ‘wider-buffer mounds are genuinely lower-signal’ lives entirely in the verifier probability, not in the D-S posterior.

## Figures

- `reliability_plot.png` — reliability diagram.
- `buffer_scatter.png` — D-S posterior vs. buffer band for mound candidates.
