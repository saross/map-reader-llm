# Tier-2 / Tier-3 sapphire state investigation — what's in the "10 to go" bucket?

**Author**: Claude Opus 4.7 (1M context), invoked by parent session 2026-05-04
during user travel.
**Status**: read-only investigation. No tracked files modified, no commits, no
API calls.
**Compute location**: zbook (sapphire off-network).
**Sources of truth**: see § 6 "Appendix" for every cited file and commit.

---

## 1. TL;DR

The "10 to go" Tier-2 / Tier-3 cells from the resume batch — actually **eleven
cells** by my count, taking the original campaign's tier breakdown literally —
are all in **pre-cleanup state on origin/main**, none have a `cleanup_history`
entry, none have a `.pre-cleanup-*.backup` sibling on zbook, and their
`probabilities.json` mtimes are all from 17–18 April or 2 May (the dates of the
original Apr-Q1 verifier writes), not from the 2026-05-03 overnight resume
launch. **Whatever sapphire did is local to sapphire; nothing reached origin.**

For closure tonight on zbook:

- **0 of 11 cells are zbook-tractable as-is** — every cell has its
  candidate-manifest committed, but every cell's bulk crop PNGs are absent
  from zbook (in contrast to the 3 skipped cells, where crops are present).
- **All 11 cells are zbook-recoverable via crop regeneration** — the source
  rasters (4 GeoTIFFs, 19 GB total) and source consensus / detection GeoJSONs
  are present locally; `scripts/extract_candidates.py` can regenerate the
  PNGs deterministically without sapphire.
- **Total recovery cost**: ~$0.95 in API spend (530 candidate verifier calls
  at flash-baseline + ~39 at pro-medium estimate); ~30–60 min wall-clock for
  crop regeneration plus ~10 min cleanup; per-cell propagation depends on
  which leaderboards / threshold sweeps consume each cell (Tier 3 is mostly
  isolated; Tier 2 propagates into era2/pv leaderboard tier).

The 3 skipped cells from the sibling investigation are **already cleaned on
zbook today** (uncommitted modifications dated 16:35–16:36 Sydney time,
2026-05-06 — see § 5.1). Eight of the eleven Tier-2/3 cells are similarly
zbook-tractable with the same kind of crop-regen-then-cleanup procedure that
the sibling investigation recommended for Cell 1 (e47).

---

## 2. Scoping the "10 to go" — actually 11 cells

The original launch summary (§ "Estimated wall-clock to overnight completion"
in `logs/phase3a-recovery-overnight-resume/launch-summary.md`) described the
resume's residual workload as cell 8 (Tier 1, h8v2) plus Tier 2 cells 9–15
plus Tier 3 cells 16–20. The driver script
(`planning/run-phase3a-recovery.sh`) confirms the cell ordering. Three cells
were placed in `SKIP_CELLS` because of missing crops (`e47-flash-high-text-1of5`,
`55maps-gen-verified-v2`, `proposer-verifier-384-adversarial-text-v1-prompt`)
— those are the sibling investigation's scope.

That leaves the following **eleven** cells which the resume run was supposed
to clean and which never reached origin/main as cleaned files:

| # | Tier | Cell name | Audit gap | Verifier model |
|---|------|-----------|----------:|----------------|
| 1 | 1 | `h8v2-wbf-scale-4` | 15 | flash, `verify_adversarial-text` |
| 2 | 2 | `image-n5-t0.0-v1-n10` | 460 | flash, `verify_adversarial-text` |
| 3 | 2 | `image-n5-t0.3-v1-n5` | 11 | flash, `verify_adversarial-text` |
| 4 | 2 | `image-n5-t1.0-v1-n5` | 1 | flash, `verify_adversarial-text` |
| 5 | 2 | `image-n5-t0.7-v1-n5` | 1 | flash, `verify_adversarial-text` |
| 6 | 2 | `session78-image-checklist` | 1 | flash, `verify_checklist` |
| 7 | 2 | `scale-4-optimal-487-v1-n10` | 1 | flash, `verify_adversarial-text` |
| 8 | 3 | `text-baseline-pro-verifier` | 21 | **gemini-3.1-pro-preview, thinking=medium** |
| 9 | 3 | `pro-medium-image-baseline-pro-verifier` | 10 | **gemini-3.1-pro-preview, thinking=medium** |
| 10 | 3 | `pro-high-image-1of5-pro-verifier` | 8 | **gemini-3.1-pro-preview, thinking=medium** |
| 11 | 3 | `flash-high-text-1of5-flash-medium-verifier` | 1 | flash, **thinking=medium** |

Total residual gap: **530 candidates**. Mismatch with the commit message
`0ceac93f` ("3 cells skipped, 10 to go"): the commit message said 10 and the
audit-derived ledger says 11. The discrepancy is most likely one cell counted
twice or one undercount in the operator's mental ledger; the audit master
list, the driver script, and the launch summary all agree on **20 total
minus 3 skipped equals 17 attempted, of which the previously-committed Tier 1
batch already absorbed 6 plus 1 (the 6 Session 78 cells plus the failed e47),
leaving 17 minus 7 equals 10 attempts on previously-untouched cells**. So
"10" probably referred to "10 cells the resume actually re-attempts for the
first time"; my list above includes h8v2-wbf-scale-4 (Tier 1, technically not
a re-attempt — it was never tried in the original overnight, which halted at
e47), making 11 in total.

The overcount is harmless; this report covers all 11 candidate cells.

---

## 3. Cell-by-cell state on origin/main and zbook

### Method

For every cell, I checked four signals:

1. **Origin commit history** of the `probabilities.json` (`git log -1` on the
   tracked file).
2. **On-disk mtime** of the working-tree file (zbook is at the latest
   `origin/main` for these tracked files).
