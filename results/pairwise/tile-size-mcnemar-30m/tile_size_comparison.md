# Tile Size Comparison: 512px vs 384px

Generated: 2026-03-28 08:17 UTC
Buffer: 30 m

## Image T=0.0

**Scoping**: 435 reference mounds in common area (of 569 total)

- 512px: 640 detections (of 777 total)
- 384px: 746 detections (of 746 total)

**McNemar concordance table** (per-mound detection):

| | 384px detected | 384px missed |
| --- | ---: | ---: |
| **512px detected** | 323 | 23 |
| **512px missed** | 64 | 25 |

**McNemar test**: b=23, c=64, p=0.0000 (***)

- Direction: 384px detects more unique mounds

**Global F1** (Hungarian matching on common area):

| Condition | F1 | Precision | Recall | TP | FP | FN |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 512px Image T=0.0 | 0.6308 | 0.5227 | 0.7954 | 346 | 316 | 89 |
| 384px Image T=0.0 | 0.6418 | 0.5019 | 0.8897 | 387 | 384 | 48 |

**Delta F1** (512 - 384): -0.0110

**Per-map-sheet breakdown**:

| Map | Condition | F1 | P | R | TP | FP | FN | Det | Ref |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| K-35-052-4 | 512px | 0.6070 | 0.4785 | 0.8298 | 78 | 85 | 16 | 163 | 94 |
| K-35-052-4 | 384px | 0.5936 | 0.4444 | 0.8936 | 84 | 105 | 10 | 189 | 94 |
| K-35-053-3 | 512px | 0.6556 | 0.5920 | 0.7346 | 119 | 82 | 43 | 201 | 162 |
| K-35-053-3 | 384px | 0.6970 | 0.5897 | 0.8519 | 138 | 96 | 24 | 234 | 162 |
| K-35-062-2 | 512px | 0.7527 | 0.6731 | 0.8537 | 140 | 68 | 24 | 208 | 164 |
| K-35-062-2 | 384px | 0.7277 | 0.6016 | 0.9207 | 151 | 100 | 13 | 251 | 164 |
| K-35-078-1 | 512px | 0.1714 | 0.1000 | 0.6000 | 9 | 81 | 6 | 90 | 15 |
| K-35-078-1 | 384px | 0.2500 | 0.1443 | 0.9333 | 14 | 83 | 1 | 97 | 15 |

## Image T=0.7

**Scoping**: 435 reference mounds in common area (of 569 total)

- 512px: 645 detections (of 783 total)
- 384px: 758 detections (of 758 total)

**McNemar concordance table** (per-mound detection):

| | 384px detected | 384px missed |
| --- | ---: | ---: |
| **512px detected** | 312 | 35 |
| **512px missed** | 59 | 29 |

**McNemar test**: b=35, c=59, p=0.0172 (*)

- Direction: 384px detects more unique mounds

**Global F1** (Hungarian matching on common area):

| Condition | F1 | Precision | Recall | TP | FP | FN |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 512px Image T=0.7 | 0.6275 | 0.5171 | 0.7977 | 347 | 324 | 88 |
| 384px Image T=0.7 | 0.6097 | 0.4744 | 0.8529 | 371 | 411 | 64 |

**Delta F1** (512 - 384): +0.0178

**Per-map-sheet breakdown**:

| Map | Condition | F1 | P | R | TP | FP | FN | Det | Ref |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| K-35-052-4 | 512px | 0.6100 | 0.4788 | 0.8404 | 79 | 86 | 15 | 165 | 94 |
| K-35-052-4 | 384px | 0.5734 | 0.4271 | 0.8723 | 82 | 110 | 12 | 192 | 94 |
| K-35-053-3 | 512px | 0.6467 | 0.5777 | 0.7346 | 119 | 87 | 43 | 206 | 162 |
| K-35-053-3 | 384px | 0.6650 | 0.5677 | 0.8025 | 130 | 99 | 32 | 229 | 162 |
| K-35-062-2 | 512px | 0.7473 | 0.6683 | 0.8476 | 139 | 69 | 25 | 208 | 164 |
| K-35-062-2 | 384px | 0.6874 | 0.5647 | 0.8780 | 144 | 111 | 20 | 255 | 164 |
| K-35-078-1 | 512px | 0.1869 | 0.1087 | 0.6667 | 10 | 82 | 5 | 92 | 15 |
| K-35-078-1 | 384px | 0.2479 | 0.1415 | 1.0000 | 15 | 91 | 0 | 106 | 15 |

