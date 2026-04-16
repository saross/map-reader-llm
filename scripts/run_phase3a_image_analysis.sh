#!/bin/bash
# Phase 3a Image Track: Comprehensive Consensus Analysis
# ========================================================
#
# Overnight analysis run on sapphire. Builds consensus GeoJSONs,
# evaluates at all thresholds and buffers, produces summary tables.
#
# Full 2×4 matrix (HIGH/MINIMAL × T=0.0/0.3/0.7/1.0):
#   - N=10 full sweep (t=1..10) for K=10 conditions
#   - N=5 sweep (runs 1-5 only, t=1..5) for K=10 conditions
#   - N=3 sweep (t=1..3) for K=3 baseline conditions (T=0.0)
#   - Evaluation at 20/30/40/50m buffers with 1000-iteration bootstrap CIs
#
# Usage:
#   nohup bash scripts/run_phase3a_image_analysis.sh > /tmp/phase3a-analysis.log 2>&1 &

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO_ROOT"

PYTHON=".venv/bin/python"
MERGE="scripts/merge_passes.py"
EVAL="scripts/evaluate_detections.py"

# Evaluation parameters
BOUNDS="inputs/vectors/bounds/384/full_evaluation_bounds.geojson"
GT="inputs/vectors/references/mounds-reference.geojson"
BUFFERS="20 30 40 50"
BOOTSTRAP=1000
SEED=42

# Output roots
HIGH_ROOT="outputs/h11/pv-diag-384/flash-high-image-n5"
MINIMAL_ROOT="outputs/h11/pv-diag-384/image-n5"
RESULTS_DIR="results/phase3a-image-matrix"

export PYTHONUNBUFFERED=1

echo "Phase 3a Image Track: Comprehensive Consensus Analysis"
echo "Started: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
echo ""

# ===================================================================
# STEP 1: Build consensus (N=10 full sweep) for all conditions
# ===================================================================
echo "================================================================"
echo "  STEP 1: Build N=10 consensus (full sweep)"
echo "================================================================"

build_consensus() {
    local input_dir="$1"
    local output_dir="$2"
    local label="$3"
    local passes="$4"  # empty = all, or "1,2,3,4,5"

    if [ -f "$output_dir/voting_summary.json" ]; then
        echo "  [$label] Already exists — skipping"
        return 0
    fi

    echo "  [$label] Building consensus..."
    local pass_flag=""
    if [ -n "$passes" ]; then
        pass_flag="--passes $passes"
    fi

    $PYTHON $MERGE \
        --input-dir "$input_dir" \
        --output-dir "$output_dir" \
        --sweep $pass_flag

    echo "  [$label] Done"
}

# HIGH thinking — N=10 (all runs)
for temp in t0.0 t0.3 t0.7 t1.0; do
    input="$HIGH_ROOT/image-${temp}"
    output="$HIGH_ROOT/image-${temp}/consensus"
    build_consensus "$input" "$output" "HIGH ${temp} N=10" ""
done

# MINIMAL thinking — N=10 (all runs)
for temp in t0.3 t0.7 t1.0; do
    input="$MINIMAL_ROOT/image-${temp}"
    output="$MINIMAL_ROOT/image-${temp}/consensus"
    build_consensus "$input" "$output" "MINIMAL ${temp} N=10" ""
done

# MINIMAL T=0.0 (already exists in n1-outstanding)
build_consensus \
    "outputs/h11/n1-outstanding-384/image-t0" \
    "outputs/h11/n1-outstanding-384/image-t0/consensus" \
    "MINIMAL t0.0 N=3 (n1)" ""

echo ""

# ===================================================================
# STEP 2: Build consensus (N=5 sweep, runs 1-5 only)
# ===================================================================
echo "================================================================"
echo "  STEP 2: Build N=5 consensus (runs 1-5)"
echo "================================================================"

# HIGH thinking — N=5
for temp in t0.3 t0.7 t1.0; do
    input="$HIGH_ROOT/image-${temp}"
    output="$HIGH_ROOT/image-${temp}/consensus-n5"
    build_consensus "$input" "$output" "HIGH ${temp} N=5" "1,2,3,4,5"
done

# MINIMAL thinking — N=5
for temp in t0.3 t0.7 t1.0; do
    input="$MINIMAL_ROOT/image-${temp}"
    output="$MINIMAL_ROOT/image-${temp}/consensus-n5"
    build_consensus "$input" "$output" "MINIMAL ${temp} N=5" "1,2,3,4,5"
