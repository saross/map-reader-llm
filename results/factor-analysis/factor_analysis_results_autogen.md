# Factor Analysis: Pairwise Permutation Test Results

FDR-corrected (Benjamini-Hochberg, q=0.05) within each factor family.
Buffer: 20m | Permutations: 10,000 | Seed: 42

## Architecture (11/12 significant)

| Question | Condition A | Condition B | F1_A | F1_B | ΔF1 | p (raw) | p (adj) | Sig |
|---|---|---|---|---|---|---|---|---|
| N=1 vs consensus (FH text) | FH text run_1 (N=1) | FH text 5-of-5 consensus | 0.392 | 0.779 | -0.387 | 0.0000 | 0.0000 | *** |
| PV on single-pass text | Text baseline + PV | Single-pass text 5-of-5 | 0.814 | 0.544 | +0.270 | 0.0000 | 0.0000 | *** |
| N=1 vs consensus (FH image) | FH image run_1 (N=1) | FH image 3-of-5 consensus | 0.515 | 0.727 | -0.212 | 0.0000 | 0.0000 | *** |
| PV on single-pass image | Image baseline + PV | Single-pass text 5-of-5 | 0.717 | 0.544 | +0.173 | 0.0000 | 0.0000 | *** |
| N=1 vs consensus (FM text) | FM text run_1 (N=1) | FM text 5-of-5 consensus | 0.493 | 0.640 | -0.147 | 0.0000 | 0.0000 | *** |
| N=1 vs consensus (Pro text) | Pro text run_1 (N=1) | Pro text 3-of-5 consensus | 0.738 | 0.840 | -0.102 | 0.0000 | 0.0000 | *** |
| PV vs consensus | Flash HIGH text 4-of-5 + PV | Flash HIGH text 5-of-5 | 0.864 | 0.779 | +0.085 | 0.0000 | 0.0000 | *** |
| PV verifier thinking | Flash HIGH text 4-of-5 + medium vf | Flash HIGH text 5-of-5 | 0.859 | 0.779 | +0.080 | 0.0000 | 0.0000 | *** |
| PV vs consensus | Flash HIGH text 16-of-30 + PV | Flash HIGH text 26-of-30 | 0.890 | 0.814 | +0.076 | 0.0000 | 0.0000 | *** |
| PV vs consensus | Flash HIGH text 9-of-10 + PV | Flash HIGH text 9-of-10 | 0.856 | 0.797 | +0.060 | 0.0000 | 0.0000 | *** |
| PV vs consensus (image) | Flash HIGH image 3-of-5 + PV | Flash HIGH image 3-of-5 | 0.778 | 0.727 | +0.051 | 0.0004 | 0.0004 | *** |
| PV vs consensus (Pro) | Pro HIGH text 3-of-5 + PV | Pro HIGH text 3-of-5 | 0.849 | 0.840 | +0.009 | 0.2580 | 0.2580 | ns |

## Thinking (5/6 significant)

| Question | Condition A | Condition B | F1_A | F1_B | ΔF1 | p (raw) | p (adj) | Sig |
|---|---|---|---|---|---|---|---|---|
| HIGH vs MINIMAL (text N=10) | Flash HIGH text 9-of-10 | Flash MIN text 10-of-10 | 0.797 | 0.633 | +0.164 | 0.0000 | 0.0000 | *** |
| HIGH vs MINIMAL (text N=30) | Flash HIGH text 26-of-30 | Flash MIN text 29-of-30 | 0.814 | 0.661 | +0.153 | 0.0000 | 0.0000 | *** |
| HIGH vs MINIMAL (text N=5) | Flash HIGH text 5-of-5 | Flash MIN text 5-of-5 | 0.779 | 0.640 | +0.139 | 0.0000 | 0.0000 | *** |
| HIGH vs MINIMAL (N=1 text) | FH text run_1 (N=1) | FM text run_1 (N=1) | 0.392 | 0.493 | -0.101 | 0.0000 | 0.0000 | *** |
| HIGH vs MINIMAL (image N=5) | Flash HIGH image 3-of-5 | Flash MIN image 4-of-5 | 0.727 | 0.664 | +0.063 | 0.0003 | 0.0004 | *** |
| HIGH vs MINIMAL (N=1 image) | FH image run_1 (N=1) | FM image run_1 (N=1) | 0.515 | 0.560 | -0.045 | 0.0588 | 0.0588 | ns |

