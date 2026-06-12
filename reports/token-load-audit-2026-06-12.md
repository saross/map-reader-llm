# Token-load audit — 55-map deployment cost manifests (2026-06-12)

> **Last revised**: 2026-06-12 (original publication). See
> [§ Changelog](#changelog) for revision history.

Audit of the four 55-map deployment `cost_manifest.json` files, recomputation
of the project cost model from original per-pass metadata, and the resulting
revision of the Pareto v2 artefacts (`results/verifier-robustness/pareto/`)
and findings document (§ 15, § 16(c)). Conducted autonomously by Claude
(Fable 5) at Shawn's direction; every number below carries its source path.

## 1. Verdict summary

| Run | Manifest vs clean | Live metas vs clean | Trustworthy source |
|---|---|---|---|
| `55maps-text-min-generalisation` | **2.0× inflated** | clean (1.0×) | live `*.meta.json` |
| `55maps-text-high-generalisation` | **2.0× inflated** | **2.0× inflated** | `per_item_metadata` |
| `55maps-text-high-t0.3-generalisation` | clean (1.0×) | clean (1.0×) | either |
| `55maps-image-generalisation` | **3.0× inflated** | **2.0× inflated** | `per_item_metadata` |

In addition, **all four manifests price at standard rates ($0.50/$3.00 per
1M) although every run executed at `--service-tier flex`** (half price), and
**all four omit thinking tokens from `cost_usd`** although Gemini bills
thinking at the output rate. The three errors compound differently per run,
so manifest totals are wrong in both directions (§ 6).

## 2. Method

1. **Pricing verified at source** (<https://ai.google.dev/gemini-api/docs/pricing>,
   retrieved 2026-06-12): Gemini 3 Flash Preview — flex and batch tiers both
   $0.25 / 1M input (text/image/video) and $1.50 / 1M output, **output price
   includes thinking tokens**; standard tier exactly 2× ($0.50 / $3.00).
   Context caching $0.05 / 1M (text/image/video) at all tiers, plus
   $1.00 / 1M tokens / hour storage.
2. **Clean per-pass loads** reconstructed by summing the `per_item_metadata`
   token records (one record per unique tile, final attempt) in each pass's
   `*.meta.json`, ignoring the merged `usage_stats` and the manifests.
   Each pass's `execution_stats.completed_items` was checked for exactly
   8,541 unique tiles (55-map corpus) or 487 (GS corpus).
3. **Double-count factors** computed as reported `usage_stats` totals divided
   by the per-item sums, per token axis (input / output / thinking).
4. Service tier confirmed from `run.log` command lines and
   `launch_manifest.json` (`"service_tier": "flex"`) in all four run
   directories.

## 3. Per-run findings (55-map corpus, 8,541 tiles/pass)

### 3.1 text-min (5 passes; minimal thinking, T = 0.7)

- Source: `outputs/55maps-text-min-generalisation/proposer/detect_brief-text/run_{1..5}/detections-detect_brief-text-3-flash-2026-04-18.meta.json`
- Live metas **clean**: factor 1.000 on all axes; `items_processed` = 8,541.
- Per pass: input 12,828,582 (exactly 1,502/tile — uniform 384 px tile +
  brief text prompt); output mean 976,791 (range 972,669–980,412);
  thinking 0.
- **Clean flex cost: $4.67/pass** (mean $4.6723).
- The manifest (`cost_manifest.json`, generated 2026-05-03T02:01:50Z) is
  nevertheless **2.0× inflated**: per-pass input 25,657,164 = exactly
  2 × 12,828,582; `tiles_processed` 17,082 = 2 × 8,541. Its
  `_metadata.cleanup_recovery_metas_merged` lists five
  `*.meta.json.pre-recovery-20260503T014926.backup` proposer files that no
  longer exist on disk — the manifest generator summed live metas with the
  backups. The suspected "~3,000 input tokens per tile" is this 2× artefact
  (25,657,164 / 8,541 = 3,004), not a real load.

### 3.2 text-high (5 passes; HIGH thinking, T = 0.7)

- Source: `outputs/55maps-text-high-generalisation/proposer/detect_brief-text/run_{1..5}/detections-detect_brief-text-3-flash-2026-04-18.meta.json`
- Live metas **2.0× inflated** (factors 2.003–2.016 across axes): the
  2026-05-02 recovery merge summed the original-run usage into the
  post-recovery cumulative usage. Diagnostics: `items_processed`
  17,040–17,057 vs 8,541 unique `completed_items`; run_1 reported input
  25,694,714 = 2 × 12,828,582 + 25 recovered tiles × 1,502;
  `recovery_history[0].recovery_cost_usd` $11.46 for 25 tiles ≈ half the
  pass cost.
- Clean per pass (per-item sums): input 12,828,582; output mean 1,647,744;
  **thinking mean 23,005,025** (2,693/tile).
- **Clean flex cost: $40.19/pass** (range $39.92–$40.45), of which thinking
  is ~$34.51 — the manifest's $22.88/pass at standard rates billed the 2×
  input and 2× output but **zero** of the 46.1M (2× inflated; true 23.0M)
  thinking tokens.

### 3.3 text-high-t0.3 (5 passes; HIGH thinking, T = 0.3)

- Source: `outputs/55maps-text-high-t0.3-generalisation/proposer/detect_brief-text/run_{1..5}/detections-detect_brief-text-3-flash-2026-04-26.meta.json`
- **Clean** as suspected (factors 1.0001–1.0012; no recovery merge;
  manifest generated 2026-04-27, `_metadata` null).
- Per pass: input 12,828,582; output mean 1,461,601; **thinking mean
  30,283,306** (3,546/tile — T0.3 thinks ~32% more than T0.7).
- **Clean flex cost: $50.82/pass** (range $49.94–$51.64). The manifest's
  $10.79/pass priced input + output at standard and omitted thinking.

### 3.4 image (library_plus-hp; 5 passes; HIGH thinking, T = 0.7)

- Source: `outputs/55maps-image-generalisation/proposer/library_plus-hp/run_{1..5}/detections-library_plus-hp-3-flash-2026-04-18.meta.json`
- Live metas **2.0× inflated** (same recovery-merge mechanism;
  `items_processed` 17,084–17,090). The manifest is **3.0× inflated**
  (per-pass `tiles_processed` 25,625–25,631 ≈ 17,090 + 8,541): the manifest
  generator added the pre-recovery backups on top of the already-doubled
  live metas.
- Clean per pass: input 133,743,514, of which **cached 124,211,741**
  (explicit context cache, 14,549 tokens — the PV library — created per
  pass with TTL = 1 h; `run.log` lines 15, 4327); non-cached input
  9,531,773; output mean 1,283,956; thinking mean 19,033,673 (2,228/tile).
- **Clean flex cost: $39.07/pass** (range $38.78–$39.27), priced as
  non-cached input × $0.25/M ($2.38) + cached × $0.05/M ($6.21) +
  (output + thinking) × $1.50/M ($30.48). Cache **storage excluded**: at
  $1.00/M/h a 14,549-token cache costs ~$0.015/h, < $0.15 across the whole
  run — negligible. The manifest's $212/pass billed 3× input (cached
  included **at the full input rate**) at standard and omitted thinking.

