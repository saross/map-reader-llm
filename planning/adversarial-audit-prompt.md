# Adversarial Results Audit

## Task Declaration

This is an ADVERSARIAL VERIFICATION task. Your goal is to find the error
that inflates the reported F1 — or to demonstrate, with evidence, that no
such error exists. Assume the result is wrong until proven otherwise.

This is NOT a code review, not a general assessment, and not a suggestions
exercise. Do not comment on code quality, propose improvements, or note
"minor issues" unless they directly affect the reported F1. Every finding
must connect to a metric impact.

## Source of Truth

The sources of truth for this audit are, in order of authority:

1. **The codebase itself** — scripts, configs, and prompt files as they
   exist on disk
2. **Ground truth GeoJSON files** — the annotated burial mound locations
3. **Raw API response archives** — the model's actual outputs
4. **API response metadata** — model version strings, timestamps,
   token counts

When code behaviour contradicts documentation, comments, or commit
messages, the code is authoritative. When output metadata contradicts
input configuration, flag the mismatch — this is a known failure mode
in this pipeline.

## Framing

Our text-only VLM pipeline reports F1 > 0.9 for point symbol detection on
degraded Soviet topographic maps, using Gemini 3 Flash with zero visual
training examples. This result, if correct, substantially exceeds every
published benchmark for point symbol detection on historical maps (best
prior: F1 = 0.73, DARPA CriticalMAAS, using a trained U-Net with abundant
annotated data). It also exceeds the best published result for any map
symbol extraction task (U-Net wetland segmentation, F1 = 0.886).

**We assume this result contains an error.** Your task is to find it. The
error may be small or large, subtle or obvious, in the data, code,
pipeline, configuration, metric calculation, or evaluation methodology.
Small errors can mask larger ones, so investigate every anomaly — not only
those that would directly inflate F1.

## Scope

**IN SCOPE:** Every component of the pipeline that could inflate or
deflate the reported F1, including ground truth, tiling, API calls,
parsing, spatial matching, metric calculation, configuration, and
statistical analysis.

**OUT OF SCOPE (do not address):**

- Code style, naming conventions, or refactoring opportunities
- Performance optimisation or alternative algorithmic approaches
- Prompt wording improvements (unless a wording issue directly affects
  detection accuracy in a way that inflates the metric)
- Results from configurations other than the one reporting F1 > 0.9,
  except when used as cross-checks for consistency (Layer 7)

## Audit Protocol

Work in three explicit phases. Do not skip phases or combine them.

### Phase 1 — Inventory (enumerate before evaluating)

For each of the 8 layers below, enumerate every verifiable claim or
assumption the pipeline makes. Do not assess correctness during this phase.
Produce a numbered checklist of claims per layer.

Example claims to extract:

- "The ground truth contains N mound annotations across 4 maps"
- "The 30m spatial tolerance equals 6 pixels at 384px tile size"
- "The Hungarian algorithm matches detections one-to-one"
- "No calibration tiles appear in the production evaluation set"

### Phase 2 — Verify (check each claim with evidence)

For every claim inventoried in Phase 1, verify it in BOTH directions:

- **Direction 1 (code/data → claim):** Read the code or data and confirm
  it implements what the claim states.
- **Direction 2 (claim → code/data):** Starting from the claim, trace
  it to the specific line of code, config value, or data file that
  produces it.

For each verification, reason through explicitly:

1. What is the claim? (restate it precisely)
2. Where in the codebase is this implemented? (cite the file and
   function/line)
3. What evidence supports the claim being correct?
4. What evidence supports the claim being incorrect?
5. Verdict: PASS / CONCERN / FAIL — with the weight of evidence

Do not shortcut this reasoning. A check that "looks obviously fine" is
the most likely place for an error to hide.

### Phase 3 — Synthesise

Aggregate all layer verdicts into an overall assessment. Identify the
single most likely source of F1 inflation. If no error was found, state
your confidence level and identify the weakest link — the layer where
an undetected error is most plausible.

## When Blocked

Some checks cannot be performed directly (e.g., re-running the API costs
money, visual inspection of tiles requires human eyes). When blocked:

1. **Mark the check as BLOCKED** — do not silently skip it
2. **Check input configs against output metadata.** Read every input
   configuration file (prompt, study YAML, CLI flags) and verify that the
   output metadata (model version, token counts, timestamps, parameters)
   is consistent with what the configs specify. Configuration mismatches
   are a known failure mode in this pipeline — configs have been silently
   wrong before, and the mismatch was only revealed by auditing metadata.
3. **Compare with adjacent runs.** If you cannot re-run the target
   condition, examine runs that differ by exactly one factor. Check that
   the results are directionally consistent — e.g., if removing the
   verifier should reduce precision, does it? If changing tile size should
   shift recall, does it?
4. **State what would be needed** to convert the BLOCKED check to a PASS
   or FAIL

## Audit Layers

Examine every layer of the pipeline, working from ground truth through to
final metrics. For each layer, first enumerate every verifiable claim
(Phase 1), then verify each one (Phase 2).

### Layer 1: Ground Truth Integrity

