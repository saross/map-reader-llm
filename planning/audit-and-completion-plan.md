# Preregistration audit and completion — working plan

> **Last revised**: 2026-07-28. **Self-sufficient**: this document is the sole
> starting point for resuming the audit in a new session. Read it, then the
> evidence pointers in § 2, and continue from § 6.

## 1. What this is

A preregistration-integrity audit of the VLM burial-mound detection study,
triggered when a routine check of one analysis sign-off surfaced an erratum
that contradicted the preregistration it described. The audit was escalated
ahead of the paper deadline by explicit decision (2026-07-27): *"the audit is
more important than the deadline, we need to do this right."* Target is a
top-tier journal.

**Two goals.** Confidence that every intermediate artefact aligns with
**(A)** the preregistration plus its amendments — or is clearly documented as
an ad hoc extension — and **(B)** the actual raw results output by each run.

**Escalation trigger held in reserve**: if errors appear to be masking other
errors, widen from the triaged audit to a full unravelling.

## 2. Evidence base — all committed

| document | contents |
|---|---|
| `reports/d17-inventory/step0-summary.md` | **start here** — consolidated Step 0 findings and reading order |
| `reports/d17-inventory/prereg-attribution-sweep.md` | 22 FALSE / 12 UNLICENSED attributions to the preregistration |
| `reports/d17-inventory/unexecuted-register.md` | 46 registered items never run or partly run |
| `reports/d17-inventory/d17-inventory-h*.md` | per-hypothesis inventories (H1–H15) |
| `reports/d17-inventory/d17-errata-census.md` | all 57 errata classified |
| `reports/d17-inventory/e37-pv-preregistration-audit.md` | proves PV *was* preregistered |
| `reports/d17-inventory/step0-h6-walkthrough.md` | H6 forensic (846 lines) |
| `reports/d17-inventory/step0-fine-to-coarse-archaeology.md` | H2 Condition C |
| `reports/d17-inventory/pro-high-text-provenance.md` | data-layer trial — came back clean |
| `reports/d17-inventory/transcript-labelling-errors.md` | transcript-index diagnostic (infrastructure-facing) |
| `reports/d17-inventory/paper-b-verification-lessons.md` | verification design input |
| `docs/paper/results-outline.md` | Results structure; D1–D4 and D12 settled, D5–D17 open |

## 3. Established findings

### The problem is in the interpretive layer, not the data

The `pro-high-text` provenance trial was run deliberately as a probe of
severity. It came back **clean**: the pool is genuinely Pro, no F1/MCC/tier
value moves, the affected metadata class is closed (12 metas / 4 pools, all
pre-2026-03-26), and zero new mis-dispatches exist corpus-wide.

| layer | state |
|---|---|
| raw data and dispatch | **sound** |
| manifests derived from it | one bug, fixed (commit `54aa9bbd2`) |
| documentation and interpretation | **unreliable** |

### The attribution problem is systemic in mechanism, concentrated in location

~80 % of non-SOUND findings reduce to **four substitutions**: Decision 10
cited as prereg § 3.5; study YAMLs cited as registered decision rules;
`analysis-summary.md` cited as the registration (it is not one of the three
lodged documents, `osf/README.md:3`); and a false memory that permutation
testing was registered (`permutation` = 0 hits).

**Structural driver**: `decisions-log.md`, `hypothesis-tracking.md`,
`execution-plan.md`, `analysis-summary.md`, `tasks/` and `simulations/` all
sit *inside* `docs/methodology/preregistration/`, one level above the actual
lodgement in `osf/`. Everything in that directory reads as "the
preregistration".

### Three corrections make the paper stronger

- **E37** — PV was preregistered as H2 Condition B (verifier prompt is in the
  registered appendix). Upgrades the headline from "post-hoc extension" to a
  confirmatory hypothesis whose registered null was falsified and whose
  registered stopping rule fired.
- **H7** — the registration predicted **T=1.0** optimal (`osf:711`); T=0.0
  won. `n1-baseline-matrix.md:401` records this as *supporting* a
  "preregistered T=0.0 optimum" that was never predicted. Correcting it
  upgrades the result to a falsified vendor recommendation.
- **Dawid–Skene** — 14 sites treat it as registered; 0 hits in any canonical
  document. Deletes a Limitations admission about an unregistered analysis.

### Method rules learned the hard way

1. **Verify against the least-writable artefact available.** Prose about
   prose is weakest; manifest better; raw output better; physical
   measurement best. The corpus-description error survived four agent passes
   over documentation and fell immediately to GeoTIFF headers.
