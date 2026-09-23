#!/bin/bash
# A268 worker -- one start node at a time from a queue268 file, with A268's levers ON (A268_COUNT=1, A268_FORCE=1).
#
#   bash worker268.sh <slot> <wall> <max own pythons> <pass> <queue file>
#
# Queue line: <chain> <nid> <pad>:<label>   chain k5 -> A211's certs/results (the k5 chain's own shard files);
#             trump5 -> A256's certs/results; seam -> A268's own seam journal (results/seam268/).
# Claims: logs/claims268/<pass>__<chain>__<nid>__<tag> (mkdir).  run268 itself runs verify268 over the shard's new
# dumps IN PROCESS (results/verify268.jsonl; one python per shard); then the ran268 line (the STALLED invariant reads it), one commit with explicit paths.
# Stop: touch attempts/A268-terminal-leaves/logs/STOP (the running shard finishes first).
cd "$(dirname "$0")/../../.." || exit 1
ATT=attempts/A268-terminal-leaves; CODE=$ATT/code
export PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1
export A220_NOROOM_INHERIT=1 A221_LANE=1 A224_SNAP=1 A268_COUNT=1 A268_FORCE=1
SLOT=${1:-w}; WALL=${2:-1800}; MAXMINE=${3:-4}; PASS=${4:-1}; Q=$5
labcount() { powershell -NoProfile -Command "Get-CimInstance Win32_Process -Filter 'Name=\"python.exe\"' | Where-Object { \$_.CommandLine -notmatch 'Claude Extensions' } | Measure-Object | Select-Object -ExpandProperty Count" | tr -d '\r '; }
mine() { powershell -NoProfile -Command "Get-CimInstance Win32_Process -Filter 'Name=\"python.exe\"' | Where-Object { \$_.CommandLine -match 'run268.py|verify268.py|queue268.py' } | Measure-Object | Select-Object -ExpandProperty Count" | tr -d '\r '; }
freemb() { powershell -NoProfile -Command "[int]((Get-CimInstance Win32_OperatingSystem).FreePhysicalMemory/1024)" | tr -d '\r '; }
mkdir -p $ATT/logs/claims268 $ATT/certs $ATT/results/seam268
while read -r CHAIN NID START REST; do
  CHAIN=${CHAIN//$'\r'/}; NID=${NID//$'\r'/}; START=${START//$'\r'/}
  [ -z "$CHAIN" ] && continue
  case "$CHAIN" in \#*) continue;; esac
  [ -f $ATT/logs/STOP ] && { echo "$(date +%H:%M:%S) [$SLOT] STOP present: exiting"; exit 0; }
  PAD=${START%%:*}; LABEL=${START#*:}
  TAG=$(printf '%s_%s' "$PAD" "$LABEL" | tr -c 'A-Za-z0-9._-' '_')
  mkdir "$ATT/logs/claims268/${PASS}__${CHAIN}__${NID}__${TAG}" 2>/dev/null || continue
  while [ "$(labcount)" -ge 12 ] || [ "$(mine)" -ge "$MAXMINE" ] || [ "$(freemb)" -lt 3072 ]; do sleep 60; done
  LOG=$ATT/logs/run268_${CHAIN}_${NID}__${TAG}.log
  T0=$(date +%s); echo "$(date +%H:%M:%S) [$SLOT] pass $PASS start $CHAIN $NID $PAD:$LABEL wall $WALL (lab $(labcount), mine $(mine))" | tee -a $LOG
  export A268_NID=$NID
  case $CHAIN in
    k5)     CD=attempts/A211-coarse-tree/certs; RS=attempts/A211-coarse-tree/results/coarsetree211.jsonl
            timeout -s KILL $(( 2 * WALL + 1200 )) python $CODE/run268.py k5 page "$NID" --pads "$PAD" --wall $WALL --start "$LABEL" \
                --cert-suffix "$TAG" --cert-dir $CD --results $RS >> $LOG 2>&1;;
    trump5) CD=attempts/A256-trump5-passes/certs; RS=attempts/A256-trump5-passes/results/trump5passes256.jsonl
            timeout -s KILL $(( 2 * WALL + 1200 )) python $CODE/run268.py trump5 page "$NID" --pads "$PAD" --wall $WALL --start "$LABEL" \
                --cert-suffix "$TAG" --cert-dir $CD --results $RS >> $LOG 2>&1;;
    seam)   CD=$ATT/results/seam268; RS=$ATT/results/seam268/pilot257.jsonl
            A230_EPS=1 timeout -s KILL $(( 2 * WALL + 1200 )) python $CODE/run268.py seam --phase siblings --only-sibling "$LABEL" \
                --wall-sib $WALL --pad "$PAD" --journal $RS >> $LOG 2>&1;;
  esac
  RC=$?
  if [ $RC -eq 0 ]; then echo "$PASS $CHAIN $NID $PAD:$LABEL rc=$RC $(( $(date +%s) - T0 ))s" >> $ATT/results/ran268.txt   # a finished pass only
  else echo "$PASS $CHAIN $NID $PAD:$LABEL rc=$RC $(( $(date +%s) - T0 ))s" >> $ATT/results/crashed268.txt; fi       # a crash is not a pass: requeued
  V=$(grep -o "A268: [^;]*" $LOG | tail -1)
  P=""; for f in $ATT/results $ATT/certs $LOG $CD/coarsetree211_${NID}__${TAG}.json $RS; do [ -e "$f" ] && P="$P $f"; done
  for i in 1 2 3 4 5 6; do
    git add -- $P 2>/dev/null
    if git commit -q -m "A268 pass $PASS: $CHAIN $NID $PAD:$LABEL [$V] $(( $(date +%s) - T0 ))s rc=$RC" -- $P 2>/dev/null; then git push -q 2>/dev/null; break; fi
    sleep $((5*i))
  done
  echo "$(date +%H:%M:%S) [$SLOT] $CHAIN $NID $PAD:$LABEL $V rc=$RC $(( $(date +%s) - T0 ))s" | tee -a $LOG
done < "$Q"
echo "$(date +%H:%M:%S) [$SLOT] queue $Q done"
