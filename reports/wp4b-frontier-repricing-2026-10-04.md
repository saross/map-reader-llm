# WP4b: the frontiers re-priced from the register — walkthrough for the PI

> **Last revised**: 2026-10-04 (later, Session 159: § 2's carried frontier
> corrected — it omitted B-N3-carried — and the oracle-versus-carried
> decision ruled, D24: both frontiers on the board). Earlier: (the PI's
> sign-offs: all three signature
> notes given; the T0.7 families reconciled; a K-ladder units error
> corrected). See
> [§ Changelog](#changelog) for revision history.

Branch `wp4b-frontier-cost`. Three signed analyses change their cost axis:
the r2 55-map final board (`55map-final-board-r2-2026-09-06`, signed
2026-09-17), the gold-standard (GS) Pareto v2 (`pass-budget-pareto-v2`,
re-signed 2026-09-12), and the K-ladders (`k-ladder-2026-09-12`, signed
2026-09-13). Under the signature policy
(`docs/methodology/signature-policy.md`), a re-pricing is recorded as a
dated signature note (the D9 pattern) and never silently. This document
gives what the PI needs to approve, amend or refuse those notes. No
F1, tile Matthews Correlation Coefficient (MCC), tier, group or pairwise
result changes anywhere: only dollars.

## 1. What changed, and why

PI ruling D19, amended 2026-10-04 (`planning/pi-decisions-2026-09-20.md`):
every configuration's own tokens are priced at one uniform discounted tier
(flex, which equals batch for every model on the rate card). No
configuration is penalised for how it was billed: not for the cached-path
defect, and not for runs made before the project knew of discounts. The
second ruling of the day: all three frontiers move, and the Phase 2
K-ladder families are priced at their own measured passes where recorded.

Every cost now comes from the passes register through
`scripts/lib_frontier_cost.py` and the mapping
`data/pricing/frontier-configurations.json`, which names the register rows
of every configuration. Design and dry run:
`planning/wp4b-frontier-cost-design-2026-10-04.md`.

A verifier leg that is a floor in the register (a cleanup overwrote its main
record; no backup meta survives) is **completed** from nominated comparable
legs with an identical verifier configuration (D19), and marked `†`. Four
legs: TM, IM, stride A's union leg, and the fourth cell's 3.7 leg.

## 2. The r2 final board

| Family | Before (US$) | After (US$) | Why |
|---|---:|---:|---|
| A-N1 / N3 / N5 / N10 | 20.53 / 41.22 / 59.75 / 103.91 | 20.40 / 41.00 / 59.45 / 103.42 † | within 0.7 % |
| B-N1 / N3 / N5 / N10 | 30.99 / 65.48 / 97.22 / 173.59 | 30.79 / 65.10 / 96.67 / 172.67 | within 0.7 % |
| TH7 / T03 / UPL | 207.4 / 261.0 / 57.87 | 207.35 / 261.15 / 57.89 | within 0.1 % |
| TM | 23.4 | 30.40 † | the old figure omitted the floored verifier |
| IM | 195.4 | 200.80 † | the same; its proposer is US$195.35 at the uniform tier (billed US$359.65) |
| ARM1-N1 / N3 / N5 | — | 34.75 / 94.31 / 153.16 | first figures |
| ARM2-N1 / N3 / N5 | — | 38.33 / 99.03 / 158.58 | first figures |
| FOURTH-N1 / N3 / N5 / N10 | — | 42.14 / 81.40 / 116.15 / 198.17 † | first figures |

**The efficiency frontier's membership changes** (a paper result):

- before: A N = 1 → A N = 3 → A N = 5 → B N = 3 → B N = 5;
- after: A N = 1 → 3.7 arm 1 N = 1 → 3.7 arm 2 N = 1 → fourth cell N = 3
  → 3.7 arm 2 N = 3.

The 3.7 runs' deployment-basis cells were unpriced, and so absent, not
dominated: the old frontier was an artefact of their missing costs. A
caution for the paper: ALL FIVE new frontier rows are ORACLE cells (the
board's deployment basis where no carried point exists, as for every run),
where four of the old five were carried. On the carried basis the frontier
runs A N = 1 → ARM2-N1-carried (0.8459, US$38) → B-N3-carried (0.8477,
US$65) → FOURTH-N3-carried (0.8744, US$81) → ARM2-N3-carried (0.8802,
US$99) → ARM2 N = 5 carried (0.8827, US$159), the 3.7 N < 5 carried cells
being the addendum's post-hoc carried-analogues; ARM1-N1-carried (0.7859
at US$35) drops out, dominated by A N = 1 (0.8227 at US$20.40).
**Corrected 2026-10-04 (Session 159):** this paragraph first omitted
B-N3-carried, which beats ARM2-N1-carried by 0.0018 F1 and so is on the
carried frontier. The PI then ruled for both frontiers on the board (D24);
the board's efficiency section now shows them.

Applied by `scripts/final_board_cost_refresh.py`, which rewrites only the
cost fields, the cost sentence and the efficiency section; the tiered
board, its 595 pairs and the addendum are byte-identical (checked).

## 3. The GS Pareto v2

The three units come from the register: the minimal and HIGH passes
(55-map passes at the uniform tier, scaled 487/8,541) and the Gemini 3
Flash verifier per candidate (pooled over the 55-map generalisation
campaign's four complete legs). They reproduce the June audit's
0.266 / 2.29 / 0.000693 as 0.2659 / 2.2914 / 0.000692.

**Nothing moves that matters.** Both efficient sets are unchanged (F1:
min6, min11, high31, high35; MCC: min6, min11), tiers and pairwise results
are identical, and every rung's cost moves by less than 0.1 % (largest
0.094 %).

The June audit's anchor leg for the verifier unit (the GS opmax run,
`outputs/verifier-robustness/.../T0.3/verified`) is not in the register,
because the `verifier-robustness` run's legs were never extracted. That is
a register gap, queued.

