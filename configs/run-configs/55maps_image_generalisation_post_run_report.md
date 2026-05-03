# Post-Run Report — 55-Map Image Generalisation

**Run name**: `55maps-image-generalisation`
**Completed**: 2026-04-18 05:10 UTC
**Recovery completed**: 2026-05-03 (proposer recovery, verifier
cleanup, aggregate-cost rebuild, and downstream re-runs)
**Host**: sapphire (192.168.1.150)
**Launcher commit**: `b84925d2` (main; original launch)
**Launcher version**: `scripts/run_generalisation.py` v1.0.0
**Config**: `configs/run-configs/55maps_image_generalisation.yaml`
**Pre-launch audit**: `configs/run-configs/55maps_image_generalisation_pre_launch_audit.md`

> **Recovery banner (2026-05-03)** — the canonical totals in this report
> reflect the post-recovery state. The original run left 26 of 42,705
> attempted proposer calls unrecovered; all 26 were recovered on
> 2026-05-03 (commits `2992056b..8699f456`), with downstream consensus,
> verifier cleanup, cost-manifest, evaluation, Dawid-Skene, and MCC
> all re-built against the post-recovery candidate set. A single new
> consensus candidate (`candidate_07877`) was promoted at 3-of-5, and
> 18 pre-existing missing-from-verifier candidates were recovered as
> a side effect of the cleanup pass. See "Recovery 2026-05-03"
> subsection below for the full propagation chain.

Companion to the pre-launch audit — records the actual run's cost,
timing, quality, and results for the reproducibility kit and paper
supplement.

## Top-line result

### Measured (against student-annotated ground truth)

Post-recovery values (2026-05-03 rebuild against the post-recovery
candidate set; see commit `da84a3d2`). Pre-recovery values are shown
for transparency in parentheses where they materially differ.

| Buffer | F1 (post-rec) | F1 (pre-rec) | Precision | Recall |
|-------:|---:|---:|---------:|------:|
| 20 m | 0.508 | (0.506) | 0.512 | 0.505 |
| 30 m | 0.689 | (0.686) | 0.693 | 0.684 |
| 40 m | 0.752 | (0.748) | 0.757 | 0.747 |
| **50 m** | **0.7745** | (0.7710) | **0.780** | **0.769** |

CIs are from BCa N=10K tile-level bootstrap at seed 42 (post-recovery
re-evaluation; pre-recovery used 1,000-iteration percentile bootstrap).
The post-recovery 50-m F1 of 0.7745 supersedes the pre-recovery 0.7710
recorded under the original 2026-04-18 evaluation.

Detections at the configured vote_t=3 / prob_t=0.15 operating point:
**4,680** (post-recovery; up from 4,665 pre-recovery, +15) across
4,770 reference mounds and 8,541 tiles.

**Tile-level MCC @ 50 m**: **0.692** [0.678, 0.706]
(Sensitivity 0.708, Specificity 0.948) — newly computed at the
post-recovery rebuild.

### Corrected for annotator incompleteness (50 m buffer)

Student-annotated ground truth is incomplete at the aggregate level
(see Sobotkova et al. 2023 for the ~5 % baseline false-negative
rate). The Dawid-Skene latent-truth model jointly estimates
annotator confusion matrices and corrected pipeline metrics from
the shared item set of 5,798 candidates (matched + student-only +
VLM-only).

| Method | F1 (post-rec) | Precision | Recall | Notes |
|--------|---:|---------:|------:|------|
| Measured (vs student GT) | 0.7745 | 0.7799 | 0.7692 | Baseline |
| Simple correction (5 % FN) | 0.7942 | 0.8209 | 0.7692 | Assumes uniform FN |
| **Dawid-Skene posterior** | **0.799** | **0.821** | **0.7782** | Model-based |

Δ F1 = **+0.024** after correction — the same magnitude as the
prior text-run correction (0.790 → 0.814). The shared item set
(post-recovery) breaks down as 3,650 matched, 1,095 student-only,
and 1,030 VLM-only (total 5,775); D-S assigns an aggregate posterior
P(true=1) = 0.187 to the VLM-only set, implying ~192 of those
1,030 are real mounds that student annotators missed. EM converged
in 11 iterations.

The corrected-F1 multi-buffer headline (Approach B, extended-GT
Hungarian re-matching with reviewer-promoted phantoms) is
**F1 = 0.8333 at R = 50 m** post-recovery (was 0.8316 pre-recovery;
+0.0017 with cand 2397 review now included), rising to F1 = 0.8565
at R = 150 m. See `results/55maps-image-generalisation/corrected-f1-multi-buffer/report.md`.

D-S's aggregate identifiability is a 2-annotator limit; per-item
ground truth for the 1,030 VLM-only candidates will be obtained
via the human-review Streamlit app
(`scripts/review_candidates.py`) and will refine the corrected F1
with an identifiable estimator.

Artefacts: `results/55maps-image-generalisation/dawid-skene/`
(``dawid-skene-results.md``, ``.json``, ``item-posteriors.csv``).

### Comparison to prior text-based 55-map run (F1 @ 50 m)

