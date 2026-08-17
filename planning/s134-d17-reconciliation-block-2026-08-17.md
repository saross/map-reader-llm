# Session 134 — D17 reconciliation block

> **Status**: IN PROGRESS 2026-08-17 — PI go given in-session
> 2026-08-17 AEST after a `/pre-run-review` dialogue (the S131
> protocol; S133 precedent). This document is the block's controlling
> document per the pre-run-review exit requirements. Budget:
> **US$0.00** — no API, no heavy compute (runs on amd-tower; nothing
> approaches the ~30 s sapphire bar).

## Scope

The gate before final Results prose (outline decision D17 = A +
schema amendment; `docs/paper/results-outline.md` § D17). Five items:

1. **Schema amendment** — replace the `preregistered` enum in
   `docs/manifest-schemas/analyses-manifest.schema.json` (currently
   `["preregistered", "exploratory", "preregistered-with-deviation",
   null]`, line 48) with `["confirmatory",
   "confirmatory-with-deviation", "registered-exploratory",
   "post-hoc", "not-executed", null]`. Field name unchanged. Retired
   values force the migration: regeneration fails validation until
   every row is re-sorted, so no half-migrated state can commit.
2. **Relabelling pass** — re-sort all 24 rows in
   `results/run-analyses.json` (the hand-authored specs; the
   generator copies human fields verbatim) into the new vocabulary,
   one-line rationale per row anchored to the preregistration /
   errata; regenerate via `generate_post_run_report.py --all
   --write`; drift-check 0 fail.
3. **H10 and H12-v2 analysis rows** — both ran to completion with
   scored conditions (`h10::greedy-pool-{020,040,080,160}`,
   `h10::verified-pool-160`; `h12-v2::{greedy,wbf}-r{1,2,3}`), both
   null per the D17 inventory, both invisible in the analyses
   register. Author their rows; manifest 24 → 26.
4. **Unexecuted-set erratum coverage** — the registered obligations
   never executed: H6 (Phase-4 transfer; E41 partial — characterises
   the substitute, no formal not-run disposition), H13 (no erratum),
   H14/H15 (no erratum; quoted-table hit only), H2 Condition C
   (**covered — E59**). Draft errata (E74+) for the gaps; PI wording
   review is the gate. Then add the five `not-executed` placeholder
   rows (manifest 26 → 31).
5. **Hypothesis-outcome table** — new generator script; the table is
   a pure projection of the manifest (zero hand-maintained cells),
   15/15 hypotheses. Lands in `results/`; the outline cross-references
   it. Tier-1 tests; registry refresh at block close.

## Rulings and hardenings recorded from the review dialogue

1. **Enum semantics (PI-approved)**: `confirmatory` /
   `confirmatory-with-deviation` name the epistemic role outright.
   No `registered-exploratory-with-deviation` — deviations do not
   change claim strength where no confirmatory claim exists; the
   `deviations` array records specifics. `null` stays legal
   (not-yet-adjudicated); finished state requires 0 nulls.
2. **Strictness rule (PI, 2026-08-17)**: honest/strict sorting —
   expectation is a *minority* of the 22 `exploratory` rows move to
   confirmatory-class (the confirmatory claims live chiefly in
   `family-bh-fdr-confirmatory` and `h1-cmt0106-pooled-modality`).
   Where doubt exists, err towards strictness — e.g. prefer
   `-with-deviation` over bare `confirmatory`, and exploratory-class
   over confirmatory-class.
3. **Register semantics (PI-approved)**: the analyses register widens
   from "analyses performed" to **"registered obligations and their
   dispositions"** — the manifest is the single source of truth for
   hypothesis disposition, including non-execution. Placeholder
   `not-executed` rows carry the disclosure erratum in `deviations`
   and a one-line disposition in `outcome`.
4. **The n1 exception**: `n1-baseline-matrix-384`'s argued label
   (`docs/methodology/n1-baseline-matrix.md:412-424` — the 18-cell
   board "was not itself in the preregistered analysis plan") is
   adjudicated individually, never in a bulk pass; expected mapping
   `post-hoc`, which preserves the argument's content exactly.
