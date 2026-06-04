# Phase 3 decomposition investigation — phase3a ↔ pv-diag-384, and the phase3a-high / phase3a-replication / phase3c shape

**Date**: 2026-06-05 (Session 100 close).
**Author**: two read-only `general-purpose` exploration agents, commissioned to set up the next session's Batch D/E work. **Status of claims**: agent-produced and **file-path-anchored** — treat as pointers to verify at the named sources, not authorities (anti-confabulation). Both agents flagged unresolved anomalies (see § Anomalies) which must NOT be silently resolved.
**Why this exists**: Session 100 flagged a surprising "cross-run sourcing" signal (phase3a evals appeared to score pv-diag-384 detections). These two investigations resolve it and characterise the four Era-1 phase3 runs for manifest decomposition (sub-step 3b/3c).

---

## Headline resolution — the phase3a ↔ pv-diag-384 "mystery" is a NAME COLLISION

There is **no detection-data linkage** between `retest-phase3a` and `pv-diag-384`. They are different corpora, tile sizes, and bounds:

- **`retest-phase3a`** = a distinct Era-1 run: 340 tiles, 512px, curator GT, H3 consensus voting. It has its **own** 180 proposer passes under `outputs/retest/phase3a/` (2 tracks × 3 temperatures × 30 runs). Its real analysis is the consensus sweep under `results/retest/phase3a-consensus/`.
- **`results/phase3a-text-matrix/` + `results/phase3a-image-matrix/`** = a *separate, name-colliding* artefact set. Every sampled `evaluation.json` there scores `outputs/h11/pv-diag-384/...` detections against `inputs/vectors/bounds/384/full_evaluation_bounds.geojson` with `n_tiles: 487` — i.e. **pv-diag-384's Era-2 / 384px / 487-tile scope**. These belong to **pv-diag-384** (Batch E), not to retest-phase3a. `results/retest/retest-production-summary.md` (line 278) itself calls them "the Era 2 `gemini-3-flash` consensus sweeps".

So the Session-100 worry ("retest-phase3a may be an analysis of pv-diag-384") was triggered by the bare string "phase3a" colliding across two unrelated artefact families. **Both exercise consensus voting (H3); only the label is shared.**

**Consequence for pv-diag-384 GAP-7 completion**: the `phase3a-text-matrix` / `phase3a-image-matrix` evals (Era-2/487, **WITH MCC** — verified) are exactly the consensus-sweep material that pv-diag-384's Batch E completion should declare (as a 3c analysis and/or operating-point conditions).

---

## The four Era-1 phase3 runs — all → sub-step 3c analyses (no MCC conditions exist)

All four (`retest-phase3a`, `retest-phase3a-high`, `retest-phase3a-replication`, `retest-phase3c`) are **absent from `results/run-conditions.json` → decomposition** (undecomposed), all Era-1 / 340 / 512px / curator GT, and share a decisive property:

> **ZERO per-condition `evaluation.json` files with MCC exist for any of them.** Every evaluable artefact is an **F1-only aggregate sweep / pairwise / permutation analysis** (`*-consensus-sweep.json`, `diversity-analysis-report.json`, `consensus-analysis-report.json`). None carries `tile_classification` / `mcc` / a tp-tn-fp-fn confusion matrix. The conditions schema's hard requirement for non-null `mcc` + confusion **cannot be satisfied from existing artefacts.**

Per-run recommendation (agent-derived):

