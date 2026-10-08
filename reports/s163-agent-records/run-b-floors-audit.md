# Run B floors and gap-change test: independent audit of the analysis code

> **Last revised**: 2026-10-08 (original publication). See
> [§ Changelog](#changelog) for revision history.

- **Auditor**: Claude (Anthropic), Claude Code, model lane Opus 5.5
  (`claude-opus-5-5`), a read-only subagent of the main Session 163 session.
- **Date**: 2026-10-08 (Sydney).
- **Repository**: `map-reader-llm`.
- **Commit audited**: branch `worktree-agent-a5cd02edc1e390007` at `3d3cfe18e`,
  `scripts/modality_bridge_floors.py` and `tests/test_modality_bridge_floors.py`,
  with the results in `results/modality-bridge-2026-10-07/floors/` and the
  reading in that branch's `results/modality-bridge-2026-10-07/findings.md`
  §§ 4–7.
- **Scope**: scoring plan items 4, 6 and 7 of `planning/modality-bridge-2026-10-07.md`
  § 9 (the gap-change interaction permutation, the date component per cell, the
  D45/D46 floors). Read-only: nothing edited, committed or pushed; no model
  Application Programming Interface (API) call. Disposable copies were used for
  recomputation.

The auditor's report is recorded below as returned, lightly formatted. The main
session applied findings 2, 3, 4, 5 and 7 to `findings.md` as wording, and
finding 1 as a quantified limit; finding 6 follows the project convention (D42
default (d)) and was not changed.

## Verdict: MERGE AFTER FIXES

The fixes are to the prose in `findings.md` only. No code defect was found, and
none of the reported numbers is wrong.

## Verified

- **Interaction permutation:**
  - The statistic is (T37 − I37) − (T3 − I3).
  - One Bernoulli(0.5) mask per tile swaps a↔c and b↔d together
    (`lib_permutation.py:353-366`), so the swap is joint across both families.
  - F1 is recomputed from summed true positive (TP), false positive (FP) and
    false negative (FN) counts in every permutation.
  - 10,000 permutations, seed 42. Bootstrap 1,000, seed 42.
  - Strictly, the null is that each tile's text and image pairs are
    exchangeable. To first order that is a sign-flip test of each tile's
    contribution, which is a valid interaction test. The two Gemini 3 cells have
    similar denominators (821 and 815), so the approximation is tight. The joint
    mask is the right paired design.
  - The family-swap version is a sensible sensitivity. The auditor's own
    variant, with an independent mask per family, agrees (p 0.0058 and 0.0035).
- **Frames:** 487 unique tiles. The per-tile matcher creates a row for every
  tile (`lib_advanced_metrics.py:1206-1209`), so no tile is dropped or silently
  zeroed. The auditor's own per-map Hungarian totals equal the per-tile sums for
  all six cells.
- **Floors:** the rules match § 6b of the W2.7 report (`floors2_rescreen.py:45-90`).
  - Adding four variances is justified: the cells come from separate arms and
    passes, with the verifier held fixed.
  - The "upper bound" adds each cell's upper standard deviation (SD) in
    quadrature, as § 6b does. It is very conservative: a delta-method 95 % upper
    for the primary is about 0.068 (ratio 0.78), still below 1.
  - At K′ = 5 the normal-approximation floor is larger than the empirical
    disjoint-pair 95th percentile (0.0155 against 0.0125 for text; 0.0349
    against 0.0290 for image), so it errs high.
  - The direct reading from `38505f81f` is sound as a labelled sensitivity,
    though at K′ ≥ 8 its standard errors are about the size of the estimates.
- **Gates:**
  - Every gate is a hard stop before anything is written
    (`modality_bridge_floors.py:1204-1283`).
  - The log and `gates.json` show all ten committed gap entries reproduced, with
    p values exactly equal.
  - Every committed set's F1 differs by 0.0, and the all-pass rungs fall within
    1.9 nm of the unions.
- **Tests and lint:** 19 of 19 tests pass; ruff is clean.
- **Date component:** the exact 0.0000 for 3.7 text under the 3.7 verifier is
  genuine. The original and the bridge both have TP/FP/FN 397/32/31, despite 22
  discordant tiles.
- **Prose numbers:** every table row and ratio in §§ 4–7 matches the JSON
  outputs (but see finding 7).

## Independent recomputation (the auditor's own code)

- Gap changes: −0.052916 and −0.054666, exact.
- Interaction p: the project's random stream reproduces 0.0047 and 0.0040
  exactly. The auditor's own stream gives 0.0041 and 0.0030, within Monte Carlo
  error (about 0.0007).
- Primary floor, rebuilt from `subset_cells.csv`: 0.042579, upper 0.07967,
  exact.

## Findings, by severity

1. **Medium (suspected): the borrowed verifier band is probably too small for
   this frame.** The band is set at `modality_bridge_floors.py:118` and applied
   at `:1097` and `:1118`. Each cell has 393 to 441 detections, so one verifier
   decision moves F1 by about 0.0011 to 0.0013, and the whole 0.001 band is
   about one decision. The 2.4 % re-invocation flip rate would be about 10
   decisions per cell. Scaling from the 55-map corpus (about 11 times as many
   detections) suggests 0.003 to 0.005 per contrast. At those values the primary
   ratios fall from 1.24 and 1.28 to 1.14 and 1.17, or to 1.05 and 1.08: still
   clear of the point floor, so the verdict holds, but the margin is thin.
   No reported number changes.
2. **Medium (prose): "parity".** §§ 4 and 7 read as an equivalence claim. The
   evidence is only non-rejection plus being below the floor, which is a weak
   basis for parity; the fifth-leg gap (−0.0164, p 0.074) is not shown to be
   parity. Reword to "no resolved gap", or add an equivalence bound.
3. **Low (prose): the flip yardstick.** It holds the verifier fixed
   (`modality_bridge_floors.py:1019-1042`), but the bridge was re-verified on a
   different date, so "generous" (§ 6) holds in one direction only. The § 8
   excess for Gemini 3 text (6.6 % against 5.3 %) may be verifier re-invocation
   rather than date plus serving mode. For 3.7, "two halves" is really two-pass
   rungs of a five-pass arm.
4. **Low (prose): the "stands narrowly" analogy.** It cites R7.2-13a, which sat
   at its upper bound; the Run B primaries sit at 0.66 of theirs. The re-screen's
   own label for this case is "clears the point floor; inside its upper bound"
   (`floors2_rescreen.py:290-294`).
5. **Low (method):** for Gemini 3 image at (0.15, k9) the vote path is unanimity
   for every K′ ≤ 5, so its carried SD is the k10 cell's (0.0164). This affects
   only that date-component floor, in the conservative direction.
6. **Info: no +1 correction on p.** This follows the project convention (D42
   default (d)). With +1 the primaries would be 0.0048 and 0.0041, and
   "< 0.0001" would strictly read "≤ 0.0001". Immaterial.
7. **Minor (prose):** § 4 item 3 quotes F1s at the operating point beside a
   ratio computed at the best points (0.37) that is in no JSON output.

## Changelog

### 2026-10-08 — Original publication

The audit as returned to the main session, recorded for provenance before the
branch merged.
