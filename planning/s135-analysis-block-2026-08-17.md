# S135 $0 analysis block — pre-run review record

> **Last revised**: 2026-08-17 (initial plan). See [§ Changelog](#changelog).

**Block**: the five-item $0 analysis batch queued by the S134 walk
(`reports/s134-relabel-walk-dossier.md` § 8 Group E) and the S135
continuity block: (1–2) the E45 bootstrap pairings for the H2 and H3
family-FDR primary contrasts; (3) the errata-census refresh at E78
vintage; (4–6) H6's three registered $0 analyses (A-06 decision rule,
A-07 voting-threshold comparison, A-09 cost-effectiveness gate) on
the existing Pro data.

**Review mode — adaptation disclosed**: the PI directed the start
("could you start the analyses") and is AFK; the operator dialogue
cannot run. Per the skill's provision, the review was conducted solo
under the naive-reviewer stance with every claim checked against the
artefacts (not memory), and the codified **clean-context agent pass**
(fresh-context Opus audit of this committed plan) substitutes for the
missing dialogue. PI-facing decisions are **queued, not assumed** —
marked ⏳PI below. Automation's finish line is
authored-and-committed; every sign-off field stays null.

**Spend**: $0. No script in this block calls any API; the audit gate
checks that no new script imports an API client.

---

## 1. Artefact inventory

| item | produces | refreshes |
|---|---|---|
| 1–2. E45 pairings | `scripts/e45_bootstrap_pairings.py` + tier1 tests; `results/e45-bootstrap-pairings/e45_bootstrap_pairings.json` + `findings.md` | `results/analyses-manifest.json` (+1 row `e45-bootstrap-pairings`); `docs/paper/methods-draft.md` M.4 [PENDING × 2] |
| 3. Errata census | in-place refresh of `reports/d17-inventory/d17-errata-census.md` to E1–E78 scope (revision-policy banner + changelog) | `docs/paper/methods-draft.md` M.x [unverified] (the counting-rule sentence and the 22/16/12/28 tally) |
| 4–6. H6 analyses | `scripts/h6_registered_analyses.py` + tier1 tests; `results/h6-registered-analyses/{a06_decision_rule.json, a07_voting_thresholds.json, a09_cost_gate.json, findings.md}` | `results/analyses-manifest.json` (+3 rows); `results/hypothesis-outcome-table/` (regenerated once, end of block) |

**Input anchors (verified this session, 2026-08-17):**

- H2 primary contrast: PV 16-of-30 (`outputs/h11/pv-diag-384/verified/flash-high-text-16of30/`,
  prob_t 0.2) vs consensus 26-of-30 (`outputs/h11/pv-diag-384/flash-high-text-n5`, pool 30);
  committed point estimates F1 0.890201 / 0.814118, ΔF1 0.076083, 487 tiles
  (`results/pairwise/20m/group_1_architecture/pv-vs-consensus-flash-high-text-16-of-30-pv-vs-flash-high-text-26-of-30.json`).
  The committed JSON carries **no per_tile block** — per-tile tables must be
  rebuilt with `run_pairwise_tests.py`'s own loaders.
- H3 primary contrast: `consensus-flash-high-text-26of30` vs
  `pv-diag-384::baseline-flash-text-high-t-0-7`; committed F1 0.8141 / 0.3871,
  ΔF1 0.427 (`results/diversity-dividend-384/tiering-champions/tiering_20m.json`,
  `headline_contrasts[2]`, analysis `diversity-dividend-consensus-vs-baseline-384`).
- Bootstrap template: `scripts/compute_family_fdr.py` H1 leg — paired tile
  bootstrap, two-sided p = 2·min-tail with floor 1/B, percentile CI95,
  validation gates before compute. The pairings reuse this convention verbatim
  for cross-artefact comparability.
- H6 decision logic: `scripts/lib_phase4_transfer.py` (tested; constants
  provenance documented in-file — registered 0.03 / >10 % / ≥20 % vs
  operational 0.05 / 0.10 / CI-augmentation).
