---
title: "Methods / Limitations note — curator ground truth as high-quality-but-not-complete reference"
date: 2026-05-03
session: 85
intended_paper_section: Methods (single sentence) + Limitations (paragraph)
source_continuity_doc: "planning/paper-writeup-continuity.md § 'Additional backlog captured during Session 84 close-out review' (B7)"
---

# Methods / Limitations note — curator GT incompleteness

## Context

Two reference-mound files anchor the project's evaluation pipeline:

- **`inputs/vectors/references/mounds-reference.geojson`** — the 4-map gold-standard reference, curator-corrected after triple-review. The canonical reference for GS-corpus evaluation.
- **`inputs/vectors/references/student-mounds-55maps-reviewed.geojson`** — the 55-map student-digitised reference, used as the practitioner-equivalent ground truth for the 55-map generalisation corpus.

Both are described in the manuscript's Methods as the authoritative ground-truth references. Today's session work surfaced two specific cases that demonstrate the curator GT is **not complete at the per-mound level**:

| Case | Sheet | Mechanism | Resolution |
|:---|:---|:---|:---|
| cand 4264 | K-35-064-3 | Second of two touching mounds — visually merged with a curator-listed mound; missed during digitisation. | Added to `student-mounds-55maps-reviewed.geojson` at commit `baf1497a` (Session 83). Curator GT now at 4,745 features. |
| cand 2397 | K-35-062-4 | Isolated mound in a region the curator review pass had not reached. | Added at commit `2e075eb9` (Session 84). Curator GT now at 4,746 features. |

Both were detected by the model and surfaced through the corrected-F1 review pipeline: a candidate the model placed at a real-mound location was reviewed, the reviewer recognised a real mound that the curator GT had not listed, and the candidate was promoted from FP to a phantom-GT-mound entry in the extended-GT-at-R Hungarian matching (Approach B).

## Implications

These two cases are not isolated bugs — they reflect a structural property of the reference data:

1. **Curator GT is high-quality but not complete at the per-mound level.** Triple-review reduces but does not eliminate per-mound omissions. The omissions are typically in two regimes:
   - **Boundary cases**: visually-merged or touching mounds, where the curator may digitise one feature and miss the second.
   - **Coverage gaps**: regions the curator reviewer did not reach during a pass (especially on student GT, where coverage varies map-by-map per the inter-student-skill variance documented in Obs 317).
2. **The corrected-F1 pipeline catches some curator omissions but not all.** Approach B (extended-GT-at-R Hungarian matching) promotes a candidate to a phantom-GT mound when (a) the model detected it, AND (b) the human reviewer confirmed it during the corrected-F1 review pass. This catches model-detected curator omissions but cannot catch curator omissions in regions the model also failed to detect (the "we don't know what we don't know" residual).
3. **Cross-corpus implications differ**:
   - On the 4-map GS corpus, the curator-corrected reference has been triple-reviewed; per-mound omission rate is plausibly very low. Today's cases were on the 55-map corpus, not GS.
   - On the 55-map corpus, the student-digitised reference has not been triple-reviewed (each map is digitised by one student; per Obs 317 the within-corpus per-map FN rate ranges 2.76–9.18 %, dominated by inter-student-skill variance). The per-mound omission rate is likely materially higher than for GS.
4. **Effect on reported metrics**: the two GT-additions during today's sessions shifted F1 by < 0.0005 absolute on cross-track comparisons (single-mound additions on a 4,745-feature reference). The cumulative shift across the project's complete recovery arc, including the prior cand 4264 and 2397 additions, is below the 0.005 absolute paper-claim sensitivity threshold. **No headline numbers in the manuscript are sensitive to these specific corrections.** The Limitations note exists to acknowledge the structural property, not to flag a specific numerical concern.

## Suggested paper-text placement

### Methods (single sentence, in the Ground Truth subsection)

> The 4-map gold-standard reference has been triple-reviewed by the curator; the 55-map student-digitised reference has been reviewed once per map by independent student annotators. Both references are treated as high-quality but not strictly complete: per-mound omissions are possible at the boundary of visually-merged mounds or in regions a single review pass did not reach.

### Limitations (paragraph)

> A consequence of treating the curator GT as the evaluation reference is that any mound the curator did not list, but the model detected, is recorded as a False Positive — even when subsequent human review confirms the model was correct. Approach B (extended-GT-at-R Hungarian matching) corrects for this on the subset of model-detected candidates that were also human-reviewed: such candidates are promoted to phantom GT mounds and the F1 / precision / recall figures the manuscript reports are *corrected* values that include these promotions. The pipeline cannot, however, correct for curator omissions in regions the model itself failed to detect; the residual under-counting on this axis is bounded by the model's recall on the corpus and is plausibly small in absolute terms (<<1 % on GS; possibly higher on 55-map per the inter-student-skill variance documented in Obs 317). Two specific examples of curator omissions surfaced and were corrected during this project's evaluation campaign (cand 4264 / K-35-064-3, a touching-mound boundary case; cand 2397 / K-35-062-4, an isolated mound in an under-reviewed region). Both shifted the corpus F1 by < 0.0005 absolute; neither is load-bearing for any headline claim. We acknowledge this as a structural property of GT-based evaluation rather than a specific numerical concern.

## Backlog item

A spot-check across 5–10 random map-tiles per corpus would estimate the per-tile curator-GT-omission rate empirically and could be reported as a quantified Limitations paragraph instead of the qualitative one above. Not paper-blocking; deferred. Sketch:

1. Sample 5–10 tiles per corpus uniformly at random from the evaluation bounds.
2. For each tile, manually inspect the rendered crop at classifier resolution and compare the visible mounds against the curator GT for that tile.
3. Compute a per-tile omission rate (k / N where N = visible mounds, k = mounds missing from the curator GT).
4. Report mean ± SE per corpus; if material (e.g. > 1 %), promote into the manuscript Limitations as a quantified bound.
5. If immaterial (≤ 1 %), the qualitative paragraph above suffices and the spot-check serves as a reproducibility-supplement footnote.

The spot-check is ~30 min user wall-time per corpus; total ~1 hour. Recommended timing: post-paper-outline, when the Limitations section is being drafted in earnest.
