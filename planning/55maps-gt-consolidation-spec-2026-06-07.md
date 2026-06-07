# 55-map ground-truth consolidation + canonical-GT re-score — spec

**Created**: 2026-06-07 (Session 105)
**Status**: COMPLETE 2026-06-07 (O1/O2/O3 signed off; analysis, docs, AND manifest
registration all done) — see § Progress.

## Progress (2026-06-07, Session 105)

**DONE (committed `bb7d5279`→`228e8675`):**

- **T2a/b/c — engine + driver + sweep.** `compute_corrected_f1_multi_buffer.py`
  gained an additive `--compute-mcc`; new driver
  `scripts/score_55maps_extended_gt_canonical.py` scored the 7 cells (14-buffer
  corrected-F1 + tile-MCC) vs the canonical extended GT on zbook.
  **Validation gate PASSED**: 5 §4b-anchored cells reproduce corrected-F1 @ 50 m
  to ~7 d.p.; below-50 m equals the Track-1 manifest exactly. Outputs
  `results/55maps-extended-gt-2026-06-07/`.
- **T2d — canonical-GT threshold permutations.** k3 > carried k4 for all three
  text configs, p<0.001 @ 50 m (TH7 +0.027, T03 +0.012, TM +0.030).
  `threshold-permutations/`.
- **Tests.** 6 tier-1 tests (`tests/test_corrected_f1_mcc_extension.py`); no
  regressions.
- **Docs (D1/D2).** Two-reference section in `55maps-generalisation-runs.md`;
  changelog entry in the deployment-oracle findings doc.

**DONE (committed `9b96a99f`→`da2cf355`):**

- **T2e — manifest minting.** 7 `…-canonical-gt` conditions registered (224→231,
  ALL VALID, 0 existing changed) via the generated-manifest flow (no hand-edit):
  `adapt_track2_evals_for_manifest.py` (Track-2 `summary.json` → generator-
  compatible `evaluation.json`) + `add_canonical_gt_conditions.py` (specs into
  `run-conditions.json`) + `generate_post_run_report.py --all --write`. Drift-check
  **0 fail**; the 5 55maps runs PASS. (O1's `@` suffix → `-canonical-gt`; the
  schema's `condition_id` pattern forbids `@`.)
- **T1b — archived** the superseded historical GT-eval variants →
  `archive/55maps-superseded-gt-evals/` (none referenced pre-move; `git mv`).
- **T1c — `_note`** canonical-track cross-reference added to each of the 4 run
  decomposition entries in `run-conditions.json`.
**Purpose**: Lock the design for two side-by-side evaluation references for the
five 55-map generalisation runs — a **historical (as-measured)** track and a
**canonical extended-GT (gold-standard-substitute)** track — so the paper can
report the canonical track while the historical record stays complete and
up-to-spec. All decisions below are source-verified against the artefacts named.

---

## 1. Locked decisions (from discussion, 2026-06-07)

1. **Two references only.** Report against (a) the reviewed student GT and
   (b) the canonical extended GT. The earlier ad-hoc per-run manual corrections
   (`human-reviewed-corrected`, `cleaned-gt-evaluation`) are **folded into the
   canonical** (which already unions them) and **archived** — *not* reported as a
   third column.
2. **Full buffer set always.** Every evaluation computes the entire 14-buffer
   sweep `[5,10,15,20,25,30,35,40,45,50,75,100,125,150]`. Headline at **50 m**
   (jitter-matched to the ~25 m student digitisation error, Obs 260). No
   truncation to `[50…150]`.
3. **Per-buffer phantom gating (the §4b rule), then MCC.** A phantom enters the
   extended GT at radius R only if its min-ring `buffer_metres ≤ R`; the ">150 m"
   sentinel shell is excluded at every R. We do **not** count phantoms we cannot
   localise at the scoring radius. MCC is computed under the *same* gated GT.
4. **Compute on zbook, 14 cores** (sapphire in use). Leave 2 cores free.
   $0 — no API. Verify zbook load before launching.

---

## 2. The two ground truths

| | file / source | n | role |
|---|---|---|---|
| reviewed student GT | `inputs/vectors/references/student-mounds-55maps-reviewed.geojson` | 4,746 | historical / as-measured (bare `…-55maps.geojson` = 4,770; review removed 24) |
| canonical phantom GT | `results/deployment-oracle-2026-06-06/canonical-gt/canonical-review.csv` | 773 | reviewer-confirmed extra mounds, deduped, **unions prior + today's corrections** (`build_canonical_gt.py:14,57-69`) |
| **canonical extended GT** | reviewed student + gated phantoms | 4,746 + ≤773 per R | **paper reference (Track 2)** |

---

## 3. Engine — single trusted engine, both tracks

Both `compute_corrected_f1_multi_buffer.py` and `evaluate_detections.py` share
the F1 core `calculate_f1_internal`. `evaluate_detections.py` additionally emits
tile-MCC (`calculate_tile_classification`, `--compute-mcc`). Therefore:

- **F1 + MCC** come from **`evaluate_detections.py`** for *both* tracks.
- The **gated extended GT** is materialised per buffer by **reusing
  `build_phantom_gdf` / `build_extended_gt`** from `compute_corrected_f1_multi_buffer.py`
  (the proven §4b gating — not a re-implementation).
- Between Track 1 and Track 2 **only the GT changes**; engine, matching, scoping,
  bootstrap and buffers are identical → clean experimental control.

**Hard validation gate.** Before trusting Track 2, the unified pipeline must
reproduce §4b's corrected-F1 @ 50 m to **4 d.p.** (carry-forward = 0.815, joint
oracle = 0.848, and the per-config row of §4b). If it does not match, stop and
reconcile the gating/scoping before proceeding.

