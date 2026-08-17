# E45 bootstrap pairings — registered instrument for the H2/H3 family contrasts

> **Last revised**: 2026-08-17 (original publication). See
> [§ Changelog](#changelog) for revision history.

**What this is.** The family-level BH-FDR correction
(`results/family-fdr/family_fdr.json`) consumed permutation p-values
for H2 and H3. Erratum E45 discloses the tile-swap permutation as an
unregistered inference method; the registered inference is bootstrap
estimation with 95 % confidence intervals (registered § 3.5 at
`docs/methodology/preregistration/osf/preregistration.md:293`;
tile-level resampling, percentile method, and the 1,000-iteration
count fixed pre-lodgement in Decision 10,
`docs/methodology/preregistration/decisions-log.md:335-345`, parameter
row `:345`; E54 records the 10,000-iteration post-hoc convention).
This analysis computes the registered construction for **the two
family contrasts that entered the correction on permutation floors
(H2 and H3)** — the E45 pairing obligation, Methods § M.4. Scoping
note (blind-verification finding, 2026-08-17): H8's family input is
also permutation-sourced, but as a Simes/BH-minimum over seven
tile-swap contrasts, for which a single paired bootstrap delta is
not defined — H8's null therefore remains permutation-based and is
disclosed as such under E45 rather than paired here. H1, H4, H5, and
H7 entered the family on bootstrap inputs already.

**What this is not.** A replacement for the family inputs. The
permutation p-values remain what the family correction consumed
(registered-before-compute construction, 2026-07-30); this artefact
is the paired disclosure.

## Results

| Contrast | ΔF1 (micro, @20 m) | Registered bootstrap (B = 1,000) CI95 | E54 sensitivity (B = 10,000) CI95 | CI excludes 0 |
|---|---:|---|---|---|
| **H2** — PV 16-of-30 vs consensus 26-of-30 | +0.076083 | [+0.051787, +0.104642], p = 0.001 (floor) | [+0.050771, +0.103945], p = 0.0001 (floor) | yes, both |
| **H3** — consensus 26-of-30 vs matched single-pass | +0.427340 | [+0.389640, +0.468082], p = 0.001 (floor) | [+0.385608, +0.469544], p = 0.0001 (floor) | yes, both |

Both intervals exclude zero at both iteration counts, in the
direction of the committed permutation results. The registered
instrument therefore corroborates both family rejections: H2 (the
falsified directional prediction — two-stage improves F1, against
the registered expectation) and H3 (consensus beats matched
single-pass). No stop state fired: had either CI included zero, the
block plan's surprising-result state would have halted the
methods-draft fill.

## Method

Paired tile-resampling bootstrap of the micro-F1 difference: the same
resampled 487-tile index set is applied to both arms, micro-F1 is
recomputed per arm from summed per-tile TP/FP/FN, and the difference
distribution yields the percentile CI95 and two-sided
p = max(2 · min tail, 1/B), seed 42. The registered quantities are
the CI95 and the CI-excludes-zero significance reading (Decision 10
registers "if the 95 % CI for a difference excludes zero, we treat
this as significant"); the 2 · min-tail p is **not** registered — it
is carried for comparability with the family-FDR H1 leg's
convention (`scripts/compute_family_fdr.py`) only. B = 1,000 is the
registered-convention primary (Decision 10); B = 10,000 is the E54
narrow-effect sensitivity. Script:
`scripts/e45_bootstrap_pairings.py` (eight tier1 tests, including a
pairing guard that fails any unpaired-resampler mutant).

**Inputs and reproduction gates** (run before any bootstrap; all
passed at tolerance 1e-6):

- **H2** per-tile tables from a non-quiet re-run of
  `scripts/run_pairwise_tests.py` on the identical single-comparison
  config (`h2-rerun/comparison.yaml`, copied verbatim from
  `configs/pairwise-comparisons.yaml` group 1 entry 1) — same code
  path, seed, and inputs as the committed artefact, which was written
  with `--quiet` and so carries no per-tile block. Gate: 5/5 fields
  reproduce the committed
  `results/pairwise/20m/group_1_architecture/pv-vs-consensus-…26-of-30.json`
  (F1 0.890201 / 0.814118, ΔF1 0.076083, n_tiles 487, p 0.0).
- **H3** per-tile tables rebuilt through
  `scripts/consensus_vs_baseline_tiering.py`'s own cell loaders
  (consensus arm: single aggregated set, integer counts; single-pass
  arm: pass-averaged float counts). Gate: 4/4 fields reproduce the
  committed tiering `pairwise` entry (micro-F1 0.814118 / 0.386778,
  Δ 0.427340). Note the tiering artefact's *headline* f1_b for this
  contrast is 0.3871 — the eval mean-of-runs vintage, ≤ 0.0005 from
  the micro-F1 the permutation and this bootstrap operate on (the
  tiering script documents the split; S135 audit adjudication
  items 3/11).

## Artefacts

- `e45_bootstrap_pairings.json` — machine-readable results, gates,
  and anchors (the source for every number above).
- `h2-rerun/` — the non-quiet H2 re-run outputs (per-tile comparison
  JSON + run manifest) as provenance.
- Register row: `e45-bootstrap-pairings` in
  `results/analyses-manifest.json` (classification PROPOSED
  confirmatory-with-deviation, deviations E45 + E54; PI ratification
  queued).

## Changelog

### 2026-08-17 (later) — Verification round

Blind fresh-context verifier (~45 claims re-derived; both bootstrap
legs reproduced bit-for-bit from independently written code; a full
leaf-field diff of the H2 re-run against the committed artefact
showed only `timestamp` and the `per_tile` block differing) +
adversarial code audit. Corrections applied: the "every confirmatory
claim resting on a permutation input" scoping narrowed (H8's family
input is also permutation-sourced — a Simes minimum, not pairable;
now stated); Decision-10 anchor corrected to
`decisions-log.md:335-345` (parameter row `:345`); the registered
(CI + CI-excludes-zero) vs convention-borrowed (2 · min-tail p)
distinction made explicit; H2 gate extended with the
wins/losses permutation fingerprint; pairing guard, length guard,
and rounded-bound-consistent CI flag added to the script. All
numbers unchanged; the artefact regenerated deterministically.

### 2026-08-17 — Original publication

S135 analysis block items 1–2, executed on sapphire ($0 API).
Registered-instrument pairing for the two permutation-sourced family
primary contrasts; both CIs exclude zero at both iteration counts.
