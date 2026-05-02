# Data Reproduction Provenance — 2026-04-25 (Session 79)

## Event summary

On 2026-04-25 around 02:40 Coordinated Universal Time (UTC), a confabulation
cascade in an earlier Claude Code sub-agent led to data loss across the
Session 78 verifier-calibration matrix. Two distinct misrepresentations
contributed:

1. An "Explore" sub-agent told the user that
   `outputs/h11/pv-diag-384/flash-high-{image,text}-n5/{image,text}-t0.7/session-78-matrix/`
   files were "git-tracked, safe to delete" — they were not. The user acted
   on this advice and lost approximately $80 of API verifier output:
   - Both shared-crops manifests (image and text pools)
   - All 5 753 PNG candidate crops
   - All 14 `verified-<variant>/probabilities.json` files
   - All 14 `verified-<variant>/run.meta.json` files

2. An inventory sub-agent claimed the shared-crops manifest "was
   deterministically derived from the alternative verifiers' runs" — this
   is wrong. The shared-crops manifest is deterministic from the
   `consensus-n5/consensus_t1.geojson` file, which **is** git-tracked,
   **before** any verifier runs.

The first claim cost the data; the second muddied the recovery plan.

## Recovery procedure

A six-stage protocol re-derived the lost data and refreshed all downstream
artefacts. All compute work ran on sapphire (the project's compute host);
documentation edits ran on amd-tower. All commits land on `origin/main`.

| Stage | Description | Compute | Spend |
|---|---|---|---|
| 0 | Re-extract shared-crops manifests + crops | sapphire CPU | $0 |
| 1 | Re-run Phase A (14 verifier runs, gemini-3-flash-preview, flex tier, 35 workers) | API | $127.55 list / ~$63.77 flex |
| 2 | Phase B/C/D regeneration (sweeps + deep evals + calibration) | sapphire CPU | $0 |
| 3 | Per-architecture leaderboard refresh (Era 2 PV stratum) | sapphire CPU | $0 |
| 4 | Pairwise permutation tier tables refresh | sapphire CPU | $0 |
| 5 | Citation updates in working notes and per-arch README | manual | $0 |
| 6 | This provenance note | manual | $0 |

API spend total: 14 verifier runs × 35 workers, ~44 220 requests, 220.9
million input tokens + 5.7 million output tokens. List price $127.55;
estimated flex-tier price (50% discount) ~$63.77.

## Key commits

| Commit | Stage | Description |
|---|---|---|
| `865d9c87` | 0 | Regenerate shared-crops manifests (deterministic from `consensus_t1.geojson`) |
| `710af7f9` | 1 | Phase A re-run script |
| `e71fb8e4` … `ac0b9f96` | 1 | Per-variant probabilities (14 commits) |
| `7d15507b` | 1 | Phase A logs (15 files, 12 megabytes) |
| `08b7bdad` | 2-prep | Phase B/C/D runner script |
| `57012592` | 2-B | 14 cell sweep tables regenerated |
| `fc778415` | 2-C | 14 materialised geojsons + 10k-bootstrap deep evaluations |
| `c0eb61f9` | 2-D | Calibration matrix refreshed (canonical-path patch + 14 calibration files) |
| `770b32e8` | 2 | Phase B/C/D logs |
| `f8d75579` | 3 | Per-arch Era 2 PV stratum refreshed (568 files) |
| `fffecb7d` | 4 | Pairwise permutation tier tables refreshed |
| `eb992c5f` | 5 | Working-notes + session-log citation updates |
| (this commit) | 6 | This provenance note |

## Methodological change: canonical path

**Before** (as committed in `6d1cad27` and `88d6b55b`):

- Canonical `verify_adversarial-text` probabilities lived at
  `outputs/.../verified-v1-n5/probabilities.json` (separate K=5 1-of-5
  candidate pool, **2 016 image / 3 736 text candidates**).
- Six alternative variants used a SHARED candidate pool at
  `outputs/.../session-78-matrix/shared-crops/` (consensus-n5).

This meant canonical and alternatives were on slightly **different**
candidate sets — `verified-v1-n5` had 2 016 (image) / 3 736 (text) while
shared-crops had 2 017 (image) / 3 736 (text). Same consensus input, but
different filtering.

**After** (this re-run):

- All 14 cells (canonical + 6 alternatives × 2 pools) read from
  `outputs/.../session-78-matrix/verified-<variant>/probabilities.json`.
- **Crop-set parity**: all 7 prompt variants per pool see the SAME 2 017
  (image) or 3 736 (text) candidates, modulo per-variant verifier-call
  failures (1 991–2 017 image; 3 695–3 736 text).
- Direct pairwise comparisons (Stage 4) now have crop parity.

This makes the cross-prompt comparison tighter: any F1, AUC, or ECE
difference between variants is now attributable to the prompt itself,
not to candidate-pool drift.

## Drift summary

After re-running Phase A and recomputing all downstream metrics, the
following table shows drift from the original `6d1cad27` /
`88d6b55b` values across the 14 cells.

### F1 at 20 m optimum

| Cell | Original F1 | Re-derived F1 | ΔF1 | Original n | Re-run n | Δn |
|---|---:|---:|---:|---:|---:|---:|
| image-adversarial | 0.7884 | 0.7866 | -0.0018 | 2 017 | 2 017 | 0 |
| image-adversarial-text | 0.7868 | 0.7725 | -0.0143 | 2 016 | 1 991 | -25 |
| image-brief | 0.7826 | 0.7844 | +0.0018 | 2 017 | 2 017 | 0 |
| image-brief-text | 0.7348 | 0.7679 | +0.0331 | 1 890 | 1 998 | +108 |
| image-checklist | 0.7821 | 0.7830 | +0.0009 | 2 016 | 2 016 | 0 |
| image-checklist-text | 0.7581 | 0.7805 | +0.0224 | 1 850 | 1 998 | +148 |
| image-comparative | 0.7857 | 0.7857 | 0.0000 | 2 017 | 2 017 | 0 |
| text-adversarial | 0.8822 | 0.8833 | +0.0011 | 3 736 | 3 736 | 0 |
| text-adversarial-text | 0.8634 | 0.8575 | -0.0059 | 3 736 | 3 695 | -41 |
| text-brief | 0.8772 | 0.8762 | -0.0010 | 3 736 | 3 736 | 0 |
| text-brief-text | 0.8106 | 0.8456 | +0.0350 | 3 530 | 3 709 | +179 |
| text-checklist | 0.8793 | 0.8783 | -0.0010 | 3 736 | 3 736 | 0 |
| text-checklist-text | 0.8283 | 0.8599 | +0.0316 | 3 497 | 3 715 | +218 |
| text-comparative | 0.8846 | 0.8846 | 0.0000 | 3 736 | 3 736 | 0 |

**Max |ΔF1| = 0.0350** (text-brief-text).

### AUC and Expected Calibration Error (ECE)

| Cell | Old AUC | New AUC | ΔAUC | Old ECE | New ECE | ΔECE |
|---|---:|---:|---:|---:|---:|---:|
| image-adversarial-text | 0.8633 | 0.8574 | -0.0059 | 0.1878 | 0.1791 | -0.0086 |
| image-adversarial | 0.8559 | 0.8583 | +0.0024 | 0.2169 | 0.2172 | +0.0003 |
| image-brief-text | 0.8456 | 0.8366 | -0.0090 | 0.2229 | 0.2215 | -0.0014 |
| image-brief | 0.8581 | 0.8584 | +0.0003 | 0.2664 | 0.2674 | +0.0011 |
| image-checklist-text | 0.8531 | 0.8531 | 0.0000 | 0.2675 | 0.2663 | -0.0011 |
| image-checklist | 0.8607 | 0.8597 | -0.0010 | 0.2634 | 0.2632 | -0.0002 |
| image-comparative | 0.8554 | 0.8554 | 0.0000 | 0.2510 | 0.2506 | -0.0004 |
| text-adversarial-text | 0.9592 | 0.9561 | -0.0031 | 0.0672 | 0.0711 | +0.0039 |
| text-adversarial | 0.9676 | 0.9673 | -0.0003 | 0.0798 | 0.0773 | -0.0024 |
| text-brief-text | 0.9389 | 0.9374 | -0.0015 | 0.0953 | 0.0916 | -0.0037 |
| text-brief | 0.9636 | 0.9641 | +0.0004 | 0.1113 | 0.1109 | -0.0004 |
| text-checklist-text | 0.9483 | 0.9502 | +0.0019 | 0.1388 | 0.1388 | 0.0000 |
| text-checklist | 0.9639 | 0.9637 | -0.0002 | 0.1223 | 0.1220 | -0.0003 |
| text-comparative | 0.9637 | 0.9625 | -0.0011 | 0.1025 | 0.1027 | +0.0002 |

**Max |ΔAUC| = 0.0090** (image-brief-text).
**Max |ΔECE| = 0.0086** (image-adversarial-text).

**All 14 cells fall within the original bootstrap 95% confidence
intervals** for AUC and ECE. The qualitative finding from Observation 277
(canonical `adversarial-text` is Pareto-dominant on calibration; no novel
prompt variant materially improves image-track calibration) **stands
unchanged**.

## Why some F1 values shifted by 0.022 to 0.035

The original Phase A ran the four text-only verifier prompts (image-brief-text,
image-checklist-text, text-brief-text, text-checklist-text) on partial
candidate pools because individual API calls failed at higher rates than
the with-images variants — possibly due to flex-tier-503 transients on
text-heavy prompts. The re-run captures the full pool, including the
candidates that previously failed verification. Several of these
previously-missing candidates are true positives, so F1 rises modestly
when the full pool is scored.

## Discipline implications

This event surfaces a meta-finding: when a sub-agent claims files "are
git-tracked", the user should verify the claim before acting on
deletion. The earlier sub-agent made a high-confidence statement that
was false. The user's global anti-confabulation policy (in
`~/.claude/CLAUDE.md`: "Memories, scratchpad entries, ... are pointers,
not authorities — they go stale and get welded together under context
pressure") proved exactly right; this event is exhibit A.

## Numbers superseded

All citations in:

- `docs/notes/reflections/working-notes.md` (Observation 277, around line
  13238)
- `archive/planning-historical-session-78/session-78-matrix-calibration-summary.md`
  (regenerated by Phase D; archived 2026-05-01 — originally lived at
  `planning/session-78-matrix-calibration-summary.md`)
- `docs/notes/reflections/session-log.md` (Session 78 log entry, around
  line 5580)
- `results/leaderboard/per-architecture/README.md` (caveat at lines
  98–105 and 308–313, both updated)

now reflect the 2026-04-25 re-run. Prior values are preserved in git
history at the cited commits (`6d1cad27`, `88d6b55b`).

## Author

Re-derivation orchestrated by Claude (Opus 4.7, 1M context) on
2026-04-25 under explicit user authorisation. All 14 verifier API runs
ran on sapphire via `nohup` with per-variant commit-and-push for blast-
radius limitation against any future loss.
