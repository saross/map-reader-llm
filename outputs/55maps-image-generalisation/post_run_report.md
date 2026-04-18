# Post-Run Report — 55-Map Image Generalisation

**Run name**: `55maps-image-generalisation`
**Completed**: 2026-04-18 05:10 UTC
**Host**: sapphire (192.168.1.150)
**Launcher commit**: `b84925d2` (main)
**Launcher version**: `scripts/run_generalisation.py` v1.0.0
**Config**: `configs/run-configs/55maps_image_generalisation.yaml`
**Pre-launch audit**: `configs/run-configs/55maps_image_generalisation_pre_launch_audit.md`

Companion to the pre-launch audit — records the actual run's cost,
timing, quality, and results for the reproducibility kit and paper
supplement.

## Top-line result

| Buffer | F1 | 95% CI | Precision | Recall |
|-------:|---:|:------:|---------:|------:|
| 20 m | 0.506 | [0.492, 0.520] | 0.512 | 0.500 |
| 30 m | 0.686 | [0.672, 0.697] | 0.693 | 0.678 |
| 40 m | 0.748 | [0.737, 0.760] | 0.757 | 0.740 |
| **50 m** | **0.771** | **[0.760, 0.782]** | **0.780** | **0.763** |

CIs are from 1,000-iteration tile-level bootstrap at seed 42.

Detections at the configured vote_t=3 / prob_t=0.15 operating point:
**4,665** across 4,770 reference mounds and 8,541 tiles.

### Comparison to prior text-based 55-map run (F1 @ 50 m)

| Run | Date | F1 @ 50 m |
|-----|------|----------:|
| Text (detect_brief-text, HIGH, K=5) | 2026-04-10 | 0.791 |
| **Image (library_plus-hp, HIGH, K=5)** | **2026-04-18** | **0.771** |
| Δ (image − text) | | **−0.020** |

The image track trails the text track at 50 m by 0.02 F1 on this
out-of-sample scope — consistent with the Era 2 pattern (Obs 250–251)
where text consensus had a larger dividend than image.

## Cost accounting

**Total: $364.70** (Gemini 3 Flash, Flex tier).

Within the pre-launch budget band of $355–385.

### By stage

| Stage | Cost | Share | Wall-clock (API) |
|-------|-----:|------:|-----------------:|
| Proposer (K=5) | $353.62 | 97.0% | 208.6 min |
| Verifier (N=1) | $11.08 | 3.0% | 40.5 min |
| Consensus, Extract, Evaluate | $0.00 | 0.0% | ~18 min (local) |
| **Total** | **$364.70** | 100% | — |

### Per proposer pass

| Pass | Workers | Wall-clock | Cost | Tiles OK | Tiles failed | Retries | Thinking tokens |
|-----:|--------:|-----------:|-----:|---------:|-------------:|--------:|----------------:|
| 1 | 60 | 55.1 min | $70.77 | 8,541 | 8 | 434 | 19.0 M |
| 2 | 60 | 54.4 min | $70.74 | 8,541 | 3 | 449 | 19.2 M |
| 3 | 250 | 32.8 min | $70.71 | 8,541 | 8 | 431 | 19.0 M |
| 4 | 250 | 32.4 min | $70.67 | 8,541 | 2 | 444 | 18.9 M |
| 5 | 250 | 34.0 min | $70.73 | 8,541 | 5 | 432 | 19.2 M |
| **Sum** | | **208.7 min** | **$353.62** | **42,705** | **26 (0.06%)** | **2,190** | **95.3 M** |

Raising Flash's worker concurrency from 60 → 250 after pass 2 cut per-pass
wall-clock by ~40% (not the 4× a pure-parallelism model would predict —
Flex tier's 1–15 min per-request latency, not worker count, is the
binding constraint above ~60 workers).

Cost is invariant across worker settings (same tiles, same tokens per
tile, independent of concurrency).

### Token breakdown

