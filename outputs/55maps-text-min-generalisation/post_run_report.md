# Post-Run Report — 55-Map Text MIN Generalisation

**Run name**: `55maps-text-min-generalisation`
**Completed**: 2026-04-18 12:21 UTC
**Host**: sapphire (192.168.1.150)
**Launcher commit (reference)**: `6b1d9192` (main) — see reproducibility caveat below
**Launcher version**: `scripts/run_generalisation.py` v1.0.0
**Config**: `configs/run-configs/55maps_text_min_generalisation.yaml`
**Pre-launch audit**: `configs/run-configs/55maps_text_min_generalisation_pre_launch_audit.md`

Companion to the pre-launch audit — records the actual run's cost,
timing, quality, and results for the reproducibility kit and paper
supplement.

This run is a **paired comparison** against the 2026-04-10 text
HIGH generalisation run (retrospective config:
`configs/run-configs/55maps_text_generalisation_retrospective.yaml`).
The two runs differ in exactly one payload parameter:
`thinking_level: high → minimal`. Every other parameter affecting
the API payload (config, K, vote_threshold, verifier, prob_threshold,
buffers, bootstrap, seed) is held constant, so the paired permutation
test below cleanly measures the thinking-level effect.

## Top-line result

### Measured (against student-annotated ground truth)

| Buffer | F1 | 95% CI | Precision | Recall |
|-------:|---:|:------:|---------:|------:|
| 20 m | 0.618 | [0.602, 0.634] | 0.691 | 0.559 |
| 30 m | 0.727 | [0.714, 0.740] | 0.813 | 0.658 |
| 40 m | 0.754 | [0.742, 0.766] | 0.843 | 0.682 |
| **50 m** | **0.759** | **[0.747, 0.771]** | **0.849** | **0.687** |

CIs are from 1,000-iteration tile-level bootstrap at seed 42.

Detections at the configured vote_t=4 / prob_t=0.15 operating point:
**3,861** across 4,770 reference mounds and 8,541 tiles.

### Corrected for annotator incompleteness (50 m buffer)

Student-annotated ground truth is incomplete at the aggregate level
(see Sobotkova et al. 2023 for the ~5 % baseline false-negative
rate). The Dawid-Skene latent-truth model jointly estimates
annotator confusion matrices and corrected pipeline metrics from the
shared item set of 5,355 candidates.

| Method | F1 | Precision | Recall |
|--------|---:|---------:|------:|
| Measured (vs student GT) | 0.759 | 0.849 | 0.687 |
| Simple correction (5 % FN) | 0.776 | 0.893 | 0.687 |
| **Dawid-Skene posterior** | **0.783** | **0.893** | **0.698** |

Δ F1 = **+0.024** after correction — the same magnitude as the two
prior 55-map corrections (text HIGH: 0.790 → 0.814; image HIGH:
0.771 → 0.795), which is reassuring: the correction is tracking the
student ground-truth incompleteness rate, independent of pipeline
configuration.

The shared item set breaks down as 3,276 matched + 1,494 student-only
+ 585 VLM-only. D-S assigns an aggregate posterior P(true=1) = 0.295
to the VLM-only set, implying ~172 of those 585 are real mounds that
student annotators missed. EM converged in 14 iterations.

Per-item ground truth for the 585 VLM-only candidates is obtainable
via the human-review Streamlit app (`scripts/review_candidates.py`)
and will refine the corrected F1 with an identifiable estimator.

Artefacts: `results/55maps-text-min-generalisation/dawid-skene/`
(``dawid-skene-results.md``, ``.json``, ``item-posteriors.csv``).

### Paired comparison vs text HIGH (the scientific question)

Purpose of this run: test whether HIGH thinking's ~$14 cost premium
on the text pipeline is statistically justified at K=5 + PV.

**Result: depends entirely on which buffer you care about.**

Paired permutation test (10,000 iterations, seed 42, same tiles,
same ground truth, matched final-detection geojsons filtered at
identical operating points):

| Buffer | HIGH F1 | MIN F1 | Δ (HIGH − MIN) | p-value | Verdict |
|:-----:|:-------:|:-------:|:---------------:|:-------:|:-------:|
| **20 m** | 0.623 | 0.618 | **+0.0052** | **p = 0.42** | **ns** |
| 30 m | 0.755 | 0.727 | +0.0278 | p < 0.0001 | *** |
| 40 m | 0.783 | 0.754 | +0.0294 | p < 0.0001 | *** |
| 50 m | 0.790 | 0.759 | +0.0306 | p < 0.0001 | *** |

At 20 m the two thinking levels are statistically indistinguishable;
at every looser buffer HIGH wins significantly.

**Precision vs recall decomposition** (50 m):

