# 55-map canonical board — tile-MCC permutation tiering @ 50 m

> Alternate-metric (tile-MCC) statistical tiering for the eight canonical-GT cells: round-robin tile-swap permutation on the MCC statistic (10k, seed 42, two-sided) + BH-FDR q=0.05 + greedy-clique tiers — the same machinery as the F1-led board. 20/28 pairs significant -> 5 tier(s). 95% CIs are the Track-2 engine's BCa bootstrap CIs, carried from `summary.json`. Gate: rebuilt per-tile confusion matrices reproduce the committed evaluations exactly (8/8).

| rank | cell | tier | MCC | 95% CI | sens | spec | tp/fp/fn/tn |
|---:|---|---:|---:|---|---:|---:|---|
| 1 | IM-k3 | 1 | 0.7104 | [0.697, 0.723] | 0.705 | 0.964 | 2483/181/1041/4836 |
| 2 | T03-k3 (oracle) | 2 | 0.6903 | [0.677, 0.704] | 0.699 | 0.953 | 2462/235/1062/4782 |
| 3 | TH7-k3 | 2 | 0.6796 | [0.666, 0.693] | 0.688 | 0.952 | 2423/241/1101/4776 |
| 4 | TM-n10-k5 (uplift) | 3 | 0.6725 | [0.659, 0.686] | 0.655 | 0.965 | 2309/175/1215/4842 |
| 5 | T03-k4 | 3 | 0.6711 | [0.657, 0.685] | 0.652 | 0.966 | 2299/172/1225/4845 |
| 6 | TH7-k4 (carry-forward) | 3 | 0.6666 | [0.653, 0.680] | 0.642 | 0.969 | 2261/158/1263/4859 |
| 7 | TM-k3 | 4 | 0.6580 | [0.644, 0.672] | 0.645 | 0.961 | 2274/197/1250/4820 |
| 8 | TM-k4 | 5 | 0.6411 | [0.628, 0.655] | 0.610 | 0.968 | 2150/159/1374/4858 |

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

## Pairwise (BH-adjusted)

| pair | ΔMCC | p | BH p | sig |
|---|---:|---:|---:|---|
| IM-k3 vs T03-k4 | +0.0393 | 0.0000 | 0.0000 | yes |
| IM-k3 vs TH7-k3 | +0.0308 | 0.0000 | 0.0000 | yes |
| IM-k3 vs TH7-k4 (carry-forward) | +0.0438 | 0.0000 | 0.0000 | yes |
| IM-k3 vs TM-k3 | +0.0525 | 0.0000 | 0.0000 | yes |
| IM-k3 vs TM-k4 | +0.0693 | 0.0000 | 0.0000 | yes |
| IM-k3 vs TM-n10-k5 (uplift) | +0.0380 | 0.0000 | 0.0000 | yes |
| T03-k3 (oracle) vs T03-k4 | +0.0193 | 0.0000 | 0.0000 | yes |
| T03-k3 (oracle) vs TH7-k4 (carry-forward) | +0.0237 | 0.0000 | 0.0000 | yes |
| T03-k3 (oracle) vs TM-k3 | +0.0324 | 0.0000 | 0.0000 | yes |
| T03-k3 (oracle) vs TM-k4 | +0.0492 | 0.0000 | 0.0000 | yes |
| T03-k4 vs TM-k4 | +0.0299 | 0.0000 | 0.0000 | yes |
| TH7-k3 vs TM-k4 | +0.0385 | 0.0000 | 0.0000 | yes |
| TM-k3 vs TM-k4 | +0.0168 | 0.0000 | 0.0000 | yes |
| TM-k4 vs TM-n10-k5 (uplift) | -0.0313 | 0.0000 | 0.0000 | yes |
| TH7-k4 (carry-forward) vs TM-k4 | +0.0255 | 0.0001 | 0.0002 | yes |
| TH7-k3 vs TM-k3 | +0.0216 | 0.0008 | 0.0014 | yes |
| TH7-k3 vs TH7-k4 (carry-forward) | +0.0130 | 0.0009 | 0.0015 | yes |
| IM-k3 vs T03-k3 (oracle) | +0.0201 | 0.0036 | 0.0056 | yes |
| T03-k3 (oracle) vs TM-n10-k5 (uplift) | +0.0179 | 0.0051 | 0.0075 | yes |
| TM-k3 vs TM-n10-k5 (uplift) | -0.0145 | 0.0060 | 0.0084 | yes |
| T03-k4 vs TM-k3 | +0.0131 | 0.0415 | 0.0553 | ns |
| T03-k3 (oracle) vs TH7-k3 | +0.0107 | 0.0614 | 0.0781 | ns |
| T03-k4 vs TH7-k3 | -0.0085 | 0.1412 | 0.1719 | ns |
| TH7-k4 (carry-forward) vs TM-k3 | +0.0087 | 0.1757 | 0.2050 | ns |
| TH7-k3 vs TM-n10-k5 (uplift) | +0.0072 | 0.2714 | 0.3040 | ns |
| TH7-k4 (carry-forward) vs TM-n10-k5 (uplift) | -0.0058 | 0.3625 | 0.3904 | ns |
| T03-k4 vs TH7-k4 (carry-forward) | +0.0044 | 0.4273 | 0.4431 | ns |
| T03-k4 vs TM-n10-k5 (uplift) | -0.0014 | 0.8244 | 0.8244 | ns |
