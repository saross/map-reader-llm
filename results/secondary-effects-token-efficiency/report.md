# Per-Condition Token Efficiency Analysis

Generated: 2026-04-27T04:46:03+00:00  
Script: `scripts/analyse_token_efficiency.py` v1.0.0  
Git commit at run time: `0e337f83`  
Primary observation: **Obs 284** (headline) in `docs/notes/reflections/working-notes.md`  
Generalisation observation: **Obs 297** (out-of-sample at 55-map scope)

## 1. Executive summary

HIGH thinking is **not uniformly worth its token spend**. The paired ΔF1-per-1k-thinking-tokens metric (HIGH vs MIN at matched temperature) shows a sharp **modality divergence at deterministic decoding (T = 0.0)**:

- **Image track, HIGH-T0.0 vs MIN-T0.0: −0.0347 ΔF1 / 1k thinking tokens** — switching from MINIMAL to HIGH at deterministic image decoding *actively cost* 14.07 percentage points of F1 (0.4883 vs 0.6290) for a spend of 4,056 thinking tokens per call. This is a **strict loss**, not a wasted spend.
- **Text track, HIGH-T0.0 vs MIN-T0.0: +0.0030 ΔF1 / 1k thinking tokens** — barely positive, ΔF1 essentially flat (~0.012). HIGH thinking is **wasted but not actively damaging** on text-only inputs.
- At T = 0.3 and T = 1.0 across both tracks, the sign flips and HIGH buys extra F1 at substantial token cost: efficiency ranges +0.0300 to +0.0469. This is the **diversity-dividend regime** (Obs 140 / 141).
- The single-line answer for the image track at deterministic decoding: HIGH thinking is a strict loss when the model can see images. On text-only inputs at the same condition, it is merely wasted spend.

The headline negative number at T = 0.0 image is the most paper-quotable per-token result we have for the in-sample 4-map matrix. See **§7 Cross-references** for how this in-sample finding is reconciled with Obs 297's out-of-sample 55-map result that HIGH thinking *does* earn its tokens at production decoding temperatures (T = 0.7).

## 2. Headline Question

Was HIGH thinking worth its token spend? We compute **ΔF1 per 1k thinking tokens** as a paired HIGH-vs-MIN metric at each temperature (where HIGH thinking data is available). Per-call denominators use ``request_count`` from ``usage_stats.by_provider.google_gemini``. Runs with ``total_input_tokens == 0`` are filtered out as batch-API logged-zero artefacts; K reported is filtered/total.

## 3. Logged-zero Artefact (footnote §15)

The Google Async Batch API records an empty ``usage_stats`` block (input, output, AND thinking all zero) for completed submissions, even when the underlying calls used real tokens. Affected conditions in this analysis are HIGH-T0.7 and MIN-T0.7 in both tracks. We do not impute; we filter and footnote. The Phase 3a 487-tile retest meta files at ``outputs/retest/phase3a/.../detections_T*_run*.meta.json`` are also entirely batch-API and therefore not used as a token-data source — the canonical real-time meta files at ``outputs/h11/pv-diag-384/...`` are the correct source.

## 4. Per-Stratum Tables

### 4.1 Image-track Phase 3a 487-tile matrix

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

### 4.2 Text-track Phase 3a 487-tile matrix

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

## 5. Paired HIGH-vs-MIN Comparisons

### 5.1 Image-track paired HIGH-vs-MIN comparisons

| HIGH | MIN | F1_HIGH | F1_MIN | ΔF1 | Δthink/call | ΔF1/1k-think | Status |
|------|-----|---------|--------|------|-------------|--------------|--------|
| HIGH-T0.0 | MIN-T0.0 | 0.4883 | 0.6290 | -0.1407 | 4,056 | -0.0347 | OK |
| HIGH-T0.3 | MIN-T0.3 | 0.7312 | 0.6597 | 0.0715 | 2,387 | 0.0300 | OK |
| HIGH-T0.7 | MIN-T0.7 | 0.7500 | 0.6803 | — | — | — | NA — logged-zero artefact |
| HIGH-T1.0 | MIN-T1.0 | 0.7350 | 0.6459 | 0.0891 | 1,900 | 0.0469 | OK |
| SCALE4-T0.7 | MIN-T0.7 | 0.7422 | 0.6803 | 0.0619 | 1,829 | 0.0338 | OK |

