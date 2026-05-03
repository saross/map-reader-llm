# Post-Run Report — 55-Map Text HIGH Generalisation (Re-run)

**Run name**: `55maps-text-high-generalisation`
**Completed (original)**: 2026-04-18 17:48 UTC
**Recovery completed**: 2026-05-03 (proposer recovery, verifier
cleanup, aggregate-cost rebuild, and downstream re-runs)
**Host**: sapphire (192.168.1.150)
**Launcher commit**: `01df51c6` (main; original launch)
**Launcher version**: `scripts/run_generalisation.py` v1.0.0
**Config**: `configs/run-configs/55maps_text_high_generalisation.yaml`
**Pre-launch audit**: `configs/run-configs/55maps_text_high_generalisation_pre_launch_audit.md`

> **Recovery banner (2026-05-03)** — the canonical totals in this report
> reflect the post-recovery state. The original run left 160 of 42,705
> attempted proposer calls unrecovered (a magnitude correction over the
> Obs 281 pre-audit count of 25; see Obs 318). All 160 were recovered on
> 2026-05-02/03 at commit `731466d8`, with downstream consensus +
> verifier cleanup + cost-manifest + evaluation + Dawid-Skene + corrected-
> F1 + MCC + paired-permutation + attractor-pull all re-built against
> the post-recovery candidate set. See "Recovery 2026-05-02/03"
> subsection below for the full propagation chain.

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

Post-recovery values (2026-05-03 rebuild against the post-recovery
candidate set; see commit `f533fda5` and the "Recovery 2026-05-02/03"
subsection below). Pre-recovery values are shown for transparency in
parentheses.

| Buffer | F1 (post-rec) | F1 (pre-rec) | Precision | Recall |
|-------:|---:|---:|---------:|------:|
| 20 m | 0.626 | (0.624) | 0.670 | 0.588 |
| 30 m | 0.757 | (0.754) | 0.810 | 0.710 |
| 40 m | 0.787 | (0.784) | 0.842 | 0.738 |
| **50 m** | **0.792** | (0.790) | **0.847** | **0.744** |

The post-recovery 50-m F1 of 0.7920 supersedes the pre-recovery 0.7896
recorded under the original 2026-04-18 evaluation. CI bounds at the
new (BCa N=10K) bootstrap are recorded in
`outputs/55maps-text-high-generalisation/evaluation/evaluation.metadata.json`
and the N=10K BCa re-run committed at `e20f3e18`.

Detections at the configured vote_t=4 / prob_t=0.15 operating point:
**4,164** (post-recovery; up from 4,143 pre-recovery, +21) across
4,770 reference mounds and 8,541 tiles.

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

Dawid-Skene latent-truth model, **post-recovery + post-GT-update**
(2026-05-03; see commit `366f9c66` for the re-aggregation against the
updated GT, and commit `a9e280a3` for the row-position bug fix that
landed alongside):

| Method | F1 | Precision | Recall |
|--------|---:|---------:|------:|
| Measured (vs student GT) | 0.7896 | 0.847 | 0.7394 |
| **Dawid-Skene posterior (post-recovery)** | **0.8142** | 0.892 | 0.7492 |
| Dawid-Skene posterior (pre-recovery) | (0.8129) | (0.8916) | (0.7491) |

Δ F1 = **+0.025** after correction — the same magnitude as the
three sister 55-map corrections (image HIGH: 0.771 → 0.795; text MIN:
0.759 → 0.783; T=0.3: see paired-permutation grid). The correction
continues to track the student ground-truth incompleteness rate
independently of pipeline configuration.

The post-recovery total VLM-only candidate set is 637 (up from 630
pre-recovery, +7); D-S aggregate posterior P(true = 1) = 0.291,
implying ~186 are real mounds the student annotators missed.

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

**Total: $126.81** (Gemini 3 Flash, Flex tier; post-recovery aggregate).

This exceeds the original pre-launch budget of ~$75 because of the
$57.10 stage-2 recovery overrun on the 160 stubborn JSON-parse
failures (see "Recovery 2026-05-02/03" subsection below for the
overrun analysis and root-cause attribution).

### By stage (post-recovery aggregate)

