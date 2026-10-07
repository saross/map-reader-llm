# W1 documentation pass — report (2026-10-06)

Branch `register-repair`, not pushed. Every commit ends with the requested
Co-Authored-By line; explicit pathspecs only. Paper edits are drafted for the
PI's review, not finalised (each paper file's changelog says so). Other
sessions committed to the same branch during this pass (`c84cfa378`,
`ef9aa5cb2`, `9d3f7dbfa`, `35990bbf3`); none touched a file edited here.

## Per site

| Site | Before → after | Commit |
|---|---|---|
| E92 (new erratum; C-23, C-24) | none → records that the retest's Phase 2a-2d image arms ran canonical-first (YAML `fixed: ordering: canonical-first`, honoured since `ead94aa81`; February ran config order, 290 Feb metas carry no `ordering_override`), that `canonical-last` was sent `[null×3, HP×4, C+×4, C−×2]` not `[HP, null, C+, C−]`, and that E70's out-of-band patched tiles went in config order | `e8f793c16` |
| E81 table (C-06) | five 2c text rows read as conditions → annotation: with `phase2b::text-t0.0`, six runs of one configuration | `2d01bddc8` |
| Retest summary (C-01) | §§ 1, 5.2, 11.4 "scale-4 > plus-hp on text, p = 0.001" → struck through + WITHDRAWN note (identical requests; tile-swap p 0.0588, BH 0.588) | `5fef977a2` |
| Retest summary (C-02) | :23, :30, :302, :316, :320 "either/both tracks" → image track only | `5fef977a2` |
| Retest summary (C-21) | § 14.5 "Gemini 2.0 Flash" → Gemini 3 Flash (`gemini-3-flash`) | `5fef977a2` |
| Retest summary (C-25) | every quoted p bootstrap → permutation (D42); § 11 tables gain BH-within-phase and keep the retired value; config-default > random and image T0.7 > T1.3 withdrawn; 24/70 → 21/70; § 5.1 "all p > 0.19" corrected | `5fef977a2` |
| Retest summary (C-17, C-23, C-24) | canonical-last → "single run", "shares Tier 1", sent nulls first; § 2 example-order bullet; § 7 note that "baseline used in all prior phases"/"reused from Phase 2c" hold for February only (E92); caveats 9-10; Obs 498/499 cross-refs | `5fef977a2` |
| `pairwise-bootstrap-comparisons.json` (C-03) | D42 annotation existed but said nothing of replicates → top-level `_annotation_2026-10-06` (rows 40-49 are replicate contrasts; [45] a bootstrap false positive, tile-swap 0.0588); no value changed (round-trip verified) | `aafdea374` |
| `phase3d-experiment-e-results.md` (C-07) | Finding 2 live → struck + VOID note; E1→E2 and E4→Baseline rows bracketed; banner, changelog and original-publication stub added | `992f6e901` |
| `results/retest/phase2b/analysis_summary.md` (C-26 origin, S-12) | "p (FDR-adj)" column held raw bootstrap p; "Six of ten" → 5/10; permutation p + BH within track + retired column; caveat 1's pilot comparison corrected (pilot re-tested: 6/10 both tracks vs 5/5 here); banner + changelog | `6ffc4ff3e` |
| `results/phase2b-carry-forward-parameters.md` (C-26, S-12) | "6/10 … vs 6/10 and 4/10 in the pilot" → 5/10 and 5/10 vs pilot 6/10 and 6/10; p-values restated; banner + changelog | `6ffc4ff3e` |
| `results/factor-analysis/factor_analysis_results.md:337` (C-26) | "+0.072, FDR p = 0.004" → bracket: raw p of a non-registered row; permutation 0.0055 (BH 0.011); H7's registered T0.3 > T1.0 +0.096, p 0.0002. The 2026-08-02 changelog row (:406) left as dated record | `6ffc4ff3e` |
| Obs 498 (new) | Phase 2c text null + bootstrap FP (a); one sentence each on Obs 155, 157, 158 (C-08); Obs 280's `h4-canonical-last` is image (C-20, W4.3) | `d427f55d9` |
| Obs 499 (new) | Obs 187 correction under D43 (c); S-12 February pseudo-p (g); B-16 72 of 558 (h) | `d427f55d9` |
| E69 | annotation → item 3's "+0.010, p 0.001" superseded; re-test +0.018, p 0.0047 (re-sweep +0.015, p 0.0067); "decisive" withdrawn to "consistent with"; W2.7's question | `11da05d77` |
| Decisions log | dated note at **Decision 16** (not 25; see below): Phase 2c text void (E90), bootstrap p retired (D42), Track 2 ran 2d | `eec66505f` |
| `methods-draft.md` (C-11, C-12, C-13) | § M.10 prompt architecture rewritten (text-only sends nothing, zero-shot; verifier text variant sends six labels; the "above Reference Examples" sentence named); § M.9 "labels alone" → "transmit no exemplar at all" (:756 changelog bracketed, not rewritten); § M.11 Track 2 also ran 2d, retest ran 2c as five identical requests; DRAFT NOTE under the phase table (D42 values, S-12, E90/E92) | `c99e74cbb` |
| `methods-draft.md` § M.x (C-25) | family adjusted p H7 0.00233 / H4 0.217 / H1 0.248 → 0.00047 / 0.191 / 0.125 | `1499c1051` |
| `results-draft.md` § R2 (C-04, C-17/C-24, C-25, C-26) | 26 configurations / 9 in Tier 1 / six Tier-1 cells one text request; canonical-last single run, shares Tier 1, sent nulls first, ordering-check cited; H8 image-only on the board; eight undefined-MCC text cells = 3 configurations (14 text cells = 8); H1 p 0.1774/0.248 → 0.0715/0.125; H4 adj 0.217 → 0.191; H7 adj 0.00233 → 0.00047 and "+0.072 at FDR p = 0.004" → T0.3 > T1.0 +0.096, p 0.0002 | `e03b67522` |
| Claims inventory R2-01/02/04/07/09/10/11 | dated notes; R2-09..11 claim text and anchors re-anchored to the D42 regeneration; no status changed, census unchanged | `4f7f850c8` |
| `discussion-seeds.md` (C-15, C-16) | Seed 8 text-only variant named zero-shot; Seed 9 boundary E48 → v2 runs transmitted (Obs 236, 239, 240), retraction Obs 235; changelog also records the unlogged C-09 notes | `112a0d052` |
| E43, E68, E72 (C-25/C-26) | annotations: "FDR p=0.004" is a raw p of T0.7 > T1.0 (perm 0.0055, BH 0.011); E68's A[1] 0.004 → 0.0055, A[0] 0.38 → 0.42 | `9ed9a8d05` |
| Tracker ticks | C-01-04, C-06-08 (W1 half), C-11-13, C-15, C-16, C-20, C-21, C-23, C-24, W1.3-W1.5, W4.3 → [x]; C-25, C-26 left [ ] with PARTLY DONE notes and open sites; W1.1 and W1 left open; banner + changelog | `ea5cebeb7` |

