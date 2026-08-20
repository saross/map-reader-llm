# Leaderboard — Era 1, Consensus (no PV), 20 m buffer

**Generated**: 2026-08-20T06:34:06.296590+00:00
**Source tier JSON**: `results/leaderboard/per-architecture/era1/consensus/leaderboard_tiers_20m.json`
**Git commit**: `ef3ec4fe`
**Conditions**: 72 in 6 tier(s). Bounds: `inputs/vectors/bounds/full_evaluation_bounds.geojson`.

Tiering at 20 m: greedy-clique BH-FDR on tile-level paired permutation tests (10,000 permutations, seed 42) at q=0.05. Bootstrap 95% CIs (1,000 iterations) recomputed per buffer.

## Tier 1 (F1: 0.770–0.775)

| # | Condition | Track | K | Vote t | Proposer | Config | Verifier | Prob t | F1 [95% CI] | P | R | MCC |
|--:|-----------|:-----:|--:|:-----:|:---------|:-------|:--------:|:-----:|:-----------:|---:|---:|---:|
| 1 | h3-high-track2-text-T1.0 | text | 30 | 23 | gemini-3-flash | detect_brief-text-high | — | — | 0.775 [0.750, 0.798] | 0.860 | 0.705 | — |
| 2 | h3-high-track2-text-T0.3 | text | 30 | 23 | gemini-3-flash | detect_brief-text-high | — | — | 0.774 [0.753, 0.803] | 0.810 | 0.742 | — |
| 3 | h3-high-track2-text-T0.7 | text | 30 | 22 | gemini-3-flash | detect_brief-text-high | — | — | 0.773 [0.752, 0.797] | 0.822 | 0.729 | — |
| 4 | h3-rep-high | text | 30 | 21 | gemini-3-flash | detect_brief-text-high | — | — | 0.770 [0.747, 0.796] | 0.785 | 0.757 | — |

## Tier 2 (F1: 0.703–0.739)

| # | Condition | Track | K | Vote t | Proposer | Config | Verifier | Prob t | F1 [95% CI] | P | R | MCC |
|--:|-----------|:-----:|--:|:-----:|:---------|:-------|:--------:|:-----:|:-----------:|---:|---:|---:|
| 5 | h9-track2-text-h9-D-t4 | text | 5 | 4 | gemini-3-flash | phase3c-t2-h9A | — | — | 0.739 [0.711, 0.765] | 0.746 | 0.731 | — |
| 6 | h9-track2-text-h9-D-t1 | text | 5 | 4 | gemini-3-flash | phase3c-t2-h9A | — | — | 0.735 [0.711, 0.756] | 0.709 | 0.762 | — |
| 7 | h9-track2-text-h9-A-p4 | text | 5 | 4 | gemini-3-flash | phase3c-t2-h9A | — | — | 0.731 [0.703, 0.754] | 0.715 | 0.748 | — |
| 8 | h9-track2-text-h9-A-p1 | text | 5 | 4 | gemini-3-flash | phase3c-t2-h9A | — | — | 0.726 [0.701, 0.752] | 0.725 | 0.727 | — |
| 9 | h9-track2-text-h9-A-p2 | text | 5 | 4 | gemini-3-flash | phase3c-t2-h9A | — | — | 0.723 [0.696, 0.746] | 0.712 | 0.735 | — |
| 10 | h9-track2-text-h9-E-p1 | text | 5 | 5 | gemini-3-flash | phase3c-t2-h9B-v1 | — | — | 0.717 [0.692, 0.743] | 0.769 | 0.672 | — |
| 11 | h9-track2-text-h9-D-t2 | text | 5 | 4 | gemini-3-flash | phase3c-t2-h9A | — | — | 0.712 [0.687, 0.742] | 0.693 | 0.733 | — |
| 12 | h9-track2-text-h9-A-p5 | text | 5 | 4 | gemini-3-flash | phase3c-t2-h9A | — | — | 0.712 [0.684, 0.740] | 0.698 | 0.727 | — |
| 13 | h9-track2-text-h9-D-t3 | text | 5 | 4 | gemini-3-flash | phase3c-t2-h9A | — | — | 0.711 [0.684, 0.741] | 0.697 | 0.725 | — |
| 14 | h9-track2-text-h9-D-t5 | text | 5 | 4 | gemini-3-flash | phase3c-t2-h9A | — | — | 0.710 [0.686, 0.735] | 0.728 | 0.694 | — |
| 15 | h9-track2-text-h9-A-p3 | text | 5 | 4 | gemini-3-flash | phase3c-t2-h9A | — | — | 0.710 [0.681, 0.735] | 0.693 | 0.727 | — |
| 16 | h3-rep-minimal | text | 30 | 25 | gemini-3-flash | detect_brief-text | — | — | 0.703 [0.679, 0.731] | 0.673 | 0.737 | — |

