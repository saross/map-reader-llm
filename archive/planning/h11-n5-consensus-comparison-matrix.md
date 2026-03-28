# Plan: Document Session 56 Work

## Context

Session 56 produced significant results and code changes that are not yet documented. Batch API jobs are running in background (Flash HIGH and Pro HIGH proposer runs). This plan covers all documentation tasks while we wait.

## Task 1: Working notes observations

Add to `docs/notes/reflections/working-notes.md`. Current numbering at Obs 182.

**Obs 183**: Pro MEDIUM single-pass underperforms Flash MINIMAL
- Flash × Pro comparison matrix (8 conditions)
- Pro proposer degrades F1 by 0.039–0.102; Pro verifier helps marginally (+0.01)
- The MEDIUM thinking constraint (Pro's lowest) may explain the proposer degradation
- Surprising: a more capable model performing worse on visual pattern matching

**Obs 184**: N=5 vs N=10 pool size — dramatic impact on PV pipeline
- Text N=5 + PV best F1=0.600 vs N=10 best F1=0.883
- Image N=5 + PV best F1=0.771 (pre-existing) vs N=10 best F1=0.789
- Pool size matters much more for text than image
- The 1-of-N union approach for verifier cost saving worked correctly

**Obs 185**: Gemini 3.1 Pro MINIMAL thinking silent failure
- All 487 tiles returned empty — no error message in batch results
- Only `partial_failure_N_tiles` in checkpoint revealed the problem
- Required `--thinking-level medium` override on both proposer and verifier paths
- `extract_conditions()` bug: pre-enumerated conditions path dropped `thinking_level`

## Task 2: Protocol errata

Add to `docs/methodology/preregistration/protocol-errata.md`. Current numbering at E39.

**E40**: Gemini 3.1 Pro requires MEDIUM thinking (deviation from §8.2/§8.9)
- The preregistration specifies `thinking_level=minimal` for both Flash and Pro
- Gemini 3.1 Pro does not support MINIMAL; MEDIUM is the lowest available
- All Pro runs use MEDIUM (single-pass) or HIGH (consensus) thinking
- Type: Deviation
- Impact: Pro results not directly comparable to Flash at matched thinking level

**E41**: 384px tile size used for Pro comparison (deviation from H6 scope)
- H6 specifies 20-tile holdout subset at 512px
- Our Pro comparison uses 487 tiles at 384px (the optimal tile size from H11)
- More statistical power but different evaluation scope
- Type: Deviation

## Task 3: Update bootstrap-cis-384px.json

Add new conditions to `results/h11-384-pv-diagnostic/bootstrap-cis-384px.json`:

From existing threshold_sweep.json files, extract best F1 + CIs for:
- `384px-pv-text-1of5` through `384px-pv-text-5of5` (5 entries)
- `384px-pv-image-1of10` through `384px-pv-image-10of10` (10 entries)
- `384px-pro-medium-text-flash-verifier` (Pro proposer + Flash verifier, text)
- `384px-pro-medium-image-flash-verifier` (Pro proposer + Flash verifier, image)
- `384px-flash-text-pro-verifier` (Flash proposer + Pro verifier, text)
- `384px-flash-image-pro-verifier` (Flash proposer + Pro verifier, image)
- `384px-pro-medium-text-pro-verifier` (Pro proposer + Pro verifier, text)
- `384px-pro-medium-image-pro-verifier` (Pro proposer + Pro verifier, image)

Total: 21 new entries. Extract from threshold_sweep.json by finding the threshold with the highest F1 mean.

Script approach: write a small consolidation script (or inline Python) that reads each threshold_sweep.json file, finds the optimal threshold, and adds to the consolidated JSON. Run on sapphire.

## Task 4: Commit code changes

Logical commits (granular, one concern per commit):

1. **feat(evaluate): add --bounds override to evaluate_pv_results.py**
   - `scripts/evaluate_pv_results.py`

2. **feat(run-phase2): add --model override for cross-model experiments**
   - `scripts/run_phase2.py` (--model threading)

3. **fix(run-phase2): propagate thinking_level in pre-enumerated conditions**
   - `scripts/run_phase2.py` (extract_conditions fix)

4. **feat(run-pv): add --thinking-level override for verifier**
   - `scripts/run_pv.py`

5. **feat(pricing): add Gemini 3.1 Pro to pricing table**
   - `scripts/lib_llm_metadata.py`

6. **feat(pv): add derive_vote_threshold_results.py for union-based evaluation**
   - `scripts/derive_vote_threshold_results.py`

7. **docs(CLAUDE.md): add critical compute location requirement (sapphire)**
   - `CLAUDE.md`

8. **feat(studies): add Pro pilot and consensus comparison study YAMLs**
   - `studies/h11-384-pro-pilot-text.yaml`
   - `studies/h11-384-pro-pilot-image.yaml`
   - `studies/h11-384-flash-high-text-n5.yaml`
   - `studies/h11-384-flash-high-image-n5.yaml`
   - `studies/h11-384-pro-high-text-n5.yaml`
   - `studies/h11-384-pro-high-image-n5.yaml`

9. **docs: Obs 183–185 — Pro pilot results and thinking level findings**
   - `docs/notes/reflections/working-notes.md`

10. **docs(errata): E40–E41 — Pro thinking level and evaluation scope deviations**
    - `docs/methodology/preregistration/protocol-errata.md`

11. **data: update bootstrap-cis-384px.json with session 56 results**
    - `results/h11-384-pv-diagnostic/bootstrap-cis-384px.json`

## Task 5: Copy plan to planning/

Per scratchpad preference, save the approved N=5 consensus comparison matrix plan to `planning/` for git tracking.

## Execution order

1. Tasks 1–2 first (writing observations and errata — read-only research, write to docs)
2. Task 3 (consolidate results — run on sapphire)
3. Task 4 (commits — sequential, granular)
4. Task 5 (copy plan)

## Verification

- `npx markdownlint-cli2` on all modified .md files
- `ruff check` on all modified .py files
- `git log --oneline -15` to verify commit sequence
- Spot-check bootstrap-cis entries against threshold_sweep.json source files
