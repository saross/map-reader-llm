# D57 (4) re-score: OLD-scorer census of committed evaluations

> **Last revised**: 2026-10-10 (census completed as the sapphire memory soak).
> See [§ Changelog](#changelog) for revision history.

- **Executed by**: Claude (Anthropic), Claude Code, model lane Opus 5.5
  (`claude-opus-5-5`), a subagent of the main Session 163 session, on
  sapphire, 2026-10-09 12:14–15:23 UTC (22.45 CPU-hours). Completed by
  the main session on 2026-10-10, 06:09–07:06 UTC, as the memory soak
  (§ Completion).
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
  (93 rows), `out/census_summary.json`, `out/compare.{json,csv}`,
  `out/plan.json`, `out/queue.json`, `scripts/` (6 files), and the replays.
  The halted run's outputs are kept in `out/pre-soak-2026-10-10/` (its
  `nonrepro.csv` has 76 rows) and its stop file as
  `out/STOP.halted-2026-10-09`; the soak's log is `out/resume.log`.
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
  fired at 15:22:55Z after 817 clean cells.
- **Resolved, as far as a soak can show (2026-10-10).** Sapphire
  rebooted at 05:09Z with its memory at JEDEC 4,800 MT/s, EXPO off (the
  PI confirmed the speed in the BIOS and with a command-line check). The
  census's remaining 467
  replays then ran as the soak, under the same 8-worker load: 467 of 467
  clean in 3,425 s, no new `Bad page state` report (5 before and after,
  all from earlier boots), and all 22 replays that crashed on
  2026-10-09 now reproduce exactly. DIMMs read 40.8–49.8 °C (alarm
  55 °C) and CPU Tctl at most 68.8 °C, logged each minute
  (`out/soak-temps.log`). On 2026-10-09 the same load crashed 21 of 46
  heavy replays.

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
Those files have since been verified: an independent re-run reproduced
all 2,262 exactly (S2 record changelog), and PR #29 merged on
2026-10-10. Other once-computed results from the fault windows are a
separate re-check (`planning/paper-writeup-continuity.md`).

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
| Reproduced exactly | 695 | 1,428 | 2,123 |
| Not reproduced | 42 | 51 | 93 |
| Replay crashed | 0 | 0 | 0 |
| Not run | 0 | 0 | 0 |

Vintage replays of the drifted cells: 26 of 26 reproduce exactly (17
small-frame, 9 on the 55-map frame).

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

## The 51 other live cells OLD does not reproduce

All three causes are deterministic, and none involves D50. The 39 found
by the completion run (§ Completion) are unregistered and feed no
register analysis; the 11 registered ones are the ones listed here before.

- **Tile-join withheld, 23 cells.** 21 unregistered, found by the
  completion run: `results/uplift-supplement/verifier-pairing` (15) and
  `results/uplift-supplement/k1-gapfill` (6), the same cause as the 42
  Phase 2 cells. Two registered ones, found first:
  `results/k-ladder-2026-09-12/phase2/cells/gemini37-screen-2026-08-28__g37-text-k1-verified-opmax`
  and `…-carried-p0_10-k1` (analyses `k-ladder-2026-09-12` and
  `null-exemplar-sensitivity-2026-09-13`). Scored 2026-09-12 at
  `f724b7a10`, hours before `7ba47b63b`. The frames table already marks
  them `mcc-refused-now`; their F1 reproduces.
- **Input drift, 26 cells; each reproduces exactly on its inputs as
  scored**, so neither the scorer nor D50 is involved. 17 unregistered,
  found by the completion run: `results/paper-eval/mcc/384px` (4),
  `results/paper-eval/n1/384px-all-buffers` (4), and the 55-map
  `outputs/55maps-{image,text-high,text-min}-generalisation` evaluations
  (3 each, counting the cell below). Nine registered ones, all feeding
  `uplift-supplement-flatten`, found first:
  `paper-eval/n1/384px-14buf-mcc` pro-image and pro-text high T0 (pin
  `1f443fd69`); `rescore-2026-05-31/n1-outstanding-384` pro-image and
  pro-text high T0 `run_1`–`run_3` (pin `c3852ebad`); and
  `rescore-2026-05-31/e47-propose-brief/…/run_4` (pin `52b0215a6`).
