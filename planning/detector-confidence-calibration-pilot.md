# Detector confidence calibration pilot — vote-fraction-as-proxy validation

**Created**: 2026-04-27
**Status**: Plan; pending execution after H-a vote-fraction-proxy analysis completes
**Cross-references**:

- Companion: `planning/detector-confidence-flag-scoping.md` (deliverable c — opt-in flag scope)
- Working notes: Obs 269 (verifier over-confidence at high p, AUC=0.65, ECE=0.269; `docs/notes/reflections/working-notes.md` line 12578) and Obs 277 (verifier-prompt variation cannot rescue image-track miscalibration; line 13215)
- Pre-condition: H-a vote-fraction-proxy analysis (uses K-pass agreement rate as a behavioural proxy for detector confidence) must complete first

## Motivation

The proposer schema returns only `{box_2d, label, subtype}` — no per-detection numeric confidence (contrast with the verifier's `mound_probability`). Item H-a proposes that the K-pass agreement rate (`vote_count / K`) can serve as a behavioural proxy for detector confidence: detections that recur across many independent passes are presumed to be the ones the model is most confident about. This pilot tests that presumption against ground truth before the proxy is reported in the paper as a calibrated quantity.

The verifier's `mound_probability` is itself only weakly calibrated on the image track (Obs 269: ECE=0.269, AUC=0.65 on 55-map; Obs 277: ECE=0.179 on the 4-map gold-standard 487-tile corpus, no prompt variant clears ECE<0.10) — so any successor "detector confidence" must be benchmarked just as carefully. This pilot is the calibration step for the proxy.

## Hypothesis

Vote-fraction `c/K` from K independent passes is monotonically correlated with `P(real_mound | detected)`.

- If the relationship is monotonic with low scatter, vote-fraction is a sound behavioural proxy and may be reported in the paper (with footnote) as a calibrated detector-confidence proxy.
- If the relationship is non-monotonic, or scatter is high enough that vote-fraction does not reliably rank-order detections by truth probability, the proxy is unreliable and the project should escalate to deliverable (c) — opt-in flag scoping.

## Pilot scope

Pick **one** condition with a high-K cell already on disk on the 4-map 487-tile gold-standard corpus, so that no new API spend is required:

- **Primary candidate (preferred)**: `outputs/retest/phase3a/track2-text/T0.7/` K=30 cell. Highest K available, gives the finest-grained vote-fraction histogram (resolutions 0/30, 1/30, …, 30/30 = 31 bins).
- **Secondary candidate**: `outputs/retest/phase3a/track1-image/T0.7/` K=30, if the text track shows pathological behaviour (e.g., near-zero variance across passes).
- **Backup (smaller K)**: `outputs/h8-v2/scale-4/run_{1..5}` (K=5) — fewer bins but a published condition; only use if the K=30 cells are unusable.

Reuse the existing per-pass detection geojsons. **Zero API spend.**

Ground truth: curator-reviewed expert mounds in `inputs/vectors/references/mounds-reference.geojson` (the 569-feature 4-map gold-standard reference; matched at 20 m tolerance per the project standard and the same protocol used in `archive/planning-historical-session-78/session-78-matrix-calibration-summary.md`, archived 2026-05-01).

Tile scope: `inputs/vectors/bounds/384/full_evaluation_bounds.geojson` (487 tiles, Era 2). This matches the Session 78 verifier matrix scope so the detector-confidence proxy and the verifier's `mound_probability` are directly comparable on the same corpus.

## Method

1. **Cluster across K passes**. For the chosen K=30 condition, run the existing pipeline (`scripts/lib_consensus.py` `cluster_across_passes`, distance threshold 20 m) over all K runs. Each cluster carries a `vote_count` ∈ {1, …, K} representing how many independent passes produced a detection at that location.

2. **Match clusters to ground truth**. For each cluster, compute match-status against the gold-standard mounds at 20 m tolerance using `gpd.sjoin_nearest` (same primitive as the Session 78 calibration matrix). Label each cluster as TP (matched a reference mound) or FP (matched no reference mound).

3. **Bin and compute reliability**. Bin clusters by `vote_count` (or by `vote_fraction = vote_count / K` for cross-K comparability). For each bin compute:
   - `n_total`: cluster count in bin
   - `n_TP`: matched count
   - `empirical P(TP) = n_TP / n_total`
   - 95% Wilson CI on `P(TP)`

4. **Reliability diagram**. Plot mean predicted vote-fraction (x-axis) vs empirical `P(TP)` (y-axis) with the diagonal reference line. Mark bin counts so the reader can see where uncertainty lives. Mirrors the reliability diagram in `results/55maps-image-generalisation/verifier-calibration-crosstab/reliability-diagram.png`.

5. **Rank-correlation**. Compute Spearman ρ between `vote_count` (per cluster, not bin-averaged) and a binary TP indicator. Report point estimate and 95% bootstrap CI (10,000 resamples, seed=42).

6. **Comparison overlay**. On the same reliability diagram, plot the verifier's `mound_probability` calibration on the same crops (where already computed for Session 78) so the paper can place vote-fraction in context against the existing verifier signal.

## Decision rule

Pre-registered:

| Spearman ρ | Reliability shape | Decision |
|---|---|---|
| **ρ ≥ 0.7** | Monotonic, no large reversals | Proxy is **sound**. Report vote-fraction in the paper as a calibrated detector-confidence proxy with a footnote describing the calibration methodology and pointing to the pilot results. |
| **0.5 ≤ ρ < 0.7** | Monotonic but noisy | Proxy is **borderline**. Report only as a coarse rank, not a probability. Consider escalation to (c) opt-in flag if a more precise per-detection confidence is needed for downstream work (e.g., verifier-input prioritisation). |
| **ρ < 0.5** OR non-monotonic | — | Proxy is **unreliable**. Do **not** report vote-fraction as a confidence proxy. Escalate to deliverable (c) — opt-in flag scoping doc. |

The pre-registration must be committed (or at minimum marked with the intended cut-offs in this file) before the pilot is run, to prevent post-hoc threshold tuning.

## Outputs

Write all artefacts to `results/detector-confidence-calibration-pilot/<condition>/`:

- `calibration.json` — per-bin counts, empirical P(TP), CIs, Spearman ρ
- `calibration.md` — human-readable summary including decision rule outcome
- `reliability-diagram.png` — vote-fraction vs empirical P(TP), with diagonal and verifier overlay
- `histogram.png` — distribution of `vote_count` across all clusters
- `clusters.parquet` — per-cluster table (`cluster_id`, `centroid_x`, `centroid_y`, `vote_count`, `vote_fraction`, `tp_flag`, `match_distance_m`)

## Compute and budget

- Compute: minutes (clustering + spatial join + reliability metrics on ~few-thousand clusters at K=30).
- API spend: **$0** — re-uses existing per-pass geojsons.
- Wall-clock from kick-off to decision: < 1 hour.

## Pre-conditions

1. H-a vote-fraction-proxy analysis must be complete and the per-pass geojsons + clustering pipeline confirmed working at K=30.
2. The 4-map curator reference (`mounds-reference.geojson`) must be the accepted ground truth for the pilot — students-corrected gold-standard corpus, not the 55-map student-only labels (which carry ~20–25 m positional jitter per Obs 260 and would inflate match noise).
3. Decision rule cut-offs in this document must be committed prior to running step 5; treat any post-hoc adjustment as a protocol violation to be flagged in the paper.

## Risks and limitations

- **Single-condition pilot**: a sound result on text-T=0.7 does not guarantee soundness on image conditions or low-T deterministic conditions. The decision rule is condition-specific; if the pilot passes, the paper footnote should restrict the claim to the same condition family. A multi-condition extension is a natural follow-up.
- **K=30 is ceiling, not floor**: lower-K conditions (K=5, K=10) have coarser vote-fraction quantisation; the pilot result on K=30 is the best case. Plot vote-fraction-conditioned on K to characterise the K-dependence before generalising.
- **Cross-pass independence assumption**: vote-fraction interpretation as proxy probability assumes the K passes are roughly independent. At T=0.7 this is plausible; at T=0.0 the runs are deterministic and the proxy collapses to a binary indicator. The pilot must verify pass-pair Jaccard overlap is well below 1.0 before treating vote-fraction as a graded signal.
- **Class imbalance**: prevalence on the 487-tile corpus is ~20% image / ~12% text per Session 78 numbers; bins with very low FP counts may have unstable empirical P(TP). Wilson CIs (not raw rate ± 1.96·SE) are required.

## Cross-link to opt-in flag scoping (deliverable c)

If the pilot fails the decision rule (Spearman ρ < 0.5 or non-monotonic), escalate to `planning/detector-confidence-flag-scoping.md`. That document scopes three approaches (prompt augmentation, SDK logprobs, within-call multi-pass) for emitting a numeric per-detection confidence score directly from the proposer.
