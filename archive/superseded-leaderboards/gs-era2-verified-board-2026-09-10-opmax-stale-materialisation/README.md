# Stale-materialisation evaluations — nine `-opmax` cells

> **Last revised**: 2026-09-10 (original publication). Board:
> `results/leaderboard/era2/gs-era2-verified-board-2026-09-10/`. Card:
> `planning/gs-era2-verified-board-2026-09-08.md`.

These are the evaluations the nine mis-materialised `-opmax` cells carried on
the GS Era-2 verified board before the 2026-09-10 re-materialisation. They are
kept, not deleted, because they are the board's published numbers for the
2026-09-10 (later) 79-cell build and are cited in that build's changelog.

## What was wrong

Each `-opmax` row is the archived per-architecture Era-2 PV board's
sweep-optimal cell, registered at the F1@20-argmax `(vote_t, prob_t)` of its
own stage sweep (`archive/superseded-leaderboards/leaderboard/era2/pv-materialised/pv_registry.json`,
field `best_at_20m`). The detection GeoJSON each row pointed at was
materialised on 2026-04-19 (commit `bd24293d4`). For nine cells that file does
**not** hold the registered point: re-applying the registry's own filter —
join the proposer pool union (`consensus_path`) to the stage's
`probabilities.json` by candidate index (union feature *i* ↔ key
`candidate_{i:05d}`), keep `vote_count >= vote_t AND mound_probability >= prob_t`
— reproduces the registry's detection count exactly for all nine, while the
archived file holds a different set. The unions, probabilities and sweeps are
unchanged since 2026-04-17/18 (commits `09fe46a7f`, `2e8cc6481`, `c3e8e0701`,
`857d5f714`, `b8961e56f`); only the materialisation moved. The materialisation
was therefore the defective side, and the nine were rebuilt by
`scripts/materialise_opmax_cells.py` into
`results/leaderboard/era2/gs-era2-verified-board-2026-09-10/opmax/materialised/`.

## What is here

| Path | Contents |
|---|---|
| `cells/<slug>/` | Board-frame (`era2-b-487`) evaluations, 10,000-draw bootstrap |
| `opmax/g2/<slug>/` | Era-2-frame (`full_evaluation_bounds.geojson`) reproductions, 200-draw bootstrap |

The superseded detection GeoJSONs themselves are unchanged and stay where they
have always been, under
`archive/superseded-leaderboards/leaderboard/era2/pv-materialised/`.

## The nine, as scored here (stale)

| cell | n | F1@20 (both frames) |
|---|---:|---:|
| `pv-high-text-t0.3-n5-opmax` | 409 | 0.8863 |
| `pv-min-text-t1.0-n10-opmax` | 395 | 0.8771 |
| `pv-min-text-t0.7-n5-opmax` | 385 | 0.8732 |
| `pv-min-text-t0.3-n10-opmax` | 392 | 0.8682 |
| `pv-high-text-t1.0-n5-opmax` | 376 | 0.8607 |
| `pv-high-image-t0.7-n10-opmax` | 351 | 0.7761 |
| `pv-high-image-t0.3-n10-opmax` | 400 | 0.7689 |
| `pv-scale4-optimal-n5-opmax` | 396 | 0.7629 |
| `pv-min-image-t1.0-n10-opmax` | 364 | 0.7409 |

Board-frame and Era-2-frame F1 agree exactly for every `-opmax` cell (gate G6,
`opmax/gates.json`), which is why one column serves both.
