# Pairwise Comparison Strategy for Paper

## Context

`metrics_master.json` contains 25 distinct configurations (condition × pool
size) evaluated at 4 spatial buffers. The theoretical maximum is 300 pairwise
comparisons at a single buffer distance — far too many to run or interpret.
This proposal defines a structured, hypothesis-driven comparison plan that
answers the paper's research questions while keeping the multiple-comparisons
burden manageable.

## Principles

1. **Hypothesis-driven, not exhaustive.** Every comparison must answer a
   specific research question. No "compare everything to everything."
2. **Confirmatory and exploratory separated.** Preregistered hypotheses get
   FDR correction as a family. Exploratory comparisons are reported
   separately without FDR pooling.
3. **One tool, one method.** Use `pairwise_permutation_test.py` (10,000
   tile-swap permutations, micro-average F1, two-sided) for all comparisons.
   This replaces both the pseudo-p-value bootstrap in
   `analyse_phase2_results.py` and the separate bootstrap effect-size script.
   Bootstrap CIs are still reported for effect magnitude, but significance
   comes from the permutation test.
4. **Primary buffer: 30m.** The audit confirmed 30m as the defensible
   primary tolerance (~1 symbol radius). Run confirmatory comparisons at 30m.
   Report 20m in a sensitivity table but do not use it as the primary.
5. **Run on sapphire.** All comparisons are computationally cheap
   (seconds each) but should run there per project conventions.

## Comparison Groups

### Group 1: Pipeline Architecture (H2 — Confirmatory)

**Question:** Does the proposer-verifier pipeline outperform consensus-only?

Compare each PV condition against its matched consensus baseline (same
proposer, same consensus threshold, without verification filtering). This
isolates the verifier's contribution.

| # | Condition A (PV) | Condition B (consensus) | Isolates |
|---|-----------------|------------------------|----------|
| 1 | flash-high-text-16-of-30--flash-min-vf | flash-high-text N=30 26-of-30 | Verifier effect (N=30 text) |
| 2 | flash-high-text-9-of-10--flash-min-vf | flash-high-text N=10 9-of-10 | Verifier effect (N=10 text) |
| 3 | flash-high-text-4-of-5--flash-min-vf | flash-high-text N=5 5-of-5 | Verifier effect (N=5 text) |
| 4 | flash-high-text-4-of-5--flash-medium-vf | flash-high-text N=5 5-of-5 | Verifier thinking level |
| 5 | flash-high-image-3-of-5--flash-min-vf | flash-high-image N=5 3-of-5 | Verifier effect (image) |
| 6 | pro-high-text-3-of-5--flash-min-vf | pro-high-text N=5 3-of-5 | Verifier effect (Pro) |
| 7 | text-baseline--flash-min-vf | single-pass-t0 N=5 5-of-5 | Verifier on single-pass text |
| 8 | image-baseline--flash-min-vf | single-pass-t0 N=5 5-of-5 | Verifier on single-pass image |

**Expected outcome:** PV consistently improves F1 over consensus-only,
primarily via precision gains. 8 comparisons.

### Group 2: Modality Effect (H1 — Confirmatory)

**Question:** Does text-only outperform image-inclusive detection?

Compare text vs image at matched pipeline stages and configurations.

| # | Condition A (text) | Condition B (image) | Context |
|---|-------------------|---------------------|---------|
| 9 | flash-high-text N=5 5-of-5 | flash-high-image N=5 3-of-5 | Consensus, HIGH, N=5 |
| 10 | flash-high-text N=10 9-of-10 | flash-high-image N=10 6-of-10 | Consensus, HIGH, N=10 |
| 11 | flash-min-text-t07 N=5 5-of-5 | flash-min-image N=5 4-of-5 | Consensus, MINIMAL, N=5 |
| 12 | flash-high-text-4-of-5--flash-min-vf | flash-high-image-3-of-5--flash-min-vf | PV pipeline |

