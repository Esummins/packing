#!/bin/bash
# A201 launcher: the quick chain with the cell-pair table over a list of pages, each page under `timeout -s KILL`, the
# lab ceiling (12 pythons excluding "Claude Extensions") counted and WAITED on before every page, a commit per verdict.
#   bash run201.sh <wall> <budget> <pages...>
cd "$(dirname "$0")/../../.." || exit 1
ATT=attempts/A201-cell-pair-exclusion; RES=$ATT/results/pairexcl201.jsonl
WALL=${1:-600}; BUDGET=${2:-60}; shift 2
export PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
labcount() { powershell -NoProfile -Command "Get-CimInstance Win32_Process -Filter 'Name=\"python.exe\"' | Where-Object { \$_.CommandLine -notmatch 'Claude Extensions' } | Measure-Object | Select-Object -ExpandProperty Count" | tr -d '\r '; }
mkdir -p $ATT/logs $ATT/certs $ATT/results
for P in "$@"; do
  while [ "$(labcount)" -ge 12 ]; do sleep 60; done
  LOG=$ATT/logs/pe201_${P}.log; TMO=$((2*WALL+300)); T0=$(date +%s)
  echo "$(date +%H:%M:%S) start $P"
  timeout -s KILL $TMO python $ATT/code/run201.py $P --wall $WALL --chain --budget $BUDGET >> $LOG 2>&1
  RC=$?
  if [ $RC -eq 137 ]; then echo "{\"nid\": \"$P\", \"verdict\": \"ALIVE\", \"pad\": \"-\", \"leaf\": \"wall ${TMO}s reached (process killed): undecided\", \"seconds\": $(( $(date +%s) - T0 )), \"killed\": true, \"when\": \"$(date '+%Y-%m-%d %H:%M:%S')\"}" >> $RES; fi
  V=$(grep "\"nid\": \"$P\"" $RES | tail -1 | grep -o '"verdict": "[A-Z]*"' | head -1)
  SVG=docs/residue_map/pairexcl201_${P}.svg; [ -f "$SVG" ] || SVG=""
  for i in 1 2 3 4 5 6; do
    git add -- $RES $ATT/certs $ATT/logs $SVG 2>/dev/null
    if git commit -q -m "A201: $P $V $(( $(date +%s) - T0 ))s (cell-pair table)" -- $RES $ATT/certs $ATT/logs $SVG 2>/dev/null; then break; fi
    sleep $((5*i))
  done
  echo "$(date +%H:%M:%S) $P $V rc=$RC $(( $(date +%s) - T0 ))s"
done
