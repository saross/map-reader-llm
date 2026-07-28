# Adversarial review of the Session-118 preregistration audit — Fable second opinion

> **Last revised**: 2026-07-28 (initial publication). See [§ Changelog](#changelog)
> for revision history.

**Reviewer**: Claude Fable 5 (fresh context, different model from the audit's
author, per Shawn's request). **Brief reviewed**:
`planning/fable-review-brief-2026-07-28.md`. Method: claims re-verified at the
cited artefacts; two SOUND verdicts re-checked as a bias control; the one
unclosed evidence link (the OSF-posted artefact) fetched and closed; one
transcript claim re-derived from the raw session archive rather than the index.

## 0. Verdict in one paragraph

The audit's findings survive adversarial re-checking: every claim I probed at
source held (C1, C2, C3 spot-checks, C4 structure, C6), and the previously
unclosed link — whether the repo copy of the registration is what was actually
posted to OSF — is now **closed in the audit's favour** (§ 1). The patterns are
a different matter: **P2's "~80 % reduce to four substitutions" does not
reproduce under any counting I could construct** (§ 3.2), C5's trigger census
was never published as an artefact and its falsification route is therefore
unrunnable (§ 2, C5), and P3 and P5 over-claim as causal stories while being
sound as cheap mitigations (§ 3.3, § 3.5). The fixes are sound but mildly
over-built relative to the paper's exposure, which remains the uncorrected
record — the prior session's own suspicion on this point (§ 3 of the brief) is
endorsed. Answers to the five § 5 questions, including three named unrun
probes, are at § 5.

## 1. New evidence: the OSF-posted artefact, fetched and diffed

The brief's one unclosed link (§ 1, "if you can fetch it, do") is closed.
Fetched via the OSF API v2 (`api.osf.io/v2/registrations/tybgq/`, public,
`reviews_state: accepted`), registration archive listed and downloaded.

**Finding 1 — the chain closes.** The registration archive's `updated/` folder
contains all three lodged documents **byte-identical** to the repo copies:

| file | OSF blob (git hash-object) | repo blob | match |
|---|---|---|---|
| `updated/preregistration.md` | `fa221b30f395…` | `fa221b30f395…` | **exact** |
| `updated/preregistration-appendix-prompts.md` | `5bf2261fab09…` | `5bf2261fab09…` | **exact** |
| `updated/preregistration-coverage.md` | `da6f107f09dd…` | `da6f107f09dd…` | **exact** |

C1 and C2 therefore no longer rest on the repo copy being what was posted —
the posted copy **is** the repo copy. E37 contradicts the artefact OSF hosts.
Independently, the registration's own narrative summary (in
`registered_meta`, frozen at lodgement) names the registered inference method:
*"bootstrap confidence intervals and False Discovery Rate correction at
q = 0.05"* — zero mention of permutation. C2 is corroborated from the OSF side.

**Finding 2 — the recorded lodgement timestamp is mislabelled, and a claim in
the brief is a timezone artefact.** OSF records
`date_registered: 2026-01-31T12:54:09Z`. `execution-checklist.md:49,61`
records "2026-01-31 23:54 UTC" — that is 23:54 **AEDT** mislabelled as UTC.
Consequence: the brief's "byte-identical from a commit 11h20m before the
registration timestamp" compares the commit's UTC time (`bd65c007f`,
12:34:27 UTC) against the mislabelled local time; the true margin is
**~20 minutes**, not 11 h 20 m. The direction still holds, and byte-identity
with the posted artefact now makes the margin moot — but the bright line moves
11 hours earlier, so I checked the window it opens: the only commit between
12:54 UTC and 23:54 UTC on 2026-01-31 is `a9ed78b05` (13:02 UTC, an archive
chore that also fixed the OSF README date — see Finding 4). **No decision or
scientific artefact changes classification.** The timestamp should be
corrected wherever quoted (`execution-checklist.md:49,61`;
`reports/d17-inventory/unexecuted-register.md` header; `step0` material).

**Finding 3 — the registration archive has two file sets, and the top-level
one is not the operative version.** The archive's top level holds the
pre-date-bump files (main document identical to the repo copy except the
line-2390 date, "2026-01-14"); the operative v4.7-content set sits in the
`updated/` folder. Anyone downloading top-level files from OSF gets a
one-line-stale main document and a README/coverage claiming v4.6. **The paper
and data-availability statement should cite the `updated/` folder path
explicitly.**

