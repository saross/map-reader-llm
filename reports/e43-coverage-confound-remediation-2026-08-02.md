# E43 coverage confound — investigation findings and remediation proposal

> **Last revised**: 2026-08-02 (original publication). Status: PROPOSAL —
> Phase R1 evidence runs executing; Phases R2–R4 await PI decisions.
> See [§ Changelog](#changelog).

**Investigators**: Session 125 (Claude Fable 5); two independent blind
investigation passes (design-intent; contamination surface) following
the ruling-11 discipline. Every figure below carries a source anchor;
the two full agent reports are preserved in the session transcript and
their key evidence is re-anchored here.

## 1. Summary

The registered erratum E43's temperature finding — "T=0.7 dramatically
outperforms T=1.0, ΔF1 ~+0.15, p<0.0001 at all pool sizes" (also
Obs 190) — is a **coverage artefact**, not a temperature effect. The
T=1.0 arm (`outputs/h11/consensus-384-UNINTENDED-T1.0/`, 30 runs)
covers 240 of 487 tiles; every post-2026-03-26 evaluation scored it
against 487-tile bounds, counting 221 of 435 ground-truth mounds
(50.8 %) as automatic false negatives. At matched scope the effect
disappears or reverses:

| comparison | scope | ΔF1 (T=0.7 − T=1.0) | source |
| :--- | :--- | ---: | :--- |
| Published (group_4) | MISMATCHED 487-vs-240 | +0.168 / +0.172 / +0.194 (N=5/10/30), p=0.0 | `results/pairwise/20m/group_4_temperature/` |
| Matched 487-tile | both arms 487 | **−0.021 (N=5) / −0.033 (N=10)** | `results/phase3a-text-matrix/minimal-t{0.7,1.0}/` |
| Matched 240-tile | both arms 240 | **+0.012**, CIs overlap | `archive/results-60-tile-validation/h11-384-consensus-flash-minimal-text-t{07,10}/` |
| Preregistered Phase 2b (Era 1, single-pass, K=3) | matched 340 | **+0.072**, FDR p=0.004 | `results/retest/phase2b/analysis_summary.md` |

**The paper's headline temperature claim is unaffected**: it rests on
the preregistered Phase 2b sweep, and `docs/paper/**` prose is clean —
the "cite Phase 2b, not E43" firewall held
(`docs/notes/working-notes.md:6070-6091` already directs this). What
is affected is the *magnitude/universality* story ("+0.15 at all pool
sizes", "halves detection quality") in internal tables, permutation
artefacts, and the errata register itself.

## 2. Was this a legitimate calibration-subset comparison? NO

The PI's caution — some designs legitimately compare smaller runs to
larger ones by removing calibration tiles — was checked first, against
the project's own scope taxonomy (`results/evaluation-scopes.md`: Eras
340/487/327, the pool_160 exclusion pattern). Verdict:

- The 240-tile set (`inputs/vectors/bounds/384/validation_bounds.geojson`)
  is the **384 px re-projection of the Era-1 60-tile validation split**
  (selection metadata: `inputs/tiles_384/tile_selection_metadata.json`,
  created 2026-03-14, method geographic_overlap ≥0.1 against the 60
  512 px validation tiles; generator `scripts/select_tiles_by_area.py`
  — built for tile-size comparability, not calibration control).
- It **contains 73 pool_160 calibration tiles** — the opposite of the
  exclusion pattern — and the canonical scope doc never lists a
  240-tile scope.
- The structural tell: in a legitimate calibration exclusion the
  BOUNDS shrink for both arms symmetrically. Here the bounds were held
  at 487 while one arm's DATA covered 240 — asymmetric by
  construction.

## 3. How it happened — three individually-reasonable steps

1. **2026-03-12/14**: the study was DESIGNED at 240 tiles
   (`studies/h11-384-consensus.yaml:69,106-112`) for H11 tile-size
   comparison against 512 px results — correct for its purpose; the
   487-tile 384 px scope did not yet exist (bounds first committed
   `8b52ab63b`, 2026-03-22). Execution matched design exactly: 240/240
   tiles, 0 failed, all 30 runs. **No dead tiles — a scope difference,
   not a coverage failure.** "UNINTENDED" refers only to temperature
   (config default T=1.0 overrode the YAML's 0.7 — that part of E43
   stands).
