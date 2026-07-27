# D17 — Errata census (E1–E57)

**Source**: `docs/methodology/preregistration/protocol-errata.md` (1,851 lines).

**Entry count**: **exactly 57**. Counted programmatically — `grep -c "^### E[0-9]"` returns 57, and
a per-entry parse of the file yields 57 blocks whose declared `Type` fields sum to 57. Not estimated.

**Repository**: `/home/shawn/Code/map-reader-llm` (read-only inspection; no edits made).
**Compiled**: 2026-07-27.

**Anchoring convention**: the `L` column gives the line number of the entry's `### En:` heading in
`protocol-errata.md`. The `Type` column reproduces the entry's own declared `Type` field **verbatim**
— including the five entries whose labels fall outside the document's own three-way scheme.

**The document's declared scheme** (`protocol-errata.md:11-15`):

> - **Correction**: Fix to implementation that brings it into alignment with the preregistered
>   protocol (no protocol change)
> - **Clarification**: Interpretation of an ambiguous point in the preregistration
> - **Deviation**: Substantive change from the preregistered protocol (requires justification)

---

## 1. Counts by classification

| Declared Type (verbatim) | Count |
|---|---:|
| `Correction` | **22** |
| `Deviation` | **18** |
| `Clarification` | **12** |
| `Reversion (restores preregistered value)` | 1 (E47) |
| `Deviation + deferral resolution` | 1 (E52) |
| `Metadata correction (non-destructive)` | 1 (E55) |
| `Methodological clarification (threshold provenance)` | 1 (E56) |
| `Metadata correction (non-destructive) + **billing reconciliation (finding-affecting)**` | 1 (E57) |
| **Total** | **57** |

**Reading for the Methods passage.** The document's own scheme admits three types, but five entries
(E47, E52, E55, E56, E57) use ad-hoc labels. Two of those five are the most interpretively
consequential entries in the whole file (E56, E57). **If the paper reports "N deviations" it must
say which counting rule it used.** Three defensible headline numbers:

- **18** — strict `Deviation` label only.
- **20** — strict `Deviation` + E47 (a reversion *is* a protocol change, back to the registered
  value) + E52 (self-labelled as a deviation with an extra qualifier).
- **22** — the above + E56 and E57, which are labelled as clarification/correction but are
  interpretation-governing (E57 explicitly self-describes as "finding-affecting",
  `protocol-errata.md:1789`).

Recommend **20 in the count, with E56 and E57 discussed in the same passage** under an explicit
"non-deviation entries that nevertheless constrain interpretation" sub-heading. That is honest and
avoids the appearance of hiding E57 behind its "metadata correction" label.

---

## 2. Full table — all 57 entries

Legend for the *Bears on* column: an H-number means the entry names or unambiguously governs that
hypothesis. **`—`** means no clear hypothesis mapping (see §4). **`ALL`** means the entry changes
evaluation, statistics, or infrastructure shared by every hypothesis.

