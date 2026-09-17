#!/usr/bin/env bash
# A249 finisher: waits (detached) for the ladder's last stage (results/pocket249.json), then runs
# summary -> test -> pages -> the Lean audit, one python at a time; logs/STOP aborts.
HERE="$(cd "$(dirname "$0")" && pwd)"; ATT="$(cd "$HERE/.." && pwd)"; ROOT="$(cd "$ATT/../.." && pwd)"
export PYTHONDONTWRITEBYTECODE=1
while [ ! -f "$ATT/results/pocket249.json" ]; do [ -f "$ATT/logs/STOP" ] && exit 0; sleep 60; done
sleep 5
bash "$HERE/run249.sh" summary && bash "$HERE/run249.sh" test && bash "$HERE/run249.sh" pages
cd "$ROOT" && python lean/audit.py > "$ATT/logs/audit249.log" 2>&1; echo "audit exit $?" >> "$ATT/logs/audit249.log"
echo FINISHED