2. **2026-03-26**: a deliberate bounds standardisation re-scored all
   paper evaluations against full 487-tile bounds
   (`results/paper-eval/sapphire-eval.log`), fixing a real
   inconsistency. Of the eight studies in that pass, seven had 487/487
   coverage; this one alone had 240/487 = 49.3 %. Nobody checked data
   coverage; the automated sparse-coverage guard
   (`lib_advanced_metrics.py:70`, threshold 0.5) read zero_fraction
   0.4641 — **mound-bearing missing tiles produce FNs rather than
   zeros and so evade the very count that would have tripped it**.
3. **2026-03-28**: the temperature comparison was wired
   opportunistically (`configs/pairwise-comparisons.yaml` group 4,
   tagged `family: confirmatory`) under the "unexpected data as
   discovery" policy — defensible then, because the 240-tile study was
   the ONLY 384 px T=1.0 data in existence. The matched 10-run
   487-tile T=1.0 arm arrived 2026-04-17
   (`outputs/h11/pv-diag-384/flash-minimal-text-n30-t07/text-t1.0/`)
   and was never wired in (`grep -rl "text-t1.0" results/pairwise/` →
   zero files).

Two flat documentation errors propagate the confusion: the study
README ("487-tile scope") and E43's impact row ("30 runs × 487
tiles") — the runs are 240 tiles (E44's parallel row correctly says
240; `results/h11/analysis_summary.md:108` repeats the error and is
self-refuting against the adjacent bullet).

## 4. Contamination inventory (compressed)

Full sweep by the second blind pass; label aliasing (five names for
the condition: `flash-min-text-t10`, `FM text T=1.0`, `Flash MIN text
T=1.0`, `consensus-384-t1-0`, bare `384`) defeats naive grep — both
label forms swept.

| class | scale | key members |
| :--- | :--- | :--- |
| Permutation-test artefacts | **148 tests**; 6 live temperature tests (group_4 ×3 at 20 m, ×3 at 30 m; group_12) + **141 group_8 leaderboard files** using the study as comparator | `results/pairwise/{20m,30m}/group_4_temperature/`, `factor-analysis-20m/group_12/`, `leaderboard-{20m,30m}/group_8/` |
| BH families | 4 families (26/26/325/300 members) — **~530 clean tests carry q-values computed against confounded p-values** | pairwise + factor-analysis + leaderboard round-robins |
| Paper tables (all dated snapshots) | 9 files; ranks/tiers MOVE (Tier 9 empties; corrected ~0.64 lands in Tier 6); MCC boards confounded too (confusion cells sum to 487) | `results/paper-tables/leaderboard_tiers{,_20m}.md/.csv`, `leaderboard-20m-annotated.md` (incl. Discussion-ready prose "+0.17 to +0.19 … largest effect in the study", "halves detection quality"), `pairwise_hypothesis_table.md/.csv` (3/3 significant → plausibly 0/3), `spatial_tolerance_comparison.md`, `results/paper-eval/mcc/remaining/batch_mcc_summary.*` |
| Registered conditions | 35 conditions; caveat fields exist and are unset (`scope_override: null`, per-buffer `coverage: null`, `coverage_status: "normal"`) | `results/conditions-manifest.json`, `run-conditions.json` |
| Results docs | `factor_analysis_results.md` ("5/6 significant" family headline), `gs-plateau-characterisation.md` (8 rows), `results/h11/analysis_summary.md`, `reports/experimental-progression.md`, `reports/results-summary-session-58.md` (confounded AND internally garbled — separate defect) | |
| Register + notes | E43 impact row; E44's "for consistency" note; Obs 190 (`working-notes.md:4613-4618`) | |
| What already got it right | `results/passes-manifest.json` (honest 240 ×30); the archived matched evaluations (×2, `archive/results-60-tile-validation/`); Phase 2b; `docs/paper/**` | |

Also surfaced: the confound is **unique** (systematic scan of all 29
decomposed runs found no second genuine coverage mismatch), plus one
separate small defect — `n_tiles_processed` mis-populated for verifier
passes (`proposer-verifier-512` reads 140 candidate ids as tiles).

## 5. Proposed remediation (phased; decision points marked ▶)

### Phase R1 — matched evidence (EXECUTING now; $0 API, sapphire, new directory only)

Goal: a defensible evidence table for the erratum. Nothing existing is
touched; outputs land in `results/e43-matched-temperature/`.

