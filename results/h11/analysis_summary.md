# H11 — Tile Size Effect Analysis Summary

**Study**: H11 — Tile Size Effect on Detection Performance (pilot + production + 256 px diagnostic)
**Date**: 2026-03-15 (pilot) / 2026-03-22 (production 384 px / 487-tile) / 2026-03-23 (256 px diagnostic) / 2026-03-28 (downstream Obs 203 synthesis)
**Protocol-errata**: E41 (384 px pathway production lock-in), E43 (consensus-384 UNINTENDED-T1.0) + E44 (single-pass-384 UNINTENDED-T1.0) — dual-role disposition settled 2026-04-23, commit `5ae94041`
**Primary aggregation**: greedy consensus + post-verifier (PV) two-stage pipeline
**Evaluation**: three-way tile-size comparison on the 487-tile production footprint (435 reference mounds) at 20 m buffer
**Pilot evaluation**: 60-tile validation footprint (97 reference mounds) — underpowered and retracted as headline (see §"Pilot vs production")

## Scope note — this summary vs the detailed narrative

`results/h11-tile-size-results.md` (646 lines, 10 sections) is the
project's comprehensive H11 narrative covering experimental design,
mechanism analysis, pilot findings, production confirmation, 256 px
diagnostic, methodological notes, and open questions. This summary
is the focused paper-citation layer that sits above it: the
headline finding, the three-way tile-size comparison, the
cross-hypothesis pointers, and the UNINTENDED-T1.0 disposition. For
mechanism and methods-level detail, cite the detailed narrative.

## Headline result — 384 px is the optimal tile size

On the 487-tile production footprint (435 reference mounds at 20 m
buffer), the F1 curve across tile sizes follows an **inverted-U**
with 384 px at the peak:

| Tile size | Best config | F1 | Paired Δ vs 384 px best | p | Scope |
|----------:|:------------|---:|------------------------:|---:|-------|
| 256 px | text 5-of-5 + PV | 0.844 | −0.005 | 0.816 | 1,032 tiles, 431 mounds |
| **384 px** | **text 6-of-10 + PV** | **0.883** | — | — | **487 tiles, 435 mounds** |
| 512 px | text 5-of-10 + PV | 0.831 | −0.063 | **0.002** | 487 tiles, 435 mounds (paired spatial-join to 384 px polygons) |

Key claims:

1. **384 px significantly outperforms 512 px** by +0.063 F1 in a
   paired comparison (p = 0.002). The effect holds across six
   paired comparisons (loose / moderate / strict consensus; single-
   pass; image / text tracks) at p ≤ 0.008 for all six.
2. **384 px is not significantly better than 256 px** (ΔF1 = +0.005,
   p = 0.816), but 256 px produces a denser false-positive pool
   (1,032 tiles vs 487) that erodes verifier precision at
   near-identical recall.
3. **The performance curve is broad near the peak.** Tile sizes in
   the ~300–400 px range would likely perform similarly;
   practitioners do not need to fine-tune tile size to the pixel —
   the target is roughly matching the feature's size to 5–13 % of
   the tile area.

## Pilot vs production — the pilot was underpowered

The initial pilot evaluation on a 60-tile / 97-mound validation set
(2026-03-15) concluded that "384 proposer-verifier does not improve
F1" (pilot F1 = 0.684 at 384 PV vs F1 = 0.796 at 512 PV — a clear
degradation). Obs 179 (2026-03-22) retracted this conclusion as
underpowered when the production 487-tile / 435-mound evaluation
revealed 384 text 6-of-10 + PV at F1 = 0.883 — the project's
best-at-the-time result.

Three reasons the pilot missed the effect:

1. **Minimum detectable effect.** The 60-tile set had MDE ≈ 0.09;
   the +0.06 production effect was below detection threshold.
2. **Missing factorial cell.** Pilot tested single-pass PV and
   consensus-without-PV separately, but never consensus + PV — the
   combination that is transformative at both tile sizes.
3. **Bounds-clipping artefact.** Clipping 384 px results to 512 px
   bounds distorted precision estimates from edge effects (Obs 179
   §"Bounds clipping", `h11-tile-size-results.md` §6.1).

