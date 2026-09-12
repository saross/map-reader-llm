# K-ladder closeout: claims with anchors, and what is left for the PI

> **Last revised**: 2026-09-12 (original publication — the closing report of the
> K-ladder closeout job). Controlling card:
> `planning/k-ladder-review-2026-09-11.md` (rulings R1–R5). Companions:
> `reports/k-ladder-phase1-deltas-2026-09-12.md`,
> `reports/k-ladder-phase2-deltas-2026-09-12.md`,
> `reports/tile-mcc-geometric-join-2026-09-12.md`,
> `reports/union-staleness-retrospective-2026-09-12.md`.
> See [§ Changelog](#changelog).

## 1. The headline

Eight items were briefed. **Five landed complete, one landed partially, and two
stopped** — one on a measurement that contradicted the item's premise and one on
a design decision the brief did not rule. The API spend came in **under the
approval**.

| # | Item | Outcome |
|---:|---|---|
| 1 | Tier E — the approved API spend | **LANDED.** US$4.9595 audited flex against a US$5.02 approval; 7,239 of 7,239 candidates verified, 0 failed |
| 2 | The K = 5 fill for stride B under the 3.7 verifier | **PARTIAL** — the generator defect is fixed and the rung builds; see § 5 |
| 3 | The tension analyses | **LANDED**, and they answer the question |
| 4 | The K-ladder analysis row | **LANDED**, UNSIGNED |
| 5 | The five stale T = 1.0 unions | **LANDED** — relabelled, propagated, erratum E85 |
| 6 | The two stale h10 consensus files | **LANDED** — archived and rebuilt, with one deliberate omission (§ 6) |
| 7 | E72 propagation | **LANDED** — a caveat field through both generators |
| 8 | The Era-2 board rebuild | **STOPPED.** The builder refuses all 46 cells by rule; admitting them is a design decision (§ 8) |

**The single most important number.** Tier E's three rungs cost
**US$4.9595** on the audited flex basis — 6.1 cents under the US$5.02 approval
and US$2.04 under the US$7.00 hard stop — at **US$0.00068512 per candidate**,
inside the audited 0.000684–0.000698 spread and 1.1 % below the adopted
`VF_CALL_USD = 0.000693`. Anchor:
`results/k-ladder-2026-09-12/tier-e/spend-ledger.json`, key `total`.

## 2. Tier E: what the money bought

### 2.1 The spend, per rung

Every figure is a key of `results/k-ladder-2026-09-12/tier-e/spend-ledger.json`,
rebuilt from the three committed `run.meta.json` files.

| row | K | passes | candidates | verified | failed | API calls | retries | audited flex USD | USD/candidate | wall |
|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 1 | `1` | 1,826 | **1,826** | 0 | 1,826 | 0 | **1.2531** | 0.000686 | 6 m 39 s |
| 2 | 3 | `1,2,3` | 2,481 | **2,481** | 0 | 2,482 | 1 | **1.6989** | 0.000685 | 8 m 09 s |
| 3 | 5 | `1,2,3,4,5` | 2,932 | **2,932** | 0 | 2,932 | 0 | **2.0074** | 0.000685 | 8 m 38 s |
| | | **total** | **7,239** | **7,239** | **0** | **7,240** | **1** | **4.9595** | **0.000685** | **23 m 27 s** |

**The union gate, which is the reason the spend was safe.** The PI's approval
named the expected candidate count of each rung, with a 2 % deviation as a STOP.
All three reproduced **exactly**:

| K | expected (PI) | measured | delta | % |
|---:|---:|---:|---:|---:|
| 1 | 1,826 | **1,826** | +0 | 0.000 |
| 3 | 2,481 | **2,481** | +0 | 0.000 |
| 5 | 2,932 | **2,932** | +0 | 0.000 |

Anchor: `results/k-ladder-2026-09-12/tier-e/unions.json`. The flex correction
Phase 2 documented recurs and is corrected the same way: all three metas record
`cost_basis: "list"` with `discount: 1.0` under `--service-tier flex`, and their
recorded totals sum to **US$9.9191** — twice the invoice.

### 2.2 The construction asymmetry, measured before the spend

This is the run's substantive finding about its own inputs, and it was found by
measuring rather than assuming. The committed K = 10 rung of this family is built
by a different rule from the three rungs tier E bought.

| K | union | candidates | builder | footprint |
|---:|---|---:|---|---|
| 1 | `outputs/grid-2026-08-18/g384_ov192/consensus-n1/consensus_t1.geojson` | 1,826 | `merge_passes.py` | pool native |
| 3 | `…/consensus-n3/consensus_t1.geojson` | 2,481 | `merge_passes.py` | pool native |
| 5 | `…/consensus-n5/consensus_t1.geojson` | 2,932 | `merge_passes.py` | pool native |
| 10 | `outputs/grid-2026-08-18/verifier/g384_ov192/union_k10.geojson` | **3,319** | `materialise_grid_unions.py` | **grid common 487-tile carrier, filtered** |

`materialise_grid_unions.union_with_votes` assigns each cluster a primary carrier
tile and drops every cluster with none, and it clusters *prepared* passes
(`grid_analysis.load_cell_passes`, reading `detections_dedup.geojson`) rather
than the raw run GeoJSONs. Measured this session:

| K | `merge_passes` union | of those, on the common carrier | committed | grid `sweep.csv` at c = 1, k = 1 |
|---:|---:|---:|---:|---:|
| 1 | 1,826 | **1,685** | — | **1,685** |
| 3 | 2,481 | **2,295** | — | **2,295** |
| 5 | 2,932 | **2,714** | — | **2,714** |
| 10 | 3,591 | **3,325** | **3,319** | **3,319** |

The carrier-filtered counts reproduce the grid sweep's own rows **exactly** at
K = 1, 3 and 5 and to within 6 features at K = 10, so the mechanism is
identified, not inferred. **Why it was nonetheless right to spend as approved:**
the PI's expected counts are the native figures, so building the filtered union
instead would have tripped the 2 % STOP on all three rungs. What it costs is
about 7 % of the spend on candidates outside the board frame (which the scorer
excludes rather than mis-books) and a ladder whose top rung's candidate universe
was assembled differently. **Morning question 3.**

### 2.3 The two 487-tile frames are not the same polygons

Measured because the tile-join invariant turns on vocabulary and the ladder's
comparability turns on geometry:

| frame | tiles | `tile_name` set | union area (m²) |
|---|---:|---|---:|
| `outputs/grid-2026-08-18/scoring/bounds/grid_common_bounds.geojson` | 487 | identical | 1,364,471,339.5 |
| `inputs/vectors/bounds/384/era2_b_intersection_bounds.geojson` | 487 | identical | 1,402,406,728.4 |

Set-identical names, 0 only in either; symmetric difference **37,935,388.9 m²**
(2.7 %). The shared vocabulary is why tier E's cells are **not** the 3.7
family's withheld-MCC case; the differing polygons are why each rung's sweep was
run on both frames and the agreement recorded per rung rather than assumed.

### 2.4 The pre-launch gate

`results/k-ladder-2026-09-12/tier-e/pre_launch_audit.md` — **READY TO LAUNCH**,
9 of 9 preregistration requirements matched, 12 of 12 transmission modes passed,
0 blockers, 4 warnings. The five-candidate smoke run stamped instruction
SHA-256 `2518d5298d9b84bac6810bb0d11e59ef534c46853f65cb25dc1454af3497e15d` — the
same hash Phase 2's 28 rungs and the August 3.7-screen verifier stamped — and
priced at US$0.00069 per candidate, corroborating the audited rate a sixth time.

### 2.5 The verified ladder

TIER_E_LADDER_PLACEHOLDER

## 3. The tension analyses: the two corpora agree

`results/k-ladder-2026-09-12/findings.md` § 8 is the analysis; this is the delta.
Artefacts: `results/k-ladder-2026-09-12/tension/{subsample,effect-sizes,grid-overlap}.json`.

### 3.1 The subsample test

The deployment MINIMAL ladders' own cells, on random 487-tile subsets of their
own 8,541 tiles — 200 draws, seed 42, the ladders' own round-robin tile-swap
instrument with BH within each draw.

| ladder | full corpus | draws BH-significant at 487 tiles | ΔF1 mean (sd) | p05 … p95 | negative draws |
|---|---:|---:|---|---|---:|
| 55-map stride A, r2 | +0.0192 (p < 0.0001) | **39 / 200 = 19.5 %** | +0.0191 (0.0113) | +0.0012 … +0.0377 | 8 |
| 55-map stride B, r2 | +0.0547 (p < 0.0001) | **197 / 200 = 98.5 %** | +0.0537 (0.0116) | +0.0329 … +0.0723 | 0 |

**The gate, and a defect it caught.** Each rung's per-tile table was rebuilt and
its micro-F1 compared with its committed board F1 before any subset was drawn:
all eight rungs reproduce to within **2.6e-5**. The first run failed that gate at
micro-F1 **0.0000** on all eight rungs — the signature the tile-join report
describes for a vocabulary mismatch — and the cause was the **projection**, not
the names: the committed cells' detections are EPSG:4326 while the reference and
frame are EPSG:32635, so a 50 m tolerance was applied in degrees. The
`source_tile` vocabulary matches the frame **2,579 of 2,579**. Fixed by
projecting to `TARGET_CRS` as `era1_leaderboard_tiering` does at `:232-235` and
`:665-666`; recorded because the gate is the only reason those numbers were not
published.

### 3.2 The effect sizes

| ladder | corpus | tiles | ΔF1, K = 1 → best | BH p | separates? |
|---|---|---:|---:|---:|:---:|
| MINIMAL image T 0.7 | gold standard | 487 | **+0.0629** | 0.0006 | **yes** |
| stride B | deployment | 8,541 | **+0.0547** | < 0.0001 | **yes** |
| MINIMAL text T 1.0 | gold standard | 487 | **+0.0546** | 0.0012 | **yes** |
| MINIMAL image T 1.0 | gold standard | 487 | +0.0384 | 0.1236 | no |
| GS stride A (exact) | gold standard | 487 | **+0.0305** | 0.0072 | **yes** |
| MINIMAL text T 0.3 | gold standard | 487 | +0.0223 | 0.2768 | no |
| stride A | deployment | 8,541 | **+0.0192** | < 0.0001 | **yes** |
| MINIMAL text T 0.7 | gold standard | 487 | +0.0164 | 0.5780 | no |
| MINIMAL image T 0.3 | gold standard | 487 | +0.0139 | 0.7803 | no |

### 3.3 The grid overlap comparison

Consensus-only, fixed MINIMAL text T 0.7, best F1@20 over the (corroboration,
vote) grid per K, on the grid-common 487-tile footprint. Source
`results/grid-2026-08-18/sweep.csv`.

| geometry | K = 1 | K = 3 | K = 5 | K = 10 | ΔF1, K = 1 → 10 | ΔMCC |
|---|---:|---:|---:|---:|---:|---:|
| 384 px / 50 % | 0.6633 | 0.6837 | 0.7045 | 0.7205 | **+0.0572** | +0.0444 |
| 512 px / 50 % | 0.7121 | 0.7429 | 0.7440 | 0.7518 | **+0.0396** | +0.0382 |
| 384 px / 12.5 % | 0.5021 | 0.5976 | 0.6176 | 0.6475 | **+0.1454** | +0.1543 |
| 512 px / 12.5 % | 0.5845 | 0.6763 | 0.6736 | 0.6759 | **+0.0914** | +0.0597 |

### 3.4 The verdict, in one line

**The scale reading, for the tension as posed: 487 tiles resolve a ΔF1 of about
0.03 and above and not below, the nine MINIMAL ladders sort by effect size
rather than by corpus, and the deployment range (+0.0192…+0.0547) sits inside
the gold-standard range (+0.0139…+0.0629) — so "K buys nothing detectable" on
four MINIMAL configurations is a statement about tile count, not about K.**
Qualified by § 3.3: K's return is not geometry-independent, and on the
consensus-only ladders tile-MCC *rises* with K, which is the opposite of the
verified ladders and consistent with the same mechanism. What is not claimed is
in `findings.md` § 8.5.

## 4. The analysis row

`results/run-analyses.json`, row `k-ladder-2026-09-12`, **UNSIGNED**
(`manually_verified_at: null`, with a `_signature_note` saying so and naming the
two things the PI should know before signing).

| field | value |
|---|---|
| `type` | `comparison` |
| `preregistered` | `post-hoc` |
| `hypothesis_refs` | `["H3", "H13"]` |
| `deviations` | `["E56", "E85"]` |
| `conditions_compared` | CONDITIONS_COUNT_PLACEHOLDER ids, all resolving |
| `output_path` | `results/k-ladder-2026-09-12/findings.md` |

**`hypothesis_refs` was checked, not assumed.** `scripts/lib_hypothesis_requirements.py`
is a config-field requirements module consumed at experiment-launch time and has
**no H3 entry at all** (H3's factor is post-hoc aggregation, not a config field),
so it does not constrain this row. The binding authority is
`scripts/generate_hypothesis_outcome_table.py:65`, whose registration-constants
table reads `"H3": ("Consensus voting improves F1 (osf:497)", "confirmatory")`,
and `docs/methodology/preregistration/hypothesis-tracking.md:126-141`, which
registers H3's pool sizes and thresholds. H13 is the tile-geometry factor. Both
are the refs every other ladder row in the register carries
(`stride-winner-ladder-exact-2026-08-25`, `stride55-ladder-2026-08-27`).

**`conditions_compared` is derived, not transcribed** — read out of the three
committed ladder inventories by `scripts/author_k_ladder_analysis_row.py` and
checked against the register before anything is written, because the generator's
foreign-key guard warns on an unresolved id and a tier-1 test asserts that
warning list is empty.

## 5. Item 2: the K = 5 fill, and the defect behind it

**The cause was not what the brief supposed, and finding it is most of the
item.** `scripts/gemini37_fourth_cell_ladder.py` is **not** the script that
produced the committed K = 1/3/10 rungs of `findings.md` § 3.3: its own output
(`results/gemini37-fourth-cell/55map/g384_ov192_55map/ladder.json`) computes
N = 1/3/5 with different numbers (0.8334 / 0.8688 / 0.8697) against the table's
0.8352 / 0.8747 / 0.8813, because it scores through
`compute_corrected_f1_multi_buffer` against the in-process canonical reference
rather than through the board chain. The table's numbers come from
`scripts/final_board_sweeps.py`'s `build_g37_families`.

**The defect, and it is a one-line asymmetry.** That function's rung loop was
the literal `for n in (1, 3):`, while the plain stride A/B branch uses
`(1, 3, 5)`. The two 3.7 arms hold five passes, so `(1, 3)` was correct for
them — a rung at N = 5 would *be* their full union. The fourth cell re-verified
stride B's **ten** passes, so its K = 5 rung was simply never generated. That is
the whole of `findings.md` § 3.3's "zero-usd-inherited, never built".

**Fixed** by deriving the rungs from the family's own `k_max` — every first-N
strictly below it — so the arms keep exactly the rungs they had, the fourth cell
gains N = 5, and the asymmetry cannot drift back in.

**What landed and what did not.** The generator fix is committed and the sweep
regeneration ran with every gate passing (G4 reproduces all eleven committed
micro-F1 values at d ±0.0000, and both pass pins verified). What is **not** done
is the rest of the chain — `r2_score_cells.py --stage board`, the register row,
and the regenerated inventory — because completing it would also mean running
`scripts/final_board_build.py --reference r2`, which **re-tiers the 55-map final
board**: its BH family would grow from 595 pairs, and `findings.md` § 4.1's gate
reproduces that board's committed pairwise p-values. Re-tiering a committed
deployment board is a board decision of exactly the kind item 8 ruled on for
Era-2, and the brief did not rule it here. **Morning question 5.**

## 6. Items 5, 6 and 7: the register work

### 6.1 The relabel (item 5)

| claim | before | after |
|---|---|---|
| The five conditions' labels | `consensus-384-t1-0::consensus-{1..5}of30` | **`…::consensus-{1..5}of5`** |
| Their `n_passes` | 30 | **5** |
| Their `_note` | E72 only | **E72 + E85** |
| The uplift supplement's `N` | 30 | **5** (derived from `n_passes`) |
| Its `cost_basis` | "sum over N=30 proposer passes" | **"sum over N=5 proposer passes"** |
| Its `K` | 30 | **30, unchanged and correct** — `K` is the pool's full pass count, `N` the prefix consumed |
| Their `notes` cell | empty | **the register caveat, carried** (item 7) |
| Erratum | — | **E85**, beside E72 by cross-reference |

No union, evaluation, or measured value was touched. Anchors:
`results/run-conditions.json` `decomposition.consensus-384-t1-0.conditions[0..4]`;
`docs/methodology/preregistration/protocol-errata.md` § E85;
`reports/union-staleness-retrospective-2026-09-12.md` § 3.3, options 1 and 4.

**One thing the brief did not anticipate, and it touched a signed row.** The
signed `uplift-supplement-flatten` row (`manually_verified_at`
`2026-09-10T22:55:40Z`) holds all five ids among its 441
`conditions_compared`. Leaving them stale would break the generator's
foreign-key guard and `tests/test_generate_post_run_report.py::test_manifest_envelopes_valid`,
which asserts `warnings == []` and `conditions_compared <= known_ids` against the
**live** register. The five ids were therefore **renamed in place** — a rename of
the same artefacts, not a change of claim — with the row's `outcome`,
`manually_verified_at` and `_signature_note` untouched and a `_conditions_note`
recording what moved and why. **Morning question 2.**

### 6.2 The h10 rebuild (item 6)

| union | committed (stale) | rebuilt | § 4.1's predicted re-derivation |
|---|---:|---:|---:|
| `consensus_t1.geojson` | 1,454 | **1,474** | 1,474 |
| `consensus_t2.geojson` | 474 | **477** | 477 |

The rebuild reproduces the retrospective's predicted counts **exactly**. The
originals are archived to
`archive/superseded-consensus-2026-09-12/h10-pool_160_hp4hn4/` with a README, and
the new `voting_summary.json` carries `pass_provenance_schema`, `pass_ids` and a
`pass_provenance` block with a `git_blob_hash` per pass. **No registered
condition reads either file** — re-verified across `results/run-conditions.json`,
`results/conditions-manifest.json` and `results/` generally.

**One deliberate omission.** `consensus_t3/t4/t5` were **not** rebuilt. They
reproduce at identical counts (313 / 236 / 163), so none is stale in the sense
`t1` and `t2` were — but `consensus_t4.geojson` is the detections file of the
registered condition `h10::greedy-pool-160`, and § 4.1 records its re-derivation
differing by one matched pair **0.444 m** apart. Rewriting a registered
condition's detections for a 0.444 m centroid shift is a PI decision.
**Morning question 6.**

### 6.3 E72 propagation (item 7)

E72's remediation item 4 promised "conditions-manifest coverage caveats set for
the derived conditions"; the retrospective's § 3.2 found it undischarged. It is
discharged:

| artefact | before | after |
|---|---|---|
| `results/conditions-manifest.json` | zero occurrences of "E72"; the condition schema had **no field** that could carry one | a nullable **`caveat`** field per condition, carrying the register's `_note` |
| `docs/manifest-schemas/conditions-manifest.schema.json` | `additionalProperties: false` with no caveat property | `caveat` declared, optional and nullable, so the other conditions stay valid |
| `results/uplift-supplement/conditions.csv` | `notes` **empty** on all five rows | the register caveat carried into the existing `notes` column |

The channel covers **all 35 conditions of that run**, which is every row carrying
the E72 note, not only the five relabelled ones.

## 7. What did NOT change

Listed because a reader's first question about a job this size is what it
disturbed.

- **No committed evaluation was rewritten** anywhere, and no measured value
  moved except the two h10 unions the PI ruled should be rebuilt.
- **The Era-2 board.** Not rebuilt, not re-tiered, no signature field written.
  Its `provenance.json` still records the S153 re-signature and its
  `signature_history` is intact — see § 8 for why that mattered.
- **The 55-map final board.** `final_board_50m.json` was not rebuilt, so its
  tiering, its 595-pair BH family and `findings.md` § 4.1's gate against it are
  untouched.
- **Every signature field.** `manually_verified_at`, `_signature_note` and
  `gates.G1.pi_ruling` are unaltered everywhere. The one signed row whose
  `conditions_compared` moved is § 6.1, and only by a rename.
- **The three withheld tile-MCC cells.** Still withheld, still under the PI's
  open tile-join decision. `TILE_JOIN_DEFAULT` is still `id`.
- **Phase 1's and Phase 2's ladders.** No rung added, no number moved.
- **The registered `pass-budget-pareto-v2` efficient set**, the E83 MCB ruling,
  and the stride ladders' registered outcomes.

## 8. Item 8: why the board rebuild stopped

**The PI ruled that the 46 Phase 2 rungs and tier E join the board. The
mechanism by which they join is not ruled, and there is no mechanism that does
it without a decision.** Measured at source rather than attempted:

`scripts/build_gs_era2_board.py` `derive_membership()` refuses **all 46** on two
independent rules, and both refusals are correct behaviour rather than bugs:

1. **`:224`** — `if bounds not in (ERA2_FRAME, B_FRAME)`. Every one of the 46
   carries `eval_path` pointing at an evaluation whose `cli_args.bounds` is
   `era2_b_intersection_bounds.geojson` — the **board frame itself**, which is
   neither `full_evaluation_bounds.geojson` nor `grid_common_bounds.geojson`.
   The rule is a rule about cells whose *committed* score is on a different
   frame, and these are already on the board's.
2. **`:227`** — `if cond.get("scope_override")`. All 46 carry
   `scope_override.test_set_id: "era2-b-487"`.

This is not speculation: the board's own 39 `-era2b` rows appear in the current
`membership.json` exclusions with exactly reason 1, 39 times.

**Three routes, each with a consequence the PI should choose between.**

| route | what it means | consequence |
|---|---|---|
| (a) a third membership source | a `k-ladder/membership.json` the main builder defers to, as it already defers to `opmax/membership.json` via `opmax_owned()` | least invasive to the existing rules; adds a second handshake to maintain |
| (b) relax `:224`–`:229` | accept a committed evaluation already on `FRAME` whose `scope_override.test_set_id == FRAME_ID` | makes the **G2 gate degenerate** for those cells — its "own frame" *is* the board frame, so G2 becomes a self-comparison, which is the G5 coincidence case the card contemplates at `:203` |
| (c) hand them to the opmax builder | treat them as that builder's members | conflates two cohorts with different provenance in one membership file |

**Two further blockers that would have bitten during the rebuild**, both found
by reading rather than by running:

- **`finalise` would have destroyed signature history.** It rebuilds
  `provenance.json` from scratch carrying forward only `signed_at`, `signed_by`
  and `gates.G1.pi_ruling` (`scripts/build_gs_era2_board.py:512-531`), so the
  existing `signature_history` array and the **resolved** `re_sign_pending`
  (`"status": "RE-SIGNED 2026-09-12T06:04:30Z by the PI (S153)"`) are not carried
  and would be overwritten with a fresh `"PENDING"` block. Any rebuild must
  snapshot both first. Note also that the README's banner is **stale**: it still
  says the board "awaits the PI's re-signature", which `provenance.json`
  contradicts.
- **Three of the 46 would abort the tiering.** The three 3.7 gold-standard text
  cells are the ones the tile-join invariant refuses, and
  `ConfusionGateError` is raised and **never caught** in
  `scripts/era1_leaderboard_tiering.py` — there is no per-cell skip, so one
  refused cell kills the whole run under `--permute-mcc`. Their committed
  evaluations also still carry the pre-invariant MCC values (0.1337 / 0.1422 /
  0.1337) rather than a `withheld` record, so they would need re-scoring first —
  and re-scoring them means choosing a tile-join variant, which is the corpus-wide
  decision still open.

**Morning question 1**, and the largest of them.

## 9. Verification

| # | Check | Result | Anchor |
|---:|---|---|---|
| 1 | Tier E union counts against the PI's approved figures | **3 of 3 exact**, delta +0 | `tier-e/unions.json` |
| 2 | Crops from rasters, never tile PNGs (E33) | every rung: `raster_crops == total_detections`, `tile_fallback_crops == 0`, enforced as a pre-spend gate | `scripts/run_k_ladder_tier_e.py`, `extract_crops` |
| 3 | Candidates verified against candidates offered | **7,239 of 7,239, 0 failed** | `tier-e/spend-ledger.json` |
| 4 | Audited flex against the approval | **US$4.9595** against US$5.02; hard stop US$7.00 never approached | same |
| 5 | Per-candidate rate against the audited constant | 0.000685 against 0.000693, inside the 0.000684–0.000698 spread | same |
| 6 | Verifier configuration identical across rungs | one config file, unmodified; instruction SHA-256 `2518d529…`, the hash Phase 2 and the August 3.7 screen stamped | `tier-e/pre_launch_audit.md` § 5 |
| 7 | The construction asymmetry's mechanism | carrier-filtered counts reproduce `grid-2026-08-18/sweep.csv` exactly at K = 1/3/5 | § 2.2 |
| 8 | The two 487-tile frames' vocabularies | **set-identical**, 0 only in either | § 2.3 |
| 9 | Per-tile rebuild before any subsample | **8 of 8 rungs within 2.6e-5** of their committed board F1; the first run's 0.0000 caught and diagnosed | § 3.1 |
| 10 | h10 rebuild against the retrospective's prediction | **1,474 and 477, both exact** | § 6.2 |
| 11 | No registered condition reads the rebuilt h10 files | confirmed across three registers | § 6.2 |
| 12 | `conditions_compared` resolves | every id checked against the register before writing; the script exits non-zero otherwise | `scripts/author_k_ladder_analysis_row.py` |
| 13 | The fourth cell's sweep regeneration gates | G4 reproduces **11 of 11** committed micro-F1 values at d ±0.0000; both pass pins verified | `/tmp/sweeps.log` on sapphire, § 5 |
| 14 | Lint | `ruff check` clean on every Python file touched; `markdownlint-cli2` clean on every Markdown file touched | — |
| 15 | Tier-1 tests | TIER1_PLACEHOLDER | — |

## 10. Morning questions for the PI

Numbered, recommended answer first.

**1. The Era-2 board rebuild: which admission mechanism?**
*Recommended: route (a), a `k-ladder/membership.json` the main builder defers to
by condition id, exactly as it already defers to `opmax/membership.json`.* It
leaves the frame and scope rules — which are doing useful work on 39 other rows —
untouched, and it keeps the three cohorts distinguishable in the record. Route
(b) is tempting because it is two lines, but it makes G2 a self-comparison for
46 cells, which weakens a gate rather than satisfying it. Whichever route, the
rebuild also needs a ruling on the three refused 3.7 cells (question 4) and must
snapshot `signature_history` and the resolved `re_sign_pending` before
`finalise` runs. Also worth knowing: admitting the 46 would roughly halve the
board's Gemini 3 F1 floor, several K = 1 image rungs scoring 0.61–0.69.

**2. The signed `uplift-supplement-flatten` row's five renamed ids — confirm?**
*Recommended: yes, confirm the rename as made.* The five ids name the same five
artefacts with the same five measured values; leaving them stale would break the
register's foreign-key guard and a tier-1 test. The row's `outcome`,
`manually_verified_at` and `_signature_note` were not touched and a
`_conditions_note` records the change. If you would rather a signed row were
never edited even for a rename, the alternative is to keep the old labels as
aliases, which the register has no mechanism for.

**3. Tier E's K = 10 rung is built by a different rule — leave it, or rebuild?**
*Recommended: leave it and cite § 2.2 wherever the ladder is reported.* The
comparison across the ladder is on the board frame, which excludes the
out-of-frame candidates either way, so the F1 shape is sound; rebuilding the
K = 10 rung as a native `merge_passes` union would be a fourth verifier pass over
3,591 candidates (about US$2.49) and would change a cell the registered
`grid-postverifier-2026-08-18` analysis reports.

**4. The tile-join rule — still unruled, and now blocking two things.**
*Recommended: adopt `geometric-primary` corpus-wide, at a moment of your
choosing, and until then keep the three cells withheld.* It is the only variant
that leaves the per-tile F1 totals — and so the board's G1/G2 gate — untouched
while changing the MCC side. But it moves every published MCC by about +0.106 on
146 of 146 cells and will fail every confusion equality gate on the day it
lands, so it is a scheduled migration, not a fix. The closeout used the default
`id` join everywhere and withheld rather than guessed, per the brief.

**5. Item 2's K = 5 rung: finish it, and re-tier the 55-map board?**
*Recommended: finish the rung and register it, but do NOT re-tier the 55-map
board in the same step.* The rung can be scored and registered additively; what
re-tiering costs is a grown BH family on a committed board whose pairwise
p-values `findings.md` § 4.1 gates against. Treating the 55-map board's
membership as its own decision, as you did for Era-2, keeps the two separable.

**6. The h10 `consensus_t3/t4/t5` — rebuild, or leave?**
*Recommended: leave them.* They reproduce at identical counts and the only
difference is one cluster centroid 0.444 m from its re-derivation; `t4` is a
registered condition's detections file, and rewriting it would move a registered
artefact for no measurable gain.

**7. The analysis row's signature.** *Recommended: read `findings.md` § 8 and
§ 7.5 first, then sign.* The row is authored UNSIGNED with its outcome complete.
Two things are still missing from the review and the row says so: the Hsu MCB
admissible sets per family, and the three withheld tile-MCC cells under
question 4.

**8. No pairing-row amendment was needed.** Recorded because the brief asked for
it: the uplift supplement's pairable population and blocked count are unchanged
by this job, so the `verifier-uplift-pairing` row needs no amendment. Tier E's
six rows are board-frame rows, excluded from the supplement by your 2026-09-10
rule, exactly as Phase 2's 46 were.

## Changelog

### 2026-09-12 — Original publication

The closing report of the K-ladder closeout job, written from artefacts the job
produced and re-read in the same session: `results/k-ladder-2026-09-12/tier-e/`
(`unions.json`, `spend-ledger.json`, `pre_launch_audit.md`,
`operating-points.json`, `scores.json`, `smoke/smoke.json`);
`results/k-ladder-2026-09-12/tension/` (all three JSONs);
`results/run-conditions.json` and `results/run-analyses.json`;
`docs/methodology/preregistration/protocol-errata.md` § E85;
`archive/superseded-consensus-2026-09-12/h10-pool_160_hp4hn4/`;
`results/grid-2026-08-18/sweep.csv` and the two 487-tile bounds files, measured
directly; and `scripts/build_gs_era2_board.py`,
`scripts/era1_leaderboard_tiering.py`, `scripts/final_board_sweeps.py`,
`scripts/materialise_grid_unions.py` and `scripts/grid_analysis.py` for the
mechanisms § 2.2, § 5 and § 8 name.

Landed on branch `worktree-agent-ae1e65fd9508397ec`, not merged to `main`.
