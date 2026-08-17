# S134 D17 reconciliation — PI walk dossier

> **Last revised**: 2026-08-17 (original publication). See
> [§ Changelog](#changelog) for revision history.

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

## Changelog

### 2026-08-17 — Original publication

Dossier authored at block execution close (Items 1–5 committed,
`dfb0eb4ad` → `ac9eb88b1`); blind verifier and code audit in flight,
to be appended as § 7 when they report.
