# Legacy-signature re-signing queue

> **Last revised**: 2026-09-16 (original publication — the 23
> `re-sign-pending` rows, grouped by the pass that moved them). See
> [§ Changelog](#changelog) for revision history.

The 2026-09-16 signature migration (`docs/methodology/signature-policy.md`)
found 23 register rows whose substance changed in a commit AFTER the timestamp
that was, under the old convention, their signature. Those stamps now vouch for
text nobody read, so each row is `re-sign-pending`.

**They are 8 conversations, not 23.** Every one moved in a systematic pass
whose commit message already says what it did and why, so the Principal
Investigator (PI) reviews the PASS and signs its rows together — which is what
the old batch timestamps were implicitly doing, minus the record.

Each batch below names the fields that actually moved, counted from the diff at
its commit. **CLAIM** marks a batch that changed a finding — a rewritten
`outcome`, a changed `tie_set`, a re-classified `preregistered` — which is a
scientific statement the old signature never covered. **BOOKKEEPING** marks one
that did not. Take the CLAIM batches first.

## The queue

### 1. `60b246994` — 2026-08-17 · 2 rows · **CLAIM**

> feat(register): S134 walk rulings applied — E78, s8-9 row, fences, stamps

Fields moved: `_note` ×1, `outcome` ×1

- [ ] Walkthrough prepared
- [ ] PI signed

- `family-bh-fdr-confirmatory`
- `phase3c-diversity-calibration`

### 2. `f54dc6787` — 2026-08-17 · 7 rows · **CLAIM**

> feat(manifest): preregistered vocabulary v2 + 24-row relabel (D17)

Fields moved: `_prereg_rationale` ×7, `deviations` ×4, `preregistered` ×7

- [ ] Walkthrough prepared
- [ ] PI signed

- `e43-matched-temperature`
- `h1-cmt0106-pooled-modality`
- `obs280-shared-reference`
- `phase3a-consensus-calibration`
- `phase3a-high-consensus-calibration`
- `phase3a-replication-thinking-calibration`
- `unswept-pools-completeness`

### 3. `1908d7917` — 2026-08-19 · 4 rows · **CLAIM**

> feat(55map): re-tier all four boards; document Track 3; fix uuid naming

Fields moved: `outcome` ×4

- [ ] Walkthrough prepared
- [ ] PI signed

- `55map-canonical-leaderboard-50m`
- `55map-canonical-leaderboard-mcc-50m`
- `55map-standardised-leaderboard-50m`
- `55map-standardised-leaderboard-mcc-50m`

### 4. `85a442e96` — 2026-08-19 · 1 row · **CLAIM**

> feat(gt): merged 55-map reference; recover 2 boards; document tile MCC

Fields moved: `outcome` ×1, `tie_set` ×1

- [ ] Walkthrough prepared
- [ ] PI signed

- `diversity-dividend-384`

### 5. `ee0a381ff` — 2026-08-19 · 4 rows · **CLAIM**

> fix(d20): re-tier eight boards to Hsu MCB; file E83

Fields moved: `outcome` ×4, `tie_set` ×4

- [ ] Walkthrough prepared
- [ ] PI signed

- `flash35-model-roles`
- `h12-v2-hp-hn-ratio`
- `min-vs-high-thinking-pv`
- `verifier-robustness-matrix`

### 6. `fe797a6d5` — 2026-08-20 · 3 rows · **CLAIM**

> fix(register): n1-384 tie set 4->3; five REVISED markers; h13 billed

Fields moved: `outcome` ×3, `tie_set` ×1

- [ ] Walkthrough prepared
- [ ] PI signed

- `era1-leaderboard`
- `n1-baseline-matrix-384`
- `pass-budget-pareto`

### 7. `506c02874` — 2026-09-07 · 1 row · **CLAIM**

> chore(register): the one manifest regeneration; two r2 rows corrected, one held

Fields moved: `_conditions_note` ×1, `conditions_compared` ×1

- [ ] Walkthrough prepared
- [ ] PI signed

- `sensitivity-mde-r2`

### 8. `6844fb182` — 2026-09-08 · 1 row · **CLAIM**

> fix(register): the estimated column's shift stated precisely (E84 correction)

Fields moved: `outcome` ×1

- [ ] Walkthrough prepared
- [ ] PI signed

- `estimated-correction-r2`

## What each walkthrough needs

Per the policy, not a summary — the material the PI needs in order to disagree:

1. **What the pass changed in these rows**, field by field, read from the diff
   at that commit rather than from its message.
1. **Whether the change altered a claim or only its bookkeeping.** A rewritten
   `outcome` or a changed `tie_set` is a new scientific claim; an added
   `_prereg_rationale` is not.
1. **The row's current claim**, verified against its artefact independently of
   whatever produced it.
1. **Scope limits** — anything the signature will not reach.

## Notes

- `era1-single-pass-baseline-matrix` and `tile-size-sweep` also moved at
  `f77d9078c` but are **not** in this queue. Both are `unsigned`, not `re-sign-
  pending`: the E88 work of 2026-09-14 amended them in place precisely because
  the project judged them never PI-signed. They need a first signature, not a re-
  signature.
- The 25 rows whose substance has NOT moved since their stamp are `legacy-
  signed` and are not queued. Their review happened; only its scope went
  unrecorded. They are promoted to `signed` opportunistically, when they next
  come up for review on their own merits — not as a back-filling exercise.

## Changelog

### 2026-09-16 — Original publication

Created by the signature migration. Groups the 23 `re-sign-pending` rows by the
8 commits that moved them, so the re-signing is 8 walkthroughs rather than 23.
No finding, number or outcome changed.
