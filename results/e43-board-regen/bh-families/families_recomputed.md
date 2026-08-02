# Recomputed BH families with the E72 members dropped

> **Last revised**: 2026-08-02 (original publication — E72 remediation).

Benjamini–Hochberg (BH) false-discovery-rate correction at q = 0.05, applied within each declared family, with the coverage-confounded members removed. Raw p-values are read verbatim from the committed permutation artefacts; nothing was re-run.

## `results/pairwise/20m` — family `confirmatory`

Published family: 26 members. Dropped under E72: 3. Retained: 23. BH-significant among the retained members — published 17, recomputed 16.

Dropped members: group 4 — T=0.7 vs T=1.0 (N=5), group 4 — T=0.7 vs T=1.0 (N=10), group 4 — T=0.7 vs T=1.0 (N=30).

| Group | Question | Condition A | Condition B | p (raw) | q (published) | q (recomputed) | Changed |
|--:|---|---|---|---:|---:|---:|:--:|
| 1 | PV vs consensus | Flash HIGH text 16-of-30 + PV | Flash HIGH text 26-of-30 | 0.0000 | 0.0000 | 0.0000 | no |
| 1 | PV vs consensus | Flash HIGH text 9-of-10 + PV | Flash HIGH text 9-of-10 | 0.0000 | 0.0000 | 0.0000 | no |
| 1 | PV vs consensus | Flash HIGH text 4-of-5 + PV | Flash HIGH text 5-of-5 | 0.0000 | 0.0000 | 0.0000 | no |
| 1 | PV verifier thinking | Flash HIGH text 4-of-5 + medium vf | Flash HIGH text 5-of-5 | 0.0000 | 0.0000 | 0.0000 | no |
| 1 | PV vs consensus (image) | Flash HIGH image 3-of-5 + PV | Flash HIGH image 3-of-5 | 0.0004 | 0.0007 | 0.0008 | no |
| 1 | PV vs consensus (Pro) | Pro HIGH text 3-of-5 + PV | Pro HIGH text 3-of-5 | 0.2580 | 0.3049 | 0.3123 | no |
| 1 | PV on single-pass text | Text baseline + PV | Single-pass text 5-of-5 | 0.0000 | 0.0000 | 0.0000 | no |
| 1 | PV on single-pass image | Image baseline + PV | Single-pass text 5-of-5 | 0.0000 | 0.0000 | 0.0000 | no |
| 2 | Text vs image | Flash HIGH text 5-of-5 | Flash HIGH image 3-of-5 | 0.0143 | 0.0196 | 0.0206 | no |
| 2 | Text vs image (N=10) | Flash HIGH text 9-of-10 | Flash HIGH image 6-of-10 | 0.0054 | 0.0078 | 0.0083 | no |
| 2 | Text vs image (MINIMAL) | Flash MIN text 5-of-5 | Flash MIN image 4-of-5 | 0.3604 | 0.3904 | 0.3947 | no |
| 2 | Text vs image (PV) | Flash HIGH text 4-of-5 + PV | Flash HIGH image 3-of-5 + PV | 0.0000 | 0.0000 | 0.0000 | no |
| 3 | HIGH vs MINIMAL (text N=5) | Flash HIGH text 5-of-5 | Flash MIN text 5-of-5 | 0.0000 | 0.0000 | 0.0000 | no |
| 3 | HIGH vs MINIMAL (text N=10) | Flash HIGH text 9-of-10 | Flash MIN text 10-of-10 | 0.0000 | 0.0000 | 0.0000 | no |
| 3 | HIGH vs MINIMAL (text N=30) | Flash HIGH text 26-of-30 | Flash MIN text 29-of-30 | 0.0000 | 0.0000 | 0.0000 | no |
| 3 | HIGH vs MINIMAL (image N=5) | Flash HIGH image 3-of-5 | Flash MIN image 4-of-5 | 0.0003 | 0.0006 | 0.0006 | no |
| 5 | Pro vs Flash (text consensus) | Pro HIGH text 3-of-5 | Flash HIGH text 5-of-5 | 0.0042 | 0.0064 | 0.0069 | no |
| 5 | Pro vs Flash (image consensus) | Pro HIGH image 3-of-5 | Flash HIGH image 3-of-5 | 0.2939 | 0.3322 | 0.3380 | no |
| 5 | Pro vs Flash (PV text) | Pro HIGH text 3-of-5 + PV | Flash HIGH text 4-of-5 + PV | 0.4002 | 0.4162 | 0.4184 | no |
| 7 | N=10 vs N=5 (HIGH text) | Flash HIGH text 9-of-10 | Flash HIGH text 5-of-5 | 0.1404 | 0.1738 | 0.1794 | no |
| 7 | N=30 vs N=10 (HIGH text) | Flash HIGH text 26-of-30 | Flash HIGH text 9-of-10 | 0.0375 | 0.0488 | 0.0507 | yes |
| 7 | N=10 vs N=5 (MIN text) | Flash MIN text 10-of-10 | Flash MIN text 5-of-5 | 0.6338 | 0.6338 | 0.6338 | no |
| 7 | N=30 vs N=10 (MIN text) | Flash MIN text 29-of-30 | Flash MIN text 10-of-10 | 0.0005 | 0.0008 | 0.0009 | no |

## `results/pairwise/30m` — family `confirmatory`

Published family: 26 members. Dropped under E72: 3. Retained: 23. BH-significant among the retained members — published 15, recomputed 15.

Dropped members: group 4 — T=0.7 vs T=1.0 (N=5), group 4 — T=0.7 vs T=1.0 (N=10), group 4 — T=0.7 vs T=1.0 (N=30).

