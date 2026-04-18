# Post-Run Report — 55-Map Text HIGH Generalisation (Re-run)

**Run name**: `55maps-text-high-generalisation`
**Completed**: 2026-04-18 17:48 UTC
**Host**: sapphire (192.168.1.150)
**Launcher commit**: `01df51c6` (main)
**Launcher version**: `scripts/run_generalisation.py` v1.0.0
**Config**: `configs/run-configs/55maps_text_high_generalisation.yaml`
**Pre-launch audit**: `configs/run-configs/55maps_text_high_generalisation_pre_launch_audit.md`

Companion to the pre-launch audit — records the actual run's cost,
timing, quality, and results for the reproducibility kit and paper
supplement.

This run is a **re-execution** of the 2026-04-10 text HIGH
generalisation under the publishable launcher. The original run
(retrospective config:
`configs/run-configs/55maps_text_generalisation_retrospective.yaml`)
remains intact at `outputs/55maps-generalisation/`; this re-run
closes the documentation gaps that the retrospective report called
out (no cost manifest, no per-map attribution, no cache-hit rate,
no launch manifest). Every API-payload parameter is identical to
the 2026-04-10 run; the only differences are orchestration
(`workers: 60 → 250`) and launcher plumbing.

## Top-line result

### Measured (against student-annotated ground truth)

| Buffer | F1 | 95% CI | Precision | Recall |
|-------:|---:|:------:|---------:|------:|
| 20 m | 0.623 | [0.608, 0.638] | 0.670 | 0.582 |
| 30 m | 0.753 | [0.741, 0.766] | 0.810 | 0.704 |
| 40 m | 0.783 | [0.772, 0.795] | 0.842 | 0.731 |
| **50 m** | **0.788** | **[0.777, 0.800]** | **0.848** | **0.737** |

CIs are from 1,000-iteration tile-level bootstrap at seed 42.

Detections at the configured vote_t=4 / prob_t=0.15 operating point:
**4,143** across 4,770 reference mounds and 8,541 tiles.

### Reproduction of the 2026-04-10 HIGH run

Sanity paired test — this re-run vs the 2026-04-10 HIGH run at 50 m,
10,000 iterations, seed 42:

| Run | F1 @ 50 m | Precision | Recall | TP / FP / FN |
|-----|:---------:|:---------:|:------:|:------------:|
| 2026-04-10 HIGH (old) | 0.790 | 0.858 | 0.732 | 3,490 / 578 / 1,280 |
| 2026-04-19 HIGH (this re-run) | 0.788 | 0.848 | 0.737 | 3,513 / 630 / 1,257 |
| **Δ (re-run − original)** | **−0.0015** | −0.010 | +0.005 | — |
| **p-value** | **0.7455** | — | — | — |

**Reproduction confirmed**: F1 differs by 0.0015 (well inside the
bootstrap CI width of ≈ 0.012), p = 0.75 on the paired permutation
test. Same thinking level, same everything — the only source of
variance is Flex-tier decoding stochasticity at T = 0.7. The old
HIGH's slight edge in precision (0.858 vs 0.848) is offset by this
re-run's slight edge in recall (0.737 vs 0.732); net F1 is
statistically indistinguishable.

### Corrected for annotator incompleteness (50 m buffer)

Dawid-Skene latent-truth model on the shared item set of 5,400
candidates (3,513 matched + 1,257 student-only + 630 VLM-only):

| Method | F1 | Precision | Recall |
|--------|---:|---------:|------:|
| Measured (vs student GT) | 0.788 | 0.848 | 0.737 |
| Simple correction (5 % FN) | 0.807 | 0.893 | 0.737 |
| **Dawid-Skene posterior** | **0.813** | **0.893** | **0.746** |

Δ F1 = **+0.025** after correction — the same magnitude as the
three prior 55-map corrections (text HIGH 2026-04-10: 0.790 → 0.814;
image HIGH: 0.771 → 0.795; text MIN: 0.759 → 0.783). The
correction continues to track the student ground-truth
incompleteness rate independently of pipeline configuration.

D-S assigns an aggregate posterior P(true = 1) = 0.294 to the 630
VLM-only candidates, implying ~185 are real mounds the student
annotators missed. EM converged in 14 iterations.

Per-item ground truth for the 630 VLM-only candidates is obtainable
via the human-review Streamlit app (`scripts/review_candidates.py`)
and will refine the corrected F1 with an identifiable estimator.

