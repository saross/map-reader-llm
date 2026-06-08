# Tile-size sweep — 256 / 384 / 512 px (F1@20 m) — `tile-size-sweep`

- **Metric**: micro-average F1 @ 20 m (cross-size comparable); MCC per size (NOT differenced).
- **Tile counts**: 256→1032, 384→487, 512→340 (different tilings of the same 4 GS maps + curator GT).
- **Caveats**: 256 px anchor (pv-diag-256) is text-only, thin proposer provenance (temp/thinking not materialised; 1032-tile scope). 256 px consensus is consensus-only (no verifier); the decisive 256 consensus+verifier cell is untested (Obs 351). image HIGH-thinking consensus exists at 384 but not 512 (phase3a-high image track never ran).

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

## View 2 — best-achievable FLASH ceiling per (size × architecture × modality)

Model-matched (gemini-3-flash) so the ceilings compare tile size, not model.

| size | architecture/modality | best cell | F1@20m | MCC |
|---:|---|---|---:|---:|
| 512 | consensus/image | `image-t0.7-n30-18of30` | 0.691 | 0.442 |
| 512 | consensus/text | `text-high-t1.0-n30-23of30` | 0.775 | 0.642 |
| 512 | single-pass/image | `image-terse` | 0.605 | 0.224 |
| 512 | single-pass/text | `canonical-last` | 0.631 | 0.213 |
| 384 | consensus/image | `flash-high-image-n5-image-t0.7-consensus-7of10` | 0.750 | 0.678 |
| 384 | consensus/text | `flash-high-text-n5-text-t0.7-consensus-26of30` | 0.814 | 0.620 |
| 384 | single-pass/image | `baseline-flash-image-minimal-t-0-0` | 0.600 | 0.312 |
| 384 | single-pass/text | `baseline-flash-text-minimal-t-0-0-pv-baseline` | 0.520 | -0.004 |
| 256 | consensus/text | `text-consensus-5of5` | 0.460 | 0.153 |
| 256 | single-pass/text | `text-baseline` | 0.342 | 0.088 |

**Pro note** (genuine Gemini-3 Pro ran ONLY at 384 px — shown for context, not a tile-size comparison):

| size/arch/modality | cell | F1@20m | MCC |
|---|---|---:|---:|
| 384/single-pass/image | `baseline-pro-image-medium-t-0-0` | 0.655 | 0.868 |
| 384/single-pass/text | `baseline-pro-text-medium-t-0-0` | 0.792 | 0.790 |
