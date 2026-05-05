# Session 86 — Tier-1 6-Cell Propagation Plan (zbook, post-travel)

**Author:** Plan agent (architect), 2026-05-04
**Repo:** `/home/shawn/Code/map-reader-llm`
**Branch:** `main`, HEAD `7beed974`
**Audience:** Session-86 operator (Claude Code on zbook). User is travelling; sapphire is unreachable.

---

## 0. Scope and assumptions

**In scope.** Heavy CPU propagation downstream of the *already-committed* Tier-1 cleanup of the **6 Session-78 verifier-calibration cells** (commits `414ee8a4` cleanup data + `b3ed509e` materialise+calibration). This is the work the 2026-05-03 launch-summary explicitly deferred to "morning operator" under runbook § 6.1 steps 3–6.

**Out of scope.**

- Tier-2 / Tier-3 cleanup or propagation (status unverifiable without sapphire). The 2026-05-03 resume launch-summary projected Tier-2/3 would finish ~15 minutes after launch, but no Tier-2/3 cleanup commits have landed on `origin/main`. **Treat Tier-2/3 as DEFERRED** until sapphire is reachable.
- The 3 skipped cells (`e47-flash-high-text-1of5`, `55maps-gen-verified-v2`, `proposer-verifier-384-…-v1-prompt`). Crops are gitignored and cannot be regenerated on zbook without inputs.
- Cross-track v2 grid rebuild, attractor-pull, FP-classify. The Tier-1 6 cells map only to Session-78 matrix consumers; runbook § 6.4 confirms cross-track grid is unaffected.
- Step 6 paper outline drafting.

**Key facts surfaced from exploration.**

1. The 6 cells already on disk (committed at `b3ed509e`) are: `text-{adversarial,brief,checklist}-text` + `image-{adversarial,brief,checklist}-text`. These are the `*-text` variants only; `*-comparative` and the bare `*-{adversarial,brief,checklist}` cells were not part of the Tier-1 cleanup.
2. AUC deltas already documented from the calibration step are 0.0001–0.0010 absolute, with **3 of 6 cells moving DOWN** (image-checklist-text, text-adversarial-text, text-checklist-text). This is below the runbook's >0.005 movement-threshold but **above the >0.001 paper-citation refresh threshold for 2 of the 6 cells** (image-brief-text +0.0010 is exactly on the boundary).
3. Per-arch leaderboards (`results/leaderboard/per-architecture/cross-architecture-era2_*.md`, `headlines_*.md`, `mc-precision-flags.md`) cite Session-78 cells directly. These rebuild from `planning/condition-inventory-with-s78.json` (70 session-78 references) which points at `results/leaderboard/era2/pv-materialised/session-78-*.geojson` — already refreshed in `b3ed509e`.
4. Latest Obs in `working-notes.md` is **Observation 322** (TP-localisation-tail reframing). **Next free Obs number is 323.**
5. Combined leaderboard `build_combined_leaderboard.sh` runs **per-Era**; only Era 2 contains Session-78 cells (per the inventory). Era 1 and Era 3 do not need rebuilding.
6. CLAUDE.md confirms: ruff on modified Python; markdownlint on modified Markdown; tier1/tier2 pytest markers if new Python; archive-never-delete; UK/Australian spelling.

---

## 1. Pre-flight verification (≤ 5 min)

Run on zbook before starting any heavy step. Operator MUST stop and ask the user if any check fails unexpectedly.

**1.1 Repo state.**

```bash
cd ~/Code/map-reader-llm
git status                             # working tree clean
git log --oneline -3                   # HEAD = 7beed974 (or further)
git log --oneline 414ee8a4..HEAD       # confirm 414ee8a4 + b3ed509e are present
```

**1.2 Branch parity.** Confirm `main` is up to date with `origin/main`. If sapphire later becomes reachable and has Tier-2/3 commits, those would land via `git pull` *after* this propagation — accept that and re-run propagation if so.

**1.3 Inputs on disk.**

