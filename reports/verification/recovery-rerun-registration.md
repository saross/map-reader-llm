# Pre-execution registration — E71 dead-tile recovery rerun

> **Last revised**: 2026-07-30 (original publication). See
> [§ Changelog](#changelog) for revision history.

**Status**: `planned` — **registered before any API call** (charter
execution rule 10). Execution is gated: dry-run, `/audit-config`, and
per-batch PI cost approval must all pass before spend. **No API call is
made under this registration until the PI approves the gate.**

**Authority**: PI ruling 2026-07-30, verbatim "Erratum + fixes + rerun to
sweep up failed tiles (through usual API-gate process including dry-run,
approval, etc.)" (`reports/verification/phase2-rulings-2026-07-30.md`
§ 2.2); E71 remediation item 3.

## 1. Scope — the worklists

Derived at `reports/verification/recovery-rerun-worklists.json`
(`scripts/derive_recovery_worklists.py`): dead tiles = corpus membership
minus the detection GeoJSON's `processed_tiles` (charter § 4 authority
#1), sidecars as corpus definition and cross-check.

| group | passes | dead tiles | model |
| --- | --- | --- | --- |
| **live-pv-diag-t0.0** (feeds two evaluated conditions) | 6 | **143** (16/34/34 image; 19/20/20 text) | `gemini-3-flash-preview`, HIGH thinking, T=0.0 |
| n1-outstanding-pro (E57-quarantined corners, off-board) | 6 | **136** (15/19/17 image; 29/29/27 text) | `gemini-3.1-pro-preview`, HIGH thinking, T=0.0 |
| single-tile shortfalls | 3 | **9** (e47 ×7; h12-v2 ×1 ×1) | `gemini-3-flash-preview` |
| ~~flash35-pv-2x2 run_3~~ | 0 | **0 — dropped** | — |

**Total: 288 tiles across 15 passes.**

Notes recorded at derivation:

- `flash35-pv-2x2::flash35-min-text-1of10::run3` **drops out**: its
  second segment GeoJSON (2026-06-11) already covers the missing tile —
  the manifest shortfall was bookkeeping only (now fixed by the v0.6.0
  generator), not missing data.
- `e47-propose-brief::propose_brief-text::run4` is messier than the
  triage grain: GeoJSON 480 processed, sidecar dual-lists 6 tiles as both
  completed and failed (the `clean_meta_failed_items` class), meta says
  486. The GeoJSON governs (evaluations consume it): **7 dead**.

## 2. Mechanism

The attested recovery path for the era's sole failure mode (output
truncation — working-notes Session 53; E70): re-run each dead tile at the
safe-mode reduced `max_output_tokens` via the `--patch-tiles` machinery,
which since the `merge_meta` fix (`scripts/lib_batch_api.py:2343`) merges
`completed_items[]`/`failed_items[]` and appends `recovery_history` — so
this rerun also repairs the E70/E71-class bookkeeping on every pass it
touches. Real-time (not batch) — 288 calls do not justify batch latency.
Pre-recovery metas, sidecars, and GeoJSONs are preserved (archive, never
delete) before merge.

## 3. Post-recovery pipeline (all US$0, sapphire/zbook)

1. Re-materialise the consensus pools for the two live conditions
   (`pv-diag-384::flash-high-image-n5-image-t0.0-consensus-1of3`,
   `pv-diag-384::flash-high-text-n5-text-t0.0-consensus-3of3`) and
   re-evaluate at the standard 14-buffer + MCC protocol.
2. **Preserve and compare** (project policy): pre-recovery evaluations
   archived; pre/post deltas reported. The pre-recovery numbers carry
   19–34 artificial zero-detection tiles (E71).
3. Regenerate manifests (the v0.6.0 completed-count semantics will pick
   up the recovered counts); drift-check must pass.
4. Ledger rows for the two live conditions' corrected evaluations;
   `conditions-manifest` rows update.
5. n1-outstanding rows: coverage completed for the preserved exploratory
   corners; no board membership change (E57's replacement stands).

## 4. `predicted_outcome`

Recovering dead tiles can only add detections to the affected passes.
For the two live conditions, tiles currently scored as artificial zero
detections gain real model output: ground-truth mounds there convert
from artificial false negatives to true positives or genuine false
negatives, so **recall and F1 are expected to rise or hold, not fall**;
precision direction is unknown (new false positives possible). Magnitude
unknown; both cells are exploratory diagnostics, so no registered claim
moves. The n1-outstanding recovery completes coverage of preserved
exploratory rows only. If a tile fails again even at safe-mode budget,
it is recorded as permanently failed (the E70 precedent: one such tile
exists in the patch campaign) and the condition's coverage note says so.

## 5. Cost estimate (to be re-verified at the gate per rule 12)

288 real-time calls: 152 Flash-preview (HIGH thinking) + 136
Pro-3.1-preview (HIGH thinking).

- Flash HIGH ≈ US$0.005–0.01/tile (token-load-audit basis) → **~$1–2**.
- Pro HIGH ≈ US$0.05–0.15/tile → **~$7–20**.
- Retries/safe-mode re-attempts headroom ×1.3.

**Estimate: ~US$10–25; worst case ~$30.** Within the run-it-now budget
envelope ("a few hundred dollars" bar — charter § 10 item 7(c));
per-batch approval still required before launch.

## 6. Gate checklist (all outstanding)

- [ ] PI approves scope and spend (model, mode, call count, cost above)
- [ ] Dry-run over the worklists (no API)
- [ ] `/audit-config` READY verdict
- [ ] Launch; per-group progress reported; post-recovery pipeline § 3

## Changelog

### 2026-07-30 — Original publication

Registered with worklists committed, before any API call, per rule 10
and PI ruling § 2.2. Awaiting the § 6 gate.
