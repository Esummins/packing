#!/bin/bash
# A256 loop_passes -- A229's loop_passes.sh for the trump5 population: while any of the pages has start nodes left,
# rebuild the start-node queue from the MERGED certificates (queue256.py), start N shard workers (worker256.sh) with
# the pass flags, wait for them to drain, repeat.  Exits when queue256 lists no start node.  No LLM in the loop.
#
#   nohup bash attempts/A256-trump5-passes/code/loop256.sh <N workers> <wall> [<pads>] [<nid> ...] \
#        > attempts/A256-trump5-passes/logs/loop256.log 2>&1 &
#
# N IS AN ARGUMENT (the lab ceiling is 12 python processes and the k5 pass loop holds 6 of them; A256 runs 3 until
# the coordinator raises it -- stop this loop, edit nothing, relaunch with a bigger N; the workers also re-check
# their own count against the 3rd argument of worker256.sh every start node).
# With no <nid> the population is A212's 84 ALIVE trump5 nodes (results/triage256.json).
#
# STOP:    touch attempts/A256-trump5-passes/logs/STOP_LOOP   (the loop exits at the top of the next pass)
#          touch attempts/A256-trump5-passes/logs/STOP        (each worker exits after its current start node)
# RESUME:  rm -f attempts/A256-trump5-passes/logs/STOP attempts/A256-trump5-passes/logs/STOP_LOOP
#          then relaunch the same command line: the queue is rebuilt from the certificates, every start node already
#          closed is simply not in it any more, and a start node interrupted mid-way is re-offered (Lemma INHERIT).
cd "$(dirname "$0")/../../.." || exit 1
N=${1:-3}; WALL=${2:-1800}; PADS=${3:-zero}; shift 3 2>/dev/null; PAGES="$@"
ATT=attempts/A256-trump5-passes; CODE=$ATT/code
export PYTHONDONTWRITEBYTECODE=1
export A220_NOROOM_INHERIT=1 A221_LANE=1 A224_SNAP=1
SLOTS=(t1 t2 t3 t4 t5 t6 t7 t8)
busy() { powershell -NoProfile -Command "(Get-CimInstance Win32_Process | Where-Object { (\$_.Name -eq 'python.exe' -and \$_.CommandLine -match 'run256.py') -or (\$_.Name -eq 'bash.exe' -and \$_.CommandLine -match 'worker256.sh') } | Measure-Object).Count" | tr -d '\r '; }
PASS=${A256_PASS:-2}
mkdir -p $ATT/logs
while true; do
  [ -f $ATT/logs/STOP_LOOP ] && { echo "$(date +%H:%M:%S) STOP_LOOP present: exiting"; exit 0; }
  while [ "$(busy)" != "0" ]; do sleep 120; done
  Q=$CODE/queue_pass${PASS}.txt
  python $CODE/queue256.py $PAGES --pads "$PADS" --wall $WALL --out $Q > /dev/null 2>&1
  NS=$(grep -vc '^#' $Q 2>/dev/null | tr -d '\r ')
  echo "$(date +%H:%M:%S) pass $PASS: $NS start nodes (pads $PADS, wall $WALL, $N workers)"
  if [ "${NS:-0}" = "0" ]; then echo "$(date +%H:%M:%S) nothing left: exiting"; exit 0; fi
  git add -- $Q 2>/dev/null; git commit -q -m "A256: pass-$PASS start-node queue ($NS start nodes)" -- $Q 2>/dev/null
  mkdir -p $ATT/logs/claims256; for d in $ATT/logs/claims256/*/; do [ -d "$d" ] && rmdir "$d" 2>/dev/null; done   # fresh claims (empty dirs only; no recursive delete)
  M=$N; [ "$NS" -lt "$N" ] && M=$NS
  for i in $(seq 1 $M); do
    SLOT=${SLOTS[$((i-1))]}
    nohup bash $CODE/worker256.sh $SLOT $WALL $N $Q > $ATT/logs/worker_${SLOT}_pass${PASS}.log 2>&1 &
    sleep 15
  done
  sleep 300
  PASS=$((PASS + 1))
done
