# SUPERSEDED 2026-04-24

**Reason**: Session closed; findings consolidated into Obs 228-232.

**See**: `docs/notes/reflections/working-notes.md` Observations 228-232 (WBF variant study, consensus-dedup, superseded-pairwise archival)

This document is preserved for audit / historical reference. Its original content follows below.

---

## WBF Investigation — Session Continuity Document

**Date**: 2026-04-13
**Session scope**: Obs 228 dedup audit → Decision 26 WBF adoption → Obs 230–232 WBF validation and buffer-sensitivity findings → critical correction on canonical pipeline
**Session cost**: ~$21 API (hp4hn4 ~$5, e47-propose-brief v1+v2 ~$16)
**Next session start task**: Priority 1 below (canonical WBF on `gold-standard-v2/detect_brief-text`)

---

## 1. State at Session End

**Weighted Boxes Fusion (WBF, Solovyev et al. 2019)** has been implemented, tested, and validated against two pipeline variants, with mixed results that depend on the specific proposer configuration. Decision 26 committed to retaining greedy-ball clustering as primary with WBF as a robustness check, but the Obs 231 production-run finding (WBF > greedy by +0.08 F1) was later discovered to have been run against a non-canonical one-off experiment rather than the actual paper pipeline. The corrected comparison is queued as Priority 1 for next session.

**Documentation state**:

- **Decision 26** written (`docs/methodology/preregistration/decisions-log.md`): retain greedy as primary, adopt WBF as robustness check, note WBF as recommended for future work. Framing is consistent with the hp4hn4 statistical tie but is now in tension with Obs 231/232 findings; **revision pending after Priority 1 canonical test completes**.
- **Obs 228** (`docs/notes/reflections/working-notes.md`): full audit of the upstream consensus dedup radius problem, final resolution pointing to WBF as the adopted method with the root-cause analysis (drift distribution, cartographic floor, cemetery over-merging failure mode caught by visual check).
- **Obs 229**: edge-artefact finding (row of FPs along tile boundaries / linear cartographic features). Deferred investigation; not blocking.
- **Obs 230**: hp4hn4 statistical equivalence (WBF ≈ greedy, p = 0.60, matching CIs).
- **Obs 231**: production-run WBF finding (WBF >> greedy, +0.08 F1, p < 0.0001). **Contains a correction note at the top** flagging that the comparison was run on the wrong baseline (non-canonical `propose_brief-text` one-off, not the canonical `detect_brief-text` production pipeline). See §6 below for the correction details.
- **Obs 232**: buffer-sensitivity finding (leaderboard rankings depend on buffer choice; image-track configs gain ranks at wider buffers due to larger centroid drift; text-track saturates at 30 m; need to run round-robin at ≥3 buffers).

**Implementation state**:

- `scripts/lib_fusion.py` — WBF library (canonical Solovyev 2019 for axis-aligned polygon boxes)
- `tests/test_lib_fusion.py` — 33 tier-1 tests covering IoU, size filter, WBF clustering, vote-aware min-separation, end-to-end pipeline
- `scripts/fuse_detections_wbf.py` — end-to-end runner with special-config support
- `scripts/sweep_f1_wbf.py` — F1 sweep script (single config, single buffer)
- `scripts/compare_wbf_vs_greedy.py` — bootstrap CI + paired permutation comparison for H10
- `scripts/compare_wbf_vs_greedy_production.py` — full (vote × prob × buffer) sweep comparison for production
- `scripts/diagnose_consensus_dedup_radius.py` — Obs 228 magnitude diagnostic
- `scripts/export_dedup_visual_check.py` — QGIS layer exporter for multi-GT visual review
- `scripts/export_wbf_visual_check.py` — QGIS layer exporter for WBF variant comparison
- `scripts/probe_verifier_independence.py` — Obs 227 follow-up probe (paused)
- `tests/test_probe_verifier_independence.py` — tests for the verifier independence probe

**Result artefacts**:

