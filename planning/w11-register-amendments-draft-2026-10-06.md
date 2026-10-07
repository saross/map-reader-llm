# W1.1: register amendments for D42 — draft for the PI

> **Last revised**: 2026-10-07 (§ 3 added: era1-leaderboard, replicate group 21). See
> [§ Changelog](#changelog) for revision history.

**Status: APPROVED by the PI on 2026-10-07 (all three texts, as shown in full in the session) and WRITTEN (`69df3b5d4`; manifests `c117cd012`).** Tracker
item W1.1 (`planning/text-track-transmission-2026-10-05.md`). Both rows are
UNSIGNED in `results/run-analyses.json` (`signature.status: unsigned`), so,
as for C-05 (`planning/era1-c05-amendments-draft-2026-10-06.md`), each
outcome is amended in place with approved text. Their artefacts were already
regenerated under D42 (`5986316b5`, 2026-10-05); only the register's outcome
sentences still quote the retired bootstrap p-values. Every number below was
re-read on 2026-10-06 from `results/family-fdr/family_fdr.json`,
`results/family-fdr/h1_cmt0106_pooled_modality.json` and
`reports/retest-bootstrap-check-2026-10-05-scripts/retest70.csv`
(`perm_p_f1`).

## 1. `h1-cmt0106-pooled-modality`

**Current:** "… delta +0.0238, CI95 [-0.0104, +0.0585], two-sided bootstrap
p = 0.1774 (B=10,000, seed 42). … pooling dilutes the significant extreme
pairs (brief-text vs image-only p=0.004; image-only vs brief+image p=0.006)
… Consequence: H1 does NOT survive the family BH correction …"

**Proposed (whole outcome):**

> NULL — the registered pooled modality effect does not reach significance.
> First execution of CMT-0106 (2026-07-30, sapphire, gates A/B passed):
> text-only group mean F1 0.5267 vs image-using 0.5029; delta +0.0238,
> CI95 [-0.0104, +0.0585] (paired tile bootstrap, percentile, B = 10,000,
> seed 42); two-sided p = 0.0715 by within-tile label permutation of the five
> conditions, each carrying its three runs (10,000 permutations, seed 42;
> PI ruling D42, regenerated 2026-10-05 in 5986316b5). That null is sharper
> than H1's own (equal group means), so read 0.0715 with the caveat in
> results/family-fdr/family_fdr.md § 1; the bootstrap p of 0.1774 first
> reported here is retired. Direction matches the falsified-designation
> finding (text >= image; E68) but pooling dilutes the significant extreme
> pairs (brief-text vs image-only p = 0.0055; image-only vs brief+image
> p = 0.009; paired tile-swap permutation, D42): verbose-text weakens the
> text pool and the two +image conditions strengthen the image pool.
> Consequence: H1 does NOT survive the family BH correction (adjusted
> p = 0.125; family-bh-fdr-confirmatory) — the outcome-blind selection
> resolved the outcome-material fork to the conservative branch. Artefact:
> results/family-fdr/h1_cmt0106_pooled_modality.json.

## 2. `family-bh-fdr-confirmatory`

**Current:** "Rejection set {H2, H3, H7} … Ranked: H2 (<1e-4, adj 0.00035),
H3 (<1e-4, adj 0.00035), H7 (<=0.001, adj 0.00233) REJECTED; H4 (0.124,
adj 0.217), H1 (0.1774, adj 0.248), H5 (0.756, adj 0.834), H8 (Simes 0.8344,
adj 0.834) not rejected. …"

**Proposed (whole outcome):**

> Rejection set {H2, H3, H7} at q=0.05 over m=7 — the smaller of the two
> pre-registered possibilities; unchanged by PI ruling D42, under which
> every input is now a permutation p (regenerated 2026-10-05 in 5986316b5).
> Ranked: H2 (p < 1e-4, adj 0.00035), H3 (p < 1e-4, adj 0.00035), H7
> (p = 0.0002, adj 0.00047) REJECTED; H1 (0.0715, adj 0.125), H4 (0.1366,
> adj 0.191), H5 (0.7262, adj 0.834), H8 (Simes 0.8344, adj 0.834) not
> rejected. The bootstrap p-values first quoted for H7 (0.001), H4 (0.124),
> H5 (0.756) and H1 (0.1774) are retired; the registration's quoted values
> stay on record in the artefact as registration_quoted_bootstrap_p. H6
> excluded (never run). H2 is a FALSIFIED directional prediction (two-stage
> improves F1 +0.076, clearing the registered >=0.05 stopping threshold in
> the direction the registration predicted against). Sensitivity: the
> all-contrasts 26-row correction (20/26 significant) reported alongside;
> complementary coverage, not nested. Artefact:
> results/family-fdr/family_fdr.json; registration committed before compute.

**Not re-verified here:** the sensitivity clause ("20/26 significant") is
carried unchanged; its artefact
(`results/pairwise/20m/fdr/pairwise_results_fdr.json`, 2026-03-28) is a
permutation result and outside D42's re-test.

## 3. `era1-leaderboard`: replicate group 21 (added 2026-10-07)

The manipulation gate (`scripts/check_manipulation.py`, PR #25) refused
`era1-leaderboard` on six pairs of replicate group 21 (manipulation-check
report § B.5: Phase 3c H9-A ≡ Phase 3a-high text T0.7, by design; the two
instruction files are byte-identical). The PI approved listing the group as
known (`5fac69fc5`) and a C-05-style note where a write-up treats the cells
as different configurations. The board's own ranking does
(`results/era1-leaderboard/tiering_20m.json`, re-read 2026-10-07): three
cells of one configuration at one aggregation sit in two tiers. The row is
UNSIGNED, so the note is appended to its outcome after the C-05 amendment.

**Proposed (appended to the outcome):**

> [AMENDED 2026-10-07, replicate group 21; manipulation gate] Three more
> cells are one transmitted configuration at one aggregation (text, HIGH
> thinking, T = 0.7, five passes, 4-of-5):
> retest-phase3a-high::text-high-t0.7-n5-4of5 (rank 13, tier 3, F1 0.730),
> retest-phase3c::text-h9-a-diversity-4of5 (rank 16, tier 4, F1 0.717; H9-A
> is the Phase 3a optimum carried forward by design) and
> retest-phase3a-replication::text-high-t0.7-n5-4of5 (rank 17, tier 4,
> F1 0.713). The tier boundary between rank 13 and ranks 16-17 separates
> replicates: their 0.013-0.017 F1 spread is inside the Era-1 five-pass
> replicate floor at 4-of-5 (0.024; reports/w27-replicate-floors-2026-10-06.md
> § 3). The 10- and 30-pass cells of the two Phase 3a runs (ranks 4, 6, 9
> and 10) are likewise replicates of one configuration, each at its own
> sweep-selected threshold.

**Not amended:** `null-exemplar-sensitivity-2026-09-13` and
`uplift-supplement-flatten` (both SIGNED) hold the same cells, but neither
contrasts them with each other: the first measures each cell against its
own null-exemplar variant, the second pairs each verified cell with its own
unverified anchor. Their refusals are table membership, not a claim.

## 4. On approval

Write the three outcomes into `results/run-analyses.json` in place (§ 1 and § 2 replace; § 3 appends), regenerate
the analyses manifest, tick W1.1 in the tracker, and record the approval
time here.

## Changelog

### 2026-10-07 — § 3 added

The era1-leaderboard note for replicate group 21, at the PI's request.

### 2026-10-06 — Original publication (Session 162)

Drafted for tracker item W1.1 after the W1 pass left it open.
