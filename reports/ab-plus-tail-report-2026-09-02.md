# AB+ tail report: 88 sources, complete — corpus build FINISHED

> **Last revised**: 2026-09-03 (overflow appendices added to all 88
> entries; amendments acted on). See [§ Changelog](#changelog).

Companion to `reports/ab-plus-pilot-report-2026-08-30.md` (the first
25 sources). This report covers the remaining 88, run on the
Personal Investigator's (PI's) extra Claude credit across Sessions
146–147 (2026-09-02), with the pilot's amendments applied first.
Manifest (authoritative per-source state):
`outputs/ab-plus/manifests/tail-2026-09-02.json`. Run card:
`planning/ab-plus-run-card-2026-08-30.md` § Tail run.

## Outcome

All 88 tail sources are drafted, deterministically quote-checked,
adversarially verified in fresh context, edited, re-checked, and
rendered to `outputs/ab-plus/*.md` (703 attested quotes, every
one byte-verified against extracted page text at render time and
stamped `claude-opus-5 / 2026-09-02` plus the pipeline revision).
Working files (`_work/`: page text, entries, verdicts, overflow
notes, OCR provenance) stay gitignored per the copyright convention.

**The headline verification statistic held at scale: 0 of 88 entries
passed the fresh-context check without edits.** Every verdict was
PASS-WITH-EDITS; none was FAIL; nothing was fabricated (the
deterministic checker held quotes byte-stable across
703 spans). Across the 88 verdicts the verifiers
scored 753 points: 564 SUPPORTED, 186 OVERREACH,
2 UNSUPPORTED, and one filed NOT CHECKABLE outside the enum (both UNSUPPORTED points — an inverted
two-baseline arithmetic in jiang_many-shot_2024 and a hook note that
contradicted the source's §3 in agarwal_many-shot_2024 — were
corrected at edit). Verifiers proposed 751 edits in total
(median 8 per entry, range 3–18);
editors applied nearly all, adapting for the 300–500 word band and
declining only where the source contradicted the verdict or the edit
rested on external knowledge. Summaries landed at a median of
498 words (range 437–500); 87 of
88 entries carry the full seven key points and every entry carries a
framing hook.

The pilot's finding therefore generalises: byte-perfect quoting
screens fabrication and nothing else. The interpretive layer needs
its own independent check, and at 113 sources it has never once
been redundant.

## Catch taxonomy (what the verifier layer caught, tail additions)

The pilot's five classes (hedge inflation, salience drift, dropped
denominators, wrong-direction repairs, bidirectional correction) all
recurred. The tail added, or sharpened, these:

