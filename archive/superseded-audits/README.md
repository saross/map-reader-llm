# Superseded Pre-Launch Audits

**Status**: archived. Pre-launch audit documents whose corresponding production run has completed and whose findings are now documented in the matched `post_run_report.md` at the original `outputs/<run>/` location.

## What goes here

- `pre_launch_audit.md` files from `outputs/<run>/` where the run is complete.
- Matched pre-launch audits from `configs/run-configs/<run>_pre_launch_audit.md` where the same pairing applies.

## What does NOT go here

- The production `post_run_report.md` files (active; stay at `outputs/<run>/` and `configs/run-configs/<run>_post_run_report.md`).
- Pre-launch audits for runs that have NOT yet been executed (stay at the original location).
- Analysis plans or decision records (separate: `archive/completed-analysis-plans/`).

## Filename convention

Files are prefixed with their original location to avoid collisions:

- `outputs-<run>-pre_launch_audit.md` for audits originally at `outputs/<run>/pre_launch_audit.md`.
- `configs-<run>_pre_launch_audit.md` for audits originally at `configs/run-configs/<run>_pre_launch_audit.md`.

## Relationship to other archive subdirs

- `archive/completed-analysis-plans/`: plans that drove a specific analysis (including early-phase pre-launch work); broader scope.

## How to retrieve

Each file has a SUPERSEDED banner identifying:

- Original location.
- Corresponding `post_run_report.md`.
- Date of run completion.
