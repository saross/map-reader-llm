# Phase 3 in-flight PI rulings — 2026-07-31 (Session 122)

Four rulings collected interactively mid-phase (structured options per
the S121 calibration rule); recorded here so triage and the fleet can
proceed without re-litigating them at GATE 3. Controller:
`planning/audit-charter.md` § 7 Phase 3. **Session-123 rulings 5–11
appended 2026-08-01 (§§ 5–11 below).**

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

---

## Session-123 rulings — 2026-08-01

Collected interactively after the S123 triage/repair arc; same force
as rulings 1–4.

## 5. Fleet model policy — Sonnet gate discharged

**Ruling: Sonnet tail runs free.** The ruling-4 spot-audit passed
(`reports/verification/c4-triage/spot-audit/spot-audit-verdict-2026-07-31.md`:
zero missed claims either direction on the b014 Opus duplicate).
Sonnet is the default for ruling-4's document classes; Opus for dense
results prose; **new task kinds or radically different target sources
get a fresh Opus-duplicate comparison before Sonnet scales there**,
and doubt escalates to Opus. Rationale: at ~25M projected fleet
tokens, the Sonnet share is material top-tier-credit conservation.

## 6. Broken-correspondence cells (corrected form)

**Ruling: ledger + banner + Obs 377; no remediation re-run.** As
corrected by the Obs 377 writer's independent verification: ONE
genuine post-audit regression (`text-t0.0/verified-v1-n3`, pool
re-materialised 1,256 → 1,319 on 2026-07-30, gap 63; zero
conditions-manifest exposure); the other four flagged cells were a
triage-level wrong-pool binding artefact, re-bound and confirmed
MATCH. Condition for remediation (paper exposure) verified absent.

## 7. Recompute-script class — comprehensive, not deferred

**Ruling: bite the bullet.** Build a runner registry in the recompute
harness (census/count primitive first — it covers roughly half the
class; then the audited-flex cost/token runner; then statistical
runners on the existing bootstrap/permutation/tiering machinery,
executed on sapphire). Execute over the current corpus immediately and
re-execute per fleet wave. Any family that proves genuinely hard
becomes a NAMED line with its count in the GATE 3 package — no silent
deferrals.

## 8. File-level claims — dedicated repair pass

**Ruling: do now, no folding.** First item of Session 124: one
dedicated repair pass over the ~204 pathless file-level values via a
shared quantity→anchor mapping (conditions-manifest filter paths,
bounds len: counts) plus an LLM tail for the remainder. Instrument
v1.2 amendment 3 caps growth of the class.

## 9. Missing-anchor artefacts — git-era resolution

**Ruling: resolve at the document's era.** For anchors deleted after
extraction (~38 rows), the resolver gains a git-era mode: resolve the
anchor from the blob at the source document's era commit. Ruling 1
covers document bodies; this extends the same era logic to anchor
resolution.

## 10. Materiality ratifications

**Ruling: ratified as adjudicated.** No superseded-figures banner on
the 2026-03-27 adversarial-audit report (header CI moved with
post-audit re-scores; verdicts hold in both eras); the S111 dossier's
"2.4–2.7 %" band edge stands as in-era presentation (artefact
2.64 %). Ledger rows only.

## 11. Independent verification — systematise the pattern

**Ruling (PI, verbatim intent): "We should systematise the
independent-verification pattern wherever possible, it's the way to
be sure about things."** The pattern — a blind re-derivation by a
fresh context before an artefact lands — corrected the record twice
in two sessions (Obs 376/regen-0002b: the writer corrected the
author's probe record; Obs 377/round-4: the writer refuted the
triager's causal story for four of five cells). Standing application
in Phase 3+: obs-writer re-derivation remains mandatory; triage
adjudications that assert causal mechanisms get an independent check
before ledger emission; `generate_c4_ledger.py` carries a
verification lane; gate packages are assembled with the same
discipline. Writer-vs-author disagreement is signal, not friction.
