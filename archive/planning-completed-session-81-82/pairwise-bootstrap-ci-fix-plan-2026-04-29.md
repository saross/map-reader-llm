# Pairwise tile-size-30m bootstrap-CI fix — implementation plan

> **⚠️ SUPERSEDED 2026-05-01.** This planning document is preserved
> for historical reference. The work it describes was executed in
> Session 81 (sparse-coverage suppression patch landed at commit
> `2026999a`; in-plan checklist marked DONE at commit `2ac81876` on
> 2026-05-01); see `planning/paper-writeup-continuity.md`
> §"Session 81 closure roll-up" for the current state, and the
> codified mitigation in `scripts/evaluate_detections.py`
> (sparse-coverage suppression block) plus
> `scripts/lib_advanced_metrics.py` for the canonical implementation.
> Do not act on items in this file as if they are pending.

**Date**: 2026-04-29  
**Author**: Claude Opus 4.7 (1M context), via Plan agent  
**Status**: Plan-only, not yet executed  
**Scope**: `results/pairwise/tile-size-30m/` (5 cells × 2 buffers = 10
cell × buffer combinations, 9 of 10 affected)

## 1. Executive summary

Five cross-grid evaluation cells under `results/pairwise/tile-size-30m/`
emit bootstrap 95 % confidence intervals (CIs) that exclude their own F1
point estimates. Empirically, 74.5 % – 83.4 % of the 487 evaluation tiles
have zero true-positive (TP), false-positive (FP), and false-negative
(FN) counts in these cells, far above the ~10 % seen in matched-grid
evaluations. The percentile bootstrap, when resampling sparse signal
across a large empty pool, centres the bootstrap distribution below the
all-data F1 point estimate.

This plan recommends **Mitigation 3 only** (transparent flagging) for
immediate landing: a coverage check inside `bootstrap_ci`, an
`unreliable_ci` flag in `evaluation.json`, and CI suppression in
the rendered Markdown / Comma-Separated Values (CSV) outputs. The
methodologically heavier **Bias-Corrected and Accelerated (BCa)** bootstrap is
deferred as an optional follow-up — it would only modify the 5 cells
already flagged as a methodological caveat in commit `52e6c40d`, the
primary statistical comparison for this subtree uses paired McNemar /
permutation in `tile-size-mcnemar-30m`, and the BCa-vs-mitigation
trade-off (effort + dependency on `scipy.stats.bootstrap`) does not pay
back on a 5-cell scope. Estimated effort: ~3 hours coding + tests; LOC
delta ≤ 80.

## 2. Bug recap and root cause

`scripts/lib_advanced_metrics.py:560-638` (`calculate_f1_internal`)
computes F1 globally over **all 487 tiles** by summing per-tile TP / FP
/ FN, then deriving precision and recall from totals. The companion
`bootstrap_ci` (lines 641–719) at line 690 resamples
`tiles, n_tiles, replace=True` then calls `aggregate_tile_metrics`
(lines 511–557), which sums TP / FP / FN across the **bootstrap
sample only**. With 487 tiles and ~80 % zero-count tiles in the cross-grid
configuration, the bootstrap distribution centres below the all-data
F1: e.g. `512px-image-t0` @ 30 m has F1 = 0.5710 but bootstrap CI
[0.2054, 0.5141]; the point lies **0.057 above** the upper bound.
Five-cell summary measured live (n_tiles = 487, n_zero = tiles with
TP = FP = FN = 0):

| Cell | 20 m zero % | 30 m zero % |
|---|---|---|
| 512px-image-t0 | 76.8 % | 80.7 % |
| 512px-image-t07 | 74.5 % | 80.5 % |
| 512px-text-t0 | 81.9 % | 83.4 % |
| 512px-text-t07 | 81.7 % | 82.5 % |

(`eval-512-on-384-image-t0` is the 3-run mean of `512px-image-t0` runs;
its coverage matches.) Matched-grid baselines (e.g. 384 px image-t0 on
the same 487-tile bounds) are 0.2 % – 11.1 % zero-coverage, so a
mid-range threshold cleanly separates the two regimes.

## 3. Recommended solution — Mitigation 3 only