### 3.5 Uplift run (runs 6–10; minimal thinking, T = 0.7)

- Source: `outputs/55maps-text-min-n10-uplift/proposer/run_{6..10}/detections-detect_brief-text-3-flash-2026-06-11.meta.json`
- Clean (factors ≤ 1.0001). Per pass: input 12,828,582 (1,502/tile —
  identical to the TM run); output mean 963,967; thinking 0.
- **Clean flex cost: $4.65/pass** (mean $4.6531) — corroborates § 3.1.
- Verifier (`verified-3of10/run.meta.json`): 16,482 calls, input 29,535,744
  (exactly 1,792/call), output 2,588,179; **flex $11.27** ($0.000684/call).

## 4. GS-scale loads (487-tile corpus)

- **HIGH text, measured** (per-item sums,
  `outputs/h11/pv-diag-384/flash-high-text-n5/text-t{0.0,0.3,1.0}/run_*/`):
  T0.0 $3.22/pass (3 passes; think/tile 3,993); T0.3 $2.64/pass (10 passes;
  think/tile 3,188); T1.0 $2.15/pass (10 passes; think/tile 2,487). Input is
  uniformly 1,502/tile (731,474/pass; 726,968–729,972 at T0.0 where 1–2
  tiles differ).
- **HIGH text T0.7 — the temperature the Pareto rungs use — could NOT be
  measured at GS**: the 30 metas in `.../text-t0.7/run_*/` are batch-API
  records with zero usage (`usage_stats` all 0, `batch_api.execution_mode:
  "batch"`). Scaling the five measured 55-map T0.7 passes (§ 3.2) to 487
  tiles gives **$2.29/pass** (input 731,474; output 93,952; thinking
  1,311,725), which sits inside the measured GS bracket [T1.0 $2.15,
  T0.3 $2.64]. Adopted with that bracket as the uncertainty.
