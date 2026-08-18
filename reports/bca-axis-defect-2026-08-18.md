# BCa bootstrap: transposed axes rescale every affected interval by sqrt(n/B)

> **Last revised**: 2026-08-19 (adversarial re-examination — mechanism
> confirmed, three parts of the recorded claim corrected, code fixed and
> tested). See [§ Changelog](#changelog) for revision history.

**Status: MECHANISM CONFIRMED. CODE FIXED. NO COMMITTED VALUE
RE-EMITTED.** The wrapper defect is real and was reproduced exactly,
including a bit-identical reproduction of a committed published
interval. The fix landed in commit `122104b8a` together with five tier-1
regression tests. The correction *scope* — which committed artefacts to
re-emit — remains the PI's decision and nothing under `results/`,
`outputs/` or `docs/paper/` has been touched.

**Three parts of the original record were wrong and are corrected
below.** A correction to a correction is worth as much as the original,
so they are stated first:

1. **The intervals are not uniformly "too narrow".** The width is
   rescaled by `sqrt(n / B)`. That is a narrowing only when `B > n`.
   840 committed BCa intervals sit at `B < n`, where the defect made
   them **too wide** — an error towards false *negatives*. See
   [§ Direction](#direction-and-magnitude-the-error-changes-sign).
2. **The scope counts do not reproduce.** The recorded "1,520 at
   B = 10,000 and 101 at B = 1,000" does not match the committed
   artefacts under any counting rule tried. The verified figures are in
   [§ Scope](#true-scope-verified-against-the-artefacts).
3. **No published significance verdict changes — the count is zero.**
   The recorded claim that "every significance reading resting on a BCa
   interval is unverified" is true but vacuous: the registered
   significance rule is defined on a *difference* CI, and no difference
   CI in this study is on the BCa path. See
   [§ How many conclusions change](#how-many-published-conclusions-change-zero).

A fourth item is a genuine finding the original record did not contain:
**BCa is itself an unregistered method.** Decision 10 registers the
*percentile* method. That is a disclosure gap independent of this bug.
See [§ BCa is unregistered](#bca-itself-is-an-unregistered-deviation).

**Provenance**: found by the E81 correction agent while routing
degenerate tile-MCC resamples off the BCa path; recorded 2026-08-18;
re-examined adversarially on 2026-08-19 with the explicit brief of
refuting it.

## The defect

`scripts/lib_advanced_metrics.py`, `_bca_ci_from_indices` (line 299), in
the wrapper that adapts a per-tile statistic to
`scipy.stats.bootstrap(vectorized=True)`:

```python
return np.array(
    [statistic(row) for row in np.moveaxis(idx_array, axis, 0)]
)
```

scipy's `vectorized=True` contract is that the statistic is computed
**along** `axis`, which is then consumed; every remaining axis
enumerates independent resamples. `np.moveaxis(idx_array, axis, 0)`
moves the observation axis to the front, so iterating the result walks
the wrong axis.

Instrumenting the wrapper against real dimensions (n = 340 tiles,
B = 1,000, scipy 1.17.1, numpy 2.4.3) records every call scipy makes:

```text
in=(1000, 340)  axis=-1  returned=340   <- resample batch: expected 1000
in=(340,)       axis=-1  returned=1     <- point estimate: correct
in=(340, 339)   axis=-1  returned=339   <- BCa jackknife: expected 340
len(bootstrap_distribution) = 340
```

Each entry of the resulting "bootstrap distribution" is
`idx_array[:, k]` — the k-th draw of every resample, i.e. `B`
independent uniform draws from the tile pool. So the distribution
consists of `n` statistics of `B` draws each, where it should be `B`
statistics of `n` draws each.

## What scipy does with the wrong-length return

**Nothing.** It neither errors, broadcasts, truncates, nor reinterprets.
Verified against the installed source,
`.venv/lib/python3.13/site-packages/scipy/stats/_resampling.py`
(scipy 1.17.1):

- line 646 — `theta_hat_b.append(statistic(*resampled_data, axis=-1))`
- line 647 — `theta_hat_b = xp.concat(theta_hat_b, axis=-1)`
- line 662 — `ci = stats.quantile(theta_hat_b, interval, axis=-1)`

There is no shape assertion anywhere between those three lines. The
returned array simply *becomes* the bootstrap distribution, and the
interval is read off it. `BootstrapResult.bootstrap_distribution` and
`standard_error` are computed from the same wrong array. This is why the
fault was silent for the life of the function: nothing raises, nothing
warns, and the output has the right dtype and shape *rank*.

## The jackknife and the acceleration term

The same wrapper serves the BCa acceleration step.
`_bca_interval` (line 109) calls
`statistic(*broadcasted, axis=-1)` (line 133) on the batch produced by
`_jackknife_resample` (line 54), which for a 1-D sample is an
`(n, n - 1)` array of leave-one-out index rows. The transposing wrapper
returns `n - 1` values instead of `n`, and — worse — each value is a
statistic over a *column* of the leave-one-out matrix. Column `j` holds
index `j` repeated for every row `i > j` and index `j + 1` for every row
`i <= j`, so each "jackknife pseudo-value" is a statistic computed over
a sample containing at most **two distinct tiles**.

That is not merely noisy; it is a different quantity. On H13 arm A,
F1@20 m, B = 1,000:

| | `len(theta_hat_b)` | `a_hat` | alpha_1 | alpha_2 |
|---|---:|---:|---:|---:|
| defective | 340 | −0.000912 | 0.03144 | 0.98028 |
| corrected | 1,000 | +0.000129 | 0.02145 | 0.97097 |

The acceleration term changes sign, and the quantile levels the interval
is read at move by roughly one percentage point in each tail. The width
effect below dominates, but the interval is mis-*shaped* as well as
mis-scaled.

For a statistic on which those two-tile samples are undefined — tile-level
Matthews Correlation Coefficient (MCC) is the case in this study — the
pseudo-values collapse and `a_hat` becomes non-finite, which makes the
whole BCa call return `NaN` bounds. `_bca_ci_from_indices` catches that
and falls back to its own percentile resampler. That interaction turns
out to matter; see [§ Scope](#true-scope-verified-against-the-artefacts).

## Direction and magnitude: the error changes sign

A statistic's sampling spread falls as `1/sqrt(sample size)`, so a
distribution of statistics-over-`B`-draws is tighter than one of
statistics-over-`n`-draws by `sqrt(B / n)`, and the interval inherits
that. The recorded claim stopped there and concluded "too narrow". It is
**too narrow only when `B > n`**, and the study contains both regimes.

Measured on real committed per-tile counts (H13 arm A common,
`results/h13-overlap-2026-08-18/per_tile_counts.json`, n = 340,
F1@20 m, seed 42), defective versus corrected interval width:

| B | defective width | corrected width | defective / corrected | `sqrt(n/B)` |
|---:|---:|---:|---:|---:|
| 50 | 0.2820 | 0.0873 | **3.231** | 2.608 |
| 100 | 0.2111 | 0.1002 | **2.107** | 1.844 |
| 200 | 0.1524 | 0.0985 | **1.547** | 1.304 |
| 340 | 0.1175 | 0.1069 | **1.100** | 1.000 |
| 1,000 | 0.0698 | 0.1179 | **0.592** | 0.583 |
| 10,000 | 0.0208 | 0.1147 | **0.182** | 0.184 |

The ratio tracks `sqrt(n / B)` closely at `B >= 1,000` and crosses 1 at
`B ≈ n`, exactly as the mechanism predicts. (The excess at `B <= 200`
is expected: there the *corrected* interval is itself read off only
50–200 resamples and is under-resolved.) The consequence:

- **`B > n` — intervals too narrow, error towards false positives.**
  69,663 committed BCa intervals.
- **`B < n` — intervals too wide, error towards false negatives.**
  840 committed BCa intervals, chiefly the 55-map cells at n = 8,541
  with B = 1,000, where the interval is roughly 2.9x too wide.

The original record's title and its "the direction of the error is
towards false positives, not false negatives" are therefore correct for
the dominant regime and wrong in general.

## Refutation attempts, and how each failed

The brief was to break the claim, not to confirm it. Four independent
attacks were run; all failed, which is what promotes this from plausible
to established.

**1. "The wrapper is right and the reference was wrong."** Refuted. The
corrected wrapper was compared against `scipy.stats.bootstrap` with
`vectorized=False`, which calls the statistic once per resample through
scipy's own `_vectorize_statistic` shim and structurally cannot carry
this defect. On identical seeds scipy draws identical resamples either
way, so the two must agree exactly — and they do, to floating-point
equality, on all six real cells tested (H13 arms A/B/C × B ∈ {1,000;
10,000}). The defective wrapper agrees with neither.

**2. "BCa is legitimately narrower than percentile for a skewed
statistic, so the percentile reference was unfair."** Refuted. With the
wrapper corrected, BCa and a hand-rolled percentile bootstrap agree on
width to within 1.8 % on every cell (ratios 0.997, 1.000, 1.000, 1.001,
1.003, 1.018). BCa is not meaningfully narrower here; the 1.7x–5.5x gap
is not an estimator difference.

**3. "The `sqrt(B/n)` agreement is coincidence."** Refuted. It holds
across three independent cells at two iteration counts, and — the
decisive test — it correctly predicts the *reversal* at `B < n`, which a
coincidental fit could not.

**4. "scipy detects the wrong length and does something sensible."**
Refuted by reading the installed source; see
[§ What scipy does](#what-scipy-does-with-the-wrong-length-return).

**Reproduction gate.** Re-running the committed command for H13 arm A
common (`scripts/evaluate_detections.py`, three passes, 20 m, B = 1,000,
seed 42) against the pre-fix code reproduces the committed
`f1_ci_lower = 0.521`, `f1_ci_upper = 0.5934`, `p_ci_lower = 0.4111`,
`p_ci_upper = 0.4862`, `r_ci_lower = 0.7072`, `r_ci_upper = 0.7723`
**exactly**. The defect is in the code that produced the published
numbers, not in a reconstruction of it.

## True scope, verified against the artefacts

### Inside the library

`_bca_ci_from_indices` is reached from exactly **two** public functions:

- `bootstrap_ci` (line 1278) — F1, precision, recall, at lines 1390,
  1393, 1396;
- `bootstrap_tile_classification_ci` (line 2107) — tile MCC,
  sensitivity, specificity, at lines 2221, 2225, 2229.

Every **difference / effect-size** interval in the library instead goes
through `_compute_bca_ci` (line 521), a hand-rolled BCa over a bootstrap
distribution the caller has already computed in its own resampling loop:
lines 1539, 1653–1655, 1767–1769, 1927, 1947, 2374–2376. That helper
never touches scipy's vectorised path and is structurally immune.
`_compute_ci` (line 492) is dead code — nothing in `scripts/` calls it.

Scripts that produce intervals or p-values by their own resampling, and
are therefore unaffected, include `e45_bootstrap_pairings.py`
(`default_rng` at line 121, percentiles at 135–136),
`compute_family_fdr.py` (line 318, percentiles at 329),
`h13_overlap_analysis.py` (line 194, percentiles at 211–212),
`grid_analysis.py` (line 391, percentiles at 407–408), and
`paired_mcc_permutation.py` (permutation kernel, no bootstrap CI).
`run_bootstrap_10k.py` runs no statistics of its own — it shells out to
`evaluate_detections.py`, so everything it produced is path-1 output.

### In the committed artefacts

Counted from git-tracked files, not from assumption. **Where the truth
lives**: the only observed record of the path taken is the per-metric
`f1_ci_method` / `p_ci_method` / `r_ci_method` fields
(`scripts/evaluate_detections.py` lines 716, 721, 726) and
`tile_classification.<metric>.method` (line 214).
`_metadata.bootstrap.method` (line 539) is a **hard-coded literal**
written unconditionally and is *not* evidence of anything. All read
sites use `.get("method", "BCa")`, so a recorded `"BCa"` cannot be
distinguished from an absent key.

Across 1,749 tracked `evaluation.json`:

| Quantity | Verified count |
|---|---:|
| files carrying >= 1 BCa-path interval | 1,691 |
| intervals recorded `BCa` | 76,404 |
| intervals recorded `percentile_fallback` | 166 |
| intervals recorded `undefined` | 35 |
| files declaring B = 10,000 | 1,583 |
| files declaring B = 1,000 | 114 |
| files declaring no iteration count | 52 |

The recorded claim's "1,520 at B = 10,000 and 101 at B = 1,000" does not
match under any counting rule tried (files, intervals, tracked-only, or
all tracked JSON including aggregates). The figures above supersede it.
The recorded claim that only degenerate cases reach the fallback branch
**stands**: 166 fallbacks against 76,404 BCa.

Distortion regimes among BCa intervals: 69,663 with `B > n` (too
narrow), 840 with `B < n` (too wide), 5,901 where `n` or `B` could not
be read from the artefact.

### Point estimates

The recorded claim "no F1, precision, recall or MCC **point** value is
affected" **stands** — `f1`, `f1_point`, `precision`, `recall` are
written from `calculate_f1_internal`, which does no resampling. One
precisification: `tile_classification.<metric>.mean` *is* the mean of
the bootstrap distribution and is therefore on the defective path, and
`scripts/build_tiered_leaderboard.py` line 935 reads exactly that `mean`
for the MCC column of every tiered board. Measured over 25 real cells
the shift is negligible — median |Δ| = 0.0001, maximum 0.0024 — so this
is a completeness note, not a second defect.

### Interaction with E81 — tile-MCC largely escaped

An unexpected and load-bearing result. Under current code (E81's
`skip_undefined=True`), the *defective* wrapper makes the BCa jackknife
undefined for tile-MCC, `_bca_ci_from_indices` catches the non-finite
bounds, and the call falls back to its own **correct** percentile
resampler. Across 40 sampled real cells the pre-fix code fell back in
**40/40**, and the fallback interval agrees with the fixed-BCa interval
to within ~0.005 — so **0/40 zero-exclusion verdicts differ between the
pre-fix and post-fix code**.

The committed tile-MCC intervals were nonetheless computed *before* E81,
when an undefined MCC was coerced to `0.0`; that coercion kept the
transposed jackknife finite and let the defective BCa succeed. Those
committed intervals are distorted, e.g. a real n = 487 cell with
committed `[0.5485, 0.5765]` (width 0.028) against a correct
`[0.5025, 0.6187]` (width 0.116) — a 4.1x narrowing, against
`sqrt(10000/487) = 4.53`.

**Practical consequence: for tile-MCC, E81's already-landed re-emission
delivers the D15 correction as a by-product.** No separate re-run is
needed for that metric family. F1, precision and recall have no such
escape hatch and remain fully exposed.

## How many published conclusions change: zero

This is the question that matters, and the answer is **zero published
significance verdicts change**.

**The registered rule is defined on a difference.** Decision 10
(`docs/methodology/preregistration/decisions-log.md`) reads: *"If the
95% CI for a difference excludes zero, we treat this as 'significant'
for FDR purposes (pseudo-p < 0.05)."* No difference CI in this study is
produced by `_bca_ci_from_indices`; every one comes from an independent
resampling loop or from `_compute_bca_ci`.

**Every CI the paper quotes is a difference CI on the percentile path.**
`docs/paper/**` contains exactly three numeric intervals:

| Claim | Location | Source |
|---|---|---|
| H2 ΔF1 +0.076 (95 % CI +0.052 to +0.105) | `docs/paper/methods-draft.md:196` | `results/e45-bootstrap-pairings/e45_bootstrap_pairings.json` → `H2.bootstrap.registered_b1000.ci95` = [0.051787, 0.104642] |
| H3 ΔF1 +0.427 (95 % CI +0.390 to +0.468) | `docs/paper/methods-draft.md:197` | same file → `H3...ci95` = [0.38964, 0.468082] |
| H1 Δ +0.0238, 95 % CI −0.0104 to +0.0585 | `docs/paper/results-draft.md:155` | `results/family-fdr/family_fdr.md:26`, labelled "(percentile, B = 10 000, seed 42)" |

All three come from `e45_bootstrap_pairings.paired_bootstrap` /
`compute_family_fdr`, both own-loop percentile bootstraps. Unaffected.

**The family-FDR chain takes p-values, not CI positions.** All seven
inputs in `results/family-fdr/family_fdr.json` are p-values — two
permutation floors (H2, H3), one bootstrap-difference floor (H7), and
four computed difference p-values. None is a path-1 interval.

**Tiering does not read interval overlap.**
`build_tiered_leaderboard.apply_fdr_and_tier` (line 1432) tiers on
BH-corrected *permutation* p-values via greedy clique (lines 1483–1506).
The era-1 board (`era1_leaderboard_tiering.py`) and the diversity
analysis (`analyse_diversity.paired_permutation_test`) do the same. The
55-map MCC boards carry their own printed warning that the intervals are
marginal and that readers must use the BH-adjusted pairwise table, not
interval overlap.

**The one place a path-1 interval is read comparatively is
`results/h8-v2/analysis_summary.md`** ("no condition's CI excludes any
other condition's point estimate"), supporting a **null**. Widening the
intervals can only strengthen a null, and the seven contrasts were
already declared non-significant by BH-corrected permutation p-values.
No verdict moves.

**What does change, descriptively.** Recomputing every committed
tile-MCC interval from its own confusion matrix (1,962 blocks, 1,209
unique confusion x B cells — the statistic is a pure function of the
2x2 tile confusion matrix, so this needs no geometry and no API call):

- 1,911 committed blocks currently show an interval excluding zero;
- **225 of them no longer exclude zero** when recomputed correctly;
- 51 already included zero and still do.

None of those 225 backs a published significance claim; they are
marginal "MCC above chance" readings on board tables. They are, however,
the concrete size of the re-emission the PI is choosing about — and per
the E81 interaction above, an E81 re-emission delivers them anyway.

*Caveat on that count*: the tile label **order** is not recorded in the
artefacts, only the four counts, so the reconstruction is
distributionally exact but not bit-identical to the committed draw.
Cells sitting within Monte-Carlo noise of zero could tip either way, so
read 225 as the scale of the change, not as a per-cell verdict.

**What could not be covered.** The F1/precision/recall intervals were
not recomputed corpus-wide: unlike tile-MCC they are not reconstructible
from a recorded summary and would need the detection geometry re-scored
for each of ~1,691 files. This is $0 compute but hours of wall-clock,
and it was judged unnecessary once it was established that no F1
interval carries a significance verdict. The width correction for them
is predicted by `sqrt(n / B)` and was validated exactly on H13 arm A.

## BCa itself is an unregistered deviation

Independent of the bug, and arguably more serious for the paper:

Decision 10 registers **"Bootstrap resampling (tile-level) | 1000
iterations, percentile method (2.5th/97.5th)"**. `grep -c "BCa"` returns
**0** in both `docs/methodology/preregistration/decisions-log.md` and
`docs/methodology/preregistration/osf/preregistration.md`. It returns 5
in `docs/methodology/preregistration/protocol-errata.md`, all at lines
4428–4540 inside E81, where BCa appears only as the route of a defect —
not as a disclosure of the method change.

The switch is real and dated: `scripts/evaluate_detections.py`
lines 522–525 record *"metadata_version: 1.1 (2026-04-29) added BCa …
Downstream consumers should treat 1.0 outputs as percentile-method and
1.1+ as BCa"*. E54 discloses only the iteration-count change (1,000 →
10,000) and explicitly reaffirms the percentile method, so it does not
cover this. `reports/d17-inventory/d17-errata-census.md` already flagged
the gap and recommended an erratum; the number it suggested has since
been used three times over.

`grep -c "^### E"` on the errata file returns 81 and E81 (line 4069) is
the last heading, so **E82 is the next free number**. Two disclosures are
owed: the undisclosed percentile → BCa migration, and this defect.

Mitigating: `docs/paper/methods-draft.md:176` describes the registered
instrument as "1,000 iterations, percentile method" and the three CIs it
quotes really are percentile-path, so the paper's Methods statement is
currently *accurate about what it quotes*. It would become inaccurate
the moment a BCa interval is quoted as registered.

## The fix

Landed in `122104b8a`. The adapter now moves the observation axis to the
*end*, flattens the remaining resample-enumerating axes, applies the
statistic per row, and reshapes so `axis` is consumed — the general form
of scipy's contract, correct for 2-D and higher batches alike:

```python
moved = np.moveaxis(idx_array, axis, -1)
flat = moved.reshape(-1, moved.shape[-1])
return np.array(
    [statistic(row) for row in flat],
    dtype=float,
).reshape(moved.shape[:-1])
```

**Validation.** Against `scipy.stats.bootstrap(vectorized=False)` — an
independent implementation that calls the statistic once per resample —
the fixed adapter agrees to floating-point equality on the same seed, on
all six real cells tested and in the unit tests. It also agrees to
within 1.8 % with a hand-rolled percentile bootstrap that uses no scipy
code at all.

**Tests.** `tests/test_bca_vectorised_wrapper.py`, five tier-1 tests:
the returned distribution has length `B`; every statistic call receives
`n` indices (`n − 1` for the jackknife batch) and the call-length
profile is exactly `{n: B+1, n−1: n}`; equality with the
`vectorized=False` reference; width agreement with the hand-rolled
percentile bootstrap; and a negative control that drives scipy with the
pre-fix adapter and asserts it fails all of the above. Mutating the
source back to `np.moveaxis(idx_array, axis, 0)` fails **5 of 5**. The
full tier-1 suite is green (1,524 passed, 1 skipped, 3 xfailed), which
also establishes that no existing test had pinned the defective widths.

## Remaining remediation, for PI decision

1. **Re-emission scope.** Unchanged as a decision, but better informed:
   tile-MCC is delivered by the E81 re-emission; F1/precision/recall
   intervals are the real cost. Since no significance verdict depends on
   them, "correct on next touch" is now defensible where it was not
   before.
2. **Erratum E82** for the axis defect, and a separate disclosure for
   the unregistered percentile → BCa migration. The second is the one
   that constrains what the paper may claim.
3. **Do not bundle with E81** — its corrections are landed and
   attributable.

## See also

- **Preceding experiment(s)**: `reports/defect-register-2026-08-18.md` —
  the session's defect list, where this is recorded as D15.
- **Follow-up experiment(s)**: none. The code fix is landed; re-emission
  is pending the PI's decision on scope.
- **Run output directory**: none. This is a defect in an analysis
  instrument, not a run.
- **Working-notes Observations**: none yet.
- **Decisions / Errata**: Decision 10 — registers tile-level percentile
  bootstrap CIs and the CI-excludes-zero rule on differences. E45 —
  unregistered inference method (the precedent for this class of
  disclosure). E54 — the 10,000-iteration convention, which does *not*
  cover the BCa switch. E81 — the correction whose work surfaced this,
  and which incidentally routes tile-MCC off the defective path.

## Changelog

### 2026-08-19 — Adversarial re-examination; mechanism confirmed, three claims corrected, code fixed

**Refresh trigger**: a deliberate attempt to refute the 2026-08-18
record before acting on it, plus the code fix and regression tests it
warranted.

**Confirmed**: the transposition, its exact call shapes, scipy's total
absence of validation, the `sqrt` scaling law, and bit-exact
reproduction of a committed published interval.

**Corrected**:

| Claim (2026-08-18) | Corrected (2026-08-19) |
|---|---|
| "every affected interval too narrow"; error towards false positives | width rescaled by `sqrt(n/B)`; too narrow only at `B > n` (69,663 intervals), too **wide** at `B < n` (840 intervals) |
| "1,520 at B = 10,000 and 101 at B = 1,000" | 1,583 files at B = 10,000; 114 at B = 1,000; 52 undeclared; 76,404 BCa intervals across 1,691 of 1,749 tracked `evaluation.json` |
| "every significance reading resting on a BCa interval is unverified" | true but vacuous — no difference CI is on the BCa path; **0** published significance verdicts change |
| jackknife "meaningless" | precisely: pseudo-values computed over <= 2 distinct tiles; `a_hat` flips sign (−0.000912 → +0.000129); for tile-MCC it goes non-finite and the call falls back to the correct percentile branch |
| "point estimates everywhere" unaffected | holds for `point` fields; `tile_classification.*.mean` is bootstrap-derived (median absolute shift 0.0001, max 0.0024) |

**Unchanged**: the `percentile_fallback` branch is correct and rarely
reached (166 of 76,605 recorded methods); permutation tests and the
Session 136 paired bootstraps are unaffected; F1/precision/recall point
estimates are unaffected.

**Added**: the `B < n` regime; scipy's exact handling; the E81
interaction that spares tile-MCC going forward; the 225-of-1,911
tile-MCC zero-exclusion changes; and the finding that BCa is an
unregistered method independent of this bug (next free erratum: E82).

**Landed**: `122104b8a` — fix in
`scripts/lib_advanced_metrics.py::_bca_ci_from_indices` plus
`tests/test_bca_vectorised_wrapper.py` (5 tier-1 tests, all 5 fail on
the pre-fix source). No committed result re-emitted.

### 2026-08-18 — Original publication

Verified and recorded, not fixed. Mechanism confirmed by reproducing the
wrapper outside the module; magnitude confirmed against a real published
cell at two iteration counts, matching `sqrt(B/n)` at both.
