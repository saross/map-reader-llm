# Session 95 — overnight autonomous work summary

**Date**: 2026-05-31 (overnight, autonomous).
**Mandate**: you approved the zero-API sequence + ready-work and asked me to run
it all autonomously overnight, plus `/observe` the diversity-dividend finding.
**Compute**: all scoring on **zbook** (sapphire left untouched). **Zero API spend**
— everything was materialisation, eval-only re-scoring, authoring, and archiving.
**Git**: 11 commits, all pushed; local + zbook both at `169d6602`, 0 behind/ahead.

---

## TL;DR — all six tasks done

| # | Task | Status | Headline |
|---|---|---|---|
| 1 | `/observe` diversity dividend | ✅ | Obs 333 (`44c0fa91`) |
| 2 | §2 #4 score consensus-PV | ✅ | 12 conditions; verifier-t-pilot F1 **0.856** |
| 3 | §2 #3 pv-diag-384 PV quadrants | ✅ | single-run-PV 0.718, consensus-PV **0.861** |
| 4 | Ready-work #3 author `run-conditions.json` | ✅ | 36 conditions, 0 extraction errors |
| 5 | Ready-work #4 archive n1 evals | ✅ | `384px-outstanding/` only (ambiguous held) |
| — | Ready-work #1 verified subsets (earlier this session) | ✅ | 16 sets; verifier benefit now measurable |
| — | Ready-work #2 single-pass deltas (earlier) | ✅ | 63 passes; single↔consensus delta for 4 runs |

The **performance-shape 2×2** is now substantially filled with standardised
(14-buffer + MCC) numbers. See the results below.

---

## Results

### Ready-work #1 — verified subsets (Decision 1A) measure the verifier

Filtering each pv-384/512 verifier output to its `verified:true` subset turned the
flat proposer baseline into a real verifier signal:

| | full candidate set (572) | accepted subsets (verified:true) |
|---|---|---|
| F1@20 | 0.403 (identical across configs) | **0.471 – 0.531** |
| MCC | 0.030 (≈ no skill) | **0.315 – 0.445** |

### Ready-work #2 — single↔consensus dividend (the `/observe` finding)

| run | single-pass F1@20 (n) | consensus sweep | dividend |
|---|---|---|---|
| e47-propose-brief | 0.364 ± 0.019 (5) | t1 0.167 → t5 **0.714** | **+0.35 huge** |
| n1-outstanding-384 | 0.530 ± 0.057 (17) | 0.47 – 0.68 | moderate |
| retest-h11-single-pass (T=0) | 0.503 ± 0.004 (10) | t1 0.493 → t10 0.554 | +0.05 tiny |
| consensus-384-t1-0 (T=1.0) | 0.384 ± 0.010 (30) | t1 0.304 → t5 0.471 | +0.09 |

**Obs 333**: the dividend tracks proposer diversity; single-pass σ is a proxy.
T=0's near-zero σ ⇒ near-zero dividend.

### §2 #4 — consensus-PV (12 conditions)

| condition | n | F1@20 | MCC |
|---|---|---|---|
| verifier-t-pilot T0.5 vote4_prob0.20 | 371 | **0.856** | 0.771 |
| verifier-t-pilot T0.0 / T1.0 | 369 / 370 | 0.851 / 0.842 | 0.778 / 0.756 |
| h8-v2 scale-4 (greedy / wbf) | 251 / 297 | 0.737 | 0.803 / 0.805 |
| h8-v2 wbf scale-8 | 285 | 0.722 | 0.813 |
| h10 pool_160 vt4 | 232 | 0.722 | 0.760 |
| 55maps generalisation (5 runs) | 3865–4680 | 0.508 – 0.629 | 0.626 – 0.693 |

### §2 #3 — pv-diag-384 PV quadrants (the closest-to-complete 2×2)

| quadrant | n | F1@20 | MCC |
|---|---|---|---|
| single-run-PV (1of5 union → verified) | 649 | 0.718 | 0.750 |
| consensus-PV (4of5 → verified) | 385 | **0.861** | 0.774 |

Verifying the higher-quality 4of5 consensus beats verifying the FP-heavy 1of5
union — both materialised from `consensus/flash-high-text-1of5.geojson` + cached
probabilities at **prob_t=0.20** (the documented operating point — see flags).

### Ready-work #3 — `run-conditions.json` (36 conditions authored)