Artefacts: `results/55maps-text-high-generalisation/dawid-skene/`
(``dawid-skene-results.md``, ``.json``, ``item-posteriors.csv``).

### Paired comparison vs text MIN (the scientific question)

Purpose of this re-run in the 3-way comparison: close the paired
HIGH-vs-MIN story with a HIGH arm produced under the publishable
launcher (the MIN post-run's paired test used the 2026-04-10
retrospective HIGH geojson — this replaces that with a clean
launcher-produced geojson).

Paired permutation test, 10,000 iterations, seed 42, same tiles,
same ground truth, matched final-detection geojsons filtered at
identical operating points (vote_t = 4, prob_t = 0.15):

| Buffer | HIGH F1 | MIN F1 | Δ (HIGH − MIN) | p-value | Verdict |
|:-----:|:-------:|:-------:|:---------------:|:-------:|:-------:|
| **20 m** | 0.623 | 0.618 | **+0.0047** | **p = 0.465** | **ns** |
| 30 m | 0.753 | 0.727 | +0.0259 | p < 0.0001 | *** |
| 40 m | 0.783 | 0.754 | +0.0291 | p < 0.0001 | *** |
| 50 m | 0.788 | 0.759 | +0.0292 | p < 0.0001 | *** |

**Pattern reproduces the 2026-04-10-HIGH vs 2026-04-18-MIN
comparison exactly**: ns at 20 m (previously p = 0.42, now p = 0.47),
highly significant at 30/40/50 m (previously p < 0.0001 at all,
now p < 0.0001 at all; effect sizes match within 0.002 F1).

**Precision vs recall decomposition at 50 m**:

| | HIGH (re-run) | MIN | Δ |
|---|---:|---:|---:|
| Precision | 0.848 | 0.849 | −0.001 |
| **Recall** | **0.737** | **0.687** | **+0.050** |

Same mechanism as the MIN post-run finding, with a sharper picture
now that this re-run's pipeline-health check exposed the full
stage-by-stage counts:

| Stage | HIGH (this re-run) | MIN | Δ |
|-------|-------------------:|----:|---:|
| Consensus candidates (4-of-5) | 9,131 | 10,131 | **−1,000** |
| Verifier retention rate | 45.4 % | 38.1 % | **+7.3 pp** |
| Verified detections | 4,143 | 3,861 | **+282** |
| TP @ 20 m | 2,775 | 2,667 | +108 |
| TP @ 50 m | 3,513 | 3,276 | +237 |
| FP @ 20 m | 1,368 | 1,194 | **+174** |
| FP @ 50 m | 630 | 585 | +45 |

HIGH's proposer is more *selective* (produces fewer consensus
candidates), but its candidates are higher-quality — the verifier
retains them at a much higher rate. The net-extra 282 verified
detections are approximately-localised real mounds: at 20 m
tolerance most count as FPs (ΔFP = +174), but at 50 m most become
TPs (ΔFP = +45; ΔTP = +237). Spatial localisation per candidate is
unchanged by thinking level (precision is essentially flat at 50 m);
what changes is how many approximately-matched real mounds the
pipeline retains. See working-notes Obs 258 (amended 2026-04-19)
for the generalisable interpretation.

### Side-by-side with the three 55-map runs

All three at K = 5 + PV, paper-headline operating points:

| Metric | Image HIGH | Text HIGH (this re-run) | Text MIN |
|--------|:----------:|:-----------------------:|:--------:|
| Date | 2026-04-18 | 2026-04-19 | 2026-04-18 |
| vote_t | 3 | 4 | 4 |
| F1 @ 20 m | 0.506 | 0.623 | 0.618 |
| F1 @ 50 m | 0.771 | **0.788** | 0.759 |
| F1 @ 50 m (D-S) | 0.795 | 0.813 | 0.783 |
| Precision @ 50 m | 0.780 | 0.848 | 0.849 |
| Recall @ 50 m | 0.763 | 0.737 | 0.687 |
| **Total cost** | **$364.70** | **$69.60** | **$60.79** |
| Thinking tokens | 95.2 M | **115.0 M** | 0 |
| Runtime | ~4 h 55 m | 3 h 21 m | 2 h 6 m |

Notable: the text HIGH re-run consumed **more thinking tokens than
the image HIGH run** (115 M vs 95 M, +20.8 %) for the same number of
API calls. Per-call, text HIGH thinks ~2,690 tokens vs image HIGH's
~2,230 — plausibly because the image modality provides visual
context that reduces abstract reasoning burden, while text-only
forces the model to reason entirely from descriptive cues.

