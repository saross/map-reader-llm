# Closing the recovery-fragment drop: five unions rebuilt, four cells re-scored

> **Last revised**: 2026-09-13 (original publication). See
> [§ Changelog](#changelog) for revision history.

**Verdict in one line.** The PI's "fix properly" ruling of 2026-09-13 is
executed. Five committed consensus unions were rebuilt with the fixed builder and
every count the measuring report predicted reproduced exactly; four registered
conditions were re-scored on their recorded recipes; **the whole numerical
consequence of the defect across the repository is one added false-positive
detection**, worth **−0.0010 F1** on a single cell that the Era-2 board already
withholds. Four verifier calls were made, **US$0.002784** audited on the corpus
flex basis, which is what the PI approved and the only spend incurred.

Three things the ruling did not anticipate came out of doing it, and each is
flagged for the PI in § 6 rather than smoothed over: one of the four approved
calls was **confirmatory rather than necessary**; six carried probabilities sit on
a crop shifted by one pixel, one of them the sole sensitivity in a claimed zero
delta; and the three Gemini 3.7 gold-standard cells **can no longer be scored at
all** by `scripts/evaluate_detections.py`, which blocks repair of the one figure
that moved.

Everything below was measured on sapphire on 2026-09-13 in an isolated worktree at
`~/worktrees/map-reader-llm/claude-unions`, on branch
`worktree-agent-a41b647e2345bdb44`.

## 1. What was wrong, and what the fix does

`resolve_pass_files` derived a pass directory's number by stripping the prefix and
casting the remainder, so `int("2_recovery")` raised `ValueError` and the
`except ValueError: continue` swallowed it in silence. A storm-recovery fragment
directory never reached the loader. The graver half was the denominator:
`merge_passes` sets `total_passes = len(raw_passes)` from the loader's output and
`load_pass_detections` keeps a pass only `if features`, so a pass whose main file
held an empty FeatureCollection vanished entirely and every vote threshold was
divided by the wrong number. Full mechanism, with file and line:
`reports/recovery-fragment-drop-2026-09-13.md` § 1.

The fix — `75d7c8d4cd55b6ec8d2a40abff70a31f62b67725`, *"fix(merge_passes): fold
run_N_recovery fragments into their pass"* — groups pass directories by the number
matched from `_PASS_DIR_RE` (`scripts/merge_passes.py:413`), appends each
fragment's files after the main directory's so within-pass deduplication still
prefers the main feature, keeps the main directory's name as the pass id, and
leaves the pass **count** unchanged. It was already on `main` at `fe73bb82b` when
this work began.

## 2. The five rebuilds

Rebuilt with the same `--passes` selections the committed builds recorded in their
own `experiment_intent.md` files — `1`, `1,2,3` and `1,2,3,4,5`.

| union | committed | rebuilt | Δ | predicted |
|---|---:|---:|---:|---|
| `gemini37-screen-…/consensus-n3/consensus_t1.geojson` | 757 | **759** | +2 | 759 ✓ |
| `gemini37-screen-…/consensus-n3/consensus_t2.geojson` | 608 | **609** | +1 | 609 ✓ |
| `gemini37-screen-…/consensus-n3/consensus_t3.geojson` | 529 | **530** | +1 | 530 ✓ |
| `gemini37-screen-…/consensus-n1/consensus_t1.geojson` | 640 | **640** | 0 | 640 ✓ |
| `grid-2026-08-18/g384_ov192/consensus-n5/consensus_t5.geojson` | 1,168 | **1,169** | +1 | 1,169 ✓ |

All five match. The grid pool's unaffected thresholds are also unchanged, in count
*and* in membership: T1–T4 at 2,932 / 2,025 / 1,650 / 1,396, with every candidate
matched.

`pass_provenance` is now the artefact-level signature of the fix. Each fragment
appears under its **parent pass's** id — `run_1_recovery` under `pass_id`
`run_1`, `run_4_recovery` under `run_4` — and `total_passes` still reads 1, 3
and 5. A fragment joins a pass; it never creates one.

### 2.1 Candidate preservation, measured rather than asserted

The ruling asked that every previously present candidate still be present at the
same coordinates. Matching pre-fix against rebuilt by projected position
(EPSG:32635, greedy nearest-neighbour, one-to-one):

**At the 20 m tolerance `merge_passes.py` itself clusters on, `absent_from_new`
is 0 for all nine rebuilt threshold files.** Nothing was lost.

At a strict 2 m tolerance two screen-pool candidates read as absent-and-new, and
both are the same mound displaced, because a fragment contributed a co-located
detection that moved the cluster centroid:

| union | displacement | what it is |
|---|---:|---|
| `consensus-n1/consensus_t1` | 3.026 m | same source tile, vote count unchanged at 1 |
| `consensus-n3/consensus_t1` | 9.551 m | same source tile, vote count 1 → 2 |

The genuinely new candidates are three, all in `consensus-n3`: the vote-promoted
one above plus two at (24.761750, 42.290037) and (24.920161, 42.274606). In
`consensus-n5` the entire effect of the pool's 14 dropped features is one cluster
promoted from 4 votes to 5 — `candidate_01335` at (26.513551, 41.879916), source
tile `K-35-078-1_Lesovo_x192_y2496.png`.

**A displacement census the earlier report did not carry, and it matters.** Among
*matched* candidates, `consensus-n1/consensus_t1` moved 4 of 640 and
`consensus-n3/consensus_t1` moved **52 of 757** (51 of them by ≤ 1.334 m),
`consensus-n5/consensus_t1` 1 of 2,932. At the sheets' ground resolution of
**5.02 m/px** (measured: `K-35-062-2_Rakovski` 5.0188, `K-35-052-4_32635` 5.0102,
`K-35-078-1_Lesovo` 5.0315) a 1.334 m shift is **0.27 px**, so these are almost
all sub-pixel. That census is what made a correct, cheap coverage test possible —
see § 3.

## 3. The four verifier calls

A rebuilt union re-numbers its candidates, so a committed `probabilities.json`
keyed to the old numbering cannot be read against the new crops manifest. Three
**new** stage directories were created beside the committed ones; no committed
`probabilities.json` was touched.

Coverage was decided on the **integer crop window**, not on metric distance
alone, because `extract_candidates._crop_from_raster` builds its window from
`rasterio.DatasetReader.index`, which floors the projected centroid to a whole
(row, col). Two candidates whose centroids differ by less than a pixel therefore
usually get a byte-identical crop, and a carried probability for such a candidate
is exactly valid rather than merely close.

| stage | extends | carried | calls | audited flex |
|---|---|---:|---:|---:|
| `…/g384_ov192_g37/verify_k1_recovery-fixed` | `verify_k1` (640) | 639 | **1** | **US$0.000757** |
| `…/g384_ov192_g37/verify_k3_recovery-fixed` | `verify_k3` (757) | 756 | **3** | **US$0.002027** |
| `…/g384_ov192/k-ladder/k5_recovery-fixed` | `k-ladder/k5` (2,932) | 2,932 | **0** | **US$0.00** |
| | | | **4** | **US$0.002784** |

The uncovered sets reproduce the measuring report's exactly: 1 for K = 1 and 3
for K = 3, at the same positions; and **0** for tier E, confirming its US$0
re-score. Audited on the basis every cost column in the corpus uses — input ×
0.25/1e6 + (output + thoughts) × 1.50/1e6, via
`run_k_ladder_phase2_verifier.audited_flex_usd` — against a list basis of
US$0.005567. The report's estimate was US$0.0028.

**Instrument, unchanged and not overridden**: `verify_adversarial-text`,
`gemini-3-flash` resolving to `gemini-3-flash-preview`, system instruction
`verify_adversarial.md` (hash `2518d5298d9b84bac6810bb0d11e59ef534c46853f65cb25dc1454af3497e15d`),
temperature 0.0, thinking MINIMAL, 1 iteration, no examples, real-time flex — all
read back from each committed stage's own `run.meta.json`. Crop extraction: 640,
759 and 2,932 crops, **0 tile fallbacks** in every case, so the E33 guard holds.

The calls were isolated to exactly the uncovered candidates by seeding each new
stage's `probabilities.json` with the carried results and letting `run_pv.py`'s
own resume filter (`scripts/run_pv.py:1078-1091`) skip them; `all_results =
dict(existing_results)` at `:1102` is why the carried results survive into the
final file. Verified before spending: the filter would call 1 and 3 times, with 0
orphan seeds.

### 3.1 What the verifier said

| candidate | stage | votes | probability |
|---|---|---:|---:|
| `candidate_00092` | K = 1 | 1 | **0.95** |
| `candidate_00523` | K = 3 | 2 | **0.0** |
| `candidate_00706` | K = 3 | 1 | **1.0** |
| `candidate_00707` | K = 3 | 1 | **0.0** |

None of the three K = 3 candidates enters that rung's scored set: all sit at 1 or
2 votes against a vote ≥ 3 gate.

## 4. The four re-scores

On each cell's recorded recipe: curator reference
`inputs/vectors/references/mounds-reference.geojson`, board frame
`inputs/vectors/bounds/384/era2_b_intersection_bounds.geojson` (487 tiles, 569
reference features in frame), 14 buffers 5…150, 10,000 BCa draws, seed 42, MCC,
tile-level resampling, EPSG:32635. Operating points by each family's own rule —
board-frame F1@20 argmax per ruling R2, or the carried point — chosen by the
committed drivers' **own** `argmax_at_headline`, with the tier-E carrier re-key
through `run_k_ladder_tier_e.reassign_carrier_tiles`.

| condition | F1@20 before | after | Δ | detections |
|---|---:|---:|---:|---|
| `gemini37-screen-2026-08-28::g37-text-k1-verified-opmax` | 0.8495 | **0.8495** | 0.0000 | 502 → 502 |
| `gemini37-screen-2026-08-28::g37-text-k1-verified-carried-p0.10-k1` | 0.8338 | **0.8338** | 0.0000 | 558 → 558 |
| `gemini37-screen-2026-08-28::g37-text-k3-verified-opmax` | 0.8870 | **0.8860** | **−0.0010** | 494 → **495** |
| `grid-2026-08-18::g384-ov192-k5-verified-opmax` | 0.8905 | **0.8905** | 0.0000 | 435 → 435 |

**Every "before" was re-derived in the same process as its "after" and reproduces
the committed value exactly.** That is the control that rules out the alternative
explanation — that a difference came from the scorer changing since 2026-09-12
rather than from the detections changing.

**No operating point moved.** All four argmaxes are where they were — (1, 0.15),
(1, 0.10) carried, (3, 0.10), (5, 0.15) — with **0 ties** each, and the board frame
and the Era-2 frame still agree on every one.

**Tier E's zero delta is now a measurement.** The rebuilt K = 5 cell's evaluation
is **dict-identical** to the committed one: F1@20 0.8905, precision 0.9130, recall
0.8690, BCa CI [0.8595, 0.9149], tile-MCC 0.8139, confusion tp 193 / tn 248 /
fp 10 / fn 36, 435 detections. The promoted `candidate_01335` carries probability
0.10 against that rung's prob ≥ 0.15 gate, so it never enters. The committed
artefact is already correct and was left untouched.

### 4.1 The one movement, decomposed

`g37-text-k3-verified-opmax` gains exactly one detection: `candidate_00049` at
(25.865733, 42.441604), source tile `K-35-052-4_32635_x1920_y960.png`, which the
fragment promoted from 2 votes to 3 so that it clears vote ≥ 3, at probability
1.0. It is a **false positive** — precision falls 0.8340 → 0.8323 while recall
holds at 0.9471 exactly.

So a fragment whose recovery was unambiguously correct data recovery made this
cell very slightly worse. That is the honest shape of the result, and it is not a
reason to doubt the fix: more data recovered, one more confident-but-wrong
candidate promoted past a vote gate.

### 4.2 A movement the headline buffer hides

The two K = 1 cells are unchanged at 20 m and at every buffer from 10 m up, but
both move at **5 m**, with no change in detection count:

| condition | F1@5 before | after | Δ |
|---|---:|---:|---:|
| `g37-text-k1-verified-opmax` | 0.4781 | 0.4760 | −0.0021 |
| `g37-text-k1-verified-carried-p0.10-k1` | 0.4693 | 0.4673 | −0.0020 |

The cause is the 3.026 m centroid shift of § 2.1 — far inside a 20 m match
radius, straddling a 5 m one. Recorded because a reader checking only the headline
buffer would conclude, wrongly, that these two cells are untouched.

## 5. The board, the register, and the documents

**The board is not rebuilt and not re-tiered**, per the ruling. Its
`provenance.json` already carried an unresolved `re_sign_pending` block, so a
second top-level key of that name is impossible; the note is nested inside it as
`cells_pending_rescore`, shaped like `tiering.withheld_cells`. The diff is **44
insertions and zero deletions**, guarded by an assertion that **16**
signature-bearing paths are byte-equal before and after — `signed_at`,
`signature_history`, `_carried_forward`, `finalised_at_utc`,
`gates.G1.pi_ruling`, the block's own `status`, `reason`, `signed_outcome`,
`proposed_outcome` and the two `*_n_conditions_compared`,
`tiering_membership_source`, `untouched_fields`, `previous_resolved`, and the
whole `tiering` and `membership` blocks.

**Why the asymmetry makes this safe.** Of the four cells, the only one whose F1
moves is one of the three already in `tiering.withheld_cells` — ranked and tested
nowhere, its whole-frame F1 quoted as reference. The one **tiered** cell of the
four, `g384-ov192-k5-verified-opmax` at rank 9, tier 2, MCB-admissible and
feeding 149 pairwise comparisons, re-scores dict-identically. So no rank, tier,
pairwise test, BH family or MCB admissible set is touched by a number that
actually changed.

The note is **mirrored into the board README's changelog**, because that is the
durable copy: `finalise()` overwrites a `PENDING` `re_sign_pending` block
outright rather than nesting it (`scripts/build_gs_era2_board.py:690-694`), so a
hand-added key inside it would not survive the very rebuild meant to pick these
cells up, whereas `finalise()` preserves an existing `## Changelog` (`:772-779`).

**`results/k-ladder-2026-09-12/findings.md`** § 7.3 is amended and its changelog
and banner refreshed. **No number in that document moves** — its F1@20 0.8495,
502 detections and tp 10 / fn 219 / MCC 0.1337 all belong to the K = 1 rung; § 4.3's
ladder runs K = 1 to K = 10; § 8.4's tier-E K = 5 row is unchanged; § 7.1's table
is aggregated by thinking level. The K = 3 figure that did move is quoted nowhere
in it.

**The uplift supplement needs no update**, verified rather than assumed. All four
conditions appear in it exactly once, in the `Excluded (153)` list under
`### Board-frame rows excluded` (`results/uplift-supplement/build-report.md:37`),
and in **zero** data rows of `conditions.csv`, `conditions-by-buffer.csv`,
`verifier-uplift.csv`, `verifier-uplift-mcc.csv`, `strata.csv`,
`transfer-pairs.csv`, `verifier-pairing-worklist.csv` or
`k1-gapfill-worklist.csv`. `era2-b-487` appears in no data row at all. The
exclusion is structural — `lib_uplift_supplement.BOARD_FRAMES` keyed on
`scope_override.test_set_id` (`:1227-1243`) — so it survives the re-score, and the
pool cross-check is clean too: `g384_ov192_g37` appears in 6 `conditions.csv`
rows, none of them one of the four.

**The manifest flow was run as a check, not a write.** `generate_post_run_report.py
--all --dry-run` reports **ALL VALID** (41 runs + 593 conditions + 1,317 passes +
67 analyses) with **no drift rows**. `--write` was deliberately not run: no
`evaluation.json` changed, so no manifest row would change, and a regeneration
would sweep in an unrelated signature-timestamp refresh on a signed analysis row,
which is the PI's to authorise.

## 6. Flagged for the PI

**6.1 One of the four approved calls was confirmatory, not necessary.** The K = 1
candidate was classified uncovered because its centroid moved 3.026 m, beyond a
2 m positional tolerance. At 5.02 m/px that is 0.60 px, and the crop window is
byte-identical either side — `(col_off, row_off) = (3177, 3192)` before and
after. The call returned **0.95**, exactly the committed value, because it was the
same image. **The right coverage test is the integer crop window, not a metric
distance.** Worth adopting the next time a union is rebuilt: it would have made
this US$0.000757 cheaper and, more usefully, it is the test that does not
mis-classify.

**6.2 Six carried probabilities sit on a crop shifted by one pixel.** Five of
K = 3's 756 carried results (displacements 0.237–0.999 m) and tier E's single
changed result (1.410 m) crossed a pixel boundary, so their crops are offset by
1 px from the ones their committed probabilities were measured on. They were
carried, not re-verified, because that is outside the approved spend. For the five
the argument from magnitude is strong — all carry 0.95 or 1.0 against a 0.10 gate.
**For tier E's it is weaker and it is the single sensitivity in that cell's
zero delta**: `candidate_01335` carries **0.10** against a **0.15** gate, below
but not far below, and it now has 5 votes, so if a re-crop lifted it above 0.15 it
*would* enter. **One call, about US$0.0007, settles it.** Not spent; the PI's to
authorise.

**6.3 The three Gemini 3.7 gold-standard cells can no longer be scored at HEAD,
which blocks repairing the one figure that moved.** `evaluate_detections.py`
aborts on all three: the tile-join invariant refuses their per-tile table
(21 of 475 in-frame detections booked under the `id` join), and because the F1
bootstrap resamples *tiles* the refusal raises inside `bootstrap_ci` and takes the
whole evaluation with it, not just the tile-MCC block. Their committed evaluations
predate the invariant (`7ba47b63b`) and are no longer reproducible.

The concrete consequence: `g37-text-k3-verified-opmax`'s F1 has genuinely moved,
but its `evaluation.json` **cannot be regenerated**, so
`results/conditions-manifest.json` still carries 0.8870 / 494 and is stale by
−0.0010 / −1 detection. This report and
`results/k-ladder-2026-09-12/recovery-fix-2026-09-13/` are the record of the true
value until the artefact can be rewritten. **So the open tile-join ruling
(`reports/tile-mcc-geometric-join-2026-09-12.md`, still carrying a STOP) is now a
prerequisite for repairing these cells, not only for reporting them.** That is an
argument for raising its priority, and it was not visible before this job.

Those three cells were therefore re-scored on the **F1 arm only**, with the
confidence intervals and the whole per-tile block named **WITHHELD** in
`f1-only/*.json` rather than silently omitted — consistent with the board, which
already publishes only their whole-frame F1.

## 7. What did NOT change

- **`scripts/merge_passes.py`** — untouched here; the fix landed on `main` at
  `75d7c8d4c` before this work began.
- **Every committed `probabilities.json`, crops manifest and verifier
  `run.meta.json`.** The three new stages sit beside the old ones.
- **The tier-E cell's entire evaluation** — dict-identical, so its committed
  artefact was not rewritten.
- **Three of the four cells' F1 at the headline buffer**, and all four operating
  points, tie counts and frame agreements.
- **The Era-2 board's ranks, tiers, MCB admissible set, 153/150/3 counts, 14
  tiers, 7961/11175 significant pairs, tie set 5, Tier 1 and its five members,
  and every signature field.**
- **Every number in `findings.md`.**
- **The uplift supplement**, and its `Excluded (153)` count.
- **Every register row.** In particular the signed `k-ladder-2026-09-12` row in
  `results/run-analyses.json`, whose `outcome` prose an agent must not amend.
- **The 23 UNAFFECTED unions and the 106 unions of the September
  retrospective** — out of scope by the measuring report's disjointness argument.
- **API spend beyond the four approved calls: none.** US$0.002784 total.

## 8. Tests

`tests/test_committed_union_recovery_coverage.py`, **16 tier-1 tests**, asserts
that the five committed unions carry `pass_provenance` covering their recovery
fragments. It reads committed artefacts rather than rebuilding, so it is fast, and
it is written against all three ways the defect hid: the silent skip (coverage
assertions), the self-consistent wrong rebuild (absolute corrected counts), and
the count that did not move (`consensus-n1`, 640 either way).

Validated against the archived pre-fix artefacts: **all three pre-fix
`voting_summary.json` files fail the fragment-coverage assertion**, and
`consensus-n1` is caught by that assertion *alone*, since its count check passes
in both states. A premise test also fails loudly if the fragment directories are
ever moved, so the coverage assertions cannot pass vacuously.

## Changelog

### 2026-09-13 — Original publication

Executed the PI's "fix properly" ruling of 2026-09-13 on
`reports/recovery-fragment-drop-2026-09-13.md`.

| claim | before | after |
|---|---|---|
| `consensus-n3` T1 / T2 / T3 | 757 / 608 / 529 | **759 / 609 / 530** |
| `consensus-n1` T1 | 640 | 640 (one candidate displaced 3.026 m) |
| grid `consensus-n5` T5 | 1,168 | **1,169** |
| `g37-text-k1-verified-opmax` F1@20 | 0.8495 | 0.8495 |
| `g37-text-k1-verified-carried-p0.10-k1` F1@20 | 0.8338 | 0.8338 |
| `g37-text-k3-verified-opmax` F1@20 | 0.8870 | **0.8860** |
| `g384-ov192-k5-verified-opmax` F1@20 / tile-MCC | 0.8905 / 0.8139 | 0.8905 / 0.8139 |
| the two K = 1 cells' F1@**5** | 0.4781 / 0.4693 | **0.4760 / 0.4673** |
| API spend | US$0.00 | **US$0.002784** (4 calls) |

Five unions rebuilt, all counts as predicted; candidate preservation measured
(`absent_from_new` 0 at 20 m on all nine threshold files); three verifier stages
extended with 4 calls; four cells re-scored with every "before" re-derived as a
control; the board given a note-only `cells_pending_rescore` entry with 16
signature paths asserted untouched; `findings.md` § 7.3 amended with no number
moved; 16 new tier-1 tests, validated to fail on the pre-fix artefacts.

**Three findings flagged rather than smoothed over** (§ 6): the single K = 1 call
was confirmatory because coverage was tested on metric distance where the integer
crop window is the correct test; six carried probabilities sit on a 1 px-shifted
crop, one of them the sole sensitivity in tier E's zero delta and settleable for
~US$0.0007; and the three 3.7 gold-standard cells can no longer be scored at HEAD,
so the K = 3 cell's moved F1 cannot be written into its own `evaluation.json` or
its register row until the tile-join question is ruled on.

Landed on branch `worktree-agent-a41b647e2345bdb44`: archive `5a56ad248`, rebuild
`e9d1db0d0`, verifier stages `f8e0eb600`, re-scores `20c0a053f`, board note
`6291e9938`, findings amendment `35fe0b0f9`.
