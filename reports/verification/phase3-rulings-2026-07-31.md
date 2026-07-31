# Phase 3 in-flight PI rulings — 2026-07-31 (Session 122)

Four rulings collected interactively mid-phase (structured options per
the S121 calibration rule); recorded here so triage and the fleet can
proceed without re-litigating them at GATE 3. Controller:
`planning/audit-charter.md` § 7 Phase 3.

## 1. Dated-snapshot correction policy (load-bearing for triage)

**Ruling: snapshot + banner.** Session-dated report documents
(`reports/results-summary-session-58.md`,
`reports/session-111-discoveries.md`, and kin) are historical records:
the C4 sweep never edits their bodies. Ledger rows record divergence
from era-current artefacts; where divergence is material to a
load-bearing figure, a dated "superseded figures" banner is added
pointing forward. Documents that present themselves as current
(findings docs, leaderboards, methodology, tracking docs) remain
living documents corrected in place under the Document Revision
Policy. Rationale: session-dated docs are also C6 attestation sources —
in-place correction would falsify the record of what the session
actually found.

## 2. Clobber guards

**Ruling: fix this session.** Apply the Session-75 guardrail-6
convention to the two scripts that still write paths now holding
hand-authored content:

- `scripts/analyse_dawid_skene_v2.py:1391` → divert to
  `report_autogen.md` (the hand-levelled `report.md` in
  `dawid-skene-v2-data-driven-prior/` is the paper-citation source).
- `scripts/run_experiment_e.py:545` → divert to
  `results/phase3d-experiment-e-results_autogen.md` (the committed
  `phase3d-experiment-e-results.md` is a hand-authored replacement).

## 3. MCC bootstrap-means finding

**Ruling: record as a working-notes Obs.** The `evaluation.md` tables'
MCC/Sens/Spec columns are bootstrap means
(`scripts/evaluate_detections.py:834,837`), not point estimates; 439
of 1,635 files differ from the JSON point value in the third decimal.
Any document quoting MCC from an `evaluation.md` table quotes a mean.
Obs appended via the obs-writer agent (same session).

> **Correction (2026-07-31, same session)** — the Obs 376 writer's
> independent re-derivation corrected three specifics above (details:
> Obs 376; `c4-regen/regen-results.jsonl` row regen-0002b): the
> markdown renderer is at `evaluate_detections.py:912,914,915`
> (`:834,837` is the CSV writer with the same behaviour); "439"
> counted files with ≥ 1 problem of any kind under the point-only
> comparer run — rule-explicit counts are 387 (mean-matches, point
> does not) or 623 (plain 3 d.p.); and the divergence spread reaches
> |mean − point| = 0.0151, so triage must compare mean-vs-point per
> cell rather than apply a one-ulp tolerance. The finding itself is
> unchanged.

## 4. Fleet model policy for the mechanical tail

**Ruling: Sonnet permitted for straightforward documents.** The
extraction fleet's remaining 163 batches may run Sonnet on
low-density/mechanical documents (tracking docs, checklists,
low-span-density methodology files) per charter § 8's
"huge-but-straightforward" clause; Opus remains the default for dense
results prose. The validator, recompute harness, and triage gate every
output regardless of extraction model, and `extractor.model` records
which model produced each file.