| E | L | Date (as given) | Type (verbatim) | One-line summary | Bears on |
|---|---:|---|---|---|---|
| E1 | 21 | 2026-01-31 | Correction | Stale date in the OSF companion README aligned to prereg v4.7 | — (docs) |
| E2 | 36 | 2026-02-01 | Correction | Five execution fields missing from the Phase 1 library config; added to match §8.9 | — (Phase 1 infra; upstream of the H8/H9 library) |
| E3 | 63 | 2026-02-01 | Correction | Migrated `google-generativeai`→`google-genai` for `ThinkingConfig`; `gemini-3-flash`→`-preview` name resolution | ALL |
| E4 | 80 | 2026-02-01 | Correction | Tile-bounds Y-axis inversion shifted all bounds ~2565 m south, wrecking F1 | ALL |
| E5 | 99 | 2026-02-01 | Correction | Three evaluation bugs: reference path, `source_tiles`/`source_tile`, path in `analyse_study_effects.py` | ALL |
| E6 | 118 | 2026-02-01 | Correction | Pipeline contract validation added (assertions, bounds spot-check, 7 integration tests) to stop silent E4–E5-class failures | ALL |
| E7 | 144 | 2026-02-01 | Correction | Reference scoping moved from `union_all()` to per-tile `sjoin`; buffering moved after scoping | ALL |
| E8 | 173 | 2026-02-02 | Clarification | Hard-example crops cut 128×128 from full GeoTIFFs, not from detection tiles, so the target is always centred | H8 (library); by extension H9, H12 |
| E9 | 201 | 2026-02-02 | Clarification | Centre-pointing sentence added to all 11 detection prompts, uniformly across H5 levels | H5 (+ all prompt-bearing) |
| E10 | 222 | 2026-02-02 | Clarification | 50 m threshold set empirically to separate recognition failures from localisation errors (9 vs 15 of 24 FNs) | H8, H12 (HP pool definition) |
| E11 | 239 | 2026-02-02 | Clarification | Scale-16/Scale-32 capped — HP pool structurally exhausted at 4; preregistered contingency (prereg line 815) activated | H8 (conds 6–7; contrasts S2, S3), H10 |
| E12 | 258 | 2026-02-02 | Clarification | H9-C image diversity runs as HN-rotation only; HP channel frozen at 4 | H9, H10 |
| E13 | 275 | 2026-02-02 | **Deviation** | H12 (HP:HN ratio) deferred to post-H10 — testable ratios would confound ratio with total count | H12 (via H8, H10) |
| E14 | 294 | 2026-02-04 | Clarification | Verbose instruction grew to 779 words, ~80 above the preregistered range (brief:verbose 213:779) | H1 |
| E15 | 311 | 2026-02-04 | Correction | Appendix pass-count references inconsistent (≥3/10 vs ≥3/5); execution used the correct K=5 | — (Phase 1 library construction) |
| E16 | 335 | 2026-02-03 | Clarification | Prompt exclusion language shifted from cartographic names to visual descriptions, uniformly across H5 | H5 (+ all prompt-bearing) |
| E17 | 355 | 2026-02-05 | Correction | Erroneous `passes: 5` multiplier removed from execution plan + five Phase 2 YAMLs (would have been 5× cost) | H3 (§3.8 single-pass rationale); all Phase 2 |
| E18 | 374 | 2026-02-05 | Clarification | Config filenames drop the redundant `_minimal` H5 suffix; unsuffixed config *is* H5=Minimal | H1, H5 (naming only) |
| E19 | 391 | 2026-02-05 | Correction | `validation_bounds.geojson` built from the calibration manifest; only 7/20 tiles overlapped the 60 validation tiles | ALL (sanity-check metrics) |
| E20 | 420 | 2026-02-05 | Clarification | "holdout"→"validation" naming standardised across metadata, scripts, tests | — (naming) |
| E21 | 452 | 2026-02-05 | Correction | Stale `passes: int = 5` parameter removed from `analyse_phase2_results.py`; file globbing fixed | — (analysis infra) |
| E22 | 471 | 2026-02-05 | Correction | Evaluation rewritten from merged-runs to per-run F1 (merging made precision nonsensical at K=10) | ALL (Phase 2 metrics) |
| E23 | 499 | 2026-02-05 | Correction | Three Gemini metadata fields (citation, block reason, prompt safety) captured instead of discarded | — (metadata) |
| E24 | 524 | 2026-02-05 | Correction | `--dry-run` corrupted the checkpoint (3→50 units "completed"); guarded | — (runner infra) |
| E25 | 543 | 2026-02-06 | Correction | **Modality manipulation not implemented** — text-only conditions received all 17 example images; 20 runs invalid, re-run | **H1** |
| E26 | 582 | 2026-02-06 | Correction | Bootstrap CIs systematically deflated (~34%) by reference de-duplication on resampled tiles; 7 functions refactored | ALL (all CIs) |
| E27 | 617 | 2026-02-06 | **Deviation** | Dual-track carry-forward: two M/E levels (brief-text-image, brief-text) carried from Phase 2a instead of one | H1, H4, H5, H7, H8 |
| E28 | 643 | 2026-02-11 | **Deviation** | H5 instruction text trimmed (HN image references removed) and the 3×3 factorial simplified to single-factor OFAT | **H5** |
| E29 | 669 | 2026-02-12 | Correction | `reorder_examples()` `canonical-first` was a no-op; split into `config-default` and true `canonical-first` | H4 |
| E30 | 695 | 2026-02-12 | **Deviation** | Phase 2e tests 4 ordering conditions, not the preregistered 3 (adds `config-default` baseline) | **H4** |
| E31 | 726 | 2026-02-12 | **Deviation** | 4 deterministic T=0.0 units copied from an existing run rather than re-executed (byte-identical at T=0.0) | H4 |
| E32 | 747 | 2026-02-12 | **Deviation** | Phase 3a runs consensus at T=0.3/0.7, not the carry-forward T=0.0 (voting needs run-to-run variation) | **H3** (+ H7 carry-forward) |
| E33 | 768 | 2026-03-12 | Correction | Verifier crops read from tile PNGs not source rasters → truncated edge crops; all Phase 3d PV results re-run | **H2** |
| E34 | 795 | 2026-03-15 | Correction | `thinking_level` not copied into execution units, so `--thinking-level` was silently dropped; fixed pre-collection | H3 (phase3a-replication) |
| E35 | 826 | 2026-03-15 | Correction | Bootstrap matched per-tile while point estimates matched per-map → recall bias (~7 pp at 340 tiles); now per-map | ALL (all CIs) |
| E36 | 878 | 2026-03-17 | **Deviation** | 340-tile production retest replaces the 60-tile holdout; all Phase 2–3 conditions re-run; K cut 10→1–3 | ALL (H1, H3, H4, H5, H7, H8, H9) |
| E37 | 894 | 2026-03-15 | **Deviation** | Proposer-Verifier pipeline introduced as a post-hoc extension not in the preregistration | **H2** (+ frames H1, H9) |
| E38 | 912 | 2026-03-20 | Clarification | PV implemented for both Batch and real-time APIs via a shared IR; identical prompts and results | H2 (implementation) |
| E39 | 928 | 2026-03-21 | Clarification | All three verifier strategies statistically equivalent at 340 tiles; adversarial retained as default | H2 |
| E40 | 944 | 2026-03-24 | **Deviation** | Gemini 3.1 Pro cannot run MINIMAL thinking; Pro uses MEDIUM (single-pass) / HIGH (consensus) | **H6** |
| E41 | 960 | 2026-03-24 | **Deviation** | Pro comparison run at 384 px on 487 tiles, not the preregistered 20-tile 512 px H6 holdout | **H6**, H11 |
| E42 | 976 | 2026-03-25 (initial); 2026-03-25 (corrected) | Correction | `configuration.model` recorded the config default, not the `--model` override; an initial mis-diagnosis renamed Pro dirs to Flash and was reverted | H6 (model provenance) |
| E43 | 1039 | 2026-03-25 (discovered during configuration audit) | **Deviation** | consensus-384 ran at T=1.0 not T=0.7 (30 runs × 487 tiles); data preserved and reused as a T sensitivity analysis | H11, H3, H7 |
| E44 | 1070 | 2026-03-25 (discovered during configuration audit) | **Deviation** | single-pass-384 ran at T=1.0 not T=0.0 (10 runs × 240 tiles); archived unused, corrected rerun at 487 tiles | H11, H7 |
| E45 | 1097 | 2026-03-26 | **Deviation** | Pairwise permutation statistic changed from macro-average to micro-average F1 (tile-swap) | ALL (every pairwise test) |
| E46 | 1163 | 2026-03-27 | **Deviation** | Primary spatial matching buffer changed 20 m → 30 m | ALL |
| E47 | 1236 | 2026-03-29 | *Reversion (restores preregistered value)* | Primary buffer reverted 30 m → preregistered 20 m; supersedes E46; 30 m retained as secondary | ALL |
| E48 | 1291 | 2026-04-15 | Correction | §8.4.1 "target M=3" HN is a stale draft value; HN=4 (consistent with Scale-8) adopted | H8 |
| E49 | 1313 | 2026-04-15 | **Deviation** | H10 calibration uses a cold-start production config (T=0.7, HIGH, text+image, 9 examples, 150 px) not the prereg image-only T=1.0 baseline | **H10** (+ defines "hard" for H8, H12) |
| E50 | 1343 | 2026-04-15 | **Deviation** | H10 holdout expanded 60 → 327 tiles (consequence of the 384 px move) | **H10**, H11 |
| E51 | 1366 | 2026-04-15 | **Deviation** | H8 re-run at 384 px under production carry-forward (T=0.7, HIGH, K=5, 327-tile manifest); Scale-16/32 re-enabled | **H8** (+ H7, H10, H11, H12) |
| E52 | 1468 | 2026-04-15 | *Deviation + deferral resolution* | H12 re-run at production carry-forward, R2 reused from H8 v2 Scale-8; Decision 11 deferral resolved; the "H8 shows size matters" trigger relaxed after H8 v2 returned null | **H12** (+ H8 trigger) |
| E53 | 1581 | 2026-04-16 | **Deviation** | Phase 3a-HIGH image track moved 512 px (340 tiles) → 384 px (487 tiles); replaced by a 2×4 thinking×temperature matrix | **H3**, H11 |
| E54 | 1673 | 2026-04-21 | Clarification | Bootstrap iterations: 1,000 for preregistered primary F1; 10,000 for named post-hoc narrow-effect analyses | ALL (all CIs) — **see §5** |
| E55 | 1711 | 2026-05-30 | *Metadata correction (non-destructive)* | Verifier-t-pilot T0.5/T1.0 `run.meta.json` retained `temperature: 0.0`; additive `temperature_effective` + `_correction` block added | H2 (exploratory pilot) |
| E56 | 1746 | 2026-06-02 (+ Update 2026-06-06) | *Methodological clarification (threshold provenance)* | Verifier `prob_t` operating points are selected on the 487-tile **test** set with no held-out verifier data; headline binary verdict unaffected | H2 (+ H3 scope in the Update) — **see §5** |
| E57 | 1782 | 2026-06-02 (original); revised 2026-06-03 | *Metadata correction (non-destructive) + **billing reconciliation (finding-affecting)*** | Four "Pro" cells were dispatched and billed as Flash; genuine-Pro re-run changed the N=1 leaderboard tie_set and the H6 narrative | **H6**, H1, H7, H11 |

