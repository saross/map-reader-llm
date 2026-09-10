# `pv-high-text-t0.0-n3`: a rebuilt union, not a stale sweep

> **Last revised**: 2026-09-11 (original publication). Board:
> `results/leaderboard/era2/gs-era2-verified-board-2026-09-10/`. Card:
> `planning/gs-era2-verified-board-2026-09-08.md`. See [§ Changelog](#changelog).

## What was asked and what was found

The 2026-09-10 nine-cell re-materialisation reported one `-opmax` row it could
not reconcile: the off-board (K = 3) `pv-diag-384::pv-high-text-t0.0-n3-opmax`,
where re-applying the materialisation registry's filter gave **410** detections
against the **403** recorded in both the registry and the archived file. The
entry attributed it to the union having been re-materialised on 2026-07-30
(`f6116cba0`, `77bb342b4`) and classed it with Obs 461 — a sweep older than its
inputs. The PI ruled on 2026-09-11: re-sweep, re-materialise, re-score, report.

Executing that ruling turned up a different diagnosis, and the ruling's premise
does not survive it.

**The 410 is an artefact of a cross-vintage join, not an operating point.** The
union at `consensus_path` today holds **1,319** features; the registered
stage's `probabilities.json` holds **1,256**. The 2026-07-30 rebuild was not an
append: comparing the two blobs feature by feature, only **994 of the 1,256**
original positions still hold the same point, 12 original candidates are gone
and 75 are new. Joining union index *i* to key `candidate_{i:05d}` therefore
pairs 262 of the 1,256 probabilities with the wrong geometry and drops 63
features as unverified. Any count it produces is noise.

**The committed sweep is not stale — it reproduces exactly.** Rebuilding the
April candidate universe from the union blob at `09fe46a7f` and sweeping it
against the stage's own probabilities with the stage's own tool
(`scripts/sweep_f1_greedy_pv.py`, buffers 20/30/40/50 m,
`full_evaluation_bounds.geojson`) reproduces the committed `sweep_2d.json` in
**all 240 rows**, to every recorded digit. Its 20 m argmax is the registered
`(vote_t 3, prob_t 0.15)`, n 403, F1 0.8234, and re-applying the registry
filter to that blob yields exactly the 403 features the row's archived
detection file holds. Registry, sweep, filter and file agree with one another
on the vintage they all describe.

**The argmax does not move on the current vintage either.** The union as
committed today was completely re-verified on 2026-09-08 (`43516df9a`, stage
`verified-v1-n3-recovery-2026-09-08`, same verifier config and system-
instruction hash `2518d529…`, US$1.82 already spent). That stage's manifest is
the current union in index order (all 1,319 centroids reproduce to 0 m), so it
is the only sound "current inputs" join available. Sweeping it gives the same
operating point, `(vote_t 3, prob_t 0.15)`, at n 423 and F1 0.8508 — and
reproduces the committed recovery sweep in all 240 rows.

| | original vintage (April) | current vintage (2026-09-08 complete) |
|---|---:|---:|
| candidate universe | 1,256 | 1,319 |
| 20 m argmax | (3, 0.15) | **(3, 0.15)** — unmoved |
| n at the argmax | 403 | 423 |
| sweep F1@20 | 0.8234 | 0.8508 |
| Era-2-frame F1@20 (14 buffers, 10,000 BCa, seed 42) | 0.8234 [0.7788, 0.8585] | 0.8508 [0.8147, 0.8813] |
| Era-2-frame tile-MCC | 0.7750 [0.7176, 0.8263] | 0.7857 [0.7273, 0.8363] |
| tile confusion (TP/TN/FP/FN) | 184 / 247 / 11 / 45 | 188 / 246 / 12 / 41 |

At 20 m the current vintage ties two points at F1 0.8508 — (3, 0.15) at n 423
and (3, 0.20) at n 416. The tie is broken the way the sweep tool breaks it, by
first occurrence, which is the registered point.

## What was NOT done, and why

**The registered row was not repointed.** Its `detections` still name the
403-feature April file, and its evaluation still records F1@20 0.8234. Three
reasons:

1. The row is defined as *the archived per-architecture Era-2 PV board's
   sweep-optimal cell* (`_note`, "IN-SAMPLE OPTIMUM (E56 class)"). On its own
   vintage it is exactly that, and it is correct.
2. Repointing it at the current vintage would silently change what the row IS —
   from an April cell of the archived board to a September re-verification of a
   rebuilt candidate set. That is a scope change the PI ruled on a different
   premise, so it is put back to the PI rather than taken.
3. The row is off-board (K = 3 < 5), so nothing on the board depends on the
   choice: no re-tier, no MCB, no Tier-1 movement in either direction.

Everything needed to make the other choice is in this directory. Repointing
would mean pointing the row's `detections` at
`current-vintage/pv-high-text-t0.0-n3-current-vintage.geojson`, its `eval_path`
at `current-vintage/era2-eval/evaluation.json`, and adjusting the off-board
gate expectation in `scripts/build_gs_era2_board_opmax.py` from the archived
0.8234 / 403 to 0.8508 / 423.

## The class, across the whole registry

`scripts/check_pv_sweep_vintage.py survey` classifies every `pv_registry` cell
by comparing three universe sizes: the union's feature count, the
probabilities' key count, and the sweep's own universe (its `n` at
`vote_t 1, prob_t 0.0`). Over the 30 cells (`vintage-survey.json`):

| verdict | n | meaning |
|---|---:|---|
| `same-vintage` | 24 | all three agree; nothing to check |
| `probabilities-grew` | 4 | the sweep saw fewer candidates than are now verified — the probabilities were completed after the sweep ran. The index join stays SOUND; only the sweep is stale. This is the Obs 461 class, and these four are exactly the stages re-swept on the PI's 2026-09-08 ruling (`results/recovery-reeval-2026-09-08/pv-diag-384/`) |
| `union-rebuilt` | 1 | `pv-high-text-t0.0-n3` — the union grew past the probabilities, so the join is INVALID |
| `manifest-mode` | 1 | `pv-flash-high-text-16of30`, whose universe is a manifest keyed by `candidate_id`; there is no index join to go stale |

The other two off-board (K = 3) rows are clean on every check: for
`pv-min-text-t0.0-n3` the union, probabilities and sweep all hold 1,087
candidates and the filter reproduces the registered 393 exactly; for
`pv-n1-image-t0-n3` all three hold 690 and the filter reproduces 446. Neither
union was touched by the 2026-07-30 recovery, which rebuilt only the two live
`t0.0` cells of the `flash-high-*-n5` pools.

The guard is now built in. `scripts/materialise_opmax_cells.py` classifies each
row before filtering and publishes **no count at all** for a `union-rebuilt`
row (`check.json`, field `vintage`), instead of the soft-failing join that
produced the 410.

## Files

| path | what |
|---|---|
| `vintage-survey.json` | the 30-cell classification, with each input's last commit |
| `vintages.json` | the two universes' sizes and provenance for this cell |
| `original-vintage/crops/candidate_manifest.json` | the April universe, reconstructed from the union blob at `09fe46a7f` |
| `original-vintage/sweep_2d.json` | the reproduction sweep — identical to the committed `sweep_2d.json` in all 240 rows |
| `current-vintage/crops/candidate_manifest.json` | the current union as a sweepable manifest |
| `current-vintage/sweep_2d.json` | the current-vintage sweep — identical to the committed 2026-09-08 recovery sweep in all 240 rows |
| `current-vintage/pv-high-text-t0.0-n3-current-vintage.geojson` | the comparison cell: (3, 0.15) on the current union against the complete re-verification, 423 features |
| `current-vintage/…provenance.json` | its inputs' git blob hashes and last commits |
| `current-vintage/era2-eval/` | its Era-2-frame score under the row's own recipe |

Each vintage directory also needs a `verified/probabilities.json` to be swept;
those are byte-for-byte copies of committed files and are not duplicated here.
Recreate them with `scripts/check_pv_sweep_vintage.py manifests`.

## Reproducing

```bash
python scripts/check_pv_sweep_vintage.py survey \
    --write results/leaderboard/era2/gs-era2-verified-board-2026-09-10/opmax/staleness-2026-09-11/vintage-survey.json

python scripts/check_pv_sweep_vintage.py manifests --cell pv-high-text-t0.0-n3 \
    --original-commit 09fe46a7f \
    --current-probabilities outputs/h11/pv-diag-384/flash-high-text-n5/text-t0.0/verified-v1-n3-recovery-2026-09-08/probabilities.json \
    --out-dir results/leaderboard/era2/gs-era2-verified-board-2026-09-10/opmax/staleness-2026-09-11

# one per vintage
python scripts/sweep_f1_greedy_pv.py --config high-text-t0.0-n3 \
    --crops-dir <vintage>/crops --verified-dir <vintage>/verified \
    --bounds inputs/vectors/bounds/384/full_evaluation_bounds.geojson \
    --buffer-m 20 30 40 50 --output <vintage>/sweep_2d.json

python scripts/check_pv_sweep_vintage.py materialise --cell pv-high-text-t0.0-n3 \
    --union outputs/h11/pv-diag-384/flash-high-text-n5/text-t0.0/consensus/consensus_t1.geojson \
    --probabilities outputs/h11/pv-diag-384/flash-high-text-n5/text-t0.0/verified-v1-n3-recovery-2026-09-08/probabilities.json \
    --vote-t 3 --prob-t 0.15 \
    --stage-id flash-high-text-n5-text-t0.0-verified-v1-n3-recovery-2026-09-08 \
    --output <…>/current-vintage/pv-high-text-t0.0-n3-current-vintage.geojson

python scripts/evaluate_detections.py \
    --detections <…>/pv-high-text-t0.0-n3-current-vintage.geojson \
    --ground-truth inputs/vectors/references/mounds-reference.geojson \
    --bounds inputs/vectors/bounds/384/full_evaluation_bounds.geojson \
    --buffers 5 10 15 20 25 30 35 40 45 50 75 100 125 150 \
    --bootstrap 10000 --seed 42 --mcc \
    --output-dir <…>/current-vintage/era2-eval \
    --label pv-diag-384__pv-high-text-t0_0-n3-opmax-current-vintage
```

All of it ran on sapphire; zero API spend.

## Changelog

### 2026-09-11 — Original publication

Built in S153 on the PI's 2026-09-11 ruling ("re-sweep, re-materialise,
re-score, report") for the one `-opmax` row the 2026-09-10 nine-cell
re-materialisation could not reconcile. The ruling's premise — the Obs 461
sweep-staleness class — did not survive execution: the sweep reproduces
exactly on its own vintage, and the 410 that prompted the ruling is a
cross-vintage index join. Reported to the PI with the repoint left untaken.
