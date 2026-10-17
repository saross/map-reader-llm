#!/usr/bin/env bash
# Worker-cap guard for the 2026-10-15 re-checks (cap: 8 worker processes in
# all). Every 5 s it counts the Pool workers of the two sweep replays plus
# any Python process running in a w2-3* replay tree; if that count plus the
# short-step driver's one process would exceed 8, it pauses (SIGSTOP) the
# short-step driver's Python child, and resumes it (SIGCONT) once there is
# room. Pausing a process cannot change its output. Exits when the short-step
# driver ends; every pause and resume is logged.
# Usage: cap_guard.sh <sweep 1 pid file> <sweep 2 pid file> <cells pid file>
set -u
S1=$(cat "$1"); S2=$(cat "$2"); CE=$(cat "$3")
pool() { local m; m=$(pgrep -P "$1" -f final_board_sweeps | head -1)
         [ -n "$m" ] && pgrep -P "$m" | wc -l || echo 0; }
others() { local n=0 p c
           for p in $(pgrep -u "$USER" python); do
             c=$(readlink "/proc/$p/cwd" 2>/dev/null)
             case $c in */s164-fw-recheck2-2026-10-15/w2-3*) n=$((n + 1)) ;; esac
           done; echo $n; }
while kill -0 "$CE" 2>/dev/null; do
  child=$(pgrep -P "$CE" | head -1)
  if [ -n "$child" ]; then
    busy=$(( $(pool "$S1") + $(pool "$S2") + $(others) ))
    st=$(ps -o stat= -p "$child" | cut -c1)
    if [ $((busy + 1)) -gt 8 ] && [ "$st" != "T" ]; then
      kill -STOP "$child"; echo "$(date -u +%FT%TZ) paused $child (others busy: $busy)"
    elif [ $((busy + 1)) -le 8 ] && [ "$st" = "T" ]; then
      kill -CONT "$child"; echo "$(date -u +%FT%TZ) resumed $child (others busy: $busy)"
    fi
  fi
  sleep 5
done
echo "$(date -u +%FT%TZ) short-step driver ended; guard exits"
