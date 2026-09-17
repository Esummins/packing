#!/usr/bin/env bash
# A251 finisher: waits for the ladder's results, then summary + pages + tests + the Lean audit.
# bash attempts/A251-ring-pocket/code/finish251.sh   (detached; logs/finish251.log)
set -e
HERE="$(cd "$(dirname "$0")" && pwd)"
ATT="$(cd "$HERE/.." && pwd)"
ROOT="$(cd "$ATT/../.." && pwd)"
export PYTHONDONTWRITEBYTECODE=1
for i in $(seq 1 2880); do
  [ -f "$ATT/logs/STOP" ] && { echo "STOP present"; break; }
  if grep -q "LADDER DONE" "$ATT/logs/run251.log" 2>/dev/null; then break; fi
  sleep 30
done
bash "$HERE/run251.sh" summary || true
bash "$HERE/run251.sh" pages || true
bash "$HERE/run251.sh" test || true
python "$ROOT/lean/audit.py" > "$ATT/logs/audit251.log" 2>&1 || true
echo "audit exit $?" >> "$ATT/logs/audit251.log"
echo FINISHED
