#!/bin/bash
# A270 LOOP -- passes of the pad-g4 campaign over the *_r270w4 records (A57's level-1 cover at pin slack 9/400):
# queue270 (Lemma INHERIT merge over A270's certificates + the STALLED invariant + the crash cap) -> N workers
# (worker270.sh) -> wait for them to drain -> next pass.  Exits when the queue is empty (every record CLOSED, STALLED or
# crashed-out), on STOP_LOOP, or when progress270's 150 CPU-h CAP writes STOP / STOP_LOOP.  No LLM in the loop.
#
#   ( "/c/Program Files/Git/bin/bash.exe" -c "cd /c/Users/esumm/code/packing && nohup bash attempts/A270-k5-lower-slabs/code/loop270.sh 4 1800 \
#        > attempts/A270-k5-lower-slabs/logs/loop270.log 2>&1" & )
#   optional 3rd argument: first pass number
#
# STOP:    touch attempts/A270-k5-lower-slabs/logs/STOP_LOOP   (the loop exits at the top of the next pass)
#          touch attempts/A270-k5-lower-slabs/logs/STOP        (every worker exits after its current start node)
# RESUME:  rm -f attempts/A270-k5-lower-slabs/logs/STOP attempts/A270-k5-lower-slabs/logs/STOP_LOOP, relaunch the SAME
#          line: the pass number continues from results/ran270.txt, finished shards are in the certificates (the merge
#          picks them up), STALLED / crashed-out nodes stay excluded, an interrupted start node is simply re-run.
#          (After a CAP stop, raise progress270.CAP only on the coordinator's word.)
cd "$(dirname "$0")/../../.." || exit 1
ATT=attempts/A270-k5-lower-slabs; CODE=$ATT/code
N=${1:-4}; WALL=${2:-1800}; FIRST=${3:-}
export PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
mkdir -p $ATT/logs $ATT/queues $ATT/results
busy() { powershell -NoProfile -Command "(Get-CimInstance Win32_Process | Where-Object { (\$_.Name -eq 'python.exe' -and \$_.CommandLine -match 'run270.py') -or (\$_.Name -eq 'bash.exe' -and \$_.CommandLine -match 'worker270.sh') } | Measure-Object).Count" | tr -d '\r '; }
PASS=$(awk '{print $1}' $ATT/results/ran270.txt 2>/dev/null | sort -n | tail -1); PASS=$(( ${PASS:-0} + 1 ))
[ -n "$FIRST" ] && PASS=$FIRST
echo "$(date +%H:%M:%S) A270 loop: $N workers, wall $WALL, starting at pass $PASS"
while true; do
  [ -f $ATT/logs/STOP_LOOP ] && { echo "$(date +%H:%M:%S) STOP_LOOP present: exiting"; exit 0; }
  while [ "$(busy)" != "0" ]; do sleep 120; done
  [ -f $ATT/logs/STOP_LOOP ] && { echo "$(date +%H:%M:%S) STOP_LOOP present: exiting"; exit 0; }
  Q=$ATT/queues/queue270_pass${PASS}.txt
  python $CODE/queue270.py --pass $PASS --out $Q
  python $CODE/progress270.py > /dev/null 2>&1
  NS=$(grep -vc '^#' $Q 2>/dev/null | tr -d '\r ')
  echo "$(date +%H:%M:%S) pass $PASS: $NS start node(s)"
  git add -- $Q $ATT/results 2>/dev/null; git commit -q -m "A270: pass-$PASS queue ($NS start nodes; STALLED excluded)" -- $Q $ATT/results 2>/dev/null && git push -q 2>/dev/null
  if [ "${NS:-0}" = "0" ]; then echo "$(date +%H:%M:%S) nothing left (every record CLOSED, STALLED or crashed-out): exiting"; exit 0; fi
  [ -f $ATT/logs/STOP ] && { echo "$(date +%H:%M:%S) STOP present (CAP?): exiting"; exit 0; }
  M=$N; [ "$NS" -lt "$N" ] && M=$NS
  for i in $(seq 1 $M); do
    nohup bash $CODE/worker270.sh w$i $WALL $N $PASS $Q > $ATT/logs/worker270_w${i}_pass${PASS}.out 2>&1 &
    sleep 20
  done
  sleep 300
  PASS=$((PASS + 1))
done
