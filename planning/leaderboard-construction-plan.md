# Leaderboard Construction Plan

**Created**: 2026-04-16
**Status**: In progress — condition inventory COMPLETE, consensus building next
**Decision reference**: Obs 242 (working-notes.md)

## Goal

Build comprehensive, reproducible leaderboards for the paper and supplemental
materials. All leaderboards use greedy consensus as the primary aggregation,
report F1 / precision / recall / bootstrap CIs at multiple spatial tolerances
(20 m, 30 m, 40 m, 50 m), and group conditions into statistically
distinguishable tiers via round-robin tile-level paired permutation tests
with BH-FDR correction.

## Evaluation scopes

Three production test tile sets (fully nested, documented in
`results/evaluation-scopes.md`):

| Era | Tiles | Tile size | Stride | GT mounds | Coverage of Era 1 |
|---|---|---|---|---|---|
| 1 | 340 | 512 px | 448 px | 539 | 100% |
| 2 | 487 | 384 px | 336 px | 435 | 80.8% |
| 3 | 327 | 384 px | 336 px | 319 | 59.0% |

Plus the 55-map generalisation set (separate, not part of the leaderboard).

## Construction stages

### Stage 1 — Per-era leaderboards (primary analysis)

Pure within-era comparisons. No cross-era caveats needed.

**1a. 512-px leaderboard** (Era 1, 340 tiles)

- Source: `outputs/retest/phase2a..3c` (H1–H9 retest)
- Bounds: `inputs/vectors/bounds/full_evaluation_bounds.geojson`
- All conditions share the same tile grid → tile-level pairing is clean
- Hypotheses covered: H1 modality, H3 consensus, H4 ordering, H5 neg text,
  H7 temperature, H8 library (original scale-4..8), H9 diversity

**1b. 384-px leaderboard** (Era 2 + Era 3 merged, 327-tile pairing)

- Era 2 source: `outputs/h11/` (H11 tile-size, PV diagnostic, consensus)
- Era 3 source: `outputs/h8-v2/`, `outputs/h10/`, `outputs/h12-v2/`
- Bounds for pairing: `inputs/vectors/bounds/384/h10_test_bounds.geojson`
  (327 tiles — the intersection of Era 2 and Era 3)
- Era 2 conditions evaluated on 487 tiles are restricted to the 327 shared
  tiles when paired against Era 3 conditions
- Hypotheses covered: H8 v2 (library composition), H10 v2 (pool size),
  H11 (tile size, PV, consensus N-sweep), H12 v2 (HP:HN ratio)

### Stage 2 — Consolidated cross-era leaderboard (secondary analysis)

Spatial re-tiling of Era 1 detections from 512-px to 384-px grid.

- Strip `source_tile` from Era 1 consensus GeoJSONs
- Evaluate against 384-px `h10_test_bounds.geojson` (327 tiles) — scripts
  auto-assign tiles via spatial join
- Merge with Stage 1b conditions → single unified leaderboard
- **Must be flagged as secondary analysis** with prominent caveats:
  - Tile-size context effect (VLM saw 512-px windows, not 384-px)
  - H11 bridge quantifies the confound
  - Write-up text: "Conditions originally run at 512 px were spatially
    re-assigned to the 384-px grid for tile-level pairing; the tile-size
    effect on F1 is quantified separately in the H11 analysis (§X.X)."

## Leaderboard format

### Architecture categories

| | No PV | +PV verifier |
|---|---|---|
| **Single-pass** | mean-of-K F1 | mean-of-K F1 after verifier filter |
| **Consensus** | best (N, t) | best (N, t, verifier threshold) |

× tracks: **text, image, combined/overall**

Within each category, report all configurations that appear in the **top 20
by F1 at any spatial tolerance** (union across 20 m / 30 m / 40 m / 50 m).

### Per-condition columns

- Condition name / label
- Era (1 / 2 / 3)
- Tile size (512 / 384)
- Track (text / image)
- Architecture (single-pass / consensus / consensus+PV)
- K (number of proposer passes)
- Consensus threshold t (or "N/A" for single-pass)
- F1 [95% CI] at each buffer (20, 30, 40, 50 m)
- Precision, Recall at each buffer
- Token count (per tile, total)
- Cost ($ at Flex tier, excluding context caching)
- Tier assignment (from FDR-grouped round-robin)

