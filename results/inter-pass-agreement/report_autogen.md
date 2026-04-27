# Inter-Pass Agreement Analysis (autogen)

**Generated**: 2026-04-27T04:46:30.029388+00:00
**Script version**: 1.0.0
**Script**: `scripts/analyse_inter_pass_agreement.py`

## Caveats

- **Cluster radius**: candidate-match kappa uses a 20 m radius in UTM-32635 by default. A 30 m sensitivity row is reported for the gold-standard-v2 cell only (and labelled `_sens` in tables).
- **Tile denominator alignment**: tile-presence kappa uses the intersection of per-pass `*.tiles.json` `completed` lists. Passes with no tiles.json are dropped and listed under `tile_passes_dropped` in the JSON output.
- **Marginal-prevalence kappa paradox**: Cohen's kappa deflates when one rating dominates (e.g. very few detections per pass means most cluster-presence vectors are near-all-zero). Observed agreement P_o is reported alongside kappa to make this visible at extremes.
- **Phase 3a retest borderline thresholds**: no canonical F1-optimal threshold has been published for the K=30 retest cells; the borderline anchor uses `round(K * 0.7) = 21` as a documented fallback. Borderline metrics for these cells should be read in relative comparison rather than as headline numbers.

## 1. Headline Pairwise Kappa Summary

Mean / SD / min / max are computed over off-diagonal entries of the K x K matrix.

| Stratum | Condition | K | n_clusters | kappa_cm mean | kappa_cm SD | kappa_cm min | kappa_cm max | P_o_cm mean | kappa_tile mean |
|---------|-----------|--:|----------:|------:|------:|------:|------:|------:|------:|
| phase3a_image_matrix | HIGH-T0.0 | 3 | 802 | 0.316 | 0.487 | -0.035 | 0.943 | 0.930 | — |
| phase3a_image_matrix | MIN-T0.0 | 3 | 690 | 0.351 | 0.382 | -0.011 | 0.821 | 0.986 | 0.993 |
| phase3a_image_matrix | HIGH-T0.7 | 10 | 3211 | 0.336 | 0.025 | 0.287 | 0.399 | 0.754 | 0.674 |
| phase3a_image_matrix | HIGH-T0.3 | 10 | 3406 | 0.365 | 0.021 | 0.313 | 0.406 | 0.755 | 0.670 |
| phase3a_image_matrix | HIGH-T1.0 | 10 | 4632 | 0.250 | 0.031 | 0.182 | 0.315 | 0.756 | 0.579 |
| phase3a_image_matrix | MIN-T0.3 | 10 | 1110 | 0.607 | 0.027 | 0.530 | 0.662 | 0.824 | 0.835 |
| phase3a_image_matrix | MIN-T0.7 | 10 | 1444 | 0.529 | 0.036 | 0.440 | 0.624 | 0.765 | 0.805 |
| phase3a_image_matrix | MIN-T1.0 | 10 | 1972 | 0.456 | 0.027 | 0.403 | 0.537 | 0.742 | 0.695 |
| phase3a_text_matrix | HIGH-T0.0 | 3 | 1256 | 0.175 | 0.054 | 0.118 | 0.238 | 0.729 | 0.712 |
| phase3a_text_matrix | MIN-T0.0 | 3 | 1087 | 0.224 | 0.100 | 0.098 | 0.310 | 0.823 | 0.777 |
| phase3a_text_matrix | HIGH-T0.3 | 10 | 4309 | 0.373 | 0.023 | 0.325 | 0.418 | 0.742 | 0.448 |
| phase3a_text_matrix | MIN-T0.3 | 10 | 1572 | 0.551 | 0.035 | 0.474 | 0.625 | 0.787 | 0.498 |
| phase3a_text_matrix | HIGH-T1.0 | 10 | 5925 | 0.287 | 0.020 | 0.245 | 0.326 | 0.741 | 0.316 |
| phase3a_text_matrix | MIN-T1.0 | 10 | 2480 | 0.462 | 0.021 | 0.417 | 0.510 | 0.739 | 0.420 |
| phase3a_text_matrix | MIN-T0.7 | 30 | 2786 | 0.654 | 0.022 | 0.591 | 0.708 | 0.839 | 0.572 |
| phase3a_text_matrix | HIGH-T0.7 | 30 | 11731 | 0.381 | 0.017 | 0.345 | 0.447 | 0.868 | 0.389 |
| scale4_t07 | SCALE4-T0.7 | 10 | 3610 | 0.293 | 0.036 | 0.206 | 0.364 | 0.756 | 0.645 |
| phase3a_retest | image-T0.3 | 30 | 1516 | 0.666 | 0.022 | 0.611 | 0.731 | 0.834 | 0.854 |
| phase3a_retest | image-T0.7 | 30 | 2608 | 0.570 | 0.025 | 0.500 | 0.659 | 0.827 | 0.708 |
| phase3a_retest | image-T1.0 | 30 | 3477 | 0.498 | 0.021 | 0.440 | 0.566 | 0.832 | 0.570 |
| phase3a_retest | text-T0.3 | 30 | 1664 | 0.724 | 0.031 | 0.605 | 0.814 | 0.862 | 0.381 |
| phase3a_retest | text-T0.7 | 30 | 2415 | 0.662 | 0.020 | 0.602 | 0.726 | 0.846 | 0.221 |
| phase3a_retest | text-T1.0 | 30 | 3281 | 0.605 | 0.024 | 0.541 | 0.669 | 0.844 | 0.305 |
| phase3a_retest | high-text-T0.3 | 30 | 7935 | 0.448 | 0.021 | 0.397 | 0.506 | 0.865 | 0.434 |
| phase3a_retest | high-text-T0.7 | 30 | 11795 | 0.368 | 0.019 | 0.323 | 0.427 | 0.875 | 0.296 |
| phase3a_retest | high-text-T1.0 | 30 | 13445 | 0.344 | 0.015 | 0.299 | 0.389 | 0.881 | 0.289 |
| phase3a_retest | replication-high | 30 | 11251 | 0.385 | 0.018 | 0.343 | 0.438 | 0.875 | 0.334 |
| phase3a_retest | replication-minimal | 30 | 2415 | 0.658 | 0.027 | 0.585 | 0.733 | 0.845 | 0.264 |
| gold_standard_v2 | detect_brief-text | 5 | 3830 | 0.146 | 0.020 | 0.113 | 0.181 | 0.602 | 0.362 |

