# Session 59 Plan: Final Statistical Analysis and Paper Preparation

**Created**: 2026-03-26, end of Session 58
**Status**: All API work complete. Remaining work is local analysis
(sapphire) and documentation.

---

## 1. Define Pairwise Comparison Families for FDR

**Priority**: First — everything else depends on this.

The preregistration requires Benjamini-Hochberg FDR correction at q=0.05
across pairwise comparisons within each analysis family. We need to:

1. **Group existing comparisons into families.** Proposed families:
   - *Consensus quality*: HIGH vs MINIMAL, text vs image, N=5 vs N=10 vs
     N=30, T=0.7 vs T=1.0 (the existing 17 pairwise tests)
   - *Verifier model*: Pro vs Flash minimal, Flash minimal vs medium vs
     HIGH (the new PV comparisons)
   - *PV vs consensus-only*: best PV vs best consensus at matched
     conditions

2. **Decide what additional comparisons are needed** for the paper
   (the gap matrix — item 6 below). Add these to the appropriate family
   before computing FDR.

3. **Important**: FDR correction must be applied to the *complete* family,
   not incrementally. So define the full set of comparisons first, run
   them all, then correct.

**Key risk**: The Pro verifier p=0.019 and N=10 vs N=5 p=0.025 are near
the threshold. With ~20 tests in a family, BH correction may push these
above 0.05. Be prepared for this — it's an honest result.

**Script**: Use `pairwise_permutation_test.py --mode pv` for all new PV
comparisons. For consensus comparisons, either use `--mode consensus` or
re-run the existing comparisons with the new script for methodological
consistency (recommended — see item 3).

---

## 2. Re-Run All Pairwise Comparisons with New Script

**Priority**: High — needed for consistency before FDR.

The 17 existing pairwise results in `results/h11-384-pairwise-n5/` use
the old macro-average sign-flip method. The new script uses micro-average
tile-swap (E45). For the paper, all comparisons should use the same
method.

**Approach**: Write a batch shell script that re-runs all 17 existing
comparisons plus the new PV comparisons using
`pairwise_permutation_test.py`. This replaces the old results with
methodologically consistent ones.

**Key data for re-running existing consensus comparisons**: The old JSON
files contain `condition_a.study_dir`, `condition_a.config`, and labels
that can be parsed to reconstruct the invocations. Alternatively, the
to-do list (planning/to-do.md, lines 190–211) has the full comparison
list with results.

**Expected outcome**: ΔF1 values will change (macro→micro), p-values
will change. Directions should be preserved. Some borderline results
may flip significance.

**Run on sapphire.**

---

## 3. Additional PV Pairwise Comparisons

**Priority**: High — needed before FDR.

We only have 2 PV pairwise tests. The paper needs at least:

| Comparison | Purpose |
|-----------|---------|
| Best PV (Flash HIGH text 16-of-30 + Flash min vf) vs best consensus-only (Flash HIGH text 26-of-30) | Does the verifier add significant value over consensus alone? |
| Flash HIGH text 4-of-5 + PV vs Flash HIGH text 4-of-5 consensus-only | Same question at N=5 |
| Flash MINIMAL T=0.7 4-of-5 + PV vs Flash HIGH text 4-of-5 + PV | Does proposer thinking level matter in PV? |
| Pro HIGH text 3-of-5 + Pro vf vs Flash HIGH text 4-of-5 + Flash min vf | Full Pro pipeline vs full Flash pipeline |

**Data**: All the detection GeoDataFrames needed for these comparisons
can be built from the existing probabilities.json + manifest + threshold
combinations. Use `--mode pv` for PV conditions and `--mode consensus`
(or `--mode geojson` with the consensus GeoJSONs) for consensus-only.

**Complication**: Comparing PV results to consensus-only results requires
care. PV results are filtered by a probability threshold on individual
candidates. Consensus-only results are filtered by a vote threshold on
clusters. The comparison is valid (both produce a detection set evaluated
against the same ground truth) but the paper should note the different
filtering mechanisms.

---

## 4. Apply FDR Correction

**Priority**: After items 1–3 (all p-values must be final).

**Method**: Benjamini-Hochberg at q=0.05. Apply within each family
defined in item 1.

**Implementation**: Simple — collect all p-values from the pairwise
result JSONs within a family, apply BH correction using
`scipy.stats.false_discovery_control()` or a manual implementation,
report adjusted p-values alongside originals.

