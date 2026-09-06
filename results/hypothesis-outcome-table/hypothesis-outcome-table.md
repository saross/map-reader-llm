# Hypothesis-outcome table

> **GENERATED FILE — do not hand-edit.** Produced by
> `scripts/generate_hypothesis_outcome_table.py` from
> `results/analyses-manifest.json` at commit `c14651930`; re-run the
> script after any manifest regeneration. Pure projection per the
> D17 ruling (`docs/paper/results-outline.md` § D17): no cell is
> hand-maintained.

Labels: vocabulary v2 (`docs/manifest-schemas/analyses-manifest.schema.json`).
`post-hoc` rows never count as execution of a registered
obligation; they are listed as related characterisation. The
family BH-FDR verdict is parsed from the
`family-bh-fdr-confirmatory` row (rejection = the registered H0 rejected at
q = 0.05; for H2 that falsifies the registered no-improvement
prediction — see the row's outcome for interpretation). The
deviations column is the union over the hypothesis's
registered-analysis rows; a family-level row contributes its full
array, so per-hypothesis attribution lives in the errata entries
themselves.

| Hyp | Registered hypothesis | Registered as | Disposition | Family BH-FDR | Registered-analysis rows | Deviations |
|-----|----------------------|---------------|-------------|---------------|--------------------------|------------|
| H1 | Modality and elaboration level (osf:400) | confirmatory | executed | not rejected | family-bh-fdr-confirmatory [confirmatory-with-deviation]; h1-cmt0106-pooled-modality [confirmatory-with-deviation]; image-b-modality-2026-08-28 [registered-exploratory]; image-b-thinking-pair-2026-08-28 [registered-exploratory] | E28, E30, E36, E41, E45, E51, E53, E54, E58, E59, E60, E64 |
| H2 | Two-stage pipelines do not improve detection (osf:451) | confirmatory | partially executed | rejected (q=0.05) | e45-bootstrap-pairings [confirmatory-with-deviation]; family-bh-fdr-confirmatory [confirmatory-with-deviation]; h2-condition-c-fine-to-coarse [not-executed] | E28, E30, E36, E41, E45, E51, E53, E54, E58, E59, E60, E64 |
| H3 | Consensus voting improves F1 (osf:497) | confirmatory | executed | rejected (q=0.05) | diversity-dividend-384 [confirmatory-with-deviation]; e45-bootstrap-pairings [confirmatory-with-deviation]; family-bh-fdr-confirmatory [confirmatory-with-deviation]; phase3a-consensus-calibration [registered-exploratory]; stride55-ladder-2026-08-27 [registered-exploratory] | E28, E30, E32, E36, E41, E45, E49, E51, E53, E54, E56, E58, E59, E60, E64 |
| H4 | Example ordering / canonical placement (osf:534) | confirmatory | executed | not rejected | family-bh-fdr-confirmatory [confirmatory-with-deviation] | E28, E30, E36, E41, E45, E51, E53, E54, E58, E59, E60, E64 |
| H5 | Negative text treatment (osf:578) | confirmatory | executed | not rejected | family-bh-fdr-confirmatory [confirmatory-with-deviation] | E28, E30, E36, E41, E45, E51, E53, E54, E58, E59, E60, E64 |
| H6 | Flash-to-Pro transfer (osf:651) | confirmatory | not executed | — (excluded: never run) | h6-phase4-transfer [not-executed] | E40, E41, E74 |
| H7 | Temperature affects detection (osf:705) | confirmatory | executed | rejected (q=0.05) | family-bh-fdr-confirmatory [confirmatory-with-deviation]; h7-escalation-2026-08-28 [registered-exploratory] | E28, E30, E36, E41, E45, E51, E53, E54, E58, E59, E60, E64 |
| H8 | Library composition and scaling (osf:737) | confirmatory | executed | not rejected | family-bh-fdr-confirmatory [confirmatory-with-deviation] | E28, E30, E36, E41, E45, E51, E53, E54, E58, E59, E60, E64 |
| H9 | Diversity mechanisms in consensus voting (osf:841) | exploratory (Tier A) | executed | — (exploratory: not in family) | phase3c-diversity-calibration [registered-exploratory] | E12, E32, E63 |
| H10 | Training-pool size effects (osf:904) | exploratory (Tier B) | executed | — (exploratory: not in family) | h10-pool-size [registered-exploratory] | E13, E37, E45, E49, E50 |
| H11 | Tile size effects (osf:944) | exploratory (Tier B) | executed | — (exploratory: not in family) | tile-size-sweep [registered-exploratory] | E36, E41, E43, E44, E56, E57, E62 |
| H12 | Hard-positive to hard-negative ratio (osf:980) | exploratory (Tier B) | executed | — (exploratory: not in family) | h12-v2-hp-hn-ratio [registered-exploratory] | E13, E45, E49, E50, E51, E52 |
| H13 | Overlap/stride effects (osf:1014) | exploratory (Tier B) | executed | — (exploratory: not in family) | h13-overlap-2026-08-18 [registered-exploratory]; stride55-ladder-2026-08-27 [registered-exploratory]; stride55-sweep-oracle-2026-08-27 [registered-exploratory] | E54, E66, E75 |
| H14 | Cross-model consistency (osf:1056) | exploratory (Tier C, deferred) | not executed | — (exploratory: not in family) | h14-cross-model-consistency [not-executed] | E76 |
| H15 | Cross-model consensus voting (osf:1074) | exploratory (Tier C, deferred) | not executed | — (exploratory: not in family) | h15-cross-model-voting [not-executed] | E77 |

## Related post-hoc characterisation

| Hyp | Post-hoc rows referencing the hypothesis |
|-----|------------------------------------------|
| H1 | era1-leaderboard [post-hoc]; era1-single-pass-baseline-matrix [post-hoc]; gemini37-image-gs-2026-09-01 [post-hoc]; n1-baseline-matrix-384 [post-hoc] |
| H2 | era1-leaderboard [post-hoc]; flash35-model-roles [post-hoc]; min-vs-high-thinking-pv [post-hoc]; pass-budget-pareto [post-hoc]; pass-budget-pareto-v2 [post-hoc]; unswept-pools-completeness [post-hoc]; verifier-robustness-matrix [post-hoc] |
| H3 | 55map-final-board-2026-08-27 [post-hoc]; era1-leaderboard [post-hoc]; min-vs-high-thinking-pv [post-hoc]; pass-budget-pareto [post-hoc]; pass-budget-pareto-v2 [post-hoc]; phase3a-high-consensus-calibration [post-hoc]; phase3a-replication-thinking-calibration [post-hoc]; pv-diag-384-consensus-calibration [post-hoc]; stride-winner-ladder-exact-2026-08-25 [post-hoc] |
| H4 | era1-leaderboard [post-hoc]; era1-single-pass-baseline-matrix [post-hoc] |
| H5 | era1-leaderboard [post-hoc]; era1-single-pass-baseline-matrix [post-hoc] |
| H6 | h6-a06-decision-rule [post-hoc]; h6-a07-voting-thresholds [post-hoc]; h6-a09-cost-gate [post-hoc] |
| H7 | e43-matched-temperature [post-hoc]; era1-leaderboard [post-hoc]; era1-single-pass-baseline-matrix [post-hoc]; n1-baseline-matrix-384 [post-hoc] |
| H8 | era1-leaderboard [post-hoc]; era1-single-pass-baseline-matrix [post-hoc]; sensitivity-mde-2026-08-28 [post-hoc] |
| H9 | era1-leaderboard [post-hoc]; sensitivity-mde-2026-08-28 [post-hoc] |
| H10 | sensitivity-mde-2026-08-28 [post-hoc] |
| H11 | unswept-pools-completeness [post-hoc] |
| H12 | sensitivity-mde-2026-08-28 [post-hoc] |
| H13 | 55map-final-board-2026-08-27 [post-hoc]; stride-plateau-2026-08-25 [post-hoc]; stride-winner-ladder-exact-2026-08-25 [post-hoc]; stride55-a5-vs-b5-2026-08-27 [post-hoc] |
| H14 | — |
| H15 | — |

## Register rows outside the hypothesis frame

Rows with no H-numbered refs (deployment boards,
methodological re-measurements, and named-programme
dispositions) — part of the register but outside the
H1–H15 reconciliation:

- `55map-canonical-leaderboard-50m`
- `55map-canonical-leaderboard-mcc-50m`
- `55map-standardised-leaderboard-50m`
- `55map-standardised-leaderboard-mcc-50m`
- `gemini37-55map-grid-2026-08-31`
- `gemini37-55map-gridboard-2026-08-31`
- `gemini37-fourth-cell-gs-leg-2026-08-31`
- `gemini37-screen-2026-08-28`
- `gemini38-screen-armv-2026-09-04`
- `grid-postverifier-2026-08-18`
- `grid-tilesize-overlap-2026-08-18`
- `obs280-shared-reference`
- `s8-9-post-experiment-verification`
- `tile-level-f1`
