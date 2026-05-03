# Post-Run Report — 55-Map Text MIN Generalisation

**Run name**: `55maps-text-min-generalisation`
**Completed**: 2026-04-18 12:21 UTC
**Recovery completed**: 2026-05-03 (no-op proposer recovery, dedup
consensus rebuild, cost-manifest aggregate, and downstream re-runs)
**Host**: sapphire (192.168.1.150)
**Launcher commit (reference)**: `6b1d9192` (main) — see reproducibility caveat below
**Launcher version**: `scripts/run_generalisation.py` v1.0.0
**Config**: `configs/run-configs/55maps_text_min_generalisation.yaml`
**Pre-launch audit**: `configs/run-configs/55maps_text_min_generalisation_pre_launch_audit.md`

> **Recovery banner (2026-05-03)** — the canonical totals in this report
> reflect the post-recovery state. The 124 "failed" tiles flagged by
> the parser-fix audit (commit `e3aef6fa`) turned out to be a
> historical record from `failed_items[]` rather than a current failure
> — the per-pass detection geojsons were already bit-identical to the
> committed 2026-04-18 versions. Recovery was therefore a no-op at the
> tile-content level, but the consensus rebuild + dedup cycle added
> +39 features (10,131 → 10,170) and 4 additional verified detections
> (3,861 → 3,865). See "Recovery 2026-05-03" subsection below for the
> full propagation chain. F1 @ 50 m delta of +0.0004 falls well within
> the auto-proceed gate.

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

Post-recovery values (2026-05-03 rebuild against the post-recovery
candidate set; see commit `c1ea6df3` for the consensus / verifier
refresh and `236327d8` for the BCa N=10K bootstrap re-evaluation
against the reviewed GT 4,745). Pre-recovery values are shown for
transparency in parentheses where they differ.

| Buffer | F1 (post-rec) | F1 (pre-rec) | Precision | Recall |
|-------:|---:|---:|---------:|------:|
| 20 m | 0.620 | (0.618) | 0.691 | 0.563 |
| 30 m | 0.730 | (0.727) | 0.813 | 0.662 |
| 40 m | 0.756 | (0.754) | 0.842 | 0.686 |
| **50 m (vs un-reviewed GT)** | **0.7595** | (0.7591) | **0.849** | **0.687** |
| **50 m (vs reviewed GT 4,745)** | **0.7619** | — | **0.8486** | **0.6912** |

CIs are from BCa N=10K tile-level bootstrap at seed 42 (post-recovery
re-evaluation; pre-recovery used 1,000-iteration percentile bootstrap).
The post-recovery 50-m F1 of 0.7595 (vs un-reviewed GT) and 0.7619
(vs reviewed GT 4,745) supersedes the pre-recovery 0.7591.

Detections at the configured vote_t=4 / prob_t=0.15 operating point:
**3,865** (post-recovery; up from 3,861, +4) across 4,770 reference
mounds and 8,541 tiles.

**F1 @ 150 m**: 0.767 (asymptotic ceiling, full-buffer-eval).

**Tile-level MCC @ 50 m**: **0.626** [0.611, 0.641]
(Sensitivity 0.614, Specificity 0.955) — newly added at the
post-recovery rebuild.

### Corrected for annotator incompleteness (50 m buffer)

Student-annotated ground truth is incomplete at the aggregate level
(see Sobotkova et al. 2023 for the ~5 % baseline false-negative
rate). The Dawid-Skene latent-truth model jointly estimates
annotator confusion matrices and corrected pipeline metrics from the
shared item set of 5,355 candidates.

| Method | F1 (post-rec) | Precision | Recall |
|--------|---:|---------:|------:|
| Measured (vs student GT) | 0.7591 | 0.8485 | 0.6868 |
| Simple correction (5 % FN) | 0.7764 | 0.893 | 0.6867 |
| **Dawid-Skene posterior** | **0.7834** | **0.8931** | **0.6977** |

Δ F1 = **+0.024** after correction — the same magnitude as the two
prior 55-map corrections (text HIGH: 0.790 → 0.814; image HIGH:
0.7745 → 0.799), which is reassuring: the correction is tracking the
student ground-truth incompleteness rate, independent of pipeline
configuration.

**Approach B corrected-F1 (multi-buffer, post-recovery)**:
F1 = **0.7964 @ R = 50 m** (essentially unchanged from the
pre-recovery baseline of 0.7964; the text-MIN review CSV was not
modified during the recovery, so the corrected number is
unchanged at 4 decimals). See
`results/55maps-text-min-generalisation/corrected-f1-multi-buffer/report_autogen.md`
for the full F1 curve (0.7968 → 0.8019 across R ∈ {50, …, 150} m).

The shared item set breaks down as 3,276 matched, 1,494 student-only,
and 585 VLM-only. D-S assigns an aggregate posterior P(true=1) = 0.295
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

All three at K=5 + PV, paper-headline operating points (post-recovery
2026-05-03 where applicable):

