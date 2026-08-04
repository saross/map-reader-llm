# Wave-7 draft stories — pre-registered before the blind passes

**Date**: 2026-08-04 · **Session**: 127 (48-hour Opus window) ·
**Author**: the wave-7 triager (Claude Opus 5)

Ruling 11 requires the triager's causal stories to be written down
*before* independent blind passes run, so the blind layer can correct
them rather than confirm them. In both Session-126 waves the blind
layer did correct the triager — six and seven consecutive corrections
across the programme — so these are hypotheses on the record, not
findings.

**Scope**: the 206 wave-7 MISMATCH rows from the canonical post-wave-7
recompute (`ce76fffb9`, 16,083 rows). Wave-7 rows resolve
1,577 MATCH / 206 MISMATCH / 272 UNRESOLVED / 1,040 SKIPPED.

**Standing constraint**: under this session's interim conservatism no
adjudication lands. Every disposition below, and whatever the blind
passes make of it, goes to the PI queue.

---

## Family A — `results/documentation-audit/**` (182 rows, 88 %)

**Draft story: dated-snapshot divergence, not defects.** All four
documents are dated 2026-04-21 audit records. Their figures were
faithful to the artefacts as they stood in April; the artefacts have
since moved through the recovery campaign, the token-load audit's
re-pricing, and the W6-E9 de-dup regeneration. The signature is
unmistakable — `090-audit-summary#9[1]` quotes total spend `$552.30`
against an actual `$438.61`, and its component rows quote `$364.70`
for image against `$200.83` and `$126.81` for text-HIGH against
`$207.34`. Those two actuals are precisely the audited costs that
drove escalation W6-E1, so this family is the April document meeting
the July audit.

**Predicted disposition**: SNAPSHOT-DIVERGENCE under rulings 1 and 14,
ledger-only, no repair. Ruling 17's two-layer rule then asks whether
any of these four is a *living* document in `results/**.md` scope
rather than a dated snapshot — if so it takes an in-place refresh
instead. That is the sub-question most likely to be where the draft
story is wrong.

**What would falsify it**: any row whose quoted figure never matched
the artefact at the document's own era. That is a defect-at-era, not
divergence, and needs the era check rather than a banner.

## Family B — bootstrap iterations, 1,000 quoted vs 10,000 actual (8 rows)

`083#5[0]`, `083#11[0]`, `083#56[0]`, `083#63[0]`, `087#2[2]`,
`087#3[2]`, `087#4[2]`, `087#5[1]`.

**Draft story: a 10,000-iteration re-run superseded the 1,000-iteration
original, and the documents were never refreshed.** `scripts/`
contains `verify_bootstrap_10k_followup.py`, which makes a deliberate
10k follow-up the most economical explanation.

**Why this family is flagged HIGHER than its row count suggests**: a
bootstrap iteration count is a *methods* parameter, not a result. If
any paper-facing text says 1,000 while the artefacts say 10,000, that
is a live Methods inaccuracy, not a stale snapshot — and it is exactly
the class the run-it-now policy (GATE 1 ruling (c)) cares about. The
blind pass should establish which number the reported CIs were
actually computed from, and whether `083`/`087`'s host documents are
paper-citable.

## Family C — canonical GT count, 4,744/4,745 quoted vs 4,746 actual (6 rows)

`083#3[1]`, `083#8[0]`, `083#17[2]`, `083#29[1]`, `083#58[0]`,
`099#10[0]`.

**Draft story: the W6-E9 de-dup fix chain
(`1de559119` → `30a902f56` → `fcfc90bff`) moved the canonical
ground-truth count by one, and these documents predate it.** Same
mechanism as the 20 channel-accounting rows that flipped
MATCH → MISMATCH on pre-wave claims at this join, where the count
signature was TP +1, FP −1, GT 4745 → 4746.

**Predicted disposition**: divergence caused by a landed, PI-approved
correction; ledger-only for dated documents, in-place refresh for
living ones. Note `099#10[0]` sits in the newly-surveyed 240-tile
section of `evaluation-scopes.md`, so it has never been triaged before.

## Family D — 0.8332 / 0.832 quoted vs 0.833333 actual (2 rows + 3 pre-wave)

`083#34[1]`, `098#49[1]`, plus the three pre-wave ds-summary rows
`073#60[1]`, `074#9[1]`, `074#28[2]` that flipped MATCH → MISMATCH.

**Draft story: the S126 repair pass standardised on `0.8332` while the
regenerated artefact yields `0.833333…`, which rounds to `0.8333`.**
The corrected-f1 report's own 50 m row now reads **0.8333**. So two
living documents disagree in the fourth decimal, and the ds-summary
side is the one out of step.

**This is escalation material, not a triage disposition** — see
W7-E4. Immaterial to any conclusion, but a cross-document
inconsistency the ledger should not silently absorb.

## Family E — small count and rate discrepancies (8 rows)

`084#29[0]` (17 vs 18 false positives), `085-high-pull#9[13]` (3 vs 4
detections) and `#9[14]` (33 % vs 0.25), `086#22[0]` (52 vs 54
comparisons), `086#37[0]` (19 vs 36 conditions), `090-audit-summary#15[3]`
(cache hit 91.0 vs 0.9287), plus the `080#42[0]` / `099#16[0]` headline
F1 rows (0.771 vs 0.7745; 0.788 vs 0.7921).

**Draft story: mixed, and the least confident family.** Three
sub-hypotheses, deliberately not merged:

1. *Scope mismatch* — `086#37[0]`'s 19-vs-36 gap is too large for
   drift and looks like the document counting a filtered subset while
   the anchor counts the whole collection.
2. *Unit bridging* — `#9[14]`'s "33 %" against `0.25` and the cache-hit
   `91.0` against `0.9287` are percentage-versus-fraction shapes, but
   note that bridging the unit does **not** reconcile either pair
   (33 ≠ 25, 91.0 ≠ 92.87), so a genuine value difference sits
   underneath the unit question.
3. *Post-recovery drift* — the headline F1 rows quote pre-recovery
   values.

**What would falsify the whole family**: finding a single shared cause.
It is registered as three sub-hypotheses precisely so that a blind pass
collapsing them into one is visible as a correction.

---

## Registered predictions (so the blind passes can score them)

1. Family A resolves overwhelmingly to divergence, with **fewer than 10**
   rows turning out to be defects-at-era.
2. At least one of the four `documentation-audit` documents is judged a
   living document under ruling 17 rather than a dated snapshot.
3. Family B is confirmed as a 1k → 10k supersession, and at least one
   host document proves paper-citable.
4. Family E does **not** collapse to a single cause.
5. No wave-7 row requires a research conclusion to move.

Prediction 5 is the one worth watching: the wave-6 experience was that
the interesting finding arrives in the family the triager was least
sure about, which here is Family E.
