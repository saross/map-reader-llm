# D42 implemented: every contrast by permutation

> **Last revised**: 2026-10-06 (class B re-tested under D43/D44). See
> [§ Changelog](#changelog) for revision history.

**Status: code, regeneration and findings DONE; the batch signature note
APPROVED by the PI 2026-10-05T11:34:51Z and recorded on the four analyses;
class B (§ 6) next.** Tracker item W2.6
(`planning/text-track-transmission-2026-10-05.md`).

## 1. The ruling

PI ruling D42 (2026-10-05, `planning/pi-decisions-2026-09-20.md`): every
contrast is tested by the paired tile-swap permutation test with
Benjamini-Hochberg (BH) correction; no p-value is read from a bootstrap.
Bootstrap confidence intervals (CIs) stay. The PI added two scope rulings
in Session 161: regenerate on sapphire with one batch signature note
(annotating the March pairwise file, which has no producer), and include
the February 60-tile instrument.

Implementation defaults the PI accepted (Session 161): precision and recall
are tested on the same swap mask as F1; the 2 × 2 interaction swaps the two
factor-level pairs per tile; H1's pooled contrast permutes the five
condition labels within each tile; a p of exactly 0 is kept as computed and
written "< 0.0001" in prose.

## 2. Code: seven paths, one kernel

`scripts/lib_permutation.py` (`86ab4828a`) is the one array-level kernel.
On single-run arrays it reproduces the signed boards' kernel
(`n1_baseline_leaderboard_tiering.permutation_test_float`) bit for bit, at
3, 40 and 300 discordant tiles, on integer and float counts
(`tests/test_lib_permutation.py`). Its BH wraps the boards'
`apply_bh_correction`, so there is one BH.

| # | Path | What it did | Now | Commit |
|---|---|---|---|---|
| 1 | `lib_advanced_metrics.bootstrap_effect_size_ci(return_p_values=True)` | 2 × min tail, floor 1/B | permutation p on the same per-tile counts, tiles sorted (the bootstrap's tile list followed the hash seed) | `06c71b39e` |
| 2 | `compute_family_fdr.py` (H1; H4/H5/H7 inputs) | bootstrap p; H4/H5/H7 read the March bootstrap | H1 by within-tile label permutation; H4/H5/H7 read the March permutation re-test | `12ad4c4b8` |
| 3 | `e45_bootstrap_pairings.paired_bootstrap` (also H6) | 2 × min tail, floor 1/B | permutation p beside the CI | `3c3023f51` |
| 4 | `h13_overlap_analysis.paired_bootstrap` (grid, grid verifier, incumbents, stride) | 2 × min tail, floor 1/B | permutation p beside the CI | `d41bc09d4` |
| 5 | `grid_analysis.paired_interaction` | 2 × min tail, floor 1/B | per-tile swap of the factor-level pairs | `d41bc09d4` |
| 6 | `analyse_phase2_results.apply_fdr_correction` (February instrument, Decision 10) | "pseudo-p" = 0.05 minus the CI bound, fed to BH | BH on run-block permutation p; refuses a comparison without one | `88edfd312` |
| 7 | `evaluate_retest_all.pairwise_effect_sizes` (found this session) | "significant" = CI excludes zero, uncorrected | permutation p, BH within the phase | `9b241426a` |

Two tests pinned the retired behaviour (identical arms at the 1/B floor);
both now assert the permutation result (identical arms give p = 1). Not
converted: `lib_phase4_transfer.ci_excludes_zero`, a CI-excludes-zero flag
in the H6 transfer analysis, which never ran.

## 3. Regeneration and annotation (sapphire, 2026-10-05)

The runner, its step log and the diff helper are in
`reports/d42-implementation-2026-10-05-scripts/`. Every regenerated file
was diffed field by field against its committed version before commit;
only p-value fields were allowed to move.

| Artefact | Treatment | Commit |
|---|---|---|
| `results/family-fdr/` (H1, family) | regenerated | `5986316b5` |
| `results/e45-bootstrap-pairings/e45_bootstrap_pairings.json` | regenerated | `5986316b5` |
| `results/h13-overlap-2026-08-18/h13_overlap_analysis.json` | regenerated | `5986316b5` |
| `results/grid-2026-08-18/grid_analysis.json` | regenerated; the `verifier_costing` block kept as committed (§ 5.4) | `5986316b5` |
| `results/grid-2026-08-18/verifier_analysis.json` | regenerated; the `conditions` block kept as committed (§ 5.4) | `5986316b5` |
| `results/grid-2026-08-18/incumbents_common_footprint.json` | regenerated | `5986316b5` |
| `results/stride-2026-08-25/stride_verifier_analysis.json` | regenerated after restoring two contrasts the script lacked (`7aef6d2ff`) | `5986316b5` |
| `results/retest/pairwise-bootstrap-comparisons.json` (70 rows) | annotated from W2's re-test (`permutation_retest` blocks) | `8908bad23` |
| `results/retest/phase2*-evaluation.json` (9 files, 61 rows) | annotated, not regenerated (§ 5.3) | `5f02cfbc2` |
| February 60-tile Phase 2 analyses (8) | re-run to `results/d42-retest-2026-10-05/feb-60-tile/`; the archive untouched | `35f9814d7` |
| Five findings documents | body p-values updated, banner and changelog | `0926e5627` |

## 4. What changed

### 4.1 Verdicts at α = 0.05 (after the relevant BH)

| Where | Contrast | Before | After |
|---|---|---|---|
| March retest (A[45]) | Phase 2c text: plus-hp vs scale-4 | significant (bootstrap p 0.001) | not (permutation 0.0588, BH 0.588) |
| Retest evaluations (uncorrected CI) | Phase 2a image-only vs verbose-text | significant | not (p 0.0573, BH 0.143) |
| Retest evaluations | Phase 2b image, T0.7 vs T1.3 | significant | not (p 0.0588, BH 0.094) |
| Retest evaluations | Phase 2b text, T0.7 vs T1.3 | significant | not (p 0.0535, BH 0.089) |
| Retest evaluations | Phase 2c text, plus-hp vs scale-4 (A[45] again) | significant | not |
| February 60-tile (pseudo-p) | Phase 2b text, T0.3 vs T1.0 | not | **significant** (p 0.0132, BH 0.022) |
| February 60-tile | Phase 2b text, T1.0 vs T1.3 | not | **significant** (p 0.0070, BH 0.014) |
| February 60-tile | Phase 2e config-default vs random | not | **significant** (p 0.0095, BH 0.029) |
| February 60-tile | Phase 2e canonical-last vs random | not | **significant** (p 0.0096, BH 0.029) |

**Surprise: the February pseudo-p was conservative, not liberal.** The
retired retest bootstrap over-rejected at sparse discordance (W2); the
February "0.05 minus the CI bound" construction did the opposite, and four
contrasts that real p-values pass were never declared. None of them is a
carry-forward input: Decisions 16-18 carried forward the highest-F1
condition, not a significance verdict, and H4's primary
(canonical-first vs canonical-last) stays null at 60 tiles (p 0.333).
They do bear on prose that called those February contrasts null.

**Unchanged**: the H-family rejection set {H2, H3, H7}; H4, H5, H7; every
grid, H13, stride, incumbent and E45 verdict; every Δ, CI and F1 in the
regenerated artefacts.

### 4.2 p-values that moved in signed analyses

| Analysis (signed) | Contrast | Before | After |
|---|---|---:|---:|
| `e45-bootstrap-pairings` | H2, H3 (B = 1,000 / 10,000) | 0.001 / 0.0001 (floors) | < 0.0001 |
| `h13-overlap-2026-08-18` | A − B (B = 10,000 / 1,000) | 0.0416 / 0.0500 | 0.0385 |
| | A − C, B − C | 0.0001 / 0.0010 (floors) | < 0.0001 |
| `grid-tilesize-overlap-2026-08-18` | overlap at 512, at 384; tile size at 50 % | 0.0001 (floor) | < 0.0001 |
| | tile size at 12.5 % | 0.0001 (floor) | 0.0002 |
| | interaction (quoted in the outcome) | 0.4902 | 0.4681 |
| `grid-postverifier-2026-08-18` (all quoted in the outcome) | post-verifier tile size 12.5 % / 50 % | 0.034 / 0.2308 | 0.0373 / 0.2353 |
| | post-verifier overlap 512 / 384 | 0.0004 / 0.0208 | 0.0003 / 0.0235 |
| | post-verifier interaction | 0.2336 | 0.2257 |
| | K = 10 baseline tile size 12.5 % / 50 % | 0.2808 / 0.0886 | 0.2975 / 0.0939 |
| | K = 10 baseline overlap 512 / 384 | 0.0004 / 0.0026 | 0.0008 / 0.0032 |

Unsigned: `h1-cmt0106-pooled-modality` (outcome quotes p = 0.1774, now
0.0715) and `family-bh-fdr-confirmatory` (inputs as in
`results/family-fdr/family_fdr.md` § 2).

## 5. Caveats

1. **H1's permutation tests a sharper null than H1.** Shuffling five
   condition labels per tile tests "all five interchangeable", not "group
   means equal"; within-group gaps here (brief-text 0.552 vs verbose-text
   0.502; image-only 0.469 vs about 0.52) are as large as the contrast.
   H1 moved from 0.1774 to 0.0715 (BH 0.125): not rejected either way, and
   its bootstrap CI includes zero. A test of H1's own null would need a
   different design (for example, permuting only within matched
   elaboration pairs); not done.
2. **The tile-swap test compares outputs, not configurations** (S-10,
   tracker W2.7). D42 fixes the bootstrap's defect; it does not add
   run-to-run variance. The February re-test averages ten runs per arm,
   which narrows but does not close the gap.
3. **The nine retest phase evaluations were annotated, not regenerated.**
   Re-running `evaluate_retest_all.py` today re-scores per-condition F1 by
   up to 0.0059 (evaluator changes since March, BCa CIs), which would have
   rewritten published point estimates. Their permutation p-values were
   computed on the current input files.
4. **Two blocks were carried over unchanged** in regenerated files because
   other code writes them: `verifier_analysis.json` `conditions` (the
   separate `--materialise-conditions` mode) and `grid_analysis.json`
   `verifier_costing`. A fresh run of the latter picks up the WP4b uniform
   re-pricing (verifier per-call US$0.000693 → 0.000692, every option about
   0.15 % lower): a currency gap for W6.3, not D42.
5. **Archive defects met on the way** (repaired only in a `/tmp` copy): the
   February Phase 2b detection files have no `.geojson` suffix (the "." in
   `T1.3` stood where the extension should be), so loaders skip them; the
   Phase 2e `config-default` symlinks broke when the outputs moved into
   `archive/`.

## 6. Not yet done

1. **Class B: DONE 2026-10-06** under rulings D43 and D44 (`e7b32de0b`;
   re-run records `results/d42-retest-2026-10-05/class-b/`; script
   `scripts/annotate_classb_permutation.py`). Every committed file is
   annotated in place after a point-estimate check. Results: the six
   384-vs-512 contrasts stay significant (I4 0.006 → 0.007 on the March
   sweep; 0.0111 on the E39 sweep, 512 px F1 0.7701, the figure to cite);
   the PV pairwise files have one raw-α flip (checklist-text vs brief-text,
   0.034 / 0.046 → 0.0527, which now agrees with "the three strategies are
   statistically equivalent"); the Phase 3a HIGH-text pairs keep every
   verdict; B-17 stays significant as run (0.001 → 0.0047) and re-swept
   (minimal threshold 0.15, p 0.0067), with the stale variant summary
   flagged; B-18 stays null (0.166 → 0.1626). B-16 (`pairwise-384px.json`)
   is NOT re-testable: the current per-tile scorer refuses its 512 px
   detections on the 384 px frame (72 of 558 credited), the defect its
   March tables carried silently; it carries a note and should not be
   cited. Was: **Class B (needs the PI).** The PV pairwise files, `fair-384-vs-512.json`,
   `phase3a-high-text-pairwise.json` and the two Pro-thinking comparisons.
   Their inputs were found (`reports/d42-implementation-2026-10-05-scripts/moved-inputs.md`,
   a read-only agent's search, spot-checked), but two choices are the PI's:
   - **B-17** (Obs 187, E69, PI ruling 1a): the committed variant row and
     the pairwise test appear to have read two different versions of one
     `probabilities.json`. The search infers, from timestamps and mean
     probabilities (not observed directly), that the March job was
     submitted twice and the file rewritten 33 s after the sweep loaded
     it; that would also explain the sign and estimand mismatch W2 found
     in Obs 187's "+0.010". Re-test as-is, or re-sweep the current file
     first (which changes B-17's inputs).
   - **I4** in the 384-vs-512 file: its 512 px threshold sweep was
     regenerated by E39 (`01c84b841`); re-test on the March sweep (git blob
     at `e686e695e`) or the current one.
   Also: `~/cc-scratch/bootstrap-cis/` on sapphire is untracked and holds
   the only copy of 85 pre-patch detection files those outputs used;
   archiving it is recommended.
2. **C-25's documentation sites** (about 740 sites, 30 in paper text):
   tracker W1, after the batch note.
3. **The analyses manifest**: regenerated when the batch note lands.

## 7. Draft batch signature note (for the PI)

One note, appended to each of the four signed analyses in § 4.2, in the D9
pattern; the analysis-specific CHANGED clause is § 4.2's rows for it:

> SIGNATURE NOTE 2026-10-05 (D9 pattern; re-testing; ruling D42, approved
> by the PI ‹timestamp›, Session 161). Every p-value in this analysis's
> artefact is now the paired tile-swap permutation test's
> (`scripts/lib_permutation.py`; 10,000 permutations, seed 42; for a 2 × 2
> interaction, a per-tile swap of the two factor-level pairs), not the
> bootstrap's 2 × min-tail p, which D42 retired; the artefact was
> regenerated on sapphire (`5986316b5`). CHANGED: ‹the analysis's rows from
> § 4.2›. UNCHANGED: every Δ, CI, F1 and verdict at 0.05. The outcome text
> keeps its signed figures; the regenerated JSON carries these. The
> signature of ‹date› stands; the PI approves the re-tested p-values as of
> this note. Walkthrough: `reports/d42-implementation-2026-10-05.md`.

## Changelog

### 2026-10-06 — Class B re-tested (D43, D44)

§ 6.1 records the class B re-test and its results; B-16 is not
re-testable and is flagged.

### 2026-10-05 (later) — Batch signature note approved

The PI approved § 7's note as written (2026-10-05T11:34:51Z). It is appended
to `signature.attests` of `e45-bootstrap-pairings`, `h13-overlap-2026-08-18`,
`grid-tilesize-overlap-2026-08-18` and `grid-postverifier-2026-08-18` in
`results/run-analyses.json`, each with its § 4.2 rows and its prior text in
`history`.

### 2026-10-05 — Original publication (Session 161)

Written after the D42 code (seven paths), the sapphire regeneration and
the findings updates, for the PI's batch signature note.
