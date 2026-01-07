# Multi-Scale Pilot: Preregistration Text

## Suggested Location

**Section 12: Future Directions** — add as subsection 12.2 or integrate into existing multi-scale discussion.

Alternatively, if there's a "Pre-Registration Calibration" or "Pilot Studies" section, this could go there.

---

## Text for Preregistration

### Option A: Brief (for Section 12 Future Directions)

> **12.2 Multi-Scale Fusion**
> 
> A calibration pilot (n=19 ground truth mounds, 10 regions) explored whether combining detections across tile sizes (256px, 512px, 1024px) improves performance. Point estimates suggest multi-scale fusion may offer substantial improvement over single-scale detection: the best multi-scale strategy (requiring agreement across all three scales) achieved F1=0.61 versus F1=0.49 for the best single-scale configuration (512px at 4/5 voting threshold).
> 
> However, bootstrap confidence intervals are wide due to limited ground truth (multi-scale: [0.28, 0.91]; single-scale: [0.14, 0.73]), and the intervals overlap substantially. Error correlation across scales was low (r = -0.18 to +0.13), supporting the theoretical basis for multi-scale fusion—the scales make independent errors, suggesting genuine complementary information.
> 
> Multi-scale fusion is designated as **exploratory future work** for Paper 2, pending validation on a larger ground truth set (target: 50+ mounds). The current study retains 512px single-scale detection as the primary methodology.

---

### Option B: Minimal (single paragraph)

> **Multi-Scale Fusion**: A calibration pilot explored combining detections across tile sizes. Point estimates favoured multi-scale (F1=0.61) over single-scale (F1=0.49), but wide confidence intervals due to limited ground truth (n=19) prevent definitive conclusions. Low error correlation across scales (r ≈ -0.1 to +0.1) supports the theoretical basis. Multi-scale fusion is designated as exploratory future work; the current study retains 512px single-scale detection.

---

### Option C: With methodology note (if more detail needed)

> **12.2 Multi-Scale Fusion**
> 
> A calibration pilot tested whether combining detections from multiple tile sizes improves performance. Three scales were tested on identical geographic coverage: 256px (160 tiles), 512px (40 tiles), and 1024px (10 tiles), each with K=5 detection passes.
> 
> **Results**: The best multi-scale strategy (scale confirmation requiring 3/3 agreement) achieved F1=0.61 [95% CI: 0.28–0.91] versus F1=0.49 [0.14–0.73] for single-scale (512px, 4/5 threshold). The +0.12 F1 improvement is promising but confidence intervals overlap substantially due to limited ground truth (n=19 mounds).
> 
> **Scale characteristics**: Small tiles (256px) provided high recall but low precision; large tiles (1024px) showed the opposite pattern with unacceptably low recall (37%). Error correlation across scales was low to negative (small-medium: r=-0.18; small-large: r=-0.09; medium-large: r=+0.13), indicating independent error patterns that support multi-scale fusion.
> 
> **Disposition**: Multi-scale fusion is designated as **exploratory analysis** for Paper 2, contingent on validation with a larger ground truth set. The current preregistration retains 512px single-scale detection as the confirmatory methodology.

---

## Notes for Integration

1. **Cross-reference**: If Section 12 already mentions multi-scale or tile size as future work, integrate rather than duplicate.

2. **Pilot data location**: Reference the archived pilot outputs:
   - `outputs/pilot/multiscale_analysis.json`
   - `outputs/pilot/multiscale_full_sweep.csv`
   - `results/multiscale-pilot-results.md` (detailed analysis)

3. **Version note**: If updating preregistration version, note this addition in the changelog.
