# Buffer elasticity — verifier-calibration-matrix (5 m granularity)

**Generated**: 2026-04-27 (Wave 3 of Session 80, Theme 6).
**Source**: per-cell `evaluation.json` (Phase C, commit `fc7843158b04cbdd`, 2026-04-25).
**Buffers**: 5–50 m at 5 m granularity (10 buffers per cell).

This summary captures the F1 vs spatial-tolerance-buffer behaviour of the
14 verifier-prompt-variant cells in the post-PV verifier-calibration matrix.

## Monotonicity check

All 14 cells are F1-monotonic in buffer (no non-monotonicity at any 5 m step
on this corpus). Per the Obs 252 monotonicity assumption (which only had 10 m
granularity in the phase3a matrix), this is a useful confirmation.

## Per-cell F1 vs buffer

Image-track cells (verifier output on image-track proposer outputs); the canonical
post-PV operating buffer is 20 m.

| Cell | 5 m | 10 m | 15 m | 20 m | 25 m | 30 m | 35 m | 40 m | 45 m | 50 m | 20→50m elast |
|:---|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|
| image-adversarial | 0.1776 | 0.4752 | 0.6828 | 0.7866 | 0.8304 | 0.8651 | 0.8789 | 0.8858 | 0.8904 | 0.8950 | 13.8 % |
| image-adversarial-text | 0.1801 | 0.4716 | 0.6682 | 0.7725 | 0.8128 | 0.8460 | 0.8578 | 0.8649 | 0.8673 | 0.8697 | 12.6 % |
| image-brief | 0.1766 | 0.4725 | 0.6812 | 0.7844 | 0.8280 | 0.8624 | 0.8761 | 0.8830 | 0.8876 | 0.8922 | 13.7 % |
| image-brief-text | 0.1722 | 0.4665 | 0.6627 | 0.7679 | 0.8038 | 0.8397 | 0.8517 | 0.8565 | 0.8612 | 0.8636 | 12.5 % |
| image-checklist | 0.1768 | 0.4730 | 0.6797 | 0.7830 | 0.8266 | 0.8611 | 0.8749 | 0.8817 | 0.8863 | 0.8909 | 13.8 % |
| image-checklist-text | 0.1789 | 0.4715 | 0.6760 | 0.7805 | 0.8223 | 0.8571 | 0.8711 | 0.8780 | 0.8827 | 0.8873 | 13.7 % |
| image-comparative | 0.1774 | 0.4724 | 0.6820 | 0.7857 | 0.8295 | 0.8641 | 0.8779 | 0.8848 | 0.8894 | 0.8940 | 13.8 % |

Text-track cells (verifier output on text-track proposer outputs):

| Cell | 5 m | 10 m | 15 m | 20 m | 25 m | 30 m | 35 m | 40 m | 45 m | 50 m | 20→50m elast |
|:---|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|
| text-adversarial | 0.3081 | 0.7076 | 0.8375 | 0.8833 | 0.8977 | 0.9097 | 0.9097 | 0.9097 | 0.9097 | 0.9097 | 3.0 % |
| text-adversarial-text | 0.3045 | 0.6991 | 0.8210 | 0.8575 | 0.8721 | 0.8843 | 0.8843 | 0.8843 | 0.8843 | 0.8843 | 3.1 % |
| text-brief | 0.3048 | 0.7024 | 0.8310 | 0.8762 | 0.8905 | 0.9024 | 0.9024 | 0.9024 | 0.9024 | 0.9024 | 3.0 % |
| text-brief-text | 0.2917 | 0.6716 | 0.8039 | 0.8456 | 0.8578 | 0.8701 | 0.8701 | 0.8701 | 0.8701 | 0.8701 | 2.9 % |
| text-checklist | 0.3055 | 0.7041 | 0.8329 | 0.8783 | 0.8926 | 0.9045 | 0.9045 | 0.9045 | 0.9045 | 0.9045 | 3.0 % |
| text-checklist-text | 0.2969 | 0.6888 | 0.8147 | 0.8599 | 0.8741 | 0.8860 | 0.8860 | 0.8860 | 0.8860 | 0.8860 | 3.0 % |
| text-comparative | 0.3077 | 0.7091 | 0.8389 | 0.8846 | 0.8990 | 0.9111 | 0.9111 | 0.9111 | 0.9111 | 0.9111 | 3.0 % |

## Observations

1. **Image-track elasticity is ~4× text-track**: 12.5 – 13.8 % vs 2.9 – 3.1 %.
   This replicates the modality split observed at the pre-PV consensus stage
   (Obs 252) and confirms that the modality difference in spatial precision
   persists through the verifier.

2. **Text-track plateaus by 30 m**: F1 saturates at the 30 m buffer for all
   seven text-track variants — additional tolerance beyond 30 m yields zero
   incremental F1. By contrast, image-track continues to gain F1 monotonically
   through 50 m (post-50 m behaviour is not measured here).

3. **All 14 cells are monotonic in F1 vs buffer** at 5 m granularity. The
   monotonicity assumption underlying Obs 252's 8.6–21.5 % elasticity claim
   (phase3a consensus, 10 m granularity) holds at finer granularity in the
   post-verifier matrix.

4. **5 m and 10 m F1 are dramatically lower than 20 m+**: image-track at 5 m
   is 0.17–0.18 vs 0.78 at 20 m; text-track is 0.29–0.31 vs 0.86. The 5–10 m
   regime is below useful detection precision on this corpus and is included
   here only for completeness.

## See also

- Obs 252 (image-track has ~4× higher buffer elasticity than text — 10 m
  granularity in phase3a consensus).
- Obs 277 (verifier-prompt-variant calibration; canonical Pareto-dominant
  selection of `verify_adversarial-text`).
- `results/secondary-effects/secondary_effects.md` §6 (phase3a image-track
  buffer elasticity, 10 m granularity).
- `results/phase3a-text-matrix/secondary_effects.md` §6 (phase3a text-track
  buffer elasticity, 10 m granularity).