**Rationale**: Mitigation 3 is faithful to what we already know — the
prior commit `52e6c40d` ("data(results): add 512px vs 384px tile size
comparison") explicitly notes the methodological caveat in its commit
message, and the primary statistical inference for this subtree
(McNemar + paired permutation) lives in
`results/pairwise/tile-size-mcnemar-30m/`, not in the per-cell
percentile bootstrap. Mitigation 3 turns an implicit caveat into an
explicit, machine-readable flag (`unreliable_ci` per buffer + per cell)
without changing any number that downstream analysis or the paper
already relies on.

### 3.1 Why not BCa (now)

- **Scope**: BCa would only ever fix these 5 cells. The other 540 cells
  in the active matrix already have well-behaved percentile bootstraps
  (point estimate inside CI). Spending 2–3 h on BCa to "rescue" 5 cells
  whose primary inference is paired-tile McNemar is poor value for
  effort.
- **Methodological precision**: BCa is calibrated for moderate
  bias-and-skew, not for the regime where ~80 % of resampling units
  contribute zero signal. With this much sparsity, the bootstrap is
  near-degenerate at the upper tail; bias-correction tightens the lower
  bound but does not necessarily restore valid coverage. We would still
  want to flag these cells.
- **Dependency surface**: `scipy.stats.bootstrap` (scipy ≥ 1.7) is
  already in the environment (`scipy.optimize.linear_sum_assignment` is
  imported in `lib_advanced_metrics.py:31`), but BCa requires
  jackknife evaluation of the statistic on n−1 leave-one-out samples,
  approximately doubling per-call cost and complicating the pre-computed
  per-tile counts pipeline.
- **Disagreement with prior diagnosis**: the prior diagnosis
  recommended Mitigation 3 + Fix 1 (BCa). I confirm Mitigation 3,
  refute the simultaneous BCa investment for this scope, and recommend
  re-evaluating BCa **only if** the user later requests percentile-bootstrap
  CIs to be the primary inference for cross-grid comparisons (which they
  are not at present).

### 3.2 Why not BCa-only

The "skip the mitigation" option would replace the percentile CI with
BCa unconditionally for *all* `bootstrap_ci` callers, not just the 5
affected cells. That is a global methodology change touching every
paper-cited cell — a much larger blast radius requiring re-running the
N=10K sweep on all 165 / 540 cells (per
`archive/planning-completed-session-81-82/daylight-followup-sweep-plan-2026-04-29.md` §7.3 – §7.5).
Out of scope for this fix.

## 4. Implementation design

### 4.1 Coverage check inside `bootstrap_ci`

Add a `coverage_threshold: float = 0.5` argument and emit a per-call
diagnostic. Computed once on the pre-computed `tile_metrics` DataFrame
(no extra passes).

```python
total_per_tile = tile_metrics["tp"] + tile_metrics["fp"] + tile_metrics["fn"]
n_zero = int((total_per_tile == 0).sum())
zero_fraction = n_zero / max(len(tile_metrics), 1)
unreliable = zero_fraction >= coverage_threshold
```

Returned dict gains a top-level `coverage` block (alongside the
existing `f1`, `precision`, `recall`, `n_iterations` keys):

```python
"coverage": {
    "n_tiles": int(n_tiles),
    "n_zero_count_tiles": int(n_zero),
    "zero_fraction": float(zero_fraction),
    "threshold": float(coverage_threshold),
    "unreliable_ci": bool(unreliable),
}
```

The percentile CI bounds are still computed and returned (callers may
inspect them), but consumers that respect the flag will suppress
display.

### 4.2 Coverage threshold — recommended value: 0.50

- Cross-grid affected cells measured: 74.5 % – 83.4 % zero-tile
- Matched-grid baselines measured: 0.2 % – 11.1 % zero-tile

A threshold of **0.50** sits ~40 percentage points above the worst
matched-grid case and ~25 points below the least-sparse affected cell,
giving a comfortable margin in both directions. The brief proposed
0.30 (per the prior diagnosis); 0.30 also discriminates these cells
correctly but offers a smaller margin against future matched-grid cells
with naturally sparse map coverage. **Open question for user**: confirm
0.50 or revise to 0.30. The threshold is a configuration knob (default
in code, not hard-coded), so it can change later without re-running.

### 4.3 Per-buffer flag plumbed through `evaluate_single_run`

In `scripts/evaluate_detections.py:338-356` (the `bootstrap_ci` call
inside `evaluate_single_run`), surface the new fields into each
`buffer_results` entry:

```python
buffer_results.append({
    "buffer_metres": buffer_m,
    "f1": round(f1, 4),
    "f1_ci_lower": round(ci["f1"]["ci_lower"], 4),
    "f1_ci_upper": round(ci["f1"]["ci_upper"], 4),
    # ... existing precision/recall fields ...
    "ci_coverage": ci["coverage"],
    "ci_unreliable": ci["coverage"]["unreliable_ci"],
})
```

The flag is per buffer, because in principle one buffer's TP / FN
matching can be sparser than another's (though for these 5 cells both
20 m and 30 m fire). This is the right granularity.

