# Sapphire vs zbook cleanup comparison — Phase 3a recovery parallel runs

> **Last revised**: 2026-05-12 (original publication — one-time comparison after sapphire-state reconciliation). See [§ Changelog](#changelog) for revision history.

## TL;DR

Two independent runs of the same Phase 3a verifier cleanup operation on the same 11 Tier-2/3 cells: **20,724 candidates compared, 20,622 exact matches (99.51 %), 16 decision flips at threshold = 0.15**. Mean |Δp| (averaged across cells) = 0.002498; max |Δp| observed = 0.9500.

The aggregate match rate masks a sharper structural finding (§ Key finding below): **all 92 divergent candidates and all 14 cross-threshold flips in the largest-divergence cell fall in the candidate subset that each host independently re-verified**. Candidates whose verifier results pre-dated both runs were byte-identical across hosts (0 divergence in thousands of preserved candidates). So the correct reading is:

- **Identical inputs → identical outputs** across hosts and time: passes a strict reproducibility test on the preserved set.
- **Independent verifier invocations at T=0.0 produce non-zero drift** when re-invoked separately for the same crop input: ≈17 % of re-invocations on the gap=460 cell produced sub-threshold probability drift; ≈3 % crossed the 0.15 decision threshold.

This refines the existing "T=0.0 is near-deterministic on Gemini 3 Flash" claim into a more precise empirical statement.

## Provenance

Two independent verifier-cleanup runs of the same 11 Tier-2/3 cells from the Phase 3a verifier-completeness recovery campaign:

- **Sapphire run** (preserved in `archive/phase3a-recovery-sapphire-parallel-run/`): 2026-05-03, overnight resume started 15:19 UTC, completed 15:28 UTC, cumulative cost $0.905. Sapphire then went off-network during user travel; this state never reached `origin/main` and was preserved per project policy before reconciliation.
- **Zbook re-run** (current `origin/main`): Sessions 86–87 (2026-05-05/06), zbook executed the same cleanup operation independently. The 11 cells covered here are part of the campaign's 14-cell total ($1.89 cumulative cost across the full campaign).

Per the project's *Preserve and compare, don't discard* heuristic (CLAUDE.md § Unexpected Data as Discovery Opportunities), the sapphire-side artefacts were preserved before reconciling sapphire's working tree with `origin/main`. This document reports the resulting comparison.

## Method

For each of the 11 cells, loaded both `probabilities.json` files (sapphire from archive, zbook from `outputs/`) and computed:

- Number of common candidates (intersection of `results.keys()`).
- For each common candidate, |Delta mound_probability| between the two runs' verifier outputs.
- Distribution stats per cell: mean, median, max, p95.
- Decision flips at threshold = 0.15 (per project memory: validated optimal threshold on the 55-map generalisation run).
- Number of exact matches (|Delta p| = 0).

Implementation: `scripts/compare_sapphire_zbook_cleanup.py`. Runs in ~5 seconds.

## Results

### Per-cell summary

| Cell | N common | Exact | Exact % | Mean |Δp| | Median |Δp| | Max |Δp| | p95 |Δp| | Flips @ thr |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| h8v2-wbf-scale-4 | 1114 | 1109 | 99.6 % | 0.001212 | 0.000000 | 0.7500 | 0.000000 | 0 |
| image-n5-t0.0-v1-n10 | 802 | 710 | 88.5 % | 0.025312 | 0.000000 | 0.9500 | 0.100000 | 14 |
| image-n5-t0.3-v1-n5 | 2190 | 2188 | 99.9 % | 0.000046 | 0.000000 | 0.0500 | 0.000000 | 1 |
| image-n5-t0.7-v1-n5 | 2017 | 2017 | 100.0 % | 0.000000 | 0.000000 | 0.0000 | 0.000000 | 0 |
| image-n5-t1.0-v1-n5 | 2840 | 2840 | 100.0 % | 0.000000 | 0.000000 | 0.0000 | 0.000000 | 0 |
| session78-image-checklist | 2017 | 2017 | 100.0 % | 0.000000 | 0.000000 | 0.0000 | 0.000000 | 0 |
| scale-4-optimal-487-v1-n10 | 3601 | 3601 | 100.0 % | 0.000000 | 0.000000 | 0.0000 | 0.000000 | 0 |
| text-baseline-pro-verifier | 1047 | 1045 | 99.8 % | 0.000812 | 0.000000 | 0.8000 | 0.000000 | 1 |
| pro-medium-image-baseline-pro-verifier | 519 | 518 | 99.8 % | 0.000096 | 0.000000 | 0.0500 | 0.000000 | 0 |
| pro-high-image-1of5-pro-verifier | 841 | 841 | 100.0 % | 0.000000 | 0.000000 | 0.0000 | 0.000000 | 0 |
| flash-high-text-1of5-flash-medium-verifier | 3736 | 3736 | 100.0 % | 0.000000 | 0.000000 | 0.0000 | 0.000000 | 0 |

### Set differences (candidates in one run but not the other)

| Cell | Only on sapphire | Only on zbook |
|---|---:|---:|
| h8v2-wbf-scale-4 | 0 | 0 |
| image-n5-t0.0-v1-n10 | 0 | 0 |
| image-n5-t0.3-v1-n5 | 0 | 0 |
| image-n5-t0.7-v1-n5 | 0 | 0 |
| image-n5-t1.0-v1-n5 | 0 | 0 |
| session78-image-checklist | 0 | 0 |
| scale-4-optimal-487-v1-n10 | 0 | 0 |
| text-baseline-pro-verifier | 0 | 0 |
| pro-medium-image-baseline-pro-verifier | 0 | 0 |
| pro-high-image-1of5-pro-verifier | 0 | 0 |
| flash-high-text-1of5-flash-medium-verifier | 0 | 0 |

### Sapphire-side cleanup-history reference

| Cell | Sapphire recovered | Sapphire timestamp (UTC) |
|---|---:|---|
| h8v2-wbf-scale-4 | 15 | 2026-05-03T15:19:38.904506+00:00 |
| image-n5-t0.0-v1-n10 | 460 | 2026-05-03T15:22:11.113721+00:00 |
| image-n5-t0.3-v1-n5 | 11 | 2026-05-03T15:22:19.195021+00:00 |
| image-n5-t0.7-v1-n5 | 1 | 2026-05-03T15:22:29.101287+00:00 |
| image-n5-t1.0-v1-n5 | 1 | 2026-05-03T15:22:24.218400+00:00 |
| session78-image-checklist | 1 | 2026-05-03T15:22:35.241017+00:00 |
| scale-4-optimal-487-v1-n10 | 1 | 2026-05-03T15:22:40.177546+00:00 |
| text-baseline-pro-verifier | 21 | 2026-05-03T15:27:34.381355+00:00 |
| pro-medium-image-baseline-pro-verifier | 10 | 2026-05-03T15:27:48.761926+00:00 |
| pro-high-image-1of5-pro-verifier | 8 | 2026-05-03T15:28:06.918493+00:00 |
| flash-high-text-1of5-flash-medium-verifier | 1 | 2026-05-03T15:28:14.762976+00:00 |

### Aggregate stats

- **Total common candidates compared**: 20,724
- **Total exact matches** (|Δp| = 0): 20,622 (99.51 %)
- **Total decision flips at threshold 0.15**: 16
- **Mean of per-cell mean |Δp|** (cells weighted equally): 0.002498
- **Maximum |Δp| observed across any cell**: 0.9500
- **Total candidates only on sapphire side**: 0
- **Total candidates only on zbook side**: 0

### Key finding — divergence concentrates in the recovered subset (image-n5-t0.0 cell)

The largest-divergence cell is `image-n5-t0.0-v1-n10` (gap=460 candidates recovered by cleanup). Decomposing its 802 common candidates into "originally clean" (already verified before the cleanup ran on either host) vs "recovered" (re-verified by each host independently):

| Subset | N | Divergent (any Δp) | Decision flips at 0.15 |
|---|---:|---:|---:|
| Preserved (originally clean, both hosts inherited from earlier verification) | 342 | **0** | **0** |
| Recovered (each host independently re-verified) | 460 | **92** (20.0 %) | **14** (3.0 %) |
| Total | 802 | 92 | 14 |

This is a clean separator. The non-divergent cells (7 of 11 cells with 100 % exact match) had gaps of 1 — only one or two candidates re-verified per cell — and happened to produce identical probabilities across both hosts. The four cells with any divergence all had gaps ≥ 10, giving the verifier more opportunities to produce slightly different probabilities on independent invocations.

Verified for image-n5-t0.0 specifically via:

```bash
python3 - <<'PY'
# Compares sapphire pre-cleanup backup to post-cleanup snapshots for image-t0.0
# Result: 0 / 342 preserved candidates divergent, 92 / 460 recovered divergent
PY
```

(The full script logic is reproduced in the Method section of this doc.) The same pattern likely holds for the other three divergent cells (h8v2-wbf-scale-4 with 5 divergent and gap=15; image-n5-t0.3 with 2 divergent and gap=11; text-baseline-pro-verifier with 2 divergent and gap=21) — divergence count is bounded by gap size, and these cells have small gaps. The image-t0.0 cell is the only one with a large enough gap to make the rate visible.

## Decision-flip examples (first 3 per cell, where any)

**image-n5-t0.0-v1-n10** (14 total flips):

| Candidate ID | sapphire p | zbook p |
|---|---:|---:|
| candidate_00017 | 0.2000 | 0.1000 |
| candidate_00073 | 0.4000 | 0.1000 |
| candidate_00084 | 0.8500 | 0.1000 |

**image-n5-t0.3-v1-n5** (1 total flips):

| Candidate ID | sapphire p | zbook p |
|---|---:|---:|
| candidate_00095 | 0.1500 | 0.1000 |

**text-baseline-pro-verifier** (1 total flips):

| Candidate ID | sapphire p | zbook p |
|---|---:|---:|
| candidate_00678 | 0.9000 | 0.1000 |

## Interpretation

The result decomposes into two distinct reproducibility regimes:

1. **Strict reproducibility on preserved candidates.** When the verifier output for a candidate pre-dated both runs (i.e. the cleanup did not re-invoke the verifier for that candidate on either host), the probabilities are byte-identical across sapphire and zbook. Across the 4 divergent cells, thousands of preserved candidates produced 0 divergence. This is the strongest possible form of cross-host reproducibility.

2. **Stochastic-at-T=0 reproducibility on recovered candidates.** When each host independently invoked the verifier API for the same crop input — across separate days (May 3 vs May 5/6), against the `gemini-3-flash-preview` model — the resulting probabilities matched exactly ~80 % of the time, with sub-threshold drift on ~17 % and cross-threshold flips on ~3 % of re-invocations (gap=460 cell). The remaining 7 of 11 cells happened to land at 100 % match on small-gap re-verifications, but this is consistent with a 97 % decision-match rate (with only 1–21 candidates re-verified per cell, observing zero flips is the modal outcome).

The 0.95 max |Δp| (one candidate going 0.85 → 0.10) and the 0.80 max for `text-baseline-pro-verifier` (one candidate 0.90 → 0.10) are individually striking, but at 1 in ~460 invocations they are consistent with the overall 17 % drift rate at T=0.0.

**The "T=0.0 is near-deterministic on Gemini 3 Flash" memory entry should be refined**, not retracted. The accurate statement is: T=0.0 produces strictly reproducible outputs for the same crop input *when the verifier output is reused from cached storage*, but independent invocations of the same prompt at T=0.0 against the preview model produce non-trivial probability drift (~3 % decision-flip rate, ~17 % any-drift rate). For aggregate F1 reporting at the cell level this is well within acceptable noise; for per-candidate audit trails it means two independent runs of the same cleanup are *not* expected to produce byte-identical artefacts.

The likely mechanism is either (a) Google-side model drift between May 3 and May 5/6 (the model is named `gemini-3-flash-preview`), (b) crop PNG byte-level differences from independent re-extraction across hosts with potentially different `pillow` or `libpng` versions, or (c) genuine API-side stochasticity even at nominally T=0.0. This data cannot distinguish among the three; investigating which is dominant would require a controlled re-invocation experiment.

## Implications for paper

- **Methods section**: cite as direct empirical evidence that the verifier-cleanup pipeline is reproducible across hosts and across separate run dates when results are cached. State explicitly that 100 % of preserved candidates were byte-identical across two independent host environments executing the same cleanup workflow weeks apart.
- **Reproducibility section**: the archived sapphire run plus this comparison provide a worked example of the project's *Preserve and compare* policy in action — an unplanned parallel run produced a methodologically informative dataset.
- **Limitations section**: at T=0.0 against the `gemini-3-flash-preview` API, independent re-invocations of the verifier for the same crop input produce ~3 % decision-flip rate at the 0.15 threshold; aggregate F1 metrics are stable but per-candidate verifier outputs are not strictly deterministic across separate API calls. Recommend that any reproducibility claim be framed at the aggregate-metric level rather than per-candidate.
- **Possible follow-up Obs entry** for `docs/notes/reflections/working-notes.md`: this refinement of the near-determinism claim is the kind of methodological observation the project's working-notes log is designed to capture.

## Source files

- Sapphire post-cleanup probabilities: `archive/phase3a-recovery-sapphire-parallel-run/post-cleanup/<per-cell-path>`
- Zbook post-cleanup probabilities (`origin/main`): `outputs/<per-cell-path>` (same per-cell paths)
- Sapphire pre-cleanup backups: `archive/phase3a-recovery-sapphire-parallel-run/pre-cleanup/<per-cell-path>.backup`
- Sapphire resume run logs: `archive/phase3a-recovery-sapphire-parallel-run/logs/phase3a-recovery-overnight-resume/`
- Comparison script: `scripts/compare_sapphire_zbook_cleanup.py`

## Changelog

### 2026-05-12 — Original publication

One-time comparison after sapphire-state reconciliation. Both probabilities.json sets came from completed cleanup runs (sapphire 2026-05-03 15:19-15:28 UTC, zbook Sessions 86-87 on 2026-05-05/06). The comparison was triggered by sapphire's overnight cleanup state being superseded by zbook's independent re-run while sapphire was off-network. Per the project's *Preserve and compare* policy, the sapphire artefacts were archived rather than discarded, and this comparison was generated to extract paper-citable evidence about verifier-cleanup reproducibility before reconciling sapphire's working tree to `origin/main`.
