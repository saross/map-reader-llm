# WP4b design: the frontier cost axis from the register

> **Last revised**: 2026-10-04 (original publication). See
> [§ Changelog](#changelog) for revision history.

WP4b of `planning/cost-accounting-fix-plan-2026-09-21.md`, on branch
`wp4b-frontier-cost`. The Pareto frontier is a paper result and its cost
axis was hand-entered; this replaces every hand-entered figure with one
derived from the passes register (`results/passes-manifest.json`), so each
cost traces to named register rows.

## 1. The ruling this implements

D19 as amended 2026-10-04 (`planning/pi-decisions-2026-09-20.md`): every
configuration's own tokens are priced at **one uniform discounted tier**.
Flex and batch carry identical rates for every model on the rate card
(`data/pricing/gemini-rate-card.json`; Gemini 3.5 Flash's cached input
differs by a fraction of a cent), so the uniform tier is written `flex`.
Consequences:

- A configuration is never penalised for how it was billed: not for the
  cached-path defect, and not for runs made before the project knew of
  discounts.
- The frontier needs no tier archaeology. The as-billed register
  (`cost_usd`) is untouched; it remains the basis of the honest total.
- Superseded and aborted executions (D22) are in no configuration's cost.

Scope (PI, 2026-10-04): all three current, paper-facing cost frontiers.

## 2. The three frontiers and their hand-entered inputs

| Frontier | Builder | Output | Hand-entered inputs |
|---|---|---|---|
| 55-map deployment board, cost-efficiency table | `scripts/final_board_build.py` | `results/55map-final-board-r2-2026-09-06/final-board-50m.md` § "Cost efficiency" and `final_board_50m.json` `cost_usd` | `FAMILY_COST` (`:153`): 13 figures on a mixed basis, 9 families `None` (dropped from the table) |
| Gold-standard (GS) cost-weighted Pareto v2 | `scripts/build_pareto_v2.py` | `results/verifier-robustness/pareto/pareto_v2.json`, `.png` | `MIN_PASS_USD` 0.266, `HIGH_PASS_USD` 2.29, `VF_CALL_USD` 0.000693 (`:85-87`), from `reports/token-load-audit-2026-06-12.md` § 5 |
| K-ladders, Phase 1 and 2 | `scripts/build_k_ladder_tables.py`, `scripts/build_k_ladder_phase2_tables.py` | `results/k-ladder-2026-09-12/ladders.json`, `phase2/ladders.json`, `phase2/ladder-tables.md`, two figures | `GS_STRIDE_A_COST_USD`, `ARM_*` (`:68-81`); `MIN/HIGH/G37_PASS_USD`, `VF_CALL_USD` (`:123-126`); Phase 1 also reads the board's `cost_usd` |

Superseded and not rebuilt: Pareto v1, the r1 board, the
secondary-effects cost columns (legacy constants US$2.00 and US$0.75 per
run).

## 3. Unit costs

A new library, `scripts/lib_frontier_cost.py`, derives two units from the
register at the uniform tier.

- **Proposer pass unit** for a (run, pool): the mean, over the pool's
  passes, of each pass's own fragments re-priced at `flex`. Fragments are
  read exactly as WP3 reads them (`lib_pass_cost.fragment_usage`, each
  fragment's own model and date), so recovery fragments are included and
  the 2026-05-02 doubled metas read their per-item sums.
- **Verifier candidate unit** for a leg: the leg's own fragments re-priced
  at `flex`, divided by the candidate verifications it produced
  (`probabilities.json` results times its iterations). Retries are spend,
  so they stay in the numerator. This is per verified candidate, not per
  request: T03's leg made 10,539 requests for 9,910 results.

**Floors.** Four family legs are lower bounds in the register because a
cleanup overwrote the main record, and no backup meta survives on either
machine: TM, IM, stride A's union leg, and FOURTH's 3.7 leg. D19: a floor is
completed from comparable legs' per-candidate cost, labelled as such. The
comparable set is strict: **audited legs with an identical verifier
configuration** (model, temperature, thinking level, system-instruction
hash, prompt version). The completed cost is the floor leg's own candidate
verifications times the pooled unit (sum of cost over sum of
verifications). Checked 2026-10-04:

| Configuration | Audited comparables | Unit (US$ per candidate) |
|---|---|---|
| Gemini 3 Flash, T 0, minimal, `2518d5298d9b` | TH7, T03, uplift, stride B, ARM1 | 0.000682 to 0.000699 each |
| Gemini 3.7 Flash, T 0, low, `2518d5298d9b` | ARM2 | 0.001125 (16,799 requests for 12,715 results) |

## 4. Configuration costs

- **A family rung** (N of a K-pass run): N times the proposer unit, plus the
  rung's union size times its family leg's unit. The union sizes are the
  committed ladders' `union_n` (`results/stride55-2026-08-27/ladder.json`,
  `results/gemini37-55map-2026-08-31/ladder/ladder.json`,
  `results/gemini37-fourth-cell/55map/g384_ov192_55map/ladder.json`),
  which is how `scripts/stride55_ladder.py` already costs a rung.
- **A full run** (a family at N = K, and the carried incumbents): all its
  passes plus its verifier leg's own cost (completed, if a floor).
- **The uplift** (UPL): the five text-minimal passes, the five uplift
  passes, and the `verified-3of10` leg.
- **Pareto v2 rungs** keep their formula (passes x pass unit + crops x
  verifier N x candidate unit; 55-map units scaled by 487/8,541). The units
  come from the register: the minimal pass from the ten 55-map minimal
  passes (text-min generalisation and the n10 uplift), the HIGH pass from
  the five T 0.7 text-high passes, the candidate unit from the pooled
  Gemini 3 Flash comparables. The June anchor leg for the candidate unit
  (`outputs/verifier-robustness/.../T0.3/verified`, US$0.000693) is not in
  the register (see § 6); the pooled unit is 0.000685.
- **K-ladder rungs**: the same units, the arms' legs from the register
  (`ARM_PROPOSER_USD_TOTAL` 144.27 and `ARM_VERIFIER_USD` 8.890222 /
  14.3055 reproduce exactly), Phase 1's board join from the rebuilt board.

## 5. Prototype (2026-10-04, scratch): the board's 22 families

| Family | Register-derived (US$) | `FAMILY_COST` (US$) | Note |
|---|---:|---:|---|
| A-N1, A-N3, A-N5, A-N10 | 20.40, 41.00, 59.45, 103.42 | 20.53, 41.22, 59.75, 103.91 | within 0.5 % |
| B-N1, B-N3, B-N5, B-N10 | 30.79, 65.10, 96.67, 172.67 | 30.99, 65.48, 97.22, 173.59 | within 0.6 % |
| TH7, T03, UPL | 207.35, 261.15, 57.89 | 207.4, 261.0, 57.87 | within 0.1 % |
| TM | 30.33 | 23.4 | old figure omitted the verifier (a floor); completed adds 10,170 x 0.000685 |
| IM | 200.75 | 195.4 | old figure omitted the verifier (a floor); completed adds 7,878 x 0.000685 |

The prototype pooled four Gemini 3 Flash legs (TH7, T03, uplift, stride B:
US$0.0006851 per candidate); the build pools every audited comparable,
ARM1 included, so TM and IM move by a cent or so.
| ARM1-N1, -N3, -N5 | 34.75, 94.31, 153.16 | None | first figures |
| ARM2-N1, -N3, -N5 | 38.33, 99.03, 158.58 | None | first figures |
| FOURTH-N1, -N3, -N5, -N10 | 42.14, 81.40, 116.15, 198.17 | None (no N5 entry) | first figures; N10 completed from ARM2's unit |

**The frontier will change**: nine 3.7 families enter the efficiency table
for the first time, and TM moves up by 30 %. Membership before and after
is reported to the PI before merge.

## 6. Gaps found (dry run)

1. **`verifier-robustness` is registered but has no register rows**: the
   generator never extracted its legs, so Pareto v2's June anchor leg
   cannot be cited. Worked round with the pooled unit (§ 4); extracting the
   run is a separate register fix.
2. **Four floor legs**, completed per § 3. T03 is NOT a floor (audited,
   US$6.90; removed from the overrides 2026-10-03).
3. **`FAMILY_COST` has no FOURTH-N5 entry**, although the r2 board's
   addendum carries a FOURTH-N5-carried cell (`cost_usd` null); the rebuilt
   table covers every family the board has, addendum included.
4. Rung union sizes exist only for N in {1, 3, 5}; N = 10 (and N = 5 for
   the arms) is the full run, costed from its leg.
5. Still to map in the build: Phase 2's per-family pass anchors (several
   "scaled" or "unmeasured", e.g. `min-image-unmeasured`), its
   `spend-ledger.json` verifier legs, and `G37_PASS_USD` (1.714, a GS
   3.7 screen pool) against the register.

## 7. Build steps

1. `lib_frontier_cost.py` with tests: units, floors, provenance, and a red
   sentinel per rule. The comparables check refuses a mismatched
   configuration.
2. A committed mapping, `data/pricing/frontier-configurations.json`: each
   board family, Pareto rung and K-ladder rung, its register rows, its
   union size source, and how any floor is completed. Reviewed by the PI.
3. The three builders read the library; their formulas stay. A builder
   test that every figure traces to register rows.
4. Regenerate on sapphire; report the frontier membership before and
   after.
5. Two-lens `/audit` and re-audit; branch + PR.

## Changelog

### 2026-10-04 — Original publication (Session 158)

Design written after the PI's two rulings of 2026-10-04 (uniform discount
tier; all three frontiers), with the dry-run prototype of § 5.