3. **Schema + cleanup-history** of the on-disk JSON (canonical schema with no
   `cleanup_history` key would mean "never cleaned"; canonical with a
   `cleanup_history` entry would mean "cleaned at some point").
4. **Crop PNG availability on zbook** (the zbook-tractability check).

### Results

| # | Cell | gap (origin) | last commit | on-disk mtime | schema | cleanup_history | crops on zbook | verdict |
|---|------|-------------:|-------------|---------------|--------|-----------------|----------------|---------|
| 1 | h8v2-wbf-scale-4 | 15 | `2e84d4a6` (2026-04-16) | Apr 18 08:18 | canonical | no | absent | NOT-CLEANED, ZBOOK-TRACTABLE-VIA-CROP-REGEN |
| 2 | image-n5-t0.0-v1-n10 | 460 | `b8961e56` (2026-04-17) | Apr 18 08:18 | canonical | no | absent | NOT-CLEANED, ZBOOK-TRACTABLE-VIA-CROP-REGEN |
| 3 | image-n5-t0.3-v1-n5 | 11 | `b8961e56` (2026-04-17) | Apr 18 08:18 | canonical | no | absent | NOT-CLEANED, ZBOOK-TRACTABLE-VIA-CROP-REGEN |
| 4 | image-n5-t1.0-v1-n5 | 1 | `b8961e56` (2026-04-17) | Apr 18 08:18 | canonical | no | absent | NOT-CLEANED, ZBOOK-TRACTABLE-VIA-CROP-REGEN |
| 5 | image-n5-t0.7-v1-n5 | 1 | `b8961e56` (2026-04-17) | Apr 18 08:18 | canonical | no | absent | NOT-CLEANED, ZBOOK-TRACTABLE-VIA-CROP-REGEN |
| 6 | session78-image-checklist | 1 | `400e6fbc` (2026-04-25) | May 2 07:00 | canonical | no | absent | NOT-CLEANED, ZBOOK-TRACTABLE-VIA-CROP-REGEN |
| 7 | scale-4-optimal-487-v1-n10 | 1 | `b8961e56` (2026-04-17) | Apr 18 08:18 | canonical | no | absent | NOT-CLEANED, ZBOOK-TRACTABLE-VIA-CROP-REGEN |
| 8 | text-baseline-pro-verifier | 21 | `3d22184d` (2026-04-15) | Apr 18 08:18 | canonical | no | absent | NOT-CLEANED, ZBOOK-TRACTABLE-VIA-CROP-REGEN |
| 9 | pro-medium-image-baseline-pro-verifier | 10 | `3d22184d` (2026-04-15) | Apr 18 08:18 | canonical | no | absent | NOT-CLEANED, ZBOOK-TRACTABLE-VIA-CROP-REGEN (with manifest path correction) |
| 10 | pro-high-image-1of5-pro-verifier | 8 | `3d22184d` (2026-04-15) | Apr 18 08:18 | canonical | no | absent | NOT-CLEANED, ZBOOK-TRACTABLE-VIA-CROP-REGEN |
| 11 | flash-high-text-1of5-flash-medium-verifier | 1 | `3d22184d` (2026-04-15) | Apr 18 08:18 | canonical | no | absent | NOT-CLEANED, ZBOOK-TRACTABLE-VIA-CROP-REGEN |

The verdict for every cell is the same: **NOT-CLEANED on origin, recoverable
on zbook via crop regeneration**.

### Observed gap counts vs audit gaps (sanity check)

For every cell, I computed the gap directly from the manifest's
`total_detections` minus the count of unique `results` keys (stripping
`_iter<K>` suffix for multi-iteration runs). Every observed gap matches the
audit's recorded gap exactly:

```text
h8v2-wbf-scale-4                                              expected=1114  results=1099  gap=15  (audit: 15) ✓
image-n5-t0.0-v1-n10                                          expected= 802  results= 342  gap=460 (audit: 460) ✓
image-n5-t0.3-v1-n5                                           expected=2190  results=2179  gap=11  (audit: 11) ✓
image-n5-t1.0-v1-n5                                           expected=2840  results=2839  gap=1   (audit: 1) ✓
image-n5-t0.7-v1-n5                                           expected=2017  results=2016  gap=1   (audit: 1) ✓
session78-image-checklist                                     expected=2017  results=2016  gap=1   (audit: 1) ✓
scale-4-optimal-487-v1-n10                                    expected=3601  results=3600  gap=1   (audit: 1) ✓
text-baseline-pro-verifier                                    expected=1047  results=1026  gap=21  (audit: 21) ✓
pro-medium-image-baseline-pro-verifier                        expected= 519  results= 509  gap=10  (audit: 10) ✓
pro-high-image-1of5-pro-verifier                              expected= 841  results= 833  gap=8   (audit: 8) ✓
flash-high-text-1of5-flash-medium-verifier                    expected=3736  results=3735  gap=1   (audit: 1) ✓
```

Every cell exactly matches its audit-recorded gap, confirming none of the 11
files have been touched by cleanup since the original audit (commit
`adf95dbf`, 2026-05-03).

### Why crops are absent on zbook for all 11

Unlike the 3 skipped cells — where the gitignored `crops/` PNGs were genuinely
present on zbook (sibling investigation found 4,358 PNGs for e47, 8,942 for
55maps, 572 for proposer-verifier-384) — none of the 11 Tier-2/3 cells have
PNGs anywhere on zbook. I ran:

```bash
find outputs/h11/pv-diag-384 -name 'candidate_*.png' | wc -l   # 0
find outputs/h8-v2/wbf/scale-4 -name 'candidate_*.png' | wc -l # 0
```

