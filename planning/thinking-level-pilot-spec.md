# Thinking Level Calibration Pilot

**Date:** January 12, 2026  
**Purpose:** Determine optimal thinking level before main experiment  
**Priority:** Run before main experiment begins  
**Estimated cost:** ~$12

---

## Context

Gemini 3 introduces configurable `thinking_level` that controls reasoning depth. Symbol detection may not require deep reasoning — it's primarily pattern recognition and localisation. Running the entire experiment at "high" (default) when "low" would suffice wastes compute and potentially degrades performance through "overthinking."

This pilot establishes the optimal thinking level to use for all subsequent experimental runs.

---

## Pilot Parameters

| Parameter | Value | Notes |
|-----------|-------|-------|
| **Model** | Gemini 3 Flash | Primary development model |
| **Tiles** | 20 training tiles | Already contaminated for prompt dev; fine for parameter calibration |
| **Library** | Canonical only | Canon+ (4) + Canon- (2) + Nulls (3) = 9 examples |
| **Runs per condition** | K=10 | Matches main experiment protocol; provides stable variance estimates |
| **Temperature** | T=1.0 | Gemini 3 default |
| **Ordering** | Canonical-first | Default |

**Note on sample size:** Training tiles contain 36 mounds. With K=10 runs, this provides 10 independent F1 estimates per condition — sufficient to detect gross differences (>0.10 F1) and moderate differences (~0.05 F1) with reasonable confidence. If results remain ambiguous, default to Google's recommended "high" setting.

---

## Conditions

| Condition | `thinking_level` | Description |
|-----------|------------------|-------------|
| 1 | `minimal` | Near-zero reasoning; fastest; may still think on complex tasks |
| 2 | `low` | Minimal reasoning; optimised for latency/cost |
| 3 | `high` | Full reasoning depth (Gemini 3 default) |

**Total API calls:** 3 conditions × 10 runs × 20 tiles = **600 calls**

**Estimated cost:** ~$12

---

## API Parameter

Set via `thinking_level` in the generation config:

```python
generation_config = {
    "temperature": 1.0,
    "thinking_level": "low"  # or "minimal" or "high"
}
```

**Note:** Do not use `thinking_budget` (legacy parameter for Gemini 2.5). Use `thinking_level` for Gemini 3.

**Reference:** https://ai.google.dev/gemini-api/docs/thinking

---

## Outputs Required

For each condition, compute and report:

1. **Symbol-level metrics** (at 20m tolerance):
   - Precision
   - Recall
   - F1 (primary metric)

2. **Variance**:
   - Mean F1 across K=10 runs
   - Standard deviation
   - 95% CI

3. **Operational metrics** (if easily captured):
   - Mean latency per tile
   - Token usage (input/output/thinking tokens if available)

---

## Decision Criteria

| Outcome | Action |
|---------|--------|
| high >> low (F1 difference > 0.05) | Use `high` for main experiment |
| high ≈ low (F1 difference ≤ 0.03) | Use `low` for main experiment (cost/latency savings) |
| low > high | Use `low` (task benefits from less reasoning) |
| minimal ≈ low | Consider `minimal` for maximum efficiency |
| Ambiguous (0.03 < difference < 0.05, overlapping CIs) | Default to `high` (Google's recommended setting) |

**Primary comparison:** low vs high  
**Secondary comparison:** minimal vs low (if low ≈ high)

---

## Reporting Format

```markdown
## Thinking Level Pilot Results

**Date run:** [DATE]
**Model:** gemini-3-flash-preview

| Thinking Level | Mean F1 | SD | 95% CI | Mean Latency | Notes |
|----------------|---------|-----|--------|--------------|-------|
| minimal | | | | | |
| low | | | | | |
| high | | | | | |

**Recommendation:** Use [LEVEL] for main experiment because [REASON].
```

---

## Notes

- This pilot uses training tiles, which are "contaminated" for prompt development but appropriate for parameter calibration
- Canonical-only library is sufficient — we're testing model behaviour, not library composition
- If results are surprising or ambiguous, we can run a follow-up with full library before main experiment
- Results should be documented in the preregistration as calibration/pilot work

---

## Questions for SR Before Running

None — proceed when ready. Report results before main experiment begins so we can set thinking level appropriately.
