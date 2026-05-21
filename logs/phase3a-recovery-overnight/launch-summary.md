# Phase 3a Verifier Recovery — Overnight Launch Summary

Operator-of-record: Claude Code (Opus 4.7, 1M context) on amd-tower,
orchestrating sapphire via SSH per project compute-location policy.

## Launch metadata

- **Launch initiated (UTC):** 2026-05-03 (see `nohup.out` / `stdout.log`
  timestamp for exact start)
- **Sapphire HEAD at launch:** `1d9be35c39ad6aa6bdad432ec6782a0c318ccc31`
  (`docs(continuity): flag overnight recovery launch + zbook morning reminders`)
- **amd-tower HEAD:** matches sapphire (verified `git status` clean +
  `git pull --ff-only` returned "Already up to date").
- **Driver invoked:** `bash planning/run-phase3a-recovery.sh all`
- **Mode:** unattended overnight (NON_INTERACTIVE=1)
- **Cost approval (operator):** up to **$10 hard cap** (driver enforces;
  do not raise without operator input).
- **Approval scope:** all three tiers in advance; tier-boundary operator-go
  prompts bypassed via env var (see § "Driver edits" below).

## Sentinel file

Path: `.phase3a-recovery-fix-landed` (gitignored / local-only; not committed).

Contents:

```text
Fix arc complete at commit ee658e72; tier-1 980 passing; campaign approved 2026-05-03 night.
```

## Driver edits

The runbook's authoritative driver template at
`planning/run-phase3a-recovery.sh.template` was copied to the working
`planning/run-phase3a-recovery.sh` and modified to support unattended
launch. The `.template` was preserved unmodified.

**Edit chosen:** environment-variable bypass via `NON_INTERACTIVE=1`. This
was preferred over piping `yes y` to stdin because the driver's `read -r`
calls are entangled with messaging (the same blocks print "Press Enter…"
prompts that should be suppressed when running unattended) and because the
env-var path makes the bypass auditable from inside the log.

**Changes (3 prompt sites, 1 declaration):**

1. **Declaration block** (after `TIER=` parsing): added
   `NON_INTERACTIVE="${NON_INTERACTIVE:-0}"` with documentation comment
   listing what the bypass covers and what abort-on-error safeties remain
   in force.
2. **`tier_boundary_confirm()` function:** when `NON_INTERACTIVE=1`, prints
   "auto-continuing to <next_tier>" and skips the `read -r`.
3. **Cost-confirm-threshold soft prompt** (cumulative cost > $5): when
   `NON_INTERACTIVE=1`, prints "auto-continuing (hard cap still enforced)"
   and skips the `read -r`. The $10 hard cap (`exit 3`) is unaffected.
4. **Intra-Tier-2 image-t0.0 cost-validation pause:** when
   `NON_INTERACTIVE=1`, prints "auto-continuing Tier 2 (hard cap still
   enforced)" and skips the `read -r`.

**What was NOT bypassed (abort-on-error safeties preserved):**

- Sentinel-check exit (`exit 2` if `.phase3a-recovery-fix-landed` missing).
- Working-tree-clean exit (`exit 2` if `git status --porcelain` non-empty).
- `$10` hard cost cap (`exit 3` if `CUMULATIVE_COST > 10.00`).
- Per-cell `cleanup` failure handling (`return 1`, ledger logs FAILED).
- Residual `gap_after > 0` warning (continues to next cell, logs failure
  for follow-up).
- `set -euo pipefail` (any unhandled error halts the script).

Bash syntax-checked clean (`bash -n` passes).

## Tier ordering as inspected

The driver runs tiers strictly in order: Tier 1 → Tier 2 → Tier 3.
Within tiers, cells are ordered as documented in the runbook § 3:

**Tier 1 (8 cells, expected ~$0.43):**

1. session78-text-adversarial-text (gap 41)
2. session78-text-brief-text (gap 27)
3. session78-image-adversarial-text (gap 26)
4. session78-text-checklist-text (gap 21)
5. session78-image-checklist-text (gap 19)
6. session78-image-brief-text (gap 19)
7. e47-flash-high-text-1of5 (gap 57)
8. h8v2-wbf-scale-4 (gap 15)

