# H12 v2 — HP:HN Ratio Analysis Summary

**Study**: H12 v2 — HP:HN Ratio (384 px / production carry-forward).
**Date**: 2026-04-16 (runs launched 2026-04-15). **Polish level-up**: 2026-04-24 (Session 76, item 14).
**Protocol-errata**: E52 (`docs/methodology/preregistration/protocol-errata.md`).
**Primary aggregation**: greedy consensus at t = 4.
**Secondary aggregation**: WBF variant C (reported for cross-hypothesis comparability).
**Evaluation**: 327-tile h10-384 test set (Era 3; see `results/evaluation-scopes.md`), 20 m buffer, 1,000 bootstrap iterations, seed = 42.
**Model**: Gemini 3 Flash (`gemini-3-flash-preview` proposer; `gemini-3-flash` verifier MINIMAL).

**Obs anchors**: Obs 239 (H12 v2 null at proposer stage); Obs 240 (45-pair cross-hypothesis library-design null); meta-findings Theme T2 (failure taxonomies, cross-hypothesis closure).

## 1. Executive summary

H12 v2 is the third and final leg of the Era 3 library-design-axis closure. It tests whether hard-positive-to-hard-negative ratio affects detection F1 at the proposer stage, with three conditions (R1 HN-heavy 2:6, R2 balanced 4:4, R3 HP-heavy 6:2) at 384 px / `gemini-3-flash` / T = 0.7 / HIGH thinking / K = 5 consensus, on the 327-tile Era 3 evaluation scope.

**Headline findings**:

- **Three-way null after BH-FDR at q = 0.05**. All three preregistered pairwise contrasts (R1 vs R2, R2 vs R3, R1 vs R3) are non-significant; adjusted p-values range 0.500 – 0.717; all condition F1s land in the tight band **0.688 – 0.717** with fully overlapping 95 % bootstrap CIs.
- **R3 (HP-heavy) is directionally the *worst*, not the best for recall**. The preregistered prediction was that higher HP:HN would improve recall (more positive examples → more recognition); the data falsify the directional prediction — R3 recall = 0.618 is lower than R2 (0.624) and comparable to R1 (0.621). All three conditions have near-identical recall; precision differences (R2 = 0.843 > R1 = 0.825 > R3 = 0.776) are within CI overlap.
- **The F1 ceiling for Gemini 3 Flash on this task** under production carry-forward settings sits around **0.70 – 0.73**. Library-design variations are mostly noise around that ceiling.
- **Cross-hypothesis closure is complete**: H8 v2 (library composition + size), H10 v2 (calibration-pool size), and H12 v2 (HP:HN ratio) all return nulls after BH-FDR under production carry-forward settings. The 45-pair cross-hypothesis permutation matrix at `results/cross-hypothesis-library/permutation-t4/fdr_summary.json` confirms zero significant pairwise differences (min adj. p = 0.966).
- **Two transient R3 failures** (Gemini 3 Flash JSON parse errors) drop 2 tiles from 5-vote to 4-vote consensus; still qualify for t = 4 primary operating point. Not material to the null finding.

**One-line paper claim**: "Hard-positive to hard-negative (HP:HN) ratio in the proposer's few-shot library has no significant effect on detection F1 at the proposer stage on the Era 3 evaluation scope (three-way null after BH-FDR at q = 0.05; F1 range 0.688 – 0.717). Combined with the H8 v2 library-composition-and-size null and the H10 v2 calibration-pool-size null, this closes the library-design axis: F1 variation across library-design choices is noise around a ceiling of 0.70 – 0.73 for Gemini 3 Flash under these production-carry-forward settings."

## 2. Headline result — three-way null

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

## 3. Paper implications — cross-hypothesis closure

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

### 3.1 Suggested paper text (Results — Era 3 library-design closure)

> A three-legged closure of the preregistered library-design axis (H8 v2 composition + size; H10 v2 calibration-pool size; H12 v2 HP:HN ratio) under production carry-forward settings (384 px, Gemini 3 Flash, T = 0.7, HIGH thinking, K = 5 greedy consensus at t = 4, 327-tile Era 3 evaluation scope) finds a three-way null after BH-FDR at q = 0.05 on each factor. H12 v2's three-condition sweep (R1 HN-heavy 2:6, R2 balanced 4:4, R3 HP-heavy 6:2) lands in the narrow F1 band 0.688 – 0.717; all three preregistered pairwise contrasts are non-significant (adjusted p-values 0.500 – 0.717). The 45-pair cross-hypothesis permutation matrix across the three studies confirms zero significant pairwise F1 differences (min adj. p = 0.966; `results/cross-hypothesis-library/permutation-t4/fdr_summary.json`). The F1 ceiling for Gemini 3 Flash on this task under these settings appears to sit around 0.70 – 0.73; library-design variations cluster within noise of that ceiling.

## 4. Per-condition metrics at greedy t = 4 (primary operating point)