| Stage | Cost | Notes |
|-------|-----:|-------|
| Proposer (K=5, original launch) | $56.86 | 2026-04-18 |
| Proposer (recovery 2026-05-02) | $57.10 | 160 failed-tile recovery; cost overrun (planned $0.50 cap; see Obs 319) |
| Verifier (N=1, original launch) | $12.74 | 2026-04-18 |
| Verifier (cleanup, 74 new candidates) | $0.10 | 2026-05-03 |
| FP-classification (T=0.7 share) | $0.01 | T=0.7 portion of $0.5821 cross-corpus run (commit `33435aab`) |
| Consensus, Extract, Evaluate | $0.00 | local CPU |
| **Total** | **$126.81** | per `cost_manifest.json` (`totals.cost_usd`) |

The cost-manifest fix at commit `7f05f529` was needed to surface the
full total: prior to the fix, `aggregate_cost_manifest` read the
post-cleanup `verified/run.meta.json` and silently dropped the
original verifier meta (preserved as `*.pre-recovery-*.backup`). The
patch teaches the script to glob for backup siblings and merge their
costs into the totals, then records the merged backups under
`cost_manifest._metadata.cleanup_recovery_metas_merged`.

### Per proposer pass (original launch, 2026-04-18)

| Pass | Wall-clock | Cost | Tiles OK | Tiles failed | Thinking tokens |
|----:|-----------:|-----:|---------:|-------------:|----------------:|
| 1 | 31.9 min | $11.42 | 8,516 | 25 | 22.8 M |
| 2 | 30.8 min | $11.36 | 8,499 | 42 | 22.9 M |
| 3 | 32.4 min | $11.31 | 8,503 | 38 | 23.1 M |
| 4 | 30.6 min | $11.33 | 8,513 | 28 | 23.2 M |
| 5 | 30.6 min | $11.44 | 8,514 | 27 | 23.0 M |
| **Sum** | **156.3 min** | **$56.86** | **42,545** | **160 (0.37 %)** | **115.0 M** |

### Recovery proposer passes (2026-05-02; commit `731466d8`)

160 of 160 originally-failed tile-passes recovered (100 %) across
five sequential resume passes (`workers=30, max_retries=15,
base_wait=30, service_tier=flex`). Per-pass: run_1 25/25, run_2
42/42, run_3 38/38, run_4 28/28, run_5 27/27. Net new detections:
+612 across the 5 recovery passes.

Recovery cost: **$57.10** (vs the planned $0.50 cap; per-tile cost
$0.46 vs T=0.3 recovery's $0.0017/tile). Root cause is retry storms:
14–25 retries per recovered tile, totalling 3,144 `retries_other`
across the 5 passes. The 160 originally-failed tiles were stubborn
JSON-parse failures whose re-execution consumed heavy thinking-token
budgets per attempt. Cost is sunk; the recovery did succeed. See
Obs 319 in `docs/notes/reflections/working-notes.md` for the T=0.7-
vs-T=0.3 recovery-cost asymmetry analysis.

Per-pass cost is uniform to within 1 % — expected, since tile count,
per-tile text payload, and thinking-level ceiling are all constant.
Contrast with the MIN run (uniform cost, 0 thinking) and the image
HIGH run (uniform cost, ~19 M thinking tokens per pass).

### Token breakdown (post-recovery aggregate)

| Field | Tokens | Share |
|-------|-------:|------:|
| Input (billed) | 145.0 M | 36.8 % |
| Input (cached) | **0** | 0.0 % |
| Output | 18.1 M | 4.6 % |
| Thinking | **230.5 M** | **58.6 %** |
| **Total** | **393.6 M** | 100 % |

The roughly-doubled token totals over the original run (115 M → 230 M
thinking; 80 M → 145 M billed input) are dominated by the recovery
passes' retry storms (≈14–25 retries per recovered tile across 160
tiles; see Obs 319). Original-run-only token shares (115 M thinking,
56 % share) match the values cited under the original 2026-04-18
report, preserved here for paper-supplement transparency.

**Cache hit rate: 0.0 %.** Same mechanistic explanation as the MIN
run: the text-only prompt preamble (~393 tokens) is below Gemini
Flash's 1,024-token minimum for context caching.

### Unit costs (key publication figures, post-recovery)

