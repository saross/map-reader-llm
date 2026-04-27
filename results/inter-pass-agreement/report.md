# Inter-Pass Agreement Analysis

**Author**: Shawn Ross, Claude Code
**Generated**: 2026-04-27
**Script**: `scripts/analyse_inter_pass_agreement.py` (v1.0.0)
**Companions**: `agreement.json`, `report_autogen.md`, `figures/`

## 1. Purpose and design

Quantifies inter-pass agreement among replicate VLM detection passes within each Phase 3a stratum and the gold-standard-v2 (GS-v2) 4-map 487-tile reference cell. Two kappa flavours are reported alongside a borderline-instability count:

1. **Candidate-match kappa** — operates on the union cluster set built by `lib_consensus.cluster_across_passes` at 20 m UTM-32635. For each cluster *c* and each pass *i*, the rating is `1` if pass *i* contributed at least one detection to *c*, else `0`. Cohen's kappa is computed pairwise. Observed agreement P_o is reported alongside to make the marginal-prevalence kappa paradox visible.
2. **Tile-presence kappa** — denominator is the intersection of `*.tiles.json` `completed` lists across all retained passes (typically 487 for the 384 px corpus, 340 for the retest corpus). For each tile *t* and pass *i*, the rating is `1` if pass *i* made any detection on *t*, else `0`.
3. **Borderline-instability** — at consensus threshold *t*\* (from `secondary_effects.md` / `phase3a-text-matrix/secondary_effects.json` for matrix cells; canonical 4-of-5 for GS-v2; fallback `round(K · 0.7) = 21` for K=30 retest), B = {clusters with `vote_count` in {*t*\*−1, *t*\*, *t*\*+1}}. Reported: |B|, |B| as % of consensus@*t*\*, GT mounds gained/lost (spatial join at 20 m to `inputs/vectors/references/mounds-reference.geojson`), and **fragility ratio** = |B| / |consensus@*t*\*|.

A 30 m cluster-radius sensitivity row is added for GS-v2.

## 2. Strata covered

| Stratum                | Cells | K       | Tiles |
|------------------------|------:|---------|------:|
| `phase3a_image_matrix` |     8 | 3 / 10  |   487 |
| `phase3a_text_matrix`  |     8 | 3 / 10 / 30 | 487 |
| `scale4_t07`           |     1 | 10      |   487 |
| `phase3a_retest`       |    11 | 30      |   340 |
| `gold_standard_v2`     |     1 | 5       |   487 |
| **Total**              | **29** | —      |     — |

K=3 cells (phase3a image / text T=0.0) are retained per the K ≥ 3 spec, but their borderline metrics are naturally inflated because the band {*t*\*−1, *t*\*, *t*\*+1} covers most of the available vote-count space. Phase3a retest borderline rows use the `round(K · 0.7) = 21` fallback anchor and should be read in **relative** comparison only.

## 3. Headline findings

### 3.1 Pairwise candidate-match kappa range (20 m)

Off-diagonal mean kappa across 29 cells spans **[0.146, 0.724]**. Both extremes are partly driven by the marginal-prevalence kappa paradox (P_o for GS-v2 at 0.602 indicates ~60 % cluster-slot agreement per pair, but kappa is only 0.15 because most clusters appear in only one pass).

| Rank | Cell                                          | kappa | P_o   | Note |
|-----:|-----------------------------------------------|------:|------:|------|
| Highest | `phase3a_retest / text-T0.3` (K=30)         | 0.724 | 0.862 | High agreement on candidate set |
| —    | `phase3a_retest / image-T0.3` (K=30)          | 0.666 | 0.834 | Image close behind |
| —    | `phase3a_text_matrix / MIN-T0.7` (K=30)       | 0.654 | 0.839 | MIN consistently > HIGH at matched K |
| Lowest | `gold_standard_v2 / detect_brief-text` (K=5) | 0.146 | 0.602 | Long tail of one-pass clusters |
| —    | `phase3a_text_matrix / HIGH-T0.0` (K=3)       | 0.175 | 0.729 | K=3, text-T0 over-detects |
| —    | `phase3a_text_matrix / MIN-T0.0` (K=3)        | 0.224 | 0.823 | Same regime, MIN |

K=30 phase3a retest cells have the highest candidate-match kappas — a direct consequence of the larger denominator and uniform sampling regime.

### 3.2 The MIN-vs-HIGH inversion

At matched K and temperature, MINIMAL-thinking cells consistently show **higher candidate-match kappa** than HIGH:

| T   | HIGH κ_cm | MIN κ_cm | Δ      |
|----:|----------:|---------:|-------:|
| 0.3 | 0.365     | 0.607    | +0.242 |
| 0.7 | 0.336     | 0.529    | +0.193 |
| 1.0 | 0.250     | 0.456    | +0.206 |

(K=10 phase3a image matrix; text matrix shows similar pattern, K=30: MIN-T0.7 κ = 0.654 vs HIGH-T0.7 κ = 0.381.)

This **inverts** the F1 / MCC ranking. The story: HIGH thinking generates more diverse candidate sets per pass (e.g. 11,731 union clusters for HIGH-T0.7 text vs 2,786 for MIN-T0.7 text), so per-pass coverage of the union is lower. This is the **diversity-dividend signature** documented in Obs 141. **Kappa here is a diversity metric, not a quality metric.**

### 3.3 Borderline / fragility findings

