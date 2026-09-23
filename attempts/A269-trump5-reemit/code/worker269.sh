#!/bin/bash
# A269 worker -- one start node at a time from a queue269 file: run269.py (A211's run211 verbatim over the re-emitted
# records; A268's count268 + leaf268 ON; A257's gate + aligned split + TUBE-KILL ON), one shard certificate per start
# node (certs/coarsetree211_<nid>__<tag>.json), a ran269 line (the STALLED invariant reads it), one commit + push.
#
#   bash worker269.sh <slot> <wall> <max own pythons> <pass> <queue file>
#
# Gates: lab ceiling 12 pythons (Claude Extensions excluded), A269's own pythons < the 3rd argument, >= 3072 MB free.
# BelowNormal + affinity 0xFFFF are set inside run211.py; BLAS threads 1; PYTHONDONTWRITEBYTECODE=1.
# Stop: touch attempts/A269-trump5-reemit/logs/STOP   (the running start node finishes first; nothing is killed)
cd "$(dirname "$0")/../../.." || exit 1
ATT=attempts/A269-trump5-reemit; CODE=$ATT/code
export PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1
export A220_NOROOM_INHERIT=1 A221_LANE=1 A224_SNAP=1 A268_COUNT=1 A268_FORCE=1 A269_TUBE=1
SLOT=${1:-w}; WALL=${2:-1800}; MAXMINE=${3:-4}; PASS=${4:-1}; Q=$5
labcount() { powershell -NoProfile -Command "Get-CimInstance Win32_Process -Filter 'Name=\"python.exe\"' | Where-Object { \$_.CommandLine -notmatch 'Claude Extensions' } | Measure-Object | Select-Object -ExpandProperty Count" | tr -d '\r '; }
mine() { powershell -NoProfile -Command "Get-CimInstance Win32_Process -Filter 'Name=\"python.exe\"' | Where-Object { \$_.CommandLine -match 'run269.py|queue269.py|progress269.py' } | Measure-Object | Select-Object -ExpandProperty Count" | tr -d '\r '; }
freemb() { powershell -NoProfile -Command "[int]((Get-CimInstance Win32_OperatingSystem).FreePhysicalMemory/1024)" | tr -d '\r '; }
mkdir -p $ATT/logs/claims269 $ATT/logs/runs $ATT/certs $ATT/results
while read -r NID START REST; do
  NID=${NID//$'\r'/}; START=${START//$'\r'/}
  [ -z "$NID" ] && continue
  case "$NID" in \#*) continue;; esac
  [ -f $ATT/logs/STOP ] && { echo "$(date +%H:%M:%S) [$SLOT] STOP present: exiting"; exit 0; }
  PAD=${START%%:*}; LABEL=${START#*:}
  TAG=$(printf '%s_%s' "$PAD" "$LABEL" | tr -c 'A-Za-z0-9._-' '_')
  mkdir "$ATT/logs/claims269/${PASS}__${NID}__${TAG}" 2>/dev/null || continue
  while [ "$(labcount)" -ge 12 ] || [ "$(mine)" -ge "$MAXMINE" ] || [ "$(freemb)" -lt 3072 ]; do sleep 60; done
  LOG=$ATT/logs/runs/run269_${NID}__${TAG}.log
  T0=$(date +%s); echo "$(date +%H:%M:%S) [$SLOT] pass $PASS start $NID $PAD:$LABEL wall $WALL (lab $(labcount), mine $(mine))" | tee -a $LOG
  timeout -s KILL $(( 2 * WALL + 1200 )) python $CODE/run269.py page "$NID" --pads "$PAD" --wall $WALL --start "$LABEL" \
      --cert-suffix "$TAG" >> $LOG 2>&1
  RC=$?
  if [ $RC -eq 0 ]; then echo "$PASS $NID $PAD:$LABEL rc=$RC $(( $(date +%s) - T0 ))s" >> $ATT/results/ran269.txt       # a finished run only
  else echo "$PASS $NID $PAD:$LABEL rc=$RC $(( $(date +%s) - T0 ))s" >> $ATT/results/crashed269.txt; fi           # a crash is not a pass: requeued
  V=$(grep -o "A268: [^;]*" $LOG | tail -1)
  P=""; for f in $ATT/results $ATT/certs/count268 $ATT/certs/coarsetree211_${NID}__${TAG}.json $ATT/certs/csp209_${NID}_${PAD}_s0.json $LOG; do [ -e "$f" ] && P="$P $f"; done
  for i in 1 2 3 4 5 6; do
    git add -- $P 2>/dev/null
    if git commit -q -m "A269 pass $PASS: $NID $PAD:$LABEL [$V] $(( $(date +%s) - T0 ))s rc=$RC" -- $P 2>/dev/null; then git push -q 2>/dev/null; break; fi
    sleep $((5*i))
  done
  echo "$(date +%H:%M:%S) [$SLOT] $NID $PAD:$LABEL $V rc=$RC $(( $(date +%s) - T0 ))s" | tee -a $LOG
done < "$Q"
echo "$(date +%H:%M:%S) [$SLOT] queue $Q done"
