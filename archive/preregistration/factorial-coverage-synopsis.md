# Factorial Coverage Synopsis

**Date**: 2026-01-02
**Status**: FINAL — All decisions incorporated

---

## 1. Core Prompt Configuration Factors

These factors control how a single detection prompt is constructed:

| Factor | Symbol | Levels | Hypothesis |
|--------|--------|--------|------------|
| Modality | M | 2 (image-only, text+image) | H1 |
| Elaboration | E | 2 (brief, elaborate) | H2 |
| Hard negatives | H | 2 (without, with) | H7 |
| Ordering | O | 3 (canonical-first, canonical-last, random) | H5 |
| Temperature | T | 4 (0.0, 0.3, 0.7, 1.0) | H9 |

### Pairwise Coverage Matrix

**✅ All 10 pairwise combinations of core factors are covered:**

| Pair | Covered By | Conditions |
|------|------------|------------|
| M × H | Main factorial | 2 × 2 = 4 |
| M × O | Main factorial | 2 × 3 = 6 |
| M × T | Main factorial | 2 × 4 = 8 |
| H × O | Main factorial | 2 × 3 = 6 |
| H × T | Main factorial | 2 × 4 = 8 |
| O × T | Main factorial | 3 × 4 = 12 |
| M × E | H2 design | 2 × 2 = 4 |
| E × H | H2 design | 2 × 2 = 4 |
| E × O | Added coverage | 2 × 3 = 6 |
| E × T | Added coverage | 2 × 4 = 8 |

---

## 2. Ensemble/Meta Factors

These factors operate "on top of" the base prompt configuration:

| Factor | Symbol | Levels | Hypothesis |
|--------|--------|--------|------------|
| Text diversity | TD | 2 (fixed, varied) | H6 |
| Image diversity | ID | 2 (fixed, varied) | H6 |
| Voting pool size | N | 4 (1, 5, 10, 30) | H4 |
| Pipeline architecture | P | 2 (single-stage, two-stage) | H3 |
| Model tier | MT | 4+ (Flash, Pro, Claude, GPT) | H8, H12 |

---

## 3. Experimental Designs Summary

### 3.1 Main Factorial (H1, H5, H7, H9)

**Design**: M(2) × O(3) × H(2) × T(4) = **48 conditions**

### 3.2 H2 Design (Elaboration)

**Core**: M(2) × E(2) × H(2) = **8 conditions**
**Extensions**: E×O (6) + E×T (8) = **14 conditions**
**Total H2-related**: **22 conditions**

### 3.3 H6 Design (Diversity)

**Design**: TD(2) × ID(2) = **4 conditions** × 5 runs each = **20 runs**

### 3.4 Extended Coverage (Tiers 1-3)

| Tier | Tests | Conditions/Calls |
|------|-------|------------------|
| **Tier 1** | TD×H, ID×H, N×H | 8 + 1 grid |
| **Tier 2** | N×M, TD×M, ID×M, Pro voting | 8 + 2 grids |
| **Tier 3** | N×T, Extended cross-model | 4 grids + extra |

---

## 4. Complete Coverage Matrix

### ✅ Fully Covered

| Interaction Type | What's Covered |
|------------------|----------------|
| **Core factor pairs** | All 10 M/E/H/O/T pairs |
| **Diversity internal** | TD × ID |
| **Diversity × Hard negatives** | TD×H, ID×H |
| **Diversity × Modality** | TD×M, ID×M |
| **Voting × Hard negatives** | N × H (full grid) |
| **Voting × Modality** | N × M (full grid) |
| **Voting × Temperature** | N × T (full grid) |
| **Pro validation** | Factorial corners + voting grid |

### ⚠️ Single-Configuration Testing (with rationale)

| Factor | Approach | Rationale | Caveat |
|--------|----------|-----------|--------|
| H6 Diversity | Tested at optimal base config | Mechanism (error decorrelation) is general; should generalize | "Generalization to other configurations assumed" |
| H4 Voting optimal | Grid at optimal base config | Preliminary shows ~30-40% consistent | "Contingent follow-up if interactions detected" |

### ❌ Explicitly Excluded (with rationale)

| Interaction | Reason |
|-------------|--------|
| **TD × O, ID × O** | Weak mechanism: diversity operates independently of ordering |
| **TD × T, ID × T** | Weak mechanism: temperature affects variance, not diversity effects |
| **Full TD×ID×H×M** | Diminishing returns: core question answered by TD×ID |
| **P × {anything}** | Gated: must pass -0.10 F1 threshold first |
| **Full MT × {all}** | Transfer testing only; full optimization if cost-effective |
| **Stage 2 pilot** | Deferred: need Stage 1 results to design properly |

---

## 5. Cost Breakdown

| Category | Conditions | Calls | Cost |
|----------|------------|-------|------|
| Main factorial | 48 | 4,800 | $7 |
| H2 (core + extensions) | 22 | 2,200 | $3 |
| H3 two-stage | 2 | 400 | $1 |
| H4 voting grid | ~45 | 900 | $1 |
| H6 diversity (5 runs) | 20 runs | 2,000 | $3 |
| **Flash confirmatory** | | ~10,300 | **$15** |
| H8 Pro transfer | ~14 | 1,400 | $21 |
| **Confirmatory total** | | ~11,700 | **$36** |
| Exploratory (H10-H16) | | ~6,400 | $62 |
| Extended (Tiers 1-3) | | ~9,900 | $33 |
| **GRAND TOTAL** | | ~28,000 | **~$131** |

**Remaining from $250 budget**: ~$119 (contingency, escalation, Stage 2 seed)

---

## 6. Claims Supported by This Design

### Strong Claims (Full Factorial Coverage)
- "The optimal prompt configuration is X"
- "Factors A and B do/don't interact" (for all core factor pairs)
- "Hard negatives affect diversity effectiveness" (TD×H, ID×H tested)
- "Voting threshold varies by modality/hard negatives" (N×M, N×H tested)

### Supported with Caveats
- "Optimal voting threshold is X" — "at optimal base configuration; consistent in preliminary testing"
- "Diversity helps/doesn't help" — "tested at one configuration; generalization assumed based on mechanism"
- "Effects transfer to Pro/Claude/GPT" — "at tested configurations; stepwise adjustment if needed"

### Not Supported (Explicitly Out of Scope)
- "Diversity effect varies by ordering" — not tested (weak mechanism)
- "Two-stage architecture can be optimized to match single-stage" — only tested if competitive
- "Per-model optimization improves on Flash-optimal" — only if cost-effective

---

## 7. Stage 2 Design Principles

**Deferred to post-Stage-1, but pre-specified:**

1. Test **top 3-5 configurations**, not just winner
2. Use **80-160 reserve tiles** (from 321 available)
3. Design based on **observed effect sizes** from Stage 1
4. **Separately preregistered** after Stage 1 completion

---

*Final version — 2026-01-02*