- `results/h10/consensus_dedup_magnitude_diagnostic.json` — Obs 228 magnitude diagnostic numbers
- `results/h10/verifier_independence_probe.{json,md}` — Obs 227 probe output
- `results/h10/wbf/sweep_results_pool_160_hp4hn4_variant_c.json` — hp4hn4 Variant C F1 sweep
- `results/h10/wbf/variant_c_vs_greedy_hp4hn4.json` — hp4hn4 WBF vs greedy comparison
- `results/h11/wbf/production_vs_greedy_summary.json` — e47-propose-brief full sweep + CIs + permutation tests (on non-canonical baseline — see correction)

**Output artefacts**:

- `outputs/h10/wbf/pool_160_hp4hn4_{variant_c,voteaware_v6,voteaware_v5,voteaware_v3,voteaware,no_minsep}/` — WBF output for hp4hn4 variants
- `outputs/h11/wbf/e47-propose-brief-n5/` — WBF output + extracted crops + v1 + v2 verifier probabilities for the propose_brief-text one-off (non-canonical)
- `outputs/qgis-dedup-check/` — Obs 228 visual review layers
- `outputs/qgis-wbf-check/` — WBF variant visual review layers

**Memory files**:

- `~/.claude/projects/-home-shawn-Code-map-reader-llm/memory/project_wbf_decision.md` — Decision 26 summary as durable memory
- `~/.claude/projects/-home-shawn-Code-map-reader-llm/memory/MEMORY.md` — entry pointing to the above
- `~/personal-assistant/data/scratchpad.md` — two new constraint entries: "Read metadata, don't trust directory names" and "Flag directory cleanup and missing READMEs proactively"

---

## 2. Key Findings (Chronological)

### 2.1 Obs 228 — The dedup radius audit

**Problem**: The upstream consensus pipeline (`lib_consensus.py`) uses greedy-ball clustering at a 20 m centroid-distance radius. On the H10/H12 test set, this produced ~49 duplicate candidates per config where a single physical mound had multiple distinct cluster IDs.

**Investigation path**:

1. **Initial hypothesis** — "just raise the radius". Proposed 50 m.
2. **Shawn's pushback** — cartographic constraint: mound symbols are ~75 m in diameter and never overlap, so centroids should be ≥75 m apart. Manual measurement confirmed ~70 m minimum.
3. **Empirical check** — min GT–GT distance is 68.1 m, p1 = 72 m; only 5 GT pairs within 75 m across all 569 mounds. Shawn's claim verified to within 7 m.
4. **Geometric refinement** — Shawn argued R < 35 m is needed to guarantee separation. Drift distribution check confirmed: candidate-to-GT drift p50 = 7 m, p90 = 23 m, p99 = 37 m. A 30 m radius captures most drift while staying below the cartographic floor.
5. **Visual failure mode** — Shawn's QGIS check of a 6-mound cemetery showed that a plain 60 m min-separation post-step **lost a real mound** to over-merging, even though the aggregate multi-GT metric reported zero failures. Vote-aware min-separation at 30 m with anchor ≥ vote_t fixed the cemetery case.

**Resolution**: WBF Variant C parameters finalised:

- IoU threshold: 0.25 (captures drift up to ~45 m centroid offset for 75 m boxes)
- Min-separation: 30 m, vote-aware with anchor ≥ 6 (for 10-pass) or ≥ 4 (for 5-pass)
- Box size filter: 20 m ≤ width, height ≤ 200 m; 400 ≤ area ≤ 40,000 m²

### 2.2 Obs 230 — hp4hn4 statistical equivalence

On H10/H12 `pool_160_hp4hn4` (`detect_brief-text`, minimal thinking, T=0.0, 10 passes):

- Greedy F1 = 0.8853 (vote = 6, prob = 0.15, 20 m buffer)
- WBF F1 = 0.8800 (vote = 7, prob = 0.15)
- ΔF1 = −0.0053
- **Paired permutation test p = 0.6019** (two-sided, 10,000 iter)
- Bootstrap 95 % CIs overlap ~97 % (greedy [0.8483, 0.9165], WBF [0.8452, 0.9108])
- Tile-level wins: 11 greedy, 11 WBF, 305 ties (exact symmetric split)

Interpretation: **statistical tie**. Decision 26 written on this basis: retain greedy as primary, adopt WBF as validated robustness check.