**Output**: A summary table per family showing original p, adjusted p,
and whether the result survives correction. Add to the consolidated
results report.

---

## 5. Compute Tile-Level MCC

**Priority**: Medium — preregistered secondary outcome.

**What**: Matthews Correlation Coefficient at tile level. For each tile,
classify as positive (≥1 detection within buffer of a reference) or
negative (no detections near references). Compare against ground truth
(tile has ≥1 reference mound or not).

**Conditions to evaluate**: Top 5-10 from the leaderboard, plus the
best N=5 conditions and the best consensus-only condition.

**Script**: Could extend `lib_advanced_metrics.py` with a
`compute_tile_level_mcc()` function, or write a standalone analysis.
The per-tile TP/FP/FN from `compute_per_tile_tp_fp_fn()` provides the
inputs — tiles with TP>0 or FP>0 are predicted positive; tiles with
FN>0 (but TP=0) are predicted negative but actually positive.

**Run on sapphire.**

---

## 6. Gap Matrix Review

**Priority**: Do alongside item 1.

Systematic check: what comparisons does the paper need?

**Suggested paper structure for results:**

- H1 (modality): text vs image at matched conditions → already have
- H3 (consensus): N=5 vs N=10 vs N=30 → already have (consensus sweeps)
- H7 (temperature): T=0.7 vs T=1.0 → already have
- H9 (diversity): A vs B/C/D/E → already have (null result)
- H11 (tile size): 384 vs 512 single-pass → need T=0.0 rerun comparison
- PV pipeline: consensus-only vs PV → need pairwise tests (item 3)
- Verifier model: Pro vs Flash → have (p=0.019)
- Verifier thinking: minimal vs medium vs HIGH → have (ns)
- Buffer sensitivity: 20/30/40/50m → have (Obs 190, 193)
- Operating points: precision/recall bookends → have (Obs 193)
- Cross-modal: text vs image union → have (not worthwhile, Obs 191)

**Likely gaps**:
- H11 (tile size): The corrected T=0.0 single-pass rerun needs comparing
  to the 512px baseline from Phase 2. This is a consensus sweep comparison,
  not a pairwise test.
- H2 (proposer-verifier): The preregistered hypothesis about two-stage
  pipelines. The PV results are the data, but the specific preregistered
  comparison (does verification improve over single-stage?) needs a formal
  pairwise test.

---

## 7. Update Documentation

**Priority**: After items 1–5.

- Update Obs 194 ✓ (done this session — corrected p=0.013 → p=0.019)
- Update consolidated results report with FDR-corrected p-values
- Add Obs 196+ for MCC results and FDR findings
- Final update to to-do marking everything complete

---

## 8. Commit and Prepare for Paper Writing

**Priority**: Last.

- Commit all Session 59 work (new pairwise results, MCC, FDR,
  updated reports)
- Run `generate_pv_sweep_summaries.py` on any new sweep results
- Update `consolidate_pv_bootstrap_cis.py` output
- Final `ruff check` and `markdownlint` on all modified files
- Verify git status is clean for tracked files

---

## Execution Strategy

Items 1–3 can be prepared as a single batch script that runs all
pairwise comparisons on sapphire (~30 min for ~25 comparisons at
10,000 permutations each). Item 4 (FDR) is a 1-minute post-processing
step. Item 5 (MCC) is another sapphire batch job (~10 min).

**Suggested workflow**:
1. Design the comparison families and list all comparisons (local, ~30 min)
2. Write and launch the batch pairwise script on sapphire (~30 min compute)
3. While sapphire runs: write MCC computation script
4. Launch MCC on sapphire
5. Apply FDR when all p-values are in
6. Update documentation
7. Commit

Total: ~2–3 hours of active work.

---

## Key Files

| File | Role |
|------|------|
| `scripts/pairwise_permutation_test.py` | Generalised pairwise test (E45 method) |
| `scripts/analyse_pv_buffer_sensitivity.py` | Buffer sensitivity evaluation |
| `scripts/lib_advanced_metrics.py` | Core spatial matching and bootstrap |
| `results/h11-384-pv-diagnostic/` | All PV sweep results (132 conditions) |
| `results/h11-384-pairwise-n5/` | Existing pairwise results (to be replaced) |
| `reports/results-summary-session-58.md` | Consolidated report (to be updated) |
| `planning/to-do.md` | Master to-do list |
