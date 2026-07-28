# Adversarial review brief — the Session 118 audit

> **Purpose**: Shawn wants a second opinion from a different model on what this
> audit found, whether the patterns we drew from it are real, and whether the
> fixes and the planned approach are sound. This is written to be **argued
> with**, not absorbed. Everything below carries its evidence so you can check
> it; where I am uncertain or where the reasoning is contestable, I say so.
>
> **Author**: Claude Opus 5, 2026-07-27/28. Prepared for review by a fresh
> instance (Fable).

## 0. How to use this document

Do not take my conclusions on trust — that is the entire lesson of the session.
Three specific reasons to be sceptical of me in particular:

1. **I got a load-bearing call wrong mid-session** and had to reverse it (§ 4.1).
2. **I made two operational errors** with real destructive potential (§ 6).
3. **I have an interest in the fixes being adequate**, having written them.

The strongest thing you can do is pick two or three claims below, go to the
cited artefacts, and try to break them. Claims are anchored by file and line.

## 1. What the audit found — claims and their evidence

Each row is checkable. `osf:NNN` means
`docs/methodology/preregistration/osf/preregistration.md` at that line.

| # | claim | primary evidence | how to falsify |
|---|---|---|---|
| C1 | An erratum contradicts the registration it describes | E37 says "the preregistration did not include a two-stage Proposer-Verifier pipeline"; `osf:457` registers "Coarse-to-fine (proposer-verifier)"; the verifier's own prompt is at `preregistration-appendix-prompts.md` § 1.6.2, "Used by: H2 (Stage 2)" | show the OSF-posted registration differs from the repo copy |
| C2 | The inference method used throughout is not the registered one | `grep -c -i permutation` on `osf` = **0**; registered method is bootstrap + BH-FDR (`osf:270`); every leaderboard uses tile-swap permutation; E45 calls permutation "preregistered (Section 3.5)" | find permutation registered under another name |
| C3 | 22 FALSE + 12 UNLICENSED attributions to the registration | `reports/d17-inventory/prereg-attribution-sweep.md`; 1,060 candidates across 126 files | show individual verdicts are wrong |
| C4 | 46 registered items never executed or only partly | `reports/d17-inventory/unexecuted-register.md` | show an item was in fact discharged |
| C5 | 43 conditionals; 16 point-estimate-only; only ONE names its uncertainty treatment | `reports/d17-inventory/` trigger census | find a conditional we missed, either way |
| C6 | The data layer is sound | `pro-high-text-provenance.md`: all 1,187 metas parsed, 12 cross-family disagreements, all in pools E57 already affirms, zero new mis-dispatches | find a mis-dispatch outside that class |
| C7 | 40 % of indexed `user` transcript chunks are not the user's words | `transcript-labelling-errors.md`; n=1,000 sampled; mechanism at `index-session-content.py:105` | re-sample and get a different rate |

**The one link not closed**: the OSF-posted artefact at `osf.io/tybgq` has never
been fetched. The repo-side chain is airtight (byte-identical from a commit
11h20m before the registration timestamp), but C1 rests on the repo copy being
what was posted. If you can fetch it, do.

## 2. The patterns we drew — the contestable part

Findings are facts; patterns are interpretations. These are the interpretations,
stated so they can be attacked.

**P1 — The problem is in the interpretive layer, not the data.** Evidence: the
provenance trial came back clean (C6), and the manifests/raw outputs survived
every check, while documentation produced 22 false attributions. *Weakest point*:
we ran **one** data-layer probe. One clean probe is weak evidence of a clean
layer. I said so at the time but the conclusion has been carried forward as
though it were settled.

**P2 — ~80 % of the attribution errors reduce to four substitutions.** Decision 10
cited as prereg § 3.5; study YAMLs cited as registered decision rules;
`analysis-summary.md` cited as the registration; a false memory that permutation
was registered. *Contest this by*: sampling the 22 FALSE findings and checking
whether they really collapse that way, or whether the reduction is an artefact of
how the sweeping agent grouped them.

**P3 — The structural driver is directory layout.** Working documents sit inside
`docs/methodology/preregistration/`, one level above the lodged `osf/`. *Contest
this by*: asking whether relocating files would actually change behaviour, or
whether that is a just-so story about a human error with a simpler cause.

**P4 — A preregistered trigger must name four things** (statistic, comparison
scope, uncertainty criterion, evaluation moment), because sixteen of our
conditionals name only the first. This is the finding most likely to be
*publishable* and therefore the one most deserving scepticism.