## Temperature (5/6 significant)

| Question | Condition A | Condition B | F1_A | F1_B | ΔF1 | p (raw) | p (adj) | Sig |
|---|---|---|---|---|---|---|---|---|
| T=0.7 vs T=1.0 (N=30) | Flash MIN text T=0.7 29-of-30 | Flash MIN text T=1.0 22-of-30 | 0.661 | 0.467 | +0.194 | 0.0000 | 0.0000 | *** |
| T=0.7 vs T=1.0 (N=10) | Flash MIN text T=0.7 10-of-10 | Flash MIN text T=1.0 9-of-10 | 0.633 | 0.462 | +0.172 | 0.0000 | 0.0000 | *** |
| T=0.7 vs T=1.0 (N=5) | Flash MIN text T=0.7 5-of-5 | Flash MIN text T=1.0 5-of-5 | 0.640 | 0.471 | +0.168 | 0.0000 | 0.0000 | *** |
| T=0.7 vs T=1.0 (N=1, 384px) | FM text T=0.7 run_1 (N=1) | FM text T=1.0 run_1 (N=1) | 0.493 | 0.390 | +0.103 | 0.0034 | 0.0051 | ** |
| T=0.7 vs T=1.0 (N=1, Phase 2b text) | P2b text T=0.7 run_1 | P2b text T=1.0 run_1 | 0.584 | 0.510 | +0.074 | 0.0055 | 0.0066 | ** |
| T=0.7 vs T=1.0 (N=1, Phase 2b image) | P2b image T=0.7 run_1 | P2b image T=1.0 run_1 | 0.536 | 0.521 | +0.015 | 0.4763 | 0.4763 | ns |

## Modality (8/9 significant)

| Question | Condition A | Condition B | F1_A | F1_B | ΔF1 | p (raw) | p (adj) | Sig |
|---|---|---|---|---|---|---|---|---|
| Text vs image (N=1, Pro) | Pro text run_1 (N=1) | Pro image run_1 (N=1) | 0.738 | 0.590 | +0.149 | 0.0000 | 0.0000 | *** |
| Text vs image (Pro consensus N=5) | Pro text 3-of-5 consensus | Pro image 3-of-5 consensus | 0.840 | 0.700 | +0.141 | 0.0000 | 0.0000 | *** |
| Text vs image (N=1, FH) | FH text run_1 (N=1) | FH image run_1 (N=1) | 0.392 | 0.515 | -0.123 | 0.0001 | 0.0002 | *** |
| Text vs image (baseline + PV) | Text baseline + PV | Image baseline + PV | 0.814 | 0.717 | +0.098 | 0.0000 | 0.0000 | *** |
| Text vs image (PV) | Flash HIGH text 4-of-5 + PV | Flash HIGH image 3-of-5 + PV | 0.864 | 0.778 | +0.086 | 0.0000 | 0.0000 | *** |
| Text vs image (N=1, FM) | FM text run_1 (N=1) | FM image run_1 (N=1) | 0.493 | 0.560 | -0.067 | 0.0158 | 0.0178 | * |
| Text vs image (N=10) | Flash HIGH text 9-of-10 | Flash HIGH image 6-of-10 | 0.797 | 0.740 | +0.057 | 0.0054 | 0.0081 | ** |
| Text vs image | Flash HIGH text 5-of-5 | Flash HIGH image 3-of-5 | 0.779 | 0.727 | +0.052 | 0.0143 | 0.0178 | * |
| Text vs image (MINIMAL) | Flash MIN text 5-of-5 | Flash MIN image 4-of-5 | 0.640 | 0.664 | -0.024 | 0.3604 | 0.3604 | ns |

## Prompt Engineering (0/28 significant)

