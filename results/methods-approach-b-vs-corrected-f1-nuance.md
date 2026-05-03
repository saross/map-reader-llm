---
title: "Methods note — two implementations of Approach B (corrected-F1 multi-buffer vs paired-permutation)"
date: 2026-05-03
session: 85
intended_paper_section: Methods supplement (and brief Limitations footnote)
source_continuity_doc: "planning/paper-writeup-continuity.md § 'Additional backlog captured during Session 84 close-out review' (B6)"
---

# Methods note — two implementations of Approach B

## Context

The corrected F1 reported throughout the manuscript follows **Approach B — extended-GT-at-R Hungarian matching**: the per-side ground truth is augmented with reviewer-promoted phantom mounds (candidates the reviewer confirmed as real within radius `R`) before per-map Hungarian matching at `max_distance = R`. Two scripts in the project codebase implement this method, and a brief note on their relationship is warranted because they can produce numerically distinct values for the same pair under one specific condition.

## The two implementations

`scripts/compute_corrected_f1_multi_buffer.py` is the **canonical citation source** for the corrected F1 / P / R values reported in the leaderboard, cross-track summary tables, and per-run evaluation cells. It builds the extended GT by adding all reviewer-promoted phantoms in scope and runs Hungarian matching against the augmented GT, then aggregates per-map TP / FP / FN counts to micro-averaged precision, recall, and F1 with tile-level bootstrap CIs.

`scripts/paired_permutation_corrected_55maps.py` is the paired-test counterpart consuming the same review CSVs to produce ΔF1 / p-values for paired-permutation tests across buffer radii. Its docstring states it implements "Hungarian matching, identical to `compute_corrected_f1_multi_buffer.py`", and **under fully-up-to-date review CSVs the two scripts agree to within rounding** (≤ 0.003 absolute on the cells we have checked).

## When and why they can diverge

Under review CSVs that lag behind the verified detection set — for example, where the verified set has acquired new candidates after a verifier-recovery pass that have not yet been re-reviewed — the two scripts can disagree. The pair script attributes un-reviewed candidates to FP; the multi-buffer script's defaulting can produce a different FP count, leading to F1 values that diverge by 0.01–0.06 absolute on paper-relevant cells.

A concrete example surfaced in Session 84 (2026-05-03): for the post-recovery image-track at R = 50 m, the pair script returned F1 = 0.7748 against a corrected-f1.csv canonical value of 0.8333 — a 0.0585 gap caused by a review-CSV refresh having not yet propagated through to the pair script's input. The gap closed once the review CSV was refreshed.

## Practical guidance for paper text and reproducibility supplement

1. **All cell-level corrected F1 / P / R values** cited in the manuscript come from `compute_corrected_f1_multi_buffer.py`'s `corrected-f1-multi-buffer/summary.json` outputs. The leaderboard, cross-track summary tables, and per-run evaluation cells all source from this script.
2. **ΔF1 values from paired tests** (`paired_permutation_corrected_55maps.py`'s outputs) should only be cited when the underlying review CSVs are current — i.e., when post-recovery review passes have completed for both sides of the pair. Stale review CSVs can produce spurious ΔF1 magnitudes that do not reflect real cross-condition differences.
3. **Pre-flight check** (recommended for reviewers reproducing results): confirm that each side's pair-script F1 agrees with the corresponding `corrected-f1-multi-buffer/summary.json` value to within 0.005 absolute before citing the paired-test result. A larger discrepancy indicates review-CSV staleness and should trigger a review-pass refresh before the paired test is interpreted.

## Suggested paper-text placement

- **Methods supplement**: a paragraph describing Approach B in full (extended-GT-at-R Hungarian matching, the phantom-mound mechanism, and the two implementations), with a brief note that the canonical numbers come from the multi-buffer script.
- **Limitations footnote** (one to two sentences): "Paired-permutation ΔF1 values are sensitive to the freshness of the human-review CSVs underlying each side; results reported here use review CSVs current as of [date]. Under stale review CSVs the paired-test values can drift from the published corrected-F1 cells by up to ~0.06 absolute. The reproducibility supplement gives a pre-flight check for this case."

This is a methodological subtlety that should be surfaced rather than hidden — it does not affect any of the manuscript's headline conclusions (all of which use the canonical multi-buffer script's outputs), but it would be a fair question for a reproducer to ask, and the supplement should answer it pre-emptively.