### 5.2 Text-track paired HIGH-vs-MIN comparisons

| HIGH | MIN | F1_HIGH | F1_MIN | ΔF1 | Δthink/call | ΔF1/1k-think | Status |
|------|-----|---------|--------|------|-------------|--------------|--------|
| HIGH-T0.0 | MIN-T0.0 | 0.6051 | 0.5932 | 0.0119 | 3,993 | 0.0030 | OK |
| HIGH-T0.3 | MIN-T0.3 | 0.7891 | 0.6424 | 0.1467 | 3,188 | 0.0460 | OK |
| HIGH-T0.7 | MIN-T0.7 | 0.8141 | 0.6611 | — | — | — | NA — logged-zero artefact |
| HIGH-T1.0 | MIN-T1.0 | 0.7727 | 0.6667 | 0.1060 | 2,487 | 0.0426 | OK |

## 6. Discussion

HIGH thinking is not uniformly worth its token spend. On the image-track 487-tile matrix, the paired ΔF1-per-1k-thinking-tokens metric is negative at T=0.0 (-0.0347), indicating that switching from MINIMAL to HIGH thinking at deterministic decoding actively *cost* F1 — most likely because MIN-T0.0 already saturates recall while HIGH-T0.0 over-thinks and hurts precision. At T=0.3 (0.0300) and T=1.0 (0.0469) the sign flips: HIGH buys extra F1, though at substantial token cost. SCALE4-T0.7 — the only non-batch HIGH-T0.7 image evidence — yields a positive efficiency of 0.0338, consistent with the diversity dividend from richer prompt scaffolding seen elsewhere in the matrix. The text-track tells a *different* story at T=0.0: efficiency is barely positive (0.0030), not negative — ΔF1 is essentially flat (~0.012) so HIGH thinking is wasted but not actively damaging. At higher temperatures the text-track agrees with image (T=0.3: 0.0460; T=1.0: 0.0426). HIGH-T0.7 in both tracks is logged-zero (batch-API ``usage_stats`` artefact) and cannot be compared. The headline negative number at T=0.0 in the image track is the single-line answer for that modality: HIGH thinking at deterministic decoding is a strict loss when the model can see images, but only a wasted spend (not a loss) on text-only inputs.

## 7. Cross-references — resolving the apparent paradox

The in-sample 4-map per-token finding (this report; Obs 284) and the out-of-sample 55-map paired-permutation finding (Obs 297) appear to disagree about whether HIGH thinking is "worth it". They are reconciled by recognising that they answer **different questions** at **different scopes**:

### 7.1 Obs 284 — in-sample, per-token, deterministic regime included

This report's headline. On the 4-map Phase 3a 487-tile matrix:

- HIGH thinking has **negative per-token efficiency at T = 0.0 image** (−0.0347 ΔF1 / 1k thinking tokens; ΔF1 = −0.1407 absolute).
- HIGH thinking has **positive per-token efficiency at T ∈ {0.3, 1.0}** in both tracks (+0.0300 to +0.0469).
- The mechanism (Obs 140 / 141): HIGH's F1 advantage comes from output diversity that consensus voting can exploit; at T = 0.0 there is no diversity to exploit, so HIGH only adds token cost — and on the image track also adds precision-hurting elaboration (Obs 244: HIGH-T0.0 image retains only 89.5 % unanimous detections vs MIN-T0.0's 97.8 %).

### 7.2 Obs 297 — out-of-sample, paired-permutation, production temperatures only

The 55-map paired-permutation v2 analysis on the four manually-corrected runs at canonical buffer R = 50 m:

| Pair | ΔF1 (mean) | 95 % CI | BH-FDR p | Significant? |
|:---|:--:|:--:|:--:|:--:|
| T=0.3 vs T=MIN | **+0.0473** | [+0.0379, +0.0568] | < 0.001 | yes |
| T=0.7 vs T=MIN | **+0.0296** | [+0.0200, +0.0392] | < 0.001 | yes |
| image vs T=MIN | **+0.0353** | [+0.0245, +0.0464] | < 0.001 | yes |

T=MIN sits at the bottom of all four corrected 55-map runs at every buffer R ≥ 25 m. The out-of-sample answer at production decoding temperatures is unambiguous: **HIGH thinking earns its tokens at 55-map scope.**

