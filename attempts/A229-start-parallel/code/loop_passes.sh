#!/bin/bash
# loop_passes.sh -- keep the k5 lab busy without an LLM in the loop: while any of the given pages has start nodes
# left, rebuild the start-node queue from the merged certificates (queue229.py), start N shard workers
# (worker229.sh) with the pass flags, wait for them to drain, repeat.  Exits when queue229 lists no start node.
#   nohup bash attempts/A229-start-parallel/code/loop_passes.sh 6 k5_16_interior_Y0402 k5_16_interior_Y1056 \
#        > attempts/A211-coarse-tree/logs/loop_passes.log 2>&1 &
# Stop: touch attempts/A211-coarse-tree/logs/STOP_LOOP (the running shards finish their start node).
cd "$(dirname "$0")/../../.." || exit 1
N=${1:-6}; shift; PAGES="$@"
ATT=attempts/A211-coarse-tree; A229=attempts/A229-start-parallel/code
export PYTHONDONTWRITEBYTECODE=1
export A220_NOROOM_INHERIT=1 A221_LANE=1 A224_SNAP=1
SLOTS=(p8a p8b p8c p8d p8e p8f p8g p8h)
busy() { powershell -NoProfile -Command "(Get-CimInstance Win32_Process | Where-Object { (\$_.Name -eq 'python.exe' -and \$_.CommandLine -match 'run211.py page') -or (\$_.Name -eq 'bash.exe' -and \$_.CommandLine -match 'worker2(11|29).sh') } | Measure-Object).Count" | tr -d '\r '; }
PASS=8
while true; do
  [ -f $ATT/logs/STOP_LOOP ] && { echo "$(date +%H:%M:%S) STOP_LOOP present: exiting"; exit 0; }
  while [ "$(busy)" != "0" ]; do sleep 120; done
  Q=$ATT/code/queue_pass${PASS}.txt
  python $A229/queue229.py $PAGES --out $Q > /dev/null 2>&1
  NS=$(grep -vc '^#' $Q 2>/dev/null | tr -d '\r ')
  echo "$(date +%H:%M:%S) pass $PASS: $NS start nodes over [$PAGES]"
  if [ "${NS:-0}" = "0" ]; then echo "$(date +%H:%M:%S) nothing left: exiting"; exit 0; fi
  git add -- $Q 2>/dev/null; git commit -q -m "A211: pass-$PASS start-node queue (A229 loop)" -- $Q 2>/dev/null
  mkdir -p $ATT/logs/claims229; for d in $ATT/logs/claims229/*/; do [ -d "$d" ] && rmdir "$d" 2>/dev/null; done   # fresh claims (empty dirs only; no recursive delete)
  M=$N; [ "$NS" -lt "$N" ] && M=$NS
  for i in $(seq 1 $M); do
    SLOT=${SLOTS[$((i-1))]}
    nohup bash $A229/worker229.sh $SLOT 1800 $Q > $ATT/logs/worker_${SLOT}_pass${PASS}.log 2>&1 &
    sleep 15
  done
  sleep 300
  PASS=$((PASS + 1))
done
