# D64: A-06's registered rule on the same-day genuine-Pro 2 × 2

> **Last revised**: 2026-10-15 (P12 results: the confirmatory test on
> image passes 4–6 finds C1, the image thinking contrast at T 0.0, PARTLY
> replicated and C2, the image temperature contrast at MEDIUM, REPLICATED,
> so the approved mapping selects headline (a), "TEMPERATURE IS THE
> DRIVER"; the drafts for the PI are replaced). 2026-10-14: original
> publication (the pre-specified plan, committed first in `7ae996ce6`
> before any number was computed, then the results). See
> [§ Changelog](#changelog) for revision history.

- **Executed by**: Claude (Anthropic), Claude Code, model lane Opus 5.5
  (`claude-opus-5-5`), background subagents of the main Session 164
  (S164) session (P1–P11 on 2026-10-14; P12 on 2026-10-15).
- **Date**: 2026-10-14 (UTC); P12 on 2026-10-15 (UTC).
- **Repository**: `map-reader-llm`, branch `d64-a06-analysis` from
  `origin/main` at `22c682449`. Commits: `7ae996ce6` (the plan, before any
  number) and `711ed901f` (drivers, outputs, results). For P12: the plan
  items `e783ed3ac`, `751525d7e`, and `2d5cb991c` (before any pass 4–6 F1);
  `origin/main` at `8988bc6f7` merged in (`4e10f282e`, registry rebuilt in
  `f54eb4ca9`), which brought the wave-3 passes and their top-up;
  `b77624e15` (the P12 driver, the extended original driver, and the P12
  outputs); and the commit that adds this text. The library code the
  drivers import (`scripts/`) is `main`'s at `8988bc6f7`.
- **Ruling and approval**: Principal Investigator (PI) ruling D64
  (`planning/pi-decisions-2026-09-20.md`); this analysis approved by the PI
  on 2026-10-14 ("yes, run the D64 analysis now"). Passes 4–6: D66 (4).
  The confirmatory test, its wording, and the headline mapping: D67 (P12
  and P12.1 below). Report only.
- **Guarantees**: no model Application Programming Interface (API) call; no
  committed result, output, document, or register row changed; at most two
  worker processes on sapphire at any time.
- **Where the runs are**: sapphire, `~/scratch/s164-d64-2026-10-14/`
  (`wt/` the worktree; `r1/` and `r2/` the two independent P1–P11 runs,
  2026-10-14 01:49 to 01:50 UTC; `r3/` and `r4/` the two independent P12
  runs, 2026-10-15 11:30 to 11:34 UTC; `logs/`, `pids/`). Drivers and the
  first run's outputs (the second run's are identical) are committed beside
  this record in `d64-a06-replication-scripts/` (`out/` for P1–P11,
  `out-p12/` for P12).

## Pre-specified analysis plan

> **Committed in `7ae996ce6`** before any number was computed; the plan's
> text below is unchanged since, apart from this line.

Written and committed before any F1, delta, interval, p value, or floor was
computed from the D64 passes. Read before writing it: the D64, D62 (4), D61
(3) and (4), D42, D45 to D48, D50, and D63 entries; Obs 509;
`scripts/run_pro_2x2_replication.sh`; `scripts/h6_registered_analyses.py`;
`results/h6-registered-analyses/a06_decision_rule.json` and `findings.md`
§ A-06; the register row `h6-a06-decision-rule`; W2.7's floor method
(`reports/w27-replicate-floors-2026-10-06.md` §§ 1 and 3 and its scripts);
the 32 passes' metas (parameters, usage, thought tokens, detection counts);
and `topup-2026-10-13.json`. Nothing was scored.

### P1. Inputs and gates

The 32 passes under `outputs/pro-2x2-replication-2026-10-13/<corner>/<config>/run_<N>/`
as committed on `main` (`f53ae836b`, top-up `41212b986`): eight corners,
{text, image} × {HIGH, MEDIUM} thinking × {T 0.0, T 0.7}, five passes per
text corner and three per image corner, all 487 gold-standard (GS) tiles at
384 px. Before any contrast is computed, the driver halts unless:

1. **Parameter control.** Every meta records `gemini-3.1-pro-preview`, its
   corner's temperature and thinking level, its corner's configuration
   version (`detect_brief-text` or `library_plus-hp`), 487 items processed,
   and 0 failed.
2. **Coverage.** Every pass's `tiles.json` lists the 487 tiles of
   `inputs/vectors/bounds/384/full_evaluation_bounds.geojson` as completed
   and none as failed.
3. **Method replay.** The driver, run on the committed A-06 corners (the
   eight cells `h6_registered_analyses.py` loads), reproduces
   `a06_decision_rule.json`'s pass-averaged deltas, delta intervals,
   permutation p values, and discordant-tile counts exactly. This shows
   that the driver applies A-06's method on today's code.
4. **Aggregation identity.** For every corner, the mean of the driver's
   per-pass stack equals `n1_baseline_leaderboard_tiering.pass_averaged_per_tile`
   exactly.

### P2. Per-corner estimates (A-06's own)

Each pass is scored by the canonical scorer on today's `main` (the D50
scorer: `compute_per_tile_tp_fp_fn`, Hungarian matching per map, 20 m
buffer), in the bounds file's tile order. A corner's estimate is A-06's
"pass-averaged micro vintage": the micro-F1 of the per-tile true positive,
false positive, and false negative (TP, FP, FN) counts averaged over the
corner's passes. Beside it, the mean of the per-pass micro-F1s, the
analogue of A-06's "manifest eval vintage" (the conditions manifest has no
entry for these passes). Precision and recall are reported with F1.

### P3. The registered factor-T contrasts (A-06's rule)

Δ = F1(T 0.0) − F1(T 0.7) at matched thinking, per modality, at HIGH and at
MEDIUM: four contrasts. For each:

- Δ by both estimators of P2;
- the registered rule, Δ ≥ 0.03, applied to both; if the two estimators
  disagree, the split is reported as a surprise and not resolved;
