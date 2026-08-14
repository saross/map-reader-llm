# Reference-standardisation queue — analyses waiting on a fixed reference

> **Last revised**: 2026-08-14 (item 4 complete, blind-verified; items
> 1–4 of 5 now done — only the item-5 re-tiering remains). See
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
5. **Verification stack**: JSON-first outputs with anchored prose —
   the anchor discipline is the foundation layer and is protected
   under time pressure, since without it the verifier has nothing to
   re-derive against; tests + `/audit` on new code; a blind
   fresh-context verifier pass over each prose-bearing refresh
   (non-negotiable for item 4, the highest synthesis-density item),
   calibrated to the measured ~8% claim-mismatch rate (C4: 619 of
   7,894 decisively recomputed values); drift checks and
   citation-site sweeps; PI sign-off gates last. Three verifier
   conditions (added from the 2026-08-14 Opus review):
   (a) **denominator reporting** — the verifier states claims
   identified / re-derived and artefacts opened; an empty corrections
   table without a denominator is treated as a non-run, not a pass;
   (b) **corrections are claims, not verdicts** — a correction that
   conflicts with the draft triggers a third re-derivation from the
   data (PI adjudicates if still split); the verifier never wins by
   default; (c) **answer-shaped claims are asked cold** —
   directionality and winner claims are derived by the verifier as
   questions from the metric files and diffed against the prose;
   comparison tables are rebuilt independently, never checked
   arithmetically.

## Queue — no API spend, runs automatically once the reference lands