2. **Do not filter or attribute transcripts by role.** There is no
   trustworthy authorship field: `userType: external` appears on assistant
   records too, `isMeta` is null on plainly machine content, and
   `type: "user"` is a transport envelope. Search content across the merged
   corpus and read the surrounding record.
3. **A tooling artefact is not evidence of absence.** A line-based grep over
   pretty-printed JSON returned nothing and that absence was reported as fact
   by two successive agents.
4. **Hypothesis numbers shifted three times** before lodgement (H2-C was H10;
   H6 was H8; H14 was H12; H15 was H13; H13 was drafted as H18). Post-lodgement
   numbering is stable, so this affects archaeology only.

### The bright line

The OSF registration was lodged **2026-01-31 23:54 UTC**
(`execution-checklist.md:61`). Anything decided before that fed into writing
the registration and is baked in; it is **not** authority for what should have
been run. Pre-lodgement planning documents do not license a "the
preregistration says" claim.

## 4. Decisions taken

| decision | resolution |
|---|---|
| Results spine (D1) | architecture-ascending, as two explicit parts + a named seam |
| Headline placement (D2) | early, **both** GS and deployment headlines |
| F1-vs-MCC theme (D3) | threaded, home at §R2 |
| Cost split (D4) | split; both levels, each told once |
| Recall-ceiling (D12) | elevate to its own hub subsection |
| MCC board sign-off | signed 2026-07-27T05:28:40Z (`45d0148cd`) |
| Manifest schema | **no change needed** — it models analyses; `not-executed` is a hypothesis property. Add a separate hypothesis register instead |
| BH-FDR family | one primary test per hypothesis (7; H6 never ran) as primary, all-contrasts correction as a reported sensitivity |
| Documentation strategy | **split by derivability** — generate anything derivable (status tables, boards); keep interpretive prose but anchor and verify. Quarantine-and-promote, not rewrite |

## 5. Correction backlog

**Errata to file** — ALL FILED 2026-07-28 (Session 119, Fable):

- [x] E37 correction — retitled, re-typed, explicit withdrawal, falsified
  prediction + fired stopping rule + `coverage.md:187` contingency + five
  elaborations (item 2 phrased as *application* of the verdict, per the
  Fable review § 4.1).
- [x] H2 Condition C — filed as **E59**.
- [x] Unregistered inference method — E45 corrected in place (retitled;
  premise withdrawn; registered method stated).
- [x] H7 escalation trigger — filed as **E60**, including the Fable-review
  strengthening: on the registered 60-tile corpus the trigger never fired
  (verified at `archive/outputs-pre-retest-60-tile/phase2b/`).
- [x] Duplicate erratum — promoted to **E58**; superseded-numbering note at
  `working-notes.md:6556`; broken anchor in
  `results-audit-2026-04-21.md:430` fixed.
- [ ] NEW (Fable review): erratum for the systematic HIGH-thinking-on-Flash
  deviation (currently no erratum; E40 covers only Pro) — sweep U5's
  "related gap".
