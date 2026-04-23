# SUPERSEDED 2026-04-24

**Reason**: Stage-0 verification complete (this is the intermediate report).

**See**: `planning/nas-migration-plan.md` (active plan continues in later stages)

This document is preserved for audit / historical reference. Its original content follows below.

---

## NAS Migration — Stage 0 Completion Report

**Run**: 2026-04-20T13:35+10:00 (AEST)
**Agent**: Stage 0 background verification (read-only)
**Scope**: Steps 0.1, 0.2, 0.3, 0.6, 0.7, 0.8, 0.9 (0.4 and 0.5 pre-resolved)

## Exit criterion status

- [x] 0.1 rpi-server workspace unlocked, QNAP/Vantec mounted, ~300 GB free
- [ ] 0.2 SSH key auth from all 3 hosts to rpi-server — **BLOCKER on sapphire**
- [x] 0.3 Baseline size snapshots captured for all 3 hosts
- [ ] 0.6 Sapphire confirmed most-complete h11 — **NO: sapphire is NOT a superset**
- [~] 0.7 Phase3a/c supersession claimed on amd-tower; retest replacements on zbook are ~100× smaller than legacy — needs reinterpretation, see below
- [x] 0.8 No unexpected large data (one flag: zbook `archive/cc-sessions` 295 MB)
- [x] 0.9 Git state — all three hosts on same HEAD `bb917010`; dirty state documented

## Findings per step

### 0.1 rpi-server storage and mounts

All expected mounts present and healthy.

- `/opt/encrypted/workspace` 393 G, 73 G used, **300 G free** (20 % used) — matches plan.
- `/mnt/qnap` 26 TB, 15 TB free (39 % used).
- `/mnt/vantec` 15 TB, 4.5 TB free (68 % used).
- All three on `ext4`, device-mapper (LUKS) confirmed.
- `ls /opt/encrypted/workspace/` shows exactly `lost+found shares syncthing` —
  no stale project data. Clean target.

### 0.2 SSH auth from all three hosts to rpi-server

Mixed result — sapphire blocked.

| Host | BatchMode result |
|---|---|
| amd-tower (direct) | **OK** — `hostname` / `date` returned |
| zbook (nested SSH) | **OK** — `hostname` / `date` returned |
| sapphire (nested SSH) | **FAIL** — `Received disconnect … Too many authentication failures` |

**Root cause on sapphire**: sapphire has no local SSH keys in `~/.ssh/`
(`authorized_keys`, `config`, `known_hosts` only — no `id_*`). All SSH auth
from sapphire uses the forwarded agent from amd-tower, which holds 8 keys.
`MaxAuthTries` (default 6) is exhausted before the correct `rpi-server` key
(position 4 in the agent) is reached when combined with the key-tries the
client schedules. Verified by dumping `ssh-add -l` on sapphire.

**Consequential secondary issue**: the failed auth attempts triggered
rpi-server's `fail2ban` (sshd jail, `maxretry=3`, `bantime=3600`). Sapphire's
IP is now rejected with `Connection refused` for up to one hour. `sudo
fail2ban-client` on rpi-server requires a password I cannot supply
non-interactively, so the ban cannot be cleared from this agent.

**Remediation (for user — not attempted)**:

