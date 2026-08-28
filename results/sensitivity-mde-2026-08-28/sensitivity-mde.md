# Instrument sensitivity: what the study's negative claims can claim

> **Last revised**: 2026-08-28 (original publication). See
> [§ Changelog](#changelog) for revision history.

**Purpose**: the paper's most interesting outcomes are often negative
("varying the image library has no statistically significant
effect"). This appendix quantifies what such claims mean, from the
COMMITTED permutation records of the instruments as actually run — no
new computation, no post-hoc observed power (a known fallacy; we
report prospective sensitivity and equivalence bounds instead).

## 1. Minimum Detectable Effects, by instrument

MDE = z × (permutation null SD), two-sided α = 0.05; z = 1.96 at 50 %
power, 2.80 at 80 %. Null SDs harvested from every committed pairwise
record of each instrument (`sensitivity.json` for provenance).

| Instrument (corpus, buffer) | n tiles | n records | null SD (median) | MDE 50 % | MDE 80 % |
|---|---:|---:|---:|---:|---:|
| GS tile-swap, H8 v2 consensus (327, 20 m) | 327 | 7 | 0.0232 | 0.045 | **0.065** |
| GS tile-swap, Era-1 board (340, 20 m) | 340 | 3,321 | 0.0226 | 0.044 | **0.063** |
| GS tile-swap, verified sets on the common footprint (20 m) | 340 | 3 | 0.0087 | 0.017 | **0.024** |
| 55-map tile-swap, final board (8,541, 50 m) | 8,541 | 253 | 0.0046 | 0.009 | **0.013** |

Three structural readings:

1. **The two-tier design is visible in the numbers.** The GS corpus
   is a screening tier: it excludes effects ≳ 0.065 at 80 % power and
   cannot adjudicate below ~0.045. The 55-map corpus is the
   resolution tier (MDE₈₀ ≈ 0.013) — which is why questions that
   survive GS screening are escalated to deployment scale.
2. **Verification sharpens the GS instrument ~2.6×** (null SD 0.0087
   vs 0.023): proposer-verifier cells are compared with far less
   noise than raw consensus cells, because the verifier removes the
   high-variance false-positive load. This is why the text-vs-image
   effect (+0.055) resolved at p = 0.001 on only four sheets, while
   same-sized contrasts between unverified cells would sit near the
   detection threshold.
3. **The Obs 362 "±0.03 GS tie" rule is recovered independently**:
   MDE₅₀ ≈ 0.044–0.045 on the raw GS instruments brackets the
   empirically stated ±0.03–0.045 bounded-ignorance band.

## 2. The empirical cross-scale calibration

The design's resolution claims are not merely computed — they were
demonstrated within the study. Prediction P6 (the A-vs-B geometry
tie) was a genuine GS-scale tie; at 55-map scale the effect proved
real at ΔF1 ≈ 0.010–0.012 (p = 0.0042–0.0147, BH-robust) — an effect
sitting almost exactly at the deployment MDE₅₀ (0.009) and far below
the GS MDE. Conversely IP5 (image pass-count saturation, −0.016,
p = 0.069 on GS) shows an effect trapped in the GS indeterminate
zone. Together they calibrate the table above with live specimens.

## 3. Equivalence bounds for the headline nulls (TOST)

Two one-sided tests against margin Δ, normal approximation on each
contrast's committed permutation null SD (an approximation — the
exact permutation-TOST would resample; at these SDs the approximation
is conservative to second order). For the seven preregistered H8 v2
library contrasts, the **smallest margin at which all seven pass at
α = 0.05 is Δ = 0.07**; at that margin the worst contrast passes at
p = 0.019.

**The claim the paper can therefore make**: library composition and
scale effects, if any, are smaller than 0.07 F1 — i.e. smaller than
the modality effect measured under the same instrument family
(text − image = +0.055), and an order larger than anything that
changed a practitioner recommendation at deployment scale (steps of
0.01–0.02).

## 4. Recommended equivalence margins (PI to adopt or amend)

- **GS-scale composition nulls (H8, H9, H10, H12)**: Δ = **0.07**,
  stated as "no effect approaching the size of the modality effect".
  Grounds: the smallest TOST-passing margin across the H8 family;
  substantively, 0.07 separates "could rival a design choice that
  matters" from "could not".
- **Deployment-scale nulls (carried-point ties, saturation at carried
  points)**: Δ = **0.015**, stated as "no effect larger than one
  practitioner cost step". Grounds: deployment MDE₈₀ = 0.013; the
  cost-frontier steps the paper prices are 0.01–0.02 F1.
- Wherever a null matters to a conclusion, quote the applicable MDE
  row alongside it rather than the p-value alone.

## Method and provenance

Harvest and arithmetic: `scripts/sensitivity_mde.py` (committed
records only; sources listed per row in `sensitivity.json`). The
55-map per-sheet sign-swap instrument stores no null SD; its
resolution is evidenced directly by detected effects down to ~0.010.
No permutations were re-run.

## Changelog

### 2026-08-28 — Original publication

Built by Session 143 on PI commission, immediately after the
image-B head-to-head landed ($0; local arithmetic over committed
records).
