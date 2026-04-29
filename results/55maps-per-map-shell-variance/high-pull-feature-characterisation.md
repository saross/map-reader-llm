# High-pull tail map characterisation — qualitative cartographic-feature inspection

Per Obs 301, the per-map (50, 75] m shell-rate distribution on the 55-map text-track
runs is heavily right-skewed: median 0 % across three of four runs, with corpus
rates of 3–4 % driven by 2–3 high-pull maps showing rates of 33–75 %. This document
addresses the paper-relevant follow-up posed in Obs 301: do the high-pull maps
share an identifiable cartographic feature (dense numeric labels, vegetation
hatching, a stylistic variant) that explains their distractor-pull behaviour?

## Executive summary — verdict: HYPOTHESIS REJECTED

The hypothesis that high-pull maps share an identifiable cartographic feature is
**not supported** by qualitative inspection of the nine high-pull maps and three
low-pull controls. At 2,048 px-wide preview resolution:

1. The nine high-pull maps span the full range of cartographic landscape types
   present in the corpus — heavily forested mountainous (K-35-067-2, K-35-067-3,
   K-35-076-3), open agricultural plain (K-35-054-2, K-35-055-1), mixed
   forest-agricultural mosaic (K-35-042-3, K-35-051-3, K-35-066-3), and a coastal
   sheet (K-35-056-3). No single feature axis (label density, vegetation
   coverage, terrain type, settlement density, water-feature prevalence)
   separates them as a class.
2. Critically, control map K-35-074-3 (0 % shell rate in all four runs) is
   visually indistinguishable in cartographic character from the multi-run
   high-pull leader K-35-067-2 (heavily forested mountainous terrain, dense
   contours, sparse settlement, similar map-edition appearance). A
   cartographic-feature explanation would predict K-35-074-3 to also be a
   high-pull map; it is not.
3. The Obs 302 false-positive (FP) classification audit further weakens the
   hypothesis: per-map FP category distributions on the high-pull maps and the
   three controls are similar — contour-rings dominate in both groups, and
   absolute FP counts on controls (n = 8, 14, 19) are within or above the range
   of high-pull maps (n = 4–20). What separates high-pull from low-pull is not
   the *kind* of FPs raised, but whether those FPs happen to land within the
   (50, 75] m shell of a reference point — which is dominated by reference-point
   spatial density and small-denominator variance, not by map cartography.
4. A more parsimonious account: high-pull rates on the text track are produced
   by the **arithmetic of small denominators** (e.g., K-35-067-2 at T=0.7 has
   3 in-shell of only 4 total detections — the 75 % rate is a 3-detection signal),
   amplified where reference-point density is high enough that a few stray
   detections happen to fall near them. This is consistent with Obs 301's caveat
   that "thin-sample maps" drive the SD and tail-max values.

The paper Discussion should hedge accordingly: the per-map right-skew is a real
distributional finding worth reporting, but the high-pull tail is **not
attributable to identifiable cartographic features at the resolution available
here**. It is most likely a thin-sample / spatial-coincidence artefact compounded
by per-map heterogeneity in reference-point density.

## Methods

- **Inputs.** Per-map shell rates from
  `results/55maps-per-map-shell-variance/per_map_shell_rates.json`; FP category
  classifications from `results/55maps-fp-classification/fp_classifications.json`.
- **Maps inspected (12).** Nine high-pull maps drawn from the prompt — top-3 per
  run across T=0.3 text-HIGH, T=0.7 text-HIGH, image (T=0.7), and text-MIN:
  K-35-067-2, K-35-042-3, K-35-051-3, K-35-054-2_Atolov_4326, K-35-056-3,
  K-35-066-3, K-35-076-3, K-35-055-1, K-35-067-3. Three low-pull controls
  selected from maps with 0 % shell rate across all four runs:
  K-35-074-3, K-35-077-4, K-35-065-3_Glavan_4326.