| Group | Question | Condition A | Condition B | p (raw) | q (published) | q (recomputed) | Changed |
|--:|---|---|---|---:|---:|---:|:--:|
| 1 | PV vs consensus | Flash HIGH text 16-of-30 + PV | Flash HIGH text 26-of-30 | 0.0000 | 0.0000 | 0.0000 | no |
| 1 | PV vs consensus | Flash HIGH text 9-of-10 + PV | Flash HIGH text 9-of-10 | 0.0000 | 0.0000 | 0.0000 | no |
| 1 | PV vs consensus | Flash HIGH text 4-of-5 + PV | Flash HIGH text 5-of-5 | 0.0000 | 0.0000 | 0.0000 | no |
| 1 | PV verifier thinking | Flash HIGH text 4-of-5 + medium vf | Flash HIGH text 5-of-5 | 0.0000 | 0.0000 | 0.0000 | no |
| 1 | PV vs consensus (image) | Flash HIGH image 3-of-5 + PV | Flash HIGH image 3-of-5 | 0.0002 | 0.0004 | 0.0004 | no |
| 1 | PV vs consensus (Pro) | Pro HIGH text 3-of-5 + PV | Pro HIGH text 3-of-5 | 0.2174 | 0.2569 | 0.2632 | no |
| 1 | PV on single-pass text | Text baseline + PV | Single-pass text 5-of-5 | 0.0000 | 0.0000 | 0.0000 | no |
| 1 | PV on single-pass image | Image baseline + PV | Single-pass text 5-of-5 | 0.0000 | 0.0000 | 0.0000 | no |
| 2 | Text vs image | Flash HIGH text 5-of-5 | Flash HIGH image 3-of-5 | 0.5589 | 0.6055 | 0.6121 | no |
| 2 | Text vs image (N=10) | Flash HIGH text 9-of-10 | Flash HIGH image 6-of-10 | 0.9561 | 0.9561 | 0.9561 | no |
| 2 | Text vs image (MINIMAL) | Flash MIN text 5-of-5 | Flash MIN image 4-of-5 | 0.0013 | 0.0020 | 0.0021 | no |
| 2 | Text vs image (PV) | Flash HIGH text 4-of-5 + PV | Flash HIGH image 3-of-5 + PV | 0.0120 | 0.0173 | 0.0184 | no |
| 3 | HIGH vs MINIMAL (text N=5) | Flash HIGH text 5-of-5 | Flash MIN text 5-of-5 | 0.0000 | 0.0000 | 0.0000 | no |
| 3 | HIGH vs MINIMAL (text N=10) | Flash HIGH text 9-of-10 | Flash MIN text 10-of-10 | 0.0000 | 0.0000 | 0.0000 | no |
| 3 | HIGH vs MINIMAL (text N=30) | Flash HIGH text 26-of-30 | Flash MIN text 29-of-30 | 0.0000 | 0.0000 | 0.0000 | no |
| 3 | HIGH vs MINIMAL (image N=5) | Flash HIGH image 3-of-5 | Flash MIN image 4-of-5 | 0.0000 | 0.0000 | 0.0000 | no |
| 5 | Pro vs Flash (text consensus) | Pro HIGH text 3-of-5 | Flash HIGH text 5-of-5 | 0.0010 | 0.0016 | 0.0018 | no |
| 5 | Pro vs Flash (image consensus) | Pro HIGH image 3-of-5 | Flash HIGH image 3-of-5 | 0.2507 | 0.2834 | 0.2883 | no |
| 5 | Pro vs Flash (PV text) | Pro HIGH text 3-of-5 + PV | Flash HIGH text 4-of-5 + PV | 0.1131 | 0.1400 | 0.1445 | no |
| 7 | N=10 vs N=5 (HIGH text) | Flash HIGH text 9-of-10 | Flash HIGH text 5-of-5 | 0.0607 | 0.0831 | 0.0873 | no |
| 7 | N=30 vs N=10 (HIGH text) | Flash HIGH text 26-of-30 | Flash HIGH text 9-of-10 | 0.0671 | 0.0872 | 0.0908 | no |
| 7 | N=10 vs N=5 (MIN text) | Flash MIN text 10-of-10 | Flash MIN text 5-of-5 | 0.6704 | 0.6972 | 0.7009 | no |
| 7 | N=30 vs N=10 (MIN text) | Flash MIN text 29-of-30 | Flash MIN text 10-of-10 | 0.0005 | 0.0009 | 0.0010 | no |

## `results/factor-analysis/factor_analysis_results.json` — family `temperature`

Published family: 6 members. Dropped under E72: 4. Retained: 2. BH-significant among the retained members — published 1, recomputed 1.

Dropped members: group 12 — T=0.7 vs T=1.0 (N=1, 384px), group 4 — T=0.7 vs T=1.0 (N=5), group 4 — T=0.7 vs T=1.0 (N=10), group 4 — T=0.7 vs T=1.0 (N=30).

| Group | Question | Condition A | Condition B | p (raw) | q (published) | q (recomputed) | Changed |
|--:|---|---|---|---:|---:|---:|:--:|
| 12 | T=0.7 vs T=1.0 (N=1, Phase 2b text) | P2b text T=0.7 run_1 | P2b text T=1.0 run_1 | 0.0055 | 0.0066 | 0.0110 | no |
| 12 | T=0.7 vs T=1.0 (N=1, Phase 2b image) | P2b image T=0.7 run_1 | P2b image T=1.0 run_1 | 0.4763 | 0.4763 | 0.4763 | no |
