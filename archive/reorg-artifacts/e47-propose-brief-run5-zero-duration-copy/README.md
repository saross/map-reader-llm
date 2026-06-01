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
