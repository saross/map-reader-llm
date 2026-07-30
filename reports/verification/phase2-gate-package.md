# Phase 2 (C3 provenance) — GATE 2 package

> **Last revised**: 2026-07-30 (original publication). See
> [§ Changelog](#changelog) for revision history.

**Status**: **GATE 2 PASSED 2026-07-30** (PI rulings recorded at
`planning/audit-charter.md` § 10 item 8: dispositions accepted at the
table grain; ledger-supersession convention deferred to the Phase 5
monitor design; Phase 3 unlocked). Phase 2 executed Sessions 120–121
(C3 re-derivation overnight on sapphire; triage, rulings, and the
landing sequence in Session 121). PI morning rulings, verbatim:
`reports/verification/phase2-rulings-2026-07-30.md`.

## 1. Headline

**C3 provenance: 1,514 of 1,534 ledger rows VERIFIED, 20 FLAGGED — and
every FLAGGED row now has a landed or registered disposition.** The
conditions manifest verified 100 % clean. Of the 147 field-level
mismatches the re-derivation surfaced, 127 vindicated the manifest (the
previously-undisclosed `--patch-tiles` recovery campaign, now E70), 17
were genuine (the `n_tiles_processed` dual semantics + GAP-8 + segment
scoping, now E71, generator fixed), and 3 sided with the source.

## 2. What landed in the Session 121 sequence (all committed and pushed)

1. **Errata wave E62–E71** + five dated correction/clarification blocks
   (E36, E16, E20, E40, E55) — commit `2159d25b4`. The medium
   thinking-level limb SPLIT per ruling 1a (E62 narrowed; E69 for the
   Flash-verifier exploration; E40 clarified for the endpoint-forced
   Pro-verifier sites). E64(iii) cites the **computed** materiality
   figure: **2.21 %** cluster-level label heterogeneity (153,102
   clusters, 47 pools;
   `reports/verification/apparatus/cluster-label-heterogeneity-2026-07-30.md`),
   superseding the 17.2 %/~21 % subtype-share proxies.
2. **Working-notes riders Obs 372/373** (append-only, pointer lines at
   the original sites) and the two report corrections
   (`experimental-progression.md`, `gs-tile-pool-mapping-2026-05-28.md`)
   for the "1 of 10 survived FDR" misreport (correct figure 0).
3. **Census closure**: all 13 UNLICENSED pairs carry dated `resolution`
   objects (E62 / E69 / E40-as-clarified). Commitment ledger:
   CMT-0109 waived (E68); CMT-0047 and CMT-0106 **discharged** — now
   **404 discharged / 90 waived / 208 open**.
4. **Generator v0.6.0** (E71/E55 wave): `n_tiles_processed` uniformly
   counts COMPLETED items via the C3-validated union-of-`completed_items`
   rule; new `n_tiles_dispatched` field (schema extended); GAP-8
   resolved; E55's `run.log` provenance promise implemented;
   `pv-diag-256` purpose populated (ruling 1b). Regen diff audited:
   exactly 19 rows changed, zero status changes, ALL VALID; 58 tier-1
   tests green. First-cut lesson recorded in § 5.
5. **The family-FDR correction — registered, then computed**
   (`reports/verification/family-fdr-registration.md`;
   `results/family-fdr/`). H1's primary = registered contrast CMT-0106,
   **executed for the first time** under a pre-committed reconstruction
   rule: Δ = +0.0238 text-over-image, CI95 [−0.0104, +0.0585],
   **p = 0.1774 — null**. **Rejection set {H2, H3, H7}** — the smaller
   of the two pre-committed possibilities. The outcome-blind selection
   resolved the outcome-material fork to the conservative branch: under
   the draft's default (the p = 0.006 level pair) H1 would have
   survived. H2 carries the falsified-directional rider everywhere.
6. **The E71 recovery rerun — EXECUTED, including PI-directed deep
   sweeps** (dry-run + `/audit-config` READY first; all flex per the
   standing instruction): first pass 255/288, then sweep A (10+10
   ladder) **+10 more — final 265/288 (92.0 %)**; sweep B (safe mode
   halved to 1024) recovered nothing. The PI's pre-gate
   model-consistency check caught that the six "pro-*" shortfall
   passes are the E57 mis-dispatched FLASH corners (all-Flash run,
   ~US$3–5 total incl. sweeps). **The permanent residue is 6 unique
   tiles** (23 pass-level failures; the worst fails in 9 independent
   passes across pools and modalities) — tile-intrinsic truncation
   pathology after ~33–48 cumulative attempts each. Post-recovery
   pipeline complete at final coverage: consensus re-materialised,
   both live cells re-evaluated, manifests regenerated, ledger rows
   c2-discharge-0003/0004/0005. **At final coverage F1 rose in BOTH
   live cells** (image +0.0087, text +0.0058 @20 m) — the interim
   text-cell F1 dip recorded after the first pass was an artefact of
   incomplete recovery; precision and tile-MCC remain modestly down
   (feature-dense recovered tiles add some false detections;
   registration changelog has the full three-state table).

## 3. The 20-row correction queue — dispositions

| claim_id(s) | passes | disposition |
| --- | --- | --- |
| c3-0003 | 55maps `detect_brief-text::run3` (one-tile recovery segment) | Bookkeeping only — tile covered at run_4; generator v0.6.0 now reports 0 completed for the segment; disclosed in E71. No rerun needed |
| c3-0093 | e47 `propose_brief-text::run4` | E71; **rerun** (7 tiles — GeoJSON governs over the dual-listed sidecar) |
| c3-0104–0109 | n1-outstanding `pro-*-high-t0` ×6 | E71; manifests corrected (v0.6.0: 487→458–472); **rerun** (136 tiles); E57 quarantine unchanged |
| c3-0133–0135, 0166–0168 | pv-diag-384 t0.0 ×6 | E71; manifests corrected; **rerun** (143 tiles); the two LIVE conditions re-evaluated post-recovery under preserve-and-compare |
| c3-0318, c3-0321 | pro-medium baselines ×2 (resume-merge segment scoping) | **Fixed** — v0.6.0 union rule restores the C3-correct 487 (was 26) |
| c3-0440, c3-0442 | h12-v2 `r3-hp-heavy` ×2 | E71; manifests corrected (327→326); **rerun** (1 tile each) |
| c3-1117 | flash35 `min-text-1of10::run3` | Dropped from rerun (second segment covers the tile). **Residual**: manifest reads 486 (meta `completed_items` lacks the segment-recovered tile) vs true GeoJSON coverage 487 — meta merge-repair queued with the rerun's bookkeeping pass |
| c3-1132 | 55maps uplift `verified-3of10` | **Fixed** — GAP-8 resolved (16,484→16,482) |

## 4. Per-era field-verifiability map (the known wall, now charted)

| era / meta shape | `thinking`/config fields | token fields (`usage_stats`) | tile counts | notes |
| --- | --- | --- | --- | --- |
| retest era (phase2a–3c, batch shape, no `per_item_metadata`) | verifiable (config + meta) | **UNVERIFIABLE — wholesale unpopulated** (E63's wall; 225 phase3c + phase3a siblings) | scalar `items_processed` reliable; `completed_items[]` lists STALE on the 127 patch-tiles passes (E70) | token-level corroboration impossible for this era |
| gs-v2 / 55maps era (`per_item_metadata` present) | verifiable (per-item identity authoritative — E57) | verifiable | `items_processed` scalar **attempts-inclusive** (~2× tiles); union of `completed_items` is the correct completed count (v0.6.0 rule) | the first-cut generator fix rediscovered this the hard way (§ 5) |
| resume-merged metas (`recovery_history` present) | verifiable | verifiable | union of `completed_items` correct; `per_item_metadata` and `.tiles.json` may be **segment-scoped** (E71 defect 3) | one pass has BOTH values wrong (pv-diag image-t0.0 run_1; true coverage only in the GeoJSON) |
| detection GeoJSONs | — | — | `processed_tiles` = **authority 1** for evaluated coverage | basis of the recovery worklists |

## 5. Apparatus incidents (process transparency, charter § 12 discipline)

1. **The first cut of the E71 generator fix introduced regressions the
   diff audit caught**: `execution_stats.items_processed` is itself
   era-inconsistent (attempts-inclusive in the 55maps/gs-v2 eras;
   round-summed in resume-merged metas), so preferring the scalar
   silently corrupted 60+ rows (8,541→17,057 class). Reverted to the
   C3 re-derivation's validated union-of-`completed_items` rule; final
   diff exactly the 19 intended rows. Lesson: the audit's own validated
   derivation rule was the specification — reuse it, don't re-derive.
2. **Gate A of the family-FDR compute failed as first written**: the
   committed phase2a point values come from the global corpus matcher,
   the registered machinery is the per-tile E26 path; they coincide
   exactly only where no match crosses a tile boundary. The gate was
   revised (exact on text conditions, bounded on image-bearing) BEFORE
   the bootstrap p was computed; the registered statistic was untouched.
3. **The errata-licence register's line anchors are stale** for E16
   onwards (the correction-block insertions shifted them); re-anchoring
   + E62–E71 decomposition queued before any future census run
   (recorded in the census `_resolution_note`).
4. **Ledger supersession convention undecided**: the 20 FLAGGED c3 rows
   carry disposition "Phase 2 correction queue"; this package's § 3 is
   that queue. Whether resolved rows get superseding ledger rows (same
   `claim_id`, dated) or the package table suffices is a convention for
   the PI to set — proposal: superseding rows land with the Phase 5
   `revalidate_ledgers.py` design, which must handle them anyway.

## 6. Spend

**US$0.00 API this session.** All computation on sapphire (cluster
heterogeneity: 153k clusters; family-FDR: gates + 10k bootstrap). The
registered recovery rerun (~US$10–25 est.) is blocked on its gate.

## 7. Queued next (per charter § 7)

- The recovery-rerun gate (§ 2 item 6), then its post-recovery pipeline.
- **Phase 3 (C4) — the quantitative sweep**, the biggest unswept
  surface; per the charter it may begin once this gate passes.
- Register re-anchoring (§ 5 item 3) before any future census.
- Phase 4 / 4b carry-forwards unchanged (Sol first target: the ~150
  Session-119 corrections; cross-model cap US$150).

## Changelog

### 2026-07-30 — Original publication

Assembled at the end of the Session 121 landing sequence; all § 2 items
committed and pushed through `origin/main`. Awaiting GATE 2.
