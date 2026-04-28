# Per-map (50, 75] m shell-rate variance — diagnostic test #3 from Obs 296

**Question.** Is the cross-corpus (GS vs 55-map) gap in the (50, 75] m mid-distance pull rate (≤ 1.7 % on GS, 5–10× higher on 55-map per Obs 296) **structural** (a failure-of-generalisation effect) or **sampling** (the 4 GS maps happen to be a low-distractor subset of the 55-map universe)?

**Method.** Per-detection nearest-reference distance is computed via geometric KDTree against `inputs/vectors/references/student-mounds-55maps-reviewed.geojson` (4744 reviewed reference points), matching the GS attractor-pull methodology (`analyse_attractor_pull_gs.py`). Detections are grouped by `map_name` (55 maps); per-map (50, 75] m rate is n_in_shell / n_detections. Bootstrap: 1,000 random samples of 4 maps from 55, detection-weighted mean per sample, P(mean ≤ GS yardstick) reported.

## Per-run summary

| Run | n_det (corpus) | n_in_shell | corpus rate | per-map mean | per-map median | per-map SD | per-map min | per-map max | maps with > 0 dets |
|:---|--:|--:|--:|--:|--:|--:|--:|--:|--:|
| T=0.3 text-HIGH | 692 | 30 | 4.34 % | 4.81 % | 0.00 % | 8.56 % | 0.00 % | 42.86 % | 55 / 55 |
| T=0.7 text-HIGH | 630 | 21 | 3.33 % | 4.77 % | 0.00 % | 12.05 % | 0.00 % | 75.00 % | 55 / 55 |
| image (T=0.7) | 1029 | 163 | 15.84 % | 15.68 % | 15.38 % | 12.45 % | 0.00 % | 50.00 % | 55 / 55 |
| text-MIN | 585 | 24 | 4.10 % | 5.06 % | 0.00 % | 10.27 % | 0.00 % | 50.00 % | 55 / 55 |

## Per-map fraction below the GS yardstick

Of the maps with > 0 detections, what fraction have a per-map (50, 75] m rate ≤ the GS yardstick? Reported against both the headline 1.7 % yardstick (highest GS condition: SCALE4-optimal, image-track) and the same-track yardstick (text: 0.51 %; image: 1.21 %).

| Run | track | n_active | n maps ≤ 1.7 % | frac ≤ 1.7 % | same-track yardstick | n maps ≤ same-track | frac ≤ same-track |
|:---|:---|--:|--:|--:|--:|--:|--:|
| T=0.3 text-HIGH | text | 55 | 34 | 61.8 % | 0.51 % | 34 | 61.8 % |
| T=0.7 text-HIGH | text | 55 | 40 | 72.7 % | 0.51 % | 40 | 72.7 % |
| image (T=0.7) | image | 55 | 10 | 18.2 % | 1.21 % | 10 | 18.2 % |
| text-MIN | text | 55 | 37 | 67.3 % | 0.51 % | 37 | 67.3 % |

## Bootstrap 4-map random samples vs GS yardstick (headline)

Each row reports 1,000 bootstrap samples of 4 maps drawn without replacement from the 55-map universe; statistic is the detection-weighted mean (50, 75] m rate per sample.

| Run | bootstrap mean | bootstrap SD | bootstrap p05 | bootstrap p95 | P(mean ≤ 1.7 %) | same-track yardstick | P(mean ≤ same-track) |
|:---|--:|--:|--:|--:|--:|--:|--:|
| T=0.3 text-HIGH | 4.34 % | 3.26 % | 0.00 % | 10.26 % | 19.1 % | 0.51 % | 15.2 % |
| T=0.7 text-HIGH | 3.89 % | 3.82 % | 0.00 % | 11.37 % | 29.8 % | 0.51 % | 23.2 % |
| image (T=0.7) | 15.79 % | 5.14 % | 7.50 % | 23.94 % | 0.0 % | 1.21 % | 0.0 % |
| text-MIN | 4.78 % | 4.52 % | 0.00 % | 14.64 % | 22.3 % | 0.51 % | 17.5 % |

## Verdict

**Mixed.** Bootstrap probabilities are mixed by track. image-track: P(≤ same-track GS) = 0.0 %; text-track (worst across 3 runs): P(≤ same-track GS) = 23.2 %. The image-track gap looks **structural** (a random 4-map sample of 55-map image-track detections almost never reaches the GS image rate); the text-track gap looks **plausibly sampling** (random 4-map samples of 55-map text-track detections reach the GS text rate at non-trivial frequencies). Obs 296's failure-of-generalisation reading is **track-dependent** on this diagnostic: strongly supported on image, weakly supported on text.

### Caveats and complications

1. **Per-map distributions are heavily right-skewed on text tracks.** Median per-map rate is 0 % for all three text runs (T=0.3, T=0.7, T=MIN); the corpus-level rate of ~4 % is driven by a long tail of high-pull maps (~25–43 % per-map rate at the upper tail). 4-map random samples that miss the tail look GS-like; samples that catch even one tail map jump well above any GS condition's rate. The text-track sampling result reflects this skew, not corpus-wide GS-likeness.
2. **Methodology choice (KDTree vs reviewer band).** This diagnostic uses geometric KDTree against the 4,744-point reviewed reference for methodology-parity with the GS yardstick. The Obs 296 corpus-level rates (3.5 / 2.9 / 11.8 %) come from the review-CSV buffer-band measurement; this script's KDTree corpus-level rates (4.3 / 3.3 / 15.8 %) are within ~30 % of those values, confirming the gap is robust to method choice.
3. **The 1.7 % yardstick is image-track (SCALE4-optimal); the same-track GS text rate is 0.51 %.** Comparing 55-map text runs against a 1.7 % image-track yardstick is permissive (favours sampling); the same-track 0.51 % yardstick is stricter and produces lower P(≤ yardstick) values, but text-track P stays in the 15–23 % range under either yardstick.

## Provenance

- Reference: `inputs/vectors/references/student-mounds-55maps-reviewed.geojson` (4744 reviewed reference points)
- Bounds: `inputs/vectors/bounds/384/55maps_evaluation_bounds.geojson` (8,541 tiles, 55 maps)
- Bootstrap iterations: 1000
- RNG seed: 42
- GS yardstick: 1.7 % (SCALE4-optimal, per Obs 296)
- Driver: `scripts/analyse_55maps_per_map_shell_variance.py`

## Cross-references

- **Obs 296** (GS-vs-55-map cap = failure-of-generalisation, 5–10× per-detection mid-distance pull): the observation this diagnostic tests.
- **Obs 295 / Obs 298** (GS 25 m cap; 4-run 100 / 125 m 55-map cap split): adjacent results characterising the cap difference being explained.
- `results/gold-standard-attractor-pull/attractor-pull-gs.json` (GS yardstick source).
- `results/55maps-attractor-pull-v2/attractor-pull-v2.json` (55-map per-corpus rates referenced in Obs 296).
