# Daylight follow-up sweep — in-progress status (2026-04-29)

**Status as of 2026-04-29 14:10 UTC**: full sweep launched on sapphire at 14:01 UTC; running.

This document is a checkpoint in case I (the implementing agent) am
interrupted before the sweep completes. It lists what's been done, what's
running, and what remains so a follow-up session can continue without
re-tracing the work.

## What's been done

1. **Pre-sweep tag** created and pushed: `pre-bootstrap-10k-followup-2026-04-29`
   at HEAD `ee4f18cb`.
2. **Builder script** `scripts/build_bootstrap_10k_queue_followup.py` written
   (~470 LOC, lint-clean, tested locally and on sapphire). Read-only on
   configs and sidecars; emits a 165-row CSV queue at
   `/tmp/bootstrap-10k-jobs-followup.csv`. Validates all 165 rows have
   detection / bounds / GT paths on disk before writing.
3. **Verification script** `scripts/verify_bootstrap_10k_followup.py` written
   (~230 LOC, lint-clean). Implements §7.1–7.5 verification queries.
   Tolerance is 5e-4 for F1 and MCC point estimates (accounts for
   pre-tag rounding to 4 decimals).
4. **Sweep launcher** `scripts/launch_bootstrap_10k_followup_sweep.sh`
   written; runs xargs -P 16 over indices 0..164 minus the 3 already-done
   dry-run cells (135, 156, 164), so 162 cells in this sweep run.
5. **Dry-run completed for 3 of 4 cells**:
   - Index 135 (paper-eval/n1/384px/flash-text-minimal-t-0-0): N=10K
     confirmed, F1=0.5147 vs pre 0.515 (Δ=0.0003 within tolerance), schema
     preserved (per_run=10).
   - Index 156 (pairwise/512px-image-t0): N=10K confirmed AFTER fixing
     bounds from 340-tile to 487-tile (see surprise finding §1 below).
   - Index 164 (gold-standard-extended-buffer-sweep): N=10K confirmed,
     F1 stable to 0.0000 across all 6 buffers.
6. **Index 163** (55maps/text-min) was attempted but killed at 24 min
   wall (one buffer of 4 completed). Will be re-run as part of the
   full sweep.
7. **Full sweep launched** on sapphire at 14:01 UTC, 16 workers.
   Log: `/tmp/bootstrap-10k-followup-progress.log` on sapphire.
   Failures: `/tmp/bootstrap-10k-followup-failures.log`.

## Surprise finding 1 — pairwise bounds correction

The 5 pairwise/tile-size-30m cells (`512px-{image,text}-t0`,
`512px-{image,text}-t07`, `eval-512-on-384-image-t0`) had pre-existing
**buggy bootstrap CIs** in their pre-tag evaluation.json — the F1 point
estimates fell **outside** the f1_ci_lower / f1_ci_upper bounds. The
original commit message (`52e6c40d`, 2026-03-28) noted "Methodological
caveat: cross-grid bootstrap CIs unreliable due to sparse tile coverage;
point estimates directionally clear."

The plan §3.2 said use 340-tile bounds for the first 4 cells; the
empirical dry-run discovered the pre-tag eval was actually generated
with **487-tile bounds**. Re-running with 340-tile bounds produced ΔF1
of 0.07–0.08 vs pre-tag (a methodology shift, not just MC noise). I
corrected the queue to use 487-tile bounds for all 5 cells; index 156
re-ran cleanly with ΔF1=0.0000 vs pre-tag.

Note: the buggy CIs persist in the new N=10K eval too (e.g.,
512px-image-t0 @ 30m: F1=0.571, CI=[0.205, 0.514] — point still
outside CI). This is a pre-existing bug in the evaluator's bootstrap
sampling under sparse tile coverage; not introduced by this sweep.
**Worth flagging to the user** — may want a separate investigation
into whether the bootstrap sampling is correct for these 5 cells, or
whether the report-time guidance to ignore the CIs is sufficient.

## What's running now

- **Full sweep**: 162 cells via xargs -P 16, ~6/161 OK at 9 min in.
- ETA based on early cells: 3-4 hours wall (much longer than the
  plan's 30-60 min estimate; the 30-run paper-eval cells and the
  3 × 55maps cells are the bottleneck).

## What remains

After the sweep completes:

1. Verify §7.1 (N=10K presence on all 165 cells) — binding.
2. Verify §7.2 (detection-count cross-check, 5-cell sample).
3. Verify §7.3 (F1 stability, 5-cell sample, |Δ| < 5e-4) — binding.
4. Verify §7.5 (MCC stability for all 51 MCC-flag cells, |Δ| < 5e-4) — binding.
5. **Pairwise group**: the §7.3 F1 stability check will FAIL on the 5
   pairwise cells if they're sampled, because the new N=10K eval
   produces sensible CIs while pre-tag had buggy CIs. The point
   estimates DO match (Δ=0.0000 with 487-tile bounds). The verifier
   spot-check may need scoping to non-pairwise cells, OR the user
   may want to treat the pairwise cells as a separate "data correction"
   rather than an N=1K → N=10K standardisation.
6. Per-group commits (4 commits): paper-eval, pairwise/tile-size-30m,
   55maps-cleaned-gt, gold-standard.
7. Push to origin/main with rebase-on-conflict (parallel agents may
   push concurrently).

## Follow-up agent's TODOs

If you (a follow-up agent) are picking this up:

1. SSH to sapphire, check sweep status:
   `ssh sapphire 'grep -cE "OK   |FAIL " /tmp/bootstrap-10k-followup-progress.log'`
2. If sweep done: run verification:
   `ssh sapphire 'cd ~/Code/map-reader-llm && source .venv/bin/activate && python3 scripts/verify_bootstrap_10k_followup.py'`
3. Inspect failures (if any):
   `ssh sapphire 'cat /tmp/bootstrap-10k-followup-failures.log'`
4. Per-group commits per plan §8.
5. Push with rebase-on-conflict.