**P5 — The manifest system models artefacts, not commitments**, and all three
failure classes trace to that. *This is my framing, not a finding.* It is
tidy, which is exactly why it should be doubted.

## 3. The fixes — what we built and what it does not do

Implemented (commits `f607adf20`, `0a85abb14`, `b92d0c6f2`):

- **Write-once predictions.** `predicted_outcome` immutable once set; amendment
  requires `predicted_outcome_amended` whose `previous` must equal the on-disk
  value, so an amendment is spent when used.
- **`status: planned`.** Runs declare intent before execution; excluded from
  generated manifests; staleness-flagged after 30 days; a planned entry whose
  directory exists is rejected at load.

**What it explicitly does NOT do, and I want this challenged:**

- It **cannot retro-validate the 18 existing predictions**, all authored
  post-hoc under the old regime. The audit found one (H7) recorded as confirming
  a prediction the registration never made.
- **C3 remains open**: delete-then-re-add launders a rewrite across two builds.
  Mitigated by a warning, not closed. Decision recorded at
  `planning/audit-and-completion-plan.md` § 6.6. Until the append-only ledger
  exists, the honest claim is "**detectable**", not "structurally impossible".
- Is this machinery worth its cost at all, given the paper's exposure is the
  *existing* record? Shawn had to redirect me back to the paper. **A defensible
  answer is "you over-built"** — I would like that tested.

## 4. Where I was wrong, so you can check the corrections

### 4.1 I accepted an erratum over the registration it describes

I read E37 myself, treated it as authoritative, and told Shawn a confirmatory
framing for the headline was unavailable. He said he remembered considering PV.
He was right; E37 is wrong. **Check the reversal is itself right** — that PV
really is registered, and that my enumeration of the five things exceeding the
spec (consensus proposer pool; binary verdict vs registered raw probabilities;
adversarial framing; crop geometry; verifier consensus size) is neither
over- nor under-stated.

### 4.2 I claimed `userType: external` identified genuine human turns

It does not — assistant records carry it too. I used it to "verify" a quote from
Shawn and to scope a negative search. **Both conclusions survived re-testing
content-first**, but the method was wrong. Worth re-checking the fine-to-coarse
negative (`2026-03-07T05-59_c634c7c3`) independently.

### 4.3 I shipped a critical bug in the guard

The escape hatch did not exist end to end; it passed 31/31 of my own tests.
Found by fresh-context audit, not by me. **The fix has itself been audited
twice**, but the person who wrote both the bug and the fix is the same one
telling you the fix is good.

## 5. The planned approach — the part most worth your opinion

Recorded at `planning/audit-and-completion-plan.md`. Adopted: the two-lens audit
(`/audit`, personal-assistant `491a225`) and the pipeline-fixture rule. Declined
for now: coverage, mutation testing, property-based testing (§ 6.4a).

**The open question I most want challenged**: is the audit converging or not?
Every probe returned roughly what it was pointed at — 6 triggers became 43; 5
unexecuted hypotheses became 46 items; an item four passes missed was found by a
fifth. I have no basis for estimating what an unrun probe would return. Paper-B's
advice was "do not sample at this error density", which we followed for the
errata but not elsewhere.

**Specific questions:**

1. Is P1 (clean data layer) safe on one probe? What would a second probe be?
2. Does P2's four-substitution reduction survive spot-checking?
3. Is the machinery proportionate, or should the effort have gone to the record?
4. What probe have we not run? This is the highest-value thing you could name.
5. Is "detectable, not impossible" the right claim about the guard, or should the
   paper avoid claiming anything about the machinery at all?

## 6. Operational errors worth knowing about

I authorised an audit agent to apply mutations and restore via `git checkout` on
an **uncommitted** file. It did, destroying work recoverable from no commit; it
reconstructed by hand and verified by blob hash. Nothing was lost, by luck. Within
the hour I ran a mutation check myself on the same uncommitted file. Both are now
closed by a rule in `/audit`: commit before delegating; restore by re-applying the
inverse edit, never by checkout. **Both errors were mine, after I had documented
the hazard.**

## 7. State

Everything committed and pushed; both repos clean. Tier-1 1,178 passed. Manifests
ALL VALID. Nothing half-finished. Full reading order at
`reports/d17-inventory/step0-summary.md`; resumption status at
`planning/audit-and-completion-plan.md` § 7a.

**Untouched, and this is the paper's actual exposure**: none of the 22 FALSE or
12 UNLICENSED attributions is corrected.
