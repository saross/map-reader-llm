#!/bin/bash
# Background cross-hypothesis library-design analysis for H12 v2.
# Runs:
#   A) 3 WBF internal H12 pairwise permutation tests
#   B) All-vs-all pairwise permutation tests across the combined
#      H8 v2 + H12 v2 condition set (10 conditions, 45 pairs) at
#      greedy t=4
# Then applies BH-FDR correction at q=0.05 over each family.

set -e
cd ~/Code/map-reader-llm

PYTHON=.venv/bin/python
SCRIPT=scripts/pairwise_permutation_test.py
REF=inputs/vectors/references/mounds-reference.geojson
BOUNDS=inputs/vectors/bounds/384/h10_test_bounds.geojson

H8_CONDS=(pure-positive-canon canonical plus-hp scale-4 scale-8 scale-16 scale-32)
H12_CONDS=(r1-hn-heavy r2-balanced r3-hp-heavy)

# Map condition name -> greedy consensus file path
greedy_path() {
  local cond=$1
  case $cond in
    pure-positive-canon|canonical|plus-hp|scale-4|scale-8|scale-16|scale-32)
      echo "outputs/h8-v2/greedy/$cond/consensus_t4.geojson"
      ;;
    r1-hn-heavy|r2-balanced|r3-hp-heavy)
      echo "outputs/h12-v2/greedy/$cond/consensus_t4.geojson"
      ;;
  esac
}

wbf_path() {
  echo "outputs/h12-v2/wbf/$1/wbf_candidates.geojson"
}

LOG=/tmp/h12-cross-analysis.log
: > "$LOG"

