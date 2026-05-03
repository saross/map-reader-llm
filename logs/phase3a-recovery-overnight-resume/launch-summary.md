# Phase 3a Verifier Recovery — Overnight Resume Launch Summary

Operator-of-record: Claude Code (Opus 4.7, 1M context) on amd-tower,
orchestrating sapphire via SSH per project compute-location policy.
This is the **resume launch** following the partial completion of the
2026-05-03T14:58:15Z initial overnight run (which halted at cell 7 of 20
due to missing crop PNGs in the e47 cell).

## Resume launch metadata

- **Resume initiated (UTC):** 2026-05-03T15:19:30Z
- **Sapphire HEAD at resume:** `cebe5fed65018bdb20c74b869bf5d2c7df1d9a1d`
  (`chore(gitignore): exclude phase3a-recovery-overnight-resume driver logs`)
- **Driver invoked:** `bash planning/run-phase3a-recovery.sh all`
  (under nohup with `source .venv/bin/activate` in a wrapping subshell —
  required because the driver calls bare `python` rather than `python3`).
- **Mode:** unattended overnight (`NON_INTERACTIVE=1`)
- **Cost approval (operator):** unchanged at **$10 hard cap**.
- **PID file:** `logs/phase3a-recovery-overnight-resume/pid.txt`
- **Process PID at launch:** **259394**
- **stdout log:** `logs/phase3a-recovery-overnight-resume/stdout.log`
- **stderr log:** `logs/phase3a-recovery-overnight-resume/stderr.log`
- **Per-cell timestamped log dir:** `logs/phase3a-recovery-20260503T151930Z/`

## Step 1 commits (six Tier-1 successes + propagation)

The six Session-78 cells cleaned by the previous overnight run were
committed in two logical groups, per runbook section 9:

| Commit | Subject |
|---|---|
| `414ee8a4b` | `data(p3a-recovery): cleanup Session-78 matrix verifier outputs (6 cells, 153 cands)` |
| `b3ed509e6` | `analysis(p3a-recovery): propagate Session-78 cleanup through materialise + calibration` |

The propagation commit covers the materialise step (six Session-78
GeoJSONs + registry under `results/leaderboard/era2/pv-materialised/`)
and the calibration matrix step (six `calibration.json` refreshes plus
`planning/session-78-matrix-calibration-summary.md`).

**Pre/post AUC deltas** (image and text canonical adversarial-text;
all six cells):

| cell | n_total | AUC pre -> post |
|---|---|---|
| image-adversarial-text  | 1991 -> 2017 | 0.8574 -> 0.8578 (+0.0004) |
| image-brief-text        | 1998 -> 2017 | 0.8366 -> 0.8376 (+0.0010) |
| image-checklist-text    | 1998 -> 2017 | 0.8531 -> 0.8524 (-0.0006) |
| text-adversarial-text   | 3695 -> 3736 | 0.9561 -> 0.9560 (-0.0001) |
| text-brief-text         | 3709 -> 3736 | 0.9374 -> 0.9381 (+0.0007) |
| text-checklist-text     | 3715 -> 3736 | 0.9502 -> 0.9500 (-0.0002) |

All movements within the runbook's expected magnitude (<0.005 absolute);
no surprises requiring intervention.

**Deferred to morning operator** (heavier CPU; runbook section 6.1
steps 3-6 — these are 2-3 hours wall-clock on sapphire and benefit from
operator review of the rebuilt leaderboard tier output):

```bash
bash scripts/run_per_arch_leaderboards.sh        # ~2-3h
bash scripts/finalise_per_arch_leaderboard.sh
bash scripts/build_combined_leaderboard.sh 2
bash scripts/build_combined_tier_stability.sh
```

The decision to defer was made because the campaign relaunch is the
priority (overnight wall-clock budget) and the per-arch / combined
rebuild produces no API spend — it can run on the morning.

## Step 2 commits (driver edit)

| Commit | Subject |
|---|---|
| `e174390e4` | `fix(phase3a-recovery): skip 3 crop-missing cells; resume from cell 8` |
| `cebe5fed6` | `chore(gitignore): exclude phase3a-recovery-overnight-resume driver logs` |

The driver edit adds a `SKIP_CELLS` array, a `SKIP_REASON` map, and an
`is_cell_skipped()` helper. The `recover_cell()` entry point
short-circuits with a `SKIP:reason` ledger row before invoking
`compute_gap` or `run_pv.py cleanup`. The 6 already-cleaned Session-78
cells are NOT in `SKIP_CELLS` — they hit the existing `gap_before == 0`
fast-path inside `recover_cell()` (line 140 of the original driver).

The gitignore commit was needed because the resume directory's transient
log files were being picked up by the driver's pre-flight
`git status --porcelain` check, which initially aborted the relaunch.

## Three skipped cells

| Cell | Tier | Gap | Reason |
|---|---|---|---|
| `e47-flash-high-text-1of5` | 1 | 57 | `missing_crops_gitignored` |
| `55maps-gen-verified-v2` | 2 | 3 | `missing_crops_gitignored` |
| `proposer-verifier-384-adversarial-text-v1-prompt` | 3 | 1 | `missing_crops_gitignored` |

All three cells lack the crop PNG files that `run_pv.py cleanup`
requires. The crop directories are gitignored bulk intermediates that
were never committed to the repository. Verified absent on sapphire on
2026-05-03 (e47 has zero PNGs in `crops/`; 55maps and proposer-verifier-384
have only `candidate_manifest.json`, no PNGs).

