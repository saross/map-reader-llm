# Factor Analysis — Pairwise Permutation Test Results

> **Last revised**: 2026-08-02 (E72 — the Temperature family's headline
> recomputed from the retained clean contrasts). See
> [§ Changelog](#changelog) for revision history.
>
> **⚠ Superseded figures (2026-08-02, E72)**: four of the six Temperature
> contrasts — the three Group 4 rows (`Flash MIN text T=0.7` versus `T=1.0` at
> N=5/10/30) and the Group 12 row `T=0.7 vs T=1.0 (N=1, 384 px)` — pair a
> 487-tile arm against `outputs/h11/consensus-384-UNINTENDED-T1.0`, a 240-tile
> study scored against 487-tile bounds (coverage confound — see
> protocol-errata E43 correction block and E72), and understate that arm by
> ~0.17–0.19 F1. Those four rows are void; the § 5 table is retained as the
> dated record and its headline is corrected in place below. The other four
> families (Architecture, Thinking, Modality, Prompt Engineering) contain no
> confounded contrast and are unaffected — BH is applied within family here, so
> their q-values do not move. Recomputed family:
> `results/e43-board-regen/bh-families/`. Matched-scope analysis:
> `results/e43-matched-temperature/`. Do not cite the four affected rows.

**Study**: Cross-phase factor analysis across five factor families (Architecture, Thinking, Temperature, Modality, Prompt Engineering)
**Date**: 2026-03-31
**Test**: paired bootstrap-style permutation on tile-level F1 differences
**Corpus**: phase3a image-track + text-track matrices + 512 px Phase 2a–2e exploration (see §"Data provenance")
**Buffer**: 20 m
**Permutations**: 10,000 per contrast
**Seed**: 42
**FDR correction**: Benjamini–Hochberg at q = 0.05, applied **within each factor family** independently (families represent independent analytical questions, not a single multiple-comparison problem)

## 1. Executive summary

Across **61 pairwise contrasts over 5 factor families**, four factor
families produce significant effects and one is a clean null:

| Family | Contrasts | FDR-significant | Headline finding |
|--------|----------:|:---------------:|------------------|
| Architecture | 12 | **11 / 12** | Pipeline architecture dominates: N=1 → consensus (ΔF1 up to +0.39); +PV adds +0.05 to +0.09 on top |
| Thinking | 6 | **5 / 6** | HIGH > MINIMAL at consensus across text + image; non-significant only at Flash N=1 image |
| Temperature | 2 usable (6 published) | **1 / 2** | T=0.7 > T=1.0 at single-pass on the Phase 2b text track (ΔF1 +0.074, recomputed q = 0.011); the image track is null (+0.015, ns). The four Flash MIN text contrasts are void under E72 — see § 5 [corrected 2026-08-02, E72] |
| Modality | 9 | **8 / 9** | Text > image at Pro level and at PV stage; image wins at Flash N=1 (asymmetric optimisation story) |
| Prompt Engineering | 28 | **0 / 28** | Library composition, example ordering, text treatment all null — consistent with H8 v2 / H10 v2 / H12 v2 nulls |

**Paper-headline implication**: the factors that measurably affect
detection F1 are architectural choices (consensus, PV, model
family), thinking budget, temperature, and modality. The prompt-
level choices — which hard examples to include, what order to list
them in, how verbose the text scaffold is — are null to BH-FDR across
28 tested contrasts. This cleanly justifies the paper's claim that
library curation beyond canonical positives + nulls is not a lever.

The full matrix of contrasts appears in §§3–7 below, preserved
verbatim from the 2026-03-31 analysis output. Two 512 px Temperature
rows have incomplete metadata (see §"Caveats" item 3); their ΔF1
and p-values are valid but their condition labels and per-condition
F1s are absent from the source JSON.

## 2. Methods

### Permutation test design

For each pairwise contrast (condition A vs condition B):

1. Compute observed ΔF1 = F1(A) − F1(B) at the 20 m buffer on the
   shared tile-scope matching both conditions' bounds.
2. Under the null hypothesis of no difference, sign-flip each tile's
   contribution (A's TP/FP/FN and B's TP/FP/FN are interchangeable
   at that tile) with probability 0.5 per tile, recomputing ΔF1 per
   permutation.
3. The p-value is the fraction of 10,000 permutations with |ΔF1|
   ≥ |observed| (two-sided).
4. BH-FDR correction applied within each factor family (Architecture,
   Thinking, Temperature, Modality, Prompt Engineering) at q = 0.05.

### Data provenance

Per-contrast F1 values are drawn from:

- **Phase 3a image-track matrix** (`outputs/phase3a-image-matrix/`) — supplies
  the Flash HIGH / MEDIUM / MINIMAL × text / image × 5-of-5 / 4-of-5 /
  3-of-5 cells for Architecture, Thinking, and Modality families.
- **Phase 3a text-track matrix** (`outputs/phase3a-text-matrix/`) — supplies
  the K=10 / K=30 text-track cells used in Architecture and Thinking.
- **Phase 3a consensus + PV** (`outputs/55maps-image-generalisation/` pipeline
  sans-55-maps) — supplies the +PV contrasts.
- **Pro family** (`outputs/pro-gold-standard/`) — supplies the Pro text
  / Pro image cells for Architecture and Modality.
- **Phase 2b 512 px temperature** (pre-retest 60-tile pilot) — supplies
  the Temperature contrasts except for the two 512 px rows whose
  source labels are missing from the aggregator JSON (see Caveats).
- **Phase 2c / 2d / 2e (512 px)** — supplies the Prompt Engineering
  contrasts (library composition / text treatment / example ordering).

All F1 values in the tables are at 20 m buffer; for consistency with
the Phase 2b retest and 55-map multi-buffer analyses, the 20 m buffer
is the preregistered primary evaluation tolerance.

### FDR correction — why within-family

The five families represent different scientific questions:

- *Architecture*: how does pipeline structure affect performance?
- *Thinking*: how much does reasoning budget help?
- *Temperature*: how does sampling randomness affect single-pass F1?
- *Modality*: does text-only or image-using do better?
- *Prompt Engineering*: do library / prompt-surface choices matter?

Combining all 61 contrasts into one FDR would bias toward the
largest family (Prompt Engineering, 28 contrasts, all null), masking
significance in the smaller families. Within-family FDR protects each
scientific question independently while preserving type-I error
control within the question.

## 3. Architecture (11 of 12 significant)

| Question | Condition A | Condition B | F1_A | F1_B | ΔF1 | p (raw) | p (adj) | Sig |
|---|---|---|---|---|---|---|---|---|
| N=1 vs consensus (FH text) | FH text run_1 (N=1) | FH text 5-of-5 consensus | 0.392 | 0.779 | −0.387 | 0.0000 | 0.0000 | *** |
| PV on single-pass text | Text baseline + PV | Single-pass text 5-of-5 | 0.814 | 0.544 | +0.270 | 0.0000 | 0.0000 | *** |
| N=1 vs consensus (FH image) | FH image run_1 (N=1) | FH image 3-of-5 consensus | 0.515 | 0.727 | −0.212 | 0.0000 | 0.0000 | *** |
| PV on single-pass image | Image baseline + PV | Single-pass text 5-of-5 | 0.717 | 0.544 | +0.173 | 0.0000 | 0.0000 | *** |
| N=1 vs consensus (FM text) | FM text run_1 (N=1) | FM text 5-of-5 consensus | 0.493 | 0.640 | −0.147 | 0.0000 | 0.0000 | *** |
| N=1 vs consensus (Pro text) | Pro text run_1 (N=1) | Pro text 3-of-5 consensus | 0.738 | 0.840 | −0.102 | 0.0000 | 0.0000 | *** |
| PV vs consensus | Flash HIGH text 4-of-5 + PV | Flash HIGH text 5-of-5 | 0.864 | 0.779 | +0.085 | 0.0000 | 0.0000 | *** |
| PV verifier thinking | Flash HIGH text 4-of-5 + medium vf | Flash HIGH text 5-of-5 | 0.859 | 0.779 | +0.080 | 0.0000 | 0.0000 | *** |
| PV vs consensus | Flash HIGH text 16-of-30 + PV | Flash HIGH text 26-of-30 | 0.890 | 0.814 | +0.076 | 0.0000 | 0.0000 | *** |
| PV vs consensus | Flash HIGH text 9-of-10 + PV | Flash HIGH text 9-of-10 | 0.856 | 0.797 | +0.060 | 0.0000 | 0.0000 | *** |
| PV vs consensus (image) | Flash HIGH image 3-of-5 + PV | Flash HIGH image 3-of-5 | 0.778 | 0.727 | +0.051 | 0.0004 | 0.0004 | *** |
| PV vs consensus (Pro) | Pro HIGH text 3-of-5 + PV | Pro HIGH text 3-of-5 | 0.849 | 0.840 | +0.009 | 0.2580 | 0.2580 | ns |

**Reading**: The top six rows ("N=1 vs consensus" and "PV on single-pass")
show single-pass → consensus / PV gains of +0.10 to +0.39 F1 — the
largest effects in the study. The next six rows ("PV vs consensus")
show +PV gains on top of already-consensus output, +0.05 to +0.09 F1,
all significant except the Pro HIGH text 3-of-5 cell (where consensus
already saturates the verifier's reachable precision). Architecture is
the single most consequential factor family.

## 4. Thinking (5 of 6 significant)

| Question | Condition A | Condition B | F1_A | F1_B | ΔF1 | p (raw) | p (adj) | Sig |
|---|---|---|---|---|---|---|---|---|
| HIGH vs MINIMAL (text N=10) | Flash HIGH text 9-of-10 | Flash MIN text 10-of-10 | 0.797 | 0.633 | +0.164 | 0.0000 | 0.0000 | *** |
| HIGH vs MINIMAL (text N=30) | Flash HIGH text 26-of-30 | Flash MIN text 29-of-30 | 0.814 | 0.661 | +0.153 | 0.0000 | 0.0000 | *** |
| HIGH vs MINIMAL (text N=5) | Flash HIGH text 5-of-5 | Flash MIN text 5-of-5 | 0.779 | 0.640 | +0.139 | 0.0000 | 0.0000 | *** |
| HIGH vs MINIMAL (N=1 text) | FH text run_1 (N=1) | FM text run_1 (N=1) | 0.392 | 0.493 | −0.101 | 0.0000 | 0.0000 | *** |
| HIGH vs MINIMAL (image N=5) | Flash HIGH image 3-of-5 | Flash MIN image 4-of-5 | 0.727 | 0.664 | +0.063 | 0.0003 | 0.0004 | *** |
| HIGH vs MINIMAL (N=1 image) | FH image run_1 (N=1) | FM image run_1 (N=1) | 0.515 | 0.560 | −0.045 | 0.0588 | 0.0588 | ns |

**Reading**: HIGH thinking beats MINIMAL at consensus N ≥ 5 on both
text and image tracks (ΔF1 +0.06 to +0.16). The two N=1 single-pass
contrasts invert: MINIMAL outperforms HIGH at N=1 (text ΔF1 = −0.10
significant; image ΔF1 = −0.05 non-significant). This is consistent
with the "HIGH thinking adds variance that consensus averages out"
interpretation: at N=1 the extra thinking-driven variance is a
handicap; at N ≥ 5 consensus exploits it.

## 5. Temperature (1 of 2 usable contrasts significant)

> **[corrected 2026-08-02, E72]** This family was published as "5 of 6
> significant, ΔF1 +0.17 to +0.19". Four of its six contrasts — the three
> Group 4 rows and the Group 12 384 px N=1 row — score a 240-tile arm against
> 487-tile bounds and are void. Recomputing Benjamini–Hochberg over the two
> retained contrasts (family size 6 → 2) gives: Phase 2b text, ΔF1 +0.074,
> q = 0.011 (significant, was q = 0.0066); Phase 2b image, ΔF1 +0.015,
> q = 0.4763 (unchanged, still null). At matched 487-tile scope the Flash MIN
> text contrast reverses sign and is not significant (−0.021 at N=5, −0.034 at
> N=10; `results/e43-matched-temperature/`). The table below is retained as the
> dated record — read the first three rows and the 384 px N=1 row as
> superseded. Recomputed family:
> `results/e43-board-regen/bh-families/families_recomputed.md`.

| Question | Condition A | Condition B | F1_A | F1_B | ΔF1 | p (raw) | p (adj) | Sig |
|---|---|---|---|---|---|---|---|---|
| T=0.7 vs T=1.0 (N=30) | Flash MIN text T=0.7 29-of-30 | Flash MIN text T=1.0 22-of-30 | 0.661 | 0.467 | +0.194 | 0.0000 | 0.0000 | *** |
| T=0.7 vs T=1.0 (N=10) | Flash MIN text T=0.7 10-of-10 | Flash MIN text T=1.0 9-of-10 | 0.633 | 0.462 | +0.172 | 0.0000 | 0.0000 | *** |
| T=0.7 vs T=1.0 (N=5) | Flash MIN text T=0.7 5-of-5 | Flash MIN text T=1.0 5-of-5 | 0.640 | 0.471 | +0.168 | 0.0000 | 0.0000 | *** |
| T=0.7 vs T=1.0 (N=1, 384 px) | FM text T=0.7 run_1 (N=1) | FM text T=1.0 run_1 (N=1) | 0.493 | 0.390 | +0.103 | 0.0034 | 0.0051 | ** |
| T=0.7 vs T=1.0 (N=1, Phase 2b text) | P2b text T=0.7 run_1 | P2b text T=1.0 run_1 | 0.584 | 0.510 | +0.074 | 0.0055 | 0.0066 | ** |
| T=0.7 vs T=1.0 (N=1, Phase 2b image) | P2b image T=0.7 run_1 | P2b image T=1.0 run_1 | 0.536 | 0.521 | +0.015 | 0.4763 | 0.4763 | ns |

**Reading**: T=0.7 beats T=1.0 by +0.10 to +0.19 F1 on Flash MIN text
at all K values (N=1, 5, 10, 30). The Phase 2b N=1 text row also
supports T=0.7 > T=1.0 (+0.074, p_adj = 0.007). The Phase 2b N=1 image
row is the non-significant outlier (+0.015, p = 0.48) — consistent with
the pattern that image-track is less temperature-sensitive than text-
track at single-pass. Note the T values tested here (T=0.7 vs T=1.0)
differ from the Phase 2b retest's full 5-temperature sweep
(T=0.0 / 0.3 / 0.7 / 1.0 / 1.3) — this factor-analysis addresses a
narrower question (is T=0.7 better than T=1.0?) but on a wider
architectural grid (K=1 / 5 / 10 / 30 × text / image, all 384 px per
E41 production lock-in). The last two Phase 2b rows draw from the
same Phase 2b retest tree (`outputs/retest/phase2b/track{1-image,2-text}/T{0.7,1.0}/run_1/`) at run_1 single-pass.

## 6. Modality (8 of 9 significant)

| Question | Condition A | Condition B | F1_A | F1_B | ΔF1 | p (raw) | p (adj) | Sig |
|---|---|---|---|---|---|---|---|---|
| Text vs image (N=1, Pro) | Pro text run_1 (N=1) | Pro image run_1 (N=1) | 0.738 | 0.590 | +0.149 | 0.0000 | 0.0000 | *** |
| Text vs image (Pro consensus N=5) | Pro text 3-of-5 consensus | Pro image 3-of-5 consensus | 0.840 | 0.700 | +0.141 | 0.0000 | 0.0000 | *** |
| Text vs image (N=1, FH) | FH text run_1 (N=1) | FH image run_1 (N=1) | 0.392 | 0.515 | −0.123 | 0.0001 | 0.0002 | *** |
| Text vs image (baseline + PV) | Text baseline + PV | Image baseline + PV | 0.814 | 0.717 | +0.098 | 0.0000 | 0.0000 | *** |
| Text vs image (PV) | Flash HIGH text 4-of-5 + PV | Flash HIGH image 3-of-5 + PV | 0.864 | 0.778 | +0.086 | 0.0000 | 0.0000 | *** |
| Text vs image (N=1, FM) | FM text run_1 (N=1) | FM image run_1 (N=1) | 0.493 | 0.560 | −0.067 | 0.0158 | 0.0178 | * |
| Text vs image (N=10) | Flash HIGH text 9-of-10 | Flash HIGH image 6-of-10 | 0.797 | 0.740 | +0.057 | 0.0054 | 0.0081 | ** |
| Text vs image | Flash HIGH text 5-of-5 | Flash HIGH image 3-of-5 | 0.779 | 0.727 | +0.052 | 0.0143 | 0.0178 | * |
| Text vs image (MINIMAL) | Flash MIN text 5-of-5 | Flash MIN image 4-of-5 | 0.640 | 0.664 | −0.024 | 0.3604 | 0.3604 | ns |

**Reading**: Text > image at Pro level (ΔF1 +0.14 to +0.15) and at
Flash HIGH consensus + PV stages (+0.05 to +0.10). Image > text at
Flash N=1 and Flash MINIMAL N=1 — the FH and FM N=1 rows invert the
text-advantage. This is the asymmetric-optimisation trajectory
discussed in Obs 204 / 205: image improvements disproportionately
help image-using conditions, while text improvements are limited to
the text prompt. On the current pipeline, Flash benefits more from
text at consensus stages; Pro universally prefers text.

## 7. Prompt Engineering (0 of 28 significant)

| Question | Condition A | Condition B | F1_A | F1_B | ΔF1 | p (raw) | p (adj) | Sig |
|---|---|---|---|---|---|---|---|---|
| Example ordering | P2e canonical-last | P2e random | 0.631 | 0.571 | +0.061 | 0.0019 | 0.0532 | ns |
| Example ordering | P2e config-default | P2e random | 0.606 | 0.571 | +0.035 | 0.0563 | 0.5488 | ns |
| Example ordering | P2e canonical-first | P2e canonical-last | 0.599 | 0.631 | −0.033 | 0.1366 | 0.6375 | ns |
| Library composition (image) | P2c Image plus-hp | P2c Image pure-positive-canon | 0.599 | 0.568 | +0.031 | 0.0907 | 0.6349 | ns |
| Example ordering | P2e canonical-first | P2e random | 0.599 | 0.571 | +0.028 | 0.1218 | 0.6375 | ns |
| Example ordering | P2e canonical-last | P2e config-default | 0.631 | 0.606 | +0.026 | 0.1857 | 0.7428 | ns |
| Library composition (image) | P2c Image pure-positive-canon | P2c Image scale-8 | 0.568 | 0.587 | −0.019 | 0.2757 | 0.7957 | ns |
| Library composition (image) | P2c Image canonical | P2c Image plus-hp | 0.581 | 0.599 | −0.017 | 0.3691 | 0.7957 | ns |
| Library composition (image) | P2c Image pure-positive-canon | P2c Image scale-4 | 0.568 | 0.584 | −0.016 | 0.4653 | 0.7957 | ns |
| Text treatment (text) | P2d Text terse | P2d Text verbose | 0.598 | 0.583 | +0.015 | 0.4263 | 0.7957 | ns |
| Library composition (image) | P2c Image plus-hp | P2c Image scale-4 | 0.599 | 0.584 | +0.015 | 0.5115 | 0.7957 | ns |
| Library composition (image) | P2c Image canonical | P2c Image pure-positive-canon | 0.581 | 0.568 | +0.014 | 0.4001 | 0.7957 | ns |
| Library composition (text) | P2c Text plus-hp | P2c Text scale-4 | 0.597 | 0.609 | −0.013 | 0.0588 | 0.5488 | ns |
| Library composition (image) | P2c Image plus-hp | P2c Image scale-8 | 0.599 | 0.587 | +0.012 | 0.4983 | 0.7957 | ns |
| Library composition (text) | P2c Text plus-hp | P2c Text scale-8 | 0.597 | 0.607 | −0.010 | 0.3089 | 0.7957 | ns |
| Library composition (text) | P2c Text plus-hp | P2c Text pure-positive-canon | 0.597 | 0.605 | −0.008 | 0.6080 | 0.8147 | ns |
| Library composition (text) | P2c Text canonical | P2c Text plus-hp | 0.605 | 0.597 | +0.007 | 0.5630 | 0.8147 | ns |
| Example ordering | P2e canonical-first | P2e config-default | 0.599 | 0.606 | −0.007 | 0.6401 | 0.8147 | ns |
| Library composition (image) | P2c Image canonical | P2c Image scale-8 | 0.581 | 0.587 | −0.005 | 0.7611 | 0.9266 | ns |
| Library composition (text) | P2c Text canonical | P2c Text scale-4 | 0.605 | 0.609 | −0.005 | 0.6216 | 0.8147 | ns |
| Library composition (text) | P2c Text pure-positive-canon | P2c Text scale-4 | 0.605 | 0.609 | −0.005 | 0.2623 | 0.7957 | ns |
| Library composition (image) | P2c Image scale-4 | P2c Image scale-8 | 0.584 | 0.587 | −0.003 | 0.8880 | 0.9497 | ns |
| Library composition (text) | P2c Text canonical | P2c Text scale-8 | 0.605 | 0.607 | −0.003 | 0.8057 | 0.9400 | ns |
| Library composition (text) | P2c Text pure-positive-canon | P2c Text scale-8 | 0.605 | 0.607 | −0.003 | 0.4549 | 0.7957 | ns |
| Text treatment (image) | P2d Image terse | P2d Image verbose | 0.605 | 0.603 | +0.003 | 0.8779 | 0.9497 | ns |
| Library composition (text) | P2c Text scale-4 | P2c Text scale-8 | 0.609 | 0.607 | +0.002 | 0.4338 | 0.7957 | ns |
| Library composition (image) | P2c Image canonical | P2c Image scale-4 | 0.581 | 0.584 | −0.002 | 0.9158 | 0.9497 | ns |
| Library composition (text) | P2c Text canonical | P2c Text pure-positive-canon | 0.605 | 0.605 | −0.000 | 1.0000 | 1.0000 | ns |

**Reading**: Zero of 28 Prompt Engineering contrasts reach
significance after BH-FDR at q = 0.05. The two contrasts with the
smallest raw p-values (P2e canonical-last vs P2e random, p = 0.002;
P2c Text plus-hp vs P2c Text scale-4, p = 0.059) are both swamped by
the 28-way BH correction. Library composition, example ordering, and
text treatment (terse vs verbose) are all null at this level of power.
These 512 px Phase 2a–2e contrasts are consistent with the H8 v2
(Obs 238), H10 v2 (Obs 236), and H12 v2 (Obs 239) null re-runs at
384 px under the production pipeline — together forming a
**five-study convergent null** on the library / prompt-surface axis.

## 8. Caveats

1. **Within-family FDR is methodologically defensible but not the
   only reasonable choice.** A referee could argue for a global 61-way
   FDR, under which some of the Thinking, Temperature, and Modality
   contrasts with raw p in the 0.004–0.06 range would become
   non-significant. The within-family framing is pre-specified in
   this analysis and is consistent with treating each family as a
   scientific question; alternative framings are noted here for
   transparency.
2. **Paired permutation requires matched tile-scope.** Contrasts that
   span different evaluation scopes (e.g. 340-tile pilot vs 487-tile
   production) could not be tested here and are excluded. All 61
   contrasts are within-scope paired tests.
3. **Two Temperature rows were mislabelled "512 px" and had blank
   metadata until Session 75 (2026-04-24)**. The rows originally
   labelled "T=0.7 vs T=1.0 (512 px text/image)" were discovered to
   be (a) schema-mismatched during aggregation (the aggregator
   `scripts/collect-factor-analysis.py` read `global_a`/`global_b`
   keys but the source permutation JSONs use
   `condition_a`/`condition_b`, losing labels + per-condition
   metrics) and (b) **mislabelled as 512 px when the source is
   actually Phase 2b retest at 384 px N=1**
   (`outputs/retest/phase2b/track{1-image,2-text}/T{0.7,1.0}/run_1/`).
   Both issues were corrected in the same commit that created this
   level-up: the rows are relabelled "(N=1, Phase 2b text/image)",
   the labels and F1 values are recovered from the source permutation
   JSONs' `condition_a`/`condition_b` blocks, and the aggregator
   script has been patched to handle both schemas defensively. The
   ΔF1 and p-values were always valid (the permutation test itself
   is unaffected by the aggregation bug).
4. **Prompt Engineering null at 512 px does not preclude effects at
   384 px under PV.** The 28 Prompt Engineering contrasts are all at
   the 512 px Phase 2a–2e scope (pre-production). The H8 v2 / H10 v2 /
   H12 v2 384 px re-runs under the production pipeline also return
   null on library composition, HP:HN ratio, and pool size (Obs 236 /
   238 / 239), strengthening the null interpretation at the pipeline
   that the paper actually cites. The 512 px null here is not the
   paper's primary claim; it is one of five convergent studies.
5. **F1 values in the tables are at 20 m buffer point estimates.** No
   bootstrap CIs are reported here because the test of interest is
   the paired ΔF1 permutation p-value, not a per-condition CI. Per-
   condition CIs live in the source evaluation JSONs cited in
   §"Data provenance".

## 9. Paper implications

1. **Five-family factor-analysis is a clean paper-Results structure.**
   The paper's "which factors matter" section can present four
   families of significant effects (Architecture, Thinking,
   Temperature, Modality) and one null family (Prompt Engineering)
   with within-family FDR control. This is the most legible
   structure for a reader who wants a quick answer to "what
   matters?".
2. **Architecture is the dominant axis.** The largest observed
   effects in the study (ΔF1 up to +0.39 for N=1 → consensus +PV)
   are architectural, not model- or prompt-level. The paper's
   pipeline-design story (consensus → PV → tile-size → calibration
   pool) is supported quantitatively here.
3. **Five-study convergent library null.** Prompt Engineering (0/28
   at 512 px), H8 v2 (0/7 at 384 px under E51), H10 v2 (0/1 at
   384 px under E49), H12 v2 (0/3 at 384 px under E52), and the five-
   config HP:HN cross-hypothesis matrix (see `results/h10/analysis_summary.md`
   §"Cross-hypothesis coverage") all return library / prompt-surface
   null. This is a stronger claim than any individual hypothesis
   alone and is the cleanest single sentence the paper's Discussion
   can point at for "what doesn't matter".
4. **The temperature claim rests on Phase 2b, not on this family.**
   *[corrected 2026-08-02, E72]* The published version of this item
   read "T=0.7 > T=1.0 is robust across K … ΔF1 = +0.10 to +0.19".
   The four Flash MIN text contrasts that supported it are void
   (coverage confound; at matched scope the effect reverses sign and
   is not significant). What survives here is the single-pass Phase 2b
   text contrast (ΔF1 +0.074, recomputed q = 0.011), with the Phase 2b
   image track null (+0.015, ns). The paper's practitioner claim
   ("change Gemini's T=1.0 default") should be sourced to the
   preregistered Phase 2b sweep (text +0.072, FDR p = 0.004; image
   +0.014, ns) — that claim stands, but as a text-track finding rather
   than a universal T=0.7 superiority across K.
5. **Modality effects are model-dependent.** Text > image at Pro;
   ambiguous or flipped at Flash N=1. The paper's modality claim
   should be stated conditionally on model family rather than as
   a blanket "text-only is better".

## 10. Reproducibility

| Metric | Value |
|--------|-------|
| Permutations per contrast | 10,000 |
| Seed | 42 |
| Buffer | 20 m |
| FDR method | Benjamini–Hochberg at q = 0.05, within-family |
| Test statistic | paired ΔF1 under tile-level sign-flip |
| Analysis date | 2026-03-31 |
| Source JSON | `results/factor-analysis/factor_analysis_results.json` (61 contrasts) |
| Source CSV | `results/factor-analysis/factor_analysis_results.csv` |

## 11. Artefacts

- `factor_analysis_results.json` — 61-contrast source (this doc's
  authoritative data layer)
- `factor_analysis_results.csv` — same data, flat CSV
- `factor_analysis_results.md` — this doc (narrative + tables)
- Underlying F1 sources: see §"Data provenance" for the per-family
  source trees (phase3a-image-matrix, phase3a-text-matrix, 55maps-
  image-generalisation pipeline, pro-gold-standard, Phase 2a–2e
  512 px exploration, Phase 2b 60-tile pilot pre-retest)

## 12. Cross-hypothesis links

- Phase 2b Retest (H7 Temperature): `results/retest/phase2b/analysis_summary.md`
- H8 v2 library composition: `results/h8-v2/analysis_summary.md`
- H10 v2 calibration-pool size: `results/h10/analysis_summary.md`
- H12 v2 HP:HN ratio: `results/h12-v2/analysis_summary.md`
- H11 tile size: `results/h11/analysis_summary.md`
- Paper-eval MCC family: `results/paper-eval/mcc/report.md`
- Meta-findings synthesis: `results/meta-findings-summary.md` (Themes T2 failure taxonomies, T5 library-axis closure)
- Working-notes Obs 204 / 205 — asymmetric modality-optimisation trajectory
- Working-notes Obs 236 / 238 / 239 — 384 px library-axis nulls

---

**Status**: Paper-citation-ready factor-analysis report. The 61
pairwise contrasts across 5 families, preserved verbatim from the
2026-03-31 source tables, now sit inside a narrative frame with
executive summary, methods, caveats, and paper implications. The
two 512 px Temperature rows with incomplete condition metadata are
explicitly flagged; their statistical outputs (ΔF1, p-values) remain
valid.

## Changelog

### 2026-08-02 — Temperature family corrected under E72

**Trigger**: protocol erratum E72 (coverage confound) and the Principal
Investigator's remediation ruling. Four of the six Temperature
contrasts score `outputs/h11/consensus-384-UNINTENDED-T1.0` — a
240-tile study — against 487-tile bounds, so their ΔF1 understates the
T=1.0 arm by ~0.17–0.19.

| Claim | Before | After |
|---|---|---|
| Temperature family headline (§ 1 table, § 5 heading) | 6 contrasts, **5 / 6** significant, "ΔF1 +0.17 to +0.19" | 2 usable contrasts (6 published), **1 / 2** significant, ΔF1 +0.074 (text, q = 0.011) and +0.015 (image, ns) |
| Phase 2b text contrast q-value | 0.0066 (family of 6) | **0.0110** (family of 2) |
| Phase 2b image contrast q-value | 0.4763 | 0.4763 (unchanged) |
| § 9 implication 4 | "T=0.7 > T=1.0 is robust across K … +0.10 to +0.19" | Rewritten: the claim is sourced to the preregistered Phase 2b sweep (text +0.072, FDR p = 0.004; image +0.014, ns), not to this family |

**What did NOT change**: the § 5 table itself (retained as the dated
record under the superseded-figures banner); the Architecture,
Thinking, Modality and Prompt Engineering families and all their
q-values (Benjamini–Hochberg is applied within family here, so
dropping Temperature members cannot move them — verified by
recomputation); the within-family FDR framing; the data-provenance and
caveats sections.

**Landed by**: `scripts/regen_e43_board.py`; recomputed family at
`results/e43-board-regen/bh-families/families_recomputed.md`.

### 2026-03-31 — Original publication

61 pairwise permutation contrasts across five factor families
(Architecture 12, Modality 9, Thinking 6, Temperature 6, Prompt
Engineering 28), Benjamini–Hochberg-corrected within each family at
q = 0.05, wrapped in a narrative frame with executive summary,
methods, caveats and paper implications. Session 75 (2026-04-24) later
repaired two 512 px Temperature rows' condition metadata without
changing their statistics.