## Tier 3 (F1: 0.655–0.698)

| # | Condition | Track | K | Vote t | Proposer | Config | Verifier | Prob t | F1 [95% CI] | P | R | MCC |
|--:|-----------|:-----:|--:|:-----:|:---------|:-------|:--------:|:-----:|:-----------:|---:|---:|---:|
| 17 | h9-track2-text-h9-B-v1 | text | 5 | 4 | gemini-3-flash | phase3c-t2-h9B-v1 | — | — | 0.698 [0.671, 0.725] | 0.659 | 0.740 | — |
| 18 | h3-track2-text-T0.3 | text | 30 | 23 | gemini-3-flash | detect_brief-text | — | — | 0.692 [0.659, 0.718] | 0.626 | 0.774 | — |
| 19 | h3-track2-text-T0.7 | text | 30 | 24 | gemini-3-flash | detect_brief-text | — | — | 0.692 [0.665, 0.719] | 0.649 | 0.740 | — |
| 20 | h3-track1-image-T0.7 | image | 30 | 18 | gemini-3-flash | library_plus-hp | — | — | 0.691 [0.665, 0.713] | 0.694 | 0.688 | — |
| 21 | h9-track1-image-h9-C-img5 | image | 5 | 3 | gemini-3-flash | phase3c-t1-h9C-img5 | — | — | 0.689 [0.665, 0.715] | 0.716 | 0.664 | — |
| 22 | h7-track2-text-T0.7 | text | 3 | 3 | gemini-3-flash | detect_brief-text | — | — | 0.687 [0.659, 0.716] | 0.648 | 0.731 | — |
| 23 | h3-track2-text-T1.0 | text | 30 | 22 | gemini-3-flash | detect_brief-text | — | — | 0.686 [0.656, 0.715] | 0.651 | 0.725 | — |
| 24 | h7-track2-text-T0.3 | text | 3 | 3 | gemini-3-flash | detect_brief-text | — | — | 0.683 [0.654, 0.708] | 0.627 | 0.751 | — |
| 25 | h9-track1-image-h9-A-p1 | image | 5 | 3 | gemini-3-flash | phase3c-t1-h9A | — | — | 0.682 [0.656, 0.714] | 0.701 | 0.664 | — |
| 26 | h9-track1-image-h9-A-p5 | image | 5 | 3 | gemini-3-flash | phase3c-t1-h9A | — | — | 0.679 [0.650, 0.705] | 0.702 | 0.659 | — |
| 27 | h3-track1-image-T1.0 | image | 30 | 19 | gemini-3-flash | library_plus-hp | — | — | 0.679 [0.651, 0.705] | 0.728 | 0.636 | — |
| 28 | h9-track1-image-h9-E-p2 | image | 5 | 3 | gemini-3-flash | phase3c-t1-h9E-p2 | — | — | 0.675 [0.649, 0.703] | 0.686 | 0.664 | — |
| 29 | h9-track2-text-h9-B-v2 | text | 5 | 4 | gemini-3-flash | phase3c-t2-h9B-v2 | — | — | 0.673 [0.644, 0.704] | 0.673 | 0.673 | — |
| 30 | h9-track1-image-h9-D-t2 | image | 5 | 3 | gemini-3-flash | phase3c-t1-h9A | — | — | 0.673 [0.644, 0.697] | 0.674 | 0.672 | — |
| 31 | h9-track1-image-h9-C-img4 | image | 5 | 3 | gemini-3-flash | phase3c-t1-h9C-img4 | — | — | 0.672 [0.646, 0.700] | 0.683 | 0.662 | — |
| 32 | h9-track1-image-h9-D-t5 | image | 5 | 3 | gemini-3-flash | phase3c-t1-h9A | — | — | 0.669 [0.640, 0.692] | 0.699 | 0.642 | — |
| 33 | h9-track1-image-h9-D-t1 | image | 5 | 4 | gemini-3-flash | phase3c-t1-h9A | — | — | 0.668 [0.640, 0.691] | 0.776 | 0.586 | — |
| 34 | h9-track2-text-h9-B-v5 | text | 5 | 4 | gemini-3-flash | phase3c-t2-h9B-v5 | — | — | 0.667 [0.639, 0.696] | 0.691 | 0.646 | — |
| 35 | h3-track1-image-T0.3 | image | 30 | 22 | gemini-3-flash | library_plus-hp | — | — | 0.666 [0.643, 0.691] | 0.652 | 0.681 | — |
| 36 | h9-track1-image-h9-A-p4 | image | 5 | 3 | gemini-3-flash | phase3c-t1-h9A | — | — | 0.665 [0.638, 0.693] | 0.673 | 0.657 | — |
| 37 | h9-track1-image-h9-A-p2 | image | 5 | 3 | gemini-3-flash | phase3c-t1-h9A | — | — | 0.664 [0.638, 0.692] | 0.666 | 0.662 | — |
| 38 | h9-track1-image-h9-B-v1 | image | 5 | 3 | gemini-3-flash | phase3c-t1-h9B-v1 | — | — | 0.664 [0.639, 0.690] | 0.655 | 0.673 | — |
| 39 | h9-track1-image-h9-C-img3 | image | 5 | 3 | gemini-3-flash | phase3c-t1-h9C-img3 | — | — | 0.664 [0.637, 0.688] | 0.667 | 0.660 | — |
| 40 | h9-track1-image-h9-D-t3 | image | 5 | 3 | gemini-3-flash | phase3c-t1-h9A | — | — | 0.663 [0.634, 0.689] | 0.675 | 0.651 | — |
| 41 | h9-track1-image-h9-C-img2 | image | 5 | 3 | gemini-3-flash | phase3c-t1-h9C-img2 | — | — | 0.663 [0.635, 0.687] | 0.692 | 0.636 | — |
| 42 | h9-track2-text-h9-E-p2 | text | 5 | 4 | gemini-3-flash | phase3c-t2-h9B-v2 | — | — | 0.661 [0.634, 0.693] | 0.649 | 0.673 | — |
| 43 | h9-track2-text-h9-B-v4 | text | 5 | 4 | gemini-3-flash | phase3c-t2-h9B-v4 | — | — | 0.658 [0.628, 0.682] | 0.670 | 0.647 | — |
| 44 | h9-track2-text-h9-E-p4 | text | 5 | 4 | gemini-3-flash | phase3c-t2-h9B-v4 | — | — | 0.658 [0.631, 0.690] | 0.669 | 0.647 | — |
| 45 | h9-track1-image-h9-D-t4 | image | 5 | 3 | gemini-3-flash | phase3c-t1-h9A | — | — | 0.657 [0.625, 0.682] | 0.679 | 0.636 | — |
| 46 | h9-track1-image-h9-E-p5 | image | 5 | 3 | gemini-3-flash | phase3c-t1-h9E-p5 | — | — | 0.656 [0.628, 0.683] | 0.681 | 0.633 | — |
| 47 | h9-track1-image-h9-B-v2 | image | 5 | 3 | gemini-3-flash | phase3c-t1-h9B-v2 | — | — | 0.655 [0.626, 0.680] | 0.672 | 0.638 | — |