The paper's tile-size claim must cite the 487-tile production
result, not the pilot.

## Consensus-stage sub-findings (384 px, 487-tile scope)

### N=5 ≈ N=30 at 384 px (recall saturation)

| Config | Best threshold | F1 | P | R |
|--------|:--------------:|---:|---:|---:|
| 384 N=5 | x=5 | **0.664** | 0.560 | 0.814 |
| 384 N=10 | x=10 | 0.648 | 0.595 | 0.711 |
| 384 N=30 | x=28 | 0.643 | 0.567 | 0.742 |

At 384 px, going from N=5 to N=30 **reduces** F1 by −0.021 — the
opposite of the 512 px pattern where N=30 added +0.094 over N=5.
Per-run 384 consensus achieves ~0.92 recall at T=0.7, so additional
runs beyond N=5 contribute almost no new true positives while
inflating the false-positive pool.

### Consensus + PV Goldilocks zone

At 384 px, the consensus-threshold Goldilocks zone spans 4-of-10
through 7-of-10 (all F1 > 0.86), peaking at 6-of-10 (F1 = 0.883).
Slightly higher than the 512 px Goldilocks zone (3-of-5 to 5-of-10),
consistent with the denser 384 px candidate pool needing a
marginally stricter consensus filter.

## ⚠️ UNINTENDED-T1.0 disposition — settled 2026-04-23

Two H11 directories retain the `-UNINTENDED-` label as a permanent
origin-of-data signal:

- `outputs/h11/consensus-384-UNINTENDED-T1.0/`
- `outputs/h11/single-pass-384-UNINTENDED-T1.0/`

**Origin**: two distinct but root-cause-linked errata —

- **§E43** (consensus): 30 consensus-pipeline runs at 487-tile scope
  inadvertently executed at T=1.0 when T=0.7 was intended.
- **§E44** (single-pass): 10 single-pass runs at 240-tile scope
  inadvertently executed at T=1.0 when the deterministic T=0.0
  baseline was intended.

Shared root cause: a config propagation failure where the
`detect_brief-text.json` prompt config has `"temperature": 1.0`
hardcoded, and the proposer launcher used the config's default
instead of the YAML-specified temperature override. Discovered in
the Session 57 configuration audit (2026-03-25); documented in
`docs/methodology/preregistration/protocol-errata.md` §E43 + §E44.

**Status**: retained for 487-tile / Era 2-scope T=1.0 coverage where
the preregistered Phase 2b (340-tile, K=3 × 5 T × 2 tracks) does not
extend. The corrected T=0.7 baseline was re-run separately at
`outputs/retest/h11-single-pass-384-t0/` and the corrected T=0.7
consensus baseline lives at
`outputs/h11/pv-diag-384/flash-minimal-text-n30-t07/`.

**Paper citation rule**:

| Claim | Cite |
|-------|------|
| "T=1.0 (Gemini default) is suboptimal" (scientific) | `results/retest/phase2b/analysis_summary.md` (preregistered 340-tile K=3 H7 temperature sweep) |
| 487-tile / Era 2 T=1.0 leaderboard rows and pairwise tests | `outputs/h11/{consensus,single-pass}-384-UNINTENDED-T1.0/` — with transparent "UNINTENDED" provenance labelling |