---

## 3. The substantive-Deviation subset — what a Methods "deviations" passage must cover

The 18 strictly-labelled `Deviation` entries plus E47 and E52 (**20 total**, per §1). For each: does
it change how a result should be interpreted?

| E | Deviation | Changes interpretation? |
|---|---|---|
| **E13** (L275) | H12 deferred post-H10 | **No, but must be disclosed.** Later *reversed* by E52. The pair together tells a clean story: deferred for a stated confound, then run once the confound lifted. |
| **E27** (L617) | Dual-track carry-forward (two M/E levels, not one) | **Yes — structurally.** The preregistered OFAT design assumed one carry-forward. Track 2 (text-only) results from Phase 2d/2e are, on the erratum's own terms (`L639`), "reported as exploratory". Any claim resting on Track 2 must inherit that label. |
| **E28** (L643) | H5 3×3 factorial → single-factor OFAT; instruction text trimmed | **Yes.** The preregistered M/E × H5 **interaction test is not estimable** — the erratum concedes it "reduces statistical power for detecting M/E × H5 interactions" (`L665`). H5's registered prediction (`preregistration.md:1156`) explicitly includes "M/E × H5 interaction non-significant" as an advance criterion. That criterion cannot be evaluated. |
| **E30** (L695) | 4 ordering conditions, not 3 | **Mildly.** Adds a baseline; strengthens rather than weakens H4. The multiplicity burden rises from 3 to 4 conditions — check that the FDR family was defined over 4. |
| **E31** (L726) | 4 deterministic units copied, not re-executed | **No**, if T=0.0 determinism holds — which the erratum evidences (`L737`, Phase 2d byte-identical replicates). But it means **within-condition variance for fixed-ordering T=0.0 conditions is structurally zero, not measured**. Do not report an SD or CI for those cells as if it were sampled. |
| **E32** (L747) | Phase 3a consensus at T=0.3/0.7, not carry-forward T=0.0 | **Yes.** H3's comparison is consensus-at-T>0 against a **T=0.0 single-run** baseline (`L762`), i.e. temperature and aggregation move together. The consensus gain is not a pure aggregation effect. This is the erratum's own framing and it is the right one, but it must be stated. |
| **E36** (L878) | 60-tile holdout → 340-tile retest; K cut 10→1–3 | **Yes, pervasively.** Every Phase 2–3 number in the paper comes from the retest, not from the preregistered evaluation set, and **K=10 replication was abandoned for single-pass conditions**. Power went up; per-condition replicate variance went away. Any "K=10 independent runs" language inherited from `preregistration.md:315` is now false for most cells. |
| **E37** (L894) | Proposer-Verifier pipeline introduced post-hoc | **Yes — this is the single largest scope deviation.** The study's headline architecture is not preregistered. The erratum is explicit (`L908`): "The PV pipeline is an extension beyond the preregistered design". Every PV result is exploratory by construction, however strong. |
| **E40** (L944) | Pro cannot run MINIMAL; uses MEDIUM/HIGH | **Yes.** Confounds model capability with thinking budget; the erratum says so (`L956`). No clean Flash-vs-Pro contrast at matched thinking exists. H6 conclusions are model+budget conclusions. |
| **E41** (L960) | Pro compared at 384 px / 487 tiles, not 20 tiles / 512 px | **Yes.** The erratum's own verdict (`L972`): "best characterised as an exploratory extension rather than a strict implementation of H6". If the paper claims H6 confirmatorily, this erratum is the counter-argument a reviewer will reach for. |
| **E43** (L1039) | consensus-384 executed at T=1.0, not 0.7 | **No for the headline** (a corrected baseline was produced, `L1065`), **yes as a bonus finding** — the wrong-temperature data became a T=0.7-vs-T=1.0 sensitivity analysis (`L1060-1062`, ΔF1 ~+0.15, p<0.0001). Report the provenance if that sensitivity result is cited. |
| **E44** (L1070) | single-pass-384 executed at T=1.0, not 0.0 | **No.** Data archived, unused in any published analysis (`L1085-1086`); corrected rerun at 487 tiles. Disclose for completeness only. |
| **E45** (L1097) | Permutation statistic macro→micro F1 | **Yes.** Different ΔF1 *and* different p-values for the same comparison — the erratum gives a worked case (`L1155-1158`): ΔF1 +0.015, p=0.019 micro vs +0.007, p=0.081 macro. A comparison that is significant under the reported statistic is not significant under the registered one. **See also §4, item 3 — the preregistration does not actually specify a permutation test at all.** |
| **E46** (L1163) | Primary buffer 20 m → 30 m | **Superseded** by E47. Matters only for artefacts generated between 2026-03-27 and 2026-03-29. Report the pair, not E46 alone. |
| **E47** (L1236) | Buffer reverted to preregistered 20 m | **Yes, favourably.** Restores registered alignment and (per `L1259-1263`) yields greater discrimination. Both tolerances reported. This is the model of how a deviation should be handled and is worth foregrounding. |
| **E49** (L1313) | H10 calibration on a cold-start production config | **Yes.** It "Changes which examples are identified as hard" (`L1320`) — so the hard-example library that H8 and H12 depend on is mined under different settings than registered. The dependency chain E49→E51→E52 should be stated once, together. |
| **E50** (L1343) | H10 holdout 60 → 327 tiles | **No adversely** — more power, calibration pool sizes unchanged (`L1356-1357`). Disclose as a scope change. |
| **E51** (L1366) | H8 re-run at 384 px / production carry-forward; Scale-16/32 re-enabled | **Yes.** H8 results are reported on a different pipeline (tile size, T, thinking, K, evaluation manifest — nine parameters change per the table at `L1381-1395`) than registered, and two previously-deferred conditions return. The original 512 px H8 and H8 v2 are **not comparable** and should not be pooled. |
| **E52** (L1468) | H12 re-run at production carry-forward; **trigger relaxed** | **Yes — this is the one to watch.** H12's registered trigger was "run if H8 shows library size matters" (`preregistration.md:1010`); H8 v2 returned null on all seven contrasts, so the erratum concedes (`L1503-1504`) "Strictly read, the trigger is not met" and runs H12 anyway for two stated reasons. **A registered trigger that was not met but was overridden is exactly the disclosure a preregistration-checking reviewer looks for.** It is defensibly argued, but it must appear in the deviations passage, not be left in the errata file. |
| **E53** (L1581) | Phase 3a-HIGH image track moved 512 px → 384 px, redesigned as a 2×4 matrix | **Yes.** The H3 image-track consensus result is on a different tile size and tile set than the H3 text-track result (`L1588`). Cross-track H3 comparisons at matched scope are not available from this pair. The erratum argues the replacement is "more informative" (`L1634`), which is fair — but it is a different experiment. |

