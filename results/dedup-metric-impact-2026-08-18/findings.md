# Deduplication metric impact: MCC moves the other way, and the Tier-1 tie does not survive

> **Last revised**: 2026-08-18 (original publication — closes the three gaps
> the S136 scoring-sensitivity review left open). See
> [§ Changelog](#changelog) for revision history.

**Date**: 2026-08-18 (Session 136)
**Author**: Claude Code (Opus 5), amd-tower; all measurement executed on sapphire
**API spend**: US$0.00 — every number below is recomputed from committed
artefacts
**Scope**: the three gaps named in
[`reports/scoring-sensitivity-review-2026-08-18.md`](../../reports/scoring-sensitivity-review-2026-08-18.md)
§ 5 — no Matthews Correlation Coefficient (MCC) movement measured anywhere
(its gap 4), no confidence interval or permutation test re-run so no tie or
tier membership resolved (gap 1), and the six duplicate-exposed `consensus`
conditions never explained (gap 3)
**Artefacts**: this directory — four impact runs, ten tiering re-runs, the
consensus-mechanism diagnosis, and `findings-summary.json`

---

## TL;DR

1. **Deduplication moves F1 and tile-level MCC in OPPOSITE directions, in 40 of
   the 46 cells where it removes anything.** F1 @ 20 m rises by +0.0018 to
   +0.0578; MCC falls by as much as **−0.1818**. There is no cell in the
   measured set where both metrics move the same way.
2. **The entire MCC movement is an artefact of tile attribution, not of removing
   false positives.** Under a membership-preserving attribution — a tile counts
   as predicted-populated if any of its raw detections joined a surviving
   cluster — ΔMCC is **exactly 0.0000 in all 46 cells**. Deduplication answers
   an object-level question; tile-level MCC asks a per-tile question that the
   raw pass already answers correctly.
3. **A naive `--deduplicate` flag on `evaluate_detections.py` would silently
   degrade every MCC on every board.** Any such flag MUST attribute a cluster to
   all contributing tiles inside the tile-classification block. This is the most
   actionable result here, and it is testable
   (`tests/test_dedup_metric_impact.py`).
4. **The `diversity-dividend-384` Tier-1 tie does NOT survive.** Deduplicated,
   Tier 1 shrinks from three members to **two**, both Gemini-3-Pro single-pass
   cells; the Flash consensus champion is demoted to Tier 2 and the pair that
   carried the cross-architecture headline flips from non-significant
   (ΔF1 +0.0096, BH-p 0.6622) to **significant against it** (ΔF1 −0.0404,
   BH-p 0.0346). The registered claim "cheap Flash consensus reaches the
   expensive Pro single-pass tier on localisation F1" is not supported once the
   asymmetry is removed.
5. **The 55-map tile-MCC boards hold.** Their sole Tier-1 member `IM-k3` is the
   only duplicate-exposed cell on the board, but deduplication removes only 24
   of its 4,680 detections across 8,541 tiles and moves its MCC by **−0.0002**.
   Tier 1 stays `IM-k3` alone under both references.
6. **The `era1-leaderboard` sole Tier-1 leader becomes a two-member tie.**
   Deduplicated uniformly, the exposed challenger
   `retest-phase2b::verified-adv-text-t0.0` rises 0.7703 → 0.8128 and joins the
   unmoved committed leader (0.7925) in Tier 1; 225 of 3,321 pairs change
   significance. The prose "statistically clear of everything below"
   (`docs/paper/results-draft.md:218-224`) does not survive, though the
   verifier-lift argument it supports does.
7. **The six "exposed" consensus conditions were never un-deduplicated.** All
   six carry the exact `merge_passes.apply_threshold` property set, and **0 of
   their 193 residual within-20 m pairs share a contributing pass** — decisive
   evidence that within-pass deduplication ran. The residual is cross-pass
   greedy-star-clustering seed sensitivity, already documented in
   `cluster_across_passes`'s own docstring, and it decays to zero by a vote
   threshold of 3 or 4.
8. **A defect in the prior review's input resolution is corrected here.** Two
   conditions — one of them a Tier-1 tie member — were scored on 1 of their 3
   passes, because their pass pool mixes two file-naming conventions.

---

## 1. What this closes, and what it does not

The prior review established the exposure (155 of 333 conditions) and the F1
effect (48 re-scored cells), and named what it had not done. This document does
those three things. It does not revisit the exposure register, re-derive the
preregistration compliance reading (erratum
[E80](../../docs/methodology/preregistration/protocol-errata.md) and
`reports/dedup-gap-compliance-2026-08-18.md` hold that), or enumerate the full
blast radius (`reports/dedup-correction-worklist-2026-08-18.md` holds that).

The prior review's load-bearing claims, re-verified at source rather than
assumed:

| Claim | Verified? |
|---|---|
| `evaluate_detections.py` has no *spatial* deduplication step | **Yes** — the file's only `Deduplicate` mention is at `:1437-1442`, and it deduplicates the *tile list* for one detection (erratum E79's tie-break), not the detections themselves; there is no clustering anywhere in its scoring path |
| `merge_passes.deduplicate_within_pass` at `:137`, `DISTANCE_THRESHOLD_METRES = 20.0` at `:71` | **Yes** |
| `extract_candidates.py` crops one candidate per input feature with no clustering | **Yes** — the loop opens `for idx, feature in enumerate(features)` at `:315` and contains no clustering |
| 155 dedup-exposed / 123 tie-break-exposed / 6 in both, of 333 conditions | **Yes** — `exposure-survey.json` `summary` |
| `diversity-dividend-384` Tier 1 is a three-member tie at F1@20 m 0.8141 / 0.8045 / 0.7921 | **Yes** — `tiering_20m.json` `tie_set` and `ranking` |
| "recall is *exactly* unchanged in almost every cell" | **Yes, independently** — across the 55 cells measured here, Δrecall @ 30 m is exactly 0.0000 in 44 and never worse than −0.0023; Δprecision @ 20 m runs +0.0012 to +0.1159 |
| "the as-committed column reproduces the committed `evaluation.json` F1 to four decimal places in every one of the 48 cells" | **No** — one cell is out by 0.0157; see [§ 5](#5-a-defect-in-the-prior-reviews-input-resolution) |

---

## 2. Task 1 — MCC movement

### 2.1 Why tile-level MCC is not invariant under deduplication

`lib_advanced_metrics.calculate_tile_classification` classifies every evaluation
tile on two booleans: does any reference mound intersect it, and does any
detection carry its name in `source_tile`. Deduplication returns clusters, and a
cluster spanning two overlapping tiles has no single source tile —
`merge_passes.deduplicate_within_pass` records the whole `source_tiles` list and
leaves the choice to the consumer. Picking one tile *discards* the other tile's
evidence that the model reported something there.

The direction is not obvious a priori: emptying a tile with no reference mound
turns a false positive into a true negative (MCC up), while emptying one with a
reference mound turns a true positive into a false negative (MCC down). Which
dominates is the empirical question the prior review left open.

### 2.2 Three attribution rules, reported side by side

`scripts/dedup_metric_impact.py` scores each cell as committed and after
deduplication, reporting the deduplicated MCC under three rules:

| Rule | Definition | Why it is here |
|---|---|---|
| `first_source_tile` | the lexicographically first contributing tile | the rule `scoring_sensitivity_probe.dedup_geodataframe` already applies, so ΔF1 stays comparable to the prior review cell for cell |
| `nearest_centroid` | the contributing tile whose centroid is nearest the cluster centroid | the geometric rule `lib_advanced_metrics._assign_refs_to_primary_tiles` already applies to references |
| `union_contributing` | every contributing tile counts as predicted-populated | membership-preserving: the per-tile question is answered from the raw pass, so MCC should be invariant by construction |

F1 is insensitive to the choice because `calculate_f1_internal` matches per map
sheet and 20 m clusters do not cross sheets. Measured, not assumed: of the
**131,919** clusters formed across the gold-standard runs, **8,576** span more
than one tile and exactly **1** spans more than one map sheet (in
`e47-propose-brief::consensus-1of5`, at a sheet boundary).

Two gates back the numbers. The fast set-based tile confusion is checked against
`calculate_tile_classification` itself on the first cell of every run (identical
TP/TN/FP/FN and MCC). The as-committed arm is then checked against each cell's
`evaluation.json`:

- **F1** agrees to four decimal places in **58 of 59** cells. The exception is a
  rounding boundary (0.814673 against a stored 0.8146, absolute difference
  7 × 10⁻⁵), not a discrepancy.
- **MCC** agrees to three decimal places in **57 of 59**. One exception is
  another rounding boundary (0.40546 against a stored 0.4055, 4 × 10⁻⁵). The
  other is real: `retest-phase2b::text-t0.3` reproduces at 0.0665 against a
  committed 0.0443, because one of its three passes has an undefined MCC that
  the committed aggregation averages in as zero (§ 2.6).

### 2.3 Results

Fifty-nine cells were measured across four specifications: the 22-cell
`diversity-dividend-384` board, the 11 proposer-verifier `*-baseline*` cells of
`gs-era2-pv-family-30m`, the 20-member Tier-1 tie set of
`era1-single-pass-baseline-matrix`, and the 6 flagged consensus conditions.
Deduplication changes 55 of them; 9 of those have an **undefined** committed MCC
(§ 2.6) and are excluded, leaving **46 scorable cells**.

| Movement | n | min | median | max | positive | negative | zero |
|---|--:|--:|--:|--:|--:|--:|--:|
| ΔF1 @ 20 m | 46 | +0.0018 | +0.0259 | +0.0578 | **46** | 0 | 0 |
| ΔMCC, `first_source_tile` | 46 | **−0.1818** | −0.0532 | 0.0000 | 0 | **40** | 6 |
| ΔMCC, `nearest_centroid` | 46 | −0.1496 | −0.0464 | 0.0000 | 0 | 40 | 6 |
| ΔMCC, `union_contributing` | 46 | 0.0000 | 0.0000 | 0.0000 | 0 | 0 | **46** |

By board:

| Board / family | scorable cells | ΔF1 @ 20 m | ΔMCC (`first_source_tile`) |
|---|--:|---|---|
| `diversity-dividend-384` | 18 | +0.0169 … +0.0499 | −0.1039 … −0.0200 |
| `gs-era2-pv-family-30m` | 11 | +0.0126 … +0.0578 | −0.0692 … −0.0202 |
| `era1-single-pass-baseline-matrix` | 11 | +0.0182 … +0.0285 | −0.1818 … −0.1062 |
| exposed `consensus` conditions | 6 | +0.0018 … +0.0073 | 0.0000 (exactly) |

### 2.4 The sign disagreement

**Forty of the 46 scorable cells move in opposite directions: F1 up, MCC down.**
The six that do not are exactly the six consensus conditions, whose ΔMCC is
exactly zero because their residual pairs are within-tile ([§ 4](#4-task-3--the-six-consensus-conditions)).
So there is **no cell in the measured set where deduplication improves both
metrics, and none where it worsens F1**.

This is not noise. It is a deterministic consequence of the attribution step,
and the `union_contributing` column proves it: the same deduplication, scored
with cluster provenance retained, moves MCC by exactly nothing in all 46 cells.

### 2.5 The mechanism, at the level of the confusion matrix

The clearest case is a Tier-1 tie member,
`n1-pro-rerun-384::baseline-pro-text-high-t-0-0` (first pass, 487 tiles):

| Arm | TP | TN | FP | FN | MCC |
|---|--:|--:|--:|--:|--:|
| as committed | 188 | 247 | 11 | 41 | 0.7903 |
| deduplicated, `first_source_tile` | 181 | 248 | 10 | 48 | 0.7684 |
| deduplicated, `union_contributing` | 188 | 247 | 11 | 41 | 0.7903 |

Deduplication converts **one** false-positive tile to a true negative and
**seven** true-positive tiles to false negatives. The asymmetry is structural. A
mound in a 12.5 % overlap band intersects both tiles, so *both* are
reference-populated; collapsing its duplicate pair necessarily empties one
populated tile. Duplicates in genuinely empty tiles are rarer, because a
duplicate means the detector fired twice at one location, and such locations are
usually real mounds.

(The committed board reports 11 tile false positives for this cell — see the
`diversity-dividend-384` outcome text in `results/analyses-manifest.json` —
matching the as-committed row exactly, an independent check on this rebuild.)

### 2.6 Degenerate MCC on the Era-1 board

Nine of the 20 Era-1 cells have at least one pass whose committed tile confusion
matrix has a zero row or column: every tile in the 340-tile Era-1 scope carries
a detection, so TN + FP = 0 and MCC is undefined.
`calculate_tile_classification` returns `None`; `evaluate_detections` stores
`0.0` (`_safe_round`, `scripts/evaluate_detections.py:533-535`: "Round a value,
returning 0.0 for None (undefined MCC)"). Those cells therefore appear on the
board as MCC 0.0000 when the truthful statement is "undefined" — and worse, a
multi-pass cell with only *some* degenerate passes has its committed MCC pulled
toward zero, because `aggregate_runs` averages those zeroes in with the defined
values. `retest-phase2b::text-t0.3` is the measured case: one degenerate pass of
three gives a committed 0.0443 where the mean over its two defined passes is
0.0665. Deduplication empties enough tiles to make the matrix
non-degenerate, so a ΔMCC against them would measure the *appearance* of a
defined value rather than a change in discrimination; they are counted and
excluded rather than averaged in. **This is a pre-existing reporting infelicity
in the committed boards, independent of the deduplication gap, and worth fixing
separately.**

### 2.7 What this means for the paper's MCC claims

- The `diversity-dividend-384` outcome text asserts "F1-parity is NOT
  MCC-parity: the Pro text leaders are more tile-precise (MCC 0.790, 11 tile
  FPs) than the Flash consensus champion (MCC 0.620, 41 tile FPs)". Deduplicated,
  the Pro leaders fall to 0.7628 and 0.7487 while the consensus champion is
  unmoved at 0.6204. **The claim's direction survives; its margin narrows by
  about a fifth.**
- The § R3 55-map deployment table (`docs/paper/results-draft.md:398-405`) bolds
  the image cell's tile-MCC (0.712) as the metric-dependent winner, and that
  cell is the only duplicate-exposed row on the board. Measured, the movement is
  −0.0002 ([§ 3.3](#33-the-55-map-tile-mcc-boards)) — the claim is safe.
- **The `gs-era2-pv-family-30m` tile-MCC ordering does move.** Its top three MCC
  rows are all duplicate-exposed at 21–22 % pair involvement; two of them were
  in the measured set (`verified-adv-image-baseline-pro-vf` 0.8887 → 0.8562,
  `verified-adv-image-baseline` 0.8766 → 0.8392) and the third
  (`verified-adv-image-baseline-medium-vf`, 0.8848) was not. Their mutual
  ordering survives, but the third-ranked row falls **below** the unexposed
  `verified-adv-pro-image-pro-vf-3of5` (0.8499, 0.92 % exposure) and
  `verified-adv-image-min-3of5` (0.8461, 0 %) — an exposed-versus-unexposed
  crossover on the metric, and the reason any MCC-ordering claim drawn from
  that board needs the full 12 `*-baseline*` rows re-scored before it is
  reported.

---

## 3. Task 2 — tie-set and tier membership

### 3.1 Harness validation

`scripts/dedup_tiering_rerun.py` imports the committed boards' machinery
verbatim — `permutation_test_float`, `greedy_clique_tiers`, `micro_f1`,
`board_f1_at_20m`, `load_baseline_cells` from
`n1_baseline_leaderboard_tiering`; `apply_bh_correction` from
`apply_fdr_correction`; `tile_vectors`, `permutation_test_mcc` and
`mcc_from_confusion` from `mcc_tiering_55map`. Only the artefacts fed to the
per-tile statistic change. Everything runs at the registered settings: 10,000
permutations, seed 42, two-sided, Benjamini–Hochberg False Discovery Rate at
q = 0.05, greedy-clique tier merge.

Four controls establish that the harness is faithful:

| Control | Result |
|---|---|
| `--dedup none --rank-by eval_f1` | reproduces `results/diversity-dividend-384/tiering-champions/tiering_20m.json` **exactly**: all 7 tiers identical, tie set identical, and **0 of 231** pairwise significance decisions differing |
| `--dedup none --rank-by observed_micro_f1` | identical again — the ranking-key change alone (needed because a deduplicated artefact has no `evaluation.json` F1) moves nothing |
| 55-map `--dedup none` | the committed per-tile confusion matrices are reproduced exactly for all 8 cells (the board's own gate), and Tier 1 is `IM-k3` alone as committed |
| `era1-leaderboard --dedup none --rank-by eval_f1` | reproduces `results/era1-leaderboard/tiering_20m.json` **exactly**: all 10 tiers identical, tie set identical, 2,351 of 3,321 pairs significant as committed, and **0 of 3,321** significance decisions differing |

### 3.2 `diversity-dividend-384` — the Tier-1 tie does not survive

| Arm | Tier 1 | tiers |
|---|---|--:|
| committed (`tiering_20m.json`) | `consensus-flash-high-text-26of30`, `baseline-pro-text-high-t-0-0`, `baseline-pro-text-medium-t-0-0` | 7 |
| control, no deduplication | identical | 7 |
| **treatment, single-pass artefacts deduplicated** | **`baseline-pro-text-high-t-0-0`, `baseline-pro-text-medium-t-0-0`** | **8** |
| sensitivity, consensus champions deduplicated too | identical to the treatment | 8 |

The decisive pair — the one that carries the cross-architecture headline:

| Pair | ΔF1@20 m | p | BH-p | significant? |
|---|--:|--:|--:|:--:|
| consensus 26-of-30 vs Pro text HIGH T0.0, **as committed** | +0.0096 | 0.6163 | 0.6622 | no |
| the same pair, **deduplicated** | **−0.0404** | **0.0277** | **0.0346** | **yes** |

The Flash consensus champion falls to Tier 2, where it still ties the second Pro
cell (BH-p 0.1622) and two other Pro single-pass cells. The two Pro cells remain
mutually inseparable (BH-p 0.2179), so Tier 1 is a genuine two-member tie rather
than a new sole leader.

**Read this carefully.** A point-estimate reordering inside a statistical tie is
not a finding — a tie says the cells are not orderable. What has happened here
is stronger: the tie itself has broken. The permutation, run at the registered
settings on inputs whose scoring paths have been made symmetric, now separates
the Flash consensus champion from the Pro single-pass leader and puts the Pro
cell above it. The registered outcome sentence "Cheap Flash consensus reaches
the expensive Pro single-pass tier on localisation F1"
(`results/analyses-manifest.json`, `diversity-dividend-384` outcome) is not
supported on symmetric inputs, and the associated prose at
`docs/paper/results-draft.md` needs revisiting.

**Caveat, stated plainly.** Deduplicating a committed single-pass artefact after
the fact is exactly what preregistration § 8.5 Step 1 prescribes for a pass, so
this arm is the more protocol-faithful of the two. It is nevertheless a
re-scoring, not a re-run: nothing was re-detected. The comparison is now
like-for-like in the sense that every cell on the board has passed through 20 m
deduplication; it is not a claim about what the pipeline would have produced had
deduplication run before verification (the § R5 caveat in the prior review
applies unchanged to the proposer-verifier cells).

### 3.3 The 55-map tile-MCC boards

These boards were the newly identified risk: their sole Tier-1 member `IM-k3`
(`55maps-image-generalisation::verified-k3-*-gt`) is the only cell the exposure
register flags (1.05 % pair involvement, against 0.19–0.61 % for its
competitors), the boards rank on **MCC**, and the prior review cleared them on
an F1 movement of +0.0004. Measured on the ranking metric:

| Cell | committed MCC | deduplicated | Δ | features removed |
|---|--:|--:|--:|--:|
| `IM-k3` | 0.7104 | 0.7102 | −0.0002 | 24 of 4,680 |
| `T03-k3 (oracle)` | 0.6903 | 0.6892 | −0.0012 | 15 |
| `TH7-k3` | 0.6796 | 0.6796 | 0.0000 | 13 |
| `TM-n10-k5 (uplift)` | 0.6725 | 0.6722 | −0.0002 | 6 |
| `T03-k4` | 0.6711 | 0.6708 | −0.0002 | 1 |
| `TH7-k4 (carry-forward)` | 0.6666 | 0.6666 | 0.0000 | 0 |
| `TM-k3` | 0.6580 | 0.6577 | −0.0002 | 4 |
| `TM-k4` | 0.6411 | 0.6409 | −0.0002 | 1 |

**Verdict: the boards hold.** The five-tier structure is identical before and
after, **0 of 28** pairwise significance decisions change, and Tier 1 remains
`IM-k3` alone. The standardised-reference board behaves the same way (IM-k3
0.7120 → 0.7117; identical tiers; 0 of 28 changes).

The reason the effect is more than two orders of magnitude smaller than on
the gold-standard boards is scale, not kind: 24 removed detections can empty at most
24 of 8,541 tiles, whereas a gold-standard single-pass cell sheds ~10 % of ~450
detections over 487 tiles. The 55-map corpus is also scored at a 50 m buffer
while deduplication runs at the preregistered 20 m, so this measures the
preregistered merge, not a merge matched to the scoring tolerance.

### 3.4 The mixed-comparison audit

Cross-referencing every `tie_set` in `results/analyses-manifest.json` against the
exposure register gives five analyses with a duplicate-exposed cell inside their
tie set:

| Analysis | tie set | exposure | mixed? |
|---|--:|---|---|
| `diversity-dividend-384` | 3 | 1 unexposed consensus + 2 exposed Pro (0.213, 0.229) | **yes — resolved in § 3.2** |
| `n1-baseline-matrix-384` | 2 | both exposed (0.213, 0.229) | no — same-kind comparison |
| `era1-single-pass-baseline-matrix` | 20 | all 20 exposed (0.119–0.159) | no — but removal fractions differ by 1.6×, so within-tie ordering can move |
| `55map-canonical-leaderboard-mcc-50m` | 1 (`IM-k3`) | exposed, sole Tier 1 against unexposed challengers | **yes — resolved in § 3.3** |
| `55map-standardised-leaderboard-mcc-50m` | 1 (`IM-k3`) | as above | **yes — resolved in § 3.3** |

A sole-member Tier 1 is a mixed comparison whenever its challengers are
differently exposed, which is how the `era1-leaderboard` case
(`reports/dedup-correction-worklist-2026-08-18.md` TL;DR 2) enters the set: its
Tier-1 leader `retest-phase3a-high::verified-adv-text-high-t1.0-n30-23of30` is
unexposed while the challenger `retest-phase2b::verified-adv-text-t0.0` is
exposed at 20.5 % pair involvement. That case is resolved in
[§ 3.5](#35-era1-leaderboard--the-sole-tier-1-leader-becomes-a-two-member-tie).

### 3.5 `era1-leaderboard` — the sole Tier-1 leader becomes a two-member tie

The 82-cell definitive Era-1 board is reachable through the same tooling
(`--board analysis --analysis-id era1-leaderboard`), because
`scripts/era1_leaderboard_tiering.py` is already generic over
`conditions_compared`. Deduplication is injected by replacing that harness's
single `_per_tile_one_set` entry point, so the cell dispatch, CRS contract,
ranking, permutation and tiering stay identical; here it is applied
**uniformly** to every cell, which is the point — an asymmetric scoring path is
the confound being removed.

The control reproduces the committed board exactly: 10 tiers, the same sole
Tier-1 leader, and **0 of 3,321** pairwise significance decisions differing
(2,351 significant, matching the committed `era1-leaderboard` outcome text).

| Arm | Tier 1 | tiers | significant pairs |
|---|---|--:|--:|
| committed / control | `retest-phase3a-high::verified-adv-text-high-t1.0-n30-23of30` alone | 10 | 2,351 / 3,321 |
| **uniformly deduplicated** | **that cell plus `retest-phase2b::verified-adv-text-t0.0`** | 9 | 2,192 / 3,321 |

The committed leader does not move (F1@20 m 0.7925 → 0.7925; it is unexposed).
The challenger `retest-phase2b::verified-adv-text-t0.0` — exposed at 20.5 % pair
involvement — rises **0.7703 → 0.8128**, which takes the point-estimate top of
the board with it. The pair was never separable (BH-p 0.2731 as committed,
0.2866 deduplicated); what changed is that the challenger is no longer
significantly below the leader's other neighbours, so it joins the clique.
**225 of 3,321** pairs change their significance decision.

**Verdict: "the sole Tier-1 leader … statistically clear of everything below"
(`docs/paper/results-draft.md:218-224`) does not survive.** Tier 1 becomes a
two-member tie. Note what does NOT change: the leader remains in Tier 1, the
verifier-lift argument that sentence makes is untouched, and the two Tier-1
members are both proposer-verifier cells, so "proposer-verifier is the single
best Era-1 architecture" is if anything strengthened. What is lost is the word
*sole*, and with it the claim that the 30-call HIGH-thinking consensus plus
verifier is uniquely best — a three-call `verified-adv-text-t0.0` ties it.

---

## 4. Task 3 — the six consensus conditions

The anomaly: `merge_passes` applies the preregistered within-pass deduplication
at its Step 1 (`merge_passes.py`, `deduplicate_within_pass` at `:137`) before
cross-pass clustering, so a consensus artefact should carry no features within
20 m of one another. Six do. Three explanations were possible — a different code
path, a hand-built or weighted-box-fusion artefact, or a survey false positive.
`scripts/diagnose_consensus_dedup_exposure.py` decides between them from the
artefacts themselves.

**Finding: none of the three. Within-pass deduplication ran and worked; what
remains is cross-pass clustering order dependence.**

1. **Provenance.** All six artefacts carry exactly the property set
   `merge_passes.apply_threshold` writes — `subtype`, `confidence`,
   `vote_count`, `total_passes`, `contributing_passes`, `source_tiles`,
   `cluster_size` — and none carries a singular `source_tile`. They are
   `merge_passes` outputs, not hand-built sets and not a weighted-box-fusion
   path.
2. **Residual-pair anatomy, the decisive evidence.** Across the six artefacts
   there are **193** within-20 m pairs. **Zero** of them share a contributing
   pass. Two clusters that share no pass cannot be "one pass seeing the same
   mound twice through overlapping tiles" — which is precisely what within-pass
   deduplication removes. They are two *cross-pass* clusters whose mean
   centroids drifted within 20 m of one another after
   `cluster_across_passes` recentred them on the cluster mean (the seeds must
   have been more than 20 m apart, or greedy star clustering would have merged
   them). Their separations run 9.2–20.0 m, and **166 of 193 (86 %)** share a
   source tile, so they are mostly *within-tile* splits rather than
   overlap-band duplicates at all. This is the order dependence
   `cluster_across_passes` documents in its own docstring: "Cluster composition
   is order-dependent: different input orderings can produce different clusters
   for detections near the threshold boundary."
3. **Why exactly these six.** `apply_threshold` filters one cluster list by
   `vote_count >= K`, so the outputs across K are nested subsets of the same
   artefact and the residual can be recounted by filtering in place. Exposure
   collapses as K rises:

   | Condition | K=1 | K=2 | K=3 | K=4 |
   |---|--:|--:|--:|--:|
   | `consensus-384-t1-0::consensus-1of30` | 6.9 % | 3.2 % | 0 % | 0 % |
   | `e47-propose-brief::consensus-1of5` | 4.5 % | 2.5 % | 0.19 % | 0 % |
   | `n1-outstanding-384::image-t03-consensus-1of3` | 4.2 % | 0.6 % | 0 % | — |
   | `n1-outstanding-384::brief-text-t03-consensus-1of3` | 1.6 % | 0 % | 0 % | — |

   Every one of the six sits at K ∈ {1, 2}; every consensus condition in the
   study at K ≥ 3 carries no residual pairs at all. Low thresholds retain
   singleton clusters, which is where the drifted near-neighbours live: 129 of
   the 386 pair members are single-vote clusters, and no pair has two.

**Re-scored anyway, because the brief asked and it costs nothing.** Holding the
tile-assignment rule fixed across both arms (both derive `source_tile` by the
committed first-intersecting spatial join, so erratum E79's mechanism cannot
contaminate the measurement), an additional 20 m merge moves them by:

| Condition | removed | F1@20 m | → | Δ | ΔMCC (all three rules) |
|---|--:|--:|--:|--:|--:|
| `consensus-384-t1-0::consensus-1of30` | 3.4 % | 0.3038 | 0.3110 | +0.0073 | 0.0000 |
| `n1-outstanding-384::image-t03-consensus-1of3` | 2.1 % | 0.5822 | 0.5886 | +0.0064 | 0.0000 |
| `e47-propose-brief::consensus-2of5` | 1.3 % | 0.3868 | 0.3917 | +0.0049 | 0.0000 |
| `consensus-384-t1-0::consensus-2of30` | 1.6 % | 0.3977 | 0.4015 | +0.0038 | 0.0000 |
| `n1-outstanding-384::brief-text-t03-consensus-1of3` | 0.8 % | 0.4663 | 0.4692 | +0.0028 | 0.0000 |
| `e47-propose-brief::consensus-1of5` | 2.2 % | 0.1669 | 0.1687 | +0.0018 | 0.0000 |

The prior review's inference — "by analogy with H13 arm C the expected movement
is ≤ +0.006 F1" — is close but slightly optimistic: the largest is +0.0073 at
20 m and +0.0088 at 30 m. **ΔMCC is exactly zero for all six**, because these
residual pairs sit inside a single tile, so collapsing them cannot empty one.

**Interpretation.** These six are not evidence of a missing preregistered step.
Re-scoring them applies an *additional* cross-pass merge the protocol does not
prescribe at that point, so the deduplicated column above is a sensitivity, not
a correction. The exposure register's classification of them as "dedup-exposed"
is technically true of the artefact and misleading as to cause; the register
should carry the distinction.

---

## 5. A defect in the prior review's input resolution

`scoring_sensitivity_survey.resolve_detection_paths` expands a pass directory
with the glob the cell's evaluation record names, falling back to a wider
pattern only when that glob matches **nothing**. A batch evaluation records the
CLI *default* glob (`*/detections_*.geojson`), not the per-condition pattern from
its YAML, and two runs name their passes `detections-<config>-<date>.geojson`.
Where a pool mixes both conventions the primary glob matches something, the
fallback never fires, and the hyphenated passes are dropped silently.

Audited across all 333 conditions, **two** are affected — and one of them is a
Tier-1 tie member:

| Condition | resolved | actual | committed F1@20 m | prior review's "as committed" | error |
|---|--:|--:|--:|--:|--:|
| `pv-diag-384::baseline-pro-text-medium-t-0-0` | 1 pass | 3 | **0.7921** | 0.7764 | −0.0157 |
| `pv-diag-384::baseline-pro-image-medium-t-0-0` | 1 pass | 3 | 0.6555 | not re-scored | — |

Consequences, bounded:

- The prior review's claim that its as-committed column "reproduces the
  committed `evaluation.json` F1 to four decimal places in every one of the 48
  cells" is false for this one cell (the other three near-misses are 0.0001
  rounding).
- Its § 3.3(a) table gives the deduplicated value of that cell as **0.8211**;
  the correct three-pass figure measured here is **0.8415**.
- Neither condition's exposed/unexposed **classification** changes — both are
  duplicate-exposed either way — so the 155/123/6 exposure headline stands.
- The committed boards were never affected: `n1_baseline_leaderboard_tiering`
  already unions both patterns in its `PASS_GLOBS`.

`scripts/dedup_metric_impact.py` unions both patterns and additionally gates the
resolved pass count against the evaluation record's own `n_runs`, so a
recurrence fails loudly. Fixing the survey and probe themselves is left to
whoever owns those scripts; the register's exposure fractions for these two
conditions are measured on one pass of three and should be refreshed.

---

## 6. What remains unresolved

1. **Nothing here is a re-run of the pipeline.** Post-hoc deduplication of a
   committed artefact reproduces what § 8.5 Step 1 would have done to a *pass*,
   but not what a properly deduplicated proposer pool would have fed a verifier.
   The prior review's § 3.3 caveat stands unchanged for every
   proposer-verifier cell: the accepted set could differ in composition, not
   only in count. Answering that needs API spend and is not needed for any
   claim above.
2. **No bootstrap confidence intervals were recomputed.** The tiering re-runs
   settle tier and tie membership, which is what the permutation decides. The
   per-cell BCa intervals in each `evaluation.json` are still the committed,
   un-deduplicated ones; any figure or table quoting a CI beside a deduplicated
   point estimate would be mixing arms. Recomputing them is $0 but is a
   re-scoring campaign (`evaluate_detections.py` with a deduplication flag),
   not an analysis re-run.
3. **`era1-single-pass-baseline-matrix`'s 20-member Tier-1 tie was measured but
   not re-tiered.** Every member is exposed, so it is not a mixed comparison,
   but the removal fractions span 6.2–8.3 % and the committed F1 spread inside
   the tie is only 0.048, so within-tie ordering can move. Re-tiering it is one
   more `--board analysis --analysis-id era1-single-pass-baseline-matrix`
   invocation at $0.
4. **The other 108 exposed conditions are still un-re-scored**, as in the prior
   review. They are per-pass lineage rows no draft cites; the exposure register
   records their fractions so the selection can be audited.
5. **The degenerate-MCC reporting infelicity (§ 2.6) is unfixed.** Nine Era-1
   cells publish MCC 0.0000 where the honest value is "undefined". That is
   independent of deduplication and needs a decision from the PI about what a
   board should print.
6. **Two decisions remain with the PI**, unchanged from the prior review but now
   with one of them sharpened:
   - *Whether to add deduplication to `evaluate_detections.py`.* If it is added,
     the tile-classification block MUST use the union-of-contributing-tiles
     attribution, or every MCC on every board silently drops by up to 0.18
     ([§ 2](#2-task-1--mcc-movement)). A `--deduplicate` flag defaulting off,
     with an explicit re-scoring campaign run under it, remains the safer
     pattern.
   - *Whether the exposure register should distinguish "never deduplicated" from
     "deduplicated, with residual clustering order dependence"*
     ([§ 4](#4-task-3--the-six-consensus-conditions)). Six conditions are
     currently labelled in a way that implies the former when the latter is
     true.

---

## 7. Reproduction

Every step ran on **sapphire** (`ssh sapphire`, `~/Code/map-reader-llm`,
`source .venv/bin/activate`). Zero API calls; total wall clock about 25 minutes.

```bash
OUT=results/dedup-metric-impact-2026-08-18

# Consensus-artefact mechanism (Task 3)
python scripts/diagnose_consensus_dedup_exposure.py \
    --output $OUT/consensus-mechanism.json

# F1 + MCC impact (Task 1); specs name cells by condition_id and the script
# resolves paths, bounds and evaluation records from the conditions manifest
for S in diversity-dividend-384 gs-era2-pv-family era1-single-pass-board \
         consensus-exposed; do
  python scripts/dedup_metric_impact.py \
      --spec $OUT/spec-$S.json --output $OUT/impact-$S.json
done

# Tiering re-runs (Task 2): controls first, then the treatments
python scripts/dedup_tiering_rerun.py --board diversity-dividend-384 \
    --dedup none --rank-by eval_f1 \
    --output $OUT/tiering-dd384-control-none-evalf1.json
python scripts/dedup_tiering_rerun.py --board diversity-dividend-384 \
    --dedup none --rank-by observed_micro_f1 \
    --output $OUT/tiering-dd384-control-none-microf1.json
python scripts/dedup_tiering_rerun.py --board diversity-dividend-384 \
    --dedup single-pass --rank-by observed_micro_f1 \
    --mcc-impact $OUT/impact-diversity-dividend-384.json \
    --output $OUT/tiering-dd384-dedup-singlepass.json
python scripts/dedup_tiering_rerun.py --board diversity-dividend-384 \
    --dedup all --rank-by observed_micro_f1 \
    --mcc-impact $OUT/impact-diversity-dividend-384.json \
    --output $OUT/tiering-dd384-dedup-all.json
for REF in canonical standardised; do
  python scripts/dedup_tiering_rerun.py --board 55map-mcc --reference $REF \
      --dedup none  --output $OUT/tiering-55map-mcc-$REF-control.json
  python scripts/dedup_tiering_rerun.py --board 55map-mcc --reference $REF \
      --dedup all   --output $OUT/tiering-55map-mcc-$REF-dedup.json
done
python scripts/dedup_tiering_rerun.py --board analysis \
    --analysis-id era1-leaderboard --dedup none --rank-by eval_f1 \
    --output $OUT/tiering-era1-leaderboard-control.json
python scripts/dedup_tiering_rerun.py --board analysis \
    --analysis-id era1-leaderboard --dedup all --rank-by observed_micro_f1 \
    --output $OUT/tiering-era1-leaderboard-dedup.json

# Consolidated machine-readable summary
python scripts/summarise_dedup_impact.py --input-dir $OUT \
    --output $OUT/findings-summary.json

# Tier-1 unit tests for the three load-bearing properties
python -m pytest tests/test_dedup_metric_impact.py -q
```

---

## See also

- `reports/scoring-sensitivity-review-2026-08-18.md` — the review whose § 5 gaps
  this closes, and whose exposure register and F1 measurements it builds on
- `reports/dedup-correction-worklist-2026-08-18.md` — the blast-radius trace and
  remediation plan (independently identifies the MCC exposure this quantifies)
- `reports/dedup-gap-compliance-2026-08-18.md` — the preregistration reading
- `docs/methodology/preregistration/protocol-errata.md` — **E80** (this gap),
  **E79** (the order-dependent tile assignment held fixed in § 4's measurement)
- `results/scoring-sensitivity-2026-08-18/` — the exposure register and the five
  probe batches this document audits and extends
- `results/diversity-dividend-384/tiering-champions/tiering_20m.{json,md}` — the
  committed tiering the § 3.2 controls reproduce exactly
- `results/metric-leaderboards/55map-mcc-tiering{,-standardised}.{json,md}` — the
  committed 55-map tile-MCC boards
- `scripts/dedup_metric_impact.py`, `scripts/dedup_tiering_rerun.py`,
  `scripts/diagnose_consensus_dedup_exposure.py`,
  `scripts/summarise_dedup_impact.py`, `tests/test_dedup_metric_impact.py`

---

## Changelog

### 2026-08-18 — Original publication

First measurement of the deduplication gap's effect on tile-level MCC, and the
first re-run of a committed permutation tiering on deduplicated inputs. Measured
59 cells across four boards; found that F1 and MCC move in opposite directions
in 40 of the 46 scorable cells, and that the entire MCC movement disappears
under a membership-preserving tile attribution — establishing that deduplication
does not degrade tile-level discrimination, but that collapsing cluster
provenance to a single tile does. Re-ran the `diversity-dividend-384` tiering at
the registered settings with two controls that reproduce the committed board
exactly (7 tiers, 0 of 231 significance decisions differing) and found the
Tier-1 three-member tie **breaks** into a two-member Pro-only tie, with the
consensus-versus-Pro pair moving from BH-p 0.6622 to BH-p 0.0346 against the
consensus champion. Re-ran both 55-map tile-MCC boards and found them
unchanged (0 of 28 significance decisions differing), and the 82-cell
`era1-leaderboard`, whose sole Tier-1 leader becomes a two-member tie (225 of
3,321 significance decisions change; the control again reproduces the committed
board exactly). Established that the six
duplicate-exposed consensus conditions were never un-deduplicated: 0 of their
193 residual pairs share a contributing pass, and exposure decays to zero by a
vote threshold of 3. Corrected a pass-file resolution defect that had the prior
review scoring two conditions — one a Tier-1 tie member — on 1 of 3 passes
(commit `4339cabc1`).
