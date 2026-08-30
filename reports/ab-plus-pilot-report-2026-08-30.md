# AB+ pilot report: 25 sources, complete — PAUSED at the checkpoint

> **Last revised**: 2026-08-30 (original publication; pilot complete,
> corpus build PAUSED per the PI's quota ruling pending the usage
> checkpoint). See [§ Changelog](#changelog).

## Outcome

All 25 pilot sources are drafted, deterministically quote-checked,
adversarially verified in fresh context, edited, re-checked, and
rendered to `outputs/ab-plus/*.md` (196 attested quotes, every one
byte-verified against extracted page text at render time). The
deliverables are committed; working files (`_work/`, incl. page text
and OCR provenance notes) stay gitignored per the copyright
convention.

**The headline verification statistic: 0 of 25 entries passed the
fresh-context check without edits.** Every verdict was
PASS-WITH-EDITS; none was FAIL; nothing was fabricated (the
deterministic checker held quotes byte-stable throughout). The
two-mechanism design (code catches fabrication, an independent LLM
catches overreach) found interpretive defects in every single entry
that byte-perfect quoting could not screen.

## Catch taxonomy (what the verifier layer caught)

1. **Hedge inflation** — "consistent with our mechanism" promoted to
   "evidence for our mechanism" — the most common catch, appearing in
   some form in the majority of entries (e.g. Maxwell's
   carried-operating-point "signature", Minderer's calibration claim).
2. **Salience drift** — a true source claim framed to overstate its
   relevance (Orengo's settlement-mound bridge; V*'s 2023-vintage
   chance floor nearly travelling into our Results as a capability
   prior).
3. **Dropped denominators, baselines, and scope** (YOLO-World's 20×;
   Bou's unscoped YOLOv5 win; Zhang's welded head-to-head).
4. **Silently repaired source errors** — entries fixing garbled source
   sentences in the wrong direction (Sobotkova's 35-of-49).
5. **Bidirectional correction** — drafters caught two errors in
   verifier verdicts (the Ståhl referent misreading; Yuan's
   protocol-mixing overclaim was itself half-overturned), and one
   contamination critique was re-scored and found neutral (Yin,
   0.941 vs 0.947): the layers check each other, not just downstream.

## What the corpus now attests for the paper (selection)

- **O'Hara**: the 98.2 = majority-class derivation is reproducible
  from an attested contiguous quote of the confusion matrix;
  wetland-class 90.8 pinned; the Ståhl comparison is class-matched
  but protocol-incommensurable — no like-for-like exists.
- **Saxton**: "0.73" is the validation/common-legend cell; the test
  split is 48.10 with rare symbols at exactly 0.
- **DIGMAPPER**: the 0.89 tier is binned BY F1, not scan quality;
  0.82 is carried 69 % by one abundant class; no extraction module
  is evaluated on more than eleven maps.
- **WODAN 2020**: transfer tax measured on burial mounds in 2020
  (barrows 70.1→49.8, same counting convention); the ~50 % headline
  is the argmax of a 120-cell sweep vs 24.0 at the carried default;
  its own fifteen-model bagging is the consensus-over-passes
  antecedent.
- **Sobotkova 2023**: the novice-human baseline is measured on
  precisely our gold-standard tiles (preregistration lines 19/260);
  corrected human operating point ≈ 95.0 % recall at 99.1 %
  precision, failure omission-shaped and outlier-driven.
- **Caspari**: tile-level classification twin; the citable F1 0.99
  belongs to the EMPTY tiles (tomb-present 0.91 on ~40 positives).
- **Yin**: a published system with aggregate F1 0.89 and TOTAL-row
  MCC −0.109 on its own protocol — the MCC thread's sharpest exhibit.
- **Berganzo**: sparse-pool F1 collapse (78.73→18.67) with identical
  TP/FN — pure negative-pool artefact; the full apparatus buys +0.24
  on the dense pool vs +57.6 on the sparse one.
- **Gould**: the D.9 dossier — "Adaptive Preregistration" is *sensu
  Srivastava 2018* but Gould et al. plausibly coined the label; term
  occupancy is UNSETTLED without reading Srivastava directly; zero
  LLM/AI/automation mentions in the body (grep-receipted); their
  admitted gaps are all execution-side.

**Candidate bibliography additions surfaced by the corpus itself**:
Huang et al. 2023 and Miao et al. 2017 (point-symbol recognition on
scanned topographic maps — a strand-3 novelty claim must clear
them); Guyot et al. 2018 (burial mounds from LiDAR); Green et al.
2019 (cite directly, not via Orengo); Srivastava 2018 (D.9
prerequisite — the preprint is already in `~/Downloads`).

## Pipeline amendments before the full run

1. **Pre-flight cache-quality gate**: 3 of 25 sources (12 %) were
   rasterised print-to-PDFs needing OCR repair, with three distinct
   signatures (empty ×2; watermark-only text layer ×1, which evaded
   a zero-character check). Gate on characters-per-page BEFORE
   drafters launch; the repair pattern is documented in the three
   `_work/*.pages-provenance.md` notes (requires tesseract — absent
   on sapphire, present locally).
2. **Per-citekey work directories** (one scratchpad filename
   collision between concurrent agents).
3. **Consider an overflow-notes field** in the schema: the 300–500
   word band displaced verified secondary caveats from two entries
   into agent reports.
4. Transcript eviction of long-idle drafters is handled by design
   (fresh edit agents work from on-disk verdict + entry + provenance)
   — no change needed, but batches should expect it.

## Usage (the checkpoint numbers)

Reported subagent token usage, summed from agent telemetry: ≈ 9.0M
tokens across ~74 Opus-tier agent runs (25 drafts ≈ 2.95M, 25
verifications ≈ 2.42M, 24 edit passes ≈ 3.65M), ≈ 360k reported
tokens per source all-in. Orchestration overhead in the main session
is additional. **Naive extrapolation to the remaining 88 sources:
≈ 32M reported tokens, ~3.5× the pilot.** The PI's weekly meter
stood at 26 % at pilot approval; the post-pilot reading converts
these relative numbers into %-per-25-sources and decides batch sizing
for the remainder.

## Status

**PAUSED** (PI ruling, 2026-08-30, quota conservation) after the
first 25. The remaining ~88 sources run on PI go, in batches sized
by the checkpoint arithmetic, with the § amendments applied first.

## Changelog

### 2026-08-30 — Original publication

Written at pilot completion, same day as approval and execution.
