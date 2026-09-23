#!/bin/bash
# A268 terminal-leaf LOOP -- passes over the k5 / trump5-g1 / seam terminal start nodes with A268's levers ON,
# N workers (worker268.sh), the STALLED invariant enforced by queue268.py (a start node a pass returned UNCHANGED is
# recorded in results/stalled268.txt and never requeued), a queue rebuilt from the certificates every pass.
#
#   nohup bash attempts/A268-terminal-leaves/code/loop268.sh 4 1800 > attempts/A268-terminal-leaves/logs/loop268.log 2>&1 &
#
# STOP:    touch attempts/A268-terminal-leaves/logs/STOP_LOOP   (the loop exits at the top of the next pass)
#          touch attempts/A268-terminal-leaves/logs/STOP        (every worker exits after its current start node)
# RESUME:  rm -f attempts/A268-terminal-leaves/logs/STOP attempts/A268-terminal-leaves/logs/STOP_LOOP, relaunch the SAME
#          line: the pass number continues from results/ran268.txt, finished shards are in the certificates (Lemma
#          INHERIT / PAR: the merge picks them up), STALLED nodes stay excluded, an interrupted shard is simply re-run.
cd "$(dirname "$0")/../../.." || exit 1
ATT=attempts/A268-terminal-leaves; CODE=$ATT/code
N=${1:-4}; WALL=${2:-1800}
K5PAGES="k5_16_interior_Y0384 k5_11_interior_Y0738_D01 k5_11_interior_Y0738_D02 k5_11_interior_Y0738_D03 k5_16_interior_Y0391 k5_11_interior_Y0596"
SEAM="R.1.1,R.1.2.1"
export PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
mkdir -p $ATT/logs $ATT/results/seam268 $ATT/queues
if [ ! -s $ATT/results/seam268/pilot257.jsonl ]; then                 # the A257 spine row: the siblings replay it
  head -1 attempts/A257-trump5-window/results/pilot257.jsonl > $ATT/results/seam268/pilot257.jsonl
  cp attempts/A257-trump5-window/certs/csp209_synth257_d001_h002_t2_g1_s0.json $ATT/results/seam268/
fi
busy() { powershell -NoProfile -Command "(Get-CimInstance Win32_Process | Where-Object { (\$_.Name -eq 'python.exe' -and \$_.CommandLine -match 'run268.py') -or (\$_.Name -eq 'bash.exe' -and \$_.CommandLine -match 'worker268.sh') } | Measure-Object).Count" | tr -d '\r '; }
PASS=$(awk '{print $1}' $ATT/results/ran268.txt 2>/dev/null | sort -n | tail -1); PASS=$(( ${PASS:-0} + 1 ))
echo "$(date +%H:%M:%S) A268 loop: $N workers, wall $WALL, starting at pass $PASS"
while true; do
  [ -f $ATT/logs/STOP_LOOP ] && { echo "$(date +%H:%M:%S) STOP_LOOP present: exiting"; exit 0; }
  while [ "$(busy)" != "0" ]; do sleep 120; done
  Q=$ATT/queues/queue268_pass${PASS}.txt
  python $CODE/queue268.py --pass $PASS --k5 $K5PAGES --trump5-g1 --seam "$SEAM" --out $Q
  NS=$(grep -vc '^#' $Q 2>/dev/null | tr -d '\r ')
  echo "$(date +%H:%M:%S) pass $PASS: $NS start node(s)"
  git add -- $Q $ATT/results 2>/dev/null; git commit -q -m "A268: pass-$PASS queue ($NS start nodes; STALLED excluded)" -- $Q $ATT/results 2>/dev/null
  if [ "${NS:-0}" = "0" ]; then echo "$(date +%H:%M:%S) nothing left (every node DEAD or STALLED): exiting"; exit 0; fi
  M=$N; [ "$NS" -lt "$N" ] && M=$NS
  for i in $(seq 1 $M); do
    nohup bash $CODE/worker268.sh w$i $WALL $N $PASS $Q > $ATT/logs/worker268_w${i}_pass${PASS}.log 2>&1 &
    sleep 20
  done
  sleep 300
  PASS=$((PASS + 1))
done
