#!/bin/bash
# A200 launcher (bash so that only the page process counts as a lab python): the quick chain over the k5_16 pages of one
# shard, each page under `timeout -s KILL` (the process is its own tree: no verifier child), the lab ceiling (12 pythons
# excluding "Claude Extensions" command lines) counted and WAITED on before every page, a git commit after every verdict.
#   bash run200.sh <shard> <nshard> [wall] [mode: chain|deep] [pages...]
cd "$(dirname "$0")/../../.." || exit 1
ROOT=$(pwd); ATT=attempts/A200-k516-quick; RES=$ATT/results/quick200.jsonl
SHARD=${1:-0}; NSHARD=${2:-1}; WALL=${3:-900}; MODE=${4:-chain}; shift 4 2>/dev/null
export PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
if [ $# -gt 0 ]; then PAGES="$@"; else PAGES=$(ls docs/shadows/a57v4 | grep -o 'k5_16_interior_Y[0-9]*' | sort -u); fi
labcount() { powershell -NoProfile -Command "Get-CimInstance Win32_Process -Filter 'Name=\"python.exe\"' | Where-Object { \$_.CommandLine -notmatch 'Claude Extensions' } | Measure-Object | Select-Object -ExpandProperty Count" | tr -d '\r '; }
k=0
for P in $PAGES; do
  k=$((k+1)); if [ $(( (k-1) % NSHARD )) -ne "$SHARD" ]; then continue; fi
  LAST=$(grep "\"nid\": \"$P\"" $RES 2>/dev/null | tail -1)
  if [ "$MODE" = fast ] && { echo "$LAST" | grep -q '"verdict": "DEAD"' || echo "$LAST" | grep -q '"pad": "zero"'; }; then echo "skip $P (fast done)"; continue; fi
  if [ "$MODE" = chain ] && { echo "$LAST" | grep -q '"verdict": "DEAD"' || echo "$LAST" | grep -q '"chain_done": true'; }; then echo "skip $P (done)"; continue; fi
  if [ "$MODE" = deep ] && { echo "$LAST" | grep -q '"verdict": "DEAD"' || echo "$LAST" | grep -q '"path": "deep"'; }; then echo "skip $P (done)"; continue; fi
  # a page whose last row is an interim ALIVE row younger than 45 min is IN PROGRESS in another launcher: skip it
  W=$(echo "$LAST" | grep -o '"when": "[^"]*"' | cut -d'"' -f4); if [ -n "$W" ] && [ $(( $(date +%s) - $(date -d "$W" +%s) )) -lt 2700 ]; then echo "skip $P (in progress)"; continue; fi
  while [ "$(labcount)" -ge 12 ]; do sleep 60; done
  # re-check after the gate: another launcher may have taken the page meanwhile
  LAST=$(grep "\"nid\": \"$P\"" $RES 2>/dev/null | tail -1)
  if [ -n "$LAST" ]; then W=$(echo "$LAST" | grep -o '"when": "[^"]*"' | cut -d'"' -f4); if [ -n "$W" ] && [ $(( $(date +%s) - $(date -d "$W" +%s) )) -lt 2700 ]; then echo "skip $P (taken)"; continue; fi; fi
  CERT=$ATT/certs/q200_${P}.json; LOG=$ATT/logs/q200_${P}.log; SVG=docs/residue_map/quick200_${P}.svg
  if [ "$MODE" = deep ]; then CERT=$ATT/certs/q200_${P}_deep.json; LOG=$ATT/logs/q200_${P}_deep.log; ARGS="--deep --noseal --pad g1"; TMO=$((WALL+240)); elif [ "$MODE" = fast ]; then ARGS="--chain --noseal"; TMO=$((2*WALL+120)); else ARGS="--chain"; TMO=$((2*WALL+300)); fi
  T0=$(date +%s); echo "$(date +%H:%M:%S) start $P ($MODE)"
  timeout -s KILL $TMO python $ATT/code/quick200.py $P --wall $WALL $ARGS --cert $CERT --out $RES --svg $SVG >> $LOG 2>&1
  RC=$?
  if [ $RC -eq 137 ]; then echo "{\"nid\": \"$P\", \"verdict\": \"ALIVE\", \"path\": \"$MODE\", \"pad\": \"-\", \"chain_done\": true, \"leaf\": \"wall ${TMO}s reached (process killed): undecided\", \"seconds\": $(( $(date +%s) - T0 )), \"killed\": true, \"when\": \"$(date '+%Y-%m-%d %H:%M:%S')\"}" >> $RES; fi
  V=$(grep "\"nid\": \"$P\"" $RES | tail -1 | grep -o '"verdict": "[A-Z]*"' | head -1)
  ST=$(grep "\"nid\": \"$P\"" $RES | tail -1 | grep -o '"step_killed": "[^"]*"\|"pad": "[a-z0-9]*"' | tr '\n' ' ')
  [ -f "$SVG" ] && SVGP="$SVG" || SVGP=""
  RECENT=""
  for i in 1 2 3 4 5 6; do
    FAST=$(ls docs/residue_map/quick200_${P}_fast_*.svg 2>/dev/null | tr '
' ' ')
    git add -- $RES $ATT/certs $ATT/logs $SVGP $FAST 2>/dev/null
    if git commit -q -m "A200: $P $V [$ST] $(( $(date +%s) - T0 ))s" -- $RES $ATT/certs $ATT/logs $SVGP $FAST 2>/dev/null; then break; fi
    sleep $((5*i))
  done
  echo "$(date +%H:%M:%S) $P $V $ST rc=$RC $(( $(date +%s) - T0 ))s"
done