1. Paired permutation tests, `--mode geojson`, matched 487-tile scope,
   both buffers (20 m, 30 m), 10,000 permutations, seed 42:
   - N=5: `flash-minimal-text-n30-t07/text-t0.7` first-5 consensus
     best-threshold vs `text-t1.0` first-5 consensus best-threshold
     (best-F1 operating point per arm from the existing
     `results/phase3a-text-matrix` sweeps — the project's standard
     selection rule).
   - N=10: same at 10 (t0.7 first-10 per the preregistered first-N
     rule vs t1.0's 10).
   - N=30 is impossible matched at 487 (T=1.0 has 10 runs); stated
     as a scope limit, covered by the 240-matched leg.
2. 240-matched leg: cite the two archived 2026-03-24 reports
   (ΔF1 +0.012, overlapping CIs) — a restore, not a recomputation —
   and re-verify their headline numbers read back correctly.
3. Assemble `results/e43-matched-temperature/findings.md`: the
   four-row evidence table (§ 1), per-test JSONs, and the coverage
   quantification (221/435 mounds; recall ceiling 0.556).

### Phase R2 — registration remediation ▶ (PI approval of exact text)

1. **New erratum** (E-next, dated): corrects E43's impact row (487 →
   240), records the coverage confound mechanism (E71's own
   artificial-false-negative language, at 247 tiles), supersedes the
   "~+0.15 at all pool sizes" direction with the matched evidence
   table, and notes the E44 scope expansion's comparability cost.
   E43's body is NEVER edited (append-only register).
2. **E71 rider**: post-recovery coverage counts (484–486, shortfall
   1–4) so its Live-impact paragraph stops overstating.
3. ▶ Whether the prereg-integrity items from wave-4 (broken § 8.6
   pointer path; `holdout_manifest.json` rename;
   `select_tiles_phase2.py` writing the old name) join as further
   errata entries.

### Phase R3 — results and table remediation ▶ (options per class)

1. README + `analysis_summary.md` corrections (flat factual fixes,
   living artefact descriptions; in-place with dated note).
2. Paper tables: ▶ choose per file — (a) regenerate with the matched
   arm (moves tiers/ranks; honest but rewrites dated snapshots) vs
   (b) superseded-figures banners pointing at
   `e43-matched-temperature/` (ruling-1-consistent for dated
   snapshots; RECOMMENDED). The annotated leaderboard's
   interpretation prose needs the banner regardless.
3. Permutation artefacts: never edited (data); group_4/group_12
   superseded by R1 outputs; ▶ group_8's 141 leaderboard files need a
   scoping decision (drop the confounded comparator column vs re-run
   the round-robin without it).
4. ▶ BH families: recompute q-values for the four families excluding
   (or replacing) the confounded tests — mechanical on sapphire, but
   changes significance counts in dated artefacts; recommend
   recomputing into `e43-matched-temperature/` with banners on the
   affected summaries, not in-place edits.
5. Instrument hardening: register the 240-tile pool in
   `results/evaluation-scopes.md`; set the 35 conditions'
   `scope_override`/coverage caveats; fix the coverage guard's blind
   spot (count unprocessed tiles directly from the run's
   processed_tiles, not via zero-detection inference); fix
   `n_tiles_processed` for verifier passes.
6. `reports/results-summary-session-58.md`: dated snapshot →
   superseded-figures banner (its ΔF1 column is also internally
   inconsistent — noted independently of the confound).

### Phase R4 — observations ▶

Obs 190 correction lands as a NEW Obs (never edit the old) via
obs-writer with the ruling-11 lane, after R1's numbers are in. The
session's obs-candidate on the guard blind spot (missing-mound tiles
evade the zero-count) can ride in the same entry or separately.

## 6. What is NOT affected

- `docs/paper/**` prose (firewall held).
- The Phase 2b preregistered temperature evidence (+0.072 single-pass,
  Era 1) — the paper's citable anchor, unchanged.
- Every other run's coverage (unique confound; 29-run scan).
- The E43 temperature-deviation record itself (the config default DID
  override the YAML — that erratum remains true; only its impact row
  and the derived comparison are wrong).

## 7. Correction to the wave-4 escalation figures

The wave-4 blind pass cited 0.6639 as the matched-bounds figure; the
design-intent pass established that number is the **60-tile**
evaluation. The genuine matched 240-tile figure is **0.6443** (5-of-5;
`archive/results-60-tile-validation/h11-384-consensus-flash-minimal-text-t10/consensus-analysis-report.json`).
The confound's magnitude story is unchanged (0.6443 vs 0.4712
mis-scoped); any remediation restoring the matched number must use
0.6443.

## Changelog

### 2026-08-02 — Original publication

Investigation findings (two blind passes), contamination inventory,
and the phased remediation proposal; Phase R1 evidence runs launched
the same session. Trigger: PI commissioned investigation and proposal
after the wave-4 triage escalation
(`reports/verification/c4-triage/mismatch-triage-2026-08-02-wave4.json`).
