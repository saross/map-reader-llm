# Ruling-21 application — the instruction set for the standardised reference

> **Status: DRAFT — awaiting PI sign-off.** No layer has been mutated.
> This document and its computed artefacts
> (`ruling21-instructions.csv`, `ruling21-summary.json`) are the
> derivation; materialising the standardised reference is the next,
> gated step. See [§ Changelog](#changelog).

**What this is.** Ruling 21 (`reports/verification/phase3-rulings-2026-07-31.md`
§ 21) requires the ground-truth reference to be standardised once, from a
fixed artefact, before any reference-tainted re-analysis runs. The fixed
artefact is the point-marking campaign's output — `marked-centres.csv`,
1,317 adjudications (762 `c` / 509 `d` / 45 `x` / 1 `m`), campaign closed
with all eight gates green at commit `1b9c308aa`. This spec turns those
adjudications, plus the Session-130 decision rules, into a per-record
instruction set, computed by `scripts/derive_ruling21_instructions.py`
and persisted as
`results/deployment-oracle-2026-06-06/canonical-gt/ruling21-instructions.csv`
(1,432 instructions; any student feature not named is implicitly "keep as
digitised, grade `out_of_scope`").

## Inputs

| Layer | File | Count |
|-------|------|-------|
| Marks | `canonical-gt/marked-centres.csv` | 1,317 |
| Student GT | `inputs/vectors/references/student-mounds-55maps-reviewed.geojson` | 4,746 |
| Phantom extension | `canonical-gt/canonical-review.csv` | 773 |
| Pre-merge originals | `canonical-gt/superseded-marking-queue.csv` | 52 |
| Marking-pass extras | `canonical-gt/extra-review-items.csv` | 1 |

## Decision rules (Session-130 adjudications)

1. **Mound identity comes from mark position clusters, never from claim
   chains** (app spec § How to count: "distinct mounds = number of
   position clusters among marks carrying a centre"). Marks within the
   5 m de-duplication tolerance are one mound (single linkage; the
   largest observed within-cluster spread is 5.1 m via a chain). A
   conflation claim is a record-level statement: it attaches an
   **unmarked** record (an out-of-queue student, a restored pre-merge
   original) to the claimant's mound; a claim onto a **marked** record
   in another cluster is superseded by that record's own mark (§ Open
   decisions, item 1). A claim onto a marked record within the 15 m
   distinct-mound floor corroborates one mound (one case:
   `student:861` ↔ `phantom:329`, marks 5.03 m apart, mutual claims).
2. **One survivor per mound**, by provenance: genuine student record
   (including restored pre-merge originals) > phantom > marking-pass
   extra. Among students, the claimed partner beats the claimant
   ("the claimant is the duplicate"). Residual ties — the 24 mutual
   phantom pairs — fall to lowest layer index, deterministically,
   and are listed in the summary JSON.
3. **The survivor takes the marked centre**: its own mark where it was
   reviewed; the claimant's mark where it was claimed from outside the
   queue. This is the attractor-displacement correction — a claimed
   partner can move up to ~100 m from its digitised position.
4. **The contradicted merge** `corrected_student:4172` (`m`) is
   removed; both pre-merge originals (superseded points #46 and #47,
   24.6 m either side of the centroid) are restored.
   `promoted_phantom:389`'s red-partner claim resolves to #46 exactly,
   so #46 takes 389's mark (`proxy_confirmed`); #47 is restored
   as recorded.
5. **W7-R2**: student features #4744 and #4745 are curator additions
   of MODEL detections, not student digitisation. Both were verdicted
   `c`; both leave the student layer, keeping its provenance purely
   student. Their mounds survive — #4744's through genuine student
   record #2724 (which claimed it), #4745's through its phantom
   partner (`phantom:72`) in the extension layer.
6. **Removals**: the 45 `x` records are false positives — 41 phantoms
   and 4 student records (#2508, #2536, #2601, #4559) — and are
   removed outright. An `x` record never bridges two clusters.
7. **Confidence grades** (student layer): `directly_reviewed` — in
   queue, own mark (526 survivors); `proxy_confirmed` — out of queue,
   claimed as a partner from a reviewed mark, position inherited
   (113); `out_of_scope` — untouched, as digitised (4,090).

## The census

| Action | Count |
|--------|-------|
| `keep_student` (526 own-mark + 113 claimant-mark) | 639 |
| `remove_duplicate` (454 phantoms + 12 students) | 466 |
| `keep_phantom_extension` | 278 |
| `remove_fp` (41 phantoms + 4 students) | 45 |
| `restore_premerge` | 2 |
| `remove_contradicted_merge` | 1 |
| `add_marking_pass_extra` | 1 |

**Student layer**: 4,746 − 17 (4 FP + 1 merge centroid + 12 duplicates)
+ 2 restored = **4,731**. The 12 duplicate removals are the 9 jitter-
sample attractor duplicates, `#1442`, and the two W7-R2 records.

**Extension layer**: **278 phantom survivors** (of 773: 41 FP, 454
redundant with a student record or a co-located phantom) **+ 1
marking-pass extra** (`nested-benchmark-3207`, the burial mound under
the benchmark at student #3207, whose own record is the settlement
mound 15.5 m north).

**Positional quality**: marked centres carry the app's ~±2.5 m
precision floor. The jitter sample measures the out-of-scope grade's
as-digitised noise: median 8.6 m, mean 9.7 m, p90 18.3 m, max 30.0 m
displacement from the true centre.

## Deltas from the Session-130 beacon

- **Student→student claims: 13, not "9–10"** (the beacon's mid-campaign
  estimate): 9 jitter samples, 2 `student_pair`, 1 `student_conflation`,
  1 chain into #4744. Three of the 13 claimants survive anyway (two via
  superseded cross-cluster claims, one — #2724 — as its cluster's best
  record).
- **Proxy-confirmed population: 113, not 108.** The 108 counted
  coordinate-bearing claims only; 5 more out-of-queue students are
  claimed by pre-fix (coordinate-less) marks, resolved uniquely by the
  recorded partner distance (±0.5 m). With restored #46 the grade
  covers 114 records.
- **The proxy tally reads 114 claims / 83 within 15 m** where the S130
  hand count said 113 / 82 — a one-claim boundary difference; the
  108-point population agrees exactly.

## Findings to flag (Research Finding Calibration)

1. **~9% long-range duplicate rate in the unreviewed student layer.**
   The jitter sample was random, seeded, and drawn conflation-free at
   the queue's 50 m cut — yet 9 of 100 records were adjudicated
   attractor-displaced duplicates of other student records at 72–100 m.
   Extrapolated to the 4,095 out-of-scope records: roughly 370
   (Wilson 95% CI ≈ 4.8–16.2% → ≈ 200–660) undetected long-range
   duplicates remain in the reference. The detection floor matters
   too: partners were only offered within the 110 m flag radius, so
   the true rate is a lower bound. This belongs in the reference
   header and in Methods as a stated limitation — it materially
   supports ruling 21(b)'s "best possible, NOT a gold standard".
2. **Six superseded cross-cluster claims** (57.8–169.9 m): each is an
   attractor case where a record's claim points at a mound whose own
   mark settled elsewhere. All six sit in structures the S130
   re-review walks resolved; under rule 1 the marks win and both
   mounds survive.

## Open decisions for the PI

1. **The six cross-cluster claims are superseded by marks** — confirm,
   or re-review the six on the map:
   `624→ph:320` (63.7 m), `2087→ph:523` (73.9 m), `2474→ph:430`
   (114.1 m), `4197→4198` (57.8 m), `4547→4548` (85.4 m),
   `4635→ph:699` (169.9 m). *Recommend: confirm — the counting rule
   makes marks authoritative, and each was individually walked in
   S130.*
2. **24 mutual phantom pairs resolved by lowest index** — arbitrary
   but deterministic; the pair's marks are co-located, so only the
   surviving `candidate_id` differs. *Recommend: accept.*
3. **Four multi-claimant proxies** (students #1266, #2667, #3165,
   #3502 claimed by 2–3 co-located marks; lowest-indexed claimant's
   mark used, spreads ≤ 3.9 m). *Recommend: accept.*
4. **The legacy-resolved five join the proxy grade** (113 rather than
   the beacon's 108). *Recommend: yes — the claims are explicit, only
   their coordinates were lost to the pre-fix app.*
5. **The marking-pass extra enters the extension layer**, not the
   student layer — consistent with W7-R2's provenance cleaning (the
   student layer holds only student digitisation). *Recommend: yes.*
6. **Settlement-mound records stay, carrying their symbol type**:
   4 reclassified burial→settlement plus #3207's settlement call.
   Evaluation can filter on `symbol_type`; silent removal would lose
   the adjudication. *Recommend: keep with symbol type.*
7. **Restored #47's grade is `directly_reviewed`** (the `m` verdict
   adjudicated the site) though its position is as-recorded pre-merge
   digitisation. *Recommend: accept, with the position caveat in the
   artefact header.*

## Materialisation plan (after sign-off)

1. Apply `ruling21-instructions.csv` to emit the standardised
   reference as NEW artefacts (never mutating the campaign layers):
   a standardised student layer (4,731), a standardised extension
   layer (279), and a per-record provenance table carrying confidence
   grade, position source, and symbol type.
2. The artefact header states, per ruling 21(b): best-possible
   reference, NOT a gold standard; joint student+model false negatives
   unrecovered; mixed provenance (marked centres vs as-digitised, with
   the jitter noise figures); the ~9% residual long-range duplicate
   rate in the out-of-scope grade.
3. Re-run `scripts/marking_campaign_gates.py` (must stay 8/8 green —
   the campaign layers are untouched) and the derivation's tier-2
   census test.
4. Then the reference-standardisation queue items 1–5
   (`reports/verification/reference-standardisation-queue.md`): the
   four Dawid–Skene fits, the t0.3 evaluation, F1/MCC unification,
   Obs 280 re-measurement, re-tier both boards and re-verify every
   55-map figure in `results-draft.md`. All $0, no API.

## Changelog

### 2026-08-10 — Original publication

Derived in Session 131 from the closed marking campaign (`1b9c308aa`).
Derivation script, instruction set, and census committed together with
this spec. One algorithmic correction during derivation is recorded in
the session log: an initial draft clustered on claim chains and glued
two-mound attractor structures into one (worst case 169.9 m); the
committed algorithm clusters on mark co-location per the app spec's
counting rule, with claims acting only as attachments.