- **Inspection method.** Each raster
  (`inputs/rasters/Russian1981_32635/<map>.tif`, 40–52 MB GeoTIFFs) was
  downsampled to a 2,048 px-wide PNG preview using
  `gdal_translate -outsize 2048 0 -of PNG -scale`, then visually inspected. One
  preview per map was sufficient for cartographic-feature inspection; specific
  FP-cluster regions were not reinspected at higher zoom because the
  Obs 302 categorical FP audit already provides the per-map
  contour-ring / number / settlement breakdown.
- **Resolution caveat.** At 2,048 px wide the broad cartographic character
  (terrain type, vegetation coverage, settlement density, contour density,
  water features, coastline / large water bodies) is legible. Specific
  contour-line numeric values, road class symbols, and small annotation labels
  are not legible. Claims below are restricted to features visible at this
  resolution.
- **Calibration.** "Sparse / moderate / dense" labels for label density,
  vegetation hatching, and contour density were applied consistently across all
  12 maps via direct visual comparison.

## Comparison table

Twelve maps. Max shell rate is the maximum across the four runs. "Runs in top-3"
identifies the run(s) for which the map appears in the high-pull triple per the
prompt; controls are blank. Numeric-label density, vegetation hatching, contour
density, and settlement density are coarse qualitative judgements at 2,048 px.

| Map | Top-3 in | Max rate | Label density | Vegetation hatching | Contour density | Settlement density | Other notable features |
|:---|:---|--:|:---|:---|:---|:---|:---|
| K-35-067-2 | T=0.3, T=0.7, MIN | 75.00 % | moderate | heavy (forested) | dense (mountainous) | sparse | river/stream system; high-relief mountainous |
| K-35-042-3 | T=0.3 | 33.33 % | moderate | moderate-heavy | dense (mountainous L half) | moderate | mixed valley + mountain; multiple settlements |
| K-35-051-3 | T=0.3, T=0.7 | 36.36 % | moderate-dense | moderate | moderate | moderate-dense | mixed forest/agricultural mosaic; multiple villages |
| K-35-054-2_Atolov_4326 | T=0.7 | 25.00 % | dense (near villages) | sparse | light-moderate | dense (many villages) | open agricultural plain; field-pattern hatching |
| K-35-056-3 | image | 50.00 % | sparse | moderate (forest L portion) | moderate (coastal hills) | sparse | **coastal — large sea (Black Sea) covers ~50 % of sheet** |
| K-35-066-3 | image | 42.86 % | moderate | moderate-heavy (patches) | moderate-dense | moderate | hilly mixed forest/open; villages and small streams |
| K-35-076-3 | image | 40.00 % | moderate | moderate | dense (mountainous) | moderate | mountainous valley network; river systems |
| K-35-055-1 | MIN | 42.86 % | moderate | sparse | light | dense (many villages) | open agricultural; field-pattern hatching |
| K-35-067-3 | MIN | 30.00 % | moderate | heavy (forested) | dense (mountainous) | sparse | heavily forested mountains; same character as K-35-067-2 |
| K-35-074-3 (control) | — | 0.00 % | moderate | heavy (forested) | dense (mountainous) | sparse | **visually indistinguishable from K-35-067-2/067-3** |
| K-35-077-4 (control) | — | 0.00 % | moderate | sparse | light | moderate | major river valley running W–E; open ground |
| K-35-065-3_Glavan_4326 (control) | — | 0.00 % | moderate | moderate | moderate | moderate-dense | mixed forest/open with multiple settlements; similar to K-35-051-3 / K-35-066-3 |

### FP category distribution per map (Obs 302 source data, all four runs combined)

| Map | Total FPs | Dominant FP category | Notable secondary categories |
|:---|--:|:---|:---|
| K-35-067-2 | 4 | contour-ring (2) | settlement (2) |
| K-35-042-3 | 11 | contour-ring (6) | benchmark (2), number (2) |
| K-35-051-3 | 17 | settlement (6) | contour-ring (5), water-feature (3), number (3) |
| K-35-054-2_Atolov_4326 | 6 | contour-ring (3) | number (2) |
| K-35-056-3 | 6 | vegetation (2), settlement (2) | contour-ring (1), number (1) |
| K-35-066-3 | 14 | contour-ring (7) | number (5) |
| K-35-076-3 | 19 | contour-ring (13) | water-feature (4) |
| K-35-055-1 | 12 | benchmark (4) | contour-ring (3), water-feature (2) |
| K-35-067-3 | 20 | contour-ring (5), number (5) | settlement (4), vegetation (3) |
| K-35-074-3 (control) | 8 | contour-ring (6) | water-feature (1), settlement (1) |
| K-35-077-4 (control) | 19 | contour-ring (10) | settlement (5), water-feature (2) |
| K-35-065-3_Glavan_4326 (control) | 14 | number (5) | contour-ring (4), settlement (2), water-feature (2) |

