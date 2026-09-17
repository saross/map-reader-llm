# Legacy-signature review queue

> **Last revised**: 2026-09-16 (PI ruling: all 50 legacy-stamped rows go
> to the queue, not just the 23 that drifted). See
> [§ Changelog](#changelog) for revision history.

Until 2026-09-16 one field, `manually_verified_at`, served both authoring and
signature (`docs/methodology/signature-policy.md`). **50 register rows carry a
stamp from that period.** Asked whether those stamps represent his review, the
Principal Investigator (PI) said he is not confident they do — so none of them
is treated as a signature. All 50 are `unsigned` and queued here for a FIRST
signature.

**They are 18 walkthroughs, not 50.** Every row was stamped, or moved, in a
batch operation, and the batch is the natural unit of review.

## Part A — stamped, and unchanged since

25 rows whose substance has not moved since they were stamped. The PI reads
them as they stand. Grouped by the commit that set the stamp; several of those
commits describe a PI sign-off in their own message, which is context for the
review, not a substitute for it.

### A1. `60b246994` — 2026-08-17 · 6 row(s) — **SIGNED 2026-09-17**

> feat(register): S134 walk rulings applied — E78, s8-9 row, fences, stamps

Evidence: PI sign-off described in the commit message.

- [x] Walkthrough prepared
- [x] PI signed

- `h10-pool-size`
- `h14-cross-model-consistency`
- `h15-cross-model-voting`
- `h2-condition-c-fine-to-coarse`
- `h6-phase4-transfer`
- `s8-9-post-experiment-verification`

### A2. `6a97da344` — 2026-08-17 · 1 row(s) — **SIGNED 2026-09-17**

> docs(register): S135 L4 walk part 1 — three PI rulings applied

Evidence: PI sign-off described in the commit message.

- [x] Walkthrough prepared
- [x] PI signed

- `e45-bootstrap-pairings`

### A3. `75a6b190c` — 2026-08-17 · 1 row(s) — **SIGNED 2026-09-17**

> docs(register): H6 rows ratified post-hoc and stamped (S135 L4 walk)

Evidence: PI sign-off described in the commit message.

- [x] Walkthrough prepared
- [x] PI signed

- `h6-a06-decision-rule`

### A4. `667561e65` — 2026-08-28 · 3 row(s) — **SIGNED 2026-09-17**

> registry(pass3): PI sign-off — registration backlog CLEAR

Evidence: PI sign-off described in the commit message.

- [x] Walkthrough prepared
- [x] PI signed

- `h7-escalation-2026-08-28`
- `image-b-modality-2026-08-28`
- `image-b-thinking-pair-2026-08-28`

### A5. `b2949c27e` — 2026-08-28 · 5 row(s) — **SIGNED 2026-09-17**

> registry(pass1): PI sign-off — all five analyses verified

Evidence: PI sign-off described in the commit message.

- [x] Walkthrough prepared
- [x] PI signed

- `stride-plateau-2026-08-25`
- `stride-winner-ladder-exact-2026-08-25`
- `stride55-a5-vs-b5-2026-08-27`
- `stride55-ladder-2026-08-27`
- `stride55-sweep-oracle-2026-08-27`

### A6. `e84b4e592` — 2026-08-28 · 2 row(s) — **SIGNED 2026-09-17**

> registry(pass2): PI sign-off — final board + sensitivity verified

Evidence: PI sign-off described in the commit message.

- [x] Walkthrough prepared
- [x] PI signed

- `55map-final-board-2026-08-27`
- `sensitivity-mde-2026-08-28`

### A7. `60bac9fb8` — 2026-09-07 · 5 row(s) — **SIGNED 2026-09-17**

> register(r2): eight analysis rows, PI-signed 2026-09-07

Evidence: PI sign-off described in the commit message.

- [x] Walkthrough prepared
- [x] PI signed

- `55map-final-board-r2-2026-09-06`
- `55map-r2-leaderboard-50m`
- `55map-r2-leaderboard-mcc-50m`
- `obs280-shared-reference-r2`
- `tile-level-f1-r2`

### A8. `38aa9ed1b` — 2026-09-08 · 1 row(s) — **SIGNED 2026-09-17** (after separate review)

> register(h6): A-07 and A-09 refreshed on the recovered comparator; e47 rows re-pointed

Evidence: no sign-off language in the commit message.

- [x] Walkthrough prepared
- [x] PI signed

- `h6-a09-cost-gate`

### A9. `da37c642c` — 2026-09-08 · 1 row(s) — **SIGNED 2026-09-17**

> merge main into schema/reference-level-diagnostics; manifests regenerated

Evidence: no sign-off language in the commit message.

- [x] Walkthrough prepared
- [x] PI signed

- `student-baseline-r2`

## Part B — stamped, then moved

25 rows whose substance changed in a commit AFTER the stamp, so even a review
at stamping time would not cover what stands there now. Grouped by the pass
that moved them, and annotated with the fields that actually changed, counted
from the diff at that commit. **CLAIM** marks a batch that altered a finding;
**BOOKKEEPING** one that did not.

### B1. `60b246994` — 2026-08-17 · 2 row(s) · **CLAIM**

> feat(register): S134 walk rulings applied — E78, s8-9 row, fences, stamps

Fields moved: `_note` x1, `outcome` x1

- [x] Walkthrough prepared
- [x] PI signed

- `family-bh-fdr-confirmatory`
- `phase3c-diversity-calibration`

### B2. `f54dc6787` — 2026-08-17 · 7 row(s) · **CLAIM**

> feat(manifest): preregistered vocabulary v2 + 24-row relabel (D17)

Fields moved: `_prereg_rationale` x7, `deviations` x4, `preregistered` x7

- [x] Walkthrough prepared
- [x] PI signed

- `e43-matched-temperature`
- `h1-cmt0106-pooled-modality`
- `obs280-shared-reference`
- `phase3a-consensus-calibration`
- `phase3a-high-consensus-calibration`
- `phase3a-replication-thinking-calibration`
- `unswept-pools-completeness`

### B3. `1908d7917` — 2026-08-19 · 4 row(s) · **CLAIM**

> feat(55map): re-tier all four boards; document Track 3; fix uuid naming

Fields moved: `outcome` x4

- [x] Walkthrough prepared
- [x] PI signed

- `55map-canonical-leaderboard-50m`
- `55map-canonical-leaderboard-mcc-50m`
- `55map-standardised-leaderboard-50m`
- `55map-standardised-leaderboard-mcc-50m`

### B4. `85a442e96` — 2026-08-19 · 1 row(s) · **CLAIM**

> feat(gt): merged 55-map reference; recover 2 boards; document tile MCC

Fields moved: `outcome` x1, `tie_set` x1

- [x] Walkthrough prepared
- [x] PI signed

- `diversity-dividend-384`

### B5. `ee0a381ff` — 2026-08-19 · 4 row(s) · **CLAIM**

> fix(d20): re-tier eight boards to Hsu MCB; file E83

Fields moved: `outcome` x4, `tie_set` x4

- [x] Walkthrough prepared
- [x] PI signed

- `flash35-model-roles`
- `h12-v2-hp-hn-ratio`
- `min-vs-high-thinking-pv`
- `verifier-robustness-matrix`

### B6. `fe797a6d5` — 2026-08-20 · 3 row(s) · **CLAIM**

> fix(register): n1-384 tie set 4->3; five REVISED markers; h13 billed

Fields moved: `outcome` x3, `tie_set` x1

- [x] Walkthrough prepared
- [x] PI signed

- `era1-leaderboard`
- `n1-baseline-matrix-384`
- `pass-budget-pareto`

### B7. `506c02874` — 2026-09-07 · 1 row(s) · **CLAIM**

> chore(register): the one manifest regeneration; two r2 rows corrected, one held

Fields moved: `_conditions_note` x1, `conditions_compared` x1

- [x] Walkthrough prepared
- [x] PI signed

- `sensitivity-mde-r2`

### B8. `6844fb182` — 2026-09-08 · 1 row(s) · **CLAIM**

> fix(register): the estimated column's shift stated precisely (E84 correction)

Fields moved: `outcome` x1

- [x] Walkthrough prepared
- [x] PI signed

- `estimated-correction-r2`

### B9. `f77d9078c` — 2026-09-14 · 2 row(s) · **BOOKKEEPING**

> fix(register): repair run-analyses.json after a mis-resolved merge

Fields moved: see the diff

- [x] Walkthrough prepared
- [x] PI signed

- `era1-single-pass-baseline-matrix`
- `tile-size-sweep`

## What each walkthrough needs

Per the policy — not a summary, but the material the PI needs in order to
disagree:

1. **The row's current claim**, verified against its artefact independently of
   whatever produced it.
1. **For Part B, what the pass changed**, field by field, read from the diff
   rather than from the commit message, and whether it altered a claim or only
   bookkeeping.
1. **Scope limits** — anything the signature will not reach.
1. **Anything that looks wrong, weak or over-stated.**

## Changelog

### 2026-09-17 — A8 signed after separate review; Part A complete

`h6-a09-cost-gate` signed. The hold was warranted by an unexplained
asymmetry — one commit refreshed A-07 and A-09 together, A-07 was
re-signed two days later, A-09 was not — and the explanation proved
benign.

Reading the artefact against its archived pre-refresh copy showed the
refresh moved exactly ONE quantity: the Flash matched-configuration
comparator's N=3 consensus F1 rose 0.552454 to 0.585411 when recomputed
against recovered evidence, lowering the image F1 ratio from 1.2052 to
1.1373. Pro's F1 and both cost figures are unchanged.

**No verdict moved.** `registered_gate_verdict` is CLOSED in both, and
`limb1_fires` is False in BOTH: the 1.20 F1 threshold the ratio crossed
was never the binding condition, because limb 1 also requires comparable
cost and the 1.3207 cost ratio already failed the declared ±10% window.
An agent first presented the crossing as changing the limb's behaviour;
the PI's questioning established it did not. The comparator got stronger
and the margin to the threshold is wider than before.

Part A is complete: 25 of 25 signed. Register tally: 42 signed, 26
unsigned, 1 unsigned-by-design.

### 2026-09-17 — Part A signed, 24 of 25; A8 held

The PI approved Part A as a batch after a written walkthrough grouping its
rows by the strength of the evidence behind each stamp: sixteen rows whose
commit message records an explicit PI sign-off, eight from "rulings
applied"/"ratified" commits (five of which are NOT EXECUTED dispositions
recording an absence rather than a finding), and one held.

