# Registered family-level BH-FDR correction — results

> **Last revised**: 2026-10-05 (every input is now a permutation p under
> PI ruling D42; H1 0.1774 → 0.0715, still not rejected; the rejection set
> {H2, H3, H7} is unchanged). See [§ Changelog](#changelog) for revision
> history.

**Registration**: `reports/verification/family-fdr-registration.md`
(REGISTERED and committed **before** this computation; PI rulings at
`reports/verification/phase2-rulings-2026-07-30.md` § 3).
**Computed**: 2026-07-30, sapphire, `scripts/compute_family_fdr.py`,
US$0 API. **Machine-readable**: `family_fdr.json`,
`h1_cmt0106_pooled_modality.json` (+ metadata sidecar), this directory.

## 1. H1's primary — registered contrast CMT-0106, first execution

The registered pooled modality contrast ("Text-only conditions vs
Image-using conditions", `preregistration.md:441`) had never been
executed; the PI selected it as H1's primary under the run-it-now policy,
with the reconstruction rule fixed at registration § 5.1.1 **before** the
number below existed — the family's one outcome-blind input.

| quantity | value |
| --- | --- |
| text-only group mean F1 ({brief-text, verbose-text}) | 0.5267 |
| image-using group mean F1 ({image-only, brief-text-image, verbose-text-image}) | 0.5029 |
| Δ (text − image) | **+0.0238** |
| 95 % CI (percentile, B = 10 000, seed 42) | [−0.0104, +0.0585] |
| two-sided permutation p (D42; 10 000 within-tile label permutations, seed 42) | **0.0715** |
| (retired) two-sided bootstrap p, as first published | 0.1774 |

**The H1 test since D42.** PI ruling D42 (2026-10-05) retired the bootstrap
p-value project-wide. H1's pooled contrast has no two-arm tile swap, so its
p comes from a within-tile label permutation: on each permutation every
tile's five condition labels are shuffled (each condition carrying its three
runs) and the statistic is recomputed. Its null is that all five conditions
are interchangeable on each tile, which is sharper than H1's own null (equal
group means): differences inside a group count against it, and here they
are as large as the contrast (brief-text 0.552 vs verbose-text 0.502;
image-only 0.469 vs the two text-plus-image conditions about 0.52). Read
0.0715 with that caveat. The verdict does not depend on it: the bootstrap
CI includes zero, and both tests leave H1 unrejected.

Both validation gates passed (per-condition F1 reproduction against the
committed evaluation — exact on the text conditions; vectorised-vs-library
scoring equivalence on 50 probes).

**Reading**: the pooled modality effect is positive — text-described
examples over image examples, the direction that falsified the
"academic baseline" designation (E68) — but **not significant**. Pooling
dilutes the two significant extreme pairs (brief-text vs image-only
p = 0.0055; image-only vs brief+image p = 0.009, permutation re-test of the
March contrasts): `verbose-text` weakens
the text pool and the two `+image` conditions strengthen the image pool.
The registration's § 9 directional expectation (+~0.03, significance
unknown) is confirmed in direction and resolved null in significance.

## 2. The family correction (q = 0.05, m = 7; H6 excluded, never run)

| rank | H | primary (as registered) | p | BH-adjusted p | verdict |
| --- | --- | --- | --- | --- | --- |
| 1 | H2 | two-stage PV vs optimal single-stage | < 1 × 10⁻⁴ (permutation floor) | 0.00035 | **REJECTED** |
| 2 | H3 | consensus vs matched single-pass | < 1 × 10⁻⁴ (permutation floor) | 0.00035 | **REJECTED** |
| 3 | H7 | T0.3 vs T1.0, text track | 0.0002 (permutation) | 0.00047 | **REJECTED** |
| 4 | H1 | CMT-0106 pooled modality (§ 1) | 0.0715 (permutation) | 0.125 | not rejected |
| 5 | H4 | canonical-first vs canonical-last | 0.1366 (permutation) | 0.191 | not rejected |
| 6 | H5 | terse vs verbose, image track, precision | 0.7262 (permutation) | 0.834 | not rejected |
| 7 | H8 | Simes global null (within-H8 BH minimum) | 0.8344 | 0.834 | not rejected |