| # | Analysis | Why it is tainted | Register |
|---|----------|-------------------|----------|
| 1 | ✅ **DONE 2026-08-14** — The four 55-map Dawid–Skene fits (`scripts/analyse_dawid_skene.py`) | Was: the fits did not share a reference (4,770 ×3 / 4,745). Re-fit on the standardised reference with current canonical inputs (fits `b140f686a`, crosstabs `b31093e9f`, report refresh `13b386875` + blind-verified corrections `2d8a3dc83`). All four fits at 4,731 exactly; the W7-D9 withdrawal resolved; T=0.3 leads. One residue registered: the superseded T=0.3 fit's input provenance is unidentified (report § 6.3). | W7-D9 |
| 2 | ✅ **DONE 2026-08-14** — `outputs/55maps-text-high-t0.3-generalisation/evaluation/` | Was: evaluated against the unreviewed 4,770 base; no full-buffer eval. The t0.3 cells were scored ONCE against the standardised reference (14 buffers, F1 + MCC) and registered under this item and item 3: conditions `verified-k4/k3-standardised-gt` under `55maps-text-high-t0-3-generalisation` (commit `fab017085`); scoring `6f7e7b651`, summary + blind-verifier corrections `cb3629e7f`/`0f19370cd`. The tainted run-level eval dirs remain as dated history. | W7-D8, ruling 19(c) |
| 3 | ✅ **DONE 2026-08-14** — F1 / MCC reference unification | Was: corrected-F1 on the extended reference, MCC on the student layer alone. Completion gate met: 8/8 board cells carry F1 AND tile MCC against the standardised reference (drift check 0 fail; extension census 279/0-drops at every buffer). A0 gate reproduced every committed legacy value at delta 0.0 exactly; A1−A0 = the W6-E9 fix (+8.7e-05 uniform); full A0/A1/B/C decomposition in `results/55maps-standardised-ref-2026-08-14/`. MCC is buffer-invariant by construction under the shared reference. | Ruling 20(a) |
| 4 | ✅ **DONE 2026-08-14** — Obs 280 — the F1-versus-MCC rank divergence | Re-measured with both metrics on the standardised reference: the divergence SURVIVES (text T03-k4 leads F1 0.8303; image IM-k3 leads MCC 0.7120 from third place on F1) and is ≈90 % metric behaviour — the reference axis moves the MCC gap only +0.004 of ~0.043, in the widening direction, so the mixed-reference original had understated it. The Obs 292 R≥75 m F1 crossover was a per-run-vintage artefact and does not carry. Analysis `obs280-shared-reference` (22 analyses, ALL VALID); doc + JSON in `results/55maps-standardised-ref-2026-08-14/` (`bfaeb1c17`, verifier corrections `ddc559c78` — incl. a substantive mechanism correction: on this board text wins F1 on precision and image wins MCC on tile sensitivity, NOT Obs 280's high-TN framing). Blind verifier: 89/83/80/3. | Ruling 20(a) |
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

### 2026-08-14 (e) — Item 4 complete, blind-verified

The Obs 280 re-measurement landed the same session, immediately
after items 2–3 (the DAG's 3→4 edge). Verdict: the F1-vs-MCC
divergence survives reference unification and is ≈90 % metric
behaviour — the reference asymmetry ruling 20(a) worried about
accounts for only +0.004 of the ~0.043 MCC gap, and in the
WIDENING direction (the original understated image's lead). Image
leads MCC from third place on F1; both headline gaps carry
non-overlapping marginal CIs. The Obs 292 R≥75 m F1 crossover was
traced to the per-run self-referential reference vintage and does
not carry to any shared reference. The mandatory blind verifier
(89/83/80/3) caught one substantive error the draft had imported
from Obs 280's matrix-tree phrasing: on this board the mechanism is
text-precision vs image-tile-sensitivity, NOT high-TN selectivity —
corrected and third-re-derived. Item 5 (re-tier both boards,
re-verify every 55-map figure in results-draft.md) is now the only
open item; the narrowed T03-k3-vs-TH7-k3 margin (+0.0006) is its
central question.

### 2026-08-14 (d) — Items 2–3 complete, blind-verified

The {2→3} leg landed under the full contract in Session 132. The
t0.3 cell was scored ONCE and registered under both items. New
engine mode (`--extension-csv`, commit `c951aa749` hardened through
`6e38c0e5f` by a dual-lens audit + re-audit): the standardised
extension layer's marked centres dissolve the Obs 371 ring gate, so
all 279 records enter the extended GT at every buffer and tile MCC
is buffer-invariant on the shared reference. Leg A0 reproduced all
eight committed legacy values at delta 0.0 exactly (de-duplication
disabled = the committed configuration); the audit caught that the
committed anchors pre-date the W6-E9 fix, and A1 isolates that fix
(+8.7e-05 uniform, exactly one twin drop per cell). Publication
scoring (leg C, sapphire, $0): rank order preserved 8/8; T03-k3
still leads but its margin over TH7-k3 narrows +0.0051 → +0.0006;
all movements inside the Obs 396 band — no stop state. Registered
as 8 `-standardised-gt` conditions (322→330, ALL VALID, drift 0
fail). Blind verifier over the summary: 249 identified / 242
re-derived / 234 confirmed / 8 corrections, none numerical, applied
(`0f19370cd`); the 50 m-shell recomposition (146 removed / 11
added) was third-re-derived per the disagreement rule. Item 4 (Obs
280 re-measurement — F1-vs-MCC divergence pattern survives at point
estimates: image tops MCC 0.712 while text tops F1) and item 5
(re-tiering; the narrowed oracle margin is its central question)
are now unblocked.

### 2026-08-14 (c) — Item 1 complete, blind-verified

The four Dawid–Skene refits landed under the full contract: B/C
vintage decomposition, all reproduction gates, crosstab re-runs, the
report refresh in one commit, and a blind verifier pass (488 claims
identified / 481 re-derived / 476 confirmed / 5 corrections applied —
1 material: the § 2.3 reclassification mechanism; all three B fits
independently re-derived CONFIRMED). Headline: T=0.3 takes the D-S
and measured F1 lead on the common reference; the Obs 293
cross-method disagreement narrows to the middle pair. The verifier's
methodological gap is closed in code: `analyse_dawid_skene.py` now
records `input_paths` in its own artefact. Registered residue: the
superseded T=0.3 fit's inputs remain unidentified (two hypotheses
exactly falsified; report § 6.3).

### 2026-08-14 (b) — Verifier conditions hardened from the Opus review

Three additions to contract item 5, from an external Opus review the
PI relayed: verifier denominator reporting (a clean pass and a lazy
pass are otherwise indistinguishable), the named disagreement rule
(verifier corrections are claims, not verdicts — third re-derivation
on conflict, PI adjudicates if split), and cold derivation for
answer-shaped claims (directionality/winner questions asked, not
handed over). Layer 0's anchor discipline named as the foundation to
protect under time pressure. Same refinements versioned into the
`/pre-run-review` skill.

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
