# Cluster label-heterogeneity — the true E64(iii) materiality figure

> **Last revised**: 2026-07-30 (original publication). See
> [§ Changelog](#changelog) for revision history.

**Status**: apparatus record for erratum E64 sub-item (iii) (the voting
step-4 label clause). Produced under the Principal Investigator (PI)
ruling of 2026-07-30 ("Compute true figure now" —
`reports/verification/phase2-rulings-2026-07-30.md` § 1c). Computed on
sapphire, zero Application Programming Interface (API) cost, from
committed detection GeoJSONs.

**Script**: `scripts/analyse_cluster_label_heterogeneity.py` (imports the
executed pipeline's own primitives — `merge_passes.deduplicate_within_pass`,
its 20 m greedy star clustering semantics, and
`analyse_diversity.load_replication_passes` — so clustering is faithful to
what ran; only member labels are retained instead of collapsed).

**Data**: `reports/verification/apparatus/cluster-label-heterogeneity-2026-07-30.json`
(sapphire run, 2026-07-30).

## 1. Question

The registration's voting step 4 (reading A) would cluster detections on
distance AND matching label; the executed pipeline (reading B, adopted as
operative in E64) clusters spatially and majority-votes the label
post hoc. The readings diverge only where detections within 20 m carry
different subtypes. Previously available figures — 17.2 % (re-verified)
and ~21 % (defence-pass, pool unrecorded) non-`burial_mound` subtype
shares — are loose upper bounds. The true materiality quantities are:

1. the share of spatial clusters whose members disagree on subtype; and
2. at each vote threshold t, the share of spatially-passing clusters
   whose best single-label distinct-pass vote count falls below t — the
   clusters reading A would actually remove (label-split approximation
   of reading A's gate; reading A's own greedy geometry could differ
   marginally near the distance boundary).

## 2. Corpus

47 pools, 153,102 clusters:

- **Era 1** (340 tiles, 512 px): all 45 phase3c H9 diversity pools
  (track1-image A–E × replications 1–5; track2-text A, B, D, E ×
  replications 1–5), N = 5 passes each.
- **Era 2** (487 tiles, 384 px): the `pv-diag-384` flash-high-text pool
  at N = 30 (the 0.890 headline's proposer pool) and its first-5
  sub-pool (N = 5).

## 3. Results

**Headline: 2.21 % of spatial clusters are label-heterogeneous**
(3,390 / 153,102). Era 1: 2.17 % (2,985 / 137,595); Era 2: 2.61 %
(405 / 15,507; 2.76 % at N = 30, 2.14 % at N = 5).

**Threshold impact** (clusters passing spatially at t whose best
single-label vote count < t):

| Corpus | t | affected / passing | share |
|---|---|---|---|
| Era 1 (45 × N=5, aggregate) | 2 | 755 / 44,278 | 1.71 % |
| Era 1 | 3 | 648 / 28,003 | 2.31 % |
| Era 1 | 4 | 1,082 / 20,078 | 5.39 % |
| Era 1 | 5 (unanimous) | 1,272 / 12,785 | 9.95 % |
| Era 2 N=30 | 3 | 49 / 3,072 | 1.60 % |
| Era 2 N=30 | 16 (headline op. point) | 17 / 729 | 2.33 % |
| Era 2 N=30 | 26 (single-stage optimum) | 39 / 415 | 9.40 % |
| Era 2 N=30 | 30 (unanimous) | 43 / 256 | 16.80 % |
| Era 2 N=5 (first 5) | 3 | 20 / 855 | 2.34 % |
| Era 2 N=5 | 5 (unanimous) | 40 / 415 | 9.64 % |

At t = 1 the readings are identical by construction (0 affected,
everywhere).

## 4. Reading

1. **The materiality bound collapses by an order of magnitude**: from
   the 17.2 %/~21 % subtype-share proxies to **2.2 %** cluster-level
   heterogeneity — co-located differing-subtype pairs are much rarer
   than differing subtypes overall, as E64(iii) anticipated.
2. **At the operative thresholds the label gate would touch ~1.6–2.4 %
   of passing clusters** (t = 3 of 5 across both eras; t = 16 of 30 at
   the headline operating point).
3. **The readings diverge most at strict/unanimous thresholds**
   (~10 % at t = 5 of 5 and t = 26 of 30; ~17 % at t = 30 of 30):
   a heterogeneous cluster can pass a strict threshold on combined
   votes while no single label reaches it. Any analysis at
   near-unanimous thresholds inherits the larger gap; the direction of
   reading A's effect is removal (higher precision, lower recall).
4. The defence-pass ~21 % figure remains unanchored (no recorded pool
   or denominator) and is superseded by this computation; the 17.2 %
   subtype share stands as a re-verified descriptive bound only.

## Changelog

### 2026-07-30 — Original publication

Computed on sapphire per the PI's morning ruling (phase2-rulings
§ 1c); 47 pools, 153,102 clusters; headline 2.21 %. Anchored to the
JSON sidecar and script named above.
