# Documentation foundation, Batch 1 items 1–2 — deltas (2026-09-13)

> **Last revised**: 2026-09-13 (original publication; Session 153, Batch 1 items
> 1 and 2). See [§ Changelog](#changelog) for revision history.

What items 1 and 2 of
`planning/documentation-foundation-checklist-2026-09-13.md` changed, what they
deliberately did not, and where every claim below can be re-checked. Zero API
spend; all compute local and sub-minute (nothing in this batch meets the
sapphire threshold).

## 1. Headline

| Measure | Before | After | Anchor |
|---|---|---|---|
| Run directories with a `post_run_report.md` | 2 of 41 | **41 of 41** | `find outputs -name post_run_report.md \| wc -l` |
| — of those, generated projections | 0 | **39** | `python3 scripts/generate_run_reports.py --check` |
| — of those, hand-authored | 2 | 2 | `scripts/generate_run_reports.py`, `HAND_AUTHORED` |
| `verify_run_conditions.py` verdicts | 22 pass / 19 partial / 0 fail | **38 pass / 3 partial / 0 fail** | `python3 scripts/verify_run_conditions.py` |
| Open WARNs across all runs | 221 | **12** | same command, `--json` |
| Registered runs | 41 | 41 | `results/run-registry.json` |
| Registered conditions | 593 | 593 | `results/conditions-manifest.json` |
| Metrics changed | — | **none** | § 5 |

The checklist card said "34 missing of 36". The registry actually holds **41**
runs at **41 distinct** directory paths, all of which exist and are tracked in
this checkout, and **2** carried a report — so the gap was **39**, not 34 of 36.
No run's outputs turned out to be sapphire-only, so no report needed the
"untracked on sapphire" treatment the brief provided for.

## 2. Item 1 — post-run reports

### 2.1 What was written

39 generated `outputs/<run>/post_run_report.md`, emitted by the new
`scripts/generate_run_reports.py` v1.1.0 at source commit `e88fd5bfa`. Ten
sections each: identity and registration; scope and evaluation frame; passes on
file (model used and requested, modality, thinking level, temperature, status,
tiles, retries — proposer and verifier tables kept apart on the manifest's own
`n_tiles_null_reason` marker, the E72/GAP-8 distinction); recorded token load
and cost; registered conditions with F1@20 m, F1@50 m and tile MCC; the
analyses that read the run; findings documents; protocol errata; in-directory
documents and registered pools; provenance.

Sizes run from 9 KB (`h7-escalation-2026-08-28`) to 265 KB
(`pv-diag-384`, whose 185 conditions carry 138 distinct caveats). Caveats,
scope overrides and waived evaluations are grouped by identical text so a
qualification shared by a family of sibling cells prints once with every cell
named; that alone cut the pv-diag-384 report from 409 KB to 265 KB without
eliding anything.

### 2.2 Why generated rather than hand-authored

The brief offered both routes and preferred the generated one; the 2026-09-11 PI
ruling (`docs/methodology/output-directory-standard.md` § "Documents in Revision
Policy Scope") makes a generated projection exempt from banner-and-changelog and
subject instead to a GENERATED banner, a source-commit stamp and a tested
`--check` drift guard. Taken here for a reason beyond convenience: 39 hand
changelogs would each go stale at the next manifest rebuild, and the question
they exist to answer — "is this current?" — is answered strictly better by
`tests/test_generate_run_reports.py::test_no_drift_in_committed_reports`.

The standard's scope table and its § "generated projections" paragraph were
updated to say so, and the standard's own Changelog carries the before→after.

**The guard caught a bug in itself, which is the best evidence it works.**
`--check` blanks the source-commit stamp before comparing, because regenerating at
a new HEAD must not read as drift when the projection is unchanged. The first
`_neutralise` blanked the banner's "source commit `<hash>`" but missed § 10's table
cell, "| Source commit | `<hash>` |", where the pipe and spaces break the
contiguous *commit-then-backtick* match the regex needed. That is not cosmetic: the
stamp is
written by the commit that
LANDS the reports, so from that moment HEAD has moved past it and an
un-neutralised site never matches again. The guard would have fired on every run,
for every report, for ever — reporting drift that did not exist and masking drift
that did. It surfaced the first time the full tier-1 suite ran after the landing
commit (`c4edf1328`), reporting all 39 reports stale while `--check` passed by hand
minutes earlier. Fixed by neutralising both sites, with
`test_drift_check_ignores_the_commit_stamp_everywhere` asserting each site is
blanked and that a real content change is still visible. The reports themselves
were not regenerated: their stamps correctly name the commit they were projected
at, and churning 39 files for one token would have been the wrong fix.

### 2.3 Anti-confabulation, and the three places it bit

Every figure in a report is read from a file named in that report's § 10. Three
cases where naive projection would have published something false:

1. **An unscored buffer is not a zero.** `h13`'s six conditions were scored at
   the 20 m buffer **alone** (`results/conditions-manifest.json`, any `h13` row's
   `metrics.per_buffer`). The F1@50 m column therefore reads *not supplied*, and
   every report additionally states which buffer sets are on file and for how
   many conditions, so a reader can distinguish an absent metric from a measured
   zero. Pinned by
   `test_absent_metric_is_not_supplied_not_zero`.
2. **The recorded cost is not the run's cost — and neither are the token
   totals.** `cost_usd` in the passes manifest is each pass meta's own
   `cost_estimate.total_cost_usd` (`scripts/generate_post_run_report.py:568,672`),
   and `reports/token-load-audit-2026-06-12.md` § 1 established that those
   self-reported figures price at STANDARD rates although the audited runs ran at
   `--service-tier flex` (half price) and omit thinking tokens although Gemini
   bills thinking at the output rate. The reports print the sum labelled
   "recorded", with that finding attached, and never as a total to cite. Pinned by
   `test_cost_is_labelled_recorded_not_audited`.

   **The sharper half of this was caught only on review of the first draft.** The
   manifest takes a pass's `tokens` from the meta's `usage_stats` block
   (`generate_post_run_report.py:567,671` → `_tokens_from_usage`), and the audit
   recomputed from `per_item_metadata` that the 2026-05-02/03 recovery merge
   **doubled that very block** on `55maps-text-high-generalisation` (factors
   2.003–2.016, § 3.2) and `55maps-image-generalisation` (§ 3.4, whose
   `cost_manifest.json` is 3.0× because the generator then added the pre-recovery
   backups on top again). Generator v1.0.0 printed those totals as plain fact —
   figures wrong by 2× in a known direction, which is precisely what the
   anti-confabulation contract forbids. v1.1.0 added a per-run audit block
   (`TOKEN_AUDIT`) carrying each run's `usage_stats` verdict, its manifest verdict,
   the trustworthy source, and the audited clean per-pass figures transcribed from
   the audit's § 3.1–3.5, for the five runs the audit covers. It deliberately
   derives **no** run total: the audit's pass count and the manifest's need not
   agree (text-high has 6 pass rows against the audit's 5), so multiplying would
   manufacture a figure no file carries. Pinned by
   `test_double_counted_token_totals_are_disclosed`.
3. **A mention is not an audit.** A run is listed against one of the four spend
   reports when its run_id or directory path appears in that report's text —
   `token-load-audit-2026-06-12` names 7 runs, `r7-gaps-deltas-2026-09-11` 5,
   `k-ladder-phase2-deltas-2026-09-12` 3, `billing-reconciliation-2026-09-11` 2.
   The wording says a mention is a pointer to where audited figures live. A run
   no audit names says so explicitly rather than leaving the section silent.
   Pinned by `test_audit_citation_only_where_the_report_names_the_run`.

Errata are likewise split into **registered** (named in the `deviations` field of
an analysis that reads the run) and **mention-only** (the entry's text names the
run), each labelled, so neither borrows the other's authority.

### 2.4 The two hand-authored reports, and a correction they surfaced

`55maps-image-generalisation` and `55maps-text-min-generalisation` are skipped by
the generator, not overwritten: they carry Dawid-Skene annotator-incompleteness
corrections, the paired HIGH-vs-MIN comparison that is the text-MIN run's
scientific question, per-map cost extrema, timelines and recovery narratives —
none of it re-derivable from the manifests. A projection would have destroyed
irreplaceable analysis. `test_hand_authored_reports_are_not_projections` is the
tripwire against a future change dropping them from the skip table.

They were given the Revision-Policy banner and a Changelog instead. Doing so
**corrected a claim in the standard**: its scope table read "2 compliant; 15
missing entirely", but neither document carried a banner or a Changelog before
today, so that cell described *existence*, not banner compliance. The cell is
restated and the standard's Changelog records the correction.

## 3. Item 2 — the 19 partial runs

### 3.1 WARNs cleared, by class

| Class | Before | Cleared how | After |
|---|---:|---|---:|
| `pool-unresolved` | 115 | `source_run` annotation on 115 conditions across 7 runs | 0 |
| `geojson-missing` | 79 | verifier instrument correction (directory-valued detections) | 0 |
| `unclaimed-eval` | 13 | 13 `_ignored_evals` waivers with reasons | 0 |
| `pool-dir-not-found` | 2 | verifier instrument correction (materialised pool path) | 0 |
| `pinned-vintage` | 9 | **left standing by design** — § 3.4 | 9 |
| `n-passes-over` | 3 | **left standing by design** — § 3.4 | 3 |
| **Total** | **221** | | **12** |

### 3.2 Two instrument corrections (commit `f4fd90c71`)

81 of the 221 WARNs were verifier false positives, not findings, and they alone
accounted for eleven of the nineteen partial runs.

**`geojson-missing` (79).** `fc is None` had two causes the single WARN
conflated. A condition whose `detections` names a **directory** is an aggregated
multi-pass cell: the evaluation was pointed at the directory and
`summary.n_detections` is the post-aggregation count. All 79 affected rows were
checked individually — every one is a directory that **exists**, every one of
their evaluations records exactly one input (the directory itself), and 54 carry
no `n_detections` at all, so the comparison the WARN claimed to be skipping was
vacuous either way. Saying "detections missing/unreadable" about 79 present
directories trained the reader to discount the check. The branch now checks the
shape's real failure mode instead — a cell whose directory holds no geojson has
lost its inputs (`detections-dir-empty`) — and `geojson-missing` is reserved for
a genuinely absent path, with a regression test for that half.

**`pool-dir-not-found` (2).** A pool whose registered `path` resolves to a FILE
is a materialised pool: `flash35-pv-2x2`'s `f3-min-text-1of10` is
`consensus/f3-min-text-1of10-with-passes.geojson`, the cross-run pv-diag-384
text-n10 minimal lineage merged into one committed geojson
(`scripts/author_second_wave_registration.py` `_flags`). Pass resolution has
nothing to count, but the artefact is present, which "not found" denied. The WARN
is now reserved for an absent path.

Five tier-1 tests pin both corrections and both regression guards.

### 3.3 Annotations (commit `e88fd5bfa`)

`scripts/annotate_partial_run_warns.py` applied, per run:

| Run | `source_run` on | Waivers | Pool ownership, and its anchor |
|---|---:|---:|---|
| `pv-diag-384` | 66 | — | itself, across 25 distinct pool names: 10 N1 baselines naming their own pool by relative path-string (`pool/temp`, whose registered key is `pool-temp`); 13 verifier-stage selection bands that are real directories under `outputs/h11/pv-diag-384/verified/` (one, `pro-high-image-1of5`, under the sweep's `-pro-verifier` spelling); and 2 top-level single-pass baseline pool directories (`pro-medium-{image,text}-baseline`) |
| `proposer-verifier-384` | 16 | — | itself: one un-numbered proposer pass at `proposer/detections-detect_brief-text-3-flash-2026-03-15.geojson`, so `proposer_pools` is empty |
| `grid-2026-08-18` | 15 | — | itself: `brief-text` is the PROMPT; passes are keyed by grid geometry (`g384_ov048`, `g384_ov192`, `g512_ov064`, `g512_ov256`, each with `run_*`) |
| `retest-phase3c` | 9 | — | itself: nine diversity groupings over the run's own registered pass-variant pools; consensus outputs under `diversity-consensus/track{1-image,2-text}/{A..E}` |
| `h13` | 6 | — | itself: `brief-text` is the PROMPT; per-arm passes at `scoring/{common,native}/arm{A,B,C}/run_{1..3}` |
| `pv-diag-256` | 2 | 2 | itself: proposer passes never materialised as `run_*` dirs (only `consensus/`), as the run's own `_note` already stated |
| `proposer-verifier-512` | 1 | — | itself: one un-numbered pass at `proposer/detections.geojson` |
| `e47-propose-brief` | — | 5 | — |
| `n1-outstanding-384` | — | 6 | — |
| **Total** | **115** | **13** | |

**`source_run` is not a new convention.** `pv-diag-384` already carried
`source_run: "pv-diag-384"` on `verified-adv-text-consensus-16of30` for exactly
this reason; three run `_note`s (`pv-diag-256`, `pv-diag-384`,
`retest-phase3c`) already adjudicated the class as "benign pool-unresolved" in
prose; and `scripts/author_verifier_robustness_registration.py` registers the
same band names (`flash-high-text-1of5`, `text-1of5`, …) with
`source_run: "pv-diag-384"` / `"pv-diag-256"` from the *other* side, which
settles pool ownership independently of this pass. The annotation moved an
adjudication that already existed in prose the verifier cannot read into a field
it can. Each entry carries its filesystem or authoring-script anchor in
`POOL_SOURCE_RUNS`, and a `_source_run_basis` string on the condition itself.

**The 13 waivers**, each written after opening the evaluation and reading its
`_metadata.input_files.detections`:

- **11 superseded pre-recovery scorings** (`e47-propose-brief` 5,
  `n1-outstanding-384` 6). Each `results/rescore-2026-05-31/…/consensus_t<k>/`
  evaluation scored the same consensus geojson that the registered condition now
  scores at `results/recovery-reeval-2026-09-08/…`, after the E71 dead-tile
  recovery (`99ae28ec4`) rewrote the file. Kept as the pre-recovery record under
  ruling 3a (PI, 2026-09-07); not second conditions.
- **2 uplift-supplement pairing inputs** (`pv-diag-256`). Both belong to the
  cross-run `verifier-robustness::verified-256-{union-t0-0,ge3of5-t0-3}-n5`
  conditions, whose proposer pool is pv-diag-256, and both score
  `outputs/h11/pv-diag-256/consensus/text-5of5.geojson`. They surface under
  pv-diag-256 only because the detections live there — exactly the cross-run
  limitation `verify_completeness`'s docstring describes. Same waiver class as
  the existing `55maps-text-min-n10-uplift` pairing entries (PI ruling
  2026-09-07).

### 3.4 WARNs left standing, and what clearing them would take

Three runs remain PARTIAL on 12 WARNs. **None is an oversight; each is a
disclosure the project has already settled, and clearing it would delete
information.**

| Run | WARNs | Why it stays |
|---|---:|---|
| `55maps-text-min-n10-uplift` | 3 `n-passes-over` | The pool is MIXED-PROVENANCE: passes 1–5 are the `55maps-text-min-generalisation` deployment passes, 6–10 are this run's. The run's own `_note` in `results/run-conditions.json` calls the WARN "the honest by-design signal, per the S106 settled position". `source_run` cannot clear it — the pool IS registered, so the check runs in the `elif pool in proposer_pools` arm. |
| `e47-propose-brief` | 1 `pinned-vintage` | Raised only when the pin **checks out**: the evaluation declares it scored the vintage-frozen copy at the commit the register pins (E82/D40; ruling 3a, PI 2026-09-07). The verifier docstring calls it "a disclosed WARN, not a wrong-source ERROR". |
| `n1-outstanding-384` | 8 `pinned-vintage` | As above, on the eight pinned Pro rows. |

**What clearing them would take** — a PI decision, not an annotation. Both
classes are *satisfied checks* that the verdict model has nowhere to put: it has
`discrepancies` and nothing else, so a passing disclosure degrades a run to
PARTIAL exactly as an open question does. The fix is a verdict-model change —
a third `disclosures` list beside `discrepancies`, populated by `pinned-vintage`
and by an `n-passes-over` that a `_note` or an explicit
`mixed_provenance_pool` field declares, with PASS defined over `discrepancies`
alone. That is a change to what a signature attests, so it is not in this batch's
remit. Recommended, and flagged here rather than done.

`tests/test_verify_run_conditions.py::test_partial_runs_are_exactly_the_three_by_design_disclosures`
pins the set, so a new PARTIAL run is a real finding rather than noise.

## 4. Manifests regenerated

`python3 scripts/generate_post_run_report.py --all --write` → 41 runs, 593
conditions, 1,317 passes, 67 analyses, ALL VALID against the schemas.

Every `runs`, `conditions` and `passes` row is **identical** to its predecessor
once extraction timestamps are ignored (row-by-row comparison against the
pre-change files; 41 → 41, 593 → 593, 1,317 → 1,317). The annotations are
additive fields on the decomposition INPUT; they change no extracted value.

One unrelated catch-up landed with the rebuild, and is not from this batch:
`results/analyses-manifest.json` picked up the `k-ladder-2026-09-12` row's signed
`outcome` text from `results/run-analyses.json`, which was committed in
`76a0cb96e` **after** the manifest's last build (`c2060da40`). The committed
manifest was one signature stale; the rebuild is the correct output.

## 5. What did NOT change

- **No metric, evaluation, detection, threshold or operating point.** § 4 is the
  row-by-row proof.
- **No condition was added, removed or relabelled.** 593 before and after.
- **No board, leaderboard, findings document or signature.** Nothing under
  `results/leaderboard/`, `results/**/findings.md` or any signed analysis row was
  touched.
- **No run's registry entry, scope, corpus or `gt_reference`.**
- **The 2026-09-11 generated-projections ruling** — this batch applies it; it
  does not amend it.
- **The two hand-authored reports' bodies.** Banner and Changelog only, plus one
  pre-existing MD032 fixed on touch (a wrapped line beginning `+ 585 VLM-only.`
  that markdownlint read as a list item); no figure or sentence altered.
- **`results/uplift-supplement/verifier-pairing-*`** was deliberately NOT
  regenerated. A test rebuild differs from the committed artefacts by one row —
  `stride-55map-2026-08-25::g384-ov192-55map-n5-verified37-oracle-p0.96-k5-r2-gt`
  — which was registered in `c2060da40`, after the artefacts' last regeneration
  in `3c5de3f23`. That is pre-existing drift from a run this batch never touched,
  and those artefacts belong to checklist item 10; regenerating them here would
  move a document a PI signature attaches to. Flagged for item 10.
- **The `experiment_intent.md` (139), `evaluation.md` (11) and
  `pre_launch_audit.md` (1) censuses** in the standard's scope table stay as
  dated 2026-05-26 figures. They were not re-counted in this pass and are not
  restated as current.

## 6. Reproduce

```bash
python3 scripts/verify_run_conditions.py                  # 38 pass / 3 partial / 0 fail
python3 scripts/generate_run_reports.py --check            # 39 reports up to date
python3 scripts/generate_post_run_report.py --all          # ALL VALID
python3 -m pytest tests/test_generate_run_reports.py \
                 tests/test_verify_run_conditions.py -m tier1 -q
```

## Changelog

### 2026-09-13 — Original publication (Session 153)

Written with Batch 1 items 1 and 2 of
`planning/documentation-foundation-checklist-2026-09-13.md`. Landed across five
commits on `worktree-agent-ac61dfb2fc08e0949`: `f4fd90c71` (verifier instrument
corrections), `e88fd5bfa` (annotations and manifest rebuild), `c4edf1328` (the 39
generated reports, the two banners and the standard's scope-table update),
`cca28cc5c` (the token double-count disclosure, this report and the checklist
tick), `840e0d401` (the drift guard's own commit-stamp bug).
