# Superseded evals — `n1-outstanding-384`

**Archived**: 2026-05-31 (Session 95).
**Reason**: superseded by the Session 94/95 standardised re-score.

## What is here

- `paper-eval-384px-outstanding/` — the legacy `results/paper-eval/n1/384px-outstanding/`
  batch-eval tree (24 tracked files: `batch_summary.{csv,json,md}` + 7 model
  sub-directories). These are the **superseded** paper-pipeline evaluations of the
  `n1-outstanding-384` run (study manifest: *"H11 Pro MEDIUM T=0.7 384px"* plus the
  outstanding flash/pro pools that completed the n1 384px matrix).

## Why superseded

The 3b standardisation campaign re-scored every `n1-outstanding-384` condition through
the current standard scorer (14 uniform buffers + MCC, BCa bootstrap seed 42) on each
condition's own scope. The current, authoritative evals live at:

- `results/rescore-2026-05-31/n1-outstanding-384/` — 7 pools, individual-pass evals
  (commit `02f1493b`).

All seven pools in the archived tree map 1:1 to the re-scored pools (the legacy tree
uses full `model-prompt-temperature` names; the run/rescore use short names):

| legacy `384px-outstanding/` dir | run / rescore pool |
|---|---|
| `pro-image-high-t-0-0` | `pro-image-high-t0` |
| `pro-image-medium-t-0-7` | `pro-image-medium-t07` |
| `pro-text-high-t-0-0` | `pro-text-high-t0` |
| `pro-text-medium-t-0-7` | `pro-text-medium-t07` |
| `flash-image-minimal-t-0-0-487-tiles` | `image-t0` (487-tile sibling) |
| `flash-image-minimal-t-0-3` | `image-t03` |
| `flash-text-minimal-t-0-3` | `brief-text-t03` |

**Caveat flagged for review**: the text-flash pool is named `brief-text` in the run
but `flash-text-minimal` in the legacy tree (prompt-name convention difference, not a
different pool). Worth a one-glance confirmation.

## NOT archived (held for joint review — Session 95 Q4)

Left in place under `results/paper-eval/n1/` pending the user's adjudication:

- `384px/`, `384px-all-buffers/` — 384 px but **not** the `-outstanding` run; correspondence
  to a specific run not yet confirmed.
- `512px/`, `512px-all-buffers/` — these are **not** `n1` at all: their `batch_summary`
  rows are `P2a/P2b/P2c/P2d` (the `retest-phase2*` runs). Do not archive as n1.

## Reversal

`git mv` move (tracked, R100 renames) — fully reversible. See the commit that landed
this README for the exact path mapping.