e47 (5 consensus + 1 baseline), n1 (15 consensus), retest-h11-single-pass (10
repeated-single-pass), c384 (5 consensus). All extract cleanly via the generator
(`build_extraction_context` + `extract_conditions`), 0 bad-metrics, explicit
`eval_path` → this session's standardised re-scores.

---

## ⚠ Flags for your review (decisions I made or deferred)

1. **pv-diag-384 `prob_t=0.20`** — I used 0.20 as the verifier operating point
   (matches gs-v2 / verifier-t-pilot). It's a documented, reversible default;
   confirm or change. Re-materialising at another threshold is ~1 min.
2. **55maps-text-high-t0.3 GT** — it was scored against the **non-reviewed** GT
   (`student-mounds-55maps.geojson`, 4770 feats) while the other four use the
   reviewed GT (4746). I preserved each run's original GT rather than silently
   harmonise. Recommend re-scoring t0.3 against the reviewed GT for comparability.
3. **e47 run_5 dual pass** — `run_5/` holds a real dated pass (1694 feats, ~1060 s)
   **and** a zero-duration `run05` copy (1403 feats). All `run_NN` files are
   zero-duration reorg copies; the two dated files are the real-duration
   originals. Obs 333 / the single-pass set use the canonical 5 (excluding the
   spurious copy). The e47 baseline condition uses the separate `text-baseline`,
   so it's unaffected — but the run_5 provenance is worth a glance.
4. **n1 ambiguous archive dirs** — only `results/paper-eval/n1/384px-outstanding/`
   was archived (you authorised it). Held for joint review per your Q4:
   `384px/` + `384px-all-buffers/` (ambiguous run). Confirmed NOT n1 and left
   alone: `512px/` + `512px-all-buffers/` (they're `retest-phase2*` — P2a–P2d).
   One naming caveat: the archived `flash-text-minimal` dir = the run's
   `brief-text` pool (prompt-name convention difference).
5. **run-conditions.json scope** — I authored exactly the agreed grain. NOT yet
   done (held for your go-ahead):
   - Single-pass conditions for the **consensus** runs (e47/n1/c384) — the
     Decision-2 "BOTH" half. Their passes are already scored; adding them is cheap.
   - n1's two K=1 pools (`pro-image-medium-t07`, `pro-text-medium-t07`) are
     pool-only (no consensus possible) → 1 single-pass condition each under Dec 2.
   - **Manifest regeneration + `GENERATOR_VERSION` bump** (0.2.0 → next) — a
     deliberate step per the Session 94 beacon, NOT run here.
6. **Syncthing churn (environmental)** — 17 git-tracked binaries under `archive/`
   and `inputs/tiles_384/` show as modified mid-session and intermittently fail
   `git hash` with "short read". Cause: Syncthing is rewriting them concurrently.
   I left them untouched and used explicit pathspecs throughout, so no commit
   swept them. Worth deciding whether those binaries should be git-tracked **and**
   Syncthing-synced (a known footgun).

---

## Beacon correction worth noting

The Session 94 handoff said **consensus-384-t1-0 "crashed on NaN source_tile /
unscored"**. Re-checking the source: it is **fully scored** (14 buffers + MCC) in
`outputs/.../voting/eval-t{1..5}/`, git-tracked, written during Batch A. No fix
was needed (Q2 dissolved). The beacon was stale.

---

## Commits (this overnight run, newest first)

```text
169d6602 feat(manifest): author 4 runs into run-conditions.json (#3)
d18b963d archive(evals): n1-outstanding-384 superseded paper-eval (#4)
7861b6d0 eval(rescore): pv-diag-384 PV quadrants (§2 #3)
1f1bbd36 feat(pv-diag): materialise pv-diag-384 PV quadrants (§2 #3)
8b6c25f3 eval(rescore): consensus-PV scores (§2 #4, 12 conditions)
0e980055 chore(rescore): consensus-PV worklist (§2 #4)
44c0fa91 docs(reflection): Obs 333 — consensus dividend tracks proposer σ
```

(plus the earlier #1/#2 commits: `4d51c07d`, `dcd849df`, `78571094`, `02f1493b`.)

## Suggested next steps

1. Adjudicate the flags above (esp. the t0.3 GT and the pv-diag prob_t).
2. Decide on the Decision-2 single-pass-conditions completion for e47/n1/c384.
3. When ready, regenerate `runs-manifest.json` + bump `GENERATOR_VERSION`.
4. Continue the 3b decomposition for the remaining runs (the worklist).
5. Consider `/handoff` to fold this into `paper-writeup-continuity.md`.
