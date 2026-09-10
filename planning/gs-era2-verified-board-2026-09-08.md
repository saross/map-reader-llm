# The GS Era-2 verified board: the Gemini 3.7 and 3.8 GS cells on one frame with the incumbents

> **Last revised**: 2026-09-09 (later: § 2 frame rule and recommendation —
> Era-2 ∩ B-union, 435 mounds; § 3 membership and G6 follow; earlier the
> same day: frame description corrected, same carrier tiles, 80 clipped; prior: 2026-09-08 original publication, drafted
> overnight in Session 151 on the PI's instruction; **DRAFT — awaits PI
> sign-off, § 9**).
> Controls one $0 API block (re-scoring and tiering on sapphire). Split out
> of the r2 recompute chain by PI ruling (S149; `planning/reference-revision-2026-09-06.md`
> § 4 step 4 and its pre-run audit fork 2). See [§ Changelog](#changelog).

## 1. Purpose and the split ruling

The paper's Gold Standard (GS) verified board is the Era-2 proposer–verifier
(PV) board on the 4-map, 487-tile, 384 px frame against the curator
reference (§ R4 of `docs/paper/results-draft.md`; skeleton exhibit (i)).
The Gemini 3.7 and 3.8 campaigns of 2026-08-28 → 2026-09-04 scored seven GS
cells that clear every Gemini 3 cell on that instrument (§ 3), and the
image-B campaign two image cells; none of them sits on any tiered GS board.
The r2 chain's pre-run audit found that the Era-2 GS boards git-track zero
artefacts (`results/leaderboard/era2/` and `results/leaderboard/per-architecture/era2/`
are untracked working copies; the tracked per-architecture boards were
retired to `archive/superseded-leaderboards/` at `b69d8af4b`), that no
leaderboard spec YAML exists, and that `planning/condition-inventory.json`
carries no 3.7/3.8 row. The leg is therefore a build-from-scratch with no
data dependency on reference r2 (the GS reference is
`inputs/vectors/references/mounds-reference.geojson`, untouched by r2), and
the PI ruled it out of the r2 chain into its own card. This is that card.

**Deliverable in one sentence**: one tiered GS Era-2 verified board on one
frame, holding the Gemini 3 incumbents and the 3.7 / 3.8 / image-B cells,
with its spec, inventory rows, gates, and register row.

## 2. Reference, frame, and metric

- **Reference**: `inputs/vectors/references/mounds-reference.geojson`
  (curator GS, 569 mounds), unchanged by r2.
- **Metric**: F1 at 20 m (the preregistered GS buffer), tile-level MCC
  alongside (`feedback_mcc_with_f1`), bootstrap 95 % CIs; tiering on F1.
- **Frame — a PI fork, because the two candidate frames are the same 487
  carrier tiles but not the same footprint** (corrected 2026-09-09; the
  original draft's "no polygon is shared" came from a faulty comparison).
  `inputs/vectors/bounds/384/full_evaluation_bounds.geojson` is the Era-2
  frame of pv-diag and verifier-robustness (487 tiles, union 1,415.8 km²,
  435 of the 569 reference mounds inside).
  `outputs/grid-2026-08-18/scoring/bounds/grid_common_bounds.geojson` is
  the same 487 tiles, by name and geometry (407 identical, 0 m
  displacement), with the 80 edge tiles CLIPPED to the grid campaign's
  four-way footprint intersection (union 1,364.5 km², 428 reference
  mounds; `results/grid-2026-08-18/findings.md` § Scope, built 2026-08-18
  after verifying that the four grid geometries' tile unions diverge —
  a majority-rule tile hanging off the footprint is kept whole, so denser
  tilings accrete area). Grid-common is therefore a strict subset of the
  Era-2 frame: 51.4 km² of edge and 7 reference mounds lie in the Era-2
  frame only. Every grid, stride, image-B, 3.7, and 3.8 GS cell is scored
  on grid-common. A board that mixes the two differs in frame as well as
  in cell (the 327-versus-487 leakage trap of `verify_run_conditions.py`,
  at the edge rather than the interior).
  - **The rule that decides it (proposed, 2026-09-09)**: a board's frame is
    the intersection of its members' DISPATCHED coverage — no cell is scored
    on ground its proposer never saw (the E72 partial-coverage discipline),
    and no ground every member saw is thrown away. Measured on 2026-09-09
    against the curator reference (569 mounds):

    | frame | area | reference mounds | who saw it |
    |---|---:|---:|---|
    | Era-2 frame (`full_evaluation_bounds`) | 1,415.8 km² | 435 | the incumbents' tiling; the B tiling misses 13.4 km² of it, which holds **0** mounds |
    | **Era-2 ∩ B-union (recommended)** | 1,402.4 km² | **435** | every incumbent and every B-geometry cell |
    | grid-common (four-way intersection) | 1,364.5 km² | 428 | everyone, including the 512 px and 384/12.5 % geometries |

  - **(a) Recommended — Era-2 ∩ B-union.** The nine new cells and the grid
    and stride B cells were all dispatched on the B tiling (384 px / 50 %,
    `grid_g384_ov192_bounds.geojson`, 1,398 tiles, 1,508 km²), which covers
    the Era-2 frame except a 13.4 km² edge strip containing no reference
    mound. Intersecting the two frames keeps all 435 mounds of the paper's
    GS instrument, scores no cell on unseen ground, and changes the
    incumbents' committed figures only through false positives in that
    mound-free strip (≈ 1 % of area), so § R4's cited numbers survive within
    rounding. The new cells gain the 7 mounds and 37.9 km² that grid-common
    had clipped from ground they did cover; the change from their campaign
    figures is reported per cell (§ 6, G6). Cost: one new bounds artefact
    (`Era-2 ∩ B`, materialised and committed with its construction) and a
    re-score of every member at $0.
  - **(b) Grid-common.** Reproduces the nine new cells' committed figures
    exactly (G5) and admits the 11 verified cells of the other grid and
    stride geometries, at the price of 7 mounds (1.6 %) and 51.4 km² that
    every proposed member actually covered. Those 11 cells answer the
    geometry question, which the stride plateau (Obs 435) and the grid
    boards already answer on grid-common; this board's question is
    architecture and model generation at the paper's GS instrument. Not
    recommended, but the fallback if the PI wants the geometry cells on
    the same board.
  - **(c) Full Era-2 frame — rejected.** Scores the B-geometry cells on
    13.4 km² their proposers never saw. The strip is mound-free, so no false
    negative is manufactured, but the rule would not hold for any future
    member, and the numbers would still differ from the campaign documents.

## 3. Membership

Two sets, one enumerated and one by rule; the total is **derived at build
time from the spec**, never asserted here.

**The new cells (enumerated; all on grid-common, curator reference, 20 m):**

| cell | register id | F1@20 [95 %] | P | R | n |
|---|---|---:|---:|---:|---:|
| 3.7 text, K = 5, carried Gemini 3 verifier, (0.10, k5) | `gemini37-screen-2026-08-28::g37-text-k5-verified-carried-p0.10-k5` | 0.9139 [0.887, 0.934] | 0.898 | 0.930 | 443 |
| 3.7 text, K = 10, carried Gemini 3 verifier, (0.10, k10) | `gemini37-screen-2026-08-28::g37-text-k10-verified-carried-p0.10-k10` | 0.9142 [0.886, 0.936] | 0.920 | 0.909 | 423 |
| 3.7 text, K = 5, 3.7 verifier (swap), (0.80, k5) | `gemini37-screen-2026-08-28::g37-text-k5-verified-swap37-p0.80-k5` | 0.9265 [0.901, 0.946] | 0.925 | 0.928 | 429 |
| 3.7 text, K = 5, 3.8 verifier (Arm V), (0.88, k5) | `gemini37-screen-2026-08-28::g37-text-k5-verified-swap38-p0.88-k5` | 0.9258 [0.900, 0.946] | 0.934 | 0.918 | 421 |
| fourth cell: Gemini 3 grid B K = 10 union, 3.7 verifier, (0.98, k10) | `grid-2026-08-18::g384-ov192-k10-verified37-p0.98-k10` | 0.9140 [0.885, 0.937] | 0.964 | 0.869 | 386 |
| 3.7 image, K = 5, carried Gemini 3 verifier, (0.10, k5) | `gemini37-image-gs-2026-09-01::g37-image-k5-verified-carried-p0.10-k5` | 0.9254 [0.899, 0.946] | 0.923 | 0.928 | 430 |
| 3.7 image, K = 5, 3.7 verifier, (0.90, k5) | `gemini37-image-gs-2026-09-01::g37-image-k5-verified-swap37-p0.90-k5` | 0.9308 [0.905, 0.951] | 0.934 | 0.928 | 425 |
| image-B: Gemini 3 image MIN, 384/50 %, K = 10, (0.15, k9) | `image-b-gs-2026-08-28::g384-ov192-image-min-k10-verified-p0.15-k9` | 0.8412 [0.801, 0.872] | 0.874 | 0.811 | 397 |
| image-B: Gemini 3 image HIGH, 384/50 %, K = 10, (0.20, k8) | `image-b-gs-2026-08-28::g384-ov192-image-high-k10-verified-p0.20-k8` | 0.8333 [0.797, 0.864] | 0.863 | 0.806 | 400 |

(Values re-read from each row's `best-eval/evaluation.json` on 2026-09-08;
the text-B GS anchor the image-B findings cite, 0.8961, is the grid cell
`grid-2026-08-18::g384-ov192-k10-verified-p0.15-k10` and joins under the
rule below.)

**The incumbents (by rule):** every registered condition with
`aggregation: verified` whose run is a 4-map-GS, 384 px, curator-reference
run at N ≥ 5 dispatched on the Era-2 tiling or the B tiling — the members
of the archived per-architecture Era-2 PV board (44 conditions at
`ef3ec4fe`) plus the B-geometry verified cells of the grid and stride
campaigns (`grid-2026-08-18::g384-ov192-*-verified-*`, the stride B cells).
Under the frame rule of § 2 the 11 verified cells of the other grid and
stride geometries (512 px; 384 px at 12.5 % and 33 %; 256 px) are
excluded — their tilings fall short of the Era-2 frame by up to 38 km² —
and stay on the grid and stride boards. The spec's `--dry-run` listing is
the membership; the PI confirms it at sign-off (§ 9). Smoke-test and
quarantined v2-verifier cells are excluded by the inventory builder's
existing rules.

## 4. Prerequisites ($0)

1. **Inventory rows**: `scripts/build_condition_inventory.py` crawls
   `outputs/retest`, `outputs/h11`, `outputs/h8-v2`, `outputs/h10`, and
   `outputs/h12-v2` only. Extend its crawl (or add an explicit addendum
   list) so the nine new cells and the grid / stride / image-B verified
   cells gain `planning/condition-inventory.json` rows with `era: 2`,
   `verifier_data: true`, `model` (`gemini-3.7-flash`, `gemini-3.8-flash`),
   and `path` pointing at each cell's committed verified GeoJSON.
2. **Spec YAML**: `planning/leaderboard-specs/gs-era2-verified-board.yaml`
   (new directory; the builder's `--spec` input), listing the enumerated
   cells and the incumbent rule's resolved ids, the frame of § 2, the
   reference, buffers `20 30 40 50`, bootstrap 10,000, seed 42, MCC on.
3. **One-frame re-score** of every member whose committed evaluation is on
   the other frame (`evaluate_detections.py`, the board's own stage-2
   instrument) into the board's `cells/` directory. The committed
   evaluations are not touched or re-pointed.

## 5. Instrument

`scripts/build_tiered_leaderboard.py --spec …`: threshold sweep per cell
at the four buffers, F1-led selection at 20 m, round-robin tile-level
paired permutation tests (10,000, seed 42), Benjamini–Hochberg q = 0.05,
greedy-clique tiers with the Tier-1 membership reported as the MCB
admissible set (E83 / D20), bootstrap CIs per buffer, MCC alongside.
Identical to the archived Era-2 PV board's instrument
(`archive/superseded-leaderboards/leaderboard/per-architecture/era2/pv/`,
`ef3ec4fe`), so the regression gate below is meaningful.

## 6. Gates (nothing published unless all pass)

- **G1 regression**: the archived Era-2 PV board (44 cells, `ef3ec4fe`)
  reproduces on `full_evaluation_bounds` from the same inputs before any
  new cell is added — F1 per cell to 1e-6, the 20 m pairwise p-values, the
  tiers.
- **G2 committed-evaluation reproduction**: every member's F1@20 on its OWN
  committed frame reproduces its `evaluation.json` to 1e-6 before the
  one-frame re-score is read.
- **G3 frame identity**: every cell on the board is scored on the § 2 frame;
  `verify_run_conditions.py`'s scope check runs on the new rows; a cell
  whose scope cannot be resolved is dropped with a reason, never scored on
  a guessed frame.
- **G4 membership count derived**: the board's cell count equals the spec's
  `--dry-run` listing; no count is typed into a document.
- **G5 coincidence**: where a member's board-frame score coincides with a
  committed evaluation (every cell under option (b); none under (a)), the
  board's stage-2 evaluation reproduces the committed value exactly.
- **G6 frame delta, reported not gated**: every cell carries the difference
  between its committed-frame score and its board-frame score (incumbents:
  Era-2 frame → board frame; new cells: grid-common → board frame), so the
  edge effect is visible per cell and a tier that depends on it is flagged.
- **Stop states**: any gate failing; a re-score whose n_detections differs
  from the committed GeoJSON's feature count (`feedback_feature_count_crosscheck`).

## 7. Deliverables

- `results/leaderboard/era2/gs-era2-verified-board-2026-09/` —
  `board_20m.json`, `board-20m.md` (tiers, CIs, MCC, the significance
  figure), `cells/<id>/evaluation.json` for every one-frame re-score,
  `spec.yaml` copied in, `provenance.json` (inputs, commit, gates passed).
  **Git-tracked**, unlike its predecessors.
- `planning/leaderboard-specs/gs-era2-verified-board.yaml`; inventory rows.
- Register: `verifier_passes` / conditions already exist for every member;
  one analysis row `gs-era2-verified-board-2026-09` (type `leaderboard`,
  post-hoc, H-refs H2 and H1 for the modality cells, `paper_section`
  Results § R4 / R7.3), PI-signed; manifests regenerated;
  hypothesis-outcome table regenerated.
- An Obs (obs-writer) once the board is read: whether the 3.7 stack's GS
  gain is a tier move on the tiered instrument (the campaigns' pairwise
  tests say yes; the board says it against all incumbents at once).
- `docs/paper/results-draft.md` § R4: one paragraph and the board pointer
  (the compression pass decides how much survives; S2 carries the board).

## 8. Cost

API $0. Compute: the re-scores (bootstrap 10,000 per cell, ≈ 50–60 cells,
≈ 5–7 min each) and the pairwise tests (≈ 1,500 pairs) — a few hours
sequential on sapphire, under an hour at 4-way parallelism. Nothing runs
until § 9 is signed.

## 9. Sign-off (PI)

- [x] Frame: **(a) Era-2 ∩ B-union** — PI, 2026-09-09: "maintaining
      discipline is important for a large, complex project like this, I
      accept your proposal, please proceed".
- [x] Membership: the enumerated nine plus the incumbent rule of § 3
      (B-geometry and Era-2-tiling cells), confirmed with the proposal;
      the `--dry-run` listing is recorded in § Changelog when built.
- [x] Buffers / tiering as § 5.
- [x] Go — 2026-09-09.

## Changelog

### 2026-09-10 — Built (S151-d, PI go 2026-09-09); three deviations disclosed

**Executed**: frame materialised (`scripts/materialise_era2_b_frame.py`,
`f9b87da22`: 487 tiles, 34 clipped, 453 identical, 1,402.41 km², 435
mounds; sidecar records the construction); membership derived by the
§ 3 rule (`scripts/build_gs_era2_board.py membership`, `be01df377`):
**39 members**, 77 exclusions each with its reason
(`membership.json`); every member scored on the frame with its own
committed recipe and reproduced on its committed frame (`e8f4c9d85`);
gates (`77cc55617`): G2 0 failures (every committed evaluation
reproduces exactly under the current evaluator), G3 0, G4 39/39, G6 the
29 Era-2-frame incumbents unchanged to four decimals and the 10
B-geometry cells −0.0070 to −0.0078; register rows minted and the G2
evaluations waived (`d15e6fe7e`); tiering and MCB via the canonical
chain (recorded below when landed).

**Deviation 1 — the archived board is not register-backed.** The card's
§ 3 named "the members of the archived per-architecture Era-2 PV board
(44 conditions)". Only 4 of those 44 match any registered condition by
committed F1: the archived board was built from sweep-optimal
"pv-materialised" cells, the in-sample optima E56 / E83 retired, not
from the register's operating-point cells. Membership is therefore the
register's cells by the rule (39), and the archived board's cells are
NOT on this board.

**Deviation 2 — instrument.** § 5 named `build_tiered_leaderboard.py`
as "identical to the archived board's instrument". The archived board is
the retired instrument; the current canonical one is the register-driven
chain (`scripts/era1_leaderboard_tiering.py`, the definitive Era-1, the
n1 and the final 55-map boards; round-robin tile-swap micro-F1
permutation 10,000, seed 42, BH q = 0.05, greedy clique, 20 m) with the
MCB admissible set from `selection_aware_intervals.py --board`. The
board uses the canonical chain; both need the members as register rows
scored on the board frame, hence **deviation 3 — the `-era2b` rows**:
one new condition per member (scope_override `era2-b-487`, eval_path the
board cell), the r2 chain's pattern; § 7's "conditions already exist for
every member" was wrong under a one-frame board.

**G1 as specified — FAIL, marginal and localised.** Rebuilding the
archived 44-cell board from its archived inputs with the retired
builder (`gs-era2-regression-archived-board-2026-09-10.yaml`;
`--top-n 0`, which the archived metadata records and the builder does
not default to — the first attempt silently kept 26 cells): 43 of 44
cells reproduce F1@20 exactly; `pv-high-image-t0.3-n5` moves
0.7460 → 0.7475; one of 946 pairs crosses BH q = 0.05 (adjusted p
0.046 → 0.059); tiers 5–6 (the bottom of the image block) re-cut,
tiers 1–4 identical. Instrument drift in the RETIRED builder on one
archived input between `005e6c71` (2026-08-20) and today
(`g1-regression.json`). **Publication ruling (§ 6: nothing published
unless all gates pass) is the PI's**; the analysis row is unsigned.

**The dry-run listing (39):** `flash35-pv-2x2::f35prop-f35vf-4of10`, `flash35-pv-2x2::f35prop-f3vf-4of10`, `flash35-pv-2x2::f3prop-f35vf-6of10`, `gemini37-image-gs-2026-09-01::g37-image-k5-verified-carried-p0.10-k5`, `gemini37-image-gs-2026-09-01::g37-image-k5-verified-swap37-p0.90-k5`, `gemini37-screen-2026-08-28::g37-text-k10-verified-carried-p0.10-k10`, `gemini37-screen-2026-08-28::g37-text-k5-verified-carried-p0.10-k5`, `gemini37-screen-2026-08-28::g37-text-k5-verified-swap37-p0.80-k5`, `gemini37-screen-2026-08-28::g37-text-k5-verified-swap38-p0.88-k5`, `grid-2026-08-18::g384-ov192-k10-verified-p0.15-k10`, `grid-2026-08-18::g384-ov192-k10-verified37-p0.98-k10`, `image-b-gs-2026-08-28::g384-ov192-image-high-k10-verified-p0.20-k8`, `image-b-gs-2026-08-28::g384-ov192-image-min-k10-verified-p0.15-k9`, `pv-diag-384::verified-adv-image-3of5`, `pv-diag-384::verified-adv-image-min-3of5`, `pv-diag-384::verified-adv-image-min-6of10`, `pv-diag-384::verified-adv-pro-image-pro-vf-3of5`, `pv-diag-384::verified-adv-pro-text-flash-vf-3of5`, `pv-diag-384::verified-adv-pro-text-medium-vf-3of5`, `pv-diag-384::verified-adv-pro-text-pro-vf-3of5`, `pv-diag-384::verified-adv-text-4of5`, `pv-diag-384::verified-adv-text-6of10`, `pv-diag-384::verified-adv-text-consensus-16of30`, `pv-diag-384::verified-adv-text-high-vf-4of5`, `pv-diag-384::verified-adv-text-medium-vf-4of5`, `pv-diag-384::verified-adv-text-min-6of10`, `pv-diag-384::verified-adv-text-min-n30lineage-4of5`, `pv-diag-384::verified-adv-text-min-true-3of5`, `pv-diag-384::verified-adv-text-pro-vf-4of5`, `pv-diag-384::verified-adv-text-t03-4of5`, `verifier-robustness::verified-384-16of30-t0-3-n5-opmax`, `verifier-robustness::verified-384-ge3of5-t0-3-high-n5`, `verifier-robustness::verified-384-ge3of5-t0-3-n5`, `verifier-robustness::verified-384-ge3of5-t0-7-high-n5`, `verifier-robustness::verified-384-ge3of5-t0-7-n5`, `verifier-robustness::verified-384-union-t0-0-n5`, `verifier-t-pilot::verified-t0-0`, `verifier-t-pilot::verified-t0-5`, `verifier-t-pilot::verified-t1-0`.

### 2026-09-09 (later) — Frame rule and recommendation added

On the PI's request for a principled decision: the frame is the
intersection of the members' dispatched coverage. Measured: the B tiling
(1,398 tiles) covers the Era-2 frame except a mound-free 13.4 km² strip, so
Era-2 ∩ B-union keeps all 435 reference mounds while grid-common keeps
428. Recommended (a) Era-2 ∩ B-union; (b) grid-common retained as the
fallback that admits the 11 other-geometry cells; (c) the full frame
rejected. § 3 membership restated under the rule; G6 (per-cell frame
delta) added; § 9 options renumbered.

### 2026-09-09 — § 2 frame description corrected

The original draft said the two 487-tile frames share no polygon; a
proper one-CRS comparison shows they are the same carrier tiles, 407
identical and 80 clipped, grid-common a strict subset (1,364.5 vs
1,415.8 km²; 428 vs 435 reference mounds). The fork stands, its cost now
stated: 7 edge mounds and 51.4 km² under option (a).

### 2026-09-08 — Original publication (draft for sign-off)

Drafted overnight in Session 151 on the PI's instruction ("Write the GS
Era-2 board leg its own card, split out of the r2 chain"). Facts re-read at
drafting: the split ruling and audit findings (`planning/reference-revision-2026-09-06.md`
§ 4 step 4, fork 2), the archived board's instrument and membership
(`archive/superseded-leaderboards/leaderboard/per-architecture/era2/pv/leaderboard_tiers_100m.md`),
the nine cells' evaluations, the two frames' polygon sets, the builder's
CLI, and the inventory crawl list. Nothing has been built or scored.
