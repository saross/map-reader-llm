# BCa bootstrap: transposed axes make every affected interval too narrow

> **Last revised**: 2026-08-18 (original publication). See
> [§ Changelog](#changelog) for revision history.

**Status: VERIFIED, NOT FIXED.** The defect is confirmed empirically against
real published data. No code has been changed and no committed value has been
altered, because the correction moves essentially every bootstrap confidence
interval in the study and that is the PI's call to sequence, not an
implementation detail.

**Provenance**: found by the E81 correction agent while routing degenerate
tile-MCC resamples off the BCa path, and reported by it as a separate,
larger, pre-existing defect rather than folded into E81 — correctly, since
bundling them would have made both deltas unattributable. Independently
verified by the session owner before being recorded here.

## The defect

`scripts/lib_advanced_metrics.py`, `_bca_ci_from_indices`, in the wrapper that
adapts a per-tile statistic to `scipy.stats.bootstrap(vectorized=True)`:

```python
return np.array(
    [statistic(row) for row in np.moveaxis(idx_array, axis, 0)]
)
```

SciPy passes a `(B, n)` array of resampled indices with `axis=-1`, meaning the
statistic is to be applied **along the last axis** — `B` results, each computed
over `n` resampled tiles. `np.moveaxis(idx_array, axis, 0)` moves that last
axis to the front, producing `(n, B)`, so the comprehension iterates the wrong
way: it computes **`n` statistics of `B` draws each** instead of **`B`
statistics of `n` draws each`**.

Verified directly against the wrapper, reproduced verbatim outside the module:

```text
scipy passes shape (2000, 340) (B=2000 resamples, N=340 tiles), axis=-1
wrapper returned 340 values  -> expected 2000
each statistic call saw 2000 indices -> expected 340
```

## Why this narrows intervals

Each value in the resulting "bootstrap distribution" is a statistic over `B`
draws rather than `n`. A statistic's sampling spread falls as `1/sqrt(sample
size)`, so the distribution the interval is read from is too tight by roughly
`sqrt(B / n)` — and the interval inherits that. The BCa jackknife acceleration
is computed on the same transposed array and is therefore meaningless as well.

Measured on a real published cell — H13 arm A, F1@20 m, 340 tiles, committed
interval `[0.5210, 0.5934]`:

| B | Library interval | Width | Correct percentile bootstrap | Width | Too narrow by | `sqrt(B/n)` |
|---:|---|---:|---|---:|---:|---:|
| 1,000 | [0.5232, 0.5931] | 0.0698 | [0.4978, 0.6136] | 0.1159 | **1.66×** | 1.71 |
| 10,000 | [0.5475, 0.5683] | 0.0208 | [0.4994, 0.6141] | 0.1146 | **5.50×** | 5.42 |

The observed factor tracks `sqrt(B/n)` to two decimal places at both iteration
counts, which is what confirms the mechanism rather than merely the symptom.

## Scope

**Affected**: any interval produced on the **BCa** path. Committed evaluations
record **1,520 at B = 10,000** and **101 at B = 1,000** — so the majority sit
where the distortion is largest, around 5.4× at 340 tiles and 4.5× at 487.

**Not affected**:

- The `percentile_fallback` branch, which is an independent and correct
  implementation: it draws `n` indices per resample and computes
  `n_iterations` statistics. Only degenerate cases reach it.
- Permutation tests, which are a different instrument entirely.
- The paired tile bootstraps written this session
  (`h13_overlap_analysis.paired_bootstrap`, `grid_analysis`), which implement
  their own resampling loop and never call this function.
- Point estimates everywhere. **No F1, precision, recall or MCC point value is
  affected** — this defect touches only interval width.

## Why it matters more than a width

Decision 10 registers the bootstrap interval as the study's inference
instrument, and the registered significance criterion is *"if the 95 % CI for
a difference excludes zero, we treat this as significant"*. An interval too
narrow by 1.7× to 5.4× will exclude zero in cases where a correct one would
not. Every significance reading resting on a BCa interval is therefore
unverified until recomputed — the direction of the error is towards
false positives, not false negatives.

## Recommended remediation, for PI decision

1. **Fix the wrapper.** The correction is to iterate the resample axis rather
   than move it to the front — for the `(B, n)`/`axis=-1` case this is simply
   iterating `idx_array` directly, with the general form handled by moving all
   axes *except* `axis`. One line, plus a test asserting the returned
   distribution has length `B` and each call sees `n` indices. That test would
   have caught this at any point since the function was written.
2. **Decide the re-emission scope.** Options, in ascending cost: correct only
   intervals that carry a published significance claim; correct every
   BCa-path interval in `results/`; or correct and additionally re-run the
   family-FDR chain that consumes them. All are $0 compute, none needs API
   spend.
3. **Erratum.** This warrants its own entry — it is a defect in the registered
   inference instrument, distinct from E79 (tile-assignment sensitivity), E80
   (deduplication path asymmetry) and E81 (undefined MCC published as zero).
4. **Do not bundle with E81.** E81's corrections are landed and attributable;
   mixing this in would make both undiagnosable.

## See also

- **Preceding experiment(s)**: `reports/defect-register-2026-08-18.md` — the
  session's defect list, where this is recorded as D15.
- **Follow-up experiment(s)**: None yet — remediation is pending the PI's
  decision on scope.
- **Run output directory**: None. This is a defect in an analysis instrument,
  not a run.
- **Working-notes Observations**: None yet.
- **Decisions / Errata**: Decision 10 — registers tile-level bootstrap CIs and
  the CI-excludes-zero significance rule, which is what this defect
  undermines. E54 — the 10,000-iteration convention, which is precisely where
  the distortion is worst. E81 — the correction whose work surfaced this.

## Changelog

### 2026-08-18 — Original publication

Verified and recorded, not fixed. Mechanism confirmed by reproducing the
wrapper outside the module; magnitude confirmed against a real published cell
at two iteration counts, matching `sqrt(B/n)` at both.
