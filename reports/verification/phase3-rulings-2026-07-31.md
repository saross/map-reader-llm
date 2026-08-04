# Phase 3 in-flight PI rulings — 2026-07-31 (Session 122)

Four rulings collected interactively mid-phase (structured options per
the S121 calibration rule); recorded here so triage and the fleet can
proceed without re-litigating them at GATE 3. Controller:
`planning/audit-charter.md` § 7 Phase 3. **Session-123 rulings 5–11
appended 2026-08-01 (§§ 5–11 below); Session-124 rulings 12–13
appended 2026-08-01, second batch (§§ 12–13 below).**

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

---

## Session-124 rulings — 2026-08-01 (second batch)

Collected interactively after the S124 wave-2 triage and repair arc;
same force as rulings 1–11.

## 12. Era-check extension for moved anchors + snapshot classification

**Ruling: approved as recommended.** On dated-snapshot documents, a
MISMATCH on a mechanical (`read`/`arithmetic`) row gains a
supplementary `era_check` field — the harness re-resolves the locator
(or every operand) at the source document's era commit and records
whether the document was faithful to its era. Never a status change:
the primary verdict stays the current-artefact comparison; the field
lets triage separate SNAPSHOT-DIVERGENCE from SNAPSHOT-DEFECT
mechanically. **Snapshot classification rule (provisional — finalise
after experience in actual use): a dated filename or dated title
makes a document a snapshot, regardless of directory location.**
Motivating case: wave-2 family 002 — 7 of 14 `run.meta.json` operands
overwritten in place; era-faithfulness took a manual blind pass to
establish (Obs 380).

## 13. The 005#2[0] gap-bound escalation

**Ruling: adjudicate in wave-3 under the usual discipline.** The
`n1-baseline-matrix.md` "board-vs-micro F1 gap ≤ 0.0003" bound versus
`tiering_20m.json` `f1_gap` spanning to 0.000466: blind verification
before any edit; LIVING-DOC-FIX with changelog if confirmed.

---

## Session-125 rulings — 2026-08-03 (third batch)

Collected interactively via the D1–D6 decision sequence; same force as
rulings 1–13. (D1 landed Obs 385; D2 the E39 fix, commit `01c84b841`;
D3 is a documentation-governance ruling recorded in
`output-directory-standard.md`'s scope section; D6's root-cause fix is
commit `75aa47125`.)

## 14. Snapshot classification finalised — the two-axis rule (supersedes ruling 12's provisional sentence)

**Ruling: adopted as recommended.** The presentation class (dated
filename or dated title) is ADVISORY ONLY — it never decides a
disposition. The deciding axis is per-claim era-faithfulness (the
`era_check` machinery; extending it to runner rows is registered
instrument work). For entry-dated registers (protocol-errata,
decisions-log), the snapshot unit is the ENTRY, not the file.
Dispositions follow evidence: era-faithful + artefact moved ⇒
SNAPSHOT-DIVERGENCE; wrong at its own era ⇒ DOC-DEFECT-AT-ERA,
regardless of filename. Motivating cases: the S125 wave-4 triage's
three misleads (h11 dated-filename report carrying doc-defects-at-era
on a file unchanged since five weeks before it;
session-111-discoveries behaving as living despite its dated title;
E-entry dating in the errata register).

## 15. Machine scope — the tracked-proxies rule (GATE 3 ruling on Obs 383's question)

**Ruling: adopted with phasing.** Mechanical verification scope =
git-tracked artefacts PLUS tracked proxies: a **regeneration
manifest** (generator + tracked inputs + params + expected
count/content-hash) is the tracked, machine-independent referent for a
regenerable untracked tree; a **bundle index** (tracked
checksums/sizes) is the referent for non-regenerable bulk whose
payload lives outside git (cross-machine syncable now;
Zenodo-depositable at publication, alongside the GitHub-integration
code DOI). Claims anchored to neither are a NAMED triage family, never
silently mechanical. Phasing: (1) tracking-gap audit + commit of
small analysis-relevant strays (the 044-class) and (2) regeneration-
manifest pilots for the two census-implicated crop trees execute in
S125; (3) bundle-index pilot on one run with mass bundling deferred to
a dedicated session (storage decision); (4) charter § 4/§ 5 amendment
plus registry re-anchoring ride the queued register re-anchoring; (5)
Zenodo assembly at publication. Rationale (PI, 2026-08-03): the
untracked strata split into regenerable-by-recipe, non-regenerable
evidence, and by-omission strays — each wants a different referent,
and the proxies keep every quoted verification figure checkable by an
external reader.

## Session-126 rulings — 2026-08-03 (fourth batch)

Collected interactively at the S126 wave-6 escalation review; same
force as rulings 1–15.

## 16. Approximate-equality threshold for cost/ratio claims

**Ruling (PI, verbatim intent): "anything within ~5 % can be called
'approximately equal'."** Applied first to escalation W6-E1: the
audited 55-map production costs (image $200.83 vs text-HIGH $207.34,
ratio 0.97×) supersede the cross-track report's "2.9× lower API cost"
conclusion, and the corrected claim is **approximately equal API
cost**, not a new ordering. The threshold generalises to future
cost/ratio repair wording: differences within ~5 % are presented as
approximate equality rather than a ranking.