done

echo ""

# ===================================================================
# STEP 3: Evaluate ALL consensus GeoJSONs at all buffers
# ===================================================================
echo "================================================================"
echo "  STEP 3: Evaluate all consensus thresholds"
echo "================================================================"

mkdir -p "$RESULTS_DIR"

evaluate_condition() {
    local geojson="$1"
    local label="$2"
    local output_dir="$3"

    # Each threshold gets its own subdirectory to avoid overwriting
    local slug
    slug=$(echo "$label" | tr '[:upper:]' '[:lower:]' | sed 's/[^a-z0-9]/-/g' | sed 's/^-//;s/-$//')
    local cond_dir="$output_dir/$slug"

    if [ -f "$cond_dir/evaluation.json" ]; then
        echo "    [$label] Cached — skipping"
        return 0
    fi

    echo "    [$label] Evaluating..."
    mkdir -p "$cond_dir"
    $PYTHON $EVAL \
        --detections "$geojson" \
        --buffers $BUFFERS \
        --bootstrap $BOOTSTRAP \
        --seed $SEED \
        --bounds "$BOUNDS" \
        --ground-truth "$GT" \
        --output-dir "$cond_dir" \
        --label "$label" 2>/dev/null

    echo "    [$label] Done"
}

# Evaluate N=10 sweeps (HIGH)
for temp in t0.0 t0.3 t0.7 t1.0; do
    consensus_dir="$HIGH_ROOT/image-${temp}/consensus"
    eval_dir="$RESULTS_DIR/high-${temp}/n10"
    mkdir -p "$eval_dir"
    echo "  HIGH ${temp} N=10:"
    for gj in "$consensus_dir"/consensus_t*.geojson; do
        [ -f "$gj" ] || continue
        t_val=$(basename "$gj" | sed 's/consensus_t\([0-9]*\).geojson/\1/')
        evaluate_condition "$gj" "HIGH-${temp}-${t_val}of10" "$eval_dir"
    done
done

# Evaluate N=10 sweeps (MINIMAL)
for temp in t0.3 t0.7 t1.0; do
    consensus_dir="$MINIMAL_ROOT/image-${temp}/consensus"
    eval_dir="$RESULTS_DIR/minimal-${temp}/n10"
    mkdir -p "$eval_dir"
    echo "  MINIMAL ${temp} N=10:"
    for gj in "$consensus_dir"/consensus_t*.geojson; do
        [ -f "$gj" ] || continue
        t_val=$(basename "$gj" | sed 's/consensus_t\([0-9]*\).geojson/\1/')
        evaluate_condition "$gj" "MINIMAL-${temp}-${t_val}of10" "$eval_dir"
    done
done

# Evaluate MINIMAL T=0.0 (K=3, in n1-outstanding)
eval_dir="$RESULTS_DIR/minimal-t0.0/n3"
mkdir -p "$eval_dir"
echo "  MINIMAL t0.0 N=3:"
for gj in outputs/h11/n1-outstanding-384/image-t0/consensus/consensus_t*.geojson; do
    [ -f "$gj" ] || continue
    t_val=$(basename "$gj" | sed 's/consensus_t\([0-9]*\).geojson/\1/')
    evaluate_condition "$gj" "MINIMAL-t0.0-${t_val}of3" "$eval_dir"
done

# Evaluate N=5 sweeps (HIGH)
for temp in t0.3 t0.7 t1.0; do
    consensus_dir="$HIGH_ROOT/image-${temp}/consensus-n5"
    eval_dir="$RESULTS_DIR/high-${temp}/n5"
    mkdir -p "$eval_dir"
    echo "  HIGH ${temp} N=5:"
    for gj in "$consensus_dir"/consensus_t*.geojson; do
        [ -f "$gj" ] || continue
        t_val=$(basename "$gj" | sed 's/consensus_t\([0-9]*\).geojson/\1/')
        evaluate_condition "$gj" "HIGH-${temp}-${t_val}of5" "$eval_dir"
    done
done