- the paired tile-bootstrap interval of Δ (B = 1,000, seed 42,
  `e45_bootstrap_pairings.paired_bootstrap`, A-06's helper);
- the D42 paired tile-swap permutation p (10,000 permutations, seed 42,
  computed inside the same helper);
- Benjamini–Hochberg (BH) across the four as one family, q = 0.05
  (`lib_permutation.bh_adjust`, as `apply_bh_to_factor_t` applies it);
- the floor verdict (P6).

### P4. The thinking contrasts (context, not a registered factor)

Δ = F1(HIGH) − F1(MEDIUM) at matched temperature, per modality, at T 0.0
and at T 0.7: four contrasts, with the same statistics as P3; the 0.03 flag
on |Δ| (A-06's `reaches_0.03`); BH across these four as their own family.
The committed A-06 reported intervals only for these; D42 tests every
contrast, so they get p values here. As a sensitivity, BH across all eight
contrasts of P3 and P4 as one family. Caveat carried by every thinking row:
thinking was barely delivered (HIGH about 0 to 4 thought tokens per
request, MEDIUM about 7 to 48, from the metas), so these contrasts compare
two levels of almost no thinking and are not a test of thinking.

### P5. The corner gap and its decomposition (descriptive)

Δ = F1(HIGH, T 0.0) − F1(MEDIUM, T 0.7) per modality, the superseded S135
corner contrast, with interval and permutation p, in no BH family. The
corner gap splits exactly into (T at HIGH) + (thinking at T 0.7), and into
(T at MEDIUM) + (thinking at T 0.0); temperature's share is reported both
ways.

**The answer to D64's question**, per modality, is read from P3, P4, and
P6 with these labels fixed in advance. For each contrast: R, the 0.03 rule
(Δ ≥ 0.03 for T, |Δ| ≥ 0.03 for thinking); P, BH-adjusted p ≤ 0.05; F, |Δ|
clears the floor (P6). A configuration-level claim (D45) needs P and F.

- **Temperature is the driver** if both factor-T contrasts have R, P, and F,
  and no thinking contrast has |Δ| ≥ 0.03 with P and F.
- **Temperature is the driver at one thinking level only** if one factor-T
  contrast has R, P, and F and the other does not.
- **The difference holds between outputs, not configurations** if a
  factor-T contrast has R and P but not F (D45 wording).
- **Not supported** if neither factor-T contrast has R; **reversed** if
  either factor-T Δ ≤ −0.03.

### P6. Replicate floors (D45 and D46, W2.7's method)

A floor is the 95th percentile (linear interpolation, W2.7's `pct`) of
|ΔF1| between pass-averaged micro-F1s of disjoint, equal-size pass subsets
of one corner, scored as in P2. Subset sizes K: text K = 1 (10 pairs per
corner) and K = 2 (all 15 disjoint pairs of 2-subsets per corner); image
K = 1 (3 pairs per corner). The verdict floor is the modality's floor pooled
over its four corners, as W2.7 pools by corpus, at the largest K the
corners allow (text K = 2, 60 pairs; image K = 1, 12 pairs); the two
corners' own pooled floor is reported beside each contrast, and a verdict
that differs between the two is flagged.

The contrasts compare means of five (text) or three (image) passes, and a
mean of more passes varies less, so a floor measured at K < n is
conservative. Each contrast's floor verdict therefore takes one of three
values: **clears** (|Δ| above the measured floor); **clears only the scaled
floor** (above the measured floor × √(K/n), a model-based extrapolation
assuming independent passes, which is not a D46 floor); **inside** (below
both). All 32 passes ran on one date in one mode, so the within-execution
floor applies (D48) with no cross-date term. As in W2.7 § 3, the tile-swap
test's rejection rate at α = 0.05 on the replicate pairs is reported as a
diagnostic. With 12 pairs, the image 95th percentile sits close to the
maximum; that is stated beside it.

### P7. Sensitivity: the 15 topped-up tiles

The 15 distinct tiles in `topup-2026-10-13.json` (two in text HIGH T 0.7
run 3, three in text HIGH T 0.0 run 3, ten in text HIGH T 0.0 run 4) ran
real-time flex, not Batch. They are dropped from both arms of every contrast
with a text HIGH corner on either side (text T at HIGH, text thinking at
T 0.0 and at T 0.7, the text corner gap), leaving 472 tiles; the text
floors are recomputed on the same 472 tiles; the BH families are recomputed
with the replaced p values. Contrasts with no text HIGH corner are
unchanged by construction and are reported as such. Reported: any change in
a flag, a BH decision, a floor verdict, or the answer.

### P8. Side by side with the committed A-06

The committed corners' F1s, deltas, intervals, p values, BH values, and
flags from `a06_decision_rule.json` beside the new ones, and per corner the
difference D64 − committed (descriptive; different dates, modes, and pass
counts; not tested).

### P9. Thought tokens delivered

Per pass and per corner, `usage_stats.total_thoughts_tokens` over
`n_responses_with_usage` from each meta, with the topped-up passes marked.

### P10. Determinism and integrity

Two independent runs of the driver (fresh processes, separate output
directories, `PYTHONHASHSEED` 0 and 1), compared byte for byte after the
timestamp fields are removed; the kernel's "Bad page state" count on
sapphire before and after.

### P11. Surprises declared in advance

Flagged if seen, and not explained away: a factor-T Δ below 0.03 or
negative; a thinking |Δ| ≥ 0.03 that rejects after BH; an estimator split
on the 0.03 rule; a failed gate; a factor-T Δ inside its floor where the
committed A-06 read a clear effect; a D64 corner that differs from its
committed counterpart by more than the floor.

### P12. Confirmatory test on image passes 4–6 (added 2026-10-15, before any pass 4–6 F1 was computed)

**Why.** After this record's first results (passes 1–3), the PI approved
three more passes per image corner (runs 4–6, wave 3, committed
`9664f1094`; PI ruling D66 (4)), and the case for them rested partly on the
two borderline image results below. Data collected because a result looked
borderline cannot be pooled with it without overstating that result. So,
following a side agent's note relayed by the PI (D67), passes 4–6 are a
separate replication, specified here before any of their F1 values were
computed (the only figures read from them so far are cost, thought tokens,
and failed-tile counts, for the run's stop rule). Passes 4–6 ran on
2026-10-14, one day after passes 1–3, all four image corners on that day.

**Data.** The 12 wave-3 image passes after the D67 (1) batch-mode top-up
restores every pass to 487 of 487 tiles; scored exactly as in P2 (the D50
scorer, 20 m, all 487 GS tiles, pass-averaged micro-F1).

**The two confirmatory contrasts** (the borderline image results of passes
1–3): **C1**, image HIGH − MEDIUM at T 0.0 (passes 1–3: +0.0374, BH-adjusted
p 0.043); **C2**, image T 0.0 − T 0.7 at MEDIUM (passes 1–3: +0.0336, BH p
0.0318). Each is estimated on passes 4–6 alone, with the paired tile-swap
permutation test as in P3 (D42; tiles in sorted order, D63), and BH across
C1 and C2 only.

**Replication criterion, fixed in advance.** A contrast REPLICATES if all
four hold on passes 4–6 alone: (a) its sign matches passes 1–3; (b) its
BH-adjusted p < 0.05; (c) |Δ| ≥ 0.03 (A-06's rule); (d) |Δ| exceeds the
image replicate floor computed from passes 4–6 alone as in P6 (K = 1, 12
pairs). It PARTLY replicates if (a) holds but not all of (b)–(d), and FAILS
to replicate if (a) does not hold. Each criterion is reported separately.

**Secondary, labelled as such.** The pooled six-pass estimates for all eight
contrasts (with the note that the extension was data-dependent, so their p
values are not used for C1 or C2); the other two image factor-T contrasts on
passes 4–6 alone, for completeness; a day-effect check (per image corner,
passes 1–3 against passes 4–6, as a K = 3 disjoint-subset difference,
against the K = 1 floor); and the P7-style sensitivity dropping the
topped-up wave-3 tiles from both sides.

**What A-06 quotes.** The A-06 outcome text and the new Observation quote
the confirmatory verdicts for C1 and C2 from passes 4–6, not the pooled p
values.

### P12.1 Wording for each replication verdict (added 2026-10-15, before any pass 4–6 F1 was computed)

**Power, stated in advance** (a side agent's note relayed by the PI; an
approximation from passes 1–3's own figures, not a simulation): passes 4–6
are no larger than passes 1–3, so the replication has the same noise
(standard error about 0.015 for C1, 0.016 for C2). If the true effects were
exactly as first observed, a replication |Δ| of at least 0.03 would appear
about 69 % (C1) and 59 % (C2) of the time, and all four criteria together
roughly 55–65 % and about 50 %; if the true effects are smaller, as
borderline first results often prove, the odds fall to about 40 % or less.
PARTLY REPLICATES is therefore a likely outcome even for a real effect.

**Wording (approved by the PI, 2026-10-15)**, used in this record, A-06's
outcome text, and the new Observation, for each of C1 and C2:

| Verdict | Condition | Wording |
|---|---|---|
| REPLICATES | all four criteria met | "confirmed on three independent passes run the next day" |
| PARTLY | same sign; not all of p, 0.03, and floor | "same direction on three further passes but not confirmed; the check had roughly even odds of passing even if the effect were as large as first seen", with which criteria failed, and the pooled six-pass estimate as secondary |
| FAILS | opposite sign | "not replicated: the direction reversed on three further passes" |

**A-06 headline for each verdict (approved by the PI, 2026-10-15, before
any pass 4–6 F1 was computed)**:

- C1 REPLICATES → headline (b): "TEMPERATURE IS THE DRIVER IN TEXT; IN IMAGE
  THE MAIN DRIVER, WITH THE REQUESTED THINKING LEVEL ALSO MATTERING AT T=0.0
  (D64 same-day replication)".
- C1 PARTLY or FAILS → headline (a): "TEMPERATURE IS THE DRIVER", with the
  dated paragraph carrying the thinking result in the wording above.
- If C2 FAILS (the image temperature effect at MEDIUM reverses), whichever
  headline applies gains "; IN IMAGE AT MEDIUM THINKING, NOT REPLICATED".

Reasons (the main session's recommendation, approved): the headline answers
the question A-06 was registered for (temperature; thinking is not a
registered factor in A-06); (a) stays true whatever C1 does, since
temperature fires the rule in all four cells and explains most of each
corner gap; a hedged headline invites misquotation; and an effect of the
*requested* thinking level, when HIGH delivered about 1 and MEDIUM about 11
thought tokens per request, should reach the headline only once confirmed.
The new Observation's title follows the same mapping.

## Bottom line

### P12: the confirmatory test on image passes 4–6 (2026-10-15)

1. **C1, image HIGH − MEDIUM at T 0.0, PARTLY replicates.** On passes 4–6
   alone it keeps its sign (+0.0202, against +0.0374 on passes 1–3) but
   meets none of the other three criteria: BH-adjusted p 0.138 (not below
   0.05), |Δ| below 0.03, and |Δ| below the floor of passes 4–6 (0.0205,
   missed by 0.0003). In the approved wording: same direction on three
   further passes but not confirmed; the check had roughly even odds of
   passing even if the effect were as large as first seen. The pooled
   six-pass estimate (secondary) is +0.0288.
2. **C2, image T 0.0 − T 0.7 at MEDIUM, REPLICATES.** +0.0653 on passes
   4–6 (against +0.0336), interval [+0.0352, +0.0954], BH-adjusted p
   0.0002, above both 0.03 and the floor. In the approved wording:
   confirmed on three independent passes run the next day.
3. **Headline: (a), "TEMPERATURE IS THE DRIVER".** P12.1's mapping sends
   C1 PARTLY to headline (a); C2 did not fail, so no suffix is added. This
   replaces the headline (b) the PI accepted under D66 (3) on 2026-10-14,
   before P12 existed; neither was applied to the register, whose outcome
   already opens with (a).
4. **Secondary results agree with the confirmatory reading.** On passes 4–6
   image temperature at HIGH is +0.0786 and the thinking contrast at T 0.7
   +0.0069. Pooled over six image passes, the pre-specified P5 label
   "temperature is the driver" now applies in image as well as in text.
5. **Surprise: the image corners moved between the two days.** From
   2026-10-13 to 2026-10-14 three image corners fell (by 0.0115, 0.0210,
   and 0.0259) and one rose (by 0.0058). The largest move, image MEDIUM
   T 0.7, is at the within-day floor (0.0254). These moves account exactly
   for C1 shrinking by 0.0172 and C2 growing by 0.0317. The second day's
   corners sit within 0.011 of the committed A-06 corners, against up to
   0.028 on the first day.
6. **The sensitivities change no verdict.** Dropping the 138 tiles topped
   up in Batch a day after their passes (349 tiles left) leaves C1 PARTLY,
   C2 REPLICATES, and the headline (a). The 15 real-time tiles of
   2026-10-13 touch only text, so C1 and C2 are unchanged by construction.
7. **Integrity.** All gates passed, including a replay of passes 1–3
   against the committed results. Two independent runs under hash seeds 0
   and 1 are identical apart from timestamps. The extended original driver
   reproduces its 2026-10-14 outputs on the merged tree. The kernel
   bad-page count was 0 before and 0 after.
8. **For the PI.** Three drafts are in § For the PI: A-06's headline and
   dated paragraph, a note for `findings.md` § A-06, and an Observation
   qualifying Obs 415. Nothing is applied.

### Passes 1–3 (2026-10-14)

1. **A-06's registered verdict reproduces on same-day data.** With the
   date, mode, and thinking-record confounds removed (all eight corners on
   2026-10-13, Batch API, one model version, thinking booked per pass), the
   registered rule fires for factor T in all four cells, every one rejects
   after BH, and every one clears the same-day replicate floor.
2. **Text: temperature is the driver** (the pre-specified label applies).
   T 0.0 beats T 0.7 by +0.0500 at HIGH (Δ interval [+0.0262, +0.0723],
   p < 0.0001) and +0.0464 at MEDIUM ([+0.0218, +0.0704], p 0.0002), about
   four times the floor of 0.0116. The thinking contrasts are +0.0026 and
   −0.0010 (p 0.84 and 0.92). Temperature accounts for 95 to 102 % of the
   corner gap of +0.0490.
3. **Image: temperature is the main driver, but not the only one.** Under
   the labels fixed in P5, none applies. Both temperature contrasts fire,
   reject, and clear the floor, at +0.0690 for HIGH ([+0.0385, +0.1011],
   p < 0.0001) and +0.0336 for MEDIUM ([+0.0042, +0.0653], p 0.0318). But
   **the thinking contrast at T 0.0 does too, which the plan declared a
   surprise.** HIGH beats MEDIUM by +0.0374 ([+0.0104, +0.0680],
   permutation p 0.0107, BH-adjusted p 0.0428, above the floor of 0.0295).
   HIGH delivered about 1 thought token per request there and MEDIUM about
   11, so the contrast measures the requested level; these data cannot say
   whether the difference of about ten tokens in delivered thinking is the
   cause.
   At T 0.7 the thinking contrast is +0.0020. Temperature accounts for 97 %
   of the image corner gap (+0.0710) measured at HIGH and 47 % measured at
   MEDIUM. *(2026-10-15: on passes 4–6 the thinking contrast at T 0.0 was
   not confirmed; see P12 above.)*
4. **The image temperature effect at MEDIUM roughly halved** against the
   committed A-06 (+0.0605 → +0.0336). It clears the 0.03 rule by 0.0036
   and the floor by 0.0041, and it would not reject if the eight contrasts
   were one BH family (adjusted p 0.0509). The image 2 × 2's interaction
   (+0.0354, post hoc) does not reject (p 0.089). *(2026-10-15: on passes
   4–6 this effect was confirmed at +0.0653; see P12 above.)*
5. **The top-up sensitivity changes nothing.** Dropping the 15 real-time
   tiles moves the affected text contrasts by at most 0.0013, and no flag,
   BH decision, floor verdict, or answer changes.
6. **Integrity.** All four gates passed, including an exact replay of the
   committed A-06's four bootstrap blocks and four thinking intervals,
   which shows that the driver applies A-06's method on today's code. Two
   independent runs under hash seeds 0 and 1 are identical apart from the
   timestamp. The kernel bad-page count was 0 before and 0 after.
7. **For the PI.** A-06's outcome text needs a dated revision in image (its
   line "the thinking contrast … reaches 0.03 in none of four cells" no
   longer holds on same-day data). *(2026-10-15: the 2026-10-14 draft is
   superseded by the P12 drafts in § For the PI.)*

## Results: the confirmatory test on image passes 4–6 (P12)

All figures are read from `d64-a06-replication-scripts/out-p12/d64_p12_results.json`
(run r3; run r4 is identical) unless another file is named. They are
computed by `d64_p12_replication.py`, which imports the record's own driver
for scoring, contrasts, floors, and BH. Scoring is unchanged from P2: micro-F1
at 20 m on all 487 GS tiles, from pass-averaged per-tile counts. Tiles are in
the bounds file's order, which is sorted (D63). p is the D42 paired tile-swap
permutation test (10,000, seed 42); "< 0.0001" means none of the 10,000
permutations reached the observed |Δ|. Intervals are paired tile bootstrap
(B = 1,000, seed 42). "Passes 1–3" are runs 1–3 (2026-10-13); "passes 4–6"
are runs 4–6 (2026-10-14).

### Gates (P12)

| Gate | Result |
|---|---|
| Text passes and image runs 1–3: the original driver's gates 1 and 2 | pass |
| All 24 image passes: model, temperature, thinking level, configuration, 487 processed, 0 failed, Batch tier, 487 responses with usage, coverage, and start date (runs 1–3 on 2026-10-13, runs 4–6 on 2026-10-14) | pass |
| The 2026-10-15 top-up (`topup-2026-10-15.json`): its 8 topped-up and 4 untouched passes are the 12 wave-3 passes; each recovered and merged all its failed tiles; each pass's last `recovery_history` entry names the same tiles; no pass of runs 1–3 has a recovery history; 152 tile-pass instances, as the record totals | pass |
| Aggregation identity against the A-06 helper, every pool (image pools on all six passes) | pass, 8 of 8 |
| Replay: passes 1–3, analysed by the P12 driver, equal the committed `out/d64_a06_results.json` (contrasts, floors, and corners) | pass |
| The extended original driver, re-run on the merged tree, reproduces every 2026-10-14 output (§ Integrity) | pass |

### Image corners by day, and thought tokens (P2, P9)

Thought tokens per request are `total_thoughts_tokens` over
`n_responses_with_usage` from the merged metas (top-up requests included),
pooled over each wave's passes.

| Corner | F1, passes 1–3 | F1, passes 4–6 | Day difference (4–6 − 1–3) | F1, passes 1–6 | Per-pass F1, passes 4–6 | Thought tokens per request (1–3 / 4–6 / 1–6) |
|---|---:|---:|---:|---:|---|---|
| image HIGH T 0.0 | 0.6877 | 0.6763 | −0.0115 | 0.6820 | 0.6790, 0.6728, 0.6770 | 1.30 / 0 / 0.65 |
| image HIGH T 0.7 | 0.6187 | 0.5977 | −0.0210 | 0.6082 | 0.5957, 0.6091, 0.5884 | 2.28 / 3.08 / 2.68 |
| image MEDIUM T 0.0 | 0.6503 | 0.6561 | +0.0058 | 0.6532 | 0.6487, 0.6639, 0.6556 | 11.2 / 11.0 / 11.1 |
| image MEDIUM T 0.7 | 0.6167 | 0.5908 | −0.0259 | 0.6038 | 0.5899, 0.5811, 0.6014 | 44.4 / 44.3 / 44.3 |

Per pass on passes 4–6, thought tokens per request were 0, 0, 0 (HIGH
T 0.0); 3.42, 1.63, 4.20 (HIGH T 0.7); 10.41, 14.78, 7.82 (MEDIUM T 0.0);
and 42.36, 46.27, 44.17 (MEDIUM T 0.7). Some top-ups were bursty. In image
HIGH T 0.7 run 4, every one of the pass's 1,665 thought tokens came from
the 5 tiles topped up on 2026-10-15 (333 per request, from the top-up
record's `usage`); the pass's 482 requests of 2026-10-14 recorded none (its
pre-top-up meta in `archive/pre-topup-2026-10-15/`). In image MEDIUM T 0.7
run 4 the 24 top-up requests averaged 94.75, against 39.6 for the pass's
other 463 (18,357 tokens). The top-up requests of the other four
topped-up HIGH passes recorded 0.

### The confirmatory contrasts C1 and C2 (P12)

The floor of passes 4–6 is W2.7's 95th percentile of |ΔF1| over the 12
single-pass pairs (K = 1) inside the four image corners' passes 4–6:
**0.0205** (median 0.0086, maximum 0.0207; tile-swap rejections 0 of 12).
Per corner it is 0.0060 (HIGH T 0.0), 0.0200 (HIGH T 0.7), 0.0145 (MEDIUM
T 0.0), and 0.0195 (MEDIUM T 0.7). The same floor on passes 1–3 was 0.0295.
Pair rows are in `out-p12/p12_floor_pairs.csv`.

| | C1: image HIGH − MEDIUM at T 0.0 | C2: image T 0.0 − T 0.7 at MEDIUM |
|---|---:|---:|
| Δ, passes 1–3 (the sign to match) | +0.0374 | +0.0336 |
| **Δ, passes 4–6** | **+0.0202** | **+0.0653** |
| Δ, mean of per-pass F1 | +0.0202 | +0.0652 |
| Δ interval | [−0.0073, +0.0479] | [+0.0352, +0.0954] |
| Permutation p | 0.138 | 0.0001 |
| BH-adjusted p (C1 and C2) | 0.138 | 0.0002 |
| Discordant tiles | 129 | 165 |
| (a) sign matches passes 1–3 | met | met |
| (b) BH-adjusted p < 0.05 | not met | met |
| (c) \|Δ\| ≥ 0.03 | not met | met |
| (d) \|Δ\| above the floor (0.0205) | not met (short by 0.0003) | met |
| **Verdict** | **PARTLY** | **REPLICATES** |

- **C1: same direction on three further passes but not confirmed; the
  check had roughly even odds of passing even if the effect were as large
  as first seen.** Criteria (b), (c), and (d) are not met. Every HIGH pass
  (0.6728 to 0.6790) still beats every MEDIUM pass (0.6487 to 0.6639), but
  the pass-averaged difference is about half the first day's. Under P6's
  three-valued reading it clears only the scaled floor (0.0118); P12's
  criterion (d) uses the measured floor. The pooled six-pass estimate
  (secondary) is +0.0288.
- **C2: confirmed on three independent passes run the next day.** All four
  criteria are met, and every MEDIUM T 0.0 pass (0.6487 to 0.6639) beats
  every MEDIUM T 0.7 pass (0.5811 to 0.6014). The effect nearly doubled,
  from +0.0336 to +0.0653, close to the committed A-06's +0.0605.
- The second estimator (mean of per-pass F1) gives the same reading on
  criteria (a), (c), and (d) for both contrasts.
- **Headline.** By P12.1, C1 PARTLY selects headline (a), "TEMPERATURE IS
  THE DRIVER", with the dated paragraph carrying the thinking result; C2
  did not fail, so no suffix is added.

### The other image contrasts on passes 4–6 (secondary)

P12 calls these "the other two image factor-T contrasts". Image has only
one factor-T contrast besides C2, so they are read here as the two image
contrasts of the 2 × 2 other than C1 and C2; the corner gap is added
because the A-06 text quotes its decomposition. Raw p, in no family; floor
verdicts against the floor of passes 4–6 (0.0205).

| Contrast | Δ | Interval | p | Floor | Discordant tiles |
|---|---:|---|---:|---|---:|
| image T 0.0 − T 0.7 at HIGH | +0.0786 | [+0.0478, +0.1087] | < 0.0001 | clears | 161 |
| image HIGH − MEDIUM at T 0.7 | +0.0069 | [−0.0244, +0.0369] | 0.671 | inside | 179 |
| image corner gap (HIGH T 0.0 − MEDIUM T 0.7) | +0.0854 | [+0.0552, +0.1147] | < 0.0001 | clears | 174 |

On passes 4–6, temperature accounts for 92 % of the image corner gap
measured at HIGH (+0.0786 of +0.0854) and 76 % measured at MEDIUM (+0.0653
of +0.0854), against 97 % and 47 % on passes 1–3.

### Pooled six-pass estimates (secondary)

Passes 4–6 were added partly because C1 and C2 looked borderline, so the
pooled extension is data-dependent and its p values are not used for C1 or
C2. Text keeps its five passes (all from 2026-10-13), so its rows equal
P3 and P4. Image uses six passes per corner. P6's rule takes the image floor
at the largest K the corners allow, K = 3 (40 pairs): 0.0213 (K = 1, 60
pairs: 0.0373; K = 2, 180 pairs: 0.0263). These pairs mix the two days.
Families as in P3 and P4.

| Contrast | Δ | Interval | p | BH p (own family) | BH p (all eight) | Rule or 0.03 | Floor |
|---|---:|---|---:|---:|---:|---|---|
| text T at HIGH | +0.0500 | [+0.0262, +0.0723] | < 0.0001 | < 0.0001 | < 0.0001 | fires | clears (0.0116) |
| text T at MEDIUM | +0.0464 | [+0.0218, +0.0704] | 0.0002 | 0.00027 | 0.00053 | fires | clears (0.0116) |
| image T at HIGH | +0.0738 | [+0.0480, +0.0990] | < 0.0001 | < 0.0001 | < 0.0001 | fires | clears (0.0213) |
| image T at MEDIUM | +0.0494 | [+0.0235, +0.0761] | 0.0005 | 0.0005 | 0.0010 | fires | clears (0.0213) |
| text thinking at T 0.0 | +0.0026 | [−0.0238, +0.0276] | 0.839 | 0.924 | 0.924 | no | inside |
| text thinking at T 0.7 | −0.0010 | [−0.0236, +0.0201] | 0.924 | 0.924 | 0.924 | no | inside |
| image thinking at T 0.0 | +0.0288 | [+0.0045, +0.0540] | 0.0252 | 0.101 | 0.0403 | no | clears (0.0213) |
| image thinking at T 0.7 | +0.0044 | [−0.0176, +0.0272] | 0.721 | 0.924 | 0.924 | no | inside |

- **The P5 labels, pooled:** "temperature is the driver" in text and in
  image. The image thinking contrast at T 0.0 has F (it clears the floor)
  but neither R (+0.0288 is below 0.03) nor P (0.101 in its family).
- In the all-eight sensitivity family the pooled image thinking contrast
  at T 0.0 would reject (0.0403). That is the overstatement the
  confirmatory design guards against, and it is not used.
- The image corner gap pooled is +0.0782 ([+0.0502, +0.1043], p < 0.0001);
  temperature's share is 94 % via HIGH and 63 % via MEDIUM.
- Each contrast's own two-corner floor gives the same verdict, and the two
  estimators never split on the rule.

### The day effect (secondary)

Per image corner, the pass-averaged F1 of passes 4–6 minus that of passes
1–3: a K = 3 disjoint-subset difference. It is set against the within-day
K = 1 floor, the 95th percentile over the 24 single-pass pairs inside the
two days (**0.0254**; maximum 0.0335), with P6's three-valued verdict
(scaled floor 0.0254 × √(1/3) = 0.0147). Each day's own floor is 0.0295
(passes 1–3) and 0.0205 (passes 4–6). The last column ranks the day split
among the corner's ten disjoint 3-vs-3 splits of its six passes (1 is the
largest |Δ|); with no day effect it is one of ten exchangeable splits.

| Corner | Δ (4–6 − 1–3) | Tile-swap p | Discordant tiles | Verdict (within-day floor 0.0254) | Rank of the day split |
|---|---:|---:|---:|---|---:|
| image HIGH T 0.0 | −0.0115 | 0.312 | 115 | inside | 1 of 10 |
| image HIGH T 0.7 | −0.0210 | 0.147 | 180 | clears only the scaled floor | 1 of 10 |
| image MEDIUM T 0.0 | +0.0058 | 0.406 | 82 | inside | 6 of 10 |
| image MEDIUM T 0.7 | **−0.0259** | 0.055 | 159 | **clears** | 2 of 10 |

- **One day difference clears the within-day floor**, image MEDIUM T 0.7,
  by 0.0005. Two exceed the second day's own floor (HIGH and MEDIUM at
  T 0.7); none exceeds the first day's.
- **The day moves are what changed C1 and C2.** C1 moved by
  (−0.0115) − (+0.0058) = −0.0172, and C2 by (+0.0058) − (−0.0259) =
  +0.0317 (6-dp values; the sums match the confirmatory deltas exactly).
- **Pairs that cross days differ more than pairs within a day.** Among the
  six-pass image K = 1 pairs (`out-p12/p12_floor_pairs.csv`), the 36
  cross-day pairs have median |ΔF1| 0.0144 and maximum 0.0513, against
  0.0087 and 0.0335 for the 24 within-day pairs. The tile-swap test
  rejected 5 of the 180 six-pass image K = 2 pairs, all in MEDIUM corners
  and each mixing the days; it rejected none of the 112 replicate pairs of
  passes 1–3 (P6) and none of the 12 of passes 4–6.
- **Against the committed A-06 corners** (descriptive; different dates and
  modes, `out/d64_a06_results.json` § side by side), the second day's image
  corners differ by +0.0105, +0.0069, +0.0010, and −0.0042 (HIGH T 0.0,
  HIGH T 0.7, MEDIUM T 0.0, MEDIUM T 0.7), against +0.0220, +0.0279,
  −0.0047, and +0.0217 on the first day.

### Sensitivities (secondary)

**(i) The 15 real-time top-up tiles of 2026-10-13** lie in text HIGH
corners only. C1 and C2 have no text corner, so they are unchanged by
construction. On the pooled estimates, dropping the 15 from both arms of
the four contrasts with a text HIGH corner reproduces P7 exactly (text T at
HIGH +0.0507, the text thinking contrasts +0.0015 and −0.0004, the text
corner gap +0.0502, the text floor 0.0135 on 472 tiles). The only other
change is the BH-adjusted p of the pooled image thinking contrast at T 0.7
(0.924 → 0.970), through its family. No flag, BH decision, floor verdict,
or label changes.

**(ii) The wave-3 batch top-up tiles of 2026-10-15** ran a day after their
passes: 152 tile-pass instances on 138 distinct tiles, in 8 of the 12
wave-3 passes (HIGH T 0.0 runs 4 and 5: 9 and 2; HIGH T 0.7 runs 4, 5, and
6: 5, 3, and 7; MEDIUM T 0.0 runs 4 and 5: 19 and 83; MEDIUM T 0.7 run 4:
24). Every image corner has a topped-up pass, so, as in P7, the 138 tiles
are dropped from both arms of every image contrast (349 tiles left), and
the image floors are re-measured on the same tiles.

| Quantity | 487 tiles | 349 tiles |
|---|---|---|
| Floor of passes 4–6 (K = 1, 12 pairs) | 0.0205 | 0.0306 |
| C1: Δ, p, BH-adjusted p | +0.0202, 0.138, 0.138 | +0.0190, 0.228, 0.228 |
| C1 verdict (criteria not met) | PARTLY (b, c, d) | PARTLY (b, c, d) |
| C2: Δ, p, BH-adjusted p | +0.0653, 0.0001, 0.0002 | +0.0785, < 0.0001, < 0.0001 |
| C2 verdict | REPLICATES | REPLICATES |
| Headline selected | (a) | (a) |
| Image T at HIGH, passes 4–6 | +0.0786 (clears) | +0.0798 (clears) |
| Image thinking at T 0.7, passes 4–6 | +0.0069 (inside) | +0.0176 (inside) |
| Pooled image floor (K = 3) | 0.0213 | 0.0276 |
| Pooled image T at MEDIUM: Δ, p | +0.0494, 0.0005 | +0.0563, 0.0007 |
| Pooled image thinking at T 0.0: Δ, p, BH p (own family) | +0.0288, 0.0252, 0.101 | +0.0282, 0.0514, 0.206 |
| Pooled P5 label, image | temperature is the driver | temperature is the driver |
| Day effect, image MEDIUM T 0.7: Δ, p, verdict | −0.0259, 0.055, clears | −0.0361, 0.025, clears |

No verdict, criterion, label, or headline changes. Without the top-up tiles
the day effect at image MEDIUM T 0.7 is larger and clears both single-day
floors (within-day floor 0.0278 on 349 tiles).

## Results: passes 1–3 (P1–P11)

All figures are read from `d64-a06-replication-scripts/out/d64_a06_results.json`
(run 1; run 2 is identical) unless another file is named. F1 is micro-F1
at 20 m on all 487 GS tiles. Δ is computed from pass-averaged per-tile
counts (A-06's "pass-averaged micro vintage"), and the "mean of per-pass"
Δ is shown beside it. Intervals are paired tile bootstrap (B = 1,000, seed
42); p is the D42 paired tile-swap permutation test (10,000, seed 42),
where "< 0.0001" means none of the 10,000 permutations reached the
observed |Δ|.

### Gates (P1)

| Gate | Result |
|---|---|
| 1. Parameter control (32 metas: model, temperature, thinking level, configuration, 487 processed, 0 failed) | pass |
| 2. Coverage (every `tiles.json` lists the 487 bounds tiles, none failed) | pass |
| 3. Method replay on the committed A-06 corners | pass: the four factor-T bootstrap blocks (Δ, bootstrap mean, interval, p, permutations, discordant tiles, the interval-excludes-zero flag) and the four thinking intervals are identical to `a06_decision_rule.json` |
| 4. Aggregation identity against `pass_averaged_per_tile` | pass, 8 of 8 corners exactly |

### The eight corners (P2, P9)

Thought tokens per request are `total_thoughts_tokens` over
`n_responses_with_usage` from each meta, shown as the corner mean, with
the per-pass range in brackets.

| Corner | Passes | F1 | Precision | Recall | Mean of per-pass F1 | Per-pass F1 range | Thought tokens per request |
|---|---:|---:|---:|---:|---:|---|---|
| text HIGH T 0.0 | 5 | 0.8008 | 0.7922 | 0.8097 | 0.8008 | 0.7977–0.8032 | 0 (0–0) |
| text HIGH T 0.7 | 5 | 0.7508 | 0.7375 | 0.7646 | 0.7508 | 0.7427–0.7576 | 0.33 (0–1.67) |
| text MEDIUM T 0.0 | 5 | 0.7982 | 0.7790 | 0.8184 | 0.7982 | 0.7885–0.8067 | 16.8 (9.4–28.4) |
| text MEDIUM T 0.7 | 5 | 0.7518 | 0.7286 | 0.7766 | 0.7518 | 0.7472–0.7601 | 39.8 (36.7–44.1) |
| image HIGH T 0.0 | 3 | 0.6877 | 0.6233 | 0.7670 | 0.6877 | 0.6852–0.6926 | 1.30 (0–3.91) |
| image HIGH T 0.7 | 3 | 0.6187 | 0.5595 | 0.6920 | 0.6187 | 0.6109–0.6256 | 2.28 (0.92–3.93) |
| image MEDIUM T 0.0 | 3 | 0.6503 | 0.5922 | 0.7211 | 0.6503 | 0.6356–0.6618 | 11.2 (7.4–17.2) |
| image MEDIUM T 0.7 | 3 | 0.6167 | 0.5572 | 0.6904 | 0.6167 | 0.5990–0.6324 | 44.4 (42.4–48.0) |

Thinking was barely delivered. The HIGH corners delivered 0 to 2.3 thought
tokens per request, and the MEDIUM corners 11 to 44. The three topped-up passes (text HIGH T 0.0 runs
3 and 4, text HIGH T 0.7 run 3) record 0, 0, and 1.67. Their metas give
the billing tier as `batch`, although 15 of their requests ran on
real-time flex (`topup-2026-10-13.json`).

### The registered factor-T contrasts (P3)

Δ = F1(T 0.0) − F1(T 0.7). BH is applied across these four as one family
(A-06's family, through `apply_bh_to_factor_t`). "All eight" is the P4
sensitivity, which puts these and the thinking contrasts in one family.

| Contrast | Δ | Δ (mean of per-pass) | Δ interval | p | BH p | BH p (all eight) | Rule fires | Floor | Discordant tiles |
|---|---:|---:|---|---:|---:|---:|---|---|---:|
| text, HIGH | +0.0500 | +0.0500 | [+0.0262, +0.0723] | < 0.0001 | < 0.0001 | < 0.0001 | yes (both) | clears (0.0116) | 168 |
| text, MEDIUM | +0.0464 | +0.0464 | [+0.0218, +0.0704] | 0.0002 | 0.00027 | 0.00053 | yes (both) | clears (0.0116) | 206 |
| image, HIGH | +0.0690 | +0.0690 | [+0.0385, +0.1011] | < 0.0001 | < 0.0001 | < 0.0001 | yes (both) | clears (0.0295) | 165 |
| image, MEDIUM | +0.0336 | +0.0336 | [+0.0042, +0.0653] | 0.0318 | 0.0318 | 0.0509 | yes (both) | clears (0.0295) | 164 |

The two estimators agree to 0.00003 and never split on the rule. Each
contrast's own two-corner floor gives the same verdict. Those floors are
0.0093 (text HIGH), 0.0119 (text MEDIUM), 0.0132 (image HIGH), and 0.0317
(image MEDIUM, which the contrast clears by 0.0020).

### The thinking contrasts (P4)

Δ = F1(HIGH) − F1(MEDIUM). BH is applied across these four as their own
family. Every row compares two levels of almost no thinking (see the
corner table), so none is a test of thinking.

| Contrast | Δ | Δ (mean of per-pass) | Δ interval | p | BH p | BH p (all eight) | Reaches 0.03 | Floor | Discordant tiles |
|---|---:|---:|---|---:|---:|---:|---|---|---:|
| text, T 0.0 | +0.0026 | +0.0026 | [−0.0238, +0.0276] | 0.839 | 0.924 | 0.924 | no | inside (0.0116) | 103 |
| text, T 0.7 | −0.0010 | −0.0011 | [−0.0236, +0.0201] | 0.924 | 0.924 | 0.924 | no | inside (0.0116) | 205 |
| image, T 0.0 | **+0.0374** | +0.0374 | [+0.0104, +0.0680] | 0.0107 | **0.0428** | 0.0214 | **yes** | **clears** (0.0295) | 126 |
| image, T 0.7 | +0.0020 | +0.0020 | [−0.0309, +0.0351] | 0.903 | 0.924 | 0.924 | no | inside (0.0295) | 169 |

In the image T 0.0 contrast, every HIGH pass (0.6852 to 0.6926) beats
every MEDIUM pass (0.6356 to 0.6618).

### The corner gap and its decomposition (P5)

The corner gap is F1(HIGH, T 0.0) − F1(MEDIUM, T 0.7), the superseded S135
contrast. It belongs to no BH family.

| Modality | Gap | Interval | p | T at HIGH + thinking at T 0.7 | T at MEDIUM + thinking at T 0.0 | T share (via HIGH) | T share (via MEDIUM) |
|---|---:|---|---:|---|---|---:|---:|
| text | +0.0490 | [+0.0241, +0.0730] | 0.0002 | +0.0500 − 0.0010 | +0.0464 + 0.0026 | 102 % | 95 % |
| image | +0.0710 | [+0.0372, +0.1067] | 0.0001 | +0.0690 + 0.0020 | +0.0336 + 0.0374 | 97 % | 47 % |

**The answer to D64's question, by the labels fixed in P5.**

- **Text: "temperature is the driver".** Both factor-T contrasts have R
  (the 0.03 rule), P (BH p ≤ 0.05), and F (clear of the floor); neither
  thinking contrast has any of the three.
- **Image: none of the pre-specified labels applies.** Both factor-T
  contrasts have R, P, and F, but so does the thinking contrast at T 0.0,
  which the "driver" label excludes. Temperature therefore drives the
  whole image corner gap measured at HIGH. Measured at MEDIUM, it drives
  half the gap, and the thinking-level request drives the other half,
  through its effect at T 0.0.

### Replicate floors (P6)

W2.7's method (§ 3 of `reports/w27-replicate-floors-2026-10-06.md`) is
applied to these passes. A floor is the 95th percentile, with linear
interpolation, of |ΔF1| between disjoint, equal-size pass subsets of one
corner. Pair rows are in `out/floor_pairs.csv`.

| Modality | K | Pairs | Median \|ΔF1\| | 95th percentile | Max | Tile-swap rejects at 0.05 | Scaled to the cell (× √(K/n)) |
|---|---:|---:|---:|---:|---:|---:|---:|
| text | 1 | 40 | 0.0063 | 0.0147 | 0.0183 | 0 % | — |
| text | **2** (verdict floor) | 60 | 0.0028 | **0.0116** | 0.0130 | 0 % | 0.0073 |
| image | **1** (verdict floor) | 12 | 0.0111 | **0.0295** | 0.0335 | 0 % | 0.0170 |

Per corner, at the verdict K (95th percentile):

| Corner | text (K = 2, 15 pairs) | image (K = 1, 3 pairs) |
|---|---:|---:|
| HIGH T 0.0 | 0.0033 | 0.0074 |
| HIGH T 0.7 | 0.0107 | 0.0141 |
| MEDIUM T 0.0 | 0.0124 | 0.0254 |
| MEDIUM T 0.7 | 0.0116 | 0.0321 |

- No contrast's verdict rests on the scaled floor. Every |Δ| either clears
  the measured floor or falls inside both floors.
- The image floor rests on 12 pairs, so its 95th percentile (0.0295) sits
  near its maximum (0.0335), as P6 anticipated. Two image verdicts, the
  temperature contrast at MEDIUM (+0.0336) and the thinking contrast at
  T 0.0 (+0.0374), clear it by 0.0041 and 0.0079.
- The tile-swap test rejected none of the 112 replicate pairs.
- At T 0.0, the corners that did a little thinking (MEDIUM) are three to
  four times as variable between passes as the corners that did none
  (HIGH), at 0.0124 against 0.0033 in text and 0.0254 against 0.0074 in
  image.

### Sensitivity: the 15 topped-up tiles dropped (P7)

The 15 tiles are dropped from both arms of the four contrasts that have a
text HIGH corner on either side (472 tiles). Re-measured on the same 472
tiles, the text floor is 0.0135 at K = 2 (0.0169 at K = 1), against 0.0116
on all tiles. Pair rows are in `out/floor_pairs_sensitivity.csv`.

| Contrast | Δ, 487 tiles | Δ, 472 tiles | Interval, 472 | p, 472 | BH p, 472 | Rule or 0.03 | Floor verdict |
|---|---:|---:|---|---:|---:|---|---|
| text T at HIGH | +0.0500 | +0.0507 | [+0.0274, +0.0727] | 0.0001 | 0.0002 | fires (unchanged) | clears (unchanged) |
| text thinking at T 0.0 | +0.0026 | +0.0015 | [−0.0217, +0.0256] | 0.902 | 0.970 | no (unchanged) | inside (unchanged) |
| text thinking at T 0.7 | −0.0010 | −0.0004 | [−0.0219, +0.0216] | 0.970 | 0.970 | no (unchanged) | inside (unchanged) |
| text corner gap | +0.0490 | +0.0502 | [+0.0264, +0.0761] | < 0.0001 | — | — | clears (unchanged) |

The other four contrasts keep their tiles and floors, so they are
unchanged by construction; only the image thinking contrast at T 0.7 moves,
and only in its BH-adjusted p (0.924 → 0.970), because its family's other
p values changed. The answer labels are unchanged ("temperature is the
driver" in text, none in image).

### Side by side with the committed A-06 (P8)

The committed corners came from different dates and modes. HIGH T 0.0 ran
in June in real time (`n1-pro-rerun-384`), HIGH T 0.7 in March on the Batch
API (`pv-diag-384`), MEDIUM T 0.0 in March and June (`pv-diag-384`), and
MEDIUM T 0.7 in June (`n1-pro-rerun-384`). The committed pass-averaged F1 is
recomputed in the replay; the manifest F1 is read from
`results/conditions-manifest.json`. The differences are descriptive, and
the within-execution floors above do not bound cross-date differences (see
W2.7 § 4).

| Corner | Committed passes | Committed F1 (manifest / pass-averaged) | D64 F1 | D64 − committed |
|---|---:|---|---:|---:|
| text HIGH T 0.0 | 3 | 0.8045 / 0.8046 | 0.8008 | −0.0037 |
| text HIGH T 0.7 | 10 | 0.7450 / 0.7450 | 0.7508 | +0.0057 |
| text MEDIUM T 0.0 | 3 | 0.7921 / 0.7922 | 0.7982 | +0.0060 |
| text MEDIUM T 0.7 | 3 | 0.7555 / 0.7556 | 0.7518 | −0.0037 |
| image HIGH T 0.0 | 3 | 0.6658 / 0.6658 | 0.6877 | +0.0220 |
| image HIGH T 0.7 | 5 | 0.5908 / 0.5908 | 0.6187 | +0.0279 |
| image MEDIUM T 0.0 | 3 | 0.6555 / 0.6550 | 0.6503 | −0.0047 |
| image MEDIUM T 0.7 | 3 | 0.5950 / 0.5950 | 0.6167 | +0.0217 |

| Contrast | Committed Δ, interval, p | D64 Δ, interval, p | Rule or 0.03 (committed → D64) |
|---|---|---|---|
| text T at HIGH | +0.0595, [+0.0340, +0.0846], < 0.0001 | +0.0500, [+0.0262, +0.0723], < 0.0001 | fires → fires |
| text T at MEDIUM | +0.0366, [+0.0113, +0.0620], 0.0019 | +0.0464, [+0.0218, +0.0704], 0.0002 | fires → fires |
| image T at HIGH | +0.0750, [+0.0421, +0.1076], < 0.0001 | +0.0690, [+0.0385, +0.1011], < 0.0001 | fires → fires |
| image T at MEDIUM | +0.0605, [+0.0299, +0.0888], 0.0002 | +0.0336, [+0.0042, +0.0653], 0.0318 | fires → fires |
| text thinking at T 0.0 | +0.0124, [−0.0101, +0.0351], not tested | +0.0026, [−0.0238, +0.0276], 0.839 | no → no |
| text thinking at T 0.7 | −0.0105, [−0.0341, +0.0126], not tested | −0.0010, [−0.0236, +0.0201], 0.924 | no → no |
| image thinking at T 0.0 | +0.0103, [−0.0167, +0.0384], not tested | +0.0374, [+0.0104, +0.0680], 0.0107 | no → **yes** |
| image thinking at T 0.7 | −0.0042, [−0.0358, +0.0278], not tested | +0.0020, [−0.0309, +0.0351], 0.903 | no → no |

The committed thinking Δs are the manifest-vintage figures, which carry no
p (`a06_decision_rule.json`). The text MEDIUM temperature contrast, which
the phase gate judged under-powered at three passes, strengthens at five
(+0.0366 → +0.0464), and the text 2 × 2 keeps its shape. In image, three
corners rose by 0.022 to 0.028 and MEDIUM T 0.0 fell by 0.005. That
halves the temperature effect at MEDIUM and turns the thinking contrast at
T 0.0 from +0.0103 into +0.0374. No corner moved by more than its
modality's within-execution floor; the largest move, image HIGH T 0.7, is
+0.0279 against a floor of 0.0295.

### Post hoc (not in the plan): the temperature × thinking interaction

This check was added after the image thinking contrast was seen, to ask
whether the image temperature effect differs between the two thinking
levels. The statistic is (T effect at HIGH) − (T effect at MEDIUM), on the
same pass-averaged counts. p comes from `lib_permutation.paired_interaction_permutation`
(10,000, seed 42), and the interval from a paired tile bootstrap (B =
1,000, seed 42). The driver is `posthoc_interaction.py`, and its output,
`out/posthoc_interaction.json`, is identical across both runs. The check
belongs to no family and decides nothing above.

| Modality | T at HIGH | T at MEDIUM | Interaction | Interval | p |
|---|---:|---:|---:|---|---:|
| text | +0.0500 | +0.0464 | +0.0037 | [−0.0283, +0.0350] | 0.812 |
| image | +0.0690 | +0.0336 | +0.0354 | [−0.0071, +0.0748] | 0.089 |

By construction, the interaction equals the thinking contrast at T 0.0
minus the thinking contrast at T 0.7 (+0.0374 − 0.0020). At 487 tiles and
three passes per corner, the image data do not separate it from noise.

## Surprises

### P12 (2026-10-15)

P12.1 declared PARTLY a likely outcome even for a real effect, so C1's
verdict is not itself a surprise. These are.

1. **The image corners moved between two consecutive days, at the edge of
   the floor** (not declared). Three image corners fell from 2026-10-13 to
   2026-10-14 and one rose; image MEDIUM T 0.7's fall (−0.0259; tile-swap p
   0.055) clears the within-day floor by 0.0005, and without the top-up
   tiles it is −0.0361 (p 0.025). Cross-day single-pass pairs differ more
   than within-day pairs (median 0.0144 against 0.0087), and the tile-swap
   test rejected 5 of 180 six-pass K = 2 replicate pairs, all mixing the
   days, where it had rejected none within a day. D48 assumes little drift
   within a week; on these image corners a one-day term is about the size
   of the within-day floor. It moved the two confirmatory contrasts in
   opposite directions (C1 −0.0172, C2 +0.0317).
2. **The first day, not the second, looks like the outlier** (not
   declared). The second day's image corners sit within 0.011 of the
   committed A-06 corners from March and June; the first day's were up to
   0.028 above them (this record's passes 1–3 surprise 3). C2 on the second
   day (+0.0653) is close to the committed +0.0605, and C1 (+0.0202) is
   closer to the committed +0.0103 than the first day's +0.0374 was.
   Descriptive only; the committed corners come from other dates and modes,
   and this record does not test drift (compare Obs 508).
3. **C2 nearly doubled** (not declared). The temperature effect at MEDIUM
   went from +0.0336, which cleared the rule by 0.0036, to +0.0653, which
   clears it by 0.0353. Item 1 accounts for the move.
4. **A top-up delivered real thinking at HIGH** (not declared; the top-up
   agent flagged bursty thought tokens). Five image HIGH T 0.7 tiles topped
   up on 2026-10-15 recorded 1,665 thought tokens (333 per request), where
   the same pass's 482 requests of 2026-10-14 recorded none, and 24 image
   MEDIUM T 0.7 top-up requests averaged 94.75 against 39.6. The per-pass
   figure for that HIGH pass (3.42 per request) is therefore entirely
   top-up thinking. Sensitivity (ii) drops these tiles and changes no
   verdict. The other 21 HIGH top-up requests recorded none.
5. **On passes 4–6, image HIGH at T 0.0 delivered no thinking at all**
   (all three passes 0), so C1 on the second day compares 0 with about 11
   thought tokens per request. Every HIGH pass still beats every MEDIUM
   pass at T 0.0, by less.

None of the gates failed, and the two runs are identical.

### Passes 1–3 (2026-10-14)

Checked against the list declared in P11, then anything else.

1. **In image, a thinking |Δ| ≥ 0.03 rejects after BH** (declared in
   P11). HIGH − MEDIUM at T 0.0 is +0.0374, with interval [+0.0104,
   +0.0680], BH-adjusted p 0.0428 (0.0214 in the all-eight family), and
   above the floor. The committed A-06 had +0.0103 here, with an interval
   straddling zero. The contrast is between levels that delivered about 1
   and about 11 thought tokens per request. This record does not explain
   the difference. Two features of the data bear on it. Every HIGH pass
   beats every MEDIUM pass. The MEDIUM T 0.0 passes are about three times
   as variable as the HIGH T 0.0 passes (0.0254 against 0.0074), and the
   floor they enter rests on 12 pairs.
2. **The image temperature effect at MEDIUM halved** (+0.0605 → +0.0336;
   not declared). It still fires, rejects in its registered family, and
   clears the floor, but by margins under 0.005. It would not reject in
   the all-eight family (0.0509), and its interval's lower bound is
   +0.0042. The change comes mainly from image MEDIUM T 0.7, which is
   0.0217 higher than the committed June corner.
3. **The image corners moved together** (not declared). Three of the four
   image corners are 0.022 to 0.028 higher than their committed
   counterparts (HIGH T 0.0, HIGH T 0.7, MEDIUM T 0.7), against
   −0.004 to +0.006 for every text corner. Each move is inside the
   within-execution floor. A common upward shift across three corners
   from different dates is consistent with the same-model drift that
   Obs 508 records, but this record does not test that.
4. **T 0.0 is not deterministic, and a little thinking makes it noisier**
   (not declared). Every T 0.0 corner varies between passes, and at T 0.0
   the MEDIUM corners are three to four times as variable as the HIGH
   corners (§ Replicate floors).
5. **Not a surprise in the analysis, but a correction to the record.**
   D64's "HIGH 0–2, MEDIUM 9–48" thought tokens per request
   (`planning/pi-decisions-2026-09-20.md`) matches the first pass of each
   corner (wave 1). Over all 32 passes the per-pass range is HIGH 0 to
   3.93 and MEDIUM 7.43 to 48.02.

None of the other P11 conditions occurred. No factor-T Δ fell below 0.03
or inside its floor, the estimators never split, every gate passed, and no
corner differs from its committed counterpart by more than the floor.

## Integrity

### P12 (2026-10-15)

- **Two independent runs** of `run-p12.sh` (`r3/`, `r4/`), in fresh
  processes with separate output directories and `PYTHONHASHSEED` 0 and 1,
  run concurrently, 11:30 to 11:34 UTC. Each ran the extended original
  driver, the post hoc script on its output, and the P12 driver; all six
  processes exited 0 and their logs carry no warning or error line. Every
  output of the two runs is identical apart from `generated_at` (a raw diff
  of each results JSON without that line shows no difference; CSVs byte for
  byte; the counts archives member for member). The transcript is
  `out-p12/integrity.txt` and the logs are in `out-p12/logs/`.
- **The extended original driver reproduces 2026-10-14.** Re-run on the
  merged tree (image pools now holding six passes), `d64_a06_replication.py`
  writes a results JSON that differs from the committed
  `out/d64_a06_results.json` only in `generated_at` and `git_head`, both
  floor CSVs byte for byte, the counts archive member for member, and the
  post hoc JSON exactly. The extension (`P1_RUNS`, `select_runs`, and the
  floor subset sizes and passes per arm read from the stacks) therefore
  changes no output.
- **Kernel "Bad page state" count** on sapphire was 0 before the merge and
  0 after both runs (`journalctl -k -b | grep -c "Bad page state"`).
- **The drivers as run** are the files committed in `b77624e15`: SHA-256
  `197bbd0542f4…` (`d64_p12_replication.py`), `47fc5e807b8e…`
  (`d64_a06_replication.py`, extended; the 2026-10-14 version, `90761d0fbea2…`,
  is in `711ed901f`), and `3253e075854e…` (`run-p12.sh`). The results
  JSON's `git_head` is `f54eb4ca9`, because the drivers were still
  uncommitted when they ran on that tree.
- **Independent arithmetic check:** C1, C2, the floor of passes 4–6, the
  four day differences, and the passes 4–6 corner gap and temperature
  contrast at HIGH were recomputed from `out-p12/d64_p12_per_pass_counts.npz`
  in a separate process with plain numpy, and agree to 6 dp.
- **Deterministic order (D63).** The bounds file's tile order is sorted
  (the driver halts otherwise), pass files are sorted by run, every
  resampler and permuter is seeded, and the two hash seeds give identical
  outputs.

### Passes 1–3 (2026-10-14)

- **Two independent runs** of `run-d64.sh`, in fresh processes with
  separate output directories (`r1/`, `r2/`) and `PYTHONHASHSEED` 0 and 1,
  run concurrently, give identical outputs. The results JSON matches once
  `generated_at` is removed (a raw diff shows no other difference), both
  floor CSVs match byte for byte, and the per-pass counts archive matches
  member for member. The post hoc JSON, computed from each run's archive,
  is also byte-identical. The transcript is `out/integrity.txt` and the
  logs are in `out/logs/`. Both runs exited 0, and their logs carry no
  warning or error line.
- **Kernel "Bad page state" count** on sapphire
  (`journalctl -k -b | grep -c "Bad page state"`) was 0 before the
  worktree was created and 0 after both runs.
- **The driver as run** is the file committed here (SHA-256 of
  `d64_a06_replication.py`: `90761d0fbea2…`). The record of each run in the
  results JSON (`git_head`) is `7ae996ce6`, the plan commit, because the
  driver was still uncommitted when it ran on that tree.
- **Independent arithmetic check:** every corner's pass-averaged F1, the
  image thinking Δ at T 0.0, and the image floor were recomputed from the
  saved per-pass counts, in a separate process with plain numpy, and agree
  to 6 dp.
- **Deterministic order (D63).** The tile order is the bounds file's order
  (no set iteration). Pass files are sorted. Every resampler and permuter
  is seeded, and the two hash seeds give identical outputs.

## Not done

- **P12: nothing beyond P12 and P12.1.** No post hoc interaction on passes
  4–6 or on six passes; no cross-date floor (W2.7 § 4) applied to the day
  effect; no per-contrast top-up masks (P7's convention, one mask for every
  affected contrast, was followed); no per-request thought tokens for the
  top-ups, which the top-up record does not keep (its `usage` totals only).
- **P12: no draft applied.** The three drafts in § For the PI are text for
  the PI's approval; the register row, `findings.md`, and the working notes
  are unchanged.
- **No change** to the register row, `a06_decision_rule.json`,
  `findings.md`, Obs 415 or Obs 509, the D64 entry, or any committed
  output (report only).
- **No floor at the cells' own aggregation.** A floor for means of 5 or 3
  passes would need 10 or 6 passes per corner. The floors here are
  measured at K = 2 (text) and K = 1 (image), which is conservative, and
  no verdict depends on the scaled extrapolation.
- **No cross-date test.** The D64 − committed differences are descriptive.
  W2.7 § 4's cross-execution floors were not applied to them.
- **No tile-level Matthews correlation coefficient (MCC).** A-06 is
  registered on F1, and the conditions manifest's tile-classification
  definition was not reproduced for these passes.
- **No tests under `tests/`.** The drivers are scoped to this record, like
  the drivers of earlier agent records.
- **No explanation of the image thinking-level effect.** This record does
  not attempt one (see § Surprises).

## For the PI

**Updated 2026-10-15 for P12.** Three drafts follow, for approval; none
is applied. The numbers are read from `out-p12/d64_p12_results.json` and
`out/d64_a06_results.json`. Under P12.1's mapping, C1 PARTLY selects
headline (a) and C2 REPLICATES adds no suffix. On 2026-10-14 the PI
accepted headline (b) and the earlier paragraph (D66 (3)); the mapping
approved under D67 replaces that choice for this outcome. Neither was
applied, so nothing needs reverting. The earlier draft is kept below under
§ Superseded.

### (a) A-06 (`h6-a06-decision-rule`): headline and dated paragraph

**Headline: (a), "TEMPERATURE IS THE DRIVER".** This is the headline the
outcome text already carries, so its opening is unchanged. The dated
paragraph below is appended to the outcome, after the 2026-10-13 thinking
disclosure, with the earlier text kept. Appending it lapses the row's
signature (its attests provide for revision and re-signing if D64 moves
the reading).

> D64 same-day replication (2026-10-15; reports/s164-agent-records/d64-a06-replication.md):
> all eight corners re-run on 2026-10-13 on gemini-3.1-pro-preview through
> the Batch API with thinking booked per pass
> (outputs/pro-2x2-replication-2026-10-13/; 5 passes per text corner, 3 per
> image corner), then 3 more passes per image corner on 2026-10-14 as a
> confirmatory test of the two image contrasts that were borderline on the
> first day, its criteria fixed before any of their F1 values were computed
> (D66 (4), D67). Top-ups (15 of 15,584 first-day requests real-time; 152
> of 5,844 second-day requests through the Batch API a day later) move no
> verdict. On the first day the registered rule fires again in all four
> cells, for text at +0.0500 at HIGH (dCI [+0.0262, +0.0723]) and +0.0464
> at MEDIUM ([+0.0218, +0.0704]), and for image at +0.0690 at HIGH
> ([+0.0385, +0.1011]) and +0.0336 at MEDIUM ([+0.0042, +0.0653]). All four
> reject after BH (permutation p < 0.0001, 0.0002, < 0.0001, 0.0318) and
> exceed the same-day replicate floor (the 95th percentile of replicate
> |dF1|, 0.0116 for text and 0.0295 for image). The image effect at MEDIUM,
> about half the committed +0.0605 on the first day, is confirmed on three
> independent passes run the next day, at +0.0653 ([+0.0352, +0.0954],
> BH-adjusted p 0.0002 across the two confirmatory contrasts, above that
> day's floor of 0.0205). Thinking was barely delivered (corner means
> 0–2.7 thought tokens per request at HIGH, 11–44 at MEDIUM). In text the
> reading holds with the date, mode, and thinking confounds removed. The
> HIGH − MEDIUM contrasts are +0.0026 and −0.0010 (p 0.84 and 0.92), and
> temperature accounts for 95–102 % of the corner gap. In image, at T=0.0,
> HIGH beat MEDIUM by +0.0374 on the first day ([+0.0104, +0.0680],
> BH-adjusted p 0.043, above the floor). On three passes the next day the
> difference was +0.0202 ([−0.0073, +0.0479]), short of the 0.03 rule, of
> BH-adjusted p < 0.05 (0.138), and of that day's floor (0.0205): same
> direction on three further passes but not confirmed; the check had
> roughly even odds of passing even if the effect were as large as first
> seen. Over all six passes it is +0.0288 (secondary; the extension was
> data-dependent). HIGH delivered under 1 and MEDIUM about 11 thought
> tokens per request (HIGH none on the second day), so this contrast
> measures the requested thinking level; whether the difference in
> delivered thinking causes it is not established. At T=0.7 the contrast is
> +0.0020 and +0.0069 on the two days. Temperature accounts for 97 % and
> 92 % of the image corner gap measured at HIGH on the two days, and 47 %
> and 76 % measured at MEDIUM. Between the days three image corners fell by
> 0.011–0.026 and one rose by 0.006, the largest move at the within-day
> floor (0.0254); these moves shrank the thinking contrast and enlarged the
> temperature contrast at MEDIUM. A post-hoc interaction test on the first
> day does not separate the two image temperature effects (+0.0354, p
> 0.089).

What changed against the paragraph accepted on 2026-10-14:

| Item | 2026-10-14 draft | This draft |
|---|---|---|
| Date and scope | 2026-10-14; the 2026-10-13 run | 2026-10-15; adds the 2026-10-14 image passes and their confirmatory purpose |
| Top-ups | 15 of 15,584 real-time | adds 152 of 5,844 through the Batch API a day later |
| Image temperature at MEDIUM | "about half the committed +0.0605 … clears the 0.03 rule by 0.0036 and the floor by 0.0041" | C2's verdict in the approved wording, with the next day's figures |
| Thought tokens at HIGH | corner means 0–2.3 | 0–2.7 (all six image passes; one top-up burst included) |
| "In image it holds only in part" | present | removed: under C1 PARTLY the image temperature reading holds and the thinking result is carried as unconfirmed |
| Image thinking at T=0.0 | +0.0374, BH p 0.043 | first day kept; next day's figures, the criteria missed, C1's verdict in the approved wording, and the six-pass estimate as secondary |
| HIGH and MEDIUM thinking delivered | about 1 and 11 | under 1 and about 11, none at HIGH on the second day |
| Thinking at T=0.7 | +0.0020 | +0.0020 and +0.0069 on the two days |
| Temperature's share of the image corner gap | 97 % (HIGH), 47 % (MEDIUM) | adds the next day's 92 % and 76 % |
| Day effect | not present | one sentence added |
| Post hoc interaction | +0.0354, p 0.089 | unchanged, labelled first day |

### (b) Note for `results/h6-registered-analyses/findings.md` § A-06

To be placed after the "Note, 2026-10-12" block. Applying it also needs
the document's banner and a changelog entry (Document Revision Policy);
drafts of both follow the note.

> **Note, 2026-10-15 (PI rulings D64, D66, and D67): the same-day
> genuine-Pro replication.** The table above, the four rule verdicts, the
> artefact, and the registered outcome text are unchanged. D64 re-ran the
> 2 × 2 on one date, in one mode, with thinking booked per pass
> (`outputs/pro-2x2-replication-2026-10-13/`): five passes per text corner
> and three per image corner on 2026-10-13, then three more per image
> corner on 2026-10-14. Those three were a confirmatory test of the two
> image contrasts that were borderline on the first day, with criteria
> fixed before any of their F1 values were computed (the first day's sign,
> BH-adjusted p < 0.05 across the two, |Δ| ≥ 0.03, and |Δ| above the
> replicate floor of the new passes). Record:
> `reports/s164-agent-records/d64-a06-replication.md` (branch
> `d64-a06-analysis`, draft PR #48).
>
> | Contrast | Committed (table above) | D64, first day | D64, next day (confirmatory) | D64, all passes (secondary) |
> |---|---:|---:|---:|---:|
> | Text, T = 0.0 − T = 0.7 at HIGH | +0.0595 | +0.0500 | not run | +0.0500 |
> | Text, T = 0.0 − T = 0.7 at MEDIUM | +0.0366 | +0.0464 | not run | +0.0464 |
> | Image, T = 0.0 − T = 0.7 at HIGH | +0.0750 | +0.0690 | +0.0786 | +0.0738 |
> | Image, T = 0.0 − T = 0.7 at MEDIUM | +0.0605 | +0.0336 | **+0.0653, replicates** | +0.0494 |
> | Text, HIGH − MEDIUM at T = 0.0 | +0.0124 | +0.0026 | not run | +0.0026 |
> | Text, HIGH − MEDIUM at T = 0.7 | −0.0105 | −0.0010 | not run | −0.0010 |
> | Image, HIGH − MEDIUM at T = 0.0 | +0.0103 | +0.0374 | **+0.0202, partly** | +0.0288 |
> | Image, HIGH − MEDIUM at T = 0.7 | −0.0042 | +0.0020 | +0.0069 | +0.0044 |
>
> In text, "temperature is the driver" holds with the date, mode, and
> thinking confounds removed. Both temperature contrasts fire the rule,
> reject after BH, and exceed the same-day replicate floor (0.0116), and
> the thinking contrasts are near zero. In image, the temperature contrast
> fires and exceeds the floor at both thinking levels on both days. At
> MEDIUM, borderline on the first day (BH-adjusted p 0.032, 0.0036 above
> the rule), it was confirmed on three independent passes run the next day
> (BH-adjusted p 0.0002). On the first day the image thinking contrast at
> T = 0.0 reached 0.03 and rejected after BH (BH-adjusted p 0.043), against
> this section's reading that the thinking contrast "reaches 0.03 in none
> of the four cells". On the next day it was +0.0202 (BH-adjusted p 0.138,
> below 0.03 and below that day's floor of 0.0205): same direction on three
> further passes but not confirmed; the check had roughly even odds of
> passing even if the effect were as large as first seen. Across the six
> image passes it is +0.0288, below 0.03 (secondary). The thinking level
> was requested rather than delivered (image HIGH delivered under one
> thought token per request at T = 0.0, and MEDIUM about 11), so the
> contrast cannot test thinking. Between the two days three image corners
> fell by 0.011–0.026 F1 and one rose by 0.006, the largest move at the
> within-day replicate floor; that change moved the two confirmatory
> contrasts in opposite directions. Under the mapping the PI fixed before
> the confirmatory test (D67), A-06's headline stays "temperature is the
> driver"; the register row's dated revision and its re-signing are the
> PI's.

Banner, new lead sentence (the current lead moves behind it):

> **Last revised**: 2026-10-15 (A-06 gains a dated note on the D64
> same-day replication, PI rulings D64, D66, and D67: temperature is the
> driver in text and image on same-day data, and the first day's image
> thinking contrast at T = 0.0 was not confirmed the next day; nothing
> registered changes). 2026-10-14: …

Changelog entry:

> ### 2026-10-15 — A-06: the D64 same-day replication noted (PI rulings D64, D66, and D67)
>
> A dated note is added under A-06. It records the D64 same-day
> replication and its confirmatory test on image passes 4–6
> (`reports/s164-agent-records/d64-a06-replication.md`, draft PR #48).
> Nothing above it changes: the table, the four rule verdicts,
> `a06_decision_rule.json`, and the registered outcome text. Commit: the
> one that applies it.

### (c) New Observation qualifying Obs 415 (`docs/notes/working-notes.md`)

The title follows the A-06 mapping (headline (a)). Obs 511 is the next
free number on `origin/main` at `8988bc6f7` and on every remote branch
checked on 2026-10-15; re-check before minting.

> ## Observation 511: Temperature is the driver on same-day data too — Obs 415 holds for the genuine-Pro 2 × 2 in text and image, and the image thinking-level effect seen on 2026-10-13 kept its direction on three further passes but was not confirmed (Session 164, 2026-10-15)
>
> **Context.** The Principal Investigator (PI) asked in Session 164 for a
> new Observation qualifying Obs 415 for image (ruling D66 (4)), and fixed
> under D67 that it quotes the confirmatory verdicts and that its title
> follows A-06's headline mapping. Obs 415 is not edited. Obs 415
> ("Temperature, not thinking level, drives the genuine-Pro corner gap",
> Session 135, 2026-08-17) read A-06's thinking × temperature 2 × 2 from
> committed corners run on different dates and in different modes, two of
> them with no recorded thinking. Obs 509 then found that Pro at HIGH and
> T = 0.0 did not think. Ruling D64 re-ran the 2 × 2 to remove those
> confounds. Below, T is temperature, "thinking" is HIGH − MEDIUM, Δ is a
> difference in micro-F1 at 20 m on the 487 gold-standard tiles, and "Pro"
> is `gemini-3.1-pro-preview`.
>
> **What was established.** All eight corners ran on 2026-10-13 through
> the Batch API with thinking booked per pass (five passes per text
> corner, three per image corner). Three more passes per image corner ran
> on 2026-10-14 as a confirmatory test of the two image contrasts that were
> borderline on the first day. Its four criteria were committed before any
> of their F1 values were computed: the first day's sign,
> Benjamini–Hochberg (BH) adjusted p < 0.05 across the two, |Δ| ≥ 0.03
> (A-06's rule), and |Δ| above the replicate floor of the new passes.
>
> | Contrast | Obs 415 (committed) | First day | Next day (confirmatory) | All passes (secondary) |
> |---|---:|---:|---:|---:|
> | Text, T at HIGH | +0.0595 | +0.0500 | not run | +0.0500 |
> | Text, T at MEDIUM | +0.0366 | +0.0464 | not run | +0.0464 |
> | Image, T at HIGH | +0.0750 | +0.0690 | +0.0786 | +0.0738 |
> | Image, T at MEDIUM | +0.0605 | +0.0336 | +0.0653, replicates | +0.0494 |
> | Text, thinking at T 0.0 | +0.0124 | +0.0026 | not run | +0.0026 |
> | Text, thinking at T 0.7 | −0.0105 | −0.0010 | not run | −0.0010 |
> | Image, thinking at T 0.0 | +0.0103 | +0.0374 | +0.0202, partly | +0.0288 |
> | Image, thinking at T 0.7 | −0.0042 | +0.0020 | +0.0069 | +0.0044 |
>
> 1. **Text: Obs 415 holds with the confounds removed.** Both temperature
>    contrasts fire the rule, reject after BH, and clear the same-day
>    replicate floor (0.0116); the thinking contrasts are +0.0026 and
>    −0.0010.
> 2. **Image temperature: Obs 415 holds, and the borderline cell is
>    confirmed.** At MEDIUM the first day's +0.0336 cleared the rule by
>    0.0036. On the next day it was +0.0653 (BH-adjusted p 0.0002, above
>    that day's floor of 0.0205), confirmed on three independent passes run
>    the next day.
> 3. **Image thinking at T = 0.0: not confirmed.** The first day's +0.0374
>    (BH-adjusted p 0.043, above the floor) contradicted Obs 415's "the
>    thinking contrast at matched temperature reaches 0.03 in no cell". On
>    the next day it was +0.0202, with BH-adjusted p 0.138, below 0.03, and
>    below the floor: same direction on three further passes but not
>    confirmed; the check had roughly even odds of passing even if the
>    effect were as large as first seen. Over six passes it is +0.0288
>    (secondary).
> 4. **Thinking was requested, not delivered.** Corner means were 0–2.7
>    thought tokens per request at HIGH and 11–44 at MEDIUM, and image HIGH
>    at T = 0.0 delivered none on the second day.
>
> **Reading.** Obs 415's title holds on same-day data in both modalities,
> provided "thinking level" is read as the requested level. Neither Obs 415
> nor this entry tests thinking, since Pro delivered a few tokens at most.
> The image thinking contrast at T = 0.0 is the one open item. It favoured
> HIGH on both days, with every HIGH pass above every MEDIUM pass, but its
> size halved and it missed three of the four criteria, so it stands as
> unconfirmed.
>
> **Methodological note.**
>
> 1. **Pre-specifying the confirmatory test changed the reading.** Passes
>    4–6 were requested partly because two image results looked
>    borderline. Pooled with the first day, the thinking contrast is
>    +0.0288 with permutation p 0.025, which would reject in an all-eight
>    BH family (0.040). The criteria fixed in advance read the new passes
>    alone, and they do not support it.
> 2. **A one-day term about the size of the floor.** Between 2026-10-13
>    and 2026-10-14 three image corners fell by 0.011–0.026 F1 and one rose
>    by 0.006. The largest move (image MEDIUM, T 0.7) is at the within-day
>    replicate floor (0.0254), and single passes from different days differ
>    more than single passes from one day (median 0.0144 against 0.0087).
>    That term shrank one confirmatory contrast by 0.017 and grew the other
>    by 0.032, so a borderline contrast between corners run on one day can
>    move by about the floor when re-run the next. The second day's corners
>    sit within 0.011 of the committed March and June corners, which
>    suggests the first day was the outlier; this is not tested (compare
>    Obs 497 and Obs 508).
>
> **Caveats.** Two days and one model version; 384 px and 487 tiles
> (Era 2), not the registered Phase-4 scope. The image floors rest on 12
> pairs per day and sit near their maxima, and the day effect rests on 24
> within-day pairs and sits at the edge of the floor. 152 of the second
> day's 5,844 requests were topped up through the Batch API a day later;
> dropping their 138 tiles changes no verdict. Five of those top-ups, at
> image HIGH T 0.7, delivered real thinking (333 thought tokens per
> request).
>
> **Findable later.** Obs 415 qualification, D64, same-day replication,
> genuine-Pro 2 × 2, A-06, confirmatory test, passes 4–6, C1 partly
> replicates, C2 replicates, temperature is the driver, requested thinking
> level, thought tokens, day effect, 0.0374 → 0.0202, 0.0336 → 0.0653,
> pooled 0.0288, within-day floor 0.0254.
>
> **Related.** Obs 415 (qualified here; its title holds); Obs 509 (Pro at
> HIGH and T = 0.0 did not think); Obs 508 (same-model drift is a standing
> condition); Obs 497 (the run date is a factor).
>
> **Artefacts**: `reports/s164-agent-records/d64-a06-replication.md`
> (draft PR #48: plan items P12 and P12.1, results, and these drafts);
> `reports/s164-agent-records/d64-a06-replication-scripts/out-p12/d64_p12_results.json`;
> `outputs/pro-2x2-replication-2026-10-13/` (`topup-2026-10-13.json`,
> `topup-2026-10-15.json`); `planning/pi-decisions-2026-09-20.md` D64,
> D66, and D67; plan commits `e783ed3ac`, `751525d7e`, `2d5cb991c`;
> results `b77624e15`.

### Other items for the PI

1. **Re-signing.** Appending draft (a) lapses `h6-a06-decision-rule`'s
   signature; the row then needs the PI's re-signing.
2. **The day effect and D48.** D48 lets claims comparing runs up to seven
   days apart take the within-execution floor plus a same-week verifier
   band, assuming little proposer drift within a week. On these image Pro
   corners, one day moved a corner by about the within-day floor. Whether
   that bears on D48 for image claims is the PI's call; nothing here asks
   for a run.

### Superseded: the 2026-10-14 draft (accepted under D66 (3), not applied)

Kept as written on 2026-10-14. The P12 drafts above replace it.

**Does A-06's outcome text need revising? Yes, in image.** Its registered
verdict (the rule fires for T in all four cells) reproduces on same-day
data, and its text reading holds with the confounds removed. Its image
reading, and its sentence "The thinking contrast at matched temperature
(not a registered Phase-2 factor) reaches 0.03 in none of four cells
(every CI straddles zero)", do not hold on the same-day data. The row's
attests say it is revised and re-signed if D64 moves the reading. A draft
follows. Like the 2026-10-13 thinking disclosure, it is a dated paragraph
appended to the outcome, with the earlier text kept. There are two options
for the headline.

- **(a)** Keep "TEMPERATURE IS THE DRIVER" and let the appended paragraph
  qualify it.
- **(b)** Change it to "TEMPERATURE IS THE DRIVER IN TEXT; IN IMAGE THE
  MAIN DRIVER, WITH THE REQUESTED THINKING LEVEL ALSO MATTERING AT T=0.0
  (D64 same-day replication)". I recommend (b), because the headline is
  what readers quote.

The draft paragraph below is for appending to `h6-a06-decision-rule`'s
outcome.

> D64 same-day replication (2026-10-14; reports/s164-agent-records/d64-a06-replication.md):
> all eight corners re-run on 2026-10-13 on gemini-3.1-pro-preview through
> the Batch API with thinking booked per pass
> (outputs/pro-2x2-replication-2026-10-13/; 5 passes per text corner, 3 per
> image corner; 15 of 15,584 requests topped up real-time, which moves
> nothing). The registered rule fires again in all four cells, for text
> at +0.0500 at HIGH (dCI [+0.0262, +0.0723]) and +0.0464 at MEDIUM
> ([+0.0218, +0.0704]), and for image at +0.0690 at HIGH ([+0.0385,
> +0.1011]) and +0.0336 at MEDIUM ([+0.0042, +0.0653]). All four reject after BH (permutation p
> < 0.0001, 0.0002, < 0.0001, 0.0318) and exceed the same-day replicate
> floor (the 95th percentile of replicate |dF1|, 0.0116 for text and
> 0.0295 for image).
> Thinking was barely delivered (corner means 0–2.3 thought tokens per
> request at HIGH, 11–44 at MEDIUM). In text the reading holds with the
> date, mode, and thinking confounds removed. The HIGH − MEDIUM contrasts
> are +0.0026 and −0.0010 (p 0.84 and 0.92), and temperature accounts for
> 95–102 % of the corner gap. In image it holds only in part. At T=0.0,
> HIGH beats MEDIUM by +0.0374 ([+0.0104, +0.0680], BH-adjusted p 0.043,
> above the floor). HIGH delivered about 1 and MEDIUM about 11 thought
> tokens per request, so this contrast measures the requested thinking
> level; whether the difference of about ten tokens in delivered thinking
> causes it is not established. At T=0.7 the contrast is +0.0020. The temperature
> effect at MEDIUM is about half the committed +0.0605 and clears the 0.03
> rule by 0.0036 and the floor by 0.0041. Temperature accounts for 97 % of
> the image corner gap measured at HIGH and 47 % measured at MEDIUM. A
> post-hoc interaction test does not separate the two image temperature
> effects (+0.0354, p 0.089).

Four consequential items are for the PI to decide; none is done here.

1. A dated note in `results/h6-registered-analyses/findings.md` § A-06,
   whose "Temperature is the driver" paragraph carries the same image
   reading.
2. An Observation recording the same-day result, because Obs 415's title
   ("temperature, not thinking, drives the genuine-Pro corner gap") holds
   in text and not unqualified in image.
3. The thought-token figures in the D64 entry (wave 1 only; § Surprises,
   item 5).
4. Whether the image result warrants more passes. Three more passes per
   image corner (about 5,800 calls) would put the image floor on 40 pairs
   at K = 3 rather than 12 at K = 1. That run would be a new API
   decision, and nothing here asks for it.

## Changelog

### 2026-10-15 — P12: the confirmatory test on image passes 4–6

**Trigger.** The PI approved three more passes per image corner (D66 (4);
runs 4–6, 2026-10-14, committed on `main`), then a confirmatory test of
the two borderline image contrasts on those passes alone, its wording, and
the headline mapping (D67; plan items P12 and P12.1, committed in
`e783ed3ac`, `751525d7e`, and `2d5cb991c` before any pass 4–6 F1 was
computed). The wave-3 passes were completed by a Batch top-up on
2026-10-15 (D67 (1), PR #51, `8988bc6f7`).

**What was added.** `origin/main` at `8988bc6f7` was merged in
(`4e10f282e`; registry rebuilt in `f54eb4ca9`). The P12 driver, the
extended original driver, `run-p12.sh`, and the outputs (`out-p12/`) are
in `b77624e15`; this text is in the commit that follows it. New sections:
the P12 bottom line, § Results: the confirmatory test on image passes 4–6
(P12), and the P12 parts of § Surprises, § Integrity, and § Not done.
§ For the PI is replaced by the three P12 drafts, with the 2026-10-14
draft kept under § Superseded.

**Claims that moved.**

| Claim | Before (passes 1–3) | After (P12) |
|---|---|---|
| Image thinking contrast at T 0.0 (C1) | +0.0374, BH p 0.043, above the floor: a declared surprise | PARTLY replicates: +0.0202 on passes 4–6, BH p 0.138, below 0.03 and the floor (0.0205); pooled +0.0288 (secondary) |
| Image temperature at MEDIUM (C2) | +0.0336, clears the rule by 0.0036 and the floor by 0.0041 | REPLICATES: +0.0653 on passes 4–6, BH p 0.0002, above the floor |
| The P5 label in image | none of the pre-specified labels applies | "temperature is the driver" on the pooled six passes (secondary) |
| Recommended A-06 headline | (b), accepted by the PI under D66 (3) | (a), "TEMPERATURE IS THE DRIVER", as P12.1's mapping requires for C1 PARTLY |
| Image thought tokens per request at HIGH (corner means) | 1.30 and 2.28 | 0.65 and 2.68 over six passes |

**What did not change.** Every passes 1–3 result (P1–P11) is unchanged:
the extended original driver reproduces the 2026-10-14 outputs exactly on
the merged tree, and the P12 driver's replay of passes 1–3 equals them. The
text results, the four factor-T verdicts, and the plan's text are
unchanged. The passes 1–3 sections are kept as written, with dated
pointers to P12 added to the bottom line's items 3, 4, and 7.

### 2026-10-14 — Original publication

The pre-specified plan was committed first (`7ae996ce6`) on branch
`d64-a06-analysis`, before any number was computed. The results, drivers,
and outputs were added in the following commit, with the plan's text
unchanged apart from a line marking its commit.
