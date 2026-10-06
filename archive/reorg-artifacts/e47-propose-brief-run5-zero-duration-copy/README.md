# e47-propose-brief `run_5` — spurious zero-duration copy

**Archived**: 2026-06-01 (Session 95 follow-up).
**Reason**: folder cleanup — `run_5/` held two detection files; this is the spurious one.

## What happened

`run_5/` of e47-propose-brief (`flash-high-text-n5/propose_brief-text/`) contained
**two** detection geojsons:

| file | detections | runtime | verdict |
|---|---|---|---|
| `detections-propose_brief-text-3-flash-2026-04-09.geojson` (kept) | 1694 | **1060.97 s** | genuine API detection pass |
| `detections_propose_brief-text_run05.geojson` (archived here) | 1403 | **0.000224 s** | spurious — not a real run |

The archived `run05` trio (`.geojson`, `.meta.json`, `.tiles.json`) has a
physically-impossible **0.0002 s** runtime (real passes over ~471 tiles take
~1000 s) and an **outlier-low detection count** (1403 vs the five real passes'
1614 / 1755 / 1645 / 1619 / 1694). It is a reorganisation artifact, not a
detection pass. The genuine dated pass remains in `run_5/`.

## Provenance note

The e47 consensus geojsons (`…/consensus/consensus_t*.geojson`) are **frozen from
before this folder reorganisation**, so they do not disambiguate the two files
(`voting_summary.json` records only counts; `contributing_passes` is dir-level).
The decision to keep the dated file rests on the runtime + detection-count
evidence above, not on the consensus provenance.

The single-pass condition for e47 `run_5` (in `results/run-conditions.json`, if
added) points at the kept dated pass. `git mv` move — fully reversible.

## Correction (2026-10-05, Session 160 register repair)

The diagnosis above is wrong: this trio is the output of a **real, billed
Batch API job**, not a reorganisation artefact. On 2026-04-08/09 two
overlapping submit loops ran e47 runs 4 and 5; after both were killed and runs
4 and 5 were relaunched on real-time flex (2026-04-08T23:51Z), loop
`bqkbtf9t9` went on to run its run-5 iteration in batch mode and completed it
at 2026-04-09T03:36:42Z (session
`~/cc-archives/map-reader-llm/2026-04-07T23-44_automated-mound-detection-pipeline`).
The meta's `timestamp.start` is one second before that completion notice, it
records `execution_mode: batch` (lib_batch_api 1.5.0), and the 0.0002 s
"runtime" is that batch writer's timestamp artefact (the March pv-diag batch
metas show 0.000235 s). The detection count is low because 40 of its 487
tiles failed.

Keeping the dated flex pass in `run_5/` is still right: the flex relaunch
superseded this job. Its spend, about US$2.31 to 2.82 at batch, recorded in no
usage field, is carried in `data/pricing/unmetered-executions.json` (entry U3,
PI ruling D35).
