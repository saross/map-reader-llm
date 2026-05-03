# Future work — deferred items not in current paper scope

**Created**: 2026-05-03 (Session 85)
**Purpose**: Parking lot for items that have been spec'd or partially explored but
deliberately deferred from the current paper. Items here are *not* abandoned —
they have crisp scoping, but the cost-benefit case for landing them in the
current preregistered manuscript is weak. Each item lists the trigger condition
under which it should be revisited.

This file is the canonical register for "deferred to future work". When an item
is moved here from `paper-writeup-continuity.md`, update the continuity doc to
point to this file rather than carry the spec in two places.

---

## 1. Detector confidence (graded)

**Status**: Deferred 2026-05-03 (Session 85). Detailed specs preserved in their
own files; only the framing and trigger conditions are summarised here.

### Background

The proposer schema returns `{box_2d, label, subtype}` — no per-detection
numeric confidence (in contrast to the verifier's `mound_probability`). Two
related lines of work were spec'd to address this:

- **(b) Calibration pilot** for vote-fraction (`vote_count / K` from K
  independent passes) as a behavioural proxy for detector confidence — see
  `planning/detector-confidence-calibration-pilot.md`. Zero API cost; uses
  the existing K=30 cell on the 4-map gold-standard corpus.
- **(c) Opt-in flag scoping** for emitting a numeric per-detection confidence
  directly from the proposer (Option A: prompt augmentation; Option B: SDK
  logprobs; Option C: within-call multi-pass) — see
  `planning/detector-confidence-flag-scoping.md`. Recommendation in that
  doc is to defer all three options.

### Why deferred from the current paper

1. **Vote-fraction-as-proxy was never executed**. Without the calibration
   pilot, the project cannot make a calibrated claim about detector confidence
   in the manuscript. Running the pilot now would expand scope at the
   outline-and-write phase rather than the experiment phase.
2. **Verifier `mound_probability` is the operative confidence signal in the
   paper**. Obs 269 (verifier ECE 0.27, AUC 0.65 on 55-map) and Obs 277
   (verifier ECE 0.18 on 4-map gold-standard, no prompt variant clears
   ECE < 0.10) characterise its calibration. The paper can discuss the
   verifier signal as the project's confidence quantity without needing
   detector-side confidence.
3. **The paper makes no graded-confidence claim** that requires either deliverable
   to support. The leaderboard, cross-track comparisons, and hypothesis tests
   all use binary detection sets (post-threshold, post-consensus), not
   continuous confidence ranks.
4. **Deliverable (c) carries non-trivial engineering risk**. Option A (prompt
   augmentation) is the cheapest path but Obs 269 / 277 evidence suggests
   self-reported VLM confidence is unlikely to be better-calibrated than
   vote-fraction. Options B and C have material capability uncertainty on
   the current Gemini API.

### Items deferred (originally items #4 + #6 in `paper-writeup-continuity.md`)

#### #4 Detector-confidence calibration pilot (vote-fraction-as-proxy validation)

- **Source**: `planning/detector-confidence-calibration-pilot.md`
- **Test**: Spearman ρ between `vote_count` and observed P(TP) on the
  4-map gold-standard K=30 cell. ρ ≥ 0.7 → proxy sound (paper-reportable);
  ρ < 0.5 → proxy unreliable (escalate to deliverable c).
- **Cost**: ~1 hour compute; $0 API.
- **Cross-reference**: H-a (Obs 283).

#### #6 Multi-condition vote-fraction calibration extension

- **Source**: `planning/detector-confidence-calibration-pilot.md` line 92.
- **Description**: A single-condition pilot (#4) does not guarantee
  vote-fraction soundness on image conditions or low-T deterministic regimes.
  Multi-condition extension would characterise K-dependence and
  condition-family generality.
- **Cost**: 2–4 hours per condition; varies.
- **Pre-condition**: #4 pilot passes.

### Triggers for revisiting

Revisit deliverables (b) and (c) when **any** of the following hold:

1. A follow-up paper or manuscript revision needs to discuss detector
   confidence as a graded quantity (e.g. for downstream practitioner
   prioritisation, active-learning loops, or per-detection uncertainty
   communication).
2. Reviewer feedback on the current manuscript specifically requests a
   per-detection confidence signal that the verifier `mound_probability`
   cannot provide (e.g. for very-low-confidence FP gating without verifier
   re-runs).
3. The Gemini API ships well-supported `response_logprobs` on the proposer
   surfaces in use (Flash + Pro, real-time + batch), making Option B
   substantially cheaper to implement than the current scoping suggests.
4. A new dataset or task surfaces where the existing K-pass infrastructure
   is impractical (e.g. K=1 production runs at scale) and a within-call
   confidence signal becomes load-bearing.

### Detailed specs (do not duplicate here)

- Calibration pilot: `planning/detector-confidence-calibration-pilot.md`
- Opt-in flag scoping: `planning/detector-confidence-flag-scoping.md`

Both specs remain valid; revisit them as the starting point if any trigger
condition fires.

---

## Adding new items to this register

When an item is moved here from the continuity doc:

1. Add a top-level section to this file with: **Status**, **Background**,
   **Why deferred from the current paper**, **Items deferred**,
   **Triggers for revisiting**, and **Detailed specs** (cross-references
   only — do not duplicate spec content).
2. Update `paper-writeup-continuity.md` to mark the corresponding items
   as "DEFERRED to `planning/future-work.md` § <section>" rather than
   leaving them in the active to-do register.
3. Preserve the original detailed specs in their existing files; this
   document is a register, not a replacement.