| run | what it is | passes on disk | eval shape | recommendation |
|---|---|---|---|---|
| `retest-phase3a` | H3 consensus-voting sweep, K=30, 2 tracks × 3 temps | 180 (`track1-image` + `track2-text`, `T{0.3,0.7,1.0}`/run_1..30) | `results/retest/phase3a-consensus/{track1-image,track2-text}/` — F1 sweep summaries, **no MCC** | **3c analysis** + record the 180 passes; do NOT attach the `phase3a-*-matrix` evals (those are pv-diag-384's) |
| `retest-phase3a-high` | H3 HIGH-thinking temp sweep (T=0.3/0.7/1.0), K=30 | text-track only (`track2-text`, run_1..30 × 3 temps). **`track1-image` NEVER RAN** (only `study_manifest.json`) | `results/retest/phase3a-high-text/*.json` — consensus sweep + pairwise, **no MCC** | **3c analysis** (text); record `track1-image` as **planned-but-unexecuted** (no passes/conditions — do not invent) |
| `retest-phase3a-replication` | clean `high` vs `minimal` thinking at T=0.7, K=30, text — built because the original phase3a HIGH/min both accidentally used minimal | 60 (`high/`, `minimal/`, run_1..30) | `results/retest/phase3a-consensus/replication/consensus-analysis-report.json` (`study_dir = outputs/retest/phase3a-replication`) — F1 sweep, **no MCC** | **3c analysis** + record the 60 passes |
| `retest-phase3c` | H9 diversity study (does cross-pass diversity beat identical passes?) | 45 pools (`track1` 25, `track2` 20), each a PASS-variant `h9-{A..E}-{p,v,img,t}N` with run_1..5 | `results/phase3c-diversity/{track1-image,track2-text}/diversity-analysis-report.json` / `diversity-consensus-sweep.json` — condition-level F1 means + permutation p, **no MCC** | **3c analysis** + record the 45 pools as passes. **H9 was REJECTED** (no diversity mechanism gives a significant gain) |

**phase3c pool naming decoded** (verified vs `diversity-analysis-report.json` `study_conditions`): the `h9-{A..E}` letter is the diversity **condition**; the suffix is the **pass variant** within that condition's 5-pass set. A = baseline (5 identical), B = text/instruction-variant diversity (`_v1..v5.md`), C = image/hard-negative diversity (Track 1 only), D = temperature diversity (0.4/0.55/0.7/0.85/1.0), E = combined. Each `h9-X-yN` dir is ONE pass variant holding `run_1..5`. The registry (line 159) already notes "h9-A-p1..p4 are PASSES, not conditions (GAP-6)".

**The trap to avoid**: do NOT mint 3b conditions from these proposer pools — that mistakes passes for conditions (GAP-6). 3b conditions would require fresh tile-level MCC scoring at chosen operating points (new compute), which does not currently exist.

---

## ⚠ Anomalies flagged by the agents — DO NOT silently resolve

1. **Model contradiction (Era-1 retest provenance)**: all sampled `outputs/retest/phase3a*/**/*.meta.json` record `configuration.model: "gemini-3-flash"`, but `results/retest/retest-production-summary.md` (line 6, and lines 277–278/318/345) repeatedly states the Era-1 retest **Model** is `gemini-2.0-flash` and frames Era-1 as the `gemini-2.0-flash` run distinct from the Era-2/3 `gemini-3-flash` work. **These cannot both be true.** Resolve before recording any model-of-record for the phase3/phase2 Era-1 retest runs. (Per E57, trust per-item `model_version` → `config.model` over prose docs — but Era-1 metas are GAP-9 with no per-item, so `config.model = gemini-3-flash` is the only meta signal, which still conflicts with the prose. A genuine conflict, not auto-resolvable.) Pool meta git commits: `5a57f586` / `195fa64a` (2026-03-15/16).
2. **phase3c thinking-level doc conflict**: `phase3c-comprehensive-results-report.md` says "All conditions use HIGH thinking"; `cross-track-comparison.md` says "Both tracks used MINIMAL". Per-run metas record `thinking_level=high` (agree with the comprehensive report). `cross-track-comparison.md`'s "MINIMAL" prose appears stale/wrong — correct it; don't trust its parameter prose.
3. **Era-1 batch metas have placeholder timing**: `duration_seconds` ≈ 0.000156 with start≈end despite `items_processed: 340`. Consistent with batch-API timing placeholders (the runs are real — `execution_stats`/`usage_stats` populated) — but do not read those timestamps as wall-clock.

---

## Key anchor paths (re-verify here)

- `results/run-facts.json` → `facts.{retest-phase3a,retest-phase3a-high,retest-phase3a-replication,retest-phase3c,pv-diag-384}`
- `results/run-registry.json` lines ~143–160 (directory_path mappings + the GAP-6 "PASSES not conditions" note)
- `results/run-conditions.json` → `decomposition` (the four phase3 runs are MISSING = undecomposed)
- `outputs/retest/phase3a/{track1-image,track2-text}/T{0.3,0.7,1.0}/run_*/detections_*.meta.json`
- `outputs/retest/phase3a-high/track1-image/study_manifest.json` (only file — track never ran); `.../track2-text/T0.7/run_1/*.meta.json`
- `outputs/retest/phase3a-replication/{high,minimal}/run_*/*.meta.json`
- `outputs/retest/phase3c/{track1-image,track2-text}/h9-*/run_*/*.meta.json`
- `results/retest/phase3a-consensus/{track1-image,track2-text,replication}/consensus-analysis-*.{json,md}`
- `results/retest/phase3a-high-text/{phase3a-high-text-consensus-sweep.json,phase3a-high-text-pairwise.json}`
- `results/phase3c-diversity/{track1-image,track2-text}/diversity-*.{json,md}`, `phase3c-comprehensive-results-report.md`, `cross-track-comparison.md`
- `results/phase3a-text-matrix/`, `results/phase3a-image-matrix/` — **pv-diag-384's** Era-2/487 consensus sweeps (HAVE MCC); detections under `outputs/h11/pv-diag-384/...`
- `results/retest/retest-production-summary.md` (model + Era framing — see Anomaly 1)
