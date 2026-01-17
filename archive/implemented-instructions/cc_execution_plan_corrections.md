# Execution Plan Corrections

**Document:** `execution-plan.md`  
**Issues Found:** API call counts and cost estimates are systematically incorrect  
**Root Cause:** Missing N=5 consensus voting factor in calculations

---

## Issue Summary

The execution plan calculates API calls as: `cells × K × tiles`  
But should calculate as: `cells × K × tiles × N`

Where:
- K = 10 independent runs
- tiles = 60 holdout tiles  
- **N = 5 consensus voting passes per run** (MISSING from current calculations)

---

## Corrections Needed

### 1. Hard Negative Target Count (Line 173)

**Current:**
```markdown
- Hard negatives: Top M FPs (target M=3)
```

**Corrected:**
```markdown
- Hard negatives: Top M FPs (target M=4)
```

**Rationale:** Scale-8 library composition specifies HN=4, not 3. This is consistent throughout preregistration (Canon+ 4, Canon- 2, HP 4, **HN 4**, null 3 = 17 total).

---

### 2. Phase 2a Cost (Lines 266-267)

**Current:**
```markdown
- 5 × K=10 × 60 tiles = **3,000 API calls** (~$11)
```

**Corrected:**
```markdown
- 5 × K=10 × 60 tiles × N=5 = **15,000 API calls** (~$55)
```

**Explanation:** Each cell requires 3,000 calls (K=10 × 60 × N=5). With 5 cells total = 15,000 calls at ~$55 total.

---

### 3. Phase 2b Cost (Lines 292-293)

**Current:**
```markdown
- 5 × K=10 × 60 = **3,000 API calls** (~$11)
```

**Corrected:**
```markdown
- 5 × K=10 × 60 × N=5 = **15,000 API calls** (~$55)
```

**Explanation:** Same as Phase 2a - 5 cells × 3,000 calls/cell = 15,000 total calls.

---

### 4. Phase 2c Cost (Lines 321-322)

**Current:**
```markdown
- 7 × K=10 × 60 = **4,200 API calls** (~$21)
```

**Corrected:**
```markdown
- 7 × K=10 × 60 × N=5 = **21,000 API calls** (~$77)
```

**Explanation:** 7 cells × 3,000 calls/cell = 21,000 total calls.

---

### 5. Phase 2e Cost (Lines 385-386)

**Current:**
```markdown
- 3 × K=10 × 60 = **1,800 API calls** (~$8)
```

**Corrected:**
```markdown
- 3 × K=10 × 60 × N=5 = **9,000 API calls** (~$33)
```

**Explanation:** 3 cells × 3,000 calls/cell = 9,000 total calls.

---

### 6. Phase 2d H5 Cost (Lines 360-361)

**Current:**
```markdown
- 6 × K=10 × 60 = **3,600 API calls** (~$66)
```

**Corrected:**
```markdown
- 6 × K=10 × 60 × N=5 = **18,000 API calls** (~$66)
```

**Explanation:** 6 cells × 3,000 calls/cell = 18,000 total calls. The cost estimate (~$66) is actually correct, but the API call count was wrong.

---

### 7. Evaluation Protocol Clarification (Line 398)

**Current:**
```markdown
Each condition is evaluated using K=10 independent single-pass runs (see preregistration Section 3.8):
```

**Suggested Addition:**
```markdown
Each condition is evaluated using K=10 independent runs with N=5 consensus voting per run (see preregistration Section 3.8):

- Each run makes 5 independent API calls per tile (consensus voting)
- Voting result (threshold-based) is the primary output per run
- Post-hoc analysis also compares single-pass results to voted results
```

**Rationale:** The term "single-pass run" is ambiguous. Clarify that each run uses N=5 consensus voting, but "single-pass" refers to producing one consensus result per run (as opposed to analyzing multiple voting configurations).

---

## Cost Summary Table

After corrections, per-phase costs should be:

| Phase | Description | Cells | API Calls | Cost (~$11/cell) |
|-------|-------------|-------|-----------|------------------|
| 2a | H1 M/E | 5 | 15,000 | ~$55 |
| 2b | H7 Temperature | 5 | 15,000 | ~$55 |
| 2c | H8 Library | 7 | 21,000 | ~$77 |
| 2d | H5 Negative Text | 6 | 18,000 | ~$66 |
| 2e | H4 Ordering | 3 | 9,000 | ~$33 |
| **Confirmatory Total** | | **26** | **78,000** | **~$286** |

This matches the preregistration budget table exactly (Section 8.4.7, line 1825-1832).

---

## Understanding "Single-Pass" vs "Consensus Voting"

The preregistration terminology is:

- **"Single-pass run"** = One independent execution producing one consensus-voted result per tile
  - Internally uses N=5 voting to produce that result
  - "Single" refers to producing one output, not one API call
  
- **"Post-hoc voting analysis"** = Taking the K=10 single-pass results and computing additional voting schemes
  - N=5 voting: Pool runs 1-5 together, or runs 6-10 together
  - N=10 voting: Pool all 10 runs together
  - Tests different aggregation strategies from the same data

- **"H3 extended voting (N=30)"** = Additional 20 runs at optimal config
  - Enables deeper voting analysis
  - 20 new runs × 60 tiles × N=5 = 6,000 additional API calls

---

## Implementation Note for CC

When implementing the execution code, ensure that for each run on each tile:

```python
def run_detection_with_voting(config, tile, run_num):
    """
    Execute one run with N=5 consensus voting.
    
    Returns:
        - Single consensus result (primary output)
        - Individual pass results (for post-hoc analysis)
    """
    individual_results = []
    
    # Make N=5 independent API calls
    for pass_num in range(5):
        response = call_vlm_api(config, tile)
        result = parse_response(response)
        individual_results.append(result)
    
    # Compute consensus (e.g., 3-of-5 threshold)
    consensus_result = compute_consensus(individual_results, threshold=3)
    
    # Save both for analysis
    save_individual_passes(individual_results)  # For post-hoc voting
    save_consensus_result(consensus_result)      # Primary output
    
    return consensus_result
```

Each "run" makes 5 API calls per tile for consensus voting.

---

## Verification Checklist

After making corrections:

- [ ] All API call counts include × N=5 factor
- [ ] All per-phase costs match preregistration budget table
- [ ] Hard negative target count is M=4 (not 3)
- [ ] Total confirmatory cost is ~$286 (26 cells)
- [ ] Evaluation protocol clarifies N=5 consensus voting per run
- [ ] Total confirmatory API calls = 78,000
