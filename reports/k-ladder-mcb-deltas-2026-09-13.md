# The K-ladder MCB job: what changed, with anchors

> **Last revised**: 2026-09-13 (original publication). See
> [§ Changelog](#changelog) for revision history.

**What this reports.** The Principal Investigator (PI) gave two rulings on
2026-09-13 (afternoon) on the K-ladder review
(`planning/k-ladder-review-2026-09-11.md`):

1. **"Wait for the sets", then sign** — supply the per-family Hsu
   multiple-comparisons-with-the-best (MCB) admissible set, the review's last
   outstanding run-card requirement, before the analysis row
   `k-ladder-2026-09-12` is signed.
2. **The carried convention** — the stride ladder's own vote shell is *the*
   carried point; ruling R2's literal `k = K` stays as a disclosed column.

Both landed. **Zero Application Programming Interface (API) calls; US$0 spent.**
All MCB computation ran on sapphire in an isolated worktree
(`~/worktrees/map-reader-llm/claude-mcb`, removed afterwards). Every claim below
names the file it was read from.

**One-line answer.** K = 3 is admissible on 12 of the 22 tiered ladders and is
the cheapest admissible rung on 10; **no** ladder's F1-admissible set excludes
K = 10; K = 1 is ruled out on F1 on 20 of 22 ladders and admissible on tile-level
Matthews Correlation Coefficient (MCC) on **22 of 22**; one family is withheld
whole; and the carried columns are re-labelled without a single number moving.

---

## 1. The instrument, and its gate

**The instrument is the Era-2 board's own MCB step, unmodified.**
`scripts/selection_aware_intervals.py --board` — Hsu's (1984) constrained
one-sided form on `theta_i = stat_i - max(j != i) stat_j`, a rung ruled out as
best only when its simultaneous **upper** bound falls at or below zero, the
critical value bootstrapped over **tiles** rather than read from Dunnett's table.
10,000 resamples, seed 42, m-out-of-n fraction 1.0, simultaneous 95 %. This is
the same tool and the same parameters the board's own
`mcb/gs-era2-verified-board-2026-09-10_b20_m1.json` was produced with (that
artefact's `bootstrap`, `m_frac`, `seed` and `buffer_metres` fields; the board
`README.md`'s 2026-09-12 and 2026-09-13 entries describe the step).

**Each ladder runs on its own frame, reference and headline buffer** — the ones
its committed tiering used, held in one registry in the new driver
`scripts/k_ladder_mcb.py`:

| group | ladders | frame | reference | buffer |
|---|---:|---|---|---:|
| gold standard (stride A, exact re-verification) | 1 | `era2-b-487` by override | curator (`mounds-reference.geojson`) | 20 m |
| tier E (grid 384 px / 50 % MINIMAL text, verified) | 1 | `era2-b-487` by override | curator | 20 m |
| Phase 2 `pv-diag-384` families | 13 | `era2-b-487`, the cells' own | curator | 20 m |
| 55-map deployment | 7 | 8,541-tile `55maps_evaluation_bounds`, the cells' own | r2 or standardised, the cells' own | 50 m |

**The gate, before any set was read.** All **44 runs** (22 ladders × 2 metrics)
had to reproduce their ladder's committed `tiering_<buffer>m.json` ranking: the
candidate label set exactly, each rung's `observed_micro_f1`, and each rung's
`mcc`. **170 candidate rows gated, all passed, maximum absolute deviation
4.958e-05** — `results/k-ladder-2026-09-12/mcb/summary.json`, key
`gate_all_passed: true` and each ladder's `gates[].candidates[].abs_delta`.

**Why the committed tiering and not the ladder inventories.** The first gate
attempt read tile-MCC from `results/k-ladder-2026-09-12/ladders.json` and refused
a correct run: that inventory records the gold-standard ladder's tile-MCC on its
**grid-common** frame (0.7894 at K = 1) while this MCB runs it on the **board**
frame (0.7834, the value `findings.md` § 2's table publishes). The gate reference
is now the committed tiering for both metrics, which was produced on the same
frame, over the same cells, at the same operating points. The wrong-frame trap is
pinned by a tier-1 test.

## 2. The MCB result, claim by claim

Every figure here is from `results/k-ladder-2026-09-12/mcb/summary.json` (the
`roll_up` block and the per-ladder `f1` / `mcc` blocks); the rendered table is
`mcb/table.md` and is reproduced in `findings.md` § 6.1.

| claim | value | anchor |
|---|---:|---|
| ladders with an admissible set | **22** of 23 | `summary.json` `n_ladders` |
| — on F1 and on tile-MCC each | **22 / 22** | each ladder's `f1`, `mcc` blocks |
| F1 set contains K = 3 | **12 of 22** | `roll_up.ladders_whose_F1_admissible_set_contains_K3` |
| K = 3 is the CHEAPEST admissible rung | **10 of 22** | per-ladder `hsu_admissible_K` minima |
| F1 set excludes K = 10 | **0** of the 20 ladders that have a K = 10 rung | `roll_up.ladders_whose_F1_admissible_set_excludes_K10` (empty) |
| F1 set contains K = 1 | **2 of 22** | per-ladder `hsu_admissible_K` |
| F1 set is the WHOLE ladder | **2 of 22** | `roll_up.…_F1_…_is_the_whole_ladder` |
| F1 set is a SINGLE rung | **1** (55-map stride B, 3.7 verifier: {K = 10}) | that ladder's `f1.hsu_admissible_K` |
| tile-MCC set contains K = 1 | **22 of 22** | `roll_up.ladders_whose_MCC_admissible_set_contains_K1` |
| K = 1 holds the highest tile-MCC | **13 of 22** | per-ladder `mcc.best_K` |
| tile-MCC set is the WHOLE ladder | **12 of 22** | `roll_up.…_MCC_…_is_the_whole_ladder` |
| tile-MCC set excludes K = 10 | **7** of the 20 that have one | per-ladder `mcc.hsu_admissible_K` |
| tile-MCC set is {K = 1} alone | **2** (55-map stride B 3.7 vf; 3.7 arm 2) | same |
| simultaneous F1 width `w_upper`, 487 tiles | **0.0151–0.0326** (15 ladders) | per-ladder `f1.hsu_w_upper`, `f1.n_tiles` |
| simultaneous F1 width `w_upper`, 8,541 tiles | **0.0047–0.0056** (7 ladders) | same |

**What these say, in four sentences.** *(a)* The review's Pareto reading — K = 3
on every ladder's efficient set — is endorsed by the simultaneous instrument on
roughly half the corpus and declined on the other half: on nine ladders nothing
below K = 5 is admissible, even though K = 3 remains the efficient *buy*, so
"K = 3 is on the efficient set" is a cost claim rather than a statistical one.
*(b)* The top rung is never statistically excluded, only never worth its price —
the formal counterpart of § 7.4's US$1,100-to-US$43,000 per 0.001 F1 figures.
*(c)* The review's "the two objectives select different rungs" finding now has
its sharpest statement: **on F1 the cheapest rung is almost always ruled out; on
tile-level discrimination it never is.** *(d)* Resolution tracks the corpus, not
the response to K: the simultaneous band is three to six times narrower on 8,541
tiles than on 487, which is § 8's subsampling result in the MCB's own units.

## 3. The carried-column changes

**The ruling.** The stride ladder's own vote shell — k = 1 / 3 / 4 / 8 at
K = 1 / 3 / 5 / 10, the four `stride-phaseb-2026-08-25` rungs' own `k` column —
is the carried point. `k = K` stays as a disclosed column.

**What changed, and what did not.** `scripts/build_k_ladder_phase2_tables.py`
goes to **v1.1.0**. In every per-family table of
`results/k-ladder-2026-09-12/phase2/ladder-tables.md`:

| before | after |
|---|---|
| `carried k=K F1@20` (first), `carried shell F1@20` (second) | `carried F1@20` = the shell reading (first), `carried F1@20, k = K (disclosed)` (second) |

**No number was recomputed.** Both readings were already scored and committed by
`scripts/derive_k_ladder_committed_carried.py` in
`phase2/committed-carried/scores.json`, and the table now sources the headline
column from the `stride-shell` block and the disclosure column from
`k-equals-K`. They coincide at K ≤ 3, so only the committed K = 5 and K = 10
rungs of the thirteen `pv-diag-384` families are affected, and for those two rows
the two columns **swapped places**. Worked example, MINIMAL text T 0.3
(`ladder-tables.md`, first table):

| K | carried F1@20 (before: `k = K`) | carried F1@20 (after: shell) | disclosed `k = K` |
|---:|---:|---:|---:|
| 1 | 0.8555 | 0.8555 | 0.8555 |
| 3 | 0.8586 | 0.8586 | 0.8586 |
| 5 | 0.8492 | **0.8635** | 0.8492 |
| 10 | 0.8320 | **0.8582** | 0.8320 |

Two further re-sourcings, both no-ops in value: the compatibility inventory's
`carried` operating-point basis now reads the `stride-shell` block (it is used by
one family only, the 3.7 gold-standard text screen, whose two readings coincide
at every rung), and `phase2/ladders.json` gains a `carried_convention` block
recording the ruling, the reported reading, and the disclosed one.

**One disclosure the ruling surfaced, which nothing had recorded.** Reading the
ruling back against `findings.md` § 3's committed 55-map cells shows the two
stride ladders were built on **different readings** of "carried":

| table | committed carried cells | reading |
|---|---|---|
| § 3.1 stride A | `…-n3-carried-posthoc-p0.15-k3`, `…-n5-carried-p0.15-k4`, `…-n10-carried-p0.15-k8` | **the stride shell** |
| § 3.2 stride B | `…-n3-carried-posthoc-p0.15-k3`, `…-n5-carried-p0.15-k5`, `…-n10-carried-p0.15-k10` | **`k = K`** |
| § 3.3 stride B, 3.7 vf | `…-n10-verified37-carried-p0.98-k10` | **`k = K`** |
| § 3.4 arms 1 and 2 | `arm1-n5-carried-p0.10-k5`, `arm2-n5-carried-p0.80-k5` | **`k = K`** |

Anchor: each cell's `vote_threshold` in `results/run-conditions.json` under
`decomposition` keys `stride-55map-2026-08-25` and `gemini37-55map-2026-08-29`.
§ 3 now carries this table and states the consequence: **§§ 3.2–3.4's transfer
taxes are `k = K` taxes and are an upper bound on the transfer cost** under the
ruling's convention, since `k = K` costs up to −0.2566 F1@20 where the shell
costs at most −0.0735. **No § 3 number was changed**, because no shell-reading
carried cell exists for those ladders and building one is a rescore the PI has
not asked for.

## 4. Two findings worth the PI's attention

**(1) The MCB and the greedy clique disagree in BOTH directions.** The committed
tie set is a rank band from pairwise permutation plus Benjamini-Hochberg plus a
greedy clique; the admissible set is simultaneous by construction. Compared
ladder for ladder, the F1-admissible set is **smaller** than the committed tie
set on two ladders and **larger** on six — which is exactly what erratum E83 and
defect D20 warn of. The sharp case: `findings.md` § 7.1 reports four MINIMAL
ladders that "greedy-clique into a single tier, where K buys nothing detectable
at all", and under MCB only **two of those four** are admissible whole — MINIMAL
text T 0.3 and MINIMAL image T 1.0 both rule K = 1 out as best, giving
{3, 5, 10}. § 7.1 is **not withdrawn**: a within-ladder pairwise BH family and a
simultaneous comparison against the best answer different questions, and the
pairwise one is the registered tiering instrument. But "one tier" must not be
read as "every rung could be the best one", and § 6.1 now says so.

**(2) A degenerate tie returns an EMPTY admissible set.** Hsu's rule admits a
candidate only when `theta_i + w_upper > 0`. Four *byte-identical* rungs give
`theta_i = 0` on every resample, so `w_upper` is exactly 0 and the strict
inequality rules out even the empirical best. No real ladder is byte-identical —
`degenerate_zero_width` is `false` on all 44 runs — but the behaviour is now
pinned by a tier-1 test and flagged in the summary artefact, so an empty set can
never be misread as "no rung can be the best".

## 5. What did NOT change

- **Every F1 and tile-MCC point estimate** in `findings.md` §§ 2–8, in the
  Phase 2 tables, and in the ladder inventories.
- **Every cost figure.** This job spent **US$0** and made zero API calls.
- **§ 4.1's and § 4.2's permutation results** and their BH p-values; the tiering,
  tiers and tie sets of all 22 committed ladders (no tiering was re-run).
- **The Era-2 board**: not re-tiered, not re-signed, not re-scored, no membership
  change. **The 55-map final board**: untouched.
- **Every signature field.** The review row's `manually_verified_at` is still
  `null` — it is the PI's to set — and no other register row was edited.
- **The withheld cells stay withheld.** The three Gemini 3.7 gold-standard text
  rungs' per-tile table is still refused on this frame, so that family has no
  admissible set on either metric and is listed rather than dropped
  (`mcb/summary.json` key `withheld`). Lifting it needs the corpus-wide
  tile-join decision, still open.

## 6. Artefacts and verification

| artefact | what it holds |
|---|---|
| `scripts/k_ladder_mcb.py` | the driver: ladder registry, the runs, the gate, the collation, the § 6.1 table |
| `tests/test_k_ladder_mcb.py` | 17 tier-1 tests, including a synthetic four-rung ladder run through the real instrument |
| `results/k-ladder-2026-09-12/mcb/<ladder>/*.json` | 44 raw MCB artefacts, each reproducible from its own metadata |
| `results/k-ladder-2026-09-12/mcb/summary.json` | roll-up, gate record, withheld family |
| `results/k-ladder-2026-09-12/mcb/table.md` | the generated § 6.1 table |
| `results/k-ladder-2026-09-12/findings.md` | § 2.1, § 3, § 6.1, § 6.2, § 7.5 revised; changelog entry |
| `planning/k-ladder-review-2026-09-11.md` | banner, § 6's step-5 scope note, changelog |
| `results/run-analyses.json` | the row's outcome and `_signature_note`; still UNSIGNED |

**Verification run**: `ruff check` clean on every touched script;
`npx markdownlint-cli2` clean on every touched Markdown file; tier-1 suite
**2,494 passed, 6 skipped, 3 xfailed**; `generate_hypothesis_outcome_table.py
--check` reports up to date.

## Changelog

### 2026-09-13 — Original publication

Written with the MCB job, which executed the PI's two rulings of 2026-09-13
(afternoon) at US$0: the per-family Hsu MCB admissible sets for all 22 tiered
ladders on F1 and tile-MCC, and the carried convention. The document's initial
state is § 1's instrument and gate, § 2's fourteen-row claims table, § 3's
carried-column changes and the 55-map reading disclosure, § 4's two findings,
§ 5's what-did-not-change list, and § 6's artefact index.
