# Superseded — N=1 baseline matrix, 384px, 30 m-only (`paper-eval/n1/384px`)

**Archived**: 2026-06-02 (Session 95 follow-up).
**Reason**: superseded by the all-buffers version of the same matrix.

## What this is

The legacy `results/paper-eval/n1/384px/` tree (36 tracked files: the three
`batch_summary.{csv,json,md}` files plus 11 model-config pool sub-directories). This
is the **N=1 single-pass baseline matrix**
at 384 px, scored at the **30 m buffer only** — the denominators that quantify how much
consensus voting and the proposer-verifier pipeline improve over a single pass.

## Why superseded

`results/paper-eval/n1/384px-all-buffers/` (18 pools, all four 20/30/40/50 m buffers)
**supersedes** this 30 m-only cut by its own metadata (*"Supersedes the 30m-only
evaluations in n1-eval-384px.yaml"*). The pool set here is a strict subset of the
all-buffers version (verified 2026-06-02: 0 pools present here that are absent there),
so this tree is fully redundant.

## Provenance (for the eventual manifest authoring)

The baseline pools are **cross-run** but every cell maps to one real source run
(background-agent traced 2026-06-02, all 18 all-buffers pools):

- `pv-diag-384` — 10 pools (proposer single-pass outputs inside the PV diagnostic run)
- `n1-outstanding-384` — 7 pools
- `retest-h11-single-pass-384-t0` — 1 pool (`flash-text-minimal-t-0-0`)

The agreed manifest model is: **single-pass conditions on those 3 runs + one `analyses`
row**, NOT a pseudo-run (consistent with the leaderboard + wbf/GAP-6 precedent). When
authoring, point `eval_path` at `384px-all-buffers/` (full buffer set), not at this
archived 30 m-only tree. See `planning/paper-writeup-continuity.md` Session 95
carry-forward #3.

`git mv` move — fully reversible.