**Rejection set: {H2, H3, H7}** — the smaller of the registration's two
pre-committed possibilities ({H2, H3, H7} or {H1, H2, H3, H7}), decided
by the outcome-blind H1 computation.

**Mandatory reporting riders** (registration §§ 5.2, 7.1, 8.3):

- **H2 is a falsified directional prediction**, not a confirmation: the
  registration predicted two-stage would *not* improve; it improves by
  +0.076 F1, clearing the registered ≥ 0.05 stopping-rule threshold in
  the direction the registration predicted against.
- All tests are two-sided per E64(v)'s operative reading; H4 would be
  p ≈ 0.062 one-tailed — still null.
- H8's input is the Simes global-null p over its seven registered
  contrasts (the within-H8 BH minimum), not a raw contrast p — labelled
  as such wherever reported.
- H5's primary is a constrained stand-in: the registered headline
  (Minimal vs Terse) never ran at the current era.

## 3. Sensitivity — the all-contrasts correction

Per the PI decision, the committed all-contrasts correction
(`results/pairwise/20m/fdr/pairwise_results_fdr.json`: 26 confirmatory
rows, 20 significant, Era-2 tile-swap permutation) is reported alongside.
The two corrections answer different questions — "which registered
hypotheses survive?" (this document) versus "which executed comparisons
survive?" — and are complementary, not nested: the 26-row family contains
no H4, H5, H7, or H8 rows. They agree on direction everywhere they
overlap (H2/H3-adjacent architecture contrasts are significant in both).

## 4. Methods disclosure (for the paper, GATE 1 ruling 7(d))

The registered family-level correction was deferred at the retest era
("FDR correction deferred until all data available") and never resolved
until this campaign. Running it now discharges the obligation but does
not make it prospective: six of the seven input p-values were visible
in-repo when the family was fixed. The registration therefore claims
only selection-fixing, not outcome blindness — except for H1, whose
primary was computed for the first time under a pre-committed
reconstruction rule, and whose result determined which of the two
pre-committed rejection sets obtained. Discharges CMT-0047 and CMT-0106.

## Changelog

### 2026-10-05 — Every input a permutation p (PI ruling D42)

**Refresh trigger**: PI ruling D42 (`planning/pi-decisions-2026-09-20.md`):
every contrast is tested by the paired permutation test with BH, and no
p-value is read from a bootstrap. `compute_family_fdr.py` now computes H1's
p by within-tile label permutation and reads H4, H5 and H7 from the March
contrasts' permutation re-test (`results/retest/pairwise-bootstrap-comparisons.json`,
each row's `permutation_retest`, from `reports/retest-bootstrap-check-2026-10-05.md`).
Regenerated on sapphire (`5986316b5`). This departs from the family
registration's § 5.1.1 p construction, which named the bootstrap; D42 is
the ruling that changes it.

| H | Before | After | BH before → after |
|---|---:|---:|---:|
| H7 | ≤ 0.001 (bootstrap floor) | 0.0002 | 0.00233 → 0.00047 |
| H1 | 0.1774 | 0.0715 | 0.248 → 0.125 (now rank 4) |
| H4 | 0.124 | 0.1366 | 0.217 → 0.191 (now rank 5) |
| H5 | 0.756 | 0.7262 | 0.834 → 0.834 |

**What did NOT change**: H2, H3 and H8's inputs; the rejection set
{H2, H3, H7}; H1's point estimate and bootstrap CI. § 1 now explains the
H1 permutation's null and why 0.0715 should be read with a caveat.

### 2026-07-30 — Original publication

Registered computation executed on sapphire the same day the
registration was committed (registration first — commit order verifiable
in git). Gates A/B passed; all six fixed p-values re-read from their
anchored artefacts and asserted against the registered quotes.