## Cross-cut analysis

### No shared feature across the high-pull set

The nine high-pull maps span the corpus's full landscape range. K-35-067-2 and
K-35-067-3 are heavily forested mountainous sheets; K-35-054-2 and K-35-055-1
are open agricultural plains; K-35-051-3, K-35-042-3, and K-35-066-3 are mixed
forest-agricultural mosaics; K-35-076-3 is a contour-dense mountain-valley
network; K-35-056-3 is a coastal sheet with sea covering roughly half the area.
Settlement density ranges from sparse (K-35-067-2, K-35-067-3, K-35-056-3) to
dense (K-35-054-2, K-35-055-1). Forest cover ranges from sparse (K-35-054-2,
K-35-055-1, K-35-077-4) through moderate (most maps) to heavy (K-35-067-2,
K-35-067-3, K-35-074-3). No single visible feature axis separates the high-pull
maps from the controls.

### A control is visually indistinguishable from the high-pull leader

K-35-074-3 — a control map with 0 % shell rate in all four runs — is visually
indistinguishable from K-35-067-2 (the multi-run high-pull leader, top-3 in
T=0.3, T=0.7, and text-MIN with rates of 42.86 %, 75.00 %, and 50.00 %
respectively) and from K-35-067-3 (top-3 in text-MIN at 28.57 %). All three
sheets show the same heavily forested mountainous terrain, dense contours,
sparse settlement, similar river-network topology, and the same Soviet 1981
edition appearance. If a cartographic-feature signal explained the high-pull
behaviour, K-35-074-3 should also be high-pull. It is not. This single
counter-example is sufficient to reject the strong form of the hypothesis.

### Image-track and text-track tails do not overlap meaningfully

Of the nine high-pull maps, only K-35-051-3 appears in both a text-track top-3
(T=0.3, T=0.7) and the image-track top-3. K-35-067-2 is the multi-run text-track
leader but ranks at 31.58 % on the image run (well below the image top-3
threshold of 40 %). The image top-3 (K-35-056-3, K-35-066-3, K-35-076-3)
otherwise appears nowhere in the text-track top-3s. This near-disjoint structure
is consistent with two qualitatively different mechanisms by track (per Obs 301:
image-track is uniformly distributed across all maps; text-track is bimodal
with a sparse high-pull tail), rather than with a single shared cartographic
mechanism.

### FP categorical distributions are similar between high-pull and control groups

The Obs 302 FP-classification audit shows that across both groups, contour-ring
is the dominant FP category (high-pull: present in 8 of 9 maps; controls: 3 of 3).
Absolute FP counts are similar: high-pull maps span 4–20 total FPs across the
four runs (median 12); controls span 8–19 (median 14). The control K-35-077-4
has 19 FPs — among the highest counts in the entire 12-map sample — yet a 0 %
shell rate. The category distribution does not separate the groups; what
separates them is whether the FPs happen to fall in the (50, 75] m annulus around
a reference point, which is a function of reference-point density, FP spatial
distribution, and the number of detections (denominator), not of a special
distractor feature on the high-pull maps.

### Small-denominator arithmetic accounts for the most extreme rates

