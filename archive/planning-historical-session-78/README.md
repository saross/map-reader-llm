# Session 78 Verifier Calibration Matrix — Historical Summary Docs

**Status**: archived. Two summary documents authored during Session 78 (2026-04-24/25) to record per-cell metrics for the seven-variant verifier prompt matrix across image and text candidate pools. Preserved for the audit trail of how the canonical `verify_adversarial-text` Pareto-dominance result was first established and subsequently re-confirmed.

## What goes here

- Session-78-vintage planning summary docs whose canonical metrics have since been refreshed (Phase D shared-crops parity re-run; bootstrap CIs upgraded from N=1K to N=10K; BCa migration), re-confirmed, and superseded by the canonical artefacts in `results/verifier-calibration-matrix/` and `results/verifier-calibration-matrix-pairwise/`.

## What does NOT go here

- Active planning documents (stay in `planning/`).
- Active calibration metrics (live under `results/verifier-calibration-matrix/<pool>-<variant>/calibration.json` and `evaluation.json`).
- Plans whose execution completed in Sessions 81–82 (those live at `archive/planning-completed-session-81-82/`).

## Index of archived documents

| File | Created / refreshed by | Authoritative reference for current state |
|---|---|---|
| `session-78-matrix-calibration-summary.md` | Created `88d6b55b` (Phase C, 2026-04-25); refreshed `c0eb61f9` (Phase D shared-crops parity, 2026-04-27); re-confirmed `2a928cf7` (Session 80 Wave 3 staleness audit); bootstrap upgraded to N=10K at `e1955ddf` (2026-04-28); BCa migration `28e7de84` (post-Session 80) | `results/verifier-calibration-matrix/<pool>-<variant>/calibration.json` (per-cell AUC/Brier/ECE with current bootstrap CIs); Obs 290 Theme 8 in `docs/notes/reflections/working-notes.md` |
| `session-78-verifier-calibration-matrix-summary.md` | Created `6d1cad27` (Phase B/C, 2026-04-25); refreshed `c0eb61f9` (Phase D shared-crops parity, 2026-04-27); pairwise extension `fffecb7d` (Session 79 pairwise permutation tests) | Obs 277 (Session 78 closure — canonical `verify_adversarial-text` Pareto-dominance) and Obs 290 Theme 8 (Wave 3 re-confirmation) in `docs/notes/reflections/working-notes.md`; `results/verifier-calibration-matrix-pairwise/README.md` for the pairwise extension |

## Relationship to other archive subdirs

- `archive/planning-completed-session-81-82/`: planning docs whose execution completed in Sessions 81–82.
- `archive/completed-analysis-plans/`: earlier (Session-77-and-prior) completed plans.
- `archive/superseded-audits/`: pre-launch-audit files (single-run `pre → post` pairing).

## How to retrieve

Each archived file carries a SUPERSEDED banner immediately under its H1 heading, identifying (a) the supersession date (2026-05-01), (b) the executing session and the relevant commits, and (c) the authoritative reference for current state. Use that banner to navigate from this archive back to the active artefact.
