# E82 D41 widening inspection — mechanism, population, options

> **Last revised**: 2026-08-22 (original publication). See [§ Changelog](#changelog) for
> revision history.

**Inspector**: Claude (Opus 5), read-only pass for the Principal Investigator (PI) ruling
requested after the E82 corpus re-emission aborted overnight on 2026-08-21→22.
**Checkout**: `66b6d41a8` (clean tree, local workstation). **Method**: every number below is
derived from committed `evaluation.json` files and from the campaign engine's own code by
importing its selection, recipe-recovery, and gate helpers. The evaluation engine was NOT
run, no `evaluation.json` was modified, and nothing was read from sapphire. Zero API spend.

**Contract under inspection**: `planning/e82-corpus-reemission-2026-08-20.md`
(§ "Resume attempt outcome"). **Engine**: `scripts/rerun_bca_corpus.py`. **Defect register**:
`reports/defect-register-2026-08-18.md` (D41 row).

## Headline

The overnight diagnosis was wrong in an important way, and the news is good.

1. **The six new failures are not D41.** None of the six
   `results/paper-eval/n1/384px-14buf-mcc/` cells publishes run 1's tile point as its summary.
   All six publish the *correct* defined-pass mean. They fail for an unrelated reason:
   the replay resolves their detection passes in **numeric** run order while the committed
   evaluation resolved them in **lexicographic** order, so the `per_run` blocks are
   **permuted** and the gate's `runs_moved` test reads a permutation as moved measurements.
2. **D41 itself is not wider than diagnosed.** A corpus-wide signature scan finds
   **exactly 19** signature-positive cells — precisely the originally diagnosed 19, all under
   `results/paper-eval/mcc/**`. **Zero** new ones anywhere, including in the ~829 worklist
   cells the aborted run never reached.
3. **The one re-failed original cell has a third, separate cause**: a floating-point
   summation-order disagreement at a 4-decimal-place rounding boundary between the gate's
   re-aggregation helper (`sum()/len()`) and the writer's aggregation (`numpy.mean`).

Three distinct causes, three disjoint populations, all fully enumerated: 6 + 19 + 1
(the last overlapping the 19). Nothing else in the corpus is exposed.

## 1. Mechanism confirmation

### 1.1 What the gate actually compares

`gate()` (`scripts/rerun_bca_corpus.py:357-397`) builds three comparisons between the
committed document (`before`) and the replay (`after`):

- `moved` — `point_table()`: `summary.buffers[*].{f1, precision, recall}`, tolerance `1e-9`
  (imported from `scripts/rerun_evals_at_10k.py`). **F1 is compared only at the summary
  buffer level, never per run.**
- `runs_moved` — `per_run_tile_points()`: for each `per_run[i]`, the tile-level
  `mcc`/`sensitivity`/`specificity` `point` values, compared **by list index** with exact
  equality, plus an `n_runs` length check.
- `tile_moved` — `tile_point_table()`: `summary.tile_classification.{mcc, sensitivity,
  specificity}.point` plus the `confusion` counts, exact equality.

The D41 exception is the block at lines 386-392: **if and only if** `tile_moved` is
non-empty **and** `runs_moved` is empty, each moved tile metric whose replayed value equals
`_reaggregated_mean(before, metric)` is popped from the failure set and recorded under
`summary_tile_point_reaggregated`. `confusion` is explicitly skipped (never rescuable), and
any residue fails. All three comparisons feed one failure string — `"point estimates
moved"` — which is why the overnight operator could not tell the three causes apart.

### 1.2 The six n1-tree cells: the D41 signature is absent

For each of the six, the committed summary tile point equals the **defined-pass mean of the
committed per-run points** (the aggregation the current writer produces), not run 1's point:

| n1 cell | runs | metric | summary | run 1 | defined-pass mean | == run 1? | == mean? |
|---|---|---|---|---|---|---|---|
| `flash-image-minimal-t-0-7` | 10 | mcc | 0.3295 | 0.3232 | 0.3295 | no | **yes** |
| | | sensitivity | 0.9982 | 0.9956 | 0.9982 | no | **yes** |
| | | specificity | 0.2101 | 0.2093 | 0.2101 | no | **yes** |
| `pro-text-high-t-0-7` | 10 | mcc | 0.7465 | 0.7412 | 0.7465 | no | **yes** |
| | | sensitivity | 0.7681 | 0.7642 | 0.7681 | no | **yes** |
| | | specificity | 0.9589 | 0.9574 | 0.9589 | no | **yes** |
| `flash-image-high-t-0-7` | 10 | mcc | 0.6019 | 0.6146 | 0.6019 | no | **yes** |
| | | sensitivity | 0.9930 | 0.9825 | 0.9930 | no | **yes** |
| | | specificity | 0.5593 | 0.5930 | 0.5593 | no | **yes** |
| `flash-text-minimal-t-0-0` | 10 | mcc | 0.0459 | 0.0427 | 0.0459 | no | **yes** |
| | | sensitivity | 1.0000 | 1.0000 | 1.0000 | yes (tie) | **yes** |
| | | specificity | 0.0047 | 0.0039 | 0.0047 | no | **yes** |
| `flash-text-minimal-t-0-7` | 30 | mcc | 0.0784 | 0.0742 | 0.0784 | no | **yes** |
| | | sensitivity | 0.9997 | 1.0000 | 0.9997 | no | **yes** |
| | | specificity | 0.0140 | 0.0116 | 0.0140 | no | **yes** |
| `flash-text-high-t-0-7` | 30 | mcc | 0.3314 | 0.3421 | 0.3314 | no | **yes** |
| | | sensitivity | 0.9900 | 0.9913 | 0.9900 | no | **yes** |
| | | specificity | 0.2314 | 0.2403 | 0.2314 | no | **yes** |

The single `== run 1: yes` cell (`flash-text-minimal-t-0-0` sensitivity) is a degenerate tie —
every run scored 1.0000, so run 1's value and the mean coincide. It is not the signature,
which requires equality with run 1 **and** inequality with the mean.

The `confusion` block is likewise identical between summary and run 1 in all six — but that
is the writer's documented, deliberate behaviour (`aggregate_tile_classification`,
`scripts/evaluate_detections.py:341-347`: *"Use the first run's confusion matrix as
representative"*, stamped `confusion_source: "run_1"`), so it reproduces on replay and is
not a failure source.

**Verdict: the "same-symptom" reading in the contract's Resume-attempt-outcome section is
falsified. These six are not D41 cells.**

### 1.3 What actually fails: per-run ORDER, not per-run VALUES

The committed `per_run[*].label` fields carry the source filename stem, so the consumed
order is recoverable from the committed file alone. For
`n1/384px-14buf-mcc/flash-image-minimal-t-0-7`:

```text
committed per_run labels : run01, run10, run02, run03, run04, run05, run06, run07, run08, run09
canonical resolver order : run01, run02, run03, run04, run05, run06, run07, run08, run09, run10
```

That is lexicographic vs numeric ordering, and the two diverge exactly when a pool has ten
or more passes. The predicted `runs_moved` diagnostic for that cell is eight moved indices:

```text
run1: 0.3292 -> 0.3430    run5: 0.3267 -> 0.3151
run2: 0.3430 -> 0.3396    run6: 0.3151 -> 0.3232
run4: 0.3396 -> 0.3267    run7: 0.3232 -> 0.3257
                          run8: 0.3257 -> 0.3302
                          run9: 0.3302 -> 0.3292
```

The **set** of resolved files is identical (verified: `sorted(committed) ==
sorted(predicted)` for all six), the measurements are identical, only their index order
differs. `flash-text-high-t-0-7` and `flash-text-minimal-t-0-7` show the same pattern at 30
runs (`run01, run10, run11, run12, run13, …`).

**Why these cells and not their `mcc/384px` twins.** `build_command()`
(`scripts/rerun_bca_corpus.py:287-316`) computes:

```python
recovered = not (original_cli.get("detections") or original_cli.get("detections_dir"))
...
if recipe.get("glob") and not recovered:
    cmd += ["--glob", recipe["glob"]]
```

The n1-tree cells were scored through `--batch configs/n1-eval-384px-14buf-mcc.yaml`, so
their `cli_args` records `detections: null`, `detections_dir: null` and only
`glob: "*/detections_*.geojson"`. `recover_recipe()` fills `detections_dir` from
`_metadata.input_files.detections`, but `recovered` is computed from the **original** CLI,
so it is `True` and the recorded glob is deliberately dropped in favour of the canonical
resolver (the D6 fix). `resolve_pool_passes()` sorts run directories with `run_sort_key`,
which is numeric (`scripts/lib_detection_paths.py:160-172`). The original batch run used
`sorted(detections_dir.glob(pattern))`, which is lexicographic
(`scripts/evaluate_detections.py:676`). Their `mcc/384px` counterparts record
`detections_dir` explicitly, so `recovered` is `False`, the glob is replayed verbatim, and
the lexicographic order is preserved.

The predictive model is exact: **failure ⟺ (replay uses the canonical resolver) ∧
(n_runs ≥ 10)**. Corpus-wide there are 21 multi-run cells with ≥ 10 runs; 15 replay via the
recorded glob (order preserved) and 6 via the canonical resolver — and those 6 are precisely
the six observed failures. The 12 canonical-resolver cells with ≤ 9 runs are safe only
because lexicographic and numeric order coincide below 10.

A second-order consequence worth recording: for
`n1/.../flash-image-minimal-t-0-7`, `numpy.mean` over the permuted array rounds to 0.3296
where the committed order rounds to 0.3295, so this cell's *summary* mcc point would move
too — but the D41 exception is gated behind `not runs_moved`, so it cannot fire.

### 1.4 Why the existing exception did not catch them

Not a cell list, not a tree path — the exception is **already** a signature test, and the
signature is simply absent:

- It is **not scoped to an explicit cell list**. There is no allow-list anywhere in
  `scripts/rerun_bca_corpus.py`; the exception is purely structural.
- It is **not tree-path-scoped**. Nothing in `gate()` inspects the path.
- It **is** conditioned on `not runs_moved`, and that condition is correct as written: a
  moved per-run measurement must never be forgiven. The six cells trip exactly that guard —
  and they trip it on an artefact of pass ordering rather than on a measurement.

So the exception did not "miss" these cells; they were never in its domain. **The fault is
upstream, in the replay's pass-ordering fidelity, not in the gate's tolerance.**

Test coverage confirms the gap is a blind spot rather than a decision. The three D41 tests
(`tests/test_rerun_bca_corpus.py:377-437`) all build on `_multirun_doc()`: a synthetic
**3-run** document with values (0.3065, 0.2934, 0.3160) whose mean is exactly 0.3053. They
encode the semantics correctly (re-aggregation accepted; a moved per-run point rejected; a
summary point moving to anything but the mean rejected) but exercise neither ≥ 10 runs, nor
a resolver-order mismatch, nor a rounding-boundary mean.

### 1.5 The original-19 cell that re-failed

`results/paper-eval/mcc/384px/flash-image-minimal-t-0-7` is genuinely D41-positive (summary
mcc 0.3232 = run 1's point; correct mean 0.3295). It re-failed on a **third** mechanism:

| quantity | value |
|---|---|
| committed summary mcc point | 0.3232 (= run 1) |
| per-run points (10) | 0.3232, 0.3292, 0.3430, 0.3396, 0.3396, 0.3267, 0.3151, 0.3232, 0.3257, 0.3302 |
| exact sum | 3.2955 |
| writer's aggregate — `round(float(np.mean(vals)), 4)` | **0.3295** (`np.mean` = 0.32954999999999995) |
| gate helper — `round(sum(vals) / len(vals), 4)` | **0.3296** (naive sum = 0.32955) |

`numpy.mean` uses pairwise summation; `_reaggregated_mean`
(`scripts/rerun_bca_corpus.py:351-354`) uses a naive left-to-right `sum()`. The two land on
opposite sides of a 4-dp half-boundary. The replay emits 0.3295; the exception demands
0.3296; the metric is not popped; the cell fails. This is a latent defect **in the exception
itself**, not in the data.

Corpus-wide exposure to this boundary: **365 tile-metric blocks** across all multi-run
worklist cells were re-computed both ways. Exactly **two** disagree, and both trace to the
same 10-pass pool `outputs/h11/pv-diag-384/image-n5/image-t0.7`:

- `results/paper-eval/mcc/384px/flash-image-minimal-t-0-7` — mcc (the re-failure above)
- `results/paper-eval/n1/384px-14buf-mcc/flash-image-minimal-t-0-7` — mcc (masked behind the
  order defect; would surface once ordering is fixed)

## 2. Full population enumeration, corpus-wide

### 2.1 How the population was reconstructed

`select_targets()` was imported directly from the engine and run over
`git ls-files '*evaluation.json'` on this checkout, so the census is the engine's own, not a
re-implementation. Local census:

```text
{selected: 1655, done_1.3: 2, other_vintage: 42, unparseable: 0, no_recipe: 13}
```

The `no_recipe = 13` freeze holds, matching `EXPECTED_SKIPS`. Sapphire's overnight census
was `{selected: 1424, done_1.3: 233, …}`; 1424 + 233 = 1657 = 1655 + 2, so the two checkouts
describe the same population and the local scan is a **superset** of everything the resumed
run will touch — including the ~829 cells the abort never reached. The two locally-`1.3`
cells were checked by hand and are single-run (no `per_run`), so neither defect can apply.

Of the 1655 selected cells, **169 are multi-run** (`len(per_run) ≥ 2`) and therefore capable
of exhibiting either defect; **123** of those carry a summary `tile_classification` block.

### 2.2 D41 signature test (summary tile point == run 1's, and != the defined-pass mean)

Applied to every multi-run worklist cell, per metric, at the gate's own exact-equality
comparison (`tile_point_table` values are already 4-dp rounded, so `1e-9` never binds):

| Population | Count | Where |
|---|---|---|
| (a) The originally diagnosed 19 | **19** | 12 in `results/paper-eval/mcc/384px/`, 7 in `results/paper-eval/mcc/512px/` |
| (b) The six new n1-tree failures | **0** | signature absent — see § 1.2 |
| (c) Further cells not yet reached by the run | **0** | none anywhere in the 1655-cell worklist |
| **Total signature-positive, corpus-wide** | **19** | all under `results/paper-eval/mcc/**` |

The 19, with the metrics that carry the signature:

| Cell (under `results/paper-eval/mcc/`) | runs | signature metrics |
|---|---|---|
| `384px/flash-image-high-t-0-7` | 10 | mcc, sensitivity, specificity |
| `384px/flash-image-minimal-t-0-0-487-tiles` | 3 | mcc, specificity |
| `384px/flash-image-minimal-t-0-3` | 3 | mcc, specificity |
| `384px/flash-image-minimal-t-0-7` | 10 | mcc, sensitivity, specificity |
| `384px/flash-text-high-t-0-7` | 30 | mcc, sensitivity, specificity |
| `384px/flash-text-minimal-t-0-0` | 10 | mcc, specificity |
| `384px/flash-text-minimal-t-0-3` | 3 | mcc, sensitivity, specificity |
| `384px/flash-text-minimal-t-0-7` | 30 | mcc, sensitivity, specificity |
| `384px/pro-image-high-t-0-0` | 3 | mcc, sensitivity, specificity |
| `384px/pro-image-high-t-0-7` | 5 | mcc, sensitivity, specificity |
| `384px/pro-text-high-t-0-0` | 3 | mcc, sensitivity, specificity |
| `384px/pro-text-high-t-0-7` | 10 | mcc, sensitivity, specificity |
| `512px/p2a-brief-text-image` | 3 | mcc, specificity |
| `512px/p2a-image-only` | 3 | mcc, sensitivity, specificity |
| `512px/p2a-verbose-text-image` | 3 | mcc, specificity |
| `512px/p2b-image-t-0-3` | 3 | mcc, sensitivity, specificity |
| `512px/p2b-image-t-0-7` | 3 | mcc, specificity |
| `512px/p2b-image-t-1-0` | 3 | mcc, specificity |
| `512px/p2b-image-t-1-3` | 3 | mcc, specificity |

**The contract's resume criterion "`n_reaggregated` must read 19" is therefore correct as
written** — provided the run reaches all 19. Eighteen were already re-emitted and stamped
1.3 in sapphire's uncommitted working tree (per the contract's Resume-attempt-outcome
record, not independently verified here), so a resumed run will re-visit only
`384px/flash-image-minimal-t-0-7` and should report `n_reaggregated = 1` for this leg,
19 cumulatively.

### 2.3 Pass-ordering defect (the actual new population)

Predicted by reconstructing, for every multi-run worklist cell, the pass sequence the replay
will resolve — using `recover_recipe()`, the same `recovered` test as `build_command()`, and
either `sorted(dir.glob(pattern))` or `resolve_pool_passes()` accordingly — then comparing it
to the committed `per_run[*].label` sequence:

| Replay resolution path | ok | order-permuted | set-differs |
|---|---|---|---|
| Recorded glob replayed verbatim | 145 | 0 | 0 |
| Canonical resolver (batch-recovered rows) | 12 | **6** | 0 |
| Explicit `--detections` list | 6 | 0 | 0 |
| **Total (169 multi-run cells)** | **163** | **6** | **0** |

The six order-permuted cells are exactly, and only:

| Cell (under `results/paper-eval/n1/384px-14buf-mcc/`) | runs |
|---|---|
| `flash-image-high-t-0-7` | 10 |
| `flash-image-minimal-t-0-7` | 10 |
| `flash-text-high-t-0-7` | 30 |
| `flash-text-minimal-t-0-0` | 10 |
| `flash-text-minimal-t-0-7` | 30 |
| `pro-text-high-t-0-7` | 10 |

This reproduces the observed failure list exactly — six predicted, six observed, no false
positives and no false negatives — and **zero set-differs** means no cell in the corpus
would silently score a different pool. All six were already reached by the aborted run; there
are no further order-permuted cells hiding in the unprocessed remainder.

### 2.4 Combined exposure for the resumed run

| Cause | Population | Already re-emitted | Still to clear |
|---|---|---|---|
| D41 mis-aggregation (§ 2.2) | 19 | 18 | 1 |
| Pass-order permutation (§ 2.3) | 6 | 0 | 6 |
| `sum()` vs `np.mean` boundary (§ 1.5) | 2 cells, 1 metric each | 0 | 2 (1 shared with D41, 1 with order) |
| **Distinct cells still failing on resume** | | | **7** |

Seven is above the `MAX_FAILURES = 5` abort threshold, so a resume without a code change
aborts again — and, because the campaign is ~842 of 1424 through, it would abort having made
progress but no headway on this class.

## 3. Options for the ruling

Not implemented. Presented for the PI's decision.

| # | Option | What changes | Trade-offs |
|---|---|---|---|
| **A** | Widen the D41 exception to an enumerated cell list and bump the expected re-aggregation count | An explicit allow-list of the 19 + 6 cells in `rerun_bca_corpus.py`; contract's "must read 19" becomes 25 | Auditable and frozen, and a new same-symptom cell would still stop the run. **But it does not work here**: the six are not D41 cells, so forgiving their `tile_moved` does nothing — their failure is `runs_moved`, which no D41 widening reaches. Also leaves the § 1.5 boundary bug live. **Not recommended on the evidence.** |
| **B** | Replace the list with the signature test as the exception condition | No change — the exception **is** already the signature test (§ 1.4), with no list to replace | Nothing to do. The distinction the option was reaching for (does the signature let genuinely-moved estimates through?) is already answered by `not runs_moved`: the per-run measurements must reproduce **exactly**, so a real change in the data can never be re-labelled as re-aggregation. That guard should be kept. |
| **C1** | **Fix the ordering upstream — index per-run blocks by `label`, not position** (recommended) | In `per_run_tile_points()` / `gate()`, key each run's tile points by its `label` and compare label-keyed maps (falling back to index when labels are absent or non-unique) | Compares measurements to the *same* measurement rather than to whichever pass happens to sit at that index. Clears all six with no tolerance loosening: a genuine change still moves a labelled value, and a changed pool still shows as a differing label set (which the check should report as a failure). Small, testable, and independent of pass count. Requires `label` to be present and unique per run — verified true for all six, and label mismatch is itself a failure signal. |
| **C2** | Fix the ordering upstream — replay the recorded glob for batch-recovered rows too | Drop the `and not recovered` clause in `build_command()` | Restores the exact consumed order, one-line change. **But it re-opens D6**: the recorded glob `*/detections_*.geojson` is convention-A-only and silently under-reads mixed pools, which is the defect `lib_detection_paths` exists to prevent. Safe for these six (glob and resolver return the same set), unsafe as a rule. Not recommended alone. |
| **C3** | Fix the ordering upstream — sort committed and replayed per-run rows into canonical order before comparison | Sort both `per_run` sequences by `run_sort_key`-equivalent before the index-wise compare | Same effect as C1 with slightly less information: it tolerates a permutation but cannot say *which* pass changed if something genuinely moves. C1 dominates. |
| **D** | Fix `_reaggregated_mean` to match the writer's aggregation exactly | Use `round(float(np.mean(vals)), 4)` in `_reaggregated_mean`, mirroring `aggregate_tile_classification` | Required regardless of which ordering option is taken, otherwise `mcc/384px/flash-image-minimal-t-0-7` fails a third time. It **tightens** rather than loosens: the helper stops disagreeing with the very function whose output it is meant to predict. Two cells affected corpus-wide, both enumerated in § 1.5. |
| **E** | Do nothing to the gate; accept the seven cells as permanent failures and exclude them | Contract records 7 non-re-emitted cells; the rest of the corpus completes | Cheapest, but leaves seven cells at pre-fix B and stale intervals for no scientific reason — the six order cells contain no defect at all, only a comparison artefact. Also leaves `MAX_FAILURES` primed to abort unless the seven are pre-skipped. |

**Recommended combination**: **C1 + D**, with the contract's expected-re-aggregation count
left at 19 and a new expected-order-normalisation count of 6 recorded alongside it. That
clears all seven remaining failures, loosens no measurement tolerance, and adds two
regression tests the current suite lacks (a ≥ 10-run pool whose committed labels are in
lexicographic order; a per-run mean sitting on a 4-dp half-boundary).

**On the "does the signature distinguish genuine movement?" question** (the PI's concern in
option B): yes, and it does so through `runs_moved`, not through the signature itself. The
per-run tile points are the actual measurements; the summary point is a derived aggregate.
The exception forgives only a *derived* value, and only when it equals the aggregate the
current writer would compute from per-run values that have **all** reproduced exactly. A
genuinely moved estimate necessarily moves at least one per-run point, which disables the
exception entirely. Option C1 preserves that property — it changes only *which committed run*
each replayed run is compared against, from "the one at the same index" to "the one from the
same file".

## Anti-confabulation note

Every count, filename, and numeric value above was computed within this session from files
at `66b6d41a8` and can be re-derived without network access. Two classes of claim are **not**
independently verified here and are attributed rather than asserted: (i) the overnight run's
tallies (`n_ok 588`, `n_reaggregated 18`, `n_no_ci 2`, median 4.66) and the identity of the
six failing cells, which come from
`planning/e82-corpus-reemission-2026-08-20.md` § "Resume attempt outcome" — the run report
JSON `results/e82-corpus-reemission-2026-08-20.json` exists only on sapphire and was not
consulted; and (ii) sapphire's uncommitted working-tree state. The six failing cells named in
the contract are, however, corroborated independently: the § 2.3 scan predicts exactly that
set from committed data alone.

## See also

- **Contract**: `planning/e82-corpus-reemission-2026-08-20.md` (§ "Resume attempt outcome",
  § "Resume runbook")
- **Engine**: `scripts/rerun_bca_corpus.py`; helpers in
  `scripts/build_bca_migration_queue.py`, `scripts/rerun_evals_at_10k.py`
- **Resolver**: `scripts/lib_detection_paths.py` (D6); consumer at
  `scripts/evaluate_detections.py` `find_detection_files()`
- **Writer aggregation**: `scripts/evaluate_detections.py` `aggregate_tile_classification()`
- **Defects**: `reports/defect-register-2026-08-18.md` — D41 (this row needs correcting: its
  scope is 19, not "wider"), D6 (resolver), D40 (input-vintage drift)
- **Tests**: `tests/test_rerun_bca_corpus.py:377-437` (the three D41 cases)

## Changelog

### 2026-08-22 — Original publication

Written for the PI ruling requested after the E82 corpus re-emission aborted at more than
five failures on the night of 2026-08-21→22. Read-only inspection of committed data at
`66b6d41a8`; the evaluation engine was not run and no `evaluation.json` was modified.

Findings at publication: the six new `results/paper-eval/n1/384px-14buf-mcc/` failures are
**not** D41 — their summary tile points are correctly aggregated, and they fail on a
per-run **ordering** mismatch between the canonical resolver (numeric) and the original
batch glob (lexicographic), which bites only at ≥ 10 passes. The D41 signature population is
**19 corpus-wide** — the originally diagnosed set exactly, with zero new cells in the
~829 worklist cells the aborted run never reached. The one re-failed original cell
(`results/paper-eval/mcc/384px/flash-image-minimal-t-0-7`) fails on a third cause: a
`sum()`-vs-`numpy.mean` rounding-boundary disagreement inside `_reaggregated_mean`,
affecting exactly two cells corpus-wide. Six options tabled; C1 (label-keyed per-run
comparison) + D (align the helper's aggregation with the writer's) recommended.

No prior revision — this is the baseline for future diffs.