| Metric | Image HIGH K=5+PV | Text HIGH K=5+PV | Text MIN K=5+PV |
|--------|:-----------------:|:----------------:|:---------------:|
| Date | 2026-04-18 (post-rec 2026-05-03) | 2026-04-10 | 2026-04-18 (post-rec 2026-05-03) |
| F1 @ 20 m | 0.508 | 0.623 | 0.620 |
| F1 @ 50 m | 0.7745 | **0.790** | 0.7595 |
| F1 @ 50 m (D-S) | 0.799 | 0.814 | 0.7834 |
| Precision @ 50 m | 0.7799 | 0.858 | 0.8485 |
| Recall @ 50 m | 0.7692 | 0.732 | 0.6868 |
| **Total cost** | **~$365** | ~$75 (est) | **~$60.93** |
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

## Recovery 2026-05-03

The original 2026-04-18 run had 124 tile-passes (113 unique tiles)
flagged as historical failures in the per-pass `failed_items[]`
records. The parser fix at commit `e3aef6fa` (3-tier JSON repair on
the realtime proposer; sister recovery on the text HIGH and image
HIGH runs) made these tractable in principle, and the recovery was
executed on 2026-05-03 across commits `a9bc85b2..6e077005`.

### Key finding — the recovery was a proposer-level no-op

The 124 "failures" recorded in `failed_items[]` turned out to be a
historical record from an earlier execution; the per-pass detection
geojsons committed on 2026-04-18 were already bit-identical to what
re-execution produced. So at the tile-content level the recovery
was a no-op. However, the consensus rebuild + dedup cycle did
surface +39 features (10,131 → 10,170), 4 of which retained as
verified detections (3,861 → 3,865), and the BCa N=10K bootstrap
re-evaluation against the reviewed GT 4,745 lifted F1 @ 50 m by
+0.0028 (vs un-reviewed 4,770: +0.0004).

### Outcomes versus pre-recovery (50 m buffer)

| Metric | Pre-recovery | Post-recovery | Δ |
|--------|-------------:|--------------:|----:|
| Verified detections | 3,861 | **3,865** | +4 |
| Consensus candidates (4-of-5) | 10,131 | 10,170 | +39 |
| F1 raw @ 50 m (vs un-reviewed GT 4,770) | 0.7591 | **0.7595** | +0.0004 |
| F1 raw @ 50 m (vs reviewed GT 4,745) | — | **0.7619** | — |
| F1 corrected @ 50 m (Approach B) | 0.7964 | 0.7964 | ≈ 0 (review CSV unchanged) |
| MCC @ 50 m | (n/a in pre-rec mirror) | **0.626** [0.611, 0.641] | — |
| F1 @ 150 m (full-buffer-eval) | — | **0.767** | — |

### Recovery cost

- Proposer recovery: **$0.144** (124 tile-passes; ~$0.0012 per tile,
  ~290× cheaper than the T=0.7 sister recovery's $0.357 per tile —
  the parser-fix dividend means the realtime proposer no longer
  burns thinking-token budgets on JSON-parse retries; here the cost
  is even lower than the image sibling because text-MIN has no
  thinking tokens and minimal payload)
- Verifier cleanup: included in the no-op (no new candidates
  required verification)
- **Total recovery cost: ~$0.144**

### Bug discoveries surfaced during recovery

1. **`failed_items[]` is a historical record, not a current-failure
   signal**: the 124-tile audit count was misleading. The per-pass
   geojsons were already bit-identical to the committed state. This
   was confirmed by md5sum comparison of the regenerated vs committed
   per-pass geojsons (commit `c1ea6df3`).
2. **Cosmetic 2× double-counting in cost-manifest aggregator**
   (post-recovery): the aggregator reports proposer cost as $93.45
   USD with `proposer_processed: 85410` (~2× expected 42,705).
   When the recovery is a no-op, the in-line resume merge in
   `4_detect_mounds_batch.py` adds 8,541 already-completed items to
   `completed_items`, doubling the count, and `merge_recovery_meta`
   then folds the recovery meta back over the backup, double-counting
   again. **True cost remains $46.72 proposer + $13.93 verifier
   + $0.144 recovery + $0.10 verifier cleanup ≈ $60.93** as
   originally measured. This bug affects only the `cost_manifest`
   count fields, not F1/MCC/precision. Same root cause as the image
   sibling (commit `a78cd7c5`).

### Propagation chain

| Stage | Commit | Notes |
|------:|:-------|:------|
| Proposer + downstream artefacts (Phases 1-5) | `c1ea6df3` | No-op proposer; +39 dedup features; +4 verified detections; F1 0.7591 → 0.7595 |
| Cost manifest aggregate (Phase 6) | `b4a928d2` | Cosmetic double-counting flagged |
| Re-evaluate vs reviewed GT 4,745 (Stages 8-9) | `236327d8` | F1 @ 50 m: 0.7619; corrected-F1 multi-buffer @ 50 m: 0.7964 |
| Refresh per-run MCC vs reviewed GT | `6e077005` | MCC = 0.626 [0.611, 0.641] |