Several of the highest per-map rates resolve to a 1–3 detection count when the
numerator and denominator are inspected. K-35-067-2 at T=0.7 = 3 of 4 (75 %);
K-35-056-3 at image = 3 of 6 (50 %); K-35-067-2 at text-MIN = 3 of 6 (50 %);
K-35-042-3 at T=0.3 = 1 of 3 (33 %); K-35-051-3 at T=0.7 = 1 of 3 (33 %).
Removing or adding a single detection in these cells flips the per-map rate by
20–25 percentage points. This is consistent with Obs 301's caveat that thin-sample
maps drive the SD and tail-max values; the right-skew shape is real but the
identification of specific maps as "high-pull" is unstable when n_detections
is small.

## Paper implications

The paper Discussion should treat the per-map right-skew as a distributional
finding without attributing it to identifiable cartographic features. Suggested
phrasing:

> Per-map (50, 75] m shell rates are heavily right-skewed on the text track
> (median 0 %; long tail to 33–75 %), indicating that the corpus-level rate of
> 3–4 % is driven by 2–3 maps rather than uniform across the corpus. Qualitative
> inspection of the high-pull tail and matched low-pull controls did not
> identify a shared cartographic feature (label density, vegetation hatching,
> terrain type, edition variant) explaining the elevated rates. Control maps
> with visually indistinguishable cartographic character to the most
> high-pull text-track map (K-35-067-2) record 0 % shell rates, and FP category
> distributions across the high-pull and control sets are similar. The
> right-skew is most parsimoniously attributed to small-denominator variance
> on text-track sheets (where n_detections is typically 4–20 per map) compounded
> by per-map heterogeneity in reference-point density. We therefore report the
> per-map distribution shape (median + IQR or boxplot) alongside the corpus
> rate but do not claim a cartographic-feature mechanism for the tail.

For the image track, the per-map distribution is broadly centred (Obs 301:
median 15.4 %); the image top-3 still differ from the text top-3, but
characterising the image-track FP-anchoring mechanism is a separate question
already partly addressed by Obs 296 / Obs 300 / Obs 302.

## Caveats and limitations

1. **Sample size.** Twelve maps inspected (9 + 3) is a small sample. Stronger
   counter-examples (a feature shared by 8 of 9 high-pull maps and absent in all
   3 controls) would have been detectable; a feature shared by, e.g., 5 of 9
   may not have been. The single counter-example (K-35-074-3) suffices to
   reject the strong form of the hypothesis but does not exclude weaker
   feature-correlation hypotheses.
2. **Qualitative judgement.** The "sparse / moderate / dense" labels are
   subjective and were applied by visual inspection at 2,048 px. A trained
   cartographer's reading at full resolution may disagree at the margins. The
   broad strokes (no terrain type appears uniquely on the high-pull set) are
   robust to the labelling choice.
3. **Resolution constraint.** At 2,048 px wide, fine-grained features
   (specific contour values, small symbol-set differences, edition number or
   date stamps in the margin) are not legible. A feature operating only at fine
   resolution (e.g., a specific contour-line label numeric pattern) cannot be
   ruled out by this inspection. The Obs 302 VLM-based FP classification, which
   operates on 150 m crops (much higher effective resolution per FP), provides
   the categorical complement to this coarse-feature pass and converges on the
   same conclusion: contour-rings dominate FPs across both groups.
4. **Single inspection per map.** No FP-cluster region inspection at higher
   zoom was performed. The Obs 302 per-FP categorical audit substitutes for
   this on the question of "what kind of feature is being mistaken for a
   mound", and shows the same dominant category (contour-ring) on both the
   high-pull and control groups.
5. **Reference-point density not measured here.** A more rigorous follow-up
   would correlate per-map shell rate with per-map reference-point density (or
   reference-point spatial clustering); under the small-denominator-arithmetic
   hypothesis, maps with high reference-point density should produce higher
   shell rates given the same FP rate. This is out of scope for this
   characterisation document but flagged for any future quantitative follow-up.

## Provenance

- Source data: `results/55maps-per-map-shell-variance/per_map_shell_rates.json`
- FP categorical audit: `results/55maps-fp-classification/fp_classifications.json`
- Rasters: `inputs/rasters/Russian1981_32635/K-35-*.tif`
- Previews generated: `gdal_translate -outsize 2048 0 -of PNG -scale`
- Cross-references: Obs 301, Obs 302, Obs 300, Obs 296