## 4. The K-ladders

**Phase 1** (`results/k-ladder-2026-09-12/ladders.json`):

- **A defect, corrected.** The cost lookup was keyed by pool alone, and
  stride B's union was verified twice (Gemini 3, family B; Gemini 3.7, the
  fourth cell). The fourth cell's ladder therefore carried stride B's
  Gemini 3 costs (US$30.99 / 65.48 / 173.59 at K = 1 / 3 / 10), while the
  builder's own documentation said its costs were not supplied. It now
  carries its own: US$42.14 / 81.40 / 198.17 †.
- The 3.7 arms' K = 1 and K = 3 rungs were priced with the full K = 5
  union's verifier (an upper bound); they now price their own unions
  (arm 1: 37.74 → 34.75 and 95.45 → 94.31; arm 2: 43.16 → 38.33 and
  100.87 → 99.03). K = 5 is unchanged.
- The GS stride-A ladder reproduces its findings figures within US$0.02
  (1.3774 / 2.6411 / 3.8056 / 6.5445 against 1.38 / 2.64 / 3.81 / 6.56).

**Phase 2** (`phase2/ladders.json`, `ladder-tables.md`): each family at its
own measured GS passes where the register records them (ten of fourteen).
The T0.7 text families keep the 55-map T0.7 measurement scaled; the T0.7
image families take the mean of their own T0.3 and T1.0 passes (labelled
interpolated).

- **Every ladder's efficient rungs are unchanged**: efficiency is decided
  within a ladder, where the pass unit is constant.
- Dollar levels move per family. The largest: the **MINIMAL image**
  ladders had borrowed the MINIMAL text unit (0.266) and now cost their
  own measured pass (0.573), so their all-in rises 1.4x to 1.9x (T0.3
  K = 10: US$3.43 → 6.50). HIGH text T0.3 rises 15 % (own pass 2.64);
  HIGH image T1.0 and scale-4 fall 13 to 17 %.
- `cost_share_at_k3` moves accordingly (MINIMAL image: about 40 % → 36 %).
- **Reconciled (PI, 2026-10-04):** all four T0.7 families, text and image,
  are priced at the plain mean of their own GS T0.3 and T1.0 passes. The
  text families had first taken the 55-map T0.7 measurement (0.2659 for
  MINIMAL), 6.6 % and 8.1 % below their GS neighbours because the 55-map
  corpus is sparser. MINIMAL text T0.7 is now 0.2869, HIGH text T0.7 2.3958.
- The committed K = 5 and K = 10 rungs' verifier legs are priced at the
  pooled unit rather than their own legs (within 1.5 %; pennies).
- **A units error in the signed row and the findings** (found preparing the
  sign-off): "US$1,100 to US$43,000 per 0.001 F1" are per UNIT of F1. Per
  0.001 F1 the last steps cost about US$0.2 (MINIMAL image T0.7) to US$43
  (3.7), and four ladders' last steps lose F1; findings §§ 5 and 7.4 carry
  the same 1,000x slip (stride B: US$17, not US$17,400). The ordering is
  unchanged. Recorded in the K-ladder signature note.

## 5. Things the PI should know

1. **The fourth cell's verifier, two estimates.** The register completion
   (ARM2's per-candidate unit, US$64.67) is the figure the 2026-09-11
   billing reconciliation also simulated (its § 3: US$64.7). The same
   reconciliation isolated the leg from its billing day at about US$58 (its
   § 3.1), the basis the PI approved for the results draft on 2026-09-12. The
   frontier uses the D19 completion; the invoice bound is 3 % of
   FOURTH-N10's US$198 and moves no frontier membership (FOURTH-N3 is on
   the frontier either way).
