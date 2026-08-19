# Inference instruments: which one answers which question

> **Last revised**: 2026-08-19 (original publication). See
> [§ Changelog](#changelog) for revision history.

**What this is.** A reporting policy for the study's uncertainty claims. The
project computes several different interval and test procedures, and they answer
different questions. Using the wrong one is the easiest way to overstate a
result, and one such misuse is already documented as a defect (D20). This note
fixes which instrument licenses which sentence.

**Status.** Policy proposed 2026-08-19; the D20 remediation it depends on is an
open Principal-Investigator decision.

## The registered baseline

Registered § 3.5 asks for **effect sizes — F1, precision and recall
*differences* — with 95 % bootstrapped CIs**, and for both uncorrected and
FDR-corrected p-values. Decision 10 (`decisions-log.md:345`) fixes tile-level
bootstrap resampling, Benjamini–Hochberg FDR at q = 0.05, and a significance rule
defined on a **difference**: "if the 95 % CI for a difference excludes zero, we
treat this as significant".

Two consequences follow immediately and are easy to miss.

1. **The registered inferential object is the difference interval.** A
   single-condition confidence interval is descriptive. It is not what Decision 10
   adjudicates, and no registered claim rests on one.
2. **Erratum E82** records that the executed method is BCa at 10 000 iterations
   rather than the pre-specified percentile method at 1 000. The resampling unit
   and the significance rule are unchanged.

## The instruments, and what each licenses

| Question | Instrument | Licenses |
|---|---|---|
| How precise is this one cell's estimate? | Single-condition bootstrap CI (BCa, tile-level, B = 10 000) | "F1 is 0.75, 95 % CI [0.70, 0.79]" — **descriptive only** |
| Does condition A differ from condition B? | Paired tile bootstrap or paired tile-swap permutation on the difference | "A exceeds B by 0.12, CI [0.09, 0.15], excludes zero" |
| Which of many conditions differ, controlling error across the family? | Round-robin paired permutation + BH-FDR at q = 0.05 | "24 of 28 pairs are significant after correction" |
| **Which conditions cannot be ruled out as the best?** | **MCB (Hsu, constrained one-sided)** | "these *k* conditions are statistically indistinguishable from best" |
| How optimistic is a figure that was chosen by an argmax on this data? | Selection-aware bootstrap (Efron–Gong optimism, argmax replayed) | "apparent 0.7518, optimism +0.0016, corrected 0.7501" |

### The rule that matters most

**Never infer a difference from overlapping single-condition intervals.** Two
intervals can overlap substantially while their paired difference excludes zero,
because the paired instrument removes the between-tile variance that dominates
each marginal interval. The study's own contrasts are paired for exactly this
reason. Any sentence of the form "A and B are indistinguishable because their CIs
overlap" is unsupported; the licensed forms are the difference CI, the permutation
test, or MCB.

Audited 2026-08-19: the Results draft quotes one interval and it is a difference
interval, so no current prose violates this.

### Selection: the narrow scope

Selection-aware correction applies **only** where an argmax was taken over
candidates scored on the evaluation data. It must **not** be applied to a
comparison made at a fixed operating point across arms. The grid's overlap,
tile-size and interaction contrasts are computed on run-averaged single-pass
counts with no consensus filter and no selection; correcting them would introduce
a bias rather than remove one.

Measured magnitudes are in `results/selection-aware/findings.md`: optimism runs
from −0.0008 to +0.0132 across ten candidate sets and tracks argmax stability. It
is small enough to state and move on, but it should be stated.

## Sparse coverage: the `ci_unreliable` flag over-warns

`ci_unreliable` fires when more than 50 % of evaluation tiles carry zero
TP + FP + FN. It reaches **91 of 337 conditions at the 20 m headline buffer**,
including `gold-standard-v2::verified-v1` and all five 55-map generalisation
conditions — so a naive reading would put a health warning on the paper's headline
results.

That reading is wrong, and the record should say so. The flag was introduced on
2026-04-30 (`2026999ad`) as "Mitigation 3", to detect a specific percentile-method
pathology: bootstrap distributions whose 2.5–97.5 percentile range **systematically
excluded the all-data point estimate**. The *same commit* replaced the percentile
method with BCa, which fixed that pathology, and the flag was never re-evaluated
against the corrected intervals.

Re-checked 2026-08-19 across every flagged buffer-row in the manifest:

| Flagged rows with a readable interval | Interval contains the point estimate | Interval excludes it |
|---:|---:|---:|
| 1,041 | **1,041** | **0** |

**The pathology the flag was raised to detect no longer occurs anywhere.**

Sparseness itself remains real and worth disclosing — containment of the point
estimate is necessary for a usable interval, not sufficient, and a cell where most
tiles are empty carries genuinely less information than its tile count suggests.
The reporting rule therefore changes from suppression to disclosure:

1. **Do not suppress or asterisk** a flagged interval on the strength of this flag.
2. **Report the zero-fraction** where a cell is discussed in the text
   (`coverage.zero_fraction`; 0.571 on the 384-consensus cell, for instance),
   so a reader can judge the effective sample size.
3. **Rename the field's meaning in prose**: it marks *sparse cross-grid coverage*,
   which is what `coverage_status` already calls it, not an unreliable interval.
4. Treat the 50 % cut as the heuristic it declares itself to be
   (`coverage_source: zero_fraction_heuristic`), not a threshold with inferential
   standing.

## Reporting both uncorrected and FDR-corrected p-values

Registered § 3.5 requires both. The computation is present — the tiering artefacts
carry `p_value` and `bh_adjusted_p` per pair — but **no analysis outcome in the
register reports the uncorrected value**, so the requirement is met in the
artefacts and unmet in the reporting.

Rule: any table or outcome quoting an FDR-corrected p-value must give the
uncorrected one beside it. Where a family is large enough that per-pair listing is
impractical, report the count at both levels ("227 of 630 pairs significant
uncorrected; 189 after BH at q = 0.05") and cite the artefact for the full table.

## See also

- `docs/methodology/preregistration/decisions-log.md:345` (Decision 10)
- Errata E56 (in-sample operating points), E82 (BCa and the iteration count)
- `results/selection-aware/findings.md` (measured selection optimism, MCB sets)
- `reports/defect-register-2026-08-18.md` D20 (tier construction)

## Changelog

### 2026-08-19 — Original publication

Written after the selection-aware interval work surfaced two reporting problems:
the absence of a stated rule for which instrument licenses which claim (D20 is a
consequence), and a stale sparse-coverage flag that over-warns on 91 of 337
conditions including the headline gold-standard cell. Records the measured result
that all 1,041 flagged intervals now contain their point estimate, so the
pathology the flag detects has been fixed since 2026-04-30.