### 2.3 Obs 231 — e47-propose-brief production-run WBF result (⚠️ non-canonical)

On `outputs/h11/e47-propose-brief/flash-high-text-n5/propose_brief-text/run_{1..5}/` with HIGH thinking, T=0.7, 5 passes, loose 1-of-5 consensus, minimal v1 and v2 verifiers:

- Greedy v1 optimum F1 = 0.8086 at 50 m; WBF v1 = 0.9054 (Δ = +0.097, p < 0.0001)
- Greedy v2 optimum F1 = 0.8273 at 50 m; WBF v2 = 0.9108 (Δ = +0.084, p < 0.0001)
- Non-overlapping bootstrap CIs at every buffer
- Tile-level wins: 25–29 greedy vs 61–72 WBF (2.3–2.9× WBF advantage)
- WBF improvement is **precision-driven** (+0.14 to +0.34 per map) with essentially flat recall
- Universal across all 4 maps (+0.06 to +0.20 F1 per map)

**⚠️ CORRECTION**: this test was run against `propose_brief-text`, which is a **7-file one-off experiment**, not the canonical production pipeline. The canonical pipeline uses `detect_brief-text` (53+ files, including the 55-map generalisation). The +0.08 finding applies specifically to the loose-consensus propose_brief-text variant and has **not** been validated on the canonical detect_brief-text 4-of-5 pipeline. See §6.

### 2.4 Obs 232 — Buffer-sensitivity of leaderboard rankings

Analysis of existing `results/paper-eval/pv/*/buffer_sensitivity.json` (8 configs at buffers {20, 30, 40, 50} m) and `results/pairwise/leaderboard-{20,30}m/` (pre-existing pairwise comparisons):

- **20 m → 30 m**: 2 rank flips
- **30 m → 40 m**: 3 rank flips (image-track gains further)
- **40 m → 50 m**: 0 rank flips (ranking stable beyond 40 m)

**Flash HIGH image 3-of-5** climbs rank 7 at 20 m → rank 6 at 30 m → **rank 4 at 40 m/50 m**. 3-rank gain across the full buffer sweep. Pattern is **one-directional**: every flip is image-track gaining at wider buffers.

**Mechanism hypothesis**: image-track proposers have larger centroid drift (~40 m tail vs ~20 m for text-track), matching half the 75 m mound symbol diameter. Image-track may be "fixating" on a salient feature of the mound symbol rather than its centre. Text-track saturates at 30 m (no F1 improvement beyond); image-track keeps climbing to 40 m.

**Implication for round-robin**: must run at **{20 m, 30 m, 40 m}** minimum. Text-track top-3 is stable across buffers (Flash HIGH text 16-of-30 + min-vf at F1 ≈ 0.90); image-track rankings require 40 m to reflect true ceiling. Cross-track comparisons are fundamentally buffer-dependent.

**Implication for WBF**: WBF's IoU threshold captures drift up to ~45 m, which matches the image-track drift tail. **Prediction**: WBF's advantage over greedy should be **larger on image-track than on text-track**. Not yet tested.

---

## 3. Critical Correction — Non-Canonical Baseline

**Discovered near the end of the session**. The user asked whether we'd been using `detect_brief-text` consistently; investigation revealed:

| Proposer version | File count on disk | Where |
|---|---|---|
| **`detect_brief-text`** | **53 files** | Many directories — canonical |
| `propose_brief-text` | 7 files | `e47-propose-brief/` only — one-off |
| `propose_brief` | 1 file | `propose-brief-v1-test/` — one-off |
| `propose_brief_v2` | 2 files | `v2-proposer-test{,-BAD-TILESIZE}/` — failed experiments |
| `library_plus-hp` | 10 files | `n1-outstanding-384/` — unrelated |

**My WBF production test (Obs 231) used `propose_brief-text`, not `detect_brief-text`.** The +0.08 F1 finding applies to the loose-consensus propose_brief-text one-off, not the canonical pipeline.

**The canonical production pipeline is** `outputs/h11/gold-standard-v2/proposer/detect_brief-text/run_{1..5}/`:

