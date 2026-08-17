# S134 D17 reconciliation — PI walk dossier

> **Last revised**: 2026-08-17 (verification reports landed; § 7
> added; corrections applied). See [§ Changelog](#changelog) for
> revision history.

**Purpose**: the L4 operator gate for the S134 D17 reconciliation
block (`planning/s134-d17-reconciliation-block-2026-08-17.md`). All
five block items are executed and committed; this dossier is the
walk: ratify or overturn the provisional rulings, adjudicate the
flagged rows, and close the unexecuted-set dispositions. Every claim
below carries its anchor; the blind verifier's report (separate,
fresh-context) should be read alongside.

**State at writing**: register = 31 rows (3 confirmatory-with-
deviation, 5 registered-exploratory, 18 post-hoc, 5 not-executed),
0 retired values, 0 nulls; manifest ALL VALID, drift warnings 208 =
pre-block baseline; tier-1 suite 1,471 passing; table generated
15/15 (`results/hypothesis-outcome-table/`). Commits `dfb0eb4ad` →
`ac9eb88b1`.

## 1. The headline sort (ratify)

Applying your strictness rule, the 24 relabelled rows sorted as: the
two previously-`preregistered` rows plus `diversity-dividend-384`
became **confirmatory-with-deviation**; three became
**registered-exploratory** (`phase3a-consensus-calibration`,
`phase3c-diversity-calibration`, `tile-size-sweep`); eighteen became
**post-hoc**. The minority-moves expectation held. Every row carries
a `_prereg_rationale` with prereg/errata anchors in
`results/run-analyses.json`.

Two rulings folded in from the pre-run dialogue (hardening 5):

- `h1-cmt0106-pooled-modality` and `family-bh-fdr-confirmatory` both
  carry non-empty deviations arrays, so under strictness both are now
  `confirmatory-with-deviation` (not bare `confirmatory`). **Ratify
  or overturn.**
- `diversity-dividend-384` was upgraded to confirmatory-class on a
  decisive fact: the family BH-FDR's H3 headline contrast is sourced
  from its tiering output
  (`reports/verification/family-fdr-registration.md:698`, marked
  SELECTED) — it is part of the confirmatory chain. Its deviations
  field keeps the three prose entries including the argued
  no-deviation note.

## 2. Flagged rows needing your ruling (5)

1. **`diversity-dividend-384` outcome fence.** The row's outcome
   opens "Both named claims of the diversity-dividend test are
   confirmed", but claim 1 (the HIGH-vs-MINIMAL thinking dividend) is
   post-registration — thinking level is fixed at minimal by the
   registration (`osf/preregistration.md:1211-1212`, `:2135`; D17
   sweep U5 rates the mislabelling "reaches the paper"). Proposal:
   amend the outcome prose to fence claim 1 as post-hoc while claim 2
   (consensus vs single-pass) stays the registered H3 result. The row
   is PI-signed, so the amendment needs your explicit approval.
2. **`pv-diag-384-consensus-calibration` → post-hoc.** It implements
   the registered H3 sweep method verbatim but over unregistered
   production carry-forward pools (HIGH thinking). The D17 inventory
   thought `preregistered-with-deviation` defensible
   (`d17-inventory-h1-h4.md:836-843`); strictness says post-hoc.
   **Confirm post-hoc or move to registered-exploratory.**
3. **`phase3a-high-consensus-calibration` and
   `phase3a-replication-thinking-calibration` → post-hoc.** Same
   tension: registered sweep grid, unregistered contrast dimension
   (thinking). Strictness applied. **Confirm.**
4. **`era1-leaderboard` → post-hoc, with H2 added to
   `hypothesis_refs`.** The D17 inventory found the registered H2
   contrast's result sitting on this row ("PROPOSER-VERIFIER IS THE
   SINGLE BEST ERA-1 ARCHITECTURE") while the row did not claim H2
   (`d17-inventory-h1-h4.md:476-484`, `:617-619`) — the ref is now
   added. The inventory's alternative was to attach a
   confirmatory-class label *here*; I kept the board post-hoc because
   the confirmatory H2 adjudication lives at
   `family-bh-fdr-confirmatory` and boards are characterisation.
   **Confirm the division of labour.**
5. **`n1-baseline-matrix-384` H6 ref.** The inventory recommends
   removing `H6` from its `hypothesis_refs` ("the cleanest encoding",
   `d17-inventory-h5-h8.md:474-476`) now that `h6-phase4-transfer`
   carries H6's disposition. Not applied — refs were out of the
   ruled relabelling scope. **Rule: remove or keep.**

