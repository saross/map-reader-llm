# SUPERSEDED 2026-04-24

**Reason**: Decisions finalised and analysis executed.

**See**: `results/gold-standard-subtype-classification/report.md` (executes the finalised decisions)

This document is preserved for audit / historical reference. Its original content follows below.

---

## Gold-standard classification metrics — decision record

**Date**: 2026-04-20
**Context**: Metric-set decisions for the subtype-classification accuracy analysis on the 4-map gold-standard subset. See `gold-standard-classification-accuracy-plan.md` for the full analysis plan; this file records the decisions that were resolved before execution.
**Source**: `/review-implementation` skill invoked on the plan's §3 metric shortlist, 2026-04-20. Shawn accepted all nine default recommendations without edit.

## Scope

This decision record applies to the classification-accuracy analysis planned for:

- Ground truth: `inputs/vectors/references/reference_*.geojson` (4 maps, 569 features total)
- Predictions: `outputs/h11/gold-standard-v2/consensus/consensus-4of5.geojson` (607 features at default 4/5 consensus)
- Buffer: primary 50 m, sensitivity at 20 m / 30 m
- Class support: burial 455 / benchmark 65 / triangulation 43 / settlement **5** (the sparse class)

## Decisions

| # | Decision | Resolution | Rationale |
|---|---|---|---|
| **D1** | Report a 2-level hierarchical analysis alongside the flat 4-class confusion matrix? Level 1 = mound-family (burial + benchmark + trig) vs settlement; Level 2 = plain / + benchmark marker / + trig marker. | **YES — alongside, as a secondary set of tables.** | Mirrors Obs 266's sub-pattern taxonomy directly: sub-pattern 3 (settlement → burial) is a Level-1 error, sub-pattern 1 (plain → compound) is a Level-2 error. Flat 4-class matrix obscures this. ~10% extra analysis effort. |
| **D2** | Report F-beta variants (F2 for rare-class recall, F0.5 for rare-class precision) alongside F1? | **Partial — F1 only as headline; mention F2 framing for settlement in the discussion section.** | F1 is the expected paper metric. F2 framing comes up naturally when discussing "we found 2 of 5 real tells" — noting it verbally in the text is cheaper than adding F-beta columns everywhere. |
| **D3** | Include a consensus-threshold sweep (3/5, 4/5, 5/5) for subtype accuracy? | **YES.** | Cheap to compute (~10 min extra on sapphire); directly tests whether vote-share carries subtype-correctness signal, analogous to the verifier-calibration analysis just completed (Obs 269). Likely shows higher consensus = higher accuracy. |
| **D4** | Report both row-normalised and column-normalised heat maps of the confusion matrix in the paper figure? | **YES.** | Row-normalised (P(predicted \| GT)) shows per-class recall perspective; column-normalised (P(GT \| predicted)) shows per-class precision perspective. Obs 266 sub-pattern 1 (over-assignment) is a precision-angle finding; sub-pattern 3 (under-assignment) is a recall-angle finding. Paper figure needs both perspectives. |
| **D5** | Adopt a cost-weighted kappa or custom archaeological cost matrix (weighting "settlement → burial" as more costly than "benchmark → burial")? | **NO for the headline analysis; optional in discussion.** | Adds argument surface (cost matrix choices can be contested) without changing the main findings. Report raw cells and let readers interpret. |
| **D6** | Bootstrap resample unit for classification metrics: tile-level or matched-pair-level? | **Matched-pair-level** (stratified by map for variance) for classification metrics. Tile-level is retained for detection-level metric reproduction where that unit is correct. | Classification-given-matched is a per-pair property, not a per-tile property. Tile-level bootstrap (inherited from detection F1) would average over within-tile correlation that isn't present for the classification question. Statistical correctness. |
| **D7** | Bootstrap iteration count. | **10,000 throughout** — confusion-matrix cells, per-class F1, weighted/macro-F1, kappa, MCC. | Cost is trivial on sapphire (~30 min total). Unification removes an inconsistency between 1,000 (cells) and 10,000 (summaries) in the original plan draft. |
| **D8** | Kappa variant: unweighted, linearly-weighted, or quadratically-weighted? | **Linearly-weighted Cohen's kappa** (because D1 adopts the hierarchical structure — a Level-1 error is weighted more heavily than a Level-2 error). Also report unweighted for comparison with the broader ML literature. | Default for nominal classes is unweighted; but D1's hierarchical interpretation makes ordering available, so linearly-weighted is defensible. Both are cheap to compute. |
| **D9** | Lead summary metric: macro-F1 or weighted-F1? | **Weighted-F1 as the headline.** Macro-F1 reported as companion. | Settlement n=5 dominates macro-F1 with noise (a single misclassification moves macro-F1 by ~0.05). Weighted-F1 is less distorted for a paper audience reading "overall subtype accuracy" and is more honest for the imbalanced support. |

## Downstream implications for the plan

1. **§3.1 metric shortlist**: adds Level-1 and Level-2 hierarchical tables (D1); consensus-threshold-sweep table at 3/5 / 4/5 / 5/5 (D3); row- and column-normalised heat map specifications (D4); linearly-weighted kappa (D8).
2. **§3.2 deprioritised**: cost-weighted custom kappa moves from "considered" to "explicitly deferred" (D5).
3. **§4.3 bootstrap protocol**: resample unit clarified (D6); iteration count unified at 10,000 (D7).
4. **Headline metric framing**: weighted-F1 named as lead; macro-F1 as companion (D9).

## Reviewer-applicability note

These decisions are tailored to the 4-map gold-standard subset of the map-reader-llm project and its specific class-support profile (455 / 65 / 43 / 5). They are NOT universal best practice for VLM-classification papers. In particular, D5 (no cost-weighted kappa) and D9 (weighted-F1 lead) follow from the specific imbalance structure here; different papers on different corpora might legitimately choose differently.

## History

- 2026-04-20: Initial `/review-implementation` review surfaced the 9 decisions above. Shawn accepted all default recommendations. Decision record written, plan updated accordingly.
