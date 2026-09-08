# Recovery consistency audit — E71 dead-tile rerun (2026-09-08)

> **Last revised**: 2026-09-08 (later still — § 6.1: the three verifier stages
> refreshed and compared; the § 6 open item closed). See [§ Changelog](#changelog)
> for revision history.

Which derived artefacts were built from the **pre-recovery** versions of the passes
rewritten by the E71 dead-tile rerun (`99ae28ec4`, 2026-07-30 15:25:26 +1000) and
never rebuilt, which registered conditions cite them, and what a rebuild costs.

## 1. Scope and method

**The recovered passes.** `reports/verification/recovery-rerun-results.json`
carries **15** pass rows, not 16: `reports/verification/recovery-rerun-worklists.json`
lists a sixteenth, `flash35-pv-2x2::flash35-min-text-1of10::run3`, at `n_dead: 0`,
and `recovery-rerun-registration.md` § 1 records it as dropped (its second segment
GeoJSON already covered the tile). **The audit brief's inclusion of that pass is
therefore incorrect; no flash35 artefact is in scope.**

| pool (run::pool) | passes | dead tiles registered | recovered (first sweep) |
| --- | --- | --- | --- |
| `pv-diag-384::flash-high-image-n5-image-t0.0` | run1–3 | 84 | 72 |
| `pv-diag-384::flash-high-text-n5-text-t0.0` | run1–3 | 59 | 52 |
| `n1-outstanding-384::pro-image-high-t0` | run1–3 | 51 | 46 |
| `n1-outstanding-384::pro-text-high-t0` | run1–3 | 85 | 76 |
| `e47-propose-brief::propose_brief-text` | run4 | 7 | 7 |
| `h12-v2::r3-hp-heavy` | run3, run5 | 2 | 2 |

Deep sweep A (`reports/verification/recovery-rerun-results-deep.json`, committed
`d01ea4412`) recovered 10 more tiles across five of those passes; sweep B
(`-deep-b.json`) recovered none. Final 265/288 per the registration changelog.

**Vintage rule used.** An artefact is STALE if the last commit touching it is an
ancestor of `99ae28ec4` (`git merge-base --is-ancestor <commit> 99ae28ec4`) **and**
it consumes one of the 15 passes. Where an evaluation carries
`_metadata.e82_input_vintage`, the pinned commit — not the file date — is the
vintage.

**In-flight change.** `git log fee173d0b..HEAD` shows commit `185681674`
(2026-09-08 11:35:47 +1000, "data(recovery): n1-outstanding consensus rebuilt from
the recovered passes") landed **during this audit**. The n1-outstanding consensus
sets were STALE at audit start and are CURRENT at audit end; their evaluations are
not yet rebuilt. This report states the end-of-audit state.

## 2. Per-pool findings

### 2.1 `pv-diag-384` — image-t0.0 and text-t0.0

| derived artefact | vintage evidence | verdict |
| --- | --- | --- |
| `outputs/h11/pv-diag-384/flash-high-image-n5/image-t0.0/consensus/` (t1–t3, voting_summary) | last commit `77bb342b4` 2026-07-30, a descendant of `99ae28ec4` | CURRENT |
| `outputs/h11/pv-diag-384/flash-high-text-n5/text-t0.0/consensus/` (t1–t3, voting_summary) | `77bb342b4` | CURRENT |
| `outputs/h11/pv-diag-384/flash-high-image-n5/image-t0.0/verified-v1-n10/` | `probabilities.json` last commit `c6b5e6b10` 2026-05-06 (pre-recovery); `total_results` 802 = pre-recovery `consensus_t1` feature count read from `git show 2e8cc6481:…/consensus_t1.geojson` | **STALE** |
| `outputs/h11/pv-diag-384/flash-high-text-n5/text-t0.0/verified-v1-n3/` | `857d5f714` 2026-04-18; `total_results` 1256 = pre-recovery `consensus_t1` count at `09fe46a7f` | **STALE** |

Registered conditions on this pool:
`pv-diag-384::flash-high-image-n5-image-t0.0-consensus-1of3` and
`pv-diag-384::flash-high-text-n5-text-t0.0-consensus-3of3`. Both cite
`results/recovery-reeval-2026-07-30/…/evaluation.json` — the post-recovery
re-score — so **both are CURRENT**. Analysis citing them:
`pv-diag-384-consensus-calibration` (post-hoc, `manually_verified_at: null`).

Neither verified-v1 pass is cited by any condition's `detections`/`eval_path`, nor
by any analysis; they appear only as inventory rows in
`decomposition["pv-diag-384"].verifier_passes`.

**Inconsistency to flag.** `pv-diag-384-consensus-calibration` has
`output_path: results/rescore-2026-06-05/pv-diag-384/consensus-sweep`. The t0.0
evaluations in that directory are E82 vintage-frozen replays pinned to
`2e8cc6481` (image) and `09fe46a7f` (text) — i.e. they score the **pre-recovery**
consensus — whereas the two registered conditions' `eval_path` values point at the
post-recovery `recovery-reeval-2026-07-30` scores. The same pre-recovery pins hold
for `results/phase3a-image-matrix/high-t0.0/n10/high-t0-0-{1,2,3}of10/` and
`results/phase3a-text-matrix/high-t0.0/n3/high-t0-0-{1,2,3}of3/` (all listed in
`_ignored_evals`). Pinning is correct by D40 design; the mismatch between an
analysis output directory and its conditions' registered evals is the finding.

### 2.2 `n1-outstanding-384` — pro-image-high-t0 and pro-text-high-t0

| derived artefact | vintage evidence | verdict |
| --- | --- | --- |
| `outputs/h11/n1-outstanding-384/pro-image-high-t0/consensus/` (t1–t3) | rebuilt at `185681674` 2026-09-08; pre-recovery copies at `archive/pre-recovery-2026-09-08/n1-outstanding-384__pro-image-high-t0__consensus/` | CURRENT (rebuilt today) |
| `outputs/h11/n1-outstanding-384/pro-text-high-t0/consensus/` (t1–t3) | `185681674`; archive as above | CURRENT (rebuilt today) |
| `results/rescore-2026-05-31/n1-outstanding-384/pro-image-high-t0/consensus/consensus_t{1,2,3}/evaluation.json` | `_metadata.generated_at_utc` 2026-08-21, no `e82_input_vintage`; scored the then-working-tree file, which `185681674` has since replaced | **STALE** |
| `results/rescore-2026-05-31/n1-outstanding-384/pro-text-high-t0/consensus/consensus_t{1,2,3}/evaluation.json` | as above | **STALE** |

Feature counts, archive vs working tree (`len(features)`):

| set | pre-recovery | post-rebuild |
| --- | --- | --- |
| pro-image t1 / t2 / t3 | 665 / 627 / 604 | 730 / 690 / 648 |
| pro-text t1 / t2 / t3 | 1118 / 946 / 783 | 1192 / 991 / 842 |

Registered conditions citing the stale evaluations —
`n1-outstanding-384::pro-image-high-t0-consensus-{1,2,3}of3` and
`…::pro-text-high-t0-consensus-{1,2,3}of3` (six rows). Analysis citing all six:
**`h6-a07-voting-thresholds`** (type `sweep`, `preregistered: post-hoc`,
`manually_verified_at: 2026-08-17T13:02:16Z`,
`output_path: results/h6-registered-analyses`, `deviations: [E74, E57, E71]`).

The chain is exact: `a07_voting_thresholds.json` (`generated_at`
2026-08-17T09:46:16Z) records the Flash comparator curve as
0.472634 / 0.519913 / 0.566502 (text k1–k3) and 0.550909 / 0.549906 (image k1–k2);
the stale evaluations report F1@20 m of 0.4726 / 0.5199 / 0.5665 and
0.5509 / 0.5499. The same pre-recovery numbers are carried in
`results/conditions-manifest.md` (lines 108–113) and
`results/working-precision/gs-plateau-characterisation.md` (lines 76–78, 116).

ALREADY-HANDLED rows on this pool (ruling 3a, registered at `cf8a93c5d`
2026-09-07): eight of the nine `-post-e71` rows —
`pro-image-high-t0-single-pass-run_{1,2,3}-post-e71`,
`pro-text-high-t0-single-pass-run_{1,2,3}-post-e71`,
`baseline-pro-image-high-t-0-0-post-e71`, `baseline-pro-text-high-t-0-0-post-e71`.
Their pinned partners carry `input_vintage.detections_commit` `c3852ebad`
(per-run) and `1f443fd69` (pooled), with `recovery_commit: 99ae28ec4`.
`baseline-pro-{image,text}-high-t-0-0` are cited by `h6-a09-cost-gate`
(post-hoc, `manually_verified_at: 2026-08-17T13:02:16Z`); the six per-run rows are
cited by no analysis.

### 2.3 `e47-propose-brief` — propose_brief-text run_4

| derived artefact | vintage evidence | verdict |
| --- | --- | --- |
| `outputs/h11/e47-propose-brief/flash-high-text-n5/propose_brief-text/consensus/consensus_t{1..5}.geojson` + `voting_summary.json` | last commit `1f443fd69` 2026-04-16 (ancestor of `99ae28ec4`) | **STALE** |
| `outputs/h11/e47-propose-brief/flash-high-text-n5/union-input/run_4.geojson` | `52b0215a6` 2026-04-09; `processed_tiles` 480 vs run_4's current 487 | **STALE** |
| `outputs/h11/e47-propose-brief/consensus/flash-high-text-1of5.geojson` | `fbef3def9` 2026-05-31 (pre-recovery); 4358 features | **STALE** |
| `outputs/h11/e47-propose-brief/crops/flash-high-text-1of5/candidate_manifest.json` | `f33058f01` 2026-04-10; `source_geojson` names the 1of5 union; `total_detections` 4358 | **STALE** |
| `outputs/h11/e47-propose-brief/verified/flash-high-text-{1,2,3,4,5}of5/probabilities.json` | `6683952ac` 2026-05-06; all five `derived_from: "1-of-5 union"` (4358 / 1654 / 1072 / 753 / 487 results) | **STALE (verifier)** |
| `results/rescore-2026-05-31/e47-propose-brief/flash-high-text-n5/propose_brief-text/consensus/consensus_t{1..5}/evaluation.json` | `generated_at_utc` 2026-08-21, no e82 pin, scoring the stale consensus | **STALE** |
| `results/rescore-2026-05-31/e47-propose-brief/consensus/flash-high-text-1of5/evaluation.json` | as above; listed in `_ignored_evals` | **STALE (unregistered)** |

Direct `processed_tiles` evidence: run_4 now carries **22 detections on its 7
recovered tiles** (487 processed tiles), while `union-input/run_4.geojson` carries
**0** on those tiles (480 processed tiles). The pool consensus still counts votes
without them — 83 / 36 / 21 / 15 / 4 clusters touch a recovered tile at t1–t5.

Registered conditions: `e47-propose-brief::consensus-{1,2,3,4,5}of5`.
**No analysis in `results/run-analyses.json` cites any of them**
(`conditions_compared` search returns 0 for all five).

ALREADY-HANDLED: the ninth ruling-3a row,
`e47-propose-brief::single-pass-run_4-post-e71`
(`results/rescore-2026-09-07/e47-propose-brief/single-pass-run_4/evaluation.json`);
its pinned partner `single-pass-run_4` carries
`input_vintage.detections_commit: 52b0215a6`. Cited by no analysis.

### 2.4 `h12-v2` — r3-hp-heavy run_3 and run_5

| derived artefact | vintage evidence | verdict |
| --- | --- | --- |
| `outputs/h12-v2/greedy/r3-hp-heavy/consensus_t{1..5}.geojson` + `voting_summary.json` | `2e84d4a65` 2026-04-16 | **STALE** |
| `outputs/h12-v2/wbf/r3-hp-heavy/wbf_candidates.{geojson,json}`, `wbf_diagnostics.json` | `2e84d4a65` 2026-04-16 | **STALE** |
| `outputs/h12-v2/wbf/r3-hp-heavy/wbf_vote4.geojson` | `cee75dcb4` 2026-06-04 (still pre-recovery) | **STALE** |
| `results/h12-v2/greedy/r3-hp-heavy/t{1..5}/evaluation.json`, `results/h12-v2/with-mcc/r3-hp-heavy/evaluation.json`, `results/h12-v2/wbf-mcc/r3-hp-heavy/evaluation.json`, `results/h12-v2/wbf/r3-hp-heavy/evaluation.json` | all `generated_at_utc` 2026-08-20, no e82 pin, scoring the stale sets | **STALE** |

Registered conditions: `h12-v2::greedy-r3-hp-heavy`
(`outputs/h12-v2/greedy/r3-hp-heavy/consensus_t4.geojson` →
`results/h12-v2/with-mcc/r3-hp-heavy/evaluation.json`) and
`h12-v2::wbf-r3-hp-heavy` (`wbf_vote4.geojson` →
`results/h12-v2/wbf-mcc/r3-hp-heavy/evaluation.json`). Analysis citing both:
**`h12-v2-hp-hn-ratio`** (type `comparison`, `preregistered:
registered-exploratory`, `manually_verified_at: 2026-08-17T03:50:21Z`,
`output_path: results/h12-v2/analysis_summary.md`, last commit `a3f305520`
2026-04-23).

**Materiality is small and must be stated.** Only two tiles are involved. run_5's
recovered tile now carries 3 detections; run_3's carries 0. Across runs 1–5 the
two tiles hold 0/1/0/0/3 detections, so a rebuild changes vote counts on at most
two clusters (1 cluster touches those tiles at greedy t1 today; 0 at t2–t5, 0 in
`wbf_vote4`).

**Bookkeeping residue to flag.** `git show --numstat 99ae28ec4` shows run_3's
`.meta.json` and `.tiles.json` were rewritten but **its GeoJSON was not**. The
sidecar records `completed: 327`, `failed: 0`, `patched: [K-35-053-3_Elenovo_x672_y3360.png]`
and `recovery_history` records the recovery, but the GeoJSON's `processed_tiles`
is still **326** and omits that tile. Any rebuild gating on GeoJSON
`processed_tiles` (charter § 4 authority 1) will still see run_3 as short by one.

## 3. Rebuild cost

**US$0 — consensus/union rebuild from committed passes plus re-scoring:**

1. `results/rescore-2026-05-31/n1-outstanding-384/pro-{image,text}-high-t0/consensus/consensus_t{1,2,3}/evaluation.json`
   — 6 evaluations; the consensus inputs already exist (`185681674`).
   `results/recovery-reeval-2026-09-08/` does not yet exist.
   Downstream regeneration also needed: `results/h6-registered-analyses/a07_voting_thresholds.json`,
   `results/conditions-manifest.md`, `results/working-precision/gs-plateau-characterisation.md`.
2. e47 pool consensus `consensus_t{1..5}` + `voting_summary.json`, plus the five
   evaluations under `results/rescore-2026-05-31/e47-propose-brief/…/consensus/`.
   Requires refreshing `union-input/run_4.geojson` from the recovered run_4 first.
3. h12-v2 `greedy/r3-hp-heavy/consensus_t{1..5}`, `wbf/r3-hp-heavy/*`, and the
   eight h12-v2 evaluations. Fix the run_3 `processed_tiles` residue first, or the
   coverage gate will reject the rebuild.

**API calls required — verifier stages that must re-run on new candidates
(estimates only; nothing was run):**

| verifier stage | candidates verified (pre-recovery) | candidates after rebuild | new candidates | full re-verification |
| --- | --- | --- | --- | --- |
| `pv-diag-384/flash-high-image-n5/image-t0.0/verified-v1-n10` | 802 (`probabilities.json.total_results`) | 889 (current `consensus_t1.geojson`) | **+87** | 889 crops |
| `pv-diag-384/flash-high-text-n5/text-t0.0/verified-v1-n3` | 1256 | 1319 (current `consensus_t1.geojson`) | **+63** | 1319 crops |
| `e47-propose-brief/verified/flash-high-text-1of5` (the 2of5–5of5 sets are filtered subsets of it) | 4358 | not yet rebuilt | **≤22** (upper bound: all 22 run_4 detections on the 7 recovered tiles form new clusters) | 4358 crops |

Adding a pass shifts cluster centroids, so candidate identity is not stable and a
strict rebuild re-verifies the whole set (889 + 1319 + 4358 = **6,566** crops);
the "new candidates" column is the floor if identity-stable reuse is accepted.
Per-crop cost is **unverified** here — no token audit was consulted. None of these
three verifier stages is cited by any registered condition or analysis, so the
spend is optional under the current register.

## 4. What is unaffected, and why

- **The two live pv-diag t0.0 consensus cells.** Registration § 3 committed to
  re-materialising exactly these; `77bb342b4` did so and both registered
  conditions point at `results/recovery-reeval-2026-07-30/`.
- **The nine ruling-3a `-post-e71` rows** (`cf8a93c5d`, 2026-09-07). Their pinned
  partners carry `input_vintage` naming `recovery_commit: 99ae28ec4`, so the
  historical measurement and the post-recovery measurement are both on the record.
- **`outputs/h11/pv-diag-384/consensus/*.geojson`** (the run-level 1of5/1of10
  sets). They carry `total_passes: 5` or more, while the two recovered t0.0 pools
  hold only three runs each (`ls -d run_*`); `flash-high-text-1of5.geojson` was
  last committed at `5b82e0848` 2026-04-14, before the t0.0 passes were first
  committed (`2e8cc6481` / `09fe46a7f`, 2026-04-17). They cannot consume a
  recovered pass.
- **`n1-pro-rerun-384`** (the genuine-Pro corners). No pass of that run appears in
  `recovery-rerun-results.json`.
- **The in-run recovery legs (recovery kind 2).** Spot-checked as instructed.
  `scripts/stride55_prepare_and_union.py:66` `resolve_pass_paths` globs
  `{run}_recovery*` alongside the main detections;
  `scripts/gemini37_arm_ladder.py:103` `load_deduped_passes` raises `CoverageError`
  unless `processed == manifest`. Against
  `inputs/stride-55map-2026-08-25/g384_ov192_55map_manifest.json` (24,561 tiles):
  `outputs/stride-55map-2026-08-25/g384_ov192_55map/run_3` is 24,558 main-only
  (3 missing) and 24,561 with its 1 fragment (0 missing);
  `outputs/gemini37-55map-2026-08-29/g384_ov192_55map_g37/run_3` is 9,186
  main-only and 24,561 with its 2 fragments (0 missing). Both gates hold.

## 5. Unverified

- Whether `e47-propose-brief` **run_5**'s coverage shortfall
  (`union-input/run_5.geojson` `processed_tiles` 481 of 487) is registered
  anywhere. It is outside the E71 worklist and was not investigated.
- Per-crop verifier cost in US$ — no token audit was read for this report.
- Whether the ruling-3a `-post-e71` treatment is intended to extend to the
  consensus-level rows in § 2.2–2.4, or whether those are to be rebuilt in place.

## 6. Actions taken (2026-09-08, Session 150, PI instruction)

| finding | action | commits |
| --- | --- | --- |
| passes manifest counted only `run_N` metas; 48 complete passes read as partial | extractor unions `run_N_recovery*` fragment metas; 70 → 22 partial passes, all genuine residue | `dd9bc22fb` |
| conditions manifest's per-buffer `coverage` null on every row | filled from the evaluation's coverage block, else the pool's pass-union coverage (355 of 437 rows) | `dd9bc22fb` |
| n1-outstanding comparator sweeps stale (§ 2.2) | rebuilt at the original protocol (`scripts/rebuild_recovered_consensus.py`), pre-recovery sweeps archived; six cells re-scored (`scripts/recovery_reeval.py`, sapphire); rows re-pointed; H6 recomputed with the `-post-e71` aggregates — no verdict moved, image fragility flag retired; `findings.md` and both rows refreshed and re-signed | `185681674`, `10e933ded`, `0100d6b5c`, `e13323a63`, `93ff7f4e9`, `38aa9ed1b` |
| control: is the rebuild a protocol change? | today's builder on the archived pre-recovery n1 passes reproduces the April sweeps exactly (665/627/604; 1118/946/783) — deltas are recovery effects | scratch only |
| e47 sweep stale (§ 2.3) | rebuilt and five cells re-scored; the April sweep is additionally a pre-D6 double read of `run_5` (4,491 vs 4,146 t1 clusters at the pre-recovery vintage) — noted on the rows | `e01b8617a`, `93ff7f4e9`, `38aa9ed1b` |
| h12-v2 run_3 residue (§ 2.4) | meta rebuilt from the GeoJSON (326 of 327; `_correction` block; sidecars archived); the recovered tile's output is not preserved anywhere — residue 34 tiles, not 33 | `c053f5a41` |
| h12-v2 greedy + WBF sweeps stale (§ 2.4) | rebuilt at the original protocols (greedy: only the vote-1 layer changes, 1,518 → 1,521; WBF: 1,097 → 1,099 clusters); the t = 4 greedy set and the vote ≥ 4 WBF set are feature-identical to the archived ones, so both registered cells and `h12-v2-hp-hn-ratio` stand unchanged — no re-score, no permutation re-run | `e7ebc1695` |
| three uncited verifier stages (§ 3) | **refreshed** (S151, PI ceiling US$20; card `planning/verifier-stage-refresh-2026-09-08.md`): re-run at the recorded configuration on candidate sets rebuilt from the recovered passes (889 / 1,319 / 4,149 crops, 0 failed) into new dated directories beside the untouched originals; US$8.73 at list price (`cost_basis: "list"`; flex bills half); registered as `verifier_passes` inventory rows (e47's first; passes manifest 1,279 → 1,282); compared in § 6.1 — none is cited, nothing in the paper moves | `43516df9a` (outputs), `scripts/register_verifier_stage_refresh.py` |
| `pv-diag-384-consensus-calibration` output-directory mismatch (§ 5) | the six t = 0.0 sweep cells re-scored on the post-recovery consensus (`results/recovery-reeval-2026-09-08/pv-diag-384/consensus-sweep/`, `275c43fc0`); the image t = 0.0 best threshold moved 1-of-3 → 3-of-3 (0.497 → 0.5127), so a 3-of-3 row is registered and becomes the config's headline; text t = 0.0 stays 3-of-3 (0.6109); the analysis row's range reads 0.513–0.814 and names both directories | `8e98f8edf` |

Disclosure: E71 rider (2026-09-08) in `docs/methodology/preregistration/protocol-errata.md`.

### 6.1 Verifier-stage refresh — preserve and compare (2026-09-08, later; Session 151)

The three stages of § 3 were re-run on 2026-09-08 (card
`planning/verifier-stage-refresh-2026-09-08.md`; sapphire; commit `43516df9a`;
US$8.73 at list price — `cost_basis: "list"` in each `run.meta.json`, the flex
tier bills at half of list). Each refreshed stage sits in a new dated directory
beside its original, which is untouched. Registered as `verifier_passes`
inventory rows by `scripts/register_verifier_stage_refresh.py` (passes manifest
1,279 → 1,282; e47's first). Each `sweep_2d.json` is compared on
`full_evaluation_bounds` (487 tiles, curator reference): the best F1 over
vote threshold × probability threshold at 20 m, the operating point that gives
it, and the best at 50 m.

| stage | candidates | best F1 at 20 m (P / R; n kept) | operating point | best F1 at 50 m |
| --- | ---: | --- | --- | ---: |
| pv-diag image t0.0 `verified-v1-n10`, April sweep as committed (`b8961e56f`) | 802 (342 swept) | 0.2739 (0.633 / 0.175; 120) | vote ≥ 1, p ≥ 0.15 | 0.3423 |
| … the same stage, complete 802 probabilities re-swept (S151, $0; `results/recovery-reeval-2026-09-08/pv-diag-384/image-t0.0-verified-v1-n10-april-complete-resweep/`) | 802 | 0.6589 (0.665 / 0.653; 427) | vote ≥ 1, p ≥ 0.20 | 0.7981 |
| pv-diag image t0.0 `verified-v1-n10-recovery-2026-09-08` | 889 | **0.6872** (0.658 / 0.720; 476) | vote ≥ 1, p ≥ 0.20 | 0.8241 |
| pv-diag text t0.0 `verified-v1-n3`, April (`857d5f714`) | 1,256 | 0.8234 (0.856 / 0.793; 403) | vote ≥ 3, p ≥ 0.15 | 0.8568 |
| pv-diag text t0.0 `verified-v1-n3-recovery-2026-09-08` | 1,319 | **0.8508** (0.863 / 0.839; 423) | vote ≥ 3, p ≥ 0.15 | 0.8884 |
| e47 `verified/flash-high-text-1of5`, April (`52b0215a6`; complete after the 2026-05-06 57-crop cleanup, `6683952ac`; swept for the first time S151 on the PI's ruling — `results/recovery-reeval-2026-09-08/e47-propose-brief/verified-flash-high-text-1of5-april-complete-sweep/`; NOT a like-for-like, see the e47 reading) | 4,358 | 0.7953 (0.745 / 0.853; 498) | vote ≥ 3, p ≥ 0.20 | 0.8189 |
| e47 `verified/flash-high-text-1of5-recovery-2026-09-08` | 4,149 | **0.8735** (0.928 / 0.825; 387) | vote ≥ 4, p ≥ 0.15 | 0.9028 |

Readings:

- **Text — like-for-like** (both stages complete; the April sweep post-dates
  its probabilities). +0.027 F1 at an unchanged operating point, almost all
  of it recall (0.793 → 0.839; precision 0.856 → 0.863). The unverified
  vote ≥ 1 candidate set's recall rises 0.848 → 0.894 — the recovered tiles'
  candidates. Verifier uplift over the within-sweep vote ≥ 3, p ≥ 0 row is
  preserved: 0.6125 → 0.8508 (April: 0.6051 → 0.8234).
- **Image — the committed April sweep is NOT a comparator.** It was computed
  on 2026-04-17 (`b8961e56f`) when 342 of the 802 candidates carried a
  probability; the remaining 460 were verified in the 2026-05-06 cleanup pass
  (`c6b5e6b10`; `cleanup_history` in `probabilities.json`;
  `reports/phase3a-verifier-completeness-audit-2026-05-03.md` records the
  gap) and the sweep was never re-run — its vote ≥ 1, p ≥ 0 row has n = 342
  and recall 0.186. This is a staleness class § 1 did not look for (a sweep
  older than its own probabilities). **Surveyed corpus-wide the same day**
  (`reports/sweep-staleness-survey-2026-09-08.md`; sapphire; 265 verifier
  stages, 33 with an in-directory sweep): five stages are stale, all
  `pv-diag-384` image stages amended by the same 2026-05-06 cleanup
  (`c6b5e6b10`) — this one (gap 460) and four with gaps of 11, 1, 1, and 1
  (`image-t0.3/verified-v1-n5`, `image-t0.7/verified-v1-n5`,
  `image-t1.0/verified-v1-n5`, `scale-4-optimal-487/verified-v1-n10`);
  none is cited by a registered condition or analysis. On the PI's ruling
  the four small ones were re-swept on their complete probabilities
  (S151, sapphire, $0; `results/recovery-reeval-2026-09-08/pv-diag-384/README-april-complete-resweeps.md`):
  the gap-11 stage moves 0.7460 → 0.7475 at 20 m at the same operating
  point and the three gap-1 stages are identical to four decimals — the
  committed sweeps were materially sound, and the class matters only where
  the gap is large. Re-swept on the complete 802
  probabilities (row 2), the April stage scores 0.6589 and the refreshed
  stage's 0.6872 at the same operating point is a recovery effect of the
  text stage's size: +0.028 F1, recall 0.653 → 0.720, precision 0.665 →
  0.658; unverified vote ≥ 1 recall 0.697 → 0.759. Verifier uplift on the
  refreshed set: 0.4985 → 0.6872 at vote ≥ 1. The committed April
  `sweep_2d.json` stays as it is (preserve, do not swap); the re-sweep is
  preserved beside the other recovery re-evaluations.
- **e47 — first SWEPT proposer-verifier cell for this pool.** Correction
  (S151): the card and § 3 called the April stage "abandoned (57 of 4,358
  verified)"; that misread a cleanup-overwritten `run.meta.json`. The
  April stage verified all 4,358 candidates (2026-04-09, `52b0215a6`, a
  57-crop gap closed by the 2026-05-06 cleanup, `6683952ac`, whose meta
  overwrote the original — the image stage's pattern), but was never swept
  in place, never evaluated as a verified set (the one evaluation under its
  name, waived in `_ignored_evals`, scores the unverified candidate
  GeoJSON), and until S151 never registered (PI ruling 2026-09-08: it and
  `verified/text-baseline` are now inventory rows,
  `scripts/register_e47_april_verifier_stages.py`); its `2of5`–`5of5`
  siblings are CPU-derived vote-threshold subsets of the same
  probabilities, not verifier runs. **Swept for the first time on the PI's
  ruling** (table row above; `proposer_votes` mapped to `vote_count`,
  exact): best 20 m F1 0.7953 at vote ≥ 3, p ≥ 0.20, against the refreshed
  stage's 0.8735 at vote ≥ 4, p ≥ 0.15. **Not a like-for-like**: the April
  candidate set has 209 more vote ≥ 1 clusters and more at every vote tier
  (≥ 2: 1,654 vs 1,537; ≥ 3: 1,072 vs 998; ≥ 4: 753 vs 699; ≥ 5: 487 vs
  455) despite being built from pre-recovery passes with fewer detections,
  and § 2.3 had already found the April e47 consensus irreproducible at any
  vintage (pre-D6 resolver). The 0.078 gap is almost all precision (0.745 →
  0.928) at a looser vote tier — what looser April vote counts would
  produce — and is a construction difference, not a recovery effect; the
  refreshed stage is the pool's only sweep on a reproducible candidate set.
  Verifier uplift on the refreshed set over the within-sweep vote ≥ 4,
  p ≥ 0 row: 0.6561 → 0.8735; over vote ≥ 3: 0.5485 → 0.8727. The verifier
  flattens the vote-threshold curve (0.8489–0.8735 across vote ≥ 2–4) — the
  same pattern as the registered pv-diag text cells, on a five-pass pool.

None of the six stages is cited by a registered condition or analysis; the
refreshed directories are inventory, and these readings are the only place
they are compared. Disclosure: E71 rider addendum (2026-09-08, later) in
`docs/methodology/preregistration/protocol-errata.md`.

## Changelog

### 2026-09-08 (S151, fourth revision) — PI rulings executed: April e47 stages registered, five sweeps preserved

The two April e47 verifier directories are inventory rows; the four small
stale stages are re-swept complete (gap-11 stage 0.7460 → 0.7475, the
gap-1 stages identical); the April e47 stage carries its first sweep
(0.7953 at 20 m) with the finding that it is not a like-for-like against
the refreshed 0.8735 (different candidate-set construction). No registered
number moves.

### 2026-09-08 (S151, third revision) — sweep-staleness class surveyed corpus-wide

The § 6.1 image reading now cites `reports/sweep-staleness-survey-2026-09-08.md`:
five stale stages of 265, all the one May cleanup's pv-diag image stages, none
cited. No number in this report moves.

### 2026-09-08 (S151, second revision) — e47 April stage description corrected

The § 6.1 table and e47 reading called the April `verified/flash-high-text-1of5`
stage "abandoned (57 of 4,358 verified)", repeating the card § 1. Wrong: all
4,358 carry a probability (the 57 is the 2026-05-06 cleanup pass whose meta
overwrote the original). The stage was never swept or registered, which is
the accurate description. No number in the comparison moves.

### 2026-09-08 (later still) — § 6.1 verifier-stage refresh compared; § 6 open item closed

Refresh trigger: the card's § 5 after-run steps (`43516df9a` landed the
outputs). Numerical claims moved: none in §§ 1–5 (the § 3 cost estimate was
≈ US$9; recorded US$8.73 at list). New: the § 6.1 comparison table, and the
finding that the image stage's committed April sweep is a 342-of-802
partial-verification artefact (re-swept complete at $0). What did not change:
every finding of §§ 2–5; no registered condition or analysis cites the stages.

### 2026-09-08 (later) — § 6 actions taken

The refresh the audit motivated, with commits; three items left open.

### 2026-09-08 — Original publication

First audit of E71 derived-artefact consistency. Established: 15 recovered passes
(not 16 — the brief's `flash35-pv-2x2` entry is `n_dead: 0` and was dropped at
registration); 9 ruling-3a rows already handled; the n1-outstanding consensus
rebuilt mid-audit at `185681674` with its 6 evaluations now stale; 3 stale
consensus/union artefact groups (e47 pool consensus, e47 1of5 union chain,
h12-v2 greedy + WBF) and 3 stale verifier stages; 20 stale `evaluation.json`
files; 2 registered analyses affected (`h6-a07-voting-thresholds`,
`h12-v2-hp-hn-ratio`) plus one output-path inconsistency in
`pv-diag-384-consensus-calibration`.