## Text T=0.0

**Scoping**: 435 reference mounds in common area (of 569 total)

- 512px: 734 detections (of 884 total)
- 384px: 1093 detections (of 1093 total)

**McNemar concordance table** (per-mound detection):

| | 384px detected | 384px missed |
| --- | ---: | ---: |
| **512px detected** | 359 | 15 |
| **512px missed** | 37 | 24 |

**McNemar test**: b=15, c=37, p=0.0032 (**)

- Direction: 384px detects more unique mounds

**Global F1** (Hungarian matching on common area):

| Condition | F1 | Precision | Recall | TP | FP | FN |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 512px Text T=0.0 | 0.6275 | 0.4941 | 0.8598 | 374 | 383 | 61 |
| 384px Text T=0.0 | 0.5093 | 0.3536 | 0.9103 | 396 | 724 | 39 |

**Delta F1** (512 - 384): +0.1182

**Per-map-sheet breakdown**:

| Map | Condition | F1 | P | R | TP | FP | FN | Det | Ref |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| K-35-052-4 | 512px | 0.6113 | 0.4737 | 0.8617 | 81 | 90 | 13 | 171 | 94 |
| K-35-052-4 | 384px | 0.5076 | 0.3562 | 0.8830 | 83 | 150 | 11 | 233 | 94 |
| K-35-053-3 | 512px | 0.7721 | 0.6825 | 0.8889 | 144 | 67 | 18 | 211 | 162 |
| K-35-053-3 | 384px | 0.6636 | 0.5294 | 0.8889 | 144 | 128 | 18 | 272 | 162 |
| K-35-062-2 | 512px | 0.7696 | 0.6927 | 0.8659 | 142 | 63 | 22 | 205 | 164 |
| K-35-062-2 | 384px | 0.7273 | 0.5887 | 0.9512 | 156 | 109 | 8 | 265 | 164 |
| K-35-078-1 | 512px | 0.0757 | 0.0412 | 0.4667 | 7 | 163 | 8 | 170 | 15 |
| K-35-078-1 | 384px | 0.0712 | 0.0371 | 0.8667 | 13 | 337 | 2 | 350 | 15 |

## Text T=0.7

**Scoping**: 435 reference mounds in common area (of 569 total)

- 512px: 770 detections (of 924 total)
- 384px: 1090 detections (of 1090 total)

**McNemar concordance table** (per-mound detection):

| | 384px detected | 384px missed |
| --- | ---: | ---: |
| **512px detected** | 348 | 20 |
| **512px missed** | 43 | 24 |

**McNemar test**: b=20, c=43, p=0.0052 (**)

- Direction: 384px detects more unique mounds

**Global F1** (Hungarian matching on common area):

| Condition | F1 | Precision | Recall | TP | FP | FN |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 512px Text T=0.7 | 0.5998 | 0.4646 | 0.8460 | 368 | 424 | 67 |
| 384px Text T=0.7 | 0.5022 | 0.3485 | 0.8989 | 391 | 731 | 44 |

**Delta F1** (512 - 384): +0.0976

**Per-map-sheet breakdown**:

| Map | Condition | F1 | P | R | TP | FP | FN | Det | Ref |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| K-35-052-4 | 512px | 0.6045 | 0.4655 | 0.8617 | 81 | 93 | 13 | 174 | 94 |
| K-35-052-4 | 384px | 0.5419 | 0.3889 | 0.8936 | 84 | 132 | 10 | 216 | 94 |
| K-35-053-3 | 512px | 0.7322 | 0.6569 | 0.8272 | 134 | 70 | 28 | 204 | 162 |
| K-35-053-3 | 384px | 0.6842 | 0.5586 | 0.8827 | 143 | 113 | 19 | 256 | 162 |
| K-35-062-2 | 512px | 0.7624 | 0.6667 | 0.8902 | 146 | 73 | 18 | 219 | 164 |
| K-35-062-2 | 384px | 0.7103 | 0.5758 | 0.9268 | 152 | 112 | 12 | 264 | 164 |
| K-35-078-1 | 512px | 0.0667 | 0.0359 | 0.4667 | 7 | 188 | 8 | 195 | 15 |
| K-35-078-1 | 384px | 0.0599 | 0.0311 | 0.8000 | 12 | 374 | 3 | 386 | 15 |
