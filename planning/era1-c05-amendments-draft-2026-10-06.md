# C-05: amendments to the two Era-1 boards — draft for the PI

> **Last revised**: 2026-10-06 (approved and applied). See
> [§ Changelog](#changelog) for revision history.

**Status: APPROVED by the PI as written (2026-10-06, about 06:50 UTC) and APPLIED** to both rows' `outcome` in `results/run-analyses.json`. Tracker C-05
(`planning/text-track-transmission-2026-10-05.md`). The tracker called both
boards SIGNED; they are not. Both rows in `results/run-analyses.json` are
`unsigned` (their 2026-06-09 stamps are authoring stamps, queued for a first
walkthrough in `planning/legacy-signature-queue-2026-09-16.md`). So no D9
signature note applies: under the 2026-09-14 ruling an unsigned row's
outcome is amended in place, and the first walkthrough signs the amended
text. The paragraphs below would be appended to each row's `outcome`.

## `era1-single-pass-baseline-matrix`

> [AMENDED 2026-10-06, erratum E90; tracker C-05] Six of the 36 cells are one
> transmitted configuration: retest-phase2c::text-{canonical, plus-hp,
> pure-positive-canon, scale-4, scale-8} sent identical requests (a text-only
> request transmits no exemplar, so their library levels never reached the
> model), and retest-phase2b::text-t0.0 sent the same request again. All six
> are in the 15-member tie set and in Tier 1 (ranks 2, 3, 6, 8, 9 and 15;
> F1 0.597-0.609): their spread is run-to-run variance, their order carries no
> information, and no tier boundary rests on a difference between them (none
> of their 15 pairwise contrasts is significant, even uncorrected; lowest
> p 0.0588).
> Counted by distinct transmitted configuration, the board's 36 cells are 26
> and its 15-member tie set holds 9
> (reports/manipulation-check-2026-10-05.md § B.5).

## `era1-leaderboard`

> [AMENDED 2026-10-06, erratum E90; tracker C-05] Six of the 82 cells
> (retest-phase2c::text-{canonical, plus-hp, pure-positive-canon, scale-4,
> scale-8} and retest-phase2b::text-t0.0) are one transmitted configuration
> (a text-only request transmits no exemplar). All six fall in rank band 7
> (ranks 48-61, F1 0.597-0.609), outside the 10-member tie set; their spread
> is run-to-run variance and their order carries no information.

## Evidence

- Ranks, tiers and F1: `results/paper-eval/n1/512px-14buf-mcc/tiering/tiering_20m.json`
  and `results/era1-leaderboard/tiering_20m.json` (`ranking`, `tiers`);
  tie-set membership: each row's `tie_set` in `results/run-analyses.json`.
- Identical requests: erratum E90; `reports/manipulation-check-2026-10-05.md`
  § B.5 (group 16).
- No significant difference among the six: the single-pass board's
  `pairwise` list holds all 15 pairs among them; none is significant, and the
  lowest raw p is 0.0588 (plus-hp against scale-4, the A[45] pair; checked
  2026-10-06).

## Changelog

### 2026-10-06 (later) — Approved and applied

The PI approved both paragraphs as written; appended to each row's outcome.

### 2026-10-06 — Original publication (Session 161)

Drafted under the PI's acceptance of the Session 161 defaults; the form
changed from a signature note to an in-place amendment because both rows are
unsigned.