**Tier 2 (7 cells, cells 9–15 in campaign sequence, expected ~$1.00):**

1. image-n5-t0.0-v1-n10 (gap 460) — cost-validation cell, intra-tier
   checkpoint after this cell
2. image-n5-t0.3-v1-n5 (gap 11)
3. 55maps-gen-verified-v2 (gap 3)
4. image-n5-t1.0-v1-n5 (gap 1)
5. image-n5-t0.7-v1-n5 (gap 1)
6. session78-image-checklist (gap 1)
7. scale-4-optimal-487-v1-n10 (gap 1)

**Tier 3 (5 cells, cells 16–20 in campaign sequence, expected ~$0.42;
3 use Pro thinking=medium):**

1. text-baseline-pro-verifier (gap 21, **pro-medium**)
2. pro-medium-image-baseline-pro-verifier (gap 10, **pro-medium**)
3. pro-high-image-1of5-pro-verifier (gap 8, **pro-medium**)
4. flash-high-text-1of5-flash-medium-verifier (gap 1, flash-medium)
5. proposer-verifier-384-adversarial-text-v1-prompt (gap 1, flash)

**Total expected cost:** ~$1.84 (1.5× empirical baseline);
worst-case $3.70 (3× retry headroom); hard cap $10.

**Total candidates to recover:** 776.

**Note on derived cells:** the 11 derived cells in the audit (e47 2of5–5of5,
pro-vf 1of5–5of5, flash-medium-vf 1of5) regenerate for free from the cleaned
sources via `scripts/derive_vote_threshold_results.py`. The driver does NOT
auto-trigger this regeneration; it is documented as an OPERATOR (manual)
step in the driver and runbook § 6. Morning session will run the derivative
regeneration + per-tier propagation chains.

## PID and log paths

(Populated post-launch; see § "Launch verification" appended below for the
ps output and log tail.)

- **Process PID file:** `logs/phase3a-recovery-overnight/pid.txt`
- **stdout:** `logs/phase3a-recovery-overnight/stdout.log`
- **stderr:** `logs/phase3a-recovery-overnight/stderr.log`
- **Per-cell logs (driver-managed):** `logs/phase3a-recovery-<UTC-timestamp>/`
  (the driver creates its own timestamped subdirectory under `logs/` for the
  cost ledger and per-cell logs; see `logs/phase3a-recovery-overnight/stdout.log`
  for that path once the driver prints it).

## Expected completion window

Per-cell wall clock: empirically ~10–60 s for small cells (gap 1–41), and
~5–10 min for the gap=460 image-t0.0 cell (Tier 2 dominant). Pro-medium
cells (Tier 3) likely 1–3 min for ~10–20 candidates each due to slower
per-call latency.

Total wall-clock estimate: **~4–7 hours** unattended. Will not finish
before morning Sydney time.

## Resumption instructions

If the campaign halts partway (cost cap, repeated failure, or unhandled
error):

1. Check `logs/phase3a-recovery-overnight/stderr.log` for the abort cause.
2. Inspect the timestamped per-cell log subdirectory (path printed at
   driver start) for `cost-ledger.csv` — this records every cell's
   gap_before / gap_after / cost / wall.
3. Identify the last successful cell from the ledger.
4. Decide whether the abort cause is recoverable (e.g. transient API error
   → resume from next cell) or needs investigation (e.g. cost overshoot
   → re-estimate).
5. To resume from a specific tier, invoke
   `NON_INTERACTIVE=1 bash planning/run-phase3a-recovery.sh tier2`
   (or `tier3`). Cells already at gap=0 are skipped automatically by the
   driver (see `recover_cell()` early-return).
6. The `.pre-cleanup-*.backup` files alongside each cell's
   `probabilities.json` preserve the pre-recovery state for soft rollback
   per runbook § 10.

## Stopping conditions surfaced (if any)

**CAMPAIGN HALTED on cell 7 of 20 (e47-flash-high-text-1of5) — 2026-05-03 14:59 UTC.**

