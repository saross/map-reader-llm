# Buffer-band lift analysis — VLM candidates vs extended GT

**Date**: 2026-04-21
**Candidates combined**: 1029 (yesterday mound@50 m: 474, today re-reviewed: 555)
**Student GT (null reference)**: 4744 at 0.149 per km²
**Reviewer-promoted real mounds**: 746
**Total real-mound universe**: 5490 at 0.173 per km² (bias-correction factor 0.8641)
**Study area**: 31817.94 km² (55-map evaluation bounds, 8,541 tiles)
**Permutations**: 1000, seed 42

## Cumulative lift — P(mound within R | candidate)

|   R_m |   obs_rate |   null_mean |   null_mean_bias_corrected |   null_ci_lo |   null_ci_hi |   lift_ratio |   lift_ratio_bias_corrected |   signal_fraction |   signal_fraction_bias_corrected |   p_value |
|------:|-----------:|------------:|---------------------------:|-------------:|-------------:|-------------:|----------------------------:|------------------:|---------------------------------:|----------:|
|    50 |     0.4606 |      0.0039 |                     0.0045 |       0.001  |       0.0078 |       118.32 |                      102.24 |            0.9915 |                           0.9902 |     0.001 |
|    75 |     0.5782 |      0.0087 |                     0.0101 |       0.0029 |       0.0146 |        66.55 |                       57.51 |            0.985  |                           0.9826 |     0.001 |
|   100 |     0.6239 |      0.0153 |                     0.0178 |       0.0078 |       0.0233 |        40.65 |                       35.12 |            0.9754 |                           0.9715 |     0.001 |
|   125 |     0.6424 |      0.0236 |                     0.0273 |       0.0146 |       0.033  |        27.2  |                       23.5  |            0.9632 |                           0.9575 |     0.001 |
|   150 |     0.6531 |      0.0329 |                     0.0381 |       0.0224 |       0.0437 |        19.83 |                       17.14 |            0.9496 |                           0.9416 |     0.001 |
|   286 |     0.725  |      0.1034 |                     0.1197 |       0.0855 |       0.1224 |         7.01 |                        6.06 |            0.8573 |                           0.8349 |     0.001 |

## Annular (shell) lift — new mounds per band

|   R_inner_m |   R_outer_m |   obs_rate_in_shell |   null_mean_in_shell |   null_mean_bias_corrected |   null_ci_lo |   null_ci_hi |   lift_ratio |   lift_ratio_bias_corrected |   signal_fraction |   signal_fraction_bias_corrected |   p_value |
|------------:|------------:|--------------------:|---------------------:|---------------------------:|-------------:|-------------:|-------------:|----------------------------:|------------------:|---------------------------------:|----------:|
|           0 |          50 |              0.4606 |               0.0039 |                     0.0045 |       0.001  |       0.0078 |       118.32 |                      102.24 |            0.9915 |                           0.9902 |     0.001 |
|          50 |          75 |              0.1176 |               0.0048 |                     0.0055 |       0.001  |       0.0087 |        24.52 |                       21.19 |            0.9592 |                           0.9528 |     0.001 |
|          75 |         100 |              0.0457 |               0.0067 |                     0.0077 |       0.0019 |       0.0126 |         6.86 |                        5.93 |            0.8542 |                           0.8312 |     0.001 |
|         100 |         125 |              0.0185 |               0.0083 |                     0.0096 |       0.0029 |       0.0146 |         2.23 |                        1.93 |            0.5522 |                           0.4817 |     0.002 |
|         125 |         150 |              0.0107 |               0.0093 |                     0.0108 |       0.0039 |       0.0155 |         1.15 |                        0.99 |            0.129  |                          -0.008  |     0.381 |
|         150 |         286 |              0.0719 |               0.0705 |                     0.0816 |       0.0554 |       0.0865 |         1.02 |                        0.88 |            0.0198 |                          -0.1343 |     0.433 |

## Ripley's cross-L (centred at zero)

Observed $L_{12}(r) - r$ above the null envelope indicates attraction (clustering of detection centroids near mounds). Crossings into the envelope indicate the scale at which clustering becomes indistinguishable from within-tile null.