| Condition | HP:HN | F1 [95 % CI] | Precision | Recall | n detections |
|-----------|-------|--------------|-----------|--------|--------------|
| r1-hn-heavy | 2:6 (1:3) | 0.708 [0.643, 0.761] | 0.825 | 0.621 | 240 |
| **r2-balanced** | **4:4 (1:1)** | **0.717 [0.661, 0.768]** | **0.843** | **0.624** | **236** |
| r3-hp-heavy | 6:2 (3:1) | 0.688 [0.637, 0.740] | 0.776 | 0.618 | 254 |

R2 is reused from H8 v2 Scale-8 (byte-identical to the existing H10 v2
`pool_160_hp4hn4` run).

## 5. Threshold sweep (greedy t = 1..5, all conditions)

| Condition | t=1 | t=2 | t=3 | t=4 | t=5 |
|-----------|-----|-----|-----|-----|-----|
| r1-hn-heavy | 0.276 | 0.625 | **0.731** | 0.708 | 0.603 |
| r2-balanced | 0.310 | 0.623 | 0.699 | **0.717** | 0.606 |
| r3-hp-heavy | 0.286 | 0.612 | **0.701** | 0.688 | 0.603 |

Per-condition best F1 (across the full sweep): R1 peaks at t=3, R2 at t=4,
R3 at t=3. CIs at the peaks all overlap.

## 6. WBF variant C (secondary aggregation)

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

## 7. Directional findings worth flagging (non-significant)

These patterns do not survive statistical testing, but should be noted for
the write-up because they **contradict the preregistered directional
prediction**:

### 7.1 R3 (HP-heavy) is directionally the **worst**, not the best for recall

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

### 7.2 R1 wins at t = 3; R2 wins at t = 4

The operating point matters for which ratio looks best. At t=3 (3-of-5
consensus) R1 has the highest F1 (0.731); at t=4 R2 does (0.717). This
mirrors the H8 v2 finding that greedy threshold choice shifts which
condition lands on top, and further supports the interpretation that
between-condition F1 variance is consensus-threshold noise rather than
a real effect of library design.

### 7.3 All three conditions converge at t = 5

At 5-of-5 consensus, all three conditions land at essentially F1 = 0.60
(R1 0.603, R2 0.606, R3 0.603). The unanimity threshold removes whatever
weak directional signal exists at t=3/t=4, collapsing onto a shared hard
core of high-confidence detections.

## 8. Caveats / risk register

1. **Three-way null is preregistered-but-post-errata**: H12 v2 deviated from the preregistered H12 trigger (running without H8 showing library-size significance; see E52 in `protocol-errata.md`). The run was justified under orthogonality + publishable-null rationale. The null is real; the framing as preregistered-closure requires the E52 disclosure.
2. **R2 = H8 v2 Scale-8 reuse**: R2 (balanced 4:4) is byte-identical to H8 v2 Scale-8 `pool_160_hp4hn4`. This is not double-counting — the design reuses R2 as a shared anchor across the two studies — but the R2 CI is not a fresh sample from a re-run; downstream analyses that bootstrap at the run level must treat R2 as a single-study contribution.
3. **Two transient Gemini 3 Flash JSON parse failures in R3**: impact minor (2 tiles drop from 5-vote to 4-vote consensus; both still qualify for t = 4 primary). Mentioned for transparency.
4. **Directional prediction falsified, not confirmed**: the preregistered prediction was that higher HP:HN ratio would improve recall; R3's recall is **not** higher. The null framing is correct (no significant difference), but the directional prediction's falsification is a separate methodological data point — it eliminates the proposer-stage HP-recall mechanism as a library-design lever.
5. **F1 ceiling 0.70 – 0.73 is Gemini-3-Flash-under-these-settings specific**. A different model family (e.g., `gemini-3-pro`) or different temperature / thinking setting could move the ceiling. The paper should not cite the 0.73 as a model-intrinsic cap.
6. **Era 3 scope only**: H12 v2 is evaluated on the 327-tile Era 3 scope (see `evaluation-scopes.md`). Cross-era generalisation to the 340-tile Era 1 or 487-tile Era 2 scopes is not tested here.

## 9. Execution summary

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

### 9.1 Two transient tile-level failures in R3

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

## 10. Artefacts

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

## 11. Scripts used

| Phase | Script | Purpose |
|-------|--------|---------|
| 1 | `scripts/merge_passes.py --sweep` | Greedy consensus t=1..5 |
| 2 | `scripts/fuse_detections_wbf.py --config h12v2-*` | WBF variant C |
| 3 | `scripts/evaluate_detections.py` | F1/P/R with 1000-iteration bootstrap CIs |
| 4 | `scripts/pairwise_permutation_test.py --mode geojson` | Tile-level paired permutation |
| 5 | `scripts/apply_fdr_h12v2.py` | BH-FDR at q=0.05 over 3 contrasts |
| 6 | `scripts/summarise_h12v2.py` | Collated per-condition summary table |
