# Reference-standardisation queue — analyses waiting on a fixed reference

> **Last revised**: 2026-08-14 (gate OPEN — standardised reference
> materialised; execution contract added from the pre-run review). See
> [§ Changelog](#changelog) for revision history.

**What this is.** Ruling 21 fixes the ground-truth reference *first*, then
runs every reference-tainted analysis once against it. This file is the
register of what is waiting. Nothing here may be re-run before the
standardised reference lands — that is the ruling, and the reason is that
four separate reference defects surfaced in four days (W7-D8, W7-D9,
rulings 19 and 20), each of which would have triggered its own recompute
had it been handled alone.

**Interim rule (ruling 21f).** Items here are **caveated in place** in
their host documents, never re-run. A caveat is not a recompute.

**What "tainted" means here.** An analysis is tainted if its result depends
on *which* ground-truth layer or *which* extended-GT gating it consumed.
An analysis that merely mentions a GT count is not tainted; it is a
documentation item and belongs with the W7-E4 sweep instead.

## The gate

The queue opens when the point-marking pass lands. Per ruling 21(c) that
pass is the **773 promoted phantoms only** — click-the-centre, mound type
and map and label inheriting, ≈ 1 hour of review plus the UI build. The
4,746 student mounds are **not** re-marked; that option (≈ 6 hours, ≈ 7
for both layers) was priced and declined.

Two consequences to carry forward:

1. The resulting reference is **mixed-provenance by design** — marked
   centres for the phantom layer, as-digitised positions for the student
   layer. Document it as a property, not an oversight.
2. It is a **best-possible reference, not a gold standard**. Joint student
   + model false negatives — mounds both the students and every model
   missed — are not economically recoverable. This limitation ships in the
   artefact's own header (ruling 21b).

**Out of scope**: the 4-map gold-standard corpus. Four careful review
passes, every point re-positioned to dead centre within 1–2 px, one
additional false negative found at the fourth pass and nothing since
(ruling 21d). It needs no review.

## Resolved BY the point-marking pass

These do not wait for the reference — the marking pass *is* their fix.

| Item | What it is | Source |
|------|-----------|--------|
| Obs 371 | Phantom match distances recorded as 25 m rings anchored at 50 m rather than marked centres. Below R = 50 m the extended GT collapses to the reviewed student GT, so sub-50 m Track-2 figures penalise correct detections of student-missed mounds. | Committed future work, `planning/paper-writeup-continuity.md` |
| 4–6 borderline conflations | Promoted-phantom pairs sitting between 7.3 m and 15 m from a student point — closer than the pipeline's ≳15–20 m "genuinely distinct mounds" floor, further than the 5 m de-duplication catches. Cannot be settled from coordinates; must be seen on a map. | Ruling 20(c) |
| `canonical-review.csv` row sort | Rows re-sorted on the exact-position result once centres are marked. | Ruling 20(d) step 3 |

## Execution contract (pre-run review with the PI, 2026-08-14)

The gate is OPEN: the standardised reference landed at `ecc00f31f`
(`results/deployment-oracle-2026-06-06/canonical-gt/standardised/`).
Items 1–5 run under the following contract, agreed in the pre-run
review (`/pre-run-review` protocol; see Obs 397):

1. **Dependency order**: items 1 and {2→3} may run in parallel; 4 only
   after 3; 5 only after 1–4. The 2→3 edge is an artefact-coherence
   ordering, not a data dependency — the t0.3 cell is scored ONCE and
   registered under both items, never computed twice.
2. **Countable completion gates**: a dependent item starts only when
   the upstream item's finished state is exact (e.g. item 3 = "8/8
   board cells carry F1 and MCC against the standardised reference,
   drift-check clean"). No mixed-vintage artefacts: item 5 never
   re-tiers a board whose cells straddle references.
3. **One-commit-per-document rule**: a refreshed document's numbers
   and its changelog entry land in a single commit; no document ever
   straddles two references across a commit boundary.
4. **Stop states** (halt and escalate, never absorb): any API spend;
   gate battery or census test red; a surprising result (tier flip,
   headline moving beyond the Obs 396 bias band, direction reversal);
   missing inputs (no near-enough substitution); sequencing
   violations; sapphire unavailable (check, never silently fall back).
5. **Verification stack**: JSON-first outputs with anchored prose;
   tests + `/audit` on new code; a blind fresh-context verifier pass
   over each prose-bearing refresh (non-negotiable for item 4, the
   highest synthesis-density item; brief it on directionality and
   comparison tables), calibrated to the measured ~8% claim-mismatch
   rate (C4: 619 of 7,894 decisively recomputed values); drift checks
   and citation-site sweeps; PI sign-off gates last.

## Queue — no API spend, runs automatically once the reference lands

| # | Analysis | Why it is tainted | Register |
|---|----------|-------------------|----------|
| 1 | The four 55-map Dawid–Skene fits (`scripts/analyse_dawid_skene.py`) | The fits do not share a reference. `item-posteriors.csv` student rows: **4,770** for T=0.7, T=0.3 and text-MIN (the script default, `analyse_dawid_skene.py:57`); **4,745** for image. Every cross-run comparison in `results/55maps-ds-summary-v2/report.md` §§ 2.1, 2.2, 4.1, 4.2 mixes the two. | W7-D9 |
| 2 | `outputs/55maps-text-high-t0.3-generalisation/evaluation/` | Evaluated against the unreviewed 4,770 base while sibling runs used the reviewed layer. t0.3 also lacks a full-buffer-eval, unlike the other three, and leads on F1 in several documents. | W7-D8, ruling 19(c) |
| 3 | F1 / MCC reference unification | Corrected-F1 scores against the extended reference (student 4,746 + phantoms gated per buffer); tile-level MCC scores against the student layer alone. The two metrics must share a reference. | Ruling 20(a) |
| 4 | Obs 280 — the F1-versus-MCC rank divergence (text wins F1, image wins MCC) | Currently measured across metrics that do not share a ground truth, so an unknown share of the divergence could be reference effect rather than metric behaviour. Re-measure after item 3. | Ruling 20(a) |
| 5 | Re-tier both boards; re-verify every 55-map figure in `docs/paper/results-draft.md` | Downstream of items 1–4. The committed-future-work estimate is 8 cells × 14 buffers of re-scoring. | Ruling 20(d) step 4 |

## Queue — requires API spend, discussed case by case before launch

Nothing currently. Any item that migrates here goes through the standing
API review gate — model, batch versus real-time, call count, estimated
cost — before anything is launched (ruling 21e).

## Not in this queue

- **Stale GT *counts* in prose** — a documentation defect, not a tainted
  analysis. Handled by the W7-E4 sweep under the
  `gt_count_era_resolution` rule in
  `reports/verification/c4-triage/coverage-drift-2026-08-04.json`.
- **Historical corrected states (4,744 / 4,745)** — record-only under
  ruling 19(a). A dated document describing what a 2026-05-03 evaluation
  consumed is history and stays.

## Changelog

### 2026-08-14 — Gate opened; execution contract added

Ruling-21 application completed: marking campaign closed (S130), the
instruction set derived and PI-ratified (S131), the six-claim walk
landed (`b2692f188`), and the standardised reference materialised
(`ecc00f31f`). Added the § Execution contract from the pre-run review
dialogue with the PI — dependency DAG, countable completion gates,
the one-commit-per-document rule, stop states, and the layered
verification stack. Queue items 1–5 are unchanged and now runnable.

### 2026-08-04 — Original publication

Created under ruling 21 (Session 128), which generalises ruling 20(b)'s
"do not recompute yet" from the F1/MCC pair to the whole class of
reference-tainted analyses. Seeded with the five no-API items and the
three point-marking-resolved items known at creation. The immediate
trigger was W7-D9 — the discovery that the four Dawid–Skene fits do not
share a reference — which was the fourth reference defect in four days
and made case-by-case repair visibly the wrong strategy.

Landed at commit `TBD` (recorded in the next revision of this file).