| Question | Condition A | Condition B | F1_A | F1_B | ΔF1 | p (raw) | p (adj) | Sig |
|---|---|---|---|---|---|---|---|---|
| Example ordering | P2e canonical-last | P2e random | 0.631 | 0.571 | +0.061 | 0.0019 | 0.0532 | ns |
| Example ordering | P2e config-default | P2e random | 0.606 | 0.571 | +0.035 | 0.0563 | 0.5488 | ns |
| Example ordering | P2e canonical-first | P2e canonical-last | 0.599 | 0.631 | -0.033 | 0.1366 | 0.6375 | ns |
| Library composition (image) | P2c Image plus-hp | P2c Image pure-positive-canon | 0.599 | 0.568 | +0.031 | 0.0907 | 0.6349 | ns |
| Example ordering | P2e canonical-first | P2e random | 0.599 | 0.571 | +0.028 | 0.1218 | 0.6375 | ns |
| Example ordering | P2e canonical-last | P2e config-default | 0.631 | 0.606 | +0.026 | 0.1857 | 0.7428 | ns |
| Library composition (image) | P2c Image pure-positive-canon | P2c Image scale-8 | 0.568 | 0.587 | -0.019 | 0.2757 | 0.7957 | ns |
| Library composition (image) | P2c Image canonical | P2c Image plus-hp | 0.581 | 0.599 | -0.017 | 0.3691 | 0.7957 | ns |
| Library composition (image) | P2c Image pure-positive-canon | P2c Image scale-4 | 0.568 | 0.584 | -0.016 | 0.4653 | 0.7957 | ns |
| Text treatment (text) | P2d Text terse | P2d Text verbose | 0.598 | 0.583 | +0.015 | 0.4263 | 0.7957 | ns |
| Library composition (image) | P2c Image plus-hp | P2c Image scale-4 | 0.599 | 0.584 | +0.015 | 0.5115 | 0.7957 | ns |
| Library composition (image) | P2c Image canonical | P2c Image pure-positive-canon | 0.581 | 0.568 | +0.014 | 0.4001 | 0.7957 | ns |
| Library composition (text) | P2c Text plus-hp | P2c Text scale-4 | 0.597 | 0.609 | -0.013 | 0.0588 | 0.5488 | ns |
| Library composition (image) | P2c Image plus-hp | P2c Image scale-8 | 0.599 | 0.587 | +0.012 | 0.4983 | 0.7957 | ns |
| Library composition (text) | P2c Text plus-hp | P2c Text scale-8 | 0.597 | 0.607 | -0.010 | 0.3089 | 0.7957 | ns |
| Library composition (text) | P2c Text plus-hp | P2c Text pure-positive-canon | 0.597 | 0.605 | -0.008 | 0.6080 | 0.8147 | ns |
| Library composition (text) | P2c Text canonical | P2c Text plus-hp | 0.605 | 0.597 | +0.007 | 0.5630 | 0.8147 | ns |
| Example ordering | P2e canonical-first | P2e config-default | 0.599 | 0.606 | -0.007 | 0.6401 | 0.8147 | ns |
| Library composition (image) | P2c Image canonical | P2c Image scale-8 | 0.581 | 0.587 | -0.005 | 0.7611 | 0.9266 | ns |
| Library composition (text) | P2c Text canonical | P2c Text scale-4 | 0.605 | 0.609 | -0.005 | 0.6216 | 0.8147 | ns |
| Library composition (text) | P2c Text pure-positive-canon | P2c Text scale-4 | 0.605 | 0.609 | -0.005 | 0.2623 | 0.7957 | ns |
| Library composition (image) | P2c Image scale-4 | P2c Image scale-8 | 0.584 | 0.587 | -0.003 | 0.8880 | 0.9497 | ns |
| Library composition (text) | P2c Text canonical | P2c Text scale-8 | 0.605 | 0.607 | -0.003 | 0.8057 | 0.9400 | ns |
| Library composition (text) | P2c Text pure-positive-canon | P2c Text scale-8 | 0.605 | 0.607 | -0.003 | 0.4549 | 0.7957 | ns |
| Text treatment (image) | P2d Image terse | P2d Image verbose | 0.605 | 0.603 | +0.003 | 0.8779 | 0.9497 | ns |
| Library composition (text) | P2c Text scale-4 | P2c Text scale-8 | 0.609 | 0.607 | +0.002 | 0.4338 | 0.7957 | ns |
| Library composition (image) | P2c Image canonical | P2c Image scale-4 | 0.581 | 0.584 | -0.002 | 0.9158 | 0.9497 | ns |
| Library composition (text) | P2c Text canonical | P2c Text pure-positive-canon | 0.605 | 0.605 | -0.000 | 1.0000 | 1.0000 | ns |

