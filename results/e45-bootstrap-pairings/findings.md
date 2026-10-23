# E45 bootstrap pairings — registered instrument for the H2/H3 family contrasts

> **Last revised**: 2026-10-15 (H2 and H3 restated on the consensus route
> that keeps each cluster's contributing tiles, PI ruling D60 (3): the 26-of-30
> arm's F1 0.814118 → 0.816471; both intervals still exclude zero). Prior:
> 2026-10-05 (the bootstrap p-values are retired under PI ruling D42; the
> permutation p is carried instead). See [§ Changelog](#changelog) for
> revision history.

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
| **H2** — PV 16-of-30 vs consensus 26-of-30 | +0.073730 | [+0.049520, +0.101772] | [+0.048250, +0.101597] | yes, both |
| **H3** — consensus 26-of-30 vs matched single-pass | +0.429693 | [+0.392114, +0.470439] | [+0.388060, +0.472072] | yes, both |

The p-value beside each pair is now the paired tile-swap permutation
test's (PI ruling D42, 2026-10-05): p < 0.0001 for both H2 and H3, the
same test the family correction consumed. Both intervals exclude zero at
both iteration counts, in the
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
distribution yields the percentile CI95, seed 42. The two-sided
p = max(2 · min tail, 1/B) this artefact first carried is retired (D42);
the JSON now carries the permutation p on the same arrays. The registered quantities are
the CI95 and the CI-excludes-zero significance reading (Decision 10
registers "if the 95 % CI for a difference excludes zero, we treat
this as significant"); no p-value is registered (the 2 · min-tail p
was carried only for comparability with the family-FDR H1 leg, and both
are now permutation p-values under D42). B = 1,000 is the
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
  (F1 0.890201 / 0.816471, ΔF1 0.073730, n_tiles 487, p 0.0; the
  committed artefact as regenerated on 2026-10-15).
- **H3** per-tile tables rebuilt through
  `scripts/consensus_vs_baseline_tiering.py`'s own cell loaders
  (consensus arm: single aggregated set, integer counts; single-pass
  arm: pass-averaged float counts). Gate: 4/4 fields reproduce the
  committed tiering `pairwise` entry (micro-F1 0.816471 / 0.386778,
  Δ 0.429693; the tiering as regenerated on 2026-10-15). Note the tiering artefact's *headline* f1_b for this
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

### 2026-10-15 — H2 and H3 restated on the consensus route (PI ruling D60 (3))

**Refresh trigger**: PI rulings D60 (3) and D62 (2)
(`planning/pi-decisions-2026-09-20.md`), executed by the S164
restatement pass (`reports/s164-agent-records/restatement-pass.md`,
§ 1.5). PR #37 (fix `4e9d659ab`;
`reports/s163-agent-records/d60-3-consensus-route.md`) made the
in-memory consensus route keep each cluster's contributing tiles, so a
consensus detection is scored on its origin sheet as its file already
was. One detection of the consensus 26-of-30 arm moves (true positives
346 → 347), and its F1 rises 0.814118 → 0.816471. That arm is H2's
arm B and H3's arm A. The H2 per-pair artefact, its non-quiet re-run
(`h2-rerun/`), the H3 champions tiering this script gates against
(`results/diversity-dividend-384/tiering-champions/tiering_20m.json`),
and `e45_bootstrap_pairings.json` were regenerated on sapphire in two
independent copies that agree apart from timestamps and run roots, and
committed at `08af04cf3`. Every value equals its prediction (PR #37's
NEW run for H2; the S3 record's H3 tiering).

| Quantity | Before | After |
|---|---|---|
| H2 ΔF1 (micro, @ 20 m) | +0.076083 | +0.073730 |
| H2 registered CI95 (B = 1,000) | [+0.051787, +0.104642] | [+0.049520, +0.101772] |
| H2 E54 CI95 (B = 10,000) | [+0.050771, +0.103945] | [+0.048250, +0.101597] |
| H2 gate: arm B F1 | 0.814118 | 0.816471 |
| H3 ΔF1 | +0.427340 | +0.429693 |
| H3 registered CI95 (B = 1,000) | [+0.389640, +0.468082] | [+0.392114, +0.470439] |
| H3 E54 CI95 (B = 10,000) | [+0.385608, +0.469544] | [+0.388060, +0.472072] |
| H3 gate: arm A micro-F1 | 0.814118 | 0.816471 |

Sources: `e45_bootstrap_pairings.json` (`results.H2`, `results.H3`:
`bootstrap.registered_b1000`, `bootstrap.e54_sensitivity_b10000`,
`reproduction_gate`), read at `718d0ee08` (before) and at the pass's
head (after).

**What did NOT change**: every CI-excludes-zero reading, so both family
rejections are still corroborated; the permutation p (< 0.0001 for both);
H2 arm A (0.890201) and H3 arm B (0.386778, headline 0.3871); the
gates' tolerance and pass. `results/family-fdr/family_fdr.json` was not
regenerated and its p values do not move. Older changelog entries keep
the figures they reported.

**Commits**: `08af04cf3` (the regenerated pairwise, tiering, and e45
artefacts); this document refresh in the restatement pass's document
commit.

### 2026-10-05 — Bootstrap p retired (PI ruling D42)

**Refresh trigger**: PI ruling D42 (`planning/pi-decisions-2026-09-20.md`).
The table's p-values (0.001 and 0.0001, the bootstrap floors) are removed;
`e45_bootstrap_pairings.json` (regenerated on sapphire, `5986316b5`) carries
the paired permutation p on the same arrays: p < 0.0001 for H2 and H3.

**What did NOT change**: the registered quantities (the CIs and the
CI-excludes-zero readings), ΔF1, and the corroboration of both family
rejections.

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
