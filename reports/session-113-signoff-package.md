# Session 113 — sign-off package for Shawn

> **Last revised**: 2026-06-12 (token-load audit outcome appended as
> § 5.4). See [§ Changelog](#changelog) for revision history.

Everything queued for human review after the second-wave manifest
registration, the 55-map board refresh, and the Flash 3.5 permutation
closure. Work through top to bottom; each item carries its anchor.

## 1. Analyses awaiting `manually_verified_at` (7)

In `results/run-analyses.json` (regenerate manifests after signing:
`generate_post_run_report.py --all --write`):

| analysis | session | what you are signing |
|---|---|---|
| `verifier-robustness-matrix` | S111 | thinking × temperature one tier at N=5; high hurts n=1 (`results/verifier-robustness/matrix_tiering.json`) |
| `pass-budget-pareto` | S111 | v1 passes-axis ladder, one tier; opmax ns (p=0.363). Superseded by v2 for citation but remains the registered record |
| `min-vs-high-thinking-pv` | S113 | GS min ≈ high under PV (five targeted pairs, all ns); recall-ceiling mechanism; scope-qualified by Obs 362 |
| `pass-budget-pareto-v2` | S113 | cost-weighted frontier; efficient set {min6, min11, high31, high35}; 0/21 pairs sig |
| `flash35-model-roles` | S113 | Flash 3.5 wins in no role; proposer loss resolved (p=0.035), verifier losses are cost-rule ties |
| `unswept-pools-completeness` | S113 | 18-pool sweep; headline survives the global-optimum check; Pro-verifier discovery (post-hoc p=0.019) |
| `55map-canonical-leaderboard-50m` | S113 | the 8-cell deployment board: 24/28 sig, 5 tiers; T1 = {T03-k3, TH7-k3} |

`pv-diag-384-consensus-calibration` stays unsigned **by design**
(calibration material; its signed sibling is `diversity-dividend-384`).

## 2. Observations 357–364 (staged, `docs/notes/working-notes.md`)

Obs 357 (cost meta-rule) · 358 (55-map 50 m board) · 359 (diversity
dividend obsolete under PV) · 360 (working precisions) · 361 (GT
epistemics) · 362 (deployment reversal) · 363 (completeness sweep) ·
364 (min11 uplift halves the thinking gap).

## 3. User-observations candidates (S111–112)

`docs/notes/user-observations.md` — prune/accept the collaboration-pattern
candidates committed at `7113de5b7`.

## 4. Decision needed — 18-sweep citability

The completeness sweep scored 18 never-swept pools
(`results/verifier-robustness/unswept_pools_sweep.json`). **Two** are now
first-class conditions (`verified-adv-text-pro-vf-4of5`,
`verified-adv-image-3of5`); the remaining **16 are analysis-internal**,
flagged as pending your call in the `unswept-pools-completeness` analysis
note. Recommendation: leave the 16 analysis-internal — none is on a board
or in the paper narrative; the sweep JSON preserves them citably enough.

## 5. New results from this session worth a look

1. **Flash 3.5 role permutations** (the dossier § 11 "pending" tests,
   `results/flash35-2x2/flash35_permutations.json`): the proposer-role
   loss is statistically resolved (−0.0355, p = 0.035 raw; marginal under
   BH across the three role tests); both verifier-role losses are
   within-noise ties (p = 0.17 / p = 0.10) — the verifier verdict now
   formally rests on the cost meta-rule rather than a measured gap.
   Findings § 14 and dossier § 11 updated in place with changelogs.
2. **Board prediction miss (informative)**: the continuity predicted six
   tiers; the refreshed board kept **five** — the uplift (0.8290) is ns
   vs T03-k4 (0.8359) and shares Tier 2, while remaining significantly
   above TM-k3 and below TH7-k3 (Obs 364's claims hold). Recorded as
   predicted-vs-outcome in the board analysis entry.
3. **Uplift Track-2 eval**: the canonical-GT engine reproduced the
   committed sweep value to six decimal places (0.829028) — strong
   mechanism-equivalence evidence between the corrected-F1 engine and
   the board scorer.
4. **Token-load audit (2026-06-12,
   `reports/token-load-audit-2026-06-12.md`)**: the 55-map cost
   manifests are unreliable — the 2026-05-03 recovery merge
   double-counted token totals (text-min and text-high 2×, image 3×;
   t0.3 clean), all four priced standard instead of flex, and none
   billed thinking tokens. The Pareto cost model inherited both errors;
   rebuilt from per-item metadata (min pass $4.66, HIGH T0.7 $40.19,
   image HIGH $39.07 per 8,541-tile pass at flex; verifier
   $0.000693/call). **Efficient set and all F1/tier results unchanged**;
   dollars moved (min rungs 36–41% down, HIGH rungs 31–42% up — high31
   production ~$856 → ~$1,214; the § 16(c) trade is now ~$58 vs ~$207).
   True total
   spend across the five 55-map campaigns ≈ $722 flex (lower bound;
   retry attempts unrecorded) — **cross-check against the Google billing
   console**, which is ground truth. ~~Recommendation: regenerate the
   three corrupted manifests (and re-price t0.3) in a dedicated pass~~
   **DONE (Shawn-directed, 2026-06-12)**: generator fixed
   (`--pricing-tier` audited path, commit `dc8ac772c`) and all four
   manifests regenerated at flex with stub verifier legs reconstructed
   (commit `8e142df9c`); originals archived to
   `archive/superseded-cost-manifests-2026-06-12/`. Corrected campaign
   totals: $30.44 / $207.34 / $261.02 / $200.83.

## 6. Registration conventions adopted (flag if you disagree)

- The uplift run's `gt_reference` is **`combined`** (schema vocabulary
  for the canonical extended GT); the precise GT composition is in the
  run's `_flags`.
- The uplift pool's mixed provenance (passes 1–5 from
  `55maps-text-min-generalisation`, 6–10 new) is documented in the
  decomposition note; the `n-passes-over` drift WARN is the accepted
  honest signal (S106 convention).
- Flash 3.5 verifier model string recorded as `gemini-3.5-flash` (the
  stable name in `run.meta.json`); Flash 3 configs keep
  `gemini-3-flash-preview` for manifest consistency.

## Changelog

### 2026-06-12 — Token-load audit appended

Added § 5.4 summarising the token-load audit of the 55-map cost
manifests and the resulting cost-model rebuild (constants commit
`7360c54c4`; regenerated Pareto artefacts `d638fba22`). Headline cost
figures it supersedes: minimal pass ~$9.40 → $4.66, HIGH pass
"3× minimal" → $40.19 measured (8,541 tiles, flex, thinking billed).
No other section touched.

### 2026-06-11 — Original publication

Compiled at the close of the Session 113 registration wave
(commits `7aa28475b`…`a17d6bba3`).