### Sweep convention — consensus AND verifier thresholds

**Consensus sweep**: For every K > 1 condition, evaluate at ALL consensus
thresholds (1-of-K through K-of-K). Each threshold trades recall (lower
threshold = more detections = higher recall, lower precision) against
precision (higher threshold = fewer detections = higher precision, lower
recall). The leaderboard reports both the optimal-F1 threshold AND the
full sweep curve.

- K=3: evaluate at t=1, 2, 3
- K=5: evaluate at t=1, 2, 3, 4, 5
- K=10: evaluate at t=1, 2, ..., 10
- K=30: evaluate at t=1, 2, ..., 30

**Verifier threshold sweep**: For every condition with PV data, sweep the
verifier probability threshold from 0.0 to 1.0 (step 0.05). If consensus
is also available, the full 2D sweep (consensus_t × verifier_prob) gives
the complete operating-point surface (as demonstrated in Obs 241 for
Scale-4 vs Scale-8).

**Spatial buffer sweep**: Evaluate every condition × threshold at
20 m, 30 m, 40 m, 50 m buffer distances. This is "free" (no API cost,
just evaluation compute) and gives readers the sensitivity of results to
the matching tolerance assumption.

**What appears on the leaderboard**: each condition's BEST operating point
(optimal consensus threshold and/or verifier threshold by F1 at each
buffer). The full sweep data goes in supplemental materials so readers
can navigate the precision/recall trade-off themselves.

### Tiering method

1. Select top-20 conditions (by F1 at any buffer) within a category
2. Run all C(20,2) = 190 tile-level paired permutation tests (10,000
   permutations, seed 42) at the primary buffer (20 m)
3. Apply BH-FDR at q = 0.05
4. Group into tiers: conditions within the same tier are statistically
   indistinguishable (all pairwise adjusted p ≥ 0.05)
5. Repeat tiering at each buffer for supplemental (or use 20 m as primary
   and note consistency across buffers)

## Concrete execution steps

### Step 1: Condition inventory

Systematic crawl of all production-scope conditions:

- [ ] `outputs/retest/` — list every condition with detection file paths
- [ ] `outputs/h11/` — list H11 conditions (pv-diag-384, n1-outstanding, etc.)
- [ ] `outputs/h8-v2/`, `outputs/h10/`, `outputs/h12-v2/` — list all v2 conditions
- [ ] Assign each condition: era, track, architecture category, K, config name
- [ ] Estimate total number of conditions per category

**Output**: `planning/condition-inventory.json` (machine-readable, 144 conditions)
**Script**: `scripts/build_condition_inventory.py` (reproducible)
**Status**: ✅ COMPLETE (2026-04-16)

**Summary**: 144 total conditions (96 Era 1, 34 Era 2, 14 Era 3).
137 eligible for leaderboard. 88 need consensus building (~21 min on sapphire).
27 are single-pass only (K=1). 8 PV-ready (v1 verifier). 6 quarantined (v2 verifier).
See `planning/condition-inventory.json` for full machine-readable inventory

### Step 2: Verify / build greedy consensus (full sweep for every condition)

For EVERY condition with K > 1, we need **all consensus thresholds** from
1-of-K through K-of-K. This enables:
- Finding the optimal operating point per condition
- Understanding the precision/recall trade-off at each consensus level
- Tuning for application needs (e.g., high-recall survey vs high-precision verification)

- [ ] Run `merge_passes.py --sweep` for all 81 NEEDS_CONSENSUS conditions
      (produces consensus_t1..tK for each)
- [ ] Verify existing consensus outputs cover full threshold range (some H11
      conditions only have the t=1 union — need full sweeps)
- [ ] Verify all consensus GeoJSONs use correct CRS (EPSG:32635 internally,
      EPSG:4326 in GeoJSON per RFC 7946)

**Compute**: sapphire, ~30 min estimated

### Step 3: Write general-purpose tiering script

- [ ] `scripts/build_tiered_leaderboard.py` — takes a list of (condition_name,
      geojson_path) pairs + bounds + buffer distances, runs:
  1. `evaluate_detections.py` on each condition at each buffer
  2. Round-robin `pairwise_permutation_test.py` for all pairs at primary buffer
  3. BH-FDR correction
  4. Tier grouping
  5. Output: JSON + formatted markdown table
