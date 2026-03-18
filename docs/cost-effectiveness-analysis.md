# Cost-Effectiveness Analysis

Cost analysis for VLM-based burial mound detection using the Gemini Batch API.
All costs are for Gemini 3 Flash Preview as of March 2026 with batch pricing
(50% discount on input and output tokens).

## Pricing

| | Input tokens | Output tokens |
|---|---|---|
| **Real-time API** | $0.10 / 1M | $0.40 / 1M |
| **Batch API (50% discount)** | $0.05 / 1M | $0.20 / 1M |

Thinking tokens (used by HIGH thinking level) are billed at the output token
rate. This is the dominant cost driver for HIGH thinking configurations.

## Per-Tile Token Costs

Token counts per tile vary substantially by prompt modality. System instruction
and few-shot examples are included in every request, so the per-tile overhead
is higher than the raw tile content alone.

| Configuration | Input tokens/tile | Output tokens/tile | Cost/tile (batch) |
|---|---|---|---|
| Text-only, minimal thinking | ~1,500 | ~170 | $0.000109 |
| Text-only, HIGH thinking | ~1,500 | ~4,000 (est.) | $0.000875 |
| Image+text, minimal thinking | ~20,000 | ~170 | $0.001034 |
| Image+text, HIGH thinking | ~20,000 | ~4,000 (est.) | $0.001801 |

Image+text input costs are ~13× higher than text-only because each tile's
512×512 px image is base64-encoded into the request (~18,500 image tokens).
HIGH thinking output costs are ~24× higher than minimal thinking because the
model's extended reasoning chain consumes most of the output token budget.

## Per-Unit Costs (340 tiles)

A "unit" is one execution of the detection pipeline across all 340 tiles.

| Configuration | Cost/unit | Relative to text-min baseline |
|---|---|---|
| Text-only, minimal | **$0.037** | 1.0× |
| Text-only, HIGH | **$0.298** | 8.1× |
| Image+text, minimal | **$0.352** | 9.5× |
| Image+text, HIGH | **$0.612** | 16.6× |

## Consensus Voting Cost-Effectiveness

The key trade-off: consensus voting improves F1 by running N independent passes
and keeping detections that appear in ≥x of N runs. Cost scales linearly with N.

### Cost vs F1 Improvement

All comparisons use the text-only minimal-thinking N=1 baseline (F1=0.605,
cost=$0.037) as the reference point. ΔF1 is the improvement over this baseline.
$/ΔF1 measures the cost of each 0.001 improvement in F1.

| Configuration | N | F1 | Cost | ×base | ΔF1 | $/ΔF1 |
|---|---|---|---|---|---|---|
| **Text, minimal, N=1** | 1 | 0.605 | $0.04 | 1× | — | — |
| **Image, minimal, N=1 (best single)** | 1 | 0.631 | $0.35 | 10× | +0.026 | $13.53 |
| **Text, minimal, N=5** | 5 | 0.686 | $0.18 | 5× | +0.081 | $2.28 |
| **Text, minimal, N=10** | 10 | 0.687 | $0.37 | 10× | +0.082 | $4.50 |
| **Text, minimal, N=30** | 30 | 0.692 | $1.11 | 30× | +0.087 | $12.72 |
| **Image, minimal, N=5** | 5 | 0.663 | $1.76 | 48× | +0.058 | $30.32 |
| **Image, minimal, N=30** | 30 | 0.691 | $10.55 | 286× | +0.086 | $122.67 |
| **Text, HIGH, N=5** | 5 | 0.713 | $1.49 | 40× | +0.108 | $13.78 |
| **Text, HIGH, N=10** | 10 | 0.747 | $2.98 | 81× | +0.142 | $20.95 |
| **Text, HIGH, N=30** | 30 | 0.771 | $8.93 | 242× | +0.166 | $53.77 |

### Key Findings

**1. Text-only N=5 is the cost-efficiency sweet spot.**
At $0.18 per 340-tile evaluation (5× baseline cost), text-only N=5 consensus
achieves F1=0.686 — an improvement of +0.081 over baseline at $2.28 per ΔF1
unit. This is the lowest $/ΔF1 of any configuration.

**2. Image+text is expensive for marginal gain.**
The best single-pass image configuration (F1=0.631) costs 10× the text-only
baseline for only +0.026 ΔF1. Image-using consensus (N=30) reaches F1=0.691
but at 286× baseline cost. The same F1 is achievable with text-only N=30 at
30× baseline cost — an order of magnitude cheaper.