- version: `detect_brief-text`
- thinking: `high`
- temperature: `0.7`
- library_hash: `8580ecb2258b64a0fdbc` **(same as 55-map generalisation)**
- K = 5
- consensus: 4-of-5 (strict)
- existing greedy verifier output at `verified-v1/probabilities.json` (597 results) and `verified-v2/probabilities.json` (607 results)

**Note on "gold-standard-v2" naming**: the "v2" in the directory name refers to the recreation script version (`scripts/11maps-gold-standard-v2.sh` is the second iteration), **not** the proposer version. The proposer inside is plain `detect_brief-text`.

**Obs 231 has a correction note appended at the top** flagging this. Decision 26 is in tension with both Obs 231/232 and the canonical-baseline question, and should be amended or superseded by Decision 27 after Priority 1 completes.

---

## 4. "Why not medium-thinking verifier everywhere?"

The F1 = 0.885 headline is historically associated with `flash-high-text-4-of-5 + flash-medium-vf`, but the paper-eval leaderboard shows this is actually the **third-best result**, not the best:

| Config | F1 at 30 m |
|---|---|
| flash-high-text 16-of-30 + min-vf | **0.9044** (rank 1) |
| flash-high-text 4-of-5 + min-vf | **0.8908** (rank 2) |
| flash-high-text 4-of-5 + medium-vf | 0.8850 (rank 3) |

Minimal-thinking verifier at the same 4-of-5 consensus beats medium-thinking verifier by +0.006 F1 **and** is cheaper per call (no thinking token overhead). The "F1 = 0.885 medium-vf" headline is likely an early/preregistered result that was later surpassed by minimal-vf in the leaderboard but stuck around as the remembered number.

**Implication for Priority 2**: the sapphire medium-vf comparison was originally Priority 2 but has been **downgraded** because medium-vf is not actually the paper's best-performing config. It's now a historical footnote, not a headline validator.

---

## 5. Priorities for Next Session

### Priority 1 — Canonical WBF vs greedy on `gold-standard-v2/detect_brief-text` ⭐ FIRST TASK

**Goal**: Validate WBF vs greedy on the actual paper pipeline (detect_brief-text + 4-of-5 + min-vf).

**Data reuse**:

- Raw proposer: `outputs/h11/gold-standard-v2/proposer/detect_brief-text/run_{1..5}/` (7,561 raw boxes, 4 maps) — local
- Greedy v1 baseline: `outputs/h11/gold-standard-v2/verified-v1/probabilities.json` (597 candidates) — local, **reuse, no API**
- Greedy v2 baseline: `outputs/h11/gold-standard-v2/verified-v2/probabilities.json` (607 candidates) — local, **reuse, no API**
- Canonical consensus file: `outputs/h11/gold-standard-v2/consensus/consensus-4of5.geojson`

**Steps**:

1. Add `gold-standard-v2-detect` entry to `SPECIAL_CONFIGS` in `fuse_detections_wbf.py` (point at the 5 raw detection paths; filenames use `detections-detect_brief-text-3-flash-2026-04-10.geojson` pattern)
2. Run WBF with `--anchor-vote-threshold 4` (matches canonical 4-of-5 consensus optimum for 5-pass pipeline)
3. Filter WBF output to vote ≥ 2 (matches downstream minimum)
4. Extract verifier crops (no API)
5. Run v1 + v2 verifier in **Flex** mode — estimated ~1,000–1,600 calls × 2 = **~$6–10** API (gate with user before launching)
6. Adapt `compare_wbf_vs_greedy_production.py` to point at the new paths (edit `GREEDY_MANIFEST`, `GREEDY_PROBS_V1`, `GREEDY_PROBS_V2`, `WBF_MANIFEST`, `WBF_PROBS_V1`, `WBF_PROBS_V2` constants); full sweep at buffers {20, 25, 30, 40, 50} m
7. Bootstrap CIs and paired permutation tests
8. Write **Obs 233** with the corrected canonical result, cross-reference from Obs 231 correction note

**Prediction** (likely outcome): WBF vs greedy ΔF1 is smaller on canonical detect_brief-text than on the propose_brief-text one-off — possibly in the +0.01 to +0.03 range, possibly a statistical tie like hp4hn4. The +0.08 production finding was on a pipeline that was already far from ceiling; the canonical pipeline is much closer to ceiling, so WBF has less room to improve.