- `results/leaderboard/era2/pv-materialised/session-78-{image,text}-{adversarial,brief,checklist}-text.geojson` (6 files, refreshed at `b3ed509e`).
- `results/leaderboard/era2/pv-materialised/session-78-matrix-registry.json` (refreshed at `b3ed509e`).
- `results/verifier-calibration-matrix/{image,text}-{adversarial,brief,checklist}-text/calibration.json` (6 files, refreshed at `b3ed509e`).
- `planning/condition-inventory-with-s78.json` (canonical inventory; should be unchanged).
- `inputs/vectors/bounds/384/full_evaluation_bounds.geojson` (Era-2 bounds, 487 tiles).

**1.4 Python env.** `source .venv/bin/activate && python -V` (project venv, not system Python).

**1.5 Tier-1 sanity.**

```bash
pytest -m tier1 --tb=short -q | tail -3
```

Expect green. If failures surface, halt and ask the user — do not propagate on top of broken tests.

**1.6 Disk and CPU sanity.** `df -h .` should have ≥10 GB free for cache (`results/leaderboard/per-architecture/era*/.cache/` is the dominant consumer). `nproc` should report ≥ 8 cores; the per-arch script defaults to `WORKERS=8`. If zbook has fewer cores, edit `scripts/run_per_arch_leaderboards.sh` `WORKERS=...` line **inline** for this run only (do not commit) — runbook § 6.1 doesn't pin the worker count.

**Halt criterion for pre-flight.** Any failure → stop and ask the user. Do not "fix" by editing tracked files.

---

## 2. Step 1 — `build_tiered_leaderboard.py` for the 6 Session-78 cells (~20–30 min)

**Per runbook § 6.1 step 3.** This rebuilds the 6 leaderboard-cell JSONs at `results/leaderboard/cells/session-78-{image,text}-{adversarial,brief,checklist}-text-487tile.json`.

**Question for operator:** the launch-summary lists `bash scripts/run_per_arch_leaderboards.sh` directly, which calls `build_tiered_leaderboard.py` per stratum. The per-arch script *does* read the inventory (which references the materialised Session-78 GeoJSONs), so cell rebuilds happen as a side effect of step 3. **Confirm there is no separate per-cell script needed**; if `build_tiered_leaderboard.py` has a single-cell invocation mode, prefer that for the 6 Session-78 cells specifically (cheaper). Inspect:

```bash
python scripts/build_tiered_leaderboard.py --help | head -40
```

If a `--cell` or `--filter` flag exists, use it. Otherwise the per-arch script (Step 3) handles this implicitly — skip Step 2 here and treat the per-arch run as covering both.

**Verification.**

- 6 files at `results/leaderboard/cells/session-78-{image,text}-{adversarial,brief,checklist}-text-487tile.json` have mtime > b3ed509e commit time.
- `git status` shows only those 6 JSONs modified (and possibly cache files).

**Commit boundary 1 (only if Step 2 is run separately):**

```text
analysis(p3a-recovery): rebuild 6 Session-78 leaderboard cells post-cleanup

Re-runs build_tiered_leaderboard.py on the 6 Session-78 *-text cells
that were cleaned in 414ee8a4 and re-materialised in b3ed509e. F1 deltas
within calibration AUC bounds (<0.005 absolute); no tier-rank flips.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
```

If Step 2 is folded into Step 3, skip this commit.

---

## 3. Step 2 — Per-architecture leaderboards (`run_per_arch_leaderboards.sh`) — **DOMINANT WALL-CLOCK** (~2–3 h)

**Per runbook § 6.1 step 4.** This is the single longest step.

**3.1 Pre-decision: cache reuse.** The script writes to `results/leaderboard/per-architecture/era<N>/<arch>/.cache/`. Per-cell evaluations and pairwise-permutation results are cached. **Sessions-78 cells live in Era-2-pv only** (per the inventory). The `consensus`, `single-pass`, and `single-pass+PV` strata of Era 2 do NOT reference Session-78 cells (verified via grep: only `pv` stratum hits Session-78 cells in `cross-architecture-era2_*.md`). So:

- Era 1 (consensus, single-pass): **cache-unaffected; rerun is a no-op via cache**.
- Era 2 consensus, single-pass, single-pass+PV: **cache-unaffected; rerun is a no-op via cache**.
- Era 2 pv: **cache invalidation expected on the 6 Session-78 cells; ~20–40 min for this stratum alone**.
- Era 3 (consensus): **cache-unaffected; no-op**.