## Cost accounting

**Total: $69.60** (Gemini 3 Flash, Flex tier).

Within the pre-launch budget of ~$75.

### By stage

| Stage | Cost | Share | Wall-clock (API) |
|-------|-----:|------:|-----------------:|
| Proposer (K=5) | $56.86 | 81.7 % | 156.2 min |
| Verifier (N=1) | $12.74 | 18.3 % | 23.0 min |
| Consensus, Extract, Evaluate | $0.00 | 0.0 % | ~22 min (local) |
| **Total** | **$69.60** | 100 % | — |

### Per proposer pass

| Pass | Wall-clock | Cost | Tiles OK | Tiles failed | Thinking tokens |
|----:|-----------:|-----:|---------:|-------------:|----------------:|
| 1 | 31.9 min | $11.42 | 8,516 | 25 | 22.8 M |
| 2 | 30.8 min | $11.36 | 8,499 | 42 | 22.9 M |
| 3 | 32.4 min | $11.31 | 8,503 | 38 | 23.1 M |
| 4 | 30.6 min | $11.33 | 8,513 | 28 | 23.2 M |
| 5 | 30.6 min | $11.44 | 8,514 | 27 | 23.0 M |
| **Sum** | **156.3 min** | **$56.86** | **42,545** | **160 (0.37 %)** | **115.0 M** |

Per-pass cost is uniform to within 1 % — expected, since tile count,
per-tile text payload, and thinking-level ceiling are all constant.
Contrast with the MIN run (uniform cost, 0 thinking) and the image
HIGH run (uniform cost, ~19 M thinking tokens per pass).

### Token breakdown

| Field | Tokens | Share |
|-------|-------:|------:|
| Input (billed) | 80.5 M | 39.2 % |
| Input (cached) | **0** | 0.0 % |
| Output | 9.8 M | 4.8 % |
| Thinking | **115.0 M** | **56.0 %** |
| **Total** | **205.3 M** | 100 % |

**Thinking tokens account for 56 % of all tokens consumed.** At
Flex-tier rates, this is cheap per token (thinking is billed at the
same output rate), but it is the dominant cost driver in absolute
terms: ~$48 of the $57 proposer cost is thinking. Setting
`thinking_level: minimal` would zero this out (as the MIN run
demonstrates at $46.72 proposer cost).

**Cache hit rate: 0.0 %.** Same mechanistic explanation as the MIN
run: the text-only prompt preamble (~393 tokens) is below Gemini
Flash's 1,024-token minimum for context caching.

### Unit costs (key publication figures)

| Metric | Value |
|--------|------:|
| Cost per tile | **$0.00815** |
| Cost per map | **$1.265** |
| Cost per detection | **$0.01681** |
| Cost per reference mound | **$0.01459** |
| Tile count | 8,541 |
| Map count | 55 |
| Reference mound count | 4,770 |
| Final detection count (post vote + prob) | 4,143 |

Text HIGH per-tile cost is **5.2× cheaper than image HIGH** ($0.0081
vs $0.0427) and **14 % more expensive than text MIN** ($0.0081 vs
$0.0071). The text HIGH premium over MIN buys the recall advantage
quantified above; whether that is a good trade depends on whether
the paper's headline buffer is ≤ 20 m (no advantage) or ≥ 30 m
(clearly significant).

## Per-map extrema

### Top 5 by cost

| Map | Tiles | Cost | Candidates |
|-----|------:|-----:|-----------:|
| K-35-063-1 (Granit) | 779 | $1.500 | 329 |
| K-35-063-2 (Chirpan) | 778 | $1.387 | 249 |
| K-35-077-2 | 775 | $1.333 | 213 |
| K-35-050-4 | 778 | $1.331 | 209 |
| K-35-066-1 | 776 | $1.329 | 209 |

### Bottom 5 by cost

| Map | Tiles | Cost | Candidates |
|-----|------:|-----:|-----------:|
| K-35-074-2 | 776 | $1.198 | 115 |
| K-35-066-2 | 711 | $1.192 | 173 |
| K-35-066-4 | 713 | $1.185 | 166 |
| K-35-056-3 | 780 | $1.181 | 99 |
| K-35-074-1 | 779 | $1.165 | 89 |

