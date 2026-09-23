#!/bin/bash
# A269 LOOP -- passes over the re-emitted trump5 records at the window pad(s): queue269 (Lemma INHERIT merge over A269's
# certificates + the STALLED invariant) -> N workers (worker269.sh) -> wait for them to drain -> next pass.  Exits when
# the queue is empty (every record CLOSED or STALLED).  No LLM in the loop.
#
#   (cd /c/Users/esumm/code/packing && nohup bash attempts/A269-trump5-reemit/code/loop269.sh 4 1800 window \
#        > attempts/A269-trump5-reemit/logs/loop269.log 2>&1 &)
#   optional 4th argument: a comma list of source nids (e.g. the benchmark's 10); 5th: first pass number
#
# STOP:    touch attempts/A269-trump5-reemit/logs/STOP_LOOP   (the loop exits at the top of the next pass)
#          touch attempts/A269-trump5-reemit/logs/STOP        (every worker exits after its current start node)
# RESUME:  rm -f attempts/A269-trump5-reemit/logs/STOP attempts/A269-trump5-reemit/logs/STOP_LOOP, relaunch the SAME line:
#          the pass number continues from results/ran269.txt, finished shards are in the certificates (the merge picks
#          them up), STALLED nodes stay excluded, an interrupted start node is simply re-run (a crash is not a pass).
cd "$(dirname "$0")/../../.." || exit 1
ATT=attempts/A269-trump5-reemit; CODE=$ATT/code
N=${1:-4}; WALL=${2:-1800}; PADS=${3:-window}; ONLY=${4:-}; FIRST=${5:-}
export PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
mkdir -p $ATT/logs $ATT/queues $ATT/results
busy() { powershell -NoProfile -Command "(Get-CimInstance Win32_Process | Where-Object { (\$_.Name -eq 'python.exe' -and \$_.CommandLine -match 'run269.py') -or (\$_.Name -eq 'bash.exe' -and \$_.CommandLine -match 'worker269.sh') } | Measure-Object).Count" | tr -d '\r '; }
PASS=$(awk '{print $1}' $ATT/results/ran269.txt 2>/dev/null | sort -n | tail -1); PASS=$(( ${PASS:-0} + 1 ))
[ -n "$FIRST" ] && PASS=$FIRST
echo "$(date +%H:%M:%S) A269 loop: $N workers, wall $WALL, pads $PADS, only '${ONLY}', starting at pass $PASS"
while true; do
  [ -f $ATT/logs/STOP_LOOP ] && { echo "$(date +%H:%M:%S) STOP_LOOP present: exiting"; exit 0; }
  while [ "$(busy)" != "0" ]; do sleep 120; done
  Q=$ATT/queues/queue269_pass${PASS}.txt
  python $CODE/queue269.py --pass $PASS --pads "$PADS" ${ONLY:+--only "$ONLY"} --out $Q
  python $CODE/progress269.py > /dev/null 2>&1
  NS=$(grep -vc '^#' $Q 2>/dev/null | tr -d '\r ')
  echo "$(date +%H:%M:%S) pass $PASS: $NS start node(s)"
  git add -- $Q $ATT/results 2>/dev/null; git commit -q -m "A269: pass-$PASS queue ($NS start nodes; STALLED excluded)" -- $Q $ATT/results 2>/dev/null
  if [ "${NS:-0}" = "0" ]; then echo "$(date +%H:%M:%S) nothing left (every record CLOSED or STALLED): exiting"; exit 0; fi
  M=$N; [ "$NS" -lt "$N" ] && M=$NS
  for i in $(seq 1 $M); do
    nohup bash $CODE/worker269.sh w$i $WALL $N $PASS $Q > $ATT/logs/worker269_w${i}_pass${PASS}.log 2>&1 &
    sleep 20
  done
  sleep 300
  PASS=$((PASS + 1))
done