| Metric | Value (post-recovery) | Value (original 2026-04-18) |
|--------|-----------------------:|----------------------------:|
| Cost per tile | $0.01485 | $0.00815 |
| Cost per map | $2.306 | $1.265 |
| Cost per detection | $0.03045 | $0.01681 |
| Cost per reference mound | $0.02658 | $0.01459 |
| Tile count | 8,541 | 8,541 |
| Map count | 55 | 55 |
| Reference mound count | 4,770 | 4,770 |
| Final detection count (post vote + prob) | **4,164** | 4,143 |

The post-recovery per-tile cost ($0.01485) inflates over the original
$0.00815 because the recovery overrun added $57.10 to the proposer
budget on the same 8,541-tile denominator. Paper-citable per-tile
cost should use the original-launch figure ($0.00815) for cross-run
comparability, with the post-recovery figure available as a
supplement.

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

## Scope (post-recovery)

| Field | Value |
|-------|------:|
| Maps processed | 55 |
| Tiles processed | 8,541 (each processed 5 times) |
| Proposer API calls (attempted, original launch) | 42,705 |
| Proposer API calls (completed at original launch) | 42,545 |
| Proposer API calls (failed at original launch) | 160 (0.37 % of 42,705) |
| Proposer API calls (recovered 2026-05-02) | 160 of 160 (100 %) |
| Proposer API calls (failed post-recovery) | **0** |
| Verifier API calls | 9,205 candidates extracted; 9,131 original-pass + 74 cleanup-pass verified |
| Reference ground-truth mounds | 4,770 (curator); 4,745 in updated student-GT (commit `baf1497a` adds the second of two touching mounds at K-35-064-3) |
| Consensus candidates (4-of-5) | 9,206 features (post-recovery; up from 9,131 pre-recovery, +75) |
| Final detections (prob ≥ 0.15) | **4,164** (post-recovery; up from 4,143, +21) |

