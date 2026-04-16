# H12 v2 — HP:HN Ratio Analysis Summary

**Study**: H12 v2 — HP:HN Ratio (384 px / production carry-forward)
**Date**: 2026-04-16 (runs launched 2026-04-15)
**Protocol-errata**: E52
**Primary aggregation**: greedy consensus at t=4
**Secondary aggregation**: WBF variant C (reported for cross-hypothesis comparability)
**Evaluation**: 327-tile h10-384 test set, 20 m buffer, 1000 bootstrap iterations, seed=42

## Headline result — three-way null

All three preregistered pairwise contrasts are **null** after
Benjamini–Hochberg FDR correction at q = 0.05. All condition F1s cluster in a
tight 0.688–0.717 band at the primary operating point (greedy t=4), with
fully overlapping 95 % bootstrap confidence intervals.

| Code | Contrast | F1 (a → b) | ΔF1 | raw p | BH-adj p | Signif? |
|------|----------|------------|-----|-------|----------|---------|
| R12 | R1 HN-heavy vs R2 balanced | 0.708 → 0.717 | −0.009 | 0.717 | 0.717 | no |
| R23 | R2 balanced vs R3 HP-heavy | 0.717 → 0.688 | +0.030 | 0.167 | 0.500 | no |
| R13 | R1 HN-heavy vs R3 HP-heavy | 0.708 → 0.688 | +0.021 | 0.406 | 0.609 | no |

Tile-level paired permutation pattern is similarly weak: every contrast has
80 %+ of tiles tied between the two conditions, with the remaining 50–60
tiles split roughly evenly.

## Cross-hypothesis context

H12 v2 closes the hard-example library axis at the proposer stage:

| Hypothesis | Factor | Result | Reference |
|------------|--------|--------|-----------|
| H8 v2 | Library composition + size (7 levels) | NULL after BH-FDR | Obs 238 |
| H10 v2 | Calibration-pool size (4 levels) | NULL | H10 v2 summary |
| **H12 v2** | **HP:HN ratio (3 levels)** | **NULL after BH-FDR** | this report |

With all three preregistered factors in the hard-example library design
returning nulls at the proposer stage under production carry-forward
settings, the library-design story is closed for the write-up. The F1
ceiling for Gemini 3 Flash on this task under these settings appears to
sit around 0.70–0.73, and library-design variations are mostly noise around
that ceiling.

## Per-condition metrics at greedy t=4 (primary operating point)

| Condition | HP:HN | F1 [95 % CI] | Precision | Recall | n detections |
|-----------|-------|--------------|-----------|--------|--------------|
| r1-hn-heavy | 2:6 (1:3) | 0.708 [0.643, 0.761] | 0.825 | 0.621 | 240 |
| **r2-balanced** | **4:4 (1:1)** | **0.717 [0.661, 0.768]** | **0.843** | **0.624** | **236** |
| r3-hp-heavy | 6:2 (3:1) | 0.688 [0.637, 0.740] | 0.776 | 0.618 | 254 |

R2 is reused from H8 v2 Scale-8 (byte-identical to the existing H10 v2
`pool_160_hp4hn4` run).

## Threshold sweep (greedy t=1..5, all conditions)

| Condition | t=1 | t=2 | t=3 | t=4 | t=5 |
|-----------|-----|-----|-----|-----|-----|
| r1-hn-heavy | 0.276 | 0.625 | **0.731** | 0.708 | 0.603 |
| r2-balanced | 0.310 | 0.623 | 0.699 | **0.717** | 0.606 |
| r3-hp-heavy | 0.286 | 0.612 | **0.701** | 0.688 | 0.603 |

Per-condition best F1 (across the full sweep): R1 peaks at t=3, R2 at t=4,
R3 at t=3. CIs at the peaks all overlap.

## WBF variant C (secondary aggregation)

| Condition | F1 [95 % CI] | Precision | Recall | n fused |
|-----------|--------------|-----------|--------|---------|
| r1-hn-heavy | 0.315 [0.263, 0.371] | 0.201 | 0.737 | 1171 |
| r2-balanced | 0.348 [0.291, 0.408] | 0.228 | 0.743 | 1041 |
| r3-hp-heavy | 0.332 [0.281, 0.386] | 0.214 | 0.737 | 1097 |

WBF variant C produces a high-recall / low-precision candidate set by
design (unconditional merge at IoU 0.25, 60 m min-separation, no vote
threshold). Absolute WBF F1s here are not directly comparable to H8 v2 or
H10 v2 greedy numbers. The ordering is consistent with greedy: R2 > R3 > R1
on F1, R2 > R3 > R1 on precision, all three effectively tied on recall.

## ⚠️ Directional findings worth flagging (non-significant)

These patterns do not survive statistical testing, but should be noted for
the write-up because they **contradict the preregistered directional
prediction**:

### 1. R3 (HP-heavy) is directionally the **worst**, not the best for recall

