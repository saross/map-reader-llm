# Superseded: h10 pool_160_hp4hn4 consensus t1/t2 (archived 2026-09-12)

These two consensus unions —
`outputs/h10/evaluation-v2/pool_160_hp4hn4/consensus/consensus_t1.geojson`
(1,454 features) and `consensus_t2.geojson` (474 features) — were built from a
slightly **earlier state of their own five-pass pool** and were never rebuilt.
Re-derived today from the pool as committed, the same thresholds give **1,474**
and **477**: `t1` was short 20 clusters (3 of its features have no re-derived
match within 1 m) and `t2` was short 3. Diagnosis and the full sweep comparison:
`reports/union-staleness-retrospective-2026-09-12.md` § 4.1, which classifies the
directory REPRODUCES overall and names these two siblings as stale.

Superseded by a rebuild of the same two thresholds from the full pool
(`run_1` … `run_5`, the pool's complete pass set) with the current
`scripts/merge_passes.py`, which additionally writes a machine-readable
`pass_provenance` block with a `git_blob_hash` per contributing pass file
(added on `main` by commit `ac7d393c7`, "fix(consensus): record and check a
union's pass list") — the mechanism whose absence is why staleness of this kind
was invisible from the artefact. The superseded `voting_summary.json` is
archived beside them: it is eight lines carrying only `total_passes` and
`thresholds`, which is itself the evidence that it predates that mechanism.

The rebuild command was:

```bash
python scripts/merge_passes.py \
    --input-dir outputs/h10/evaluation-v2/pool_160_hp4hn4 \
    --output-dir <temporary directory> \
    --sweep
```

with `consensus_t1.geojson`, `consensus_t2.geojson` and `voting_summary.json`
copied from the temporary directory into place.

## Why `t3`, `t4` and `t5` were deliberately NOT rebuilt

**`consensus_t4.geojson` is read by a registered condition.**
`results/run-conditions.json` registers `h10::greedy-pool-160` with
`"detections": "outputs/h10/evaluation-v2/pool_160_hp4hn4/consensus/consensus_t4.geojson"`,
and that is the only threshold of this pool any registered condition reads
(verified this session across `results/run-conditions.json`,
`results/conditions-manifest.json` and `results/` generally: **no file anywhere
references `consensus_t1.geojson` or `consensus_t2.geojson` of this pool**, which
is why rebuilding those two changes no registered number).

The rebuild reproduces `t3`, `t4` and `t5` at **identical feature counts** (313,
236, 163), so nothing about them is stale in the sense `t1` and `t2` were. But
the retrospective records that the re-derived `t4` differs from the committed one
by a single matched pair **0.444 m** apart — the residual trace of one cluster's
mean centroid shifting — so a rebuild would rewrite the bytes of a registered
condition's detections file for no measurable gain. It was therefore not done,
and whether it should be is put to the Principal Investigator rather than taken
here.

Consequence to read carefully: the installed `voting_summary.json` records the
rebuild's `pass_provenance`, and its `thresholds` block (1,474 / 477 / 313 / 236
/ 163) describes the directory truthfully — but `t3`, `t4` and `t5` on disk are
the **original** build of those same five passes, not the rebuild's output.

## Contents

| file | features | note |
|---|---:|---|
| `consensus_t1.geojson` | 1,454 | superseded; the rebuild gives 1,474 |
| `consensus_t2.geojson` | 474 | superseded; the rebuild gives 477 |
| `voting_summary.json` | — | superseded; `{total_passes, thresholds}` only, no `pass_provenance` |
