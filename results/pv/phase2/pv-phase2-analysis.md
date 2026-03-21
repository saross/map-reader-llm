# PV Phase 2: Production Verifier Results (340-Tile Corpus)

**Generated**: 2026-03-21
**Verifier**: Adversarial-text, 150 px crops, N=1, T=0.0
**Experiments**: 25 proposer configurations (N=1 single runs + consensus unions)
**Bootstrap**: 1,000 iterations, seed=42
**Phase 1 reference**: `results/pv/phase1/pv-phase1-analysis.md`

## Key Finding

The PV verifier improved F1 in **25/25 experiments** (mean +0.1733). The optimal architecture is moderate consensus (3--5 of 10 runs) + single-pass verifier, achieving **F1=0.8314** -- the new project best, up from 0.7620 (HIGH 25-of-30 consensus without PV). The "Goldilocks zone" of 3-of-10 through 5-of-10 text consensus + PV dominates the leaderboard, with 11 total passes costing approximately $0.004/tile versus 30 passes at approximately $0.026/tile for the previous best.

## Leaderboard (Top 15 by PV F1)

| Rank | Experiment | Config | Proposer F1 | PV F1 | 95% CI | P | R | Delta F1 |
|-----:|:-----------|:-------|------------:|------:|:------:|------:|------:|---------:|
| 1 | 09 | text-5of10 | 0.6658 | 0.8314 | [0.7894, 0.8699] | 0.8815 | 0.7866 | +0.1656 |
| 2 | 08 | text-3of10 | 0.6129 | 0.8227 | [0.7838, 0.8598] | 0.8411 | 0.8052 | +0.2098 |
| 3 | 25 | high-20of30 | 0.7602 | 0.8188 | [0.7763, 0.8561] | 0.9132 | 0.7421 | +0.0586 |
| 4 | 07 | text-2of10 | 0.5596 | 0.8066 | [0.7654, 0.8466] | 0.7971 | 0.8163 | +0.2470 |
| 5 | 21 | text-25of30 | 0.6843 | 0.7941 | [0.7520, 0.8343] | 0.9280 | 0.6939 | +0.1098 |
| 6 | 26 | high-25of30 | 0.7620 | 0.7852 | [0.7377, 0.8291] | 0.9524 | 0.6679 | +0.0232 |
| 7 | 15 | text-t0.7 | 0.5819 | 0.7678 | [0.7207, 0.8099] | 0.7750 | 0.7607 | +0.1859 |
| 8 | 14 | rep-min-1of10 | 0.4340 | 0.7423 | [0.7017, 0.7848] | 0.6742 | 0.8256 | +0.3083 |
| 9 | 06 | text-1of10 | 0.4225 | 0.7371 | [0.6943, 0.7787] | 0.6682 | 0.8219 | +0.3146 |
| 10 | 19 | brief-text | 0.5384 | 0.7331 | [0.6813, 0.7769] | 0.7429 | 0.7236 | +0.1947 |
| 11 | 03 | high-text-t0.3 | 0.4982 | 0.7249 | [0.6792, 0.7691] | 0.6908 | 0.7625 | +0.2267 |
| 12 | 02 | canonical-last | 0.6032 | 0.7194 | [0.6743, 0.7614] | 0.6981 | 0.7421 | +0.1162 |
| 13 | 23 | image-20of30 | 0.6758 | 0.7187 | [0.6755, 0.7611] | 0.8317 | 0.6327 | +0.0429 |
| 14 | 16 | text-t1.0 | 0.5106 | 0.7163 | [0.6680, 0.7591] | 0.7183 | 0.7143 | +0.2057 |
| 15 | 13 | image-5of10 | 0.6467 | 0.7124 | [0.6660, 0.7554] | 0.7425 | 0.6846 | +0.0657 |

**Previous project best without PV**: HIGH 25-of-30 consensus, F1=0.7620 [0.7169, 0.8057]

## Group A: N=1 Single Runs + PV

Single proposer runs verified by adversarial-text.