## 17. Partial-refresh residue in living documents — the two-layer rule (resolves W6-E3)

**Ruling: adopted as recommended.** Ruling 14 and the Document
Revision Policy operate at DIFFERENT LAYERS and do not compete.
Ruling 14 remains the TRIAGE vocabulary: a clause faithful when
written whose artefact later moved books as SNAPSHOT-DIVERGENCE, not
a defect — the historical verdict stands. The Document Revision
Policy remains the REPAIR policy for living documents
(`results/**.md`, `reports/**.md` in scope): stale clauses are
refreshed in place with a changelog entry, ledger cross-referenced,
so readers see current truth on first read. "Divergence ⇒
ledger-only" was a triage-lane verdict, never a repair rule. Dated
snapshot records keep ruling-1 banner/rider treatment. Where a
refresh changes a cited 3-d.p. form, downstream citations are swept
in the same pass (P2 R9's coupling discipline).

---

## Session-127 rulings — 2026-08-04 (fifth batch)

Collected interactively during the wave-7 escalation review, in the
48-hour Opus window. Same force as rulings 1–17.

## 18. Repair-and-re-extract coupling; the backlog rides the waves

**Ruling: complete repair, sequenced by coupling rather than by date.**
The PI asked the right question of the W7-E2 escalation — if future
corrections re-stale the corpus, *when* does a complete repair happen?
The answer is that no date works on its own: 78 batches remain (~4
waves), every wave produces triage repairs, and every repair re-stales
the documents it touches. A sweep run early is invalidated ~4 more
times; a sweep run late leaves every intervening wave carrying
spurious mismatch rows.

Adopted instead, in this order:

1. **The coupling invariant, effective immediately** — a pass that
   edits a mine document re-extracts it in the same commit. Landed as
   charter § 5 rule 14. This stops accumulation at source and is what
   makes any subsequent sweep durable.
2. **Clear the pending document-repair queue first** — the deferred
   wave-6 doc repairs, W6-E10, and W7-E4 are known future edits;
   sweeping before them would re-stale exactly those documents.
3. **Fold the backlog into waves 8–12** — 18 documents, 10,092 lines,
   roughly 40 batches, distributed across the remaining schedule rather
   than run as a separate exercise. Total fleet ~118 batches instead of
   78, with no second pass over the corpus.
4. **GATE 3 carries a whole-corpus validation and drift check** as
   proof the invariant held. Per-wave validation sees only its own
   wave, which is precisely why the drift went unnoticed for six waves.

Rejected: a single pre-GATE-3 sweep with no invariant (cheapest to
schedule, but every intervening wave's triage pays for it), and
limiting the backlog to paper-citable documents (paper exposure is not
currently recorded anywhere, so it would need establishing first).

## 19. The four ground-truth layers, and what each may be used for

**Ruling (PI, 2026-08-04).** Prompted by the PI's question "did I really
find so few additional mounds? I thought I'd found hundreds" — which
was the right instinct and surfaced a layer the session had missed. The
55-map ground truth is FOUR things, not three, and they are not
interchangeable:

1. **The fixed original student digitisation** —
   `inputs/vectors/references/student-mounds-55maps.geojson`, **4,770**
   features. Verified genuinely immutable: one commit ever
   (`301b51128`, 2026-04-08), working-tree md5 byte-identical to it.
2. **The current corrected student GT** —
   `student-mounds-55maps-reviewed.geojson`, **4,746**. Reached by
   4,770 − 52 + 28: twenty-six merged-centroid replacements of student
   double-marks under 50 m, plus two curator additions. A NET DECREASE,
   because it is duplicate-cleaning, not discovery.
3. **Historical corrected states** — 4,744 (`dea1155fa`) and 4,745
   (`baf1497a7`). **Historical record only.**
4. **The reviewer-promoted extension** —
   `results/deployment-oracle-2026-06-06/canonical-gt/canonical-review.csv`,
   **773 mounds**, every row `human_label=mound`. These are the PI's
   "hundreds": real mounds the students missed, held as a separate
   layer rather than merged into the student GT. They enter analysis
   through the extended GT, gated per buffer — 474 qualify at R = 50 m,
   rising to 672 at 150 m, giving extended references of 5,220 to 5,418.

**Rulings on use**:

(a) **The historical corrected GT is a record, not an input.** It must
not be used in any analysis postdating the correction to 4,746. Where a
dated document describes what a 2026-05-03 evaluation consumed, that is
history and stays; where anything *computes* on 4,744 or 4,745 today,
it is wrong.

(b) **Nothing goes to publication on 4,770 where 4,770 is the wrong
reference.** Re-running metrics is authorised where needed; the cost of
a re-run is not a reason to publish a figure computed against the
uncorrected base.

(c) **W7-D8 is deferred, not dismissed.** The t0.3 evaluation-layer
difference touches a run that leads on F1, so it is handled
deliberately rather than opportunistically: keep it well documented and
investigate when the time comes. Its documentation obligation is
therefore load-bearing — the finding must stay legible until someone
acts on it.

**Note for future sessions**: the four-layer structure explains a
recurring confusion. A reader meeting "4,746" naturally reads it as
"all the ground truth", and then the PI's review effort looks
vanishingly small. The 773-mound extension is where that effort lives,
and any document citing a student-GT count near a claim about review
effort should say which layer it means.
