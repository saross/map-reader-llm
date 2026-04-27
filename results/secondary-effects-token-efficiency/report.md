# Per-Condition Token Efficiency Analysis

Generated: 2026-04-27T04:46:03+00:00  
Script: `scripts/analyse_token_efficiency.py` v1.0.0

## Headline Question

Was HIGH thinking worth its token spend? We compute **ΔF1 per 1k thinking tokens** as a paired HIGH-vs-MIN metric at each temperature (where HIGH thinking data is available). Per-call denominators use ``request_count`` from ``usage_stats.by_provider.google_gemini``. Runs with ``total_input_tokens == 0`` are filtered out as batch-API logged-zero artefacts; K reported is filtered/total.

## Logged-zero Artefact (footnote §15)

The Google Async Batch API records an empty ``usage_stats`` block (input, output, AND thinking all zero) for completed submissions, even when the underlying calls used real tokens. Affected conditions in this analysis are HIGH-T0.7 and MIN-T0.7 in both tracks. We do not impute; we filter and footnote. The Phase 3a 487-tile retest meta files at ``outputs/retest/phase3a/.../detections_T*_run*.meta.json`` are also entirely batch-API and therefore not used as a token-data source — the canonical real-time meta files at ``outputs/h11/pv-diag-384/...`` are the correct source.

## Per-Stratum Tables

### Image-track Phase 3a 487-tile matrix