### 7.3 Resolution

There is no contradiction. The diversity-dividend mechanism (Obs 140 / 141) predicts exactly this pattern:

1. **At T = 0.0 (deterministic decoding)** — no diversity is generated for consensus to filter. HIGH thinking only adds token cost; on the image track it actively hurts F1. This is Obs 284's regime and this report's headline.
2. **At production T ∈ {0.3, 0.7, 1.0}** — diversity is generated and consensus voting exploits it. HIGH thinking earns its tokens both in-sample (Obs 284) and out-of-sample at scale (Obs 297).

The paper's load-bearing claim is the second: HIGH thinking is justified at production temperatures, with the per-token efficiency framing of this report explaining *why* (the diversity-dividend mechanism) and the deterministic-decoding regime explicitly carved out as the exception.

## 8. Paper implications — token efficiency as model-cost/value framing

This report supplies the **per-token cost/value trade-off framing** for the paper's HIGH-vs-MIN comparison. Recommended use:

1. **Methods — HIGH-vs-MIN justification**: "HIGH-thinking premium is justified by the diversity-dividend mechanism documented out-of-sample at 55-map scope (T = 0.7 vs T = MIN ΔF1 = +0.0296, BH-FDR p < 0.001; Obs 297) and not by per-token efficiency at deterministic decoding (T = 0.0 image = −0.0347 ΔF1 / 1k thinking tokens; this report)." This makes the regime-conditionality of the claim explicit.
2. **Methods — deterministic-decoding caveat**: cite the −0.0347 figure when explaining *why the production pipeline does not use T = 0.0*. The choice of T > 0 is not arbitrary; it is the regime where HIGH thinking is empirically worth its tokens.
3. **Methods — modality framing**: text-track HIGH-T0.0 is wasted (+0.0030, ~0 ΔF1) but not damaging; image-track HIGH-T0.0 is a strict loss (−0.0347, −0.1407 ΔF1). The asymmetry supports the broader paper claim that vision-input failure modes are mechanistically distinct from text-input failure modes (see also Obs 252 buffer elasticity, Obs 259 thinking-budget asymmetry).
4. **Cost transparency table (suggested)**: a paper-figure variant of §4.1 / §4.2 with three columns — F1, mean thinking tokens per call, ΔF1 per 1k thinking tokens — gives readers a one-glance read on cost-effectiveness across the matrix. The headline cells are HIGH-T0.0 image (negative) and the SCALE4-T0.7 image cell (the only non-batch HIGH-T0.7 image evidence; +0.0338).
5. **Quoted cell for the text**: "HIGH thinking at deterministic image decoding cost 14.07 percentage points of F1 for a spend of 4,056 thinking tokens per call (ΔF1 / 1k think = −0.0347); the same comparison on text-only inputs was effectively flat (+0.0030 ΔF1 / 1k think)."

The paper Methods section can cite this report as the cost side of the HIGH-vs-MIN comparison; Obs 297 supplies the value side at production scope.

## 9. Reproducibility

- **Script**: `scripts/analyse_token_efficiency.py` v1.0.0 (ruff-clean).
- **Git commit at run time**: `0e337f83`.
- **Random seed**: not applicable — this analysis is a deterministic per-call aggregation (no bootstrap, no Monte Carlo). Re-running the script against the same inputs produces byte-identical outputs.
- **Bootstrap iterations**: not applicable (no resampling step).
- **Compute**: ~5 seconds wall-clock on amd-tower (light I/O over `.meta.json` files; no heavy compute). No need for sapphire offload.
- **Filter rule**: drop runs where `total_input_tokens == 0` (Google Async Batch API logged-zero artefact; see §3 / §15).
- **Per-call denominator**: `usage_stats.by_provider.google_gemini.request_count`.
- **F1 sources**: `results/secondary-effects/secondary_effects.json` (image), `results/phase3a-text-matrix/secondary_effects.json` (text). Greedy at optimal vote_t, 20 m buffer.
- **Per-call meta files**: `outputs/h11/pv-diag-384/<condition>/run_*/*.meta.json` (canonical real-time meta files; not the batch-API retest meta files at `outputs/retest/phase3a/`).
- **Re-run command** (from the repo root):

  ```bash
  python scripts/analyse_token_efficiency.py \
      --output-dir results/secondary-effects-token-efficiency/
  ```