### Priority 2 — Sapphire data inventory + medium-vf comparison (⬇ downgraded)

**Why downgraded**: medium-vf is no longer expected to be the best verifier (see §4). This is now a historical-headline validation, not a core result.

**Sapphire tasks** (when home network access is available, 2026-04-14+):

1. `ls -la outputs/h11/pv-diag-384/ --recursive` or equivalent to inventory what's actually on sapphire vs local assumptions
2. If medium-vf probabilities are accessible, copy `outputs/h11/pv-diag-384/verified/flash-high-text-medium-vf-4of5/candidate_manifest.json` + `probabilities.json` back to local
3. Run WBF vs greedy comparison against the medium-vf greedy baseline — cheap if the data is just copied back (no re-verification needed)
4. Determines whether WBF matches, exceeds, or converges with the medium-vf historical headline

### Priority 3 — Image-track WBF validation

**Goal**: Determine whether WBF's advantage extends to image-track configs (currently zero image-track WBF data).

**Candidate target**: `flash-high-image-3-of-5 + flash-min-vf` — the config that climbs 3 ranks across the buffer sweep in Obs 232, likely has the most drift for WBF to recover.

**Steps**:

1. Find local raw image-track proposer data (TBD which directory — search for image-track K=5 runs)
2. Run WBF with appropriate anchor vote threshold
3. Compare to existing greedy image-track verifier output
4. Prediction: WBF ΔF1 ≥ +0.08 (larger than text-track because image-track has more drift)

**Estimated cost**: ~$5–10 Flex (single-config replication).

### Priority 4 — 55-map generalisation WBF 5-map subset

**Goal**: Validate whether WBF advantage transfers to the student-GT 55-map corpus before committing to a full (~$200) rollout.

**Approach**:

1. Pick 5 random maps from the 55-map set
2. Run WBF on the existing raw proposer data at `outputs/55maps-generalisation/proposer/detect_brief-text/run_{1..5}/` (HIGH, T=0.7, K=5, library 8580ecb2... — same as canonical production)
3. Extract crops for WBF candidates on those 5 maps only
4. Run v1 + v2 verifier on the subset
5. Compare to the existing 55-map greedy baseline restricted to the same 5 maps
6. Decision criterion: if Δ ≥ +0.04 F1 on the subset, approve full 55-map rollout; if < +0.04, accept greedy as the generalisation-run method

**Estimated cost**: ~$18 Flex.

### Priority 5 — Round-robin pairwise permutation tests (text, image, combined top-20)

**Goal**: Rank existing production-run configurations at multiple buffers; pick the "optimum" for each track for the generalisation run carryforward.

**Buffers to run**: {20 m, 30 m, 40 m} per Obs 232 (50 m is redundant with 40 m).

**Three round-robins**:

- **Text-track top-20** — use existing `results/pairwise/leaderboard-{20,30}m/` data, add 40 m
- **Image-track top-20** — new round-robin
- **Combined text+image top-20** — new round-robin, report per-buffer

**Pre-analysis decisions needed**:

1. Buffer selection rule per track:
   - Text-track primary: 30 m (saturates here)
   - Image-track primary: 40 m (climbs until here)
   - Combined primary: 30 m with 20 m and 40 m as sensitivity checks
2. Tie-break rule within top-3: highest F1 → highest recall → lowest n_candidates
3. Whether to include WBF variants in the round-robin or keep it greedy-only (for preregistration consistency)

### Priority 6 — Generalisation run carryforward (depends on Priorities 1–5)

**Goal**: Run the selected optimum text-track and image-track configs on the 55-map generalisation set.

- **Text-track carryforward**: use selected optimum from Priority 5 + v2 + WBF (if Priority 4 confirms transfer)
- **Image-track carryforward**: use selected optimum from Priority 5, verifier choice depends on Priorities 2 + 3
- **Manual corrections**: use `scripts/review_candidates.py` on highest-value candidates from the final generalisation output

**Use caching + Flex** to reduce costs. Reuse existing 55-map raw proposer data (no proposer re-spend needed).