2. **A defect in the results draft.** `docs/paper/results-draft.md` § R7.2
   prices the fourth cell at "≈ $231 (proposer $173.59 audited (B, K = 10)
   + verifier ≈ $58)". US$173.59 is B's ALL-IN figure, which includes B's
   own Gemini 3 verifier (about US$39). The fourth cell does not use that
   verifier, so ≈ $231 overstates it by about that much. The uniform-tier
   figure is US$198.17 (or about US$191.50 with the invoice bound).
3. **Documents that quote the old figures** and need refreshing once the
   PI signs off (not edited here): `results/k-ladder-2026-09-12/findings.md`
   (B and fourth-cell ladder costs), `results/stride55-2026-08-27/findings.md`,
   `results/verifier-robustness/verifier-robustness-findings.md` § 15,
   `docs/paper/results-draft.md` §§ R6, R7.2,
   `docs/paper/results-claims-inventory-2026-09-12.md` R6, and the
   continuity file.

## 6. Signature notes — GIVEN 2026-10-04

The PI approved all three notes, each in the D9 pattern: the original
signature stands, the prior attests text is kept in the row's `history`,
and the dated note is appended (`results/run-analyses.json`).

| Row | Approved (UTC) |
|---|---|
| `55map-final-board-r2-2026-09-06` | 2026-10-04T00:25:02Z |
| `pass-budget-pareto-v2` | 2026-10-04T00:25:02Z |
| `k-ladder-2026-09-12` | 2026-10-04T02:49:10Z (after the T0.7 reconciliation; with the units correction) |

The drafts as first proposed, kept for the record:

- **`55map-final-board-r2-2026-09-06`**: "Cost axis re-priced
  2026-10-04 (WP4b, D19 amended): each family's register tokens at the
  uniform discounted tier; four floored verifier legs completed from
  comparable legs (†). Tiers, groups, pairs and F1 unchanged. The
  efficiency frontier's membership changes because the nine 3.7 families
  are priced for the first time (§ 2 of
  `reports/wp4b-frontier-repricing-2026-10-04.md`). The signature stands
  for the tiering; the cost axis is re-approved as of this note."
- **`pass-budget-pareto-v2`**: "Units re-derived 2026-10-04 from the
  register at the uniform tier (0.2659 / 2.2914 / 0.000692); efficient
  sets, tiers and pairs unchanged; costs within 0.1 %."
- **`k-ladder-2026-09-12`**: "Re-priced 2026-10-04: Phase 1's fourth-cell
  ladder corrected from stride B's costs to its own; the arms' N < 5 rungs
  priced on their own unions; Phase 2 families at their own measured GS
  passes (MINIMAL image 1.4x to 1.9x). Every ladder's efficient rungs
  unchanged."

## Changelog

### 2026-10-04 (Session 159) — carried frontier corrected; D24 executed

Recomputed with the board's own row selection before the decision went to the
PI: B-N3-carried (0.8477, US$65.10) is on the carried frontier, between
ARM2-N1-carried and FOURTH-N3-carried, and § 2 had left it out. The PI ruled
for both frontiers on the one signed board (D24,
`planning/pi-decisions-2026-09-20.md`); the board's efficiency section and
`efficiency_frontiers` JSON block now carry them
(`results/55map-final-board-r2-2026-09-06/`). § 5.2's fourth-cell defect is
corrected in the draft and in the two reports it came from (D26).

### 2026-10-04 (sign-offs) — notes given; T0.7 reconciled; units corrected

The PI approved the three signature notes (§ 6, with times); ruled that
all four Phase 2 T0.7 families take their GS-neighbour mean (§ 4); and the
K-ladder note records a 1,000x units error found in the signed row and the
findings (§ 4). The oracle-versus-carried frontier presentation is queued
as an open decision (one signed board, two efficiency frontiers
recommended). Commits `5eaa8cb9f`, `2e0c2941d` and the note commit after.

### 2026-10-04 (later) — audit lens A corrections

Precision claims corrected (A and B within 0.7 %, not 0.5 / 0.6 %; stride
A within US$0.02, not "to the cent"; Pareto v2 stays within 0.1 %, largest
0.094 % after the fix, a brief "0.12 %" having described the pre-fix
output); "the 3.7 runs were never dominated" narrowed to their
deployment-basis cells, with the oracle-basis caution (all five new
frontier rows are oracle cells) and a carried-basis frontier for
comparison; the two estimation choices added to § 4 with their exact
gaps. A counting fix (results merged from an unpriced cleanup)
moved TM from US$30.39 to US$30.40; no membership changed. Commit
`61ab7a446` and the regeneration after it.

### 2026-10-04 — Original publication (Session 158)

Written for the PI's review of WP4b before merge, from the outputs
regenerated on sapphire at `0a5cadaf4` (Pareto v2 and K-ladders) and the
board refresh at `927d99ced`.