- **Resolved as input drift**:
  `outputs/55maps-text-min-generalisation/full-buffer-eval`, first listed
  as unresolved (points and intervals off by ±0.0001, F1@20 0.6202 →
  0.6201; its pinned reference blob `student-mounds-55maps-reviewed.geojson`
  at `baf1497a7` differs from today's). Its vintage replay, run in the
  completion, reproduces it exactly.
- **Older interval vintage, 2 cells (unregistered)**:
  `outputs/55maps-text-high-t0.3-generalisation/evaluation` and
  `…/extended-buffer-eval`, scored 2026-04-27 (`291715b4`, `548604d9`).
  Points, MCC point, and `n_detections` reproduce; 28 and 30 interval
  values and 4 and 5 flags do not (e.g. F1@50 interval [0.7911, 0.8128]
  committed, [0.7916, 0.8134] replayed; a `sparse_cross_grid` coverage
  flag added). A second replay of both, by the main session, matched
  the first in every field except the output path and timestamps, with
  byte-equal CSVs (`repeat-b-interval-2026-10-10/`), so the difference
  is deterministic: an interval or coverage change between April and
  `b3c52591d`, like the archived spot check. Not attributed to a commit.
- **Paper check**: `git grep` of `docs/paper/` for every affected cell's
  committed interval pairs, MCC points, F1@20/30/50, and condition ids
  finds no citation (one coincidental hit: 0.8709 in R5-05's
  "F1 0.8709–0.8764", which describes a different matrix). For the 39
  found by the completion run, by the main session: 192 distinct
  committed values give 8 coincidental hits (p values, differences, and
  another corpus's ladder), and two labels match: R2-13's tie set names
  `pro-text-high-t-0-0` and `pro-text-medium-t-0-0` (run
  `n1-baseline-matrix-384`). The files here with those labels are
  unregistered copies, and each reproduces on its inputs as scored.

## Completion (2026-10-10): the memory soak

The 467 remaining replays (458 cells, 22 of them the crashed ones, plus 9
vintage replays) ran on sapphire from 06:09:23 to 07:06:39 UTC as the PI's
confirmation soak, after the reboot. The halted run's stop file was kept as
`out/STOP.halted-2026-10-09`; the command was the one this record gave,
with `--workers 8 --halt-on-failure --kernel-tripwire` (armed at 5 reports).
A logger wrote DIMM (`spd5118`) and CPU (`k10temp` Tctl) temperatures each
minute until the run ended. Then, with the previous outputs copied to
`out/pre-soak-2026-10-10/`:

```bash
python compare_census.py --census-root <root> --repo ~/Code/map-reader-llm \
  --rev 494b5a7af \
  --repro-failures ~/scratch/frames-blast-radius-2026-10-07/out/summary/reproduction_failures.csv
python analyse_census.py --census-root <root> --repo ~/Code/map-reader-llm --rev 494b5a7af
```

Both exited 0. The run: `DONE 467/467 ok in 3425s; failed 0`; no stop
file; kernel count 5 before and after.

## Changelog

### 2026-10-10 — Census completed as the sapphire memory soak

Trigger: the PI's memory change and soak (D59). The 467 replays left by the
halted run ran clean on the rebooted machine; the main session ran the
comparison and analysis, re-ran the two new interval-vintage cells to
show the difference is deterministic, and checked the 39 newly found
non-reproductions against `docs/paper/`.

| Count | Before | After |
|---|---:|---:|
| Reproduced exactly (Phase 2 / other / total) | 695 / 1,009 / 1,704 | 695 / 1,428 / 2,123 |
| Not reproduced | 42 / 12 / 54 | 42 / 51 / 93 |
| Crashed (memory fault) | 22 | 0 |
| Not run | 436 | 0 |
| Vintage replays reproducing | 17 of 17 run | 26 of 26 |

Not changed: the Phase 2 answer (695 of 737; the 42 tile-join cells), the
11 registered non-reproductions and their causes, and the finding that
no affected value is cited in the paper. The one "unresolved" cell is now
explained as input drift.

### 2026-10-10 — Original publication

The census agent's hand-back, with the main session's checks at source:
the kernel-log entries, the bit-34 signature across all logged index
errors, the census summary counts, and one tile-join cell on `main`
against draft PR #29.
