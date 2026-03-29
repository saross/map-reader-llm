# Audit Report — 5 files, 2026-03-22

**Scope**: All source code changed since last audit (commit `96d17bf`, 2026-03-20)

**Files audited**:

1. `scripts/evaluate_pv_results.py` — new (committed)
2. `tests/test_evaluate_pv_results.py` — new (committed)
3. `scripts/run_phase2.py` — modified (uncommitted)
4. `scripts/compute-pairwise-effect-sizes.py` — new (untracked)
5. `scripts/consensus-sweep-phase3a-high-text.py` — new (untracked)

---

## Critical (must fix)

### 1. `consensus.json` key mismatch — consensus path is non-functional in two scripts

- **Files**: `compute-pairwise-effect-sizes.py:679`, `consensus-sweep-phase3a-high-text.py:736`
- **Category**: Cross-file data format contract
- **Description**: Both scripts read `consensus_data.get("results", {})`, but the producer
  (`run_pv.py`) writes under the key `"consensus"`. `evaluate_pv_results.py` correctly reads
  `"consensus"`. The two standalone scripts silently get an empty dict and fall back to raw
  per-iteration probabilities.
- **Impact**: The consensus override path in these scripts is dead code — they always use
  single-pass probabilities even when consensus data exists. Results labelled as "consensus"
  may not actually use consensus data.

### 2. Deduplication algorithm divergence between scripts

- **Files**: `compute-pairwise-effect-sizes.py:434-449` vs
  `consensus-sweep-phase3a-high-text.py:521-534`
- **Category**: Cross-file consistency / statistical correctness
- **Description**: `compute-pairwise-effect-sizes.py` uses O(N²) greedy pairwise distance,
  while `consensus-sweep-phase3a-high-text.py` uses `scipy.spatial.cKDTree`. These can produce
  different cluster assignments for the same input data.
- **Impact**: Detection counts (and therefore F1 scores) from the two scripts are not directly
  comparable, despite both claiming to implement the same logic from `lib_advanced_metrics.py`.

---

## Medium (should fix)

### 3. `evaluate_pv_results.py:131` — Iteration-level data silently produces all-zero results

- **Category**: Logic error
- **Description**: When `probabilities.json` contains iteration-level keys but no
  `consensus.json` exists, the function logs a warning but returns the iteration-level dict.
  Keys never match `candidate_NNNNN`, so the sweep produces all-zero F1 at every threshold.
- **Impact**: Valid-looking output file with all F1=0 — easy to miss.

### 4. `evaluate_pv_results.py:273-275` — Threshold sweep can miss 1.0 or exceed 1.0

- **Category**: Logic error
- **Description**: `np.arange(0.0, 1.0 + step/2, step)` does not reliably include 1.0 for all
  step sizes (e.g., step=0.3 → `[0.0, 0.3, 0.6, 0.9]`), and can generate >1.0 for others.
- **Impact**: Incomplete sweep with non-default step sizes.

### 5. `run_phase2.py:1909` — `audit_file_storage()` unguarded in `_proactive_sweep()`

- **Category**: Edge case / error handling
- **Description**: `audit_file_storage()` can raise on API errors but is called without
  try/except. The sweep itself succeeds but the diagnostic audit crashes the poll loop.
- **Impact**: A transient API error during a diagnostic call kills the entire batch
  orchestration.

### 6. `run_phase2.py:2078` — Final sweep runs after Ctrl+C

- **Category**: Edge case / UX
- **Description**: After `KeyboardInterrupt`, `_proactive_sweep()` makes further API calls
  before exiting. A second Ctrl+C could produce a traceback.
- **Impact**: Process doesn't exit promptly after operator cancellation.

### 7. `compute-pairwise-effect-sizes.py:1214,1216` — Duplicate comparisons in Group H

- **Category**: Logic error
- **Description**: Two comparisons in Group H are exact duplicates of entries in earlier groups
  (D:1117 and B:1064).
- **Impact**: Wasted compute + inflated denominator for FDR correction, reducing statistical
  power.

### 8. `consensus-sweep-phase3a-high-text.py:1508-1519` — Error results displayed as p=0.0000

- **Category**: Logic error / misleading output
- **Description**: When `bootstrap_effect_size_ci` returns an error dict, the summary prints
  `deltaF1=0.0000 p=0.0000` with no error indication.
- **Impact**: A failed comparison looks like a highly significant result.

### 9. Massive code duplication (~300 lines of metrics functions)

- **Files**: `compute-pairwise-effect-sizes.py` and `consensus-sweep-phase3a-high-text.py` vs
  `lib_advanced_metrics.py`
- **Category**: Cross-file consistency / maintenance
- **Description**: Core functions copied verbatim into standalone scripts, already diverging
  (return format, algorithm choice). Any fix to the library won't propagate.
- **Impact**: Growing silent divergence. Already caused issues #1 and #2.

---

## Low (note for later)

| # | File | Issue |
|---|------|-------|
| 10 | `evaluate_pv_results.py:110-113` | Direct key access on `candidate_id`/`mean_probability` without guard |
| 11 | `evaluate_pv_results.py:111` | `:05d` format assumes integer `candidate_id` |
| 12 | `evaluate_pv_results.py` (9 locations) | `open()` calls lack explicit `encoding="utf-8"` |
| 13 | `compute-pairwise-effect-sizes.py:604` | `load_shared_data()` defined but never called (dead code) |
| 14 | `compute-pairwise-effect-sizes.py:624`, `consensus-sweep-phase3a-high-text.py:802` | `pd.concat(ref_gdfs)` unguarded — crashes unhelpfully if references dir empty |
| 15 | Both standalone scripts: `centroid_from_geometry` | Returns `(0, 0)` for malformed geometries — silent phantom detection |
| 16 | `consensus-sweep-phase3a-high-text.py:831` | `get_run_dirs` doesn't filter non-directory entries — `.DS_Store` etc. crash it |
| 17 | `consensus-sweep-phase3a-high-text.py:1144` | `max(sweep_results)` unguarded against empty list |
| 18 | `compute-pairwise-effect-sizes.py:11` | Docstring claims 25+62 comparisons; actual counts differ |
| 19 | `consensus-sweep-phase3a-high-text.py:43` | Unused `import math` |
| 20 | `test_evaluate_pv_results.py:298-299` | `TestCmdSweepIntegration` marked `tier1` but described as "integration" |
| 21 | `test_evaluate_pv_results.py:306-330` | `test_results_key_unwrapping` duplicates inline logic rather than testing `load_probabilities` |
| 22 | `test_evaluate_pv_results.py:192,242` | Two tests assert count but don't verify *which* candidate survived |

---

## No issues found

- **Security**: No command injection, path traversal, secrets exposure, or unsafe
  deserialisation in any file.
- **UK/AU English**: All files pass — no US spelling violations (only `scipy.optimize` which
  is correctly exempted).
- **Bootstrap methodology**: Consistent across all files (1000 iterations, seed 42, 95% CI,
  paired resampling).
- **CRS/distance threshold**: Consistent (`EPSG:32635`, 20m) across all spatial matching code.

---

## Recommended priority

The **critical** findings (#1 and #2) share a root cause: code duplication from
`lib_advanced_metrics.py` into standalone scripts (#9). The cleanest fix is to refactor the
two standalone scripts to import from the library rather than maintaining divergent copies.
That would eliminate #1, #2, #9, and prevent future drift.

For `run_phase2.py` (#5, #6), wrapping `audit_file_storage()` in try/except and making the
final sweep best-effort are both small, targeted fixes.