| Condition | K (filt/total) | mean in/call | mean out/call | mean think/call | F1 | n det | tokens/det | tokens/F1 | ΔF1/1k-think (vs paired-T MIN) |
|-----------|----------------|--------------|---------------|------------------|-------|-------|------------|-----------|-------------------------------|
| HIGH-T0.0 | 3/3 | 15,659 | 175 | 4,056 | 0.4883 | 802 | 19,833 | 32,573,875 | -0.0347 |
| HIGH-T0.3 | 10/10 | 15,659 | 133 | 2,387 | 0.7312 | 361 | 213,040 | 105,179,602 | 0.0300 |
| HIGH-T0.7 | 0/10 | — | — | — | 0.7500 | 405 | — | — | NA — logged-zero artefact |
| HIGH-T1.0 | 10/10 | 15,659 | 138 | 1,900 | 0.7350 | 433 | 177,672 | 104,669,571 | 0.0469 |
| MIN-T0.0 | 3/3 | 15,659 | 106 | 0 (by design — MINIMAL doesn't think) | 0.6290 | 681 | 33,823 | 36,618,765 | — |
| MIN-T0.3 | 10/10 | 15,659 | 114 | 0 (by design — MINIMAL doesn't think) | 0.6597 | 517 | 148,581 | 116,441,616 | — |
| MIN-T0.7 | 0/10 | — | — | — | 0.6803 | 494 | — | — | — |
| MIN-T1.0 | 10/10 | 15,659 | 116 | 0 (by design — MINIMAL doesn't think) | 0.6459 | 466 | 164,864 | 118,944,944 | — |
| SCALE4-T0.7 | 10/10 | 15,659 | 119 | 1,829 | 0.7422 | 403 | 190,669 | 103,529,718 | 0.0338 |

### Text-track Phase 3a 487-tile matrix

| Condition | K (filt/total) | mean in/call | mean out/call | mean think/call | F1 | n det | tokens/det | tokens/F1 | ΔF1/1k-think (vs paired-T MIN) |
|-----------|----------------|--------------|---------------|------------------|-------|-------|------------|-----------|-------------------------------|
| HIGH-T0.0 | 3/3 | 1,497 | 159 | 3,993 | 0.6051 | 745 | 3,247 | 3,998,152 | 0.0030 |
| HIGH-T0.3 | 10/10 | 1,502 | 181 | 3,188 | 0.7891 | 409 | 20,038 | 10,386,046 | 0.0460 |
| HIGH-T0.7 | 0/30 | — | — | — | 0.8141 | 415 | — | — | NA — logged-zero artefact |
| HIGH-T1.0 | 10/10 | 1,502 | 203 | 2,487 | 0.7727 | 414 | 20,053 | 10,744,300 | 0.0426 |
| MIN-T0.0 | 3/3 | 1,502 | 137 | 0 (by design — MINIMAL doesn't think) | 0.5932 | 799 | 2,997 | 4,037,306 | — |
| MIN-T0.3 | 10/10 | 1,502 | 139 | 0 (by design — MINIMAL doesn't think) | 0.6424 | 608 | 13,146 | 12,442,483 | — |
| MIN-T0.7 | 0/30 | — | — | — | 0.6611 | 530 | — | — | — |
| MIN-T1.0 | 10/10 | 1,502 | 146 | 0 (by design — MINIMAL doesn't think) | 0.6667 | 549 | 14,616 | 12,035,625 | — |

## Paired HIGH-vs-MIN Comparisons

### Image-track paired HIGH-vs-MIN comparisons

| HIGH | MIN | F1_HIGH | F1_MIN | ΔF1 | Δthink/call | ΔF1/1k-think | Status |
|------|-----|---------|--------|------|-------------|--------------|--------|
| HIGH-T0.0 | MIN-T0.0 | 0.4883 | 0.6290 | -0.1407 | 4,056 | -0.0347 | OK |
| HIGH-T0.3 | MIN-T0.3 | 0.7312 | 0.6597 | 0.0715 | 2,387 | 0.0300 | OK |
| HIGH-T0.7 | MIN-T0.7 | 0.7500 | 0.6803 | — | — | — | NA — logged-zero artefact |
| HIGH-T1.0 | MIN-T1.0 | 0.7350 | 0.6459 | 0.0891 | 1,900 | 0.0469 | OK |
| SCALE4-T0.7 | MIN-T0.7 | 0.7422 | 0.6803 | 0.0619 | 1,829 | 0.0338 | OK |

### Text-track paired HIGH-vs-MIN comparisons

| HIGH | MIN | F1_HIGH | F1_MIN | ΔF1 | Δthink/call | ΔF1/1k-think | Status |
|------|-----|---------|--------|------|-------------|--------------|--------|
| HIGH-T0.0 | MIN-T0.0 | 0.6051 | 0.5932 | 0.0119 | 3,993 | 0.0030 | OK |
| HIGH-T0.3 | MIN-T0.3 | 0.7891 | 0.6424 | 0.1467 | 3,188 | 0.0460 | OK |
| HIGH-T0.7 | MIN-T0.7 | 0.8141 | 0.6611 | — | — | — | NA — logged-zero artefact |
| HIGH-T1.0 | MIN-T1.0 | 0.7727 | 0.6667 | 0.1060 | 2,487 | 0.0426 | OK |

### Discussion

HIGH thinking is not uniformly worth its token spend. On the image-track 487-tile matrix, the paired ΔF1-per-1k-thinking-tokens metric is negative at T=0.0 (-0.0347), indicating that switching from MINIMAL to HIGH thinking at deterministic decoding actively *cost* F1 — most likely because MIN-T0.0 already saturates recall while HIGH-T0.0 over-thinks and hurts precision. At T=0.3 (0.0300) and T=1.0 (0.0469) the sign flips: HIGH buys extra F1, though at substantial token cost. SCALE4-T0.7 — the only non-batch HIGH-T0.7 image evidence — yields a positive efficiency of 0.0338, consistent with the diversity dividend from richer prompt scaffolding seen elsewhere in the matrix. The text-track tells a *different* story at T=0.0: efficiency is barely positive (0.0030), not negative — ΔF1 is essentially flat (~0.012) so HIGH thinking is wasted but not actively damaging. At higher temperatures the text-track agrees with image (T=0.3: 0.0460; T=1.0: 0.0426). HIGH-T0.7 in both tracks is logged-zero (batch-API ``usage_stats`` artefact) and cannot be compared. The headline negative number at T=0.0 in the image track is the single-line answer for that modality: HIGH thinking at deterministic decoding is a strict loss when the model can see images, but only a wasted spend (not a loss) on text-only inputs.