- Enumerate every ground truth annotation file. How many files, how many
  annotations per file, how many total across all 4 maps?
- Check every annotation for duplicates (same mound annotated twice
  within or across files).
- Verify that annotation coordinates correctly align with tile pixel
  coordinates after tiling — spot-check at least 3 annotations per map
  by tracing coordinates through the tiling transform.
- When tiles are generated at 384px vs 512px, verify that every ground
  truth point re-maps to exactly one tile at each size. Check for points
  lost at tile boundaries.
- Confirm the total ground truth count is consistent across every report,
  script, and output file that references it. List every source and the
  count it reports.

### Layer 2: Tile Generation and Coverage

- Verify that the 384px and 512px tile sets cover exactly the same
  geographic extent — compare bounding boxes.
- Confirm the overlap/stride implementation for both tile sizes by reading
  the tiling code and computing expected tile counts from map dimensions.
- Enumerate every ground truth point and confirm none fall in gaps between
  tiles.
- Identify every tile excluded from the production evaluation set
  (training/calibration tiles). List them by ID. Confirm none appear in
  the evaluated set.
- Report exact tile counts: total generated, excluded, evaluated — for
  each tile size.

### Layer 3: API Response Parsing

- Confirm raw API responses are archived. Spot-check at least 3 response
  files for structural integrity.
- Read the parser code and identify every code path that could silently
  drop a detection (regex mismatches, exception handlers that swallow
  errors, default returns of empty lists).
- For the consensus proposer + adversarial verifier pipeline: trace the
  exact data flow from proposer output through to verifier input through
  to final reconciliation. Document every transformation step.
- Count the number of tiles with parsed results and compare to the number
  submitted. If they differ, identify every missing tile and the reason
  for its absence.

### Layer 4: Spatial Matching (Hungarian Algorithm)

- Verify the pixel-to-metre conversion factor by reading the code that
  computes it. Confirm it is correct for both 384px and 512px tiles using
  the known map scale and resolution.
- At 30m tolerance: compute the maximum pixel distance allowed for each
  tile size. Show the arithmetic.
- Read the Hungarian algorithm implementation. Confirm detections are
  matched one-to-one with no double-counting. Check boundary handling
  (what happens at exactly the tolerance distance?).
- **Critical check**: run the matching at 1m, 5m, 10m, 15m, 20m, 25m,
  30m, 40m, 50m and plot the full spatial tolerance curve. Verify the
  curve is monotonically non-decreasing. Identify the inflection point
  and confirm it is consistent with the expected symbol spacing on these
  maps.

### Layer 5: Metric Calculation

- Verify F1, precision, and recall calculations from raw TP/FP/FN
  counts. Show the arithmetic.
- Confirm TP + FN = total ground truth symbols. If not, identify every
  unaccounted symbol and explain why it is missing.
- Determine how empty tiles (no ground truth, no detections) are handled.
  Verify they do not inflate F1.
- For consensus voting: trace the code path to confirm the voting
  threshold is applied before spatial matching, not after.
- **Spot-check**: select 5 random tiles (provide the tile IDs), manually
  verify the detections against ground truth, confirm TP/FP/FN counts
  match the pipeline output for each tile.

### Layer 6: Configuration and Pipeline Integrity

- Identify the exact configuration that produced F1 > 0.9. List every
  parameter: model, prompt file, thinking level, temperature, tile size,
  consensus pool size, voting threshold, verifier config.
- Check for cached results, intermediate files, or stale outputs that
  could contaminate the evaluation. List every intermediate file in the
  output directory and confirm its timestamp is consistent with the
  reported run.
- Read every prompt file used and confirm none contain embedded images,
  image references, or base64-encoded content.
- Read the API response metadata for at least 3 tiles and confirm the
  model called is Gemini 3 Flash (verify the exact model version string).
- Document exactly what differs between the proposer and verifier
  configurations (prompt, model, thinking level, temperature). Confirm
  only the intended parameters differ.

### Layer 7: Cross-Configuration Consistency

- Compare the F1 > 0.9 configuration against at least 3 worse-performing
  configurations. For each pair, identify the parameter that differs and
  confirm the performance difference is directionally consistent with
  expectations.
- If text-only F1 > 0.9 but text+image F1 is substantially lower, this
  requires explanation — investigate whether the image condition uses a
  different prompt, model, or pipeline path that could account for the
  gap.
- Verify that single-pass (no consensus voting) performance sits in a
  plausible range given the voted result. Compute the expected
  relationship between single-pass and voted performance.
- Confirm the 384px vs 512px results are internally consistent with the
  reported direction of effect.

### Layer 8: Statistical Validity

- How many independent runs contribute to the F1 > 0.9 figure? Are they
  truly independent (different API calls, not cached copies)?
- Verify the bootstrap CI implementation: read the code, confirm the
  resampling unit (tiles, not individual detections), confirm the number
  of iterations, confirm the CI calculation method.
- Enumerate every configuration tested in the full study. How many
  pairwise comparisons does this imply? Is FDR correction applied, and
  does it change which results are significant?
- After FDR correction at q = 0.05, does the F1 > 0.9 result remain
  statistically distinguishable from the next-best configuration?