The campaign began correctly under `NON_INTERACTIVE=1`, completed all 6
Tier-1 Group-1A Session-78 matrix cells successfully (153 candidates
recovered, ~$0.20 total cost), then failed when attempting to clean
`outputs/h11/e47-propose-brief/verified/flash-high-text-1of5` (57 missing
candidates, the largest Tier-1 cell). All 57 cleanup attempts failed
across 3 attempts because the candidate crop PNG files do not exist on
disk.

### Root cause

The e47 cleanup needs to read crop PNGs from
`outputs/h11/e47-propose-brief/verified/flash-high-text-1of5/crops/candidate_*.png`
(per the driver's `--crops-dir` argument), but that directory does not
exist. The sibling location
`outputs/h11/e47-propose-brief/crops/flash-high-text-1of5/` exists but
contains only `candidate_manifest.json`; **0 PNG files are present**. The
crops have never been committed to git (gitignored as bulk
intermediates), are missing on both sapphire and amd-tower, and would
need to be regenerated from upstream proposer detections before this
cell's cleanup can run.

The driver halted via `set -e` + `return 1` on cleanup failure, which
matches its safety contract — silent-skipping a 57-candidate paper-cited
cell would be the wrong default. Per stop condition § 8.1 in the runbook
("halts the affected cell's recovery and continues with the next cell"),
the driver as written goes further (halts the entire campaign on
non-zero cleanup return); this divergence between runbook prose and
driver behaviour is itself worth surfacing.

### Pre-flight discovery: missing-crops issue affects 3 of 13 remaining cells

A post-halt audit checked crop availability for all remaining cells:

| Cell | Tier | Manifest n | PNGs on disk | Status |
|---|---|---|---|---|
| e47 flash-high-text-1of5 | 1 | 4358 | 0 | **BLOCKED — campaign halted here** |
| h8-v2 wbf scale-4 | 1 | 1114 | 1114 | OK |
| 55maps-gen verified-v2 | 2 | 8942 | 0 | **WOULD FAIL similarly** |
| image-t0.0 / image-t0.3 / image-t0.7 / image-t1.0 | 2 | 802–2840 | full | OK |
| scale-4-optimal-487 | 2 | 3601 | 3601 | OK |
| tier3 text-baseline / pro-medium / pro-high-1of5 / flash-medium | 3 | 519–3736 | full | OK |
| tier3 proposer-verifier v1-prompt | 3 | 572 | 0 | **WOULD FAIL similarly** |

So 10 of the 13 remaining cells could be cleaned today; 3 need crop
regeneration before they can run.

### Resumption decision points (for the morning operator)

1. **Commit the 6 Session-78 successes?** They modified
   `probabilities.json` files on sapphire (gap 153 → 0). The
   pre-cleanup `.backup` siblings are intact for soft-rollback if the
   user prefers to redo this once a fix is in place. Recommend
   committing — these recoveries are clean, the cost is paid, and the
   `cleanup_history` audit trail inside each `probabilities.json`
   records what changed.
2. **Regenerate e47 / 55maps-gen / proposer-verifier-384 crops?** This
   is a CPU-only step (re-tile from raw proposer detection geojsons),
   no API spend. Once crops are present, re-running the campaign with
   `NON_INTERACTIVE=1 bash planning/run-phase3a-recovery.sh all` will
   skip already-clean cells and clean only the still-gappy ones.
3. **Skip those 3 cells and clean the other 10 first?** Edit the driver
   to insert a per-cell guard that checks for crop PNGs before invoking
   cleanup, falling back to `continue` (per runbook § 8.1). This
   recovers the bulk of the gap (~720 candidates) and defers only the
   3 cells that need crop regeneration.
4. **Investigate the gap=460 image-t0.0 cell first** (Tier 2 cell 9):
   if that cell behaves as expected (~$0.65 cost, gap 460 → 0), that
   confirms the cleanup path scales to the largest gap before deciding
   how to handle the 3 missing-crops cells.

### What was successfully completed

| # | Cell | gap_before | recovered | cost (USD) | wall (s) |
|---|---|---|---|---|---|
| 1 | session78-text-adversarial-text | 41 | 41 | 0.0560 | 17 |
| 2 | session78-text-brief-text | 27 | 27 | 0.0269 | 9 |
| 3 | session78-image-adversarial-text | 26 | 26 | 0.0364 | 11 |
| 4 | session78-text-checklist-text | 21 | 21 | 0.0300 | 14 |
| 5 | session78-image-checklist-text | 19 | 19 | 0.0271 | 7 |
| 6 | session78-image-brief-text | 19 | 19 | 0.0188 | 10 |
| **Subtotal** | | **153** | **153** | **0.1951** | 68 |

Per-cell logs at `logs/phase3a-recovery-20260503T145815Z/`.
Cost ledger: `logs/phase3a-recovery-20260503T145815Z/cost-ledger.csv`
(also visible from amd-tower once the .gitignore allows or via SSH).

### Per-cell artefacts on sapphire (uncommitted)

The 6 successful cleanups wrote new `probabilities.json` files into:

- `outputs/h11/pv-diag-384/flash-high-text-n5/text-t0.7/session-78-matrix/verified-{adversarial,brief,checklist}-text/`
- `outputs/h11/pv-diag-384/flash-high-image-n5/image-t0.7/session-78-matrix/verified-{adversarial,brief,checklist}-text/`

Each cell now has:

- `probabilities.json` (cleaned, with `cleanup_history` audit entry)
- `probabilities.json.pre-cleanup-20260503T*.backup` (gitignored;
  preserves pre-cleanup state for rollback)
- `run.meta.json` (overwritten with cleanup-pass cost; the cost-manifest
  aggregator merges with the `.backup` sibling per fix `7f05f529`)

### What was NOT pushed and why

Per the user's pre-flight instruction in this session
(*"If you stop, document why in the launch-summary file and DO NOT push
(so the user can decide)"*), no commits beyond the launch-prep commits
have been made:

- `81ab99be` (driver + launch summary)
- `9c58721e` (gitignore for sentinel + driver logs)

The 6 successful Session-78 cleanups are present on sapphire as
**uncommitted working-tree changes**. The morning operator decides
whether to commit them as-is, roll them back via the `.backup`
siblings, or extend the campaign and commit a single Tier-1 group.

## Post-launch actions for morning session

Per runbook § 6 (propagation) and § 7 (documentation):

- For each Tier-1 cell with gap_before > 0: re-evaluate, rebuild
  leaderboard, run paired-permutation as applicable.
- Regenerate 11 derived cells via `derive_vote_threshold_results.py`.
- Refresh paper-citation Markdown only if F1 movement > 0.001.
- Append closure observation to `docs/notes/reflections/working-notes.md`.
- Update `planning/paper-writeup-continuity.md` with a "Session 85 closure"
  arc.
- Annotate `reports/phase3a-verifier-completeness-audit-2026-05-03.md` with
  the post-recovery status.

## Launch verification

**Launch attempt 1 — 14:57 UTC:** failed sentinel-check style (working tree
not clean — sentinel and driver-emitted log dirs were untracked, blocking
`git status --porcelain`). Resolved by adding `.phase3a-recovery-fix-landed`
and `logs/phase3a-recovery-2[0-9]*/` to `.gitignore` (commit `9c58721e`).

**Launch attempt 2 — 14:58 UTC:** PID 246632, started successfully under
`NON_INTERACTIVE=1`. Driver progressed through 6 Tier-1 Session-78 cells
(all gap=0 post-cleanup, costs in line with the empirical $0.00140 per-call
baseline) before halting on cell 7 (e47 flash-high-text-1of5) due to
missing crop PNGs (see § "Stopping conditions surfaced" above). Process
exited cleanly per `set -e` + driver `return 1`. No zombies; no API quota
issues; no cost-cap concerns ($0.20 spent against $10 cap).

### Cost-cap status

Cumulative actual cost at halt: **$0.1951** (well within the $10 hard cap;
no $5 confirm-threshold tripped). The cost-cap guards never fired — the
driver halted on cleanup-failure, not budget.

### Sentinel confirmation

```text
$ ls -la .phase3a-recovery-fix-landed
-rw-rw-r-- 1 shawn shawn 93 May  3 14:53 .phase3a-recovery-fix-landed
$ cat .phase3a-recovery-fix-landed
Fix arc complete at commit ee658e72; tier-1 980 passing; campaign approved 2026-05-03 night.
```

Sentinel exists on sapphire and is gitignored (so it does not surface as
untracked when the driver checks the working tree).