## 2. Borderline-Instability

Borderline set B = {clusters with vote_count in {t* - 1, t*, t* + 1}}; fragility = |B| / |consensus@t*|.

| Stratum | Condition | K | t* | t* source | Consensus n | Borderline n | Borderline % | Fragility | GT lost % | GT gained % |
|---------|-----------|--:|---:|-----------|----------:|----------:|----------:|----------:|----------:|----------:|
| phase3a_image_matrix | HIGH-T0.0 | 3 | 1 | registry | 802 | 84 | 10.470 | 0.105 | 5.800 | 0.000 |
| phase3a_image_matrix | MIN-T0.0 | 3 | 2 | registry | 681 | 690 | 101.320 | 1.013 | 0.350 | 0.000 |
| phase3a_image_matrix | HIGH-T0.7 | 10 | 7 | registry | 404 | 181 | 44.800 | 0.448 | 5.100 | 3.340 |
| phase3a_image_matrix | HIGH-T0.3 | 10 | 9 | registry | 362 | 419 | 115.750 | 1.157 | 8.960 | 3.510 |
| phase3a_image_matrix | HIGH-T1.0 | 10 | 6 | registry | 437 | 195 | 44.620 | 0.446 | 5.100 | 3.690 |
| phase3a_image_matrix | MIN-T0.3 | 10 | 10 | registry | 517 | 578 | 111.800 | 1.118 | 0.000 | 2.990 |
| phase3a_image_matrix | MIN-T0.7 | 10 | 8 | registry | 493 | 175 | 35.500 | 0.355 | 4.040 | 2.280 |
| phase3a_image_matrix | MIN-T1.0 | 10 | 8 | registry | 466 | 208 | 44.640 | 0.446 | 5.450 | 2.640 |
| phase3a_text_matrix | HIGH-T0.0 | 3 | 3 | registry | 745 | 985 | 132.210 | 1.322 | 0.000 | 0.880 |
| phase3a_text_matrix | MIN-T0.0 | 3 | 3 | registry | 799 | 946 | 118.400 | 1.184 | 0.000 | 1.580 |
| phase3a_text_matrix | HIGH-T0.3 | 10 | 10 | registry | 409 | 513 | 125.430 | 1.254 | 0.000 | 5.620 |
| phase3a_text_matrix | MIN-T0.3 | 10 | 10 | registry | 608 | 684 | 112.500 | 1.125 | 0.000 | 2.460 |
| phase3a_text_matrix | HIGH-T1.0 | 10 | 9 | registry | 414 | 507 | 122.460 | 1.225 | 10.720 | 5.450 |
| phase3a_text_matrix | MIN-T1.0 | 10 | 9 | registry | 549 | 642 | 116.940 | 1.169 | 9.310 | 4.220 |
| phase3a_text_matrix | MIN-T0.7 | 30 | 29 | registry | 530 | 596 | 112.450 | 1.125 | 4.570 | 2.810 |
| phase3a_text_matrix | HIGH-T0.7 | 30 | 26 | registry | 414 | 78 | 18.840 | 0.188 | 2.460 | 0.700 |
| scale4_t07 | SCALE4-T0.7 | 10 | 6 | registry | 404 | 150 | 37.130 | 0.371 | 4.040 | 3.340 |
| phase3a_retest | image-T0.3 | 30 | 21 | fallback_round(K*0.7)=21 | 571 | 34 | 5.950 | 0.059 | 0.180 | 0.530 |
| phase3a_retest | image-T0.7 | 30 | 21 | fallback_round(K*0.7)=21 | 482 | 47 | 9.750 | 0.098 | 1.760 | 0.700 |
| phase3a_retest | image-T1.0 | 30 | 21 | fallback_round(K*0.7)=21 | 430 | 49 | 11.400 | 0.114 | 1.760 | 1.930 |
| phase3a_retest | text-T0.3 | 30 | 21 | fallback_round(K*0.7)=21 | 695 | 37 | 5.320 | 0.053 | 0.700 | 0.350 |
| phase3a_retest | text-T0.7 | 30 | 21 | fallback_round(K*0.7)=21 | 673 | 42 | 6.240 | 0.062 | 0.530 | 0.700 |
| phase3a_retest | text-T1.0 | 30 | 21 | fallback_round(K*0.7)=21 | 618 | 53 | 8.580 | 0.086 | 0.880 | 1.580 |
| phase3a_retest | high-text-T0.3 | 30 | 21 | fallback_round(K*0.7)=21 | 548 | 73 | 13.320 | 0.133 | 1.230 | 0.530 |
| phase3a_retest | high-text-T0.7 | 30 | 21 | fallback_round(K*0.7)=21 | 504 | 76 | 15.080 | 0.151 | 1.580 | 1.230 |
| phase3a_retest | high-text-T1.0 | 30 | 21 | fallback_round(K*0.7)=21 | 494 | 75 | 15.180 | 0.152 | 1.930 | 1.410 |
| phase3a_retest | replication-high | 30 | 21 | fallback_round(K*0.7)=21 | 524 | 71 | 13.550 | 0.136 | 1.580 | 0.700 |
| phase3a_retest | replication-minimal | 30 | 21 | fallback_round(K*0.7)=21 | 659 | 43 | 6.530 | 0.065 | 0.880 | 0.530 |
| gold_standard_v2 | detect_brief-text | 5 | 4 | registry | 607 | 865 | 142.500 | 1.425 | 8.260 | 3.510 |

## 3. Cluster-Radius Sensitivity (gold-standard-v2)

Candidate-match kappa is recomputed at 30 m for the gold-standard-v2 cell. Compare with the 20 m row above.

| Stratum | Condition | Radius | kappa mean | kappa SD | kappa min | kappa max | P_o mean |
|---------|-----------|-------:|----------:|---------:|----------:|----------:|---------:|
| gold_standard_v2 | detect_brief-text | 30.0 m | 0.185 | 0.023 | 0.154 | 0.238 | 0.608 |