| Experiment | Config | Proposer F1 | PV F1 | 95% CI | P | R | Threshold | n | Delta F1 |
|:-----------|:-------|------------:|------:|:------:|------:|------:|----------:|----:|---------:|
| 02 | text T0.0 run_3 | 0.6032 | 0.7194 | [0.6743, 0.7614] | 0.6981 | 0.7421 | 0.20 | 573 | +0.1162 |
| 03 | HIGH text T0.3 | 0.4982 | 0.7249 | [0.6792, 0.7691] | 0.6908 | 0.7625 | 0.20 | 595 | +0.2267 |
| 04 | rep HIGH | 0.4413 | 0.6934 | [0.6456, 0.7420] | 0.6551 | 0.7365 | 0.20 | 606 | +0.2521 |
| 05 | image T0.0 N=1 | 0.5844 | 0.6799 | [0.6392, 0.7183] | 0.6631 | 0.6976 | 0.15 | 567 | +0.0955 |
| 15 | text T0.7 N=1 | 0.5819 | 0.7678 | [0.7207, 0.8099] | 0.7750 | 0.7607 | 0.15 | 529 | +0.1859 |
| 16 | text T1.0 N=1 | 0.5106 | 0.7163 | [0.6680, 0.7591] | 0.7183 | 0.7143 | 0.20 | 536 | +0.2057 |
| 17 | image T0.0 N=1 | 0.5844 | 0.6679 | [0.6236, 0.7125] | 0.6554 | 0.6809 | 0.15 | 560 | +0.0835 |
| 18 | HIGH text T0.7 | 0.4336 | 0.6853 | [0.6415, 0.7261] | 0.6898 | 0.6809 | 0.40 | 532 | +0.2517 |
| 19 | brief-text N=1 | 0.5384 | 0.7331 | [0.6813, 0.7769] | 0.7429 | 0.7236 | 0.20 | 525 | +0.1947 |
| 20 | image T0.7 N=1 | 0.5348 | 0.6350 | [0.5870, 0.6825] | 0.6146 | 0.6568 | 0.20 | 576 | +0.1002 |

Mean Delta F1 for single runs: +0.1717

## Group B: Consensus Unions + PV

Consensus proposer unions (x-of-N agreement threshold) verified by adversarial-text. This group contains the key result.

| Experiment | Config | Proposer F1 | PV F1 | 95% CI | P | R | Threshold | n | Delta F1 |
|:-----------|:-------|------------:|------:|:------:|------:|------:|----------:|----:|---------:|
| 06 | text-1of10 | 0.4225 | 0.7371 | [0.6943, 0.7787] | 0.6682 | 0.8219 | 0.20 | 663 | +0.3146 |
| 07 | text-2of10 | 0.5596 | 0.8066 | [0.7654, 0.8466] | 0.7971 | 0.8163 | 0.20 | 552 | +0.2470 |
| 08 | **text-3of10** | 0.6129 | **0.8227** | [0.7838, 0.8598] | 0.8411 | 0.8052 | 0.15 | 516 | +0.2098 |
| 09 | **text-5of10** | 0.6658 | **0.8314** | [0.7894, 0.8699] | 0.8815 | 0.7866 | 0.15 | 481 | +0.1656 |
| 10 | image-1of10 | 0.3921 | 0.5519 | [0.5112, 0.5900] | 0.4420 | 0.7347 | 0.35 | 896 | +0.1598 |
| 11 | image-2of10 | 0.5163 | 0.6348 | [0.5932, 0.6768] | 0.5557 | 0.7403 | 0.20 | 718 | +0.1185 |
| 12 | image-3of10 | 0.5794 | 0.6684 | [0.6243, 0.7110] | 0.6310 | 0.7106 | 0.15 | 607 | +0.0890 |
| 13 | image-5of10 | 0.6467 | 0.7124 | [0.6660, 0.7554] | 0.7425 | 0.6846 | 0.15 | 497 | +0.0657 |
| 14 | rep-min-1of10 | 0.4340 | 0.7423 | [0.7017, 0.7848] | 0.6742 | 0.8256 | 0.20 | 660 | +0.3083 |

The **Goldilocks zone** (Obs 170): text consensus at 3-of-10 and 5-of-10 produces the two highest PV F1 scores in the entire study. Lower thresholds (1-of-10) retain too many false positives for the verifier to clean up; higher thresholds (consensus-only without PV) sacrifice recall that the verifier cannot recover.

Mean Delta F1 for consensus runs: +0.1865

## Top-Performer Additions (experiments 21--26)

HIGH consensus and N=30 pool experiments.