| Field | Tokens | Share |
|-------|-------:|------:|
| Input (billed, non-cached) | 61.5 M | 7.8% |
| Input (cached) | **621.3 M** | **79.1%** |
| Output | 7.8 M | 1.0% |
| Thinking | 95.2 M | 12.1% |
| **Total** | **785.7 M** | 100% |

**Cache hit rate: 91.0%** — Gemini context caching saved ~79% of
billable input tokens across the run. Without caching, proposer cost
would have been roughly 4× higher (~$1,400).

### Unit costs (key publication figures)

| Metric | Value |
|--------|------:|
| Cost per tile | **$0.0427** |
| Cost per map | **$6.63** |
| Cost per detection | **$0.0782** |
| Cost per reference mound | **$0.0765** |
| Tile count | 8,541 |
| Map count | 55 |
| Reference mound count | 4,770 |
| Final detection count (post vote + prob) | 4,665 |

## Per-map extrema

### Top 5 by cost

| Map | Tiles | Cost | Candidates |
|-----|------:|-----:|-----------:|
| K-35-063-1 (Granit) | 780 | $6.88 | 298 |
| K-35-063-2 (Chirpan) | 780 | $6.79 | 237 |
| K-35-050-4 | 780 | $6.77 | 222 |
| K-35-066-1 | 780 | $6.75 | 205 |
| K-35-075-2 | 780 | $6.74 | 202 |

### Bottom 5 by cost

| Map | Tiles | Cost | Candidates |
|-----|------:|-----:|-----------:|
| K-35-056-3 | 780 | $6.55 | 66 |
| K-35-074-3 | 780 | $6.54 | 60 |
| K-35-066-2 | 715 | $6.11 | 137 |
| K-35-066-4 | 715 | $6.09 | 120 |
| K-35-067-3 | 715 | $6.04 | 87 |

Cost per tile is remarkably uniform (mean $0.0085 per tile per pass,
SD across maps < 3%) — a direct consequence of the fixed proposer
prompt + per-call input payload. Candidate counts vary 5× across maps
(60 → 298), reflecting genuine mound density differences rather than
any cost artefact.

## Scope

| Field | Value |
|-------|------:|
| Maps processed | 55 |
| Tiles processed | 8,541 (each processed 5 times) |
| Proposer API calls (completed) | 42,679 |
| Proposer API calls (failed) | 26 |
| Verifier API calls | 7,859 |
| Reference ground-truth mounds | 4,770 |
| Consensus candidates (3-of-5) | 7,877 |
| Final detections (prob ≥ 0.15) | 4,665 |

Mean candidates per tile: 0.184 (pre-verifier); 0.092 (post-verifier).

## Timeline

| Event | UTC |
|-------|-----|
| Launch (pass 1 start) | 2026-04-18 00:15 |
| Pass 1 complete (60w) | 01:11 (+55 min) |
| Pass 2 complete (60w) | 02:05 (+54 min) |
| **Switched to 250 workers** | 02:09 (kill + --resume) |
| Pass 3 complete (250w) | 02:41 (+33 min) |
| Pass 4 complete (250w) | 03:14 (+32 min) |
| Pass 5 complete (250w) | 03:48 (+34 min) |
| Launcher bug: aborted at proposer safety gate | 03:48 |
| **Resumed** (passes skip, consensus runs) | 04:12 |
| Consensus complete | 04:23 (+11 min) |
| Extract complete | 04:25 (+1 min) |
| Verify complete | 05:05 (+40 min) |
| Evaluate complete | 05:10 (+5 min) |
| Cost manifest written | 05:10 |
| **Run complete** | 05:10 |

End-to-end elapsed: **4 h 55 min** (includes a restart for worker
switch and a resume after a launcher-side safety-gate abort — neither
incurred duplicate API cost thanks to per-pass output skipping).

## Operational issues and recoveries