Rejected alternative: a single static extended-GT geojson scored across all
buffers (counts every phantom at every radius) — methodologically wrong, per
decision §1.3.

---

## 4. Track 1 — historical record (mostly DONE; consolidate + document)

The five carried conditions are **already** scored at the full 14-buffer sweep +
tile-MCC vs the reviewed student GT — `results/rescore-2026-05-31/<run>/verified*/evaluation.json`
(the source the manifest conditions cite). Verified: 14 buffers + `tile_classification`
(MCC 0.626–0.693). So **no recompute** is needed for Track 1.

Remaining Track-1 work ($0, no compute):

- **T1a.** Confirm all 5 `rescore-2026-05-31` evals are spec-complete (14-buf + MCC,
  GT = reviewed student). [check]
- **T1b.** Archive the superseded historical variants to
  `archive/55maps-superseded-gt-evals/`: `55maps-cleaned-gt-evaluation/`,
  `55maps-*/human-reviewed-corrected/`, `55maps-*/mcc/`,
  `condition-scoring-backfill-2026-05-30/55maps-*`. (Archive, never delete.)
- **T1c.** Add `gt_reference: student-mounds-55maps-reviewed.geojson` + `_note`
  (pointing to the canonical track + findings doc) to the 5 manifest conditions.

## 5. Track 2 — canonical extended-GT re-score (NEW compute) — **7 cells**

Re-score against the **canonical extended GT**, full 14-buffer + MCC, per-buffer
gated. Output → `results/55maps-extended-gt-2026-06-07/`. All detections already
exist → **$0, no API**.

**The 7 cells** (4 carried configs + oracle + 2 threshold-completion k3s):

