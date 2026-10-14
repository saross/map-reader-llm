# D64: A-06's registered rule on the same-day genuine-Pro 2 × 2

> **Last revised**: 2026-10-14 (original publication: the pre-specified
> plan, committed before any number was computed). See
> [§ Changelog](#changelog) for revision history.

- **Executed by**: Claude (Anthropic), Claude Code, model lane Opus 5.5
  (`claude-opus-5-5`), a background subagent of the main Session 164
  (S164) session.
- **Date**: 2026-10-14 (UTC).
- **Repository**: `map-reader-llm`, branch `d64-a06-analysis` from
  `origin/main` at `22c682449`.
- **Ruling and approval**: Principal Investigator (PI) ruling D64
  (`planning/pi-decisions-2026-09-20.md`); this analysis approved by the PI
  on 2026-10-14 ("yes, run the D64 analysis now"). Report only.
- **Guarantees**: no model Application Programming Interface (API) call; no
  committed result, output, document, or register row changed; at most four
  worker processes on sapphire.

## Pre-specified analysis plan

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

## Bottom line

Pending: computed after the plan commit.

## Changelog

### 2026-10-14 — Original publication

The pre-specified plan, committed on branch `d64-a06-analysis` before any
number was computed.