# Evaluate N=5 sweeps (MINIMAL)
for temp in t0.3 t0.7 t1.0; do
    consensus_dir="$MINIMAL_ROOT/image-${temp}/consensus-n5"
    eval_dir="$RESULTS_DIR/minimal-${temp}/n5"
    mkdir -p "$eval_dir"
    echo "  MINIMAL ${temp} N=5:"
    for gj in "$consensus_dir"/consensus_t*.geojson; do
        [ -f "$gj" ] || continue
        t_val=$(basename "$gj" | sed 's/consensus_t\([0-9]*\).geojson/\1/')
        evaluate_condition "$gj" "MINIMAL-${temp}-${t_val}of5" "$eval_dir"
    done
done

echo ""

# ===================================================================
# STEP 4: Build comprehensive summary
# ===================================================================
echo "================================================================"
echo "  STEP 4: Build summary tables"
echo "================================================================"

$PYTHON - "$RESULTS_DIR" <<'PYEOF'
"""Compile Phase 3a image matrix evaluation results into summary tables."""

import json
import sys
from pathlib import Path

results_dir = Path(sys.argv[1])


def load_eval(eval_dir: Path) -> list[dict]:
    """Load all evaluation JSONs from a directory."""
    results = []
    for f in sorted(eval_dir.glob("*.json")):
        if f.name.startswith("batch_") or f.name == "evaluation.json":
            # evaluate_detections writes evaluation.json
            try:
                with open(f) as fh:
                    data = json.load(fh)
                # Handle both formats: direct summary or wrapped
                summary = data.get("summary", data)
                if "buffers" in summary:
                    results.append(summary)
            except (json.JSONDecodeError, KeyError):
                pass
    return results


def extract_best(evals: list[dict], buffer_m: int) -> dict | None:
    """Find the evaluation with the best F1 at the given buffer."""
    best = None
    best_f1 = -1
    for ev in evals:
        for buf in ev.get("buffers", []):
            if buf.get("buffer_metres") == buffer_m and buf.get("f1", 0) > best_f1:
                best_f1 = buf["f1"]
                best = {"label": ev.get("label", ""), **buf}
                break
    return best


# Collect all results
matrix = {}
for thinking_dir in sorted(results_dir.iterdir()):
    if not thinking_dir.is_dir():
        continue
    for pool_dir in sorted(thinking_dir.iterdir()):
        if not pool_dir.is_dir():
            continue
        evals = load_eval(pool_dir)
        if evals:
            key = f"{thinking_dir.name}/{pool_dir.name}"
            matrix[key] = evals

# Write comprehensive JSON
all_results = {}
for key, evals in matrix.items():
    all_results[key] = []
    for ev in evals:
        entry = {"label": ev.get("label", "")}
        for buf in ev.get("buffers", []):
            bm = buf.get("buffer_metres", 0)
            entry[f"f1_{bm}m"] = buf.get("f1", 0)
            entry[f"f1_ci_lo_{bm}m"] = buf.get("f1_ci_lower", 0)
            entry[f"f1_ci_hi_{bm}m"] = buf.get("f1_ci_upper", 0)
            entry[f"p_{bm}m"] = buf.get("precision", 0)
            entry[f"r_{bm}m"] = buf.get("recall", 0)
        all_results[key].append(entry)

with open(results_dir / "all-evaluations.json", "w") as f:
    json.dump(all_results, f, indent=2)

# Build summary markdown: best F1 per (thinking, temp, pool_size) at 20m
lines = []
lines.append("# Phase 3a Image Track: Consensus Analysis Summary")
lines.append("")
lines.append("## Best operating point per condition (20m buffer)")
lines.append("")
lines.append(
    "| Thinking | T | N | Best t | "
    "F1 | 95% CI | P | R |"
)
lines.append(
    "|----------|---:|--:|-------:|"
    "---:|:------:|---:|---:|"
)

for key in sorted(matrix.keys()):
    evals = matrix[key]
    best = extract_best(evals, 20)
    if best:
        # Parse key: "high-t0.3/n10" or "minimal-t0.7/n5"
        parts = key.split("/")
        thinking_temp = parts[0]  # e.g., "high-t0.3"
        pool = parts[1] if len(parts) > 1 else "?"  # e.g., "n10"

        thinking = thinking_temp.split("-")[0].upper()
        temp = thinking_temp.split("-", 1)[1] if "-" in thinking_temp else "?"

        # Extract threshold from label (e.g., "HIGH-t0.3-4of10" → 4)
        label = best.get("label", "")
        t_str = "?"
        if "of" in label:
            import re
            m = re.search(r"-(\d+)of", label)
            if m:
                t_str = m.group(1)

        f1 = best.get("f1", 0)
        ci_lo = best.get("f1_ci_lower", 0)
        ci_hi = best.get("f1_ci_upper", 0)
        p = best.get("precision", 0)
        r = best.get("recall", 0)

        lines.append(
            f"| {thinking} | {temp} | {pool} | {t_str} | "
            f"{f1:.3f} | [{ci_lo:.3f}, {ci_hi:.3f}] | "
            f"{p:.3f} | {r:.3f} |"
        )

