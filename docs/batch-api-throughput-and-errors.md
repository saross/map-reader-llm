# Batch API Throughput and Error Characterisation

Performance characteristics of the Gemini Batch API for VLM-based map symbol
detection. All measurements from the 340-tile (512×512 px) full-corpus
evaluation using Gemini 3 Flash Preview.

## Throughput

### Per-Unit Processing Time

Each "unit" is one execution of the detection pipeline across all 340 tiles,
submitted as a single Batch API job.

| Configuration | Input tokens/tile | Tokens/unit | Time per unit | Max concurrent |
|---|---|---|---|---|
| Text-only, minimal thinking | ~700 | ~237K | **2–3 min** | ~11 |
| Text-only, HIGH thinking | ~700 (input) | ~237K (input) | **20–30 min** | ~11 |
| Image+text, minimal thinking | ~4,000 | ~1.37M | **~30 min** | ~2 |
| Image+text, HIGH thinking | ~4,000 (input) | ~1.37M (input) | **45–60 min** (est.) | ~2 |

### Throughput Bottlenecks

**1. Google Batch API turnaround time.** Each batch job takes 20–30 minutes to
process on Google's servers, regardless of input size. This is the dominant
bottleneck — even text-only jobs with modest token counts take ~20 minutes when
HIGH thinking is enabled, because the model generates substantially more output
tokens (thinking + detection JSON).

**2. Enqueued token quota.** The Batch API enforces a 3 million token limit on
total input tokens across all active (PENDING + RUNNING) jobs. Text-only jobs
(~237K tokens each) allow ~11 concurrent jobs; image-using jobs (~1.37M tokens
each) allow only ~2. This is the binding constraint for image-track experiments.

**3. Quota contention across studies.** When multiple studies run simultaneously,
each process maintains its own token ledger but they share the same API quota.
This adds ~50% to per-unit times as processes back off on 429 (RESOURCE_EXHAUSTED)
errors and wait for quota to free up.

**4. Disk space for image-using JSONL files.** The Batch API requires input as
JSONL files uploaded via the Files API. Image-using JSONL files are ~400 MB each
(base64-encoded tile images). The pipeline prepares all JSONL files before
submitting, so an image-track study with 90 units requires ~36 GB of temporary
storage. This limits image-track studies to sequential execution.

### Aggregate Timing

For the full experimental design (Phases 2a–3c, 340 tiles, both tracks):

| Phase | Units | Modality | Thinking | Approx. wall time |
|---|---|---|---|---|
| Phase 2a–2e OFAT (all tracks) | 71 | Mixed | Minimal | ~4 hours |
| Phase 3a voting, minimal (both tracks) | 180 | Both | Minimal | ~12 hours |
| Phase 3a voting, HIGH (both tracks) | 180 | Both | HIGH | ~48 hours (est.) |
| Phase 3a replication | 60 | Text | Both | ~12 hours |
| Phase 3c diversity (both tracks) | 225 | Both | HIGH | ~48 hours (est.) |

Total estimated wall time: ~5 days of continuous processing. Actual elapsed time
is longer due to quota resets (daily token limits reset at midnight US Pacific),
sequential scheduling of image-track studies, and investigation/debugging time.

All runs used the 50% cost-reduced Batch API rather than the real-time API.
Real-time processing would be faster but at double the per-token cost.

## Error Characterisation

### Failure Mode

The sole failure mode observed is **JSON parse failure**: the model produces
detection output wrapped in malformed JSON that cannot be parsed. Typical error
signatures include:

- `Expecting ',' delimiter` (most common — ~40% of parse errors)
- `Expecting value` (~25%)
- `Unterminated string starting at` (~20%)
- `Expecting property name enclosed in double quotes` (~15%)

These errors consistently occur at similar character offsets (~line 52, char
~750 for HIGH thinking text-only runs), suggesting output truncation as the
primary cause: the model's thinking tokens consume most of the `max_output_tokens`
budget (8192), leaving insufficient room for the detection JSON.

### Failure Rates by Condition

Failure rates are reported as the percentage of units (340-tile batch jobs) that
contain at least one tile-level parse failure, measured after the pipeline's
built-in synchronous retry loop (up to 10 attempts per failed tile).

**By modality** (strongest effect):

| Modality | Units | Units with failures | Failure rate |
|---|---|---|---|
| Image+text | 115 | 60 | 52% |
| Text-only | 189 | 15 | 8% |

Image-using prompts are ~6× more failure-prone, likely because the larger prompt
(base64 images + text) leaves less output budget for the model's response.

**By thinking level:**

Thinking level has a complex interaction with failure rates. At the individual
tile level, HIGH thinking produces more initial parse failures per batch job
(typically 5–8 tiles out of 340, vs 0–2 for minimal). However, HIGH thinking
failures are more responsive to retry — most resolve within the 10-attempt retry
loop because the failure is stochastic (thinking length varies per attempt).

Before retry, HIGH thinking units show ~2% tile-level failure rate; after 10
retries, this drops to near zero. The remaining failures can be recovered via
the `--patch-tiles` post-hoc cleanup mode, which retries with reduced
`max_output_tokens` to constrain the thinking budget.

**By temperature:**

| Temperature | Tile-level failure rate (image track, minimal thinking) |
|---|---|
| T0.0 | ~1% (near-deterministic output) |
| T0.3 | ~2% (low variance) |
| T0.7 | ~1.5% |
| T1.0 | ~1.5% |

Temperature has minimal effect on failure rates when thinking level is held
constant. The dominant factors are modality (image vs text) and thinking level.

### Tile-Level Failure Concentration

Failures are highly concentrated in a small number of tiles. Out of 340 tiles
in the evaluation corpus, 46 unique tiles experienced at least one parse failure
across all conditions. One tile (`K-35-053-3_Elenovo_x1344_y896.png`) accounts
for ~31% of all failures, suggesting specific image content characteristics
trigger malformed model output.

The per-tile failure rate (probability of failure on any single attempt) ranges
from ~3% (occasional failures) to ~60% (the most failure-prone tile at T0.3
with image+text input). With the 10-attempt retry loop, even a 60% per-attempt
failure rate resolves with probability 99.4%.

### Recovery Mechanisms

The pipeline implements three tiers of failure recovery:

1. **Inline retry loop** (automatic): Up to 10 synchronous retries per failed
   tile immediately after batch completion. Resolves ~99% of failures. Cost is
   negligible (~$0.0005 per retry).

2. **`--patch-tiles` mode** (manual): Post-hoc cleanup that retries failed tiles
   with the original parameters (tier 1), then falls back to reduced
   `max_output_tokens` (2048 tokens, tier 2) to prevent output truncation.
   Recovers tiles that exhausted the inline retry budget.

3. **Acceptance threshold**: Units with ≤10 tile failures (out of 340, ~3%) are
   accepted as complete. For consensus voting studies (K=30 runs), individual
   tile gaps are tolerable — each tile gets data from multiple independent runs.

### Impact on Results

At the acceptance threshold of ≤10 tile failures per unit (~3%), the maximum
data loss is 10 tiles × 1 run out of 340 tiles × 30 runs = 0.1% of
tile-run combinations. In practice, tile failures are largely non-overlapping
across runs (stochastic), so the effective data loss is substantially lower.
No tile is systematically missing from all 30 runs of any condition.