All Markdown touched lints clean except pre-existing legacy in
`working-notes.md` (205 errors before and after; none in the new lines).

## Could not do / did not do (and why)

1. **Decision 25 note**: Decision 25 (moderate consensus for PV) already
   carries the 2026-10-05 E90 note and cites neither Phase 2c nor a
   bootstrap p; the Phase 2c/D42 note was put at Decision 16, where the
   "meaningless" judgement is. Decision 18 (Phase 2e config-default "reused
   from Phase 2c") could take an E92 pointer — not done (not a listed site).
2. **"baseline used in all prior phases" / "reused from Phase 2c" are not in
   the retest summary.** They are in `studies/retest/phase2e-h4-ordering.yaml:8`,
   `:32` and `outputs/retest/phase2e/study_manifest.json` (execution records,
   left as written). E92 and the summary's § 7 note explain them.
3. **W1.1 (register)**: `results/run-analyses.json` outcomes of
   `h1-cmt0106-pooled-modality` and `family-bh-fdr-confirmatory` still quote
   the bootstrap figures (H1 0.1774; H7 ≤ 0.001, adj 0.00233; H4 0.124/0.217;
   H5 0.756). The methods phase table copies them; it carries a DRAFT NOTE
   rather than edited cells.
4. **C-26 sites not edited** (variants of "FDR p = 0.004" outside the exact
   grep): `results/e43-matched-temperature/findings.md:40`, `:336`;
   `results/paper-tables/leaderboard-20m-annotated.md:288`, `:418`;
   `results/h11/analysis_summary.md:146`;
   `reports/e43-coverage-confound-remediation-2026-08-02.md:36`;
   `results/run-analyses.json` (E72 `_note`) and its three tiering-input
   snapshot copies (generated); working notes :6298, :24179, :24210, :24350
   (never edited).
5. **C-25 beyond the summary and § R2**: the W2 inventory's ~740 sites are
   not all done; e.g. the D17 audit `reports/d17-inventory/d17-inventory-h5-h8.md:905-919`
   (reads A[45] as falsifying the "identical prompts" rationale) is
   unannotated (Obs 498 records it). C-25 and C-26 are left unticked with a
   progress note.
6. **C-14a** (script note) and **C-08's W5 half** not in this brief.
7. No generated file was hand-edited (the docs edited are all hand-authored;
   generators `collect-factor-analysis.py` and `run_experiment_e.py` write
   `_autogen.md` siblings, not these files).

## Surprises (things the tracker missed or that did not match)

1. **Phase 2a also ran canonical-first.** `studies/retest/phase2a-h1-modality.yaml:32-34`
   sets `fixed: ordering: canonical-first`; Phase 2a ran on the batch path at
   `5a57f586e`, so its three image arms were reordered too. W3 and C-23 named
   only 2b, 2c and 2d. E92 covers 2a-2d. The reorder changed the sent order
   only for libraries with hard examples (17-example configs, plus-hp,
   scale-4, scale-8); canonical and pure-positive libraries are unchanged.
2. **Patched tiles went in config order.** `patch_failed_tiles()` at
   `d9361ea8e` (E70, run 2026-03-22) rebuilt requests from the meta's config
   snapshot with no reorder: 18 of 34 Phase 2a-2d image passes had 1-2 such
   tiles, and in Phase 2e `canonical-first` had 2 tiles (Elenovo x3584 y896,
   Lesovo x0 y1344) and `random` 1 sent in config-default order. Recorded in
   E92's scope note.
3. **Track 2 ran Phase 2d in February too** (`archive/outputs-pre-retest-60-tile/phase2d/track2-text/`,
   2026-02-11), so the methods draft's "Track 2 ran temperature testing and
   passed directly to Phase 3a" was wrong for both programmes, not only the
   retest.
4. **The origin of C-26 is `results/retest/phase2b/analysis_summary.md`**: its
   "p (FDR-adj)" column held raw bootstrap p-values, which is where "FDR
   p = 0.004" and "6/10" come from.
5. **S-12 reverses a stated comparison**: the carry-forward note's "the
   retest sharpens the pattern (6/10, 5/10 vs pilot 6/10, 4/10)" becomes
   5/10, 5/10 vs pilot 6/10, 6/10. Also, February text ranks T1.0 above
   T1.3 significantly (+0.041, p 0.007) where the retest ranks it below
   (−0.036, p 0.25): opposite signs across executions (in Obs 499).
6. **Era-1 board text counts**: the 14 text cells are 8 transmitted
   configurations (groups 16 and 13: Phase 2a brief-text ≡ 2b text-t1.0); the
   8 undefined-MCC text cells are 3. Verified from
   `reports/manipulation-check-2026-10-05-arms.json` flags against
   `tiering_20m.json`.
7. **`reports/manipulation-check-2026-10-05-arms.json` still flags group 19
   as plus-hp ≡ `config-default`**; the report body was corrected to
   `canonical-first`, the per-arm JSON was not.
8. **`tiering_20m.json` holds a 20-member `tie_set`** (generated 2026-06-08)
   while the register row holds 15 (E83). Noticed, not checked.
9. **Claims inventory R2-09..R2-11 say SIGNED**; the register records those
   analyses unsigned (recorded in the inventory's changelog, statuses not
   changed).
10. **Obs 280's claim was already inconsistent** with its own table (Era-2
    single-pass+PV's F1 leader is an image cell); with C-20 corrected the
    text-F1/image-MCC split holds in 3 of 5 divergent strata.
11. **The retest summary's § 14.5 "Gemini 2.0 Flash" survived the 2026-06-05
    model correction**, and its § 5.1 "all p > 0.19" was false on its own
    numbers (A[34] 0.076).
12. **Methods draft M.x errata range** still reads E1-E87 (now E1-E92);
    not changed (the M.x tally refresh is separate).