5. **Adjudication point flagged for the PI walk**: the two rows
   currently `preregistered` both carry non-empty `deviations`
   arrays (h1-cmt0106: 4 E-numbers; family-bh-fdr: 12) — whether
   they become `confirmatory-with-deviation` under the stricter
   vocabulary is a per-row PI ruling.
6. **Audit gate (PI, 2026-08-17)**: `/audit` on all new or modified
   code (the table generator; schema/generator touches); correct
   medium+ findings and immediately-worthwhile lows; **report
   uncorrected items explicitly**. Audits run on Opus subagents per
   the standing token-conservation policy.
7. **Adjudication gate (unexecuted set; PI, 2026-08-17)**: after
   Item 4 lands, a PI walk of the five `not-executed` rows decides
   run / formally drop per hypothesis. Any "run it" ruling spawns a
   **gated future item** (API spend → its own
   phase-gate/audit-config), never absorbed into this $0 block. The
   table generates beforehand; placeholders regenerate cheaply if a
   ruling changes one.
8. **Coherence ordering**: Items 2 and 3 both edit
   `run-analyses.json` and regenerate the manifest — serialised, one
   regeneration per commit, never concurrent. Item 4's new E-numbers
   back-reference into `deviations` arrays only after erratum
   numbering is settled.
9. **One-commit rule per artefact**: schema+tests one commit;
   relabel+regeneration one commit; new analysis rows with their
   regeneration; errata one commit; placeholders+regeneration;
   table script+output+registry one commit.
10. **Verification stack**: L0 — every label carries a rationale
    anchored to prereg/errata line numbers; outcomes cite condition
    metrics. L1 — tier-1 tests, `ruff`, `--self-test`. L2 — blind
    fresh-context verifier (Opus) on the highest synthesis-density
    item: cold, answer-shaped ("classify each of H1–H15 from the
    prereg + manifests + errata: executed or not; confirmatory /
    deviation / registered-exploratory / post-hoc; where reported"),
    diffed against the authored labels and table; denominator
    reported; disagreement rule = third derivation, never
    verifier-wins. L3 — drift-check; citation-site sweep for the
    retired `exploratory` value and stale analysis counts (e.g. "18
    analyses" at `results-outline.md:466`). L4 — PI gates: the
    classification walk, sign-off on the two new analyses, erratum
    wording, the unexecuted-set adjudication.

## Finished states (countable)

1. Schema validates; `--self-test` passes; tier-1 tests green.
2. 31/31 rows validate; **0 rows carry a retired value; 0 rows
   null**; drift-check 0 fail; the n1 argument survives verbatim in
   its row's rationale.
3. 2 new analysis rows registered and VALID with outcomes authored
   from the scored conditions.
4. 5/5 unexecuted obligations have named erratum coverage and
   placeholder rows.
5. Table covers 15/15 hypotheses, every cell traceable to
   manifest/errata fields; registry `--check` green.

Automation's finish is authored-and-committed; the PI gates sit
after.

## Stop states

- Any API spend ($0 budget) — hard stop.
- Generator validation failure or drift-check red — stop, fix,
  never write around it.
- A row whose classification is genuinely ambiguous — escalate to
  the PI, never guess.
- H10/H12-v2 outcome authoring surfaces a **non-null** result
  (expected band: both null per the D17 inventory) — verify the
  pipeline, then escalate (calibration rule).
- Bulk-pass touch of `n1-baseline-matrix-384` — tripwire.
- Erratum numbering collision, or any edit to lodged/immutable
  preregistration text — stop.
- Dependency-chain violation (Items 2/3 concurrent; Item 5 before
  its inputs) — stop.

## PI stop-condition playback (comprehension check, 2026-08-17)

Recorded verbatim in-session: API spend; unexpected results
(non-nulls where nulls expected); dependency-chain violation;
ambiguous results requiring investigation or PI input; tripwires
(critical files, numbering collisions). Matches the plan — check
passed.

## Changelog

### 2026-08-17 — Original publication

Block plan authored from the S134 pre-run-review dialogue; PI go
recorded 2026-08-17 AEST. Items not yet executed at time of writing.
