# Monte-Carlo precision flags

**Generated**: Session 79 redesign (2026-04-25)

Pairwise tests where the observed null-difference count is <= 5 (i.e., p <= 5/N). These p-values are precision-limited by the permutation count; the true p might be much smaller but cannot be distinguished from N=10K. For tests where the observed count is 0/N, the only valid conclusion is `p < 1/N`.

Total flagged tests: 2748
Of which p == 0/N (cannot bound below 1/N): 2238

## Recommendations

If a paper-citation hinges on a flagged comparison, re-run that pair at N=100,000 permutations to either tighten the p-value or bound it more precisely.

## Flagged pairs

| Era | Arch | Metric | Label A | Label B | p | approx null count | zero count? |
|---:|:---|:---|:---|:---|---:|---:|:---:|
| 1 | single-pass | mcc | `h5-track1-image-verbose` | `h8-track1-image-plus-hp` | 0.0002 | 2 |  |
| 1 | single-pass | mcc | `h5-track1-image-verbose` | `h8-track1-image-scale-4` | 0.0002 | 2 |  |
| 1 | single-pass | mcc | `h5-track1-image-verbose` | `h4-canonical-first` | 0.0002 | 2 |  |
| 1 | single-pass | mcc | `h5-track1-image-verbose` | `h8-track1-image-canonical` | 0.0003 | 3 |  |
| 1 | single-pass | mcc | `h5-track1-image-verbose` | `h4-random` | 0.0000 | 0 | Y |
| 1 | single-pass | mcc | `h5-track1-image-verbose` | `h8-track1-image-exploratory-pure-positive-canon` | 0.0002 | 2 |  |
| 1 | single-pass | mcc | `h5-track1-image-verbose` | `h5-track2-text-terse` | 0.0000 | 0 | Y |
| 1 | single-pass | mcc | `h5-track1-image-verbose` | `h8-track1-image-exploratory-pure-positive-2hp` | 0.0000 | 0 | Y |
| 1 | single-pass | mcc | `h5-track1-image-verbose` | `h8-track1-image-pure-positive-canon` | 0.0002 | 2 |  |
| 1 | single-pass | mcc | `h5-track1-image-verbose` | `h8-track2-text-canonical` | 0.0000 | 0 | Y |
| 1 | single-pass | mcc | `h5-track1-image-verbose` | `h5-track2-text-verbose` | 0.0000 | 0 | Y |
| 1 | single-pass | mcc | `h5-track1-image-verbose` | `h8-track2-text-plus-hp` | 0.0000 | 0 | Y |
| 1 | single-pass | mcc | `h5-track1-image-verbose` | `h8-track2-text-pure-positive-canon` | 0.0000 | 0 | Y |
| 1 | single-pass | mcc | `h5-track1-image-verbose` | `h8-track2-text-scale-4` | 0.0000 | 0 | Y |
| 1 | single-pass | mcc | `h5-track1-image-verbose` | `h8-track2-text-scale-8` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h3-high-track2-text-T1.0` | `h9-track2-text-h9-A-p2` | 0.0002 | 2 |  |
| 1 | consensus | f1 | `h3-high-track2-text-T1.0` | `h9-track2-text-h9-E-p1` | 0.0002 | 2 |  |
| 1 | consensus | f1 | `h3-high-track2-text-T1.0` | `h9-track2-text-h9-D-t5` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h3-high-track2-text-T1.0` | `h9-track2-text-h9-A-p5` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h3-high-track2-text-T1.0` | `h9-track2-text-h9-D-t2` | 0.0001 | 1 |  |
| 1 | consensus | f1 | `h3-high-track2-text-T1.0` | `h9-track2-text-h9-D-t3` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h3-high-track2-text-T1.0` | `h9-track2-text-h9-A-p3` | 0.0001 | 1 |  |
| 1 | consensus | f1 | `h3-high-track2-text-T1.0` | `h3-rep-minimal` | 0.0001 | 1 |  |
| 1 | consensus | f1 | `h3-high-track2-text-T1.0` | `h9-track2-text-h9-B-v1` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h3-high-track2-text-T1.0` | `h9-track1-image-h9-C-img5` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h3-high-track2-text-T1.0` | `h3-track1-image-T0.7` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h3-high-track2-text-T1.0` | `h3-track2-text-T0.3` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h3-high-track2-text-T1.0` | `h3-track2-text-T0.7` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h3-high-track2-text-T1.0` | `h7-track2-text-T0.7` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h3-high-track2-text-T1.0` | `h3-track2-text-T1.0` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h3-high-track2-text-T1.0` | `h9-track1-image-h9-A-p1` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h3-high-track2-text-T1.0` | `h7-track2-text-T0.3` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h3-high-track2-text-T1.0` | `h3-track1-image-T1.0` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h3-high-track2-text-T1.0` | `h9-track1-image-h9-A-p5` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h3-high-track2-text-T1.0` | `h9-track1-image-h9-E-p2` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h3-high-track2-text-T1.0` | `h9-track2-text-h9-B-v2` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h3-high-track2-text-T1.0` | `h9-track1-image-h9-D-t2` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h3-high-track2-text-T1.0` | `h9-track1-image-h9-C-img4` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h3-high-track2-text-T1.0` | `h9-track1-image-h9-D-t1` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h3-high-track2-text-T1.0` | `h9-track1-image-h9-D-t5` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h3-high-track2-text-T1.0` | `h9-track2-text-h9-B-v5` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h3-high-track2-text-T1.0` | `h3-track1-image-T0.3` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h3-high-track2-text-T1.0` | `h9-track1-image-h9-A-p4` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h3-high-track2-text-T1.0` | `h9-track1-image-h9-B-v1` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h3-high-track2-text-T1.0` | `h9-track1-image-h9-A-p2` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h3-high-track2-text-T1.0` | `h9-track1-image-h9-D-t3` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h3-high-track2-text-T1.0` | `h9-track1-image-h9-C-img3` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h3-high-track2-text-T1.0` | `h9-track1-image-h9-C-img2` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h3-high-track2-text-T1.0` | `h9-track2-text-h9-B-v4` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h3-high-track2-text-T1.0` | `h9-track2-text-h9-E-p2` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h3-high-track2-text-T1.0` | `h9-track2-text-h9-E-p4` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h3-high-track2-text-T1.0` | `h9-track1-image-h9-D-t4` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h3-high-track2-text-T1.0` | `h9-track1-image-h9-B-v2` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h3-high-track2-text-T1.0` | `h9-track2-text-h9-E-p5` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h3-high-track2-text-T1.0` | `h9-track1-image-h9-E-p5` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h3-high-track2-text-T1.0` | `h9-track1-image-h9-E-p1` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h3-high-track2-text-T1.0` | `h1-brief-text` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h3-high-track2-text-T1.0` | `h9-track1-image-h9-B-v5` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h3-high-track2-text-T1.0` | `h9-track1-image-h9-A-p3` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h3-high-track2-text-T1.0` | `h7-track2-text-T1.0` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h3-high-track2-text-T1.0` | `h9-track1-image-h9-E-p4` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h3-high-track2-text-T1.0` | `h7-track2-text-T0.0` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h3-high-track2-text-T1.0` | `h9-track1-image-h9-C-img1` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h3-high-track2-text-T1.0` | `h7-track2-text-T1.3` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h3-high-track2-text-T1.0` | `h9-track1-image-h9-B-v3` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h3-high-track2-text-T1.0` | `h9-track2-text-h9-B-v3` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h3-high-track2-text-T1.0` | `h7-track1-image-T1.0` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h3-high-track2-text-T1.0` | `h9-track1-image-h9-B-v4` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h3-high-track2-text-T1.0` | `h7-track1-image-T0.3` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h3-high-track2-text-T1.0` | `h9-track1-image-h9-E-p3` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h3-high-track2-text-T1.0` | `h1-verbose-text-image` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h3-high-track2-text-T1.0` | `h1-brief-text-image` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h3-high-track2-text-T1.0` | `h9-track2-text-h9-E-p3` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h3-high-track2-text-T1.0` | `h7-track1-image-T0.7` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h3-high-track2-text-T1.0` | `h7-track1-image-T0.0` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h3-high-track2-text-T1.0` | `h7-track1-image-T1.3` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h3-high-track2-text-T1.0` | `h1-verbose-text` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h3-high-track2-text-T1.0` | `h1-image-only` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h3-high-track2-text-T1.0` | `h11-bridge-brief-text-t0` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h3-high-track2-text-T0.3` | `h9-track2-text-h9-A-p1` | 0.0005 | 5 |  |
| 1 | consensus | f1 | `h3-high-track2-text-T0.3` | `h9-track2-text-h9-A-p2` | 0.0001 | 1 |  |
| 1 | consensus | f1 | `h3-high-track2-text-T0.3` | `h9-track2-text-h9-E-p1` | 0.0001 | 1 |  |
| 1 | consensus | f1 | `h3-high-track2-text-T0.3` | `h9-track2-text-h9-D-t2` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h3-high-track2-text-T0.3` | `h9-track2-text-h9-A-p5` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h3-high-track2-text-T0.3` | `h9-track2-text-h9-D-t3` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h3-high-track2-text-T0.3` | `h9-track2-text-h9-D-t5` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h3-high-track2-text-T0.3` | `h9-track2-text-h9-A-p3` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h3-high-track2-text-T0.3` | `h9-track2-text-h9-B-v1` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h3-high-track2-text-T0.3` | `h3-track2-text-T0.3` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h3-high-track2-text-T0.3` | `h3-track2-text-T0.7` | 0.0001 | 1 |  |
| 1 | consensus | f1 | `h3-high-track2-text-T0.3` | `h9-track1-image-h9-C-img5` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h3-high-track2-text-T0.3` | `h3-track1-image-T0.7` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h3-high-track2-text-T0.3` | `h7-track2-text-T0.7` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h3-high-track2-text-T0.3` | `h3-track2-text-T1.0` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h3-high-track2-text-T0.3` | `h9-track1-image-h9-A-p1` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h3-high-track2-text-T0.3` | `h7-track2-text-T0.3` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h3-high-track2-text-T0.3` | `h3-track1-image-T1.0` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h3-high-track2-text-T0.3` | `h9-track1-image-h9-A-p5` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h3-high-track2-text-T0.3` | `h9-track1-image-h9-E-p2` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h3-high-track2-text-T0.3` | `h9-track2-text-h9-B-v2` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h3-high-track2-text-T0.3` | `h9-track1-image-h9-D-t2` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h3-high-track2-text-T0.3` | `h9-track1-image-h9-C-img4` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h3-high-track2-text-T0.3` | `h9-track1-image-h9-D-t1` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h3-high-track2-text-T0.3` | `h9-track1-image-h9-D-t5` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h3-high-track2-text-T0.3` | `h9-track2-text-h9-B-v5` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h3-high-track2-text-T0.3` | `h3-track1-image-T0.3` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h3-high-track2-text-T0.3` | `h9-track1-image-h9-A-p4` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h3-high-track2-text-T0.3` | `h9-track1-image-h9-A-p2` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h3-high-track2-text-T0.3` | `h9-track1-image-h9-B-v1` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h3-high-track2-text-T0.3` | `h9-track1-image-h9-C-img3` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h3-high-track2-text-T0.3` | `h9-track1-image-h9-D-t3` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h3-high-track2-text-T0.3` | `h9-track1-image-h9-C-img2` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h3-high-track2-text-T0.3` | `h9-track2-text-h9-B-v4` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h3-high-track2-text-T0.3` | `h9-track2-text-h9-E-p2` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h3-high-track2-text-T0.3` | `h9-track2-text-h9-E-p4` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h3-high-track2-text-T0.3` | `h9-track1-image-h9-D-t4` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h3-high-track2-text-T0.3` | `h9-track1-image-h9-E-p5` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h3-high-track2-text-T0.3` | `h9-track1-image-h9-B-v2` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h3-high-track2-text-T0.3` | `h9-track2-text-h9-E-p5` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h3-high-track2-text-T0.3` | `h9-track1-image-h9-E-p1` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h3-high-track2-text-T0.3` | `h9-track1-image-h9-B-v5` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h3-high-track2-text-T0.3` | `h1-brief-text` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h3-high-track2-text-T0.3` | `h9-track1-image-h9-A-p3` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h3-high-track2-text-T0.3` | `h7-track2-text-T0.0` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h3-high-track2-text-T0.3` | `h7-track2-text-T1.0` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h3-high-track2-text-T0.3` | `h9-track1-image-h9-E-p4` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h3-high-track2-text-T0.3` | `h7-track2-text-T1.3` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h3-high-track2-text-T0.3` | `h9-track1-image-h9-C-img1` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h3-high-track2-text-T0.3` | `h9-track1-image-h9-B-v3` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h3-high-track2-text-T0.3` | `h7-track1-image-T1.0` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h3-high-track2-text-T0.3` | `h9-track2-text-h9-B-v3` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h3-high-track2-text-T0.3` | `h7-track1-image-T0.3` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h3-high-track2-text-T0.3` | `h9-track1-image-h9-B-v4` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h3-high-track2-text-T0.3` | `h9-track1-image-h9-E-p3` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h3-high-track2-text-T0.3` | `h1-verbose-text-image` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h3-high-track2-text-T0.3` | `h1-brief-text-image` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h3-high-track2-text-T0.3` | `h7-track1-image-T0.7` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h3-high-track2-text-T0.3` | `h7-track1-image-T0.0` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h3-high-track2-text-T0.3` | `h9-track2-text-h9-E-p3` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h3-high-track2-text-T0.3` | `h7-track1-image-T1.3` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h3-high-track2-text-T0.3` | `h1-verbose-text` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h3-high-track2-text-T0.3` | `h1-image-only` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h3-high-track2-text-T0.3` | `h11-bridge-brief-text-t0` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h3-high-track2-text-T0.7` | `h9-track2-text-h9-A-p2` | 0.0005 | 5 |  |
| 1 | consensus | f1 | `h3-high-track2-text-T0.7` | `h9-track2-text-h9-D-t2` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h3-high-track2-text-T0.7` | `h9-track2-text-h9-A-p5` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h3-high-track2-text-T0.7` | `h9-track2-text-h9-D-t3` | 0.0001 | 1 |  |
| 1 | consensus | f1 | `h3-high-track2-text-T0.7` | `h9-track2-text-h9-D-t5` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h3-high-track2-text-T0.7` | `h9-track2-text-h9-A-p3` | 0.0002 | 2 |  |
| 1 | consensus | f1 | `h3-high-track2-text-T0.7` | `h9-track2-text-h9-B-v1` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h3-high-track2-text-T0.7` | `h3-track2-text-T0.3` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h3-high-track2-text-T0.7` | `h3-track2-text-T0.7` | 0.0002 | 2 |  |
| 1 | consensus | f1 | `h3-high-track2-text-T0.7` | `h3-track1-image-T0.7` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h3-high-track2-text-T0.7` | `h9-track1-image-h9-C-img5` | 0.0001 | 1 |  |
| 1 | consensus | f1 | `h3-high-track2-text-T0.7` | `h7-track2-text-T0.7` | 0.0002 | 2 |  |
| 1 | consensus | f1 | `h3-high-track2-text-T0.7` | `h3-track2-text-T1.0` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h3-high-track2-text-T0.7` | `h9-track1-image-h9-A-p1` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h3-high-track2-text-T0.7` | `h7-track2-text-T0.3` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h3-high-track2-text-T0.7` | `h3-track1-image-T1.0` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h3-high-track2-text-T0.7` | `h9-track1-image-h9-A-p5` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h3-high-track2-text-T0.7` | `h9-track1-image-h9-E-p2` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h3-high-track2-text-T0.7` | `h9-track2-text-h9-B-v2` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h3-high-track2-text-T0.7` | `h9-track1-image-h9-D-t2` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h3-high-track2-text-T0.7` | `h9-track1-image-h9-D-t1` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h3-high-track2-text-T0.7` | `h9-track1-image-h9-C-img4` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h3-high-track2-text-T0.7` | `h9-track1-image-h9-D-t5` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h3-high-track2-text-T0.7` | `h9-track2-text-h9-B-v5` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h3-high-track2-text-T0.7` | `h3-track1-image-T0.3` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h3-high-track2-text-T0.7` | `h9-track1-image-h9-A-p4` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h3-high-track2-text-T0.7` | `h9-track1-image-h9-A-p2` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h3-high-track2-text-T0.7` | `h9-track1-image-h9-B-v1` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h3-high-track2-text-T0.7` | `h9-track1-image-h9-C-img3` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h3-high-track2-text-T0.7` | `h9-track1-image-h9-D-t3` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h3-high-track2-text-T0.7` | `h9-track1-image-h9-C-img2` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h3-high-track2-text-T0.7` | `h9-track2-text-h9-E-p2` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h3-high-track2-text-T0.7` | `h9-track2-text-h9-B-v4` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h3-high-track2-text-T0.7` | `h9-track2-text-h9-E-p4` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h3-high-track2-text-T0.7` | `h9-track1-image-h9-D-t4` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h3-high-track2-text-T0.7` | `h9-track1-image-h9-E-p5` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h3-high-track2-text-T0.7` | `h9-track1-image-h9-B-v2` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h3-high-track2-text-T0.7` | `h9-track2-text-h9-E-p5` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h3-high-track2-text-T0.7` | `h9-track1-image-h9-E-p1` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h3-high-track2-text-T0.7` | `h1-brief-text` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h3-high-track2-text-T0.7` | `h9-track1-image-h9-B-v5` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h3-high-track2-text-T0.7` | `h9-track1-image-h9-A-p3` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h3-high-track2-text-T0.7` | `h7-track2-text-T0.0` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h3-high-track2-text-T0.7` | `h7-track2-text-T1.0` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h3-high-track2-text-T0.7` | `h9-track1-image-h9-E-p4` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h3-high-track2-text-T0.7` | `h9-track1-image-h9-C-img1` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h3-high-track2-text-T0.7` | `h7-track2-text-T1.3` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h3-high-track2-text-T0.7` | `h9-track1-image-h9-B-v3` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h3-high-track2-text-T0.7` | `h9-track2-text-h9-B-v3` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h3-high-track2-text-T0.7` | `h7-track1-image-T1.0` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h3-high-track2-text-T0.7` | `h7-track1-image-T0.3` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h3-high-track2-text-T0.7` | `h9-track1-image-h9-B-v4` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h3-high-track2-text-T0.7` | `h9-track1-image-h9-E-p3` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h3-high-track2-text-T0.7` | `h1-verbose-text-image` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h3-high-track2-text-T0.7` | `h1-brief-text-image` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h3-high-track2-text-T0.7` | `h7-track1-image-T0.7` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h3-high-track2-text-T0.7` | `h9-track2-text-h9-E-p3` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h3-high-track2-text-T0.7` | `h7-track1-image-T0.0` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h3-high-track2-text-T0.7` | `h7-track1-image-T1.3` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h3-high-track2-text-T0.7` | `h1-verbose-text` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h3-high-track2-text-T0.7` | `h1-image-only` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h3-high-track2-text-T0.7` | `h11-bridge-brief-text-t0` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h3-rep-high` | `h9-track2-text-h9-A-p5` | 0.0002 | 2 |  |
| 1 | consensus | f1 | `h3-rep-high` | `h9-track2-text-h9-D-t2` | 0.0002 | 2 |  |
| 1 | consensus | f1 | `h3-rep-high` | `h9-track2-text-h9-D-t3` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h3-rep-high` | `h9-track2-text-h9-D-t5` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h3-rep-high` | `h3-rep-minimal` | 0.0004 | 4 |  |
| 1 | consensus | f1 | `h3-rep-high` | `h9-track2-text-h9-A-p3` | 0.0001 | 1 |  |
| 1 | consensus | f1 | `h3-rep-high` | `h9-track2-text-h9-B-v1` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h3-rep-high` | `h3-track2-text-T0.3` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h3-rep-high` | `h3-track2-text-T0.7` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h3-rep-high` | `h3-track1-image-T0.7` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h3-rep-high` | `h9-track1-image-h9-C-img5` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h3-rep-high` | `h7-track2-text-T0.7` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h3-rep-high` | `h3-track2-text-T1.0` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h3-rep-high` | `h7-track2-text-T0.3` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h3-rep-high` | `h9-track1-image-h9-A-p1` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h3-rep-high` | `h9-track1-image-h9-A-p5` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h3-rep-high` | `h3-track1-image-T1.0` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h3-rep-high` | `h9-track2-text-h9-B-v2` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h3-rep-high` | `h9-track1-image-h9-E-p2` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h3-rep-high` | `h9-track1-image-h9-D-t2` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h3-rep-high` | `h9-track1-image-h9-D-t5` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h3-rep-high` | `h9-track1-image-h9-C-img4` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h3-rep-high` | `h9-track1-image-h9-D-t1` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h3-rep-high` | `h9-track2-text-h9-B-v5` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h3-rep-high` | `h3-track1-image-T0.3` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h3-rep-high` | `h9-track1-image-h9-A-p4` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h3-rep-high` | `h9-track1-image-h9-A-p2` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h3-rep-high` | `h9-track1-image-h9-B-v1` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h3-rep-high` | `h9-track1-image-h9-C-img3` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h3-rep-high` | `h9-track1-image-h9-D-t3` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h3-rep-high` | `h9-track1-image-h9-C-img2` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h3-rep-high` | `h9-track2-text-h9-E-p2` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h3-rep-high` | `h9-track2-text-h9-B-v4` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h3-rep-high` | `h9-track2-text-h9-E-p4` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h3-rep-high` | `h9-track1-image-h9-D-t4` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h3-rep-high` | `h9-track1-image-h9-E-p5` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h3-rep-high` | `h9-track1-image-h9-B-v2` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h3-rep-high` | `h9-track1-image-h9-E-p1` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h3-rep-high` | `h9-track2-text-h9-E-p5` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h3-rep-high` | `h9-track1-image-h9-B-v5` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h3-rep-high` | `h1-brief-text` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h3-rep-high` | `h9-track1-image-h9-A-p3` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h3-rep-high` | `h7-track2-text-T1.0` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h3-rep-high` | `h7-track2-text-T0.0` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h3-rep-high` | `h9-track1-image-h9-E-p4` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h3-rep-high` | `h7-track2-text-T1.3` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h3-rep-high` | `h9-track1-image-h9-C-img1` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h3-rep-high` | `h9-track1-image-h9-B-v3` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h3-rep-high` | `h7-track1-image-T1.0` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h3-rep-high` | `h9-track2-text-h9-B-v3` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h3-rep-high` | `h7-track1-image-T0.3` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h3-rep-high` | `h9-track1-image-h9-B-v4` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h3-rep-high` | `h9-track1-image-h9-E-p3` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h3-rep-high` | `h1-brief-text-image` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h3-rep-high` | `h1-verbose-text-image` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h3-rep-high` | `h7-track1-image-T0.7` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h3-rep-high` | `h9-track2-text-h9-E-p3` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h3-rep-high` | `h7-track1-image-T0.0` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h3-rep-high` | `h7-track1-image-T1.3` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h3-rep-high` | `h1-image-only` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h3-rep-high` | `h1-verbose-text` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h3-rep-high` | `h11-bridge-brief-text-t0` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h9-track2-text-h9-D-t4` | `h9-track2-text-h9-B-v5` | 0.0005 | 5 |  |
| 1 | consensus | f1 | `h9-track2-text-h9-D-t4` | `h3-track1-image-T0.3` | 0.0003 | 3 |  |
| 1 | consensus | f1 | `h9-track2-text-h9-D-t4` | `h9-track2-text-h9-E-p2` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h9-track2-text-h9-D-t4` | `h9-track2-text-h9-B-v4` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h9-track2-text-h9-D-t4` | `h9-track2-text-h9-E-p4` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h9-track2-text-h9-D-t4` | `h9-track1-image-h9-E-p5` | 0.0001 | 1 |  |
| 1 | consensus | f1 | `h9-track2-text-h9-D-t4` | `h9-track1-image-h9-B-v2` | 0.0004 | 4 |  |
| 1 | consensus | f1 | `h9-track2-text-h9-D-t4` | `h9-track2-text-h9-E-p5` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h9-track2-text-h9-D-t4` | `h9-track1-image-h9-E-p1` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h9-track2-text-h9-D-t4` | `h1-brief-text` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h9-track2-text-h9-D-t4` | `h9-track1-image-h9-A-p3` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h9-track2-text-h9-D-t4` | `h7-track2-text-T0.0` | 0.0001 | 1 |  |
| 1 | consensus | f1 | `h9-track2-text-h9-D-t4` | `h7-track2-text-T1.0` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h9-track2-text-h9-D-t4` | `h9-track1-image-h9-E-p4` | 0.0001 | 1 |  |
| 1 | consensus | f1 | `h9-track2-text-h9-D-t4` | `h7-track2-text-T1.3` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h9-track2-text-h9-D-t4` | `h9-track1-image-h9-C-img1` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h9-track2-text-h9-D-t4` | `h9-track1-image-h9-B-v3` | 0.0001 | 1 |  |
| 1 | consensus | f1 | `h9-track2-text-h9-D-t4` | `h7-track1-image-T1.0` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h9-track2-text-h9-D-t4` | `h9-track2-text-h9-B-v3` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h9-track2-text-h9-D-t4` | `h7-track1-image-T0.3` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h9-track2-text-h9-D-t4` | `h9-track1-image-h9-B-v4` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h9-track2-text-h9-D-t4` | `h9-track1-image-h9-E-p3` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h9-track2-text-h9-D-t4` | `h1-verbose-text-image` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h9-track2-text-h9-D-t4` | `h1-brief-text-image` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h9-track2-text-h9-D-t4` | `h7-track1-image-T0.7` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h9-track2-text-h9-D-t4` | `h7-track1-image-T0.0` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h9-track2-text-h9-D-t4` | `h9-track2-text-h9-E-p3` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h9-track2-text-h9-D-t4` | `h7-track1-image-T1.3` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h9-track2-text-h9-D-t4` | `h1-verbose-text` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h9-track2-text-h9-D-t4` | `h1-image-only` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h9-track2-text-h9-D-t4` | `h11-bridge-brief-text-t0` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h9-track2-text-h9-D-t1` | `h9-track2-text-h9-B-v2` | 0.0003 | 3 |  |
| 1 | consensus | f1 | `h9-track2-text-h9-D-t1` | `h3-track1-image-T0.3` | 0.0005 | 5 |  |
| 1 | consensus | f1 | `h9-track2-text-h9-D-t1` | `h9-track2-text-h9-E-p2` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h9-track2-text-h9-D-t1` | `h9-track2-text-h9-B-v4` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h9-track2-text-h9-D-t1` | `h9-track2-text-h9-E-p4` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h9-track2-text-h9-D-t1` | `h9-track1-image-h9-E-p5` | 0.0004 | 4 |  |
| 1 | consensus | f1 | `h9-track2-text-h9-D-t1` | `h9-track1-image-h9-B-v2` | 0.0005 | 5 |  |
| 1 | consensus | f1 | `h9-track2-text-h9-D-t1` | `h9-track1-image-h9-E-p1` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h9-track2-text-h9-D-t1` | `h9-track2-text-h9-E-p5` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h9-track2-text-h9-D-t1` | `h1-brief-text` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h9-track2-text-h9-D-t1` | `h9-track1-image-h9-A-p3` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h9-track2-text-h9-D-t1` | `h7-track2-text-T1.0` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h9-track2-text-h9-D-t1` | `h7-track2-text-T0.0` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h9-track2-text-h9-D-t1` | `h9-track1-image-h9-E-p4` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h9-track2-text-h9-D-t1` | `h9-track1-image-h9-C-img1` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h9-track2-text-h9-D-t1` | `h7-track2-text-T1.3` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h9-track2-text-h9-D-t1` | `h9-track1-image-h9-B-v3` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h9-track2-text-h9-D-t1` | `h7-track1-image-T1.0` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h9-track2-text-h9-D-t1` | `h9-track2-text-h9-B-v3` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h9-track2-text-h9-D-t1` | `h9-track1-image-h9-B-v4` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h9-track2-text-h9-D-t1` | `h7-track1-image-T0.3` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h9-track2-text-h9-D-t1` | `h9-track1-image-h9-E-p3` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h9-track2-text-h9-D-t1` | `h1-verbose-text-image` | 0.0001 | 1 |  |
| 1 | consensus | f1 | `h9-track2-text-h9-D-t1` | `h1-brief-text-image` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h9-track2-text-h9-D-t1` | `h7-track1-image-T0.7` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h9-track2-text-h9-D-t1` | `h9-track2-text-h9-E-p3` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h9-track2-text-h9-D-t1` | `h7-track1-image-T0.0` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h9-track2-text-h9-D-t1` | `h7-track1-image-T1.3` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h9-track2-text-h9-D-t1` | `h1-image-only` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h9-track2-text-h9-D-t1` | `h1-verbose-text` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h9-track2-text-h9-D-t1` | `h11-bridge-brief-text-t0` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h9-track2-text-h9-A-p4` | `h9-track2-text-h9-B-v5` | 0.0005 | 5 |  |
| 1 | consensus | f1 | `h9-track2-text-h9-A-p4` | `h9-track2-text-h9-E-p2` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h9-track2-text-h9-A-p4` | `h9-track2-text-h9-B-v4` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h9-track2-text-h9-A-p4` | `h9-track2-text-h9-E-p4` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h9-track2-text-h9-A-p4` | `h9-track1-image-h9-E-p5` | 0.0005 | 5 |  |
| 1 | consensus | f1 | `h9-track2-text-h9-A-p4` | `h9-track1-image-h9-B-v2` | 0.0005 | 5 |  |
| 1 | consensus | f1 | `h9-track2-text-h9-A-p4` | `h9-track1-image-h9-E-p1` | 0.0003 | 3 |  |
| 1 | consensus | f1 | `h9-track2-text-h9-A-p4` | `h9-track2-text-h9-E-p5` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h9-track2-text-h9-A-p4` | `h1-brief-text` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h9-track2-text-h9-A-p4` | `h9-track1-image-h9-A-p3` | 0.0002 | 2 |  |
| 1 | consensus | f1 | `h9-track2-text-h9-A-p4` | `h7-track2-text-T1.0` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h9-track2-text-h9-A-p4` | `h7-track2-text-T0.0` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h9-track2-text-h9-A-p4` | `h9-track1-image-h9-E-p4` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h9-track2-text-h9-A-p4` | `h9-track1-image-h9-C-img1` | 0.0001 | 1 |  |
| 1 | consensus | f1 | `h9-track2-text-h9-A-p4` | `h7-track2-text-T1.3` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h9-track2-text-h9-A-p4` | `h9-track1-image-h9-B-v3` | 0.0003 | 3 |  |
| 1 | consensus | f1 | `h9-track2-text-h9-A-p4` | `h7-track1-image-T1.0` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h9-track2-text-h9-A-p4` | `h9-track2-text-h9-B-v3` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h9-track2-text-h9-A-p4` | `h7-track1-image-T0.3` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h9-track2-text-h9-A-p4` | `h9-track1-image-h9-B-v4` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h9-track2-text-h9-A-p4` | `h9-track1-image-h9-E-p3` | 0.0001 | 1 |  |
| 1 | consensus | f1 | `h9-track2-text-h9-A-p4` | `h1-verbose-text-image` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h9-track2-text-h9-A-p4` | `h1-brief-text-image` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h9-track2-text-h9-A-p4` | `h7-track1-image-T0.7` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h9-track2-text-h9-A-p4` | `h7-track1-image-T0.0` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h9-track2-text-h9-A-p4` | `h9-track2-text-h9-E-p3` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h9-track2-text-h9-A-p4` | `h7-track1-image-T1.3` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h9-track2-text-h9-A-p4` | `h1-verbose-text` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h9-track2-text-h9-A-p4` | `h1-image-only` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h9-track2-text-h9-A-p4` | `h11-bridge-brief-text-t0` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h9-track2-text-h9-A-p1` | `h9-track2-text-h9-E-p2` | 0.0003 | 3 |  |
| 1 | consensus | f1 | `h9-track2-text-h9-A-p1` | `h9-track2-text-h9-E-p4` | 0.0001 | 1 |  |
| 1 | consensus | f1 | `h9-track2-text-h9-A-p1` | `h9-track2-text-h9-B-v4` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h9-track2-text-h9-A-p1` | `h9-track1-image-h9-E-p5` | 0.0003 | 3 |  |
| 1 | consensus | f1 | `h9-track2-text-h9-A-p1` | `h9-track2-text-h9-E-p5` | 0.0001 | 1 |  |
| 1 | consensus | f1 | `h9-track2-text-h9-A-p1` | `h9-track1-image-h9-E-p1` | 0.0001 | 1 |  |
| 1 | consensus | f1 | `h9-track2-text-h9-A-p1` | `h1-brief-text` | 0.0004 | 4 |  |
| 1 | consensus | f1 | `h9-track2-text-h9-A-p1` | `h9-track1-image-h9-A-p3` | 0.0001 | 1 |  |
| 1 | consensus | f1 | `h9-track2-text-h9-A-p1` | `h7-track2-text-T0.0` | 0.0002 | 2 |  |
| 1 | consensus | f1 | `h9-track2-text-h9-A-p1` | `h7-track2-text-T1.0` | 0.0001 | 1 |  |
| 1 | consensus | f1 | `h9-track2-text-h9-A-p1` | `h9-track1-image-h9-E-p4` | 0.0001 | 1 |  |
| 1 | consensus | f1 | `h9-track2-text-h9-A-p1` | `h9-track1-image-h9-C-img1` | 0.0001 | 1 |  |
| 1 | consensus | f1 | `h9-track2-text-h9-A-p1` | `h7-track2-text-T1.3` | 0.0001 | 1 |  |
| 1 | consensus | f1 | `h9-track2-text-h9-A-p1` | `h9-track1-image-h9-B-v3` | 0.0004 | 4 |  |
| 1 | consensus | f1 | `h9-track2-text-h9-A-p1` | `h9-track2-text-h9-B-v3` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h9-track2-text-h9-A-p1` | `h7-track1-image-T1.0` | 0.0001 | 1 |  |
| 1 | consensus | f1 | `h9-track2-text-h9-A-p1` | `h7-track1-image-T0.3` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h9-track2-text-h9-A-p1` | `h9-track1-image-h9-E-p3` | 0.0001 | 1 |  |
| 1 | consensus | f1 | `h9-track2-text-h9-A-p1` | `h9-track1-image-h9-B-v4` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h9-track2-text-h9-A-p1` | `h1-verbose-text-image` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h9-track2-text-h9-A-p1` | `h1-brief-text-image` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h9-track2-text-h9-A-p1` | `h7-track1-image-T0.7` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h9-track2-text-h9-A-p1` | `h7-track1-image-T0.0` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h9-track2-text-h9-A-p1` | `h9-track2-text-h9-E-p3` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h9-track2-text-h9-A-p1` | `h7-track1-image-T1.3` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h9-track2-text-h9-A-p1` | `h1-verbose-text` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h9-track2-text-h9-A-p1` | `h1-image-only` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h9-track2-text-h9-A-p1` | `h11-bridge-brief-text-t0` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h9-track2-text-h9-A-p2` | `h9-track2-text-h9-E-p2` | 0.0002 | 2 |  |
| 1 | consensus | f1 | `h9-track2-text-h9-A-p2` | `h9-track2-text-h9-B-v4` | 0.0003 | 3 |  |
| 1 | consensus | f1 | `h9-track2-text-h9-A-p2` | `h9-track2-text-h9-E-p4` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h9-track2-text-h9-A-p2` | `h9-track2-text-h9-E-p5` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h9-track2-text-h9-A-p2` | `h9-track1-image-h9-E-p1` | 0.0002 | 2 |  |
| 1 | consensus | f1 | `h9-track2-text-h9-A-p2` | `h1-brief-text` | 0.0001 | 1 |  |
| 1 | consensus | f1 | `h9-track2-text-h9-A-p2` | `h9-track1-image-h9-A-p3` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h9-track2-text-h9-A-p2` | `h7-track2-text-T1.0` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h9-track2-text-h9-A-p2` | `h9-track1-image-h9-E-p4` | 0.0003 | 3 |  |
| 1 | consensus | f1 | `h9-track2-text-h9-A-p2` | `h9-track1-image-h9-C-img1` | 0.0002 | 2 |  |
| 1 | consensus | f1 | `h9-track2-text-h9-A-p2` | `h7-track2-text-T1.3` | 0.0002 | 2 |  |
| 1 | consensus | f1 | `h9-track2-text-h9-A-p2` | `h7-track1-image-T1.0` | 0.0001 | 1 |  |
| 1 | consensus | f1 | `h9-track2-text-h9-A-p2` | `h9-track2-text-h9-B-v3` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h9-track2-text-h9-A-p2` | `h7-track1-image-T0.3` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h9-track2-text-h9-A-p2` | `h9-track1-image-h9-B-v4` | 0.0001 | 1 |  |
| 1 | consensus | f1 | `h9-track2-text-h9-A-p2` | `h9-track1-image-h9-E-p3` | 0.0001 | 1 |  |
| 1 | consensus | f1 | `h9-track2-text-h9-A-p2` | `h1-verbose-text-image` | 0.0001 | 1 |  |
| 1 | consensus | f1 | `h9-track2-text-h9-A-p2` | `h1-brief-text-image` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h9-track2-text-h9-A-p2` | `h7-track1-image-T0.7` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h9-track2-text-h9-A-p2` | `h7-track1-image-T0.0` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h9-track2-text-h9-A-p2` | `h9-track2-text-h9-E-p3` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h9-track2-text-h9-A-p2` | `h7-track1-image-T1.3` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h9-track2-text-h9-A-p2` | `h1-verbose-text` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h9-track2-text-h9-A-p2` | `h1-image-only` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h9-track2-text-h9-A-p2` | `h11-bridge-brief-text-t0` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h9-track2-text-h9-E-p1` | `h9-track2-text-h9-E-p5` | 0.0001 | 1 |  |
| 1 | consensus | f1 | `h9-track2-text-h9-E-p1` | `h1-brief-text` | 0.0004 | 4 |  |
| 1 | consensus | f1 | `h9-track2-text-h9-E-p1` | `h7-track2-text-T1.3` | 0.0003 | 3 |  |
| 1 | consensus | f1 | `h9-track2-text-h9-E-p1` | `h7-track1-image-T1.0` | 0.0003 | 3 |  |
| 1 | consensus | f1 | `h9-track2-text-h9-E-p1` | `h9-track2-text-h9-B-v3` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h9-track2-text-h9-E-p1` | `h7-track1-image-T0.3` | 0.0001 | 1 |  |
| 1 | consensus | f1 | `h9-track2-text-h9-E-p1` | `h9-track1-image-h9-B-v4` | 0.0003 | 3 |  |
| 1 | consensus | f1 | `h9-track2-text-h9-E-p1` | `h9-track1-image-h9-E-p3` | 0.0002 | 2 |  |
| 1 | consensus | f1 | `h9-track2-text-h9-E-p1` | `h1-verbose-text-image` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h9-track2-text-h9-E-p1` | `h7-track1-image-T0.7` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h9-track2-text-h9-E-p1` | `h1-brief-text-image` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h9-track2-text-h9-E-p1` | `h7-track1-image-T0.0` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h9-track2-text-h9-E-p1` | `h9-track2-text-h9-E-p3` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h9-track2-text-h9-E-p1` | `h7-track1-image-T1.3` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h9-track2-text-h9-E-p1` | `h1-verbose-text` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h9-track2-text-h9-E-p1` | `h1-image-only` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h9-track2-text-h9-E-p1` | `h11-bridge-brief-text-t0` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h9-track2-text-h9-D-t2` | `h9-track2-text-h9-B-v3` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h9-track2-text-h9-D-t2` | `h1-brief-text-image` | 0.0002 | 2 |  |
| 1 | consensus | f1 | `h9-track2-text-h9-D-t2` | `h7-track1-image-T0.7` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h9-track2-text-h9-D-t2` | `h9-track2-text-h9-E-p3` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h9-track2-text-h9-D-t2` | `h7-track1-image-T0.0` | 0.0001 | 1 |  |
| 1 | consensus | f1 | `h9-track2-text-h9-D-t2` | `h7-track1-image-T1.3` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h9-track2-text-h9-D-t2` | `h1-image-only` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h9-track2-text-h9-D-t2` | `h1-verbose-text` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h9-track2-text-h9-D-t2` | `h11-bridge-brief-text-t0` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h9-track2-text-h9-A-p5` | `h7-track2-text-T1.0` | 0.0002 | 2 |  |
| 1 | consensus | f1 | `h9-track2-text-h9-A-p5` | `h9-track2-text-h9-B-v3` | 0.0003 | 3 |  |
| 1 | consensus | f1 | `h9-track2-text-h9-A-p5` | `h1-brief-text-image` | 0.0002 | 2 |  |
| 1 | consensus | f1 | `h9-track2-text-h9-A-p5` | `h7-track1-image-T0.7` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h9-track2-text-h9-A-p5` | `h9-track2-text-h9-E-p3` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h9-track2-text-h9-A-p5` | `h7-track1-image-T0.0` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h9-track2-text-h9-A-p5` | `h7-track1-image-T1.3` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h9-track2-text-h9-A-p5` | `h1-image-only` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h9-track2-text-h9-A-p5` | `h1-verbose-text` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h9-track2-text-h9-A-p5` | `h11-bridge-brief-text-t0` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h9-track2-text-h9-D-t3` | `h9-track2-text-h9-B-v3` | 0.0002 | 2 |  |
| 1 | consensus | f1 | `h9-track2-text-h9-D-t3` | `h1-brief-text-image` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h9-track2-text-h9-D-t3` | `h7-track1-image-T0.7` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h9-track2-text-h9-D-t3` | `h9-track2-text-h9-E-p3` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h9-track2-text-h9-D-t3` | `h7-track1-image-T0.0` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h9-track2-text-h9-D-t3` | `h7-track1-image-T1.3` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h9-track2-text-h9-D-t3` | `h1-verbose-text` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h9-track2-text-h9-D-t3` | `h1-image-only` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h9-track2-text-h9-D-t3` | `h11-bridge-brief-text-t0` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h9-track2-text-h9-D-t5` | `h7-track2-text-T1.3` | 0.0005 | 5 |  |
| 1 | consensus | f1 | `h9-track2-text-h9-D-t5` | `h9-track2-text-h9-B-v3` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h9-track2-text-h9-D-t5` | `h7-track1-image-T1.0` | 0.0004 | 4 |  |
| 1 | consensus | f1 | `h9-track2-text-h9-D-t5` | `h7-track1-image-T0.3` | 0.0003 | 3 |  |
| 1 | consensus | f1 | `h9-track2-text-h9-D-t5` | `h9-track1-image-h9-E-p3` | 0.0004 | 4 |  |
| 1 | consensus | f1 | `h9-track2-text-h9-D-t5` | `h1-verbose-text-image` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h9-track2-text-h9-D-t5` | `h1-brief-text-image` | 0.0001 | 1 |  |
| 1 | consensus | f1 | `h9-track2-text-h9-D-t5` | `h7-track1-image-T0.7` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h9-track2-text-h9-D-t5` | `h9-track2-text-h9-E-p3` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h9-track2-text-h9-D-t5` | `h7-track1-image-T0.0` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h9-track2-text-h9-D-t5` | `h7-track1-image-T1.3` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h9-track2-text-h9-D-t5` | `h1-image-only` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h9-track2-text-h9-D-t5` | `h1-verbose-text` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h9-track2-text-h9-D-t5` | `h11-bridge-brief-text-t0` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h9-track2-text-h9-A-p3` | `h9-track2-text-h9-B-v3` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h9-track2-text-h9-A-p3` | `h1-verbose-text-image` | 0.0004 | 4 |  |
| 1 | consensus | f1 | `h9-track2-text-h9-A-p3` | `h1-brief-text-image` | 0.0001 | 1 |  |
| 1 | consensus | f1 | `h9-track2-text-h9-A-p3` | `h7-track1-image-T0.7` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h9-track2-text-h9-A-p3` | `h9-track2-text-h9-E-p3` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h9-track2-text-h9-A-p3` | `h7-track1-image-T0.0` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h9-track2-text-h9-A-p3` | `h7-track1-image-T1.3` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h9-track2-text-h9-A-p3` | `h1-verbose-text` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h9-track2-text-h9-A-p3` | `h1-image-only` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h9-track2-text-h9-A-p3` | `h11-bridge-brief-text-t0` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h3-rep-minimal` | `h1-brief-text` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h3-rep-minimal` | `h7-track2-text-T1.0` | 0.0001 | 1 |  |
| 1 | consensus | f1 | `h3-rep-minimal` | `h7-track2-text-T1.3` | 0.0004 | 4 |  |
| 1 | consensus | f1 | `h3-rep-minimal` | `h9-track2-text-h9-E-p3` | 0.0002 | 2 |  |
| 1 | consensus | f1 | `h3-rep-minimal` | `h7-track1-image-T0.0` | 0.0002 | 2 |  |
| 1 | consensus | f1 | `h3-rep-minimal` | `h7-track1-image-T1.3` | 0.0002 | 2 |  |
| 1 | consensus | f1 | `h3-rep-minimal` | `h1-verbose-text` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h3-rep-minimal` | `h1-image-only` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h3-rep-minimal` | `h11-bridge-brief-text-t0` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h9-track2-text-h9-B-v1` | `h9-track2-text-h9-B-v3` | 0.0005 | 5 |  |
| 1 | consensus | f1 | `h9-track2-text-h9-B-v1` | `h7-track1-image-T0.7` | 0.0004 | 4 |  |
| 1 | consensus | f1 | `h9-track2-text-h9-B-v1` | `h9-track2-text-h9-E-p3` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h9-track2-text-h9-B-v1` | `h7-track1-image-T0.0` | 0.0001 | 1 |  |
| 1 | consensus | f1 | `h9-track2-text-h9-B-v1` | `h7-track1-image-T1.3` | 0.0001 | 1 |  |
| 1 | consensus | f1 | `h9-track2-text-h9-B-v1` | `h1-verbose-text` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h9-track2-text-h9-B-v1` | `h1-image-only` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h9-track2-text-h9-B-v1` | `h11-bridge-brief-text-t0` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h3-track2-text-T0.3` | `h7-track1-image-T1.3` | 0.0004 | 4 |  |
| 1 | consensus | f1 | `h3-track2-text-T0.3` | `h1-verbose-text` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h3-track2-text-T0.3` | `h1-image-only` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h3-track2-text-T0.3` | `h11-bridge-brief-text-t0` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h3-track2-text-T0.7` | `h1-brief-text` | 0.0005 | 5 |  |
| 1 | consensus | f1 | `h3-track2-text-T0.7` | `h1-verbose-text` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h3-track2-text-T0.7` | `h1-image-only` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h3-track2-text-T0.7` | `h11-bridge-brief-text-t0` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h3-track1-image-T0.7` | `h7-track1-image-T0.3` | 0.0003 | 3 |  |
| 1 | consensus | f1 | `h3-track1-image-T0.7` | `h1-verbose-text-image` | 0.0002 | 2 |  |
| 1 | consensus | f1 | `h3-track1-image-T0.7` | `h1-brief-text-image` | 0.0001 | 1 |  |
| 1 | consensus | f1 | `h3-track1-image-T0.7` | `h7-track1-image-T0.7` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h3-track1-image-T0.7` | `h7-track1-image-T0.0` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h3-track1-image-T0.7` | `h7-track1-image-T1.3` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h3-track1-image-T0.7` | `h1-verbose-text` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h3-track1-image-T0.7` | `h1-image-only` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h3-track1-image-T0.7` | `h11-bridge-brief-text-t0` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h9-track1-image-h9-C-img5` | `h9-track1-image-h9-B-v4` | 0.0002 | 2 |  |
| 1 | consensus | f1 | `h9-track1-image-h9-C-img5` | `h1-verbose-text-image` | 0.0001 | 1 |  |
| 1 | consensus | f1 | `h9-track1-image-h9-C-img5` | `h1-brief-text-image` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h9-track1-image-h9-C-img5` | `h7-track1-image-T0.7` | 0.0001 | 1 |  |
| 1 | consensus | f1 | `h9-track1-image-h9-C-img5` | `h7-track1-image-T0.0` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h9-track1-image-h9-C-img5` | `h7-track1-image-T1.3` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h9-track1-image-h9-C-img5` | `h1-image-only` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h9-track1-image-h9-C-img5` | `h1-verbose-text` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h9-track1-image-h9-C-img5` | `h11-bridge-brief-text-t0` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h7-track2-text-T0.7` | `h1-verbose-text` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h7-track2-text-T0.7` | `h1-image-only` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h7-track2-text-T0.7` | `h11-bridge-brief-text-t0` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h3-track2-text-T1.0` | `h1-verbose-text` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h3-track2-text-T1.0` | `h1-image-only` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h3-track2-text-T1.0` | `h11-bridge-brief-text-t0` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h7-track2-text-T0.3` | `h1-verbose-text` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h7-track2-text-T0.3` | `h1-image-only` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h7-track2-text-T0.3` | `h11-bridge-brief-text-t0` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h9-track1-image-h9-A-p1` | `h1-brief-text-image` | 0.0005 | 5 |  |
| 1 | consensus | f1 | `h9-track1-image-h9-A-p1` | `h7-track1-image-T0.7` | 0.0002 | 2 |  |
| 1 | consensus | f1 | `h9-track1-image-h9-A-p1` | `h7-track1-image-T0.0` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h9-track1-image-h9-A-p1` | `h7-track1-image-T1.3` | 0.0002 | 2 |  |
| 1 | consensus | f1 | `h9-track1-image-h9-A-p1` | `h1-image-only` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h9-track1-image-h9-A-p1` | `h11-bridge-brief-text-t0` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h9-track1-image-h9-A-p5` | `h7-track1-image-T0.0` | 0.0001 | 1 |  |
| 1 | consensus | f1 | `h9-track1-image-h9-A-p5` | `h7-track1-image-T1.3` | 0.0004 | 4 |  |
| 1 | consensus | f1 | `h9-track1-image-h9-A-p5` | `h1-image-only` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h9-track1-image-h9-A-p5` | `h11-bridge-brief-text-t0` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h3-track1-image-T1.0` | `h7-track1-image-T0.7` | 0.0003 | 3 |  |
| 1 | consensus | f1 | `h3-track1-image-T1.0` | `h7-track1-image-T0.0` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h3-track1-image-T1.0` | `h7-track1-image-T1.3` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h3-track1-image-T1.0` | `h1-image-only` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h3-track1-image-T1.0` | `h1-verbose-text` | 0.0001 | 1 |  |
| 1 | consensus | f1 | `h3-track1-image-T1.0` | `h11-bridge-brief-text-t0` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h9-track1-image-h9-E-p2` | `h7-track1-image-T0.0` | 0.0003 | 3 |  |
| 1 | consensus | f1 | `h9-track1-image-h9-E-p2` | `h7-track1-image-T1.3` | 0.0005 | 5 |  |
| 1 | consensus | f1 | `h9-track1-image-h9-E-p2` | `h1-image-only` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h9-track1-image-h9-E-p2` | `h11-bridge-brief-text-t0` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h9-track2-text-h9-B-v2` | `h1-verbose-text` | 0.0002 | 2 |  |
| 1 | consensus | f1 | `h9-track2-text-h9-B-v2` | `h1-image-only` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h9-track2-text-h9-B-v2` | `h11-bridge-brief-text-t0` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h9-track1-image-h9-D-t2` | `h7-track1-image-T0.0` | 0.0003 | 3 |  |
| 1 | consensus | f1 | `h9-track1-image-h9-D-t2` | `h1-image-only` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h9-track1-image-h9-D-t2` | `h11-bridge-brief-text-t0` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h9-track1-image-h9-C-img4` | `h1-image-only` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h9-track1-image-h9-C-img4` | `h11-bridge-brief-text-t0` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h9-track1-image-h9-D-t5` | `h1-image-only` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h9-track1-image-h9-D-t5` | `h11-bridge-brief-text-t0` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h9-track1-image-h9-D-t1` | `h1-image-only` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h9-track1-image-h9-D-t1` | `h11-bridge-brief-text-t0` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h9-track2-text-h9-B-v5` | `h1-image-only` | 0.0002 | 2 |  |
| 1 | consensus | f1 | `h9-track2-text-h9-B-v5` | `h11-bridge-brief-text-t0` | 0.0001 | 1 |  |
| 1 | consensus | f1 | `h3-track1-image-T0.3` | `h1-image-only` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h3-track1-image-T0.3` | `h11-bridge-brief-text-t0` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h9-track1-image-h9-A-p4` | `h1-image-only` | 0.0001 | 1 |  |
| 1 | consensus | f1 | `h9-track1-image-h9-A-p4` | `h11-bridge-brief-text-t0` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h9-track1-image-h9-A-p2` | `h1-image-only` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h9-track1-image-h9-A-p2` | `h11-bridge-brief-text-t0` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h9-track1-image-h9-B-v1` | `h1-image-only` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h9-track1-image-h9-B-v1` | `h11-bridge-brief-text-t0` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h9-track1-image-h9-C-img3` | `h1-image-only` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h9-track1-image-h9-C-img3` | `h11-bridge-brief-text-t0` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h9-track1-image-h9-D-t3` | `h1-image-only` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h9-track1-image-h9-D-t3` | `h11-bridge-brief-text-t0` | 0.0001 | 1 |  |
| 1 | consensus | f1 | `h9-track1-image-h9-C-img2` | `h1-image-only` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h9-track1-image-h9-C-img2` | `h11-bridge-brief-text-t0` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h9-track2-text-h9-E-p2` | `h1-image-only` | 0.0002 | 2 |  |
| 1 | consensus | f1 | `h9-track2-text-h9-E-p2` | `h11-bridge-brief-text-t0` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h9-track2-text-h9-B-v4` | `h1-image-only` | 0.0002 | 2 |  |
| 1 | consensus | f1 | `h9-track2-text-h9-B-v4` | `h11-bridge-brief-text-t0` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h9-track2-text-h9-E-p4` | `h1-image-only` | 0.0001 | 1 |  |
| 1 | consensus | f1 | `h9-track2-text-h9-E-p4` | `h11-bridge-brief-text-t0` | 0.0001 | 1 |  |
| 1 | consensus | f1 | `h9-track1-image-h9-D-t4` | `h1-image-only` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h9-track1-image-h9-D-t4` | `h11-bridge-brief-text-t0` | 0.0001 | 1 |  |
| 1 | consensus | f1 | `h9-track1-image-h9-E-p5` | `h1-image-only` | 0.0001 | 1 |  |
| 1 | consensus | f1 | `h9-track1-image-h9-E-p5` | `h11-bridge-brief-text-t0` | 0.0001 | 1 |  |
| 1 | consensus | f1 | `h9-track1-image-h9-B-v2` | `h1-image-only` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h9-track1-image-h9-B-v2` | `h11-bridge-brief-text-t0` | 0.0003 | 3 |  |
| 1 | consensus | f1 | `h9-track1-image-h9-E-p1` | `h1-image-only` | 0.0001 | 1 |  |
| 1 | consensus | f1 | `h9-track1-image-h9-E-p1` | `h11-bridge-brief-text-t0` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h9-track2-text-h9-E-p5` | `h11-bridge-brief-text-t0` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h9-track1-image-h9-B-v5` | `h11-bridge-brief-text-t0` | 0.0002 | 2 |  |
| 1 | consensus | f1 | `h1-brief-text` | `h11-bridge-brief-text-t0` | 0.0002 | 2 |  |
| 1 | consensus | f1 | `h9-track1-image-h9-A-p3` | `h1-image-only` | 0.0004 | 4 |  |
| 1 | consensus | f1 | `h9-track1-image-h9-A-p3` | `h11-bridge-brief-text-t0` | 0.0003 | 3 |  |
| 1 | consensus | f1 | `h7-track2-text-T0.0` | `h11-bridge-brief-text-t0` | 0.0000 | 0 | Y |
| 1 | consensus | f1 | `h7-track2-text-T1.0` | `h11-bridge-brief-text-t0` | 0.0001 | 1 |  |
| 1 | consensus | f1 | `h9-track1-image-h9-E-p4` | `h1-image-only` | 0.0001 | 1 |  |
| 1 | consensus | f1 | `h9-track1-image-h9-E-p4` | `h11-bridge-brief-text-t0` | 0.0004 | 4 |  |
| 1 | consensus | f1 | `h7-track2-text-T1.3` | `h11-bridge-brief-text-t0` | 0.0002 | 2 |  |
| 1 | consensus | f1 | `h7-track1-image-T1.0` | `h11-bridge-brief-text-t0` | 0.0004 | 4 |  |
| 1 | consensus | f1 | `h9-track2-text-h9-B-v3` | `h11-bridge-brief-text-t0` | 0.0004 | 4 |  |
| 1 | consensus | f1 | `h7-track1-image-T0.3` | `h11-bridge-brief-text-t0` | 0.0003 | 3 |  |
| 1 | consensus | mcc | `h9-track1-image-h9-B-v4` | `h9-track1-image-h9-C-img4` | 0.0001 | 1 |  |
| 1 | consensus | mcc | `h9-track1-image-h9-B-v4` | `h9-track2-text-h9-A-p1` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-B-v4` | `h9-track2-text-h9-B-v3` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-B-v4` | `h9-track2-text-h9-A-p4` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-B-v4` | `h9-track2-text-h9-A-p2` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-B-v4` | `h9-track2-text-h9-E-p1` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-B-v4` | `h9-track2-text-h9-D-t1` | 0.0001 | 1 |  |
| 1 | consensus | mcc | `h9-track1-image-h9-B-v4` | `h3-track1-image-T1.0` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-B-v4` | `h9-track2-text-h9-E-p3` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-B-v4` | `h9-track2-text-h9-D-t2` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-B-v4` | `h9-track2-text-h9-D-t3` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-B-v4` | `h3-track1-image-T0.7` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-B-v4` | `h9-track2-text-h9-A-p5` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-B-v4` | `h9-track2-text-h9-D-t5` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-B-v4` | `h9-track2-text-h9-B-v2` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-B-v4` | `h9-track2-text-h9-B-v5` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-B-v4` | `h9-track2-text-h9-D-t4` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-B-v4` | `h9-track2-text-h9-E-p2` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-B-v4` | `h9-track2-text-h9-A-p3` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-B-v4` | `h9-track2-text-h9-E-p5` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-B-v4` | `h9-track2-text-h9-E-p4` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-B-v4` | `h9-track2-text-h9-B-v1` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-B-v4` | `h1-verbose-text-image` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-B-v4` | `h7-track2-text-T1.3` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-B-v4` | `h7-track1-image-T1.3` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-B-v4` | `h7-track1-image-T1.0` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-B-v4` | `h9-track2-text-h9-B-v4` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-B-v4` | `h3-rep-minimal` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-B-v4` | `h3-track2-text-T1.0` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-B-v4` | `h1-brief-text-image` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-B-v4` | `h7-track2-text-T1.0` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-B-v4` | `h7-track2-text-T0.7` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-B-v4` | `h3-track1-image-T0.3` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-B-v4` | `h7-track1-image-T0.3` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-B-v4` | `h1-brief-text` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-B-v4` | `h3-track2-text-T0.7` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-B-v4` | `h1-image-only` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-B-v4` | `h7-track2-text-T0.3` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-B-v4` | `h7-track1-image-T0.7` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-B-v4` | `h1-verbose-text` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-B-v4` | `h3-track2-text-T0.3` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-B-v4` | `h7-track1-image-T0.0` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-B-v4` | `h11-bridge-brief-text-t0` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-B-v4` | `h7-track2-text-T0.0` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-A-p5` | `h9-track2-text-h9-B-v3` | 0.0001 | 1 |  |
| 1 | consensus | mcc | `h9-track1-image-h9-A-p5` | `h9-track2-text-h9-A-p1` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-A-p5` | `h9-track2-text-h9-A-p4` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-A-p5` | `h9-track2-text-h9-A-p2` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-A-p5` | `h9-track2-text-h9-D-t1` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-A-p5` | `h3-track1-image-T1.0` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-A-p5` | `h9-track2-text-h9-E-p1` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-A-p5` | `h9-track2-text-h9-D-t2` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-A-p5` | `h9-track2-text-h9-E-p3` | 0.0001 | 1 |  |
| 1 | consensus | mcc | `h9-track1-image-h9-A-p5` | `h3-track1-image-T0.7` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-A-p5` | `h9-track2-text-h9-D-t3` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-A-p5` | `h9-track2-text-h9-A-p5` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-A-p5` | `h9-track2-text-h9-D-t5` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-A-p5` | `h9-track2-text-h9-B-v2` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-A-p5` | `h9-track2-text-h9-D-t4` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-A-p5` | `h9-track2-text-h9-B-v5` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-A-p5` | `h9-track2-text-h9-E-p2` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-A-p5` | `h9-track2-text-h9-E-p5` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-A-p5` | `h9-track2-text-h9-E-p4` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-A-p5` | `h9-track2-text-h9-A-p3` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-A-p5` | `h9-track2-text-h9-B-v1` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-A-p5` | `h1-verbose-text-image` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-A-p5` | `h7-track2-text-T1.3` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-A-p5` | `h7-track1-image-T1.3` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-A-p5` | `h9-track2-text-h9-B-v4` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-A-p5` | `h7-track1-image-T1.0` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-A-p5` | `h3-track2-text-T1.0` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-A-p5` | `h3-rep-minimal` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-A-p5` | `h1-brief-text-image` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-A-p5` | `h7-track2-text-T1.0` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-A-p5` | `h7-track2-text-T0.7` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-A-p5` | `h3-track1-image-T0.3` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-A-p5` | `h7-track1-image-T0.3` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-A-p5` | `h3-track2-text-T0.7` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-A-p5` | `h1-brief-text` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-A-p5` | `h7-track1-image-T0.7` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-A-p5` | `h1-image-only` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-A-p5` | `h7-track2-text-T0.3` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-A-p5` | `h1-verbose-text` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-A-p5` | `h3-track2-text-T0.3` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-A-p5` | `h7-track1-image-T0.0` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-A-p5` | `h7-track2-text-T0.0` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-A-p5` | `h11-bridge-brief-text-t0` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-A-p3` | `h9-track2-text-h9-A-p1` | 0.0003 | 3 |  |
| 1 | consensus | mcc | `h9-track1-image-h9-A-p3` | `h9-track2-text-h9-B-v3` | 0.0001 | 1 |  |
| 1 | consensus | mcc | `h9-track1-image-h9-A-p3` | `h9-track2-text-h9-A-p4` | 0.0003 | 3 |  |
| 1 | consensus | mcc | `h9-track1-image-h9-A-p3` | `h9-track2-text-h9-A-p2` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-A-p3` | `h9-track2-text-h9-D-t1` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-A-p3` | `h3-track1-image-T1.0` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-A-p3` | `h9-track2-text-h9-E-p1` | 0.0001 | 1 |  |
| 1 | consensus | mcc | `h9-track1-image-h9-A-p3` | `h9-track2-text-h9-D-t2` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-A-p3` | `h9-track2-text-h9-E-p3` | 0.0001 | 1 |  |
| 1 | consensus | mcc | `h9-track1-image-h9-A-p3` | `h9-track2-text-h9-D-t3` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-A-p3` | `h3-track1-image-T0.7` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-A-p3` | `h9-track2-text-h9-A-p5` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-A-p3` | `h9-track2-text-h9-D-t5` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-A-p3` | `h9-track2-text-h9-B-v2` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-A-p3` | `h9-track2-text-h9-B-v5` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-A-p3` | `h9-track2-text-h9-D-t4` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-A-p3` | `h9-track2-text-h9-E-p2` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-A-p3` | `h9-track2-text-h9-E-p5` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-A-p3` | `h9-track2-text-h9-A-p3` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-A-p3` | `h9-track2-text-h9-E-p4` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-A-p3` | `h9-track2-text-h9-B-v1` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-A-p3` | `h1-verbose-text-image` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-A-p3` | `h7-track2-text-T1.3` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-A-p3` | `h7-track1-image-T1.3` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-A-p3` | `h9-track2-text-h9-B-v4` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-A-p3` | `h7-track1-image-T1.0` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-A-p3` | `h3-track2-text-T1.0` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-A-p3` | `h3-rep-minimal` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-A-p3` | `h1-brief-text-image` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-A-p3` | `h7-track2-text-T1.0` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-A-p3` | `h3-track1-image-T0.3` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-A-p3` | `h7-track2-text-T0.7` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-A-p3` | `h7-track1-image-T0.3` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-A-p3` | `h3-track2-text-T0.7` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-A-p3` | `h1-brief-text` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-A-p3` | `h1-image-only` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-A-p3` | `h7-track1-image-T0.7` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-A-p3` | `h7-track2-text-T0.3` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-A-p3` | `h1-verbose-text` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-A-p3` | `h3-track2-text-T0.3` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-A-p3` | `h7-track1-image-T0.0` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-A-p3` | `h11-bridge-brief-text-t0` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-A-p3` | `h7-track2-text-T0.0` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-D-t1` | `h9-track2-text-h9-A-p1` | 0.0002 | 2 |  |
| 1 | consensus | mcc | `h9-track1-image-h9-D-t1` | `h9-track2-text-h9-A-p4` | 0.0005 | 5 |  |
| 1 | consensus | mcc | `h9-track1-image-h9-D-t1` | `h9-track2-text-h9-B-v3` | 0.0005 | 5 |  |
| 1 | consensus | mcc | `h9-track1-image-h9-D-t1` | `h9-track2-text-h9-A-p2` | 0.0003 | 3 |  |
| 1 | consensus | mcc | `h9-track1-image-h9-D-t1` | `h9-track2-text-h9-D-t1` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-D-t1` | `h3-track1-image-T1.0` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-D-t1` | `h9-track2-text-h9-E-p1` | 0.0001 | 1 |  |
| 1 | consensus | mcc | `h9-track1-image-h9-D-t1` | `h9-track2-text-h9-D-t2` | 0.0002 | 2 |  |
| 1 | consensus | mcc | `h9-track1-image-h9-D-t1` | `h9-track2-text-h9-E-p3` | 0.0002 | 2 |  |
| 1 | consensus | mcc | `h9-track1-image-h9-D-t1` | `h9-track2-text-h9-D-t3` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-D-t1` | `h3-track1-image-T0.7` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-D-t1` | `h9-track2-text-h9-A-p5` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-D-t1` | `h9-track2-text-h9-D-t5` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-D-t1` | `h9-track2-text-h9-B-v2` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-D-t1` | `h9-track2-text-h9-B-v5` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-D-t1` | `h9-track2-text-h9-D-t4` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-D-t1` | `h9-track2-text-h9-E-p2` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-D-t1` | `h9-track2-text-h9-E-p5` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-D-t1` | `h9-track2-text-h9-A-p3` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-D-t1` | `h9-track2-text-h9-E-p4` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-D-t1` | `h9-track2-text-h9-B-v1` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-D-t1` | `h1-verbose-text-image` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-D-t1` | `h7-track2-text-T1.3` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-D-t1` | `h7-track1-image-T1.3` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-D-t1` | `h9-track2-text-h9-B-v4` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-D-t1` | `h7-track1-image-T1.0` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-D-t1` | `h3-track2-text-T1.0` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-D-t1` | `h3-rep-minimal` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-D-t1` | `h1-brief-text-image` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-D-t1` | `h7-track2-text-T1.0` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-D-t1` | `h3-track1-image-T0.3` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-D-t1` | `h7-track2-text-T0.7` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-D-t1` | `h7-track1-image-T0.3` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-D-t1` | `h3-track2-text-T0.7` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-D-t1` | `h1-brief-text` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-D-t1` | `h1-image-only` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-D-t1` | `h7-track1-image-T0.7` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-D-t1` | `h7-track2-text-T0.3` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-D-t1` | `h1-verbose-text` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-D-t1` | `h3-track2-text-T0.3` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-D-t1` | `h7-track1-image-T0.0` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-D-t1` | `h11-bridge-brief-text-t0` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-D-t1` | `h7-track2-text-T0.0` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-A-p4` | `h9-track2-text-h9-A-p4` | 0.0004 | 4 |  |
| 1 | consensus | mcc | `h9-track1-image-h9-A-p4` | `h9-track2-text-h9-A-p2` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-A-p4` | `h9-track2-text-h9-D-t1` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-A-p4` | `h3-track1-image-T1.0` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-A-p4` | `h9-track2-text-h9-E-p1` | 0.0001 | 1 |  |
| 1 | consensus | mcc | `h9-track1-image-h9-A-p4` | `h9-track2-text-h9-D-t2` | 0.0001 | 1 |  |
| 1 | consensus | mcc | `h9-track1-image-h9-A-p4` | `h9-track2-text-h9-E-p3` | 0.0002 | 2 |  |
| 1 | consensus | mcc | `h9-track1-image-h9-A-p4` | `h9-track2-text-h9-D-t3` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-A-p4` | `h3-track1-image-T0.7` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-A-p4` | `h9-track2-text-h9-A-p5` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-A-p4` | `h9-track2-text-h9-D-t5` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-A-p4` | `h9-track2-text-h9-B-v2` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-A-p4` | `h9-track2-text-h9-B-v5` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-A-p4` | `h9-track2-text-h9-D-t4` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-A-p4` | `h9-track2-text-h9-E-p2` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-A-p4` | `h9-track2-text-h9-E-p5` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-A-p4` | `h9-track2-text-h9-A-p3` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-A-p4` | `h9-track2-text-h9-E-p4` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-A-p4` | `h9-track2-text-h9-B-v1` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-A-p4` | `h1-verbose-text-image` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-A-p4` | `h7-track2-text-T1.3` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-A-p4` | `h7-track1-image-T1.3` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-A-p4` | `h9-track2-text-h9-B-v4` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-A-p4` | `h7-track1-image-T1.0` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-A-p4` | `h3-track2-text-T1.0` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-A-p4` | `h3-rep-minimal` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-A-p4` | `h1-brief-text-image` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-A-p4` | `h7-track2-text-T1.0` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-A-p4` | `h3-track1-image-T0.3` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-A-p4` | `h7-track2-text-T0.7` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-A-p4` | `h7-track1-image-T0.3` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-A-p4` | `h3-track2-text-T0.7` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-A-p4` | `h1-brief-text` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-A-p4` | `h1-image-only` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-A-p4` | `h7-track1-image-T0.7` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-A-p4` | `h7-track2-text-T0.3` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-A-p4` | `h1-verbose-text` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-A-p4` | `h3-track2-text-T0.3` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-A-p4` | `h7-track1-image-T0.0` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-A-p4` | `h11-bridge-brief-text-t0` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-A-p4` | `h7-track2-text-T0.0` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-C-img2` | `h9-track2-text-h9-A-p1` | 0.0003 | 3 |  |
| 1 | consensus | mcc | `h9-track1-image-h9-C-img2` | `h9-track2-text-h9-A-p4` | 0.0004 | 4 |  |
| 1 | consensus | mcc | `h9-track1-image-h9-C-img2` | `h9-track2-text-h9-A-p2` | 0.0002 | 2 |  |
| 1 | consensus | mcc | `h9-track1-image-h9-C-img2` | `h9-track2-text-h9-D-t1` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-C-img2` | `h3-track1-image-T1.0` | 0.0001 | 1 |  |
| 1 | consensus | mcc | `h9-track1-image-h9-C-img2` | `h9-track2-text-h9-E-p1` | 0.0001 | 1 |  |
| 1 | consensus | mcc | `h9-track1-image-h9-C-img2` | `h9-track2-text-h9-D-t2` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-C-img2` | `h9-track2-text-h9-E-p3` | 0.0002 | 2 |  |
| 1 | consensus | mcc | `h9-track1-image-h9-C-img2` | `h9-track2-text-h9-D-t3` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-C-img2` | `h3-track1-image-T0.7` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-C-img2` | `h9-track2-text-h9-A-p5` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-C-img2` | `h9-track2-text-h9-D-t5` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-C-img2` | `h9-track2-text-h9-B-v2` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-C-img2` | `h9-track2-text-h9-B-v5` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-C-img2` | `h9-track2-text-h9-D-t4` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-C-img2` | `h9-track2-text-h9-E-p2` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-C-img2` | `h9-track2-text-h9-E-p5` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-C-img2` | `h9-track2-text-h9-A-p3` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-C-img2` | `h9-track2-text-h9-E-p4` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-C-img2` | `h9-track2-text-h9-B-v1` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-C-img2` | `h1-verbose-text-image` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-C-img2` | `h7-track2-text-T1.3` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-C-img2` | `h7-track1-image-T1.3` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-C-img2` | `h9-track2-text-h9-B-v4` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-C-img2` | `h7-track1-image-T1.0` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-C-img2` | `h3-track2-text-T1.0` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-C-img2` | `h3-rep-minimal` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-C-img2` | `h1-brief-text-image` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-C-img2` | `h7-track2-text-T1.0` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-C-img2` | `h7-track2-text-T0.7` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-C-img2` | `h3-track1-image-T0.3` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-C-img2` | `h7-track1-image-T0.3` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-C-img2` | `h3-track2-text-T0.7` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-C-img2` | `h1-brief-text` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-C-img2` | `h1-image-only` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-C-img2` | `h7-track1-image-T0.7` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-C-img2` | `h7-track2-text-T0.3` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-C-img2` | `h1-verbose-text` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-C-img2` | `h3-track2-text-T0.3` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-C-img2` | `h7-track1-image-T0.0` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-C-img2` | `h11-bridge-brief-text-t0` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-C-img2` | `h7-track2-text-T0.0` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-C-img3` | `h9-track2-text-h9-A-p1` | 0.0004 | 4 |  |
| 1 | consensus | mcc | `h9-track1-image-h9-C-img3` | `h9-track2-text-h9-A-p2` | 0.0001 | 1 |  |
| 1 | consensus | mcc | `h9-track1-image-h9-C-img3` | `h9-track2-text-h9-D-t1` | 0.0001 | 1 |  |
| 1 | consensus | mcc | `h9-track1-image-h9-C-img3` | `h9-track2-text-h9-E-p1` | 0.0003 | 3 |  |
| 1 | consensus | mcc | `h9-track1-image-h9-C-img3` | `h3-track1-image-T1.0` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-C-img3` | `h9-track2-text-h9-D-t2` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-C-img3` | `h9-track2-text-h9-E-p3` | 0.0001 | 1 |  |
| 1 | consensus | mcc | `h9-track1-image-h9-C-img3` | `h9-track2-text-h9-D-t3` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-C-img3` | `h3-track1-image-T0.7` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-C-img3` | `h9-track2-text-h9-A-p5` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-C-img3` | `h9-track2-text-h9-D-t5` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-C-img3` | `h9-track2-text-h9-B-v2` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-C-img3` | `h9-track2-text-h9-B-v5` | 0.0001 | 1 |  |
| 1 | consensus | mcc | `h9-track1-image-h9-C-img3` | `h9-track2-text-h9-D-t4` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-C-img3` | `h9-track2-text-h9-E-p2` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-C-img3` | `h9-track2-text-h9-E-p5` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-C-img3` | `h9-track2-text-h9-A-p3` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-C-img3` | `h9-track2-text-h9-E-p4` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-C-img3` | `h9-track2-text-h9-B-v1` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-C-img3` | `h1-verbose-text-image` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-C-img3` | `h7-track2-text-T1.3` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-C-img3` | `h7-track1-image-T1.3` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-C-img3` | `h9-track2-text-h9-B-v4` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-C-img3` | `h7-track1-image-T1.0` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-C-img3` | `h3-track2-text-T1.0` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-C-img3` | `h3-rep-minimal` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-C-img3` | `h1-brief-text-image` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-C-img3` | `h7-track2-text-T1.0` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-C-img3` | `h7-track2-text-T0.7` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-C-img3` | `h3-track1-image-T0.3` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-C-img3` | `h7-track1-image-T0.3` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-C-img3` | `h3-track2-text-T0.7` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-C-img3` | `h1-brief-text` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-C-img3` | `h1-image-only` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-C-img3` | `h7-track1-image-T0.7` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-C-img3` | `h7-track2-text-T0.3` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-C-img3` | `h1-verbose-text` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-C-img3` | `h3-track2-text-T0.3` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-C-img3` | `h7-track1-image-T0.0` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-C-img3` | `h11-bridge-brief-text-t0` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-C-img3` | `h7-track2-text-T0.0` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-C-img1` | `h9-track2-text-h9-B-v3` | 0.0004 | 4 |  |
| 1 | consensus | mcc | `h9-track1-image-h9-C-img1` | `h9-track2-text-h9-A-p1` | 0.0003 | 3 |  |
| 1 | consensus | mcc | `h9-track1-image-h9-C-img1` | `h9-track2-text-h9-A-p4` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-C-img1` | `h9-track2-text-h9-A-p2` | 0.0005 | 5 |  |
| 1 | consensus | mcc | `h9-track1-image-h9-C-img1` | `h3-track1-image-T1.0` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-C-img1` | `h9-track2-text-h9-D-t1` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-C-img1` | `h9-track2-text-h9-E-p1` | 0.0002 | 2 |  |
| 1 | consensus | mcc | `h9-track1-image-h9-C-img1` | `h9-track2-text-h9-D-t2` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-C-img1` | `h9-track2-text-h9-E-p3` | 0.0001 | 1 |  |
| 1 | consensus | mcc | `h9-track1-image-h9-C-img1` | `h9-track2-text-h9-D-t3` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-C-img1` | `h3-track1-image-T0.7` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-C-img1` | `h9-track2-text-h9-A-p5` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-C-img1` | `h9-track2-text-h9-B-v2` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-C-img1` | `h9-track2-text-h9-D-t5` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-C-img1` | `h9-track2-text-h9-B-v5` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-C-img1` | `h9-track2-text-h9-D-t4` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-C-img1` | `h9-track2-text-h9-E-p2` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-C-img1` | `h9-track2-text-h9-E-p5` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-C-img1` | `h9-track2-text-h9-A-p3` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-C-img1` | `h9-track2-text-h9-E-p4` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-C-img1` | `h9-track2-text-h9-B-v1` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-C-img1` | `h1-verbose-text-image` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-C-img1` | `h7-track2-text-T1.3` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-C-img1` | `h7-track1-image-T1.3` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-C-img1` | `h9-track2-text-h9-B-v4` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-C-img1` | `h7-track1-image-T1.0` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-C-img1` | `h3-rep-minimal` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-C-img1` | `h3-track2-text-T1.0` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-C-img1` | `h1-brief-text-image` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-C-img1` | `h7-track2-text-T1.0` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-C-img1` | `h7-track2-text-T0.7` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-C-img1` | `h7-track1-image-T0.3` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-C-img1` | `h3-track1-image-T0.3` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-C-img1` | `h3-track2-text-T0.7` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-C-img1` | `h1-brief-text` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-C-img1` | `h1-image-only` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-C-img1` | `h7-track1-image-T0.7` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-C-img1` | `h7-track2-text-T0.3` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-C-img1` | `h1-verbose-text` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-C-img1` | `h3-track2-text-T0.3` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-C-img1` | `h7-track1-image-T0.0` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-C-img1` | `h11-bridge-brief-text-t0` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-C-img1` | `h7-track2-text-T0.0` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-D-t3` | `h9-track2-text-h9-A-p4` | 0.0004 | 4 |  |
| 1 | consensus | mcc | `h9-track1-image-h9-D-t3` | `h9-track2-text-h9-D-t1` | 0.0001 | 1 |  |
| 1 | consensus | mcc | `h9-track1-image-h9-D-t3` | `h9-track2-text-h9-E-p1` | 0.0001 | 1 |  |
| 1 | consensus | mcc | `h9-track1-image-h9-D-t3` | `h3-track1-image-T1.0` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-D-t3` | `h9-track2-text-h9-D-t2` | 0.0003 | 3 |  |
| 1 | consensus | mcc | `h9-track1-image-h9-D-t3` | `h9-track2-text-h9-D-t3` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-D-t3` | `h3-track1-image-T0.7` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-D-t3` | `h9-track2-text-h9-A-p5` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-D-t3` | `h9-track2-text-h9-D-t5` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-D-t3` | `h9-track2-text-h9-B-v2` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-D-t3` | `h9-track2-text-h9-B-v5` | 0.0001 | 1 |  |
| 1 | consensus | mcc | `h9-track1-image-h9-D-t3` | `h9-track2-text-h9-D-t4` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-D-t3` | `h9-track2-text-h9-E-p2` | 0.0001 | 1 |  |
| 1 | consensus | mcc | `h9-track1-image-h9-D-t3` | `h9-track2-text-h9-E-p5` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-D-t3` | `h9-track2-text-h9-A-p3` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-D-t3` | `h9-track2-text-h9-E-p4` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-D-t3` | `h9-track2-text-h9-B-v1` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-D-t3` | `h1-verbose-text-image` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-D-t3` | `h7-track2-text-T1.3` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-D-t3` | `h7-track1-image-T1.3` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-D-t3` | `h9-track2-text-h9-B-v4` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-D-t3` | `h7-track1-image-T1.0` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-D-t3` | `h3-track2-text-T1.0` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-D-t3` | `h3-rep-minimal` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-D-t3` | `h1-brief-text-image` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-D-t3` | `h7-track2-text-T1.0` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-D-t3` | `h7-track2-text-T0.7` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-D-t3` | `h3-track1-image-T0.3` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-D-t3` | `h7-track1-image-T0.3` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-D-t3` | `h3-track2-text-T0.7` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-D-t3` | `h1-brief-text` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-D-t3` | `h1-image-only` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-D-t3` | `h7-track1-image-T0.7` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-D-t3` | `h7-track2-text-T0.3` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-D-t3` | `h1-verbose-text` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-D-t3` | `h7-track1-image-T0.0` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-D-t3` | `h3-track2-text-T0.3` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-D-t3` | `h11-bridge-brief-text-t0` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-D-t3` | `h7-track2-text-T0.0` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-B-v1` | `h9-track2-text-h9-A-p2` | 0.0003 | 3 |  |
| 1 | consensus | mcc | `h9-track1-image-h9-B-v1` | `h9-track2-text-h9-D-t1` | 0.0002 | 2 |  |
| 1 | consensus | mcc | `h9-track1-image-h9-B-v1` | `h3-track1-image-T1.0` | 0.0002 | 2 |  |
| 1 | consensus | mcc | `h9-track1-image-h9-B-v1` | `h9-track2-text-h9-E-p1` | 0.0001 | 1 |  |
| 1 | consensus | mcc | `h9-track1-image-h9-B-v1` | `h9-track2-text-h9-D-t2` | 0.0001 | 1 |  |
| 1 | consensus | mcc | `h9-track1-image-h9-B-v1` | `h9-track2-text-h9-E-p3` | 0.0001 | 1 |  |
| 1 | consensus | mcc | `h9-track1-image-h9-B-v1` | `h3-track1-image-T0.7` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-B-v1` | `h9-track2-text-h9-D-t3` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-B-v1` | `h9-track2-text-h9-A-p5` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-B-v1` | `h9-track2-text-h9-D-t5` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-B-v1` | `h9-track2-text-h9-B-v2` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-B-v1` | `h9-track2-text-h9-B-v5` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-B-v1` | `h9-track2-text-h9-D-t4` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-B-v1` | `h9-track2-text-h9-E-p2` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-B-v1` | `h9-track2-text-h9-E-p5` | 0.0001 | 1 |  |
| 1 | consensus | mcc | `h9-track1-image-h9-B-v1` | `h9-track2-text-h9-A-p3` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-B-v1` | `h9-track2-text-h9-E-p4` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-B-v1` | `h9-track2-text-h9-B-v1` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-B-v1` | `h1-verbose-text-image` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-B-v1` | `h7-track2-text-T1.3` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-B-v1` | `h7-track1-image-T1.3` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-B-v1` | `h9-track2-text-h9-B-v4` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-B-v1` | `h7-track1-image-T1.0` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-B-v1` | `h3-track2-text-T1.0` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-B-v1` | `h3-rep-minimal` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-B-v1` | `h1-brief-text-image` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-B-v1` | `h7-track2-text-T1.0` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-B-v1` | `h7-track2-text-T0.7` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-B-v1` | `h3-track1-image-T0.3` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-B-v1` | `h7-track1-image-T0.3` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-B-v1` | `h3-track2-text-T0.7` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-B-v1` | `h1-brief-text` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-B-v1` | `h1-image-only` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-B-v1` | `h7-track1-image-T0.7` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-B-v1` | `h7-track2-text-T0.3` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-B-v1` | `h3-track2-text-T0.3` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-B-v1` | `h1-verbose-text` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-B-v1` | `h7-track1-image-T0.0` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-B-v1` | `h11-bridge-brief-text-t0` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-B-v1` | `h7-track2-text-T0.0` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-A-p1` | `h9-track2-text-h9-D-t1` | 0.0004 | 4 |  |
| 1 | consensus | mcc | `h9-track1-image-h9-A-p1` | `h3-track1-image-T1.0` | 0.0003 | 3 |  |
| 1 | consensus | mcc | `h9-track1-image-h9-A-p1` | `h9-track2-text-h9-E-p1` | 0.0004 | 4 |  |
| 1 | consensus | mcc | `h9-track1-image-h9-A-p1` | `h9-track2-text-h9-D-t2` | 0.0003 | 3 |  |
| 1 | consensus | mcc | `h9-track1-image-h9-A-p1` | `h9-track2-text-h9-E-p3` | 0.0005 | 5 |  |
| 1 | consensus | mcc | `h9-track1-image-h9-A-p1` | `h9-track2-text-h9-D-t3` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-A-p1` | `h3-track1-image-T0.7` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-A-p1` | `h9-track2-text-h9-A-p5` | 0.0001 | 1 |  |
| 1 | consensus | mcc | `h9-track1-image-h9-A-p1` | `h9-track2-text-h9-D-t5` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-A-p1` | `h9-track2-text-h9-B-v2` | 0.0002 | 2 |  |
| 1 | consensus | mcc | `h9-track1-image-h9-A-p1` | `h9-track2-text-h9-B-v5` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-A-p1` | `h9-track2-text-h9-D-t4` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-A-p1` | `h9-track2-text-h9-E-p2` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-A-p1` | `h9-track2-text-h9-E-p5` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-A-p1` | `h9-track2-text-h9-A-p3` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-A-p1` | `h9-track2-text-h9-E-p4` | 0.0001 | 1 |  |
| 1 | consensus | mcc | `h9-track1-image-h9-A-p1` | `h9-track2-text-h9-B-v1` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-A-p1` | `h1-verbose-text-image` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-A-p1` | `h7-track2-text-T1.3` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-A-p1` | `h7-track1-image-T1.3` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-A-p1` | `h7-track1-image-T1.0` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-A-p1` | `h9-track2-text-h9-B-v4` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-A-p1` | `h3-track2-text-T1.0` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-A-p1` | `h3-rep-minimal` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-A-p1` | `h1-brief-text-image` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-A-p1` | `h7-track2-text-T1.0` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-A-p1` | `h7-track2-text-T0.7` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-A-p1` | `h3-track1-image-T0.3` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-A-p1` | `h7-track1-image-T0.3` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-A-p1` | `h1-brief-text` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-A-p1` | `h3-track2-text-T0.7` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-A-p1` | `h1-image-only` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-A-p1` | `h7-track1-image-T0.7` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-A-p1` | `h7-track2-text-T0.3` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-A-p1` | `h1-verbose-text` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-A-p1` | `h3-track2-text-T0.3` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-A-p1` | `h7-track1-image-T0.0` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-A-p1` | `h11-bridge-brief-text-t0` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-A-p1` | `h7-track2-text-T0.0` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-C-img5` | `h9-track2-text-h9-A-p2` | 0.0005 | 5 |  |
| 1 | consensus | mcc | `h9-track1-image-h9-C-img5` | `h9-track2-text-h9-D-t1` | 0.0003 | 3 |  |
| 1 | consensus | mcc | `h9-track1-image-h9-C-img5` | `h3-track1-image-T1.0` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-C-img5` | `h9-track2-text-h9-D-t2` | 0.0004 | 4 |  |
| 1 | consensus | mcc | `h9-track1-image-h9-C-img5` | `h9-track2-text-h9-D-t3` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-C-img5` | `h3-track1-image-T0.7` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-C-img5` | `h9-track2-text-h9-A-p5` | 0.0002 | 2 |  |
| 1 | consensus | mcc | `h9-track1-image-h9-C-img5` | `h9-track2-text-h9-D-t5` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-C-img5` | `h9-track2-text-h9-B-v2` | 0.0001 | 1 |  |
| 1 | consensus | mcc | `h9-track1-image-h9-C-img5` | `h9-track2-text-h9-B-v5` | 0.0002 | 2 |  |
| 1 | consensus | mcc | `h9-track1-image-h9-C-img5` | `h9-track2-text-h9-D-t4` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-C-img5` | `h9-track2-text-h9-E-p2` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-C-img5` | `h9-track2-text-h9-E-p5` | 0.0001 | 1 |  |
| 1 | consensus | mcc | `h9-track1-image-h9-C-img5` | `h9-track2-text-h9-A-p3` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-C-img5` | `h9-track2-text-h9-E-p4` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-C-img5` | `h9-track2-text-h9-B-v1` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-C-img5` | `h1-verbose-text-image` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-C-img5` | `h7-track2-text-T1.3` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-C-img5` | `h7-track1-image-T1.3` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-C-img5` | `h9-track2-text-h9-B-v4` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-C-img5` | `h7-track1-image-T1.0` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-C-img5` | `h3-track2-text-T1.0` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-C-img5` | `h3-rep-minimal` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-C-img5` | `h1-brief-text-image` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-C-img5` | `h7-track2-text-T1.0` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-C-img5` | `h7-track2-text-T0.7` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-C-img5` | `h3-track1-image-T0.3` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-C-img5` | `h7-track1-image-T0.3` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-C-img5` | `h3-track2-text-T0.7` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-C-img5` | `h1-brief-text` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-C-img5` | `h1-image-only` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-C-img5` | `h7-track1-image-T0.7` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-C-img5` | `h7-track2-text-T0.3` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-C-img5` | `h1-verbose-text` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-C-img5` | `h3-track2-text-T0.3` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-C-img5` | `h7-track1-image-T0.0` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-C-img5` | `h7-track2-text-T0.0` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-C-img5` | `h11-bridge-brief-text-t0` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-B-v5` | `h9-track2-text-h9-D-t1` | 0.0002 | 2 |  |
| 1 | consensus | mcc | `h9-track1-image-h9-B-v5` | `h3-track1-image-T1.0` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-B-v5` | `h9-track2-text-h9-D-t2` | 0.0004 | 4 |  |
| 1 | consensus | mcc | `h9-track1-image-h9-B-v5` | `h9-track2-text-h9-E-p3` | 0.0004 | 4 |  |
| 1 | consensus | mcc | `h9-track1-image-h9-B-v5` | `h9-track2-text-h9-D-t3` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-B-v5` | `h9-track2-text-h9-A-p5` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-B-v5` | `h3-track1-image-T0.7` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-B-v5` | `h9-track2-text-h9-D-t5` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-B-v5` | `h9-track2-text-h9-B-v2` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-B-v5` | `h9-track2-text-h9-B-v5` | 0.0002 | 2 |  |
| 1 | consensus | mcc | `h9-track1-image-h9-B-v5` | `h9-track2-text-h9-D-t4` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-B-v5` | `h9-track2-text-h9-E-p2` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-B-v5` | `h9-track2-text-h9-E-p5` | 0.0001 | 1 |  |
| 1 | consensus | mcc | `h9-track1-image-h9-B-v5` | `h9-track2-text-h9-A-p3` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-B-v5` | `h9-track2-text-h9-B-v1` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-B-v5` | `h9-track2-text-h9-E-p4` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-B-v5` | `h1-verbose-text-image` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-B-v5` | `h7-track2-text-T1.3` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-B-v5` | `h7-track1-image-T1.3` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-B-v5` | `h9-track2-text-h9-B-v4` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-B-v5` | `h7-track1-image-T1.0` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-B-v5` | `h3-track2-text-T1.0` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-B-v5` | `h3-rep-minimal` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-B-v5` | `h1-brief-text-image` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-B-v5` | `h7-track2-text-T1.0` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-B-v5` | `h7-track2-text-T0.7` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-B-v5` | `h3-track1-image-T0.3` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-B-v5` | `h7-track1-image-T0.3` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-B-v5` | `h3-track2-text-T0.7` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-B-v5` | `h1-brief-text` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-B-v5` | `h1-image-only` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-B-v5` | `h7-track1-image-T0.7` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-B-v5` | `h7-track2-text-T0.3` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-B-v5` | `h1-verbose-text` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-B-v5` | `h3-track2-text-T0.3` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-B-v5` | `h7-track1-image-T0.0` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-B-v5` | `h11-bridge-brief-text-t0` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-B-v5` | `h7-track2-text-T0.0` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-E-p2` | `h3-track1-image-T1.0` | 0.0001 | 1 |  |
| 1 | consensus | mcc | `h9-track1-image-h9-E-p2` | `h9-track2-text-h9-D-t3` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-E-p2` | `h3-track1-image-T0.7` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-E-p2` | `h9-track2-text-h9-A-p5` | 0.0001 | 1 |  |
| 1 | consensus | mcc | `h9-track1-image-h9-E-p2` | `h9-track2-text-h9-D-t5` | 0.0002 | 2 |  |
| 1 | consensus | mcc | `h9-track1-image-h9-E-p2` | `h9-track2-text-h9-B-v2` | 0.0002 | 2 |  |
| 1 | consensus | mcc | `h9-track1-image-h9-E-p2` | `h9-track2-text-h9-B-v5` | 0.0001 | 1 |  |
| 1 | consensus | mcc | `h9-track1-image-h9-E-p2` | `h9-track2-text-h9-D-t4` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-E-p2` | `h9-track2-text-h9-E-p2` | 0.0001 | 1 |  |
| 1 | consensus | mcc | `h9-track1-image-h9-E-p2` | `h9-track2-text-h9-E-p5` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-E-p2` | `h9-track2-text-h9-A-p3` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-E-p2` | `h9-track2-text-h9-E-p4` | 0.0001 | 1 |  |
| 1 | consensus | mcc | `h9-track1-image-h9-E-p2` | `h9-track2-text-h9-B-v1` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-E-p2` | `h1-verbose-text-image` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-E-p2` | `h7-track2-text-T1.3` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-E-p2` | `h7-track1-image-T1.3` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-E-p2` | `h9-track2-text-h9-B-v4` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-E-p2` | `h7-track1-image-T1.0` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-E-p2` | `h3-track2-text-T1.0` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-E-p2` | `h3-rep-minimal` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-E-p2` | `h1-brief-text-image` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-E-p2` | `h7-track2-text-T1.0` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-E-p2` | `h7-track2-text-T0.7` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-E-p2` | `h3-track1-image-T0.3` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-E-p2` | `h7-track1-image-T0.3` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-E-p2` | `h3-track2-text-T0.7` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-E-p2` | `h1-brief-text` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-E-p2` | `h1-image-only` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-E-p2` | `h7-track1-image-T0.7` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-E-p2` | `h7-track2-text-T0.3` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-E-p2` | `h1-verbose-text` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-E-p2` | `h3-track2-text-T0.3` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-E-p2` | `h7-track1-image-T0.0` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-E-p2` | `h11-bridge-brief-text-t0` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-E-p2` | `h7-track2-text-T0.0` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-E-p3` | `h9-track2-text-h9-D-t1` | 0.0003 | 3 |  |
| 1 | consensus | mcc | `h9-track1-image-h9-E-p3` | `h3-track1-image-T1.0` | 0.0001 | 1 |  |
| 1 | consensus | mcc | `h9-track1-image-h9-E-p3` | `h9-track2-text-h9-D-t2` | 0.0005 | 5 |  |
| 1 | consensus | mcc | `h9-track1-image-h9-E-p3` | `h9-track2-text-h9-D-t3` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-E-p3` | `h3-track1-image-T0.7` | 0.0001 | 1 |  |
| 1 | consensus | mcc | `h9-track1-image-h9-E-p3` | `h9-track2-text-h9-A-p5` | 0.0002 | 2 |  |
| 1 | consensus | mcc | `h9-track1-image-h9-E-p3` | `h9-track2-text-h9-D-t5` | 0.0001 | 1 |  |
| 1 | consensus | mcc | `h9-track1-image-h9-E-p3` | `h9-track2-text-h9-B-v2` | 0.0002 | 2 |  |
| 1 | consensus | mcc | `h9-track1-image-h9-E-p3` | `h9-track2-text-h9-B-v5` | 0.0002 | 2 |  |
| 1 | consensus | mcc | `h9-track1-image-h9-E-p3` | `h9-track2-text-h9-D-t4` | 0.0001 | 1 |  |
| 1 | consensus | mcc | `h9-track1-image-h9-E-p3` | `h9-track2-text-h9-E-p2` | 0.0002 | 2 |  |
| 1 | consensus | mcc | `h9-track1-image-h9-E-p3` | `h9-track2-text-h9-E-p5` | 0.0001 | 1 |  |
| 1 | consensus | mcc | `h9-track1-image-h9-E-p3` | `h9-track2-text-h9-A-p3` | 0.0001 | 1 |  |
| 1 | consensus | mcc | `h9-track1-image-h9-E-p3` | `h9-track2-text-h9-E-p4` | 0.0001 | 1 |  |
| 1 | consensus | mcc | `h9-track1-image-h9-E-p3` | `h9-track2-text-h9-B-v1` | 0.0001 | 1 |  |
| 1 | consensus | mcc | `h9-track1-image-h9-E-p3` | `h1-verbose-text-image` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-E-p3` | `h7-track2-text-T1.3` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-E-p3` | `h7-track1-image-T1.3` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-E-p3` | `h9-track2-text-h9-B-v4` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-E-p3` | `h7-track1-image-T1.0` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-E-p3` | `h3-track2-text-T1.0` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-E-p3` | `h3-rep-minimal` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-E-p3` | `h1-brief-text-image` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-E-p3` | `h7-track2-text-T1.0` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-E-p3` | `h7-track2-text-T0.7` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-E-p3` | `h3-track1-image-T0.3` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-E-p3` | `h7-track1-image-T0.3` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-E-p3` | `h3-track2-text-T0.7` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-E-p3` | `h1-image-only` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-E-p3` | `h1-brief-text` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-E-p3` | `h7-track1-image-T0.7` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-E-p3` | `h7-track2-text-T0.3` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-E-p3` | `h1-verbose-text` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-E-p3` | `h3-track2-text-T0.3` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-E-p3` | `h7-track1-image-T0.0` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-E-p3` | `h11-bridge-brief-text-t0` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-E-p3` | `h7-track2-text-T0.0` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-A-p2` | `h9-track2-text-h9-D-t3` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-A-p2` | `h3-track1-image-T0.7` | 0.0003 | 3 |  |
| 1 | consensus | mcc | `h9-track1-image-h9-A-p2` | `h9-track2-text-h9-A-p5` | 0.0003 | 3 |  |
| 1 | consensus | mcc | `h9-track1-image-h9-A-p2` | `h9-track2-text-h9-D-t5` | 0.0003 | 3 |  |
| 1 | consensus | mcc | `h9-track1-image-h9-A-p2` | `h9-track2-text-h9-B-v2` | 0.0001 | 1 |  |
| 1 | consensus | mcc | `h9-track1-image-h9-A-p2` | `h9-track2-text-h9-B-v5` | 0.0002 | 2 |  |
| 1 | consensus | mcc | `h9-track1-image-h9-A-p2` | `h9-track2-text-h9-D-t4` | 0.0001 | 1 |  |
| 1 | consensus | mcc | `h9-track1-image-h9-A-p2` | `h9-track2-text-h9-E-p2` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-A-p2` | `h9-track2-text-h9-E-p5` | 0.0001 | 1 |  |
| 1 | consensus | mcc | `h9-track1-image-h9-A-p2` | `h9-track2-text-h9-A-p3` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-A-p2` | `h9-track2-text-h9-E-p4` | 0.0002 | 2 |  |
| 1 | consensus | mcc | `h9-track1-image-h9-A-p2` | `h1-verbose-text-image` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-A-p2` | `h9-track2-text-h9-B-v1` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-A-p2` | `h7-track2-text-T1.3` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-A-p2` | `h7-track1-image-T1.3` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-A-p2` | `h9-track2-text-h9-B-v4` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-A-p2` | `h7-track1-image-T1.0` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-A-p2` | `h3-rep-minimal` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-A-p2` | `h3-track2-text-T1.0` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-A-p2` | `h1-brief-text-image` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-A-p2` | `h7-track2-text-T1.0` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-A-p2` | `h7-track2-text-T0.7` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-A-p2` | `h3-track1-image-T0.3` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-A-p2` | `h7-track1-image-T0.3` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-A-p2` | `h3-track2-text-T0.7` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-A-p2` | `h1-brief-text` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-A-p2` | `h1-image-only` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-A-p2` | `h7-track1-image-T0.7` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-A-p2` | `h1-verbose-text` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-A-p2` | `h7-track2-text-T0.3` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-A-p2` | `h3-track2-text-T0.3` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-A-p2` | `h7-track1-image-T0.0` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-A-p2` | `h11-bridge-brief-text-t0` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-A-p2` | `h7-track2-text-T0.0` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-E-p1` | `h3-track1-image-T1.0` | 0.0004 | 4 |  |
| 1 | consensus | mcc | `h9-track1-image-h9-E-p1` | `h9-track2-text-h9-D-t3` | 0.0001 | 1 |  |
| 1 | consensus | mcc | `h9-track1-image-h9-E-p1` | `h3-track1-image-T0.7` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-E-p1` | `h9-track2-text-h9-A-p5` | 0.0001 | 1 |  |
| 1 | consensus | mcc | `h9-track1-image-h9-E-p1` | `h9-track2-text-h9-D-t5` | 0.0005 | 5 |  |
| 1 | consensus | mcc | `h9-track1-image-h9-E-p1` | `h9-track2-text-h9-B-v2` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-E-p1` | `h9-track2-text-h9-B-v5` | 0.0005 | 5 |  |
| 1 | consensus | mcc | `h9-track1-image-h9-E-p1` | `h9-track2-text-h9-D-t4` | 0.0002 | 2 |  |
| 1 | consensus | mcc | `h9-track1-image-h9-E-p1` | `h9-track2-text-h9-E-p2` | 0.0001 | 1 |  |
| 1 | consensus | mcc | `h9-track1-image-h9-E-p1` | `h9-track2-text-h9-E-p5` | 0.0001 | 1 |  |
| 1 | consensus | mcc | `h9-track1-image-h9-E-p1` | `h9-track2-text-h9-A-p3` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-E-p1` | `h9-track2-text-h9-E-p4` | 0.0001 | 1 |  |
| 1 | consensus | mcc | `h9-track1-image-h9-E-p1` | `h9-track2-text-h9-B-v1` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-E-p1` | `h1-verbose-text-image` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-E-p1` | `h7-track2-text-T1.3` | 0.0001 | 1 |  |
| 1 | consensus | mcc | `h9-track1-image-h9-E-p1` | `h7-track1-image-T1.3` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-E-p1` | `h9-track2-text-h9-B-v4` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-E-p1` | `h7-track1-image-T1.0` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-E-p1` | `h3-track2-text-T1.0` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-E-p1` | `h3-rep-minimal` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-E-p1` | `h1-brief-text-image` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-E-p1` | `h7-track2-text-T1.0` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-E-p1` | `h7-track2-text-T0.7` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-E-p1` | `h3-track1-image-T0.3` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-E-p1` | `h7-track1-image-T0.3` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-E-p1` | `h3-track2-text-T0.7` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-E-p1` | `h1-brief-text` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-E-p1` | `h1-image-only` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-E-p1` | `h7-track1-image-T0.7` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-E-p1` | `h7-track2-text-T0.3` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-E-p1` | `h1-verbose-text` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-E-p1` | `h3-track2-text-T0.3` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-E-p1` | `h7-track1-image-T0.0` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-E-p1` | `h11-bridge-brief-text-t0` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-E-p1` | `h7-track2-text-T0.0` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-E-p4` | `h3-track1-image-T1.0` | 0.0001 | 1 |  |
| 1 | consensus | mcc | `h9-track1-image-h9-E-p4` | `h9-track2-text-h9-D-t3` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-E-p4` | `h9-track2-text-h9-A-p5` | 0.0003 | 3 |  |
| 1 | consensus | mcc | `h9-track1-image-h9-E-p4` | `h3-track1-image-T0.7` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-E-p4` | `h9-track2-text-h9-D-t5` | 0.0002 | 2 |  |
| 1 | consensus | mcc | `h9-track1-image-h9-E-p4` | `h9-track2-text-h9-B-v2` | 0.0002 | 2 |  |
| 1 | consensus | mcc | `h9-track1-image-h9-E-p4` | `h9-track2-text-h9-B-v5` | 0.0002 | 2 |  |
| 1 | consensus | mcc | `h9-track1-image-h9-E-p4` | `h9-track2-text-h9-D-t4` | 0.0002 | 2 |  |
| 1 | consensus | mcc | `h9-track1-image-h9-E-p4` | `h9-track2-text-h9-E-p2` | 0.0002 | 2 |  |
| 1 | consensus | mcc | `h9-track1-image-h9-E-p4` | `h9-track2-text-h9-E-p5` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-E-p4` | `h9-track2-text-h9-A-p3` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-E-p4` | `h9-track2-text-h9-E-p4` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-E-p4` | `h9-track2-text-h9-B-v1` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-E-p4` | `h1-verbose-text-image` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-E-p4` | `h7-track2-text-T1.3` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-E-p4` | `h7-track1-image-T1.3` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-E-p4` | `h9-track2-text-h9-B-v4` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-E-p4` | `h7-track1-image-T1.0` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-E-p4` | `h1-brief-text-image` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-E-p4` | `h3-track2-text-T1.0` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-E-p4` | `h3-rep-minimal` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-E-p4` | `h7-track2-text-T1.0` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-E-p4` | `h7-track2-text-T0.7` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-E-p4` | `h3-track1-image-T0.3` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-E-p4` | `h7-track1-image-T0.3` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-E-p4` | `h3-track2-text-T0.7` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-E-p4` | `h1-brief-text` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-E-p4` | `h7-track1-image-T0.7` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-E-p4` | `h1-image-only` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-E-p4` | `h7-track2-text-T0.3` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-E-p4` | `h1-verbose-text` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-E-p4` | `h3-track2-text-T0.3` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-E-p4` | `h7-track1-image-T0.0` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-E-p4` | `h11-bridge-brief-text-t0` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-E-p4` | `h7-track2-text-T0.0` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h3-high-track2-text-T1.0` | `h9-track2-text-h9-D-t1` | 0.0003 | 3 |  |
| 1 | consensus | mcc | `h3-high-track2-text-T1.0` | `h9-track2-text-h9-D-t2` | 0.0004 | 4 |  |
| 1 | consensus | mcc | `h3-high-track2-text-T1.0` | `h9-track2-text-h9-D-t3` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h3-high-track2-text-T1.0` | `h3-track1-image-T0.7` | 0.0004 | 4 |  |
| 1 | consensus | mcc | `h3-high-track2-text-T1.0` | `h9-track2-text-h9-A-p5` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h3-high-track2-text-T1.0` | `h9-track2-text-h9-D-t5` | 0.0001 | 1 |  |
| 1 | consensus | mcc | `h3-high-track2-text-T1.0` | `h9-track2-text-h9-B-v5` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h3-high-track2-text-T1.0` | `h9-track2-text-h9-B-v2` | 0.0001 | 1 |  |
| 1 | consensus | mcc | `h3-high-track2-text-T1.0` | `h9-track2-text-h9-D-t4` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h3-high-track2-text-T1.0` | `h9-track2-text-h9-E-p2` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h3-high-track2-text-T1.0` | `h9-track2-text-h9-E-p5` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h3-high-track2-text-T1.0` | `h9-track2-text-h9-A-p3` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h3-high-track2-text-T1.0` | `h9-track2-text-h9-E-p4` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h3-high-track2-text-T1.0` | `h9-track2-text-h9-B-v1` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h3-high-track2-text-T1.0` | `h7-track2-text-T1.3` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h3-high-track2-text-T1.0` | `h1-verbose-text-image` | 0.0001 | 1 |  |
| 1 | consensus | mcc | `h3-high-track2-text-T1.0` | `h7-track1-image-T1.3` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h3-high-track2-text-T1.0` | `h9-track2-text-h9-B-v4` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h3-high-track2-text-T1.0` | `h7-track1-image-T1.0` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h3-high-track2-text-T1.0` | `h3-track2-text-T1.0` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h3-high-track2-text-T1.0` | `h3-rep-minimal` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h3-high-track2-text-T1.0` | `h1-brief-text-image` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h3-high-track2-text-T1.0` | `h7-track2-text-T1.0` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h3-high-track2-text-T1.0` | `h7-track2-text-T0.7` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h3-high-track2-text-T1.0` | `h3-track1-image-T0.3` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h3-high-track2-text-T1.0` | `h7-track1-image-T0.3` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h3-high-track2-text-T1.0` | `h3-track2-text-T0.7` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h3-high-track2-text-T1.0` | `h1-brief-text` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h3-high-track2-text-T1.0` | `h1-image-only` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h3-high-track2-text-T1.0` | `h7-track1-image-T0.7` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h3-high-track2-text-T1.0` | `h7-track2-text-T0.3` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h3-high-track2-text-T1.0` | `h1-verbose-text` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h3-high-track2-text-T1.0` | `h3-track2-text-T0.3` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h3-high-track2-text-T1.0` | `h7-track1-image-T0.0` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h3-high-track2-text-T1.0` | `h11-bridge-brief-text-t0` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h3-high-track2-text-T1.0` | `h7-track2-text-T0.0` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-B-v3` | `h3-track1-image-T1.0` | 0.0004 | 4 |  |
| 1 | consensus | mcc | `h9-track1-image-h9-B-v3` | `h9-track2-text-h9-D-t3` | 0.0001 | 1 |  |
| 1 | consensus | mcc | `h9-track1-image-h9-B-v3` | `h9-track2-text-h9-A-p5` | 0.0002 | 2 |  |
| 1 | consensus | mcc | `h9-track1-image-h9-B-v3` | `h3-track1-image-T0.7` | 0.0002 | 2 |  |
| 1 | consensus | mcc | `h9-track1-image-h9-B-v3` | `h9-track2-text-h9-D-t5` | 0.0003 | 3 |  |
| 1 | consensus | mcc | `h9-track1-image-h9-B-v3` | `h9-track2-text-h9-B-v2` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-B-v3` | `h9-track2-text-h9-B-v5` | 0.0001 | 1 |  |
| 1 | consensus | mcc | `h9-track1-image-h9-B-v3` | `h9-track2-text-h9-D-t4` | 0.0001 | 1 |  |
| 1 | consensus | mcc | `h9-track1-image-h9-B-v3` | `h9-track2-text-h9-E-p2` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-B-v3` | `h9-track2-text-h9-E-p5` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-B-v3` | `h9-track2-text-h9-A-p3` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-B-v3` | `h9-track2-text-h9-E-p4` | 0.0001 | 1 |  |
| 1 | consensus | mcc | `h9-track1-image-h9-B-v3` | `h9-track2-text-h9-B-v1` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-B-v3` | `h1-verbose-text-image` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-B-v3` | `h7-track1-image-T1.3` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-B-v3` | `h7-track2-text-T1.3` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-B-v3` | `h9-track2-text-h9-B-v4` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-B-v3` | `h7-track1-image-T1.0` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-B-v3` | `h3-rep-minimal` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-B-v3` | `h3-track2-text-T1.0` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-B-v3` | `h1-brief-text-image` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-B-v3` | `h7-track2-text-T1.0` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-B-v3` | `h7-track2-text-T0.7` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-B-v3` | `h3-track1-image-T0.3` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-B-v3` | `h7-track1-image-T0.3` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-B-v3` | `h3-track2-text-T0.7` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-B-v3` | `h1-brief-text` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-B-v3` | `h1-image-only` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-B-v3` | `h7-track1-image-T0.7` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-B-v3` | `h7-track2-text-T0.3` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-B-v3` | `h1-verbose-text` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-B-v3` | `h3-track2-text-T0.3` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-B-v3` | `h11-bridge-brief-text-t0` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-B-v3` | `h7-track1-image-T0.0` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-B-v3` | `h7-track2-text-T0.0` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-D-t2` | `h3-track1-image-T1.0` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-D-t2` | `h9-track2-text-h9-D-t3` | 0.0004 | 4 |  |
| 1 | consensus | mcc | `h9-track1-image-h9-D-t2` | `h3-track1-image-T0.7` | 0.0002 | 2 |  |
| 1 | consensus | mcc | `h9-track1-image-h9-D-t2` | `h9-track2-text-h9-A-p5` | 0.0003 | 3 |  |
| 1 | consensus | mcc | `h9-track1-image-h9-D-t2` | `h9-track2-text-h9-D-t5` | 0.0002 | 2 |  |
| 1 | consensus | mcc | `h9-track1-image-h9-D-t2` | `h9-track2-text-h9-B-v2` | 0.0003 | 3 |  |
| 1 | consensus | mcc | `h9-track1-image-h9-D-t2` | `h9-track2-text-h9-B-v5` | 0.0003 | 3 |  |
| 1 | consensus | mcc | `h9-track1-image-h9-D-t2` | `h9-track2-text-h9-D-t4` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-D-t2` | `h9-track2-text-h9-E-p2` | 0.0001 | 1 |  |
| 1 | consensus | mcc | `h9-track1-image-h9-D-t2` | `h9-track2-text-h9-E-p5` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-D-t2` | `h9-track2-text-h9-A-p3` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-D-t2` | `h9-track2-text-h9-E-p4` | 0.0001 | 1 |  |
| 1 | consensus | mcc | `h9-track1-image-h9-D-t2` | `h9-track2-text-h9-B-v1` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-D-t2` | `h1-verbose-text-image` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-D-t2` | `h7-track2-text-T1.3` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-D-t2` | `h7-track1-image-T1.3` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-D-t2` | `h9-track2-text-h9-B-v4` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-D-t2` | `h7-track1-image-T1.0` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-D-t2` | `h3-track2-text-T1.0` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-D-t2` | `h3-rep-minimal` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-D-t2` | `h1-brief-text-image` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-D-t2` | `h7-track2-text-T1.0` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-D-t2` | `h7-track2-text-T0.7` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-D-t2` | `h7-track1-image-T0.3` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-D-t2` | `h3-track1-image-T0.3` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-D-t2` | `h3-track2-text-T0.7` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-D-t2` | `h1-brief-text` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-D-t2` | `h1-image-only` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-D-t2` | `h7-track1-image-T0.7` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-D-t2` | `h7-track2-text-T0.3` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-D-t2` | `h1-verbose-text` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-D-t2` | `h3-track2-text-T0.3` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-D-t2` | `h7-track1-image-T0.0` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-D-t2` | `h7-track2-text-T0.0` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-D-t2` | `h11-bridge-brief-text-t0` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-D-t5` | `h9-track2-text-h9-D-t3` | 0.0003 | 3 |  |
| 1 | consensus | mcc | `h9-track1-image-h9-D-t5` | `h9-track2-text-h9-A-p5` | 0.0002 | 2 |  |
| 1 | consensus | mcc | `h9-track1-image-h9-D-t5` | `h9-track2-text-h9-B-v5` | 0.0004 | 4 |  |
| 1 | consensus | mcc | `h9-track1-image-h9-D-t5` | `h9-track2-text-h9-B-v2` | 0.0002 | 2 |  |
| 1 | consensus | mcc | `h9-track1-image-h9-D-t5` | `h9-track2-text-h9-D-t4` | 0.0004 | 4 |  |
| 1 | consensus | mcc | `h9-track1-image-h9-D-t5` | `h9-track2-text-h9-E-p2` | 0.0002 | 2 |  |
| 1 | consensus | mcc | `h9-track1-image-h9-D-t5` | `h9-track2-text-h9-E-p5` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-D-t5` | `h9-track2-text-h9-A-p3` | 0.0001 | 1 |  |
| 1 | consensus | mcc | `h9-track1-image-h9-D-t5` | `h9-track2-text-h9-B-v1` | 0.0001 | 1 |  |
| 1 | consensus | mcc | `h9-track1-image-h9-D-t5` | `h1-verbose-text-image` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-D-t5` | `h9-track2-text-h9-E-p4` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-D-t5` | `h7-track2-text-T1.3` | 0.0001 | 1 |  |
| 1 | consensus | mcc | `h9-track1-image-h9-D-t5` | `h7-track1-image-T1.3` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-D-t5` | `h9-track2-text-h9-B-v4` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-D-t5` | `h7-track1-image-T1.0` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-D-t5` | `h3-track2-text-T1.0` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-D-t5` | `h1-brief-text-image` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-D-t5` | `h3-rep-minimal` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-D-t5` | `h7-track2-text-T0.7` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-D-t5` | `h7-track2-text-T1.0` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-D-t5` | `h3-track1-image-T0.3` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-D-t5` | `h7-track1-image-T0.3` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-D-t5` | `h3-track2-text-T0.7` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-D-t5` | `h1-brief-text` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-D-t5` | `h1-image-only` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-D-t5` | `h7-track1-image-T0.7` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-D-t5` | `h7-track2-text-T0.3` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-D-t5` | `h1-verbose-text` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-D-t5` | `h3-track2-text-T0.3` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-D-t5` | `h7-track1-image-T0.0` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-D-t5` | `h11-bridge-brief-text-t0` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-D-t5` | `h7-track2-text-T0.0` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-D-t4` | `h3-track1-image-T0.7` | 0.0001 | 1 |  |
| 1 | consensus | mcc | `h9-track1-image-h9-D-t4` | `h9-track2-text-h9-B-v2` | 0.0005 | 5 |  |
| 1 | consensus | mcc | `h9-track1-image-h9-D-t4` | `h9-track2-text-h9-B-v5` | 0.0004 | 4 |  |
| 1 | consensus | mcc | `h9-track1-image-h9-D-t4` | `h9-track2-text-h9-D-t4` | 0.0005 | 5 |  |
| 1 | consensus | mcc | `h9-track1-image-h9-D-t4` | `h9-track2-text-h9-E-p2` | 0.0001 | 1 |  |
| 1 | consensus | mcc | `h9-track1-image-h9-D-t4` | `h9-track2-text-h9-E-p5` | 0.0003 | 3 |  |
| 1 | consensus | mcc | `h9-track1-image-h9-D-t4` | `h9-track2-text-h9-A-p3` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-D-t4` | `h1-verbose-text-image` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-D-t4` | `h9-track2-text-h9-E-p4` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-D-t4` | `h9-track2-text-h9-B-v1` | 0.0001 | 1 |  |
| 1 | consensus | mcc | `h9-track1-image-h9-D-t4` | `h7-track2-text-T1.3` | 0.0002 | 2 |  |
| 1 | consensus | mcc | `h9-track1-image-h9-D-t4` | `h7-track1-image-T1.3` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-D-t4` | `h9-track2-text-h9-B-v4` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-D-t4` | `h7-track1-image-T1.0` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-D-t4` | `h3-track2-text-T1.0` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-D-t4` | `h3-rep-minimal` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-D-t4` | `h1-brief-text-image` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-D-t4` | `h7-track2-text-T1.0` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-D-t4` | `h7-track2-text-T0.7` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-D-t4` | `h3-track1-image-T0.3` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-D-t4` | `h7-track1-image-T0.3` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-D-t4` | `h3-track2-text-T0.7` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-D-t4` | `h1-brief-text` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-D-t4` | `h1-image-only` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-D-t4` | `h7-track1-image-T0.7` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-D-t4` | `h7-track2-text-T0.3` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-D-t4` | `h1-verbose-text` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-D-t4` | `h3-track2-text-T0.3` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-D-t4` | `h7-track1-image-T0.0` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-D-t4` | `h11-bridge-brief-text-t0` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-D-t4` | `h7-track2-text-T0.0` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-B-v2` | `h9-track2-text-h9-D-t3` | 0.0003 | 3 |  |
| 1 | consensus | mcc | `h9-track1-image-h9-B-v2` | `h3-track1-image-T0.7` | 0.0002 | 2 |  |
| 1 | consensus | mcc | `h9-track1-image-h9-B-v2` | `h9-track2-text-h9-A-p5` | 0.0003 | 3 |  |
| 1 | consensus | mcc | `h9-track1-image-h9-B-v2` | `h9-track2-text-h9-D-t5` | 0.0004 | 4 |  |
| 1 | consensus | mcc | `h9-track1-image-h9-B-v2` | `h9-track2-text-h9-B-v5` | 0.0002 | 2 |  |
| 1 | consensus | mcc | `h9-track1-image-h9-B-v2` | `h9-track2-text-h9-D-t4` | 0.0004 | 4 |  |
| 1 | consensus | mcc | `h9-track1-image-h9-B-v2` | `h9-track2-text-h9-E-p2` | 0.0001 | 1 |  |
| 1 | consensus | mcc | `h9-track1-image-h9-B-v2` | `h9-track2-text-h9-E-p5` | 0.0002 | 2 |  |
| 1 | consensus | mcc | `h9-track1-image-h9-B-v2` | `h9-track2-text-h9-A-p3` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-B-v2` | `h9-track2-text-h9-E-p4` | 0.0001 | 1 |  |
| 1 | consensus | mcc | `h9-track1-image-h9-B-v2` | `h9-track2-text-h9-B-v1` | 0.0001 | 1 |  |
| 1 | consensus | mcc | `h9-track1-image-h9-B-v2` | `h7-track2-text-T1.3` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-B-v2` | `h1-verbose-text-image` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-B-v2` | `h7-track1-image-T1.3` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-B-v2` | `h9-track2-text-h9-B-v4` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-B-v2` | `h7-track1-image-T1.0` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-B-v2` | `h3-track2-text-T1.0` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-B-v2` | `h3-rep-minimal` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-B-v2` | `h1-brief-text-image` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-B-v2` | `h7-track2-text-T1.0` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-B-v2` | `h7-track2-text-T0.7` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-B-v2` | `h3-track1-image-T0.3` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-B-v2` | `h7-track1-image-T0.3` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-B-v2` | `h3-track2-text-T0.7` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-B-v2` | `h1-brief-text` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-B-v2` | `h1-image-only` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-B-v2` | `h7-track1-image-T0.7` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-B-v2` | `h7-track2-text-T0.3` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-B-v2` | `h1-verbose-text` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-B-v2` | `h3-track2-text-T0.3` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-B-v2` | `h7-track1-image-T0.0` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-B-v2` | `h11-bridge-brief-text-t0` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-B-v2` | `h7-track2-text-T0.0` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-E-p5` | `h9-track2-text-h9-A-p3` | 0.0004 | 4 |  |
| 1 | consensus | mcc | `h9-track1-image-h9-E-p5` | `h9-track2-text-h9-B-v1` | 0.0001 | 1 |  |
| 1 | consensus | mcc | `h9-track1-image-h9-E-p5` | `h1-verbose-text-image` | 0.0002 | 2 |  |
| 1 | consensus | mcc | `h9-track1-image-h9-E-p5` | `h7-track2-text-T1.3` | 0.0003 | 3 |  |
| 1 | consensus | mcc | `h9-track1-image-h9-E-p5` | `h7-track1-image-T1.3` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-E-p5` | `h9-track2-text-h9-B-v4` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-E-p5` | `h7-track1-image-T1.0` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-E-p5` | `h3-track2-text-T1.0` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-E-p5` | `h3-rep-minimal` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-E-p5` | `h1-brief-text-image` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-E-p5` | `h7-track2-text-T1.0` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-E-p5` | `h7-track2-text-T0.7` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-E-p5` | `h3-track1-image-T0.3` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-E-p5` | `h7-track1-image-T0.3` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-E-p5` | `h3-track2-text-T0.7` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-E-p5` | `h1-brief-text` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-E-p5` | `h1-image-only` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-E-p5` | `h7-track1-image-T0.7` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-E-p5` | `h7-track2-text-T0.3` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-E-p5` | `h1-verbose-text` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-E-p5` | `h7-track1-image-T0.0` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-E-p5` | `h3-track2-text-T0.3` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-E-p5` | `h11-bridge-brief-text-t0` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-E-p5` | `h7-track2-text-T0.0` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-C-img4` | `h1-verbose-text-image` | 0.0004 | 4 |  |
| 1 | consensus | mcc | `h9-track1-image-h9-C-img4` | `h7-track1-image-T1.3` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-C-img4` | `h9-track2-text-h9-B-v4` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-C-img4` | `h7-track1-image-T1.0` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-C-img4` | `h3-track2-text-T1.0` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-C-img4` | `h3-rep-minimal` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-C-img4` | `h1-brief-text-image` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-C-img4` | `h7-track2-text-T1.0` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-C-img4` | `h3-track1-image-T0.3` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-C-img4` | `h7-track2-text-T0.7` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-C-img4` | `h7-track1-image-T0.3` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-C-img4` | `h3-track2-text-T0.7` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-C-img4` | `h1-brief-text` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-C-img4` | `h1-image-only` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-C-img4` | `h7-track1-image-T0.7` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-C-img4` | `h7-track2-text-T0.3` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-C-img4` | `h1-verbose-text` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-C-img4` | `h3-track2-text-T0.3` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-C-img4` | `h7-track1-image-T0.0` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-C-img4` | `h11-bridge-brief-text-t0` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track1-image-h9-C-img4` | `h7-track2-text-T0.0` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h3-high-track2-text-T0.3` | `h9-track2-text-h9-A-p3` | 0.0004 | 4 |  |
| 1 | consensus | mcc | `h3-high-track2-text-T0.3` | `h9-track2-text-h9-E-p4` | 0.0004 | 4 |  |
| 1 | consensus | mcc | `h3-high-track2-text-T0.3` | `h9-track2-text-h9-B-v1` | 0.0002 | 2 |  |
| 1 | consensus | mcc | `h3-high-track2-text-T0.3` | `h7-track2-text-T1.3` | 0.0002 | 2 |  |
| 1 | consensus | mcc | `h3-high-track2-text-T0.3` | `h7-track1-image-T1.3` | 0.0004 | 4 |  |
| 1 | consensus | mcc | `h3-high-track2-text-T0.3` | `h9-track2-text-h9-B-v4` | 0.0001 | 1 |  |
| 1 | consensus | mcc | `h3-high-track2-text-T0.3` | `h7-track1-image-T1.0` | 0.0001 | 1 |  |
| 1 | consensus | mcc | `h3-high-track2-text-T0.3` | `h3-track2-text-T1.0` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h3-high-track2-text-T0.3` | `h3-rep-minimal` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h3-high-track2-text-T0.3` | `h1-brief-text-image` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h3-high-track2-text-T0.3` | `h7-track2-text-T1.0` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h3-high-track2-text-T0.3` | `h7-track2-text-T0.7` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h3-high-track2-text-T0.3` | `h7-track1-image-T0.3` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h3-high-track2-text-T0.3` | `h3-track1-image-T0.3` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h3-high-track2-text-T0.3` | `h3-track2-text-T0.7` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h3-high-track2-text-T0.3` | `h1-brief-text` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h3-high-track2-text-T0.3` | `h7-track1-image-T0.7` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h3-high-track2-text-T0.3` | `h1-image-only` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h3-high-track2-text-T0.3` | `h7-track2-text-T0.3` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h3-high-track2-text-T0.3` | `h1-verbose-text` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h3-high-track2-text-T0.3` | `h3-track2-text-T0.3` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h3-high-track2-text-T0.3` | `h7-track1-image-T0.0` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h3-high-track2-text-T0.3` | `h11-bridge-brief-text-t0` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h3-high-track2-text-T0.3` | `h7-track2-text-T0.0` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h3-high-track2-text-T0.7` | `h9-track2-text-h9-A-p3` | 0.0002 | 2 |  |
| 1 | consensus | mcc | `h3-high-track2-text-T0.7` | `h9-track2-text-h9-B-v4` | 0.0001 | 1 |  |
| 1 | consensus | mcc | `h3-high-track2-text-T0.7` | `h7-track1-image-T1.0` | 0.0002 | 2 |  |
| 1 | consensus | mcc | `h3-high-track2-text-T0.7` | `h3-track2-text-T1.0` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h3-high-track2-text-T0.7` | `h3-rep-minimal` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h3-high-track2-text-T0.7` | `h1-brief-text-image` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h3-high-track2-text-T0.7` | `h7-track2-text-T1.0` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h3-high-track2-text-T0.7` | `h7-track2-text-T0.7` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h3-high-track2-text-T0.7` | `h3-track1-image-T0.3` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h3-high-track2-text-T0.7` | `h7-track1-image-T0.3` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h3-high-track2-text-T0.7` | `h3-track2-text-T0.7` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h3-high-track2-text-T0.7` | `h1-brief-text` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h3-high-track2-text-T0.7` | `h1-image-only` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h3-high-track2-text-T0.7` | `h7-track1-image-T0.7` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h3-high-track2-text-T0.7` | `h7-track2-text-T0.3` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h3-high-track2-text-T0.7` | `h1-verbose-text` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h3-high-track2-text-T0.7` | `h3-track2-text-T0.3` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h3-high-track2-text-T0.7` | `h7-track1-image-T0.0` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h3-high-track2-text-T0.7` | `h11-bridge-brief-text-t0` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h3-high-track2-text-T0.7` | `h7-track2-text-T0.0` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h3-rep-high` | `h9-track2-text-h9-B-v4` | 0.0001 | 1 |  |
| 1 | consensus | mcc | `h3-rep-high` | `h3-track2-text-T1.0` | 0.0001 | 1 |  |
| 1 | consensus | mcc | `h3-rep-high` | `h3-rep-minimal` | 0.0001 | 1 |  |
| 1 | consensus | mcc | `h3-rep-high` | `h1-brief-text-image` | 0.0001 | 1 |  |
| 1 | consensus | mcc | `h3-rep-high` | `h7-track2-text-T1.0` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h3-rep-high` | `h7-track2-text-T0.7` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h3-rep-high` | `h3-track1-image-T0.3` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h3-rep-high` | `h7-track1-image-T0.3` | 0.0001 | 1 |  |
| 1 | consensus | mcc | `h3-rep-high` | `h3-track2-text-T0.7` | 0.0001 | 1 |  |
| 1 | consensus | mcc | `h3-rep-high` | `h1-brief-text` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h3-rep-high` | `h1-image-only` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h3-rep-high` | `h7-track1-image-T0.7` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h3-rep-high` | `h7-track2-text-T0.3` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h3-rep-high` | `h1-verbose-text` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h3-rep-high` | `h3-track2-text-T0.3` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h3-rep-high` | `h7-track1-image-T0.0` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h3-rep-high` | `h11-bridge-brief-text-t0` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h3-rep-high` | `h7-track2-text-T0.0` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track2-text-h9-A-p1` | `h7-track2-text-T1.0` | 0.0003 | 3 |  |
| 1 | consensus | mcc | `h9-track2-text-h9-A-p1` | `h7-track2-text-T0.7` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track2-text-h9-A-p1` | `h3-track1-image-T0.3` | 0.0001 | 1 |  |
| 1 | consensus | mcc | `h9-track2-text-h9-A-p1` | `h3-track2-text-T0.7` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track2-text-h9-A-p1` | `h1-brief-text` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track2-text-h9-A-p1` | `h1-image-only` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track2-text-h9-A-p1` | `h7-track1-image-T0.7` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track2-text-h9-A-p1` | `h7-track2-text-T0.3` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track2-text-h9-A-p1` | `h1-verbose-text` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track2-text-h9-A-p1` | `h3-track2-text-T0.3` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track2-text-h9-A-p1` | `h7-track1-image-T0.0` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track2-text-h9-A-p1` | `h11-bridge-brief-text-t0` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track2-text-h9-A-p1` | `h7-track2-text-T0.0` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track2-text-h9-B-v3` | `h3-rep-minimal` | 0.0005 | 5 |  |
| 1 | consensus | mcc | `h9-track2-text-h9-B-v3` | `h7-track2-text-T1.0` | 0.0001 | 1 |  |
| 1 | consensus | mcc | `h9-track2-text-h9-B-v3` | `h7-track2-text-T0.7` | 0.0001 | 1 |  |
| 1 | consensus | mcc | `h9-track2-text-h9-B-v3` | `h3-track1-image-T0.3` | 0.0001 | 1 |  |
| 1 | consensus | mcc | `h9-track2-text-h9-B-v3` | `h7-track1-image-T0.3` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track2-text-h9-B-v3` | `h3-track2-text-T0.7` | 0.0001 | 1 |  |
| 1 | consensus | mcc | `h9-track2-text-h9-B-v3` | `h1-brief-text` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track2-text-h9-B-v3` | `h1-image-only` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track2-text-h9-B-v3` | `h7-track1-image-T0.7` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track2-text-h9-B-v3` | `h7-track2-text-T0.3` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track2-text-h9-B-v3` | `h1-verbose-text` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track2-text-h9-B-v3` | `h3-track2-text-T0.3` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track2-text-h9-B-v3` | `h7-track1-image-T0.0` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track2-text-h9-B-v3` | `h11-bridge-brief-text-t0` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track2-text-h9-B-v3` | `h7-track2-text-T0.0` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track2-text-h9-A-p4` | `h7-track2-text-T1.0` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track2-text-h9-A-p4` | `h7-track2-text-T0.7` | 0.0001 | 1 |  |
| 1 | consensus | mcc | `h9-track2-text-h9-A-p4` | `h7-track1-image-T0.3` | 0.0003 | 3 |  |
| 1 | consensus | mcc | `h9-track2-text-h9-A-p4` | `h3-track1-image-T0.3` | 0.0002 | 2 |  |
| 1 | consensus | mcc | `h9-track2-text-h9-A-p4` | `h3-track2-text-T0.7` | 0.0001 | 1 |  |
| 1 | consensus | mcc | `h9-track2-text-h9-A-p4` | `h1-brief-text` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track2-text-h9-A-p4` | `h1-image-only` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track2-text-h9-A-p4` | `h7-track1-image-T0.7` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track2-text-h9-A-p4` | `h7-track2-text-T0.3` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track2-text-h9-A-p4` | `h3-track2-text-T0.3` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track2-text-h9-A-p4` | `h1-verbose-text` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track2-text-h9-A-p4` | `h7-track1-image-T0.0` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track2-text-h9-A-p4` | `h11-bridge-brief-text-t0` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track2-text-h9-A-p4` | `h7-track2-text-T0.0` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track2-text-h9-A-p2` | `h7-track2-text-T1.0` | 0.0003 | 3 |  |
| 1 | consensus | mcc | `h9-track2-text-h9-A-p2` | `h7-track2-text-T0.7` | 0.0003 | 3 |  |
| 1 | consensus | mcc | `h9-track2-text-h9-A-p2` | `h3-track1-image-T0.3` | 0.0001 | 1 |  |
| 1 | consensus | mcc | `h9-track2-text-h9-A-p2` | `h7-track1-image-T0.3` | 0.0005 | 5 |  |
| 1 | consensus | mcc | `h9-track2-text-h9-A-p2` | `h3-track2-text-T0.7` | 0.0001 | 1 |  |
| 1 | consensus | mcc | `h9-track2-text-h9-A-p2` | `h1-brief-text` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track2-text-h9-A-p2` | `h7-track1-image-T0.7` | 0.0001 | 1 |  |
| 1 | consensus | mcc | `h9-track2-text-h9-A-p2` | `h1-image-only` | 0.0001 | 1 |  |
| 1 | consensus | mcc | `h9-track2-text-h9-A-p2` | `h1-verbose-text` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track2-text-h9-A-p2` | `h7-track2-text-T0.3` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track2-text-h9-A-p2` | `h3-track2-text-T0.3` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track2-text-h9-A-p2` | `h7-track1-image-T0.0` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track2-text-h9-A-p2` | `h11-bridge-brief-text-t0` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track2-text-h9-A-p2` | `h7-track2-text-T0.0` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track2-text-h9-D-t1` | `h3-track1-image-T0.3` | 0.0004 | 4 |  |
| 1 | consensus | mcc | `h9-track2-text-h9-D-t1` | `h3-track2-text-T0.7` | 0.0004 | 4 |  |
| 1 | consensus | mcc | `h9-track2-text-h9-D-t1` | `h1-brief-text` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track2-text-h9-D-t1` | `h1-image-only` | 0.0002 | 2 |  |
| 1 | consensus | mcc | `h9-track2-text-h9-D-t1` | `h7-track1-image-T0.7` | 0.0002 | 2 |  |
| 1 | consensus | mcc | `h9-track2-text-h9-D-t1` | `h7-track2-text-T0.3` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track2-text-h9-D-t1` | `h1-verbose-text` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track2-text-h9-D-t1` | `h3-track2-text-T0.3` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track2-text-h9-D-t1` | `h7-track1-image-T0.0` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track2-text-h9-D-t1` | `h11-bridge-brief-text-t0` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track2-text-h9-D-t1` | `h7-track2-text-T0.0` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h3-track1-image-T1.0` | `h3-track1-image-T0.3` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h3-track1-image-T1.0` | `h7-track1-image-T0.3` | 0.0001 | 1 |  |
| 1 | consensus | mcc | `h3-track1-image-T1.0` | `h1-brief-text` | 0.0003 | 3 |  |
| 1 | consensus | mcc | `h3-track1-image-T1.0` | `h1-image-only` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h3-track1-image-T1.0` | `h7-track1-image-T0.7` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h3-track1-image-T1.0` | `h7-track2-text-T0.3` | 0.0002 | 2 |  |
| 1 | consensus | mcc | `h3-track1-image-T1.0` | `h1-verbose-text` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h3-track1-image-T1.0` | `h3-track2-text-T0.3` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h3-track1-image-T1.0` | `h7-track1-image-T0.0` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h3-track1-image-T1.0` | `h11-bridge-brief-text-t0` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h3-track1-image-T1.0` | `h7-track2-text-T0.0` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track2-text-h9-E-p1` | `h1-image-only` | 0.0005 | 5 |  |
| 1 | consensus | mcc | `h9-track2-text-h9-E-p1` | `h7-track1-image-T0.7` | 0.0002 | 2 |  |
| 1 | consensus | mcc | `h9-track2-text-h9-E-p1` | `h7-track2-text-T0.3` | 0.0002 | 2 |  |
| 1 | consensus | mcc | `h9-track2-text-h9-E-p1` | `h1-verbose-text` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track2-text-h9-E-p1` | `h3-track2-text-T0.3` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track2-text-h9-E-p1` | `h7-track1-image-T0.0` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track2-text-h9-E-p1` | `h11-bridge-brief-text-t0` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track2-text-h9-E-p1` | `h7-track2-text-T0.0` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track2-text-h9-D-t2` | `h7-track2-text-T0.7` | 0.0003 | 3 |  |
| 1 | consensus | mcc | `h9-track2-text-h9-D-t2` | `h3-track2-text-T0.7` | 0.0003 | 3 |  |
| 1 | consensus | mcc | `h9-track2-text-h9-D-t2` | `h1-brief-text` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track2-text-h9-D-t2` | `h1-image-only` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track2-text-h9-D-t2` | `h7-track1-image-T0.7` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track2-text-h9-D-t2` | `h7-track2-text-T0.3` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track2-text-h9-D-t2` | `h1-verbose-text` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track2-text-h9-D-t2` | `h3-track2-text-T0.3` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track2-text-h9-D-t2` | `h7-track1-image-T0.0` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track2-text-h9-D-t2` | `h11-bridge-brief-text-t0` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track2-text-h9-D-t2` | `h7-track2-text-T0.0` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track2-text-h9-E-p3` | `h3-track2-text-T0.7` | 0.0005 | 5 |  |
| 1 | consensus | mcc | `h9-track2-text-h9-E-p3` | `h1-brief-text` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track2-text-h9-E-p3` | `h1-image-only` | 0.0003 | 3 |  |
| 1 | consensus | mcc | `h9-track2-text-h9-E-p3` | `h7-track1-image-T0.7` | 0.0003 | 3 |  |
| 1 | consensus | mcc | `h9-track2-text-h9-E-p3` | `h7-track2-text-T0.3` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track2-text-h9-E-p3` | `h1-verbose-text` | 0.0002 | 2 |  |
| 1 | consensus | mcc | `h9-track2-text-h9-E-p3` | `h3-track2-text-T0.3` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track2-text-h9-E-p3` | `h7-track1-image-T0.0` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track2-text-h9-E-p3` | `h11-bridge-brief-text-t0` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track2-text-h9-E-p3` | `h7-track2-text-T0.0` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track2-text-h9-D-t3` | `h7-track2-text-T0.3` | 0.0004 | 4 |  |
| 1 | consensus | mcc | `h9-track2-text-h9-D-t3` | `h1-verbose-text` | 0.0002 | 2 |  |
| 1 | consensus | mcc | `h9-track2-text-h9-D-t3` | `h3-track2-text-T0.3` | 0.0001 | 1 |  |
| 1 | consensus | mcc | `h9-track2-text-h9-D-t3` | `h7-track1-image-T0.0` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track2-text-h9-D-t3` | `h11-bridge-brief-text-t0` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track2-text-h9-D-t3` | `h7-track2-text-T0.0` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h3-track1-image-T0.7` | `h3-track1-image-T0.3` | 0.0002 | 2 |  |
| 1 | consensus | mcc | `h3-track1-image-T0.7` | `h7-track1-image-T0.3` | 0.0005 | 5 |  |
| 1 | consensus | mcc | `h3-track1-image-T0.7` | `h1-image-only` | 0.0004 | 4 |  |
| 1 | consensus | mcc | `h3-track1-image-T0.7` | `h7-track1-image-T0.7` | 0.0001 | 1 |  |
| 1 | consensus | mcc | `h3-track1-image-T0.7` | `h7-track2-text-T0.3` | 0.0002 | 2 |  |
| 1 | consensus | mcc | `h3-track1-image-T0.7` | `h1-verbose-text` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h3-track1-image-T0.7` | `h3-track2-text-T0.3` | 0.0001 | 1 |  |
| 1 | consensus | mcc | `h3-track1-image-T0.7` | `h7-track1-image-T0.0` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h3-track1-image-T0.7` | `h11-bridge-brief-text-t0` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h3-track1-image-T0.7` | `h7-track2-text-T0.0` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track2-text-h9-A-p5` | `h1-verbose-text` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track2-text-h9-A-p5` | `h7-track2-text-T0.3` | 0.0002 | 2 |  |
| 1 | consensus | mcc | `h9-track2-text-h9-A-p5` | `h3-track2-text-T0.3` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track2-text-h9-A-p5` | `h7-track1-image-T0.0` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track2-text-h9-A-p5` | `h11-bridge-brief-text-t0` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track2-text-h9-A-p5` | `h7-track2-text-T0.0` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track2-text-h9-D-t5` | `h7-track2-text-T0.3` | 0.0003 | 3 |  |
| 1 | consensus | mcc | `h9-track2-text-h9-D-t5` | `h3-track2-text-T0.3` | 0.0002 | 2 |  |
| 1 | consensus | mcc | `h9-track2-text-h9-D-t5` | `h7-track1-image-T0.0` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track2-text-h9-D-t5` | `h11-bridge-brief-text-t0` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track2-text-h9-D-t5` | `h7-track2-text-T0.0` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track2-text-h9-B-v2` | `h1-verbose-text` | 0.0003 | 3 |  |
| 1 | consensus | mcc | `h9-track2-text-h9-B-v2` | `h7-track2-text-T0.3` | 0.0003 | 3 |  |
| 1 | consensus | mcc | `h9-track2-text-h9-B-v2` | `h3-track2-text-T0.3` | 0.0001 | 1 |  |
| 1 | consensus | mcc | `h9-track2-text-h9-B-v2` | `h7-track1-image-T0.0` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track2-text-h9-B-v2` | `h11-bridge-brief-text-t0` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track2-text-h9-B-v2` | `h7-track2-text-T0.0` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track2-text-h9-B-v5` | `h3-track2-text-T0.3` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track2-text-h9-B-v5` | `h11-bridge-brief-text-t0` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track2-text-h9-B-v5` | `h7-track1-image-T0.0` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track2-text-h9-B-v5` | `h7-track2-text-T0.0` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track2-text-h9-D-t4` | `h3-track2-text-T0.3` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track2-text-h9-D-t4` | `h1-verbose-text` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track2-text-h9-D-t4` | `h7-track1-image-T0.0` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track2-text-h9-D-t4` | `h11-bridge-brief-text-t0` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track2-text-h9-D-t4` | `h7-track2-text-T0.0` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track2-text-h9-E-p2` | `h7-track2-text-T0.3` | 0.0003 | 3 |  |
| 1 | consensus | mcc | `h9-track2-text-h9-E-p2` | `h1-verbose-text` | 0.0003 | 3 |  |
| 1 | consensus | mcc | `h9-track2-text-h9-E-p2` | `h3-track2-text-T0.3` | 0.0001 | 1 |  |
| 1 | consensus | mcc | `h9-track2-text-h9-E-p2` | `h7-track1-image-T0.0` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track2-text-h9-E-p2` | `h11-bridge-brief-text-t0` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track2-text-h9-E-p2` | `h7-track2-text-T0.0` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track2-text-h9-E-p5` | `h3-track2-text-T0.3` | 0.0005 | 5 |  |
| 1 | consensus | mcc | `h9-track2-text-h9-E-p5` | `h7-track1-image-T0.0` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track2-text-h9-E-p5` | `h11-bridge-brief-text-t0` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track2-text-h9-E-p5` | `h7-track2-text-T0.0` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track2-text-h9-A-p3` | `h7-track1-image-T0.0` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track2-text-h9-A-p3` | `h11-bridge-brief-text-t0` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track2-text-h9-A-p3` | `h7-track2-text-T0.0` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track2-text-h9-E-p4` | `h3-track2-text-T0.3` | 0.0004 | 4 |  |
| 1 | consensus | mcc | `h9-track2-text-h9-E-p4` | `h7-track1-image-T0.0` | 0.0001 | 1 |  |
| 1 | consensus | mcc | `h9-track2-text-h9-E-p4` | `h11-bridge-brief-text-t0` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track2-text-h9-E-p4` | `h7-track2-text-T0.0` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track2-text-h9-B-v1` | `h3-track2-text-T0.3` | 0.0001 | 1 |  |
| 1 | consensus | mcc | `h9-track2-text-h9-B-v1` | `h7-track1-image-T0.0` | 0.0001 | 1 |  |
| 1 | consensus | mcc | `h9-track2-text-h9-B-v1` | `h11-bridge-brief-text-t0` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h9-track2-text-h9-B-v1` | `h7-track2-text-T0.0` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h1-verbose-text-image` | `h7-track1-image-T0.7` | 0.0002 | 2 |  |
| 1 | consensus | mcc | `h1-verbose-text-image` | `h7-track1-image-T0.0` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h1-verbose-text-image` | `h11-bridge-brief-text-t0` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h1-verbose-text-image` | `h7-track2-text-T0.0` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h7-track2-text-T1.3` | `h3-track2-text-T0.3` | 0.0003 | 3 |  |
| 1 | consensus | mcc | `h7-track2-text-T1.3` | `h7-track1-image-T0.0` | 0.0002 | 2 |  |
| 1 | consensus | mcc | `h7-track2-text-T1.3` | `h7-track2-text-T0.0` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h7-track2-text-T1.3` | `h11-bridge-brief-text-t0` | 0.0001 | 1 |  |
| 1 | consensus | mcc | `h7-track1-image-T1.3` | `h7-track1-image-T0.0` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h7-track1-image-T1.3` | `h11-bridge-brief-text-t0` | 0.0002 | 2 |  |
| 1 | consensus | mcc | `h7-track1-image-T1.3` | `h7-track2-text-T0.0` | 0.0001 | 1 |  |
| 1 | consensus | mcc | `h9-track2-text-h9-B-v4` | `h7-track2-text-T0.0` | 0.0004 | 4 |  |
| 1 | consensus | mcc | `h7-track1-image-T1.0` | `h7-track1-image-T0.0` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h7-track1-image-T1.0` | `h7-track2-text-T0.0` | 0.0003 | 3 |  |
| 1 | consensus | mcc | `h3-track2-text-T1.0` | `h11-bridge-brief-text-t0` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h3-track2-text-T1.0` | `h7-track2-text-T0.0` | 0.0000 | 0 | Y |
| 1 | consensus | mcc | `h3-rep-minimal` | `h7-track2-text-T0.0` | 0.0001 | 1 |  |
| 1 | consensus | mcc | `h1-brief-text-image` | `h7-track1-image-T0.0` | 0.0000 | 0 | Y |
| 2 | single-pass | f1 | `h11-pvd-pro-medium-text-baseline` | `h11-pvd-pro-medium-image-baseline` | 0.0000 | 0 | Y |
| 2 | single-pass | f1 | `h11-pvd-pro-medium-text-baseline` | `h11-pvd-image-baseline` | 0.0000 | 0 | Y |
| 2 | single-pass | f1 | `h11-pvd-pro-medium-text-baseline` | `h11-pvd-text-baseline` | 0.0000 | 0 | Y |
| 2 | single-pass | f1 | `h11-pvd-pro-medium-text-baseline` | `h11-n1-pro-image-medium-t07` | 0.0000 | 0 | Y |
| 2 | single-pass | f1 | `h11-pvd-pro-medium-image-baseline` | `h11-n1-pro-image-medium-t07` | 0.0000 | 0 | Y |
| 2 | single-pass | f1 | `h11-pvd-pro-medium-text-baseline` | `h11-n1-pro-text-medium-t07` | 0.0000 | 0 | Y |
| 2 | single-pass | f1 | `h11-pvd-pro-medium-image-baseline` | `h11-n1-pro-text-medium-t07` | 0.0000 | 0 | Y |
| 2 | single-pass | f1 | `h11-pvd-image-baseline` | `h11-n1-pro-image-medium-t07` | 0.0000 | 0 | Y |
| 2 | single-pass | f1 | `h11-pvd-image-baseline` | `h11-n1-pro-text-medium-t07` | 0.0000 | 0 | Y |
| 2 | single-pass | f1 | `h11-pvd-text-baseline` | `h11-n1-pro-text-medium-t07` | 0.0000 | 0 | Y |
| 2 | single-pass | mcc | `h11-pvd-pro-medium-text-baseline` | `h11-pvd-text-baseline` | 0.0000 | 0 | Y |
| 2 | single-pass | mcc | `h11-pvd-pro-medium-image-baseline` | `h11-pvd-image-baseline` | 0.0000 | 0 | Y |
| 2 | single-pass | mcc | `h11-pvd-pro-medium-image-baseline` | `h11-n1-pro-text-medium-t07` | 0.0000 | 0 | Y |
| 2 | single-pass | mcc | `h11-pvd-pro-medium-text-baseline` | `h11-pvd-image-baseline` | 0.0000 | 0 | Y |
| 2 | single-pass | mcc | `h11-pvd-pro-medium-text-baseline` | `h11-n1-pro-text-medium-t07` | 0.0000 | 0 | Y |
| 2 | single-pass | mcc | `h11-pvd-pro-medium-image-baseline` | `h11-pvd-text-baseline` | 0.0000 | 0 | Y |
| 2 | single-pass | mcc | `h11-n1-pro-image-medium-t07` | `h11-pvd-text-baseline` | 0.0000 | 0 | Y |
| 2 | single-pass | mcc | `h11-n1-pro-image-medium-t07` | `h11-pvd-image-baseline` | 0.0000 | 0 | Y |
| 2 | single-pass | mcc | `h11-n1-pro-image-medium-t07` | `h11-n1-pro-text-medium-t07` | 0.0000 | 0 | Y |
| 2 | single-pass | mcc | `h11-pvd-image-baseline` | `h11-pvd-text-baseline` | 0.0000 | 0 | Y |
| 2 | single-pass | mcc | `h11-n1-pro-text-medium-t07` | `h11-pvd-text-baseline` | 0.0000 | 0 | Y |
| 2 | consensus | f1 | `h11-pvd-pro-high-text-n5` | `scale4-optimal-487` | 0.0001 | 1 |  |
| 2 | consensus | f1 | `h11-pvd-pro-high-text-n5` | `p3a-high-image-t1.0` | 0.0000 | 0 | Y |
| 2 | consensus | f1 | `h11-pvd-pro-high-text-n5` | `p3a-high-image-t0.3` | 0.0000 | 0 | Y |
| 2 | consensus | f1 | `h11-pvd-pro-high-text-n5` | `h11-e47-propose-brief` | 0.0000 | 0 | Y |
| 2 | consensus | f1 | `h11-pvd-pro-high-text-n5` | `h11-pvd-pro-high-image-n5` | 0.0000 | 0 | Y |
| 2 | consensus | f1 | `h11-pvd-pro-high-text-n5` | `p3a-minimal-text-t1.0` | 0.0000 | 0 | Y |
| 2 | consensus | f1 | `h11-pvd-pro-high-text-n5` | `h11-pvd-image-n5` | 0.0000 | 0 | Y |
| 2 | consensus | f1 | `h11-pvd-pro-high-text-n5` | `h11-n1-image-t03` | 0.0000 | 0 | Y |
| 2 | consensus | f1 | `h11-pvd-pro-high-text-n5` | `h11-pvd-flash-minimal-text-n30-t07` | 0.0000 | 0 | Y |
| 2 | consensus | f1 | `h11-pvd-pro-high-text-n5` | `p3a-minimal-text-t1.0-n5` | 0.0000 | 0 | Y |
| 2 | consensus | f1 | `h11-pvd-pro-high-text-n5` | `p3a-min-image-t0.3` | 0.0000 | 0 | Y |
| 2 | consensus | f1 | `h11-pvd-pro-high-text-n5` | `p3a-min-image-t1.0` | 0.0000 | 0 | Y |
| 2 | consensus | f1 | `h11-pvd-pro-high-text-n5` | `p3a-minimal-text-t0.3` | 0.0000 | 0 | Y |
| 2 | consensus | f1 | `h11-pvd-pro-high-text-n5` | `p3a-minimal-text-t0.3-n5` | 0.0000 | 0 | Y |
| 2 | consensus | f1 | `h11-pvd-pro-high-text-n5` | `h11-pvd-text-n10` | 0.0000 | 0 | Y |
| 2 | consensus | f1 | `h11-pvd-pro-high-text-n5` | `p3a-high-text-t0.0` | 0.0000 | 0 | Y |
| 2 | consensus | f1 | `h11-pvd-pro-high-text-n5` | `h11-n1-image-t0` | 0.0000 | 0 | Y |
| 2 | consensus | f1 | `h11-pvd-pro-high-text-n5` | `p3a-minimal-text-t0.0` | 0.0000 | 0 | Y |
| 2 | consensus | f1 | `h11-pvd-pro-high-text-n5` | `h11-n1-brief-text-t03` | 0.0000 | 0 | Y |
| 2 | consensus | f1 | `h11-pvd-pro-high-text-n5` | `h11-n1-pro-text-high-t0` | 0.0000 | 0 | Y |
| 2 | consensus | f1 | `h11-pvd-pro-high-text-n5` | `h11-n1-pro-image-high-t0` | 0.0000 | 0 | Y |
| 2 | consensus | f1 | `h11-pvd-pro-high-text-n5` | `p3a-high-image-t0.0` | 0.0000 | 0 | Y |
| 2 | consensus | f1 | `h11-pvd-flash-high-text-n5` | `scale4-optimal-487` | 0.0004 | 4 |  |
| 2 | consensus | f1 | `h11-pvd-flash-high-text-n5` | `p3a-high-image-t1.0` | 0.0001 | 1 |  |
| 2 | consensus | f1 | `h11-pvd-flash-high-text-n5` | `p3a-high-image-t0.3` | 0.0001 | 1 |  |
| 2 | consensus | f1 | `h11-pvd-flash-high-text-n5` | `h11-e47-propose-brief` | 0.0000 | 0 | Y |
| 2 | consensus | f1 | `h11-pvd-flash-high-text-n5` | `h11-pvd-pro-high-image-n5` | 0.0000 | 0 | Y |
| 2 | consensus | f1 | `h11-pvd-flash-high-text-n5` | `h11-pvd-image-n5` | 0.0000 | 0 | Y |
| 2 | consensus | f1 | `h11-pvd-flash-high-text-n5` | `h11-n1-image-t03` | 0.0000 | 0 | Y |
| 2 | consensus | f1 | `h11-pvd-flash-high-text-n5` | `p3a-minimal-text-t1.0` | 0.0000 | 0 | Y |
| 2 | consensus | f1 | `h11-pvd-flash-high-text-n5` | `p3a-minimal-text-t1.0-n5` | 0.0000 | 0 | Y |
| 2 | consensus | f1 | `h11-pvd-flash-high-text-n5` | `h11-pvd-flash-minimal-text-n30-t07` | 0.0000 | 0 | Y |
| 2 | consensus | f1 | `h11-pvd-flash-high-text-n5` | `p3a-min-image-t0.3` | 0.0000 | 0 | Y |
| 2 | consensus | f1 | `h11-pvd-flash-high-text-n5` | `p3a-min-image-t1.0` | 0.0000 | 0 | Y |
| 2 | consensus | f1 | `h11-pvd-flash-high-text-n5` | `p3a-minimal-text-t0.3` | 0.0000 | 0 | Y |
| 2 | consensus | f1 | `h11-pvd-flash-high-text-n5` | `p3a-minimal-text-t0.3-n5` | 0.0000 | 0 | Y |
| 2 | consensus | f1 | `h11-pvd-flash-high-text-n5` | `h11-n1-image-t0` | 0.0000 | 0 | Y |
| 2 | consensus | f1 | `h11-pvd-flash-high-text-n5` | `h11-pvd-text-n10` | 0.0000 | 0 | Y |
| 2 | consensus | f1 | `h11-pvd-flash-high-text-n5` | `p3a-high-text-t0.0` | 0.0000 | 0 | Y |
| 2 | consensus | f1 | `h11-pvd-flash-high-text-n5` | `p3a-minimal-text-t0.0` | 0.0000 | 0 | Y |
| 2 | consensus | f1 | `h11-pvd-flash-high-text-n5` | `h11-n1-brief-text-t03` | 0.0000 | 0 | Y |
| 2 | consensus | f1 | `h11-pvd-flash-high-text-n5` | `h11-n1-pro-text-high-t0` | 0.0000 | 0 | Y |
| 2 | consensus | f1 | `h11-pvd-flash-high-text-n5` | `h11-n1-pro-image-high-t0` | 0.0000 | 0 | Y |
| 2 | consensus | f1 | `h11-pvd-flash-high-text-n5` | `p3a-high-image-t0.0` | 0.0000 | 0 | Y |
| 2 | consensus | f1 | `p3a-high-text-t0.3` | `h11-e47-propose-brief` | 0.0000 | 0 | Y |
| 2 | consensus | f1 | `p3a-high-text-t0.3` | `h11-pvd-image-n5` | 0.0000 | 0 | Y |
| 2 | consensus | f1 | `p3a-high-text-t0.3` | `h11-n1-image-t03` | 0.0000 | 0 | Y |
| 2 | consensus | f1 | `p3a-high-text-t0.3` | `p3a-minimal-text-t1.0` | 0.0000 | 0 | Y |
| 2 | consensus | f1 | `p3a-high-text-t0.3` | `p3a-minimal-text-t1.0-n5` | 0.0000 | 0 | Y |
| 2 | consensus | f1 | `p3a-high-text-t0.3` | `h11-pvd-flash-minimal-text-n30-t07` | 0.0000 | 0 | Y |
| 2 | consensus | f1 | `p3a-high-text-t0.3` | `p3a-min-image-t0.3` | 0.0000 | 0 | Y |
| 2 | consensus | f1 | `p3a-high-text-t0.3` | `p3a-min-image-t1.0` | 0.0000 | 0 | Y |
| 2 | consensus | f1 | `p3a-high-text-t0.3` | `p3a-minimal-text-t0.3` | 0.0000 | 0 | Y |
| 2 | consensus | f1 | `p3a-high-text-t0.3` | `p3a-minimal-text-t0.3-n5` | 0.0000 | 0 | Y |
| 2 | consensus | f1 | `p3a-high-text-t0.3` | `h11-pvd-text-n10` | 0.0000 | 0 | Y |
| 2 | consensus | f1 | `p3a-high-text-t0.3` | `h11-n1-image-t0` | 0.0000 | 0 | Y |
| 2 | consensus | f1 | `p3a-high-text-t0.3` | `p3a-high-text-t0.0` | 0.0000 | 0 | Y |
| 2 | consensus | f1 | `p3a-high-text-t0.3` | `p3a-minimal-text-t0.0` | 0.0000 | 0 | Y |
| 2 | consensus | f1 | `p3a-high-text-t0.3` | `h11-n1-brief-text-t03` | 0.0000 | 0 | Y |
| 2 | consensus | f1 | `p3a-high-text-t0.3` | `h11-n1-pro-text-high-t0` | 0.0000 | 0 | Y |
| 2 | consensus | f1 | `p3a-high-text-t0.3` | `h11-n1-pro-image-high-t0` | 0.0000 | 0 | Y |
| 2 | consensus | f1 | `p3a-high-text-t0.3` | `p3a-high-image-t0.0` | 0.0000 | 0 | Y |
| 2 | consensus | f1 | `p3a-high-text-t0.3-n5` | `h11-e47-propose-brief` | 0.0000 | 0 | Y |
| 2 | consensus | f1 | `p3a-high-text-t0.3-n5` | `h11-pvd-image-n5` | 0.0000 | 0 | Y |
| 2 | consensus | f1 | `p3a-high-text-t0.3-n5` | `p3a-minimal-text-t1.0` | 0.0000 | 0 | Y |
| 2 | consensus | f1 | `p3a-high-text-t0.3-n5` | `h11-n1-image-t03` | 0.0000 | 0 | Y |
| 2 | consensus | f1 | `p3a-high-text-t0.3-n5` | `p3a-minimal-text-t1.0-n5` | 0.0000 | 0 | Y |
| 2 | consensus | f1 | `p3a-high-text-t0.3-n5` | `h11-pvd-flash-minimal-text-n30-t07` | 0.0000 | 0 | Y |
| 2 | consensus | f1 | `p3a-high-text-t0.3-n5` | `p3a-min-image-t0.3` | 0.0000 | 0 | Y |
| 2 | consensus | f1 | `p3a-high-text-t0.3-n5` | `p3a-min-image-t1.0` | 0.0000 | 0 | Y |
| 2 | consensus | f1 | `p3a-high-text-t0.3-n5` | `p3a-minimal-text-t0.3` | 0.0000 | 0 | Y |
| 2 | consensus | f1 | `p3a-high-text-t0.3-n5` | `p3a-minimal-text-t0.3-n5` | 0.0000 | 0 | Y |
| 2 | consensus | f1 | `p3a-high-text-t0.3-n5` | `h11-n1-image-t0` | 0.0000 | 0 | Y |
| 2 | consensus | f1 | `p3a-high-text-t0.3-n5` | `h11-pvd-text-n10` | 0.0000 | 0 | Y |
| 2 | consensus | f1 | `p3a-high-text-t0.3-n5` | `p3a-minimal-text-t0.0` | 0.0000 | 0 | Y |
| 2 | consensus | f1 | `p3a-high-text-t0.3-n5` | `p3a-high-text-t0.0` | 0.0000 | 0 | Y |
| 2 | consensus | f1 | `p3a-high-text-t0.3-n5` | `h11-n1-brief-text-t03` | 0.0000 | 0 | Y |
| 2 | consensus | f1 | `p3a-high-text-t0.3-n5` | `h11-n1-pro-text-high-t0` | 0.0000 | 0 | Y |
| 2 | consensus | f1 | `p3a-high-text-t0.3-n5` | `h11-n1-pro-image-high-t0` | 0.0000 | 0 | Y |
| 2 | consensus | f1 | `p3a-high-text-t0.3-n5` | `p3a-high-image-t0.0` | 0.0000 | 0 | Y |
| 2 | consensus | f1 | `p3a-high-text-t1.0` | `h11-pvd-image-n5` | 0.0000 | 0 | Y |
| 2 | consensus | f1 | `p3a-high-text-t1.0` | `h11-n1-image-t03` | 0.0001 | 1 |  |
| 2 | consensus | f1 | `p3a-high-text-t1.0` | `p3a-minimal-text-t1.0` | 0.0000 | 0 | Y |
| 2 | consensus | f1 | `p3a-high-text-t1.0` | `h11-pvd-flash-minimal-text-n30-t07` | 0.0000 | 0 | Y |
| 2 | consensus | f1 | `p3a-high-text-t1.0` | `p3a-minimal-text-t1.0-n5` | 0.0000 | 0 | Y |
| 2 | consensus | f1 | `p3a-high-text-t1.0` | `p3a-min-image-t0.3` | 0.0000 | 0 | Y |
| 2 | consensus | f1 | `p3a-high-text-t1.0` | `p3a-min-image-t1.0` | 0.0000 | 0 | Y |
| 2 | consensus | f1 | `p3a-high-text-t1.0` | `p3a-minimal-text-t0.3` | 0.0000 | 0 | Y |
| 2 | consensus | f1 | `p3a-high-text-t1.0` | `p3a-minimal-text-t0.3-n5` | 0.0000 | 0 | Y |
| 2 | consensus | f1 | `p3a-high-text-t1.0` | `h11-pvd-text-n10` | 0.0000 | 0 | Y |
| 2 | consensus | f1 | `p3a-high-text-t1.0` | `h11-n1-image-t0` | 0.0000 | 0 | Y |
| 2 | consensus | f1 | `p3a-high-text-t1.0` | `p3a-high-text-t0.0` | 0.0000 | 0 | Y |
| 2 | consensus | f1 | `p3a-high-text-t1.0` | `h11-n1-brief-text-t03` | 0.0000 | 0 | Y |
| 2 | consensus | f1 | `p3a-high-text-t1.0` | `p3a-minimal-text-t0.0` | 0.0000 | 0 | Y |
| 2 | consensus | f1 | `p3a-high-text-t1.0` | `h11-n1-pro-text-high-t0` | 0.0000 | 0 | Y |
| 2 | consensus | f1 | `p3a-high-text-t1.0` | `h11-n1-pro-image-high-t0` | 0.0000 | 0 | Y |
| 2 | consensus | f1 | `p3a-high-text-t1.0` | `p3a-high-image-t0.0` | 0.0000 | 0 | Y |
| 2 | consensus | f1 | `p3a-high-text-t1.0-n5` | `h11-pvd-image-n5` | 0.0000 | 0 | Y |
| 2 | consensus | f1 | `p3a-high-text-t1.0-n5` | `h11-n1-image-t03` | 0.0001 | 1 |  |
| 2 | consensus | f1 | `p3a-high-text-t1.0-n5` | `p3a-minimal-text-t1.0` | 0.0000 | 0 | Y |
| 2 | consensus | f1 | `p3a-high-text-t1.0-n5` | `p3a-minimal-text-t1.0-n5` | 0.0000 | 0 | Y |
| 2 | consensus | f1 | `p3a-high-text-t1.0-n5` | `h11-pvd-flash-minimal-text-n30-t07` | 0.0000 | 0 | Y |
| 2 | consensus | f1 | `p3a-high-text-t1.0-n5` | `p3a-min-image-t0.3` | 0.0000 | 0 | Y |
| 2 | consensus | f1 | `p3a-high-text-t1.0-n5` | `p3a-min-image-t1.0` | 0.0000 | 0 | Y |
| 2 | consensus | f1 | `p3a-high-text-t1.0-n5` | `p3a-minimal-text-t0.3` | 0.0000 | 0 | Y |
| 2 | consensus | f1 | `p3a-high-text-t1.0-n5` | `p3a-minimal-text-t0.3-n5` | 0.0000 | 0 | Y |
| 2 | consensus | f1 | `p3a-high-text-t1.0-n5` | `h11-pvd-text-n10` | 0.0000 | 0 | Y |
| 2 | consensus | f1 | `p3a-high-text-t1.0-n5` | `h11-n1-image-t0` | 0.0000 | 0 | Y |
| 2 | consensus | f1 | `p3a-high-text-t1.0-n5` | `p3a-minimal-text-t0.0` | 0.0000 | 0 | Y |
| 2 | consensus | f1 | `p3a-high-text-t1.0-n5` | `p3a-high-text-t0.0` | 0.0000 | 0 | Y |
| 2 | consensus | f1 | `p3a-high-text-t1.0-n5` | `h11-n1-brief-text-t03` | 0.0000 | 0 | Y |
| 2 | consensus | f1 | `p3a-high-text-t1.0-n5` | `h11-n1-pro-text-high-t0` | 0.0000 | 0 | Y |
| 2 | consensus | f1 | `p3a-high-text-t1.0-n5` | `h11-n1-pro-image-high-t0` | 0.0000 | 0 | Y |
| 2 | consensus | f1 | `p3a-high-text-t1.0-n5` | `p3a-high-image-t0.0` | 0.0000 | 0 | Y |
| 2 | consensus | f1 | `h11-pvd-flash-high-image-n5` | `h11-pvd-image-n5` | 0.0001 | 1 |  |
| 2 | consensus | f1 | `h11-pvd-flash-high-image-n5` | `h11-n1-image-t03` | 0.0002 | 2 |  |
| 2 | consensus | f1 | `h11-pvd-flash-high-image-n5` | `h11-pvd-flash-minimal-text-n30-t07` | 0.0005 | 5 |  |
| 2 | consensus | f1 | `h11-pvd-flash-high-image-n5` | `p3a-min-image-t0.3` | 0.0000 | 0 | Y |
| 2 | consensus | f1 | `h11-pvd-flash-high-image-n5` | `p3a-min-image-t1.0` | 0.0000 | 0 | Y |
| 2 | consensus | f1 | `h11-pvd-flash-high-image-n5` | `p3a-minimal-text-t0.3` | 0.0000 | 0 | Y |
| 2 | consensus | f1 | `h11-pvd-flash-high-image-n5` | `p3a-minimal-text-t0.3-n5` | 0.0000 | 0 | Y |
| 2 | consensus | f1 | `h11-pvd-flash-high-image-n5` | `h11-n1-image-t0` | 0.0000 | 0 | Y |
| 2 | consensus | f1 | `h11-pvd-flash-high-image-n5` | `h11-pvd-text-n10` | 0.0000 | 0 | Y |
| 2 | consensus | f1 | `h11-pvd-flash-high-image-n5` | `p3a-high-text-t0.0` | 0.0000 | 0 | Y |
| 2 | consensus | f1 | `h11-pvd-flash-high-image-n5` | `p3a-minimal-text-t0.0` | 0.0000 | 0 | Y |
| 2 | consensus | f1 | `h11-pvd-flash-high-image-n5` | `h11-n1-brief-text-t03` | 0.0000 | 0 | Y |
| 2 | consensus | f1 | `h11-pvd-flash-high-image-n5` | `h11-n1-pro-text-high-t0` | 0.0000 | 0 | Y |
| 2 | consensus | f1 | `h11-pvd-flash-high-image-n5` | `h11-n1-pro-image-high-t0` | 0.0000 | 0 | Y |
| 2 | consensus | f1 | `h11-pvd-flash-high-image-n5` | `p3a-high-image-t0.0` | 0.0000 | 0 | Y |
| 2 | consensus | f1 | `scale4-optimal-487` | `p3a-min-image-t0.3` | 0.0000 | 0 | Y |
| 2 | consensus | f1 | `scale4-optimal-487` | `p3a-min-image-t1.0` | 0.0000 | 0 | Y |
| 2 | consensus | f1 | `scale4-optimal-487` | `p3a-minimal-text-t0.3` | 0.0000 | 0 | Y |
| 2 | consensus | f1 | `scale4-optimal-487` | `p3a-minimal-text-t0.3-n5` | 0.0000 | 0 | Y |
| 2 | consensus | f1 | `scale4-optimal-487` | `h11-n1-image-t0` | 0.0000 | 0 | Y |
| 2 | consensus | f1 | `scale4-optimal-487` | `h11-pvd-text-n10` | 0.0000 | 0 | Y |
| 2 | consensus | f1 | `scale4-optimal-487` | `p3a-high-text-t0.0` | 0.0000 | 0 | Y |
| 2 | consensus | f1 | `scale4-optimal-487` | `p3a-minimal-text-t0.0` | 0.0000 | 0 | Y |
| 2 | consensus | f1 | `scale4-optimal-487` | `h11-n1-brief-text-t03` | 0.0000 | 0 | Y |
| 2 | consensus | f1 | `scale4-optimal-487` | `h11-n1-pro-text-high-t0` | 0.0000 | 0 | Y |
| 2 | consensus | f1 | `scale4-optimal-487` | `h11-n1-pro-image-high-t0` | 0.0000 | 0 | Y |
| 2 | consensus | f1 | `scale4-optimal-487` | `p3a-high-image-t0.0` | 0.0000 | 0 | Y |
| 2 | consensus | f1 | `p3a-high-image-t1.0` | `p3a-min-image-t1.0` | 0.0000 | 0 | Y |
| 2 | consensus | f1 | `p3a-high-image-t1.0` | `p3a-min-image-t0.3` | 0.0001 | 1 |  |
| 2 | consensus | f1 | `p3a-high-image-t1.0` | `p3a-minimal-text-t0.3` | 0.0005 | 5 |  |
| 2 | consensus | f1 | `p3a-high-image-t1.0` | `p3a-minimal-text-t0.3-n5` | 0.0005 | 5 |  |
| 2 | consensus | f1 | `p3a-high-image-t1.0` | `h11-n1-image-t0` | 0.0000 | 0 | Y |
| 2 | consensus | f1 | `p3a-high-image-t1.0` | `h11-pvd-text-n10` | 0.0000 | 0 | Y |
| 2 | consensus | f1 | `p3a-high-image-t1.0` | `p3a-high-text-t0.0` | 0.0001 | 1 |  |
| 2 | consensus | f1 | `p3a-high-image-t1.0` | `p3a-minimal-text-t0.0` | 0.0000 | 0 | Y |
| 2 | consensus | f1 | `p3a-high-image-t1.0` | `h11-n1-brief-text-t03` | 0.0000 | 0 | Y |
| 2 | consensus | f1 | `p3a-high-image-t1.0` | `h11-n1-pro-text-high-t0` | 0.0000 | 0 | Y |
| 2 | consensus | f1 | `p3a-high-image-t1.0` | `h11-n1-pro-image-high-t0` | 0.0000 | 0 | Y |
| 2 | consensus | f1 | `p3a-high-image-t1.0` | `p3a-high-image-t0.0` | 0.0000 | 0 | Y |
| 2 | consensus | f1 | `p3a-high-image-t0.3` | `p3a-min-image-t1.0` | 0.0001 | 1 |  |
| 2 | consensus | f1 | `p3a-high-image-t0.3` | `p3a-min-image-t0.3` | 0.0002 | 2 |  |
| 2 | consensus | f1 | `p3a-high-image-t0.3` | `h11-pvd-text-n10` | 0.0001 | 1 |  |
| 2 | consensus | f1 | `p3a-high-image-t0.3` | `h11-n1-image-t0` | 0.0000 | 0 | Y |
| 2 | consensus | f1 | `p3a-high-image-t0.3` | `p3a-high-text-t0.0` | 0.0004 | 4 |  |
| 2 | consensus | f1 | `p3a-high-image-t0.3` | `p3a-minimal-text-t0.0` | 0.0000 | 0 | Y |
| 2 | consensus | f1 | `p3a-high-image-t0.3` | `h11-n1-pro-text-high-t0` | 0.0000 | 0 | Y |
| 2 | consensus | f1 | `p3a-high-image-t0.3` | `h11-n1-brief-text-t03` | 0.0000 | 0 | Y |
| 2 | consensus | f1 | `p3a-high-image-t0.3` | `h11-n1-pro-image-high-t0` | 0.0000 | 0 | Y |
| 2 | consensus | f1 | `p3a-high-image-t0.3` | `p3a-high-image-t0.0` | 0.0000 | 0 | Y |
| 2 | consensus | f1 | `h11-e47-propose-brief` | `h11-n1-image-t0` | 0.0003 | 3 |  |
| 2 | consensus | f1 | `h11-e47-propose-brief` | `h11-pvd-text-n10` | 0.0000 | 0 | Y |
| 2 | consensus | f1 | `h11-e47-propose-brief` | `p3a-high-text-t0.0` | 0.0004 | 4 |  |
| 2 | consensus | f1 | `h11-e47-propose-brief` | `p3a-minimal-text-t0.0` | 0.0000 | 0 | Y |
| 2 | consensus | f1 | `h11-e47-propose-brief` | `h11-n1-brief-text-t03` | 0.0001 | 1 |  |
| 2 | consensus | f1 | `h11-e47-propose-brief` | `h11-n1-pro-image-high-t0` | 0.0000 | 0 | Y |
| 2 | consensus | f1 | `h11-e47-propose-brief` | `h11-n1-pro-text-high-t0` | 0.0000 | 0 | Y |
| 2 | consensus | f1 | `h11-e47-propose-brief` | `p3a-high-image-t0.0` | 0.0000 | 0 | Y |
| 2 | consensus | f1 | `h11-pvd-pro-high-image-n5` | `h11-n1-pro-text-high-t0` | 0.0000 | 0 | Y |
| 2 | consensus | f1 | `h11-pvd-pro-high-image-n5` | `h11-n1-pro-image-high-t0` | 0.0000 | 0 | Y |
| 2 | consensus | f1 | `h11-pvd-pro-high-image-n5` | `p3a-high-image-t0.0` | 0.0000 | 0 | Y |
| 2 | consensus | f1 | `h11-pvd-image-n5` | `h11-n1-pro-text-high-t0` | 0.0000 | 0 | Y |
| 2 | consensus | f1 | `h11-pvd-image-n5` | `h11-n1-pro-image-high-t0` | 0.0000 | 0 | Y |
| 2 | consensus | f1 | `h11-pvd-image-n5` | `p3a-high-image-t0.0` | 0.0000 | 0 | Y |
| 2 | consensus | f1 | `h11-n1-image-t03` | `h11-n1-image-t0` | 0.0000 | 0 | Y |
| 2 | consensus | f1 | `h11-n1-image-t03` | `h11-n1-pro-text-high-t0` | 0.0000 | 0 | Y |
| 2 | consensus | f1 | `h11-n1-image-t03` | `h11-n1-pro-image-high-t0` | 0.0000 | 0 | Y |
| 2 | consensus | f1 | `h11-n1-image-t03` | `p3a-high-image-t0.0` | 0.0000 | 0 | Y |
| 2 | consensus | f1 | `p3a-minimal-text-t1.0` | `p3a-minimal-text-t0.0` | 0.0001 | 1 |  |
| 2 | consensus | f1 | `p3a-minimal-text-t1.0` | `h11-n1-brief-text-t03` | 0.0002 | 2 |  |
| 2 | consensus | f1 | `p3a-minimal-text-t1.0` | `h11-n1-pro-text-high-t0` | 0.0003 | 3 |  |
| 2 | consensus | f1 | `p3a-minimal-text-t1.0` | `h11-n1-pro-image-high-t0` | 0.0002 | 2 |  |
| 2 | consensus | f1 | `p3a-minimal-text-t1.0` | `p3a-high-image-t0.0` | 0.0000 | 0 | Y |
| 2 | consensus | f1 | `p3a-minimal-text-t1.0-n5` | `p3a-minimal-text-t0.0` | 0.0001 | 1 |  |
| 2 | consensus | f1 | `p3a-minimal-text-t1.0-n5` | `h11-n1-brief-text-t03` | 0.0002 | 2 |  |
| 2 | consensus | f1 | `p3a-minimal-text-t1.0-n5` | `h11-n1-pro-text-high-t0` | 0.0003 | 3 |  |
| 2 | consensus | f1 | `p3a-minimal-text-t1.0-n5` | `h11-n1-pro-image-high-t0` | 0.0002 | 2 |  |
| 2 | consensus | f1 | `p3a-minimal-text-t1.0-n5` | `p3a-high-image-t0.0` | 0.0000 | 0 | Y |
| 2 | consensus | f1 | `h11-pvd-flash-minimal-text-n30-t07` | `h11-n1-brief-text-t03` | 0.0004 | 4 |  |
| 2 | consensus | f1 | `h11-pvd-flash-minimal-text-n30-t07` | `h11-n1-pro-text-high-t0` | 0.0001 | 1 |  |
| 2 | consensus | f1 | `h11-pvd-flash-minimal-text-n30-t07` | `h11-n1-pro-image-high-t0` | 0.0001 | 1 |  |
| 2 | consensus | f1 | `h11-pvd-flash-minimal-text-n30-t07` | `p3a-high-image-t0.0` | 0.0000 | 0 | Y |
| 2 | consensus | f1 | `p3a-min-image-t0.3` | `h11-n1-pro-text-high-t0` | 0.0004 | 4 |  |
| 2 | consensus | f1 | `p3a-min-image-t0.3` | `h11-n1-pro-image-high-t0` | 0.0000 | 0 | Y |
| 2 | consensus | f1 | `p3a-min-image-t0.3` | `p3a-high-image-t0.0` | 0.0000 | 0 | Y |
| 2 | consensus | f1 | `p3a-min-image-t1.0` | `p3a-high-image-t0.0` | 0.0000 | 0 | Y |
| 2 | consensus | f1 | `p3a-minimal-text-t0.3` | `p3a-high-image-t0.0` | 0.0000 | 0 | Y |
| 2 | consensus | f1 | `p3a-minimal-text-t0.3-n5` | `p3a-high-image-t0.0` | 0.0000 | 0 | Y |
| 2 | consensus | f1 | `h11-n1-image-t0` | `p3a-high-image-t0.0` | 0.0000 | 0 | Y |
| 2 | consensus | f1 | `h11-pvd-text-n10` | `p3a-high-image-t0.0` | 0.0000 | 0 | Y |
| 2 | consensus | f1 | `p3a-high-text-t0.0` | `p3a-high-image-t0.0` | 0.0002 | 2 |  |
| 2 | consensus | mcc | `h11-pvd-pro-high-image-n5` | `p3a-high-image-t1.0` | 0.0000 | 0 | Y |
| 2 | consensus | mcc | `h11-pvd-pro-high-image-n5` | `p3a-high-text-t0.3` | 0.0000 | 0 | Y |
| 2 | consensus | mcc | `h11-pvd-pro-high-image-n5` | `p3a-high-text-t0.3-n5` | 0.0000 | 0 | Y |
| 2 | consensus | mcc | `h11-pvd-pro-high-image-n5` | `h11-pvd-flash-high-text-n5` | 0.0000 | 0 | Y |
| 2 | consensus | mcc | `h11-pvd-pro-high-image-n5` | `p3a-high-text-t1.0-n5` | 0.0000 | 0 | Y |
| 2 | consensus | mcc | `h11-pvd-pro-high-image-n5` | `p3a-high-text-t1.0` | 0.0000 | 0 | Y |
| 2 | consensus | mcc | `h11-pvd-pro-high-image-n5` | `h11-n1-pro-image-high-t0` | 0.0000 | 0 | Y |
| 2 | consensus | mcc | `h11-pvd-pro-high-image-n5` | `p3a-high-image-t0.0` | 0.0000 | 0 | Y |
| 2 | consensus | mcc | `h11-pvd-pro-high-image-n5` | `p3a-high-text-t0.0` | 0.0000 | 0 | Y |
| 2 | consensus | mcc | `h11-pvd-pro-high-image-n5` | `p3a-min-image-t1.0` | 0.0000 | 0 | Y |
| 2 | consensus | mcc | `h11-pvd-pro-high-image-n5` | `h11-e47-propose-brief` | 0.0000 | 0 | Y |
| 2 | consensus | mcc | `h11-pvd-pro-high-image-n5` | `p3a-minimal-text-t1.0` | 0.0000 | 0 | Y |
| 2 | consensus | mcc | `h11-pvd-pro-high-image-n5` | `p3a-minimal-text-t1.0-n5` | 0.0000 | 0 | Y |
| 2 | consensus | mcc | `h11-pvd-pro-high-image-n5` | `h11-pvd-image-n5` | 0.0000 | 0 | Y |
| 2 | consensus | mcc | `h11-pvd-pro-high-image-n5` | `h11-n1-pro-text-high-t0` | 0.0000 | 0 | Y |
| 2 | consensus | mcc | `h11-pvd-pro-high-image-n5` | `h11-n1-image-t03` | 0.0000 | 0 | Y |
| 2 | consensus | mcc | `h11-pvd-pro-high-image-n5` | `p3a-min-image-t0.3` | 0.0000 | 0 | Y |
| 2 | consensus | mcc | `h11-pvd-pro-high-image-n5` | `h11-pvd-flash-minimal-text-n30-t07` | 0.0000 | 0 | Y |
| 2 | consensus | mcc | `h11-pvd-pro-high-image-n5` | `h11-pvd-text-n10` | 0.0000 | 0 | Y |
| 2 | consensus | mcc | `h11-pvd-pro-high-image-n5` | `p3a-minimal-text-t0.3` | 0.0000 | 0 | Y |
| 2 | consensus | mcc | `h11-pvd-pro-high-image-n5` | `p3a-minimal-text-t0.3-n5` | 0.0000 | 0 | Y |
| 2 | consensus | mcc | `h11-pvd-pro-high-image-n5` | `p3a-minimal-text-t0.0` | 0.0000 | 0 | Y |
| 2 | consensus | mcc | `h11-pvd-pro-high-image-n5` | `h11-n1-image-t0` | 0.0000 | 0 | Y |
| 2 | consensus | mcc | `h11-pvd-pro-high-image-n5` | `h11-n1-brief-text-t03` | 0.0000 | 0 | Y |
| 2 | consensus | mcc | `scale4-optimal-487` | `p3a-high-image-t1.0` | 0.0000 | 0 | Y |
| 2 | consensus | mcc | `scale4-optimal-487` | `p3a-high-text-t0.3` | 0.0000 | 0 | Y |
| 2 | consensus | mcc | `scale4-optimal-487` | `h11-pvd-flash-high-text-n5` | 0.0000 | 0 | Y |
| 2 | consensus | mcc | `scale4-optimal-487` | `p3a-high-text-t1.0` | 0.0000 | 0 | Y |
| 2 | consensus | mcc | `scale4-optimal-487` | `p3a-high-text-t0.3-n5` | 0.0000 | 0 | Y |
| 2 | consensus | mcc | `scale4-optimal-487` | `p3a-high-text-t1.0-n5` | 0.0000 | 0 | Y |
| 2 | consensus | mcc | `scale4-optimal-487` | `h11-e47-propose-brief` | 0.0000 | 0 | Y |
| 2 | consensus | mcc | `scale4-optimal-487` | `h11-n1-pro-image-high-t0` | 0.0000 | 0 | Y |
| 2 | consensus | mcc | `scale4-optimal-487` | `p3a-high-image-t0.0` | 0.0000 | 0 | Y |
| 2 | consensus | mcc | `scale4-optimal-487` | `p3a-high-text-t0.0` | 0.0000 | 0 | Y |
| 2 | consensus | mcc | `scale4-optimal-487` | `p3a-min-image-t1.0` | 0.0000 | 0 | Y |
| 2 | consensus | mcc | `scale4-optimal-487` | `p3a-minimal-text-t1.0` | 0.0000 | 0 | Y |
| 2 | consensus | mcc | `scale4-optimal-487` | `h11-pvd-image-n5` | 0.0000 | 0 | Y |
| 2 | consensus | mcc | `scale4-optimal-487` | `p3a-minimal-text-t1.0-n5` | 0.0000 | 0 | Y |
| 2 | consensus | mcc | `scale4-optimal-487` | `h11-n1-pro-text-high-t0` | 0.0000 | 0 | Y |
| 2 | consensus | mcc | `scale4-optimal-487` | `h11-pvd-flash-minimal-text-n30-t07` | 0.0000 | 0 | Y |
| 2 | consensus | mcc | `scale4-optimal-487` | `h11-n1-image-t03` | 0.0000 | 0 | Y |
| 2 | consensus | mcc | `scale4-optimal-487` | `h11-pvd-text-n10` | 0.0000 | 0 | Y |
| 2 | consensus | mcc | `scale4-optimal-487` | `p3a-min-image-t0.3` | 0.0000 | 0 | Y |
| 2 | consensus | mcc | `scale4-optimal-487` | `p3a-minimal-text-t0.3` | 0.0000 | 0 | Y |
| 2 | consensus | mcc | `scale4-optimal-487` | `p3a-minimal-text-t0.3-n5` | 0.0000 | 0 | Y |
| 2 | consensus | mcc | `scale4-optimal-487` | `p3a-minimal-text-t0.0` | 0.0000 | 0 | Y |
| 2 | consensus | mcc | `scale4-optimal-487` | `h11-n1-image-t0` | 0.0000 | 0 | Y |
| 2 | consensus | mcc | `scale4-optimal-487` | `h11-n1-brief-text-t03` | 0.0000 | 0 | Y |
| 2 | consensus | mcc | `h11-pvd-pro-high-text-n5` | `p3a-high-text-t0.3` | 0.0000 | 0 | Y |
| 2 | consensus | mcc | `h11-pvd-pro-high-text-n5` | `p3a-high-text-t0.3-n5` | 0.0000 | 0 | Y |
| 2 | consensus | mcc | `h11-pvd-pro-high-text-n5` | `p3a-high-text-t1.0` | 0.0000 | 0 | Y |
| 2 | consensus | mcc | `h11-pvd-pro-high-text-n5` | `p3a-high-text-t1.0-n5` | 0.0000 | 0 | Y |
| 2 | consensus | mcc | `h11-pvd-pro-high-text-n5` | `h11-n1-pro-image-high-t0` | 0.0001 | 1 |  |
| 2 | consensus | mcc | `h11-pvd-pro-high-text-n5` | `h11-e47-propose-brief` | 0.0000 | 0 | Y |
| 2 | consensus | mcc | `h11-pvd-pro-high-text-n5` | `p3a-high-image-t0.0` | 0.0000 | 0 | Y |
| 2 | consensus | mcc | `h11-pvd-pro-high-text-n5` | `p3a-high-text-t0.0` | 0.0000 | 0 | Y |
| 2 | consensus | mcc | `h11-pvd-pro-high-text-n5` | `p3a-min-image-t1.0` | 0.0000 | 0 | Y |
| 2 | consensus | mcc | `h11-pvd-pro-high-text-n5` | `p3a-minimal-text-t1.0` | 0.0000 | 0 | Y |
| 2 | consensus | mcc | `h11-pvd-pro-high-text-n5` | `p3a-minimal-text-t1.0-n5` | 0.0000 | 0 | Y |
| 2 | consensus | mcc | `h11-pvd-pro-high-text-n5` | `h11-pvd-image-n5` | 0.0000 | 0 | Y |
| 2 | consensus | mcc | `h11-pvd-pro-high-text-n5` | `h11-n1-pro-text-high-t0` | 0.0000 | 0 | Y |
| 2 | consensus | mcc | `h11-pvd-pro-high-text-n5` | `h11-pvd-flash-minimal-text-n30-t07` | 0.0000 | 0 | Y |
| 2 | consensus | mcc | `h11-pvd-pro-high-text-n5` | `p3a-min-image-t0.3` | 0.0000 | 0 | Y |
| 2 | consensus | mcc | `h11-pvd-pro-high-text-n5` | `h11-n1-image-t03` | 0.0000 | 0 | Y |
| 2 | consensus | mcc | `h11-pvd-pro-high-text-n5` | `h11-pvd-text-n10` | 0.0000 | 0 | Y |
| 2 | consensus | mcc | `h11-pvd-pro-high-text-n5` | `p3a-minimal-text-t0.3` | 0.0000 | 0 | Y |
| 2 | consensus | mcc | `h11-pvd-pro-high-text-n5` | `p3a-minimal-text-t0.3-n5` | 0.0000 | 0 | Y |
| 2 | consensus | mcc | `h11-pvd-pro-high-text-n5` | `p3a-minimal-text-t0.0` | 0.0000 | 0 | Y |
| 2 | consensus | mcc | `h11-pvd-pro-high-text-n5` | `h11-n1-image-t0` | 0.0000 | 0 | Y |
| 2 | consensus | mcc | `h11-pvd-pro-high-text-n5` | `h11-n1-brief-text-t03` | 0.0000 | 0 | Y |
| 2 | consensus | mcc | `p3a-high-image-t0.3` | `h11-e47-propose-brief` | 0.0000 | 0 | Y |
| 2 | consensus | mcc | `p3a-high-image-t0.3` | `p3a-high-image-t0.0` | 0.0000 | 0 | Y |
| 2 | consensus | mcc | `p3a-high-image-t0.3` | `p3a-min-image-t1.0` | 0.0000 | 0 | Y |
| 2 | consensus | mcc | `p3a-high-image-t0.3` | `p3a-high-text-t0.0` | 0.0000 | 0 | Y |
| 2 | consensus | mcc | `p3a-high-image-t0.3` | `p3a-minimal-text-t1.0` | 0.0000 | 0 | Y |
| 2 | consensus | mcc | `p3a-high-image-t0.3` | `p3a-minimal-text-t1.0-n5` | 0.0000 | 0 | Y |
| 2 | consensus | mcc | `p3a-high-image-t0.3` | `h11-pvd-image-n5` | 0.0000 | 0 | Y |
| 2 | consensus | mcc | `p3a-high-image-t0.3` | `h11-pvd-flash-minimal-text-n30-t07` | 0.0000 | 0 | Y |
| 2 | consensus | mcc | `p3a-high-image-t0.3` | `h11-n1-pro-text-high-t0` | 0.0000 | 0 | Y |
| 2 | consensus | mcc | `p3a-high-image-t0.3` | `h11-n1-image-t03` | 0.0000 | 0 | Y |
| 2 | consensus | mcc | `p3a-high-image-t0.3` | `p3a-min-image-t0.3` | 0.0000 | 0 | Y |
| 2 | consensus | mcc | `p3a-high-image-t0.3` | `h11-pvd-text-n10` | 0.0000 | 0 | Y |
| 2 | consensus | mcc | `p3a-high-image-t0.3` | `p3a-minimal-text-t0.3` | 0.0000 | 0 | Y |
| 2 | consensus | mcc | `p3a-high-image-t0.3` | `p3a-minimal-text-t0.3-n5` | 0.0000 | 0 | Y |
| 2 | consensus | mcc | `p3a-high-image-t0.3` | `p3a-minimal-text-t0.0` | 0.0000 | 0 | Y |
| 2 | consensus | mcc | `p3a-high-image-t0.3` | `h11-n1-image-t0` | 0.0000 | 0 | Y |
| 2 | consensus | mcc | `p3a-high-image-t0.3` | `h11-n1-brief-text-t03` | 0.0000 | 0 | Y |
| 2 | consensus | mcc | `h11-pvd-flash-high-image-n5` | `h11-e47-propose-brief` | 0.0000 | 0 | Y |
| 2 | consensus | mcc | `h11-pvd-flash-high-image-n5` | `p3a-high-image-t0.0` | 0.0000 | 0 | Y |
| 2 | consensus | mcc | `h11-pvd-flash-high-image-n5` | `p3a-high-text-t0.0` | 0.0000 | 0 | Y |
| 2 | consensus | mcc | `h11-pvd-flash-high-image-n5` | `p3a-min-image-t1.0` | 0.0000 | 0 | Y |
| 2 | consensus | mcc | `h11-pvd-flash-high-image-n5` | `p3a-minimal-text-t1.0` | 0.0000 | 0 | Y |
| 2 | consensus | mcc | `h11-pvd-flash-high-image-n5` | `p3a-minimal-text-t1.0-n5` | 0.0000 | 0 | Y |
| 2 | consensus | mcc | `h11-pvd-flash-high-image-n5` | `h11-pvd-image-n5` | 0.0000 | 0 | Y |
| 2 | consensus | mcc | `h11-pvd-flash-high-image-n5` | `h11-n1-pro-text-high-t0` | 0.0000 | 0 | Y |
| 2 | consensus | mcc | `h11-pvd-flash-high-image-n5` | `h11-pvd-flash-minimal-text-n30-t07` | 0.0000 | 0 | Y |
| 2 | consensus | mcc | `h11-pvd-flash-high-image-n5` | `p3a-min-image-t0.3` | 0.0000 | 0 | Y |
| 2 | consensus | mcc | `h11-pvd-flash-high-image-n5` | `h11-n1-image-t03` | 0.0000 | 0 | Y |
| 2 | consensus | mcc | `h11-pvd-flash-high-image-n5` | `h11-pvd-text-n10` | 0.0000 | 0 | Y |
| 2 | consensus | mcc | `h11-pvd-flash-high-image-n5` | `p3a-minimal-text-t0.3` | 0.0000 | 0 | Y |
| 2 | consensus | mcc | `h11-pvd-flash-high-image-n5` | `p3a-minimal-text-t0.3-n5` | 0.0000 | 0 | Y |
| 2 | consensus | mcc | `h11-pvd-flash-high-image-n5` | `p3a-minimal-text-t0.0` | 0.0000 | 0 | Y |
| 2 | consensus | mcc | `h11-pvd-flash-high-image-n5` | `h11-n1-image-t0` | 0.0000 | 0 | Y |
| 2 | consensus | mcc | `h11-pvd-flash-high-image-n5` | `h11-n1-brief-text-t03` | 0.0000 | 0 | Y |
| 2 | consensus | mcc | `p3a-high-image-t1.0` | `p3a-high-image-t0.0` | 0.0005 | 5 |  |
| 2 | consensus | mcc | `p3a-high-image-t1.0` | `p3a-high-text-t0.0` | 0.0000 | 0 | Y |
| 2 | consensus | mcc | `p3a-high-image-t1.0` | `p3a-minimal-text-t1.0` | 0.0000 | 0 | Y |
| 2 | consensus | mcc | `p3a-high-image-t1.0` | `p3a-min-image-t1.0` | 0.0000 | 0 | Y |
| 2 | consensus | mcc | `p3a-high-image-t1.0` | `p3a-minimal-text-t1.0-n5` | 0.0000 | 0 | Y |
| 2 | consensus | mcc | `p3a-high-image-t1.0` | `h11-pvd-image-n5` | 0.0000 | 0 | Y |
| 2 | consensus | mcc | `p3a-high-image-t1.0` | `h11-n1-pro-text-high-t0` | 0.0000 | 0 | Y |
| 2 | consensus | mcc | `p3a-high-image-t1.0` | `h11-pvd-flash-minimal-text-n30-t07` | 0.0000 | 0 | Y |
| 2 | consensus | mcc | `p3a-high-image-t1.0` | `h11-n1-image-t03` | 0.0000 | 0 | Y |
| 2 | consensus | mcc | `p3a-high-image-t1.0` | `p3a-min-image-t0.3` | 0.0000 | 0 | Y |
| 2 | consensus | mcc | `p3a-high-image-t1.0` | `h11-pvd-text-n10` | 0.0000 | 0 | Y |
| 2 | consensus | mcc | `p3a-high-image-t1.0` | `p3a-minimal-text-t0.3` | 0.0000 | 0 | Y |
| 2 | consensus | mcc | `p3a-high-image-t1.0` | `p3a-minimal-text-t0.3-n5` | 0.0000 | 0 | Y |
| 2 | consensus | mcc | `p3a-high-image-t1.0` | `p3a-minimal-text-t0.0` | 0.0000 | 0 | Y |
| 2 | consensus | mcc | `p3a-high-image-t1.0` | `h11-n1-image-t0` | 0.0000 | 0 | Y |
| 2 | consensus | mcc | `p3a-high-image-t1.0` | `h11-n1-brief-text-t03` | 0.0000 | 0 | Y |
| 2 | consensus | mcc | `h11-pvd-flash-high-text-n5` | `p3a-high-text-t0.0` | 0.0000 | 0 | Y |
| 2 | consensus | mcc | `h11-pvd-flash-high-text-n5` | `p3a-min-image-t1.0` | 0.0000 | 0 | Y |
| 2 | consensus | mcc | `h11-pvd-flash-high-text-n5` | `p3a-minimal-text-t1.0` | 0.0000 | 0 | Y |
| 2 | consensus | mcc | `h11-pvd-flash-high-text-n5` | `p3a-minimal-text-t1.0-n5` | 0.0000 | 0 | Y |
| 2 | consensus | mcc | `h11-pvd-flash-high-text-n5` | `h11-pvd-image-n5` | 0.0000 | 0 | Y |
| 2 | consensus | mcc | `h11-pvd-flash-high-text-n5` | `h11-n1-pro-text-high-t0` | 0.0000 | 0 | Y |
| 2 | consensus | mcc | `h11-pvd-flash-high-text-n5` | `h11-pvd-flash-minimal-text-n30-t07` | 0.0000 | 0 | Y |
| 2 | consensus | mcc | `h11-pvd-flash-high-text-n5` | `h11-n1-image-t03` | 0.0000 | 0 | Y |
| 2 | consensus | mcc | `h11-pvd-flash-high-text-n5` | `p3a-min-image-t0.3` | 0.0000 | 0 | Y |
| 2 | consensus | mcc | `h11-pvd-flash-high-text-n5` | `h11-pvd-text-n10` | 0.0000 | 0 | Y |
| 2 | consensus | mcc | `h11-pvd-flash-high-text-n5` | `p3a-minimal-text-t0.3` | 0.0000 | 0 | Y |
| 2 | consensus | mcc | `h11-pvd-flash-high-text-n5` | `p3a-minimal-text-t0.3-n5` | 0.0000 | 0 | Y |
| 2 | consensus | mcc | `h11-pvd-flash-high-text-n5` | `p3a-minimal-text-t0.0` | 0.0000 | 0 | Y |
| 2 | consensus | mcc | `h11-pvd-flash-high-text-n5` | `h11-n1-image-t0` | 0.0000 | 0 | Y |
| 2 | consensus | mcc | `h11-pvd-flash-high-text-n5` | `h11-n1-brief-text-t03` | 0.0000 | 0 | Y |
| 2 | consensus | mcc | `p3a-high-text-t0.3` | `p3a-minimal-text-t1.0` | 0.0001 | 1 |  |
| 2 | consensus | mcc | `p3a-high-text-t0.3` | `p3a-minimal-text-t1.0-n5` | 0.0001 | 1 |  |
| 2 | consensus | mcc | `p3a-high-text-t0.3` | `h11-pvd-image-n5` | 0.0000 | 0 | Y |
| 2 | consensus | mcc | `p3a-high-text-t0.3` | `h11-n1-pro-text-high-t0` | 0.0001 | 1 |  |
| 2 | consensus | mcc | `p3a-high-text-t0.3` | `h11-n1-image-t03` | 0.0000 | 0 | Y |
| 2 | consensus | mcc | `p3a-high-text-t0.3` | `h11-pvd-flash-minimal-text-n30-t07` | 0.0000 | 0 | Y |
| 2 | consensus | mcc | `p3a-high-text-t0.3` | `p3a-min-image-t0.3` | 0.0000 | 0 | Y |
| 2 | consensus | mcc | `p3a-high-text-t0.3` | `h11-pvd-text-n10` | 0.0000 | 0 | Y |
| 2 | consensus | mcc | `p3a-high-text-t0.3` | `p3a-minimal-text-t0.3` | 0.0000 | 0 | Y |
| 2 | consensus | mcc | `p3a-high-text-t0.3` | `p3a-minimal-text-t0.3-n5` | 0.0000 | 0 | Y |
| 2 | consensus | mcc | `p3a-high-text-t0.3` | `p3a-minimal-text-t0.0` | 0.0000 | 0 | Y |
| 2 | consensus | mcc | `p3a-high-text-t0.3` | `h11-n1-image-t0` | 0.0000 | 0 | Y |
| 2 | consensus | mcc | `p3a-high-text-t0.3` | `h11-n1-brief-text-t03` | 0.0000 | 0 | Y |
| 2 | consensus | mcc | `p3a-high-text-t0.3-n5` | `p3a-minimal-text-t1.0` | 0.0001 | 1 |  |
| 2 | consensus | mcc | `p3a-high-text-t0.3-n5` | `p3a-minimal-text-t1.0-n5` | 0.0001 | 1 |  |
| 2 | consensus | mcc | `p3a-high-text-t0.3-n5` | `h11-pvd-image-n5` | 0.0000 | 0 | Y |
| 2 | consensus | mcc | `p3a-high-text-t0.3-n5` | `h11-n1-pro-text-high-t0` | 0.0001 | 1 |  |
| 2 | consensus | mcc | `p3a-high-text-t0.3-n5` | `h11-pvd-flash-minimal-text-n30-t07` | 0.0000 | 0 | Y |
| 2 | consensus | mcc | `p3a-high-text-t0.3-n5` | `h11-n1-image-t03` | 0.0000 | 0 | Y |
| 2 | consensus | mcc | `p3a-high-text-t0.3-n5` | `p3a-min-image-t0.3` | 0.0000 | 0 | Y |
| 2 | consensus | mcc | `p3a-high-text-t0.3-n5` | `h11-pvd-text-n10` | 0.0000 | 0 | Y |
| 2 | consensus | mcc | `p3a-high-text-t0.3-n5` | `p3a-minimal-text-t0.3` | 0.0000 | 0 | Y |
| 2 | consensus | mcc | `p3a-high-text-t0.3-n5` | `p3a-minimal-text-t0.3-n5` | 0.0000 | 0 | Y |
| 2 | consensus | mcc | `p3a-high-text-t0.3-n5` | `p3a-minimal-text-t0.0` | 0.0000 | 0 | Y |
| 2 | consensus | mcc | `p3a-high-text-t0.3-n5` | `h11-n1-image-t0` | 0.0000 | 0 | Y |
| 2 | consensus | mcc | `p3a-high-text-t0.3-n5` | `h11-n1-brief-text-t03` | 0.0000 | 0 | Y |
| 2 | consensus | mcc | `p3a-high-text-t1.0` | `h11-pvd-image-n5` | 0.0002 | 2 |  |
| 2 | consensus | mcc | `p3a-high-text-t1.0` | `h11-n1-pro-text-high-t0` | 0.0001 | 1 |  |
| 2 | consensus | mcc | `p3a-high-text-t1.0` | `h11-pvd-flash-minimal-text-n30-t07` | 0.0000 | 0 | Y |
| 2 | consensus | mcc | `p3a-high-text-t1.0` | `h11-n1-image-t03` | 0.0000 | 0 | Y |
| 2 | consensus | mcc | `p3a-high-text-t1.0` | `p3a-min-image-t0.3` | 0.0000 | 0 | Y |
| 2 | consensus | mcc | `p3a-high-text-t1.0` | `h11-pvd-text-n10` | 0.0000 | 0 | Y |
| 2 | consensus | mcc | `p3a-high-text-t1.0` | `p3a-minimal-text-t0.3` | 0.0000 | 0 | Y |
| 2 | consensus | mcc | `p3a-high-text-t1.0` | `p3a-minimal-text-t0.3-n5` | 0.0000 | 0 | Y |
| 2 | consensus | mcc | `p3a-high-text-t1.0` | `p3a-minimal-text-t0.0` | 0.0000 | 0 | Y |
| 2 | consensus | mcc | `p3a-high-text-t1.0` | `h11-n1-brief-text-t03` | 0.0000 | 0 | Y |
| 2 | consensus | mcc | `p3a-high-text-t1.0` | `h11-n1-image-t0` | 0.0000 | 0 | Y |
| 2 | consensus | mcc | `p3a-high-text-t1.0-n5` | `h11-pvd-image-n5` | 0.0002 | 2 |  |
| 2 | consensus | mcc | `p3a-high-text-t1.0-n5` | `h11-n1-pro-text-high-t0` | 0.0001 | 1 |  |
| 2 | consensus | mcc | `p3a-high-text-t1.0-n5` | `h11-pvd-flash-minimal-text-n30-t07` | 0.0000 | 0 | Y |
| 2 | consensus | mcc | `p3a-high-text-t1.0-n5` | `h11-n1-image-t03` | 0.0000 | 0 | Y |
| 2 | consensus | mcc | `p3a-high-text-t1.0-n5` | `p3a-min-image-t0.3` | 0.0000 | 0 | Y |
| 2 | consensus | mcc | `p3a-high-text-t1.0-n5` | `h11-pvd-text-n10` | 0.0000 | 0 | Y |
| 2 | consensus | mcc | `p3a-high-text-t1.0-n5` | `p3a-minimal-text-t0.3` | 0.0000 | 0 | Y |
| 2 | consensus | mcc | `p3a-high-text-t1.0-n5` | `p3a-minimal-text-t0.3-n5` | 0.0000 | 0 | Y |
| 2 | consensus | mcc | `p3a-high-text-t1.0-n5` | `p3a-minimal-text-t0.0` | 0.0000 | 0 | Y |
| 2 | consensus | mcc | `p3a-high-text-t1.0-n5` | `h11-n1-brief-text-t03` | 0.0000 | 0 | Y |
| 2 | consensus | mcc | `p3a-high-text-t1.0-n5` | `h11-n1-image-t0` | 0.0000 | 0 | Y |
| 2 | consensus | mcc | `h11-n1-pro-image-high-t0` | `h11-pvd-image-n5` | 0.0005 | 5 |  |
| 2 | consensus | mcc | `h11-n1-pro-image-high-t0` | `h11-n1-pro-text-high-t0` | 0.0001 | 1 |  |
| 2 | consensus | mcc | `h11-n1-pro-image-high-t0` | `h11-pvd-flash-minimal-text-n30-t07` | 0.0001 | 1 |  |
| 2 | consensus | mcc | `h11-n1-pro-image-high-t0` | `h11-n1-image-t03` | 0.0000 | 0 | Y |
| 2 | consensus | mcc | `h11-n1-pro-image-high-t0` | `p3a-min-image-t0.3` | 0.0000 | 0 | Y |
| 2 | consensus | mcc | `h11-n1-pro-image-high-t0` | `h11-pvd-text-n10` | 0.0000 | 0 | Y |
| 2 | consensus | mcc | `h11-n1-pro-image-high-t0` | `p3a-minimal-text-t0.3` | 0.0000 | 0 | Y |
| 2 | consensus | mcc | `h11-n1-pro-image-high-t0` | `p3a-minimal-text-t0.3-n5` | 0.0000 | 0 | Y |
| 2 | consensus | mcc | `h11-n1-pro-image-high-t0` | `p3a-minimal-text-t0.0` | 0.0000 | 0 | Y |
| 2 | consensus | mcc | `h11-n1-pro-image-high-t0` | `h11-n1-image-t0` | 0.0000 | 0 | Y |
| 2 | consensus | mcc | `h11-n1-pro-image-high-t0` | `h11-n1-brief-text-t03` | 0.0000 | 0 | Y |
| 2 | consensus | mcc | `h11-e47-propose-brief` | `p3a-min-image-t0.3` | 0.0001 | 1 |  |
| 2 | consensus | mcc | `h11-e47-propose-brief` | `h11-pvd-text-n10` | 0.0000 | 0 | Y |
| 2 | consensus | mcc | `h11-e47-propose-brief` | `p3a-minimal-text-t0.3-n5` | 0.0001 | 1 |  |
| 2 | consensus | mcc | `h11-e47-propose-brief` | `p3a-minimal-text-t0.3` | 0.0001 | 1 |  |
| 2 | consensus | mcc | `h11-e47-propose-brief` | `p3a-minimal-text-t0.0` | 0.0000 | 0 | Y |
| 2 | consensus | mcc | `h11-e47-propose-brief` | `h11-n1-image-t0` | 0.0000 | 0 | Y |
| 2 | consensus | mcc | `h11-e47-propose-brief` | `h11-n1-brief-text-t03` | 0.0000 | 0 | Y |
| 2 | consensus | mcc | `p3a-high-image-t0.0` | `p3a-minimal-text-t0.3` | 0.0001 | 1 |  |
| 2 | consensus | mcc | `p3a-high-image-t0.0` | `p3a-minimal-text-t0.3-n5` | 0.0001 | 1 |  |
| 2 | consensus | mcc | `p3a-high-image-t0.0` | `h11-n1-image-t0` | 0.0000 | 0 | Y |
| 2 | consensus | mcc | `p3a-high-image-t0.0` | `p3a-minimal-text-t0.0` | 0.0000 | 0 | Y |
| 2 | consensus | mcc | `p3a-high-image-t0.0` | `h11-n1-brief-text-t03` | 0.0000 | 0 | Y |
| 2 | consensus | mcc | `p3a-high-text-t0.0` | `p3a-minimal-text-t0.0` | 0.0000 | 0 | Y |
| 2 | consensus | mcc | `p3a-high-text-t0.0` | `h11-n1-image-t0` | 0.0000 | 0 | Y |
| 2 | consensus | mcc | `p3a-high-text-t0.0` | `h11-n1-brief-text-t03` | 0.0000 | 0 | Y |
| 2 | consensus | mcc | `p3a-min-image-t1.0` | `h11-n1-image-t0` | 0.0000 | 0 | Y |
| 2 | consensus | mcc | `p3a-min-image-t1.0` | `p3a-minimal-text-t0.0` | 0.0000 | 0 | Y |
| 2 | consensus | mcc | `p3a-min-image-t1.0` | `h11-n1-brief-text-t03` | 0.0000 | 0 | Y |
| 2 | consensus | mcc | `p3a-minimal-text-t1.0` | `p3a-minimal-text-t0.0` | 0.0000 | 0 | Y |
| 2 | consensus | mcc | `p3a-minimal-text-t1.0` | `h11-n1-image-t0` | 0.0000 | 0 | Y |
| 2 | consensus | mcc | `p3a-minimal-text-t1.0` | `h11-n1-brief-text-t03` | 0.0000 | 0 | Y |
| 2 | consensus | mcc | `p3a-minimal-text-t1.0-n5` | `p3a-minimal-text-t0.0` | 0.0000 | 0 | Y |
| 2 | consensus | mcc | `p3a-minimal-text-t1.0-n5` | `h11-n1-image-t0` | 0.0000 | 0 | Y |
| 2 | consensus | mcc | `p3a-minimal-text-t1.0-n5` | `h11-n1-brief-text-t03` | 0.0000 | 0 | Y |
| 2 | consensus | mcc | `h11-pvd-image-n5` | `p3a-minimal-text-t0.0` | 0.0000 | 0 | Y |
| 2 | consensus | mcc | `h11-pvd-image-n5` | `h11-n1-image-t0` | 0.0000 | 0 | Y |
| 2 | consensus | mcc | `h11-pvd-image-n5` | `h11-n1-brief-text-t03` | 0.0000 | 0 | Y |
| 2 | consensus | mcc | `h11-n1-pro-text-high-t0` | `p3a-minimal-text-t0.0` | 0.0000 | 0 | Y |
| 2 | consensus | mcc | `h11-n1-pro-text-high-t0` | `h11-n1-image-t0` | 0.0000 | 0 | Y |
| 2 | consensus | mcc | `h11-n1-pro-text-high-t0` | `h11-n1-brief-text-t03` | 0.0000 | 0 | Y |
| 2 | consensus | mcc | `h11-pvd-flash-minimal-text-n30-t07` | `p3a-minimal-text-t0.0` | 0.0005 | 5 |  |
| 2 | consensus | mcc | `h11-pvd-flash-minimal-text-n30-t07` | `h11-n1-image-t0` | 0.0004 | 4 |  |
| 2 | consensus | mcc | `h11-pvd-flash-minimal-text-n30-t07` | `h11-n1-brief-text-t03` | 0.0000 | 0 | Y |
| 2 | consensus | mcc | `h11-n1-image-t03` | `h11-n1-image-t0` | 0.0000 | 0 | Y |
| 2 | consensus | mcc | `h11-n1-image-t03` | `h11-n1-brief-text-t03` | 0.0003 | 3 |  |
| 2 | consensus | mcc | `p3a-min-image-t0.3` | `h11-n1-brief-text-t03` | 0.0004 | 4 |  |
| 2 | consensus | mcc | `h11-pvd-text-n10` | `h11-n1-brief-text-t03` | 0.0000 | 0 | Y |
| 2 | consensus | mcc | `p3a-minimal-text-t0.3` | `h11-n1-brief-text-t03` | 0.0003 | 3 |  |
| 2 | consensus | mcc | `p3a-minimal-text-t0.3-n5` | `h11-n1-brief-text-t03` | 0.0003 | 3 |  |
| 2 | single-pass+PV | mcc | `pv-cascade-adversarial-checklist` | `pv-brief-image` | 0.0003 | 3 |  |
| 2 | single-pass+PV | mcc | `pv-cascade-adversarial-checklist` | `pv-checklist-text` | 0.0000 | 0 | Y |
| 2 | single-pass+PV | mcc | `pv-adversarial-image` | `pv-checklist-text` | 0.0005 | 5 |  |
| 2 | pv | f1 | `pv-flash-high-text-16of30` | `pv-high-text-t0.0-n3` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `pv-flash-high-text-16of30` | `pv-min-image-t0.7-n10` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `pv-flash-high-text-16of30` | `pv-high-image-t0.7-n5` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `pv-flash-high-text-16of30` | `session-78-image-adversarial` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `pv-flash-high-text-16of30` | `session-78-image-comparative` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `pv-flash-high-text-16of30` | `session-78-image-checklist` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `pv-flash-high-text-16of30` | `pv-min-image-t0.3-n10` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `pv-flash-high-text-16of30` | `session-78-image-brief` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `pv-flash-high-text-16of30` | `pv-min-image-t0.3-n5` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `pv-flash-high-text-16of30` | `pv-high-image-t0.7-n10` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `pv-flash-high-text-16of30` | `session-78-image-checklist-text` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `pv-flash-high-text-16of30` | `pv-min-image-t0.7-n5` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `pv-flash-high-text-16of30` | `session-78-image-adversarial-text` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `pv-flash-high-text-16of30` | `session-78-image-brief-text` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `pv-flash-high-text-16of30` | `pv-high-image-t0.3-n10` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `pv-flash-high-text-16of30` | `pv-scale4-optimal-n10` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `pv-flash-high-text-16of30` | `pv-high-image-t0.3-n5` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `pv-flash-high-text-16of30` | `pv-n1-image-t0-n3` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `pv-flash-high-text-16of30` | `pv-high-image-t1.0-n10` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `pv-flash-high-text-16of30` | `pv-scale4-optimal-n5` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `pv-flash-high-text-16of30` | `pv-min-image-t1.0-n10` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `pv-flash-high-text-16of30` | `pv-min-image-t1.0-n5` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `pv-flash-high-text-16of30` | `pv-high-image-t1.0-n5` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `pv-high-text-t0.3-n5` | `pv-min-image-t0.7-n10` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `pv-high-text-t0.3-n5` | `pv-high-text-t0.0-n3` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `pv-high-text-t0.3-n5` | `pv-high-image-t0.7-n5` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `pv-high-text-t0.3-n5` | `session-78-image-adversarial` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `pv-high-text-t0.3-n5` | `session-78-image-brief` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `pv-high-text-t0.3-n5` | `session-78-image-comparative` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `pv-high-text-t0.3-n5` | `session-78-image-checklist` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `pv-high-text-t0.3-n5` | `pv-min-image-t0.3-n10` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `pv-high-text-t0.3-n5` | `session-78-image-checklist-text` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `pv-high-text-t0.3-n5` | `pv-min-image-t0.3-n5` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `pv-high-text-t0.3-n5` | `pv-high-image-t0.7-n10` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `pv-high-text-t0.3-n5` | `pv-min-image-t0.7-n5` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `pv-high-text-t0.3-n5` | `session-78-image-adversarial-text` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `pv-high-text-t0.3-n5` | `pv-high-image-t0.3-n10` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `pv-high-text-t0.3-n5` | `pv-scale4-optimal-n10` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `pv-high-text-t0.3-n5` | `session-78-image-brief-text` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `pv-high-text-t0.3-n5` | `pv-n1-image-t0-n3` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `pv-high-text-t0.3-n5` | `pv-high-image-t1.0-n10` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `pv-high-text-t0.3-n5` | `pv-scale4-optimal-n5` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `pv-high-text-t0.3-n5` | `pv-high-image-t0.3-n5` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `pv-high-text-t0.3-n5` | `pv-min-image-t1.0-n10` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `pv-high-text-t0.3-n5` | `pv-min-image-t1.0-n5` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `pv-high-text-t0.3-n5` | `pv-high-image-t1.0-n5` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `session-78-text-comparative` | `pv-high-text-t0.7-n5` | 0.0004 | 4 |  |
| 2 | pv | f1 | `session-78-text-comparative` | `session-78-text-adversarial-text` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `session-78-text-comparative` | `session-78-text-checklist-text` | 0.0001 | 1 |  |
| 2 | pv | f1 | `session-78-text-comparative` | `session-78-text-brief-text` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `session-78-text-comparative` | `pv-min-image-t0.7-n10` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `session-78-text-comparative` | `pv-high-image-t0.7-n5` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `session-78-text-comparative` | `session-78-image-adversarial` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `session-78-text-comparative` | `session-78-image-comparative` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `session-78-text-comparative` | `session-78-image-brief` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `session-78-text-comparative` | `session-78-image-checklist` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `session-78-text-comparative` | `pv-min-image-t0.3-n10` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `session-78-text-comparative` | `session-78-image-checklist-text` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `session-78-text-comparative` | `pv-min-image-t0.3-n5` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `session-78-text-comparative` | `pv-high-image-t0.7-n10` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `session-78-text-comparative` | `pv-min-image-t0.7-n5` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `session-78-text-comparative` | `session-78-image-adversarial-text` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `session-78-text-comparative` | `pv-high-image-t0.3-n10` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `session-78-text-comparative` | `pv-scale4-optimal-n10` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `session-78-text-comparative` | `session-78-image-brief-text` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `session-78-text-comparative` | `pv-n1-image-t0-n3` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `session-78-text-comparative` | `pv-high-image-t1.0-n10` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `session-78-text-comparative` | `pv-scale4-optimal-n5` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `session-78-text-comparative` | `pv-high-image-t0.3-n5` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `session-78-text-comparative` | `pv-min-image-t1.0-n10` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `session-78-text-comparative` | `pv-min-image-t1.0-n5` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `session-78-text-comparative` | `pv-high-image-t1.0-n5` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `session-78-text-adversarial` | `pv-high-text-t0.7-n5` | 0.0003 | 3 |  |
| 2 | pv | f1 | `session-78-text-adversarial` | `session-78-text-checklist-text` | 0.0002 | 2 |  |
| 2 | pv | f1 | `session-78-text-adversarial` | `session-78-text-adversarial-text` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `session-78-text-adversarial` | `session-78-text-brief-text` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `session-78-text-adversarial` | `pv-min-image-t0.7-n10` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `session-78-text-adversarial` | `pv-high-image-t0.7-n5` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `session-78-text-adversarial` | `session-78-image-adversarial` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `session-78-text-adversarial` | `session-78-image-comparative` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `session-78-text-adversarial` | `session-78-image-brief` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `session-78-text-adversarial` | `session-78-image-checklist` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `session-78-text-adversarial` | `pv-min-image-t0.3-n10` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `session-78-text-adversarial` | `session-78-image-checklist-text` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `session-78-text-adversarial` | `pv-high-image-t0.7-n10` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `session-78-text-adversarial` | `pv-min-image-t0.3-n5` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `session-78-text-adversarial` | `pv-min-image-t0.7-n5` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `session-78-text-adversarial` | `session-78-image-adversarial-text` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `session-78-text-adversarial` | `pv-high-image-t0.3-n10` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `session-78-text-adversarial` | `pv-scale4-optimal-n10` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `session-78-text-adversarial` | `session-78-image-brief-text` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `session-78-text-adversarial` | `pv-n1-image-t0-n3` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `session-78-text-adversarial` | `pv-high-image-t1.0-n10` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `session-78-text-adversarial` | `pv-scale4-optimal-n5` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `session-78-text-adversarial` | `pv-high-image-t0.3-n5` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `session-78-text-adversarial` | `pv-min-image-t1.0-n5` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `session-78-text-adversarial` | `pv-min-image-t1.0-n10` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `session-78-text-adversarial` | `pv-high-image-t1.0-n5` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `pv-high-text-t1.0-n10` | `pv-high-text-t0.0-n3` | 0.0004 | 4 |  |
| 2 | pv | f1 | `pv-high-text-t1.0-n10` | `pv-min-image-t0.7-n10` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `pv-high-text-t1.0-n10` | `pv-high-image-t0.7-n5` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `pv-high-text-t1.0-n10` | `session-78-image-adversarial` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `pv-high-text-t1.0-n10` | `session-78-image-comparative` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `pv-high-text-t1.0-n10` | `session-78-image-brief` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `pv-high-text-t1.0-n10` | `pv-min-image-t0.3-n10` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `pv-high-text-t1.0-n10` | `session-78-image-checklist` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `pv-high-text-t1.0-n10` | `session-78-image-checklist-text` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `pv-high-text-t1.0-n10` | `pv-min-image-t0.3-n5` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `pv-high-text-t1.0-n10` | `pv-high-image-t0.7-n10` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `pv-high-text-t1.0-n10` | `pv-min-image-t0.7-n5` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `pv-high-text-t1.0-n10` | `session-78-image-adversarial-text` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `pv-high-text-t1.0-n10` | `session-78-image-brief-text` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `pv-high-text-t1.0-n10` | `pv-scale4-optimal-n10` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `pv-high-text-t1.0-n10` | `pv-high-image-t0.3-n10` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `pv-high-text-t1.0-n10` | `pv-n1-image-t0-n3` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `pv-high-text-t1.0-n10` | `pv-high-image-t1.0-n10` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `pv-high-text-t1.0-n10` | `pv-scale4-optimal-n5` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `pv-high-text-t1.0-n10` | `pv-high-image-t0.3-n5` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `pv-high-text-t1.0-n10` | `pv-min-image-t1.0-n10` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `pv-high-text-t1.0-n10` | `pv-min-image-t1.0-n5` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `pv-high-text-t1.0-n10` | `pv-high-image-t1.0-n5` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `session-78-text-checklist` | `session-78-text-brief-text` | 0.0001 | 1 |  |
| 2 | pv | f1 | `session-78-text-checklist` | `pv-min-image-t0.7-n10` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `session-78-text-checklist` | `pv-high-image-t0.7-n5` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `session-78-text-checklist` | `session-78-image-adversarial` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `session-78-text-checklist` | `session-78-image-comparative` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `session-78-text-checklist` | `session-78-image-brief` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `session-78-text-checklist` | `session-78-image-checklist` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `session-78-text-checklist` | `pv-min-image-t0.3-n10` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `session-78-text-checklist` | `session-78-image-checklist-text` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `session-78-text-checklist` | `pv-min-image-t0.3-n5` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `session-78-text-checklist` | `pv-high-image-t0.7-n10` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `session-78-text-checklist` | `pv-min-image-t0.7-n5` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `session-78-text-checklist` | `session-78-image-adversarial-text` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `session-78-text-checklist` | `pv-high-image-t0.3-n10` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `session-78-text-checklist` | `pv-scale4-optimal-n10` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `session-78-text-checklist` | `session-78-image-brief-text` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `session-78-text-checklist` | `pv-n1-image-t0-n3` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `session-78-text-checklist` | `pv-high-image-t1.0-n10` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `session-78-text-checklist` | `pv-scale4-optimal-n5` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `session-78-text-checklist` | `pv-high-image-t0.3-n5` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `session-78-text-checklist` | `pv-min-image-t1.0-n10` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `session-78-text-checklist` | `pv-min-image-t1.0-n5` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `session-78-text-checklist` | `pv-high-image-t1.0-n5` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `pv-min-text-t0.3-n5` | `pv-min-image-t0.7-n10` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `pv-min-text-t0.3-n5` | `pv-high-image-t0.7-n5` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `pv-min-text-t0.3-n5` | `session-78-image-adversarial` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `pv-min-text-t0.3-n5` | `session-78-image-comparative` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `pv-min-text-t0.3-n5` | `session-78-image-brief` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `pv-min-text-t0.3-n5` | `session-78-image-checklist` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `pv-min-text-t0.3-n5` | `pv-min-image-t0.3-n10` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `pv-min-text-t0.3-n5` | `session-78-image-checklist-text` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `pv-min-text-t0.3-n5` | `pv-min-image-t0.3-n5` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `pv-min-text-t0.3-n5` | `pv-high-image-t0.7-n10` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `pv-min-text-t0.3-n5` | `pv-min-image-t0.7-n5` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `pv-min-text-t0.3-n5` | `session-78-image-adversarial-text` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `pv-min-text-t0.3-n5` | `pv-high-image-t0.3-n10` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `pv-min-text-t0.3-n5` | `pv-scale4-optimal-n10` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `pv-min-text-t0.3-n5` | `session-78-image-brief-text` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `pv-min-text-t0.3-n5` | `pv-n1-image-t0-n3` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `pv-min-text-t0.3-n5` | `pv-high-image-t1.0-n10` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `pv-min-text-t0.3-n5` | `pv-scale4-optimal-n5` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `pv-min-text-t0.3-n5` | `pv-high-image-t0.3-n5` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `pv-min-text-t0.3-n5` | `pv-min-image-t1.0-n10` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `pv-min-text-t0.3-n5` | `pv-min-image-t1.0-n5` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `pv-min-text-t0.3-n5` | `pv-high-image-t1.0-n5` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `pv-min-text-t1.0-n10` | `pv-min-image-t0.7-n10` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `pv-min-text-t1.0-n10` | `pv-high-image-t0.7-n5` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `pv-min-text-t1.0-n10` | `session-78-image-adversarial` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `pv-min-text-t1.0-n10` | `session-78-image-comparative` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `pv-min-text-t1.0-n10` | `session-78-image-brief` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `pv-min-text-t1.0-n10` | `session-78-image-checklist` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `pv-min-text-t1.0-n10` | `pv-min-image-t0.3-n10` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `pv-min-text-t1.0-n10` | `session-78-image-checklist-text` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `pv-min-text-t1.0-n10` | `pv-min-image-t0.3-n5` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `pv-min-text-t1.0-n10` | `pv-high-image-t0.7-n10` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `pv-min-text-t1.0-n10` | `pv-min-image-t0.7-n5` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `pv-min-text-t1.0-n10` | `session-78-image-adversarial-text` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `pv-min-text-t1.0-n10` | `pv-high-image-t0.3-n10` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `pv-min-text-t1.0-n10` | `pv-scale4-optimal-n10` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `pv-min-text-t1.0-n10` | `session-78-image-brief-text` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `pv-min-text-t1.0-n10` | `pv-n1-image-t0-n3` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `pv-min-text-t1.0-n10` | `pv-high-image-t1.0-n10` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `pv-min-text-t1.0-n10` | `pv-scale4-optimal-n5` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `pv-min-text-t1.0-n10` | `pv-min-image-t1.0-n10` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `pv-min-text-t1.0-n10` | `pv-high-image-t0.3-n5` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `pv-min-text-t1.0-n10` | `pv-min-image-t1.0-n5` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `pv-min-text-t1.0-n10` | `pv-high-image-t1.0-n5` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `session-78-text-brief` | `session-78-text-brief-text` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `session-78-text-brief` | `pv-min-image-t0.7-n10` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `session-78-text-brief` | `pv-high-image-t0.7-n5` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `session-78-text-brief` | `session-78-image-adversarial` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `session-78-text-brief` | `session-78-image-comparative` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `session-78-text-brief` | `session-78-image-brief` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `session-78-text-brief` | `session-78-image-checklist` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `session-78-text-brief` | `pv-min-image-t0.3-n10` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `session-78-text-brief` | `session-78-image-checklist-text` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `session-78-text-brief` | `pv-min-image-t0.3-n5` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `session-78-text-brief` | `pv-high-image-t0.7-n10` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `session-78-text-brief` | `pv-min-image-t0.7-n5` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `session-78-text-brief` | `session-78-image-adversarial-text` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `session-78-text-brief` | `pv-high-image-t0.3-n10` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `session-78-text-brief` | `pv-scale4-optimal-n10` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `session-78-text-brief` | `session-78-image-brief-text` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `session-78-text-brief` | `pv-high-image-t1.0-n10` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `session-78-text-brief` | `pv-n1-image-t0-n3` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `session-78-text-brief` | `pv-scale4-optimal-n5` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `session-78-text-brief` | `pv-min-image-t1.0-n10` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `session-78-text-brief` | `pv-high-image-t0.3-n5` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `session-78-text-brief` | `pv-min-image-t1.0-n5` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `session-78-text-brief` | `pv-high-image-t1.0-n5` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `pv-high-text-t0.7-n10` | `pv-min-image-t0.7-n10` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `pv-high-text-t0.7-n10` | `pv-high-image-t0.7-n5` | 0.0001 | 1 |  |
| 2 | pv | f1 | `pv-high-text-t0.7-n10` | `session-78-image-adversarial` | 0.0001 | 1 |  |
| 2 | pv | f1 | `pv-high-text-t0.7-n10` | `session-78-image-comparative` | 0.0001 | 1 |  |
| 2 | pv | f1 | `pv-high-text-t0.7-n10` | `session-78-image-brief` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `pv-high-text-t0.7-n10` | `pv-min-image-t0.3-n10` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `pv-high-text-t0.7-n10` | `session-78-image-checklist` | 0.0001 | 1 |  |
| 2 | pv | f1 | `pv-high-text-t0.7-n10` | `session-78-image-checklist-text` | 0.0001 | 1 |  |
| 2 | pv | f1 | `pv-high-text-t0.7-n10` | `pv-min-image-t0.3-n5` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `pv-high-text-t0.7-n10` | `pv-high-image-t0.7-n10` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `pv-high-text-t0.7-n10` | `pv-min-image-t0.7-n5` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `pv-high-text-t0.7-n10` | `session-78-image-adversarial-text` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `pv-high-text-t0.7-n10` | `pv-high-image-t0.3-n10` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `pv-high-text-t0.7-n10` | `session-78-image-brief-text` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `pv-high-text-t0.7-n10` | `pv-scale4-optimal-n10` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `pv-high-text-t0.7-n10` | `pv-n1-image-t0-n3` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `pv-high-text-t0.7-n10` | `pv-high-image-t1.0-n10` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `pv-high-text-t0.7-n10` | `pv-scale4-optimal-n5` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `pv-high-text-t0.7-n10` | `pv-min-image-t1.0-n10` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `pv-high-text-t0.7-n10` | `pv-high-image-t0.3-n5` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `pv-high-text-t0.7-n10` | `pv-min-image-t1.0-n5` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `pv-high-text-t0.7-n10` | `pv-high-image-t1.0-n5` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `pv-min-text-t0.7-n5` | `pv-min-image-t0.7-n10` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `pv-min-text-t0.7-n5` | `pv-high-image-t0.7-n5` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `pv-min-text-t0.7-n5` | `session-78-image-adversarial` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `pv-min-text-t0.7-n5` | `session-78-image-brief` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `pv-min-text-t0.7-n5` | `pv-min-image-t0.3-n10` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `pv-min-text-t0.7-n5` | `session-78-image-comparative` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `pv-min-text-t0.7-n5` | `session-78-image-checklist` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `pv-min-text-t0.7-n5` | `session-78-image-checklist-text` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `pv-min-text-t0.7-n5` | `pv-min-image-t0.3-n5` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `pv-min-text-t0.7-n5` | `pv-high-image-t0.7-n10` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `pv-min-text-t0.7-n5` | `pv-min-image-t0.7-n5` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `pv-min-text-t0.7-n5` | `session-78-image-adversarial-text` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `pv-min-text-t0.7-n5` | `pv-high-image-t0.3-n10` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `pv-min-text-t0.7-n5` | `pv-scale4-optimal-n10` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `pv-min-text-t0.7-n5` | `session-78-image-brief-text` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `pv-min-text-t0.7-n5` | `pv-n1-image-t0-n3` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `pv-min-text-t0.7-n5` | `pv-high-image-t1.0-n10` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `pv-min-text-t0.7-n5` | `pv-scale4-optimal-n5` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `pv-min-text-t0.7-n5` | `pv-high-image-t0.3-n5` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `pv-min-text-t0.7-n5` | `pv-min-image-t1.0-n10` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `pv-min-text-t0.7-n5` | `pv-min-image-t1.0-n5` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `pv-min-text-t0.7-n5` | `pv-high-image-t1.0-n5` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `pv-min-text-t0.7-n10` | `pv-min-image-t0.7-n10` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `pv-min-text-t0.7-n10` | `pv-high-image-t0.7-n5` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `pv-min-text-t0.7-n10` | `session-78-image-adversarial` | 0.0001 | 1 |  |
| 2 | pv | f1 | `pv-min-text-t0.7-n10` | `session-78-image-comparative` | 0.0001 | 1 |  |
| 2 | pv | f1 | `pv-min-text-t0.7-n10` | `session-78-image-brief` | 0.0001 | 1 |  |
| 2 | pv | f1 | `pv-min-text-t0.7-n10` | `session-78-image-checklist` | 0.0001 | 1 |  |
| 2 | pv | f1 | `pv-min-text-t0.7-n10` | `pv-min-image-t0.3-n10` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `pv-min-text-t0.7-n10` | `session-78-image-checklist-text` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `pv-min-text-t0.7-n10` | `pv-min-image-t0.3-n5` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `pv-min-text-t0.7-n10` | `pv-high-image-t0.7-n10` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `pv-min-text-t0.7-n10` | `session-78-image-adversarial-text` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `pv-min-text-t0.7-n10` | `pv-min-image-t0.7-n5` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `pv-min-text-t0.7-n10` | `pv-high-image-t0.3-n10` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `pv-min-text-t0.7-n10` | `pv-scale4-optimal-n10` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `pv-min-text-t0.7-n10` | `session-78-image-brief-text` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `pv-min-text-t0.7-n10` | `pv-n1-image-t0-n3` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `pv-min-text-t0.7-n10` | `pv-high-image-t1.0-n10` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `pv-min-text-t0.7-n10` | `pv-scale4-optimal-n5` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `pv-min-text-t0.7-n10` | `pv-high-image-t0.3-n5` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `pv-min-text-t0.7-n10` | `pv-min-image-t1.0-n10` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `pv-min-text-t0.7-n10` | `pv-min-image-t1.0-n5` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `pv-min-text-t0.7-n10` | `pv-high-image-t1.0-n5` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `pv-high-text-t0.3-n10` | `pv-high-text-t0.0-n3` | 0.0003 | 3 |  |
| 2 | pv | f1 | `pv-high-text-t0.3-n10` | `pv-min-image-t0.7-n10` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `pv-high-text-t0.3-n10` | `pv-high-image-t0.7-n5` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `pv-high-text-t0.3-n10` | `session-78-image-adversarial` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `pv-high-text-t0.3-n10` | `session-78-image-comparative` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `pv-high-text-t0.3-n10` | `session-78-image-brief` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `pv-high-text-t0.3-n10` | `session-78-image-checklist` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `pv-high-text-t0.3-n10` | `pv-min-image-t0.3-n10` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `pv-high-text-t0.3-n10` | `session-78-image-checklist-text` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `pv-high-text-t0.3-n10` | `pv-min-image-t0.3-n5` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `pv-high-text-t0.3-n10` | `pv-high-image-t0.7-n10` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `pv-high-text-t0.3-n10` | `pv-min-image-t0.7-n5` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `pv-high-text-t0.3-n10` | `session-78-image-adversarial-text` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `pv-high-text-t0.3-n10` | `pv-high-image-t0.3-n10` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `pv-high-text-t0.3-n10` | `pv-scale4-optimal-n10` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `pv-high-text-t0.3-n10` | `session-78-image-brief-text` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `pv-high-text-t0.3-n10` | `pv-n1-image-t0-n3` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `pv-high-text-t0.3-n10` | `pv-high-image-t1.0-n10` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `pv-high-text-t0.3-n10` | `pv-scale4-optimal-n5` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `pv-high-text-t0.3-n10` | `pv-high-image-t0.3-n5` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `pv-high-text-t0.3-n10` | `pv-min-image-t1.0-n10` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `pv-high-text-t0.3-n10` | `pv-min-image-t1.0-n5` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `pv-high-text-t0.3-n10` | `pv-high-image-t1.0-n5` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `pv-min-text-t1.0-n5` | `pv-min-image-t0.7-n10` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `pv-min-text-t1.0-n5` | `pv-high-image-t0.7-n5` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `pv-min-text-t1.0-n5` | `session-78-image-adversarial` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `pv-min-text-t1.0-n5` | `session-78-image-comparative` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `pv-min-text-t1.0-n5` | `session-78-image-brief` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `pv-min-text-t1.0-n5` | `session-78-image-checklist` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `pv-min-text-t1.0-n5` | `pv-min-image-t0.3-n10` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `pv-min-text-t1.0-n5` | `session-78-image-checklist-text` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `pv-min-text-t1.0-n5` | `pv-min-image-t0.3-n5` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `pv-min-text-t1.0-n5` | `pv-high-image-t0.7-n10` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `pv-min-text-t1.0-n5` | `pv-min-image-t0.7-n5` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `pv-min-text-t1.0-n5` | `session-78-image-adversarial-text` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `pv-min-text-t1.0-n5` | `pv-high-image-t0.3-n10` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `pv-min-text-t1.0-n5` | `pv-scale4-optimal-n10` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `pv-min-text-t1.0-n5` | `session-78-image-brief-text` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `pv-min-text-t1.0-n5` | `pv-n1-image-t0-n3` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `pv-min-text-t1.0-n5` | `pv-high-image-t1.0-n10` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `pv-min-text-t1.0-n5` | `pv-scale4-optimal-n5` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `pv-min-text-t1.0-n5` | `pv-high-image-t0.3-n5` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `pv-min-text-t1.0-n5` | `pv-min-image-t1.0-n10` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `pv-min-text-t1.0-n5` | `pv-min-image-t1.0-n5` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `pv-min-text-t1.0-n5` | `pv-high-image-t1.0-n5` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `pv-min-text-t0.3-n10` | `pv-min-image-t0.7-n10` | 0.0001 | 1 |  |
| 2 | pv | f1 | `pv-min-text-t0.3-n10` | `pv-high-image-t0.7-n5` | 0.0001 | 1 |  |
| 2 | pv | f1 | `pv-min-text-t0.3-n10` | `session-78-image-adversarial` | 0.0002 | 2 |  |
| 2 | pv | f1 | `pv-min-text-t0.3-n10` | `session-78-image-comparative` | 0.0001 | 1 |  |
| 2 | pv | f1 | `pv-min-text-t0.3-n10` | `session-78-image-brief` | 0.0001 | 1 |  |
| 2 | pv | f1 | `pv-min-text-t0.3-n10` | `session-78-image-checklist` | 0.0001 | 1 |  |
| 2 | pv | f1 | `pv-min-text-t0.3-n10` | `pv-min-image-t0.3-n10` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `pv-min-text-t0.3-n10` | `session-78-image-checklist-text` | 0.0001 | 1 |  |
| 2 | pv | f1 | `pv-min-text-t0.3-n10` | `pv-min-image-t0.3-n5` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `pv-min-text-t0.3-n10` | `pv-high-image-t0.7-n10` | 0.0001 | 1 |  |
| 2 | pv | f1 | `pv-min-text-t0.3-n10` | `pv-min-image-t0.7-n5` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `pv-min-text-t0.3-n10` | `session-78-image-adversarial-text` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `pv-min-text-t0.3-n10` | `pv-high-image-t0.3-n10` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `pv-min-text-t0.3-n10` | `pv-scale4-optimal-n10` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `pv-min-text-t0.3-n10` | `session-78-image-brief-text` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `pv-min-text-t0.3-n10` | `pv-n1-image-t0-n3` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `pv-min-text-t0.3-n10` | `pv-high-image-t1.0-n10` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `pv-min-text-t0.3-n10` | `pv-scale4-optimal-n5` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `pv-min-text-t0.3-n10` | `pv-high-image-t0.3-n5` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `pv-min-text-t0.3-n10` | `pv-min-image-t1.0-n10` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `pv-min-text-t0.3-n10` | `pv-min-image-t1.0-n5` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `pv-min-text-t0.3-n10` | `pv-high-image-t1.0-n5` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `pv-high-text-t0.7-n5` | `pv-min-image-t0.7-n10` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `pv-high-text-t0.7-n5` | `pv-high-image-t0.7-n5` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `pv-high-text-t0.7-n5` | `session-78-image-adversarial` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `pv-high-text-t0.7-n5` | `session-78-image-brief` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `pv-high-text-t0.7-n5` | `session-78-image-checklist` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `pv-high-text-t0.7-n5` | `session-78-image-comparative` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `pv-high-text-t0.7-n5` | `pv-min-image-t0.3-n10` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `pv-high-text-t0.7-n5` | `session-78-image-checklist-text` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `pv-high-text-t0.7-n5` | `pv-min-image-t0.3-n5` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `pv-high-text-t0.7-n5` | `pv-high-image-t0.7-n10` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `pv-high-text-t0.7-n5` | `pv-min-image-t0.7-n5` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `pv-high-text-t0.7-n5` | `session-78-image-adversarial-text` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `pv-high-text-t0.7-n5` | `pv-high-image-t0.3-n10` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `pv-high-text-t0.7-n5` | `pv-scale4-optimal-n10` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `pv-high-text-t0.7-n5` | `session-78-image-brief-text` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `pv-high-text-t0.7-n5` | `pv-n1-image-t0-n3` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `pv-high-text-t0.7-n5` | `pv-high-image-t1.0-n10` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `pv-high-text-t0.7-n5` | `pv-scale4-optimal-n5` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `pv-high-text-t0.7-n5` | `pv-high-image-t0.3-n5` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `pv-high-text-t0.7-n5` | `pv-min-image-t1.0-n10` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `pv-high-text-t0.7-n5` | `pv-min-image-t1.0-n5` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `pv-high-text-t0.7-n5` | `pv-high-image-t1.0-n5` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `pv-min-text-t0.0-n3` | `pv-high-image-t0.7-n5` | 0.0005 | 5 |  |
| 2 | pv | f1 | `pv-min-text-t0.0-n3` | `pv-min-image-t0.3-n10` | 0.0001 | 1 |  |
| 2 | pv | f1 | `pv-min-text-t0.0-n3` | `session-78-image-checklist-text` | 0.0003 | 3 |  |
| 2 | pv | f1 | `pv-min-text-t0.0-n3` | `pv-min-image-t0.3-n5` | 0.0001 | 1 |  |
| 2 | pv | f1 | `pv-min-text-t0.0-n3` | `pv-high-image-t0.7-n10` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `pv-min-text-t0.0-n3` | `pv-min-image-t0.7-n5` | 0.0001 | 1 |  |
| 2 | pv | f1 | `pv-min-text-t0.0-n3` | `session-78-image-adversarial-text` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `pv-min-text-t0.0-n3` | `pv-high-image-t0.3-n10` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `pv-min-text-t0.0-n3` | `pv-scale4-optimal-n10` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `pv-min-text-t0.0-n3` | `session-78-image-brief-text` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `pv-min-text-t0.0-n3` | `pv-n1-image-t0-n3` | 0.0001 | 1 |  |
| 2 | pv | f1 | `pv-min-text-t0.0-n3` | `pv-high-image-t1.0-n10` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `pv-min-text-t0.0-n3` | `pv-scale4-optimal-n5` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `pv-min-text-t0.0-n3` | `pv-high-image-t0.3-n5` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `pv-min-text-t0.0-n3` | `pv-min-image-t1.0-n10` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `pv-min-text-t0.0-n3` | `pv-min-image-t1.0-n5` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `pv-min-text-t0.0-n3` | `pv-high-image-t1.0-n5` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `pv-high-text-t1.0-n5` | `pv-min-image-t0.7-n10` | 0.0002 | 2 |  |
| 2 | pv | f1 | `pv-high-text-t1.0-n5` | `session-78-image-adversarial` | 0.0001 | 1 |  |
| 2 | pv | f1 | `pv-high-text-t1.0-n5` | `pv-high-image-t0.7-n5` | 0.0002 | 2 |  |
| 2 | pv | f1 | `pv-high-text-t1.0-n5` | `session-78-image-comparative` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `pv-high-text-t1.0-n5` | `session-78-image-brief` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `pv-high-text-t1.0-n5` | `pv-min-image-t0.3-n10` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `pv-high-text-t1.0-n5` | `session-78-image-checklist` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `pv-high-text-t1.0-n5` | `session-78-image-checklist-text` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `pv-high-text-t1.0-n5` | `pv-min-image-t0.3-n5` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `pv-high-text-t1.0-n5` | `pv-high-image-t0.7-n10` | 0.0001 | 1 |  |
| 2 | pv | f1 | `pv-high-text-t1.0-n5` | `pv-min-image-t0.7-n5` | 0.0001 | 1 |  |
| 2 | pv | f1 | `pv-high-text-t1.0-n5` | `session-78-image-adversarial-text` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `pv-high-text-t1.0-n5` | `pv-high-image-t0.3-n10` | 0.0001 | 1 |  |
| 2 | pv | f1 | `pv-high-text-t1.0-n5` | `pv-scale4-optimal-n10` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `pv-high-text-t1.0-n5` | `session-78-image-brief-text` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `pv-high-text-t1.0-n5` | `pv-n1-image-t0-n3` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `pv-high-text-t1.0-n5` | `pv-high-image-t1.0-n10` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `pv-high-text-t1.0-n5` | `pv-scale4-optimal-n5` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `pv-high-text-t1.0-n5` | `pv-high-image-t0.3-n5` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `pv-high-text-t1.0-n5` | `pv-min-image-t1.0-n10` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `pv-high-text-t1.0-n5` | `pv-min-image-t1.0-n5` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `pv-high-text-t1.0-n5` | `pv-high-image-t1.0-n5` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `session-78-text-checklist-text` | `pv-min-image-t0.7-n10` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `session-78-text-checklist-text` | `pv-high-image-t0.7-n5` | 0.0001 | 1 |  |
| 2 | pv | f1 | `session-78-text-checklist-text` | `session-78-image-adversarial` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `session-78-text-checklist-text` | `session-78-image-comparative` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `session-78-text-checklist-text` | `session-78-image-brief` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `session-78-text-checklist-text` | `session-78-image-checklist` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `session-78-text-checklist-text` | `pv-min-image-t0.3-n10` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `session-78-text-checklist-text` | `session-78-image-checklist-text` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `session-78-text-checklist-text` | `pv-min-image-t0.3-n5` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `session-78-text-checklist-text` | `pv-high-image-t0.7-n10` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `session-78-text-checklist-text` | `pv-min-image-t0.7-n5` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `session-78-text-checklist-text` | `session-78-image-adversarial-text` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `session-78-text-checklist-text` | `pv-high-image-t0.3-n10` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `session-78-text-checklist-text` | `pv-scale4-optimal-n10` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `session-78-text-checklist-text` | `session-78-image-brief-text` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `session-78-text-checklist-text` | `pv-n1-image-t0-n3` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `session-78-text-checklist-text` | `pv-high-image-t1.0-n10` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `session-78-text-checklist-text` | `pv-scale4-optimal-n5` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `session-78-text-checklist-text` | `pv-high-image-t0.3-n5` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `session-78-text-checklist-text` | `pv-min-image-t1.0-n10` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `session-78-text-checklist-text` | `pv-min-image-t1.0-n5` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `session-78-text-checklist-text` | `pv-high-image-t1.0-n5` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `session-78-text-adversarial-text` | `pv-min-image-t0.7-n10` | 0.0001 | 1 |  |
| 2 | pv | f1 | `session-78-text-adversarial-text` | `pv-high-image-t0.7-n5` | 0.0002 | 2 |  |
| 2 | pv | f1 | `session-78-text-adversarial-text` | `session-78-image-adversarial` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `session-78-text-adversarial-text` | `session-78-image-comparative` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `session-78-text-adversarial-text` | `session-78-image-brief` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `session-78-text-adversarial-text` | `session-78-image-checklist` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `session-78-text-adversarial-text` | `pv-min-image-t0.3-n10` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `session-78-text-adversarial-text` | `session-78-image-checklist-text` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `session-78-text-adversarial-text` | `pv-min-image-t0.3-n5` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `session-78-text-adversarial-text` | `pv-high-image-t0.7-n10` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `session-78-text-adversarial-text` | `pv-min-image-t0.7-n5` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `session-78-text-adversarial-text` | `session-78-image-adversarial-text` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `session-78-text-adversarial-text` | `pv-high-image-t0.3-n10` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `session-78-text-adversarial-text` | `pv-scale4-optimal-n10` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `session-78-text-adversarial-text` | `session-78-image-brief-text` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `session-78-text-adversarial-text` | `pv-high-image-t1.0-n10` | 0.0001 | 1 |  |
| 2 | pv | f1 | `session-78-text-adversarial-text` | `pv-n1-image-t0-n3` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `session-78-text-adversarial-text` | `pv-scale4-optimal-n5` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `session-78-text-adversarial-text` | `pv-min-image-t1.0-n10` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `session-78-text-adversarial-text` | `pv-high-image-t0.3-n5` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `session-78-text-adversarial-text` | `pv-min-image-t1.0-n5` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `session-78-text-adversarial-text` | `pv-high-image-t1.0-n5` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `session-78-text-brief-text` | `session-78-image-checklist-text` | 0.0005 | 5 |  |
| 2 | pv | f1 | `session-78-text-brief-text` | `pv-min-image-t0.3-n5` | 0.0001 | 1 |  |
| 2 | pv | f1 | `session-78-text-brief-text` | `pv-high-image-t0.7-n10` | 0.0002 | 2 |  |
| 2 | pv | f1 | `session-78-text-brief-text` | `pv-min-image-t0.7-n5` | 0.0002 | 2 |  |
| 2 | pv | f1 | `session-78-text-brief-text` | `session-78-image-adversarial-text` | 0.0001 | 1 |  |
| 2 | pv | f1 | `session-78-text-brief-text` | `pv-high-image-t0.3-n10` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `session-78-text-brief-text` | `pv-scale4-optimal-n10` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `session-78-text-brief-text` | `session-78-image-brief-text` | 0.0001 | 1 |  |
| 2 | pv | f1 | `session-78-text-brief-text` | `pv-high-image-t1.0-n10` | 0.0001 | 1 |  |
| 2 | pv | f1 | `session-78-text-brief-text` | `pv-n1-image-t0-n3` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `session-78-text-brief-text` | `pv-scale4-optimal-n5` | 0.0001 | 1 |  |
| 2 | pv | f1 | `session-78-text-brief-text` | `pv-high-image-t0.3-n5` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `session-78-text-brief-text` | `pv-min-image-t1.0-n10` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `session-78-text-brief-text` | `pv-min-image-t1.0-n5` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `session-78-text-brief-text` | `pv-high-image-t1.0-n5` | 0.0000 | 0 | Y |
| 2 | pv | f1 | `pv-high-text-t0.0-n3` | `pv-min-image-t1.0-n5` | 0.0005 | 5 |  |
| 2 | pv | f1 | `pv-high-text-t0.0-n3` | `pv-high-image-t1.0-n5` | 0.0003 | 3 |  |
| 2 | pv | mcc | `pv-min-image-t0.3-n5` | `pv-high-text-t1.0-n5` | 0.0005 | 5 |  |
| 2 | pv | mcc | `pv-min-image-t0.3-n5` | `session-78-text-adversarial-text` | 0.0000 | 0 | Y |
| 2 | pv | mcc | `pv-min-image-t0.3-n10` | `session-78-text-adversarial-text` | 0.0002 | 2 |  |
| 2 | pv | mcc | `pv-high-image-t0.7-n5` | `session-78-text-adversarial-text` | 0.0000 | 0 | Y |
| 2 | pv | mcc | `pv-scale4-optimal-n5` | `session-78-text-adversarial-text` | 0.0005 | 5 |  |
| 3 | consensus | mcc | `h8v2-scale-4` | `h8v2-pure-positive-canon` | 0.0001 | 1 |  |

