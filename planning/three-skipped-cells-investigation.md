# Three skipped cells — investigation and remediation plan

**Author**: Claude Opus 4.7 (1M context), invoked by parent session 2026-05-04
**Status**: read-only investigation. No tracked files modified; no API calls;
no working-tree edits.
**Compute location**: zbook (sapphire off-network during user travel).
**Sources of truth**: see § 6 "Appendix" for every cited file and commit.

---

## 1. TL;DR — one paragraph per cell

### Cell 1 — `e47-flash-high-text-1of5` (Tier 1, gap 57)

**The original "missing crops" diagnosis is wrong on zbook.** The 4,358 crop
PNGs are physically present at
`outputs/h11/e47-propose-brief/crops/flash-high-text-1of5/crops/`. The cell
was skipped on sapphire because **the bulk crop directory is gitignored and
was never pushed to that machine**, AND because **the recovery driver was
invoked with `--crops-dir` pointing at the verified directory** (which has no
PNGs), not at the canonical crops directory. So zbook can run the cleanup
locally with no crop regeneration, but the driver path argument is buggy and
needs a one-line fix before re-running. The "schema-transformation" surprise
is real but **resolved**: the file in `HEAD` is already in derived schema
(self-referential `source`, `derived_from: 1-of-5 union`); cleanup will
rewrite to canonical schema, which is **safe** for every downstream consumer
because they all only read the `results` dict and ignore the schema
metadata. **Recommended action**: run cleanup with the corrected
`--crops-dir`, then `derive_vote_threshold_results.py` to refresh
2of5..5of5, then propagate. **Cost**: ~$0.08 (57 cleanup calls at
~$0.0014 each), ~5 min wall-clock plus ~30 min CPU propagation.

### Cell 2 — `55maps-gen-verified-v2` (Tier 2, gap 3)

Crops present locally on zbook at `outputs/55maps-generalisation/crops/crops/`
(8,942 PNGs match expected `total_detections`). The cell's
`probabilities.json` is in clean canonical schema with no prior cleanup
history. The driver path arguments for this cell **are correct**; the cell
was skipped only because sapphire was missing the gitignored crops at
campaign time. **Recommended action**: run cleanup unmodified, then refresh
the v2 threshold sweep at 50 m. **Cost**: ~$0.005 (3 calls); under one
minute of cleanup plus ~5 min of sweep refresh.

### Cell 3 — `proposer-verifier-384-adversarial-text-v1-prompt` (Tier 3, gap 1)

