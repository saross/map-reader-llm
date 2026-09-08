# Recovery consistency audit — E71 dead-tile rerun (2026-09-08)

> **Last revised**: 2026-09-08 (original publication). See [§ Changelog](#changelog)
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
| h12-v2 greedy + WBF sweeps stale (§ 2.4) | **open** — needs the greedy sweep into `outputs/h12-v2/greedy/r3-hp-heavy/`, the WBF variant at `wbf_diagnostics.json`'s parameters, two re-scores, and a re-run of `h12-v2-hp-hn-ratio` (registered-exploratory, signed) | — |
| three uncited verifier stages (§ 3) | **open** — ≈ 6,600 crops at ≈ US$0.0013 each (≈ US$9) if a strict refresh is wanted; none is cited | — |
| `pv-diag-384-consensus-calibration` output-directory mismatch (§ 5) | **open** — noted for the PI | — |

Disclosure: E71 rider (2026-09-08) in `docs/methodology/preregistration/protocol-errata.md`.

## Changelog

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
