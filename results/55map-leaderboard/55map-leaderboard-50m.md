# 55-map generalisation leaderboard — canonical GT @ 50 m

> Working buffer 50 m per the noise-floor derivation (`results/working-precision/55maps-csr-noise-floor.json`). Round-robin tile-swap permutation (10k, seed 42) + BH-FDR q=0.05 + greedy-clique tiers; 24/28 pairs significant.

| rank | cell | tier | F1@50 | 95% CI | P@50 | R@50 | tile-MCC | n |
|---:|---|---:|---:|---|---:|---:|---:|---:|
| 1 | T03-k3 (oracle) | 1 | 0.8476 | [0.8388, 0.8559] | 0.8697 | 0.8266 | 0.690 | 4905 |
| 2 | TH7-k3 | 1 | 0.8425 | [0.8335, 0.8512] | 0.8755 | 0.8119 | 0.680 | 4786 |
| 3 | T03-k4 | 2 | 0.8359 | [0.8265, 0.8447] | 0.9138 | 0.7702 | 0.671 | 4350 |
| 4 | TM-n10-k5 (uplift) | 2 | 0.8290 | [0.8190, 0.8385] | 0.9051 | 0.7648 | 0.672 | 4361 |
| 5 | TH7-k4 (carry-forward) | 3 | 0.8152 | [0.8051, 0.8251] | 0.9128 | 0.7365 | 0.667 | 4164 |
| 6 | TM-k3 | 3 | 0.8127 | [0.8025, 0.8227] | 0.8965 | 0.7433 | 0.658 | 4279 |
| 7 | IM-k3 | 4 | 0.7987 | [0.7887, 0.8081] | 0.8397 | 0.7615 | 0.710 | 4680 |
| 8 | TM-k4 | 5 | 0.7831 | [0.7719, 0.7940] | 0.9144 | 0.6848 | 0.641 | 3865 |

## Reading this board

**Confidence intervals vs significance.** The 95% intervals in the board table
are *marginal* per-cell BCa bootstrap intervals; the significance tests are
*paired* tile-swap permutations over the same tiles. Overlapping intervals are
therefore consistent with a significant paired difference — the paired test
removes between-tile variance that the marginal intervals retain. Read the
BH-adjusted pairwise table below, not interval overlap, for significance.

**Attribution resolution (55-map deployment corpus).** Two distinct sources of
spatial imprecision affect this reference, and they behave differently:

1. *Student-digitised mounds* (n = 4,746) carry roughly 20–25 m of positional
   jitter — continuous error in where a recorded mound sits.
2. *Reviewer-confirmed phantoms* (n = 773 — model detections that human
   verification found to be real mounds the students had missed) carry their
   match distance only as a **25 m ring anchored at 50 m**: a mound within 50 m
   of the detection was recorded as "50 m", the next ring as "75 m", and so on.
   This error is interval-censored, not continuous.

Phantoms enter the extended ground truth only at R >= their recorded ring
(`build_phantom_gdf`): detections we cannot localise at the scoring radius are
not credited. Because the tightest available ring is 50 m, **below R = 50 m the
extended ground truth reduces to the reviewed student ground truth** — Track-2
results are distinct from Track-1 only at R >= 50 m, and sub-50 m Track-2
figures penalise correct detections of student-missed mounds. The 55-map
headline is therefore reported at 50 m, and the full 14-buffer sweep should be
read as descriptive rather than as evidence of sub-25 m precision differences.
This applies to the 55-map deployment corpus only; the gold-standard corpus
uses curator ground truth and is unaffected.

Review coverage was pooled across all four proposer configurations
(`build_canonical_gt.py` `CARRIED_RUNS`) and deduplicated by 20 m clustering,
each cluster taking the tightest ring any run achieved, so the reference is
config-agnostic. The additional k3-shell review pass covered the three text
configurations only, so any residual enrichment asymmetry favours the text
cells.
