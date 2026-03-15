# Flash-Lite Transfer Pilot Plan

**Purpose**: Test whether Gemini 3.1 Flash-Lite preserves the performance
shape of Gemini 3 Flash — i.e., the same factors that improve/degrade
performance on Flash also improve/degrade performance on Flash-Lite, even
if absolute F1 is lower.

**Model**: `gemini-3.1-flash-lite-preview`
**Tile size**: 512×512 (60 validation tiles)
**Execution**: Batch API (`--mode batch`)
**Base config**: `detect_brief-text.json` with model override

---

## Motivation

Most of our Phase 2 calibration decisions are "vibe-based" — directionally
consistent but not statistically significant at n=60. Flash-Lite's 2× lower
cost (4× with Batch API) would make comprehensive reruns with the full
ground truth tile corpus affordable, enabling properly powered statistical
tests.

The pilot answers three questions:

1. **Can Flash-Lite detect mound symbols at all?** (capability gate)
2. **Do the same factors matter?** (ordinal ranking transfer)
3. **Is the performance gap uniform?** (shape similarity)

## Concerns

1. Flash-Lite may simply fail on this niche visual task (Soviet topographic
   map symbols at 512×512 resolution)
2. The error profile may be qualitatively different (different FP types),
   making ordinal comparisons meaningless
3. The Gemini 3 documentation warns that T < 1.0 "may lead to unexpected
   behavior, such as looping" — our optimal T=0.0 is at the extreme

---

## Staged Design

Each stage gates on the previous one succeeding. If a gate fails, we stop
and document where the transfer breaks down.

### Stage 1: Basic Capability

**Test**: Single-pass detection with the optimal Flash config.

| Run | Config | T | Calls | Est. cost |
|:----|:-------|--:|------:|----------:|
| 1a | `detect_brief-text.json` | 0.0 | 60 | ~$0.005 |

**Gate**: F1 > 0.2 at 20 m tolerance. Below this, the model cannot parse
map symbols and the pilot stops.

**Also check**: Does T=0.0 cause looping or degraded output? If so, retry
at T=0.3 before declaring failure.

### Stage 2: Single-Pass Contrasts

**Test**: The two largest-effect contrasts from Flash Phase 2.

| Run | Config | T | Contrast | Flash effect |
|:----|:-------|--:|:---------|:-------------|
| 2a | `detect_image-only.json` | 0.0 | H1: modality | ~+5 pp for text-only |
| 2b | `detect_brief-text.json` | 1.0 | H7: temperature | ~−8 pp vs T=0.0 |

**Gate**: Both ordinal rankings preserved (text-only > image-only, and
T=0.0 > T=1.0). If either reverses, the performance shape doesn't transfer
and Flash-Lite calibration would need independent optimisation.

**Calls**: 120 total (~$0.01)

### Stage 3: Consensus Voting

**Test**: Does consensus voting improve over single-pass, as it did on
Flash?

| Run | Config | T | N | Calls | Notes |
|:----|:-------|--:|--:|------:|:------|
| 3a | `detect_brief-text.json` | 0.7 | 5 | 300 | Consensus pool |

**Evaluate**: Sweep vote thresholds T>=1 through T>=5. Compare best
consensus F1 to Stage 1a single-pass F1.

**Gate**: Consensus F1 > single-pass F1. On Flash, consensus at N=5 added
~+12 pp.

**Calls**: 300 (~$0.02)

### Stage 4: Proposer-Verifier

**Test**: Does the two-stage pipeline improve precision, as it did on
Flash?

| Run | Stage | Config | T | Calls |
|:----|:------|:-------|--:|------:|
| 4a | Proposer | Stage 1a output (reuse) | — | 0 |
| 4b | Verifier | `verify_adversarial-text.json` | 0.0 | ~140 |

**Gate**: PV F1 > single-pass F1 (Stage 1a). On Flash, PV added ~+7 pp
(corrected v2).

**Calls**: ~140 (~$0.01)

**Note**: The verifier also needs model override to Flash-Lite. Check
whether `5_verify_crops.py` supports `--model` override; if not, create
a Flash-Lite verifier config.

---

## Totals

| Stage | Calls | Cost (Batch) | Cumulative |
|:------|------:|-------------:|-----------:|
| 1 | 60 | $0.005 | $0.005 |
| 2 | 120 | $0.01 | $0.015 |
| 3 | 300 | $0.02 | $0.035 |
| 4 | 140 | $0.01 | $0.045 |
| **Total** | **620** | **~$0.05** | |

---

## Implementation Notes

- **Model override**: Use `--model gemini-3.1-flash-lite-preview` at CLI
  (or create Flash-Lite config variants). Verify `lib_batch_api.py` passes
  model override through to JSONL.
- **Evaluation**: Use the same 20 m tolerance, same ground truth, same
  bounds as all Flash experiments. The comparison is ordinal (does the
  ranking transfer?), not absolute (we expect lower F1).
- **Output directory**: `outputs/flash-lite-pilot/`
- **Configs needed**: May need Flash-Lite verifier config for Stage 4
  (`verify_adversarial-text-flash-lite.json` or model override)
- **Study YAML**: Create `studies/flash-lite-pilot.yaml` for each stage

## Success Criteria

The pilot succeeds if **all four gates pass** — meaning Flash-Lite
preserves the ordinal performance shape across modality, temperature,
consensus, and verification. This justifies proceeding to a full-scale
replication with the complete ground truth tile set.

## If the Pilot Fails

Document which gate failed and why. Possible outcomes:

- **Gate 1 fails**: Flash-Lite can't parse map symbols. Consider
  Flash-Lite with HIGH thinking, or abandon Flash-Lite pathway.
- **Gate 2 fails**: Performance shape doesn't transfer. Flash-Lite
  needs independent calibration (defeats the purpose).
- **Gate 3 fails**: Consensus doesn't help. May still proceed with
  single-pass at scale if Gates 1–2 passed.
- **Gate 4 fails**: PV doesn't help. Same as Gate 3.

---

## Status

- [ ] Stage 1: Basic capability (pending)
- [ ] Stage 2: Single-pass contrasts (pending)
- [ ] Stage 3: Consensus voting (pending)
- [ ] Stage 4: Proposer-verifier (pending)
- [ ] Decision: proceed to full-scale / abandon / modify