- H6 Pro data: `n1-outstanding-384::pro-{text,image}-high-t0-consensus-{1,2,3}of3`
  + Pro baselines (`n1-outstanding-384`, `n1-pro-rerun-384`); Flash optimal
  thresholds tabulated in `phase3a-consensus-calibration` /
  `diversity-dividend-384`; costs from `pass-budget-pareto-v2` (audited basis).
- Census source: `docs/methodology/preregistration/protocol-errata.md`;
  E1–E57 census counted programmatically (`^### E[0-9]` + per-entry Type
  parse). **Known discrepancy to resolve**: the E57-vintage census counts 18
  bare `Deviation` labels; `methods-draft.md:23-34` asserts 16 at E78 vintage
  — one of the two is wrong, which is why the slot is [unverified].

## 2. Finished states (countable)

1. **Pairings**: reproduction gates pass (both contrasts reproduce the
   committed F1s and ΔF1 at 6-dp equality **before** any bootstrap); JSON
   carries CI95 + p for both contrasts at B = 10,000 (E54 parameters, primary)
   and B = 1,000 (Decision-10 registered parameters, sensitivity), seed 42;
   findings doc cites the JSON; run on sapphire; committed + pushed.
2. **Census**: programmatic entry count returns exactly 78; every E58–E78
   entry classified with its verbatim `Type`; counts table, headline-count
   options, and counting-rule recommendation updated; the methods-draft tally
   reconciled (confirmed or corrected, discrepancy explained); changelog entry.
3. **H6**: A-06 evaluated for every factor the Pro data supports (with the
   at-most-one-registered-factor scope caveat stated); A-07 Pro-vs-Flash
   optimal vote thresholds with >10 %-relative flags per the registered rule;
   A-09 gate verdict (opened/closed) on audited costs; **an explicit A-08
   statement that the three-way transfer verdict cannot be honestly computed
   (1 of 4 registered factors varied)**; findings doc; 3 schema-valid manifest
   rows.
4. **Block**: hypothesis-outcome table regenerated once,
   `generate_hypothesis_outcome_table.py --check` green; full test battery
   green; `ruff check` + `npx markdownlint-cli2` clean on touched files;
   blind verification (L2) complete with denominators; methods-draft slots
   filled citing verified artefacts only; all commits pushed.

## 3. Stop states (halt and escalate)

- **Reproduction gate failure** (committed point estimate not reproduced) →
  halt that item before bootstrap; investigate; escalate. Never bootstrap on
  unreproduced inputs.
- **H2 or H3 bootstrap CI95 includes 0** → contradicts the family-FDR
  rejection → STOP the slot-fill; flag as a surprising finding (calibration
  protocol); the M.4 sentence is NOT written.
- **A-09 gate OPENS** (Pro cost-effectiveness superior) → surprising against
  the standing all-Flash-3 conclusion → flag prominently in the report; it
  feeds the PI's ~$48 H6 re-run decision. Report, do not decide.
- **Census tally ≠ draft numbers** → not a stop; the draft is corrected (the
  slot is [unverified] precisely for this), with before→after recorded here
  and in the census changelog.
- **Any API call** → impossible by construction; if any new code imports an
  API client, the audit fails the block.
- **sapphire unavailable** → compute items halt (no silent local fallback);
  census may proceed locally (pure text work). Verified at review time:
  sapphire up, load 0.00, repo behind 43 — `git pull --ff-only` is step zero
  there.
- **Schema validation or `--check` drift failure** after row additions → stop
  before any slot fill.

## 4. Dependency structure

- Items 1–2 (pairings), 3 (census), 4–6 (H6) are **data-independent** — no
  item consumes another's outputs. Simultaneous-safe in principle; executed
  serially here for legibility.
- **Coherence orderings** (the ones parallel execution would break):
  1. The hypothesis-outcome table regenerates **once**, after ALL manifest
     rows land (a per-item regen would produce three intermediate vintages).
  2. `docs/paper/methods-draft.md` is touched **once**, at the end, after L2
     verification passes on the artefacts its new sentences cite (one-commit
     rule; no draft sentence may cite an unverified artefact).
  3. Within H6: predicted-outcome text for the three rows is authored from
     the preregistration quotes **before** outcomes are computed
     (outcome-blind discipline, CMT-0106 precedent); A-08's non-computability
     statement drafts with the findings doc.