**Three deviation clusters worth writing as narrative rather than as a list**, because they are
causally linked and reviewers will otherwise read three separate lapses where there is one decision:

1. **Evaluation-scale cluster** — E36 (60→340 tiles) → E50 (60→327 for H10) → E41 (Pro at 487) →
   E51/E52/E53 (everything re-run at 384 px). One decision (the corpus was too small to have power)
   propagating through the whole design.
2. **Buffer cluster** — E46 → E47. One excursion, reverted, both reported.
3. **Library-provenance cluster** — E11 (HP pool exhausted) → E12 (H9-C degraded) → E13 (H12
   deferred) → E49 (new mining config) → E51 (H8 v2, Scale-16/32 restored) → E52 (H12 undeferred,
   trigger overridden). One structural constraint and its eventual resolution.

---

## 4. Entries with no clear hypothesis mapping

These are **pipeline / infrastructure / documentation** errata. They belong in a Methods
"implementation and evaluation pipeline" passage or a reproducibility supplement — **not** in a
"deviations from the registered protocol" passage, where they would dilute the entries that matter.

**Genuinely hypothesis-free (10):** E1 (docs), E2 (Phase 1 config), E15 (appendix pass-count
inconsistency), E19 (bounds file), E20 (naming), E21 (analysis-script parameter), E23 (metadata
capture), E24 (runner dry-run bug), plus — on a looser reading — E3 (SDK migration) and E38 (dual-mode
API). All are `Correction` or `Clarification`; none changes a reported number.