- [ ] NEW (Fable review): erratum recording the posted `preregistration.md`'s
  stale v4.6 header/footer (the way E1 recorded the README's stale date);
  paper should cite the OSF archive's `updated/` folder.

**Document corrections**:

- `docs/methods-outline.md:341` — "budget prioritised for Flash experiments"
  is invented; the real reason is a dated deferral for a competing paper
  deadline (2026-03-11, in Shawn's own words).
- `hypothesis-tracking.md:86-87` — "coarse-to-fine results were strong
  enough" is invalid under the registered design.
- `reports/experimental-progression.md:49-50` — corpus is **1:50,000**, not
  1:25,000, and **not** the Kazanlak Valley. Confirmed three ways: the
  registration (4 hits for 1:50,000, 0 for 1:25,000); Soviet nomenclature
  (`K-35-052-4` is three-level = 1:50,000); and measured sheet extent
  (~20.8 × 18.7 km = 15′ × 10′). The four GS sheets span lon 24.74–26.75°E,
  lat 41.83–42.50°N — ~165 km west to east. The registration's own hedged
  wording, "Thracian Plain and surrounding areas" (`osf:42`), is correct.
- `reports/experimental-progression.md:264-266` — claims PV could not have
  been anticipated; contradicted by `osf:455` and by E37's correction.
- `n1-baseline-matrix.md:401` — the H7 inversion.
- The four substitution sources (§ 3), which cascade to ~130 sites.
- `hypothesis-tracking.md` should be **generated**, not hand-maintained.

**Structural fix**: header banner on every non-lodged file inside
`docs/methodology/preregistration/`, or relocate the three lodged documents
somewhere unambiguous.

## 6. Work queue

### 6.1 H7 escalation — RECOMMEND NOT RUNNING; file an erratum instead

The registered trigger (`osf:731`): *"If T=1.3 yields higher F1 than T=1.0
(point estimate, same M/E and H5 condition), exploratory testing at T=1.6 and
T=2.0 will be conducted at the optimal configuration to characterise the upper
bound of the temperature-performance curve."*

On the text track the trigger **did** fire on a point estimate. But:

| | ΔF1 | 95 % CI | p | significant |
|---|---:|:---:|---:|---|
| Text, T=1.0 vs T=1.3 | −0.0357 | [−0.0908, +0.0137] | 0.204 | **no** |
| Image, T=1.0 vs T=1.3 | +0.0210 | [−0.0164, +0.0566] | 0.290 | **no** |

Source: `results/retest/pairwise-bootstrap-comparisons.json`.

The CI crosses zero; the direction **reverses** between tracks; and the two
levels compared are the worst two of five on the text track. The full curve
(`results/phase2b-carry-forward-parameters.md:35-70`) is monotone declining:
text T=0.3 0.606 / T=0.0 0.605 / T=0.7 0.584 / T=1.3 0.544 / T=1.0 0.533,
with T=0.3 significantly better than both T=1.0 and T=1.3.

So escalation would characterise the upper bound of a curve already known to
be declining, triggered by a difference indistinguishable from noise. The
scientific question — is there benefit above the vendor default? — is already
answered decisively in the negative.

**Recommended disposition**: file an erratum recording that the trigger fired
as written on a point estimate, that the triggering difference is not
significant (p = 0.204, CI crosses zero), that the direction reverses on the
image track, and that escalation was therefore judged uninformative. This is a
stronger position than running two cells to confirm a decline.

### 6.2 Zero-cost analyses (9 items, $0, run on sapphire)

Highest value first: the **family-level BH-FDR** (definition settled, § 4);
the H6 voting-threshold comparison and ≥0.03 decision rule on existing Pro
data; H8 F1-per-input-token; H10 library-composition; the § 8.6
tile-exclusion register; the § 8.9 latency limb; H1-optimal vs H5-optimal;
H12 error-profile and H11 crowded-area; library manifest and H9 assignment
matrix. Detail in `unexecuted-register.md`.

### 6.3 Paid runs — batch by hypothesis, metadata authored first

| run | hypothesis | scope | cost |
|---|---|---|---|
| `h1-h8-me-sensitivity` | H1 × H8 | 3 cells at the scale-4 library | ~$45–51 |
| `h5-hn-only` | H5 | 1 cell | ~$2 |
| `h2-condition-c` | H2 | fine-to-coarse, GS | needs costing |

`h7-escalation` is removed from this list per § 6.1.

**H2 Condition C** — registered at `osf:478-482`: Stage 1 standard detection
on 512 px with 5-pass voting; identify 2/5–3/5 uncertain candidates; Stage 2
extract ~1024 px tiles centred on each and re-query with a verification
prompt. Stage 1 exists (`outputs/retest/phase3a/`, 512 px, 30 runs per cell;
`build_phase3_subpool_consensus.py` builds the subpool; `lib_consensus.py:238`
already emits `vote_count`). Stage 2 needs no new crop code
(`extract_candidates.py --padding 512` → 1024×1024). New work: prompt file,
`expand_*.json`, ~4–6 h orchestration. **Two open items**: the spec
contradicts itself on crop size (1024 px body `:482` vs 896 px appendix
`:1144`), and the 37 % recall premise is stale given model drift — which
argues *for* running it.

### 6.4 Metadata-as-we-go discipline (NEW — applies to every run above)

Three hand-authored sources feed one generator:

| file | holds |
|---|---|
| `results/run-registry.json` | `run_id`, `directory_path`, `status`, `notes` |
| `results/run-conditions.json` | `_note`, `scope`, `proposer_pools{}`, `verifier_passes{}`, `conditions[]` |
| `results/run-analyses.json` | `analysis_id`, `hypothesis_refs[]`, `preregistered`, `deviations[]`, `predicted_outcome`, `outcome`, `paper_section` |

→ `scripts/generate_post_run_report.py --all --write`

**The rule**: author the registry entry, decomposition, and analysis spec —
including `predicted_outcome` — and **commit them before the run executes**.
Each run becomes a miniature preregistration with a git timestamp.

This is the structural fix for what the audit found. A prediction committed
before the data exists cannot later be rewritten as a confirmation — which is
precisely how the H7 inversion, the invented H6 budget rationale, and the
H2-C rationalisation became possible.

### 6.4a Verification practices for code (settled 2026-07-28)

Derived from what actually worked across three rounds of auditing the manifest
machinery. The datum worth keeping: **fresh-context adversarial review found
every real defect; the author's own tests found none** — including a critical
bug that shipped while passing 31/31 of its author's tests.

**ADOPTED — the two-lens audit.** Written into the `/audit` command
(`~/personal-assistant/commands/audit.md`, commit `491a225`): commit before
delegating; never audit your own work in your own context; run two *orthogonal*
lenses (implementation correctness, test adequacy) in fresh context, read-only,
with `git checkout` forbidden. Lens B is new and is the one that finds why a
defect got past review.

**ADOPTED — the pipeline-fixture rule.** *Any test asserting on a generated
object must build it through the real constructor, never by hand.* A hand-built
fixture can encode a shape the code path cannot emit, so the test passes against
an object that never exists in production. This is exactly how the write-once
guard shipped unusable: its escape hatch was tested against a manifest row
`build_analyses` could not produce. No tooling required; now enforced by Lens B.

**RECORDED, NOT ADOPTED — coverage measurement.** `pytest-cov` is not installed.
It would objectively surface untested branches, but Lens B's "is the wiring
tested?" question found the same gap without it, so the marginal value is now
small. Reach for it if this machinery is substantially extended.

**RECORDED, NOT ADOPTED — automated mutation testing.** `mutmut` or
`cosmic-ray`, scoped to changed modules only (each mutant re-runs the suite).
This is the technique that actually found the green-test bypasses — done by hand
it found one, done systematically by an agent it found five. Worth automating if
the guard logic grows; not worth it while the append-only ledger is about to
replace most of it.

**NOT ADOPTED — property-based testing** (`hypothesis`). Good structural fit for
a JSON-in/rows-out generator with crisp invariants, but the highest-effort item
and not justified before the paper.

### 6.5 Verification infrastructure (design pending)

Build an agent pair over a skill, per the adversarial-reviewer pilot: the
**skill** holds definitions (anchor standards, verdict vocabulary, the bright
line, the authority hierarchy); the **writer** drafts interpretation with
mandatory anchors; the **verifier** works in fresh context and asks an
*orthogonal* question — "reconstruct what the source says about X" — then
diffs. Do not sample the errata: at this error density, "two errors found by
luck predicted a field of them."

### 6.6 Manifest architecture — the principled repair

**Diagnosis: the manifest system models artefacts, not commitments.** Every
entity is validated against something that already exists on disk — `run`
requires a `directory_path`, `conditions_compared` is FK-checked against built
conditions, and `drift_check` reconciles three sources that all describe what
happened. There is no representation of intent, obligation, or authority.

All three audit failure classes trace to that one gap:

| audit finding | root cause |
|---|---|
| H7 inversion; invented H6 rationale; H2-C rationalisation | no timestamped intent — prediction and outcome authored in a single act |
| 4 unhonoured triggers; 46 unexecuted registered items | no place for "promised, not done" |
| 22 FALSE attributions | no link from a claim back to its authority |

The repair is a **second spine** beside the artefact spine:

```text
ARTEFACT (exists today)          COMMITMENT (missing)
run -> conditions -> passes      commitment -> obligation -> discharge
         |                                          ^
      analyses --------------------------------------
```

#### The four changes, by value per effort

**(1) Commitment ledger — `results/commitments.json`.** The registration
decomposed into atomic checkable rows: `commitment_id`, `source` (file + line
in the lodged text), `kind` (hypothesis / condition / factor / trigger /
analysis / disclosure), verbatim `statement`, **`decision_statistic` and
`uncertainty_treatment`**, `status` (open / discharged / waived),
`discharged_by`, `waiver` (E-number).

`drift_check` then gains a fourth check: **any commitment still `open` with no
waiver warns at every regeneration.** The 46-item unexecuted register stops
being an audit discovery and becomes a standing line in the build output.

The `uncertainty_treatment` field encodes the H7 lesson structurally: a
trigger that cannot state how "better" is characterised **fails validation at
authoring time**, before it can create a phantom obligation.

The ledger should be authored **at lodgement, from the registration, before
execution**. For this project it is retrospective — but the content already
exists in `unexecuted-register.md` and the trigger census; what is missing is
making it live.

**(2) Write-once predictions.** `predicted_outcome` becomes immutable: the
generator refuses to modify a non-null value. Amendment requires an explicit
`predicted_outcome_amended` object carrying reason and date, which then
surfaces in the manifest. Makes the H7 inversion *structurally impossible*
rather than merely discouraged. **Implemented 2026-07-28.**

**(3) `status: planned` on runs.** Planned runs are held in the registry but
excluded from the generated manifests, which continue to describe only what
exists. A `planned_at` date supports a staleness warning. This makes the
honest ordering — intent, then execution, then outcome — representable at all.
With (2), the prediction precedes the data by construction rather than by
discipline. **Implemented 2026-07-28.**

**(4) Source anchors on authority claims.** Any field asserting registration
authority carries a resolvable `source`; the generator validates that it
resolves. Converts the attribution sweep — which cost one agent 378 k tokens —
into a build-time check.

#### C3 — the open bypass in the write-once guard (DECIDED 2026-07-28)

**The hole.** The guard compares the incoming manifest against the one currently
on disk, so a row that *disappears* takes its prediction history with it. Delete
an analysis from `results/run-analyses.json`, build (the row vanishes), re-add
the same `analysis_id` with a different prediction, build again — **no step is
blocked**. Renaming `analysis_id` achieves it in a single build. This is the
historical failure mode surviving the repair.

**Decision (Shawn, 2026-07-28): (b) now, (d) later.**

- **(b) — DONE.** `check_write_once_predictions` now emits a loud `WARN` to
  stderr when an analysis carrying a non-empty prediction disappears from the
  manifest, quoting the prediction that is losing protection. This raises the
  cost of the bypass and makes step one visible in the build log. It does **not**
  close the hole.
- **(d) — TODO, with the commitment ledger.** An **append-only prediction
  ledger** that never loses rows: deleting an analysis removes it from the
  manifest but not from the ledger, so re-adding it is checked against the
  original prediction. This is the same artefact repair (1) needs, so building
  it once serves both.

**Options considered and rejected**:

- *(a) accept and document* — cheapest, but leaves a claim we would have to
  soften in the paper for no gain once (d) is being built anyway.
- *(c) check against git history* rather than the working manifest. Conceptually
  the right answer, since git already **is** the audit log. Rejected because it
  couples the generator to git state (shallow clones, detached HEAD, ordering
  relative to the commit) in a script that otherwise touches only JSON — and the
  ledger buys the same guarantee with a plain file.

**Until (d) lands, the honest claim about this machinery is "prediction
rewriting is DETECTABLE", not "structurally impossible".** Any paper or
methods text describing the guard must use the weaker wording. This is recorded
here so the stronger phrasing is not reached for by habit.

**(5) Filesystem authority separation** (not code). `preregistration/lodged/`
with a hash manifest versus `preregistration/working/`. The structural driver
of the attribution problem was working documents sharing a directory with the
lodgement; a hash manifest also makes OSF drift detectable.

#### Deliberately not built

- **Not a workflow engine.** The discipline is the point; automating execution
  addresses no finding.
- **Not automated verification of interpretive claims.** Paper-B is explicit
  that reliability transfers exactly as far as a structural check exists.
  "We deprioritised C because B was strong" has no anchor and never will.
- **Not a database.** Git supplies the timestamping and *is* the audit log;
  JSON plus commits is the right substrate.

#### Sequencing

- **This project**: (2) and (3) first — small, and they protect the runs about
  to be launched. (1) once the trigger census lands, since that supplies the
  trigger rows and the unexecuted register supplies the hypothesis rows. (4)
  and (5) with the documentation revision.
- **Future vision projects**: build (1) first, at preregistration time. The
  ledger costs almost nothing when authored from a live registration, and
  everything else hangs off it.

#### The framing worth keeping

Every fact this audit surfaced was already on disk; nothing was hidden or
lost. It took five agents and two days because the system had no way to
surface *"you promised X and have not done it"*. The commitment ledger is what
converts audit into monitoring — a thing run once, versus a thing that reports
continuously.

## 7. Held elsewhere

- **Transcript infrastructure fixes** — being handled in a separate
  personal-assistant session. Recommendation passed back: consolidate the raw
  corpus and search that (raw is a strict superset of the archive); add a thin
  extraction pass emitting `(session_id, record_idx, timestamp, type, text)`
  with **no speaker column**, since no trustworthy authorship field exists.
- **OSF-side verification** — diff the posted artefact at `osf.io/tybgq`
  against blob `fa221b30f395feb7ef0c9425c36eae0b94e917ba` before submission.
  The repo copy is byte-identical from the registration commit to HEAD, but
  the OSF side has not been fetched. An API key exists at
  `~/personal-assistant/.env` (do not read it into context).

## 7a. Session status — resume here (updated 2026-07-28, Session 119/Fable)

**The adversarial review is DONE**:
`reports/d17-inventory/fable-adversarial-review-2026-07-28.md` (`fdc711145`).
Headlines: OSF-side verification CLOSED (posted `updated/` set byte-identical
to the repo lodged copies; lodgement actually 12:54:09 UTC — the 23:54 figure
was AEDT mislabelled as UTC); C1–C6 survive spot-checking; C5's trigger census
was never published (write `reports/d17-inventory/trigger-census.md` before
using P4); P2's "~80 % four substitutions" does not reproduce (~a third of
sites; six single-source families cover ~three-quarters); three unrun probes
named (numbers-vs-artefacts sweep of paper-bound prose; execution→errata
inverse census; passes-manifest field probe).

**The correction pass is SUBSTANTIALLY DONE** (commits `2c354ca2e` →
this one): all § 7a-items 1–4 of the previous version of this block are
complete — the five isolated corrections; the four substitution-source root
fixes + directory banners; the carry-forward chain (FALSE-3/4/5/6); E37 and
E45 corrected in place; **E58/E59/E60 filed**; E10 reclassified
Clarification→Deviation with its E11/E12/E13 cascade; E22/E26/E35/E49/E53/
E54/E56 attribution corrections; Decision 26 corrected (greedy IS registered,
§8.5); the D-S family (FALSE-12) de-"preregistered" across all results docs;
the first-N boilerplate (U2) fixed in 39 summaries + 3 scripts;
run-analyses.json citations repointed and manifests regenerated (drift clean);
results-draft.md diversity passage corrected (U5/U12). Tier-1 1,178 passed.

**Remaining, next session:**

1. **Notes-file sites** (reflections + working-notes families: FALSE-11
   permutation traces, D-S ×7, FALSE-17/18 families, U4 ×6) — sweep
   recommends appended dated correction notes, not edits; consider one new
   Obs rider covering the lot.
2. **Two new errata** queued in § 5 (HIGH-thinking-on-Flash; stale v4.6
   header of the posted primary document).
3. **The nine zero-cost analyses** (§ 6.2), starting with the family-level
   BH-FDR — now also motivated by the corrected E45 (registered bootstrap+FDR
   must accompany permutation results). Runs on sapphire.
4. **Publish the trigger census** as an artefact (C5).
5. **Two of the three unrun probes** from the Fable review § 5 Q4: the
   execution→errata inverse census and the passes-manifest field probe.
   The third (numbers-vs-artefacts sweep of paper-bound prose) is
   **DROPPED per Shawn 2026-07-28**: all paper-bound text will be
   regenerated from the source documents using the new prose-generation
   skill, so auditing the existing prose is wasted effort. The corollary:
   the *source* documents (`results/**`, `reports/**`) are now the binding
   accuracy constraint for regeneration — which is what the correction pass
   just addressed.
6. Legacy markdownlint debt in `preregistration/simulations/` (20 errors,
   pre-existing; `osf/` files must NEVER be lint-fixed — they are frozen).

**Not started, needs a decision or a gate**: the paid batch (§ 6.3); the
commitment ledger (repair (1), closes C3). **Needs Shawn**: § 8 questions,
plus the embargo-field discrepancy (checklist says "None"; OSF API records
`embargo_end_date: 2026-06-30`), and the H4 omnibus-vs-contrast question
(decides whether H4b is owed).

## 8. Open questions for the PI

1. H2 Condition C: faithful-to-registration (512 px, Era-1, 340 tiles) or
   current instrument (384 px GS, 487 tiles)? Only the first is the registered
   test.
2. H2 Condition C crop size: 1024 px or 896 px (the spec says both)?
3. Do the four GS sheets span more than one province? — PI answer
   (2026-07-28): unknown, never tracked against Bulgarian internal divisions;
   resolvable by projecting the four sheet extents onto a provinces layer if
   the regenerated study-area description needs it. (Cheap GIS check; can be
   done on request.)
4. Whether to record resolved model strings (`gemini-3-flash-preview`)
   project-wide, or keep the requested alias — deliberately deferred when the
   manifest bug was fixed.
