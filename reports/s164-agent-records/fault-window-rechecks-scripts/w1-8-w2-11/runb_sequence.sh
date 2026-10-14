#!/usr/bin/env bash
# =============================================================================
# W1-8 fault-window re-check (2026-10-14): every zero-API Run B step, in order.
#
# Serialised in ONE replay worktree (each step checks out its generating
# commit; nothing runs concurrently, so one CPU at a time):
#   1. per arm: union, extract, provenance, coverage, metas
#      (runb_stage2_rebuild.sh, at the commits the build/coverage records name)
#   2. per verifier leg: probabilities + meta usage/cost re-derived from the
#      committed batch_results.jsonl (reparse_verifier_leg.py, at the leg
#      meta's git_commit)
#   3. per repaired copy: modality_bridge_stage2_checks.py repair, at the
#      commit that added the copy, with the copy removed from the working
#      tree first and restored afterwards
#   4. g37-image Stage 1: the five chunked passes re-merged (remerge_chunks.py)
#   5. validate-chain (modality_bridge_union.py --validate-originals) at its
#      git_head 2cff16c91
#   6. cost audits at 69eb32132: audit_proposer_cost.py per Stage 1 arm and
#      audit_verifier_cost.py over the ten Stage 2 legs, --tier batch
#   7. anchor gate (modality_bridge_anchors.py) at 2b6edde9a
# Zero API: no verify, no lodge, no client; API keys blanked, proxies dead.
# =============================================================================
set -uo pipefail
D=$HOME/scratch/s164-fw-recheck-2026-10-14/wt/reports/s164-agent-records/fault-window-rechecks-scripts/w1-8-w2-11
T=$HOME/scratch/s164-fw-recheck-2026-10-14/w1-8-w2-11-92b151058
R=$HOME/scratch/s164-fw-recheck-2026-10-14/wt
O=$HOME/scratch/s164-fw-recheck-2026-10-14/w1-8-w2-11-out/runb
PY=$HOME/Code/map-reader-llm/.venv/bin/python
OUTD=outputs/modality-bridge-2026-10-07
export GEMINI_API_KEY= GOOGLE_API_KEY= GOOGLE_GENAI_API_KEY=
export HTTPS_PROXY=http://127.0.0.1:9 HTTP_PROXY=http://127.0.0.1:9
export https_proxy=http://127.0.0.1:9 http_proxy=http://127.0.0.1:9 NO_PROXY= no_proxy=
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
step() { echo "=== $(date -Is) $*"; }
co() {  # check out a commit in the replay tree, refusing tracked changes
  if [ -n "$(git -C "$T" status --porcelain --untracked-files=no)" ]; then
    echo "REFUSED: tracked changes in replay tree"; git -C "$T" status --short | head; exit 1
  fi
  git -C "$T" checkout -q --detach "$1" && echo "HEAD $(git -C "$T" rev-parse --short=9 HEAD)"
}
ver() { case $1 in *image*) echo detect_brief-text-image ;; *) echo detect_brief-text ;; esac; }

# 1. arms ---------------------------------------------------------------------
for spec in g3-image:92b151058:fd07fd61b g3-text-temp1:92b151058:fd07fd61b \
            g3-image-temp1:92b151058:fd07fd61b g37-text:2718be084:2718be084 \
            g37-image-cache:60aceebdd:a3ea389c2 g37-image:987718a66:987718a66; do
  IFS=: read -r arm uc cc <<< "$spec"
  step "ARM $arm union@$uc check@$cc"
  bash "$D/runb_stage2_rebuild.sh" "$arm" "$uc" "$cc" || { echo "ARM $arm FAILED"; exit 1; }
done

# 2. re-parse legs ------------------------------------------------------------
# leg spec: arm:verifier:code_commit:added_commit
for spec in g3-text:g3:fd07fd61b:2b6edde9a g3-image:g3:fd07fd61b:2b6edde9a \
            g3-text-temp1:g3:fd07fd61b:2b6edde9a g3-image-temp1:g3:fd07fd61b:2b6edde9a \
            g37-text:g3:2718be084:a3ea389c2 g37-text:g37:2718be084:a3ea389c2 \
            g37-image-cache:g3:60aceebdd:94be8b01a g37-image-cache:g37:a3ea389c2:94be8b01a \
            g37-image:g3:987718a66:69eb32132 g37-image:g37:987718a66:69eb32132; do
  IFS=: read -r arm v code added <<< "$spec"
  step "REPARSE $arm:$v code@$code added@$added"
  co "$code" || exit 1
  $PY "$D/reparse_verifier_leg.py" --tree "$T" --repo "$R" \
    --leg "$OUTD/$arm/verifier/$(ver "$arm")/verify_$v" --added "$added" \
    --out "$O/reparse/$arm-$v.json"