**Finding 4 — the lodged artefact's version metadata is internally
inconsistent** (confirms UD-2 of the attribution sweep from the OSF side).
Both posted copies of `preregistration.md` self-identify as **v4.6** in header
(`:9`) and footer (`:2388`) while carrying the v4.7 changelog entry (`:2394`);
the lodged README and coverage doc claim "v4.7". The one-line README
difference between posted and repo copies is explained by `a9ed78b05` landing
the date fix **8 minutes after lodgement** (E1 records the same correction).
Recommendation: an erratum recording the stale header of the primary document,
exactly as E1 recorded the README's — a reviewer citing "prereg v4.7" against
the posted file will find "4.6".

## 2. The seven claims — verification outcomes

| # | outcome | notes |
|---|---|---|
| C1 | **CONFIRMED** | `osf:455-457` registers "Coarse-to-fine (proposer-verifier)" with prediction, test table, stopping rule; verifier prompt lodged at appendix § 1.6.2; E37's description (`protocol-errata.md:904`) contradicts it verbatim. OSF byte-identity closes the last escape route. |
| C2 | **CONFIRMED, evidence line needs fixing** | "grep = 0 on `osf`" is true only of `preregistration.md`; the lodged **appendix** has 3 hits, all H4 example-order shuffling (`:1528,1533,1711`), none statistical. The claim survives; the stated evidence under-describes the search space and should quote the appendix hits so the negative is auditable — the sweep's own § "Method note" standard. |
| C3 | **CONFIRMED on spot-checks** | Re-verified at source: FALSE-8 (E37 text vs `osf:466-476`), FALSE-13 (§ 8.5 step 4 registers "Greedy clustering" by name), FALSE-16 (`osf:711` predicts T=1.0 optimal, "lower temperatures will degrade"), U1 (Decision 10 at `decisions-log.md:337` holds the 1000-iteration/percentile/tile-level parameters; the registered text has only "95 % bootstrapped CIs"). Bias control: two SOUND rows re-checked (E52's model citation `protocol-errata.md:1498` vs `osf:1010` — exact; `merge_passes.py` § 8.5 refs — correct). Counts match: FALSE-1…22, U1…U12. |
| C4 | **CONFIRMED structurally** | 46 distinct items across 48 rows with an explicit trust policy re-deriving execution status from manifests, not documentation. Not all 46 re-derived here (out of scope for one session); the register's method — which caught H10/H12 as *falsely believed unexecuted* — cuts both ways, which is the property you want. Header repeats the mislabelled 23:54 UTC timestamp (Finding 2). |
| C5 | **WEAKEST CLAIM — census unpublished** | The brief cites "`reports/d17-inventory/` trigger census". **No such file exists.** The 43/16/1 numbers live only in `session-log.md:7445` and a gated working-notes candidate (`working-notes.md:21695`). The falsification route ("find a conditional we missed") cannot be run without the enumeration. Before P4 goes anywhere near the paper, the census must be written up as an artefact with per-conditional verdicts. NB the working-notes version contains a *stronger* H7 fact than plan § 6.1 uses: on the registered 60-tile K=10 corpus the trigger **does not fire at all** — the firing exists only on the E36-expanded corpus. That belongs in the H7 erratum. |
| C6 | **CONFIRMED at report level** | The provenance report is anchored, self-critical, and documents its own live failure demonstration (line-based grep on pretty-printed JSON producing a confident false absence from two agents). One probe remains one probe — see Q1. |
| C7 | **ACCEPTED, not re-sampled** | Infrastructure-facing, handled in the personal-assistant thread; re-sampling has no paper value. The operational rule it produced (never attribute by role metadata) was applied in this review (§ 4). |

## 3. The patterns, attacked

### 3.1 P1 — "interpretive layer, not data": directionally right, under-supported as stated, and better supported than the brief admits

The brief is right that one deliberate probe is weak. But the data layer has
survived more checks than the pattern cites, all incidental: the S105/S106
re-scores reproduced published operating points to ~4–7 d.p.; the S113 billing
reconciliation matched the console to −4 %; the S114–117 identical-confusion-
matrix coincidence was checked and cleared; drift-checks run at every build.
The honest statement is: *the data layer has repeatedly survived incidental
re-derivation and one deliberate probe; the documentation layer failed
systematically wherever probed.* That is stronger evidence for the contrast
than the single-trial framing — and it still licenses a second deliberate
probe (Q1, § 5).

### 3.2 P2 — "~80 % reduce to four substitutions": DOES NOT REPRODUCE

Counting the sweep's own enumerated sites: the four named sources — Decision 10
as § 3.5 (U1, 12 sites), study YAMLs as registered rules (FALSE-3/4/5/6/7/21 +
U6/U8, ~11 sites), `analysis-summary.md` as the registration (U4 + FALSE-13,
~17 sites), the permutation false memory (FALSE-9/10/11, ~5 sites) — total
**~45 sites of the ~138 the sweep identifies, i.e. roughly a third**, not
~80 %. Counted by findings instead of sites: at most 16 of 34
FALSE+UNLICENSED, under half. The two largest single families are **not
substitutions**: U2's first-N § 3.8 boilerplate (42 sites — over-generalising
a *partially* registered convention) and the Dawid–Skene family (FALSE-12,
18 sites — outright invention). The 22 FALSE class also contains two fabricated
quotations (FALSE-4, FALSE-15) with no source anywhere in the repository.