1. **Frequency inflation** — the source's "sometimes" reported as
   "often"; "some" as "most"; "can" as "does" (liu_paths_2020's
   HARKing point; hekler_agile_2016's "displaces"). The most common
   single catch in the preregistration cluster.
2. **Self-flattering direction** — errors that ran toward the citing
   paper's own thesis. fafchamps_using_2017 "excluded outright" what
   the source calls "not yet implementable" (flattering its
   no-working-mechanism verdict); ross_introducing_2022 (co-authored
   by the PI) took the permissive half of an abduction argument and
   rejected the restrictive half resting on the same premise;
   ofosu_pre-analysis_2023 softened a five-hypothesis threshold to
   "the high-count tail". Verifiers were briefed to hunt this
   direction and found it repeatedly.
3. **Role-split findings generalised** — pu_designing_2019's
   "registrations mostly do not get checked" when the source says
   authors check thoroughly and everyone else checks thinly; gamble's
   consensus Table items bundled with Discussion "should"s under one
   "required".
4. **Definite-article ranking** — "the canonical", "the cleanest",
   "the strongest" where the source's own Related Work names closer
   neighbours (liu_paths_2020; lin_standard_2016). Editors either
   dropped the article or marked the ranking as the citing paper's.
5. **Source voice versus our voice** — a transfer argument (threshold
   sweeps as sanctioned exploration; cell scrambling as a blinding
   retrofit; the Q18 knowledge-of-data line placing our pilot exposure
   on the permitted side) stated as if the source made it. The fix is
   a marker, not a deletion.
6. **Drafter counting errors** — srivastava's "decision independence"
   count (33→37) and interim-registration count (5→6); jiang's
   inverted baseline arithmetic; a page-attribution slip in
   fafchamps. Verifiers recomputed every figure-bar sum and
   denominator they could (ofosu's Figure 2 panel A sums to 169, not
   the stated full sample of 195; liu's Table 1 shares reproduce to
   the integer).
7. **Bidirectional correction, again** — editors declined verdict
   edits that traded one unverified claim for another (nosek: "a
   retrospectively assembled errata log" contradicted by the errata
   file's per-entry date and commit fields; hekler: a verifier's
   proposed quote failed the checker on a de-hyphenation join and was
   paraphrased instead; ioannidis: the verdict quoted
   "pre-registration" where the cache reads "preregistration").
8. **Dispatch errors caught downstream** — the orchestrator's
   one-line cluster description mis-described pu_designing_2019 as a
   Center for Open Science working paper (it is a University of
   Michigan preprint deposited on OSF); the drafter corrected it and
   the editor confirmed no field carried the misattribution.

## New cache-defect classes (beyond the pilot's three OCR signatures)

The pilot's amendment 1 became `cli.py gate`, which caught the two
Wiley watermark-only PDFs (trier_using_2019,
gerasimova_argumentbased_2024; 10 and 21 byte-identical pages) that
a zero-length check would have passed; both were OCR-rebuilt with
provenance notes and drafted last, under the visual-attestation
controls. Beyond that, the tail surfaced defect classes the gate does
not see, because the page text is present and plausible:

1. **Caption-only tables** (IEEE Access: canAutomaticDetectionRoad2021,
   uhlAutomatedExtractionHuman2020) — captions extract, bodies do
   not. A drafter quoting "Table 3" numbers from prose is safe; one
   inferring them is not. Verifiers rendered the pages.
2. **Neighbouring-article contamination** — first or last pages
   carrying the end of the previous article or the start of the next
   (nosek_preregistration_2019 in TICS; dwork_reusable_2015 in
   Science; maccoun_blind_2015 in Nature, whose page 2 opens an
   unrelated Comment on the same theme). The checker would pass a
   verbatim quote from the wrong article. Editors re-tested every
   embedded quotation against a Nosek-only or Dwork-only
   reconstruction.
3. **Cover-sheet page offset** (UvA-DARE deposits: cruwell,
   sarafoglou ×2) — `page_index 0` is a repository cover sheet, so the
   usual `page_index N = printed p.(N+1)` mapping is off by one; and
   **appendix renumbering** (strobl_simp2l_2026: three appendices each
   restart at p.1) — both recorded in the entries' `section` fields
   and overflow notes.
4. **Unreliable `section` field** — the extractor records the last
   heading on a page, not the governing one, and degrades to
   reference-list fragments (vaccaro_preregistration_2026). Drafters
   assigned sections by reading body text.
5. **Glyph and join corruptions** — curly quotes as `B…^`, broken
   ligatures ("specifi c"), mean/SD concatenation ("87.226.03"),
   τ→"t", colon-for-decimal ("38:9%"), and de-hyphenation joins with
   the hyphen dropped and a space left ("preregistra tion") or
   consumed ("clinicaltrial", "opensource"). Quotes carry them
   verbatim and paraphrases flag them; editors learned to test a
   proposed quote against the normaliser before adopting it.
6. **Figure-label number runs** — bar values and axis labels
   flattened into reading-order runs beside prose (thomas, ofosu,
   sarafoglou). Usable for reconciliation sums, unsafe as citations
   without legend mapping.
7. **Source-level contradictions** the cache faithfully preserves
   (sarafoglou_comparing_2023: which condition the four merged teams
   joined, p.4 vs p.12; ofosu's Appendix 120 vs 110 authors; gamble's
   Abstract vs Methods Delphi denominators). Entries record, never
   resolve.

## What the corpus now attests for the paper (selection, tail)

The preregistration and open-science cluster (30 sources) now
supplies the D.9 material with page-anchored quotes:

- **Term occupancy for the D.9 naming ruling**: Srivastava 2018 uses
  "adaptive preregistration" four times as a lowercase common noun,
  never defined or claimed; "registered flexibility" occurs nowhere
  in the corpus. Nosek 2018 names four data-dependent strategies
  including "sequential preregistration"; Crüwell 2021 §6.2 registers
  a model evaluation "for each of the models"; Ioannidis 2022 offers
  "small bites of pre-registration" alongside, not instead of,
  registering the space of approaches; Lakens 2024 places the novelty
  boundary at machine-readable hypothesis tests; Gould 2026 and
  Vaccaro 2026 are the two occupants of the staged/adaptive cell.
- **The automation cell is empty across the cluster**: `automat*`
  returns zero or proposal-only hits in every source (Pu 2019's
  "declaration of match ... could even be partially or fully
  automated" is the closest, unbuilt). Thomas 2026 cites and
  dismisses an LLM checklist assistant as self-report — the objection
  the LLM-support claim must answer.
- **Measured base rates for deviation reporting**: Ofosu 2023 —
  deviation noted in 1 of 14 cases; 18% tested unregistered
  hypotheses and 82% of those were silent; median 25% of registered
  hypotheses omitted. Sarafoglou 2023 — self-report vs independent
  coding ICC .43, and the authors judge self-report the more accurate
  record. Willroth 2024/2022 and van den Akker 2021 supply the
  taxonomy and the secondary-data template.
- **Rival remedies with evidence**: analysis blinding halved
  deviations (38% vs 20% model estimates, BF 71.40) but saved no time
  (BF 13.19 for the null); Dwork 2015's reusable holdout scopes to
  bounded-mean statistics, which F1 and MCC are not; MacCoun 2015 is
  advocacy without efficacy evidence.
- **Disciplinary baselines**: Ross 2022's four non-teaching OSF hits
  for "archaeology" out of 304,904 registrations (19 March 2020,
  keyword search) — a figure that must travel with all four
  conditions; Sarafoglou 2022's 88%/83% recommend/reuse among the
  experienced versus 45%/7% among the inexperienced.
- **ML-side standards the apparatus can be audited against**: Thomas
  2026 Table 1 (prompts and decoding as conditions, output-validity
  rules, eligible-model set, abandonment rule); Vaccaro 2026 Table 1
  (inference budget, aggregation method, and multiple comparisons as
  named p-hacking surfaces); Strobl 2026's "oracle conditions" as a
  disclosure category and its across-DGP pooling rule.

## Pipeline amendments for a future run

1. **Gate heuristics for the new classes**: flag pages where a table
   caption is present but the following block has fewer than N
   digits (caption-only tables); flag first/last pages whose text
   contains a second title-and-author block or a DOI other than the
   source's (neighbouring-article contamination); flag `page_index 0`
   pages matching repository cover-sheet signatures (UvA-DARE,
   SocArXiv) and record the offset in the provenance note.
2. **Enforce the verdict enum**: one verifier scored a point
   `NOT CHECKABLE` in `per_point` rather than in a note
   (chen_can_2025); the renderer tolerated it. Validate
   `per_point[].verdict ∈ {SUPPORTED, OVERREACH, UNSUPPORTED}` at
   render and reject otherwise.
3. **Enforce the word band at check time**: two entries left the
   band (a pilot exemplar at 620 words; a tail draft at 548 before
   edit). `validate_entry` should warn outside 300–500.
4. **Overflow notes deserve a committed home** (DONE 2026-09-03: sidecar
   plus paraphrase-only appendix, all 88 sources): nearly every tail
   drafter wrote one, and editors moved verified material there to
   hold the band. They are the drafter's evidence base for the
   summary and carry the cache-defect register per source. They
   contain verbatim source spans, so they belong with `_work/`
   (gitignored) unless trimmed to paraphrase; a per-source
   `## Overflow` appendix rendered from paraphrase-only notes is the
   candidate.
5. **Dispatch descriptions are a source of error**: keep the
   orchestrator's cluster line to the citekey, the cluster, and the
   cache notes; do not characterise the source (see pu_designing_2019).
6. **Visual attestation is expensive but worked**: the two OCR-rebuilt
   sources were drafted under the provenance-note controls (render
   page, read the span off the image) and passed verification with
   8/8 quotes each after two independent visual attestations (drafter and verifier), the editor adding a third; no transcription error was found in either.

## Usage

The tail ran at the harness cap of 20 concurrent Opus-tier agents
with rolling refill (an editor for every verdict, a verifier for
every draft, drafters from the queue) across two sessions with one
graceful pause at the 5-hour usage limit (S146; resumed S147 after
a manifest-versus-disk reconcile that matched exactly). Agent counts:
88 drafters, 88 verifiers, 88 editors, plus re-launches after cap
refusals — about 264 (88 per stage; the two cap-refused launches left no transcript) Opus-tier runs. Reported per-agent
usage where captured in notifications: drafters ~120–155k tokens,
verifiers ~95–125k, editors ~85–135k, so ≈ 0.3–0.4M reported tokens
per source across the three stages, ≈ 30–40M for the tail
(the pilot measured ≈ 360k per source; the harness's per-task output
files hold only final messages, so this is an estimate from the
notification telemetry, not a meter reading). Orchestration overhead
in the main session is additional. Wall clock: drafters 6–13 min,
verifiers 5–8 min, editors 3.5–11 min.

## Status

**COMPLETE.** Corpus: 113 deliverables in `outputs/ab-plus/`
(25 pilot + 88 tail), all model-stamped. Next: the PI's read of the
preregistration cluster feeds D.9 directly; the run card carries the
final numbers; the beacon (`planning/paper-writeup-continuity.md`
§ STATE AFTER S147) records the close.

## Changelog

### 2026-09-03 (later) — Overflow appendices added to all 88 tail entries

Trigger: PI approval of the sidecar conversion batch. Each free-form
note was structured by a fresh Opus-tier agent into
`_work/<citekey>.overflow.json` (918 items across 88 sidecars, median
11.5, 44 at the twelve-item cap); every span verified at render and
none was withheld. The public entries gained a paraphrase-only
`## Overflow` section with page anchors. Corrections the structurers
surfaced against the notes and sources were appended to the `.md`
notes as orchestrator-recorded sections. Observed in use: the
caption-only numeric gate rule fired on 14 caches and every flag a
structurer checked on the rendered page was benign; trailing-text
flags were appendices or author biographies in every checked case bar
MacCoun 2015. No numbers in the body changed. Run-card changelog
carries the full entry.

### 2026-09-03 — Amendments 1–4 acted on (PI rulings)

Trigger: the PI's review of this report. Amendment 1 (gate heuristics)
landed as `gate.content_notes` — cover-sheet, author-manuscript,
neighbour-contamination, trailing-text, caption-only-table,
sections-empty — calibrated on all 113 caches (79 PASS / 34 WARN /
0 FAIL); the caption-only class proved undetectable from text
statistics, so the publisher signature is the trigger. Amendment 2
(verdict enum) enforced at render with NOT CHECKABLE admitted as a
fourth value requiring a note; 51 entries re-rendered with named
per-point labels. Amendment 3 (word band) is an advisory warning, per
the PI's ruling that length limits are targets, not gates. Amendment 4
(overflow home) decided: complete sidecar in `_work/`, paraphrase-only
appendix in the public entry; conversion of the 88 free-form notes
awaits PI approval of the agent batch. No numbers in the body changed.
Commit `5a871e5d8` (pipeline) and the re-render commit that follows it.

### 2026-09-02 — Original publication

Written at tail completion (S147), from the manifest, the verdict
JSONs, and the agent notifications. Commit: the tail-complete series ending `bcf2e4692` (this file lands in the next commit; see `git log -- reports/ab-plus-tail-report-2026-09-02.md`).