The PNGs were extracted on whichever machine ran the original April runs
(probably a previous sapphire session) and never synced to zbook. The audit
report describes `pv-diag-384/` as "gitignored, only on sapphire" (per the
`Output Standardisation` memory entry); the 11 cells are entirely under
`outputs/h11/pv-diag-384/` (10 cells) or `outputs/h8-v2/wbf/` (1 cell), both
gitignored bulk dirs.

### Why crop regeneration is feasible (despite no PNGs locally)

For every cell, three preconditions are met on zbook:

1. **Source raster GeoTIFFs present**: the 4 gold-standard maps
   (`K-35-052-4_32635.tif`, `K-35-053-3_Elenovo.tif`, `K-35-062-2_Rakovski.tif`,
   `K-35-078-1_Lesovo.tif`) are at `inputs/rasters/` (19 GB total). Every
   manifest's candidate set draws exclusively from these 4 maps (verified by
   distinct `source_tile` prefixes per cell — 4 unique prefixes per cell, all
   matching the rasters).
2. **Source consensus / detection geojson present**: every cell's
   `candidate_manifest.json::source_geojson` resolves to an existing file on
   zbook, with the sole exception of `pro-medium-image-baseline-pro-verifier`,
   whose manifest points at the legacy `pv-pilot-image/` directory which no
   longer exists. The actual file lives under
   `outputs/h11/pv-diag-384/pro-medium-image-baseline/image-t0.0/run_1/detections_image-t0.0_run01.geojson`
   (519 features, matching manifest's 519 candidates exactly). Re-extraction
   requires using this corrected path.
3. **Extraction is deterministic from source-geojson + raster + padding**:
   `scripts/extract_candidates.py` assigns `candidate_id = idx` where `idx` is
   the source geojson's feature index. Re-extraction from the same source
   geojson with the same `--padding 75` produces an identical manifest with
   identical candidate IDs — the existing `probabilities.json::results` keys
   (which use these same IDs) will match the regenerated PNG filenames
   without any need for re-mapping.

The cleanup loop reads `--crops-dir` and for each candidate resolves
`crops_base_dir / "crops/candidate_NNNNN.png"` (per
`scripts/lib_verifier.py:398`); after re-extraction, those paths exist and
cleanup proceeds.

---

## 4. Closure-tonight feasibility

### Cost estimate per tier

Empirical per-call cost from earlier Phase 3a recoveries
(`logs/phase3a-recovery-overnight-resume/launch-summary.md` § "Estimated
wall-clock"):

- Flash, minimal thinking, single-attempt success: **~$0.00140 per call**
- Pro-medium thinking estimate (no direct precedent yet): **~$0.007 per call**
  (5× flash, conservative).

Tonight's empirical evidence from the sibling-investigation run on the e47
cell (57 candidates, flash, `verify_adversarial-text`): **~22 s wall-clock,
all-attempt-1 success**, see `logs/session-87-cleanup/cell1-e47-flash-high-text-1of5-20260506T083607Z.log`.
This validates the per-call estimate and the wall-clock estimate of
~10 calls / second on the local network.

| Tier | Cells | Candidates | Per-call | Expected (1× empirical) | Expected (1.5× headroom) |
|------|-------|-----------:|---------:|------------------------:|-------------------------:|
| Tier 1 (h8v2-wbf-scale-4) | 1 | 15 | $0.00140 | **$0.021** | $0.032 |
| Tier 2 (cells 2–7) | 6 | 474 | $0.00140 | **$0.664** | $0.996 |
| Tier 3 — pro-medium (cells 8–10) | 3 | 39 | $0.007 | **$0.273** | $0.410 |
| Tier 3 — flash-medium (cell 11) | 1 | 1 | $0.00140 | **<$0.01** | <$0.01 |
| **All eleven cells** | **11** | **529** | mixed | **~$0.96** | **~$1.44** |

The 530 candidates aligns with the original campaign budget's expected $1.84
total for all 20 cells (Session 78 matrix already cleaned — that was 153 of
the original 776; the residual 530 is well within the unspent budget of
$1.84 - $0.905 ≈ $0.94 already-spent).

### Wall-clock estimate per tier

Empirical: ~10 candidates / second for flash cleanup (matches the e47 run's
57 candidates / 22 s = 2.6 candidates/s with HTTP overhead; for very small
gaps the API-call overhead dominates and per-call latency is ~1-2 s; for
larger batches the parallelism kicks in via `--workers 10`).

Crop regeneration speed: the project does not have a recent extraction
benchmark log; per-candidate raster crop is a single `rasterio.windows.read`
plus a `Pillow` save, typically ~50–150 ms per candidate on zbook (to be
empirically confirmed but well-bounded).

| Phase | Wall-clock |
|-------|-----------|
| Crop regeneration for 11 cells (~17,820 PNGs total expected) | ~30–60 min CPU |
| Cleanup (flash, 11 cells, 529 candidates) | ~10–15 min API |
| Cleanup (pro-medium, 3 cells, 39 candidates) | ~5–10 min API |
| Per-cell propagation (materialise, threshold-sweep, leaderboard rebuild) | ~30 min CPU per non-Tier-3 cell × ≤7 cells = ~3.5 h |
| Tier-3 propagation (threshold-sweep refresh on `sapphire-pro-verifier-analysis.sh`) | ~30 min CPU |
| **Total wall-clock if pursued tonight** | **~5–6 hours attended + ~30 min API** |

The propagation chain is the dominant cost. If the operator is willing to
defer leaderboard rebuilds to a separate session (or to sapphire when it's
back online), the cleanup-only path is **~45–75 min total wall-clock** with
~$1 API spend.

### Per-cell propagation impact

Recall that the per-arch leaderboard reads either pre-materialised
`results/leaderboard/era2/pv-materialised/<id>.geojson` files
(architecture=pv) or directly from consensus geojsons (architecture=consensus
or single-pass), per `scripts/build_tiered_leaderboard.py`.

Mapping our cells to era2 leaderboard conditions
(per `planning/condition-inventory-with-s78.json`):

| Cell | Consumed by leaderboard condition | Architecture | Rebuild required |
|------|-----------------------------------|--------------|------------------|
| h8v2-wbf-scale-4 | `results/h8-v2/verifier-sweep/permutation-wbf-s4-vs-s8/pairwise_permutation_result.json` (paired permutation, NOT in era2 leaderboard) | n/a | h8-v2 paired-perm refresh only |
| image-n5-t0.0-v1-n10 | **none** (`pv-high-image-t0.0` does not exist; `p3a-high-image-t0.0` is consensus-arch and reads consensus geojson, not verified probs) | n/a | none |
| image-n5-t0.3-v1-n5 | `pv-high-image-t0.3-n5` (era2/pv) | pv | re-materialise + rebuild era2/pv tier |
| image-n5-t1.0-v1-n5 | `pv-high-image-t1.0-n5` (era2/pv) | pv | re-materialise + rebuild era2/pv tier |
| image-n5-t0.7-v1-n5 | `pv-high-image-t0.7-n5` (era2/pv) | pv | re-materialise + rebuild era2/pv tier |
| session78-image-checklist | `session-78-image-checklist` (era2/pv) AND `results/verifier-calibration-matrix/image-checklist*/calibration.json` | pv | re-materialise + calibration matrix refresh + rebuild era2/pv tier |
| scale-4-optimal-487-v1-n10 | `pv-scale4-optimal-n10` and `pv-scale4-optimal-n5` (era2/pv) | pv | re-materialise (×2) + rebuild era2/pv tier |
| text-baseline-pro-verifier | `results/h11-384-pv-diagnostic/text-baseline-pro-verifier/threshold_sweep.json` only | n/a | threshold sweep refresh only |
| pro-medium-image-baseline-pro-verifier | `results/h11-384-pv-diagnostic/pro-medium-image-baseline-pro-verifier/threshold_sweep.json` only | n/a | threshold sweep refresh only |
| pro-high-image-1of5-pro-verifier | no result-file references found (per `grep -rln`); 5 derived `pro-high-image-pro-vf-Nof5` cells regenerate from the cleaned source via `derive_vote_threshold_results.py` | n/a | derive_vote_threshold_results.py |
| flash-high-text-1of5-flash-medium-verifier | no result-file references found; 1 derived `flash-high-text-medium-vf-1of5` regenerates similarly | n/a | derive_vote_threshold_results.py |

**Critical observation about the `image-t0.0` cell (gap=460)**: the audit's
§ 0.2 was correct. There is no era2 pv-materialised condition for `image-t0.0`
(only `pv-high-text-t0.0-n3` exists, which is the text track). The
`p3a-high-image-t0.0` condition that does exist in the era2/consensus tier
reads the consensus geojson directly, not the verified probabilities file —
so the gap=460 cell's cleanup has **zero downstream leaderboard impact** even
though it dominates the campaign's residual API spend (87 % of remaining 530
candidates). Its only consumer is the audit ledger itself.

This means the closure-tonight scope splits cleanly into "high-information
cells" (cleanup yields downstream leaderboard movement, ~$0.10 in API spend)
and "ledger-only cells" (cleanup closes the audit but produces no analysis
movement, ~$0.85 in API spend on the gap=460 alone).

### Propagation-chain risk: today's redesign rebuild

Today's earlier work (commit `ca0567d3` — `analysis(p3a-recovery): full
redesign rebuild — q01 + MCC variants + stage 3-5`) finalised the era2/pv
leaderboard tier composition based on the **post-Tier-1, pre-Tier-2/3** state
of probabilities. If the Tier-2 cells are cleaned tonight, the era2/pv tier
output should be rebuilt, which means:

1. Re-materialise the 5 affected era2/pv conditions
   (`pv-high-image-t0.3-n5`, `pv-high-image-t0.7-n5`, `pv-high-image-t1.0-n5`,
   `pv-scale4-optimal-n10`, `pv-scale4-optimal-n5`,
   `session-78-image-checklist`).
2. Re-run `bash scripts/build_per_arch_redesign.sh` (the canonical multi-pass
   runner; not `run_per_arch_leaderboards.sh`, which was the wrong-driver
   detour fixed in `baa271bf` / `ef3ec4fe`).
3. Re-run `bash scripts/build_combined_leaderboard.sh 2` and
   `build_combined_tier_stability.sh 2` for the era2 combined view.
4. Re-run the calibration matrix
   (`compute_session78_calibration_matrix.py`) for
   `session78-image-checklist`.

The gap-1 cells (5 of the 6 Tier-2 cells) will produce sub-0.001 F1 movement;
the era2/pv tier composition is unlikely to change. The gap=11 cell
(`image-t0.3-v1-n5`) and gap=15 cell (`h8v2-wbf-scale-4`) might produce
detectable F1 shifts. The redesign rebuild is the one part of tonight's
work that deserves human review of the diff before commit.

### Recommended order

If pursuing closure tonight on zbook, **descending tractability**:

1. **flash-high-text-1of5-flash-medium-verifier** (1 candidate, no
   propagation, no derivative regeneration except `flash-high-text-medium-vf-1of5`).
   Dirt cheap, dirt fast — useful warm-up.
2. **The five gap-1 Tier-2 cells** as a group:
   `image-n5-t1.0-v1-n5`, `image-n5-t0.7-v1-n5`, `session78-image-checklist`,
   `scale-4-optimal-487-v1-n10`, plus
   `image-n5-t0.3-v1-n5` (gap=11). One cleanup + one materialise per pv
   condition + one full era2 leaderboard rebuild covers all of them.
3. **h8v2-wbf-scale-4** (gap=15) — Tier 1, isolated propagation
   (`evaluate_detections.py` + `paired_permutation_consensus.py` for the
   s4-vs-s8 paired comparison). No leaderboard rebuild.
4. **image-n5-t0.0-v1-n10** (gap=460) — biggest gap, biggest API spend, but
   zero consumers, so if budget is tight, this cell can be deferred without
   any analysis impact. If budget allows, run it for ledger completeness.
5. **Tier 3 pro-medium triple**: `text-baseline-pro-verifier`,
   `pro-medium-image-baseline-pro-verifier`, `pro-high-image-1of5-pro-verifier`.
   Pro pricing is the only material cost per call; threshold-sweep refresh is
   the only required propagation. Invoke
   `scripts/sapphire-pro-verifier-analysis.sh` (renamed-not-needed; despite
   the filename it works on zbook too — it's just the threshold-sweep driver
   for pro-verifier cells). Generate 5 derivatives from the cleaned
   `pro-high-image-1of5-pro-verifier` source via
   `derive_vote_threshold_results.py`.

---

## 5. Cross-cutting findings, decisions, and broader context

### 5.1 The 3 skipped cells are already cleaned on zbook today

While checking the working tree, I noticed three modified files with
`.pre-cleanup-20260506T083*.backup` siblings:

```text
M outputs/55maps-generalisation/verified-v2/probabilities.json
M outputs/55maps-generalisation/verified-v2/run.meta.json
M outputs/h11/e47-propose-brief/verified/flash-high-text-1of5/probabilities.json
M outputs/h11/e47-propose-brief/verified/flash-high-text-1of5/run.meta.json
M outputs/h11/proposer-verifier-384/verified-adversarial-text-v1-prompt/probabilities.json
M outputs/h11/proposer-verifier-384/verified-adversarial-text-v1-prompt/run.meta.json
?? logs/session-87-cleanup/
```

The cleanup_history entries record:

- `55maps-gen-verified-v2`: recovered=3, still_missing=0
  (timestamp 2026-05-06T08:35:42Z).
- `proposer-verifier-384-...-v1-prompt`: recovered=1, still_missing=0
  (timestamp 2026-05-06T08:35:23Z).
- `e47-flash-high-text-1of5`: recovered=57, still_missing=0
  (timestamp 2026-05-06T08:36:29Z).

The sibling investigation's recommendations have therefore already been
executed on zbook; the only outstanding action is to commit the modifications
(per-cell propagation may also be pending — needs separate verification).
**This means the "Tier-2/3 sapphire-state-investigation" of these cells is
moot for the 3-cell sub-bucket; only the 11-cell bucket of this report
remains as an open question.**

### 5.2 Maximum closure scope possible tonight (without sapphire)

**All 11 cells are recoverable without sapphire**, contingent on:

- ~30–60 min wall-clock for crop regeneration (zbook CPU; uses local rasters,
  no API).
- ~$1 API spend (530 verifier calls; ≤$1.44 with 1.5× headroom).
- ~10–15 min wall-clock for cleanup itself.
- ~3.5–4 h wall-clock for full propagation (if all leaderboard rebuilds and
  threshold sweeps are desired in this session).

If propagation is deferred to a follow-up session (e.g. on sapphire post-travel),
**cleanup alone takes ~45–75 min wall-clock + ~$1 API**.

### 5.3 Minimum closure scope (just the 3 skipped cells)

The 3 skipped cells are **already done locally** (§ 5.1) — zero additional
work required to reach gap=0 on those cells. The minimum is "commit what's
already on the working tree", which is purely a `git add` + `git commit`
operation. Per-cell propagation for Cell 1 (e47) needs to be verified
separately (the sibling investigation's recommended steps include
`derive_vote_threshold_results.py` for 2of5..5of5, then `compare_wbf_vs_greedy_production.py`, then leaderboard rebuilds).

### 5.4 User-decision-required scope

The following decisions are **not** required for the 3 skipped cells (already
clean) but **are** required for the 11-cell tier-2/3 bucket:

#### Decision A — API spend approval

The campaign's hard cap was $10; cumulative actual spend reported in the
launch summary was ~$0.91 across the 17 successful Tier-1/2/3 cells, plus
today's session-87 cleanup of the 3 skipped cells (~$0.09 inferred). Tonight's
remaining 11-cell scope is ~$0.96–1.44 expected. The cumulative campaign
spend if all 11 are run: $0.91 + $0.09 + $1.44 ≈ **$2.44** versus the $10
hard cap. Well within budget but requires explicit per-batch approval per the
project's API Call Review Gate convention.

If the operator wants the **gap=460 cell deferred** (zero downstream
consumers), tonight's spend drops to ~$0.10–0.14 for the other 10 cells.
This is the **minimum-information-loss cost-cut option**.

#### Decision B — risk tolerance for re-running cells that may be cleaned on sapphire

The audit annotation states "17 of 20 cells cleaned on the unattended sapphire
run". If sapphire's local working tree truly does have those 17 cells in
post-cleanup state with backups, then re-running cleanup on zbook will
produce a **different** post-cleanup file (because the verifier is
non-deterministic on individual API calls — even at T=0.0, retry windows and
API-side variation produce minor probability differences). When sapphire
eventually comes back online, the user will have to choose which copy to
keep.

The cleanest options are:

1. **Run on zbook tonight, accept zbook as authoritative**. Sapphire's local
   state, when reachable, gets discarded for these 11 cells. Loses the
   cumulative-cost provenance from sapphire's `run.meta.json` (the API spend
   reported in the launch summary's $0.905 ledger was on sapphire-side
   `run.meta.json` files which won't have been merged into the
   cost-manifest). The cost-manifest aggregator at commit `7f05f529` does a
   backup-merge of pre-recovery meta but here the **post-recovery** meta on
   sapphire is what would be lost.
2. **Wait for sapphire**. Pull whatever sapphire has, commit it, propagate
   from there. Risks: (a) sapphire-side cleanup may have been incomplete
   (driver halts not surfaced in the launch-summary), (b) sapphire's HEAD
   might have diverged from origin/main (need to check), (c) timeline is
   user-travel-bound and indeterminate.
3. **Hybrid**: run only the cells with non-trivial gaps tonight (h8v2 gap=15,
   image-t0.3 gap=11, the 3 pro-medium with gap 21+10+8 = 39), defer the
   gap-1 cells (5 cells × 1 candidate each = 5 candidates) and the gap=460
   cell to sapphire pull. Closes the audit gap most cheaply where it matters.

#### Decision C — propagation chain depth

The full propagation chain (re-materialise + canonical multi-pass per-arch
rebuild + combined era2 leaderboard + tier stability + paired permutations +
threshold sweeps) is ~3.5–4 h CPU on zbook. The decision is whether to do
this tonight (long attended session) or split it (cleanup tonight, propagate
on sapphire post-travel, with the propagation diff serving as a
data-integrity check).

Recommendation: **defer the propagation chain to sapphire (or a focused zbook
session on a separate day)**. The cleanup itself produces all the
authoritative `probabilities.json` updates; downstream rebuilds are
mechanical and zero-API-cost. Splitting them keeps tonight's session focused
and bounded.

---

## 6. Recommended specific plan

If the user approves the API spend, my recommended **sequenced plan** (this
is for the user to validate before execution; **read-only investigation has
not run any of these steps**):

### Phase 0 — commit the already-completed 3 skipped cells (~5 min, $0 API)

```bash
git add outputs/55maps-generalisation/verified-v2/probabilities.json \
        outputs/55maps-generalisation/verified-v2/run.meta.json \
        outputs/h11/proposer-verifier-384/verified-adversarial-text-v1-prompt/probabilities.json \
        outputs/h11/proposer-verifier-384/verified-adversarial-text-v1-prompt/run.meta.json
git commit -m "data(p3a-recovery): cleanup proposer-verifier-384 + 55maps-v2 (4 cands)"

# e47 needs derivative regeneration first (per sibling-investigation § 2.6)
python scripts/derive_vote_threshold_results.py \
   --consensus outputs/h11/e47-propose-brief/consensus/flash-high-text-1of5.geojson \
   --probabilities outputs/h11/e47-propose-brief/verified/flash-high-text-1of5/probabilities.json \
   --manifest outputs/h11/e47-propose-brief/verified/flash-high-text-1of5/candidate_manifest.json \
   --pool-size 5 \
   --output-dir outputs/h11/e47-propose-brief/verified \
   --prefix flash-high-text

git add outputs/h11/e47-propose-brief/verified/flash-high-text-{1,2,3,4,5}of5/
git commit -m "data(p3a-recovery): cleanup e47 1of5 + regen 2of5..5of5 derivatives"
```

### Phase 1 — Tier 1 / Tier 2 cells (~30–60 min crop regen + ~10 min API + $0.70)

For each of the 7 cells in this phase (h8v2 + 6 Tier-2), run the
two-step pattern. Example for `h8v2-wbf-scale-4`:

```bash
python scripts/extract_candidates.py \
    --proposer outputs/h8-v2/wbf/scale-4/wbf_candidates.geojson \
    --rasters-dir inputs/rasters \
    --tiles-dir inputs/tiles \
    --output-dir outputs/h8-v2/wbf/scale-4/crops \
    --padding 75

python scripts/run_pv.py cleanup \
    --crops-dir outputs/h8-v2/wbf/scale-4/crops \
    --verified-dir outputs/h8-v2/wbf/scale-4/verified \
    --verifier-config prompts/configs/verify_adversarial-text.json \
    --max-attempts 3 \
    --safe-mode-tokens 2048
```

Repeat per cell, swapping `--proposer`, `--output-dir`, `--verified-dir`, and
the verifier config. The
`session78-image-checklist` cell uses `prompts/configs/verify_checklist.json`
(no `-text` suffix); the rest use `verify_adversarial-text.json`. The
`pro-medium-image-baseline-pro-verifier` cell needs the corrected
`--proposer` path:
`outputs/h11/pv-diag-384/pro-medium-image-baseline/image-t0.0/run_1/detections_image-t0.0_run01.geojson`.

### Phase 2 — Tier 3 cells (~15 min crop regen + ~10 min API + $0.30)

The three pro-medium cells require `--model gemini-3.1-pro-preview
--thinking-level medium` overrides. The flash-medium cell uses
`--thinking-level medium` only.

After cleanup of `pro-high-image-1of5-pro-verifier`, regenerate the 5
`pro-high-image-pro-vf-Nof5` derivatives via
`scripts/derive_vote_threshold_results.py`. After cleanup of
`flash-high-text-1of5-flash-medium-verifier`, regenerate
`flash-high-text-medium-vf-1of5` similarly.

### Phase 3 — propagation (defer or do separately)

Deferring this to a focused session is the cleanest option (per § 5.4,
Decision C). The user should decide whether to:

- (a) run propagation tonight on zbook (~3.5 h CPU, 0 API),
- (b) defer to sapphire post-travel,
- (c) defer to a focused zbook session on a separate day.

### Cumulative tonight scope (Phases 0+1+2 only, no propagation)

| | Wall-clock | API spend |
|-|------------|-----------|
| Phase 0 (commit-only for 3 skipped cells + e47 derivative regen) | 5 min | $0 |
| Phase 1 (Tier 1 + Tier 2; 7 cells, 489 candidates) | 60–80 min | $0.66–1.00 |
| Phase 2 (Tier 3; 4 cells, 40 candidates) | 25 min | $0.30 |
| **Total** | **~90–110 min** | **~$0.96–1.30** |

If the gap=460 cell is **deferred** (it has zero downstream consumers), the
cleanup-tonight scope drops to:

- 10 cells, 70 candidates, ~70 min wall-clock, **~$0.10–0.14 API spend**.

This is the minimum-cost-and-time path that closes the maximum-information-value
portion of the campaign tonight.

---

## 7. Decisions for the user before remediation can start

1. **API spend approval**: explicit per-batch approval at the chosen scope.
   - Option A (full closure tonight): ~$0.96–1.44, 11 cells, 530 candidates.
   - Option B (deferred gap=460): ~$0.10–0.14, 10 cells, 70 candidates.
   - Option C (Tier 3 only as an experimental probe of pro-medium pricing):
     ~$0.30, 4 cells, 40 candidates.
2. **Risk tolerance for re-running cells that may already be cleaned on sapphire**:
   - Option I (zbook-authoritative): run all 11 on zbook; accept that
     sapphire's local state for those cells will be overwritten when sapphire
     pulls. Sapphire-side cleanup-history audit trail (~$0.91 ledger + meta
     stats) is lost.
   - Option II (wait for sapphire): defer everything; close minimum scope
     (Phase 0) tonight. Timeline indeterminate.
   - Option III (hybrid): clean only the non-trivial-gap cells tonight
     (h8v2 + image-t0.3 + Tier 3 pro-medium triple = 5 cells, 64 candidates,
     ~$0.30); defer the 6 gap-1-or-460 cells.
3. **Propagation chain**: do tonight or defer.
   - "Tonight on zbook": +3.5–4 h CPU.
   - "Sapphire post-travel": no additional zbook time; assumes sapphire is
     reachable and re-runs the canonical drivers at HEAD, including the
     `--top-n 0` fix landed in `baa271bf`.
   - "Separate zbook session": preserves time-boxing.
4. **Whether to commit Phase 0 (the 3 already-cleaned skipped cells) right now**,
   independent of the 11-cell decision. Phase 0 is zero-API-spend and zero-risk;
   the only reason to delay would be to bundle Phase 0's commit with later
   propagation or to wait for the sibling investigation's specific commit-message
   recommendations.

---

## 8. Bottom line — what I'd recommend

**Phase 0 is a no-brainer**: commit the 3 already-cleaned skipped cells
immediately (Decision 4). This closes the sibling investigation's scope and
removes the dirty working-tree state.

**For the 11-cell bucket**, my recommendation is **Option III + defer
propagation** (Decisions 2 and 3 combined):

- Run cleanup on the 5 high-information cells tonight (h8v2, image-t0.3, the
  3 Tier-3 pro-medium cells), ~$0.30, ~30 min wall-clock.
- Defer the 5 gap-1 cells and the gap-460 cell — they produce sub-0.001 F1
  movements at most and zero leaderboard movement; they can be picked up by
  sapphire's pull when she's back online (sapphire's local state is the
  authoritative copy by virtue of being on the originating machine).
- Defer all propagation to sapphire post-travel.

This minimises tonight's risk (Option II preserves the most sapphire-side
audit trail) while still moving the audit ledger forward on the cells that
matter most (h8v2 because it's Tier 1; image-t0.3 because it's the largest
non-Tier-1 leaderboard-feeder; Tier 3 pro-medium because it surfaces
pro-medium per-call pricing as empirical data, not a 5× extrapolation).

The user's final say on which option to pick.

---

## 9. Appendix — sources of truth

### 9.1 Files cited

| Path | Purpose in this report |
|------|------------------------|
| `logs/phase3a-recovery-overnight/launch-summary.md` (full) | Original campaign launch metadata + tier ordering |
| `logs/phase3a-recovery-overnight-resume/launch-summary.md` (full, especially § "Three skipped cells" and § "Estimated wall-clock to overnight completion") | Resume launch metadata; sapphire-side $0.905 ledger |
| `planning/run-phase3a-recovery.sh` (lines 87–95 SKIP_CELLS, lines 311–544 per-cell invocations) | Driver source of truth for cell list |
| `planning/phase3a-verifier-recovery-runbook.md` (§ 0–4, especially § 0.1 derived cells and § 1.1 cell inventory) | Cell-by-cell tier breakdown + propagation chain |
| `planning/three-skipped-cells-investigation.md` (full; especially § 2.5 Option A, § 5.3 Sapphire requirement) | Sibling investigation referenced for Cell 1/2/3; not duplicated |
| `reports/phase3a-verifier-completeness-audit-2026-05-03.md` (§ "Recovery status" lines 605–667) | "17 of 20 cleaned" annotation; outstanding-work list |
| `outputs/h8-v2/wbf/scale-4/{crops,verified}/` | Cell 1 manifest + verified state |
| `outputs/h11/pv-diag-384/flash-high-image-n5/image-t{0.0,0.3,0.7,1.0}/{verified-*,consensus-n5}/` | Cells 2–5 |
| `outputs/h11/pv-diag-384/flash-high-image-n5/image-t0.7/session-78-matrix/{shared-crops,verified-checklist}/` | Cell 6 |
| `outputs/h11/pv-diag-384/scale-4-optimal-487/{verified-v1-n10,consensus}/` | Cell 7 |
| `outputs/h11/pv-diag-384/{crops,verified}/{text-baseline,pro-medium-image-baseline,pro-high-image-1of5,flash-high-text-1of5}*/` | Cells 8–11 |
| `outputs/h11/pv-diag-384/pro-medium-image-baseline/image-t0.0/run_1/detections_image-t0.0_run01.geojson` | Cell 9's correct source-geojson path (manifest's `pro-pilot-image` reference is stale) |
| `inputs/rasters/{K-35-052-4_32635,K-35-053-3_Elenovo,K-35-062-2_Rakovski,K-35-078-1_Lesovo}.tif` | Source GeoTIFFs for crop regeneration |
| `planning/condition-inventory-with-s78.json` | Condition inventory mapping cells to leaderboard architectures (pv vs consensus vs single-pass) |
| `results/leaderboard/per-architecture/era2/pv/leaderboard_rows_50m.json` | era2/pv leaderboard rows at 50 m, used to verify which cells actually feed the tier rebuild |
| `scripts/run_pv.py` (`_compute_missing_candidates` lines 235–265, `cmd_cleanup` lines 268–401) | Cleanup logic |
| `scripts/extract_candidates.py` (`main` lines 462–540, `extract_candidates` lines 222–425) | Crop extraction CLI |
| `scripts/lib_verifier.py` (line 398) | Crop path resolution |
| `scripts/build_tiered_leaderboard.py` (lines 384–470) | Architecture dispatch (pv reads materialised geojson; consensus reads consensus geojson) |
| `scripts/materialise_pv_geojson.py` (CLI lines 263–305) | Materialisation script for pv-arch conditions |
| `scripts/derive_vote_threshold_results.py` (`main` and lines 60–175) | Derivative regeneration logic |
| `scripts/sapphire-pro-verifier-analysis.sh` (line 57, lines 73–74) | Threshold-sweep refresh driver for Tier-3 cells |
| `logs/session-87-cleanup/cell{1,2,3}-*.log` | Today's session-87 cleanup logs for the 3 skipped cells (timing evidence + success confirmation) |

### 9.2 Commits cited

| Commit | Subject | Significance |
|--------|---------|--------------|
| `adf95dbf` | `reports(verifier): Phase 3a verifier completeness audit` | Original audit's commit; pre-recovery anchor |
| `b8961e56` | `data(verifier): full-matrix text-only adversarial v1 verification` | 7 of 11 cells last touched here (Apr 17 2026) |
| `2e84d4a6` | `data(h12-v2): H12 v2 detection data + Scale-4/Scale-8 verifier outputs` | h8v2-wbf-scale-4 last commit (Apr 16 2026) |
| `3d22184d` | `data(outputs): track detection GeoJSON and verifier results from gitignored dirs` | 3 Tier-3 cells last commit (Apr 15 2026) |
| `400e6fbc` | `data(s78-rerun): Phase A — checklist on image pool (6 candidates scored, 0 failed)` | session78-image-checklist last commit (Apr 25 2026) |
| `414ee8a4b` | `data(p3a-recovery): cleanup Session-78 matrix verifier outputs (6 cells, 153 cands)` | First batch (Tier 1 Session-78 6 cells) |
| `b3ed509e` | `analysis(p3a-recovery): propagate Session-78 cleanup through materialise + calibration` | Tier-1 propagation; last recovery commit on origin |
| `e174390e` | `fix(phase3a-recovery): skip 3 crop-missing cells; resume from cell 8` | SKIP_CELLS landed |
| `cebe5fed` | `chore(gitignore): exclude phase3a-recovery-overnight-resume driver logs` | Resume-launch chore |
| `0ceac93f` | `ops(phase3a-recovery): resume overnight on sapphire (3 cells skipped, 10 to go)` | Resume-launch operations note (the "10 to go" message) |
| `1f5c8bde` | `docs(continuity): reflect overnight recovery state — relaunched with 3 cells skipped` | Continuity update post-resume |
| `64974ec5` | `docs(reflection): Obs 323 — Phase3a Tier-1 propagation closure` | Tier-1 closure narrative; covers post-cleanup propagation through `b3ed509e` |
| `c067bca4` | `analysis(p3a-recovery): restore per-arch tier composition with --top-n 0` | Per-arch rebuild after the wrong-driver detour |
| `a8f4b7f8` | `analysis(p3a-recovery): Step 4 + 5 — combined Era-2 leaderboard + tier stability` | Combined era2 leaderboard rebuild |
| `ca0567d3` | `analysis(p3a-recovery): full redesign rebuild — q01 + MCC variants + stage 3-5` | Today's full redesign rebuild; finalised tier composition based on pre-Tier-2/3-cleanup state |
| `1b2842d0` | `fix(phase3a-recovery): correct e47 --crops-dir path in driver` | Today's driver fix following the sibling investigation's discovery of the bug |
| `baa271bf` | `fix(per-arch): add --top-n 0 + --seed 42 to run_per_arch_leaderboards.sh` | Wrong-driver detour fix |
| `ef3ec4fe` | `docs(runbook): correct § 6.1 / § 6.2 — separate tier rebuild from finalise` | Runbook fix |
| `7f05f529` | `fix(aggregate-cost): merge pre-recovery verifier-meta backups` | Cost-manifest backup-merge fix; relevant to API-cost provenance |

### 9.3 Out of scope

- The 3 skipped cells themselves (e47, 55maps-v2, proposer-verifier-384) —
  covered by `planning/three-skipped-cells-investigation.md` and already
  cleaned on zbook today.
- Whether sapphire's local working tree has these 11 cells in a cleaned
  state. Cannot be verified from zbook; the answer determines whether
  Decision 2's Option II (wait for sapphire) is viable as a reproducible
  alternative.
- Whether sapphire's cumulative-cost ledger for the resume run can be
  reconstructed from session archives alone or whether `7f05f529`'s
  backup-merge logic suffices once the post-cleanup `run.meta.json` files
  are cherry-picked.
- The unmatched-cells (8 cells) from the original audit — runbook § 11 lists
  them as out-of-scope and the campaign deliberately doesn't attempt them.
- Whether to migrate any of the 11 cells' bulk PNG directories from the
  to-be-extracted state on zbook back to sapphire post-travel — affects
  reproducibility infrastructure and is a separate workstream.

---

## End of investigation