Total expected wall-clock on zbook (cache-reuse warm): **~30–60 min**, dominated by the Era-2-pv re-pairing across the affected 6 cells × ~40 other pv conditions × 5 buffers × 10K permutations.

**Operator option:** to confirm cache will be reused, peek at `.cache/evaluations/` before kickoff (the cell's cached evaluation key embeds the materialised GeoJSON's hash; refreshed GeoJSONs invalidate only their own keys). If unsure, just run — wall-clock budget allows the worst case.

**3.2 Run.**

```bash
bash scripts/run_per_arch_leaderboards.sh 2>&1 | tee logs/session-86-per-arch-$(date -u +%Y%m%dT%H%M%SZ).log
```

*(The script's own log dir is `logs/per-arch-leaderboards/`; the tee captures driver-level stdout for sanity.)*

Operator should monitor periodically — but per the harness's policy, do not poll; rely on `run_in_background=true` if launching from a shell tool, or simply schedule an extended wakeup window if invoking from a /loop.

**3.3 Verification.**

- All 12 strata complete (Era 1: 2 strata; Era 2: 4 strata; Era 3: 1 stratum, plus stub generation).
- `results/leaderboard/per-architecture/era2/pv/leaderboard_tiers_*.json` mtimes are post-launch.
- Tier-membership of Session-78 cells in `era2/pv/leaderboard_tiers_20m.json`: **expected zero tier flips** (AUC deltas of 0.0001–0.0010 against pools of 2K–4K should not move tier).
- Spot-check `results/leaderboard/per-architecture/cross-architecture-era2_20m_f1.md` for `session-78-` rows: expect F1 changes ≤0.001 absolute, ranks stable.

**Halt criterion:** any tier-rank flip on the 6 cells → halt, capture state, ask the user. (Runbook § 5.3 invariant.) The script does not auto-halt on this; the operator must inspect the post-rebuild output.

**3.4 Step-3-of-script note.** `run_per_arch_leaderboards.sh` does NOT auto-trigger `finalise_per_arch_leaderboard.sh`. That is Step 4 below.

---

## 4. Step 3 — Finalise per-arch (`finalise_per_arch_leaderboard.sh`) — ~5–10 min

**Per runbook § 6.1 step 4 (continuation).** This:

1. Augments tier JSONs with tile-MCC @ 20 m (`augment_per_arch_with_mcc.py`, ~60 s).
2. Enriches per-buffer Markdown tables (`enrich_per_arch_markdown.py`).
3. Builds cross-architecture comparison at 20 m (`build_cross_arch_comparison.py`).
4. Per-stratum headlines (`summarise_per_arch_headlines.py`).
5. Spot-check verification (`verify_per_arch_leaderboard.py`).

**Run.**

```bash
bash scripts/finalise_per_arch_leaderboard.sh 2>&1 | tee logs/session-86-finalise-$(date -u +%Y%m%dT%H%M%SZ).log
```

**Verification.**

- `results/leaderboard/per-architecture/cross-architecture-era2_*.md` and `headlines_*.md` mtimes post-step.
- Spot-check verification step prints "OK" for each stratum.

**Commit boundary 2 (combine Steps 2 + 3):**

```text
analysis(p3a-recovery): rebuild per-arch leaderboards post-Session-78 cleanup

Per runbook section 6.1 steps 3-4, refresh per-architecture leaderboards
across all 12 (era, arch) strata. Cache-reuse limits effective rebuild
to era2/pv where the 6 Session-78 *-text cells live. Tier rankings
preserved on all 6 cells; F1 deltas <= 0.001 absolute (matches AUC
deltas in b3ed509e). Headlines + cross-architecture comparison +
per-buffer markdown tables all refreshed.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
```

**DO NOT push yet.** Push at end of all propagation (Step 7, after the closure docs).

---

## 5. Step 4 — Combined leaderboard for Era 2 (`build_combined_leaderboard.sh 2`) — ~30–60 min

**Per runbook § 6.1 step 5.** Cross-architecture pooling, BH-FDR-tiered ranking. Cache reuses per-arch hardlinks; only cross-architecture pairs involving the 6 cleaned cells are computed fresh (a small fraction of total pairs).

**Decision point — Era 1 and Era 3:** these eras do NOT contain Session-78 cells. **Recommend skipping** `build_combined_leaderboard.sh 1` and `build_combined_leaderboard.sh 3` (rebuild would be a cache-only no-op but doubles wall-clock). The launch-summary's "Option C" lists only `build_combined_leaderboard.sh 2`; align with that.

**Run.**

```bash
bash scripts/build_combined_leaderboard.sh 2 2>&1 | tee logs/session-86-combined-era2-$(date -u +%Y%m%dT%H%M%SZ).log
```

**Verification.**

- `results/leaderboard/combined/era2/leaderboard_tiers_f1_{20,30,40,50,100}m.json` mtimes post-step.
- `results/leaderboard/combined/era2/leaderboard_tiers_mcc.json` mtime post-step.
- Session-78 cells rank-stability check across the 5 buffers.

---

## 6. Step 5 — Combined tier stability (`build_combined_tier_stability.sh 2`) — ~5–10 min

**Per runbook § 6.1 step 6.** Tier-stability tables.

**Run.**

```bash
bash scripts/build_combined_tier_stability.sh 2 2>&1 | tee logs/session-86-stability-era2-$(date -u +%Y%m%dT%H%M%SZ).log
```

**Verification.**

- `results/leaderboard/combined/era2/tier-stability*.{md,json}` mtimes post-step.

**Commit boundary 3 (combine Steps 4 + 5):**

```text
analysis(p3a-recovery): rebuild Era-2 combined leaderboard + tier stability

Per runbook section 6.1 steps 5-6, refresh combined cross-architecture
leaderboard for Era 2 (only era containing Session-78 cells) and the
tier-stability tables. Era 1 + Era 3 unaffected; not rebuilt.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
```

---

## 7. Step 6 — Paper-citation Markdown refresh — DECISION POINT

**Per runbook § 7.3 / continuity-doc § "Heavy propagation" item 3.** The trigger is "F1 movement > 0.001 absolute".

**Surfaced AUC deltas (from `b3ed509e` commit message):**

| Cell | AUC delta |
|---|---|
| image-adversarial-text | +0.0004 |
| image-brief-text | **+0.0010** (boundary) |
| image-checklist-text | **−0.0006** (down) |
| text-adversarial-text | **−0.0001** (down) |
| text-brief-text | **+0.0007** |
| text-checklist-text | **−0.0002** (down) |

**🛑 USER DECISION POINT 1 — refresh threshold ambiguity.**

The continuity doc says ">0.001"; the runbook § 7.3 says "> 0.001". Strictly, only `image-brief-text` at +0.0010 *equals* (does not exceed) the threshold, and three cells went DOWN. The operator should NOT auto-decide:

- **Option α — strict `>0.001`**: refresh nothing. AUC deltas are AUC deltas (not F1 deltas; F1 deltas at the chosen threshold could be larger or smaller in either direction). After Step 4 lands, compute F1 deltas explicitly per cell from the new vs old leaderboard JSONs and apply the threshold to F1 — that's the canonical metric.
- **Option β — `>=0.001`**: refresh `image-brief-text` only.
- **Option γ — refresh all 6**: cheap, transparent, treats the campaign as a single coherent state-update. Costs ~15 min of editing.
- **Option δ — refresh all where sign or magnitude moved**: include the 3 down-shifts even if magnitude is < 0.001 — these are factually different numbers post-cleanup.

**Plan:** the operator should compute F1 deltas at 20 m + 50 m primary buffers from the post-Step-4 leaderboard JSONs and present a 6-row delta table to the user, then ask which option to apply. **Do NOT auto-pick.**

**Possible refresh targets (locate dynamically once the deltas are known):**

```bash
grep -rln "session-78-\(image\|text\)-\(adversarial\|brief\|checklist\)-text" docs/ planning/ results/ | grep -v archive/
```

If refreshes happen, lint Markdown:

```bash
npx markdownlint-cli2 <files>
```

**Commit boundary 4 (only if any refresh applied):**

```text
docs(p3a-recovery): refresh paper-citation numbers for cleaned Session-78 cells

Per runbook section 7.3, refresh F1 / AUC quotations in <files> for
cells whose F1 movement post-Tier-1 cleanup exceeded the >0.001
threshold (or per user decision in Session 86). Pre/post deltas:
<table>.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
```

If no refresh applied, document the decision in the closure Obs (Step 9 below).

---

## 8. Step 7 — Decision points to surface to the user

These are decisions the user explicitly told the planner not to auto-resolve. The operator should present a single message to the user covering:

**🛑 USER DECISION POINT 2 — refresh threshold (see Step 6 above).**

**🛑 USER DECISION POINT 3 — wait for Tier-2/3 confirmation before per-arch rebuild?**

The plan above runs the per-arch rebuild now. Alternative: defer until sapphire is reachable and Tier-2/3 status is known.

- **Pro of running now**: forward progress; the 6-cell delta is small; if Tier-2/3 cells later affect different conditions, the rebuild reruns idempotently with cache reuse (cost: ~30–60 min wall-clock the second time).
- **Con of running now**: doubles bookkeeping (two commits + two Obs entries) if Tier-2/3 cells touch the same Era-2-pv stratum.
- **Pro of deferring**: single coherent rebuild covering all 17 cleaned cells.
- **Con of deferring**: blocks all paper-text drafting until sapphire is reachable; user is travelling for an unspecified duration.

**Recommendation (do not auto-apply):** given the user said "zbook is capable" and explicitly framed this as "Phase3a Tier-1 6-cell propagation", the implicit endorsement is to run now. But surface the trade-off explicitly.

**🛑 USER DECISION POINT 4 — closure Obs scope.**

The continuity doc envisions Obs 323 as the "campaign closure including all 17 cleaned cells". With Tier-2/3 unconfirmed:

- **Option A — Obs 323 = Tier-1-only closure** (this session). Title: "Tier-1 Session-78 6-cell propagation closure (Session 86)". Defer the campaign-wide closure to a future Obs (324?) when Tier-2/3 lands.
- **Option B — Defer Obs 323 entirely** until Tier-2/3 is confirmed. Risk: in-flight knowledge is not captured; future operator must reconstruct Tier-1 propagation from commits.
- **Option C — Obs 323 = "Tier-1 propagation + Tier-2/3 status unknown"**, single Obs with explicit gap. Captures more context but reads as incomplete.

**Recommendation (do not auto-apply):** Option A. Tier-1 is a coherent closure; Tier-2/3 (if/when they exist) get their own Obs. This matches the precedent of Obs 320 (T=0.7 closure) → Obs 321 (Session-84 follow-ups) being separate Obs entries for separate sub-campaigns.

**🛑 USER DECISION POINT 5 — `post_run_report` convention.**

User explicitly said "don't auto-pick — discuss in Session 86". The three options (refresh in place / forward-pointer banner / leave as historical snapshot) are documented in `planning/paper-writeup-continuity.md` lines ~64–68 and ~112–116. Operator should raise this when presenting Decision Points 2–4 to the user. **NO ACTION** in this propagation arc.

---

## 9. Step 8 — Closure observation in `working-notes.md` — ~10 min

**Pending User Decision Point 4.**

If Option A (Tier-1-only closure, Obs 323):

The /observe skill is the canonical mechanism. Operator should invoke it:

```text
/observe
```

…and supply title + body. **Recommended title:**

> Observation 323: Phase3a Tier-1 propagation closure — Session-78 6 cells, AUC deltas ≤0.0010, no tier flips (Session 86, 2026-05-04)

**Body should include** (per the Obs 321 / Obs 322 template):

- "The finding" — 6 cells cleaned, 153 candidates recovered (cleanup cost $0.1951 from `414ee8a4`); AUC deltas table; F1 deltas table (from Step 4 output); zero tier-rank flips on Era-2-pv leaderboard.
- "Caveats" — Tier-2/3 status unverifiable (sapphire unreachable); the gap=460 Tier-2 cell outcome unknown; the 3 skipped cells (e47, 55maps-gen-v2, proposer-verifier-384) still pending.
- "Findable later" — search-term block (commit hashes `414ee8a4`, `b3ed509e`, this-session commits; Session-78 matrix; per-arch rebuild Session 86).
- "Related Obs / artefacts" — Obs 320 (T=0.7 recovery closure), Obs 321 (Session-84 follow-ups), the recovery runbook, the launch summaries.

**Verification:** `npx markdownlint-cli2 docs/notes/reflections/working-notes.md` clean.

**Commit boundary 5 (combine Steps 8 + 9 + 10):** see § 11.

---

## 10. Step 9 — Continuity doc update (`paper-writeup-continuity.md`)

**Per continuity doc § 5 ("Update this continuity doc")**.

Append a new top-level "Session 86 — Tier-1 propagation complete (post-travel resume)" section before the existing "Session 85 closure" section, with:

- Headline: 6 cells propagated, 0 tier flips, ≤0.001 F1 delta.
- Commit chain (from this session).
- What's done / what's still pending (Tier-2/3 status, 3 skipped cells, A2 image re-evaluation, paper outline).
- A pointer to Obs 323 (or whatever Decision Point 4 resolves).
- Decision Point 5 (post_run_report) status — still pending discussion.

Update the doc's `**Last updated**:` line to `2026-05-04 (Session 86 — Tier-1 propagation complete)`.

**Verification:** `npx markdownlint-cli2 planning/paper-writeup-continuity.md` clean.

---

## 11. Step 10 — Audit-report annotation (`reports/phase3a-verifier-completeness-audit-2026-05-03.md`)

**Per runbook § 7.4 / continuity § 6.** Append at end of file:

```markdown
## Recovery status (annotated post-execution, partial)

- 2026-05-03 night: campaign cleanup phase ran (commits 414ee8a4 + b3ed509e + …).
  17 of 20 cells cleaned; 3 skipped (`e47-flash-high-text-1of5`,
  `55maps-gen-verified-v2`, `proposer-verifier-384-…-v1-prompt`) due to
  missing crops (gitignored bulk intermediates).
- 2026-05-04 (Session 86, zbook): Tier-1 propagation through per-arch +
  combined leaderboards complete. 0 tier-rank flips on the 6 Session-78
  cells; F1 deltas <= 0.001 absolute. See Obs 323 and commits
  <range>.
- **Tier-2 / Tier-3 propagation status: UNVERIFIED at Session 86 close**
  (sapphire unreachable during user travel). To be resolved when sapphire
  is back online; campaign-wide closure deferred to a future Obs.
- See `planning/phase3a-verifier-recovery-runbook.md` for procedure;
  `logs/phase3a-recovery-overnight-resume/launch-summary.md` for the
  cleanup-phase ground truth.
```

**Verification:** `npx markdownlint-cli2 reports/phase3a-verifier-completeness-audit-2026-05-03.md` clean.

**Commit boundary 5 (combined closure docs):**

```text
docs(p3a-recovery): Tier-1 propagation closure — Obs 323 + continuity + audit annotation

Closes the Tier-1 6-cell Session-78 propagation arc. Adds Obs 323 to
working-notes; Session 86 entry to paper-writeup-continuity; partial
recovery-status annotation to the 2026-05-03 audit report. Tier-2/3
status remains unverified pending sapphire reachability.

Per runbook sections 7.1, 7.2, 7.4.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
```

---

## 12. Step 11 — Final verification + push — ~2 min

**Verification.**

- `git status` clean (all intended changes committed).
- `git log --oneline 7beed974..HEAD` shows the expected 3–5 commits (Steps 4-or-5, 7-conditional, 11).
- `pytest -m tier1 --tb=short -q | tail -3` still green.

**Push.**

```bash
git push origin main
```

*(Per project policy: push at tier boundaries; the Tier-1 propagation arc is a tier boundary.)*

---

## 13. Rollback / abort criteria

The operator MUST halt and ask the user (not auto-recover) if any of these surface:

1. **Tier-rank flip on any of the 6 Session-78 cells in any leaderboard at any buffer** (runbook § 5.3 invariant). The AUC deltas (≤0.001) make this very unlikely; if it happens, the cleanup itself or the materialise step is suspect.
2. **F1 movement > 0.01 absolute on any cell** (runbook § 5.2 prompts manual inspection). Highly unlikely given AUC deltas, but the F1 metric at the chosen threshold can amplify.
3. **`pytest -m tier1` regression** between pre-flight and post-step (any new failures).
4. **Disk full** during per-arch rebuild (cache can grow several GB).
5. **Per-arch script aborts mid-run** for any reason. Inspect log; do NOT just rerun.
6. **markdownlint or ruff failures** on any modified file. Fix the violation; do not commit through.
7. **Sapphire becomes reachable mid-session and shows Tier-2/3 commits on origin/main beyond what zbook has pulled.** Halt, pull, re-plan — Tier-2/3 may invalidate Step 4 cache.
8. **Combined Era-2 rebuild produces zero changes** (mtimes don't bump). Indicates a cache-handling bug; investigate before committing.

For #1, #2, #5, #7, #8: **do not commit; do not push; surface to user**.

For #3, #4, #6: fix in place if trivial, otherwise halt.

**Soft rollback (if needed):** `git revert <commit-range>` — the pre-recovery `probabilities.json.pre-cleanup-*.backup` files preserve the upstream state per runbook § 10.1.

---

## 14. Tier-2 / Tier-3 placeholder (DEFERRED)

The full campaign closure (the "Obs 323 = all 17 cells" envisioned in `paper-writeup-continuity.md` line 91) is **contingent on Tier-2/3 cleanup status being verifiable**. As of 2026-05-04 morning:

- No Tier-2 cleanup commits beyond `b3ed509e` exist on `origin/main`.
- No Tier-3 cleanup commits exist on `origin/main`.
- The launch-summary (`logs/phase3a-recovery-overnight-resume/launch-summary.md`) projected ~15 min wall-clock for the unattended Tier-2/3 cleanup, but whether it succeeded is unknown without sapphire access.

**When sapphire is reachable** (future session), the operator should:

1. `ssh sapphire 'cd ~/Code/map-reader-llm && git log --oneline 1d9be35c..HEAD'` and inspect for cleanup commits.
2. If commits exist, pull them to zbook + re-run Steps 2–6 (cache reuse will limit wall-clock).
3. If campaign halted partially, consult `logs/phase3a-recovery-20260503T151930Z/cost-ledger.csv` on sapphire for per-cell status.
4. Update Obs 323 (or add Obs 324) to capture the Tier-2/3 outcome.
5. Resolve the 3 skipped cells per the continuity doc § 2 plan (regenerate crops on sapphire; cleanup; propagate).

**This Tier-1-only propagation does NOT block Tier-2/3 work.** Cache reuse + commit-per-tier policy mean the second pass is incremental.

---

## 15. Estimated total wall-clock

| Step | Description | Wall-clock |
|---|---|---|
| 1 | Pre-flight verification | 5 min |
| 2 | (Optional, if separable) per-cell leaderboard rebuild | 0–30 min |
| 3 | `run_per_arch_leaderboards.sh` | 30–180 min |
| 4 | `finalise_per_arch_leaderboard.sh` | 5–10 min |
| 5 | `build_combined_leaderboard.sh 2` | 30–60 min |
| 6 | `build_combined_tier_stability.sh 2` | 5–10 min |
| 7 | Paper-citation Markdown refresh (decision-gated) | 0–30 min |
| 8 | User decision points | 5–15 min user |
| 9 | Closure Obs (`/observe`) | 10 min |
| 10 | Continuity doc update | 10 min |
| 11 | Audit-report annotation | 5 min |
| 12 | Push + final verify | 2 min |
| **Total** | | **~2–6 h** (typical: 2.5 h cache-warm; 4 h cache-cold) |

Within the user's stated 2–3 h envelope if cache reuse holds; if cache-cold (full Era-2-pv rebuild from scratch), runs over budget — operator should monitor and halt at Step 3 if it exceeds 3 h, then ask the user.

---

## Critical files for implementation

- `/home/shawn/Code/map-reader-llm/planning/phase3a-verifier-recovery-runbook.md`
- `/home/shawn/Code/map-reader-llm/planning/paper-writeup-continuity.md`
- `/home/shawn/Code/map-reader-llm/scripts/run_per_arch_leaderboards.sh`
- `/home/shawn/Code/map-reader-llm/scripts/build_combined_leaderboard.sh`
- `/home/shawn/Code/map-reader-llm/reports/phase3a-verifier-completeness-audit-2026-05-03.md`