**Note:** Thresholds differ between text and image conditions (e.g., 5-of-5
vs 3-of-5) because each uses its own optimal threshold from the consensus
sweep. This is correct — we compare each modality at its best operating point,
not at a forced common threshold. 4 comparisons.

### Group 3: Thinking Level Effect (Confirmatory)

**Question:** Does HIGH thinking outperform MINIMAL?

| # | Condition A (HIGH) | Condition B (MINIMAL) | Context |
|---|-------------------|----------------------|---------|
| 13 | flash-high-text N=5 5-of-5 | flash-min-text-t07 N=5 5-of-5 | Text, N=5 |
| 14 | flash-high-text N=10 9-of-10 | flash-min-text-t07 N=10 10-of-10 | Text, N=10 |
| 15 | flash-high-text N=30 26-of-30 | flash-min-text-t07 N=30 29-of-30 | Text, N=30 |
| 16 | flash-high-image N=5 3-of-5 | flash-min-image N=5 4-of-5 | Image, N=5 |

4 comparisons.

### Group 4: Temperature Effect (H7 — Confirmatory)

**Question:** Does T=0.7 outperform T=1.0 for MINIMAL thinking?

| # | Condition A (T=0.7) | Condition B (T=1.0) | Context |
|---|--------------------|--------------------|---------|
| 17 | flash-min-text-t07 N=5 5-of-5 | flash-min-text-t10 N=5 5-of-5 | N=5 |
| 18 | flash-min-text-t07 N=10 10-of-10 | flash-min-text-t10 N=10 9-of-10 | N=10 |
| 19 | flash-min-text-t07 N=30 29-of-30 | flash-min-text-t10 N=30 22-of-30 | N=30 |

3 comparisons.

### Group 5: Model Platform (Confirmatory)

**Question:** Does Pro outperform Flash at matched configs?

| # | Condition A (Pro) | Condition B (Flash) | Context |
|---|------------------|---------------------|---------|
| 20 | pro-high-text N=5 3-of-5 | flash-high-text N=5 5-of-5 | Text, HIGH, N=5 |
| 21 | pro-high-image N=5 3-of-5 | flash-high-image N=5 3-of-5 | Image, HIGH, N=5 |
| 22 | pro-high-text-3-of-5--flash-min-vf | flash-high-text-4-of-5--flash-min-vf | PV text |

3 comparisons.

### Group 6: Top-N Distinguishability (Exploratory)

**Question:** Are the top-performing configurations statistically
distinguishable from each other?

This is the group the audit flagged as missing. Compare the best condition
against each runner-up to determine which configurations belong to the same
statistical tier.

| # | Condition A | Condition B | Gap (F1) |
|---|------------|------------|----------|
| 23 | flash-high-text-16-of-30--flash-min-vf (0.904) | flash-high-text-4-of-5--flash-min-vf (0.891) | 0.014 |
| 24 | flash-high-text-16-of-30--flash-min-vf (0.904) | flash-high-text-4-of-5--flash-medium-vf (0.885) | 0.019 |
| 25 | flash-high-text-16-of-30--flash-min-vf (0.904) | flash-high-text-9-of-10--flash-min-vf (0.869) | 0.035 |
| 26 | flash-high-text-16-of-30--flash-min-vf (0.904) | pro-high-text-3-of-5--flash-min-vf (0.865) | 0.040 |
| 27 | flash-high-text-4-of-5--flash-min-vf (0.891) | flash-high-text-4-of-5--flash-medium-vf (0.885) | 0.006 |
| 28 | flash-high-text-4-of-5--flash-min-vf (0.891) | flash-high-text-9-of-10--flash-min-vf (0.869) | 0.022 |

**Expected outcome:** The top 2–3 PV conditions are statistically
indistinguishable. The paper should report them as a tier ("F1 = 0.89–0.90")
rather than claiming one specific configuration is best. 6 comparisons.

### Group 7: Consensus Pool Size (H3 — Confirmatory)

**Question:** Does increasing pool size improve performance?

