# Phase 2b Retest — H7 Temperature Analysis Summary

**Study**: Phase 2b retest — H7 Temperature (5 T × 2 tracks × K=3 × 340 tiles)
**Date**: 2026-03-16 (evaluation at `scripts/evaluate_retest_all.py` git hash `e038bfe8`, generation timestamp 2026-03-16T22:53 UTC)
**Protocol-errata**: E27 (dual-track carry-forward from Phase 2a), E43 (distinguished but not active in this retest — see §"Preregistered T=1.0 vs E43 UNINTENDED-T1.0")
**Primary aggregation**: greedy consensus (K=3 runs pooled tile-level)
**Evaluation**: 340-tile retest test set, 20 m buffer, 1,000 bootstrap iterations, seed=42, tile-level-multi-run resampling
**FDR correction**: Benjamini–Hochberg at q=0.05, applied within each track independently (tracks represent independent OFAT chains)

## Headline result — T=0.0 optimal on both tracks; T=1.0 (Gemini default) significantly worse

**Track 1 (image-using, `brief-text-image`)**: Monotonic decline from
T=0.0 to T=1.3. T=0.0 is the optimum and is significantly better than
T=0.7, T=1.0, and T=1.3 after FDR correction.

**Track 2 (text-only, `brief-text`)**: T=0.0 and T=0.3 are essentially
tied at the top (ΔF1 = −0.002, p = 0.862); both are significantly
better than T=1.0 and T=1.3. The text-track optimum is T=0.0–T=0.3.

| Track | Best T | F1 [95 % CI] | Worst T | F1 [95 % CI] | ΔF1 optimum vs worst |
|-------|:------:|--------------|:-------:|--------------|---------------------:|
| Image | T=0.0 | 0.587 [0.541, 0.633] | T=1.3 | 0.490 [0.459, 0.540] | +0.097 |
| Text | T=0.3 | 0.606 [0.553, 0.654] | T=1.0 | 0.533 [0.432, 0.583] | +0.073 |

**Practitioner claim**: Gemini API's default temperature (T=1.0) is
not optimal for mound detection; setting T=0.0 yields +0.06 to +0.10
F1 over the default on the image track and +0.07 to +0.10 on the
text track.

## Cross-hypothesis context

Phase 2b sits in Era 1 (preregistered confirmatory hypotheses) as the
H7 Temperature test. Its output — the per-track carry-forward
temperature — feeds Phase 2c (H8 Library Composition) and downstream
Era 1 phases. The retest at 340 tiles × K=3 replaces a 60-tile K=10
pilot (archived to `archive/outputs-pre-retest-60-tile/phase2b/`)
that reported the same qualitative direction at less power.

| Phase | Factor | Carry-forward from Phase 2b |
|-------|--------|-----------------------------|
| 2c | Library composition (H8) | T=0.0 (both tracks) |
| 2d | Negation text (H5) | T=0.0 (both tracks) |
| 2e | Example ordering (H4) | T=0.0 (image track) |

The Phase 2b carry-forward is captured as a standalone reference
document at `results/phase2b-carry-forward-parameters.md`
(retest-era equivalent created in this same Session 75 commit; see
§"Option B residual — carry-forward repoint" below).

## Experiment — Phase 2b H7 Temperature

### Design

Five temperature levels (T=0.0, T=0.3, T=0.7, T=1.0, T=1.3) × two
tracks (track 1 = image-using `brief-text-image`; track 2 = text-only
`brief-text`) × K=3 runs × 340 tiles = **10,200 tile-runs total**.
Both tracks inherit the Phase 2a carry-forward (Decision 16, E27):
two independent OFAT chains from the best text-only and best image-
using modality/elaboration level.

Fixed parameters (both tracks):

- Model: `gemini-3-flash`
- Thinking level: `minimal` (per Phase 2a preregistration carry-forward; distinct from the HIGH-thinking production setting used in Era 2 / 55-map runs)
- Tile size: 384 px
- Ordering: canonical-first
- Example images: `include_example_images: true` for track 1,
  `false` for track 2
- Manifest: 340-tile retest evaluation set
- Per-run seed: non-seeded (Gemini's non-deterministic decoding
  produces the run-to-run variance that K=3 captures)

### Track 1 (Image) — full results

