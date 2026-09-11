#!/bin/bash
# A204 launcher: the polygon-clip cascade to a fixed point (g1 pad, then pad 0 if ALIVE) over A203's g1-alive survivors, one
# shard; the lab ceiling (12 pythons excluding "Claude Extensions" command lines) counted and WAITED on before every page;
# CURRENT.json refreshed and a git commit (explicit pathspecs) after every page.      bash run204.sh <shard> <nshard> [pages...]
cd "$(dirname "$0")/../../.." || exit 1
ATT=attempts/A204-polyclip-cascade; RES=$ATT/results/polyclip204.jsonl; PAGES_DIR=docs/residue_map/campaigns/A204-polyclip
SHARD=${1:-0}; NSHARD=${2:-1}; shift 2 2>/dev/null
export PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
if [ $# -gt 0 ]; then PAGES="$@"; else PAGES=$(tr -d '\r' < $ATT/survivors_from_A203.txt); fi
labcount() { powershell -NoProfile -Command "Get-CimInstance Win32_Process -Filter 'Name=\"python.exe\"' | Where-Object { \$_.CommandLine -notmatch 'Claude Extensions' } | Measure-Object | Select-Object -ExpandProperty Count" | tr -d '\r '; }
k=0
for P in $PAGES; do
  k=$((k+1)); if [ $(( (k-1) % NSHARD )) -ne "$SHARD" ]; then continue; fi
  if grep "\"nid\": \"$P\"" $RES 2>/dev/null | grep -q '"pad": "zero"' || grep "\"nid\": \"$P\"" $RES 2>/dev/null | grep -q '"verdict": "DEAD"'; then echo "skip $P (done)"; continue; fi
  while [ "$(labcount)" -ge 12 ]; do sleep 60; done
  LOG=$ATT/logs/polyclip204_${P}.log
  T0=$(date +%s); echo "$(date +%H:%M:%S) start $P"
  timeout -s KILL 2100 python $ATT/code/run204.py $P --wall 900 >> $LOG 2>&1
  RC=$?
  if [ $RC -eq 137 ]; then echo "{\"nid\": \"$P\", \"verdict\": \"ALIVE\", \"pad\": \"-\", \"leaf\": \"process wall 2100 s reached (killed): undecided\", \"seconds\": $(( $(date +%s) - T0 )), \"killed\": true, \"when\": \"$(date '+%Y-%m-%d %H:%M:%S')\"}" >> $RES; fi
  python docs/residue_map/refresh_current.py > /dev/null 2>&1
  V=$(grep "\"nid\": \"$P\"" $RES | grep -o '"verdict": "[A-Z]*"\|"pad": "[a-z0-9]*"' | tr '\n' ' ')
  for i in 1 2 3 4 5 6; do
    git add -- $RES $ATT/certs $ATT/logs $PAGES_DIR docs/residue_map/current 2>/dev/null
    if git commit -q -m "A204: $P [$V] $(( $(date +%s) - T0 ))s" -- $RES $ATT/certs $ATT/logs $PAGES_DIR docs/residue_map/current 2>/dev/null; then break; fi
    sleep $((5*i))
  done
  echo "$(date +%H:%M:%S) $P $V rc=$RC $(( $(date +%s) - T0 ))s"
done