1. Wait ~1 hour for fail2ban to expire the ban.
2. On sapphire, either:
   - `ssh-copy-id -i <key> -p 2222 rpi-server` after first generating a local
     key (`ssh-keygen -t ed25519`), OR
   - Copy the existing `rpi-server` private key from amd-tower to sapphire
     (user's choice), then add `~/.ssh/config` entry:

     ```text
     Host rpi-server
         HostName 192.168.1.100
         Port 2222
         User shawn
         IdentityFile ~/.ssh/id_ed25519_rpi
         IdentitiesOnly yes
     ```

3. Verify with `ssh sapphire 'ssh -p 2222 -o BatchMode=yes rpi-server hostname'`.

Until resolved, Stage 1.3 / 2.x rsync commands issued from sapphire (notably
the authoritative `outputs/h11/` push) will not work.

### 0.3 Baseline size snapshots

Captured to:

- `/home/shawn/Code/map-reader-llm/planning/nas-migration-baseline-amd-tower-ubuntu-20260420.txt`
- `/home/shawn/Code/map-reader-llm/planning/nas-migration-baseline-sapphire-20260420.txt`
- `/home/shawn/Code/map-reader-llm/planning/nas-migration-baseline-zbook-ubuntu-20260420.txt`

Summary:

| Host | inputs | outputs | archive | results | logs | disk free |
|---|---|---|---|---|---|---|
| amd-tower | 3.2 G | 6.9 G | 3.4 G | 185 M | 52 K | 161 G / 469 G (64 % used) |
| sapphire | 5.2 G | 12 G | 2.0 G | 125 M | 180 K | 470 G / 787 G (38 % used) |
| zbook | 22 G | 53 G | 2.3 G | 105 M | 40 K | **59 G / 944 G (94 % used)** |

### 0.6 Sapphire h11 superset check — **NOT a superset**

Directory and file counts:

| Host | h11 subdirs (maxdepth 3) | h11 files (total) |
|---|---|---|
| amd-tower | 388 | 57 641 |
| sapphire | 384 | **133 156** |
| zbook | 427 | 16 170 |

Top-level `outputs/h11/` directory list reveals divergence immediately:

- **sapphire** and **amd-tower** share identical top-level set (12 dirs).
- **zbook** has four additional top-level dirs that sapphire/amd-tower lack:
  - `consensus-384/` — **2.3 GB, 30 run dirs** (`run_1` … `run_30`)
  - `single-pass-384/` — **775 MB, 10 run dirs**
  - `test/` — empty (4 KB)
  - `v2-proposer-test-BAD-TILESIZE/` — 31 MB (self-annotated as bad data)

59 directories exist on zbook but not sapphire (mix of the above plus
regeneratable `crops/` subdirs and `e47-propose-brief/verified-v2-cleanup/…`).
4 directories exist on amd-tower but not sapphire, all trivial
(`pv-diag-256/text-baseline/*` and `pv-diag-256/text-n5/*`, 12–28 KB total).

Sapphire's much higher **file count** (133k vs 57k on amd-tower) is consistent
with it being the generation machine for most h11 artefacts (many small JSON
per-tile files). The count is not inconsistent with the directory picture —
sapphire has more artefact depth in the shared dirs; zbook has extra top-level
experimental dirs that never made it back.

**Implication for Stage 2 (D3)**: the plan's merge strategy (sapphire as
authoritative base, then `--ignore-existing` from amd-tower and zbook) is
still the right shape, but the volume being merged from zbook is **~3 GB of
genuine experimental runs**, not a trivial top-up. Specifically:

- `outputs/h11/consensus-384/` (30 runs, 2.3 GB) — needs provenance check:
  is this superseded by `consensus-384-UNINTENDED-T1.0` (present everywhere),
  or is it a distinct earlier/intentional run?
- `outputs/h11/single-pass-384/` (10 runs, 775 MB) — same question vs
  `single-pass-384-UNINTENDED-T1.0`.
- `outputs/h11/v2-proposer-test-BAD-TILESIZE/` — zbook self-marked as bad;
  decide whether to archive or discard before Stage 2.

Recommend a short pre-Stage-2 decision pass on these four zbook-only top-level
dirs before running the merge.

### 0.7 Phase3a/c supersession check

Legacy and retest sizes on zbook:

| Path | Legacy (zbook `outputs/`) | Retest (zbook `outputs/retest/`) |
|---|---|---|
| phase3a | 20 G | 199 M |
| phase3c | 21 G | 242 M |
| phase3a-replication | 2.2 G | 84 M |
| phase3a-high | — | 140 M |

The retest replacements are present on zbook (created 2026-04-18), but are
**~100× smaller** than the legacy originals. On amd-tower, the ARCHIVE-MANIFEST
and `archive/outputs-pre-retest-60-tile/` reflect the April-16 archive move
that produced the retest set.

**Interpretation**: the 100× size differential is expected — the retest runs
operate on a different (smaller, production-locked) tile scope and store
far fewer per-tile artefacts. Supersession is scientifically complete (per
`archive/ARCHIVE-MANIFEST.md` on amd-tower and zbook), not size-equivalent.
This matches the plan's framing of phase3a/c as "superseded archival" — they
are not replaced byte-for-byte, they are replaced by a smaller, cleaner
evaluation at a new scope.

**No blocker**, but flag: the plan text in Stage 4.2 invites the reader to
`rm -rf outputs/phase3a` on zbook after Stage 1.4 pushes the legacy set to
QNAP. Do not interpret the size differential as "retest is incomplete".
Supersession is verified by the April-16 ARCHIVE-MANIFEST, not by size parity.

### 0.8 Non-obvious large data

| Host | results | logs | archive/cc-sessions |
|---|---|---|---|
| amd-tower | 185 M | 52 K | 3.0 M |
| sapphire | 125 M | 180 K | 1.5 M |
| zbook | 105 M | 40 K | **295 M** |

Only **zbook's `archive/cc-sessions/` at 295 MB** stands out — well under the
500 MB threshold but large enough to mention. This is session-archive data
(JSONL transcripts) and is git-tracked in `archive/cc-sessions/`. The plan's
Stage 2.5 "send each host's `archive/` to QNAP" already handles this. No
action required for Stage 1.

Nothing else above 200 MB outside the main `inputs/` and `outputs/` trees
considered in the plan.

