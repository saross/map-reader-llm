# Completed Analysis Plans

**Status**: archived. Analysis plans and decision records for analyses whose execution is complete and whose results are documented in the active `results/` tree. Preserved for audit trail of how each analysis was designed.

## What goes here

- Planning documents for analyses that have been fully executed.
- Decision records (methodology choices, metric selection, threshold picking) for executed analyses.
- Pre-launch audit / pre-run analysis plans where a `post_run_report.md` or equivalent has been generated.

## What does NOT go here

- Active planning documents (stay in `planning/`).
- Pilot or superseded data outputs (go to `archive/outputs-*-*/` or `archive/deprecated-*/`).
- Plans for analyses that have been partially executed but not yet completed (stay in `planning/` with status annotation).
- Pre-launch audits for production runs — those live at `archive/superseded-audits/` (separate bucket because they have a specific `pre → post` pairing).

## Relationship to other archive subdirs

- `archive/superseded-audits/`: pre-launch-audit files specifically; this subdir is broader (plans + decisions).
- `archive/deprecated-studies/`: study YAMLs that are no longer active. Often paired with a plan here if the plan drove the study design.
- `archive/implemented-instructions/`: software-feature specifications (different focus from analysis plans).

## How to retrieve

Each file moved into this directory has a SUPERSEDED banner at the top identifying (a) the date of supersession, (b) the reason, and (c) the replacement doc. Use that banner to navigate from this archive to the active artefact.
