# D17 — Errata census (E1–E78)

> **Last revised**: 2026-08-17 (refreshed to E78 vintage: two-vintage recount, E58–E78 table
> extension, three post-compilation retypes reconciled, line anchors re-derived). See
> [§ Changelog](#changelog) for revision history.

**Source**: `docs/methodology/preregistration/protocol-errata.md` (3,607 lines at refresh).

**Entry count**: **exactly 78**. Counted programmatically — `grep -c "^### E[0-9]"` returns 78, and
a per-entry parse yields 78 blocks, each declaring exactly one `Type`, across the file's **three
entry formats** (table `| Type | … |`; bulleted `- **Type**:` used only by E31/E32; bold
`**Type**:`). Not estimated. A parser matching only one format under-counts silently — the E31/E32
format cost this refresh's first pass two bare `Deviation` entries.

**Repository**: `/home/shawn/Code/map-reader-llm` (read-only inspection of the errata file; this
census document is the only file edited).
**Compiled**: 2026-07-27 (E1–E57). **Refreshed**: 2026-08-17 (E1–E78; S135 analysis block, item 3).

**Anchoring convention**: the `L` column gives the line number of the entry's `### En:` heading in
`protocol-errata.md`. The `Type` column reproduces the entry's own declared `Type` field **verbatim**
— including the 26 entries whose labels fall outside the document's own three-way scheme (see § 1).

**The document's declared scheme** (`protocol-errata.md:11-15`):

> - **Correction**: Fix to implementation that brings it into alignment with the preregistered
>   protocol (no protocol change)
> - **Clarification**: Interpretation of an ambiguous point in the preregistration
> - **Deviation**: Substantive change from the preregistered protocol (requires justification)

---

## 1. Counts by classification (E78 vintage, refreshed 2026-08-17)

**Bare three-way labels** (the document's declared scheme, label matched exactly):

| Bare label | E1–E78 | of which E1–E57 (today) | of which E58–E78 |
|---|---:|---:|---:|
| `Correction` | **22** | 22 | 0 |
| `Deviation` | **18** | 16 | 2 (E58, E59) |
| `Clarification` | **12** | 11 | 1 (E61) |
| Composite or ad-hoc labels | **26** | 8 | 18 |
| **Total** | **78** | 57 | 21 |

**The 26 composite/ad-hoc labels, grouped by family**: deviation-family composites —
`Deviation (…)` qualifiers on E10, E45, E60, E62, E63, E65, E69, plus the three
omission-recording entries E74, E75, E78 (`Deviation (records an omission, not a change)`) and
`Deviation + deferral resolution` (E52); correction-family composites — E37, E67, E71;
clarification-family composites — E64, E66, E68, E70, E76, E77; true ad-hoc — `Reversion
(restores preregistered value)` (E47), `Metadata correction (non-destructive)` (E55),
`Methodological clarification (threshold provenance)` (E56), `Metadata correction
(non-destructive) + billing reconciliation (finding-affecting)` (E57), `Analysis defect
(exploratory; no registered hypothesis affected)` (E72), `Documentation integrity` (E73).

**Vintage reconciliation.** The compile-time table (2026-07-27) counted 22 / 18 / 12 / 5 over
E1–E57 and was correct when compiled. Three entries were retyped in place afterwards (commits
`044cbcd82`, `df16d855a`): **E10** bare `Clarification` → `Deviation (originally recorded as
Clarification)`; **E37** bare `Deviation` → `Correction (originally recorded as Deviation)`;
**E45** bare `Deviation` → `Deviation (unregistered inference method adopted)`. Within E1–E57
today the bare counts are therefore 22 / 16 / 11 with 8 composites. Any consumer holding the
compile-time "18 bare Deviations" figure is quoting a superseded vintage — this bit
`docs/paper/methods-draft.md`, whose first tally asserted 16 bare deviations *at E78 scope*
(correct only for E1–E57) and 28 composites (correct for neither vintage; the true E78 figure
is 26). The same draft passage also lists E59 among the composite-labelled omission-recording
entries; E59's Type is bare `Deviation` (it records an omission in substance, not by label),
so only E74/E75/E78 belong to that labelled set.

**Reading for the Methods passage.** The scheme admits three types; 26 of 78 entries now use
composite or ad-hoc labels, including several of the most interpretively consequential (E56,
E57, E45). **If the paper reports "N deviations" it must say which counting rule it used.**
Defensible headline numbers at E78 vintage:

- **18** — strict bare `Deviation` label only.
- **30** — all deviation-labelled entries (the 18 bare + the eleven deviation-family composites
  listed in the grouping paragraph above, E52 included) + E47 (a reversion *is* a protocol
  change, back to the registered value).
- **27** — as 30, excluding the three omission-recording entries (E74, E75, E78), which record
  registered work that never happened rather than changes to what did.

The compile-time recommendation ("20, with E56 and E57 discussed alongside") does not survive
the vintage move; its nearest E78 descendant is **27 with E56/E57/E74/E75/E78 discussed in the
same passage**. The Methods draft currently takes the alternative this census also licenses:
**no aggregate at all — cite entries individually because any headline count depends on the
counting rule adopted**. Both are honest; adopting one is a PI call (queued, S135 block plan
§ 6 L4).

---

## 2. Full table — all 78 entries

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
| E10 | 222 | 2026-02-02; reclassified 2026-07-28 | Deviation (originally recorded as Clarification) | Recognition/localisation split and its 50 m threshold are post-hoc additions to the registered FN→HP definition (9 vs 15 of 24 FNs); original registered-status description withdrawn | H8, H12 (HP pool definition) |
| E11 | 239 | 2026-02-02 | Clarification | Scale-16/Scale-32 capped — HP pool structurally exhausted at 4; preregistered contingency (prereg line 815) activated | H8 (conds 6–7; contrasts S2, S3), H10 |
| E12 | 258 | 2026-02-02 | Clarification | H9-C image diversity runs as HN-rotation only; HP channel frozen at 4 | H9, H10 |
| E13 | 275 | 2026-02-02 | **Deviation** | H12 (HP:HN ratio) deferred to post-H10 — testable ratios would confound ratio with total count | H12 (via H8, H10) |
| E14 | 294 | 2026-02-04 | Clarification | Verbose instruction grew to 779 words, ~80 above the preregistered range (brief:verbose 213:779) | H1 |
| E15 | 311 | 2026-02-04 | Correction | Appendix pass-count references inconsistent (≥3/10 vs ≥3/5); execution used the correct K=5 | — (Phase 1 library construction) |
| E16 | 335 | 2026-02-03 | Clarification | Prompt exclusion language shifted from cartographic names to visual descriptions, uniformly across H5 | H5 (+ all prompt-bearing) |
| E17 | 395 | 2026-02-05 | Correction | Erroneous `passes: 5` multiplier removed from execution plan + five Phase 2 YAMLs (would have been 5× cost) | H3 (§3.8 single-pass rationale); all Phase 2 |
| E18 | 414 | 2026-02-05 | Clarification | Config filenames drop the redundant `_minimal` H5 suffix; unsuffixed config *is* H5=Minimal | H1, H5 (naming only) |
| E19 | 431 | 2026-02-05 | Correction | `validation_bounds.geojson` built from the calibration manifest; only 7/20 tiles overlapped the 60 validation tiles | ALL (sanity-check metrics) |
| E20 | 460 | 2026-02-05 | Clarification | "holdout"→"validation" naming standardised across metadata, scripts, tests | — (naming) |
| E21 | 514 | 2026-02-05 | Correction | Stale `passes: int = 5` parameter removed from `analyse_phase2_results.py`; file globbing fixed | — (analysis infra) |
| E22 | 533 | 2026-02-05 | Correction | Evaluation rewritten from merged-runs to per-run F1 (merging made precision nonsensical at K=10) | ALL (Phase 2 metrics) |
| E23 | 561 | 2026-02-05 | Correction | Three Gemini metadata fields (citation, block reason, prompt safety) captured instead of discarded | — (metadata) |
| E24 | 586 | 2026-02-05 | Correction | `--dry-run` corrupted the checkpoint (3→50 units "completed"); guarded | — (runner infra) |
| E25 | 605 | 2026-02-06 | Correction | **Modality manipulation not implemented** — text-only conditions received all 17 example images; 20 runs invalid, re-run | **H1** |
| E26 | 644 | 2026-02-06 | Correction | Bootstrap CIs systematically deflated (~34%) by reference de-duplication on resampled tiles; 7 functions refactored | ALL (all CIs) |
| E27 | 679 | 2026-02-06 | **Deviation** | Dual-track carry-forward: two M/E levels (brief-text-image, brief-text) carried from Phase 2a instead of one | H1, H4, H5, H7, H8 |
| E28 | 705 | 2026-02-11 | **Deviation** | H5 instruction text trimmed (HN image references removed) and the 3×3 factorial simplified to single-factor OFAT | **H5** |
| E29 | 731 | 2026-02-12 | Correction | `reorder_examples()` `canonical-first` was a no-op; split into `config-default` and true `canonical-first` | H4 |
| E30 | 757 | 2026-02-12 | **Deviation** | Phase 2e tests 4 ordering conditions, not the preregistered 3 (adds `config-default` baseline) | **H4** |
| E31 | 788 | 2026-02-12 | **Deviation** | 4 deterministic T=0.0 units copied from an existing run rather than re-executed (byte-identical at T=0.0) | H4 |
| E32 | 809 | 2026-02-12 | **Deviation** | Phase 3a runs consensus at T=0.3/0.7, not the carry-forward T=0.0 (voting needs run-to-run variation) | **H3** (+ H7 carry-forward) |
| E33 | 830 | 2026-03-12 | Correction | Verifier crops read from tile PNGs not source rasters → truncated edge crops; all Phase 3d PV results re-run | **H2** |
| E34 | 857 | 2026-03-15 | Correction | `thinking_level` not copied into execution units, so `--thinking-level` was silently dropped; fixed pre-collection | H3 (phase3a-replication) |
| E35 | 888 | 2026-03-15 | Correction | Bootstrap matched per-tile while point estimates matched per-map → recall bias (~7 pp at 340 tiles); now per-map | ALL (all CIs) |
| E36 | 942 | 2026-03-17 | **Deviation** | 340-tile production retest replaces the 60-tile holdout; all Phase 2–3 conditions re-run; K cut 10→1–3 | ALL (H1, H3, H4, H5, H7, H8, H9) |
| E37 | 999 | 2026-03-15; reclassified 2026-07-28 | Correction (originally recorded as Deviation) | Proposer-Verifier pipeline ruled the production implementation of registered H2 Condition B (D17 audit); the compile-time "post-hoc extension" reading is superseded | **H2** (+ frames H1, H9) |
| E38 | 1074 | 2026-03-20 | Clarification | PV implemented for both Batch and real-time APIs via a shared IR; identical prompts and results | H2 (implementation) |
| E39 | 1090 | 2026-03-21 | Clarification | All three verifier strategies statistically equivalent at 340 tiles; adversarial retained as default | H2 |
| E40 | 1106 | 2026-03-24 | **Deviation** | Gemini 3.1 Pro cannot run MINIMAL thinking; Pro uses MEDIUM (single-pass) / HIGH (consensus) | **H6** |
| E41 | 1140 | 2026-03-24 | **Deviation** | Pro comparison run at 384 px on 487 tiles, not the preregistered 20-tile 512 px H6 holdout | **H6**, H11 |
| E42 | 1156 | 2026-03-25 (initial); 2026-03-25 (corrected) | Correction | `configuration.model` recorded the config default, not the `--model` override; an initial mis-diagnosis renamed Pro dirs to Flash and was reverted | H6 (model provenance) |
| E43 | 1219 | 2026-03-25 (discovered during configuration audit) | **Deviation** | consensus-384 ran at T=1.0 not T=0.7 (30 runs × 487 tiles); data preserved and reused as a T sensitivity analysis | H11, H3, H7 |
| E44 | 1279 | 2026-03-25 (discovered during configuration audit) | **Deviation** | single-pass-384 ran at T=1.0 not T=0.0 (10 runs × 240 tiles); archived unused, corrected rerun at 487 tiles | H11, H7 |
| E45 | 1306 | 2026-03-26; corrected 2026-07-28 | Deviation (unregistered inference method adopted) | Permutation statistic macro→micro F1 (tile-swap), and the corrected entry discloses the permutation method itself as unregistered (the registration specifies bootstrap CIs + BH only) | ALL (every pairwise test) |
| E46 | 1388 | 2026-03-27 | **Deviation** | Primary spatial matching buffer changed 20 m → 30 m | ALL |
| E47 | 1461 | 2026-03-29 | *Reversion (restores preregistered value)* | Primary buffer reverted 30 m → preregistered 20 m; supersedes E46; 30 m retained as secondary | ALL |
| E48 | 1516 | 2026-04-15 | Correction | §8.4.1 "target M=3" HN is a stale draft value; HN=4 (consistent with Scale-8) adopted | H8 |
| E49 | 1538 | 2026-04-15 | **Deviation** | H10 calibration uses a cold-start production config (T=0.7, HIGH, text+image, 9 examples, 150 px) not the prereg image-only T=1.0 baseline | **H10** (+ defines "hard" for H8, H12) |
| E50 | 1568 | 2026-04-15 | **Deviation** | H10 holdout expanded 60 → 327 tiles (consequence of the 384 px move) | **H10**, H11 |
| E51 | 1591 | 2026-04-15 | **Deviation** | H8 re-run at 384 px under production carry-forward (T=0.7, HIGH, K=5, 327-tile manifest); Scale-16/32 re-enabled | **H8** (+ H7, H10, H11, H12) |
| E52 | 1693 | 2026-04-15 | *Deviation + deferral resolution* | H12 re-run at production carry-forward, R2 reused from H8 v2 Scale-8; Decision 11 deferral resolved; the "H8 shows size matters" trigger relaxed after H8 v2 returned null | **H12** (+ H8 trigger) |
| E53 | 1806 | 2026-04-16 | **Deviation** | Phase 3a-HIGH image track moved 512 px (340 tiles) → 384 px (487 tiles); replaced by a 2×4 thinking×temperature matrix | **H3**, H11 |
| E54 | 1901 | 2026-04-21 | Clarification | Bootstrap iterations: 1,000 for preregistered primary F1; 10,000 for named post-hoc narrow-effect analyses | ALL (all CIs) — **see §5** |
| E55 | 1939 | 2026-05-30 | *Metadata correction (non-destructive)* | Verifier-t-pilot T0.5/T1.0 `run.meta.json` retained `temperature: 0.0`; additive `temperature_effective` + `_correction` block added | H2 (exploratory pilot) |
| E56 | 1990 | 2026-06-02 (+ Update 2026-06-06) | *Methodological clarification (threshold provenance)* | Verifier `prob_t` operating points are selected on the 487-tile **test** set with no held-out verifier data; headline binary verdict unaffected | H2 (+ H3 scope in the Update) — **see §5** |
| E57 | 2026 | 2026-06-02 (original); revised 2026-06-03 | *Metadata correction (non-destructive) + **billing reconciliation (finding-affecting)*** | Four "Pro" cells were dispatched and billed as Flash; genuine-Pro re-run changed the N=1 leaderboard tie_set and the H6 narrative | **H6**, H1, H7, H11 |
| E58 | 2099 | 2026-04-08 (analysed); registered 2026-07-28 | **Deviation** | Registered proposer prompt `propose_brief` never used; `detect_brief-text` substituted across every PV run — measured conservative at N=1, superior under production consensus | **H2** (all PV) |
| E59 | 2144 | 2026-07-28 (+ Update 2026-08-17) | **Deviation** | H2 Condition C (fine-to-coarse) never executed and never formally dropped; no `expand_*` artefacts exist; 1024 px pricing run queued before the run-vs-disclose decision | **H2** |
| E60 | 2210 | 2026-07-28 | *Deviation (registered conditional evaluated; escalation not conducted)* | H7 escalation trigger never fired on the registered corpus; fired within noise on the unregistered expanded corpus; T=1.6/T=2.0 not run | **H7** |
| E61 | 2261 | 2026-07-28 | Clarification | "Main effect" in the H4b trigger designates the registered directional contrast; H4b is not an owed experiment; fixes H4's primary test ahead of the family FDR | **H4** |
| E62 | 2314 | 2026-07-30 | *Deviation (unregistered exploratory extensions; no registered study altered)* | Three unregistered proposer-verifier extension studies disclosed; with E69 and E40's clarification, closes the unlicensed-run set | — (exploratory PV extensions) |
| E63 | 2440 | 2026-07-30 | *Deviation (unregistered thinking level on an exploratory hypothesis)* | `retest-phase3c` (H9) executed at HIGH thinking; constant across all compared H9 conditions, so within-H9 contrasts are unconfounded | **H9** |
| E64 | 2548 | 2026-07-30 | *Clarification (five reconciliations; no registered procedure altered)* | Five internal contradictions in the lodged registration; execution followed one lodged reading in every case | ALL (lodged text) |
| E65 | 2854 | 2026-07-30 | *Deviation (lodged prompt text altered post-lodgement; lodged appendix never amended)* | `verify_brief.md` edited post-lodgement; affects the `verify_brief` strategy arm only (E39: verifier strategy not load-bearing) | H2 (verifier-strategy arm) |
| E66 | 2915 | 2026-07-30 | *Clarification (orchestration layer substituted; batch engine unchanged)* | `run_study.py` → `run_phase1.py`/`run_phase2.py`; the API-calling engine is the one the registration names | — (infra) |
| E67 | 2967 | 2026-07-30 | *Correction (documentation metadata; no protocol content affected)* | Lodged document's version header reads 4.6 against actual v4.7 | — (docs) |
| E68 | 3010 | 2026-07-30 | *Clarification (registered interpretive designation superseded by registered results)* | "Academic baseline" designation for text-only conditions retired as falsified; the deployment headline's reliance on a text-prompted condition must be disclosed | H1 (+ deployment reporting) |
| E69 | 3067 | 2026-07-30 | *Deviation (unregistered parameter levels inside an otherwise-licensed family)* | Unregistered Flash-verifier thinking levels in `pv-diag-384` (seven exploratory conditions); the production MINIMAL verifier is vindicated independently | — (pv-diag exploratory) |
| E70 | 3141 | 2026-07-30 | *Clarification (recovery mechanism disclosed; no experimental parameter changed)* | March 2026 out-of-band tile-recovery campaign (127 passes / 350 tiles); recovered detections are genuine API outputs | ALL (recovery disclosure) |
| E71 | 3197 | 2026-07-30 | *Correction (manifest bookkeeping defect + coverage shortfall disclosure)* | `n_tiles_processed` carries two semantics; two evaluated pv-diag conditions score 19–34 dead tiles as artificial false negatives | — (manifest semantics; 2 conditions) |
| E72 | 3281 | 2026-08-02 | *Analysis defect (exploratory; no registered hypothesis affected)* | Temperature comparison scored a 240-tile arm against 487-tile arms; the +0.17–0.19 "effect" was a coverage artefact (matched scope: nothing significant) | — (temperature analyses) |
| E73 | 3335 | 2026-08-02 | *Documentation integrity* | Stale preregistration pointers and one reproducibility defect on a prereg-cited script | — (docs) |
| E74 | 3367 | 2026-08-17 | *Deviation (records an omission, not a change)* | H6 (Flash→Pro transfer, Phase 4) never executed; deferral never ratified; the only registered confirmatory hypothesis with no result; excluded from the family FDR (m = 7) | **H6** |
| E75 | 3422 | 2026-08-17 | *Deviation (records an omission, not a change)* | H13 overlap/stride arms B–C silently dropped; tile overlap stayed a fixed 12.5 % parameter, never a manipulated factor | **H13** |
| E76 | 3478 | 2026-08-17 | *Clarification (registered deferral honoured; qualifications recorded)* | H14 deferral honoured with three qualifications; constrains every generalisation claim to Gemini | **H14** |
| E77 | 3521 | 2026-08-17 | *Clarification (registered deferral honoured; gated precondition)* | H15 gated on H14, which never ran; blocks any cross-architecture ensemble claim | **H15** |
| E78 | 3571 | 2026-08-17 | *Deviation (records an omission, not a change)* | § 8.9 post-experiment thinking-level verification never run; the latency limb has no coverage at all | S8.9 (minimal-thinking verification) |

---

## 3. The substantive-Deviation subset — what a Methods "deviations" passage must cover

**Membership updated 2026-08-17.** At compile time this section covered the then-18
strictly-labelled `Deviation` entries plus E47 and E52 (20 total). The E10/E37/E45 retypes move
the E1–E57 membership (E37 leaves as a correction; E10 joins; E45 stays under its composite
label), and §3b below adds the E58–E78 deviation-substance entries. For each: does it change how
a result should be interpreted?

| E | Deviation | Changes interpretation? |
|---|---|---|
| **E10** (L222; joined this subset on its 2026-07-28 retype) | Recognition/localisation split + 50 m threshold added post hoc to the registered FN→HP definition | **Yes.** Under the registered definition a mislocalised detection is an FN and an eligible hard-positive candidate; the post-hoc split changed HP eligibility (9 vs 15 of 24 FNs), upstream of the H8/H12 library. The compile-time census carried this entry as a bare Clarification. |
| **E13** (L275) | H12 deferred post-H10 | **No, but must be disclosed.** Later *reversed* by E52. The pair together tells a clean story: deferred for a stated confound, then run once the confound lifted. |
| **E27** (L679) | Dual-track carry-forward (two M/E levels, not one) | **Yes — structurally.** The preregistered OFAT design assumed one carry-forward. Track 2 (text-only) results from Phase 2d/2e are, on the erratum's own terms (`L639`), "reported as exploratory". Any claim resting on Track 2 must inherit that label. |
| **E28** (L705) | H5 3×3 factorial → single-factor OFAT; instruction text trimmed | **Yes.** The preregistered M/E × H5 **interaction test is not estimable** — the erratum concedes it "reduces statistical power for detecting M/E × H5 interactions" (`L665`). H5's registered prediction (`preregistration.md:1156`) explicitly includes "M/E × H5 interaction non-significant" as an advance criterion. That criterion cannot be evaluated. |
| **E30** (L757) | 4 ordering conditions, not 3 | **Mildly.** Adds a baseline; strengthens rather than weakens H4. The multiplicity burden rises from 3 to 4 conditions — check that the FDR family was defined over 4. |
| **E31** (L788) | 4 deterministic units copied, not re-executed | **No**, if T=0.0 determinism holds — which the erratum evidences (`L737`, Phase 2d byte-identical replicates). But it means **within-condition variance for fixed-ordering T=0.0 conditions is structurally zero, not measured**. Do not report an SD or CI for those cells as if it were sampled. |
| **E32** (L809) | Phase 3a consensus at T=0.3/0.7, not carry-forward T=0.0 | **Yes.** H3's comparison is consensus-at-T>0 against a **T=0.0 single-run** baseline (`L762`), i.e. temperature and aggregation move together. The consensus gain is not a pure aggregation effect. This is the erratum's own framing and it is the right one, but it must be stated. |
| **E36** (L942) | 60-tile holdout → 340-tile retest; K cut 10→1–3 | **Yes, pervasively.** Every Phase 2–3 number in the paper comes from the retest, not from the preregistered evaluation set, and **K=10 replication was abandoned for single-pass conditions**. Power went up; per-condition replicate variance went away. Any "K=10 independent runs" language inherited from `preregistration.md:315` is now false for most cells. |
| **E37** (L999; left this subset on its 2026-07-28 retype to Correction) | Proposer-Verifier pipeline: compile-time reading "post-hoc extension" **superseded** | **Reading superseded.** The D17 audit ruled the PV pipeline the production implementation of registered H2 Condition B, and the entry was retyped `Correction (originally recorded as Deviation)`. The compile-time sentence "Every PV result is exploratory by construction" no longer holds: H2's confirmatory adjudication lives at the family-FDR row, and PV analyses carry their own register classes (vocabulary v2). Row retained because the superseded reading circulated for three weeks. |
| **E40** (L1106) | Pro cannot run MINIMAL; uses MEDIUM/HIGH | **Yes.** Confounds model capability with thinking budget; the erratum says so (`L956`). No clean Flash-vs-Pro contrast at matched thinking exists. H6 conclusions are model+budget conclusions. |
| **E41** (L1140) | Pro compared at 384 px / 487 tiles, not 20 tiles / 512 px | **Yes.** The erratum's own verdict (`L972`): "best characterised as an exploratory extension rather than a strict implementation of H6". If the paper claims H6 confirmatorily, this erratum is the counter-argument a reviewer will reach for. |
| **E43** (L1219) | consensus-384 executed at T=1.0, not 0.7 | **No for the headline** (a corrected baseline was produced, `L1065`), **yes as a bonus finding** — the wrong-temperature data became a T=0.7-vs-T=1.0 sensitivity analysis (`L1060-1062`, ΔF1 ~+0.15, p<0.0001). Report the provenance if that sensitivity result is cited. |
| **E44** (L1279) | single-pass-384 executed at T=1.0, not 0.0 | **No.** Data archived, unused in any published analysis (`L1085-1086`); corrected rerun at 487 tiles. Disclose for completeness only. |
| **E45** (L1306; retyped 2026-07-28 to `Deviation (unregistered inference method adopted)`) | Permutation statistic macro→micro F1; corrected entry discloses the permutation method itself as unregistered | **Yes.** Different ΔF1 *and* different p-values for the same comparison — the erratum gives a worked case (`L1155-1158`): ΔF1 +0.015, p=0.019 micro vs +0.007, p=0.081 macro. A comparison that is significant under the reported statistic is not significant under the registered one. **See also §4, item 3 — the preregistration does not actually specify a permutation test at all.** |
| **E46** (L1388) | Primary buffer 20 m → 30 m | **Superseded** by E47. Matters only for artefacts generated between 2026-03-27 and 2026-03-29. Report the pair, not E46 alone. |
| **E47** (L1461) | Buffer reverted to preregistered 20 m | **Yes, favourably.** Restores registered alignment and (per `L1259-1263`) yields greater discrimination. Both tolerances reported. This is the model of how a deviation should be handled and is worth foregrounding. |
| **E49** (L1538) | H10 calibration on a cold-start production config | **Yes.** It "Changes which examples are identified as hard" (`L1320`) — so the hard-example library that H8 and H12 depend on is mined under different settings than registered. The dependency chain E49→E51→E52 should be stated once, together. |
| **E50** (L1568) | H10 holdout 60 → 327 tiles | **No adversely** — more power, calibration pool sizes unchanged (`L1356-1357`). Disclose as a scope change. |
| **E51** (L1591) | H8 re-run at 384 px / production carry-forward; Scale-16/32 re-enabled | **Yes.** H8 results are reported on a different pipeline (tile size, T, thinking, K, evaluation manifest — nine parameters change per the table at `L1381-1395`) than registered, and two previously-deferred conditions return. The original 512 px H8 and H8 v2 are **not comparable** and should not be pooled. |
| **E52** (L1693) | H12 re-run at production carry-forward; **trigger relaxed** | **Yes — this is the one to watch.** H12's registered trigger was "run if H8 shows library size matters" (`preregistration.md:1010`); H8 v2 returned null on all seven contrasts, so the erratum concedes (`L1503-1504`) "Strictly read, the trigger is not met" and runs H12 anyway for two stated reasons. **A registered trigger that was not met but was overridden is exactly the disclosure a preregistration-checking reviewer looks for.** It is defensibly argued, but it must appear in the deviations passage, not be left in the errata file. |
| **E53** (L1806) | Phase 3a-HIGH image track moved 512 px → 384 px, redesigned as a 2×4 matrix | **Yes.** The H3 image-track consensus result is on a different tile size and tile set than the H3 text-track result (`L1588`). Cross-track H3 comparisons at matched scope are not available from this pair. The erratum argues the replacement is "more informative" (`L1634`), which is fair — but it is a different experiment. |

**Three deviation clusters worth writing as narrative rather than as a list**, because they are
causally linked and reviewers will otherwise read three separate lapses where there is one decision:

1. **Evaluation-scale cluster** — E36 (60→340 tiles) → E50 (60→327 for H10) → E41 (Pro at 487) →
   E51/E52/E53 (everything re-run at 384 px). One decision (the corpus was too small to have power)
   propagating through the whole design.
2. **Buffer cluster** — E46 → E47. One excursion, reverted, both reported.
3. **Library-provenance cluster** — E11 (HP pool exhausted) → E12 (H9-C degraded) → E13 (H12
   deferred) → E49 (new mining config) → E51 (H8 v2, Scale-16/32 restored) → E52 (H12 undeferred,
   trigger overridden). One structural constraint and its eventual resolution.

### 3b. E58–E78 deviation-substance additions (refresh, 2026-08-17)

The refresh adds ten deviation-labelled entries (two bare, eight composite). One-line
dispositions, grounded in each entry's own Impact field:

- **E58** (bare) — the registered proposer prompt was never used; every PV run rode a
  substitute, measured conservative at N=1 and superior under consensus. Must appear wherever
  PV prompt provenance is described.
- **E59** (bare) — H2 Condition C has no result and no decision trail; the run-vs-disclose
  decision is queued behind a 1024 px pricing run (S134 walk, Group E).
- **E60** — the H7 escalation conditional was evaluated and not conducted; the trigger fired
  only on an unregistered corpus, within noise.
- **E62, E63, E65, E69** — unregistered extensions/parameter levels, none altering a registered
  study; E63's HIGH-thinking setting is constant within H9, so within-H9 contrasts stand.
- **E74, E75, E78** (omission-recorders) — registered obligations with no result: H6 (the only
  registered *confirmatory* hypothesis with no result, excluded from the family FDR at m = 7),
  H13 arms B–C, and the § 8.9 thinking-level verification. This is the disclosure set a
  preregistration-checking reviewer will look for first; the register carries them as
  `not-executed` disposition rows.

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
   `results/ci-metadata-registry.md:187` (commit `e20f3e18`). **Recommend a new erratum (the number E58 has since been taken — next free is E79) rather
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

Every count in this document was produced by parsing `protocol-errata.md`, not recalled: the
entry total, the distinct `Type` strings and their frequencies, and the per-entry line anchors
all come from a single pass over the file. Manifest counts quoted at compile time (322
conditions, 1,132 pass rows, 4,180 CI blocks, 18 analyses) come from parsing
`results/conditions-manifest.json`, `results/passes-manifest.md`, and
`results/analyses-manifest.json`, and are themselves compile-time vintage (the analyses register
now carries 32 rows under vocabulary v2). The absence claims (no permutation spec in the
preregistration; no `BCa` in the errata or decisions log; no H13/H14/H15 anywhere outside the
preregistration and its derived planning documents) are `grep -c` results, each re-runnable in
one command.

**Refresh verification (2026-08-17).** The E78-vintage recount was computed twice independently
— by the S135 clean-context auditor and by the executing session's parser — with an
initial two-entry disagreement traced to E31/E32's bulleted `- **Type**:` format (a third
derivation); after the format fix the two counts agree exactly (22/18/12/26 at E1–E78,
22/16/11/8 at E1–E57 today). The **heading** line anchors in §§ 2–3 (the `L` column and the
`(L###)` row keys) were re-derived programmatically against the current file (60 updated); the
17 **inline quote citations** inside § 3's interpretation cells (e.g. "`L639`", "`L1155-1158`")
were NOT re-derived and remain compile-time vintage — the 2026-08-17 blind verification
confirmed the quoted content verbatim inside the correct entries but found all 17 inline
anchors displaced by the file's growth. Treat § 3's inline `L###` as historical. Sections 4 and 5 retain compile-time `protocol-errata.md:<range>`
citations; ranges may have drifted with the file's growth. At refresh, E54's entry was re-read
in full (its 1,000-registered / 10,000-post-hoc split stands, with the 2026-07-28 attribution
correction to Decision 10) and E56's heading and thesis were confirmed against the entry
(operating points in-sample; binary verdict unaffected); § 5's prose was not otherwise
re-audited.

## Changelog

### 2026-08-17 (later) — Blind-verification corrections

Fresh-context verifier (Opus): all counts confirmed exact across
three independent derivations (zero counting errors; the E10/E37/E45
retype list proven complete by a full Type diff against the
compile-time vintage; all 78 heading anchors and Type strings
re-checked programmatically). Six findings, all citation hygiene,
corrected: header "five entries" → 26; § 3's 17 inline quote
anchors flagged as compile-time vintage with § 6's claim narrowed
to heading anchors; § 5's stale "(E58)" recommendation renumbered
(next free E79); the E59 label-vs-substance point added to § 1's
methods-draft diagnosis; the § 1 deviation-family boundary
harmonised with the "30" option.

### 2026-08-17 — Refreshed to E78 vintage (S135 analysis block, item 3)

**Refresh trigger**: the S134 D17 reconciliation added E74–E78 and the
`methods-draft.md` M.x deviation-tally sentence was flagged
`[unverified]` pending this refresh. Changes: title and header scope
E1–E57 → E1–E78; § 1 rebuilt as a two-vintage recount with the
composite-label families enumerated; § 2 extended with 21 rows
(E58–E78) and the three retyped rows (E10, E37, E45) corrected in
place; § 3 membership updated (E10 in, E37 out-with-superseded-note,
E45 relabelled) and § 3b added for the E58–E78 deviation-substance
entries; § 6 gains the refresh-verification paragraph; line anchors
re-derived programmatically (60 updated).

Numbers that moved (before → after):

| Claim | Compile (2026-07-27) | Refresh (2026-08-17) |
|---|---|---|
| Scope | E1–E57 | E1–E78 |
| Bare `Deviation` | 18 | 18 at E78 (16 within E1–E57 after retypes) |
| Bare `Clarification` | 12 | 12 at E78 (11 within E1–E57) |
| Bare `Correction` | 22 | 22 (both vintages) |
| Composite/ad-hoc labels | 5 | 26 at E78 (8 within E1–E57) |
| Headline-count options | 18 / 20 / 22 | 18 / 27 / 30 |
| Recommendation | 20 + E56/E57 discussed | 27 + E56/E57/E74/E75/E78 discussed, or cite-individually (PI call, queued) |

What did NOT change: the three-way declared scheme; the § 3 cluster
narratives; §§ 4–5 content (compile-time citations retained, E54
re-read, E56 thesis confirmed).

### 2026-07-27 — Original publication

Compiled as part of the D17 inventory (Step 0): 57 entries parsed
programmatically, counts by verbatim Type, full table with line
anchors, the substantive-Deviation subset (20 rows), the no-clear-
hypothesis set, and the E54/E56 constraint notes.
