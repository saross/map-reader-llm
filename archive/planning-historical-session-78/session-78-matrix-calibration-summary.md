# Session 78 Verifier Calibration Matrix — Summary

> **⚠️ SUPERSEDED 2026-05-01.** This planning summary is preserved for
> historical reference. The metrics it tabulates were refreshed in Phase D
> (commit `c0eb61f9`, 2026-04-27, shared-crops parity), re-confirmed in
> Session 80 Wave 3 (commit `2a928cf7`), upgraded to N=10K bootstrap at
> `e1955ddf`, and migrated to BCa CIs at `28e7de84`. Current authoritative
> values live under `results/verifier-calibration-matrix/<pool>-<variant>/calibration.json`;
> see Obs 290 Theme 8 in `docs/notes/reflections/working-notes.md`. Do not
> act on items in this file as if they are pending.

Per-cell calibration metrics (AUC, Brier, ECE) for the Session 78 verifier prompt variant matrix. Fourteen cells = seven verifier variants (six novel alternatives + the canonical `adversarial-text`) across two candidate pools (image track, text track). Ground truth: spatial matching at 20 m buffer vs. curator reference mounds (`inputs/vectors/references/mounds-reference.geojson`, 569 features). Candidates filtered to the 487-tile Era 2 evaluation scope.

## Main table

| pool | variant | n_total | prevalence | AUC | Brier | ECE | P(mound\|p<=0.25) |
|------|---------|---------|-----------|-----|-------|-----|---------------------|
| image | adversarial | 2017 | 0.215 | 0.858 (0.844–0.872) | 0.211 (0.194–0.228) | 0.217 (0.202–0.237) | 0.012 |
| image | brief | 2017 | 0.215 | 0.858 (0.845–0.871) | 0.250 (0.232–0.268) | 0.267 (0.249–0.286) | 0.001 |
| image | brief-text | 1998 | 0.213 | 0.837 (0.818–0.855) | 0.232 (0.215–0.250) | 0.222 (0.205–0.242) | 0.025 |
| image | checklist | 2016 | 0.215 | 0.860 (0.847–0.872) | 0.238 (0.219–0.256) | 0.263 (0.245–0.281) | 0.002 |
| image | checklist-text | 1998 | 0.215 | 0.853 (0.839–0.867) | 0.245 (0.226–0.264) | 0.266 (0.248–0.285) | 0.004 |
| image | comparative | 2017 | 0.215 | 0.855 (0.844–0.867) | 0.235 (0.217–0.254) | 0.251 (0.233–0.269) | 0.002 |
| image | adversarial-text | 1991 | 0.215 | 0.857 (0.841–0.873) | 0.190 (0.174–0.207) | 0.179 (0.163–0.198) | 0.041 |
| text | adversarial | 3736 | 0.115 | 0.967 (0.962–0.972) | 0.059 (0.052–0.066) | 0.077 (0.072–0.086) | 0.004 |
| text | brief | 3736 | 0.115 | 0.964 (0.959–0.969) | 0.087 (0.078–0.096) | 0.111 (0.102–0.120) | 0.000 |
| text | brief-text | 3709 | 0.114 | 0.937 (0.923–0.950) | 0.083 (0.075–0.092) | 0.092 (0.083–0.100) | 0.009 |
| text | checklist | 3736 | 0.115 | 0.964 (0.959–0.968) | 0.083 (0.074–0.092) | 0.122 (0.114–0.131) | 0.001 |
| text | checklist-text | 3715 | 0.115 | 0.950 (0.941–0.959) | 0.106 (0.096–0.115) | 0.139 (0.129–0.148) | 0.002 |
| text | comparative | 3736 | 0.115 | 0.963 (0.958–0.967) | 0.076 (0.068–0.084) | 0.103 (0.095–0.111) | 0.000 |
| text | adversarial-text | 3695 | 0.116 | 0.956 (0.946–0.965) | 0.059 (0.053–0.066) | 0.071 (0.065–0.079) | 0.018 |

## Comparison to Observation 269

Observation 269 (55-map image-track canonical, earlier session work) reported **AUC = 0.655, ECE = 0.269** — a strongly miscalibrated low-tail where candidates with low verifier probability still carried high empirical mound rates.

Current run, image track, canonical `adversarial-text` (Era 2 scope, 4-map gold-standard corpus):

- AUC = 0.857 (95% CI: 0.841–0.873)
- ECE = 0.179 (95% CI: 0.163–0.198)
- P(mound | p<=0.25) = 0.041

Note: Obs 269 scope is 55 maps; this run's scope is the four-map gold-standard corpus (487-tile Era 2). Differences in corpus composition confound a direct numerical comparison, but the qualitative pattern (low-tail P(mound) vs AUC vs ECE) is what the matrix is designed to probe.

## Top and bottom per track

**image track**

- Best ECE: `adversarial-text` (ECE = 0.179, AUC = 0.857)
- Worst ECE: `brief` (ECE = 0.267, AUC = 0.858)
- Best AUC: `checklist` (AUC = 0.860, ECE = 0.263)

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
