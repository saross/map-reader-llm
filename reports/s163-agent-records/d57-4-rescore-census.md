# D57 (4) re-score: OLD-scorer census of committed evaluations

> **Last revised**: 2026-10-10 (original publication). See
> [§ Changelog](#changelog) for revision history.

- **Executed by**: Claude (Anthropic), Claude Code, model lane Opus 5.5
  (`claude-opus-5-5`), a subagent of the main Session 163 session, on
  sapphire, 2026-10-09 12:14–15:23 UTC (22.45 CPU-hours).
- **Repository**: `map-reader-llm`. Committed values read from git at
  `494b5a7af`; `results/` and `archive/` are identical across
  `b3c52591d`..`ea5d0b602`.
- **Scorer replayed**: OLD, `git archive b3c52591d` (before D50).
- **Question**: the archived spot check that failed under D57 (4) (an
  interval from before E72) — does a systematic class of committed
  intervals fail to reproduce? If OLD reproduces a committed file exactly,
  every change in its regenerated NEW twin is D50 alone.
- **Where the outputs are**: `~/scratch/d57-4-rescore-2026-10-09/census-old/`
  on sapphire — `out/census_cells.csv` (2,800 rows with disposition,
  result, cause, provenance, conditions, and analyses), `out/nonrepro.csv`
  (76 rows), `out/census_summary.json`, `out/compare.{json,csv}`,
  `out/plan.json`, `out/queue.json`, `scripts/` (6 files), and the replays.
- **Guarantees**: no repository or worktree was modified, nothing was
  committed, and no model Application Programming Interface (API) was
  called.
- **Comparison**: the whole `summary` plus every `per_run` block, exact
  equality, `detection_scope` excluded. A red sentinel (a NEW-regenerated
  cell against its committed file) was flagged as different.

## ⚠ Sapphire has a memory fault

**Found during this run.** The main session confirmed the kernel-log
entries and the bit-34 signature at source; the rates and temperatures are
the agent's readings.

- `/var/log/kern.log` on sapphire carries five
  `BUG: Bad page state in process python` reports ("page does not match
  folio", "compound_head not consistent"): 2026-10-05T04:14:24Z, then
  2026-10-09T13:51:41Z, 14:21:18Z, 14:22:15Z, and 15:22:55Z.
- 22 census replays died in scipy's bootstrap resampling with indices such
  as `17179869230` "out of bounds for axis 0 with size 8541". Every such
  index is 2^34 (17,179,869,184) plus a valid offset: **the same bit, bit
  34, set in a 64-bit integer**. With seed 42 a software defect would recur
  at the same place, and these cells scored cleanly before. The Phase 4
  agent hit the same signature independently
  (`IndexError: index 17179872156`, 2^34 + 2,972), and a re-run of that
  command reproduced cleanly.
- Rate: 1 of 119 such cells failed before 14:10Z, then 21 of 46 after.
- Sapphire registers no EDAC (error detection and correction) controller;
  the Ryzen 9 7900 is probably on non-ECC memory. DIMMs read 48–49 °C and
  CPU Tctl 69 °C at 14:26Z. Instability under sustained load (for example a
  memory overclock profile) is a hypothesis only.
- The census stopped its load at 14:24Z, then ran only small-frame cells
  under a stop file, halt-on-failure, and a kernel-log tripwire, which
  fired at 15:22:55Z after 817 clean cells. No census process is running.

**What it means.** An exact reproduction cannot arise from corruption, so
every "reproduced exactly" below stands, and so do Run B and Run C's
byte-identical files (Phase 4 record). A single set bit is loud in an
integer (a crash) but nearly silent in a 64-bit float, where bit 34 is a
mantissa bit worth about 4 parts in a million of the value — below the
four decimals the documents quote, but enough to break a byte-for-byte
comparison. Values computed on sapphire and never checked against an
independent computation are therefore unverified, including the
D57 (4) Phase 2 NEW files in draft PR #29 (computed about 09:35–10:15Z,
before today's first kernel report but after the 2026-10-05 one).

## Counts

Classified set: 2,751 frames-measurement cells (2,727 scored plus 24
diagnostics-only).

| Disposition | Cells |
|---|---:|
| `archive/**`, excluded (includes the 26th drifted cell) | 54 |
| Already verified by the S2 byte-diff, not replayed | 432 |
| Already verified as Q2 Stage A cells, not replayed | 25 |
| No recipe (adapter cells without `_metadata.cli_args`) | 24 |
| Replayable | 2,216 |

A further 49 rows of `out/census_cells.csv` are unclassified (2,800 rows
in all).

Of the 2,216 replayable cells (737 Phase 2, 1,479 other):

| Result | Phase 2 | Other | Total |
|---|---:|---:|---:|
| Reproduced exactly | 695 | 1,009 | 1,704 |
| Not reproduced | 42 | 12 | 54 |
| Replay crashed (memory fault) | 0 | 22 | 22 |
| Not run (325 small-frame halted by the tripwire, 111 deferred 55-map) | 0 | 436 | 436 |

Vintage replays of the E82-pinned drifted cells: 17 of 17 small-frame
ones reproduce exactly; the 9 on the 55-map frame were not run.

**Answer.** Among the 737 Phase 2 cells, OLD reproduces 695 exactly —
every point, every interval bound at every buffer, the Matthews correlation
coefficient (MCC), sensitivity and specificity blocks with their intervals,
confusion matrices, `coverage_status`, `ci_unreliable`, and the other
flags, per run where a cell has several. Every interval change in those
695 regenerated cells is therefore D50 alone. Nothing like the archived
spot check's failure turned up among live cells.

## The 42 Phase 2 cells OLD does not reproduce: one cause

- **Where**: `results/uplift-supplement/k1-gapfill` (35),
  `results/pairwise/tile-size-30m` (5), and
  `results/uplift-supplement/verifier-pairing` (2).
- **What still matches**: F1, precision, recall, and `n_detections` at every
  buffer.
- **What differs**: the committed F1, precision, and recall intervals at
  every buffer, the confidence interval (CI) methods, the coverage blocks
  and flags, and — in the 37 scored with `--mcc` — the whole tile block.
  OLD withholds all of these (`ci-withheld-tile-join-refusal`), and the NEW
  files in draft PR #29 withhold them identically (checked in all 42).
- **Why**: the committed files were scored at `9c82d3fa0` (5 cells,
  2026-08-20), `1fca9caad` (20, 2026-08-29), `26cc430ad` (15, 2026-09-07),
  and `c1d6424b7` (2, 2026-09-08), before the tile-join invariant
  `7ba47b63b` (2026-09-12), the MCC withholding `fd59a68b0` (2026-09-12),
  and interval withholding instead of aborting `3eeaf96f4` (2026-09-13).
  Their intervals came from the defective name-based join (e.g. a
  verifier-pairing cell's F1@50 interval [0.0296, 0.0913] beside a point of
  0.4463).
- **Main-session check (2026-10-10)**:
  `results/uplift-supplement/verifier-pairing/stride-55map-2026-08-25__g384-ov128-55map-n10-oracle-p0_15-k7-r2-gt/evaluation.json`
  on `main` carries intervals (script commit `c1d6424b7`); on
  `origin/d57-4-rescore` it carries 14 `ci-withheld` markers.
- **Consequence**: draft PR #29 removes these intervals and 37 MCCs from
  committed files for a reason that is not D50. None of the 42 is a
  registered condition or a register-analysis input.
  `results/uplift-supplement/verifier-uplift-mcc.csv` takes its unverified
  MCC 0.0122 and 0.0121 (uplift 0.6836 and 0.6833) from the two
  verifier-pairing cells; Phase 3 found those two go computed → pending,
  and this is why. None of these values is cited in `docs/paper/`.

## The 12 other live cells OLD does not reproduce

- **Tile-join withheld, 2 cells (registered)**:
  `results/k-ladder-2026-09-12/phase2/cells/gemini37-screen-2026-08-28__g37-text-k1-verified-opmax`
  and `…-carried-p0_10-k1` (analyses `k-ladder-2026-09-12` and
  `null-exemplar-sensitivity-2026-09-13`). Scored 2026-09-12 at
  `f724b7a10`, hours before `7ba47b63b`. The frames table already marks
  them `mcc-refused-now`; their F1 reproduces.
- **Input drift, 9 cells (all registered; all feed
  `uplift-supplement-flatten`)**. Each reproduces exactly on its
  E82-pinned inputs, so neither the scorer nor D50 is involved:
  `paper-eval/n1/384px-14buf-mcc` pro-image and pro-text high T0 (pin
  `1f443fd69`); `rescore-2026-05-31/n1-outstanding-384` pro-image and
  pro-text high T0 `run_1`–`run_3` (pin `c3852ebad`); and
  `rescore-2026-05-31/e47-propose-brief/…/run_4` (pin `52b0215a6`).
- **Unresolved, 1 cell (unregistered)**:
  `outputs/55maps-text-min-generalisation/full-buffer-eval`. Points and
  intervals are off by ±0.0001 (F1@20 0.6202 → 0.6201); `n_detections`
  equal. Its pinned reference blob
  (`student-mounds-55maps-reviewed.geojson` at `baf1497a7`) differs from
  today's; the frames table calls it `unexplained`. Replayed at 13:47Z,
  before today's first kernel report; its vintage replay was not run.
- **Paper check**: `git grep` of `docs/paper/` for every affected cell's
  committed interval pairs, MCC points, F1@20/30/50, and condition ids
  finds no citation (one coincidental hit: 0.8709 in R5-05's
  "F1 0.8709–0.8764", which describes a different matrix).

## To resume (after sapphire is cleared)

458 live cells (102 registered) plus 9 vintage replays remain. Delete
`out/STOP` first; the runner skips finished cells and re-runs failed ones:

```bash
nohup ~/Code/map-reader-llm/.venv/bin/python <root>/scripts/run_census.py \
  --queue <root>/out/queue.json --old ~/scratch/d57-4-rescore-2026-10-09/old \
  --inputs-root <root>/inputs --sidecars <root>/sidecars \
  --pidfile <root>/out/resume.pid --workers 8 --stop-file <root>/out/STOP \
  --halt-on-failure --kernel-tripwire > <root>/out/resume.log 2>&1 < /dev/null &
```

Then `compare_census.py` and `analyse_census.py`, with the arguments in
their docstrings.

## Changelog

### 2026-10-10 — Original publication

The census agent's hand-back, with the main session's checks at source:
the kernel-log entries, the bit-34 signature across all logged index
errors, the census summary counts, and one tile-join cell on `main`
against draft PR #29.