Cost scales primarily with tile count (711–780) but — unlike the
MIN run, where per-tile cost was uniform — the HIGH re-run shows a
candidate-density effect on cost. Granit (329 candidates) costs
~28 % more than K-35-074-1 (89 candidates) on nearly identical tile
counts. Mechanism: high-candidate tiles trigger longer output and
more thinking per call; at HIGH thinking this variance is visible.
At MIN thinking (0 thinking tokens) this effect disappears.

## Scope

| Field | Value |
|-------|------:|
| Maps processed | 55 |
| Tiles processed | 8,541 (each processed 5 times) |
| Proposer API calls (completed) | 42,545 |
| Proposer API calls (failed) | 160 (0.37 %) |
| Verifier API calls | 9,131 candidates extracted, verified one-pass |
| Reference ground-truth mounds | 4,770 |
| Consensus candidates (4-of-5) | 9,131 (pre-verifier) |
| Final detections (prob ≥ 0.15) | 4,143 |

## Timeline

| Event | UTC | Δ from launch |
|-------|-----|--------------:|
| Launch (pass 1 start) | 2026-04-18 14:27 | 0 |
| Pass 1 complete | 14:58 | +32 min |
| Pass 2 complete | 15:29 | +31 min |
| Pass 3 complete | 16:02 | +32 min |
| Pass 4 complete | 16:32 | +31 min |
| Pass 5 complete | 17:03 | +31 min |
| Consensus complete | 17:19 | +16 min |
| Extract crops complete | 17:20 | +1 min |
| Verifier complete | 17:43 | +23 min |
| Evaluate + cost manifest | 17:48 | +5 min |
| **Run complete** | **17:48** | **3 h 21 min** |

Within the pre-launch 2–3 h estimate (slightly over; MIN's 2 h 6 min
was the reference, and HIGH adds ~50 min across the 5 passes for
thinking-token latency). No operational issues. Failure rate 0.37 %
across 42,705 expected proposer calls — all retried within the
launcher's cleanup loop and accounted for in the per-pass totals.

## Key scientific finding — three-way comparison closed

The text HIGH re-run completes the 3-way generalisation matrix under
the publishable launcher:

1. **Image HIGH (library_plus-hp, 2026-04-18)**: F1 @ 50 m = 0.771
   (D-S 0.795). High-precision, recall-limited. **$364.70.**
2. **Text HIGH (this re-run, 2026-04-19)**: F1 @ 50 m = 0.788
   (D-S 0.813). Best headline F1. **$69.60.**
3. **Text MIN (2026-04-18)**: F1 @ 50 m = 0.759 (D-S 0.783).
   Cheapest; ns vs HIGH at 20 m, but significantly worse at ≥ 30 m.
   **$60.79.**

Five paper-relevant conclusions fall out:

1. **Text HIGH dominates image HIGH at the 55-map scale**: F1 @ 50 m
   of 0.788 vs 0.771 at 1/5 the cost ($69.60 vs $364.70). Text MIN
   at 0.759 is within bootstrap CI of image HIGH's 0.771 — so even
   the cheapest text operating point is roughly on par with image
   HIGH for F1 per dollar terms.

2. **The D-S correction is stable across runs** (+0.024 ± 0.001 F1
   in all four corrections), suggesting the ~5 % student
   false-negative rate from Sobotkova et al. 2023 is the right
   prior.

3. **Paired HIGH-vs-MIN on text reproduces at the re-run level**:
   the thinking-level effect is real and buffer-dependent,
   regardless of which HIGH run you test against.

4. **The re-run itself reproduces the 2026-04-10 result to within
   0.0015 F1** (p = 0.75 on paired test) — evidence that K = 5
   averaging and the Flex-tier's per-call stochasticity combine to
   produce very stable downstream F1 at this scale.

5. **The thinking-level cost is substantial but targeted**:
   115 M thinking tokens (56 % of total tokens) for a +0.029 F1
   gain at 50 m, or +0.030 F1 D-S-corrected. At $0.0081/tile for
   HIGH vs $0.0071/tile for MIN, the 14 % cost premium on text
   buys a clear recall advantage at ≥ 30 m but no advantage at
   the preregistered 20-m primary.

### Practical implication for the paper

- **If the paper's primary generalisation metric is F1 @ 20 m** (the
  preregistered primary per §4.1.1, E47): **MIN is the cost-optimal
  text operating point**. The re-run re-confirms this at p = 0.47.
- **If the paper reports headline F1 at 50 m** (recent convention):
  **HIGH remains optimal**. This re-run provides a cleanly
  launcher-produced HIGH geojson for all downstream analyses.