| | HIGH | MIN | Δ |
|---|---:|---:|---:|
| Precision | 0.858 | 0.849 | −0.009 |
| **Recall** | **0.732** | **0.687** | **−0.045** |

HIGH's F1 premium is entirely driven by recall. Precision is
essentially unchanged. Interpretation *(refined 2026-04-19 after
the HIGH re-run pipeline-health check — see working-notes Obs 258
amendment)*: HIGH thinking produces *fewer* consensus candidates
than MIN (9,131 vs 10,131 on the re-run), but higher per-candidate
quality. The verifier retains HIGH's candidates at a much higher
rate (~45 % vs ~38 %), and the resulting extra verified detections
are *approximately-localised* real mounds — they count as TPs at
loose buffers (30–50 m) but not at the tight 20 m primary. So the
thinking-level effect is in candidate *quality and retention*, not
in spatial *localisation*.

**Applying the project's ≥10 % cheaper + statistically indistinguishable
heuristic:**

- Cost saving HIGH → MIN on text: **−19 %** ($75 → $60.79). Passes the
  10 % threshold.
- Statistical indistinguishability: **Yes at 20 m** (preregistered
  primary), **No at ≥30 m**.

### Side-by-side with the two other 55-map runs

All three at K=5 + PV, paper-headline operating points:

| Metric | Image HIGH K=5+PV | Text HIGH K=5+PV | Text MIN K=5+PV |
|--------|:-----------------:|:----------------:|:---------------:|
| Date | 2026-04-18 | 2026-04-10 | 2026-04-18 |
| F1 @ 20 m | 0.506 | 0.623 | 0.618 |
| F1 @ 50 m | 0.771 | **0.790** | 0.759 |
| F1 @ 50 m (D-S) | 0.795 | 0.814 | 0.783 |
| Precision @ 50 m | 0.780 | 0.858 | 0.849 |
| Recall @ 50 m | 0.763 | 0.732 | 0.687 |
| **Total cost** | **$364.70** | ~$75 (est) | **$60.79** |
| Thinking tokens | 95.2 M | (not tracked) | **0** |

## Cost accounting

**Total: $60.79** (Gemini 3 Flash, Flex tier).

Below the pre-launch budget band of $65–80.

### By stage

| Stage | Cost | Share | Wall-clock (API) |
|-------|-----:|------:|-----------------:|
| Proposer (K=5) | $46.72 | 76.9 % | 87.6 min |
| Verifier (N=1) | $14.06 | 23.1 % | 28.3 min |
| Consensus, Extract, Evaluate | $0.00 | 0.0 % | ~15 min (local) |
| **Total** | **$60.79** | 100 % | — |

### Per proposer pass

| Pass | Wall-clock | Cost | Tiles OK | Tiles failed | Retries | Thinking |
|----:|-----------:|-----:|---------:|-------------:|--------:|---------:|
| 1 | 15.9 min | $9.34 | 8,541 | 22 | 11 | **0** |
| 2 | 24.9 min | $9.35 | 8,541 | 25 | 6 | **0** |
| 3 | 16.1 min | $9.36 | 8,541 | 32 | 18 | **0** |
| 4 | 15.8 min | $9.33 | 8,541 | 26 | 0 | **0** |
| 5 | 15.8 min | $9.35 | 8,541 | 19 | 26 | **0** |
| **Sum** | **88.5 min** | **$46.72** | **42,705** | **124 (0.29 %)** | **61** | **0** |

Per-pass cost is uniform to within 0.3 % — expected, since tile
count and per-tile text payload are constant. Pass 2 is the odd one
out at 24.9 min (vs ~16 min for the rest) — random Flex-tier
latency variation; no impact on cost or content.

### Token breakdown

| Field | Tokens | Share |
|-------|-------:|------:|
| Input (billed) | 82.3 M | 92.6 % |
| Input (cached) | **0** | 0.0 % |
| Output | 6.5 M | 7.4 % |
| Thinking | **0** | 0.0 % |
| **Total** | **88.8 M** | 100 % |

**Cache hit rate: 0.0 %.** The text-only prompt preamble (system
instruction + 17 text-described examples) totals ~393 tokens, below
Gemini Flash's 1,024-token minimum for context caching. Caching is
a no-op on text-only pipelines at this scale — this is the
mechanistic explanation for why text runs are so much cheaper than
image runs per tile: image runs cache ~15 K tokens of example images
and amortise, while text runs simply send a smaller payload on every
call.

Contrast with the image HIGH run on the same scope: 91.0 % cache hit
rate on a ~620 M cached-tokens base. The fact that text MIN still
costs 6× less per tile than image HIGH — even without caching —
tells you how much of the image-run cost is the example-image
payload (which caching amortises but does not eliminate).

### Unit costs (key publication figures)