### 0.9 Git state

All three hosts on the same HEAD: `bb917010cc6e1b2e23242232fdf963ae76fa0da6`
("plan(session-resume): doc-audit re-run + browser-use enablement"). Good.

Dirty state per host:

- **amd-tower** — 1 modified + 4 untracked (4 baseline txts + this agent's
  updates + the NAS migration plan itself):
  - `M planning/55maps-image-generalisation-followups.md`
  - `?? planning/nas-migration-plan.md`
  - `?? planning/nas-migration-baseline-*.txt` (×3)
  - (This report is also untracked, just-created.)

- **sapphire** — 0 modified, many untracked:
  - `configs/run-configs/55maps-image-generalisation-followups.md`
  - 5 × `logs/build_all_consensus_*.log`
  - 40+ × `outputs/h11/pv-diag-384/flash-high-image-n5/**/experiment_intent.md`
  - Notable: the `experiment_intent.md` files are produced by live runs
    invoked from sapphire and are not currently committed. They will be
    preserved by any rsync of `outputs/h11/` to NAS (they are gitignored as
    part of the outputs tree), so Stage 1/2 do not lose them, but they are
    not in git.

- **zbook** — 0 modified, 0 untracked (**clean**).

No host has dirty state that would be lost if the project dir were copied.
All three agree on the same tracked tree. The scripts/configs all match.

## Blockers or surprises

### BLOCKER — sapphire cannot SSH to rpi-server

Stage 0.2 fails from sapphire, and we tripped fail2ban during diagnosis
(1 h ban). Sapphire needs a permanent fix (local key + `IdentitiesOnly yes`
in `~/.ssh/config`) before any Stage 1.3 or Stage 2 step that runs rsync
from sapphire can proceed. Impact: the canonical `outputs/h11/` push (Stage
2.2 step 1), which per D3 must originate on sapphire, is blocked.

Workaround for interim: rsync sapphire's `outputs/h11/` to NAS could be run
**through** amd-tower (sapphire → amd-tower → NAS), but that is ~3 hops and
costs time. Fix the direct path first.

### SURPRISE — sapphire is not a proper h11 superset

D3 in the plan says "Sapphire (7.6 GB) — purely file-merge mechanics, H11 is
scientifically done. Top up with `--ignore-existing` from others." This is
conditionally true, but zbook holds ~3 GB of h11 content (notably
`consensus-384/` with 30 runs and `single-pass-384/` with 10 runs) that
sapphire genuinely lacks at the directory level, not just at the file level.

Before Stage 2, confirm:

1. Are `consensus-384/` and `single-pass-384/` (on zbook) scientifically
   valid predecessors of `consensus-384-UNINTENDED-T1.0/` and
   `single-pass-384-UNINTENDED-T1.0/` (everywhere)?
2. If yes: keep, archive to QNAP as earlier evaluation rather than living
   in active h11? Or keep in active h11 as historical runs?
3. `v2-proposer-test-BAD-TILESIZE/` — discard or archive?

### SURPRISE — amd-tower has no `outputs/pv/`

Plan Stage 1.4 says "From amd-tower: rsync outputs/pv/ to
QNAP/…/outputs-pv-legacy/". amd-tower does not have `outputs/pv/`. The 1.9 GB
`outputs/pv/` exists on **sapphire**. Update Stage 1.4 to pull from sapphire
(and this then depends on the sapphire SSH fix above).

### MINOR — amd-tower free disk tighter than expected

amd-tower has only 161 GB free on `/home` (64 % used). Not a Stage 0 blocker,
but worth noting if any stage proposes staging data on amd-tower.

### MINOR — zbook `archive/cc-sessions/` (295 MB)

Largest non-tracked-elsewhere piece of data outside `inputs/`/`outputs/`.
Already covered by plan Stage 2.5 (per-host archive snapshots to QNAP).

## Ready for Stage 1?

**NO** — one blocker and one plan revision needed.

1. **Fix sapphire → rpi-server SSH auth** (and wait for fail2ban to clear).
   Stage 1.3 push of `inputs/rasters/Russian1981_4326/` from zbook is fine,
   but any sapphire-originated rsync (including the D3 canonical h11 push in
   Stage 2.2) is blocked.
2. **Decide on the four zbook-only h11 top-level dirs** (`consensus-384`,
   `single-pass-384`, `test`, `v2-proposer-test-BAD-TILESIZE`): keep / archive
   / discard. This affects Stage 2 merge strategy, not Stage 1 bytes.
3. **Correct plan Stage 1.4** source host for `outputs/pv/` (sapphire, not
   amd-tower).

Stage 1.1 (safety snapshot of each host's tree to QNAP) and the phase3a/c/rep
archival from zbook to QNAP can begin independently of the above — they do
not require sapphire and do not touch the h11 merge question.
