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

**Errata to file** (none of these exist yet):

- E37 correction — retitle, re-type *Deviation* → *Correction*, open with an
  explicit withdrawal, state the falsified prediction, the fired stopping
  rule, the activated `coverage.md:187` optimisation contingency, and the five
  genuine elaborations beyond the registered spec.
- H2 Condition C — never executed, never formally dropped.
- Unregistered inference method — the leaderboards use tile-swap permutation;
  the registered method is bootstrap + BH-FDR (`osf:270`). E45 mis-describes
  permutation as registered.
- H7 escalation trigger — fired, not honoured (see § 6.1 for the recommended
  disposition).
- Duplicate erratum — `working-notes.md:6556` declares a second "E47"
  colliding with the canonical E47 and absent from the register.

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

### 6.5 Verification infrastructure (design pending)

Build an agent pair over a skill, per the adversarial-reviewer pilot: the
**skill** holds definitions (anchor standards, verdict vocabulary, the bright
line, the authority hierarchy); the **writer** drafts interpretation with
mandatory anchors; the **verifier** works in fresh context and asks an
*orthogonal* question — "reconstruct what the source says about X" — then
diffs. Do not sample the errata: at this error density, "two errors found by
luck predicted a field of them."

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

## 8. Open questions for the PI

1. H2 Condition C: faithful-to-registration (512 px, Era-1, 340 tiles) or
   current instrument (384 px GS, 487 tiles)? Only the first is the registered
   test.
2. H2 Condition C crop size: 1024 px or 896 px (the spec says both)?
3. Do the four GS sheets span more than one province? Needed for an accurate
   study-area description.
4. Whether to record resolved model strings (`gemini-3-flash-preview`)
   project-wide, or keep the requested alias — deliberately deferred when the
   manifest bug was fixed.