| Metric | Value |
|--------|------:|
| Cost per tile | **$0.00712** |
| Cost per map | **$1.105** |
| Cost per detection | **$0.01574** |
| Cost per reference mound | **$0.01274** |
| Tile count | 8,541 |
| Map count | 55 |
| Reference mound count | 4,770 |
| Final detection count (post vote + prob) | 3,861 |

The text MIN per-tile cost is **6× cheaper than image HIGH**
($0.0071 vs $0.0427). Scaling implications for future work:
per-tile text is cheap enough that mound-density surveys on new
regions are feasible at single-digit-dollar per map.

## Per-map extrema

### Top 5 by cost

| Map | Tiles | Cost | Candidates |
|-----|------:|-----:|-----------:|
| K-35-063-1 (Granit) | 780 | $1.245 | (see cost_manifest) |
| K-35-063-2 (Chirpan) | 780 | $1.225 | |
| K-35-050-4 | 780 | $1.220 | |
| K-35-075-2 | 780 | $1.213 | |
| K-35-064-3 (Nova Zagora) | 780 | $1.212 | |

### Bottom 5 by cost

| Map | Tiles | Cost |
|-----|------:|-----:|
| K-35-066-2 | 715 | $1.014 |
| K-35-067-3 | 715 | $1.018 |
| K-35-066-4 | 715 | $1.019 |
| K-35-067-4 | 715 | $1.026 |
| K-35-066-1 | 715 | $1.027 |

Cost scales directly with tile count (715 vs 780). No
text-processing-density effect on cost — text payload is uniform
per tile regardless of map content. (Contrast with image HIGH: same
uniformity, because image payload is also uniform per tile.)

## Scope

| Field | Value |
|-------|------:|
| Maps processed | 55 |
| Tiles processed | 8,541 (each processed 5 times) |
| Proposer API calls (completed) | 42,581 |
| Proposer API calls (failed) | 124 |
| Verifier API calls | 4,947 (shared item set: 5,355 — verifier has some cached cohesion across retries) |
| Reference ground-truth mounds | 4,770 |
| Consensus candidates (4-of-5) | ~4,300 (pre-verifier) |
| Final detections (prob ≥ 0.15) | 3,861 |

## Timeline

| Event | UTC |
|-------|-----|
| Launch (pass 1 start) | 2026-04-18 10:15 |
| Pass 1 complete | 10:31 (+16 min) |
| Pass 2 complete | 10:56 (+25 min — Flex latency variance) |
| Pass 3 complete | 11:12 (+16 min) |
| Pass 4 complete | 11:28 (+16 min) |
| Pass 5 complete | 11:43 (+16 min) |
| Consensus complete | 11:47 (+4 min) |
| Extract complete | 11:49 (+1 min) |
| Verifier complete | 12:20 (+31 min) |
| Evaluate complete | 12:21 (+1 min) |
| Cost manifest written | 12:21 |
| **Run complete** | 12:21 |

End-to-end elapsed: **2 h 6 min**. Under the pre-launch 2–3 h
estimate. Compare to the image HIGH run (~4 h 55 min): text at
250 workers is ~2× faster than image at equivalent workers because
text payloads are smaller and Flex capacity is less saturated.

No operational issues. All three launcher-robustness fixes from the
image run (tasks #15 #16 #17, commit `b80cfc30`) were in effect
and worked correctly — no orphaned subprocesses, no partial-geojson
skip errors, no spurious exit-code-2 aborts despite 124 tile
failures across the 5 proposer passes.

## Key scientific finding — paired HIGH vs MIN

The core question this run was designed to answer:

> **Does HIGH thinking's ~$14 premium on the text pipeline buy a
> statistically distinguishable F1 improvement?**

**Answer: depends entirely on which evaluation buffer you use.**

- At the preregistered primary 20 m buffer: **no** (p = 0.42).
- At looser 30/40/50 m buffers: **yes, highly significantly**
  (p < 0.0001 each; +0.028–0.031 F1).

The split is not an artefact — it reveals a clean mechanism
(refined 2026-04-19 after the HIGH re-run exposed the full
pipeline-health picture; see working-notes Obs 258 amendment):

**HIGH thinking helps approximate-match retention, not spatial
localisation.** The precision/recall decomposition at 50 m shows
HIGH's advantage is entirely recall (+0.045 R, −0.009 P vs MIN).
HIGH's proposer actually produces *fewer* consensus candidates
than MIN's (55-map re-run: 9,131 vs 10,131) but of higher quality:
the verifier retains HIGH's candidates at a substantially higher
rate (~45 % vs ~38 %), yielding more verified detections overall
(4,143 vs 3,861). The net-extra detections are approximately-
localised real mounds — they match ground truth at loose tolerance
but drift out of range at 20 m. So tightening the spatial
tolerance to 20 m collapses HIGH's recall advantage because those
extras lose their matches; the tight-buffer precision gap (HIGH
0.670 vs MIN 0.691) reflects the same dynamic from the other side.

**Practical implication for the paper**:

- If the paper's primary generalisation metric is F1 @ 20 m (the
  preregistered primary per §4.1.1, E47), **MIN is the cost-optimal
  text operating point**: 19 % cheaper, statistically
  indistinguishable, no justification for HIGH's premium.
