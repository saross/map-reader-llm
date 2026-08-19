# Audit brief: Session 137 (2026-08-19)

> **Last revised**: 2026-08-19 (original publication). See
> [§ Changelog](#changelog) for revision history.

**Who this is for**: a fresh-context model with no memory of Session 137, asked
to audit it adversarially. **Written by the instance that did the work**, which
is the reason to distrust it: I chose what to check and what to call settled, and
those choices are exactly where an error would now be invisible to me.

**Your job is not to confirm my conclusions.** It is to find what I got wrong and
what I did not think to look at. A report that says "verified, all correct" is a
failed audit unless it shows the checks that could have failed and did not.

## What happened, in one paragraph

The session began by filing an erratum for a bootstrap defect and ended having
changed the inferential instrument behind fourteen leaderboards, re-run 49
committed evaluations, corrected a published tie set from one member to ten,
retired a stale reliability flag affecting 91 of 337 conditions, and materialised
two new ground-truth references. Eighteen commits, `2907713f3` through
`a4abdb7ed`, on top of `3abec641a`. Most of it is corrective, several of the
corrections were themselves corrected mid-session, and the volume is high enough
that a quiet mistake would survive.

## How to work

1. **Read the primary artefacts, not my summaries.** Every claim below names the
   file that should support it. My prose is the thing under audit.
2. **Prefer re-derivation to re-reading.** Where a number is checkable, recompute
   it. Heavy compute goes on sapphire (`ssh sapphire`); the repo is synced.
3. **Report what you could not check**, and why. Silence about a gap reads as
   coverage.
4. **Separate three verdicts**: *wrong* (the claim fails), *unsupported* (may be
   true, evidence does not establish it), and *fragile* (true now, will break).
5. **Do not fix anything.** Report. The PI decides what lands.

## Part 1 — the claims most worth attacking

Ranked by consequence if wrong.

| # | Claim | Where it rests | Why it is worth attacking |
|---|---|---|---|
| 1 | Ten of fourteen board tie sets were wrong and are now corrected via Hsu MCB | erratum E83; `results/selection-aware/*.json`; `scripts/selection_aware_intervals.py` | It changes fourteen paper-facing claims. The critical value is an unverified bootstrap substitution (D24). If it is anti-conservative, the new sets are too small and I have replaced one wrong instrument with another. |
| 2 | `era1-leaderboard` has no sole leader; the leader's clique has six members | `results/era1-leaderboard/tiering_20m.json` (`pairwise`); `scripts/audit_tier1_cliques.py` | This retracts a headline. I verified all 15 pairs within the six are non-significant — re-derive that from the artefact independently. Check I did not confuse the BH-adjusted and raw columns. |
| 3 | Re-running 49 evaluations at B = 10,000 moved no point estimate | `results/bootstrap-10k-restandardisation.json`; git history of the 49 files | I gated on this at 1e-9 but wrote the gate myself. Diff the committed files against `HEAD~` directly and confirm only interval fields moved. |
| 4 | `ci_unreliable` now fires on measured grounds; sparse coverage alone does not | `scripts/evaluate_detections.py::assess_ci_reliability` | The old flag protected E72 partial coverage too. Confirm I did not weaken that path. Confirm the 1,041/1,041 containment result. |
| 5 | Selection optimism is negligible (≤ +0.0137 across 18 candidate sets) | `results/selection-aware/findings.md` | If the optimism estimator is wrong, every "corrected" figure is wrong. It is Efron–Gong with the argmax replayed — check the replay actually re-selects. |
| 6 | The four 55-map boards return tie sets identical to those published | `results/selection-aware/55map-*_b50_m1.json` | Convenient results deserve more scrutiny than inconvenient ones. Verify the reproduction gate really ran at 50 m and compared against 50 m. |
| 7 | Phase 0.3: the 256 px deficit survives a common footprint but "swamping" does not explain it | `results/phase0-recall-levers/tilesize-premise/findings.md` | The conclusion rests on precision AND recall both being lower. Check the common footprint is genuinely common and the carrier grids are what I claim. |

## Part 2 — the error classes found today, and where to hunt analogues

**This is the highest-value section.** Each class below was found once. Each is
almost certainly present elsewhere. Hunt the class, not the instance.

1. **A hard-coded constant published as a measurement.** `_metrics_from_eval`
   defaulted `n_iter = 10000` and its only caller never overrode it, so 49
   conditions declared an iteration count their source contradicted (D17). The
   sibling case — `_metadata.bootstrap.method`, a literal written
   unconditionally — was already known. *Hunt*: every default argument in a
   metadata-writing path; every field whose value is identical across artefacts
   that should differ.
2. **A hand-applied correction to a generated artefact.** Erratum E81's fixes
   were edited into the manifests, not into the generator or the schema, so
   regeneration silently reverted them and the committed file failed its own
   schema on 26 counts (D18). *Hunt*: any artefact edited by hand that a script
   also writes. Regenerate and diff.
3. **Validation that never validates the committed artefact.** The generator
   reported ALL VALID over rows it had just built, never over the file on disk,
   which is how (2) hid. *Hunt*: every "valid" claim — ask what object was
   validated.
4. **An algorithm whose docstring promises something it does not compute.**
   `greedy_clique_tiers` says `tiers[0]` is "the leader's clique"; it closes the
   tier at the first significant condition instead (D20). *Hunt*: docstrings
   asserting a mathematical property. Test the property.
5. **A flag detecting a pathology that was fixed years of commits ago.**
   `ci_unreliable` fired on a heuristic for a percentile-method failure that the
   same commit's BCa migration had already fixed. *Hunt*: every warning flag —
   does the condition it detects still occur?
6. **A summary that inverts the sign of a correct source.** I wrote "overlap
   helps" into a register row where the contrast is (12.5 % − 50 %) on
   single-pass counts, so the sign meant the opposite; the findings document was
   right throughout (`0611ce58a`). *Hunt*: every register outcome quoting a
   signed contrast. Check the sign convention against the source.
7. **A default parameter silently wrong for a subset.** The tiering harness read
   a fixed 20 m buffer; four boards are 50 m boards, and it reported gap = +0.17
   before I noticed. *Hunt*: every hard-coded buffer, threshold, or scope
   constant applied across heterogeneous inputs.
8. **A loader gap making committed data unreproducible.** Cells scored via
   `--batch` recorded the batch-level invocation, so 18 cells across two boards
   could not be reproduced at all (D22). Adapter-written evaluations have no
   `cli_args` whatsoever. *Hunt*: try to reproduce every committed evaluation
   from its own metadata; count the failures.
9. **One field with two committed shapes.** `tile_classification.mcc` is a block
   from the scorer and a bare float from the adapters. *Hunt*: fields read with
   `.get(...).get(...)` — each is a shape assumption.
10. **A field named as an identifier that is not one.** `uuid` in the 55-map
    student layer is a symbol code: 4,746 records, 839 values (D21). Previously
    flagged by the 2026-08-04 census and rediscovered here, which is itself a
    finding about how the project loses knowledge. *Hunt*: any join key. Check
    cardinality.
11. **A mixed-format numeric column.** `buffer_metres` holds `"50"` and `"50.0"`;
    `int()` raises on the decimals and catching it would drop 33 of 773 records.
    *Hunt*: string-typed numeric columns in every CSV that feeds a filter.
12. **A cross-scope comparison read as a like-for-like one.** The 256 px premise
    compared 1,032-tile and 487-tile scopes. Session 136 corrected this class
    four times; I found a fifth. *Hunt*: any two numbers compared in prose —
    confirm identical scope, buffer, and reference vintage.
13. **A derivation that looks right and reproduces nothing.** My first tile-MCC
    derivation gave a plausible 0.898 against a committed 0.790, because
    detections book to one tile and references to every tile they intersect.
    *Hunt*: every re-derivation in this session — does it reproduce a committed
    value, or only look reasonable?

## Part 3 — where I am least confident

Stated so you can weight your effort. These are my own doubts, not established
defects.

- **D24, the MCB critical value.** Fully briefed at
  `docs/methodology/mcb-critical-value-open-question.md`. A statistician is being
  sought. If you can assess coverage, that is the single most valuable thing you
  could do.
- **The optimism estimator.** Efron–Gong with the argmax replayed is standard,
  but I implemented it from a paper description rather than a reference
  implementation, and I got the interval construction wrong on the first pass
  (reporting the distribution of the selected cell rather than a location-shifted
  interval). The current version may still be subtly wrong.
- **The four 55-map boards agreeing exactly** with what was published. Four for
  four is a good outcome and I did not interrogate it hard.
- **`h12-v2-hp-hn-ratio` going 3 → 6 of 6 candidates admissible.** The whole
  board is admissible, which may be correct on six cells at n = 327, or may
  indicate the critical value is too wide there.
- **Whether the E83 tie-set replacement should have touched MCC-tiered boards
  using the F1 statistic or the MCC statistic.** I used each board's own metric.
  Check that against what each board's outcome text actually claims.

## Part 4 — checks I did NOT run

Absence here is not safety.

- No audit of whether any published number depends on a `uuid` join (D21).
- No re-emission of committed BCa intervals outside the 49 register-backing ones;
  `archive/` and pre-2026-04-30 artefacts were deliberately left (E82).
- No verification that the two-sided band and Hsu construction agree on
  *membership* rather than size, board by board.
- No check that `results-draft.md`'s four `[E83]` flags are the complete set of
  affected sentences — I grepped for a handful of patterns.
- No coverage simulation for anything.
- Tier-1 suite only (1,593 passing); tier-2 was never run this session.

## Part 5 — what "done" looks like

A report with:

1. **Findings**, each classified *wrong* / *unsupported* / *fragile*, with the
   artefact and the re-derivation that establishes it.
2. **New instances of the Part 2 classes**, which is the main deliverable.
3. **Claims you checked and confirmed**, with the check — so the PI can tell
   coverage from silence.
4. **What you could not check**, and what it would take.

Do not open a defect register row or edit an erratum. Hand the PI a report.

## Reference

- Session commits: `2907713f3`..`a4abdb7ed` (18), parent `3abec641a`
- Errata filed: **E82** (bootstrap deviations), **E83** (tie-set instrument)
- Defects opened: D17, D18, D19, D20, D21, D22, D23, D24; N1b
- Defect register: `reports/defect-register-2026-08-18.md`
- Key findings: `results/selection-aware/findings.md`;
  `results/phase0-recall-levers/tilesize-premise/findings.md`
- Policy written: `docs/methodology/inference-instrument-policy.md`;
  `docs/methodology/tile-mcc-explained.md`
- Compute: sapphire (`ssh sapphire`), venv at `.venv`, repo synced

## Changelog

### 2026-08-19 — Original publication

Written at the close of Session 137 by the instance that performed the work, at
the PI's request, for an audit the following day. Structured around error
*classes* rather than a checklist of my conclusions, because the classes are what
generalise and my conclusions are what I already believe.