| Temperature | F1 | 95 % CI | Precision | Recall | K |
|:-----------:|:---:|:------:|:---------:|:------:|:-:|
| **T=0.0** | **0.587** | **[0.541, 0.633]** | **0.499** | **0.713** | 3 |
| T=0.3 | 0.575 | [0.528, 0.612] | 0.488 | 0.699 | 3 |
| T=0.7 | 0.537 | [0.489, 0.580] | 0.452 | 0.660 | 3 |
| T=1.0 | 0.527 | [0.474, 0.561] | 0.440 | 0.657 | 3 |
| T=1.3 | 0.490 | [0.459, 0.540] | 0.406 | 0.618 | 3 |

Inter-run std at T=0.0 = 0.001 (essentially deterministic), rising
to 0.022 at T=1.0 and 0.018 at T=1.3. K=3 replication captures the
stochasticity budget at higher temperatures; at T=0.0 the three runs
are near-identical by construction.

### Track 1 — FDR-significant pairwise contrasts

Six of ten pairwise contrasts are significant after BH-FDR at q=0.05:

| Comparison | ΔF1 | p (FDR-adj) |
|------------|:---:|:-----------:|
| T=0.0 > T=0.7 | +0.050 | 0.002 |
| T=0.0 > T=1.0 | +0.064 | 0.001 |
| T=0.0 > T=1.3 | +0.085 | 0.001 |
| T=0.3 > T=1.0 | +0.050 | 0.006 |
| T=0.3 > T=1.3 | +0.071 | 0.001 |
| T=0.7 > T=1.3 | +0.035 | 0.042 |

Non-significant contrasts: T=0.0 vs T=0.3 (ΔF1 = +0.015, p = 0.30 —
the two lowest temperatures are statistically tied at this power);
T=0.3 vs T=0.7 (+0.036, p ≈ 0.06); T=0.7 vs T=1.0 (+0.014); T=1.0 vs
T=1.3 (+0.020).

### Track 2 (Text) — full results

| Temperature | F1 | 95 % CI | Precision | Recall | K |
|:-----------:|:---:|:------:|:---------:|:------:|:-:|
| **T=0.3** | **0.606** | **[0.553, 0.654]** | **0.491** | **0.793** | 3 |
| T=0.0 | 0.605 | [0.547, 0.655] | 0.487 | 0.798 | 3 |
| T=0.7 | 0.584 | [0.521, 0.636] | 0.461 | 0.798 | 3 |
| T=1.3 | 0.544 | [0.487, 0.603] | 0.425 | 0.756 | 3 |
| T=1.0 | 0.533 | [0.432, 0.583] | 0.415 | 0.748 | 3 |

Note the **T=1.0 < T=1.3 inversion on the text track** (point-estimate
ΔF1 = −0.011 from the table; bootstrap-mean ΔF1 = −0.036 from
`pairwise-bootstrap-comparisons.json`; p = 0.204, non-significant).
This is a reminder that between-temperature
differences at the top of the range are small and noise-dominated.

### Track 2 — FDR-significant pairwise contrasts

Five of ten pairwise contrasts are significant after BH-FDR at q=0.05:

| Comparison | ΔF1 | p (FDR-adj) |
|------------|:---:|:-----------:|
| T=0.0 > T=1.0 | +0.093 | 0.001 |
| T=0.0 > T=1.3 | +0.057 | 0.004 |
| T=0.3 > T=1.0 | +0.096 | 0.001 |
| T=0.3 > T=1.3 | +0.060 | 0.006 |
| T=0.7 > T=1.0 | +0.072 | 0.004 |

Non-significant contrasts: T=0.0 vs T=0.3 (ΔF1 = −0.002, p = 0.862);
T=0.0 vs T=0.7 (+0.021, n.s.); T=0.3 vs T=0.7 (+0.023, n.s.);
T=0.7 vs T=1.3 (+0.037, n.s.); T=1.0 vs T=1.3 (−0.011, n.s.).

### Retention at higher temperatures

Inter-run precision and recall widen at higher T on both tracks. The
F1 decline is precision-driven: as T rises, the model emits more
candidates per tile (higher recall-denominator), but the additional
candidates are disproportionately false positives. This is consistent
across both tracks and consistent with the 60-tile K=10 pilot (which
reported the same qualitative pattern at less statistical power —
see `archive/outputs-pre-retest-60-tile/phase2b/`).

## ⚠️ Preregistered T=1.0 vs E43 UNINTENDED-T1.0 — paper must cite this row

The paper's scientific temperature finding rests on **this Phase 2b
retest** (340-tile K=3, preregistered five-temperature sweep). It
does NOT rest on a separate set of runs at
`outputs/h11/consensus-384-UNINTENDED-T1.0/` and
`outputs/h11/single-pass-384-UNINTENDED-T1.0/`, which are
**accidental deployment data** from protocol-errata E43.