|   r_m |   L_minus_r_obs |   L_minus_r_null_mean |   L_minus_r_envelope_lo |   L_minus_r_envelope_hi | outside_envelope   |
|------:|----------------:|----------------------:|------------------------:|------------------------:|:-------------------|
|    10 |          126.65 |                 -2.49 |                  -10    |                   35.55 | True               |
|    20 |          233.61 |                  5.8  |                  -20    |                   58.89 | True               |
|    30 |          397.29 |                 16.65 |                  -30    |                   61.1  | True               |
|    40 |          493.14 |                 28.04 |                  -40    |                   71.8  | True               |
|    50 |          577.85 |                 37.77 |                   -4.45 |                   78.83 | True               |
|    60 |          696.72 |                 47.64 |                    4.42 |                   91.07 | True               |
|    70 |          767.41 |                 57.28 |                    8.89 |                  100.43 | True               |
|    80 |          809.09 |                 66.01 |                   21.85 |                  113.25 | True               |
|    90 |          832.3  |                 75.62 |                   30.29 |                  118.73 | True               |
|   100 |          842.33 |                 84.45 |                   36.65 |                  132.26 | True               |
|   110 |          849.78 |                 93.71 |                   41.07 |                  143.61 | True               |
|   120 |          862.22 |                102.49 |                   50.43 |                  149.47 | True               |
|   130 |          870.01 |                111.22 |                   57.8  |                  154.45 | True               |
|   140 |          868.28 |                119.54 |                   68.73 |                  165.55 | True               |
|   150 |          874.6  |                127.87 |                   77.75 |                  175.29 | True               |
|   160 |          881.67 |                136.28 |                   89.48 |                  183.89 | True               |
|   170 |          879.61 |                144.55 |                   95.6  |                  191.54 | True               |
|   180 |          888.22 |                152.98 |                  104.45 |                  201.09 | True               |
|   190 |          907.92 |                161.57 |                  112.14 |                  209.69 | True               |
|   200 |          923.14 |                169.91 |                  122.08 |                  219.94 | True               |
|   210 |          943.21 |                178.47 |                  130.86 |                  226.89 | True               |
|   220 |          943.07 |                186.8  |                  135.75 |                  233.27 | True               |
|   230 |          949.01 |                195.02 |                  145.61 |                  243.36 | True               |
|   240 |          953.88 |                203.15 |                  154.4  |                  250.58 | True               |
|   250 |          960.27 |                211.35 |                  162.47 |                  261.29 | True               |
|   260 |          962.21 |                219.44 |                  167.29 |                  269.23 | True               |
|   270 |          963.2  |                227.13 |                  176.29 |                  276.59 | True               |
|   280 |          967.42 |                235.24 |                  184.46 |                  283.41 | True               |
|   290 |          961.57 |                243.19 |                  189.89 |                  291.58 | True               |
|   300 |          970.49 |                251.52 |                  198.97 |                  302.56 | True               |
|   310 |          971.87 |                259.51 |                  209.34 |                  309.54 | True               |
|   320 |          969.94 |                267.34 |                  215.08 |                  319.35 | True               |

## Interpretation

- **Signal fraction** at each R tells you what share of ``mound-within-R`` candidates are genuine attractor-pulls rather than coincidental mounds happening to fall near a random detection in the same tile. A value near 1 means the observed rate is almost entirely real clustering; near 0 means the rate is essentially what random placement would produce.
- **Lift ratio** is observed / null — how many times more often mounds appear within R than random placement would predict. Decays toward 1 as R grows and incidental mounds dominate.
- **Shell analysis** isolates the band-specific effect: the 50 m shell is yesterday's TP pool (frozen); the 50-75 m and 75-100 m shells capture the attractor-pull effect; shells beyond 150 m admit increasingly incidental mounds. A signal fraction per shell falling below ~50 % is the honest ceiling for practitioner-useful detection at that tolerance.
- **Ripley's cross-L** is a second-line confirmation. Observed above the envelope → detections attract mounds at that scale. The crossover into the envelope marks where the spatial relationship becomes statistically indistinguishable from tile-conditional randomness.

