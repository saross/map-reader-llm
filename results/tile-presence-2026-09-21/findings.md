# Tile presence: what a metric indifferent to over-generation buys, and what it costs

> **Last revised**: 2026-09-21 (first publication; PI ruling 2026-09-21).
> See [§ Changelog](#changelog) for revision history.
> Sources: [`leaderboard.md`](leaderboard.md),
> [`frontier/frontier.md`](frontier/frontier.md),
> [`verifier-costs.json`](verifier-costs.json). Built by
> `scripts/build_tile_presence_board.py` from the committed sweep records.
> Zero API.

## Who this is for

A reader whose unit of interest is **the tile, not the detection**. Survey
triage asks "is there a mound on this sheet square?", and for that question
tile-level Matthews correlation (tile-MCC) is the right currency and
micro-F1 @ 50 m is not. This directory answers, for every configuration the
project has swept: *what is the best tile-presence discrimination this pool
can support, at what vote count, and what would the verifier pool cost?*

It is **not** a board. The main boards
(`results/55map-final-board-r2-2026-09-06/final-board-50m.md` and the two
image campaigns' findings) report tile-MCC beside micro-F1 **at the carried
and F1-oracle points**, where both metrics describe a configuration someone
chose in advance or could have. Nothing here is such a configuration.

## Every row is an oracle, and the ruling that made this a separate table

The operating point on each row is the tile-MCC argmax over that
configuration's whole achievable grid, chosen **on the evaluation reference
itself**. **No configuration on this table has a calibrated carried point at
its tile-MCC optimum** — 32 of the 35 rows have a carried point and not one
of them coincides with the optimum, and the remaining three (`UPL`, `A-N1`,
`B-N1`) have no carried cell at all. Read the table as an upper bound on
what tile-presence discrimination a pool can support, never as a result.

The tile-MCC optimum was briefly published on the boards as an "MCC oracle",
first unconstrained (PI ruling 2026-09-20 item 2) and then pinned to each
family's carried vote count (ruling 6c, same day). **PI ruling 2026-09-21
dropped it from the main boards under both definitions** and moved it here.
The reason is the next section: beside an F1 oracle, a tile-MCC optimum
reads as a rival configuration, and it is not one.

## The vote-count finding

**26 of the 35 configurations put their tile-MCC optimum at a single vote**,
abandoning the unanimity their carried point relies on. Broken down:

| track | configurations | at k = 1 | vote counts seen |
|---|---:|---:|---|
| r2 55-map board | 23 | **18** | 1, 3 |
| Gemini 3.7 image campaign | 6 | 2 | 1, 2, 3, 5 |
| Gemini 3 image campaign | 6 | **6** | 1 |

On the **board the collapse is total**: all 23 families put the optimum at
the lowest vote count their sweep offers, and the five that do not reach
k = 1 — `TH7`, `T03`, `TM`, `IM`, `UPL` — sit on their k = 3 floor because
their verified unions begin at three votes, not because three votes won.
That is the "13 of 13" of PI decision log D6a read at full scope: of the
eighteen board families whose sweeps reach a single vote, eighteen take it,
and thirteen of those thereby abandon a **multi-vote F1 oracle** (the other
five already had an F1 oracle at k = 1).

The mechanism is structural. Tile-MCC asks only whether a tile was hit at
all, so a second or third detection inside an already-positive tile is free
in that currency and costly in F1. Lowering the vote threshold adds exactly
that kind of detection. A metric indifferent to over-generation *within* a
tile will always prefer the setting that over-generates.

**But the collapse is a property of the pool, not of the metric alone.** The
Gemini 3 image row collapses completely — all six rungs to a single vote,
paying **0.23 to 0.31 of micro-F1** against their own carried points
(`G3IMG-ARM2-K5` −0.3089, `G3IMG-ARM1-K5` −0.2972, `G3IMG-ARM2-K3` −0.2355,
`G3IMG-ARM1-K3` −0.2301). The 3.7 image row barely moves: only its two
K = 1 rungs sit at a single vote because that is all they offer,
`IMG-ARM2-K3` steps down one notch to k = 2, and `IMG-ARM1-K3`,
`IMG-ARM1-K5` and `IMG-ARM2-K5` put the optimum at **full unanimity**. The
reading that fits is Obs 485's: the Gemini 3 image proposer over-generates
roughly threefold at a single pass, so its low-vote band is full of
detections landing in tiles that are already hit, which tile-MCC takes for
free; the 3.7 pool is clean enough that its low-vote band adds
false-positive *tiles* instead. **If that reading holds, the depth of the
collapse measures proposer over-generation** — a diagnostic sitting in sweep
data already on disk.

## The cost dimension

A tile-MCC optimum at k = 1 does not just change a threshold: it needs a
verifier probability for **every candidate with at least one vote**, not
only the unanimous ones. The `pool @ votes` column is that pool, read off
the sweep's own zero-threshold row, and `pool US$` prices it at the audited
per-candidate rate of that configuration's verifier leg.

What that buys is not flattering. The table's top two rows —
`G3IMG-ARM2-K5` at tile-MCC 0.7755 and `G3IMG-ARM2-K3` at 0.7706 — need
pools of **45,786 and 36,389 candidates**, costing **US$51.09 and
US$40.58**. Row 3, `IMG-ARM2-K5`, reaches **0.7681** on a **5,593**-candidate
pool for **US$6.21**, and does it at micro-F1 **0.9280** against
`G3IMG-ARM2-K5`'s **0.5217**. 8.2 times the verifier spend and a 0.4063
collapse in micro-F1 buys **0.0073** of tile-MCC. Anyone choosing a tile-presence
deployment on tile-MCC alone should see that trade before choosing.

**11 of 35 rows draw on a pool smaller than their verifier leg**: they
inherit probabilities from a larger verification (every A/B and 3.7 rung
inherits from its K = 10 or K = 5 union's single leg), so `pool US$` is what
the point alone would cost, not what was spent. **No row asks for more
candidates than its leg verified**, so every point on this table is
reachable from a verification that already exists.

### What is not priced, and why

Costs come from `scripts/audit_verifier_cost.py` over each leg's committed
metas — the auditor both image campaigns' post-run reports cite — with the
campaigns' own published figures used where the auditor cannot reach the
truth. **21 of 35 configurations are audited, 2 published, and 12 have no
usable cost**:

| basis | configurations | meaning |
|---|---|---|
| `audited` | 21 | the auditor read every pass of the leg |
| `published` | `IMG-ARM2-K1`, `IMG-ARM2-K3` | the auditor reads a lower bound; the figure is `outputs/gemini37-image-55map-2026-09-13/post_run_report.md`'s |
| `unaudited` | `TH7`, `T03`, `TM`, `IM`, `A-N{1,3,5,10}`, `FOURTH-N{1,3,5,10}` | neither: no cost is shown |

The twelve unaudited legs are all pre-2026-09-14 stages whose `run_pv.py`
cleanup overwrote `run.meta.json` with the retry pass's usage only, so the
auditor reads a **lower bound** and says so. A lower bound multiplied by a
pool size is a number that looks like a cost and is not, so those rows are
left blank rather than filled. `verifier-costs.json` names each leg's stage
directories as an audit target. **Where the auditor and a published figure
both exist they agree to the cent on all ten overlapping legs** — an
unplanned cross-check that the two sources have not drifted.

## The frontier is the honest version

A leaderboard shows one end of a trade. [`frontier/`](frontier/frontier.md)
shows the trade: per configuration, the `(micro-F1 @ 50 m, tile-MCC)`
Pareto-non-dominated sweep points, with the carried point and the F1 oracle
marked on a figure per campaign.

**21 of 35 configurations have more than two non-dominated points** — a
genuine interior choice rather than a straight swap between the two ends.
The split is the finding again: **16 of the board's 23** and **5 of the
Gemini 3 row's 6** do, and **none of the 3.7 image row's six** does. On the
3.7 pool the two metrics have essentially nothing to argue about; on the
Gemini 3 pool they have a long argument.

## Caveat: the E89 verifier-drift floor

Five rows' advantage over their own carried point is **smaller than or close
to the measured re-invocation drift** of the verifier that produced them:
`FOURTH-N1` (+0.0004), `IMG-ARM2-K3` (+0.0008), `IMG-ARM1-K5` (+0.0014),
`IMG-ARM2-K5` (+0.0022) and `IMG-ARM2-K1` (+0.0045).

Independent re-invocations of the arm 2 verifier (`gemini-3.7-flash`, low
thinking, T = 0) over the same 9,173-candidate K = 5 union flip **2.46 % of
decisions** at the 0.90 operating point (226 of 9,173, Wilson 95 % interval
[2.17 %, 2.80 %]), and in metric units the drift-only contrast is
**+0.0008 micro-F1** (*p* = 0.4015) and **−0.0005 tile-MCC** (*p* = 0.8225)
at the carried point (`reports/image-2x2-tests-declaration-2026-09-19.md`
§ 5 caveat 1, read 2026-09-21; the arm 1 floor is
`planning/pi-decisions-2026-09-20.md` D8 — 2.41 % flips, +0.0001 tile-MCC,
*p* = 0.93). **A ΔMCC of order 0.001 is not an effect**; it is the verifier
disagreeing with itself. Read the ΔMCC column against that band before
quoting it, and note that **no drift floor has been measured for the Gemini
3 verifier at all** (D4, 2026-09-20), so the Gemini 3 row's ΔMCC values have
no band to be read against.

## Changelog

### 2026-09-21 — Original publication

**Refresh trigger**: PI ruling 2026-09-21, superseding ruling 6c of
2026-09-20. The "MCC oracle" is dropped from the main boards under both
definitions — unconstrained and at-the-carried-k — tile-MCC stays reported
beside micro-F1 at the carried and F1-oracle points, the F1 oracle stays
free over both dimensions, and the tile-MCC optimum moves into this separate
tile-presence presentation.

**What this is**: 35 configurations — the r2 board's 23 families and the two
image campaigns' twelve rung x arm cells — each at its unconstrained
tile-MCC optimum, with the vote count as a column, the verifier pool priced,
and the micro-F1 / tile-MCC Pareto front beside it.

**Numbers that moved**: none. Every figure is read from a committed sweep
CSV, from `scripts/audit_verifier_cost.py` over committed metas, or from a
cited post-run report. No sweep was re-run and no API was called.

**What did NOT change**: no board was re-tiered, no cell was deleted, and
every cell the boards stop presenting stays on disk. The corresponding board
and campaign edits are recorded in those documents' own changelogs.