## Specific Failure Hypotheses

These are hypotheses for how F1 could be artificially inflated. Test each
one explicitly — state the evidence for and against, then render a verdict.
Do not dismiss a hypothesis without evidence.

1. **Ground truth leakage**: Are any ground truth coordinates visible to
   the model (e.g., baked into tile filenames, embedded in prompt
   metadata, passed as part of the API request)?
2. **Tolerance inflation**: Is 30m / 6px actually correct, or has a unit
   conversion error made the tolerance larger than intended? Show the
   arithmetic from map scale through to pixel distance.
3. **Double-counting TPs**: Could a single detection match multiple ground
   truth points, or vice versa? Read the matching code and confirm
   one-to-one assignment.
4. **Selective tile exclusion**: Are tiles where the model performs poorly
   being silently dropped? Compare the set of tiles submitted to the API
   against the set of tiles in the evaluation. Account for every
   difference.
5. **Contamination between proposer and verifier**: Does the verifier
   see the proposer's coordinates in a way that biases it toward
   confirmation? Trace the exact data passed from proposer to verifier.
6. **Empty tile inflation**: If empty tiles (no mounds, no detections)
   are counted as perfect performance, this inflates F1. Verify how
   empty tiles contribute to the aggregate metric.
7. **Training tile inclusion**: List every tile ID in the production
   evaluation set. List every tile ID used for calibration/training.
   Confirm zero overlap.
8. **Stale results**: Verify that the output files used for metric
   calculation were produced by the configuration claimed. Check
   timestamps, model version metadata, and parameter logs.
9. **Configuration mismatch**: Verify that every input configuration file
   (prompt, study YAML, system instruction) used in the reported run
   matches the parameters recorded in the output metadata. This is a
   known failure mode — configs have silently diverged from intended
   parameters in this pipeline before.

## Prohibitions

DO NOT:

- Declare a check "PASS" without citing the specific file, line, or data
  point that confirms it
- Accept a plausible explanation for an anomaly without verifying the
  explanation against the code — "this is probably because..." is not
  evidence
- Skip a check because it "appears straightforward" — straightforward
  checks are where errors hide when the complex ones have been debugged
- Group multiple checks under a single verdict — each check gets its own
  status
- Propose fixes, improvements, or alternative approaches — this is a
  verification task, not a development task
- Conclude the audit without completing the completeness check (see below)

## Output Format

For each layer, report using this exact structure:

```text
### Layer N: [Layer Name]

**Claims inventoried:** [count]

| # | Claim | Evidence checked | Verdict | Impact on F1 |
|---|-------|-----------------|---------|--------------|
| 1 | Ground truth contains 83 annotations on Map K-35-052 | Counted features in GT GeoJSON: 83 features found | PASS | None |
| 2 | 30m tolerance = 6px at 384px tile size | Pixel size = 5.0m (from tiling code, line 47); 30m / 5.0m = 6.0px | PASS | None |
| 3 | No calibration tiles in evaluation set | Calibration list has tile IDs [x, y, z]; tile "y" also appears in evaluation set | FAIL | Inflates F1 — calibration tile performance likely higher than production |

**Layer verdict:** PASS / CONCERN / FAIL
**Reasoning:** [2-3 sentences explaining the verdict, citing evidence]
```

For the Specific Failure Hypotheses section, use:

```text
| # | Hypothesis | Evidence FOR inflation | Evidence AGAINST inflation | Verdict |
|---|-----------|----------------------|--------------------------|---------|
| 1 | Ground truth leakage | [specific evidence or "None found"] | [specific evidence] | REJECTED / PLAUSIBLE / CONFIRMED |
```

## Success Criteria

This audit is complete when ALL of the following are satisfied:

- [ ] Every claim in every layer has been inventoried and individually
      verified with a cited evidence source
- [ ] Every specific failure hypothesis has been tested with evidence
      for and against, and given an explicit verdict
- [ ] Every BLOCKED check includes: (a) what was blocked, (b) what
      indirect evidence was examined, (c) what would be needed to resolve
- [ ] Every CONCERN or FAIL includes a directional estimate of F1 impact
- [ ] The completeness check (below) has been performed
- [ ] An overall confidence assessment has been provided

## Completeness Check (mandatory final step)

After completing all 8 layers and all 9 failure hypotheses, perform this
check before writing your overall assessment:

1. List every layer and confirm it received a verdict.
2. List every failure hypothesis and confirm it received a verdict.
3. List every check you marked BLOCKED and confirm you applied the
   indirect verification protocol (config-vs-metadata audit, adjacent
   run comparison).
4. Identify the layer you spent the LEAST time on. Go back and verify
   you did not rush it.
5. Ask yourself: "If the error is in the one place I didn't look
   carefully, where would that be?" Check there.

## Overall Assessment

After the completeness check, conclude with:

1. **Confidence level** that F1 > 0.9 is genuine: percentage with
   justification
2. **Most likely error source**, if one was found, with estimated F1
   impact
3. **Weakest link** — the layer where an undetected error is most
   plausible, even if no error was confirmed
4. **Recommendations** — specific additional checks that would increase
   confidence, if any checks remain BLOCKED