- If the paper's headline F1 is at 50 m (the reporting convention
  in recent observations), **HIGH retains its advantage** at
  p < 0.0001. The ~$14 saving is not worth a +0.031 F1 loss.
- If the paper reports both buffers, the MIN run provides a clean
  illustrative point about where thinking-level helps vs where
  it is noise.

## Artefacts for the paper

Published alongside the paper and tracked in git:

| File | Purpose |
|------|---------|
| `configs/run-configs/55maps_text_min_generalisation.yaml` | Parameter set |
| `configs/run-configs/55maps_text_min_generalisation_pre_launch_audit.md` | Pre-run config audit |
| `configs/run-configs/55maps_text_min_generalisation_post_run_report.md` | This file |
| `outputs/55maps-text-min-generalisation/launch_manifest.json` | Run-time reproducibility metadata |
| `outputs/55maps-text-min-generalisation/cost_manifest.json` | Full cost accounting |
| `outputs/55maps-text-min-generalisation/consensus/consensus-4of5.geojson` | Voted candidates |
| `outputs/55maps-text-min-generalisation/verified/verified_detections.geojson` | Final filtered detections |
| `outputs/55maps-text-min-generalisation/evaluation/evaluation.json` | F1 / P / R at 20/30/40/50 m |
| `results/55maps-text-min-generalisation/dawid-skene/` | D-S corrected metrics |
| `results/55maps-text-min-generalisation/paired-vs-high-20m/` | Paired permutation test, 20 m buffer |
| `results/55maps-text-min-generalisation/paired-vs-high/` | Paired permutation test, 50 m buffer |

## Reproducibility caveat — launcher provenance

At launch time, sapphire's git HEAD was `b57cf6c2` (4 commits behind
`origin/main`) because sapphire pulls were deferred. The launcher
file `scripts/run_generalisation.py` that actually ran was the
latest published version (commit `b80cfc30` content, rsynced from
amd-tower). `launch_manifest.json` records `git.commit_sha:
b57cf6c2` because that was sapphire's HEAD, not the rsynced file's
provenance.

This is a reproducibility gap: a replicator who checks out
`b57cf6c2` cleanly would get a different (older) launcher than the
one that ran. Mitigations:

1. **For this run's reproducibility**, use
   `configs/run-configs/55maps_text_min_generalisation.yaml` at
   commit `6b1d9192` (which includes the config) against the
   launcher at commit `b80cfc30` or later — both on
   `origin/main`. The `resolved_config.yaml` in the output dir
   documents the exact parameter values used, so replication is
   straightforward even with the git SHA gap.
2. **For future runs**, pull sapphire to `origin/main` before
   launching so the manifest's git SHA reflects the actual code.
3. **For the launcher tooling**, record the launcher script's own
   SHA256 in `launch_manifest.input_sha256` alongside the YAML
   config's SHA256. This is filed as
   [GitHub issue #5](https://github.com/saross/map-reader-llm/issues/5)
   (to be created — see follow-up below).

## Limitations

- **Per-pass thinking token counter is 0 by design** — MIN thinking
  produces no thinking tokens. Not a measurement error.
- **Cache hit rate 0.0 %** is expected (text preamble below Flash's
  1,024-tok cache minimum). Cannot be improved without either
  (a) expanding the system instruction artificially or (b) moving
  to a model with a lower cache threshold.
- **Paired permutation test scope** is 55-map only — it tells us
  MIN ≈ HIGH at 20 m on THIS data; generalising that to all text
  detection tasks requires repeating the pairing at other scales
  (Era 2 data already supports the same conclusion — Phase 3a
  matrix HIGH vs MIN at K=5 + PV shows p = 0.43 on 487 tiles).

## Follow-up items (added to tracker)

- GitHub issue #5 (to create): record launcher SHA256 in launch
  manifest alongside git SHA. Closes the provenance gap noted above.
- Human review of the 585 VLM-only candidates via
  `scripts/review_candidates.py` would replace the D-S aggregate
  posterior with per-item ground truth. Scope is smaller than the
  HIGH run's VLM-only set (585 vs 1,028) — faster to complete.
- Observation write-up: document the HIGH-vs-MIN mechanistic finding
  (thinking helps approximate-match retention, not localisation —
  see working-notes Obs 258 amendment) in
  `docs/notes/reflections/working-notes.md` after the paper section
  using it is drafted.