**Hypothesis-free but *evaluation-affecting*, so they must be reported somewhere (9):** E4, E5, E6,
E7, E22, E26, E35, E45, E54. These do not attach to a hypothesis but they change how *every*
hypothesis was measured. Suggested home: a Methods subsection on evaluation-pipeline corrections,
with a pointer to the errata document. Note that four of these (E26, E35, E45, E54) are
**statistical-method** entries, which is where the sharpest reviewer attention will land.

**Three flags raised by this census that are not in the errata file at all:**

1. **The preregistration never specifies a permutation test.** `grep -c -i "permut"` returns **0**
   for `docs/methodology/preregistration/osf/preregistration.md`, **0** for
   `preregistration-coverage.md`, **0** for `analysis-summary.md` (the 3 hits in
   `preregistration-appendix-prompts.md`, lines 1528/1533/1711, are about few-shot example ordering,
   not inference). The registered inference method is **bootstrap CIs with Benjamini–Hochberg FDR**
   (`preregistration.md:266-270`, `:290-296`; `analysis-summary.md:75,93,99,111,117`). Yet E45
   (`protocol-errata.md:1107-1109`) opens "The preregistered pairwise permutation test (Section 3.5)
   specifies tile-level resampling with a sign-flip permutation…" — and §3.5 of the preregistration
   (lines 290–296) is a *Reporting* section containing no such specification. **The study's actual
   headline inference engine — round-robin tile-swap micro-F1 permutation with BH-FDR, used across
   every leaderboard in `analyses-manifest.json` — is not the registered method.** E45 documents a
   change *within* permutation testing while mis-citing permutation testing as registered. This
   needs either a new erratum or a correction to E45; it is more consequential than most of the
   entries that do have E-numbers.
