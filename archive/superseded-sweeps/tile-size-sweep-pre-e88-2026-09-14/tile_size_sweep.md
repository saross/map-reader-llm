# Tile-size sweep — 256 / 384 / 512 px (F1@20 m) — `tile-size-sweep`

- **Metric**: micro-average F1 @ 20 m (cross-size comparable); MCC per size (NOT differenced).
- **Tile counts**: 256→1032, 384→487, 512→340 (different tilings of the same 4 GS maps + curator GT).
- **Caveats**: 256 px anchor (pv-diag-256) is text-only, thin proposer provenance (temp/thinking not materialised; 1032-tile scope). 256 px consensus+verifier IS now tested (Stage-D, Obs 352, View 3: F1 0.856); its proposer is the plain text 5-of-5 (N=5) family, whereas 384/512 share the HIGH-text N=30 lineage (HIGH-text was not run at 256), so the 256 PV cell is its own thin-provenance anchor. image HIGH-thinking consensus exists at 384 but not 512 (phase3a-high image track never ran).

## View 1a — single-pass clean isolation (flash minimal; vary only tile size)

| modality | temp | 256 | 384 | 512 | direction |
|---|---|---:|---:|---:|---|
| text | 0.0 | 0.342 | 0.520 | 0.606 | best=512px (Δ+0.264 over 256→512) |
| text | 0.7 | — | 0.488 | 0.584 | best=512px (Δ+0.096 over 384→512) |
| image | 0.0 | — | 0.600 | 0.586 | flat (384≈512) |
| image | 0.7 | — | 0.553 | 0.537 | best=384px (Δ-0.017 over 384→512) |

## View 1b — consensus clean isolation (best-F1 op-point per size; vote scales with size)

| modality | thinking | temp | 256 | 384 | 512 | direction |
|---|---|---|---:|---:|---:|---|
| text | minimal | 0.3 | — | 0.642 | 0.692 | best=512px (Δ+0.050 over 384→512) |
| text | minimal | 0.7 | — | 0.661 | 0.703 | best=512px (Δ+0.042 over 384→512) |
| text | minimal | 1.0 | — | 0.667 | 0.686 | best=512px (Δ+0.019 over 384→512) |
| text | high | 0.3 | — | 0.789 | 0.774 | flat (384≈512) |
| text | high | 0.7 | — | 0.814 | 0.773 | best=384px (Δ-0.041 over 384→512) |
| text | high | 1.0 | — | 0.773 | 0.775 | flat (384≈512) |
| image | minimal | 0.3 | — | — | 0.666 | single-size |
| image | minimal | 0.7 | — | — | 0.691 | single-size |
| image | minimal | 1.0 | — | — | 0.679 | single-size |
| image | high | 0.3 | — | 0.731 | — | single-size |
| image | high | 0.7 | — | 0.750 | — | single-size |
| image | high | 1.0 | — | 0.735 | — | single-size |

## View 3 — consensus+PV matched (Stage-D head-to-head; carry-forward verifier)

Consensus champion VERIFIED with the production adversarial verifier (gemini-3-flash, verify_adversarial-text, T=0.0, minimal, n=1), scored at 14-buffer + tile-MCC, best-F1@20 m operating point per size.

| modality | arch | 256 | 384 | 512 | direction |
|---|---|---:|---:|---:|---|
| text | consensus+PV | 0.856 | 0.890 | 0.792 | best=384px (Δ-0.063 over 256→512) |

## View 2 — best-achievable FLASH ceiling per (size × architecture × modality)

Model-matched (gemini-3-flash) so the ceilings compare tile size, not model.

| size | architecture/modality | best cell | F1@20m | MCC |
|---:|---|---|---:|---:|
| 512 | consensus/image | `image-t0.7-n30-18of30` | 0.691 | 0.442 |
| 512 | consensus/text | `text-high-t1.0-n30-23of30` | 0.775 | 0.642 |
| 512 | proposer-verifier/image | `verified-adv-image-t0.7-n30-18of30` | 0.728 | 0.785 |
| 512 | proposer-verifier/text | `verified-adv-text-high-t1.0-n30-23of30` | 0.792 | 0.676 |
| 512 | single-pass/image | `image-terse` | 0.605 | 0.224 |
| 512 | single-pass/text | `canonical-last` | 0.631 | 0.213 |
| 384 | consensus/image | `flash-high-image-n5-image-t0.7-consensus-7of10` | 0.750 | 0.678 |
| 384 | consensus/text | `flash-high-text-n5-text-t0.7-consensus-26of30` | 0.814 | 0.620 |
| 384 | proposer-verifier/text | `verified-adv-text-consensus-16of30` | 0.890 | 0.790 |
| 384 | single-pass/image | `baseline-flash-image-minimal-t-0-0` | 0.600 | 0.312 |
| 384 | single-pass/text | `baseline-flash-text-minimal-t-0-0-pv-baseline` | 0.520 | -0.004 |
| 256 | consensus/text | `text-consensus-5of5` | 0.460 | 0.153 |
| 256 | proposer-verifier/text | `verified-adv-text-consensus-5of5` | 0.856 | 0.745 |
| 256 | single-pass/text | `text-baseline` | 0.342 | 0.088 |

**Pro note** (genuine Gemini-3 Pro ran ONLY at 384 px — shown for context, not a tile-size comparison):

| size/arch/modality | cell | F1@20m | MCC |
|---|---|---:|---:|
| 384/single-pass/image | `baseline-pro-image-medium-t-0-0` | 0.655 | 0.868 |
| 384/single-pass/text | `baseline-pro-text-medium-t-0-0` | 0.792 | 0.790 |