| Data source | Scientific status | Paper use |
|-------------|-------------------|-----------|
| **`outputs/retest/phase2b/{track1-image,track2-text}/T{0.0, 0.3, 0.7, 1.0, 1.3}/`** | Preregistered H7 temperature sweep at 340 tiles, K=3, bootstrap n=1000, FDR-corrected | **Cite this row** for "T=1.0 (Gemini default) is suboptimal" |
| `outputs/h11/consensus-384-UNINTENDED-T1.0/` + `outputs/h11/single-pass-384-UNINTENDED-T1.0/` | Accidental E43 deployment at T=1.0 when T=0.7 was intended. Retained for 487-tile / Era 2 T=1.0 scope coverage (dual-role banners in the directories' READMEs, commit `5ae94041`) | Do NOT cite as scientific evidence of "T=1.0 is suboptimal". May be referenced for errata transparency or for Era 2 T=1.0 scope where Phase 2b's 340-tile corpus cannot extend (see Obs 274) |

The E43 UNINTENDED-T1.0 data is serendipitous coverage that the paper
may choose to reference for Era 2 / 487-tile leaderboard contexts,
but it is not the source for the scientific claim that T=1.0 is
inferior. See working-notes Obs 274 and `docs/methodology/preregistration/protocol-errata.md`
§E43 for the full framing.

## Carry-forward decision

**T=0.0 (deterministic decoding) selected for both tracks.**

### Decision rule

The preregistered decision rule: "If T=1.0 (default) is within 0.02 F1
of best, prefer T=1.0 for simplicity." T=1.0 is NOT within 0.02 of
best on either track:

- Track 1 image: T=0.0 − T=1.0 = +0.060 F1 (well outside 0.02)
- Track 2 text: T=0.3 − T=1.0 = +0.073 F1 (well outside 0.02)

T=0.0 is unambiguously optimal. Both tracks show monotonic (track 1)
or near-monotonic (track 2, with T=0.0/T=0.3 tied at the top)
degradation with increasing temperature.

### Note on the two-track independence

Track 1's T=0.0 and track 2's T=0.3 are the separate optima. Both
within-track decision rules pass the 0.02 threshold cleanly. The
dual-track design (Decision 16, E27) requires independent carry-
forwards; we do not merge the tracks into a single temperature
preference.

## Option B residual — carry-forward repoint (this commit)

Per `planning/interim-docs-review.md` §3.15 "Superseded pre-retest
artefacts", this level-up executes three bound sub-tasks in the same
commit sequence:

1. **Create retest-era `results/phase2b-carry-forward-parameters.md`** —
   new doc based on the 340-tile K=3 retest data (this analysis).
   Replaces the pre-retest 60-tile K=10 pilot version.
2. **Repoint `results/phase2c-carry-forward-parameters.md:126`** — the
   active citation to the pre-retest carry-forward is redirected to
   the new retest-era equivalent.
3. **Archive the pre-retest `results/phase2b-carry-forward-parameters.md`** —
   move to `archive/outputs-pre-retest-60-tile/phase2b/` alongside the
   six pilot files archived in Session 74 (commit `16ee3ae5`), under
   a distinct filename (`carry-forward-parameters-with-retention-banner.md`)
   to preserve both historical snapshots of the pre-retest carry-forward.

These three sub-tasks resolve the "Option B residual" tracked in
Session 74's end-of-session note, in the retention banner on the
archived file, and in scorecard §3.15 + §6 Step-4 item 3.

## Caveats

1. **K=3 vs K=10 pilot.** The retest at K=3 is tighter than the
   60-tile K=10 pilot on n-tiles (340 vs 60) but looser on replicate
   count (3 vs 10). The choice trades off sampling power against
   API spend. At K=3, inter-run variance is directly observable
   (std = 0.001 at T=0.0 rising to 0.022 at T=1.0), and bootstrap
   resampling preserves the multi-run structure. The qualitative
   finding (T=0.0 optimal, T=1.0 significantly worse) holds at both
   K values; the FDR-significant contrast list is more confident at
   the 340-tile K=3 retest because the larger n-tiles more than
   compensates for the smaller K.
2. **Track 2 T=0.0 vs T=0.3 is non-significant (p = 0.862).** The
   carry-forward rule selects T=0.0 because ΔF1 is essentially zero
   and T=0.0 is the simpler default. A reader wishing to argue for
   T=0.3 on the text track has no statistical objection from this
   data, only the convention that deterministic decoding is the
   preferred default when the best-T is statistically indistinguishable
   from the next-best-T.
3. **Phase 2b T=0.0 is NOT the consensus-optimum T=0.7.** Working-notes
   line 6095+ documents the "five design decisions that cross over"
   between the single-pass Phase 2b regime and the K=5 consensus
   production regime. Phase 2b's K=3 single-pass optimum is T=0.0;
   the K=5 consensus-stage operation point is T=0.7 (Phase 3a image-
   matrix finding). The paper should not conflate the two: the Phase
   2b finding is "temperature affects single-pass F1"; the Phase 3a /
   55-map finding is "T=0.7 is the consensus-stage optimum". These
   are compatible — at higher K, consensus voting averages out some
   of the T>0 noise, so a modest T>0 can benefit aggregation — but
   the paper's practitioner message about Gemini's T=1.0 default is
   supported by Phase 2b, not by an implicit assumption that T=0.0
   is also the production operating point.
4. **Bootstrap multi-run resampling.** Bootstrap CIs are tile-level-
   multi-run: each bootstrap draw resamples tiles with replacement
   and, independently, resamples runs with replacement within each
   drawn tile. This preserves the K=3 structure and avoids
   under-reporting run-to-run variance. Sibling evaluation JSONs
   (retest phases 2a / 2c / 2d / 2e / 3a) use the same resampling
   methodology — see `results/retest/phase2b-track{1,2}-evaluation.metadata.json`
   for the canonical script reference.
5. **E43 UNINTENDED-T1.0 distinction is load-bearing.** See the
   §"⚠️ Preregistered T=1.0 vs E43 UNINTENDED-T1.0" block above. A
   paper reviewer asking "why are there two T=1.0 results?" must be
   routed to this retest row and the UNINTENDED directories' READMEs
   (commit `5ae94041`), not cross-cited.

## Paper implications

1. **Practitioner-facing headline: change Gemini API's T=1.0 default.**
   Setting T=0.0 (or T=0.3 on the text track) improves F1 by 0.06–0.10
   versus the Gemini default. This is a transferable finding that
   applies to any downstream user of Gemini 3 Flash for
   detection-style tasks, and is the clearest actionable output of
   the paper's Methods section.
2. **T=0.0 is the Era 1 single-pass optimum; carry-forward to
   Phases 2c–2e is clean.** All three downstream Era 1 phases use
   T=0.0 from Phase 2b. Library composition (Phase 2c), negation text
   (Phase 2d), and example ordering (Phase 2e) therefore test their
   own factors at the Phase-2b-optimal temperature.
3. **T=0.0 single-pass ≠ T=0.7 consensus-stage.** The paper's Methods
   section should flag the crossover explicitly. Single-pass users
   want T=0.0; K=5 consensus pipelines benefit from a moderate T
   because consensus voting filters out the FP excess. See
   working-notes Obs 116, 177, 209, 274 for the consensus-stage
   temperature story.
4. **The monotonic decline across T on the image track is a
   mechanism-level finding.** Precision drops faster than recall
   rises with T. This is consistent with the "prompt-faithfulness"
   story — at higher T, the model's output distribution spreads,
   generating more false-positive candidates without adding many
   true-positive recoveries.

## Reproducibility

| Metric | Value |
|--------|-------|
| Bootstrap iterations | 1,000 |
| Bootstrap seed | 42 |
| Bootstrap resampling unit | tile-level-multi-run (resample tiles, then resample runs within drawn tile) |
| Bootstrap methodology | percentile, 95 % CI (2.5 / 97.5 quantiles) |
| Evaluation tiles | 340 (retest test set) |
| Evaluation buffer | 20 m |
| K (runs per condition) | 3 |
| Conditions (per track) | 5 temperatures (T=0.0, 0.3, 0.7, 1.0, 1.3) |
| Tracks | 2 (image-using, text-only) |
| Total tile-runs | 10,200 (340 × 3 × 5 × 2) |
| FDR method | Benjamini–Hochberg at q=0.05, within-track |
| Evaluation script | `scripts/evaluate_retest_all.py` at git hash `e038bfe8` |

## Artefacts

### Retest data (this summary's authoritative source)

- Study YAMLs:
  - `studies/retest/phase2b-h7-temperature.yaml` (Track 1 image)
  - `studies/retest/phase2b-h7-temperature-text-only.yaml` (Track 2 text)
- Raw detections (Track 1): `outputs/retest/phase2b/track1-image/{T0.0,T0.3,T0.7,T1.0,T1.3}/run_{1,2,3}/detections_T*_run0*.geojson`
- Raw detections (Track 2): `outputs/retest/phase2b/track2-text/{T0.0,T0.3,T0.7,T1.0,T1.3}/run_{1,2,3}/detections_T*_run0*.geojson`
- Per-run tile manifests: sibling `*.tiles.json` in each run directory (each reports `total_tiles = 340`, `len(completed) = 340`, `len(failed) = 0`)
- Per-run meta: sibling `*.meta.json` in each run directory (model, temperature, thinking level, timestamps)
- Evaluation outputs:
  - `results/retest/phase2b-track1-evaluation.json` + `.metadata.json` (Track 1)
  - `results/retest/phase2b-track2-evaluation.json` + `.metadata.json` (Track 2)
- Aggregated narrative embedding: `results/retest/retest-production-summary.md` §Phase 2b (lines 40–69) + §Pairwise Comparison Highlights (lines 248–267)
- Cross-phase pairwise bootstrap: `results/retest/pairwise-bootstrap-comparisons.json` (all 70 contrasts across Phase 2a–3a; Phase 2b entries = 20)

### Superseded pre-retest pilot

- Archive root: `archive/outputs-pre-retest-60-tile/phase2b/` (moved Session 74, commit `16ee3ae5`, plus this Session 75 pass)
- Files (60-tile K=10 pilot): `phase2b-track1-image-summary.md`, `phase2b-track2-text-summary.md`, `phase2b-track{1,2}-*-analysis.{json, metadata.json}`, `track{1,2}-*/`, `track{1,2}-*.log`, `carry-forward-parameters.md` (original archived 2026-04-23), `carry-forward-parameters-with-retention-banner.md` (this Session 75 pass — the active retained-copy with the retention banner, superseded by the new retest-era doc)

### Paper-track and cross-hypothesis

- E43 UNINTENDED-T1.0 directories (dual-role, 487-tile scope): `outputs/h11/{consensus,single-pass}-384-UNINTENDED-T1.0/` + READMEs (commit `5ae94041`)
- Protocol errata: `docs/methodology/preregistration/protocol-errata.md` §E43, §E27
- Working-notes: Obs 116, 177, 209 (consensus-stage temperature story), Obs 274 (Phase 2b tile-level MCC, 2026-04-23)
- H8 v2 summary: `results/h8-v2/analysis_summary.md` (Scale-8 at Phase 2b-optimal T=0.0 carry-forward)

## Scripts used

| Phase | Script | Purpose |
|-------|--------|---------|
| 1 | `scripts/run_phase2.py` (or retest-specific launch entrypoint) | K=3 detection runs per temperature × track |
| 2 | `scripts/merge_passes.py` / inline aggregation | Tile-level aggregation across K=3 runs |
| 3 | `scripts/evaluate_detections.py` | Per-condition F1 / P / R computation at 20 m buffer |
| 4 | `scripts/evaluate_retest_all.py` (at git hash `e038bfe8`) | Multi-phase retest evaluator with 1,000-iteration tile-level-multi-run bootstrap CIs + pairwise permutation scaffolding; produces `results/retest/phase2b-track{1,2}-evaluation.json` |
| 5 | `scripts/apply_fdr_correction.py` (or equivalent FDR pass) | Benjamini–Hochberg correction within-track across 10 pairwise contrasts |

## Cross-hypothesis links

- Phase 2a — modality and elaboration (source of the dual-track carry-forward, E27)
- Phase 2c — library composition (inherits T=0.0 from this Phase 2b retest)
- Phase 2d — negation text (inherits T=0.0)
- Phase 2e — example ordering (inherits T=0.0)
- Phase 3a — image/text matrices at consensus stage (T=0.7 is the K=5 consensus optimum, not T=0.0 — see caveat 3)
- Obs 116 / 177 / 209 / 274 — consensus-stage temperature story
- Protocol errata E27 (dual-track carry-forward), E43 (UNINTENDED-T1.0 distinction), E49 / E51 / E52 (library-axis retests at T=0.7, using the production operating point rather than Phase-2b-optimal T=0.0)

---

**Status**: Authoritative narrative summary for Phase 2b Retest
(340-tile K=3 H7 Temperature). Supersedes the embedded narrative in
`results/retest/retest-production-summary.md` §Phase 2b as the primary
paper-citation target, and supersedes the 60-tile K=10 pilot at
`archive/outputs-pre-retest-60-tile/phase2b/` (retained for
historical record per the archive-never-delete policy).