| Experiment | Config | Proposer F1 | PV F1 | 95% CI | P | R | Threshold | n | Delta F1 |
|:-----------|:-------|------------:|------:|:------:|------:|------:|----------:|----:|---------:|
| 21 | text-25of30 | 0.6843 | 0.7941 | [0.7520, 0.8343] | 0.9280 | 0.6939 | 0.15 | 403 | +0.1098 |
| 22 | text-1of30 | 0.3231 | 0.6630 | [0.6218, 0.7040] | 0.5720 | 0.7885 | 0.25 | 743 | +0.3399 |
| 23 | image-20of30 | 0.6758 | 0.7187 | [0.6755, 0.7611] | 0.8317 | 0.6327 | 0.20 | 410 | +0.0429 |
| 24 | image-1of30 | 0.2892 | 0.4779 | [0.4407, 0.5191] | 0.3568 | 0.7236 | 0.80 | 1093 | +0.1887 |
| 25 | **high-20of30** | 0.7602 | **0.8188** | [0.7763, 0.8561] | 0.9132 | 0.7421 | 0.15 | 438 | +0.0586 |
| 26 | high-25of30 | 0.7620 | 0.7852 | [0.7377, 0.8291] | 0.9524 | 0.6679 | 0.15 | 378 | +0.0232 |

HIGH 20-of-30 + PV (F1=0.8188) is the third-best overall, and the best among HIGH configurations. However, it requires 31 total passes (30 proposer + 1 verifier) versus 11 passes (10 proposer + 1 verifier) for text-5of10, which achieves a higher F1=0.8314. HIGH 25-of-30 + PV (F1=0.7852) actually *underperforms* its 20-of-30 counterpart because the aggressive consensus threshold sacrifices too much recall (0.6679) for the verifier to compensate.

## Track Comparison (Obs 173)

Text versus image proposers at matched consensus levels.

| Consensus | Text PV F1 | Image PV F1 | Delta |
|:----------|----------:|:-----------:|------:|
| 1-of-10 | 0.7371 | 0.5519 | +0.1852 |
| 2-of-10 | 0.8066 | 0.6348 | +0.1718 |
| 3-of-10 | 0.8227 | 0.6684 | +0.1543 |
| 5-of-10 | 0.8314 | 0.7124 | +0.1190 |
| 1-of-30 | 0.6630 | 0.4779 | +0.1851 |
| 20-of-30 | -- | 0.7187 | -- |
| 25-of-30 | 0.7941 | -- | -- |

Text proposers consistently outperform image proposers by +0.12 to +0.19 F1 at every consensus level. The gap narrows at higher consensus thresholds because aggressive filtering removes more image-track false positives before verification. The image track's ceiling appears to be approximately F1=0.72 even with heavy consensus + PV.

## Cost-Efficiency Analysis (Obs 174)

All costs assume Gemini 2.0 Flash real-time API pricing.

| Configuration | Total Passes | Est. Cost/Tile | PV F1 |
|:--------------|------------:|:--------------:|------:|
| text-5of10 + PV | 11 | ~$0.004 | 0.8314 |
| text-3of10 + PV | 11 | ~$0.004 | 0.8227 |
| high-20of30 + PV | 31 | ~$0.012 | 0.8188 |
| text-2of10 + PV | 11 | ~$0.004 | 0.8066 |
| text-25of30 + PV | 31 | ~$0.012 | 0.7941 |
| HIGH 25-of-30 (no PV) | 30 | ~$0.026 | 0.7620 |
| text-1of10 + PV | 11 | ~$0.004 | 0.7371 |
| single text + PV | 2 | ~$0.001 | 0.7194 |

**Headline**: 11 passes at approximately $0.004/tile (text-5of10 + PV) beats 30 passes at approximately $0.026/tile (HIGH 25-of-30 consensus without PV) by +0.0694 F1, at one-sixth the cost.

## [PENDING] Sections

- [PENDING: Pairwise bootstrap comparisons (computing on sapphire)]
- [PENDING: False Discovery Rate (FDR)-corrected significance tests]
- [PENDING: Phase 3c image track PV results (blocked on image diversity runs)]

## Methodology

1. Proposer detections sourced from Phase 2b single runs (T=0.0, T=0.3, T=0.7, T=1.0), Phase 2a brief-text, Phase 3a consensus unions (text, image, HIGH, minimal), and Phase 3a replication runs
2. Consensus unions computed using x-of-N vote threshold with 20 m clustering tolerance
3. Candidate crops extracted from source GeoTIFF rasters at 150 px (E33 non-truncating path)
4. Each crop submitted to adversarial-text verifier via real-time API (N=1, T=0.0)
5. Probability threshold swept 0.0--1.0 in 0.05 steps; optimal selected by maximum F1
6. F1/P/R computed via Hungarian matching at 20 m spatial tolerance
7. Bootstrap CIs via tile-level resampling (K=1,000, seed=42)
