# Planning Documents Completed in Sessions 81–82

**Status**: archived. Nine planning documents whose execution completed during Session 81 (2026-04-29) and Session 81's close-out + Session 82 (2026-04-30 to 2026-05-01). Preserved for audit trail of how each follow-up workstream was scoped and delivered.

## What goes here

- Planning documents whose proposed work has been fully executed (run, audit, or app build) and whose outcomes are documented in active artefacts (`results/*/report.md`, `planning/paper-writeup-continuity.md` closure sections, working-notes Obs entries, or in-tree scripts).
- Mid-flight status snapshots of the same work (e.g., the daylight-sweep checkpoint), preserved alongside their parent plan.
- Audit reports whose findings have been incorporated into closure narratives.

## What does NOT go here

- Active planning documents (stay in `planning/`).
- Planning documents whose execution was started but not completed (stay in `planning/` with a status annotation).
- Pre-launch audits of single production runs — those live at `archive/superseded-audits/` (separate bucket, distinct `pre → post` pairing).
- Earlier Session-77-and-prior completed plans — those are at `archive/completed-analysis-plans/`.

## Index of archived documents

| File | Executing session / commit(s) | Authoritative reference |
|---|---|---|
| `gs-fp-classification-plan-2026-04-29.md` | Session 81 (`ee4f18cb`, `9fa6db4e`, `ec21c8ef`; Obs 306–308) | `results/55maps-fp-classification/report.md`; `planning/paper-writeup-continuity.md` §"Session 81 closure roll-up" Item 1 |
| `v2-burial-mound-bet-test-app-plan-2026-04-29.md` | Session 81 (bet-test app built and run; 0/177 review errors; Obs 312) | `planning/paper-writeup-continuity.md` §"Session 81 closure roll-up" Item 13; Obs 312 in `docs/notes/reflections/working-notes.md` |
| `daylight-followup-sweep-plan-2026-04-29.md` | Session 81 (full 165-cell N=10K sweep complete) | `planning/paper-writeup-continuity.md` §"Session 81 closure roll-up" (closure note on the daylight follow-up sweep) |
| `daylight-sweep-status-2026-04-29.md` | Session 81 (mid-flight status snapshot; sweep completed) | Same as the parent plan above |
| `pairwise-bootstrap-ci-fix-plan-2026-04-29.md` | Session 81 (sparse-coverage suppression patch landed at `2026999a`; checklist marked DONE at `2ac81876` on 2026-05-01) | `planning/paper-writeup-continuity.md` §"Session 81 closure roll-up"; codified in `scripts/evaluate_detections.py` and `scripts/lib_advanced_metrics.py` |
| `dedupe-raw-gs-student-data-plan-2026-04-30.md` | Session 82 (`a0ee28c6..6f15b8c9`; Obs 316 + 317) | `planning/paper-writeup-continuity.md` §"Session 82 closure (2026-05-01)"; Obs 316 + 317 in `docs/notes/reflections/working-notes.md` |
| `input-expansion-audit-2026-04-29.md` | Audit complete (commit `29b8cc64`; Obs 305); daylight follow-up sweep finished in Session 81 | `planning/paper-writeup-continuity.md` §"Session 81 closure roll-up"; Obs 305 in `docs/notes/reflections/working-notes.md` |
| `ci-rerun-todo.md` | "0 files require a re-run" per the doc's own executive summary; durable mitigation tracked as Item #8 | `results/ci-metadata-registry.md`; `planning/paper-writeup-continuity.md` §"Session 81 closure roll-up" Item 8 |
| `candidate-review-app.md` | App built as `scripts/review_candidates.py` and in active use; "Future Extensions" implemented selectively per design judgement; design ceiling reached | `scripts/review_candidates.py` |

## Relationship to other archive subdirs

- `archive/completed-analysis-plans/`: earlier (Session-77-and-prior) completed plans; this subdir is the Session-81–82 cohort.
- `archive/superseded-audits/`: pre-launch-audit files specifically (single-run `pre → post` pairing).
- `archive/infrastructure-planning/`: infrastructure / migration / operations plans.
- `archive/implemented-instructions/`: software-feature specifications (different focus from analysis or workstream plans).

## How to retrieve

Each archived file carries a SUPERSEDED banner immediately under its H1 heading, identifying (a) the supersession date (2026-05-01), (b) the executing session and commit(s), and (c) the authoritative reference for current state. Use that banner to navigate from this archive back to the active artefact.