Dual-role READMEs committed 2026-04-23 as commit `5ae94041`
("docs(unintended): clarify dual-role disposition for UNINTENDED-T1.0
dirs"). The directories must not be archived — ~157 downstream
references depend on them for legitimate 487-tile scope use. See also
working-notes Obs 274 (2026-04-23) for the Phase 2b tile-level MCC
inversion finding that sits alongside this disposition decision.

## Cross-hypothesis context

H11's 384 px outcome is load-bearing for the paper's pipeline
architecture claim: the production detection stack runs at 384 px
tiles with 336 px stride (12.5 % overlap), post-verifier two-stage,
K=5 consensus, text-only `detect_brief-text` proposer. The library-
axis hypotheses (H8 v2, H10 v2, H12 v2) were all re-executed at
384 px under this production pipeline; H11 is therefore the
pipeline-lock-in result that enables the Era 1 / Era 2 comparability
of H8 / H10 / H12 results.

| Hypothesis | Relationship to H11 |
|------------|---------------------|
| H8 v2 library composition (Obs 238) | Re-run at 384 px under E51; uses 384 px production pipeline |
| H10 v2 pool-size (Obs 236) | Re-run at 384 px under E49; calibration test set is the 327-tile h10-384 holdout |
| H12 v2 HP:HN ratio (Obs 239) | Re-run at 384 px under E52; same 327-tile test set |
| Phase 2b H7 temperature (retest) | Run at 384 px under E27 dual-track; T=0.0 optimum feeds downstream Era 1 phases |
| Phase 3a image / text matrices | Run at 384 px at production operating point; T=0.7 + HIGH thinking consensus |
| 55-map generalisation | 384 px production pipeline; F1 = 0.891 on gold standard (2026-04-08) |

## Caveats

1. **Pilot conclusions retracted.** Sections 2–7 of
   `h11-tile-size-results.md` (the pilot narrative) describe pilot-
   era findings that production retraction has superseded. They are
   retained for historical record and as a cautionary tale about
   underpowered evaluation; they are NOT valid as citations for the
   paper. Sections 8–9 (production + 256 px diagnostic) are the
   citable layer.
2. **256 px vs 384 px is directionally informative but not a tie
   under power.** The paired ΔF1 = −0.005 (p = 0.816) is consistent
   with either "256 ≈ 384" or "256 slightly worse than 384"; the
   MDE at 256 px scope (1,032 tiles, 431 mounds) is small enough
   that a real −0.02 effect would likely be detected. The practical
   argument for 384 px over 256 px rests on the false-positive
   density difference (doubling tile count roughly doubles false-
   positive candidates) and the verifier precision gradient, not on
   a significant F1 gap.
3. **Tile-size sensitivity is broad near the peak.** "384 px is
   optimal" should not be read as "384 px is uniquely optimal".
   ~300–400 px would likely perform similarly. The paper's claim is
   well-supported as "tile size materially affects F1 (inverted-U),
   with the peak region around 300–400 px matching 5–13 % mound-to-
   tile area ratio".
4. **UNINTENDED-T1.0 retention is by design.** See the §"UNINTENDED-
   T1.0 disposition" block above. The paper's scientific T=1.0 claim
   rests on Phase 2b, not on the UNINTENDED directories.

## Paper implications

1. **384 px tile size is a defensible production choice.** The +0.063
   F1 advantage over 512 px is statistically robust (p = 0.002 in
   paired comparison) and replicates across six comparisons and
   downstream hypothesis retests.
2. **Pipeline architecture: 384 px + consensus + PV.** The three-
   factor combination is what produces the F1 = 0.883 production
   result. The paper's Methods section should present this as the
   production stack, not as separate optimisations.
3. **N=5 consensus is sufficient at 384 px.** Higher N (10, 30) does
   not improve F1 because per-run recall is already saturated at
   ~0.92. This is practitioner-relevant: users do not need to pay
   for K=30 at 384 px.
4. **Underpowered-pilot cautionary pattern.** The pilot's 60-tile /
   97-mound evaluation produced a retracted finding that the
   production 487-tile / 435-mound evaluation reversed. This is a
   worked example of the "flag surprising results and verify the
   pipeline" discipline that the paper's methodology contribution
   can reference (together with Obs 235 for a complementary
   retracted-finding case).

## Reproducibility

| Metric | Value |
|--------|-------|
| Production evaluation scope | 487 tiles, 435 reference mounds |
| Diagnostic scope (256 px) | 1,032 tiles, 431 reference mounds |
| Pilot scope (retracted) | 60 tiles, 97 reference mounds |
| Buffer | 20 m (primary); 30 / 40 / 50 m for multi-tolerance |
| Proposer | `detect_brief-text.json` (text-only) + `detect_brief-text-image.json` (image-using) |
| Verifier | `flash-adversarial-v1` |
| Consensus N | 5 (production default); 10 and 30 tested |
| Consensus threshold sweep | x = 1..N at each N |
| Bootstrap iterations | 1,000 |
| Bootstrap seed | 42 |
| Paired permutation | tile-level paired, 10,000 iterations, seed 42 (E45 methodology) |
| FDR | Benjamini–Hochberg at q = 0.05 where applicable |

## Artefacts

### Primary narrative

- `results/h11-tile-size-results.md` (646 lines, 10 sections — the
  comprehensive narrative; this summary supplements it as the focused
  paper-citation layer)

### Production 384 px (487-tile scope) — the citable layer

- PV diagnostic matrix: `results/h11-384-pv-diagnostic/` with
  `summary.json` (aggregate) + per-cell subdirectories for each
  (consensus N / threshold / strategy) combination; `bootstrap-cis-384px.json`
  provides the bootstrap CI layer; `pairwise/` subdirectory has the
  paired permutation tests against 512 px
- Single-pass T=0 re-run: `results/h11-384-single-pass-t0-rerun/` —
  consensus-sweep-results.csv + consensus-analysis-{report.json, summary.md}
- Production raw detections: `outputs/h11/pv-diag-384/` (30+ run
  directories across text / image × consensus-N × threshold cells)

### 256 px diagnostic (1,032-tile scope)

- `outputs/h11/pv-diag-256/` (raw detections)
- Evaluation rolled into `h11-tile-size-results.md` §9; no separate
  results subtree (by design — this was a diagnostic, not a full
  production replication)

### UNINTENDED-T1.0 (dual-role, retained)

- `outputs/h11/consensus-384-UNINTENDED-T1.0/` + README
- `outputs/h11/single-pass-384-UNINTENDED-T1.0/` + README
- Dual-role framing commit: `5ae94041` (2026-04-23)
- Scientific T=1.0 evidence lives at `results/retest/phase2b/analysis_summary.md`, not here

### Protocol errata

- E41: 384 px pathway production lock-in
- E43: consensus-384 UNINTENDED-T1.0 deviation + disposition
- E44: single-pass-384 UNINTENDED-T1.0 deviation + disposition

### Working-notes cross-references

- Obs 161 / 162 — pilot PV findings (retracted as headline; retained
  for narrative)
- Obs 179 — production 384 px confirms pilot was underpowered
- Obs 180 — paired tests necessary for cross-tile-size comparisons
- Obs 181 — 256 px confirms 384 px as optimal
- Obs 203 — tile size as pipeline optimisation (downstream synthesis)
- Obs 274 — Phase 2b tile-level MCC (2026-04-23; complements this H11
  disposition for Era 2 T=1.0 scope)

## Scripts used

| Phase | Script | Purpose |
|-------|--------|---------|
| 1 | `scripts/run_phase1.py` / `run_phase2.py` (detection launch) | K-pass detection runs across tile sizes + strategies |
| 2 | `scripts/merge_passes.py --sweep` | Consensus threshold sweep |
| 3 | `scripts/run_pv.py` | Post-verifier probability scoring |
| 4 | `scripts/evaluate_detections.py` | F1 / P / R with 1,000-iteration bootstrap CIs at 20 m buffer |
| 5 | `scripts/pairwise_permutation_test.py --mode tile-level` | Paired permutation against 512 px at matched-footprint scope |

## Cross-hypothesis links

- H8 v2 summary: `results/h8-v2/analysis_summary.md`
- H10 v2 summary: `results/h10/analysis_summary.md`
- H12 v2 summary: `results/h12-v2/analysis_summary.md`
- Phase 2b retest summary: `results/retest/phase2b/analysis_summary.md`
- Meta-findings synthesis: `results/meta-findings-summary.md`
- Protocol errata: `docs/methodology/preregistration/protocol-errata.md` §E41, §E43, §E44

---

**Status**: Authoritative paper-citation summary for H11 tile-size
effect. Sits above `results/h11-tile-size-results.md` (comprehensive
narrative) as the focused claim-level layer. The UNINTENDED-T1.0
disposition is settled per commit `5ae94041`; the pilot-era findings
in `h11-tile-size-results.md` §§2–7 are retracted as citable paper
material but retained as historical record.
