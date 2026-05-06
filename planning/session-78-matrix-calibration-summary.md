# Session 78 Verifier Calibration Matrix — Summary

Per-cell calibration metrics (AUC, Brier, ECE) for the Session 78 verifier prompt variant matrix. Fourteen cells = seven verifier variants (six novel alternatives + the canonical `adversarial-text`) across two candidate pools (image track, text track). Ground truth: spatial matching at 20 m buffer vs. curator reference mounds (`inputs/vectors/references/mounds-reference.geojson`, 569 features). Candidates filtered to the 487-tile Era 2 evaluation scope.

## Main table

| pool | variant | n_total | prevalence | AUC | Brier | ECE | P(mound\|p<=0.25) |
|------|---------|---------|-----------|-----|-------|-----|---------------------|
| image | adversarial | 2017 | 0.215 | 0.858 (0.844–0.872) | 0.211 (0.194–0.228) | 0.217 (0.202–0.237) | 0.012 |
| image | brief | 2017 | 0.215 | 0.858 (0.845–0.871) | 0.250 (0.232–0.268) | 0.267 (0.249–0.286) | 0.001 |
| image | brief-text | 2017 | 0.215 | 0.838 (0.819–0.856) | 0.231 (0.213–0.249) | 0.220 (0.204–0.241) | 0.025 |
| image | checklist | 2017 | 0.215 | 0.859 (0.847–0.872) | 0.238 (0.220–0.256) | 0.264 (0.246–0.281) | 0.002 |
| image | checklist-text | 2017 | 0.215 | 0.852 (0.839–0.866) | 0.244 (0.226–0.263) | 0.266 (0.248–0.284) | 0.004 |
| image | comparative | 2017 | 0.215 | 0.855 (0.844–0.867) | 0.235 (0.217–0.254) | 0.251 (0.233–0.269) | 0.002 |
| image | adversarial-text | 2017 | 0.215 | 0.858 (0.842–0.874) | 0.190 (0.175–0.206) | 0.179 (0.163–0.198) | 0.040 |
| text | adversarial | 3736 | 0.115 | 0.967 (0.962–0.972) | 0.059 (0.052–0.066) | 0.077 (0.072–0.086) | 0.004 |
| text | brief | 3736 | 0.115 | 0.964 (0.959–0.969) | 0.087 (0.078–0.096) | 0.111 (0.102–0.120) | 0.000 |
| text | brief-text | 3736 | 0.115 | 0.938 (0.924–0.951) | 0.083 (0.075–0.092) | 0.092 (0.083–0.100) | 0.009 |
| text | checklist | 3736 | 0.115 | 0.964 (0.959–0.968) | 0.083 (0.074–0.092) | 0.122 (0.114–0.131) | 0.001 |
| text | checklist-text | 3736 | 0.115 | 0.950 (0.940–0.958) | 0.106 (0.097–0.116) | 0.139 (0.130–0.149) | 0.002 |
| text | comparative | 3736 | 0.115 | 0.963 (0.958–0.967) | 0.076 (0.068–0.084) | 0.103 (0.095–0.111) | 0.000 |
| text | adversarial-text | 3736 | 0.115 | 0.956 (0.946–0.965) | 0.059 (0.053–0.066) | 0.071 (0.064–0.079) | 0.018 |

## Comparison to Observation 269

Observation 269 (55-map image-track canonical, earlier session work) reported **AUC = 0.655, ECE = 0.269** — a strongly miscalibrated low-tail where candidates with low verifier probability still carried high empirical mound rates.

Current run, image track, canonical `adversarial-text` (Era 2 scope, 4-map gold-standard corpus):

- AUC = 0.858 (95% CI: 0.842–0.874)
- ECE = 0.179 (95% CI: 0.163–0.198)
- P(mound | p<=0.25) = 0.040

Note: Obs 269 scope is 55 maps; this run's scope is the four-map gold-standard corpus (487-tile Era 2). Differences in corpus composition confound a direct numerical comparison, but the qualitative pattern (low-tail P(mound) vs AUC vs ECE) is what the matrix is designed to probe.

## Top and bottom per track

**image track**

- Best ECE: `adversarial-text` (ECE = 0.179, AUC = 0.858)
- Worst ECE: `brief` (ECE = 0.267, AUC = 0.858)
- Best AUC: `checklist` (AUC = 0.859, ECE = 0.264)

**text track**

- Best ECE: `adversarial-text` (ECE = 0.071, AUC = 0.956)
- Worst ECE: `checklist-text` (ECE = 0.139, AUC = 0.950)
- Best AUC: `adversarial` (AUC = 0.967, ECE = 0.077)

## Interpretation

Variants on the image track that improve both ECE and AUC versus the canonical `adversarial-text`:

- None — no matrix variant dominates the canonical `adversarial-text` on both ECE and AUC simultaneously.

Obs 269 image-track miscalibration pattern = ECE ~ 0.27. Variants on this run that sit well below that threshold (ECE < 0.10):

- None — no image-track variant clears ECE < 0.10; all sit in the miscalibrated regime.

## Anomaly flags

- Image-track reference-GT coverage: `mounds-reference.geojson` is the curator ground truth for the four-map gold-standard corpus. If any image-pool candidates fall on tiles outside the corpus reference coverage, their zero-label assignments may under-count true mounds. The 487-tile scope filter mitigates this, but the caveat persists for any corpus expansion.

## Method

- Ground truth: candidate centroid within 20 m of any reference mound centroid (EPSG:32635, `gpd.sjoin_nearest`).
- ECE: 10 equal-width probability bins on `[0, 1]`; weighted mean `|mean_predicted - empirical_P(mound)|`.
- Bootstrap: 10,000 resamples with replacement, seed=42; 95% percentile CIs.
- Scope filter: `inputs/vectors/bounds/384/full_evaluation_bounds.geojson` (487 tiles, Era 2).

Per-cell machine-readable results at `results/verifier-calibration-matrix/<pool>-<variant>/calibration.json`.