- [ ] Adapt from `apply_fdr_h8v2.py` + `score_leaderboard_cells.py`

**Effort**: ~1–2 hours

### Step 4: Build Era 1 leaderboard (512-px, 340 tiles)

- [ ] Evaluate all Era 1 conditions at buffers 20/30/40/50 m
- [ ] Round-robin tiering at 20 m (primary)
- [ ] Format leaderboard table
- [ ] Identify top-20 inclusion set (union across buffers)

**Compute**: sapphire, ~1–2 hours (evaluation + permutation)

### Step 5: Build Era 2+3 leaderboard (384-px, 327 tiles)

- [ ] Evaluate all Era 2+3 conditions at buffers 20/30/40/50 m
- [ ] Round-robin tiering at 20 m
- [ ] Format leaderboard table

**Compute**: sapphire, ~1–2 hours

### Step 6: Build consolidated leaderboard (secondary)

- [ ] Re-tile Era 1 consensus GeoJSONs to 384-px grid (strip source_tile)
- [ ] Evaluate on 327-tile 384-px bounds
- [ ] Merge with Step 5 conditions
- [ ] Round-robin tiering across the merged set
- [ ] Format with caveats prominently noted

**Compute**: sapphire, ~2–3 hours (larger condition set)

### Step 7: Cost annotation

- [ ] For each condition, extract token counts from `run.meta.json`
- [ ] Compute per-tile and total cost at Flex tier pricing (excluding cache)
- [ ] Add to leaderboard tables

### Step 8: Supplemental materials

- [ ] N-sweep table (consensus N=5/10/30 per track)
- [ ] Parameter sensitivity tables (T, thinking, tile size)
- [ ] Library-design null table (H8/H10/H12 45-pair matrix from Obs 240)
- [ ] Verifier strategy comparison (Phase 3d + H11)
- [ ] Greedy vs WBF justification (Obs 241)
- [ ] Pareto frontier (F1 vs cost scatter)

## Open questions

- [ ] Confirm Tier 1 (FH text 16/30 + PV, F1=0.890) was on 487-tile Era 2 scope
- [ ] Decide: do tiering at 20 m only (primary) or at all 4 buffers?
- [ ] Decide: paper body shows which leaderboard(s)? Era-specific or consolidated?
- [ ] Code review: is `evaluate_detections.py` default bounds compatible with
      each era, or must `--bounds` always be passed explicitly?

## Key scripts

| Script | Purpose |
|---|---|
| `scripts/merge_passes.py --sweep` | Greedy consensus t=1..5 |
| `scripts/evaluate_detections.py` | F1/P/R + bootstrap CIs at multiple buffers |
| `scripts/pairwise_permutation_test.py --mode geojson` | Tile-level paired permutation |
| `scripts/build_tiered_leaderboard.py` | **TO WRITE** — orchestrates the full pipeline |
| `scripts/apply_fdr_h8v2.py` | Reference for BH-FDR tiering logic |
| `scripts/score_leaderboard_cells.py` | Reference for existing leaderboard scoring |

## References

- Evaluation scopes: `results/evaluation-scopes.md`
- Archive manifest: `archive/ARCHIVE-MANIFEST.md`
- Decision observation: Obs 242 (working-notes.md)
- Existing leaderboard (to supersede): `results/paper-tables/leaderboard_tiers_20m.md`
- Scale-4 library decision: Obs 241
- Library-design null: Obs 240
- Greedy vs WBF: Obs 241

## Update 2026-04-25 — 12-stratum per-architecture redesign (Session 79)

**Status**: redesign of the per-architecture leaderboard tree under
`results/leaderboard/per-architecture/`. The original Session 79
build (commit `03bf71c8`) is preserved in git history but the live
tree has been regenerated with the additions below.

### Methodology additions (relative to the 2026-04-16 plan)

**1. Parallel F1 + MCC tier tables.** Each populated stratum
produces tier tables under both metrics. Threshold selection still
uses F1 at the primary buffer (20 m) for cross-metric alignment.
The MCC permutation test uses a per-tile (TP, TN, FP, FN)
classification swap; the resulting null distribution was validated
symmetric and zero-centred before launch (see
`docs/methodology/mcc-permutation-validation-2026-04-25.md`).