- **Minimal text**: T1.0 measured at GS
  (`outputs/h11/pv-diag-384/flash-minimal-text-n30-t07/text-t1.0/run_*/`,
  10 passes): $0.289/pass. T0.7 (rung temperature) scaled from the ten
  measured 55-map minimal passes: **$0.266/pass** (input 731,474; output
  55,328). The GS T0.7 minimal metas are likewise empty batch records.
- **Verifier, measured** (minimal thinking, so no thinking-token issue):
  - opmax run (`outputs/verifier-robustness/384-flash-high-text-16of30/T0.3/verified/run.meta.json`):
    3,645 calls, input 6,531,840 (uniform 1,792/call), output 595,165 →
    flex $2.5257 = **$0.000693/call** (published $0.000697 ≈ same run,
    coarser rounding).
  - 55-map text-high verifier: 9,205 calls (74 live + 9,131 backup — the
    verifier merge was additive over disjoint call sets, NOT
    double-counted), flex $6.42 = $0.000697/call
    (`outputs/55maps-text-high-generalisation/verified/run.meta.json{,.pre-recovery-20260502T235106.backup}`).
  - 55-map t0.3 verifier: 9,910 calls, flex $6.90 = $0.000696/call.
  - Uplift verifier: 16,482 calls, flex $11.27 = $0.000684/call.

## 5. Corrected cost model

Adopted in `scripts/build_pareto_v2.py` (was → now):

| Constant | Old | New | Basis |
|---|---:|---:|---|
| `MIN_PASS_USD` (GS 487) | 0.54 | **0.266** | ten measured 55-map minimal passes scaled by 487/8,541 (§ 3.1, § 3.5) |
| `HIGH_PASS_USD` (GS 487) | 1.61 | **2.29** | five measured 55-map T0.7 HIGH passes scaled; bracket [2.15, 2.64] measured at GS (§ 4) |
| `VF_CALL_USD` | 0.000697 | **0.000693** | opmax meta recompute; deployment runs measured 0.000684–0.000698 |

Deployment-scale (8,541 tiles) per-pass flex costs, **measured**:

| Pass type | $/pass | n passes | Source |
|---|---:|---:|---|
| Minimal text (T0.7) | **$4.66** | 10 | § 3.1 + § 3.5 |
| HIGH text (T0.7) | **$40.19** | 5 | § 3.2 |
| HIGH text (T0.3) | **$50.82** | 5 | § 3.3 |
| HIGH image (cached) | **$39.07** | 5 | § 3.4 |

The old model's two errors partially offset: `MIN_PASS_USD` was 2.0× too
high (built on the double-counted TM manifest), while `HIGH_PASS_USD`
("3× minimal", extrapolated from verifier-side high-vs-min calls) was 1.4×
too LOW because proposer-side HIGH thinking (2,693 tokens/tile at T0.7)
dominates the pass cost. The true min : HIGH ratio per pass is **8.6×**,
not 3×. Notably, explicit caching makes the image HIGH pass ($39.07)
slightly CHEAPER than the text HIGH pass ($40.19) despite a 10× larger
prompt.

## 6. Corrected whole-run spend (proposer + verifier, flex)

For Shawn's cross-check against the Google billing console (ground truth):

| Run | Manifest `cost_usd` | Corrected flex spend | Manifest error |
|---|---:|---:|---|
| text-min | $93.50 | **~$23.4** (5 × $4.67 + $0.03 verifier) | 4.0× over (2× count, 2× rates) |
| text-high | $126.81 | **~$207.4** (5 × $40.19 + $6.42) | 0.61× under (thinking omitted) |
| text-high-t0.3 | $67.82 | **~$261.0** (5 × $50.82 + $6.90) | 0.26× under (thinking omitted) |
| image | $1,061.08 | **~$195.4** (5 × $39.07 + $0.001) | 5.4× over (3× count, 2× rates, cache rate) |
| uplift (no manifest) | — | **~$34.5** (5 × $4.65 + $11.27) | — |

