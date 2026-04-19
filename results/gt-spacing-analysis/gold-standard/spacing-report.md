# Ground-truth nearest-neighbour spacing — gold-standard maps

Inter-mound nearest-neighbour (NN) distances on the four gold-standard reference maps. All coordinates are in EPSG:32635 (UTM Zone 35N, metric, Bulgaria). NN distances are computed *within each map*; the pooled distribution concatenates per-map NN vectors.

**Motivation.** On the 55-map text HIGH run the F1 score plateaus at ~40-50 m IoU-buffer diameter. If inter-mound spacing approaches the buffer diameter, match-zone overlap introduces matching ambiguity (one prediction may legitimately sit inside two truth buffers). This analysis quantifies how close we are to that danger zone.

## Distribution summary (metres)

| Map | n | min | p05 | p10 | p25 | p50 | p75 | p90 | p95 | max | mean | std |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| K-35-052-4 | 136 | 80.2 | 88.1 | 105.3 | 189.5 | 473.4 | 986.0 | 1396.8 | 1575.1 | 4296.2 | 644.7 | 599.0 |
| K-35-053-3_Elenovo | 217 | 68.1 | 76.8 | 82.8 | 135.6 | 412.3 | 643.4 | 1036.0 | 1324.0 | 2296.3 | 500.3 | 423.2 |
| K-35-062-2_Rakovski | 196 | 83.1 | 99.7 | 120.1 | 248.2 | 442.2 | 754.9 | 1074.3 | 1250.1 | 2408.2 | 551.7 | 408.0 |
| K-35-078-1_Lesovo | 20 | 421.7 | 421.7 | 489.6 | 520.3 | 777.6 | 1176.3 | 2435.7 | 2652.0 | 6761.4 | 1276.1 | 1449.6 |
| **Pooled** | **569** | **68.1** | **83.2** | **100.7** | **198.5** | **449.5** | **782.2** | **1219.2** | **1456.4** | **6761.4** | **579.8** | **549.2** |

## Mounds with NN distance below buffer thresholds

Counts (and fraction of map total) of mounds whose nearest neighbour lies within each buffer threshold. A mound with NN < buffer diameter shares its match zone with at least one other ground-truth mound.

| Map | n | < 20 m | < 30 m | < 50 m | < 70 m | < 100 m |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| K-35-052-4 | 136 | 0 (0.0%) | 0 (0.0%) | 0 (0.0%) | 0 (0.0%) | 12 (8.8%) |
| K-35-053-3_Elenovo | 217 | 0 (0.0%) | 0 (0.0%) | 0 (0.0%) | 2 (0.9%) | 35 (16.1%) |
| K-35-062-2_Rakovski | 196 | 0 (0.0%) | 0 (0.0%) | 0 (0.0%) | 0 (0.0%) | 10 (5.1%) |
| K-35-078-1_Lesovo | 20 | 0 (0.0%) | 0 (0.0%) | 0 (0.0%) | 0 (0.0%) | 0 (0.0%) |
| **Pooled** | **569** | **0 (0.0%)** | **0 (0.0%)** | **0 (0.0%)** | **2 (0.4%)** | **57 (10.0%)** |

## NN distance histogram — 10 m bins

Counts per 10 m bin from 0-200 m. The final column reports the overflow (NN >= 200 m).

| Map | 0-10 | 10-20 | 20-30 | 30-40 | 40-50 | 50-60 | 60-70 | 70-80 | 80-90 | 90-100 | 100-110 | 110-120 | 120-130 | 130-140 | 140-150 | 150-160 | 160-170 | 170-180 | 180-190 | 190-200 | >=200 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| K-35-052-4 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 10 | 2 | 4 | 4 | 5 | 2 | 0 | 2 | 2 | 2 | 2 | 2 | 99 |
| K-35-053-3_Elenovo | 0 | 0 | 0 | 0 | 0 | 0 | 2 | 13 | 16 | 4 | 5 | 0 | 8 | 7 | 4 | 0 | 2 | 5 | 0 | 2 | 149 |
| K-35-062-2_Rakovski | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 8 | 2 | 4 | 6 | 4 | 4 | 2 | 4 | 4 | 0 | 1 | 0 | 157 |
| K-35-078-1_Lesovo | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 20 |
| **Pooled** | **0** | **0** | **0** | **0** | **0** | **0** | **2** | **13** | **34** | **8** | **13** | **10** | **17** | **13** | **6** | **6** | **8** | **7** | **3** | **4** | **425** |

## Headline interpretation

- Pooled median NN distance: **449.5 m**; tight tail (5th percentile): **83.2 m**.
- **0.0%** of mounds have a nearest neighbour within 50 m (the operating point where the F1 plateau emerges); **10.0%** are within 100 m.

Interpret the match-zone overlap risk by comparing the NN distance against twice the buffer radius (i.e. the buffer *diameter*). For a 50 m buffer diameter (25 m radius), truth buffers begin to overlap when NN < 50 m; at NN < 25 m, truth centres lie inside each other's buffers.