## Tier 4 (F1: 0.612–0.652)

| # | Condition | Track | K | Vote t | Proposer | Config | Verifier | Prob t | F1 [95% CI] | P | R | MCC |
|--:|-----------|:-----:|--:|:-----:|:---------|:-------|:--------:|:-----:|:-----------:|---:|---:|---:|
| 48 | h9-track1-image-h9-E-p1 | image | 5 | 3 | gemini-3-flash | phase3c-t1-h9E-p1 | — | — | 0.652 [0.626, 0.678] | 0.621 | 0.686 | — |
| 49 | h9-track2-text-h9-E-p5 | text | 5 | 4 | gemini-3-flash | phase3c-t2-h9B-v5 | — | — | 0.650 [0.619, 0.679] | 0.690 | 0.614 | — |
| 50 | h9-track1-image-h9-B-v5 | image | 5 | 3 | gemini-3-flash | phase3c-t1-h9B-v5 | — | — | 0.649 [0.619, 0.680] | 0.651 | 0.647 | — |
| 51 | h1-brief-text | text | 3 | 3 | gemini-3-flash | detect_brief-text | — | — | 0.644 [0.613, 0.672] | 0.626 | 0.662 | — |
| 52 | h9-track1-image-h9-A-p3 | image | 5 | 3 | gemini-3-flash | phase3c-t1-h9A | — | — | 0.644 [0.616, 0.672] | 0.642 | 0.646 | — |
| 53 | h7-track2-text-T0.0 | text | 3 | 3 | gemini-3-flash | detect_brief-text | — | — | 0.643 [0.610, 0.673] | 0.540 | 0.796 | — |
| 54 | h7-track2-text-T1.0 | text | 3 | 3 | gemini-3-flash | detect_brief-text | — | — | 0.643 [0.615, 0.672] | 0.633 | 0.653 | — |
| 55 | h9-track1-image-h9-E-p4 | image | 5 | 3 | gemini-3-flash | phase3c-t1-h9E-p4 | — | — | 0.642 [0.616, 0.667] | 0.663 | 0.623 | — |
| 56 | h9-track1-image-h9-C-img1 | image | 5 | 3 | gemini-3-flash | phase3c-t1-h9C-img1 | — | — | 0.641 [0.611, 0.669] | 0.648 | 0.634 | — |
| 57 | h7-track2-text-T1.3 | text | 3 | 3 | gemini-3-flash | detect_brief-text | — | — | 0.640 [0.612, 0.674] | 0.645 | 0.636 | — |
| 58 | h9-track1-image-h9-B-v3 | image | 5 | 3 | gemini-3-flash | phase3c-t1-h9B-v3 | — | — | 0.640 [0.615, 0.668] | 0.640 | 0.640 | — |
| 59 | h7-track1-image-T1.0 | image | 3 | 2 | gemini-3-flash | detect_brief-text-image | — | — | 0.640 [0.614, 0.666] | 0.596 | 0.690 | — |
| 60 | h9-track2-text-h9-B-v3 | text | 5 | 4 | gemini-3-flash | phase3c-t2-h9B-v3 | — | — | 0.635 [0.607, 0.664] | 0.632 | 0.638 | — |
| 61 | h7-track1-image-T0.3 | image | 3 | 3 | gemini-3-flash | detect_brief-text-image | — | — | 0.634 [0.609, 0.659] | 0.622 | 0.647 | — |
| 62 | h9-track1-image-h9-B-v4 | image | 5 | 3 | gemini-3-flash | phase3c-t1-h9B-v4 | — | — | 0.632 [0.607, 0.659] | 0.633 | 0.631 | — |
| 63 | h9-track1-image-h9-E-p3 | image | 5 | 3 | gemini-3-flash | phase3c-t1-h9E-p3 | — | — | 0.628 [0.600, 0.653] | 0.629 | 0.627 | — |
| 64 | h1-verbose-text-image | image | 3 | 2 | gemini-3-flash | detect_verbose-text-image | — | — | 0.627 [0.603, 0.654] | 0.591 | 0.668 | — |
| 65 | h1-brief-text-image | image | 3 | 2 | gemini-3-flash | detect_brief-text-image | — | — | 0.624 [0.599, 0.650] | 0.582 | 0.672 | — |
| 66 | h7-track1-image-T0.7 | image | 3 | 2 | gemini-3-flash | detect_brief-text-image | — | — | 0.620 [0.593, 0.647] | 0.561 | 0.692 | — |
| 67 | h7-track1-image-T0.0 | image | 3 | 3 | gemini-3-flash | detect_brief-text-image | — | — | 0.613 [0.589, 0.639] | 0.540 | 0.709 | — |
| 68 | h9-track2-text-h9-E-p3 | text | 5 | 4 | gemini-3-flash | phase3c-t2-h9B-v3 | — | — | 0.612 [0.583, 0.642] | 0.603 | 0.622 | — |