K=10 phase3a image cells (published *t*\* from `secondary_effects.md`):

| Cell        | *t*\* | Cons n | Border n | Fragility | GT lost % | GT gained % |
|-------------|------:|-------:|---------:|----------:|----------:|------------:|
| HIGH-T0.7   |     7 |    404 |      181 |     0.448 |      5.10 |        3.34 |
| HIGH-T1.0   |     6 |    437 |      195 |     0.446 |      5.10 |        3.69 |
| MIN-T0.7    |     8 |    493 |      175 |     0.355 |      4.04 |        2.28 |
| MIN-T1.0    |     8 |    466 |      208 |     0.446 |      5.45 |        2.64 |
| SCALE4-T0.7 |     6 |    404 |      150 |     0.371 |      4.04 |        3.34 |

- **HIGH-T0.7 / HIGH-T1.0** sit at fragility ≈ 0.45 with 5 % GT lost on raising *t*\*.
- **SCALE4-T0.7** has the lowest fragility of K=10 winners (0.371), consistent with its MCC-leader status.
- **MIN-T0.7** is most stable (fragility 0.355, GT lost 4.04 %), corroborating its widest-plateau status from threshold-robustness analysis.
- **HIGH-T0.3 / MIN-T0.3** have fragility > 1 because *t*\* = K = 10: structural artefact of corner thresholds.
- **GS-v2** (K=5, *t*\*=4): fragility 1.425, 8.26 % GT lost on raising to 5, 3.51 % gained on lowering to 3 — motivates the 4-of-5 consensus choice over 5-of-5.

K=30 retest cells (with `round(K · 0.7) = 21` fallback anchor):

| Cell                | Fragility | GT lost % |
|---------------------|----------:|----------:|
| image-T0.3          |     0.059 |      0.18 |
| image-T0.7          |     0.098 |      1.76 |
| image-T1.0          |     0.114 |      1.76 |
| text-T0.3           |     0.053 |      0.70 |
| text-T0.7           |     0.062 |      0.53 |
| text-T1.0           |     0.086 |      0.88 |
| high-text-T0.3      |     0.133 |      1.23 |
| high-text-T0.7      |     0.151 |      1.58 |
| high-text-T1.0      |     0.152 |      1.93 |
| replication-high    |     0.136 |      1.58 |
| replication-minimal |     0.065 |      0.88 |

Fragility increases monotonically with temperature within each sub-track, and HIGH > MIN at matched temperature (high-text-T1.0=0.152 vs text-T1.0=0.086). **Variance hypothesis corroborated**: high temperature plus HIGH thinking yields more borderline noise.

The naive cross-K check ("HIGH-T1.0 fragility should exceed MIN-T0.0") does **not** corroborate, because MIN-T0.0 is K=3 with *t*\*=2 — the band covers the entire vote space, a structural artefact rather than a falsification.

### 3.4 Cluster-radius sensitivity (GS-v2)

| Radius | kappa_cm mean | P_o mean |
|-------:|-------------:|---------:|
| 20 m   | 0.146        | 0.602    |
| 30 m   | 0.185        | 0.608    |

Increasing radius from 20 m to 30 m raises kappa from 0.146 to 0.185 (+27 % relative), with P_o nearly unchanged. The increase is the expected effect of merging near-neighbour pass-singletons; the 20 m headline is conservative in the sense of kappa-suppression from positional jitter, not genuine disagreement.

## 4. Caveats

- **Cluster-radius sensitivity**: 20 m default; 30 m sensitivity for GS-v2 only. Relative ordering of cells within a stratum is unlikely to flip at 30 m.
- **Tile-denominator alignment**: tile-presence kappa uses the intersection of per-pass `*.tiles.json` `completed` lists. No passes were dropped (all had a tiles.json). For GS-v2 the intersection is 485 / 487 (two tiles failed in some passes); other cells equal corpus size.
- **Marginal-prevalence kappa paradox**: P_o reported alongside kappa throughout. For cells with long tails of one-pass clusters (GS-v2, HIGH-T0.0 text), kappa under-states agreement. For high-base-rate cells, kappa and P_o converge.
- **Borderline-anchor provenance**: matrix cells use published *t*\* from `secondary_effects.md` and `results/phase3a-text-matrix/secondary_effects.json`. GS-v2 uses canonical 4-of-5. Phase3a retest uses `round(K · 0.7) = 21` fallback — relative comparison only.
- **Independence of passes**: Cohen's kappa assumes independent raters. VLM passes share prompt, model, and image preprocessing — exchangeable but not strictly independent. Read kappa as the standard statistic conditional on this shared substrate, not as inter-rater reliability in the human-coding sense.

## 5. Files manifest

| File                            | Purpose |
|---------------------------------|---------|
| `agreement.json`                | Full per-pair K x K matrices + condition-level summaries. |
| `report.md`                     | This hand-authored synthesis. |
| `report_autogen.md`             | Auto-generated companion. |
| `figures/<stratum>__<cond>.png` | K x K candidate-match kappa heatmap per cell. |

## 6. Reproducibility

```bash
.venv/bin/python scripts/analyse_inter_pass_agreement.py \
    --output-dir results/inter-pass-agreement \
    --max-workers 4
```

Wall-clock on sapphire (4 workers): ≈ 9 s for all 29 cells. Deterministic — no random sampling — re-runs against the same input data yield byte-identical JSON.
