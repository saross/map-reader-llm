#!/usr/bin/env bash
# Pre-flight compute-host load check (backstop).
# ==============================================
# Reports 1-minute load, physical cores, and free-core headroom for each
# compute host, and names the freest. Run BEFORE launching any compute-
# intensive job so we never pile onto a host another session is using.
#
# Rule of thumb: treat a host as unavailable for heavy compute when
# (physical_cores - load1) < 2. amd-tower (local) is never a compute target.
#
# Usage:  bash scripts/check-compute-hosts.sh
set -uo pipefail

HOSTS=("sapphire" "zbook")
PROBE='phys=$(lscpu | awk -F: "/^Socket\(s\)/{s=\$2} /Core\(s\) per socket/{c=\$2} END{print s*c}"); load1=$(cut -d" " -f1 /proc/loadavg); echo "$load1 $phys"'

best_host=""; best_free=-999
printf "%-10s %8s %8s %8s   %s\n" "host" "load1" "cores" "free" "status"
for h in "${HOSTS[@]}"; do
    out=$(timeout 12 ssh -o ConnectTimeout=6 -o BatchMode=yes "$h" "$PROBE" 2>/dev/null)
    if [[ -z "$out" ]]; then
        printf "%-10s %8s %8s %8s   %s\n" "$h" "-" "-" "-" "UNREACHABLE"
        continue
    fi
    load1=$(echo "$out" | awk '{print $1}')
    cores=$(echo "$out" | awk '{print $2}')
    free=$(awk -v c="$cores" -v l="$load1" 'BEGIN{printf "%d", c - l}')
    if (( free < 2 )); then status="BUSY (avoid heavy compute)"; else status="available"; fi
    printf "%-10s %8s %8s %8d   %s\n" "$h" "$load1" "$cores" "$free" "$status"
    if (( free > best_free )); then best_free="$free"; best_host="$h"; fi
done

echo
if [[ -n "$best_host" && "$best_free" -ge 2 ]]; then
    echo "→ freest host: $best_host (~$best_free free cores). Cap workers at (cores - 2)."
else
    echo "→ NO host has >=2 free cores — defer heavy compute or ask the operator."
fi