The defensible restatement: **six single-source corrections (the four
substitutions, the first-N boilerplate, the D-S family) cover roughly
three-quarters of affected sites** — the cascade logic is right, the
mechanism taxonomy under it is not. This matters beyond bookkeeping: "four
substitutions" implies the fix is *citation discipline*; the boilerplate and
invention families require *content verification*, which no directory banner
prevents. It also re-scopes § 7a item 1 (see § 6).

### 3.3 P3 — directory layout: a contributing risk, not "the structural driver"

For the substitution families the mechanism is plausible, and the fix (banners
/ `lodged/` split with hash manifest) is cheap and worth doing. But three
observations cut against the causal story: (a) the D-S, fabricated-quote, and
permutation-memory families have nothing to do with directory location;
(b) the same directory produced model citations (E52's exact-line quote,
`hypothesis-tracking.md`'s correct rows) — location is not sufficient;
(c) the errata register itself produced FALSE content (E10, E37, E45, E54),
and errata are *legitimately* authority-adjacent — no banner fixes that. The
deeper mechanism, which the step0 report already identified, is **rationales
written from memory during documentation-catch-up commits without re-reading
the source**. The layout fix is worth its ten minutes; it should not be sold
as closing the class.

### 3.4 P4 — the four-things trigger rule: the best idea here, currently unpublishable, and missing a fifth thing

The rule (statistic, comparison scope, uncertainty criterion, evaluation
moment) is genuinely good and the H7 case study is vivid. Two problems. First,
its evidentiary base is C5, which exists only as session notes (§ 2). Second,
the project's own H7 evidence shows the list is incomplete: the trigger fires
on the 340-tile expanded corpus and **does not fire on the 60-tile corpus the
registration specified** — so a trigger must also name its **evaluation
corpus/data scope**. Five things, not four. The strongest version of the
publishable claim comes from the project's own near-miss.

### 3.5 P5 — "artefacts, not commitments": right design principle, over-unified as diagnosis

The commitment ledger genuinely addresses the unexecuted-register class (46
open items become a standing build warning) and, via append-only rows, closes
C3. The prediction-rewrite class is addressed by repairs (2)+(3). But the
largest class — the 22 FALSE attributions — is prose written from memory, and
no data model prevents it; repair (4) (resolvable source anchors) helps only
where claims are structured, and the two-lens audit is the actual control. "All
three failure classes trace to that one gap" is tidy, as the brief itself
warns; two of three trace to it well, the third only partially.

## 4. The brief's self-identified errors — checked

**§ 4.1 (E37 reversal)**: the reversal is right — verified at `osf:455-476`,
appendix § 1.6.2, and now against the posted artefact. The five-elaborations
enumeration is **materially right with one wording hazard**: item 2 ("binary
verdict vs registered raw probabilities") is about the *handling* — the
headline pipeline applies the verifier as accept/reject with
`prob_threshold = null` (E56, `protocol-errata.md:1755`) against the
registered "raw `mound_probability` scores used directly … no binary
thresholding" (appendix `:1584`) — not about the prompt's output type: the
production adversarial prompt still elicits `mound_probability`
(`prompts/system-instructions/verify_adversarial.md:50`). The corrected E37
should phrase it as application, not output. The full e37 report (§ 6) already
gets this right; the brief's compression loses it.

**§ 4.2 (role-metadata error)**: independently re-derived. I read the **full
raw session archive** (`~/cc-archives/map-reader-llm/2026-03-07T05-59_c634c7c3`,
4,201 records — the index holds only 361 turns) rather than the index.
Confirmed: the Condition-C question was asked twice (records 3509 and 3568,
"Confirm C stays dropped?" with recommendation "Drop (confirm)"), and **no
subsequent user turn engages it** — Shawn's substantive reply (record 3573)
addresses Phase 2e, the 1+1 pilot, and text-track adaptation, not Condition C.
The "no decision was ever made" conclusion is now confirmed from the primary
source. One trap for future archaeology: record 3733's "Condition C" is Phase
3c's *diversity* condition C, an unrelated identifier collision.

**§ 4.3 (the shipped guard bug)**: not re-audited (already audited twice,
fresh-context). The implementation read for § 5 Q5 shows honest in-code
limitation notes ("C3 MITIGATION (not a closure)"); one additional bypass worth
recording in the code comment: the guard **disarms with a WARN when the
on-disk manifest is absent or unreadable**, so deleting the manifest file
before a build achieves what C3's delete-row achieves — visible in git, like
C3, but the disarm pathway should be listed alongside it.

## 5. The five questions

**Q1 — is P1 safe on one probe?** No, but see § 3.1 — restate it on the full
incidental evidence and it is much safer. The second deliberate probe should
target the one layer where the trial actually found a defect:
**`results/passes-manifest.json`** (10 passes mislabelled). Probe: sample
~30 passes stratified across runs/eras, re-derive every manifest field from
the underlying `*.meta.json` at source, report mismatch rate. $0, sapphire,
an afternoon.

**Q2 — does P2 survive spot-checking?** As a queue of fixes, yes; as a
mechanism claim at "~80 %", no (§ 3.2). Re-scope to six single-source families
and re-state.

**Q3 — machinery proportionate?** Mildly over-built, as the brief suspects.
The sunk work is sound and reusable; the error was sequencing (machinery
before record), which Shawn already corrected by redirect. Spend nothing more
on machinery except the commitment ledger — the one piece that pays into the
paper (turns the 46-item register into a standing build check and closes C3)
— and only after the correction pass is done.

**Q4 — what probe have we not run?** Three, in value order:

1. **The numbers-vs-artefacts sweep of paper-bound prose.** Every audit so far
   checked claims *about the registration* or *about execution*. Nobody has
   swept the quantitative claims in the documents the paper will be drafted
   from (`docs/paper/results-outline.md`, `results-draft.md`,
   `key-findings-summary`, the findings docs) against the manifests and eval
   JSONs they cite. The project's history says this is where the bodies are:
   the token-load audit found **all four** cost manifests wrong; the corpus
   description survived four documentation passes and fell to GeoTIFF headers.
   The attribution error rate in prose was ~3 % of candidates; there is no
   reason to believe the *numerical* error rate in prose is zero, and no probe
   has measured it.
2. **The erratum-coverage enumeration (inverse census).** The sweep verified
   existing errata against the registration; the unexecuted register verified
   registration → execution. The unswept direction is **execution → errata**:
   enumerate every factor level and protocol choice present in
   `results/run-conditions.json` that the registration does not license, and
   check each has an erratum. The two known gaps (H2-C omission, systematic
   HIGH-thinking on Flash) were found *incidentally*; this closes the class by
   construction, from the manifest, $0.
3. **The passes-manifest field-level probe** (Q1 above).

**Q5 — "detectable, not impossible"?** "Detectable" is the correct claim for
the guard as built — and the paper should go further and **claim nothing about
the machinery at all**. All 18 existing predictions predate it and cannot be
retro-validated; a methods paragraph advertising a guard that does not protect
the study's own predictions invites exactly the review it was meant to
forestall. The machinery belongs in a lessons-learned/future-work sentence at
most. The paper's integrity claim is the corrected record, the errata, and
this audit — which is a *strong* story: preregistration lodged and frozen
(§ 1), deviations enumerated and errata'd, and the strongest results
(PV headline, H7, H12) are *falsifications* of registered predictions, the
best kind of preregistered finding.

## 6. Consequences for the correction queue (§ 7a)

1. Item 1's arithmetic conflates the sweep total with the four-source cascade:
   the four substitution sources cover **~45 sites**; reaching ~130 requires
   adding the first-N boilerplate family (U2, 42 sites, one sed-able sentence)
   and the D-S family (18 sites). Plan the pass as **six families + residue**.
2. Add to item 2's small-corrections list: the lodgement timestamp
   (`execution-checklist.md:49,61` and its quotations — Finding 2); an erratum
   for the posted file's stale v4.6 header (Finding 4); the OSF citation
   pointing at `updated/` (Finding 3).
3. The H7 erratum should include the corpus-scope fact from
   `working-notes.md:21695`: under the registered 60-tile corpus the trigger
   never fired. It converts "fired, judged uninformative" into "fired only on
   an unregistered corpus, and is noise there" — materially stronger.
4. Publish the trigger census as `reports/d17-inventory/trigger-census.md`
   before any use of P4 (§ 2, C5).

## Changelog

### 2026-07-28 — Original publication

Written by Claude Fable 5 as the independent second opinion Session 119 was
convened for. All verifications performed at source this session; OSF fetch
performed via public API, no credentials used.