### 4.4 Optional cell-level rollup

`evaluate_single_run` returns a `result` dict; add a sibling key:

```python
result["bootstrap_ci_unreliable_any_buffer"] = any(
    b.get("ci_unreliable", False) for b in buffer_results
)
```

This gives consumers (paper tables, analysis notebooks) a one-shot
boolean per cell without scanning each buffer entry.

### 4.5 CI suppression in `evaluation.md` and `evaluation.csv`

In `evaluate_detections.py:602-654` (the Markdown table writer):

- **Markdown rendering** — when `buf.get("ci_unreliable", False)`, emit
  the CI columns as `N/A *` and append a footnote to the file:

  ```markdown
  | 30m | 0.571 | N/A * | 0.445 | N/A * | 0.795 | N/A * |
  
  \* Bootstrap CI suppressed: 80.7 % of tiles have zero TP/FP/FN counts
  (≥ 50 % threshold). Per-cell McNemar / paired permutation in
  `tile-size-mcnemar-30m/` is the primary inference for this comparison.
  ```

- **CSV rendering** — add three new columns (`ci_zero_fraction`,
  `ci_unreliable`, `ci_n_tiles`) so the flag is machine-readable. Keep
  the numeric `f1_ci_lower` / `f1_ci_upper` values populated even when
  unreliable, so downstream tooling that already reads them does not
  break (the new boolean column is the contract for "do you trust
  these?").

### 4.6 Out-of-scope siblings (noted, not modified)

`scripts/lib_advanced_metrics.py` contains 7 other
`rng.choice(..., replace=True)` callsites at lines 690 (the one we
modify), 793, 899, 1014, 1149, 1385, 1500. These belong to
`bootstrap_effect_size_ci`, `bootstrap_multi_run_ci`,
`bootstrap_multi_run_effect_size_ci`, `bootstrap_interaction_ci`,
`bootstrap_tile_classification_ci`, `bootstrap_tile_effect_size_ci`.
None are called for the 5 affected cells. Plan does **not** propagate
the coverage check to them — that is a deliberate scope limit,
revisitable if future analyses surface analogous sparsity in
multi-run / effect-size paths.

## 5. Test design

All new tests live in `tests/test_advanced_metrics_coverage.py` (new
file) under `pytest.mark.tier1`. Pattern follows
`tests/test_analyse_phase2.py`'s synthetic-data idioms.

### 5.1 Test 1 — sparse coverage flags as unreliable

Construct 100 tiles where only 20 have any reference; place all 20
detections at one extreme corner. Expect `unreliable_ci` = True with
default threshold 0.5.

```python
def test_bootstrap_ci_flags_sparse_coverage(self) -> None:
    """When ≥50 % of tiles have zero TP/FP/FN, flag CI as unreliable."""
    run_gdfs, gdf_ref, gdf_bounds = _make_sparse_synthetic(
        n_tiles=100, n_active=20, seed=42,
    )
    _, gdf_det = run_gdfs[0]
    result = bootstrap_ci(gdf_det, gdf_ref, gdf_bounds, n_iterations=200)
    assert result["coverage"]["zero_fraction"] >= 0.5
    assert result["coverage"]["unreliable_ci"] is True
```

### 5.2 Test 2 — dense coverage does not flag

Use the existing `_make_synthetic_runs(n_tiles=10, ...)` helper where
every tile has detections and references. Expect
`unreliable_ci` = False.

```python
def test_bootstrap_ci_does_not_flag_dense(self) -> None:
    """When all tiles have non-zero counts, do not flag."""
    run_gdfs, gdf_ref, gdf_bounds = _make_synthetic_runs(
        n_runs=1, n_tiles=10, detections_per_tile=2, seed=42,
    )
    _, gdf_det = run_gdfs[0]
    result = bootstrap_ci(gdf_det, gdf_ref, gdf_bounds, n_iterations=200)
    assert result["coverage"]["zero_fraction"] < 0.5
    assert result["coverage"]["unreliable_ci"] is False
```

### 5.3 Test 3 — boundary at threshold

Construct a fixture with exactly 50 % zero-coverage; expect
`unreliable_ci` = True (using `>=` semantics) and revise if the user
prefers strict `>`.

### 5.4 Test 4 — `evaluate_single_run` propagates the flag

Mock `bootstrap_ci` to return `coverage.unreliable_ci = True`; assert
each `buffer_results` entry contains `ci_unreliable = True` and
`bootstrap_ci_unreliable_any_buffer = True` on the result dict.

### 5.5 Test 5 — Markdown / CSV writer suppression

Extend `tests/test_evaluate_detections_mcc_rendering.py`:

- A buffer block with `ci_unreliable = True` produces `N/A *` cells in
  the Markdown CI columns and a footnote line.
- A buffer block without the flag (legacy shape) renders as today
  (regression guard for back-compat).
- The CSV gains `ci_unreliable` / `ci_zero_fraction` / `ci_n_tiles`
  columns; numeric CI columns remain populated.

### 5.6 Existing tests to not break

- `test_analyse_phase2.py::test_bootstrap_ci_contains_point_estimate`
  (line 801) currently asserts the point estimate lies in the CI on
  dense synthetic data. Should pass unchanged — we do not modify the
  percentile computation, only add a sibling `coverage` block.
- `test_evaluate_detections_mcc_rendering.py` legacy shapes must keep
  rendering byte-identical when the new flag is absent.

## 6. Migration path for the 5 affected cells

**Recommendation: re-run `evaluate_detections.py` on each cell to
populate the new flag in-place.**

### 6.1 Why re-run rather than annotate by hand

- The 5 cells are tiny — 1 detection geojson per cell, 20 m + 30 m
  buffers, ~5–10 s CPU each, ~1 min total. The
  `daylight-followup-sweep-plan-2026-04-29.md` §6 already costed this
  group at "5 pairwise cells × ~5–10 s ≈ 1 min single-thread".
- Re-run keeps `evaluation.json`, `evaluation.csv`, `evaluation.md`
  in sync; manual annotation creates drift between the JSON and the
  rendered Markdown.
- A pre-tag (e.g. `pre-bootstrap-ci-coverage-flag-2026-04-29`) plus a
  per-cell commit makes rollback trivial if needed.

### 6.2 Step-by-step

1. Tag current `HEAD` as `pre-bootstrap-ci-coverage-flag-2026-04-29`
   (mirrors the convention of `pre-bootstrap-10k-followup-2026-04-29`).
2. Implement the code changes (§4) on a feature branch; merge to
   `main`.
3. On `sapphire`, with the feature branch checked out, re-run
   `evaluate_detections.py` for each of the 5 cells using the recorded
   invocation in `results/pairwise/tile-size-30m/.metadata.json`
   (line 25 — `command_shape`):

   ```bash
   python scripts/evaluate_detections.py \
     --detections <per-cell> \
     --buffers 20 30 \
     --bootstrap 1000 \
     --seed 42 \
     --ground-truth inputs/vectors/references/mounds-reference.geojson \
     --bounds inputs/vectors/bounds/384/full_evaluation_bounds.geojson \
     --output-dir results/pairwise/tile-size-30m/<cell>
   ```

4. Verify each cell's `evaluation.json` now has the `ci_coverage`
   block on each buffer entry and `ci_unreliable = True` for both
   buffers. Verify `evaluation.md` shows `N/A *` and the footnote.
5. Commit per-cell or one-commit-for-all-five with message
   `data(pairwise-tile-size-30m): annotate sparse-coverage CIs`.
6. Update `results/pairwise/tile-size-30m/.metadata.json` to bump
   `metadata_version` to `1.1` and add a
   `coverage_check: { threshold: 0.5, unreliable_cells: [...] }` block.

### 6.3 Paper-side trade-off

The paper's tile-size comparison narrative already cites the McNemar +
paired permutation result as primary (per the commit `52e6c40d`
methodological caveat). The plan does not require any paper revision;
the per-cell `evaluation.md` will simply show suppressed CI columns
where it currently shows numerically-misleading bounds. If the paper
previously cited the percentile CIs from these cells (it should not,
per the caveat), the user should note this for the next manuscript
pass.

## 7. Effort estimate

| Item | Lines of Code | Wall time |
|---|---|---|
| `bootstrap_ci` coverage block + threshold arg | ~25 | 30 min |
| `evaluate_single_run` per-buffer plumbing + cell rollup | ~10 | 15 min |
| `write_outputs` Markdown N/A * + footnote | ~20 | 30 min |
| `write_outputs` CSV columns | ~10 | 15 min |
| New file `tests/test_advanced_metrics_coverage.py` (5 tests) | ~120 | 60 min |
| Extend `test_evaluate_detections_mcc_rendering.py` | ~40 | 20 min |
| Re-run 5 cells on sapphire + commit + tag | n/a | 20 min |
| Linting (`ruff`, `markdownlint`) + manual diff review | n/a | 20 min |
| **Total** | **~225 LOC** | **~3 h 30 min** |

Production (Mitigation 3 only) is well within a single session. The
optional BCa follow-up, if ever pursued, is +3 h with separate tag and
rollback.

## 8. Pre-launch checklist

> **Status 2026-05-01**: all checklist items closed. Implementation
> landed at commit `2026999a` (BCa + Mit-3 sparse-coverage flag in
> `scripts/lib_advanced_metrics.py`). Verified 2026-05-01 via post-hoc
> audit on pairwise cells (metadata v1.1, BCa method, `ci_unreliable`
> flag populated).

- [x] Coverage threshold confirmed with user (0.5 default vs 0.3
  prior-diagnosis proposal). **DONE — 0.50 implemented in `2026999a`.**
- [x] `pre-bootstrap-ci-coverage-flag-2026-04-29` tag created on `main`
  before any code change. **DONE — actual tag created is
  `pre-bca-mit3-2026-04-29` (renamed during implementation to reflect
  the combined BCa + Mit-3 scope).**
- [x] All 5 unit tests pass on synthetic data; existing
  `test_bootstrap_ci_contains_point_estimate` still passes. **DONE
  — 24 new tests added; all 839 tier-1 tests pass per Session 81
  closure roll-up.**
- [x] `evaluation.md` / `.csv` rendering byte-identical for cells that
  do **not** trip the flag (regression guard). **DONE — no regression
  flagged during Session 81 BCa migration sweep across all 526 cells.**
- [x] Re-run on sapphire of the 5 cells produces non-empty
  `ci_coverage` block in each `evaluation.json`. **DONE — 5 tile-size
  cross-grid pairwise cells under `results/pairwise/tile-size-30m/`
  re-evaluated; `ci_unreliable` flag populated.**
- [x] `.metadata.json` sidecar updated with threshold + flagged-cell
  inventory. **DONE — metadata v1.1 schema in place across all
  evaluations.**

## 9. Open questions for the user

1. **Threshold**: 0.50 (recommended) or 0.30 (prior diagnosis)? Either
   works; 0.50 has cleaner separation from observed matched-grid
   maxima (~11 %).
2. **BCa follow-up**: Is the McNemar + paired permutation in
   `tile-size-mcnemar-30m/` confirmed as the primary inference, so we
   can defer BCa indefinitely? Or is a percentile-replacement BCa run
   wanted as a paper-supplement table?
3. **Boundary semantics**: `>= threshold` triggers (recommended) or
   strictly `> threshold`? The brief said ">30 %" which implies strict,
   but `>=` simplifies the boundary test.
4. **Cell-level vs buffer-level flag**: I propose **both** (per-buffer
   `ci_unreliable` + cell-level
   `bootstrap_ci_unreliable_any_buffer`). Confirm this is what is
   wanted, or restrict to per-buffer only.
5. **Apply the flag retroactively to the 5 existing cells** (re-run,
   recommended) **or leave them as paper-side notes only**? Re-running
   is the cleanest; ~1 min compute on sapphire.