Same shape as Cell 2: 572 crops present at
`outputs/h11/proposer-verifier-384/candidates/crops/`, canonical schema, no
known downstream consumers (audit confirms "no current script or analysis
output references this cell"; cleanup is for ledger completeness only).
Driver paths correct. **Recommended action**: run cleanup unmodified, no
propagation needed. **Cost**: ~$0.0014 (1 call), seconds.

**Total to close all three**: ~$0.09 in API spend, well under the campaign's
remaining cap; ~30–40 min of wall-clock time. **Sapphire is not required**
— everything can be done on zbook tonight or whenever the user resumes.

---

## 2. Cell 1 — `e47-flash-high-text-1of5`

### 2.1 Current state on disk (verified 2026-05-04 on zbook)

| File | Status |
|---|---|
| `outputs/h11/e47-propose-brief/verified/flash-high-text-1of5/probabilities.json` | tracked, 3.2 MB, 4,301 results, **derived schema** |
| `outputs/h11/e47-propose-brief/verified/flash-high-text-1of5/candidate_manifest.json` | tracked, 1.7 MB, 4,358 candidates, derived-by-vt=1 |
| `outputs/h11/e47-propose-brief/verified/flash-high-text-1of5/run.meta.json` | tracked, canonical original-run stats (success=4301, error=1147, cost=$5.89, 8.39 M tokens) |
| `outputs/h11/e47-propose-brief/crops/flash-high-text-1of5/candidate_manifest.json` | gitignored (under `crops/`), full 4,358 candidate manifest, **NO `derived_from` / `vote_threshold` keys** — this is the canonical source manifest |
| `outputs/h11/e47-propose-brief/crops/flash-high-text-1of5/crops/candidate_*.png` | gitignored, **4,358 PNGs present on zbook**; first = `candidate_00000.png`, last = `candidate_04357.png` |
| Pre-cleanup `.backup` | absent (already restored by Step 1 of resume run, then deleted; `find ... -name '*.backup'` returns nothing) |

`git ls-files outputs/h11/e47-propose-brief/verified/flash-high-text-1of5/`
shows only the three files above. The probabilities file has been touched
exactly once in the entire repo history at commit `52b0215a` (2026-04-09
"data(e47): add N=5 consensus + PV results for propose_brief proposer").
Working tree matches `HEAD` byte-for-byte (`git diff` empty).

### 2.2 The "schema-transformation" question — resolved

The launch summary's § "Surprise" flagged that the previous overnight run
rewrote the e47 file from derived to canonical schema. Re-reading the full
chain:

1. **What's in HEAD now (and on disk now, identically)**: derived schema,
   keys = `{source, derived_from, vote_threshold, results}`. `source` is
   **self-referential** (points at itself); `derived_from = "1-of-5 union"`,
   `vote_threshold = 1`, 4,301 result entries.
2. **What the canonical schema would look like**: keys = `{version, mode,
   verifier_config, iterations, total_results, results}` — what
   `_save_probabilities_incremental()` writes (see `scripts/run_pv.py:950`).
3. **What happened on the failed cleanup attempt**: `cmd_cleanup()` read
   the existing 4,301 results, identified 57 missing, and called
   `_verify_realtime()`. The first incremental save would have written
   canonical schema (overwriting the derived keys). Then every API call
   failed with "Crop file not found" because the driver passed the wrong
   `--crops-dir`. After max_attempts, the file was left in canonical
   schema with `cleanup_history` showing 0 recovered / 57 still missing
   and a wiped `run.meta.json` (because `_verify_realtime` finalised an
   empty metadata tracker).
4. **What Step 1 of the resume restored**: per launch-summary lines 119–124,
   the operator copied
   `probabilities.json.pre-cleanup-20260503T145925.backup` over
   `probabilities.json` and `git checkout`-ed `run.meta.json` from HEAD,
   restoring the pre-run state — i.e., back to derived schema with 4,301
   results and the canonical original-run meta with 5,448 calls.

**The on-disk file in HEAD was ALREADY in derived schema before the
campaign even started.** The only commit that ever touched this file
(`52b0215a`) added it in derived form with self-referential `source`. The
operator's interpretation in the launch summary is correct: an earlier
`derive_vote_threshold_results.py` invocation must have used this 1of5
file as both `--probabilities` input and as a `--prefix flash-high-text`
output target, which structurally writes a vt=1 derived file with all
results unchanged but with `source` pointing back at itself. The
canonical-schema source for e47 1of5 with the original-run version /
mode / verifier_config / iterations metadata **was never committed**
(audit-trail end of road). The closest surviving canonical metadata is
in `run.meta.json` (which is intact and correct).

**Why this is not a blocker for cleanup or downstream consumption**:

- `cmd_cleanup` reads `results` regardless of schema (see
  `_compute_missing_candidates` at line 263: `verified_ids = set(probs.get
  ("results", {}).keys())`).
- All downstream consumers of `probabilities.json` for this cell — namely
  `compare_wbf_vs_greedy_production.py` (line 76, only reads
  `["results"]`), `materialise_pv_geojson.py` (line 179, only reads
  `["results"]`), and `derive_vote_threshold_results.py` (lines 86–88,
  reads `prob_data.get("results", {})`) — ignore the top-level schema
  keys.
- The schema rewrite **does** lose the self-referential `source` /
  `derived_from` / `vote_threshold` markers, but those are reconstructable
  from `derive_vote_threshold_results.py` re-running on the 1of5 file (it
  outputs a vt=1 derived file structurally identical to the current state).

**Conclusion**: the schema transformation is cosmetic. The data-integrity
question reduces to: "do you want the e47 1of5 file in canonical schema
with `cleanup_history` recording the recovered 57, or do you want to
re-run `derive_vote_threshold_results.py` afterwards to restore the
self-referential derived schema?" Either is reproducible. The simpler
choice is canonical schema after cleanup, no post-hoc derive on the source.

### 2.3 Why the Phase 3a recovery driver couldn't recover this cell

The driver invocation (lines 367–370 of `planning/run-phase3a-recovery.sh`):

```bash
recover_cell tier1 "e47-flash-high-text-1of5" \
    "outputs/h11/e47-propose-brief/verified/flash-high-text-1of5" \
    "outputs/h11/e47-propose-brief/verified/flash-high-text-1of5" \
    "$CONFIG_DIR/verify_adversarial-text.json"
```

Both `--crops-dir` and `--verified-dir` point at
`verified/flash-high-text-1of5/`. The verified directory has the
manifest and probabilities but **no** `crops/candidate_*.png` files.
`run_pv.py cleanup` resolves crop paths as
`crops_base_dir / candidate["crop_file"]` (see `lib_verifier.py:398`),
where `crop_file` in the manifest is `"crops/candidate_00000.png"`. With
`--crops-dir = outputs/.../verified/flash-high-text-1of5`, this resolves
to `outputs/.../verified/flash-high-text-1of5/crops/candidate_00000.png`,
which does not exist — hence the "Crop file not found" error reported
in the original overnight log.

The **canonical** crops directory for this cell is
`outputs/h11/e47-propose-brief/crops/flash-high-text-1of5/`. With
`--crops-dir` set to that path, `crops_base_dir / "crops/candidate_00000.png"`
resolves to `outputs/.../crops/flash-high-text-1of5/crops/candidate_00000.png`,
which exists (verified — 4,358 PNGs present).

This is therefore a **driver bug**, not a missing-data problem on zbook.
The bug was disguised as "missing crops" because on **sapphire**, the
gitignored crops directory was genuinely absent (sapphire stores only what
was committed to the repo, and crop PNGs are not committed). The original
overnight run on sapphire would have failed even with the correct
`--crops-dir` because the PNGs were not on that machine. The skip list
took the conservative interpretation: "missing crops" is the symptom; the
root cause distinction (driver path vs sapphire-side absence) was not
diagnosed at the time.

### 2.4 Dependency graph for 2of5..5of5 derivatives

After the audit (2026-05-03), the 11 derived cells inventory included:

| Derived cell (relative to `outputs/h11/e47-propose-brief/verified/`) | Gap (audit) | Live gap (re-checked now) |
|---|---:|---:|
| `flash-high-text-2of5` | 28 | 28 |
| `flash-high-text-3of5` | 19 | 19 |
| `flash-high-text-4of5` | 14 | 14 |
| `flash-high-text-5of5` | 9 | 9 |

All four derivatives are produced by
`scripts/derive_vote_threshold_results.py --pool-size 5 --prefix flash-high-text`
operating on the 1of5 source file plus the consensus geojson at
`outputs/h11/e47-propose-brief/consensus/flash-high-text-1of5.geojson`.
Once the 1of5 file is gap=0, re-running the derive script regenerates
all four derivatives at gap=0 (verified by reading lines 60–175 of
`derive_vote_threshold_results.py`: the script filters
`prob_data["results"]` by vote count ≥ threshold, so any candidate
present in the source ends up in the appropriate derivatives).

**Downstream consumers of e47 1of5 + derivatives** (per `grep -rln
"e47.*flash-high-text\|flash-high-text-[12345]of5" results/ scripts/`):

- 8 scripts: `compare_wbf_greedy_pv_permutation.py`,
  `fuse_detections_wbf.py`, `compare_wbf_vs_greedy_production.py`,
  `build_condition_inventory.py`, plus four shell drivers
  (`overnight-pro-verifier-all.sh`, `sapphire-pro-verifier-analysis.sh`,
  `final-pv-jobs.sh`, `sapphire-final-sweeps.sh`).
- 1 leaderboard cell:
  `results/leaderboard/per-architecture/era2/consensus/leaderboard_rows_50m.json`
  row `condition_id = "h11-e47-propose-brief"` (rank 11, tier 3,
  F1=0.7299 at 50 m, 5-of-5 vote_t). Tier-3 leaderboard ranking; not a
  Tier-1 paper-anchor unlike the Session-78 matrix cells.
- Combined era2 leaderboard tier files (12 leaderboard_tiers JSONs in
  `results/leaderboard/combined/era2/`). Same row carries through.

The consensus geojson file (`flash-high-text-1of5.geojson`) is **not**
affected by the cleanup — it is the proposer-side cluster output. Only
the verifier-side `probabilities.json` files need updating.

### 2.5 Remediation options (≥ 3, with trade-offs)

#### Option A — Cleanup with corrected `--crops-dir`, accept canonical schema

**What it does**: invoke `python scripts/run_pv.py cleanup` with
`--crops-dir outputs/h11/e47-propose-brief/crops/flash-high-text-1of5`
and `--verified-dir outputs/h11/e47-propose-brief/verified/flash-high-text-1of5`.
Then run `derive_vote_threshold_results.py` to refresh 2of5..5of5.

- **Cost**: ~57 verifier calls × ~$0.0014 = **~$0.08**. Wall-clock ~3–6 min
  for cleanup; ~30 min CPU for downstream propagation (`compare_wbf_vs_greedy_production.py`,
  `build_tiered_leaderboard.py`, `run_per_arch_leaderboards.sh`,
  `finalise_per_arch_leaderboard.sh`, `build_combined_leaderboard.sh 2`,
  `build_combined_tier_stability.sh`).
- **Risks**: (1) cleanup still fails for some candidates — the original
  run had 1,147 errors from a 5,448-call total, so the model is known to
  have difficulty with these specific candidates; (2) F1 movement on the
  e47 era2/consensus tier-3 row, rebalancing the leaderboard. The
  movement is bounded — 57 candidates against a pool of 4,358 (~1.3 %)
  — so the F1 shift will likely be < 0.005 absolute. Tier flips on
  rank 11 would only matter if a tier-2/3 boundary lies near. Worst case
  a per-arch tier-membership change requires running the post-arch
  stability check.
- **Reversibility**: full — `git revert` on the cleanup commits restores
  the pre-recovery state. The `.pre-cleanup-*.backup` is created
  automatically by `cmd_cleanup` (line 327) and stored alongside; even
  without git, the backup gives a one-line restore.
- **Decisions for user**: just one — accept canonical schema
  post-cleanup (default), or run a separate re-derive of the 1of5 file
  on itself to restore self-referential derived schema (cosmetic; not
  recommended).

#### Option B — Cleanup with corrected `--crops-dir`, then post-cleanup re-derive on the source for derived-schema preservation

**What it does**: same as Option A, then additionally run
`derive_vote_threshold_results.py` with the cleaned 1of5 as both source
input and as a vt=1 derive output overwriting itself, restoring the
self-referential derived schema as it appears in commit `52b0215a`.

- **Cost**: same as Option A plus a few seconds of CPU for the extra
  derive-on-self.
- **Risks**: this is exactly the operation that caused the canonical
  schema to be lost in the first place; doing it intentionally now is a
  research-hygiene preservation choice, not a recovery action. Risk is
  low because the on-disk file already has the same self-referential
  shape; the operation just reinstates the `source / derived_from /
  vote_threshold` keys that cleanup stripped.
- **Reversibility**: full (one more `git revert` step).
- **Decisions for user**: whether the schema-as-committed-at-`52b0215a`
  is worth preserving. Given that downstream consumers ignore the
  schema, this is mostly a documentation question. Recommend skipping.

#### Option C — Defer indefinitely; mark e47 1of5 as "known incomplete"

**What it does**: leave the 4,301-of-4,358 state in place; annotate
the audit report and continuity doc with "57 candidates intentionally
unrecovered, tier-3 row unaffected by < 1.5 % completeness gap". No
cleanup, no derive, no propagation.

- **Cost**: zero.
- **Risks**: (1) the audit ledger's "30 cells, 30 cleaned" closure story
  doesn't fully land — the project would carry forward "29 of 30 plus
  one accepted-incomplete" forever; (2) any future analysis that re-uses
  e47 1of5 inherits the gap; the well-known
  `cleanup_history`-as-audit-trail mechanism is bypassed. Note that the
  current state has no `cleanup_history` (the file is in derived schema
  with no audit trail field), so a future agent grepping for
  completeness will see 4,301 ≠ 4,358 with no documented explanation.
- **Reversibility**: full — Option A is always available later.
- **Decisions for user**: whether the recovery campaign's stated goal of
  "all 30 cells gap=0" is worth the ~$0.08 + 30 min compute. Given that
  Cell 2 and Cell 3 collectively close at <$0.01, accepting Option C
  for e47 alone is not an obviously preferable trade-off. Recommend
  Option A unless schema preservation is judged important.

#### Option D — Wait for sapphire, recover canonical-schema source from session archives

**What it does**: when sapphire is reachable post-travel, search session
archives (`archive/cc-sessions/vlm-burial-mound-detection/`,
`~/.claude/projects/`) for the original April 9 run's
`probabilities.json` before the self-referential derive overwrote it.
If found, restore as the cleanup base, then proceed with Option A.

- **Cost**: ~30 min investigation, no API spend. Cleanup cost same as
  Option A if successful.
- **Risks**: searching session archives may turn up nothing (the canonical
  source may simply not exist anywhere on disk); the investigation is a
  sunk-cost commitment. Even if found, the gain over Option A is
  marginal (canonical schema preservation; downstream consumers don't
  notice).
- **Reversibility**: investigation phase doesn't modify the working
  tree. Restoration would be reversible via `git`.
- **Decisions for user**: whether canonical-schema lineage is worth the
  archive investigation.

### 2.6 Recommendation for Cell 1

**Option A** — fix the driver path, run cleanup, run derive, propagate.
Total ~$0.08 + ~35 min wall-clock. Schema transformation is cosmetic;
no current consumer depends on derived-schema markers.

**Action sequence** (zbook, no sapphire required):

1. Verify the bug in `planning/run-phase3a-recovery.sh` lines 367–370
   (driver path). Either patch the driver or invoke the underlying
   `run_pv.py cleanup` directly with the corrected paths:

   ```bash
   python scripts/run_pv.py cleanup \
     --crops-dir outputs/h11/e47-propose-brief/crops/flash-high-text-1of5 \
     --verified-dir outputs/h11/e47-propose-brief/verified/flash-high-text-1of5 \
     --verifier-config prompts/configs/verify_adversarial-text.json \
     --max-attempts 3 \
     --safe-mode-tokens 2048
   ```

2. Run the consensus-based derive to refresh 2of5..5of5:

   ```bash
   python scripts/derive_vote_threshold_results.py \
     --consensus outputs/h11/e47-propose-brief/consensus/flash-high-text-1of5.geojson \
     --probabilities outputs/h11/e47-propose-brief/verified/flash-high-text-1of5/probabilities.json \
     --manifest outputs/h11/e47-propose-brief/verified/flash-high-text-1of5/candidate_manifest.json \
     --pool-size 5 \
     --output-dir outputs/h11/e47-propose-brief/verified \
     --prefix flash-high-text
   ```

3. Propagate per runbook § 6.1 e47 group: `compare_wbf_vs_greedy_production.py`,
   `build_tiered_leaderboard.py`, then the per-arch + combined chain.
4. Commit per logical group; push to `origin/main`; spot-check the
   per-arch tier composition for stability.

**Decisions for user before launch**:

- (a) accept Option A (canonical schema after cleanup, no post-derive
  on source) — recommended;
- (b) accept the API spend (~$0.08 — well under any meaningful threshold);
- (c) confirm no objection to a tier composition refresh on e47's
  era2/consensus tier-3 row.

---

## 3. Cell 2 — `55maps-gen-verified-v2`

### 3.1 Current state on disk

| File | Status |
|---|---|
| `outputs/55maps-generalisation/verified-v2/probabilities.json` | tracked, 7.0 MB, 8,939 results, **canonical schema** (`{version, mode, verifier_config, iterations, total_results, results}`) |
| `outputs/55maps-generalisation/verified-v2/run.meta.json` | tracked |
| `outputs/55maps-generalisation/crops/candidate_manifest.json` | gitignored, 6.2 MB, 8,942 candidates |
| `outputs/55maps-generalisation/crops/crops/candidate_*.png` | gitignored, **8,942 PNGs present on zbook** |
| Pre-cleanup `.backup` | absent |

`total_results = 8939`, expected `total_detections = 8942`, gap = 3 ✓
(matches the audit). Canonical schema; no `cleanup_history` field — this
cell has never been cleaned before. The driver path arguments at lines
440–443 (`outputs/55maps-generalisation/crops` and
`outputs/55maps-generalisation/verified-v2`) are **correct**: the
manifest's `crop_file = "crops/candidate_00000.png"` resolves under
`--crops-dir = outputs/55maps-generalisation/crops` to
`outputs/55maps-generalisation/crops/crops/candidate_00000.png`, which
exists.

### 3.2 Why the cell was skipped

The skip reason was `missing_crops_gitignored`. On **sapphire** in early
May, the bulk PNGs in `outputs/55maps-generalisation/crops/crops/` were
absent (per the launch-summary note: "55maps and proposer-verifier-384
have only `candidate_manifest.json`, no PNGs"). On zbook, they are
present (verified — 8,942 files matching `total_detections`). The
audit's classification — Tier 2, contamination-policy investigation,
gap=3 of ~9,000 — sets a low bar for movement; the v2 verifier and the
50 m threshold sweep are the only consumers.

### 3.3 Feasibility on zbook (no sapphire required)

- Crops present: ✓
- `--crops-dir` driver path correct as-is: ✓
- `--verifier-config` driver path correct as-is: ✓
- Tracked file paths consistent with on-disk layout: ✓
- No schema repair needed — file is already canonical.

The driver invocation can be re-run unmodified (after removing
`55maps-gen-verified-v2` from `SKIP_CELLS`), or the underlying
`run_pv.py cleanup` can be invoked directly. Wall-clock for 3 candidates
at ~$0.0014 each ≈ **~$0.005**, < 1 minute API time, plus a
`v2-threshold-sweep-50m/threshold_sweep.json` refresh (~5 min sweeping
21 thresholds with N=1,000 bootstrap).

### 3.4 Propagation path

Per runbook § 6.2 "verified-v2 (1 cell)":

1. Refresh `results/55maps-generalisation/v2-threshold-sweep-50m/threshold_sweep.json`
   via the threshold-sweep script (the file's `probabilities_file`
   field points at `outputs/55maps-generalisation/verified-v2/probabilities.json`,
   so re-running the sweep on the cleaned probabilities is sufficient).
2. Optionally annotate `docs/methodology/v2-verifier-contamination-policy.md`
   if its quoted F1 changes (gap=3 of 8,942 ≈ 0.034 % so movement will
   be sub-0.001 F1; almost certainly no annotation needed).

The original v2 sweep was run with the canonical
`scripts/7_analyse_consensus.py --threshold-sweep` pathway (per
threshold_sweep.json's `version: "1.0"` and the
`results/55maps-generalisation/v2-sweep.log` content). Re-running the
same script with the same `--probabilities-file` path picks up the
cleaned data automatically.

### 3.5 Recommended sequence

1. Run cleanup on this cell (zbook, ~< 1 min, ~$0.005).
2. Refresh the v2 50-m threshold sweep (~5 min CPU, no API).
3. Spot-check `results/55maps-generalisation/v2-threshold-sweep-50m/threshold_sweep.json`
   for whether F1 at any threshold moved ≥ 0.001; if so, the
   contamination-policy doc may need a one-line update.
4. Commit the cleanup + sweep refresh as one logical group (runbook § 9).

**Decisions for user**: just (a) accept the trivial spend and (b) accept
that the sweep result may differ at the 4th decimal place, which would
not require any paper-citation refresh.

---

## 4. Cell 3 — `proposer-verifier-384-adversarial-text-v1-prompt`

### 4.1 Current state on disk

| File | Status |
|---|---|
| `outputs/h11/proposer-verifier-384/verified-adversarial-text-v1-prompt/probabilities.json` | tracked, 446 KB, 571 results, **canonical schema** |
| `outputs/h11/proposer-verifier-384/verified-adversarial-text-v1-prompt/run.meta.json` | tracked, original-run stats (April 10) |
| `outputs/h11/proposer-verifier-384/candidates/candidate_manifest.json` | gitignored (?), 295 KB, 572 candidates |
| `outputs/h11/proposer-verifier-384/candidates/crops/candidate_*.png` | gitignored, **572 PNGs present on zbook** |
| Pre-cleanup `.backup` | absent |

`total_results = 571`, expected `total_detections = 572`, gap = 1 ✓.
Driver paths at lines 531–534 (`outputs/h11/proposer-verifier-384/candidates`
and `outputs/h11/proposer-verifier-384/verified-adversarial-text-v1-prompt`)
are correct: `--crops-dir = candidates/` + `crop_file = "crops/candidate_00000.png"`
resolves to `candidates/crops/candidate_00000.png` ✓.

### 4.2 Why the cell was skipped

Same reason as Cell 2 — gitignored crops absent on sapphire at
campaign time.

### 4.3 Feasibility on zbook

Trivial. 1 candidate at ~$0.0014 → seconds, well under any cost
threshold. No propagation needed: the audit reports "no current script
or analysis output references this cell" (runbook § 6.3 step 4
"`proposer-verifier-384/verified-adversarial-text-v1-prompt` cell has
no current consumer per the audit; cleanup is for ledger completeness
only, no propagation needed"). Verified by `grep -rln
verified-adversarial-text-v1-prompt scripts/ results/`: zero matches in
`scripts/` or `results/`; matches only in `docs/notes/reflections/`
(historical mentions), confirming no live consumer.

### 4.4 Recommended sequence

1. Run cleanup unmodified on this cell (~seconds, ~$0.0014).
2. No propagation needed.
3. Commit alongside Cell 2 in a single ledger-completeness commit.

**Decisions for user**: none — sub-cent spend, sub-second wall-clock,
no downstream effects.

---

## 5. Cross-cutting recommendations

### 5.1 Order to tackle the three cells

**Recommended order**: Cell 3 → Cell 2 → Cell 1.

Rationale: Cell 3 is the lowest-risk smallest-scope warm-up (1 candidate,
no propagation). Cell 2 follows with similar shape (3 candidates,
threshold-sweep-only propagation). Cell 1 is the only one with the
driver bug, the schema-transformation question, and a non-trivial
propagation chain (e47 derivatives + per-arch + combined leaderboards);
running it last lets the simpler cleanups validate the campaign's
software state on zbook before committing to the longer-running
e47 chain.

### 5.2 Sapphire requirement

**None**. All three cells can be cleaned on zbook with crops present
locally:

- Cell 3 — driver paths correct, crops present, sub-second wall-clock,
  zero propagation.
- Cell 2 — driver paths correct, crops present, < 1 min cleanup +
  ~5 min sweep refresh.
- Cell 1 — needs a one-line driver fix or direct invocation of
  `run_pv.py cleanup` with the corrected `--crops-dir`. Cleanup +
  derive + propagation all CPU-bound; no sapphire required even though
  the runbook originally assumed sapphire.

The CLAUDE.md compute-location-policy preference is sapphire for
"computationally intensive analysis", but the wall-clock here is
~30–35 min of CPU work plus a few minutes of API; well under the
threshold where zbook fan noise becomes disruptive. If sapphire is
reachable when the user resumes, sapphire is preferred for the e47
propagation chain (~30 min of CPU) but not required.

### 5.3 Right-now-on-zbook vs later-when-sapphire-reachable

If the user resumes on zbook before sapphire is reachable:

- **Tonight or tomorrow on zbook**: Cell 3 (5 min including commit),
  Cell 2 (15 min including commit + sweep refresh), Cell 1 (45 min
  including driver fix, cleanup, derive, propagation, commit).
- **Total**: ~1 hour of attended work, ~$0.09 API spend.

If the user prefers to wait for sapphire:

- All three can be moved to sapphire after the home-network reconnect.
- Sapphire would also need the gitignored crops re-extracted (a separate
  ~10 min `extract_candidates.py` pass per cell), making sapphire a
  worse choice unless rsync from zbook is faster than re-extraction.
- The e47 propagation chain runs noticeably faster on sapphire, but
  zbook will complete it within ~30 min — not worth deferring.

**Recommendation**: do all three on zbook. Sapphire is the right
location only for the broader Tier-2/3 propagation campaign where
sapphire was the original campaign's compute location and where local
state may have diverged.

### 5.4 Campaign-wide closure (Obs 324+)

The runbook (§ 7.1) calls for one campaign-closure observation. Two
options:

- **Option I**: roll the three skipped cells into the existing campaign
  closure narrative. Author Obs 324 only after all 20 cells (17
  cleaned + 3 closed via this report's plan) are gap=0. This requires
  finishing the Tier-2/3 propagation through sapphire before writing
  closure.
- **Option II**: write Obs 324 now to close Tier-1 (the 17 cleaned cells
  + the e47 1of5 once Cell 1 is done), and a follow-up Obs 325 to
  close Tier-2/3 once sapphire-side cleanup state is verified. This
  decouples the e47-Tier-1 closure (which can land tonight) from the
  larger campaign closure (which awaits sapphire).

**Recommendation**: **Option II** — close Tier 1 cleanly tonight by
fixing Cell 1 (the only Tier-1 skipped cell), then defer Cells 2 and 3
to a small sub-campaign once sapphire's Tier-2/3 work is verified. This
gives the user a clean Tier-1-closed milestone (`e47` no longer in the
"skipped" ledger) without depending on sapphire reachability.

---

## 6. Appendix — source-of-truth references

### 6.1 Files cited

| Path | Purpose in this report |
|---|---|
| `planning/paper-writeup-continuity.md` (lines 11–80) | Session-88 entry-point + 3 skipped cells beacon |
| `planning/phase3a-verifier-recovery-runbook.md` (full) | Cell inventory, tier definitions, propagation matrix, cost budget, rollback |
| `planning/run-phase3a-recovery.sh` (lines 87–95, 367–370, 440–443, 531–534) | Driver SKIP_CELLS + the 3 cells' `recover_cell` invocations |
| `planning/run-phase3a-recovery.sh.template` | Pristine template (not read; cited as canonical source per launch-summary) |
| `logs/phase3a-recovery-overnight/launch-summary.md` (full) | Original overnight launch metadata |
| `logs/phase3a-recovery-overnight-resume/launch-summary.md` (full, especially § "Surprise" lines 102–127, § "Three skipped cells" lines 88–100, § Morning-user resumption lines 147–206) | Resume-launch documentation including the schema-transformation diagnosis and the SKIP_CELLS list |
| `reports/phase3a-verifier-completeness-audit-2026-05-03.md` (last section "Recovery status (annotated post-execution, partial — 2026-05-06)") | Authoritative outstanding-work list and methodological-note on the wrong-driver detour |
| `outputs/h11/e47-propose-brief/verified/flash-high-text-1of5/{probabilities,candidate_manifest,run.meta}.json` | Cell 1 on-disk state |
| `outputs/h11/e47-propose-brief/crops/flash-high-text-1of5/{candidate_manifest.json, crops/*.png}` | Cell 1 canonical crops directory (4,358 PNGs present) |
| `outputs/h11/e47-propose-brief/consensus/flash-high-text-1of5.geojson` | Cell 1 consensus geojson (input to `derive_vote_threshold_results.py`) |
| `outputs/h11/e47-propose-brief/verified/flash-high-text-{2,3,4,5}of5/probabilities.json` | Cell 1 derivatives — gap=28/19/14/9 verified |
| `outputs/55maps-generalisation/{crops/crops, verified-v2/}` | Cell 2 on-disk state |
| `outputs/h11/proposer-verifier-384/{candidates/crops, verified-adversarial-text-v1-prompt/}` | Cell 3 on-disk state |
| `scripts/run_pv.py` (lines 235–265 `_compute_missing_candidates`, 268–422 `cmd_cleanup`, 862–927 `_log_cleanup_failures_to_meta`, 930–963 `_save_probabilities_incremental`, 970–1059 `_verify_realtime`, 1326–1339 metadata persistence) | Cleanup logic and schema-transformation behaviour |
| `scripts/lib_verifier.py` (line 398 `crop_path = crops_base_dir / candidate["crop_file"]`) | Crop path resolution |
| `scripts/derive_vote_threshold_results.py` (lines 60–175 derivation logic, 182–218 CLI args) | Derivative regeneration logic and source schema |
| `scripts/extract_candidates.py` (lines 462–540 main + CLI; defaults at lines 66–68) | Crop extraction CLI; not invoked but feasibility-validated |
| `scripts/compare_wbf_vs_greedy_production.py` (lines 51–82 paths, 65–98 load logic) | Downstream consumer of e47 1of5 (only reads `["results"]`) |
| `scripts/materialise_pv_geojson.py` (lines 175–194) | Downstream consumer (only reads `["results"]`) |
| `results/leaderboard/per-architecture/era2/consensus/leaderboard_rows_50m.json` | Cell 1 leaderboard impact (rank 11, tier 3, F1=0.7299 at 50 m) |
| `results/55maps-generalisation/v2-threshold-sweep-50m/threshold_sweep.json` | Cell 2 only consumer |
| `results/55maps-generalisation/v2-sweep.log` | Cell 2 sweep provenance |

### 6.2 Commits cited

| Commit | Subject | Significance |
|---|---|---|
| `52b0215a` | `data(e47): add N=5 consensus + PV results for propose_brief proposer` | First and only commit touching e47 1of5 probabilities.json — already in derived schema with self-referential `source` |
| `cc914da5` | `data(e47): add v2 verifier results with cleanup (4358/4358 complete)` | Demonstrates a successful precedent for cleaning the e47 corpus (under v2 verifier); confirms the campaign-end state is achievable |
| `adf95dbf` | Phase 3a verifier-completeness audit | The original audit identifying these cells as gap-positive |
| `b3ed509e` | `analysis(p3a-recovery): propagate Session-78 cleanup through materialise + calibration` | Last Tier-1 propagation commit before the 3 cells were skipped |
| `e174390e` | `fix(phase3a-recovery): skip 3 crop-missing cells; resume from cell 8` | Where the SKIP_CELLS array landed |
| `cebe5fed` | `chore(gitignore): exclude phase3a-recovery-overnight-resume driver logs` | Resume-launch chore |
| `64974ec5` | `Obs 323` — Tier-1 propagation closure | Anchoring observation; this report extends the closure narrative |
| `ca0567d3` | Full redesign rebuild (q01 + MCC + stage 3-5) | Completes the q01+MCC follow-up; tier composition matches `c067bca4` audit anchor |
| `baa271bf`, `ef3ec4fe` | runner default fix + runbook fix | The wrong-driver detour fixes; relevant to any future propagation re-runs |
| `d59798ac` | (cited as `git_commit` in proposer-verifier-384's `run.meta.json`) | Provenance for Cell 3's original run |

### 6.3 What was NOT investigated (out of scope)

- The Tier-2/3 sapphire-side cleanup state. The continuity doc's "Tier
  2/3 propagation when sapphire is reachable" is a separate workstream;
  this report addresses only the three cells whose driver invocations
  were skipped on sapphire.
- Whether to migrate any of the three cells' bulk PNG directories from
  zbook to sapphire (or to commit a small subset). Out of scope; affects
  reproducibility infrastructure rather than the immediate closure.
- The 8 "unrecoverable cells" from the original audit (no candidate
  manifest). Runbook § 11 documents these as out-of-scope for the
  recovery campaign; this report does not revisit.
- API Call Review Gate. The total spend across all three cells (~$0.09)
  is below any meaningful approval threshold, but the project's policy
  in `~/.claude/CLAUDE.md` calls for explicit per-batch approval. The
  user should apply that policy to the recommendations here.

---

## End of investigation