- **For the 3-way comparison table**, all three runs now have
  matching documentation (YAML, pre-launch audit, post-run report,
  launch_manifest, cost_manifest, per-map attribution). No
  retrospective data-entry gaps remain.

## Artefacts for the paper

Published alongside the paper and tracked in git:

| File | Purpose |
|------|---------|
| `configs/run-configs/55maps_text_high_generalisation.yaml` | Parameter set |
| `configs/run-configs/55maps_text_high_generalisation_pre_launch_audit.md` | Pre-run config audit |
| `configs/run-configs/55maps_text_high_generalisation_post_run_report.md` | This file |
| `outputs/55maps-text-high-generalisation/launch_manifest.json` | Run-time reproducibility metadata |
| `outputs/55maps-text-high-generalisation/cost_manifest.json` | Full cost accounting |
| `outputs/55maps-text-high-generalisation/consensus/consensus-4of5.geojson` | Voted candidates |
| `outputs/55maps-text-high-generalisation/verified/verified_detections.geojson` | Final filtered detections |
| `outputs/55maps-text-high-generalisation/evaluation/evaluation.json` | F1 / P / R at 20/30/40/50 m |
| `results/55maps-text-high-generalisation/dawid-skene/` | D-S corrected metrics |
| `results/55maps-text-high-generalisation/paired-vs-min-20m/` | Paired vs MIN, 20 m buffer |
| `results/55maps-text-high-generalisation/paired-vs-min-30m/` | Paired vs MIN, 30 m buffer |
| `results/55maps-text-high-generalisation/paired-vs-min-40m/` | Paired vs MIN, 40 m buffer |
| `results/55maps-text-high-generalisation/paired-vs-min-50m/` | Paired vs MIN, 50 m buffer |
| `results/55maps-text-high-generalisation/paired-vs-high-2026-04-10-50m/` | Sanity paired test vs 2026-04-10 HIGH |

## Reproducibility

Launch-time git state was clean (sapphire pulled from origin/main
before launch per the plan). `launch_manifest.json` records:

- `git.commit_sha: 01df51c601264180f2a29551e96a3aa4c8fd7361`
- `git.dirty: false`
- `config_file_sha256: 6a3f3c9f3dd1b4ede0cdf5dfb0d17831f9d57ff82f5fe95bd8554575f8f9fb7e`
- `pre_launch_audit.sha256: 66e82fc3452b87e20042cb4f05caba4846ac33750102d885ffcb300b77f9d9e1`
- All six input SHA256s populated (manifest, ground_truth, bounds,
  proposer_config, verifier_config, rasters_dir_listing)

This closes the provenance caveat noted for the text MIN run
(GH issue #5 — that run's `git.commit_sha` pointed to a state behind
the launcher's actual content). A replicator who checks out
`01df51c6` will get the exact launcher, config, and audit that
produced this run.

## Limitations

- **`expected_cost_usd` in launch_manifest = $355.18** (image-
  calibrated estimator, GH issue #1). Actual text HIGH cost was
  $69.60. The discrepancy is a cosmetic artefact of the shared
  estimator; it does not affect the run.
- **Per-tile thinking-cost variance** is observable in the per-map
  extrema (Granit at $1.50, K-35-074-1 at $1.17 on similar tile
  counts). This is a feature of HIGH thinking, not a measurement
  error.
- **Cache hit rate 0.0 %** is structural (text preamble below
  Flash's cache threshold). Cannot be improved without expanding
  the system instruction artificially.
- **Paired permutation test scope** is 55-map only. Generalising
  the HIGH-vs-MIN finding to other text detection tasks requires
  repeating the pairing at other scales — but the MIN post-run
  already reported that the Era 2 matrix (487 tiles) shows the same
  pattern (p = 0.43 at 20 m in the HIGH-vs-MIN PV comparison).

## Follow-up items

- Human review of the 630 VLM-only candidates via
  `scripts/review_candidates.py` would replace the D-S aggregate
  posterior with per-item ground truth. Adds ~185 expected
  reclassifications (P(true) ≥ 0.5 under D-S) to the TP count.
- Observation write-up: record the "text HIGH thinks more than
  image HIGH per call" observation in
  `docs/notes/reflections/working-notes.md` — plausibly evidence
  that visual context offloads reasoning burden.
- Update the paper's 3-way comparison table with this run's
  measured + D-S-corrected figures (replacing the 2026-04-10
  estimated-cost entries).
