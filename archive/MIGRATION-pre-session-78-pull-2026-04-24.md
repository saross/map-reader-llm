# Migration Note — `pre-session-78-pull-2026-04-24/`

**Migration date**: 2026-04-27 (Session 80, carry-over backlog item #8)
**Trigger**: Project archive-don't-delete policy review.
**Outcome**: Documentation-only migration. No file movement was performed
because the directory no longer exists on any host; this note captures
provenance so the path is searchable in the working tree per project policy.

## Original location

- **Host**: `sapphire` (192.168.1.150) only.
- **Path**: `~/Code/map-reader-llm/archive/pre-session-78-pull-2026-04-24/`
- **Existed on**: amd-tower? No. Local working tree never contained this
  directory — confirmed by `ls /home/shawn/Code/map-reader-llm/archive/`
  on 2026-04-27.
- **Tracked by git anywhere**? No. Created and removed on sapphire entirely
  outside version control.

## Provenance

Created during Session 78 (2026-04-24) when an attempted `git pull` on
sapphire was blocked by 10 untracked files in the working tree. Those
untracked files were Session-78 outputs generated on sapphire that had not
yet been registered with git on that machine. To unblock the pull, they were
moved into a sibling archive directory rather than deleted.

The Session-78 outputs in question were subsequently committed to
`origin/main` from amd-tower (where the canonical copies were already
present after `rsync`-back). The relevant canonical commits are:

- `aa36b638` — `data(session-78): GS text-HIGH Era 2 companion + 487-tile
  leaderboard cell`
- `4cc95e80` — `data(session-78-q3): 55-map text-HIGH corrected F1 +
  verifier calibration`
- `651b8ab4` — `data(session-78): image-track PV anchor + consensus-only F1
  verification`

Per the Session 78 reflection note (Step 6 backlog item logged at commit
`cf192345`, see `docs/notes/reflections/session-log.md` line 5602 and
`planning/paper-writeup-continuity.md` lines 1002–1020), every file in
the archived directory was an **exact duplicate** of a file already
committed to `origin/main` in its canonical location.

## Reproducibility status

**Fully reproducible from git.** Zero data loss; zero recovery value.
Because the originals are in the canonical commits listed above, the
archived copies were redundant. The backlog item explicitly proposed
hash-comparison-then-`rm` as the appropriate cleanup; the dir has since
been removed from sapphire's working tree (verified 2026-04-27 via
`ssh sapphire 'find /home/shawn/Code/map-reader-llm -maxdepth 5 -type d
| grep -i pre-session'` returning `NOT_FOUND`).

## Contents inventory at time of cleanup

10 untracked files (per Session 78 backlog note). Exact filenames not
recorded in git, but every file is recoverable from one of the three
canonical commits above. Approximate footprint: ~1 MB (per backlog
estimate). No API outputs, probability files, or `run.meta` records were
unique to this archive — every artefact is on `origin/main`.

## New location

**None — directory no longer exists.**

This migration note is the sole working-tree record of the directory's
former existence. The dir was never tracked in git, so no `git mv` is
involved and there is no `archive/migrated/` destination directory.

If the project ever needs to repopulate the directory for forensic
purposes, the canonical commits above contain every file that was inside
it.

## Whether anything had to be committed first

**No.** Per `feedback_commit_api_outputs.md`, irreplaceable API outputs
must be committed to git before archive movement. In this case the API
outputs that the archive shadowed were already on `origin/main` via the
Session 78 commits cited above — the archive was duplicate material, not
irreplaceable data.

## Related

- Backlog item: `planning/paper-writeup-continuity.md` lines 1002–1020
  (Step 6 backlog item 7 from Session 78; carry-over item 8 in Session 80
  entry-point queue at line 1233).
- Session log entry: `docs/notes/reflections/session-log.md` line 5602.
- Memory: `feedback_commit_api_outputs.md` (commit-API-outputs-first
  policy that this migration honours by confirming the archive shadowed
  already-committed material).