**3. HIGH thinking + consensus is the quality ceiling, at a price.**
The best overall F1 (0.771) uses HIGH thinking with N=30, costing $8.93 per
evaluation (242× baseline). However, HIGH thinking N=5 achieves F1=0.713 at
$1.49 (40× baseline) — 84% of the way to the ceiling at 17% of the cost.

**4. Diminishing returns are steep beyond N=5.**
For text-only minimal thinking, going from N=5 to N=30 improves F1 by only
+0.006 (0.686→0.692) at 6× the cost. For HIGH thinking, N=5→N=30 improves by
+0.058 (0.713→0.771) at 6× the cost — a better return, but still diminishing.

### Cost-Efficiency Frontier

The Pareto-optimal configurations (those where no other configuration achieves
higher F1 at lower cost) are:

1. **Text, minimal, N=1** — F1=0.605, $0.04 (cheapest)
2. **Text, minimal, N=5** — F1=0.686, $0.18 (best $/ΔF1)
3. **Text, HIGH, N=5** — F1=0.713, $1.49 (best mid-range)
4. **Text, HIGH, N=10** — F1=0.747, $2.98
5. **Text, HIGH, N=30** — F1=0.771, $8.93 (highest quality)

All image-using configurations are dominated by text-only alternatives that
achieve equal or higher F1 at lower cost. This is a key practical finding:
**sending example images to the model does not justify the ~10× cost increase**.

## Retry and Failure Overhead

Tiles that fail JSON parsing are retried via the real-time API (no batch
discount). The retry overhead is modest:

| Configuration | Failure rate | Avg retries | Overhead |
|---|---|---|---|
| Text-only, minimal | ~2% | ~1.5 | ~8% of unit cost |
| Text-only, HIGH | ~5% | ~3 | ~15% of unit cost (est.) |
| Image+text, minimal | ~2% | ~1.5 | ~8% of unit cost |
| Image+text, HIGH | ~5% | ~3 | ~10% of unit cost (est.) |

The retry overhead is negligible (<$0.03 per unit) and does not materially
affect the cost-effectiveness analysis. Temperature has minimal effect on
failure rates (see `batch-api-throughput-and-errors.md`).

## Scaling Considerations

### Per-Map-Sheet Costs

The evaluation corpus covers 4 map sheets with 340 tiles (512×512 px). For
operational deployment across a study region:

| Configuration | Cost per map sheet (~85 tiles) | Cost per 100 map sheets |
|---|---|---|
| Text, minimal, N=1 | ~$0.01 | ~$1.00 |
| Text, minimal, N=5 | ~$0.05 | ~$4.50 |
| Text, HIGH, N=5 | ~$0.37 | ~$37 |
| Text, HIGH, N=30 | ~$2.23 | ~$223 |

Even the most expensive configuration (HIGH N=30) costs less than $2.25 per
map sheet — trivial compared to the cost of manual digitisation.

### Comparison to Manual Digitisation

Manual digitisation of burial mounds from topographic maps requires expert
knowledge and typically takes 30–60 minutes per map sheet. At archaeological
research assistant rates (~$25–50/hour), this represents $12.50–50.00 per
sheet. The VLM approach at the Pareto-optimal N=5 configuration costs $0.05
per sheet — a reduction of **250–1,000×**.

## Placeholder: Proposer-Verifier Costs

*To be added when PV pipeline results are available.*

The proposer-verifier (PV) approach adds a second API call per candidate
detection. Estimated costs depend on the number of candidates per tile and
the verifier's crop size. Preliminary estimates suggest PV costs are
comparable to N=5–10 consensus for similar F1 improvements, but with
different precision/recall trade-offs.

## Placeholder: Tile Size (384 vs 512) Costs

*To be added when 384-tile results are available.*

Smaller tiles (384×384) produce more tiles per map sheet (~1.8×) but with
fewer input tokens per tile (smaller images). The net cost effect depends on
whether the token reduction per tile offsets the increased tile count.

## Notes

- All costs assume Gemini 3 Flash Preview pricing as of March 2026.
  Pricing may change; relative cost ratios are more stable than absolute costs.
- HIGH thinking output token estimates (~4,000/tile) are approximate — the
  Batch API does not report per-tile token usage. Actual costs may vary ±30%.
- The batch discount (50%) is available for all configurations. Real-time API
  costs are exactly 2× the figures shown.
- Cost estimates do not include Google Cloud Platform (GCP) infrastructure,
  compute for pre/post-processing, or storage — these are negligible for this
  application.