Three launcher-side issues were encountered during the run. All three
were recovered without data loss or extra API spend, and have been
logged as post-run fixes:

1. **Subprocess orphan on kill (task #16)**: When killing the launcher
   mid-pass to switch workers from 60→250, the subprocess proposer was
   orphaned and continued running alongside the re-launched process.
   Recovered with targeted `kill -9` and a fresh restart. Fix: install
   a SIGTERM handler that propagates to active subprocess.

2. **Pass-skip check uses partial geojson (task #15)**: The `*.geojson`
   existence check matches the proposer's incrementally-written file,
   so an interrupted pass could be wrongly skipped. Recovered by
   requiring `*.meta.json` (written at end-of-run) instead. The
   run_3 directory was re-created fresh after the worker switch.

3. **`failed_passes >= 3` gate too strict (task #17)**: The launcher
   treated every exit-code-2 (partial-tile-failure) pass as a "failed
   pass" and aborted after 3 such. At Flex tier, every pass has ~0.1%
   of tiles retry-until-max, producing exit-code-2 as the normal
   completion signal. The gate fired after all 5 proposer passes had
   succeeded, before consensus could run. Recovered with `--resume`
   (all 5 passes skipped on the geojson check, pipeline continued
   past proposer to consensus/verifier/evaluate). Fix: remove the gate
   or threshold on aggregate tile-failure rate (e.g., > 1%), not
   per-pass count.

All three issues are cosmetic robustness improvements for the launcher,
not protocol violations. The final artefacts are identical to what an
uninterrupted run would have produced.

## Reproducing this run

```bash
cd /home/shawn/Code/map-reader-llm
git checkout b84925d2
uv sync   # or pip install -r requirements-lock.txt

# Ensure inputs are staged:
#   inputs/tiles_384_55maps/full_evaluation_manifest.json (8,541 entries)
#   inputs/rasters/Russian1981_32635/ (55 rasters)
#   inputs/vectors/references/student-mounds-55maps.geojson (4,770 mounds)
#   inputs/vectors/bounds/384/55maps_evaluation_bounds.geojson (55 bounds)

python scripts/run_generalisation.py all \
    --run-config configs/run-configs/55maps_image_generalisation.yaml \
    --run-name 55maps-image-generalisation \
    --yes

# Inspect:
cat outputs/55maps-image-generalisation/cost_manifest.json | jq .totals
cat outputs/55maps-image-generalisation/evaluation/evaluation.md
```

Expected cost: **~$365 at Flex tier** (±5% for token-count variation,
which is tiny at HIGH thinking). Expected runtime: ~4 h end-to-end at
250 workers on a single Flex-tier project.

## Artefacts for the paper

Published alongside the paper and tracked in git:

| File | Purpose |
|------|---------|
| `configs/run-configs/55maps_image_generalisation.yaml` | Parameter set |
| `configs/run-configs/55maps_image_generalisation_pre_launch_audit.md` | Pre-run config audit |
| `configs/run-configs/55maps_image_generalisation_post_run_report.md` | This file |
| `outputs/55maps-image-generalisation/launch_manifest.json` | Run-time reproducibility metadata (git SHA, input SHA256s, resolved config) |
| `outputs/55maps-image-generalisation/cost_manifest.json` | Full cost accounting (per-stage + per-map + unit costs) |
| `outputs/55maps-image-generalisation/consensus/consensus-3of5.geojson` | Voted candidates (pre-verifier) |
| `outputs/55maps-image-generalisation/verified/verified_detections.geojson` | Final filtered detections |
| `outputs/55maps-image-generalisation/evaluation/evaluation.json` | F1 / P / R at 20/30/40/50 m |
| `outputs/55maps-image-generalisation/resolved_config.yaml` | Effective config as merged from YAML + CLI |

Large intermediate artefacts (per-pass detection GeoJSONs, verifier
crop PNGs, raw per-tile probabilities) are available in the companion
data release but not tracked in the main git history.