Total corrected proposer + verifier spend across these five campaigns:
**~$722 flex**. Caveat: these are **lower bounds** — see § 8.

## 7. Published figures changed (before → after)

Pareto v2 (`results/verifier-robustness/pareto/pareto_v2.json`, findings
§ 15 table; GS run cost / 55-map production cost):

| Rung | F1@20m | Old GS | New GS | Old production | New production |
|---|---:|---:|---:|---:|---:|
| min6 | 0.8784 | $3.81 | **$2.43** | ~$67 | **~$43** |
| min11 | 0.8835 | $6.75 | **$4.00** | ~$118 | **~$70** |
| high6 | 0.8641 | $10.65 | **$14.04** | ~$187 | **~$246** |
| high5+5vf | 0.8739 | $11.03 | **$14.41** | ~$193 | **~$253** |
| high11 | 0.8769 | $20.19 | **$26.97** | ~$354 | **~$473** |
| high31 | 0.8902 | $48.81 | **$69.21** | ~$856 | **~$1,214** |
| high35 | 0.8951 | $50.84 | **$71.23** | ~$892 | **~$1,249** |

Findings § 16(c) production trade: "~$105 for 0.829 vs ~$150 for 0.843"
→ **"~$58 for 0.829 vs ~$207 for 0.843"** (min11-uplift as-run:
10 × $4.66 + $11.27 verifier; TH7-k3 as-run: 5 × $40.19 + $6.42 verifier).
The trade widens from ~1.4× to ~3.6×.

## 8. What did NOT change, and residual caveats

- **F1 values, permutation results, tiers**: untouched — only the dollar
  axis moved. The re-run reproduced 0/21 significant pairs, one tier.
- **Pareto-efficient set**: **unchanged** — {min6, min11, high31, high35}.
  The frontier shape survives because min got cheaper and HIGH dearer
  monotonically; no dominance relation flipped.
- **Verifier rate**: confirmed within 1% of the published value; verifier
  legs of all published costings were essentially correct.
- **Historical actual-spend figures** in findings §§ 1–14 (e.g. $21.93,
  $2.54, $20.86 flex): minimal-thinking verifier runs with correct flex
  pricing — not revised (the $2.54 recomputes to $2.5257; rounding only).
- **Retry spend is unmeasured** (lower-bound caveat): `per_item_metadata`
  records only the final attempt, and `usage_stats` match the per-item sums
  even in clean runs, so no on-disk record captures tokens consumed by
  retried attempts. Retry counts (live metas; text-high/image counts
  halved for merge inflation, marked inferred): text-min 61; text-high
  ~3,130 (inferred); t0.3 12,322; image ~2,190 (inferred). Worst case if
  every retry billed a full request: t0.3 up to ~29% higher. The billing
  console is the only ground truth here.
- **GS T0.7 HIGH and GS T0.7 minimal rates are scaled, not measured**
  (empty batch metas, § 4); marked with measured brackets.
- **Image cache split**: clean and exact per item (cached_input_tokens is a
  subset of input_tokens; modality breakdowns confirm). Storage cost
  excluded (< $0.15 per campaign, § 3.4).

## 9. Recommendation on the manifests

**Regenerate the three affected `cost_manifest.json` files** (text-min,
text-high, image) from per-item metadata at flex rates with thinking
billed, and **re-price the t0.3 manifest** (counts clean; rates and
thinking omission still wrong) — but do so as a deliberate, separate pass
with the archive-never-delete convention (move current manifests to
`archive/`), since downstream documents cite them. Not done in this audit
(out of scope by instruction). The manifest generator needs three fixes
before any regeneration: (1) sum from `per_item_metadata`, never merge
pre-recovery backups additively; (2) price at the run's recorded
`service_tier`; (3) bill thinking tokens at the output rate.

## Changelog

### 2026-06-12 — Original publication

Token-load audit conducted against the four 55-map cost manifests, the
uplift run, the GS HIGH/minimal pools, and the verifier metas. Cost model
in `scripts/build_pareto_v2.py` corrected (MIN 0.54 → 0.266, HIGH 1.61 →
2.29, VF 0.000697 → 0.000693); Pareto v2 artefacts regenerated on zbook;
findings § 15/§ 16(c) and the S113 sign-off package revised in the same
commit series.