> **Magnitude correction (Obs 318)**: the original report cited the
> failure count as "25" (drawing on Obs 281's pre-audit pass-1 count).
> The audited total across all 5 passes is 160. See Obs 318
> (`docs/notes/reflections/working-notes.md`, commit `f5df7a09`) for
> the full reconciliation. The corrected denominator (42,705) and
> failure count (160) are both reflected here.

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
the publishable launcher (post-recovery values 2026-05-03):

1. **Image HIGH (library_plus-hp, 2026-04-18)**: F1 @ 50 m = 0.771
   (D-S 0.795). High-precision, recall-limited. **$364.70.**
2. **Text HIGH (this re-run, 2026-04-19; recovered 2026-05-02/03)**:
   F1 @ 50 m = **0.792** (post-recovery; D-S **0.814**). Best headline
   F1. Total cost **$126.81** (original $69.60 + recovery $57.10 +
   verifier cleanup $0.10 + FP-classify share $0.01); paper-citable
   per-tile cost uses the original-launch $0.00815 figure for cross-
   run comparability.
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

## Recovery 2026-05-02/03

The original 2026-04-18 run left 160 of 42,705 attempted proposer
calls unrecovered (rate 0.37 %). Three audit findings made full
recovery attractive: (1) Obs 318 corrected the previously-cited
Obs 281 failure count from "25" to 160, raising the visibility of
the issue; (2) Obs 319 surfaced the T=0.7 vs T=0.3 recovery-cost
asymmetry as a methodological observation; and (3) the parser fix
at commit `e3aef6fa` (3-tier JSON repair on the realtime proposer)
identified ~92 % of historical failures as repairable patterns,
suggesting the recovery was tractable in principle.

### Propagation chain (commit-by-commit)

The full propagation arc spans 2026-05-02 through 2026-05-03:

| Stage | Commit | Notes |
|------:|:-------|:------|
| Driver script | `1ea92b9c` | Single-round recovery driver added |
| **Proposer recovery** | **`731466d8`** | 160/160 tiles recovered (5 sequential resume passes); +612 net new detections; cost overrun $57.10 vs $0.50 cap |
| Obs 319 | `c913b69b`, `3219aa76` | T=0.7 vs T=0.3 recovery-cost asymmetry analysis |
| Parser fix (root cause) | **`e3aef6fa`** | 3-tier JSON repair added to realtime proposer (was batch-API-only); +163 outstanding failures across 3 other runs (image, text-MIN, GS-v2) recoverable |
| Consensus + verifier cleanup + rebuild | **`d7f85978`** | consensus 9,131 → 9,206; 74 new candidates verified; cost-manifest rebuilt; verified geojson rebuilt |
| Aggregate-cost fix | **`7f05f529`** | merge `*.pre-recovery-*.backup` siblings (handles cleanup-overwrite case) — surfaced full $126.81 |
| D-S row-position fix | **`a9e280a3`** | use stable candidate_id instead of row position (safe under re-cluster) |
| BCa N=10K eval re-run | `e20f3e18` | baseline + full-buffer + extended-buffer |
| Curator GT mound added | `baf1497a` | 2nd of 2 touching mounds at K-35-064-3 cand 4264; GT 4,744 → 4,745 features |
| Updated GT re-evaluation | `f533fda5` | re-eval against 4,745 features |
| Review-app entries (T=0.7) | `9b80621e` | 7 new entries from 2026-05-03 |
| Corrected-F1 multi-buffer | `f6eaeca9` | with 6 new reviews + 1 new GT mound; F1 corrected @50m: 0.8260 → 0.8273 |
| Pairwise-permutation v2 | `aeb9fb7f` | 3 pairs touching T=0.7 |
| Phase 4-6 propagation | **`33435aab`** | attractor-pull v2 + FP-classify ($0.58) + TP-localisation + per-map shell + student-GT-FN |
| D-S re-aggregation | `366f9c66` | post-recovery + new GT |
| **DS-vs-human cross-tab** | **`e07dae37`** | re-run on text-high (final propagation step) |

### Bug discoveries surfaced during recovery

1. **JSON parser realtime-vs-batch asymmetry** (fixed at `e3aef6fa`):
   the realtime proposer in `scripts/4_detect_mounds_batch.py`
   previously called `json.loads()` directly and treated any
   `JSONDecodeError` as unrecoverable. The canonical Tier 1 trailing-
   comma strip was already present at `scripts/lib_batch_api.py:920`
   for the batch path. The patch ports it as `parse_response_with_repair()`
   with three tiers (regex strip → permissive json5 → bracket-balance
   fallback), recovering ~92 % of historical failures. **+163 tiles
   outstanding across 3 other runs** (image, text-MIN, GS-v2) are
   recoverable under the same fix and queued for follow-up.
2. **Dawid-Skene row-position bug** (fixed at `a9e280a3`): D-S
   indexing relied on row position, which is unsafe under re-cluster
   (recovery added new consensus rows, shifting positions). Patched
   to use stable `candidate_id` indexing.
3. **`cost_manifest` cleanup-overwrites-meta** (fixed at `7f05f529`):
   `aggregate_cost_manifest` previously read the post-cleanup
   `verified/run.meta.json` and silently dropped the original
   verifier meta. Patch teaches it to glob for `*.pre-recovery-*.backup`
   and `*.pre-cleanup-*.backup` siblings and merge their costs into
   the totals; merged backups are recorded under
   `cost_manifest._metadata.cleanup_recovery_metas_merged`.
4. **Obs 281 magnitude correction** (Obs 318, commit `f5df7a09`):
   the previously-cited 25/42,545 figure was a Pass 1 only count;
   the audit total across all 5 passes is 160/42,705.

### Outcomes versus pre-recovery (50 m buffer)

| Metric | Pre-recovery | Post-recovery | Δ |
|--------|-------------:|--------------:|----:|
| Verified detections | 4,143 | 4,164 | +21 |
| F1 raw @50 m | 0.7896 | 0.7920 | +0.0024 |
| F1 corrected @50 m (Approach B) | 0.8260 | 0.8273 | +0.0013 |
| MCC @50 m | (n/a in pre-rec mirror) | 0.648 [0.633, 0.662] | — |
| Total run cost | $69.60 | **$126.81** | +$57.21 |

### Known follow-up after this recovery

The parser fix surfaced **3 outstanding recoveries** that should be
queued under the same recovery pattern:

1. `outputs/55maps-image-generalisation/` — image HIGH run
2. `outputs/55maps-text-min-generalisation/` — text MIN run
3. `outputs/h11/gold-standard-v2/` — GS-v2 run

Per the parser-fix audit (commit message of `e3aef6fa`), these three
runs collectively lost 163 tiles to JSON-parse failures that the
3-tier repair would now recover. None has been actioned as of
2026-05-03; they are tracked in `planning/paper-writeup-continuity.md`
under "Pending before paper outline".