| # | Condition A (larger pool) | Condition B (smaller pool) | Context |
|---|--------------------------|---------------------------|---------|
| 29 | flash-high-text N=10 9-of-10 | flash-high-text N=5 5-of-5 | HIGH text, N=10 vs 5 |
| 30 | flash-high-text N=30 26-of-30 | flash-high-text N=10 9-of-10 | HIGH text, N=30 vs 10 |
| 31 | flash-min-text-t07 N=10 10-of-10 | flash-min-text-t07 N=5 5-of-5 | MIN text, N=10 vs 5 |
| 32 | flash-min-text-t07 N=30 29-of-30 | flash-min-text-t07 N=10 10-of-10 | MIN text, N=30 vs 10 |

4 comparisons.

---

## Summary

| Group | Question | N | FDR family |
|-------|----------|---|------------|
| 1. Pipeline architecture | PV vs consensus | 8 | Confirmatory |
| 2. Modality | Text vs image | 4 | Confirmatory |
| 3. Thinking level | HIGH vs MINIMAL | 4 | Confirmatory |
| 4. Temperature | T=0.7 vs T=1.0 | 3 | Confirmatory |
| 5. Model platform | Pro vs Flash | 3 | Confirmatory |
| 6. Top-N distinguishability | Best vs runners-up | 6 | Exploratory |
| 7. Consensus pool size | Larger vs smaller | 4 | Confirmatory |
| **Total** | | **32** | 26 confirmatory + 6 exploratory |

## FDR Correction

- **Confirmatory family (Groups 1–5, 7):** 26 comparisons. Apply
  Benjamini-Hochberg at q = 0.05 across this family. Report raw p-value
  and FDR-adjusted p-value for each.
- **Exploratory family (Group 6):** 6 comparisons. Apply BH separately
  at q = 0.05 within this group. Report as exploratory with appropriate
  caveats.
- Use `scipy.stats.false_discovery_control(p_values, method='bh')` for
  both families.

## Reporting

For each comparison, report:
- F1 difference (A − B) with 95% bootstrap CI
- Permutation test p-value (raw and FDR-adjusted)
- Significance indicator: *** (p < 0.001), ** (p < 0.01), * (p < 0.05),
  ns (not significant after FDR)

For Group 6, additionally report which conditions are **statistically
indistinguishable** (FDR p ≥ 0.05) and group them into tiers. If the top
2–3 conditions are indistinguishable, report the tier range (e.g.,
"F1 = 0.89–0.90, 95% CI [0.86, 0.93]") rather than claiming one best
configuration.

## Execution

All 32 comparisons use `pairwise_permutation_test.py` with:
- `--buffer-metres 30` (primary)
- `--n-permutations 10000`
- `--seed 42`
- Appropriate `--mode` (pv, consensus, or geojson) per condition type

Run on sapphire. Estimated time: ~32 × 5 seconds = ~3 minutes total.

After all 32 comparisons complete, collect the 32 p-values and apply FDR
correction in a consolidation step. Write results to
`results/paper-tables/pairwise_comparisons.json`.

Optionally repeat at 20m buffer for sensitivity analysis (not
FDR-corrected — reported as a supplementary table to show tolerance
robustness).

## Implementation Notes

- The `pairwise_permutation_test.py` script requires explicit `--mode`
  and condition-specific flags. A wrapper script or YAML config
  defining all 32 comparisons would avoid manual CLI invocations.
- The existing `compute-pairwise-effect-sizes.py` has 54 pre-defined
  comparisons (Groups A–G) using bootstrap CIs. These overlap
  substantially with Groups 1–5 above. The bootstrap CIs from that
  script can be reused for effect magnitude reporting, but significance
  should come from the permutation test p-values.
- The pseudo-p-value FDR in `analyse_phase2_results.py` (lines 199–210)
  should be retired. See the companion explanation in the audit report
  (`reports/adversarial-audit-report.md`, Layer 8, Check 39) for why.