2. **BCa bootstrap at 10,000 iterations is undocumented.** `grep -in "BCa"` returns **0** in both
   `protocol-errata.md` and `decisions-log.md`. But `results/conditions-manifest.json` records
   **4,068 per-buffer CI blocks with `"method": "BCa", "n_iter": 10000`** and **112 with
   `"method": "percentile", "n_iter": 10000`** — i.e. **zero CIs at the registered 1,000-iteration
   percentile setting**. The migration is traceable (`results/ci-metadata-registry.md:187`, "commit
   `e20f3e18` for the BCa N=10K migration", noting it "Replaces the 2026-04-18 N=1000 percentile
   entry"), so this is a documentation gap rather than a hidden change — but E54, dated 2026-04-21,
   predates the migration and therefore **does not cover it**. See §5.
3. **Several errata mis-cite preregistration section numbers.** E45, E46, and E47 all give
   "Preregistration ref | Section 3.5". The 20 m primary buffer is actually specified at
   `preregistration.md:341` (§4.1.1 Spatial Tolerance), and the Hungarian matching at `:358-368`
   (§4.1.2). E54 cites "Section 3.5" for the 1,000-iteration percentile bootstrap but anchors it to
   `decisions-log.md:337` — which *does* contain that specification, in **Decision 10**, not in the
   preregistration. Low-stakes individually; collectively they mean **an OSF reader following the
   errata's section references will not find the cited text**. Worth a sweep before the errata file
   is published as a supplement.

---

## 5. E54 and E56 — what they constrain the paper from claiming

### E54 — bootstrap iteration count (`protocol-errata.md:1673-1707`)

**What it says.** The preregistered setting is 1,000 iterations, percentile method (2.5th/97.5th),
tile-level resampling (`L1682`; the actual specification lives at `decisions-log.md:337`, Decision
10 — see §4 item 3). Scripts evaluating preregistered conditions use 1,000: `evaluate_detections.py`
(`DEFAULT_BOOTSTRAP = 1000`), `lib_advanced_metrics.bootstrap_ci` (default `n_iterations = 1000`),
`compute-pairwise-effect-sizes.py`, `evaluate_pv_results.py`, `compare_wbf_vs_greedy.py`,
`analyse_secondary_effects_text.py` (`L1682`, `L1705`). Four named **post-hoc** analyses use 10,000:
`compute_corrected_f1_human_reviewed.py`, `compute_corrected_f1_multi_buffer.py`,
`analyse_subtype_classification.py`, `crosstab_uncalibrated_vs_calibrated.py` (`L1686-1689`).
`analyse_buffer_band_lift.py` stays at M=1,000 (`L1690`).

**What it constrains the paper from claiming — plainly:**

1. **The paper cannot state a single uniform bootstrap specification.** Any sentence of the form
   "all confidence intervals are N-iteration tile-level bootstrap" is false. E54 itself drafts the
   correct split-form wording (`L1700`) and the paper should use it or something like it.
2. **The paper cannot present a tightened CI as preregistered precision.** The 10,000-iteration runs
   exist *because* the effects are narrow — the erratum says so explicitly (`L1684`, "narrow effect
   sizes where CI precision at 2-3 decimal places is material for narrative clarity"). Any claim of
   the form "these per-class F1s are separable / this disagreement rate is bounded" that rests on a
   10,000-iteration CI is a **post-hoc** claim and must be labelled exploratory. E54's own rule
   (`L1694`) is that any 10,000-iteration setting applied to a *preregistered* condition would
   require a Deviation-class erratum, not a Clarification. That rule is the paper's guardrail: if a
   preregistered result is quoted with a 10K CI, the classification of that erratum is wrong.
3. **More iterations reduce Monte-Carlo error, not sampling error.** The paper must not let the
   tighter intervals read as a stronger design. Going 1,000→10,000 shrinks the noise in the *estimate
   of the interval*; it does not shrink the interval that the data support. If any narrative implies
   otherwise, it overclaims.
4. **E54 does not cover the CI method actually in the manifests.** `results/conditions-manifest.json`
   carries **no** CIs at the registered percentile/1,000 setting: 4,068 blocks are `BCa` at 10,000
   and 112 are `percentile` at 10,000. BCa is a *different estimator* from the percentile method
   (bias-corrected and accelerated), not merely a different iteration count, so this is a change E54
   never addresses. Until it is documented, **the paper cannot claim that its reported CIs follow the
   preregistered CI procedure.** The honest statement is that CIs on the deployment/condition
   register use BCa at 10,000 iterations with tile-level resampling and seed 42, that this departs
   from the registered percentile/1,000 specification, and that the migration is traced at
   `results/ci-metadata-registry.md:187` (commit `e20f3e18`). **Recommend a new erratum (E58) rather
   than an edit to E54**, since E54's date (2026-04-21) precedes the migration and rewriting it would
   destroy the chronology.

### E56 — verifier probability-threshold operating points (`protocol-errata.md:1746-1778`)

**What it says.** The headline PV pipeline applies the verifier as a **binary accept/reject verdict**
— `prob_threshold = null`, no cutoff tuned (`L1755`, verified against `results/run-conditions.json`).
But the verifier's continuous `mound_probability` is explored in the **diagnostic** runs, where the
per-cell operating point `(vote_t, prob_t)` is chosen by sweeping the grid and taking the F1 optimum
at 20 m — **and that sweep is performed on the 487-tile evaluation scope, which is the test set**
(`L1757`). There is no calibration-tile verifier data to select on: the verifier never ran on the 20
calibration tiles, and pv-diag ∩ calibration = 0 (`L1757`, `L1759`). Therefore "any single
`prob_t`-thresholded F1 quoted for these diagnostics is an **in-sample, test-set-optimised** number,
not a calibrated one" (`L1757`).

**What it constrains the paper from claiming — plainly:**

1. **No `prob_t`-thresholded diagnostic F1 may be reported as an achievable or generalisable
   operating point.** It is the maximum of a curve fitted on the same data it is evaluated on. The
   erratum's reporting rule (`L1766`) requires such numbers be presented as **threshold-sensitivity
   curves**, and that where a single point is quoted it be labelled "20 m test-set F1-optimum
   (in-sample)" with the fixed-reference value beside it.
2. **The blast radius is specific and enumerated** (`L1761`): the 14 `*-opt-20m.geojson` Session 78
   cells, the h10 / h8-v2 / verifier-t-pilot `detections_vt*_pt*` materialisations, and the
   pv-diag-384 PV quadrants. Anything outside that list is unaffected.
3. **What is *not* constrained, and the paper must not over-correct.** The headline PV results
   (binary verdict) and **all** consensus-vote-threshold results are explicitly unaffected (`L1761`)
   — the vote threshold was calibrated on the 20 held-out calibration tiles at ≥3/5 (`L1755`,
   `L1774`). The 2026-06-06 Update (`L1772-1778`) goes further and rules that the **H3 consensus
   characterisation** (`diversity-dividend-384`) is **not** an in-sample limitation, because the
   preregistered H3 analysis plan asks for "threshold sweep curves showing **optimal (N, threshold)
   combinations**" — so swept-optimal reporting *is* the registered method there. The Update
   enumerates three provenances that must be kept distinct (`L1774-1776`): calibrated (Phase-1 vote
   threshold), preregistered-swept (H3 characterisation), and in-sample (verifier `prob_t`). **A
   paper that collapses these under one "in-sample" caveat is as wrong as one that omits the caveat
   entirely.**
4. **A transfer constraint that is easy to miss.** `L1768`: the text-track verifier is
   well-calibrated (AUC 0.956, ECE 0.071); **the image track is not** (AUC 0.86, ECE 0.18). So a
   fixed probability threshold transfers on text but **not** on image. Any image-track operating
   point must carry that citation. The paper cannot present image-track `prob_t` results with the
   same confidence as text-track ones.
5. **Why the constraint is survivable.** The erratum evidences that the F1@20 curve is flat in the
   operating range (`L1759`): single-run PV ≈0.74 across prob_t 0.25–0.40, consensus PV ≈0.86 across
   0.15–0.20, with the fixed reference (0.20) and the in-sample optimum differing by **≤0.022 F1**.
   That number is the honest bound on the optimism, and quoting it is a stronger move than hedging
   vaguely. But it bounds the optimism *on the text track*, where calibration is good — do not extend
   it to image.

**One-sentence versions for the Methods passage.** *E54*: confidence intervals in this study were not
all computed under the registered procedure — primary preregistered evaluations use 1,000-iteration
percentile bootstrap as registered, named post-hoc analyses use 10,000 iterations, and the
condition-level register uses BCa at 10,000, so no blanket statement about CI provenance can be made
and tightened intervals must not be read as preregistered precision. *E56*: any verifier
probability-threshold operating point we report was selected on the evaluation set itself and is
therefore an in-sample optimum, not a calibrated or deployable threshold — we report these as
sensitivity curves; the headline pipeline uses the verifier's binary verdict with no tuned cutoff,
and the consensus vote threshold was calibrated on held-out tiles.

---

## 6. Verification note

Every count in this document was produced by parsing `protocol-errata.md` at compile time, not
recalled: the 57-entry total, the eight distinct `Type` strings and their frequencies, and the
per-entry line anchors all come from a single pass over the file. Manifest counts (322 conditions,
1,132 pass rows, 4,180 CI blocks, 18 analyses) come from parsing `results/conditions-manifest.json`,
`results/passes-manifest.md`, and `results/analyses-manifest.json`. The absence claims
(no permutation spec in the preregistration; no `BCa` in the errata or decisions log; no H13/H14/H15
anywhere outside the preregistration and its derived planning documents) are `grep -c` results, and
each is re-runnable in one command.