## Tier 5 (F1: 0.575–0.606)

| # | Condition | Track | K | Vote t | Proposer | Config | Verifier | Prob t | F1 [95% CI] | P | R | MCC |
|--:|-----------|:-----:|--:|:-----:|:---------|:-------|:--------:|:-----:|:-----------:|---:|---:|---:|
| 69 | h7-track1-image-T1.3 | image | 3 | 2 | gemini-3-flash | detect_brief-text-image | — | — | 0.606 [0.583, 0.628] | 0.577 | 0.636 | — |
| 70 | h1-verbose-text | text | 3 | 2 | gemini-3-flash | detect_verbose-text | — | — | 0.596 [0.560, 0.625] | 0.510 | 0.716 | — |
| 71 | h1-image-only | image | 3 | 2 | gemini-3-flash | detect_image-only | — | — | 0.575 [0.547, 0.599] | 0.534 | 0.622 | — |

## Tier 6 (F1: 0.515–0.515)

| # | Condition | Track | K | Vote t | Proposer | Config | Verifier | Prob t | F1 [95% CI] | P | R | MCC |
|--:|-----------|:-----:|--:|:-----:|:---------|:-------|:--------:|:-----:|:-----------:|---:|---:|---:|
| 72 | h11-bridge-brief-text-t0 | text | 10 | 10 | gemini-3-flash-preview | detect_brief-text | — | — | 0.515 [0.474, 0.550] | 0.412 | 0.688 | — |

---

### Column reference

- **Vote t** — proposer-consensus vote threshold selected (the `t` value at which this condition's F1 at 20 m is maximal; for `single-pass` and `single-pass+PV` this is always 1).
- **Proposer** — proposer model (Gemini 3 Flash for the vast majority of the corpus).
- **Config** — the `config_version` string from the condition inventory — identifies the prompt library and major variant.
- **Verifier** — for PV pipelines, the verifier prompt label (`v1` = the canonical adversarial-text verifier; `session-78-<variant>` = one of the 7 S78 matrix verifiers).
- **Prob t** — verifier probability threshold (optimal at 20 m for each PV cell; `—` for non-PV architectures).
- **MCC** — Matthews Correlation Coefficient at the buffer. `—` when `evaluate_detections.py` did not emit MCC for this condition (legacy evaluation outputs, primarily Era 1).
