# The GS Era-2 verified board: the Gemini 3.7 and 3.8 GS cells on one frame with the incumbents

> **Last revised**: 2026-09-08 (original publication, drafted overnight in
> Session 151 on the PI's instruction; **DRAFT — awaits PI sign-off, § 9**).
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
- **Frame — a PI fork, because the two candidate frames are NOT the same
  487 tiles.** `inputs/vectors/bounds/384/full_evaluation_bounds.geojson`
  (the pv-diag / verifier-robustness Era-2 frame) and
  `outputs/grid-2026-08-18/scoring/bounds/grid_common_bounds.geojson` (the
  grid campaign's common frame, on which every grid, stride, image-B, 3.7,
  and 3.8 GS cell is scored) both hold 487 polygons, but no polygon is
  shared (checked 2026-09-08: 0 of 487 bounding boxes coincide). A board
  that mixes them differs in frame as well as in cell (the 327-versus-487
  leakage trap of `verify_run_conditions.py`, in a new coat).
  - **(a) Proposed default — grid-common.** The nine new cells already sit
    on it; the incumbents' detection sets are point sets and re-score on it
    at $0 (`evaluate_detections.py`, bootstrap 10,000, seed 42). Every cell
    on the board is then scored by one command on one frame, and the
    incumbents' committed 487-frame evaluations stay as their register
    record (nothing is re-pointed).
  - **(b) Alternative — full_evaluation_bounds.** The historical frame of
    § R4; the nine new cells would be re-scored on it instead (also $0), but
    their register rows and the 3.7 / 3.8 campaign findings are written on
    grid-common, so the board's numbers would not match the campaign
    documents the paper cites.

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
run at N ≥ 5 and whose committed evaluation covers 487 tiles — the members
of the archived per-architecture Era-2 PV board (44 conditions at
`ef3ec4fe`) plus the grid campaign's verified cells
(`grid-2026-08-18::*-verified-*`) and the stride Phase B/C verified cells.
The spec's `--dry-run` listing is the membership; the PI confirms it at
sign-off (§ 9). Smoke-test and quarantined v2-verifier cells are excluded
by the inventory builder's existing rules.

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
- **G5 coincidence**: where a new cell's grid-common score coincides with a
  committed evaluation (the nine new cells, on option (a)), the board's
  stage-2 evaluation reproduces the committed value exactly.
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

- [ ] Frame: option (a) grid-common (proposed) or (b) `full_evaluation_bounds`.
- [ ] Membership: the enumerated nine plus the incumbent rule as listed by
      `--dry-run`, or an amended list.
- [ ] Buffers / tiering as § 5, or amended.
- [ ] Go.

## Changelog

### 2026-09-08 — Original publication (draft for sign-off)

Drafted overnight in Session 151 on the PI's instruction ("Write the GS
Era-2 board leg its own card, split out of the r2 chain"). Facts re-read at
drafting: the split ruling and audit findings (`planning/reference-revision-2026-09-06.md`
§ 4 step 4, fork 2), the archived board's instrument and membership
(`archive/superseded-leaderboards/leaderboard/per-architecture/era2/pv/leaderboard_tiers_100m.md`),
the nine cells' evaluations, the two frames' polygon sets, the builder's
CLI, and the inventory crawl list. Nothing has been built or scored.
