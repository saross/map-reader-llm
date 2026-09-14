# GS characterisation vs 55-map deployment — all deployed configurations (@ 50 m)

> **Last revised**: 2026-09-13 (revision trail attached; no number changed). See [§ Changelog](#changelog) for revision history.
>
> GS side: the matching 5-pass + n=1-verifier cell at its best operating point, scored at the shared 50 m operational buffer vs curator GT. 55-map side: the canonical-GT board (tiers in brackets). Δ = 55-map k3 − GS. T0.3 GS comparator added 2026-06-11 (Run A).

| config | GS F1@50 (MCC) | 55-map k3 (tier) | 55-map k4 (tier) | Δ (k3−GS) |
|---|---|---|---|---:|
| text HIGH T0.3 | 0.9045 (0.783) | 0.8476 | 0.8359 | -0.0569 |
| text HIGH T0.7 | 0.8908 (0.769) | 0.8425 | 0.8152 | -0.0483 |
| text MIN T0.7 | 0.8996 (0.790) | 0.8127 | 0.7831 | -0.0869 |
| image HIGH T0.7 | 0.8771 (0.827) | 0.7987 | — | -0.0784 |

## Changelog

### 2026-09-13 — Revision trail attached (no number changed)

**Trigger**: checklist item 11b
(`planning/documentation-foundation-checklist-2026-09-13.md`), closing the
generated documents that sat in neither compliance regime. The three boards
beside this file in `results/55map-leaderboard/` are generated projections and
took the 2026-09-11 ruling's machine provenance — a GENERATED banner, a
source-commit stamp and a tested `--check` drift guard. This file is the
exception in the directory: it has **no sidecar JSON and no generator**
(`reports/verification/apparatus/generator-map.json`, rule
`hw-gs-55map-transfer`, classifies it hand-written), so it owes the hand
banner-and-changelog pattern instead, and until now carried neither.

**Before → after**: no numerical claim moved. Every GS F1@50, MCC, 55-map k3
and k4 figure and every Δ is exactly as published on 2026-06-11; the only
edits are this banner and this section.

**What did NOT change**: the four compared configurations, the tiers quoted in
brackets on the 55-map side, the 50 m operational buffer, and the direction of
every Δ (all four negative — GS characterisation over 55-map deployment).

### 2026-06-11 — Original publication

Four deployed configurations compared at the shared 50 m operational buffer:
the GS side's matching 5-pass + n=1-verifier cell at its best operating point
against the canonical-GT 55-map board, with Δ = 55-map k3 − GS. Published in
two steps the same day — the table (`de7f50cb7`) and then the T0.3 comparator
row filled from Run A (`7d78aca2c`).
