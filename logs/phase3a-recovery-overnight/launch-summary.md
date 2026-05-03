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

(Populated post-launch.)

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

(Appended post-launch.)