Preregistered prediction (§H12, prereg lines 988–989):

> Higher HP:HN ratio may improve recall (more positive guidance)
> Lower HP:HN ratio may improve precision (more exclusion examples)

Observed at greedy t=4:

| Metric | R1 (HN-heavy) | R2 (balanced) | R3 (HP-heavy) |
|--------|---------------|---------------|---------------|
| Precision | 0.825 | **0.843** | 0.776 |
| Recall | 0.621 | 0.624 | 0.618 |
| P − R | +0.204 | +0.219 | +0.158 |

R3's recall is **identical** to R1 and R2 (0.618 vs 0.621 vs 0.624), while
its precision is **lower** by 0.05–0.07. Adding more hard positives does
not increase recall in any direction we can see — it just adds more
candidates, most of which are false positives. The mechanism the
preregistration hypothesised (more HPs → more recognition → higher recall)
is not supported by the data.

### 2. R1 wins at t=3; R2 wins at t=4

The operating point matters for which ratio looks best. At t=3 (3-of-5
consensus) R1 has the highest F1 (0.731); at t=4 R2 does (0.717). This
mirrors the H8 v2 finding that greedy threshold choice shifts which
condition lands on top, and further supports the interpretation that
between-condition F1 variance is consensus-threshold noise rather than
a real effect of library design.

### 3. All three conditions converge at t=5

At 5-of-5 consensus, all three conditions land at essentially F1 = 0.60
(R1 0.603, R2 0.606, R3 0.603). The unanimity threshold removes whatever
weak directional signal exists at t=3/t=4, collapsing onto a shared hard
core of high-confidence detections.

## Execution summary

| Metric | Value |
|--------|-------|
| Conditions launched | R1, R3 (R2 reused) |
| Passes per condition | 5 |
| Tiles per pass | 327 |
| Total new API calls | 3,270 |
| Wall time (all 10 runs) | ~26 minutes |
| Workers | 250 |
| Mode | realtime + flex + context cache |
| Cache hit rate (R1 run_1) | 94.5 % |
| Total cost (meta-reported) | ~$34.00 |

### Two transient tile-level failures in R3

| Run | Tile | Failure mode |
|-----|------|--------------|
| R3 run_3 | `K-35-053-3_Elenovo_x672_y3360.png` | JSON parse error (malformed model response) |
| R3 run_5 | `K-35-062-2_Rakovski_x4032_y336.png` | JSON parse error (malformed model response) |

Both are known transient failure modes of Gemini 3 Flash (non-retriable JSON
parse failures). Impact on analysis is minor: each affected tile drops from
5 votes to 4 votes in the R3 consensus. Both still qualify for the t=4
primary operating point. The R3 voting summary shows 254 clusters at t=4
(vs 240 for R1 and 236 for R2), consistent with R3's lower precision rather
than with the 2 missing votes.

## Artefacts

- Study YAML: `studies/h12-v2-ratio.yaml`
- Configs: `prompts/configs/h12/v2/detect_h12_{r1-hn-heavy,r2-balanced,r3-hp-heavy}_v2.json`
- Raw detections: `outputs/h12-v2/{r1-hn-heavy,r3-hp-heavy}/run_{1..5}/`
- R2 reuse source: `outputs/h10/evaluation-v2/pool_160_hp4hn4/run_{1..5}/`
- Greedy consensus: `outputs/h12-v2/greedy/{r1-hn-heavy,r2-balanced,r3-hp-heavy}/consensus_t{1..5}.geojson`
- WBF candidates: `outputs/h12-v2/wbf/{r1-hn-heavy,r2-balanced,r3-hp-heavy}/wbf_candidates.geojson`
- Evaluation reports: `results/h12-v2/{greedy,wbf}/{condition}/evaluation.{json,csv,md}`
- Permutation tests: `results/h12-v2/permutation-t4/R{12,23,13}-*/pairwise_permutation_result.json`
- FDR summary: `results/h12-v2/fdr_summary.txt`, `results/h12-v2/permutation-t4/fdr_summary.json`
- Full console summary: `results/h12-v2/analysis_summary.txt`
- Protocol errata: `docs/methodology/preregistration/protocol-errata.md` (entry E52)

## Scripts used

| Phase | Script | Purpose |
|-------|--------|---------|
| 1 | `scripts/merge_passes.py --sweep` | Greedy consensus t=1..5 |
| 2 | `scripts/fuse_detections_wbf.py --config h12v2-*` | WBF variant C |
| 3 | `scripts/evaluate_detections.py` | F1/P/R with 1000-iteration bootstrap CIs |
| 4 | `scripts/pairwise_permutation_test.py --mode geojson` | Tile-level paired permutation |
| 5 | `scripts/apply_fdr_h12v2.py` | BH-FDR at q=0.05 over 3 contrasts |
| 6 | `scripts/summarise_h12v2.py` | Collated per-condition summary table |
