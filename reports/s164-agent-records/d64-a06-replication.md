# D64: A-06's registered rule on the same-day genuine-Pro 2 × 2

> **Last revised**: 2026-10-14 (original publication: the pre-specified
> plan, committed first in `7ae996ce6` before any number was computed, then
> the results). See [§ Changelog](#changelog) for revision history.

- **Executed by**: Claude (Anthropic), Claude Code, model lane Opus 5.5
  (`claude-opus-5-5`), a background subagent of the main Session 164
  (S164) session.
- **Date**: 2026-10-14 (UTC).
- **Repository**: `map-reader-llm`, branch `d64-a06-analysis` from
  `origin/main` at `22c682449`. Commits: `7ae996ce6` (the plan, before any
  number) and the commit that adds this text (drivers, outputs, results).
  The library code the drivers import (`scripts/`) is `main`'s at
  `22c682449`, unchanged on the branch.
- **Ruling and approval**: Principal Investigator (PI) ruling D64
  (`planning/pi-decisions-2026-09-20.md`); this analysis approved by the PI
  on 2026-10-14 ("yes, run the D64 analysis now"). Report only.
- **Guarantees**: no model Application Programming Interface (API) call; no
  committed result, output, document, or register row changed; at most two
  worker processes on sapphire at any time.
- **Where the runs are**: sapphire, `~/scratch/s164-d64-2026-10-14/`
  (`wt/` the worktree; `r1/` and `r2/` the two independent runs, 01:49 to
  01:50 UTC; `logs/`, `pids/`). Drivers and run 1's outputs (run 2's are
  identical) are committed beside this record in
  `d64-a06-replication-scripts/` (`out/`).

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
   MEDIUM.
4. **The image temperature effect at MEDIUM roughly halved** against the
   committed A-06 (+0.0605 → +0.0336). It clears the 0.03 rule by 0.0036
   and the floor by 0.0041, and it would not reject if the eight contrasts
   were one BH family (adjusted p 0.0509). The image 2 × 2's interaction
   (+0.0354, post hoc) does not reject (p 0.089).
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
   longer holds on same-day data). A draft is in § For the PI.

## Results

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

### 2026-10-14 — Original publication

The pre-specified plan was committed first (`7ae996ce6`) on branch
`d64-a06-analysis`, before any number was computed. The results, drivers,
and outputs were added in the following commit, with the plan's text
unchanged apart from a line marking its commit.