## 3. Factual defects surfaced by the evidence pass (3)

1. **`phase3c-diversity-calibration` p-value mis-slot** (signed row):
   its outcome says condition D "was not significant (p~0.06)", but
   the source gives D-vs-A p = 0.1812; 0.0610 belongs to B-vs-A and
   E-vs-A (`d17-inventory-h9-h12.md:305-311`). Needs an outcome
   correction under your sign-off.
2. **`docs/paper/results-draft.md:121`** cites the diversity dividend
   as "both preregistered" — the half that is the thinking dividend
   is not (U5). A prose-drafting fix; queued for the drafting pass.
3. **`docs/methods-outline.md:343-350`** ("What the Preregistration
   Planned but Was Not Executed") is stale in both directions: it
   omits H13 entirely and still lists H10 and H12, which ran to
   completion and now have register rows. Queued for refresh against
   the generated table.

## 4. Erratum wording review (gate)

New disclosures awaiting your wording approval (commit `67627978a`):
**E74** (H6 — never executed, deferral never ratified), **E75** (H13
— silently dropped; cannot shelter under the Tier C deferred
framing), **E76** (H14 — deferral honoured + three qualifications,
including the `preregistration-coverage.md:163` correction needed
before supplement publication), **E77** (H15 — gated on H14;
cascade-vs-vote boundary; the mixed-pool provenance hazard), and the
**E59 dated Update** (H2-C residual facts: missing `expand_*`
artefacts, unevaluable registered limbs, the Strategy-10
approximation, the stale 37 %-recall premise, precise omission
dating). Revise via new commits as needed.

## 5. The unexecuted-set adjudication (hardening 7)

Run or formally close, per obligation. The unexecuted register's
recommendations (`reports/d17-inventory/unexecuted-register.md`) for
context; any "run" ruling becomes a gated future item with its own
phase-gate/audit-config — nothing executes in this $0 block.

| Obligation | Cost to run | Register's read | Your ruling |
|---|---|---|---|
| H6 Phase 4 as registered | ~US$48 max (`studies/phase4-transfer.yaml:165`) + E40 confound persists | Do the **$0 analyses first** (A-06 decision rule, A-07 voting comparison, A-09 cost gate, on the existing Pro data), then decide (Tier 1 item 2; arguable call 2) | ☐ |
| H13 arms B+C | ~$6-8 (pre-lodgement estimate — re-price) | Cheapest unexecuted experiment, weakest decision trail; "a PI who weights disclosure exposure over effort should promote it" (arguable call 3) | ☐ |
| H14 | ~$40-60 (stale) | **Disclose only** (Tier 3 item 21) | ☐ |
| H15 | gated on H14 | **Disclose only**; the $0 within-Gemini analogue is provenance-gated (arguable call 6) | ☐ |
| H2 Condition C | ~1-1.5 days build + unpriced 1024 px API (needs a pricing run) | Run vs disclose-as-superseded: "reasonable people differ" (arguable call 5); the stale 37 % premise argues for re-measurement | ☐ |

## 6. Sign-offs pending

- `h10-pool-size` and `h12-v2-hp-hn-ratio` (`manually_verified_at`
  null — outcomes authored from the committed analysis summaries,
  both null as the D17 inventory expected).
- The five disposition rows (cheap: each is a one-line disposition).
- The 22 previously-signed rows whose `preregistered` value changed
  keep their original stamps; this walk is the ratification record
  for the label changes (re-stamping optional — your call).

## 7. Verification reports (blind verifier + code audit)

Both ran as fresh-context Opus agents after the block's five items
were committed; denominators reported by both.

### 7.1 Blind classification verifier

Cold-derived all 31 row labels and all 15 hypothesis dispositions
from the prereg/errata/inventories before reading the committed
values (denominator: 166/166 claims re-derived; 105/105 table cells
confirmed by an independent script; all 15 `osf:` anchors and all 28
cited E-numbers resolve). Result: **26 AGREE, 3 DISAGREE — two
conceded to the committed (stricter) labels, one upheld**:

- **Upheld disagreement — `diversity-dividend-384`** (walk item 2.1
  gains an adversarial position): the verifier derives `post-hoc` on
  the grounds that two of its three headline claims are unregistered
  (thinking contrast; cross-architecture tie), its corpus is the
  Era-2 487-tile/384 px substitution E41 itself calls "an exploratory
  extension", and the register's own seam (pv-diag-384-calibration =
  post-hoc on the same pools) sits on the other side. The
  counter-position (mine, which the verifier could not dismiss): its
  claim 2 IS the registered H3 confirmatory contrast, and the family
  BH-FDR sources its H3 headline p-value from this row's tiering
  output — demoting it without demoting the family row creates the
  opposite inconsistency. **Downstream impact of either ruling: zero
  table cells.** Your adjudication under the disagreement rule.