lines.append("")

# HIGH vs MINIMAL comparison at 20m
lines.append("## HIGH vs MINIMAL comparison (20m, best operating point per N)")
lines.append("")
lines.append(
    "| T | N | HIGH F1 | HIGH CI | MIN F1 | MIN CI | Δ F1 |"
)
lines.append(
    "|---:|--:|--------:|:-------:|-------:|:------:|-----:|"
)

for temp in ["t0.3", "t0.7", "t1.0"]:
    for pool in ["n5", "n10"]:
        high_key = f"high-{temp}/{pool}"
        min_key = f"minimal-{temp}/{pool}"
        high_best = extract_best(matrix.get(high_key, []), 20)
        min_best = extract_best(matrix.get(min_key, []), 20)
        if high_best and min_best:
            hf1 = high_best.get("f1", 0)
            hci = f"[{high_best.get('f1_ci_lower', 0):.3f}, {high_best.get('f1_ci_upper', 0):.3f}]"
            mf1 = min_best.get("f1", 0)
            mci = f"[{min_best.get('f1_ci_lower', 0):.3f}, {min_best.get('f1_ci_upper', 0):.3f}]"
            delta = hf1 - mf1
            lines.append(
                f"| {temp} | {pool} | {hf1:.3f} | {hci} | "
                f"{mf1:.3f} | {mci} | {delta:+.3f} |"
            )

lines.append("")

# Full threshold sweep tables at 20m
lines.append("## Full threshold sweep (20m buffer)")
lines.append("")

for key in sorted(matrix.keys()):
    evals = matrix[key]
    lines.append(f"### {key}")
    lines.append("")
    lines.append("| t | F1 | 95% CI | P | R |")
    lines.append("|--:|---:|:------:|---:|---:|")
    for ev in evals:
        label = ev.get("label", "")
        for buf in ev.get("buffers", []):
            if buf.get("buffer_metres") == 20:
                f1 = buf.get("f1", 0)
                ci_lo = buf.get("f1_ci_lower", 0)
                ci_hi = buf.get("f1_ci_upper", 0)
                p = buf.get("precision", 0)
                r = buf.get("recall", 0)
                # Extract t from label
                t_str = label.rsplit("-", 1)[-1].split("of")[0] if "of" in label else "?"
                lines.append(
                    f"| {t_str} | {f1:.3f} | "
                    f"[{ci_lo:.3f}, {ci_hi:.3f}] | {p:.3f} | {r:.3f} |"
                )
    lines.append("")

# Multi-buffer summary (best operating point per condition at each buffer)
lines.append("## Buffer sensitivity (best F1 per condition)")
lines.append("")
lines.append("| Condition | 20m | 30m | 40m | 50m |")
lines.append("|-----------|----:|----:|----:|----:|")

for key in sorted(matrix.keys()):
    evals = matrix[key]
    vals = []
    for bm in [20, 30, 40, 50]:
        best = extract_best(evals, bm)
        vals.append(f"{best['f1']:.3f}" if best else "—")
    lines.append(f"| {key} | {' | '.join(vals)} |")

lines.append("")
lines.append(
    f"*Generated: {__import__('datetime').datetime.now(__import__('datetime').timezone.utc).isoformat()}*"
)

with open(results_dir / "consensus-analysis-summary.md", "w") as f:
    f.write("\n".join(lines))

print(f"Summary written to {results_dir / 'consensus-analysis-summary.md'}")
print(f"All evaluations: {results_dir / 'all-evaluations.json'}")
print(f"Conditions analysed: {len(matrix)}")
total_evals = sum(len(v) for v in matrix.values())
print(f"Total evaluations: {total_evals}")
PYEOF

echo ""
echo "================================================================"
echo "  ALL STEPS COMPLETE"
echo "  Finished: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
echo "================================================================"
