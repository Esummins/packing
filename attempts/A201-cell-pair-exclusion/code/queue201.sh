#!/bin/bash
# A201 two-slot queue: launches run201.sh for one page at a time whenever fewer than 2 A201 page processes run (and the
# lab ceiling holds).   bash queue201.sh <wall> <budget> <pages...>
cd "$(dirname "$0")/../../.." || exit 1
WALL=${1:-1200}; BUDGET=${2:-300}; shift 2
mine() { powershell -NoProfile -Command "(Get-CimInstance Win32_Process -Filter 'Name=\"python.exe\"' | Where-Object { \$_.CommandLine -match 'run201.py' -and \$_.CommandLine -notmatch 'Claude Extensions' } | Measure-Object).Count" | tr -d '\r '; }
for P in "$@"; do
  while [ "$(mine)" -ge 2 ]; do sleep 60; done
  echo "$(date +%H:%M:%S) queue -> $P"
  nohup bash attempts/A201-cell-pair-exclusion/code/run201.sh $WALL $BUDGET $P >> attempts/A201-cell-pair-exclusion/logs/launch_queue.log 2>&1 &
  sleep 90
done
echo "$(date +%H:%M:%S) queue drained"
