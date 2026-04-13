# Verifier Independence Probe — H10/H12

Buffer for cross-config spatial clustering: **20 m** (matches the evaluation buffer).

## Verdict: **H-A**

Set divergence: configs propose substantially different candidate pools; equivalence is averaged-out at the F1 level rather than pointwise.

## Set overlap

- Total cross-config clusters: **2352**
- Pooled per-config candidate rows: **6959**
- Clusters present in all 5 configs: **835**
- Clusters unique to a single config: **851**
- Fraction of pooled rows lying in full-overlap clusters: **0.600**
- Intra-config collisions (>1 candidate from a config in one cluster): **346**

### Sharing distribution

| Configs sharing | Cluster count |
|---|---|
| 1 | 851 |
| 2 | 275 |
| 3 | 181 |
| 4 | 210 |
| 5 | 835 |

## Pointwise probability comparison (complete cases)

- Complete-case clusters: **835**
- ICC(2,1) absolute agreement: **0.9321**
- Maximum pairwise mean absolute difference: **0.0683**

### Per-config probability moments (complete cases)

| Config | Mean | SD |
|---|---|---|
| pool_160_hp4hn4 | 0.3616 | 0.4323 |
| pool_160_hp2hn6 | 0.3669 | 0.4369 |
| pool_160_hp6hn2 | 0.3749 | 0.4397 |
| pool_160_hp8hn8 | 0.3703 | 0.4372 |
| pool_160_hp16hn16 | 0.3687 | 0.4367 |

### Pairwise correlations and differences

| Pair | n | Pearson r | Mean abs diff | Mean diff |
|---|---|---|---|---|
| pool_160_hp4hn4 vs pool_160_hp2hn6 | 1063 | 0.9299 | 0.0552 | -0.0039 |
| pool_160_hp4hn4 vs pool_160_hp6hn2 | 1025 | 0.9345 | 0.0559 | -0.0130 |
| pool_160_hp4hn4 vs pool_160_hp8hn8 | 1065 | 0.9379 | 0.0534 | -0.0079 |
| pool_160_hp4hn4 vs pool_160_hp16hn16 | 1035 | 0.9183 | 0.0643 | -0.0091 |
| pool_160_hp2hn6 vs pool_160_hp6hn2 | 1035 | 0.9448 | 0.0484 | -0.0068 |
| pool_160_hp2hn6 vs pool_160_hp8hn8 | 1059 | 0.9462 | 0.0483 | -0.0033 |
| pool_160_hp2hn6 vs pool_160_hp16hn16 | 1039 | 0.9213 | 0.0591 | -0.0054 |
| pool_160_hp6hn2 vs pool_160_hp8hn8 | 1033 | 0.9487 | 0.0478 | +0.0037 |
| pool_160_hp6hn2 vs pool_160_hp16hn16 | 1031 | 0.9263 | 0.0607 | +0.0032 |
| pool_160_hp8hn8 vs pool_160_hp16hn16 | 1043 | 0.9384 | 0.0526 | +0.0008 |

## Per-config sweep optima

| Config | vote_t | prob_t | F1 | P | R |
|---|---|---|---|---|---|
| pool_160_hp4hn4 | 6 | 0.15 | 0.8853 | 0.9133 | 0.8589 |
| pool_160_hp2hn6 | 7 | 0.20 | 0.8849 | 0.9308 | 0.8433 |
| pool_160_hp6hn2 | 7 | 0.20 | 0.8699 | 0.9167 | 0.8276 |
| pool_160_hp8hn8 | 7 | 0.20 | 0.8820 | 0.9244 | 0.8433 |
| pool_160_hp16hn16 | 6 | 0.15 | 0.8853 | 0.9133 | 0.8589 |

Distinct (vote_t, prob_t) optima across configs: **2**