**`h6-a09-cost-gate` (A8) is HELD.** Its stamp comes from
`38aa9ed1b`, "register(h6): A-07 and A-09 refreshed on the recovered
comparator", which carries no sign-off language. What marks it out is not the
missing phrase but the asymmetry: that commit refreshed A-07 and A-09
together, the PI re-signed A-07 two days later with a proper signature note,
and A-09 never received one. Its sibling was reviewed after the refresh; it
was not.

The A9-tagged row (`student-baseline-r2`) was signed WITH A7. Tracing its
stamp to its origin puts it in the `60bac9fb8` "PI-signed 2026-09-07" batch;
the merge commit `da37c642c` that this document originally credited had only
rewritten the file later. Register tally after signing: 41 signed, 27
unsigned, 1 unsigned-by-design.

### 2026-09-16 — PI ruling: all 50 rows queued

The original migration split the 50 legacy rows, sending 25 unchanged ones to a
`legacy-signed` status on the reading that their review had happened and only
its scope went unrecorded. The PI ruled that he cannot confirm he reviewed
them, so that reading is not supported and the status was retired: all 50 are
`unsigned` and all 50 are queued. Part A (25 rows, 9 batches) is new; Part B
(25 rows, 9 batches) was the original queue, now including the two rows
previously held out.

### 2026-09-16 — Original publication

Created by the signature migration, covering the 23 rows that had drifted after
their stamp.