| # | config | k | detection set | role | §4b gate @50 m |
|---|---|---|---|---|---|
| 1 | text-high T0.7 | 4 | `outputs/55maps-text-high-generalisation/verified/verified_detections.geojson` | carry-forward | 0.815 |
| 2 | text-high T0.7 | 3 | `results/deployment-oracle-2026-06-06/k3-scoring/55maps-text-high-generalisation/k3_verified.geojson` | threshold (NEW) | — (per-run §1 = 0.850) |
| 3 | text-high T0.3 | 4 | `outputs/55maps-text-high-t0.3-generalisation/verified/verified_detections.geojson` | config | 0.836 |
| 4 | text-high T0.3 | 3 | `results/deployment-oracle-2026-06-06/k3-scoring/55maps-text-high-t0.3-generalisation/k3_verified.geojson` | **oracle** | 0.848 |
| 5 | text-min | 4 | `outputs/55maps-text-min-generalisation/verified/verified_detections.geojson` | config | 0.783 |
| 6 | text-min | 3 | `results/deployment-oracle-2026-06-06/k3-scoring/55maps-text-min-generalisation/k3_verified.geojson` | threshold (NEW) | — (per-run §1 = 0.822) |
| 7 | image | 3 | `outputs/55maps-image-generalisation/verified/verified_detections.geojson` | config (carried) | 0.799 |

(The `55maps-generalisation` superseded original = config-duplicate of #1; kept
for the historical record, not re-analysed in Track 2.)

- **T2a.** Wrapper materialises gated extended GT per buffer (reuse
  `build_phantom_gdf`/`build_extended_gt`) and scores each cell via the **same
  library calls** `evaluate_detections.py` uses (`calculate_f1_internal`,
  `calculate_tile_classification`, bootstrap CIs) → identical numbers by
  construction. One gated GT per R, all 7 cells scored against it.
- **T2b.** Run on zbook (14 workers). Assemble 14-buffer F1+MCC sweep per cell.
- **T2c.** **Validation gate** (§3): the 5 gated cells with §4b values reproduce
  corrected-F1 @ 50 m to 4 d.p. (go/no-go). Cells 2 & 6 sanity-checked vs §1
  per-run values (canonical ≠ per-run GT, so close-not-equal expected).
- **T2d.** k3-vs-k4 **paired permutation against the canonical GT** for the three
  text configs (T0.7, T0.3, text-min) via `paired_permutation_corrected_55maps.py`
  — moves §1's central claim onto the canonical GT (was per-run).
- **T2e.** Author the 7 cells into the manifest as `…@canonical-gt` conditions
  (O1) + cross-link findings doc.

NB §4b's oracle/config/joint deltas already exist @ 50 m corrected-F1; Track 2
extends to all 14 buffers + MCC and adds the canonical-GT threshold permutations.

## 6. Downstream documentation

- **D1.** `docs/methodology/55maps-generalisation-runs.md` (dated 2026-06-02,
  pre-oracle) — add revision banner + a section on the two-track design, the
  canonical GT, and the carry-forward→oracle gap.
- **D2.** `results/deployment-oracle-2026-06-06/deployment-oracle-findings.md` —
  add a changelog entry pointing to the Track-2 full sweep + MCC.
- **D3.** Continuity beacon + an Obs entry.

---

## 7. Resolved (signed off 2026-06-07)

- **O1 — manifest layout — RESOLVED:** new condition label suffix per cell
  (`…@canonical-gt`), explicit and greppable; **include the oracle cell**.
- **O2 — validation tolerance — RESOLVED:** 4 d.p. on corrected-F1 @ 50 m.
- **O3 — Track 2 scope — RESOLVED:** **7 cells** (§5) — both k3 and k4 for the
  three text configs (the 4-of-5 vs 3-of-5 argument needs both), plus image
  carried and the oracle. **Re-run the k3-vs-k4 paired permutation against the
  canonical GT** for the three text configs (T2d). All *other* vote thresholds
  (2-of-5, 5-of-5, full sweep) stay deferred `_ignored_evals` per the
  decomposition rule.

---

## 8. Execution order (after sign-off)

1. T1a check → T2a wrapper → T2b/T2c (the validation gate is the go/no-go).
2. If gate passes: T2d author + T1b archive + T1c notes.
3. D1–D3 docs.
4. Commit in focused units; push.

Compute: zbook, 14 workers, $0. Verify host load first with
`scripts/check-compute-hosts.sh` and `hostname`. No API.
