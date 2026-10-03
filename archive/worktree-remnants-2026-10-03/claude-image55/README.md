# Remnants of the `claude-image55` worktree on sapphire

Archived 2026-10-03 (Session 158) before the worktree was removed at the PI's
instruction ("please clean up all worktrees"). The worktree was on branch
`gemini37-image-55map-2026-09-13` at `0b92df092`, which has no commits
outside `origin/main`.

- `pre-merge-backup/`: the worktree's untracked `.pre-merge-backup/`
  folder (12 files), present nowhere else.
- `sweep-log-uncommitted.patch`: 504 lines appended to the tracked
  `outputs/gemini37-image-55map-2026-09-13/sweep.log` and never committed.

Everything else in the worktree was either a symlink into the main checkout
or byte-identical to a file in sapphire's main checkout, so nothing else was
lost by the removal.
