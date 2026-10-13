# Superseded W2.7 floors files (archived 2026-10-12)

PI ruling D60 (4) (`planning/pi-decisions-2026-09-20.md`) rebuilt the
floors-v2 `FastScorer` on the shared library's attribution and regenerated
W2.7 § 6 and § 6b of `reports/w27-replicate-floors-2026-10-06.md` under the
current scorer (`scripts/lib_advanced_metrics.py` as merged in PR #29,
`b9b42c79b`: ruling D50's detection scope). The files below are the versions
those regenerations replaced, kept so the before and after can be compared
in the working tree. The report's changelog entry of 2026-10-12 gives the
numbers that moved.

- `floors-v2/floors2_lib.py`: the pre-D50 `FastScorer` (created
  2026-10-07, `a4b5734cb`). It split detections by `source_tile` prefix,
  with no geometric scope and no origin restoration, and so reproduced the
  pre-D50 scorer. `floors-v2/floors2_scorer_gate.py` loads it from here as
  its red sentinel: it must fail the live-library gate on the § 6 cells the
  D50 rule moved.
- `w27-replicate-floors-2026-10-06-scripts/`: the § 6 outputs written on
  2026-10-06 (`c84cfa378`) by `w27_55map_subset_replicates.py` under the
  pre-D50 scorer: `subset_cells.json`, `subset_pairs.csv`, `gates.json` and
  the run log `map55_run.log`.
- `w27-replicate-floors-2026-10-06-scripts/floors-v2/`: the § 6b outputs
  written on 2026-10-07 (`a4b5734cb`) with the pre-D50 `FastScorer`: the
  `results/` files the regeneration rewrote and the run logs.

Nothing here is read by the current pipeline except the sentinel's
`floors2_lib.py`.