- The two conceded disagreements (era1 boards: verifier initially
  derived registered-exploratory, conceded to post-hoc under the
  strictness rule) surface one consequence to see plainly: **H4, H5,
  H7, and H8 each rest on exactly one registered-analysis row — the
  family BH-FDR — with no per-hypothesis analysis row.** The table
  displays this honestly.

Further verifier findings, dispositioned:

- **H11 under-disclosure (corrected)**: `tile-size-sweep` compares
  `pv-diag-256` conditions (E62 names that run) at best-prob_t
  operating points (E56) — both now added to its deviations; E62
  likewise added to the three post-hoc rows analysing
  `verifier-robustness` conditions.
- **§ 8.9 post-experiment verification** (`osf:2139-2145`): a
  registered obligation with no H-number — full-Hungarian
  confirmatory comparison of F1/latency/tokens at the optimal
  configuration — has no register row; its closest execution
  (`min-vs-high-thinking-pv`, post-hoc) lacks the latency limb. The
  register's single-source-of-truth claim is currently **H-scoped**.
  **Walk item: mint a named-programme disposition/analysis row, or
  record the H-scope limitation explicitly.**
- **Family row hygiene**: `family-bh-fdr-confirmatory`'s
  `conditions_compared` (12 conditions ≈ 6 pairs) carries no pair for
  H3's input (sourced from diversity-dividend-384's tiering artefact)
  and H1's input is the CMT-0106 artefact — the row cannot be audited
  to its inputs from the manifest alone. Walk item: curate the list
  or note the artefact-sourced inputs in the row.
- Could-not-verify (inherited limits, no action this block): the
  family's five "registered artefact (re-read and asserted)" input
  p-values; whether H5's family input used the registered
  precision-primary; statistics inside outcome free text.

### 7.2 Code audit

Independently re-implemented the projection and confirmed **all 15
rows × 5 projected fields, 0 mismatches**; verified the schema
conditional across 10 probe cases; confirmed all 8 author-script
literal placements. Findings and dispositions:

- **Fixed (2 high)**: exclusion verdict now derived structurally from
  the family row's `hypothesis_refs` with the prose as a cross-check
  (a rewording can no longer silently convert "never run" into "not
  rejected"); the deviations union now extracts E-numbers from within
  prose entries (E49 — previously silently dropped from H3's cell —
  now surfaces from diversity-dividend-384's prose array).
- **Fixed (7 medium)**: `--check` false-STALE when git is absent;
  unadjudicated (null) rows now abort loudly instead of vanishing;
  the uncovered-hypothesis error message no longer misdiagnoses the
  null case; the near-vacuous live test replaced with real MD/JSON
  equality assertions; the post-hoc-only failure mode now genuinely
  pinned; single-rejection-clause and confirmatory-membership guards
  added to the family parse; `n1-baseline-matrix.md:414` updated to
  the v2 label with a dated note.
- **Fixed (4 low)**: reverse schema conditional (`type: disposition`
  now forces `not-executed` — fault-injection verified); git call
  timeout; hard-coded count in `--check` output; a "register rows
  outside the hypothesis frame" section added to the table (the five
  no-hypothesis rows are no longer invisible).
- **Not corrected (reported per the audit gate)**: L-2 nested-brace
  truncation in the rejection-set regex (fails loudly already — the
  audit itself recommends no fix); L-3's second half (the generation
  stamp records HEAD but not dirty-tree state — accepted; the
  `--check` guard covers the practical risk); L-5 (the generator-map
  rule's regex covers `.json` but the registry only indexes `.md` by
  design — cosmetic; and `--check` is exercised by the strengthened
  tier-1 test rather than a separate CI hook).

## Changelog

### 2026-08-17 (later) — Verification landed, corrections applied

Blind verifier: 26/31 AGREE, 2 conceded, 1 upheld
(diversity-dividend-384 → walk item 2.1); 105/105 table cells
confirmed. Audit: 2 high + 7 medium + 4 low corrected, 3 lows
accepted with reasons (§ 7.2). Register deviations completed on four
rows (E56/E62); table regenerated; full battery green.

### 2026-08-17 — Original publication

Dossier authored at block execution close (Items 1–5 committed,
`dfb0eb4ad` → `ac9eb88b1`); blind verifier and code audit in flight,
to be appended as § 7 when they report.