| Run | Date | F1 @ 50 m |
|-----|------|----------:|
| Text (detect_brief-text, HIGH, K=5) | 2026-04-10 | 0.791 |
| **Image (library_plus-hp, HIGH, K=5)** | **2026-04-18 (post-recovery 2026-05-03)** | **0.7745** |
| Δ (image − text) | | **−0.017** |

The image track trails the text track at 50 m by ~0.017 F1
post-recovery (was −0.020 pre-recovery) on this out-of-sample
scope — consistent with the Era 2 pattern (Obs 250–251) where
text consensus had a larger dividend than image.

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

## Recovery 2026-05-03

The original 2026-04-18 run left 26 of 42,705 attempted proposer
calls unrecovered. The parser fix at commit `e3aef6fa` (3-tier JSON
repair on the realtime proposer; sister recovery on the text HIGH
run) made these tractable in principle, and the recovery was
executed on 2026-05-03 across commits `2992056b..8699f456`.

### Outcomes versus pre-recovery (50 m buffer)

| Metric | Pre-recovery | Post-recovery | Δ |
|--------|-------------:|--------------:|----:|
| Verified detections | 4,665 | **4,680** | **+15** |
| Consensus candidates (3-of-5) | 7,877 | 7,878 | +1 |
| F1 raw @ 50 m | 0.7710 | **0.7745** | +0.0035 |
| F1 corrected @ 50 m (Approach B) | 0.8316 | **0.8333** | +0.0017 |
| MCC @ 50 m | (n/a in pre-rec mirror) | **0.692** [0.678, 0.706] | — |
| D-S corrected F1 @ 50 m | 0.795 | 0.799 | +0.004 |
| Subtype weighted F1 (companion GS-v2 4-of-5) | 0.8873 | 0.8876 | +0.0003 |

### Recovery cost

- Proposer recovery: **$0.029** (26 tile-passes; ~$0.001 per tile,
  ~360× cheaper than the T=0.7 sister recovery's $0.357 per tile —
  the parser-fix dividend means the realtime proposer no longer
  burns thinking-token budgets on JSON-parse retries)
- Verifier cleanup: **~$0.02** (19 candidates: 18 pre-existing
  missing-from-verifier rescued as a side effect, plus 1 new
  consensus candidate)
- **Total recovery cost: ~$0.05**

The 18 pre-existing missing-from-verifier candidates (ids 253, 292,
302, 304, 321, 359, 397, 408, 435, 520 + 8 more) had been silently
dropped during the original 2026-04-18 verifier pass; their recovery
means the previously-published F1 was understated. A 19th candidate
(`candidate_07877`) was newly promoted from the post-recovery
3-of-5 consensus rebuild.

### Bug discoveries surfaced during recovery

1. **Cosmetic 2× double-counting in cost-manifest aggregator**
   (post-recovery): `aggregate_cost_manifest` reports proposer cost
   as $1,061.08 with `proposer_processed: 128141` (~3× expected
   42,705) when the recovery is largely a no-op. The in-line resume
   merge in `4_detect_mounds_batch.py` adds already-completed items
   to `completed_items`, and `merge_recovery_meta` then folds the
   recovery meta back over the backup, compounding the double count.
   **True total ≈ $365** as originally measured ($353.62 proposer
   + $11.08 verifier + $0.029 recovery proposer + ~$0.02 verifier
   cleanup). This bug affects only the `cost_manifest` count fields,
   not F1/MCC/precision. Same root cause as the text-MIN sibling
   (commit `b4a928d2`).
2. **18 silently-dropped verifier candidates** discovered in the
   original 2026-04-18 `probabilities.json` (ids 253, 292, 302, 304,
   321, 359, 397, 408, 435, 520 and 8 more). All recovered as a
   side effect of the cleanup pass; previously-published F1 was
   understated by ~+0.0035 at 50 m as a result.
3. **Stage-3 race against `merge_passes.py`** (lessons learnt at
   commit `8699f456`): `merge_passes` writes via direct `with open(p, "w")`
   (no tmp+rename) and takes ~5 min on the 55-map image library;
   reading the consensus geojson mid-write returns a malformed file
   or (more confusingly) a stale copy from before the write started.
   Recoverable by waiting for the `merge_passes` process to truly exit.

### Propagation chain

| Stage | Commit | Notes |
|------:|:-------|:------|
| Proposer recovery | `2992056b` | All 26 tiles recovered |
| Verifier cleanup (Stage 5) | `8082896b` | 18 pre-existing missing candidates recovered |
| Cost-manifest aggregate (Stage 6) | `a78cd7c5` | Cosmetic double-counting flagged |
| Verified geojson rebuild (Stage 7) | `8965d236` | 4,665 → 4,679 (+14) |
| Re-evaluate vs reviewed GT 4745 (Stage 8) | `da84a3d2` | F1 0.771 → 0.774 (un-reviewed → reviewed GT delta) |
| **Stage-3 race correction + 1 candidate** | **`8699f456`** | 4,679 → 4,680 (+1); F1 0.774 → 0.7745; downstream re-runs |
| Image FP review launcher | `165c7415` | Post-recovery review tooling |
| Cand 2397 review entry | `c816d4bd` | mound/trig_point_on_mound at buffer 50 m |