# ---------- Part A: WBF internal H12 pairs ----------
echo "=== Part A: H12 WBF internal pairs ===" | tee -a "$LOG"
mkdir -p results/h12-v2/permutation-wbf
WBF_PAIRS=(
  "R12:r1-hn-heavy:r2-balanced"
  "R23:r2-balanced:r3-hp-heavy"
  "R13:r1-hn-heavy:r3-hp-heavy"
)
for spec in "${WBF_PAIRS[@]}"; do
  code=${spec%%:*}
  rest=${spec#*:}
  a=${rest%%:*}
  b=${rest#*:}
  out="results/h12-v2/permutation-wbf/${code}-${a}-vs-${b}"
  mkdir -p "$out"
  echo ">>> WBF $code: $a vs $b" | tee -a "$LOG"
  $PYTHON $SCRIPT \
    --mode geojson \
    --geojson-a "$(wbf_path $a)" \
    --geojson-b "$(wbf_path $b)" \
    --label-a "$a-wbf" \
    --label-b "$b-wbf" \
    --ground-truth "$REF" \
    --bounds "$BOUNDS" \
    --buffer-metres 20 \
    --n-permutations 10000 \
    --seed 42 \
    --output-dir "$out" >> "$LOG" 2>&1
done

# ---------- Part B: Cross-hypothesis all-vs-all at greedy t=4 ----------
echo "" | tee -a "$LOG"
echo "=== Part B: Cross-hypothesis all-vs-all (10 conditions, 45 pairs) ===" | tee -a "$LOG"
mkdir -p results/cross-hypothesis-library/permutation-t4
ALL_CONDS=("${H8_CONDS[@]}" "${H12_CONDS[@]}")
N=${#ALL_CONDS[@]}
pair_count=0
for ((i=0; i<N; i++)); do
  for ((j=i+1; j<N; j++)); do
    a=${ALL_CONDS[i]}
    b=${ALL_CONDS[j]}
    pair_count=$((pair_count+1))
    out="results/cross-hypothesis-library/permutation-t4/${a}-vs-${b}"
    mkdir -p "$out"
    echo ">>> cross[$pair_count]: $a vs $b" | tee -a "$LOG"
    $PYTHON $SCRIPT \
      --mode geojson \
      --geojson-a "$(greedy_path $a)" \
      --geojson-b "$(greedy_path $b)" \
      --label-a "$a" \
      --label-b "$b" \
      --ground-truth "$REF" \
      --bounds "$BOUNDS" \
      --buffer-metres 20 \
      --n-permutations 10000 \
      --seed 42 \
      --output-dir "$out" >> "$LOG" 2>&1
  done
done
echo "Total pairs run: $pair_count" | tee -a "$LOG"

# ---------- Part C: BH-FDR summaries ----------
echo "" | tee -a "$LOG"
echo "=== Part C: BH-FDR summaries ===" | tee -a "$LOG"

# C1: WBF H12 family (3 tests)
$PYTHON - <<'PY' | tee -a "$LOG"
import json, pathlib
base = pathlib.Path("results/h12-v2/permutation-wbf")
contrasts = [
    ("R12", "r1-hn-heavy", "r2-balanced"),
    ("R23", "r2-balanced", "r3-hp-heavy"),
    ("R13", "r1-hn-heavy", "r3-hp-heavy"),
]
rows = []
for code, a, b in contrasts:
    p = base / f"{code}-{a}-vs-{b}" / "pairwise_permutation_result.json"
    if not p.exists():
        rows.append({"code": code, "a": a, "b": b, "p": None})
        continue
    d = json.load(open(p))
    rows.append({
        "code": code, "a": a, "b": b,
        "f1_a": d["condition_a"]["f1"],
        "f1_b": d["condition_b"]["f1"],
        "delta": d["permutation_test"]["observed_f1_diff"],
        "p": d["permutation_test"]["p_value"],
        "wins_a": d["permutation_test"]["wins_a"],
        "losses_a": d["permutation_test"]["losses_a"],
        "ties": d["permutation_test"]["ties"],
    })
m = sum(1 for r in rows if r.get("p") is not None)
ranked = sorted([r for r in rows if r.get("p") is not None], key=lambda r: r["p"])
for k, r in enumerate(ranked):
    r["bh_adj_p"] = min(r["p"] * m / (k+1), 1.0)
for k in range(len(ranked)-2, -1, -1):
    ranked[k]["bh_adj_p"] = min(ranked[k]["bh_adj_p"], ranked[k+1]["bh_adj_p"])
by_code = {r["code"]: r for r in ranked}

print("\nH12 v2 WBF pairwise (BH-FDR q=0.05 over 3 contrasts)")
print("="*96)
print(f"{'Code':<5}{'Contrast':<34}{'F1 (a -> b)':<22}{'ΔF1':>9}{'raw p':>10}{'BH-adj p':>11}{'signif?':>10}")
print("-"*96)
for row in rows:
    if row.get("p") is None:
        print(f"{row['code']:<5}MISSING")
        continue
    adj = by_code.get(row['code'], {})
    f1s = f"{row['f1_a']:.3f} -> {row['f1_b']:.3f}"
    sig = "YES" if adj.get('bh_adj_p', 1) < 0.05 else "no"
    print(f"{row['code']:<5}{row['a']+' vs '+row['b']:<34}{f1s:<22}{row['delta']:+9.4f}{row['p']:>10.4f}{adj.get('bh_adj_p', 0):>11.4f}{sig:>10}")

out = {"method": "BH-FDR q=0.05 over 3 H12 WBF contrasts", "contrasts": rows,
       "any_significant": any(r.get("bh_adj_p", 1) < 0.05 for r in ranked)}
json.dump(out, open(base / "fdr_summary.json", "w"), indent=2)
print(f"\nWritten: {base}/fdr_summary.json")
PY

# C2: Cross-hypothesis family (45 tests)
$PYTHON - <<'PY' | tee -a "$LOG"
import json, pathlib, itertools
base = pathlib.Path("results/cross-hypothesis-library/permutation-t4")
h8 = ["pure-positive-canon","canonical","plus-hp","scale-4","scale-8","scale-16","scale-32"]
h12 = ["r1-hn-heavy","r2-balanced","r3-hp-heavy"]
all_conds = h8 + h12
rows = []
for a, b in itertools.combinations(all_conds, 2):
    p = base / f"{a}-vs-{b}" / "pairwise_permutation_result.json"
    if not p.exists():
        rows.append({"a": a, "b": b, "p": None})
        continue
    d = json.load(open(p))
    rows.append({
        "a": a, "b": b,
        "f1_a": d["condition_a"]["f1"],
        "f1_b": d["condition_b"]["f1"],
        "delta": d["permutation_test"]["observed_f1_diff"],
        "p": d["permutation_test"]["p_value"],
        "wins_a": d["permutation_test"]["wins_a"],
        "losses_a": d["permutation_test"]["losses_a"],
        "ties": d["permutation_test"]["ties"],
    })
m = sum(1 for r in rows if r.get("p") is not None)
ranked = sorted([r for r in rows if r.get("p") is not None], key=lambda r: r["p"])
for k, r in enumerate(ranked):
    r["bh_adj_p"] = min(r["p"] * m / (k+1), 1.0)
for k in range(len(ranked)-2, -1, -1):
    ranked[k]["bh_adj_p"] = min(ranked[k]["bh_adj_p"], ranked[k+1]["bh_adj_p"])

key = lambda r: (r["a"], r["b"])
by_pair = {key(r): r for r in ranked}

print("\n\nH8 v2 + H12 v2 cross-hypothesis library-design matrix")
print(f"(10 conditions, {m} pairs, BH-FDR q=0.05, greedy t=4, 10,000 permutations, seed 42)")
print("="*120)
print(f"{'a':<22}{'b':<22}{'F1 a':<8}{'F1 b':<8}{'ΔF1':>9}{'raw p':>10}{'BH-adj p':>11}{'signif?':>10}")
print("-"*120)
# Sort by raw p for display
for row in sorted(rows, key=lambda r: r["p"] if r.get("p") is not None else 1):
    if row.get("p") is None:
        print(f"{row['a']:<22}{row['b']:<22}MISSING")
        continue
    adj = by_pair.get((row['a'], row['b']), {})
    sig = "YES" if adj.get('bh_adj_p', 1) < 0.05 else "no"
    print(f"{row['a']:<22}{row['b']:<22}{row['f1_a']:<8.3f}{row['f1_b']:<8.3f}{row['delta']:+9.4f}{row['p']:>10.4f}{adj.get('bh_adj_p', 0):>11.4f}{sig:>10}")

any_sig = any(r.get("bh_adj_p", 1) < 0.05 for r in ranked)
print()
print("="*120)
print("OVERALL:")
if any_sig:
    sigs = [(r['a'], r['b']) for r in ranked if r.get('bh_adj_p', 1) < 0.05]
    print(f"  {len(sigs)} pair(s) significant after BH-FDR q=0.05: {sigs}")
else:
    print("  ZERO pairs significant after BH-FDR correction at q=0.05.")
    print(f"  All {m} pairwise contrasts across H8 v2 + H12 v2 library-design")
    print("  space are null. Library composition, size, and HP:HN ratio produce")
    print("  no detectable F1 differences at the proposer stage under production")
    print("  carry-forward settings.")
print("="*120)

out = {"method": "BH-FDR q=0.05 over cross-hypothesis library-design pairs",
       "n_conditions": len(all_conds), "n_pairs": m,
       "operating_point": "greedy t=4, 20 m buffer, 327-tile h10-384 test set",
       "conditions": all_conds, "contrasts": rows, "any_significant": any_sig}
json.dump(out, open(base / "fdr_summary.json", "w"), indent=2)
print(f"\nWritten: {base}/fdr_summary.json")
PY

echo "" | tee -a "$LOG"
echo "=== Cross-analysis complete at $(date -Iseconds) ===" | tee -a "$LOG"