- The M.3 Dawid–Skene [PENDING] slots (methods-draft:140, :153) are **out of
  scope** for this block — prose fills from the existing D-S report, queued
  separately.

## 5. Partial-completion semantics

All computation is deterministic from committed inputs with fixed seeds —
any item re-runs from scratch at identical results. Partial state is
visible: a missing JSON artefact, an absent changelog entry, a null
`--check`. Mixed-vintage risk is carried by the two shared artefacts (the
analyses manifest and the outcome table) and is gated by coherence ordering
1; the methods-draft carries none because of ordering 2. One-commit rule:
each findings doc moves with its JSON in one commit; the census doc's counts
and changelog move in one commit; the methods-draft fills land in one commit.

## 6. Verification stack

- **L0**: machine-readable JSON first; findings docs cite them; every
  checkable specific carries a path/commit anchor; seeds and B recorded in
  the artefacts.
- **L1**: tier1 pytest for both new scripts; `ruff check`; `/audit` on new
  code (standing memory: audit is part of verification, not optional);
  markdownlint on touched Markdown.
- **L2**: blind fresh-context verification (Opus), one pass per findings
  doc + the census. Answer-shaped questions put **cold** (e.g. "from these
  per-tile tables, compute the 95 % CI for the ΔF1"; "count entries by
  declared Type in protocol-errata.md"), then diffed against the drafts.
  Denominator required (claims re-derived, artefacts opened); an empty
  corrections table without a denominator is not a pass. **Disagreement
  rule**: a verifier correction conflicting with the draft triggers a third
  derivation from the data; unresolved conflicts queue for PI adjudication —
  the verifier never wins by default.
- **L3**: `generate_hypothesis_outcome_table.py --check`; manifest schema
  validation; a citation-site sweep for every number the census moves
  (the 22/16/12/28 tally, "78", and any "deviations" headline count).
- **L4** (⏳PI, queued for return): sign-offs on the 4 new manifest rows;
  ratification of the PROPOSED preregistration classes (see below); the
  counting-rule adoption for the paper; the ~$48 H6 re-run decision on the
  A-06/A-07/A-09 evidence; review of any surprising-result flag.

**PROPOSED classifications (⏳PI — authored with rationale, sign-off
null):** `e45-bootstrap-pairings` → `confirmatory-with-deviation`
(registered instrument applied to the registered confirmatory contrasts;
discharges the E45 pairing obligation; deviations E45, E54). A-06/A-07/A-09
rows → proposed per-row at authoring time against the discharge principle
(registered obligations computed on existing-scope Pro data; scope caveats
E-anchored), explicitly flagged as the block's least-certain calls.

## Hardenings adopted at review

1. Reproduction gates precede every bootstrap (6-dp equality with committed
   values).
2. One table regeneration, at block end (coherence over convenience).
3. Methods-draft is written once, last, and only from L2-verified artefacts.
4. Bootstrap p convention copied verbatim from the H1 leg for
   cross-artefact comparability (2·min-tail, floor 1/B).
5. B = 10,000 primary + B = 1,000 registered-parameter sensitivity, both
   reported — no silent parameter choice.
6. Predicted-outcome fields authored before computation (outcome-blind).
7. A-08 silence converted to an explicit non-computability statement.
8. No-API-import check added to the audit scope.
9. sapphire pull-to-current is step zero; compute never falls back locally
   without confirmed unavailability.
10. All classification calls PROPOSED, never self-ratified.

## Clean-context audit adjudication (2026-08-17)

The fresh-context Opus audit returned 15 findings (1 BLOCKER, 1
blocker-class contract defect, 5 HIGH, 4 MEDIUM, 4 LOW) against a
21-file / 23-probe denominator. All 15 confirmed on adjudication.
Dispositions:

1. **BLOCKER-1 (fix — scope amendment)**: the plan's "H6 Pro data"
   (`n1-outstanding-384::pro-*-consensus-*of3`) is **Flash** — the
   E57 mis-dispatch (`passes-manifest` model fields; F1 0.494 vs the
   genuine-Pro 0.804 matches E57's table to 3 dp). **Amended H6
   inputs**: genuine Pro = `n1-pro-rerun-384` (12 per-pass
   detections, 4 corners × 3 runs, model `gemini-3.1-pro-preview`
   verified). A genuine-Pro N = 3 consensus is materialised at $0
   via the standard merge machinery for the two high-t0.0 corners;
   the E57 mis-dispatch pools are **reused as the matched-N Flash
   comparator** (preserve-and-compare heuristic). ⏳PI: ratify the
   amended source; the walk ruling's words were "on the existing Pro
   data", which `n1-pro-rerun-384` is.
2. **BLOCKER-2 (fix)**: `preregistered: null` crashes the table
   generator (`generate_hypothesis_outcome_table.py:137-143`
   raises). "Sign-off null" means `manually_verified_at` **only**;
   every new row carries its PROPOSED class in `preregistered`, with
   the PROPOSED marker recorded in `provenance`.
3. **HIGH-3 + MEDIUM-11 (fix)**: the H3 gate re-anchors on the
   tiering artefact's `pairwise` block (micro-F1 0.814118 /
   0.386778 / Δ 0.42734) — the quantities a paired tile bootstrap
   operates on; the headline 0.3871 is the eval mean-of-runs
   vintage (≤ 0.0005 apart, per the tiering script's own
   documentation). Statistic choice now explicit: the bootstrap
   resamples exactly the per-tile tables the committed permutation
   consumed (pass-averaged counts for the single-pass arm).
4. **HIGH-4 (fix — census scope widened)**: the plan's binary
   framing was wrong. The census itself is stale inside E1–E57
   (E10/E37/E45 retyped post-compilation: bare `Deviation` 18 → 16
   within E1–E57; E78-scope bare counts are 22/18/12/26). The
   refresh does a four-bucket recount at both vintages with a
   before→after table covering the retypes, corrects the census §§ 1
   and 3 tables, and fixes methods-draft (16 → 18, 28 → 26, and the
   omission-qualifier set is E74/E75/E78 — E59's Type is bare
   `Deviation`).
5. **HIGH-5 (fix)**: A-07 as registered presupposes matched N;
   |T−26|/26 over Pro's k ∈ {1,2,3} is data-independent. **Primary
   = matched-N = 3 comparison** (genuine-Pro curves vs the E57
   Flash N = 3 curves, same corpus/config family); the registered
   N = 30-vs-N = 3 form is declared not-computable-as-registered
   (A-08 pattern), with the fraction-form reported descriptively.
6. **HIGH-6 (fix)**: A-06 verdict computed under the **registered**
   rule (Δ ≥ 0.03, no CI condition, `preregistration.md:677`); the
   library's CI augmentation is fed a real paired tile-bootstrap
   **delta** CI (never the per-condition F1 CI, which is vacuous),
   and labelled operational. Scope: zero of the four registered
   factors are cleanly evaluable; the nearest contrast (temperature
   confounded with thinking, both corners) reports under the E40
   confound caveat.
7. **HIGH-7 (fix)**: A-09's cost basis = per-pass audited `cost_usd`
   from `passes-manifest` on **both** sides (genuine-Pro ~$1.85/pass
   text vs Flash per-pass at matched configuration), basis stated in
   the artefact; `pass-budget-pareto-v2` (all-Flash) cited as
   context only.
8. **MEDIUM-8 (fix via reclassification)**: the H6 rows are
   PROPOSED **post-hoc**, not confirmatory-with-deviation — the
   discharge principle (Obs 413) rules: registered method applied to
   material other than the registered Phase-4 runs is E41-class
   extension. The existing `h6-phase4-transfer` not-executed
   disposition row then stands unchanged and the outcome table does
   not move. Supersedes the scratchpad row stubs. ⏳PI: this is the
   block's least-certain call; the walk's phrase "registered
   analyses" pulls the other way.
9. **MEDIUM-9 (accept + inline mitigation)**: no schema-validation
   runner exists; validation runs inline (jsonschema 4.26.0) as part
   of L3. A permanent `validate_manifests.py` is a follow-up
   candidate, out of scope here.
10. **MEDIUM-10 (fix in prose)**: the permutation p remains the
    family-FDR input (registered-before-compute, historical); the
    bootstrap is the E45 **paired disclosure**, never a replacement.
    `family_fdr.json` is not regenerated. The positional
    `headline_contrasts[2]` fragility is noted as standing risk, not
    triggered by this block.
11. **LOW-12 (moot)**: sapphire reached HEAD after the plan was
    written; step zero is a no-op.
12. **LOW-13 (fix)**: `tests/README.md` does not exist; tier
    markers per `pytest.ini`. New tests carry `tier1` markers.
13. **LOW-14 (fix)**: all new artefacts cite the full
    `docs/methodology/preregistration/osf/preregistration.md` path.
14. **LOW-15 (adopt)**: the H2 per-tile route is a re-run of
    `run_pairwise_tests.py` **without** `--quiet` (the committed
    artefact was written with it), which makes the 6-dp gate free —
    same code path, same seed. If the re-run would overwrite the
    committed artefact, the git diff must show only the `per_tile`
    addition (identical stats) or the output is redirected.

## Go / no-go

PI-directed start (2026-08-17, "could you start the analyses", AFK).
**Agent go issued 2026-08-17** after all 15 audit findings were
adjudicated above. ⏳PI ratifications queued: the BLOCKER-1 source
amendment, the MEDIUM-8 post-hoc classification, the E45-row class,
the counting rule, sign-offs, and the ~$48 H6 decision.

## Changelog

### 2026-08-17 (final) — BLOCK COMPLETE; verification stack discharged

All five items executed and committed; every finished state in § 2
met. Census: two-vintage recount, blind-verified exact (zero
counting errors across three independent derivations), six
citation-hygiene corrections applied (`14eb57848`, `3b9091559`).
E45 pairings: gates 7/7 + 4/4, both CIs exclude zero at both B;
blind verifier reproduced both legs bit-for-bit from independently
written code (`0f5c7ff9b`, `29144d0e3`, revisions `a2e86a95f`). H6:
model-provenance gate 12 pools; **A-06 upgraded at the verification
round** — the full genuine-Pro 2×2 exists, temperature is the
driver (fires in all four cells, CIs exclude zero; thinking reaches
0.03 nowhere); A-07 split verdict with fragility flags; A-09 CLOSED
with the verdict now in the artefact itself (`896878fe2`,
`1dd68f1ee`). Register: 36 rows, 4 PROPOSED, schema 0 errors,
outcome-table `--check` green, H6 disposition unmoved. L1: 15 new
tier1 tests (incl. the mutant-killing pairing guard); full battery
1438 passed on sapphire + 52 streamlit-dependent locally; ruff
clean; adversarial code audit (3 HIGH / 9 MEDIUM / 10 LOW) fully
adjudicated — H-1 (JSON/prose verdict divergence), H-2 (silent
materialisation no-op), H-3 (pairing-blind tests) all fixed and
regression-tested. Methods-draft slots closed (`95bd7758c`); the
document carries no live markers. L4 queue for the PI: four row
ratifications (E45 class, three H6 post-hoc classes), the
counting-rule adoption (cite-individually vs 18/27/30), the ~$48 H6
re-run decision (inputs updated: temperature settled at $0), and
review of the A-06 upgrade. $0 API spent; no stop state fired.

### 2026-08-17 (later) — Audit adjudicated; go issued; scope amended

15/15 findings confirmed. Material amendments: H6 inputs move to
genuine-Pro `n1-pro-rerun-384` (+ $0 consensus materialisation, E57
pools retained as matched-N Flash comparator); A-07 redesigned as
matched-N; A-06 runs the registered rule with a real delta CI; A-09
re-based on per-pass audited costs; H6 rows re-proposed post-hoc
(discharge principle); census refresh widened to a two-vintage
recount; H3 gate re-anchored on the pairwise micro-F1 block; H2
per-tile via non-quiet re-run.

### 2026-08-17 — Initial plan (S135)

Solo pre-run review under the AFK adaptation; clean-context audit pass
queued next. No execution before audit adjudication.