**2. q=0.01 sensitivity pass.** Each F1 / MCC tier table at q=0.05
has a parallel q=0.01 sensitivity sibling. Larger tier-1 sets at
q=0.05 benefit from a stricter q=0.01 directional inspection; the
two passes share evaluation + pairwise caches so the sensitivity
cost is near-zero.

**3. Tier stability with Spearman rho.** Per-stratum
`tier_stability_<metric>.md` reports the Spearman rank correlation
between tier@20m and tier@30/40/50/100m. MCC is buffer-invariant by
construction (rho = 1.0 always); F1's tier ordering can shift with
buffer.

**4. Cross-architecture flat tables (Stage 4a).** For each (Era,
buffer, metric) triple, a flat 4-row table picks the best tier-1
representative of each architecture column within that Era. 30
files (3 Eras x 5 buffers x 2 metrics).

**5. Cross-architecture paired comparisons (Stage 4b).** Within
each Era, proposer-config tuples (model, config_version,
instruction_file, thinking, T, N, track, vote_t) appearing in 2+
architecture columns are tested pairwise on the shared tiles. This
directly answers the question \"does adding the verifier help on
this proposer config?\" — the obvious paper question. BH-FDR
within Era at q=0.05.

**6. Monte-Carlo precision flagging (Stage 4c).** Pairwise tests
where the observed null-difference count is <= 5 (i.e.,
p <= 5/N) are catalogued in `mc-precision-flags.md`. Tests at
p == 0/N have only the conclusion \"p < 1/N\".

**7. --top-n 0 ("include all conditions").** The original build
filtered to top-20 at any buffer; the redesign uses --top-n 0 for
comprehensive paper-table coverage.

**8. Single-pass+PV F1=0 evaluator fix.** The
`outputs/h11/proposer-verifier-384/verified-*.geojson` files have
three pathologies (verified=False rows, polygon footprints, missing
CRS metadata with UTM-magnitude coords labelled EPSG:4326) that the
generic loader did not handle. Fix: detect via the `verified`
column + invalid-geometry signature, then re-read with CRS override,
filter verified=True, polygon -> centroid. All 8 PV_READY single-
pass+PV cells now produce non-zero F1 (was 0.000 in the original
build). See `results/leaderboard/per-architecture/era2/single-pass+PV/`
for the now-interpretable tier tables.

### Output tree (new)

```text
results/leaderboard/per-architecture/
├── README.md                                      (top-level)
├── headlines.md                                   (top-3 per stratum)
├── mc-precision-flags.md                          (Stage 4c)
├── cross-architecture-era<N>_<buf>m_<metric>.md   (Stage 4a, 30 files)
├── cross-architecture-paired-era<N>_<metric>.md   (Stage 4b, 6 files)
├── era<N>/<arch>/                                 (12 strata)
│   ├── README.md                                  (per-stratum summary)
│   ├── leaderboard_tiers_<buf>m.{md,json}         (F1 tier, q=0.05)
│   ├── leaderboard_tiers_q01_<buf>m.{md,json}     (F1 tier, q=0.01)
│   ├── leaderboard_tiers_mcc_<buf>m.{md,json}     (MCC tier, q=0.05)
│   ├── leaderboard_tiers_mcc_q01_<buf>m.{md,json} (MCC tier, q=0.01)
│   ├── leaderboard_all_evaluations.json           (sweep)
│   ├── tier_stability.md                          (F1 buffer rho)
│   └── tier_stability_mcc.md                      (MCC buffer rho)
└── archive/                                       (prior caches)
```

### Within-stratum FDR caveat

BH-FDR is applied within stratum: each (Era, Architecture, Buffer,
Metric) family is corrected independently. Cross-stratum claims
(e.g. \"Era 1 best vs Era 2 best\") have inflated family-wise error
rate and are descriptive only; paper-citation should use within-
stratum claims primarily.

### Driver script

`scripts/build_per_arch_redesign.sh` runs the 7 populated strata x
4 passes (F1@q05, F1@q01, MCC@q05, MCC@q01) sequentially, with
each pass using 8 internal worker processes for parallel pairwise
testing. Stage 3, 4, 5 scripts:

| Script | Purpose |
|---|---|
| `scripts/build_tier_stability.py` | Spearman rho across buffers |
| `scripts/build_cross_architecture_tables.py` | Stage 4a + 4b + 4c |
| `scripts/build_per_arch_documentation.py` | Stage 5 READMEs + headlines |