### Priority 7 — Documentation and paper work (ongoing)

- **Decision 26 amendment** (or Decision 27 addition) — reflect WBF findings after Priorities 1 and 2 complete
- **Obs 233** — canonical WBF test write-up (after Priority 1)
- **Obs 234+** — additional findings as they emerge
- **Paper methods section draft** — include buffer-sensitivity note (Obs 232), aggregation-vs-proposer interaction, reviewer defence for method selection
- **Centroid offset diagnostic** (Obs 232 mechanism confirmation): per-map mean offset vector from image-track candidates to GT; compare to text-track. Cheap, no API, paper-worthy.

---

## 6. Data Locations Reference

**Local (this workstation)**:

| Path | Purpose | Status |
|---|---|---|
| `outputs/h10/evaluation/pool_*/run_*/` | H10/H12 raw proposer (5 configs × 10 passes) | untracked, large |
| `outputs/h10/verifier-crops/pool_*/` | H10/H12 greedy candidate manifests | tracked (earlier commit) |
| `outputs/h10/verified/pool_*/` | H10/H12 greedy verifier probabilities | tracked (earlier commit) |
| `outputs/h10/wbf/pool_160_hp4hn4_*/` | hp4hn4 WBF outputs | untracked, will commit |
| `outputs/h11/e47-propose-brief/proposer/detect_brief-text-*` | 4-map single-pass detect_brief-text (older) | tracked |
| `outputs/h11/e47-propose-brief/flash-high-text-n5/propose_brief-text/run_*/` | **Non-canonical propose_brief-text one-off (DO NOT confuse with canonical)** | tracked |
| `outputs/h11/gold-standard-v2/proposer/detect_brief-text/run_{1..5}/` | **Canonical 4-map production raw proposer (next session's Priority 1 data)** | tracked |
| `outputs/h11/gold-standard-v2/crops/candidate_manifest.json` | Canonical 4-of-5 consensus greedy manifest (607 candidates) | tracked |
| `outputs/h11/gold-standard-v2/verified-v1/probabilities.json` | **Canonical greedy v1 baseline** (reuse for Priority 1) | tracked |
| `outputs/h11/gold-standard-v2/verified-v2/probabilities.json` | **Canonical greedy v2 baseline** (reuse for Priority 1) | tracked |
| `outputs/h11/wbf/e47-propose-brief-n5/` | WBF outputs from Obs 231 (non-canonical) | untracked, will commit |
| `outputs/55maps-generalisation/proposer/detect_brief-text/run_{1..5}/` | 55-map generalisation raw proposer (K=5) | tracked |
| `outputs/55maps-generalisation/verified{,-v2}/probabilities.json` | 55-map greedy v1 and v2 probabilities | tracked |

**Sapphire-only (not on this workstation)**:

- `outputs/h11/pv-diag-384/verified/flash-high-text-medium-vf-4of5/{candidate_manifest,probabilities}.json` — medium-vf historical headline data (gitignored, not committed, only exists on sapphire)
- Likely also other pv-diag sweep variants (minimal-vf, different verifier prompts, different consensus thresholds) — inventory on sapphire next session to confirm
- The `pv-diag-384` gitignore policy has since been updated to permit committing lightweight artefacts, but historical data remains sapphire-only

---

## 7. Key Numbers to Remember

**Cartographic constants**:

- Mound symbol diameter: ~75 m (15 px × 5 m/px)
- Minimum inter-mound distance in GT corpus: **68.1 m** (p1 = 72 m, only 5 pairs within 75 m)
- Tile size: 384 px × 5 m = 1920 m; tile stride 336 px with 48 px overlap → 240 m geographic tile overlap

**Drift distribution** (candidate-to-GT offset, attribution-safe at 40 m):

- p50: 7 m
- p90: 23 m
- p99: 37 m

**Pipeline configurations**:

- 4-map production canonical: `detect_brief-text`, HIGH, T=0.7, K=5, 4-of-5 consensus, lib `8580ecb2258b64a0fdbc`
- 55-map generalisation: same config as above, different map set (55 vs 4)
- H10/H12: `detect_brief-text`, minimal, T=0.0, K=10, vote threshold swept in F1 analysis, lib depends on pool
- e47-propose-brief (non-canonical one-off): `propose_brief-text`, HIGH, T=0.7, K=5, **1-of-5** consensus (loose)

**Published F1 headlines** (all from `results/paper-eval/pv/*/buffer_sensitivity.json`):

- `flash-high-text 16-of-30 + min-vf`: **F1 = 0.9044** at 30 m+ (true leaderboard #1)
- `flash-high-text 4-of-5 + min-vf`: F1 = 0.8908 at 30 m+ (rank 2, cheapest)
- `flash-high-text 4-of-5 + medium-vf`: F1 = 0.8850 at 30 m+ (historical "0.885" headline)
- `flash-high-image 3-of-5 + min-vf`: F1 = 0.8771 at 50 m (rank 4 at 40 m+, rank 7 at 20 m — biggest buffer-mobility)

**WBF Variant C parameters (final)**:

- IoU threshold: 0.25
- Min-separation: 30 m, vote-aware
- Anchor vote threshold: 6 (for 10-pass) / 4 (for 5-pass) = matches F1-sweep optimal vote_t
- Box size filter: width × height ∈ [20, 200] m each; area ∈ [400, 40000] m²

---

## 8. Critical Warnings for Next Session

1. **⚠️ Don't trust directory names — read metadata first.** Examples:
   - `e47-propose-brief/` holds a non-canonical `propose_brief-text` one-off (7 files)
   - `gold-standard-v2/` contains the canonical `detect_brief-text` proposer ("v2" is the script version)
   - `v2-proposer-test{,-BAD-TILESIZE}/` holds the actual `propose_brief_v2` proposer (failed experiments — do not use)
   - `pv-diag-384/` is sapphire-only but is referenced from local `results/` paths
   - `proposer-verifier-384/` holds a **single-pass** detect_brief-text run, not a 5-pass production run
   Always verify via `meta.json`: `version`, `thinking_level`, `temperature`, `library_hash`.

2. **⚠️ Obs 231 is on a non-canonical baseline.** The +0.08 F1 finding applies only to the propose_brief-text one-off. The canonical detect_brief-text WBF test is Priority 1 for next session.

3. **⚠️ Medium-vf is not the paper's best config.** The F1 = 0.885 headline is historically associated with medium-vf but is actually **third** in the leaderboard behind two minimal-vf variants. Don't default to medium-vf as the target; default to minimal-vf.

4. **⚠️ Rankings are buffer-dependent.** Run round-robin at ≥3 buffers (20 m, 30 m, 40 m). Image-track climbs ranks at wider buffers; text-track saturates at 30 m.

5. **⚠️ The 55-map generalisation is a protocol deviation (E47).** It uses `detect_brief-text` (unchanged from production); the E47 errata notes this was an accidental substitution that turned out to work better than the preregistered `propose_brief`. Document this in the paper methods section.

---

## 9. Pending Decisions

1. **Priority 1 launch** — approve WBF canonical test (~$6–10 API)?
2. **Decision 26 revision** — amend in place, add Decision 27, or no change until Priority 1 completes?
3. **Priority 3 scope** — run image-track WBF validation on one config (~$5–10)?
4. **Priority 4 scope** — run 5-map subset 55-map check (~$18)?
5. **Round-robin primary buffer per track** — confirm Text=30, Image=40, Combined=30?
6. **Paper narrative** — report WBF as "robustness check" (Decision 26 as written) or as "primary method for HIGH/T=0.7 pipelines" (if Priority 1 confirms)?

---

## 10. Session Artefacts to Commit

See separate commit batches (to be made immediately after this document):

- **Commit 1** — WBF fusion library + tests
- **Commit 2** — WBF runner and analysis scripts
- **Commit 3** — Obs 228 investigation scripts (dedup audit)
- **Commit 4** — Obs 228–232 working notes, Decision 26, this continuity doc
- **Commit 5** — hp4hn4 and production results JSON artefacts
- **Commit 6** — Visual export layers and WBF output manifests
- **Commit 7** — Probe scripts and tests (Obs 227 follow-up, paused)

---

*End of continuity document. Start next session by reading this file, then launch Priority 1.*