done

# 3. repairs ------------------------------------------------------------------
for spec in g3-image-temp1:g3:2b6edde9a g37-text:g3:3c155685a g37-text:g37:3c155685a \
            g37-image-cache:g3:94be8b01a g37-image-cache:g37:94be8b01a \
            g37-image:g3:69eb32132 g37-image:g37:69eb32132; do
  IFS=: read -r arm v added <<< "$spec"
  step "REPAIR $arm:$v at@$added"
  co "$added" || exit 1
  leg="$OUTD/$arm/verifier/$(ver "$arm")/verify_$v"
  rm -rf "$T/${leg}_repaired"
  (cd "$T" && $PY scripts/modality_bridge_stage2_checks.py repair "$leg")
  mkdir -p "$O/repair/$arm-$v"
  cp "$T/${leg}_repaired/"* "$O/repair/$arm-$v/"
  rm -rf "$T/${leg}_repaired"
  git -C "$T" checkout -q -- "${leg}_repaired"
done

# 4. g37-image chunk merges -----------------------------------------------------
step "REMERGE g37-image at 987718a66"
co 987718a66 || exit 1
for n in 1 2 3 4 5; do
  $PY "$D/remerge_chunks.py" --tree "$T" --repo "$R" \
    --run-dir "$OUTD/g37-image/detect_brief-text-image/run_$n" \
    --version detect_brief-text-image --run-number "$n" \
    --chunks-commit 987718a66 --merged-commit 987718a66 \
    --scratch "$O/remerge/g37-image/run_$n" --out "$O/remerge/g37-image-run_$n.json"
done

# 5. validate-chain ---------------------------------------------------------------
step "VALIDATE-CHAIN at 2cff16c91"
co 2cff16c91 || exit 1
rm -rf "$O/validate"; mkdir -p "$O/validate"
(cd "$T" && $PY scripts/modality_bridge_union.py --validate-originals "$O/validate/scratch" \
  --json-out "$O/validate/validate-chain.json") > "$O/validate/validate.log" 2>&1
echo "validate rc=$?"
rm -rf "$O/validate/scratch"

# 6. cost audits --------------------------------------------------------------------
step "COST AUDITS at 69eb32132"
co 69eb32132 || exit 1
mkdir -p "$O/audit"
for arm in g3-text g3-image g37-text g37-image g37-image-cache g3-text-temp1 g3-image-temp1; do
  v=$(ver "$arm"); roots=("$OUTD/$arm/$v")
  for rd in "$T/$OUTD/$arm"/recovery_rd*/"$v"; do
    [ -d "$rd" ] && roots+=("${rd#"$T"/}")
  done
  (cd "$T" && $PY scripts/audit_proposer_cost.py "${roots[@]}" --tier batch --json) \
    > "$O/audit/stage1-$arm.json" 2> "$O/audit/stage1-$arm.err"
  echo "stage1 $arm roots=${roots[*]} rc=$?"
done
legs=()
for lv in g3-text:g3 g3-image:g3 g37-text:g3 g37-text:g37 g37-image:g3 g37-image:g37 \
          g37-image-cache:g3 g37-image-cache:g37 g3-text-temp1:g3 g3-image-temp1:g3; do
  IFS=: read -r arm v <<< "$lv"; legs+=("$OUTD/$arm/verifier/$(ver "$arm")/verify_$v")
done
(cd "$T" && $PY scripts/audit_verifier_cost.py "${legs[@]}" --tier batch --json) \
  > "$O/audit/stage2.json" 2> "$O/audit/stage2.err"
echo "stage2 rc=$?"

# 7. anchor gate ----------------------------------------------------------------------
step "ANCHOR GATE at 2b6edde9a"
co 2b6edde9a || exit 1
mkdir -p "$O/anchor"
(cd "$T" && $PY scripts/modality_bridge_anchors.py --json-out "$O/anchor/anchor-gate.json") \
  > "$O/anchor/anchor.log" 2>&1
echo "anchor rc=$?"
co 69eb32132
step "SEQUENCE DONE"