## Surprise — e47 cleanup damaged the on-disk file

The previous overnight run's failed cleanup of `e47-flash-high-text-1of5`
**rewrote the cell's `probabilities.json` from the derived schema
(`source` / `derived_from` / `vote_threshold`) to the canonical schema
(`version` / `mode` / `verifier_config` / ...) with a `cleanup_history`
showing 0 recovered / 57 still_missing**. Every candidate failed because
the crops were absent.

Per runbook section 0.1, the e47 cell is documented as the canonical
SOURCE for the four `2of5..5of5` derivatives. But the file in HEAD prior
to the failed cleanup was already in DERIVED schema (with self-reference
in `source` and `derived_from: "1-of-5 union"`). This suggests the
canonical source was overwritten earlier (possibly by an inadvertent
`derive_vote_threshold_results.py` run on the source itself, which is
structurally identical at vt=1).

**Action taken in Step 1**: restored the on-disk file from the
`probabilities.json.pre-cleanup-20260503T145925.backup` sibling and
restored `run.meta.json` from HEAD via `git checkout`. This means the
e47 cell remains in its (already-degraded) pre-recovery state. **Do NOT
commit the file as the previous-agent left it; it would corrupt the
file's schema downstream.**

This is a deeper data-integrity finding than just "missing crops" — see
the morning-user resumption decision section below.

## Estimated wall-clock to overnight completion

Based on the previous run's timing (cells 1-7 of Tier 1: 9-17s each;
Tier 1 cell 8 (h8v2): 9s; the dominant Tier 2 cell 9 with gap=460 will
take roughly 50-90s at the observed rate of ~10 calls/s):

- Tier 1 cell 8 (h8v2): **already complete** (9s, $0.022, recovered=15).
- Tier 2 cell 9 (image-n5-t0.0, gap=460): in flight at launch+30s,
  estimate ~60-90s remaining.
- Tier 2 remaining (cells 10, 12, 13, 14, 15 — 4 cells with gap=1-11
  each; cell 11 = `55maps-gen-verified-v2` is SKIPPED): ~30-60s total.
- Tier 3 cells 16-19 (3 pro-medium + 1 flash-medium-vf, gap totals ~40):
  pro-medium cleanup is ~5x slower per call, so estimate ~2-3 min total.
- Tier 3 cell 20 (`proposer-verifier-384-...-v1-prompt`): **SKIPPED**.

**Total estimated wall-clock to completion: ~10-15 minutes from launch
(by ~15:35 UTC on 2026-05-03).** Hard cap: $10 USD across all tiers.

## Morning-user resumption decision

The morning user has three orthogonal options:

### Option A — accept the 16-of-19 outcome and move on

Skipped-cell impact:

- `e47-flash-high-text-1of5` (gap=57 of 4358): the cell is also
  derivative-corrupted (see "Surprise" above) — pursuing recovery
  requires both crop regeneration AND schema repair.
- `55maps-gen-verified-v2` (gap=3 of N): contamination-policy
  investigation cell, not paper-citation-load-bearing per runbook
  section 0.3.
- `proposer-verifier-384-...-v1-prompt` (gap=1): legacy diagnostic, no
  current consumer per audit.

If the user accepts these gaps as residual ledger items, the campaign
is complete after the overnight run finishes.

### Option B — recover the 3 skipped cells

Total additional wall-clock if pursued (mostly CPU-only):

- **~30 min** crop regeneration via `scripts/extract_candidates.py`
  (or `python scripts/run_pv.py extract` if that subcommand exists) —
  CPU-only, no API spend. Run on sapphire.
- **~10 min** re-cleanup of the 3 cells (API calls, but only ~61
  candidates total; cost <$0.10).
- **~30 min** per-cell propagation per runbook section 6.

Caveat for `e47-flash-high-text-1of5`: the derived-schema state of the
on-disk file means cleanup would write canonical schema, breaking any
downstream code that expects the derived schema (and breaking the
`derive_vote_threshold_results.py` regeneration of 2of5..5of5
derivatives from this source). Schema repair is required first; the
cleanest path is probably:

1. Recover the original canonical-schema source from a session archive
   or earlier git history (last canonical state is unclear; commit
   `52b0215a` may not have it).
2. Regenerate crops.
3. Run cleanup.
4. Run `derive_vote_threshold_results.py` to refresh 2of5..5of5.

### Option C — defer the per-arch + combined leaderboard rebuild

Independent of the 3 skipped cells, the runbook section 6.1 step 3-6
chain (per-arch + combined rebuild) is deferred from this overnight run:

```bash
bash scripts/run_per_arch_leaderboards.sh        # ~2-3h
bash scripts/finalise_per_arch_leaderboard.sh
bash scripts/build_combined_leaderboard.sh 2
bash scripts/build_combined_tier_stability.sh
```

Run this if the morning user wants the leaderboard tier outputs
refreshed against the cleaned Session-78 matrix.

## Files NOT to commit

- `outputs/.../probabilities.json.pre-cleanup-*.backup` — gitignored.
- `outputs/h11/e47-propose-brief/verified/flash-high-text-1of5/` —
  the on-disk state was restored from backup; no commit pending here.
- `logs/phase3a-recovery-20260503T151930Z/` — runtime artefacts,
  gitignored via `logs/phase3a-recovery-2[0-9]*/`.
- `logs/phase3a-recovery-overnight-resume/{stdout,stderr,pid}.log` —
  gitignored via the resume-launch chore commit.
